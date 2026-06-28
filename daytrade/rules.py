"""Rule layer: tradable filter + direction from frozen conviction scores.

Signal Modes
------------

**single** (default, proven)
    Uses one frozen signed regression score per ETF.  The sign of the score
    determines direction (positive → long, negative → short); the magnitude
    determines conviction.  Each side's expanding-percentile threshold is
    conditioned on that side's own prior history only (positive-score days
    for long, negative-score days for short).  Long and short are mutually
    exclusive by construction — no conflict resolution needed.

**hybrid** (experimental, opt-in)
    Keeps the single model for *direction* but replaces conviction with the
    product ``|single_score| × dual_side_score``.  This requires **both** the
    single model (directional accuracy) and the side-specialist model
    (asymmetric conviction) to agree, reducing false positives at the cost of
    fewer trades.  Dual models must be trained first via
    ``python day-model/train_model.py --side both``.

**dual** (v2, true independent execution)
    Each side-specialist model fires **independently** based on its own
    rank-normalised score — no single-model sign gate.  Scores are converted
    to walk-forward percentile ranks via ``expanding_pct_rank`` (fixes the
    threshold-dilution root cause of v1).  When both sides fire, the side
    with the higher normalised margin wins.  This is a genuine dual system:
    the long model can fire on any day regardless of the short model.

Thresholds are always walk-forward (expanding percentile, no look-ahead).
"""
from __future__ import annotations

import bisect
import numpy as np
import pandas as pd

from .scores import compute_scores
from . import ETFS

MIN_PERIODS_DEFAULT = 252  # 1 year burn-in for expanding percentile (legacy)


def expanding_pct(series: pd.Series, q: float, min_periods: int = MIN_PERIODS_DEFAULT) -> pd.Series:
    """Walk-forward percentile threshold: at each row, the threshold is the
    `q`-quantile computed over the PRIOR `min_periods`+ rows of `series`.

    Uses only lagged observations, so no look-ahead bias.
    """
    s = series.shift(1)  # use prior history only
    return s.expanding(min_periods=min_periods).quantile(q)


_MASKED_PCT_CACHE = {}

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
    key = (series.values.tobytes(), q, min_periods)
    if key in _MASKED_PCT_CACHE:
        return _MASKED_PCT_CACHE[key]

    vals = series.shift(1).values  # prior values, NaN where condition didn't hold
    n = len(vals)
    out = np.full(n, np.nan, dtype=float)
    # Pre-extract valid prior values via cumulative mask
    isnan = np.isnan(vals)
    valid_idx = np.where(~isnan)[0]
    if len(valid_idx) == 0:
        res = pd.Series(out, index=series.index)
        _MASKED_PCT_CACHE[key] = res
        return res

    buf = np.empty(len(valid_idx), dtype=float)
    buf[0] = vals[valid_idx[0]]
    for k in range(1, len(valid_idx)):
        buf[k] = vals[valid_idx[k]]
        if k + 1 >= min_periods:
            start = valid_idx[k] + 1
            end = valid_idx[k + 1] + 1 if k + 1 < len(valid_idx) else n
            thr = np.quantile(buf[:k + 1], q)
            out[start:end] = thr
    res = pd.Series(out, index=series.index)
    _MASKED_PCT_CACHE[key] = res
    return res


_RANK_CACHE = {}

def expanding_pct_rank(series: pd.Series, min_periods: int = 60) -> pd.Series:
    """Walk-forward percentile rank of each value relative to prior history.

    For each row *t*, returns the fraction of prior non-NaN values that are
    **strictly less than** ``series[t]``.  Output is in ``[0, 1]``.

    This normalises any score distribution to a uniform ``[0, 1]`` scale,
    making percentile thresholds directly interpretable regardless of the raw
    distribution shape.  A threshold of ``0.9`` selects exactly the top 10 %
    of historical scores — no dilution from a wider positive base (the v1
    dual-model root cause).

    Uses ``bisect`` on a maintained sorted buffer for O(N log N) performance.

    Parameters
    ----------
    series : pd.Series
        Raw scores (may contain NaN for days when the side is inactive).
    min_periods : int
        Minimum number of valid prior observations before the rank is valid.
    """
    key = (series.values.tobytes(), min_periods)
    if key in _RANK_CACHE:
        return _RANK_CACHE[key]

    vals = series.values
    n = len(vals)
    out = np.full(n, np.nan, dtype=float)
    sorted_buf: list[float] = []  # maintained sorted (via bisect.insort)
    for i in range(n):
        v = vals[i]
        if np.isnan(v):
            continue
        if len(sorted_buf) >= min_periods:
            out[i] = bisect.bisect_left(sorted_buf, v) / len(sorted_buf)
        bisect.insort(sorted_buf, float(v))
    res = pd.Series(out, index=series.index)
    _RANK_CACHE[key] = res
    return res


