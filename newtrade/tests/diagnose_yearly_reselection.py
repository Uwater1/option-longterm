#!/usr/bin/env python3
"""
Deep diagnostic: WHY does yearly reselection underperform in newtrade?

Hypotheses:
  H1: Period pools have low overlap with static → signal discontinuity at year boundaries
  H2: Dynamic top-10 IC already adapts within the static pool → pool switching adds noise
  H3: Per-year threshold sweeps produce inconsistent thresholds → unstable trading
  H4: Period pools are better in day-model-new (EW) but worse with ICW+topK interaction
  H5: The expanding IC warm-up is polluted when pool changes (features unseen in early history)

Diagnostics:
  1. Feature overlap matrix (static vs each period pool)
  2. Per-year raw signal IC (before thresholding) for both groups
  3. Threshold comparison per year
  4. Top-10 feature selection stability within each pool
  5. EW vs ICW+TopK comparison on both pools (isolates weighting effect)
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, expanding_factor_ic_numba
)
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot, sweep_optimal_threshold, compute_production_threshold

DAY_MODEL_DATA = REPO_ROOT / "day-model-new" / "data"

YEAR_TO_POOL_SUFFIX = {
    2022: "",
    2023: "_p2015_2023",
    2024: "_p2016_2024",
    2025: "_p2017_2025",
}


def load_period_pool(etf: str, year: int) -> list:
    suffix = YEAR_TO_POOL_SUFFIX.get(year, "_p2017_2025")
    fpath = DAY_MODEL_DATA / f"selected_pool_{etf}_single{suffix}.json"
    if not fpath.exists():
        return []
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_signal_ic(Z_composite, trade_returns, dates, year):
    """Compute realized rank IC of composite signal for a specific year."""
    mask = dates.dt.year == year
    if mask.sum() < 20:
        return np.nan
    z_y = Z_composite[mask.values]
    r_y = trade_returns[mask.values]
    valid = ~(np.isnan(z_y) | np.isnan(r_y))
    if valid.sum() < 20:
        return np.nan
    return float(np.corrcoef(z_y[valid], r_y[valid])[0, 1])


def diagnose_etf(etf: str):
    print(f"\n{'═' * 90}")
    print(f"  DIAGNOSTIC: {etf}")
    print(f"{'═' * 90}")

    df = load_etf_dataset(etf)
    full_trade_ret = df["trade_return"].values.astype(np.float64)
    dates = df["date"]
    fee_bps = 0.0008

    static_pool = load_admitted_pool(etf, side="single", min_features=5)
    if not static_pool:
        print("  [SKIP] No static pool")
        return

    # ─── D1: Feature Overlap ───
    print(f"\n  ┌─── D1: Feature Overlap (Static={len(static_pool)} features) ───")
    static_names = set(p["feature_name"] for p in static_pool)
    for y in [2022, 2023, 2024, 2025]:
        pool_y = load_period_pool(etf, y)
        if not pool_y:
            print(f"  │  {y}: NO POOL")
            continue
        names_y = set(p["feature_name"] for p in pool_y)
        overlap = static_names & names_y
        only_static = static_names - names_y
        only_yearly = names_y - static_names
        print(f"  │  {y} (N={len(pool_y)}): overlap={len(overlap)}/{len(static_names)} "
              f"| only_static={len(only_static)} | only_yearly={len(only_yearly)}")
        if len(only_static) <= 5:
            for n in sorted(only_static):
                print(f"  │    static-only: {n[:70]}")
        if len(only_yearly) <= 5:
            for n in sorted(only_yearly):
                print(f"  │    yearly-only: {n[:70]}")

    # ─── D2: Raw Signal IC per year (no thresholding) ───
    print(f"\n  ┌─── D2: Raw Composite Signal IC per Year ───")
    print(f"  │  {'Year':<6} | {'Static EW':>10} {'Static ICW+TopK':>16} | {'Yearly EW':>10} {'Yearly ICW+TopK':>16}")
    print(f"  │  {'-'*6}-+-{'-'*28}-+-{'-'*28}")

    # Static pool signals
    X_s, signs_s, _ = build_pool_feature_matrix(df, static_pool)
    Z_s = expanding_zscore_numba(X_s, burn_in=252, clip=3.0)
    IC_s = expanding_factor_ic_numba(Z_s, signs_s, full_trade_ret, burn_in=252)
    N_s = len(static_pool)

    # EW composite (static)
    Z_ew_s = np.mean(Z_s * signs_s, axis=1)
    # ICW+TopK composite (static)
    icw_func = get_weighting_scheme("icw")
    n_train = int((dates < pd.Timestamp("2022-01-01")).sum())
    Z_icw_s = icw_func(Z_s, signs_s, pool=static_pool, n_train=n_train,
                       expanding_ic=IC_s, top_k=min(10, N_s - 1) if N_s > 10 else None,
                       ic_ema_span=30, dynamic_metric="ic")

    for y in [2022, 2023, 2024, 2025]:
        ic_ew_s = compute_signal_ic(Z_ew_s, full_trade_ret, dates, y)
        ic_icw_s = compute_signal_ic(Z_icw_s, full_trade_ret, dates, y)

        # Yearly pool
        pool_y = load_period_pool(etf, y)
        if pool_y and len(pool_y) >= 5:
            X_y, signs_y, _ = build_pool_feature_matrix(df, pool_y)
            Z_y = expanding_zscore_numba(X_y, burn_in=252, clip=3.0)
            IC_y = expanding_factor_ic_numba(Z_y, signs_y, full_trade_ret, burn_in=252)
            N_y = len(pool_y)
            Z_ew_y = np.mean(Z_y * signs_y, axis=1)
            topk_y = min(10, N_y - 1) if N_y > 10 else None
            Z_icw_y = icw_func(Z_y, signs_y, pool=pool_y, n_train=n_train,
                               expanding_ic=IC_y, top_k=topk_y, ic_ema_span=30, dynamic_metric="ic")
            ic_ew_y = compute_signal_ic(Z_ew_y, full_trade_ret, dates, y)
            ic_icw_y = compute_signal_ic(Z_icw_y, full_trade_ret, dates, y)
            topk_note = f"(topK={'OFF' if topk_y is None else topk_y})"
        else:
            ic_ew_y = ic_icw_y = np.nan
            topk_note = "(no pool)"

        print(f"  │  {y:<6} | {ic_ew_s:>10.4f} {ic_icw_s:>16.4f} | {ic_ew_y:>10.4f} {ic_icw_y:>16.4f} {topk_note}")

    # ─── D3: Threshold Comparison ───
    print(f"\n  ┌─── D3: Auto-Threshold Sweep per Year ───")
    print(f"  │  {'Year':<6} | {'Static z_th':>12} {'Sharpe':>8} | {'Yearly z_th':>12} {'Sharpe':>8}")
    print(f"  │  {'-'*6}-+-{'-'*22}-+-{'-'*22}")

    for y in [2022, 2023, 2024, 2025]:
        t_start = pd.Timestamp(f"{y}-01-01")
        train_mask = dates < t_start

        # Static
        Z_train_s = Z_icw_s[train_mask.values]
        ret_train = full_trade_ret[train_mask.values]
        sweep_s = sweep_optimal_threshold(Z_train_s, ret_train, mode="binary", fee_bps=fee_bps, long_only=False)
        z_th_s, z_th_short_s = compute_production_threshold(sweep_s, z_buffer=0.1)

        # Yearly
        pool_y = load_period_pool(etf, y)
        if pool_y and len(pool_y) >= 5:
            X_y, signs_y, _ = build_pool_feature_matrix(df, pool_y)
            Z_y = expanding_zscore_numba(X_y, burn_in=252, clip=3.0)
            IC_y = expanding_factor_ic_numba(Z_y, signs_y, full_trade_ret, burn_in=252)
            N_y = len(pool_y)
            topk_y = min(10, N_y - 1) if N_y > 10 else None
            Z_icw_y_full = icw_func(Z_y, signs_y, pool=pool_y, n_train=int(train_mask.sum()),
                                    expanding_ic=IC_y, top_k=topk_y, ic_ema_span=30, dynamic_metric="ic")
            Z_train_y = Z_icw_y_full[train_mask.values]
            sweep_y = sweep_optimal_threshold(Z_train_y, ret_train, mode="binary", fee_bps=fee_bps, long_only=False)
            z_th_y, _ = compute_production_threshold(sweep_y, z_buffer=0.1)
            print(f"  │  {y:<6} | {z_th_s:>12.3f} {sweep_s['best_sharpe']:>8.3f} | {z_th_y:>12.3f} {sweep_y['best_sharpe']:>8.3f}")
        else:
            print(f"  │  {y:<6} | {z_th_s:>12.3f} {sweep_s['best_sharpe']:>8.3f} | {'N/A':>12} {'N/A':>8}")

    # ─── D4: Top-10 Feature Selection Stability ───
    print(f"\n  ┌─── D4: Dynamic Top-10 Feature Stability (Static Pool) ───")
    if N_s > 10:
        # EMA-smoothed IC
        alpha = 2.0 / 31.0
        ic_ema = np.zeros_like(IC_s)
        ic_ema[0] = IC_s[0]
        for t in range(1, len(IC_s)):
            ic_ema[t] = alpha * IC_s[t] + (1 - alpha) * ic_ema[t - 1]

        # Check which features are in top-10 at start of each year
        feat_names_s = [p["feature_name"] for p in static_pool]
        for y in [2022, 2023, 2024, 2025]:
            yr_mask = dates.dt.year == y
            yr_indices = np.where(yr_mask.values)[0]
            if len(yr_indices) == 0:
                continue
            # Average top-10 selection frequency within this year
            selection_count = np.zeros(N_s)
            for t in yr_indices:
                top_idx = np.argsort(ic_ema[t])[-10:]
                selection_count[top_idx] += 1
            freq = selection_count / len(yr_indices)
            top_features = np.argsort(-freq)[:10]
            print(f"  │  {y} top-10 (freq%): ", end="")
            for i in top_features[:5]:
                print(f"{feat_names_s[i][:35]}={freq[i]*100:.0f}%", end="  ")
            print()
    else:
        print(f"  │  Pool has {N_s} features (≤10), top-K not active")

    # ─── D5: EW vs ICW+TopK isolation ───
    print(f"\n  ┌─── D5: Weighting Scheme Isolation (Full Period Sharpe) ───")
    print(f"  │  Tests: is the problem the POOL or the WEIGHTING?")

    # Run 4 combinations: {static, yearly} × {EW, ICW+TopK}
    # For "yearly" we stitch per-year
    t_start = pd.Timestamp("2022-01-01")
    t_end = pd.Timestamp("2026-01-01")
    oos_mask = (dates >= t_start) & (dates < t_end)

    # Static EW
    pos_ew_s = generate_positions(Z_ew_s, z_th=0.8, z_th_short=0.8, mode="binary", long_only=False)
    ret_ew_s, _, _ = simulate_etf_spot(full_trade_ret[oos_mask.values], pos_ew_s[oos_mask.values], fee_bps=fee_bps)
    sr_ew_s = np.mean(ret_ew_s) / np.std(ret_ew_s) * np.sqrt(252) if np.std(ret_ew_s) > 1e-12 else 0

    # Static ICW+TopK (auto threshold)
    train_mask = dates < t_start
    sweep_s = sweep_optimal_threshold(Z_icw_s[train_mask.values], full_trade_ret[train_mask.values], mode="binary", fee_bps=fee_bps, long_only=False)
    z_th_s, z_th_short_s = compute_production_threshold(sweep_s, z_buffer=0.1)
    pos_icw_s = generate_positions(Z_icw_s, z_th=z_th_s, z_th_short=z_th_short_s, mode="binary", long_only=False)
    ret_icw_s, _, _ = simulate_etf_spot(full_trade_ret[oos_mask.values], pos_icw_s[oos_mask.values], fee_bps=fee_bps)
    sr_icw_s = np.mean(ret_icw_s) / np.std(ret_icw_s) * np.sqrt(252) if np.std(ret_icw_s) > 1e-12 else 0

    # Yearly EW (stitched)
    yearly_ew_rets = []
    yearly_icw_rets = []
    for y in [2022, 2023, 2024, 2025]:
        pool_y = load_period_pool(etf, y)
        if not pool_y or len(pool_y) < 5:
            continue
        X_y, signs_y, _ = build_pool_feature_matrix(df, pool_y)
        Z_y = expanding_zscore_numba(X_y, burn_in=252, clip=3.0)
        IC_y = expanding_factor_ic_numba(Z_y, signs_y, full_trade_ret, burn_in=252)
        N_y = len(pool_y)
        Z_ew_y = np.mean(Z_y * signs_y, axis=1)
        topk_y = min(10, N_y - 1) if N_y > 10 else None
        Z_icw_y = icw_func(Z_y, signs_y, pool=pool_y, n_train=int((dates < pd.Timestamp(f'{y}-01-01')).sum()),
                           expanding_ic=IC_y, top_k=topk_y, ic_ema_span=30, dynamic_metric="ic")

        yr_mask = (dates >= f"{y}-01-01") & (dates < f"{y+1}-01-01")
        if not yr_mask.any():
            continue

        # EW with fixed threshold
        pos_ew_y = generate_positions(Z_ew_y, z_th=0.8, z_th_short=0.8, mode="binary", long_only=False)
        r_ew_y, _, _ = simulate_etf_spot(full_trade_ret[yr_mask.values], pos_ew_y[yr_mask.values], fee_bps=fee_bps)
        yearly_ew_rets.append(r_ew_y)

        # ICW+TopK with auto threshold
        train_m = dates < pd.Timestamp(f"{y}-01-01")
        sw_y = sweep_optimal_threshold(Z_icw_y[train_m.values], full_trade_ret[train_m.values], mode="binary", fee_bps=fee_bps, long_only=False)
        z_y, zs_y = compute_production_threshold(sw_y, z_buffer=0.1)
        pos_icw_y = generate_positions(Z_icw_y, z_th=z_y, z_th_short=zs_y, mode="binary", long_only=False)
        r_icw_y, _, _ = simulate_etf_spot(full_trade_ret[yr_mask.values], pos_icw_y[yr_mask.values], fee_bps=fee_bps)
        yearly_icw_rets.append(r_icw_y)

    if yearly_ew_rets:
        all_ew_y = np.concatenate(yearly_ew_rets)
        sr_ew_y = np.mean(all_ew_y) / np.std(all_ew_y) * np.sqrt(252) if np.std(all_ew_y) > 1e-12 else 0
    else:
        sr_ew_y = 0
    if yearly_icw_rets:
        all_icw_y = np.concatenate(yearly_icw_rets)
        sr_icw_y = np.mean(all_icw_y) / np.std(all_icw_y) * np.sqrt(252) if np.std(all_icw_y) > 1e-12 else 0
    else:
        sr_icw_y = 0

    print(f"  │")
    print(f"  │  {'':20} | {'EW (fixed z=0.8)':>18} | {'ICW+TopK (auto z)':>18}")
    print(f"  │  {'-'*20}-+-{'-'*18}-+-{'-'*18}")
    print(f"  │  {'Static Pool':<20} | {sr_ew_s:>18.3f} | {sr_icw_s:>18.3f}")
    print(f"  │  {'Yearly Pool':<20} | {sr_ew_y:>18.3f} | {sr_icw_y:>18.3f}")
    print(f"  │")
    print(f"  │  Interpretation:")
    if sr_ew_y > sr_ew_s and sr_icw_y < sr_icw_s:
        print(f"  │    → Yearly pool has BETTER raw signal (EW) but WORSE after ICW+TopK")
        print(f"  │    → Problem: ICW+TopK interaction with changing pools")
    elif sr_ew_y > sr_ew_s and sr_icw_y > sr_icw_s:
        print(f"  │    → Yearly pool wins in BOTH → original A/B test had implementation bug")
    elif sr_ew_y < sr_ew_s and sr_icw_y < sr_icw_s:
        print(f"  │    → Yearly pool is genuinely worse in both weighting schemes")
        print(f"  │    → Problem: pool quality, not weighting interaction")
    elif sr_ew_y < sr_ew_s and sr_icw_y > sr_icw_s:
        print(f"  │    → Yearly pool worse raw but better with ICW+TopK (unexpected)")
    print(f"  └───")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all")
    args = parser.parse_args()

    etfs = ["300ETF", "500ETF", "159915ETF"] if args.etf == "all" else [args.etf]
    for etf in etfs:
        diagnose_etf(etf)


if __name__ == "__main__":
    main()
