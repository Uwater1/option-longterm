#!/usr/bin/env python3
"""
Utils module for NewTrade framework.
Handles:
1. Loading admitted feature pools from admitted_pools.py.
2. Loading ETF feature datasets.
3. Dynamically computing recipe features.
4. Strict zero-lookahead expanding window z-score standardization.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# Append paths to import day-model-new and day-model modules
sys.path.append(str(REPO_ROOT / "day-model-new"))
sys.path.append(str(REPO_ROOT / "day-model-new" / "mining"))
sys.path.append(str(REPO_ROOT / "day-model"))

from admitted_pools import POOLS
from recipe_utils import compute_recipe
from build_features import FEATURES


def load_admitted_pool(etf: str, side: str = "single", min_features: int = 10) -> list:
    """
    Load admitted feature pool for given ETF and side.
    Enforces feature count floor (min_features).
    """
    etf_pools = POOLS.get(etf, {})
    pool = etf_pools.get(side, [])
    
    if len(pool) < min_features:
        print(f"[GUARDRAIL WARNING] {etf} ({side}) has only {len(pool)} features (< {min_features} minimum). Skipping execution.")
        return []
    
    return pool


def load_etf_dataset(etf: str) -> pd.DataFrame:
    """
    Load raw ETF features dataset from day-model/data/features_{etf}.parquet.
    """
    path = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    
    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    # Fill base features defensively using forward fill + median fill
    base_med = df[FEATURES].median().fillna(0.0)
    df[FEATURES] = df[FEATURES].ffill().fillna(base_med)
    
    return df


def build_pool_feature_matrix(df: pd.DataFrame, pool: list) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Compute feature columns for all items in admitted pool.
    Returns:
      - X_raw: np.ndarray shape (T, N)
      - signs: np.ndarray shape (N,)
      - feature_names: list of feature names
    """
    if not pool:
        return np.empty((len(df), 0)), np.empty(0), []

    # Pre-calculate training statistics for recipe features if needed
    # We use expanding or global training statistics defensively
    train_end = pd.Timestamp("2022-01-01") if "588000" not in str(df) else pd.Timestamp("2025-01-01")
    train_mask = df["date"] < train_end
    train_df = df[train_mask] if train_mask.sum() > 252 else df.iloc[:500]

    train_means = {}
    train_stds = {}
    train_medians = {}
    
    for item in pool:
        if "recipe" in item:
            r = item["recipe"]
            for key in ["feature_a", "feature_b", "feature_c", "feature_cond", "feature_cond2"]:
                if key in r:
                    col = r[key]
                    if col not in train_means and col in df.columns:
                        train_means[col] = train_df[col].mean()
                        train_stds[col] = train_df[col].std()
                        train_medians[col] = train_df[col].median()

    X_raw_list = []
    feature_names = []
    signs_list = []

    for item in pool:
        feat_name = item["feature_name"]
        sign = item.get("sign", 1)
        
        if "recipe" in item:
            val = compute_recipe(df, item["recipe"], train_means, train_stds, train_medians)
        elif feat_name in df.columns:
            val = df[feat_name].values.astype(np.float64)
        else:
            print(f"[WARNING] Feature {feat_name} not found in dataset. Filling with zeros.")
            val = np.zeros(len(df), dtype=np.float64)

        X_raw_list.append(val)
        feature_names.append(feat_name)
        signs_list.append(sign)

    X_raw = np.column_stack(X_raw_list) if X_raw_list else np.empty((len(df), 0))
    signs = np.array(signs_list, dtype=np.float64)
    
    return X_raw, signs, feature_names


@njit(cache=True)
def expanding_zscore_numba(X: np.ndarray, burn_in: int = 252, clip: float = 3.0) -> np.ndarray:
    """
    Strict zero-lookahead expanding z-score standardizer.
    For day t, mean and std are computed over [0, t-1].
    Values before burn_in are set to 0.0.
    Clips output to [-clip, clip].
    """
    T, N = X.shape
    Z = np.zeros((T, N), dtype=np.float64)
    
    if T < burn_in or N == 0:
        return Z

    # Running sums for fast O(1) mean/variance update
    sum_x = np.zeros(N, dtype=np.float64)
    sum_sq = np.zeros(N, dtype=np.float64)

    # Initialize burn_in period
    for t in range(burn_in):
        for j in range(N):
            val = X[t, j]
            sum_x[j] += val
            sum_sq[j] += val * val

    # Expanding window calculation for t >= burn_in
    for t in range(burn_in, T):
        n_count = float(t)
        for j in range(N):
            mean = sum_x[j] / n_count
            var = (sum_sq[j] / n_count) - (mean * mean)
            std = np.sqrt(var) if var > 1e-12 else 1.0
            
            # Standardize x_t using stats up to t-1
            z_val = (X[t, j] - mean) / std
            
            # Clip
            if z_val > clip:
                z_val = clip
            elif z_val < -clip:
                z_val = -clip
                
            Z[t, j] = z_val

            # Update running sums with current point X[t, j] for future steps
            val = X[t, j]
            sum_x[j] += val
            sum_sq[j] += val * val

    return Z
