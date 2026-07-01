"""
Tradability / Big-Move Gating Classifier.

Trains per-side classifiers that predict whether a day will see a large
directional move (big-up for long, big-down for short), to be used as a veto
gate over the daytrade directional pipeline.

Three target variants (best per ETF×side is auto-selected by honest OOS metric):
  - two_sided : per-side binary big-move (legacy behaviour).
  - joint3    : one 3-class softmax {big_up, neutral, big_down}; long uses
                P(big_up), short uses P(big_down). Shares signal between sides.
  - gated     : two-stage — big-move label ANDed with a tradability/regime mask
                (rolling vol20 / early_range regime). Single binary classifier.

Three feature selectors (best per cell auto-selected):
  - none      : all 238 features (legacy baseline).
  - stability : regime-stratified block bootstrap + randomized ElasticNet +
                OOB IC screen + variance cap (ported via feature_select.py).
  - lgbm      : walk-forward LightGBM gain + permutation importance.

IS/OOS protocol:
  - Dev/Holdout chronological 80/20 split.
  - Purged expanding-window walk-forward CV inside Dev.
  - "dev_only_oos"        : honest holdout metric of the dev-trained model
                            (the unbiased generalization estimate reported).
  - "forward_wf_estimate" : pooled purged walk-forward OOS metric over the
                            *entire* dataset — what the deployed (dev+holdout
                            retrained) model is expected to deliver.
  - Deployed artifact is retrained on Dev+Holdout (more data = better); the
    two metrics above are the honest estimates for it.

Outputs (per ETF × side × variant × selector):
  - gating_model/gating_{etf}_{side}_{variant}_{selector}.joblib
  - gating_model/gating_scaler_{etf}_{side}_{variant}_{selector}.joblib
  - gating_model/report_{etf}_{side}_{variant}_{selector}.json
Promoted winner (backward compatible):
  - gating_model/gating_{etf}_{side}.joblib
  - gating_model/gating_scaler_{etf}_{side}.joblib
  - gating_model/report_{etf}_{side}.json   (includes chosen variant+selector)
"""
import argparse
import json
import shutil
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    roc_auc_score, average_precision_score,
    precision_score, recall_score, f1_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
import optuna

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
OUT_DIR = HERE / "gating_model"
PLOTS_DIR = OUT_DIR / "plots"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

import sys
sys.path.append(str(HERE))
from build_features import FEATURES
from feature_select import select_stability, select_lgbm_importance

TARGET = "trade_return"

ETF_CLI_MAP = {
    "300": "300ETF", "50": "50ETF", "500": "500ETF",
    "588000": "588000ETF", "159915": "159915ETF",
    "300ETF": "300ETF", "50ETF": "50ETF", "500ETF": "500ETF",
    "588000ETF": "588000ETF", "159915ETF": "159915ETF",
    "all": ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"],
}

# Defaults
DEFAULT_N_SPLITS = 5
DEFAULT_PURGE_GAP = 5
HOLDOUT_FRACTION = 0.20
MIN_RETURN_THRESHOLD = 0.003
DEFAULT_QUANTILE = 0.70

MODEL_TYPES = ["logistic", "lightgbm"]  # RF dropped: rarely wins & 3-4× slower. Use --models rf to re-enable.
JOINT3_MODEL_TYPES = ["lightgbm", "logistic"]   # multiclass-friendly

VARIANTS = ["two_sided", "joint3", "gated"]
SELECTORS = ["none", "stability", "lgbm"]

# Optuna / parallelism
import os as _os
# Threads per Optuna study. With 5 ETFs run as separate processes (main),
# 2 threads/ETF × 5 workers = 10 threads on a 12-core box (safe).
_OPTUNA_NJOBS = max(1, min(2, (_os.cpu_count() or 4) // 6)) or 1

# Tradability mask regime thresholds (for `gated` variant)
TRADE_MASK_WINDOW = 60          # rolling window (trading days) for vol20 percentile
TRADE_MASK_VOL20_PCT = 40       # vol20 must be above rolling p40
TRADE_MASK_EARLYRANGE_PCT = 40  # OR early_range above rolling p40

# Cache for joint3 multiclass models, keyed by (etf, selector)
_JOINT3_CACHE: dict = {}


# ============================================================
# Splits & metrics
# ============================================================
def purged_tssplit(n: int, n_splits: int, gap: int):
    """Yields (train_idx, test_idx) with a purge gap to prevent leakage."""
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


def compute_metrics(y_true, y_prob, threshold_pct=70.0) -> dict:
    if len(np.unique(y_true)) < 2:
        return {"auc": 0.5, "pr_auc": 0.0, "precision_at_thr": 0.0,
                "recall_at_thr": 0.0, "f1_at_thr": 0.0, "firing_threshold": 0.0}
    auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    thr = np.percentile(y_prob, threshold_pct)
    y_pred = (y_prob >= thr).astype(int)
    return {
        "auc": float(auc),
        "pr_auc": float(pr_auc),
        "precision_at_thr": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_at_thr": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_at_thr": float(f1_score(y_true, y_pred, zero_division=0)),
        "firing_threshold": float(thr),
    }


def _sharpe(rets: np.ndarray) -> float:
    s = np.std(rets)
    return float(np.mean(rets) / s * np.sqrt(252)) if s > 1e-12 else 0.0


# ============================================================
# Model factory
# ============================================================
def build_model(model_type: str, params: dict, n_classes: int = 2):
    if model_type == "logistic":
        if n_classes >= 3:
            # liblinear doesn't support multiclass; use multinomial lbfgs
            return LogisticRegression(
                C=params["C"], penalty="l2", solver="lbfgs",
                random_state=42, max_iter=1000,
            )
        return LogisticRegression(
            C=params["C"], penalty=params["penalty"],
            solver="liblinear" if params["penalty"] == "l1" else "lbfgs",
            random_state=42, max_iter=1000,
        )
    elif model_type == "rf":
        return RandomForestClassifier(
            n_estimators=params["n_estimators"], max_depth=params["max_depth"],
            min_samples_split=params["min_samples_split"],
            random_state=42, n_jobs=1,
        )
    elif model_type == "lightgbm":
        return LGBMClassifier(
            n_estimators=params["n_estimators"], learning_rate=params["learning_rate"],
            num_leaves=params["num_leaves"], max_depth=params["max_depth"],
            min_child_samples=params["min_child_samples"],
            random_state=42, n_jobs=1, verbose=-1,
        )
    raise ValueError(f"Unknown model type: {model_type}")


def get_optuna_params(trial, model_type: str) -> dict:
    if model_type == "logistic":
        return {
            "C": trial.suggest_float("C", 1e-4, 10.0, log=True),
            "penalty": trial.suggest_categorical("penalty", ["l1", "l2"]),
        }
    elif model_type == "rf":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 30, 120),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 15),
        }
    elif model_type == "lightgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 20, 100),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 7, 31),
            "max_depth": trial.suggest_int("max_depth", 3, 6),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 40),
        }
    raise ValueError(f"Unknown model type: {model_type}")


