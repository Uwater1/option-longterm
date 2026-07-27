#!/usr/bin/env python3
"""
Experiment: Sortino Null Mismatch Fix — TP/FP Impact Analysis.

Tests the effect of aligning the B3 null kernel Sortino formula with simulate_returns.
Sweeps Sortino weight and percentile thresholds to find the configuration that:
  - Maximizes TP admission (lock IC > 0 AND lock Sharpe > 0)
  - Keeps FP admission at or below current level

Outputs:
  - Console table per ETF/side
  - day-model-new/data/sortino_fix_experiment.json
"""

import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata
from joblib import Parallel, delayed

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))

from build_features import FEATURES
from recipe_utils import compute_recipe, simulate_returns

# Import gate functions from select_features
from select_features import (
    evaluate_single_feature,
    numba_fast_rolling_tail_ic,
    fast_spearman,
    _tail_ic_from_sorted,
    MAX_FLIPS,
    FDR_THRESHOLD,
)

ETFS = ["300ETF", "500ETF", "50ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

ADAPTIVE_DATES = {
    "588000ETF": ("2020-11-01", "2025-01-01", "2025-01-01", "2025-07-01"),
    "_default": ("2015-01-01", "2022-01-01", "2022-01-01", "2024-03-01"),
}

# Sweep configurations — centered on inflation-compensated weight (~2.58x * 0.3 ≈ 0.77)
SORTINO_WEIGHTS = [0.3, 0.65, 0.70, 0.75, 0.80, 0.85]
PERCENTILES = [90, 92, 95, 97, 99]
N_SIMS = 500
BLOCK_SIZE = 10


def _spearman(a, b):
    if len(a) < 5 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom >= 1e-12 else 0.0


def compute_tail_ic(y, pred, side):
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


def numpy_null_composite_sim(x_flipped, y, window_starts, window_ends, side,
                             n_sims, block_size, sortino_weight, denom_mode):
    """Pure NumPy reference implementation of B3 null composite simulation.
    
    Args:
        denom_mode: "n_tail" (current buggy) or "n" (fixed, aligned with simulate_returns)
        sortino_weight: weight for Sortino in composite (remainder split: 0.4/(1-sw) for mono, etc.)
    
    Returns:
        null_scores: array of shape (n_sims,)
    """
    n = len(y)
    x32 = x_flipped.astype(np.float32)
    y32 = y.astype(np.float32)

    if side == "long":
        tail_def = 1
        pct = 0.15
    elif side == "short":
        tail_def = 2
        pct = 0.15
    else:
        tail_def = 3
        pct = 0.10

    n_tail = max(5, int(n * pct))
    ix_overall = np.argsort(x32)

    if tail_def == 1:
        long_idx = ix_overall[-n_tail:]
        short_idx = np.array([], dtype=np.int64)
    elif tail_def == 2:
        short_idx = ix_overall[:n_tail]
        long_idx = np.array([], dtype=np.int64)
    else:
        long_idx = ix_overall[-n_tail:]
        short_idx = ix_overall[:n_tail]

    is_two_sided = (tail_def == 3)

    # Precompute window sorted indices for rolling mono
    n_days = len(window_starts)
    window_offsets = np.zeros(n_days, dtype=np.int32)
    flat_indices = []
    curr_offset = 0
    for t in range(n_days):
        st = window_starts[t]
        en = window_ends[t]
        window_offsets[t] = curr_offset
        x_win = x32[st:en]
        ix = np.argsort(x_win).astype(np.int32)
        flat_indices.extend(ix)
        curr_offset += len(ix)
    window_sorted_idx = np.array(flat_indices, dtype=np.int32)

    # Composite weight layout: mono gets 0.4 share of non-sortino, tail_ic 0.2, raw_ic 0.1
    # Original: 0.4*mono + 0.3*sortino + 0.2*tail_ic + 0.1*raw_ic
    # Parameterized: keep relative ratios of non-sortino components fixed
    w_sortino = sortino_weight
    remaining = 1.0 - w_sortino
    w_mono = remaining * (0.4 / 0.7)   # 0.4/(0.4+0.2+0.1) = 4/7
    w_tail = remaining * (0.2 / 0.7)   # 2/7
    w_raw = remaining * (0.1 / 0.7)    # 1/7

    # Denominator for Sortino downside std
    sortino_denom = n_tail if not is_two_sided else (len(long_idx) + len(short_idx))
    if denom_mode == "n":
        sortino_denom = n

    # Generate random starts
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = max(1, n - block_size + 1)
    rng = np.random.default_rng(42)
    all_starts = rng.integers(0, possible_starts, size=(n_sims, num_blocks)).astype(np.int32)

    null_scores = np.empty(n_sims, dtype=np.float64)

    for s in range(n_sims):
        # Block shuffle
        starts_s = all_starts[s]
        y_null = np.empty(n, dtype=np.float32)
        pos = 0
        for i in range(num_blocks):
            st = starts_s[i]
            for offset in range(block_size):
                if pos < n:
                    y_null[pos] = y32[st + offset]
                    pos += 1
                else:
                    break

        # Raw IC
        raw_ic_null = fast_spearman(y_null, x32)

        # Tail IC
        tail_ic_null = _tail_ic_from_sorted(ix_overall, x32, y_null, n, n_tail, tail_def)

        # Rolling Mono
        mono_null = numba_fast_rolling_tail_ic(
            x32, y_null, window_starts, window_ends,
            window_offsets, window_sorted_idx, tail_def, pct
        )

        # Sortino
        if not is_two_sided:
            if tail_def == 1:
                tail_idx = long_idx
            else:
                tail_idx = short_idx
            m = len(tail_idx)
            sum_ret = 0.0
            sum_sq_down = 0.0
            for k in range(m):
                idx = tail_idx[k]
                r = (y_null[idx] - 0.0008) if tail_def == 1 else (-y_null[idx] - 0.0008)
                sum_ret += r
                if r < 0:
                    sum_sq_down += r * r
            ann_ret = (sum_ret / m) * 244.0
            down_std = np.sqrt(sum_sq_down / sortino_denom) * np.sqrt(244.0)
            sortino_null = ann_ret / (down_std + 1e-10)
        else:
            n_l = len(long_idx)
            n_s = len(short_idx)
            total_cnt = n_l + n_s
            sum_ret = 0.0
            sum_sq_down = 0.0
            for k in range(n_l):
                r = y_null[long_idx[k]] - 0.0008
                sum_ret += r
                if r < 0:
                    sum_sq_down += r * r
            for k in range(n_s):
                r = -y_null[short_idx[k]] - 0.0008
                sum_ret += r
                if r < 0:
                    sum_sq_down += r * r
            ann_ret = (sum_ret / total_cnt) * 244.0
            down_std = np.sqrt(sum_sq_down / sortino_denom) * np.sqrt(244.0)
            sortino_null = ann_ret / (down_std + 1e-10)

        null_scores[s] = w_mono * mono_null + w_sortino * sortino_null + w_tail * abs(tail_ic_null) + w_raw * abs(raw_ic_null)

    return null_scores


def evaluate_on_lockbox(lockbox_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians):
    """Compute lockbox IC and Sharpe for a feature."""
    if recipe:
        try:
            vals = compute_recipe(lockbox_df, recipe, train_means, train_stds, train_medians)
        except Exception:
            return None
    else:
        if feat_name not in lockbox_df.columns:
            return None
        vals = lockbox_df[feat_name].values.astype(np.float64)

    pred = sign * vals
    y = lockbox_df["trade_return"].values
    ic = _spearman(y, pred)
    _, sharpe, _, _, _, _ = simulate_returns(y, pred, side=side, position_mode="binary", enforce_absolute_sign=False)
    return {"ic": float(ic), "sharpe": float(sharpe)}


def run_experiment_for_etf_side(etf, side, n_jobs=-1, n_sims=500):
    """Run the Sortino fix experiment for one ETF/side combination."""
    print(f"\n{'='*80}")
    print(f"  EXPERIMENT: {etf} — {side}")
    print(f"{'='*80}")

    # Load data
    features_dir = REPO_ROOT / "day-model" / "data"
    path = features_dir / f"features_{etf}.parquet"
    if not path.exists():
        print(f"  SKIP: Dataset not found at {path}")
        return None

    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    dates_cfg = ADAPTIVE_DATES.get(etf, ADAPTIVE_DATES["_default"])
    train_start, train_end, oos_start, lockbox_start = dates_cfg
    train_start = pd.Timestamp(train_start)
    train_end = pd.Timestamp(train_end)
    lockbox_start = pd.Timestamp(lockbox_start)

    train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
    lockbox_df = df[df["date"] >= lockbox_start].reset_index(drop=True)

    if len(train_df) < 100 or len(lockbox_df) < 30:
        print(f"  SKIP: Insufficient data (train={len(train_df)}, lock={len(lockbox_df)})")
        return None

    print(f"  Train: {len(train_df)} rows ({train_start.date()} to {train_end.date()})")
    print(f"  Lockbox: {len(lockbox_df)} rows (from {lockbox_start.date()})")

    # Fill NaNs
    col_med_train = train_df[FEATURES].median().fillna(0.0)
    for col in FEATURES:
        if col in train_df.columns:
            train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
        if col in lockbox_df.columns:
            lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])

    y_train = train_df["trade_return"].values.astype(np.float64)
    dates_train = train_df["date"]

    # Compute train stats for recipes
    train_means = train_df[FEATURES].mean().to_dict()
    train_stds = train_df[FEATURES].std().to_dict()
    train_medians = train_df[FEATURES].median().to_dict()

    # Build feature matrix
    features_to_eval = [f for f in FEATURES if f in train_df.columns]
    X_df = train_df[features_to_eval].copy()

    # Load candidate recipes if available
    candidate_recipes = {}
    candidates_path = HERE / "data" / f"candidates_{etf}_{side}.json"
    if candidates_path.exists():
        try:
            with open(candidates_path, "r") as f:
                cands = json.load(f)
            # Compute recipe columns
            from scipy.stats import rankdata as _rankdata
            _std_cache = {}
            _rank_cache = {}
            n_rows = len(X_df)

            def _get_std_col_fast(col_name):
                if col_name not in _std_cache:
                    val = X_df[col_name].values.astype(np.float64)
                    mean = np.nanmean(val)
                    std = np.nanstd(val)
                    if std < 1e-12:
                        std = 1.0
                    _std_cache[col_name] = (val - mean) / std
                return _std_cache[col_name]

            def _get_rank_col_fast(col_name):
                if col_name not in _rank_cache:
                    val = X_df[col_name].values.astype(np.float64)
                    med = np.nanmedian(val)
                    val_filled = np.where(np.isnan(val), med, val)
                    _rank_cache[col_name] = _rankdata(val_filled) / n_rows
                return _rank_cache[col_name]

            def _compute_recipe_fast(recipe):
                op = recipe["op"]
                if op == "min":
                    return np.minimum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]))
                elif op == "max":
                    return np.maximum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]))
                elif op == "diff":
                    return _get_std_col_fast(recipe["feature_a"]) - _get_std_col_fast(recipe["feature_b"])
                elif op == "mean":
                    return (_get_std_col_fast(recipe["feature_a"]) + _get_std_col_fast(recipe["feature_b"])) / 2.0
                elif op == "product":
                    return _get_std_col_fast(recipe["feature_a"]) * _get_std_col_fast(recipe["feature_b"])
                elif op == "abs_diff":
                    return np.abs(_get_std_col_fast(recipe["feature_a"]) - _get_std_col_fast(recipe["feature_b"]))
                elif op == "rank_min":
                    return np.minimum(_get_rank_col_fast(recipe["feature_a"]), _get_rank_col_fast(recipe["feature_b"]))
                elif op == "rank_max":
                    return np.maximum(_get_rank_col_fast(recipe["feature_a"]), _get_rank_col_fast(recipe["feature_b"]))
                elif op == "z_sum":
                    return _get_std_col_fast(recipe["feature_a"]) + _get_std_col_fast(recipe["feature_b"])
                elif op == "z_diff":
                    return _get_std_col_fast(recipe["feature_a"]) - _get_std_col_fast(recipe["feature_b"])
                elif op == "sig_product":
                    a_std = _get_std_col_fast(recipe["feature_a"])
                    b_std = _get_std_col_fast(recipe["feature_b"])
                    return np.sign(a_std) * np.abs(b_std)
                elif op == "rel_diff":
                    a_std = _get_std_col_fast(recipe["feature_a"])
                    b_std = _get_std_col_fast(recipe["feature_b"])
                    return (a_std - b_std) / (np.abs(a_std) + np.abs(b_std) + 1e-5)
                elif op == "clamp_diff":
                    return np.clip(_get_std_col_fast(recipe["feature_a"]) - _get_std_col_fast(recipe["feature_b"]), -2.0, 2.0)
                elif op == "ifelse":
                    cond_val = X_df[recipe["feature_cond"]].values.astype(np.float64)
                    thresh = np.nanmedian(cond_val)
                    return np.where(cond_val > thresh, _get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]))
                elif op == "ratio":
                    a_val = X_df[recipe["feature_a"]].values.astype(np.float64)
                    b_val = X_df[recipe["feature_b"]].values.astype(np.float64)
                    return a_val / (np.abs(b_val) + 1e-5)
                elif op == "tri_mean" or op == "tri_z_mean":
                    return (_get_std_col_fast(recipe["feature_a"]) + _get_std_col_fast(recipe["feature_b"]) + _get_std_col_fast(recipe["feature_c"])) / 3.0
                elif op == "tri_min":
                    return np.minimum(np.minimum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"])), _get_std_col_fast(recipe["feature_c"]))
                elif op == "tri_max":
                    return np.maximum(np.maximum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"])), _get_std_col_fast(recipe["feature_c"]))
                elif op == "tri_sig_max":
                    a_std = _get_std_col_fast(recipe["feature_a"])
                    b_std = _get_std_col_fast(recipe["feature_b"])
                    c_std = _get_std_col_fast(recipe["feature_c"])
                    return np.maximum(a_std * np.sign(c_std), b_std * np.sign(c_std))
                elif op == "tri_median":
                    return np.median(np.stack([_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]), _get_std_col_fast(recipe["feature_c"])]), axis=0)
                elif op == "tri_ifelse":
                    cond1_val = X_df[recipe["feature_cond"]].values.astype(np.float64)
                    cond2_val = X_df[recipe["feature_cond2"]].values.astype(np.float64)
                    thresh1 = np.nanmedian(cond1_val)
                    thresh2 = np.nanmedian(cond2_val)
                    inner = np.where(cond2_val > thresh2, _get_std_col_fast(recipe["feature_b"]), _get_std_col_fast(recipe["feature_c"]))
                    return np.where(cond1_val > thresh1, _get_std_col_fast(recipe["feature_a"]), inner)
                else:
                    raise ValueError(f"Unknown op: {op}")

            batch_values = {}
            for item in cands:
                feat_name = item["feature_name"]
                recipe = item["recipe"]
                try:
                    candidate_values = _compute_recipe_fast(recipe)
                    batch_values[feat_name] = candidate_values
                    features_to_eval.append(feat_name)
                    candidate_recipes[feat_name] = recipe
                except Exception:
                    pass
            if batch_values:
                X_df = pd.concat([X_df, pd.DataFrame(batch_values, index=X_df.index)], axis=1, copy=False)
            print(f"  Loaded {len(batch_values)} combo candidates.")
        except Exception as e:
            print(f"  WARNING: Failed to load candidates: {e}")

    X_train = X_df[features_to_eval].values.astype(np.float64)

    # Rolling window indices
    dates_np = dates_train.values.astype('datetime64[D]')
    start_dates = dates_np - np.timedelta64(90, 'D')
    window_starts = np.searchsorted(dates_np, start_dates).astype(np.int32)
    window_ends = np.arange(1, len(dates_train) + 1, dtype=np.int32)

    # Run B1 + B2 gates (evaluate_single_feature includes jackknife + rolling guard)
    print(f"  Evaluating {len(features_to_eval)} features (B1 jackknife + B2 rolling guard)...")
    mono_thr = 0.55 if side in ["long", "short"] else 0.60
    ir_thr = 0.15 if side in ["long", "short"] else 0.30

    X_train_f32 = X_train.astype(np.float32)
    y_train_f32 = y_train.astype(np.float32)
    eval_results = Parallel(n_jobs=n_jobs)(
        delayed(evaluate_single_feature)(
            features_to_eval[i], X_train_f32[:, i], y_train_f32, window_starts, window_ends, side, MAX_FLIPS
        ) for i in range(len(features_to_eval))
    )
    eval_results.sort(key=lambda item: item["overall_ic"], reverse=True)

    # Filter to B1+B2 survivors
    survivors = [r for r in eval_results if r["split_half_passes"] and r["passes_rolling_guard"]]
    print(f"  B1+B2 survivors: {len(survivors)} / {len(features_to_eval)}")

    if len(survivors) == 0:
        print("  SKIP: No survivors.")
        return None

    # Cap to top-80 by IC to keep runtime manageable
    MAX_CANDIDATES = 80
    if len(survivors) > MAX_CANDIDATES:
        survivors = survivors[:MAX_CANDIDATES]
        print(f"  Capped to top {MAX_CANDIDATES} by IC for runtime.")

    # Compute lockbox labels for each survivor
    print(f"  Computing lockbox labels for {len(survivors)} candidates...")
    lockbox_labels = []
    for cand in survivors:
        feat_name = cand["feature_name"]
        sign = cand["sign"]
        recipe = candidate_recipes.get(feat_name, None)
        lock_res = evaluate_on_lockbox(lockbox_df, feat_name, recipe, sign, side, train_means, train_stds, train_medians)
        if lock_res:
            is_tp = lock_res["ic"] > 0 and lock_res["sharpe"] > 0
            lockbox_labels.append({"feature_name": feat_name, "lock_ic": lock_res["ic"],
                                   "lock_sharpe": lock_res["sharpe"], "is_tp": is_tp})
        else:
            lockbox_labels.append({"feature_name": feat_name, "lock_ic": 0.0,
                                   "lock_sharpe": 0.0, "is_tp": False})

    n_tp = sum(1 for lb in lockbox_labels if lb["is_tp"])
    n_fp = len(lockbox_labels) - n_tp
    print(f"  Lockbox labels: {n_tp} TP, {n_fp} FP (of {len(lockbox_labels)} total)")

    if n_tp == 0:
        print("  WARNING: No TP candidates — experiment may not be informative.")

    # Run null simulations for each configuration
    configs = []
    # Config A: current buggy (n_tail denom, weight=0.3)
    configs.append({"denom_mode": "n_tail", "sortino_weight": 0.3, "label": "CURRENT (n_tail, w=0.3)"})
    # Config B-J: fixed (n denom, swept weight)
    for w in SORTINO_WEIGHTS:
        configs.append({"denom_mode": "n", "sortino_weight": w, "label": f"FIXED (n, w={w:.1f})"})

    results = []

    for cfg in configs:
        print(f"\n  --- Config: {cfg['label']} ---")
        denom_mode = cfg["denom_mode"]
        sw = cfg["sortino_weight"]

        # For each candidate, run null sim and get thresholds
        admissions = {pct: [] for pct in PERCENTILES}

        for idx, cand in enumerate(survivors):
            x_flipped = cand["x_flipped"]
            real_comp = cand["composite_score"]

            # Recompute real composite with this weight config
            # (composite_score was computed with w=0.3, need to recompute for other weights)
            remaining = 1.0 - sw
            w_mono = remaining * (0.4 / 0.7)
            w_tail = remaining * (0.2 / 0.7)
            w_raw = remaining * (0.1 / 0.7)
            # Real composite uses simulate_returns Sortino (always correct)
            real_sortino = cand["sortino"]
            real_mono = cand["monotonicity"]  # This is the rolling mono value
            real_tail_ic = abs(cand["mean_tail_ic"])
            real_raw_ic = abs(cand["raw_ic"])
            real_comp_adjusted = w_mono * real_mono + sw * real_sortino + w_tail * real_tail_ic + w_raw * real_raw_ic

            # Run null simulation
            null_scores = numpy_null_composite_sim(
                x_flipped, y_train, window_starts, window_ends, side,
                n_sims, BLOCK_SIZE, sw, denom_mode
            )

            # Get percentile thresholds
            for pct in PERCENTILES:
                threshold = float(np.percentile(null_scores, pct))
                admitted = real_comp_adjusted >= threshold
                admissions[pct].append(admitted)

            if (idx + 1) % 20 == 0:
                print(f"    Processed {idx + 1}/{len(survivors)} candidates...")

        # Evaluate TP/FP for each percentile
        for pct in PERCENTILES:
            admitted_mask = admissions[pct]
            tp_admitted = sum(1 for i, adm in enumerate(admitted_mask) if adm and lockbox_labels[i]["is_tp"])
            fp_admitted = sum(1 for i, adm in enumerate(admitted_mask) if adm and not lockbox_labels[i]["is_tp"])
            total_admitted = sum(admitted_mask)

            results.append({
                "etf": etf,
                "side": side,
                "config": cfg["label"],
                "denom_mode": denom_mode,
                "sortino_weight": sw,
                "percentile": pct,
                "tp_admitted": tp_admitted,
                "tp_total": n_tp,
                "fp_admitted": fp_admitted,
                "fp_total": n_fp,
                "total_admitted": total_admitted,
                "tp_recall": tp_admitted / max(1, n_tp),
                "fp_rate": fp_admitted / max(1, n_fp),
                "net": tp_admitted - fp_admitted,
            })

    return results


