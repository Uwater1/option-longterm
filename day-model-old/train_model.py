"""
Phase 2: Train Optuna-tuned sparse/robust linear regression predicting trade_return per ETF.
Tunes skglm models (skglm_huber_l1, skglm_mcp) via hyperparameter optimization.
Uses Unified Time-Series Stability Selection (regime-stratified bootstrap, randomized ElasticNet, OOB IC) to select robust feature subsets,
and tunes the selection threshold as a walk-forward CV hyperparameter.

Target: trade_return = log(close[EXIT_BAR] / open[decision_bar+1])
        Mirrors actual daytrade P&L (entry at next-bar open after decision, exit at 14:30 close).

Validation: Purged TimeSeriesSplit walk-forward (gap=N between train and test).
Optuna objective: mean Spearman rank IC across folds (robust to outliers).

Outputs:
  - models/linear_{ETF}.joblib                     (trained best linear model, full data)
  - models/scaler_{ETF}.joblib                     (StandardScaler + features metadata)
  - data/results_{ETF}.json                        (all metrics + diagnostics)
  - data/optuna_study_{ETF}.sqlite3                (Optuna history)
  - plots/{diagnostic}_{ETF}.png

Usage:
    python train_model.py -e all                   # full run, CPU, n_trials=100
    python train_model.py -e 300 --trials 100      # custom trials
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
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge, Lasso, ElasticNet, HuberRegressor, LassoCV, ElasticNetCV
from sklearn.inspection import permutation_importance
import optuna
import joblib
from joblib import Parallel, delayed

# skglm: L1-regularized Huber, MCP, SCAD penalties (not available in sklearn)
from skglm import GeneralizedLinearEstimator
from skglm.datafits import Huber as SkglmHuber
from skglm.penalties import L1 as SkglmL1, MCPenalty

SKGLM_MODEL_TYPES = {"skglm_huber_l1", "skglm_mcp"}

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

ETF_CLI_MAP = {
    "300": "300ETF", "50": "50ETF", "500": "500ETF",
    "588000": "588000ETF", "159915": "159915ETF",
    "300ETF": "300ETF", "50ETF": "50ETF", "500ETF": "500ETF",
    "588000ETF": "588000ETF", "159915ETF": "159915ETF",
    "all": ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"],
}

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns (imported from build_features.py)
import sys
sys.path.append(str(Path(__file__).resolve().parent))
from build_features import EARLY_FEATURES, DAY_FEATURES, YESTERDAY_FEATURES, FEATURES
TARGET = "trade_return"

# Defaults
DEFAULT_TRIALS = 50          # Phase-3: lowered from 100 to curb Optuna selection bias
DEFAULT_N_SPLITS = 5
DEFAULT_PURGE_GAP = 5
HOLDOUT_FRACTION = 0.20      # last 20% of data is the final OOS holdout
BLOCK_SIZE = 20              # Block bootstrap contiguous length (approx 1 calendar month)
N_BOOTSTRAPS = 50            # Number of bootstrap trials for stability selection
Y_SCALE = 100.0              # target scaling (raw trade_return * 100)

# Nested-CV (honest OOS) defaults — Phase-3 overfit controls
DEFAULT_NESTED_SPLITS = 5    # outer walk-forward folds
DEFAULT_INNER_SPLITS = 3     # inner Optuna CV folds (kept small for speed)
DEFAULT_INNER_TRIALS = 20    # Optuna trials inside each outer fold
DEFAULT_INNER_BOOTSTRAPS = 25  # stability-selection bootstraps per outer fold
DEFAULT_SMALL_N = 1500       # below this, tighter top_k cap

# Combinatorial Purged CV (López de Prado) — multi-path OOS estimate
DEFAULT_CPCV_GROUPS = 8      # split timeline into N groups
DEFAULT_CPCV_TEST_GROUPS = 2 # number of contiguous test groups per path

# Locked split registry — keeps dev/holdout boundary stable across re-runs
LOCK_FILE = DATA_DIR / "locked_splits.json"


# ============================================================
# Model factory (skglm unified — sklearn kept for legacy model loading)
# ============================================================
# Optuna searches ONLY these two types; sklearn types retained in
# _build_model() solely for loading previously-trained models.
_OPTUNA_MODEL_TYPES = ["skglm_huber_l1", "skglm_mcp"]


def _build_model(model_type: str, params: dict):
    """Instantiate a linear model from type string + params dict.

    Supported types: ridge, lasso, elasticnet, huber (sklearn),
    skglm_huber_l1 (Huber datafit + L1 penalty),
    skglm_mcp (Quadratic datafit + MCP penalty).
    """
    if model_type == "ridge":
        return Ridge(alpha=params["ridge_alpha"], random_state=42)
    elif model_type == "lasso":
        return Lasso(alpha=params["lasso_alpha"], random_state=42,
                     max_iter=5000, tol=1e-3)
    elif model_type == "elasticnet":
        return ElasticNet(alpha=params["en_alpha"],
                          l1_ratio=params["en_l1_ratio"],
                          random_state=42, max_iter=5000, tol=1e-3)
    elif model_type == "huber":
        return HuberRegressor(alpha=params["huber_alpha"],
                              epsilon=params["huber_epsilon"],
                              max_iter=2000)
    elif model_type == "skglm_huber_l1":
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
    else:
        raise ValueError(f"Unknown model_type: {model_type!r}")


def _safe_fit(model, X, y, sample_weight=None):
    """Fit model, skipping sample_weight for skglm (not supported)."""
    if isinstance(model, GeneralizedLinearEstimator):
        model.fit(X, y)
    elif sample_weight is not None:
        model.fit(X, y, sample_weight=sample_weight)
    else:
        model.fit(X, y)
    return model


# ============================================================
# Purged TimeSeriesSplit
# ============================================================
def purged_tssplit(n: int, n_splits: int, gap: int):
    """Yield (train_idx, test_idx) for expanding-window walk-forward with a purge gap.

    Train is [0, t_end]; test is [t_end + gap, t_end + gap + test_size].
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    for train_idx, test_idx in tscv.split(np.arange(n)):
        if gap > 0:
            train_end = train_idx[-1] - gap
            if train_end < 1:
                continue
            train_idx = train_idx[train_idx <= train_end]
        if len(train_idx) < 50 or len(test_idx) < 30:
            continue
        yield train_idx, test_idx


# ============================================================
# Metrics
# ============================================================
def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 5 or np.std(y_pred) < 1e-12:
        return 0.0
    rho, _ = spearmanr(y_pred, y_true)
    return float(rho) if not np.isnan(rho) else 0.0


def direction_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(np.sign(y_true) == np.sign(y_pred)))


def long_short_sharpe(returns: np.ndarray, preds: np.ndarray, n_quant: int = 5) -> dict:
    """Stratify predictions into quintiles, compute long (top) - short (bottom) return."""
    if len(returns) < n_quant * 5:
        return {"ls_mean": 0.0, "ls_sharpe": 0.0, "top_mean": 0.0, "bot_mean": 0.0}
    q = pd.qcut(preds, n_quant, labels=False, duplicates="drop")
    valid = ~np.isnan(q)
    if valid.sum() < n_quant * 5:
        return {"ls_mean": 0.0, "ls_sharpe": 0.0, "top_mean": 0.0, "bot_mean": 0.0}
    q = q[valid]
    r = returns[valid]
    top = r[q == q.max()]
    bot = r[q == q.min()]
    ls = np.concatenate([top, -bot])
    return {
        "ls_mean": float(ls.mean()),
        "ls_sharpe": float(ls.mean() / (ls.std() + 1e-10) * np.sqrt(252)),
        "top_mean": float(top.mean()),
        "bot_mean": float(bot.mean()),
    }


