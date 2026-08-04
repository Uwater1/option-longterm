#!/usr/bin/env python3
"""
Verify the new production defaults (2026-08): spans 60/90/90 + Sortino<=0 gate.

Arms per ETF (icw scheme, ER=25, REPORT.md config, OOS 2022-2026):
  new_defaults : resolve_ic_ema_span defaults (60/90/90) + sortino_gate=True
  gate_off     : same spans, sortino_gate=False  (isolates the gate under new spans)
  old_prod     : spans 30/90/90, gate off (should reproduce 0.204/1.039/0.930)

Expectations from earlier tests:
  500ETF: gate never fires -> new_defaults == gate_off == old_prod (1.039)
  300ETF: span 60 lifts to ~0.539 (gate may or may not fire under new spans)
  159915ETF: gate adds ~+0.135 over span-90 baseline

Usage:
    python newtrade/tests/test_new_defaults_verify.py
"""

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from run_backtest import run_single_backtest, resolve_ic_ema_span

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
OLD_SPANS = {"300ETF": 30, "500ETF": 90, "159915ETF": 90}
OLD_REPORT = {"300ETF": 0.204, "500ETF": 1.039, "159915ETF": 0.930}


def run(etf, span, gate):
    return run_single_backtest(
        etf=etf, side="single", scheme_name="icw", z_th=0.5,
        position_mode="fast_ramp_quadratic", fee_bps=8.0 / 10000.0,
        start_date="2022-01-01", end_date="2026-01-01",
        z_buffer=0.1, auto_threshold=True, dynamic_ic=True,
        rank_kwargs={"top_k": 10, "ic_ema_span": span, "dynamic_metric": "ic"},
        ic_mode="rolling_tail", tail_window=480, tail_pct=0.10,
        use_stoploss=True, stoploss_mode="time_decay_trailing", stoploss_param=0.03,
        hysteresis=True, exit_rank=25, min_pos=0.7, delta_z_full=0.4,
        sortino_gate=gate,
    )


def main():
    print("=" * 100)
    print("NEW PRODUCTION DEFAULTS VERIFICATION — spans 60/90/90 + Sortino<=0 gate")
    print("=" * 100)
    rows = []
    for etf in AVAILABLE_ETFS:
        new_span = resolve_ic_ema_span(etf, None)
        print(f"\n# {etf} (new default span={new_span}, old span={OLD_SPANS[etf]})")
        for arm, span, gate in [
            ("new_defaults", new_span, True),
            ("gate_off", new_span, False),
            ("old_prod", OLD_SPANS[etf], False),
        ]:
            res = run(etf, span, gate)
            if res.get("status") != "SUCCESS":
                print(f"  [{arm:<13}] SKIPPED")
                continue
            rows.append({"Arm": arm, "ETF": etf, "Span": span, "Gate": gate,
                         "CostSharpe": res["cost_sharpe"], "TotalPnL": res["total_pnl"],
                         "Trades": res["n_trades"]})
            tag = ""
            if arm == "old_prod":
                exp = OLD_REPORT[etf]
                d = res["cost_sharpe"] - exp
                tag = f"  <-- old REPORT (Δ={d:+.4f}) [{'OK' if abs(d) < 0.005 else 'MISMATCH!'}]"
            print(f"  [{arm:<13}] Sharpe={res['cost_sharpe']:.3f}  PnL={res['total_pnl']:+.4f}  trades={res['n_trades']}{tag}")

    df = pd.DataFrame(rows)
    pv = df.pivot_table(index="Arm", columns="ETF", values="CostSharpe", aggfunc="first")
    pv["Avg"] = pv.mean(axis=1)
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(pv.round(3).to_string())
    old_avg = sum(OLD_REPORT.values()) / 3
    nd = pv.loc["new_defaults", "Avg"]
    print(f"\n  new defaults avg = {nd:.3f} vs old production avg = {old_avg:.3f} (Δ={nd-old_avg:+.3f})")
    gate_eff = df[df["Arm"] == "new_defaults"].set_index("ETF")["CostSharpe"] - \
               df[df["Arm"] == "gate_off"].set_index("ETF")["CostSharpe"]
    print("  gate effect under new spans: " + "  ".join(f"{e}:{d:+.3f}" for e, d in gate_eff.items()))

    df.to_csv(HERE / "new_defaults_verify_results.csv", index=False)
    print(f"\nSaved to {HERE / 'new_defaults_verify_results.csv'}")


if __name__ == "__main__":
    main()
