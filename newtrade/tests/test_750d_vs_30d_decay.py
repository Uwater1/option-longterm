#!/usr/bin/env python3
"""
Experiment 5: 750d Long-Term Rolling Window vs 30d Short-Term IC & Cadence Interaction.
Tests long-term 750d A-share market cycle window vs 252d, 504d, and 30d across cadences (Daily, Weekly, Monthly, Yearly).

Compares:
  - Metric windows: 30d EMA, 252d Rolling, 504d Rolling, 750d Rolling
  - Reweighting cadences: Daily, Weekly, Monthly, Yearly
  - Long-term Decay Cutoffs: 252d IC < 0 cutoff, 504d IC < 0 cutoff, 750d IC < 0 cutoff vs 30d

Evaluates OOS performance (2022-01 ~ 2026-01) under 8 bps friction on 300ETF, 500ETF, 159915ETF.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
sys.path.insert(0, str(NEWTRADE_DIR))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba, expanding_factor_score_numba
from strategy import generate_positions, simulate_etf_spot, sweep_optimal_threshold

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
FEE_BPS = 0.0008
BURN_IN = 252
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"


def compute_window_cadence_signal(Z_std: np.ndarray, signs: np.ndarray, IC_mat: np.ndarray, trade_returns: np.ndarray,
                                  dates: pd.Series, pool: list, top_k: int = 10, cadence: str = "daily",
                                  decay_cutoff_window: int = None) -> np.ndarray:
    """
    Compute composite Z signal under specific metric window, cadence, and optional decay cutoff.
    """
    T, N = Z_std.shape
    Z_signed = Z_std * signs
    Z_composite = np.zeros(T, dtype=np.float64)

    # Compute trailing daily IC matrix for long-term decay detection
    trailing_ic = np.zeros((T, N), dtype=np.float64)
    if decay_cutoff_window and decay_cutoff_window > 0:
        daily_ic = Z_signed * trade_returns[:, None]
        for t in range(decay_cutoff_window, T):
            trailing_ic[t] = np.mean(daily_ic[t - decay_cutoff_window:t], axis=0)

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
        if decay_cutoff_window and t >= decay_cutoff_window:
            decay_mask = trailing_ic[t] < 0.0
            w_active[decay_mask] = 0.0
            w_sum = w_active.sum()
            if w_sum > 1e-12:
                w_active = w_active / w_sum

        Z_composite[t] = Z_signed[t] @ w_active

    return Z_composite


def run_experiment():
    print("================================================================================")
    print("EXPERIMENT 5: 750d LONG-TERM ROLLING WINDOW VS 30d SHORT-TERM IC & CADENCE")
    print("================================================================================")

    test_matrix = [
        # (Label, metric_type, window_span, cadence, decay_cutoff_window)
        ("1. 30d EMA IC — Daily Reweight", "ic_ema", 30, "daily", None),
        ("2. 30d EMA IC — Monthly Reweight", "ic_ema", 30, "monthly", None),
        ("3. 252d Rolling Score — Daily", "score_multi", 252, "daily", None),
        ("4. 252d Rolling Score — Monthly", "score_multi", 252, "monthly", None),
        ("5. 504d Rolling Score — Daily", "score_multi", 504, "daily", None),
        ("6. 504d Rolling Score — Monthly", "score_multi", 504, "monthly", None),
        ("7. 750d Rolling Score — Daily", "score_multi", 750, "daily", None),
        ("8. 750d Rolling Score — Monthly", "score_multi", 750, "monthly", None),
        ("9. 750d Rolling Score — Yearly", "score_multi", 750, "yearly", None),
        ("10. Monthly + 252d Long-Term Decay Cutoff", "ic_ema", 30, "monthly", 252),
        ("11. Monthly + 504d Long-Term Decay Cutoff", "ic_ema", 30, "monthly", 504),
        ("12. Monthly + 750d Long-Term Decay Cutoff", "ic_ema", 30, "monthly", 750),
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

        # Precompute IC_mat EMA30
        IC_mat_raw = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=BURN_IN)
        alpha = 2.0 / (30.0 + 1.0)
        IC_mat_ema30 = np.zeros_like(IC_mat_raw)
        IC_mat_ema30[0] = IC_mat_raw[0]
        for t_idx in range(1, len(IC_mat_raw)):
            IC_mat_ema30[t_idx] = alpha * IC_mat_raw[t_idx] + (1.0 - alpha) * IC_mat_ema30[t_idx - 1]

        # Precompute Score matrices for 252d, 504d, 750d
        Score_mat_252 = expanding_factor_score_numba(Z_std, signs, full_trade_ret, burn_in=BURN_IN, score_weights=(0.70, 0.0, 0.30), mono_window=252)
        Score_mat_504 = expanding_factor_score_numba(Z_std, signs, full_trade_ret, burn_in=BURN_IN, score_weights=(0.70, 0.0, 0.30), mono_window=504)
        Score_mat_750 = expanding_factor_score_numba(Z_std, signs, full_trade_ret, burn_in=BURN_IN, score_weights=(0.70, 0.0, 0.30), mono_window=750)

        t_start_ts = pd.Timestamp(START_DATE)
        t_end_ts = pd.Timestamp(END_DATE)
        oos_mask = (dates >= t_start_ts) & (dates < t_end_ts)
        train_mask = dates < t_start_ts

        print(f"\n---> Testing 750d vs 30d Windows on {etf}...")

        for label, mtype, wspan, cad, dcutoff in test_matrix:
            if mtype == "ic_ema":
                mat_to_use = IC_mat_ema30
            elif wspan == 252:
                mat_to_use = Score_mat_252
            elif wspan == 504:
                mat_to_use = Score_mat_504
            else:
                mat_to_use = Score_mat_750

            Z_comp = compute_window_cadence_signal(
                Z_std, signs, mat_to_use, full_trade_ret, dates, pool,
                top_k=10, cadence=cad, decay_cutoff_window=dcutoff
            )

            # Threshold sweep on train
            Z_train = Z_comp[train_mask.values]
            ret_train = full_trade_ret[train_mask.values]
            sw_res = sweep_optimal_threshold(Z_train, ret_train, fee_bps=FEE_BPS, long_only=False)

            z_l = sw_res["optimal_z_th_long"] + 0.10
            z_s = sw_res["optimal_z_th_short"] + 0.10

            pos = generate_positions(Z_comp, z_th=z_l, z_th_short=z_s, mode="binary", long_only=False)
            net_ret, pnl, trades = simulate_etf_spot(full_trade_ret, pos, fee_bps=FEE_BPS)

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
            turnover = np.sum(np.abs(np.diff(pos[oos_mask.values], prepend=0.0))) / (len(oos_net) / 252.0)

            records.append({
                "ETF": etf,
                "Config": label,
                "Cost Sharpe": sharpe,
                "Raw Sharpe": raw_sr,
                "Total PnL": total_pnl,
                "Max DD": max_dd,
                "Win Rate": win_rate,
                "Turnover": turnover,
            })

    df = pd.DataFrame(records)

    print("\n================================================================================")
    print("750d VS 30d METRIC WINDOW & CADENCE EXPERIMENT RESULTS SUMMARY")
    print("================================================================================")
    print(df.to_string(index=False))

    avg_df = df.groupby("Config")[["Cost Sharpe", "Total PnL", "Turnover", "Win Rate"]].mean().reset_index()
    avg_df = avg_df.sort_values("Cost Sharpe", ascending=False)

    print("\n--------------------------------------------------------------------------------")
    print("CROSS-ETF AVERAGE PERFORMANCE RANKING")
    print("--------------------------------------------------------------------------------")
    print(avg_df.to_string(index=False))

    out_csv = NEWTRADE_DIR / "tests" / "test_750d_vs_30d_decay_results.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved experiment results to {out_csv}")


if __name__ == "__main__":
    run_experiment()
