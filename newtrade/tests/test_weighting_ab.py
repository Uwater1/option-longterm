#!/usr/bin/env python3
"""
A/B Test: Weighting Pipeline Comparison (Post-Cluster Era)

Question: After ONC cluster constraint + rolling tail IC 480d upgrades, is the current
production weighting (Rolling Tail IC + ICW shrinkage) still optimal? Or do multi-score
(IC + IR + Monotonicity) pipelines now outperform?

11 arms × 3 ETFs × per-year breakdown = comprehensive pipeline comparison.

Arms:
  Group A — Metric comparison (ICW scheme fixed):
    1. TailIC_ICW (BASELINE): rolling_tail_480d + ICW shrinkage
    2. ExpIC_ICW: expanding IC + ICW shrinkage

  Group B — Multi-score variants (Score scheme unless noted):
    3. Multi_50_50_ScoreW: (IC=0.50, IR=0, Mono=0.50) mono=750d
    4. Multi_20_80_ScoreW: (IC=0.20, IR=0, Mono=0.80) mono=750d
    5. Multi_75_25_ScoreW: (IC=0.75, IR=0, Mono=0.25) mono=750d
    6. Multi_35_30_35_ScoreW: (IC=0.35, IR=0.30, Mono=0.35) mono=750d
    7. Multi_50_50_Mono252: (IC=0.50, IR=0, Mono=0.50) mono=252d
    8. Multi_50_50_ICW: multi-score(0.50/0/0.50) matrix + ICW shrinkage weighting

  Group C — Weighting comparison (Rolling Tail IC metric fixed):
    9. TailIC_ScoreW: rolling_tail_480d + score-proportional
   10. TailIC_EW: rolling_tail_480d + equal weight
   11. TailIC_Rank: rolling_tail_480d + rank bounded (linear 0.2-1.8)

Usage:
    python newtrade/tests/test_weighting_ab.py
    python newtrade/tests/test_weighting_ab.py --fee-bps 12
    python newtrade/tests/test_weighting_ab.py --start-date 2023-01-01
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from run_backtest import run_single_backtest, resolve_ic_ema_span

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
YEARS = [2022, 2023, 2024, 2025]

# ─── Arm Definitions ───────────────────────────────────────────────────────────
# Each arm: (label, scheme, ic_mode, dynamic_metric, score_weights, mono_window, tail_window, tail_pct)
ARMS = [
    # Group A: Metric comparison (ICW scheme)
    {
        "label": "TailIC_ICW",
        "group": "A",
        "scheme": "icw",
        "ic_mode": "rolling_tail",
        "dynamic_metric": "ic",
        "score_weights": None,
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
        "baseline": True,
    },
    {
        "label": "ExpIC_ICW",
        "group": "A",
        "scheme": "icw",
        "ic_mode": "expanding",
        "dynamic_metric": "ic",
        "score_weights": None,
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    # Group B: Multi-score variants
    {
        "label": "Multi_50_50_ScoreW",
        "group": "B",
        "scheme": "score",
        "ic_mode": "expanding",
        "dynamic_metric": "multi",
        "score_weights": (0.50, 0.00, 0.50),
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "Multi_20_80_ScoreW",
        "group": "B",
        "scheme": "score",
        "ic_mode": "expanding",
        "dynamic_metric": "multi",
        "score_weights": (0.20, 0.00, 0.80),
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "Multi_75_25_ScoreW",
        "group": "B",
        "scheme": "score",
        "ic_mode": "expanding",
        "dynamic_metric": "multi",
        "score_weights": (0.75, 0.00, 0.25),
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "Multi_35_30_35_ScoreW",
        "group": "B",
        "scheme": "score",
        "ic_mode": "expanding",
        "dynamic_metric": "multi",
        "score_weights": (0.35, 0.30, 0.35),
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "Multi_50_50_Mono252",
        "group": "B",
        "scheme": "score",
        "ic_mode": "expanding",
        "dynamic_metric": "multi",
        "score_weights": (0.50, 0.00, 0.50),
        "mono_window": 252,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "Multi_50_50_ICW",
        "group": "B",
        "scheme": "icw",
        "ic_mode": "expanding",
        "dynamic_metric": "multi",
        "score_weights": (0.50, 0.00, 0.50),
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    # Group C: Weighting comparison (Rolling Tail IC metric)
    {
        "label": "TailIC_ScoreW",
        "group": "C",
        "scheme": "score",
        "ic_mode": "rolling_tail",
        "dynamic_metric": "ic",
        "score_weights": None,
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "TailIC_EW",
        "group": "C",
        "scheme": "ew",
        "ic_mode": "rolling_tail",
        "dynamic_metric": "ic",
        "score_weights": None,
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
    {
        "label": "TailIC_Rank",
        "group": "C",
        "scheme": "rank",
        "ic_mode": "rolling_tail",
        "dynamic_metric": "ic",
        "score_weights": None,
        "mono_window": 750,
        "tail_window": 480,
        "tail_pct": 0.10,
    },
]


def run_arm(arm: dict, etf: str, start_date: str, end_date: str,
            fee_bps: float, z_buffer: float) -> dict:
    """Run a single arm for one ETF."""
    rank_kwargs = {
        "top_k": 10,
        "ic_ema_span": resolve_ic_ema_span(etf, None),
        "dynamic_metric": arm["dynamic_metric"],
        "mono_window": arm["mono_window"],
    }
    if arm["score_weights"] is not None:
        rank_kwargs["score_weights"] = arm["score_weights"]
    # Rank scheme params
    if arm["scheme"] == "rank":
        rank_kwargs["mapping_shape"] = "linear"
        rank_kwargs["w_min_ratio"] = 0.2
        rank_kwargs["w_max_ratio"] = 1.8

    res = run_single_backtest(
        etf=etf, side="single", scheme_name=arm["scheme"], z_th=0.5,
        position_mode="binary", fee_bps=fee_bps,
        start_date=start_date, end_date=end_date,
        z_buffer=z_buffer, auto_threshold=True, dynamic_ic=True,
        rank_kwargs=rank_kwargs,
        ic_mode=arm["ic_mode"],
        tail_window=arm["tail_window"], tail_pct=arm["tail_pct"],
        use_stoploss=True,
    )
    return res


def main():
    parser = argparse.ArgumentParser(description="Weighting Pipeline A/B Test (11 arms × 3 ETFs)")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Transaction fee in bps (default: 8.0)")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Production threshold buffer (default: 0.1)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS start date")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS end date")
    parser.add_argument("--yearly", action="store_true", default=True, help="Run per-year breakdown (default: True)")
    parser.add_argument("--no-yearly", dest="yearly", action="store_false", help="Skip per-year breakdown")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0

    print("=" * 90)
    print("WEIGHTING PIPELINE A/B TEST - 11 Arms x 3 ETFs")
    print(f"OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps | Z-buffer={args.z_buffer}")
    print("=" * 90)

    # ─── Phase 1: Full-period backtests ────────────────────────────────────────
    results = []
    total_runs = len(ARMS) * len(AVAILABLE_ETFS)
    run_idx = 0

    for arm in ARMS:
        for etf in AVAILABLE_ETFS:
            run_idx += 1
            tag = "*" if arm.get("baseline") else " "
            print(f"\n[{run_idx:2d}/{total_runs}] {tag} {arm['label']} - {etf}...")
            res = run_arm(arm, etf, args.start_date, args.end_date, fee_bps, args.z_buffer)
            if res.get("status") == "SUCCESS":
                results.append({
                    "Arm": arm["label"],
                    "Group": arm["group"],
                    "ETF": etf,
                    "Features": res["n_features"],
                    "Trades": res["n_trades"],
                    "CostSharpe": res["cost_sharpe"],
                    "RawSharpe": res["raw_sharpe"],
                    "TotalPnL": res["total_pnl"],
                    "MaxDD": res["max_drawdown"],
                    "WinRate": res["win_rate_pct"],
                    "Turnover": res.get("ann_turnover", 0),
                })
            else:
                print(f"    ! SKIPPED: {res.get('status', 'UNKNOWN')}")

    if not results:
        print("\nERROR: No successful backtests. Check data availability.")
        return

    df_full = pd.DataFrame(results)

    # ─── Phase 2: Per-year breakdown ──────────────────────────────────────────
    yearly_results = []
    if args.yearly:
        print("\n" + "=" * 90)
        print("PER-YEAR BREAKDOWN")
        print("=" * 90)
        for year in YEARS:
            y_start = f"{year}-01-01"
            y_end = f"{year + 1}-01-01"
            for arm in ARMS:
                for etf in AVAILABLE_ETFS:
                    res = run_arm(arm, etf, y_start, y_end, fee_bps, args.z_buffer)
                    if res.get("status") == "SUCCESS":
                        yearly_results.append({
                            "Arm": arm["label"],
                            "Group": arm["group"],
                            "ETF": etf,
                            "Year": year,
                            "CostSharpe": res["cost_sharpe"],
                            "TotalPnL": res["total_pnl"],
                            "Trades": res["n_trades"],
                        })

    # ─── Report: Full-period ranking ──────────────────────────────────────────
    print("\n" + "=" * 90)
    print("FULL-PERIOD RESULTS - RANKED BY AVG COST SHARPE")
    print("=" * 90)

    avg_by_arm = df_full.groupby(["Arm", "Group"]).agg(
        AvgSharpe=("CostSharpe", "mean"),
        AvgPnL=("TotalPnL", "mean"),
        AvgMaxDD=("MaxDD", "mean"),
        AvgWinRate=("WinRate", "mean"),
        AvgTurnover=("Turnover", "mean"),
    ).reset_index().sort_values("AvgSharpe", ascending=False)

    # Mark baseline
    baseline_label = next(a["label"] for a in ARMS if a.get("baseline"))
    baseline_sharpe = avg_by_arm.loc[avg_by_arm["Arm"] == baseline_label, "AvgSharpe"].values
    base_sr = baseline_sharpe[0] if len(baseline_sharpe) > 0 else 0.0

    print(f"\n{'Rank':<5} {'Arm':<25} {'Grp':<4} {'AvgSharpe':>10} {'Δ vs Base':>10} {'AvgPnL':>10} {'AvgMaxDD':>9} {'AvgWR%':>7} {'Turnover':>9}")
    print("-" * 95)
    for i, row in avg_by_arm.iterrows():
        rank = avg_by_arm.index.get_loc(i) + 1
        delta = row["AvgSharpe"] - base_sr
        marker = " *" if row["Arm"] == baseline_label else ""
        print(f"{rank:<5} {row['Arm']:<25} {row['Group']:<4} {row['AvgSharpe']:>10.3f} {delta:>+10.3f} {row['AvgPnL']:>10.4f} {row['AvgMaxDD']:>9.4f} {row['AvgWinRate']:>7.1f} {row['AvgTurnover']:>9.2f}{marker}")

    # ─── Report: Per-ETF detail ────────────────────────────────────────────────
    print("\n" + "-" * 90)
    print("PER-ETF DETAIL")
    print("-" * 90)
    for etf in AVAILABLE_ETFS:
        sub = df_full[df_full["ETF"] == etf].sort_values("CostSharpe", ascending=False)
        print(f"\n  {etf}:")
        print(f"  {'Arm':<25} {'CostSharpe':>10} {'TotalPnL':>10} {'MaxDD':>8} {'WR%':>6} {'Trades':>7}")
        for _, r in sub.iterrows():
            marker = " *" if r["Arm"] == baseline_label else ""
            print(f"  {r['Arm']:<25} {r['CostSharpe']:>10.3f} {r['TotalPnL']:>10.4f} {r['MaxDD']:>8.4f} {r['WinRate']:>6.1f} {r['Trades']:>7}{marker}")

    # ─── Report: Per-ETF winner ────────────────────────────────────────────────
    print("\n" + "-" * 90)
    print("PER-ETF WINNER")
    print("-" * 90)
    for etf in AVAILABLE_ETFS:
        sub = df_full[df_full["ETF"] == etf].sort_values("CostSharpe", ascending=False)
        if not sub.empty:
            best = sub.iloc[0]
            delta = best["CostSharpe"] - base_sr
            print(f"  {etf}: {best['Arm']} (Sharpe={best['CostSharpe']:.3f}, Δ={delta:+.3f})")

    # ─── Report: Per-year stability ───────────────────────────────────────────
    if yearly_results:
        df_yearly = pd.DataFrame(yearly_results)

        print("\n" + "=" * 90)
        print("PER-YEAR STABILITY - AVG COST SHARPE BY ARM x YEAR")
        print("=" * 90)

        pivot = df_yearly.groupby(["Arm", "Year"])["CostSharpe"].mean().unstack(fill_value=0)
        pivot["Avg"] = pivot.mean(axis=1)
        pivot["Std"] = pivot[YEARS].std(axis=1)
        pivot["Min"] = pivot[YEARS].min(axis=1)
        pivot = pivot.sort_values("Avg", ascending=False)

        print(f"\n{'Arm':<25}", end="")
        for y in YEARS:
            print(f" {y:>8}", end="")
        print(f" {'Avg':>8} {'Std':>7} {'Min':>7}")
        print("-" * 90)
        for arm_label, row in pivot.iterrows():
            marker = " *" if arm_label == baseline_label else ""
            print(f"{arm_label:<25}", end="")
            for y in YEARS:
                print(f" {row[y]:>8.3f}", end="")
            print(f" {row['Avg']:>8.3f} {row['Std']:>7.3f} {row['Min']:>7.3f}{marker}")

        # Yearly winner count
        print("\n" + "-" * 90)
        print("YEARLY WIN COUNT (how many years each arm is #1 avg across ETFs)")
        print("-" * 90)
        yearly_avg = df_yearly.groupby(["Arm", "Year"])["CostSharpe"].mean().reset_index()
        win_counts = defaultdict(int)
        for year in YEARS:
            yr_sub = yearly_avg[yearly_avg["Year"] == year].sort_values("CostSharpe", ascending=False)
            if not yr_sub.empty:
                winner = yr_sub.iloc[0]["Arm"]
                win_counts[winner] += 1
                print(f"  {year}: {winner} (Sharpe={yr_sub.iloc[0]['CostSharpe']:.3f})")

        print(f"\n  Win counts: ", end="")
        for arm_label, cnt in sorted(win_counts.items(), key=lambda x: -x[1]):
            print(f"{arm_label}={cnt}  ", end="")
        print()

    # ─── Save CSV ──────────────────────────────────────────────────────────────
    out_csv = Path(args.output) if args.output else HERE / "weighting_ab_results.csv"
    df_full.to_csv(out_csv, index=False)
    print(f"\nSaved full-period results to {out_csv}")

    if yearly_results:
        out_yearly = out_csv.with_name(out_csv.stem + "_yearly.csv")
        df_yearly.to_csv(out_yearly, index=False)
        print(f"Saved yearly results to {out_yearly}")

    print("\n[OK] A/B test complete.")


if __name__ == "__main__":
    main()
