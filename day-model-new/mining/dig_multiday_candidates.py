"""
Mining & Screening Script for Multi-Day (2-5 day) Day-Level Primitives.

Targets mechanism gap: existing features mostly capture single-day "yesterday" properties.
Strategy ideas (Dual-Thrust, R-Breaker, Turtle, Momentum) suggest past 2-5 day STRUCTURE
is predictive of intraday returns.

These are DAY-LEVEL features: computed from daily OHLCV, shifted by 1 upstream (causality safe).
Screening uses same 4 gates as early-bar candidates:
  - IC_CV <= 3.0
  - n_negative_years <= 2
  - 7-Year Jackknife sign stability PASS
  - |IC| >= 0.02
"""
import sys
import os
import csv
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from build_features import INDEX_CONFIG, ETF_CONFIG
DATA_DIR = REPO_ROOT / "data"


def fast_spearman(a: np.ndarray, b: np.ndarray) -> float:
    n = len(a)
    if n < 5:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)


def compute_yearly_ic(x: np.ndarray, y: np.ndarray, dates: pd.Index) -> dict:
    years = pd.to_datetime(dates).year if hasattr(dates, "year") else pd.to_datetime(dates).dt.year
    df_temp = pd.DataFrame({"x": x, "y": y, "year": years})
    yearly_ics = []
    for yr, group in df_temp.groupby("year"):
        if len(group) >= 15:
            ic = fast_spearman(group["x"].values, group["y"].values)
            yearly_ics.append(ic)
    if not yearly_ics:
        return {"mean_ic": 0.0, "ic_cv": 999.0, "n_neg_years": 999, "jackknife_pass": False, "flips": 999}
    arr = np.array(yearly_ics)
    mean_ic = float(np.mean(arr))
    std_ic = float(np.std(arr))
    ic_cv = abs(std_ic / (mean_ic + 1e-8)) if abs(mean_ic) > 1e-6 else 999.0
    n_neg = int(np.sum(arr < 0)) if mean_ic > 0 else int(np.sum(arr > 0))

    # 7-Year Jackknife sign stability
    n_chunks = 7
    chunk_size = len(x) // n_chunks
    chunk_signs = []
    for c in range(n_chunks):
        sub_x = x[c * chunk_size: (c + 1) * chunk_size]
        sub_y = y[c * chunk_size: (c + 1) * chunk_size]
        if len(sub_x) >= 10:
            cic = fast_spearman(sub_x, sub_y)
            chunk_signs.append(1 if cic * mean_ic > 0 else -1)

    flips = sum(1 for s in chunk_signs if s < 0)
    jackknife_pass = (flips <= 1) and (len(chunk_signs) >= 2 and chunk_signs[-1] > 0 and chunk_signs[-2] > 0)

    return {
        "mean_ic": mean_ic,
        "std_ic": std_ic,
        "ic_cv": ic_cv,
        "n_neg_years": n_neg,
        "jackknife_pass": jackknife_pass,
        "flips": flips,
    }


# ============================================================
# Multi-Day Candidate Feature Functions
# Each takes a DataFrame with columns: open_adj, high_adj, low_adj, close_adj, volume
# Returns a Series (already shifted by 1 for causality)
# ============================================================

