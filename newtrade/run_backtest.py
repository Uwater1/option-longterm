#!/usr/bin/env python3
"""
Main CLI Backtest Runner for NewTrade framework.
Runs full pipeline:
  1. Load admitted pools & raw ETF datasets.
  2. Compute zero-lookahead expanding z-score standardization over history.
  3. Aggregate composite signal Z_composite using chosen weighting scheme.
  4. Filter to target OOS period (default: 2022-01-01 to 2026-01-01).
  5. Apply conviction threshold & position sizing.
  6. Simulate ETF spot backtest with 8 bps friction.
  7. Output markdown performance report & JSON results.
"""

import sys
import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
ALL_SCHEMES = ["ew", "icw", "score", "rank"]  # glm deferred


def run_single_backtest(etf: str, side: str = "single", scheme_name: str = "ew", z_th: float = 0.5, 
                        position_mode: str = "binary", fee_bps: float = 0.0008, min_features: int = 10,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                        z_buffer: float = 0.2, auto_threshold: bool = False) -> dict:
    """
    Run backtest for one ETF and side combination filtered to OOS date range.
    
    If auto_threshold=True, sweeps Z_th on training data and applies production buffer.
    """
    print(f"--> Running Backtest: ETF={etf}, Side={side}, Scheme={scheme_name.upper()}, z_th={'auto' if auto_threshold else z_th}, Mode={position_mode}, OOS=[{start_date} to {end_date}]")
    
    # 1. Load admitted pool
    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        print(f"    [SKIP] Pool size {len(pool)} < {min_features} threshold.")
        return {
            "etf": etf,
            "side": side,
            "scheme": scheme_name,
            "status": "SKIPPED_FEAT_FLOOR",
            "n_features": len(pool),
            "period": f"{start_date[:7]} ~ {end_date[:7]}",
            "n_trades": 0,
            "cost_sharpe": 0.0,
            "raw_sharpe": 0.0,
            "total_pnl": 0.0,
            "max_drawdown": 0.0,
            "win_rate_pct": 0.0,
            "ann_turnover": 0.0,
        }

    # 2. Load ETF dataset
    df = load_etf_dataset(etf)
    
    # 3. Build raw feature matrix & signs
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    
    # 4. Zero-lookahead expanding z-score standardizer on full history
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    
    # 5. Calculate Composite Signal using weighting scheme
    scheme_func = get_weighting_scheme(scheme_name)
    
    # Determine n_train for ICW shrinkage (days before start_date)
    t_start_ts = pd.Timestamp(start_date)
    n_train = int((df["date"] < t_start_ts).sum())
    if n_train < 252:
        n_train = 1700  # fallback ~7 years
    
    Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train)

    # 6. Threshold Determination (auto-sweep or fixed)
    sweep_info = None
    if auto_threshold:
        # Get training-period composite signal and returns for sweep
        train_mask = df["date"] < t_start_ts
        Z_composite_train = Z_composite[train_mask.values]
        trade_returns_col = "trade_return" if "trade_return" in df.columns else None
        if trade_returns_col:
            trade_returns_train = df[train_mask][trade_returns_col].values.astype(np.float64)
        else:
            trade_returns_train = df[train_mask]["close"].pct_change().fillna(0.0).values
        
        # Sweep on training data
        sweep_info = sweep_optimal_threshold(
            Z_composite_train, trade_returns_train,
            mode=position_mode, fee_bps=fee_bps
        )
        z_th_prod = compute_production_threshold(sweep_info, z_buffer=z_buffer)
        print(f"    [THRESHOLD] Train-optimal Z_th={sweep_info['optimal_z_th']:.2f} (Sharpe={sweep_info['best_sharpe']:.3f}) -> Prod Z_th={z_th_prod:.2f} (buffer=+{z_buffer:.2f})")
    else:
        z_th_prod = z_th

    # 7. Position Sizing with production threshold
    positions_full = generate_positions(Z_composite, z_th=z_th_prod, mode=position_mode, long_only=True)

    # 8. Date Filtering to OOS Evaluation Period
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not mask.any():
        print(f"    [WARNING] No data available for date range {start_date} to {end_date}. Falling back to recent history.")
        mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[mask].reset_index(drop=True)
    positions_oos = positions_full[mask]

    # 9. Backtest Simulation on OOS slice
    trade_returns = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df_oos.columns else df_oos["close"].pct_change().fillna(0.0).values
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns, positions_oos, fee_bps=fee_bps)

    # 10. Calculate Metrics
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    metrics.update({
        "etf": etf,
        "side": side,
        "scheme": scheme_name,
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th_prod,
        "z_th_train": sweep_info["optimal_z_th"] if sweep_info else None,
        "z_buffer": z_buffer if auto_threshold else 0.0,
        "position_mode": position_mode,
        "dates": df_oos["date"].dt.strftime("%Y-%m-%d").tolist() if "date" in df_oos.columns else [],
        "cum_pnl": np.cumsum(net_returns).tolist(),
    })

    print(f"    [RESULT] OOS ({metrics['period']}) | Cost Sharpe: {metrics['cost_sharpe']} | PnL: {metrics['total_pnl']} | WinRate: {metrics['win_rate_pct']}% | Intraday Trades: {metrics['n_trades']}/{metrics['n_days']}")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="NewTrade Day-Model Factor Monetization Backtest Runner")
    parser.add_argument("-e", "--etf", type=str, default="all", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"], help="Trading side")
    parser.add_argument("--scheme", type=str, default="ew", choices=["ew", "icw", "score", "rank", "glm", "all"], help="Factor weighting scheme ('all' runs ew/icw/score/rank)")
    parser.add_argument("--z-th", type=str, default="auto", help="Conviction threshold Z score. 'auto' = train-sweep + buffer, or float value for fixed.")
    parser.add_argument("--z-buffer", type=float, default=0.2, help="Production buffer added to train-optimal threshold (default 0.2)")
    parser.add_argument("--position-mode", type=str, default="binary", choices=["binary", "tanh"], help="Position sizing mode")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in basis points (default 8.0 = 0.0008)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS Start Date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS End Date (YYYY-MM-DD)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output markdown report path (default: newtrade/REPORT.md)")

    args = parser.parse_args()

    # Parse z_th: 'auto' or float
    auto_threshold = args.z_th.lower() == "auto"
    z_th_fixed = 0.5 if auto_threshold else float(args.z_th)

    etfs_to_run = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    schemes_to_run = ALL_SCHEMES if args.scheme.lower() == "all" else [args.scheme]
    fee_bps = args.fee_bps / 10000.0

    print("================================================================================")
    print(f"NewTrade Backtest Engine | Scheme={args.scheme.upper()} | z_th={args.z_th} | buffer={args.z_buffer} | OOS=[{args.start_date} ~ {args.end_date}]")
    print("================================================================================")

    results = []
    for scheme in schemes_to_run:
        for etf in etfs_to_run:
            res = run_single_backtest(
                etf=etf,
                side=args.side,
                scheme_name=scheme,
                z_th=z_th_fixed,
                position_mode=args.position_mode,
                fee_bps=fee_bps,
                start_date=args.start_date,
                end_date=args.end_date,
                z_buffer=args.z_buffer,
                auto_threshold=auto_threshold,
            )
            results.append(res)

    # Generate Rank Bounded Weight plot artifact
    rank_results = [r for r in results if r.get("scheme") == "rank" and r.get("status") == "SUCCESS"]
    chart_rel_path = None
    if rank_results:
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(10, 4.5), dpi=150)
            for r in rank_results:
                if r.get("dates") and r.get("cum_pnl"):
                    dates = pd.to_datetime(r["dates"])
                    cum_pnl = r["cum_pnl"]
                    ax.plot(dates, cum_pnl, label=f"{r['etf']} (Sharpe: {r['cost_sharpe']:.3f}, PnL: {r['total_pnl']:+.4f})", linewidth=1.8)
            
            ax.set_title("Rank Bounded Weight — OOS Cumulative Net PnL (10:00 - 14:35 Intraday)", fontsize=11, fontweight='bold')
            ax.set_xlabel("Date", fontsize=9)
            ax.set_ylabel("Cumulative Net PnL", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", frameon=True, fontsize=9)
            fig.tight_layout()

            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            chart_path = artifacts_dir / "rank_bounded_equity.png"
            fig.savefig(chart_path)
            plt.close(fig)
            chart_rel_path = "artifacts/rank_bounded_equity.png"
            print(f"Saved Rank Bounded equity chart to {chart_path}")
        except Exception as e:
            print(f"[WARNING] Failed to generate plot: {e}")

    # Print summary table
    print("\n================================================================================")
    print("NEWTRADE OOS BACKTEST PERFORMANCE SUMMARY (10:00 - 14:35 Intraday Trades)")
    print("================================================================================")
    
    headers = ["ETF", "Side", "OOS Period", "Z_th", "Features", "Trades", "Cost Sharpe", "Raw Sharpe", "Total PnL", "Max DD", "Win Rate", "Turnover"]
    
    SCHEME_TITLES = {
        "rank": "Rank Bounded Weight (Primary)",
        "ew": "Equal Weight (EW)",
        "icw": "IC Weight (ICW)",
        "score": "Score Weighted",
        "glm": "Linear GLM",
    }
    
    def _format_row(r):
        if r["status"] == "SUCCESS":
            z_th_str = f"{r['z_th']:.2f}"
            if r.get("z_th_train") is not None:
                z_th_str += f" (train:{r['z_th_train']:.2f})"
            return [
                r["etf"],
                r["side"],
                r["period"],
                z_th_str,
                str(r["n_features"]),
                str(r.get("n_trades", 0)),
                f"{r['cost_sharpe']:.3f}",
                f"{r['raw_sharpe']:.3f}",
                f"{r['total_pnl']:+.4f}",
                f"{r['max_drawdown']:.4f}",
                f"{r['win_rate_pct']:.1f}%",
                f"{r['ann_turnover']:.1f}x",
            ]
        else:
            return [
                r["etf"],
                r["side"],
                r.get("period", "N/A"),
                "N/A",
                str(r["n_features"]),
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
            ]
    
    def _render_table(rows):
        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)
    
    # Group results by scheme (ensure 'rank' is first)
    from collections import OrderedDict
    scheme_groups = OrderedDict()
    # Put rank first if present
    if "rank" in [r.get("scheme") for r in results]:
        scheme_groups["rank"] = [r for r in results if r.get("scheme") == "rank"]
    for r in results:
        s = r.get("scheme", "?")
        if s != "rank":
            scheme_groups.setdefault(s, []).append(r)
    
    # Build report sections
    report_sections = []
    for scheme_key, scheme_results in scheme_groups.items():
        rows = [_format_row(r) for r in scheme_results]
        title = SCHEME_TITLES.get(scheme_key, scheme_key.upper())
        table_md = _render_table(rows)
        
        if scheme_key == "rank":
            # Uncollapsed main section with chart
            img_md = f"![Rank Bounded Weight Cumulative Equity]({chart_rel_path})\n\n" if chart_rel_path else ""
            section = f"## {title}\n\n{img_md}{table_md}"
        else:
            # Collapsed details block for secondary schemes
            section = f"<details>\n<summary><b>{title}</b> (click to expand)</summary>\n\n{table_md}\n\n</details>"
        report_sections.append(section)
    
    report_content = "\n\n".join(report_sections)
    print("\n" + report_content + "\n")

    # Clean results before saving JSON (drop large arrays to keep JSON clean)
    clean_results = []
    for r in results:
        r_copy = dict(r)
        r_copy.pop("dates", None)
        r_copy.pop("cum_pnl", None)
        clean_results.append(r_copy)

    # Save markdown report (default: REPORT.md in newtrade/)
    out_path = Path(args.output) if args.output else HERE / "REPORT.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# NewTrade OOS Backtest Report\n\n")
        f.write(f"- **OOS Evaluation Period**: `{args.start_date} ~ {args.end_date}`\n")
        f.write(f"- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`\n")
        f.write(f"- **Scheme(s)**: `{args.scheme.upper()}`\n")
        f.write(f"- **Conviction Threshold**: `{args.z_th}` (buffer=+{args.z_buffer})\n")
        f.write(f"- **Position Mode**: `{args.position_mode}`\n")
        f.write(f"- **Transaction Friction**: `{args.fee_bps} bps`\n\n")
        f.write(report_content + "\n")
    print(f"Saved backtest report to {out_path}")

    # Save JSON result artifact in newtrade/data/
    data_dir = HERE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    scheme_label = args.scheme if args.scheme != "all" else "all_schemes"
    json_path = data_dir / f"backtest_results_{scheme_label}_{args.side}.json"
    with open(json_path, "w") as f:
        json.dump(clean_results, f, indent=2)
    print(f"Saved JSON results to {json_path}")


if __name__ == "__main__":
    main()
