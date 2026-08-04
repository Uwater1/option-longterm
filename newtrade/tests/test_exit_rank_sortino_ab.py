#!/usr/bin/env python3
"""
A/B Test: exit_rank (hysteresis band) tuning × Sortino Score IC

Questions:
  1. Was changing exit_rank 25 -> 20 a mistake? Sweep ER on the CURRENT pipeline.
  2. Should ER adapt to pool size / cluster count instead of being fixed?
  3. Does the Sortino-480d Score IC blend prefer a different ER than pure tail IC?
  4. Component decomposition: does Sortino help more as the SELECTION metric
     (top-10 + hysteresis) or as the WEIGHTING metric (ICW shrinkage weights)?

Groups (all arms keep the REPORT.md pipeline otherwise identical):
  A — TailIC baseline × ER variants:
      ER ∈ {15, 17, 20*, 23, 25, poolAdapt, clustAdapt}   (* = REPORT.md config)
      poolAdapt  = min(10 + (N-10)//2, 25)
      clustAdapt = min(10 + max(5, n_clusters//2), 25)
  B — Sortino4_6 blend (w_ic=0.4) × same ER variants
  C — Selection/weighting decomposition at ER=20:
      selSortino_wTailIC : Sortino score picks top-10, tail IC gives ICW weights
      selTailIC_wSortino : tail IC picks top-10, Sortino score gives weights

Usage:
    python newtrade/tests/test_exit_rank_sortino_ab.py
    python newtrade/tests/test_exit_rank_sortino_ab.py --groups A
"""

import sys
import time
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from run_backtest import run_single_backtest, resolve_ic_ema_span
from weighting import adaptive_exit_rank, adaptive_exit_rank_clusters
from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, rolling_tail_ic_numba,
                   rolling_factor_risk_numba, composite_tailic_risk_score,
                   load_cluster_assignments)

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
ER_FIXED = [15, 17, 20, 23, 25]
SORTINO_W_IC = 0.4
TAIL_WINDOW = 480
TAIL_PCT = 0.10

# REPORT.md baseline expected Cost Sharpe (TailIC, ER=20)
REPORT_BASELINE = {"300ETF": 0.145, "500ETF": 0.942, "159915ETF": 0.965}


def er_variants_for_etf(n_features: int, n_clusters: int) -> list:
    """(label, exit_rank) list: fixed grid + pool-adaptive + cluster-adaptive."""
    variants = [(f"ER{er}", er) for er in ER_FIXED]
    variants.append(("poolAdapt", adaptive_exit_rank(n_features, 10, hard_cap=25)))
    variants.append(("clustAdapt", adaptive_exit_rank_clusters(n_clusters, 10, hard_cap=25)))
    return variants


def run_icw_backtest(etf: str, start_date: str, end_date: str, fee_bps: float,
                     z_buffer: float, exit_rank: int,
                     ic_override: np.ndarray = None,
                     weight_ic_override: np.ndarray = None) -> dict:
    """ICW backtest with REPORT.md production config; only ER / IC matrices vary."""
    return run_single_backtest(
        etf=etf, side="single", scheme_name="icw", z_th=0.5,
        position_mode="fast_ramp_quadratic", fee_bps=fee_bps,
        start_date=start_date, end_date=end_date,
        z_buffer=z_buffer, auto_threshold=True, dynamic_ic=True,
        rank_kwargs={
            "top_k": 10,
            "ic_ema_span": resolve_ic_ema_span(etf, None),
            "dynamic_metric": "ic",
        },
        ic_mode="rolling_tail", tail_window=TAIL_WINDOW, tail_pct=TAIL_PCT,
        use_stoploss=True, stoploss_mode="time_decay_trailing", stoploss_param=0.03,
        hysteresis=True, exit_rank=exit_rank, min_pos=0.7, delta_z_full=0.4,
        ic_override=ic_override, weight_ic_override=weight_ic_override,
    )


