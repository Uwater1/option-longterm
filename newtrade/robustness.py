#!/usr/bin/env python3
"""
Robustness Module for NewTrade framework.
Addresses multiple-testing overfit concerns (Bailey & López de Prado):

1. DSR  — Deflated Sharpe Ratio: corrects for N trials, skewness, kurtosis.
2. CPCV — Combinatorial Purged Cross-Validation: distribution of OOS Sharpe.
3. PBO  — Probability of Backtest Overfitting via CPCV.
4. Ensemble — Average of Rank+ICW+Score composite signals (Rapach et al.).
5. Sensitivity Grid — Fee/burn-in/feature-floor stress test.

Usage:
    python newtrade/robustness.py -e 300ETF --all
    python newtrade/robustness.py -e all --dsr --trials 50
    python newtrade/robustness.py -e 500ETF --cpcv --n-splits 6 --n-test 2
    python newtrade/robustness.py -e all --ensemble
    python newtrade/robustness.py -e all --sensitivity
"""

import argparse
import sys
import json
from pathlib import Path
from itertools import combinations
from math import comb, log, sqrt, exp

import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, expanding_factor_ic_numba, expanding_factor_score_numba,
)
from weighting import compute_ew, compute_icw, compute_score_w, compute_rank_w
from strategy import (
    generate_positions, sweep_optimal_threshold, compute_production_threshold,
    simulate_etf_spot, calculate_metrics,
)


# =============================================================================
# 1. DEFLATED SHARPE RATIO (Bailey & López de Prado, 2014)
# =============================================================================

def deflated_sharpe_ratio(observed_sr: float, n_trials: int, n_obs: int,
                          sr_std: float = None, skewness: float = 0.0,
                          kurtosis_excess: float = 3.0) -> dict:
    """
    Compute Deflated Sharpe Ratio.
    
    DSR = Φ( (SR_obs - SR_0) * sqrt(T-1) / sqrt(1 - skew*SR_obs + (kurt-1)/4 * SR_obs^2) )
    
    where SR_0 = E[max(SR)] under null ≈ sqrt(V[SR]) * ((1-γ)*Φ^{-1}(1-1/N) + γ*Φ^{-1}(1-1/(N*e)))
    γ = Euler-Mascheroni ≈ 0.5772
    
    All SR values are per-period (not annualized). We de-annualize internally.
    
    Args:
        observed_sr: Annualized Sharpe ratio observed.
        n_trials: Number of independent strategy configurations tested.
        n_obs: Number of return observations (trading days).
        sr_std: Std of Sharpe estimates across trials (if None, estimated).
        skewness: Skewness of return series.
        kurtosis_excess: Excess kurtosis of return series (normal=0, but we use raw kurtosis internally).
    
    Returns:
        dict with DSR, p-value, expected_max_sr, verdict.
    """
    EULER_MASCHERONI = 0.5772156649
    
    # De-annualize: SR_period = SR_annual / sqrt(252)
    sr_obs = observed_sr / sqrt(252.0)
    
    # Variance of SR estimator (Lo 2002):
    # V[SR] ≈ (1 - skew*SR + (kurt-1)/4 * SR^2) / (T-1)
    # For the expected max, we need the std of SR under null
    kurt_raw = kurtosis_excess + 3.0  # convert excess to raw
    
    # SR standard deviation under null (per-period)
    if sr_std is None:
        sr_var = (1.0 - skewness * sr_obs + ((kurt_raw - 1.0) / 4.0) * sr_obs**2) / max(n_obs - 1, 1)
        sr_std = sqrt(max(sr_var, 1e-12))
    
    # Expected maximum SR under null (Euler-Mascheroni approximation)
    if n_trials <= 1:
        sr_0 = 0.0
    else:
        z1 = norm.ppf(1.0 - 1.0 / n_trials)
        z2 = norm.ppf(1.0 - 1.0 / (n_trials * exp(1.0)))
        sr_0 = sr_std * ((1.0 - EULER_MASCHERONI) * z1 + EULER_MASCHERONI * z2)
    
    # DSR test statistic
    denom_inner = 1.0 - skewness * sr_obs + ((kurt_raw - 1.0) / 4.0) * sr_obs**2
    if denom_inner <= 0:
        denom_inner = 1e-12
    
    test_stat = (sr_obs - sr_0) * sqrt(n_obs - 1) / sqrt(denom_inner)
    dsr = float(norm.cdf(test_stat))
    
    return {
        "observed_sr_annual": round(observed_sr, 4),
        "n_trials": n_trials,
        "n_obs": n_obs,
        "skewness": round(skewness, 4),
        "kurtosis_excess": round(kurtosis_excess, 4),
        "expected_max_sr_annual": round(sr_0 * sqrt(252.0), 4),
        "dsr": round(dsr, 4),
        "dsr_pct": f"{dsr*100:.1f}%",
        "verdict": "SIGNIFICANT" if dsr > 0.95 else ("MARGINAL" if dsr > 0.90 else "NOT_SIGNIFICANT"),
    }


