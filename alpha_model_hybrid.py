"""
alpha_model_hybrid.py — Phase 3: Rule-anchored hybrid stack
============================================================
Layer 1 inputs (all look-ahead-free):
  - Phase 1 linear weighted score (from alpha_put_models.json), expanding-rank normalized.
  - Phase 2 LightGBM calibrated probability (walk-forward OOS).
  - Rule flags: statistically-validated binary signals from FINDINGS.md (bias-free
    expanding-window quantiles where applicable).
Layer 2: L2-regularized logistic regression combining the inputs → final P(bad).
  Trained walk-forward (expanding, purged). Strong regularization (C=0.5) given
  the tiny effective sample and to avoid the over-triggering seen in pure ML.

The rule flags are the most robust component (validated p-values in FINDINGS.md);
anchoring on them is the key anti-overfit device.

predict_all(df, etf_choice) → (preds_dict, thresholds_dict)
"""

import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from alpha_model import AlphaModel
from alpha_model_ml import predict_proba_all, _make_labels, _active_features, REGIME_IS_CRASH, PHASE1_FILE
from optimize_put_alpha import compute_forward_targets, _make_fold_splits, _purge_train, MIN_TRAIN_ROWS

PHASE1_FILE_HYB = "backtest/alpha_put_models.json"


def _roll_q(series, q, min_periods=252):
    """Expanding-window quantile (look-ahead free)."""
    return series.expanding(min_periods=min_periods).quantile(q)


def compute_rule_flags(df_norm):
    """Build validated rule flags from FINDINGS.md. Returns DataFrame of 0/1 flags.
    Rules are look-ahead-free (expanding-window quantiles for adaptive thresholds)."""
    rf = pd.DataFrame(index=df_norm.index)
    c = "close_adj" if "close_adj" in df_norm.columns else "close"

    # Generic: low-kurtosis + neg-skew (300ETF 93.3% neg-30d)
    if "kurt_20" in df_norm.columns and "skew_20" in df_norm.columns:
        kurt_q10 = _roll_q(df_norm["kurt_20"], 0.10)
        rf["rule_kurt_skew"] = ((df_norm["kurt_20"] < kurt_q10) & (df_norm["skew_20"] < -0.3)).astype(float)

    # 300ETF bear-trend: deep drawdown + far below SMA50 (p=0.0003, 2.33x lift)
    if "dd_252" in df_norm.columns and "dist_sma50" in df_norm.columns:
        rf["rule_bear_trend"] = ((df_norm["dd_252"] < -0.15) & (df_norm["dist_sma50"] < -1.0)).astype(float)

    # 300ETF overbought reversal: high RSI + neg skew (p=0.076, 3.09x lift)
    if "rsi14" in df_norm.columns and "skew_20" in df_norm.columns:
        rf["rule_overbought"] = ((df_norm["rsi14"] > 65) & (df_norm["skew_20"] < -0.3)).astype(float)

    # 500ETF skew+close> SMA50 (2.19x lift)
    if "skew_20" in df_norm.columns and "sma50" in df_norm.columns:
        rf["rule_skew_close"] = ((df_norm["skew_20"] < -0.5) & (df_norm[c] > df_norm["sma50"])).astype(float)

    # 50ETF vol spike: vol20 > expanding q90 (2.85x lift)
    if "vol20" in df_norm.columns:
        vol_q90 = _roll_q(df_norm["vol20"], 0.90)
        rf["rule_vol_spike"] = (df_norm["vol20"] > vol_q90).astype(float)

    # 50ETF VRP compression: neg skew + cheap IV (underpriced puts)
    if "skew_20" in df_norm.columns and "iv_vol_ratio" in df_norm.columns:
        rf["rule_vrp_compression"] = ((df_norm["skew_20"] < -0.5) & (df_norm["iv_vol_ratio"] < 0.9)).astype(float)

    rf = rf.fillna(0.0)
    return rf


def _phase1_scores(df_norm, etf_cfg, regime_key):
    """Weighted score from Phase 1 JSON config, expanding-rank normalized to [0,1]."""
    weights = etf_cfg[regime_key]["weights"]
    ws = pd.Series(0.0, index=df_norm.index)
    tw = 0.0
    for col, w in weights.items():
        if col in df_norm.columns:
            ws += df_norm[col].fillna(0.5) * w
            tw += w
    score = (ws / tw) if tw > 0 else ws
    return score.expanding(min_periods=252).rank(pct=True)


