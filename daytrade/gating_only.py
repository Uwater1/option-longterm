"""Standalone gating-only backtest.

Tests the gating model as the SOLE trading signal: no daytrade linear score,
no expanding-percentile thresholds. If the long-gate fires → go long; if the
short-gate fires → go short; if both or neither → flat.

This answers: "Is the gate alone enough, without the daytrade conviction layer?"

Trade plan mirrors daytrade exactly:
  - decision at close[DECISION_BAR]
  - entry at open[DECISION_BAR + 1]
  - exit at close[EXIT_BAR=41] (14:30)
  - optional stop-loss (fixed-% or ATR)
  - 15 bps round-trip cost

Usage:
    python -m daytrade.gating_only                 # all ETFs, default stops
    python -m daytrade.gating_only -e 300          # one ETF
    python -m daytrade.gating_only --stop-pct 0.04 # fixed-% stop sweep
    python -m daytrade.gating_only --no-stop       # no stop-loss
"""
from __future__ import annotations

import argparse
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from . import ETFS, DECISION_BAR, EXIT_BAR, DEFAULT_COST_BPS, HOLDOUT_START
from .backtest import (
    get_grouped_bars, get_daily_atr14, _day_bars_to_series,
    _summarize_long_short, _empty_long_short_result, split_holdout,
)
from .gating_loader import load_gating_mask


def _sharpe(rets: np.ndarray) -> float:
    if len(rets) < 2 or np.std(rets, ddof=1) == 0:
        return float("nan")
    return float(np.mean(rets) / np.std(rets, ddof=1) * np.sqrt(252))


def backtest_gating_only(
    etf: str,
    cost_bps: float = DEFAULT_COST_BPS,
    stop_pct: float | None = None,
    stop_atr_k: float | None = None,
    long_enabled: bool = True,
    short_enabled: bool = True,
    conflict: str = "flat",
) -> dict:
    """Trade purely on the gating model's fire signal.

    conflict : {"flat", "long", "short"}
        What to do when BOTH gates fire on the same day.
        "flat" = no trade; "long" = take long; "short" = take short.
    """
    long_mask = load_gating_mask(etf, "long")
    short_mask = load_gating_mask(etf, "short")
    if long_mask is None and short_mask is None:
        print(f"  [{etf}] no gating models available — skipping.")
        return _empty_long_short_result(etf)

    by_date = get_grouped_bars(etf)
    decision_bar = DECISION_BAR[etf]
    exit_bar = EXIT_BAR
    atr_series = get_daily_atr14(etf) if stop_atr_k is not None else None

    # Align masks to a common date index (the features parquet index).
    idx = long_mask.index if long_mask is not None else short_mask.index

    rows = []
    for date in idx:
        d = date.date()
        if d not in by_date:
            continue
        day = by_date[d]

        l_fire = bool(long_mask.loc[date]) if (long_mask is not None and date in long_mask.index) else False
        s_fire = bool(short_mask.loc[date]) if (short_mask is not None and date in short_mask.index) else False

        if l_fire and s_fire:
            if conflict == "long":
                direction = 1
            elif conflict == "short":
                direction = -1
            else:
                direction = 0
        elif l_fire:
            direction = 1
        elif s_fire:
            direction = -1
        else:
            direction = 0

        if direction == 0:
            continue
        if direction > 0 and not long_enabled:
            continue
        if direction < 0 and not short_enabled:
            continue

        # Resolve stop
        effective_stop = None
        if stop_atr_k is not None and atr_series is not None:
            atr_val = atr_series.get(d)
            if atr_val is None or np.isnan(atr_val):
                atr_val = atr_series.iloc[:atr_series.index.get_loc(d)].max() if len(atr_series) > 0 else None
            if atr_val is not None and not np.isnan(atr_val):
                entry_idx = decision_bar + 1
                if len(day["open"]) > entry_idx:
                    entry_tmp = float(day["open"][entry_idx])
                    if entry_tmp > 0:
                        effective_stop = stop_atr_k * atr_val / entry_tmp
        elif stop_pct is not None:
            effective_stop = stop_pct

        entry, exit_, exit_type = _day_bars_to_series(
            day, decision_bar, exit_bar, direction=direction, stop_pct=effective_stop,
        )
        if entry is None:
            continue
        gross = direction * (exit_ / entry - 1.0)
        net = gross - cost_bps / 1e4
        rows.append({
            "date": date, "direction": direction,
            "side": "long" if direction > 0 else "short",
            "entry": entry, "exit": exit_, "exit_type": exit_type,
            "gross_ret": gross, "net_ret": net,
        })

    if not rows:
        return _empty_long_short_result(etf)

    trades = pd.DataFrame(rows).set_index("date").sort_index()
    metrics = _summarize_long_short(trades, etf, cost_bps)
    metrics["trades"] = trades
    return metrics