# ============================================================
# Labeling
# ============================================================
def _side_threshold(y_raw_slice: np.ndarray, side: str,
                    quantile_k: float, min_ret: float) -> float:
    if side == "long":
        pos = y_raw_slice[y_raw_slice > 0]
        if len(pos) > 10:
            return max(min_ret, float(np.quantile(pos, quantile_k)))
        return max(min_ret, float(np.quantile(y_raw_slice, 0.70)))
    else:
        neg = np.abs(y_raw_slice[y_raw_slice < 0])
        if len(neg) > 10:
            return max(min_ret, float(np.quantile(neg, quantile_k)))
        return max(min_ret, float(np.quantile(np.abs(y_raw_slice), 0.70)))


def label_two_sided(y_raw_slice: np.ndarray, threshold: float, side: str) -> np.ndarray:
    if side == "long":
        return (y_raw_slice >= threshold).astype(int)
    return (y_raw_slice <= -threshold).astype(int)


def label_joint3(y_raw_slice: np.ndarray, up_thr: float, dn_thr: float) -> np.ndarray:
    """3-class: 0=neutral, 1=big_up, 2=big_down."""
    labels = np.zeros(len(y_raw_slice), dtype=int)
    labels[y_raw_slice >= up_thr] = 1
    labels[y_raw_slice <= -dn_thr] = 2
    return labels


def compute_tradable_mask(feat: pd.DataFrame) -> np.ndarray:
    """Boolean regime mask: vol20 or early_range above rolling p40 (causal)."""
    vol20 = feat["vol20"].values if "vol20" in feat.columns else np.zeros(len(feat))
    er = feat["early_range"].values if "early_range" in feat.columns else np.zeros(len(feat))
    n = len(feat)
    mask = np.zeros(n, dtype=bool)
    for t in range(TRADE_MASK_WINDOW, n):
        window = slice(t - TRADE_MASK_WINDOW, t)
        vol_p = np.nanpercentile(vol20[window], TRADE_MASK_VOL20_PCT)
        er_p = np.nanpercentile(er[window], TRADE_MASK_EARLYRANGE_PCT)
        mask[t] = (vol20[t] > vol_p) or (er[t] > er_p)
    return mask


# ============================================================
# Walk-forward evaluation
# ============================================================
def evaluate_oos_walkforward(precomputed_folds, model_type: str, params: dict):
    """Binary walk-forward eval on pre-scaled folds."""
    oos_preds, oos_targets = [], []
    fold_metrics = []
    for fold, (X_tr_s, y_tr, X_te_s, y_te) in enumerate(precomputed_folds):
        model = build_model(model_type, params)
        model.fit(X_tr_s, y_tr)
        prob = model.predict_proba(X_te_s)[:, 1]
        m = compute_metrics(y_te, prob)
        m["fold"] = fold
        m["base_rate"] = float(np.mean(y_te))
        fold_metrics.append(m)
        oos_preds.extend(prob)
        oos_targets.extend(y_te)
    oos_preds = np.array(oos_preds); oos_targets = np.array(oos_targets)
    overall = compute_metrics(oos_targets, oos_preds)
    overall["base_rate"] = float(np.mean(oos_targets))
    return overall, fold_metrics


