"""
Wave 5 Feature Mining — 7 Untapped Feature Families.

Motivation
----------
Survey of features_extra.py shows ZERO coverage of:
  - Smart-money volume indicators (OBV, A/D, NVI, PVI, Force Index, MFI, PVT)
  - Path/distribution metrics (skewness, kurtosis, Ulcer, Pain, drawdown, MFE/MAE)
  - Cross-asset regime (5 ETFs as leading indicators / breadth)
  - Calendar/event (options expiry, month boundaries, pre-holiday)
  - Liquidity microstructure (Amihud, Roll spread, turnover/trade trend)
  - Higher-timeframe context (weekly, monthly, quarterly)
  - IV/VIX dynamics (rq_vix per-ETF)

This script mines ~45 candidates across these 7 families. Same 4-gate screen
as Wave 3/4: IC_CV<=3.0, n_neg_years<=2, 7Y Jackknife pass, |IC|>=0.02.

Data sources loaded once at startup:
  - Each ETF's 1d parquet (already has open_adj/high_adj/low_adj/close_adj/volume/turnover/num_trades)
  - rq_vix.parquet (per-ETF ATM IV, daily, indexed by date)
  - Cross-ETF: all 5 ETFs' 1d data for cross-asset features

All features shifted by 1 (causality) — when integrating into features_extra.py,
remove the trailing .shift(1) (upstream build_features.py:697 applies shift).
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
    ra = rankdata(a); rb = rankdata(b)
    ra = ra - ra.mean(); rb = rb - rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)


def compute_yearly_ic(x, y, dates):
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
        sx = x[c * chunk_size: (c + 1) * chunk_size]
        sy = y[c * chunk_size: (c + 1) * chunk_size]
        if len(sx) >= 10:
            cic = fast_spearman(sx, sy)
            chunk_signs.append(1 if cic * mean_ic > 0 else -1)
    flips = sum(1 for s in chunk_signs if s < 0)
    jk_pass = (flips <= 1) and (len(chunk_signs) >= 2 and chunk_signs[-1] > 0 and chunk_signs[-2] > 0)
    return {"mean_ic": mean_ic, "ic_cv": ic_cv, "n_neg_years": n_neg,
            "jackknife_pass": jk_pass, "flips": flips}


def _atr(df, n):
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    prev_cl = cl.shift(1)
    tr = pd.concat([(hi - lo).abs(), (hi - prev_cl).abs(),
                    (lo - prev_cl).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def _rolling_slope(s, n):
    x = np.arange(n, dtype=np.float64)
    xm = x.mean()
    xv = ((x - xm) ** 2).sum()
    if xv < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return s.rolling(n).apply(lambda v: ((x - xm) * (v - v.mean())).sum() / xv if len(v) == n else 0.0, raw=True)


# ============================================================
# Section 1 — Smart Money / Volume Indicators
# ============================================================

def calc_obv_slope_10d(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume slope over 10 days, normalized by 10d mean volume.
    Positive OBV slope = accumulation; negative = distribution."""
    cl = df["close_adj"]
    vol = df["volume"]
    sign = np.sign(cl.diff().fillna(0))
    obv = (sign * vol).cumsum()
    slope = (obv - obv.shift(10)) / 10.0
    norm = slope / (vol.rolling(10).mean() + 1e-8)
    return (norm / 10.0).clip(-1, 1).shift(1)


