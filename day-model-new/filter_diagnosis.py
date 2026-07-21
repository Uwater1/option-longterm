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
from recipe_utils import compute_recipe, simulate_returns

# Exclude 588000ETF — insufficient history for meaningful diagnosis
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

ADAPTIVE_DATES = {
    "_default": ("2015-01-01", "2022-01-01", "2022-01-01", "2024-03-01"),
}

GATE_ORDER = [
    ("REJECTED_SPLIT_HALF", "7-Year Jackknife"),
    ("REJECTED_ROLLING_GUARD", "B2 Rolling Guard"),
    ("REJECTED_FDR_GATE", "BH-FDR Gate"),
    ("REJECTED_ADMISSION_FLOOR", "B3 Composite Floor"),
    ("REJECTED_REDUNDANCY", "B4 Correlation Gate"),
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


def compute_feature_values(df, feat_name, recipe, train_means, train_stds, train_medians):
    """Get raw feature values (sign-adjusted later)."""
    if recipe:
        try:
            return compute_recipe(df, recipe, train_means, train_stds, train_medians)
        except Exception:
            return None
    else:
        if feat_name not in df.columns:
            return None
        return df[feat_name].values.astype(np.float64)


def evaluate_feature(df, feat_name, recipe, sign, side, train_means, train_stds, train_medians):
    """Compute IC and Sharpe for a feature on a dataframe split."""
    vals = compute_feature_values(df, feat_name, recipe, train_means, train_stds, train_medians)
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


def temporal_ic_decomposition(train_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians):
    """Decompose training IC by year to detect era-concentrated signals.
    
    Returns per-year ICs and stability metrics. A feature whose IC is driven by
    a single year/regime is more likely to fail OOS.
    """
    vals = compute_feature_values(train_df, feat_name, recipe, train_means, train_stds, train_medians)
    if vals is None:
        return None

    pred = sign * vals
    y = train_df["trade_return"].values
    dates = train_df["date"].values

    # Yearly decomposition
    years = pd.DatetimeIndex(dates).year
    unique_years = sorted(set(years))
    yearly_ics = {}
    for yr in unique_years:
        mask = years == yr
        if mask.sum() < 20:
            continue
        yearly_ics[int(yr)] = _spearman(y[mask], pred[mask])

    if len(yearly_ics) < 3:
        return None

    ic_values = list(yearly_ics.values())
    mean_ic = np.mean(ic_values)
    std_ic = np.std(ic_values)
    
    # Stability metrics (TRAINING-ONLY discriminators)
    ic_cv = std_ic / abs(mean_ic) if abs(mean_ic) > 1e-6 else 99.0  # Coefficient of variation
    n_negative_years = sum(1 for ic in ic_values if ic < 0)
    min_ic = min(ic_values)
    max_ic = max(ic_values)
    
    # Recent vs early ratio (last 2 years vs first 2 years)
    sorted_years = sorted(yearly_ics.keys())
    early_years = sorted_years[:2]
    recent_years = sorted_years[-2:]
    early_ic = np.mean([yearly_ics[y] for y in early_years])
    recent_ic = np.mean([yearly_ics[y] for y in recent_years])
    recency_ratio = recent_ic / early_ic if abs(early_ic) > 1e-6 else (99.0 if recent_ic > 0 else -99.0)
    
    # Half-split stability
    n = len(pred)
    half = n // 2
    ic_first_half = _spearman(y[:half], pred[:half])
    ic_second_half = _spearman(y[half:], pred[half:])
    half_ratio = ic_second_half / ic_first_half if abs(ic_first_half) > 1e-6 else 99.0

    return {
        "yearly_ics": yearly_ics,
        "mean_ic": float(mean_ic),
        "std_ic": float(std_ic),
        "ic_cv": float(ic_cv),
        "n_negative_years": n_negative_years,
        "n_years": len(yearly_ics),
        "min_ic": float(min_ic),
        "max_ic": float(max_ic),
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


def load_attempts(etf, side):
    """Load mining attempts for an ETF/side."""
    path = HERE / "data" / f"mining_attempts_{etf}_{side}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Filter Pipeline Deep Diagnosis")
    parser.add_argument("-e", "--etf", nargs="*", default=ETFS)
    parser.add_argument("-s", "--side", nargs="*", default=SIDES)
    args = parser.parse_args()

    features_dir = REPO_ROOT / "day-model" / "data"
    data_out_dir = HERE / "data"
    data_out_dir.mkdir(parents=True, exist_ok=True)

    all_results = {}

    for etf in args.etf:
        if etf not in ETFS:
            continue
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
        lockbox_df = df[df["date"] >= lockbox_start].reset_index(drop=True)

        # Fill NaNs
        col_med_train = train_df[FEATURES].median().fillna(0.0)
        for col in FEATURES:
            train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
            lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])

        # Pre-compute train stats
        train_means = {col: float(train_df[col].mean()) for col in FEATURES}
        train_stds = {col: float(train_df[col].std()) for col in FEATURES}
        train_medians = {col: float(train_df[col].median()) for col in FEATURES}

        all_results[etf] = {}

        for side in args.side:
            print(f"\n  {etf}/{side}:")

            attempts = load_attempts(etf, side)
            if not attempts:
                print(f"    No mining attempts found")
                continue

            admitted = [a for a in attempts if a.get("verdict", "").startswith("ADMITTED")]
            if not admitted:
                print(f"    No admitted features")
                continue

            print(f"    {len(attempts)} attempts, {len(admitted)} admitted")

            # ─── Phase 1: Label each admitted feature as TP or FP using lockbox ───
            fp_list = []  # False Positives (admitted but failed lockbox)
            tp_list = []  # True Positives (admitted and succeeded in lockbox)

            for item in admitted:
                feat_name = item["feature_name"]
                sign = item.get("sign", 1)
                recipe = item.get("recipe", None)

                lock_result = evaluate_feature(lockbox_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians)
                if lock_result is None:
                    continue

                is_fp = lock_result["ic"] <= 0 or lock_result["sharpe"] <= 0

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

                if is_fp:
                    fp_list.append(entry)
                else:
                    tp_list.append(entry)

            print(f"    FP: {len(fp_list)}, TP: {len(tp_list)}")

            if not fp_list:
                print(f"    No false positives — pipeline working well!")
                all_results[etf][side] = {"n_fp": 0, "n_tp": len(tp_list)}
                continue

            # ─── Phase 2: Deep WHY analysis on each FP and TP ───────────────────
            print(f"    Running temporal decomposition...")
            for entry in fp_list + tp_list:
                temporal = temporal_ic_decomposition(
                    train_df, entry["feature_name"], entry["recipe"],
                    entry["sign"], side, train_means, train_stds, train_medians
                )
                if temporal:
                    entry.update(temporal)

            print(f"    Running component stability...")
            for entry in fp_list + tp_list:
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
            for entry in fp_list + tp_list:
                regime = regime_concentration_analysis(
                    train_df, entry["feature_name"], entry["recipe"],
                    entry["sign"], side, train_means, train_stds, train_medians
                )
                if regime:
                    entry["ic_std_across_regimes"] = regime["ic_std_across_regimes"]
                    entry["n_negative_regimes"] = regime["n_negative_regimes"]
                    entry["regime_ics"] = regime["regime_ics"]

            # ─── Phase 3: Compute training-only discriminators ──────────────────
            print(f"    Computing training discriminators...")
            discriminators = compute_training_discriminators(fp_list, tp_list)

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

            all_results[etf][side] = {
                "n_fp": len(fp_list),
                "n_tp": len(tp_list),
                "fp_rate": len(fp_list) / (len(fp_list) + len(tp_list)) if (fp_list or tp_list) else 0,
                "fp_features": fp_list,
                "tp_features": tp_list,
                "discriminators": discriminators,
                "gate_mechanism": gate_mech,
                "fn_analysis": fn_analysis,
            }

    # Save JSON
    json_path = data_out_dir / "filter_diagnosis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nJSON written to: {json_path}")

    # Generate report
    generate_report(all_results)


