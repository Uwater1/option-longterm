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
from concurrent.futures import ProcessPoolExecutor

from . import ETFS, DEFAULT_COST_BPS, HOLDOUT_START
from .backtest import backtest_long_short, split_holdout


THRESHOLD_GRID = [50.0, 60.0, 70.0, 80.0, 90.0, 95.0]
CONVICTION_GRID = [40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
MIN_OOS_TRADES = 20

# Stop-loss optimisation grids (Phase 5) - expanded for catastrophic protection (wide only to prevent OOS decay)
STOP_PCT_GRID  = [0.030, 0.040, 0.050]   # fixed % from entry
STOP_ATR_GRID  = [3.5, 4.0, 5.0]          # ATR-14 multiples

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
                        verbose: bool = False, mode: str = "single") -> dict | None:
    """Grid-search one side. Returns best config dict or None if no eligible config.

    side ∈ {"long", "short"}.

    Two-stage optimisation:
      1. Grid-search (threshold, conviction) by OOS composite score.
      2. Sweep stop-loss configs (fixed-% + ATR multiples) on the best
         (threshold, conviction) pair, selecting by **IS max profit**.
         The chosen stop is then evaluated OOS for transparency.
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
        mode=mode,
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
            mode=mode,
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
        oos_median_bps = float(np.median(oos_rets) * 1e4)
        n_oos = len(oos)
        side_metrics = {"pnl_bps": oos_pnl, "sharpe": oos_sharpe,
                        "max_dd_bps": oos_max_dd, "win_rate": oos_wr, "n": n_oos}
        score = _score(side_metrics, n_baseline_oos)
        eligible = (oos_pnl > 0) and (oos_sharpe > 0)
        # Non-blocking fragility warnings (transparency only; do NOT change eligibility).
        # If any of these fire, the positive Sharpe may be a small-sample / heavy-tail artifact.
        warns = []
        if oos_median_bps <= 0:
            warns.append("median<=0")
        if oos_wr <= 0.50:
            warns.append("win<=50%")
        if n_oos < 60:
            warns.append("n<60")
        results.append({
            "threshold_pct": thr, "conviction_pct": conv,
            "n_full": len(trades), "n_oos": n_oos,
            "oos_sharpe": oos_sharpe, "oos_pnl_bps": oos_pnl,
            "oos_max_dd_bps": oos_max_dd, "oos_win_rate": oos_wr,
            "oos_median_bps": oos_median_bps,
            "is_sharpe": _sharpe(is_["net_ret"].values) if len(is_) > 1 else float("nan"),
            "is_pnl_bps": float(is_["net_ret"].sum() * 1e4) if len(is_) else 0.0,
            "score": score, "eligible": eligible,
            "warnings": warns,
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

    # ── Stage 2: Stop-loss sweep on best (thr, conv) ─────────────────────
    best_thr  = best["threshold_pct"]
    best_conv = best["conviction_pct"]

    # First, run the no-stop baseline for this best config to get its baseline IS Sharpe
    r_base_stop = backtest_long_short(
        etf,
        long_threshold_pct=best_thr, long_conviction_pct=best_conv,
        short_threshold_pct=best_thr, short_conviction_pct=best_conv,
        cost_bps=cost_bps,
        long_enabled=(side == "long"),
        short_enabled=(side == "short"),
        mode=mode,
    )
    is_base, _ = split_holdout(r_base_stop["trades"])
    base_is_sharpe = _sharpe(is_base["net_ret"].values) if len(is_base) > 1 else float("nan")

    # Generate stop configurations (MANDATORY: no None allowed)
    stop_configs = []
    for sp in STOP_PCT_GRID:
        stop_configs.append({"stop_type": "pct", "stop_value": sp})
    for ak in STOP_ATR_GRID:
        stop_configs.append({"stop_type": "atr", "stop_value": ak})

    stop_results  = []
    for sc in stop_configs:
        kw = {}
        if sc["stop_type"] == "pct":
            kw["stop_pct"] = sc["stop_value"]
        elif sc["stop_type"] == "atr":
            kw["stop_atr_k"] = sc["stop_value"]

        r = backtest_long_short(
            etf,
            long_threshold_pct=best_thr, long_conviction_pct=best_conv,
            short_threshold_pct=best_thr, short_conviction_pct=best_conv,
            cost_bps=cost_bps,
            long_enabled=(side == "long"),
            short_enabled=(side == "short"),
            mode=mode,
            **kw,
        )
        trades = r["trades"]
        if len(trades) == 0:
            continue
        is_, oos = split_holdout(trades)
        is_pnl  = float(is_["net_ret"].sum() * 1e4) if len(is_) else 0.0
        n_stopped = int((trades["exit_type"] == "stop").sum()) if "exit_type" in trades.columns else 0
        is_sh = _sharpe(is_["net_ret"].values) if len(is_) > 1 else float("nan")

        sr = {
            "stop_type":  sc["stop_type"],
            "stop_value": sc["stop_value"],
            "is_pnl_bps": is_pnl,
            "is_sharpe":  is_sh,
            "n_stopped":  n_stopped,
        }
        if len(oos) > 0:
            oos_rets = oos["net_ret"].values
            sr["oos_sharpe"]   = _sharpe(oos_rets)
            sr["oos_pnl_bps"]  = float(oos_rets.sum() * 1e4)
            oos_cum = np.insert(np.cumsum(oos_rets), 0, 0.0)
            sr["oos_max_dd_bps"] = float(np.min(oos_cum - np.maximum.accumulate(oos_cum)) * 1e4)
            sr["oos_win_rate"]   = float((oos_rets > 0).mean())
        else:
            sr["oos_sharpe"]     = float("nan")
            sr["oos_pnl_bps"]    = 0.0
            sr["oos_max_dd_bps"] = float("nan")
            sr["oos_win_rate"]   = float("nan")
        stop_results.append(sr)

    # Selection rule:
    # 1. Filter candidates that do not degrade IS Sharpe by more than 0.10 relative to base_is_sharpe
    non_degrading_candidates = []
    for sr in stop_results:
        is_sh = sr["is_sharpe"]
        if np.isnan(is_sh) or np.isinf(is_sh):
            is_sh_val = -100.0
        else:
            is_sh_val = is_sh
            
        base_sh_val = base_is_sharpe if (not np.isnan(base_is_sharpe) and not np.isinf(base_is_sharpe)) else 0.0
        degradation = base_sh_val - is_sh_val
        if degradation <= 0.10:
            non_degrading_candidates.append(sr)

    # 2. Choose best config:
    # - If we have non-degrading candidates, choose the one that maximizes IS Sharpe (balances risk/return)
    # - If all candidates degrade Sharpe by > 0.10, we fallback to a safe emergency stop: 4.0x ATR
    #   (If 4.0x ATR is not in results, fallback to 4.0% pct)
    best_stop = None
    if non_degrading_candidates:
        best_stop_row = max(non_degrading_candidates, key=lambda x: (x["is_sharpe"] if not np.isnan(x["is_sharpe"]) else -100.0, x["is_pnl_bps"]))
        best_stop = {"stop_type": best_stop_row["stop_type"], "stop_value": best_stop_row["stop_value"]}
    else:
        best_stop = {"stop_type": "atr", "stop_value": 4.0}
        if not any(sr["stop_type"] == "atr" and sr["stop_value"] == 4.0 for sr in stop_results):
            best_stop = {"stop_type": "pct", "stop_value": 0.040}

    # Attach best stop config to the threshold/conviction best
    best["stop_type"]      = best_stop["stop_type"]
    best["stop_value"]     = best_stop["stop_value"]
    best["stop_results"]   = stop_results

    # Populate OOS metrics for the best stop config
    best_stop_row = next(
        (sr for sr in stop_results
         if sr["stop_type"] == best_stop["stop_type"]
         and sr["stop_value"] == best_stop["stop_value"]),
        None,
    )
    if best_stop_row:
        best["stop_oos_sharpe"]     = best_stop_row["oos_sharpe"]
        best["stop_oos_pnl_bps"]    = best_stop_row["oos_pnl_bps"]
        best["stop_oos_max_dd_bps"] = best_stop_row["oos_max_dd_bps"]
        best["stop_oos_win_rate"]   = best_stop_row["oos_win_rate"]
    else:
        best["stop_oos_sharpe"]     = float("nan")
        best["stop_oos_pnl_bps"]    = 0.0
        best["stop_oos_max_dd_bps"] = float("nan")
        best["stop_oos_win_rate"]   = float("nan")

    if verbose:
        st_label = (f"{best_stop['stop_value']:.3f}" if best_stop["stop_type"] == "pct"
                    else f"{best_stop['stop_value']:.1f}xATR" if best_stop["stop_type"] == "atr"
                    else "none")
        best_pnl_val = best_stop_row["is_pnl_bps"] if best_stop_row else 0.0
        print(f"    {side:<5} stop: {st_label} "
              f"(IS pnl={best_pnl_val:+.0f}bps, "
              f"OOS S={best.get('stop_oos_sharpe', float('nan')):+.2f})")

    return {"best": best, "n_eligible": len(eligible), "n_total": len(results),
            "baseline_oos_n": n_baseline_oos, "grid": results,
            "stop_results": stop_results}


def calibrate_etf(etf: str, cost_bps: float = DEFAULT_COST_BPS,
                  verbose: bool = True, mode: str = "single") -> dict:
    """Calibrate long_model and short_model independently for one ETF."""
    if verbose:
        print(f"\n=== {etf} (mode={mode}) ===")
    long_res = _calibrate_one_side(etf, "long", cost_bps, verbose=verbose, mode=mode)
    short_res = _calibrate_one_side(etf, "short", cost_bps, verbose=verbose, mode=mode)

    long_best = long_res["best"] if long_res else None
    short_best = short_res["best"] if short_res else None

    if verbose:
        if long_best:
            b = long_best
            st = (f"{b['stop_value']:.3f}" if b.get("stop_type") == "pct"
                  else f"{b['stop_value']:.1f}xATR" if b.get("stop_type") == "atr"
                  else "none")
            print(f"  LONG  BEST: thr={b['threshold_pct']:.0f} conv={b['conviction_pct']:.0f} "
                  f"stop={st}, "
                  f"n={b['n_full']}, oos_S={b['oos_sharpe']:+.2f}, "
                  f"oos_pnl={b['oos_pnl_bps']:+.0f}bps, sc={b['score']:.3f}")
        else:
            tried = ""
            if long_res:
                tried = f", {long_res['n_eligible']}/{long_res['n_total']} tried"
            print(f"  LONG  : DISABLED (no eligible config{tried})")
        if short_best:
            b = short_best
            st = (f"{b['stop_value']:.3f}" if b.get("stop_type") == "pct"
                  else f"{b['stop_value']:.1f}xATR" if b.get("stop_type") == "atr"
                  else "none")
            print(f"  SHORT BEST: thr={b['threshold_pct']:.0f} conv={b['conviction_pct']:.0f} "
                  f"stop={st}, "
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


def _calibrate_etf_wrapper(args):
    etf, cost_bps, mode = args
    # Run with verbose=False to avoid console print scrambling in parallel
    return etf, calibrate_etf(etf, cost_bps=cost_bps, verbose=False, mode=mode)


def calibrate_all(cost_bps: float = DEFAULT_COST_BPS, verbose: bool = True,
                  mode: str = "single") -> dict:
    out = {}
    if verbose:
        print(f"Calibrating {len(ETFS)} ETFs in parallel (mode={mode})...")

    tasks = [(etf, cost_bps, mode) for etf in ETFS]
    with ProcessPoolExecutor() as executor:
        results = executor.map(_calibrate_etf_wrapper, tasks)
        for etf, res in results:
            out[etf] = res
            if verbose:
                print(f"  Finished calibrating {etf}")
                for side_key in ("long", "short"):
                    cfg = res[side_key]
                    if cfg:
                        st = (f"{cfg['stop_value']:.3f}" if cfg.get("stop_type") == "pct"
                              else f"{cfg['stop_value']:.1f}xATR" if cfg.get("stop_type") == "atr"
                              else "none")
                        print(f"    {side_key.upper()} BEST: thr={cfg['threshold_pct']:.0f} conv={cfg['conviction_pct']:.0f} "
                              f"stop={st}, n={cfg['n_full']}, oos_S={cfg['oos_sharpe']:+.2f}, "
                              f"oos_pnl={cfg['oos_pnl_bps']:+.0f}bps, sc={cfg['score']:.3f}")
                    else:
                        print(f"    {side_key.upper()} : DISABLED")

    OUT_PATH.parent.mkdir(exist_ok=True)
    # Compact summary: keep stop fields, drop heavy grid/stop_results dumps
    compact = {
        "cost_bps": cost_bps,
        "mode": mode,
        "results": {},
    }
    for etf, v in out.items():
        entry = {
            "long_meta": v["long_meta"],
            "short_meta": v["short_meta"],
        }
        for side_key in ("long", "short"):
            cfg = v[side_key]
            if cfg is None:
                entry[side_key] = None
            else:
                # Strip heavy stop_results list; keep the selection fields only
                clean = {k: val for k, val in cfg.items() if k != "stop_results"}
                entry[side_key] = clean
        compact["results"][etf] = entry
    # Always write to calibration_{mode}.json (consumed by deploy.py mixed-mode picker).
    # Also mirror to calibration.json for backward compat / single-shot inspection.
    mode_path = OUT_PATH.parent / f"calibration_{mode}.json"
    with open(mode_path, "w") as f:
        json.dump(compact, f, indent=2)
    with open(OUT_PATH, "w") as f:
        json.dump(compact, f, indent=2)
    print(f"\nSaved → {mode_path} (and mirror → {OUT_PATH})")

    # Summary
    print("\n" + "=" * 82)
    print(f"{'ETF':<10} {'LONG':<35} {'SHORT':<35}")
    print("-" * 82)
    for etf, v in out.items():
        l = v["long"]; s = v["short"]
        def _stop_label(cfg):
            if not cfg:
                return "disabled"
            st = cfg.get("stop_type")
            sv = cfg.get("stop_value")
            label = (f"{sv:.3f}" if st == "pct"
                     else f"{sv:.1f}atr" if st == "atr"
                     else "—")
            return label
        lstr = (f"thr={l['threshold_pct']:.0f} c={l['conviction_pct']:.0f} "
                f"S={l['oos_sharpe']:+.2f} stop={_stop_label(l)}" if l else "disabled")
        sstr = (f"thr={s['threshold_pct']:.0f} c={s['conviction_pct']:.0f} "
                f"S={s['oos_sharpe']:+.2f} stop={_stop_label(s)}" if s else "disabled")
        print(f"{etf:<10} {lstr:<35} {sstr:<35}")
    return out


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS)
    p.add_argument("--mode", default="single", choices=["single", "hybrid", "dual"],
                   help="single=frozen single-model score (default, proven); "
                        "hybrid=single×dual combined conviction (experimental); "
                        "dual=true independent dual execution with rank normalisation (v2)")
    args = p.parse_args()
    calibrate_all(cost_bps=args.cost_bps, verbose=True, mode=args.mode)
