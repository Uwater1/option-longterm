"""Walk-forward per-side calibration (no look-ahead in hyperparameter selection).

For each (ETF, side, fold), grid-search (threshold, conviction, stop-loss) using
ONLY train-window data (all dates strictly before the fold's test year, minus a
1-day purge gap). The selected config is then applied to the fold's test year —
that is the honest out-of-sample evaluation. Trades are stitched across all
test folds to produce a pooled walk-forward equity curve.

This eliminates the hyperparameter snooping bias of the previous single IS/OOS
split at ``HOLDOUT_START`` (which selected the best of a 36-cell grid by metrics
computed on the same window it then reported on).

Runtime signal generation remains fully causal: ``expanding_pct_masked`` and
``expanding_pct_rank`` in ``rules.py`` already use ``series.shift(1)`` so the
threshold at time *t* depends only on data strictly before *t*. Only the
SELECTION of (thr, conv, stop, mode) needed the walk-forward fix.

Output: ``daytrade/data/calibration_{mode}[_gated].json`` per mode, each
containing per-fold configs + pooled WF metrics. ``deploy.py`` then picks the
best mode per (ETF, side) by pooled WF Sharpe.
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

from . import ETFS, DEFAULT_COST_BPS
from .backtest import backtest_long_short
from .walkforward import make_yearly_folds, filter_train, filter_test
from .scores import load_features


THRESHOLD_GRID = [50.0, 60.0, 70.0, 80.0, 90.0, 95.0]
CONVICTION_GRID = [40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
MIN_TRAIN_TRADES = 20      # per-fold eligibility: enough train trades to trust the config
MIN_FOLD_ELIGIBILITY_FRAC = 0.50   # side deploys only if eligible in >=50% of folds

# Stop-loss optimisation grids (Phase 5) - wide only to prevent OOS decay
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

    def s1(x):
        return max(0.0, min(1.0, x / 3.0)) if not np.isnan(x) else 0.0
    def s2(x):
        return max(0.0, min(1.0, x / 3000.0))
    def s3(x):
        return max(0.0, min(1.0, (-x) / 1500.0)) if not np.isnan(x) else 0.0
    def s4(x):
        return max(0.0, min(1.0, (x - 0.40) / 0.25)) if not np.isnan(x) else 0.0
    def s5(n, n_base):
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


def _metrics_from_rets(rets: np.ndarray) -> dict:
    if len(rets) == 0:
        return {"n": 0, "sharpe": float("nan"), "pnl_bps": 0.0,
                "max_dd_bps": float("nan"), "win_rate": float("nan"),
                "mean_ret_bps": float("nan"), "median_bps": float("nan")}
    cum = np.insert(np.cumsum(rets), 0, 0.0)
    return {
        "n": int(len(rets)),
        "sharpe": _sharpe(rets),
        "pnl_bps": float(rets.sum() * 1e4),
        "max_dd_bps": float(np.min(cum - np.maximum.accumulate(cum)) * 1e4),
        "win_rate": float((rets > 0).mean()),
        "mean_ret_bps": float(np.mean(rets) * 1e4),
        "median_bps": float(np.median(rets) * 1e4),
    }


def _grid_search_on_window(
    etf: str, side: str, cost_bps: float, train_end: pd.Timestamp,
    mode: str = "single", gated: bool = False, verbose: bool = False,
) -> dict | None:
    """Grid-search (thr, conv, stop) scoring on the train window ending at ``train_end``.

    Returns dict with the best eligible config + train-window metrics + grid
    details, or ``None`` if no eligible config exists.

    Stage 1: grid-search (threshold, conviction) by train-window composite score.
    Stage 2: stop-loss sweep on the best (thr, conv), selected by train-window
             Sharpe (must not degrade baseline train Sharpe by more than 0.10).
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
        gated=gated,
    )
    base_trades = base["trades"]
    if len(base_trades) == 0:
        return None
    base_train = filter_train(base_trades, {"train_end": train_end})
    n_baseline_train = len(base_train)
    if n_baseline_train < MIN_TRAIN_TRADES:
        return None

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
            gated=gated,
        )
        trades = r["trades"]
        if len(trades) == 0:
            continue
        train = filter_train(trades, {"train_end": train_end})
        if len(train) < MIN_TRAIN_TRADES:
            continue
        train_rets = train["net_ret"].values
        m = _metrics_from_rets(train_rets)
        score = _score(m, n_baseline_train)
        eligible = (m["pnl_bps"] > 0) and (m["sharpe"] > 0)
        results.append({
            "threshold_pct": thr, "conviction_pct": conv,
            "n_full": len(trades), "n_train": m["n"],
            "train_sharpe": m["sharpe"], "train_pnl_bps": m["pnl_bps"],
            "train_max_dd_bps": m["max_dd_bps"], "train_win_rate": m["win_rate"],
            "train_median_bps": m["median_bps"],
            "score": score, "eligible": eligible,
        })
        if verbose:
            print(f"    {side:<5} thr={thr:>4.0f} conv={conv:>4.0f} "
                  f"n_train={m['n']:>4} S_train={m['sharpe']:+.2f} "
                  f"pnl_train={m['pnl_bps']:+.0f} sc={score:.3f}"
                  f"{'  *' if eligible else ''}")

    if not results:
        return None
    eligible = [r for r in results if r["eligible"]]
    if not eligible:
        return {"best": None, "n_eligible": 0, "n_total": len(results),
                "baseline_train_n": n_baseline_train, "grid": results}
    best = max(eligible, key=lambda r: (r["score"], r["train_sharpe"]))

    # ── Stage 2: Stop-loss sweep on best (thr, conv) ─────────────────────
    best_thr  = best["threshold_pct"]
    best_conv = best["conviction_pct"]

    # Baseline (no stop) train Sharpe for degradation check
    r_base_stop = backtest_long_short(
        etf,
        long_threshold_pct=best_thr, long_conviction_pct=best_conv,
        short_threshold_pct=best_thr, short_conviction_pct=best_conv,
        cost_bps=cost_bps,
        long_enabled=(side == "long"),
        short_enabled=(side == "short"),
        mode=mode,
        gated=gated,
    )
    base_train_stop = filter_train(r_base_stop["trades"], {"train_end": train_end})
    base_train_sharpe = (_sharpe(base_train_stop["net_ret"].values)
                         if len(base_train_stop) > 1 else float("nan"))

    stop_configs = [{"stop_type": "pct", "stop_value": sp} for sp in STOP_PCT_GRID]
    stop_configs += [{"stop_type": "atr", "stop_value": ak} for ak in STOP_ATR_GRID]

    stop_results = []
    for sc in stop_configs:
        kw = {}
        if sc["stop_type"] == "pct":
            kw["stop_pct"] = sc["stop_value"]
        else:
            kw["stop_atr_k"] = sc["stop_value"]

        r = backtest_long_short(
            etf,
            long_threshold_pct=best_thr, long_conviction_pct=best_conv,
            short_threshold_pct=best_thr, short_conviction_pct=best_conv,
            cost_bps=cost_bps,
            long_enabled=(side == "long"),
            short_enabled=(side == "short"),
            mode=mode,
            gated=gated,
            **kw,
        )
        trades = r["trades"]
        if len(trades) == 0:
            continue
        train = filter_train(trades, {"train_end": train_end})
        train_rets = train["net_ret"].values if len(train) else np.array([])
        is_sh = _sharpe(train_rets) if len(train) > 1 else float("nan")
        n_stopped = int((trades["exit_type"] == "stop").sum()) if "exit_type" in trades.columns else 0

        sr = {
            "stop_type":  sc["stop_type"],
            "stop_value": sc["stop_value"],
            "train_pnl_bps": float(train_rets.sum() * 1e4) if len(train) else 0.0,
            "train_sharpe":  is_sh,
            "n_stopped":  n_stopped,
        }
        stop_results.append(sr)

    # Selection: candidates that do not degrade train Sharpe by > 0.10
    non_degrading = []
    for sr in stop_results:
        is_sh = sr["train_sharpe"]
        is_sh_val = is_sh if (not np.isnan(is_sh) and not np.isinf(is_sh)) else -100.0
        base_val = base_train_sharpe if (not np.isnan(base_train_sharpe)
                                          and not np.isinf(base_train_sharpe)) else 0.0
        if (base_val - is_sh_val) <= 0.10:
            non_degrading.append(sr)

    if non_degrading:
        best_stop_row = max(non_degrading,
                            key=lambda x: (x["train_sharpe"] if not np.isnan(x["train_sharpe"]) else -100.0,
                                           x["train_pnl_bps"]))
        best_stop = {"stop_type": best_stop_row["stop_type"],
                     "stop_value": best_stop_row["stop_value"]}
    else:
        # Safe fallback: 4.0x ATR (or 4.0% pct if ATR unavailable)
        best_stop = {"stop_type": "atr", "stop_value": 4.0}
        if not any(sr["stop_type"] == "atr" and sr["stop_value"] == 4.0 for sr in stop_results):
            best_stop = {"stop_type": "pct", "stop_value": 0.040}

    best["stop_type"]  = best_stop["stop_type"]
    best["stop_value"] = best_stop["stop_value"]
    best["stop_results"] = stop_results
    best["base_train_sharpe_nostop"] = base_train_sharpe

    if verbose:
        st_label = (f"{best_stop['stop_value']:.3f}" if best_stop["stop_type"] == "pct"
                    else f"{best_stop['stop_value']:.1f}xATR")
        print(f"    {side:<5} stop: {st_label} "
              f"(train Sharpe w/ stop = "
              f"{next((s['train_sharpe'] for s in stop_results if s['stop_type']==best_stop['stop_type'] and s['stop_value']==best_stop['stop_value']), float('nan')):+.2f})")

    return {"best": best, "n_eligible": len(eligible), "n_total": len(results),
            "baseline_train_n": n_baseline_train, "grid": results,
            "stop_results": stop_results}