def generate_report(results):
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
    lines.extend(["## 1. FP/TP Summary", ""])
    lines.extend([
        "| ETF | Side | Admitted | FP | TP | FP Rate |",
        "| :--- | :--- | ---: | ---: | ---: | ---: |",
    ])
    for etf, sides in results.items():
        for side, data in sides.items():
            n_fp = data.get("n_fp", 0)
            n_tp = data.get("n_tp", 0)
            total = n_fp + n_tp
            if total == 0:
                continue
            lines.append(f"| {etf} | {side} | {total} | {n_fp} | {n_tp} | {n_fp/total:.0%} |")
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
                if not yearly:
                    continue
                years_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly.items()))
                lines.extend([
                    f"**`{f['feature_name']}`** (Lock IC={f['lock_ic']:+.4f}, Sharpe={f['lock_sharpe']:+.4f})",
                    f"- Yearly ICs: {years_str}",
                    f"- IC CV={f.get('ic_cv', 0):.2f}, Neg years={f.get('n_negative_years', 0)}/{f.get('n_years', 0)}, "
                    f"Half ratio={f.get('half_ratio', 0):.2f}, Recency ratio={f.get('recency_ratio', 0):.2f}",
                ])
                if f.get("weak_link"):
                    lines.append(f"- Weak component: `{f['weak_link']}` (CV={f.get('weak_link_cv', 0):.2f}, neg years={f.get('weak_link_n_neg_years', 0)})")
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
                if not yearly:
                    continue
                years_str = " | ".join(f"{yr}: {ic:+.3f}" for yr, ic in sorted(yearly.items()))
                lines.extend([
                    f"**`{f['feature_name']}`** (Lock IC={f['lock_ic']:+.4f}, Sharpe={f['lock_sharpe']:+.4f})",
                    f"- Yearly ICs: {years_str}",
                    f"- IC CV={f.get('ic_cv', 0):.2f}, Neg years={f.get('n_negative_years', 0)}/{f.get('n_years', 0)}, "
                    f"Half ratio={f.get('half_ratio', 0):.2f}, Recency ratio={f.get('recency_ratio', 0):.2f}",
                ])
                if f.get("weak_link"):
                    lines.append(f"- Weak component: `{f['weak_link']}` (CV={f.get('weak_link_cv', 0):.2f})")
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

    # Write report
    report_path = HERE / "FILTER_DIAGNOSIS.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
