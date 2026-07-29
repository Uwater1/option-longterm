#!/usr/bin/env python3
"""
Experiment 4: Reweighting Cadence & Recent IC Decay Cutoff Test.
Compares factor re-ranking & re-weighting cadences:
  1. Daily (Current baseline: EMA30 dynamic expanding IC updated daily)
  2. Weekly (Re-weight every 5 trading days)
  3. Monthly (Re-weight at 1st trading day of each month)
  4. Quarterly (Re-weight at start of each quarter)
  5. Yearly (Re-weight at 1st trading day of each year)
  6. Monthly + Decay Cutoff (Monthly re-weighting, but if trailing 30d IC < 0, zero out weight immediately)
  7. Monthly + 60d Decay Cutoff (Monthly re-weighting, zero out if trailing 60d IC < 0)

Evaluates OOS performance (2022-01 ~ 2026-01) under 8 bps friction on 300ETF, 500ETF, 159915ETF.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from strategy import generate_positions, simulate_etf_spot, sweep_optimal_threshold
from scipy.stats import rankdata

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
FEE_BPS = 0.0008
BURN_IN = 252
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"


def compute_cadence_signal(Z_std: np.ndarray, signs: np.ndarray, IC_mat: np.ndarray, trade_returns: np.ndarray,
                           dates: pd.Series, pool: list, top_k: int = 10, cadence: str = "daily",
                           decay_cutoff: bool = False, decay_window: int = 30) -> np.ndarray:
    """
    Compute composite Z signal under different reweighting cadences and optional decay cutoffs.
    """
    T, N = Z_std.shape
    Z_signed = Z_std * signs
    Z_composite = np.zeros(T, dtype=np.float64)

    # Compute trailing 30d/60d daily IC matrix for decay detection
    trailing_ic = np.zeros((T, N), dtype=np.float64)
    if decay_cutoff:
        daily_ic = Z_signed * trade_returns[:, None]
        for t in range(decay_window, T):
            trailing_ic[t] = np.mean(daily_ic[t - decay_window:t], axis=0)

    # Determine reweighting days
    reweight_flags = np.zeros(T, dtype=bool)
    if cadence == "daily":
        reweight_flags[:] = True
    elif cadence == "weekly":
        reweight_flags[::5] = True
        reweight_flags[0] = True
    elif cadence == "monthly":
        months = dates.dt.month.values
        reweight_flags[0] = True
        for t in range(1, T):
            if months[t] != months[t - 1]:
                reweight_flags[t] = True
    elif cadence == "quarterly":
        quarters = dates.dt.quarter.values
        reweight_flags[0] = True
        for t in range(1, T):
            if quarters[t] != quarters[t - 1]:
                reweight_flags[t] = True
    elif cadence == "yearly":
        years = dates.dt.year.values
        reweight_flags[0] = True
        for t in range(1, T):
            if years[t] != years[t - 1]:
                reweight_flags[t] = True

    se_ic = 1.0 / np.sqrt(1700)
    current_w = np.ones(N, dtype=np.float64) / float(N) if N > 0 else np.empty(0)

    for t in range(T):
        if reweight_flags[t]:
            ic_t = IC_mat[t]
            top_idx = np.argsort(ic_t)[-top_k:] if (1 <= top_k < N) else np.arange(N)
            w_t = np.zeros(N, dtype=np.float64)
            raw_w = np.maximum(0.0, ic_t[top_idx] - se_ic)
            w_sum = raw_w.sum()
            if w_sum < 1e-12:
                w_t[top_idx] = 1.0 / float(len(top_idx))
            else:
                w_t[top_idx] = raw_w / w_sum
            current_w = w_t.copy()

        w_active = current_w.copy()
        # Apply decay cutoff if active
        if decay_cutoff and t >= decay_window:
            decay_mask = trailing_ic[t] < 0.0
            w_active[decay_mask] = 0.0
            w_sum = w_active.sum()
            if w_sum > 1e-12:
                w_active = w_active / w_sum

        Z_composite[t] = Z_signed[t] @ w_active

    return Z_composite


def run_experiment():
    print("================================================================================")
    print("EXPERIMENT 4: REWEIGHTING CADENCE & RECENT IC DECAY CUTOFF TEST")
    print("================================================================================")

    cadences = [
        ("1. Daily (Baseline)", "daily", False, 30),
        ("2. Weekly", "weekly", False, 30),
        ("3. Monthly", "monthly", False, 30),
        ("4. Quarterly", "quarterly", False, 30),
        ("5. Yearly", "yearly", False, 30),
        ("6. Monthly + 30d Decay Cutoff", "monthly", True, 30),
        ("7. Monthly + 60d Decay Cutoff", "monthly", True, 60),
        ("8. Daily + 30d Decay Cutoff", "daily", True, 30),
    ]

    records = []

    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue

        df = load_etf_dataset(etf)
        full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0).values
        dates = df["date"]

        X_raw, signs, fn = build_pool_feature_matrix(df, pool)
        Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
        IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=BURN_IN)

        # Smooth IC_mat with EMA30
        alpha = 2.0 / (30.0 + 1.0)
        IC_mat_ema = np.zeros_like(IC_mat)
        IC_mat_ema[0] = IC_mat[0]
        for t_idx in range(1, len(IC_mat)):
            IC_mat_ema[t_idx] = alpha * IC_mat[t_idx] + (1.0 - alpha) * IC_mat_ema[t_idx - 1]

        t_start_ts = pd.Timestamp(START_DATE)
        t_end_ts = pd.Timestamp(END_DATE)
        oos_mask = (dates >= t_start_ts) & (dates < t_end_ts)
        train_mask = dates < t_start_ts

        print(f"\n---> Testing Cadences for {etf}...")

        for cad_name, cad_type, decay_flag, decay_win in cadences:
            Z_comp = compute_cadence_signal(
                Z_std, signs, IC_mat_ema, full_trade_ret, dates, pool,
                top_k=10, cadence=cad_type, decay_cutoff=decay_flag, decay_window=decay_win
            )

            # Auto threshold sweep on train data
            Z_train = Z_comp[train_mask.values]
            ret_train = full_trade_ret[train_mask.values]
            sw_res = sweep_optimal_threshold(Z_train, ret_train, fee_bps=FEE_BPS, long_only=False)

            z_l = sw_res["optimal_z_th_long"] + 0.10
            z_s = sw_res["optimal_z_th_short"] + 0.10

            pos = generate_positions(Z_comp, z_th=z_l, z_th_short=z_s, mode="binary", long_only=False)
            net_ret, pnl, trades = simulate_etf_spot(full_trade_ret, pos, fee_bps=FEE_BPS)

            # Filter to OOS
            oos_net = net_ret[oos_mask.values]
            oos_pos = pos[oos_mask.values]

            sharpe = np.mean(oos_net) / np.std(oos_net) * np.sqrt(252) if np.std(oos_net) > 1e-12 else 0.0
            raw_ret = full_trade_ret[oos_mask.values] * oos_pos
            raw_sr = np.mean(raw_ret) / np.std(raw_ret) * np.sqrt(252) if np.std(raw_ret) > 1e-12 else 0.0

            total_pnl = np.sum(oos_net)
            cum_net = np.cumsum(oos_net)
            peak = np.maximum.accumulate(cum_net)
            dd = (peak - cum_net)
            max_dd = np.max(dd) if len(dd) > 0 else 0.0

            traded_mask = np.abs(oos_pos) > 1e-5
            win_rate = (oos_net[traded_mask] > 0).mean() * 100.0 if traded_mask.sum() > 0 else 0.0
            n_trades = len(trades)
            turnover = np.sum(np.abs(np.diff(pos[oos_mask.values], prepend=0.0))) / (len(oos_net) / 252.0)

            records.append({
                "ETF": etf,
                "Cadence": cad_name,
                "Cost Sharpe": sharpe,
                "Raw Sharpe": raw_sr,
                "Total PnL": total_pnl,
                "Max DD": max_dd,
                "Win Rate": win_rate,
                "Turnover": turnover,
            })

    df = pd.DataFrame(records)

    print("\n================================================================================")
    print("REWEIGHTING CADENCE EXPERIMENT RESULTS SUMMARY")
    print("================================================================================")
    print(df.to_string(index=False))

    avg_df = df.groupby("Cadence")[["Cost Sharpe", "Total PnL", "Turnover", "Win Rate"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n--------------------------------------------------------------------------------")
    print("CROSS-ETF AVERAGE PERFORMANCE BY REWEIGHTING CADENCE")
    print("--------------------------------------------------------------------------------")
    print(avg_df.to_string(index=False))

    out_csv = NEWTRADE_DIR / "tests" / "test_reweight_cadence_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved experiment results to {out_csv}")


if __name__ == "__main__":
    run_experiment()
