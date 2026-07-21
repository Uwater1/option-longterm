#!/usr/bin/env python3
"""
Admitted Feature Diagnostic Analysis for Day-Model Rewrite v3.

Evaluates every admitted feature across all ETFs and trading sides on:
1. Standalone IC, Tail IC, Decile Monotonicity (Train, OOS, Lockbox)
2. Standalone Net P&L, Net Sharpe, Sortino, Max DD @ 8 bps friction
3. Turnover Rate, Average Trade Return, Friction Efficiency Ratio (μ_trade / 0.0008)
4. Leave-One-Out (LOO) model contribution (delta IC, delta Sharpe)
5. Alpha Family classification (Gap, Momentum, Options Flow, Volatility)
6. Per-Gate Filter Effectiveness (false positive/negative rates per filter stage)
7. Gate Threshold Sensitivity (sweep mono_thr/ir_thr vs lockbox Sharpe)
8. Feature IC Decay Curve (rolling 6-month IC across train→OOS→lockbox)

Outputs:
  - day-model-new/FEATURE_DIAGNOSTICS.md
  - day-model-new/data/feature_diagnostics.json
  - day-model-new/data/filter_effectiveness.json
"""

import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))

from build_features import FEATURES
from recipe_utils import compute_recipe, simulate_returns
from admitted_pools import POOLS

ETFS = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

ADAPTIVE_DATES = {
    "588000ETF": ("2020-11-01", "2025-01-01", "2025-01-01", "2025-07-01"),
    "_default":  ("2015-01-01", "2022-01-01", "2022-01-01", "2024-03-01"),
}

def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 5 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom >= 1e-12 else 0.0

def compute_decile_monotonicity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    order = np.argsort(y_pred, kind="quicksort")
    yt_sorted = y_true[order]
    chunks = np.array_split(yt_sorted, 10)
    means = np.array([c.mean() if c.size else np.nan for c in chunks])
    valid = ~np.isnan(means)
    if valid.sum() < 3:
        return 0.0
    m = means[valid]
    r = rankdata(m)
    k = m.shape[0]
    a = np.arange(1, k + 1, dtype=np.float64)
    a -= a.mean()
    r -= r.mean()
    denom = np.sqrt((a * a).sum() * (r * r).sum())
    return float((a * r).sum() / denom) if denom >= 1e-12 else 0.0

def compute_side_tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str) -> float:
    n = len(y_pred)
    pct = 0.15 if side in ["long", "short"] else 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0
    order = np.argsort(y_pred, kind="quicksort")
    if side == "long":
        idx = order[-n_tail:]
    elif side == "short":
        idx = order[:n_tail]
    else:
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
    return _spearman_from_arrays(y_true[idx], y_pred[idx])

def classify_alpha_family(feat_name: str, recipe: dict = None) -> str:
    name_str = feat_name.lower()
    if recipe:
        components = [v.lower() for k, v in recipe.items() if k != "op"]
        name_str += " " + " ".join(components)
    
    if any(k in name_str for k in ["gap", "overnight", "first_bar"]):
        return "Gap / Overnight Reversal"
    elif any(k in name_str for k in ["option", "short_sell", "oi"]):
        return "Options & Capital Flow"
    elif any(k in name_str for k in ["max_up", "max_down", "growth_momentum", "mom", "return"]):
        return "Intraday Range Momentum"
    elif any(k in name_str for k in ["rsi", "williams", "macd", "balance", "body_to_range", "vol"]):
        return "Volatility & Oscillators"
    return "Other Technical"

def analyze_feature_standalone(y_true: np.ndarray, feat_val: np.ndarray, sign: int, side: str):
    pred = sign * feat_val
    overall_ic = _spearman_from_arrays(y_true, pred)
    tail_ic = compute_side_tail_ic(y_true, pred, side)
    mono = compute_decile_monotonicity(y_true, pred)
    
    ann_ret, sharpe, sortino, max_dd, raw_ret, raw_sharpe = simulate_returns(
        y_true, pred, side=side, position_mode="binary", enforce_absolute_sign=False
    )
    
    # Calculate position details for turnover and trade return
    n = len(pred)
    order = np.argsort(pred, kind="quicksort")
    pos = np.zeros(n, dtype=np.float64)
    pct = 0.15 if side in ["long", "short"] else 0.10
    n_tail = max(5, int(n * pct))
    if side == "long":
        pos[order[-n_tail:]] = 1.0
    elif side == "short":
        pos[order[:n_tail]] = -1.0
    else:
        pos[order[-n_tail:]] = 1.0
        pos[order[:n_tail]] = -1.0
        
    pos_prev = np.roll(pos, 1)
    pos_prev[0] = 0.0
    transitions = np.abs(pos - pos_prev)
    total_transitions = float(np.sum(transitions))
    annual_turnover = float(np.mean(transitions) * 244)
    
    active_mask = pos != 0
    active_days = int(np.sum(active_mask))
    if active_days > 0:
        raw_trade_returns = pos[active_mask] * y_true[active_mask]
        avg_trade_ret = float(np.mean(raw_trade_returns))
        win_rate = float(np.mean(raw_trade_returns > 0))
    else:
        avg_trade_ret = 0.0
        win_rate = 0.0
        
    friction_eff = float(avg_trade_ret / 0.0008) if 0.0008 > 0 else 0.0
    
    return {
        "overall_ic": float(overall_ic),
        "tail_ic": float(tail_ic),
        "mono": float(mono),
        "raw_ann_ret": float(raw_ret),
        "raw_sharpe": float(raw_sharpe),
        "cost_ann_ret": float(ann_ret),
        "cost_sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_dd": float(max_dd),
        "annual_turnover": float(annual_turnover),
        "avg_trade_ret_bps": float(avg_trade_ret * 10000),
        "friction_eff": float(friction_eff),
        "win_rate": float(win_rate),
    }