# =============================================================================
# 2. COMBINATORIAL PURGED CROSS-VALIDATION (López de Prado, 2018)
# =============================================================================

def cpcv_splits(n_samples: int, n_splits: int = 6, n_test: int = 2, purge_gap: int = 5):
    """
    Generate Combinatorial Purged Cross-Validation train/test index arrays.
    
    Splits data into n_splits contiguous chunks. For each combination of n_test chunks
    as test set, the remaining chunks form training set. Purge gap removes boundary
    samples from training to prevent information leakage.
    
    Yields:
        (train_indices, test_indices) tuples
    """
    chunk_size = n_samples // n_splits
    chunk_boundaries = [(i * chunk_size, min((i + 1) * chunk_size, n_samples)) for i in range(n_splits)]
    
    for test_chunks in combinations(range(n_splits), n_test):
        test_indices = []
        train_indices = []
        
        for chunk_idx in range(n_splits):
            start, end = chunk_boundaries[chunk_idx]
            indices = list(range(start, end))
            if chunk_idx in test_chunks:
                test_indices.extend(indices)
            else:
                train_indices.extend(indices)
        
        # Purge: remove training samples within purge_gap of any test boundary
        test_set = set(test_indices)
        purged_train = []
        for idx in train_indices:
            # Check if idx is within purge_gap of any test sample
            too_close = False
            for t_start, t_end in [(chunk_boundaries[c][0], chunk_boundaries[c][1]) for c in test_chunks]:
                if abs(idx - t_start) < purge_gap or abs(idx - t_end + 1) < purge_gap:
                    too_close = True
                    break
            if not too_close:
                purged_train.append(idx)
        
        yield np.array(purged_train, dtype=np.int64), np.array(sorted(test_indices), dtype=np.int64)


