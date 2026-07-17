#!/usr/bin/env python3
"""
Stage A Feature Selection for Day-Model Rewrite v3.
Implements:
1. Flipping features to have positive overall training IC (2015-01-01 to 2022-01-01).
2. A3 Rolling pre-filter (90-calendar-day rolling tail IC monotonicity & IR check).
3. A2 Admission gate (theta correlation gate + replacement rule).
4. A4 Trial logging and Deflated IC calculation.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from numba import njit
from scipy.stats import rankdata, norm
from joblib import Parallel, delayed

# Set up paths to import existing features list
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from build_features import FEATURES

# Training period for Stage A (IC testing)
TRAIN_START = pd.Timestamp("2015-01-01")
TRAIN_END = pd.Timestamp("2022-01-01")

def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson over ranks. Faster than scipy.stats.spearmanr."""
    if a.shape[0] < 5:
        return 0.0
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)

@njit
def fast_rankdata(a: np.ndarray) -> np.ndarray:
    n = len(a)
    ix = np.argsort(a)
    ranks = np.empty(n, dtype=np.float64)
    for i in range(n):
        ranks[ix[i]] = i + 1.0
    return ranks

@njit
def fast_spearman(a: np.ndarray, b: np.ndarray) -> float:
    n = len(a)
    if n < 5:
        return 0.0
    mean_a = a.sum() / n
    mean_b = b.sum() / n
    var_a = 0.0
    var_b = 0.0
    for i in range(n):
        var_a += (a[i] - mean_a) ** 2
        var_b += (b[i] - mean_b) ** 2
    if var_a < 1e-24 or var_b < 1e-24:
        return 0.0
        
    ra = fast_rankdata(a)
    rb = fast_rankdata(b)
    
    mean_ra = ra.sum() / n
    mean_rb = rb.sum() / n
    
    cov = 0.0
    var_ra = 0.0
    var_rb = 0.0
    for i in range(n):
        diff_a = ra[i] - mean_ra
        diff_b = rb[i] - mean_rb
        cov += diff_a * diff_b
        var_ra += diff_a ** 2
        var_rb += diff_b ** 2
        
    denom = np.sqrt(var_ra * var_rb)
    if denom < 1e-12:
        return 0.0
    return cov / denom

@njit
def numba_rolling_tail_ic(x: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, tail_def: int, pct: float) -> np.ndarray:
    n_days = len(window_starts)
    out = np.zeros(n_days)
    
    for t in range(n_days):
        start = window_starts[t]
        end = window_ends[t]
        n_win = end - start
        n_tail = int(n_win * pct)
        if n_tail < 5:
            n_tail = 5
            
        if n_win < 15:
            out[t] = 0.0
            continue
            
        x_win = x[start:end]
        y_win = y[start:end]
        
        ix = np.argsort(x_win)
        
        if tail_def == 1:  # top
            x_tail = np.empty(n_tail)
            y_tail = np.empty(n_tail)
            for i in range(n_tail):
                idx = ix[n_win - n_tail + i]
                x_tail[i] = x_win[idx]
                y_tail[i] = y_win[idx]
        elif tail_def == 2:  # bot
            x_tail = np.empty(n_tail)
            y_tail = np.empty(n_tail)
            for i in range(n_tail):
                idx = ix[i]
                x_tail[i] = x_win[idx]
                y_tail[i] = y_win[idx]
        else:  # two-sided
            x_tail = np.empty(n_tail * 2)
            y_tail = np.empty(n_tail * 2)
            for i in range(n_tail):
                idx_bot = ix[i]
                x_tail[i] = x_win[idx_bot]
                y_tail[i] = y_win[idx_bot]
                
                idx_top = ix[n_win - n_tail + i]
                x_tail[n_tail + i] = x_win[idx_top]
                y_tail[n_tail + i] = y_win[idx_top]
                
        out[t] = fast_spearman(y_tail, x_tail)
        
    return out

