#!/usr/bin/env python3
"""
Pool Switching Protocol Research.

Problem: Features decay. Can't keep a static pool forever. But naive yearly reselection
is chaotically path-dependent (B4 gate). Need a principled switching plan.

Protocol Design:
  1. Cadence: Run reselection every 2 years (not yearly)
  2. Gate: Only switch if new pool passes threshold-free validation
  3. Transition: Use percentile threshold during calibration period
  4. Rollback: Auto-revert if post-switch performance degrades

This script tests:
  A) 2-year cadence reselection (switch at 2024 using p2016_2024 pool)
  B) Gated switch: only switch if trailing 6-month IC of new > old
  C) Percentile threshold during first 6 months post-switch
  D) Compare vs static (never switch) and yearly (always switch)
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


def load_old_pools():
    spec = importlib.util.spec_from_file_location("old_pools", HERE / "data" / "old_admitted_pools_backup.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.POOLS


def load_period_pool(etf, suffix):
    fpath = DAY_MODEL_DATA / f"selected_pool_{etf}_single{suffix}.json"
    if not fpath.exists():
        return []
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_composite(df, pool, full_trade_ret, top_k=10):
    """Build ICW composite signal."""
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


def rolling_ic(Z_comp, returns, dates, window=126):
    """Compute trailing rolling IC (zero-lookahead)."""
    T = len(Z_comp)
    ic = np.full(T, np.nan)
    for t in range(window, T):
        z = Z_comp[t-window:t]
        r = returns[t-window:t]
        valid = ~(np.isnan(z) | np.isnan(r))
        if valid.sum() > 30:
            ic[t] = np.corrcoef(z[valid], r[valid])[0, 1]
    return ic


def eval_period(Z_comp, full_trade_ret, dates, start, end, method="auto"):
    """Evaluate a period with given threshold method."""
    oos = (dates >= start) & (dates < end)
    oos_idx = np.where(oos.values)[0]
    if len(oos_idx) < 10:
        return {"sharpe": 0, "pnl": 0, "trades": 0, "wr": 0}

    if method == "auto":
        t_start = pd.Timestamp(start)
        train_mask = dates < t_start
        if train_mask.sum() < 100:
            return {"sharpe": 0, "pnl": 0, "trades": 0, "wr": 0}
        sweep = sweep_optimal_threshold(Z_comp[train_mask.values], full_trade_ret[train_mask.values],
                                        mode="binary", fee_bps=FEE_BPS, long_only=False)
        z_th, z_th_s = compute_production_threshold(sweep, z_buffer=0.1)
        pos = generate_positions(Z_comp, z_th=z_th, z_th_short=z_th_s, mode="binary", long_only=False)
        net, _, _ = simulate_etf_spot(full_trade_ret[oos.values], pos[oos.values], fee_bps=FEE_BPS)
    else:  # percentile
        pos = np.zeros(len(Z_comp))
        for t in oos_idx:
            hist = Z_comp[max(0, t-504):t]
            if len(hist) < 100:
                continue
            thresh = np.percentile(np.abs(hist), 75)
            if abs(Z_comp[t]) > thresh:
                pos[t] = np.sign(Z_comp[t])
        net, _, _ = simulate_etf_spot(full_trade_ret[oos.values], pos[oos.values], fee_bps=FEE_BPS)

    active = np.abs(pos[oos.values]) > 1e-5
    if active.sum() < 5 or np.std(net[active]) < 1e-12:
        return {"sharpe": 0, "pnl": float(np.sum(net)), "trades": int(active.sum()), "wr": 0}
    sr = float(np.mean(net[active]) / np.std(net[active]) * np.sqrt(252))
    wr = float((net[active] > 0).mean() * 100)
    return {"sharpe": sr, "pnl": float(np.sum(net)), "trades": int(active.sum()), "wr": wr}


def test_switching_protocol(etf, df, full_trade_ret, dates, old_pool):
    """
    Test the gated switching protocol:
    - At 2024-01-01: evaluate whether to switch to p2016_2024 pool
    - Gate: trailing 6-month rolling IC of new pool > old pool
    - If switch: use percentile threshold for first 6 months, then auto-sweep
    - Compare vs never-switch and always-switch
    """
    print(f"\n{'═' * 90}")
    print(f"  SWITCHING PROTOCOL: {etf}")
    print(f"{'═' * 90}")

    # Load candidate pools for switching
    pool_2024 = load_period_pool(etf, "_p2016_2024")  # Available at 2024-01-01
    pool_2025 = load_period_pool(etf, "_p2017_2025")  # Available at 2025-01-01

    # Compute composites for all pools
    Z_old = compute_composite(df, old_pool, full_trade_ret)
    Z_2024 = compute_composite(df, pool_2024, full_trade_ret) if pool_2024 and len(pool_2024) >= 5 else None
    Z_2025 = compute_composite(df, pool_2025, full_trade_ret) if pool_2025 and len(pool_2025) >= 5 else None

    # ─── Strategy 1: Never switch (static old pool) ───
    print(f"\n  Strategy 1: NEVER SWITCH (old pool, auto-sweep)")
    for period, start, end in [("2022-2023", "2022-01-01", "2024-01-01"),
                                ("2024-2025", "2024-01-01", "2026-01-01"),
                                ("FULL", "2022-01-01", "2026-01-01")]:
        r = eval_period(Z_old, full_trade_ret, dates, start, end, "auto")
        print(f"    {period}: Sharpe={r['sharpe']:.3f} PnL={r['pnl']:+.4f} WR={r['wr']:.1f}% N={r['trades']}")

    # ─── Strategy 2: Always switch at 2024 (ungated) ───
    if Z_2024 is not None:
        print(f"\n  Strategy 2: ALWAYS SWITCH at 2024 (ungated, auto-sweep)")
        # 2022-2023: old pool
        r1 = eval_period(Z_old, full_trade_ret, dates, "2022-01-01", "2024-01-01", "auto")
        # 2024-2025: new pool
        r2 = eval_period(Z_2024, full_trade_ret, dates, "2024-01-01", "2026-01-01", "auto")
        print(f"    2022-2023 (old): Sharpe={r1['sharpe']:.3f} PnL={r1['pnl']:+.4f}")
        print(f"    2024-2025 (new): Sharpe={r2['sharpe']:.3f} PnL={r2['pnl']:+.4f}")
        # Stitched
        all_net = []
        for start, end, Z in [("2022-01-01", "2024-01-01", Z_old), ("2024-01-01", "2026-01-01", Z_2024)]:
            t_s = pd.Timestamp(start)
            train_m = dates < t_s
            sweep = sweep_optimal_threshold(Z[train_m.values], full_trade_ret[train_m.values],
                                            mode="binary", fee_bps=FEE_BPS, long_only=False)
            z_th, z_th_s = compute_production_threshold(sweep, z_buffer=0.1)
            pos = generate_positions(Z, z_th=z_th, z_th_short=z_th_s, mode="binary", long_only=False)
            oos = (dates >= start) & (dates < end)
            net, _, _ = simulate_etf_spot(full_trade_ret[oos.values], pos[oos.values], fee_bps=FEE_BPS)
            all_net.append(net)
        stitched = np.concatenate(all_net)
        sr_full = np.mean(stitched) / np.std(stitched) * np.sqrt(252) if np.std(stitched) > 1e-12 else 0
        print(f"    FULL stitched:   Sharpe={sr_full:.3f} PnL={np.sum(stitched):+.4f}")

    # ─── Strategy 3: GATED switch (only if trailing IC new > old) ───
    if Z_2024 is not None:
        print(f"\n  Strategy 3: GATED SWITCH at 2024 (trailing 6m IC gate)")
        # Compute trailing 6-month IC at switch point (2024-01-01)
        switch_idx = np.where(dates >= "2024-01-01")[0][0]
        window = 126  # ~6 months

        ic_old_trail = rolling_ic(Z_old, full_trade_ret, dates, window)
        ic_new_trail = rolling_ic(Z_2024, full_trade_ret, dates, window)

        ic_old_at_switch = ic_old_trail[switch_idx] if not np.isnan(ic_old_trail[switch_idx]) else 0
        ic_new_at_switch = ic_new_trail[switch_idx] if not np.isnan(ic_new_trail[switch_idx]) else 0
        gate_pass = ic_new_at_switch > ic_old_at_switch

        print(f"    Trailing 6m IC at 2024-01-01: Old={ic_old_at_switch:.4f} New={ic_new_at_switch:.4f}")
        print(f"    Gate: {'PASS → SWITCH' if gate_pass else 'FAIL → KEEP OLD'}")

        if gate_pass:
            # Use percentile for first 6 months, then auto-sweep
            print(f"    Transition: Percentile P75 for 2024-H1, auto-sweep for 2024-H2+")
            r_h1 = eval_period(Z_2024, full_trade_ret, dates, "2024-01-01", "2024-07-01", "pct")
            r_h2 = eval_period(Z_2024, full_trade_ret, dates, "2024-07-01", "2026-01-01", "auto")
            print(f"    2024-H1 (pct):   Sharpe={r_h1['sharpe']:.3f} PnL={r_h1['pnl']:+.4f} N={r_h1['trades']}")
            print(f"    2024-H2+ (auto): Sharpe={r_h2['sharpe']:.3f} PnL={r_h2['pnl']:+.4f} N={r_h2['trades']}")
        else:
            print(f"    Keeping old pool. No switch.")

    # ─── Strategy 4: Gated + Percentile全程 ───
    if Z_2024 is not None:
        print(f"\n  Strategy 4: GATED + PERCENTILE全程 (P75 entire OOS)")
        # Old pool P75 for 2022-2023
        r1 = eval_period(Z_old, full_trade_ret, dates, "2022-01-01", "2024-01-01", "pct")
        # Gate check at 2024
        if gate_pass:
            r2 = eval_period(Z_2024, full_trade_ret, dates, "2024-01-01", "2026-01-01", "pct")
            print(f"    2022-2023 (old P75): Sharpe={r1['sharpe']:.3f} PnL={r1['pnl']:+.4f}")
            print(f"    2024-2025 (new P75): Sharpe={r2['sharpe']:.3f} PnL={r2['pnl']:+.4f}")
        else:
            r2 = eval_period(Z_old, full_trade_ret, dates, "2024-01-01", "2026-01-01", "pct")
            print(f"    2022-2023 (old P75): Sharpe={r1['sharpe']:.3f} PnL={r1['pnl']:+.4f}")
            print(f"    2024-2025 (old P75, gate failed): Sharpe={r2['sharpe']:.3f} PnL={r2['pnl']:+.4f}")

    # ─── Rolling IC trajectory (for visualization) ───
    print(f"\n  Rolling 6m IC trajectory (at year boundaries):")
    print(f"    {'Date':<12} | {'Old IC':>8} | {'New(2024) IC':>12} | {'New(2025) IC':>12}")
    for yr in ["2022-07-01", "2023-01-01", "2023-07-01", "2024-01-01", "2024-07-01", "2025-01-01", "2025-07-01"]:
        idx = np.where(dates >= yr)[0]
        if len(idx) == 0:
            continue
        t = idx[0]
        ic_o = ic_old_trail[t] if t < len(ic_old_trail) and not np.isnan(ic_old_trail[t]) else 0
        ic_n24 = ic_new_trail[t] if Z_2024 is not None and t < len(ic_new_trail) and not np.isnan(ic_new_trail[t]) else 0
        if Z_2025 is not None:
            ic_2025_trail = rolling_ic(Z_2025, full_trade_ret, dates, window)
            ic_n25 = ic_2025_trail[t] if t < len(ic_2025_trail) and not np.isnan(ic_2025_trail[t]) else 0
        else:
            ic_n25 = 0
        print(f"    {yr:<12} | {ic_o:>8.4f} | {ic_n24:>12.4f} | {ic_n25:>12.4f}")


def main():
    old_pools = load_old_pools()

    print("=" * 90)
    print("POOL SWITCHING PROTOCOL RESEARCH")
    print("  Testing: Never-switch vs Ungated-switch vs Gated-switch vs Gated+Percentile")
    print("=" * 90)

    for etf in ETFS:
        df = load_etf_dataset(etf)
        full_trade_ret = df["trade_return"].values.astype(np.float64)
        dates = df["date"]
        old_pool = old_pools.get(etf, {}).get("single", [])
        if len(old_pool) < 5:
            print(f"\n  [SKIP] {etf}: old pool too small ({len(old_pool)})")
            continue
        test_switching_protocol(etf, df, full_trade_ret, dates, old_pool)

    # Final protocol recommendation
    print(f"\n\n{'=' * 90}")
    print("PROPOSED SWITCHING PROTOCOL")
    print(f"{'=' * 90}")
    print("""
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  RESELECTION CADENCE: Every 2 years (aligned with day-model-new periods)│
  │                                                                         │
  │  GATE (must pass ALL):                                                  │
  │    1. Trailing 6-month IC of new pool > old pool (at switch date)       │
  │    2. New pool has ≥ 10 features                                        │
  │    3. New pool trained on ≥ 7 years of data                             │
  │                                                                         │
  │  TRANSITION (if gate passes):                                           │
  │    Phase 1 (months 1-6): Percentile P75 threshold (no coupling)         │
  │    Phase 2 (month 7+):  Auto-sweep recalibrated on new pool history     │
  │                                                                         │
  │  ROLLBACK:                                                              │
  │    If post-switch 3-month realized Sharpe < 0: revert to old pool       │
  │                                                                         │
  │  MONITORING:                                                            │
  │    - Track rolling 6m IC of active pool quarterly                       │
  │    - Alert if IC drops below 0.05 for 2 consecutive quarters            │
  └─────────────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    main()