def evaluate_joint3_walkforward(precomputed_folds, model_type: str, params: dict):
    """3-class walk-forward eval. Returns (long_metrics, short_metrics, fold_metrics)
    where long/short metrics use P(big_up) / P(big_down) as the score vs the
    per-side binary target."""
    long_preds, long_tgts = [], []
    short_preds, short_tgts = [], []
    fold_metrics = []
    for fold, (X_tr_s, y3_tr, X_te_s, y3_te) in enumerate(precomputed_folds):
        model = build_model(model_type, params, n_classes=3)
        model.fit(X_tr_s, y3_tr)
        prob = model.predict_proba(X_te_s)
        # Map class index: 0=neutral, 1=up, 2=down
        p_up = prob[:, list(model.classes_).index(1)] if 1 in model.classes_ else np.zeros(len(y3_te))
        p_dn = prob[:, list(model.classes_).index(2)] if 2 in model.classes_ else np.zeros(len(y3_te))
        long_bin = (y3_te == 1).astype(int)
        short_bin = (y3_te == 2).astype(int)
        long_preds.extend(p_up); long_tgts.extend(long_bin)
        short_preds.extend(p_dn); short_tgts.extend(short_bin)
    long_preds = np.array(long_preds); long_tgts = np.array(long_tgts)
    short_preds = np.array(short_preds); short_tgts = np.array(short_tgts)
    long_m = compute_metrics(long_tgts, long_preds); long_m["base_rate"] = float(np.mean(long_tgts))
    short_m = compute_metrics(short_tgts, short_preds); short_m["base_rate"] = float(np.mean(short_tgts))
    return long_m, short_m, fold_metrics


# ============================================================
# Feature selection wrapper
# ============================================================
def select_features(selector: str, X_dev: np.ndarray, y_dev_raw: np.ndarray,
                    y_dev_bin: np.ndarray, features: list, side: str,
                    variant: str) -> list:
    """Return the selected feature-name subset for the chosen selector."""
    if selector == "none":
        return list(features)
    # For stability: regress on side-clip target (matches train_model.py dual mode)
    if side == "long":
        y_reg = np.maximum(0.0, y_dev_raw)
    else:
        y_reg = np.maximum(0.0, -y_dev_raw)
    if selector == "stability":
        return select_stability(X_dev, y_reg, features, n_bootstraps=30, n_jobs=-1)
    elif selector == "lgbm":
        # For joint3 use raw; otherwise use the binary label
        if variant == "joint3":
            return select_lgbm_importance(
                X_dev, np.abs(y_dev_raw), features,
                task="regression", top_n=25, n_jobs=-1,
            )
        return select_lgbm_importance(
            X_dev, y_dev_bin, features,
            task="classification", top_n=25, n_jobs=-1,
        )
    raise ValueError(f"Unknown selector: {selector}")