# ============================================================
# Unified Multi-Regime Time-Series Feature Stability Selection
# ============================================================
def _run_stratified_bootstrap_trial(X, y, regimes, block_starts, block_freqs, block_size, randomization_alpha, best_alpha, best_l1_ratio, random_seed):
    warnings.filterwarnings("ignore")
    N, D = X.shape
    n_blocks = int(np.ceil(N / block_size))
    
    rng = np.random.default_rng(random_seed)
    
    # Stratified block selection
    m_blocks = {}
    total_assigned = 0
    regimes_list = list(block_starts.keys())
    for r in regimes_list:
        m = int(np.round(n_blocks * block_freqs[r]))
        m_blocks[r] = m
        total_assigned += m
        
    diff = n_blocks - total_assigned
    if diff != 0 and len(regimes_list) > 0:
        chosen_regime = int(np.argmax(block_freqs))
        m_blocks[chosen_regime] = max(0, m_blocks[chosen_regime] + diff)
        
    start_indices = []
    for r, m in m_blocks.items():
        if m > 0 and len(block_starts[r]) > 0:
            draws = rng.choice(block_starts[r], size=m, replace=True)
            start_indices.extend(draws)
            
    rng.shuffle(start_indices)
    
    boot_indices = []
    for start in start_indices:
        boot_indices.extend(range(start, start + block_size))
    boot_indices = boot_indices[:N]
    
    all_indices = np.arange(N)
    oob_indices = np.setdiff1d(all_indices, boot_indices)
    
    if len(boot_indices) == 0:
        boot_indices = np.arange(N)
        oob_indices = np.array([])
        
    X_boot = X[boot_indices]
    y_boot = y[boot_indices]
    
    scaler = StandardScaler()
    X_boot_scaled = scaler.fit_transform(X_boot).astype(np.float32)
    
    W = rng.uniform(randomization_alpha, 1.0, size=D)
    X_boot_scaled_rand = X_boot_scaled / W
    
    model = ElasticNet(alpha=best_alpha, l1_ratio=best_l1_ratio, random_state=random_seed, max_iter=1000, tol=1e-3)
    model.fit(X_boot_scaled_rand, y_boot)
    coef_selected = np.abs(model.coef_) > 1e-5
    
    ic_selected = np.ones(D, dtype=bool)
    if len(oob_indices) >= 10:
        X_oob = X[oob_indices]
        y_oob = y[oob_indices]
        X_oob_scaled = StandardScaler().fit_transform(X_oob).astype(np.float32)
        
        for j in range(D):
            x_oob_j = X_oob_scaled[:, j]
            rho, pval = spearmanr(x_oob_j, y_oob)
            if np.isnan(rho):
                ic_selected[j] = True
            else:
                ic_selected[j] = (pval < 0.05) or (abs(rho) > 0.02)
                
    joint_selected = coef_selected & ic_selected
    return joint_selected, coef_selected, ic_selected


class TimeSeriesStabilitySelector:
    """Unified Multi-Regime Time-Series Feature Stability Selector."""
    def __init__(self, n_bootstraps=N_BOOTSTRAPS, block_size=BLOCK_SIZE, randomization_alpha=0.5,
                 l1_ratio=0.8, ic_threshold=0.02, ic_sig_level=0.05,
                 n_splits=5, purge_gap=5, variance_cap=0.15):
        self.n_bootstraps = n_bootstraps
        self.block_size = block_size
        self.randomization_alpha = randomization_alpha
        self.l1_ratio = l1_ratio
        self.ic_threshold = ic_threshold
        self.ic_sig_level = ic_sig_level
        self.n_splits = n_splits
        self.purge_gap = purge_gap
        self.variance_cap = variance_cap

    def fit(self, X, y, features):
        N, D = X.shape
        # Detect regimes on daily vol20 feature
        vol_idx = -1
        if "vol20" in features:
            vol_idx = features.index("vol20")
            vols = X[:, vol_idx]
        else:
            vols = np.zeros(N)
            for i in range(20, N):
                vols[i] = np.std(y[i-20:i])
        
        q33 = np.quantile(vols, 0.33)
        q66 = np.quantile(vols, 0.66)
        regimes = np.zeros(N, dtype=int)
        regimes[vols > q33] = 1
        regimes[vols > q66] = 2

        # Define block starts and their regimes (overlapping blocks)
        block_starts = []
        block_regimes = []
        for s in range(0, N - self.block_size + 1):
            block_starts.append(s)
            mode_r = int(np.bincount(regimes[s:s+self.block_size]).argmax())
            block_regimes.append(mode_r)
        
        block_starts = np.array(block_starts)
        block_regimes = np.array(block_regimes)

        fold_stability_scores = []
        fold_coef_scores = []
        fold_ic_scores = []
        
        splits = list(purged_tssplit(N, self.n_splits, self.purge_gap))
        print(f"  [Stability Selection] Running {self.n_splits} splits of walk-forward stability selection...")
        
        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            X_tr, y_tr = X[train_idx], y[train_idx]
            regimes_tr = regimes[train_idx]
            
            max_start = len(train_idx) - self.block_size
            if max_start < 1:
                continue
                
            tr_block_starts = block_starts[block_starts <= max_start]
            tr_block_regimes = block_regimes[block_starts <= max_start]
            
            regime_starts = {}
            for r in [0, 1, 2]:
                regime_starts[r] = tr_block_starts[tr_block_regimes == r]
            
            counts = np.bincount(regimes_tr, minlength=3)
            freqs = counts / len(regimes_tr)
            
            scaler_tr = StandardScaler()
            X_tr_scaled = scaler_tr.fit_transform(X_tr).astype(np.float32)
            
            try:
                enet_cv = ElasticNetCV(l1_ratio=self.l1_ratio, cv=5, random_state=42, 
                                       alphas=np.logspace(-4, 1, 20), tol=1e-2, max_iter=500, n_jobs=-1)
                enet_cv.fit(X_tr_scaled, y_tr)
                best_alpha = enet_cv.alpha_
                best_l1_ratio = enet_cv.l1_ratio_
            except Exception:
                best_alpha = 0.01
                best_l1_ratio = self.l1_ratio

            results = Parallel(n_jobs=-1)(
                delayed(_run_stratified_bootstrap_trial)(
                    X_tr, y_tr, regimes_tr, regime_starts, freqs,
                    self.block_size, self.randomization_alpha,
                    best_alpha, best_l1_ratio, 42 + fold_idx * 1000 + i
                )
                for i in range(self.n_bootstraps)
            )
            
            joint_selections = np.array([r[0] for r in results])
            coef_selections = np.array([r[1] for r in results])
            ic_selections = np.array([r[2] for r in results])
            
            fold_stability_scores.append(np.mean(joint_selections, axis=0))
            fold_coef_scores.append(np.mean(coef_selections, axis=0))
            fold_ic_scores.append(np.mean(ic_selections, axis=0))
            
        fold_stability_scores = np.array(fold_stability_scores)
        fold_coef_scores = np.array(fold_coef_scores)
        fold_ic_scores = np.array(fold_ic_scores)
        
        mean_stability = np.mean(fold_stability_scores, axis=0)
        std_stability = np.std(fold_stability_scores, axis=0)
        mean_coef = np.mean(fold_coef_scores, axis=0)
        mean_ic = np.mean(fold_ic_scores, axis=0)
        
        stats_df = pd.DataFrame({
            "feature": features,
            "mean_stability": mean_stability,
            "std_stability": std_stability,
            "mean_coef_selection": mean_coef,
            "mean_ic_selection": mean_ic
        })
        
        print("\n  Top Feature Stability Scores (Walk-Forward CV):")
        sorted_stats = stats_df.sort_values(by="mean_stability", ascending=False)
        for _, row in sorted_stats.iterrows():
            print(f"    {row['feature']:<25} : Mean={row['mean_stability']:.1%}, Std={row['std_stability']:.1%}, L1={row['mean_coef_selection']:.1%}, IC={row['mean_ic_selection']:.1%}")
            
        return stats_df


def compute_stability_scores(X, y, features, n_splits=5, gap=5, block_size=BLOCK_SIZE, n_bootstraps=N_BOOTSTRAPS, variance_cap=0.15):
    selector = TimeSeriesStabilitySelector(
        n_bootstraps=n_bootstraps,
        block_size=block_size,
        randomization_alpha=0.5,
        l1_ratio=0.8,
        ic_threshold=0.02,
        ic_sig_level=0.05,
        n_splits=n_splits,
        purge_gap=gap,
        variance_cap=variance_cap
    )
    stats_df = selector.fit(X, y, features)
    return stats_df["mean_stability"].values, stats_df["std_stability"].values


# ============================================================
# Optuna objective
# ============================================================
def _side_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str) -> float:
    """Side-aware Spearman IC.

    long  : IC between prediction and max(0, y)  — upside ranking quality
    short : IC between -prediction and max(0, -y) — downside ranking quality
    single: IC between prediction and y            — overall ranking quality
    """
    if side == "long":
        target = np.maximum(0.0, y_true)
    elif side == "short":
        target = np.maximum(0.0, -y_true)
        y_pred = -y_pred
    else:
        target = y_true
    return spearman_ic(target, y_pred)


