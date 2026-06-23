"""Frozen-linear score computation.

Loads trained coefficients from day-model and produces a per-day score
that is a direct port of the underlying LASSO/Huber/etc model.
Runtime = pure arithmetic, no ML fitting.

Dual-Model Architecture
-----------------------
Each ETF runs TWO independent models trained by ``day-model/train_model.py --side``:

  * ``side="long"``  -> target ``max(0, trade_return)``, files ``linear_{ETF}_long.joblib``
  * ``side="short"`` -> target ``max(0, -trade_return)``, files ``linear_{ETF}_short.joblib``

Both scores are **positive-oriented conviction** series.  The legacy
``side="single"`` path (symmetric target) is retained for backward compat
and IC diagnostics.
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

SIDES = ("single", "long", "short")


def _side_suffix(side: str) -> str:
    if side not in SIDES:
        raise ValueError(f"side must be one of {SIDES}, got {side!r}")
    return "" if side == "single" else f"_{side}"


def load_model(etf: str, side: str = "single") -> dict:
    """Load frozen model + scaler + selected features for an ETF side.

    The scaler_{ETF}{_side}.joblib file is a bundle dict containing:
      scaler (StandardScaler), features (full list), selected_features,
      stability_scores, best_params, best_model_type, holdout_ic,
      train_end_date, holdout_start_date, y_scale, side.

    Returns dict with: model, scaler, features, model_type, intercept, coef,
    y_scale, holdout_ic (reference from day-model training), side.
    """
    suffix = _side_suffix(side)
    model_path = MODEL_DIR / f"linear_{etf}{suffix}.joblib"
    bundle_path = MODEL_DIR / f"scaler_{etf}{suffix}.joblib"

    model = joblib.load(model_path)
    bundle = joblib.load(bundle_path)

    scaler = bundle["scaler"]
    features = list(bundle["selected_features"])
    y_scale = float(bundle.get("y_scale", 1.0))
    holdout_ic = float(bundle.get("holdout_ic", float("nan")))

    coef = getattr(model, "coef_", None)
    if coef is None:
        raise ValueError(f"{etf}({side}): model has no coef_")
    if len(features) != coef.shape[0]:
        raise ValueError(
            f"{etf}({side}): feature count mismatch ({len(features)} vs coef {coef.shape[0]})"
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
        "side": side,
    }


def load_features(etf: str) -> pd.DataFrame:
    """Load feature parquet (137 features + trade_return target, indexed by date).

    ``trade_return`` = log(close[EXIT_BAR] / open[decision_bar+1]) mirrors the
    actual daytrade P&L. ``pm_return`` retained for diagnostic IC checks vs the
    old baseline.
    """
    return pd.read_parquet(DATA_DIR / f"features_{etf}.parquet")


_SCORES_CACHE = {}


def compute_scores(etf: str, side: str = "single", dropna: bool = True) -> pd.Series:
    """Compute frozen-linear conviction score for every day.

    score_t = intercept + (scaler.transform(X_full)[:, sel_idx] @ coef)

    For ``side="long"`` / ``side="short"`` the score is positive-oriented
    (higher = stronger conviction for that side).  For ``side="single"``
    the score is signed (legacy behaviour).

    The scaler was fitted on all 127 features; we slice to selected afterwards.
    """
    key = (etf, side, dropna)
    if key in _SCORES_CACHE:
        return _SCORES_CACHE[key]

    info = load_model(etf, side=side)
    df = load_features(etf)

    # Reload bundle to get full feature list & selected indices
    suffix = _side_suffix(side)
    bundle = joblib.load(MODEL_DIR / f"scaler_{etf}{suffix}.joblib")
    full_features = list(bundle["features"])
    sel_features = list(bundle["selected_features"])
    sel_idx = [full_features.index(f) for f in sel_features]

    Xfull = df[full_features].values
    mask = ~np.isnan(Xfull).any(axis=1)
    Xc = Xfull[mask]

    Xs_all = info["scaler"].transform(Xc)
    Xs = Xs_all[:, sel_idx]
    scores = Xs @ info["coef"] + info["intercept"]

    # The short model is trained on raw pm_return; negate its output so the
    # score is positive-oriented (high = strong downside / short conviction).
    if side == "short":
        scores = -scores

    name = f"{etf}_score{suffix}"
    out = pd.Series(np.nan, index=df.index, name=name, dtype=float)
    out.iloc[mask] = scores

    if dropna:
        out = out.dropna()
    _SCORES_CACHE[key] = out
    return out


def verify_ic(etf: str, side: str = "single") -> dict:
    """Compute IC vs the appropriate target.

    For ``side="long"`` the target is ``max(0, trade_return)``; for
    ``side="short"`` it is ``max(0, -trade_return)``; for ``single`` it is
    the raw ``trade_return``.
    """
    s = compute_scores(etf, side=side, dropna=False)
    df = load_features(etf)
    pm = df["trade_return"]
    if side == "long":
        target = np.maximum(0.0, pm.values)
    elif side == "short":
        target = np.maximum(0.0, -pm.values)
    else:
        target = pm.values

    valid = ~(s.isna() | pm.isna())
    score = s[valid].values
    tgt = target[valid.values]

    ic, _ = spearmanr(score, tgt)
    return {
        "etf": etf,
        "side": side,
        "n": int(valid.sum()),
        "ic_full": float(ic) if not np.isnan(ic) else 0.0,
        "score_mean": float(np.mean(score)),
        "score_std": float(np.std(score)),
        "score_min": float(np.min(score)),
        "score_max": float(np.max(score)),
    }


def verify_all() -> pd.DataFrame:
    """Verify IC for every ETF on every side (single, long, short)."""
    rows = []
    for etf in ETFS:
        for side in ("long", "short"):
            rows.append(verify_ic(etf, side))
    return pd.DataFrame(rows).set_index(["etf", "side"])


if __name__ == "__main__":
    print("Verifying dual-model frozen scores (full history IC)...")
    df = verify_all()
    print(df.to_string())
