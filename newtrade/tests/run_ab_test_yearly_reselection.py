#!/usr/bin/env python3
"""
A/B Test: Static Feature Pool vs Yearly-Reselected Feature Pool.

Group A (Static): Use the production admitted_pools.py pool for all OOS years.
Group B (Yearly): Use period-specific pools from day-model-new/data/, switching
                  feature list each year based on the most recent reselection.

Period mapping for Group B:
  - 2022 trading days: selected_pool_{ETF}_single.json (original, train 2015-2022)
  - 2023 trading days: selected_pool_{ETF}_single_p2015_2023.json
  - 2024 trading days: selected_pool_{ETF}_single_p2016_2024.json
  - 2025 trading days: selected_pool_{ETF}_single_p2017_2025.json

Both groups use identical backtest mechanics:
  - ICW scheme, Top-10, dynamic IC (30d EMA), binary L+S
  - Auto threshold with +0.1 buffer
  - 8 bps friction
  - No stop-loss (pure signal comparison)

Evaluates 300ETF, 500ETF, 159915ETF over 2022-2026.
Reports per-year and aggregate Sharpe, PnL, WinRate, MaxDD.
"""

import sys
import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, expanding_factor_ic_numba
)
from weighting import get_weighting_scheme
from strategy import generate_positions, simulate_etf_spot, sweep_optimal_threshold, compute_production_threshold

# Period-specific pool file mapping: OOS year -> suffix
YEAR_TO_POOL_SUFFIX = {
    2022: "",              # original (train 2015-2022)
    2023: "_p2015_2023",
    2024: "_p2016_2024",
    2025: "_p2017_2025",
    2026: "_p2017_2025",   # use latest available
}

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
DAY_MODEL_DATA = REPO_ROOT / "day-model-new" / "data"


def load_period_pool(etf: str, year: int, min_features: int = 5) -> list:
    """Load period-specific pool for a given ETF and OOS year."""
    suffix = YEAR_TO_POOL_SUFFIX.get(year, "_p2017_2025")
    fname = f"selected_pool_{etf}_single{suffix}.json"
    fpath = DAY_MODEL_DATA / fname
    if not fpath.exists():
        print(f"  [WARNING] Pool file not found: {fname}")
        return []
    with open(fpath, "r", encoding="utf-8") as f:
        pool = json.load(f)
    if len(pool) < min_features:
        print(f"  [WARNING] {fname} has only {len(pool)} features (< {min_features})")
        return []
    return pool


def run_backtest_with_pool(etf: str, pool: list, df: pd.DataFrame, full_trade_ret: np.ndarray,
                           start_date: str, end_date: str, fee_bps: float = 0.0008,
                           z_buffer: float = 0.1, top_k: int = 10) -> dict:
    """
    Run a single backtest using a given pool. Returns metrics dict.
    Uses ICW + dynamic IC + top-K + binary L+S + auto threshold.
    """
    if not pool or len(pool) < 5:
        return {"status": "SKIPPED", "n_features": len(pool) if pool else 0}

    # Build feature matrix
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    burn_in = 252

    # Expanding z-score
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    # Expanding IC for dynamic ranking
    IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)

    # ICW composite with top-K dynamic selection
    t_start_ts = pd.Timestamp(start_date)
    n_train = int((df["date"] < t_start_ts).sum())
    if n_train < 252:
        n_train = 1700

    scheme_func = get_weighting_scheme("icw")
    Z_composite = scheme_func(
        Z_std, signs, pool=pool, n_train=n_train,
        expanding_ic=IC_mat, top_k=top_k, ic_ema_span=30, dynamic_metric="ic"
    )

    # Auto threshold sweep on training data
    train_mask = df["date"] < t_start_ts
    Z_train = Z_composite[train_mask.values]
    ret_train = full_trade_ret[train_mask.values]
    sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary", fee_bps=fee_bps, long_only=False)
    z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer, z_short_buffer=None)

    # Generate positions
    positions_full = generate_positions(Z_composite, z_th=z_th_prod, z_th_short=z_th_short, mode="binary", long_only=False)

    # Filter to OOS period
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not mask.any():
        return {"status": "NO_DATA"}

    positions_oos = positions_full[mask.values]
    trade_returns_oos = full_trade_ret[mask.values]
    dates_oos = df["date"][mask.values]

    # Simulate
    net_returns, raw_returns, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

    # Metrics
    n_days = len(net_returns)
    if n_days < 20 or np.std(net_returns) < 1e-12:
        return {"status": "INSUFFICIENT", "n_features": len(pool)}

    sharpe = float(np.mean(net_returns) / np.std(net_returns) * np.sqrt(252))
    total_pnl = float(np.sum(net_returns))
    n_trades = int((np.abs(positions_oos) > 1e-5).sum())
    wr = float((net_returns[np.abs(positions_oos) > 1e-5] > 0).mean() * 100) if n_trades > 0 else 0.0

    # Max drawdown
    cum = np.cumsum(net_returns)
    peak = np.maximum.accumulate(cum)
    dd = peak - cum
    max_dd = float(np.max(dd)) if len(dd) > 0 else 0.0

    return {
        "status": "SUCCESS",
        "n_features": len(pool),
        "sharpe": sharpe,
        "total_pnl": total_pnl,
        "n_trades": n_trades,
        "n_days": n_days,
        "win_rate": wr,
        "max_dd": max_dd,
        "z_th_long": z_th_prod,
        "z_th_short": z_th_short,
    }