def _run_test_window(
    etf: str, side: str, cfg: dict, cost_bps: float,
    fold: dict, mode: str, gated: bool,
) -> pd.DataFrame:
    """Run backtest with the selected config over full history; filter to fold's test window."""
    if cfg is None:
        return pd.DataFrame()
    return _run_side_backtest_filtered(etf, side, cfg, cost_bps, fold, mode, gated)


def _run_side_backtest_filtered(
    etf: str, side: str, cfg: dict, cost_bps: float,
    fold: dict | None, mode: str, gated: bool,
) -> pd.DataFrame:
    """Run a single (thr, conv, stop) config; optionally filter to a fold's test window."""
    thr = cfg["threshold_pct"]
    conv = cfg["conviction_pct"]
    kw = {}
    if cfg.get("stop_type") == "pct":
        kw["stop_pct"] = cfg["stop_value"]
    elif cfg.get("stop_type") == "atr":
        kw["stop_atr_k"] = cfg["stop_value"]

    r = backtest_long_short(
        etf,
        long_threshold_pct=thr, long_conviction_pct=conv,
        short_threshold_pct=thr, short_conviction_pct=conv,
        cost_bps=cost_bps,
        long_enabled=(side == "long"),
        short_enabled=(side == "short"),
        mode=mode,
        gated=gated,
        **kw,
    )
    trades = r["trades"]
    if len(trades) == 0:
        return trades
    if fold is not None:
        trades = filter_test(trades, fold)
    return trades


