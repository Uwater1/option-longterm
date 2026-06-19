"""Frozen-linear score computation.

Loads trained coefficients from day-model and produces a per-day score
that is a direct port of the underlying LASSO/Huber/etc model.
Runtime = pure arithmetic, no ML fitting.
"""
from __future__ import annotations

import warnings
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Suppress sklearn version-mismatch warnings when loading pickled models.
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*InconsistentVersion.*")

from . import MODEL_DIR, DATA_DIR, ETFS


def load_model(etf: str) -> dict:
    """Load frozen model + scaler + selected features for an ETF.

    The scaler_{ETF}.joblib file is a bundle dict containing:
      scaler (StandardScaler), features (full list), selected_features,
      stability_scores, best_params, best_model_type, holdout_ic,
      train_end_date, holdout_start_date, y_scale.

    Returns dict with: model, scaler, features, model_type, intercept, coef,
    y_scale, holdout_ic (reference from day-model training).
    """
    model_path = MODEL_DIR / f"linear_{etf}.joblib"
    bundle_path = MODEL_DIR / f"scaler_{etf}.joblib"

    model = joblib.load(model_path)
    bundle = joblib.load(bundle_path)

    scaler = bundle["scaler"]
    features = list(bundle["selected_features"])
    y_scale = float(bundle.get("y_scale", 1.0))
    holdout_ic = float(bundle.get("holdout_ic", float("nan")))

    coef = getattr(model, "coef_", None)
    if coef is None:
        raise ValueError(f"{etf}: model has no coef_")
    if len(features) != coef.shape[0]:
        raise ValueError(
            f"{etf}: feature count mismatch ({len(features)} vs coef {coef.shape[0]})"
        )

    return {
        "model": model,
        "scaler": scaler,
        "features": features,
        "model_type": type(model).__name__,
        "intercept": float(model.intercept_),
        "coef": coef,
        "y_scale": y_scale,
        "holdout_ic_ref": holdout_ic,
        "holdout_start": bundle.get("holdout_start_date"),
        "train_end": bundle.get("train_end_date"),
    }


def load_features(etf: str) -> pd.DataFrame:
    """Load feature parquet (137 features + pm_return target, indexed by date)."""
    return pd.read_parquet(DATA_DIR / f"features_{etf}.parquet")


def compute_scores(etf: str, dropna: bool = True) -> pd.Series:
    """Compute frozen-linear score for every day in the feature parquet.

    score_t = intercept + (scaler.transform(X_full)[:, sel_idx] @ coef)

    The scaler was fitted on all 127 features; we slice to selected afterwards.
    """
    info = load_model(etf)
    df = load_features(etf)

    # Reload bundle to get full feature list & selected indices
    bundle = joblib.load(MODEL_DIR / f"scaler_{etf}.joblib")
    full_features = list(bundle["features"])
    sel_features = list(bundle["selected_features"])
    sel_idx = [full_features.index(f) for f in sel_features]

    Xfull = df[full_features].values
    mask = ~np.isnan(Xfull).any(axis=1)
    Xc = Xfull[mask]

    Xs_all = info["scaler"].transform(Xc)
    Xs = Xs_all[:, sel_idx]
    scores = Xs @ info["coef"] + info["intercept"]

    out = pd.Series(np.nan, index=df.index, name=f"{etf}_score", dtype=float)
    out.iloc[mask] = scores

    if dropna:
        out = out.dropna()
    return out


def verify_ic(etf: str) -> dict:
    """Compute IC vs pm_return on full history; should match day-model report."""
    s = compute_scores(etf, dropna=False)
    df = load_features(etf)
    valid = ~(s.isna() | df["pm_return"].isna())
    score = s[valid].values
    target = df.loc[valid, "pm_return"].values

    ic, _ = spearmanr(score, target)
    dir_acc = float(((np.sign(score) == np.sign(target)) |
                     (score == 0)).mean()) if len(score) else float("nan")
    return {
        "etf": etf,
        "n": int(valid.sum()),
        "ic_full": float(ic),
        "dir_acc_full": dir_acc,
        "score_mean": float(np.mean(score)),
        "score_std": float(np.std(score)),
    }


def verify_all() -> pd.DataFrame:
    """Verify all ETFs against report. Day-model holdout IC reference:
      300: +0.0580, 50: +0.0157, 500: +0.0780, 588000: -0.0139, 159915: +0.1999
    Note: report IC was on 20% holdout (2024-03-19+) only. Here we compute on full history.
    """
    rows = [verify_ic(etf) for etf in ETFS]
    return pd.DataFrame(rows).set_index("etf")


if __name__ == "__main__":
    print("Verifying frozen scores match day-model report IC (full history)...")
    df = verify_all()
    print(df.to_string())
    print("\nReference holdout IC (day-model REPORT):")
    print("  300: +0.0580, 50: +0.0157, 500: +0.0780, 588000: -0.0139, 159915: +0.1999")
