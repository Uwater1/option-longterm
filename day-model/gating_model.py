"""
Tradability Pre-Gate Classifier.
Trains separate binary classifiers (long_gate, short_gate) to predict if a day is "tradable"
(i.e., will have a large positive or negative trade_return).
Benchmarks 3 models: LogisticRegression, RandomForest, LightGBM.
Optimized for speed: pre-scales and pre-labels CV folds to avoid duplicate scaling/math.
Uses Purged TimeSeriesSplit with Optuna tuning.
"""
import argparse
import json
import os
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
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score
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

# Import feature lists from build_features
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

# Default parameters
DEFAULT_N_SPLITS = 5
DEFAULT_PURGE_GAP = 5
HOLDOUT_FRACTION = 0.20
MIN_RETURN_THRESHOLD = 0.003  # 30 bps (covers 15 bps round-trip cost)
DEFAULT_QUANTILE = 0.70       # Top 30% of days (long/short separately)

MODEL_TYPES = ["logistic", "rf", "lightgbm"]


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


def build_model(model_type: str, params: dict):
    """Factory to build a model with given hyperparameters."""
    if model_type == "logistic":
        return LogisticRegression(
            C=params["C"],
            penalty=params["penalty"],
            solver="liblinear" if params["penalty"] == "l1" else "lbfgs",
            random_state=42,
            max_iter=1000
        )
    elif model_type == "rf":
        # Run RF with n_jobs=1 during tuning to avoid fork/process-creation overhead
        return RandomForestClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            min_samples_split=params["min_samples_split"],
            random_state=42,
            n_jobs=1
        )
    elif model_type == "lightgbm":
        return LGBMClassifier(
            n_estimators=params["n_estimators"],
            learning_rate=params["learning_rate"],
            num_leaves=params["num_leaves"],
            max_depth=params["max_depth"],
            min_child_samples=params["min_child_samples"],
            random_state=42,
            n_jobs=1,
            verbose=-1
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def get_optuna_params(trial, model_type: str) -> dict:
    """Defines search space for each model type."""
    if model_type == "logistic":
        return {
            "C": trial.suggest_float("C", 1e-4, 10.0, log=True),
            "penalty": trial.suggest_categorical("penalty", ["l1", "l2"])
        }
    elif model_type == "rf":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 30, 120),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 15)
        }
    elif model_type == "lightgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 20, 100),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 7, 31),
            "max_depth": trial.suggest_int("max_depth", 3, 6),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 40)
        }


def compute_metrics(y_true, y_prob, threshold_pct=70.0) -> dict:
    """Compute various classification and trading metrics.
    
    threshold_pct: percentile threshold for decision making (e.g. 70.0 means top 30% predicted probabilities fire).
    """
    if len(np.unique(y_true)) < 2:
        return {"auc": 0.5, "pr_auc": 0.0, "precision_at_thr": 0.0, "recall_at_thr": 0.0, "f1_at_thr": 0.0}
    
    auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    
    # Calculate decision threshold based on predicted probability percentile
    thr = np.percentile(y_prob, threshold_pct)
    y_pred = (y_prob >= thr).astype(int)
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    return {
        "auc": float(auc),
        "pr_auc": float(pr_auc),
        "precision_at_thr": float(precision),
        "recall_at_thr": float(recall),
        "f1_at_thr": float(f1),
        "firing_threshold": float(thr)
    }


def evaluate_oos_walkforward_precomputed(precomputed_folds, model_type: str, params: dict):
    """Runs a walk-forward evaluation using precomputed/pre-scaled folds (extremely fast)."""
    oos_preds = []
    oos_targets = []
    fold_metrics = []
    
    for fold, (X_train_scaled, train_y, X_test_scaled, test_y, threshold) in enumerate(precomputed_folds):
        # Fit model
        model = build_model(model_type, params)
        model.fit(X_train_scaled, train_y)
        
        # Predict probability
        prob = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics for this fold
        metrics = compute_metrics(test_y, prob)
        metrics["fold"] = fold
        metrics["threshold_val"] = threshold
        metrics["base_rate"] = float(np.mean(test_y))
        fold_metrics.append(metrics)
        
        oos_preds.extend(prob)
        oos_targets.extend(test_y)
        
    oos_preds = np.array(oos_preds)
    oos_targets = np.array(oos_targets)
    
    overall = compute_metrics(oos_targets, oos_preds)
    overall["base_rate"] = float(np.mean(oos_targets))
    
    return overall, fold_metrics