def calc_dual_thrust_range_ratio(df: pd.DataFrame) -> pd.Series:
    """Dual-Thrust N-day range asymmetry (N=3).
    Range = max(HH - LC, HC - LL) where HH=highest high, LC=lowest close, etc.
    Asymmetry = (HH - LC) / (Range + 1e-8) - 0.5
    Positive = upside range dominates (bullish bias), Negative = downside dominates.
    Normalized to [-1, 1]."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    hh = hi.rolling(3).max()
    ll = lo.rolling(3).min()
    hc = cl.rolling(3).max()
    lc = cl.rolling(3).min()
    upside = hh - lc
    downside = hc - ll
    total_range = np.maximum(upside, downside)
    # Asymmetry: >0.5 means upside range > downside range
    asym = (upside - downside) / (total_range + 1e-8)
    return asym.clip(-1, 1).shift(1)


def calc_range_compression_3d(df: pd.DataFrame) -> pd.Series:
    """3-day range compression relative to 10-day average range.
    Compression = mean(range_last_3d) / mean(range_last_10d) - 1
    Negative = compressing (breakout setup), Positive = expanding.
    Clipped to [-1, 1]."""
    rng = (df["high_adj"] - df["low_adj"]) / (df["close_adj"] + 1e-8)
    avg3 = rng.rolling(3).mean()
    avg10 = rng.rolling(10).mean()
    compression = (avg3 / (avg10 + 1e-8)) - 1.0
    return compression.clip(-1, 1).shift(1)


def calc_return_acceleration_3d(df: pd.DataFrame) -> pd.Series:
    """3-day return acceleration: last 1.5 days vs prior 1.5 days.
    Captures whether momentum is building or fading over recent days.
    Normalized by ATR proxy (5-day avg range).
    Shifted by 1: at prediction day T, uses only close[T-1], close[T-2], close[T-3]."""
    cl = df["close_adj"]
    ret_1d = cl.pct_change(1)
    # Last day return vs average of prior 2 days
    recent = ret_1d  # day T
    prior = (ret_1d.shift(1) + ret_1d.shift(2)) / 2.0  # avg(T-1, T-2)
    accel = recent - prior
    # Normalize by 5-day realized vol
    vol5 = ret_1d.rolling(5).std() + 1e-8
    norm_accel = accel / vol5
    return (norm_accel.clip(-3, 3) / 3.0).shift(1)  # shift(1) for causality


def calc_volume_price_corr_5d(df: pd.DataFrame) -> pd.Series:
    """5-day rolling correlation between daily returns and volume.
    Positive = volume confirms price moves (healthy trend).
    Negative = volume diverges from price (exhaustion/reversal risk)."""
    cl = df["close_adj"]
    ret = cl.pct_change(1)
    vol = df["volume"]
    corr = ret.rolling(5).corr(vol)
    return corr.fillna(0).clip(-1, 1).shift(1)


def calc_gap_persistence_3d(df: pd.DataFrame) -> pd.Series:
    """Average overnight gap relative to intraday range over 3 days.
    Gap = open - prev_close, Intraday = close - open.
    High positive = persistent gap-up with follow-through (bullish).
    High negative = persistent gap-down (bearish).
    Near zero = gaps fade intraday (mean-reversion regime)."""
    op = df["open_adj"]
    cl = df["close_adj"]
    prev_cl = cl.shift(1)
    gap = (op - prev_cl) / (prev_cl + 1e-8)
    intraday = (cl - op) / (op + 1e-8)
    # Ratio: gap vs intraday over 3 days
    gap_sum = gap.rolling(3).sum()
    intraday_sum = intraday.rolling(3).sum()
    # Normalized difference
    total_move = gap_sum.abs() + intraday_sum.abs() + 1e-8
    persistence = (gap_sum - intraday_sum) / total_move
    return persistence.clip(-1, 1).shift(1)


def calc_close_trend_consistency_5d(df: pd.DataFrame) -> pd.Series:
    """Count of up-closes in last 5 days, normalized to [-1, 1].
    +1 = all 5 days up, -1 = all 5 days down, 0 = mixed.
    Simple but powerful multi-day momentum streak measure."""
    cl = df["close_adj"]
    up = (cl > cl.shift(1)).astype(float)
    count_5d = up.rolling(5).sum()
    # Normalize: 0-5 -> [-1, 1]
    norm = (count_5d - 2.5) / 2.5
    return norm.clip(-1, 1).shift(1)


def calc_overnight_intraday_decomp_3d(df: pd.DataFrame) -> pd.Series:
    """3-day overnight vs intraday return decomposition.
    overnight = open_t - close_{t-1}, intraday = close_t - open_t
    Ratio = sum(overnight) / (sum(|overnight|) + sum(|intraday|))
    Positive = overnight buyers in control, Negative = intraday sellers."""
    op = df["open_adj"]
    cl = df["close_adj"]
    prev_cl = cl.shift(1)
    overnight = (op - prev_cl) / (prev_cl + 1e-8)
    intraday = (cl - op) / (op + 1e-8)
    on_sum = overnight.rolling(3).sum()
    id_sum = intraday.rolling(3).sum()
    denom = on_sum.abs() + id_sum.abs() + 1e-8
    ratio = on_sum / denom
    return ratio.clip(-1, 1).shift(1)


def calc_position_in_3d_range(df: pd.DataFrame) -> pd.Series:
    """Close position within 3-day high-low range.
    1 = at 3-day high, 0 = at 3-day low, 0.5 = middle.
    Centered to [-1, 1]: (pos - 0.5) * 2."""
    hi3 = df["high_adj"].rolling(3).max()
    lo3 = df["low_adj"].rolling(3).min()
    cl = df["close_adj"]
    pos = (cl - lo3) / (hi3 - lo3 + 1e-8)
    centered = (pos - 0.5) * 2.0
    return centered.clip(-1, 1).shift(1)


def calc_body_accumulation_5d(df: pd.DataFrame) -> pd.Series:
    """5-day signed body accumulation: sum(close-open)/range over 5 days.
    Measures net directional conviction across multiple days.
    High positive = persistent bullish bodies, negative = bearish."""
    op = df["open_adj"]
    cl = df["close_adj"]
    hi = df["high_adj"]
    lo = df["low_adj"]
    body = (cl - op) / (hi - lo + 1e-8)
    accum = body.rolling(5).sum() / 5.0
    return accum.clip(-1, 1).shift(1)


def calc_volume_weighted_return_3d(df: pd.DataFrame) -> pd.Series:
    """Volume-weighted 3-day return: more recent days weighted by volume.
    Captures whether high-volume days drove the move (stronger signal).
    Normalized by 5-day vol."""
    cl = df["close_adj"]
    vol = df["volume"]
    ret = cl.pct_change(1)
    # Volume-weighted return over 3 days
    vw_ret = (ret * vol).rolling(3).sum() / (vol.rolling(3).sum() + 1e-8)
    # Normalize by recent vol
    vol5 = ret.rolling(5).std() + 1e-8
    norm = vw_ret / vol5
    return norm.clip(-3, 3).div(3).shift(1)


def calc_higher_high_streak(df: pd.DataFrame) -> pd.Series:
    """Consecutive days of higher highs (positive) or lower lows (negative).
    Captures trend structure persistence over 2-5 days.
    Streak capped at 5, normalized to [-1, 1]."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    hh = (hi > hi.shift(1)).astype(int)
    ll = (lo < lo.shift(1)).astype(int)
    # Compute run-length streaks
    hh_streak = _consecutive_streak(hh.values)
    ll_streak = _consecutive_streak(ll.values)
    streak = (hh_streak - ll_streak) / 5.0
    result = pd.Series(np.clip(streak, -1, 1), index=df.index)
    return result.shift(1)