def replay_side_wf_trades(
    etf: str, side: str, side_cfg: dict, cost_bps: float,
    folds: list[dict] | None = None,
) -> pd.DataFrame:
    """Replay stitched WF test-window trades from a persisted per-fold config.

    Used by ``report.py`` to rebuild the honest equity curve from the per-fold
    configs in ``calibration.json`` without re-running the grid search.

    Skips folds marked ``eligible=False`` (side was disabled for that fold).
    """
    if not side_cfg or not side_cfg.get("deployed"):
        return pd.DataFrame()
    mode = side_cfg.get("_mode", "single")
    gated = mode.endswith("+gated")
    base_mode = mode.replace("+gated", "")

    if folds is None:
        feats = load_features(etf)
        folds = make_yearly_folds(feats.index)
    fold_by_year = {f["test_year"]: f for f in folds}

    parts = []
    for fr in side_cfg.get("folds", []):
        if not fr.get("eligible"):
            continue
        fold = fold_by_year.get(fr["test_year"])
        if fold is None:
            continue
        cfg = {
            "threshold_pct": fr["threshold_pct"],
            "conviction_pct": fr["conviction_pct"],
            "stop_type": fr.get("stop_type"),
            "stop_value": fr.get("stop_value"),
        }
        trades = _run_side_backtest_filtered(etf, side, cfg, cost_bps, fold, base_mode, gated)
        if len(trades):
            trades = trades.copy()
            trades["fold_year"] = fr["test_year"]
            trades["mode"] = mode
            parts.append(trades)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts).sort_index()


