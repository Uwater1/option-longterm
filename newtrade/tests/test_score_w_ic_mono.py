#!/usr/bin/env python3
"""
Experiment 3: IC + Monotonicity Score Weighting Optimization for Top-10 Selection & Allocation.
Grid search over IC and Monotonicity weights in [0.3, 0.7] with w_ir = 0.0:
  - IC weights: [0.30, 0.40, 0.50, 0.60, 0.70]
  - Mono weights: 1.0 - IC_weight
  - Mono rolling windows: [252, 504, 750]
  - Schemes: 'score' (Score Weighted), 'icw' (IC Weighted), 'ew' (Equal Weight)

Evaluates OOS performance (2022-01 ~ 2026-01) under 8 bps friction on 300ETF, 500ETF, 159915ETF.
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
IC_WEIGHTS = [0.30, 0.40, 0.50, 0.60, 0.70]
MONO_WINDOWS = [252, 504, 750]
SCHEMES_TO_TEST = ["score", "icw", "ew"]


def run_experiment():
    print("================================================================================")
    print("EXPERIMENT 3: IC + MONOTONICITY SCORE SYSTEM & WEIGHTING OPTIMIZATION")
    print("================================================================================")

    records = []

    for w_ic in IC_WEIGHTS:
        w_mono = round(1.0 - w_ic, 2)
        score_weights = (w_ic, 0.0, w_mono)
        
        for mw in MONO_WINDOWS:
            for scheme in SCHEMES_TO_TEST:
                cfg_name = f"IC={w_ic:.2f}/Mono={w_mono:.2f} (win={mw}d) [{scheme.upper()}]"
                print(f"---> Testing Config: {cfg_name}...")
                
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
                        dynamic_ic=True,
                        rank_kwargs={
                            "top_k": 10,
                            "dynamic_metric": "multi",
                            "score_weights": score_weights,
                            "mono_window": mw
                        }
                    )
                    if res.get("status") == "SUCCESS":
                        records.append({
                            "ETF": etf,
                            "w_ic": w_ic,
                            "w_mono": w_mono,
                            "mono_window": mw,
                            "Scheme": scheme.upper(),
                            "Cost Sharpe": res["cost_sharpe"],
                            "Raw Sharpe": res["raw_sharpe"],
                            "Total PnL": res["total_pnl"],
                            "Max DD": res["max_drawdown"],
                            "Win Rate": res["win_rate_pct"],
                            "Turnover": res["ann_turnover"],
                            "Trades": res["n_trades"],
                        })

    df = pd.DataFrame(records)
    
    print("\n================================================================================")
    print("TOP-PERFORMING CONFIGURATIONS (BY CROSS-ETF AVERAGE SHARPE)")
    print("================================================================================")

    group_cols = ["w_ic", "w_mono", "mono_window", "Scheme"]
    avg_df = df.groupby(group_cols)[["Cost Sharpe", "Total PnL", "Turnover", "Win Rate"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print(avg_df.head(15).to_string(index=False))

    print("\n--------------------------------------------------------------------------------")
    print("SCORE WEIGHTED SCHEME ONLY (SCOREW) - IC/MONO TILT BREAKDOWN")
    print("--------------------------------------------------------------------------------")
    score_only = avg_df[avg_df["Scheme"] == "SCORE"].sort_values("Cost Sharpe", ascending=False)
    print(score_only.to_string(index=False))

    out_csv = NEWTRADE_DIR / "tests" / "test_score_w_ic_mono_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved full experiment results to {out_csv}")


if __name__ == "__main__":
    run_experiment()
