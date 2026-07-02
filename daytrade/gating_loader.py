"""Gating-model prediction loader for the daytrade pipeline.

Loads the canonical (per-ETF × side) gating model trained by
``day-model/gating_model.py`` and returns a causal boolean series indicating
whether the gating model "fires" (predicts a tradable big-move day) for each
historical date.

Contract
--------
``load_gating_mask(etf, side) -> pd.Series[date -> bool]``

The returned series is indexed by date (matching ``features_{ETF}.parquet``'s
DatetimeIndex, which is also the index used by ``rules.get_long_short_signals``).
A missing gating artifact returns ``None`` (caller treats as "no gate").
"""
from __future__ import annotations

from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd

from . import DATA_DIR

# Import custom penalties for skglm model deserialization
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from penalties import MCP_plus_L2
except ImportError:
    pass

# day-model/gating_model/ holds the canonical promoted artifacts.
GATING_DIR = (DATA_DIR.parent / "gating_model").resolve()


def _load_canonical_report(etf: str, side: str) -> dict | None:
    p = GATING_DIR / f"report_{etf}_{side}.json"
    if not p.exists():
        return None
    import json
    with open(p) as f:
        return json.load(f)


def load_gating_mask(etf: str, side: str, quantile: float = 70.0) -> pd.Series | None:
    """Return a boolean Series (date → fire?) for the chosen gating model.

    Parameters
    ----------
    etf, side : str
        e.g. ("300ETF", "long").
    quantile : float
        If the canonical report has no persisted ``firing_threshold``, fall back
        to using this percentile of in-sample predicted probabilities.

    Returns
    -------
    pd.Series of bool indexed by date, or ``None`` if no model is available.
    """
    report = _load_canonical_report(etf, side)
    if report is None:
        return None

    model_path = GATING_DIR / f"gating_{etf}_{side}.joblib"
    scaler_path = GATING_DIR / f"gating_scaler_{etf}_{side}.joblib"
    if not (model_path.exists() and scaler_path.exists()):
        return None

    feat_path = DATA_DIR / f"features_{etf}.parquet"
    if not feat_path.exists():
        return None

    feat = pd.read_parquet(feat_path).sort_index()
    features_used = report.get("features_used")
    if not features_used:
        # Fall back to the full 130-feature list if metadata is missing
        import sys
        sys.path.append(str(DATA_DIR.parent))
        from build_features import FEATURES
        features_used = FEATURES

    missing = [c for c in features_used if c not in feat.columns]
    if missing:
        # Selector kept a feature no longer present in the parquet — abort gate
        return None

    X = feat[features_used].values.astype(np.float32)
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    Xs = scaler.transform(X)

    # Determine the firing threshold
    fire_thr = report.get("firing_threshold")
    variant = report.get("chosen_variant") or report.get("variant")
    joint3_class = report.get("joint3_class") or side

    proba = model.predict_proba(Xs)
    classes = list(model.classes_)

    if variant == "joint3":
        # 3-class softmax: 0=neutral, 1=big_up, 2=big_down
        target_class = 1 if joint3_class == "long" else 2
        if target_class not in classes:
            return None
        score = proba[:, classes.index(target_class)]
    else:
        # Binary classifier: probability of the positive (big-move) class
        if len(classes) == 2:
            score = proba[:, classes.index(1)] if 1 in classes else proba[:, 1]
        else:
            score = proba[:, -1]

    if fire_thr is None:
        fire_thr = float(np.percentile(score, quantile))
    else:
        fire_thr = float(fire_thr)

    mask = pd.Series(score >= fire_thr, index=feat.index)
    return mask


def load_gating_masks(etf: str) -> dict[str, pd.Series | None]:
    """Convenience: return {"long": mask_or_None, "short": mask_or_None}."""
    return {"long": load_gating_mask(etf, "long"),
            "short": load_gating_mask(etf, "short")}


__all__ = ["load_gating_mask", "load_gating_masks", "GATING_DIR"]
