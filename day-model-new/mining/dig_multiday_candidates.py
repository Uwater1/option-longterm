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