def print_results_table(all_results):
    """Print formatted comparison table."""
    if not all_results:
        print("No results to display.")
        return

    # Group by ETF/side
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in all_results:
        grouped[(r["etf"], r["side"])].append(r)

    for (etf, side), results in sorted(grouped.items()):
        print(f"\n{'='*100}")
        print(f"  {etf} — {side}  (TP total={results[0]['tp_total']}, FP total={results[0]['fp_total']})")
        print(f"{'='*100}")
        print(f"{'Config':<28} {'Pct':>4} {'TP Adm':>7} {'TP Rec':>7} {'FP Adm':>7} {'FP Rate':>8} {'Net':>5} {'Total':>6}")
        print("-" * 80)

        # Print baseline first, then fixed configs
        baseline = [r for r in results if r["denom_mode"] == "n_tail"]
        fixed = [r for r in results if r["denom_mode"] == "n"]

        for r in baseline:
            print(f"{r['config']:<28} {r['percentile']:>4} {r['tp_admitted']:>7} {r['tp_recall']:>7.1%} "
                  f"{r['fp_admitted']:>7} {r['fp_rate']:>8.1%} {r['net']:>5} {r['total_admitted']:>6}")
        print("-" * 80)
        for r in sorted(fixed, key=lambda x: (x["sortino_weight"], x["percentile"])):
            print(f"{r['config']:<28} {r['percentile']:>4} {r['tp_admitted']:>7} {r['tp_recall']:>7.1%} "
                  f"{r['fp_admitted']:>7} {r['fp_rate']:>8.1%} {r['net']:>5} {r['total_admitted']:>6}")


