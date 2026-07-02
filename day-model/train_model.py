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

LOCKBOX_DATE = "2024-03-01"
PILOT_N_TRIALS = 50
PILOT_SEED = 42
STABILITY_B = 100
STABILITY_PI = 0.60
STABILITY_Q = 35
SCREEN_FDR = 0.40
SCREEN_FALLBACK_K = 50 # Doublc Research this 

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
# Model Factory
# ============================================================
def _build_model(model_type: str, params: dict):
    solver = AndersonCD(max_epochs=2000, tol=1e-3)
    if model_type == "skglm_huber_l1":
        return GeneralizedLinearEstimator(
            datafit=SkglmHuber(delta=params.get("skglm_huber_delta", 1.35)),
            penalty=SkglmL1(alpha=params["skglm_huber_l1_alpha"]),
            solver=solver,
        )
    elif model_type == "skglm_mcp":
        return GeneralizedLinearEstimator(
            datafit=SkglmHuber(delta=params.get("skglm_mcp_delta", 1.35)),
            penalty=MCPenalty(alpha=params["skglm_mcp_alpha"],
                               gamma=params.get("skglm_mcp_gamma", 3.0)),
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


def run_stability_selection(X_working: np.ndarray, y_working: np.ndarray, screen_mask: np.ndarray,
                            B: int = STABILITY_B, pi: float = STABILITY_PI,
                            n_jobs: int = BOOTSTRAP_N_JOBS):
    # Step 2: Stability Selection
    screened_features_idx = np.where(screen_mask)[0]
    X_screened = X_working[:, screened_features_idx]

    scaler = StandardScaler()
    X_cluster_scaled = scaler.fit_transform(X_screened)

    alphas, _, _ = enet_path(X_cluster_scaled, y_working, l1_ratio=0.5, n_alphas=50)
    alphas = _to_f32(alphas)

    n_total = X_working.shape[0]
    subsample_size = n_total // 2
    n_screened = X_screened.shape[1]

    # Parallelize the B bootstrap fits across cores. The original code seeded
    # a single default_rng(42) and called .choice sequentially; we preserve
    # that exact per-bootstrap RNG stream by deriving seeds 42+b from base.
    base_seed = 42
    slices = Parallel(n_jobs=n_jobs, backend="loky")(
        delayed(_stability_one_bootstrap)(
            b, X_screened, y_working, alphas, n_total, subsample_size, base_seed
        )
        for b in range(B)
    )
    selection_matrix = np.stack(slices, axis=2)  # (n_screened, n_alphas, B)

    sel_probs = np.mean(selection_matrix, axis=2)
    
    # Restrict alphas to those that select at most STABILITY_Q features on average
    expected_active = sel_probs.sum(axis=0)
    valid_alphas_idx = np.where(expected_active <= STABILITY_Q)[0]
    if len(valid_alphas_idx) == 0:
        valid_alphas_idx = np.array([0])
        
    stability_scores = np.max(sel_probs[:, valid_alphas_idx], axis=1)

    stability_keep = stability_scores >= pi
    if stability_keep.sum() < 3:
        full_stability_scores = np.max(sel_probs, axis=1)
        top_idx = np.argsort(full_stability_scores)[-5:]
        stability_keep = np.zeros_like(stability_keep, dtype=bool)
        stability_keep[top_idx] = True
        stability_scores = full_stability_scores

    stability_selected_idx = screened_features_idx[stability_keep]

    all_stability_scores = np.zeros(X_working.shape[1])
    for local_i, orig_i in enumerate(screened_features_idx):
        all_stability_scores[orig_i] = stability_scores[local_i]

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
    oof_preds = np.zeros(n_samples, dtype=np.float64)
    if n_jobs and n_jobs > 1 and len(loyo_folds) > 1:
        results = Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(_loyo_one_fold)(f, model_type, params, k_weight)
            for f in loyo_folds
        )
        for test_idx, preds in results:
            oof_preds[test_idx] = preds
    else:
        for fold in loyo_folds:
            test_idx, preds = _loyo_one_fold(fold, model_type, params, k_weight)
            oof_preds[test_idx] = preds
    return oof_preds


