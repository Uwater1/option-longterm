#!/usr/bin/env python3
"""
Research module for evaluating intraday stop-loss methods in NewTrade.

Methods evaluated:
  1. baseline: No stop loss (hold 10:00 -> 14:35)
  2. fixed_pct: Exit if loss >= alpha% from 10:00 open
  3. early_high_low: Stop set relative to 09:30-10:00 session High (Long) / Low (Short)
  4. trailing_pct: Dynamic trailing stop from peak high (Long) / trough low (Short) post 10:00
  5. vol_atr: Volatility-scaled stop distance based on early realized vol
  6. time_decay_trailing: Trailing stop that tightens as market close approaches

Data leakage prevention:
  - All parameter sweeps & optimal selection occur strictly on Train period (2010 to 2021-12-31).
  - OOS period (2022-01-01 to 2026-07-20) evaluated strictly single-pass with Train-locked params.
"""

import os
import sys
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

sys.path.append(str(HERE))
sys.path.append(str(REPO_ROOT / "day-model-new"))
sys.path.append(str(REPO_ROOT / "day-model"))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import get_weighting_scheme
from strategy import generate_positions, sweep_optimal_threshold, compute_production_threshold, calculate_metrics
from robustness import deflated_sharpe_ratio

from functools import lru_cache

# ETF Ticker -> 1m Parquet mapping
ETF_1M_MAP = {
    "300ETF": "data/510300_1m.parquet",
    "500ETF": "data/500ETF_1m.parquet",
    "50ETF": "data/50ETF_1m.parquet",
    "588000ETF": "data/588000ETF_1m.parquet",
    "159915ETF": "data/159915ETF_1m.parquet",
}


@lru_cache(maxsize=16)
def load_intraday_bars_dict(etf: str) -> dict:
    """
    Pre-process 1m intraday parquet file into day-keyed numpy matrices for ultra-fast simulation.
    Cached in memory to prevent repeated disk reads & string parsing.
    """
    rel_path = ETF_1M_MAP.get(etf)
    if not rel_path:
        return {}
    
    file_path = REPO_ROOT / rel_path
    if not file_path.exists():
        print(f"[WARNING] 1m file not found: {file_path}")
        return {}

    df_1m = pd.read_parquet(file_path)
    df_1m["datetime"] = pd.to_datetime(df_1m["datetime"])
    df_1m = df_1m.sort_values("datetime").reset_index(drop=True)
    
    dt_col = df_1m["datetime"].dt
    df_1m["date_str"] = dt_col.date.astype(str)
    df_1m["time_min"] = dt_col.hour * 60 + dt_col.minute
    
    bars_per_day = {}
    grouped = df_1m.groupby("date_str")
    
    for d_str, g in grouped:
        times_min = g["time_min"].values
        opens = g["open"].values.astype(np.float64)
        highs = g["high"].values.astype(np.float64)
        lows = g["low"].values.astype(np.float64)
        closes = g["close"].values.astype(np.float64)
        
        # Locate indices (600 = 10:00, 875 = 14:35)
        idx_1000 = -1
        idx_1435 = -1
        
        for i, t in enumerate(times_min):
            if t == 600:
                idx_1000 = i
            elif t <= 875:
                idx_1435 = i
                
        if idx_1000 < 0 or idx_1435 <= idx_1000:
            continue
            
        # Early session parameters (09:30 to 10:00)
        early_highs = highs[:idx_1000+1]
        early_lows = lows[:idx_1000+1]
        early_closes = closes[:idx_1000+1]
        
        h_early = float(np.max(early_highs)) if len(early_highs) > 0 else float(opens[0])
        l_early = float(np.min(early_lows)) if len(early_lows) > 0 else float(opens[0])
        
        # Realized vol in early session
        if len(early_closes) > 3:
            log_rets = np.diff(np.log(early_closes))
            vol_early = float(np.std(log_rets))
        else:
            vol_early = 0.005 # fallback ~0.5%
            
        bars_per_day[d_str] = {
            "opens": opens,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "idx_1000": idx_1000,
            "idx_1435": idx_1435,
            "h_early": h_early,
            "l_early": l_early,
            "vol_early": max(1e-4, vol_early),
        }
        
    return bars_per_day