def calc_range_expansion_velocity(df: pd.DataFrame) -> pd.Series:
    """Rate of daily range expansion over 3 days.
    range_t / range_{t-1} averaged over 3 days.
    >1 = expanding volatility (breakout), <1 = contracting (compression).
    Log-scaled and normalized."""
    rng = df["high_adj"] - df["low_adj"]
    # 3-day range ratio: today vs 3 days ago
    ratio_3d = rng / (rng.shift(3) + 1e-8)
    # Also 1-day expansion
    ratio_1d = rng / (rng.shift(1) + 1e-8)
    # Combine: geometric mean of recent expansion
    combined = np.log(ratio_1d.clip(0.1, 10) * ratio_3d.clip(0.1, 10)) / 2.0
    return pd.Series(combined.clip(-2, 2) / 2.0, index=df.index).shift(1)


def calc_multi_day_vwap_deviation(df: pd.DataFrame) -> pd.Series:
    """Deviation of close from 3-day VWAP (volume-weighted average price).
    Positive = trading above multi-day VWAP (bullish), negative = below.
    Normalized by 3-day average range."""
    cl = df["close_adj"]
    vol = df["volume"]
    # 3-day VWAP approximation
    vwap3 = (cl * vol).rolling(3).sum() / (vol.rolling(3).sum() + 1e-8)
    dev = (cl - vwap3) / (vwap3 + 1e-8)
    # Normalize by 3-day avg range
    rng3 = ((df["high_adj"] - df["low_adj"]) / (cl + 1e-8)).rolling(3).mean()
    norm_dev = dev / (rng3 + 1e-8)
    return norm_dev.clip(-3, 3).div(3).shift(1)


def _consecutive_streak(flags: np.ndarray) -> np.ndarray:
    """Run-length of consecutive 1s ending at each position."""
    out = np.zeros(len(flags), dtype=np.float64)
    run = 0
    for i, f in enumerate(flags):
        if f:
            run += 1
        else:
            run = 0
        out[i] = run
    return out


def calc_dual_thrust_range_ratio_5d(df: pd.DataFrame) -> pd.Series:
    """Dual-Thrust range asymmetry with N=5 (longer lookback).
    Same mechanism as 3d but captures weekly structure."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    hh = hi.rolling(5).max()
    ll = lo.rolling(5).min()
    hc = cl.rolling(5).max()
    lc = cl.rolling(5).min()
    upside = hh - lc
    downside = hc - ll
    total_range = np.maximum(upside, downside)
    asym = (upside - downside) / (total_range + 1e-8)
    return asym.clip(-1, 1).shift(1)


def calc_close_location_in_range_3d(df: pd.DataFrame) -> pd.Series:
    """Average close position within each day's range over 3 days.
    High = closes near highs (buyers in control at close).
    Low = closes near lows (sellers in control).
    Averaged over 3 days for stability."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    pos = (cl - lo) / (hi - lo + 1e-8)
    avg_pos = pos.rolling(3).mean()
    # Center to [-1, 1]
    return ((avg_pos - 0.5) * 2.0).clip(-1, 1).shift(1)


def calc_volume_trend_3d(df: pd.DataFrame) -> pd.Series:
    """3-day volume trend: linear regression slope of volume over 3 days.
    Normalized by mean volume. Rising volume = accumulation."""
    vol = df["volume"]
    vol_ma5 = vol.rolling(5).mean()
    # 3-day volume slope: (vol[T] - vol[T-2]) / 2, normalized
    slope = (vol - vol.shift(2)) / (2.0 * vol_ma5 + 1e-8)
    return slope.clip(-1, 1).shift(1)


