"""Rule layer: tradable filter + direction from frozen score.

Both thresholds use expanding-window percentiles (walk-forward safe, no look-ahead).
A day is tradable iff |score| >= expanding pct(threshold_pct) of prior |score| history.
Direction = sign(score), but only if |score| also >= expanding pct(min_conviction_pct).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .scores import compute_scores
from . import ETFS

MIN_PERIODS_DEFAULT = 252  # 1 year burn-in for expanding percentile


def expanding_pct(series: pd.Series, q: float, min_periods: int = MIN_PERIODS_DEFAULT) -> pd.Series:
    """Walk-forward percentile threshold: at each row, the threshold is the
    `q`-quantile computed over the PRIOR `min_periods`+ rows of `series`.

    Uses only lagged observations, so no look-ahead bias.
    """
    s = series.shift(1)  # use prior history only
    return s.expanding(min_periods=min_periods).quantile(q)


def expanding_pct_masked(
    series: pd.Series, q: float, min_periods: int = 60
) -> pd.Series:
    """Walk-forward percentile over only the non-NaN prior values of `series`.

    Use this when the threshold should be conditioned on a subset of history
    (e.g. only positive-score days for the long-model threshold). `min_periods`
    here counts non-NaN prior observations, not raw row count.

    Vectorized: tracks a running buffer of valid (non-NaN) prior values and
    computes np.quantile at each step. O(N × K) where K = buffer length, but
    numpy-quantile on small arrays is fast.
    """
    vals = series.shift(1).values  # prior values, NaN where condition didn't hold
    n = len(vals)
    out = np.full(n, np.nan, dtype=float)
    # Pre-extract valid prior values via cumulative mask
    isnan = np.isnan(vals)
    valid_idx = np.where(~isnan)[0]
    if len(valid_idx) == 0:
        return pd.Series(out, index=series.index)

    # For each row i, the buffer is all valid_vals[j] where valid_idx[j] < i.
    # Since valid_idx is sorted and < i means position before cursor, use searchsorted.
    # Walk through rows that have at least min_periods prior valid values.
    # The k-th valid value (k >= min_periods - 1) "unlocks" rows in
    # (valid_idx[k], valid_idx[k+1]] for threshold computation using first k+1 values.
    buf = np.empty(len(valid_idx), dtype=float)
    buf[0] = vals[valid_idx[0]]
    for k in range(1, len(valid_idx)):
        buf[k] = vals[valid_idx[k]]
        if k + 1 >= min_periods:
            # Apply threshold to rows in (valid_idx[k], valid_idx[k+1]] (or to end)
            start = valid_idx[k] + 1
            end = valid_idx[k + 1] + 1 if k + 1 < len(valid_idx) else n
            thr = np.quantile(buf[:k + 1], q)
            out[start:end] = thr
    return pd.Series(out, index=series.index)


def get_long_short_signals(
    etf: str,
    long_threshold_pct: float = 70.0,
    long_conviction_pct: float = 60.0,
    short_threshold_pct: float = 70.0,
    short_conviction_pct: float = 60.0,
    min_periods: int = 60,
    long_enabled: bool = True,
    short_enabled: bool = True,
) -> pd.DataFrame:
    """Return per-day signal frame with INDEPENDENT long_model / short_model.

    Each side uses its own expanding-window percentile computed ONLY over
    that side's prior history (positive-score days for long, negative for short).

    Columns:
      score, abs_score,
      long_threshold, long_conviction, long_fires (bool),
      short_threshold, short_conviction, short_fires (bool),
      direction (+1 long, -1 short, 0 none).

    Long & short are mutually exclusive by construction (different score signs),
    so no conflict resolution is needed.
    """
    score = compute_scores(etf, dropna=True)

    # Masked magnitudes per side
    pos_mag = score.where(score > 0).abs()  # |score| on long-side days, NaN else
    neg_mag = score.where(score < 0).abs()  # |score| on short-side days, NaN else

    long_thr = expanding_pct_masked(pos_mag, long_threshold_pct / 100.0, min_periods)
    long_conv = expanding_pct_masked(pos_mag, long_conviction_pct / 100.0, min_periods)
    short_thr = expanding_pct_masked(neg_mag, short_threshold_pct / 100.0, min_periods)
    short_conv = expanding_pct_masked(neg_mag, short_conviction_pct / 100.0, min_periods)

    long_fires = (
        long_enabled
        & (score > 0)
        & (score.abs() >= long_thr)
        & (score.abs() >= long_conv)
    )
    short_fires = (
        short_enabled
        & (score < 0)
        & (score.abs() >= short_thr)
        & (score.abs() >= short_conv)
    )

    direction = pd.Series(0, index=score.index, dtype=int)
    direction[long_fires] = 1
    direction[short_fires] = -1

    return pd.DataFrame({
        "score": score,
        "abs_score": score.abs(),
        "long_threshold": long_thr,
        "long_conviction": long_conv,
        "long_fires": long_fires,
        "short_threshold": short_thr,
        "short_conviction": short_conv,
        "short_fires": short_fires,
        "direction": direction,
    })


def get_signals(
    etf: str,
    threshold_pct: float = 70.0,
    min_conviction_pct: float = 60.0,
    min_periods: int = MIN_PERIODS_DEFAULT,
    direction_mode: str = "both",
) -> pd.DataFrame:
    """[Legacy] Symmetric-threshold signal generator. Kept for backward compat;
    new code should use `get_long_short_signals`.
    """
    score = compute_scores(etf, dropna=True)
    abs_score = score.abs()

    thr = expanding_pct(abs_score, threshold_pct / 100.0, min_periods=min_periods)
    conv = expanding_pct(abs_score, min_conviction_pct / 100.0, min_periods=min_periods)

    out = pd.DataFrame({
        "score": score,
        "abs_score": abs_score,
        "threshold": thr,
        "conviction": conv,
    })
    out["tradable"] = (abs_score >= thr) & thr.notna()
    sign = np.sign(score).astype(int)
    base_dir = np.where(out["tradable"] & (abs_score >= conv), sign, 0)

    if direction_mode == "long_only":
        base_dir = np.where(base_dir > 0, 1, 0)
    elif direction_mode == "short_only":
        base_dir = np.where(base_dir < 0, -1, 0)
    elif direction_mode != "both":
        raise ValueError(f"unknown direction_mode: {direction_mode}")

    out["direction"] = base_dir
    return out


if __name__ == "__main__":
    # Long/short signal counts at default symmetric thresholds
    print(f"{'ETF':<10} {'N':>5} {'Long':>6} {'Short':>6} {'Both':>6} {'Mean|s|':>8}")
    for etf in ETFS:
        s = get_long_short_signals(etf)
        n = len(s)
        if n == 0:
            continue
        longs = int(s["long_fires"].sum())
        shorts = int(s["short_fires"].sum())
        print(f"{etf:<10} {n:>5} {longs:>6} {shorts:>6} "
              f"{longs+shorts:>6} {s['abs_score'].mean():>8.4f}")