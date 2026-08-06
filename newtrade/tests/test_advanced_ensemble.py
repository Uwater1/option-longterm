#!/usr/bin/env python3
"""
Fast Cached Advanced Ensemble Research Experiments:
1. Shrinkage Intensity Lambda: Z_composite = lambda*Z_ew + (1-lambda)*Z_icw
   for lambda in [0.0, 0.20, 0.35, 0.50, 0.65, 0.80, 1.00].
2. ICIR (IC / std(IC)) scheme vs Raw ICW.
3. 3-Way Ensemble: (Z_ew + Z_icw + Z_icir) / 3 vs 2-Way Baseline.
4. Walk-forward OOS validation across 2022-2026, 2023-2026, 2024-2026.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, rolling_tail_ic_numba, rolling_factor_risk_numba
)
from weighting import _get_top_k_indices, compute_ew, compute_icw
from strategy import generate_positions, simulate_etf_spot, calculate_metrics

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
PERIODS = [
    ("2022-01-01", "2026-01-01", "2022-2026"),
    ("2023-01-01", "2026-01-01", "2023-2026"),
    ("2024-01-01", "2026-01-01", "2024-2026"),
]

def simulate_signal(Z_composite, trade_ret, df, etf, start_date, end_date):
    date_ser = pd.to_datetime(df["date"])
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    
    z_th_l = 1.20 if etf in ["300ETF", "50ETF"] else 0.90
    z_th_s = 1.30 if etf in ["300ETF", "50ETF"] else 1.10
    
    oos_mask = (date_ser >= start_ts) & (date_ser < end_ts)
    if not oos_mask.any():
        return {}
    
    Z_oos = Z_composite[oos_mask]
    ret_oos = trade_ret[oos_mask]
    dates_oos = date_ser[oos_mask]
    
    pos = generate_positions(Z_oos, z_th=z_th_l, z_th_short=z_th_s, mode="binary")
    net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, pos, fee_bps=0.0008)
    return calculate_metrics(net_ret, raw_ret, pos, dates_oos)


def main():
    print("================================================================================")
    print("FAST CACHED ADVANCED ENSEMBLE RESEARCH EXPERIMENTS")
    print("================================================================================")

    records = []

    for etf in AVAILABLE_ETFS:
        print(f"\n---> Precomputing signals for {etf}...")
        df = load_etf_dataset(etf)
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue
        
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        Z_std = expanding_zscore_numba(X_raw, burn_in=252, clip=3.0)
        trade_ret = df["trade_return"].values.astype(np.float64)
        
        tail_ic = rolling_tail_ic_numba(Z_std, signs, trade_ret, window=480, tail_pct=0.10, burn_in=252)
        _, sortino_mat = rolling_factor_risk_numba(Z_std, signs, trade_ret, window=480, burn_in=252)
        ic_smoothed = np.where(sortino_mat <= 0.0, -10.0, tail_ic)
        
        T, N = Z_std.shape
        Z_icw = compute_icw(Z_std, signs, pool=pool, n_train=1700, top_k=10, expanding_ic=ic_smoothed)
        Z_ew = compute_ew(Z_std, signs, pool=pool, top_k=10, expanding_ic=ic_smoothed)
        
        # ICIR Signal
        ic_df = pd.DataFrame(tail_ic)
        ic_mean = ic_df.rolling(window=480, min_periods=10).mean().shift(1).fillna(0.0).values
        ic_std = ic_df.rolling(window=480, min_periods=10).std().shift(1).fillna(1.0).values + 1e-4
        icir_mat = ic_mean / ic_std
        icir_gated = np.where(sortino_mat <= 0.0, -10.0, icir_mat)
        
        Z_icir = np.zeros(T, dtype=np.float64)
        Z_signed = Z_std * signs
        for t in range(T):
            top_idx = _get_top_k_indices(icir_gated[t], 10)
            raw_w = np.maximum(0.0, icir_gated[t, top_idx])
            w_sum = raw_w.sum()
            w_t = np.zeros(N, dtype=np.float64)
            if w_sum < 1e-12:
                w_t[top_idx] = 1.0 / float(len(top_idx))
            else:
                w_t[top_idx] = raw_w / w_sum
            Z_icir[t] = Z_signed[t] @ w_t

        for start_date, end_date, period_label in PERIODS:
            # 1. Lambda Shrinkage Sweep
            lambdas = [0.0, 0.20, 0.35, 0.50, 0.65, 0.80, 1.00]
            for lmb in lambdas:
                Z_comp = lmb * Z_ew + (1.0 - lmb) * Z_icw
                m = simulate_signal(Z_comp, trade_ret, df, etf, start_date, end_date)
                if m:
                    records.append({
                        "Period": period_label,
                        "Category": "1. Lambda Shrinkage",
                        "Experiment": f"Lambda={lmb:.2f} ({lmb:.0%} EW / {1-lmb:.0%} ICW)",
                        "ETF": etf,
                        "Cost Sharpe": m["cost_sharpe"],
                        "Total PnL": m["total_pnl"],
                        "Max DD": m["max_drawdown"],
                        "Turnover": m["ann_turnover"],
                    })

            # 2. Standalone ICIR
            m_icir = simulate_signal(Z_icir, trade_ret, df, etf, start_date, end_date)
            if m_icir:
                records.append({
                    "Period": period_label,
                    "Category": "2. ICIR Scheme",
                    "Experiment": "Standalone ICIR (IC/std(IC))",
                    "ETF": etf,
                    "Cost Sharpe": m_icir["cost_sharpe"],
                    "Total PnL": m_icir["total_pnl"],
                    "Max DD": m_icir["max_drawdown"],
                    "Turnover": m_icir["ann_turnover"],
                })

            # 3. 3-Way Ensemble (EW + ICW + ICIR)
            Z_3way = (Z_ew + Z_icw + Z_icir) / 3.0
            m_3way = simulate_signal(Z_3way, trade_ret, df, etf, start_date, end_date)
            if m_3way:
                records.append({
                    "Period": period_label,
                    "Category": "3. 3-Way Ensemble",
                    "Experiment": "3-Way Ensemble (EW + ICW + ICIR)",
                    "ETF": etf,
                    "Cost Sharpe": m_3way["cost_sharpe"],
                    "Total PnL": m_3way["total_pnl"],
                    "Max DD": m_3way["max_drawdown"],
                    "Turnover": m_3way["ann_turnover"],
                })

    df = pd.DataFrame(records)
    out_csv = HERE / "advanced_ensemble_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")

    # Aggregated Summary
    avg_df = df.groupby(["Period", "Category", "Experiment"])[["Cost Sharpe", "Total PnL", "Max DD", "Turnover"]].mean().reset_index()
    avg_df = avg_df.sort_values(["Period", "Category", "Cost Sharpe"], ascending=[True, True, False])

    print("\n================================================================================")
    print("CROSS-ETF AVERAGE PERFORMANCE BY RESEARCH DIRECTION")
    print("================================================================================")
    print(avg_df.to_string(index=False))

if __name__ == "__main__":
    main()
