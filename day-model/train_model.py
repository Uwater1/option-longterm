"""
Phase 2 Remake: Train Optuna-tuned return prediction model based on first principles.
Implements the 7-step optimization and robust selection plan from day-model_plan.md.
"""
import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso, ElasticNet, HuberRegressor
import optuna
import joblib

# skglm imports
from skglm import GeneralizedLinearEstimator
from skglm.datafits import Huber as SkglmHuber
from skglm.penalties import L1 as SkglmL1, MCPenalty

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

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
    "m1": 0.20,  # Yearly Tail IC IR
    "m2": 0.20,  # Yearly Tail IC Mean
    "m3": 0.15,  # Yearly Hit Rate
    "m4": 0.15,  # Overall Rank IC
    "m5": 0.10,  # Decile Monotonicity
    "m6": 0.05,  # Top-Bottom Spread
    "m7": 0.10,  # Feature Parsimony
    "m8": 0.05,  # Coefficient Bloat
}


# ============================================================
# Model Factory
# ============================================================
def _build_model(model_type: str, params: dict):
    if model_type == "skglm_huber_l1":
        return GeneralizedLinearEstimator(
            datafit=SkglmHuber(delta=params.get("skglm_huber_delta", 1.35)),
            penalty=SkglmL1(alpha=params["skglm_huber_l1_alpha"]),
        )
    elif model_type == "skglm_mcp":
        return GeneralizedLinearEstimator(
            datafit=SkglmHuber(delta=params.get("skglm_mcp_delta", 1.35)),
            penalty=MCPenalty(alpha=params["skglm_mcp_alpha"],
                              gamma=params.get("skglm_mcp_gamma", 3.0)),
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
def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 5 or np.std(y_pred) < 1e-12 or np.std(y_true) < 1e-12:
        return 0.0
    rho, _ = spearmanr(y_pred, y_true)
    return float(rho) if not np.isnan(rho) else 0.0


def compute_decile_monotonicity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    try:
        df["decile"] = pd.qcut(df["y_pred"], 10, labels=False, duplicates="drop")
        decile_means = df.groupby("decile")["y_true"].mean().sort_index()
        if len(decile_means) < 3:
            return 0.0
        rho, _ = spearmanr(decile_means.index, decile_means.values)
        return float(rho) if not np.isnan(rho) else 0.0
    except Exception:
        return 0.0


def compute_top_bottom_spread(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    try:
        df["decile"] = pd.qcut(df["y_pred"], 10, labels=False, duplicates="drop")
        decile_means = df.groupby("decile")["y_true"].mean().sort_index()
        if len(decile_means) < 2:
            return 0.0
        return float(decile_means.iloc[-1] - decile_means.iloc[0])
    except Exception:
        return 0.0


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


def run_screening_and_clustering(X_working: np.ndarray, y_working: np.ndarray, feature_names: list):
    # Step 1: Cheap screening
    p_vals = []
    rhos = []
    for j in range(X_working.shape[1]):
        rho, p_val = spearmanr(X_working[:, j], y_working)
        if np.isnan(p_val):
            p_val = 1.0
            rho = 0.0
        p_vals.append(p_val)
        rhos.append(rho)
    p_vals = np.array(p_vals)
    rhos = np.array(rhos)

    screen_mask = benjamini_hochberg(p_vals, fdr_level=0.20)
    if screen_mask.sum() < 5:
        # Fallback to top 50 by p-value
        top_indices = np.argsort(p_vals)[:50]
        screen_mask = np.zeros(len(p_vals), dtype=bool)
        screen_mask[top_indices] = True

    surviving_idx = np.where(screen_mask)[0]
    X_surviving = X_working[:, surviving_idx]

    # Step 1.5: Hierarchical Clustering
    corr_matrix = np.abs(np.corrcoef(X_surviving.T))
    corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)

    dist_matrix = 1.0 - corr_matrix
    dist_matrix = np.clip(dist_matrix, 0.0, 2.0)

    cond_dist = squareform((dist_matrix + dist_matrix.T) / 2.0, checks=False)
    Z = linkage(cond_dist, method='complete')
    cluster_labels = fcluster(Z, t=0.7, criterion='distance')

    # Keep best feature per cluster
    cluster_selected_idx = []
    for label in np.unique(cluster_labels):
        in_cluster = np.where(cluster_labels == label)[0]
        orig_idx_in_cluster = surviving_idx[in_cluster]
        best_feat = orig_idx_in_cluster[np.argmax(np.abs(rhos[orig_idx_in_cluster]))]
        cluster_selected_idx.append(best_feat)

    cluster_mask = np.zeros(X_working.shape[1], dtype=bool)
    cluster_mask[cluster_selected_idx] = True

    return cluster_mask, p_vals, rhos


def run_stability_selection(X_working: np.ndarray, y_working: np.ndarray, cluster_mask: np.ndarray, B: int = 100, pi: float = 0.60):
    # Step 2: Stability Selection
    cluster_features_idx = np.where(cluster_mask)[0]
    X_cluster = X_working[:, cluster_features_idx]

    scaler = StandardScaler()
    X_cluster_scaled = scaler.fit_transform(X_cluster)

    # Pre-compute alphas grid
    from sklearn.linear_model import lasso_path
    alphas, _, _ = lasso_path(X_cluster_scaled, y_working, n_alphas=50)

    subsample_size = X_working.shape[0] // 2
    selection_matrix = np.zeros((X_cluster.shape[1], len(alphas), B), dtype=bool)

    rng = np.random.default_rng(42)
    for b in range(B):
        sub_idx = rng.choice(X_working.shape[0], size=subsample_size, replace=False)
        X_sub = X_cluster[sub_idx]
        y_sub = y_working[sub_idx]
        
        X_sub_scaled = StandardScaler().fit_transform(X_sub)
        _, coefs, _ = lasso_path(X_sub_scaled, y_sub, alphas=alphas)
        selection_matrix[:, :, b] = (np.abs(coefs) > 1e-5)

    sel_probs = np.mean(selection_matrix, axis=2)
    stability_scores = np.max(sel_probs, axis=1)

    stability_keep = stability_scores >= pi
    if stability_keep.sum() < 3:
        # Fallback to top 5 stability features
        top_idx = np.argsort(stability_scores)[-5:]
        stability_keep = np.zeros_like(stability_keep, dtype=bool)
        stability_keep[top_idx] = True

    stability_selected_idx = cluster_features_idx[stability_keep]
    
    # Store stability score for all FEATURES
    all_stability_scores = np.zeros(X_working.shape[1])
    for local_i, orig_i in enumerate(cluster_features_idx):
        all_stability_scores[orig_i] = stability_scores[local_i]

    return stability_selected_idx, all_stability_scores


# ============================================================
# Yearly Blocked CV Engine
# ============================================================
def run_loyo_cv(X_feat: np.ndarray, y_target: np.ndarray, dates: pd.Series, model_type: str, params: dict, k_weight: float):
    unique_years = sorted(list(set(dates.dt.year.values)))
    oof_preds = np.zeros(len(y_target))
    
    dates_val = dates.values
    for test_year in unique_years:
        test_mask = dates.dt.year == test_year
        test_idx = np.where(test_mask)[0]
        
        # Test boundaries
        test_dates = dates_val[test_mask]
        min_test_date = np.min(test_dates)
        max_test_date = np.max(test_dates)
        
        # Embargo range (10 calendar days buffer around testing block)
        embargo_start = min_test_date - pd.Timedelta(days=10)
        embargo_end = max_test_date + pd.Timedelta(days=10)
        
        train_mask = (dates.dt.year != test_year) & ((dates_val < embargo_start) | (dates_val > embargo_end))
        train_idx = np.where(train_mask)[0]
        
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue
            
        X_tr, y_tr = X_feat[train_idx], y_target[train_idx]
        X_te = X_feat[test_idx]
        
        scaler = StandardScaler()
        X_tr_scaled = scaler.fit_transform(X_tr)
        X_te_scaled = scaler.transform(X_te)
        
        w_tr = compute_sample_weights(y_tr, k_weight)
        X_tr_w, y_tr_w = scale_data_with_weights(X_tr_scaled, y_tr, w_tr)
        
        model = _build_model(model_type, params)
        model.fit(X_tr_w, y_tr_w)
        
        oof_preds[test_idx] = model.predict(X_te_scaled)
        
    return oof_preds


def calculate_yearly_metrics(y_true: np.ndarray, y_pred: np.ndarray, dates: pd.Series, k_features: int, coef_norm: float):
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred, "date": dates})
    df["year"] = df["date"].dt.year
    unique_years = sorted(list(df["year"].unique()))
    
    y_ics = []
    y_tail_ics = []
    y_tail_hits = []
    y_monos = []
    y_spreads = []
    
    for year in unique_years:
        year_df = df[df["year"] == year]
        y_t = year_df["y_true"].values
        y_p = year_df["y_pred"].values
        
        # 1. Overall IC
        ic = spearman_ic(y_t, y_p)
        y_ics.append(ic)
        
        # 2. Tail IC (top/bottom 10%)
        n_tail = max(5, int(len(y_p) * 0.10))
        if len(y_p) >= n_tail * 2:
            top_idx = np.argsort(y_p)[-n_tail:]
            bot_idx = np.argsort(y_p)[:n_tail]
            tail_idx = np.concatenate([bot_idx, top_idx])
            tail_ic = spearman_ic(y_t[tail_idx], y_p[tail_idx])
        else:
            tail_ic = 0.0
        y_tail_ics.append(tail_ic)
        
        # 3. Yearly Hit Rate indicator
        y_tail_hits.append(1.0 if tail_ic > 0 else 0.0)
        
        # 4. Decile Monotonicity
        mono = compute_decile_monotonicity(y_t, y_p)
        y_monos.append(mono)
        
        # 5. Top-Bottom Spread
        spread = compute_top_bottom_spread(y_t, y_p)
        y_spreads.append(spread)
        
    y_ics = np.array(y_ics)
    y_tail_ics = np.array(y_tail_ics)
    y_tail_hits = np.array(y_tail_hits)
    y_monos = np.array(y_monos)
    y_spreads = np.array(y_spreads)
    
    mean_tail_ic = np.mean(y_tail_ics)
    std_tail_ic = np.std(y_tail_ics)
    
    m1 = mean_tail_ic / (std_tail_ic + 1e-10)     # Yearly Tail IC IR
    m2 = mean_tail_ic                             # Yearly Tail IC Mean
    m3 = np.mean(y_tail_hits)                     # Yearly Hit Rate
    m4 = np.mean(y_ics)                           # Overall Rank IC
    m5 = np.mean(y_monos)                         # Decile Monotonicity
    m6 = np.mean(y_spreads)                       # Top-Bottom Spread
    m7 = -np.log(1.0 + k_features)                # Feature Parsimony (penalized)
    m8 = -coef_norm                               # Coefficient Bloat (penalized)
    
    raw_metrics = [m1, m2, m3, m4, m5, m6, m7, m8]
    return raw_metrics, unique_years, y_tail_ics