def _tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str,
             top_frac: float = 0.3) -> float:
    """Tail-weighted Spearman IC — IC computed only on the top predictions.

    Phase 2.5 fix: overall IC optimises for rank correlation across ALL
    predictions, but trading only fires on the top tail.  This function
    computes IC on the top ``top_frac`` of predictions by conviction.

    For ``long``/``short``: top = highest side-oriented prediction.
    For ``single``: top = highest |prediction| (strongest conviction either way).
    """
    n = len(y_pred)
    if n < 10:
        return _side_ic(y_true, y_pred, side)
    if side == "short":
        oriented = -y_pred
    elif side == "long":
        oriented = y_pred
    else:
        oriented = np.abs(y_pred)
    cutoff = np.nanquantile(oriented, 1.0 - top_frac)
    mask = oriented >= cutoff
    if mask.sum() < 5:
        return _side_ic(y_true, y_pred, side)
    return spearman_ic(y_true[mask], y_pred[mask])


def make_objective(pre_scaled_splits, y, sample_w, stability_scores, fold_std_stability, side="single",
                   tail_weight: float = 0.0, variance_cap: float = 0.15,
                   max_top_k: int = 20):
    def objective(trial: optuna.Trial) -> float:
        model_type = trial.suggest_categorical(
            "model_type", _OPTUNA_MODEL_TYPES)
        # Suggest top K features as a hyperparameter (bounded by capacity cap)
        top_lo = 3
        top_hi = max(top_lo, int(max_top_k))
        top_k_features = trial.suggest_int("top_k_features", top_lo, top_hi, step=1)

        # Select indices by ranking stability scores descending
        selected_indices = np.argsort(stability_scores)[::-1][:top_k_features]

        if model_type == "skglm_huber_l1":
            alpha = trial.suggest_float("skglm_huber_l1_alpha", 1e-5, 1e3, log=True)
            delta = trial.suggest_float("skglm_huber_delta", 1.0, 3.0)
            params = {"skglm_huber_l1_alpha": alpha, "skglm_huber_delta": delta}
        elif model_type == "skglm_mcp":
            alpha = trial.suggest_float("skglm_mcp_alpha", 1e-5, 1e3, log=True)
            gamma = trial.suggest_float("skglm_mcp_gamma", 1.5, 15.0)
            params = {"skglm_mcp_alpha": alpha, "skglm_mcp_gamma": gamma}

        model = _build_model(model_type, params)

        ics = []
        tail_ics = []
        for Xtr_s, Xte_s, train_idx, test_idx in pre_scaled_splits:
            Xtr_sel = Xtr_s[:, selected_indices]
            Xte_sel = Xte_s[:, selected_indices]

            _safe_fit(model, Xtr_sel, y[train_idx], sample_w[train_idx])
            preds = model.predict(Xte_sel)
            ics.append(_side_ic(y[test_idx], preds, side))
            tail_ics.append(_tail_ic(y[test_idx], preds, side))

        mean_ic = float(np.mean(ics)) if ics else -1.0
        mean_tail = float(np.mean(tail_ics)) if tail_ics else -1.0
        # Phase 2.5: blend overall IC with tail IC to align with trading
        return (1.0 - tail_weight) * mean_ic + tail_weight * mean_tail
    return objective


# ============================================================
# Phase-3 overfit controls: top-K cap, nested CV, CPCV, locked splits
# ============================================================
def _top_k_cap(n_dev: int, override: int = None) -> int:
    """Capacity cap on the number of selected features.

    Rule of thumb: sqrt(n_dev)/4 with hard caps (20 by default, 15 for small n).
    Driven by sample-size consideration — too many features vs samples invites
    multiple-testing wins inside Optuna.
    """
    if override is not None and override > 0:
        return max(3, int(override))
    cap = max(5, int(np.sqrt(n_dev) / 4))
    cap = min(cap, 20)
    if n_dev < DEFAULT_SMALL_N:
        cap = min(cap, 15)
    return cap


def _load_or_create_locked_split(tag: str, n: int, holdout_n: int):
    """Lock dev/holdout boundary in a JSON registry.

    Re-running Optuna on a different split inflates apparent holdout IC.
    First run writes the boundary; subsequent runs reuse it (clamped to n).
    Returns (train_dev_idx, holdout_idx).
    """
    locked = {}
    if LOCK_FILE.exists():
        try:
            locked = json.load(open(LOCK_FILE))
        except Exception:
            locked = {}
    key = f"{tag}__n{n}"
    if key in locked:
        ho = int(locked[key])
    else:
        ho = holdout_n
        locked[key] = ho
        try:
            with open(LOCK_FILE, "w") as f:
                json.dump(locked, f, indent=2)
        except Exception:
            pass
    ho = max(10, min(ho, n - 50))
    train_dev_idx = np.arange(0, n - ho)
    holdout_idx = np.arange(n - ho, n)
    return train_dev_idx, holdout_idx


def _optuna_sampler(sampler_name: str, seed: int = 42):
    if sampler_name == "random":
        return optuna.samplers.RandomSampler(seed=seed)
    return optuna.samplers.TPESampler(seed=seed)


def _inner_optuna_search(X_inner, y_inner, sw_inner, stab_scores, features,
                         side, tail_weight, n_inner_splits, gap,
                         n_inner_trials, sampler, max_top_k):
    """Run Optuna inside an outer fold. Returns best_params dict."""
    pre_scaled_splits = []
    for tr, te in purged_tssplit(len(y_inner), n_inner_splits, gap):
        sc = StandardScaler().fit(X_inner[tr])
        Xtr_s = sc.transform(X_inner[tr]).astype(np.float32)
        Xte_s = sc.transform(X_inner[te]).astype(np.float32)
        pre_scaled_splits.append((Xtr_s, Xte_s, tr, te))
    if not pre_scaled_splits:
        return {"model_type": "skglm_huber_l1",
                "top_k_features": 5,
                "skglm_huber_l1_alpha": 0.01,
                "skglm_huber_delta": 1.35}
    obj = make_objective(pre_scaled_splits, y_inner, sw_inner, stab_scores, None,
                         side=side, tail_weight=tail_weight, variance_cap=0.15,
                         max_top_k=max_top_k)
    study = optuna.create_study(direction="maximize", sampler=sampler,
                                pruner=optuna.pruners.MedianPruner(n_warmup_steps=5))
    study.optimize(obj, n_trials=n_inner_trials, show_progress_bar=False)
    return study.best_params


def _outer_fold_predict(X_inner, y_inner, sw_inner, stab_target_inner,
                        X_outer, features, side, tail_weight,
                        n_inner_splits, gap, n_inner_trials, n_bootstraps,
                        sampler_seed, max_top_k, ridge_alpha=1.0):
    """One outer fold: stability selection + inner Optuna + skglm fit + Ridge control.

    Returns dict with oos_preds (skglm), ridge_oos_preds, best_params,
    selected_indices, n_selected.
    """
    # 1) stability selection on inner-train (uses side-aware target)
    stab_scores, stab_std = compute_stability_scores(
        X_inner, stab_target_inner, features,
        n_splits=n_inner_splits, gap=gap, n_bootstraps=n_bootstraps)

    # 2) inner Optuna
    sampler = _optuna_sampler("tpe", seed=sampler_seed)
    best_params = _inner_optuna_search(
        X_inner, y_inner, sw_inner, stab_scores, features,
        side, tail_weight, n_inner_splits, gap, n_inner_trials, sampler, max_top_k)

    top_k = int(best_params["top_k_features"])
    selected_indices = np.argsort(stab_scores)[::-1][:top_k]

    # 3) fit skglm on inner-train selected features, predict outer-test
    sc = StandardScaler().fit(X_inner)
    Xtr_sel = sc.transform(X_inner)[:, selected_indices].astype(np.float32)
    Xte_sel = sc.transform(X_outer)[:, selected_indices].astype(np.float32)
    model = _build_model(best_params["model_type"], best_params)
    _safe_fit(model, Xtr_sel, y_inner, sw_inner)
    preds_oos = model.predict(Xte_sel) / Y_SCALE

    # 4) Ridge control — same selected features, no further tuning
    ridge = Ridge(alpha=ridge_alpha, random_state=42)
    ridge.fit(Xtr_sel, y_inner, sample_weight=sw_inner)
    preds_ridge = ridge.predict(Xte_sel) / Y_SCALE

    return {
        "oos_preds": preds_oos,
        "ridge_oos_preds": preds_ridge,
        "best_params": best_params,
        "selected_indices": selected_indices,
        "n_selected": top_k,
    }