def calc_ad_line_slope_10d(df: pd.DataFrame) -> pd.Series:
    """Accumulation/Distribution line slope over 10 days.
    A/D = sum(((close-low) - (high-close)) / (high-low) * volume).
    Positive slope = buyers in control."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    vol = df["volume"]
    rng = hi - lo + 1e-8
    mf_mult = ((cl - lo) - (hi - cl)) / rng
    mf_vol = mf_mult * vol
    ad = mf_vol.cumsum()
    slope = (ad - ad.shift(10)) / 10.0
    norm = slope / (vol.rolling(10).mean() + 1e-8)
    return (norm / 10.0).clip(-1, 1).shift(1)


def calc_negative_volume_index_change(df: pd.DataFrame) -> pd.Series:
    """Negative Volume Index: smart money accumulates on quiet days.
    5-day pct change of NVI, normalized."""
    cl = df["close_adj"]
    vol = df["volume"]
    ret = cl.pct_change()
    quiet = (vol < vol.shift(1))
    # NVI starts at 1000; only updates on quiet days
    nvi = pd.Series(1000.0, index=df.index)
    for i in range(1, len(df)):
        if quiet.iloc[i]:
            nvi.iloc[i] = nvi.iloc[i - 1] * (1 + ret.iloc[i])
        else:
            nvi.iloc[i] = nvi.iloc[i - 1]
    change = (nvi - nvi.shift(5)) / nvi.shift(5)
    return change.clip(-1, 1).shift(1)


def calc_positive_volume_index_change(df: pd.DataFrame) -> pd.Series:
    """Positive Volume Index: retail activity on loud days."""
    cl = df["close_adj"]
    vol = df["volume"]
    ret = cl.pct_change()
    loud = (vol > vol.shift(1))
    pvi = pd.Series(1000.0, index=df.index)
    for i in range(1, len(df)):
        if loud.iloc[i]:
            pvi.iloc[i] = pvi.iloc[i - 1] * (1 + ret.iloc[i])
        else:
            pvi.iloc[i] = pvi.iloc[i - 1]
    change = (pvi - pvi.shift(5)) / pvi.shift(5)
    return change.clip(-1, 1).shift(1)


def calc_force_index_10d(df: pd.DataFrame) -> pd.Series:
    """Elder Force Index smoothed 10-day EMA, normalized.
    FI = (close - prev_close) * volume. Large |FI| = strong force."""
    cl = df["close_adj"]
    vol = df["volume"]
    fi_raw = cl.diff() * vol
    fi_ema = fi_raw.ewm(span=10, adjust=False).mean()
    # Normalize by avg (price * volume)
    norm_factor = (cl.abs() * vol).rolling(20).mean()
    norm = fi_ema / (norm_factor + 1e-8)
    return (norm * 100).clip(-1, 1).shift(1)


def calc_ease_of_movement_10d(df: pd.DataFrame) -> pd.Series:
    """Ease of Movement (10-day avg). EVM = ((midpoint_change) / range) / volume_scale.
    High = price moves easily on low volume (bullish if positive)."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    vol = df["volume"]
    mid = (hi + lo) / 2.0
    mid_chg = mid - mid.shift(1)
    rng = hi - lo + 1e-8
    # Volume scale: divide by turnover mean to get manageable number
    vol_scale = (vol / (vol.rolling(20).mean() + 1e-8)) * 1e-3
    evm = mid_chg / (rng + 1e-8) / (vol_scale + 1e-8)
    # 10-day smoothed, normalized
    evm_smooth = evm.rolling(10).mean()
    return (evm_smooth * 1000).clip(-1, 1).shift(1)


def calc_money_flow_index_14d(df: pd.DataFrame) -> pd.Series:
    """Money Flow Index (14-day): volume-weighted RSI.
    MFI = 100 - 100/(1 + money_flow_ratio).
    Signed to [-1,1] via (MFI - 50) / 50."""
    hi, lo, cl = df["close_adj"], df["low_adj"], df["close_adj"]
    vol = df["volume"]
    tp = (hi + lo + cl) / 3.0
    mf = tp * vol
    pos_mf = pd.Series(np.where(tp > tp.shift(1), mf, 0.0), index=df.index)
    neg_mf = pd.Series(np.where(tp < tp.shift(1), mf, 0.0), index=df.index)
    pos_sum = pos_mf.rolling(14).sum()
    neg_sum = neg_mf.rolling(14).sum()
    mfr = pos_sum / (neg_sum + 1e-8)
    mfi = 100.0 - 100.0 / (1.0 + mfr)
    signed = (mfi - 50.0) / 50.0
    return signed.clip(-1, 1).shift(1)


def calc_pvt_slope_10d(df: pd.DataFrame) -> pd.Series:
    """Price Volume Trend slope. PVT = cumsum(return * volume).
    Captures smart money conviction weighted by price change."""
    cl = df["close_adj"]
    vol = df["volume"]
    ret = cl.pct_change()
    pvt = (ret * vol).cumsum()
    slope = (pvt - pvt.shift(10)) / 10.0
    norm = slope / (vol.rolling(10).mean() + 1e-8)
    return (norm / 10.0).clip(-1, 1).shift(1)


def calc_volume_differential_10d(df: pd.DataFrame) -> pd.Series:
    """Diff between avg volume on up days vs down days over 10 days.
    Positive = up-day volume > down-day volume (bullish accumulation)."""
    cl = df["close_adj"]
    vol = df["volume"]
    up = cl > cl.shift(1)
    dn = cl < cl.shift(1)
    up_vol = (vol.where(up, 0)).rolling(10).mean()
    dn_vol = (vol.where(dn, 0)).rolling(10).mean()
    diff = (up_vol - dn_vol) / (up_vol + dn_vol + 1e-8)
    return diff.clip(-1, 1).shift(1)


