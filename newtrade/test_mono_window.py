#!/usr/bin/env python3
"""
Test script to evaluate monotonicity window lengths (W in [126, 252, 500, 750, 1000, 0]).
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_score_numba
from weighting import compute_score_w
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold

ETFS = ["300ETF", "500ETF", "159915ETF"]
WINDOWS = [126, 252, 500, 750, 1000, 0]  # 0 = lifetime expanding
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"
FEE_BPS = 0.0008


def run_window_test(etf: str, w_mono: int):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None

    df = load_etf_dataset(etf)
    trade_ret = df["trade_return"].values.astype(np.float64)
    X_raw, signs, _ = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    score_weights = (0.20, 0.15, 0.65)
    exp_mat = expanding_factor_score_numba(
        Z_std, signs, trade_ret, burn_in=burn_in, score_weights=score_weights, mono_window=w_mono
    )

    rank_kwargs = {
        "ic_ema_span": 30,
        "expanding_ic": exp_mat,
        "score_weights": score_weights,
    }

    Z_composite = compute_score_w(Z_std, signs, pool=pool, **rank_kwargs)

    t_start_ts = pd.Timestamp(START_DATE)
    train_mask = df["date"] < t_start_ts
    Z_train = Z_composite[train_mask.values]
    ret_train = trade_ret[train_mask.values]

    sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary", fee_bps=FEE_BPS, long_only=False)
    z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=0.1)

    positions = generate_positions(Z_composite, z_th=z_th_l, z_th_short=z_th_s, mode="binary", long_only=False)

    t_start = pd.Timestamp(START_DATE)
    t_end = pd.Timestamp(END_DATE)
    mask = (df["date"] >= t_start) & (df["date"] < t_end)

    df_oos = df[mask].reset_index(drop=True)
    pos_oos = positions[mask]
    ret_oos = trade_ret[mask.values]

    net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, pos_oos, fee_bps=FEE_BPS)
    m = calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_oos["date"])

    win_title = "Expanding" if w_mono == 0 else f"{w_mono}d ({w_mono/250:.1f}yr)"

    return {
        "etf": etf,
        "window": win_title,
        "trades": m["n_trades"],
        "cost_sharpe": m["cost_sharpe"],
        "pnl": m["total_pnl"],
        "max_dd": m["max_drawdown"],
        "win_rate": m["win_rate_pct"],
        "turnover": m["ann_turnover"],
    }


def main():
    print("================================================================================")
    print("      EVALUATING MONOTONICITY WINDOW LENGTHS ACROSS ALL ETFS                   ")
    print("================================================================================")
    for etf in ETFS:
        print(f"\n>>> ETF: {etf}")
        print(f"{'Window':<18} | {'Cost Sharpe':<11} | {'Total PnL':<10} | {'Max DD':<8} | {'Win Rate':<8} | {'Turnover':<8}")
        print("-" * 75)
        for w in WINDOWS:
            res = run_window_test(etf, w)
            if res:
                print(f"{res['window']:<18} | {res['cost_sharpe']:11.3f} | {res['pnl']:+10.4f} | {res['max_dd']:8.4f} | {res['win_rate']:7.1f}% | {res['turnover']:7.1f}x")

if __name__ == "__main__":
    main()
