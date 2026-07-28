#!/usr/bin/env python3
"""
Diagnostic test script for Dynamic IC Smoothing Options in NewTrade.
Tests Option 1 (IC EMA), Option 2 (Weight Partial Adjustment), Option 3 (No-Update Band).
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from strategy import simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold
from weighting import compute_rank_w

def run_smoothed_dynamic_ic_backtest(etf="159915ETF", side="single", start_date="2022-01-01", end_date="2026-01-01",
                                     mode="none", param=None, z_buffer=0.1):
    pool = load_admitted_pool(etf, side=side)
    df = load_etf_dataset(etf)
    X, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X, burn_in=252)
    trade_ret = df["trade_return"].values
    
    exp_ic = expanding_factor_ic_numba(Z_std, signs, trade_ret, burn_in=252)
    T, N = Z_std.shape
    Z_signed = Z_std * signs
    
    w_min = 0.2 / N
    w_max = 1.8 / N
    
    # Process IC / Weights according to smoothing mode
    if mode == "none":
        # Baseline raw expanding IC
        ic_mat = exp_ic
        weights_hist = np.zeros((T, N))
        Z_composite = np.zeros(T)
        for t in range(T):
            r_t = rankdata(ic_mat[t], method="average")
            w_t = w_min + (w_max - w_min) * (r_t - 1.0) / (N - 1.0)
            w_t /= w_t.sum()
            weights_hist[t] = w_t
            Z_composite[t] = Z_signed[t] @ w_t

    elif mode == "ema_ic":
        # Option 1: EMA on expanding IC matrix
        span = param  # e.g., 10, 20, 30 days
        alpha = 2.0 / (span + 1.0)
        ic_mat = np.zeros_like(exp_ic)
        ic_mat[0] = exp_ic[0]
        for t in range(1, T):
            ic_mat[t] = alpha * exp_ic[t] + (1.0 - alpha) * ic_mat[t-1]
            
        weights_hist = np.zeros((T, N))
        Z_composite = np.zeros(T)
        for t in range(T):
            r_t = rankdata(ic_mat[t], method="average")
            w_t = w_min + (w_max - w_min) * (r_t - 1.0) / (N - 1.0)
            w_t /= w_t.sum()
            weights_hist[t] = w_t
            Z_composite[t] = Z_signed[t] @ w_t

    elif mode == "partial_w":
        # Option 2: Partial Adjustment Rule on Weights w_t = w_{t-1} + delta * (w_t^* - w_{t-1})
        delta = param  # e.g., 0.05, 0.1, 0.2
        weights_hist = np.zeros((T, N))
        w_prev = np.ones(N) / N
        Z_composite = np.zeros(T)
        for t in range(T):
            r_t = rankdata(exp_ic[t], method="average")
            w_target = w_min + (w_max - w_min) * (r_t - 1.0) / (N - 1.0)
            w_target /= w_target.sum()
            
            if t == 0:
                w_t = w_target
            else:
                w_t = w_prev + delta * (w_target - w_prev)
                w_t /= w_t.sum()
            w_prev = w_t
            weights_hist[t] = w_t
            Z_composite[t] = Z_signed[t] @ w_t

    elif mode == "band_w":
        # Option 3: Weight Hysteresis / No-trade band (only update if L1 shift > band)
        band = param  # e.g. 0.05, 0.1
        weights_hist = np.zeros((T, N))
        w_prev = np.ones(N) / N
        Z_composite = np.zeros(T)
        for t in range(T):
            r_t = rankdata(exp_ic[t], method="average")
            w_target = w_min + (w_max - w_min) * (r_t - 1.0) / (N - 1.0)
            w_target /= w_target.sum()
            
            if t == 0 or np.abs(w_target - w_prev).sum() > band:
                w_t = w_target
            else:
                w_t = w_prev
            w_prev = w_t
            weights_hist[t] = w_t
            Z_composite[t] = Z_signed[t] @ w_t

    # Filter to OOS
    t_start_ts = pd.Timestamp(start_date)
    t_end_ts = pd.Timestamp(end_date)
    train_mask = df["date"] < t_start_ts
    oos_mask = (df["date"] >= t_start_ts) & (df["date"] < t_end_ts)
    
    Z_train = Z_composite[train_mask.values]
    trade_ret_train = trade_ret[train_mask.values]
    
    sweep_info = sweep_optimal_threshold(Z_train, trade_ret_train, mode="binary", fee_bps=0.0008)
    z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer)
    
    df_oos = df[oos_mask.values].copy()
    Z_oos = Z_composite[oos_mask.values]
    
    # Calculate weight turnover: sum of |w_t - w_{t-1}| across days
    weights_oos = weights_hist[oos_mask.values]
    w_turnover = np.abs(np.diff(weights_oos, axis=0)).sum(axis=1).mean()
    
    from strategy import generate_positions
    pos = generate_positions(Z_oos, z_th=z_th_prod, mode="binary", long_only=False, z_th_short=z_th_short)
    trade_ret_oos = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df_oos.columns else df_oos["close"].pct_change().fillna(0.0).values
    net_returns, raw_returns, fees = simulate_etf_spot(trade_ret_oos, pos, fee_bps=0.0008)
    m = calculate_metrics(net_returns, raw_returns, pos)
    
    n_trades = int((np.abs(np.diff(np.pad(pos, (1, 0)))) > 1e-5).sum()) // 2
    if n_trades == 0 and (np.abs(pos) > 1e-5).any():
        n_trades = int((np.abs(np.diff(np.pad(pos, (1, 0)))) > 1e-5).sum())

    return {
        "etf": etf,
        "mode": mode,
        "param": param,
        "trades": m.get("n_trades", n_trades),
        "cost_sharpe": round(m.get("cost_sharpe", 0.0), 3),
        "total_pnl": round(m.get("total_pnl", 0.0), 4),
        "win_rate": round(m.get("win_rate_pct", 0.0), 1),
        "max_dd": round(m.get("max_drawdown", 0.0), 4),
        "w_turnover_daily": round(w_turnover, 4),
        "z_th_long": round(z_th_prod, 2),
        "z_th_short": round(z_th_short, 2),
    }

if __name__ == "__main__":
    print("=== DYNAMIC IC SMOOTHING EXPERIMENT ===")
    etfs = ["159915ETF", "300ETF", "500ETF"]
    
    for etf in etfs:
        print(f"\n------------------- {etf} -------------------")
        # Baseline raw dynamic IC
        base = run_smoothed_dynamic_ic_backtest(etf, mode="none")
        print(f"Base Unsmoothed: Trades={base['trades']}, Cost Sharpe={base['cost_sharpe']}, PnL={base['total_pnl']}, Win={base['win_rate']}%, MaxDD={base['max_dd']}, WeightTurnover/Day={base['w_turnover_daily']}")
        
        # Option 1: EMA IC
        for span in [5, 10, 20, 40]:
            res = run_smoothed_dynamic_ic_backtest(etf, mode="ema_ic", param=span)
            print(f"Opt 1 (EMA span={span:02d}): Trades={res['trades']}, Cost Sharpe={res['cost_sharpe']}, PnL={res['total_pnl']}, Win={res['win_rate']}%, MaxDD={res['max_dd']}, WeightTurnover/Day={res['w_turnover_daily']}")

        # Option 2: Partial Weight Adjustment
        for delta in [0.02, 0.05, 0.10, 0.20]:
            res = run_smoothed_dynamic_ic_backtest(etf, mode="partial_w", param=delta)
            print(f"Opt 2 (Partial delta={delta:.2f}): Trades={res['trades']}, Cost Sharpe={res['cost_sharpe']}, PnL={res['total_pnl']}, Win={res['win_rate']}%, MaxDD={res['max_dd']}, WeightTurnover/Day={res['w_turnover_daily']}")

        # Option 3: Weight Hysteresis Band
        for band in [0.02, 0.05, 0.10]:
            res = run_smoothed_dynamic_ic_backtest(etf, mode="band_w", param=band)
            print(f"Opt 3 (Band band={band:.2f}): Trades={res['trades']}, Cost Sharpe={res['cost_sharpe']}, PnL={res['total_pnl']}, Win={res['win_rate']}%, MaxDD={res['max_dd']}, WeightTurnover/Day={res['w_turnover_daily']}")