def train_gating_model(etf: str, side: str, n_trials: int = 30, n_splits: int = DEFAULT_N_SPLITS, gap: int = DEFAULT_PURGE_GAP, quantile_k: float = DEFAULT_QUANTILE, min_ret: float = MIN_RETURN_THRESHOLD):
    """Trains and benchmarks gating models for one ETF and side."""
    print(f"\n==========================================")
    print(f"Training Gating Model for {etf} (side={side})")
    print(f"==========================================")
    
    feat_path = DATA_DIR / f"features_{etf}.parquet"
    if not feat_path.exists():
        print(f"[SKIP] Feature file {feat_path.name} not found.")
        return None
        
    feat = pd.read_parquet(feat_path).sort_index()
    feat = feat.dropna(subset=FEATURES + [TARGET]).copy()
    
    X = feat[FEATURES].values.astype(np.float32)
    y_raw = feat[TARGET].values.astype(np.float32)
    dates = feat.index
    
    # 1. Dev/Holdout Split (80% dev, 20% holdout)
    n = len(feat)
    dev_size = int(n * (1 - HOLDOUT_FRACTION))
    
    X_dev, y_dev_raw = X[:dev_size], y_raw[:dev_size]
    X_ho, y_ho_raw = X[dev_size:], y_raw[dev_size:]
    
    # Generate cross-validation splits on Dev set
    cv_splits = list(purged_tssplit(len(X_dev), n_splits, gap))
    
    # 2. Pre-process splits (scaling, labeling, quantiles) to completely eliminate overhead inside the Optuna loop
    precomputed_folds = []
    for train_idx, test_idx in cv_splits:
        train_y_raw = y_dev_raw[train_idx]
        test_y_raw = y_dev_raw[test_idx]
        
        if side == "long":
            pos_train = train_y_raw[train_y_raw > 0]
            q_val = np.quantile(pos_train, quantile_k) if len(pos_train) > 10 else np.quantile(train_y_raw, 0.70)
            threshold = max(min_ret, q_val)
            train_y = (train_y_raw >= threshold).astype(int)
            test_y = (test_y_raw >= threshold).astype(int)
        else:
            neg_train = np.abs(train_y_raw[train_y_raw < 0])
            q_val = np.quantile(neg_train, quantile_k) if len(neg_train) > 10 else np.quantile(np.abs(train_y_raw), 0.70)
            threshold = max(min_ret, q_val)
            train_y = (train_y_raw <= -threshold).astype(int)
            test_y = (test_y_raw <= -threshold).astype(int)
            
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_dev[train_idx])
        X_test_scaled = scaler.transform(X_dev[test_idx])
        
        precomputed_folds.append((X_train_scaled, train_y, X_test_scaled, test_y, float(threshold)))
        
    results = {}
    
    # Define labels on full dev set for holdout evaluation
    if side == "long":
        pos_dev = y_dev_raw[y_dev_raw > 0]
        dev_threshold = max(min_ret, np.quantile(pos_dev, quantile_k) if len(pos_dev) > 10 else np.quantile(y_dev_raw, 0.70))
        y_dev = (y_dev_raw >= dev_threshold).astype(int)
        y_ho = (y_ho_raw >= dev_threshold).astype(int)
    else:
        neg_dev = np.abs(y_dev_raw[y_dev_raw < 0])
        dev_threshold = max(min_ret, np.quantile(neg_dev, quantile_k) if len(neg_dev) > 10 else np.quantile(np.abs(y_dev_raw), 0.70))
        y_dev = (y_dev_raw <= -dev_threshold).astype(int)
        y_ho = (y_ho_raw <= -dev_threshold).astype(int)
        
    print(f"Dataset: {n} days (Dev: {len(X_dev)}, Holdout: {len(X_ho)})")
    print(f"Dev Label Threshold: {dev_threshold:.5f} (Tradable days: {np.sum(y_dev)} / {len(y_dev)} = {np.mean(y_dev):.2%})")
    
    # Benchmark each model type
    for model_type in MODEL_TYPES:
        t0 = time.time()
        print(f"Tuning {model_type}...", end="", flush=True)
        
        def objective(trial):
            params = get_optuna_params(trial, model_type)
            overall, _ = evaluate_oos_walkforward_precomputed(precomputed_folds, model_type, params)
            return overall["pr_auc"] + 0.5 * overall["auc"]
            
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, n_jobs=2)  # Parallelize trial search
        best_params = study.best_params
        
        # Evaluate best params on walk-forward CV
        overall_cv, fold_metrics = evaluate_oos_walkforward_precomputed(precomputed_folds, model_type, best_params)
        
        # Evaluate on Holdout set
        scaler = StandardScaler()
        X_dev_scaled = scaler.fit_transform(X_dev)
        X_ho_scaled = scaler.transform(X_ho)
        
        full_model = build_model(model_type, best_params)
        # Train full model with standard sklearn parallelization (if any) or keep fast
        full_model.fit(X_dev_scaled, y_dev)
        
        ho_prob = full_model.predict_proba(X_ho_scaled)[:, 1]
        ho_metrics = compute_metrics(y_ho, ho_prob)
        ho_metrics["base_rate"] = float(np.mean(y_ho))
        
        results[model_type] = {
            "best_params": best_params,
            "cv_metrics": overall_cv,
            "fold_metrics": fold_metrics,
            "holdout_metrics": ho_metrics
        }
        
        elapsed = time.time() - t0
        print(f" done in {elapsed:.1f}s")
        print(f"  CV PR-AUC: {overall_cv['pr_auc']:.4f} | CV AUC: {overall_cv['auc']:.4f} | CV Prec@70: {overall_cv['precision_at_thr']:.2%}")
        print(f"  HO PR-AUC: {ho_metrics['pr_auc']:.4f} | HO AUC: {ho_metrics['auc']:.4f} | HO Prec@70: {ho_metrics['precision_at_thr']:.2%}")

    # Determine best model based on CV PR-AUC
    best_model_type = max(results.keys(), key=lambda m: results[m]["cv_metrics"]["pr_auc"])
    best_params = results[best_model_type]["best_params"]
    
    print(f"\n>>> Best Model: {best_model_type} (CV PR-AUC: {results[best_model_type]['cv_metrics']['pr_auc']:.4f})")
    
    # Train winning model on ALL data (Dev + Holdout)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Re-calculate threshold on all data
    if side == "long":
        pos_all = y_raw[y_raw > 0]
        final_threshold = max(min_ret, np.quantile(pos_all, quantile_k) if len(pos_all) > 10 else np.quantile(y_raw, 0.70))
        y_all = (y_raw >= final_threshold).astype(int)
    else:
        neg_all = np.abs(y_raw[y_raw < 0])
        final_threshold = max(min_ret, np.quantile(neg_all, quantile_k) if len(neg_all) > 10 else np.quantile(np.abs(y_raw), 0.70))
        y_all = (y_raw <= -final_threshold).astype(int)
        
    final_model = build_model(best_model_type, best_params)
    final_model.fit(X_scaled, y_all)
    
    # Save best model + scaler
    model_name = f"gating_{etf}_{side}.joblib"
    scaler_name = f"gating_scaler_{etf}_{side}.joblib"
    joblib.dump(final_model, OUT_DIR / model_name)
    joblib.dump(scaler, OUT_DIR / scaler_name)
    
    # Save metadata
    meta = {
        "etf": etf,
        "side": side,
        "best_model_type": best_model_type,
        "best_params": best_params,
        "final_threshold": float(final_threshold),
        "results": results
    }
    
    with open(OUT_DIR / f"report_{etf}_{side}.json", "w") as f:
        json.dump(meta, f, indent=4)
        
    # Generate diagnostic plots
    plot_diagnostic_curves(etf, side, y_ho, ho_prob, best_model_type)
    
    return meta


