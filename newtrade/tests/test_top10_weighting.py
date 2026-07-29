#!/usr/bin/env python3
"""
Experiment 2: Optimization of Weight Distribution Across Top-10 Features.
Tests different weight allocation schemes over the selected Top-10 features:
  1. Equal Weight (EW): 1/10 = 0.10 each
  2. IC Weighted (ICW): Empirical Bayes shrinkage on Top 10
  3. Score Weighted (ScoreW): Proportional to score on Top 10
  4. Rank Bounded Linear Mild (0.5 ~ 1.5 ratio): Top factor gets 3x bottom factor
  5. Rank Bounded Linear Moderate (0.2 ~ 1.8 ratio): Top factor gets 9x bottom factor (Default)
  6. Rank Bounded Linear Steep (0.05 ~ 1.95 ratio): Top factor gets 39x bottom factor
  7. Rank Bounded Power (power=1.5): Moderate convex tilt
  8. Rank Bounded Power (power=2.0): Convex quadratic tilt
  9. Rank Bounded Power (power=3.0): Heavy convex tilt
 10. Rank Bounded Softmax (tau=1.0): Exponential tilt (tau=1.0)
 11. Rank Bounded Softmax (tau=2.0): Steep exponential tilt (tau=2.0)
 12. Ensemble Scheme: Equal-weight average of EW + ICW + ScoreW + Rank(Moderate)

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

WEIGHTING_CONFIGS = [
    {
        "name": "1. Equal Weight (EW)",
        "scheme": "ew",
        "rank_kwargs": {"top_k": 10}
    },
    {
        "name": "2. IC Weighted (ICW)",
        "scheme": "icw",
        "rank_kwargs": {"top_k": 10}
    },
    {
        "name": "3. Score Weighted (ScoreW)",
        "scheme": "score",
        "rank_kwargs": {"top_k": 10}
    },
    {
        "name": "4. Rank Mild (0.5 ~ 1.5)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "linear", "w_min_ratio": 0.5, "w_max_ratio": 1.5}
    },
    {
        "name": "5. Rank Moderate (0.2 ~ 1.8) [Default]",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "linear", "w_min_ratio": 0.2, "w_max_ratio": 1.8}
    },
    {
        "name": "6. Rank Steep (0.05 ~ 1.95)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "linear", "w_min_ratio": 0.05, "w_max_ratio": 1.95}
    },
    {
        "name": "7. Rank Power (p=1.5)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "power", "power": 1.5, "w_min_ratio": 0.2, "w_max_ratio": 1.8}
    },
    {
        "name": "8. Rank Power (p=2.0)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "power", "power": 2.0, "w_min_ratio": 0.2, "w_max_ratio": 1.8}
    },
    {
        "name": "9. Rank Power (p=3.0)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "power", "power": 3.0, "w_min_ratio": 0.2, "w_max_ratio": 1.8}
    },
    {
        "name": "10. Rank Softmax (tau=1.0)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "softmax", "softmax_tau": 1.0}
    },
    {
        "name": "11. Rank Softmax (tau=2.0)",
        "scheme": "rank",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "softmax", "softmax_tau": 2.0}
    },
    {
        "name": "12. Ensemble (EW+ICW+Score+Rank)",
        "scheme": "ensemble",
        "rank_kwargs": {"top_k": 10, "mapping_shape": "linear", "w_min_ratio": 0.2, "w_max_ratio": 1.8}
    },
]


def run_experiment():
    print("================================================================================")
    print("EXPERIMENT 2: TOP-10 WEIGHT DISTRIBUTION SCHEME OPTIMIZATION")
    print("================================================================================")

    records = []
    for etf in AVAILABLE_ETFS:
        print(f"\n---> Testing Weight Distributions on {etf}...")
        for cfg in WEIGHTING_CONFIGS:
            name = cfg["name"]
            scheme = cfg["scheme"]
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
                rank_kwargs=cfg["rank_kwargs"]
            )
            if res.get("status") == "SUCCESS":
                records.append({
                    "ETF": etf,
                    "Weight Distribution": name,
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
    print("WEIGHT DISTRIBUTION OPTIMIZATION RESULTS SUMMARY")
    print("================================================================================")
    print(df.to_string(index=False))

    # Average Sharpe per weight distribution across all 3 ETFs
    avg_df = df.groupby("Weight Distribution")[["Cost Sharpe", "Total PnL", "Turnover"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n--------------------------------------------------------------------------------")
    print("CROSS-ETF AVERAGE PERFORMANCE BY WEIGHT DISTRIBUTION")
    print("--------------------------------------------------------------------------------")
    print(avg_df.to_string(index=False))

    out_csv = NEWTRADE_DIR / "tests" / "top10_weighting_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved weighting experiment results to {out_csv}")


if __name__ == "__main__":
    run_experiment()