def precompute(etf: str) -> dict:
    """tailIC / Sharpe / Sortino 480d matrices + pool & cluster info (zero-lookahead)."""
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None
    df = load_etf_dataset(etf)
    full_trade_ret = (df["trade_return"].values.astype(np.float64)
                      if "trade_return" in df.columns
                      else df["close"].pct_change().fillna(0.0).values)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    t0 = time.time()
    ic_mat = rolling_tail_ic_numba(Z_std, signs, full_trade_ret,
                                   window=TAIL_WINDOW, tail_pct=TAIL_PCT, burn_in=burn_in)
    sharpe_mat, sortino_mat = rolling_factor_risk_numba(Z_std, signs, full_trade_ret,
                                                        window=TAIL_WINDOW, burn_in=burn_in)

    feat_to_cluster = load_cluster_assignments(etf, "single") or {}
    n_clusters = len(set(feat_to_cluster.values())) if feat_to_cluster else len(pool)

    print(f"  [{etf}] matrices in {time.time()-t0:.1f}s | N={len(pool)} | clusters={n_clusters}")
    return {"ic": ic_mat, "sortino": sortino_mat, "n_features": len(pool),
            "n_clusters": n_clusters}


def _record(results: list, arm: str, er_label: str, exit_rank: int, etf: str, res: dict):
    results.append({
        "Arm": arm, "ER": er_label, "ExitRank": exit_rank, "ETF": etf,
        "Features": res["n_features"], "Trades": res["n_trades"],
        "CostSharpe": res["cost_sharpe"], "TotalPnL": res["total_pnl"],
        "MaxDD": res["max_drawdown"], "WinRate": res["win_rate_pct"],
        "Turnover": res.get("ann_turnover", 0),
    })


