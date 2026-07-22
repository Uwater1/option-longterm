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
from strategy import generate_positions, simulate_etf_spot, calculate_metrics

AVAILABLE_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]


def run_single_backtest(etf: str, side: str = "single", scheme_name: str = "ew", z_th: float = 0.5, 
                        position_mode: str = "binary", fee_bps: float = 0.0008, min_features: int = 10,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01") -> dict:
    """
    Run backtest for one ETF and side combination filtered to OOS date range.
    """
    print(f"--> Running Backtest: ETF={etf}, Side={side}, Scheme={scheme_name.upper()}, z_th={z_th}, Mode={position_mode}, OOS=[{start_date} to {end_date}]")
    
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
    Z_composite = scheme_func(Z_std, signs, pool=pool)

    # 6. Position Sizing
    positions_full = generate_positions(Z_composite, z_th=z_th, mode=position_mode, long_only=True)

    # 7. Date Filtering to OOS Evaluation Period
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not mask.any():
        print(f"    [WARNING] No data available for date range {start_date} to {end_date}. Falling back to recent history.")
        mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[mask].reset_index(drop=True)
    positions_oos = positions_full[mask]

    # 8. Backtest Simulation on OOS slice
    trade_returns = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df_oos.columns else df_oos["close"].pct_change().fillna(0.0).values
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns, positions_oos, fee_bps=fee_bps)

    # 9. Calculate Metrics
    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=df_oos["date"])
    metrics.update({
        "etf": etf,
        "side": side,
        "scheme": scheme_name,
        "status": "SUCCESS",
        "n_features": len(pool),
        "z_th": z_th,
        "position_mode": position_mode,
    })

    print(f"    [RESULT] OOS ({metrics['period']}) | Cost Sharpe: {metrics['cost_sharpe']} | PnL: {metrics['total_pnl']} | WinRate: {metrics['win_rate_pct']}% | Intraday Trades: {metrics['n_trades']}/{metrics['n_days']}")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="NewTrade Day-Model Factor Monetization Backtest Runner")
    parser.add_argument("-e", "--etf", type=str, default="all", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"], help="Trading side")
    parser.add_argument("--scheme", type=str, default="ew", choices=["ew", "icw", "score", "rank", "glm"], help="Factor weighting scheme")
    parser.add_argument("--z-th", type=float, default=0.5, help="Conviction threshold Z score")
    parser.add_argument("--position-mode", type=str, default="binary", choices=["binary", "tanh"], help="Position sizing mode")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in basis points (default 8.0 = 0.0008)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS Start Date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS End Date (YYYY-MM-DD)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output markdown report path")

    args = parser.parse_args()

    etfs_to_run = AVAILABLE_ETFS if args.etf.lower() == "all" else [args.etf]
    fee_bps = args.fee_bps / 10000.0

    print("================================================================================")
    print(f"NewTrade Backtest Engine | Scheme={args.scheme.upper()} | z_th={args.z_th} | OOS=[{args.start_date} ~ {args.end_date}]")
    print("================================================================================")

    results = []
    for etf in etfs_to_run:
        res = run_single_backtest(
            etf=etf,
            side=args.side,
            scheme_name=args.scheme,
            z_th=args.z_th,
            position_mode=args.position_mode,
            fee_bps=fee_bps,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        results.append(res)

    # Print summary table
    print("\n================================================================================")
    print("NEWTRADE OOS BACKTEST PERFORMANCE SUMMARY (10:00 - 14:35 Intraday Trades)")
    print("================================================================================")
    
    headers = ["ETF", "Side", "OOS Period", "Trade Window", "Status", "Features", "Intraday Trades", "Cost Sharpe", "Raw Sharpe", "Total PnL", "Max DD", "Win Rate", "Turnover"]
    table_rows = []
    
    for r in results:
        if r["status"] == "SUCCESS":
            row = [
                r["etf"],
                r["side"],
                r["period"],
                r.get("trade_window", "10:00-14:35"),
                r["status"],
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
            row = [
                r["etf"],
                r["side"],
                r.get("period", "N/A"),
                "10:00-14:35",
                r["status"],
                str(r["n_features"]),
                "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
            ]
        table_rows.append(row)

    # Render Markdown table
    md_table = []
    md_table.append("| " + " | ".join(headers) + " |")
    md_table.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in table_rows:
        md_table.append("| " + " | ".join(row) + " |")

    report_content = "\n".join(md_table)
    print("\n" + report_content + "\n")

    # Save output if requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            f.write("# NewTrade OOS Backtest Report\n\n")
            f.write(f"- **OOS Evaluation Period**: `{args.start_date} ~ {args.end_date}`\n")
            f.write(f"- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`\n")
            f.write(f"- **Scheme**: `{args.scheme.upper()}`\n")
            f.write(f"- **Conviction Threshold ($Z_{{th}}$)**: `{args.z_th}`\n")
            f.write(f"- **Position Mode**: `{args.position_mode}`\n")
            f.write(f"- **Transaction Friction**: `{args.fee_bps} bps`\n\n")
            f.write(report_content + "\n")
        print(f"Saved backtest report to {out_path}")

    # Save JSON result artifact in newtrade/data/
    data_dir = HERE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / f"backtest_results_{args.scheme}_{args.side}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved JSON results to {json_path}")


if __name__ == "__main__":
    main()
