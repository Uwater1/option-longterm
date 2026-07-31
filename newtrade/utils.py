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
from scipy.stats import rankdata

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


# Futures symbol & continuous contract 5m parquet mapping
FUTURES_MAP = {
    "300ETF": "IF88_5m.parquet",
    "500ETF": "IC88_5m.parquet",
    "50ETF": "IH88_5m.parquet",
}

FUTURES_NAME_MAP = {
    "300ETF": "IF88 (CSI 300 Futures)",
    "500ETF": "IC88 (CSI 500 Futures)",
    "50ETF": "IH88 (SSE 50 Futures)",
}


def load_future_trade_returns(etf: str, df_etf: pd.DataFrame) -> tuple[np.ndarray, bool, str]:
    """
    Load intraday trade return (10:00 open -> 14:35 close) for underlying index future.
    Falls back to ETF spot trade_return for historical dates prior to 5m futures data coverage.

    Returns:
      - combined_returns: np.ndarray shape (T,)
      - is_available: bool
      - future_name: str
    """
    if etf not in FUTURES_MAP:
        return None, False, ""

    fut_file = REPO_ROOT / "data" / FUTURES_MAP[etf]
    if not fut_file.exists():
        return None, False, ""

    df_5m = pd.read_parquet(fut_file)
    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
    df_5m["date"] = df_5m["datetime"].dt.date

    fut_returns_dict = {}
    for d, g in df_5m.groupby("date"):
        g = g.sort_values("datetime").reset_index(drop=True)
        if len(g) > 42:
            entry_open = float(g.iloc[6]["open"])
            exit_close = float(g.iloc[42]["close"])
            if entry_open > 0 and exit_close > 0:
                fut_returns_dict[pd.Timestamp(d)] = float(np.log(exit_close / entry_open))

    fut_s = pd.Series(fut_returns_dict, name="future_trade_return")
    merged = df_etf[["date", "trade_return"]].set_index("date").join(fut_s)

    # Fallback to ETF spot trade_return for dates without 5m futures data
    combined = merged["future_trade_return"].fillna(merged["trade_return"]).values.astype(np.float64)
    fut_name = FUTURES_NAME_MAP.get(etf, FUTURES_MAP[etf])

    return combined, True, fut_name


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


def load_cluster_assignments(etf: str, side: str = "single", suffix: str = "") -> dict | None:
    """
    Load ONC cluster assignments for group-constrained feature selection.

    Returns:
        dict mapping {feature_name: cluster_id} or None if file not found.
    """
    import json
    cluster_path = REPO_ROOT / "day-model-new" / "data" / f"cluster_assignments_{etf}_{side}{suffix}.json"
    if not cluster_path.exists():
        return None

    with open(cluster_path, "r") as f:
        data = json.load(f)

    # Convert {cluster_id: [feature_names]} to {feature_name: cluster_id}
    feature_to_cluster = {}
    for cluster_id, members in data.get("clusters", {}).items():
        cid = int(cluster_id)
        for feat_name in members:
            feature_to_cluster[feat_name] = cid

    return feature_to_cluster


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


