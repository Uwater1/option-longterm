#!/usr/bin/env python3
"""
Filter Pipeline Diagnosis for Day-Model Rewrite v3.

Deep causal analysis of WHY admission gates fail. Uses lockbox as ground truth
for labeling TP/FP, but all proposed discriminators are TRAINING-ONLY signals.

Key questions answered:
  1. What training-period characteristics distinguish features that will persist
     (TP) from those that will fail OOS (FP)?
  2. How do FPs "game" each gate — what metric patterns let them through?
  3. For combo features, is failure driven by component degradation?
  4. Is training IC concentrated in specific temporal regimes (overfit to era)?

Outputs:
  - day-model-new/FILTER_DIAGNOSIS.md
  - day-model-new/data/filter_diagnosis.json
"""

import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata
from collections import defaultdict

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))

from build_features import FEATURES
from recipe_utils import compute_recipe, simulate_returns, build_ecdf_grid_float32

# Exclude 588000ETF — insufficient history for meaningful diagnosis
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

ADAPTIVE_DATES = {
    "_default": ("2014-01-01", "2022-01-01", "2022-01-01", "2024-03-01"),
}

GATE_ORDER = [
    ("REJECTED_SPLIT_HALF", "7-Year Jackknife"),
    ("REJECTED_ROLLING_GUARD", "B2 Rolling Guard"),
    ("REJECTED_TEMPORAL", "Temporal Validation Gate"),
    ("REJECTED_FDR_GATE", "BH-FDR Gate"),
    ("REJECTED_ADMISSION_FLOOR", "B3 Composite Floor"),
    ("REJECTED_HIGH_YEARLY_IC_CV", "B6 Yearly IC CV Gate"),
    ("REJECTED_UNSTABLE_COMPONENT", "B6 Unstable Component Gate"),
    ("REJECTED_STABILITY_GATE", "B6 Temporal Stability Gate"),
    ("REJECTED_QUALITY_GATE", "B6 Quality Gate"),
    ("REJECTED_REDUNDANCY", "B4 Correlation Gate"),
    ("REJECTED_ADAPTIVE_QUALITY_FLOOR", "Adaptive Quality Floor"),
    ("REJECTED_ADAPTIVE_REDUNDANCY", "Adaptive Correlation Gate"),
    ("REJECTED_ADAPTIVE_CAP_TRIM", "Adaptive Pool Size Cap"),
]


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 5 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom >= 1e-12 else 0.0


def compute_tail_ic(y: np.ndarray, pred: np.ndarray, side: str) -> float:
    n = len(pred)
    pct = 0.15 if side in ["long", "short"] else 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0
    order = np.argsort(pred, kind="quicksort")
    if side == "long":
        idx = order[-n_tail:]
    elif side == "short":
        idx = order[:n_tail]
    else:
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
    return _spearman(y[idx], pred[idx])


def compute_feature_values(df, feat_name, recipe, train_means, train_stds, train_medians, train_ecdfs=None):
    """Get raw feature values (sign-adjusted later)."""
    if recipe:
        try:
            return compute_recipe(df, recipe, train_means, train_stds, train_medians, train_ecdfs)
        except Exception:
            return None
    else:
        if feat_name not in df.columns:
            return None
        return df[feat_name].values.astype(np.float64)


def evaluate_feature(df, feat_name, recipe, sign, side, train_means, train_stds, train_medians, train_ecdfs=None):
    """Compute IC and Sharpe for a feature on a dataframe split."""
    vals = compute_feature_values(df, feat_name, recipe, train_means, train_stds, train_medians, train_ecdfs)
    if vals is None:
        return None

    pred = sign * vals
    y = df["trade_return"].values
    ic = _spearman(y, pred)
    tail_ic = compute_tail_ic(y, pred, side)
    _, sharpe, _, _, _, _ = simulate_returns(y, pred, side=side, position_mode="binary", enforce_absolute_sign=False)

    # Turnover
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
    annual_turnover = float(np.mean(transitions) * 244)

    active_mask = pos != 0
    if active_mask.sum() > 0:
        avg_trade_ret = float(np.mean(pos[active_mask] * y[active_mask]))
    else:
        avg_trade_ret = 0.0
    friction_eff = avg_trade_ret / 0.0008

    return {
        "ic": float(ic),
        "tail_ic": float(tail_ic),
        "sharpe": float(sharpe),
        "annual_turnover": annual_turnover,
        "avg_trade_ret_bps": avg_trade_ret * 10000,
        "friction_eff": friction_eff,
    }


# ─── Deep WHY Analysis Functions ──────────────────────────────────────────────


def temporal_ic_decomposition(train_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians, full_df=None):
    """Decompose training & OOS IC by year (2015-2025+) to track signal evolution.
    
    `yearly_ics` and `yearly_tail_ics` span the full timeline (including OOS years).
    Stability discriminators (ic_cv, recency_ratio, half_ratio) remain training-only.
    """
    eval_df = full_df if full_df is not None else train_df
    vals = compute_feature_values(eval_df, feat_name, recipe, train_means, train_stds, train_medians)
    if vals is None:
        return None

    pred = sign * vals
    y = eval_df["trade_return"].values
    dates = eval_df["date"].values

    # Multi-year breakdown across timeline (2015 - present)
    years = pd.DatetimeIndex(dates).year
    unique_years = [yr for yr in sorted(set(years)) if yr >= 2015]
    yearly_ics = {}
    yearly_tail_ics = {}
    for yr in unique_years:
        mask = years == yr
        if mask.sum() < 20:
            continue
        yearly_ics[int(yr)] = _spearman(y[mask], pred[mask])
        yearly_tail_ics[int(yr)] = compute_tail_ic(y[mask], pred[mask], side)

    if len(yearly_ics) < 3:
        return None

    # Compute training-period stability discriminators strictly on train_df (no look-ahead)
    train_vals = compute_feature_values(train_df, feat_name, recipe, train_means, train_stds, train_medians)
    if train_vals is not None:
        train_pred = sign * train_vals
        train_y = train_df["trade_return"].values
        train_dates = train_df["date"].values
        train_years_idx = pd.DatetimeIndex(train_dates).year
        train_unique_years = sorted(set(train_years_idx))
        
        train_yearly_ics = []
        train_yearly_tail_ics = []
        for yr in train_unique_years:
            m = train_years_idx == yr
            if m.sum() >= 20:
                train_yearly_ics.append(_spearman(train_y[m], train_pred[m]))
                train_yearly_tail_ics.append(compute_tail_ic(train_y[m], train_pred[m], side))

        mean_ic = np.mean(train_yearly_ics) if train_yearly_ics else 0.0
        std_ic = np.std(train_yearly_ics) if train_yearly_ics else 0.0
        ic_cv = std_ic / abs(mean_ic) if abs(mean_ic) > 1e-6 else 99.0
        n_negative_years = sum(1 for ic in train_yearly_ics if ic < 0)
        n_negative_tail_years = sum(1 for ic in train_yearly_tail_ics if ic < 0)

        early_ic = np.mean(train_yearly_ics[:2]) if len(train_yearly_ics) >= 2 else mean_ic
        recent_ic = np.mean(train_yearly_ics[-2:]) if len(train_yearly_ics) >= 2 else mean_ic
        recency_ratio = recent_ic / early_ic if abs(early_ic) > 1e-6 else (99.0 if recent_ic > 0 else -99.0)

        n_tr = len(train_pred)
        half_tr = n_tr // 2
        ic_first_half = _spearman(train_y[:half_tr], train_pred[:half_tr])
        ic_second_half = _spearman(train_y[half_tr:], train_pred[half_tr:])
        half_ratio = ic_second_half / ic_first_half if abs(ic_first_half) > 1e-6 else 99.0
    else:
        mean_ic, std_ic, ic_cv = 0.0, 0.0, 99.0
        n_negative_years, n_negative_tail_years = 0, 0
        early_ic, recent_ic, recency_ratio = 0.0, 0.0, 99.0
        ic_first_half, ic_second_half, half_ratio = 0.0, 0.0, 99.0

    return {
        "yearly_ics": yearly_ics,
        "yearly_tail_ics": yearly_tail_ics,
        "mean_ic": float(mean_ic),
        "std_ic": float(std_ic),
        "ic_cv": float(ic_cv),
        "n_negative_years": n_negative_years,
        "n_negative_tail_years": n_negative_tail_years,
        "n_years": len(train_unique_years) if train_vals is not None else len(yearly_ics),
        "early_ic": float(early_ic),
        "recent_ic": float(recent_ic),
        "recency_ratio": float(recency_ratio),
        "ic_first_half": float(ic_first_half),
        "ic_second_half": float(ic_second_half),
        "half_ratio": float(half_ratio),
    }