def simulate_stoploss_day(day_data: dict, pos: float, method: str, param: float, 
                          fee_bps: float = 0.0008, slip_bps: float = 0.0002) -> tuple[float, float, bool, float]:
    """
    Simulate intraday stoploss for a single day and position.
    
    Returns:
      - net_return: Cost & slippage-adjusted daily return
      - raw_return: Gross daily return before fees & friction
      - stop_hit: True if stop loss was triggered, False if held to 14:35
      - fee_cost: Total fees + friction incurred
    """
    if abs(pos) < 1e-5:
        return 0.0, 0.0, False, 0.0
        
    if not day_data:
        # If 1m data missing, return 0.0 defensively
        return 0.0, 0.0, False, 0.0
        
    opens = day_data["opens"]
    highs = day_data["highs"]
    lows = day_data["lows"]
    closes = day_data["closes"]
    i_1000 = day_data["idx_1000"]
    i_1435 = day_data["idx_1435"]
    
    P_open = opens[i_1000]
    if P_open <= 0:
        return 0.0, 0.0, False, 0.0

    # Intraday round-trip fee (entry + exit transition)
    abs_pos = abs(pos)
    base_fee = fee_bps * 2.0
    
    if method == "baseline":
        P_close = closes[i_1435]
        raw_ret = pos * (P_close - P_open) / P_open
        total_fee = abs_pos * base_fee
        net_ret = raw_ret - total_fee
        return net_ret, raw_ret, False, total_fee
        
    # Intraday tracking from 10:00 to 14:35
    n_bars = i_1435 - i_1000 + 1
    
    if pos > 0:  # LONG
        running_peak = highs[i_1000]
        
        # Pre-compute fixed stop level if applicable
        if method == "fixed_pct":
            L_stop = P_open * (1.0 - param)
        elif method == "early_high_low":
            L_stop = max(day_data["h_early"] * (1.0 - param), P_open * (1.0 - param))
        elif method == "vol_atr":
            # param is k multiplier for early realized vol
            L_stop = P_open * (1.0 - param * day_data["vol_early"])
        else:
            L_stop = -1.0
            
        for i in range(i_1000, i_1435 + 1):
            bar_o = opens[i]
            bar_h = highs[i]
            bar_l = lows[i]
            
            if bar_h > running_peak:
                running_peak = bar_h
                
            # Compute dynamic stop level for trailing methods
            if method == "trailing_pct":
                L_stop_curr = running_peak * (1.0 - param)
            elif method == "time_decay_trailing":
                frac_time = (i - i_1000) / float(n_bars)
                param_curr = param * (1.0 - 0.3 * frac_time)  # tightens up to 30% by end of day
                L_stop_curr = running_peak * (1.0 - param_curr)
            else:
                L_stop_curr = L_stop
                
            # Check stop condition
            if bar_l <= L_stop_curr:
                # Stop triggered! Exit price is min of bar_open and L_stop_curr
                P_stop = min(bar_o, L_stop_curr)
                # Raw return at stop price with position scaling
                raw_ret = pos * (P_stop - P_open) / P_open
                total_fee = abs_pos * (base_fee + slip_bps)
                net_ret = raw_ret - total_fee
                return net_ret, raw_ret, True, total_fee
                
        # If no stop triggered, exit at 14:35 close
        P_close = closes[i_1435]
        raw_ret = pos * (P_close - P_open) / P_open
        total_fee = abs_pos * base_fee
        net_ret = raw_ret - total_fee
        return net_ret, raw_ret, False, total_fee

    else:  # SHORT (pos < 0)
        running_trough = lows[i_1000]
        
        if method == "fixed_pct":
            H_stop = P_open * (1.0 + param)
        elif method == "early_high_low":
            H_stop = min(day_data["l_early"] * (1.0 + param), P_open * (1.0 + param))
        elif method == "vol_atr":
            H_stop = P_open * (1.0 + param * day_data["vol_early"])
        else:
            H_stop = 999999.0
            
        for i in range(i_1000, i_1435 + 1):
            bar_o = opens[i]
            bar_h = highs[i]
            bar_l = lows[i]
            
            if bar_l < running_trough:
                running_trough = bar_l
                
            if method == "trailing_pct":
                H_stop_curr = running_trough * (1.0 + param)
            elif method == "time_decay_trailing":
                frac_time = (i - i_1000) / float(n_bars)
                param_curr = param * (1.0 - 0.3 * frac_time)
                H_stop_curr = running_trough * (1.0 + param_curr)
            else:
                H_stop_curr = H_stop
                
            if bar_h >= H_stop_curr:
                P_stop = max(bar_o, H_stop_curr)
                # Short return: pos * (P_stop - P_open) / P_open, where pos < 0
                raw_ret = pos * (P_stop - P_open) / P_open
                total_fee = abs_pos * (base_fee + slip_bps)
                net_ret = raw_ret - total_fee
                return net_ret, raw_ret, True, total_fee
                
        P_close = closes[i_1435]
        raw_ret = pos * (P_close - P_open) / P_open
        total_fee = abs_pos * base_fee
        net_ret = raw_ret - total_fee
        return net_ret, raw_ret, False, total_fee