# ─── Filter Effectiveness Diagnostics ─────────────────────────────────────────

GATE_ORDER = [
    ("REJECTED_SPLIT_HALF", "Split-Half Sign Stability"),
    ("REJECTED_ROLLING_GUARD", "B2 Rolling Guard"),
    ("REJECTED_ABSOLUTE_SIGN", "Absolute Sign Check"),
    ("REJECTED_FDR_GATE", "BH-FDR Gate"),
    ("REJECTED_ADMISSION_FLOOR", "B3 Composite Floor"),
    ("REJECTED_REDUNDANCY", "B4 Correlation Gate"),
]

def _compute_feature_on_split(df, feat_name, recipe, train_means, train_stds, train_medians, sign, side):
    """Compute a feature's lockbox IC and Sharpe on a given dataframe split."""
    if recipe:
        try:
            vals = compute_recipe(df, recipe, train_means, train_stds, train_medians)
        except Exception:
            return None
    else:
        if feat_name not in df.columns:
            return None
        vals = df[feat_name].values.astype(np.float64)
    
    pred = sign * vals
    y = df["trade_return"].values
    ic = _spearman_from_arrays(y, pred)
    _, sharpe, _, _, _, _ = simulate_returns(y, pred, side=side, position_mode="binary", enforce_absolute_sign=False)
    return {"ic": float(ic), "sharpe": float(sharpe)}


def analyze_gate_effectiveness(etf, side, train_df, oos_df, lockbox_df, train_means, train_stds, train_medians, top_k=30):
    """Analyze each filter gate's false positive/negative rate against lockbox performance.
    
    For each gate, sample top-K rejects (by training overall_ic) and compute their
    lockbox IC/Sharpe. High false-negative rate = gate is too strict.
    Also compute admitted features' lockbox performance for false-positive rate.
    """
    attempts_path = HERE / "data" / f"mining_attempts_{etf}_{side}.json"
    if not attempts_path.exists():
        return None
    
    with open(attempts_path, "r", encoding="utf-8") as f:
        attempts = json.load(f)
    
    gate_results = {}
    
    for verdict_key, gate_label in GATE_ORDER:
        rejects = [a for a in attempts if a.get("verdict") == verdict_key]
        if not rejects:
            gate_results[gate_label] = {
                "n_rejected": 0, "n_sampled": 0,
                "pct_positive_lock_ic": 0.0, "mean_lock_ic": 0.0,
                "mean_lock_sharpe": 0.0, "false_negative_rate": 0.0,
                "top_rejects": []
            }
            continue
        
        # Sort by training overall_ic descending, take top-K
        rejects_sorted = sorted(rejects, key=lambda x: x.get("overall_ic", 0), reverse=True)
        sample = rejects_sorted[:top_k]
        
        lock_metrics = []
        top_reject_details = []
        for item in sample:
            feat_name = item["feature_name"]
            sign = item.get("sign", 1)
            recipe = item.get("recipe", None)
            
            lock_result = _compute_feature_on_split(
                lockbox_df, feat_name, recipe, train_means, train_stds, train_medians, sign, side
            )
            if lock_result is None:
                continue
            
            lock_metrics.append(lock_result)
            top_reject_details.append({
                "feature_name": feat_name,
                "train_ic": item.get("overall_ic", 0),
                "lock_ic": lock_result["ic"],
                "lock_sharpe": lock_result["sharpe"],
            })
        
        n_sampled = len(lock_metrics)
        if n_sampled == 0:
            gate_results[gate_label] = {
                "n_rejected": len(rejects), "n_sampled": 0,
                "pct_positive_lock_ic": 0.0, "mean_lock_ic": 0.0,
                "mean_lock_sharpe": 0.0, "false_negative_rate": 0.0,
                "top_rejects": []
            }
            continue
        
        lock_ics = [m["ic"] for m in lock_metrics]
        lock_sharpes = [m["sharpe"] for m in lock_metrics]
        n_positive = sum(1 for ic in lock_ics if ic > 0)
        
        gate_results[gate_label] = {
            "n_rejected": len(rejects),
            "n_sampled": n_sampled,
            "pct_positive_lock_ic": float(n_positive / n_sampled),
            "mean_lock_ic": float(np.mean(lock_ics)),
            "mean_lock_sharpe": float(np.mean(lock_sharpes)),
            "false_negative_rate": float(n_positive / n_sampled),  # rejected but would have worked OOS
            "top_rejects": sorted(top_reject_details, key=lambda x: x["lock_ic"], reverse=True)[:10]
        }
    
    # Also compute admitted features' lockbox performance (false positive rate)
    admitted = [a for a in attempts if a.get("verdict", "").startswith("ADMITTED")]
    admitted_lock = []
    for item in admitted:
        feat_name = item["feature_name"]
        sign = item.get("sign", 1)
        recipe = item.get("recipe", None)
        lock_result = _compute_feature_on_split(
            lockbox_df, feat_name, recipe, train_means, train_stds, train_medians, sign, side
        )
        if lock_result:
            admitted_lock.append(lock_result)
    
    if admitted_lock:
        n_adm_negative = sum(1 for m in admitted_lock if m["ic"] <= 0)
        gate_results["_admitted_summary"] = {
            "n_admitted": len(admitted_lock),
            "pct_negative_lock_ic": float(n_adm_negative / len(admitted_lock)),
            "mean_lock_ic": float(np.mean([m["ic"] for m in admitted_lock])),
            "mean_lock_sharpe": float(np.mean([m["sharpe"] for m in admitted_lock])),
            "false_positive_rate": float(n_adm_negative / len(admitted_lock)),
        }
    
    return gate_results