def component_stability_analysis(train_df, recipe, sign, side, train_means, train_stds, train_medians):
    """For combo features, analyze each component's standalone IC stability.
    
    Identifies if one component is the "weak link" that degrades the combo.
    """
    if not recipe:
        return None

    components = []
    for key in ["feature_a", "feature_b", "feature_c", "feature_cond"]:
        if key in recipe:
            components.append(recipe[key])

    if not components:
        return None

    y = train_df["trade_return"].values
    dates = train_df["date"].values
    years = pd.DatetimeIndex(dates).year
    unique_years = sorted(set(years))

    component_results = {}
    for comp in components:
        if comp not in train_df.columns:
            continue
        comp_vals = train_df[comp].values.astype(np.float64)
        
        # Determine component sign from its correlation with target
        comp_ic = _spearman(y, comp_vals)
        comp_sign = 1.0 if comp_ic >= 0 else -1.0
        comp_pred = comp_sign * comp_vals

        # Yearly ICs for this component
        yearly_ics = {}
        for yr in unique_years:
            mask = years == yr
            if mask.sum() < 20:
                continue
            yearly_ics[int(yr)] = _spearman(y[mask], comp_pred[mask])

        if len(yearly_ics) < 3:
            continue

        ic_values = list(yearly_ics.values())
        component_results[comp] = {
            "overall_ic": float(comp_ic),
            "yearly_ics": yearly_ics,
            "ic_std": float(np.std(ic_values)),
            "ic_cv": float(np.std(ic_values) / abs(np.mean(ic_values))) if abs(np.mean(ic_values)) > 1e-6 else 99.0,
            "n_negative_years": sum(1 for ic in ic_values if ic < 0),
            "min_ic": float(min(ic_values)),
        }

    if not component_results:
        return None

    # Identify weak link: component with highest IC instability
    weak_link = max(component_results.items(), key=lambda x: x[1]["ic_cv"])
    
    return {
        "components": component_results,
        "weak_link": weak_link[0],
        "weak_link_cv": weak_link[1]["ic_cv"],
        "weak_link_n_neg_years": weak_link[1]["n_negative_years"],
    }


def regime_concentration_analysis(train_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians):
    """Analyze if feature IC is concentrated in specific volatility regimes.
    
    Uses realized vol quintiles within training to detect regime-dependent signals.
    """
    vals = compute_feature_values(train_df, feat_name, recipe, train_means, train_stds, train_medians)
    if vals is None:
        return None

    pred = sign * vals
    y = train_df["trade_return"].values

    # Compute 20-day realized vol as regime indicator
    if "trade_return" in train_df.columns:
        vol20 = pd.Series(y).rolling(20).std().values
    else:
        return None

    # Remove NaN period
    valid = ~np.isnan(vol20)
    if valid.sum() < 100:
        return None

    vol_valid = vol20[valid]
    pred_valid = pred[valid]
    y_valid = y[valid]

    # Quintile-based regime ICs
    vol_pcts = np.percentile(vol_valid, [20, 40, 60, 80])
    regime_masks = [
        vol_valid <= vol_pcts[0],  # Low vol
        (vol_valid > vol_pcts[0]) & (vol_valid <= vol_pcts[1]),
        (vol_valid > vol_pcts[1]) & (vol_valid <= vol_pcts[2]),
        (vol_valid > vol_pcts[2]) & (vol_valid <= vol_pcts[3]),
        vol_valid > vol_pcts[3],  # High vol
    ]
    regime_labels = ["Q1_low_vol", "Q2", "Q3_mid", "Q4", "Q5_high_vol"]

    regime_ics = {}
    for label, mask in zip(regime_labels, regime_masks):
        if mask.sum() < 20:
            continue
        regime_ics[label] = _spearman(y_valid[mask], pred_valid[mask])

    if len(regime_ics) < 3:
        return None

    ic_values = list(regime_ics.values())
    
    # Concentration: what fraction of total IC comes from extreme regimes?
    total_ic = _spearman(y_valid, pred_valid)
    extreme_mask = regime_masks[0] | regime_masks[-1]
    extreme_ic = _spearman(y_valid[extreme_mask], pred_valid[extreme_mask]) if extreme_mask.sum() > 20 else 0.0

    return {
        "regime_ics": regime_ics,
        "total_ic": float(total_ic),
        "extreme_regime_ic": float(extreme_ic),
        "ic_range": float(max(ic_values) - min(ic_values)),
        "ic_std_across_regimes": float(np.std(ic_values)),
        "n_negative_regimes": sum(1 for ic in ic_values if ic < 0),
    }


def post_discovery_decay_analysis(df, train_end, feat_name, recipe, sign, side, train_means, train_stds, train_medians, train_ecdfs=None):
    """Compute IC/Sharpe in successive 1-year windows AFTER training ends.

    Reveals whether alpha decays immediately post-discovery or persists 1-2 years.
    Windows: Y1 = [train_end, train_end+1y), Y2 = [train_end+1y, train_end+2y), etc.
    Also includes a final 'remaining' window for any data beyond the last full year.

    Returns list of dicts: [{window, start, end, n_days, ic, tail_ic, sharpe}, ...]
    """
    train_end_ts = pd.Timestamp(train_end)
    post_df = df[df["date"] >= train_end_ts].reset_index(drop=True)
    if len(post_df) < 30:
        return None

    windows = []
    year_idx = 0
    while True:
        w_start = train_end_ts + pd.DateOffset(years=year_idx)
        w_end = train_end_ts + pd.DateOffset(years=year_idx + 1)
        w_df = post_df[(post_df["date"] >= w_start) & (post_df["date"] < w_end)]
        if len(w_df) < 20:
            # If we haven't started yet and no data, break
            if year_idx == 0:
                break
            # For later windows, include remaining data if >= 20 rows
            w_df = post_df[post_df["date"] >= w_start]
            if len(w_df) < 20:
                break
            result = evaluate_feature(w_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians, train_ecdfs)
            if result:
                windows.append({
                    "window": f"Y{year_idx + 1}+",
                    "start": str(w_start.date()),
                    "end": str(post_df['date'].max().date()),
                    "n_days": len(w_df),
                    **result,
                })
            break
        else:
            result = evaluate_feature(w_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians, train_ecdfs)
            if result:
                windows.append({
                    "window": f"Y{year_idx + 1}",
                    "start": str(w_start.date()),
                    "end": str(w_end.date()),
                    "n_days": len(w_df),
                    **result,
                })
        year_idx += 1
        if year_idx > 10:  # safety
            break

    if not windows:
        return None

    # Compute decay summary
    ics = [w["ic"] for w in windows]
    sharpes = [w["sharpe"] for w in windows]

    # Decay classification
    y1_ic = ics[0] if len(ics) >= 1 else 0.0
    y2_ic = ics[1] if len(ics) >= 2 else None
    last_ic = ics[-1]

    if y1_ic <= 0:
        decay_type = "immediate"  # Dead on arrival
    elif y2_ic is not None and y2_ic <= 0:
        decay_type = "fast"  # Dies within 1-2 years
    elif last_ic <= 0:
        decay_type = "gradual"  # Persists then decays
    else:
        decay_type = "persistent"  # Still alive

    # Half-life estimate: first window where IC drops below 50% of Y1
    half_life_years = None
    if y1_ic > 0.01:
        for i, ic in enumerate(ics[1:], 1):
            if ic < y1_ic * 0.5:
                half_life_years = i  # years to halve
                break

    return {
        "windows": windows,
        "decay_type": decay_type,
        "y1_ic": float(y1_ic),
        "y2_ic": float(y2_ic) if y2_ic is not None else None,
        "last_ic": float(last_ic),
        "half_life_years": half_life_years,
        "ic_trajectory": [float(ic) for ic in ics],
        "sharpe_trajectory": [float(s) for s in sharpes],
    }


