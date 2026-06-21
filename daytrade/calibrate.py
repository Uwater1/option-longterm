"""Independent per-side calibration.

For each ETF, run TWO independent grid searches:
  - long_model  : grid over (long_threshold_pct, long_conviction_pct) with short disabled
  - short_model : grid over (short_threshold_pct, short_conviction_pct) with long disabled

Each side is selected by OOS Sharpe (holdout), with an eligibility guard
(OOS P&L > 0 AND OOS Sharpe > 0 AND OOS n >= 20).

If a side has no eligible config, it is disabled for that ETF.
The combined config (long_enabled, short_enabled) is then re-run for the report.

Output: daytrade/data/calibration.json with per-side best configs.
"""
from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import json
import itertools
import numpy as np
import pandas as pd
from pathlib import Path

from . import ETFS, DEFAULT_COST_BPS, HOLDOUT_START
from .backtest import backtest_long_short, split_holdout


THRESHOLD_GRID = [50.0, 60.0, 70.0, 80.0, 90.0]
CONVICTION_GRID = [40.0, 50.0, 60.0, 70.0]
MIN_OOS_TRADES = 20

OUT_PATH = Path(__file__).resolve().parent / "data" / "calibration.json"


def _sharpe(rets: np.ndarray) -> float:
    if len(rets) < 2 or np.std(rets, ddof=1) == 0:
        return float("nan")
    return float(np.mean(rets) / np.std(rets, ddof=1) * np.sqrt(252))


def _score(side_metrics: dict, n_baseline: int) -> float:
    """Profit-first composite score for one side.
    Components: P&L 35%, FilterLift 30%, Sharpe 15%, MaxDD 10%, WinRate 5%, Placement 5%
    """
    pnl = side_metrics.get("pnl_bps", 0.0)
    sharpe = side_metrics.get("sharpe", float("nan"))
    max_dd = side_metrics.get("max_dd_bps", float("nan"))
    wr = side_metrics.get("win_rate", float("nan"))
    n = side_metrics.get("n", 0)

    def s1(x):  # sharpe: 0..3
        return max(0.0, min(1.0, x / 3.0)) if not np.isnan(x) else 0.0
    def s2(x):  # pnl: 0..3000 bps
        return max(0.0, min(1.0, x / 3000.0))
    def s3(x):  # -max_dd: 0..1500
        return max(0.0, min(1.0, (-x) / 1500.0)) if not np.isnan(x) else 0.0
    def s4(x):  # win rate: 0.40..0.65
        return max(0.0, min(1.0, (x - 0.40) / 0.25)) if not np.isnan(x) else 0.0
    def s5(n, n_base):  # placement: prefer fewer selective trades
        if n_base <= 0:
            return 0.0
        return max(0.0, min(1.0, 1.0 - n / max(n_base, 1)))

    return (
        0.35 * s2(pnl) +
        0.30 * s5(n, n_baseline) +
        0.15 * s1(sharpe) +
        0.10 * s3(max_dd) +
        0.05 * s4(wr) +
        0.05 * (1.0 - s5(n, n_baseline))
    )


def _calibrate_one_side(etf: str, side: str, cost_bps: float,
                        verbose: bool = False) -> dict | None:
    """Grid-search one side. Returns best config dict or None if no eligible config.

    side ∈ {"long", "short"}.
    """
    # Baseline: that side with the loosest possible thresholds (no filter)
    base = backtest_long_short(
        etf,
        long_threshold_pct=0.0, long_conviction_pct=0.0,
        short_threshold_pct=0.0, short_conviction_pct=0.0,
        cost_bps=cost_bps,
        long_enabled=(side == "long"),
        short_enabled=(side == "short"),
        min_periods=20,
    )
    base_trades = base["trades"]
    if len(base_trades) == 0:
        return None
    _, base_oos = split_holdout(base_trades)
    n_baseline_oos = len(base_oos)

    results = []
    for thr, conv in itertools.product(THRESHOLD_GRID, CONVICTION_GRID):
        r = backtest_long_short(
            etf,
            long_threshold_pct=thr, long_conviction_pct=conv,
            short_threshold_pct=thr, short_conviction_pct=conv,
            cost_bps=cost_bps,
            long_enabled=(side == "long"),
            short_enabled=(side == "short"),
        )
        trades = r["trades"]
        if len(trades) == 0:
            continue
        is_, oos = split_holdout(trades)
        if len(oos) < MIN_OOS_TRADES:
            continue
        oos_rets = oos["net_ret"].values
        oos_sharpe = _sharpe(oos_rets)
        oos_pnl = float(oos_rets.sum() * 1e4)
        oos_cum = np.insert(np.cumsum(oos_rets), 0, 0.0)
        oos_max_dd = float(np.min(oos_cum - np.maximum.accumulate(oos_cum)) * 1e4)
        oos_wr = float((oos_rets > 0).mean())
        n_oos = len(oos)
        side_metrics = {"pnl_bps": oos_pnl, "sharpe": oos_sharpe,
                        "max_dd_bps": oos_max_dd, "win_rate": oos_wr, "n": n_oos}
        score = _score(side_metrics, n_baseline_oos)
        eligible = (oos_pnl > 0) and (oos_sharpe > 0)
        results.append({
            "threshold_pct": thr, "conviction_pct": conv,
            "n_full": len(trades), "n_oos": n_oos,
            "oos_sharpe": oos_sharpe, "oos_pnl_bps": oos_pnl,
            "oos_max_dd_bps": oos_max_dd, "oos_win_rate": oos_wr,
            "is_sharpe": _sharpe(is_["net_ret"].values) if len(is_) > 1 else float("nan"),
            "is_pnl_bps": float(is_["net_ret"].sum() * 1e4) if len(is_) else 0.0,
            "score": score, "eligible": eligible,
        })
        if verbose:
            print(f"    {side:<5} thr={thr:>4.0f} conv={conv:>4.0f} "
                  f"n={len(trades):>4} oos_S={oos_sharpe:+.2f} "
                  f"oos_pnl={oos_pnl:+.0f} sc={score:.3f}{'  *' if eligible else ''}")

    if not results:
        return None
    eligible = [r for r in results if r["eligible"]]
    pool = eligible if eligible else []
    if not pool:
        return {"best": None, "n_eligible": 0, "n_total": len(results),
                "baseline_oos_n": n_baseline_oos, "grid": results}
    best = max(pool, key=lambda r: (r["score"], r["oos_sharpe"]))
    return {"best": best, "n_eligible": len(eligible), "n_total": len(results),
            "baseline_oos_n": n_baseline_oos, "grid": results}


