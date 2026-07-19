#!/usr/bin/env python3
"""
Stage B Evaluation for Day-Model Rewrite v3.
Implements:
1. Loading selected pool from Stage A.
2. VIF safety net pass (B2).
3. IC-weighted linear sum model (B1).
4. Out-of-sample (OOS) evaluation on:
   - Holdout OOS (2022-01-01 to present)
   - Lockbox (2024-03-01 to present)
5. Block-bootstrap CI reporting for overall IC, tail IC, decile monotonicity, and simulated trading metrics.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata

# Set up paths to import from day-model
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from build_features import FEATURES

# Date ranges will be set dynamically based on ETF

def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson over ranks. Faster than scipy.stats.spearmanr."""
    if a.shape[0] < 5:
        return 0.0
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)

def compute_decile_monotonicity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate the Spearman rank correlation of decile means."""
    n = len(y_true)
    if n < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    order = np.argsort(y_pred, kind="quicksort")
    yt_sorted = y_true[order]
    chunks = np.array_split(yt_sorted, 10)
    means = np.array([c.mean() if c.size else np.nan for c in chunks])
    valid = ~np.isnan(means)
    if valid.sum() < 3:
        return 0.0
    m = means[valid]
    r = rankdata(m)
    k = m.shape[0]
    a = np.arange(1, k + 1, dtype=np.float64)
    a -= a.mean()
    r -= r.mean()
    denom = np.sqrt((a * a).sum() * (r * r).sum())
    if denom < 1e-12:
        return 0.0
    return float((a * r).sum() / denom)

def compute_side_tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str) -> float:
    """Side-aware Tail IC computation matching v2 config."""
    n = len(y_pred)
    if side in ["long", "short"]:
        pct = 0.15
    else:  # single (two-sided)
        pct = 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0
        
    order = np.argsort(y_pred, kind="quicksort")
    if side == "long":
        idx = order[-n_tail:]
    elif side == "short":
        idx = order[:n_tail]
    else:  # two-sided
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
        
    return _spearman_from_arrays(y_true[idx], y_pred[idx])

def _spearman_rows(y_true_matrix: np.ndarray, y_pred_matrix: np.ndarray) -> np.ndarray:
    """Compute Spearman correlation for multiple rows in parallel."""
    B, n = y_true_matrix.shape
    out = np.zeros(B)
    for b in range(B):
        out[b] = _spearman_from_arrays(y_true_matrix[b], y_pred_matrix[b])
    return out

def _decile_mono_rows(y_true_matrix: np.ndarray, y_pred_matrix: np.ndarray) -> np.ndarray:
    """Compute decile monotonicity for multiple rows in parallel."""
    B, n = y_true_matrix.shape
    out = np.zeros(B)
    for b in range(B):
        out[b] = compute_decile_monotonicity(y_true_matrix[b], y_pred_matrix[b])
    return out

def block_bootstrap_ci(y_true: np.ndarray, y_pred: np.ndarray, side: str, block_size=10, n_bootstraps=1000):
    """Vectorized block-bootstrap CIs for Spearman IC, Tail IC, and decile monotonicity."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    n = len(y_true)
    if n < block_size:
        block_size = max(1, n // 5)
        
    np.random.seed(42)
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = n - block_size + 1
    
    if possible_starts <= 0:
        idx = np.random.choice(n, size=(n_bootstraps, n), replace=True)
    else:
        starts = np.random.choice(possible_starts, size=(n_bootstraps, num_blocks), replace=True)
        offsets = np.arange(block_size)
        idx = (starts[:, :, None] + offsets[None, None, :]).reshape(n_bootstraps, -1)[:, :n]
        
    y_b = y_true[idx]
    p_b = y_pred[idx]
    
    boot_overall_ics = _spearman_rows(y_b, p_b)
    boot_monos = _decile_mono_rows(y_b, p_b)
    
    boot_tail_ics = np.zeros(n_bootstraps)
    for b in range(n_bootstraps):
        boot_tail_ics[b] = compute_side_tail_ic(y_b[b], p_b[b], side)
        
    ci_overall = (float(np.percentile(boot_overall_ics, 2.5)), float(np.percentile(boot_overall_ics, 97.5)))
    ci_tail = (float(np.percentile(boot_tail_ics, 2.5)), float(np.percentile(boot_tail_ics, 97.5)))
    ci_mono = (float(np.percentile(boot_monos, 2.5)), float(np.percentile(boot_monos, 97.5)))
    
    return ci_overall, ci_tail, ci_mono

def compute_vif(X: np.ndarray) -> np.ndarray:
    """Calculate Variance Inflation Factor (VIF) for design matrix columns."""
    n_features = X.shape[1]
    vifs = np.zeros(n_features)
    for i in range(n_features):
        y_col = X[:, i]
        X_other = np.delete(X, i, axis=1)
        # Solve OLS: X_other * w = y_col
        # Add intercept
        X_other_int = np.column_stack([np.ones(len(X_other)), X_other])
        try:
            w, _, _, _ = np.linalg.lstsq(X_other_int, y_col, rcond=None)
            y_pred = X_other_int @ w
            r2 = 1.0 - np.sum((y_col - y_pred)**2) / (np.sum((y_col - y_col.mean())**2) + 1e-10)
            vifs[i] = 1.0 / (1.0 - r2 + 1e-10)
        except Exception:
            vifs[i] = 999.0
    return vifs

def simulate_returns(y_true: np.ndarray, y_pred: np.ndarray, side: str):
    """Simulate strategy daily returns based on tail signals."""
    n = len(y_pred)
    if n < 10:
        return 0.0, 0.0, 0.0, 0.0
        
    if np.max(y_pred) - np.min(y_pred) < 1e-12:
        return 0.0, 0.0, 0.0, 0.0
        
    order = np.argsort(y_pred, kind="quicksort")
    strat_returns = np.zeros(n)
    
    if side == "long":
        pct = 0.15
        n_tail = max(5, int(n * pct))
        long_idx = order[-n_tail:]
        strat_returns[long_idx] = y_true[long_idx]
    elif side == "short":
        pct = 0.15
        n_tail = max(5, int(n * pct))
        short_idx = order[:n_tail]
        strat_returns[short_idx] = -y_true[short_idx]
    else:  # single (two-sided)
        pct = 0.10
        n_tail = max(5, int(n * pct))
        long_idx = order[-n_tail:]
        short_idx = order[:n_tail]
        strat_returns[long_idx] = y_true[long_idx]
        strat_returns[short_idx] = -y_true[short_idx]
        
    # Transaction cost = 15 bps (0.0015) per active day
    active_days = np.abs(strat_returns) > 1e-12
    strat_returns[active_days] -= 0.0015
    
    ann_return = float(np.mean(strat_returns) * 244)
    ann_vol = float(np.std(strat_returns) * np.sqrt(244))
    
    # Sharpe
    sharpe = ann_return / (ann_vol + 1e-10)
    
    # Sortino
    downside_returns = np.minimum(strat_returns, 0.0)
    downside_vol = float(np.std(downside_returns) * np.sqrt(244))
    sortino = ann_return / (downside_vol + 1e-10)
    
    # Max DD
    cum_returns = np.cumsum(strat_returns)
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = running_max - cum_returns
    max_dd = float(np.max(drawdowns))
    
    return ann_return, sharpe, sortino, max_dd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", required=True, choices=["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"])
    parser.add_argument("-s", "--side", required=True, choices=["single", "long", "short"])
    parser.add_argument("-k", type=float, default=1.0, help="Exponent for weighting overall IC")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    args = parser.parse_args()

    # Determine dynamic date ranges
    if args.etf == "588000ETF":
        train_start = pd.Timestamp("2020-11-01")
        train_end = pd.Timestamp("2025-01-01")
        oos_start = pd.Timestamp("2025-01-01")
        lockbox_start = pd.Timestamp("2025-07-01")
    else:
        train_start = pd.Timestamp("2015-01-01")
        train_end = pd.Timestamp("2022-01-01")
        oos_start = pd.Timestamp("2022-01-01")
        lockbox_start = pd.Timestamp("2024-03-01")

    print(f"================================================================================")
    print(f"Stage B Evaluation: ETF={args.etf}, Side={args.side}, Early={args.early}, k={args.k}")
    print(f"================================================================================")

    # 1. Load selected feature pool
    suffix = "_early" if args.early else ""
    data_out_dir = HERE / "data"
    pool_path = data_out_dir / f"selected_pool_{args.etf}_{args.side}{suffix}.json"
    if not pool_path.exists():
        print(f"ERROR: Selected pool file not found at {pool_path}. Run select_features.py first.")
        sys.exit(1)
        
    with open(pool_path, "r") as f:
        selected_pool = json.load(f)
        
    if not selected_pool:
        print(f"WARNING: Selected feature pool is empty. Simple model will produce 0.0 predictions.")
        # Create dummy prediction metrics
        
    # 2. Load dataset
    features_dir = REPO_ROOT / "day-model" / "data"
    fname = f"features_{args.etf}_early.parquet" if args.early else f"features_{args.etf}.parquet"
    path = features_dir / fname
    if not path.exists():
        print(f"ERROR: Dataset not found at {path}")
        sys.exit(1)
        
    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Filter to training and OOS periods
    train_mask = (df["date"] >= train_start) & (df["date"] < train_end)
    train_df = df[train_mask].reset_index(drop=True)
    
    oos_mask = df["date"] >= oos_start
    oos_df = df[oos_mask].reset_index(drop=True)
    
    lockbox_mask = df["date"] >= lockbox_start
    lockbox_df = df[lockbox_mask].reset_index(drop=True)

    # Standardize and prepare feature values based on selection pool
    # Fill base features NaNs defensively across all three datasets using training median
    col_med_train = train_df[FEATURES].median().fillna(0.0)
    for col in FEATURES:
        train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
        oos_df[col] = oos_df[col].ffill().fillna(col_med_train[col])
        lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])

    # Import recipe utils
    import sys
    sys.path.append(str(HERE / "mining"))
    from recipe_utils import compute_recipe

    # Build reference statistics for any base features used in recipes to prevent OOS leakage
    train_means = {}
    train_stds = {}
    train_medians = {}
    for item in selected_pool:
        if "recipe" in item:
            r = item["recipe"]
            for key in ["feature_a", "feature_b", "feature_cond"]:
                if key in r:
                    col = r[key]
                    if col not in train_means:
                        train_means[col] = train_df[col].mean()
                        train_stds[col] = train_df[col].std()
                        train_medians[col] = train_df[col].median()

    # Compute recipe features dynamically for train, OOS, and lockbox
    for item in selected_pool:
        if "recipe" in item:
            feat_name = item["feature_name"]
            recipe = item["recipe"]
            train_df[feat_name] = compute_recipe(train_df, recipe, train_means, train_stds, train_medians)
            oos_df[feat_name] = compute_recipe(oos_df, recipe, train_means, train_stds, train_medians)
            lockbox_df[feat_name] = compute_recipe(lockbox_df, recipe, train_means, train_stds, train_medians)

    all_selected_features = [item["feature_name"] for item in selected_pool]
    
    # Train standardization parameters
    means = {}
    stds = {}
    
    if all_selected_features:
        for feat in all_selected_features:
            means[feat] = train_df[feat].mean()
            stds[feat] = train_df[feat].std()
            if stds[feat] < 1e-12:
                stds[feat] = 1.0

        # Create standardized arrays for train, OOS, and lockbox
        def get_standardized_x(data_df):
            X_std = np.zeros((len(data_df), len(all_selected_features)))
            for i, feat in enumerate(all_selected_features):
                X_std[:, i] = (data_df[feat].values - means[feat]) / stds[feat]
            return X_std

        X_train_std = get_standardized_x(train_df)
        X_oos_std = get_standardized_x(oos_df)
        X_lock_std = get_standardized_x(lockbox_df)

        # Apply sign flips saved in selection pool
        signs = np.array([item["sign"] for item in selected_pool])
        X_train_std = X_train_std * signs
        X_oos_std = X_oos_std * signs
        X_lock_std = X_lock_std * signs

        # B2: VIF safety net pass on final pool (computed over training set)
        print("Computing VIF on final selected features...")
        vifs = compute_vif(X_train_std)
        clean_selected_pool = []
        clean_indices = []
        for i, (feat, vif) in enumerate(zip(selected_pool, vifs)):
            if vif > 12.0:
                print(f"  [SAFETY NET] Dropping collinear feature: {feat['feature_name']} (VIF = {vif:.2f})")
            else:
                clean_selected_pool.append(feat)
                clean_indices.append(i)
                
        selected_pool = clean_selected_pool
        X_train_std = X_train_std[:, clean_indices]
        X_oos_std = X_oos_std[:, clean_indices]
        X_lock_std = X_lock_std[:, clean_indices]

    # Target returns
    y_train = train_df["trade_return"].values.astype(np.float64)
    y_oos = oos_df["trade_return"].values.astype(np.float64)
    y_lock = lockbox_df["trade_return"].values.astype(np.float64)

    # 3. IC-weighted combination predictions (B1)
    if selected_pool:
        weights = np.array([max(0.0, item.get("deflated_ic", 0.0))**args.k for item in selected_pool])
        # Normalize weights so they sum to 1.0 (or just scale predictions)
        if sum(weights) > 1e-12:
            weights = weights / sum(weights)
            
        pred_train = X_train_std @ weights
        pred_oos = X_oos_std @ weights
        pred_lock = X_lock_std @ weights
    else:
        pred_train = np.zeros(len(y_train))
        pred_oos = np.zeros(len(y_oos))
        pred_lock = np.zeros(len(y_lock))

    print(f"\nFinal active pool size: {len(selected_pool)}")
    for item in selected_pool:
        print(f"  - {item['feature_name']}: sign={item['sign']}, overall_ic={item['overall_ic']:.4f}, deflated_ic={item['deflated_ic']:.4f}")

    # 4. Evaluate Performance
    def run_eval(y_true, y_pred, label):
        overall_ic = _spearman_from_arrays(y_true, y_pred)
        tail_ic = compute_side_tail_ic(y_true, y_pred, args.side)
        mono = compute_decile_monotonicity(y_true, y_pred)
        
        ci_overall, ci_tail, ci_mono = block_bootstrap_ci(y_true, y_pred, args.side)
        ann_ret, sharpe, sortino, max_dd = simulate_returns(y_true, y_pred, args.side)
        
        print(f"\n--- {label} Results ---")
        print(f"Overall IC:          {overall_ic:+.4f} (95% CI: [{ci_overall[0]:+.4f}, {ci_overall[1]:+.4f}])")
        print(f"Tail IC:             {tail_ic:+.4f} (95% CI: [{ci_tail[0]:+.4f}, {ci_tail[1]:+.4f}])")
        print(f"Decile Monotonicity: {mono:+.4f} (95% CI: [{ci_mono[0]:+.4f}, {ci_mono[1]:+.4f}])")
        print(f"Simulated Ann. Ret:  {ann_ret * 100:.2f}%")
        print(f"Simulated Sharpe:    {sharpe:.4f}")
        print(f"Simulated Sortino:   {sortino:.4f}")
        print(f"Simulated Max DD:    {max_dd * 100:.2f}%")
        
        return {
            "overall_ic": overall_ic,
            "overall_ic_ci": ci_overall,
            "tail_ic": tail_ic,
            "tail_ic_ci": ci_tail,
            "monotonicity": mono,
            "monotonicity_ci": ci_mono,
            "ann_ret": ann_ret,
            "sharpe": sharpe,
            "sortino": sortino,
            "max_dd": max_dd
        }

    train_results = run_eval(y_train, pred_train, f"Training Period ({train_start.year}-{train_end.year})")
    oos_results = run_eval(y_oos, pred_oos, f"Holdout OOS Period ({oos_start.year}-present)")
    lock_results = run_eval(y_lock, pred_lock, f"OOS Lockbox Period ({lockbox_start.year}-present)")

    # Save results to a report file
    results_path = data_out_dir / f"results_{args.etf}_{args.side}{suffix}.json"
    out_dict = {
        "etf": args.etf,
        "side": args.side,
        "early": args.early,
        "k": args.k,
        "features_selected": [item["feature_name"] for item in selected_pool],
        "training_metrics": train_results,
        "oos_metrics": oos_results,
        "lockbox_metrics": lock_results
    }
    with open(results_path, "w") as f:
        json.dump(out_dict, f, indent=2)
    print(f"\nSaved evaluation metrics to {results_path}")
    print(f"================================================================================")

if __name__ == "__main__":
    main()