def calc_inside_day_count_5d(df: pd.DataFrame) -> pd.Series:
    """Count of inside days (H < prev_H AND L > prev_L) in last 5 days.
    Inside days = compression/coiling before breakout.
    Normalized: 0-4 inside days -> [0, 1]."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    inside = ((hi < hi.shift(1)) & (lo > lo.shift(1))).astype(float)
    count = inside.rolling(5).sum()
    return (count / 4.0).clip(0, 1).shift(1)


def calc_atr_acceleration_3d(df: pd.DataFrame) -> pd.Series:
    """ATR acceleration: ATR(3) vs ATR(3).shift(2).
    Positive = volatility expanding, Negative = compressing.
    Normalized by ATR(10)."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    prev_cl = cl.shift(1)
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(), (lo - prev_cl).abs()], axis=1).max(axis=1)
    atr3 = tr.rolling(3).mean()
    atr3_lag = atr3.shift(2)
    atr10 = tr.rolling(10).mean()
    accel = (atr3 - atr3_lag) / (atr10 + 1e-8)
    return accel.clip(-2, 2).div(2).shift(1)


def calc_consecutive_close_direction(df: pd.DataFrame) -> pd.Series:
    """Weighted consecutive close direction over 5 days.
    More recent days weighted more heavily.
    Weights: [0.35, 0.25, 0.20, 0.12, 0.08] for days T-1 to T-5.
    Positive = persistent up-closes, Negative = down-closes."""
    cl = df["close_adj"]
    direction = np.sign(cl - cl.shift(1))
    weights = [0.35, 0.25, 0.20, 0.12, 0.08]
    weighted = direction * weights[0]
    for i, w in enumerate(weights[1:], 1):
        weighted = weighted + direction.shift(i) * w
    return weighted.clip(-1, 1).shift(1)


def calc_range_position_momentum(df: pd.DataFrame) -> pd.Series:
    """Momentum of range position: is close-in-range improving or deteriorating?
    Compares avg close-position last 2 days vs prior 2 days.
    Rising = buyers gaining control into close."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    pos = (cl - lo) / (hi - lo + 1e-8)
    recent = pos.rolling(2).mean()
    prior = pos.shift(2).rolling(2).mean()
    delta = (recent - prior) * 2.0  # scale to [-1, 1]
    return delta.clip(-1, 1).shift(1)


def calc_open_close_reversal_3d(df: pd.DataFrame) -> pd.Series:
    """3-day open-to-close reversal pattern.
    If opens gap up but closes come back down (or vice versa),
    this indicates intraday mean-reversion pressure.
    = mean(sign(open-prev_close) * (close-open)/range) over 3 days."""
    op = df["open_adj"]
    cl = df["close_adj"]
    hi = df["high_adj"]
    lo = df["low_adj"]
    prev_cl = cl.shift(1)
    gap_dir = np.sign(op - prev_cl)
    intraday_ret = (cl - op) / (hi - lo + 1e-8)
    reversal = gap_dir * intraday_ret
    avg_reversal = reversal.rolling(3).mean()
    return avg_reversal.clip(-1, 1).shift(1)


# ============================================================
# Registry of all multi-day candidates
# ============================================================
# ============================================================
# Wave 3: Market Regime & Big Trend Factors (Al Brooks / Strategies)
# ============================================================

def calc_adx_14d(df: pd.DataFrame) -> pd.Series:
    """14-day ADX (Average Directional Index) — trend strength measure.
    ADX > 25 = trending, ADX < 20 = ranging.
    Normalized to [0, 1] by dividing by 50."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    prev_cl = cl.shift(1)
    # True Range
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(), (lo - prev_cl).abs()], axis=1).max(axis=1)
    # Directional Movement
    up_move = hi - hi.shift(1)
    down_move = lo.shift(1) - lo
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_dm_s = pd.Series(plus_dm, index=df.index).rolling(14).mean()
    minus_dm_s = pd.Series(minus_dm, index=df.index).rolling(14).mean()
    tr_s = tr.rolling(14).mean()
    plus_di = 100.0 * plus_dm_s / (tr_s + 1e-8)
    minus_di = 100.0 * minus_dm_s / (tr_s + 1e-8)
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-8)
    adx = dx.rolling(14).mean()
    # Normalize: ADX 0-50 -> [0, 1]
    return (adx / 50.0).clip(0, 1).shift(1)


def calc_ema_ribbon_width(df: pd.DataFrame) -> pd.Series:
    """EMA ribbon width: (EMA5 - EMA20) / ATR14.
    Wide positive ribbon = strong bull trend, wide negative = bear trend.
    Narrow = ranging/compression."""
    cl = df["close_adj"]
    hi = df["high_adj"]
    lo = df["low_adj"]
    prev_cl = cl.shift(1)
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(), (lo - prev_cl).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()
    ema5 = cl.ewm(span=5, adjust=False).mean()
    ema20 = cl.ewm(span=20, adjust=False).mean()
    ribbon = (ema5 - ema20) / (atr14 + 1e-8)
    return ribbon.clip(-3, 3).div(3).shift(1)


