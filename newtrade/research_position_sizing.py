#!/usr/bin/env python3
"""
NewTrade — Comprehensive Bug-Free Position Sizing A/B Benchmark

Evaluates clean, zero-lookahead position sizing rules against Binary Baseline across:
  - 300ETF, 500ETF, 159915ETF
  - OOS Window: 2022-01-01 ~ 2026-01-01 (1000 trading days)
  - Intraday 1m Stop-Loss: time_decay_trailing = 0.03
  - Friction: 8.0 bps proportional transaction cost
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from utils import (
    load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
    expanding_zscore_numba, rolling_tail_ic_numba, load_cluster_assignments,
)
from weighting import compute_icw_hysteresis, adaptive_exit_rank
from strategy import (
    generate_positions, simulate_etf_spot, calculate_metrics,
    sweep_optimal_threshold, compute_production_threshold,
)
from research_stoploss import load_intraday_bars_dict, simulate_full_series
from run_backtest import resolve_ic_ema_span

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
FEE_BPS_DEFAULT = 8.0
TAIL_WINDOW = 480
TAIL_PCT = 0.10
TOP_K = 10


def evaluate_arm_positions(dates_oos: pd.Series, positions_oos: np.ndarray,
                           ret_oos: np.ndarray, bars_dict: dict, fee_bps: float) -> dict:
    if bars_dict:
        net_returns, raw_returns, stop_hits, trig_pct = simulate_full_series(
            dates_oos, positions_oos, bars_dict, method="time_decay_trailing",
            param=0.03, fee_bps=fee_bps
        )
    else:
        net_returns, raw_returns, fees = simulate_etf_spot(ret_oos, positions_oos, fee_bps=fee_bps)

    metrics = calculate_metrics(net_returns, raw_returns, positions_oos, dates=dates_oos)
    active_mask = np.abs(positions_oos) > 1e-5
    metrics["avg_abs_pos"] = round(float(np.mean(np.abs(positions_oos[active_mask]))), 3) if active_mask.any() else 0.0
    return metrics


def main():
    fee_bps = FEE_BPS_DEFAULT / 10000.0

    print("=" * 95)
    print("NEWTRADE POSITION SIZING MASTER BENCHMARK (BUG-FREE AUDITED VERIFICATION)")
    print(f"OOS Window: [2022-01-01 ~ 2026-01-01] | Intraday Stop-Loss: 3.0% Time-Decay | Friction: {FEE_BPS_DEFAULT} bps")
    print("=" * 95)

    etf_data = {}
    baselines = {}

    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        df = load_etf_dataset(etf)
        full_trade_ret = (df["trade_return"].values.astype(np.float64)
                         if "trade_return" in df.columns
                         else df["close"].pct_change().fillna(0.0).values)

        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        feat_to_cluster = load_cluster_assignments(etf, "single")
        cluster_ids = None
        if feat_to_cluster:
            cids = [feat_to_cluster.get(fn, 1000 + i) for i, fn in enumerate(feat_names)]
            cluster_ids = np.array(cids, dtype=np.int64)

        ic_raw = rolling_tail_ic_numba(Z_std, signs, full_trade_ret, window=TAIL_WINDOW, tail_pct=TAIL_PCT, burn_in=burn_in)
        ema_span = resolve_ic_ema_span(etf, None)
        T_z, N_z = Z_std.shape
        alpha_e = 2.0 / (ema_span + 1.0)
        ic_smoothed = np.zeros_like(ic_raw)
        ic_smoothed[0] = ic_raw[0]
        for t_i in range(1, T_z):
            ic_smoothed[t_i] = alpha_e * ic_raw[t_i] + (1.0 - alpha_e) * ic_smoothed[t_i - 1]

        n_train_ts = pd.Timestamp("2022-01-01")
        train_mask = (df["date"] < n_train_ts).values
        n_train = int(train_mask.sum())
        if n_train < 252:
            n_train = 1700

        er = adaptive_exit_rank(N_z, TOP_K)
        Z_composite = compute_icw_hysteresis(
            Z_std, signs, ic_smoothed,
            cluster_ids=cluster_ids,
            n_train=n_train, top_k=TOP_K,
            exit_rank=er, max_per_group=1
        )

        t_start = pd.Timestamp("2022-01-01")
        t_end = pd.Timestamp("2026-01-01")
        oos_mask = ((df["date"] >= t_start) & (df["date"] < t_end)).values
        bars_dict = load_intraday_bars_dict(etf)

        Z_train = Z_composite[train_mask]
        ret_train = full_trade_ret[train_mask]
        sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary", fee_bps=fee_bps, long_only=False)

        etf_data[etf] = {
            "df": df,
            "full_trade_ret": full_trade_ret,
            "Z_composite": Z_composite,
            "train_mask": train_mask,
            "oos_mask": oos_mask,
            "sweep_info": sweep_info,
            "bars_dict": bars_dict,
        }

        # Calculate baseline
        df_oos = df[oos_mask].reset_index(drop=True)
        dates_oos = df_oos["date"]
        Z_oos = Z_composite[oos_mask]
        ret_oos = full_trade_ret[oos_mask]
        z_prod_l, z_prod_s = compute_production_threshold(sweep_info, z_buffer=0.10)
        pos_a = generate_positions(Z_oos, z_th=z_prod_l, z_th_short=z_prod_s, mode="binary", long_only=False)
        met_a = evaluate_arm_positions(dates_oos, pos_a, ret_oos, bars_dict, fee_bps)
        baselines[etf] = met_a

    candidate_rules = [
        ("Binary Baseline (m=1.00)", "binary", 1.00, 0.00),
        ("Fast Ramp Linear (m=0.50, dz=0.20)", "fast_ramp_linear", 0.50, 0.20),
        ("Fast Ramp Linear (m=0.50, dz=0.30)", "fast_ramp_linear", 0.50, 0.30),
        ("Fast Ramp Linear (m=0.50, dz=0.40)", "fast_ramp_linear", 0.50, 0.40),
        ("Fast Ramp Quad (m=0.50, dz=0.20)", "fast_ramp_quadratic", 0.50, 0.20),
        ("Fast Ramp Quad (m=0.50, dz=0.30)", "fast_ramp_quadratic", 0.50, 0.30),
        ("Fast Ramp Quad (m=0.50, dz=0.40)", "fast_ramp_quadratic", 0.50, 0.40),
        ("Fast Ramp Tanh (m=0.50, dz=0.20)", "fast_ramp_tanh", 0.50, 0.20),
        ("Fast Ramp Tanh (m=0.50, dz=0.30)", "fast_ramp_tanh", 0.50, 0.30),
        ("Fast Ramp Quad (m=0.70, dz=0.40)", "fast_ramp_quadratic", 0.70, 0.40),
        ("Fast Ramp Linear (m=0.70, dz=0.40)", "fast_ramp_linear", 0.70, 0.40),
    ]

    results = []

    for rule_label, mode, m, dz in candidate_rules:
        for etf, d in etf_data.items():
            df_oos = d["df"][d["oos_mask"]].reset_index(drop=True)
            dates_oos = df_oos["date"]
            Z_oos = d["Z_composite"][d["oos_mask"]]
            ret_oos = d["full_trade_ret"][d["oos_mask"]]
            z_prod_l, z_prod_s = compute_production_threshold(d["sweep_info"], z_buffer=0.10)

            if mode == "binary":
                pos = generate_positions(Z_oos, z_th=z_prod_l, z_th_short=z_prod_s, mode="binary", long_only=False)
            else:
                pos = generate_positions(Z_oos, z_th=z_prod_l, z_th_short=z_prod_s, mode=mode, long_only=False, min_pos=m, delta_z_full=dz)

            met = evaluate_arm_positions(dates_oos, pos, ret_oos, d["bars_dict"], fee_bps)

            results.append({
                "Rule": rule_label,
                "ETF": etf,
                "CostSharpe": met["cost_sharpe"],
                "TotalPnL": met["total_pnl"],
                "MaxDD": met["max_drawdown"],
                "WinRate": met["win_rate_pct"],
                "Trades": met["n_trades"],
                "AvgPos": met["avg_abs_pos"],
            })

    df_res = pd.DataFrame(results)

    print("\n" + "=" * 95)
    print("MASTER SUMMARY TABLE (ALL ETFS COMBINED)")
    print("=" * 95)

    summary = df_res.groupby("Rule").agg(
        AvgSharpe=("CostSharpe", "mean"),
        AvgPnL=("TotalPnL", "mean"),
        AvgMaxDD=("MaxDD", "mean"),
        AvgWinRate=("WinRate", "mean"),
        AvgPosSize=("AvgPos", "mean"),
    ).reset_index().sort_values("AvgSharpe", ascending=False)

    base_sr = summary.loc[summary["Rule"] == "Binary Baseline (m=1.00)", "AvgSharpe"].values[0]
    base_dd = summary.loc[summary["Rule"] == "Binary Baseline (m=1.00)", "AvgMaxDD"].values[0]

    print(f"\n{'Rule':<45} {'AvgSharpe':>10} {'Delta':>8} {'AvgPnL':>10} {'AvgMaxDD':>9} {'MaxDD Red.':>11} {'AvgPos':>8}")
    print("-" * 108)
    for _, r in summary.iterrows():
        sr_delta = r["AvgSharpe"] - base_sr
        dd_red = (r["AvgMaxDD"] - base_dd) / base_dd * 100.0
        marker = " *" if r["Rule"] == "Binary Baseline (m=1.00)" else ""
        print(f"{r['Rule']:<45} {r['AvgSharpe']:>10.3f} {sr_delta:>+8.3f} {r['AvgPnL']:>10.4f} {r['AvgMaxDD']:>9.4f} {dd_red:>+10.1f}% {r['AvgPosSize']:>8.2f}{marker}")

    print("\n" + "=" * 95)
    print("PER-ETF DETAILED BREAKDOWN")
    print("=" * 95)
    for etf in AVAILABLE_ETFS:
        sub = df_res[df_res["ETF"] == etf].sort_values("CostSharpe", ascending=False)
        base_sr = baselines[etf]["cost_sharpe"]
        base_dd = baselines[etf]["max_drawdown"]
        print(f"\n--- {etf} (Baseline Sharpe: {base_sr:.3f}, Baseline MaxDD: {base_dd:.4f}) ---")
        print(f"{'Rule':<45} {'CostSharpe':>10} {'Delta':>8} {'TotalPnL':>10} {'MaxDD':>8} {'WR%':>6} {'AvgPos':>8}")
        print("-" * 105)
        for _, r in sub.iterrows():
            sr_delta = r["CostSharpe"] - base_sr
            marker = " *" if r["Rule"] == "Binary Baseline (m=1.00)" else ""
            print(f"{r['Rule']:<45} {r['CostSharpe']:>10.3f} {sr_delta:>+8.3f} {r['TotalPnL']:>10.4f} {r['MaxDD']:>8.4f} {r['WinRate']:>6.1f} {r['AvgPos']:>8.2f}{marker}")


if __name__ == "__main__":
    main()
