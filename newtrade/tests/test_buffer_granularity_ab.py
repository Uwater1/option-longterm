#!/usr/bin/env python3
"""
Z Buffer & Sweep Granularity A/B Test for ENSEMBLE baseline.
Tests:
1. z_buffer = 0.10 vs 0.15 vs 0.20
2. Threshold sweep step = 0.10 vs 0.05
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

TEST_CONFIGS = [
    {"name": "1. Baseline (Buffer=0.10, Step=0.10)", "buffer": 0.10, "step": 0.10},
    {"name": "2. Increased Buffer (Buffer=0.15, Step=0.10)", "buffer": 0.15, "step": 0.10},
    {"name": "3. Increased Buffer (Buffer=0.20, Step=0.10)", "buffer": 0.20, "step": 0.10},
    {"name": "4. Finer Granularity (Buffer=0.10, Step=0.05)", "buffer": 0.10, "step": 0.05},
    {"name": "5. Finer + Higher Buffer (Buffer=0.15, Step=0.05)", "buffer": 0.15, "step": 0.05},
]

def main():
    print("================================================================================")
    print("Z BUFFER & SWEEP GRANULARITY A/B TEST (ENSEMBLE)")
    print("================================================================================")

    records = []
    for cfg in TEST_CONFIGS:
        print(f"\n---> Testing Config: {cfg['name']}...")
        for etf in AVAILABLE_ETFS:
            res = run_single_backtest(
                etf=etf,
                side="single",
                scheme_name="ensemble",
                z_th="auto",
                auto_threshold=True,
                z_buffer=cfg["buffer"],
                position_mode="fast_ramp_quadratic",
                min_pos=0.5,
                delta_z_full=0.3,
                fee_bps=0.0008,
                start_date="2022-01-01",
                end_date="2026-01-01",
                dynamic_ic=True,
                score_blend_w_ic=1.0,
                rank_kwargs={"top_k": 10}
            )
            if res.get("status") == "SUCCESS":
                records.append({
                    "Config": cfg["name"],
                    "ETF": etf,
                    "Cost Sharpe": res["cost_sharpe"],
                    "Raw Sharpe": res["raw_sharpe"],
                    "Total PnL": res["total_pnl"],
                    "Max DD": res["max_drawdown"],
                    "Win Rate": res["win_rate_pct"],
                    "Turnover": res["ann_turnover"],
                    "Trades": res["n_trades"],
                    "Z_th_Long": res.get("prod_z_th_long", 0.0),
                    "Z_th_Short": res.get("prod_z_th_short", 0.0),
                })

    df = pd.DataFrame(records)
    out_csv = HERE / "buffer_granularity_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")

    avg_df = df.groupby("Config")[["Cost Sharpe", "Total PnL", "Max DD", "Turnover", "Trades"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n================================================================================")
    print("CROSS-ETF AVERAGE SUMMARY")
    print("================================================================================")
    print(avg_df.to_string(index=False))

if __name__ == "__main__":
    main()