# ============================================================
# Section 2 — Path / Distribution Metrics
# ============================================================

def calc_return_skewness_20d(df: pd.DataFrame) -> pd.Series:
    """Skewness of daily log returns over 20-day window.
    Negative skew = crash-risk regime; positive skew = momentum regime."""
    cl = df["close_adj"]
    ret = np.log(cl / cl.shift(1))
    skew = ret.rolling(20).skew()
    return (skew / 2.0).clip(-1, 1).shift(1)


def calc_return_kurtosis_20d(df: pd.DataFrame) -> pd.Series:
    """Excess kurtosis of daily log returns over 20 days.
    High kurtosis = fat-tail regime (extreme moves likely)."""
    cl = df["close_adj"]
    ret = np.log(cl / cl.shift(1))
    kurt = ret.rolling(20).kurt()
    return (kurt / 6.0).clip(-1, 1).shift(1)


def calc_down_up_vol_ratio_20d(df: pd.DataFrame) -> pd.Series:
    """Ratio of downside std to upside std over 20 days.
    >1 = downside dominance (bear regime); <1 = upside dominance."""
    cl = df["close_adj"]
    ret = cl.pct_change()
    neg_ret = ret.where(ret < 0, np.nan)
    pos_ret = ret.where(ret > 0, np.nan)
    neg_std = neg_ret.rolling(20).std()
    pos_std = pos_ret.rolling(20).std()
    ratio = neg_std / (pos_std + 1e-8)
    # Center at 1, scale to [-1,1]
    centered = np.tanh(np.log(ratio.clip(0.1, 10.0)))
    return centered.clip(-1, 1).shift(1)


def calc_path_loopiness_5d(df: pd.DataFrame) -> pd.Series:
    """Path loopiness: sum(|sign changes of return|) / sum(|returns|) over 5 days.
    High = choppy/indecisive; low = trending."""
    cl = df["close_adj"]
    ret = cl.pct_change()
    sign_changes = (np.sign(ret) != np.sign(ret.shift(1))).astype(float).rolling(5).sum()
    total_path = ret.abs().rolling(5).sum()
    loopiness = sign_changes / (total_path * 100 + 1e-8)
    return loopiness.clip(-1, 1).shift(1)


def calc_ulcer_index_14d(df: pd.DataFrame) -> pd.Series:
    """Ulcer Index: sqrt(mean(drawdown_pct^2)) over 14 days.
    High = persistent drawdown pain (stress regime).
    Signed by recent return direction."""
    cl = df["close_adj"]
    hh = cl.rolling(14).max()
    dd_pct = (cl - hh) / (hh + 1e-8)
    ulcer = np.sqrt((dd_pct ** 2).rolling(14).mean())
    # Sign with recent momentum
    sign = np.sign(cl - cl.shift(5))
    return (ulcer * sign * 100).clip(-1, 1).shift(1)


def calc_current_drawdown_from_peak_20d(df: pd.DataFrame) -> pd.Series:
    """Drawdown from 20-day peak, signed by whether recovering or deepening."""
    cl = df["close_adj"]
    hh = cl.rolling(20).max()
    dd = (cl - hh) / (hh + 1e-8)
    # Sign: negative = in drawdown. Magnitude scaled.
    return (dd * 5).clip(-1, 1).shift(1)


def calc_max_drawdown_20d(df: pd.DataFrame) -> pd.Series:
    """Max drawdown magnitude over 20 days. Pure risk metric."""
    cl = df["close_adj"]
    hh = cl.rolling(20).max()
    dd = (cl - hh) / (hh + 1e-8)
    max_dd = dd.rolling(20).min().abs()
    return (max_dd * 5).clip(-1, 1).shift(1)


def calc_mfe_mae_ratio_5d(df: pd.DataFrame) -> pd.Series:
    """Max Favorable / Max Adverse Excursion ratio over 5 days.
    For each day, MFE = (high - open)/open; MAE = (open - low)/open.
    Ratio averaged: >1 = upside excursion dominates."""
    hi, lo, op = df["high_adj"], df["low_adj"], df["open_adj"]
    mfe = (hi - op) / (op + 1e-8)
    mae = (op - lo) / (op + 1e-8)
    avg_mfe = mfe.rolling(5).mean()
    avg_mae = mae.rolling(5).mean()
    ratio = avg_mfe / (avg_mae + 1e-8)
    centered = np.tanh(np.log(ratio.clip(0.1, 10.0)))
    return centered.clip(-1, 1).shift(1)