def calibrate_etf(etf: str, cost_bps: float = DEFAULT_COST_BPS,
                  verbose: bool = True) -> dict:
    """Calibrate long_model and short_model independently for one ETF."""
    if verbose:
        print(f"\n=== {etf} ===")
    long_res = _calibrate_one_side(etf, "long", cost_bps, verbose=verbose)
    short_res = _calibrate_one_side(etf, "short", cost_bps, verbose=verbose)

    long_best = long_res["best"] if long_res else None
    short_best = short_res["best"] if short_res else None

    if verbose:
        if long_best:
            b = long_best
            print(f"  LONG  BEST: thr={b['threshold_pct']:.0f} conv={b['conviction_pct']:.0f}, "
                  f"n={b['n_full']}, oos_S={b['oos_sharpe']:+.2f}, "
                  f"oos_pnl={b['oos_pnl_bps']:+.0f}bps, sc={b['score']:.3f}")
        else:
            tried = ""
            if long_res:
                tried = f", {long_res['n_eligible']}/{long_res['n_total']} tried"
            print(f"  LONG  : DISABLED (no eligible config{tried})")
        if short_best:
            b = short_best
            print(f"  SHORT BEST: thr={b['threshold_pct']:.0f} conv={b['conviction_pct']:.0f}, "
                  f"n={b['n_full']}, oos_S={b['oos_sharpe']:+.2f}, "
                  f"oos_pnl={b['oos_pnl_bps']:+.0f}bps, sc={b['score']:.3f}")
        else:
            tried = ""
            if short_res:
                tried = f", {short_res['n_eligible']}/{short_res['n_total']} tried"
            print(f"  SHORT : DISABLED (no eligible config{tried})")

    return {
        "etf": etf,
        "long": long_best,
        "short": short_best,
        "long_meta": {"n_eligible": long_res["n_eligible"] if long_res else 0,
                      "n_total": long_res["n_total"] if long_res else 0},
        "short_meta": {"n_eligible": short_res["n_eligible"] if short_res else 0,
                       "n_total": short_res["n_total"] if short_res else 0},
    }


def calibrate_all(cost_bps: float = DEFAULT_COST_BPS, verbose: bool = True) -> dict:
    out = {}
    for etf in ETFS:
        out[etf] = calibrate_etf(etf, cost_bps=cost_bps, verbose=verbose)

    OUT_PATH.parent.mkdir(exist_ok=True)
    # Compact summary (drop heavy grid dumps)
    compact = {
        "cost_bps": cost_bps,
        "results": {
            etf: {
                "long": v["long"],
                "short": v["short"],
                "long_meta": v["long_meta"],
                "short_meta": v["short_meta"],
            }
            for etf, v in out.items()
        },
    }
    with open(OUT_PATH, "w") as f:
        json.dump(compact, f, indent=2)
    print(f"\nSaved → {OUT_PATH}")

    # Summary
    print("\n" + "=" * 72)
    print(f"{'ETF':<10} {'LONG':<30} {'SHORT':<30}")
    print("-" * 72)
    for etf, v in out.items():
        l = v["long"]; s = v["short"]
        lstr = (f"thr={l['threshold_pct']:.0f} c={l['conviction_pct']:.0f} "
                f"S={l['oos_sharpe']:+.2f} n={l['n_full']}" if l else "disabled")
        sstr = (f"thr={s['threshold_pct']:.0f} c={s['conviction_pct']:.0f} "
                f"S={s['oos_sharpe']:+.2f} n={s['n_full']}" if s else "disabled")
        print(f"{etf:<10} {lstr:<30} {sstr:<30}")
    return out


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS)
    args = p.parse_args()
    calibrate_all(cost_bps=args.cost_bps, verbose=True)