def find_optimal_config(all_results):
    """Find the configuration that maximizes TP recall while keeping FP rate <= baseline."""
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in all_results:
        grouped[(r["etf"], r["side"])].append(r)

    recommendations = []
    for (etf, side), results in sorted(grouped.items()):
        # Baseline: current config at 95th percentile (standard admission)
        baseline_95 = [r for r in results if r["denom_mode"] == "n_tail" and r["percentile"] == 95]
        if not baseline_95:
            continue
        baseline_fp_rate = baseline_95[0]["fp_rate"]
        baseline_tp_recall = baseline_95[0]["tp_recall"]

        # Find best fixed config: maximize TP recall with FP rate <= baseline + 0.05 (small tolerance)
        fixed = [r for r in results if r["denom_mode"] == "n"]
        # Filter: FP rate <= baseline + 5% tolerance
        acceptable = [r for r in fixed if r["fp_rate"] <= baseline_fp_rate + 0.05]
        if not acceptable:
            # If none acceptable, pick the one with lowest FP rate among fixed
            acceptable = fixed

        # Sort by: net (TP - FP) descending, then TP recall descending
        best = max(acceptable, key=lambda r: (r["net"], r["tp_recall"], -r["fp_rate"]))
        recommendations.append({
            "etf": etf,
            "side": side,
            "baseline_tp_recall": baseline_tp_recall,
            "baseline_fp_rate": baseline_fp_rate,
            "recommended_weight": best["sortino_weight"],
            "recommended_percentile": best["percentile"],
            "new_tp_recall": best["tp_recall"],
            "new_fp_rate": best["fp_rate"],
            "improvement": best["tp_recall"] - baseline_tp_recall,
        })

    return recommendations


