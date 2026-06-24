"""
Phase 2: Train Optuna-tuned linear regression predicting trade_return per ETF.
Supports Ridge, Lasso, ElasticNet, HuberRegressor.
Uses Lasso-based Block Bootstrap Stability Selection to select robust feature subsets,
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
from sklearn.linear_model import Ridge, Lasso, ElasticNet, HuberRegressor, LassoCV
from sklearn.inspection import permutation_importance
import optuna
import joblib
from joblib import Parallel, delayed

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
DEFAULT_TRIALS = 100
DEFAULT_N_SPLITS = 5
DEFAULT_PURGE_GAP = 5
HOLDOUT_FRACTION = 0.20   # last 20% of data is the final OOS holdout
BLOCK_SIZE = 20           # Block bootstrap contiguous length (approx 1 calendar month)
N_BOOTSTRAPS = 50         # Number of bootstrap trials for stability selection


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
# Lasso-based Block Bootstrap Stability Selection
# ============================================================
def _run_bootstrap_trial(X_scaled, y, block_size, random_seed):
    warnings.filterwarnings("ignore")
    N, D = X_scaled.shape
    n_blocks = int(np.ceil(N / block_size))
    
    # Use a localized RNG to preserve cross-process independence
    rng = np.random.default_rng(random_seed)
    start_indices = rng.integers(0, N - block_size + 1, size=n_blocks)
    
    boot_indices = []
    for start in start_indices:
        boot_indices.extend(range(start, start + block_size))
    boot_indices = boot_indices[:N]
    
    X_boot_s = X_scaled[boot_indices]
    y_boot = y[boot_indices]
    
    # Fit LassoCV to automatically select best L1 penalty
    lasso = LassoCV(cv=5, random_state=random_seed, alphas=50, tol=1e-3, max_iter=1000)
    lasso.fit(X_boot_s, y_boot)
    
    return np.abs(lasso.coef_) > 1e-5


def compute_stability_scores(X, y, features, block_size=BLOCK_SIZE, n_bootstraps=N_BOOTSTRAPS):
    N, D = X.shape
    print(f"  [Stability Selection] Running {n_bootstraps} block bootstrap trials (block_size={block_size}) ...")
    
    # Pre-scale features once for stability selection
    X_scaled = StandardScaler().fit_transform(X).astype(np.float32)
    
    # Parallel execution across all CPU cores
    results = Parallel(n_jobs=-1)(
        delayed(_run_bootstrap_trial)(X_scaled, y, block_size, 42 + i)
        for i in range(n_bootstraps)
    )
    
    selection_counts = np.sum(results, axis=0)
    scores = selection_counts / n_bootstraps
    
    sorted_idx = np.argsort(scores)[::-1]
    print("  Feature stability scores:")
    for idx in sorted_idx:
        print(f"    {features[idx]:<20} : {scores[idx]:.2%}")
        
    return scores


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


def make_objective(pre_scaled_splits, y, sample_w, stability_scores, side="single",
                   tail_weight: float = 0.0):
    def objective(trial: optuna.Trial) -> float:
        model_type = trial.suggest_categorical("model_type", ["ridge", "lasso", "elasticnet", "huber"])
        # Suggest stability selection threshold as a hyperparameter
        stability_threshold = trial.suggest_float("stability_threshold", 0.4, 0.9, step=0.05)

        # Select indices where score >= threshold
        selected_indices = np.where(stability_scores >= stability_threshold)[0]
        # Keep at least 3 features to prevent empty subsets
        if len(selected_indices) < 3:
            selected_indices = np.argsort(stability_scores)[::-1][:3]

        if model_type == "ridge":
            alpha = trial.suggest_float("ridge_alpha", 1e-3, 1e4, log=True)
            model = Ridge(alpha=alpha, random_state=42)
        elif model_type == "lasso":
            alpha = trial.suggest_float("lasso_alpha", 1e-5, 1.0, log=True)
            model = Lasso(alpha=alpha, random_state=42, max_iter=1000, tol=1e-3)
        elif model_type == "elasticnet":
            alpha = trial.suggest_float("en_alpha", 1e-5, 1.0, log=True)
            l1_ratio = trial.suggest_float("en_l1_ratio", 0.0, 1.0)
            model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42, max_iter=1000, tol=1e-3)
        elif model_type == "huber":
            alpha = trial.suggest_float("huber_alpha", 1e-4, 1e4, log=True)
            epsilon = trial.suggest_float("huber_epsilon", 1.0, 2.0)
            model = HuberRegressor(alpha=alpha, epsilon=epsilon, max_iter=2000)

        ics = []
        tail_ics = []
        for Xtr_s, Xte_s, train_idx, test_idx in pre_scaled_splits:
            Xtr_sel = Xtr_s[:, selected_indices]
            Xte_sel = Xte_s[:, selected_indices]

            model.fit(Xtr_sel, y[train_idx], sample_weight=sample_w[train_idx])
            preds = model.predict(Xte_sel)
            ics.append(_side_ic(y[test_idx], preds, side))
            tail_ics.append(_tail_ic(y[test_idx], preds, side))

        mean_ic = float(np.mean(ics)) if ics else -1.0
        mean_tail = float(np.mean(tail_ics)) if tail_ics else -1.0
        # Phase 2.5: blend overall IC with tail IC to align with trading
        return (1.0 - tail_weight) * mean_ic + tail_weight * mean_tail
    return objective


# ============================================================
# Train + evaluate one ETF
# ============================================================
def train_etf(etf_name: str, n_trials: int, n_splits: int, gap: int,
              side: str = "single") -> dict:
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
    Y_SCALE = 100.0
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

    # ── 1) Holdout: last 20% is final OOS (never used in Optuna) ──
    holdout_n = int(n * HOLDOUT_FRACTION)
    train_dev_idx = np.arange(0, n - holdout_n)
    holdout_idx = np.arange(n - holdout_n, n)
    X_dev, y_dev, dates_dev = X[train_dev_idx], y[train_dev_idx], dates[train_dev_idx]
    X_ho, y_ho, dates_ho = X[holdout_idx], y[holdout_idx], dates[holdout_idx]
    sw_dev = sample_w[train_dev_idx]
    y_clip_dev = y_clip[train_dev_idx]
    print(f"  dev (Optuna): {len(X_dev)}, holdout (final OOS): {len(X_ho)}")

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
    stability_scores = compute_stability_scores(X_dev, stab_target, FEATURES)

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
        sampler=optuna.samplers.TPESampler(seed=42),
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
    obj = make_objective(pre_scaled_splits, y_dev, sw_dev, stability_scores,
                         side=side, tail_weight=tail_weight)
    study.optimize(obj, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_cv_ic = study.best_value
    print(f"  best CV IC: {best_cv_ic:.4f}  params: {best_params}")

    # ── 4) Final model: train on all dev data, evaluate on holdout ──
    scaler = StandardScaler().fit(X_dev)
    X_dev_s = scaler.transform(X_dev)
    X_ho_s = scaler.transform(X_ho)

    best_threshold = best_params["stability_threshold"]
    selected_indices = np.where(stability_scores >= best_threshold)[0]
    if len(selected_indices) < 3:
        selected_indices = np.argsort(stability_scores)[::-1][:3]
    selected_features = [FEATURES[i] for i in selected_indices]
    print(f"  Final selected features ({len(selected_features)}): {selected_features}")

    X_dev_sel = X_dev_s[:, selected_indices]
    X_ho_sel = X_ho_s[:, selected_indices]

    model_type = best_params["model_type"]
    if model_type == "ridge":
        final_model = Ridge(alpha=best_params["ridge_alpha"], random_state=42)
    elif model_type == "lasso":
        final_model = Lasso(alpha=best_params["lasso_alpha"], random_state=42, max_iter=5000)
    elif model_type == "elasticnet":
        final_model = ElasticNet(alpha=best_params["en_alpha"], l1_ratio=best_params["en_l1_ratio"], random_state=42, max_iter=5000)
    elif model_type == "huber":
        final_model = HuberRegressor(alpha=best_params["huber_alpha"], epsilon=best_params["huber_epsilon"], max_iter=2000)

    final_model.fit(X_dev_sel, y_dev, sample_weight=sw_dev)
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

        if model_type == "ridge":
            m = Ridge(alpha=best_params["ridge_alpha"], random_state=42)
        elif model_type == "lasso":
            m = Lasso(alpha=best_params["lasso_alpha"], random_state=42, max_iter=5000)
        elif model_type == "elasticnet":
            m = ElasticNet(alpha=best_params["en_alpha"], l1_ratio=best_params["en_l1_ratio"], random_state=42, max_iter=5000)
        elif model_type == "huber":
            m = HuberRegressor(alpha=best_params["huber_alpha"], epsilon=best_params["huber_epsilon"], max_iter=2000)

        m.fit(Xtr_sel, y[train_idx], sample_weight=sample_w[train_idx])
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

    # ── 9) Standardized Coefficients & Permutation Importance ──
    coefs = np.zeros(len(FEATURES))
    coefs[selected_indices] = final_model.coef_
    coef_imp = dict(zip(FEATURES, coefs.tolist()))

    perm = permutation_importance(
        final_model, X_ho_sel, y_ho, n_repeats=10, random_state=42,
        scoring="neg_mean_squared_error", n_jobs=-1,
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

            if model_type == "ridge":
                m = Ridge(alpha=best_params["ridge_alpha"], random_state=42)
            elif model_type == "lasso":
                m = Lasso(alpha=best_params["lasso_alpha"], random_state=42, max_iter=5000)
            elif model_type == "elasticnet":
                m = ElasticNet(alpha=best_params["en_alpha"], l1_ratio=best_params["en_l1_ratio"], random_state=42, max_iter=5000)
            elif model_type == "huber":
                m = HuberRegressor(alpha=best_params["huber_alpha"], epsilon=best_params["huber_epsilon"], max_iter=2000)

            m.fit(Xtr_sel, y[train_idx], sample_weight=sample_w[train_idx])
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
                 "sample_weight_lambda": 0.5 if side != "single" else 0.0},
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
        s = pd.Series(imp).sort_values()
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
                                gap=args.gap, side=side)
                if res:
                    key = res.get("tag", etf)
                    all_results[key] = res
                    suffix = "" if side == "single" else f"_{side}"
                    with open(DATA_DIR / f"results_{etf}{suffix}.json", "w") as f:
                        json.dump(res, f, indent=2, default=str)
            except Exception as e:
                print(f"  [ERROR] {etf} ({side}): {e}")
                import traceback; traceback.print_exc()

    print("\n" + "=" * 90)
    print(f"{'Tag':<18} {'Model Type':<12} {'Threshold':<10} {'Features':<8} {'Holdout IC':>10} {'Holdout Dir':>12} {'L/S Sharpe':>12} {'Ridge IC':>10}")
    print("-" * 90)
    for key, r in all_results.items():
        best_model = r["best_params"]["model_type"].upper()
        threshold = r["best_params"]["stability_threshold"]
        n_sel_feats = r["n_selected_features"]
        ridge_ic = r["baselines"]["ridge"]["ic"]
        print(f"{key:<18} {best_model:<12} {threshold:<10.2f} {n_sel_feats:<8d} {r['holdout_ic']:>10.4f} {r['holdout_dir_acc']:>12.3f} "
              f"{r['holdout_long_short']['ls_sharpe']:>12.2f} {ridge_ic:>10.4f}")
    print("=" * 90)

    results_tag = "all" + ("" if args.side == "single" else f"_{args.side}")
    with open(DATA_DIR / f"results_{results_tag}.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    total_time = time.time() - t_start
    print(f"\nTotal wall time: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Combined results → {DATA_DIR / f'results_{results_tag}.json'}")


if __name__ == "__main__":
    main()
