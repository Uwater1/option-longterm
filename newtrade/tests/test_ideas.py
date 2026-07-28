#!/usr/bin/env python3
"""
Test Idea 1 (Hybrid EMA IC + Partial Weight Adjustment) 
and Idea 2 (Dynamic Multi-Metric Score: IC + IC_IR + Monotonicity).
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from strategy import simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold, generate_positions

def compute_daily_ic_matrix(Z_signed: np.ndarray, trade_ret: np.ndarray) -> np.ndarray:
    """Compute daily cross-sectional or single-day feature ICs."""
    T, N = Z_signed.shape
    daily_ic = np.zeros((T, N))
    for t in range(T):
        r_t = trade_ret[t]
        for j in range(N):
            daily_ic[t, j] = Z_signed[t, j] * r_t
    return daily_ic

def run_experiment(etf="159915ETF", side="single", start_date="2022-01-01", end_date="2026-01-01",
                   allow_short=True, idea_mode="base", span=10, delta=0.1):
    pool = load_admitted_pool(etf, side=side)
    df = load_etf_dataset(etf)
    X, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X, burn_in=252)
    trade_ret = df["trade_return"].values
    
    T, N = Z_std.shape
    Z_signed = Z_std * signs
    exp_ic = expanding_factor_ic_numba(Z_std, signs, trade_ret, burn_in=252)
    
    w_min = 0.2 / N
    w_max = 1.8 / N
    
    weights_hist = np.zeros((T, N))
    Z_composite = np.zeros(T)
    
    if idea_mode == "base":
        # Base raw dynamic IC
        for t in range(T):
            r_t = rankdata(exp_ic[t], method="average")
            w_t = w_min + (w_max - w_min) * (r_t - 1.0) / (N - 1.0)
            w_t /= w_t.sum()
            weights_hist[t] = w_t
            Z_composite[t] = Z_signed[t] @ w_t

    elif idea_mode == "idea1_hybrid":
        # Idea 1: EMA IC + Partial Weight Adjustment
        alpha = 2.0 / (span + 1.0)
        ic_ema = np.zeros_like(exp_ic)
        ic_ema[0] = exp_ic[0]
        for t in range(1, T):
            ic_ema[t] = alpha * exp_ic[t] + (1.0 - alpha) * ic_ema[t-1]
            
        w_prev = np.ones(N) / N
        for t in range(T):
            r_t = rankdata(ic_ema[t], method="average")
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

    elif idea_mode == "idea2_multi_metric":
        # Idea 2: Dynamic Score (Expanding IC + Expanding IC_IR + Expanding Monotonicity)
        daily_ic = compute_daily_ic_matrix(Z_signed, trade_ret)
        
        # Calculate expanding metrics
        cum_ic = np.cumsum(daily_ic, axis=0)
        cum_sq_ic = np.cumsum(daily_ic**2, axis=0)
        cum_pos_ic = np.cumsum(daily_ic > 0, axis=0)
        
        score_mat = np.zeros((T, N))
        for t in range(252, T):
            n_samples = t
            mean_ic = cum_ic[t-1] / n_samples
            var_ic = (cum_sq_ic[t-1] / n_samples) - mean_ic**2
            std_ic = np.sqrt(np.maximum(1e-12, var_ic))
            ic_ir = mean_ic / std_ic
            mono = cum_pos_ic[t-1] / n_samples
            
            r_ic = rankdata(mean_ic) / N
            r_ir = rankdata(ic_ir) / N
            r_mono = rankdata(mono) / N
            
            score_mat[t] = 0.40 * r_ic + 0.35 * r_ir + 0.25 * r_mono

        for t in range(252):
            score_mat[t] = score_mat[252]
            
        w_prev = np.ones(N) / N
        for t in range(T):
            r_t = rankdata(score_mat[t], method="average")
            w_target = w_min + (w_max - w_min) * (r_t - 1.0) / (N - 1.0)
            w_target /= w_target.sum()
            
            # Apply light partial adjustment
            if t == 0:
                w_t = w_target
            else:
                w_t = w_prev + delta * (w_target - w_prev)
                w_t /= w_t.sum()
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
    
    sweep_info = sweep_optimal_threshold(Z_train, trade_ret_train, mode="binary", fee_bps=0.0008, long_only=not allow_short)
    z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=0.1, z_short_buffer=0.2 if allow_short else 0.1)
    
    df_oos = df[oos_mask.values].copy()
    Z_oos = Z_composite[oos_mask.values]
    trade_ret_oos = trade_ret[oos_mask.values]
    
    pos = generate_positions(Z_oos, z_th=z_th_prod, mode="binary", long_only=not allow_short, z_th_short=z_th_short)
    net_returns, raw_returns, fees = simulate_etf_spot(trade_ret_oos, pos, fee_bps=0.0008)
    m = calculate_metrics(net_returns, raw_returns, pos)
    
    weights_oos = weights_hist[oos_mask.values]
    w_turnover = np.abs(np.diff(weights_oos, axis=0)).sum(axis=1).mean()
    
    n_long = int((pos > 1e-5).sum())
    n_short = int((pos < -1e-5).sum())
    
    return {
        "etf": etf,
        "mode": idea_mode,
        "span": span,
        "delta": delta,
        "trades": m.get("n_trades", 0),
        "long_trades": n_long,
        "short_trades": n_short,
        "cost_sharpe": round(m.get("cost_sharpe", 0.0), 3),
        "total_pnl": round(m.get("total_pnl", 0.0), 4),
        "win_rate": round(m.get("win_rate_pct", 0.0), 1),
        "max_dd": round(m.get("max_drawdown", 0.0), 4),
        "w_turnover": round(w_turnover, 4),
        "z_th_long": round(z_th_prod, 2),
        "z_th_short": round(z_th_short, 2),
    }

if __name__ == "__main__":
    print("=== TESTING IDEA 1 (Hybrid EMA+Partial) & IDEA 2 (Dynamic Multi-Metric Score) ===")
    
    for allow_short in [False, True]:
        mode_str = "ALLOW-SHORT (Options/Futures)" if allow_short else "LONG-ONLY (Spot ETF)"
        print(f"\n==================== MODE: {mode_str} ====================")
        
        for etf in ["159915ETF", "300ETF", "500ETF"]:
            print(f"\n--- {etf} ---")
            b = run_experiment(etf, idea_mode="base", allow_short=allow_short)
            print(f"Base Raw Dynamic IC   : Sharpe={b['cost_sharpe']:5.3f} | PnL={b['total_pnl']:+6.4f} | Win={b['win_rate']:4.1f}% | DD={b['max_dd']:6.4f} | Trades={b['trades']:3d} (L:{b['long_trades']}/S:{b['short_trades']}) | Z_th=L:{b['z_th_long']}/S:{b['z_th_short']}")

            # Idea 1
            i1 = run_experiment(etf, idea_mode="idea1_hybrid", span=10, delta=0.1, allow_short=allow_short)
            print(f"Idea 1 (EMA10+Partial): Sharpe={i1['cost_sharpe']:5.3f} | PnL={i1['total_pnl']:+6.4f} | Win={i1['win_rate']:4.1f}% | DD={i1['max_dd']:6.4f} | Trades={i1['trades']:3d} (L:{i1['long_trades']}/S:{i1['short_trades']}) | Z_th=L:{i1['z_th_long']}/S:{i1['z_th_short']}")

            # Idea 2
            i2 = run_experiment(etf, idea_mode="idea2_multi_metric", span=10, delta=0.1, allow_short=allow_short)
            print(f"Idea 2 (Multi-Metric) : Sharpe={i2['cost_sharpe']:5.3f} | PnL={i2['total_pnl']:+6.4f} | Win={i2['win_rate']:4.1f}% | DD={i2['max_dd']:6.4f} | Trades={i2['trades']:3d} (L:{i2['long_trades']}/S:{i2['short_trades']}) | Z_th=L:{i2['z_th_long']}/S:{i2['z_th_short']}")
