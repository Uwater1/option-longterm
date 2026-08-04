#!/usr/bin/env python3
"""
A/B Test: Hysteresis Exit-Rank Sweep x Threshold Combination

Sweeps exit_rank and combines hysteresis with the two best threshold arms:
  - Hysteresis + Baseline threshold (argmax + 0.10)
  - Hysteresis + 90%-of-peak threshold (conservative)

Tests whether a wider exit_rank (stickier selection) further improves performance,
and whether combining signal stabilization with threshold conservatism is additive.

Usage:
    python newtrade/tests/test_hysteresis_sweep.py
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, rolling_tail_ic_numba, load_cluster_assignments,
)
from weighting import compute_icw
from strategy import (
    sweep_optimal_threshold, compute_production_threshold,
    simulate_etf_spot, calculate_metrics, generate_positions,
)
from research_stoploss import load_intraday_bars_dict, simulate_full_series
from run_backtest import resolve_ic_ema_span
from test_zthreshold_ab import compute_icw_hysteresis, arm_baseline, arm_90pct_peak, arm_rolling_percentile

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
TAIL_WINDOW = 480
TAIL_PCT = 0.10
TOP_K = 10
FEE_BPS_DEFAULT = 8.0


def adaptive_exit_rank(n_features: int, top_k: int = 10, hard_cap: int = 25) -> int:
    """Compute pool-adaptive exit_rank: min(top_k + (N-top_k)//2, hard_cap)."""
    formula = top_k + (n_features - top_k) // 2
    return min(formula, hard_cap)


def evaluate_with_stoploss(positions, trade_returns, oos_mask, fee_bps, dates, bars_dict):
    """Evaluate positions with stoploss if available."""
    pos_oos = positions[oos_mask]
    ret_oos = trade_returns[oos_mask]
    df_dates = dates[oos_mask] if dates is not None else None
    if isinstance(df_dates, pd.Series):
        df_dates = df_dates.reset_index(drop=True)

    if bars_dict:
        net_ret, raw_ret, fees, stop_hits, trig_pct = simulate_full_series(
            df_dates, pos_oos, bars_dict, method="time_decay_trailing",
            param=0.03, fee_bps=fee_bps
        )
    else:
        net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, pos_oos, fee_bps=fee_bps)

    return calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_dates)