# ---------------------------------------------------------------------------
# Main signal generator (single-mode default, hybrid optional)
# ---------------------------------------------------------------------------
_SIGNALS_CACHE = {}


def get_long_short_signals(
    etf: str,
    long_threshold_pct: float = 70.0,
    long_conviction_pct: float = 60.0,
    short_threshold_pct: float = 70.0,
    short_conviction_pct: float = 60.0,
    min_periods: int = 60,
    long_enabled: bool = True,
    short_enabled: bool = True,
    mode: str = "single",
) -> pd.DataFrame:
    """Return per-day signal frame with per-side expanding-percentile thresholds.

    Memoised: calibration re-runs the same (etf, thr, conv, mode) combos many
    times across stop/exit_bar sweeps, so caching the signal frame is a big
    win. Callers treat the result as read-only (they copy before mutating).

    Parameters
    ----------
    mode : {"single", "hybrid", "dual"}
        ``"single"`` (default) uses the frozen single-model signed score.
        Sign determines direction; magnitude determines conviction.
        Long and short are mutually exclusive.

        ``"hybrid"`` multiplies the single-model magnitude by the dual-model
        side score to form a combined conviction.  Requires dual models
        (``linear_{ETF}_long.joblib`` etc.).  Conflict resolution picks the
        side with the higher normalised margin when both fire.

        ``"dual"`` (v2) lets each side-specialist model fire independently on
        its own rank-normalised score.  No single-model sign gate.  Requires
        dual models.  Conflict resolution picks the side with the higher
        normalised margin when both fire.

    Returns
    -------
    DataFrame indexed by date with columns:
        score, long_fires, short_fires, both_fire,
        direction (+1 / -1 / 0), fired_score,
        long_threshold, long_conviction_thr, long_margin,
        short_threshold, short_conviction_thr, short_margin.
    """
    key = (etf, float(long_threshold_pct), float(long_conviction_pct),
           float(short_threshold_pct), float(short_conviction_pct),
           int(min_periods), bool(long_enabled), bool(short_enabled), mode)
    cached = _SIGNALS_CACHE.get(key)
    if cached is not None:
        return cached

    score = compute_scores(etf, "single", dropna=True)

    if mode == "single":
        out = _signals_single(
            etf, score,
            long_threshold_pct, long_conviction_pct,
            short_threshold_pct, short_conviction_pct,
            min_periods, long_enabled, short_enabled,
        )
    elif mode == "hybrid":
        out = _signals_hybrid(
            etf, score,
            long_threshold_pct, long_conviction_pct,
            short_threshold_pct, short_conviction_pct,
            min_periods, long_enabled, short_enabled,
        )
    elif mode == "dual":
        out = _signals_dual(
            etf,
            long_threshold_pct, long_conviction_pct,
            short_threshold_pct, short_conviction_pct,
            min_periods, long_enabled, short_enabled,
        )
    else:
        raise ValueError(f"mode must be 'single', 'hybrid', or 'dual', got {mode!r}")

    _SIGNALS_CACHE[key] = out
    return out


def _signals_single(
    etf, score,
    long_threshold_pct, long_conviction_pct,
    short_threshold_pct, short_conviction_pct,
    min_periods, long_enabled, short_enabled,
) -> pd.DataFrame:
    """Single-model mode: sign of score → direction, |score| → conviction.

    Threshold for each side is the expanding percentile of |score| computed
    ONLY over that side's prior history (positive-score days for long,
    negative-score days for short).  This conditional thresholding is the key
    insight: long and short score magnitudes have different distributions, so
    a symmetric cutoff is sub-optimal.

    Long and short are mutually exclusive by construction (different signs),
    so no conflict resolution is needed.
    """
    pos_mag = score.where(score > 0).abs()   # |score| on long-side days, NaN else
    neg_mag = score.where(score < 0).abs()   # |score| on short-side days, NaN else

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

    fired_score = pd.Series(np.nan, index=score.index, dtype=float)
    fired_score[long_fires] = score.abs()[long_fires]
    fired_score[short_fires] = score.abs()[short_fires]

    return pd.DataFrame({
        "score": score,
        "long_threshold": long_thr,
        "long_conviction_thr": long_conv,
        "long_fires": long_fires,
        "long_margin": score.abs() / long_thr.where(long_thr > 1e-12, 1e-12),
        "short_threshold": short_thr,
        "short_conviction_thr": short_conv,
        "short_fires": short_fires,
        "short_margin": score.abs() / short_thr.where(short_thr > 1e-12, 1e-12),
        "both_fire": pd.Series(False, index=score.index),
        "direction": direction,
        "fired_score": fired_score,
    })


