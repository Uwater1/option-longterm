#!/usr/bin/env python3
"""
Diagnostic script for analyzing dynamic factor weighting metrics in NewTrade.
Compares:
1. Metric components: Pure IC, Pure IC_IR, Pure Mono, Multi-Score (IC+IR+Mono), Static.
2. Windowing schemes: Expanding vs Rolling EMA (span=10, 30, 60, 120, 252).
3. Metric formulas: Correlation-based IC vs Cross-product IC.
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba
from weighting import compute_rank_w
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold

ETFS = ["300ETF", "500ETF", "159915ETF"]
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"
FEE_BPS = 0.0008  # 8 bps


def compute_expanding_metrics(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray, burn_in: int = 252):
    """
    Computes expanding components separately:
    - true_ic: correlation IC
    - prod_ic: mean(Z_signed * r)
    - ic_ir: prod_ic / std(Z_signed * r)
    - mono: fraction(Z_signed * r > 0)
    """
    T, N = Z_std.shape
    Z_signed = Z_std * signs
    daily_prod = np.zeros((T, N), dtype=np.float64)
    for t in range(T):
        daily_prod[t] = Z_signed[t] * trade_returns[t]

    cum_prod = np.cumsum(daily_prod, axis=0)
    cum_sq_prod = np.cumsum(daily_prod**2, axis=0)
    cum_pos = np.cumsum(daily_prod > 0, axis=0)

    true_ic_mat = np.zeros((T, N), dtype=np.float64)
    prod_ic_mat = np.zeros((T, N), dtype=np.float64)
    ic_ir_mat = np.zeros((T, N), dtype=np.float64)
    mono_mat = np.zeros((T, N), dtype=np.float64)

    for t in range(burn_in, T):
        ret_sub = trade_returns[:t]
        std_ret = np.std(ret_sub)
        n_samples = float(t)

        m_prod = cum_prod[t-1] / n_samples
        v_prod = (cum_sq_prod[t-1] / n_samples) - m_prod**2
        s_prod = np.sqrt(np.maximum(1e-12, v_prod))

        prod_ic_mat[t] = m_prod
        ic_ir_mat[t] = m_prod / s_prod
        mono_mat[t] = cum_pos[t-1] / n_samples

        if std_ret > 1e-12:
            m_ret = np.mean(ret_sub)
            for j in range(N):
                z_sub = Z_signed[:t, j]
                std_z = np.std(z_sub)
                if std_z > 1e-12:
                    cov = np.mean((z_sub - np.mean(z_sub)) * (ret_sub - m_ret))
                    true_ic_mat[t, j] = cov / (std_z * std_ret)

    # Fill burn-in
    if burn_in < T:
        true_ic_mat[:burn_in] = true_ic_mat[burn_in]
        prod_ic_mat[:burn_in] = prod_ic_mat[burn_in]
        ic_ir_mat[:burn_in] = ic_ir_mat[burn_in]
        mono_mat[:burn_in] = mono_mat[burn_in]

    return true_ic_mat, prod_ic_mat, ic_ir_mat, mono_mat


def run_experiment_metric(etf: str, metric_name: str, span: int = 10):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None

    df = load_etf_dataset(etf)
    trade_ret = df["trade_return"].values.astype(np.float64)
    X_raw, signs, _ = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    true_ic, prod_ic, ic_ir, mono = compute_expanding_metrics(Z_std, signs, trade_ret, burn_in=burn_in)
    N = len(pool)

    # Determine metric matrix
    if metric_name == "static":
        exp_mat = None
    elif metric_name == "true_ic":
        exp_mat = true_ic
    elif metric_name == "prod_ic":
        exp_mat = prod_ic
    elif metric_name == "ic_ir":
        exp_mat = ic_ir
    elif metric_name == "mono":
        exp_mat = mono
    elif metric_name == "multi_equal": # 1/3 IC + 1/3 IR + 1/3 Mono
        score_mat = np.zeros_like(true_ic)
        for t in range(len(df)):
            r_ic = rankdata(true_ic[t]) / N
            r_ir = rankdata(ic_ir[t]) / N
            r_mono = rankdata(mono[t]) / N
            score_mat[t] = (r_ic + r_ir + r_mono) / 3.0
        exp_mat = score_mat
    elif metric_name == "multi_b3": # 0.40 IC + 0.35 IR + 0.25 Mono
        score_mat = np.zeros_like(true_ic)
        for t in range(len(df)):
            r_ic = rankdata(true_ic[t]) / N
            r_ir = rankdata(ic_ir[t]) / N
            r_mono = rankdata(mono[t]) / N
            score_mat[t] = 0.40 * r_ic + 0.35 * r_ir + 0.25 * r_mono
        exp_mat = score_mat
    elif metric_name == "ic_plus_mono": # 0.7 IC + 0.3 Mono (no IR)
        score_mat = np.zeros_like(true_ic)
        for t in range(len(df)):
            r_ic = rankdata(true_ic[t]) / N
            r_mono = rankdata(mono[t]) / N
            score_mat[t] = 0.70 * r_ic + 0.30 * r_mono
        exp_mat = score_mat
    else:
        raise ValueError(f"Unknown metric {metric_name}")

    rank_kwargs = {
        "w_min_ratio": 0.2,
        "w_max_ratio": 1.8,
        "mapping_shape": "linear",
        "ic_ema_span": span,
        "expanding_ic": exp_mat,
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
        "metric": metric_name,
        "span": span,
        "trades": m["n_trades"],
        "cost_sharpe": m["cost_sharpe"],
        "raw_sharpe": m["raw_sharpe"],
        "pnl": m["total_pnl"],
        "max_dd": m["max_drawdown"],
        "win_rate": m["win_rate_pct"],
        "turnover": m["ann_turnover"],
    }


def main():
    metrics_to_test = ["static", "true_ic", "prod_ic", "ic_ir", "mono", "multi_b3", "multi_equal", "ic_plus_mono"]
    results = []

    print("================================================================================")
    print("DYNAMIC METRIC DEEP-DIVE DIAGNOSTIC")
    print("================================================================================")

    for etf in ETFS:
        print(f"\n--- {etf} ---")
        for m in metrics_to_test:
            res = run_experiment_metric(etf, m, span=10)
            if res:
                results.append(res)
                print(f"  Metric: {m:<14} | Sharpe: {res['cost_sharpe']:.3f} | PnL: {res['pnl']:+.4f} | MaxDD: {res['max_dd']:.4f} | Trades: {res['trades']:<3} | Turnover: {res['turnover']:.1f}x")

    df_res = pd.DataFrame(results)
    out_csv = HERE / "artifacts" / "diagnostic_dynamic_metrics.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_res.to_csv(out_csv, index=False)
    print(f"\nDiagnostic results saved to {out_csv}")


if __name__ == "__main__":
    main()