# ============================================================
# Core training: one (etf, side, variant, selector) config
# ============================================================
def _train_binary_config(
    etf: str, side: str, variant: str, selector: str,
    X: np.ndarray, y_raw: np.ndarray, feat: pd.DataFrame, features_used: list,
    n_trials: int, n_splits: int, gap: int,
    quantile_k: float, min_ret: float,
):
    """Train and evaluate a binary config (two_sided or gated). Returns meta dict."""
    n = len(X)
    dev_size = int(n * (1 - HOLDOUT_FRACTION))
    X_dev, y_dev_raw = X[:dev_size], y_raw[:dev_size]
    X_ho, y_ho_raw = X[dev_size:], y_raw[dev_size:]

    # Thresholds (fit on dev only — no leak)
    dev_thr = _side_threshold(y_dev_raw, side, quantile_k, min_ret)
    final_thr = _side_threshold(y_raw, side, quantile_k, min_ret)

    # Tradable mask (for gated variant)
    if variant == "gated":
        full_mask = compute_tradable_mask(feat)
        dev_mask = full_mask[:dev_size]
        ho_mask = full_mask[dev_size:]
    else:
        dev_mask = np.ones(dev_size, dtype=bool)
        ho_mask = np.ones(n - dev_size, dtype=bool)

    # Precompute CV folds on dev (using dev threshold; mask applied to label)
    cv_splits = list(purged_tssplit(dev_size, n_splits, gap))
    precomputed_folds = []
    for train_idx, test_idx in cv_splits:
        tr_raw = y_dev_raw[train_idx]
        # Per-fold threshold fit on its own train (no leak)
        fold_thr = _side_threshold(tr_raw, side, quantile_k, min_ret)
        tr_bin = label_two_sided(tr_raw, fold_thr, side)
        te_bin = label_two_sided(y_dev_raw[test_idx], fold_thr, side)
        if variant == "gated":
            tr_mask = dev_mask[train_idx]
            te_mask = dev_mask[test_idx]
            tr_bin = tr_bin & tr_mask.astype(int)
            te_bin = te_bin & te_mask.astype(int)
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_dev[train_idx])
        X_te_s = scaler.transform(X_dev[test_idx])
        precomputed_folds.append((X_tr_s, tr_bin, X_te_s, te_bin))

    # Dev/Holdout labels (dev threshold)
    y_dev_bin = label_two_sided(y_dev_raw, dev_thr, side) & dev_mask.astype(int)
    y_ho_bin = label_two_sided(y_ho_raw, dev_thr, side) & ho_mask.astype(int)

    # Benchmark model types
    results = {}
    for model_type in MODEL_TYPES:
        t0 = time.time()

        def objective(trial):
            params = get_optuna_params(trial, model_type)
            overall, _ = evaluate_oos_walkforward(precomputed_folds, model_type, params)
            return overall["pr_auc"] + 0.5 * overall["auc"]

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, n_jobs=_OPTUNA_NJOBS)
        best_params = study.best_params

        cv_overall, fold_metrics = evaluate_oos_walkforward(precomputed_folds, model_type, best_params)

        # Holdout: honest dev-trained model
        scaler = StandardScaler()
        X_dev_s = scaler.fit_transform(X_dev)
        X_ho_s = scaler.transform(X_ho)
        full_model = build_model(model_type, best_params)
        full_model.fit(X_dev_s, y_dev_bin)
        ho_prob = full_model.predict_proba(X_ho_s)[:, 1]
        ho_metrics = compute_metrics(y_ho_bin, ho_prob)
        ho_metrics["base_rate"] = float(np.mean(y_ho_bin))

        results[model_type] = {
            "best_params": best_params,
            "cv_metrics": cv_overall,
            "fold_metrics": fold_metrics,
            "dev_only_oos": ho_metrics,            # honest holdout (dev-trained)
            "forward_wf_estimate": None,           # filled only for the winner
        }
        elapsed = time.time() - t0
        print(f"  [{variant}/{selector}] {model_type}: {elapsed:.1f}s "
              f"cv_PR={cv_overall['pr_auc']:.3f} HO_PR={ho_metrics['pr_auc']:.3f}")

    # Pick CV-winner by CV PR-AUC; compute the expensive forward_wf only for it.
    best_model_type = max(results, key=lambda m: results[m]["cv_metrics"]["pr_auc"])
    best_params = results[best_model_type]["best_params"]
    wf_overall = _forward_wf_full_binary(
        X, y_raw, features_used, side, variant,
        full_mask if variant == "gated" else None,
        best_model_type, best_params, quantile_k, min_ret, n_splits, gap,
    )
    results[best_model_type]["forward_wf_estimate"] = wf_overall
    print(f"  [{variant}/{selector}] WINNER={best_model_type} WF_PR={wf_overall['pr_auc']:.3f} WF_AUC={wf_overall['auc']:.3f}")

    # Use best dev-model holdout predictions for plotting
    scaler = StandardScaler()
    X_dev_s = scaler.fit_transform(X_dev)
    X_ho_s = scaler.transform(X_ho)
    ho_model = build_model(best_model_type, best_params)
    ho_model.fit(X_dev_s, y_dev_bin)
    ho_prob = ho_model.predict_proba(X_ho_s)[:, 1]

    # Retrain winning model on ALL data (Dev + Holdout) for deployment
    final_thr = _side_threshold(y_raw, side, quantile_k, min_ret)
    full_mask = compute_tradable_mask(feat) if variant == "gated" else np.ones(n, dtype=bool)
    y_all = label_two_sided(y_raw, final_thr, side) & full_mask.astype(int)

    scaler_final = StandardScaler()
    X_scaled = scaler_final.fit_transform(X)
    final_model = build_model(best_model_type, best_params)
    final_model.fit(X_scaled, y_all)

    # Firing probability threshold = p70 of model's predicted probabilities
    # on its full training data (used at inference time by the daytrade loader).
    train_prob = final_model.predict_proba(X_scaled)[:, 1]
    firing_threshold = float(np.percentile(train_prob, 70))

    return {
        "model": final_model, "scaler": scaler_final,
        "best_model_type": best_model_type, "best_params": best_params,
        "final_threshold": float(final_thr),
        "firing_threshold": firing_threshold,
        "features_used": features_used,
        "results": results,
        "ho_prob": ho_prob, "y_ho_bin": y_ho_bin,  # for plotting (last model)
    }


def _forward_wf_full_binary(X, y_raw, features, side, variant, full_mask,
                            model_type, params, quantile_k, min_ret, n_splits, gap):
    """Pooled purged walk-forward over the entire dataset.
    Returns metrics that estimate deployed-model OOS behaviour."""
    n = len(X)
    splits = list(purged_tssplit(n, n_splits, gap))
    oos_preds, oos_tgts = [], []
    for train_idx, test_idx in splits:
        tr_raw = y_raw[train_idx]
        thr = _side_threshold(tr_raw, side, quantile_k, min_ret)
        tr_bin = label_two_sided(tr_raw, thr, side)
        te_bin = label_two_sided(y_raw[test_idx], thr, side)
        if variant == "gated" and full_mask is not None:
            tr_bin = tr_bin & full_mask[train_idx].astype(int)
            te_bin = te_bin & full_mask[test_idx].astype(int)
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X[train_idx])
        X_te_s = scaler.transform(X[test_idx])
        model = build_model(model_type, params)
        model.fit(X_tr_s, tr_bin)
        if len(np.unique(tr_bin)) < 2:
            prob = np.full(len(test_idx), 0.5)
        else:
            prob = model.predict_proba(X_te_s)[:, 1]
        oos_preds.extend(prob); oos_tgts.extend(te_bin)
    oos_preds = np.array(oos_preds); oos_tgts = np.array(oos_tgts)
    if len(np.unique(oos_tgts)) < 2:
        return {"auc": 0.5, "pr_auc": 0.0, "precision_at_thr": 0.0,
                "recall_at_thr": 0.0, "f1_at_thr": 0.0,
                "base_rate": float(np.mean(oos_tgts)), "firing_threshold": 0.0}
    m = compute_metrics(oos_tgts, oos_preds)
    m["base_rate"] = float(np.mean(oos_tgts))
    return m