def _signals_hybrid(
    etf, score,
    long_threshold_pct, long_conviction_pct,
    short_threshold_pct, short_conviction_pct,
    min_periods, long_enabled, short_enabled,
) -> pd.DataFrame:
    """Hybrid mode: single model for direction × dual model for conviction.

    Combined conviction = |single_score| × dual_side_score.

    This product is high ONLY when the single model (directional accuracy)
    and the side-specialist model (asymmetric feature selection) agree on
    strong conviction.  It reduces false positives but also reduces trade
    count.  When both sides fire, the side with the higher normalised margin
    (conviction / threshold) wins.
    """
    long_dual = compute_scores(etf, "long", dropna=True)
    short_dual = compute_scores(etf, "short", dropna=True)

    common_idx = score.index.intersection(long_dual.index).intersection(short_dual.index)
    score = score.loc[common_idx]
    long_dual = long_dual.loc[common_idx]
    short_dual = short_dual.loc[common_idx]

    # Combined conviction (only defined on same-sign days)
    pos_mag = score.where(score > 0, 0.0).abs()
    neg_mag = score.where(score < 0, 0.0).abs()
    long_active = (pos_mag * long_dual).where(pos_mag > 0)
    short_active = (neg_mag * short_dual).where(neg_mag > 0)

    long_thr = expanding_pct_masked(long_active, long_threshold_pct / 100.0, min_periods)
    long_conv = expanding_pct_masked(long_active, long_conviction_pct / 100.0, min_periods)
    short_thr = expanding_pct_masked(short_active, short_threshold_pct / 100.0, min_periods)
    short_conv = expanding_pct_masked(short_active, short_conviction_pct / 100.0, min_periods)

    long_fires = (
        long_enabled
        & (score > 0)
        & (long_active >= long_thr)
        & (long_active >= long_conv)
    )
    short_fires = (
        short_enabled
        & (score < 0)
        & (short_active >= short_thr)
        & (short_active >= short_conv)
    )

    eps = 1e-12
    long_margin = long_active / long_thr.where(long_thr > eps, eps)
    short_margin = short_active / short_thr.where(short_thr > eps, eps)
    both_fire = long_fires & short_fires

    direction = pd.Series(0, index=common_idx, dtype=int)
    direction[long_fires & ~both_fire] = 1
    direction[short_fires & ~both_fire] = -1
    direction[both_fire & (long_margin >= short_margin)] = 1
    direction[both_fire & (long_margin < short_margin)] = -1

    fired_score = pd.Series(np.nan, index=common_idx, dtype=float)
    fired_score[direction > 0] = long_active[direction > 0]
    fired_score[direction < 0] = short_active[direction < 0]

    return pd.DataFrame({
        "score": score,
        "long_score": long_dual,
        "short_score": short_dual,
        "long_threshold": long_thr,
        "long_conviction_thr": long_conv,
        "long_fires": long_fires,
        "long_margin": long_margin,
        "short_threshold": short_thr,
        "short_conviction_thr": short_conv,
        "short_fires": short_fires,
        "short_margin": short_margin,
        "both_fire": both_fire,
        "direction": direction,
        "fired_score": fired_score,
    })