def main():
    parser = argparse.ArgumentParser(description="exit_rank x Sortino Score IC A/B test")
    parser.add_argument("--fee-bps", type=float, default=8.0)
    parser.add_argument("--z-buffer", type=float, default=0.1)
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("--groups", type=str, default="ABC",
                        help="Subset of groups to run, e.g. 'A', 'AB', 'ABC' (default)")
    parser.add_argument("-o", "--output", type=str, default=None)
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0
    run_groups = set(args.groups.upper())

    print("=" * 100)
    print("EXIT_RANK × SORTINO SCORE IC A/B TEST")
    print(f"OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps | buffer={args.z_buffer} | groups={''.join(sorted(run_groups))}")
    print("=" * 100)

    results = []
    baseline_er20 = {}

    for etf in AVAILABLE_ETFS:
        print(f"\n{'#'*100}\n# {etf}\n{'#'*100}")
        mats = precompute(etf)
        if mats is None:
            print(f"  [{etf}] SKIP (pool < 10)")
            continue

        variants = er_variants_for_etf(mats["n_features"], mats["n_clusters"])
        print(f"  ER variants: {[(lab, er) for lab, er in variants]}")
        sortino_score = composite_tailic_risk_score(mats["ic"], mats["sortino"], SORTINO_W_IC)
        run_cache = {}  # (arm, er_val) -> result dict (avoid duplicate backtests)

        for er_label, er_val in variants:
            # ─── Group A: TailIC baseline ───
            if "A" in run_groups:
                tag = "TailIC"
                ck = (tag, er_val)
                if ck in run_cache:
                    res = run_cache[ck]
                    print(f"\n[{tag}/{er_label}={er_val}] {etf}... (cached)")
                else:
                    print(f"\n[{tag}/{er_label}={er_val}] {etf}...")
                    res = run_icw_backtest(etf, args.start_date, args.end_date,
                                           fee_bps, args.z_buffer, exit_rank=er_val)
                    run_cache[ck] = res
                if res.get("status") == "SUCCESS":
                    _record(results, tag, er_label, er_val, etf, res)
                    if er_val == 20:
                        exp = REPORT_BASELINE[etf]
                        d = res["cost_sharpe"] - exp
                        flag = "OK" if abs(d) < 0.005 else "MISMATCH vs REPORT.md!"
                        print(f"    Sharpe={res['cost_sharpe']:.3f} (REPORT.md={exp:.3f}, Δ={d:+.4f}) [{flag}]")
                        baseline_er20[etf] = res["cost_sharpe"]
                    else:
                        print(f"    Sharpe={res['cost_sharpe']:.3f}")

            # ─── Group B: Sortino4_6 blend ───
            if "B" in run_groups:
                tag = "Sortino4_6"
                ck = (tag, er_val)
                if ck in run_cache:
                    res = run_cache[ck]
                    print(f"\n[{tag}/{er_label}={er_val}] {etf}... (cached)")
                else:
                    print(f"\n[{tag}/{er_label}={er_val}] {etf}...")
                    res = run_icw_backtest(etf, args.start_date, args.end_date,
                                           fee_bps, args.z_buffer, exit_rank=er_val,
                                           ic_override=sortino_score)
                    run_cache[ck] = res
                if res.get("status") == "SUCCESS":
                    _record(results, tag, er_label, er_val, etf, res)
                    print(f"    Sharpe={res['cost_sharpe']:.3f}")

        # ─── Group C: selection/weighting decomposition at ER=20 ───
        if "C" in run_groups:
            for tag, ic_ov, w_ov in [
                ("selSortino_wTailIC", sortino_score, mats["ic"]),
                ("selTailIC_wSortino", None, sortino_score),
            ]:
                print(f"\n[{tag}/ER20] {etf}...")
                res = run_icw_backtest(etf, args.start_date, args.end_date,
                                       fee_bps, args.z_buffer, exit_rank=20,
                                       ic_override=ic_ov, weight_ic_override=w_ov)
                if res.get("status") == "SUCCESS":
                    _record(results, tag, "ER20", 20, etf, res)
                    print(f"    Sharpe={res['cost_sharpe']:.3f}")

    if not results:
        print("\nERROR: no successful backtests.")
        return

    df_res = pd.DataFrame(results)

    # ─── Report: pivot per arm ────────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("RESULTS — CostSharpe by Arm × ER (rows) and ETF (cols); Avg + Δ vs TailIC/ER20")
    print("=" * 100)
    df_res["ArmER"] = df_res["Arm"] + "/" + df_res["ER"]
    pivot = df_res.pivot_table(index=["Arm", "ER", "ExitRank"], columns="ETF",
                               values="CostSharpe", aggfunc="first")
    pivot["Avg"] = pivot.mean(axis=1)
    base_avg = pivot.loc[("TailIC", "ER20", 20), "Avg"] if ("TailIC", "ER20", 20) in pivot.index else 0.0
    pivot["ΔBase"] = pivot["Avg"] - base_avg
    pivot = pivot.sort_values("Avg", ascending=False)
    print("\n" + pivot.round(3).to_string())

    # ─── Per-arm group summary ────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("HEAD-TO-HEAD vs TailIC/ER20 baseline (per-ETF Δ Sharpe)")
    print("-" * 100)
    base = pivot.loc[("TailIC", "ER20", 20)].drop(["Avg", "ΔBase"]) if ("TailIC", "ER20", 20) in pivot.index else None
    if base is not None:
        for idx, row in pivot.iterrows():
            if idx == ("TailIC", "ER20", 20):
                continue
            deltas = row.drop(["Avg", "ΔBase"]) - base
            wins = int((deltas > 0).sum())
            dstr = "  ".join(f"{e}:{d:+.3f}" for e, d in deltas.items())
            print(f"  {idx[0]:<18} {idx[1]:<10} wins={wins}/{len(deltas)}  [{dstr}]")

    # ─── Best config detection ────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("BEST CONFIGS")
    print("-" * 100)
    top3 = pivot.head(3)
    for idx, row in top3.iterrows():
        per_etf = row.drop(["Avg", "ΔBase"])
        all_beat = bool((per_etf > base).all()) if base is not None else False
        print(f"  {idx[0]}/{idx[1]} (ER={idx[2]}): AvgSharpe={row['Avg']:.3f} (Δ={row['ΔBase']:+.3f})"
              f"{'  <-- beats baseline on ALL ETFs' if all_beat else ''}")

    out_csv = Path(args.output) if args.output else HERE / "exit_rank_sortino_ab_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")
    print("\n[OK] exit_rank × Sortino A/B test complete.")


if __name__ == "__main__":
    main()