@njit(cache=True)
def expanding_factor_ic_numba(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray, burn_in: int = 252) -> np.ndarray:
    """
    Compute expanding zero-lookahead IC (correlation) for each factor over time.
    Returns IC_matrix of shape (T, N) where row t contains IC calculated using data up to t-1.
    Uses O(TN) running sum online updates instead of O(T^2 N) re-computation.
    """
    T, N = Z_std.shape
    IC_matrix = np.zeros((T, N), dtype=np.float64)
    if T < burn_in or N == 0:
        return IC_matrix

    # Pre-align signs
    Z_signed = np.zeros((T, N), dtype=np.float64)
    for j in range(N):
        Z_signed[:, j] = Z_std[:, j] * signs[j]

    sum_y = 0.0
    sum_y2 = 0.0
    sum_z = np.zeros(N, dtype=np.float64)
    sum_z2 = np.zeros(N, dtype=np.float64)
    sum_zy = np.zeros(N, dtype=np.float64)

    # Initialize burn_in accumulation
    for t in range(burn_in):
        y_val = trade_returns[t]
        sum_y += y_val
        sum_y2 += y_val * y_val
        for j in range(N):
            z_val = Z_signed[t, j]
            sum_z[j] += z_val
            sum_z2[j] += z_val * z_val
            sum_zy[j] += z_val * y_val

    # Expanding window calculation for t >= burn_in
    for t in range(burn_in, T):
        n_count = float(t)
        mean_y = sum_y / n_count
        var_y = (sum_y2 / n_count) - (mean_y * mean_y)
        std_y = np.sqrt(var_y) if var_y > 1e-12 else 0.0

        if std_y > 1e-12:
            for j in range(N):
                mean_z = sum_z[j] / n_count
                var_z = (sum_z2[j] / n_count) - (mean_z * mean_z)
                std_z = np.sqrt(var_z) if var_z > 1e-12 else 0.0
                if std_z > 1e-12:
                    cov_zy = (sum_zy[j] / n_count) - (mean_z * mean_y)
                    IC_matrix[t, j] = cov_zy / (std_z * std_y)

        # Update running sums with current step t data (for t+1)
        y_val = trade_returns[t]
        sum_y += y_val
        sum_y2 += y_val * y_val
        for j in range(N):
            z_val = Z_signed[t, j]
            sum_z[j] += z_val
            sum_z2[j] += z_val * z_val
            sum_zy[j] += z_val * y_val

    # For burn-in period, fill with first computed IC
    if burn_in < T:
        for t in range(burn_in):
            IC_matrix[t, :] = IC_matrix[burn_in, :]

    return IC_matrix


@njit(cache=True)
def _fast_rankdata_norm(arr: np.ndarray) -> np.ndarray:
    N = len(arr)
    order = np.argsort(arr)
    ranks = np.empty(N, dtype=np.float64)
    for i in range(N):
        ranks[order[i]] = (i + 1.0) / float(N)
    return ranks


@njit(cache=True)
def expanding_factor_score_numba(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray, burn_in: int = 252,
                                 score_weights: tuple = (0.20, 0.15, 0.65), mode: str = "fixed", mono_window: int = 750) -> np.ndarray:
    """
    Compute zero-lookahead expanding multi-metric factor score (IC + IC_IR + Monotonicity) over time.
    Supports rolling mono_window (default 750 trading days ~ 3 years, 0 for lifetime expanding).
    Returns Score_matrix of shape (T, N) where row t contains score calculated using data up to t-1.
    """
    T, N = Z_std.shape
    Score_matrix = np.zeros((T, N), dtype=np.float64)
    if T < burn_in or N == 0:
        return Score_matrix

    Z_signed = Z_std * signs
    daily_ic = np.zeros((T, N), dtype=np.float64)
    for t in range(T):
        r_t = trade_returns[t]
        daily_ic[t] = Z_signed[t] * r_t

    cum_ic = np.zeros((T, N), dtype=np.float64)
    cum_sq_ic = np.zeros((T, N), dtype=np.float64)
    cum_pos_ic = np.zeros((T, N), dtype=np.float64)

    for j in range(N):
        c_p = 0.0
        c_sq = 0.0
        c_pos = 0.0
        for t in range(T):
            dp = daily_ic[t, j]
            c_p += dp
            c_sq += dp * dp
            if dp > 0:
                c_pos += 1.0
            cum_ic[t, j] = c_p
            cum_sq_ic[t, j] = c_sq
            cum_pos_ic[t, j] = c_pos

    w_ic, w_ir, w_mono = score_weights

    for t in range(burn_in, T):
        n_samples = float(t)
        mean_ic = cum_ic[t-1] / n_samples
        var_ic = (cum_sq_ic[t-1] / n_samples) - mean_ic**2
        std_ic = np.sqrt(np.maximum(1e-12, var_ic))
        ic_ir = mean_ic / std_ic

        if mono_window > 0 and t > mono_window:
            start_idx = t - mono_window
            n_win = float(mono_window)
            mono = (cum_pos_ic[t-1] - cum_pos_ic[start_idx-1]) / n_win
        else:
            mono = cum_pos_ic[t-1] / n_samples

        r_ic = _fast_rankdata_norm(mean_ic)
        r_ir = _fast_rankdata_norm(ic_ir)
        r_mono = _fast_rankdata_norm(mono)

        Score_matrix[t] = w_ic * r_ic + w_ir * r_ir + w_mono * r_mono

    if burn_in < T:
        for t in range(burn_in):
            Score_matrix[t, :] = Score_matrix[burn_in, :]

    return Score_matrix