def calc_donchian_breakout_proximity_20d(df: pd.DataFrame) -> pd.Series:
    """Proximity of close to 20-day Donchian channel extreme.
    +1 = at 20-day high, -1 = at 20-day low, 0 = middle.
    Captures whether market is at breakout levels."""
    hi20 = df["high_adj"].rolling(20).max()
    lo20 = df["low_adj"].rolling(20).min()
    cl = df["close_adj"]
    pos = (cl - lo20) / (hi20 - lo20 + 1e-8)
    centered = (pos - 0.5) * 2.0
    return centered.clip(-1, 1).shift(1)


def calc_trend_persistence_hurst_proxy(df: pd.DataFrame) -> pd.Series:
    """Hurst exponent proxy via variance ratio of multi-day returns.
    VR = Var(5d returns) / (5 * Var(1d returns)). VR > 1 = trending, VR < 1 = mean-reverting.
    Centered at 0: (VR - 1) clipped to [-1, 1]."""
    cl = df["close_adj"]
    ret1 = cl.pct_change(1)
    ret5 = cl.pct_change(5)
    var1 = ret1.rolling(20).var()
    var5 = ret5.rolling(20).var()
    vr = var5 / (5.0 * var1 + 1e-12)
    # Center at 1: VR > 1 = trending
    centered = (vr - 1.0)
    return centered.clip(-1, 1).shift(1)


def calc_buying_selling_pressure_10d(df: pd.DataFrame) -> pd.Series:
    """Al Brooks Buying/Selling Pressure: 10-day average of lower-tail / upper-tail ratio.
    Buying pressure = lower tails prominent (buyers defending lows).
    Selling pressure = upper tails prominent (sellers defending highs).
    Returns: positive = buying pressure dominant, negative = selling."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    cl = df["close_adj"]
    op = df["open_adj"]
    rng = hi - lo + 1e-8
    lower_tail = (np.minimum(op, cl) - lo) / rng
    upper_tail = (hi - np.maximum(op, cl)) / rng
    bp = lower_tail.rolling(10).mean()
    sp = upper_tail.rolling(10).mean()
    pressure = (bp - sp) / (bp + sp + 1e-8)
    return pressure.clip(-1, 1).shift(1)


def calc_trend_maturity_bars_since_reversal(df: pd.DataFrame) -> pd.Series:
    """Bars (days) since last significant trend reversal.
    Reversal = close crosses 10-day EMA after being on other side for 3+ days.
    Young trend (few bars since reversal) = high continuation probability.
    Returns: normalized bars since reversal, signed by trend direction."""
    cl = df["close_adj"]
    ema10 = cl.ewm(span=10, adjust=False).mean()
    above = (cl > ema10).astype(int)
    # Detect crossings
    cross = (above != above.shift(1)).astype(int)
    # Count bars since last cross
    bars_since = np.zeros(len(df), dtype=np.float64)
    last_cross_idx = 0
    for i in range(len(df)):
        if cross.iloc[i] == 1:
            last_cross_idx = i
        bars_since[i] = i - last_cross_idx
    # Sign by current trend direction
    direction = np.where(above == 1, 1.0, -1.0)
    # Normalize: cap at 30 bars
    norm_bars = np.minimum(bars_since / 30.0, 1.0)
    result = pd.Series(direction * norm_bars, index=df.index)
    return result.clip(-1, 1).shift(1)


def calc_spike_quality_5d(df: pd.DataFrame) -> pd.Series:
    """Quality of the largest single-day move in last 5 days.
    Spike quality = body/range of the largest absolute return day.
    High quality spike (body >> tails) = strong institutional conviction.
    Signed by spike direction."""
    cl = df["close_adj"]
    op = df["open_adj"]
    hi = df["high_adj"]
    lo = df["low_adj"]
    ret = (cl - cl.shift(1)).abs()
    body = (cl - op)
    rng = hi - lo + 1e-8
    body_ratio = body.abs() / rng
    # Find the day with max absolute return in rolling 5-day window
    # Use rolling apply to get body_ratio of max-return day
    def _spike_quality(window_ret, window_br):
        if len(window_ret) < 5:
            return 0.0
        max_idx = np.argmax(window_ret)
        return window_br[max_idx]
    # Simpler: rolling max return * its body ratio
    max_ret_5d = ret.rolling(5).max()
    # Get sign and quality of the spike day
    signed_body = body / rng
    # Use the body_ratio of the day with max return
    spike_quality = pd.Series(0.0, index=df.index)
    for i in range(4, len(df)):
        window_ret = ret.iloc[i-4:i+1].values
        window_br = signed_body.iloc[i-4:i+1].values
        max_idx = np.argmax(window_ret)
        spike_quality.iloc[i] = window_br[max_idx]
    return spike_quality.clip(-1, 1).shift(1)


def calc_volatility_compression_breakout_setup(df: pd.DataFrame) -> pd.Series:
    """Bollinger Band width compression over 10 days relative to 40 days.
    Extreme compression = breakout imminent (direction from BB slope).
    Returns: compression * sign(EMA5 slope)."""
    cl = df["close_adj"]
    sma20 = cl.rolling(20).mean()
    std20 = cl.rolling(20).std()
    bb_width = (2.0 * std20) / (sma20 + 1e-8)
    # Compression: current width vs 40-day average width
    bb_width_40 = bb_width.rolling(40).mean()
    compression = 1.0 - (bb_width / (bb_width_40 + 1e-8))
    # Direction from EMA5 slope
    ema5 = cl.ewm(span=5, adjust=False).mean()
    slope_sign = np.sign(ema5 - ema5.shift(3))
    result = compression * slope_sign
    return result.clip(-1, 1).shift(1)


def calc_directional_movement_efficiency_10d(df: pd.DataFrame) -> pd.Series:
    """10-day directional movement efficiency: net displacement / total path length.
    High = clean trend (efficient movement), Low = choppy/ranging.
    Signed by direction."""
    cl = df["close_adj"]
    # Net displacement over 10 days
    net_disp = cl - cl.shift(10)
    # Total path length: sum of absolute daily moves over 10 days
    daily_move = (cl - cl.shift(1)).abs()
    path_len = daily_move.rolling(10).sum()
    efficiency = net_disp / (path_len + 1e-8)
    return efficiency.clip(-1, 1).shift(1)


def calc_channel_width_trend_5d(df: pd.DataFrame) -> pd.Series:
    """5-day channel width trend: is the daily range expanding or contracting?
    Expanding channel = trend acceleration, Contracting = trend exhaustion.
    Returns slope of 5-day range normalized by mean range."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    rng = (hi - lo) / (df["close_adj"] + 1e-8)
    # Linear slope over 5 days
    x = np.arange(5, dtype=np.float64)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()
    def _slope(vals):
        if len(vals) < 5:
            return 0.0
        y = vals - vals.mean()
        return ((x - x_mean) * y).sum() / x_var
    slope = rng.rolling(5).apply(_slope, raw=True)
    mean_rng = rng.rolling(20).mean()
    norm_slope = slope / (mean_rng + 1e-8)
    return norm_slope.clip(-2, 2).div(2).shift(1)


