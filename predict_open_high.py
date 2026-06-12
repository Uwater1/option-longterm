"""
predict_open_high.py - Production Open-to-High Limit Order Prediction System
============================================================================
Predicts the 10th percentile of (High - Open) / Open using quantile regression
and LightGBM, enabling 90% fill-rate limit sell orders for covered call entry.

When used with --model-offset in backtest_covered_call.py, sell legs execute at
mid price (no bid-ask spread slippage). The model only predicts whether the
limit order will fill, not a price discount. Only commission applies as cost.

Usage:
    python predict_open_high.py -e 300        # Train & validate for 300ETF
    python predict_open_high.py -e 50         # Train & validate for 50ETF
    python predict_open_high.py -e 500        # Train & validate for 500ETF
    python predict_open_high.py -e 300 --predict  # Predict today's offset only
"""

import os
import sys
import json
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas_ta as ta
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_pinball_loss
from statsmodels.regression.quantile_regression import QuantReg
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")

# ── ETF configurations ────────────────────────────────────────────────────────
ETF_CONFIG = {
    "50":  {"path": "./data/50ETF_1d.parquet",  "name": "50ETF (510050)"},
    "300": {"path": "./data/510300_1d.parquet",  "name": "300ETF (510300)"},
    "500": {"path": "./data/500ETF_1d.parquet",  "name": "500ETF (510500)"},
}

# ── Candidate feature list ────────────────────────────────────────────────────
# (feature_name, description)
CANDIDATE_FEATURES = [
    # ── Original features ──
    "gap_pct",           # Overnight gap (open - prev_close) / prev_close
    "rsi14",             # RSI(14) — momentum/overbought
    "vol20",             # 20d realized vol
    "atr14_norm",        # ATR(14) / close — normalized intraday range
    "close_sma50_ratio", # Close / SMA50 — trend context
    "macd_hist",         # MACD histogram — short-term momentum
    "roc5",              # Rate of change 5d
    "roc10",             # Rate of change 10d
    "roc20",             # Rate of change 20d
    "bb_width",          # Bollinger band width (vol compression)
    "volume_ratio",      # Volume / SMA(volume, 20) — unusual volume
    "dow",               # Day of week (categorical, encoded as 0-4)
    "open_ema5_div",     # (open - EMA5) / EMA5 — divergence from short MA
    "open_ema20_div",    # (open - EMA20) / EMA20 — divergence from medium MA
    # ── Expanded features (v2) ──
    "prev_day_range",        # Yesterday's (high - low) / prev_close — prior day volatility
    "prev_open_to_high",     # Yesterday's (high - open) / open — prior day open-to-high (autocorr with target)
    "overnight_gap_from_high",  # (open - prev_high) / prev_high — gap from yesterday's high
    "upper_shadow",          # Yesterday's upper candle shadow — selling pressure
    "lower_shadow",          # Yesterday's lower candle shadow — buying support
    "stoch_k14",             # Stochastic %K(14) — momentum oscillator
    "williams_r14",          # Williams %R(14) — overbought/oversold
    "adx14",                 # ADX(14) — trend strength
    "mfi14",                 # Money Flow Index(14) — volume-weighted momentum
    "cci20",                 # CCI(20) — deviation from statistical mean
    "vol_skew20",            # Rolling skewness of 20d returns — tail risk
]

QUANTILE = 0.10          # Predict 10th percentile → 90% fill rate
TARGET_COVERAGE = 0.90   # Target empirical coverage rate
RETRAIN_EVERY = 60       # Retrain rolling model every N trading days
BLOCK_SIZE = 20          # Block size for block-bootstrap augmentation
AUGMENT_RATIO = 1.0      # Ratio of synthetic to real data (1.0 = double the data)
N_BAGGING_MODELS = 5     # Number of bootstrap-bagged LightGBM models
VOL_REGIME_THRESHOLD = None  # Auto-computed: median vol20 splits low/high vol
OUT_DIR = "./backtest"