def run_per_year_backtest(etf: str, pool: list, df: pd.DataFrame, full_trade_ret: np.ndarray,
                          fee_bps: float, z_buffer: float, top_k: int) -> dict:
    """Run backtest per year and return yearly + aggregate metrics."""
    years = [2022, 2023, 2024, 2025]
    yearly_results = {}

    for y in years:
        start = f"{y}-01-01"
        end = f"{y + 1}-01-01"
        res = run_backtest_with_pool(etf, pool, df, full_trade_ret, start, end, fee_bps, z_buffer, top_k)
        yearly_results[y] = res

    # Full period aggregate
    full_res = run_backtest_with_pool(etf, pool, df, full_trade_ret, "2022-01-01", "2026-01-01", fee_bps, z_buffer, top_k)

    return {"yearly": yearly_results, "full": full_res}


def run_yearly_reselected(etf: str, df: pd.DataFrame, full_trade_ret: np.ndarray,
                          fee_bps: float, z_buffer: float, top_k: int) -> dict:
    """
    Run backtest with yearly-reselected pools.
    For each year, load the appropriate period pool and run backtest on that year's data.
    Then stitch together for aggregate metrics.
    """
    years = [2022, 2023, 2024, 2025]
    yearly_results = {}
    all_net_returns = []
    all_positions = []

    for y in years:
        pool = load_period_pool(etf, y)
        if not pool:
            yearly_results[y] = {"status": "NO_POOL"}
            continue

        start = f"{y}-01-01"
        end = f"{y + 1}-01-01"
        res = run_backtest_with_pool(etf, pool, df, full_trade_ret, start, end, fee_bps, z_buffer, top_k)
        yearly_results[y] = res

    # Full period: run each year with its own pool, stitch net returns
    # We need to do this at a lower level to get stitched returns
    stitched_returns = []
    stitched_positions = []
    for y in years:
        pool = load_period_pool(etf, y)
        if not pool or len(pool) < 5:
            continue

        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        Z_std = expanding_zscore_numba(X_raw, burn_in=252, clip=3.0)
        IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=252)

        t_start_ts = pd.Timestamp(f"{y}-01-01")
        n_train = int((df["date"] < t_start_ts).sum())
        if n_train < 252:
            n_train = 1700

        scheme_func = get_weighting_scheme("icw")
        Z_composite = scheme_func(
            Z_std, signs, pool=pool, n_train=n_train,
            expanding_ic=IC_mat, top_k=top_k, ic_ema_span=30, dynamic_metric="ic"
        )

        # Threshold from training
        train_mask = df["date"] < t_start_ts
        Z_train = Z_composite[train_mask.values]
        ret_train = full_trade_ret[train_mask.values]
        sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary", fee_bps=fee_bps, long_only=False)
        z_th_prod, z_th_short = compute_production_threshold(sweep_info, z_buffer=z_buffer, z_short_buffer=None)

        positions_full = generate_positions(Z_composite, z_th=z_th_prod, z_th_short=z_th_short, mode="binary", long_only=False)

        # Slice this year
        mask = (df["date"] >= f"{y}-01-01") & (df["date"] < f"{y + 1}-01-01")
        if not mask.any():
            continue
        pos_y = positions_full[mask.values]
        ret_y = full_trade_ret[mask.values]
        net_y, _, _ = simulate_etf_spot(ret_y, pos_y, fee_bps=fee_bps)
        stitched_returns.append(net_y)
        stitched_positions.append(pos_y)

    # Aggregate stitched
    if stitched_returns:
        all_ret = np.concatenate(stitched_returns)
        all_pos = np.concatenate(stitched_positions)
        n_days = len(all_ret)
        sharpe = float(np.mean(all_ret) / np.std(all_ret) * np.sqrt(252)) if np.std(all_ret) > 1e-12 else 0.0
        total_pnl = float(np.sum(all_ret))
        n_trades = int((np.abs(all_pos) > 1e-5).sum())
        wr = float((all_ret[np.abs(all_pos) > 1e-5] > 0).mean() * 100) if n_trades > 0 else 0.0
        cum = np.cumsum(all_ret)
        peak = np.maximum.accumulate(cum)
        max_dd = float(np.max(peak - cum))
        full_res = {
            "status": "SUCCESS", "n_features": "varies",
            "sharpe": sharpe, "total_pnl": total_pnl, "n_trades": n_trades,
            "n_days": n_days, "win_rate": wr, "max_dd": max_dd,
        }
    else:
        full_res = {"status": "NO_DATA"}

    return {"yearly": yearly_results, "full": full_res}