def nested_cv_evaluate(X, y_raw, sample_w, stab_target_full, features, side, tail_weight,
                       n_outer=DEFAULT_NESTED_SPLITS, gap=DEFAULT_PURGE_GAP,
                       n_inner_splits=DEFAULT_INNER_SPLITS,
                       n_inner_trials=DEFAULT_INNER_TRIALS,
                       n_bootstraps=DEFAULT_INNER_BOOTSTRAPS,
                       max_top_k=20, base_seed=42, dates=None):
    """Honest OOS estimate via nested purged walk-forward CV.

    Outer loop walks forward over the full dataset. Inside each outer fold:
      * stability selection + Optuna are run on inner-train only
      * skglm model and Ridge control are evaluated on the outer test fold
    No information from outside the inner-train window leaks into outer preds.
    Returns dict with preds arrays, per-fold IC for skglm + Ridge, and overall.
    """
    n = len(y_raw)
    y = (y_raw * Y_SCALE).astype(np.float32)
    stab_target = (stab_target_full * Y_SCALE).astype(np.float32)
    preds_full = np.full(n, np.nan)
    ridge_full = np.full(n, np.nan)
    fold_meta = []

    splits = list(purged_tssplit(n, n_outer, gap))
    print(f"  [Nested CV] {len(splits)} outer folds × "
          f"{n_inner_trials} inner trials (gap={gap}) ...")
    for fi, (tr, te) in enumerate(splits):
        t0 = time.time()
        res = _outer_fold_predict(
            X[tr], y[tr], sample_w[tr], stab_target[tr],
            X[te], features, side, tail_weight,
            n_inner_splits, gap, n_inner_trials, n_bootstraps,
            base_seed + fi * 7919, max_top_k)
        preds_full[te] = res["oos_preds"]
        ridge_full[te] = res["ridge_oos_preds"]
        ic_sk = spearman_ic(y_raw[te], res["oos_preds"])
        ic_rg = spearman_ic(y_raw[te], res["ridge_oos_preds"])
        fold_meta.append({
            "fold": fi,
            "n_train": int(len(tr)), "n_test": int(len(te)),
            "ic_skglm": float(ic_sk), "ic_ridge": float(ic_rg),
            "n_selected": int(res["n_selected"]),
            "best_params": res["best_params"],
            "train_end": str(dates[tr[-1]].date()) if dates is not None else None,
            "test_start": str(dates[te[0]].date()) if dates is not None else None,
            "elapsed_sec": float(time.time() - t0),
        })
        print(f"    fold {fi}: n_tr={len(tr)} n_te={len(te)} "
              f"IC(skglm)={ic_sk:+.4f}  IC(ridge)={ic_rg:+.4f}  "
              f"k={res['n_selected']}  ({time.time()-t0:.0f}s)")

    valid = ~np.isnan(preds_full)
    overall_skglm = spearman_ic(y_raw[valid], preds_full[valid])
    overall_ridge = spearman_ic(y_raw[valid], ridge_full[valid])
    dir_skglm = direction_accuracy(y_raw[valid], preds_full[valid])
    ls_skglm = long_short_sharpe(y_raw[valid], preds_full[valid])
    ls_ridge = long_short_sharpe(y_raw[valid], ridge_full[valid])

    # Per-year breakdown (using outer-fold preds, fully OOS to selection)
    yearly = {}
    if dates is not None:
        df = pd.DataFrame({"d": dates, "y": y_raw, "p": preds_full, "r": ridge_full})
        df["year"] = pd.to_datetime(df["d"]).dt.year
        for yr, g in df.dropna(subset=["p"]).groupby("year"):
            if len(g) >= 20:
                yearly[int(yr)] = {
                    "ic_skglm": spearman_ic(g["y"].values, g["p"].values),
                    "ic_ridge": spearman_ic(g["y"].values, g["r"].values),
                    "n": int(len(g)),
                }

    return {
        "preds": preds_full,
        "ridge_preds": ridge_full,
        "overall_ic_skglm": float(overall_skglm),
        "overall_ic_ridge": float(overall_ridge),
        "dir_skglm": float(dir_skglm),
        "ls_sharpe_skglm": float(ls_skglm["ls_sharpe"]),
        "ls_sharpe_ridge": float(ls_ridge["ls_sharpe"]),
        "per_fold": fold_meta,
        "yearly": yearly,
        "valid_mask": valid,
        # Deployability gate: skglm must beat Ridge by >0.02 IC OOS
        "deployable": bool(overall_skglm - overall_ridge > 0.02
                           and overall_skglm > 0.0),
        "edge_over_ridge": float(overall_skglm - overall_ridge),
    }


def _cpcv_paths(n: int, n_groups: int = DEFAULT_CPCV_GROUPS,
                n_test_groups: int = DEFAULT_CPCV_TEST_GROUPS,
                gap: int = DEFAULT_PURGE_GAP):
    """Combinatorial Purged Cross-Validation paths (López de Prado).

    Split the timeline into ``n_groups`` contiguous groups. For each combination
    of ``n_test_groups`` contiguous groups, the test set is that span (with a
    purge of ``gap`` samples at each boundary) and the train set is everything
    else. Yields multiple (train_idx, test_idx) paths.
    """
    boundaries = np.linspace(0, n, n_groups + 1).astype(int)
    paths = []
    for start in range(n_groups - n_test_groups + 1):
        te_lo = boundaries[start]
        te_hi = boundaries[start + n_test_groups]
        # purge around the test window
        te_lo_p = max(0, te_lo - gap)
        te_hi_p = min(n, te_hi + gap)
        test_idx = np.arange(te_lo, te_hi)
        train_idx = np.concatenate([
            np.arange(0, te_lo_p),
            np.arange(te_hi_p, n),
        ])
        train_idx = train_idx[train_idx < n]
        if len(train_idx) < 50 or len(test_idx) < 30:
            continue
        paths.append((train_idx, test_idx))
    return paths


def cpcv_evaluate(X, y_raw, sample_w, stab_target_full, features, side, tail_weight,
                  selected_indices_locked, best_params_locked,
                  n_groups=DEFAULT_CPCV_GROUPS, n_test_groups=DEFAULT_CPCV_TEST_GROUPS,
                  gap=DEFAULT_PURGE_GAP, dates=None, ridge_alpha=1.0):
    """Multi-path OOS IC using a *locked* (already tuned) configuration.

    Unlike nested CV this does NOT re-tune per path; it uses the deployed
    feature set + params and only varies the train/test split. Gives a
    distribution of OOS IC rather than a single point estimate.
    """
    n = len(y_raw)
    y = (y_raw * Y_SCALE).astype(np.float32)
    paths = _cpcv_paths(n, n_groups, n_test_groups, gap)
    if not paths:
        return {"path_ics_skglm": [], "path_ics_ridge": [],
                "mean_ic_skglm": 0.0, "mean_ic_ridge": 0.0,
                "n_paths": 0}
    sk_ics, rg_ics = [], []
    for pi, (tr, te) in enumerate(paths):
        sc = StandardScaler().fit(X[tr])
        Xtr_sel = sc.transform(X[tr])[:, selected_indices_locked].astype(np.float32)
        Xte_sel = sc.transform(X[te])[:, selected_indices_locked].astype(np.float32)
        m = _build_model(best_params_locked["model_type"], best_params_locked)
        _safe_fit(m, Xtr_sel, y[tr], sample_w[tr])
        p_sk = m.predict(Xte_sel) / Y_SCALE
        ridge = Ridge(alpha=ridge_alpha, random_state=42)
        ridge.fit(Xtr_sel, y[tr], sample_weight=sample_w[tr])
        p_rg = ridge.predict(Xte_sel) / Y_SCALE
        sk_ics.append(spearman_ic(y_raw[te], p_sk))
        rg_ics.append(spearman_ic(y_raw[te], p_rg))
    sk_arr = np.array(sk_ics)
    rg_arr = np.array(rg_ics)
    return {
        "n_paths": len(paths),
        "path_ics_skglm": [float(x) for x in sk_ics],
        "path_ics_ridge": [float(x) for x in rg_ics],
        "mean_ic_skglm": float(sk_arr.mean()) if len(sk_arr) else 0.0,
        "std_ic_skglm": float(sk_arr.std()) if len(sk_arr) else 0.0,
        "mean_ic_ridge": float(rg_arr.mean()) if len(rg_arr) else 0.0,
        "std_ic_ridge": float(rg_arr.std()) if len(rg_arr) else 0.0,
        "min_ic_skglm": float(sk_arr.min()) if len(sk_arr) else 0.0,
    }