# ─────────────────────────────────────────────────────────────────────────────
# Data Loading & Feature Engineering
# ─────────────────────────────────────────────────────────────────────────────
def load_and_engineer(etf_key: str) -> pd.DataFrame:
    """Load ETF daily data and compute all candidate features + target."""
    cfg = ETF_CONFIG[etf_key]
    df = pd.read_parquet(cfg["path"]).sort_values("date").copy()
    df = df.reset_index(drop=True)

    # ── Target: (high - open) / open * 100 (percent) ──
    df["y"] = (df["high"] - df["open"]) / df["open"] * 100.0

    # ── Features ──
    # 1. Overnight gap
    df["gap_pct"] = (df["open"] - df["prev_close"]) / df["prev_close"] * 100.0

    # 2. RSI(14)
    df["rsi14"] = ta.rsi(df["close"], length=14)

    # 3. Realized volatility (20d annualized)
    df["vol20"] = df["close"].pct_change().rolling(20).std() * np.sqrt(252)

    # 4. ATR(14) normalized
    df["atr14"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["atr14_norm"] = df["atr14"] / df["close"] * 100.0  # as %

    # 5. Close / SMA50 ratio
    df["sma50"] = ta.sma(df["close"], length=50)
    df["close_sma50_ratio"] = df["close"] / df["sma50"]

    # 6. MACD histogram
    macd = ta.macd(df["close"])
    df["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan

    # 7-9. Rate of change at multiple horizons
    df["roc5"]  = ta.roc(df["close"], length=5)
    df["roc10"] = ta.roc(df["close"], length=10)
    df["roc20"] = ta.roc(df["close"], length=20)

    # 10. Bollinger band width
    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None:
        bbu = bb["BBU_20_2.0_2.0"]
        bbl = bb["BBL_20_2.0_2.0"]
        sma20 = bb["BBM_20_2.0_2.0"]
        df["bb_width"] = (bbu - bbl) / sma20
    else:
        df["bb_width"] = np.nan

    # 11. Volume ratio
    df["vol_sma20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["vol_sma20"]

    # 12. Day of week
    df["dow"] = pd.to_datetime(df["date"]).dt.dayofweek.astype(float)

    # 13-14. Divergence between MA/EMA and open price
    df["ema5"]  = ta.ema(df["close"], length=5)
    df["ema20"] = ta.ema(df["close"], length=20)
    df["open_ema5_div"]  = (df["open"] - df["ema5"])  / df["ema5"]  * 100.0
    df["open_ema20_div"] = (df["open"] - df["ema20"]) / df["ema20"] * 100.0

    # ── Expanded features (v2) ──
    # Shifted OHLC for previous-day references
    prev_high  = df["high"].shift(1)
    prev_low   = df["low"].shift(1)
    prev_open  = df["open"].shift(1)
    prev_close_s = df["close"].shift(1)  # alias to avoid collision with column "prev_close"

    # 15. Previous day range (high-low) as % of prev_close
    df["prev_day_range"] = (prev_high - prev_low) / prev_close_s * 100.0

    # 16. Previous day open-to-high (autocorrelation signal with target)
    df["prev_open_to_high"] = (prev_high - prev_open) / prev_open * 100.0

    # 17. Overnight gap from yesterday's high (distinct from gap_pct which uses prev_close)
    df["overnight_gap_from_high"] = (df["open"] - prev_high) / prev_high * 100.0

    # 18-19. Candlestick shadow features (selling pressure / buying support)
    df["upper_shadow"] = (prev_high - pd.concat([prev_open, prev_close_s], axis=1).max(axis=1)) / prev_close_s * 100.0
    df["lower_shadow"] = (pd.concat([prev_open, prev_close_s], axis=1).min(axis=1) - prev_low) / prev_close_s * 100.0

    # 20. Stochastic %K(14)
    stoch = ta.stoch(df["high"], df["low"], df["close"], length=14)
    df["stoch_k14"] = stoch["STOCHk_14_3_3"] if stoch is not None else np.nan

    # 21. Williams %R(14)
    df["williams_r14"] = ta.willr(df["high"], df["low"], df["close"], length=14)

    # 22. ADX(14) — trend strength
    adx = ta.adx(df["high"], df["low"], df["close"], length=14)
    df["adx14"] = adx["ADX_14"] if adx is not None else np.nan

    # 23. Money Flow Index(14) — volume-weighted momentum
    df["mfi14"] = ta.mfi(df["high"], df["low"], df["close"], df["volume"], length=14)

    # 24. CCI(20) — deviation from statistical mean
    df["cci20"] = ta.cci(df["high"], df["low"], df["close"], length=20)

    # 25. Rolling skewness of 20d returns — tail risk signal
    df["vol_skew20"] = ta.skew(df["close"].pct_change(), length=20)

    # Drop warmup rows
    df = df.dropna(subset=["y"] + list(CANDIDATE_FEATURES)).reset_index(drop=True)

    # Keep date for reference
    if "date" not in df.columns:
        df["date"] = pd.to_datetime(df.index)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Pinball Loss (Quantile Loss) Helper
# ─────────────────────────────────────────────────────────────────────────────
def pinball_loss(y_true, y_pred, q=QUANTILE):
    """Compute mean pinball loss for quantile q."""
    diff = y_true - y_pred
    return np.mean(np.maximum(q * diff, (q - 1) * diff))


# ─────────────────────────────────────────────────────────────────────────────
# Feature Selection: Forward Selection via CV Pinball Loss
# ─────────────────────────────────────────────────────────────────────────────
def forward_feature_selection(X: pd.DataFrame, y: pd.Series,
                               max_features: int = 4,
                               n_splits: int = 5) -> dict:
    """
    Greedy forward selection: for each feature set size (1..max_features),
    add the feature that reduces CV pinball loss the most.

    Uses LightGBM quantile as the scoring model for speed.

    Returns dict with:
      - 'best_sets': {2: [f1,f2], 3: [f1,f2,f3], 4: [f1,f2,f3,f4]}
      - 'best_set_size': int (size with best CV score)
      - 'cv_scores': {size: score}
      - 'selection_order': [(feature, score), ...]
    """
    feature_names = list(X.columns)
    tscv = TimeSeriesSplit(n_splits=n_splits)
    selected = []
    remaining = set(feature_names)
    best_sets = {}
    cv_scores = {}
    selection_order = []

    for step in range(max_features):
        best_feat = None
        best_score = np.inf

        candidates = list(remaining)
        for feat in candidates:
            trial_set = selected + [feat]
            X_trial = X[trial_set].values

            scores = []
            for train_idx, val_idx in tscv.split(X_trial):
                X_tr, X_val = X_trial[train_idx], X_trial[val_idx]
                y_tr, y_val = y.iloc[train_idx].values, y.iloc[val_idx].values

                model = lgb.LGBMRegressor(
                    objective="quantile", alpha=QUANTILE,
                    num_leaves=31, max_depth=5, n_estimators=150,
                    learning_rate=0.05, min_child_samples=max(20, len(X_tr) // 30),
                    verbose=-1, random_state=42
                )
                model.fit(X_tr, y_tr)
                pred = model.predict(X_val)
                scores.append(pinball_loss(y_val, pred))

            avg_score = np.mean(scores)
            if avg_score < best_score:
                best_score = avg_score
                best_feat = feat

        selected.append(best_feat)
        remaining.discard(best_feat)
        selection_order.append((best_feat, best_score))
        set_size = len(selected)
        best_sets[set_size] = list(selected)
        cv_scores[set_size] = best_score

        print(f"  Step {set_size}: Added '{best_feat}' → CV pinball loss = {best_score:.6f}")

    # Find best set size
    best_set_size = min(cv_scores, key=cv_scores.get)

    return {
        "best_sets": best_sets,
        "best_set_size": best_set_size,
        "cv_scores": cv_scores,
        "selection_order": selection_order,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Cross-ETF Pooled Data Loading
# ─────────────────────────────────────────────────────────────────────────────
def load_and_engineer_all(etf_keys=None) -> pd.DataFrame:
    """Load and engineer features for multiple ETFs, pooling into one DataFrame.
    Adds an 'etf_vol' feature (each ETF's vol20) as a cross-ETF differentiator."""
    if etf_keys is None:
        etf_keys = list(ETF_CONFIG.keys())
    frames = []
    for key in etf_keys:
        df = load_and_engineer(key)
        df["etf_vol"] = df["vol20"].median()  # ETF-level vol fingerprint
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    return combined


# ─────────────────────────────────────────────────────────────────────────────
# Block-Bootstrap Synthetic Data Augmentation
# ─────────────────────────────────────────────────────────────────────────────
def block_bootstrap_augment(X: pd.DataFrame, y: pd.Series,
                            block_size: int = BLOCK_SIZE,
                            augment_ratio: float = AUGMENT_RATIO,
                            random_state: int = 42) -> tuple:
    """
    Augment training data via circular block bootstrap.
    Preserves temporal dependence within blocks of `block_size` consecutive days.

    Returns (X_aug, y_aug) with real + synthetic data concatenated.
    """
    rng = np.random.RandomState(random_state)
    n = len(X)
    n_synth = int(n * augment_ratio)
    n_blocks = int(np.ceil(n_synth / block_size))

    # Circular block bootstrap: sample starting indices with replacement
    start_indices = rng.randint(0, n, size=n_blocks)
    synth_indices = []
    for start in start_indices:
        block = [(start + j) % n for j in range(block_size)]
        synth_indices.extend(block)
    synth_indices = synth_indices[:n_synth]

    X_synth = X.iloc[synth_indices].reset_index(drop=True)
    y_synth = y.iloc[synth_indices].reset_index(drop=True)

    # Add small noise to features to avoid exact duplicates (regularization)
    noise_scale = 0.02  # 2% of feature std
    for col in X_synth.columns:
        col_std = X_synth[col].std()
        if col_std > 0:
            X_synth[col] += rng.normal(0, noise_scale * col_std, size=len(X_synth))

    # Concatenate real + synthetic
    X_aug = pd.concat([X, X_synth], ignore_index=True)
    y_aug = pd.concat([y, y_synth], ignore_index=True)

    return X_aug, y_aug


# ─────────────────────────────────────────────────────────────────────────────
# Coverage Calibration
# ─────────────────────────────────────────────────────────────────────────────
def compute_calibration_offset(predictions: np.ndarray, actuals: np.ndarray,
                                target_coverage: float = TARGET_COVERAGE) -> float:
    """
    Compute a constant offset that, when added to predictions, achieves target coverage.
    We want: P(actual >= pred + offset) = target_coverage
    Therefore: offset = P_{1-target}(actual - pred)
    E.g. for 90% coverage: offset = P10(actual - pred)
    A negative offset means predictions are too optimistic (need to shift down).
    """
    mask = ~np.isnan(predictions) & ~np.isnan(actuals)
    diff = actuals[mask] - predictions[mask]
    # offset = percentile of (actual - pred) at (1-target)*100
    offset = np.percentile(diff, (1 - target_coverage) * 100)
    return float(offset)


def compute_vol_regime_calibration(predictions: np.ndarray, actuals: np.ndarray,
                                    vol20: np.ndarray,
                                    target_coverage: float = TARGET_COVERAGE) -> dict:
    """
    Compute separate calibration offsets for low-vol and high-vol regimes.
    Splits by median vol20. Returns dict with 'low_vol_offset', 'high_vol_offset',
    'vol_threshold', and combined 'coverage' after regime calibration.
    """
    mask = ~np.isnan(predictions) & ~np.isnan(actuals) & ~np.isnan(vol20)
    preds = predictions[mask]
    acts = actuals[mask]
    vols = vol20[mask]

    vol_thresh = float(np.median(vols))
    low_mask = vols <= vol_thresh
    high_mask = vols > vol_thresh

    low_offset = compute_calibration_offset(preds[low_mask], acts[low_mask], target_coverage) if low_mask.sum() > 20 else 0.0
    high_offset = compute_calibration_offset(preds[high_mask], acts[high_mask], target_coverage) if high_mask.sum() > 20 else 0.0

    # Compute combined coverage after regime-conditional calibration
    cal_preds = np.where(vols <= vol_thresh, preds + low_offset, preds + high_offset)
    coverage = np.mean(acts >= cal_preds) * 100

    return {
        "low_vol_offset": float(low_offset),
        "high_vol_offset": float(high_offset),
        "vol_threshold": vol_thresh,
        "coverage": float(coverage),
    }


def adaptive_quantile_search(X: pd.DataFrame, y: pd.Series, features: list,
                              model_type: str, target_coverage: float = TARGET_COVERAGE,
                              n_splits: int = 5, tol: float = 0.01,
                              max_iter: int = 8) -> dict:
    """
    Binary search for the quantile q' that achieves target_coverage after calibration.
    Returns dict with 'quantile', 'coverage', 'calibration_offset'.
    """
    lo, hi = 0.02, 0.15  # Search range for quantile
    best_result = None

    for iteration in range(max_iter):
        mid_q = (lo + hi) / 2.0
        # Train at mid_q and validate
        tscv = TimeSeriesSplit(n_splits=n_splits)
        all_preds = []
        all_actuals = []
        for train_idx, val_idx in tscv.split(X):
            X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
            try:
                model = lgb.LGBMRegressor(
                    objective="quantile", alpha=mid_q,
                    num_leaves=31, max_depth=5, n_estimators=200,
                    learning_rate=0.05,
                    min_child_samples=max(20, len(X_tr) // 30),
                    verbose=-1, random_state=42
                )
                model.fit(X_tr[features].values, y_tr.values)
                pred = model.predict(X_val[features].values)
                all_preds.extend(pred)
                all_actuals.extend(y_val.values)
            except Exception:
                continue

        preds_arr = np.array(all_preds)
        actuals_arr = np.array(all_actuals)
        coverage = np.mean(actuals_arr >= preds_arr) * 100
        cal_offset = compute_calibration_offset(preds_arr, actuals_arr, target_coverage)

        print(f"    q={mid_q:.4f}  coverage={coverage:.1f}%  cal_offset={cal_offset:+.4f}%")

        best_result = {"quantile": mid_q, "coverage": coverage, "calibration_offset": cal_offset}

        if coverage > (target_coverage * 100 + tol * 100):
            lo = mid_q  # Coverage too high → increase q (predict higher → fewer fills)
        elif coverage < (target_coverage * 100 - tol * 100):
            hi = mid_q  # Coverage too low → decrease q (predict lower → more fills)
        else:
            break  # Within tolerance

    return best_result


# ─────────────────────────────────────────────────────────────────────────────
# Model Training: Statsmodels Quantile Regression
# ─────────────────────────────────────────────────────────────────────────────
def train_statsmodels_qr(X: pd.DataFrame, y: pd.Series, features: list, quantile: float = QUANTILE):
    """Train Statsmodels Quantile Regression at q=0.10. Returns fitted model."""
    df_model = X[features].copy()
    df_model["y"] = y.values
    # Build formula: y ~ f1 + f2 + ...
    formula = "y ~ " + " + ".join(features)
    model = smf.quantreg(formula, data=df_model)
    result = model.fit(q=quantile, max_iter=500)
    return result


def predict_statsmodels_qr(result, X_new: pd.DataFrame, features: list) -> np.ndarray:
    """Predict using fitted Statsmodels QR model."""
    df_pred = X_new[features].copy()
    df_pred["y"] = 0  # dummy
    return result.predict(df_pred).values


# ─────────────────────────────────────────────────────────────────────────────
# Model Training: LightGBM Quantile
# ─────────────────────────────────────────────────────────────────────────────
def train_lightgbm_qr(X: pd.DataFrame, y: pd.Series, features: list, quantile: float = QUANTILE):
    """Train LightGBM Quantile model at given q. Returns fitted model."""
    X_arr = X[features].values
    y_arr = y.values

    model = lgb.LGBMRegressor(
        objective="quantile", alpha=quantile,
        num_leaves=31, max_depth=5, n_estimators=200,
        learning_rate=0.05, min_child_samples=max(20, len(X_arr) // 30),
        verbose=-1, random_state=42
    )
    model.fit(X_arr, y_arr)
    return model


def train_lightgbm_bagged(X: pd.DataFrame, y: pd.Series, features: list,
                           quantile: float = QUANTILE,
                           n_models: int = N_BAGGING_MODELS) -> list:
    """Train N LightGBM Quantile models on different bootstrap resamples.
    Returns list of fitted models for ensemble averaging."""
    rng = np.random.RandomState(42)
    n = len(X)
    models = []
    for i in range(n_models):
        # Bootstrap sample (with replacement)
        idx = rng.choice(n, size=n, replace=True)
        X_boot = X.iloc[idx]
        y_boot = y.iloc[idx]
        model = lgb.LGBMRegressor(
            objective="quantile", alpha=quantile,
            num_leaves=31, max_depth=5, n_estimators=200,
            learning_rate=0.05, min_child_samples=max(20, n // 30),
            verbose=-1, random_state=42 + i
        )
        model.fit(X_boot[features].values, y_boot.values)
        models.append(model)
    return models


def predict_lightgbm_bagged(models: list, X_new: pd.DataFrame, features: list) -> np.ndarray:
    """Average predictions from multiple bagged LightGBM models."""
    preds = np.stack([m.predict(X_new[features].values) for m in models])
    return np.mean(preds, axis=0)


def predict_lightgbm_qr(model, X_new: pd.DataFrame, features: list) -> np.ndarray:
    """Predict using fitted LightGBM Quantile model."""
    return model.predict(X_new[features].values)


# ─────────────────────────────────────────────────────────────────────────────
# Model Comparison via CV
# ─────────────────────────────────────────────────────────────────────────────
def compare_models_cv(X: pd.DataFrame, y: pd.Series, features: list,
                       n_splits: int = 5) -> dict:
    """Compare Statsmodels QR vs LightGBM via time-series CV pinball loss."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    sm_scores, lgb_scores = [], []

    for train_idx, val_idx in tscv.split(X):
        X_tr = X.iloc[train_idx]
        X_val = X.iloc[val_idx]
        y_tr = y.iloc[train_idx]
        y_val = y.iloc[val_idx]

        # Statsmodels QR
        try:
            sm_result = train_statsmodels_qr(X_tr, y_tr, features)
            sm_pred = predict_statsmodels_qr(sm_result, X_val, features)
            sm_scores.append(pinball_loss(y_val.values, sm_pred))
        except Exception as e:
            sm_scores.append(np.inf)

        # LightGBM
        lgb_model = train_lightgbm_qr(X_tr, y_tr, features)
        lgb_pred = predict_lightgbm_qr(lgb_model, X_val, features)
        lgb_scores.append(pinball_loss(y_val.values, lgb_pred))

    sm_avg = np.mean(sm_scores)
    lgb_avg = np.mean(lgb_scores)

    # Determine winner
    if abs(sm_avg - lgb_avg) / max(sm_avg, lgb_avg, 1e-10) < 0.05:
        winner = "ensemble"
    elif sm_avg < lgb_avg:
        winner = "statsmodels"
    else:
        winner = "lightgbm"

    return {
        "statsmodels_cv_loss": sm_avg,
        "lightgbm_cv_loss": lgb_avg,
        "winner": winner,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Rolling Validation (expanding window, retrain every N days)
# ─────────────────────────────────────────────────────────────────────────────
def rolling_validation(X: pd.DataFrame, y: pd.Series, features: list,
                        model_type: str, retrain_every: int = RETRAIN_EVERY,
                        min_train: int = 200, use_bagging: bool = True) -> dict:
    """
    Expanding-window rolling validation.
    Retrain model every `retrain_every` days on all prior data.
    Uses bagged LightGBM (N_BAGGING_MODELS) when use_bagging=True.
    Returns predictions and metrics.
    """
    n = len(X)
    predictions = np.full(n, np.nan)
    actuals = np.full(n, np.nan)
    retrain_indices = list(range(min_train, n, retrain_every))
    # Ensure we cover the tail
    if retrain_indices[-1] + retrain_every < n:
        retrain_indices.append(n - retrain_every)

    for i, start_idx in enumerate(retrain_indices):
        end_idx = min(start_idx + retrain_every, n)
        train_X = X.iloc[:start_idx]
        train_y = y.iloc[:start_idx]
        test_X  = X.iloc[start_idx:end_idx]
        test_y  = y.iloc[start_idx:end_idx]

        # Retrain with bagging for LightGBM
        if model_type in ("lightgbm", "ensemble") and use_bagging:
            bagged_models = train_lightgbm_bagged(train_X, train_y, features)
            preds_lgb = predict_lightgbm_bagged(bagged_models, test_X, features)
        elif model_type in ("lightgbm", "ensemble"):
            trained_lgb = train_lightgbm_qr(train_X, train_y, features)
            preds_lgb = predict_lightgbm_qr(trained_lgb, test_X, features)
        else:
            preds_lgb = None

        preds_sm = None
        if model_type in ("statsmodels", "ensemble"):
            try:
                trained_sm_result = train_statsmodels_qr(train_X, train_y, features)
                preds_sm = predict_statsmodels_qr(trained_sm_result, test_X, features)
            except Exception:
                preds_sm = None

        if model_type == "ensemble" and preds_lgb is not None and preds_sm is not None:
            preds = (preds_lgb + preds_sm) / 2.0
        elif preds_lgb is not None:
            preds = preds_lgb
        elif preds_sm is not None:
            preds = preds_sm
        else:
            continue

        predictions[start_idx:end_idx] = preds
        actuals[start_idx:end_idx] = test_y.values

    # Compute metrics on valid predictions
    mask = ~np.isnan(predictions)
    pred_valid = predictions[mask]
    actual_valid = actuals[mask]

    coverage = np.mean(actual_valid >= pred_valid) * 100
    mean_pred_offset = np.mean(pred_valid)
    mean_actual = np.mean(actual_valid)
    pl = pinball_loss(actual_valid, pred_valid)

    return {
        "predictions": predictions,
        "actuals": actuals,
        "coverage": coverage,
        "mean_pred_offset": mean_pred_offset,
        "mean_actual": mean_actual,
        "pinball_loss": pl,
        "n_predictions": int(np.sum(mask)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Static Baseline (per gap-regime 10th percentile)
# ─────────────────────────────────────────────────────────────────────────────
def compute_static_baseline(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    """Compute static per-gap-regime 10th percentile baseline."""
    gap = X["gap_pct"].values
    p10 = np.full(len(y), np.nan)

    regimes = [
        (gap < -0.5,                         "sig_down"),
        ((gap >= -0.5) & (gap < -0.05),      "mod_down"),
        ((gap >= -0.05) & (gap <= 0.05),     "neutral"),
        ((gap > 0.05) & (gap <= 0.5),        "mod_up"),
        (gap > 0.5,                           "sig_up"),
    ]

    for mask, name in regimes:
        if mask.sum() > 5:
            p10[mask] = y.values[mask].quantile(QUANTILE) if hasattr(y.values[mask], 'quantile') else np.percentile(y.values[mask], QUANTILE * 100)
    return p10


# ─────────────────────────────────────────────────────────────────────────────
# Visualization
# ─────────────────────────────────────────────────────────────────────────────
def plot_results(df: pd.DataFrame, features: list, selection_result: dict,
                  cv_comparison: dict, rolling_result: dict,
                  etf_name: str, etf_key: str, static_baseline: np.ndarray):
    """Generate comprehensive visualization."""
    fig = plt.figure(figsize=(18, 14))
    gs = gridspec.GridSpec(3, 2, hspace=0.35, wspace=0.25)

    mask = ~np.isnan(rolling_result["predictions"])
    pred = rolling_result["predictions"][mask]
    actual = rolling_result["actuals"][mask]
    dates = pd.to_datetime(df["date"].values[mask])

    # 1. Scatter: predicted p10 vs actual
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.scatter(dates, actual, s=8, alpha=0.4, color="#1976D2", label="Actual (H-O)/O %")
    ax1.scatter(dates, pred, s=8, alpha=0.8, color="#E53935", label="Predicted P10")
    ax1.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax1.set_title(f"Predicted P10 vs Actual — {etf_name}\n"
                  f"Coverage: {rolling_result['coverage']:.1f}% (target 90%)", fontsize=11)
    ax1.set_ylabel("(High - Open) / Open (%)")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # 2. Coverage calibration by gap regime
    ax2 = fig.add_subplot(gs[0, 1])
    gap = df["gap_pct"].values[mask]
    regimes = [
        (gap < -0.5,       "Sig Down"),
        ((gap >= -0.5) & (gap < -0.05), "Mod Down"),
        ((gap >= -0.05) & (gap <= 0.05), "Neutral"),
        ((gap > 0.05) & (gap <= 0.5),  "Mod Up"),
        (gap > 0.5,        "Sig Up"),
    ]
    regime_names, coverages, counts = [], [], []
    for rmask, rname in regimes:
        if rmask.sum() > 5:
            cov = np.mean(actual[rmask] >= pred[rmask]) * 100
            regime_names.append(rname)
            coverages.append(cov)
            counts.append(rmask.sum())

    bars = ax2.bar(regime_names, coverages, color=["#B71C1C", "#EF5350", "#757575", "#42A5F5", "#0D47A1"],
                   edgecolor="white", linewidth=0.8)
    ax2.axhline(90, color="#E53935", linestyle="--", linewidth=1.5, label="Target 90%")
    for bar, cov, cnt in zip(bars, coverages, counts):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{cov:.1f}%\n(n={cnt})", ha="center", fontsize=8)
    ax2.set_ylabel("Coverage (%)")
    ax2.set_title("Coverage Calibration by Gap Regime", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.grid(True, axis="y", alpha=0.3)

    # 3. Feature importance / selection order
    ax3 = fig.add_subplot(gs[1, 0])
    sel_order = selection_result["selection_order"]
    feat_names = [s[0] for s in sel_order]
    feat_scores = [s[1] for s in sel_order]
    # Show as horizontal bar chart (score reduction)
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(feat_names)))
    y_pos = range(len(feat_names))
    ax3.barh(y_pos, feat_scores, color=colors, edgecolor="white")
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(feat_names, fontsize=9)
    ax3.set_xlabel("CV Pinball Loss (lower = better)")
    ax3.set_title(f"Forward Feature Selection Order\nBest set size: {selection_result['best_set_size']}", fontsize=11)
    ax3.invert_yaxis()
    ax3.grid(True, axis="x", alpha=0.3)

    # 4. Model comparison
    ax4 = fig.add_subplot(gs[1, 1])
    model_names = ["Statsmodels QR", "LightGBM QR"]
    model_losses = [cv_comparison["statsmodels_cv_loss"], cv_comparison["lightgbm_cv_loss"]]
    bar_colors = ["#42A5F5", "#E53935"]
    bars = ax4.bar(model_names, model_losses, color=bar_colors, edgecolor="white", width=0.5)
    ax4.set_ylabel("CV Pinball Loss")
    ax4.set_title(f"Model Comparison — Winner: {cv_comparison['winner'].upper()}", fontsize=11)
    for bar, loss in zip(bars, model_losses):
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0001,
                 f"{loss:.5f}", ha="center", fontsize=9)
    ax4.grid(True, axis="y", alpha=0.3)

    # 5. Predicted offset vs static baseline over time
    ax5 = fig.add_subplot(gs[2, :])
    static = static_baseline[mask]
    ax5.plot(dates, pred, color="#E53935", linewidth=1.2, alpha=0.8, label="Model Predicted P10")
    # Static baseline as scatter (it's per-regime, not continuous)
    ax5.scatter(dates, static, s=12, alpha=0.4, color="#757575", label="Static Per-Regime P10")
    ax5.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax5.set_title("Predicted Offset vs Static Baseline Over Time", fontsize=11)
    ax5.set_ylabel("P10 Offset (%)")
    ax5.set_xlabel("Date")
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)

    plt.suptitle(f"Open-to-High P10 Prediction System — {etf_name}",
                 fontsize=14, fontweight="bold", y=0.98)

    out_path = os.path.join(OUT_DIR, f"open_high_predictions_{etf_key}.png")
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved visualization to {out_path}")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# Model Serialization (for backtest integration)
# ─────────────────────────────────────────────────────────────────────────────
def save_model(features, model_type, etf_key, sm_coeffs=None, lgb_model=None,
               lgb_bagged_models=None,
               cv_comparison=None, selection_result=None, rolling_result_summary=None,
               calibration_offset=0.0, adaptive_quantile=QUANTILE,
               vol_regime_cal=None):
    """Save model metadata + LightGBM model(s) to disk for backtest integration."""
    os.makedirs(OUT_DIR, exist_ok=True)

    # Save LightGBM model file(s)
    lgb_paths = []
    if lgb_bagged_models:
        for i, m in enumerate(lgb_bagged_models):
            path = os.path.join(OUT_DIR, f"open_high_lgb_{etf_key}_bag{i}.txt")
            m.booster_.save_model(path)
            lgb_paths.append(path)
    elif lgb_model is not None:
        path = os.path.join(OUT_DIR, f"open_high_lgb_{etf_key}.txt")
        lgb_model.booster_.save_model(path)
        lgb_paths.append(path)

    # Save JSON metadata
    meta = {
        "etf_key": etf_key,
        "features": features,
        "model_type": model_type,
        "quantile": QUANTILE,
        "adaptive_quantile": adaptive_quantile,
        "calibration_offset": calibration_offset,
        "vol_regime_calibration": vol_regime_cal,
        "cv_comparison": cv_comparison,
        "selection_order": [(f, float(s)) for f, s in selection_result["selection_order"]],
        "best_set_size": selection_result["best_set_size"],
        "rolling_coverage": rolling_result_summary["coverage"],
        "rolling_mean_pred_offset": rolling_result_summary["mean_pred_offset"],
        "rolling_pinball_loss": rolling_result_summary["pinball_loss"],
        "rolling_n_predictions": rolling_result_summary["n_predictions"],
        "statsmodels_coeffs": sm_coeffs,
        "lgb_model_paths": lgb_paths,
    }

    json_path = os.path.join(OUT_DIR, f"open_high_model_{etf_key}.json")
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"Saved model metadata to {json_path}")
    return json_path


def load_model(etf_key: str) -> dict:
    """Load trained model from disk for prediction."""
    json_path = os.path.join(OUT_DIR, f"open_high_model_{etf_key}.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No trained model found at {json_path}. Run training first.")

    with open(json_path, "r") as f:
        meta = json.load(f)

    # Load LightGBM model(s) — support both single and bagged
    lgb_boosters = []
    paths = meta.get("lgb_model_paths", [])
    if not paths:
        # Legacy: single model path
        legacy_path = meta.get("lgb_model_path")
        if legacy_path and os.path.exists(legacy_path):
            paths = [legacy_path]
    for p in paths:
        if os.path.exists(p):
            lgb_boosters.append(lgb.Booster(model_file=p))

    meta["lgb_boosters"] = lgb_boosters
    # Legacy compat
    meta["lgb_booster"] = lgb_boosters[0] if lgb_boosters else None
    return meta


def predict_single(model_meta: dict, features_df: pd.DataFrame,
                    current_vol20: float = None) -> float:
    """Predict p10 offset for a single row (latest data point).
    Applies vol-regime-conditional calibration if available, else flat calibration_offset."""
    features = model_meta["features"]
    model_type = model_meta["model_type"]

    preds = []
    # Bagged LightGBM predictions (average over all models)
    boosters = model_meta.get("lgb_boosters", [])
    if not boosters:
        # Legacy single booster
        b = model_meta.get("lgb_booster")
        boosters = [b] if b else []

    if model_type in ("lightgbm", "ensemble") and boosters:
        lgb_preds = np.mean([b.predict(features_df[features].values)[0] for b in boosters])
        preds.append(lgb_preds)

    if model_type in ("statsmodels", "ensemble") and model_meta.get("statsmodels_coeffs"):
        coeffs = model_meta["statsmodels_coeffs"]
        x = features_df[features].values[0]
        pred_sm = coeffs["Intercept"] + sum(coeffs[f] * x[i] for i, f in enumerate(features))
        preds.append(pred_sm)

    if not preds:
        raise ValueError("No trained model available for prediction")

    raw_pred = np.mean(preds)

    # Apply vol-regime-conditional calibration if available
    vol_cal = model_meta.get("vol_regime_calibration")
    if vol_cal and current_vol20 is not None:
        vol_thresh = vol_cal["vol_threshold"]
        if current_vol20 <= vol_thresh:
            offset = vol_cal["low_vol_offset"]
        else:
            offset = vol_cal["high_vol_offset"]
    else:
        offset = model_meta.get("calibration_offset", 0.0)

    return raw_pred + offset


# ─────────────────────────────────────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Open-to-High P10 Prediction System — 90% fill-rate limit orders")
    parser.add_argument("-e", "--etf", type=str, required=True, choices=["50", "300", "500"],
                        help="ETF key: 50, 300, or 500")
    parser.add_argument("--predict", action="store_true",
                        help="Only predict today's offset (requires prior training)")
    parser.add_argument("--max-features", type=int, default=6,
                        help="Maximum number of features to select (default: 6)")
    parser.add_argument("--retrain-every", type=int, default=RETRAIN_EVERY,
                        help="Retrain rolling model every N days (default: 60)")
    parser.add_argument("--cv-splits", type=int, default=5,
                        help="Number of time-series CV splits (default: 5)")
    parser.add_argument("--pool", action="store_true",
                        help="Pool all 3 ETFs for training (cross-ETF, more data)")
    args = parser.parse_args()

    etf_key = args.etf
    cfg = ETF_CONFIG[etf_key]
    os.makedirs(OUT_DIR, exist_ok=True)

    # ── Predict-only mode ──
    if args.predict:
        print(f"Loading trained model for {cfg['name']}...")
        meta = load_model(etf_key)
        print(f"  Features: {meta['features']}")
        print(f"  Model type: {meta['model_type']}")
        print(f"  Adaptive quantile: {meta.get('adaptive_quantile', QUANTILE):.4f}")
        print(f"  Calibration offset: {meta.get('calibration_offset', 0.0):+.4f}%")
        print(f"  Training coverage: {meta['rolling_coverage']:.1f}%")

        # Load latest data and predict
        df = load_and_engineer(etf_key)
        latest = df.iloc[[-1]].copy()
        current_vol = float(latest["vol20"].values[0]) if "vol20" in latest.columns else None
        p10 = predict_single(meta, latest, current_vol20=current_vol)
        latest_date = pd.to_datetime(latest["date"].values[0]).strftime("%Y-%m-%d")
        latest_open = latest["open"].values[0]
        limit_price = latest_open * (1 + p10 / 100.0)

        print(f"\n{'='*60}")
        print(f"  Date:       {latest_date}")
        print(f"  Open:       {latest_open:.4f}")
        print(f"  Predicted P10 offset: {p10:.4f}%")
        print(f"  Limit sell at:  {limit_price:.4f}  (90% fill confidence)")
        print(f"  Gap today:  {latest['gap_pct'].values[0]:.3f}%")
        print(f"{'='*60}")
        return

    # ── Full Training Pipeline ──
    print(f"\n{'='*60}")
    print(f"  Open-to-High P10 Prediction System")
    print(f"  ETF: {cfg['name']}")
    print(f"  Target: {QUANTILE*100:.0f}th percentile (90% fill rate)")
    print(f"{'='*60}\n")

    # Step 1: Load & engineer features
    print("Step 1: Loading data & engineering features...")
    df = load_and_engineer(etf_key)
    feature_cols = list(CANDIDATE_FEATURES)

    if args.pool:
        # Cross-ETF pooled training: use all 3 ETFs for fitting
        print("  Cross-ETF POOL mode: loading all 3 ETFs...")
        df_pooled = load_and_engineer_all()
        X = df_pooled[feature_cols].copy()
        y = df_pooled["y"].copy()
        print(f"  Pooled data: {len(df_pooled)} trading days from {len(ETF_CONFIG)} ETFs")
    else:
        X = df[feature_cols].copy()
        y = df["y"].copy()
    print(f"  Target ETF: {len(df)} trading days, {len(feature_cols)} candidate features")
    print(f"  Target stats: mean={y.mean():.3f}%, median={y.median():.3f}%, "
          f"p10={y.quantile(0.10):.3f}%\n")

    # Step 2: Forward feature selection
    print("Step 2: Forward feature selection (CV pinball loss)...")
    sel_result = forward_feature_selection(X, y, max_features=args.max_features,
                                            n_splits=args.cv_splits)
    best_size = sel_result["best_set_size"]
    best_features = sel_result["best_sets"][best_size]
    print(f"\n  Best feature set (size={best_size}): {best_features}")
    for size, feats in sel_result["best_sets"].items():
        score = sel_result["cv_scores"][size]
        print(f"    Size {size}: {feats} → CV loss = {score:.6f}")

    # Step 3: Compare models
    print(f"\nStep 3: Comparing Statsmodels QR vs LightGBM ({args.cv_splits}-fold TS CV)...")
    cv_comp = compare_models_cv(X, y, best_features, n_splits=args.cv_splits)
    model_type = cv_comp["winner"]
    print(f"  Statsmodels CV loss: {cv_comp['statsmodels_cv_loss']:.6f}")
    print(f"  LightGBM CV loss:    {cv_comp['lightgbm_cv_loss']:.6f}")
    print(f"  Winner: {model_type.upper()}\n")

    # Step 4: Adaptive quantile search (find q' that natively achieves ~90% coverage)
    print("Step 4: Adaptive quantile search for 90% coverage...")
    aq_result = adaptive_quantile_search(X, y, best_features, model_type,
                                          n_splits=args.cv_splits)
    adaptive_q = aq_result["quantile"]
    print(f"  Adaptive quantile: {adaptive_q:.4f} (coverage={aq_result['coverage']:.1f}%, "
          f"cal_offset={aq_result['calibration_offset']:+.4f}%)\n")

    # Step 5: Block-bootstrap augmentation + train final bagged models
    print("Step 5: Block-bootstrap augmentation & bagged training...")
    X_aug, y_aug = block_bootstrap_augment(X, y)
    print(f"  Real data: {len(X)} rows → Augmented: {len(X_aug)} rows "
          f"(+{len(X_aug)-len(X)} synthetic, {BLOCK_SIZE}-day blocks)")

    # Train bagged LightGBM models (N_BAGGING_MODELS models on bootstrap resamples)
    bagged_models = train_lightgbm_bagged(X_aug, y_aug, best_features, quantile=adaptive_q)
    print(f"  Trained {len(bagged_models)} bagged LightGBM models (q={adaptive_q:.4f}, {len(X_aug)} rows each).")

    sm_coeffs = None
    try:
        sm_result = train_statsmodels_qr(X_aug, y_aug, best_features, quantile=adaptive_q)
        sm_coeffs = {"Intercept": float(sm_result.params["Intercept"])}
        for f in best_features:
            sm_coeffs[f] = float(sm_result.params[f])
        print(f"  Statsmodels QR coefficients:")
        for k, v in sm_coeffs.items():
            print(f"    {k}: {v:.6f}")
    except Exception as e:
        print(f"  Statsmodels QR failed: {e}")

    # Step 6: Rolling validation (bagged, with vol-regime calibration)
    # Use target ETF data only for validation (not pooled)
    X_val = df[feature_cols].copy()
    y_val = df["y"].copy()
    print(f"\nStep 6: Rolling validation (retrain every {args.retrain_every} days, bagged)...")
    roll_result = rolling_validation(X_val, y_val, best_features, model_type,
                                      retrain_every=args.retrain_every, use_bagging=True)

    # Compute flat calibration offset
    cal_offset = compute_calibration_offset(
        roll_result["predictions"], roll_result["actuals"])

    # Compute vol-regime-conditional calibration
    vol20_arr = df["vol20"].values
    vol_regime_cal = compute_vol_regime_calibration(
        roll_result["predictions"], roll_result["actuals"], vol20_arr)

    # Recompute coverage after vol-regime calibration
    mask_cal = ~np.isnan(roll_result["predictions"]) & ~np.isnan(roll_result["actuals"]) & ~np.isnan(vol20_arr)
    cal_preds = np.where(
        vol20_arr[mask_cal] <= vol_regime_cal["vol_threshold"],
        roll_result["predictions"][mask_cal] + vol_regime_cal["low_vol_offset"],
        roll_result["predictions"][mask_cal] + vol_regime_cal["high_vol_offset"])
    cal_actuals = roll_result["actuals"][mask_cal]
    cal_coverage = vol_regime_cal["coverage"]
    cal_mean_offset = np.mean(cal_preds)

    # Also compute flat-calibrated coverage for comparison
    flat_cal_preds = roll_result["predictions"][mask_cal] + cal_offset
    flat_cal_coverage = np.mean(cal_actuals >= flat_cal_preds) * 100

    print(f"  Raw predictions: {roll_result['n_predictions']} days")
    print(f"  Raw coverage: {roll_result['coverage']:.1f}%")
    print(f"  Flat calibrated coverage: {flat_cal_coverage:.1f}%  (offset={cal_offset:+.4f}%)")
    print(f"  Vol-regime calibrated coverage: {cal_coverage:.1f}%  (target: {TARGET_COVERAGE*100:.0f}%)")
    print(f"    Low-vol offset (vol20 <= {vol_regime_cal['vol_threshold']:.2f}): {vol_regime_cal['low_vol_offset']:+.4f}%")
    print(f"    High-vol offset (vol20 >  {vol_regime_cal['vol_threshold']:.2f}): {vol_regime_cal['high_vol_offset']:+.4f}%")
    print(f"  Mean predicted offset (calibrated): {cal_mean_offset:.4f}%")
    print(f"  Mean actual: {roll_result['mean_actual']:.4f}%")
    print(f"  Pinball loss (raw): {roll_result['pinball_loss']:.6f}")

    # Update roll_result for downstream use
    roll_result["coverage"] = cal_coverage
    roll_result["mean_pred_offset"] = cal_mean_offset

    # Step 7: Static baseline comparison
    print(f"\nStep 7: Static baseline comparison...")
    static_p10 = compute_static_baseline(X_val, y_val)
    static_mask = ~np.isnan(static_p10) & ~np.isnan(roll_result["predictions"])
    static_cov = np.mean(roll_result["actuals"][static_mask] >= static_p10[static_mask]) * 100
    static_mean = np.nanmean(static_p10)
    print(f"  Static coverage: {static_cov:.1f}%")
    print(f"  Static mean offset: {static_mean:.4f}%")
    print(f"  Model coverage (vol-regime calibrated): {cal_coverage:.1f}%")
    print(f"  Model mean offset (calibrated): {cal_mean_offset:.4f}%")

    improvement = cal_mean_offset - static_mean
    print(f"  Improvement (model - static): {improvement:+.4f}% "
          f"({'tighter' if improvement > 0 else 'wider'} → "
          f"{'better' if improvement > 0 else 'worse'} fill price)")

    # Step 8: Feature importance from first bagged LightGBM model
    lgb_importance = dict(zip(best_features, bagged_models[0].feature_importances_))
    print(f"\n  LightGBM Feature Importance (bag 0):")
    for f, imp in sorted(lgb_importance.items(), key=lambda x: -x[1]):
        print(f"    {f}: {imp}")

    # Step 9: Visualization
    print(f"\nStep 8: Generating visualization...")
    plot_results(df, best_features, sel_result, cv_comp,
                 roll_result, cfg["name"], etf_key, static_p10)

    # Step 10: Save model
    print(f"\nStep 9: Saving model...")
    roll_summary = {
        "coverage": cal_coverage,
        "mean_pred_offset": cal_mean_offset,
        "pinball_loss": roll_result["pinball_loss"],
        "n_predictions": roll_result["n_predictions"],
    }
    save_model(best_features, model_type, etf_key,
               sm_coeffs=sm_coeffs, lgb_bagged_models=bagged_models,
               cv_comparison=cv_comp, selection_result=sel_result,
               rolling_result_summary=roll_summary,
               calibration_offset=cal_offset,
               adaptive_quantile=adaptive_q,
               vol_regime_cal=vol_regime_cal)

    # Final summary
    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE — {cfg['name']}")
    print(f"  Best features: {best_features}")
    print(f"  Model: {model_type.upper()}")
    print(f"  Bagged models: {len(bagged_models)}")
    print(f"  Adaptive quantile: {adaptive_q:.4f}")
    print(f"  Vol-regime calibration: low={vol_regime_cal['low_vol_offset']:+.4f}%, high={vol_regime_cal['high_vol_offset']:+.4f}%")
    print(f"  Calibrated coverage: {cal_coverage:.1f}%")
    print(f"  Run with --predict to get today's limit order offset")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