def calc_pain_index_20d(df: pd.DataFrame) -> pd.Series:
    """Pain Index: mean drawdown over 20 days (depth × duration).
    Signed by trend direction."""
    cl = df["close_adj"]
    hh = cl.rolling(20).max()
    dd = (cl - hh) / (hh + 1e-8)
    pain = dd.rolling(20).mean()
    sign = np.sign(cl - cl.shift(10))
    return (pain * sign * 20).clip(-1, 1).shift(1)


# ============================================================
# Section 5 — Liquidity / Microstructure
# ============================================================

def calc_amihud_illiquidity_10d(df: pd.DataFrame) -> pd.Series:
    """Amihud illiquidity: mean(|daily_return| / turnover) over 10 days.
    High = illiquid market (large price impact per unit volume)."""
    cl = df["close_adj"]
    turnover = df["total_turnover"]
    ret = cl.pct_change().abs()
    amihud_daily = ret / (turnover / 1e8 + 1e-8)  # scale turnover to 100M RMB units
    amihud_10d = amihud_daily.rolling(10).mean()
    # Normalize: log scale, clip
    log_amihud = np.log(amihud_10d.clip(1e-6, 1e3))
    return (log_amihud / 5.0).clip(-1, 1).shift(1)


def calc_liquidity_efficiency_ratio_10d(df: pd.DataFrame) -> pd.Series:
    """Volume per unit of range — high = deep liquidity, low = thin.
    Signed by close position (positive = efficient + bullish)."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    vol = df["volume"]
    rng = (hi - lo) / (cl + 1e-8)
    eff = vol / (rng + 1e-8)
    eff_z = (eff - eff.rolling(60).mean()) / (eff.rolling(60).std() + 1e-8)
    sign = np.sign(cl - cl.shift(5))
    return (eff_z * sign / 3.0).clip(-1, 1).shift(1)


def calc_roll_spread_proxy_10d(df: pd.DataFrame) -> pd.Series:
    """Roll's effective spread estimator: 2*sqrt(-cov(return_t, return_{t-1}))
    when cov < 0 (market-maker spread), else 0. High = wide spreads."""
    cl = df["close_adj"]
    ret = cl.pct_change()
    # Rolling lag-1 covariance
    def _roll_cov(v):
        if len(v) < 5:
            return 0.0
        a = v[:-1]; b = v[1:]
        ma = a.mean(); mb = b.mean()
        return ((a - ma) * (b - mb)).mean()
    cov = ret.rolling(11).apply(_roll_cov, raw=True)
    roll = np.where(cov < 0, 2 * np.sqrt(-cov), 0.0)
    roll_s = pd.Series(roll, index=df.index)
    # Normalize by realized vol
    rv = ret.rolling(10).std()
    norm = roll_s / (rv + 1e-8)
    return (norm * 10).clip(-1, 1).shift(1)


def calc_volume_per_trade_trend_5d(df: pd.DataFrame) -> pd.Series:
    """Average trade size trend (turnover / num_trades) over 5 days.
    Rising avg trade size = institutional activity; falling = retail."""
    turnover = df["total_turnover"]
    trades = df["num_trades"]
    avg_size = turnover / (trades + 1e-8)
    slope = _rolling_slope(avg_size, 5)
    mean_size = avg_size.rolling(20).mean()
    norm = slope / (mean_size + 1e-8)
    return (norm * 10).clip(-1, 1).shift(1)


def calc_turnover_zscore_20d(df: pd.DataFrame) -> pd.Series:
    """Z-score of today's turnover vs 60-day rolling mean.
    Captures capital deployment regime."""
    turnover = df["total_turnover"]
    mean = turnover.rolling(60, min_periods=20).mean()
    std = turnover.rolling(60, min_periods=20).std()
    z = (turnover - mean) / (std + 1e-8)
    return (z / 3.0).clip(-1, 1).shift(1)


# ============================================================
# Section 6 — Higher-Timeframe Context
# ============================================================

def calc_weekly_return_5d(df: pd.DataFrame) -> pd.Series:
    """5-day (weekly) return. Captures weekly momentum regime."""
    cl = df["close_adj"]
    ret_5d = cl.pct_change(5)
    rv = cl.pct_change().rolling(20).std()
    norm = ret_5d / (rv * np.sqrt(5) + 1e-8)
    return (norm / 3.0).clip(-1, 1).shift(1)


def calc_weekly_atr_position(df: pd.DataFrame) -> pd.Series:
    """Position of close within 5-day high-low range, centered to [-1,1]."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    hh5 = hi.rolling(5).max()
    ll5 = lo.rolling(5).min()
    pos = (cl - ll5) / (hh5 - ll5 + 1e-8)
    return ((pos - 0.5) * 2.0).clip(-1, 1).shift(1)


