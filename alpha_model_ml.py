"""
alpha_model_ml.py — Phase 2: LightGBM regime models
====================================================
Per-regime supervised models replacing the linear weighted score:
  - Crash regimes (reg3, reg4): binary classifier → P(worst_dd_m <= -0.05)
  - Fall regimes  (reg1, reg2): binary classifier → P(fwd_ret_m < 0)

Output for all regimes is a calibrated probability in [0,1] (higher = more bearish),
so the validator's score-threshold mechanism works uniformly.

Anti-overfit measures (per plan):
  - Shallow trees (num_leaves=8, max_depth=3), min_child_samples=50.
  - Monotone constraints = +1 for every feature (all ind_* are bearish-positive).
  - Bagged ensemble (N=5 bootstrap bags), probabilities averaged.
  - Isotonic regression calibration on a held-out split.
  - Walk-forward (expanding, purged) training for OOS predictions.

Usage:
  python -m alpha_model_ml -e 300          # train + save models
  python -m alpha_model_ml -e all          # train all ETFs
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.isotonic import IsotonicRegression

from alpha_model import AlphaModel
from optimize_put_alpha import compute_forward_targets, _make_fold_splits, _purge_train, MIN_TRAIN_ROWS

MODEL_DIR = "backtest/alpha_ml_models"
PHASE1_FILE = "backtest/alpha_put_models.json"
OOS_START_YEAR = 2021
N_BAGS = 5
CRASH_THRESH = -0.05  # worst_dd <= this = crash event

# Feature set (bearish-positive normalized indicators from Phase 1).
FEATURES = [
    "ind_rsi_high", "ind_rsi_low", "ind_skew_neg", "ind_kurt_high",
    "ind_vol_accel_high", "ind_iv_vol_low", "ind_dd_deep",
    "ind_dist_sma50_neg", "ind_dist_sma200_neg", "ind_roc5_neg",
    "ind_roc20_neg", "ind_macd_neg", "ind_obv_divergence", "ind_volume_spike",
    "ind_atr_ratio_high", "ind_vol_of_vol_high", "ind_range_expansion_high",
    "ind_term_structure_neg", "ind_rsi_divergence_neg",
]

REGIME_IS_CRASH = {"reg1": False, "reg2": False, "reg3": True, "reg4": True}


def _active_features(df):
    return [f for f in FEATURES if f in df.columns]


def _make_labels(df, horizon, is_crash):
    """Binary labels: crash → worst_dd<=thresh; fall → fwd_ret<0."""
    fwd_ret, worst_dd = compute_forward_targets(df, horizon)
    if is_crash:
        y = (worst_dd <= CRASH_THRESH).astype(float)
    else:
        y = (fwd_ret < 0).astype(float)
    return pd.Series(y, index=df.index), fwd_ret, worst_dd


def _train_bagged(X, y, feature_names, seed=42):
    """Train N_BAGS bootstrap LightGBM classifiers with monotone constraints."""
    n = len(X)
    rng = np.random.RandomState(seed)
    models = []
    mono = [1] * len(feature_names)  # all features bearish-positive
    pos_frac = float(y.mean())
    spw = max(1.0, (1.0 - pos_frac) / max(pos_frac, 1e-3))  # balance rare class
    for i in range(N_BAGS):
        idx = rng.choice(n, size=n, replace=True)
        Xb = X.iloc[idx][feature_names]
        yb = y.iloc[idx]
        if yb.nunique() < 2:
            continue
        m = lgb.LGBMClassifier(
            objective="binary",
            num_leaves=8, max_depth=3, n_estimators=150,
            learning_rate=0.03, min_child_samples=50,
            reg_alpha=1.0, reg_lambda=1.0,
            subsample=0.7, subsample_freq=1, colsample_bytree=0.7,
            monotone_constraints=mono,
            scale_pos_weight=spw,
            verbose=-1, random_state=seed + i,
        )
        m.fit(Xb.values, yb.values)
        models.append(m)
    return models


def _predict_raw(models, X, feature_names):
    """Average raw probability across bags. Returns np.array."""
    if not models:
        return np.full(len(X), 0.5)
    preds = np.stack([m.predict_proba(X[feature_names].values)[:, 1] for m in models])
    return preds.mean(axis=0)


def _calibrate_isotonic(raw_train, y_train, raw_test):
    """Fit isotonic on train, apply to test. Clips to [0,1]."""
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(raw_train, y_train)
    return iso.transform(raw_test), iso


def predict_proba_all(df, etf_choice, walk_forward=True, verbose=False):
    """
    Return (preds_dict, thresholds_dict) where:
      preds_dict[regime] = pd.Series of calibrated probabilities aligned to df.index
      thresholds_dict[regime] = float, train-derived p85 cutoff (avg across folds)
    walk_forward=True: each row predicted by a model trained only on prior data
    (expanding window, purged by horizon). Honest OOS prediction.
    walk_forward=False: train on all data, predict all (live deployment).
    """
    df_norm = AlphaModel().compute_normalized_indicators(df)
    feats = _active_features(df_norm)
    X = df_norm[feats]

    with open(PHASE1_FILE) as f:
        p1 = json.load(f)
    etf_cfg = p1.get(etf_choice, {})

    out = {}
    thresholds = {}
    n = len(df_norm)
    dates = pd.to_datetime(df_norm.index)
    yr_arr = df_norm.index.year.values
    pos = np.arange(n)

    for r_key, is_crash in REGIME_IS_CRASH.items():
        if r_key not in etf_cfg:
            continue
        horizon = int(etf_cfg[r_key]["horizon"])
        y, _, _ = _make_labels(df_norm, horizon, is_crash)
        preds = np.full(n, np.nan)
        fold_thr = []

        if walk_forward:
            splits = _make_fold_splits(df_norm)
            for (train_idx, test_idx) in splits:
                test_start = dates[test_idx[0]]
                train_idx_p = _purge_train(train_idx, dates.values, test_start, horizon)
                if len(train_idx_p) < MIN_TRAIN_ROWS:
                    continue
                n_tr = len(train_idx_p)
                n_cal = max(60, n_tr // 5)
                cal_idx = train_idx_p[-n_cal:]
                fit_idx = train_idx_p[:-n_cal]
                if len(fit_idx) < MIN_TRAIN_ROWS // 2:
                    fit_idx = train_idx_p
                    cal_idx = train_idx_p
                y_fit = y.iloc[fit_idx].dropna()
                X_fit = X.iloc[fit_idx].loc[y_fit.index]
                models = _train_bagged(X_fit, y_fit, feats)
                # Train-set threshold: p85 of calibrated probs on the calibration slice.
                raw_cal = _predict_raw(models, X.iloc[cal_idx], feats)
                y_cal = y.iloc[cal_idx]
                if y_cal.notna().any() and len(y_cal) >= 30:
                    cal_cal, _ = _calibrate_isotonic(raw_cal, y_cal.dropna().values, raw_cal)
                    fold_thr.append(float(np.percentile(cal_cal, 85)))
                raw_test = _predict_raw(models, X.iloc[test_idx], feats)
                if y_cal.notna().any() and len(y_cal) >= 30:
                    y_cal_v = y_cal.dropna()
                    raw_cal_v = _predict_raw(models, X.loc[y_cal_v.index], feats)
                    _, iso = _calibrate_isotonic(raw_cal_v, y_cal_v.values, raw_test)
                    cal_test = iso.transform(raw_test)
                else:
                    cal_test = raw_test
                preds[test_idx] = cal_test
            thresholds[r_key] = float(np.mean(fold_thr)) if fold_thr else 0.5
            if verbose:
                valid = ~np.isnan(preds)
                print(f"    {r_key}: WF preds on {valid.sum()} rows "
                      f"(pos_rate y={y[valid].mean():.3f}, pred={np.nanmean(preds):.3f}, "
                      f"thr={thresholds[r_key]:.3f})")
        else:
            yv = y.dropna()
            Xv = X.loc[yv.index]
            n_cal = max(60, len(yv) // 5)
            cal_idx = yv.index[-n_cal:]
            fit_idx = yv.index[:-n_cal]
            models = _train_bagged(Xv.loc[fit_idx], yv.loc[fit_idx], feats)
            raw_all = _predict_raw(models, X, feats)
            raw_cal = _predict_raw(models, Xv.loc[cal_idx], feats)
            cal_all, iso = _calibrate_isotonic(raw_cal, yv.loc[cal_idx].values, raw_all)
            preds = cal_all
            thresholds[r_key] = float(np.percentile(iso.transform(raw_cal), 85))

        out[r_key] = pd.Series(preds, index=df_norm.index)
    return out, thresholds


def train_and_save(etf_choice, df):
    """Train full-data models and persist (for live deployment + reference)."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    df_norm = AlphaModel().compute_normalized_indicators(df)
    feats = _active_features(df_norm)
    X = df_norm[feats]
    with open(PHASE1_FILE) as f:
        etf_cfg = json.load(f).get(etf_choice, {})

    manifest = {"etf": etf_choice, "features": feats, "n_bags": N_BAGS,
                "regimes": {}}
    for r_key, is_crash in REGIME_IS_CRASH.items():
        if r_key not in etf_cfg:
            continue
        horizon = int(etf_cfg[r_key]["horizon"])
        y, _, _ = _make_labels(df_norm, horizon, is_crash)
        yv = y.dropna()
        Xv = X.loc[yv.index]
        n_cal = max(60, len(yv) // 5)
        cal_idx = yv.index[-n_cal:]
        fit_idx = yv.index[:-n_cal]
        models = _train_bagged(Xv.loc[fit_idx], yv.loc[fit_idx], feats)
        raw_cal = _predict_raw(models, Xv.loc[cal_idx], feats)
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(raw_cal, yv.loc[cal_idx].values)
        # Save bags
        bag_dir = os.path.join(MODEL_DIR, f"{etf_choice}_{r_key}")
        os.makedirs(bag_dir, exist_ok=True)
        for i, m in enumerate(models):
            m.booster_.save_model(os.path.join(bag_dir, f"bag{i}.txt"))
        # Save isotonic params
        manifest["regimes"][r_key] = {
            "horizon": horizon, "is_crash": is_crash,
            "n_fit": int(len(fit_idx)), "n_cal": int(len(cal_idx)),
            "positive_rate": float(yv.mean()),
            "iso_X_min": float(iso.X_min_), "iso_X_max": float(iso.X_max_),
            "iso_X_thresholds": iso.X_thresholds_.tolist(),
            "iso_y_thresholds": iso.y_thresholds_.tolist(),
        }
        print(f"  {etf_choice} {r_key}: saved {len(models)} bags (pos_rate={yv.mean():.3f}, "
              f"n_fit={len(fit_idx)})")
    with open(os.path.join(MODEL_DIR, f"manifest_{etf_choice}.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Saved ML manifest → {MODEL_DIR}/manifest_{etf_choice}.json")


def main():
    parser = argparse.ArgumentParser(description="Phase 2 LightGBM regime model trainer")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500", "all"], default="300")
    args = parser.parse_args()
    etfs = ["50", "300", "500"] if args.etf == "all" else [args.etf]

    from backtest_engine import select_underlying, load_data
    for etf_choice in etfs:
        print(f"\n=== Training Phase 2 ML models for {etf_choice}ETF ===")
        select_underlying(etf_choice)
        inst, opt, etf = load_data()
        train_and_save(etf_choice, etf)
        # Quick OOS AUC report
        from sklearn.metrics import roc_auc_score
        preds, _ = predict_proba_all(etf, etf_choice, walk_forward=True, verbose=True)
        print(f"  Walk-forward OOS AUC (regime: AUC / n_valid):")
        with open(PHASE1_FILE) as f:
            etf_cfg = json.load(f).get(etf_choice, {})
        for r_key, p in preds.items():
            horizon = int(etf_cfg[r_key]["horizon"])
            y, _, _ = _make_labels(AlphaModel().compute_normalized_indicators(etf), horizon,
                                   REGIME_IS_CRASH[r_key])
            valid = p.notna() & y.notna()
            if valid.sum() > 30 and y[valid].nunique() == 2:
                auc = roc_auc_score(y[valid], p[valid])
                print(f"    {r_key}: AUC={auc:.3f} (n={valid.sum()})")
            else:
                print(f"    {r_key}: n/a (n={valid.sum()})")


if __name__ == "__main__":
    main()
