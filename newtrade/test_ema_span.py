#!/usr/bin/env python3
"""
Test script to evaluate dynamic metric 'ic' (true_ic) with different EMA spans (10, 30, 60, 120, 252).
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import compute_rank_w
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold

ETFS = ["300ETF", "500ETF", "159915ETF"]
SPANS = [10, 30, 60, 120, 252]
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"
FEE_BPS = 0.0008


def run_span_test(etf: str, span: int):
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
        "ic_ema_span": span,
        "expanding_ic": exp_ic,
    }

    Z_composite = compute_rank_w(Z_std, signs, pool=pool, **rank_kwargs)

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

    return {
        "etf": etf,
        "span": span,
        "trades": m["n_trades"],
        "cost_sharpe": m["cost_sharpe"],
        "pnl": m["total_pnl"],
        "max_dd": m["max_drawdown"],
        "turnover": m["ann_turnover"],
    }


def main():
    print("================================================================================")
    print("TESTING DYNAMIC METRIC 'ic' WITH DIFFERENT EMA SPANS")
    print("================================================================================")
    results = []
    for etf in ETFS:
        print(f"\n--- {etf} ---")
        for s in SPANS:
            res = run_span_test(etf, s)
            if res:
                results.append(res)
                print(f"  Span: {s:<4} | Cost Sharpe: {res['cost_sharpe']:.3f} | PnL: {res['pnl']:+.4f} | MaxDD: {res['max_dd']:.4f} | Trades: {res['trades']:<3} | Turnover: {res['turnover']:.1f}x")

    df_res = pd.DataFrame(results)
    out_csv = HERE / "artifacts" / "test_ema_span_results.csv"
    df_res.to_csv(out_csv, index=False)


if __name__ == "__main__":
    main()
