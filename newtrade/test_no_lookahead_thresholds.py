#!/usr/bin/env python3
"""
Test Zero-Overfit, Non-Swept Threshold & Sizing Schemes:
1. Fixed Production Thresholds (z_th = 0.50, 0.80, 1.00) with zero in-sample tuning.
2. Continuous Position Sizing (tanh(Z / gamma) & linear Z clipping) without step-function thresholds.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import compute_rank_w
from strategy import simulate_etf_spot, calculate_metrics

ETFS = ["300ETF", "500ETF", "159915ETF"]
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"
FEE_BPS = 0.0008


def evaluate_fixed_or_continuous(etf: str, mode: str = "fixed", z_th: float = 0.8, gamma: float = 1.0):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None

    df = load_etf_dataset(etf)
    trade_ret = df["trade_return"].values.astype(np.float64)
    X_raw, signs, _ = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    exp_ic = expanding_factor_ic_numba(Z_std, signs, trade_ret, burn_in=burn_in)
    rank_kwargs = {
        "w_min_ratio": 0.2,
        "w_max_ratio": 1.8,
        "mapping_shape": "linear",
        "ic_ema_span": 30,
        "expanding_ic": exp_ic,
    }
    Z_composite = compute_rank_w(Z_std, signs, pool=pool, **rank_kwargs)

    t_start = pd.Timestamp(START_DATE)
    t_end = pd.Timestamp(END_DATE)
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    df_oos = df[mask].reset_index(drop=True)
    ret_oos = trade_ret[mask.values]
    Z_oos = Z_composite[mask.values]

    if mode == "fixed_binary":
        positions = np.zeros(len(Z_oos), dtype=np.float64)
        positions[Z_oos > z_th] = 1.0
        positions[Z_oos < -z_th] = -1.0
    elif mode == "pure_tanh":
        # Pure continuous tanh sizing without any threshold cutoff
        positions = np.tanh(Z_oos / gamma)
    elif mode == "pure_linear_clip":
        # Pure linear position sizing clipped to [-1, 1]
        positions = np.clip(Z_oos / gamma, -1.0, 1.0)
    else:
        raise ValueError(f"Unknown mode {mode}")

    net_ret, raw_ret, _ = simulate_etf_spot(ret_oos, positions, fee_bps=FEE_BPS)
    m = calculate_metrics(net_ret, raw_ret, positions, dates=df_oos["date"])

    return {
        "etf": etf,
        "mode": mode,
        "z_th_or_gamma": z_th if mode == "fixed_binary" else gamma,
        "trades": m["n_trades"],
        "cost_sharpe": m["cost_sharpe"],
        "raw_sharpe": m["raw_sharpe"],
        "pnl": m["total_pnl"],
        "max_dd": m["max_drawdown"],
        "turnover": m["ann_turnover"],
    }


def main():
    print("================================================================================")
    print("ZERO-LOOKAHEAD / NO SWEEP TEST: FIXED THRESHOLDS vs CONTINUOUS SIZING")
    print("================================================================================")

    # 1. Fixed Binary Thresholds (no train sweep at all)
    print("\n--- Fixed Binary Thresholds (z_th = 0.50, 0.80, 1.00) ---")
    for etf in ETFS:
        for z in [0.50, 0.80, 1.00]:
            r = evaluate_fixed_or_continuous(etf, mode="fixed_binary", z_th=z)
            print(f"  {etf:<10} | Fixed Z_th={z:.2f} | Trades: {r['trades']:<3} | Cost Sharpe: {r['cost_sharpe']:.3f} | Raw Sharpe: {r['raw_sharpe']:.3f} | PnL: {r['pnl']:+.4f} | MaxDD: {r['max_dd']:.4f} | Turnover: {r['turnover']:.1f}x")

    # 2. Pure Continuous Tanh Sizing (S = tanh(Z / gamma), zero step threshold)
    print("\n--- Pure Continuous Tanh Sizing (S = tanh(Z / gamma), no step threshold) ---")
    for etf in ETFS:
        for g in [1.0, 1.5, 2.0]:
            r = evaluate_fixed_or_continuous(etf, mode="pure_tanh", gamma=g)
            print(f"  {etf:<10} | Tanh gamma={g:.1f} | Trades: {r['trades']:<3} | Cost Sharpe: {r['cost_sharpe']:.3f} | Raw Sharpe: {r['raw_sharpe']:.3f} | PnL: {r['pnl']:+.4f} | MaxDD: {r['max_dd']:.4f} | Turnover: {r['turnover']:.1f}x")


if __name__ == "__main__":
    main()
