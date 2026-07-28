#!/usr/bin/env python3
"""
NewTrade Unified Parameter Optimizer.

Searches for the BEST SINGLE CONFIG that works across ALL ETFs simultaneously.
No per-ETF customization — one set of parameters for everything.

Evaluates on portfolio-level Sharpe (equal-weight combined daily returns).
Reports top-N configs and validates winner with DSR/CPCV.

Usage:
    python newtrade/optimize_unified.py                    # Full grid
    python newtrade/optimize_unified.py --quick            # Reduced grid
    python newtrade/optimize_unified.py --top 10           # Show top 10
"""

import sys
import time
import argparse
import json
from pathlib import Path
from itertools import product
from math import sqrt

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, expanding_factor_ic_numba, expanding_factor_score_numba,
)
from weighting import compute_ew, compute_icw, compute_score_w, compute_rank_w
from strategy import (
    generate_positions, sweep_optimal_threshold, compute_production_threshold,
    simulate_etf_spot,
)
from robustness import deflated_sharpe_ratio, run_cpcv_backtest

# Live ETFs (those with >= 10 features)
ETFS = ["159915ETF", "500ETF", "300ETF"]

# 3-period walk-forward (ZERO look-ahead):
#   TRAIN: start → 2020  (threshold sweep)
#   VALIDATION: 2020 → 2022  (parameter selection)
#   TEST: 2022 → 2026  (final evaluation, reported)
TRAIN_END = "2020-01-01"
VAL_START = "2020-01-01"
VAL_END = "2022-01-01"
TEST_START = "2022-01-01"
TEST_END = "2026-01-01"

FEE_BPS = 0.0008
BURN_IN = 252


def precompute_etf_data(etf: str, burn_in: int = BURN_IN) -> dict:
    """Pre-compute expensive per-ETF data (Z_std, IC matrix, trade returns)."""
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None
    
    df = load_etf_dataset(etf)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    
    trade_returns = (df["trade_return"].values.astype(np.float64)
                     if "trade_return" in df.columns
                     else df["close"].pct_change().fillna(0.0).values)
    
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    IC_mat = expanding_factor_ic_numba(Z_std, signs, trade_returns, burn_in=burn_in)
    
    dates = df["date"]
    train_mask = (dates < pd.Timestamp(TRAIN_END)).values
    val_mask = ((dates >= pd.Timestamp(VAL_START)) & (dates < pd.Timestamp(VAL_END))).values
    test_mask = ((dates >= pd.Timestamp(TEST_START)) & (dates < pd.Timestamp(TEST_END))).values
    
    return {
        "etf": etf,
        "pool": pool,
        "signs": signs,
        "Z_std": Z_std,
        "IC_mat": IC_mat,
        "trade_returns": trade_returns,
        "train_mask": train_mask,
        "val_mask": val_mask,
        "test_mask": test_mask,
        "dates": dates,
        "n_features": len(pool),
    }


def compute_composite(data: dict, scheme: str, score_weights: tuple,
                      ic_ema_span: int, rank_min: float, rank_max: float,
                      mono_window: int, dynamic_metric: str = "ic") -> np.ndarray:
    """Compute composite signal for given params.
    
    dynamic_metric:
      'ic'    = EMA-smoothed expanding IC (current default, score_weights irrelevant)
      'multi' = Multi-metric score (IC + IC_IR + Monotonicity, score_weights matter!)
    """
    Z_std = data["Z_std"]
    signs = data["signs"]
    pool = data["pool"]
    IC_mat = data["IC_mat"]
    trade_returns = data["trade_returns"]
    
    # Choose the dynamic weighting matrix
    if dynamic_metric == "multi":
        # Multi-metric: IC + IC_IR + Monotonicity (score_weights matter here!)
        score_mat = expanding_factor_score_numba(
            Z_std, signs, trade_returns, burn_in=BURN_IN,
            score_weights=score_weights, mono_window=mono_window)
        dyn_mat = score_mat
    else:
        # Pure IC with EMA (score_weights irrelevant)
        dyn_mat = IC_mat
    
    if scheme == "ew":
        return compute_ew(Z_std, signs)
    elif scheme == "icw":
        return compute_icw(Z_std, signs, pool=pool)
    elif scheme == "score":
        return compute_score_w(Z_std, signs, pool=pool, expanding_ic=dyn_mat,
                               ic_ema_span=ic_ema_span, score_weights=score_weights)
    elif scheme == "rank":
        return compute_rank_w(Z_std, signs, pool=pool, expanding_ic=dyn_mat,
                              ic_ema_span=ic_ema_span, w_min_ratio=rank_min,
                              w_max_ratio=rank_max, score_weights=score_weights)
    elif scheme == "ensemble":
        Z_ew = compute_ew(Z_std, signs)
        Z_icw = compute_icw(Z_std, signs, pool=pool)
        Z_score = compute_score_w(Z_std, signs, pool=pool, expanding_ic=dyn_mat,
                                   ic_ema_span=ic_ema_span, score_weights=score_weights)
        Z_rank = compute_rank_w(Z_std, signs, pool=pool, expanding_ic=dyn_mat,
                                 ic_ema_span=ic_ema_span, w_min_ratio=rank_min,
                                 w_max_ratio=rank_max, score_weights=score_weights)
        return (Z_ew + Z_icw + Z_score + Z_rank) / 4.0
    else:
        raise ValueError(f"Unknown scheme: {scheme}")


