#!/usr/bin/env python3
"""Diagnose: why production is long-only, and find optimal per-ETF config."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from math import sqrt

from robustness import build_all_composites, compute_ensemble_composite, deflated_sharpe_ratio, run_cpcv_backtest
from strategy import sweep_optimal_threshold, compute_production_threshold, generate_positions, simulate_etf_spot

ETFS = ["159915ETF", "500ETF", "300ETF"]
MODES = ["binary", "tanh", "quadratic"]
BUFFERS = [0.10, 0.15, 0.20]

print("=" * 90)
print("DIAGNOSTIC: SHORT-SIDE ANALYSIS + PER-ETF OPTIMAL CONFIG")
print("=" * 90)

best_configs = {}

for etf in ETFS:
    Z_composites, trade_returns, df, pool = build_all_composites(etf)
    if not Z_composites:
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
    n_oos = int(oos_mask.sum())
    
    print(f"\n{'━'*90}")
    print(f"  {etf} (N_feat={len(pool)}, N_oos={n_oos})")
    print(f"{'━'*90}")
    
    # Part 1: Sweep diagnostics — what does train find?
    print(f"\n  [A] Train threshold sweep diagnostics:")
    for mode in MODES:
        sw = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=0.0008)
        print(f"    {mode:10s}: train_long={sw['optimal_z_th_long']:.2f} "
              f"train_short={sw['optimal_z_th_short']:.2f} "
              f"best_SR_long={sw['best_sharpe']:.3f} "
              f"best_SR_short={sw['best_sharpe_short']:.3f}")
    
    # Part 2: Long-only vs Long+Short comparison
    print(f"\n  [B] Long-only vs Long+Short (buffer=0.15):")
    print(f"    {'Mode':<12s} {'Side':<8s} {'SR':>6s} {'PnL':>9s} {'Trades':>7s} {'WR%':>6s} {'DSR10':>7s}")
    
    best_sr = -999
    best_cfg = None
    
    for mode in MODES:
        for long_only in [True, False]:
            sw = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=0.0008, long_only=long_only)
            zl, zs = compute_production_threshold(sw, z_buffer=0.15)
            pos = generate_positions(Z_oos, z_th=zl, z_th_short=zs, mode=mode, long_only=long_only)
            nr, _, _ = simulate_etf_spot(ret_oos, pos, fee_bps=0.0008)
            
            std_n = np.std(nr)
            sr = float((np.mean(nr) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
            na = int((np.abs(pos) > 1e-5).sum())
            n_long = int((pos > 1e-5).sum())
            n_short = int((pos < -1e-5).sum())
            wr = float((nr[np.abs(pos) > 1e-5] > 0).mean() * 100) if na > 0 else 0.0
            
            sk_v = float(skew(nr))
            kt_v = float(kurtosis(nr))
            dsr = deflated_sharpe_ratio(sr, n_trials=10, n_obs=n_oos, skewness=sk_v, kurtosis_excess=kt_v)
            
            side_str = "L-only" if long_only else "L+S"
            print(f"    {mode:<12s} {side_str:<8s} {sr:>6.3f} {nr.sum():>+9.4f} {na:>4d}({n_long}L/{n_short}S) {wr:>5.1f}% {dsr['dsr']:>7.3f}")
            
            # Track best by DSR
            if dsr['dsr'] > best_sr:
                best_sr = dsr['dsr']
                best_cfg = {"mode": mode, "long_only": long_only, "sr": sr, "dsr": dsr['dsr'],
                           "pnl": float(nr.sum()), "trades": na, "wr": wr,
                           "z_th_l": zl, "z_th_s": zs}
    
    # Part 3: Buffer sensitivity for best mode
    if best_cfg:
        mode = best_cfg["mode"]
        long_only = best_cfg["long_only"]
        print(f"\n  [C] Buffer sensitivity for {mode} ({'L-only' if long_only else 'L+S'}):")
        print(f"    {'Buffer':>8s} {'SR':>6s} {'PnL':>9s} {'Trades':>7s} {'DSR10':>7s} {'DSR50':>7s}")
        
        for buf in BUFFERS:
            sw = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=0.0008, long_only=long_only)
            zl, zs = compute_production_threshold(sw, z_buffer=buf)
            pos = generate_positions(Z_oos, z_th=zl, z_th_short=zs, mode=mode, long_only=long_only)
            nr, _, _ = simulate_etf_spot(ret_oos, pos, fee_bps=0.0008)
            
            std_n = np.std(nr)
            sr = float((np.mean(nr) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
            na = int((np.abs(pos) > 1e-5).sum())
            sk_v = float(skew(nr))
            kt_v = float(kurtosis(nr))
            dsr10 = deflated_sharpe_ratio(sr, n_trials=10, n_obs=n_oos, skewness=sk_v, kurtosis_excess=kt_v)
            dsr50 = deflated_sharpe_ratio(sr, n_trials=50, n_obs=n_oos, skewness=sk_v, kurtosis_excess=kt_v)
            
            print(f"    {buf:>8.2f} {sr:>6.3f} {nr.sum():>+9.4f} {na:>7d} {dsr10['dsr']:>7.3f} {dsr50['dsr']:>7.3f}")
    
    best_configs[etf] = best_cfg
    print(f"\n  ★ BEST CONFIG: {best_cfg}")

# Summary
print(f"\n\n{'='*90}")
print("OPTIMAL PER-ETF CONFIGURATION SUMMARY")
print(f"{'='*90}")
for etf, cfg in best_configs.items():
    if cfg:
        print(f"  {etf:12s}: mode={cfg['mode']:<10s} long_only={cfg['long_only']!s:<6s} "
              f"SR={cfg['sr']:.3f} DSR10={cfg['dsr']:.3f} PnL={cfg['pnl']:+.4f}")