# ============================================================
# Joint3 config (one model per etf, shared across sides)
# ============================================================
def _train_joint3_config(
    etf: str, selector: str,
    X: np.ndarray, y_raw: np.ndarray, feat: pd.DataFrame, features_used: list,
    n_trials: int, n_splits: int, gap: int,
    quantile_k: float, min_ret: float,
):
    """Train a 3-class softmax model. Returns meta dict with long/short metrics."""
    n = len(X)
    dev_size = int(n * (1 - HOLDOUT_FRACTION))
    X_dev, y_dev_raw = X[:dev_size], y_raw[:dev_size]
    X_ho, y_ho_raw = X[dev_size:], y_raw[dev_size:]

    up_thr_dev = _side_threshold(y_dev_raw, "long", quantile_k, min_ret)
    dn_thr_dev = _side_threshold(y_dev_raw, "short", quantile_k, min_ret)
    up_thr_all = _side_threshold(y_raw, "long", quantile_k, min_ret)
    dn_thr_all = _side_threshold(y_raw, "short", quantile_k, min_ret)

    cv_splits = list(purged_tssplit(dev_size, n_splits, gap))
    precomputed = []
    for train_idx, test_idx in cv_splits:
        tr_raw = y_dev_raw[train_idx]
        up_thr = _side_threshold(tr_raw, "long", quantile_k, min_ret)
        dn_thr = _side_threshold(tr_raw, "short", quantile_k, min_ret)
        y3_tr = label_joint3(tr_raw, up_thr, dn_thr)
        y3_te = label_joint3(y_dev_raw[test_idx], up_thr, dn_thr)
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_dev[train_idx])
        X_te_s = scaler.transform(X_dev[test_idx])
        precomputed.append((X_tr_s, y3_tr, X_te_s, y3_te))

    results = {}
    for model_type in JOINT3_MODEL_TYPES:
        t0 = time.time()

        def objective(trial):
            params = get_optuna_params(trial, model_type)
            long_m, short_m, _ = evaluate_joint3_walkforward(precomputed, model_type, params)
            return 0.5 * (long_m["pr_auc"] + short_m["pr_auc"]) + 0.25 * (long_m["auc"] + short_m["auc"])

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, n_jobs=_OPTUNA_NJOBS)
        best_params = study.best_params

        cv_long, cv_short, _ = evaluate_joint3_walkforward(precomputed, model_type, best_params)

        # Holdout (dev-trained)
        y3_dev = label_joint3(y_dev_raw, up_thr_dev, dn_thr_dev)
        y3_ho = label_joint3(y_ho_raw, up_thr_dev, dn_thr_dev)
        scaler = StandardScaler()
        X_dev_s = scaler.fit_transform(X_dev)
        X_ho_s = scaler.transform(X_ho)
        full_model = build_model(model_type, best_params, n_classes=3)
        full_model.fit(X_dev_s, y3_dev)
        prob_ho = full_model.predict_proba(X_ho_s)
        classes = list(full_model.classes_)
        p_up_ho = prob_ho[:, classes.index(1)] if 1 in classes else np.zeros(len(y3_ho))
        p_dn_ho = prob_ho[:, classes.index(2)] if 2 in classes else np.zeros(len(y3_ho))
        ho_long = compute_metrics((y3_ho == 1).astype(int), p_up_ho)
        ho_short = compute_metrics((y3_ho == 2).astype(int), p_dn_ho)

        results[model_type] = {
            "best_params": best_params,
            "cv_long": cv_long, "cv_short": cv_short,
            "dev_only_oos_long": ho_long, "dev_only_oos_short": ho_short,
            "forward_wf_long": None, "forward_wf_short": None,  # filled for winner only
        }
        elapsed = time.time() - t0
        print(f"  [joint3/{selector}] {model_type}: {elapsed:.1f}s "
              f"cv_L_PR={cv_long['pr_auc']:.3f} cv_S_PR={cv_short['pr_auc']:.3f}")

    # Pick CV-winner by mean CV PR-AUC; compute expensive forward_wf only for it.
    best_model_type = max(
        results,
        key=lambda m: results[m]["cv_long"]["pr_auc"] + results[m]["cv_short"]["pr_auc"],
    )
    best_params = results[best_model_type]["best_params"]
    wf_long, wf_short = _forward_wf_full_joint3(
        X, y_raw, best_model_type, best_params, quantile_k, min_ret, n_splits, gap,
    )
    results[best_model_type]["forward_wf_long"] = wf_long
    results[best_model_type]["forward_wf_short"] = wf_short
    print(f"  [joint3/{selector}] WINNER={best_model_type} "
          f"WF_L_PR={wf_long['pr_auc']:.3f} WF_S_PR={wf_short['pr_auc']:.3f}")

    # Retrain on all data
    y3_all = label_joint3(y_raw, up_thr_all, dn_thr_all)
    scaler_final = StandardScaler()
    X_scaled = scaler_final.fit_transform(X)
    final_model = build_model(best_model_type, best_params, n_classes=3)
    final_model.fit(X_scaled, y3_all)

    # Per-side firing probability thresholds (p70 of P(big_up) / P(big_down))
    prob_all = final_model.predict_proba(X_scaled)
    classes = list(final_model.classes_)
    p_up_all = prob_all[:, classes.index(1)] if 1 in classes else np.zeros(len(y3_all))
    p_dn_all = prob_all[:, classes.index(2)] if 2 in classes else np.zeros(len(y3_all))
    firing_thr_long = float(np.percentile(p_up_all, 70))
    firing_thr_short = float(np.percentile(p_dn_all, 70))

    return {
        "model": final_model, "scaler": scaler_final,
        "best_model_type": best_model_type, "best_params": best_params,
        "up_threshold": float(up_thr_all), "dn_threshold": float(dn_thr_all),
        "firing_threshold_long": firing_thr_long,
        "firing_threshold_short": firing_thr_short,
        "features_used": features_used,
        "results": results,
    }