def calc_monthly_high_proximity(df: pd.DataFrame) -> pd.Series:
    """Proximity of close to 21-day (monthly) high.
    +1 = at high (breakout regime), -1 = far from high."""
    hi, lo, cl = df["high_adj"], df["low_adj"], df["close_adj"]
    hh21 = hi.rolling(21).max()
    ll21 = lo.rolling(21).min()
    pos = (cl - ll21) / (hh21 - ll21 + 1e-8)
    return ((pos - 0.5) * 2.0).clip(-1, 1).shift(1)


def calc_quarterly_trend_direction(df: pd.DataFrame) -> pd.Series:
    """63-day (quarterly) EMA slope normalized by ATR.
    Long-term trend direction."""
    cl = df["close_adj"]
    ema63 = cl.ewm(span=63, adjust=False).mean()
    slope = _rolling_slope(ema63, 10)
    atr14 = _atr(df, 14)
    norm = slope / (atr14 + 1e-8)
    return (norm / 3.0).clip(-1, 1).shift(1)


def calc_monthly_momentum_zscore(df: pd.DataFrame) -> pd.Series:
    """Z-score of 21-day return against its 250-day distribution.
    High = momentum exhaustion; low = oversold bounce setup."""
    cl = df["close_adj"]
    ret_21 = cl.pct_change(21)
    mean = ret_21.rolling(250, min_periods=60).mean()
    std = ret_21.rolling(250, min_periods=60).std()
    z = (ret_21 - mean) / (std + 1e-8)
    return (z / 3.0).clip(-1, 1).shift(1)


# ============================================================
# Section 7 — Calendar / Event Features (Chinese A-share)
# ============================================================

def calc_options_expiry_proximity(df: pd.DataFrame) -> pd.Series:
    """Days to next monthly options expiry (4th Wednesday of month) for 50/300/500 ETF.
    Range: 0 (expiry day) to ~28. Normalized to [-1,1] via tanh.
    Captures pre-expiry gamma / pinning effects."""
    dates = pd.to_datetime(df["date"])
    # Compute 4th Wednesday of each month
    def _fourth_wednesday(d):
        # First day of month
        first = pd.Timestamp(year=d.year, month=d.month, day=1)
        # Day of week: Monday=0, Wednesday=2
        first_wed_offset = (2 - first.dayofweek) % 7
        first_wed = first + pd.Timedelta(days=first_wed_offset)
        fourth_wed = first_wed + pd.Timedelta(days=21)
        return fourth_wed

    # For each date, find days to next 4th Wednesday
    days_to = []
    for d in dates:
        target = _fourth_wednesday(d)
        if target < d:
            # Move to next month
            if d.month == 12:
                target = _fourth_wednesday(pd.Timestamp(year=d.year + 1, month=1, day=1))
            else:
                target = _fourth_wednesday(pd.Timestamp(year=d.year, month=d.month + 1, day=1))
        days_to.append((target - d).days)
    s = pd.Series(days_to, index=df.index)
    # Center: 0 = expiry day, 14 = mid-cycle. tanh((days - 14) / 14)
    centered = np.tanh((s - 14.0) / 14.0)
    return centered.clip(-1, 1).shift(1)


def calc_first_day_of_month_flag(df: pd.DataFrame) -> pd.Series:
    """+1 if first trading day of month, -1 if last, 0 otherwise.
    Captures month-boundary rebalancing effect."""
    dates = pd.to_datetime(df["date"])
    month_series = dates.dt.month
    is_first = (month_series != month_series.shift(1)).astype(int)
    is_last = (month_series != month_series.shift(-1)).astype(int)
    flag = is_first - is_last
    return pd.Series(flag.values, index=df.index).shift(1)


