#!/usr/bin/env python3
"""
EMA Span — yearly stability confirmation for the span sweep result.

Full-OOS sweep (test_ema_span_ab.py) found: span=1 (off) is WORST everywhere;
longer spans win (300ETF: 60 beats prod 30 by +0.335; 500ETF: prod 90 optimal;
159915ETF: 120 beats prod 90 by +0.191). Since spans were chosen on the same
OOS window, confirm on per-year backtests (threshold re-swept on pre-year data):

Configs:
  prod       : spans 30 / 90 / 90 (300/500/159915)
  fixed60    : span 60 everywhere
  perETF-best: spans 60 / 90 / 120
  compromise : spans 60 / 90 / 90

Usage:
    python newtrade/tests/test_ema_span_yearly.py
"""

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from run_backtest import run_single_backtest

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
YEARS = [2022, 2023, 2024, 2025]
CONFIGS = {
    "prod":        {"300ETF": 30, "500ETF": 90, "159915ETF": 90},
    "fixed60":     {"300ETF": 60, "500ETF": 60, "159915ETF": 60},
    "perETF_best": {"300ETF": 60, "500ETF": 90, "159915ETF": 120},
    "compromise":  {"300ETF": 60, "500ETF": 90, "159915ETF": 90},
}


def run_year(etf: str, year: int, span: int) -> dict:
    return run_single_backtest(
        etf=etf, side="single", scheme_name="icw", z_th=0.5,
        position_mode="fast_ramp_quadratic", fee_bps=8.0 / 10000.0,
        start_date=f"{year}-01-01", end_date=f"{year + 1}-01-01",
        z_buffer=0.1, auto_threshold=True, dynamic_ic=True,
        rank_kwargs={"top_k": 10, "ic_ema_span": span, "dynamic_metric": "ic"},
        ic_mode="rolling_tail", tail_window=480, tail_pct=0.10,
        use_stoploss=True, stoploss_mode="time_decay_trailing", stoploss_param=0.03,
        hysteresis=True, exit_rank=25, min_pos=0.7, delta_z_full=0.4,
    )


def main():
    print("=" * 100)
    print("EMA SPAN — YEARLY STABILITY (threshold re-swept on pre-year data)")
    print("=" * 100)

    rows = []
    for cfg_name, spans in CONFIGS.items():
        for etf in AVAILABLE_ETFS:
            span = spans[etf]
            for year in YEARS:
                res = run_year(etf, year, span)
                if res.get("status") == "SUCCESS":
                    rows.append({"Config": cfg_name, "ETF": etf, "Year": year,
                                 "Span": span, "CostSharpe": res["cost_sharpe"],
                                 "TotalPnL": res["total_pnl"], "Trades": res["n_trades"]})
                    print(f"  [{cfg_name:<12} {etf:<10} {year} span={span:<3}] "
                          f"Sharpe={res['cost_sharpe']:.3f}  trades={res['n_trades']}")
                else:
                    print(f"  [{cfg_name:<12} {etf:<10} {year}] SKIPPED")

    df = pd.DataFrame(rows)
    pv = df.pivot_table(index=["Config", "ETF"], columns="Year",
                        values="CostSharpe", aggfunc="first")
    pv["Mean"] = pv.mean(axis=1)
    pv["N_neg"] = (pv[YEARS] < 0).sum(axis=1)

    print("\n" + "=" * 100)
    print("YEARLY COST SHARPE BY CONFIG × ETF")
    print("=" * 100)
    print(pv.round(3).to_string())

    print("\n" + "-" * 100)
    print("CONFIG COMPARISON (mean across ETFs)")
    print("-" * 100)
    cfg_mean = df.groupby(["Config", "Year"])["CostSharpe"].mean().unstack()
    cfg_mean["AllMean"] = cfg_mean.mean(axis=1)
    print(cfg_mean.round(3).to_string())

    prod = pv.loc["prod"]
    for cfg in ["fixed60", "perETF_best", "compromise"]:
        wins = 0
        deltas = []
        for etf in AVAILABLE_ETFS:
            d = pv.loc[(cfg, etf), "Mean"] - prod.loc[etf, "Mean"]
            deltas.append(d)
            wins += 1 if d > 0 else 0
        dstr = "  ".join(f"{e}:{d:+.3f}" for e, d in zip(AVAILABLE_ETFS, deltas))
        print(f"  {cfg:<12} vs prod: wins={wins}/3  meanΔ={sum(deltas)/3:+.3f}  [{dstr}]")

    df.to_csv(HERE / "ema_span_yearly_results.csv", index=False)
    print(f"\nSaved to {HERE / 'ema_span_yearly_results.csv'}")
    print("\n[OK] EMA span yearly confirmation complete.")


if __name__ == "__main__":
    main()
