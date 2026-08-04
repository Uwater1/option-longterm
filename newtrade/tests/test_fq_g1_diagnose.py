#!/usr/bin/env python3
"""
G1 Diagnosis — why did the tailIC>0 gate hurt, and does baseline selection
actually hold factors with negative tail IC?

Part 1: replicate the production selection (EMA tail IC, hysteresis ER=25,
        cluster cap 1, top-10) and measure how often the active set contains
        factors with smoothed IC <= 0, and how often raw tailIC touches <= 0
        (which, under the previous -1e9 pre-EMA mask, triggered a ~span*ln(1e9)
        day EMA kill-switch — an implementation artifact).

Part 2: CLEAN gate A/B — mask applied AFTER EMA smoothing (value -10, bounded),
        pre-smoothed matrix injected with ic_ema_span=1 (no double smoothing).
        Arms: Baseline, G1c (tailIC<=0), G2c (+Sortino<=0), G4c (+loo<=0).

Usage:
    python newtrade/tests/test_fq_g1_diagnose.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from run_backtest import run_single_backtest, resolve_ic_ema_span
from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, rolling_tail_ic_numba,
                   load_cluster_assignments)
from factor_quality import compute_fq_components, rolling_daily_ic_matrix, \
    rolling_block_stats_numba, WINDOW

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
TAIL_WINDOW = 480
OOS_START = "2022-01-01"
REPORT_BASELINE_ER25 = {"300ETF": 0.204, "500ETF": 1.039, "159915ETF": 0.930}
MASK_VAL = -10.0


def run_pre_smoothed(etf, exp_mat, start_date, end_date):
    """ICW backtest with PRE-SMOOTHED matrix injected, no re-smoothing (span=1)."""
    return run_single_backtest(
        etf=etf, side="single", scheme_name="icw", z_th=0.5,
        position_mode="fast_ramp_quadratic", fee_bps=8.0 / 10000.0,
        start_date=start_date, end_date=end_date,
        z_buffer=0.1, auto_threshold=True, dynamic_ic=True,
        rank_kwargs={"top_k": 10, "ic_ema_span": 1, "dynamic_metric": "ic"},
        ic_mode="rolling_tail", tail_window=TAIL_WINDOW, tail_pct=0.10,
        use_stoploss=True, stoploss_mode="time_decay_trailing", stoploss_param=0.03,
        hysteresis=True, exit_rank=25, min_pos=0.7, delta_z_full=0.4,
        ic_override=exp_mat,
    )


def replicate_selection(smoothed, cluster_ids, top_k=10, exit_rank=25):
    """Replicate compute_icw_hysteresis selection; return list of active sets."""
    T, N = smoothed.shape
    active = set()
    history = []
    for t in range(T):
        scores = smoothed[t]
        order = np.argsort(scores)[::-1]
        rank_of = np.zeros(N, dtype=np.int64)
        for rp, idx in enumerate(order):
            rank_of[idx] = rp + 1
        for f in [f for f in active if rank_of[f] > exit_rank]:
            active.discard(f)
        occupied = {}
        if cluster_ids is not None:
            for f in active:
                occupied[int(cluster_ids[f])] = f
        for idx in order:
            if len(active) >= top_k:
                break
            i = int(idx)
            if i in active:
                continue
            if rank_of[i] > top_k:
                break
            if cluster_ids is not None:
                c = int(cluster_ids[i])
                if c in occupied:
                    continue
                occupied[c] = i
            active.add(i)
        history.append(set(active))
    return history


def main():
    print("=" * 100)
    print("G1 DIAGNOSIS — negative-IC selection frequency + clean post-EMA gate A/B")
    print("=" * 100)

    results = []
    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue
        df = load_etf_dataset(etf)
        trade_ret = (df["trade_return"].values.astype(np.float64)
                     if "trade_return" in df.columns
                     else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        # tail IC + production EMA smoothing (identical to run_backtest)
        tail = rolling_tail_ic_numba(Z_std, signs, trade_ret, window=TAIL_WINDOW,
                                     tail_pct=0.10, burn_in=burn_in)
        span = resolve_ic_ema_span(etf, None)
        alpha = 2.0 / (span + 1.0)
        smoothed = np.zeros_like(tail)
        smoothed[0] = tail[0]
        for t in range(1, len(df)):
            smoothed[t] = alpha * tail[t] + (1 - alpha) * smoothed[t - 1]

        # cluster ids (same logic as run_backtest)
        feat_to_cluster = load_cluster_assignments(etf, "single", suffix="")
        cluster_ids = None
        if feat_to_cluster is not None:
            nxt = (max(feat_to_cluster.values()) + 1) if feat_to_cluster else 1000
            cids = []
            for fn in feat_names:
                if fn in feat_to_cluster:
                    cids.append(feat_to_cluster[fn])
                else:
                    cids.append(nxt); nxt += 1
            cluster_ids = np.array(cids, dtype=np.int64)

        dates = df["date"]
        oos = dates >= pd.Timestamp(OOS_START)
        oos_idx = np.where(oos)[0]
        t_start_ts = pd.Timestamp(OOS_START)
        n_train = int((dates < t_start_ts).sum())
        se_ic = 1.0 / np.sqrt(n_train)

        # ── Part 1: baseline selection diagnostics ─────────────────────────────
        hist = replicate_selection(smoothed, cluster_ids)
        n_neg_days, n_zw_days, short_days = 0, 0, 0
        neg_counts = []
        for t in oos_idx:
            act = np.array(sorted(hist[t]), dtype=int)
            if len(act) < 10:
                short_days += 1
            if len(act) == 0:
                neg_counts.append(0)
                continue
            sc = smoothed[t, act]
            n_neg = int((sc <= 0).sum())
            n_zw = int((sc <= se_ic).sum())   # selected but zero ICW weight
            neg_counts.append(n_neg)
            n_neg_days += 1 if n_neg > 0 else 0
            n_zw_days += 1 if n_zw > 0 else 0
        n_days = len(oos_idx)
        # raw tailIC <= 0 frequency (kill-switch trigger rate under old mask)
        valid = np.arange(480, len(df))
        touch_frac = float((tail[valid] <= 0).any(axis=0).mean())
        day_frac = float((tail[valid] <= 0).mean())

        print(f"\n[{etf}] N={len(pool)}, EMA span={span}, se_ic={se_ic:.4f}, OOS days={n_days}")
        print(f"  PART 1 — baseline selection composition (OOS 2022-2026):")
        print(f"    days with <10 active factors        : {short_days}/{n_days} ({short_days/n_days:.1%})")
        print(f"    days with >=1 active EMA-IC <= 0    : {n_neg_days}/{n_days} ({n_neg_days/n_days:.1%})")
        print(f"    days with >=1 zero-weight selection : {n_zw_days}/{n_days} ({n_zw_days/n_days:.1%})  (IC <= se)")
        print(f"    avg neg-IC factors in active set    : {np.mean(neg_counts):.3f}")
        print(f"  raw tailIC <= 0: {day_frac:.2%} of factor-days; {touch_frac:.0%} of factors ever touch <=0")

        # ── Part 2: clean post-EMA gate A/B ────────────────────────────────────
        comps = compute_fq_components(Z_std, signs, trade_ret, window=WINDOW, burn_in=burn_in)
        daily_ic = rolling_daily_ic_matrix(Z_std, signs, trade_ret)
        _, loo_min = rolling_block_stats_numba(daily_ic, window=WINDOW, n_blocks=4, burn_in=burn_in)

        masks = {
            "Baseline": None,
            "G1c_tail<=0": tail <= 0,
            "G2c_sort<=0": (tail <= 0) | (comps["sortino"] <= 0),
            "G4c_sort_loo": (tail <= 0) | (comps["sortino"] <= 0) | (loo_min <= 0),
        }
        print(f"  PART 2 — clean post-EMA gate A/B (mask={MASK_VAL}, applied after smoothing):")
        for arm, m in masks.items():
            ov = smoothed if m is None else np.where(m, MASK_VAL, smoothed)
            res = run_pre_smoothed(etf, ov, OOS_START, "2026-01-01")
            if res.get("status") != "SUCCESS":
                print(f"    [{arm:<13}] SKIPPED")
                continue
            results.append({"Arm": arm, "ETF": etf, "CostSharpe": res["cost_sharpe"],
                            "TotalPnL": res["total_pnl"], "Trades": res["n_trades"]})
            if arm == "Baseline":
                exp = REPORT_BASELINE_ER25[etf]
                d = res["cost_sharpe"] - exp
                flag = "OK" if abs(d) < 0.005 else "MISMATCH!"
                print(f"    [{arm:<13}] Sharpe={res['cost_sharpe']:.3f} (report={exp:.3f}, Δ={d:+.4f}) [{flag}]")
            else:
                print(f"    [{arm:<13}] Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}")

    df_res = pd.DataFrame(results)
    pv = df_res.pivot_table(index="Arm", columns="ETF", values="CostSharpe", aggfunc="first")
    pv["Avg"] = pv.mean(axis=1)
    etf_cols = [c for c in pv.columns if c != "Avg"]
    base = pv.loc["Baseline", etf_cols]
    pv["ΔBase"] = pv["Avg"] - pv.loc["Baseline", "Avg"]
    print("\n" + "=" * 100)
    print("CLEAN GATE A/B RESULTS (post-EMA mask)")
    print("=" * 100)
    print(pv.round(3).to_string())
    for arm, row in pv.iterrows():
        if arm == "Baseline":
            continue
        deltas = row[etf_cols] - base
        dstr = "  ".join(f"{e}:{d:+.3f}" for e, d in deltas.items())
        print(f"  {arm:<13} ΔAvg={row['ΔBase']:+.3f}  [{dstr}]")
    df_res.to_csv(HERE / "fq_g1_diagnose_results.csv", index=False)
    print(f"\nSaved to {HERE / 'fq_g1_diagnose_results.csv'}")


if __name__ == "__main__":
    main()