def run_cpcv_backtest(Z_composite: np.ndarray, trade_returns: np.ndarray, dates: pd.Series,
                      n_splits: int = 6, n_test: int = 2, purge_gap: int = 5,
                      mode: str = "binary", fee_bps: float = 0.0008,
                      z_buffer: float = 0.1, long_only: bool = False) -> dict:
    """
    Run CPCV on a composite signal. For each fold:
      - Train: sweep optimal threshold
      - Test: apply threshold + buffer, compute Sharpe
    
    Returns distribution of OOS Sharpe ratios across all folds.
    """
    n_samples = len(Z_composite)
    fold_sharpes = []
    fold_details = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(cpcv_splits(n_samples, n_splits, n_test, purge_gap)):
        if len(train_idx) < 100 or len(test_idx) < 50:
            continue
        
        Z_train = Z_composite[train_idx]
        ret_train = trade_returns[train_idx]
        Z_test = Z_composite[test_idx]
        ret_test = trade_returns[test_idx]
        
        # Train threshold
        sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=fee_bps, long_only=long_only)
        z_th_long, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer)
        
        # Test
        positions = generate_positions(Z_test, z_th=z_th_long, z_th_short=z_th_short,
                                       mode=mode, long_only=long_only)
        net_ret, raw_ret, fees = simulate_etf_spot(ret_test, positions, fee_bps=fee_bps)
        
        std_net = np.std(net_ret)
        fold_sharpe = float((np.mean(net_ret) / std_net) * sqrt(252)) if std_net > 1e-12 else 0.0
        n_active = int((np.abs(positions) > 1e-5).sum())
        
        fold_sharpes.append(fold_sharpe)
        fold_details.append({
            "fold": fold_idx,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "z_th_long": z_th_long,
            "z_th_short": z_th_short,
            "cost_sharpe": round(fold_sharpe, 4),
            "n_active": n_active,
            "total_pnl": round(float(net_ret.sum()), 4),
        })
    
    arr = np.array(fold_sharpes)
    return {
        "n_folds": len(fold_sharpes),
        "sharpe_mean": round(float(arr.mean()), 4) if len(arr) > 0 else 0.0,
        "sharpe_median": round(float(np.median(arr)), 4) if len(arr) > 0 else 0.0,
        "sharpe_std": round(float(arr.std()), 4) if len(arr) > 0 else 0.0,
        "sharpe_min": round(float(arr.min()), 4) if len(arr) > 0 else 0.0,
        "sharpe_max": round(float(arr.max()), 4) if len(arr) > 0 else 0.0,
        "pct_positive": round(float((arr > 0).mean() * 100), 1) if len(arr) > 0 else 0.0,
        "fold_details": fold_details,
    }


# =============================================================================
# 3. PROBABILITY OF BACKTEST OVERFITTING (PBO)
# =============================================================================

def compute_pbo(Z_composites: dict, trade_returns: np.ndarray,
                n_splits: int = 6, n_test: int = 2, purge_gap: int = 5,
                mode: str = "binary", fee_bps: float = 0.0008,
                z_buffer: float = 0.1, long_only: bool = False) -> dict:
    """
    Compute Probability of Backtest Overfitting across multiple scheme configurations.
    
    PBO = fraction of CPCV folds where the IS-best scheme is below-median OOS.
    
    Args:
        Z_composites: dict of {scheme_name: Z_composite_array}
    """
    n_samples = len(trade_returns)
    scheme_names = list(Z_composites.keys())
    n_schemes = len(scheme_names)
    
    if n_schemes < 2:
        return {"pbo": None, "error": "Need at least 2 schemes for PBO"}
    
    n_overfit = 0
    n_valid_folds = 0
    fold_records = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(cpcv_splits(n_samples, n_splits, n_test, purge_gap)):
        if len(train_idx) < 100 or len(test_idx) < 50:
            continue
        
        ret_train = trade_returns[train_idx]
        ret_test = trade_returns[test_idx]
        
        # For each scheme: train threshold on IS, compute IS and OOS Sharpe
        is_sharpes = {}
        oos_sharpes = {}
        
        for name in scheme_names:
            Z_full = Z_composites[name]
            Z_train = Z_full[train_idx]
            Z_test = Z_full[test_idx]
            
            # IS: sweep threshold, compute IS Sharpe
            sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=fee_bps, long_only=long_only)
            z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=z_buffer)
            
            pos_train = generate_positions(Z_train, z_th=z_th_l, z_th_short=z_th_s, mode=mode, long_only=long_only)
            net_train, _, _ = simulate_etf_spot(ret_train, pos_train, fee_bps=fee_bps)
            std_tr = np.std(net_train)
            is_sharpes[name] = float((np.mean(net_train) / std_tr) * sqrt(252)) if std_tr > 1e-12 else 0.0
            
            # OOS: apply same threshold
            pos_test = generate_positions(Z_test, z_th=z_th_l, z_th_short=z_th_s, mode=mode, long_only=long_only)
            net_test, _, _ = simulate_etf_spot(ret_test, pos_test, fee_bps=fee_bps)
            std_te = np.std(net_test)
            oos_sharpes[name] = float((np.mean(net_test) / std_te) * sqrt(252)) if std_te > 1e-12 else 0.0
        
        # Find IS-best scheme
        is_best = max(is_sharpes, key=is_sharpes.get)
        
        # Check if IS-best is below median OOS
        oos_vals = sorted(oos_sharpes.values())
        oos_median = float(np.median(oos_vals))
        
        if oos_sharpes[is_best] < oos_median:
            n_overfit += 1
        
        n_valid_folds += 1
        fold_records.append({
            "fold": fold_idx,
            "is_best": is_best,
            "is_best_oos_sharpe": round(oos_sharpes[is_best], 4),
            "oos_median": round(oos_median, 4),
            "overfit": oos_sharpes[is_best] < oos_median,
        })
    
    pbo = n_overfit / n_valid_folds if n_valid_folds > 0 else None
    
    return {
        "pbo": round(pbo, 4) if pbo is not None else None,
        "pbo_pct": f"{pbo*100:.1f}%" if pbo is not None else "N/A",
        "n_valid_folds": n_valid_folds,
        "n_overfit_folds": n_overfit,
        "verdict": "LOW_RISK" if (pbo is not None and pbo < 0.30) else ("MODERATE" if (pbo is not None and pbo < 0.50) else "HIGH_RISK"),
        "fold_records": fold_records,
    }