def _stack_features(df_norm, etf_cfg, regime_key, p1_ranked, p2_prob, rules):
    """Assemble logistic features for a regime. Returns DataFrame."""
    feats = pd.DataFrame(index=df_norm.index)
    feats["p1_rank"] = p1_ranked.reindex(df_norm.index).fillna(0.5)
    feats["p2_prob"] = p2_prob.reindex(df_norm.index).fillna(0.5)
    # Rule intensity: sum of active rule flags (captures how many validated signals agree).
    rule_cols = [c for c in rules.columns if c.startswith("rule_")]
    feats["rule_intensity"] = rules[rule_cols].sum(axis=1) / max(len(rule_cols), 1)
    # Strongest-rule flag: any rule active.
    feats["any_rule"] = (rules[rule_cols].sum(axis=1) > 0).astype(float)
    return feats


def predict_all(df, etf_choice):
    """Return (preds_dict, thresholds_dict) of final hybrid probabilities, walk-forward OOS."""
    df_norm = AlphaModel().compute_normalized_indicators(df)
    with open(PHASE1_FILE_HYB) as f:
        etf_cfg = json.load(f).get(etf_choice, {})

    rules = compute_rule_flags(df_norm)
    p2_preds, _ = predict_proba_all(df, etf_choice, walk_forward=True)
    dates = pd.to_datetime(df_norm.index)
    n = len(df_norm)

    out = {}
    thresholds = {}
    for r_key, is_crash in REGIME_IS_CRASH.items():
        if r_key not in etf_cfg or r_key not in p2_preds:
            continue
        horizon = int(etf_cfg[r_key]["horizon"])
        y, _, _ = _make_labels(df_norm, horizon, is_crash)
        p1r = _phase1_scores(df_norm, etf_cfg, r_key)
        feats = _stack_features(df_norm, etf_cfg, r_key, p1r, p2_preds[r_key], rules)
        feat_cols = list(feats.columns)
        preds = np.full(n, np.nan)
        fold_thr = []

        for (train_idx, test_idx) in _make_fold_splits(df_norm):
            test_start = dates[test_idx[0]]
            train_idx_p = _purge_train(train_idx, dates.values, test_start, horizon)
            if len(train_idx_p) < MIN_TRAIN_ROWS:
                continue
            y_tr = y.iloc[train_idx_p].dropna()
            X_tr = feats.iloc[train_idx_p].loc[y_tr.index]
            if y_tr.nunique() < 2 or len(y_tr) < 60:
                # Fallback: blend without logistic (fixed weights).
                X_test = feats.iloc[test_idx][feat_cols]
                blend = 0.45 * X_test["p1_rank"] + 0.40 * X_test["p2_prob"] + 0.15 * X_test["rule_intensity"]
                preds[test_idx] = blend.values
                continue
            # L2-regularized logistic (C=0.5 → strong regularization, anti-overfit).
            try:
                lr = LogisticRegression(C=0.5, max_iter=200, class_weight="balanced")
                lr.fit(X_tr.values, y_tr.values)
                X_test = feats.iloc[test_idx][feat_cols]
                proba = lr.predict_proba(X_test.values)[:, 1]
                preds[test_idx] = proba
                # Train threshold from in-fold predictions
                tr_proba = lr.predict_proba(X_tr.values)[:, 1]
                fold_thr.append(float(np.percentile(tr_proba, 85)))
            except Exception:
                X_test = feats.iloc[test_idx][feat_cols]
                blend = 0.45 * X_test["p1_rank"] + 0.40 * X_test["p2_prob"] + 0.15 * X_test["rule_intensity"]
                preds[test_idx] = blend.values

        out[r_key] = pd.Series(preds, index=df_norm.index)
        thresholds[r_key] = float(np.mean(fold_thr)) if fold_thr else 0.5
    return out, thresholds


if __name__ == "__main__":
    import argparse
    from backtest_engine import select_underlying, load_data
    from sklearn.metrics import roc_auc_score
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", choices=["50", "300", "500", "all"], default="300")
    args = parser.parse_args()
    etfs = ["50", "300", "500"] if args.etf == "all" else [args.etf]
    for etf_choice in etfs:
        select_underlying(etf_choice)
        inst, opt, etf = load_data()
        preds, _ = predict_all(etf, etf_choice)
        with open(PHASE1_FILE_HYB) as f:
            etf_cfg = json.load(f).get(etf_choice, {})
        dn = AlphaModel().compute_normalized_indicators(etf)
        print(f"\n=== {etf_choice}ETF Phase 3 hybrid walk-forward AUC ===")
        for r_key, p in preds.items():
            horizon = int(etf_cfg[r_key]["horizon"])
            y, _, _ = _make_labels(dn, horizon, REGIME_IS_CRASH[r_key])
            valid = p.notna() & y.notna()
            if valid.sum() > 30 and y[valid].nunique() == 2:
                print(f"  {r_key}: AUC={roc_auc_score(y[valid], p[valid]):.3f} (n={valid.sum()})")
            else:
                print(f"  {r_key}: n/a (n={valid.sum()})")
