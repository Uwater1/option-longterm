"""
Mining & Screening Script for New Day-Model Base Primitives.
1. Computes candidate features on historical intraday/daily data for all 5 ETFs.
2. Runs mandatory Causality Perturbation Test (bars [6..end] scrambled).
3. Evaluates 7-Year Jackknife sign stability, In-Sample IC, IC CV, Monotonicity, Deflated IC.
4. Exports all candidate evaluations to day-model-new/mining/mined_candidates.csv.
5. Identifies gate-passing features for integration into features_extra.py / build_features.py.
"""
import sys
import os
import csv
import json
import numpy as np
import pandas as pd
from pathlib import Path
from numba import njit
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE.parent))

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
    
    # 7-Year Jackknife sign stability: split into 7 chunks, check if IC sign flips
    n_chunks = 7
    chunk_size = len(x) // n_chunks
    chunk_signs = []
    for c in range(n_chunks):
        sub_x = x[c*chunk_size : (c+1)*chunk_size]
        sub_y = y[c*chunk_size : (c+1)*chunk_size]
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
        "flips": flips
    }

# --- Define New Candidate Primitives ---
@njit(cache=True, fastmath=True)
def calc_h2_l2_pullback_continuation(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks High 2 / Low 2 pullback continuation signal."""
    n = len(op)
    if n < 4:
        return np.float32(0.0)
    CD = float(cl[n - 1])
    rng = float(hi[0]) - float(lo[0])
    for i in range(1, n):
        r = float(hi[i]) - float(lo[i])
        if r > rng:
            rng = r
    # Count pullback legs (highs lower than prior high, or lows higher than prior low)
    h_pullbacks = 0
    l_pullbacks = 0
    for i in range(1, n):
        if float(hi[i]) < float(hi[i - 1]):
            h_pullbacks += 1
        if float(lo[i]) > float(lo[i - 1]):
            l_pullbacks += 1
    val = (h_pullbacks - l_pullbacks) / float(n)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_first_ma_gap_bar_reversal(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks First MA Gap Bar Reversal."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # 3-bar SMA
    gap_count = 0
    for i in range(2, n):
        sma3 = (float(cl[i]) + float(cl[i-1]) + float(cl[i-2])) / 3.0
        if float(lo[i]) > sma3:
            gap_count += 1
        elif float(hi[i]) < sma3:
            gap_count -= 1
    val = float(gap_count) / float(n - 2)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_failed_breakout_reversal_thrust(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks Failed Breakout & Reversal Thrust."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # Opening 15m high/low (first 3 bars)
    or_h = max(float(hi[0]), float(hi[1]))
    or_l = min(float(lo[0]), float(lo[1]))
    CD = float(cl[n-1])
    rng = or_h - or_l + 1e-8
    fail_up = max(0.0, float(hi[n-1]) - or_h) * (or_h - CD) / rng
    fail_dn = max(0.0, or_l - float(lo[n-1])) * (CD - or_l) / rng
    val = (fail_dn - fail_up) / rng
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_shaved_bar_trend_conviction(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks Shaved Bar Trend Conviction."""
    n = len(op)
    if n < 1:
        return np.float32(0.0)
    score = 0.0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        body_i = float(cl[i]) - float(op[i])
        upper_wick = float(hi[i]) - max(float(op[i]), float(cl[i]))
        lower_wick = min(float(op[i]), float(cl[i])) - float(lo[i])
        # Shaved bull bar: low near open, close near high
        if body_i > 0 and lower_wick < 0.1 * rng_i:
            score += abs(body_i) / rng_i
        elif body_i < 0 and upper_wick < 0.1 * rng_i:
            score -= abs(body_i) / rng_i
    val = score / float(n)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_vwap_channel_compression(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Intraday VWAP Band Compression / Coiling Ratio."""
    n = len(op)
    if n < 2:
        return np.float32(0.0)
    cum_vol = 0.0
    cum_pv = 0.0
    for i in range(n):
        v = float(vol[i])
        p = (float(hi[i]) + float(lo[i]) + float(cl[i])) / 3.0
        cum_vol += v
        cum_pv += p * v
    vwap = cum_pv / (cum_vol + 1e-8)
    dev_sum = 0.0
    for i in range(n):
        p = (float(hi[i]) + float(lo[i]) + float(cl[i])) / 3.0
        dev_sum += (p - vwap) ** 2
    std_vwap = np.sqrt(dev_sum / float(n))
    val = 1.0 - (std_vwap / (prev_close * 0.01 + 1e-8))
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_morning_volume_weighted_momentum(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Volume-Weighted Early Momentum Vector."""
    n = len(op)
    if n < 1:
        return np.float32(0.0)
    O0 = float(op[0])
    CD = float(cl[n-1])
    ret = (CD - O0) / (O0 + 1e-8)
    tot_vol = 0.0
    for i in range(n):
        tot_vol += float(vol[i])
    avg_vol = tot_vol / float(n)
    vol_ratio = avg_vol / (exp_bar_vol + 1e-8)
    val = ret * min(vol_ratio, 3.0) / 0.02
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_lunch_transition_volume_skew(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Late Morning Volume Skew (9:50-10:00 vs 9:30-9:40)."""
    n = len(op)
    if n < 6:
        return np.float32(0.0)
    v_early = float(vol[0]) + float(vol[1])
    v_late = float(vol[4]) + float(vol[5])
    tot = v_early + v_late + 1e-8
    val = (v_late - v_early) / tot
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_intraday_range_expansion_velocity(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Intraday Range Expansion Velocity."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # Range of each bar
    r_sum = 0.0
    for i in range(n):
        r_sum += (float(hi[i]) - float(lo[i]))
    avg_r = r_sum / float(n)
    hh = float(hi[0])
    ll = float(lo[0])
    exp_count = 0
    for i in range(1, n):
        if float(hi[i]) > hh or float(lo[i]) < ll:
            exp_count += 1
            hh = max(hh, float(hi[i]))
            ll = min(ll, float(lo[i]))
    val = float(exp_count) / float(n - 1)
    return np.float32(min(max(val, 0.0), 1.0))

# --- Define New Candidate Primitives (Batch 2: Al Brooks / Microstructure) ---

@njit(cache=True, fastmath=True)
def calc_triangle_apex_compression(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks Ch23 Triangles: rate of range contraction across bars.
    Successively smaller ranges indicate coiling before breakout.
    Returns slope of bar ranges normalized by mean range, in [-1, 1]."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # Compute range per bar
    ranges = np.zeros(n, dtype=np.float32)
    for i in range(n):
        ranges[i] = float(hi[i]) - float(lo[i])
    mean_r = 0.0
    for i in range(n):
        mean_r += ranges[i]
    mean_r /= float(n)
    if mean_r < 1e-8:
        return np.float32(0.0)
    # OLS slope of ranges
    sx = 0.0
    sy = 0.0
    sxx = 0.0
    sxy = 0.0
    for i in range(n):
        xi = float(i)
        yi = float(ranges[i])
        sx += xi
        sy += yi
        sxx += xi * xi
        sxy += xi * yi
    denom = float(n) * sxx - sx * sx
    if abs(denom) < 1e-12:
        return np.float32(0.0)
    slope = (float(n) * sxy - sx * sy) / denom
    # Normalize: negative slope = compression (triangle), positive = expansion
    val = slope / (mean_r + 1e-8)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_trap_bar_reversal_intensity(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks Ch32 'Getting Trapped': bars that sweep prior bar extreme then close back.
    Trapped traders' stops fuel reversal. Returns signed intensity in [-1, 1].
    Positive = bull traps (sweep high then close below) => bearish.
    Negative = bear traps (sweep low then close above) => bullish."""
    n = len(op)
    if n < 2:
        return np.float32(0.0)
    bull_traps = 0.0
    bear_traps = 0.0
    for i in range(1, n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        # Bull trap: high exceeds prior high but close below prior high
        if float(hi[i]) > float(hi[i-1]) and float(cl[i]) < float(hi[i-1]):
            penetration = (float(hi[i]) - float(hi[i-1])) / rng_i
            bull_traps += penetration
        # Bear trap: low breaks prior low but close above prior low
        if float(lo[i]) < float(lo[i-1]) and float(cl[i]) > float(lo[i-1]):
            penetration = (float(lo[i-1]) - float(lo[i])) / rng_i
            bear_traps += penetration
    val = (bear_traps - bull_traps) / float(n - 1)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_two_leg_momentum_completion(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks Ch16 'Counting Legs': detect 2-leg impulse-correction-impulse structure.
    A completed 2-leg move often exhausts. Returns signed completion score in [-1, 1].
    Positive = 2-leg up completed (potential exhaustion/reversal down).
    Negative = 2-leg down completed (potential bounce)."""
    n = len(op)
    if n < 4:
        return np.float32(0.0)
    # Find swing points using simple pivot rule
    # Split into segments and detect impulse-correction-impulse
    CD = float(cl[n-1])
    O0 = float(op[0])
    # Detect leg structure: find max drawup and drawdown sequences
    # Leg 1 up: find first significant high
    leg1_high = float(hi[0])
    leg1_high_idx = 0
    for i in range(1, n//2 + 1):
        if float(hi[i]) > leg1_high:
            leg1_high = float(hi[i])
            leg1_high_idx = i
    # Correction: find low after leg1 high
    corr_low = float(lo[min(leg1_high_idx + 1, n-1)])
    corr_low_idx = min(leg1_high_idx + 1, n-1)
    for i in range(leg1_high_idx + 1, min(leg1_high_idx + 3, n)):
        if float(lo[i]) < corr_low:
            corr_low = float(lo[i])
            corr_low_idx = i
    # Leg 2: check if price makes new high after correction
    leg2_high = corr_low
    for i in range(corr_low_idx, n):
        if float(hi[i]) > leg2_high:
            leg2_high = float(hi[i])
    # Score: two legs up if leg2_high > leg1_high and correction was shallow
    rng = float(max(hi[0], hi[n-1])) - float(min(lo[0], lo[n-1])) + 1e-8
    corr_depth = (leg1_high - corr_low) / rng
    up_completion = 0.0
    if leg2_high > leg1_high and corr_depth < 0.5 and leg1_high_idx > 0:
        up_completion = (1.0 - corr_depth) * (leg2_high - leg1_high) / rng
    # Symmetric for down
    leg1_low = float(lo[0])
    leg1_low_idx = 0
    for i in range(1, n//2 + 1):
        if float(lo[i]) < leg1_low:
            leg1_low = float(lo[i])
            leg1_low_idx = i
    corr_high = float(hi[min(leg1_low_idx + 1, n-1)])
    corr_high_idx = min(leg1_low_idx + 1, n-1)
    for i in range(leg1_low_idx + 1, min(leg1_low_idx + 3, n)):
        if float(hi[i]) > corr_high:
            corr_high = float(hi[i])
            corr_high_idx = i
    leg2_low = corr_high
    for i in range(corr_high_idx, n):
        if float(lo[i]) < leg2_low:
            leg2_low = float(lo[i])
    corr_depth_dn = (corr_high - leg1_low) / rng
    dn_completion = 0.0
    if leg2_low < leg1_low and corr_depth_dn < 0.5 and leg1_low_idx > 0:
        dn_completion = (1.0 - corr_depth_dn) * (leg1_low - leg2_low) / rng
    val = up_completion - dn_completion
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_micro_double_top_bottom(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Al Brooks Ch20 'Double Tops/Bottoms': micro double top/bottom at range extremes.
    Two touches of the same level that fail to break => reversal signal.
    Returns: positive = double bottom detected (bullish), negative = double top (bearish)."""
    n = len(op)
    if n < 4:
        return np.float32(0.0)
    hh = float(hi[0])
    ll = float(lo[0])
    for i in range(1, n):
        if float(hi[i]) > hh:
            hh = float(hi[i])
        if float(lo[i]) < ll:
            ll = float(lo[i])
    rng = hh - ll + 1e-8
    tolerance = 0.15 * rng  # within 15% of range counts as same level
    # Double top: two bars with highs near hh that fail to break
    dt_count = 0
    dt_last_idx = -1
    for i in range(n):
        if abs(float(hi[i]) - hh) <= tolerance:
            dt_count += 1
            dt_last_idx = i
    # Double bottom: two bars with lows near ll
    db_count = 0
    db_last_idx = -1
    for i in range(n):
        if abs(float(lo[i]) - ll) <= tolerance:
            db_count += 1
            db_last_idx = i
    CD = float(cl[n-1])
    # Double top is bearish if close is below midpoint after 2+ touches
    dt_signal = 0.0
    if dt_count >= 2 and CD < (hh + ll) / 2.0:
        dt_signal = -float(dt_count - 1) * (hh - CD) / rng
    # Double bottom is bullish if close is above midpoint after 2+ touches
    db_signal = 0.0
    if db_count >= 2 and CD > (hh + ll) / 2.0:
        db_signal = float(db_count - 1) * (CD - ll) / rng
    val = db_signal + dt_signal
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_opening_range_persistence(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Fraction of bars whose close stays within bar-0 range [L0, H0].
    High persistence = coiling inside opening range => breakout mode (Brooks 'breakout mode').
    Returns ratio in [0, 1]."""
    n = len(op)
    if n < 2:
        return np.float32(0.0)
    H0 = float(hi[0])
    L0 = float(lo[0])
    inside_count = 0
    for i in range(1, n):
        if float(cl[i]) <= H0 and float(cl[i]) >= L0:
            inside_count += 1
    val = float(inside_count) / float(n - 1)
    return np.float32(val)

@njit(cache=True, fastmath=True)
def calc_volume_weighted_momentum_acceleration(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Second derivative of volume-weighted price: momentum building vs fading.
    Compares volume-weighted return of last half vs first half of early bars.
    Positive = accelerating momentum, Negative = decelerating/exhaustion."""
    n = len(op)
    if n < 4:
        return np.float32(0.0)
    mid = n // 2
    # First half volume-weighted return
    vw_ret_first = 0.0
    vol_first = 0.0
    for i in range(mid):
        ret_i = (float(cl[i]) - float(op[i])) / (float(op[i]) + 1e-8)
        vw_ret_first += ret_i * float(vol[i])
        vol_first += float(vol[i])
    if vol_first > 0:
        vw_ret_first /= vol_first
    # Second half volume-weighted return
    vw_ret_second = 0.0
    vol_second = 0.0
    for i in range(mid, n):
        ret_i = (float(cl[i]) - float(op[i])) / (float(op[i]) + 1e-8)
        vw_ret_second += ret_i * float(vol[i])
        vol_second += float(vol[i])
    if vol_second > 0:
        vw_ret_second /= vol_second
    # Acceleration = second - first, normalized by ATR proxy
    atr_proxy = 0.0
    for i in range(n):
        atr_proxy += float(hi[i]) - float(lo[i])
    atr_proxy /= float(n)
    val = (vw_ret_second - vw_ret_first) / (atr_proxy / (prev_close + 1e-8) + 1e-8)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_price_memory_retest_proximity(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Proximity of decision-bar close to the early-session extreme (high or low).
    Retests of extremes often trigger reversals (Brooks Ch9 'prior failed reversals').
    Returns: positive = near high (potential resistance), negative = near low (support)."""
    n = len(op)
    if n < 2:
        return np.float32(0.0)
    hh = float(hi[0])
    ll = float(lo[0])
    for i in range(1, n):
        if float(hi[i]) > hh:
            hh = float(hi[i])
        if float(lo[i]) < ll:
            ll = float(lo[i])
    rng = hh - ll + 1e-8
    CD = float(cl[n-1])
    # Distance to high (negative = close to high) and low (positive = close to low)
    dist_to_high = (hh - CD) / rng
    dist_to_low = (CD - ll) / rng
    # If very close to high (< 10% of range), signal potential reversal down
    # If very close to low (< 10% of range), signal potential reversal up
    val = 0.0
    if dist_to_high < 0.10:
        val = -(1.0 - dist_to_high / 0.10)  # negative = at high, bearish
    elif dist_to_low < 0.10:
        val = (1.0 - dist_to_low / 0.10)   # positive = at low, bullish
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_bar_efficiency_decay(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Rate of decline in body-to-range ratio (efficiency) across bars.
    Decaying efficiency = trend exhaustion (Brooks 'channel exhaustion').
    Returns slope of efficiency, negative = decay/exhaustion."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    eff = np.zeros(n, dtype=np.float32)
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        eff[i] = abs(float(cl[i]) - float(op[i])) / rng_i
    # OLS slope of efficiency
    sx = 0.0
    sy = 0.0
    sxx = 0.0
    sxy = 0.0
    for i in range(n):
        xi = float(i)
        yi = float(eff[i])
        sx += xi
        sy += yi
        sxx += xi * xi
        sxy += xi * yi
    denom = float(n) * sxx - sx * sx
    if abs(denom) < 1e-12:
        return np.float32(0.0)
    slope = (float(n) * sxy - sx * sy) / denom
    # Normalize by mean efficiency
    mean_eff = sy / float(n)
    val = slope / (mean_eff + 1e-8)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_cumulative_delta_divergence(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Divergence between cumulative volume delta and price.
    Price rising but delta falling (or vice versa) => absorption/reversal.
    Returns: positive = bullish divergence (price down, delta up), negative = bearish."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # Cumulative delta: sum of signed volume
    cum_delta = 0.0
    delta_arr = np.zeros(n, dtype=np.float32)
    for i in range(n):
        sign_i = 1.0 if float(cl[i]) > float(op[i]) else (-1.0 if float(cl[i]) < float(op[i]) else 0.0)
        cum_delta += sign_i * float(vol[i])
        delta_arr[i] = cum_delta
    # Price trend (slope of closes)
    sx = 0.0
    sy_p = 0.0
    sy_d = 0.0
    sxx = 0.0
    sxy_p = 0.0
    sxy_d = 0.0
    for i in range(n):
        xi = float(i)
        sx += xi
        sxx += xi * xi
        sy_p += float(cl[i])
        sxy_p += xi * float(cl[i])
        sy_d += float(delta_arr[i])
        sxy_d += xi * float(delta_arr[i])
    denom = float(n) * sxx - sx * sx
    if abs(denom) < 1e-12:
        return np.float32(0.0)
    price_slope = (float(n) * sxy_p - sx * sy_p) / denom
    delta_slope = (float(n) * sxy_d - sx * sy_d) / denom
    # Normalize slopes
    mean_price = sy_p / float(n)
    mean_delta = abs(sy_d / float(n)) + 1e-8
    norm_p = price_slope / (mean_price + 1e-8)
    norm_d = delta_slope / mean_delta
    # Divergence: delta slope opposes price slope
    val = norm_d - norm_p  # positive = delta stronger than price (bullish divergence)
    return np.float32(min(max(val * 5.0, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_false_breakout_accumulation(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Count of false breakouts (new extreme then close back inside prior range).
    High false-breakout count = trap-filled regime => mean reversion expected.
    Returns signed accumulation: positive = more false breakdowns (bullish), negative = false breakouts up (bearish)."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    false_up = 0.0
    false_dn = 0.0
    # Running high/low excluding current bar
    run_h = float(hi[0])
    run_l = float(lo[0])
    for i in range(1, n):
        # False breakout up: makes new high but closes below prior running high
        if float(hi[i]) > run_h and float(cl[i]) < run_h:
            rng_i = float(hi[i]) - float(lo[i]) + 1e-8
            false_up += (float(hi[i]) - run_h) / rng_i
        # False breakdown: makes new low but closes above prior running low
        if float(lo[i]) < run_l and float(cl[i]) > run_l:
            rng_i = float(hi[i]) - float(lo[i]) + 1e-8
            false_dn += (run_l - float(lo[i])) / rng_i
        # Update running extremes
        if float(hi[i]) > run_h:
            run_h = float(hi[i])
        if float(lo[i]) < run_l:
            run_l = float(lo[i])
    val = (false_dn - false_up) / float(n - 1)
    return np.float32(min(max(val, -1.0), 1.0))


# --- Batch 3: Refined near-misses + new concepts ---

@njit(cache=True, fastmath=True)
def calc_range_retention_ratio(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Fraction of range expansion that is retained (not filled back).
    Measures trend follow-through vs mean reversion tendency.
    High retention = trend persistence, Low retention = chop/reversal regime.
    Returns ratio in [-1, 1], positive = upward retention, negative = downward."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # Track running high/low and measure how much expansion persists
    run_h = float(hi[0])
    run_l = float(lo[0])
    up_expansion = 0.0
    dn_expansion = 0.0
    up_retained = 0.0
    dn_retained = 0.0
    for i in range(1, n):
        # Upward expansion
        if float(hi[i]) > run_h:
            exp_amt = float(hi[i]) - run_h
            up_expansion += exp_amt
            # Check if close retains the expansion (closes above old high)
            if float(cl[i]) > run_h:
                up_retained += min(float(cl[i]) - run_h, exp_amt)
            run_h = float(hi[i])
        # Downward expansion
        if float(lo[i]) < run_l:
            exp_amt = run_l - float(lo[i])
            dn_expansion += exp_amt
            # Check if close retains (closes below old low)
            if float(cl[i]) < run_l:
                dn_retained += min(run_l - float(cl[i]), exp_amt)
            run_l = float(lo[i])
    # Net retention ratio
    up_ratio = up_retained / (up_expansion + 1e-8) if up_expansion > 0 else 0.5
    dn_ratio = dn_retained / (dn_expansion + 1e-8) if dn_expansion > 0 else 0.5
    val = up_ratio - dn_ratio
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_volume_price_confirmation(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Do high-volume bars confirm the price direction?
    Correlation between volume and absolute body direction.
    Positive = volume confirms trend (healthy), Negative = volume opposes (divergence).
    Returns correlation in [-1, 1]."""
    n = len(op)
    if n < 3:
        return np.float32(0.0)
    # Compute signed body and volume
    sum_v = 0.0
    sum_b = 0.0
    sum_vv = 0.0
    sum_bb = 0.0
    sum_vb = 0.0
    for i in range(n):
        v = float(vol[i])
        # Signed body normalized by range
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        b = (float(cl[i]) - float(op[i])) / rng_i
        sum_v += v
        sum_b += b
        sum_vv += v * v
        sum_bb += b * b
        sum_vb += v * b
    nf = float(n)
    cov = sum_vb - (sum_v * sum_b) / nf
    var_v = sum_vv - (sum_v * sum_v) / nf
    var_b = sum_bb - (sum_b * sum_b) / nf
    if var_v < 1e-8 or var_b < 1e-8:
        return np.float32(0.0)
    corr = cov / (np.sqrt(var_v) * np.sqrt(var_b) + 1e-8)
    return np.float32(min(max(corr, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_early_late_momentum_divergence(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Compare momentum of first 2 bars vs last 2 bars.
    Divergence indicates exhaustion (early strong, late weak) or building (early weak, late strong).
    Returns: positive = late momentum > early (building), negative = early > late (exhaustion)."""
    n = len(op)
    if n < 4:
        return np.float32(0.0)
    # Early momentum: average body of first 2 bars
    early_mom = 0.0
    for i in range(2):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        early_mom += (float(cl[i]) - float(op[i])) / rng_i
    early_mom /= 2.0
    # Late momentum: average body of last 2 bars
    late_mom = 0.0
    for i in range(n - 2, n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        late_mom += (float(cl[i]) - float(op[i])) / rng_i
    late_mom /= 2.0
    # Divergence: late - early
    val = late_mom - early_mom
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_consecutive_compression_count(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Count consecutive bars with declining range (compression/coiling).
    Brooks Ch22 'Tight Trading Ranges': compression precedes breakout.
    Returns normalized count in [0, 1]."""
    n = len(op)
    if n < 2:
        return np.float32(0.0)
    max_compress = 0
    cur_compress = 0
    for i in range(1, n):
        rng_cur = float(hi[i]) - float(lo[i])
        rng_prev = float(hi[i-1]) - float(lo[i-1])
        if rng_cur < rng_prev:
            cur_compress += 1
            if cur_compress > max_compress:
                max_compress = cur_compress
        else:
            cur_compress = 0
    val = float(max_compress) / float(n - 1)
    return np.float32(val)

@njit(cache=True, fastmath=True)
def calc_smooth_momentum_structure(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Smoothed momentum structure using rolling 3-bar average.
    Detects whether momentum is accelerating, decelerating, or reversing.
    Returns: positive = accelerating up, negative = accelerating down."""
    n = len(op)
    if n < 4:
        return np.float32(0.0)
    # Compute bar returns
    rets = np.zeros(n, dtype=np.float32)
    for i in range(n):
        rets[i] = (float(cl[i]) - float(op[i])) / (float(op[i]) + 1e-8)
    # Rolling 3-bar momentum (if available)
    if n < 3:
        return np.float32(0.0)
    # Compare first half momentum vs second half momentum
    mid = n // 2
    first_mom = 0.0
    for i in range(mid):
        first_mom += rets[i]
    first_mom /= float(mid)
    second_mom = 0.0
    for i in range(mid, n):
        second_mom += rets[i]
    second_mom /= float(n - mid)
    # Acceleration normalized by ATR proxy
    atr_proxy = 0.0
    for i in range(n):
        atr_proxy += float(hi[i]) - float(lo[i])
    atr_proxy /= float(n)
    val = (second_mom - first_mom) / (atr_proxy / (prev_close + 1e-8) + 1e-8)
    return np.float32(min(max(val, -1.0), 1.0))

@njit(cache=True, fastmath=True)
def calc_volume_confirmed_trap_intensity(op, hi, lo, cl, vol, prev_close, exp_bar_vol, is_20pct):
    """Volume-confirmed trap detection: traps with above-average volume are more significant.
    Returns signed intensity: positive = bear traps with volume (bullish), negative = bull traps (bearish)."""
    n = len(op)
    if n < 2:
        return np.float32(0.0)
    # Compute average volume
    avg_vol = 0.0
    for i in range(n):
        avg_vol += float(vol[i])
    avg_vol /= float(n)
    bull_traps = 0.0
    bear_traps = 0.0
    for i in range(1, n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        vol_factor = float(vol[i]) / (avg_vol + 1e-8)
        # Bull trap: high exceeds prior high but close below prior high (with volume confirmation)
        if float(hi[i]) > float(hi[i-1]) and float(cl[i]) < float(hi[i-1]):
            penetration = (float(hi[i]) - float(hi[i-1])) / rng_i
            bull_traps += penetration * min(vol_factor, 2.0)
        # Bear trap: low breaks prior low but close above prior low
        if float(lo[i]) < float(lo[i-1]) and float(cl[i]) > float(lo[i-1]):
            penetration = (float(lo[i-1]) - float(lo[i])) / rng_i
            bear_traps += penetration * min(vol_factor, 2.0)
    val = (bear_traps - bull_traps) / float(n - 1)
    return np.float32(min(max(val, -1.0), 1.0))


CANDIDATES = {
    # Batch 1 (original)
    "h2_l2_pullback_continuation": calc_h2_l2_pullback_continuation,
    "first_ma_gap_bar_reversal": calc_first_ma_gap_bar_reversal,
    "failed_breakout_reversal_thrust": calc_failed_breakout_reversal_thrust,
    "shaved_bar_trend_conviction": calc_shaved_bar_trend_conviction,
    "vwap_channel_compression": calc_vwap_channel_compression,
    "morning_volume_weighted_momentum": calc_morning_volume_weighted_momentum,
    "lunch_transition_volume_skew": calc_lunch_transition_volume_skew,
    "intraday_range_expansion_velocity": calc_intraday_range_expansion_velocity,
    # Batch 2 (new: Al Brooks / Microstructure)
    "triangle_apex_compression": calc_triangle_apex_compression,
    "trap_bar_reversal_intensity": calc_trap_bar_reversal_intensity,
    "two_leg_momentum_completion": calc_two_leg_momentum_completion,
    "micro_double_top_bottom": calc_micro_double_top_bottom,
    "opening_range_persistence": calc_opening_range_persistence,
    "volume_weighted_momentum_acceleration": calc_volume_weighted_momentum_acceleration,
    "price_memory_retest_proximity": calc_price_memory_retest_proximity,
    "bar_efficiency_decay": calc_bar_efficiency_decay,
    "cumulative_delta_divergence": calc_cumulative_delta_divergence,
    "false_breakout_accumulation": calc_false_breakout_accumulation,
    # Batch 3 (refined near-misses + new concepts)
    "range_retention_ratio": calc_range_retention_ratio,
    "volume_price_confirmation": calc_volume_price_confirmation,
    "early_late_momentum_divergence": calc_early_late_momentum_divergence,
    "consecutive_compression_count": calc_consecutive_compression_count,
    "smooth_momentum_structure": calc_smooth_momentum_structure,
    "volume_confirmed_trap_intensity": calc_volume_confirmed_trap_intensity,
}

def main():
    print("=== Digging & Testing Candidate Primitives ===")
    results = []

    # 1. Test Causality Perturbation for all candidate functions
    np.random.seed(42)
    op_dummy = np.random.randn(48).astype(np.float32) + 10.0
    hi_dummy = op_dummy + np.abs(np.random.randn(48).astype(np.float32)) * 0.1
    lo_dummy = op_dummy - np.abs(np.random.randn(48).astype(np.float32)) * 0.1
    cl_dummy = op_dummy + np.random.randn(48).astype(np.float32) * 0.05
    vol_dummy = np.random.randint(1000, 10000, 48).astype(np.float32)
    
    print("\n--- Running Causality Perturbation Tests ---")
    for name, fn in CANDIDATES.items():
        v1 = fn(op_dummy[:6], hi_dummy[:6], lo_dummy[:6], cl_dummy[:6], vol_dummy[:6], 10.0, 5000.0, False)
        
        # Scramble bars 6..47
        op_scrambled = op_dummy.copy()
        op_scrambled[6:] += 5.0
        v2 = fn(op_scrambled[:6], hi_dummy[:6], lo_dummy[:6], cl_dummy[:6], vol_dummy[:6], 10.0, 5000.0, False)
        diff = abs(v1 - v2)
        passed = diff < 1e-6
        print(f"[{'PASS' if passed else 'FAIL'}] {name:40s} Diff = {diff:.6e}")
        assert passed, f"Causality perturbation failed for {name}"

    # 2. Evaluate IC & Stability on Historical Data
    etf_list = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
    
    for etf in etf_list:
        print(f"\nEvaluating candidates on {etf}...")
        feat_file = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not feat_file.exists():
            print(f"Skipping {etf}: {feat_file} does not exist")
            continue

        df = pd.read_parquet(feat_file)
        y = df["trade_return"].values
        dates = df.index

        file_5m = INDEX_CONFIG[etf]["file_5m"]
        df_5m_path = REPO_ROOT / "data" / file_5m
        if not df_5m_path.exists():
            print(f"5m data missing for {etf}: {df_5m_path}")
            continue

        df_5m = pd.read_parquet(df_5m_path)
        is_20pct = etf in ["588000ETF", "159915ETF"]

        # Group 5m data by date
        dt_col = pd.to_datetime(df_5m["datetime"]) if "datetime" in df_5m.columns else pd.to_datetime(df_5m.index)
        df_5m["date"] = dt_col.dt.date

        # Precompute candidate values per day
        feature_values = {name: [] for name in CANDIDATES}
        valid_indices = []

        grouped = df_5m.groupby("date")
        exp_bar_vol = 50000.0

        for t_idx, dt in enumerate(dates):
            d_date = pd.to_datetime(dt).date()
            if d_date not in grouped.groups:
                continue
            day_bars = grouped.get_group(d_date).head(6)
            if len(day_bars) < 6:
                continue

            op = day_bars["open"].values.astype(np.float32)
            hi = day_bars["high"].values.astype(np.float32)
            lo = day_bars["low"].values.astype(np.float32)
            cl = day_bars["close"].values.astype(np.float32)
            vol = day_bars["volume"].values.astype(np.float32)
            prev_c = float(op[0])  # approx prev_close

            for name, fn in CANDIDATES.items():
                val = fn(op, hi, lo, cl, vol, prev_c, exp_bar_vol, is_20pct)
                feature_values[name].append(val)

            valid_indices.append(t_idx)

        y_valid = y[valid_indices]
        dates_valid = dates[valid_indices]

        for name in CANDIDATES:
            x = np.array(feature_values[name])
            if np.std(x) < 1e-8:
                continue
            metrics = compute_yearly_ic(x, y_valid, dates_valid)
            
            gate_pass = (metrics["ic_cv"] <= COMPONENT_IC_CV_MAX if "COMPONENT_IC_CV_MAX" in globals() else metrics["ic_cv"] <= 3.0) and \
                        (metrics["n_neg_years"] <= 2) and \
                        metrics["jackknife_pass"] and \
                        (abs(metrics["mean_ic"]) >= 0.02)

            res_record = {
                "feature_name": name,
                "etf": etf,
                "overall_ic": round(metrics["mean_ic"], 6),
                "ic_cv": round(metrics["ic_cv"], 4),
                "n_neg_years": metrics["n_neg_years"],
                "jackknife_pass": metrics["jackknife_pass"],
                "flips": metrics["flips"],
                "gate_pass": gate_pass
            }
            results.append(res_record)
            print(f"  {name:40s} | IC={metrics['mean_ic']:+.4f} | CV={metrics['ic_cv']:.2f} | NegYrs={metrics['n_neg_years']} | JK={metrics['jackknife_pass']} => {'PASS' if gate_pass else 'REJECT'}")

    # Export to mined_candidates.csv
    csv_path = HERE / "mined_candidates.csv"
    fieldnames = ["feature_name", "etf", "overall_ic", "ic_cv", "n_neg_years", "jackknife_pass", "flips", "gate_pass"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved all candidate screening evaluations to: {csv_path}")

    # Print Summary of Gate-Passing Features
    passing = [r for r in results if r["gate_pass"]]
    print(f"\n=== Gate-Passing Features Summary ({len(passing)} passed out of {len(results)}) ===")
    for p in passing:
        print(f"  ETF={p['etf']:10s} Feature={p['feature_name']:40s} IC={p['overall_ic']:+.4f} CV={p['ic_cv']:.2f}")

if __name__ == "__main__":
    main()