# =============================================================================
# 4. ENSEMBLE SIGNAL (Rapach et al. — simple average beats pick-the-best)
# =============================================================================

def compute_ensemble_composite(Z_composites: dict, weights: dict = None) -> np.ndarray:
    """
    Compute ensemble composite as weighted average of multiple scheme signals.
    Default: equal weight across all provided schemes.
    
    Args:
        Z_composites: dict of {scheme_name: Z_composite_array}
        weights: optional dict of {scheme_name: weight}. If None, equal weight.
    """
    names = list(Z_composites.keys())
    n = len(names)
    if n == 0:
        raise ValueError("No composites provided")
    
    T = len(Z_composites[names[0]])
    
    if weights is None:
        weights = {name: 1.0 / n for name in names}
    
    # Normalize weights
    w_sum = sum(weights.values())
    weights = {k: v / w_sum for k, v in weights.items()}
    
    ensemble = np.zeros(T, dtype=np.float64)
    for name in names:
        ensemble += weights[name] * Z_composites[name]
    
    return ensemble


# =============================================================================
# 5. SENSITIVITY GRID
# =============================================================================

def run_sensitivity_grid(etf: str, side: str = "single", min_features: int = 10,
                         fee_bps_list: list = None, burn_in_list: list = None,
                         start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                         mode: str = "binary", z_buffer: float = 0.1) -> pd.DataFrame:
    """
    Run sensitivity grid across fee levels and burn-in periods.
    Reports Sharpe for each combination to identify robust parameter regions.
    """
    if fee_bps_list is None:
        fee_bps_list = [0.0008, 0.0012, 0.0015, 0.0020]
    if burn_in_list is None:
        burn_in_list = [126, 252, 504]
    
    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        return pd.DataFrame()
    
    df = load_etf_dataset(etf)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date) if end_date else None
    
    rows = []
    for burn_in in burn_in_list:
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
        
        # Compute Rank composite (primary scheme)
        Z_rank = compute_rank_w(Z_std, signs, pool=pool)
        
        for fee_bps in fee_bps_list:
            # Train threshold
            train_mask = df["date"] < t_start
            trade_returns = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values
            
            Z_train = Z_rank[train_mask.values]
            ret_train = trade_returns[train_mask.values]
            
            sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=fee_bps)
            z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=z_buffer)
            
            # OOS evaluation
            oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
            if not oos_mask.any():
                continue
            
            Z_oos = Z_rank[oos_mask.values]
            ret_oos = trade_returns[oos_mask.values]
            
            positions = generate_positions(Z_oos, z_th=z_th_l, z_th_short=z_th_s, mode=mode)
            net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, positions, fee_bps=fee_bps)
            
            std_net = np.std(net_ret)
            cost_sharpe = float((np.mean(net_ret) / std_net) * sqrt(252)) if std_net > 1e-12 else 0.0
            n_active = int((np.abs(positions) > 1e-5).sum())
            total_pnl = float(net_ret.sum())
            
            rows.append({
                "etf": etf,
                "burn_in": burn_in,
                "fee_bps": round(fee_bps * 10000, 1),
                "z_th_long": z_th_l,
                "z_th_short": z_th_s,
                "cost_sharpe": round(cost_sharpe, 4),
                "total_pnl": round(total_pnl, 4),
                "n_trades": n_active,
            })
    
    return pd.DataFrame(rows)


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def build_all_composites(etf: str, side: str = "single", min_features: int = 10,
                         burn_in: int = 252) -> tuple:
    """
    Build all scheme composites for an ETF. Returns (Z_composites_dict, trade_returns, df, pool).
    """
    pool = load_admitted_pool(etf, side=side, min_features=min_features)
    if not pool:
        return {}, None, None, []
    
    df = load_etf_dataset(etf)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    
    # Expanding IC for dynamic schemes
    IC_mat = expanding_factor_ic_numba(Z_std, signs, 
                                        df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values,
                                        burn_in=burn_in)
    
    trade_returns = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values
    
    Z_composites = {
        "ew": compute_ew(Z_std, signs),
        "icw": compute_icw(Z_std, signs, pool=pool),
        "score": compute_score_w(Z_std, signs, pool=pool, expanding_ic=IC_mat),
        "rank": compute_rank_w(Z_std, signs, pool=pool, expanding_ic=IC_mat),
    }
    
    return Z_composites, trade_returns, df, pool


