#!/usr/bin/env python3
"""
Phase 3 — Newtrade Integration A/B for the FQ Score system.

Baseline arm = unmodified REPORT.md config (icw, rolling_tail 480d, ER=25,
fast_ramp_quadratic, stoploss, 8bps) — must reproduce 300:0.204 / 500:1.039 /
159915:0.930 before judging treatment arms.

Arms (OOS 2022-01-01 ~ 2026-01-01):
  1. TailIC_ICW          — baseline (REPORT.md ER=25 numbers)
  2. FQ_select_weight    — FQ matrix drives selection AND weights (ic_override)
  3. selTailIC_wFQ       — tail IC selects, FQ gives weights (decomposition)
  4. ScoreBlend_75_25    — current production Score blend reference

Success criteria (per plan): avg Sharpe improvement over baseline AND no single
ETF regressing more than 0.05 AND Phase 2 meta-IC significant.

Usage:
    python newtrade/tests/test_fq_ab.py
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
from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, rolling_tail_ic_numba,
                   composite_tailic_risk_score)
from factor_quality import compute_fq_components, fq_from_components, WINDOW

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
TAIL_WINDOW = 480
TAIL_PCT = 0.10
EXIT_RANK = 25

# REPORT.md ER=25 baseline expected Cost Sharpe (verified 2026-08)
REPORT_BASELINE_ER25 = {"300ETF": 0.204, "500ETF": 1.039, "159915ETF": 0.930}


def run_icw_backtest(etf: str, start_date: str, end_date: str, fee_bps: float,
                     z_buffer: float, ic_override=None, weight_ic_override=None) -> dict:
    """ICW backtest with REPORT.md production config at ER=25."""
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
        hysteresis=True, exit_rank=EXIT_RANK, min_pos=0.7, delta_z_full=0.4,
        ic_override=ic_override, weight_ic_override=weight_ic_override,
    )


def precompute_matrices(etf: str) -> dict:
    """tailIC / Sortino / FQ matrices per ETF (zero-lookahead, computed once)."""
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None
    df = load_etf_dataset(etf)
    trade_ret = (df["trade_return"].values.astype(np.float64)
                 if "trade_return" in df.columns
                 else df["close"].pct_change().fillna(0.0).values)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    t0 = time.time()
    ic_mat = rolling_tail_ic_numba(Z_std, signs, trade_ret,
                                   window=TAIL_WINDOW, tail_pct=TAIL_PCT, burn_in=burn_in)
    comps = compute_fq_components(Z_std, signs, trade_ret, window=WINDOW, burn_in=burn_in)
    fq_mat = fq_from_components(comps, use_extra_gates=False)
    print(f"  [{etf}] matrices in {time.time()-t0:.1f}s | N={len(pool)} | T={len(df)}")
    return {"ic": ic_mat, "fq": fq_mat, "sortino": comps["sortino"],
            "n_features": len(pool)}


def _record(results: list, arm: str, etf: str, res: dict):
    results.append({
        "Arm": arm, "ETF": etf, "Features": res["n_features"], "Trades": res["n_trades"],
        "CostSharpe": res["cost_sharpe"], "RawSharpe": res["raw_sharpe"],
        "TotalPnL": res["total_pnl"], "MaxDD": res["max_drawdown"],
        "WinRate": res["win_rate_pct"], "Turnover": res.get("ann_turnover", 0),
    })


def main():
    parser = argparse.ArgumentParser(description="FQ Score integration A/B test")
    parser.add_argument("--fee-bps", type=float, default=8.0)
    parser.add_argument("--z-buffer", type=float, default=0.1)
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("-o", "--output", type=str, default=None)
    args = parser.parse_args()
    fee_bps = args.fee_bps / 10000.0

    print("=" * 100)
    print(f"PHASE 3 — FQ INTEGRATION A/B (OOS {args.start_date} ~ {args.end_date}, ER={EXIT_RANK}, fee {args.fee_bps} bps)")
    print("=" * 100)

    results = []
    for etf in AVAILABLE_ETFS:
        print(f"\n{'#'*90}\n# {etf}\n{'#'*90}")
        mats = precompute_matrices(etf)
        if mats is None:
            print(f"  [{etf}] SKIP (pool < 10)")
            continue
        score_blend = composite_tailic_risk_score(mats["ic"], mats["sortino"], 0.75)

        arms = [
            ("TailIC_ICW",       None,            None),
            ("FQ_select_weight", mats["fq"],      None),
            ("selTailIC_wFQ",    None,            mats["fq"]),
            ("ScoreBlend_75_25", score_blend,     None),
        ]
        for arm, ic_ov, w_ov in arms:
            print(f"\n[{arm}] {etf}...")
            res = run_icw_backtest(etf, args.start_date, args.end_date, fee_bps,
                                   args.z_buffer, ic_override=ic_ov, weight_ic_override=w_ov)
            if res.get("status") == "SUCCESS":
                _record(results, arm, etf, res)
                if arm == "TailIC_ICW":
                    exp = REPORT_BASELINE_ER25[etf]
                    d = res["cost_sharpe"] - exp
                    flag = "OK" if abs(d) < 0.005 else "MISMATCH!"
                    print(f"    Sharpe={res['cost_sharpe']:.3f} (baseline={exp:.3f}, Δ={d:+.4f}) [{flag}]")
                else:
                    print(f"    Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}")
            else:
                print(f"    ! SKIPPED: {res.get('status')}")

    if not results:
        print("\nERROR: no successful backtests.")
        return

    df_res = pd.DataFrame(results)
    pv = df_res.pivot_table(index="Arm", columns="ETF", values="CostSharpe", aggfunc="first")
    pv["Avg"] = pv.mean(axis=1)
    base = pv.loc["TailIC_ICW"]
    pv["ΔBase"] = pv["Avg"] - base["Avg"]
    pv = pv.sort_values("Avg", ascending=False)
    etf_cols = [c for c in pv.columns if c not in ("Avg", "ΔBase")]
    base_etf = base[etf_cols]

    print("\n" + "=" * 100)
    print("RESULTS — CostSharpe by Arm × ETF (baseline = TailIC_ICW @ ER25)")
    print("=" * 100)
    print(pv.round(3).to_string())

    print("\n" + "-" * 100)
    print("HEAD-TO-HEAD vs BASELINE (per-ETF Δ Sharpe)")
    print("-" * 100)
    for arm, row in pv.iterrows():
        if arm == "TailIC_ICW":
            continue
        deltas = row[etf_cols] - base_etf
        wins = int((deltas > 0).sum())
        worst = float(deltas.min())
        dstr = "  ".join(f"{e}:{d:+.3f}" for e, d in deltas.items())
        print(f"  {arm:<18} wins={wins}/{len(deltas)}  worst={worst:+.3f}  [{dstr}]")

    # ─── Success criteria ──────────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("SUCCESS CRITERIA (avg Sharpe up AND no ETF worse than -0.05 AND Phase 2 meta-IC significant)")
    print("-" * 100)
    for arm, row in pv.iterrows():
        if arm == "TailIC_ICW":
            continue
        deltas = row[etf_cols] - base_etf
        crit1 = row["ΔBase"] > 0
        crit2 = bool((deltas >= -0.05).all())
        verdict = "PASS(1+2)" if crit1 and crit2 else ("partial" if crit1 or crit2 else "FAIL")
        print(f"  {arm:<18} ΔAvg={row['ΔBase']:+.3f} ({'up' if crit1 else 'down'})  "
              f"no-ETF-regress>0.05: {crit2}  -> {verdict} (+ meta-IC significance from Phase 2)")

    out_csv = Path(args.output) if args.output else HERE / "fq_ab_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")
    print("\n[OK] Phase 3 FQ A/B complete.")


if __name__ == "__main__":
    main()
