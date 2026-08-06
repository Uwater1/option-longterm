#!/usr/bin/env python3
"""
Position Sizing A/B Test for ENSEMBLE scheme.
Sweeps position sizing modes, min_pos floors, and delta_z_full margins
to find optimal parameters for signal-averaged ENSEMBLE composite Z.
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

SIZING_CONFIGS = [
    {"name": "1. Binary Baseline", "mode": "binary", "min_pos": 1.0, "delta_z": 0.0},
    {"name": "2. Fast Ramp Quad (m=0.7, dz=0.4) [Current]", "mode": "fast_ramp_quadratic", "min_pos": 0.7, "delta_z": 0.4},
    {"name": "3. Fast Ramp Quad (m=0.5, dz=0.3)", "mode": "fast_ramp_quadratic", "min_pos": 0.5, "delta_z": 0.3},
    {"name": "4. Fast Ramp Quad (m=0.6, dz=0.3)", "mode": "fast_ramp_quadratic", "min_pos": 0.6, "delta_z": 0.3},
    {"name": "5. Fast Ramp Quad (m=0.8, dz=0.3)", "mode": "fast_ramp_quadratic", "min_pos": 0.8, "delta_z": 0.3},
    {"name": "6. Fast Ramp Linear (m=0.5, dz=0.3)", "mode": "fast_ramp_linear", "min_pos": 0.5, "delta_z": 0.3},
    {"name": "7. Fast Ramp Linear (m=0.6, dz=0.3)", "mode": "fast_ramp_linear", "min_pos": 0.6, "delta_z": 0.3},
    {"name": "8. Fast Ramp Linear (m=0.7, dz=0.4)", "mode": "fast_ramp_linear", "min_pos": 0.7, "delta_z": 0.4},
]

def main():
    print("================================================================================")
    print("POSITION SIZING A/B TEST FOR ENSEMBLE SCHEME")
    print("================================================================================")

    records = []
    for cfg in SIZING_CONFIGS:
        print(f"\n---> Testing Position Sizing: {cfg['name']}...")
        for etf in AVAILABLE_ETFS:
            res = run_single_backtest(
                etf=etf,
                side="single",
                scheme_name="ensemble",
                z_th="auto",
                auto_threshold=True,
                z_buffer=0.1,
                position_mode=cfg["mode"],
                min_pos=cfg["min_pos"],
                delta_z_full=cfg["delta_z"],
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
                })

    df = pd.DataFrame(records)
    out_csv = HERE / "position_sizing_ensemble_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved position sizing results to {out_csv}")

    avg_df = df.groupby("Config")[["Cost Sharpe", "Total PnL", "Max DD", "Turnover"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n================================================================================")
    print("CROSS-ETF AVERAGE POSITION SIZING SUMMARY")
    print("================================================================================")
    print(avg_df.to_string(index=False))

if __name__ == "__main__":
    main()