def run_full_robustness(etf: str, side: str = "single", n_trials: int = 50,
                        n_splits: int = 6, n_test: int = 2, purge_gap: int = 5,
                        mode: str = "binary", fee_bps: float = 0.0008,
                        start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                        z_buffer: float = 0.1, run_dsr: bool = True,
                        run_cpcv_flag: bool = True, run_pbo: bool = True,
                        run_ensemble: bool = True, run_sensitivity: bool = True) -> dict:
    """
    Run full robustness suite for one ETF.
    """
    print(f"\n{'='*70}")
    print(f"ROBUSTNESS ANALYSIS: {etf} ({side})")
    print(f"{'='*70}")
    
    results = {"etf": etf, "side": side}
    
    # Build composites
    Z_composites, trade_returns, df, pool = build_all_composites(etf, side=side)
    if not Z_composites:
        results["status"] = "SKIPPED_FEAT_FLOOR"
        print(f"  [SKIP] {etf} insufficient features.")
        return results
    
    results["n_features"] = len(pool)
    results["n_obs"] = len(trade_returns)
    
    t_start = pd.Timestamp(start_date)
    if end_date:
        t_end = pd.Timestamp(end_date)
        oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
    else:
        oos_mask = df["date"] >= t_start
    n_oos = int(oos_mask.sum())
    
    # --- DSR ---
    if run_dsr:
        print(f"\n  [1] DEFLATED SHARPE RATIO (N_trials={n_trials})")
        dsr_results = {}
        for name, Z_comp in Z_composites.items():
            # Compute OOS Sharpe for this scheme
            train_mask = df["date"] < t_start
            Z_train = Z_comp[train_mask.values]
            ret_train = trade_returns[train_mask.values]
            
            sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=fee_bps)
            z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=z_buffer)
            
            Z_oos = Z_comp[oos_mask.values]
            ret_oos = trade_returns[oos_mask.values]
            positions = generate_positions(Z_oos, z_th=z_th_l, z_th_short=z_th_s, mode=mode)
            net_ret, _, _ = simulate_etf_spot(ret_oos, positions, fee_bps=fee_bps)
            
            std_net = np.std(net_ret)
            obs_sr = float((np.mean(net_ret) / std_net) * sqrt(252)) if std_net > 1e-12 else 0.0
            
            sk = float(skew(net_ret))
            kt = float(kurtosis(net_ret))  # excess kurtosis
            
            dsr = deflated_sharpe_ratio(obs_sr, n_trials=n_trials, n_obs=n_oos,
                                         skewness=sk, kurtosis_excess=kt)
            dsr_results[name] = dsr
            print(f"    {name:8s}: SR={obs_sr:.3f} → DSR={dsr['dsr']:.3f} ({dsr['verdict']})")
        
        results["dsr"] = dsr_results
    
    # --- CPCV ---
    if run_cpcv_flag:
        print(f"\n  [2] CPCV (splits={n_splits}, test_chunks={n_test}, purge={purge_gap})")
        cpcv_results = {}
        for name, Z_comp in Z_composites.items():
            cpcv = run_cpcv_backtest(Z_comp, trade_returns, df["date"],
                                      n_splits=n_splits, n_test=n_test, purge_gap=purge_gap,
                                      mode=mode, fee_bps=fee_bps, z_buffer=z_buffer)
            cpcv_results[name] = cpcv
            print(f"    {name:8s}: median_SR={cpcv['sharpe_median']:.3f} ± {cpcv['sharpe_std']:.3f} "
                  f"({cpcv['pct_positive']:.0f}% positive, {cpcv['n_folds']} folds)")
        
        results["cpcv"] = cpcv_results
    
    # --- PBO ---
    if run_pbo:
        print(f"\n  [3] PBO (Probability of Backtest Overfitting)")
        pbo = compute_pbo(Z_composites, trade_returns,
                          n_splits=n_splits, n_test=n_test, purge_gap=purge_gap,
                          mode=mode, fee_bps=fee_bps, z_buffer=z_buffer)
        results["pbo"] = pbo
        print(f"    PBO = {pbo.get('pbo_pct', 'N/A')} → {pbo.get('verdict', 'N/A')}")
    
    # --- ENSEMBLE ---
    if run_ensemble:
        print(f"\n  [4] ENSEMBLE (Equal-weight average of all schemes)")
        Z_ensemble = compute_ensemble_composite(Z_composites)
        
        # OOS evaluation of ensemble
        train_mask = df["date"] < t_start
        Z_ens_train = Z_ensemble[train_mask.values]
        ret_train = trade_returns[train_mask.values]
        
        sweep_info = sweep_optimal_threshold(Z_ens_train, ret_train, mode=mode, fee_bps=fee_bps)
        z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=z_buffer)
        
        Z_ens_oos = Z_ensemble[oos_mask.values]
        ret_oos = trade_returns[oos_mask.values]
        positions = generate_positions(Z_ens_oos, z_th=z_th_l, z_th_short=z_th_s, mode=mode)
        net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, positions, fee_bps=fee_bps)
        
        df_oos = df[oos_mask].reset_index(drop=True)
        ens_metrics = calculate_metrics(net_ret, raw_ret, positions, dates=df_oos["date"])
        ens_metrics["z_th_long"] = z_th_l
        ens_metrics["z_th_short"] = z_th_s
        
        # DSR for ensemble
        std_net = np.std(net_ret)
        obs_sr = float((np.mean(net_ret) / std_net) * sqrt(252)) if std_net > 1e-12 else 0.0
        sk = float(skew(net_ret))
        kt = float(kurtosis(net_ret))
        ens_dsr = deflated_sharpe_ratio(obs_sr, n_trials=n_trials, n_obs=n_oos,
                                         skewness=sk, kurtosis_excess=kt)
        
        results["ensemble"] = {
            "metrics": ens_metrics,
            "dsr": ens_dsr,
        }
        print(f"    Ensemble OOS: SR={obs_sr:.3f}, PnL={ens_metrics['total_pnl']:+.4f}, "
              f"WR={ens_metrics['win_rate_pct']:.1f}%, DSR={ens_dsr['dsr']:.3f} ({ens_dsr['verdict']})")
        
        # CPCV for ensemble
        cpcv_ens = run_cpcv_backtest(Z_ensemble, trade_returns, df["date"],
                                      n_splits=n_splits, n_test=n_test, purge_gap=purge_gap,
                                      mode=mode, fee_bps=fee_bps, z_buffer=z_buffer)
        results["ensemble"]["cpcv"] = cpcv_ens
        print(f"    Ensemble CPCV: median_SR={cpcv_ens['sharpe_median']:.3f} ± {cpcv_ens['sharpe_std']:.3f} "
              f"({cpcv_ens['pct_positive']:.0f}% positive)")
    
    # --- SENSITIVITY ---
    if run_sensitivity:
        print(f"\n  [5] SENSITIVITY GRID (fee × burn-in)")
        sens_df = run_sensitivity_grid(etf, side=side, min_features=len(pool),
                                        start_date=start_date, end_date=end_date,
                                        mode=mode, z_buffer=z_buffer)
        if not sens_df.empty:
            results["sensitivity"] = sens_df.to_dict("records")
            print(f"    {'Fee(bps)':>10s} {'BurnIn':>8s} {'Sharpe':>8s} {'PnL':>10s} {'Trades':>7s}")
            for _, row in sens_df.iterrows():
                print(f"    {row['fee_bps']:>10.1f} {row['burn_in']:>8d} {row['cost_sharpe']:>8.3f} "
                      f"{row['total_pnl']:>+10.4f} {row['n_trades']:>7d}")
            
            # Robustness verdict
            sharpes = sens_df["cost_sharpe"].values
            pct_positive = (sharpes > 0).mean() * 100
            min_sharpe = sharpes.min()
            print(f"    → {pct_positive:.0f}% configs positive, min Sharpe = {min_sharpe:.3f}")
            results["sensitivity_summary"] = {
                "pct_positive": round(pct_positive, 1),
                "min_sharpe": round(float(min_sharpe), 4),
                "max_sharpe": round(float(sharpes.max()), 4),
                "mean_sharpe": round(float(sharpes.mean()), 4),
            }
    
    results["status"] = "SUCCESS"
    return results