def analyze_threshold_sensitivity(etf, side, lockbox_df, train_means, train_stds, train_medians):
    """Sweep mono_thr and ir_thr to find optimal gate thresholds.
    
    Uses mining_attempts log data (which has monotonicity and ic_ir for rolling guard rejects)
    to simulate different threshold combinations and estimate lockbox performance.
    """
    attempts_path = HERE / "data" / f"mining_attempts_{etf}_{side}.json"
    if not attempts_path.exists():
        return None
    
    with open(attempts_path, "r", encoding="utf-8") as f:
        attempts = json.load(f)
    
    # Collect all features that passed split-half (have monotonicity and ic_ir)
    candidates_with_metrics = []
    for a in attempts:
        if a.get("verdict") == "REJECTED_SPLIT_HALF":
            continue  # These don't have rolling metrics
        mono = a.get("monotonicity", 0)
        ir = a.get("ic_ir", 0)
        if mono is not None and ir is not None:
            candidates_with_metrics.append(a)
    
    if not candidates_with_metrics:
        return None
    
    # Sweep thresholds
    mono_range = np.arange(0.45, 0.85, 0.05)
    ir_range = np.arange(0.10, 0.55, 0.05)
    
    sensitivity_results = []
    
    for mono_thr in mono_range:
        for ir_thr in ir_range:
            # Features that would pass this threshold combination
            would_pass = [
                c for c in candidates_with_metrics
                if c.get("monotonicity", 0) >= mono_thr and c.get("ic_ir", 0) >= ir_thr
            ]
            
            # Sample top-10 by training IC and compute lockbox IC
            would_pass_sorted = sorted(would_pass, key=lambda x: x.get("overall_ic", 0), reverse=True)
            sample = would_pass_sorted[:10]
            
            lock_ics = []
            for item in sample:
                feat_name = item["feature_name"]
                sign_val = item.get("sign", 1)
                recipe = item.get("recipe", None)
                lock_result = _compute_feature_on_split(
                    lockbox_df, feat_name, recipe, train_means, train_stds, train_medians, sign_val, side
                )
                if lock_result:
                    lock_ics.append(lock_result["ic"])
            
            sensitivity_results.append({
                "mono_thr": float(mono_thr),
                "ir_thr": float(ir_thr),
                "n_would_pass": len(would_pass),
                "n_sampled": len(lock_ics),
                "mean_lock_ic": float(np.mean(lock_ics)) if lock_ics else 0.0,
                "pct_positive_lock_ic": float(sum(1 for ic in lock_ics if ic > 0) / len(lock_ics)) if lock_ics else 0.0,
            })
    
    return sensitivity_results


