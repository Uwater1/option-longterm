"""
Phase 2 Remake: Train Optuna-tuned return prediction model based on first principles.
Implements the 7-step optimization and robust selection plan from day-model_plan.md.

Performance notes
-----------------
- Data downcasted to float32 throughout to speed up BLAS-bound linear algebra.
- Feature selection (screen + stability), LOYO folds, and pilot calibration
  (medians/MADs) are disk-cached in `data/cache_*.joblib`, keyed by
  (etf, len(FEATURES), parquet mtime, B, pi, pilot seed, pilot trials).
  See "Cache invalidation" in AGENTS.md.
- Spearman screening is vectorized (single matmul over ranks).
- Stability-selection bootstrap (B=100) runs in parallel via joblib.
- Optuna studies parallelize across all cores; BLAS threads pinned to 1
  per worker to avoid oversubscription.
"""
import argparse
import hashlib
import json
import os
import time
import warnings
from pathlib import Path

# Pin BLAS threads BEFORE importing numpy/sklearn/skglm so Optuna workers
# (which fork process-parallel) do not oversubscribe the CPU.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
# Suppress sklearn/skglm ConvergenceWarnings in worker subprocesses too.
os.environ.setdefault("PYTHONWARNINGS", "ignore")

import warnings
# Suppress sklearn/skglm ConvergenceWarnings flooding stderr (these are benign
# for L1/MCP path fits that hit iteration caps).
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=Warning)
from sklearn.exceptions import ConvergenceWarning as _SklearnConvergenceWarning
warnings.filterwarnings("ignore", category=_SklearnConvergenceWarning)

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import rankdata
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso, ElasticNet, HuberRegressor, enet_path
import optuna
from optuna.storages import JournalStorage
from optuna.storages.journal import JournalFileBackend
import joblib
from joblib import Parallel, delayed

# skglm imports
from skglm import GeneralizedLinearEstimator
from skglm.datafits import Huber as SkglmHuber
from skglm.penalties import L1 as SkglmL1, MCPenalty
from skglm.solvers import AndersonCD

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Pin seeds globally for reproducibility
import random
random.seed(42)
np.random.seed(42)

LOCKBOX_DATE = "2024-03-01"
VAL_BLOCKS = [
    ("2016-10-01", "2017-01-01"),
    ("2018-07-01", "2018-10-01"),
    ("2020-04-01", "2020-07-01"),
    ("2021-07-01", "2021-10-01"),
    ("2022-10-01", "2023-01-01"),
    ("2023-07-01", "2023-10-01"),
]
PILOT_N_TRIALS = 50
PILOT_SEED = 42
STABILITY_B = 100
STABILITY_PI = 0.60
STABILITY_Q = 35
SCREEN_FDR = 0.40
SCREEN_FALLBACK_K = 50 # Doublc Research this 
ACTIVE_FEATURE_ESS_DIVISOR = 25.0

# Sample-weighting scale_data_with_weights can be done without a full rescale
# of the standardized X (sqrt(w) is row-wise); we precompute the unweighted
# standardized matrix once and apply sqrt(w) per trial.
N_JOBS_DEFAULT = max(1, (os.cpu_count() or 4))
OPTUNA_N_JOBS = N_JOBS_DEFAULT
BOOTSTRAP_N_JOBS = N_JOBS_DEFAULT

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
CACHE_DIR = HERE / "data"  # cache_* files live next to feature parquets
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Caching helpers
# ============================================================
def _cache_key(parts) -> str:
    """Stable short hash key for cache file naming."""
    blob = json.dumps(parts, default=str, sort_keys=True).encode("utf-8")
    return hashlib.md5(blob).hexdigest()[:16]


def _load_or_compute(path: Path, expected_key, compute_fn, use_cache: bool = True, verbose: bool = True):
    """Disk cache: stores (key, payload). Returns payload.

    On key mismatch (or missing file / cache disabled), recomputes via
    `compute_fn()` and writes back. `expected_key` must be a JSON-serializable
    tuple/list; compared by equality.
    """
    if use_cache and path.exists():
        try:
            blob = joblib.load(path)
            if blob.get("key") == expected_key:
                if verbose:
                    print(f"  [cache] hit   {path.name}")
                return blob["payload"]
            if verbose:
                print(f"  [cache] stale {path.name} (key mismatch) -> recompute")
        except Exception as e:
            if verbose:
                print(f"  [cache] read error {path.name}: {e} -> recompute")
    payload = compute_fn()
    if use_cache:
        try:
            joblib.dump({"key": expected_key, "payload": payload}, path, compress=3)
            if verbose:
                print(f"  [cache] write {path.name}")
        except Exception as e:
            if verbose:
                print(f"  [cache] write error {path.name}: {e}")
    return payload


def _to_f32(arr: np.ndarray) -> np.ndarray:
    """Downcast to float32 + ensure C-contiguous for BLAS-friendly matmul."""
    if arr.dtype != np.float32:
        arr = arr.astype(np.float32)
    return np.ascontiguousarray(arr)

# Feature list mapping
import sys
sys.path.append(str(HERE))
from build_features import FEATURES
TARGET = "trade_return"

ETF_CLI_MAP = {
    "300": "300ETF", "50": "50ETF", "500": "500ETF",
    "588000": "588000ETF", "159915": "159915ETF",
    "300ETF": "300ETF", "50ETF": "50ETF", "500ETF": "500ETF",
    "588000ETF": "588000ETF", "159915ETF": "159915ETF",
    "all": ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"],
}

# Metric Weights (w_i from Step 4.1)
METRIC_WEIGHTS = {
    "m1": 0.25,  # Yearly Tail IC IR
    "m2": 0.25,  # Yearly Tail IC Mean
    "m3": 0.15,  # Yearly Hit Rate
    "m4": 0.15,  # Overall Rank IC
    "m5": 0.15,  # Decile Monotonicity
    "m6": 0.05,  # Top-Bottom Spread
    "m7": 0.00,  # Feature Parsimony
    "m8": 0.00,  # Coefficient Bloat
}


# ============================================================
# Shared Penalties & Model Factory
# ============================================================
sys.path.append(str(HERE.parent))
from penalties import MCP_plus_L2


def _build_model(model_type: str, params: dict):
    solver = AndersonCD(max_epochs=2000, tol=1e-3)
    if model_type == "skglm_huber_l1":
        # Use ElasticNet (L1 + L2) with l1_ratio = 0.9 for L2 regularization
        from skglm.penalties import L1_plus_L2
        return GeneralizedLinearEstimator(
            datafit=SkglmHuber(delta=params.get("skglm_huber_delta", 1.35)),
            penalty=L1_plus_L2(alpha=params["skglm_huber_l1_alpha"], l1_ratio=0.9),
            solver=solver,
        )
    elif model_type == "skglm_mcp":
        # Use custom MCP_plus_L2 penalty with mu = 0.1 * alpha for L2 regularization
        return GeneralizedLinearEstimator(
            datafit=SkglmHuber(delta=params.get("skglm_mcp_delta", 1.35)),
            penalty=MCP_plus_L2(alpha=params["skglm_mcp_alpha"],
                               gamma=params.get("skglm_mcp_gamma", 3.0),
                               mu=0.1 * params["skglm_mcp_alpha"]),
            solver=solver,
        )
    elif model_type == "lasso":
        return Lasso(alpha=params.get("lasso_alpha", 0.01), random_state=42, max_iter=2000)
    elif model_type == "elasticnet":
        return ElasticNet(alpha=params.get("en_alpha", 0.01), l1_ratio=params.get("en_l1_ratio", 0.5), random_state=42, max_iter=2000)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")


