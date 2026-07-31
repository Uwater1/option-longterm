#!/usr/bin/env python3
"""
Experiment: Rolling Tail IC vs Expanding Total IC for Feature Weighting.

Tests whether replacing the expanding total Pearson IC (current production) with
a rolling tail Spearman IC (aligned with day-model-new admission criteria) improves
OOS performance.

Configs tested:
  - Baseline: Expanding total IC (current system)
  - Rolling Tail IC window=189d (9 months, ~38 tail obs)
  - Rolling Tail IC window=252d (1 year, ~50 tail obs)
  - Rolling Tail IC window=378d (1.5 years, ~76 tail obs)
  - Rolling Tail IC window=504d (2 years, ~100 tail obs)

All rolling tail configs use tail_pct=0.10 (two-sided 10%, matching 'single' admission).
Evaluates OOS performance (2022-01 ~ 2026-01) under 8 bps friction on 300ETF, 500ETF, 159915ETF.
"""

import sys
import argparse
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from run_backtest import run_single_backtest, resolve_ic_ema_span

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
TAIL_WINDOWS = [240, 360, 480, 600, 720]  # 1yr, 1.5yr, 2yr, 2.5yr, 3yr (China ~240 trading days/yr)
TAIL_PCT = 0.10  # Fixed: matches 'single' side admission


def main():
    parser = argparse.ArgumentParser(description="Rolling Tail IC vs Expanding IC A/B Test")
    parser.add_argument("--scheme", type=str, default="icw", help="Weighting scheme (default: icw)")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Production threshold buffer (default: 0.1)")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in bps (default: 8.0)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS start date")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS end date")
    parser.add_argument("--pool-suffix", type=str, default="", help="Pool period suffix (e.g., '_p2015_2023')")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0

    results = []

    print("=" * 80)
    print("ROLLING TAIL IC vs EXPANDING IC — A/B TEST")
    print(f"Scheme={args.scheme.upper()} | OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps | Tail={TAIL_PCT*100:.0f}% | Pool={args.pool_suffix or 'default'}")
    print("=" * 80)

    # 1. Baseline (Expanding Total IC)
    for etf in AVAILABLE_ETFS:
        print(f"\n[BASELINE] Expanding Total IC — {etf}...")
        res = run_single_backtest(
            etf=etf, side="single", scheme_name=args.scheme, z_th=0.5,
            position_mode="binary", fee_bps=fee_bps,
            start_date=args.start_date, end_date=args.end_date,
            z_buffer=args.z_buffer, auto_threshold=True, dynamic_ic=True,
            rank_kwargs={"top_k": 10, "ic_ema_span": resolve_ic_ema_span(etf, None)},
            ic_mode="expanding",
            cluster_suffix=args.pool_suffix,
        )
        if res.get("status") == "SUCCESS":
            res["ic_mode"] = "expanding"
            res["tail_window"] = "N/A"
            results.append(res)

    # 2. Rolling Tail IC variants
    for window in TAIL_WINDOWS:
        for etf in AVAILABLE_ETFS:
            print(f"\n[ROLLING TAIL] Window={window}d — {etf}...")
            res = run_single_backtest(
                etf=etf, side="single", scheme_name=args.scheme, z_th=0.5,
                position_mode="binary", fee_bps=fee_bps,
                start_date=args.start_date, end_date=args.end_date,
                z_buffer=args.z_buffer, auto_threshold=True, dynamic_ic=True,
                rank_kwargs={"top_k": 10, "ic_ema_span": resolve_ic_ema_span(etf, None)},
                ic_mode="rolling_tail", tail_window=window, tail_pct=TAIL_PCT,
                cluster_suffix=args.pool_suffix,
            )
            if res.get("status") == "SUCCESS":
                res["ic_mode"] = "rolling_tail"
                res["tail_window"] = window
                results.append(res)

    # 3. Rolling Tail 360d + EMA 90 (smoothed ranking)
    for etf in AVAILABLE_ETFS:
        print(f"\n[ROLLING TAIL + EMA90] Window=360d — {etf}...")
        res = run_single_backtest(
            etf=etf, side="single", scheme_name=args.scheme, z_th=0.5,
            position_mode="binary", fee_bps=fee_bps,
            start_date=args.start_date, end_date=args.end_date,
            z_buffer=args.z_buffer, auto_threshold=True, dynamic_ic=True,
            rank_kwargs={"top_k": 10, "ic_ema_span": 90},
            ic_mode="rolling_tail", tail_window=360, tail_pct=TAIL_PCT,
            cluster_suffix=args.pool_suffix,
        )
        if res.get("status") == "SUCCESS":
            res["ic_mode"] = "rolling_tail+EMA90"
            res["tail_window"] = 360
            results.append(res)

    # Summary
    summary_rows = []
    for r in results:
        summary_rows.append({
            "ETF": r["etf"],
            "IC Mode": r["ic_mode"],
            "Window": r["tail_window"],
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

    print("\n" + "=" * 80)
    print("ROLLING TAIL IC A/B TEST — RESULTS SUMMARY")
    print("=" * 80)
    print(df_sum.to_string(index=False))

    # Cross-ETF average by IC mode + window
    avg_df = df_sum.groupby(["IC Mode", "Window"])[["CostSharpe", "TotalPnL", "MaxDD", "Turnover"]].mean().reset_index()
    avg_df = avg_df.sort_values("CostSharpe", ascending=False)
    print("\n" + "-" * 80)
    print("CROSS-ETF AVERAGE BY IC MODE")
    print("-" * 80)
    print(avg_df.to_string(index=False))

    # Per-ETF best variant
    print("\n" + "-" * 80)
    print("PER-ETF BEST VARIANT")
    print("-" * 80)
    for etf in AVAILABLE_ETFS:
        sub = df_sum[df_sum["ETF"] == etf].sort_values("CostSharpe", ascending=False)
        if not sub.empty:
            best = sub.iloc[0]
            base = sub[sub["IC Mode"] == "expanding"]
            base_sr = base.iloc[0]["CostSharpe"] if not base.empty else 0.0
            delta = best["CostSharpe"] - base_sr
            print(f"  {etf}: Best={best['IC Mode']} (W={best['Window']}) Sharpe={best['CostSharpe']:.3f} | Baseline={base_sr:.3f} | Delta={delta:+.3f}")

    # Save
    out_csv = Path(args.output) if args.output else HERE / "rolling_tail_ic_results.csv"
    df_sum.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")


if __name__ == "__main__":
    main()