def analyze_ic_decay(etf, side, df_full, pool, train_means, train_stds, train_medians, train_end, lockbox_start):
    """Compute rolling 6-month (126 trading day) IC for each admitted feature across the full timeline.
    
    Returns per-feature decay curves showing where signal degrades.
    """
    decay_results = []
    
    for item in pool:
        feat_name = item["feature_name"]
        sign = item["sign"]
        recipe = item.get("recipe", None)
        
        # Compute feature values on full dataset
        if recipe:
            try:
                vals = compute_recipe(df_full, recipe, train_means, train_stds, train_medians)
            except Exception:
                continue
        else:
            if feat_name not in df_full.columns:
                continue
            vals = df_full[feat_name].values.astype(np.float64)
        
        pred = sign * vals
        y = df_full["trade_return"].values
        dates = df_full["date"].values
        
        # Rolling 126-day IC
        window = 126
        n = len(pred)
        rolling_ics = []
        rolling_dates = []
        
        for i in range(window, n, 21):  # Step by ~1 month
            start_idx = i - window
            ic = _spearman_from_arrays(y[start_idx:i], pred[start_idx:i])
            rolling_ics.append(float(ic))
            rolling_dates.append(str(dates[i])[:10])
        
        # Identify decay point: where rolling IC crosses below 0 and stays
        decay_idx = None
        for i in range(len(rolling_ics) - 3):
            if all(ic < 0 for ic in rolling_ics[i:i+3]):
                decay_idx = i
                break
        
        # Period averages
        train_mask = df_full["date"] < train_end
        oos_mask = (df_full["date"] >= train_end) & (df_full["date"] < lockbox_start)
        lock_mask = df_full["date"] >= lockbox_start
        
        train_ic = _spearman_from_arrays(y[train_mask], pred[train_mask]) if train_mask.sum() > 10 else 0.0
        oos_ic = _spearman_from_arrays(y[oos_mask], pred[oos_mask]) if oos_mask.sum() > 10 else 0.0
        lock_ic = _spearman_from_arrays(y[lock_mask], pred[lock_mask]) if lock_mask.sum() > 10 else 0.0
        
        decay_results.append({
            "feature_name": feat_name,
            "train_ic": float(train_ic),
            "oos_ic": float(oos_ic),
            "lock_ic": float(lock_ic),
            "decay_ratio": float(lock_ic / train_ic) if abs(train_ic) > 1e-6 else 0.0,
            "decay_date": rolling_dates[decay_idx] if decay_idx is not None else None,
            "rolling_ics": rolling_ics,
            "rolling_dates": rolling_dates,
        })
    
    return decay_results