def _forward_wf_full_joint3(X, y_raw, model_type, params, quantile_k, min_ret, n_splits, gap):
    n = len(X)
    splits = list(purged_tssplit(n, n_splits, gap))
    L_preds, L_tgts, S_preds, S_tgts = [], [], [], []
    for train_idx, test_idx in splits:
        tr_raw = y_raw[train_idx]
        up_thr = _side_threshold(tr_raw, "long", quantile_k, min_ret)
        dn_thr = _side_threshold(tr_raw, "short", quantile_k, min_ret)
        y3_tr = label_joint3(tr_raw, up_thr, dn_thr)
        y3_te = label_joint3(y_raw[test_idx], up_thr, dn_thr)
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X[train_idx])
        X_te_s = scaler.transform(X[test_idx])
        model = build_model(model_type, params, n_classes=3)
        if len(np.unique(y3_tr)) < 2:
            p_up = np.full(len(test_idx), 0.5); p_dn = np.full(len(test_idx), 0.5)
        else:
            model.fit(X_tr_s, y3_tr)
            prob = model.predict_proba(X_te_s)
            classes = list(model.classes_)
            p_up = prob[:, classes.index(1)] if 1 in classes else np.zeros(len(test_idx))
            p_dn = prob[:, classes.index(2)] if 2 in classes else np.zeros(len(test_idx))
        L_preds.extend(p_up); L_tgts.extend((y3_te == 1).astype(int))
        S_preds.extend(p_dn); S_tgts.extend((y3_te == 2).astype(int))
    L_preds = np.array(L_preds); L_tgts = np.array(L_tgts)
    S_preds = np.array(S_preds); S_tgts = np.array(S_tgts)
    long_m = compute_metrics(L_tgts, L_preds) if len(np.unique(L_tgts)) > 1 else compute_metrics(L_tgts, L_preds)
    short_m = compute_metrics(S_tgts, S_preds) if len(np.unique(S_tgts)) > 1 else compute_metrics(S_tgts, S_preds)
    long_m["base_rate"] = float(np.mean(L_tgts))
    short_m["base_rate"] = float(np.mean(S_tgts))
    return long_m, short_m


# ============================================================
# Per-ETF orchestration
# ============================================================
def train_etf_all_configs(
    etf: str, variants, selectors,
    n_trials: int, n_splits: int, gap: int,
    quantile_k: float, min_ret: float,
):
    """Train every (variant × selector) config for an ETF; save suffixed artifacts."""
    feat_path = DATA_DIR / f"features_{etf}.parquet"
    if not feat_path.exists():
        print(f"[SKIP] {feat_path.name} not found.")
        return None
    feat = pd.read_parquet(feat_path).sort_index()
    feat = feat.dropna(subset=FEATURES + [TARGET]).copy()
    X_full = feat[FEATURES].values.astype(np.float32)
    y_raw = feat[TARGET].values.astype(np.float32)
    n = len(feat)
    dev_size = int(n * (1 - HOLDOUT_FRACTION))
    print(f"\n### {etf}: {n} days (dev={dev_size}, ho={n - dev_size})")

    # Cache feature subsets per selector (dev-only fit, no leak)
    feat_subset_cache = {}
    for selector in selectors:
        if selector == "none":
            feat_subset_cache[selector] = list(FEATURES)
            continue
        # Compute binary labels for selection (use dev long+short combined tail)
        y_dev_raw = y_raw[:dev_size]
        thr_long = _side_threshold(y_dev_raw, "long", quantile_k, min_ret)
        y_long_bin = label_two_sided(y_dev_raw, thr_long, "long")
        # Use long side for selector (representative); store subset
        print(f"  [selector={selector}] computing feature subset on dev...")
        sub = select_features(selector, X_full[:dev_size], y_dev_raw, y_long_bin,
                              list(FEATURES), "long", "two_sided")
        feat_subset_cache[selector] = sub
        print(f"    -> {len(sub)} features selected")

    # Cache joint3 model per selector
    joint3_models = {}

    # Iterate variants × selectors × sides
    for variant in variants:
        for selector in selectors:
            features_used = feat_subset_cache[selector]
            X = feat[features_used].values.astype(np.float32)
            if variant == "joint3":
                if (selector) not in joint3_models:
                    print(f"\n--- {etf} variant=joint3 selector={selector} (shared 3-class model) ---")
                    joint3_models[selector] = _train_joint3_config(
                        etf, selector, X, y_raw, feat, features_used,
                        n_trials, n_splits, gap, quantile_k, min_ret,
                    )
                meta = joint3_models[selector]
                # Derive per-side reports from the shared joint3 model
                for side in ("long", "short"):
                    _save_joint3_side_artifacts(
                        etf, side, selector, meta, features_used, n_splits, gap,
                    )
            else:  # two_sided / gated
                for side in ("long", "short"):
                    print(f"\n--- {etf} variant={variant} selector={selector} side={side} ---")
                    meta = _train_binary_config(
                        etf, side, variant, selector,
                        X, y_raw, feat, features_used,
                        n_trials, n_splits, gap, quantile_k, min_ret,
                    )
                    _save_binary_artifacts(etf, side, variant, selector, meta, features_used)

    # Pick winner per side across all configs
    for side in ("long", "short"):
        _select_and_promote(etf, side, variants, selectors)


