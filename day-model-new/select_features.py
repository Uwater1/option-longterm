#!/usr/bin/env python3
"""
Stage A Feature Selection for Day-Model Rewrite v3.
Implements:
1. Flipping features to have positive overall training IC (date ranges adjusted dynamically per ETF).
2. A3 Rolling pre-filter (90-calendar-day rolling tail IC monotonicity & IR check).
2b. 7-Year Jackknife sign stability gate — reject if IC sign flips across training chunks (cheapest universal guard).
3. Light Benjamini-Hochberg FDR pre-filter gate at q = 0.20 using single-feature block-shuffled empirical null simulation.
4. Cumulative persistent ledger tracking of trial count N per (ETF, side).
5. Data-adaptive empirical 95th-percentile tail IC admission floor via multi-trial block-shuffled empirical null simulation.
6. Stage A2 Admission gate (correlation gate + replacement rule).
"""

import os
import sys
import json
import argparse
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from numba import njit, prange
from scipy.stats import rankdata
from joblib import Parallel, delayed

# Set up paths to import existing features list and recipe_utils
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))

from build_features import FEATURES
from mining.recipe_utils import simulate_returns

MAX_FLIPS = 1 # Cross-period test: MAX_FLIPS=1 creates systematic false negatives (OOS IC 0.08-0.11 rejected)
FDR_THRESHOLD = 0.20

# Feature Selection Global Constants (easily fine-tuned)
# B4 Correlation Gate: single threshold, only reject near-perfect duplicates.
# Diversity is enforced downstream by ONC clustering + newtrade group-constrained top-K.
DEFAULT_THETA = 0.95          # Near-duplicate correlation threshold (B4 gate)

# B2 Rolling Guard Defaults
MONO_THR_SINGLE = 0.65        # Rolling 90d monotonicity threshold for single side
MONO_THR_DIR = 0.60           # Rolling 90d monotonicity threshold for long/short sides
IR_THR_SINGLE = 0.30          # Rolling 90d IC_IR threshold for single side
IR_THR_DIR = 0.15             # Rolling 90d IC_IR threshold for long/short sides

# Temporal & Quality Gate Thresholds
MAX_RECENCY_RATIO = 2.5       # Cap recent_ic / early_ic to prune late-training overfit spikes
MAX_HALF_RATIO = 1.80          # Cap ic_second / early_ic to prune late-training half spikes 
MAX_EXTREME_RECENCY_RATIO = 4.0 # Universal cap for extreme recency spikes regardless of early IC
MAX_EXTREME_HALF_RATIO = 2.50   # Universal cap for extreme half-ratio spikes 
MIN_EARLY_IC_THRESHOLD = 0.03 # Minimum early IC to trigger recency ratio cap (prevents dividing by tiny early ICs)
MAX_YEARLY_IC_CV = 1.00       # Max coefficient of variation for yearly ICs (tuned: 1.15->1.00 to prune high-CV noise)
# MAX_WEAK_LINK_CV removed — combo ops stabilize noisy primitives; gate had 76-100% TP collateral
MIN_STABILITY_PRODUCT = 0.09  # Relaxed from 0.15: FILTER_DIAGNOSIS shows 0% precision, 90% TP collateral at 0.15
MAX_NEGATIVE_REGIMES = 1      # Max vol-quintile regimes with negative IC (>=2 = regime-conditional signal)
# Regime Uniformity Gate: catches "too good to be true" features that are suspiciously
# uniform across vol regimes AND have unstable yearly ICs (overfit signature).
# Conservative thresholds based on general principle: real signals have natural regime variance.
MIN_IC_STD_REGIMES = 0.030    # Min std of IC across vol regimes (below = suspiciously uniform)
MAX_IC_CV_FOR_UNIFORM = 0.85  # Max yearly IC CV to trigger uniformity check (above = unstable)

# Robustness Gate (A/B-validated in research_gate_ab_test.py, see plan.md):
# G7 Cost-stress: reject unless Sortino stays > 0 at COST_STRESS_MULT x cost
#    (A/B: FP-kill 14.7% admitted / 8.9% preb4 vs TP-kill 2.9% / 1.8%)
# G4 Bootstrap CI: reject if block-bootstrap Sortino lower bound <= 0
#    (A/B: FP-kill 15.2% admitted / 8.2% preb4 vs TP-kill 4.4% / 2.6%)
BOOT_B = 199               # Bootstrap resamples
BOOT_BLOCK = 10            # Moving-block bootstrap block length (days)
BOOT_CI_PCT = 5.0          # One-sided CI lower-bound percentile
COST_BASE = 0.0008         # 8 bps per active day — keep in sync with simulate_returns
COST_STRESS_MULT = 2.0     # G7 stress multiplier applied to COST_BASE
ANNUAL_DAYS = 244          # Trading days per year — keep in sync with simulate_returns
ROBUST_GATE_SEED = 42      # Bootstrap RNG seed (deterministic verdicts)

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


def _tail_positions_binary(y_true: np.ndarray, pred: np.ndarray, side: str) -> np.ndarray:
    """Binary tail positions mirroring simulate_returns (binary mode,
    enforce_absolute_sign=True), so Robustness Gate metrics match the
    Sortino already used by the Quality Gate."""
    n = len(pred)
    order = np.argsort(pred, kind="quicksort")
    pos = np.zeros(n, dtype=np.float64)
    if side == "long":
        n_tail = max(5, int(n * 0.15))
        idx = order[-n_tail:]
        if float(np.mean(y_true[idx])) > 0.0:
            pos[idx] = 1.0
    elif side == "short":
        n_tail = max(5, int(n * 0.15))
        idx = order[:n_tail]
        if float(np.mean(-y_true[idx])) > 0.0:
            pos[idx] = -1.0
    else:  # single: two-sided
        n_tail = max(5, int(n * 0.10))
        long_idx, short_idx = order[-n_tail:], order[:n_tail]
        if float(np.mean(y_true[long_idx])) > 0.0:
            pos[long_idx] = 1.0
        if float(np.mean(-y_true[short_idx])) > 0.0:
            pos[short_idx] = -1.0
    return pos


def _sortino_annual(returns: np.ndarray) -> float:
    """Annualized Sortino, formula identical to simulate_returns."""
    ann_ret = float(np.mean(returns) * ANNUAL_DAYS)
    down_vol = float(np.std(np.minimum(returns, 0.0)) * np.sqrt(ANNUAL_DAYS))
    return ann_ret / (down_vol + 1e-10)


def _bootstrap_sortino_ci(cost_ret: np.ndarray, rng) -> float:
    """BOOT_CI_PCT percentile of block-bootstrap Sortino (fully vectorized)."""
    T = len(cost_ret)
    nblocks = int(np.ceil(T / BOOT_BLOCK))
    starts = rng.integers(0, max(T - BOOT_BLOCK, 1), size=(BOOT_B, nblocks))
    offs = np.arange(BOOT_BLOCK)
    idx = (starts[:, :, None] + offs[None, None, :]) % T
    boot_mat = cost_ret[idx].reshape(BOOT_B, -1)[:, :T]
    ann = boot_mat.mean(axis=1) * ANNUAL_DAYS
    dvol = np.minimum(boot_mat, 0.0).std(axis=1) * np.sqrt(ANNUAL_DAYS)
    return float(np.percentile(ann / (dvol + 1e-10), BOOT_CI_PCT))


@njit(cache=True)
def fast_rankdata(a: np.ndarray) -> np.ndarray:
    n = len(a)
    ix = np.argsort(a)
    ranks = np.empty(n, dtype=np.float32)
    for i in range(n):
        ranks[ix[i]] = np.float32(i + 1.0)
    return ranks

@njit(cache=True)
def fast_spearman(a: np.ndarray, b: np.ndarray) -> float:
    n = len(a)
    if n < 5:
        return 0.0
    ra = fast_rankdata(a)
    rb = fast_rankdata(b)
    mean_ra = ra.sum() / n
    mean_rb = rb.sum() / n
    cov = np.float32(0.0)
    var_ra = np.float32(0.0)
    var_rb = np.float32(0.0)
    for i in range(n):
        diff_a = ra[i] - mean_ra
        diff_b = rb[i] - mean_rb
        cov += diff_a * diff_b
        var_ra += diff_a * diff_a
        var_rb += diff_b * diff_b
    denom = np.sqrt(var_ra * var_rb)
    if denom < 1e-12:
        return 0.0
    return float(cov / denom)

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
        out[t] = _tail_ic_from_sorted(ix, x_win, y_win, n_win, n_tail, tail_def)
        
    return out


@njit(cache=True)
def _tail_ic_from_sorted(ix: np.ndarray, x_flipped: np.ndarray, y_arr: np.ndarray, n: int, n_tail: int, tail_def: int) -> float:
    """Compute tail IC from pre-sorted indices. Shared helper."""
    if tail_def == 1:  # top
        x_tail = np.empty(n_tail, dtype=np.float32)
        y_tail = np.empty(n_tail, dtype=np.float32)
        for t in range(n_tail):
            idx = ix[n - n_tail + t]
            x_tail[t] = x_flipped[idx]
            y_tail[t] = y_arr[idx]
    elif tail_def == 2:  # bot
        x_tail = np.empty(n_tail, dtype=np.float32)
        y_tail = np.empty(n_tail, dtype=np.float32)
        for t in range(n_tail):
            idx = ix[t]
            x_tail[t] = x_flipped[idx]
            y_tail[t] = y_arr[idx]
    else:  # two-sided
        x_tail = np.empty(n_tail * 2, dtype=np.float32)
        y_tail = np.empty(n_tail * 2, dtype=np.float32)
        for t in range(n_tail):
            idx_bot = ix[t]
            x_tail[t] = x_flipped[idx_bot]
            y_tail[t] = y_arr[idx_bot]
            idx_top = ix[n - n_tail + t]
            x_tail[n_tail + t] = x_flipped[idx_top]
            y_tail[n_tail + t] = y_arr[idx_top]
    return fast_spearman(y_tail, x_tail)


