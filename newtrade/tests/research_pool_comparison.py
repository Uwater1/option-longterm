#!/usr/bin/env python3
"""
Comprehensive comparison: Old pools vs New pipeline pools vs Yearly reselection.
Uses BOTH threshold methods:
  1. Auto-sweep (production standard)
  2. Percentile-based P75 (threshold-free fair comparison)

This isolates whether the pool quality or the threshold system drives differences.
"""
import sys, json, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from utils import load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot, sweep_optimal_threshold, compute_production_threshold

DAY_MODEL_DATA = REPO_ROOT / "day-model-new" / "data"
ETFS = ["300ETF", "500ETF", "159915ETF"]
FEE_BPS = 0.0008
BURN_IN = 252

YEAR_SUFFIX = {2022: "", 2023: "_p2015_2023", 2024: "_p2016_2024", 2025: "_p2017_2025"}


def load_old_pools():
    """Load old admitted pools from backup."""
    spec = importlib.util.spec_from_file_location("old_pools", HERE / "data" / "old_admitted_pools_backup.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.POOLS


def load_new_pools():
    """Load new (regenerated) admitted pools."""
    spec = importlib.util.spec_from_file_location("new_pools", REPO_ROOT / "day-model-new" / "admitted_pools.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.POOLS


def load_period_pool(etf, year):
    suffix = YEAR_SUFFIX.get(year, "_p2017_2025")
    fpath = DAY_MODEL_DATA / f"selected_pool_{etf}_single{suffix}.json"
    if not fpath.exists():
        return []
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_composite(df, pool, full_trade_ret, top_k=10):
    """Build ICW composite signal for a pool."""
    X, signs, _ = build_pool_feature_matrix(df, pool)
    Z = expanding_zscore_numba(X, burn_in=BURN_IN, clip=3.0)
    IC = expanding_factor_ic_numba(Z, signs, full_trade_ret, burn_in=BURN_IN)
    N = len(pool)
    n_train = int((df["date"] < pd.Timestamp("2022-01-01")).sum())
    if n_train < 252:
        n_train = 1700
    icw = get_weighting_scheme("icw")
    effective_topk = min(top_k, N - 1) if N > top_k else None
    Z_comp = icw(Z, signs, pool=pool, n_train=n_train,
                 expanding_ic=IC, top_k=effective_topk, ic_ema_span=30, dynamic_metric="ic")
    return Z_comp


def eval_auto_threshold(Z_comp, full_trade_ret, dates, start="2022-01-01", end="2026-01-01"):
    """Evaluate with production auto-sweep threshold."""
    t_start = pd.Timestamp(start)
    train_mask = dates < t_start
    sweep = sweep_optimal_threshold(Z_comp[train_mask.values], full_trade_ret[train_mask.values],
                                    mode="binary", fee_bps=FEE_BPS, long_only=False)
    z_th, z_th_s = compute_production_threshold(sweep, z_buffer=0.1)
    pos = generate_positions(Z_comp, z_th=z_th, z_th_short=z_th_s, mode="binary", long_only=False)
    oos = (dates >= start) & (dates < end)
    net, _, _ = simulate_etf_spot(full_trade_ret[oos.values], pos[oos.values], fee_bps=FEE_BPS)
    if len(net) < 20 or np.std(net) < 1e-12:
        return {"sharpe": 0, "pnl": 0, "wr": 0, "trades": 0, "z_th": z_th}
    sr = float(np.mean(net) / np.std(net) * np.sqrt(252))
    trades = int((np.abs(pos[oos.values]) > 1e-5).sum())
    wr = float((net[np.abs(pos[oos.values]) > 1e-5] > 0).mean() * 100) if trades > 0 else 0
    return {"sharpe": sr, "pnl": float(np.sum(net)), "wr": wr, "trades": trades, "z_th": z_th}


def eval_percentile_threshold(Z_comp, full_trade_ret, dates, start="2022-01-01", end="2026-01-01", pct=75):
    """Evaluate with self-normalizing percentile threshold (zero-lookahead)."""
    oos_idx = np.where(((dates >= start) & (dates < end)).values)[0]
    results = []
    positions = []
    for t in oos_idx:
        hist = Z_comp[max(0, t - 504):t]
        if len(hist) < 100:
            results.append(0.0)
            positions.append(0)
            continue
        thresh = np.percentile(np.abs(hist), pct)
        if abs(Z_comp[t]) > thresh:
            pos = np.sign(Z_comp[t])
            results.append(pos * full_trade_ret[t])
            positions.append(pos)
        else:
            results.append(0.0)
            positions.append(0)
    net = np.array(results)
    pos_arr = np.array(positions)
    active = pos_arr != 0
    if active.sum() < 10 or np.std(net[active]) < 1e-12:
        return {"sharpe": 0, "pnl": 0, "wr": 0, "trades": int(active.sum())}
    sr = float(np.mean(net[active]) / np.std(net[active]) * np.sqrt(252))
    wr = float((net[active] > 0).mean() * 100)
    return {"sharpe": sr, "pnl": float(np.sum(net)), "wr": wr, "trades": int(active.sum())}


def eval_yearly_stitched(etf, df, full_trade_ret, dates, method="auto"):
    """Yearly reselection with per-year pools, stitched."""
    all_results = []
    for y in [2022, 2023, 2024, 2025]:
        pool = load_period_pool(etf, y)
        if not pool or len(pool) < 5:
            continue
        Z_comp = compute_composite(df, pool, full_trade_ret)
        if method == "auto":
            res = eval_auto_threshold(Z_comp, full_trade_ret, dates, f"{y}-01-01", f"{y+1}-01-01")
        else:
            res = eval_percentile_threshold(Z_comp, full_trade_ret, dates, f"{y}-01-01", f"{y+1}-01-01")
        all_results.append(res)
    # Aggregate
    if not all_results:
        return {"sharpe": 0, "pnl": 0, "wr": 0, "trades": 0}
    # Re-run stitched for proper aggregate
    all_net = []
    all_pos = []
    for y in [2022, 2023, 2024, 2025]:
        pool = load_period_pool(etf, y)
        if not pool or len(pool) < 5:
            continue
        Z_comp = compute_composite(df, pool, full_trade_ret)
        if method == "auto":
            t_start = pd.Timestamp(f"{y}-01-01")
            train_mask = dates < t_start
            sweep = sweep_optimal_threshold(Z_comp[train_mask.values], full_trade_ret[train_mask.values],
                                            mode="binary", fee_bps=FEE_BPS, long_only=False)
            z_th, z_th_s = compute_production_threshold(sweep, z_buffer=0.1)
            pos = generate_positions(Z_comp, z_th=z_th, z_th_short=z_th_s, mode="binary", long_only=False)
        else:
            # Percentile positions
            pos = np.zeros(len(Z_comp))
            for t in range(BURN_IN, len(Z_comp)):
                hist = Z_comp[max(0, t-504):t]
                if len(hist) < 100:
                    continue
                thresh = np.percentile(np.abs(hist), 75)
                if abs(Z_comp[t]) > thresh:
                    pos[t] = np.sign(Z_comp[t])
        yr_mask = ((dates >= f"{y}-01-01") & (dates < f"{y+1}-01-01")).values
        net_y, _, _ = simulate_etf_spot(full_trade_ret[yr_mask], pos[yr_mask], fee_bps=FEE_BPS)
        all_net.append(net_y)
        all_pos.append(pos[yr_mask])
    if not all_net:
        return {"sharpe": 0, "pnl": 0, "wr": 0, "trades": 0}
    net = np.concatenate(all_net)
    p = np.concatenate(all_pos)
    active = np.abs(p) > 1e-5
    if active.sum() < 10 or np.std(net[active]) < 1e-12:
        return {"sharpe": 0, "pnl": float(np.sum(net)), "wr": 0, "trades": int(active.sum())}
    sr = float(np.mean(net[active]) / np.std(net[active]) * np.sqrt(252))
    wr = float((net[active] > 0).mean() * 100)
    return {"sharpe": sr, "pnl": float(np.sum(net)), "wr": wr, "trades": int(active.sum())}


def main():
    old_pools = load_old_pools()
    new_pools = load_new_pools()

    print("=" * 100)
    print("COMPREHENSIVE POOL COMPARISON: Old Vintage vs New Pipeline vs Yearly Reselection")
    print("  Methods: Auto-Sweep Threshold | Percentile P75 (threshold-free)")
    print("=" * 100)

    summary = []

    for etf in ETFS:
        df = load_etf_dataset(etf)
        full_trade_ret = df["trade_return"].values.astype(np.float64)
        dates = df["date"]

        old_pool = old_pools.get(etf, {}).get("single", [])
        new_pool = new_pools.get(etf, {}).get("single", [])

        print(f"\n{'─' * 100}")
        print(f"  {etf}: Old={len(old_pool)} feats | New(p2017_2025)={len(new_pool)} feats")
        print(f"{'─' * 100}")

        if len(old_pool) < 5 and len(new_pool) < 5:
            print("  [SKIP] Both pools too small")
            continue

        # Compute composites
        Z_old = compute_composite(df, old_pool, full_trade_ret) if len(old_pool) >= 5 else None
        Z_new = compute_composite(df, new_pool, full_trade_ret) if len(new_pool) >= 5 else None

        # Evaluate all combinations
        results = {}
        if Z_old is not None:
            results["Old+AutoSweep"] = eval_auto_threshold(Z_old, full_trade_ret, dates)
            results["Old+PctP75"] = eval_percentile_threshold(Z_old, full_trade_ret, dates)
        if Z_new is not None:
            results["New+AutoSweep"] = eval_auto_threshold(Z_new, full_trade_ret, dates)
            results["New+PctP75"] = eval_percentile_threshold(Z_new, full_trade_ret, dates)
        results["Yearly+AutoSweep"] = eval_yearly_stitched(etf, df, full_trade_ret, dates, "auto")
        results["Yearly+PctP75"] = eval_yearly_stitched(etf, df, full_trade_ret, dates, "pct")

        # Print
        print(f"\n  {'Method':<22} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'Trades':>7} | {'z_th':>6}")
        print(f"  {'-'*22}-+-{'-'*34}-+-{'-'*6}")
        for name, r in results.items():
            z_str = f"{r.get('z_th', '-')}" if isinstance(r.get('z_th'), float) else "-"
            print(f"  {name:<22} | {r['sharpe']:>8.3f} {r['pnl']:>+10.4f} {r['wr']:>6.1f} {r['trades']:>7} | {z_str:>6}")

        # Delta analysis
        if Z_old is not None and Z_new is not None:
            d_auto = results["New+AutoSweep"]["sharpe"] - results["Old+AutoSweep"]["sharpe"]
            d_pct = results["New+PctP75"]["sharpe"] - results["Old+PctP75"]["sharpe"]
            print(f"\n  Δ(New-Old) AutoSweep: {d_auto:+.3f} | PctP75: {d_pct:+.3f}")
        if Z_new is not None:
            d_yr = results["Yearly+PctP75"]["sharpe"] - results["New+PctP75"]["sharpe"]
            print(f"  Δ(Yearly-New) PctP75: {d_yr:+.3f}")

        summary.append({"etf": etf, **{k: v["sharpe"] for k, v in results.items()}})

    # Final summary table
    print(f"\n\n{'=' * 100}")
    print("SUMMARY (Sharpe Ratios)")
    print(f"{'=' * 100}")
    print(f"  {'ETF':<12} | {'Old+Auto':>9} {'Old+P75':>9} | {'New+Auto':>9} {'New+P75':>9} | {'Yr+Auto':>9} {'Yr+P75':>9}")
    print(f"  {'-'*12}-+-{'-'*20}-+-{'-'*20}-+-{'-'*20}")
    for s in summary:
        print(f"  {s['etf']:<12} | {s.get('Old+AutoSweep',0):>9.3f} {s.get('Old+PctP75',0):>9.3f} | "
              f"{s.get('New+AutoSweep',0):>9.3f} {s.get('New+PctP75',0):>9.3f} | "
              f"{s.get('Yearly+AutoSweep',0):>9.3f} {s.get('Yearly+PctP75',0):>9.3f}")

    print(f"\n  Key: Old=stale admitted_pools | New=p2017_2025 pipeline | Yr=yearly reselection")
    print(f"       Auto=production sweep+buffer | P75=percentile-based (threshold-free)")


if __name__ == "__main__":
    main()
