#!/usr/bin/env python3
"""
Factor Quality (FQ) Score System — forward-predictive factor scoring.

Goal: FQ(t, f) high  =>  factor f has high predictive power over the NEXT ~3 months.
Judged scientifically via meta-IC (see tests/test_fq_validation.py), not lockbox labels.

All matrices are zero-lookahead: row t uses data from [t-window, t-1] only
(same convention as utils.rolling_tail_ic_numba).

Components (480d window unless noted):
  tailIC_480d   — rolling tail Spearman IC (reuse utils)            [IN BLEND]
  sortino_480d  — rolling factor Sortino (reuse utils)              [IN BLEND]
  mono          — share of positive daily-IC days over 480d         [IN BLEND]
  ic_cv         — std/|mean| of daily IC (kept as gate option)
  recency_ratio — tailIC(last 240d) / tailIC(prior 240d) (kept as gate option)
  half_ratio    — mean IC(last 240d) / mean IC(first 240d) (kept for diagnostics)

Phase 0 meta-IC verdict (2016-2025, 348 snapshots): tail_ic +0.048 (t=3.6),
sortino +0.053 (t=3.4), mono +0.010 (n.s.); ic_cv -0.040 and half_ratio -0.043
are NEGATIVE and were removed from the blend.

Hard gates (failing factor gets FQ = 0):
  mandatory: tailIC_480d > 0 AND sortino_480d > 0
  optional (default OFF, Phase 0 found ic_cv/recency non-predictive as gates too):
      ic_cv < 0.50, recency_ratio < 0.80

Score: equal-weight blend of cross-sectional rank-normalized components (v1).
"""

import numpy as np
from numba import njit

from utils import rolling_tail_ic_numba, rolling_factor_risk_numba, _fast_rankdata_norm

WINDOW = 480
HALF_WINDOW = 240


@njit(cache=True)
def rolling_daily_ic_matrix(Z_std: np.ndarray, signs: np.ndarray,
                            trade_returns: np.ndarray) -> np.ndarray:
    """daily_ic[t, j] = Z_signed[t, j] * trade_returns[t]."""
    T, N = Z_std.shape
    out = np.empty((T, N), dtype=np.float64)
    for j in range(N):
        for t in range(T):
            out[t, j] = Z_std[t, j] * signs[j] * trade_returns[t]
    return out


@njit(cache=True)
def rolling_block_stats_numba(daily_ic: np.ndarray, window: int = 480, n_blocks: int = 4,
                              burn_in: int = 252) -> tuple:
    """
    Rolling sub-period stability stats over [t-window, t-1], split into n_blocks.
    (Ported idea: day-model-new n_negative_years + 7-year jackknife sign stability.)

    Returns:
      n_neg_blocks (T, N): count of blocks with mean daily IC < 0
      loo_min_ic   (T, N): min leave-one-block-out mean IC (jackknife worst case)
    """
    T, N = daily_ic.shape
    n_neg = np.zeros((T, N), dtype=np.float64)
    loo_min = np.zeros((T, N), dtype=np.float64)
    blen = window // n_blocks
    effective_start = max(burn_in, window)
    if T < effective_start or N == 0:
        return n_neg, loo_min
    kept = float(window - blen)
    for t in range(effective_start, T):
        ws = t - window
        for j in range(N):
            total = 0.0
            for i in range(window):
                total += daily_ic[ws + i, j]
            cnt = 0
            worst = 1e9
            for b in range(n_blocks):
                bs = 0.0
                for i in range(blen):
                    bs += daily_ic[ws + b * blen + i, j]
                if bs < 0.0:
                    cnt += 1
                loo = (total - bs) / kept
                if loo < worst:
                    worst = loo
            n_neg[t, j] = float(cnt)
            loo_min[t, j] = worst
    if effective_start < T:
        for t in range(effective_start):
            n_neg[t, :] = n_neg[effective_start, :]
            loo_min[t, :] = loo_min[effective_start, :]
    return n_neg, loo_min