def numba_single_trial_empirical_sim(X: np.ndarray, y: np.ndarray, tail_def: int, n_tail: int, n_sims: int, block_size=10) -> np.ndarray:
    """Parallel empirical single-trial null tail IC distribution (fp32, pre-generated RNG)."""
    n, n_features = X.shape
    X32 = X.astype(np.float32)
    y32 = y.astype(np.float32)

    # Pre-compute column means for sign-flip
    col_means = X32.mean(axis=0)

    # Pre-generate all random numbers (thread-safe: no RNG inside prange)
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = n - block_size + 1
    rng = np.random.default_rng(12345)
    all_starts = rng.integers(0, max(1, possible_starts), size=(n_sims, num_blocks)).astype(np.int32)
    all_feat_idx = rng.integers(0, n_features, size=n_sims).astype(np.int32)

    @njit(parallel=True, cache=True)
    def _kernel(X32, y32, col_means, all_starts, all_feat_idx, n_sims, n, n_features, n_tail, tail_def, block_size):
        null_ics = np.empty(n_sims, dtype=np.float64)
        y_mean = y32.sum() / n
        for s in prange(n_sims):
            # Block shuffle
            starts_s = all_starts[s]
            y_null = np.empty(n, dtype=np.float32)
            pos = 0
            for i in range(len(starts_s)):
                st = starts_s[i]
                for offset in range(block_size):
                    if pos < n:
                        y_null[pos] = y32[st + offset]
                        pos += 1
                    else:
                        break

            j = all_feat_idx[s]
            x = X32[:, j]

            # Pearson correlation for sign flip (using precomputed mean)
            mean_x = col_means[j]
            mean_y = y_null.sum() / n
            cov_xy = np.float32(0.0)
            var_x = np.float32(0.0)
            var_y = np.float32(0.0)
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
            sign = np.float32(1.0) if raw_corr >= 0.0 else np.float32(-1.0)
            x_flipped = x * sign

            ix = np.argsort(x_flipped)
            null_ics[s] = _tail_ic_from_sorted(ix, x_flipped, y_null, n, n_tail, tail_def)
        return null_ics

    return _kernel(X32, y32, col_means, all_starts, all_feat_idx, n_sims, n, n_features, n_tail, tail_def, block_size)

def numba_multi_trial_empirical_sim(X: np.ndarray, y: np.ndarray, n_trials: int, tail_def: int, n_tail: int, n_sims: int, block_size=10) -> np.ndarray:
    """Parallel empirical max tail IC distribution (fp32, pre-generated RNG, prange)."""
    n, n_features = X.shape
    X32 = X.astype(np.float32)
    y32 = y.astype(np.float32)

    # Pre-compute column means for sign-flip
    col_means = X32.mean(axis=0)

    # Pre-generate all random numbers outside parallel region (thread-safe)
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = n - block_size + 1
    rng = np.random.default_rng(54321)
    all_starts = rng.integers(0, max(1, possible_starts), size=(n_sims, num_blocks)).astype(np.int32)
    all_feat_idx = rng.integers(0, n_features, size=(n_sims, n_trials)).astype(np.int32)

    @njit(parallel=True, cache=True)
    def _kernel(X32, y32, col_means, all_starts, all_feat_idx, n_sims, n_trials, n, n_features, n_tail, tail_def, block_size):
        max_ics = np.empty(n_sims, dtype=np.float64)
        for s in prange(n_sims):
            # Block shuffle target
            starts_s = all_starts[s]
            y_null = np.empty(n, dtype=np.float32)
            pos = 0
            for i in range(len(starts_s)):
                st = starts_s[i]
                for offset in range(block_size):
                    if pos < n:
                        y_null[pos] = y32[st + offset]
                        pos += 1
                    else:
                        break

            mean_y = y_null.sum() / n
            max_ic = np.float64(-1e10)

            for i in range(n_trials):
                j = all_feat_idx[s, i]
                x = X32[:, j]

                # Pearson sign-flip with precomputed mean
                mean_x = col_means[j]
                cov_xy = np.float32(0.0)
                var_x = np.float32(0.0)
                var_y = np.float32(0.0)
                for k in range(n):
                    dx = x[k] - mean_x
                    dy = y_null[k] - mean_y
                    cov_xy += dx * dy
                    var_x += dx * dx
                    var_y += dy * dy
                if var_x < 1e-24 or var_y < 1e-24:
                    continue

                raw_corr = cov_xy / np.sqrt(var_x * var_y)
                sign = np.float32(1.0) if raw_corr >= 0.0 else np.float32(-1.0)
                x_flipped = x * sign

                ix = np.argsort(x_flipped)
                tail_ic = _tail_ic_from_sorted(ix, x_flipped, y_null, n, n_tail, tail_def)
                if tail_ic > max_ic:
                    max_ic = tail_ic

            max_ics[s] = max_ic
        return max_ics

    return _kernel(X32, y32, col_means, all_starts, all_feat_idx, n_sims, n_trials, n, n_features, n_tail, tail_def, block_size)


def benjamini_hochberg_fdr(p_values: np.ndarray, fdr_threshold=FDR_THRESHOLD, m_total: int = None) -> np.ndarray:
    """Apply standard Benjamini-Hochberg (BH-FDR) procedure.
    Returns a boolean mask of kept indices.
    
    Args:
        m_total: Total number of candidates tested (before pre-filtering).
                 If provided, uses this as rank denominator to account for full search space.
                 Defaults to len(p_values).
    """
    m_tested = len(p_values)
    if m_tested == 0:
        return np.array([], dtype=bool)
    m = m_total if m_total is not None and m_total > m_tested else m_tested
    
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]
    
    bh_val = (np.arange(1, m_tested + 1) / m) * fdr_threshold
    eligible = sorted_p <= bh_val
    
    mask = np.zeros(m_tested, dtype=bool)
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