def _save_binary_artifacts(etf, side, variant, selector, meta, features_used):
    suffix = f"{variant}_{selector}"
    joblib.dump(meta["model"], OUT_DIR / f"gating_{etf}_{side}_{suffix}.joblib")
    joblib.dump(meta["scaler"], OUT_DIR / f"gating_scaler_{etf}_{side}_{suffix}.joblib")
    report = {
        "etf": etf, "side": side, "variant": variant, "selector": selector,
        "best_model_type": meta["best_model_type"], "best_params": meta["best_params"],
        "final_threshold": meta["final_threshold"],
        "firing_threshold": meta["firing_threshold"],
        "features_used": features_used, "n_features": len(features_used),
        "results": _jsonify(meta["results"]),
    }
    with open(OUT_DIR / f"report_{etf}_{side}_{suffix}.json", "w") as f:
        json.dump(report, f, indent=4)
    # Plot for this config
    try:
        _plot_curves(etf, side, suffix, meta["y_ho_bin"], meta["ho_prob"], meta["best_model_type"])
    except Exception:
        pass


def _save_joint3_side_artifacts(etf, side, selector, meta, features_used, n_splits, gap):
    variant = "joint3"
    suffix = f"{variant}_{selector}"
    # Save model + scaler once per etf (shared). Save under both side paths.
    model_path = OUT_DIR / f"gating_{etf}_{side}_{suffix}.joblib"
    scaler_path = OUT_DIR / f"gating_scaler_{etf}_{side}_{suffix}.joblib"
    joblib.dump(meta["model"], model_path)
    joblib.dump(meta["scaler"], scaler_path)
    # Pull the side-specific metrics from the best model
    best = meta["best_model_type"]
    wf = meta["results"][best][f"forward_wf_{side}"]
    dev_oos = meta["results"][best][f"dev_only_oos_{side}"]
    cv = meta["results"][best][f"cv_{side}"]
    report = {
        "etf": etf, "side": side, "variant": variant, "selector": selector,
        "best_model_type": best, "best_params": meta["best_params"],
        "final_threshold": float(meta["up_threshold"] if side == "long" else meta["dn_threshold"]),
        "firing_threshold": float(meta["firing_threshold_long"] if side == "long" else meta["firing_threshold_short"]),
        "features_used": features_used, "n_features": len(features_used),
        "results": {
            best: {
                "cv_metrics": cv,
                "dev_only_oos": dev_oos,
                "forward_wf_estimate": wf,
            }
        },
        "joint3_class": side,  # which class index this side uses
    }
    with open(OUT_DIR / f"report_{etf}_{side}_{suffix}.json", "w") as f:
        json.dump(report, f, indent=4)


def _select_and_promote(etf, side, variants, selectors):
    """Read all config reports for (etf, side), pick the one with max
    forward_wf_estimate.pr_auc subject to deployability, copy to canonical name."""
    candidates = []
    for variant in variants:
        for selector in selectors:
            p = OUT_DIR / f"report_{etf}_{side}_{variant}_{selector}.json"
            if not p.exists():
                continue
            with open(p) as f:
                rep = json.load(f)
            # Find the best-model-type entry
            best_mt = rep["best_model_type"]
            res = rep["results"].get(best_mt, {})
            # forward_wf may be under forward_wf_estimate (binary) or already flattened (joint3)
            wf = res.get("forward_wf_estimate") or res.get("forward_wf_long") or res.get("forward_wf_short")
            dev_oos = res.get("dev_only_oos")
            cv = res.get("cv_metrics") or res.get(f"cv_{side}")
            if wf is None:
                continue
            candidates.append({
                "variant": variant, "selector": selector,
                "best_model_type": best_mt,
                "wf_pr_auc": wf["pr_auc"], "wf_auc": wf["auc"],
                "wf_prec": wf["precision_at_thr"],
                "dev_pr_auc": dev_oos["pr_auc"] if dev_oos else None,
                "cv_pr_auc": cv["pr_auc"] if cv else None,
                "base_rate": wf.get("base_rate", 0.0),
            })
    if not candidates:
        print(f"  [{etf}/{side}] no candidate configs.")
        return None

    # Deployability filter
    def deployable(c):
        return c["wf_auc"] > 0.53 and c["wf_pr_auc"] > c["base_rate"] and c["wf_prec"] > c["base_rate"] * 1.1

    eligible = [c for c in candidates if deployable(c)]
    pool = eligible if eligible else candidates
    # Pick max by WF PR-AUC, tiebreak WF AUC
    winner = max(pool, key=lambda c: (c["wf_pr_auc"], c["wf_auc"]))
    wsuffix = f"{winner['variant']}_{winner['selector']}"

    # Copy artifacts to canonical names
    src_model = OUT_DIR / f"gating_{etf}_{side}_{wsuffix}.joblib"
    src_scaler = OUT_DIR / f"gating_scaler_{etf}_{side}_{wsuffix}.joblib"
    shutil.copyfile(src_model, OUT_DIR / f"gating_{etf}_{side}.joblib")
    shutil.copyfile(src_scaler, OUT_DIR / f"gating_scaler_{etf}_{side}.joblib")

    # Write canonical report
    with open(OUT_DIR / f"report_{etf}_{side}_{wsuffix}.json") as f:
        rep = json.load(f)
    rep["chosen_variant"] = winner["variant"]
    rep["chosen_selector"] = winner["selector"]
    rep["selection_summary"] = {
        "n_candidates": len(candidates),
        "n_deployable": len(eligible),
        "winner": wsuffix,
        "winner_wf_pr_auc": winner["wf_pr_auc"],
        "winner_wf_auc": winner["wf_auc"],
        "all_candidates": candidates,
    }
    with open(OUT_DIR / f"report_{etf}_{side}.json", "w") as f:
        json.dump(rep, f, indent=4)

    print(f"  [{etf}/{side}] WINNER: {wsuffix}  WF_PR={winner['wf_pr_auc']:.3f} "
          f"WF_AUC={winner['wf_auc']:.3f}  (deployable={bool(eligible)})")
    return winner


