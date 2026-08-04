#!/usr/bin/env python3
"""
Follow-up to the selTailIC_wSortino finding — two questions:

Q1. WEIGHT BLEND: Is pure-Sortino weighting optimal, or should the WEIGHT score
    blend Sortino + TailIC? Selection stays tail IC (ER=20, REPORT.md config).
    Weight score = w_ic * rank(tailIC_480d) + (1 - w_ic) * rank(sortino_480d)
    swept over w_ic ∈ {0.00 (=current winner), 0.25, 0.50, 0.75}.
    Reference: raw-tailIC-weights baseline (REPORT.md numbers).

Q2. YEARLY STABILITY: Do the conclusions hold year-by-year (2022..2025)?
    Each year re-sweeps the Z threshold on data before Jan 1 of that year
    (same protocol as REPORT_{year}.md).

Usage:
    python newtrade/tests/test_weight_blend_yearly_ab.py
    python newtrade/tests/test_weight_blend_yearly_ab.py --skip-yearly
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from test_exit_rank_sortino_ab import (run_icw_backtest, precompute,
                                       AVAILABLE_ETFS)
from utils import composite_tailic_risk_score

BLEND_W_IC = [0.00, 0.25, 0.50, 0.75]
YEARS = [2022, 2023, 2024, 2025]
REPORT_BASELINE = {"300ETF": 0.145, "500ETF": 0.942, "159915ETF": 0.965}


def blend_label(w_ic: float) -> str:
    return f"wSortino_{int((1-w_ic)*100)}_{int(w_ic*100)}"  # (sortino%_tailic%)


def run_config(etf: str, start: str, end: str, fee_bps: float, z_buffer: float,
               config: str, scores_by_w: dict) -> dict:
    """config: 'baseline' | 'w_ic=0.00' | 'w_ic=0.25' | ... (weight-score blend)."""
    if config == "baseline":
        return run_icw_backtest(etf, start, end, fee_bps, z_buffer, exit_rank=20)
    w_ic = float(config.split("=")[1])
    return run_icw_backtest(etf, start, end, fee_bps, z_buffer, exit_rank=20,
                            ic_override=None, weight_ic_override=scores_by_w[w_ic])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fee-bps", type=float, default=8.0)
    parser.add_argument("--z-buffer", type=float, default=0.1)
    parser.add_argument("--skip-yearly", action="store_true")
    parser.add_argument("-o", "--output", type=str, default=None)
    args = parser.parse_args()
    fee_bps = args.fee_bps / 10000.0

    print("=" * 100)
    print("WEIGHT-BLEND SWEEP + YEARLY STABILITY (selection = tail IC, ER=20)")
    print("=" * 100)

    # ─── Precompute matrices & blend weight scores per ETF ────────────────────
    etf_assets = {}
    for etf in AVAILABLE_ETFS:
        mats = precompute(etf)
        if mats is None:
            continue
        scores_by_w = {w: composite_tailic_risk_score(mats["ic"], mats["sortino"], w)
                       for w in BLEND_W_IC}
        etf_assets[etf] = scores_by_w

    # ─── Phase 1: blend sweep on full OOS ─────────────────────────────────────
    print("\n>>> PHASE 1: WEIGHT-BLEND SWEEP (OOS 2022-01-01 ~ 2026-01-01)")
    rows = []
    for etf, scores_by_w in etf_assets.items():
        # Baseline reference
        print(f"\n[baseline] {etf}...")
        res = run_config(etf, "2022-01-01", "2026-01-01", fee_bps, args.z_buffer,
                         "baseline", scores_by_w)
        if res.get("status") == "SUCCESS":
            exp = REPORT_BASELINE[etf]
            d = res["cost_sharpe"] - exp
            flag = "OK" if abs(d) < 0.005 else "MISMATCH!"
            print(f"    Sharpe={res['cost_sharpe']:.3f} (REPORT.md={exp:.3f}, Δ={d:+.4f}) [{flag}]")
            rows.append({"Phase": "full", "Config": "baseline(tailIC_wt)", "ETF": etf,
                         "CostSharpe": res["cost_sharpe"], "TotalPnL": res["total_pnl"],
                         "MaxDD": res["max_drawdown"], "WinRate": res["win_rate_pct"],
                         "Trades": res["n_trades"]})
        for w_ic in BLEND_W_IC:
            cfg = f"w_ic={w_ic:.2f}"
            lab = blend_label(w_ic)
            print(f"\n[{lab}] {etf} (weight score: {1-w_ic:.2f} sortino + {w_ic:.2f} tailIC)...")
            res = run_config(etf, "2022-01-01", "2026-01-01", fee_bps, args.z_buffer,
                             cfg, scores_by_w)
            if res.get("status") == "SUCCESS":
                print(f"    Sharpe={res['cost_sharpe']:.3f}")
                rows.append({"Phase": "full", "Config": lab, "ETF": etf,
                             "CostSharpe": res["cost_sharpe"], "TotalPnL": res["total_pnl"],
                             "MaxDD": res["max_drawdown"], "WinRate": res["win_rate_pct"],
                             "Trades": res["n_trades"]})

    df_full = pd.DataFrame([r for r in rows if r["Phase"] == "full"])
    pv = df_full.pivot_table(index="Config", columns="ETF", values="CostSharpe", aggfunc="first")
    pv["Avg"] = pv.mean(axis=1)
    base_avg = float(pv.loc["baseline(tailIC_wt)", "Avg"])
    pv["ΔBase"] = pv["Avg"] - base_avg
    pv = pv.sort_values("Avg", ascending=False)
    print("\n" + "=" * 100)
    print("PHASE 1 RESULTS — full OOS (selection=tailIC, ER=20; weights = blend)")
    print("=" * 100)
    print(pv.round(3).to_string())

    # Pick best blend (excluding the pure-tailIC-rank extreme w=0.75 handled naturally)
    best_cfg_label = pv.index[0]
    if best_cfg_label == "baseline(tailIC_wt)":
        yearly_configs = ["baseline", "w_ic=0.00"]
    else:
        w_best = 1.0 - float(best_cfg_label.split("_")[1]) / 100.0
        yearly_configs = ["baseline", "w_ic=0.00"]
        if f"w_ic={w_best:.2f}" != "w_ic=0.00":
            yearly_configs.append(f"w_ic={w_best:.2f}")

    # ─── Phase 2: yearly stability ────────────────────────────────────────────
    if not args.skip_yearly:
        print("\n>>> PHASE 2: YEARLY STABILITY")
        print(f"    configs: {yearly_configs}")
        for year in YEARS:
            y_start, y_end = f"{year}-01-01", f"{year+1}-01-01"
            for etf, scores_by_w in etf_assets.items():
                for cfg in yearly_configs:
                    cfg_lab = "baseline(tailIC_wt)" if cfg == "baseline" else blend_label(float(cfg.split("=")[1]))
                    print(f"\n[{cfg_lab} | {year}] {etf}...")
                    res = run_config(etf, y_start, y_end, fee_bps, args.z_buffer,
                                     cfg, scores_by_w)
                    if res.get("status") == "SUCCESS":
                        print(f"    Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}")
                        rows.append({"Phase": "yearly", "Config": cfg_lab, "ETF": etf,
                                     "Year": year, "CostSharpe": res["cost_sharpe"],
                                     "TotalPnL": res["total_pnl"], "MaxDD": res["max_drawdown"],
                                     "WinRate": res["win_rate_pct"], "Trades": res["n_trades"]})

        df_yr = pd.DataFrame([r for r in rows if r.get("Phase") == "yearly"])
        if not df_yr.empty:
            print("\n" + "=" * 100)
            print("PHASE 2 RESULTS — per-year avg across ETFs")
            print("=" * 100)
            yr_pv = df_yr.groupby(["Config", "Year"])["CostSharpe"].mean().unstack(fill_value=np.nan)
            yr_pv["Avg"] = yr_pv.mean(axis=1)
            yr_pv["Std"] = yr_pv[YEARS].std(axis=1)
            yr_pv["Min"] = yr_pv[YEARS].min(axis=1)
            yr_pv = yr_pv.sort_values("Avg", ascending=False)
            print(yr_pv.round(3).to_string())

            print("\n" + "-" * 100)
            print("PER-ETF x YEAR detail (CostSharpe)")
            print("-" * 100)
            for cfg in df_yr["Config"].unique():
                sub = df_yr[df_yr["Config"] == cfg]
                det = sub.pivot_table(index="ETF", columns="Year", values="CostSharpe", aggfunc="first")
                print(f"\n  {cfg}:")
                print(det.round(3).to_string())

            print("\n" + "-" * 100)
            print("YEARLY WIN COUNT vs baseline (per year, across ETFs)")
            print("-" * 100)
            base_yr = df_yr[df_yr["Config"] == "baseline(tailIC_wt)"].set_index(["Year", "ETF"])["CostSharpe"]
            for cfg in df_yr["Config"].unique():
                if cfg == "baseline(tailIC_wt)":
                    continue
                sub = df_yr[df_yr["Config"] == cfg].set_index(["Year", "ETF"])["CostSharpe"]
                common = sub.index.intersection(base_yr.index)
                deltas = sub.loc[common] - base_yr.loc[common]
                wins = int((deltas > 0).sum())
                per_year = {y: float((deltas.xs(y, level=0) > 0).sum()) for y in YEARS if y in deltas.index.get_level_values(0)}
                print(f"  {cfg:<28} wins={wins}/{len(common)}  per-year(W/total): {per_year}")

    # ─── Save ──────────────────────────────────────────────────────────────────
    out_csv = Path(args.output) if args.output else HERE / "weight_blend_yearly_results.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")
    print("\n[OK] weight-blend + yearly A/B complete.")


if __name__ == "__main__":
    main()
