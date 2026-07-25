"""
Mining & Screening Script for Big Trend / Market Regime Primitives (Wave 4).

Motivation
----------
newtrade/artifacts/rank_bounded_equity.png + day-model-new/BASELINE_REPORT.md
show regime/trend discrimination weakness:
  - 300ETF single OOS IC = +0.0651*  (CI spans 0)
  - 588000ETF single OOS IC = -0.0135* (sign-flip vs train)
  - All long/short sides have 0 admitted features
AL Brooks (ideas/Albrooks.md Ch11-13, 20 Gap Bars, Always-In) + ideas/strategies
(trend-following, ADX, SuperTrend, Keltner, Donchian) both say BIG TREND FACTOR
is the missing axis. Prior mining already covered basic intraday trend bars
(Batches 4-5) and basic multi-day (Wave 3 ADX/Hurst proxy). Most of those
Hurst/ADX/trend-maturity proxies FAILED gates (CV too high, sign flips).

This Wave 4 batch targets mechanisms NOT yet covered:
  1. Direct trend-strength classifiers (Kaufman ER, Choppiness Index,
     close-close autocorr, variance ratio, proper R/S Hurst).
  2. MA stack alignment (multi-timeframe consensus) + crossover age (trend maturity).
  3. Channel-based regime (Keltner position, SuperTrend ATR trailing, Donchian age/width).
  4. Brooks trend quality (HH+HL stair-step, distribution/accumulation days,
     trend-day count, climax reversal).
  5. Trend acceleration (2nd derivative via MACD-hist slope, EMA-slope ratio, RSI slope).
  6. Brooks multi-day candle structure (outside days, 2-day reversals, WRBs, NR4).
  7. Volatility regime (realized vol z-score, range percentile, BB width z-score).

All features are day-level (computed on daily OHLCV, shifted by 1 upstream).
All outputs bounded to [-1, 1] or [0, 1] for stationarity. Same 4-gate screen
as dig_multiday_candidates.py: IC_CV<=3.0, n_neg_years<=2, 7Y Jackknife pass,
|IC|>=0.02.
"""
import sys
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
        return {"mean_ic": 0.0, "ic_cv": 999.0, "n_neg_years": 999,
                "jackknife_pass": False, "flips": 999}
    arr = np.array(yearly_ics)
    mean_ic = float(np.mean(arr))
    std_ic = float(np.std(arr))
    ic_cv = abs(std_ic / (mean_ic + 1e-8)) if abs(mean_ic) > 1e-6 else 999.0
    n_neg = int(np.sum(arr < 0)) if mean_ic > 0 else int(np.sum(arr > 0))

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
    jackknife_pass = (flips <= 1) and (len(chunk_signs) >= 2
                                       and chunk_signs[-1] > 0 and chunk_signs[-2] > 0)
    return {"mean_ic": mean_ic, "std_ic": std_ic, "ic_cv": ic_cv,
            "n_neg_years": n_neg, "jackknife_pass": jackknife_pass, "flips": flips}


# ============================================================
# Helper primitives
# ============================================================
def _atr(df: pd.DataFrame, n: int) -> pd.Series:
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    prev_cl = cl.shift(1)
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(),
                    (lo - prev_cl).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def _ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def _rolling_slope(s: pd.Series, n: int) -> pd.Series:
    """OLS slope over rolling window n. Normalized by series mean."""
    x = np.arange(n, dtype=np.float64)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()
    if x_var < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index)
    def _sl(v):
        if len(v) < n:
            return 0.0
        y = v
        y_mean = y.mean()
        return ((x - x_mean) * (y - y_mean)).sum() / x_var
    return s.rolling(n).apply(_sl, raw=True)


def _run_length_streak(flags: np.ndarray) -> np.ndarray:
    out = np.zeros(len(flags), dtype=np.float64)
    run = 0
    for i, f in enumerate(flags):
        if f:
            run += 1
        else:
            run = 0
        out[i] = run
    return out


# ============================================================
# Section 1 — Trend Strength / Regime Classifiers
# ============================================================

def calc_kaufman_efficiency_ratio_10d(df: pd.DataFrame) -> pd.Series:
    """Kaufman ER: |close - close_10d_ago| / sum(|daily changes|) over 10d.
    Direction-signed: ER * sign(net change). High |ER| = clean trend.
    Smoothed ER (3-day mean) reduces noise. Returns [-1, 1]."""
    cl = df["close_adj"]
    net = (cl - cl.shift(10)).abs()
    daily_abs = (cl - cl.shift(1)).abs().rolling(10).sum()
    er = net / (daily_abs + 1e-8)
    signed_er = er * np.sign(cl - cl.shift(10))
    # 3-day smoothing for stability
    return signed_er.rolling(3).mean().clip(-1, 1).shift(1)


def calc_kaufman_efficiency_ratio_20d(df: pd.DataFrame) -> pd.Series:
    """Kaufman ER over 20-day window. Longer regime filter."""
    cl = df["close_adj"]
    net = (cl - cl.shift(20)).abs()
    daily_abs = (cl - cl.shift(1)).abs().rolling(20).sum()
    er = net / (daily_abs + 1e-8)
    signed_er = er * np.sign(cl - cl.shift(20))
    return signed_er.rolling(3).mean().clip(-1, 1).shift(1)