def calibrate_side_walkforward(
    etf: str, side: str, cost_bps: float, mode: str = "single", gated: bool = False,
    folds: list[dict] | None = None, verbose: bool = False,
) -> dict:
    """Walk-forward calibrate one side for one ETF.

    Returns dict with per-fold configs and stitched test-window trades.
    """
    if folds is None:
        feats = load_features(etf)
        folds = make_yearly_folds(feats.index)

    fold_records = []
    stitched_trades_parts = []

    for fold in folds:
        gs = _grid_search_on_window(etf, side, cost_bps, fold["train_end"],
                                     mode=mode, gated=gated, verbose=False)
        if gs is None or gs["best"] is None:
            fold_records.append({
                "test_year": fold["test_year"],
                "eligible": False, "reason": "no eligible config in train window",
                "n_train_baseline": 0,
            })
            continue

        best = gs["best"]
        # Run the selected config on the test window
        test_trades = _run_test_window(etf, side, best, cost_bps, fold, mode=mode, gated=gated)
        test_rets = test_trades["net_ret"].values if len(test_trades) else np.array([])
        test_m = _metrics_from_rets(test_rets)

        # Tag trades with fold metadata
        if len(test_trades):
            test_trades = test_trades.copy()
            test_trades["fold_year"] = fold["test_year"]
            test_trades["mode"] = f"{mode}{'+' if gated else ''}{'gated' if gated else ''}"
            stitched_trades_parts.append(test_trades)

        clean_best = {k: v for k, v in best.items() if k != "stop_results"}
        fold_records.append({
            "test_year": fold["test_year"],
            "eligible": True,
            "threshold_pct": clean_best["threshold_pct"],
            "conviction_pct": clean_best["conviction_pct"],
            "stop_type": clean_best.get("stop_type"),
            "stop_value": clean_best.get("stop_value"),
            "train_sharpe": clean_best["train_sharpe"],
            "train_pnl_bps": clean_best["train_pnl_bps"],
            "train_n": clean_best["n_train"],
            "train_win_rate": clean_best["train_win_rate"],
            "n_eligible_grid": gs["n_eligible"],
            "n_total_grid": gs["n_total"],
            "test_n": test_m["n"],
            "test_sharpe": test_m["sharpe"],
            "test_pnl_bps": test_m["pnl_bps"],
            "test_max_dd_bps": test_m["max_dd_bps"],
            "test_win_rate": test_m["win_rate"],
            "test_median_bps": test_m["median_bps"],
        })
        if verbose:
            st_lbl = (f"{clean_best.get('stop_value', 0):.3f}"
                      if clean_best.get("stop_type") == "pct"
                      else f"{clean_best.get('stop_value', 0):.1f}xATR")
            print(f"    {side:<5} fold={fold['test_year']} "
                  f"thr={clean_best['threshold_pct']:.0f} conv={clean_best['conviction_pct']:.0f} "
                  f"stop={st_lbl} | train S={clean_best['train_sharpe']:+.2f} "
                  f"pnl={clean_best['train_pnl_bps']:+.0f} | "
                  f"test S={test_m['sharpe']:+.2f} pnl={test_m['pnl_bps']:+.0f} n={test_m['n']}")

    stitched = (pd.concat(stitched_trades_parts).sort_index()
                if stitched_trades_parts else pd.DataFrame())
    pooled = _metrics_from_rets(stitched["net_ret"].values) if len(stitched) else _metrics_from_rets(np.array([]))

    n_folds = len(folds)
    n_eligible = sum(1 for fr in fold_records if fr.get("eligible"))
    majority_eligible = n_eligible / max(n_folds, 1) >= MIN_FOLD_ELIGIBILITY_FRAC
    deployed = bool(majority_eligible and pooled["sharpe"] > 0)

    return {
        "etf": etf,
        "side": side,
        "mode": mode,
        "gated": gated,
        "deployed": deployed,
        "pooled_wf_sharpe": pooled["sharpe"],
        "pooled_wf_pnl_bps": pooled["pnl_bps"],
        "pooled_wf_max_dd_bps": pooled["max_dd_bps"],
        "pooled_wf_win_rate": pooled["win_rate"],
        "pooled_wf_n": pooled["n"],
        "pooled_wf_median_bps": pooled["median_bps"],
        "n_folds": n_folds,
        "n_folds_eligible": n_eligible,
        "majority_eligible": majority_eligible,
        "folds": fold_records,
        "stitched_trades": stitched,
    }


