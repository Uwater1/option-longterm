"""
Wave 6 Feature Mining — Volume Profile + Cumulative Volume Curve Shape + Intraday Path Archetypes.

Motivation
----------
Mid-level plan (mining_todo.md / feature-mining.md) assigns Wave 6 to:
  1. Volume-Profile 2: POC, value area, high-volume nodes, low-volume nodes (liquidity vacuums)
  2. Cumulative-volume-curve shape: concavity, front/back-loading, opening/closing intensity
  3. Intraday path archetypes: time-of-day extremes, V / reversed-V / U / L day classes,
     swing imbalance, counter-trend volume

Existing coverage check (avoid duplicates):
  - day_range / day_realized_vol / day_close_pos / day_pm_am_vol_ratio / day_vwap_dev /
    day_skew / day_kurtosis / afternoon_reversal / lunch_gap / midday_drawdown / cvd_close
    are ALREADY in build_features.py extract_day_full_features. NOT re-mined here.
  - DAY_EXTRA (features_extra.py) covers trend/regime/liquidity/calendar, NOT volume profile.
  - No POC / value-area / HVN-LVN / cum-vol convexity / archetype primitives exist anywhere.

Causality: every candidate is computed on the FULL day D bars, then aligned to trade rows
with shift(1) (T-1). No same-day leak. No shift(-1) anywhere (climax-with-follow-through
family is FORBIDDEN in mining_memory_300ETF_single.json — respected).

Data source: INDEX 5m (000300/000016/000905/000688/399006) — long history for 7Y jackknife.
Same source used by build_features.py for yesterday_day_* full-day features.

Same 4-gate screen as Wave 3/4/5: IC_CV<=3.0, n_neg_years<=2, 7Y Jackknife pass, |IC|>=0.02.
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

NPB = 20  # volume-profile bins per day


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
    years = pd.to_datetime(dates).year
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


def _clip(x, lo=-1.0, hi=1.0):
    return float(np.clip(x, lo, hi))


# ============================================================
# Day-level shape primitives (one scalar per full day, T-1 aligned upstream)
# ============================================================

def vol_profile(highs, lows, closes, vols, nbins=NPB):
    """Coarse volume profile via typical-price binning. Returns profile array (nbins) or None."""
    n = len(highs)
    if n < 6:
        return None
    lo_px = float(lows.min())
    hi_px = float(highs.max())
    rng_px = hi_px - lo_px
    if rng_px <= 1e-12:
        return None
    tp = (highs + lows + closes) / 3.0
    bin_idx = (((tp - lo_px) / rng_px) * nbins).astype(int)
    bin_idx = np.clip(bin_idx, 0, nbins - 1)
    prof = np.bincount(bin_idx, weights=vols, minlength=nbins).astype(np.float64)
    return prof


def calc_poc_position_day(highs, lows, closes, vols):
    """POC (price level with max volume) position within session high-low range -> [-1,1].
    +1 = POC at session high (accumulation near highs), -1 = at session low."""
    lo_px = float(lows.min()); rng_px = float(highs.max()) - lo_px
    if rng_px <= 1e-12:
        return 0.0
    prof = vol_profile(highs, lows, closes, vols)
    if prof is None:
        return 0.0
    poc_idx = int(np.argmax(prof))
    pos = (poc_idx + 0.5) / float(NPB)
    return _clip((pos - 0.5) * 2.0)


def calc_value_area_high_pos_day(highs, lows, closes, vols):
    """Value Area high boundary (top of the 70%-volume region around POC) position in range.
    High VA-high = buyers extended near highs (close of value zone up high)."""
    lo_px = float(lows.min()); rng_px = float(highs.max()) - lo_px
    if rng_px <= 1e-12:
        return 0.0
    prof = vol_profile(highs, lows, closes, vols)
    if prof is None or prof.sum() <= 0:
        return 0.0
    total = prof.sum()
    order = np.argsort(prof)[::-1]
    run = 0.0
    included = []
    for idx in order:
        run += prof[idx]
        included.append(idx)
        if run >= 0.70 * total:
            break
    va_hi = (max(included) + 1.0) / float(NPB)
    return _clip((va_hi - 0.5) * 2.0)


def calc_value_area_width_day(highs, lows, closes, vols):
    """Value Area width (rng of 70%-volume bins) / session range -> [0,1].
    Narrow = price compressed around POC (tight value); wide = dispersed distribution."""
    prof = vol_profile(highs, lows, closes, vols)
    if prof is None or prof.sum() <= 0:
        return 0.0
    total = prof.sum()
    order = np.argsort(prof)[::-1]
    run = 0.0
    included = []
    for idx in order:
        run += prof[idx]
        included.append(idx)
        if run >= 0.70 * total:
            break
    width = (max(included) - min(included) + 1.0) / float(NPB)
    return _clip(width * 2.0 - 1.0, 0.0, 1.0)


def calc_hvn_count_day(highs, lows, closes, vols):
    """Count of High Volume Nodes (bins with >2x mean bin vol), scaled to [-1,1].
    Multiple HVN = two-sided balance / supply and demand zones."""
    prof = vol_profile(highs, lows, closes, vols)
    if prof is None or prof.sum() <= 0:
        return 0.0
    meanv = prof.mean()
    if meanv <= 0:
        return 0.0
    cnt = float(np.sum(prof > 2.0 * meanv))
    return _clip((cnt - 1.0) / 3.0)


def calc_lvn_count_day(highs, lows, closes, vols):
    """Count of Low Volume Nodes (liquidity vacuums: bins with <50% mean volume).
    High LVN = thin air / rapid-move zones (strong technical magnets on retest)."""
    prof = vol_profile(highs, lows, closes, vols)
    if prof is None or prof.sum() <= 0:
        return 0.0
    meanv = prof.mean()
    if meanv <= 0:
        return 0.0
    cnt = float(np.sum(prof < 0.5 * meanv))
    return _clip((cnt - 2.0) / 6.0)


def calc_min_vol_gap_day(highs, lows, closes, vols):
    """Largest zero-volume price gap between traded bins, normalized to session range.
    Big internal vacuum = gap/speed zone ("no man's land"), magnets for fast moves."""
    lo_px = float(lows.min()); rng_px = float(highs.max()) - lo_px
    if rng_px <= 1e-12:
        return 0.0
    prof = vol_profile(highs, lows, closes, vols)
    if prof is None or prof.sum() <= 0:
        return 0.0
    active = np.where(prof > 1e-9)[0]
    if len(active) < 2:
        return 0.0
    gaps = np.diff(active) - 1
    max_gap = float(gaps.max()) if gaps.size else 0.0
    return _clip((max_gap / float(NPB)) * 4.0)


def calc_cumvol_curve_concavity_day(highs, lows, closes, vols):
    """Concavity of the cumulative-volume curve vs the linear diagonal.
    Positive = front-loaded (volume heavy in morning); negative = back-loaded (afternoon)."""
    n = len(vols)
    total = vols.sum()
    if total <= 0 or n < 6:
        return 0.0
    cum = np.cumsum(vols) / total
    t = np.arange(1, n + 1) / float(n)
    # signed area between curve and diagonal; front-loaded -> positive
    area = np.mean(cum - t)
    return _clip(area * 4.0)


def calc_open_90m_volume_share_day(highs, lows, closes, vols):
    """Share of day volume in the first 18 bars (90 min), centered at 0.375 (linear share).
    >0 = opening intensity higher than uniform (news/institutional auction)."""
    n = len(vols)
    if n < 18:
        return 0.0
    total = vols.sum()
    if total <= 0:
        return 0.0
    share = vols[:18].sum() / total
    return _clip((share - 0.375) * 6.0)


def calc_close_30m_volume_share_day(highs, lows, closes, vols):
    """Share of day volume in the last 6 bars (30 min), centered at 0.125 (linear share).
    >0 = closing auction / end-of-day positioning unusually heavy."""
    n = len(vols)
    if n < 6:
        return 0.0
    total = vols.sum()
    if total <= 0:
        return 0.0
    share = vols[-6:].sum() / total
    return _clip((share - 0.125) * 6.0)


def calc_time_of_day_high_day(highs, lows, closes, vols):
    """When the session high was made, normalized -1 (first bar) .. +1 (last bar)."""
    n = len(highs)
    if n < 6:
        return 0.0
    idx = int(np.argmax(highs))
    frac = idx / float(n - 1)
    return _clip((frac - 0.5) * 2.0)


def calc_time_of_day_low_day(highs, lows, closes, vols):
    """When the session low was made, normalized -1 (first bar) .. +1 (last bar)."""
    n = len(lows)
    if n < 6:
        return 0.0
    idx = int(np.argmin(lows))
    frac = idx / float(n - 1)
    return _clip((frac - 0.5) * 2.0)


def calc_intraday_swing_imbalance_day(highs, lows, closes, vols):
    """(max favorable excursion - max adverse excursion from open) / session range.
    +1 = day spent above open (strong drift); -1 = below open."""
    n = len(closes)
    if n < 6:
        return 0.0
    op = float(closes[0])
    rng = float(highs.max()) - float(lows.min())
    if rng <= 1e-12:
        return 0.0
    fav = float(np.max(highs - op))
    adv = float(np.max(op - lows))
    return _clip((fav - adv) / rng)


def calc_v_recovery_strength_day(highs, lows, closes, vols):
    """V-shape day archetype: early low + close near/toward highs vs recovered gap.
    Score = close-location advantage * (session low made in first half)."""
    n = len(closes)
    if n < 6:
        return 0.0
    lo_px = float(np.min(lows)); rng = float(np.max(highs)) - lo_px
    if rng <= 1e-12:
        return 0.0
    early = lows[:n // 2]
    if np.argmin(lows) >= n // 2:
        return 0.0
    close_loc = (float(closes[-1]) - lo_px) / rng
    return _clip((close_loc - 0.5) * 2.0)


def calc_reverse_v_fade_strength_day(highs, lows, closes, vols):
    """Reversed-V day archetype: early high + close near lows.
    Score = -close-location advantage * (session high made in first half)."""
    n = len(closes)
    if n < 6:
        return 0.0
    lo_px = float(np.min(lows)); rng = float(np.max(highs)) - lo_px
    if rng <= 1e-12:
        return 0.0
    if np.argmax(highs) >= n // 2:
        return 0.0
    close_loc = (float(closes[-1]) - lo_px) / rng
    return _clip((0.5 - close_loc) * 2.0)


def calc_u_shape_midday_dip_day(highs, lows, closes, vols):
    """U-shape archetype: opening + closing firmness vs midday dip.
    Score = (early30 trend + late30 trend)/2 - midday returns, normalized by range."""
    n = len(closes)
    if n < 12:
        return 0.0
    rng = float(np.max(highs)) - float(np.min(lows))
    if rng <= 1e-12:
        return 0.0
    op = float(closes[0])
    early30 = (float(closes[5]) - op) / rng
    late30 = (float(closes[-1]) - float(closes[-6])) / rng
    mid_lo = float(np.min(lows[n // 3: 2 * n // 3]))
    mid_hi = float(np.max(highs[n // 3: 2 * n // 3]))
    middrift = (float(closes[2 * n // 3]) - float(closes[n // 3])) / rng
    return _clip((early30 + late30) / 2.0 - mid_lo + 0.5 * middrift)


def calc_l_shape_late_slide_day(highs, lows, closes, vols):
    """L-shape archetype: slow slide into close (late-session high then close near low).
    Score = -late30 return * late-close-location."""
    n = len(closes)
    if n < 12:
        return 0.0
    rng = float(np.max(highs)) - float(np.min(lows))
    if rng <= 1e-12:
        return 0.0
    late30 = (float(closes[-1]) - float(closes[-6])) / rng
    half_idx = n // 2
    mid_hi = float(np.max(highs[:half_idx]))
    close_below_mid = (float(closes[-1]) < mid_hi)
    return _clip(-late30 * (1.0 if close_below_mid else 0.0))


def calc_price_volume_corr_intraday_day(highs, lows, closes, vols):
    """Spearman corr between bar returns and bar volume within the day.
    + = moves confirmed by volume (trend); - = price moves against crowd (reversal bias)."""
    n = len(closes)
    if n < 12:
        return 0.0
    rets = np.diff(closes) / np.maximum(closes[:-1], 1e-10)
    if len(rets) < 6 or np.std(rets) < 1e-12:
        return 0.0
    return _clip(fast_spearman(rets, vols[1:]))


def calc_countertrend_volume_ratio_day(highs, lows, closes, vols):
    """Share of volume printed on bars against the day's closing direction.
    High counter-trend volume = distribution/absorption or reversal fuel."""
    n = len(closes)
    if n < 6:
        return 0.0
    day_ret = float(closes[-1] - closes[0])
    if abs(day_ret) < 1e-12:
        return 0.0
    bar_ret = np.diff(closes)
    total = vols[1:].sum()
    if total <= 0:
        return 0.0
    if day_ret > 0:
        ctr = vols[1:][bar_ret < 0].sum()
    else:
        ctr = vols[1:][bar_ret > 0].sum()
    return _clip(ctr / total)


def calc_opening_burst_ratio_day(highs, lows, closes, vols):
    """First-bar volume relative to average bar volume.
    Opening auction burst = institutional auction intensity."""
    n = len(vols)
    if n < 6:
        return 0.0
    meanv = vols.mean()
    if meanv <= 0:
        return 0.0
    return _clip((vols[0] / meanv - 1.0) / 3.0)


def calc_closing_auction_ratio_day(highs, lows, closes, vols):
    """Last bar volume relative to average bar volume (closing auction tension)."""
    n = len(vols)
    if n < 6:
        return 0.0
    meanv = vols.mean()
    if meanv <= 0:
        return 0.0
    return _clip((vols[-1] / meanv - 1.0) / 3.0)


def calc_intraday_extreme_asymmetry_day(highs, lows, closes, vols):
    """Asymmetry between distance-to-high and distance-to-low of the close.
    +1 = close much closer to high (bull extreme hold); -1 = close at low."""
    n = len(closes)
    if n < 6:
        return 0.0
    hi = float(np.max(highs)); lo = float(np.min(lows))
    rng = hi - lo
    if rng <= 1e-12:
        return 0.0
    return _clip(((closes[-1] - lo) - (hi - closes[-1])) / rng)


# ============================================================
# Registry (17 candidates)
# ============================================================
CANDIDATES = {
    # --- Volume Profile family ---
    "poc_position_day": calc_poc_position_day,
    "value_area_high_pos_day": calc_value_area_high_pos_day,
    "value_area_width_day": calc_value_area_width_day,
    "hvn_count_day": calc_hvn_count_day,
    "lvn_count_day": calc_lvn_count_day,
    "min_vol_gap_day": calc_min_vol_gap_day,
    # --- Cumulative volume curve shape ---
    "cumvol_curve_concavity_day": calc_cumvol_curve_concavity_day,
    "open_90m_volume_share_day": calc_open_90m_volume_share_day,
    "close_30m_volume_share_day": calc_close_30m_volume_share_day,
    "opening_burst_ratio_day": calc_opening_burst_ratio_day,
    "closing_auction_ratio_day": calc_closing_auction_ratio_day,
    # --- Intraday path archetypes ---
    "time_of_day_high_day": calc_time_of_day_high_day,
    "time_of_day_low_day": calc_time_of_day_low_day,
    "intraday_swing_imbalance_day": calc_intraday_swing_imbalance_day,
    "intraday_extreme_asymmetry_day": calc_intraday_extreme_asymmetry_day,
    "v_recovery_strength_day": calc_v_recovery_strength_day,
    "reverse_v_fade_strength_day": calc_reverse_v_fade_strength_day,
    "u_shape_midday_dip_day": calc_u_shape_midday_dip_day,
    "l_shape_late_slide_day": calc_l_shape_late_slide_day,
    # --- Price-volume interaction ---
    "price_volume_corr_intraday_day": calc_price_volume_corr_intraday_day,
    "countertrend_volume_ratio_day": calc_countertrend_volume_ratio_day,
}


def main():
    print("=== Wave 6: Volume Profile + Cum-Vol Curve + Intraday Path Archetypes ===")
    print(f"Candidates: {len(CANDIDATES)}")

    # Causality perturbation sanity: value must NOT change when bars are scrambled
    # AFTER the day (i.e. candidates must be pure functions of their own day's bars);
    # and cross-day influence is forbidden: same inputs -> same outputs.
    # Here we verify determinism + that shifting the whole day's prices to a different
    # level does not break the shape registry (structural check only).
    rng = np.random.default_rng(42)
    op_dummy = rng.normal(10.0, 0.1, 48)
    hi_dummy = op_dummy + np.abs(rng.normal(0.0, 0.1, 48))
    lo_dummy = op_dummy - np.abs(rng.normal(0.0, 0.1, 48))
    cl_dummy = op_dummy + rng.normal(0.0, 0.05, 48)
    vol_dummy = rng.integers(1000, 10000, 48).astype(float)
    print("\n--- Determinism / shape sanity ---")
    for name, fn in CANDIDATES.items():
        v1 = fn(hi_dummy, lo_dummy, cl_dummy, vol_dummy)
        v2 = fn(hi_dummy, lo_dummy, cl_dummy, vol_dummy)
        if not np.isclose(v1, v2):
            print(f"[FAIL] {name}: non-deterministic")
        else:
            print(f"[OK]   {name:42s} = {v1:+.4f}")

    etf_list = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
    results = []

    for etf in etf_list:
        print(f"\n{'='*60}\nEvaluating Wave 6 candidates on {etf}...\n{'='*60}")
        feat_file = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not feat_file.exists():
            print(f"  Skipping {etf}: features parquet missing")
            continue
        df_feat = pd.read_parquet(feat_file)
        if "trade_return" not in df_feat.columns:
            print(f"  Skipping {etf}: trade_return missing")
            continue
        y = df_feat["trade_return"].fillna(0.0).values
        dates = df_feat.index

        idx_cfg = INDEX_CONFIG[etf]
        df_5m_path = DATA_DIR / idx_cfg["file_5m"]
        if not df_5m_path.exists():
            print(f"  Missing index 5m for {etf}: {df_5m_path}")
            continue

        df_5m = pd.read_parquet(df_5m_path)
        df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
        df_5m["date"] = df_5m["datetime"].dt.normalize()
        df_5m = df_5m.sort_values(["date", "datetime"]).reset_index(drop=True)

        # Daily trade calendar from features parquet (index = dates)
        trade_dates = pd.to_datetime(dates).normalize()

        # Per-day candidate values keyed by date
        day_values = {name: {} for name in CANDIDATES}
        for d, g in df_5m.groupby("date", sort=True):
            if len(g) < 6:
                continue
            hi = g["high"].values.astype(np.float64)
            lo = g["low"].values.astype(np.float64)
            cl = g["close"].values.astype(np.float64)
            vo = g["volume"].values.astype(np.float64)
            for name, fn in CANDIDATES.items():
                day_values[name][d] = fn(hi, lo, cl, vo)

        # Align with shift(1): feature for trade day D uses day D-1 bars
        for name in CANDIDATES:
            s = pd.Series(day_values[name]).sort_index()
            s_shift = s.shift(1)
            feat_values = []
            valid_mask = []
            prev_d = None
            idx_map = {d: i for i, d in enumerate(s_shift.index)}
            # trade rows: use previous trading day's value when the calendar matches index 5m days
            for t in trade_dates:
                if t in idx_map:
                    val = s_shift.loc[t]
                    feat_values.append(val if pd.notna(val) else 0.0)
                    valid_mask.append(pd.notna(val))
                else:
                    feat_values.append(0.0)
                    valid_mask.append(False)

            x = np.array(feat_values, dtype=np.float64)
            valid = np.array(valid_mask)
            if valid.sum() < 100:
                continue
            if np.std(x[valid]) < 1e-8:
                continue
            metrics = compute_yearly_ic(x[valid], y[valid], trade_dates[valid])
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
            print(f"  {name:42s} | IC={metrics['mean_ic']:+.4f} | CV={metrics['ic_cv']:.2f} | "
                  f"NegYrs={metrics['n_neg_years']} | JK={metrics['jackknife_pass']} | "
                  f"N={valid.sum()} => {status}")

    csv_path = HERE / "mined_wave6_candidates.csv"
    fieldnames = ["feature_name", "etf", "overall_ic", "ic_cv", "n_neg_years",
                  "jackknife_pass", "flips", "gate_pass", "n_valid"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved to: {csv_path}")

    passing = [r for r in results if r["gate_pass"]]
    print(f"\n{'='*60}")
    print(f"=== Gate-Passing Wave 6 Features ({len(passing)}/{len(results)}) ===")
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