def calc_choppiness_index_14d(df: pd.DataFrame) -> pd.Series:
    """Bill Dreiss Choppiness Index over 14 days.
    CI = 100*log10(sum(ATR_1d) / (HH_14 - LL_14)) / log10(14)
    High (>61.8) = choppy/range, Low (<38.2) = trending.
    Returns: signed to [-1,1] via (50 - CI) / 50. Positive = trending, neg = choppy."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    prev_cl = cl.shift(1)
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(),
                    (lo - prev_cl).abs()], axis=1).max(axis=1)
    sum_tr = tr.rolling(14).sum()
    hh14 = hi.rolling(14).max()
    ll14 = lo.rolling(14).min()
    ci = 100.0 * np.log10(sum_tr / (hh14 - ll14 + 1e-8)) / np.log10(14.0)
    # Trending when CI < 50, choppy when CI > 50. Sign + center.
    signed = (50.0 - ci) / 50.0
    return signed.clip(-1, 1).shift(1)


def calc_close_close_autocorr_10d(df: pd.DataFrame) -> pd.Series:
    """Lag-1 autocorrelation of daily log returns over 10-day rolling window.
    Positive = trending/persistent, Negative = mean-reverting/choppy."""
    cl = df["close_adj"]
    ret = np.log(cl / cl.shift(1))
    # Rolling lag-1 autocorr
    def _ac(v):
        if len(v) < 5:
            return 0.0
        a = v[:-1]
        b = v[1:]
        ma, mb = a.mean(), b.mean()
        sa = np.sqrt(((a - ma) ** 2).mean())
        sb = np.sqrt(((b - mb) ** 2).mean())
        if sa < 1e-8 or sb < 1e-8:
            return 0.0
        return ((a - ma) * (b - mb)).mean() / (sa * sb)
    ac = ret.rolling(11).apply(_ac, raw=True)
    return ac.fillna(0).clip(-1, 1).shift(1)


def calc_variance_ratio_5_20d(df: pd.DataFrame) -> pd.Series:
    """Variance Ratio VR(5,20) = Var(5d return) / (5 * Var(1d return)).
    VR > 1 = trending (positive autocorr), VR < 1 = mean-reverting.
    Uses 20-day rolling windows. Returns centered/scaled to [-1,1]."""
    cl = df["close_adj"]
    ret1 = np.log(cl / cl.shift(1))
    ret5 = np.log(cl / cl.shift(5))
    var1 = ret1.rolling(20).var()
    var5 = ret5.rolling(20).var()
    vr = var5 / (5.0 * var1 + 1e-12)
    # Log-transform and clip. VR around 1 -> log ~ 0. CI: log(VR) in roughly [-1,1] meaningful range.
    log_vr = np.log(vr.clip(0.1, 10.0))
    return log_vr.clip(-1, 1).shift(1)


def calc_hurst_rs_30d(df: pd.DataFrame) -> pd.Series:
    """Proper Hurst exponent via Rescaled Range (R/S) over 30-day rolling window.
    H > 0.5 = trending, H < 0.5 = mean-reverting, H ~ 0.5 = random walk.
    Returns centered: (H - 0.5) * 2 in [-1, 1]."""
    cl = df["close_adj"]
    ret = np.log(cl / cl.shift(1)).values
    n_total = len(ret)

    def _hurst(window):
        w = window[~np.isnan(window)]
        n = len(w)
        if n < 20:
            return 0.0
        # Divide into 2-3 sub-samples of equal length, compute mean R/S
        rs_list = []
        for k in [2, 3]:
            if n % k != 0:
                continue
            chunk = n // k
            for ci in range(k):
                sub = w[ci * chunk:(ci + 1) * chunk]
                mean = sub.mean()
                dev = sub - mean
                cum = np.cumsum(dev)
                R = cum.max() - cum.min()
                S = sub.std()
                if S > 1e-8:
                    rs_list.append(R / S)
        if len(rs_list) < 2:
            return 0.0
        # Average R/S, scale by sqrt of avg chunk size
        avg_rs = np.mean(rs_list)
        avg_n = n // 2
        # H = log(R/S) / log(N) (simplified for fixed window)
        if avg_rs <= 0 or avg_n <= 1:
            return 0.0
        H = np.log(avg_rs) / np.log(avg_n)
        return float(np.clip(H, 0.0, 1.0))

    hurst = pd.Series(np.zeros(n_total), index=df.index)
    valid_ret = pd.Series(ret, index=df.index)
    hurst_vals = valid_ret.rolling(30).apply(_hurst, raw=True)
    centered = (hurst_vals - 0.5) * 2.0
    return centered.fillna(0).clip(-1, 1).shift(1)


# ============================================================
# Section 2 — Multi-Timeframe MA Stack Alignment
# ============================================================

def calc_ma_alignment_score_5_10_20_50(df: pd.DataFrame) -> pd.Series:
    """MA stack alignment: count of correctly-ordered pairs among (5,10,20,50) EMAs.
    Bull stack: EMA5 > EMA10 > EMA20 > EMA50. 6 pairs total (C(4,2)).
    Score = (#bull-aligned - #bear-aligned) / 6 in [-1,1]."""
    cl = df["close_adj"]
    e5 = _ema(cl, 5)
    e10 = _ema(cl, 10)
    e20 = _ema(cl, 20)
    e50 = _ema(cl, 50)
    emas = [e5, e10, e20, e50]
    bull_pairs = 0
    bear_pairs = 0
    n_pairs = 0
    for i in range(len(emas)):
        for j in range(i + 1, len(emas)):
            n_pairs += 1
            diff = emas[i] - emas[j]
            bull_pairs = bull_pairs + (diff > 0).astype(int)
            bear_pairs = bear_pairs + (diff < 0).astype(int)
    score = (bull_pairs - bear_pairs) / float(n_pairs)
    return pd.Series(score, index=df.index).clip(-1, 1).shift(1)


def calc_ma_alignment_score_5_10_20(df: pd.DataFrame) -> pd.Series:
    """Triple MA stack (5/10/20). Faster-responding than the 4-MA version.
    Score = (#bull - #bear) / 3."""
    cl = df["close_adj"]
    e5 = _ema(cl, 5)
    e10 = _ema(cl, 10)
    e20 = _ema(cl, 20)
    emas = [e5, e10, e20]
    bull = 0
    bear = 0
    n = 0
    for i in range(len(emas)):
        for j in range(i + 1, len(emas)):
            n += 1
            d = emas[i] - emas[j]
            bull = bull + (d > 0).astype(int)
            bear = bear + (d < 0).astype(int)
    score = (bull - bear) / float(n)
    return pd.Series(score, index=df.index).clip(-1, 1).shift(1)


def calc_ma50_slope_normalized_10d(df: pd.DataFrame) -> pd.Series:
    """10-day slope of 50-day EMA, normalized by ATR14.
    Captures long-term trend direction & acceleration."""
    cl = df["close_adj"]
    e50 = _ema(cl, 50)
    slope = _rolling_slope(e50, 10)
    atr14 = _atr(df, 14)
    norm = slope / (atr14 + 1e-8)
    return (norm / 3.0).clip(-1, 1).shift(1)


def calc_ma_crossover_age_5_20(df: pd.DataFrame) -> pd.Series:
    """Bars since 5/20 EMA crossover, signed by current direction.
    Young trend (low age) = continuation, mature = exhaustion risk.
    Normalized: sign * (1 - age/30), so recent cross has high magnitude."""
    cl = df["close_adj"]
    e5 = _ema(cl, 5)
    e20 = _ema(cl, 20)
    above = (e5 > e20).astype(int).values
    cross = (np.diff(above, prepend=above[0]) != 0).astype(int)
    bars_since = _run_length_streak(cross)
    direction = np.where(above == 1, 1.0, -1.0)
    # Recent cross = high magnitude; older = decays to 0
    magnitude = 1.0 - np.minimum(bars_since / 30.0, 1.0)
    val = direction * magnitude
    return pd.Series(val, index=df.index).clip(-1, 1).shift(1)


def calc_close_above_ma50_pct_20d(df: pd.DataFrame) -> pd.Series:
    """% of last 20 days where close > EMA50. Centered to [-1,1]."""
    cl = df["close_adj"]
    e50 = _ema(cl, 50)
    above = (cl > e50).astype(float)
    pct = above.rolling(20).mean()
    centered = (pct - 0.5) * 2.0
    return centered.clip(-1, 1).shift(1)


def calc_close_to_ema21_distance(df: pd.DataFrame) -> pd.Series:
    """Distance of close from 21-day EMA normalized by ATR14.
    Brooks 21 EMA gap distance: large gap = trend impulse/exhaustion.
    Signed: positive = above (bullish extension), negative = below."""
    cl = df["close_adj"]
    e21 = _ema(cl, 21)
    atr14 = _atr(df, 14)
    dist = (cl - e21) / (atr14 + 1e-8)
    return (dist / 3.0).clip(-1, 1).shift(1)


# ============================================================
# Section 3 — Channel / Breakout Regime
# ============================================================

def calc_keltner_position_20d(df: pd.DataFrame) -> pd.Series:
    """Position of close within 20-day Keltner Channel (EMA20 ± 2*ATR10).
    +1 = at upper band, -1 = at lower band, 0 = mid.
    Captures channel extension (overbought/oversold in trend)."""
    cl = df["close_adj"]
    mid = _ema(cl, 20)
    atr10 = _atr(df, 10)
    upper = mid + 2.0 * atr10
    lower = mid - 2.0 * atr10
    pos = (cl - mid) / ((upper - lower) / 2.0 + 1e-8)
    return pos.clip(-1, 1).shift(1)


def calc_supertrend_proxy_dir_10_2(df: pd.DataFrame) -> pd.Series:
    """SuperTrend proxy: 10-day ATR trailing stop, 2x multiplier.
    Direction flips when close crosses stop. Returns +1 (bull regime),
    -1 (bear regime), smoothed by 3-day majority vote."""
    cl = df["close_adj"]
    atr10 = _atr(df, 10)
    mid = (cl + cl.shift(1)) / 2.0
    upper_band = mid + 2.0 * atr10
    lower_band = mid - 2.0 * atr10
    # Trailing stop logic
    n = len(cl)
    stop = np.full(n, np.nan)
    direction = np.ones(n)  # 1 = bull
    stop[0] = upper_band.iloc[0]
    for i in range(1, n):
        if cl.iloc[i] > stop[i - 1]:
            direction[i] = 1
            new_stop = lower_band.iloc[i]
            stop[i] = max(new_stop, stop[i - 1]) if direction[i - 1] == 1 else new_stop
        else:
            direction[i] = -1
            new_stop = upper_band.iloc[i]
            stop[i] = min(new_stop, stop[i - 1]) if direction[i - 1] == -1 else new_stop
    sig = pd.Series(direction.astype(float), index=df.index)
    # 3-day rolling majority vote for smoothing
    smooth = sig.rolling(3).mean()
    return smooth.fillna(0).clip(-1, 1).shift(1)


def calc_donchian_breakout_age_20d(df: pd.DataFrame) -> pd.Series:
    """Bars since last 20-day Donchian breakout, signed by direction.
    Recent breakout = trend continuation; old breakout = mature trend."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    hh20 = hi.rolling(20).max().shift(1)  # exclude current
    ll20 = lo.rolling(20).min().shift(1)
    bull_break = (hi > hh20).astype(int).values
    bear_break = (lo < ll20).astype(int).values
    bull_age = _run_length_streak_with_reset(bull_break, lookback=True)
    bear_age = _run_length_streak_with_reset(bear_break, lookback=True)
    # Most recent of the two
    direction = np.where(bull_age <= bear_age, 1.0, -1.0)
    age = np.minimum(bull_age, bear_age)
    magnitude = 1.0 - np.minimum(age / 20.0, 1.0)
    val = direction * magnitude
    return pd.Series(val, index=df.index).clip(-1, 1).shift(1)


def _run_length_streak_with_reset(flags: np.ndarray, lookback: bool = False) -> np.ndarray:
    """Days since most recent flag=1. Returns count; large = stale."""
    out = np.full(len(flags), 999, dtype=np.float64)
    last_seen = -999
    for i in range(len(flags)):
        if flags[i] == 1:
            last_seen = i
        out[i] = i - last_seen if last_seen > -999 else 999.0
    return out


def calc_donchian_width_atr_ratio_20d(df: pd.DataFrame) -> pd.Series:
    """20-day Donchian channel width / ATR14.
    Wide channel = strong directional regime; narrow = compression.
    Centered by 20-day median, signed by trend direction."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    width = hi.rolling(20).max() - lo.rolling(20).min()
    atr14 = _atr(df, 14)
    ratio = width / (atr14 + 1e-8)
    # Normalize: typical range 5-20. Center at 10, scale.
    norm = (ratio - 10.0) / 10.0
    # Sign with trend direction
    trend_sign = np.sign(cl - _ema(cl, 20))
    return (norm * trend_sign).clip(-1, 1).shift(1)


def calc_bollinger_width_zscore_60d(df: pd.DataFrame) -> pd.Series:
    """Z-score of Bollinger Band width against 60-day rolling mean.
    High z = vol expansion regime, Low z = compression regime.
    Signed by BB slope direction."""
    cl = df["close_adj"]
    sma20 = cl.rolling(20).mean()
    std20 = cl.rolling(20).std()
    bb_width = (2.0 * std20) / (sma20 + 1e-8)
    mean_60 = bb_width.rolling(60).mean()
    std_60 = bb_width.rolling(60).std()
    z = (bb_width - mean_60) / (std_60 + 1e-8)
    # Sign with EMA5 slope (direction of recent vol expansion)
    slope_sign = np.sign(_ema(cl, 5) - _ema(cl, 5).shift(3))
    return (z * slope_sign / 3.0).clip(-1, 1).shift(1)


# ============================================================
# Section 4 — Al Brooks Trend Quality
# ============================================================

def calc_trend_quality_hh_hl_5d(df: pd.DataFrame) -> pd.Series:
    """Count of Higher Highs AND Higher Lows in last 5 days (bull quality)
    minus Lower Highs AND Lower Lows (bear quality).
    Signed, normalized by 4 (max pairs)."""
    hi, lo = df["high_adj"], df["low_adj"]
    hh = (hi > hi.shift(1)).astype(int)
    hl = (lo > lo.shift(1)).astype(int)
    lh = (hi < hi.shift(1)).astype(int)
    ll = (lo < lo.shift(1)).astype(int)
    bull_q = (hh & hl).astype(int).rolling(5).sum()
    bear_q = (lh & ll).astype(int).rolling(5).sum()
    score = (bull_q - bear_q) / 4.0
    return score.clip(-1, 1).shift(1)


def calc_trend_quality_stair_step_5d(df: pd.DataFrame) -> pd.Series:
    """Strict stair-step: count of bars where HH AND HL (bull) or LH AND LL (bear),
    AND body aligned with direction. Cleaner trend = more stair-step bars."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    hh = (hi > hi.shift(1))
    hl = (lo > lo.shift(1))
    lh = (hi < hi.shift(1))
    ll = (lo < lo.shift(1))
    bull_body = (cl > op)
    bear_body = (cl < op)
    bull_stair = (hh & hl & bull_body).astype(int).rolling(5).sum()
    bear_stair = (lh & ll & bear_body).astype(int).rolling(5).sum()
    score = (bull_stair - bear_stair) / 5.0
    return score.clip(-1, 1).shift(1)


def calc_distribution_day_count_5d(df: pd.DataFrame) -> pd.Series:
    """Al Brooks distribution day: high-volume bearish close in lower 25% of range.
    Count in last 5 days, signed negative (bearish pressure)."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    vol = df["volume"]
    rng = hi - lo + 1e-8
    close_pos = (cl - lo) / rng
    vol_ma20 = vol.rolling(20).mean()
    high_vol = (vol > 1.2 * vol_ma20)
    dist = (high_vol & (close_pos < 0.25) & (cl < op)).astype(int)
    count = dist.rolling(5).sum()
    return -(count / 5.0).clip(-1, 0).shift(1)


def calc_accumulation_day_count_5d(df: pd.DataFrame) -> pd.Series:
    """Al Brooks accumulation day: high-volume bullish close in upper 25% of range.
    Count in last 5 days."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    vol = df["volume"]
    rng = hi - lo + 1e-8
    close_pos = (cl - lo) / rng
    vol_ma20 = vol.rolling(20).mean()
    high_vol = (vol > 1.2 * vol_ma20)
    acc = (high_vol & (close_pos > 0.75) & (cl > op)).astype(int)
    count = acc.rolling(5).sum()
    return (count / 5.0).clip(0, 1).shift(1)


def calc_climax_volume_reversal_3d(df: pd.DataFrame) -> pd.Series:
    """3-day climax reversal (CAUSAL — no shift(-1) lookahead).
    A climax day = max-volume in 5d AND closed in lower 30% (bear climax)
    or upper 70% (bull climax). Reversal confirmed when TODAY's close is
    on opposite side of the climax day's close.
    Returns: positive = bullish reversal underway, negative = bearish."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    vol = df["volume"]
    rng = hi - lo + 1e-8
    close_pos = (cl - lo) / rng
    vol_max_5d = vol.rolling(5).max()
    is_climax = (vol >= vol_max_5d * 0.999) & (vol > 1.5 * vol.rolling(20).mean())
    # Bear climax: high vol + closed near low. Mark with its close price.
    bear_climax_flag = (is_climax & (close_pos < 0.3)).astype(float)
    bull_climax_flag = (is_climax & (close_pos > 0.7)).astype(float)
    # Track most recent bear/bull climax close in past 3 days
    bear_climax_close = (bear_climax_flag * cl).replace(0.0, np.nan)
    bull_climax_close = (bull_climax_flag * cl).replace(0.0, np.nan)
    # Most recent climax close in past 3 days (forward-fill within window)
    def _last_valid(arr):
        v = arr[~np.isnan(arr)]
        return v[-1] if len(v) > 0 else np.nan
    last_bear_close = bear_climax_close.rolling(3, min_periods=1).apply(_last_valid, raw=True)
    last_bull_close = bull_climax_close.rolling(3, min_periods=1).apply(_last_valid, raw=True)
    # Reversal confirmed by today's close crossing back past climax close
    bull_reversal = last_bear_close.notna() & (cl > last_bear_close.fillna(cl + 1))
    bear_reversal = last_bull_close.notna() & (cl < last_bull_close.fillna(cl - 1))
    score = bull_reversal.astype(int) - bear_reversal.astype(int)
    return pd.Series(score, index=df.index).clip(-1, 1).shift(1)


def calc_trend_day_count_5d(df: pd.DataFrame) -> pd.Series:
    """Al Brooks Trend Day count: |close-open|/range > 0.7 AND |net move| > 0.5*ATR.
    Signed by direction. Counts in last 5 days."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    rng = hi - lo + 1e-8
    body_ratio = (cl - op).abs() / rng
    atr14 = _atr(df, 14)
    net = (cl - op).abs()
    is_trend_day = (body_ratio > 0.7) & (net > 0.5 * atr14)
    direction = np.sign(cl - op)
    bull_td = (is_trend_day & (direction > 0)).astype(int).rolling(5).sum()
    bear_td = (is_trend_day & (direction < 0)).astype(int).rolling(5).sum()
    score = (bull_td - bear_td) / 5.0
    return score.clip(-1, 1).shift(1)


# ============================================================
# Section 5 — Trend Acceleration
# ============================================================

def calc_trend_acceleration_5_10d(df: pd.DataFrame) -> pd.Series:
    """5d EMA slope - 10d EMA slope (over 5 days each), normalized by ATR.
    Positive = trend accelerating, Negative = decelerating/maturing."""
    cl = df["close_adj"]
    e5 = _ema(cl, 5)
    e10 = _ema(cl, 10)
    slope5 = _rolling_slope(e5, 5)
    slope10 = _rolling_slope(e10, 5)
    atr14 = _atr(df, 14)
    accel = (slope5 - slope10) / (atr14 + 1e-8)
    return (accel / 2.0).clip(-1, 1).shift(1)


def calc_macd_histogram_slope_5d(df: pd.DataFrame) -> pd.Series:
    """Slope of MACD histogram (12,26,9) over 5 days.
    MACD-hist slope = momentum acceleration. Signed."""
    cl = df["close_adj"]
    e12 = _ema(cl, 12)
    e26 = _ema(cl, 26)
    macd = e12 - e26
    signal = _ema(macd, 9)
    hist = macd - signal
    slope = _rolling_slope(hist, 5)
    # Normalize by ATR
    atr14 = _atr(df, 14)
    norm = slope / (atr14 + 1e-8)
    return (norm / 2.0).clip(-1, 1).shift(1)


def calc_rsi_14_slope_5d(df: pd.DataFrame) -> pd.Series:
    """Slope of 14-day RSI over 5 days. RSI rising = momentum building."""
    cl = df["close_adj"]
    delta = cl.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / (loss + 1e-8)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    slope = _rolling_slope(rsi, 5)
    # Normalize: RSI slope of ~1/day is significant
    return (slope / 3.0).clip(-1, 1).shift(1)


def calc_macd_line_cross_age(df: pd.DataFrame) -> pd.Series:
    """Bars since MACD line crossed signal line, signed by direction.
    Young cross = fresh trend signal."""
    cl = df["close_adj"]
    e12 = _ema(cl, 12)
    e26 = _ema(cl, 26)
    macd = e12 - e26
    signal = _ema(macd, 9)
    above = (macd > signal).astype(int).values
    cross = (np.diff(above, prepend=above[0]) != 0).astype(int)
    bars_since = _run_length_streak(cross)
    direction = np.where(above == 1, 1.0, -1.0)
    magnitude = 1.0 - np.minimum(bars_since / 20.0, 1.0)
    val = direction * magnitude
    return pd.Series(val, index=df.index).clip(-1, 1).shift(1)


# ============================================================
# Section 6 — Multi-day Candle Structure (Brooks)
# ============================================================

def calc_outside_day_count_5d(df: pd.DataFrame) -> pd.Series:
    """Count of outside days (H > prev_H AND L < prev_L) in last 5 days.
    Outside days = volatility expansion + institutional interest.
    Signed by direction (close above mid = bullish, below = bearish)."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    outside = ((hi > hi.shift(1)) & (lo < lo.shift(1))).astype(int)
    rng = hi - lo + 1e-8
    close_pos = (cl - lo) / rng
    # Direction
    bull_outside = (outside.astype(bool) & (close_pos > 0.5)).astype(int)
    bear_outside = (outside.astype(bool) & (close_pos < 0.5)).astype(int)
    bull_count = bull_outside.rolling(5).sum()
    bear_count = bear_outside.rolling(5).sum()
    return ((bull_count - bear_count) / 5.0).clip(-1, 1).shift(1)


def calc_two_day_reversal_count_3d(df: pd.DataFrame) -> pd.Series:
    """2-day reversal: strong trend day followed by opposite trend day of similar size.
    Count in 3-day window. Reversal signal (Brooks)."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    body = cl - op
    body_abs = body.abs()
    rng = hi - lo + 1e-8
    body_ratio = body_abs / rng
    # Strong trend day
    is_strong = body_ratio > 0.6
    # Reversal: today's body opposite sign, similar magnitude (>= 0.7x prev)
    rev = (is_strong & (np.sign(body) != np.sign(body.shift(1))) &
           (body_abs > 0.7 * body_abs.shift(1))).astype(int)
    direction = np.sign(body)  # direction of the reversal day
    bull_rev = (rev.astype(bool) & (direction > 0)).astype(int)
    bear_rev = (rev.astype(bool) & (direction < 0)).astype(int)
    bull_count = bull_rev.rolling(3).sum()
    bear_count = bear_rev.rolling(3).sum()
    return ((bull_count - bear_count) / 3.0).clip(-1, 1).shift(1)


def calc_wide_range_bar_count_5d(df: pd.DataFrame) -> pd.Series:
    """Wide Range Bar: range > 1.5x 20-day avg range. Count in 5d, signed by close direction.
    Brooks: WRBs indicate institutional conviction / breakout."""
    hi, lo, op, cl = df["high_adj"], df["low_adj"], df["open_adj"], df["close_adj"]
    rng = hi - lo
    avg_rng = rng.rolling(20).mean()
    wrb = (rng > 1.5 * avg_rng).astype(int)
    direction = np.sign(cl - op)
    bull_wrb = (wrb.astype(bool) & (direction > 0)).astype(int)
    bear_wrb = (wrb.astype(bool) & (direction < 0)).astype(int)
    bull_count = bull_wrb.rolling(5).sum()
    bear_count = bear_wrb.rolling(5).sum()
    return ((bull_count - bear_count) / 5.0).clip(-1, 1).shift(1)


def calc_narrow_range_streak_4(df: pd.DataFrame) -> pd.Series:
    """NR4 / NR7 streak: consecutive days where range < prior range (compression).
    Brooks/Toby Crabel: NR7 often precedes volatility expansion.
    Returns: max streak / 5, positive (compression regime)."""
    hi, lo = df["high_adj"], df["low_adj"]
    rng = hi - lo
    declining = (rng < rng.shift(1)).astype(int).values
    streak = _run_length_streak(declining)
    # Cap and normalize
    val = np.minimum(streak / 5.0, 1.0)
    return pd.Series(val, index=df.index).clip(0, 1).shift(1)


# ============================================================
# Section 7 — Volatility Regime
# ============================================================

def calc_realized_vol_zscore_20d(df: pd.DataFrame) -> pd.Series:
    """Z-score of 10-day realized vol against 250-day mean.
    High z = elevated vol regime, Low z = quiet regime."""
    cl = df["close_adj"]
    ret = np.log(cl / cl.shift(1))
    rv = ret.rolling(10).std() * np.sqrt(252)
    mean = rv.rolling(250, min_periods=60).mean()
    std = rv.rolling(250, min_periods=60).std()
    z = (rv - mean) / (std + 1e-8)
    return (z / 3.0).clip(-1, 1).shift(1)


def calc_range_percentile_60d(df: pd.DataFrame) -> pd.Series:
    """Percentile rank of today's range within 60-day range history.
    Centered to [-1, 1]."""
    hi, lo = df["high_adj"], df["low_adj"]
    rng = hi - lo
    pct = rng.rolling(60).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
    centered = (pct - 0.5) * 2.0
    return centered.fillna(0).clip(-1, 1).shift(1)


def calc_volume_regime_zscore_20d(df: pd.DataFrame) -> pd.Series:
    """Z-score of today's volume vs 60-day mean.
    Captures volume surge/dryup regime."""
    vol = df["volume"]
    mean = vol.rolling(60, min_periods=20).mean()
    std = vol.rolling(60, min_periods=20).std()
    z = (vol - mean) / (std + 1e-8)
    return (z / 3.0).clip(-1, 1).shift(1)


def calc_bollinger_pctb_slope_5d(df: pd.DataFrame) -> pd.Series:
    """Slope of %B (close position within Bollinger Bands) over 5 days.
    Rising %B = price moving toward/above upper band (bullish momentum)."""
    cl = df["close_adj"]
    sma20 = cl.rolling(20).mean()
    std20 = cl.rolling(20).std()
    pct_b = (cl - sma20) / (2 * std20 + 1e-8)
    slope = _rolling_slope(pct_b, 5)
    return slope.clip(-1, 1).shift(1)


def calc_atr_percentile_rank_60d(df: pd.DataFrame) -> pd.Series:
    """Percentile rank of ATR14 within its 60-day history.
    High percentile = vol expansion regime, low = compression."""
    atr14 = _atr(df, 14)
    pct = atr14.rolling(60).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)
    centered = (pct - 0.5) * 2.0
    return centered.fillna(0).clip(-1, 1).shift(1)


# ============================================================
# Section 8 — Composite Regime Score
# ============================================================

def calc_trend_persistence_composite(df: pd.DataFrame) -> pd.Series:
    """Composite trend persistence score: average of sign-aligned
    (Kaufman ER_10, close-close autocorr, variance ratio sign).
    Robust single-number trend regime classifier."""
    cl = df["close_adj"]
    # ER 10d
    net = (cl - cl.shift(10)).abs()
    daily_abs = (cl - cl.shift(1)).abs().rolling(10).sum()
    er = net / (daily_abs + 1e-8)
    signed_er = er * np.sign(cl - cl.shift(10))
    # Lag-1 autocorr (rolling 11)
    ret = np.log(cl / cl.shift(1))
    def _ac(v):
        if len(v) < 5:
            return 0.0
        a = v[:-1]; b = v[1:]
        ma, mb = a.mean(), b.mean()
        sa = np.sqrt(((a - ma) ** 2).mean())
        sb = np.sqrt(((b - mb) ** 2).mean())
        if sa < 1e-8 or sb < 1e-8:
            return 0.0
        return ((a - ma) * (b - mb)).mean() / (sa * sb)
    ac = ret.rolling(11).apply(_ac, raw=True).fillna(0)
    # VR sign
    var1 = ret.rolling(20).var()
    var5 = (np.log(cl / cl.shift(5))).rolling(20).var()
    vr = var5 / (5 * var1 + 1e-12)
    vr_sign = np.tanh(np.log(vr.clip(0.1, 10)))  # smooth sign-strength
    composite = (signed_er + ac + vr_sign) / 3.0
    return composite.clip(-1, 1).shift(1)


def calc_directional_probability_5d(df: pd.DataFrame) -> pd.Series:
    """Brooks 'Directional Probability': % of last 5 days trending in bull direction
    weighted by body size. High DP = strong bull regime."""
    op, cl = df["open_adj"], df["close_adj"]
    body = cl - op
    bull_strength = body.where(body > 0, 0.0).rolling(5).sum()
    bear_strength = (-body.where(body < 0, 0.0)).rolling(5).sum()
    total = bull_strength + bear_strength + 1e-8
    dp = (bull_strength - bear_strength) / total
    return dp.clip(-1, 1).shift(1)


# ============================================================
# Registry
# ============================================================
TREND_CANDIDATES = {
    # Section 1: Trend strength / regime classifiers
    "kaufman_efficiency_ratio_10d": calc_kaufman_efficiency_ratio_10d,
    "kaufman_efficiency_ratio_20d": calc_kaufman_efficiency_ratio_20d,
    "choppiness_index_14d": calc_choppiness_index_14d,
    "close_close_autocorr_10d": calc_close_close_autocorr_10d,
    "variance_ratio_5_20d": calc_variance_ratio_5_20d,
    "hurst_rs_30d": calc_hurst_rs_30d,
    # Section 2: MA stack alignment
    "ma_alignment_score_5_10_20_50": calc_ma_alignment_score_5_10_20_50,
    "ma_alignment_score_5_10_20": calc_ma_alignment_score_5_10_20,
    "ma50_slope_normalized_10d": calc_ma50_slope_normalized_10d,
    "ma_crossover_age_5_20": calc_ma_crossover_age_5_20,
    "close_above_ma50_pct_20d": calc_close_above_ma50_pct_20d,
    "close_to_ema21_distance": calc_close_to_ema21_distance,
    # Section 3: Channel / breakout regime
    "keltner_position_20d": calc_keltner_position_20d,
    "supertrend_proxy_dir_10_2": calc_supertrend_proxy_dir_10_2,
    "donchian_breakout_age_20d": calc_donchian_breakout_age_20d,
    "donchian_width_atr_ratio_20d": calc_donchian_width_atr_ratio_20d,
    "bollinger_width_zscore_60d": calc_bollinger_width_zscore_60d,
    # Section 4: Brooks trend quality
    "trend_quality_hh_hl_5d": calc_trend_quality_hh_hl_5d,
    "trend_quality_stair_step_5d": calc_trend_quality_stair_step_5d,
    "distribution_day_count_5d": calc_distribution_day_count_5d,
    "accumulation_day_count_5d": calc_accumulation_day_count_5d,
    "climax_volume_reversal_3d": calc_climax_volume_reversal_3d,
    "trend_day_count_5d": calc_trend_day_count_5d,
    # Section 5: Trend acceleration
    "trend_acceleration_5_10d": calc_trend_acceleration_5_10d,
    "macd_histogram_slope_5d": calc_macd_histogram_slope_5d,
    "rsi_14_slope_5d": calc_rsi_14_slope_5d,
    "macd_line_cross_age": calc_macd_line_cross_age,
    # Section 6: Multi-day candle structure
    "outside_day_count_5d": calc_outside_day_count_5d,
    "two_day_reversal_count_3d": calc_two_day_reversal_count_3d,
    "wide_range_bar_count_5d": calc_wide_range_bar_count_5d,
    "narrow_range_streak_4": calc_narrow_range_streak_4,
    # Section 7: Volatility regime
    "realized_vol_zscore_20d": calc_realized_vol_zscore_20d,
    "range_percentile_60d": calc_range_percentile_60d,
    "volume_regime_zscore_20d": calc_volume_regime_zscore_20d,
    "bollinger_pctb_slope_5d": calc_bollinger_pctb_slope_5d,
    "atr_percentile_rank_60d": calc_atr_percentile_rank_60d,
    # Section 8: Composite
    "trend_persistence_composite": calc_trend_persistence_composite,
    "directional_probability_5d": calc_directional_probability_5d,
}


def main():
    print("=== Wave 4: Big Trend / Market Regime Feature Mining ===")
    print(f"Candidates: {len(TREND_CANDIDATES)}")
    results = []

    etf_list = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]

    for etf in etf_list:
        print(f"\n{'='*60}")
        print(f"Evaluating trend/regime candidates on {etf}...")
        print(f"{'='*60}")

        feat_file = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not feat_file.exists():
            print(f"  Skipping {etf}: {feat_file} does not exist")
            continue

        df_feat = pd.read_parquet(feat_file)
        y = df_feat["trade_return"].values
        dates = df_feat.index

        # Load ETF 1d (preferred — has _adj columns)
        file_1d = ETF_CONFIG[etf]["file_1d"]
        df_1d_path = DATA_DIR / file_1d
        if not df_1d_path.exists():
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
        for name, fn in TREND_CANDIDATES.items():
            try:
                s = fn(df_1d)
                candidate_series[name] = s
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
                continue

        date_to_idx = {d.date(): i for i, d in enumerate(df_1d["date"])}

        for name, series in candidate_series.items():
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

    csv_path = HERE / "mined_trend_regime_candidates.csv"
    fieldnames = ["feature_name", "etf", "overall_ic", "ic_cv", "n_neg_years",
                  "jackknife_pass", "flips", "gate_pass", "n_valid"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved screening results to: {csv_path}")

    passing = [r for r in results if r["gate_pass"]]
    print(f"\n{'='*60}")
    print(f"=== Gate-Passing Trend/Regime Features ({len(passing)}/{len(results)}) ===")
    print(f"{'='*60}")
    if passing:
        from collections import defaultdict
        feat_summary = defaultdict(list)
        for p in passing:
            feat_summary[p["feature_name"]].append(p)
        for fname, records in sorted(feat_summary.items(), key=lambda x: -len(x[1])):
            etfs_passed = [r["etf"] for r in records]
            ics = [r["overall_ic"] for r in records]
            cvs = [r["ic_cv"] for r in records]
            print(f"\n  {fname} -- PASSED on {len(records)}/5 ETFs")
            print(f"    ETFs: {etfs_passed}")
            print(f"    IC range: [{min(ics):+.4f}, {max(ics):+.4f}]")
            print(f"    IC_CV range: [{min(cvs):.2f}, {max(cvs):.2f}]")
    else:
        print("  No features passed all 4 gates.")


if __name__ == "__main__":
    main()