def calibrate_etf_walkforward(
    etf: str, cost_bps: float = DEFAULT_COST_BPS, mode: str = "single",
    gated: bool = False, folds: list[dict] | None = None, verbose: bool = True,
) -> dict:
    """Walk-forward calibrate long & short for one ETF, one mode."""
    if folds is None:
        feats = load_features(etf)
        folds = make_yearly_folds(feats.index)
    if verbose:
        gate_tag = "+gated" if gated else ""
        print(f"\n=== {etf} (mode={mode}{gate_tag}, {len(folds)} folds) ===")
    long_res = calibrate_side_walkforward(etf, "long", cost_bps, mode=mode, gated=gated,
                                          folds=folds, verbose=verbose)
    short_res = calibrate_side_walkforward(etf, "short", cost_bps, mode=mode, gated=gated,
                                           folds=folds, verbose=verbose)

    if verbose:
        for label, res in (("LONG", long_res), ("SHORT", short_res)):
            if res["deployed"]:
                print(f"  {label:<5} DEPLOYED  pooled_WF S={res['pooled_wf_sharpe']:+.2f} "
                      f"pnl={res['pooled_wf_pnl_bps']:+.0f}bps n={res['pooled_wf_n']} "
                      f"(eligible {res['n_folds_eligible']}/{res['n_folds']} folds)")
            else:
                print(f"  {label:<5} DISABLED  "
                      f"(eligible {res['n_folds_eligible']}/{res['n_folds']} folds, "
                      f"pooled_WF S={res['pooled_wf_sharpe']:+.2f})")
    return {"etf": etf, "long": long_res, "short": short_res}


def _calibrate_etf_mode_wrapper(args):
    etf, cost_bps, mode, gated = args
    return (etf, mode, gated), calibrate_etf_walkforward(
        etf, cost_bps=cost_bps, mode=mode, gated=gated, verbose=False)


