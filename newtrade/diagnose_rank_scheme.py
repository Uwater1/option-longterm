#!/usr/bin/env python3
"""
Scheme 4 — Rank Bounded Mapping Dedicated Diagnostic Suite.
Provides deep-dive diagnostic tools:
  1. Parameter & Mapping Sensitivity Sweep (min/max ratio, linear/power/softmax/top_k).
  2. Factor Rank Calibration (OOS return comparison of top vs bottom ranked factors).
  3. Per-Factor PnL Contribution Decomposition.
  4. Conviction Threshold & Signal Bin Analysis (|Z| intervals).
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, load_future_trade_returns

from weighting import get_rank_weights, _compute_pool_scores, compute_rank_w
from strategy import generate_positions, simulate_etf_spot, calculate_metrics, sweep_optimal_threshold, compute_production_threshold, build_trade_log_df


def run_rank_sensitivity_sweep(etf: str, df: pd.DataFrame, pool: list, X_raw: np.ndarray, signs: np.ndarray,
                               start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                               position_mode: str = "tanh", fee_bps: float = 0.0008, z_buffer: float = 0.1,
                               trade_returns_full: np.ndarray = None) -> pd.DataFrame:
    """
    Grid sweep across ratio bounds, mapping shapes, powers, and top_k settings.
    """
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    
    train_mask = df["date"] < t_start
    oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not oos_mask.any():
        oos_mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[oos_mask].reset_index(drop=True)
    if trade_returns_full is not None:
        trade_returns_train = trade_returns_full[train_mask.values]
        trade_returns_oos = trade_returns_full[oos_mask.values]
    else:
        trade_returns_train = df[train_mask]["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df[train_mask]["close"].pct_change().fillna(0.0).values
        trade_returns_oos = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df_oos["close"].pct_change().fillna(0.0).values

    configurations = [
        # (label, min_ratio, max_ratio, mapping_shape, power, softmax_tau, top_k)
        ("Linear (0.5 ~ 1.5) [Default]", 0.5, 1.5, "linear", 2.0, 1.0, None),
        ("Linear (0.2 ~ 1.8) [Moderate Tilt]", 0.2, 1.8, "linear", 2.0, 1.0, None),
        ("Linear (0.0 ~ 2.0) [Max Tilt]", 0.0, 2.0, "linear", 2.0, 1.0, None),
        ("Linear (1.0 ~ 1.0) [Equal Weight Baseline]", 1.0, 1.0, "linear", 2.0, 1.0, None),
        ("Power p=2.0 (0.2 ~ 1.8)", 0.2, 1.8, "power", 2.0, 1.0, None),
        ("Power p=3.0 (0.1 ~ 1.9)", 0.1, 1.9, "power", 3.0, 1.0, None),
        ("Softmax tau=1.0", 0.5, 1.5, "softmax", 2.0, 1.0, None),
        ("Softmax tau=2.0", 0.5, 1.5, "softmax", 2.0, 2.0, None),
        ("Top-7 Truncated Linear", 0.5, 1.5, "top_k", 2.0, 1.0, 7),
        ("Top-5 Truncated Linear", 0.5, 1.5, "top_k", 2.0, 1.0, 5),
    ]

    sweep_rows = []
    for label, min_r, max_r, shape, pow_val, tau, k_val in configurations:
        if shape == "top_k" and k_val and k_val > len(pool):
            continue

        rank_kwargs = {
            "w_min_ratio": min_r,
            "w_max_ratio": max_r,
            "mapping_shape": shape,
            "power": pow_val,
            "softmax_tau": tau,
            "top_k": k_val,
        }

        Z_comp = compute_rank_w(Z_std, signs, pool, **rank_kwargs)
        
        # Train threshold sweep
        Z_comp_train = Z_comp[train_mask.values]
        sw_res = sweep_optimal_threshold(Z_comp_train, trade_returns_train, mode=position_mode, fee_bps=fee_bps)
        z_th_long, z_th_short = compute_production_threshold(sw_res, z_buffer=z_buffer)

        # OOS simulation
        Z_comp_oos = Z_comp[oos_mask.values]
        positions_oos = generate_positions(Z_comp, z_th=z_th_long, z_th_short=z_th_short, mode=position_mode, long_only=True)[oos_mask.values]
        net_ret, raw_ret, fees = simulate_etf_spot(trade_returns_oos, positions_oos, fee_bps=fee_bps)

        metrics = calculate_metrics(net_ret, raw_ret, positions_oos, dates=df_oos["date"])
        
        sweep_rows.append({
            "config": label,
            "mapping": shape,
            "w_min_max": f"{min_r:.1f}~{max_r:.1f}",
            "z_th_prod": z_th_long,
            "trades": metrics["n_trades"],

            "cost_sharpe": metrics["cost_sharpe"],
            "raw_sharpe": metrics["raw_sharpe"],
            "total_pnl": metrics["total_pnl"],
            "max_dd": metrics["max_drawdown"],
            "win_rate": f"{metrics['win_rate_pct']:.1f}%",
            "turnover": f"{metrics['ann_turnover']:.1f}x",
        })

    return pd.DataFrame(sweep_rows)


def analyze_factor_contributions(etf: str, df: pd.DataFrame, pool: list, X_raw: np.ndarray, signs: np.ndarray,
                                 start_date: str = "2022-01-01", end_date: str = "2026-01-01",
                                 trade_returns_full: np.ndarray = None) -> pd.DataFrame:
    """
    Decompose per-factor PnL contribution OOS:
    contrib_{i,t} = w_i * sign_i * z_{i,t} * r_t
    """
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    
    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
    if not oos_mask.any():
        oos_mask = df["date"] >= df["date"].iloc[-1000]

    df_oos = df[oos_mask].reset_index(drop=True)
    if trade_returns_full is not None:
        trade_returns = trade_returns_full[oos_mask.values]
    else:
        trade_returns = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df_oos.columns else df_oos["close"].pct_change().fillna(0.0).values
    
    weights = get_rank_weights(pool, w_min_ratio=0.5, w_max_ratio=1.5, mapping_shape="linear")
    scores = _compute_pool_scores(pool)

    Z_oos = Z_std[oos_mask.values]
    
    # Per-factor daily signed return component: w_i * sign_i * z_{i,t} * r_t
    N = len(pool)
    rows = []
    for i, item in enumerate(pool):
        w_i = weights[i]
        sign_i = signs[i]
        z_i = Z_oos[:, i]
        
        raw_contrib = (sign_i * z_i) * trade_returns
        weighted_contrib = w_i * raw_contrib
        
        cum_contrib = float(weighted_contrib.sum())
        ic_i = float(np.corrcoef(z_i, trade_returns)[0, 1]) if np.std(z_i) > 1e-6 else 0.0

        rows.append({
            "rank_index": N - i,
            "feature": item["feature_name"],
            "weight": round(w_i, 4),
            "deflated_ic": round(item.get("deflated_ic", 0.0), 4),
            "ic_ir": round(item.get("ic_ir", 0.0), 4),
            "mono": round(item.get("monotonicity", 0.0), 4),
            "composite_score": round(scores[i], 4),
            "oos_ic": round(ic_i, 4),
            "total_weighted_pnl": round(cum_contrib, 6),
        })

    df_contrib = pd.DataFrame(rows).sort_values("composite_score", ascending=False).reset_index(drop=True)
    df_contrib["rank"] = range(1, len(df_contrib) + 1)
    return df_contrib


def analyze_conviction_bins(df_oos: pd.DataFrame, Z_composite_oos: np.ndarray, positions_oos: np.ndarray,
                            net_returns: np.ndarray) -> pd.DataFrame:
    """
    Bin signal Z_composite values to inspect Sharpe, WinRate, and Trade frequency by conviction strength.
    """
    bins = [0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 99.0]
    labels = ["0.0 ~ 0.3", "0.3 ~ 0.6", "0.6 ~ 0.9", "0.9 ~ 1.2", "1.2 ~ 1.5", "> 1.5"]
    
    abs_z = np.abs(Z_composite_oos)
    bin_indices = np.digitize(abs_z, bins) - 1

    bin_rows = []
    for b_idx, label in enumerate(labels):
        mask = bin_indices == b_idx
        n_days = int(mask.sum())
        if n_days == 0:
            continue

        pos_b = positions_oos[mask]
        ret_b = net_returns[mask]
        n_active = int((np.abs(pos_b) > 1e-5).sum())

        std_r = np.std(ret_b)
        mean_r = np.mean(ret_b)
        sharpe = float((mean_r / std_r) * np.sqrt(252)) if std_r > 1e-12 else 0.0

        win_rate = float((ret_b > 0).sum() / n_active * 100.0) if n_active > 0 else 0.0
        total_pnl = float(ret_b.sum())

        bin_rows.append({
            "conviction_bin": label,
            "n_days": n_days,
            "active_trades": n_active,
            "total_pnl": round(total_pnl, 4),
            "cost_sharpe": round(sharpe, 3),
            "win_rate": f"{win_rate:.1f}%",
        })

    return pd.DataFrame(bin_rows)


def run_diagnosis(etf: str, start_date: str = "2022-01-01", end_date: str = "2026-01-01", use_future: bool = False):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        print(f"[SKIP] ETF {etf} has < 10 admitted features.")
        return

    df = load_etf_dataset(etf)

    trade_returns_full = None
    asset_label = "Spot ETF"
    if use_future:
        fut_returns, fut_ok, fut_name = load_future_trade_returns(etf, df)
        if not fut_ok:
            print(f"[SKIP] {etf} has no Index Future mapping for --future mode.")
            return
        trade_returns_full = fut_returns
        asset_label = f"Future ({fut_name})"

    print("=" * 80)
    print(f"SCHEME 4 (RANK BOUNDED MAPPING) DIAGNOSTIC SUITE — {etf} ({asset_label})")
    print("=" * 80)

    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)

    # 1. Parameter Sensitivity Grid Sweep
    print("\n--- 1. Parameter & Mapping Sensitivity Sweep ---")
    df_sweep = run_rank_sensitivity_sweep(etf, df, pool, X_raw, signs, start_date=start_date, end_date=end_date, trade_returns_full=trade_returns_full)
    print(df_sweep.to_string(index=False))

    # 2. Per-Factor PnL Contribution
    print("\n--- 2. Factor Rank & PnL Contribution Decomposition ---")
    df_contrib = analyze_factor_contributions(etf, df, pool, X_raw, signs, start_date=start_date, end_date=end_date, trade_returns_full=trade_returns_full)
    print(df_contrib[["rank", "feature", "weight", "composite_score", "deflated_ic", "oos_ic", "total_weighted_pnl"]].to_string(index=False))

    # 3. Conviction Signal Bins
    print("\n--- 3. Conviction Threshold Bins ---")
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    Z_comp = compute_rank_w(Z_std, signs, pool, w_min_ratio=0.5, w_max_ratio=1.5, mapping_shape="linear")

    t_start = pd.Timestamp(start_date)
    t_end = pd.Timestamp(end_date)
    oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
    df_oos = df[oos_mask].reset_index(drop=True)

    Z_comp_oos = Z_comp[oos_mask.values]
    if trade_returns_full is not None:
        trade_returns = trade_returns_full[oos_mask.values]
    else:
        trade_returns = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df_oos.columns else df_oos["close"].pct_change().fillna(0.0).values

    positions_oos = generate_positions(Z_comp, z_th=0.5, mode="tanh", long_only=True)[oos_mask.values]
    net_ret, _, _ = simulate_etf_spot(trade_returns, positions_oos, fee_bps=0.0008)

    df_bins = analyze_conviction_bins(df_oos, Z_comp_oos, positions_oos, net_ret)
    print(df_bins.to_string(index=False))

    # Save summary artifact CSVs
    artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    fut_suffix = "_future" if use_future else ""
    df_sweep.to_csv(artifacts_dir / f"diag_rank_sensitivity_{etf}{fut_suffix}.csv", index=False)
    df_contrib.to_csv(artifacts_dir / f"diag_factor_contrib_{etf}{fut_suffix}.csv", index=False)
    df_bins.to_csv(artifacts_dir / f"diag_conviction_bins_{etf}{fut_suffix}.csv", index=False)
    print(f"\nSaved diagnostic CSV artifacts for {etf} to {artifacts_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Scheme 4 Dedicated Diagnosis Suite")
    parser.add_argument("-e", "--etf", type=str, default="300ETF", help="Target ETF or 'all'")
    parser.add_argument("--start-date", type=str, default="2022-01-01", help="OOS Start Date")
    parser.add_argument("--end-date", type=str, default="2026-01-01", help="OOS End Date")
    parser.add_argument("--future", action="store_true", help="Trade underlying Index Futures (IF88 for 300ETF, IC88 for 500ETF, IH88 for 50ETF)")

    args = parser.parse_args()

    etfs = ["300ETF", "500ETF", "50ETF"] if args.etf.lower() == "all" else [args.etf]
    for etf in etfs:
        run_diagnosis(etf, start_date=args.start_date, end_date=args.end_date, use_future=args.future)


if __name__ == "__main__":
    main()