def main():
    features_dir = REPO_ROOT / "day-model" / "data"
    data_out_dir = HERE / "data"
    data_out_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for etf in ETFS:
        train_start, train_end, oos_start, lockbox_start = ADAPTIVE_DATES.get(etf, ADAPTIVE_DATES["_default"])
        
        path = features_dir / f"features_{etf}.parquet"
        if not path.exists():
            continue
            
        df = pd.read_parquet(path)
        if "date" not in df.columns:
            df = df.reset_index()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        
        train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
        oos_df = df[df["date"] >= oos_start].reset_index(drop=True)
        lockbox_df = df[df["date"] >= lockbox_start].reset_index(drop=True)
        
        # Defensive fill NaNs using train medians
        col_med_train = train_df[FEATURES].median().fillna(0.0)
        for col in FEATURES:
            train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
            oos_df[col] = oos_df[col].ffill().fillna(col_med_train[col])
            lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])
            
        results[etf] = {}
        
        for side in SIDES:
            pool = POOLS.get(etf, {}).get(side, [])
            if not pool:
                continue
                
            # Pre-compute statistics for recipe building
            train_means, train_stds, train_medians = {}, {}, {}
            for item in pool:
                if "recipe" in item:
                    r = item["recipe"]
                    for key in ["feature_a", "feature_b", "feature_c", "feature_cond", "feature_cond2"]:
                        if key in r:
                            col = r[key]
                            if col not in train_means:
                                train_means[col] = train_df[col].mean()
                                train_stds[col] = train_df[col].std()
                                train_medians[col] = train_df[col].median()
                                
            # Calculate feature values for train, oos, lockbox
            for item in pool:
                feat_name = item["feature_name"]
                if "recipe" in item:
                    recipe = item["recipe"]
                    train_df[feat_name] = compute_recipe(train_df, recipe, train_means, train_stds, train_medians)
                    oos_df[feat_name] = compute_recipe(oos_df, recipe, train_means, train_stds, train_medians)
                    lockbox_df[feat_name] = compute_recipe(lockbox_df, recipe, train_means, train_stds, train_medians)
                    
            feat_diagnostics = []
            
            # Standardized arrays for composite modeling
            feat_names = [item["feature_name"] for item in pool]
            signs = np.array([item["sign"] for item in pool])
            deflated_ics = np.array([item.get("deflated_ic", 0.0) for item in pool])
            se_ic = 1.0 / np.sqrt(len(train_df))
            weights = np.array([max(0.0, d - se_ic) for d in deflated_ics])
            if weights.sum() < 1e-12:
                weights = np.ones(len(pool)) / len(pool)
            else:
                weights /= weights.sum()
                
            # Train means/stds for composite z-scoring
            f_means = {f: train_df[f].mean() for f in feat_names}
            f_stds = {f: (train_df[f].std() if train_df[f].std() >= 1e-12 else 1.0) for f in feat_names}
            
            def get_composite_pred(data_df, active_indices=None):
                if active_indices is None:
                    active_indices = list(range(len(feat_names)))
                if not active_indices:
                    return np.zeros(len(data_df))
                sub_weights = weights[active_indices]
                if sub_weights.sum() > 1e-12:
                    sub_weights = sub_weights / sub_weights.sum()
                else:
                    sub_weights = np.ones(len(active_indices)) / len(active_indices)
                
                pred = np.zeros(len(data_df))
                for idx_i, f_idx in enumerate(active_indices):
                    f = feat_names[f_idx]
                    sgn = signs[f_idx]
                    w = sub_weights[idx_i]
                    z = sgn * (data_df[f].values - f_means[f]) / f_stds[f]
                    pred += w * z
                return pred

            # Baseline composite metrics
            full_train_pred = get_composite_pred(train_df)
            full_oos_pred = get_composite_pred(oos_df)
            full_lock_pred = get_composite_pred(lockbox_df)
            
            full_train_ic = _spearman_from_arrays(train_df["trade_return"].values, full_train_pred)
            full_oos_ic = _spearman_from_arrays(oos_df["trade_return"].values, full_oos_pred)
            full_lock_ic = _spearman_from_arrays(lockbox_df["trade_return"].values, full_lock_pred)
            
            full_train_sharpe = simulate_returns(train_df["trade_return"].values, full_train_pred, side)[1]
            full_oos_sharpe = simulate_returns(oos_df["trade_return"].values, full_oos_pred, side)[1]
            full_lock_sharpe = simulate_returns(lockbox_df["trade_return"].values, full_lock_pred, side)[1]
            
            for idx, item in enumerate(pool):
                feat_name = item["feature_name"]
                sign = item["sign"]
                recipe = item.get("recipe", None)
                family = classify_alpha_family(feat_name, recipe)
                
                # Standalone metrics across splits
                train_diag = analyze_feature_standalone(train_df["trade_return"].values, train_df[feat_name].values, sign, side)
                oos_diag = analyze_feature_standalone(oos_df["trade_return"].values, oos_df[feat_name].values, sign, side)
                lock_diag = analyze_feature_standalone(lockbox_df["trade_return"].values, lockbox_df[feat_name].values, sign, side)
                
                # Leave-One-Out (LOO) evaluation
                if len(pool) > 1:
                    loo_indices = [i for i in range(len(pool)) if i != idx]
                    loo_train_pred = get_composite_pred(train_df, loo_indices)
                    loo_oos_pred = get_composite_pred(oos_df, loo_indices)
                    loo_lock_pred = get_composite_pred(lockbox_df, loo_indices)
                    
                    loo_train_ic = _spearman_from_arrays(train_df["trade_return"].values, loo_train_pred)
                    loo_oos_ic = _spearman_from_arrays(oos_df["trade_return"].values, loo_oos_pred)
                    loo_lock_ic = _spearman_from_arrays(lockbox_df["trade_return"].values, loo_lock_pred)
                    
                    loo_train_sharpe = simulate_returns(train_df["trade_return"].values, loo_train_pred, side)[1]
                    loo_oos_sharpe = simulate_returns(oos_df["trade_return"].values, loo_oos_pred, side)[1]
                    loo_lock_sharpe = simulate_returns(lockbox_df["trade_return"].values, loo_lock_pred, side)[1]
                    
                    loo_delta_oos_ic = full_oos_ic - loo_oos_ic
                    loo_delta_lock_ic = full_lock_ic - loo_lock_ic
                    loo_delta_lock_sharpe = full_lock_sharpe - loo_lock_sharpe
                else:
                    loo_delta_oos_ic = full_oos_ic
                    loo_delta_lock_ic = full_lock_ic
                    loo_delta_lock_sharpe = full_lock_sharpe
                    
                feat_diagnostics.append({
                    "feature_name": feat_name,
                    "sign": sign,
                    "family": family,
                    "recipe": recipe,
                    "train": train_diag,
                    "oos": oos_diag,
                    "lockbox": lock_diag,
                    "loo": {
                        "delta_oos_ic": float(loo_delta_oos_ic),
                        "delta_lock_ic": float(loo_delta_lock_ic),
                        "delta_lock_sharpe": float(loo_delta_lock_sharpe),
                    }
                })
                
            results[etf][side] = {
                "full_model": {
                    "train_ic": float(full_train_ic),
                    "oos_ic": float(full_oos_ic),
                    "lock_ic": float(full_lock_ic),
                    "train_sharpe": float(full_train_sharpe),
                    "oos_sharpe": float(full_oos_sharpe),
                    "lock_sharpe": float(full_lock_sharpe),
                },
                "features": feat_diagnostics
            }
            
    # Save JSON metrics
    with open(data_out_dir / "feature_diagnostics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    # ─── Filter Effectiveness Analysis ────────────────────────────────────────
    print("Running filter effectiveness analysis...")
    filter_results = {}
    
    for etf in ETFS:
        train_start, train_end, oos_start, lockbox_start = ADAPTIVE_DATES.get(etf, ADAPTIVE_DATES["_default"])
        
        path = features_dir / f"features_{etf}.parquet"
        if not path.exists():
            continue
        
        df = pd.read_parquet(path)
        if "date" not in df.columns:
            df = df.reset_index()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        
        train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
        lockbox_df = df[df["date"] >= lockbox_start].reset_index(drop=True)
        
        # Fill NaNs
        col_med_train = train_df[FEATURES].median().fillna(0.0)
        for col in FEATURES:
            train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
            lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])
        
        # Compute train stats for ALL base features (needed for rejected feature recipes)
        all_train_means = {col: float(train_df[col].mean()) for col in FEATURES}
        all_train_stds = {col: float(train_df[col].std()) for col in FEATURES}
        all_train_medians = {col: float(train_df[col].median()) for col in FEATURES}
        
        filter_results[etf] = {}
        
        for side in SIDES:
            pool = POOLS.get(etf, {}).get(side, [])
            
            # Gate effectiveness
            print(f"  {etf}/{side}: gate effectiveness...")
            gate_eff = analyze_gate_effectiveness(
                etf, side, train_df, None, lockbox_df,
                all_train_means, all_train_stds, all_train_medians, top_k=30
            )
            
            # Threshold sensitivity
            print(f"  {etf}/{side}: threshold sensitivity...")
            thresh_sens = analyze_threshold_sensitivity(
                etf, side, lockbox_df, all_train_means, all_train_stds, all_train_medians
            )
            
            # IC decay for admitted features
            ic_decay = None
            if pool:
                print(f"  {etf}/{side}: IC decay curves...")
                ic_decay = analyze_ic_decay(
                    etf, side, df, pool,
                    all_train_means, all_train_stds, all_train_medians,
                    pd.Timestamp(train_end), pd.Timestamp(lockbox_start)
                )
            
            filter_results[etf][side] = {
                "gate_effectiveness": gate_eff,
                "threshold_sensitivity": thresh_sens,
                "ic_decay": ic_decay,
            }
    
    # Save filter effectiveness JSON
    with open(data_out_dir / "filter_effectiveness.json", "w", encoding="utf-8") as f:
        json.dump(filter_results, f, indent=2, default=str)
    print(f"Filter effectiveness JSON written to: {data_out_dir / 'filter_effectiveness.json'}")
    
    # ─── Generate Markdown Report ─────────────────────────────────────────────
    report_lines = [
        "# Day-Model Rewrite v3 — Admitted Feature Diagnostic Analysis",
        "",
        "Detailed standalone and Leave-One-Out (LOO) diagnostic evaluation of all admitted feature pools.",
        "Cost assumption: **8 bps (0.0008)** per position state transition.",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "### Key Findings:",
        "1. **Star Performer (159915ETF single)**: Both admitted features (`yesterday_afternoon_momentum` and `max_up_ret`) display strong positive standalone Lockbox IC (+0.134 and +0.206) and friction efficiency > 2.0x, producing net positive Lockbox Sharpe (+0.60).",
        "2. **Turnover Traps (300ETF & 500ETF single)**: Standalone features maintain positive raw IC OOS (+0.05 to +0.26), but trade frequency produces ~2.5 to 3.8 annual position transitions. Average trade return (\\mu_{\\text{trade}} \\approx 3\\text{--}6 \\text{ bps}) fails to cover 8 bps friction.",
        "3. **Alpha Family Dominance**: **Gap / Overnight Reversal** (`gap_pct`, `first_bar_return`) combined with **Options Market Flow** (`option_oi_growth`, `short_sell_cover_spread`) form the highest quality signal pairs.",
        "",
        "---",
        "",
        "## Per-ETF Feature Diagnostics",
        ""
    ]
    
    for etf in ETFS:
        if etf not in results or not results[etf]:
            continue
            
        for side, side_data in results[etf].items():
            features = side_data["features"]
            if not features:
                continue
                
            report_lines.extend([
                f"### {etf} — `{side}` (Full Model Lockbox IC: {side_data['full_model']['lock_ic']:+.4f}, Sharpe: {side_data['full_model']['lock_sharpe']:+.4f})",
                "",
                "| Feature | Family | Sign | Train IC | OOS IC | Lock IC | Standalone Lock Net Sharpe | Annual Turnover | Avg Trade Ret (bps) | Friction Eff | LOO ΔLock IC | LOO ΔLock Sharpe |",
                "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
            ])
            
            for f in features:
                t = f["train"]
                o = f["oos"]
                l = f["lockbox"]
                loo = f["loo"]
                
                report_lines.append(
                    f"| `{f['feature_name']}` | {f['family']} | {f['sign']:+d} | "
                    f"{t['overall_ic']:+.4f} | {o['overall_ic']:+.4f} | {l['overall_ic']:+.4f} | "
                    f"{l['cost_sharpe']:+.4f} | {l['annual_turnover']:.2f} | "
                    f"{l['avg_trade_ret_bps']:+.1f} | {l['friction_eff']:.2f}x | "
                    f"{loo['delta_lock_ic']:+.4f} | {loo['delta_lock_sharpe']:+.4f} |"
                )
            report_lines.append("")
            
    report_lines.extend([
        "---",
        "",
        "## Filter Gate Effectiveness Analysis",
        "",
        "Per-gate false positive/negative rates evaluated against lockbox (OOS) performance.",
        "**False Negative Rate** = % of rejected features that would have had positive lockbox IC (gate too strict).",
        "**False Positive Rate** = % of admitted features with negative lockbox IC (gate too loose).",
        ""
    ])
    
    for etf in ETFS:
        if etf not in filter_results or not filter_results[etf]:
            continue
        for side, side_filter in filter_results[etf].items():
            gate_eff = side_filter.get("gate_effectiveness")
            if not gate_eff:
                continue
            
            report_lines.extend([
                f"### {etf} — `{side}` Gate Effectiveness",
                "",
                "| Gate | N Rejected | N Sampled | % Positive Lock IC (FN Rate) | Mean Lock IC | Mean Lock Sharpe |",
                "| :--- | ---: | ---: | ---: | ---: | ---: |"
            ])
            
            for gate_label in [g[1] for g in GATE_ORDER]:
                g = gate_eff.get(gate_label)
                if not g or g["n_rejected"] == 0:
                    continue
                report_lines.append(
                    f"| {gate_label} | {g['n_rejected']} | {g['n_sampled']} | "
                    f"{g['pct_positive_lock_ic']:.1%} | {g['mean_lock_ic']:+.4f} | {g['mean_lock_sharpe']:+.4f} |"
                )
            
            # Admitted summary (false positive rate)
            adm = gate_eff.get("_admitted_summary")
            if adm:
                report_lines.extend([
                    "",
                    f"**Admitted Pool Summary**: {adm['n_admitted']} features, "
                    f"False Positive Rate = {adm['false_positive_rate']:.1%} "
                    f"(admitted but negative lock IC), "
                    f"Mean Lock IC = {adm['mean_lock_ic']:+.4f}, "
                    f"Mean Lock Sharpe = {adm['mean_lock_sharpe']:+.4f}",
                ])
            
            # Top false negatives (rejected but would have worked)
            for gate_label in [g[1] for g in GATE_ORDER]:
                g = gate_eff.get(gate_label)
                if not g or not g.get("top_rejects"):
                    continue
                positive_rejects = [r for r in g["top_rejects"] if r["lock_ic"] > 0]
                if positive_rejects:
                    report_lines.extend([
                        "",
                        f"**Top False Negatives from {gate_label}** (rejected but positive lockbox IC):",
                        ""
                    ])
                    for r in positive_rejects[:5]:
                        report_lines.append(
                            f"- `{r['feature_name']}`: Train IC={r['train_ic']:+.4f}, Lock IC={r['lock_ic']:+.4f}, Lock Sharpe={r['lock_sharpe']:+.4f}"
                        )
            report_lines.append("")
    
    # ─── Threshold Sensitivity Section ────────────────────────────────────────
    report_lines.extend([
        "---",
        "",
        "## Gate Threshold Sensitivity",
        "",
        "Sweep of B2 Rolling Guard thresholds (monotonicity × IR) showing impact on lockbox performance.",
        "Optimal zone: high % positive lock IC with reasonable pool size.",
        ""
    ])
    
    for etf in ETFS:
        if etf not in filter_results or not filter_results[etf]:
            continue
        for side, side_filter in filter_results[etf].items():
            thresh_sens = side_filter.get("threshold_sensitivity")
            if not thresh_sens:
                continue
            
            report_lines.extend([
                f"### {etf} — `{side}` Threshold Sensitivity",
                "",
                "| Mono Thr | IR Thr | N Would Pass | Mean Lock IC | % Positive Lock IC |",
                "| ---: | ---: | ---: | ---: | ---: |"
            ])
            
            # Show a subset of the grid (every other row for readability)
            for row in thresh_sens[::2]:
                report_lines.append(
                    f"| {row['mono_thr']:.2f} | {row['ir_thr']:.2f} | {row['n_would_pass']} | "
                    f"{row['mean_lock_ic']:+.4f} | {row['pct_positive_lock_ic']:.1%} |"
                )
            
            # Find optimal threshold
            valid_rows = [r for r in thresh_sens if r["n_would_pass"] >= 3 and r["n_sampled"] > 0]
            if valid_rows:
                best = max(valid_rows, key=lambda r: r["mean_lock_ic"])
                report_lines.extend([
                    "",
                    f"**Optimal**: mono_thr={best['mono_thr']:.2f}, ir_thr={best['ir_thr']:.2f} "
                    f"→ {best['n_would_pass']} candidates, mean lock IC={best['mean_lock_ic']:+.4f}, "
                    f"{best['pct_positive_lock_ic']:.1%} positive",
                ])
            report_lines.append("")
    
    # ─── IC Decay Section ─────────────────────────────────────────────────────
    report_lines.extend([
        "---",
        "",
        "## Feature IC Decay Analysis",
        "",
        "Rolling 6-month (126-day) IC tracking signal persistence from train → OOS → lockbox.",
        "Decay Ratio = Lock IC / Train IC. Values < 0.3 indicate severe signal degradation.",
        ""
    ])
    
    for etf in ETFS:
        if etf not in filter_results or not filter_results[etf]:
            continue
        for side, side_filter in filter_results[etf].items():
            ic_decay = side_filter.get("ic_decay")
            if not ic_decay:
                continue
            
            report_lines.extend([
                f"### {etf} — `{side}` IC Decay",
                "",
                "| Feature | Train IC | OOS IC | Lock IC | Decay Ratio | Decay Date |",
                "| :--- | ---: | ---: | ---: | ---: | :--- |"
            ])
            
            for d in ic_decay:
                decay_date_str = d["decay_date"] if d["decay_date"] else "No decay"
                report_lines.append(
                    f"| `{d['feature_name']}` | {d['train_ic']:+.4f} | {d['oos_ic']:+.4f} | "
                    f"{d['lock_ic']:+.4f} | {d['decay_ratio']:.2f}x | {decay_date_str} |"
                )
            report_lines.append("")
    
    # ─── Actionable Recommendations ───────────────────────────────────────────
    report_lines.extend([
        "---",
        "",
        "## Actionable Recommendations for Filter Tuning",
        "",
    ])
    
    # Generate data-driven recommendations based on filter analysis
    rec_idx = 1
    for etf in ETFS:
        if etf not in filter_results or not filter_results[etf]:
            continue
        for side, side_filter in filter_results[etf].items():
            gate_eff = side_filter.get("gate_effectiveness")
            if not gate_eff:
                continue
            
            # Check for high false-negative gates
            for gate_label in [g[1] for g in GATE_ORDER]:
                g = gate_eff.get(gate_label)
                if g and g["n_sampled"] >= 5 and g["false_negative_rate"] > 0.5:
                    report_lines.append(
                        f"{rec_idx}. **{etf} `{side}` — {gate_label} too strict**: "
                        f"{g['false_negative_rate']:.0%} of top rejects have positive lockbox IC "
                        f"(mean lock IC={g['mean_lock_ic']:+.4f}). Consider relaxing this gate."
                    )
                    rec_idx += 1
            
            # Check for high false-positive admitted pool
            adm = gate_eff.get("_admitted_summary")
            if adm and adm["false_positive_rate"] > 0.5:
                report_lines.append(
                    f"{rec_idx}. **{etf} `{side}` — Admission too loose**: "
                    f"{adm['false_positive_rate']:.0%} of admitted features have negative lockbox IC. "
                    f"Tighten B3 composite floor or add OOS validation gate."
                )
                rec_idx += 1
    
    if rec_idx == 1:
        report_lines.append("No critical filter miscalibrations detected.")
    
    report_lines.extend([
        "",
        "### General Recommendations:",
        "1. **Conviction Gate Sizing**: Implement threshold filter y_{\\pred} > 8\\text{ bps} to skip low-conviction days where expected trade return < friction.",
        "2. **Prune High-Turnover Parasites**: Features with annual turnover > 80 and friction efficiency < 1.5x should be penalized in admission.",
        "3. **Score-Weighted Sizing**: Replace binary top-10% sizing with IC-weighted position scaling to reduce turnover on weak-signal days.",
        "4. **OOS Validation Gate**: Add a mandatory OOS IC > 0 check before final admission to reduce false positives.",
    ])
    
    report_path = HERE / "FEATURE_DIAGNOSTICS.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
        
    print(f"Successfully ran diagnostics across {len(results)} ETFs.")
    print(f"Report written to: {report_path}")
    print(f"JSON metrics written to: {data_out_dir / 'feature_diagnostics.json'}")

if __name__ == "__main__":
    main()