def calc_new_high_low_momentum_10d(df: pd.DataFrame) -> pd.Series:
    """Count of 10-day new highs minus new lows over last 10 days.
    Frequent new highs = strong uptrend, frequent new lows = downtrend.
    Normalized to [-1, 1]."""
    hi = df["high_adj"]
    lo = df["low_adj"]
    # Is today's high a 10-day high?
    new_high = (hi >= hi.rolling(10).max()).astype(float)
    new_low = (lo <= lo.rolling(10).min()).astype(float)
    # Count over 10 days
    nh_count = new_high.rolling(10).sum()
    nl_count = new_low.rolling(10).sum()
    momentum = (nh_count - nl_count) / 10.0
    return momentum.clip(-1, 1).shift(1)


def calc_volume_weighted_close_momentum_10d(df: pd.DataFrame) -> pd.Series:
    """10-day volume-weighted close momentum.
    Weights recent returns by volume — high-volume moves carry more weight.
    Normalized by 10-day volatility."""
    cl = df["close_adj"]
    vol = df["volume"]
    ret = cl.pct_change(1)
    # Volume-weighted return over 10 days
    vw_ret = (ret * vol).rolling(10).sum() / (vol.rolling(10).sum() + 1e-8)
    # Normalize by 10-day vol
    vol10 = ret.rolling(10).std() + 1e-8
    norm = vw_ret / vol10
    return norm.clip(-3, 3).div(3).shift(1)


def calc_trend_line_distance_10d(df: pd.DataFrame) -> pd.Series:
    """Distance of close from 10-day linear regression trend line.
    Above trend line = bullish extension, below = bearish.
    Normalized by ATR14."""
    cl = df["close_adj"]
    hi = df["high_adj"]
    lo = df["low_adj"]
    prev_cl = cl.shift(1)
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(), (lo - prev_cl).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()
    # 10-day linear regression
    x = np.arange(10, dtype=np.float64)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()
    def _trend_dist(vals):
        if len(vals) < 10:
            return 0.0
        y = vals
        y_mean = y.mean()
        slope = ((x - x_mean) * (y - y_mean)).sum() / x_var
        intercept = y_mean - slope * x_mean
        predicted_last = intercept + slope * 9.0
        return y[-1] - predicted_last
    dist = cl.rolling(10).apply(_trend_dist, raw=True)
    norm_dist = dist / (atr14 + 1e-8)
    return norm_dist.clip(-3, 3).div(3).shift(1)


def calc_consecutive_ema20_above_days(df: pd.DataFrame) -> pd.Series:
    """Number of consecutive days close is above/below EMA20.
    Extended streak = strong trend regime (Al Brooks 20 Gap Bars).
    Returns: streak / 20, signed by direction, clipped to [-1, 1]."""
    cl = df["close_adj"]
    ema20 = cl.ewm(span=20, adjust=False).mean()
    above = (cl > ema20).astype(int).values
    below = (cl < ema20).astype(int).values
    # Compute streaks
    bull_streak = np.zeros(len(df), dtype=np.float64)
    bear_streak = np.zeros(len(df), dtype=np.float64)
    bs = 0
    brs = 0
    for i in range(len(df)):
        if above[i]:
            bs += 1
            brs = 0
        elif below[i]:
            brs += 1
            bs = 0
        else:
            bs = 0
            brs = 0
        bull_streak[i] = bs
        bear_streak[i] = brs
    result = pd.Series((bull_streak - bear_streak) / 20.0, index=df.index)
    return result.clip(-1, 1).shift(1)