def gate_mechanism_analysis(attempts, admitted_features_fp, admitted_features_tp):
    """Analyze HOW false positives game each gate vs true positives.
    
    Compares the actual gate metric distributions between FP and TP admitted features.
    """
    if not admitted_features_fp or not admitted_features_tp:
        return None

    metrics_to_compare = ["monotonicity", "ic_ir", "p_value", "max_corr", "deflated_ic", "overall_ic", "raw_ic"]
    
    results = {}
    for metric in metrics_to_compare:
        fp_vals = [f.get(metric, 0) for f in admitted_features_fp if f.get(metric) is not None]
        tp_vals = [f.get(metric) for f in admitted_features_tp if f.get(metric) is not None]
        
        if len(fp_vals) < 2 or len(tp_vals) < 2:
            continue

        results[metric] = {
            "fp_mean": float(np.mean(fp_vals)),
            "fp_std": float(np.std(fp_vals)),
            "fp_min": float(np.min(fp_vals)),
            "fp_max": float(np.max(fp_vals)),
            "tp_mean": float(np.mean(tp_vals)),
            "tp_std": float(np.std(tp_vals)),
            "tp_min": float(np.min(tp_vals)),
            "tp_max": float(np.max(tp_vals)),
            "overlap": _compute_overlap(fp_vals, tp_vals),
        }

    return results


def _compute_overlap(a_vals, b_vals):
    """Compute distribution overlap coefficient (0=no overlap, 1=identical)."""
    a_min, a_max = min(a_vals), max(a_vals)
    b_min, b_max = min(b_vals), max(b_vals)
    overlap_min = max(a_min, b_min)
    overlap_max = min(a_max, b_max)
    if overlap_max <= overlap_min:
        return 0.0
    total_range = max(a_max, b_max) - min(a_min, b_min)
    return (overlap_max - overlap_min) / total_range if total_range > 1e-12 else 1.0


def compute_training_discriminators(fp_features, tp_features):
    """Identify which TRAINING-ONLY metrics best separate FP from TP.
    
    This is the key analysis: what could the pipeline have checked at admission
    time (without OOS data) to catch the FPs?
    """
    if not fp_features or not tp_features:
        return None

    # Collect all temporal stability metrics
    discriminators = {}
    
    metric_keys = [
        "ic_cv", "n_negative_years", "recency_ratio", "half_ratio",
        "weak_link_cv", "ic_std_across_regimes", "n_negative_regimes",
    ]
    
    for key in metric_keys:
        fp_vals = [f[key] for f in fp_features if key in f and f[key] is not None and abs(f[key]) < 90]
        tp_vals = [f[key] for f in tp_features if key in f and f[key] is not None and abs(f[key]) < 90]
        
        if len(fp_vals) < 2 or len(tp_vals) < 2:
            continue
        
        fp_mean = np.mean(fp_vals)
        tp_mean = np.mean(tp_vals)
        pooled_std = np.sqrt((np.var(fp_vals) + np.var(tp_vals)) / 2)
        
        # Cohen's d: effect size (>0.8 = large, >0.5 = medium)
        cohens_d = (fp_mean - tp_mean) / pooled_std if pooled_std > 1e-12 else 0.0
        
        # Potential threshold: find value that best separates
        all_vals = [(v, "fp") for v in fp_vals] + [(v, "tp") for v in tp_vals]
        all_vals.sort(key=lambda x: x[0])
        
        best_threshold = None
        best_accuracy = 0.0
        for i in range(1, len(all_vals)):
            threshold = (all_vals[i-1][0] + all_vals[i][0]) / 2
            # Assume FP has higher values (for instability metrics)
            fp_below = sum(1 for v, t in all_vals[:i] if t == "fp")
            tp_below = sum(1 for v, t in all_vals[:i] if t == "tp")
            fp_above = sum(1 for v, t in all_vals[i:] if t == "fp")
            tp_above = sum(1 for v, t in all_vals[i:] if t == "tp")
            
            # Accuracy if we reject above threshold
            accuracy = (fp_above + tp_below) / len(all_vals)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_threshold = threshold
        
        discriminators[key] = {
            "fp_mean": float(fp_mean),
            "tp_mean": float(tp_mean),
            "fp_median": float(np.median(fp_vals)),
            "tp_median": float(np.median(tp_vals)),
            "cohens_d": float(cohens_d),
            "best_threshold": float(best_threshold) if best_threshold is not None else None,
            "best_accuracy": float(best_accuracy),
            "n_fp": len(fp_vals),
            "n_tp": len(tp_vals),
        }
    
    return discriminators


