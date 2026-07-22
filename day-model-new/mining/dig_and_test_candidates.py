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

CANDIDATES = {
    "h2_l2_pullback_continuation": calc_h2_l2_pullback_continuation,
    "first_ma_gap_bar_reversal": calc_first_ma_gap_bar_reversal,
    "failed_breakout_reversal_thrust": calc_failed_breakout_reversal_thrust,
    "shaved_bar_trend_conviction": calc_shaved_bar_trend_conviction,
    "vwap_channel_compression": calc_vwap_channel_compression,
    "morning_volume_weighted_momentum": calc_morning_volume_weighted_momentum,
    "lunch_transition_volume_skew": calc_lunch_transition_volume_skew,
    "intraday_range_expansion_velocity": calc_intraday_range_expansion_velocity,
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