def train_etf(etf_name: str, n_trials: int, n_splits: int, gap: int,
              side: str = "single",
              run_nested: bool = True, run_cpcv: bool = True,
              n_outer: int = DEFAULT_NESTED_SPLITS,
              n_inner_splits: int = DEFAULT_INNER_SPLITS,
              n_inner_trials: int = DEFAULT_INNER_TRIALS,
              n_inner_bootstraps: int = DEFAULT_INNER_BOOTSTRAPS,
              sampler_name: str = "tpe",
              max_top_k_override: int = 0,
              ridge_alpha: float = 1.0) -> dict:
    """Train one linear model for an ETF.

    side="single" (default): symmetric target ``y = trade_return``.
    side="long":  asymmetric stability target ``y = max(0, trade_return)`` (upside specialist).
    side="short": asymmetric stability target ``y = max(0, -trade_return)`` (downside specialist).
    """
    if side not in ("single", "long", "short"):
        raise ValueError(f"side must be single|long|short, got {side!r}")

    t0 = time.time()
    feat_path = DATA_DIR / f"features_{etf_name}.parquet"
    if not feat_path.exists():
        print(f"  [SKIP] {etf_name}: missing {feat_path.name}. Run build_features.py first.")
        return {}

    feat = pd.read_parquet(feat_path).sort_index()
    feat = feat.dropna(subset=FEATURES + [TARGET]).copy()
    X = feat[FEATURES].values.astype(np.float32)
    # Always train on the raw trade_return so the model preserves full regression
    # signal (including the magnitude of negative returns).  The clipped target
    # is used ONLY for stability-selection feature pruning so each side picks
    # features that are relevant to its regime (upside / downside).
    y_raw = feat[TARGET].values.astype(np.float32)
    n = len(feat)
    if side == "long":
        y_clip_raw = np.maximum(0.0, y_raw)
    elif side == "short":
        y_clip_raw = np.maximum(0.0, -y_raw)
    else:
        y_clip_raw = y_raw.copy()
    y = (y_raw * Y_SCALE).astype(np.float32)          # training target (raw)
    y_clip = (y_clip_raw * Y_SCALE).astype(np.float32)  # stability-selection target (asymmetric)
    # Sample weights: gently emphasize the side's active regime without
    # distorting the overall regression.  lambda=0.5 means a +2σ day gets
    # only ~2× weight; most days stay near 1×.
    sigma = float(y_raw.std()) + 1e-10
    if side == "long":
        sample_w = 1.0 + 0.5 * np.maximum(0.0, y_raw) / sigma
    elif side == "short":
        sample_w = 1.0 + 0.5 * np.maximum(0.0, -y_raw) / sigma
    else:
        sample_w = np.ones(n)
    sample_w = sample_w.astype(np.float32)
    dates = feat.index
    full_y_raw = pd.Series(y_raw, index=dates)

    tag = etf_name if side == "single" else f"{etf_name}_{side}"
    active = y_clip_raw > 0
    n_active = int(active.sum())
    clip_label = "upside" if side == "long" else "downside" if side == "short" else "all"
    sharpe_str = (f"{y_raw[active].mean()/y_raw[active].std()*np.sqrt(252):.2f}"
                  if n_active > 5 else "n/a")
    print(f"\n[{tag}] {n} samples, {len(FEATURES)} features (side={side}), "
          f"target Sharpe={y_raw.mean()/y_raw.std()*np.sqrt(252):.2f} "
          f"({clip_label} active-day Sharpe={sharpe_str} on {n_active} days; "
          f"scaled x{Y_SCALE:.0f})")

    # ── 1) Holdout: last 20% is final OOS (locked across re-runs) ──
    holdout_n = int(n * HOLDOUT_FRACTION)
    train_dev_idx, holdout_idx = _load_or_create_locked_split(tag, n, holdout_n)
    X_dev, y_dev, dates_dev = X[train_dev_idx], y[train_dev_idx], dates[train_dev_idx]
    X_ho, y_ho, dates_ho = X[holdout_idx], y[holdout_idx], dates[holdout_idx]
    sw_dev = sample_w[train_dev_idx]
    y_clip_dev = y_clip[train_dev_idx]
    print(f"  dev (Optuna): {len(X_dev)}, holdout (final OOS, locked): {len(X_ho)}")

    # Top-K capacity cap (Phase-3 overfit control)
    max_top_k = _top_k_cap(len(X_dev), override=max_top_k_override or None)
    print(f"  [top_k cap] max_top_k={max_top_k}  (sqrt(n_dev)/4 rule, "
          f"n_dev={len(X_dev)})")

    # ── 2) Stability Selection on dev set ──
    # Phase 2.4 fix: use the asymmetric (clipped) target for dual models so
    # feature selection isolates regime-specific tail drivers, not overall
    # variance.  Single model keeps the raw target.
    if side != "single":
        stab_target = y_clip_dev
        print(f"  [Stability Selection] Using ASYMMETRIC target ({clip_label}) "
              f"for feature pruning (Phase 2.4 fix)")
    else:
        stab_target = y_dev
    stability_scores, fold_std_stability = compute_stability_scores(X_dev, stab_target, FEATURES, n_splits=n_splits, gap=gap)

    # ── 3) Optuna hyperparameter search — side-specific objective ──
    print(f"  Optuna: {n_trials} trials, {n_splits} folds, purge_gap={gap} "
          f"(side={side}) ...")
    study_path = DATA_DIR / f"optuna_study_{tag}.sqlite3"
    if study_path.exists():
        study_path.unlink()
    storage = f"sqlite:///{study_path}"
    study = optuna.create_study(
        study_name=f"linear_{tag}", direction="maximize",
        storage=storage, load_if_exists=False,
        sampler=_optuna_sampler(sampler_name),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=10),
    )
    # Pre-scale features once for each cross-validation split of Optuna
    pre_scaled_splits = []
    for train_idx, test_idx in purged_tssplit(len(y_dev), n_splits, gap):
        scaler = StandardScaler().fit(X_dev[train_idx])
        Xtr_s = scaler.transform(X_dev[train_idx]).astype(np.float32)
        Xte_s = scaler.transform(X_dev[test_idx]).astype(np.float32)
        pre_scaled_splits.append((Xtr_s, Xte_s, train_idx, test_idx))

    # Phase 2.5: weight the objective toward the trading tail for dual models
    # (0.0 for single = pure overall IC, 0.5 for dual = equal weight tail+overall)
    tail_weight = 0.0 if side == "single" else 0.5
    obj = make_objective(pre_scaled_splits, y_dev, sw_dev, stability_scores, fold_std_stability,
                         side=side, tail_weight=tail_weight, variance_cap=0.15,
                         max_top_k=max_top_k)
    study.optimize(obj, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_cv_ic = study.best_value
    print(f"  best CV IC: {best_cv_ic:.4f}  params: {best_params}")

    # ── 4) Final model: train on all dev data, evaluate on holdout ──
    scaler = StandardScaler().fit(X_dev)
    X_dev_s = scaler.transform(X_dev)
    X_ho_s = scaler.transform(X_ho)

    best_top_k = best_params["top_k_features"]
    selected_indices = np.argsort(stability_scores)[::-1][:best_top_k]
    selected_features = [FEATURES[i] for i in selected_indices]

    # Store dynamic stability threshold back into best_params for downstream compat
    best_params["stability_threshold"] = float(stability_scores[selected_indices[-1]])
    print(f"  Final selected features ({len(selected_features)}): {selected_features}")

    X_dev_sel = X_dev_s[:, selected_indices]
    X_ho_sel = X_ho_s[:, selected_indices]

    model_type = best_params["model_type"]
    final_model = _build_model(model_type, best_params)

    _safe_fit(final_model, X_dev_sel, y_dev, sw_dev)
    preds_ho = final_model.predict(X_ho_sel)
    preds_is = final_model.predict(X_dev_sel)

    # ── 5) Metrics ──
    preds_ho_raw = preds_ho / Y_SCALE
    preds_is_raw = preds_is / Y_SCALE
    y_ho_raw = y_ho / Y_SCALE
    y_dev_raw = y_dev / Y_SCALE

    holdout_ic = _side_ic(y_ho_raw, preds_ho_raw, side)
    holdout_dir = direction_accuracy(y_ho_raw, preds_ho_raw)
    holdout_rmse = float(np.sqrt(np.mean((y_ho_raw - preds_ho_raw) ** 2)))
    holdout_ls = long_short_sharpe(y_ho_raw, preds_ho_raw)

    is_ic = _side_ic(y_dev_raw, preds_is_raw, side)

    print(f"  HOLDOUT: IC={holdout_ic:.4f}  Dir={holdout_dir:.3f}  "
          f"RMSE={holdout_rmse*100:.4f}%  L/S Sharpe={holdout_ls['ls_sharpe']:.2f}")
    print(f"  OVERFITTING GAP: IS IC={is_ic:.4f} vs OOS IC={holdout_ic:.4f}  "
          f"(gap={is_ic - holdout_ic:+.4f})")

    # ── 6) Walk-forward OOS predictions across all folds (purged) ──
    wf_preds = np.full(n, np.nan)
    wf_is_ic_per_fold = []
    wf_oos_ic_per_fold = []
    for train_idx, test_idx in purged_tssplit(n, n_splits, gap):
        sc = StandardScaler().fit(X[train_idx])
        Xtr_s = sc.transform(X[train_idx])
        Xte_s = sc.transform(X[test_idx])

        Xtr_sel = Xtr_s[:, selected_indices]
        Xte_sel = Xte_s[:, selected_indices]

        m = _build_model(model_type, best_params)
        _safe_fit(m, Xtr_sel, y[train_idx], sample_w[train_idx])
        wf_preds[test_idx] = m.predict(Xte_sel) / Y_SCALE
        wf_is_ic_per_fold.append(spearman_ic(y[train_idx] / Y_SCALE, m.predict(Xtr_sel) / Y_SCALE))
        wf_oos_ic_per_fold.append(spearman_ic(y[test_idx] / Y_SCALE, wf_preds[test_idx]))

    wf_valid = ~np.isnan(wf_preds)
    wf_overall_ic = spearman_ic(y_raw[wf_valid], wf_preds[wf_valid])

    # ── 7) Year-by-year OOS IC ──
    wf_df = pd.DataFrame({"date": dates, "y": y_raw, "pred": wf_preds})
    wf_df["year"] = wf_df["date"].dt.year
    yearly_ic = {}
    for yr, g in wf_df.dropna(subset=["pred"]).groupby("year"):
        if len(g) >= 20:
            yearly_ic[int(yr)] = {
                "ic": spearman_ic(g["y"].values, g["pred"].values),
                "dir": direction_accuracy(g["y"].values, g["pred"].values),
                "n": len(g),
                "ls_sharpe": long_short_sharpe(g["y"].values, g["pred"].values)["ls_sharpe"],
            }

    # ── 8) Baselines (on holdout, unscaled units) ──
    baselines = {}
    baselines["zero"] = {
        "ic": 0.0, "dir": 0.5,
        "rmse": float(np.sqrt(np.mean(y_ho_raw ** 2))),
    }
    ylag = full_y_raw.shift(1).reindex(dates_ho).values
    valid_lag = ~np.isnan(ylag)
    baselines["yesterday_pm"] = {
        "ic": spearman_ic(y_ho_raw[valid_lag], ylag[valid_lag]) if valid_lag.sum() > 5 else 0.0,
        "dir": direction_accuracy(y_ho_raw[valid_lag], ylag[valid_lag]) if valid_lag.sum() > 5 else 0.5,
        "rmse": float(np.sqrt(np.mean((y_ho_raw[valid_lag] - ylag[valid_lag]) ** 2))) if valid_lag.sum() > 5 else 0.0,
    }
    col = FEATURES.index("first_30min_return")
    baselines["first_30min_mom"] = {
        "ic": spearman_ic(y_ho_raw, X_ho[:, col]),
        "dir": direction_accuracy(y_ho_raw, X_ho[:, col]),
        "rmse": float(np.sqrt(np.mean((y_ho_raw - X_ho[:, col]) ** 2))),
    }
    ridge_base = Ridge(alpha=1.0, random_state=42)
    ridge_base.fit(X_dev_s, y_dev)
    ridge_base_ho = ridge_base.predict(X_ho_s) / Y_SCALE
    baselines["ridge"] = {
        "ic": spearman_ic(y_ho_raw, ridge_base_ho),
        "dir": direction_accuracy(y_ho_raw, ridge_base_ho),
        "rmse": float(np.sqrt(np.mean((y_ho_raw - ridge_base_ho) ** 2))),
        "ls_sharpe": long_short_sharpe(y_ho_raw, ridge_base_ho)["ls_sharpe"],
    }

    # ── 8.5) Nested CV (honest OOS) + Ridge control + CPCV ───────────
    nested_result = None
    if run_nested:
        print(f"\n  === Nested CV (honest OOS, side={side}) ===")
        nested_result = nested_cv_evaluate(
            X, y_raw, sample_w, y_clip_raw, FEATURES, side, tail_weight,
            n_outer=n_outer, gap=gap, n_inner_splits=n_inner_splits,
            n_inner_trials=n_inner_trials, n_bootstraps=n_inner_bootstraps,
            max_top_k=max_top_k, base_seed=42, dates=dates)
        print(f"  NESTED overall IC: skglm={nested_result['overall_ic_skglm']:+.4f}  "
              f"ridge={nested_result['overall_ic_ridge']:+.4f}  "
              f"edge={nested_result['edge_over_ridge']:+.4f}  "
              f"deployable={nested_result['deployable']}")
        print(f"  NESTED L/S Sharpe: skglm={nested_result['ls_sharpe_skglm']:+.2f}  "
              f"ridge={nested_result['ls_sharpe_ridge']:+.2f}  "
              f"dir(skglm)={nested_result['dir_skglm']:.3f}")
        if nested_result["yearly"]:
            print("  NESTED yearly IC (skglm | ridge):")
            for yr, v in sorted(nested_result["yearly"].items()):
                print(f"    {yr}: {v['ic_skglm']:+.3f} | {v['ic_ridge']:+.3f}  (n={v['n']})")

    cpcv_result = None
    if run_cpcv:
        print(f"\n  === Combinatorial Purged CV (locked config) ===")
        cpcv_result = cpcv_evaluate(
            X, y_raw, sample_w, y_clip_raw, FEATURES, side, tail_weight,
            selected_indices_locked=selected_indices,
            best_params_locked=best_params,
            n_groups=DEFAULT_CPCV_GROUPS, n_test_groups=DEFAULT_CPCV_TEST_GROUPS,
            gap=gap, dates=dates, ridge_alpha=ridge_alpha)
        print(f"  CPCV paths={cpcv_result['n_paths']}  "
              f"mean IC skglm={cpcv_result['mean_ic_skglm']:+.4f} "
              f"(±{cpcv_result['std_ic_skglm']:.4f}, "
              f"min={cpcv_result['min_ic_skglm']:+.4f})  "
              f"ridge={cpcv_result['mean_ic_ridge']:+.4f} "
              f"(±{cpcv_result['std_ic_ridge']:.4f})")

    # Deployability gate — uses nested CV (most honest) when available,
    # else falls back to holdout edge over Ridge.
    if nested_result is not None:
        deployable = bool(nested_result["deployable"])
        deployability_basis = "nested_cv"
    else:
        deployable = bool(holdout_ic - baselines["ridge"]["ic"] > 0.02
                          and holdout_ic > 0.0)
        deployability_basis = "holdout"
    print(f"  DEPLOYABLE={deployable}  (basis={deployability_basis})")

    # ── 9) Standardized Coefficients & Permutation Importance ──
    coefs = np.zeros(len(FEATURES))
    coefs[selected_indices] = final_model.coef_
    coef_imp = dict(zip(FEATURES, coefs.tolist()))

    perm = permutation_importance(
        final_model, X_ho_sel, y_ho, n_repeats=10, random_state=42,
        scoring="neg_mean_squared_error",
        n_jobs=1 if isinstance(final_model, GeneralizedLinearEstimator) else -1,
    )
    perm_imp_sel = dict(zip(selected_features, perm.importances_mean.tolist()))
    perm_imp = {feat: perm_imp_sel.get(feat, 0.0) for feat in FEATURES}

    # ── 10) Purge-gap sensitivity ──
    purge_sens = {}
    for g in [0, 5, 10]:
        ics_g = []
        for train_idx, test_idx in purged_tssplit(n, n_splits, g):
            sc = StandardScaler().fit(X[train_idx])
            Xtr_s = sc.transform(X[train_idx])
            Xte_s = sc.transform(X[test_idx])

            Xtr_sel = Xtr_s[:, selected_indices]
            Xte_sel = Xte_s[:, selected_indices]

            m = _build_model(model_type, best_params)
            _safe_fit(m, Xtr_sel, y[train_idx], sample_w[train_idx])
            preds = m.predict(Xte_sel) / Y_SCALE
            ics_g.append(spearman_ic(y_raw[test_idx], preds))
        purge_sens[g] = {"mean_ic": float(np.mean(ics_g)) if ics_g else 0.0,
                         "n_folds": len(ics_g)}

    # ── 11) Optuna hyperparameter importance ──
    try:
        optuna_param_imp = optuna.importance.get_param_importances(study)
        optuna_param_imp = {k: float(v) for k, v in optuna_param_imp.items()}
    except Exception:
        optuna_param_imp = {}

    # ── 12) Save model + scaler ──
    joblib.dump(final_model, MODELS_DIR / f"linear_{tag}.joblib")
    joblib.dump({"scaler": scaler,
                 "features": FEATURES,
                 "selected_features": selected_features,
                 "stability_scores": dict(zip(FEATURES, stability_scores.tolist())),
                 "fold_std_stability": dict(zip(FEATURES, fold_std_stability.tolist())),
                 "best_params": best_params,
                 "best_model_type": model_type,
                 "holdout_ic": holdout_ic,
                 "train_end_date": str(dates_dev[-1].date()),
                 "holdout_start_date": str(dates_ho[0].date()),
                 "y_scale": Y_SCALE,
                 "side": side,
                 "target": "raw_trade_return",
                 "stability_target": ("clipped_trade_return" if side != "single" else "trade_return"),
                 "optuna_objective": ("tail_weighted_ic" if side != "single" else "overall_ic"),
                 "sample_weight_lambda": 0.5 if side != "single" else 0.0,
                 # Phase-3 overfit-control metadata
                 "max_top_k": int(max_top_k),
                 "nested_overall_ic_skglm": (nested_result["overall_ic_skglm"]
                                              if nested_result else None),
                 "nested_overall_ic_ridge": (nested_result["overall_ic_ridge"]
                                              if nested_result else None),
                 "nested_edge_over_ridge": (nested_result["edge_over_ridge"]
                                             if nested_result else None),
                 "nested_deployable": (nested_result["deployable"]
                                        if nested_result else None),
                 "cpcv_mean_ic_skglm": (cpcv_result["mean_ic_skglm"]
                                         if cpcv_result else None),
                 "cpcv_min_ic_skglm": (cpcv_result["min_ic_skglm"]
                                        if cpcv_result else None),
                 "deployable": bool(deployable),
                 "deployability_basis": deployability_basis},
                MODELS_DIR / f"scaler_{tag}.joblib")

    # ── 13) Plots ──
    _plot_diagnostics(tag, dates_ho, y_ho_raw, preds_ho_raw,
                      wf_df, coef_imp, perm_imp, optuna_param_imp,
                      purge_sens, yearly_ic, study)

    elapsed = time.time() - t0
    print(f"  [{tag}] done in {elapsed:.0f}s ({elapsed/60:.1f}min)")

    return {
        "etf": etf_name,
        "side": side,
        "tag": tag,
        "n_samples": int(n),
        "n_features": len(FEATURES),
        "selected_features": selected_features,
        "n_selected_features": len(selected_features),
        "stability_scores": dict(zip(FEATURES, stability_scores.tolist())),
        "fold_std_stability": dict(zip(FEATURES, fold_std_stability.tolist())),
        "date_range": [str(dates[0].date()), str(dates[-1].date())],
        "holdout_n": int(len(X_ho)),
        "holdout_range": [str(dates_ho[0].date()), str(dates_ho[-1].date())],
        "best_cv_ic": float(best_cv_ic),
        "best_params": best_params,
        "is_ic": float(is_ic),
        "holdout_ic": float(holdout_ic),
        "holdout_dir_acc": float(holdout_dir),
        "holdout_rmse": holdout_rmse,
        "holdout_long_short": holdout_ls,
        "walk_forward_overall_ic": float(wf_overall_ic),
        "walk_forward_is_ic_per_fold": wf_is_ic_per_fold,
        "walk_forward_oos_ic_per_fold": wf_oos_ic_per_fold,
        "yearly_ic": yearly_ic,
        "baselines": baselines,
        "coefficient_importance": coef_imp,
        "permutation_importance": perm_imp,
        "purge_sensitivity": purge_sens,
        "optuna_param_importance": optuna_param_imp,
        "target_stats": {
            "mean_pct": float(y_raw.mean() * 100),
            "std_pct": float(y_raw.std() * 100),
            "sharpe_ann": float(y_raw.mean() / y_raw.std() * np.sqrt(252)),
        },
        "y_scale": Y_SCALE,
        "elapsed_sec": elapsed,
        # ── Phase-3 overfit-control metrics ──
        "max_top_k": int(max_top_k),
        "sampler": sampler_name,
        "nested_cv": (
            {
                "overall_ic_skglm": nested_result["overall_ic_skglm"],
                "overall_ic_ridge": nested_result["overall_ic_ridge"],
                "edge_over_ridge": nested_result["edge_over_ridge"],
                "dir_skglm": nested_result["dir_skglm"],
                "ls_sharpe_skglm": nested_result["ls_sharpe_skglm"],
                "ls_sharpe_ridge": nested_result["ls_sharpe_ridge"],
                "per_fold": nested_result["per_fold"],
                "yearly": nested_result["yearly"],
                "deployable": nested_result["deployable"],
            } if nested_result is not None else None
        ),
        "cpcv": (
            {
                "n_paths": cpcv_result["n_paths"],
                "mean_ic_skglm": cpcv_result["mean_ic_skglm"],
                "std_ic_skglm": cpcv_result["std_ic_skglm"],
                "min_ic_skglm": cpcv_result["min_ic_skglm"],
                "mean_ic_ridge": cpcv_result["mean_ic_ridge"],
                "std_ic_ridge": cpcv_result["std_ic_ridge"],
                "path_ics_skglm": cpcv_result["path_ics_skglm"],
                "path_ics_ridge": cpcv_result["path_ics_ridge"],
            } if cpcv_result is not None else None
        ),
        "deployable": bool(deployable),
        "deployability_basis": deployability_basis,
    }


# ============================================================
# Plots
# ============================================================
def _plot_diagnostics(etf, dates_ho, y_ho, preds_ho, wf_df,
                      coef_imp, perm_imp, optuna_imp, purge_sens,
                      yearly_ic, study):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    ax.scatter(preds_ho * 100, y_ho * 100, alpha=0.3, s=10, c="steelblue")
    lim = max(abs(y_ho).max(), abs(preds_ho).max()) * 100 * 1.05
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.axhline(0, color="black", lw=0.5); ax.axvline(0, color="black", lw=0.5)
    ax.plot([-lim, lim], [-lim, lim], "r--", lw=0.8)
    ax.set_xlabel("Predicted trade return (%)"); ax.set_ylabel("Actual trade return (%)")
    ic = spearman_ic(y_ho, preds_ho)
    ax.set_title(f"{etf} Holdout: IC={ic:.3f}")
    ax.grid(alpha=0.3)

    ax = axes[1]
    q = pd.qcut(preds_ho, 5, labels=False, duplicates="drop")
    valid = ~np.isnan(q)
    if valid.sum() > 50:
        idx_top = np.where((q == q[valid].max()) & valid)[0]
        idx_bot = np.where((q == q[valid].min()) & valid)[0]
        ls = np.zeros(len(y_ho))
        ls[idx_top] = y_ho[idx_top]
        ls[idx_bot] = -y_ho[idx_bot]
        cum = np.cumsum(ls)
        ax.plot(pd.to_datetime(dates_ho), cum * 100, color="purple", lw=1.2)
        ax.axhline(0, color="black", lw=0.5)
        ax.set_xlabel("Date"); ax.set_ylabel("Cumulative L/S return (%)")
        ax.set_title(f"{etf} TopQ - BotQ Cumulative")
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"holdout_scatter_{etf}.png", dpi=110)
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 4))
    wf_v = wf_df.dropna(subset=["pred"]).copy()
    if len(wf_v) > 90:
        y_arr = wf_v["y"].values
        p_arr = wf_v["pred"].values
        dates_arr = wf_v["date"].values
        win = 90
        rolling_ics = []
        rolling_dates = []
        for i in range(win, len(wf_v)):
            window_y = y_arr[i - win:i]
            window_p = p_arr[i - win:i]
            if len(window_y) >= 30 and np.std(window_p) > 1e-12:
                rolling_ics.append(spearman_ic(window_y, window_p))
                rolling_dates.append(dates_arr[i])
        if rolling_dates:
            ax.plot(rolling_dates, rolling_ics, color="steelblue", lw=1)
            ax.axhline(0, color="black", lw=0.5)
            ax.set_title(f"{etf}: {win}-day rolling OOS Spearman IC")
            ax.set_ylabel("Spearman IC"); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"ic_timeseries_{etf}.png", dpi=110)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, imp, title in [
        (axes[0], coef_imp, "Standardized Coefficient"),
        (axes[1], perm_imp, "Permutation Importance (OOS)"),
    ]:
        filtered_imp = {k: v for k, v in imp.items() if abs(v) > 1e-9}
        if not filtered_imp:
            filtered_imp = imp
        s = pd.Series(filtered_imp).sort_values()
        ax.barh(s.index, s.values, color="steelblue")
        ax.set_title(f"{etf}: {title}")
        ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"feature_importance_{etf}.png", dpi=110)
    plt.close()

    if yearly_ic:
        fig, ax = plt.subplots(figsize=(9, 4))
        yrs = sorted(yearly_ic.keys())
        ics = [yearly_ic[y]["ic"] for y in yrs]
        colors = ["green" if v > 0 else "red" for v in ics]
        ax.bar(yrs, ics, color=colors)
        ax.axhline(0, color="black", lw=0.5)
        ax.set_title(f"{etf}: OOS Spearman IC by Year (walk-forward)")
        ax.set_ylabel("Spearman IC"); ax.grid(alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"yearly_ic_{etf}.png", dpi=110)
        plt.close()

    fig, ax = plt.subplots(figsize=(6, 4))
    keys = sorted(purge_sens.keys())
    ax.plot(keys, [purge_sens[k]["mean_ic"] for k in keys], "o-", color="purple")
    ax.set_xticks(keys); ax.set_xlabel("Purge gap (trading days)")
    ax.set_ylabel("Mean OOS IC")
    ax.set_title(f"{etf}: Purge-gap sensitivity (leakage diagnostic)")
    ax.axhline(0, color="black", lw=0.5)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"purge_sensitivity_{etf}.png", dpi=110)
    plt.close()

    if optuna_imp:
        fig, ax = plt.subplots(figsize=(8, 5))
        s = pd.Series(optuna_imp).sort_values()
        ax.barh(s.index, s.values, color="orange")
        ax.set_title(f"{etf}: Optuna hyperparameter importance")
        ax.grid(alpha=0.3, axis="x")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"optuna_param_importance_{etf}.png", dpi=110)
        plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="all")
    ap.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    ap.add_argument("--quick", action="store_true", help="smoke test (20 trials)")
    ap.add_argument("--splits", type=int, default=DEFAULT_N_SPLITS)
    ap.add_argument("--gap", type=int, default=DEFAULT_PURGE_GAP)
    ap.add_argument("--gpu", action="store_true", help="ignored, kept for compatibility")
    ap.add_argument("--side", default="single",
                    choices=["single", "long", "short", "both"],
                    help="single=legacy symmetric model; long/short/both=train "
                         "asymmetric dual models")
    # Phase-3 overfit-control knobs
    ap.add_argument("--sampler", default="tpe", choices=["tpe", "random"],
                    help="Optuna sampler (random=RandomSampler ablation)")
    ap.add_argument("--max-top-k", type=int, default=0,
                    help="override the sqrt(n)/4 top-K capacity cap (0=auto)")
    ap.add_argument("--no-nested", action="store_true",
                    help="skip nested CV (faster, less honest OOS)")
    ap.add_argument("--no-cpcv", action="store_true",
                    help="skip Combinatorial Purged CV")
    ap.add_argument("--nested-splits", type=int, default=DEFAULT_NESTED_SPLITS,
                    help="outer walk-forward folds for nested CV")
    ap.add_argument("--inner-splits", type=int, default=DEFAULT_INNER_SPLITS,
                    help="inner Optuna CV folds inside each outer fold")
    ap.add_argument("--inner-trials", type=int, default=DEFAULT_INNER_TRIALS,
                    help="Optuna trials inside each outer fold (nested CV)")
    ap.add_argument("--inner-bootstraps", type=int, default=DEFAULT_INNER_BOOTSTRAPS,
                    help="stability-selection bootstraps per outer fold")
    ap.add_argument("--ridge-alpha", type=float, default=1.0,
                    help="Ridge alpha for the stability-selected control")
    args = ap.parse_args()

    if args.quick:
        args.trials = min(args.trials, 20)

    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]

    sides = ["long", "short"] if args.side == "both" else [args.side]

    print(f"Training Linear day-models for: {etfs}")
    print(f"  trials={args.trials}  splits={args.splits}  purge_gap={args.gap}  "
          f"holdout_frac={HOLDOUT_FRACTION}  sides={sides}")

    t_start = time.time()
    all_results = {}
    for etf in etfs:
        for side in sides:
            try:
                res = train_etf(etf, n_trials=args.trials, n_splits=args.splits,
                                gap=args.gap, side=side,
                                run_nested=not args.no_nested,
                                run_cpcv=not args.no_cpcv,
                                n_outer=args.nested_splits,
                                n_inner_splits=args.inner_splits,
                                n_inner_trials=args.inner_trials,
                                n_inner_bootstraps=args.inner_bootstraps,
                                sampler_name=args.sampler,
                                max_top_k_override=args.max_top_k,
                                ridge_alpha=args.ridge_alpha)
                if res:
                    key = res.get("tag", etf)
                    all_results[key] = res
                    suffix = "" if side == "single" else f"_{side}"
                    with open(DATA_DIR / f"results_{etf}{suffix}.json", "w") as f:
                        json.dump(res, f, indent=2, default=str)
            except Exception as e:
                print(f"  [ERROR] {etf} ({side}): {e}")
                import traceback; traceback.print_exc()

    print("\n" + "=" * 118)
    print(f"{'Tag':<18} {'Model':<14} {'k':<5} {'HoldIC':>8} {'NestIC':>8} {'RidgeIC':>8} {'Edge':>7} {'CPCVmean':>9} {'CPCVmin':>8} {'Dir':>6} {'Deploy':>7}")
    print("-" * 118)
    for key, r in all_results.items():
        best_model = r["best_params"]["model_type"].upper()
        n_sel = r["n_selected_features"]
        ho_ic = r['holdout_ic']
        n_ic = r['nested_cv']['overall_ic_skglm'] if r.get('nested_cv') else float('nan')
        n_rg = r['nested_cv']['overall_ic_ridge'] if r.get('nested_cv') else float('nan')
        edge = r['nested_cv']['edge_over_ridge'] if r.get('nested_cv') else float('nan')
        cp_mean = r['cpcv']['mean_ic_skglm'] if r.get('cpcv') else float('nan')
        cp_min = r['cpcv']['min_ic_skglm'] if r.get('cpcv') else float('nan')
        dep = "YES" if r.get('deployable') else "no"
        print(f"{key:<18} {best_model:<14} {n_sel:<5d} {ho_ic:>8.4f} {n_ic:>8.4f} "
              f"{n_rg:>8.4f} {edge:>+7.4f} {cp_mean:>+9.4f} {cp_min:>+8.4f} "
              f"{r['holdout_dir_acc']:>6.3f} {dep:>7}")
    print("=" * 118)

    results_tag = "all" + ("" if args.side == "single" else f"_{args.side}")
    with open(DATA_DIR / f"results_{results_tag}.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    total_time = time.time() - t_start
    print(f"\nTotal wall time: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Combined results → {DATA_DIR / f'results_{results_tag}.json'}")


if __name__ == "__main__":
    main()