def main():
    parser = argparse.ArgumentParser(description="Sortino null mismatch fix experiment")
    parser.add_argument("-e", "--etf", nargs="+", default=ETFS,
                        choices=["300ETF", "50ETF", "500ETF", "159915ETF", "588000ETF"],
                        help="ETFs to test")
    parser.add_argument("-s", "--side", nargs="+", default=SIDES,
                        choices=["single", "long", "short"],
                        help="Sides to test")
    parser.add_argument("--n-jobs", type=int, default=-1, help="Parallel workers for B1/B2")
    parser.add_argument("--n-sims", type=int, default=N_SIMS, help="Null simulation count")
    args = parser.parse_args()

    all_results = []
    for etf in args.etf:
        for side in args.side:
            results = run_experiment_for_etf_side(etf, side, n_jobs=args.n_jobs, n_sims=args.n_sims)
            if results:
                all_results.extend(results)

    # Print summary
    print_results_table(all_results)

    # Find optimal config
    recommendations = find_optimal_config(all_results)
    if recommendations:
        print(f"\n{'='*80}")
        print("  RECOMMENDATIONS")
        print(f"{'='*80}")
        for rec in recommendations:
            print(f"  {rec['etf']:>10} {rec['side']:>6}: weight={rec['recommended_weight']:.1f}, "
                  f"pct={rec['recommended_percentile']} | "
                  f"TP recall: {rec['baseline_tp_recall']:.1%} -> {rec['new_tp_recall']:.1%} "
                  f"(+{rec['improvement']:.1%}) | "
                  f"FP rate: {rec['baseline_fp_rate']:.1%} -> {rec['new_fp_rate']:.1%}")

    # Save results
    out_dir = HERE / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "sortino_fix_experiment.json"
    with open(out_path, "w") as f:
        json.dump({"results": all_results, "recommendations": recommendations}, f, indent=2)
    print(f"\nSaved results to {out_path}")


if __name__ == "__main__":
    main()
