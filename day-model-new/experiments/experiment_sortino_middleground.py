#!/usr/bin/env python3
"""
Focused experiment: middle-ground Sortino weight (0.4-0.6) with fine percentile grid.
Uses multiprocessing across candidates for speed.
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata
from joblib import Parallel, delayed
from collections import defaultdict

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))
sys.path.append(str(HERE))

from build_features import FEATURES
from recipe_utils import compute_recipe, simulate_returns
from select_features import (
    evaluate_single_feature, numba_fast_rolling_tail_ic,
    fast_spearman, _tail_ic_from_sorted, MAX_FLIPS,
)
from experiment_sortino_fix import (
    numpy_null_composite_sim, evaluate_on_lockbox, ADAPTIVE_DATES,
)

ETFS = ["300ETF", "500ETF", "50ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

# Middle-ground weights + fine percentile grid
WEIGHTS = [0.40, 0.45, 0.50, 0.55, 0.60]
PERCENTILES = [90, 91, 92, 93, 94, 95]
N_SIMS = 500
BLOCK_SIZE = 10


def run_single_candidate(args):
    """Run null sim for one candidate across all configs. Used by multiprocessing."""
    x_flipped, y_train, window_starts, window_ends, side, n_sims = args
    
    results = {}
    for w in WEIGHTS:
        null_scores = numpy_null_composite_sim(
            x_flipped, y_train, window_starts, window_ends, side,
            n_sims, BLOCK_SIZE, w, "n"  # fixed formula only
        )
        for pct in PERCENTILES:
            threshold = float(np.percentile(null_scores, pct))
            results[(w, pct)] = threshold
    return results


def run_etf_side(etf, side, n_jobs=-1, n_sims=500):
    """Run experiment for one ETF/side."""
    print(f"\n{'='*70}")
    print(f"  {etf} — {side}")
    print(f"{'='*70}")

    features_dir = REPO_ROOT / "day-model" / "data"
    path = features_dir / f"features_{etf}.parquet"
    if not path.exists():
        return None

    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    dates_cfg = ADAPTIVE_DATES.get(etf, ADAPTIVE_DATES["_default"])
    train_start, train_end, oos_start, lockbox_start = dates_cfg
    train_start, train_end = pd.Timestamp(train_start), pd.Timestamp(train_end)
    lockbox_start = pd.Timestamp(lockbox_start)

    train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
    lockbox_df = df[df["date"] >= lockbox_start].reset_index(drop=True)

    if len(train_df) < 100 or len(lockbox_df) < 30:
        return None

    col_med_train = train_df[FEATURES].median().fillna(0.0)
    for col in FEATURES:
        if col in train_df.columns:
            train_df[col] = train_df[col].ffill().fillna(col_med_train[col])
        if col in lockbox_df.columns:
            lockbox_df[col] = lockbox_df[col].ffill().fillna(col_med_train[col])

    y_train = train_df["trade_return"].values.astype(np.float64)
    dates_train = train_df["date"]
    train_means = train_df[FEATURES].mean().to_dict()
    train_stds = train_df[FEATURES].std().to_dict()
    train_medians = train_df[FEATURES].median().to_dict()

    features_to_eval = [f for f in FEATURES if f in train_df.columns]
    X_df = train_df[features_to_eval].copy()

    # Load candidates
    candidate_recipes = {}
    candidates_path = HERE / "data" / f"candidates_{etf}_{side}.json"
    if candidates_path.exists():
        try:
            with open(candidates_path, "r") as f:
                cands = json.load(f)
            from scipy.stats import rankdata as _rankdata
            _std_cache, _rank_cache = {}, {}
            n_rows = len(X_df)

            def _get_std(col):
                if col not in _std_cache:
                    v = X_df[col].values.astype(np.float64)
                    m, s = np.nanmean(v), np.nanstd(v)
                    _std_cache[col] = (v - m) / (s if s > 1e-12 else 1.0)
                return _std_cache[col]

            def _get_rank(col):
                if col not in _rank_cache:
                    v = X_df[col].values.astype(np.float64)
                    v = np.where(np.isnan(v), np.nanmedian(v), v)
                    _rank_cache[col] = _rankdata(v) / n_rows
                return _rank_cache[col]

            def _recipe(r):
                op = r["op"]
                a, b = r.get("feature_a"), r.get("feature_b")
                if op == "min": return np.minimum(_get_std(a), _get_std(b))
                if op == "max": return np.maximum(_get_std(a), _get_std(b))
                if op == "diff": return _get_std(a) - _get_std(b)
                if op == "mean": return (_get_std(a) + _get_std(b)) / 2
                if op == "product": return _get_std(a) * _get_std(b)
                if op == "abs_diff": return np.abs(_get_std(a) - _get_std(b))
                if op == "rank_min": return np.minimum(_get_rank(a), _get_rank(b))
                if op == "rank_max": return np.maximum(_get_rank(a), _get_rank(b))
                if op == "z_sum": return _get_std(a) + _get_std(b)
                if op == "z_diff": return _get_std(a) - _get_std(b)
                if op == "sig_product": return np.sign(_get_std(a)) * np.abs(_get_std(b))
                if op == "rel_diff": return (_get_std(a) - _get_std(b)) / (np.abs(_get_std(a)) + np.abs(_get_std(b)) + 1e-5)
                if op == "clamp_diff": return np.clip(_get_std(a) - _get_std(b), -2, 2)
                if op == "ifelse":
                    c = X_df[r["feature_cond"]].values.astype(np.float64)
                    return np.where(c > np.nanmedian(c), _get_std(a), _get_std(b))
                if op == "ratio":
                    return X_df[a].values / (np.abs(X_df[b].values) + 1e-5)
                if op in ("tri_mean", "tri_z_mean"):
                    return (_get_std(a) + _get_std(b) + _get_std(r["feature_c"])) / 3
                if op == "tri_min":
                    return np.minimum(np.minimum(_get_std(a), _get_std(b)), _get_std(r["feature_c"]))
                if op == "tri_max":
                    return np.maximum(np.maximum(_get_std(a), _get_std(b)), _get_std(r["feature_c"]))
                if op == "tri_sig_max":
                    return np.maximum(_get_std(a) * np.sign(_get_std(r["feature_c"])), _get_std(b) * np.sign(_get_std(r["feature_c"])))
                if op == "tri_median":
                    return np.median(np.stack([_get_std(a), _get_std(b), _get_std(r["feature_c"])]), axis=0)
                if op == "tri_ifelse":
                    c1 = X_df[r["feature_cond"]].values.astype(np.float64)
                    c2 = X_df[r["feature_cond2"]].values.astype(np.float64)
                    inner = np.where(c2 > np.nanmedian(c2), _get_std(b), _get_std(r["feature_c"]))
                    return np.where(c1 > np.nanmedian(c1), _get_std(a), inner)
                raise ValueError(f"Unknown op: {op}")

            batch = {}
            for item in cands:
                try:
                    batch[item["feature_name"]] = _recipe(item["recipe"])
                    features_to_eval.append(item["feature_name"])
                    candidate_recipes[item["feature_name"]] = item["recipe"]
                except Exception:
                    pass
            if batch:
                X_df = pd.concat([X_df, pd.DataFrame(batch, index=X_df.index)], axis=1, copy=False)
        except Exception as e:
            print(f"  WARNING: {e}")

    X_train = X_df[features_to_eval].values.astype(np.float64)
    dates_np = dates_train.values.astype('datetime64[D]')
    window_starts = np.searchsorted(dates_np, dates_np - np.timedelta64(90, 'D')).astype(np.int32)
    window_ends = np.arange(1, len(dates_train) + 1, dtype=np.int32)

    # B1+B2 gates
    X_f32 = X_train.astype(np.float32)
    y_f32 = y_train.astype(np.float32)
    eval_results = Parallel(n_jobs=n_jobs)(
        delayed(evaluate_single_feature)(features_to_eval[i], X_f32[:, i], y_f32, window_starts, window_ends, side, MAX_FLIPS)
        for i in range(len(features_to_eval))
    )
    eval_results.sort(key=lambda x: x["overall_ic"], reverse=True)
    survivors = [r for r in eval_results if r["split_half_passes"] and r["passes_rolling_guard"]]
    
    MAX_CAND = 80
    if len(survivors) > MAX_CAND:
        survivors = survivors[:MAX_CAND]

    print(f"  Survivors: {len(survivors)}")
    if not survivors:
        return None

    # Lockbox labels
    labels = []
    for cand in survivors:
        res = evaluate_on_lockbox(lockbox_df, cand["feature_name"], candidate_recipes.get(cand["feature_name"]), cand["sign"], side, train_means, train_stds, train_medians)
        is_tp = res and res["ic"] > 0 and res["sharpe"] > 0
        labels.append(is_tp)

    n_tp = sum(labels)
    n_fp = len(labels) - n_tp
    print(f"  TP={n_tp}, FP={n_fp}")

    # Run null sims in parallel across candidates
    print(f"  Running null sims ({len(survivors)} candidates x {len(WEIGHTS)} weights x {n_sims} sims)...")
    sim_args = [(cand["x_flipped"], y_train, window_starts, window_ends, side, n_sims) for cand in survivors]
    all_thresholds = Parallel(n_jobs=n_jobs, prefer="threads")(
        delayed(run_single_candidate)(args) for args in sim_args
    )

    # Evaluate admissions
    results = []
    for w in WEIGHTS:
        for pct in PERCENTILES:
            tp_adm, fp_adm = 0, 0
            for idx, cand in enumerate(survivors):
                # Real composite with this weight
                remaining = 1.0 - w
                w_mono = remaining * (4/7)
                w_tail = remaining * (2/7)
                w_raw = remaining * (1/7)
                real_comp = w_mono * cand["monotonicity"] + w * cand["sortino"] + w_tail * abs(cand["mean_tail_ic"]) + w_raw * abs(cand["raw_ic"])
                
                threshold = all_thresholds[idx][(w, pct)]
                if real_comp >= threshold:
                    if labels[idx]:
                        tp_adm += 1
                    else:
                        fp_adm += 1
            
            results.append({
                "etf": etf, "side": side, "weight": w, "percentile": pct,
                "tp_admitted": tp_adm, "tp_total": n_tp,
                "fp_admitted": fp_adm, "fp_total": n_fp,
            })

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", nargs="+", default=ETFS)
    parser.add_argument("-s", "--side", nargs="+", default=SIDES)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--n-sims", type=int, default=N_SIMS)
    args = parser.parse_args()

    all_results = []
    for etf in args.etf:
        for side in args.side:
            res = run_etf_side(etf, side, n_jobs=args.n_jobs, n_sims=args.n_sims)
            if res:
                all_results.extend(res)

    # Aggregate
    agg = defaultdict(lambda: {"tp": 0, "tp_tot": 0, "fp": 0, "fp_tot": 0})
    for r in all_results:
        k = (r["weight"], r["percentile"])
        agg[k]["tp"] += r["tp_admitted"]
        agg[k]["tp_tot"] += r["tp_total"]
        agg[k]["fp"] += r["fp_admitted"]
        agg[k]["fp_tot"] += r["fp_total"]

    print(f"\n{'='*85}")
    print(f"  AGGREGATED (fixed formula, middle-ground weights)")
    print(f"{'='*85}")
    print(f"  {'Weight':<8} {'Pct':>4} {'TP_Adm':>7} {'TP_Rec':>7} {'FP_Adm':>7} {'FP_Rate':>8} {'Net':>5} {'Precision':>10}")
    print("  " + "-" * 70)
    
    # Reference: current buggy at 95th = TP 84.4%, FP 48.8%, Net +6
    print(f"  {'BASELINE':<8} {'95':>4} {'65':>7} {'84.4%':>7} {'59':>7} {'48.8%':>8} {'+6':>5} {'52.4%':>10}  <- current buggy")
    print("  " + "-" * 70)
    
    for k in sorted(agg.keys()):
        w, pct = k
        v = agg[k]
        tp_r = v["tp"] / max(1, v["tp_tot"])
        fp_r = v["fp"] / max(1, v["fp_tot"])
        net = v["tp"] - v["fp"]
        prec = v["tp"] / max(1, v["tp"] + v["fp"])
        print(f"  {w:<8.2f} {pct:>4} {v['tp']:>7} {tp_r:>7.1%} {v['fp']:>7} {fp_r:>8.1%} {net:>+5} {prec:>10.1%}")

    # Save
    out = HERE / "data" / "sortino_middleground.json"
    with open(out, "w") as f:
        json.dump({"results": all_results, "aggregated": {f"{k[0]}_{k[1]}": v for k, v in agg.items()}}, f, indent=2)
    print(f"\n  Saved to {out}")


if __name__ == "__main__":
    main()