def _jsonify(obj):
    """Recursively convert numpy scalars/arrays for JSON."""
    if isinstance(obj, dict):
        return {k: _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _plot_curves(etf, side, suffix, y_true, y_prob, model_name):
    from sklearn.metrics import roc_curve, precision_recall_curve, auc
    if len(np.unique(y_true)) < 2:
        return
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    plt.plot(fpr, tpr, label=f"ROC AUC = {auc(fpr, tpr):.3f}")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("FPR"); plt.ylabel("TPR")
    plt.title(f"ROC: {etf} {side} {suffix} ({model_name})")
    plt.legend(); plt.grid(True)
    plt.subplot(1, 2, 2)
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    pr = average_precision_score(y_true, y_prob)
    base = np.mean(y_true)
    plt.plot(rec, prec, label=f"PR AUC = {pr:.3f}")
    plt.axhline(y=base, color="r", linestyle="--", label=f"base={base:.2%}")
    plt.xlabel("Recall"); plt.ylabel("Precision")
    plt.title(f"PR: {etf} {side} {suffix} ({model_name})")
    plt.legend(); plt.grid(True)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"curves_{etf}_{side}_{suffix}.png", dpi=120)
    plt.close()


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all")
    parser.add_argument("-t", "--trials", type=int, default=30)
    parser.add_argument("-s", "--splits", type=int, default=DEFAULT_N_SPLITS)
    parser.add_argument("-g", "--gap", type=int, default=DEFAULT_PURGE_GAP)
    parser.add_argument("-q", "--quantile", type=float, default=DEFAULT_QUANTILE)
    parser.add_argument("-m", "--min_ret", type=float, default=MIN_RETURN_THRESHOLD)
    parser.add_argument("--variants", default=",".join(VARIANTS),
                        help=f"Comma-separated subset of {VARIANTS}")
    parser.add_argument("--selectors", default=",".join(SELECTORS),
                        help=f"Comma-separated subset of {SELECTORS}")
    parser.add_argument("--models", default=",".join(MODEL_TYPES),
                        help="Comma-separated subset of {logistic,rf,lightgbm}. "
                             "Default drops RF (rarely wins, 3-4× slower).")
    parser.add_argument("--jobs", type=int, default=0,
                        help="Number of ETFs to train in parallel (0 = all). "
                             "Each ETF also parallelizes Optuna internally.")
    args = parser.parse_args()

    # Override model types from CLI
    cli_models = [m.strip() for m in args.models.split(",") if m.strip()]
    valid_models = {"logistic", "rf", "lightgbm"}
    MODEL_TYPES[:] = [m for m in cli_models if m in valid_models] or ["logistic", "lightgbm"]
    JOINT3_MODEL_TYPES[:] = [m for m in MODEL_TYPES if m != "rf"] or ["lightgbm", "logistic"]

    variants = [v.strip() for v in args.variants.split(",") if v.strip() in VARIANTS]
    selectors = [s.strip() for s in args.selectors.split(",") if s.strip() in SELECTORS]
    if not variants or not selectors:
        raise SystemExit("Invalid --variants or --selectors.")

    etfs = ETF_CLI_MAP.get(args.etf, [args.etf])
    if isinstance(etfs, str):
        etfs = [etfs]

    if len(etfs) == 1 or args.jobs == 1:
        for etf in etfs:
            train_etf_all_configs(
                etf, variants, selectors,
                n_trials=args.trials, n_splits=args.splits, gap=args.gap,
                quantile_k=args.quantile, min_ret=args.min_ret,
            )
    else:
        # Parallelize across ETFs (each process also runs Optuna threads internally).
        # Cap parallelism to avoid CPU oversubscription.
        from concurrent.futures import ProcessPoolExecutor, as_completed
        n_workers = args.jobs if args.jobs > 0 else min(len(etfs), max(1, (_os.cpu_count() or 4) // 4))
        print(f"Parallelizing {len(etfs)} ETFs across {n_workers} workers "
              f"(Optuna n_jobs={_OPTUNA_NJOBS} per worker, models={MODEL_TYPES})")
        common_args = (variants, selectors, args.trials, args.splits, args.gap,
                       args.quantile, args.min_ret)
        with ProcessPoolExecutor(max_workers=n_workers) as ex:
            futures = {ex.submit(train_etf_all_configs, etf, *common_args): etf for etf in etfs}
            for fut in as_completed(futures):
                etf = futures[fut]
                try:
                    fut.result()
                    print(f"  [done] {etf}")
                except Exception as e:
                    print(f"  [ERROR] {etf}: {e}")
