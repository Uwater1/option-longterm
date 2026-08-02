#!/usr/bin/env python3
"""
Research module for evaluating option intraday stop-loss methods in NewTrade.

Methods evaluated:
  1. baseline: No option stop loss (hold entry to 14:35 close)
  2. opt_trailing_pct: Trailing stop from peak option premium (P_peak)
  3. opt_profit_lock_trailing: Hard stop initially, tight trailing stop activated once gain >= 20%
  4. opt_time_decay_trailing: Premium trailing stop that tightens over time as 14:35 approaches
  5. spot_trailing_pct: Trailing stop triggered on underlying ETF spot price (S_peak / S_trough)
  6. spot_time_decay_trailing: Time-decay trailing stop on underlying ETF spot price

Data leakage prevention:
  - All parameter sweeps & optimal selection occur strictly on Train period (2010 to 2021-12-31).
  - OOS period (2022-01-01 to 2026-07-20) evaluated strictly single-pass with Train-locked params.
"""

import sys
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

sys.path.append(str(HERE))
sys.path.append(str(REPO_ROOT / "day-model-new"))
sys.path.append(str(REPO_ROOT / "day-model"))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import get_weighting_scheme
from strategy import generate_positions, sweep_optimal_threshold, compute_production_threshold, calculate_metrics
from option_strategy import simulate_option_portfolio
from robustness import deflated_sharpe_ratio

# Parameter grids for Train optimization (robust bounds preventing noise over-triggering)
PARAM_GRIDS = {
    "opt_trailing_pct": [0.20, 0.25, 0.30, 0.35, 0.40],
    "opt_profit_lock_trailing": [0.15, 0.20, 0.25, 0.30],
    "opt_time_decay_trailing": [0.25, 0.30, 0.35, 0.40],
    "spot_trailing_pct": [0.008, 0.010, 0.012, 0.015],
    "spot_time_decay_trailing": [0.008, 0.010, 0.012, 0.015],
}


def sweep_train_optimal_option_stoploss(
    etf: str,
    pos_train: np.ndarray,
    dates_train: pd.Series,
    iv_train: np.ndarray,
    method: str,
) -> tuple[float, dict]:
    """
    Sweep parameters for a given option stoploss method strictly on Train data (dates_train).
    Returns (best_param, best_info_dict).
    """
    if method == "baseline":
        res = simulate_option_portfolio(
            etf, pos_train, dates_train, iv_series=iv_train, use_stoploss=False
        )
        rets = res["daily_returns"]
        std_ret = np.std(rets)
        sharpe = float(np.mean(rets) / std_ret * np.sqrt(252)) if std_ret > 1e-12 else 0.0
        return 0.0, {"param": 0.0, "sharpe": round(sharpe, 4), "net_pnl": res["final_capital"] - res["initial_capital"]}

    grid = PARAM_GRIDS.get(method, [0.25])
    best_sharpe = -np.inf
    best_param = grid[-1]
    best_info = {}

    for param in grid:
        res = simulate_option_portfolio(
            etf, pos_train, dates_train, iv_series=iv_train,
            use_stoploss=True, stoploss_mode=method, stoploss_param=param
        )
        rets = res["daily_returns"]
        std_ret = np.std(rets)
        sharpe = float(np.mean(rets) / std_ret * np.sqrt(252)) if std_ret > 1e-12 else 0.0
        net_pnl = float(res["final_capital"] - res["initial_capital"])

        info = {
            "param": param,
            "sharpe": round(sharpe, 4),
            "net_pnl": round(net_pnl, 2),
            "n_trades": res["n_trades"],
            "stop_hits": res["n_stop_hits"],
        }

        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_param = param
            best_info = info

    return best_param, best_info