def main():
    parser = argparse.ArgumentParser(description="A/B Test: Static Pool vs Yearly-Reselected Pool")
    parser.add_argument("-e", "--etf", type=str, default="all", help="ETF or 'all'")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Fee in bps (default: 8)")
    parser.add_argument("--z-buffer", type=float, default=0.1, help="Threshold buffer (default: 0.1)")
    parser.add_argument("--top-k", type=int, default=10, help="Top-K feature truncation (default: 10)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output report path")
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0
    etfs = AVAILABLE_ETFS if args.etf == "all" else [args.etf]

    print("=" * 90)
    print("A/B TEST: STATIC FEATURE POOL vs YEARLY-RESELECTED FEATURE POOL")
    print(f"  Scheme=ICW | Top-K={args.top_k} | Buffer={args.z_buffer} | Fee={args.fee_bps}bps")
    print(f"  Group A: admitted_pools.py (static production pool)")
    print(f"  Group B: day-model-new period-specific pools (reselected yearly)")
    print("=" * 90)

    all_results = {}

    for etf in etfs:
        print(f"\n{'─' * 90}")
        print(f"  ETF: {etf}")
        print(f"{'─' * 90}")

        # Load data once
        df = load_etf_dataset(etf)
        full_trade_ret = df["trade_return"].values.astype(np.float64)

        # Group A: Static pool
        static_pool = load_admitted_pool(etf, side="single", min_features=5)
        if not static_pool:
            print(f"  [SKIP] {etf} has no static pool.")
            continue
        print(f"\n  [Group A] Static Pool: {len(static_pool)} features")
        res_a = run_per_year_backtest(etf, static_pool, df, full_trade_ret, fee_bps, args.z_buffer, args.top_k)

        # Group B: Yearly reselected
        print(f"\n  [Group B] Yearly-Reselected Pools:")
        for y in [2022, 2023, 2024, 2025]:
            p = load_period_pool(etf, y)
            print(f"    {y}: {len(p)} features")
        res_b = run_yearly_reselected(etf, df, full_trade_ret, fee_bps, args.z_buffer, args.top_k)

        all_results[etf] = {"static": res_a, "yearly": res_b}

        # Print comparison
        print(f"\n  {'─' * 80}")
        print(f"  RESULTS: {etf}")
        print(f"  {'─' * 80}")
        print(f"  {'Period':<10} | {'Group A (Static)':<40} | {'Group B (Yearly)':<40}")
        print(f"  {'':10} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'MaxDD':>8} {'N':>5} | {'Sharpe':>8} {'PnL':>10} {'WR%':>6} {'MaxDD':>8} {'N':>5}")
        print(f"  {'-' * 10}-+-{'-' * 40}-+-{'-' * 40}")

        for y in [2022, 2023, 2024, 2025]:
            ra = res_a["yearly"].get(y, {})
            rb = res_b["yearly"].get(y, {})
            a_str = f"{ra.get('sharpe', 0):.3f}  {ra.get('total_pnl', 0):+.4f}  {ra.get('win_rate', 0):.1f}  {ra.get('max_dd', 0):.4f} {ra.get('n_trades', 0):>5}" if ra.get("status") == "SUCCESS" else "N/A".ljust(40)
            b_str = f"{rb.get('sharpe', 0):.3f}  {rb.get('total_pnl', 0):+.4f}  {rb.get('win_rate', 0):.1f}  {rb.get('max_dd', 0):.4f} {rb.get('n_trades', 0):>5}" if rb.get("status") == "SUCCESS" else "N/A".ljust(40)
            print(f"  {y:<10} | {a_str:<40} | {b_str:<40}")

        # Full period
        fa = res_a["full"]
        fb = res_b["full"]
        a_full = f"{fa.get('sharpe', 0):.3f}  {fa.get('total_pnl', 0):+.4f}  {fa.get('win_rate', 0):.1f}  {fa.get('max_dd', 0):.4f} {fa.get('n_trades', 0):>5}" if fa.get("status") == "SUCCESS" else "N/A"
        b_full = f"{fb.get('sharpe', 0):.3f}  {fb.get('total_pnl', 0):+.4f}  {fb.get('win_rate', 0):.1f}  {fb.get('max_dd', 0):.4f} {fb.get('n_trades', 0):>5}" if fb.get("status") == "SUCCESS" else "N/A"
        print(f"  {'-' * 10}-+-{'-' * 40}-+-{'-' * 40}")
        print(f"  {'FULL':<10} | {a_full:<40} | {b_full:<40}")

        # Delta
        if fa.get("status") == "SUCCESS" and fb.get("status") == "SUCCESS":
            delta_sr = fb["sharpe"] - fa["sharpe"]
            delta_pnl = fb["total_pnl"] - fa["total_pnl"]
            print(f"\n  Δ Sharpe (B-A): {delta_sr:+.3f} | Δ PnL (B-A): {delta_pnl:+.4f}")
            verdict = "YEARLY RESELECTION WINS" if delta_sr > 0 else "STATIC POOL WINS"
            print(f"  Verdict: {verdict}")

    # Save report
    report_path = Path(args.output) if args.output else HERE / "AB_YEARLY_RESELECTION_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# A/B Test: Static Pool vs Yearly-Reselected Pool\n\n")
        f.write("## Setup\n\n")
        f.write(f"- **Group A (Static)**: `admitted_pools.py` production pool (fixed)\n")
        f.write(f"- **Group B (Yearly)**: `day-model-new/data/selected_pool_*.json` (reselected per period)\n")
        f.write(f"- **Scheme**: ICW, Top-{args.top_k}, Dynamic IC (30d EMA), Binary L+S\n")
        f.write(f"- **Threshold**: Auto sweep + {args.z_buffer} buffer\n")
        f.write(f"- **Friction**: {args.fee_bps} bps\n\n")

        f.write("## Period Pool Mapping (Group B)\n\n")
        f.write("| OOS Year | Pool File | Training Window |\n")
        f.write("| --- | --- | --- |\n")
        f.write("| 2022 | selected_pool_{ETF}_single.json | 2015-2022 |\n")
        f.write("| 2023 | selected_pool_{ETF}_single_p2015_2023.json | 2015-2023 |\n")
        f.write("| 2024 | selected_pool_{ETF}_single_p2016_2024.json | 2016-2024 |\n")
        f.write("| 2025 | selected_pool_{ETF}_single_p2017_2025.json | 2017-2025 |\n\n")

        for etf in etfs:
            if etf not in all_results:
                continue
            res = all_results[etf]
            f.write(f"## {etf}\n\n")

            # Pool sizes
            static_pool = load_admitted_pool(etf, side="single", min_features=5)
            f.write(f"**Pool Sizes**: Static={len(static_pool)} | ")
            for y in [2022, 2023, 2024, 2025]:
                p = load_period_pool(etf, y)
                f.write(f"{y}:{len(p)} ")
            f.write("\n\n")

            f.write("| Year | Group | Features | Sharpe | PnL | Win Rate | Max DD | Trades |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")

            for y in [2022, 2023, 2024, 2025, "FULL"]:
                ra = res["static"]["yearly"].get(y, res["static"]["full"]) if y != "FULL" else res["static"]["full"]
                rb = res["yearly"]["yearly"].get(y, res["yearly"]["full"]) if y != "FULL" else res["yearly"]["full"]
                for label, r in [("A (Static)", ra), ("B (Yearly)", rb)]:
                    if r.get("status") == "SUCCESS":
                        f.write(f"| {y} | {label} | {r['n_features']} | {r['sharpe']:.3f} | "
                                f"{r['total_pnl']:+.4f} | {r['win_rate']:.1f}% | {r['max_dd']:.4f} | {r['n_trades']} |\n")
                    else:
                        f.write(f"| {y} | {label} | - | - | - | - | - | - |\n")

            # Summary
            fa = res["static"]["full"]
            fb = res["yearly"]["full"]
            if fa.get("status") == "SUCCESS" and fb.get("status") == "SUCCESS":
                delta = fb["sharpe"] - fa["sharpe"]
                f.write(f"\n**Δ Sharpe (B-A): {delta:+.3f}** → ")
                f.write("Yearly reselection **wins**\n\n" if delta > 0 else "Static pool **wins**\n\n")
            f.write("---\n\n")

        # Overall verdict
        f.write("## Overall Verdict\n\n")
        wins_a, wins_b = 0, 0
        for etf in etfs:
            if etf not in all_results:
                continue
            fa = all_results[etf]["static"]["full"]
            fb = all_results[etf]["yearly"]["full"]
            if fa.get("status") == "SUCCESS" and fb.get("status") == "SUCCESS":
                if fb["sharpe"] > fa["sharpe"]:
                    wins_b += 1
                else:
                    wins_a += 1
        f.write(f"- Static Pool wins: {wins_a}/{len(etfs)} ETFs\n")
        f.write(f"- Yearly Reselection wins: {wins_b}/{len(etfs)} ETFs\n")

    print(f"\n{'=' * 90}")
    print(f"Report saved to: {report_path}")
    print(f"{'=' * 90}")


if __name__ == "__main__":
    main()