def expanding_wf_sign_check(x_raw: np.ndarray, y: np.ndarray, side: str, max_flips: int = 2) -> tuple:
    """Yearly Jackknife sign stability check on RAW x.
    Splits training data into N equal chunks (one per ~calendar year, ~252 trading days).
    Computes tail IC per chunk, locks sign from full-sample IC.
    Counts 'flip chunks' where chunk IC sign disagrees with locked sign.
    Passes if flip_count <= max_flips.
    
    Returns (passes: bool, locked_sign: float, ic_first_half, ic_second_half, ic_recent).
    """
    n = len(y)
    n_years = max(1, round(n / 252))  # ~252 trading days per year
    n_chunks = max(3, n_years)        # at least 3 chunks
    chunk_size = n // n_chunks
    
    if chunk_size < 10:
        # Too few samples for 7 chunks, fall back to simple sign lock
        raw_ic = _spearman_from_arrays(x_raw, y)
        locked_sign = -1.0 if raw_ic < 0 else 1.0
        return True, locked_sign, 0.0, 0.0, 0.0

    # Lock sign from full-sample tail IC
    full_ic = compute_side_tail_ic(y, x_raw, side)
    locked_sign = 1.0 if full_ic >= 0 else -1.0

    # Sign consistency check: reject if full-sample linear IC is meaningful (|full_sample_ic| >= 0.015)
    # and its sign directly contradicts the locked tail IC sign.
    full_sample_ic = _spearman_from_arrays(x_raw, y)
    if abs(full_sample_ic) >= 0.015 and (full_sample_ic * full_ic) < 0:
        return False, locked_sign, 0.0, 0.0, 0.0

    # Compute per-chunk tail IC and count flips
    flip_count = 0
    chunk_ics = []
    for i in range(n_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < n_chunks - 1 else n
        if end - start < 10:
            continue
        chunk_ic = compute_side_tail_ic(y[start:end], x_raw[start:end], side)
        chunk_ics.append(chunk_ic)
        # Flip = chunk IC sign disagrees with locked sign
        if locked_sign > 0 and chunk_ic < 0:
            flip_count += 1
        elif locked_sign < 0 and chunk_ic > 0:
            flip_count += 1

    # Hard rule: last 2 chunks must NOT be flips (recent signal must be intact)
    n_valid = len(chunk_ics)
    recent_flips = 0
    if n_valid >= 2:
        for ic in chunk_ics[-2:]:
            if (locked_sign > 0 and ic < 0) or (locked_sign < 0 and ic > 0):
                recent_flips += 1
    
    passes = (flip_count <= max_flips) and (recent_flips == 0)
    
    # Return compatible interface: first-half IC, second-half IC, recent IC
    if n_valid >= 3:
        ic_first = float(np.mean(chunk_ics[:n_valid//2]))
        ic_second = float(np.mean(chunk_ics[n_valid//2:]))
        ic_recent = float(chunk_ics[-1])
    elif n_valid > 0:
        ic_first = float(chunk_ics[0])
        ic_second = float(chunk_ics[-1])
        ic_recent = float(chunk_ics[-1])
    else:
        ic_first = ic_second = ic_recent = 0.0

    return passes, locked_sign, ic_first, ic_second, ic_recent


def evaluate_single_feature(feature_name: str, x: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, side: str, max_flips: int = 2):
    """Evaluate a single candidate feature: cheap gates first to avoid wasting compute on rejected signals."""
    sh_passes, locked_sign, sh_ic_first, sh_ic_second, ic_f3 = expanding_wf_sign_check(x, y, side, max_flips=max_flips)
    
    x_flipped = x * locked_sign
    raw_ic = _spearman_from_arrays(x_flipped, y)
    overall_ic = compute_side_tail_ic(y, x_flipped, side)
    
    if not sh_passes:
        return {
            "feature_name": feature_name,
            "sign": int(locked_sign),
            "raw_ic": float(raw_ic),
            "overall_ic": float(overall_ic),
            "mean_tail_ic": 0.0,
            "std_tail_ic": 0.0,
            "ic_ir": 0.0,
            "monotonicity": 0.0,
            "sortino": 0.0,
            "composite_score": 0.0,
            "split_half_passes": False,
            "split_half_ic_first": sh_ic_first,
            "split_half_ic_second": sh_ic_second,
            "recent_ic": float(ic_f3),
            "x_flipped": x_flipped,
        }
        
    # B2 Compute rolling tail IC series using locked sign
    rolling_tail_ics = compute_rolling_tail_ic_series(x_flipped, y, window_starts, window_ends, side)
    
    mean_tail_ic = float(np.mean(rolling_tail_ics))  # RollingMono(90d)
    std_tail_ic = float(np.std(rolling_tail_ics))
    ic_ir = mean_tail_ic / (std_tail_ic + 1e-10)
    monotonicity = float(np.mean(rolling_tail_ics > 0))
    
    # Check B2 Rolling Guard thresholds
    mono_thr = MONO_THR_DIR if side in ["long", "short"] else MONO_THR_SINGLE
    ir_thr = IR_THR_DIR if side in ["long", "short"] else IR_THR_SINGLE
    passes_guard = (monotonicity >= mono_thr) and (ic_ir >= ir_thr)
    
    if not passes_guard:
        # B2 Fail: Return immediately! No single-candidate Sortino trade simulation needed.
        return {
            "feature_name": feature_name,
            "sign": int(locked_sign),
            "raw_ic": float(raw_ic),
            "overall_ic": float(overall_ic),
            "mean_tail_ic": mean_tail_ic,
            "std_tail_ic": std_tail_ic,
            "ic_ir": ic_ir,
            "monotonicity": monotonicity,
            "sortino": 0.0,
            "composite_score": 0.0,
            "split_half_passes": True,
            "passes_rolling_guard": False,
            "passes_abs_sign": False,
            "split_half_ic_first": sh_ic_first,
            "split_half_ic_second": sh_ic_second,
            "recent_ic": float(ic_f3),
            "x_flipped": x_flipped,
        }

    # Per-candidate Sortino trade simulation using locked sign (only for B1 + B2 survivors!)
    ann_ret, sharpe, sortino, max_dd, raw_ann_ret, raw_sharpe = simulate_returns(y, x_flipped, side)
    
    # Rank-normalized Composite Score (w=0.50 Sortino, calibrated for fixed null formula)
    composite_score = 0.3 * mean_tail_ic + 0.5 * sortino + 0.15 * abs(overall_ic) + 0.05 * abs(raw_ic)
    
    return {
        "feature_name": feature_name,
        "sign": int(locked_sign),
        "raw_ic": float(raw_ic),
        "overall_ic": float(overall_ic),
        "mean_tail_ic": mean_tail_ic,
        "std_tail_ic": std_tail_ic,
        "ic_ir": ic_ir,
        "monotonicity": monotonicity,
        "sortino": float(sortino),
        "composite_score": float(composite_score),
        "split_half_passes": True,
        "passes_rolling_guard": True,
        "passes_abs_sign": True,
        "split_half_ic_first": sh_ic_first,
        "split_half_ic_second": sh_ic_second,
        "recent_ic": float(ic_f3),
        "x_flipped": x_flipped,  # Keep for correlation gate
    }


@njit(cache=True)
def numba_fast_rolling_tail_ic(x: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, window_offsets: np.ndarray, window_sorted_idx: np.ndarray, tail_def: int, pct: float) -> float:
    n_days = len(window_starts)
    pos_count = 0
    valid_count = 0
    
    for t in range(n_days):
        start = window_starts[t]
        end = window_ends[t]
        n_win = end - start
        if n_win < 15:
            continue
        n_tail = max(5, int(n_win * pct))
        
        offset = window_offsets[t]
        ix_win = window_sorted_idx[offset:offset + n_win]
        x_win = x[start:end]
        y_win = y[start:end]
        
        ic = _tail_ic_from_sorted(ix_win, x_win, y_win, n_win, n_tail, tail_def)
        valid_count += 1
        if ic > 0:
            pos_count += 1
            
    return pos_count / (valid_count + 1e-10)

@njit(parallel=True, cache=True)
def numba_fast_null_composite_kernel(x_flipped: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, window_offsets: np.ndarray, window_sorted_idx: np.ndarray, ix_overall: np.ndarray, tail_idx: np.ndarray, is_two_sided: bool, long_idx: np.ndarray, short_idx: np.ndarray, tail_def: int, pct: float, all_starts: np.ndarray, block_size: int, n_sims: int) -> np.ndarray:
    n = len(y)
    null_scores = np.empty(n_sims, dtype=np.float64)
    n_tail = len(tail_idx) if not is_two_sided else len(long_idx)
    
    for s in prange(n_sims):
        # Block shuffle
        starts_s = all_starts[s]
        y_null = np.empty(n, dtype=np.float32)
        pos = 0
        for i in range(len(starts_s)):
            st = starts_s[i]
            for offset in range(block_size):
                if pos < n:
                    y_null[pos] = y[st + offset]
                    pos += 1
                else:
                    break
                    
        # Spearman overall IC
        raw_ic_null = fast_spearman(y_null, x_flipped)
        
        # Overall Tail IC
        tail_ic_null = _tail_ic_from_sorted(ix_overall, x_flipped, y_null, n, n_tail, tail_def)
        
        # Rolling Mono
        mono_null = numba_fast_rolling_tail_ic(x_flipped, y_null, window_starts, window_ends, window_offsets, window_sorted_idx, tail_def, pct)
        
        # Sortino
        if not is_two_sided:
            ret = np.empty(n_tail, dtype=np.float32)
            for k in range(n_tail):
                idx = tail_idx[k]
                ret[k] = y_null[idx] - 0.0008 if tail_def == 1 else -y_null[idx] - 0.0008
            
            sum_ret = 0.0
            sum_sq_down = 0.0
            for k in range(n_tail):
                r = ret[k]
                sum_ret += r
                if r < 0:
                    sum_sq_down += r * r
            ann_ret = (sum_ret / n_tail) * 244.0
            down_std = np.sqrt(sum_sq_down / n) * 15.620499351813308  # Fixed: use n denominator (aligned with simulate_returns)
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
            down_std = np.sqrt(sum_sq_down / n) * 15.620499351813308  # Fixed: use n denominator
            sortino_null = ann_ret / (down_std + 1e-10)
            
        null_scores[s] = 0.3 * mono_null + 0.5 * sortino_null + 0.15 * abs(tail_ic_null) + 0.05 * abs(raw_ic_null)
        
    return null_scores


@njit(parallel=True, cache=True)
def numba_batched_b3_null_kernel(X: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, all_starts: np.ndarray, tail_def: int, pct: float, n_tail: int, block_size: int, n_sims: int):
    """Batched B3 composite null over all candidates. prange over candidates.

    Returns (out_95, out_99, out_mean, out_ic_mean): each shape (n_cands,).
    Shared y-shuffle starts across candidates for efficiency.
    """
    n, n_cands = X.shape
    n_days = len(window_starts)
    num_blocks = all_starts.shape[1]
    y32 = y.astype(np.float32)
    is_two_sided = (tail_def == 3)

    out_p93 = np.empty(n_cands, dtype=np.float64)
    out_p97 = np.empty(n_cands, dtype=np.float64)
    out_mean = np.empty(n_cands, dtype=np.float64)
    out_ic_mean = np.empty(n_cands, dtype=np.float64)

    for c in prange(n_cands):
        x = X[:, c]

        # Per-candidate precompute: overall sorted index, window sorted indices
        ix_overall = np.argsort(x)
        if tail_def == 1:  # long
            long_idx = ix_overall[n - n_tail:]
            short_idx = np.empty(0, dtype=np.int64)
        elif tail_def == 2:  # short
            short_idx = ix_overall[:n_tail]
            long_idx = np.empty(0, dtype=np.int64)
        else:  # single (two-sided)
            long_idx = ix_overall[n - n_tail:]
            short_idx = ix_overall[:n_tail]

        # Rolling window offsets and packed sorted indices
        window_offsets = np.empty(n_days, dtype=np.int32)
        total_size = 0
        for t in range(n_days):
            window_offsets[t] = total_size
            total_size += window_ends[t] - window_starts[t]
        window_sorted_idx = np.empty(total_size, dtype=np.int32)
        for t in range(n_days):
            st = window_starts[t]
            en = window_ends[t]
            offset = window_offsets[t]
            x_win = x[st:en]
            ix = np.argsort(x_win)
            for k in range(len(ix)):
                window_sorted_idx[offset + k] = ix[k]

        # Sortino tail indices (which to use depends on side)
        if tail_def == 1:
            tail_idx_local = long_idx
        elif tail_def == 2:
            tail_idx_local = short_idx
        else:
            tail_idx_local = long_idx  # placeholder, two-sided uses both below

        null_scores_local = np.empty(n_sims, dtype=np.float64)
        raw_ic_sum = 0.0

        for s in range(n_sims):
            # Block shuffle (shared starts across candidates)
            y_null = np.empty(n, dtype=np.float32)
            pos = 0
            starts_s = all_starts[s]
            for i in range(num_blocks):
                st = starts_s[i]
                for offset in range(block_size):
                    if pos < n:
                        y_null[pos] = y32[st + offset]
                        pos += 1
                    else:
                        break

            # Composite components
            raw_ic_null = fast_spearman(y_null, x)
            raw_ic_sum += raw_ic_null
            tail_ic_null = _tail_ic_from_sorted(ix_overall, x, y_null, n, n_tail, tail_def)
            mono_null = numba_fast_rolling_tail_ic(x, y_null, window_starts, window_ends, window_offsets, window_sorted_idx, tail_def, pct)

            # Sortino
            if not is_two_sided:
                m = n_tail
                sum_ret = 0.0
                sum_sq_down = 0.0
                if tail_def == 1:
                    for k in range(m):
                        r = y_null[tail_idx_local[k]] - 0.0008
                        sum_ret += r
                        if r < 0:
                            sum_sq_down += r * r
                else:
                    for k in range(m):
                        r = -y_null[tail_idx_local[k]] - 0.0008
                        sum_ret += r
                        if r < 0:
                            sum_sq_down += r * r
                ann_ret = (sum_ret / m) * 244.0
                down_std = np.sqrt(sum_sq_down / n) * 15.620499351813308  # Fixed: use n denominator
                sortino_null = ann_ret / (down_std + 1e-10)
            else:
                n_l = len(long_idx)
                n_s_ = len(short_idx)
                total_cnt = n_l + n_s_
                sum_ret = 0.0
                sum_sq_down = 0.0
                for k in range(n_l):
                    r = y_null[long_idx[k]] - 0.0008
                    sum_ret += r
                    if r < 0:
                        sum_sq_down += r * r
                for k in range(n_s_):
                    r = -y_null[short_idx[k]] - 0.0008
                    sum_ret += r
                    if r < 0:
                        sum_sq_down += r * r
                ann_ret = (sum_ret / total_cnt) * 244.0
                down_std = np.sqrt(sum_sq_down / n) * 15.620499351813308  # Fixed: use n denominator
                sortino_null = ann_ret / (down_std + 1e-10)

            null_scores_local[s] = 0.3 * mono_null + 0.5 * sortino_null + 0.15 * abs(tail_ic_null) + 0.05 * abs(raw_ic_null)

        # 93rd and 97th percentile via partial sort (calibrated for fixed Sortino formula)
        null_scores_local.sort()
        idx_93 = int(0.93 * n_sims)
        if idx_93 >= n_sims:
            idx_93 = n_sims - 1
        idx_97 = int(0.97 * n_sims)
        if idx_97 >= n_sims:
            idx_97 = n_sims - 1
        out_p93[c] = null_scores_local[idx_93]
        out_p97[c] = null_scores_local[idx_97]
        s_sum = 0.0
        for k in range(n_sims):
            s_sum += null_scores_local[k]
        out_mean[c] = s_sum / n_sims
        out_ic_mean[c] = raw_ic_sum / n_sims

    return out_p93, out_p97, out_mean, out_ic_mean


def compute_batched_candidate_nulls(X_survivors_flipped: np.ndarray, y: np.ndarray, window_starts: np.ndarray, window_ends: np.ndarray, side: str, n_sims: int = 500, block_size: int = 10):
    """Run B3 composite null simulation for ALL surviving candidates in a single batched kernel call.

    Replaces the Parallel(n_jobs)(delayed(compute_candidate_null_composite)...) pattern.
    Uses shared y-shuffle indices across candidates and a single prange over candidates.
    """
    n = len(y)
    n_cands = X_survivors_flipped.shape[1]
    if n_cands == 0:
        return np.array([]), np.array([]), np.array([]), np.array([])

    X32 = X_survivors_flipped.astype(np.float32, copy=False)
    y32 = y.astype(np.float32, copy=False)

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

    # Shared y-shuffle starts across all candidates (deterministic seed for reproducibility)
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = max(1, n - block_size + 1)
    rng = np.random.default_rng(42)
    all_starts = rng.integers(0, possible_starts, size=(n_sims, num_blocks)).astype(np.int32)

    out_p93, out_p97, out_mean, out_ic_mean = numba_batched_b3_null_kernel(
        X32, y32, window_starts, window_ends, all_starts,
        tail_def, pct, n_tail, block_size, n_sims,
    )
    return out_p93, out_p97, out_mean, out_ic_mean

# NOTE: Adaptive Boundary Gate (gate 9) removed.
# Pool size is now unconstrained. Diversity is enforced downstream by
# ONC clustering (feature_clusters.py) + newtrade group-constrained top-K selection.

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", required=True, choices=["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"])
    parser.add_argument("-s", "--side", required=True, choices=["single", "long", "short"])
    parser.add_argument("--theta", type=float, default=DEFAULT_THETA, help="Max absolute correlation threshold (near-duplicate rejection)")
    parser.add_argument("--mono-thr", type=float, default=None, help="Rolling tail IC positivity threshold (monotonicity)")
    parser.add_argument("--ir-thr", type=float, default=None, help="Rolling tail IC Information Ratio threshold")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    parser.add_argument("--n-jobs", type=int, default=-1, help="Parallel workers")
    parser.add_argument("--train-start", type=str, default=None, help="Override training start date (YYYY-MM-DD)")
    parser.add_argument("--train-end", type=str, default=None, help="Override training end date (YYYY-MM-DD)")
    parser.add_argument("--period-suffix", type=str, default=None, help="Output file suffix for multi-period runs (e.g., _p2015_2023)")
    args = parser.parse_args()

    # Dynamic defaults based on side
    if args.mono_thr is None:
        args.mono_thr = MONO_THR_DIR if args.side in ["long", "short"] else MONO_THR_SINGLE
    if args.ir_thr is None:
        args.ir_thr = IR_THR_DIR if args.side in ["long", "short"] else IR_THR_SINGLE

    # Determine dynamic training start and end dates
    if args.train_start and args.train_end:
        train_start = pd.Timestamp(args.train_start)
        train_end = pd.Timestamp(args.train_end)
        args.max_flips = MAX_FLIPS
    elif args.etf == "588000ETF":
        train_start = pd.Timestamp("2020-11-01")
        train_end = pd.Timestamp("2025-01-01")
        args.max_flips = 1
    else:
        train_start = pd.Timestamp("2014-01-01")
        train_end = pd.Timestamp("2022-01-01")
        args.max_flips = MAX_FLIPS

    print(f"================================================================================")
    print(f"Stage A Feature Selection: ETF={args.etf}, Side={args.side}, Early={args.early}")
    print(f"Training Range: {train_start.date()} to {train_end.date()}")
    print(f"Params: theta={args.theta}, mono_thr={args.mono_thr}, ir_thr={args.ir_thr}, max_flips={args.max_flips}")
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

    # Load and compute candidate recipes dynamically (vectorized batch + parquet cache)
    from recipe_utils import compute_recipe
    
    suffix = args.period_suffix or ("_early" if args.early else "")
    cand_suffix = "_early" if args.early else ""
    candidates_path = HERE / "mining" / f"candidates_{args.etf}_{args.side}{suffix}.json"
    if not candidates_path.exists():
        candidates_path = HERE / "mining" / f"candidates_{args.etf}_{args.side}{cand_suffix}.json"
    candidate_recipes = {}
    features_to_eval = list(FEATURES)
    
    # Compute data fingerprint for cache invalidation (detects data updates even if row count unchanged)
    data_fingerprint = hashlib.md5(
        pd.util.hash_pandas_object(train_df[FEATURES].head(50), index=False).values.tobytes()
    ).hexdigest()[:16]

    # Recipe parquet cache: skip recomputation if candidates file AND data unchanged
    data_out_dir = HERE / "data"
    recipe_cache_path = data_out_dir / f"recipe_cache_{args.etf}_{args.side}{suffix}.parquet"
    recipe_meta_path = data_out_dir / f"recipe_cache_{args.etf}_{args.side}{suffix}.meta.json"
    
    if candidates_path.exists():
        # Compute hash of candidates file for cache invalidation
        cand_hash = hashlib.md5(candidates_path.read_bytes()).hexdigest()
        
        # Check if cache is valid (requires both candidates hash AND data fingerprint match)
        cache_valid = False
        if recipe_cache_path.exists() and recipe_meta_path.exists():
            try:
                with open(recipe_meta_path, "r") as f:
                    meta = json.load(f)
                if meta.get("hash") == cand_hash and meta.get("n_rows") == len(X_df) and meta.get("data_fp") == data_fingerprint:
                    cache_valid = True
            except Exception:
                pass
        
        if cache_valid:
            # Load cached recipe columns
            print(f"Loading cached recipe columns from {recipe_cache_path.name}")
            cached_df = pd.read_parquet(recipe_cache_path)
            recipe_feature_names = [c for c in cached_df.columns if c.startswith("combo_")]
            # Fast path: pd.concat is O(1) vs O(N_cols) for column-by-column assignment
            cached_subset = cached_df[recipe_feature_names]
            X_df = pd.concat([X_df, cached_subset], axis=1, copy=False)
            features_to_eval.extend(recipe_feature_names)
            # Reload candidate_recipes from candidates file (needed for output)
            with open(candidates_path, "r") as f:
                cands = json.load(f)
            cand_set = set(recipe_feature_names)
            for item in cands:
                if item["feature_name"] in cand_set:
                    candidate_recipes[item["feature_name"]] = item["recipe"]
            print(f"Cache hit: {len(recipe_feature_names)} recipe columns loaded.")
        else:
            # Compute recipes from scratch
            try:
                with open(candidates_path, "r") as f:
                    cands = json.load(f)
                print(f"Loaded {len(cands)} candidate combinations from {candidates_path.name}")
                
                # Pre-extract standardized columns once for batch recipe computation
                from recipe_utils import build_ecdf_grid_float32, fast_ecdf_interp_float32
                _std_cache = {}  # col_name -> standardized numpy array
                _rank_cache = {}  # col_name -> rank array
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
                        val32 = X_df[col_name].values.astype(np.float32)
                        xp, fp = build_ecdf_grid_float32(val32, n_knots=128)
                        _rank_cache[col_name] = fast_ecdf_interp_float32(val32, xp, fp).astype(np.float64)
                    return _rank_cache[col_name]
                
                def _compute_recipe_fast(recipe):
                    """Vectorized recipe computation using cached standardized columns."""
                    op = recipe["op"]
                    if op == "min":
                        return np.minimum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]))
                    elif op == "max":
                        return np.maximum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]))
                    elif op == "diff":
                        return _get_std_col_fast(recipe["feature_a"]) - _get_std_col_fast(recipe["feature_b"])
                    elif op == "ratio":
                        a_val = X_df[recipe["feature_a"]].values.astype(np.float64)
                        b_val = X_df[recipe["feature_b"]].values.astype(np.float64)
                        return a_val / (np.abs(b_val) + 1e-5)
                    elif op == "ifelse":
                        cond_val = X_df[recipe["feature_cond"]].values.astype(np.float64)
                        thresh = np.nanmedian(cond_val)
                        return np.where(cond_val > thresh, _get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"]))
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
                    elif op == "clamp_diff":
                        return np.clip(_get_std_col_fast(recipe["feature_a"]) - _get_std_col_fast(recipe["feature_b"]), -2.0, 2.0)
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
                    elif op == "tri_mean":
                        return (_get_std_col_fast(recipe["feature_a"]) + _get_std_col_fast(recipe["feature_b"]) + _get_std_col_fast(recipe["feature_c"])) / 3.0
                    elif op == "tri_z_mean":
                        return (_get_std_col_fast(recipe["feature_a"]) + _get_std_col_fast(recipe["feature_b"]) + _get_std_col_fast(recipe["feature_c"])) / 3.0
                    elif op == "tri_sig_max":
                        a_std = _get_std_col_fast(recipe["feature_a"])
                        b_std = _get_std_col_fast(recipe["feature_b"])
                        c_std = _get_std_col_fast(recipe["feature_c"])
                        return np.maximum(a_std * np.sign(c_std), b_std * np.sign(c_std))
                    elif op == "tri_min":
                        return np.minimum(np.minimum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"])), _get_std_col_fast(recipe["feature_c"]))
                    elif op == "tri_max":
                        return np.maximum(np.maximum(_get_std_col_fast(recipe["feature_a"]), _get_std_col_fast(recipe["feature_b"])), _get_std_col_fast(recipe["feature_c"]))
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
                
                n_failed = 0
                batch_values = {}  # feat_name -> numpy array (collected, then assigned in one shot)
                for item in cands:
                    feat_name = item["feature_name"]
                    recipe = item["recipe"]
                    try:
                        candidate_values = _compute_recipe_fast(recipe)
                        batch_values[feat_name] = candidate_values
                        features_to_eval.append(feat_name)
                        candidate_recipes[feat_name] = recipe
                    except Exception as e:
                        n_failed += 1
                        if n_failed <= 3:
                            print(f"WARNING: Failed to compute recipe for {feat_name}: {e}")
                if n_failed > 3:
                    print(f"WARNING: {n_failed} recipes failed total.")
                # Batch-assign all recipe columns at once (much faster than per-column X_df[c] = ...)
                if batch_values:
                    X_df = pd.concat([X_df, pd.DataFrame(batch_values, index=X_df.index)], axis=1, copy=False)
                
                # Save recipe cache for future runs
                recipe_cols = [c for c in X_df.columns if c.startswith("combo_")]
                if recipe_cols:
                    try:
                        X_df[recipe_cols].to_parquet(recipe_cache_path, index=False)
                        with open(recipe_meta_path, "w") as f:
                            json.dump({"hash": cand_hash, "n_rows": len(X_df), "n_recipes": len(recipe_cols), "data_fp": data_fingerprint}, f)
                        print(f"Saved recipe cache ({len(recipe_cols)} columns) to {recipe_cache_path.name}")
                    except Exception as e:
                        print(f"WARNING: Could not save recipe cache: {e}")
            except Exception as e:
                print(f"WARNING: Failed to load candidate recipes: {e}")
    else:
        print(f"No candidate combinations file found at {candidates_path}. Evaluating base features only.")

    X_train = X_df[features_to_eval].values.astype(np.float64)

    # Precompute rolling window indices (90 calendar days) — vectorized
    dates_np = dates_train.values.astype('datetime64[D]')
    start_dates = dates_np - np.timedelta64(90, 'D')
    window_starts = np.searchsorted(dates_np, start_dates).astype(np.int32)
    window_ends = np.arange(1, len(dates_train) + 1, dtype=np.int32)

    # 2. Evaluate all features in parallel (fp32 for speed)
    print(f"Evaluating {len(features_to_eval)} features on training set...")
    X_train_f32 = X_train.astype(np.float32)
    y_train_f32 = y_train.astype(np.float32)
    eval_results = Parallel(n_jobs=args.n_jobs)(
        delayed(evaluate_single_feature)(
            features_to_eval[i], X_train_f32[:, i], y_train_f32, window_starts, window_ends, args.side, args.max_flips
        ) for i in range(len(features_to_eval))
    )

    # Sort results by overall IC descending (strongest candidate first)
    eval_results.sort(key=lambda item: item["overall_ic"], reverse=True)

    # 3. Persistent Cumulative Trial Ledger with robust attempts-log seeding
    os.makedirs(data_out_dir, exist_ok=True)
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

    # 3b. 7-Year Jackknife sign stability gate (Step 2.2 — before expensive simulation)
    stable_results = []
    split_half_rejects = []
    for item in eval_results:
        if item["split_half_passes"]:
            stable_results.append(item)
        else:
            split_half_rejects.append(item)

    if split_half_rejects:
        print(f"7-Year Jackknife sign stability: rejected {len(split_half_rejects)} / {len(eval_results)} features (sign disagrees across chunks).")
    else:
        print(f"7-Year Jackknife sign stability: all {len(eval_results)} features passed.")

    # 3c. B2 Rolling Guard filter (instant check on pre-computed monotonicity & IR)
    guard_survivors = []
    guard_rejects = []
    for item in stable_results:
        passes_guard = (item["monotonicity"] >= args.mono_thr) and (item["ic_ir"] >= args.ir_thr)
        if not passes_guard:
            item["passes_rolling_guard"] = False
            guard_rejects.append(item)
        else:
            item["passes_rolling_guard"] = True
            guard_survivors.append(item)

    print(f"B2 Rolling Guard: {len(guard_survivors)} / {len(stable_results)} candidates passed (dropped {len(guard_rejects)} guard).")

    # 3d. Temporal Validation Gate: require positive tail IC in recent training AND cap recency_ratio & half_ratio
    # This catches features whose signal decayed or was artificially concentrated in late training.
    temporal_survivors = []
    temporal_rejects = []
    for item in guard_survivors:
        recent_ic = item.get("recent_ic", 0.0)
        ic_first = item.get("split_half_ic_first", 0.0)
        ic_second = item.get("split_half_ic_second", 0.0)
        denom = abs(ic_first) + 1e-4
        recency_ratio = recent_ic / denom
        half_ratio = ic_second / denom
        item["recency_ratio"] = float(recency_ratio)
        item["half_ratio"] = float(half_ratio)

        # Pass if recent IC > 0 AND signal is not excessively concentrated in late training
        is_extreme_spike = (recency_ratio >= MAX_EXTREME_RECENCY_RATIO) or (half_ratio >= MAX_EXTREME_HALF_RATIO)
        is_moderate_spike = (abs(ic_first) < MIN_EARLY_IC_THRESHOLD) and ((recency_ratio >= MAX_RECENCY_RATIO) or (half_ratio >= MAX_HALF_RATIO))
        is_late_spike = is_extreme_spike or is_moderate_spike
        passes_temporal = (recent_ic > 0.0) and (not is_late_spike)
        if passes_temporal:
            temporal_survivors.append(item)
        else:
            item["passes_temporal_gate"] = False
            temporal_rejects.append(item)

    if temporal_rejects:
        print(f"Temporal Validation Gate (recent IC > 0 & recency_ratio < {MAX_RECENCY_RATIO} & half_ratio < {MAX_HALF_RATIO}): rejected {len(temporal_rejects)} / {len(guard_survivors)} candidates (signal decayed or late-concentrated).")
    else:
        print(f"Temporal Validation Gate: all {len(guard_survivors)} candidates passed.")
    guard_survivors = temporal_survivors

    # Log temporal gate rejects (deferred to attempts_log assembly below)
    temporal_reject_items = temporal_rejects

    # 4. Light Benjamini-Hochberg FDR Pre-Filter Gate (runs ONLY on B2 survivors)
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
    
    # Pre-cache BH-FDR single-feature empirical null distribution
    fdr_cache_path = data_out_dir / f"fdr_null_{args.etf}_{args.side}{suffix}.json"
    fdr_cache_valid = False
    if fdr_cache_path.exists():
        try:
            with open(fdr_cache_path, "r") as f:
                fdr_cache = json.load(f)
            if fdr_cache.get("n_rows") == len(y_train) and fdr_cache.get("data_fp") == data_fingerprint:
                null_single_ics = np.array(fdr_cache["null_single_ics"], dtype=np.float64)
                fdr_cache_valid = True
                print(f"BH-FDR single-trial null cache hit (shape: {null_single_ics.shape})")
        except Exception:
            pass

    if not fdr_cache_valid:
        print(f"Running single-trial empirical null simulation for BH-FDR pre-filter ({len(guard_survivors)} candidates)...")
        if guard_survivors:
            X_survivors = np.column_stack([item["x_flipped"] for item in guard_survivors])
        else:
            X_survivors = X_train
        null_single_ics = numba_single_trial_empirical_sim(X_survivors, y_train, tail_def, n_tail, 5000, block_size=10)
        try:
            with open(fdr_cache_path, "w") as f:
                json.dump({"n_rows": len(y_train), "data_fp": data_fingerprint, "null_single_ics": null_single_ics.tolist()}, f)
            print(f"Saved BH-FDR null cache to {fdr_cache_path.name}")
        except Exception as e:
            print(f"WARNING: Could not save FDR null cache to {fdr_cache_path}: {e}")

    # Compute empirical p-value for each B2 survivor
    for item in guard_survivors:
        item["p_value"] = float(np.mean(null_single_ics >= item["overall_ic"]))
        
    # Apply Benjamini-Hochberg FDR procedure (corrected for full search space)
    p_values = np.array([item["p_value"] for item in guard_survivors]) if guard_survivors else np.array([])
    m_total_search_space = len(eval_results)  # total candidates before any filtering
    bh_mask = benjamini_hochberg_fdr(p_values, fdr_threshold=FDR_THRESHOLD, m_total=m_total_search_space) if len(p_values) > 0 else np.array([])
    
    surviving_candidates = []
    fdr_rejects = []
    for idx, item in enumerate(guard_survivors):
        passes_fdr = bool(bh_mask[idx])
        item["passes_fdr"] = passes_fdr
        if passes_fdr:
            surviving_candidates.append(item)
        else:
            fdr_rejects.append(item)

    # 5. Log all attempts
    attempts_log = []

    # Log 7-year jackknife rejects
    for item in split_half_rejects:
        attempts_log.append({
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "raw_ic": item["raw_ic"],
            "overall_ic": item["overall_ic"],
            "split_half_ic_first": item["split_half_ic_first"],
            "split_half_ic_second": item["split_half_ic_second"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"],
            "passes_split_half": False,
            "verdict": "REJECTED_SPLIT_HALF"
        })

    # Log rolling guard rejects
    for item in guard_rejects:
        attempts_log.append({
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "raw_ic": item["raw_ic"],
            "overall_ic": item["overall_ic"],
            "mean_tail_ic": item["mean_tail_ic"],
            "sortino": item["sortino"],
            "composite_score": item["composite_score"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"],
            "split_half_ic_first": item["split_half_ic_first"],
            "split_half_ic_second": item["split_half_ic_second"],
            "passes_split_half": True,
            "passes_rolling_guard": False,
            "passes_fdr": False,
            "verdict": "REJECTED_ROLLING_GUARD"
        })

    # Log temporal validation gate rejects
    for item in temporal_reject_items:
        attempts_log.append({
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "raw_ic": item["raw_ic"],
            "overall_ic": item["overall_ic"],
            "mean_tail_ic": item["mean_tail_ic"],
            "sortino": item["sortino"],
            "composite_score": item["composite_score"],
            "recent_ic": item.get("recent_ic", 0.0),
            "recency_ratio": item.get("recency_ratio", 0.0),
            "half_ratio": item.get("half_ratio", 0.0),
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"],
            "passes_split_half": True,
            "passes_rolling_guard": True,
            "passes_temporal_gate": False,
            "verdict": "REJECTED_TEMPORAL"
        })

    # Log FDR rejects
    for item in fdr_rejects:
        attempts_log.append({
            "feature_name": item["feature_name"],
            "sign": item["sign"],
            "raw_ic": item["raw_ic"],
            "overall_ic": item["overall_ic"],
            "mean_tail_ic": item["mean_tail_ic"],
            "sortino": item["sortino"],
            "composite_score": item["composite_score"],
            "p_value": item["p_value"],
            "ic_ir": item["ic_ir"],
            "monotonicity": item["monotonicity"],
            "split_half_ic_first": item["split_half_ic_first"],
            "split_half_ic_second": item["split_half_ic_second"],
            "passes_split_half": True,
            "passes_rolling_guard": True,
            "passes_fdr": False,
            "verdict": "REJECTED_FDR_GATE"
        })

    print(f"{len(surviving_candidates)} features survived 7-year jackknife + rolling guard + FDR out of {len(features_to_eval)}.")

    # 6. Compute Data-Adaptive Composite Score Threshold (empirical 93rd/97th percentile)
    if surviving_candidates:
        print(f"Running batched composite null simulations for {len(surviving_candidates)} candidates (n_sims=500)...")
        X_survivors_batch = np.column_stack([cand["x_flipped"] for cand in surviving_candidates]).astype(np.float32)
        emp_p93_arr, emp_p97_arr, emp_mean_arr, ic_null_mean_arr = compute_batched_candidate_nulls(
            X_survivors_batch, y_train, window_starts, window_ends, args.side, n_sims=500, block_size=10
        )
        for idx, cand in enumerate(surviving_candidates):
            cand["empirical_p93"] = float(emp_p93_arr[idx])
            cand["empirical_p97"] = float(emp_p97_arr[idx])
            cand["empirical_mean"] = float(emp_mean_arr[idx])
            cand["ic_null_mean"] = float(ic_null_mean_arr[idx])
            cand["deflated_ic"] = max(0.0, cand["overall_ic"] - cand["ic_null_mean"])

        # Helper function for unified composite Quality Score (q_score)
        def compute_q_score(item_dict):
            """Compute recalibrated composite Quality Score (q_score) for feature candidate.
            
            Weights: 50% Deflated IC + 25% Sortino + 15% Recent IC + 10% IC IR - Penalties (capped).
            Penalties:
              - complexity_penalty: 0.03 for combo_tri_, 0.01 for combo_
              - cv_penalty: 0.02 * max(0.0, ic_cv - 0.50) if ic_cv is present
              - half_penalty: 0.02 * abs(half_val - 1.0) if half_ratio present, else 0.0
            Total penalty drag is capped at 0.03 to avoid drowning out primary Deflated IC signal.
            """
            fname = item_dict.get("feature_name", "")
            def_ic = max(0.0, item_dict.get("deflated_ic", item_dict.get("overall_ic", 0.0)))
            sortino_val = max(0.0, item_dict.get("sortino", 0.0))
            ic_ir_val = max(0.0, item_dict.get("ic_ir", 0.0))
            recent_val = max(0.0, item_dict.get("recent_ic", item_dict.get("overall_ic", 0.0)))

            if "half_ratio" in item_dict:
                half_val = item_dict["half_ratio"]
            else:
                ic_first = item_dict.get("split_half_ic_first", 0.0)
                if abs(ic_first) > 1e-4:
                    half_val = item_dict.get("split_half_ic_second", 0.0) / (abs(ic_first) + 1e-4)
                else:
                    half_val = 1.0  # fallback to neutral ratio (0 penalty)

            cv_val = item_dict.get("ic_cv")

            is_tri = fname.startswith("combo_tri_")
            is_combo = fname.startswith("combo_")
            complexity_penalty = 0.03 if is_tri else (0.01 if is_combo else 0.0)

            cv_penalty = 0.02 * max(0.0, cv_val - 0.50) if cv_val is not None else 0.0
            half_penalty = 0.02 * abs(half_val - 1.0)

            total_penalty = min(0.03, cv_penalty + half_penalty + complexity_penalty)

            return (
                0.50 * def_ic +
                0.25 * sortino_val +
                0.15 * recent_val +
                0.10 * ic_ir_val -
                total_penalty
            )

        # Re-sort surviving candidates by initial q_score descending so highest quality enters B4 first
        for cand in surviving_candidates:
            cand["q_score_init"] = compute_q_score(cand)

        surviving_candidates.sort(key=lambda item: item["q_score_init"], reverse=True)

    # 7. Admission Gate (B3 Composite Floor + Stability Gate + Quality Gate + B4 Correlation Gate & Replacement Rule)
    # Quality Gate runs BEFORE correlation to prevent low-quality features from blocking high-quality ones.
    SYMMETRIC_OPS = {"max", "min", "mean", "rank_max", "rank_min"}
    n_train = len(y_train)
    min_deflated_ic = 0.05 if n_train < 1200 else 0.03  # stricter for 588000ETF (~1000 rows)
    min_raw_ic = 0.03 if n_train < 1200 else 0.02  # catch tail-only mirages
    admitted_pool = []  # list of dicts

    # Pre-compute yearly IC decomposition for temporal stability gate (P1)
    dates_years = pd.DatetimeIndex(dates_train.values).year.values
    unique_years = sorted(set(dates_years))

    # Pre-compute vol20 regime masks for negative-regime gate
    _vol20 = pd.Series(y_train).rolling(20).std().values
    _vol_valid = ~np.isnan(_vol20)
    if _vol_valid.sum() >= 100:
        _vol_pcts = np.percentile(_vol20[_vol_valid], [20, 40, 60, 80])
        _regime_masks = [
            _vol_valid & (_vol20 <= _vol_pcts[0]),
            _vol_valid & (_vol20 > _vol_pcts[0]) & (_vol20 <= _vol_pcts[1]),
            _vol_valid & (_vol20 > _vol_pcts[1]) & (_vol20 <= _vol_pcts[2]),
            _vol_valid & (_vol20 > _vol_pcts[2]) & (_vol20 <= _vol_pcts[3]),
            _vol_valid & (_vol20 > _vol_pcts[3]),
        ]
    else:
        _regime_masks = None

    def _compute_n_negative_regimes(x_flipped_arr):
        """Count vol-quintile regimes where feature IC is negative (training-only)."""
        if _regime_masks is None:
            return None
        n_neg = 0
        n_valid = 0
        for mask in _regime_masks:
            if mask.sum() < 20:
                continue
            n_valid += 1
            ic = _spearman_from_arrays(x_flipped_arr[mask], y_train[mask])
            if ic < 0:
                n_neg += 1
        if n_valid < 3:
            return None
        return n_neg

    def _compute_ic_std_across_regimes(x_flipped_arr):
        """Compute std of IC across vol-quintile regimes (training-only).
        
        Low std = suspiciously uniform across regimes (overfit signature).
        FILTER_DIAGNOSIS: FP mean=0.040 vs TP mean=0.051, Cohen's d=-0.86.
        """
        if _regime_masks is None:
            return None
        regime_ics = []
        for mask in _regime_masks:
            if mask.sum() < 20:
                continue
            ic = _spearman_from_arrays(x_flipped_arr[mask], y_train[mask])
            regime_ics.append(ic)
        if len(regime_ics) < 3:
            return None
        return float(np.std(regime_ics))

    def _compute_yearly_ic_cv(x_flipped_arr):
        """Compute coefficient of variation of yearly ICs (training-only)."""
        yearly_ics = []
        for yr in unique_years:
            mask = dates_years == yr
            if mask.sum() < 20:
                continue
            ic = _spearman_from_arrays(x_flipped_arr[mask], y_train[mask])
            yearly_ics.append(ic)
        if len(yearly_ics) < 3:
            return None
        mean_ic = np.mean(yearly_ics)
        std_ic = np.std(yearly_ics)
        return float(std_ic / abs(mean_ic)) if abs(mean_ic) > 1e-6 else None

    def _compute_weak_link_cv(cand_dict):
        """Compute weak link component IC CV for combo features (training-only)."""
        recipe = candidate_recipes.get(cand_dict["feature_name"])
        if not recipe:
            return None
        components = []
        for key in ["feature_a", "feature_b", "feature_c", "feature_cond"]:
            if key in recipe and recipe[key] in X_df.columns:
                components.append(recipe[key])
        if not components:
            return None
        max_cv = 0.0
        for comp in components:
            comp_vals = X_df[comp].values.astype(np.float64)
            comp_ic = _spearman_from_arrays(comp_vals, y_train)
            comp_sign = 1.0 if comp_ic >= 0 else -1.0
            comp_pred = comp_sign * comp_vals
            yearly_ics = []
            for yr in unique_years:
                mask = dates_years == yr
                if mask.sum() < 20:
                    continue
                yearly_ics.append(_spearman_from_arrays(comp_pred[mask], y_train[mask]))
            if len(yearly_ics) < 3:
                continue
            mean_ic = np.mean(yearly_ics)
            std_ic = np.std(yearly_ics)
            cv = float(std_ic / abs(mean_ic)) if abs(mean_ic) > 1e-6 else 99.0
            if cv > max_cv:
                max_cv = cv
        return max_cv if max_cv > 0 else None

    # Deterministic RNG for the Robustness Gate block bootstrap
    _robust_rng = np.random.default_rng(ROBUST_GATE_SEED)

    for cand in surviving_candidates:
        cand_name = cand["feature_name"]
        cand_ic = cand["overall_ic"]
        cand_comp = cand["composite_score"]
        emp_p93 = cand["empirical_p93"]
        emp_p97 = cand.get("empirical_p97", emp_p93)
        emp_p95_interp = 0.5 * (emp_p93 + emp_p97)  # interpolated 95th from 93rd and 97th
        emp_mean = cand["empirical_mean"]
        ic_null_mean = cand.get("ic_null_mean", 0.0)
        x_cand = cand["x_flipped"]
        deflated_ic = max(0.0, cand_ic - ic_null_mean)
        cand["deflated_ic"] = deflated_ic
        
        # Operator-class-aware B3 floor (calibrated for fixed Sortino formula w=0.50):
        # - 3-way combos (tri_*): 97th percentile
        # - Symmetric 2-way ops (max/min/mean/rank_max/rank_min): interpolated 95th percentile
        # - Conditional 2-way ops + base features: 93rd percentile
        is_tri_combo = cand_name.startswith("combo_tri_")
        is_combo = cand_name.startswith("combo_")
        is_symmetric = False
        if is_combo and not is_tri_combo:
            op_part = cand_name.split("__")[0].replace("combo_", "")
            is_symmetric = op_part in SYMMETRIC_OPS
        
        if is_tri_combo:
            admission_floor = emp_p97
        elif is_symmetric:
            admission_floor = emp_p95_interp
        else:
            admission_floor = emp_p93
        
        # Check composite_score >= admission floor
        if cand_comp < admission_floor:
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "mean_tail_ic": cand["mean_tail_ic"],
                "sortino": cand["sortino"],
                "composite_score": cand_comp,
                "empirical_p93": emp_p93,
                "admission_floor": admission_floor,
                "is_tri_combo": is_tri_combo,
                "is_symmetric_op": is_symmetric,
                "p_value": cand["p_value"],
                "deflated_ic": deflated_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "verdict": "REJECTED_ADMISSION_FLOOR"
            })
            continue

        # Temporal Stability Gate (P1): for combo features, require ic_cv * weak_link_cv >= 0.15
        # FP features are suspiciously "too smooth" — real signals have natural temporal variance.
        # Only applies to combo features (base features have no weak_link_cv).
        if is_combo:
            ic_cv = _compute_yearly_ic_cv(x_cand)
            wl_cv = _compute_weak_link_cv(cand)
            cand["ic_cv"] = ic_cv
            cand["weak_link_cv"] = wl_cv
            if ic_cv is not None and ic_cv > MAX_YEARLY_IC_CV:
                attempts_log.append({
                    "feature_name": cand_name,
                    "sign": cand["sign"],
                    "raw_ic": cand["raw_ic"],
                    "overall_ic": cand_ic,
                    "deflated_ic": deflated_ic,
                    "ic_cv": ic_cv,
                    "ic_ir": cand["ic_ir"],
                    "monotonicity": cand["monotonicity"],
                    "passes_rolling_guard": True,
                    "passes_fdr": True,
                    "verdict": "REJECTED_HIGH_YEARLY_IC_CV"
                })
                continue

            if ic_cv is not None and wl_cv is not None:
                stability_product = ic_cv * wl_cv
                cand["stability_product"] = stability_product
                if stability_product < MIN_STABILITY_PRODUCT:
                    attempts_log.append({
                        "feature_name": cand_name,
                        "sign": cand["sign"],
                        "raw_ic": cand["raw_ic"],
                        "overall_ic": cand_ic,
                        "deflated_ic": deflated_ic,
                        "ic_cv": ic_cv,
                        "weak_link_cv": wl_cv,
                        "stability_product": stability_product,
                        "ic_ir": cand["ic_ir"],
                        "monotonicity": cand["monotonicity"],
                        "passes_rolling_guard": True,
                        "passes_fdr": True,
                        "verdict": "REJECTED_STABILITY_GATE"
                    })
                    continue

        # Negative Regime Gate: reject if feature IC is negative in >=2 vol-quintile regimes
        # Catches regime-conditional signals that fail in transitional vol environments.
        if is_combo:
            n_neg_reg = _compute_n_negative_regimes(x_cand)
            cand["n_negative_regimes"] = n_neg_reg
            if n_neg_reg is not None and n_neg_reg > MAX_NEGATIVE_REGIMES:
                attempts_log.append({
                    "feature_name": cand_name,
                    "sign": cand["sign"],
                    "raw_ic": cand["raw_ic"],
                    "overall_ic": cand_ic,
                    "deflated_ic": deflated_ic,
                    "n_negative_regimes": n_neg_reg,
                    "ic_ir": cand["ic_ir"],
                    "monotonicity": cand["monotonicity"],
                    "passes_rolling_guard": True,
                    "passes_fdr": True,
                    "verdict": "REJECTED_NEGATIVE_REGIMES"
                })
                continue

        # Regime Uniformity Gate: reject combo features with suspiciously uniform regime ICs
        # combined with high yearly IC variability (overfit signature).
        # FP pattern: low ic_std_across_regimes (uniform) + high ic_cv (unstable yearly).
        # FILTER_DIAGNOSIS: ic_std Cohen's d=-0.86, ic_cv Cohen's d=+0.85 for 300ETF FPs.
        if is_combo:
            ic_std_reg = _compute_ic_std_across_regimes(x_cand)
            cand["ic_std_across_regimes"] = ic_std_reg
            # Use ic_cv from stability gate if available, else compute
            ic_cv_val = cand.get("ic_cv")
            if ic_cv_val is None:
                ic_cv_val = _compute_yearly_ic_cv(x_cand)
                cand["ic_cv"] = ic_cv_val
            if ic_std_reg is not None and ic_cv_val is not None:
                # Combined condition: suspiciously uniform across regimes AND unstable yearly
                if ic_std_reg < MIN_IC_STD_REGIMES and ic_cv_val > MAX_IC_CV_FOR_UNIFORM:
                    attempts_log.append({
                        "feature_name": cand_name,
                        "sign": cand["sign"],
                        "raw_ic": cand["raw_ic"],
                        "overall_ic": cand_ic,
                        "deflated_ic": deflated_ic,
                        "ic_std_across_regimes": ic_std_reg,
                        "ic_cv": ic_cv_val,
                        "ic_ir": cand["ic_ir"],
                        "monotonicity": cand["monotonicity"],
                        "passes_rolling_guard": True,
                        "passes_fdr": True,
                        "verdict": "REJECTED_REGIME_UNIFORMITY"
                    })
                    continue

        # Quality Gate (before correlation): minimum deflated IC + positive Sortino + minimum raw IC
        # Prevents low-quality features from entering correlation comparison.
        sortino_val = cand.get("sortino", 0.0)
        raw_ic_abs = abs(cand.get("raw_ic", 0.0))
        passes_quality = (deflated_ic >= min_deflated_ic) and (sortino_val > 0.0) and (raw_ic_abs >= min_raw_ic)
        if not passes_quality:
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "deflated_ic": deflated_ic,
                "sortino": sortino_val,
                "min_deflated_ic": min_deflated_ic,
                "min_raw_ic": min_raw_ic,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
                "verdict": "REJECTED_QUALITY_GATE"
            })
            continue

        # Robustness Gate (A/B-validated in research_gate_ab_test.py):
        # G7 cost-stress (cheap, runs first) then G4 block-bootstrap Sortino CI.
        # Both use the train-window daily strategy returns rebuilt with the
        # exact position logic of simulate_returns. All-flat positions are
        # already rejected above (sortino == 0 fails the Quality Gate).
        # Design note: ALL badness gates run before B5 redundancy resolution
        # (filter -> dedupe). Enforcing post-B5 was tried and reverted: a bad
        # feature could evict a good pool member via the Q-score replacement
        # rule and then die at the gate, silently losing the good feature.
        _pos = _tail_positions_binary(y_train, x_cand, args.side)
        _raw_ret = _pos * y_train
        _abs_pos = np.abs(_pos)

        stress_sortino = _sortino_annual(_raw_ret - _abs_pos * COST_BASE * COST_STRESS_MULT)
        cand["stress_sortino"] = stress_sortino
        if stress_sortino <= 0.0:
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "deflated_ic": deflated_ic,
                "sortino": sortino_val,
                "stress_sortino": stress_sortino,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
                "verdict": "REJECTED_COST_STRESS"
            })
            continue

        sortino_ci_low = _bootstrap_sortino_ci(_raw_ret - _abs_pos * COST_BASE, _robust_rng)
        cand["sortino_ci_low"] = sortino_ci_low
        if sortino_ci_low <= 0.0:
            attempts_log.append({
                "feature_name": cand_name,
                "sign": cand["sign"],
                "raw_ic": cand["raw_ic"],
                "overall_ic": cand_ic,
                "deflated_ic": deflated_ic,
                "sortino": sortino_val,
                "stress_sortino": stress_sortino,
                "sortino_ci_low": sortino_ci_low,
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
                "verdict": "REJECTED_BOOTSTRAP_CI"
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
                "stress_sortino": cand.get("stress_sortino"),
                "sortino_ci_low": cand.get("sortino_ci_low"),
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
                "stress_sortino": cand.get("stress_sortino"),
                "sortino_ci_low": cand.get("sortino_ci_low"),
                "ic_ir": cand["ic_ir"],
                "monotonicity": cand["monotonicity"],
                "passes_rolling_guard": True,
                "passes_fdr": True,
                "max_corr": max_corr,
                "max_corr_feature": max_corr_feature,
                "verdict": "ADMITTED"
            })
        else:
            # Case 2: Max correlation exceeds threshold -> Check replacement rule against correlated pool member(s)
            high_corr_members = [item for item in corrs if item[1] >= args.theta]
            
            replaced = False
            # Replacement rule: replace ONLY IF candidate strictly beats ALL correlated pool members
            if high_corr_members:
                high_corr_indices = []
                for fname, _ in high_corr_members:
                    for idx, p in enumerate(admitted_pool):
                        if p["feature_name"] == fname:
                            high_corr_indices.append(idx)
                            break
                
                if high_corr_indices:
                    cand_q = compute_q_score(cand)
                    all_beaten = all(cand_q > compute_q_score(admitted_pool[idx]) for idx in high_corr_indices)
                    
                    if all_beaten:
                        # Evict all correlated members (in reverse index order) and insert candidate
                        evicted_names = []
                        for idx in sorted(high_corr_indices, reverse=True):
                            evicted_names.append(admitted_pool[idx]["feature_name"])
                            admitted_pool.pop(idx)
                        
                        admitted_pool.append(cand)
                        replaced = True
                        attempts_log.append({
                            "feature_name": cand_name,
                            "sign": cand["sign"],
                            "raw_ic": cand["raw_ic"],
                            "overall_ic": cand_ic,
                            "p_value": cand["p_value"],
                            "deflated_ic": deflated_ic,
                            "stress_sortino": cand.get("stress_sortino"),
                            "sortino_ci_low": cand.get("sortino_ci_low"),
                            "ic_ir": cand["ic_ir"],
                            "monotonicity": cand["monotonicity"],
                            "passes_rolling_guard": True,
                            "passes_fdr": True,
                            "max_corr": max_corr,
                            "max_corr_feature": max_corr_feature,
                            "evicted_features": evicted_names,
                            "verdict": f"ADMITTED_REPLACED_{','.join(evicted_names)}"
                        })
                        for old_fname in evicted_names:
                            attempts_log.append({
                                "feature_name": old_fname,
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

    n_quality_rejects = sum(1 for a in attempts_log if a.get("verdict") == "REJECTED_QUALITY_GATE")
    n_stability_rejects = sum(1 for a in attempts_log if a.get("verdict") == "REJECTED_STABILITY_GATE")
    n_cost_rejects = sum(1 for a in attempts_log if a.get("verdict") == "REJECTED_COST_STRESS")
    n_boot_rejects = sum(1 for a in attempts_log if a.get("verdict") == "REJECTED_BOOTSTRAP_CI")
    print(f"Final admitted pool size: {len(admitted_pool)} (Quality Gate rejected {n_quality_rejects}, "
          f"Stability Gate rejected {n_stability_rejects}, Robustness Gate rejected "
          f"{n_cost_rejects} cost-stress + {n_boot_rejects} bootstrap pre-correlation)")

    # Free x_flipped arrays from non-admitted results to reclaim memory
    admitted_names_set = {item["feature_name"] for item in admitted_pool}
    for item in eval_results:
        if item["feature_name"] not in admitted_names_set and "x_flipped" in item:
            del item["x_flipped"]

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

    # ── Append batch summary to mining_log.json ──────────────────────────────
    mining_log_path = HERE / "mining" / "mining_log.json"
    try:
        if mining_log_path.exists():
            with open(mining_log_path, "r", encoding="utf-8") as f:
                _content = f.read()
            mining_log, _ = json.JSONDecoder().raw_decode(_content)
        else:
            mining_log = {"generated_space": {}, "batches": []}

        # Count verdicts
        n_admitted = sum(1 for a in attempts_log
                         if a.get("verdict", "").startswith("ADMITTED"))
        n_rej_split_half = sum(1 for a in attempts_log
                               if a.get("verdict") == "REJECTED_SPLIT_HALF")
        n_rej_rolling = sum(1 for a in attempts_log
                            if a.get("verdict") == "REJECTED_ROLLING_GUARD")
        n_rej_fdr = sum(1 for a in attempts_log
                        if a.get("verdict") == "REJECTED_FDR_GATE")
        n_rej_corr = sum(1 for a in attempts_log
                         if a.get("verdict") == "REJECTED_REDUNDANCY")
        admitted_names = [a["feature_name"] for a in attempts_log
                          if a.get("verdict", "").startswith("ADMITTED")]

        batch_id = len(mining_log.get("batches", [])) + 1
        from datetime import datetime, timezone
        mining_log.setdefault("batches", []).append({
            "batch_id": batch_id,
            "etf": args.etf,
            "side": args.side,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_candidates": len(attempts_log),
            "n_admitted": n_admitted,
            "n_rejected_split_half": n_rej_split_half,
            "n_rejected_rolling": n_rej_rolling,
            "n_rejected_fdr": n_rej_fdr,
            "n_rejected_corr": n_rej_corr,
            "admitted_names": admitted_names
        })

        mining_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(mining_log_path, "w") as f:
            json.dump(mining_log, f, indent=2)
        print(f"Appended batch #{batch_id} to mining_log.json")
    except Exception as e:
        print(f"WARNING: Could not update mining_log.json: {e}")

    print(f"================================================================================")

if __name__ == "__main__":
    main()
