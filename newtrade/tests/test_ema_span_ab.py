#!/usr/bin/env python3
"""
EMA Span Retest — is the IC EMA smoothing (30d/90d production) still justified?

Hypothesis: spans were tuned in the expanding-IC era. Rolling tail IC 480d is
already a long-window estimator; extra EMA smoothing mainly adds lag and slows
response to regime shifts. Sweep span = {1(off), 5, 10, 20, 30, 60, 90, 120}
per ETF with everything else at REPORT.md config (ER=25, tail IC 480d, 8bps).

Baselines to reproduce: 300ETF span30 = 0.204, 500ETF span90 = 1.039,
159915ETF span90 = 0.930.

Usage:
    python newtrade/tests/test_ema_span_ab.py
"""

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from run_backtest import run_single_backtest

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
SPANS = [1, 5, 10, 20, 30, 60, 90, 120]
PROD_SPAN = {"300ETF": 30, "500ETF": 90, "159915ETF": 90}
REPORT_BASELINE = {"300ETF": 0.204, "500ETF": 1.039, "159915ETF": 0.930}


def run_arm(etf: str, span: int) -> dict:
    return run_single_backtest(
        etf=etf, side="single", scheme_name="icw", z_th=0.5,
        position_mode="fast_ramp_quadratic", fee_bps=8.0 / 10000.0,
        start_date="2022-01-01", end_date="2026-01-01",
        z_buffer=0.1, auto_threshold=True, dynamic_ic=True,
        rank_kwargs={"top_k": 10, "ic_ema_span": span, "dynamic_metric": "ic"},
        ic_mode="rolling_tail", tail_window=480, tail_pct=0.10,
        use_stoploss=True, stoploss_mode="time_decay_trailing", stoploss_param=0.03,
        hysteresis=True, exit_rank=25, min_pos=0.7, delta_z_full=0.4,
    )


def main():
    print("=" * 100)
    print(f"EMA SPAN RETEST — spans={SPANS} (OOS 2022-01 ~ 2026-01, rolling tail IC 480d, ER=25)")
    print("=" * 100)

    results = []
    for etf in AVAILABLE_ETFS:
        print(f"\n{'#'*90}\n# {etf}  (production span = {PROD_SPAN[etf]})\n{'#'*90}")
        for span in SPANS:
            res = run_arm(etf, span)
            if res.get("status") != "SUCCESS":
                print(f"  [span={span:<3}] SKIPPED: {res.get('status')}")
                continue
            results.append({"ETF": etf, "Span": span, "CostSharpe": res["cost_sharpe"],
                            "RawSharpe": res["raw_sharpe"], "TotalPnL": res["total_pnl"],
                            "Trades": res["n_trades"], "MaxDD": res["max_drawdown"]})
            tag = ""
            if span == PROD_SPAN[etf]:
                exp = REPORT_BASELINE[etf]
                d = res["cost_sharpe"] - exp
                tag = f"  <-- PROD (report={exp:.3f}, Δ={d:+.4f}) [{'OK' if abs(d) < 0.005 else 'MISMATCH!'}]"
            print(f"  [span={span:<3}] Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}  trades={res['n_trades']}{tag}")

    df_res = pd.DataFrame(results)
    pv = df_res.pivot_table(index="Span", columns="ETF", values="CostSharpe", aggfunc="first")
    pv["Avg"] = pv.mean(axis=1)
    etf_cols = [c for c in pv.columns if c != "Avg"]

    # per-ETF production delta
    prod_avg = sum(REPORT_BASELINE[e] for e in etf_cols) / len(etf_cols)
    pv["ΔProd"] = pv["Avg"] - prod_avg
    pv = pv.sort_values("Avg", ascending=False)

    print("\n" + "=" * 100)
    print("RESULTS — CostSharpe by EMA span × ETF (sorted by avg)")
    print("=" * 100)
    print(pv.round(3).to_string())

    print("\n" + "-" * 100)
    print("PER-ETF BEST SPAN vs PRODUCTION SPAN")
    print("-" * 100)
    for etf in etf_cols:
        s = df_res[df_res["ETF"] == etf].set_index("Span")["CostSharpe"]
        best_span = s.idxmax()
        prod = s.loc[PROD_SPAN[etf]]
        print(f"  {etf:<12} best span={best_span:<4} ({s.max():.3f})  vs prod span={PROD_SPAN[etf]:<4} ({prod:.3f})  Δ={s.max()-prod:+.3f}")

    best_fixed = pv.index[0]
    print(f"\n  best FIXED span across ETFs: {best_fixed} (avg {pv.loc[best_fixed,'Avg']:.3f} vs production avg {prod_avg:.3f}, Δ={pv.loc[best_fixed,'ΔProd']:+.3f})")

    df_res.to_csv(HERE / "ema_span_ab_results.csv", index=False)
    print(f"\nSaved to {HERE / 'ema_span_ab_results.csv'}")
    print("\n[OK] EMA span retest complete.")


if __name__ == "__main__":
    main()
