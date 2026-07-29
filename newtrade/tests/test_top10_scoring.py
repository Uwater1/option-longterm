#!/usr/bin/env python3
"""
Experiment 1: Optimization of Scoring System for Top-10 Feature Selection.
Tests different scoring algorithms to select the Top-10 features daily or statically:
  1. Static deflated_ic (Pool metadata)
  2. Static Composite Score (0.40 IC + 0.35 IR + 0.25 Mono)
  3. Dynamic Expanding IC (raw expanding IC)
  4. Dynamic EMA IC (span=30)
  5. Dynamic EMA IC (span=10)
  6. Dynamic Multi-Metric Score (0.20 IC / 0.15 IR / 0.65 Mono 750d)
  7. Dynamic Multi-Metric Score (0.50 IC / 0.00 IR / 0.50 Mono 750d)
  8. Dynamic Multi-Metric Score (0.75 IC / 0.00 IR / 0.25 Mono 750d)
  9. Dynamic Rolling Mono 252d

Evaluates OOS performance (2022-01 ~ 2026-01) under 8 bps friction on 300ETF, 500ETF, 159915ETF.
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from run_backtest import run_single_backtest

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]

SCORING_CONFIGS = [
    {
        "name": "Static Pool IC",
        "dynamic_ic": False,
        "rank_kwargs": {"top_k": 10}
    },
    {
        "name": "Static Multi-Score",
        "dynamic_ic": False,
        "rank_kwargs": {"top_k": 10, "score_weights": (0.40, 0.35, 0.25)}
    },
    {
        "name": "Dynamic Raw IC",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "ic", "ic_ema_span": 1}
    },
    {
        "name": "Dynamic EMA30 IC",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "ic", "ic_ema_span": 30}
    },
    {
        "name": "Dynamic EMA10 IC",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "ic", "ic_ema_span": 10}
    },
    {
        "name": "Dynamic Multi (0.20/0.15/0.65 750d)",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "multi", "score_weights": (0.20, 0.15, 0.65), "mono_window": 750}
    },
    {
        "name": "Dynamic Multi (0.50/0.00/0.50 750d)",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "multi", "score_weights": (0.50, 0.00, 0.50), "mono_window": 750}
    },
    {
        "name": "Dynamic Multi (0.75/0.00/0.25 750d)",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "multi", "score_weights": (0.75, 0.00, 0.25), "mono_window": 750}
    },
    {
        "name": "Dynamic Multi (0.20/0.00/0.80 252d)",
        "dynamic_ic": True,
        "rank_kwargs": {"top_k": 10, "dynamic_metric": "multi", "score_weights": (0.20, 0.00, 0.80), "mono_window": 252}
    },
]


def run_experiment():
    print("================================================================================")
    print("EXPERIMENT 1: TOP-10 FEATURE SCORING SYSTEM OPTIMIZATION")
    print("================================================================================")

    records = []
    for etf in AVAILABLE_ETFS:
        print(f"\n---> Testing Scoring Schemes on {etf}...")
        for cfg in SCORING_CONFIGS:
            name = cfg["name"]
            res = run_single_backtest(
                etf=etf,
                side="single",
                scheme_name="ensemble",
                z_th=0.5,
                auto_threshold=True,
                z_buffer=0.1,
                position_mode="binary",
                fee_bps=0.0008,
                dynamic_ic=cfg["dynamic_ic"],
                rank_kwargs=cfg["rank_kwargs"]
            )
            if res.get("status") == "SUCCESS":
                records.append({
                    "ETF": etf,
                    "Scoring System": name,
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
    print("SCORING SYSTEM OPTIMIZATION RESULTS SUMMARY")
    print("================================================================================")
    print(df.to_string(index=False))

    # Average Sharpe per scoring system across all 3 ETFs
    avg_df = df.groupby("Scoring System")[["Cost Sharpe", "Total PnL", "Turnover"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n--------------------------------------------------------------------------------")
    print("CROSS-ETF AVERAGE PERFORMANCE BY SCORING SYSTEM")
    print("--------------------------------------------------------------------------------")
    print(avg_df.to_string(index=False))

    out_csv = NEWTRADE_DIR / "tests" / "top10_scoring_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved scoring experiment results to {out_csv}")


if __name__ == "__main__":
    run_experiment()