def compute_rolling_tail_ic_series(x_flipped: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, side: str) -> np.ndarray:
    """Calculate the rolling tail IC series for a single flipped feature using Numba."""
    if side == "long":
        tail_def = 1
        pct = 0.15
    elif side == "short":
        tail_def = 2
        pct = 0.15
    else:  # single / both
        tail_def = 3
        pct = 0.10
    return numba_rolling_tail_ic(x_flipped, y, window_starts, window_ends, tail_def, pct)

def evaluate_single_feature(feature_name: str, x: np.ndarray, y: np.ndarray, dates: pd.Series, window_starts: np.ndarray, window_ends: np.ndarray, side: str):
    """Evaluate a single candidate feature: compute overall IC, flip if needed, and run rolling tail IC pre-filter."""
    # Compute overall raw IC
    raw_ic = _spearman_from_arrays(x, y)
    sign_flip = -1.0 if raw_ic < 0 else 1.0
    x_flipped = x * sign_flip
    overall_ic = abs(raw_ic)
    
    # Compute rolling tail IC series
    rolling_tail_ics = compute_rolling_tail_ic_series(x_flipped, y, window_starts, window_ends, side)
    
    mean_tail_ic = float(np.mean(rolling_tail_ics))
    std_tail_ic = float(np.std(rolling_tail_ics))
    ic_ir = mean_tail_ic / (std_tail_ic + 1e-10)
    monotonicity = float(np.mean(rolling_tail_ics > 0))
    
    return {
        "feature_name": feature_name,
        "sign": int(sign_flip),
        "raw_ic": float(raw_ic),
        "overall_ic": float(overall_ic),
        "mean_tail_ic": mean_tail_ic,
        "std_tail_ic": std_tail_ic,
        "ic_ir": ic_ir,
        "monotonicity": monotonicity,
        "x_flipped": x_flipped,  # Keep for correlation gate
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", required=True, choices=["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"])
    parser.add_argument("-s", "--side", required=True, choices=["single", "long", "short"])
    parser.add_argument("--tau", type=float, default=0.03, help="Overall IC threshold")
    parser.add_argument("--theta", type=float, default=0.50, help="Max absolute correlation threshold")
    parser.add_argument("--mono-thr", type=float, default=None, help="Rolling tail IC positivity threshold (monotonicity)")
    parser.add_argument("--ir-thr", type=float, default=None, help="Rolling tail IC Information Ratio threshold")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    parser.add_argument("--n-jobs", type=int, default=-1, help="Parallel workers")
    args = parser.parse_args()

    # Dynamic defaults based on side
    if args.mono_thr is None:
        args.mono_thr = 0.55 if args.side in ["long", "short"] else 0.70
    if args.ir_thr is None:
        args.ir_thr = 0.15 if args.side in ["long", "short"] else 0.30

    print(f"================================================================================")
    print(f"Stage A Feature Selection: ETF={args.etf}, Side={args.side}, Early={args.early}")
    print(f"Params: tau_IC={args.tau}, theta={args.theta}, mono_thr={args.mono_thr}, ir_thr={args.ir_thr}")
    print(f"================================================================================")

    # 1. Load feature dataset
    features_dir = REPO_ROOT / "day-model" / "data"
    fname = f"features_{args.etf}_early.parquet" if args.early else f"features_{args.etf}.parquet"
    path = features_dir / fname
    if not path.exists():
        print(f"ERROR: Dataset not found at {path}")
        sys.exit(1)
        
    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Filter to training period (2015-01-01 to 2022-01-01)
    mask = (df["date"] >= TRAIN_START) & (df["date"] < TRAIN_END)
    train_df = df[mask].reset_index(drop=True)
    if len(train_df) == 0:
        print(f"ERROR: No training data found between {TRAIN_START} and {TRAIN_END}")
        sys.exit(1)
        
    print(f"Loaded {len(train_df)} training rows from {train_df['date'].min().date()} to {train_df['date'].max().date()}")

    # Extract target and features
    target_col = "trade_return"
    y_train = train_df[target_col].values.astype(np.float64)
    dates_train = train_df["date"]

    # Fill NaNs defensively
    X_df = train_df[FEATURES].ffill()
    col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(col_med)
    X_train = X_df.values.astype(np.float64)

    # Precompute rolling window indices (90 calendar days)
    window_starts = np.zeros(len(dates_train), dtype=np.int32)
    window_ends = np.zeros(len(dates_train), dtype=np.int32)
    for t in range(len(dates_train)):
        start_date = dates_train.iloc[t] - pd.Timedelta(days=90)
        window_starts[t] = np.searchsorted(dates_train, start_date)
        window_ends[t] = t + 1

    # 2. Evaluate all features in parallel
    print(f"Evaluating {len(FEATURES)} features on training set...")
    eval_results = Parallel(n_jobs=args.n_jobs)(
        delayed(evaluate_single_feature)(
            FEATURES[i], X_train[:, i], y_train, dates_train, window_starts, window_ends, args.side
        ) for i in range(len(FEATURES))
    )

    # Sort results by overall IC descending (strongest candidate first)
    eval_results.sort(key=lambda item: item["overall_ic"], reverse=True)

    # 3. Log all attempts (A4)
    attempts_log = []
    selected_pool = []
    
    # Pre-filter: Check Stage A3 rolling tail IC guard
    surviving_candidates = []
    for item in eval_results:
        # A3 rolling guard condition:
        passes_guard = (item["monotonicity"] >= args.mono_thr) and (item["ic_ir"] >= args.ir_thr)
        
        attempt_record = {
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "raw_ic": item["raw_ic"],
            "overall_ic": item["overall_ic"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"],
            "passes_rolling_guard": bool(passes_guard),
            "verdict": "REJECTED_ROLLING_GUARD" if not passes_guard else "PENDING_ADMISSION"
        }
        
        if passes_guard:
            surviving_candidates.append(item)
        else:
            attempts_log.append(attempt_record)

    print(f"{len(surviving_candidates)} features survived rolling guard out of {len(FEATURES)}.")

    # 4. Admission Gate (A2)
    # The pool of admitted features
    admitted_pool = []  # list of dicts

    for cand in surviving_candidates:
        cand_name = cand["feature_name"]
        cand_ic = cand["overall_ic"]
        x_cand = cand["x_flipped"]
        
        # Check overall IC >= tau_IC admission gate
        if cand_ic < args.tau:
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "verdict": "REJECTED_TAU_IC_THRESHOLD"
            })
            continue

        # If pool is empty, admit candidate immediately
        if not admitted_pool:
            admitted_pool.append(cand)
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "max_corr": 0.0,
                "verdict": "ADMITTED"
            })
            continue

        # Compute max correlation with current pool members
        corrs = []
        for p in admitted_pool:
            c = np.corrcoef(x_cand, p["x_flipped"])[0, 1]
            corrs.append((p["feature_name"], abs(c)))
            
        corrs.sort(key=lambda x: x[1], reverse=True)
        max_corr_feature, max_corr = corrs[0]

        # Case 1: Max correlation is below threshold -> ADMIT
        if max_corr < args.theta:
            admitted_pool.append(cand)
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "max_corr": max_corr,
                "max_corr_feature": max_corr_feature,
                "verdict": "ADMITTED"
            })
        else:
            # Case 2: Max correlation exceeds threshold -> Check replacement rule
            # Replacement rule: if IC(new) >= 0.10 and IC(new) >= 1.3 * IC(old)
            # and exactly one existing pool member g has corr(new, g) > theta, replace g with new.
            high_corr_members = [item for item in corrs if item[1] >= args.theta]
            
            replaced = False
            if cand_ic >= 0.10 and len(high_corr_members) == 1:
                old_feature_name, _ = high_corr_members[0]
                # Find old feature details in admitted_pool
                old_idx = -1
                for idx, p in enumerate(admitted_pool):
                    if p["feature_name"] == old_feature_name:
                        old_idx = idx
                        break
                
                if old_idx != -1:
                    old_ic = admitted_pool[old_idx]["overall_ic"]
                    if cand_ic >= 1.3 * old_ic:
                        # Replace old feature with new candidate!
                        admitted_pool[old_idx] = cand
                        replaced = True
                        attempts_log.append({
                            "feature_name": cand_name,
                            "sign": cand["sign"],
                            "raw_ic": cand["raw_ic"],
                            "overall_ic": cand_ic,
                            "ic_ir": cand["ic_ir"],
                            "monotonicity": cand["monotonicity"],
                            "passes_rolling_guard": True,
                            "max_corr": max_corr,
                            "max_corr_feature": max_corr_feature,
                            "verdict": f"ADMITTED_REPLACED_{old_feature_name}"
                        })
                        # Log that old feature was replaced/dropped in attempts_log
                        attempts_log.append({
                            "feature_name": old_feature_name,
                            "verdict": f"DROPPED_REPLACED_BY_{cand_name}"
                        })
            
            if not replaced:
                attempts_log.append({
                    "feature_name": cand_name,
                    "sign": cand["sign"],
                    "raw_ic": cand["raw_ic"],
                    "overall_ic": cand_ic,
                    "ic_ir": cand["ic_ir"],
                    "monotonicity": cand["monotonicity"],
                    "passes_rolling_guard": True,
                    "max_corr": max_corr,
                    "max_corr_feature": max_corr_feature,
                    "verdict": "REJECTED_REDUNDANCY"
                })

    print(f"Final admitted pool size: {len(admitted_pool)}")

    # 5. Deflated IC calculation (A4)
    # Total trial count N is the number of all candidates evaluated (i.e. length of FEATURES)
    # The distribution of overall ICs is the distribution across all completed trials
    all_trial_ics = [item["overall_ic"] for item in eval_results]
    std_trial_ics = np.std(all_trial_ics)
    n_trials = len(all_trial_ics)
    
    # Calculate mean off-diagonal correlation among all trials' daily values
    # Standard Pearson correlation of X_train
    if n_trials > 1:
        corr_matrix = np.corrcoef(X_train.T)
        np.fill_diagonal(corr_matrix, np.nan)
        mean_rho = float(np.clip(np.nanmean(abs(corr_matrix)), 0.0, 0.99))
    else:
        mean_rho = 0.5

    # Compute deflated IC for each admitted pool member
    for item in admitted_pool:
        raw_best_ic = item["overall_ic"]
        overfit_bias = std_trial_ics * np.sqrt(2.0 * np.log(max(float(n_trials), 1.001))) * np.sqrt(max(1.0 - mean_rho, 0.0))
        deflated_ic = float(raw_best_ic - overfit_bias)
        item["deflated_ic"] = deflated_ic

    # Format the selected pool output
    selected_output = []
    for item in admitted_pool:
        selected_output.append({
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "overall_ic": item["overall_ic"],
            "deflated_ic": item["deflated_ic"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"]
        })

    # Save selected pool and attempts log to json files
    data_out_dir = HERE / "data"
    os.makedirs(data_out_dir, exist_ok=True)
    suffix = "_early" if args.early else ""
    
    selected_path = data_out_dir / f"selected_pool_{args.etf}_{args.side}{suffix}.json"
    with open(selected_path, "w") as f:
        json.dump(selected_output, f, indent=2)
    print(f"Saved selected pool to {selected_path}")

    attempts_path = data_out_dir / f"mining_attempts_{args.etf}_{args.side}{suffix}.json"
    with open(attempts_path, "w") as f:
        json.dump(attempts_log, f, indent=2)
    print(f"Saved attempts log to {attempts_path}")
    print(f"================================================================================")

if __name__ == "__main__":
    main()