def main():
    parser = argparse.ArgumentParser(description="NewTrade Robustness Analysis (DSR/CPCV/PBO/Ensemble/Sensitivity)")
    parser.add_argument("-e", "--etf", type=str, default="all",
                        help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("-s", "--side", type=str, default="single", choices=["single", "long", "short"])
    parser.add_argument("--trials", type=int, default=50,
                        help="Number of trials for DSR correction (default: 50)")
    parser.add_argument("--n-splits", type=int, default=6, help="CPCV number of splits (default: 6)")
    parser.add_argument("--n-test", type=int, default=2, help="CPCV test chunks per fold (default: 2)")
    parser.add_argument("--purge-gap", type=int, default=5, help="CPCV purge gap in days (default: 5)")
    parser.add_argument("--mode", type=str, default="binary", choices=["binary", "tanh", "quadratic"])
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Base fee in bps (default: 8)")
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("--z-buffer", type=float, default=0.1)
    
    # Select which analyses to run
    parser.add_argument("--all", action="store_true", help="Run all analyses")
    parser.add_argument("--dsr", action="store_true", help="Run DSR only")
    parser.add_argument("--cpcv", action="store_true", help="Run CPCV only")
    parser.add_argument("--pbo", action="store_true", help="Run PBO only")
    parser.add_argument("--ensemble", action="store_true", help="Run ensemble only")
    parser.add_argument("--sensitivity", action="store_true", help="Run sensitivity grid only")
    
    args = parser.parse_args()
    
    # Determine which analyses to run
    if args.all or not any([args.dsr, args.cpcv, args.pbo, args.ensemble, args.sensitivity]):
        run_dsr = run_cpcv = run_pbo = run_ensemble = run_sensitivity = True
    else:
        run_dsr = args.dsr
        run_cpcv = args.cpcv
        run_pbo = args.pbo
        run_ensemble = args.ensemble
        run_sensitivity = args.sensitivity
    
    # ETF list
    ALL_ETFS = ["300ETF", "500ETF", "50ETF", "159915ETF"]
    etfs = ALL_ETFS if args.etf == "all" else [args.etf]
    
    fee_bps = args.fee_bps / 10000.0  # convert from bps to decimal
    
    all_results = []
    for etf in etfs:
        result = run_full_robustness(
            etf, side=args.side, n_trials=args.trials,
            n_splits=args.n_splits, n_test=args.n_test, purge_gap=args.purge_gap,
            mode=args.mode, fee_bps=fee_bps,
            start_date=args.start_date, end_date=args.end_date,
            z_buffer=args.z_buffer,
            run_dsr=run_dsr, run_cpcv_flag=run_cpcv, run_pbo=run_pbo,
            run_ensemble=run_ensemble, run_sensitivity=run_sensitivity,
        )
        all_results.append(result)
    
    # Save results
    artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    # JSON summary (strip non-serializable)
    json_results = []
    for r in all_results:
        jr = {k: v for k, v in r.items() if k != "sensitivity"}
        if "sensitivity" in r:
            jr["sensitivity"] = r["sensitivity"]
        json_results.append(jr)
    
    out_path = artifacts_dir / "robustness_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"\nSaved results to {out_path}")
    
    # Final summary
    print(f"\n{'='*70}")
    print("FINAL ROBUSTNESS VERDICT")
    print(f"{'='*70}")
    for r in all_results:
        if r.get("status") != "SUCCESS":
            print(f"  {r['etf']}: SKIPPED ({r.get('status', 'unknown')})")
            continue
        
        etf = r["etf"]
        # DSR verdict
        if "dsr" in r:
            best_scheme = max(r["dsr"].items(), key=lambda x: x[1]["dsr"])
            print(f"  {etf} DSR: best={best_scheme[0]} DSR={best_scheme[1]['dsr']:.3f} ({best_scheme[1]['verdict']})")
        
        # CPCV verdict
        if "cpcv" in r:
            best_cpcv = max(r["cpcv"].items(), key=lambda x: x[1]["sharpe_median"])
            print(f"  {etf} CPCV: best={best_cpcv[0]} median_SR={best_cpcv[1]['sharpe_median']:.3f} "
                  f"({best_cpcv[1]['pct_positive']:.0f}% positive)")
        
        # PBO verdict
        if "pbo" in r and r["pbo"].get("pbo") is not None:
            print(f"  {etf} PBO: {r['pbo']['pbo_pct']} ({r['pbo']['verdict']})")
        
        # Ensemble verdict
        if "ensemble" in r:
            ens = r["ensemble"]
            print(f"  {etf} ENSEMBLE: SR={ens['metrics']['cost_sharpe']:.3f}, "
                  f"DSR={ens['dsr']['dsr']:.3f} ({ens['dsr']['verdict']}), "
                  f"CPCV_median={ens['cpcv']['sharpe_median']:.3f}")
        
        # Sensitivity verdict
        if "sensitivity_summary" in r:
            ss = r["sensitivity_summary"]
            print(f"  {etf} SENSITIVITY: {ss['pct_positive']:.0f}% positive, "
                  f"range=[{ss['min_sharpe']:.3f}, {ss['max_sharpe']:.3f}]")
        
        print()


if __name__ == "__main__":
    main()
