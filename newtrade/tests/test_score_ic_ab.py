#!/usr/bin/env python3
"""
A/B Test: Score IC (Tail IC 480d + Rolling Sharpe/Sortino 480d) vs Baseline

Motivation:
  Rolling tail IC 480d (ICW shrinkage, top-10 hysteresis) beat total IC / IC_IR /
  expanding IC in prior experiments. But factor-level rolling Sharpe / Sortino 480d
  (the metric day-model-new uses to distinguish TP vs Median) was never tested as a
  weighting component. This test blends:

      Score[t,j] = w_ic * rank(tailIC_480d[t,j]) + (1 - w_ic) * rank(risk_480d[t,j])

  with w_ic swept over {0.3, 0.4, 0.5, 0.6, 0.7} and risk in {Sharpe, Sortino}.
  The score matrix is injected as the ICW ranking/weight matrix; everything else
  (EMA smoothing, top-10 hysteresis, ICW shrinkage, threshold sweep, position sizing,
  stop-loss, fees) is IDENTICAL to the REPORT.md baseline.

Baseline requirement:
  Arm "TailIC_ICW" is the UNMODIFIED REPORT.md production config
  (icw + rolling_tail 480d + dynamic_metric=ic + fast_ramp_quadratic + stoploss +
   8 bps + buffer 0.1 + exit_rank 20 + top_k 10) and must reproduce REPORT.md.

Usage:
    python newtrade/tests/test_score_ic_ab.py
    python newtrade/tests/test_score_ic_ab.py --baseline-only
    python newtrade/tests/test_score_ic_ab.py --metrics sharpe
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
                   rolling_factor_risk_numba, composite_tailic_risk_score)

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
W_IC_GRID = [0.3, 0.4, 0.5, 0.6, 0.7]
TAIL_WINDOW = 480
TAIL_PCT = 0.10
RISK_WINDOW = 480

# ─── REPORT.md baseline expected values (Cost Sharpe, for verification) ────────
REPORT_BASELINE = {"300ETF": 0.145, "500ETF": 0.942, "159915ETF": 0.965}


def run_icw_backtest(etf: str, start_date: str, end_date: str, fee_bps: float,
                     z_buffer: float, ic_override: np.ndarray = None) -> dict:
    """ICW backtest with exact REPORT.md production config (+ optional IC override)."""
    res = run_single_backtest(
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
        hysteresis=True, exit_rank=20, min_pos=0.7, delta_z_full=0.4,
        ic_override=ic_override,
    )
    return res


def precompute_metric_matrices(etf: str) -> dict:
    """Compute tailIC / Sharpe / Sortino 480d matrices ONCE per ETF (zero-lookahead)."""
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
                                                        window=RISK_WINDOW, burn_in=burn_in)
    print(f"  [{etf}] metric matrices computed in {time.time()-t0:.1f}s (N={len(pool)}, T={len(df)})")
    return {"ic": ic_mat, "sharpe": sharpe_mat, "sortino": sortino_mat, "n_features": len(pool)}


def main():
    parser = argparse.ArgumentParser(description="Score IC A/B Test (TailIC + Sharpe/Sortino 480d)")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Fee per leg in bps (default 8.0 = REPORT.md)")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Threshold buffer (default 0.1 = REPORT.md)")
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("--metrics", type=str, default="both", choices=["sharpe", "sortino", "both"],
                        help="Which risk metric family to sweep (default both)")
    parser.add_argument("--baseline-only", action="store_true",
                        help="Only run baseline arms (verify match with REPORT.md)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0
    risk_families = ["sharpe", "sortino"] if args.metrics == "both" else [args.metrics]

    print("=" * 100)
    print("SCORE IC A/B TEST — Tail IC 480d + Rolling Sharpe/Sortino 480d (top-10 ICW hysteresis)")
    print(f"OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps | Z-buffer={args.z_buffer}")
    print("=" * 100)

    results = []

    # ─── Phase 0: Baseline (unmodified REPORT.md config) ───────────────────────
    print("\n>>> PHASE 0: BASELINE (TailIC_ICW, unmodified REPORT.md config)")
    for etf in AVAILABLE_ETFS:
        print(f"\n[Baseline] {etf}...")
        res = run_icw_backtest(etf, args.start_date, args.end_date, fee_bps, args.z_buffer)
        if res.get("status") == "SUCCESS":
            exp = REPORT_BASELINE.get(etf)
            delta = (res["cost_sharpe"] - exp) if exp is not None else float("nan")
            results.append({
                "Arm": "TailIC_ICW", "w_ic": 1.0, "RiskMetric": "none", "ETF": etf,
                "Features": res["n_features"], "Trades": res["n_trades"],
                "CostSharpe": res["cost_sharpe"], "RawSharpe": res["raw_sharpe"],
                "TotalPnL": res["total_pnl"], "MaxDD": res["max_drawdown"],
                "WinRate": res["win_rate_pct"], "Turnover": res.get("ann_turnover", 0),
                "ReportSharpe": exp, "DeltaVsReport": delta,
            })
            flag = "OK" if abs(delta) < 0.005 else "MISMATCH vs REPORT.md!"
            print(f"    Sharpe={res['cost_sharpe']:.3f} (REPORT.md={exp:.3f}, Δ={delta:+.4f}) [{flag}]")
        else:
            print(f"    ! SKIPPED: {res.get('status')}")

    # ─── Phase 1: Score IC sweep arms ───────────────────────────────────────────
    if not args.baseline_only:
        print("\n>>> PHASE 1: SCORE IC SWEEP")
        for etf in AVAILABLE_ETFS:
            print(f"\n{'='*60}\n{etf}: precomputing metric matrices...\n{'='*60}")
            mats = precompute_metric_matrices(etf)
            if mats is None:
                print(f"  [{etf}] SKIP (pool < 10)")
                continue
            for risk in risk_families:
                risk_mat = mats[risk]
                for w_ic in W_IC_GRID:
                    label = f"ScoreIC_{risk}_{int(w_ic*10)}_{int((1-w_ic)*10)}"
                    print(f"\n[{label}] {etf} (w_ic={w_ic:.1f}, w_{risk}={1-w_ic:.1f})...")
                    score_mat = composite_tailic_risk_score(mats["ic"], risk_mat, w_ic)
                    res = run_icw_backtest(etf, args.start_date, args.end_date,
                                           fee_bps, args.z_buffer, ic_override=score_mat)
                    if res.get("status") == "SUCCESS":
                        results.append({
                            "Arm": label, "w_ic": w_ic, "RiskMetric": risk, "ETF": etf,
                            "Features": res["n_features"], "Trades": res["n_trades"],
                            "CostSharpe": res["cost_sharpe"], "RawSharpe": res["raw_sharpe"],
                            "TotalPnL": res["total_pnl"], "MaxDD": res["max_drawdown"],
                            "WinRate": res["win_rate_pct"], "Turnover": res.get("ann_turnover", 0),
                            "ReportSharpe": None, "DeltaVsReport": None,
                        })
                    else:
                        print(f"    ! SKIPPED: {res.get('status')}")

    if not results:
        print("\nERROR: No successful backtests.")
        return

    df_res = pd.DataFrame(results)

    # ─── Report: ranking vs baseline ────────────────────────────────────────────
    avg = df_res.groupby(["Arm", "w_ic", "RiskMetric"]).agg(
        AvgSharpe=("CostSharpe", "mean"), AvgPnL=("TotalPnL", "mean"),
        AvgMaxDD=("MaxDD", "mean"), AvgWinRate=("WinRate", "mean"),
        AvgTurnover=("Turnover", "mean"),
    ).reset_index().sort_values("AvgSharpe", ascending=False)

    base_rows = avg[avg["Arm"] == "TailIC_ICW"]
    base_sr = float(base_rows["AvgSharpe"].iloc[0]) if not base_rows.empty else 0.0

    print("\n" + "=" * 100)
    print("FULL-PERIOD RESULTS — RANKED BY AVG COST SHARPE (baseline = TailIC_ICW)")
    print("=" * 100)
    print(f"\n{'Rank':<5} {'Arm':<24} {'AvgSharpe':>10} {'Δ vs Base':>10} {'AvgPnL':>10} {'AvgMaxDD':>9} {'AvgWR%':>7} {'Turnover':>9}")
    print("-" * 90)
    for rk, (_, row) in enumerate(avg.iterrows(), start=1):
        delta = row["AvgSharpe"] - base_sr
        marker = " *" if row["Arm"] == "TailIC_ICW" else ""
        print(f"{rk:<5} {row['Arm']:<24} {row['AvgSharpe']:>10.3f} {delta:>+10.3f} "
              f"{row['AvgPnL']:>10.4f} {row['AvgMaxDD']:>9.4f} {row['AvgWinRate']:>7.1f} "
              f"{row['AvgTurnover']:>9.2f}{marker}")

    # ─── Per-ETF detail ─────────────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("PER-ETF DETAIL (CostSharpe)")
    print("-" * 100)
    pivot = df_res.pivot_table(index="Arm", columns="ETF", values="CostSharpe", aggfunc="first")
    pivot = pivot.reindex(avg["Arm"])
    print(pivot.round(3).to_string())

    # ─── Win/loss vs baseline per ETF ───────────────────────────────────────────
    if not args.baseline_only:
        print("\n" + "-" * 100)
        print("HEAD-TO-HEAD vs BASELINE (per-ETF Sharpe delta)")
        print("-" * 100)
        base_pivot = df_res[df_res["Arm"] == "TailIC_ICW"].set_index("ETF")["CostSharpe"]
        for _, row in avg.iterrows():
            if row["Arm"] == "TailIC_ICW":
                continue
            arm_sub = df_res[df_res["Arm"] == row["Arm"]].set_index("ETF")["CostSharpe"]
            deltas = arm_sub - base_pivot
            wins = int((deltas > 0).sum())
            dstr = "  ".join(f"{e}:{d:+.3f}" for e, d in deltas.items())
            print(f"  {row['Arm']:<24} wins={wins}/{len(deltas)}  [{dstr}]")

    # ─── Save CSV ────────────────────────────────────────────────────────────────
    out_csv = Path(args.output) if args.output else HERE / "score_ic_ab_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")
    print("\n[OK] Score IC A/B test complete.")


if __name__ == "__main__":
    main()
