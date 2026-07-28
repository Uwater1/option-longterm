#!/usr/bin/env python3
"""
Diagnostic script for addressing User Problems 1 & 2:
1. 300ETF: Sensitivity sweep across Z_th (0.4 ~ 1.4) and position modes to test signal validity vs low-trade-count overfit.
2. 159915ETF: Sensitivity sweep across Z_th (0.3 ~ 1.2) to find true optimal Cost Sharpe & Raw Sharpe vs friction.
3. Regularized Threshold Sweep: Evaluate min-active-days floor in threshold auto-sweep.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import compute_rank_w
from strategy import generate_positions, simulate_etf_spot, calculate_metrics

FEE_BPS = 0.0008
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"


def evaluate_etf_z_grid(etf: str, z_grid=np.arange(0.3, 1.5, 0.1), mode="binary"):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return []

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

    results = []
    for z_th in z_grid:
        z_val = round(float(z_th), 2)
        positions = generate_positions(Z_composite, z_th=z_val, mode=mode, long_only=False)
        pos_oos = positions[mask]

        net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, pos_oos, fee_bps=FEE_BPS)
        m = calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_oos["date"])

        results.append({
            "etf": etf,
            "mode": mode,
            "z_th": z_val,
            "trades": m["n_trades"],
            "cost_sharpe": m["cost_sharpe"],
            "raw_sharpe": m["raw_sharpe"],
            "pnl": m["total_pnl"],
            "max_dd": m["max_drawdown"],
            "win_rate": m["win_rate_pct"],
            "turnover": m["ann_turnover"],
        })

    return results


def test_regularized_sweep(etf: str, min_active_pct: float = 10.0):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None

    df = load_etf_dataset(etf)
    trade_ret = df["trade_return"].values.astype(np.float64)
    X_raw, signs, _ = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    exp_ic = expanding_factor_ic_numba(Z_std, signs, trade_ret, burn_in=burn_in)
    Z_composite = compute_rank_w(Z_std, signs, pool=pool, w_min_ratio=0.2, w_max_ratio=1.8, mapping_shape="linear", ic_ema_span=30, expanding_ic=exp_ic)

    t_start_ts = pd.Timestamp(START_DATE)
    train_mask = df["date"] < t_start_ts
    Z_train = Z_composite[train_mask.values]
    ret_train = trade_ret[train_mask.values]

    thresholds = np.arange(0.3, 1.5, 0.1)
    best_sharpe = -np.inf
    opt_l, opt_s = 0.5, 0.5

    for zl in thresholds:
        for zs in thresholds:
            pos = generate_positions(Z_train, z_th=zl, z_th_short=zs, mode="binary", long_only=False)
            active_pct = (np.abs(pos) > 1e-5).mean() * 100.0
            if active_pct < min_active_pct:
                continue  # Skip unrepresentative low-trade sweeps

            net_ret, _, _ = simulate_etf_spot(ret_train, pos, fee_bps=FEE_BPS)
            std_net = np.std(net_ret)
            sharpe = float((np.mean(net_ret) / std_net) * np.sqrt(252)) if std_net > 1e-12 else 0.0
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                opt_l, opt_s = float(zl), float(zs)

    # Production threshold
    z_prod_l = round(opt_l + 0.1, 2)
    z_prod_s = round(opt_s + 0.1, 2)

    positions = generate_positions(Z_composite, z_th=z_prod_l, z_th_short=z_prod_s, mode="binary", long_only=False)

    t_start = pd.Timestamp(START_DATE)
    t_end = pd.Timestamp(END_DATE)
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    df_oos = df[mask].reset_index(drop=True)
    pos_oos = positions[mask]
    ret_oos = trade_ret[mask.values]

    net_ret, raw_ret, _ = simulate_etf_spot(ret_oos, pos_oos, fee_bps=FEE_BPS)
    m = calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_oos["date"])

    return {
        "etf": etf,
        "opt_train_l": opt_l,
        "opt_train_s": opt_s,
        "z_prod_l": z_prod_l,
        "z_prod_s": z_prod_s,
        "trades": m["n_trades"],
        "cost_sharpe": m["cost_sharpe"],
        "raw_sharpe": m["raw_sharpe"],
        "pnl": m["total_pnl"],
        "max_dd": m["max_drawdown"],
    }


def main():
    print("================================================================================")
    print("PROBLEM 1 & 2 DIAGNOSTIC: Z_TH SENSITIVITY & REGULARIZED THRESHOLD SWEEP")
    print("================================================================================")

    # 1. 300ETF Z_th Grid Sweep
    print("\n--- 300ETF Z_th Grid Sweep (Testing sample size & signal robustness) ---")
    res_300 = evaluate_etf_z_grid("300ETF", z_grid=np.arange(0.4, 1.4, 0.1))
    for r in res_300:
        print(f"  Z_th: {r['z_th']:<4} | Trades: {r['trades']:<3} | Cost Sharpe: {r['cost_sharpe']:.3f} | Raw Sharpe: {r['raw_sharpe']:.3f} | PnL: {r['pnl']:+.4f} | MaxDD: {r['max_dd']:.4f} | WinRate: {r['win_rate']:.1f}%")

    # 2. 159915ETF Z_th Grid Sweep
    print("\n--- 159915ETF Z_th Grid Sweep (Finding optimal friction-adjusted threshold) ---")
    res_159915 = evaluate_etf_z_grid("159915ETF", z_grid=np.arange(0.3, 1.4, 0.1))
    for r in res_159915:
        print(f"  Z_th: {r['z_th']:<4} | Trades: {r['trades']:<3} | Cost Sharpe: {r['cost_sharpe']:.3f} | Raw Sharpe: {r['raw_sharpe']:.3f} | PnL: {r['pnl']:+.4f} | MaxDD: {r['max_dd']:.4f} | Turnover: {r['turnover']:.1f}x")

    # 3. Regularized Auto-Sweep Test (min 10% active days constraint)
    print("\n--- Regularized Threshold Auto-Sweep Test (min_active_pct=10.0%) ---")
    for etf in ["300ETF", "500ETF", "159915ETF"]:
        reg_res = test_regularized_sweep(etf, min_active_pct=10.0)
        if reg_res:
            print(f"  {etf:<10} | Train Opt: L:{reg_res['opt_train_l']}/S:{reg_res['opt_train_s']} -> Prod: L:{reg_res['z_prod_l']}/S:{reg_res['z_prod_s']} | Trades: {reg_res['trades']:<3} | Cost Sharpe: {reg_res['cost_sharpe']:.3f} | Raw Sharpe: {reg_res['raw_sharpe']:.3f} | PnL: {reg_res['pnl']:+.4f} | MaxDD: {reg_res['max_dd']:.4f}")


if __name__ == "__main__":
    main()
