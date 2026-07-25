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

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba, load_future_trade_returns
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold, build_trade_log_df

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
ALL_SCHEMES = ["ew", "icw", "score", "rank"]  # glm deferred


def run_single_backtest(etf: str, side: str = "single", scheme_name: str = "ew", z_th: float = 0.5, 
                        position_mode: str = "binary", fee_bps: float = 0.0008, min_features: int = 10,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                        z_buffer: float = 0.1, z_short_buffer: float = None, auto_threshold: bool = False,
                        rank_kwargs: dict = None, dynamic_ic: bool = False, long_only: bool = False,
                        use_future: bool = False) -> dict:
    """
    Run backtest for one ETF and side combination filtered to OOS date range.
    
    If auto_threshold=True, sweeps Z_th on training data and applies production buffer.
    If use_future=True, trades underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF).
    """
    # 1. Load admitted pool
    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        print(f"    [SKIP] Pool size {len(pool)} < {min_features} threshold.")
        return {
            "etf": etf,
            "side": side,
            "scheme": scheme_name,
            "asset_type": "Future" if use_future else "Spot ETF",
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
            "trade_log_df": None,
        }

    # 2. Load ETF dataset
    df = load_etf_dataset(etf)

    # Handle --future underlying traded return loading
    asset_type = "Spot ETF"
    if use_future:
        fut_returns, fut_ok, fut_name = load_future_trade_returns(etf, df)
        if not fut_ok:
            print(f"--> [SKIP] {etf} has no Index Future mapping for --future mode.")
            return {
                "etf": etf,
                "side": side,
                "scheme": scheme_name,
                "asset_type": "Future (N/A)",
                "status": "SKIPPED_NO_FUTURE",
                "n_features": len(pool),
                "period": f"{start_date[:7]} ~ {end_date[:7]}",
                "n_trades": 0,
                "cost_sharpe": 0.0,
                "raw_sharpe": 0.0,
                "total_pnl": 0.0,
                "max_drawdown": 0.0,
                "win_rate_pct": 0.0,
                "ann_turnover": 0.0,
                "trade_log_df": None,
            }
        full_trade_ret = fut_returns
        asset_type = f"Future ({fut_name})"
    else:
        full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values

    print(f"--> Running Backtest: ETF={etf}, Asset={asset_type}, Side={side}, Scheme={scheme_name.upper()}, z_th={'auto' if auto_threshold else z_th}, Mode={position_mode}, LongOnly={long_only}, OOS=[{start_date} to {end_date}]")
    
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
    
    extra_kwargs = rank_kwargs if (scheme_name == "rank" and rank_kwargs) else {}
    if dynamic_ic and scheme_name == "rank":
        exp_ic_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
        extra_kwargs["expanding_ic"] = exp_ic_mat

    Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train, **extra_kwargs)

    # 6. Threshold Determination (auto-sweep or fixed)
    sweep_info = None
    if auto_threshold:
        # Get training-period composite signal and returns for sweep
        train_mask = df["date"] < t_start_ts
        Z_composite_train = Z_composite[train_mask.values]
        trade_returns_train = full_trade_ret[train_mask.values]
        
        # Sweep on training data
        sweep_info = sweep_optimal_threshold(
            Z_composite_train, trade_returns_train,
            mode=position_mode, fee_bps=fee_bps, long_only=long_only
        )
        z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer, z_short_buffer=z_short_buffer)
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        opt_l = sweep_info.get("optimal_z_th_long", sweep_info.get("optimal_z_th", 0.5))
        opt_s = sweep_info.get("optimal_z_th_short", opt_l)
        print(f"    [THRESHOLD] Train-optimal Long Z_th={opt_l:.2f}, Short Z_th={opt_s:.2f} (Long Sharpe={sweep_info['best_sharpe']:.3f}) -> Prod Long Z_th={z_th_prod:.2f} (buf=+{z_buffer:.2f}), Short Z_th={z_th_short:.2f} (buf=+{eff_short_buf:.2f})")
    else:
        z_th_prod = z_th
        eff_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
        z_th_short = z_th + (eff_short_buf - z_buffer if z_short_buffer is not None else 0.0)

    # 7. Position Sizing with production thresholds
    positions_full = generate_positions(Z_composite, z_th=z_th_prod, z_th_short=z_th_short, mode=position_mode, long_only=long_only)

    # 8. Date Filtering to OOS Evaluation Period
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not mask.any():
        print(f"    [WARNING] No data available for date range {start_date} to {end_date}. Falling back to recent history.")
        mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[mask].reset_index(drop=True)
    positions_oos = positions_full[mask]
    Z_composite_oos = Z_composite[mask.values if isinstance(mask, pd.Series) else mask]

    # 9. Backtest Simulation on OOS slice
    trade_returns_oos = full_trade_ret[mask.values if isinstance(mask, pd.Series) else mask]
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

    # 10. Trade log DataFrame creation & CSV export
    trade_log_df = build_trade_log_df(
        df_oos=df_oos,
        Z_composite_oos=Z_composite_oos,
        positions_oos=positions_oos,
        net_returns=net_returns,
        raw_returns=raw_returns,
        fees=fees,
        etf=etf,
        scheme=scheme_name,
        z_th=z_th_prod,
        asset_type=asset_type,
        trade_returns_arr=trade_returns_oos,
    )
    
    artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    fut_suffix = "_future" if use_future else ""
    trade_csv_path = artifacts_dir / f"trades_{scheme_name}_{etf}{fut_suffix}.csv"
    trade_log_df.to_csv(trade_csv_path, index=False)

    # 11. Calculate Metrics
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    metrics.update({
        "etf": etf,
        "asset_type": asset_type,
        "side": side,
        "scheme": scheme_name,
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th_prod,
        "z_th_long": z_th_prod,
        "z_th_short": z_th_short,
        "z_th_train_long": sweep_info.get("optimal_z_th_long", sweep_info.get("optimal_z_th")) if sweep_info else None,
        "z_th_train_short": sweep_info.get("optimal_z_th_short") if sweep_info else None,
        "z_buffer": z_buffer if auto_threshold else 0.0,
        "long_only": long_only,
        "use_future": use_future,
        "position_mode": position_mode,
        "dates": df_oos["date"].dt.strftime("%Y-%m-%d").tolist() if "date" in df_oos.columns else [],
        "cum_pnl": np.cumsum(net_returns).tolist(),
        "trade_log_df": trade_log_df,
    })

    print(f"    [RESULT] OOS ({metrics['period']}) | Cost Sharpe: {metrics['cost_sharpe']} | PnL: {metrics['total_pnl']} | WinRate: {metrics['win_rate_pct']}% | Intraday Trades: {metrics['n_trades']}/{metrics['n_days']}")

    return metrics



