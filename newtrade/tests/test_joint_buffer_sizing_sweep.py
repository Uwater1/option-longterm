#!/usr/bin/env python3
"""
Joint Z-Buffer & Position Sizing Grid Sweep for ENSEMBLE baseline.
Sweeps:
- z_buffer in [0.15, 0.20]
- min_pos (m) in [0.50, 0.60, 0.70, 0.80, 1.00]
- delta_z_full in [0.20, 0.30, 0.40, 0.50]
- mode in ["fast_ramp_quadratic", "fast_ramp_linear", "binary"]
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

BUFFERS = [0.15, 0.20]
MIN_POS_LIST = [0.50, 0.60, 0.70, 0.80, 1.00]
DELTA_Z_LIST = [0.20, 0.30, 0.40, 0.50]
MODES = ["fast_ramp_quadratic", "fast_ramp_linear", "binary"]

def main():
    print("================================================================================")
    print("JOINT Z-BUFFER & POSITION SIZING GRID SWEEP (ENSEMBLE)")
    print("================================================================================")

    records = []

    for buf in BUFFERS:
        for mode in MODES:
            if mode == "binary":
                combos = [(1.00, 0.00)]
            else:
                combos = [(m, dz) for m in MIN_POS_LIST if m < 1.0 for dz in DELTA_Z_LIST]

            for m, dz in combos:
                config_label = f"Buffer={buf:.2f} | Mode={mode} | m={m:.2f} | dz={dz:.2f}"
                print(f"---> Sweep: {config_label}")
                
                for etf in AVAILABLE_ETFS:
                    res = run_single_backtest(
                        etf=etf,
                        side="single",
                        scheme_name="ensemble",
                        z_th="auto",
                        auto_threshold=True,
                        z_buffer=buf,
                        position_mode=mode,
                        min_pos=m,
                        delta_z_full=dz,
                        fee_bps=0.0008,
                        start_date="2022-01-01",
                        end_date="2026-01-01",
                        dynamic_ic=True,
                        score_blend_w_ic=1.0,
                        rank_kwargs={"top_k": 10}
                    )
                    if res.get("status") == "SUCCESS":
                        records.append({
                            "Buffer": buf,
                            "Mode": mode,
                            "min_pos": m,
                            "delta_z_full": dz,
                            "Config": config_label,
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
    out_csv = HERE / "joint_buffer_sizing_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")

    avg_df = df.groupby(["Buffer", "Mode", "min_pos", "delta_z_full"])[["Cost Sharpe", "Total PnL", "Max DD", "Turnover", "Trades"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n================================================================================")
    print("TOP 15 JOINT CONFIGURATIONS (CROSS-ETF AVERAGE)")
    print("================================================================================")
    print(avg_df.head(15).to_string(index=False))

if __name__ == "__main__":
    main()
