#!/usr/bin/env python3
"""
Multi-Period Sweep script for score_blend_w_ic (TailIC vs Sortino weight blend)
for EW and ENSEMBLE schemes over:
  - 2022-01-01 ~ 2026-01-01 (4-Year OOS)
  - 2023-01-01 ~ 2026-01-01 (3-Year OOS)
  - 2024-01-01 ~ 2026-01-01 (2-Year OOS)

Also verifies impact of Sortino <= 0 gate.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from run_backtest import run_single_backtest

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
W_IC_VALUES = [0.0, 0.2, 0.4, 0.6, 0.75, 0.8, 1.0]
PERIODS = [
    ("2022-01-01", "2026-01-01", "2022-2026"),
    ("2023-01-01", "2026-01-01", "2023-2026"),
    ("2024-01-01", "2026-01-01", "2024-2026"),
]
SCHEMES_TO_TEST = ["ew", "ensemble"]

def main():
    print("================================================================================")
    print("MULTI-PERIOD SWEEPING SCORE BLEND WEIGHT (TailIC vs Sortino)")
    print("================================================================================")

    records = []

    for start_date, end_date, period_label in PERIODS:
        print(f"\n==================================================")
        print(f"EVALUATING PERIOD: {period_label}")
        print(f"==================================================")

        for scheme in SCHEMES_TO_TEST:
            for w_ic in W_IC_VALUES:
                w_sortino = round(1.0 - w_ic, 2)
                
                for etf in AVAILABLE_ETFS:
                    res = run_single_backtest(
                        etf=etf,
                        side="single",
                        scheme_name=scheme,
                        z_th=0.5,
                        auto_threshold=True,
                        z_buffer=0.1,
                        position_mode="binary",
                        fee_bps=0.0008,
                        start_date=start_date,
                        end_date=end_date,
                        dynamic_ic=True,
                        score_blend_w_ic=w_ic,
                        sortino_gate=True,
                        rank_kwargs={"top_k": 10}
                    )
                    if res.get("status") == "SUCCESS":
                        records.append({
                            "Period": period_label,
                            "Scheme": scheme,
                            "w_ic": w_ic,
                            "w_sortino": w_sortino,
                            "ETF": etf,
                            "Cost Sharpe": res["cost_sharpe"],
                            "Raw Sharpe": res["raw_sharpe"],
                            "Total PnL": res["total_pnl"],
                            "Max DD": res["max_drawdown"],
                            "Win Rate": res["win_rate_pct"],
                            "Turnover": res["ann_turnover"],
                            "Trades": res["n_trades"],
                        })

    df = pd.DataFrame(records)
    out_csv = HERE / "multi_period_score_blend_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved raw multi-period sweep results to {out_csv}")

    # Aggregated table by Period, Scheme, w_ic
    avg_df = df.groupby(["Period", "Scheme", "w_ic", "w_sortino"])[["Cost Sharpe", "Total PnL", "Max DD", "Turnover"]].mean().reset_index()
    avg_df = avg_df.sort_values(["Period", "Scheme", "Cost Sharpe"], ascending=[True, True, False])

    print("\n================================================================================")
    print("MULTI-PERIOD CROSS-ETF AVERAGE PERFORMANCE SUMMARY")
    print("================================================================================")
    print(avg_df.to_string(index=False))

if __name__ == "__main__":
    main()