def main():
    parser = argparse.ArgumentParser(description="NewTrade Day-Model Factor Monetization Backtest Runner")
    parser.add_argument("-e", "--etf", type=str, default="all", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"], help="Trading side")
    parser.add_argument("--scheme", type=str, default="ew", choices=["ew", "icw", "score", "rank", "glm", "all"], help="Factor weighting scheme ('all' runs ew/icw/score/rank)")
    parser.add_argument("--z-th", type=str, default="auto", help="Conviction threshold Z score. 'auto' = train-sweep + buffer, or float value for fixed.")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Production buffer added to train-optimal threshold for long (default 0.1)")
    parser.add_argument("--z-short-buffer", type=float, default=None, help="Production buffer for short threshold (default: z_buffer + 0.1)")
    parser.add_argument("--position-mode", type=str, default="binary", choices=["binary", "tanh", "quadratic"], help="Position sizing mode")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in basis points (default 8.0 = 0.0008)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS Start Date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS End Date (YYYY-MM-DD)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output markdown report path (default: newtrade/REPORT.md)")

    
    # Scheme 4 (Rank Bounded Mapping) Options
    parser.add_argument("--rank-min-ratio", type=float, default=0.2, help="Scheme 4 w_min ratio relative to 1/N (default 0.2)")
    parser.add_argument("--rank-max-ratio", type=float, default=1.8, help="Scheme 4 w_max ratio relative to 1/N (default 1.8)")
    parser.add_argument("--rank-mapping", type=str, default="linear", choices=["linear", "power", "softmax", "top_k"], help="Scheme 4 rank mapping shape")
    parser.add_argument("--rank-power", type=float, default=2.0, help="Power exponent for 'power' rank mapping shape")
    parser.add_argument("--rank-top-k", type=int, default=None, help="Top K factors truncation threshold for 'top_k' rank mapping shape")
    parser.add_argument("--dynamic-ic", action="store_true", help="Enable zero-lookahead expanding rolling factor IC ranking")
    parser.add_argument("--long-only", action="store_true", help="Restrict to long-only trades (Spot ETF mode). Default: False (allows short trades).")
    parser.add_argument("--future", action="store_true", help="Trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF) instead of Spot ETF.")

    args = parser.parse_args()

    # Parse z_th: 'auto' or float
    auto_threshold = args.z_th.lower() == "auto"
    z_th_fixed = 0.5 if auto_threshold else float(args.z_th)

    etfs_to_run = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    schemes_to_run = ALL_SCHEMES if args.scheme.lower() == "all" else [args.scheme]
    fee_bps = args.fee_bps / 10000.0

    print("================================================================================")
    print(f"NewTrade Backtest Engine | Mode={'Future' if args.future else 'Spot ETF'} | Scheme={args.scheme.upper()} | z_th={args.z_th} | buffer={args.z_buffer} | LongOnly={args.long_only} | OOS=[{args.start_date} ~ {args.end_date}]")
    print("================================================================================")

    rank_kwargs = {
        "w_min_ratio": args.rank_min_ratio,
        "w_max_ratio": args.rank_max_ratio,
        "mapping_shape": args.rank_mapping,
        "power": args.rank_power,
        "top_k": args.rank_top_k,
    }

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
                z_short_buffer=args.z_short_buffer,
                auto_threshold=auto_threshold,
                rank_kwargs=rank_kwargs,
                dynamic_ic=args.dynamic_ic,
                long_only=args.long_only,
                use_future=args.future,
            )
            results.append(res)

    # Save aggregated Rank Bounded Weight trades CSV artifact
    rank_results = [r for r in results if r.get("scheme") == "rank" and r.get("status") == "SUCCESS"]
    if rank_results:
        all_rank_dfs = [r["trade_log_df"] for r in rank_results if r.get("trade_log_df") is not None]
        if all_rank_dfs:
            combined_rank_df = pd.concat(all_rank_dfs, ignore_index=True)
            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            fut_suffix = "_future" if args.future else ""
            combined_rank_csv = artifacts_dir / f"rank_bounded_trades{fut_suffix}.csv"
            combined_rank_df.to_csv(combined_rank_csv, index=False)
            print(f"Saved primary Rank Bounded trade log CSV to {combined_rank_csv}")

    # Generate Rank Bounded Weight plot artifact
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
                    ax.plot(dates, cum_pnl, label=f"{r['etf']} ({r.get('asset_type', 'Spot ETF')}) (Sharpe: {r['cost_sharpe']:.3f}, PnL: {r['total_pnl']:+.4f})", linewidth=1.8)
            
            mode_title = "Index Future" if args.future else "Spot ETF"
            ax.set_title(f"Rank Bounded Weight ({args.rank_mapping.upper()}) — {mode_title} OOS Net PnL (10:00 - 14:35 Intraday)", fontsize=11, fontweight='bold')
            ax.set_xlabel("Date", fontsize=9)
            ax.set_ylabel("Cumulative Net PnL", fontsize=9)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", frameon=True, fontsize=9)
            fig.tight_layout()

            artifacts_dir = HERE / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            fut_suffix = "_future" if args.future else ""
            chart_path = artifacts_dir / f"rank_bounded_equity{fut_suffix}.png"
            fig.savefig(chart_path)
            plt.close(fig)
            chart_rel_path = f"artifacts/rank_bounded_equity{fut_suffix}.png"
            print(f"Saved Rank Bounded equity chart to {chart_path}")
        except Exception as e:
            print(f"[WARNING] Failed to generate plot: {e}")

    # Print summary table
    print("\n================================================================================")
    print(f"NEWTRADE OOS BACKTEST PERFORMANCE SUMMARY ({'INDEX FUTURE' if args.future else 'SPOT ETF'}) (10:00 - 14:35 Intraday Trades)")
    print("================================================================================")
    
    headers = ["ETF", "Asset", "Side", "OOS Period", "Z_th", "Features", "Trades", "Cost Sharpe", "Raw Sharpe", "Total PnL", "Max DD", "Win Rate", "Turnover"]
    
    SCHEME_TITLES = {
        "rank": f"Rank Bounded Weight ({args.rank_mapping.capitalize()})",
        "ew": "Equal Weight (EW)",
        "icw": "IC Weight (ICW)",
        "score": "Score Weighted",
        "glm": "Linear GLM",
    }
    
    def _format_row(r):
        if r["status"] == "SUCCESS":
            z_l = r.get("z_th_long", r["z_th"])
            z_s = r.get("z_th_short", r["z_th"])
            tr_l = r.get("z_th_train_long")
            tr_s = r.get("z_th_train_short")
            
            if r.get("long_only", False) or z_l == z_s:
                z_th_str = f"{z_l:.2f}"
                if tr_l is not None:
                    z_th_str += f" (train:{tr_l:.2f})"
            else:
                z_th_str = f"L:{z_l:.2f}/S:{z_s:.2f}"
                if tr_l is not None and tr_s is not None:
                    z_th_str += f" (train L:{tr_l:.2f}/S:{tr_s:.2f})"
                elif tr_l is not None:
                    z_th_str += f" (train:{tr_l:.2f})"
            
            n_l = r.get("n_long_trades", 0)
            n_s = r.get("n_short_trades", 0)
            trades_str = f"{r.get('n_trades', 0)} ({n_l}L/{n_s}S)"

            win_l = f"{r['win_rate_long_pct']:.1f}%" if r.get("win_rate_long_pct") is not None else "N/A"
            win_s = f"{r['win_rate_short_pct']:.1f}%" if r.get("win_rate_short_pct") is not None else "N/A"
            win_str = f"{r['win_rate_pct']:.1f}% (L:{win_l}, S:{win_s})"

            return [
                r["etf"],
                r.get("asset_type", "Spot ETF"),
                r["side"],
                r["period"],
                z_th_str,
                str(r["n_features"]),
                trades_str,
                f"{r['cost_sharpe']:.3f}",
                f"{r['raw_sharpe']:.3f}",
                f"{r['total_pnl']:+.4f}",
                f"{r['max_drawdown']:.4f}",
                win_str,
                f"{r['ann_turnover']:.1f}x",
            ]
        else:
            return [
                r["etf"],
                r.get("asset_type", "N/A"),
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

    # Clean results before saving JSON (drop large arrays & DataFrames to keep JSON clean)
    clean_results = []
    for r in results:
        r_copy = dict(r)
        r_copy.pop("dates", None)
        r_copy.pop("cum_pnl", None)
        r_copy.pop("trade_log_df", None)
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
        f.write(f"- **Transaction Friction**: `{args.fee_bps} bps`\n")
        f.write(f"- **Rank Mapping Options**: `mapping={args.rank_mapping}, min_ratio={args.rank_min_ratio}, max_ratio={args.rank_max_ratio}, power={args.rank_power}`\n\n")
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