def simulate_full_series(df_dates: pd.Series, positions: np.ndarray, bars_dict: dict, 
                         method: str, param: float, fee_bps: float = 0.0008, slip_bps: float = 0.0002) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Simulate intraday stoploss across an entire series of trading dates.
    
    Returns:
      - net_returns: np.ndarray shape (T,)
      - raw_returns: np.ndarray shape (T,)
      - fees: np.ndarray shape (T,)
      - stop_hits: np.ndarray shape (T,) boolean mask
      - trigger_rate_pct: Percentage of active trading days where stop was hit
    """
    T = len(positions)
    net_returns = np.zeros(T, dtype=np.float64)
    raw_returns = np.zeros(T, dtype=np.float64)
    fees = np.zeros(T, dtype=np.float64)
    stop_hits = np.zeros(T, dtype=bool)
    
    n_active = 0
    n_stops = 0
    
    date_strs = pd.to_datetime(df_dates).dt.strftime("%Y-%m-%d").values
    
    for t in range(T):
        pos = positions[t]
        if abs(pos) < 1e-5:
            continue
            
        n_active += 1
        d_str = date_strs[t]
        day_data = bars_dict.get(d_str, None)
        
        net_ret, raw_ret, is_hit, fee_cost = simulate_stoploss_day(day_data, pos, method, param, fee_bps=fee_bps, slip_bps=slip_bps)
        net_returns[t] = net_ret
        raw_returns[t] = raw_ret
        fees[t] = fee_cost
        stop_hits[t] = is_hit
        if is_hit:
            n_stops += 1
            
    trig_pct = (n_stops / n_active * 100.0) if n_active > 0 else 0.0
    return net_returns, raw_returns, fees, stop_hits, round(trig_pct, 1)


# Expanded grid search parameters (from tight 0.3% up to wide protective 5.0%)
PARAM_GRIDS = {
    "fixed_pct": [0.003, 0.005, 0.008, 0.010, 0.012, 0.015, 0.018, 0.020, 0.025, 0.030, 0.035, 0.040, 0.050],
    "early_high_low": [0.003, 0.005, 0.008, 0.010, 0.015, 0.020, 0.025, 0.030, 0.040],
    "trailing_pct": [0.003, 0.005, 0.008, 0.010, 0.012, 0.015, 0.018, 0.020, 0.025, 0.030, 0.035, 0.040],
    "vol_atr": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0],
    "time_decay_trailing": [0.005, 0.008, 0.010, 0.012, 0.015, 0.018, 0.020, 0.025, 0.030],
}


def sweep_train_optimal_stoploss(df_train: pd.DataFrame, positions_train: np.ndarray, bars_dict: dict,
                                method: str, fee_bps: float = 0.0008, target_mode: str = "max_sharpe") -> tuple[float, dict]:
    """
    Sweep parameters for a given stoploss method strictly on Train data (df_train).
    
    Modes:
      - max_sharpe: Parameter maximizing cost-adjusted Sharpe ratio.
      - tail_risk_protective: Parameter preserving >= 90% of Baseline Train Sharpe with minimal trigger rate.
    """
    if method == "baseline":
        net_ret, raw_ret, _, _, _ = simulate_full_series(df_train["date"], positions_train, bars_dict, "baseline", 0.0, fee_bps=fee_bps)
        std_ret = np.std(net_ret)
        sharpe = float(np.mean(net_ret) / std_ret * np.sqrt(252)) if std_ret > 1e-12 else 0.0
        return 0.0, {"param": 0.0, "sharpe": sharpe, "trigger_rate": 0.0}

    grid = PARAM_GRIDS.get(method, [0.005])
    
    # Calculate baseline train sharpe for relative filtering
    net_ret_base, raw_ret_base, _, _, _ = simulate_full_series(df_train["date"], positions_train, bars_dict, "baseline", 0.0, fee_bps=fee_bps)
    std_base = np.std(net_ret_base)
    base_train_sharpe = float(np.mean(net_ret_base) / std_base * np.sqrt(252)) if std_base > 1e-12 else 0.0
    
    best_sharpe = -np.inf
    best_param = grid[-1]  # default to widest parameter (least intrusive)
    best_info = {}
    
    sweep_details = []
    
    for param in grid:
        net_ret, raw_ret, _, _, trig_pct = simulate_full_series(df_train["date"], positions_train, bars_dict, method, param, fee_bps=fee_bps)
        std_ret = np.std(net_ret)
        sharpe = float(np.mean(net_ret) / std_ret * np.sqrt(252)) if std_ret > 1e-12 else 0.0
        tot_pnl = float(np.sum(net_ret))
        
        info = {
            "param": param,
            "sharpe": round(sharpe, 4),
            "trigger_rate": trig_pct,
            "total_pnl": round(tot_pnl, 4),
        }
        sweep_details.append(info)
        
        if target_mode == "max_sharpe":
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_param = param
                best_info = info
        elif target_mode == "tail_risk_protective":
            # Pick parameter that triggers <= 10% of days and keeps >= 85% of baseline Sharpe
            if trig_pct <= 10.0 and sharpe >= 0.85 * base_train_sharpe:
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_param = param
                    best_info = info

    if not best_info:
        # Fallback to widest parameter in grid
        best_param = grid[-1]
        best_info = sweep_details[-1]
        
    return best_param, best_info


def run_etf_stoploss_experiment(etf: str, scheme: str = "icw", fee_bps: float = 0.0008,
                                start_date: str = "2022-01-01", end_date: str = "2026-07-20") -> dict:
    """
    Run complete Train-sweep + locked OOS stoploss evaluation for one ETF and scheme.
    """
    print(f"\n=======================================================")
    print(f"  Researching Intraday Stop-Loss for {etf} ({scheme.upper()})")
    print(f"=======================================================")
    
    # 1. Load admitted pool & dataset
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        print(f"  [SKIP] {etf} has insufficient features.")
        return {}
        
    df = load_etf_dataset(etf)
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    
    # 2. Expanding Z-score and Composite signal
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

    # 3. Train-Optimal Threshold Sweep for Z_composite
    train_mask = (df["date"] < t_start_ts).values
    oos_mask = ((df["date"] >= t_start_ts) & (df["date"] <= pd.Timestamp(end_date))).values
    
    df_train = df[train_mask].reset_index(drop=True)
    df_oos = df[oos_mask].reset_index(drop=True)
    
    Z_train = Z_composite[train_mask]
    Z_oos = Z_composite[oos_mask]
    
    ret_train_raw = full_trade_ret[train_mask]
    ret_oos_raw = full_trade_ret[oos_mask]
    
    sweep_res = sweep_optimal_threshold(Z_train, ret_train_raw, mode="binary", fee_bps=fee_bps)
    z_th_long, z_th_short = compute_production_threshold(sweep_res, z_buffer=0.1)
    
    pos_train = generate_positions(Z_train, z_th=z_th_long, z_th_short=z_th_short, mode="binary", long_only=False)
    pos_oos = generate_positions(Z_oos, z_th=z_th_long, z_th_short=z_th_short, mode="binary", long_only=False)

    # 4. Load 1m Intraday Bars
    print(f"  Loading 1m intraday price bars for {etf}...")
    bars_dict = load_intraday_bars_dict(etf)
    if not bars_dict:
        print(f"  [ERROR] Failed to load 1m bars for {etf}.")
        return {}
        
    print(f"  1m bars loaded for {len(bars_dict)} trading days.")
    
    # 5. Baseline (No Stoploss) Evaluation
    net_ret_base_train, raw_ret_base_train, _, _, _ = simulate_full_series(df_train["date"], pos_train, bars_dict, "baseline", 0.0, fee_bps=fee_bps)
    net_ret_base_oos, raw_ret_base_oos, _, _, _ = simulate_full_series(df_oos["date"], pos_oos, bars_dict, "baseline", 0.0, fee_bps=fee_bps)
    
    base_metrics_train = calculate_metrics(net_ret_base_train, raw_ret_base_train, pos_train, df_train["date"])
    base_metrics_oos = calculate_metrics(net_ret_base_oos, raw_ret_base_oos, pos_oos, df_oos["date"])
    
    print(f"\n  Baseline OOS Performance: Sharpe={base_metrics_oos['cost_sharpe']:.3f}, PnL={base_metrics_oos['total_pnl']:.4f}, MaxDD={base_metrics_oos['max_drawdown']:.4f}")
    
    # 6. Evaluate all stoploss methods
    methods_to_test = ["fixed_pct", "early_high_low", "trailing_pct", "vol_atr", "time_decay_trailing"]
    results_summary = []
    
    # Add baseline first
    results_summary.append({
        "method": "baseline",
        "train_param": 0.0,
        "train_sharpe": base_metrics_train["cost_sharpe"],
        "train_pnl": base_metrics_train["total_pnl"],
        "oos_sharpe": base_metrics_oos["cost_sharpe"],
        "oos_pnl": base_metrics_oos["total_pnl"],
        "oos_max_dd": base_metrics_oos["max_drawdown"],
        "oos_win_rate": base_metrics_oos["win_rate_pct"],
        "oos_trigger_rate": 0.0,
        "sharpe_lift": 0.0,
        "dsr_pvalue": 1.0,
    })
    
    # Pre-calculate baseline track for DSR
    for m_name in methods_to_test:
        best_param, train_info = sweep_train_optimal_stoploss(df_train, pos_train, bars_dict, m_name, fee_bps=fee_bps)
        
        # Single-pass locked evaluation on OOS
        net_ret_oos, raw_ret_oos, fees_oos, stop_hits_oos, trig_rate_oos = simulate_full_series(
            df_oos["date"], pos_oos, bars_dict, m_name, best_param, fee_bps=fee_bps
        )
        
        m_oos = calculate_metrics(net_ret_oos, raw_ret_oos, pos_oos, df_oos["date"])
        
        # Compute Deflated Sharpe Ratio (DSR) p-value against baseline
        dsr_res = deflated_sharpe_ratio(observed_sr=m_oos["cost_sharpe"], n_trials=len(PARAM_GRIDS[m_name]), n_obs=len(net_ret_oos))
        
        sharpe_lift = m_oos["cost_sharpe"] - base_metrics_oos["cost_sharpe"]
        
        results_summary.append({
            "method": m_name,
            "train_param": best_param,
            "train_sharpe": train_info.get("sharpe", 0.0),
            "train_pnl": train_info.get("total_pnl", 0.0),
            "oos_sharpe": m_oos["cost_sharpe"],
            "oos_pnl": m_oos["total_pnl"],
            "oos_max_dd": m_oos["max_drawdown"],
            "oos_win_rate": m_oos["win_rate_pct"],
            "oos_trigger_rate": trig_rate_oos,
            "sharpe_lift": round(sharpe_lift, 3),
            "dsr_pvalue": dsr_res.get("dsr_pvalue", 1.0),
        })
        
        print(f"  Method {m_name:20s} | TrainParam={best_param:<6} | OOS Sharpe={m_oos['cost_sharpe']:<6.3f} (Lift: {sharpe_lift:+.3f}) | OOS PnL={m_oos['total_pnl']:<7.4f} | MaxDD={m_oos['max_drawdown']:<6.4f} | StopTrig={trig_rate_oos}%")
        
    return {
        "etf": etf,
        "scheme": scheme,
        "base_metrics_oos": base_metrics_oos,
        "summary": results_summary,
    }


def generate_research_markdown_report(all_results: list, output_file: str = "newtrade/STOPLOSS_RESEARCH_REPORT.md"):
    """
    Generate clean, comprehensive Markdown report detailing Train-sweep and OOS-locked stoploss performance.
    """
    lines = []
    lines.append("# Intraday Stop-Loss Research Report (NewTrade Framework)\n")
    lines.append("## Executive Summary\n")
    lines.append("This report investigates whether intraday stop-loss methods (Fixed, Today High/Low Anchor, Trailing Peak/Trough, Volatility ATR, Time-Decay Trailing) improve factor monetization returns.")
    lines.append("\n**Strict Out-of-Sample Integrity Guardrail**:")
    lines.append("- **Train Period (2010 – 2021-12-31)**: All stop-loss threshold parameters were swept and optimized exclusively on training data.")
    lines.append("- **OOS Period (2022-01-01 – 2026-07-20)**: Evaluated **strictly once (single-pass)** using Train-locked parameters.")
    lines.append("- **Friction**: Standard 8 bps position state transition + 2 bps execution slippage on stop-loss triggers.\n")

    lines.append("## Overall Benchmark Matrix (OOS 2022–2026)\n")
    lines.append("| ETF | Scheme | Method | Train Param | OOS Sharpe | Baseline Sharpe | Sharpe Lift | OOS PnL | Baseline PnL | OOS MaxDD | Stop Trigger Rate (%) | DSR p-value |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    
    total_lifts = []
    
    for res in all_results:
        etf = res.get("etf", "")
        scheme = res.get("scheme", "")
        base_sharpe = res.get("base_metrics_oos", {}).get("cost_sharpe", 0.0)
        base_pnl = res.get("base_metrics_oos", {}).get("total_pnl", 0.0)
        
        for item in res.get("summary", []):
            m_name = item["method"]
            t_param = item["train_param"]
            oos_s = item["oos_sharpe"]
            lift = item["sharpe_lift"]
            oos_pnl = item["oos_pnl"]
            max_dd = item["oos_max_dd"]
            trig_rate = item["oos_trigger_rate"]
            dsr_p = item["dsr_pvalue"]
            
            if m_name != "baseline":
                total_lifts.append(lift)
                
            lines.append(f"| {etf} | {scheme.upper()} | `{m_name}` | {t_param} | {oos_s:.3f} | {base_sharpe:.3f} | **{lift:+.3f}** | {oos_pnl:.4f} | {base_pnl:.4f} | {max_dd:.4f} | {trig_rate}% | {dsr_p:.4f} |")

    lines.append("\n## Per-ETF Findings & Analysis\n")
    
    for res in all_results:
        etf = res.get("etf", "")
        scheme = res.get("scheme", "")
        lines.append(f"### {etf} ({scheme.upper()})\n")
        lines.append("| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for item in res.get("summary", []):
            lines.append(f"| `{item['method']}` | {item['train_param']} | {item['train_sharpe']:.3f} | {item['oos_sharpe']:.3f} | {item['oos_pnl']:.4f} | {item['oos_max_dd']:.4f} | {item['oos_win_rate']:.1f}% | {item['oos_trigger_rate']}% |")
        lines.append("\n")

    lines.append("## Core Research Conclusions & Production Recommendation\n")
    avg_lift = np.mean(total_lifts) if total_lifts else 0.0
    positive_lifts = sum(1 for x in total_lifts if x > 0)
    total_tests = len(total_lifts)
    
    lines.append(f"- **Average Sharpe Lift across all methods/ETFs**: `{avg_lift:+.3f}`")
    lines.append(f"- **Positive Sharpe Lift Ratio**: `{positive_lifts}/{total_tests}` (`{positive_lifts/max(1,total_tests)*100:.1f}%`)")
    
    if avg_lift < 0:
        lines.append("\n> [!CAUTION]")
        lines.append("> **CONCLUSION: Stop-loss degrades overall performance in NewTrade intraday monetization.**")
        lines.append("> Intraday factor monetization trades operate on noisy 10:00-14:35 mean-reverting and trending micro-structure. Setting intraday stop-losses repeatedly cuts trades near local intraday extremes before full-day signal convergence, incurring fee friction and whipsaw losses.")
        lines.append("> **RECOMMENDATION**: Keep baseline mode (hold position until 14:35) without intraday stop-loss.")
    else:
        lines.append("\n> [!TIP]")
        lines.append("> **CONCLUSION: Selective stop-loss methods demonstrate positive lift.**")
        lines.append("> **RECOMMENDATION**: Adopt the top-performing stop-loss method into production.")
        
    report_text = "\n".join(lines)
    out_path = REPO_ROOT / output_file
    with open(out_path, "w") as f:
        f.write(report_text)
        
    print(f"\n[REPORT SAVED] Saved report to {out_path}")
    return report_text


def main():
    parser = argparse.ArgumentParser(description="NewTrade Intraday Stop-Loss Research CLI")
    parser.add_argument("-e", "--etf", type=str, default="300ETF", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or all)")
    parser.add_argument("--scheme", type=str, default="icw", help="Weighting scheme (icw, ew, or all)")
    parser.add_argument("--fee-bps", type=float, default=0.0008, help="State transition fee bps (default 8 bps = 0.0008)")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS start date")
    parser.add_argument("--end-date", type=str, default="2026-07-20", help="OOS end date")
    parser.add_argument("--report", action="store_true", help="Generate Markdown research report")
    
    args = parser.parse_args()
    
    etfs = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"] if args.etf == "all" else [args.etf]
    schemes = ["icw", "ew"] if args.scheme == "all" else [args.scheme]
    
    all_results = []
    
    for e in etfs:
        for s in schemes:
            res = run_etf_stoploss_experiment(e, scheme=s, fee_bps=args.fee_bps, start_date=args.start_date, end_date=args.end_date)
            if res:
                all_results.append(res)
                
    if args.report or len(all_results) > 1:
        generate_research_markdown_report(all_results)


if __name__ == "__main__":
    main()