@njit(cache=True)
def rolling_regime_sign_numba(daily_ic: np.ndarray, vol20: np.ndarray, window: int = 480,
                              burn_in: int = 252) -> np.ndarray:
    """
    Rolling vol-regime consistency (ported: day-model-new n_negative_regimes).
    Within [t-window, t-1], split days by vol20 above/below the window MEAN;
    returns count of regimes (0-2) where mean daily IC > 0.
    """
    T, N = daily_ic.shape
    out = np.zeros((T, N), dtype=np.float64)
    effective_start = max(burn_in, window)
    if T < effective_start or N == 0:
        return out
    for t in range(effective_start, T):
        ws = t - window
        vsum = 0.0
        for i in range(window):
            vsum += vol20[ws + i]
        vthr = vsum / float(window)
        for j in range(N):
            s_lo = 0.0
            n_lo = 0
            s_hi = 0.0
            n_hi = 0
            for i in range(window):
                d = daily_ic[ws + i, j]
                if vol20[ws + i] <= vthr:
                    s_lo += d
                    n_lo += 1
                else:
                    s_hi += d
                    n_hi += 1
            cnt = 0
            if n_lo > 20 and s_lo / float(n_lo) > 0.0:
                cnt += 1
            if n_hi > 20 and s_hi / float(n_hi) > 0.0:
                cnt += 1
            out[t, j] = float(cnt)
    if effective_start < T:
        for t in range(effective_start):
            out[t, :] = out[effective_start, :]
    return out


@njit(cache=True)
def _safe_ratio(x: float) -> float:
    """Bounded ratio transform: sign(x) * |x| / (1 + |x|) in (-1, 1)."""
    ax = abs(x)
    return (1.0 if x >= 0.0 else -1.0) * ax / (1.0 + ax)


@njit(cache=True)
def rolling_ic_cv_mono_numba(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray,
                             window: int = 480, burn_in: int = 252) -> tuple:
    """
    Rolling (over [t-window, t-1]) IC coefficient-of-variation and monotonicity.
    daily_ic[i, j] = Z_signed[i, j] * trade_returns[i]

    Returns:
      ic_cv_mat (T, N): std(daily_ic) / |mean(daily_ic)| (capped at 10.0)
      mono_mat  (T, N): fraction of days with daily_ic > 0
    """
    T, N = Z_std.shape
    ic_cv_mat = np.zeros((T, N), dtype=np.float64)
    mono_mat = np.zeros((T, N), dtype=np.float64)
    effective_start = max(burn_in, window)
    if T < effective_start or N == 0:
        return ic_cv_mat, mono_mat

    Z_signed = np.zeros((T, N), dtype=np.float64)
    for j in range(N):
        Z_signed[:, j] = Z_std[:, j] * signs[j]

    for t in range(effective_start, T):
        win_start = t - window
        for j in range(N):
            s = 0.0
            s2 = 0.0
            n_pos = 0
            for i in range(window):
                d = Z_signed[win_start + i, j] * trade_returns[win_start + i]
                s += d
                s2 += d * d
                if d > 0.0:
                    n_pos += 1
            mean_d = s / float(window)
            var_d = s2 / float(window) - mean_d * mean_d
            std_d = np.sqrt(max(0.0, var_d))
            amean = abs(mean_d)
            ic_cv_mat[t, j] = min(10.0, std_d / amean) if amean > 1e-12 else 10.0
            mono_mat[t, j] = float(n_pos) / float(window)

    if effective_start < T:
        for t in range(effective_start):
            ic_cv_mat[t, :] = ic_cv_mat[effective_start, :]
            mono_mat[t, :] = mono_mat[effective_start, :]
    return ic_cv_mat, mono_mat


@njit(cache=True)
def rolling_half_ratio_numba(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray,
                             half_window: int = 240, burn_in: int = 252) -> np.ndarray:
    """
    half_ratio[t, j] = mean(daily_ic over [t-half_window, t-1]) /
                       mean(daily_ic over [t-2*half_window, t-half_window-1]),
    mapped through _safe_ratio to (-1, 1). INVERTED in the FQ blend (stable = better).
    """
    T, N = Z_std.shape
    out = np.zeros((T, N), dtype=np.float64)
    effective_start = max(burn_in, 2 * half_window)
    if T < effective_start or N == 0:
        return out

    Z_signed = np.zeros((T, N), dtype=np.float64)
    for j in range(N):
        Z_signed[:, j] = Z_std[:, j] * signs[j]

    hw = float(half_window)
    for t in range(effective_start, T):
        h2_start = t - 2 * half_window  # first half
        h1_start = t - half_window      # second (recent) half
        for j in range(N):
            s_first = 0.0
            s_second = 0.0
            for i in range(half_window):
                s_first += Z_signed[h2_start + i, j] * trade_returns[h2_start + i]
                s_second += Z_signed[h1_start + i, j] * trade_returns[h1_start + i]
            m_first = s_first / hw
            m_second = s_second / hw
            if abs(m_first) > 1e-12:
                out[t, j] = _safe_ratio(m_second / m_first)
            else:
                out[t, j] = _safe_ratio(m_second * 1000.0)

    if effective_start < T:
        for t in range(effective_start):
            out[t, :] = out[effective_start, :]
    return out