# ============================================================
# Core Metrics
# ============================================================
def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson over ranks. Faster than scipy.stats.spearmanr (no overhead)."""
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


def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    return _spearman_from_arrays(y_true, y_pred)


def compute_decile_monotonicity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    n = len(y_true)
    if n < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    order = np.argsort(np.asarray(y_pred, dtype=np.float64), kind="quicksort")
    yt_sorted = np.asarray(y_true, dtype=np.float64)[order]
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


def compute_top_bottom_spread(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    n = len(y_true)
    if n < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    order = np.argsort(np.asarray(y_pred, dtype=np.float64), kind="quicksort")
    yt_sorted = np.asarray(y_true, dtype=np.float64)[order]
    chunks = np.array_split(yt_sorted, 10)
    first, last = chunks[0], chunks[-1]
    if first.size == 0 or last.size == 0:
        return 0.0
    return float(last.mean() - first.mean())


# ============================================================
# Weighting & Input Scaling
# ============================================================
def compute_sample_weights(y: np.ndarray, k: float) -> np.ndarray:
    w = np.abs(y) ** k
    mean_w = np.mean(w)
    if mean_w > 1e-10:
        w = w / mean_w
    else:
        w = np.ones_like(w)
    return w


def scale_data_with_weights(X: np.ndarray, y: np.ndarray, w: np.ndarray):
    X_w = X * np.sqrt(w)[:, np.newaxis]
    y_w = y * np.sqrt(w)
    return X_w, y_w


# ============================================================
# Feature Selection Steps
# ============================================================
def benjamini_hochberg(p_values: np.ndarray, fdr_level: float = 0.20) -> np.ndarray:
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]
    
    thresholds = (np.arange(1, m + 1) / m) * fdr_level
    below = sorted_p <= thresholds
    
    if not np.any(below):
        return np.zeros(m, dtype=bool)
    
    max_idx = np.max(np.where(below)[0])
    cutoff = sorted_p[max_idx]
    
    return p_values <= cutoff


def run_screening(X_working: np.ndarray, y_working: np.ndarray):
    # Step 1: Cheap screening (vectorized Spearman).
    # Spearman(X_j, y) == Pearson(rank(X_j), rank(y)). Rank each column once,
    # then correlations are a single matmul.
    n, p = X_working.shape
    X_f64 = X_working.astype(np.float64, copy=False)
    y_f64 = y_working.astype(np.float64, copy=False)

    # Rank along axis 0 (per column). rankdata is 1-D only; do a single
    # concatenated rank over [X | y] column-wise via apply.
    X_rank = np.apply_along_axis(rankdata, 0, X_f64).astype(np.float64)
    y_rank = rankdata(y_f64).astype(np.float64)

    Xc = X_rank - X_rank.mean(axis=0, keepdims=True)
    yc = y_rank - y_rank.mean()
    sx = np.sqrt((Xc * Xc).sum(axis=0))
    sy = np.sqrt((yc * yc).sum())
    denom = sx * sy
    denom[denom < 1e-12] = np.nan
    rhos = (Xc.T @ yc) / denom
    rhos = np.nan_to_num(rhos, nan=0.0)

    # Two-sided p-values from Spearman under H0 using large-n normal approx.
    # t-stat via Fisher z, or normal approx under n large.
    # Standard large-n approx: r * sqrt((n-2)/(1-r^2)) ~ t_{n-2}.
    with np.errstate(divide="ignore", invalid="ignore"):
        t_sq_denom = 1.0 - rhos * rhos
        t_stat = np.where(t_sq_denom > 1e-12,
                          rhos * np.sqrt(np.maximum((n - 2) / t_sq_denom, 0.0)),
                          0.0)
    # Convert |t| -> two-sided p via survival of standard normal (n large).
    from scipy.stats import norm
    p_vals = 2.0 * norm.sf(np.abs(t_stat))
    p_vals = np.nan_to_num(p_vals, nan=1.0, posinf=1.0, neginf=1.0)

    screen_mask = benjamini_hochberg(p_vals, fdr_level=SCREEN_FDR)
    if screen_mask.sum() < 40:
        top_indices = np.argsort(p_vals)[:SCREEN_FALLBACK_K]
        screen_mask = np.zeros(len(p_vals), dtype=bool)
        screen_mask[top_indices] = True

    return screen_mask, p_vals, rhos


def run_vif_pruning(X_working: np.ndarray, selected_idx: np.ndarray, feature_names: list, threshold: float = 10.0) -> np.ndarray:
    """Iteratively remove the feature with the highest Variance Inflation Factor (VIF)

    above `threshold`, until all remaining selected features have VIF <= threshold.
    """
    if len(selected_idx) <= 1:
        return selected_idx

    current_idx = list(selected_idx)
    while len(current_idx) > 1:
        X_sub = X_working[:, current_idx]
        X_scaled = (X_sub - X_sub.mean(axis=0)) / (X_sub.std(axis=0) + 1e-10)

        n_samples, n_features = X_scaled.shape
        vifs = np.zeros(n_features)
        A = np.hstack([np.ones((n_samples, 1), dtype=X_scaled.dtype), X_scaled])

        for i in range(n_features):
            y = X_scaled[:, i]
            mask = np.ones(n_features + 1, dtype=bool)
            mask[i + 1] = False
            X_other = A[:, mask]
            coef, residues, rank, s = np.linalg.lstsq(X_other, y, rcond=None)
            if residues.size > 0:
                rss = residues[0]
            else:
                rss = np.sum((y - X_other @ coef) ** 2)
            tss = np.sum((y - y.mean()) ** 2)
            r2 = 1.0 - (rss / tss) if tss > 1e-10 else 0.0
            r2 = np.clip(r2, 0.0, 1.0 - 1e-15)
            vifs[i] = 1.0 / (1.0 - r2)

        max_idx = np.argmax(vifs)
        max_vif = vifs[max_idx]
        if max_vif > threshold:
            f_name = feature_names[current_idx[max_idx]]
            print(f"    [VIF Pruning] Drop feature '{f_name}' (VIF: {max_vif:.2f} > {threshold})")
            current_idx.pop(max_idx)
        else:
            break

    return np.array(current_idx)


def _stability_one_bootstrap(b: int, X_screened: np.ndarray, y_working: np.ndarray,
                             alphas: np.ndarray, n_total: int, subsample_size: int,
                             rng_seed: int):
    """One stability-selection subsample. Returns (selection_matrix[:, :, b]).

    Independent RNG per worker so joblib Parallel reproduces the original
    sequential `np.random.default_rng(42)` stream by re-seeding from a base.
    """
    rng = np.random.default_rng(rng_seed + b)
    sub_idx = rng.choice(n_total, size=subsample_size, replace=False)
    X_sub = X_screened[sub_idx]
    y_sub = y_working[sub_idx]
    X_sub_scaled = StandardScaler().fit_transform(X_sub)
    _, coefs, _ = enet_path(X_sub_scaled, y_sub, l1_ratio=0.5, alphas=alphas)
    return (np.abs(coefs) > 1e-5).astype(bool)


def run_stability_selection(X_working: np.ndarray, y_working: np.ndarray, screen_mask: np.ndarray, rhos: np.ndarray,
                             B: int = STABILITY_B, pi: float = STABILITY_PI,
                             n_jobs: int = BOOTSTRAP_N_JOBS):
    # Step 2: Cluster Stability Selection (CSS)
    screened_features_idx = np.where(screen_mask)[0]
    X_screened = X_working[:, screened_features_idx]

    scaler = StandardScaler()
    X_cluster_scaled = scaler.fit_transform(X_screened)

    # Hierarchical Clustering based on correlation to handle collinearity
    n_screened = X_screened.shape[1]
    if n_screened > 1:
        corr = np.corrcoef(X_cluster_scaled, rowvar=False)
        dist = 1.0 - np.abs(corr)
        dist = np.clip(dist, 0.0, 2.0)
        dist = (dist + dist.T) / 2.0
        np.fill_diagonal(dist, 0.0)
        linkage_matrix = linkage(squareform(dist), method="complete")
        cluster_labels = fcluster(linkage_matrix, t=0.25, criterion="distance") # t=0.25 means |r| >= 0.75
    else:
        cluster_labels = np.ones(n_screened, dtype=int)

    alphas, _, _ = enet_path(X_cluster_scaled, y_working, l1_ratio=0.5, n_alphas=50)
    alphas = _to_f32(alphas)

    n_total = X_working.shape[0]
    subsample_size = n_total // 2

    # Parallelize the B bootstrap fits across cores.
    base_seed = 42
    slices = Parallel(n_jobs=n_jobs, backend="loky")(
        delayed(_stability_one_bootstrap)(
            b, X_screened, y_working, alphas, n_total, subsample_size, base_seed
        )
        for b in range(B)
    )
    selection_matrix = np.stack(slices, axis=2)  # (n_screened, n_alphas, B)

    # CSS Aggregation: Group selection matrix by cluster labels
    num_clusters = cluster_labels.max()
    cluster_to_features = {g: [] for g in range(1, num_clusters + 1)}
    for local_idx, label in enumerate(cluster_labels):
        cluster_to_features[label].append(local_idx)

    # For each subsample and alpha, check if ANY feature in each cluster is active
    cluster_selection_matrix = np.zeros((num_clusters, selection_matrix.shape[1], B), dtype=bool)
    for g in range(1, num_clusters + 1):
        feature_indices = cluster_to_features[g]
        cluster_selection_matrix[g - 1] = np.any(selection_matrix[feature_indices], axis=0)

    cluster_sel_probs = np.mean(cluster_selection_matrix, axis=2) # (num_clusters, n_alphas)
    
    # Restrict alphas to those that select at most STABILITY_Q clusters on average
    expected_active_clusters = cluster_sel_probs.sum(axis=0)
    valid_alphas_idx = np.where(expected_active_clusters <= STABILITY_Q)[0]
    if len(valid_alphas_idx) == 0:
        valid_alphas_idx = np.array([0])
        
    cluster_stability_scores = np.max(cluster_sel_probs[:, valid_alphas_idx], axis=1)

    stable_clusters_keep = cluster_stability_scores >= pi
    if stable_clusters_keep.sum() < 3:
        full_cluster_stability_scores = np.max(cluster_sel_probs, axis=1)
        top_clusters = np.argsort(full_cluster_stability_scores)[-5:]
        stable_clusters_keep = np.zeros_like(stable_clusters_keep, dtype=bool)
        stable_clusters_keep[top_clusters] = True
        cluster_stability_scores = full_cluster_stability_scores

    # For each cluster, compute individual feature stability scores for ranking representatives
    individual_sel_probs = np.mean(selection_matrix, axis=2)
    individual_stability_scores = np.max(individual_sel_probs[:, valid_alphas_idx], axis=1)

    stability_selected_idx = []
    all_stability_scores = np.zeros(X_working.shape[1])

    for g in range(1, num_clusters + 1):
        feature_indices = cluster_to_features[g]
        for local_i in feature_indices:
            orig_i = screened_features_idx[local_i]
            # Store individual stability score by default
            all_stability_scores[orig_i] = individual_stability_scores[local_i]
            
        if stable_clusters_keep[g - 1]:
            # Select representative: highest individual stability score, tie-break by absolute Spearman correlation rho
            best_local_feat = max(feature_indices, key=lambda idx: (individual_stability_scores[idx], abs(rhos[screened_features_idx[idx]])))
            best_orig_i = screened_features_idx[best_local_feat]
            stability_selected_idx.append(best_orig_i)
            # Store cluster stability score for the representative
            all_stability_scores[best_orig_i] = cluster_stability_scores[g - 1]

    stability_selected_idx = np.array(stability_selected_idx)
    return stability_selected_idx, all_stability_scores


# ============================================================
# Yearly Blocked CV Engine
# ============================================================
def _loyo_one_fold(fold, model_type, params, k_weight):
    test_idx, X_tr_scaled, X_te_scaled, y_tr = fold
    w_tr = compute_sample_weights(y_tr, k_weight)
    X_tr_w, y_tr_w = scale_data_with_weights(X_tr_scaled, y_tr, w_tr)
    model = _build_model(model_type, params)
    model.fit(X_tr_w, y_tr_w)
    return test_idx, model.predict(X_te_scaled)


def run_loyo_cv(loyo_folds: list, model_type: str, params: dict, k_weight: float,
                n_samples: int, n_jobs: int = 1):
    oof_pred_sum = np.zeros(n_samples, dtype=np.float64)
    oof_pred_cnt = np.zeros(n_samples, dtype=np.float64)
    
    if n_jobs and n_jobs > 1 and len(loyo_folds) > 1:
        results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_loyo_one_fold)(f, model_type, params, k_weight)
            for f in loyo_folds
        )
        for test_idx, preds in results:
            oof_pred_sum[test_idx] += preds
            oof_pred_cnt[test_idx] += 1
    else:
        for fold in loyo_folds:
            test_idx, preds = _loyo_one_fold(fold, model_type, params, k_weight)
            oof_pred_sum[test_idx] += preds
            oof_pred_cnt[test_idx] += 1
            
    oof_preds = np.zeros(n_samples, dtype=np.float64)
    mask = oof_pred_cnt > 0
    oof_preds[mask] = oof_pred_sum[mask] / oof_pred_cnt[mask]
    return oof_preds


def calculate_yearly_metrics(year_groups, y_true: np.ndarray, y_pred: np.ndarray,
                             k_features: int, coef_norm: float, ess: float = 0.0):
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)

    y_ics = np.empty(len(year_groups))
    y_tail_ics = np.empty(len(year_groups))
    y_tail_hits = np.empty(len(year_groups))
    y_monos = np.empty(len(year_groups))
    y_spreads = np.empty(len(year_groups))

    for i, (_year, idx) in enumerate(year_groups):
        y_t = y_true[idx]
        y_p = y_pred[idx]

        y_ics[i] = spearman_ic(y_t, y_p)

        n_tail = max(5, int(y_p.shape[0] * 0.10))
        if y_p.shape[0] >= n_tail * 2:
            order = np.argsort(y_p, kind="quicksort")
            tail_idx = np.concatenate([order[:n_tail], order[-n_tail:]])
            tail_ic = _spearman_from_arrays(y_t[tail_idx], y_p[tail_idx])
        else:
            tail_ic = 0.0
        y_tail_ics[i] = tail_ic
        y_tail_hits[i] = 1.0 if tail_ic > 0 else 0.0

        y_monos[i] = compute_decile_monotonicity(y_t, y_p)
        y_spreads[i] = compute_top_bottom_spread(y_t, y_p)

    mean_tail_ic = float(y_tail_ics.mean())
    std_tail_ic = float(y_tail_ics.std())

    m1 = mean_tail_ic / (std_tail_ic + 1e-10)     # Yearly Tail IC IR
    m2 = mean_tail_ic                             # Yearly Tail IC Mean
    m3 = float(y_tail_hits.mean())                # Yearly Hit Rate
    m4 = float(y_ics.mean())                      # Overall Rank IC
    m5 = float(y_monos.mean())                    # Decile Monotonicity
    m6 = float(y_spreads.mean())                  # Top-Bottom Spread
    if ess > 0.0:
        m7 = -float(k_features) / (ess / ACTIVE_FEATURE_ESS_DIVISOR)    # Tie sparsity penalty to ESS directly
    else:
        m7 = -np.log(1.0 + k_features)            # Feature Parsimony (fallback)
    m8 = -coef_norm                               # Coefficient Bloat (penalized)

    raw_metrics = [m1, m2, m3, m4, m5, m6, m7, m8]
    return raw_metrics, [_y for _y, _ in year_groups], y_tail_ics


def compute_deflated_metric(values: list, best_value: float, rho: float = 0.5) -> float:
    """Expected multiple-comparison overfit correction for choosing the maximum

    of N correlated trial configurations (Marcos Lopez de Prado).
    """
    n = len(values)
    if n <= 1:
        return best_value
    std_val = np.std(values)
    overfit_bias = std_val * np.sqrt(2.0 * np.log(n)) * np.sqrt(1.0 - rho)
    return float(best_value - overfit_bias)


# ============================================================
# Main ETF Trainer
# ============================================================
def train_etf(etf_name: str, n_trials: int = 50, side: str = "single",
              use_cache: bool = True, optuna_n_jobs: int = OPTUNA_N_JOBS,
              bootstrap_n_jobs: int = BOOTSTRAP_N_JOBS, loyo_n_jobs: int = 1):
    print(f"\n" + "=" * 80)
    print(f"Starting First-Principles Training for {etf_name} (Side: {side})")
    print(f"  use_cache={use_cache}  optuna_n_jobs={optuna_n_jobs}  "
          f"bootstrap_n_jobs={bootstrap_n_jobs}  loyo_n_jobs={loyo_n_jobs}")
    print(f"=" * 80)

    timings = {}
    t_start = time.perf_counter()

    # Load features parquet
    features_path = DATA_DIR / f"features_{etf_name}.parquet"
    if not features_path.exists():
        print(f"  [ERROR] Features file not found: {features_path}")
        return None

    parquet_mtime = int(features_path.stat().st_mtime_ns)

    df = pd.read_parquet(features_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])

    # Handle NaNs in features
    X_df = df[FEATURES].ffill().fillna(df[FEATURES].median())
    # fp32 downcast: BLAS-friendly, ~50% memory, results within float32 epsilon.
    X = _to_f32(X_df.values)
    y = df[TARGET].values.astype(np.float32)

    N = len(df)
    print(f"Loaded {N} samples and {X.shape[1]} features.")

    tag = etf_name if side == "single" else f"{etf_name}_{side}"
    pilot_db_path = DATA_DIR / f"optuna_pilot_{tag}.log"
    main_db_path = DATA_DIR / f"optuna_main_{tag}.log"

    # Target scaling (consistent with old pipeline target scaling)
    y_scaled = (y * np.float32(100.0)).astype(np.float32)

    # Step 0: Lockout split by date (ignoring OOS lockbox data to keep it untouched during training)
    working_mask = df["date"] < LOCKBOX_DATE
    working_idx = np.where(working_mask)[0]

    X_working = _to_f32(X[working_idx])
    y_working = y_scaled[working_idx].astype(np.float32)
    dates_working = df["date"].iloc[working_idx].reset_index(drop=True)

    # Nest feature selection & validation to eliminate leakage bias
    sel_val_mask = np.zeros(len(df), dtype=bool)
    for start_val, end_val in VAL_BLOCKS:
        block_mask = (df["date"] >= pd.Timestamp(start_val)) & (df["date"] < pd.Timestamp(end_val))
        sel_val_mask |= block_mask
        
    sel_val_idx = np.where(sel_val_mask)[0]
    X_sel_val = _to_f32(X[sel_val_idx])
    y_sel_val = y_scaled[sel_val_idx].astype(np.float32)
    dates_sel_val = df["date"].iloc[sel_val_idx].reset_index(drop=True)

    # Initial selection train mask, excluding validation blocks
    sel_train_mask = (df["date"] < LOCKBOX_DATE) & (~sel_val_mask)
    
    # Apply 10-day embargo at validation boundaries to prevent leakage from train to validation
    gap_days = 10
    sel_train_dates = df["date"][sel_train_mask]
    keep_train = np.ones(len(sel_train_dates), dtype=bool)
    
    for start_val, end_val in VAL_BLOCKS:
        embargo_start = pd.Timestamp(start_val) - pd.Timedelta(days=gap_days)
        embargo_end = pd.Timestamp(end_val) + pd.Timedelta(days=gap_days)
        in_embargo = (sel_train_dates >= embargo_start) & (sel_train_dates <= embargo_end)
        keep_train[in_embargo] = False
        
    sel_train_indices = df.index[sel_train_mask][keep_train]
    sel_train_mask = np.zeros(len(df), dtype=bool)
    sel_train_mask[sel_train_indices] = True
    
    sel_train_idx = np.where(sel_train_mask)[0]
    X_sel_train = _to_f32(X[sel_train_idx])
    y_sel_train = y_scaled[sel_train_idx].astype(np.float32)
    dates_sel_train = df["date"].iloc[sel_train_idx].reset_index(drop=True)

    print(f"Split: Working={len(working_idx)} rows (Lockbox OOS data ignored during training).")
    print(f"       Selection Train={len(sel_train_idx)} rows, Selection Val={len(sel_val_idx)} rows.")

    # Precompute yearly row-index groups for the Selection Train subset (used by per-trial CV metric computation).
    years_sel_train = dates_sel_train.dt.year.values
    year_groups = [(int(y), np.where(years_sel_train == y)[0])
                   for y in sorted(np.unique(years_sel_train))]

    timings["data_loading"] = time.perf_counter() - t_start

    # ── Cache key parts ───────────────────────────────────────────────
    # Auto-invalidate when: feature parquet regen (mtime), FEATURES list
    # length changes, or any of the deterministic knobs below change.
    # See AGENTS.md "Cache invalidation" for manual-clear guidance.
    select_key = [
        "v7", etf_name, len(FEATURES), int(parquet_mtime),
        int(X_sel_train.shape[0]), int(X_sel_train.shape[1]),
        STABILITY_B, STABILITY_PI, SCREEN_FDR, SCREEN_FALLBACK_K,
        tuple(VAL_BLOCKS), TARGET,
    ]
    select_cache_path = CACHE_DIR / f"cache_select_{etf_name}_{_cache_key(select_key)}.joblib"

    # Step 1 + 2: Cheap screening + Stability selection (cached).
    def _compute_selection():
        t_sel_start = time.perf_counter()
        print("Running feature screening...")
        screen_mask, p_vals, rhos = run_screening(X_sel_train, y_sel_train)
        t_screen = time.perf_counter() - t_sel_start
        print(f"Screened features: {screen_mask.sum()} surviving candidates.")
        
        t_stab_start = time.perf_counter()
        print("Running stability selection...")
        stability_selected_idx, stability_scores = run_stability_selection(
            X_sel_train, y_sel_train, screen_mask, rhos,
            B=STABILITY_B, pi=STABILITY_PI, n_jobs=bootstrap_n_jobs,
        )
        t_stab = time.perf_counter() - t_stab_start

        # Run iterative VIF pruning to eliminate multivariate collinearity
        print("Running iterative VIF pruning...")
        t_vif_start = time.perf_counter()
        vif_pruned_idx = run_vif_pruning(X_sel_train, stability_selected_idx, FEATURES, threshold=10.0)
        t_vif = time.perf_counter() - t_vif_start
        print(f"VIF pruning finished. Dropped {len(stability_selected_idx) - len(vif_pruned_idx)} collinear features. Kept {len(vif_pruned_idx)} representatives.")

        return {
            "screen_mask": screen_mask,
            "p_vals": p_vals,
            "rhos": rhos,
            "stability_selected_idx": np.asarray(vif_pruned_idx),
            "stability_scores": np.asarray(stability_scores),
            "time_screen": t_screen,
            "time_stability": t_stab + t_vif,
        }

    t_select_block_start = time.perf_counter()
    sel = _load_or_compute(select_cache_path, select_key, _compute_selection,
                           use_cache=use_cache)
    timings["feature_selection"] = time.perf_counter() - t_select_block_start

    screen_mask = sel["screen_mask"]
    stability_selected_idx = sel["stability_selected_idx"]
    stability_scores = sel["stability_scores"]

    # ── Feature Screening (Step 1) Diagnostics ──
    p_vals = sel["p_vals"]
    rhos = sel["rhos"]
    bh_mask = benjamini_hochberg(p_vals, fdr_level=SCREEN_FDR)
    bh_pass_count = bh_mask.sum()
    fallback_triggered = (bh_pass_count < 40)

    print("\n  [DIAGNOSTICS] Feature Screening (Step 1) Details:")
    print(f"    Total features input: {len(FEATURES)}")
    print(f"    Features passing BH-FDR (FDR={SCREEN_FDR}): {bh_pass_count}")
    if fallback_triggered:
        print(f"    [WARNING] Fallback triggered! Kept top {screen_mask.sum()} features by p-value instead.")
    else:
        print(f"    No fallback needed. Kept {screen_mask.sum()} features.")

    abs_rhos = np.abs(rhos)
    print(f"    Spearman rho absolute values - Min: {abs_rhos.min():.4f}, Median: {np.median(abs_rhos):.4f}, Max: {abs_rhos.max():.4f}")
    print(f"    p-values - Min: {p_vals.min():.2e}, Median: {np.median(p_vals):.4f}, Max: {p_vals.max():.4f}")

    sorted_idx = np.argsort(rhos)
    print("    Top 5 positive Spearman correlations:")
    for idx in sorted_idx[-5:][::-1]:
        print(f"      - {FEATURES[idx]}: rho = {rhos[idx]:+.4f}, p = {p_vals[idx]:.2e}")
    print("    Top 5 negative Spearman correlations:")
    for idx in sorted_idx[:5]:
        print(f"      - {FEATURES[idx]}: rho = {rhos[idx]:+.4f}, p = {p_vals[idx]:.2e}")

    # ── Stability Selection (Step 2) Diagnostics ──
    screened_idx = np.where(screen_mask)[0]
    scores_on_screened = stability_scores[screened_idx]
    pass_pi_count = np.sum(scores_on_screened >= STABILITY_PI)
    stab_fallback_triggered = (pass_pi_count < 3)

    print("\n  [DIAGNOSTICS] Stability Selection (Step 2) Details:")
    print(f"    Features input to Stability Selection: {len(screened_idx)}")
    print(f"    Features with stability score >= {STABILITY_PI}: {pass_pi_count}")
    if stab_fallback_triggered:
        print(f"    [WARNING] Fallback triggered! Kept top {len(stability_selected_idx)} features by stability score instead.")
    else:
        print(f"    No fallback needed. Kept {len(stability_selected_idx)} features.")

    if len(scores_on_screened) > 0:
        pcts = np.percentile(scores_on_screened, [25, 50, 75, 90, 95])
        print(f"    Stability score percentiles on screened features - 25%: {pcts[0]:.2f}, 50%: {pcts[1]:.2f}, 75%: {pcts[2]:.2f}, 90%: {pcts[3]:.2f}, 95%: {pcts[4]:.2f}")

    selected_feature_names = [FEATURES[idx] for idx in stability_selected_idx]
    K_sel = len(stability_selected_idx)
    print("    Stability selected features & scores:")
    for idx in stability_selected_idx:
        print(f"      - {FEATURES[idx]}: score = {stability_scores[idx]:.2f}")

    print(f"Stability selection finished. Kept {K_sel} features.")

    # Freeze the features for the final and Optuna loops
    X_sel_train_final = _to_f32(X_sel_train[:, stability_selected_idx])
    X_sel_val_final = _to_f32(X_sel_val[:, stability_selected_idx])
    X_working_final = _to_f32(X_working[:, stability_selected_idx])

    # ── Feature Quality Diagnostics (Multicollinearity & Condition Number) ──
    if K_sel > 1:
        corr_matrix = np.corrcoef(X_sel_train_final, rowvar=False)
        collinear_pairs = []
        for i in range(K_sel):
            for j in range(i + 1, K_sel):
                if abs(corr_matrix[i, j]) >= 0.85:
                    collinear_pairs.append((selected_feature_names[i], selected_feature_names[j], float(corr_matrix[i, j])))
        
        # Standardize X_sel_train_final to compute condition number correctly
        X_scaled_tmp = (X_sel_train_final - X_sel_train_final.mean(axis=0)) / (X_sel_train_final.std(axis=0) + 1e-10)
        _, s, _ = np.linalg.svd(X_scaled_tmp, full_matrices=False)
        s_min = s.min()
        condition_number = float(s.max() / s_min) if s_min > 1e-10 else float("inf")
    else:
        collinear_pairs = []
        condition_number = 1.0

    print("\n  [DIAGNOSTICS] Selected Feature Quality:")
    print(f"    Selected Features Condition Number: {condition_number:.2f}")
    if condition_number > 100:
        print(f"    [WARNING] Severe multicollinearity detected (condition number > 100)!")
    elif condition_number > 30:
        print(f"    [WARNING] Moderate multicollinearity detected (condition number > 30).")
    else:
        print(f"    Feature matrix is numerically stable.")

    if collinear_pairs:
        print(f"    [WARNING] Found {len(collinear_pairs)} highly collinear pairs (|rho| >= 0.85):")
        for f1, f2, val in collinear_pairs:
            print(f"      - {f1} <-> {f2}: rho = {val:+.4f}")
    else:
        print("    No highly collinear feature pairs found.")

    # ── LOYO folds cache (depends on selected features only) ──────────
    loyo_key = [
        "v7", etf_name, len(FEATURES), int(parquet_mtime),
        tuple(int(i) for i in stability_selected_idx),
        tuple(VAL_BLOCKS), TARGET,
    ]
    loyo_cache_path = CACHE_DIR / f"cache_loyo_{etf_name}_{_cache_key(loyo_key)}.joblib"

    def _compute_loyo():
        from itertools import combinations
        n = len(y_sel_train)
        n_groups = 6
        n_test_groups = 2
        gap_days = 10
        
        boundaries = np.linspace(0, n, n_groups + 1).astype(int)
        folds = []
        
        group_indices = list(range(n_groups))
        for test_comb in combinations(group_indices, n_test_groups):
            test_idx_list = []
            for g in test_comb:
                test_idx_list.append(np.arange(boundaries[g], boundaries[g+1]))
            test_idx = np.concatenate(test_idx_list)
            
            all_indices = np.arange(n)
            in_test = np.zeros(n, dtype=bool)
            in_test[test_idx] = True
            train_idx_raw = all_indices[~in_test]
            
            min_test_dates = [dates_sel_train.values[boundaries[g]] for g in test_comb]
            max_test_dates = [dates_sel_train.values[boundaries[g+1] - 1] for g in test_comb]
            
            train_dates = dates_sel_train.values[train_idx_raw]
            keep_train = np.ones(len(train_idx_raw), dtype=bool)
            
            for min_d, max_d in zip(min_test_dates, max_test_dates):
                embargo_start = pd.Timestamp(min_d) - pd.Timedelta(days=gap_days)
                embargo_end = pd.Timestamp(max_d) + pd.Timedelta(days=gap_days)
                in_embargo = (train_dates >= embargo_start.to_datetime64()) & (train_dates <= embargo_end.to_datetime64())
                keep_train[in_embargo] = False
                
            train_idx = train_idx_raw[keep_train]
            
            if len(train_idx) == 0 or len(test_idx) == 0:
                continue
                
            X_tr, y_tr = X_sel_train_final[train_idx], y_sel_train[train_idx]
            X_te = X_sel_train_final[test_idx]
            
            scaler = StandardScaler()
            X_tr_scaled = scaler.fit_transform(X_tr)
            X_te_scaled = scaler.transform(X_te)
            
            folds.append((
                test_idx.astype(np.int64),
                _to_f32(X_tr_scaled),
                _to_f32(X_te_scaled),
                y_tr.astype(np.float32),
            ))
        return folds

    t_loyo_block_start = time.perf_counter()
    loyo_folds = _load_or_compute(loyo_cache_path, loyo_key, _compute_loyo,
                                  use_cache=use_cache)
    timings["loyo_folds"] = time.perf_counter() - t_loyo_block_start

    print("\n  [DIAGNOSTICS] LOYO CV Folds Details:")
    print(f"    Number of folds (years): {len(loyo_folds)}")
    for i, fold in enumerate(loyo_folds):
        test_idx, X_tr_scaled, X_te_scaled, y_tr = fold
        test_years = dates_sel_train.iloc[test_idx].dt.year.unique()
        print(f"      Fold {i+1}: Test Year(s) = {list(test_years)}, Train shape = {X_tr_scaled.shape}, Test shape = {X_te_scaled.shape}")

    # Precompute the *unweighted* standardized selection train matrix once.
    # Per-trial cost only requires re-applying row-wise sqrt(w).
    scaler_init = StandardScaler()
    X_sel_train_scaled_base = _to_f32(scaler_init.fit_transform(X_sel_train_final))
    # Standardize selection validation features using the selection train scaler.
    X_sel_val_scaled_base = _to_f32(scaler_init.transform(X_sel_val_final))

    # Define Optuna objective helper
    pilot_metrics = []

    def evaluate_params(trial_params):
        model_type = trial_params["model_type"]
        k_weight = trial_params["k_weight"]

        # Build specific parameters dict
        params = {}
        if model_type == "skglm_huber_l1":
            params["skglm_huber_l1_alpha"] = trial_params["skglm_huber_l1_alpha"]
            params["skglm_huber_delta"] = trial_params["skglm_huber_delta"]
        elif model_type == "skglm_mcp":
            params["skglm_mcp_alpha"] = trial_params["skglm_mcp_alpha"]
            params["skglm_mcp_gamma"] = trial_params["skglm_mcp_gamma"]
            params["skglm_mcp_delta"] = trial_params["skglm_mcp_delta"]
        elif model_type == "lasso":
            params["lasso_alpha"] = trial_params["lasso_alpha"]
        elif model_type == "elasticnet":
            params["en_alpha"] = trial_params["en_alpha"]
            params["en_l1_ratio"] = trial_params["en_l1_ratio"]

        # LOYO CV predictions
        oof_preds = run_loyo_cv(loyo_folds, model_type, params, k_weight,
                                len(y_sel_train), n_jobs=loyo_n_jobs)

        # Fit model on selection train set to compute coefficient norm.
        w_temp = compute_sample_weights(y_sel_train, k_weight).astype(np.float32)
        sqrt_w = np.sqrt(w_temp)[:, np.newaxis]
        X_weighted_temp = X_sel_train_scaled_base * sqrt_w
        y_weighted_temp = y_sel_train * sqrt_w[:, 0]

        model_temp = _build_model(model_type, params)
        model_temp.fit(X_weighted_temp, y_weighted_temp)

        coef_norm = float(np.linalg.norm(model_temp.coef_))
        active_k = int(np.sum(np.abs(model_temp.coef_) > 1e-5))

        # Compute Kish ESS
        sum_w = w_temp.sum()
        sum_w2 = (w_temp ** 2).sum()
        ess = float((sum_w ** 2) / sum_w2) if sum_w2 > 1e-10 else float(len(w_temp))

        # Calculate raw yearly metrics (with ESS-scaled parsimony) on CV folds
        raw_metrics, _, _ = calculate_yearly_metrics(
            year_groups, y_sel_train, oof_preds, active_k, coef_norm, ess=ess)

        # Predict on selection validation block and compute validation metrics
        val_preds = model_temp.predict(X_sel_val_scaled_base)
        val_ic = spearman_ic(y_sel_val, val_preds)

        n_tail_val = max(5, int(len(y_sel_val) * 0.10))
        if len(y_sel_val) >= n_tail_val * 2:
            order_val = np.argsort(val_preds, kind="quicksort")
            tail_idx_val = np.concatenate([order_val[:n_tail_val], order_val[-n_tail_val:]])
            val_tail_ic = spearman_ic(y_sel_val[tail_idx_val], val_preds[tail_idx_val])
        else:
            val_tail_ic = 0.0

        val_mono = compute_decile_monotonicity(y_sel_val, val_preds)
        val_spread = compute_top_bottom_spread(y_sel_val, val_preds)

        val_metrics = [val_ic, val_tail_ic, val_mono, val_spread]

        return raw_metrics, val_metrics, model_temp, scaler_init

    # ── Pilot calibration cache ───────────────────────────────────────
    pilot_key = [
        "v7", etf_name, len(FEATURES), int(parquet_mtime),
        tuple(int(i) for i in stability_selected_idx),
        tuple(VAL_BLOCKS), TARGET, PILOT_N_TRIALS, PILOT_SEED,
    ]
    pilot_cache_path = CACHE_DIR / f"cache_pilot_{etf_name}_{_cache_key(pilot_key)}.joblib"

    def _compute_pilot():
        print(f"\nRunning Optuna Pilot Study ({PILOT_N_TRIALS} trials) for normalization calibration...")
        if pilot_db_path.exists():
            pilot_db_path.unlink()
        pilot_storage = JournalStorage(JournalFileBackend(str(pilot_db_path)))
        pilot_study = optuna.create_study(
            study_name=f"pilot_{tag}",
            storage=pilot_storage,
            direction="maximize",
            sampler=optuna.samplers.TPESampler(seed=PILOT_SEED),
            load_if_exists=True
        )

        def pilot_objective(trial):
            model_type = trial.suggest_categorical("model_type", ["skglm_huber_l1", "skglm_mcp"])
            k_weight = trial.suggest_float("k_weight", 0.0, 3.0)

            trial_params = {"model_type": model_type, "k_weight": k_weight}
            if model_type == "skglm_huber_l1":
                trial_params["skglm_huber_l1_alpha"] = trial.suggest_float("skglm_huber_l1_alpha", 1e-5, 10.0, log=True)
                trial_params["skglm_huber_delta"] = trial.suggest_float("skglm_huber_delta", 0.5, 5.0)
            elif model_type == "skglm_mcp":
                trial_params["skglm_mcp_alpha"] = trial.suggest_float("skglm_mcp_alpha", 1e-5, 10.0, log=True)
                trial_params["skglm_mcp_gamma"] = trial.suggest_float("skglm_mcp_gamma", 1.5, 10.0)
                trial_params["skglm_mcp_delta"] = trial.suggest_float("skglm_mcp_delta", 0.5, 5.0)

            try:
                raw_metrics, val_metrics, _, _ = evaluate_params(trial_params)
                trial.set_user_attr("raw_metrics", raw_metrics)
                trial.set_user_attr("val_metrics", val_metrics)
                trial.set_user_attr("params", trial_params)
                # Objective in pilot: simple sum of Val Overall IC and Val Tail IC on the selection validation block
                return val_metrics[0] + val_metrics[1]
            except Exception as e:
                import traceback
                print(f"Pilot trial failed: {e}")
                traceback.print_exc()
                return -999.0

        def run_pilot_trial():
            local_study = optuna.load_study(study_name=f"pilot_{tag}", storage=pilot_storage)
            local_study.optimize(pilot_objective, n_trials=1)

        Parallel(n_jobs=optuna_n_jobs)(
            delayed(run_pilot_trial)() for _ in range(PILOT_N_TRIALS)
        )

        pilot_records = []
        final_pilot_study = optuna.load_study(study_name=f"pilot_{tag}", storage=pilot_storage)
        for t in final_pilot_study.trials:
            if t.state == optuna.trial.TrialState.COMPLETE:
                raw_m = t.user_attrs.get("raw_metrics")
                val_m = t.user_attrs.get("val_metrics")
                params = t.user_attrs.get("params")
                if raw_m is not None and val_m is not None and params is not None:
                    pilot_records.append({"params": params, "raw_metrics": raw_m, "val_metrics": val_m})
        return pilot_records

    t_pilot_block_start = time.perf_counter()
    pilot_records = _load_or_compute(pilot_cache_path, pilot_key, _compute_pilot,
                                     use_cache=use_cache)
    timings["pilot_study"] = time.perf_counter() - t_pilot_block_start

    if len(pilot_records) == 0:
        raise RuntimeError("Optuna pilot run failed entirely. Check skglm model fit/installation.")

    pilot_metrics = np.array([r["raw_metrics"] for r in pilot_records])
    pilot_val_metrics = np.array([r["val_metrics"] for r in pilot_records])

    # Compute median and MAD per metric on selection validation block
    val_medians = np.median(pilot_val_metrics, axis=0)
    val_mads = np.median(np.abs(pilot_val_metrics - val_medians), axis=0)
    # Avoid zero division
    val_mads[val_mads < 1e-6] = 1.0

    print("\n  [DIAGNOSTICS] Optuna Pilot Study Details:")
    print(f"    Total pilot trials loaded/run: {len(pilot_records)}")
    print("    Raw CV metrics distribution across pilot study:")
    metric_names = ["M1 (Tail IC IR)", "M2 (Tail IC Mean)", "M3 (Hit Rate)", "M4 (Overall IC)", 
                    "M5 (Monotonicity)", "M6 (Top-Bot Spread)", "M7 (Parsimony)", "M8 (Coef Bloat)"]
    for i in range(8):
        vals = pilot_metrics[:, i]
        print(f"      {metric_names[i]:<20}: Min = {vals.min():.4f}, Median = {np.median(vals):.4f}, Max = {vals.max():.4f}")

    print("    Selection Validation metrics distribution across pilot study:")
    val_metric_names = ["Val IC", "Val Tail IC", "Val Monotonicity", "Val Top-Bot Spread"]
    for i in range(4):
        vals = pilot_val_metrics[:, i]
        print(f"      {val_metric_names[i]:<20}: Min = {vals.min():.4f}, Median = {val_medians[i]:.4f}, Max = {vals.max():.4f}, MAD = {val_mads[i]:.4f}")

    print("Normalizing constants calibrated from Pilot run (Selection Validation):")
    for i in range(4):
        print(f"  Val{i+1}: Median={val_medians[i]:.6f}, MAD={val_mads[i]:.6f}")

    # Phase 2: Main Study (Optuna Tuning)
    print(f"\nRunning main Optuna Study ({n_trials} trials) with First-Principles Multi-Metric Objective...")
    t_main_block_start = time.perf_counter()
    if main_db_path.exists():
        main_db_path.unlink()
    main_storage = JournalStorage(JournalFileBackend(str(main_db_path)))
    study = optuna.create_study(
        study_name=f"main_{tag}",
        storage=main_storage,
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=PILOT_SEED + 1),
        load_if_exists=True
    )

    best_raw_metrics = None

    def main_objective(trial):
        model_type = trial.suggest_categorical("model_type", ["skglm_huber_l1", "skglm_mcp"])
        k_weight = trial.suggest_float("k_weight", 0.0, 3.0)

        trial_params = {"model_type": model_type, "k_weight": k_weight}
        if model_type == "skglm_huber_l1":
            trial_params["skglm_huber_l1_alpha"] = trial.suggest_float("skglm_huber_l1_alpha", 1e-5, 10.0, log=True)
            trial_params["skglm_huber_delta"] = trial.suggest_float("skglm_huber_delta", 0.5, 5.0)
        elif model_type == "skglm_mcp":
            trial_params["skglm_mcp_alpha"] = trial.suggest_float("skglm_mcp_alpha", 1e-5, 10.0, log=True)
            trial_params["skglm_mcp_gamma"] = trial.suggest_float("skglm_mcp_gamma", 1.5, 10.0)
            trial_params["skglm_mcp_delta"] = trial.suggest_float("skglm_mcp_delta", 0.5, 5.0)

        try:
            raw_metrics, val_metrics, _model_obj, _scaler_obj = evaluate_params(trial_params)

            # Extract metrics for kill switches (CV folds)
            m1, m2, m3, m4, m5, m6, m7, m8 = raw_metrics

            # Calculate Kish ESS percentage on selection train subset
            w_temp = compute_sample_weights(y_sel_train, k_weight)
            sum_w = w_temp.sum()
            sum_w2 = (w_temp ** 2).sum()
            ess = float((sum_w ** 2) / sum_w2) if sum_w2 > 1e-10 else float(len(w_temp))
            ess_pct = ess / len(w_temp)

            # Active feature cap based on ESS: events-per-variable heuristic
            active_k = int(np.sum(np.abs(_model_obj.coef_) > 1e-5))
            max_active_features = max(3, int(ess / ACTIVE_FEATURE_ESS_DIVISOR))

            # Calculate weight concentration (Gini index) of model coefficients
            coefs = _model_obj.coef_
            abs_coefs = np.abs(coefs)
            sum_abs = abs_coefs.sum()
            if sum_abs > 1e-10:
                sorted_c = np.sort(abs_coefs)
                m_gini = len(sorted_c)
                index = np.arange(1, m_gini + 1)
                gini = float((2.0 * (index * sorted_c).sum()) / (m_gini * sum_abs) - (m_gini + 1) / m_gini)
            else:
                gini = 0.0

            # Hard Constraints / Kill Switches (on CV folds to ensure training stability):
            pruning_reasons = []
            if m4 <= 0:
                pruning_reasons.append("M4 (Overall IC <= 0)")
            if m3 < 0.60:
                pruning_reasons.append("M3 (Hit Rate < 60%)")
            if m5 <= 0.25:
                pruning_reasons.append("M5 (Monotonicity <= 0.25)")
            if m6 <= 0:
                pruning_reasons.append("M6 (Top-Bottom Spread <= 0)")
            if active_k > max_active_features:
                pruning_reasons.append(f"Active features count ({active_k}) exceeds ESS-based cap ({max_active_features})")
            if gini > 0.85:
                pruning_reasons.append(f"Gini coefficient ({gini:.4f}) exceeds cap (0.85)")

            if pruning_reasons:
                trial.set_user_attr("pruned_reasons", pruning_reasons)
                trial.set_user_attr("raw_metrics", raw_metrics)
                trial.set_user_attr("val_metrics", val_metrics)
                trial.set_user_attr("gini", gini)
                return -1e9  # Pruned due to constraint violation

            trial.set_user_attr("gini", gini)

            # Soft ESS constraint penalty
            ess_penalty = 0.0
            if ess_pct < 0.20:
                ess_penalty = -10.0 * (0.20 - ess_pct)

            # Normalize selection validation metrics
            norm_val_metrics = []
            for i in range(4):
                n_m = (val_metrics[i] - val_medians[i]) / (val_mads[i] + 1e-10)
                norm_val_metrics.append(n_m)

            # Compute weighted sum on selection validation metrics
            objective_val = (
                0.40 * norm_val_metrics[0] +  # Val Overall IC
                0.40 * norm_val_metrics[1] +  # Val Tail IC
                0.15 * norm_val_metrics[2] +  # Val Monotonicity
                0.05 * norm_val_metrics[3]    # Val Spread
            ) + ess_penalty

            trial.set_user_attr("raw_metrics", raw_metrics)
            trial.set_user_attr("val_metrics", val_metrics)
            return objective_val

        except Exception as e:
            trial.set_user_attr("pruned_reasons", [f"Exception: {str(e)}"])
            return -1e9

    def run_main_trial():
        local_study = optuna.load_study(study_name=f"main_{tag}", storage=main_storage)
        local_study.optimize(main_objective, n_trials=1)

    Parallel(n_jobs=optuna_n_jobs)(
        delayed(run_main_trial)() for _ in range(n_trials)
    )

    timings["main_study"] = time.perf_counter() - t_main_block_start

    study = optuna.load_study(study_name=f"main_{tag}", storage=main_storage)
    
    # Pruning analysis & Diagnostics
    total_trials = len(study.trials)
    pruned_count = 0
    completed_count = 0
    failed_count = 0
    
    reason_counts = {
        "M4 (Overall IC <= 0)": 0,
        "M3 (Hit Rate < 60%)": 0,
        "M5 (Monotonicity <= 0.25)": 0,
        "M6 (Top-Bottom Spread <= 0)": 0,
        "exceeds ESS-based cap": 0,
        "Gini coefficient": 0,
    }
    exception_reasons = []
    
    for t in study.trials:
        if t.state == optuna.trial.TrialState.PRUNED or (t.state == optuna.trial.TrialState.COMPLETE and t.value is not None and t.value <= -1e8):
            pruned_count += 1
            reasons = t.user_attrs.get("pruned_reasons", [])
            if not reasons:
                reasons = ["Unknown / Hard constraint"]
            for r in reasons:
                matched = False
                for key in reason_counts.keys():
                    if key in r:
                        reason_counts[key] += 1
                        matched = True
                        break
                if not matched:
                    if r not in exception_reasons:
                        exception_reasons.append(r)
        elif t.state == optuna.trial.TrialState.COMPLETE:
            completed_count += 1
        elif t.state == optuna.trial.TrialState.FAIL:
            failed_count += 1

    print("\n  [DIAGNOSTICS] Main Optuna Study Trial Summary:")
    print(f"    Total trials run: {total_trials}")
    print(f"    Successful complete trials: {completed_count}")
    print(f"    Pruned/Failed trials: {pruned_count + failed_count}")
    print("    Pruning reason breakdown:")
    for reason, cnt in reason_counts.items():
        print(f"      - {reason}: {cnt} times")
    if exception_reasons:
        print("    Exceptions encountered during trials:")
        for exc in exception_reasons:
            print(f"      - {exc}")

    # Track optimization path / progression
    sorted_trials = sorted(study.trials, key=lambda t: t.number)
    best_value = -1e10
    progression = []
    for t in sorted_trials:
        if t.state == optuna.trial.TrialState.COMPLETE and t.value is not None and t.value > -1e8:
            if t.value > best_value:
                best_value = t.value
                progression.append((t.number, best_value, t.params))

    print("\n  [DIAGNOSTICS] Objective Progression (Optimization path):")
    for step, val, params in progression:
        print(f"    Trial {step:3d}: Best Objective = {val:+.4f} | params = {params}")

    # Retrieve best trial results
    best_trial = study.best_trial
    best_params = best_trial.params
    best_raw_m = best_trial.user_attrs.get("raw_metrics")
    best_val_m = best_trial.user_attrs.get("val_metrics")
    
    if best_raw_m is None:
        print(f"\n[WARNING] All main study trials violated hard constraints for {etf_name}. Searching for best valid trial...")
        valid_trials = [t for t in study.trials if t.user_attrs.get("raw_metrics") is not None]
        if valid_trials:
            valid_trials.sort(key=lambda t: t.value if t.value is not None else -1e10, reverse=True)
            best_trial = valid_trials[0]
            best_params = best_trial.params
            best_raw_m = best_trial.user_attrs.get("raw_metrics")
            best_val_m = best_trial.user_attrs.get("val_metrics")
        else:
            print("[WARNING] No main trials succeeded. Falling back to pilot study's best trial.")
            # Pick pilot record maximizing Val IC + Val Tail IC.
            pilot_valid_sorted = sorted(
                pilot_records,
                key=lambda r: (r["val_metrics"][0] + r["val_metrics"][1]),
                reverse=True,
            )
            if pilot_valid_sorted:
                best_rec = pilot_valid_sorted[0]
                best_params = best_rec["params"]
                best_raw_m = best_rec["raw_metrics"]
                best_val_m = best_rec["val_metrics"]
            else:
                raise RuntimeError("Both main and pilot studies failed to produce any valid trial results.")

    if best_val_m is None:
        best_val_m = [np.nan, np.nan, np.nan, np.nan]

    # Calculate Deflated CV IC and Deflated Objective to adjust for multiple trials (Search-Budget Overfit)
    completed_trials = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE and t.value is not None and t.value > -1e8]
    trial_m4_values = []
    trial_objective_values = []
    trial_val_ic_values = []
    trial_val_tail_ic_values = []
    for t in completed_trials:
        m = t.user_attrs.get("raw_metrics")
        val_m = t.user_attrs.get("val_metrics")
        if m is not None:
            trial_m4_values.append(m[3]) # M4 is index 3
            trial_objective_values.append(t.value)
        if val_m is not None:
            trial_val_ic_values.append(val_m[0])
            trial_val_tail_ic_values.append(val_m[1])

    deflated_cv_ic = compute_deflated_metric(trial_m4_values, best_raw_m[3], rho=0.5)
    deflated_objective = compute_deflated_metric(trial_objective_values, best_trial.value, rho=0.5)
    deflated_val_ic = compute_deflated_metric(trial_val_ic_values, best_val_m[0], rho=0.5)
    deflated_val_tail_ic = compute_deflated_metric(trial_val_tail_ic_values, best_val_m[1], rho=0.5)

    print(f"\nBest hyperparameters found by Optuna:")
    for k, v in best_params.items():
        print(f"  {k}: {v}")
        
    print(f"Best trial raw metrics (CV Folds):")
    print(f"  M1 (Tail IC IR):      {best_raw_m[0]:.4f}")
    print(f"  M2 (Tail IC Mean):    {best_raw_m[1]:.4f}")
    print(f"  M3 (Hit Rate):        {best_raw_m[2]:.4f}")
    print(f"  M4 (Overall IC):      {best_raw_m[3]:.4f}")
    print(f"  Deflated CV Overall IC: {deflated_cv_ic:.4f}")
    print(f"  M5 (Monotonicity):    {best_raw_m[4]:.4f}")
    print(f"  M6 (Top-Bot Spread):  {best_raw_m[5]:.4f}")
    print(f"  M7 (Parsimony):       {best_raw_m[6]:.4f}")
    print(f"  M8 (Coef Bloat):      {best_raw_m[7]:.4f}")

    print(f"Best trial Selection Validation metrics:")
    print(f"  Val Overall IC:       {best_val_m[0]:.4f}")
    print(f"  Deflated Val IC:      {deflated_val_ic:.4f}")
    print(f"  Val Tail IC:          {best_val_m[1]:.4f}")
    print(f"  Deflated Val Tail IC: {deflated_val_tail_ic:.4f}")
    print(f"  Val Monotonicity:     {best_val_m[2]:.4f}")
    print(f"  Val Top-Bot Spread:   {best_val_m[3]:.4f}")
    
    t_refit_start = time.perf_counter()
    # Refit final model on 2200 working rows
    model_type = best_params["model_type"]
    k_weight = best_params["k_weight"]
    
    params = {}
    if model_type == "skglm_huber_l1":
        params["skglm_huber_l1_alpha"] = best_params["skglm_huber_l1_alpha"]
        params["skglm_huber_delta"] = best_params["skglm_huber_delta"]
    elif model_type == "skglm_mcp":
        params["skglm_mcp_alpha"] = best_params["skglm_mcp_alpha"]
        params["skglm_mcp_gamma"] = best_params["skglm_mcp_gamma"]
        params["skglm_mcp_delta"] = best_params["skglm_mcp_delta"]
        
    # Scale final working features
    scaler_final = StandardScaler()
    X_working_scaled = scaler_final.fit_transform(X_working_final)
    
    w_final = compute_sample_weights(y_working, k_weight)
    X_weighted_final, y_weighted_final = scale_data_with_weights(X_working_scaled, y_working, w_final)
    
    final_model = _build_model(model_type, params)
    final_model.fit(X_weighted_final, y_weighted_final)

    # ── Weight Concentration & Effective Sample Size Diagnostics ──
    sum_w = w_final.sum()
    sum_w2 = (w_final ** 2).sum()
    ess = float((sum_w ** 2) / sum_w2) if sum_w2 > 1e-10 else float(len(w_final))
    ess_pct = ess / len(w_final)
    
    abs_coefs = np.abs(final_model.coef_)
    sum_abs = abs_coefs.sum()
    if sum_abs > 1e-10:
        sorted_c = np.sort(abs_coefs)
        m = len(sorted_c)
        index = np.arange(1, m + 1)
        gini = float((2.0 * (index * sorted_c).sum()) / (m * sum_abs) - (m + 1) / m)
    else:
        gini = 0.0

    # L2 regularized condition number computation
    l2_lambda = 0.0
    if model_type == "skglm_huber_l1":
        l2_lambda = best_params["skglm_huber_l1_alpha"] * 0.1
    elif model_type == "skglm_mcp":
        l2_lambda = best_params["skglm_mcp_alpha"] * 0.1
    elif model_type == "elasticnet":
        l2_lambda = best_params["en_alpha"] * (1.0 - best_params["en_l1_ratio"])

    n_samples_working = X_working_final.shape[0]
    X_scaled_tmp = (X_working_final - X_working_final.mean(axis=0)) / (X_working_final.std(axis=0) + 1e-10)
    _, s, _ = np.linalg.svd(X_scaled_tmp, full_matrices=False)
    s_min = s.min()
    raw_cond = float(s.max() / s_min) if s_min > 1e-10 else float("inf")

    s_sq_max = (s.max() ** 2) + n_samples_working * l2_lambda
    s_sq_min = (s.min() ** 2) + n_samples_working * l2_lambda
    reg_cond = float(s_sq_max / s_sq_min) if s_sq_min > 1e-10 else float("inf")

    print("\n  [DIAGNOSTICS] Final Model Diagnostics:")
    print(f"    Effective Sample Size (ESS) under tail-focus: {ess:.1f} / {len(w_final)} ({ess_pct*100:.1f}%)")
    if ess_pct < 0.05:
        print(f"    [WARNING] ESS is extremely low (< 5%)! Model is highly sensitive to a few extreme tail days.")
    elif ess_pct < 0.20:
        print(f"    [WARNING] ESS is low (< 20%). Fit is dominated by tail returns.")
    else:
        print(f"    ESS is healthy.")

    print(f"    Model Weight Concentration (Gini Index): {gini:.4f}")
    if gini > 0.85:
        print(f"    [WARNING] Extremely high weight concentration! A very small subset of features dominates the model.")
    elif gini < 0.15:
        print(f"    [WARNING] Extremely low weight concentration (all weights are near-identical).")
    
    print(f"    Raw Design Matrix Condition Number: {raw_cond:.2f}")
    print(f"    Regularized Normal Equations Condition Number (kappa): {reg_cond:.2f}")
    
    # Save the models/scalers/results to files
    tag = etf_name if side == "single" else f"{etf_name}_{side}"
    
    joblib.dump(final_model, MODELS_DIR / f"linear_{tag}.joblib")
    
    # Save scaler and feature metadata (compatible with deploy.py loader)
    scaler_meta = {
        "scaler": scaler_final,
        "features": FEATURES,
        "selected_features": selected_feature_names,
        "stability_scores": dict(zip(FEATURES, stability_scores.tolist())),
        "best_params": best_params,
        "best_model_type": model_type,
        "holdout_ic": np.nan,
        "holdout_tail_ic": np.nan,
        "deflated_cv_ic": deflated_cv_ic,
        "deflated_val_ic": deflated_val_ic,
        "deflated_val_tail_ic": deflated_val_tail_ic,
        "selection_val_overall_ic": best_val_m[0],
        "selection_val_tail_ic": best_val_m[1],
        "selection_val_monotonicity": best_val_m[2],
        "selection_val_spread": best_val_m[3],
        "side": side,
        "target": TARGET,
    }
    joblib.dump(scaler_meta, MODELS_DIR / f"scaler_{tag}.joblib")
    
    active_idx = np.where(np.abs(final_model.coef_) > 1e-5)[0]
    active_feature_names = [selected_feature_names[i] for i in active_idx]

    timings["final_refit"] = time.perf_counter() - t_refit_start

    print("\n  [DIAGNOSTICS] Execution Time Profiling:")
    for stage, secs in timings.items():
        print(f"    {stage:<20}: {secs:6.1f}s")
    total_time = sum(timings.values())
    print(f"    {'Total Duration':<20}: {total_time:6.1f}s")

    # Save results json
    results = {
        "etf": etf_name,
        "side": side,
        "tag": tag,
        "n_samples_working": len(y_working),
        "n_samples_lockbox": 0,
        "selected_features": selected_feature_names,
        "active_features": active_feature_names,
        "stability_scores": dict(zip(FEATURES, stability_scores.tolist())),
        "best_params": best_params,
        "best_raw_metrics": best_raw_m,
        "selection_val_overall_ic": best_val_m[0],
        "selection_val_tail_ic": best_val_m[1],
        "selection_val_monotonicity": best_val_m[2],
        "selection_val_spread": best_val_m[3],
        "deflated_cv_ic": deflated_cv_ic,
        "deflated_val_ic": deflated_val_ic,
        "deflated_val_tail_ic": deflated_val_tail_ic,
        "deflated_objective": deflated_objective,
        "lockbox_overall_ic": np.nan,
        "lockbox_tail_ic": np.nan,
        "diagnostics": {
            "timings": timings,
            "screening": {
                "total_features": len(FEATURES),
                "bh_pass_count": int(bh_pass_count),
                "fallback_triggered": bool(fallback_triggered),
                "keep_count": int(screen_mask.sum()),
            },
            "stability": {
                "fallback_triggered": bool(stab_fallback_triggered),
                "pass_pi_count": int(pass_pi_count),
                "keep_count": int(len(stability_selected_idx)),
            },
            "optuna_main": {
                "total_trials": int(total_trials),
                "completed_count": int(completed_count),
                "pruned_count": int(pruned_count),
                "failed_count": int(failed_count),
                "pruning_reasons": reason_counts,
            },
            "model_quality": {
                "condition_number": float(reg_cond),
                "condition_number_raw": float(raw_cond),
                "condition_number_regularized": float(reg_cond),
                "collinear_pairs": [[p[0], p[1], float(p[2])] for p in collinear_pairs],
                "effective_sample_size": float(ess),
                "effective_sample_size_pct": float(ess_pct),
                "gini_coefficient": float(gini),
            }
        }
    }
    with open(DATA_DIR / f"results_{tag}.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
        
    # Clean up Optuna log files to save space and keep workspace clean
    try:
        if pilot_db_path.exists():
            pilot_db_path.unlink()
        if main_db_path.exists():
            main_db_path.unlink()
    except Exception as e:
        print(f"  [cache] cleanup warning: {e}")

    return results


class _TeeWriter:
    """Duplicate writes to console and a log file simultaneously."""
    def __init__(self, filepath, stream):
        self._file = open(filepath, "a", encoding="utf-8")
        self._stream = stream
    def write(self, data):
        self._stream.write(data)
        if not self._file.closed:
            self._file.write(data)
            self._file.flush()
    def flush(self):
        self._stream.flush()
        if not self._file.closed:
            self._file.flush()
    def isatty(self):
        return self._stream.isatty()
    def fileno(self):
        return self._stream.fileno()
    def close(self):
        self._file.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="300", help="300|50|500|588000|159915|all")
    ap.add_argument("-t", "--trials", type=int, default=100, help="Optuna trials count")
    ap.add_argument("--side", default="single", choices=["single"])
    ap.add_argument("--no-cache", action="store_true",
                    help="Disable disk caches (selection, LOYO folds, pilot metrics).")
    ap.add_argument("--optuna-jobs", type=int, default=OPTUNA_N_JOBS,
                    help=f"Parallel Optuna workers (default {OPTUNA_N_JOBS}).")
    ap.add_argument("--bootstrap-jobs", type=int, default=BOOTSTRAP_N_JOBS,
                    help=f"Parallel workers for stability bootstrap (default {BOOTSTRAP_N_JOBS}).")
    ap.add_argument("--loyo-jobs", type=int, default=-1,
                    help=("Parallel workers for LOYO fold fits per trial. "
                          "-1 = auto (cpu_count // optuna-jobs). Default -1."))
    ap.add_argument("--log", default=str(HERE / "train_model_log.txt"),
                    help="Path to output log file (default: day-model/train_model_log.txt). "
                         "Pass 'none' to disable.")
    args = ap.parse_args()

    # Set up tee logging: mirror stdout/stderr to log file
    if args.log and args.log.lower() != "none":
        log_path = Path(args.log)
        # Truncate at start of run
        log_path.write_text("", encoding="utf-8")
        sys.stdout = _TeeWriter(log_path, sys.stdout)
        sys.stderr = _TeeWriter(log_path, sys.stderr)

    loyo_jobs_arg = args.loyo_jobs
    if loyo_jobs_arg < 1:
        loyo_jobs_arg = max(1, (os.cpu_count() or 4) // max(1, args.optuna_jobs))

    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]

    print(f"Remade train_model.py execution context initialized.")
    print(f"Target ETFs: {etfs}")
    print(f"Optuna main trials: {args.trials}")
    print(f"Cache: {'OFF' if args.no_cache else 'ON'}  "
          f"optuna_jobs={args.optuna_jobs}  bootstrap_jobs={args.bootstrap_jobs}  "
          f"loyo_jobs={loyo_jobs_arg}")

    for etf in etfs:
        t0 = time.perf_counter()
        try:
            train_etf(etf, n_trials=args.trials, side=args.side,
                      use_cache=not args.no_cache,
                      optuna_n_jobs=args.optuna_jobs,
                      bootstrap_n_jobs=args.bootstrap_jobs,
                      loyo_n_jobs=loyo_jobs_arg)
        except Exception as e:
            print(f"  [ERROR] Failed to train {etf}: {e}")
            import traceback
            traceback.print_exc()
        print(f"[{etf}] elapsed {time.perf_counter() - t0:.1f}s")

    # Close log file handles
    if isinstance(sys.stdout, _TeeWriter):
        sys.stdout.close()
    if isinstance(sys.stderr, _TeeWriter):
        sys.stderr.close()