def calc_multi_day_body_efficiency_5d(df: pd.DataFrame) -> pd.Series:
    """5-day average body efficiency: |close-open| / (high-low).
    High = clean directional movement (trend), Low = indecision (range).
    Signed by net direction over 5 days."""
    op = df["open_adj"]
    cl = df["close_adj"]
    hi = df["high_adj"]
    lo = df["low_adj"]
    body_eff = (cl - op).abs() / (hi - lo + 1e-8)
    avg_eff = body_eff.rolling(5).mean()
    # Sign by 5-day net return
    net_ret = cl - cl.shift(5)
    signed_eff = avg_eff * np.sign(net_ret)
    return signed_eff.clip(-1, 1).shift(1)


def calc_overnight_gap_trend_5d(df: pd.DataFrame) -> pd.Series:
    """5-day cumulative overnight gap direction.
    Persistent positive gaps = institutional buying at open (bull trend).
    Persistent negative gaps = distribution (bear trend).
    Normalized by 5-day range."""
    op = df["open_adj"]
    cl = df["close_adj"]
    prev_cl = cl.shift(1)
    gap = (op - prev_cl) / (prev_cl + 1e-8)
    cum_gap = gap.rolling(5).sum()
    # Normalize by 5-day average range
    rng = ((df["high_adj"] - df["low_adj"]) / (cl + 1e-8)).rolling(5).mean()
    norm = cum_gap / (rng + 1e-8)
    return norm.clip(-3, 3).div(3).shift(1)


DAY_CANDIDATES = {
    # Wave 1 (original)
    "dual_thrust_range_ratio": calc_dual_thrust_range_ratio,
    "range_compression_3d": calc_range_compression_3d,
    "return_acceleration_3d": calc_return_acceleration_3d,
    "volume_price_corr_5d": calc_volume_price_corr_5d,
    "gap_persistence_3d": calc_gap_persistence_3d,
    "close_trend_consistency_5d": calc_close_trend_consistency_5d,
    "overnight_intraday_decomp_3d": calc_overnight_intraday_decomp_3d,
    "position_in_3d_range": calc_position_in_3d_range,
    "body_accumulation_5d": calc_body_accumulation_5d,
    "volume_weighted_return_3d": calc_volume_weighted_return_3d,
    "higher_high_streak": calc_higher_high_streak,
    "range_expansion_velocity": calc_range_expansion_velocity,
    "multi_day_vwap_deviation": calc_multi_day_vwap_deviation,
    # Wave 2 (refined multi-day)
    "dual_thrust_range_ratio_5d": calc_dual_thrust_range_ratio_5d,
    "close_location_in_range_3d": calc_close_location_in_range_3d,
    "volume_trend_3d": calc_volume_trend_3d,
    "inside_day_count_5d": calc_inside_day_count_5d,
    "atr_acceleration_3d": calc_atr_acceleration_3d,
    "consecutive_close_direction": calc_consecutive_close_direction,
    "range_position_momentum": calc_range_position_momentum,
    "open_close_reversal_3d": calc_open_close_reversal_3d,
    # Wave 3 (Market Regime & Big Trend Factors)
    "adx_14d": calc_adx_14d,
    "ema_ribbon_width": calc_ema_ribbon_width,
    "donchian_breakout_proximity_20d": calc_donchian_breakout_proximity_20d,
    "trend_persistence_hurst_proxy": calc_trend_persistence_hurst_proxy,
    "buying_selling_pressure_10d": calc_buying_selling_pressure_10d,
    "trend_maturity_bars_since_reversal": calc_trend_maturity_bars_since_reversal,
    "spike_quality_5d": calc_spike_quality_5d,
    "volatility_compression_breakout_setup": calc_volatility_compression_breakout_setup,
    "directional_movement_efficiency_10d": calc_directional_movement_efficiency_10d,
    "channel_width_trend_5d": calc_channel_width_trend_5d,
    "new_high_low_momentum_10d": calc_new_high_low_momentum_10d,
    "volume_weighted_close_momentum_10d": calc_volume_weighted_close_momentum_10d,
    "trend_line_distance_10d": calc_trend_line_distance_10d,
    "consecutive_ema20_above_days": calc_consecutive_ema20_above_days,
    "multi_day_body_efficiency_5d": calc_multi_day_body_efficiency_5d,
    "overnight_gap_trend_5d": calc_overnight_gap_trend_5d,
}


