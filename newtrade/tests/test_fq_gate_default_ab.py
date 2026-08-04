#!/usr/bin/env python3
"""
Gate-as-default A/B — should production switch to tailIC + hard gate selection?

The FQ sweep judged gates by meta-IC / TP' rate only. This script runs the
CLEAN P&L test: tailIC_480d remains the selection+weight metric (unchanged
ICW shrinkage), and a hard gate only REMOVES factors from candidacy
(masked to -inf; if <10 pass, selection shrinks — adaptive K at backtest level).

Arms (OOS 2022-01 ~ 2026-01, ER=25, REPORT.md config; baseline must reproduce
300:0.204 / 500:1.039 / 159915:0.930):
  Baseline        — unmasked tailIC (current production)
  G1_tailIC_gt0   — mask tailIC <= 0            (sanity: ~no-op)
  G2_sort0        — mask Sortino_480d <= 0
  G3_floor        — mask tailIC <= median(|tailIC|)  (deflated-IC noise floor)
  G4_sort_loo     — mask Sortino<=0 OR jackknife loo_min<=0
  G5_kitchen      — sort0 + n_neg_blocks==0 + floor

Usage:
    python newtrade/tests/test_fq_gate_default_ab.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from test_fq_ab import run_icw_backtest, AVAILABLE_ETFS, REPORT_BASELINE_ER25
from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba)
from factor_quality import rolling_daily_ic_matrix, rolling_block_stats_numba, WINDOW
from test_fq_sweep import build_component_library

NEG_INF = -1e9


def main():
    print("=" * 100)
    print("GATE-AS-DEFAULT A/B — tailIC selection + hard gates (OOS 2022-01 ~ 2026-01, ER=25)")
    print("=" * 100)

    results = []
    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue
        df = load_etf_dataset(etf)
        trade_ret = (df["trade_return"].values.astype(np.float64)
                     if "trade_return" in df.columns
                     else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, _ = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        print(f"\n[{etf}] N={len(pool)} — building gates...")
        lib, gates, _ = build_component_library(Z_std, signs, trade_ret, burn_in)
        tail = lib["tailIC480"]
        sort = lib["sortino480"]
        floor = np.median(np.abs(tail), axis=1, keepdims=True)

        masks = {
            "Baseline":      None,
            "G1_tailIC_gt0": tail > 0,
            "G2_sort0":      (tail > 0) & (sort > 0),
            "G3_floor":      (tail > 0) & (tail > floor),
            "G4_sort_loo":   (tail > 0) & (sort > 0) & (gates["loo_min"] > 0),
            "G5_kitchen":    (tail > 0) & (sort > 0) & (gates["n_neg_blocks"] == 0) & (tail > floor),
        }
        # avg pass-through
        for arm, m in masks.items():
            if m is not None:
                print(f"    {arm:<15} avg gate-passing factors: {m.mean(axis=1).mean():.1f}/{len(pool)}")

        for arm, m in masks.items():
            ov = None if m is None else np.where(m, tail, NEG_INF)
            res = run_icw_backtest(etf, "2022-01-01", "2026-01-01", 8.0 / 10000.0, 0.1,
                                   ic_override=ov, weight_ic_override=None)
            if res.get("status") != "SUCCESS":
                print(f"    [{arm}] SKIPPED: {res.get('status')}")
                continue
            results.append({"Arm": arm, "ETF": etf, "Trades": res["n_trades"],
                            "CostSharpe": res["cost_sharpe"], "RawSharpe": res["raw_sharpe"],
                            "TotalPnL": res["total_pnl"], "MaxDD": res["max_drawdown"],
                            "WinRate": res["win_rate_pct"]})
            if arm == "Baseline":
                exp = REPORT_BASELINE_ER25[etf]
                d = res["cost_sharpe"] - exp
                flag = "OK" if abs(d) < 0.005 else "MISMATCH!"
                print(f"    [{arm:<14}] Sharpe={res['cost_sharpe']:.3f} (report={exp:.3f}, Δ={d:+.4f}) [{flag}]")
            else:
                print(f"    [{arm:<14}] Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}  trades={res['n_trades']}")

    df_res = pd.DataFrame(results)
    pv = df_res.pivot_table(index="Arm", columns="ETF", values="CostSharpe", aggfunc="first")
    pv["Avg"] = pv.mean(axis=1)
    etf_cols = [c for c in pv.columns if c != "Avg"]
    base = pv.loc["Baseline", etf_cols]
    pv["ΔBase"] = pv["Avg"] - pv.loc["Baseline", "Avg"]
    pv = pv.sort_values("Avg", ascending=False)

    print("\n" + "=" * 100)
    print("RESULTS — CostSharpe by Arm × ETF (baseline = current production tailIC)")
    print("=" * 100)
    print(pv.round(3).to_string())

    print("\n" + "-" * 100)
    print("HEAD-TO-HEAD vs BASELINE")
    print("-" * 100)
    for arm, row in pv.iterrows():
        if arm == "Baseline":
            continue
        deltas = row[etf_cols] - base
        wins = int((deltas > 0).sum())
        dstr = "  ".join(f"{e}:{d:+.3f}" for e, d in deltas.items())
        print(f"  {arm:<15} wins={wins}/{len(deltas)}  ΔAvg={row['ΔBase']:+.3f}  [{dstr}]")

    df_res.to_csv(HERE / "fq_gate_default_ab_results.csv", index=False)
    print(f"\nSaved to {HERE / 'fq_gate_default_ab_results.csv'}")
    print("\n[OK] Gate-default A/B complete.")


if __name__ == "__main__":
    main()