def load_attempts(etf, side, suffix=""):
    """Load mining attempts for an ETF/side."""
    path = HERE / "data" / f"mining_attempts_{etf}_{side}{suffix}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Filter Pipeline Deep Diagnosis")
    parser.add_argument("-e", "--etf", nargs="*", default=ETFS)
    parser.add_argument("-s", "--side", nargs="*", default=SIDES)
    parser.add_argument("--period-suffix", type=str, default=None, help="Period suffix for multi-period runs (e.g., _p2015_2023)")
    parser.add_argument("--train-start", type=str, default=None, help="Override training start date (YYYY-MM-DD)")
    parser.add_argument("--train-end", type=str, default=None, help="Override training end date (YYYY-MM-DD)")
    args = parser.parse_args()

    suffix = args.period_suffix or ""
    multi_period = bool(suffix)

    # In multi-period mode, override dates and use OOS as ground truth
    if multi_period and args.train_start and args.train_end:
        override_dates = (args.train_start, args.train_end, args.train_end, args.train_end)
    else:
        override_dates = None

    features_dir = REPO_ROOT / "day-model" / "data"
    data_out_dir = HERE / "data"
    data_out_dir.mkdir(parents=True, exist_ok=True)

    all_results = {}

    for etf in args.etf:
        if etf not in ETFS:
            continue
        if override_dates:
            train_start, train_end, oos_start, lockbox_start = override_dates
        else:
            train_start, train_end, oos_start, lockbox_start = ADAPTIVE_DATES["_default"]

        path = features_dir / f"features_{etf}.parquet"
        if not path.exists():
            print(f"Skipping {etf}: dataset not found")
            continue

        print(f"\n{'='*80}")
        print(f"Processing {etf}")
        print(f"{'='*80}")

        df = pd.read_parquet(path)
        if "date" not in df.columns:
            df = df.reset_index()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
        # Full OOS (train_end onwards, e.g. 2022-2026) as ground truth for Lock IC/Sharpe
        lockbox_df = df[df["date"] >= train_end].reset_index(drop=True)

        # Fill NaNs
        col_med_train = train_df[FEATURES].median().fillna(0.0)
        for col in FEATURES:
            train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
            lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])

        # Pre-compute train stats
        train_means = {col: float(train_df[col].mean()) for col in FEATURES}
        train_stds = {col: float(train_df[col].std()) for col in FEATURES}
        train_medians = {col: float(train_df[col].median()) for col in FEATURES}
        train_ecdfs = {col: build_ecdf_grid_float32(train_df[col].values.astype(np.float32), n_knots=128) for col in FEATURES}

        all_results[etf] = {}

        for side in args.side:
            print(f"\n  {etf}/{side}:")

            attempts = load_attempts(etf, side, suffix=suffix)
            if not attempts:
                print(f"    No mining attempts found")
                continue

            admitted = [a for a in attempts if a.get("verdict", "").startswith("ADMITTED")]
            if not admitted:
                print(f"    No admitted features")
                continue

            print(f"    {len(attempts)} attempts, {len(admitted)} admitted")

            # ─── Phase 1: Label each admitted feature as TP / Median / FP using lockbox ───
            # TP:      Lock IC > 0 AND Sharpe > 0  (profitable standalone)
            # Median:  Lock IC > 0 AND Sharpe ≤ 0  (usable signal, contributes to ensemble)
            # FP:      Lock IC ≤ 0                  (no predictive power, harmful)
            fp_list = []
            median_list = []
            tp_list = []

            for item in admitted:
                feat_name = item["feature_name"]
                sign = item.get("sign", 1)
                recipe = item.get("recipe", None)

                lock_result = evaluate_feature(lockbox_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians, train_ecdfs)
                if lock_result is None:
                    continue

                entry = {
                    "feature_name": feat_name,
                    "sign": sign,
                    "recipe": recipe,
                    "lock_ic": lock_result["ic"],
                    "lock_sharpe": lock_result["sharpe"],
                    "lock_friction_eff": lock_result["friction_eff"],
                    # Gate metrics from admission
                    "overall_ic": item.get("overall_ic", 0),
                    "raw_ic": item.get("raw_ic", 0),
                    "monotonicity": item.get("monotonicity", 0),
                    "ic_ir": item.get("ic_ir", 0),
                    "p_value": item.get("p_value", 1.0),
                    "max_corr": item.get("max_corr", 0),
                    "deflated_ic": item.get("deflated_ic", 0),
                }

                if lock_result["ic"] <= 0:
                    entry["tier"] = "FP"
                    fp_list.append(entry)
                elif lock_result["sharpe"] <= 0:
                    entry["tier"] = "Median"
                    median_list.append(entry)
                else:
                    entry["tier"] = "TP"
                    tp_list.append(entry)

            print(f"    FP: {len(fp_list)}, Median: {len(median_list)}, TP: {len(tp_list)}")

            all_features_for_analysis = fp_list + median_list + tp_list
            if not all_features_for_analysis:
                all_results[etf][side] = {"n_fp": 0, "n_median": 0, "n_tp": 0}
                continue

            # ─── Phase 2: Deep WHY analysis on each FP, Median, and TP ─────────
            print(f"    Running temporal decomposition...")
            for entry in all_features_for_analysis:
                temporal = temporal_ic_decomposition(
                    train_df, entry["feature_name"], entry["recipe"],
                    entry["sign"], side, train_means, train_stds, train_medians,
                    full_df=df
                )
                if temporal:
                    entry.update(temporal)

            print(f"    Running component stability...")
            for entry in all_features_for_analysis:
                comp = component_stability_analysis(
                    train_df, entry["recipe"], entry["sign"], side,
                    train_means, train_stds, train_medians
                )
                if comp:
                    entry["weak_link"] = comp["weak_link"]
                    entry["weak_link_cv"] = comp["weak_link_cv"]
                    entry["weak_link_n_neg_years"] = comp["weak_link_n_neg_years"]
                    entry["component_details"] = comp["components"]

            print(f"    Running regime concentration...")
            for entry in all_features_for_analysis:
                regime = regime_concentration_analysis(
                    train_df, entry["feature_name"], entry["recipe"],
                    entry["sign"], side, train_means, train_stds, train_medians
                )
                if regime:
                    entry["ic_std_across_regimes"] = regime["ic_std_across_regimes"]
                    entry["n_negative_regimes"] = regime["n_negative_regimes"]
                    entry["regime_ics"] = regime["regime_ics"]

            print(f"    Running post-discovery decay analysis...")
            for entry in all_features_for_analysis:
                decay = post_discovery_decay_analysis(
                    df, train_end, entry["feature_name"], entry["recipe"],
                    entry["sign"], side, train_means, train_stds, train_medians, train_ecdfs
                )
                if decay:
                    entry["decay"] = decay

            # ─── Phase 3: Compute training-only discriminators ──────────────────
            print(f"    Computing training discriminators...")
            discriminators = compute_training_discriminators(fp_list, tp_list)
            disc_fp_vs_median = compute_training_discriminators(fp_list, median_list)
            disc_median_vs_tp = compute_training_discriminators(median_list, tp_list)

            # ─── Phase 4: Gate mechanism analysis ───────────────────────────────
            gate_mech = gate_mechanism_analysis(attempts, fp_list, tp_list)

            # ─── Phase 5: False rejection sampling (top rejects per gate) ───────
            print(f"    Analyzing false rejections...")
            fn_analysis = {}
            for gate_verdict, gate_label in GATE_ORDER:
                rejects = [a for a in attempts if a.get("verdict") == gate_verdict]
                if not rejects:
                    continue
                # Take top-20 by training IC
                rejects_sorted = sorted(rejects, key=lambda x: x.get("overall_ic", 0), reverse=True)[:20]
                fn_entries = []
                for item in rejects_sorted:
                    lock_result = evaluate_feature(
                        lockbox_df, item["feature_name"], item.get("recipe"),
                        item.get("sign", 1), side, train_means, train_stds, train_medians
                    )
                    if lock_result and lock_result["ic"] > 0 and lock_result["sharpe"] > 0:
                        fn_entries.append({
                            "feature_name": item["feature_name"],
                            "train_ic": item.get("overall_ic", 0),
                            "lock_ic": lock_result["ic"],
                            "lock_sharpe": lock_result["sharpe"],
                        })
                if fn_entries:
                    fn_analysis[gate_label] = {
                        "n_top_rejects": len(rejects_sorted),
                        "n_false_negatives": len(fn_entries),
                        "fn_rate": len(fn_entries) / len(rejects_sorted),
                        "top_fn": sorted(fn_entries, key=lambda x: -x["lock_sharpe"])[:5],
                    }

            # ─── Phase 5b: Full-population gate confusion matrix ─────────────────
            # Evaluate ALL rejects per gate (sampled if too many) on lockbox to compute
            # precision (FP catch rate) and collateral (TP kill rate).
            print(f"    Computing per-gate confusion matrices...")
            gate_confusion = {}
            MAX_EVAL_PER_GATE = 80  # cap evaluations per gate for speed
            for gate_verdict, gate_label in GATE_ORDER:
                rejects = [a for a in attempts if a.get("verdict") == gate_verdict]
                if not rejects:
                    continue
                # Sample if too many: stratified by training IC (top/mid/bottom)
                if len(rejects) > MAX_EVAL_PER_GATE:
                    rejects_sorted_all = sorted(rejects, key=lambda x: x.get("overall_ic", 0), reverse=True)
                    n_third = MAX_EVAL_PER_GATE // 3
                    sampled = (
                        rejects_sorted_all[:n_third]
                        + rejects_sorted_all[len(rejects_sorted_all)//2 - n_third//2 : len(rejects_sorted_all)//2 + n_third//2]
                        + rejects_sorted_all[-n_third:]
                    )
                else:
                    sampled = rejects
                
                n_fp_caught = 0  # rejected AND lockbox IC <= 0 (correct rejection)
                n_median_caught = 0  # rejected AND lockbox IC > 0, Sharpe <= 0
                n_tp_killed = 0  # rejected AND lockbox IC > 0, Sharpe > 0 (false negative)
                n_evaluated = 0
                tp_killed_list = []
                fp_caught_list = []
                
                for item in sampled:
                    lock_result = evaluate_feature(
                        lockbox_df, item["feature_name"], item.get("recipe"),
                        item.get("sign", 1), side, train_means, train_stds, train_medians
                    )
                    if lock_result is None:
                        continue
                    n_evaluated += 1
                    if lock_result["ic"] <= 0:
                        n_fp_caught += 1
                        fp_caught_list.append({
                            "feature_name": item["feature_name"],
                            "train_ic": item.get("overall_ic", 0),
                            "lock_ic": lock_result["ic"],
                            "lock_sharpe": lock_result["sharpe"],
                        })
                    elif lock_result["sharpe"] > 0:
                        n_tp_killed += 1
                        tp_killed_list.append({
                            "feature_name": item["feature_name"],
                            "train_ic": item.get("overall_ic", 0),
                            "lock_ic": lock_result["ic"],
                            "lock_sharpe": lock_result["sharpe"],
                        })
                    else:
                        n_median_caught += 1
                
                if n_evaluated > 0:
                    gate_confusion[gate_label] = {
                        "n_total_rejects": len(rejects),
                        "n_evaluated": n_evaluated,
                        "n_fp_caught": n_fp_caught,
                        "n_median_caught": n_median_caught,
                        "n_tp_killed": n_tp_killed,
                        "precision": n_fp_caught / n_evaluated,  # % correctly rejected
                        "collateral_rate": n_tp_killed / n_evaluated,  # % TP killed
                        "top_tp_killed": sorted(tp_killed_list, key=lambda x: -x["lock_sharpe"])[:5],
                        "top_fp_caught": sorted(fp_caught_list, key=lambda x: x["lock_ic"])[:5],
                    }

            # ─── Phase 5c: Temporal gate sub-condition analysis ──────────────────
            # For the temporal gate specifically, break down by rejection reason.
            temporal_sub_analysis = None
            temporal_rejects = [a for a in attempts if a.get("verdict") == "REJECTED_TEMPORAL"]
            if temporal_rejects:
                print(f"    Analyzing temporal gate sub-conditions ({len(temporal_rejects)} rejects)...")
                # Split by condition
                neg_recent = [a for a in temporal_rejects if a.get("recent_ic", 0) <= 0]
                high_ratio = [a for a in temporal_rejects if a.get("recent_ic", 0) > 0 and a.get("recency_ratio", 99) >= 2.5]
                
                def _eval_subgroup(group, label, max_n=50):
                    """Evaluate a subgroup of temporal rejects on lockbox."""
                    if not group:
                        return {"label": label, "n": 0}
                    # Sample top by training IC
                    sampled = sorted(group, key=lambda x: x.get("overall_ic", 0), reverse=True)[:max_n]
                    n_fp = 0
                    n_tp = 0
                    n_med = 0
                    n_eval = 0
                    tp_list = []
                    for item in sampled:
                        lr = evaluate_feature(
                            lockbox_df, item["feature_name"], item.get("recipe"),
                            item.get("sign", 1), side, train_means, train_stds, train_medians
                        )
                        if lr is None:
                            continue
                        n_eval += 1
                        if lr["ic"] <= 0:
                            n_fp += 1
                        elif lr["sharpe"] > 0:
                            n_tp += 1
                            tp_list.append({"feature_name": item["feature_name"], "train_ic": item.get("overall_ic", 0), "lock_ic": lr["ic"], "lock_sharpe": lr["sharpe"]})
                        else:
                            n_med += 1
                    return {
                        "label": label,
                        "n": len(group),
                        "n_evaluated": n_eval,
                        "n_fp_caught": n_fp,
                        "n_tp_killed": n_tp,
                        "n_median": n_med,
                        "fp_precision": n_fp / n_eval if n_eval > 0 else 0,
                        "tp_collateral": n_tp / n_eval if n_eval > 0 else 0,
                        "top_tp_killed": sorted(tp_list, key=lambda x: -x["lock_sharpe"])[:5],
                    }
                
                temporal_sub_analysis = {
                    "total_rejects": len(temporal_rejects),
                    "neg_recent_ic": _eval_subgroup(neg_recent, "recent_ic <= 0 (decayed)"),
                    "high_ratio": _eval_subgroup(high_ratio, "recency_ratio >= 2.5 (late-concentrated)"),
                }

            all_results[etf][side] = {
                "n_fp": len(fp_list),
                "n_median": len(median_list),
                "n_tp": len(tp_list),
                "fp_rate": len(fp_list) / len(all_features_for_analysis) if all_features_for_analysis else 0,
                "fp_features": fp_list,
                "median_features": median_list,
                "tp_features": tp_list,
                "discriminators": discriminators,
                "disc_fp_vs_median": disc_fp_vs_median,
                "disc_median_vs_tp": disc_median_vs_tp,
                "gate_mechanism": gate_mech,
                "fn_analysis": fn_analysis,
                "gate_confusion": gate_confusion,
                "temporal_sub_analysis": temporal_sub_analysis,
            }

    # Compute OOS span for report caveats
    oos_years = None
    if override_dates:
        _oos_start = override_dates[2]
    else:
        _oos_start = ADAPTIVE_DATES["_default"][2]
    try:
        _oos_start_ts = pd.Timestamp(_oos_start)
        _data_end = pd.Timestamp.now().normalize()
        # Use actual data max if available
        if all_results:
            _any_side = next(iter(next(iter(all_results.values())).values()), {})
            _any_feats = _any_side.get("tp_features") or _any_side.get("median_features") or _any_side.get("fp_features") or []
            if _any_feats and _any_feats[0].get("decay") and _any_feats[0]["decay"].get("windows"):
                _last_w = _any_feats[0]["decay"]["windows"][-1]
                _data_end = pd.Timestamp(_last_w["end"])
        oos_years = (_data_end - _oos_start_ts).days / 365.25
    except Exception:
        pass

    # Save JSON
    json_path = data_out_dir / f"filter_diagnosis{suffix}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nJSON written to: {json_path}")

    # Generate report
    generate_report(all_results, suffix=suffix, oos_years=oos_years)