def _signals_dual(
    etf,
    long_threshold_pct, long_conviction_pct,
    short_threshold_pct, short_conviction_pct,
    min_periods, long_enabled, short_enabled,
) -> pd.DataFrame:
    """Dual mode (v2): true independent execution with rank normalisation.

    Each side-specialist model fires independently based on its own
    rank-normalised score.  No single-model sign gate — the long model can
    fire on any day regardless of what the short model says, and vice versa.

    Key differences from v1 hybrid mode:
      1. Scores are normalised via ``expanding_pct_rank`` to [0, 1] before
         thresholding (fixes threshold-dilution root cause).
      2. No single-model direction gate (fixes fake-dual root cause).
      3. Conflict resolution via margin on rank space when both fire.

    The percentile threshold ``long_thr=0.9`` selects exactly the top 10 %
    of historical long-scores — no dilution from a wider positive base.

    Parameters
    ----------
    long_threshold_pct, short_threshold_pct : float
        Percentile cutoff in [0, 100].  ``90`` = top 10 % of scores.
    long_conviction_pct, short_conviction_pct : float
        Additional conviction floor in [0, 100].  Typically ≤ threshold.
    """
    long_dual = compute_scores(etf, "long", dropna=True)
    short_dual = compute_scores(etf, "short", dropna=True)

    common_idx = long_dual.index.intersection(short_dual.index)
    long_dual = long_dual.loc[common_idx]
    short_dual = short_dual.loc[common_idx]

    # Rank-normalise each side independently (Phase 1 fix: no dilution)
    long_rank = expanding_pct_rank(long_dual, min_periods=min_periods)
    short_rank = expanding_pct_rank(short_dual, min_periods=min_periods)

    long_thr = long_threshold_pct / 100.0
    long_conv = long_conviction_pct / 100.0
    short_thr = short_threshold_pct / 100.0
    short_conv = short_conviction_pct / 100.0

    long_fires = (
        long_enabled
        & long_rank.notna()
        & (long_rank >= long_thr)
        & (long_rank >= long_conv)
    )
    short_fires = (
        short_enabled
        & short_rank.notna()
        & (short_rank >= short_thr)
        & (short_rank >= short_conv)
    )

    # Conflict resolution via normalised margin in rank space
    eps = 1e-12
    long_margin = long_rank / max(long_thr, eps)
    short_margin = short_rank / max(short_thr, eps)
    both_fire = long_fires & short_fires

    direction = pd.Series(0, index=common_idx, dtype=int)
    direction[long_fires & ~both_fire] = 1
    direction[short_fires & ~both_fire] = -1
    direction[both_fire & (long_margin >= short_margin)] = 1
    direction[both_fire & (long_margin < short_margin)] = -1

    fired_score = pd.Series(np.nan, index=common_idx, dtype=float)
    fired_score[direction > 0] = long_dual[direction > 0]
    fired_score[direction < 0] = short_dual[direction < 0]

    return pd.DataFrame({
        "long_score": long_dual,
        "short_score": short_dual,
        "long_rank": long_rank,
        "short_rank": short_rank,
        "long_threshold": pd.Series(long_thr, index=common_idx),
        "long_conviction_thr": pd.Series(long_conv, index=common_idx),
        "long_fires": long_fires,
        "long_margin": long_margin,
        "short_threshold": pd.Series(short_thr, index=common_idx),
        "short_conviction_thr": pd.Series(short_conv, index=common_idx),
        "short_fires": short_fires,
        "short_margin": short_margin,
        "both_fire": both_fire,
        "direction": direction,
        "fired_score": fired_score,
    })


# ---------------------------------------------------------------------------
# Legacy symmetric-threshold signal generator (backward compat)
# ---------------------------------------------------------------------------
def get_signals(
    etf: str,
    threshold_pct: float = 70.0,
    min_conviction_pct: float = 60.0,
    min_periods: int = MIN_PERIODS_DEFAULT,
    direction_mode: str = "both",
) -> pd.DataFrame:
    """[Legacy] Symmetric-threshold signal generator using single signed score.

    Uses ``expanding_pct`` (not masked) over |score| for both sides together.
    Prefer ``get_long_short_signals`` for per-side conditional thresholds.
    """
    score = compute_scores(etf, "single", dropna=True)
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
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="single", choices=["single", "hybrid", "dual"])
    args = ap.parse_args()
    print(f"Mode: {args.mode}")
    print(f"{'ETF':<12} {'N':>5} {'Long':>6} {'Short':>6} {'Both':>6} "
          f"{'MeanS':>8}")
    for etf in ETFS:
        s = get_long_short_signals(etf, mode=args.mode)
        n = len(s)
        if n == 0:
            continue
        longs = int(s["long_fires"].sum())
        shorts = int(s["short_fires"].sum())
        both = int(s["both_fire"].sum())
        if "score" in s.columns:
            mean_s = s["score"].abs().mean()
        elif "fired_score" in s.columns:
            mean_s = s["fired_score"].mean()
        else:
            mean_s = float("nan")
        print(f"{etf:<12} {n:>5} {longs:>6} {shorts:>6} {both:>6} "
              f"{mean_s:>8.4f}")