# ============================================================
# Main ETF Trainer
# ============================================================
def train_etf(etf_name: str, n_trials: int = 50, side: str = "single"):
    print(f"\n" + "=" * 80)
    print(f"Starting First-Principles Training for {etf_name} (Side: {side})")
    print(f"=" * 80)
    
    # Load features parquet
    features_path = DATA_DIR / f"features_{etf_name}.parquet"
    if not features_path.exists():
        print(f"  [ERROR] Features file not found: {features_path}")
        return None
        
    df = pd.read_parquet(features_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    
    # Handle NaNs in features
    X_df = df[FEATURES].ffill().fillna(df[FEATURES].median())
    X = X_df.values
    y = df[TARGET].values
    
    N = len(df)
    print(f"Loaded {N} samples and {X.shape[1]} features.")
    
    # Target scaling (consistent with old pipeline target scaling)
    # trade_return values are typically small log-returns, so we scale by 100.0
    y_scaled = y * 100.0
    
    # Step 0: Lockout split by date (working: before 2024-03-01, lockbox: 2024-03-01 onwards)
    working_mask = df["date"] < "2024-03-01"
    lockbox_mask = df["date"] >= "2024-03-01"
    working_idx = np.where(working_mask)[0]
    lockbox_idx = np.where(lockbox_mask)[0]
    
    X_working = X[working_idx]
    y_working = y_scaled[working_idx]
    dates_working = df["date"].iloc[working_idx].reset_index(drop=True)
    
    X_lockbox = X[lockbox_idx]
    y_lockbox = y_scaled[lockbox_idx]
    dates_lockbox = df["date"].iloc[lockbox_idx].reset_index(drop=True)
    
    print(f"Split: Working={len(working_idx)} rows, Lockbox={len(lockbox_idx)} rows.")
    
    # Step 1 & 1.5: Cheap screening & Hierarchical Feature Clustering
    print("Running feature screening and clustering...")
    cluster_mask, p_vals, rhos = run_screening_and_clustering(X_working, y_working, FEATURES)
    print(f"Screened and clustered features: {cluster_mask.sum()} surviving cluster candidates.")
    
    # Step 2: Stability Selection on the survivors
    print("Running stability selection...")
    stability_selected_idx, stability_scores = run_stability_selection(X_working, y_working, cluster_mask, B=100, pi=0.60)
    
    selected_feature_names = [FEATURES[idx] for idx in stability_selected_idx]
    K_sel = len(stability_selected_idx)
    print(f"Stability selection finished. Kept {K_sel} features: {selected_feature_names}")
    
    # Freeze the features for the final and Optuna loops
    X_working_final = X_working[:, stability_selected_idx]
    X_lockbox_final = X_lockbox[:, stability_selected_idx]
    
    # We fit a ridge model or baseline once to compute scaling factors or norms
    scaler_init = StandardScaler()
    X_working_scaled_init = scaler_init.fit_transform(X_working_final)
    
    # Define Optuna objective helper
    # We must collect pilot run metrics to compute robust z-score normalizations
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
        oof_preds = run_loyo_cv(X_working_final, y_working, dates_working, model_type, params, k_weight)
        
        # Fit final model on working set to compute coefficient norm
        # We reuse the same scaling logic
        scaler_temp = StandardScaler()
        X_working_scaled_temp = scaler_temp.fit_transform(X_working_final)
        w_temp = compute_sample_weights(y_working, k_weight)
        X_weighted_temp, y_weighted_temp = scale_data_with_weights(X_working_scaled_temp, y_working, w_temp)
        
        model_temp = _build_model(model_type, params)
        model_temp.fit(X_weighted_temp, y_weighted_temp)
        
        coef_norm = float(np.linalg.norm(model_temp.coef_))
        
        # Calculate raw yearly metrics
        raw_metrics, _, _ = calculate_yearly_metrics(y_working, oof_preds, dates_working, K_sel, coef_norm)
        return raw_metrics, model_temp, scaler_temp
        
    # Phase 1: Pilot Run (50 trials) to gather MAD metrics
    print("\nRunning Optuna Pilot Study (50 trials) for normalization calibration...")
    pilot_study = optuna.create_study(direction="maximize")
    
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
            # Objective in pilot: simple average of Tail IC Mean (M2) and Overall Rank IC (M4)
            return raw_metrics[1] + raw_metrics[3]
        except Exception as e:
            import traceback
            print(f"Pilot trial failed: {e}")
            traceback.print_exc()
            return -999.0
            
    pilot_study.optimize(pilot_objective, n_trials=50)
    
    # Gather pilot results
    for t in pilot_study.trials:
        if t.state == optuna.trial.TrialState.COMPLETE:
            raw_m = t.user_attrs.get("raw_metrics")
            if raw_m:
                pilot_metrics.append(raw_m)
                
    if len(pilot_metrics) == 0:
        raise RuntimeError("Optuna pilot run failed entirely. Check skglm model fit/installation.")
        
    pilot_metrics = np.array(pilot_metrics)
    
    # Compute median and MAD per metric
    medians = np.median(pilot_metrics, axis=0)
    mads = np.median(np.abs(pilot_metrics - medians), axis=0)
    # Avoid zero division
    mads[mads < 1e-6] = 1.0
    
    print("Normalizing constants calibrated from Pilot run:")
    for i in range(8):
        print(f"  M{i+1}: Median={medians[i]:.6f}, MAD={mads[i]:.6f}")
        
    # Phase 2: Main Study (Optuna Tuning)
    print(f"\nRunning main Optuna Study ({n_trials} trials) with First-Principles Multi-Metric Objective...")
    study = optuna.create_study(direction="maximize")
    
    best_raw_metrics = None
    best_model_obj = None
    best_scaler_obj = None
    
    def main_objective(trial):
        nonlocal best_raw_metrics, best_model_obj, best_scaler_obj
        
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
            raw_metrics, model_obj, scaler_obj = evaluate_params(trial_params)
            
            # Extract metrics for kill switches
            m1, m2, m3, m4, m5, m6, m7, m8 = raw_metrics
            
            # Hard Constraints / Kill Switches:
            # 1. Overall IC > 0 (M4 > 0)
            # 2. Minimum Hit Rate >= 60% (M3 >= 0.60)
            # 3. Decile Monotonicity > 0.4 (M5 > 0.4)
            # 4. Feature count ∈ [3, 50] (already frozen and satisfied since K_sel is checked)
            # 5. Top-Bottom Spread > 0 (M6 > 0)
            if m4 <= 0 or m3 < 0.60 or m5 <= 0.4 or m6 <= 0:
                return -1e9 # Pruned due to constraint violation
                
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
            
            # Track best models manually since trial objects don't store objects
            trial.set_user_attr("raw_metrics", raw_metrics)
            return objective_val
            
        except Exception as e:
            return -1e9
            
    study.optimize(main_objective, n_trials=n_trials)
    
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
            pilot_valid = [t for t in pilot_study.trials if t.user_attrs.get("raw_metrics") is not None]
            if pilot_valid:
                pilot_valid.sort(key=lambda t: t.value if t.value is not None else -1e10, reverse=True)
                best_trial = pilot_valid[0]
                best_params = best_trial.params
                best_raw_m = best_trial.user_attrs.get("raw_metrics")
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
    
    # Step 6: One-shot evaluation on 500 holdout lockbox
    X_lockbox_scaled = scaler_final.transform(X_lockbox_final)
    preds_lockbox = final_model.predict(X_lockbox_scaled)
    
    lockbox_ic = spearman_ic(y_lockbox, preds_lockbox)
    
    n_tail_lock = max(5, int(len(y_lockbox) * 0.10))
    top_idx_lock = np.argsort(preds_lockbox)[-n_tail_lock:]
    bot_idx_lock = np.argsort(preds_lockbox)[:n_tail_lock]
    tail_idx_lock = np.concatenate([bot_idx_lock, top_idx_lock])
    lockbox_tail_ic = spearman_ic(y_lockbox[tail_idx_lock], preds_lockbox[tail_idx_lock])
    
    print(f"\n=== ONE-SHOT LOCKBOX EVALUATION ===")
    print(f"  Lockbox Size:       {len(y_lockbox)} days")
    print(f"  Lockbox Overall IC: {lockbox_ic:.4f}")
    print(f"  Lockbox Tail IC:    {lockbox_tail_ic:.4f}")
    print(f"====================================")
    
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
        "holdout_ic": lockbox_ic,
        "holdout_tail_ic": lockbox_tail_ic,
        "side": side,
        "target": TARGET,
    }
    joblib.dump(scaler_meta, MODELS_DIR / f"scaler_{tag}.joblib")
    
    # Save results json
    results = {
        "etf": etf_name,
        "side": side,
        "tag": tag,
        "n_samples_working": len(y_working),
        "n_samples_lockbox": len(y_lockbox),
        "selected_features": selected_feature_names,
        "stability_scores": dict(zip(FEATURES, stability_scores.tolist())),
        "best_params": best_params,
        "best_raw_metrics": best_raw_m,
        "lockbox_overall_ic": lockbox_ic,
        "lockbox_tail_ic": lockbox_tail_ic,
    }
    with open(DATA_DIR / f"results_{tag}.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
        
    # Generate diagnostic plots
    _plot_diagnostics(tag, dates_lockbox, y_lockbox, preds_lockbox, final_model.coef_, selected_feature_names)
    
    return results


def _plot_diagnostics(tag, dates, y_true, y_pred, coefs, feature_names):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Feature coefficients
    ax1 = axes[0]
    # Sort coefficients by absolute value
    sort_idx = np.argsort(np.abs(coefs))
    sorted_coefs = coefs[sort_idx]
    sorted_feats = [feature_names[i] for i in sort_idx]
    
    ax1.barh(sorted_feats, sorted_coefs, color="royalblue")
    ax1.set_title("Model Coefficients")
    ax1.axvline(0, color="gray", linestyle="--")
    
    # Plot 2: Decile actual vs prediction
    ax2 = axes[1]
    df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    df["decile"] = pd.qcut(df["y_pred"], 10, labels=False, duplicates="drop")
    decile_means = df.groupby("decile")["y_true"].mean() * 100 # % return
    
    ax2.bar(decile_means.index + 1, decile_means.values, color="teal")
    ax2.set_xlabel("Predicted Decile (1=Low, 10=High)")
    ax2.set_ylabel("Mean Actual return (%)")
    ax2.set_title("Decile Performance Spread")
    ax2.set_xticks(range(1, 11))
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"diagnostics_{tag}.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="300", help="300|50|500|588000|159915|all")
    ap.add_argument("-t", "--trials", type=int, default=50, help="Optuna trials count")
    ap.add_argument("--side", default="single", choices=["single"])
    args = ap.parse_args()
    
    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]
        
    print(f"Remade train_model.py execution context initialized.")
    print(f"Target ETFs: {etfs}")
    print(f"Optuna main trials: {args.trials}")
    
    for etf in etfs:
        try:
            train_etf(etf, n_trials=args.trials, side=args.side)
        except Exception as e:
            print(f"  [ERROR] Failed to train {etf}: {e}")
            import traceback
            traceback.print_exc()
