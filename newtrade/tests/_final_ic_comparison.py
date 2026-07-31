#!/usr/bin/env python3
"""Final comparison: Tail IC 10% vs 15% vs Rolling Total IC (Pearson), at 480d window.
Tests both 2022 OOS (default pool) and 2023 OOS (_p2015_2023 pool)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from numba import njit
from run_backtest import run_single_backtest, resolve_ic_ema_span
from utils import load_etf_dataset, load_admitted_pool, build_pool_feature_matrix, expanding_zscore_numba, load_cluster_assignments

ETFS = ["300ETF", "500ETF", "159915ETF"]
WINDOW = 480


@njit(cache=True)
def rolling_total_ic_numba(Z_std, signs, trade_returns, window=480, burn_in=252):
    """Rolling Pearson IC (total, not tail) for comparison."""
    T, N = Z_std.shape
    IC_matrix = np.zeros((T, N), dtype=np.float64)
    effective_start = max(burn_in, window)
    if T < effective_start or N == 0:
        return IC_matrix
    Z_signed = np.zeros((T, N), dtype=np.float64)
    for j in range(N):
        Z_signed[:, j] = Z_std[:, j] * signs[j]
    for t in range(effective_start, T):
        win_start = t - window
        for j in range(N):
            sum_z = 0.0; sum_z2 = 0.0; sum_y = 0.0; sum_y2 = 0.0; sum_zy = 0.0
            for i in range(window):
                z = Z_signed[win_start + i, j]
                y = trade_returns[win_start + i]
                sum_z += z; sum_z2 += z * z; sum_y += y; sum_y2 += y * y; sum_zy += z * y
            n = float(window)
            mean_z = sum_z / n; mean_y = sum_y / n
            var_z = (sum_z2 / n) - mean_z * mean_z
            var_y = (sum_y2 / n) - mean_y * mean_y
            if var_z > 1e-12 and var_y > 1e-12:
                cov = (sum_zy / n) - mean_z * mean_y
                IC_matrix[t, j] = cov / (np.sqrt(var_z) * np.sqrt(var_y))
    if effective_start < T:
        for t in range(effective_start):
            IC_matrix[t, :] = IC_matrix[effective_start, :]
    return IC_matrix


def run_with_custom_ic(etf, ic_matrix, start_date, end_date, cluster_suffix=""):
    """Run backtest with a pre-computed IC matrix injected via pool_override trick."""
    # We'll use run_single_backtest but monkey-patch the IC — actually easier to
    # just call the internals directly
    from strategy import sweep_optimal_threshold, compute_production_threshold, generate_positions, simulate_etf_spot, calculate_metrics
    from weighting import get_weighting_scheme

    pool = load_admitted_pool(etf, side="single", min_features=10, suffix=cluster_suffix)
    if not pool:
        return None
    df = load_etf_dataset(etf)
    full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values
    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    # Cluster
    feat_to_cluster = load_cluster_assignments(etf, "single", suffix=cluster_suffix)
    cluster_ids = None
    if feat_to_cluster:
        cids = []
        next_cid = (max(feat_to_cluster.values()) + 1) if feat_to_cluster else 1000
        for fn in feat_names:
            if fn in feat_to_cluster:
                cids.append(feat_to_cluster[fn])
            else:
                cids.append(next_cid); next_cid += 1
        cluster_ids = np.array(cids, dtype=np.int64)

    n_train = int((df["date"] < __import__("pandas").Timestamp(start_date)).sum())
    if n_train < 252:
        n_train = 1700

    # ICW with injected IC matrix
    icw = get_weighting_scheme("icw")
    ema_span = resolve_ic_ema_span(etf, None)
    Z_composite = icw(Z_std, signs, pool=pool, n_train=n_train,
                      expanding_ic=ic_matrix, top_k=10, ic_ema_span=ema_span,
                      cluster_ids=cluster_ids, max_per_group=1)

    # Threshold
    t_start_ts = __import__("pandas").Timestamp(start_date)
    train_mask = df["date"] < t_start_ts
    sweep_info = sweep_optimal_threshold(Z_composite[train_mask.values], full_trade_ret[train_mask.values],
                                         mode="binary", fee_bps=0.0008, long_only=False)
    z_th_l, z_th_s = compute_production_threshold(sweep_info, z_buffer=0.1)

    positions = generate_positions(Z_composite, z_th=z_th_l, z_th_short=z_th_s, mode="binary", long_only=False)
    t_end = __import__("pandas").Timestamp(end_date)
    mask = (df["date"] >= t_start_ts) & (df["date"] < t_end)
    if not mask.any():
        return None
    pos_oos = positions[mask.values]
    ret_oos = full_trade_ret[mask.values]
    net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, pos_oos, fee_bps=0.0008)
    df_oos = df[mask].reset_index(drop=True)
    metrics = calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_oos["date"])
    return metrics


def main():
    scenarios = [
        ("2022 OOS (default pool)", "2022-01-01", "2026-01-01", ""),
        ("2023 OOS (_p2015_2023 pool)", "2023-01-01", "2026-01-01", "_p2015_2023"),
    ]

    for scenario_name, start, end, suffix in scenarios:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario_name} | Window=480d")
        print(f"{'='*70}")

        for etf in ETFS:
            pool = load_admitted_pool(etf, side="single", min_features=10, suffix=suffix)
            if not pool:
                print(f"  {etf}: SKIP (pool < 10)")
                continue
            df = load_etf_dataset(etf)
            full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0.0).values
            X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
            burn_in = 252 if len(df) > 500 else 100
            Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

            # Compute 3 IC variants
            from utils import rolling_tail_ic_numba, expanding_factor_ic_numba
            ic_tail10 = rolling_tail_ic_numba(Z_std, signs, full_trade_ret, window=WINDOW, tail_pct=0.10, burn_in=burn_in)
            ic_tail15 = rolling_tail_ic_numba(Z_std, signs, full_trade_ret, window=WINDOW, tail_pct=0.15, burn_in=burn_in)
            ic_total = rolling_total_ic_numba(Z_std, signs, full_trade_ret, window=WINDOW, burn_in=burn_in)
            ic_expanding = expanding_factor_ic_numba(Z_std, signs, full_trade_ret, burn_in=burn_in)

            print(f"\n  {etf} (N={len(pool)}):")
            for label, ic_mat in [("Expanding Total IC", ic_expanding),
                                   ("Rolling 480d Total IC", ic_total),
                                   ("Rolling 480d Tail 10%", ic_tail10),
                                   ("Rolling 480d Tail 15%", ic_tail15)]:
                m = run_with_custom_ic(etf, ic_mat, start, end, cluster_suffix=suffix)
                if m:
                    print(f"    {label:25s}: Sharpe={m['cost_sharpe']:.3f}  PnL={m['total_pnl']:+.4f}  WR={m['win_rate_pct']:.1f}%")


if __name__ == "__main__":
    main()