def _load_cluster_info(etf, side, suffix, admitted_features=None):
    cluster_path = HERE / "data" / f"cluster_assignments_{etf}_{side}{suffix}.json"
    cdata = None
    try:
        with open(cluster_path, "r", encoding="utf-8") as f:
            cdata = json.load(f)
    except Exception:
        pass
    if not cdata or "clusters" not in cdata:
        return {"n_clusters": "-", "sizes_str": "-", "avg_sil_str": "-"}
    clusters_dict = cdata["clusters"]
    # Filter to only admitted features if provided
    if admitted_features is not None:
        admitted_set = set(admitted_features)
        filtered_clusters = {
            k: [f for f in members if f in admitted_set]
            for k, members in clusters_dict.items()
        }
        # Keep only clusters with at least one admitted feature
        filtered_clusters = {k: v for k, v in filtered_clusters.items() if v}
        n_clusters = len(filtered_clusters)
        sizes = sorted([len(m) for m in filtered_clusters.values()], reverse=True)
    else:
        n_clusters = cdata.get("n_clusters", len(clusters_dict))
        sizes = sorted([len(m) for m in clusters_dict.values()], reverse=True)
    if len(sizes) <= 15:
        sizes_str = str(sizes)
    else:
        sizes_str = f"[{', '.join(map(str, sizes[:12]))}, ... ({len(sizes)} clusters)]"
    avg_sil = cdata.get("avg_silhouette", None)
    avg_sil_str = f"{avg_sil:.4f}" if avg_sil is not None else "N/A"
    return {
        "n_clusters": n_clusters,
        "sizes_str": sizes_str,
        "avg_sil_str": avg_sil_str,
        "sizes_raw": sizes,
    }


