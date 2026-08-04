#!/usr/bin/env python3
"""
Follow-up to test_exit_rank_sortino_ab.py: combine the two winning findings.

Findings so far:
  - TailIC baseline prefers ER=25 (avg 0.724 vs 0.684 at ER=20): 300:+0.06, 500:+0.10, 159:-0.04
  - selTailIC_wSortino (tail IC selects, Sortino weights) at ER=20 beats baseline 2/3
    with the SMALLEST 500ETF loss (-0.021): avg 0.806

Test: selTailIC_wSortino at ER ∈ {23, 25} — does the ER=25 upgrade stack with
Sortino weighting?
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from test_exit_rank_sortino_ab import (run_icw_backtest, precompute,
                                       composite_tailic_risk_score,
                                       AVAILABLE_ETFS, SORTINO_W_IC)


def main():
    print("=" * 90)
    print("FOLLOW-UP: selTailIC_wSortino × ER ∈ {23, 25}")
    print("=" * 90)
    rows = []
    for etf in AVAILABLE_ETFS:
        mats = precompute(etf)
        if mats is None:
            continue
        score = composite_tailic_risk_score(mats["ic"], mats["sortino"], SORTINO_W_IC)
        for er in [23, 25]:
            print(f"\n[selTailIC_wSortino/ER{er}] {etf}...")
            res = run_icw_backtest(etf, "2022-01-01", "2026-01-01", 0.0008, 0.1,
                                   exit_rank=er, ic_override=None,
                                   weight_ic_override=score)
            if res.get("status") == "SUCCESS":
                rows.append({"Arm": f"selTailIC_wSortino/ER{er}", "ETF": etf,
                             "CostSharpe": res["cost_sharpe"], "TotalPnL": res["total_pnl"],
                             "MaxDD": res["max_drawdown"], "WinRate": res["win_rate_pct"],
                             "Trades": res["n_trades"]})
                print(f"    Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}")

    import pandas as pd
    df = pd.DataFrame(rows)
    if not df.empty:
        pv = df.pivot_table(index="Arm", columns="ETF", values="CostSharpe", aggfunc="first")
        pv["Avg"] = pv.mean(axis=1)
        print("\n" + "=" * 90)
        print("RESULTS (reference: TailIC/ER20 baseline = 300:0.145 500:0.942 159915:0.965, avg 0.684)")
        print("         (reference: selTailIC_wSortino/ER20       = 300:0.405 500:0.921 159915:1.093, avg 0.806)")
        print("         (reference: TailIC/ER25                   = 300:0.204 500:1.039 159915:0.930, avg 0.724)")
        print("=" * 90)
        print(pv.round(3).to_string())
        df.to_csv(HERE / "followup_sel_tailic_wsortino_er.csv", index=False)
        print(f"\nSaved to {HERE / 'followup_sel_tailic_wsortino_er.csv'}")


if __name__ == "__main__":
    main()