def run_option_stoploss_experiment(
    etf: str,
    scheme: str = "icw",
    start_date: str = "2022-01-01",
    end_date: str = "2026-07-20",
) -> dict:
    """
    Run complete Train-sweep + locked OOS option stoploss evaluation for one ETF.
    """
    print(f"\n=======================================================")
    print(f"  Option Stop-Loss Research for {etf} ({scheme.upper()})")
    print(f"=======================================================")

    # 1. Load pool & dataset
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        print(f"  [SKIP] {etf} has insufficient features.")
        return {}

    df = load_etf_dataset(etf)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)

    # 2. Factor composite signal
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    t_start_ts = pd.Timestamp(start_date)
    n_train = int((df["date"] < t_start_ts).sum())
    if n_train < 252:
        n_train = 1700

    scheme_func = get_weighting_scheme(scheme)
    full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values

    if scheme == "icw":
        IC_mat = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)
        Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train, expanding_ic=IC_mat)
    else:
        Z_composite = scheme_func(Z_std, signs, pool=pool, n_train=n_train)

    # 3. Train/OOS split & Threshold sweep
    train_mask = (df["date"] < t_start_ts).values
    oos_mask = ((df["date"] >= t_start_ts) & (df["date"] <= pd.Timestamp(end_date))).values

    df_train = df[train_mask].reset_index(drop=True)
    df_oos = df[oos_mask].reset_index(drop=True)

    Z_train = Z_composite[train_mask]
    Z_oos = Z_composite[oos_mask]

    ret_train_raw = full_trade_ret[train_mask]
    sweep_res = sweep_optimal_threshold(Z_train, ret_train_raw, mode="binary", fee_bps=0.0008)
    z_th_long, z_th_short = compute_production_threshold(sweep_res, z_buffer=0.1)

    pos_train = generate_positions(Z_train, z_th=z_th_long, z_th_short=z_th_short, mode="binary", long_only=False)
    pos_oos = generate_positions(Z_oos, z_th=z_th_long, z_th_short=z_th_short, mode="binary", long_only=False)

    iv_train = df_train["iv"].values if "iv" in df_train.columns else None
    iv_oos = df_oos["iv"].values if "iv" in df_oos.columns else None

    # 4. Baseline Option Evaluation (No stoploss)
    res_base_train = simulate_option_portfolio(etf, pos_train, df_train["date"], iv_series=iv_train, use_stoploss=False)
    res_base_oos = simulate_option_portfolio(etf, pos_oos, df_oos["date"], iv_series=iv_oos, use_stoploss=False)

    base_rets_oos = res_base_oos["daily_returns"]
    std_base_oos = np.std(base_rets_oos)
    base_sharpe_oos = float(np.mean(base_rets_oos) / std_base_oos * np.sqrt(252)) if std_base_oos > 1e-12 else 0.0
    base_pnl_oos = float(res_base_oos["final_capital"] - res_base_oos["initial_capital"])
    
    # Calculate win rate and max DD
    base_trade_df = res_base_oos["trade_log_df"]
    base_win_rate = float((base_trade_df["net_pnl"] > 0).mean() * 100.0) if not base_trade_df.empty else 0.0
    
    cum_cap = np.maximum.accumulate(np.cumsum(res_base_oos["daily_pnl"]) + res_base_oos["initial_capital"])
    dd = (cum_cap - (np.cumsum(res_base_oos["daily_pnl"]) + res_base_oos["initial_capital"])) / cum_cap
    base_max_dd = float(np.max(dd)) * 100.0 if len(dd) > 0 else 0.0

    print(f"\n  Baseline OOS Performance: Sharpe={base_sharpe_oos:.3f}, Net PnL={base_pnl_oos:+,.0f} RMB, WinRate={base_win_rate:.1f}%, MaxDD={base_max_dd:.2f}%")

    methods_to_test = [
        "opt_trailing_pct",
        "opt_profit_lock_trailing",
        "opt_time_decay_trailing",
        "spot_trailing_pct",
        "spot_time_decay_trailing",
    ]

    results_summary = []
    results_summary.append({
        "method": "baseline",
        "train_param": 0.0,
        "train_sharpe": round(float(np.mean(res_base_train["daily_returns"]) / np.std(res_base_train["daily_returns"]) * np.sqrt(252)), 3) if np.std(res_base_train["daily_returns"]) > 1e-12 else 0.0,
        "oos_sharpe": round(base_sharpe_oos, 3),
        "oos_pnl_rmb": round(base_pnl_oos, 2),
        "oos_max_dd_pct": round(base_max_dd, 2),
        "oos_win_rate_pct": round(base_win_rate, 1),
        "oos_stop_hits": 0,
        "oos_stop_trig_pct": 0.0,
        "sharpe_lift": 0.0,
        "dsr_pvalue": 1.0,
    })

    for m_name in methods_to_test:
        best_param, train_info = sweep_train_optimal_option_stoploss(etf, pos_train, df_train["date"], iv_train, m_name)

        # Single-pass locked OOS simulation
        res_oos = simulate_option_portfolio(
            etf, pos_oos, df_oos["date"], iv_series=iv_oos,
            use_stoploss=True, stoploss_mode=m_name, stoploss_param=best_param
        )

        rets_oos = res_oos["daily_returns"]
        std_oos = np.std(rets_oos)
        sharpe_oos = float(np.mean(rets_oos) / std_oos * np.sqrt(252)) if std_oos > 1e-12 else 0.0
        pnl_oos = float(res_oos["final_capital"] - res_oos["initial_capital"])

        trade_df = res_oos["trade_log_df"]
        win_rate = float((trade_df["net_pnl"] > 0).mean() * 100.0) if not trade_df.empty else 0.0

        cum_cap_m = np.maximum.accumulate(np.cumsum(res_oos["daily_pnl"]) + res_oos["initial_capital"])
        dd_m = (cum_cap_m - (np.cumsum(res_oos["daily_pnl"]) + res_oos["initial_capital"])) / cum_cap_m
        max_dd = float(np.max(dd_m)) * 100.0 if len(dd_m) > 0 else 0.0

        n_trades = res_oos["n_trades"]
        n_stops = res_oos["n_stop_hits"]
        trig_pct = float(n_stops / n_trades * 100.0) if n_trades > 0 else 0.0

        dsr_res = deflated_sharpe_ratio(observed_sr=sharpe_oos, n_trials=len(PARAM_GRIDS.get(m_name, [1])), n_obs=len(rets_oos))
        sharpe_lift = sharpe_oos - base_sharpe_oos

        results_summary.append({
            "method": m_name,
            "train_param": best_param,
            "train_sharpe": train_info.get("sharpe", 0.0),
            "oos_sharpe": round(sharpe_oos, 3),
            "oos_pnl_rmb": round(pnl_oos, 2),
            "oos_max_dd_pct": round(max_dd, 2),
            "oos_win_rate_pct": round(win_rate, 1),
            "oos_stop_hits": n_stops,
            "oos_stop_trig_pct": round(trig_pct, 1),
            "sharpe_lift": round(sharpe_lift, 3),
            "dsr_pvalue": dsr_res.get("dsr_pvalue", 1.0),
        })

        print(f"  Method {m_name:24s} | TrainParam={best_param:<6} | OOS Sharpe={sharpe_oos:<6.3f} (Lift: {sharpe_lift:+.3f}) | OOS PnL={pnl_oos:+,.0f} RMB | MaxDD={max_dd:<5.2f}% | StopHits={n_stops}/{n_trades} ({trig_pct:.1f}%)")

    return {
        "etf": etf,
        "scheme": scheme,
        "summary": results_summary,
    }


def main():
    parser = argparse.ArgumentParser(description="Option Stop-Loss Research Engine")
    parser.add_argument("-e", "--etf", type=str, default="300ETF", help="ETF ticker (300ETF, 500ETF, 50ETF, all)")
    parser.add_argument("--scheme", type=str, default="icw", help="Weighting scheme (default: icw)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS start date")
    parser.add_argument("--end-date", type=str, default="2026-07-20", help="OOS end date")
    args = parser.parse_args()

    etfs = ["300ETF", "500ETF", "50ETF"] if args.etf.lower() == "all" else [args.etf]

    all_results = []
    for etf in etfs:
        res = run_option_stoploss_experiment(etf, scheme=args.scheme, start_date=args.start_date, end_date=args.end_date)
        if res:
            all_results.append(res)

    print("\n=======================================================")
    print("  RESEARCH COMPLETED SUMMARY")
    print("=======================================================")
    for res in all_results:
        etf = res["etf"]
        print(f"\n--- {etf} Summary ---")
        df_res = pd.DataFrame(res["summary"])
        print(df_res[["method", "train_param", "oos_sharpe", "sharpe_lift", "oos_pnl_rmb", "oos_max_dd_pct", "oos_stop_trig_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
