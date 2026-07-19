#!/usr/bin/env python3
"""
Stage A Feature Selection for Day-Model Rewrite v3.
Implements:
1. Flipping features to have positive overall training IC (date ranges adjusted dynamically per ETF).
2. A3 Rolling pre-filter (90-calendar-day rolling tail IC monotonicity & IR check).
3. Light Benjamini-Hochberg FDR pre-filter gate at q = 0.20 using single-feature block-shuffled empirical null simulation.
4. Cumulative persistent ledger tracking of trial count N per (ETF, side).
5. Data-adaptive empirical 95th-percentile tail IC admission floor via multi-trial block-shuffled empirical null simulation.
6. Stage A2 Admission gate (correlation gate + replacement rule).
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from numba import njit
from scipy.stats import rankdata
from joblib import Parallel, delayed

# Set up paths to import existing features list
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from build_features import FEATURES

FDR_THRESHOLD = 0.30

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

@njit(cache=True)
def fast_rankdata(a: np.ndarray) -> np.ndarray:
    n = len(a)
    ix = np.argsort(a)
    ranks = np.empty(n, dtype=np.float64)
    for i in range(n):
        ranks[ix[i]] = i + 1.0
    return ranks

@njit(cache=True)
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

@njit(cache=True)
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

@njit(cache=True)
def numba_block_shuffle(y: np.ndarray, block_size=10) -> np.ndarray:
    """Generate block-shuffled target preserving serial structure (circular block-bootstrap)."""
    n = len(y)
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = n - block_size + 1
    if possible_starts <= 0:
        # Fallback: simple bootstrap
        idx = np.empty(n, dtype=np.int32)
        for i in range(n):
            idx[i] = np.random.randint(0, n)
        out = np.empty(n)
        for i in range(n):
            out[i] = y[idx[i]]
        return out
        
    starts = np.empty(num_blocks, dtype=np.int32)
    for i in range(num_blocks):
        starts[i] = np.random.randint(0, possible_starts)
        
    idx = np.empty(n, dtype=np.int32)
    pos = 0
    for i in range(num_blocks):
        start = starts[i]
        for offset in range(block_size):
            if pos < n:
                idx[pos] = start + offset
                pos += 1
            else:
                break
    
    out = np.empty(n)
    for i in range(n):
        out[i] = y[idx[i]]
    return out

@njit(cache=True)
def numba_single_trial_empirical_sim(X: np.ndarray, y: np.ndarray, tail_def: int, n_tail: int, n_sims: int, block_size=10) -> np.ndarray:
    """Generate empirical single-trial null tail IC distribution by block-permuting the target."""
    n, n_features = X.shape
    null_ics = np.empty(n_sims)
    
    for s in range(n_sims):
        y_null = numba_block_shuffle(y, block_size)
        j = np.random.randint(0, n_features)
        x = X[:, j]
        
        # Pearson correlation for sign flip
        mean_x = x.mean()
        mean_y = y_null.mean()
        cov_xy = 0.0
        var_x = 0.0
        var_y = 0.0
        for k in range(n):
            dx = x[k] - mean_x
            dy = y_null[k] - mean_y
            cov_xy += dx * dy
            var_x += dx * dx
            var_y += dy * dy
        if var_x < 1e-24 or var_y < 1e-24:
            null_ics[s] = 0.0
            continue
        
        raw_corr = cov_xy / np.sqrt(var_x * var_y)
        sign = 1.0 if raw_corr >= 0.0 else -1.0
        x_flipped = x * sign
        
        ix = np.argsort(x_flipped)
        if tail_def == 1:  # top
            x_tail = np.empty(n_tail)
            y_tail = np.empty(n_tail)
            for t in range(n_tail):
                idx = ix[n - n_tail + t]
                x_tail[t] = x_flipped[idx]
                y_tail[t] = y_null[idx]
        elif tail_def == 2:  # bot
            x_tail = np.empty(n_tail)
            y_tail = np.empty(n_tail)
            for t in range(n_tail):
                idx = ix[t]
                x_tail[t] = x_flipped[idx]
                y_tail[t] = y_null[idx]
        else:  # two-sided
            x_tail = np.empty(n_tail * 2)
            y_tail = np.empty(n_tail * 2)
            for t in range(n_tail):
                idx_bot = ix[t]
                x_tail[t] = x_flipped[idx_bot]
                y_tail[t] = y_null[idx_bot]
                
                idx_top = ix[n - n_tail + t]
                x_tail[n_tail + t] = x_flipped[idx_top]
                y_tail[n_tail + t] = y_null[idx_top]
                
        null_ics[s] = fast_spearman(y_tail, x_tail)
        
    return null_ics

@njit(cache=True)
def numba_multi_trial_empirical_sim(X: np.ndarray, y: np.ndarray, n_trials: int, tail_def: int, n_tail: int, n_sims: int, block_size=10) -> np.ndarray:
    """Generate empirical max tail IC distribution across n_trials features by block-permuting the target."""
    n, n_features = X.shape
    max_ics = np.empty(n_sims)
    
    for s in range(n_sims):
        y_null = numba_block_shuffle(y, block_size)
        
        max_ic = -1e10
        for i in range(n_trials):
            # Select random feature column with replacement
            j = np.random.randint(0, n_features)
            x = X[:, j]
            
            mean_x = x.mean()
            mean_y = y_null.mean()
            cov_xy = 0.0
            var_x = 0.0
            var_y = 0.0
            for k in range(n):
                dx = x[k] - mean_x
                dy = y_null[k] - mean_y
                cov_xy += dx * dy
                var_x += dx * dx
                var_y += dy * dy
            if var_x < 1e-24 or var_y < 1e-24:
                continue
            
            raw_corr = cov_xy / np.sqrt(var_x * var_y)
            sign = 1.0 if raw_corr >= 0.0 else -1.0
            x_flipped = x * sign
            
            ix = np.argsort(x_flipped)
            if tail_def == 1:
                x_tail = np.empty(n_tail)
                y_tail = np.empty(n_tail)
                for t in range(n_tail):
                    idx = ix[n - n_tail + t]
                    x_tail[t] = x_flipped[idx]
                    y_tail[t] = y_null[idx]
            elif tail_def == 2:
                x_tail = np.empty(n_tail)
                y_tail = np.empty(n_tail)
                for t in range(n_tail):
                    idx = ix[t]
                    x_tail[t] = x_flipped[idx]
                    y_tail[t] = y_null[idx]
            else:
                x_tail = np.empty(n_tail * 2)
                y_tail = np.empty(n_tail * 2)
                for t in range(n_tail):
                    idx_bot = ix[t]
                    x_tail[t] = x_flipped[idx_bot]
                    y_tail[t] = y_null[idx_bot]
                    
                    idx_top = ix[n - n_tail + t]
                    x_tail[n_tail + t] = x_flipped[idx_top]
                    y_tail[n_tail + t] = y_null[idx_top]
                    
            tail_ic = fast_spearman(y_tail, x_tail)
            if tail_ic > max_ic:
                max_ic = tail_ic
                
        max_ics[s] = max_ic
        
    return max_ics

def benjamini_hochberg_fdr(p_values: np.ndarray, fdr_threshold=FDR_THRESHOLD) -> np.ndarray:
    """
    Apply Benjamini-Hochberg procedure.
    Returns a boolean mask of kept indices.
    """
    m = len(p_values)
    if m == 0:
        return np.array([], dtype=bool)
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]
    
    bh_val = (np.arange(1, m + 1) / m) * fdr_threshold
    eligible = sorted_p <= bh_val
    
    mask = np.zeros(m, dtype=bool)
    if np.any(eligible):
        max_eligible_idx = np.max(np.where(eligible)[0])
        keep_indices = sorted_indices[:max_eligible_idx + 1]
        mask[keep_indices] = True
    return mask

def compute_side_tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str) -> float:
    """Compute tail-specific Spearman correlation on the active strategy tail."""
    n = len(y_pred)
    if side == "long":
        pct = 0.15
    elif side == "short":
        pct = 0.15
    else:  # single / both
        pct = 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0
        
    order = np.argsort(y_pred)
    if side == "long":
        idx = order[-n_tail:]
    elif side == "short":
        idx = order[:n_tail]
    else:  # two-sided
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
        
    return _spearman_from_arrays(y_true[idx], y_pred[idx])

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
    # Compute overall raw IC for flipping
    raw_ic = _spearman_from_arrays(x, y)
    sign_flip = -1.0 if raw_ic < 0 else 1.0
    x_flipped = x * sign_flip
    overall_ic = compute_side_tail_ic(y, x_flipped, side)
    
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
    parser.add_argument("--tau", type=float, default=0.03, help="Overall IC threshold (obsolete, replaced by simulation gate)")
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

    # Determine dynamic training start and end dates
    if args.etf == "588000ETF":
        train_start = pd.Timestamp("2020-11-01")
        train_end = pd.Timestamp("2025-01-01")
    else:
        train_start = pd.Timestamp("2015-01-01")
        train_end = pd.Timestamp("2022-01-01")

    print(f"================================================================================")
    print(f"Stage A Feature Selection: ETF={args.etf}, Side={args.side}, Early={args.early}")
    print(f"Training Range: {train_start.date()} to {train_end.date()}")
    print(f"Params: theta={args.theta}, mono_thr={args.mono_thr}, ir_thr={args.ir_thr}")
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

    # Filter to training period
    mask = (df["date"] >= train_start) & (df["date"] < train_end)
    train_df = df[mask].reset_index(drop=True)
    if len(train_df) == 0:
        print(f"ERROR: No training data found between {train_start} and {train_end}")
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

    # Load and compute candidate recipes dynamically
    import sys
    sys.path.append(str(HERE / "mining"))
    from recipe_utils import compute_recipe
    
    suffix = "_early" if args.early else ""
    candidates_path = HERE / "mining" / f"candidates_{args.etf}_{args.side}{suffix}.json"
    candidate_recipes = {}
    features_to_eval = list(FEATURES)
    
    if candidates_path.exists():
        try:
            with open(candidates_path, "r") as f:
                cands = json.load(f)
            print(f"Loaded {len(cands)} candidate combinations from {candidates_path.name}")
            
            # Use X_df to preserve NaN filled base features
            base_filled_df = train_df.copy()
            for col in FEATURES:
                base_filled_df[col] = X_df[col]
                
            for item in cands:
                feat_name = item["feature_name"]
                recipe = item["recipe"]
                try:
                    candidate_values = compute_recipe(base_filled_df, recipe)
                    X_df[feat_name] = candidate_values
                    features_to_eval.append(feat_name)
                    candidate_recipes[feat_name] = recipe
                except Exception as e:
                    print(f"WARNING: Failed to compute recipe for {feat_name}: {e}")
        except Exception as e:
            print(f"WARNING: Failed to load candidate recipes: {e}")
    else:
        print(f"No candidate combinations file found at {candidates_path}. Evaluating base features only.")

    X_train = X_df[features_to_eval].values.astype(np.float64)

    # Precompute rolling window indices (90 calendar days)
    window_starts = np.zeros(len(dates_train), dtype=np.int32)
    window_ends = np.zeros(len(dates_train), dtype=np.int32)
    for t in range(len(dates_train)):
        start_date = dates_train.iloc[t] - pd.Timedelta(days=90)
        window_starts[t] = np.searchsorted(dates_train, start_date)
        window_ends[t] = t + 1

    # 2. Evaluate all features in parallel
    print(f"Evaluating {len(features_to_eval)} features on training set...")
    eval_results = Parallel(n_jobs=args.n_jobs)(
        delayed(evaluate_single_feature)(
            features_to_eval[i], X_train[:, i], y_train, dates_train, window_starts, window_ends, args.side
        ) for i in range(len(features_to_eval))
    )

    # Sort results by overall IC descending (strongest candidate first)
    eval_results.sort(key=lambda item: item["overall_ic"], reverse=True)

    # 3. Persistent Cumulative Trial Ledger with robust attempts-log seeding
    data_out_dir = HERE / "data"
    os.makedirs(data_out_dir, exist_ok=True)
    suffix = "_early" if args.early else ""
    ledger_path = data_out_dir / f"trial_ledger_{args.etf}_{args.side}{suffix}.json"
    
    if ledger_path.exists():
        with open(ledger_path, "r") as f:
            trial_ledger = json.load(f)
        print(f"Loaded trial ledger with {len(trial_ledger)} features.")
    else:
        # Seed from existing attempts log if available
        attempts_path = data_out_dir / f"mining_attempts_{args.etf}_{args.side}{suffix}.json"
        if attempts_path.exists():
            try:
                with open(attempts_path, "r") as f:
                    attempts = json.load(f)
                trial_ledger = list(set(item["feature_name"] for item in attempts if "feature_name" in item))
                print(f"Seeded ledger with {len(trial_ledger)} unique features from attempts log: {attempts_path.name}")
            except Exception as e:
                print(f"WARNING: failed to parse attempts log: {e}")
                trial_ledger = list(features_to_eval)
        else:
            trial_ledger = list(features_to_eval)
            print(f"Initialized ledger with {len(trial_ledger)} features from features_to_eval.")
        
    ledger_set = set(trial_ledger)
    updated_ledger = list(trial_ledger)
    for feat in features_to_eval:
        if feat not in ledger_set:
            updated_ledger.append(feat)
            ledger_set.add(feat)
            
    with open(ledger_path, "w") as f:
        json.dump(updated_ledger, f, indent=2)
        
    n_trials = len(updated_ledger)
    print(f"Cumulative ledger size: {n_trials} (added {len(updated_ledger) - len(trial_ledger)} new features)")

    # 4. Light Benjamini-Hochberg FDR Pre-Filter Gate
    if args.side == "long":
        tail_def = 1
        pct = 0.15
    elif args.side == "short":
        tail_def = 2
        pct = 0.15
    else:  # single / both
        tail_def = 3
        pct = 0.10
    n_tail = max(5, int(len(y_train) * pct))
    
    print("Running single-trial empirical null simulation for BH-FDR pre-filter...")
    # Use actual design matrix X_train to preserve real candidate distributions
    null_single_ics = numba_single_trial_empirical_sim(X_train, y_train, tail_def, n_tail, 5000, block_size=10)
    
    # Compute empirical p-value for each candidate
    for item in eval_results:
        item["p_value"] = float(np.mean(null_single_ics >= item["overall_ic"]))
        
    # Apply Benjamini-Hochberg FDR procedure
    p_values = np.array([item["p_value"] for item in eval_results])
    bh_mask = benjamini_hochberg_fdr(p_values, fdr_threshold=0.20)
    for idx, item in enumerate(eval_results):
        item["passes_fdr"] = bool(bh_mask[idx])

    # 5. Log all attempts and identify surviving candidates
    attempts_log = []
    surviving_candidates = []
    
    for item in eval_results:
        passes_guard = (item["monotonicity"] >= args.mono_thr) and (item["ic_ir"] >= args.ir_thr)
        passes_fdr = item["passes_fdr"]
        
        attempt_record = {
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "raw_ic": item["raw_ic"],
            "overall_ic": item["overall_ic"],
            "p_value": item["p_value"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"],
            "passes_rolling_guard": bool(passes_guard),
            "passes_fdr": bool(passes_fdr),
            "verdict": "PENDING_ADMISSION"
        }
        
        if not passes_guard:
            attempt_record["verdict"] = "REJECTED_ROLLING_GUARD"
            attempts_log.append(attempt_record)
        elif not passes_fdr:
            attempt_record["verdict"] = "REJECTED_FDR_GATE"
            attempts_log.append(attempt_record)
        else:
            surviving_candidates.append(item)
            
    print(f"{len(surviving_candidates)} features survived rolling guard + FDR filter out of {len(features_to_eval)}.")

    # 6. Compute Data-Adaptive Simulation Threshold (empirical 95th percentile)
    print(f"Running multi-trial empirical null simulation for N={n_trials} trials...")
    max_ics = numba_multi_trial_empirical_sim(X_train, y_train, n_trials, tail_def, n_tail, 1000, block_size=10)
    empirical_95th = float(np.percentile(max_ics, 95))
    empirical_mean = float(np.mean(max_ics))
    print(f"Empirical 95th-percentile tail IC threshold: {empirical_95th:.4f}")
    print(f"Empirical mean max tail IC: {empirical_mean:.4f}")

    # 7. Admission Gate (A2)
    admitted_pool = []  # list of dicts

    for cand in surviving_candidates:
        cand_name = cand["feature_name"]
        cand_ic = cand["overall_ic"]
        x_cand = cand["x_flipped"]
        deflated_ic = max(0.0, cand_ic - empirical_mean)
        cand["deflated_ic"] = deflated_ic
        
        # Check overall IC >= empirical_95th admission gate
        if cand_ic < empirical_95th:
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "p_value": cand["p_value"],
                "deflated_ic": deflated_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
                "verdict": "REJECTED_ADMISSION_FLOOR"
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
                "p_value": cand["p_value"],
                "deflated_ic": deflated_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
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
                "p_value": cand["p_value"],
                "deflated_ic": deflated_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
                "max_corr": max_corr,
                "max_corr_feature": max_corr_feature,
                "verdict": "ADMITTED"
            })
        else:
            # Case 2: Max correlation exceeds threshold -> Check replacement rule
            high_corr_members = [item for item in corrs if item[1] >= args.theta]
            
            replaced = False
            if cand_ic >= 0.10 and len(high_corr_members) == 1:
                old_feature_name, _ = high_corr_members[0]
                old_idx = -1
                for idx, p in enumerate(admitted_pool):
                    if p["feature_name"] == old_feature_name:
                        old_idx = idx
                        break
                
                if old_idx != -1:
                    old_ic = admitted_pool[old_idx]["overall_ic"]
                    if cand_ic >= 1.3 * old_ic:
                        admitted_pool[old_idx] = cand
                        replaced = True
                        attempts_log.append({
                            "feature_name": cand_name,
                            "sign": cand["sign"],
                            "raw_ic": cand["raw_ic"],
                            "overall_ic": cand_ic,
                            "p_value": cand["p_value"],
                            "deflated_ic": deflated_ic,
                            "ic_ir": cand["ic_ir"],
                            "monotonicity": cand["monotonicity"],
                            "passes_rolling_guard": True,
                            "passes_fdr": True,
                            "max_corr": max_corr,
                            "max_corr_feature": max_corr_feature,
                            "verdict": f"ADMITTED_REPLACED_{old_feature_name}"
                        })
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
                    "p_value": cand["p_value"],
                    "deflated_ic": deflated_ic,
                    "ic_ir": cand["ic_ir"],
                    "monotonicity": cand["monotonicity"],
                    "passes_rolling_guard": True,
                    "passes_fdr": True,
                    "max_corr": max_corr,
                    "max_corr_feature": max_corr_feature,
                    "verdict": "REJECTED_REDUNDANCY"
                })

    print(f"Final admitted pool size: {len(admitted_pool)}")

    # Format the selected pool output
    selected_output = []
    for item in admitted_pool:
        record = {
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "overall_ic": item["overall_ic"],
            "deflated_ic": item["deflated_ic"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"]
        }
        if item["feature_name"] in candidate_recipes:
            record["recipe"] = candidate_recipes[item["feature_name"]]
        selected_output.append(record)

    # Save selected pool and attempts log to json files
    selected_path = data_out_dir / f"selected_pool_{args.etf}_{args.side}{suffix}.json"
    with open(selected_path, "w") as f:
        json.dump(selected_output, f, indent=2)
    print(f"Saved selected pool to {selected_path}")

    # Inject recipes into attempts log
    for att in attempts_log:
        feat_name = att.get("feature_name")
        if feat_name in candidate_recipes:
            att["recipe"] = candidate_recipes[feat_name]

    attempts_path = data_out_dir / f"mining_attempts_{args.etf}_{args.side}{suffix}.json"
    with open(attempts_path, "w") as f:
        json.dump(attempts_log, f, indent=2)
    print(f"Saved attempts log to {attempts_path}")
    print(f"================================================================================")

if __name__ == "__main__":
    main()