def generate_report(results, suffix="", oos_years=None):
    """Generate FILTER_DIAGNOSIS.md with deep causal analysis."""
    lines = [
        "# Filter Pipeline Deep Diagnosis",
        "",
        "**Purpose**: Understand WHY admission gates fail, using only training-period signals.",
        "Lockbox is used solely for labeling TP/FP — all proposed fixes are training-only.",
        "",
        "---",
        "",
    ]

    # ─── Section 1: Summary ───────────────────────────────────────────────────
    lines.extend(["## 1. FP / Median / TP Summary", ""])
    lines.extend([
        "**TP** = Lock IC > 0 AND Sharpe > 0 (profitable standalone).  ",
        "**Median** = Lock IC > 0, Sharpe ≤ 0 (usable signal, contributes to IC-weighted ensemble).  ",
        "**FP** = Lock IC ≤ 0 (no predictive power, harmful).",
        "",
        "**Decay multiplier** (assumes annual retraining): persistent=1.0, gradual=0.75, fast=0.25, immediate=0.0.  ",
        "**Prod Score** = mean(tier_score × decay_mult) where TP=1.0, Median=0.5, FP=0.0.",
        "",
    ])
    if oos_years is not None and oos_years < 2.0:
        lines.append(f"> **Caveat**: Lockbox spans ~{oos_years:.1f}y. Sharpe-based TP/Median split has high variance at this horizon; some Median features may flip to TP with more data.")
        lines.append("")
    lines.extend([
        "| ETF | Side | Admitted | Clusters | Cluster Sizes | Avg Sil | FP | Median | TP | FP Rate | Prod Score |",
        "| :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    # Decay multipliers (production retraining context)
    DECAY_MULT = {"persistent": 1.0, "gradual": 0.75, "fast": 0.25, "immediate": 0.0}
    TIER_SCORE = {"TP": 1.0, "Median": 0.5, "FP": 0.0}

    for etf, sides in results.items():
        for side, data in sides.items():
            n_fp = data.get("n_fp", 0)
            n_median = data.get("n_median", 0)
            n_tp = data.get("n_tp", 0)
            total = n_fp + n_median + n_tp
            if total == 0:
                continue
            fp_rate = n_fp / total

            # Production score: per-feature tier_score * decay_multiplier
            all_feats = data.get("fp_features", []) + data.get("median_features", []) + data.get("tp_features", [])
            prod_scores = []
            for f in all_feats:
                tier_s = TIER_SCORE.get(f.get("tier", "FP"), 0.0)
                decay_type = f.get("decay", {}).get("decay_type", "gradual") if f.get("decay") else "gradual"
                decay_m = DECAY_MULT.get(decay_type, 0.5)
                prod_scores.append(tier_s * decay_m)
            prod_score = sum(prod_scores) / len(prod_scores) if prod_scores else 0.0

            admitted_names = [f.get("feature_name", "") for f in all_feats]
            cinfo = _load_cluster_info(etf, side, suffix, admitted_features=admitted_names)
            lines.append(
                f"| {etf} | {side} | {total} | {cinfo['n_clusters']} | `{cinfo['sizes_str']}` | {cinfo['avg_sil_str']} | "
                f"{n_fp} | {n_median} | {n_tp} | {fp_rate:.0%} | {prod_score:.2f} |"
            )
    lines.append("")

    # ─── Section 2: Training-Only Discriminators ──────────────────────────────
    lines.extend([
        "---",
        "",
        "## 2. Training-Only Discriminators (KEY SECTION)",
        "",
        "Metrics computable at admission time that separate future FP from future TP.",
        "**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.",
        "",
        "Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            disc = data.get("discriminators")
            if not disc:
                continue

            lines.extend([
                f"### {etf} — `{side}` (FP={data['n_fp']}, TP={data['n_tp']})",
                "",
                "| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ])
            for key, vals in sorted(disc.items(), key=lambda x: -abs(x[1]["cohens_d"])):
                thr_str = f"{vals['best_threshold']:.3f}" if vals['best_threshold'] is not None else "N/A"
                lines.append(
                    f"| {key} | {vals['fp_mean']:.3f} | {vals['tp_mean']:.3f} | "
                    f"{vals['fp_median']:.3f} | {vals['tp_median']:.3f} | "
                    f"{vals['cohens_d']:+.2f} | {thr_str} | {vals['best_accuracy']:.0%} |"
                )
            lines.append("")

    # ─── Section 3: FP Temporal Decomposition ─────────────────────────────────
    lines.extend([
        "---",
        "",
        "## 3. False Positive Temporal Decomposition",
        "",
        "Per-year training IC for each FP feature. Look for:",
        "- IC concentrated in 1-2 years (era overfit)",
        "- Recent IC much lower than early IC (decaying signal)",
        "- High year-to-year variance (unstable signal)",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            fp_features = data.get("fp_features", [])
            if not fp_features:
                continue

            lines.extend([f"### {etf} — `{side}` False Positives", ""])

            for f in sorted(fp_features, key=lambda x: x["lock_sharpe"]):
                yearly = f.get("yearly_ics", {})
                yearly_tail = f.get("yearly_tail_ics", {})
                if not yearly:
                    continue
                years_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly.items()))
                years_tail_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly_tail.items())) if yearly_tail else ""
                lines.extend([
                    f"**`{f['feature_name']}`** (Lock IC={f['lock_ic']:+.4f}, Sharpe={f['lock_sharpe']:+.4f})",
                    f"- Admission: Train IC={f.get('overall_ic', 0):+.4f}, Deflated={f.get('deflated_ic', 0):+.4f}, "
                    f"IR={f.get('ic_ir', 0):.2f}, Mono={f.get('monotonicity', 0):.2f}, p={f.get('p_value', 1):.4f}, MaxCorr={f.get('max_corr', 0):.2f}",
                    f"- Yearly Linear ICs: {years_str}",
                ])
                if years_tail_str:
                    lines.append(f"- Yearly Tail ICs:   {years_tail_str}")
                lines.extend([
                    f"- IC CV={f.get('ic_cv', 0):.2f}, Neg years (linear/tail)={f.get('n_negative_years', 0)}/{f.get('n_negative_tail_years', 0)} of {f.get('n_years', 0)}, "
                    f"Half ratio={f.get('half_ratio', 0):.2f}, Recency ratio={f.get('recency_ratio', 0):.2f}",
                    f"- Early IC={f.get('early_ic', 0):+.4f}, Recent IC={f.get('recent_ic', 0):+.4f}, "
                    f"1st-half IC={f.get('ic_first_half', 0):+.4f}, 2nd-half IC={f.get('ic_second_half', 0):+.4f}, "
                    f"Neg regimes={f.get('n_negative_regimes', 0)}/5",
                ])
                if f.get("weak_link"):
                    lines.append(f"- Weak component: `{f['weak_link']}` (CV={f.get('weak_link_cv', 0):.2f}, neg years={f.get('weak_link_n_neg_years', 0)})")
                if f.get("regime_ics"):
                    regime_str = ", ".join(f"{k}={v:+.3f}" for k, v in f["regime_ics"].items())
                    lines.append(f"- Regime ICs: {regime_str}")
                lines.append("")

    # ─── Section 3b: Median Temporal Decomposition ─────────────────────────────
    lines.extend([
        "---",
        "",
        "## 3b. Median (Usable) Temporal Decomposition",
        "",
        "Features with positive lockbox IC but non-positive Sharpe.",
        "These contribute signal to IC-weighted ensembles but aren't profitable standalone.",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            median_features = data.get("median_features", [])
            if not median_features:
                continue

            lines.extend([f"### {etf} — `{side}` Median Features", ""])

            for f in sorted(median_features, key=lambda x: -x["lock_ic"]):
                yearly = f.get("yearly_ics", {})
                yearly_tail = f.get("yearly_tail_ics", {})
                if not yearly:
                    continue
                years_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly.items()))
                years_tail_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly_tail.items())) if yearly_tail else ""
                lines.extend([
                    f"**`{f['feature_name']}`** (Lock IC={f['lock_ic']:+.4f}, Sharpe={f['lock_sharpe']:+.4f})",
                    f"- Admission: Train IC={f.get('overall_ic', 0):+.4f}, Deflated={f.get('deflated_ic', 0):+.4f}, "
                    f"IR={f.get('ic_ir', 0):.2f}, Mono={f.get('monotonicity', 0):.2f}, p={f.get('p_value', 1):.4f}, MaxCorr={f.get('max_corr', 0):.2f}",
                    f"- Yearly Linear ICs: {years_str}",
                ])
                if years_tail_str:
                    lines.append(f"- Yearly Tail ICs:   {years_tail_str}")
                lines.extend([
                    f"- IC CV={f.get('ic_cv', 0):.2f}, Neg years (linear/tail)={f.get('n_negative_years', 0)}/{f.get('n_negative_tail_years', 0)} of {f.get('n_years', 0)}, "
                    f"Half ratio={f.get('half_ratio', 0):.2f}, Recency ratio={f.get('recency_ratio', 0):.2f}",
                    f"- Early IC={f.get('early_ic', 0):+.4f}, Recent IC={f.get('recent_ic', 0):+.4f}, "
                    f"1st-half IC={f.get('ic_first_half', 0):+.4f}, 2nd-half IC={f.get('ic_second_half', 0):+.4f}, "
                    f"Neg regimes={f.get('n_negative_regimes', 0)}/5",
                ])
                if f.get("weak_link"):
                    lines.append(f"- Weak component: `{f['weak_link']}` (CV={f.get('weak_link_cv', 0):.2f})")
                if f.get("regime_ics"):
                    regime_str = ", ".join(f"{k}={v:+.3f}" for k, v in f["regime_ics"].items())
                    lines.append(f"- Regime ICs: {regime_str}")
                lines.append("")

    # ─── Section 4: TP Temporal Decomposition (for comparison) ────────────────
    lines.extend([
        "---",
        "",
        "## 4. True Positive Temporal Decomposition (Comparison)",
        "",
        "What stable, persistent features look like in training.",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            tp_features = data.get("tp_features", [])
            if not tp_features:
                continue

            lines.extend([f"### {etf} — `{side}` True Positives", ""])

            for f in sorted(tp_features, key=lambda x: -x["lock_sharpe"]):
                yearly = f.get("yearly_ics", {})
                yearly_tail = f.get("yearly_tail_ics", {})
                if not yearly:
                    continue
                years_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly.items()))
                years_tail_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly_tail.items())) if yearly_tail else ""
                lines.extend([
                    f"**`{f['feature_name']}`** (Lock IC={f['lock_ic']:+.4f}, Sharpe={f['lock_sharpe']:+.4f})",
                    f"- Admission: Train IC={f.get('overall_ic', 0):+.4f}, Deflated={f.get('deflated_ic', 0):+.4f}, "
                    f"IR={f.get('ic_ir', 0):.2f}, Mono={f.get('monotonicity', 0):.2f}, p={f.get('p_value', 1):.4f}, MaxCorr={f.get('max_corr', 0):.2f}",
                    f"- Yearly Linear ICs: {years_str}",
                ])
                if years_tail_str:
                    lines.append(f"- Yearly Tail ICs:   {years_tail_str}")
                lines.extend([
                    f"- IC CV={f.get('ic_cv', 0):.2f}, Neg years (linear/tail)={f.get('n_negative_years', 0)}/{f.get('n_negative_tail_years', 0)} of {f.get('n_years', 0)}, "
                    f"Half ratio={f.get('half_ratio', 0):.2f}, Recency ratio={f.get('recency_ratio', 0):.2f}",
                    f"- Early IC={f.get('early_ic', 0):+.4f}, Recent IC={f.get('recent_ic', 0):+.4f}, "
                    f"1st-half IC={f.get('ic_first_half', 0):+.4f}, 2nd-half IC={f.get('ic_second_half', 0):+.4f}, "
                    f"Neg regimes={f.get('n_negative_regimes', 0)}/5",
                ])
                if f.get("weak_link"):
                    lines.append(f"- Weak component: `{f['weak_link']}` (CV={f.get('weak_link_cv', 0):.2f})")
                if f.get("regime_ics"):
                    regime_str = ", ".join(f"{k}={v:+.3f}" for k, v in f["regime_ics"].items())
                    lines.append(f"- Regime ICs: {regime_str}")
                lines.append("")

    # ─── Section 4b: Post-Discovery Decay Curve ────────────────────────────────
    lines.extend([
        "---",
        "",
        "## 4b. Post-Discovery IC Decay Curve",
        "",
        "Year-by-year OOS IC after training ends. Reveals whether alpha decays",
        "immediately (overfit), within 1-2 years (short-lived alpha), or persists.",
        "",
        "Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            all_features = data.get("fp_features", []) + data.get("median_features", []) + data.get("tp_features", [])
            features_with_decay = [f for f in all_features if f.get("decay")]
            if not features_with_decay:
                continue

            lines.extend([f"### {etf} — `{side}`", ""])

            # Summary table
            y2_hdr = "Y2+ IC (partial)" if (oos_years is not None and oos_years < 2.0) else "Y2 IC"
            lines.extend([
                f"| Feature | Tier | Decay | Y1 IC | {y2_hdr} | Y3+ IC | Half-life |",
                "| :--- | :--- | :--- | ---: | ---: | ---: | ---: |",
            ])
            for f in sorted(features_with_decay, key=lambda x: x["decay"]["y1_ic"], reverse=True):
                d = f["decay"]
                label = f.get("tier", "?")
                y1 = f"{d['y1_ic']:+.4f}"
                y2 = f"{d['y2_ic']:+.4f}" if d['y2_ic'] is not None else "N/A"
                last = f"{d['last_ic']:+.4f}"
                hl = f"{d['half_life_years']}y" if d['half_life_years'] is not None else "∞"
                lines.append(f"| `{f['feature_name']}` | {label} | {d['decay_type']} | {y1} | {y2} | {last} | {hl} |")
            lines.append("")

            # Decay type distribution
            decay_types = [f["decay"]["decay_type"] for f in features_with_decay]
            n_imm = decay_types.count("immediate")
            n_fast = decay_types.count("fast")
            n_grad = decay_types.count("gradual")
            n_pers = decay_types.count("persistent")
            lines.append(f"**Decay distribution**: immediate={n_imm}, fast(1-2y)={n_fast}, gradual={n_grad}, persistent={n_pers}")
            lines.append("")

            # Detailed trajectories for FP features
            fp_with_decay = [f for f in data.get("fp_features", []) if f.get("decay")]
            if fp_with_decay:
                lines.append("**FP decay trajectories:**")
                lines.append("")
                for f in sorted(fp_with_decay, key=lambda x: x["decay"]["y1_ic"]):
                    d = f["decay"]
                    traj_str = " → ".join(
                        f"{w['window']}:{w['ic']:+.3f}" for w in d["windows"]
                    )
                    lines.append(f"- `{f['feature_name']}`: {traj_str}")
                lines.append("")

    # ─── Section 5: Gate Mechanism Failure ────────────────────────────────────
    lines.extend([
        "---",
        "",
        "## 5. Gate Mechanism Failure Analysis",
        "",
        "How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            gate_mech = data.get("gate_mechanism")
            if not gate_mech:
                continue

            lines.extend([
                f"### {etf} — `{side}`",
                "",
                "| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |",
                "| :--- | :--- | :--- | ---: | :--- |",
            ])
            for metric, vals in gate_mech.items():
                fp_str = f"{vals['fp_mean']:.3f}±{vals['fp_std']:.3f}"
                tp_str = f"{vals['tp_mean']:.3f}±{vals['tp_std']:.3f}"
                overlap = vals["overlap"]
                verdict = "USELESS" if overlap > 0.8 else ("WEAK" if overlap > 0.5 else "USEFUL")
                lines.append(f"| {metric} | {fp_str} | {tp_str} | {overlap:.0%} | {verdict} |")
            lines.append("")

    # ─── Section 6: False Rejection Analysis ──────────────────────────────────
    lines.extend([
        "---",
        "",
        "## 6. False Rejection (Missed Opportunities)",
        "",
        "Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            fn = data.get("fn_analysis", {})
            if not fn:
                continue

            lines.extend([f"### {etf} — `{side}`", ""])
            for gate_label, gate_data in fn.items():
                lines.extend([
                    f"**{gate_label}**: {gate_data['n_false_negatives']}/{gate_data['n_top_rejects']} "
                    f"top rejects are profitable ({gate_data['fn_rate']:.0%})",
                    "",
                ])
                for item in gate_data["top_fn"][:3]:
                    lines.append(
                        f"- `{item['feature_name']}`: Train IC={item['train_ic']:+.4f}, "
                        f"Lock IC={item['lock_ic']:+.4f}, Sharpe={item['lock_sharpe']:+.4f}"
                    )
                lines.append("")

    # ─── Section 6b: Per-Gate Confusion Matrix ─────────────────────────────
    lines.extend([
        "---",
        "",
        "## 6b. Per-Gate Confusion Matrix (Full Population)",
        "",
        "Stratified sample of ALL rejects per gate evaluated on lockbox.",
        "**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.",
        "**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            gc = data.get("gate_confusion", {})
            if not gc:
                continue

            lines.extend([
                f"### {etf} — `{side}`",
                "",
                "| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ])
            for gate_label, g in gc.items():
                lines.append(
                    f"| {gate_label} | {g['n_total_rejects']} | {g['n_evaluated']} | "
                    f"{g['n_fp_caught']} | {g['n_median_caught']} | {g['n_tp_killed']} | "
                    f"{g['precision']:.0%} | {g['collateral_rate']:.0%} |"
                )
            lines.append("")

            # Show top TP killed for gates with high collateral
            for gate_label, g in gc.items():
                if g["collateral_rate"] > 0.20 and g["top_tp_killed"]:
                    lines.append(f"**{gate_label}** — top TP casualties:")
                    for item in g["top_tp_killed"][:3]:
                        lines.append(
                            f"- `{item['feature_name']}`: Train IC={item['train_ic']:+.4f}, "
                            f"Lock IC={item['lock_ic']:+.4f}, Sharpe={item['lock_sharpe']:+.4f}"
                        )
                    lines.append("")

    # ─── Section 6c: Temporal Gate Sub-Condition Analysis ───────────────────
    lines.extend([
        "---",
        "",
        "## 6c. Temporal Gate Sub-Condition Analysis",
        "",
        "Breakdown of temporal gate rejects by condition:",
        "- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)",
        "- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            tsa = data.get("temporal_sub_analysis")
            if not tsa:
                continue

            lines.extend([f"### {etf} — `{side}` ({tsa['total_rejects']} total temporal rejects)", ""])
            lines.extend([
                "| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ])
            for key in ["neg_recent_ic", "high_ratio"]:
                sub = tsa[key]
                if sub.get("n", 0) == 0:
                    continue
                n_eval = sub.get("n_evaluated", 0)
                lines.append(
                    f"| {sub['label']} | {sub['n']} | {n_eval} | "
                    f"{sub.get('n_fp_caught', 0)} | {sub.get('n_tp_killed', 0)} | {sub.get('n_median', 0)} | "
                    f"{sub.get('fp_precision', 0):.0%} | {sub.get('tp_collateral', 0):.0%} |"
                )
            lines.append("")

            # Show top TP killed by the high-ratio condition
            high_ratio = tsa.get("high_ratio", {})
            if high_ratio.get("top_tp_killed"):
                lines.append("**Top TP killed by recency_ratio cap:**")
                for item in high_ratio["top_tp_killed"][:5]:
                    lines.append(
                        f"- `{item['feature_name']}`: Train IC={item['train_ic']:+.4f}, "
                        f"Lock IC={item['lock_ic']:+.4f}, Sharpe={item['lock_sharpe']:+.4f}"
                    )
                lines.append("")

    # ─── Section 7: Root Cause & Recommendations ──────────────────────────────
    lines.extend([
        "---",
        "",
        "## 7. Root Cause Synthesis & Training-Only Fixes",
        "",
    ])

    for etf, sides in results.items():
        for side, data in sides.items():
            disc = data.get("discriminators")
            fp_features = data.get("fp_features", [])
            if not disc or not fp_features:
                continue

            lines.extend([f"### {etf} — `{side}`", ""])

            # Find strongest discriminators
            strong = [(k, v) for k, v in disc.items() if abs(v["cohens_d"]) > 0.5]
            strong.sort(key=lambda x: -abs(x[1]["cohens_d"]))

            if strong:
                lines.append("**Strong training-only discriminators (Cohen's d > 0.5):**")
                lines.append("")
                for key, vals in strong:
                    direction = "higher" if vals["cohens_d"] > 0 else "lower"
                    lines.append(
                        f"- `{key}`: FP is {direction} (d={vals['cohens_d']:+.2f}). "
                        f"Threshold {vals['best_threshold']:.3f} → {vals['best_accuracy']:.0%} accuracy."
                    )
                lines.append("")

            # Pattern analysis
            n_era_overfit = sum(1 for f in fp_features if f.get("ic_cv", 0) > 1.5)
            n_decaying = sum(1 for f in fp_features if f.get("half_ratio", 1) < 0.3)
            n_weak_component = sum(1 for f in fp_features if f.get("weak_link_cv", 0) > 2.0)
            n_regime_dep = sum(1 for f in fp_features if f.get("n_negative_regimes", 0) >= 2)

            lines.append("**Failure pattern counts:**")
            lines.append(f"- Era-concentrated (IC CV > 1.5): {n_era_overfit}/{len(fp_features)}")
            lines.append(f"- Decaying signal (half ratio < 0.3): {n_decaying}/{len(fp_features)}")
            lines.append(f"- Weak component (CV > 2.0): {n_weak_component}/{len(fp_features)}")
            lines.append(f"- Regime-dependent (≥2 negative regimes): {n_regime_dep}/{len(fp_features)}")
            lines.append("")

    # ─── Section 8: Primitive Component Toxicity ──────────────────────────────
    lines.extend([
        "---",
        "",
        "## 8. Primitive Component FP Rate (Cross-ETF)",
        "",
        "Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.",
        "",
    ])

    # Collect all primitives from FP and TP combo features
    prim_fp_counts = defaultdict(int)
    prim_tp_counts = defaultdict(int)
    for etf, sides in results.items():
        for side, data in sides.items():
            for f in data.get("fp_features", []):
                fn = f.get("feature_name", "")
                if fn.startswith("combo_"):
                    parts = fn.split("__")[1:]
                    for p in parts:
                        prim_fp_counts[p] += 1
            for f in data.get("tp_features", []):
                fn = f.get("feature_name", "")
                if fn.startswith("combo_"):
                    parts = fn.split("__")[1:]
                    for p in parts:
                        prim_tp_counts[p] += 1

    all_prims = set(list(prim_fp_counts.keys()) + list(prim_tp_counts.keys()))
    prim_table = []
    for p in all_prims:
        fp_n = prim_fp_counts.get(p, 0)
        tp_n = prim_tp_counts.get(p, 0)
        total = fp_n + tp_n
        if total >= 2:
            prim_table.append((p, fp_n, tp_n, total, fp_n / total))
    prim_table.sort(key=lambda x: -x[4])

    if prim_table:
        lines.extend([
            "| Primitive | FP | TP | Total | FP Rate | Flag |",
            "| :--- | ---: | ---: | ---: | ---: | :--- |",
        ])
        for p, fp_n, tp_n, total, rate in prim_table:
            flag = "⚠ TOXIC" if rate >= 0.80 and total >= 5 else ""
            lines.append(f"| `{p}` | {fp_n} | {tp_n} | {total} | {rate:.0%} | {flag} |")
        lines.append("")
    else:
        lines.append("_No combo features with sufficient data for primitive analysis._")
        lines.append("")

    # ─── Section 9: Operator Class FP Rate ────────────────────────────────────
    lines.extend([
        "---",
        "",
        "## 9. Operator Class FP Rate",
        "",
    ])

    op_fp = defaultdict(int)
    op_tp = defaultdict(int)
    for etf, sides in results.items():
        for side, data in sides.items():
            for f in data.get("fp_features", []):
                fn = f.get("feature_name", "")
                if fn.startswith("combo_"):
                    op = fn.split("__")[0].replace("combo_", "")
                    op_fp[op] += 1
            for f in data.get("tp_features", []):
                fn = f.get("feature_name", "")
                if fn.startswith("combo_"):
                    op = fn.split("__")[0].replace("combo_", "")
                    op_tp[op] += 1

    sym_ops = {"max", "min", "mean", "rank_max", "rank_min"}
    cond_ops = {"ifelse", "diff", "clamp_diff", "ratio", "product", "abs_diff"}
    tri_ops = {"tri_max", "tri_min", "tri_mean", "tri_median", "tri_ifelse"}

    for label, ops in [("Symmetric", sym_ops), ("Conditional", cond_ops), ("3-way", tri_ops)]:
        fp_n = sum(op_fp.get(op, 0) for op in ops)
        tp_n = sum(op_tp.get(op, 0) for op in ops)
        total = fp_n + tp_n
        if total > 0:
            lines.append(f"- **{label}** (`{', '.join(sorted(ops))}`): FP={fp_n}, TP={tp_n}, FP rate={fp_n/total:.0%}")
    lines.append("")

    # Write report
    report_path = HERE / f"FILTER_DIAGNOSIS{suffix}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
