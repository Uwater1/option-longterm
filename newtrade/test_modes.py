#!/usr/bin/env python3
"""Quick test: ensemble signal with different position modes + DSR at reduced trial counts."""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from math import sqrt

from robustness import (
    build_all_composites, compute_ensemble_composite,
    deflated_sharpe_ratio, run_cpcv_backtest,
)
from strategy import (
    sweep_optimal_threshold, compute_production_threshold,
    generate_positions, simulate_etf_spot, calculate_metrics,
)

ETFS = ["159915ETF", "500ETF", "300ETF"]
MODES = ["binary", "tanh", "quadratic"]

print("=" * 80)
print("ENSEMBLE POSITION MODE COMPARISON + DSR AT VARIOUS TRIAL COUNTS")
print("=" * 80)

for etf in ETFS:
    Z_composites, trade_returns, df, pool = build_all_composites(etf)
    if not Z_composites:
        print(f"\n  {etf}: SKIPPED (no features)")
        continue
    
    Z_ens = compute_ensemble_composite(Z_composites)
    
    t_start = pd.Timestamp("2022-01-01")
    t_end = pd.Timestamp("2026-01-01")
    train_mask = df["date"] < t_start
    oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
    
    ret_train = trade_returns[train_mask.values]
    ret_oos = trade_returns[oos_mask.values]
    Z_train = Z_ens[train_mask.values]
    Z_oos = Z_ens[oos_mask.values]
    
    print(f"\n{'─'*80}")
    print(f"  {etf} (N_features={len(pool)}, N_oos={len(ret_oos)})")
    print(f"{'─'*80}")
    print(f"  {'Mode':<12s} {'SR':>6s} {'PnL':>9s} {'Trades':>7s} {'WR%':>6s} "
          f"{'DSR(1)':>8s} {'DSR(4)':>8s} {'DSR(10)':>8s} {'DSR(50)':>8s}")
    
    for mode in MODES:
        sw = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=0.0008)
        zl, zs = compute_production_threshold(sw, z_buffer=0.1)
        pos = generate_positions(Z_oos, z_th=zl, z_th_short=zs, mode=mode)
        nr, rr, ff = simulate_etf_spot(ret_oos, pos, fee_bps=0.0008)
        
        std_n = np.std(nr)
        sr = float((np.mean(nr) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
        na = int((np.abs(pos) > 1e-5).sum())
        wr = float((nr[np.abs(pos) > 1e-5] > 0).mean() * 100) if na > 0 else 0.0
        
        sk_v = float(skew(nr))
        kt_v = float(kurtosis(nr))
        
        dsr_1 = deflated_sharpe_ratio(sr, n_trials=1, n_obs=len(nr), skewness=sk_v, kurtosis_excess=kt_v)
        dsr_4 = deflated_sharpe_ratio(sr, n_trials=4, n_obs=len(nr), skewness=sk_v, kurtosis_excess=kt_v)
        dsr_10 = deflated_sharpe_ratio(sr, n_trials=10, n_obs=len(nr), skewness=sk_v, kurtosis_excess=kt_v)
        dsr_50 = deflated_sharpe_ratio(sr, n_trials=50, n_obs=len(nr), skewness=sk_v, kurtosis_excess=kt_v)
        
        print(f"  {mode:<12s} {sr:>6.3f} {nr.sum():>+9.4f} {na:>7d} {wr:>5.1f}% "
              f"{dsr_1['dsr']:>8.3f} {dsr_4['dsr']:>8.3f} {dsr_10['dsr']:>8.3f} {dsr_50['dsr']:>8.3f}")
    
    # Also run CPCV for ensemble with tanh
    print(f"\n  CPCV (ensemble, tanh mode):")
    cpcv = run_cpcv_backtest(Z_ens, trade_returns, df["date"],
                              n_splits=6, n_test=2, purge_gap=5,
                              mode="tanh", fee_bps=0.0008, z_buffer=0.1)
    print(f"    median_SR={cpcv['sharpe_median']:.3f} ± {cpcv['sharpe_std']:.3f} "
          f"({cpcv['pct_positive']:.0f}% positive, {cpcv['n_folds']} folds)")

print("\n\nDone.")