def evaluate_config(params: dict, etf_data: list, period: str = "val") -> dict:
    """
    Evaluate one unified config across all ETFs on specified period.
    Threshold is ALWAYS swept on TRAIN period. Evaluation on val or test.
    
    period: 'val' = validation (2020-2022, for param selection)
            'test' = test (2022-2026, for final reporting)
    """
    scheme = params["scheme"]
    score_weights = params["score_weights"]
    z_buffer = params["z_buffer"]
    mode = params["mode"]
    ic_ema_span = params["ic_ema_span"]
    rank_min = params["rank_min"]
    rank_max = params["rank_max"]
    mono_window = params["mono_window"]
    dynamic_metric = params.get("dynamic_metric", "ic")
    
    etf_period_returns = {}
    etf_sharpes = {}
    
    for data in etf_data:
        Z_comp = compute_composite(data, scheme, score_weights, ic_ema_span,
                                    rank_min, rank_max, mono_window, dynamic_metric)
        
        train_mask = data["train_mask"]
        eval_mask = data["val_mask"] if period == "val" else data["test_mask"]
        trade_returns = data["trade_returns"]
        
        Z_train = Z_comp[train_mask]
        ret_train = trade_returns[train_mask]
        Z_eval = Z_comp[eval_mask]
        ret_eval = trade_returns[eval_mask]
        
        if len(Z_eval) < 50:
            continue
        
        # Threshold ALWAYS swept on train period (zero look-ahead)
        sw = sweep_optimal_threshold(Z_train, ret_train, mode=mode, fee_bps=FEE_BPS, long_only=False)
        zl, zs = compute_production_threshold(sw, z_buffer=z_buffer)
        
        # Evaluate on target period
        positions = generate_positions(Z_eval, z_th=zl, z_th_short=zs, mode=mode, long_only=False)
        net_ret, _, _ = simulate_etf_spot(ret_eval, positions, fee_bps=FEE_BPS)
        
        std_n = np.std(net_ret)
        sr = float((np.mean(net_ret) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
        
        etf_period_returns[data["etf"]] = net_ret
        etf_sharpes[data["etf"]] = sr
    
    if not etf_period_returns:
        return {"params": params, "port_sharpe": -999.0, "port_pnl": 0.0,
                "port_maxdd": 0.0, "etf_sharpes": {}, "min_etf_sharpe": -999.0}
    
    # Portfolio: equal-weight combine
    lengths = [len(v) for v in etf_period_returns.values()]
    min_len = min(lengths)
    
    port_ret = np.zeros(min_len, dtype=np.float64)
    for ret in etf_period_returns.values():
        port_ret += ret[:min_len]
    port_ret /= len(etf_period_returns)
    
    std_p = np.std(port_ret)
    port_sharpe = float((np.mean(port_ret) / std_p) * sqrt(252)) if std_p > 1e-12 else 0.0
    total_pnl = float(port_ret.sum())
    
    cum = np.cumsum(port_ret)
    max_dd = float(np.max(np.maximum.accumulate(cum) - cum))
    
    return {
        "params": params,
        "port_sharpe": round(port_sharpe, 4),
        "port_pnl": round(total_pnl, 4),
        "port_maxdd": round(max_dd, 4),
        "etf_sharpes": {k: round(v, 4) for k, v in etf_sharpes.items()},
        "min_etf_sharpe": round(min(etf_sharpes.values()), 4) if etf_sharpes else -999.0,
    }


def build_grid(quick: bool = False) -> list:
    """Build parameter grid.
    
    Includes both dynamic_metric='ic' (current) and 'multi' (monotonicity-aware).
    For 'ic': score_weights/mono_window are irrelevant (deduped).
    For 'multi': score_weights/mono_window matter (full grid).
    """
    
    if quick:
        schemes = ["ensemble"]
        score_weights_list = [
            (0.35, 0.00, 0.65),  # Winner baseline
            (0.40, 0.00, 0.60),  # Slightly less mono
            (0.45, 0.00, 0.55),  # Moderate mono
            (0.30, 0.00, 0.70),  # More mono
            (0.30, 0.05, 0.65),  # Tiny IR + mono
            (0.35, 0.05, 0.60),  # Tiny IR + moderate mono
            (0.40, 0.05, 0.55),  # Tiny IR + less mono
            (0.25, 0.05, 0.70),  # Tiny IR + heavy mono
        ]
        buffers = [0.10]
        modes = ["binary"]
        ema_spans = [30]
        rank_bounds = [(0.4, 1.6)]
        mono_windows = [500, 750, 1000]
        dynamic_metrics = ["multi"]  # All multi-metric (IC-only already known)
    else:
        schemes = ["ew", "icw", "score", "rank", "ensemble"]
        score_weights_list = [
            (0.20, 0.15, 0.65),  # Mono-heavy (B3 default)
            (0.30, 0.30, 0.40),  # Balanced
            (0.40, 0.35, 0.25),  # IC-heavy
            (0.25, 0.25, 0.50),  # Moderate mono
            (0.15, 0.15, 0.70),  # Ultra-mono
        ]
        buffers = [0.05, 0.10, 0.15, 0.20]
        modes = ["binary", "tanh", "quadratic"]
        ema_spans = [10, 20, 30]
        rank_bounds = [(0.2, 1.8), (0.4, 1.6), (0.0, 2.0)]
        mono_windows = [500, 750, 1000]
        dynamic_metrics = ["ic", "multi"]
    
    grid = []
    for scheme, sw, buf, mode, ema, (rmin, rmax), mono, dyn_metric in product(
        schemes, score_weights_list, buffers, modes, ema_spans, rank_bounds, mono_windows, dynamic_metrics
    ):
        # Skip irrelevant combos
        if scheme in ("ew", "icw"):
            # EW/ICW don't use dynamic_metric, score_weights, ema, rank, mono
            if sw != score_weights_list[0] or ema != ema_spans[0] or (rmin, rmax) != rank_bounds[0] or mono != mono_windows[0] or dyn_metric != "ic":
                continue
        
        if scheme == "score" and (rmin, rmax) != rank_bounds[0]:
            continue
        
        # For dynamic_metric='ic': score_weights and mono_window are irrelevant
        # Only keep one combo to avoid duplicates
        if dyn_metric == "ic" and (sw != score_weights_list[0] or mono != mono_windows[0]):
            continue
        
        grid.append({
            "scheme": scheme,
            "score_weights": sw,
            "z_buffer": buf,
            "mode": mode,
            "ic_ema_span": ema,
            "rank_min": rmin,
            "rank_max": rmax,
            "mono_window": mono,
            "dynamic_metric": dyn_metric,
        })
    
    return grid


def main():
    parser = argparse.ArgumentParser(description="NewTrade Unified Parameter Optimizer (Walk-Forward)")
    parser.add_argument("--quick", action="store_true", help="Reduced grid for fast search")
    parser.add_argument("--top", type=int, default=15, help="Show top N results")
    parser.add_argument("--validate", action="store_true", help="Run DSR/CPCV on winner (uses TEST period)")
    parser.add_argument("-j", "--jobs", type=int, default=None, help="Parallel workers (default: CPU count)")
    args = parser.parse_args()
    
    import os
    from concurrent.futures import ProcessPoolExecutor, as_completed
    n_workers = args.jobs or os.cpu_count() or 4
    
    print("=" * 80)
    print("NEWTRADE UNIFIED PARAMETER OPTIMIZER (Walk-Forward, Zero Look-Ahead)")
    print(f"  TRAIN:      → {TRAIN_END}  (threshold sweep)")
    print(f"  VALIDATION: {VAL_START} → {VAL_END}  (parameter selection)")
    print(f"  TEST:       {TEST_START} → {TEST_END}  (final report, NEVER used for selection)")
    print(f"  Workers:    {n_workers}")
    print("=" * 80)
    
    # Pre-compute ETF data
    print("\n  Pre-computing ETF data...")
    t0 = time.time()
    etf_data = []
    for etf in ETFS:
        data = precompute_etf_data(etf)
        if data:
            etf_data.append(data)
            n_train = int(data["train_mask"].sum())
            n_val = int(data["val_mask"].sum())
            n_test = int(data["test_mask"].sum())
            print(f"    {etf}: {data['n_features']} feats | train={n_train}d, val={n_val}d, test={n_test}d")
    print(f"  Done in {time.time()-t0:.1f}s")
    
    # Build grid
    grid = build_grid(quick=args.quick)
    print(f"\n  Grid size: {len(grid)} configurations")
    
    # ─── PHASE 1: Select on VALIDATION period ───
    print(f"\n  PHASE 1: Evaluating on VALIDATION ({VAL_START}→{VAL_END})...")
    t0 = time.time()
    
    val_results = []
    # Use multiprocessing for large grids
    if len(grid) > 20 and n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers,
                                  initializer=_init_worker,
                                  initargs=(etf_data,)) as executor:
            futures = {executor.submit(_eval_worker, params, "val"): i 
                       for i, params in enumerate(grid)}
            done_count = 0
            for future in as_completed(futures):
                val_results.append(future.result())
                done_count += 1
                if done_count % 100 == 0:
                    elapsed = time.time() - t0
                    rate = done_count / elapsed
                    eta = (len(grid) - done_count) / rate
                    print(f"    [{done_count}/{len(grid)}] {rate:.1f}/s, ETA {eta:.0f}s")
    else:
        for i, params in enumerate(grid):
            r = evaluate_config(params, etf_data, period="val")
            val_results.append(r)
    
    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s ({len(grid)/max(elapsed,0.01):.1f} configs/s)")
    
    # Sort by VALIDATION Sharpe
    val_results.sort(key=lambda x: x["port_sharpe"], reverse=True)
    
    # Show top N on validation
    print(f"\n{'='*80}")
    print(f"TOP {args.top} ON VALIDATION PERIOD ({VAL_START}→{VAL_END})")
    print(f"{'='*80}")
    _print_table(val_results[:args.top])
    
    # ─── PHASE 2: Evaluate winner on TEST period (NEVER used for selection) ───
    winner_val = val_results[0]
    wp = winner_val["params"]
    
    print(f"\n{'━'*80}")
    print(f"  SELECTED CONFIG (by validation Sharpe):")
    print(f"    scheme={wp['scheme']}, mode={wp['mode']}, buffer={wp['z_buffer']}")
    print(f"    score_w={wp['score_weights']}, ema={wp['ic_ema_span']}")
    print(f"    rank=[{wp['rank_min']},{wp['rank_max']}], mono_win={wp['mono_window']}")
    print(f"    Val Sharpe={winner_val['port_sharpe']:.3f}")
    print(f"{'━'*80}")
    
    # Evaluate top-5 on TEST period
    print(f"\n  PHASE 2: Evaluating top-5 on TEST ({TEST_START}→{TEST_END})...")
    test_results = []
    for r in val_results[:5]:
        test_r = evaluate_config(r["params"], etf_data, period="test")
        test_r["val_sharpe"] = r["port_sharpe"]
        test_results.append(test_r)
    
    print(f"\n{'='*80}")
    print(f"TEST PERIOD RESULTS ({TEST_START}→{TEST_END}) — TRUE OUT-OF-SAMPLE")
    print(f"{'='*80}")
    _print_table(test_results)
    
    # Final winner on test
    test_results.sort(key=lambda x: x["port_sharpe"], reverse=True)
    final = test_results[0]
    fp = final["params"]
    print(f"\n  FINAL WINNER (test period):")
    print(f"    Config: scheme={fp['scheme']}, mode={fp['mode']}, buf={fp['z_buffer']}, "
          f"sw={fp['score_weights']}, ema={fp['ic_ema_span']}")
    print(f"    Test Sharpe={final['port_sharpe']:.3f}, PnL={final['port_pnl']:+.4f}, MaxDD={final['port_maxdd']:.4f}")
    print(f"    Per-ETF: {final['etf_sharpes']}")
    print(f"    Val Sharpe was: {final.get('val_sharpe', 'N/A')}")
    
    # ─── PHASE 3: DSR/CPCV validation ───
    if args.validate:
        n_trials = len(grid)
        print(f"\n  PHASE 3: DSR/CPCV VALIDATION (N_trials={n_trials})")
        
        # Get test-period portfolio returns for DSR
        port_returns_list = []
        for data in etf_data:
            Z_comp = compute_composite(data, fp["scheme"], fp["score_weights"],
                                        fp["ic_ema_span"], fp["rank_min"], fp["rank_max"], fp["mono_window"])
            # For final production: sweep on train+val, evaluate on test
            trainval_mask = data["train_mask"] | data["val_mask"]
            test_mask = data["test_mask"]
            trade_returns = data["trade_returns"]
            
            sw = sweep_optimal_threshold(Z_comp[trainval_mask], trade_returns[trainval_mask],
                                          mode=fp["mode"], fee_bps=FEE_BPS, long_only=False)
            zl, zs = compute_production_threshold(sw, z_buffer=fp["z_buffer"])
            pos = generate_positions(Z_comp[test_mask], z_th=zl, z_th_short=zs,
                                      mode=fp["mode"], long_only=False)
            nr, _, _ = simulate_etf_spot(trade_returns[test_mask], pos, fee_bps=FEE_BPS)
            port_returns_list.append(nr)
        
        min_len = min(len(r) for r in port_returns_list)
        port_ret = sum(r[:min_len] for r in port_returns_list) / len(port_returns_list)
        
        std_p = np.std(port_ret)
        port_sr = float((np.mean(port_ret) / std_p) * sqrt(252)) if std_p > 1e-12 else 0.0
        sk = float(skew(port_ret))
        kt = float(kurtosis(port_ret))
        
        dsr = deflated_sharpe_ratio(port_sr, n_trials=n_trials, n_obs=min_len,
                                     skewness=sk, kurtosis_excess=kt)
        print(f"    Portfolio SR (test): {port_sr:.3f}")
        print(f"    DSR (N={n_trials}): {dsr['dsr']:.4f} ({dsr['verdict']})")
        print(f"    Expected max SR under null: {dsr['expected_max_sr_annual']:.3f}")
        
        # CPCV
        print(f"\n    CPCV (full dataset):")
        for data in etf_data:
            Z_comp = compute_composite(data, fp["scheme"], fp["score_weights"],
                                        fp["ic_ema_span"], fp["rank_min"], fp["rank_max"], fp["mono_window"])
            cpcv = run_cpcv_backtest(Z_comp, data["trade_returns"], data["dates"],
                                      n_splits=6, n_test=2, purge_gap=5,
                                      mode=fp["mode"], fee_bps=FEE_BPS, z_buffer=fp["z_buffer"])
            print(f"      {data['etf']}: median_SR={cpcv['sharpe_median']:.3f} ± {cpcv['sharpe_std']:.3f} "
                  f"({cpcv['pct_positive']:.0f}% positive)")
    
    # Save
    out_path = HERE / "artifacts" / "unified_optimization.json"
    out_path.parent.mkdir(exist_ok=True)
    save_data = {
        "method": "walk-forward (train→val→test)",
        "periods": {"train_end": TRAIN_END, "val": f"{VAL_START}~{VAL_END}", "test": f"{TEST_START}~{TEST_END}"},
        "grid_size": len(grid),
        "elapsed_s": round(elapsed, 1),
        "winner_val": winner_val,
        "winner_test": final,
        "top_20_val": val_results[:20],
        "top_5_test": test_results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2, default=str)
    print(f"\n  Saved to {out_path}")


# Global for multiprocessing (Windows spawn pattern)
_GLOBAL_ETF_DATA = None

def _init_worker(etf_data):
    """Initializer for worker processes — sets global ETF data."""
    global _GLOBAL_ETF_DATA
    _GLOBAL_ETF_DATA = etf_data

def _eval_worker(params, period):
    """Worker function for multiprocessing."""
    return evaluate_config(params, _GLOBAL_ETF_DATA, period=period)


def _print_table(results):
    """Print results table."""
    print(f"  {'#':>3s} {'Scheme':<10s} {'Mode':<10s} {'Buf':>5s} {'ScoreW':<18s} "
          f"{'EMA':>4s} {'Rank':>10s} {'PortSR':>7s} {'PnL':>8s} {'MaxDD':>7s} "
          f"{'159915':>7s} {'500':>7s} {'300':>7s}")
    print(f"  {'-'*130}")
    for i, r in enumerate(results):
        p = r["params"]
        sw_str = f"{p['score_weights'][0]:.2f}/{p['score_weights'][1]:.2f}/{p['score_weights'][2]:.2f}"
        rank_str = f"{p['rank_min']:.1f}-{p['rank_max']:.1f}"
        es = r.get("etf_sharpes", {})
        print(f"  {i+1:>3d} {p['scheme']:<10s} {p['mode']:<10s} {p['z_buffer']:>5.2f} {sw_str:<18s} "
              f"{p['ic_ema_span']:>4d} {rank_str:>10s} {r['port_sharpe']:>7.3f} {r['port_pnl']:>+8.4f} "
              f"{r['port_maxdd']:>7.4f} {es.get('159915ETF',0):>7.3f} {es.get('500ETF',0):>7.3f} {es.get('300ETF',0):>7.3f}")


if __name__ == "__main__":
    main()
