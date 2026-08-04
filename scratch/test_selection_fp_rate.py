#!/usr/bin/env python3
"""
Test script to evaluate the User's Premise / Proposal:
"current top-10 selection system (EMA smoothed rolling 480d tail IC system with Sortino gate)
Cannot distinguish between TF (TP) and FP factor, so If FP rate are 10% and median rate 30%,
I should Expect same rate within the system. Agree or Disagree."

This script tracks daily feature selection by the production Top-10 system across all
diagnosis periods (p2015_2023, p2016_2024, p2017_2025, p2018_2026) and ETFs.

It measures:
1. Pool Base Rates (TP%, Median%, FP%)
2. Active Selected Top-10 Rates (TP%, Median%, FP%)
3. Selection Bias / Distinguishability Ratio: (Selected FP Rate) / (Pool FP Rate)
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "newtrade"))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, rolling_tail_ic_numba, rolling_factor_risk_numba,
                   load_cluster_assignments)
from weighting import compute_icw_hysteresis, adaptive_exit_rank
from run_backtest import resolve_ic_ema_span

PERIODS = [
    ("p2015_2023", "2024-01-01", "2025-01-01"),
    ("p2016_2024", "2025-01-01", "2026-01-01"),
    ("p2017_2025", "2025-01-01", "2026-06-01"),
    ("p2018_2026", "2025-01-01", "2026-06-01"),
]

ETFS = ["300ETF", "500ETF", "159915ETF"]


def load_diagnosis_classification(period_suffix: str, etf: str):
    """Load TP, Median, FP lists from day-model-new/data/filter_diagnosis_{suffix}.json"""
    json_path = REPO_ROOT / "day-model-new" / "data" / f"filter_diagnosis_{period_suffix}.json"
    if not json_path.exists():
        return None
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    etf_diag = data.get(etf, {}).get("single", {})
    if not etf_diag:
        return None
    
    tp_names = {f["feature_name"] for f in etf_diag.get("tp_features", [])}
    median_names = {f["feature_name"] for f in etf_diag.get("median_features", [])}
    fp_names = {f["feature_name"] for f in etf_diag.get("fp_features", [])}
    
    return tp_names, median_names, fp_names


def run_experiment_for_period(period_name, start_date, end_date, etf, sortino_gate=True):
    suffix = f"_{period_name}"
    diag = load_diagnosis_classification(period_name, etf)
    if diag is None:
        return None
    tp_names, median_names, fp_names = diag

    pool = load_admitted_pool(etf, side="single", min_features=5, suffix=suffix)
    if not pool:
        return None

    df = load_etf_dataset(etf)
    trade_ret = (df["trade_return"].values.astype(np.float64)
                 if "trade_return" in df.columns
                 else df["close"].pct_change().fillna(0.0).values)

    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    N = len(feat_names)

    # Classify each index in pool
    feat_class = []
    for fn in feat_names:
        if fn in tp_names:
            feat_class.append("TP")
        elif fn in fp_names:
            feat_class.append("FP")
        elif fn in median_names:
            feat_class.append("Median")
        else:
            # Fallback if label unassigned
            feat_class.append("Median")
    feat_class = np.array(feat_class)

    n_pool_tp = (feat_class == "TP").sum()
    n_pool_med = (feat_class == "Median").sum()
    n_pool_fp = (feat_class == "FP").sum()
    n_total = N

    pool_tp_rate = n_pool_tp / n_total
    pool_med_rate = n_pool_med / n_total
    pool_fp_rate = n_pool_fp / n_total

    # Load cluster assignments
    cluster_dict = load_cluster_assignments(etf, side="single", suffix=suffix)
    if cluster_dict:
        cluster_ids = np.array([cluster_dict.get(fn, i) for i, fn in enumerate(feat_names)])
    else:
        cluster_ids = None

    # Compute rolling 480d tail IC and Sortino
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    raw_ic = rolling_tail_ic_numba(Z_std, signs, trade_ret, window=480, tail_pct=0.10)

    T = len(Z_std)
    ic_ema_span = resolve_ic_ema_span(etf, None)
    if ic_ema_span > 1:
        alpha_e = 2.0 / (ic_ema_span + 1.0)
        ic_smoothed = np.zeros_like(raw_ic)
        ic_smoothed[0] = raw_ic[0]
        for t_i in range(1, T):
            ic_smoothed[t_i] = alpha_e * raw_ic[t_i] + (1.0 - alpha_e) * ic_smoothed[t_i - 1]
    else:
        ic_smoothed = raw_ic.copy()

    if sortino_gate:
        _, rolling_sortino = rolling_factor_risk_numba(Z_std, signs, trade_ret, window=480, burn_in=252)
        ic_smoothed = np.where(rolling_sortino <= 0.0, -10.0, ic_smoothed)

    # Filter dates for OOS test period
    dates = pd.to_datetime(df["date"])
    dt_start = pd.to_datetime(start_date)
    dt_end = pd.to_datetime(end_date)

    test_mask = (dates >= dt_start) & (dates < dt_end)
    test_indices = np.where(test_mask)[0]

    if len(test_indices) == 0:
        # Fallback to last 250 trading days
        test_indices = np.arange(max(0, T - 252), T)

    # Track active set each day
    exit_rank = 25
    top_k = 10
    active_set = set()

    daily_tp_cnt = 0
    daily_med_cnt = 0
    daily_fp_cnt = 0
    daily_total_cnt = 0

    for t in range(T):
        scores = ic_smoothed[t]
        order = np.argsort(scores)[::-1]
        rank_of = np.zeros(N, dtype=np.int64)
        for rank_pos, idx in enumerate(order):
            rank_of[idx] = rank_pos + 1

        # 1. Exit
        to_remove = [f for f in active_set if rank_of[f] > exit_rank]
        for f in to_remove:
            active_set.discard(f)

        # 2. Enter
        occupied_clusters = {}
        if cluster_ids is not None:
            for f in active_set:
                occupied_clusters[int(cluster_ids[f])] = f

        for idx in order:
            if rank_of[idx] > top_k:
                break
            if idx in active_set:
                continue
            if cluster_ids is not None:
                cid = int(cluster_ids[idx])
                if cid in occupied_clusters:
                    continue
                occupied_clusters[cid] = idx
            active_set.add(idx)

        # Record statistics if in test window
        if t in test_indices and len(active_set) > 0:
            active_arr = np.array(list(active_set))
            active_classes = feat_class[active_arr]
            n_tp = (active_classes == "TP").sum()
            n_med = (active_classes == "Median").sum()
            n_fp = (active_classes == "FP").sum()

            daily_tp_cnt += n_tp
            daily_med_cnt += n_med
            daily_fp_cnt += n_fp
            daily_total_cnt += len(active_set)

    sel_tp_rate = daily_tp_cnt / daily_total_cnt if daily_total_cnt > 0 else 0.0
    sel_med_rate = daily_med_cnt / daily_total_cnt if daily_total_cnt > 0 else 0.0
    sel_fp_rate = daily_fp_cnt / daily_total_cnt if daily_total_cnt > 0 else 0.0

    return {
        "period": period_name,
        "etf": etf,
        "sortino_gate": sortino_gate,
        "n_pool": n_total,
        "pool_tp_pct": pool_tp_rate * 100,
        "pool_med_pct": pool_med_rate * 100,
        "pool_fp_pct": pool_fp_rate * 100,
        "sel_tp_pct": sel_tp_rate * 100,
        "sel_med_pct": sel_med_rate * 100,
        "sel_fp_pct": sel_fp_rate * 100,
        "fp_bias_ratio": (sel_fp_rate / pool_fp_rate) if pool_fp_rate > 1e-6 else 0.0,
        "tp_bias_ratio": (sel_tp_rate / pool_tp_rate) if pool_tp_rate > 1e-6 else 0.0,
    }


def main():
    print("=" * 120)
    print("EMPIRICAL TEST OF USER PREMISE: Does Top-10 Selection system distinguish TP vs FP factors?")
    print("=" * 120)

    results = []

    for period, st, en in PERIODS:
        for etf in ETFS:
            res_gated = run_experiment_for_period(period, st, en, etf, sortino_gate=True)
            res_ungated = run_experiment_for_period(period, st, en, etf, sortino_gate=False)

            if res_gated:
                results.append(res_gated)
            if res_ungated:
                results.append(res_ungated)

    res_df = pd.DataFrame(results)
    print("\n--- DETAILED PERIOD-BY-PERIOD RESULTS (Gated vs Ungated) ---\n")
    print(res_df.to_string(index=False))

    # Calculate overall averages
    print("\n" + "=" * 120)
    print("SUMMARY COMPARISON ACROSS ALL PERIODS & ETFS:")
    print("=" * 120)

    gated_df = res_df[res_df["sortino_gate"] == True]
    ungated_df = res_df[res_df["sortino_gate"] == False]

    print(f"\n[GATED PRODUCTION SYSTEM (EMA 480d Tail IC + Sortino<=0 Gate)]")
    print(f"  Mean Pool FP Rate    : {gated_df['pool_fp_pct'].mean():.2f}%")
    print(f"  Mean Selected FP Rate: {gated_df['sel_fp_pct'].mean():.2f}%")
    print(f"  FP Selection Ratio   : {gated_df['fp_bias_ratio'].mean():.3f}x  (< 1.0x means FP rate is REDUCED)")
    print(f"  Mean Pool TP Rate    : {gated_df['pool_tp_pct'].mean():.2f}%")
    print(f"  Mean Selected TP Rate: {gated_df['sel_tp_pct'].mean():.2f}%")
    print(f"  TP Selection Ratio   : {gated_df['tp_bias_ratio'].mean():.3f}x  (> 1.0x means TP rate is ENHANCED)")

    print(f"\n[UNGATED BASELINE SYSTEM (EMA 480d Tail IC only)]")
    print(f"  Mean Pool FP Rate    : {ungated_df['pool_fp_pct'].mean():.2f}%")
    print(f"  Mean Selected FP Rate: {ungated_df['sel_fp_pct'].mean():.2f}%")
    print(f"  FP Selection Ratio   : {ungated_df['fp_bias_ratio'].mean():.3f}x")
    print(f"  Mean Pool TP Rate    : {ungated_df['pool_tp_pct'].mean():.2f}%")
    print(f"  Mean Selected TP Rate: {ungated_df['sel_tp_pct'].mean():.2f}%")
    print(f"  TP Selection Ratio   : {ungated_df['tp_bias_ratio'].mean():.3f}x")


if __name__ == "__main__":
    main()
