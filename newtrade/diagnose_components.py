#!/usr/bin/env python3
"""
Component Diagnostic: What actually drives the alpha?

Research design:
- Test each scheme individually (EW, ICW, Score, Rank)
- For Score/Rank: with vs without dynamic IC
- PRIMARY metric: per-year Sharpe on FULL history (not just OOS)
- Fixed threshold (no sweep) to isolate signal quality from threshold fitting
- OOS shown only as final confirmation

Questions answered:
1. Does dynamic IC actually improve signal vs static weights?
2. Which scheme has the most consistent year-by-year edge?
3. Where does each scheme fail?
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, expanding_factor_ic_numba)
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot

ETFS = ["300ETF", "500ETF", "159915ETF"]
FEE_BPS = 0.0008
FIXED_Z_TH = 0.8  # Fixed threshold — no sweep, isolates signal quality
BURN_IN = 252

SCHEMES = [
    ("ew", False, "EW (static equal weight)"),
    ("icw", False, "ICW (static IC-shrinkage)"),
    ("score", False, "Score (static pool metadata)"),
    ("score", True, "Score + Dynamic IC"),
    ("rank", False, "Rank (static bounds)"),
    ("rank", True, "Rank + Dynamic IC"),
]


def compute_composite(Z_std, signs, pool, full_trade_ret, scheme_name, use_dynamic_ic, burn_in, n_train):
    """Compute composite signal for a given scheme configuration."""
    scheme_func = get_weighting_scheme(scheme_name)
    kwargs = {}
    
    if scheme_name in ("rank", "score"):
        kwargs = {
            "w_min_ratio": 0.2,
            "w_max_ratio": 1.8,
            "mapping_shape": "linear",
            "ic_ema_span": 30,
        }
        if use_dynamic_ic:
            IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
            kwargs["expanding_ic"] = IC_mat
    
    Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train, **kwargs)
    return Z_composite


def yearly_sharpe(net_returns, dates):
    """Compute per-year annualized Sharpe."""
    df = pd.DataFrame({"ret": net_returns, "date": dates})
    df["year"] = df["date"].dt.year
    results = {}
    for year, grp in df.groupby("year"):
        if len(grp) < 20:
            continue
        std = grp["ret"].std()
        sr = (grp["ret"].mean() / std * np.sqrt(252)) if std > 1e-12 else 0.0
        results[year] = round(sr, 3)
    return results


def run_diagnostic():
    print("=" * 90)
    print("COMPONENT DIAGNOSTIC: Signal Quality by Scheme × Dynamic IC")
    print(f"Fixed Z_th={FIXED_Z_TH} (no sweep) | Fee={FEE_BPS*10000:.0f}bps | Binary L+S")
    print("=" * 90)
    
    all_results = []
    
    for etf in ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool or len(pool) < 10:
            print(f"\n  [{etf}] SKIP — pool too small ({len(pool) if pool else 0})")
            continue
        
        df = load_etf_dataset(etf)
        if "trade_return" in df.columns:
            full_trade_ret = df["trade_return"].values.astype(np.float64)
        else:
            full_trade_ret = df["close"].pct_change().fillna(0.0).values
        
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
        
        n_train = int((df["date"] < pd.Timestamp("2022-01-01")).sum())
        dates = df["date"]
        
        print(f"\n{'─' * 90}")
        print(f"  {etf} | {len(pool)} features | {len(df)} days | train_end=2022-01-01")
        print(f"{'─' * 90}")
        print(f"  {'Scheme':<28} {'Full SR':>8} {'Train SR':>9} {'OOS SR':>8} {'Trades':>7} {'WinRate':>8} | Per-Year Sharpe")
        print(f"  {'─'*28} {'─'*8} {'─'*9} {'─'*8} {'─'*7} {'─'*8} | {'─'*40}")
        
        for scheme_name, use_dyn, label in SCHEMES:
            Z_comp = compute_composite(Z_std, signs, pool, full_trade_ret,
                                       scheme_name, use_dyn, BURN_IN, n_train)
            
            # Generate positions with FIXED threshold
            positions = generate_positions(Z_comp, z_th=FIXED_Z_TH, z_th_short=FIXED_Z_TH,
                                           mode="binary", long_only=False)
            net_ret, _, _ = simulate_etf_spot(full_trade_ret, positions, fee_bps=FEE_BPS)
            
            # Full-period metrics
            std_full = np.std(net_ret[BURN_IN:])
            sr_full = (np.mean(net_ret[BURN_IN:]) / std_full * np.sqrt(252)) if std_full > 1e-12 else 0.0
            
            # Train vs OOS split
            train_mask = dates < pd.Timestamp("2022-01-01")
            oos_mask = dates >= pd.Timestamp("2022-01-01")
            
            train_ret = net_ret[train_mask.values]
            oos_ret = net_ret[oos_mask.values]
            
            std_tr = np.std(train_ret[BURN_IN:])
            sr_train = (np.mean(train_ret[BURN_IN:]) / std_tr * np.sqrt(252)) if std_tr > 1e-12 else 0.0
            
            std_oos = np.std(oos_ret)
            sr_oos = (np.mean(oos_ret) / std_oos * np.sqrt(252)) if std_oos > 1e-12 else 0.0
            
            n_trades = int((np.abs(positions) > 1e-5).sum())
            active_ret = net_ret[np.abs(positions) > 1e-5]
            win_rate = (active_ret > 0).mean() * 100 if len(active_ret) > 0 else 0.0
            
            # Per-year breakdown
            yr_sr = yearly_sharpe(net_ret[BURN_IN:], dates.iloc[BURN_IN:])
            yr_str = " ".join(f"{y}:{v:+.2f}" for y, v in sorted(yr_sr.items()))
            
            print(f"  {label:<28} {sr_full:>8.3f} {sr_train:>9.3f} {sr_oos:>8.3f} {n_trades:>7} {win_rate:>7.1f}% | {yr_str}")
            
            all_results.append({
                "etf": etf, "scheme": scheme_name, "dynamic_ic": use_dyn,
                "label": label, "sr_full": sr_full, "sr_train": sr_train,
                "sr_oos": sr_oos, "n_trades": n_trades, "win_rate": win_rate,
                "yearly": yr_sr,
            })
    
    # Summary: which component matters?
    print(f"\n{'=' * 90}")
    print("SUMMARY: Dynamic IC Contribution (SR difference: dynamic - static)")
    print(f"{'=' * 90}")
    for etf in ETFS:
        for base_scheme in ("score", "rank"):
            static = next((r for r in all_results if r["etf"] == etf and r["scheme"] == base_scheme and not r["dynamic_ic"]), None)
            dynamic = next((r for r in all_results if r["etf"] == etf and r["scheme"] == base_scheme and r["dynamic_ic"]), None)
            if static and dynamic:
                delta_train = dynamic["sr_train"] - static["sr_train"]
                delta_oos = dynamic["sr_oos"] - static["sr_oos"]
                verdict = "HELPS" if delta_train > 0.05 else ("HURTS" if delta_train < -0.05 else "NEUTRAL")
                print(f"  {etf} {base_scheme:>5}: Train Δ={delta_train:+.3f}, OOS Δ={delta_oos:+.3f} → {verdict}")
    
    print(f"\n{'=' * 90}")
    print("SUMMARY: Best scheme per ETF (by TRAIN Sharpe — no OOS peeking)")
    print(f"{'=' * 90}")
    for etf in ETFS:
        etf_results = [r for r in all_results if r["etf"] == etf]
        if not etf_results:
            continue
        best = max(etf_results, key=lambda r: r["sr_train"])
        print(f"  {etf}: {best['label']} → Train SR={best['sr_train']:.3f}, OOS SR={best['sr_oos']:.3f}")
    
    # Consistency check: how many years positive?
    print(f"\n{'=' * 90}")
    print("CONSISTENCY: Years with positive Sharpe (out of total)")
    print(f"{'=' * 90}")
    for etf in ETFS:
        etf_results = [r for r in all_results if r["etf"] == etf]
        if not etf_results:
            continue
        print(f"  {etf}:")
        for r in sorted(etf_results, key=lambda x: -x["sr_train"]):
            yrs = r["yearly"]
            pos_yrs = sum(1 for v in yrs.values() if v > 0)
            total_yrs = len(yrs)
            neg_yrs_str = ", ".join(f"{y}" for y, v in sorted(yrs.items()) if v <= 0)
            print(f"    {r['label']:<28}: {pos_yrs}/{total_yrs} positive | bad years: {neg_yrs_str or 'none'}")


if __name__ == "__main__":
    run_diagnostic()