def main():
    print("=== Multi-Day Feature Mining (Batch 4: Past 2-5 Day Structure) ===")
    print(f"Candidates: {len(DAY_CANDIDATES)}")
    results = []

    etf_list = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]

    for etf in etf_list:
        print(f"\n{'='*60}")
        print(f"Evaluating multi-day candidates on {etf}...")
        print(f"{'='*60}")

        # Load feature parquet for target and dates
        feat_file = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not feat_file.exists():
            print(f"  Skipping {etf}: {feat_file} does not exist")
            continue

        df_feat = pd.read_parquet(feat_file)
        y = df_feat["trade_return"].values
        dates = df_feat.index

        # Load daily 1d data
        file_1d = ETF_CONFIG[etf]["file_1d"]
        df_1d_path = DATA_DIR / file_1d
        if not df_1d_path.exists():
            # Try index data
            file_1d = INDEX_CONFIG[etf]["file_1d"]
            df_1d_path = DATA_DIR / file_1d
        if not df_1d_path.exists():
            print(f"  Skipping {etf}: 1d data not found")
            continue

        df_1d = pd.read_parquet(df_1d_path)
        df_1d["date"] = pd.to_datetime(df_1d["date"])
        df_1d = df_1d.sort_values("date").reset_index(drop=True)

        # Compute all candidate features on daily data
        candidate_series = {}
        for name, fn in DAY_CANDIDATES.items():
            try:
                s = fn(df_1d)
                candidate_series[name] = s
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
                continue

        # Map daily features to feature-parquet dates
        date_to_idx = {d.date(): i for i, d in enumerate(df_1d["date"])}

        for name, series in candidate_series.items():
            # Align: for each date in feature parquet, get the day-level feature value
            feat_values = []
            valid_mask = []
            for dt in dates:
                d = pd.to_datetime(dt).date()
                if d in date_to_idx:
                    idx = date_to_idx[d]
                    val = series.iloc[idx]
                    if pd.notna(val):
                        feat_values.append(val)
                        valid_mask.append(True)
                    else:
                        feat_values.append(0.0)
                        valid_mask.append(False)
                else:
                    feat_values.append(0.0)
                    valid_mask.append(False)

            x = np.array(feat_values, dtype=np.float64)
            valid = np.array(valid_mask)

            if valid.sum() < 100:
                print(f"  {name:40s} | Insufficient valid data ({valid.sum()} days)")
                continue

            if np.std(x[valid]) < 1e-8:
                print(f"  {name:40s} | Zero variance")
                continue

            # Evaluate only on valid samples
            x_valid = x[valid]
            y_valid = y[valid]
            dates_valid = dates[valid]

            metrics = compute_yearly_ic(x_valid, y_valid, dates_valid)

            gate_pass = (
                metrics["ic_cv"] <= 3.0
                and metrics["n_neg_years"] <= 2
                and metrics["jackknife_pass"]
                and abs(metrics["mean_ic"]) >= 0.02
            )

            res_record = {
                "feature_name": name,
                "etf": etf,
                "overall_ic": round(metrics["mean_ic"], 6),
                "ic_cv": round(metrics["ic_cv"], 4),
                "n_neg_years": metrics["n_neg_years"],
                "jackknife_pass": metrics["jackknife_pass"],
                "flips": metrics["flips"],
                "gate_pass": gate_pass,
                "n_valid": int(valid.sum()),
            }
            results.append(res_record)
            status = "PASS" if gate_pass else "REJECT"
            print(f"  {name:40s} | IC={metrics['mean_ic']:+.4f} | CV={metrics['ic_cv']:.2f} | "
                  f"NegYrs={metrics['n_neg_years']} | JK={metrics['jackknife_pass']} | "
                  f"N={valid.sum()} => {status}")

    # Export results
    csv_path = HERE / "mined_multiday_candidates.csv"
    fieldnames = ["feature_name", "etf", "overall_ic", "ic_cv", "n_neg_years",
                  "jackknife_pass", "flips", "gate_pass", "n_valid"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved screening results to: {csv_path}")

    # Summary
    passing = [r for r in results if r["gate_pass"]]
    print(f"\n{'='*60}")
    print(f"=== Gate-Passing Multi-Day Features ({len(passing)}/{len(results)}) ===")
    print(f"{'='*60}")
    if passing:
        # Group by feature
        from collections import defaultdict
        feat_summary = defaultdict(list)
        for p in passing:
            feat_summary[p["feature_name"]].append(p)
        for fname, records in sorted(feat_summary.items(), key=lambda x: -len(x[1])):
            etfs_passed = [r["etf"] for r in records]
            ics = [r["overall_ic"] for r in records]
            cvs = [r["ic_cv"] for r in records]
            print(f"\n  {fname} — PASSED on {len(records)}/5 ETFs")
            print(f"    ETFs: {etfs_passed}")
            print(f"    IC range: [{min(ics):+.4f}, {max(ics):+.4f}]")
            print(f"    IC_CV range: [{min(cvs):.2f}, {max(cvs):.2f}]")
    else:
        print("  No features passed all 4 gates.")


if __name__ == "__main__":
    main()