def _metrics_line(label: str, trades: pd.DataFrame) -> str:
    if len(trades) == 0:
        return f"{label:<8} n=0"
    rets = trades["net_ret"].values
    return (f"{label:<8} n={len(trades):>4} S={_sharpe(rets):+6.2f} "
            f"pnl={rets.sum()*1e4:+8.0f} wr={(rets>0).mean():.0%} "
            f"med={np.median(rets)*1e4:+6.1f}")


def run_one(etf: str, stop_pct, stop_atr_k, cost_bps, conflict="flat", verbose=True):
    r = backtest_gating_only(
        etf, cost_bps=cost_bps, stop_pct=stop_pct, stop_atr_k=stop_atr_k,
        conflict=conflict,
    )
    trades = r["trades"]
    if len(trades) == 0:
        if verbose:
            print(f"  [{etf}] no trades.")
        return r

    is_, oos = split_holdout(trades)
    long_trades = trades[trades["direction"] > 0]
    short_trades = trades[trades["direction"] < 0]
    is_long = long_trades[long_trades.index < pd.Timestamp(HOLDOUT_START)]
    is_short = short_trades[short_trades.index < pd.Timestamp(HOLDOUT_START)]
    oos_long = long_trades[long_trades.index >= pd.Timestamp(HOLDOUT_START)]
    oos_short = short_trades[short_trades.index >= pd.Timestamp(HOLDOUT_START)]
    if verbose:
        print(f"\n=== {etf} (gating-only, conflict={conflict}) ===")
        print(f"  FULL : { _metrics_line('all', trades)}")
        print(f"  IS   : { _metrics_line('all', is_)}")
        print(f"  OOS  : { _metrics_line('all', oos)}")
        print(f"  OOS L: { _metrics_line('long', oos_long)}")
        print(f"  OOS S: { _metrics_line('short', oos_short)}")
    return r, is_, oos


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-e", "--etf", default="all")
    p.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS)
    p.add_argument("--stop-pct", type=float, default=None,
                   help="Fixed stop-loss fraction (e.g. 0.04 = 4%).")
    p.add_argument("--stop-atr", type=float, default=None,
                   help="ATR-multiple stop (e.g. 3.5).")
    p.add_argument("--no-stop", action="store_true",
                   help="Disable stop-loss (hold to exit bar).")
    p.add_argument("--conflict", default="flat",
                   choices=["flat", "long", "short"],
                   help="Resolution when both gates fire same day.")
    args = p.parse_args()

    if args.no_stop:
        sp, sak = None, None
    else:
        sp = args.stop_pct
        sak = args.stop_atr
        if sp is None and sak is None:
            # Default: try a modest emergency stop
            sp = 0.04

    etfs = [args.etf] if args.etf != "all" else ETFS
    print(f"Gating-only backtest | cost={args.cost_bps}bps | "
          f"stop={'none' if args.no_stop else (f'{sp:.3f}' if sp else f'{sak}xATR')} | "
          f"conflict={args.conflict}")

    # Aggregate per-side OOS Sharpe across ETFs
    agg = {"long": [], "short": []}
    for etf in etfs:
        out = run_one(etf, sp, sak, args.cost_bps, conflict=args.conflict)
        if isinstance(out, tuple):
            _, _, oos = out
            for side, sign in (("long", 1), ("short", -1)):
                side_oos = oos[oos["direction"] == sign]
                if len(side_oos) >= 2:
                    agg[side].append(_sharpe(side_oos["net_ret"].values))

    if len(etfs) > 1 and (agg["long"] or agg["short"]):
        print("\n" + "=" * 60)
        print("AGGREGATE OOS Sharpe (per-side, across ETFs):")
        for side in ("long", "short"):
            vals = agg[side]
            if vals:
                print(f"  {side:<6}: sum={sum(vals):+6.2f}  mean={np.mean(vals):+5.2f}  "
                      f"(n_etfs={len(vals)})")
        total = sum(agg["long"]) + sum(agg["short"])
        print(f"  {'TOTAL':<6}: {total:+6.2f}")