def calc_week_of_month(df: pd.DataFrame) -> pd.Series:
    """Week of month (1-5), centered to [-1, 1].
    Early-month vs late-month effect."""
    dates = pd.to_datetime(df["date"])
    wom = ((dates.dt.day - 1) // 7 + 1).astype(float)
    centered = (wom - 3.0) / 2.0
    return pd.Series(centered.values, index=df.index).clip(-1, 1).shift(1)


def calc_pre_holiday_flag(df: pd.DataFrame) -> pd.Series:
    """Detect days before a holiday break (>3 day gap to next trading day).
    +1 = pre-holiday (light volume, drift), else 0."""
    dates = pd.to_datetime(df["date"])
    gap_to_next = dates.shift(-1) - dates
    gap_days = gap_to_next.dt.days.fillna(1)
    pre_holiday = (gap_days > 3).astype(int)
    # Also flag days after holiday
    gap_from_prev = dates - dates.shift(1)
    gap_from_prev_days = gap_from_prev.dt.days.fillna(1)
    post_holiday = (gap_from_prev_days > 3).astype(int)
    flag = pre_holiday.astype(int) - post_holiday.astype(int)
    return pd.Series(flag.values, index=df.index).shift(1)


def calc_month_end_effect_5d(df: pd.DataFrame) -> pd.Series:
    """+1 within last 5 trading days of month (window-dressing effect)."""
    dates = pd.to_datetime(df["date"])
    # Days until month-end (calendar)
    def _days_to_month_end(d):
        if d.month == 12:
            next_first = pd.Timestamp(year=d.year + 1, month=1, day=1)
        else:
            next_first = pd.Timestamp(year=d.year, month=d.month + 1, day=1)
        return (next_first - d).days
    days_to_end = dates.map(_days_to_month_end)
    flag = (days_to_end <= 7).astype(int)
    return pd.Series(flag.values, index=df.index).shift(1)


# ============================================================
# Registry (single-ETF features — 31 candidates)
# ============================================================
SINGLE_ETF_CANDIDATES = {
    # Section 1: Smart money / volume
    "obv_slope_10d": calc_obv_slope_10d,
    "ad_line_slope_10d": calc_ad_line_slope_10d,
    "negative_volume_index_change": calc_negative_volume_index_change,
    "positive_volume_index_change": calc_positive_volume_index_change,
    "force_index_10d": calc_force_index_10d,
    "ease_of_movement_10d": calc_ease_of_movement_10d,
    "money_flow_index_14d": calc_money_flow_index_14d,
    "pvt_slope_10d": calc_pvt_slope_10d,
    "volume_differential_10d": calc_volume_differential_10d,
    # Section 2: Path / distribution
    "return_skewness_20d": calc_return_skewness_20d,
    "return_kurtosis_20d": calc_return_kurtosis_20d,
    "down_up_vol_ratio_20d": calc_down_up_vol_ratio_20d,
    "path_loopiness_5d": calc_path_loopiness_5d,
    "ulcer_index_14d": calc_ulcer_index_14d,
    "current_drawdown_from_peak_20d": calc_current_drawdown_from_peak_20d,
    "max_drawdown_20d": calc_max_drawdown_20d,
    "mfe_mae_ratio_5d": calc_mfe_mae_ratio_5d,
    "pain_index_20d": calc_pain_index_20d,
    # Section 5: Liquidity
    "amihud_illiquidity_10d": calc_amihud_illiquidity_10d,
    "liquidity_efficiency_ratio_10d": calc_liquidity_efficiency_ratio_10d,
    "roll_spread_proxy_10d": calc_roll_spread_proxy_10d,
    "volume_per_trade_trend_5d": calc_volume_per_trade_trend_5d,
    "turnover_zscore_20d": calc_turnover_zscore_20d,
    # Section 6: Higher timeframe
    "weekly_return_5d": calc_weekly_return_5d,
    "weekly_atr_position": calc_weekly_atr_position,
    "monthly_high_proximity": calc_monthly_high_proximity,
    "quarterly_trend_direction": calc_quarterly_trend_direction,
    "monthly_momentum_zscore": calc_monthly_momentum_zscore,
    # Section 7: Calendar
    "options_expiry_proximity": calc_options_expiry_proximity,
    "first_day_of_month_flag": calc_first_day_of_month_flag,
    "week_of_month": calc_week_of_month,
    "pre_holiday_flag": calc_pre_holiday_flag,
    "month_end_effect_5d": calc_month_end_effect_5d,
}


# ============================================================
# Section 3 — Cross-Asset Regime Features (need all 5 ETFs)
# ============================================================
def compute_cross_asset_features(etf: str, etf_data: dict) -> dict:
    """Compute cross-asset regime features for the target ETF using all 5 ETFs' data.
    Returns dict of {feature_name: pd.Series indexed like target ETF df}."""
    df_self = etf_data[etf]
    out = {}

    # Compute 5-day returns for all ETFs
    rets_5d = {}
    rets_1d = {}
    for e, dfe in etf_data.items():
        cl = dfe["close_adj"]
        rets_5d[e] = cl.pct_change(5)
        rets_1d[e] = cl.pct_change()

    self_ret_5d = rets_5d[etf]

    # 3.a Cross-asset breadth score: sum of sign(5d return) across all 5 ETFs
    sign_sum = sum(np.sign(rets_5d[e]) for e in etf_data) / 5.0
    out["cross_asset_breadth_score"] = (sign_sum.reindex(df_self.index).fillna(0)
                                        .clip(-1, 1).shift(1))

    # 3.b Pairwise rotation features
    pairs = {
        "size_rotation_50_300": ("50ETF", "300ETF"),
        "breadth_rotation_500_300": ("500ETF", "300ETF"),
        "growth_rotation_588_300": ("588000ETF", "300ETF"),
        "growth_rotation_159915_300": ("159915ETF", "300ETF"),
    }
    for name, (e1, e2) in pairs.items():
        if e1 not in rets_5d or e2 not in rets_5d:
            continue
        spread = rets_5d[e1] - rets_5d[e2]
        # Normalize by combined vol
        vol_pooled = np.sqrt((rets_1d[e1].rolling(20).var() +
                              rets_1d[e2].rolling(20).var()) * 5)
        norm = spread / (vol_pooled + 1e-8)
        out[name] = norm.reindex(df_self.index).fillna(0).clip(-3, 3).div(3).shift(1)

    # 3.c Cross-asset return dispersion: std of 1d returns across 5 ETFs
    ret_df = pd.DataFrame({e: rets_1d[e] for e in etf_data})
    dispersion = ret_df.std(axis=1)
    disp_mean = dispersion.rolling(60).mean()
    disp_std = dispersion.rolling(60).std()
    z = (dispersion - disp_mean) / (disp_std + 1e-8)
    out["cross_asset_return_dispersion_z"] = z.reindex(df_self.index).fillna(0).clip(-3, 3).div(3).shift(1)

    # 3.d Cross-asset correlation: avg pairwise 20d correlation
    corr_sum = pd.Series(0.0, index=df_self.index)
    n_pairs = 0
    etf_list = list(etf_data.keys())
    for i in range(len(etf_list)):
        for j in range(i + 1, len(etf_list)):
            e1, e2 = etf_list[i], etf_list[j]
            c = rets_1d[e1].rolling(20).corr(rets_1d[e2])
            corr_sum = corr_sum.add(c.reindex(df_self.index).fillna(0), fill_value=0)
            n_pairs += 1
    avg_corr = corr_sum / max(n_pairs, 1)
    out["cross_asset_avg_correlation"] = avg_corr.reindex(df_self.index).fillna(0).clip(-1, 1).shift(1)

    # 3.e Self-vs-benchmark relative strength: sign of self_5d_ret - cross_avg_5d_ret
    cross_avg = sum(rets_5d[e] for e in etf_data if e != etf) / (len(etf_data) - 1)
    rs = self_ret_5d - cross_avg
    norm = rs / (rets_1d[etf].rolling(20).std() * np.sqrt(5) + 1e-8)
    out["relative_strength_vs_cross_5d"] = norm.reindex(df_self.index).fillna(0).clip(-3, 3).div(3).shift(1)

    return out


# ============================================================
# Section 4 — IV / VIX Features (need rq_vix)
# ============================================================
def compute_vix_features(etf: str, df_self: pd.DataFrame, vix_df: pd.DataFrame) -> dict:
    """Compute VIX/IV regime features for target ETF.
    rq_vix columns: vix_50, vix_300, vix_500, vix_588000, vix_159915."""
    vix_map = {"50ETF": "vix_50", "300ETF": "vix_300", "500ETF": "vix_500",
               "588000ETF": "vix_588000", "159915ETF": "vix_159915"}
    col = vix_map.get(etf)
    out = {}
    if col is None or col not in vix_df.columns:
        return out
    vix = vix_df[col].copy()
    # Align to df_self dates
    vix.index = pd.to_datetime(vix.index)

    # Reindex to daily frame
    self_dates = pd.to_datetime(df_self["date"].values)
    vix_aligned = vix.reindex(self_dates).ffill()

    out["vix_level_zscore_60d"] = ((vix_aligned - vix_aligned.rolling(60, min_periods=20).mean()) /
                                    (vix_aligned.rolling(60, min_periods=20).std() + 1e-8)
                                   ).clip(-3, 3).div(3)
    out["vix_change_3d"] = ((vix_aligned - vix_aligned.shift(3)) /
                             (vix_aligned.rolling(20).std() + 1e-8)
                            ).clip(-3, 3).div(3)
    # Term structure proxy: short MA vs long MA
    ema5 = vix_aligned.ewm(span=5, adjust=False).mean()
    ema20 = vix_aligned.ewm(span=20, adjust=False).mean()
    out["vix_term_structure_proxy"] = ((ema5 - ema20) /
                                        (vix_aligned.rolling(20).std() + 1e-8)
                                       ).clip(-3, 3).div(3).shift(1)
    out["vix_level_zscore_60d"] = out["vix_level_zscore_60d"].shift(1)
    out["vix_change_3d"] = out["vix_change_3d"].shift(1)
    return out


# ============================================================
# Main
# ============================================================
def main():
    print("=== Wave 5: Multi-Family Feature Mining ===")
    print(f"Single-ETF candidates: {len(SINGLE_ETF_CANDIDATES)}")
    print(f"Cross-asset candidates: ~6, VIX candidates: ~3 per ETF")
    results = []

    # Load all ETF 1d data once (for cross-asset)
    etf_list = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
    etf_data = {}
    for etf in etf_list:
        file_1d = ETF_CONFIG[etf]["file_1d"]
        path = DATA_DIR / file_1d
        if not path.exists():
            print(f"  Missing 1d for {etf}: {path}")
            continue
        df = pd.read_parquet(path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        etf_data[etf] = df

    # Load VIX
    vix_path = DATA_DIR / "rq_vix.parquet"
    vix_df = pd.read_parquet(vix_path) if vix_path.exists() else pd.DataFrame()
    if vix_path.exists():
        print(f"  Loaded VIX data: {vix_df.shape}")

    for etf in etf_list:
        if etf not in etf_data:
            continue
        print(f"\n{'='*60}")
        print(f"Evaluating Wave 5 candidates on {etf}...")
        print(f"{'='*60}")

        feat_file = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not feat_file.exists():
            print(f"  Skipping {etf}: features parquet missing")
            continue
        df_feat = pd.read_parquet(feat_file)
        y = df_feat["trade_return"].values
        dates = df_feat.index

        df_1d = etf_data[etf]
        date_to_idx = {d.date(): i for i, d in enumerate(df_1d["date"])}

        # 1) Single-ETF features
        candidate_series = {}
        for name, fn in SINGLE_ETF_CANDIDATES.items():
            try:
                candidate_series[name] = fn(df_1d)
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")

        # 2) Cross-asset features
        try:
            cross_feats = compute_cross_asset_features(etf, etf_data)
            candidate_series.update(cross_feats)
        except Exception as e:
            print(f"  [ERROR] cross-asset: {e}")

        # 3) VIX features
        if not vix_df.empty:
            try:
                vix_feats = compute_vix_features(etf, df_1d, vix_df)
                # Reindex to df_1d index (vix features returned indexed by self_dates which may differ)
                for vn, vs in vix_feats.items():
                    if len(vs) == len(df_1d):
                        candidate_series[vn] = pd.Series(vs.values, index=df_1d.index)
            except Exception as e:
                print(f"  [ERROR] vix: {e}")

        # Evaluate
        for name, series in candidate_series.items():
            feat_values = []
            valid_mask = []
            for dt in dates:
                d = pd.to_datetime(dt).date()
                if d in date_to_idx:
                    idx = date_to_idx[d]
                    val = series.iloc[idx] if idx < len(series) else np.nan
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
                continue
            if np.std(x[valid]) < 1e-8:
                continue
            metrics = compute_yearly_ic(x[valid], y[valid], dates[valid])
            gate_pass = (metrics["ic_cv"] <= 3.0 and metrics["n_neg_years"] <= 2
                         and metrics["jackknife_pass"] and abs(metrics["mean_ic"]) >= 0.02)
            results.append({
                "feature_name": name, "etf": etf,
                "overall_ic": round(metrics["mean_ic"], 6),
                "ic_cv": round(metrics["ic_cv"], 4),
                "n_neg_years": metrics["n_neg_years"],
                "jackknife_pass": metrics["jackknife_pass"],
                "flips": metrics["flips"],
                "gate_pass": gate_pass,
                "n_valid": int(valid.sum()),
            })
            status = "PASS" if gate_pass else "REJECT"
            print(f"  {name:40s} | IC={metrics['mean_ic']:+.4f} | CV={metrics['ic_cv']:.2f} | "
                  f"NegYrs={metrics['n_neg_years']} | JK={metrics['jackknife_pass']} | "
                  f"N={valid.sum()} => {status}")

    csv_path = HERE / "mined_wave5_candidates.csv"
    fieldnames = ["feature_name", "etf", "overall_ic", "ic_cv", "n_neg_years",
                  "jackknife_pass", "flips", "gate_pass", "n_valid"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved to: {csv_path}")

    passing = [r for r in results if r["gate_pass"]]
    print(f"\n{'='*60}")
    print(f"=== Gate-Passing Wave 5 Features ({len(passing)}/{len(results)}) ===")
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


if __name__ == "__main__":
    main()