def compute_fq_components(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray,
                          window: int = WINDOW, burn_in: int = 252) -> dict:
    """Compute all FQ component matrices (T, N). Zero-lookahead."""
    tail_ic = rolling_tail_ic_numba(Z_std, signs, trade_returns, window=window,
                                    tail_pct=0.10, burn_in=burn_in)
    _, sortino = rolling_factor_risk_numba(Z_std, signs, trade_returns,
                                           window=window, burn_in=burn_in)
    ic_cv, mono = rolling_ic_cv_mono_numba(Z_std, signs, trade_returns,
                                           window=window, burn_in=burn_in)
    # Recency ratio: tail IC on trailing 240d vs the PRIOR 240d
    tail_recent = rolling_tail_ic_numba(Z_std, signs, trade_returns, window=HALF_WINDOW,
                                        tail_pct=0.10, burn_in=burn_in)
    tail_prior = rolling_tail_ic_numba(Z_std, signs, trade_returns, window=HALF_WINDOW,
                                       tail_pct=0.10, burn_in=burn_in + HALF_WINDOW)
    with np.errstate(divide="ignore", invalid="ignore"):
        rec_raw = np.where(np.abs(tail_prior) > 1e-6, tail_recent / tail_prior,
                           np.sign(tail_recent) * 10.0)
    recency = np.sign(rec_raw) * np.abs(rec_raw) / (1.0 + np.abs(rec_raw))
    half_ratio = rolling_half_ratio_numba(Z_std, signs, trade_returns,
                                          half_window=HALF_WINDOW, burn_in=burn_in)
    return {
        "tail_ic": tail_ic,       # higher = better
        "sortino": sortino,       # higher = better
        "ic_cv": ic_cv,           # lower = better (inverted in blend)
        "recency": recency,       # lower = better (inverted in blend)
        "half_ratio": half_ratio, # lower = better (inverted in blend)
        "mono": mono,             # higher = better
    }


def fq_from_components(c: dict, use_extra_gates: bool = False,
                       gate_ic_cv: float = 0.50, gate_recency: float = 0.80) -> np.ndarray:
    """
    Assemble FQ(t, f) in [0, 1] from pre-computed components:
    equal-weight rank blend of the 3 meta-IC-positive components
    (tail_ic, sortino, mono) + hard gates (failing factors -> 0).
    """
    T, N = c["tail_ic"].shape
    fq = np.empty((T, N), dtype=np.float64)
    for t in range(T):
        r = (
            _fast_rankdata_norm(c["tail_ic"][t])
            + _fast_rankdata_norm(c["sortino"][t])
            + _fast_rankdata_norm(c["mono"][t])
        ) / 3.0
        fq[t] = r
    # Hard gates
    gate = (c["tail_ic"] > 0.0) & (c["sortino"] > 0.0)
    if use_extra_gates:
        gate &= (c["ic_cv"] < gate_ic_cv) & (c["recency"] < gate_recency)
    fq[~gate] = 0.0
    return fq


def compute_fq_score(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray,
                     window: int = WINDOW, burn_in: int = 252,
                     use_extra_gates: bool = False,
                     gate_ic_cv: float = 0.50, gate_recency: float = 0.80) -> np.ndarray:
    """Convenience: components + FQ assembly in one call."""
    c = compute_fq_components(Z_std, signs, trade_returns, window=window, burn_in=burn_in)
    return fq_from_components(c, use_extra_gates=use_extra_gates,
                              gate_ic_cv=gate_ic_cv, gate_recency=gate_recency)
