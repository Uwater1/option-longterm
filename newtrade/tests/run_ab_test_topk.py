#!/usr/bin/env python3
"""
Top-K Feature Selection A/B Test Suite for NewTrade framework.
Compares:
  - Baseline: Full admitted pool features (N_all)
  - Static Top-K: Top K factors selected statically by pool metadata deflated_ic
  - Dynamic Top-K Rolling Score: Top K factors selected expanding daily by rolling 3-year score
  - Dynamic Top-K Rolling IC: Top K factors selected expanding daily by rolling IC

Evaluates across 300ETF, 500ETF, 159915ETF over OOS period 2022-01-01 ~ 2026-01-01 under 8 bps friction.
"""

import sys
import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_backtest import run_single_backtest
from robustness import deflated_sharpe_ratio, run_cpcv_backtest

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
TOP_K_VALUES = [5, 8, 10, 12, 15]


def main():
    parser = argparse.ArgumentParser(description="Run Top-K Feature Selection A/B Test Suite")
    parser.add_argument("--scheme", type=str, default="ensemble", help="Weighting scheme (default: ensemble)")
    parser.add_argument("--z-th", type=str, default="auto", help="Conviction threshold ('auto' or float, default: auto)")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Production threshold buffer (default: 0.1)")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in bps (default: 8.0)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS start date")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS end date")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output markdown report path")
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0
    auto_threshold = args.z_th.lower() == "auto"
    z_th_fixed = 0.5 if auto_threshold else float(args.z_th)

    results = []

    print("================================================================================")
    print("STARTING TOP-K FEATURE SELECTION A/B TEST SUITE")
    print(f"Scheme={args.scheme.upper()} | OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps")
    print("================================================================================")

    # 1. Baseline (Full Pool)
    for etf in AVAILABLE_ETFS:
        print(f"\n[A/B TEST] Running Baseline (Full Pool) for {etf}...")
        res = run_single_backtest(
            etf=etf, side="single", scheme_name=args.scheme, z_th=z_th_fixed,
            position_mode="binary", fee_bps=fee_bps, start_date=args.start_date, end_date=args.end_date,
            z_buffer=args.z_buffer, auto_threshold=auto_threshold, dynamic_ic=True,
            rank_kwargs={"dynamic_metric": "multi", "top_k": None}
        )
        if res.get("status") == "SUCCESS":
            res["ab_group"] = "Baseline (Full Pool)"
            res["top_k_val"] = "All"
            results.append(res)

    # 2. Static Top-K
    for k in TOP_K_VALUES:
        for etf in AVAILABLE_ETFS:
            print(f"\n[A/B TEST] Running Static Top-{k} for {etf}...")
            res = run_single_backtest(
                etf=etf, side="single", scheme_name=args.scheme, z_th=z_th_fixed,
                position_mode="binary", fee_bps=fee_bps, start_date=args.start_date, end_date=args.end_date,
                z_buffer=args.z_buffer, auto_threshold=auto_threshold, dynamic_ic=False,
                rank_kwargs={"top_k": k}
            )
            if res.get("status") == "SUCCESS":
                res["ab_group"] = f"Static Top-{k}"
                res["top_k_val"] = str(k)
                results.append(res)

    # 3. Dynamic Top-K Rolling Score (multi-metric)
    for k in TOP_K_VALUES:
        for etf in AVAILABLE_ETFS:
            print(f"\n[A/B TEST] Running Dynamic Top-{k} (Rolling Score) for {etf}...")
            res = run_single_backtest(
                etf=etf, side="single", scheme_name=args.scheme, z_th=z_th_fixed,
                position_mode="binary", fee_bps=fee_bps, start_date=args.start_date, end_date=args.end_date,
                z_buffer=args.z_buffer, auto_threshold=auto_threshold, dynamic_ic=True,
                rank_kwargs={"dynamic_metric": "multi", "top_k": k}
            )
            if res.get("status") == "SUCCESS":
                res["ab_group"] = f"Dynamic Top-{k} (Score)"
                res["top_k_val"] = str(k)
                results.append(res)

    # 4. Dynamic Top-K Rolling IC
    for k in TOP_K_VALUES:
        for etf in AVAILABLE_ETFS:
            print(f"\n[A/B TEST] Running Dynamic Top-{k} (Rolling IC) for {etf}...")
            res = run_single_backtest(
                etf=etf, side="single", scheme_name=args.scheme, z_th=z_th_fixed,
                position_mode="binary", fee_bps=fee_bps, start_date=args.start_date, end_date=args.end_date,
                z_buffer=args.z_buffer, auto_threshold=auto_threshold, dynamic_ic=True,
                rank_kwargs={"dynamic_metric": "ic", "top_k": k}
            )
            if res.get("status") == "SUCCESS":
                res["ab_group"] = f"Dynamic Top-{k} (IC)"
                res["top_k_val"] = str(k)
                results.append(res)

    # Convert to DataFrame for summary
    summary_rows = []
    for r in results:
        summary_rows.append({
            "ETF": r["etf"],
            "Group": r["ab_group"],
            "TopK": r["top_k_val"],
            "Features": r["n_features"],
            "CostSharpe": r["cost_sharpe"],
            "RawSharpe": r["raw_sharpe"],
            "TotalPnL": r["total_pnl"],
            "MaxDD": r["max_drawdown"],
            "WinRate": r["win_rate_pct"],
            "Turnover": r["ann_turnover"],
            "Trades": r["n_trades"],
        })

    df_sum = pd.DataFrame(summary_rows)

    print("\n================================================================================")
    print("TOP-K FEATURE SELECTION A/B TEST RESULTS SUMMARY")
    print("================================================================================")
    print(df_sum.to_string(index=False))

    # Build Markdown Report
    report_path = Path(args.output) if args.output else HERE / "TOPK_AB_TEST_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Top-K Feature Selection A/B Test Report\n\n")
        f.write(f"- **OOS Period**: `{args.start_date} ~ {args.end_date}`\n")
        f.write(f"- **Scheme**: `{args.scheme.upper()}`\n")
        f.write(f"- **Transaction Fee**: `{args.fee_bps} bps`\n\n")
        
        f.write("## 1. Executive Summary & Comparison\n\n")
        f.write("| ETF | Group | TopK | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for row in summary_rows:
            f.write(f"| {row['ETF']} | {row['Group']} | {row['TopK']} | {row['Features']} | {row['Trades']} | "
                    f"{row['CostSharpe']:.3f} | {row['RawSharpe']:.3f} | {row['TotalPnL']:+.4f} | {row['MaxDD']:.4f} | "
                    f"{row['WinRate']:.1f}% | {row['Turnover']:.1f}x |\n")
        
        f.write("\n## 2. Key Insights per ETF\n\n")
        for etf in AVAILABLE_ETFS:
            sub = df_sum[df_sum["ETF"] == etf].sort_values("CostSharpe", ascending=False)
            if not sub.empty:
                best = sub.iloc[0]
                base = sub[sub["Group"] == "Baseline (Full Pool)"]
                base_sr = base.iloc[0]["CostSharpe"] if not base.empty else 0.0
                f.write(f"### {etf}\n")
                f.write(f"- **Baseline (Full Pool)**: Cost Sharpe = `{base_sr:.3f}`\n")
                f.write(f"- **Best Variant**: `{best['Group']}` -> Cost Sharpe = `{best['CostSharpe']:.3f}` (Delta = `{best['CostSharpe'] - base_sr:+.3f}`)\n")
                f.write(f"- **Win Rate**: `{best['WinRate']:.1f}%`, Total PnL = `{best['TotalPnL']:+.4f}`\n\n")

    print(f"\nSaved A/B Test report to {report_path}")

    # Save JSON artifact
    json_path = HERE / "data" / "topk_ab_test_results.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(summary_rows, f, indent=2)
    print(f"Saved JSON artifact to {json_path}")


if __name__ == "__main__":
    main()
