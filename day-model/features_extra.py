"""
New features imported from feature.csv (115 specifications).

Layout
------
- EARLY_EXTRA     : early-bar feature names computed causally from bars[0..decision_bar]
- DAY_EXTRA       : day-level feature names computed from daily Index history (T-1)
- YESTERDAY_EXTRA : yesterday mirrors of selected early features (computed by shift(1) upstream)

Speed / accuracy notes
----------------------
- All inner loops jit-compiled with numba (cache=True, fastmath=True).
- Arrays are passed as float32; outputs are float32.
- A single njit dispatcher computes every early-bar feature in one shot to amortize
  Python call overhead (~2700 days x 5 ETFs).
- Three primitives (_slope, _corr, _skew) are njit-callable and used by the dispatcher.

Causal / no-look-ahead policy
----------------------------
- Early-bar features consume only bars[0..decision_bar] inclusive.
- Day-level features are computed on full history ending at T-1.
- Yesterday mirrors are produced upstream via shift(1) on the early-frame.

Features requiring 20-day intraday volume history (volume_percentile_rank,
volume_regime_shift) are skipped — Index intraday history is not pre-cached in
this pipeline.  Features requiring 5m ATR(T-1) use an intraday ATR proxy
(mean early-bar range) instead.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from numba import njit


from deprecate_features import (
    INCLUDE_DEPRECATED,
    DEPRECATED_EARLY_EXTRA,
    DEPRECATED_YESTERDAY_EXTRA,
)

NaN32 = np.float32(np.nan)
N_EARLY_EXTRA = 131  # MUST match len(FULL_EARLY_EXTRA); kept as int for use inside njit


# ============================================================
# Feature name registry (single source of truth — order matters
# because the njit dispatcher returns values in this exact order)
# ============================================================
FULL_EARLY_EXTRA: list[str] = [
    # --- Brooks open patterns (6) ---
    "opening_gap_reversal", "spike_exhaustion_ratio", "barbed_wire_intensity",
    "wedge_open_flag", "inside_bar_compression", "volume_climax_exhaustion",
    # --- First-bar / opening-range (5) ---
    "first_bar_sentiment", "opening_range_size", "or_fill_ratio",
    "first_bar_body_ratio", "close_vs_open_range",
    # --- FVG / inside-bar breakouts (5) ---
    "intraday_bullish_fvg", "intraday_bearish_fvg",
    "inside_bar_failure_bull", "inside_bar_failure_bear",
    "gap_fill_ratio",
    # --- Single-bar patterns (5) ---
    "early_bullish_hammer", "early_bearish_shooting_star", "early_doji_count",
    "shark_32_signal", "decision_bar_reversal_signal",
    # --- Consecutive runs (8) ---
    "consecutive_up_closes", "consecutive_down_closes",
    "consecutive_higher_highs", "consecutive_lower_lows",
    "consecutive_same_close_dir",
    "consecutive_bullish_engulfing", "consecutive_bearish_engulfing",
    "consolidation_bars_count",
    # --- Engulfing counts (2) ---
    "early_bullish_engulfing_count", "early_bearish_engulfing_count",
    # --- Volume cluster (8) ---
    "volume_surge_max", "volume_dryup_ratio", "volume_concentration",
    "volume_trend_intraday", "volume_per_bar_regime", "volume_acceleration",
    "volume_price_corr", "volume_surge_direction",
    # --- Pullback / rally / range (9) ---
    "pullback_ratio", "rally_ratio", "range_expansion_ratio",
    "pullback_depth_ratio", "pullback_depth_max", "rally_strength_max",
    "range_expansion_final_bar", "range_compression_ratio",
    "breakout_strength_ratio",
    # --- VWAP cluster (7) ---
    "vwap_deviation_max", "vwap_slope_intraday", "vwap_cross_count",
    "vwap_deviation_decision_bar", "vwap_touch_count",
    "volume_weighted_price_position", "net_volume_flow",
    # --- Body / momentum / efficiency (10) ---
    "early_body_momentum", "open_efficiency", "late_bar_momentum",
    "trend_strength_intraday", "trend_bar_dominance", "trend_adherence",
    "high_low_sequence_momentum", "intraday_slope", "intraday_autocorr",
    "opening_momentum_score",
    # --- Direction stability / consistency (4) ---
    "opening_direction_stability", "early_trend_hhi", "early_trend_consistency",
    "trend_exhaustion_early",
    # --- Close / range position (8) ---
    "orb_breakout_sentiment", "opening_range_position",
    "session_high_proximity", "session_low_proximity",
    "close_above_open_count", "decision_bar_body", "decision_bar_range_rank",
    "open_to_current_return",
    # --- Tails (3) ---
    "upper_shadow_rejection", "lower_shadow_rejection", "upper_wick_dominance",
    # --- Range / body trends (2) ---
    "bar_size_trend", "body_size_trend",
    # --- Oscillators on opening bars (3) ---
    "rsi_opening", "stoch_opening", "adx_opening",
    # --- ATR-normalized momentum (3) ---
    "vwap_reversion_strength", "momentum_strength_intraday",
    "volatility_regime_intraday",
    # --- Composite / divergence (2) ---
    "momentum_divergence", "opening_auction_imbalance",
    # --- Yesterday-mirror bases (3) — current-day values; upstream shift produces yesterday_*
    "intraday_close_position",
    # NOTE: opening_gap_reversal & spike_exhaustion_ratio already in list;
    # their shifts feed yesterday_gap_reversal / yesterday_spike_exhaustion.
    # --- Mined Features v1 (30) ---
    "limit_up_proximity_early", "limit_down_proximity_early",
    "morning_hhi_persistence", "morning_trend_extrapolated",
    "early_bar_hhi_volume", "morning_mean_reversion_score",
    "demark_setup_reversal_early", "brooks_high_low_2_early",
    "failed_breakout_reversal_early", "price_action_thrust_ratio",
    "doji_cluster_intensity", "shaved_bars_ratio",
    "climax_reversal_followthrough", "early_wavetrend_osc",
    "early_wavetrend_cross", "atr_expansion_flag_early",
    "volatility_breakout_squeeze", "early_cvd_slope",
    "early_volume_imbalance_ratio", "early_bid_ask_spread_proxy",
    "volume_concentration_slope", "liquidity_density_early",
    "early_vwap_acceleration", "early_order_flow_imbalance",
    "rbreaker_buy_break_dist_early", "rbreaker_sell_break_dist_early",
    "rbreaker_sell_setup_proximity_early", "rbreaker_buy_setup_proximity_early",
    "skypark_gap_reversal_early", "turtle_breakout_strength_early",
    # --- Mined Base Primitives v2 (8) ---
    "star50_limit_proximity_early", "double_bottom_bull_flag_early",
    "moving_average_gap_bar_early", "tight_trading_range_breakout_thrust",
    "h2_l2_pullback_continuation", "shaved_bar_trend_conviction",
    "morning_volume_weighted_momentum", "lunch_transition_volume_skew",
    # --- Mined Base Primitives v3 (2) ---
    "volume_weighted_momentum_acceleration", "volume_price_confirmation"
]

# Dynamically filter out deprecated early extra features by default to manage the
# candidate-to-sample ratio and eliminate zero-stability collinear features.
EARLY_EXTRA: list[str] = (
    FULL_EARLY_EXTRA
    if INCLUDE_DEPRECATED
    else [f for f in FULL_EARLY_EXTRA if f not in DEPRECATED_EARLY_EXTRA]
)

# Day-level (computed in compute_daylevel_indicators, then shifted by 1 upstream)
DAY_EXTRA: list[str] = [
    # Yesterday OHLCV summary (T-1)
    "yesterday_range_ratio", "yesterday_body_ratio", "yesterday_volume_ratio",
    "yesterday_return", "yesterday_gap", "yesterday_close_position",
    # SMA distances (extra windows)
    "sma_distance_5d", "sma_distance_60d",
    # Percentile-rank context
    "volatility_percentile_20d", "volume_percentile_20d",
    # 52-week extremes
    "yearly_high_distance", "yearly_low_distance",
    # EMA-20 streak (Brooks Ch13)
    "twenty_gap_bars_regime",
    # Measured-move proximity (Brooks Ch7) — simplified pivot detection
    "measured_move_proximity",
    # Lunch break momentum preservation
    "lunch_break_momentum_preservation",
    # --- Mined Multi-Day Primitives (Batch 4) ---
    "dual_thrust_range_ratio", "close_location_in_range_3d",
]

# Yesterday mirrors (shift of early-frame columns produced upstream)
FULL_YESTERDAY_EXTRA: list[str] = [
    "yesterday_intraday_close_position",
    "yesterday_opening_gap_reversal",
    "yesterday_spike_exhaustion_ratio",
]

# Dynamically filter out deprecated yesterday features by default to manage dimensionality.
YESTERDAY_EXTRA: list[str] = (
    FULL_YESTERDAY_EXTRA
    if INCLUDE_DEPRECATED
    else [f for f in FULL_YESTERDAY_EXTRA if f not in DEPRECATED_YESTERDAY_EXTRA]
)


# ============================================================
# Numba primitives
# ============================================================
@njit(cache=True, fastmath=True)
def _slope(y: np.ndarray, n: int) -> float:
    """OLS slope of y vs x = [0..n-1]."""
    if n < 2:
        return 0.0
    sx = 0.0
    sy = 0.0
    sxx = 0.0
    sxy = 0.0
    for i in range(n):
        xi = float(i)
        yi = float(y[i])
        sx += xi
        sy += yi
        sxx += xi * xi
        sxy += xi * yi
    denom = float(n) * sxx - sx * sx
    if abs(denom) < 1e-12:
        return 0.0
    return (float(n) * sxy - sx * sy) / denom


@njit(cache=True, fastmath=True)
def _corr(a: np.ndarray, b: np.ndarray, n: int) -> float:
    if n < 3:
        return 0.0
    ma = 0.0
    mb = 0.0
    for i in range(n):
        ma += float(a[i])
        mb += float(b[i])
    ma /= n
    mb /= n
    saa = 0.0
    sbb = 0.0
    sab = 0.0
    for i in range(n):
        da = float(a[i]) - ma
        db = float(b[i]) - mb
        saa += da * da
        sbb += db * db
        sab += da * db
    if saa < 1e-12 or sbb < 1e-12:
        return 0.0
    return sab / (np.sqrt(saa) * np.sqrt(sbb))


@njit(cache=True, fastmath=True)
def _sign(x: float) -> float:
    if x > 0.0:
        return 1.0
    if x < 0.0:
        return -1.0
    return 0.0


# ============================================================
# Main early-bar dispatcher (njit, returns float32 array)
# ============================================================
@njit(cache=True, fastmath=True)
def _early_extras(op: np.ndarray, hi: np.ndarray, lo: np.ndarray,
                  cl: np.ndarray, vol: np.ndarray,
                  prev_close: float, exp_bar_vol: float,
                  is_20pct: bool, atr_5m_prev: float, bb_width_prev_price: float,
                  buy_break: float, sell_break: float, sell_setup: float, buy_setup: float,
                  high20: float, low20: float, atr20: float) -> np.ndarray:
    """Compute every EARLY_EXTRA feature for one day in one shot."""
    n = len(op)
    out = np.zeros(N_EARLY_EXTRA, dtype=np.float32)
    if n < 1 or prev_close <= 0.0 or exp_bar_vol <= 0.0:
        for k in range(len(out)):
            out[k] = np.float32(np.nan)
        return out

    O0 = float(op[0])
    H0 = float(hi[0])
    L0 = float(lo[0])
    C0 = float(cl[0])
    CD = float(cl[n - 1])
    OD = float(op[n - 1])
    HD = float(hi[n - 1])
    LD = float(lo[n - 1])

    # Opening high/low across [0..D]
    hh = H0
    ll = L0
    for i in range(n):
        if float(hi[i]) > hh:
            hh = float(hi[i])
        if float(lo[i]) < ll:
            ll = float(lo[i])
    rng = hh - ll
    rng_eps = rng + 1e-8

    # ----- 0 opening_gap_reversal -----
    g = (O0 - prev_close) / prev_close
    u = 0.0
    d = 0.0
    if g > 0.002 and n >= 2:
        l_min = float(lo[0])
        if float(lo[1]) < l_min:
            l_min = float(lo[1])
        u = max(0.0, O0 - l_min) / (g * prev_close + 1e-8)
    elif g < -0.002 and n >= 2:
        h_max = float(hi[0])
        if float(hi[1]) > h_max:
            h_max = float(hi[1])
        d = max(0.0, h_max - O0) / (-g * prev_close + 1e-8)
    out[0] = np.float32(u - d)

    # ----- 1 spike_exhaustion_ratio -----
    body0 = abs(C0 - O0) / (H0 - L0 + 1e-8)
    body1 = abs(float(cl[1]) - float(op[1])) / (float(hi[1]) - float(lo[1]) + 1e-8) if n >= 2 else 0.0
    spike = body0
    if body1 > spike:
        spike = body1
    ch_sum = 0.0
    ch_cnt = 0
    for i in range(2, n):
        ch_sum += abs(float(cl[i]) - float(op[i])) / (float(hi[i]) - float(lo[i]) + 1e-8)
        ch_cnt += 1
    ch_mean = ch_sum / ch_cnt if ch_cnt > 0 else 0.0
    out[1] = np.float32(spike / (ch_mean + 1e-8) - 1.0)

    # ----- 2 barbed_wire_intensity -----
    # longest run >=3 of overlapping bars (H_i<=H_{i-1}+eps AND L_i>=L_{i-1}-eps)
    longest = 0
    cur = 1
    doji_sum = 0.0
    tail_sum = 0.0
    doji_cnt = 0
    tail_cnt = 0
    # also accumulate stats inside runs
    cur_doji = 0.0
    cur_tail = 0.0
    cur_cnt = 0
    for i in range(1, n):
        eps = 0.0  # strict overlap
        if float(hi[i]) <= float(hi[i - 1]) + eps and float(lo[i]) >= float(lo[i - 1]) - eps:
            cur += 1
            rng_i = float(hi[i]) - float(lo[i])
            body_i = abs(float(cl[i]) - float(op[i]))
            cur_doji += (1.0 if body_i < 0.2 * (rng_i + 1e-8) else 0.0)
            cur_tail += ((float(hi[i]) - max(float(op[i]), float(cl[i])) +
                          min(float(op[i]), float(cl[i])) - float(lo[i])) / (rng_i + 1e-8))
            cur_cnt += 1
        else:
            if cur >= 3 and cur_cnt > 0:
                if cur > longest:
                    longest = cur
                doji_sum += cur_doji
                tail_sum += cur_tail
                doji_cnt += cur_cnt
                tail_cnt += cur_cnt
            cur = 1
            cur_doji = 0.0
            cur_tail = 0.0
            cur_cnt = 0
    if cur >= 3 and cur_cnt > 0:
        if cur > longest:
            longest = cur
        doji_sum += cur_doji
        tail_sum += cur_tail
        doji_cnt += cur_cnt
        tail_cnt += cur_cnt
    if longest >= 3 and n > 0:
        d_mean = doji_sum / doji_cnt if doji_cnt > 0 else 0.0
        t_mean = tail_sum / tail_cnt if tail_cnt > 0 else 0.0
        out[2] = np.float32(longest * d_mean * t_mean / (n + 1))
    else:
        out[2] = np.float32(0.0)

    # ----- 3 wedge_open_flag -----
    # Detect 3 descending peaks OR 3 ascending troughs among local pivots.
    # Pivots defined at interior indices 1..n-2 with H_i>H_{i-1},H_{i+1} (peak)
    # or L_i<L_{i-1},L_{i+1} (trough).
    peaks_i = []
    peaks_v = []
    trgh_i = []
    trgh_v = []
    for i in range(1, n - 1):
        if float(hi[i]) > float(hi[i - 1]) and float(hi[i]) > float(hi[i + 1]):
            peaks_i.append(i)
            peaks_v.append(float(hi[i]))
        if float(lo[i]) < float(lo[i - 1]) and float(lo[i]) < float(lo[i + 1]):
            trgh_i.append(i)
            trgh_v.append(float(lo[i]))
    desc3 = 0
    if len(peaks_v) >= 3:
        if peaks_v[0] > peaks_v[1] and peaks_v[1] > peaks_v[2]:
            desc3 = 1
    asc3 = 0
    if len(trgh_v) >= 3:
        if trgh_v[0] < trgh_v[1] and trgh_v[1] < trgh_v[2]:
            asc3 = 1
    if desc3:
        out[3] = np.float32(-1.0)
    elif asc3:
        out[3] = np.float32(1.0)
    else:
        out[3] = np.float32(0.0)

    # ----- 4 inside_bar_compression -----
    # r = 1 - mean(H-L for inside bars)/mean(H-L for all bars)
    all_sum = 0.0
    for i in range(n):
        all_sum += float(hi[i]) - float(lo[i])
    all_mean = all_sum / n
    ins_sum = 0.0
    ins_cnt = 0
    for i in range(1, n):
        if float(hi[i]) <= float(hi[i - 1]) and float(lo[i]) >= float(lo[i - 1]):
            ins_sum += float(hi[i]) - float(lo[i])
            ins_cnt += 1
    if ins_cnt > 0 and all_mean > 1e-8:
        out[4] = np.float32(1.0 - (ins_sum / ins_cnt) / all_mean)
    else:
        out[4] = np.float32(0.0)

    # ----- 5 volume_climax_exhaustion -----
    # ev = exp_bar_vol; vr = max(V_i / ev); pb = argmax; reversal score
    vr_max = -1.0
    pb = 0
    for i in range(n):
        ratio = float(vol[i]) / exp_bar_vol
        if ratio > vr_max:
            vr_max = ratio
            pb = i
    rng_pb = float(hi[pb]) - float(lo[pb]) + 1e-8
    mid_pb = (float(hi[pb]) + float(lo[pb])) / 2.0
    rev = 1.0 - 2.0 * abs(float(cl[pb]) - mid_pb) / rng_pb
    out[5] = np.float32(max(vr_max - 1.0, 0.0) * rev)

    # ----- 6 first_bar_sentiment -----
    out[6] = np.float32(_sign(C0 - O0))

    # ----- 7 opening_range_size -----
    out[7] = np.float32((H0 - L0) / (prev_close + 1e-8))

    # ----- 8 or_fill_ratio : (C_D - L0) / (H0 - L0) -----
    out[8] = np.float32((CD - L0) / (H0 - L0 + 1e-8))

    # ----- 9 first_bar_body_ratio -----
    out[9] = np.float32(abs(O0 - C0) / (H0 - L0 + 1e-8))

    # ----- 10 close_vs_open_range : (C_D - O0) / (H0 - L0) -----
    out[10] = np.float32((CD - O0) / (H0 - L0 + 1e-8))

    # ----- 11 intraday_bullish_fvg : max(0, max(L_{i-1} - H_{i-2})) for i>=2 -----
    bfvg = 0.0
    for i in range(2, n):
        diff = float(lo[i - 1]) - float(hi[i - 2])
        if diff > bfvg:
            bfvg = diff
    out[11] = np.float32(bfvg / (prev_close + 1e-8))

    # ----- 12 intraday_bearish_fvg : max(0, max(L_{i-2} - H_{i-1})) -----
    sfvg = 0.0
    for i in range(2, n):
        diff = float(lo[i - 2]) - float(hi[i - 1])
        if diff > sfvg:
            sfvg = diff
    out[12] = np.float32(sfvg / (prev_close + 1e-8))

    # ----- 13 inside_bar_failure_bull -----
    cnt = 0
    for i in range(1, n - 1):
        if float(hi[i]) <= float(hi[i - 1]) and float(lo[i]) >= float(lo[i - 1]):
            if float(hi[i + 1]) > float(hi[i]) and float(cl[i + 1]) > float(lo[i]):
                cnt += 1
    out[13] = np.float32(min(cnt, 3))

    # ----- 14 inside_bar_failure_bear -----
    cnt = 0
    for i in range(1, n - 1):
        if float(hi[i]) <= float(hi[i - 1]) and float(lo[i]) >= float(lo[i - 1]):
            if float(lo[i + 1]) < float(lo[i]) and float(cl[i + 1]) < float(hi[i]):
                cnt += 1
    out[14] = np.float32(min(cnt, 3))

    # ----- 15 gap_fill_ratio -----
    # fraction of bars i>=2 where bar i range overlaps both L_{i-1} and H_{i-2} (fill)
    gap_cnt = 0
    fill_cnt = 0
    for i in range(2, n):
        # bullish gap exists when L_{i-1} > H_{i-2}
        if float(lo[i - 1]) > float(hi[i - 2]):
            gap_cnt += 1
            if float(lo[i]) <= float(hi[i - 2]):
                fill_cnt += 1
        elif float(lo[i - 2]) > float(hi[i - 1]):
            gap_cnt += 1
            if float(hi[i]) >= float(lo[i - 2]):
                fill_cnt += 1
    out[15] = np.float32(fill_cnt / (gap_cnt + 1e-8)) if gap_cnt > 0 else np.float32(0.0)

    # ----- 16 early_bullish_hammer -----
    best = 0.0
    for i in range(n):
        body = abs(float(cl[i]) - float(op[i]))
        lower = min(float(op[i]), float(cl[i])) - float(lo[i])
        upper = float(hi[i]) - max(float(op[i]), float(cl[i]))
        if lower > 2.0 * body and upper < body and float(cl[i]) > float(op[i]):
            r = lower / (body + 1e-8)
            if r > best:
                best = r
    out[16] = np.float32(best)

    # ----- 17 early_bearish_shooting_star -----
    best = 0.0
    for i in range(n):
        body = abs(float(cl[i]) - float(op[i]))
        upper = float(hi[i]) - max(float(op[i]), float(cl[i]))
        lower = min(float(op[i]), float(cl[i])) - float(lo[i])
        if upper > 2.0 * body and lower < body and float(cl[i]) < float(op[i]):
            r = upper / (body + 1e-8)
            if r > best:
                best = r
    out[17] = np.float32(best)

    # ----- 18 early_doji_count -----
    doji = 0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i])
        if abs(float(cl[i]) - float(op[i])) < 0.1 * (rng_i + 1e-8):
            doji += 1
    out[18] = np.float32(doji / (n + 1e-8))

    # ----- 19 shark_32_signal -----
    flag = 0
    for i in range(n - 2):
        if (float(lo[i + 2]) < float(lo[i + 1]) < float(lo[i])
                and float(hi[i + 2]) > float(hi[i + 1]) > float(hi[i])):
            flag = 1
            break
    out[19] = np.float32(flag)

    # ----- 20 decision_bar_reversal_signal -----
    body_sign = _sign(CD - OD)
    reversal = 0.0
    if n >= 2:
        prev_h = float(hi[n - 2])
        prev_l = float(lo[n - 2])
        if (CD > OD and LD < prev_l) or (CD < OD and HD > prev_h):
            reversal = 1.0
    out[20] = np.float32(body_sign * reversal)

    # ----- 21 consecutive_up_closes -----
    max_run = 1
    cur_run = 1
    for i in range(1, n):
        if float(cl[i]) > float(cl[i - 1]):
            cur_run += 1
            if cur_run > max_run:
                max_run = cur_run
        else:
            cur_run = 1
    out[21] = np.float32(max_run / (n + 1e-8))

    # ----- 22 consecutive_down_closes -----
    max_run = 1
    cur_run = 1
    for i in range(1, n):
        if float(cl[i]) < float(cl[i - 1]):
            cur_run += 1
            if cur_run > max_run:
                max_run = cur_run
        else:
            cur_run = 1
    out[22] = np.float32(max_run / (n + 1e-8))

    # ----- 23 consecutive_higher_highs -----
    max_run = 1
    cur_run = 1
    for i in range(1, n):
        if float(hi[i]) > float(hi[i - 1]):
            cur_run += 1
            if cur_run > max_run:
                max_run = cur_run
        else:
            cur_run = 1
    out[23] = np.float32(max_run / (n + 1e-8))

    # ----- 24 consecutive_lower_lows -----
    max_run = 1
    cur_run = 1
    for i in range(1, n):
        if float(lo[i]) < float(lo[i - 1]):
            cur_run += 1
            if cur_run > max_run:
                max_run = cur_run
        else:
            cur_run = 1
    out[24] = np.float32(max_run / (n + 1e-8))

    # ----- 25 consecutive_same_close_dir (max of up/down runs) -----
    max_up = 1
    max_dn = 1
    cur_up = 1
    cur_dn = 1
    for i in range(1, n):
        if float(cl[i]) > float(cl[i - 1]):
            cur_up += 1
            cur_dn = 1
        elif float(cl[i]) < float(cl[i - 1]):
            cur_dn += 1
            cur_up = 1
        else:
            cur_up = 1
            cur_dn = 1
        if cur_up > max_up:
            max_up = cur_up
        if cur_dn > max_dn:
            max_dn = cur_dn
    out[25] = np.float32(max(max_up, max_dn) / (n + 1e-8))

    # ----- 26 consecutive_bullish_engulfing -----
    max_run = 0
    cur_run = 0
    for i in range(1, n):
        if (float(cl[i]) > float(op[i]) and float(cl[i]) > float(cl[i - 1])
                and float(op[i]) < float(cl[i - 1])):
            cur_run += 1
            if cur_run > max_run:
                max_run = cur_run
        else:
            cur_run = 0
    out[26] = np.float32(min(max_run, 3) / 3.0)

    # ----- 27 consecutive_bearish_engulfing -----
    max_run = 0
    cur_run = 0
    for i in range(1, n):
        if (float(cl[i]) < float(op[i]) and float(cl[i]) < float(cl[i - 1])
                and float(op[i]) > float(cl[i - 1])):
            cur_run += 1
            if cur_run > max_run:
                max_run = cur_run
        else:
            cur_run = 0
    out[27] = np.float32(min(max_run, 3) / 3.0)

    # ----- 28 consolidation_bars_count -----
    cnt = 0
    for i in range(1, n):
        if float(hi[i]) <= float(hi[i - 1]) and float(lo[i]) >= float(lo[i - 1]):
            cnt += 1
    out[28] = np.float32(cnt / (n + 1e-8))

    # ----- 29 early_bullish_engulfing_count -----
    # proper engulfing: prior bar bearish (C_{i-1}<O_{i-1}) and current bull engulfs
    cnt = 0
    for i in range(1, n):
        if (float(cl[i]) > float(op[i]) and float(cl[i]) > float(cl[i - 1])
                and float(op[i]) < float(cl[i - 1])
                and float(cl[i - 1]) < float(op[i - 1])):
            cnt += 1
    out[29] = np.float32(min(cnt, 3) / 3.0)

    # ----- 30 early_bearish_engulfing_count -----
    cnt = 0
    for i in range(1, n):
        if (float(cl[i]) < float(op[i]) and float(cl[i]) < float(cl[i - 1])
                and float(op[i]) > float(cl[i - 1])
                and float(cl[i - 1]) > float(op[i - 1])):
            cnt += 1
    out[30] = np.float32(min(cnt, 3) / 3.0)

    # ----- 31 volume_surge_max -----
    out[31] = np.float32(vr_max)

    # ----- 32 volume_dryup_ratio -----
    dry = 0
    for i in range(n):
        if float(vol[i]) < exp_bar_vol:
            dry += 1
    out[32] = np.float32(dry / (n + 1e-8))

    # ----- 33 volume_concentration : top-3 share -----
    total = 0.0
    for i in range(n):
        total += float(vol[i])
    v1 = 0.0
    v2 = 0.0
    v3 = 0.0
    for i in range(n):
        v = float(vol[i])
        if v >= v1:
            v3 = v2
            v2 = v1
            v1 = v
        elif v >= v2:
            v3 = v2
            v2 = v
        elif v > v3:
            v3 = v
    out[33] = np.float32((v1 + v2 + v3) / (total + 1e-8))

    # ----- 34 volume_trend_intraday : slope(vol)/mean(vol) -----
    out[34] = np.float32(_slope(vol, n) / (np.float64(np.mean(vol)) + 1e-8))

    # ----- 35 volume_per_bar_regime : sum(V)/(exp_bar_vol) - (n)/48 -----
    sum_v = 0.0
    for i in range(n):
        sum_v += float(vol[i])
    out[35] = np.float32(sum_v / (exp_bar_vol + 1e-8) - n / 48.0)

    # ----- 36 volume_acceleration : (mean(last2) - mean(first2)) / mean(all) -----
    if n >= 4:
        first2 = (float(vol[0]) + float(vol[1])) / 2.0
        last2 = (float(vol[n - 1]) + float(vol[n - 2])) / 2.0
        out[36] = np.float32((last2 - first2) / (np.float64(np.mean(vol)) + 1e-8))
    else:
        out[36] = np.float32(0.0)

    # ----- 37 volume_price_corr : corr(V, body_ratio) -----
    body_ratios = np.zeros(n, dtype=np.float32)
    for i in range(n):
        body_ratios[i] = np.float32(abs(float(cl[i]) - float(op[i])) /
                                    (float(hi[i]) - float(lo[i]) + 1e-8))
    out[37] = np.float32(_corr(vol, body_ratios, n))

    # ----- 38 volume_surge_direction -----
    out[38] = np.float32(_sign(float(cl[pb]) - float(op[pb])) * max(vr_max - 1.0, 0.0))

    # ----- 39 pullback_ratio : (hh - C_D) / (hh - ll) -----
    out[39] = np.float32((hh - CD) / rng_eps)

    # ----- 40 rally_ratio : (C_D - ll) / (hh - ll) -----
    out[40] = np.float32((CD - ll) / rng_eps)

    # ----- 41 range_expansion_ratio : (hh - ll) / (H0 - L0) -----
    out[41] = np.float32(rng / (H0 - L0 + 1e-8))

    # ----- 42 pullback_depth_ratio : (hh - max(C_D, H_D)) / (hh - ll) -----
    out[42] = np.float32((hh - max(CD, HD)) / rng_eps)

    # ----- 43 pullback_depth_max : (hh - min(C_i)) / (hh - ll) -----
    cmin = CD
    for i in range(n):
        if float(cl[i]) < cmin:
            cmin = float(cl[i])
    out[43] = np.float32((hh - cmin) / rng_eps)

    # ----- 44 rally_strength_max : (max(C_i) - ll) / (hh - ll) -----
    cmax = CD
    for i in range(n):
        if float(cl[i]) > cmax:
            cmax = float(cl[i])
    out[44] = np.float32((cmax - ll) / rng_eps)

    # ----- 45 range_expansion_final_bar : (H_D - L_D)/mean(H_i-L_i for i<D) - 1 -----
    if n >= 2:
        s = 0.0
        for i in range(n - 1):
            s += float(hi[i]) - float(lo[i])
        m_prev = s / (n - 1)
        out[45] = np.float32((HD - LD) / (m_prev + 1e-8) - 1.0)
    else:
        out[45] = np.float32(0.0)

    # ----- 46 range_compression_ratio : (H0 - L0)/mean(recent 5m ATR proxy) -----
    # use intraday ATR proxy = mean early bar range
    s = 0.0
    for i in range(n):
        s += float(hi[i]) - float(lo[i])
    atr_proxy = s / n
    out[46] = np.float32((H0 - L0) / (atr_proxy + 1e-8))

    # ----- 47 breakout_strength_ratio -----
    if CD > hh:
        out[47] = np.float32((CD - hh) / rng_eps)
    elif CD < ll:
        out[47] = np.float32((CD - ll) / rng_eps)
    else:
        out[47] = np.float32(0.0)

    # ----- 48 vwap_deviation_max : max|C_i - vwap_i| / (hh - ll) -----
    cum_cv = 0.0
    cum_v = 0.0
    vwap_dev_max = 0.0
    for i in range(n):
        cum_cv += float(cl[i]) * float(vol[i])
        cum_v += float(vol[i])
        vwap_i = cum_cv / (cum_v + 1e-8)
        dev = abs(float(cl[i]) - vwap_i)
        if dev > vwap_dev_max:
            vwap_dev_max = dev
    out[48] = np.float32(vwap_dev_max / rng_eps)

    # ----- 49 vwap_slope_intraday -----
    vwap_arr = np.zeros(n, dtype=np.float32)
    cum_cv = 0.0
    cum_v = 0.0
    for i in range(n):
        cum_cv += float(cl[i]) * float(vol[i])
        cum_v += float(vol[i])
        vwap_arr[i] = np.float32(cum_cv / (cum_v + 1e-8))
    out[49] = np.float32(_slope(vwap_arr, n) / (atr_proxy + 1e-8))

    # ----- 50 vwap_cross_count -----
    crosses = 0
    above = (C0 > float(vwap_arr[0]))
    for i in range(1, n):
        cur_above = (float(cl[i]) > float(vwap_arr[i]))
        if cur_above != above:
            crosses += 1
            above = cur_above
    out[50] = np.float32(crosses / (n + 1e-8))

    # ----- 51 vwap_deviation_decision_bar -----
    vwap_d = float(vwap_arr[n - 1])
    bar_d_rng = HD - LD + 1e-8
    out[51] = np.float32((CD - vwap_d) / bar_d_rng)

    # ----- 52 vwap_touch_count -----
    touch = 0
    for i in range(n):
        v_i = float(vwap_arr[i])
        if min(float(lo[i]), float(cl[i])) <= v_i and max(float(hi[i]), float(cl[i])) >= v_i:
            touch += 1
    out[52] = np.float32(touch / (n + 1e-8))

    # ----- 53 volume_weighted_price_position : (vwap_d - ll)/(hh - ll) -----
    out[53] = np.float32((vwap_d - ll) / rng_eps)

    # ----- 54 net_volume_flow : sum((C-O)/(H-L) * V) -----
    nvf = 0.0
    for i in range(n):
        nvf += ((float(cl[i]) - float(op[i])) /
                (float(hi[i]) - float(lo[i]) + 1e-8)) * float(vol[i])
    out[54] = np.float32(nvf / (total + 1e-8))

    # ----- 55 early_body_momentum : sum(body_i) -----
    ebm = 0.0
    for i in range(n):
        ebm += (float(cl[i]) - float(op[i])) / (float(hi[i]) - float(lo[i]) + 1e-8)
    out[55] = np.float32(ebm)

    # ----- 56 open_efficiency : mean(|C-O|/(H-L)) -----
    oe_sum = 0.0
    for i in range(n):
        oe_sum += abs(float(cl[i]) - float(op[i])) / (float(hi[i]) - float(lo[i]) + 1e-8)
    out[56] = np.float32(oe_sum / (n + 1e-8))

    # ----- 57 late_bar_momentum : sum(body_i for last2) - sum(body_i for first2) -----
    body_i_arr = np.zeros(n, dtype=np.float32)
    for i in range(n):
        body_i_arr[i] = np.float32((float(cl[i]) - float(op[i])) /
                                   (float(hi[i]) - float(lo[i]) + 1e-8))
    if n >= 4:
        first2 = float(body_i_arr[0]) + float(body_i_arr[1])
        last2 = float(body_i_arr[n - 1]) + float(body_i_arr[n - 2])
        out[57] = np.float32(last2 - first2)
    else:
        out[57] = np.float32(0.0)

    # ----- 58 trend_strength_intraday : sum(sign(C-O))/(D+1) -----
    ts = 0.0
    for i in range(n):
        ts += _sign(float(cl[i]) - float(op[i]))
    out[58] = np.float32(ts / (n + 1e-8))

    # ----- 59 trend_bar_dominance : fraction of trend bars -----
    tb = 0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        if (float(cl[i]) > float(op[i]) and (float(cl[i]) - float(lo[i])) / rng_i > 0.7):
            tb += 1
        elif (float(cl[i]) < float(op[i]) and (float(hi[i]) - float(cl[i])) / rng_i > 0.7):
            tb += 1
    out[59] = np.float32(tb / (n + 1e-8))

    # ----- 60 trend_adherence : fraction bars matching prior bar direction -----
    if n >= 2:
        ad = 0
        for i in range(1, n):
            if _sign(float(cl[i]) - float(op[i])) == _sign(float(cl[i - 1]) - float(op[i - 1])):
                ad += 1
        out[60] = np.float32(ad / (n - 1 + 1e-8))
    else:
        out[60] = np.float32(0.0)

    # ----- 61 high_low_sequence_momentum -----
    num = 0.0
    den = 0.0
    for i in range(n):
        diff = float(cl[i]) - float(op[i])
        num += diff
        den += abs(diff)
    out[61] = np.float32(num / (den + 1e-8))

    # ----- 62 intraday_slope -----
    out[62] = np.float32(_slope(cl, n) / (np.float64(np.mean(cl)) + 1e-8))

    # ----- 63 intraday_autocorr : lag-1 of bar returns -----
    if n >= 3:
        rets = np.zeros(n, dtype=np.float32)
        for i in range(1, n):
            rets[i] = np.float32((float(cl[i]) - float(cl[i - 1])) /
                                 (float(cl[i - 1]) + 1e-8))
        a = rets[1:n - 1].copy()
        b = rets[2:n].copy()
        out[63] = np.float32(_corr(a, b, len(a)))
    else:
        out[63] = np.float32(0.0)

    # ----- 64 opening_momentum_score -----
    oms = 0.0
    for i in range(n):
        oms += _sign(float(cl[i]) - float(op[i])) * \
               abs(float(cl[i]) - float(op[i])) / (float(hi[i]) - float(lo[i]) + 1e-8)
    out[64] = np.float32(oms / (n + 1e-8))

    # ----- 65 opening_direction_stability : 1 - std(sign(C-O)) -----
    signs = np.zeros(n, dtype=np.float32)
    for i in range(n):
        signs[i] = np.float32(_sign(float(cl[i]) - float(op[i])))
    s_mean = float(np.mean(signs))
    var = 0.0
    for i in range(n):
        var += (float(signs[i]) - s_mean) ** 2
    std = (var / (n + 1e-8)) ** 0.5
    out[65] = np.float32(1.0 - std)

    # ----- 66 early_trend_hhi -----
    n_up = 0
    n_dn = 0
    for i in range(n):
        s = _sign(float(cl[i]) - float(op[i]))
        if s > 0:
            n_up += 1
        elif s < 0:
            n_dn += 1
    tot = n_up + n_dn
    if tot > 0:
        pu = n_up / tot
        pd = n_dn / tot
        out[66] = np.float32(pu * pu + pd * pd)
    else:
        out[66] = np.float32(0.0)

    # ----- 67 early_trend_consistency -----
    if n >= 2:
        signs_ret = np.zeros(n - 1, dtype=np.float32)
        for i in range(1, n):
            signs_ret[i - 1] = np.float32(_sign(float(cl[i]) - float(cl[i - 1])))
        pos = 0
        neg = 0
        for i in range(len(signs_ret)):
            if signs_ret[i] > 0:
                pos += 1
            elif signs_ret[i] < 0:
                neg += 1
        out[67] = np.float32(max(pos, neg) / (len(signs_ret) + 1e-8))
    else:
        out[67] = np.float32(0.0)

    # ----- 68 trend_exhaustion_early -----
    streak_norm = max(out[21], out[22])  # consecutive_up/down normalized
    out[68] = np.float32(max(0.0, 1.0 - abs(out[55]) * streak_norm))

    # ----- 69 orb_breakout_sentiment -----
    if CD > hh:
        out[69] = np.float32(_sign(CD - hh))
    elif CD < ll:
        out[69] = np.float32(_sign(CD - ll))
    else:
        out[69] = np.float32(0.0)

    # ----- 70 opening_range_position : (C_D - ll)/(hh - ll) (alias of rally_ratio) -----
    out[70] = np.float32((CD - ll) / rng_eps)

    # ----- 71 session_high_proximity -----
    out[71] = np.float32((CD - hh) / rng_eps)

    # ----- 72 session_low_proximity -----
    out[72] = np.float32((CD - ll) / rng_eps)

    # ----- 73 close_above_open_count -----
    cnt = 0
    for i in range(n):
        if float(cl[i]) > float(op[i]):
            cnt += 1
    out[73] = np.float32(cnt / (n + 1e-8))

    # ----- 74 decision_bar_body -----
    out[74] = np.float32(abs(CD - OD) / (HD - LD + 1e-8))

    # ----- 75 decision_bar_range_rank -----
    d_rng = HD - LD
    rank = 0
    for i in range(n):
        if (float(hi[i]) - float(lo[i])) <= d_rng:
            rank += 1
    out[75] = np.float32(rank / (n + 1e-8))

    # ----- 76 open_to_current_return -----
    out[76] = np.float32((CD - O0) / (O0 + 1e-8))

    # ----- 77 upper_shadow_rejection : max((H-max(O,C))/(H-L)) -----
    best = 0.0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        r = (float(hi[i]) - max(float(op[i]), float(cl[i]))) / rng_i
        if r > best:
            best = r
    out[77] = np.float32(best)

    # ----- 78 lower_shadow_rejection -----
    best = 0.0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        r = (min(float(op[i]), float(cl[i])) - float(lo[i])) / rng_i
        if r > best:
            best = r
    out[78] = np.float32(best)

    # ----- 79 upper_wick_dominance -----
    max_up = 0.0
    max_lo = 0.0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        u = (float(hi[i]) - max(float(op[i]), float(cl[i]))) / rng_i
        l = (min(float(op[i]), float(cl[i])) - float(lo[i])) / rng_i
        if u > max_up:
            max_up = u
        if l > max_lo:
            max_lo = l
    out[79] = np.float32(max_up / (max_lo + 1e-8))

    # ----- 80 bar_size_trend -----
    rng_arr = np.zeros(n, dtype=np.float32)
    for i in range(n):
        rng_arr[i] = np.float32(float(hi[i]) - float(lo[i]))
    out[80] = np.float32(_slope(rng_arr, n) / (np.float64(np.mean(rng_arr)) + 1e-8))

    # ----- 81 body_size_trend -----
    body_arr = np.zeros(n, dtype=np.float32)
    for i in range(n):
        body_arr[i] = np.float32(abs(float(cl[i]) - float(op[i])))
    out[81] = np.float32(_slope(body_arr, n) / (np.float64(np.mean(body_arr)) + 1e-8))

    # ----- 82 rsi_opening -----
    up = 0.0
    dn = 0.0
    for i in range(n):
        diff = float(cl[i]) - float(op[i])
        if diff > 0:
            up += diff
        else:
            dn += -diff
    up /= n
    dn /= n
    rsi = 100.0 - 100.0 / (1.0 + up / (dn + 1e-8))
    out[82] = np.float32(rsi / 100.0)

    # ----- 83 stoch_opening -----
    out[83] = np.float32(100.0 * (CD - ll) / rng_eps / 100.0)

    # ----- 84 adx_opening -----
    if n >= 2:
        up_moves = np.zeros(n, dtype=np.float32)
        dn_moves = np.zeros(n, dtype=np.float32)
        trs = np.zeros(n, dtype=np.float32)
        for i in range(1, n):
            up_moves[i] = np.float32(max(float(hi[i]) - float(lo[i - 1]), 0.0))
            dn_moves[i] = np.float32(max(float(lo[i - 1]) - float(hi[i]), 0.0))
            trs[i] = np.float32(max(float(hi[i]) - float(lo[i]),
                                    max(abs(float(hi[i]) - float(cl[i - 1])),
                                        abs(float(lo[i]) - float(cl[i - 1])))))
        plus_dm = float(np.mean(up_moves[1:]))
        minus_dm = float(np.mean(dn_moves[1:]))
        atr_avg = float(np.mean(trs[1:])) + 1e-8
        dx = 100.0 * abs(plus_dm - minus_dm) / (plus_dm + minus_dm + 1e-8)
        out[84] = np.float32(dx / 100.0)
    else:
        out[84] = np.float32(0.0)

    # ----- 85 vwap_reversion_strength : (C_D - vwap_d)/atr_proxy -----
    out[85] = np.float32((CD - vwap_d) / (atr_proxy + 1e-8))

    # ----- 86 momentum_strength_intraday : (C_D - C0)/C0/atr_proxy -----
    out[86] = np.float32((CD - C0) / (C0 + 1e-8) / (atr_proxy + 1e-8))

    # ----- 87 volatility_regime_intraday : dispersion of bar ranges
    #      (CSV spec wants mean(H-L)/atr_5m(T-1); T-1 5m ATR not pre-cached,
    #      so use std(bar ranges)/(mean(bar ranges)) as regime proxy)
    rng_mean = float(np.mean(rng_arr))
    rng_std = float(np.std(rng_arr))
    out[87] = np.float32(rng_std / (rng_mean + 1e-8))

    # ----- 88 momentum_divergence -----
    pm = out[62]   # intraday_slope
    vm = out[34]   # volume_trend_intraday
    out[88] = np.float32(_sign(pm) * _sign(-vm) if abs(vm) > 1e-6 else 0.0)

    # ----- 89 opening_auction_imbalance (= normalized net_volume_flow) -----
    out[89] = np.float32(nvf / (total + 1e-8))

    # ----- 90 intraday_close_position : (C_D - L0)/(H0 - L0) (yesterday mirror base) -----
    out[90] = np.float32((CD - L0) / (H0 - L0 + 1e-8))

    # ----- 91 limit_up_proximity_early -----
    limit_up_mult = 1.20 if is_20pct else 1.10
    out[91] = np.float32((hh - prev_close * limit_up_mult) / (prev_close * limit_up_mult + 1e-8))

    # ----- 92 limit_down_proximity_early -----
    limit_down_mult = 0.80 if is_20pct else 0.90
    out[92] = np.float32((ll - prev_close * limit_down_mult) / (prev_close * limit_down_mult + 1e-8))

    # ----- 93 morning_hhi_persistence -----
    n_up = 0
    n_dn = 0
    for i in range(n):
        s = _sign(float(cl[i]) - float(op[i]))
        if s > 0.0:
            n_up += 1
        elif s < 0.0:
            n_dn += 1
    pu = n_up / n if n > 0 else 0.0
    pd = n_dn / n if n > 0 else 0.0
    out[93] = np.float32(pu * pu + pd * pd)

    # ----- 94 morning_trend_extrapolated -----
    slp = _slope(cl, n)
    xm = (n - 1) / 2.0
    ym = 0.0
    for i in range(n):
        ym += float(cl[i])
    ym /= n
    intercept = ym - slp * xm
    projected_close = slp * 42.0 + intercept
    out[94] = np.float32((projected_close - CD) / (atr_proxy + 1e-8))

    # ----- 95 early_bar_hhi_volume -----
    v_sum = 0.0
    for i in range(n):
        v_sum += float(vol[i])
    hhi_vol = 0.0
    if v_sum > 0.0:
        for i in range(n):
            pct = float(vol[i]) / v_sum
            hhi_vol += pct * pct
    out[95] = np.float32(hhi_vol)

    # ----- 96 morning_mean_reversion_score -----
    rev_score = 0.0
    if n >= 3:
        for i in range(2, n):
            rev_score += _sign(float(cl[i]) - float(cl[i - 1])) * _sign(float(cl[i - 1]) - float(cl[i - 2]))
        rev_score /= (n - 2)
    out[96] = np.float32(rev_score)

    # ----- 97 demark_setup_reversal_early -----
    demark_sum = 0.0
    for i in range(n):
        if i >= 4:
            ref = float(cl[i - 4])
        else:
            ref = prev_close
        if float(cl[i]) < ref:
            demark_sum += 1.0
        elif float(cl[i]) > ref:
            demark_sum -= 1.0
    out[97] = np.float32(demark_sum)

    # ----- 98 brooks_high_low_2_early -----
    high_breaks = 0
    low_breaks = 0
    for i in range(1, n):
        if float(cl[i]) > float(hi[i - 1]):
            high_breaks += 1
        elif float(cl[i]) < float(lo[i - 1]):
            low_breaks += 1
    if high_breaks >= 2:
        out[98] = np.float32(1.0)
    elif low_breaks >= 2:
        out[98] = np.float32(-1.0)
    else:
        out[98] = np.float32(0.0)

    # ----- 99 failed_breakout_reversal_early -----
    flag = 0.0
    if n >= 6:
        h_max = H0
        l_min = L0
        for i in range(n):
            if float(hi[i]) > h_max:
                h_max = float(hi[i])
            if float(lo[i]) < l_min:
                l_min = float(lo[i])
        if h_max > H0 and CD < L0:
            flag = 1.0
        elif l_min < L0 and CD > H0:
            flag = -1.0
    out[99] = np.float32(flag)

    # ----- 100 price_action_thrust_ratio -----
    body_sum = 0.0
    for i in range(n):
        body_sum += abs(float(cl[i]) - float(op[i]))
    out[100] = np.float32(body_sum / rng_eps)

    # ----- 101 doji_cluster_intensity -----
    max_doji_run = 0
    cur_doji_run = 0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        if abs(float(cl[i]) - float(op[i])) < 0.1 * rng_i:
            cur_doji_run += 1
            if cur_doji_run > max_doji_run:
                max_doji_run = cur_doji_run
        else:
            cur_doji_run = 0
    out[101] = np.float32(max_doji_run)

    # ----- 102 shaved_bars_ratio -----
    shaved_count = 0
    for i in range(n):
        if abs(float(cl[i]) - float(hi[i])) < 1e-6 or abs(float(cl[i]) - float(lo[i])) < 1e-6:
            shaved_count += 1
    out[102] = np.float32(shaved_count / n if n > 0 else 0.0)

    # ----- 103 climax_reversal_followthrough -----
    climax_val = -1.0
    climax_idx = 0
    for i in range(n):
        if float(vol[i]) > climax_val:
            climax_val = float(vol[i])
            climax_idx = i
    c_clim = float(cl[climax_idx])
    o_clim = float(op[climax_idx])
    val = 0.0
    if c_clim > o_clim:
        val = CD - c_clim
    else:
        val = o_clim - CD
    out[103] = np.float32(val / (atr_proxy + 1e-8))

    # ----- 104 early_wavetrend_osc -----
    ap_bar = np.zeros(n, dtype=np.float32)
    for i in range(n):
        ap_bar[i] = (float(hi[i]) + float(lo[i]) + float(cl[i])) / 3.0
    esa_bar = np.zeros(n, dtype=np.float32)
    d_bar = np.zeros(n, dtype=np.float32)
    if n > 0:
        esa_bar[0] = ap_bar[0]
        d_bar[0] = 0.0
        for i in range(1, n):
            esa_bar[i] = 0.5 * ap_bar[i] + 0.5 * esa_bar[i - 1]
            d_bar[i] = 0.5 * abs(ap_bar[i] - esa_bar[i]) + 0.5 * d_bar[i - 1]
    wt1_val = (ap_bar[n - 1] - esa_bar[n - 1]) / (0.015 * d_bar[n - 1] + 1e-8)
    out[104] = np.float32(wt1_val / 100.0)

    # ----- 105 early_wavetrend_cross -----
    wt1_prev = 0.0
    if n >= 2:
        wt1_prev = (ap_bar[n - 2] - esa_bar[n - 2]) / (0.015 * d_bar[n - 2] + 1e-8)
    wt2_val = (wt1_val + wt1_prev) / 2.0
    out[105] = np.float32((wt1_val - wt2_val) / 100.0)

    # ----- 106 atr_expansion_flag_early -----
    out[106] = np.float32(atr_proxy / (atr_5m_prev / np.sqrt(48.0) + 1e-8))

    # ----- 107 volatility_breakout_squeeze -----
    out[107] = np.float32((hh - ll) / (bb_width_prev_price + 1e-8))

    # ----- 108 early_cvd_slope -----
    cvd = np.zeros(n, dtype=np.float32)
    cum_cvd = 0.0
    for i in range(n):
        cum_cvd += _sign(float(cl[i]) - float(op[i])) * float(vol[i])
        cvd[i] = cum_cvd
    out[108] = np.float32(_slope(cvd, n) / (exp_bar_vol + 1e-8))

    # ----- 109 early_volume_imbalance_ratio -----
    v_up = 0.0
    v_dn = 0.0
    for i in range(n):
        diff = float(cl[i]) - float(op[i])
        if diff > 0.0:
            v_up += float(vol[i])
        else:
            v_dn += float(vol[i])
    out[109] = np.float32(v_up / (v_dn + 1e-8))

    # ----- 110 early_bid_ask_spread_proxy -----
    spread_sum = 0.0
    for i in range(n):
        spread_sum += (float(hi[i]) - float(lo[i])) / (float(vol[i]) + 1e-8)
    out[110] = np.float32(spread_sum / n if n > 0 else 0.0)

    # ----- 111 volume_concentration_slope -----
    v_shares = np.zeros(n, dtype=np.float32)
    for i in range(n):
        v_shares[i] = float(vol[i]) / (total + 1e-8)
    out[111] = np.float32(_slope(v_shares, n))

    # ----- 112 liquidity_density_early -----
    c_diff_sum = 0.0
    for i in range(1, n):
        c_diff_sum += abs(float(cl[i]) - float(cl[i - 1]))
    out[112] = np.float32(c_diff_sum / (total + 1e-8))

    # ----- 113 early_vwap_acceleration -----
    if n >= 6:
        vwap_first = vwap_arr[0:3].copy()
        vwap_last = vwap_arr[3:6].copy()
        out[113] = np.float32((_slope(vwap_last, 3) - _slope(vwap_first, 3)) / (atr_proxy + 1e-8))
    else:
        out[113] = np.float32(0.0)

    # ----- 114 early_order_flow_imbalance -----
    ofi = 0.0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        ofi += ((float(cl[i]) - float(lo[i]) - (float(hi[i]) - float(cl[i]))) / rng_i) * float(vol[i])
    out[114] = np.float32(ofi / (total + 1e-8))

    # ----- 115 rbreaker_buy_break_dist_early -----
    out[115] = np.float32((CD - buy_break) / (atr_5m_prev + 1e-8))

    # ----- 116 rbreaker_sell_break_dist_early -----
    out[116] = np.float32((CD - sell_break) / (atr_5m_prev + 1e-8))

    # ----- 117 rbreaker_sell_setup_proximity_early -----
    out[117] = np.float32((hh - sell_setup) / (atr_5m_prev + 1e-8))

    # ----- 118 rbreaker_buy_setup_proximity_early -----
    out[118] = np.float32((ll - buy_setup) / (atr_5m_prev + 1e-8))

    # ----- 119 skypark_gap_reversal_early -----
    sky = 0.0
    if abs(g) >= 0.01 and n >= 2:
        h15 = float(hi[1])
        l15 = float(lo[1])
        for i in range(1, n):
            if float(hi[i]) > h15:
                h15 = float(hi[i])
            if float(lo[i]) < l15:
                l15 = float(lo[i])
        sky = ((h15 - H0) - (L0 - l15)) / prev_close
    out[119] = np.float32(sky)

    # ----- 120 turtle_breakout_strength_early -----
    turtle = 0.0
    if CD > high20:
        turtle = (CD - high20) / (atr20 + 1e-8)
    elif CD < low20:
        turtle = (CD - low20) / (atr20 + 1e-8)
    out[120] = np.float32(turtle)

    # ----- 121 star50_limit_proximity_early -----
    limit_pct = 0.20 if is_20pct else 0.10
    upper_limit = prev_close * (1.0 + limit_pct)
    lower_limit = prev_close * (1.0 - limit_pct)
    dist_upper = (upper_limit - hh) / prev_close
    dist_lower = (ll - lower_limit) / prev_close
    out[121] = np.float32((dist_lower - dist_upper) / limit_pct)

    # ----- 122 double_bottom_bull_flag_early -----
    db_flag = 0.0
    if n >= 4:
        min_idx1 = 0
        min_v1 = float(lo[0])
        for i in range(1, n // 2):
            if float(lo[i]) < min_v1:
                min_v1 = float(lo[i])
                min_idx1 = i
        min_v2 = float(lo[n // 2])
        for i in range(n // 2 + 1, n):
            if float(lo[i]) < min_v2:
                min_v2 = float(lo[i])
        diff_v = abs(min_v2 - min_v1)
        if diff_v <= 0.3 * (rng + 1e-8):
            db_flag = (1.0 - diff_v / (rng + 1e-8)) * (CD - min_v2) / (rng + 1e-8)
    out[122] = np.float32(min(max(db_flag, -1.0), 1.0))

    # ----- 123 moving_average_gap_bar_early -----
    gap_cnt = 0.0
    for i in range(n):
        sum_p = 0.0
        cnt_p = 0
        for j in range(max(0, i - 2), i + 1):
            sum_p += float(cl[j])
            cnt_p += 1
        ma_i = sum_p / float(cnt_p)
        if float(lo[i]) > ma_i:
            gap_cnt += 1.0
        elif float(hi[i]) < ma_i:
            gap_cnt -= 1.0
    out[123] = np.float32(gap_cnt / float(n))

    # ----- 124 tight_trading_range_breakout_thrust -----
    ttr_thrust = 0.0
    if n >= 3:
        hh_ttr = float(hi[0])
        ll_ttr = float(lo[0])
        for i in range(1, n - 1):
            if float(hi[i]) > hh_ttr:
                hh_ttr = float(hi[i])
            if float(lo[i]) < ll_ttr:
                ll_ttr = float(lo[i])
        ttr_rng = hh_ttr - ll_ttr
        ttr_thrust = (CD - OD) / (ttr_rng + 1e-8)
    out[124] = np.float32(min(max(ttr_thrust, -2.0), 2.0) / 2.0)

    # ----- 125 h2_l2_pullback_continuation -----
    h_pullbacks = 0
    l_pullbacks = 0
    for i in range(1, n):
        if float(hi[i]) < float(hi[i - 1]):
            h_pullbacks += 1
        if float(lo[i]) > float(lo[i - 1]):
            l_pullbacks += 1
    val_h2 = float(h_pullbacks - l_pullbacks) / float(n) if n > 0 else 0.0
    out[125] = np.float32(min(max(val_h2, -1.0), 1.0))

    # ----- 126 shaved_bar_trend_conviction -----
    score_shaved = 0.0
    for i in range(n):
        rng_i = float(hi[i]) - float(lo[i]) + 1e-8
        body_i = float(cl[i]) - float(op[i])
        upper_wick = float(hi[i]) - max(float(op[i]), float(cl[i]))
        lower_wick = min(float(op[i]), float(cl[i])) - float(lo[i])
        if body_i > 0 and lower_wick < 0.1 * rng_i:
            score_shaved += abs(body_i) / rng_i
        elif body_i < 0 and upper_wick < 0.1 * rng_i:
            score_shaved -= abs(body_i) / rng_i
    val_shaved = score_shaved / float(n) if n > 0 else 0.0
    out[126] = np.float32(min(max(val_shaved, -1.0), 1.0))

    # ----- 127 morning_volume_weighted_momentum -----
    ret_mwm = (CD - O0) / (O0 + 1e-8)
    tot_vol_mwm = 0.0
    for i in range(n):
        tot_vol_mwm += float(vol[i])
    avg_vol_mwm = tot_vol_mwm / float(n) if n > 0 else 0.0
    vol_ratio_mwm = avg_vol_mwm / (exp_bar_vol + 1e-8)
    val_mwm = ret_mwm * min(vol_ratio_mwm, 3.0) / 0.02
    out[127] = np.float32(min(max(val_mwm, -1.0), 1.0))

    # ----- 128 lunch_transition_volume_skew -----
    val_lvs = 0.0
    if n >= 6:
        v_early = float(vol[0]) + float(vol[1])
        v_late = float(vol[4]) + float(vol[5])
        val_lvs = (v_late - v_early) / (v_early + v_late + 1e-8)
    out[128] = np.float32(min(max(val_lvs, -1.0), 1.0))

    # ----- 129 volume_weighted_momentum_acceleration -----
    # Second derivative of volume-weighted price: momentum building vs fading.
    # Compares volume-weighted return of last half vs first half of early bars.
    if n >= 4:
        mid_vwma = n // 2
        vw_ret_first = 0.0
        vol_first_vwma = 0.0
        for i in range(mid_vwma):
            ret_i = (float(cl[i]) - float(op[i])) / (float(op[i]) + 1e-8)
            vw_ret_first += ret_i * float(vol[i])
            vol_first_vwma += float(vol[i])
        if vol_first_vwma > 0:
            vw_ret_first /= vol_first_vwma
        vw_ret_second = 0.0
        vol_second_vwma = 0.0
        for i in range(mid_vwma, n):
            ret_i = (float(cl[i]) - float(op[i])) / (float(op[i]) + 1e-8)
            vw_ret_second += ret_i * float(vol[i])
            vol_second_vwma += float(vol[i])
        if vol_second_vwma > 0:
            vw_ret_second /= vol_second_vwma
        val_vwma = (vw_ret_second - vw_ret_first) / (atr_proxy / (prev_close + 1e-8) + 1e-8)
        out[129] = np.float32(min(max(val_vwma, -1.0), 1.0))
    else:
        out[129] = np.float32(0.0)

    # ----- 130 volume_price_confirmation -----
    # Correlation between volume and signed body direction.
    # Positive = volume confirms trend (healthy), Negative = divergence.
    if n >= 3:
        sum_v_vpc = 0.0
        sum_b_vpc = 0.0
        sum_vv_vpc = 0.0
        sum_bb_vpc = 0.0
        sum_vb_vpc = 0.0
        for i in range(n):
            v_vpc = float(vol[i])
            rng_i_vpc = float(hi[i]) - float(lo[i]) + 1e-8
            b_vpc = (float(cl[i]) - float(op[i])) / rng_i_vpc
            sum_v_vpc += v_vpc
            sum_b_vpc += b_vpc
            sum_vv_vpc += v_vpc * v_vpc
            sum_bb_vpc += b_vpc * b_vpc
            sum_vb_vpc += v_vpc * b_vpc
        nf_vpc = float(n)
        cov_vpc = sum_vb_vpc - (sum_v_vpc * sum_b_vpc) / nf_vpc
        var_v_vpc = sum_vv_vpc - (sum_v_vpc * sum_v_vpc) / nf_vpc
        var_b_vpc = sum_bb_vpc - (sum_b_vpc * sum_b_vpc) / nf_vpc
        if var_v_vpc > 1e-8 and var_b_vpc > 1e-8:
            corr_vpc = cov_vpc / (np.sqrt(var_v_vpc) * np.sqrt(var_b_vpc) + 1e-8)
            out[130] = np.float32(min(max(corr_vpc, -1.0), 1.0))
        else:
            out[130] = np.float32(0.0)
    else:
        out[130] = np.float32(0.0)

    return out


# Constant tuple for use inside njit (must be defined at module load)
EARLY_EXTRA_N = tuple(FULL_EARLY_EXTRA)


# ============================================================
# Public Python wrappers
# ============================================================
def extract_early_extras(day_5m: pd.DataFrame, prev_close: float,
                         exp_bar_vol: float, decision_bar: int,
                         is_20pct: bool = False, atr14_prev: float = 0.0,
                         bb_width_prev_price: float = 0.0, buy_break: float = 0.0,
                         sell_break: float = 0.0, sell_setup: float = 0.0,
                         buy_setup: float = 0.0, high20: float = 0.0,
                         low20: float = 0.0, atr20: float = 0.0) -> dict:
    """Slice bars[0..decision_bar], cast to float32, dispatch to numba helper."""
    bars = day_5m.head(decision_bar + 1)
    if len(bars) < 1 or prev_close is None or np.isnan(prev_close) or prev_close <= 0 \
            or exp_bar_vol is None or np.isnan(exp_bar_vol) or exp_bar_vol <= 0:
        return {k: np.float32(np.nan) for k in EARLY_EXTRA}

    op = bars["open"].values.astype(np.float32)
    hi = bars["high"].values.astype(np.float32)
    lo = bars["low"].values.astype(np.float32)
    cl = bars["close"].values.astype(np.float32)
    vol = bars["volume"].values.astype(np.float32)

    vals = _early_extras(
        op, hi, lo, cl, vol,
        np.float32(prev_close), np.float32(exp_bar_vol),
        is_20pct, np.float32(atr14_prev), np.float32(bb_width_prev_price),
        np.float32(buy_break), np.float32(sell_break), np.float32(sell_setup), np.float32(buy_setup),
        np.float32(high20), np.float32(low20), np.float32(atr20)
    )
    
    full_dict = {name: np.float32(vals[i]) for i, name in enumerate(FULL_EARLY_EXTRA)}
    if INCLUDE_DEPRECATED:
        return full_dict
    else:
        return {k: v for k, v in full_dict.items() if k not in DEPRECATED_EARLY_EXTRA}


def empty_early_extras() -> dict:
    return {k: np.float32(np.nan) for k in EARLY_EXTRA}


# ============================================================
# Day-level extras (pandas / numpy vectorized on full history)
# ============================================================
def compute_daylevel_extras(df_1d: pd.DataFrame) -> pd.DataFrame:
    """Compute day-level extras from daily Index data.

    Returns a DataFrame indexed like df_1d with DAY_EXTRA columns.
    Upstream shifts the entire frame by 1 day to prevent leakage.
    """
    out = pd.DataFrame(index=df_1d.index)
    px = df_1d["close_adj"]
    hi = df_1d["high_adj"]
    lo = df_1d["low_adj"]
    op = df_1d["open_adj"]
    vol = df_1d["volume"]

    # ATR(14) on daily — reused
    prev_close = px.shift(1)
    tr = pd.concat([(hi - lo).abs(),
                    (hi - prev_close).abs(),
                    (lo - prev_close).abs()], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean()

    # --- Yesterday OHLCV summary (T-1 → already shifted upstream by 1) ---
    out["yesterday_range_ratio"] = (hi - lo) / (px + 1e-8)
    out["yesterday_body_ratio"] = (px - op).abs() / (hi - lo + 1e-8)
    out["yesterday_volume_ratio"] = vol / (vol.rolling(20).mean() + 1e-8)
    out["yesterday_return"] = (px - px.shift(1)) / (px.shift(1) + 1e-8)
    out["yesterday_gap"] = (op - px.shift(1)) / (px.shift(1) + 1e-8)
    out["yesterday_close_position"] = (px - lo) / (hi - lo + 1e-8)

    # --- SMA distances ---
    sma5 = px.rolling(5).mean()
    sma60 = px.rolling(60).mean()
    out["sma_distance_5d"] = (px - sma5) / (sma5 + 1e-8)
    out["sma_distance_60d"] = (px - sma60) / (sma60 + 1e-8)

    # --- Percentile ranks (20-day) ---
    out["volatility_percentile_20d"] = atr14.rolling(20).apply(
        _pct_rank_1d, raw=True)
    out["volume_percentile_20d"] = vol.rolling(20).apply(
        _pct_rank_1d, raw=True)

    # --- 52-week extremes ---
    high_252 = hi.rolling(252).max()
    low_252 = lo.rolling(252).min()
    out["yearly_high_distance"] = (px - high_252) / (atr14 + 1e-8)
    out["yearly_low_distance"] = (px - low_252) / (atr14 + 1e-8)

    # --- Brooks Ch13: 20-EMA gap-bar streak ---
    ema20 = px.ewm(span=20, adjust=False).mean()
    above = (px > ema20).astype(int)
    below = (px < ema20).astype(int)
    # consecutive streak ending at T-1
    bull_streak = _consecutive_streak(above.values)
    bear_streak = _consecutive_streak(below.values)
    out["twenty_gap_bars_regime"] = np.clip(
        (bull_streak - bear_streak) / 20.0, -1.0, 1.0)

    # --- Brooks Ch7: measured-move proximity (simplified 2-bar pivots) ---
    out["measured_move_proximity"] = _measured_move_proximity(
        hi.values, lo.values, px.values, atr14.values)

    # --- Market Microstructure: lunch break momentum preservation ---
    out["lunch_break_momentum_preservation"] = np.clip(
        ((px - op) / (hi - lo + 1e-8)).rolling(5).mean(), -1.0, 1.0)

    # --- Mined Multi-Day Primitives (Batch 4) ---
    # Dual-Thrust range asymmetry (3-day): upside vs downside range dominance.
    # From Dual-Thrust strategy: Range = max(HH-LC, HC-LL).
    # Positive = upside range dominates (bullish bias), Negative = downside.
    hh3 = hi.rolling(3).max()
    ll3 = lo.rolling(3).min()
    hc3 = px.rolling(3).max()
    lc3 = px.rolling(3).min()
    upside_range = hh3 - lc3
    downside_range = hc3 - ll3
    total_dt_range = np.maximum(upside_range, downside_range)
    out["dual_thrust_range_ratio"] = np.clip(
        (upside_range - downside_range) / (total_dt_range + 1e-8), -1.0, 1.0)

    # Close location in range (3-day average): where closes sit within daily range.
    # High = closes near highs (buyers in control), Low = closes near lows.
    # Negative IC: overbought when high → predicts lower forward returns.
    close_pos = (px - lo) / (hi - lo + 1e-8)
    out["close_location_in_range_3d"] = np.clip(
        (close_pos.rolling(3).mean() - 0.5) * 2.0, -1.0, 1.0)

    return out[DAY_EXTRA]


def _pct_rank_1d(arr: np.ndarray) -> float:
    """Rolling percentile rank of last value vs window."""
    v = arr[-1]
    if np.isnan(v):
        return np.nan
    valid = arr[~np.isnan(arr)]
    if len(valid) < 2:
        return np.nan
    return float(np.sum(valid <= v) / len(valid))


def _consecutive_streak(flags: np.ndarray) -> np.ndarray:
    """Run-length of consecutive 1s ending at each position."""
    out = np.zeros(len(flags), dtype=np.float32)
    run = 0
    for i, f in enumerate(flags):
        if f:
            run += 1
        else:
            run = 0
        out[i] = run
    return out


def _measured_move_proximity(highs: np.ndarray, lows: np.ndarray,
                             closes: np.ndarray, atr14: np.ndarray) -> np.ndarray:
    """Simplified measured-move: pivot high/low detection (2-bar), then
    project leg-measured target from last leg.
    Returns ratio = (close - target)/atr14, clipped to [-2, 2]."""
    n = len(closes)
    out = np.zeros(n, dtype=np.float32)
    piv_h_idx = []
    piv_h_val = []
    piv_l_idx = []
    piv_l_val = []
    for i in range(1, n - 1):
        if np.isnan(highs[i]) or np.isnan(lows[i]):
            continue
        if highs[i] >= highs[i - 1] and highs[i] > highs[i + 1]:
            piv_h_idx.append(i)
            piv_h_val.append(highs[i])
        if lows[i] <= lows[i - 1] and lows[i] < lows[i + 1]:
            piv_l_idx.append(i)
            piv_l_val.append(lows[i])
    for t in range(n):
        if t < 5 or np.isnan(atr14[t]) or atr14[t] <= 0:
            out[t] = 0.0
            continue
        # find most recent two pivots before t-1
        ph = [(idx, val) for idx, val in zip(piv_h_idx, piv_h_val) if idx < t - 1]
        pl = [(idx, val) for idx, val in zip(piv_l_idx, piv_l_val) if idx < t - 1]
        if len(ph) < 1 or len(pl) < 1:
            out[t] = 0.0
            continue
        last_ph_idx, last_ph_val = ph[-1]
        last_pl_idx, last_pl_val = pl[-1]
        leg = last_ph_val - last_pl_val
        if leg <= 0:
            out[t] = 0.0
            continue
        if last_ph_idx > last_pl_idx:
            # last leg up: target = H + (H - L)
            target = last_ph_val + leg
        else:
            target = last_pl_val - leg
        r = (closes[t] - target) / (atr14[t] + 1e-8)
        out[t] = np.float32(np.clip(r, -2.0, 2.0))
    return out