def calculate_yearly_metrics(year_groups, y_true: np.ndarray, y_pred: np.ndarray,
                             k_features: int, coef_norm: float):
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
    m7 = -np.log(1.0 + k_features)                # Feature Parsimony (penalized)
    m8 = -coef_norm                               # Coefficient Bloat (penalized)

    raw_metrics = [m1, m2, m3, m4, m5, m6, m7, m8]
    return raw_metrics, [_y for _y, _ in year_groups], y_tail_ics


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

    print(f"Split: Working={len(working_idx)} rows (Lockbox OOS data ignored during training).")

    # Precompute yearly row-index groups (used by per-trial metric computation).
    years_working = dates_working.dt.year.values
    year_groups = [(int(y), np.where(years_working == y)[0])
                   for y in sorted(np.unique(years_working))]

    timings["data_loading"] = time.perf_counter() - t_start

    # ── Cache key parts ───────────────────────────────────────────────
    # Auto-invalidate when: feature parquet regen (mtime), FEATURES list
    # length changes, or any of the deterministic knobs below change.
    # See AGENTS.md "Cache invalidation" for manual-clear guidance.
    select_key = [
        "v2", etf_name, len(FEATURES), int(parquet_mtime),
        int(X_working.shape[0]), int(X_working.shape[1]),
        STABILITY_B, STABILITY_PI, SCREEN_FDR, SCREEN_FALLBACK_K,
        LOCKBOX_DATE, TARGET,
    ]
    select_cache_path = CACHE_DIR / f"cache_select_{etf_name}_{_cache_key(select_key)}.joblib"

    # Step 1 + 2: Cheap screening + Stability selection (cached).
    def _compute_selection():
        t_sel_start = time.perf_counter()
        print("Running feature screening...")
        screen_mask, p_vals, rhos = run_screening(X_working, y_working)
        t_screen = time.perf_counter() - t_sel_start
        print(f"Screened features: {screen_mask.sum()} surviving candidates.")
        
        t_stab_start = time.perf_counter()
        print("Running stability selection...")
        stability_selected_idx, stability_scores = run_stability_selection(
            X_working, y_working, screen_mask,
            B=STABILITY_B, pi=STABILITY_PI, n_jobs=bootstrap_n_jobs,
        )
        t_stab = time.perf_counter() - t_stab_start
        return {
            "screen_mask": screen_mask,
            "p_vals": p_vals,
            "rhos": rhos,
            "stability_selected_idx": np.asarray(stability_selected_idx),
            "stability_scores": np.asarray(stability_scores),
            "time_screen": t_screen,
            "time_stability": t_stab,
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
    X_working_final = _to_f32(X_working[:, stability_selected_idx])

    # ── LOYO folds cache (depends on selected features only) ──────────
    loyo_key = [
        "v2", etf_name, len(FEATURES), int(parquet_mtime),
        tuple(int(i) for i in stability_selected_idx),
        LOCKBOX_DATE, TARGET,
    ]
    loyo_cache_path = CACHE_DIR / f"cache_loyo_{etf_name}_{_cache_key(loyo_key)}.joblib"

    def _compute_loyo():
        folds = []
        unique_years = sorted(list(set(dates_working.dt.year.values)))
        dates_val = dates_working.values
        for test_year in unique_years:
            test_mask = dates_working.dt.year == test_year
            test_idx = np.where(test_mask)[0]

            test_dates = dates_val[test_mask]
            min_test_date = np.min(test_dates)
            max_test_date = np.max(test_dates)

            embargo_start = min_test_date - pd.Timedelta(days=10)
            embargo_end = max_test_date + pd.Timedelta(days=10)

            train_mask = (dates_working.dt.year != test_year) & ((dates_val < embargo_start) | (dates_val > embargo_end))
            train_idx = np.where(train_mask)[0]

            if len(train_idx) == 0 or len(test_idx) == 0:
                continue

            X_tr, y_tr = X_working_final[train_idx], y_working[train_idx]
            X_te = X_working_final[test_idx]

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
        test_years = dates_working.iloc[test_idx].dt.year.unique()
        print(f"      Fold {i+1}: Test Year(s) = {list(test_years)}, Train shape = {X_tr_scaled.shape}, Test shape = {X_te_scaled.shape}")

    # Precompute the *unweighted* standardized full-working matrix once.
    # Per-trial cost only requires re-applying row-wise sqrt(w).
    scaler_init = StandardScaler()
    X_working_scaled_base = _to_f32(scaler_init.fit_transform(X_working_final))

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
                                len(y_working), n_jobs=loyo_n_jobs)

        # Fit final model on working set to compute coefficient norm.
        # Reuse precomputed standardized matrix; only apply sqrt(w) per trial.
        w_temp = compute_sample_weights(y_working, k_weight).astype(np.float32)
        sqrt_w = np.sqrt(w_temp)[:, np.newaxis]
        X_weighted_temp = X_working_scaled_base * sqrt_w
        y_weighted_temp = y_working * sqrt_w[:, 0]

        model_temp = _build_model(model_type, params)
        model_temp.fit(X_weighted_temp, y_weighted_temp)

        coef_norm = float(np.linalg.norm(model_temp.coef_))
        active_k = int(np.sum(np.abs(model_temp.coef_) > 1e-5))

        # Calculate raw yearly metrics
        raw_metrics, _, _ = calculate_yearly_metrics(
            year_groups, y_working, oof_preds, active_k, coef_norm)
        return raw_metrics, model_temp, scaler_init

    # ── Pilot calibration cache ───────────────────────────────────────
    pilot_key = [
        "v2", etf_name, len(FEATURES), int(parquet_mtime),
        tuple(int(i) for i in stability_selected_idx),
        LOCKBOX_DATE, TARGET, PILOT_N_TRIALS, PILOT_SEED,
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
                raw_metrics, _, _ = evaluate_params(trial_params)
                trial.set_user_attr("raw_metrics", raw_metrics)
                trial.set_user_attr("params", trial_params)
                # Objective in pilot: simple average of Tail IC Mean (M2) and Overall Rank IC (M4)
                return raw_metrics[1] + raw_metrics[3]
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
                params = t.user_attrs.get("params")
                if raw_m is not None and params is not None:
                    pilot_records.append({"params": params, "raw_metrics": raw_m})
        return pilot_records

    t_pilot_block_start = time.perf_counter()
    pilot_records = _load_or_compute(pilot_cache_path, pilot_key, _compute_pilot,
                                     use_cache=use_cache)
    timings["pilot_study"] = time.perf_counter() - t_pilot_block_start

    if len(pilot_records) == 0:
        raise RuntimeError("Optuna pilot run failed entirely. Check skglm model fit/installation.")

    pilot_metrics = np.array([r["raw_metrics"] for r in pilot_records])

    # Compute median and MAD per metric
    medians = np.median(pilot_metrics, axis=0)
    mads = np.median(np.abs(pilot_metrics - medians), axis=0)
    # Avoid zero division
    mads[mads < 1e-6] = 1.0

    print("\n  [DIAGNOSTICS] Optuna Pilot Study Details:")
    print(f"    Total pilot trials loaded/run: {len(pilot_records)}")
    print("    Raw metrics distribution across pilot study:")
    metric_names = ["M1 (Tail IC IR)", "M2 (Tail IC Mean)", "M3 (Hit Rate)", "M4 (Overall IC)", 
                    "M5 (Monotonicity)", "M6 (Top-Bot Spread)", "M7 (Parsimony)", "M8 (Coef Bloat)"]
    for i in range(8):
        vals = pilot_metrics[:, i]
        print(f"      {metric_names[i]:<20}: Min = {vals.min():.4f}, Median = {medians[i]:.4f}, Max = {vals.max():.4f}, MAD = {mads[i]:.4f}")

    print("Normalizing constants calibrated from Pilot run:")
    for i in range(8):
        print(f"  M{i+1}: Median={medians[i]:.6f}, MAD={mads[i]:.6f}")

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
            raw_metrics, _model_obj, _scaler_obj = evaluate_params(trial_params)

            # Extract metrics for kill switches
            m1, m2, m3, m4, m5, m6, m7, m8 = raw_metrics

            # Hard Constraints / Kill Switches:
            pruning_reasons = []
            if m4 <= 0:
                pruning_reasons.append("M4 (Overall IC <= 0)")
            if m3 < 0.60:
                pruning_reasons.append("M3 (Hit Rate < 60%)")
            if m5 <= 0.25:
                pruning_reasons.append("M5 (Monotonicity <= 0.25)")
            if m6 <= 0:
                pruning_reasons.append("M6 (Top-Bottom Spread <= 0)")

            if pruning_reasons:
                trial.set_user_attr("pruned_reasons", pruning_reasons)
                trial.set_user_attr("raw_metrics", raw_metrics)
                return -1e9  # Pruned due to constraint violation

            # Normalize metrics
            norm_metrics = []
            for i in range(8):
                n_m = (raw_metrics[i] - medians[i]) / (mads[i] + 1e-10)
                norm_metrics.append(n_m)

            # Compute weighted sum
            objective_val = (
                METRIC_WEIGHTS["m1"] * norm_metrics[0] +
                METRIC_WEIGHTS["m2"] * norm_metrics[1] +
                METRIC_WEIGHTS["m3"] * norm_metrics[2] +
                METRIC_WEIGHTS["m4"] * norm_metrics[3] +
                METRIC_WEIGHTS["m5"] * norm_metrics[4] +
                METRIC_WEIGHTS["m6"] * norm_metrics[5] +
                METRIC_WEIGHTS["m7"] * norm_metrics[6] +
                METRIC_WEIGHTS["m8"] * norm_metrics[7]
            )

            trial.set_user_attr("raw_metrics", raw_metrics)
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
    }
    exception_reasons = []
    
    for t in study.trials:
        if t.state == optuna.trial.TrialState.PRUNED or (t.state == optuna.trial.TrialState.COMPLETE and t.value is not None and t.value <= -1e8):
            pruned_count += 1
            reasons = t.user_attrs.get("pruned_reasons", [])
            if not reasons:
                reasons = ["Unknown / Hard constraint"]
            for r in reasons:
                if r in reason_counts:
                    reason_counts[r] += 1
                else:
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
    
    if best_raw_m is None:
        print(f"\n[WARNING] All main study trials violated hard constraints for {etf_name}. Searching for best valid trial...")
        valid_trials = [t for t in study.trials if t.user_attrs.get("raw_metrics") is not None]
        if valid_trials:
            valid_trials.sort(key=lambda t: t.value if t.value is not None else -1e10, reverse=True)
            best_trial = valid_trials[0]
            best_params = best_trial.params
            best_raw_m = best_trial.user_attrs.get("raw_metrics")
        else:
            print("[WARNING] No main trials succeeded. Falling back to pilot study's best trial.")
            # Pick pilot record maximizing M2+M4 (pilot objective).
            pilot_valid_sorted = sorted(
                pilot_records,
                key=lambda r: (r["raw_metrics"][1] + r["raw_metrics"][3]),
                reverse=True,
            )
            if pilot_valid_sorted:
                best_rec = pilot_valid_sorted[0]
                best_params = best_rec["params"]
                best_raw_m = best_rec["raw_metrics"]
            else:
                raise RuntimeError("Both main and pilot studies failed to produce any valid trial results.")

    print(f"\nBest hyperparameters found by Optuna:")
    for k, v in best_params.items():
        print(f"  {k}: {v}")
        
    print(f"Best trial raw metrics:")
    print(f"  M1 (Tail IC IR):      {best_raw_m[0]:.4f}")
    print(f"  M2 (Tail IC Mean):    {best_raw_m[1]:.4f}")
    print(f"  M3 (Hit Rate):        {best_raw_m[2]:.4f}")
    print(f"  M4 (Overall IC):      {best_raw_m[3]:.4f}")
    print(f"  M5 (Monotonicity):    {best_raw_m[4]:.4f}")
    print(f"  M6 (Top-Bot Spread):  {best_raw_m[5]:.4f}")
    print(f"  M7 (Parsimony):       {best_raw_m[6]:.4f}")
    print(f"  M8 (Coef Bloat):      {best_raw_m[7]:.4f}")
    
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
    ap.add_argument("-t", "--trials", type=int, default=50, help="Optuna trials count")
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