def calibrate_all(cost_bps: float = DEFAULT_COST_BPS, verbose: bool = True,
                  mode: str = "single", gated: bool = False) -> dict:
    """Walk-forward calibrate all ETFs for one (mode, gated) combo.

    Writes ``calibration_{mode}[_gated].json`` with per-fold configs + pooled WF
    metrics. Also mirrors to ``calibration.json`` for backward compat.
    """
    if verbose:
        gate_tag = "+gated" if gated else ""
        print(f"Walk-forward calibrating {len(ETFS)} ETFs (mode={mode}{gate_tag})...")

    # Pre-compute folds per ETF (data starts vary — 588000ETF starts 2021)
    folds_per_etf = {}
    for etf in ETFS:
        feats = load_features(etf)
        folds_per_etf[etf] = make_yearly_folds(feats.index)

    tasks = [(etf, cost_bps, mode, gated) for etf in ETFS]
    out = {}
    with ProcessPoolExecutor() as executor:
        results = executor.map(_calibrate_etf_mode_wrapper, tasks)
        for key, res in results:
            out[key] = res
            if verbose:
                etf, _, _ = key
                print(f"  Finished {etf}")

    # Write per-mode file
    OUT_PATH.parent.mkdir(exist_ok=True)
    gate_suffix = "_gated" if gated else ""
    mode_path = OUT_PATH.parent / f"calibration_{mode}{gate_suffix}.json"

    compact = {
        "cost_bps": cost_bps,
        "mode": mode,
        "gated": gated,
        "walk_forward": True,
        "min_fold_eligibility_frac": MIN_FOLD_ELIGIBILITY_FRAC,
        "results": {},
    }
    for key, v in out.items():
        etf, m, g = key
        assert m == mode and g == gated
        compact["results"][etf] = {
            "long": _side_to_compact(v["long"]),
            "short": _side_to_compact(v["short"]),
        }
    with open(mode_path, "w") as f:
        json.dump(compact, f, indent=2, default=str)
    if not gated:
        with open(OUT_PATH, "w") as f:
            json.dump(compact, f, indent=2, default=str)
        print(f"\nSaved → {mode_path} (and mirror → {OUT_PATH})")
    else:
        print(f"\nSaved → {mode_path}")

    _print_summary(out, mode, gated)
    return out


def _side_to_compact(res: dict) -> dict:
    """Drop heavy 'stitched_trades' (DataFrame) for JSON serialisation."""
    return {k: v for k, v in res.items() if k != "stitched_trades"}


def _print_summary(out: dict, mode: str, gated: bool):
    print("\n" + "=" * 96)
    gate_tag = "+gated" if gated else ""
    print(f"{'ETF':<12} {'LONG (WF pooled)':<42} {'SHORT (WF pooled)':<42}")
    print("-" * 96)
    for key, v in out.items():
        etf, _, _ = key
        l = v["long"]; s = v["short"]
        def _row(r):
            if not r["deployed"]:
                return f"DISABLED (elig {r['n_folds_eligible']}/{r['n_folds']}, S={r['pooled_wf_sharpe']:+.2f})"
            return (f"S={r['pooled_wf_sharpe']:+.2f} pnl={r['pooled_wf_pnl_bps']:+.0f} "
                    f"n={r['pooled_wf_n']} elig {r['n_folds_eligible']}/{r['n_folds']}")
        print(f"{etf:<12} {_row(l):<42} {_row(s):<42}")
    print("=" * 96)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS)
    p.add_argument("--mode", default="single", choices=["single", "hybrid", "dual"],
                   help="single=frozen single-model score (default); "
                        "hybrid=single×dual combined conviction; "
                        "dual=independent dual execution with rank normalisation")
    p.add_argument("--gated", action="store_true",
                   help="Apply the day-model gating model as a post-hoc veto.")
    p.add_argument("--sweep-gated", action="store_true",
                   help="Run both ungated and gated calibrations (writes both files).")
    args = p.parse_args()

    if args.sweep_gated:
        calibrate_all(cost_bps=args.cost_bps, verbose=True, mode=args.mode, gated=False)
        calibrate_all(cost_bps=args.cost_bps, verbose=True, mode=args.mode, gated=True)
    else:
        calibrate_all(cost_bps=args.cost_bps, verbose=True, mode=args.mode, gated=args.gated)
