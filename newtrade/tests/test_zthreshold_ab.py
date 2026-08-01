#!/usr/bin/env python3
"""
A/B Test: Z-Threshold System Comparison

Tests 7 alternative threshold/trigger mechanisms for the daily trading gate.
The threshold determines WHETHER to trade on a given day (enter 10:00, exit 14:35).

Group A - Threshold logic changes (same Z_composite signal):
  1. BASELINE: argmax Sharpe sweep + fixed +0.10 buffer
  2. 90%-of-peak: most conservative z_th within 90% of peak Sharpe, x1.10 buffer
  3. Expanding percentile: trade when Z[t] in top/bottom P% of expanding history
  4. Rolling percentile 480d: trade when Z[t] in top/bottom P% of trailing 480d
  5. Walk-forward re-sweep: re-optimize threshold every 60d on trailing 480d, x1.10
  6. Variance-scaled: z_th[t] = k * rolling_std(Z, 252d)

Group B - Signal construction change:
  7. Feature hysteresis: enter top-10, exit only below rank-15 (cluster-aware)
     + baseline threshold. Stabilizes Z_composite distribution at the source.

Usage:
    python newtrade/tests/test_zthreshold_ab.py
    python newtrade/tests/test_zthreshold_ab.py --fee-bps 12
    python newtrade/tests/test_zthreshold_ab.py --start-date 2023-01-01
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
from weighting import compute_icw, _get_top_k_indices
from strategy import (
    sweep_optimal_threshold, compute_production_threshold,
    simulate_etf_spot, calculate_metrics, generate_positions,
)
from research_stoploss import load_intraday_bars_dict, simulate_full_series
from run_backtest import resolve_ic_ema_span

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
FEE_BPS_DEFAULT = 8.0
TAIL_WINDOW = 480
TAIL_PCT = 0.10
TOP_K = 10
EXIT_RANK = 15  # Hysteresis: exit only when rank > 15


# =============================================================================
# Threshold Arms (Group A) - operate on pre-computed Z_composite
# =============================================================================

def arm_baseline(Z_composite, trade_returns, train_mask, fee_bps, long_only=False):
    """Arm 1: Current production - argmax Sharpe + fixed +0.10 buffer."""
    Z_train = Z_composite[train_mask]
    ret_train = trade_returns[train_mask]
    sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary",
                                         fee_bps=fee_bps, long_only=long_only)
    z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=0.10)
    positions = generate_positions(Z_composite, z_th=z_th_l, z_th_short=z_th_s,
                                   mode="binary", long_only=long_only)
    info = {"z_th_long": z_th_l, "z_th_short": z_th_s,
            "train_z_l": sweep_info["optimal_z_th_long"],
            "train_z_s": sweep_info["optimal_z_th_short"]}
    return positions, info


def arm_90pct_peak(Z_composite, trade_returns, train_mask, fee_bps, long_only=False):
    """Arm 2: 90%-of-peak rule + proportional x1.10 buffer."""
    Z_train = Z_composite[train_mask]
    ret_train = trade_returns[train_mask]
    sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary",
                                         fee_bps=fee_bps, long_only=long_only)
    # Re-sweep to get full Sharpe landscape
    from strategy import generate_positions as gp
    z_range = (0.5, 1.5)
    z_step = 0.1
    thresholds = np.arange(z_range[0], z_range[1] + z_step * 0.5, z_step)

    sharpes_long = []
    for z_th in thresholds:
        pos = gp(Z_train, z_th=z_th, mode="binary", long_only=True)
        net, _, _ = simulate_etf_spot(ret_train, pos, fee_bps=fee_bps)
        std = np.std(net)
        sr = float((np.mean(net) / std) * np.sqrt(252)) if std > 1e-12 else 0.0
        n_active = int((np.abs(pos) > 1e-5).sum())
        active_pct = n_active / len(pos) * 100.0
        sharpes_long.append((z_th, sr, active_pct))

    # Find peak and 90% threshold (highest z_th with Sharpe >= 90% of peak)
    valid = [(z, s, a) for z, s, a in sharpes_long if a >= 8.0]
    if not valid:
        valid = sharpes_long
    peak_sharpe = max(s for _, s, _ in valid)
    threshold_90 = 0.9 * peak_sharpe
    # Pick highest z_th where Sharpe >= 90% of peak
    candidates = [(z, s) for z, s, _ in valid if s >= threshold_90]
    z_train_90 = max(z for z, _ in candidates) if candidates else sweep_info["optimal_z_th_long"]

    # Same for short
    sharpes_short = []
    for z_th in thresholds:
        pos_s = np.zeros(len(Z_train))
        pos_s[Z_train < -z_th] = -1.0
        net, _, _ = simulate_etf_spot(ret_train, pos_s, fee_bps=fee_bps)
        std = np.std(net)
        sr = float((np.mean(net) / std) * np.sqrt(252)) if std > 1e-12 else 0.0
        n_active = int((np.abs(pos_s) > 1e-5).sum())
        active_pct = n_active / len(pos_s) * 100.0
        sharpes_short.append((z_th, sr, active_pct))

    valid_s = [(z, s, a) for z, s, a in sharpes_short if a >= 8.0]
    if not valid_s:
        valid_s = sharpes_short
    peak_s = max(s for _, s, _ in valid_s)
    cand_s = [(z, s) for z, s, _ in valid_s if s >= 0.9 * peak_s]
    z_train_90_s = max(z for z, _ in cand_s) if cand_s else sweep_info["optimal_z_th_short"]

    # Proportional buffer x1.10
    z_th_l = round(z_train_90 * 1.10, 2)
    z_th_s = round(z_train_90_s * 1.10, 2)

    positions = generate_positions(Z_composite, z_th=z_th_l, z_th_short=z_th_s,
                                   mode="binary", long_only=long_only)
    info = {"z_th_long": z_th_l, "z_th_short": z_th_s,
            "train_z_90_l": z_train_90, "train_z_90_s": z_train_90_s,
            "peak_sharpe_l": peak_sharpe}
    return positions, info


def arm_expanding_percentile(Z_composite, trade_returns, train_mask, fee_bps, long_only=False):
    """Arm 3: Trade when Z[t] is in top/bottom P% of expanding history."""
    T = len(Z_composite)
    # Sweep percentile on training data
    best_pct = 15.0
    best_sharpe = -np.inf
    for pct in [10.0, 12.0, 15.0, 18.0, 20.0, 25.0]:
        positions_trial = np.zeros(T, dtype=np.float64)
        for t in range(1, T):
            history = Z_composite[:t]
            z = Z_composite[t]
            pct_rank = (history < z).sum() / len(history) * 100.0
            if pct_rank > (100.0 - pct):
                positions_trial[t] = 1.0
            elif pct_rank < pct:
                if not long_only:
                    positions_trial[t] = -1.0
        # Evaluate on training portion only
        pos_train = positions_trial[train_mask]
        ret_train = trade_returns[train_mask]
        net, _, _ = simulate_etf_spot(ret_train, pos_train, fee_bps=fee_bps)
        std = np.std(net)
        sr = float((np.mean(net) / std) * np.sqrt(252)) if std > 1e-12 else 0.0
        n_active = int((np.abs(pos_train) > 1e-5).sum())
        if n_active / max(1, train_mask.sum()) * 100 >= 8.0 and sr > best_sharpe:
            best_sharpe = sr
            best_pct = pct

    # Generate full positions with best percentile
    positions = np.zeros(T, dtype=np.float64)
    for t in range(1, T):
        history = Z_composite[:t]
        z = Z_composite[t]
        pct_rank = (history < z).sum() / len(history) * 100.0
        if pct_rank > (100.0 - best_pct):
            positions[t] = 1.0
        elif pct_rank < best_pct:
            if not long_only:
                positions[t] = -1.0

    info = {"best_pct": best_pct, "train_sharpe": best_sharpe}
    return positions, info


def arm_rolling_percentile(Z_composite, trade_returns, train_mask, fee_bps,
                           long_only=False, window=480):
    """Arm 4: Trade when Z[t] in top/bottom P% of trailing 480d window."""
    T = len(Z_composite)
    # Sweep percentile on training data
    best_pct = 15.0
    best_sharpe = -np.inf
    for pct in [10.0, 12.0, 15.0, 18.0, 20.0, 25.0]:
        positions_trial = np.zeros(T, dtype=np.float64)
        for t in range(window, T):
            win = Z_composite[t - window:t]
            z = Z_composite[t]
            pct_rank = (win < z).sum() / len(win) * 100.0
            if pct_rank > (100.0 - pct):
                positions_trial[t] = 1.0
            elif pct_rank < pct:
                if not long_only:
                    positions_trial[t] = -1.0
        pos_train = positions_trial[train_mask]
        ret_train = trade_returns[train_mask]
        net, _, _ = simulate_etf_spot(ret_train, pos_train, fee_bps=fee_bps)
        std = np.std(net)
        sr = float((np.mean(net) / std) * np.sqrt(252)) if std > 1e-12 else 0.0
        n_active = int((np.abs(pos_train) > 1e-5).sum())
        if n_active / max(1, train_mask.sum()) * 100 >= 8.0 and sr > best_sharpe:
            best_sharpe = sr
            best_pct = pct

    # Generate full positions
    positions = np.zeros(T, dtype=np.float64)
    for t in range(window, T):
        win = Z_composite[t - window:t]
        z = Z_composite[t]
        pct_rank = (win < z).sum() / len(win) * 100.0
        if pct_rank > (100.0 - best_pct):
            positions[t] = 1.0
        elif pct_rank < best_pct:
            if not long_only:
                positions[t] = -1.0

    info = {"best_pct": best_pct, "window": window, "train_sharpe": best_sharpe}
    return positions, info


def arm_walkforward(Z_composite, trade_returns, train_mask, fee_bps,
                    long_only=False, cadence=60, window=480):
    """Arm 5: Re-sweep threshold every 60d on trailing 480d, x1.10 buffer."""
    T = len(Z_composite)
    positions = np.zeros(T, dtype=np.float64)

    # Initial threshold from training data
    Z_train = Z_composite[train_mask]
    ret_train = trade_returns[train_mask]
    sweep_info = sweep_optimal_threshold(Z_train, ret_train, mode="binary",
                                         fee_bps=fee_bps, long_only=long_only)
    z_th_l = round(sweep_info["optimal_z_th_long"] * 1.10, 2)
    z_th_s = round(sweep_info["optimal_z_th_short"] * 1.10, 2)

    last_recal = 0
    for t in range(T):
        # Re-calibrate every cadence days (using trailing window)
        if t > window and (t - last_recal) >= cadence:
            win_start = t - window
            Z_win = Z_composite[win_start:t]
            ret_win = trade_returns[win_start:t]
            sw = sweep_optimal_threshold(Z_win, ret_win, mode="binary",
                                         fee_bps=fee_bps, long_only=long_only)
            z_th_l = round(sw["optimal_z_th_long"] * 1.10, 2)
            z_th_s = round(sw["optimal_z_th_short"] * 1.10, 2)
            last_recal = t

        # Generate position for day t
        z = Z_composite[t]
        if z > z_th_l:
            positions[t] = 1.0
        elif z < -z_th_s and not long_only:
            positions[t] = -1.0

    info = {"cadence": cadence, "window": window, "final_z_l": z_th_l, "final_z_s": z_th_s}
    return positions, info


def arm_variance_scaled(Z_composite, trade_returns, train_mask, fee_bps,
                        long_only=False, std_window=252):
    """Arm 6: z_th[t] = k * rolling_std(Z, 252d). Sweep k on training."""
    T = len(Z_composite)
    # Compute rolling std
    rolling_std = np.zeros(T, dtype=np.float64)
    for t in range(std_window, T):
        rolling_std[t] = np.std(Z_composite[t - std_window:t])
    # Fill early values with expanding std
    for t in range(1, std_window):
        rolling_std[t] = np.std(Z_composite[:t]) if t > 10 else 0.5

    # Sweep k on training data
    best_k = 2.0
    best_sharpe = -np.inf
    for k in [1.5, 1.75, 2.0, 2.25, 2.5, 3.0]:
        positions_trial = np.zeros(T, dtype=np.float64)
        for t in range(T):
            z_th = k * rolling_std[t]
            z = Z_composite[t]
            if z > z_th:
                positions_trial[t] = 1.0
            elif z < -z_th and not long_only:
                positions_trial[t] = -1.0
        pos_train = positions_trial[train_mask]
        ret_train = trade_returns[train_mask]
        net, _, _ = simulate_etf_spot(ret_train, pos_train, fee_bps=fee_bps)
        std = np.std(net)
        sr = float((np.mean(net) / std) * np.sqrt(252)) if std > 1e-12 else 0.0
        n_active = int((np.abs(pos_train) > 1e-5).sum())
        if n_active / max(1, train_mask.sum()) * 100 >= 8.0 and sr > best_sharpe:
            best_sharpe = sr
            best_k = k

    # Generate full positions
    positions = np.zeros(T, dtype=np.float64)
    for t in range(T):
        z_th = best_k * rolling_std[t]
        z = Z_composite[t]
        if z > z_th:
            positions[t] = 1.0
        elif z < -z_th and not long_only:
            positions[t] = -1.0

    info = {"best_k": best_k, "std_window": std_window, "train_sharpe": best_sharpe}
    return positions, info


# =============================================================================
# Group B: Feature Hysteresis (signal construction change)
# =============================================================================

def compute_icw_hysteresis(Z_std, signs, ic_mat, cluster_ids, n_train,
                           top_k=10, exit_rank=15, max_per_group=1):
    """
    ICW with feature selection hysteresis (cluster-aware).
    Enter: feature ranks <= top_k AND cluster not occupied.
    Exit: feature ranks > exit_rank (wider threshold to leave).
    Features in ranks (top_k, exit_rank] are 'on probation' - they stay.
    """
    T, N = Z_std.shape
    se_ic = 1.0 / np.sqrt(n_train)
    Z_signed = Z_std * signs
    Z_composite = np.zeros(T, dtype=np.float64)

    # Track active feature set
    active_set = set()

    for t in range(T):
        scores = ic_mat[t]
        # Rank features by score (descending)
        order = np.argsort(scores)[::-1]
        rank_of = np.zeros(N, dtype=np.int64)
        for rank_pos, idx in enumerate(order):
            rank_of[idx] = rank_pos + 1  # 1-based rank

        # --- Hysteresis logic ---
        # 1. Remove features that dropped below exit_rank
        to_remove = []
        for feat_idx in active_set:
            if rank_of[feat_idx] > exit_rank:
                to_remove.append(feat_idx)
        for feat_idx in to_remove:
            active_set.discard(feat_idx)

        # 2. Add new features that rank <= top_k (respecting cluster constraint)
        # Build occupied clusters from current active set
        occupied_clusters = {}
        if cluster_ids is not None:
            for feat_idx in active_set:
                c = int(cluster_ids[feat_idx])
                occupied_clusters[c] = feat_idx

        # Greedy add from top-ranked features
        for idx in order:
            if len(active_set) >= top_k:
                break
            idx_int = int(idx)
            if idx_int in active_set:
                continue
            if rank_of[idx_int] > top_k:
                break  # No more eligible entrants
            # Check cluster constraint
            if cluster_ids is not None:
                c = int(cluster_ids[idx_int])
                if c in occupied_clusters:
                    continue  # Cluster already occupied
                occupied_clusters[c] = idx_int
            active_set.add(idx_int)

        # 3. Compute ICW weights for active set
        if len(active_set) == 0:
            Z_composite[t] = 0.0
            continue

        active_idx = np.array(sorted(active_set), dtype=np.int64)
        w_t = np.zeros(N, dtype=np.float64)
        raw_w = np.maximum(0.0, scores[active_idx] - se_ic)
        w_sum = raw_w.sum()
        if w_sum < 1e-12:
            w_t[active_idx] = 1.0 / float(len(active_idx))
        else:
            w_t[active_idx] = raw_w / w_sum
        Z_composite[t] = Z_signed[t] @ w_t

    return Z_composite


def arm_hysteresis(etf, side, df, pool, Z_std, signs, feat_names,
                   full_trade_ret, train_mask, fee_bps, cluster_ids,
                   ic_mode="rolling_tail", tail_window=480, tail_pct=0.10,
                   top_k=10, exit_rank=15, long_only=False):
    """Arm 7: Feature hysteresis + baseline threshold."""
    from utils import rolling_tail_ic_numba, expanding_factor_ic_numba

    # Compute IC matrix
    burn_in = 252 if len(df) > 500 else 100
    if ic_mode == "rolling_tail":
        ic_raw = rolling_tail_ic_numba(Z_std, signs, full_trade_ret,
                                       window=tail_window, tail_pct=tail_pct, burn_in=burn_in)
    else:
        ic_raw = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)

    # EMA smooth
    ema_span = resolve_ic_ema_span(etf, None)
    T, N = Z_std.shape
    alpha = 2.0 / (ema_span + 1.0)
    ic_mat = np.zeros_like(ic_raw)
    ic_mat[0] = ic_raw[0]
    for t in range(1, T):
        ic_mat[t] = alpha * ic_raw[t] + (1.0 - alpha) * ic_mat[t - 1]

    # Compute Z_composite with hysteresis
    n_train = int(train_mask.sum())
    if n_train < 252:
        n_train = 1700
    Z_composite = compute_icw_hysteresis(
        Z_std, signs, ic_mat, cluster_ids, n_train,
        top_k=top_k, exit_rank=exit_rank, max_per_group=1
    )

    # Apply baseline threshold
    positions, info = arm_baseline(Z_composite, full_trade_ret, train_mask, fee_bps, long_only)
    info["exit_rank"] = exit_rank
    return positions, info, Z_composite


# =============================================================================
# Main
# =============================================================================

def evaluate_positions(positions, trade_returns, oos_mask, fee_bps, dates=None, bars_dict=None):
    """Evaluate positions on OOS slice. Uses stoploss simulation if bars_dict provided."""
    pos_oos = positions[oos_mask]
    ret_oos = trade_returns[oos_mask]
    df_dates = dates[oos_mask] if dates is not None else None
    if isinstance(df_dates, pd.Series):
        df_dates = df_dates.reset_index(drop=True)

    if bars_dict:
        net_ret, raw_ret, stop_hits, trig_pct = simulate_full_series(
            df_dates, pos_oos, bars_dict, method="time_decay_trailing",
            param=0.03, fee_bps=fee_bps
        )
    else:
        net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, pos_oos, fee_bps=fee_bps)

    metrics = calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_dates)
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Z-Threshold System A/B Test (7 arms x 3 ETFs)")
    parser.add_argument("--fee-bps", type=float, default=FEE_BPS_DEFAULT)
    parser.add_argument("--start-date", type=str, default="2022-01-01")
    parser.add_argument("--end-date", type=str, default="2026-01-01")
    parser.add_argument("-o", "--output", type=str, default=None)
    args = parser.parse_args()

    fee_bps = args.fee_bps / 10000.0

    print("=" * 90)
    print("Z-THRESHOLD SYSTEM A/B TEST - 7 Arms x 3 ETFs")
    print(f"OOS=[{args.start_date} ~ {args.end_date}] | Fee={args.fee_bps} bps")
    print("=" * 90)

    ARM_NAMES = [
        "1_Baseline",
        "2_90pct_Peak",
        "3_ExpPercentile",
        "4_RollPct480",
        "5_WalkFwd60d",
        "6_VarScaled",
        "7_Hysteresis",
    ]

    results = []

    for etf in AVAILABLE_ETFS:
        print(f"\n{'='*70}")
        print(f"  {etf}")
        print(f"{'='*70}")

        # Load data
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool or len(pool) < 10:
            print(f"  [SKIP] Pool too small ({len(pool) if pool else 0})")
            continue

        df = load_etf_dataset(etf)
        full_trade_ret = (df["trade_return"].values.astype(np.float64)
                         if "trade_return" in df.columns
                         else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        # Cluster assignments
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
            print(f"  [INFO] {len(set(cluster_ids))} ONC clusters loaded.")

        # Load 1m bars for stoploss evaluation
        bars_dict = load_intraday_bars_dict(etf)
        if bars_dict:
            print(f"  [INFO] 1m bars loaded ({len(bars_dict)} days) - stoploss enabled.")
        else:
            print(f"  [WARNING] No 1m bars - falling back to simple simulation.")

        # Compute standard Z_composite (rolling tail IC + ICW)
        ic_raw = rolling_tail_ic_numba(Z_std, signs, full_trade_ret,
                                       window=TAIL_WINDOW, tail_pct=TAIL_PCT, burn_in=burn_in)
        ema_span = resolve_ic_ema_span(etf, None)
        T, N = Z_std.shape
        alpha_ema = 2.0 / (ema_span + 1.0)
        ic_mat = np.zeros_like(ic_raw)
        ic_mat[0] = ic_raw[0]
        for t in range(1, T):
            ic_mat[t] = alpha_ema * ic_raw[t] + (1.0 - alpha_ema) * ic_mat[t - 1]

        n_train_ts = pd.Timestamp(args.start_date)
        train_mask = (df["date"] < n_train_ts).values
        n_train = int(train_mask.sum())
        if n_train < 252:
            n_train = 1700

        Z_composite = compute_icw(Z_std, signs, pool=pool, n_train=n_train,
                                  expanding_ic=ic_raw, top_k=TOP_K,
                                  ic_ema_span=ema_span,
                                  cluster_ids=cluster_ids, max_per_group=1)

        # OOS mask
        t_start = pd.Timestamp(args.start_date)
        t_end = pd.Timestamp(args.end_date)
        oos_mask = ((df["date"] >= t_start) & (df["date"] < t_end)).values
        dates = df["date"]

        # --- Run Group A arms (same Z_composite) ---
        group_a_arms = [
            ("1_Baseline", arm_baseline),
            ("2_90pct_Peak", arm_90pct_peak),
            ("3_ExpPercentile", arm_expanding_percentile),
            ("4_RollPct480", arm_rolling_percentile),
            ("5_WalkFwd60d", arm_walkforward),
            ("6_VarScaled", arm_variance_scaled),
        ]

        for arm_name, arm_func in group_a_arms:
            print(f"  [{arm_name}]...", end=" ", flush=True)
            positions, info = arm_func(Z_composite, full_trade_ret, train_mask, fee_bps)
            metrics = evaluate_positions(positions, full_trade_ret, oos_mask, fee_bps, dates, bars_dict)
            if metrics:
                results.append({
                    "Arm": arm_name, "ETF": etf,
                    "CostSharpe": metrics.get("cost_sharpe", 0),
                    "RawSharpe": metrics.get("raw_sharpe", 0),
                    "TotalPnL": metrics.get("total_pnl", 0),
                    "MaxDD": metrics.get("max_drawdown", 0),
                    "WinRate": metrics.get("win_rate_pct", 0),
                    "Trades": metrics.get("n_trades", 0),
                    "ActivePct": metrics.get("active_pct", 0),
                })
                print(f"Sharpe={metrics.get('cost_sharpe', 0):.3f} | "
                      f"PnL={metrics.get('total_pnl', 0):+.4f} | "
                      f"Trades={metrics.get('n_trades', 0)}")
            else:
                print("FAILED")

        # --- Run Group B arm (hysteresis - different Z_composite) ---
        print(f"  [7_Hysteresis]...", end=" ", flush=True)
        positions_h, info_h, Z_hyst = arm_hysteresis(
            etf, "single", df, pool, Z_std, signs, feat_names,
            full_trade_ret, train_mask, fee_bps, cluster_ids,
            ic_mode="rolling_tail", tail_window=TAIL_WINDOW, tail_pct=TAIL_PCT,
            top_k=TOP_K, exit_rank=EXIT_RANK
        )
        metrics_h = evaluate_positions(positions_h, full_trade_ret, oos_mask, fee_bps, dates, bars_dict)
        if metrics_h:
            results.append({
                "Arm": "7_Hysteresis", "ETF": etf,
                "CostSharpe": metrics_h.get("cost_sharpe", 0),
                "RawSharpe": metrics_h.get("raw_sharpe", 0),
                "TotalPnL": metrics_h.get("total_pnl", 0),
                "MaxDD": metrics_h.get("max_drawdown", 0),
                "WinRate": metrics_h.get("win_rate_pct", 0),
                "Trades": metrics_h.get("n_trades", 0),
                "ActivePct": metrics_h.get("active_pct", 0),
            })
            print(f"Sharpe={metrics_h.get('cost_sharpe', 0):.3f} | "
                  f"PnL={metrics_h.get('total_pnl', 0):+.4f} | "
                  f"Trades={metrics_h.get('n_trades', 0)}")
        else:
            print("FAILED")

    # ─── Summary Report ────────────────────────────────────────────────────────
    if not results:
        print("\nERROR: No results collected.")
        return

    df_res = pd.DataFrame(results)

    print("\n" + "=" * 90)
    print("RESULTS - RANKED BY AVG COST SHARPE")
    print("=" * 90)

    avg_by_arm = df_res.groupby("Arm").agg(
        AvgSharpe=("CostSharpe", "mean"),
        AvgPnL=("TotalPnL", "mean"),
        AvgMaxDD=("MaxDD", "mean"),
        AvgWinRate=("WinRate", "mean"),
        AvgTrades=("Trades", "mean"),
        AvgActivePct=("ActivePct", "mean"),
    ).reset_index().sort_values("AvgSharpe", ascending=False)

    baseline_sharpe = avg_by_arm.loc[avg_by_arm["Arm"] == "1_Baseline", "AvgSharpe"].values
    base_sr = baseline_sharpe[0] if len(baseline_sharpe) > 0 else 0.0

    print(f"\n{'Rank':<5} {'Arm':<20} {'AvgSharpe':>10} {'Delta':>8} {'AvgPnL':>10} "
          f"{'AvgMaxDD':>9} {'AvgWR%':>7} {'AvgTrades':>10} {'Active%':>8}")
    print("-" * 95)
    for rank_idx, (_, row) in enumerate(avg_by_arm.iterrows(), 1):
        delta = row["AvgSharpe"] - base_sr
        marker = " *" if row["Arm"] == "1_Baseline" else ""
        print(f"{rank_idx:<5} {row['Arm']:<20} {row['AvgSharpe']:>10.3f} {delta:>+8.3f} "
              f"{row['AvgPnL']:>10.4f} {row['AvgMaxDD']:>9.4f} {row['AvgWinRate']:>7.1f} "
              f"{row['AvgTrades']:>10.0f} {row['AvgActivePct']:>8.1f}{marker}")

    # Per-ETF detail
    print("\n" + "-" * 90)
    print("PER-ETF DETAIL")
    print("-" * 90)
    for etf in AVAILABLE_ETFS:
        sub = df_res[df_res["ETF"] == etf].sort_values("CostSharpe", ascending=False)
        if sub.empty:
            continue
        print(f"\n  {etf}:")
        print(f"  {'Arm':<20} {'CostSharpe':>10} {'TotalPnL':>10} {'MaxDD':>8} "
              f"{'WR%':>6} {'Trades':>7} {'Active%':>8}")
        for _, r in sub.iterrows():
            marker = " *" if r["Arm"] == "1_Baseline" else ""
            print(f"  {r['Arm']:<20} {r['CostSharpe']:>10.3f} {r['TotalPnL']:>10.4f} "
                  f"{r['MaxDD']:>8.4f} {r['WinRate']:>6.1f} {r['Trades']:>7} "
                  f"{r['ActivePct']:>8.1f}{marker}")

    # Per-ETF winner
    print("\n" + "-" * 90)
    print("PER-ETF WINNER")
    print("-" * 90)
    for etf in AVAILABLE_ETFS:
        sub = df_res[df_res["ETF"] == etf].sort_values("CostSharpe", ascending=False)
        if not sub.empty:
            best = sub.iloc[0]
            delta = best["CostSharpe"] - base_sr
            print(f"  {etf}: {best['Arm']} (Sharpe={best['CostSharpe']:.3f}, Delta={delta:+.3f})")

    # Save
    out_csv = Path(args.output) if args.output else HERE / "zthreshold_ab_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nSaved results to {out_csv}")
    print("\n[OK] Z-Threshold A/B test complete.")


if __name__ == "__main__":
    main()