def plot_diagnostic_curves(etf, side, y_true, y_prob, model_name):
    """Generates ROC and Precision-Recall plots for the Holdout set."""
    from sklearn.metrics import roc_curve, precision_recall_curve, auc
    
    plt.figure(figsize=(12, 5))
    
    # 1. ROC Curve
    plt.subplot(1, 2, 1)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.3f})")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve: {etf} {side} ({model_name})")
    plt.legend(loc="lower right")
    plt.grid(True)
    
    # 2. Precision-Recall Curve
    plt.subplot(1, 2, 2)
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    base_rate = np.mean(y_true)
    plt.plot(recall, precision, label=f"PR Curve (AUC = {pr_auc:.3f})")
    plt.axhline(y=base_rate, color="r", linestyle="--", label=f"Base Rate ({base_rate:.2%})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"PR Curve: {etf} {side} ({model_name})")
    plt.legend(loc="upper right")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"curves_{etf}_{side}.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all", help="ETF code or 'all'")
    parser.add_argument("-t", "--trials", type=int, default=30, help="Number of Optuna trials per model")
    parser.add_argument("-s", "--splits", type=int, default=DEFAULT_N_SPLITS, help="Number of CV splits")
    parser.add_argument("-g", "--gap", type=int, default=DEFAULT_PURGE_GAP, help="Purge gap size")
    parser.add_argument("-q", "--quantile", type=float, default=DEFAULT_QUANTILE, help="Percentile threshold for labeling")
    parser.add_argument("-m", "--min_ret", type=float, default=MIN_RETURN_THRESHOLD, help="Minimum absolute return for label")
    args = parser.parse_args()
    
    etfs = ETF_CLI_MAP.get(args.etf, [args.etf])
    if isinstance(etfs, str):
        etfs = [etfs]
        
    for etf in etfs:
        for side in ["long", "short"]:
            train_gating_model(etf, side, n_trials=args.trials, n_splits=args.splits, gap=args.gap, quantile_k=args.quantile, min_ret=args.min_ret)