def main():
    parser = argparse.ArgumentParser(description="Hysteresis Exit-Rank Sweep x Threshold Combo")
    parser.add_argument("--fee-bps", type=float, default=FEE_BPS_DEFAULT)
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("-o", "--output", type=str, default=None)
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0

    # Build per-ETF exit_rank list: adaptive + fixed comparisons
    # We'll collect all unique ERs across ETFs for the sweep
    all_exit_ranks = set([15, 20, 25])  # fixed comparisons
    etf_adaptive_er = {}

    print("=" * 90)
    print("HYSTERESIS SWEEP v2: adaptive cap + RollPct480")
    print(f"thresholds=[Baseline, 90pct_Peak, RollPct480]")
    print(f"OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps | Stoploss=ON")
    print("=" * 90)

    results = []

    for etf in AVAILABLE_ETFS:
        print(f"\n{'='*70}")
        print(f"  {etf}")
        print(f"{'='*70}")

        # Load data
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool or len(pool) < 10:
            print(f"  [SKIP] Pool too small")
            continue

        df = load_etf_dataset(etf)
        full_trade_ret = (df["trade_return"].values.astype(np.float64)
                         if "trade_return" in df.columns
                         else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        # Cluster
        feat_to_cluster = load_cluster_assignments(etf, "single")
        cluster_ids = None
        if feat_to_cluster:
            cids = []
            next_cid = (max(feat_to_cluster.values()) + 1) if feat_to_cluster else 1000
            for fn in feat_names:
                if fn in feat_to_cluster:
                    cids.append(feat_to_cluster[fn])
                else:
                    cids.append(next_cid)
                    next_cid += 1
            cluster_ids = np.array(cids, dtype=np.int64)
            print(f"  [INFO] {len(set(cluster_ids))} ONC clusters, pool={len(pool)} features")

        # 1m bars
        bars_dict = load_intraday_bars_dict(etf)
        if bars_dict:
            print(f"  [INFO] 1m bars: {len(bars_dict)} days")

        # IC matrix (shared across all arms)
        ic_raw = rolling_tail_ic_numba(Z_std, signs, full_trade_ret,
                                       window=TAIL_WINDOW, tail_pct=TAIL_PCT, burn_in=burn_in)
        ema_span = resolve_ic_ema_span(etf, None)
        T, N = Z_std.shape
        alpha_ema = 2.0 / (ema_span + 1.0)
        ic_mat = np.zeros_like(ic_raw)
        ic_mat[0] = ic_raw[0]
        for t in range(1, T):
            ic_mat[t] = alpha_ema * ic_raw[t] + (1.0 - alpha_ema) * ic_mat[t - 1]

        # Masks
        n_train_ts = pd.Timestamp(args.start_date)
        train_mask = (df["date"] < n_train_ts).values
        n_train = int(train_mask.sum())
        if n_train < 252:
            n_train = 1700
        t_start = pd.Timestamp(args.start_date)
        t_end = pd.Timestamp(args.end_date)
        oos_mask = ((df["date"] >= t_start) & (df["date"] < t_end)).values
        dates = df["date"]

        # Compute adaptive exit_rank for this ETF
        N_feats = len(pool)
        adapt_er = adaptive_exit_rank(N_feats, TOP_K, hard_cap=25)
        etf_adaptive_er[etf] = adapt_er
        # Exit ranks to test: adaptive, adaptive-3, adaptive+3, plus fixed 15/20/25
        er_set = sorted(set([adapt_er, max(TOP_K + 2, adapt_er - 3), adapt_er + 3, 15, 20, 25]))
        # Remove duplicates and values <= top_k
        er_set = [er for er in er_set if er > TOP_K]
        all_exit_ranks.update(er_set)
        print(f"  [INFO] Adaptive ER={adapt_er} (N={N_feats}). Testing: {er_set}")

        # --- Baseline (no hysteresis) for reference ---
        Z_base = compute_icw(Z_std, signs, pool=pool, n_train=n_train,
                             expanding_ic=ic_raw, top_k=TOP_K, ic_ema_span=ema_span,
                             cluster_ids=cluster_ids, max_per_group=1)
        pos_base, _ = arm_baseline(Z_base, full_trade_ret, train_mask, fee_bps)
        m_base = evaluate_with_stoploss(pos_base, full_trade_ret, oos_mask, fee_bps, dates, bars_dict)
        results.append({
            "Arm": "NoHyst_Baseline", "ExitRank": 0, "Threshold": "Baseline",
            "ETF": etf, "CostSharpe": m_base.get("cost_sharpe", 0),
            "TotalPnL": m_base.get("total_pnl", 0), "MaxDD": m_base.get("max_drawdown", 0),
            "WinRate": m_base.get("win_rate_pct", 0), "Trades": m_base.get("n_trades", 0),
        })
        print(f"  [NoHyst_Baseline] Sharpe={m_base.get('cost_sharpe',0):.3f}")

        # --- Sweep exit_rank x threshold ---
        for exit_rank in er_set:
            # Compute hysteresis Z_composite
            Z_hyst = compute_icw_hysteresis(
                Z_std, signs, ic_mat, cluster_ids, n_train,
                top_k=TOP_K, exit_rank=exit_rank, max_per_group=1
            )

            is_adaptive = (exit_rank == adapt_er)
            tag = "*" if is_adaptive else " "

            # Threshold A: Baseline
            pos_a, _ = arm_baseline(Z_hyst, full_trade_ret, train_mask, fee_bps)
            m_a = evaluate_with_stoploss(pos_a, full_trade_ret, oos_mask, fee_bps, dates, bars_dict)
            results.append({
                "Arm": f"Hyst_ER{exit_rank}_Base", "ExitRank": exit_rank, "Threshold": "Baseline",
                "ETF": etf, "CostSharpe": m_a.get("cost_sharpe", 0),
                "TotalPnL": m_a.get("total_pnl", 0), "MaxDD": m_a.get("max_drawdown", 0),
                "WinRate": m_a.get("win_rate_pct", 0), "Trades": m_a.get("n_trades", 0),
            })

            # Threshold B: 90%-of-peak
            pos_b, _ = arm_90pct_peak(Z_hyst, full_trade_ret, train_mask, fee_bps)
            m_b = evaluate_with_stoploss(pos_b, full_trade_ret, oos_mask, fee_bps, dates, bars_dict)
            results.append({
                "Arm": f"Hyst_ER{exit_rank}_90pct", "ExitRank": exit_rank, "Threshold": "90pct",
                "ETF": etf, "CostSharpe": m_b.get("cost_sharpe", 0),
                "TotalPnL": m_b.get("total_pnl", 0), "MaxDD": m_b.get("max_drawdown", 0),
                "WinRate": m_b.get("win_rate_pct", 0), "Trades": m_b.get("n_trades", 0),
            })

            # Threshold C: Rolling Percentile 480d
            pos_c, _ = arm_rolling_percentile(Z_hyst, full_trade_ret, train_mask, fee_bps)
            m_c = evaluate_with_stoploss(pos_c, full_trade_ret, oos_mask, fee_bps, dates, bars_dict)
            results.append({
                "Arm": f"Hyst_ER{exit_rank}_RollPct", "ExitRank": exit_rank, "Threshold": "RollPct",
                "ETF": etf, "CostSharpe": m_c.get("cost_sharpe", 0),
                "TotalPnL": m_c.get("total_pnl", 0), "MaxDD": m_c.get("max_drawdown", 0),
                "WinRate": m_c.get("win_rate_pct", 0), "Trades": m_c.get("n_trades", 0),
            })

            print(f" {tag}[ER={exit_rank:2d}] Base={m_a.get('cost_sharpe',0):.3f} | "
                  f"90pct={m_b.get('cost_sharpe',0):.3f} | "
                  f"RollPct={m_c.get('cost_sharpe',0):.3f}")

    # ─── Summary ───────────────────────────────────────────────────────────────
    if not results:
        print("\nERROR: No results.")
        return

    df_res = pd.DataFrame(results)

    print("\n" + "=" * 90)
    print("RESULTS - RANKED BY AVG COST SHARPE")
    print("=" * 90)

    avg = df_res.groupby("Arm").agg(
        AvgSharpe=("CostSharpe", "mean"),
        AvgPnL=("TotalPnL", "mean"),
        AvgMaxDD=("MaxDD", "mean"),
        AvgWR=("WinRate", "mean"),
        AvgTrades=("Trades", "mean"),
    ).reset_index().sort_values("AvgSharpe", ascending=False)

    base_sr = avg.loc[avg["Arm"] == "NoHyst_Baseline", "AvgSharpe"].values
    base_sr = base_sr[0] if len(base_sr) > 0 else 0.0

    print(f"\n{'Rank':<5} {'Arm':<25} {'AvgSharpe':>10} {'Delta':>8} {'AvgPnL':>10} "
          f"{'AvgMaxDD':>9} {'AvgWR%':>7} {'Trades':>7}")
    print("-" * 85)
    for rank_idx, (_, row) in enumerate(avg.iterrows(), 1):
        delta = row["AvgSharpe"] - base_sr
        marker = " *" if row["Arm"] == "NoHyst_Baseline" else ""
        print(f"{rank_idx:<5} {row['Arm']:<25} {row['AvgSharpe']:>10.3f} {delta:>+8.3f} "
              f"{row['AvgPnL']:>10.4f} {row['AvgMaxDD']:>9.4f} {row['AvgWR']:>7.1f} "
              f"{row['AvgTrades']:>7.0f}{marker}")

    # Per-ETF: show adaptive ER result
    print("\n" + "-" * 90)
    print("PER-ETF ADAPTIVE ER RESULT (capped formula)")
    print("-" * 90)
    for etf in AVAILABLE_ETFS:
        aer = etf_adaptive_er.get(etf, "?")
        sub = df_res[(df_res["ETF"] == etf) & (df_res["ExitRank"] == aer)]
        base_etf = df_res[(df_res["ETF"] == etf) & (df_res["Arm"] == "NoHyst_Baseline")]
        base_val = base_etf.iloc[0]["CostSharpe"] if not base_etf.empty else 0
        if not sub.empty:
            best = sub.sort_values("CostSharpe", ascending=False).iloc[0]
            print(f"  {etf} (ER={aer}): {best['Arm']} Sharpe={best['CostSharpe']:.3f} "
                  f"(vs base {base_val:.3f}, delta={best['CostSharpe']-base_val:+.3f})")

    # Exit-rank trend
    print("\n" + "-" * 90)
    print("EXIT-RANK TREND (avg Sharpe across ETFs)")
    print("-" * 90)
    for er in sorted(all_exit_ranks):
        er_sub = df_res[df_res["ExitRank"] == er]
        if er_sub.empty:
            continue
        avg_base = er_sub[er_sub["Threshold"] == "Baseline"]["CostSharpe"].mean()
        avg_90 = er_sub[er_sub["Threshold"] == "90pct"]["CostSharpe"].mean()
        avg_rp = er_sub[er_sub["Threshold"] == "RollPct"]["CostSharpe"].mean()
        print(f"  ER={er:2d}: Base={avg_base:.3f} | 90pct={avg_90:.3f} | RollPct={avg_rp:.3f}")

    # Save
    out_csv = Path(args.output) if args.output else HERE / "hysteresis_sweep_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nSaved to {out_csv}")
    print("[OK] Hysteresis sweep complete.")


if __name__ == "__main__":
    main()
