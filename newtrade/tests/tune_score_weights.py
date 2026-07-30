#!/usr/bin/env python3
"""
Fast Numba & Precomputed Simplex Grid Search for Multi-Metric Score Weights in NewTrade.
Eliminates redundant feature & expanding metric calculations to run in < 2 seconds.
"""

import time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba
from strategy import compute_production_threshold

ETFS = ["300ETF", "500ETF", "159915ETF"]
START_DATE = "2022-01-01"
FEE_BPS = 0.0008  # 8 bps
EMA_SPAN = 30


@njit(cache=True)
def fast_ema_numba(mat: np.ndarray, span: int = 30) -> np.ndarray:
    T, N = mat.shape
    out = np.zeros_like(mat)
    alpha = 2.0 / (span + 1.0)
    out[0] = mat[0]
    for t in range(1, T):
        out[t] = alpha * mat[t] + (1.0 - alpha) * out[t-1]
    return out


@njit(cache=True)
def fast_compute_expanding_ranks(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray, burn_in: int = 252):
    T, N = Z_std.shape
    Z_signed = Z_std * signs
    daily_prod = np.zeros((T, N), dtype=np.float64)
    for t in range(T):
        daily_prod[t] = Z_signed[t] * trade_returns[t]

    cum_prod = np.zeros((T, N), dtype=np.float64)
    cum_sq_prod = np.zeros((T, N), dtype=np.float64)
    cum_pos = np.zeros((T, N), dtype=np.float64)

    for j in range(N):
        c_p = 0.0
        c_sq = 0.0
        c_pos = 0.0
        for t in range(T):
            dp = daily_prod[t, j]
            c_p += dp
            c_sq += dp * dp
            if dp > 0:
                c_pos += 1.0
            cum_prod[t, j] = c_p
            cum_sq_prod[t, j] = c_sq
            cum_pos[t, j] = c_pos

    r_ic_mat = np.zeros((T, N), dtype=np.float64)
    r_ir_mat = np.zeros((T, N), dtype=np.float64)
    r_mono_mat = np.zeros((T, N), dtype=np.float64)

    for t in range(burn_in, T):
        n_samples = float(t)
        m_prod = cum_prod[t-1] / n_samples
        v_prod = (cum_sq_prod[t-1] / n_samples) - m_prod**2
        s_prod = np.sqrt(np.maximum(1e-12, v_prod))
        ic_ir = m_prod / s_prod
        mono = cum_pos[t-1] / n_samples

        order_ic = np.argsort(m_prod)
        order_ir = np.argsort(ic_ir)
        order_mono = np.argsort(mono)

        for j in range(N):
            r_ic_mat[t, order_ic[j]] = (j + 1.0) / N
            r_ir_mat[t, order_ir[j]] = (j + 1.0) / N
            r_mono_mat[t, order_mono[j]] = (j + 1.0) / N

    if burn_in < T:
        for t in range(burn_in):
            r_ic_mat[t] = r_ic_mat[burn_in]
            r_ir_mat[t] = r_ir_mat[burn_in]
            r_mono_mat[t] = r_mono_mat[burn_in]

    return Z_signed, r_ic_mat, r_ir_mat, r_mono_mat


@njit(cache=True)
def fast_rank_weights_numba(Z_signed: np.ndarray, Score_mat: np.ndarray, w_min: float, w_max: float) -> np.ndarray:
    T, N = Z_signed.shape
    Z_comp = np.zeros(T, dtype=np.float64)
    if N == 1:
        return Z_signed[:, 0]

    for t in range(T):
        score_t = Score_mat[t]
        order = np.argsort(score_t)
        ranks = np.empty(N, dtype=np.float64)
        for i in range(N):
            ranks[order[i]] = float(i + 1)

        w_target = w_min + (w_max - w_min) * (ranks - 1.0) / (N - 1.0)
        w_target = w_target / np.sum(w_target)

        s = 0.0
        for j in range(N):
            s += Z_signed[t, j] * w_target[j]
        Z_comp[t] = s

    return Z_comp


@njit(cache=True)
def fast_eval_signal(Z_comp: np.ndarray, trade_ret: np.ndarray, z_th_long: float, z_th_short: float, fee_bps: float = 0.0008):
    T = len(Z_comp)
    net_returns = np.zeros(T, dtype=np.float64)
    raw_returns = np.zeros(T, dtype=np.float64)
    pos = np.zeros(T, dtype=np.float64)

    for t in range(T):
        z = Z_comp[t]
        if z > z_th_long:
            pos[t] = 1.0
        elif z < -z_th_short:
            pos[t] = -1.0
        else:
            pos[t] = 0.0

    pos_prev = 0.0
    for t in range(T):
        p = pos[t]
        raw_r = p * trade_ret[t]
        fee = np.abs(p) * fee_bps * 2.0  # intraday round-trip
        net_returns[t] = raw_r - fee
        raw_returns[t] = raw_r
        pos_prev = p

    mean_net = np.mean(net_returns)
    std_net = np.std(net_returns)
    cost_sharpe = (mean_net / std_net) * np.sqrt(252.0) if std_net > 1e-12 else 0.0
    total_pnl = np.sum(net_returns)

    n_active = 0
    win_cnt = 0
    for t in range(T):
        if np.abs(pos[t]) > 1e-5:
            n_active += 1
            if net_returns[t] > 0:
                win_cnt += 1

    win_rate = (win_cnt / n_active * 100.0) if n_active > 0 else 0.0

    # Max DD
    cum = np.cumsum(net_returns)
    peak = cum[0]
    max_dd = 0.0
    for t in range(T):
        if cum[t] > peak:
            peak = cum[t]
        dd = peak - cum[t]
        if dd > max_dd:
            max_dd = dd

    return cost_sharpe, total_pnl, win_rate, max_dd, n_active


@njit(cache=True)
def fast_sweep_thresholds(Z_comp_train: np.ndarray, trade_ret_train: np.ndarray, fee_bps: float = 0.0008):
    thresholds = np.linspace(0.1, 2.0, 39)
    best_sharpe_long = -999.0
    best_z_long = 0.5
    best_sharpe_short = -999.0
    best_z_short = 0.5

    # Sweep Long
    for z_th in thresholds:
        T = len(Z_comp_train)
        pos = np.zeros(T, dtype=np.float64)
        for t in range(T):
            if Z_comp_train[t] > z_th:
                pos[t] = 1.0

        pos_prev = 0.0
        r_sum = 0.0
        sq_sum = 0.0
        n_active = 0
        for t in range(T):
            p = pos[t]
            if p > 0:
                n_active += 1
            r = p * trade_ret_train[t] - np.abs(p) * fee_bps * 2.0
            r_sum += r
            sq_sum += r * r
            pos_prev = p

        act_pct = n_active / T * 100.0
        if act_pct >= 3.0 and T > 0:
            m = r_sum / T
            v = (sq_sum / T) - m * m
            s = np.sqrt(np.maximum(1e-12, v))
            sharpe = (m / s) * np.sqrt(252.0) if s > 1e-12 else 0.0
            if sharpe > best_sharpe_long:
                best_sharpe_long = sharpe
                best_z_long = z_th

    # Sweep Short
    for z_th in thresholds:
        T = len(Z_comp_train)
        pos = np.zeros(T, dtype=np.float64)
        for t in range(T):
            if Z_comp_train[t] < -z_th:
                pos[t] = -1.0

        pos_prev = 0.0
        r_sum = 0.0
        sq_sum = 0.0
        n_active = 0
        for t in range(T):
            p = pos[t]
            if p < 0:
                n_active += 1
            r = p * trade_ret_train[t] - np.abs(p) * fee_bps * 2.0
            r_sum += r
            sq_sum += r * r
            pos_prev = p

        act_pct = n_active / T * 100.0
        if act_pct >= 3.0 and T > 0:
            m = r_sum / T
            v = (sq_sum / T) - m * m
            s = np.sqrt(np.maximum(1e-12, v))
            sharpe = (m / s) * np.sqrt(252.0) if s > 1e-12 else 0.0
            if sharpe > best_sharpe_short:
                best_sharpe_short = sharpe
                best_z_short = z_th

    # Add buffer
    prod_z_long = round(best_z_long + 0.10, 2)
    prod_z_short = round(best_z_short + 0.10, 2)
    return prod_z_long, prod_z_short


def generate_simplex_grid(step: float = 0.05):
    grid = []
    steps = int(round(1.0 / step))
    for i in range(steps + 1):
        for j in range(steps + 1 - i):
            k = steps - i - j
            w1 = round(i * step, 2)
            w2 = round(j * step, 2)
            w3 = round(k * step, 2)
            if abs(w1 + w2 + w3 - 1.0) < 1e-5:
                grid.append((w1, w2, w3))
    return grid


def main():
    t0 = time.time()
    print("================================================================================")
    print("      NUMBA-ACCELERATED MULTI-METRIC SCORE WEIGHT GRID SEARCH                    ")
    print("================================================================================")

    grid = generate_simplex_grid(step=0.05)
    print(f"Dense Simplex Weight Grid Size: {len(grid)} candidate tuples (step=0.05)")

    baseline_w = (0.40, 0.35, 0.25)
    results_by_etf = {}

    for etf in ETFS:
        print(f"\n---> Precomputing expanding metrics for {etf}...")
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue

        df = load_etf_dataset(etf)
        trade_ret = df["trade_return"].values.astype(np.float64)
        X_raw, signs, _ = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        # Precompute expanding metric matrices once!
        Z_signed, r_ic_mat, r_ir_mat, r_mono_mat = fast_compute_expanding_ranks(
            Z_std, signs, trade_ret, burn_in=burn_in
        )

        T, N = Z_signed.shape
        w_min = 0.2 / N
        w_max = 1.8 / N

        t_start_ts = pd.Timestamp(START_DATE)
        train_idx = np.where(df["date"] < t_start_ts)[0]
        oos_idx = np.where(df["date"] >= t_start_ts)[0]

        trade_ret_train = trade_ret[train_idx]
        trade_ret_oos = trade_ret[oos_idx]
        Z_signed_train = Z_signed[train_idx]
        Z_signed_oos = Z_signed[oos_idx]

        grid_evals = []
        for w in grid:
            w1, w2, w3 = w
            Score_mat = w1 * r_ic_mat + w2 * r_ir_mat + w3 * r_mono_mat
            Score_ema = fast_ema_numba(Score_mat, span=EMA_SPAN)

            Z_comp = fast_rank_weights_numba(Z_signed, Score_ema, w_min, w_max)

            Z_comp_train = Z_comp[train_idx]
            Z_comp_oos = Z_comp[oos_idx]

            z_long, z_short = fast_sweep_thresholds(Z_comp_train, trade_ret_train, fee_bps=FEE_BPS)

            is_sharpe, is_pnl, is_win, is_dd, _ = fast_eval_signal(
                Z_comp_train, trade_ret_train, z_long, z_short, fee_bps=FEE_BPS
            )
            oos_sharpe, oos_pnl, oos_win, oos_dd, oos_trades = fast_eval_signal(
                Z_comp_oos, trade_ret_oos, z_long, z_short, fee_bps=FEE_BPS
            )

            grid_evals.append({
                "weights": w,
                "is_sharpe": is_sharpe,
                "is_pnl": is_pnl,
                "oos_sharpe": oos_sharpe,
                "oos_pnl": oos_pnl,
                "oos_win_rate": oos_win,
                "oos_max_dd": oos_dd,
                "oos_trades": oos_trades,
            })

        # Adaptive Inverse-Variance Metric Run
        # Compute std of metric ranks across past time up to t-1
        std_ric = np.std(r_ic_mat, axis=1)  # cross-sectional std
        inv_v_ic = 1.0 / (np.var(r_ic_mat, axis=0) + 1e-6)
        inv_v_ir = 1.0 / (np.var(r_ir_mat, axis=0) + 1e-6)
        inv_v_mono = 1.0 / (np.var(r_mono_mat, axis=0) + 1e-6)
        tot_inv = inv_v_ic + inv_v_ir + inv_v_mono
        
        w_ic_ad = np.mean(inv_v_ic / tot_inv)
        w_ir_ad = np.mean(inv_v_ir / tot_inv)
        w_mono_ad = np.mean(inv_v_mono / tot_inv)
        
        Score_mat_ad = w_ic_ad * r_ic_mat + w_ir_ad * r_ir_mat + w_mono_ad * r_mono_mat
        Score_ema_ad = fast_ema_numba(Score_mat_ad, span=EMA_SPAN)
        Z_comp_ad = fast_rank_weights_numba(Z_signed, Score_ema_ad, w_min, w_max)
        
        z_l_ad, z_s_ad = fast_sweep_thresholds(Z_comp_ad[train_idx], trade_ret_train, fee_bps=FEE_BPS)
        is_s_ad, is_p_ad, _, _, _ = fast_eval_signal(Z_comp_ad[train_idx], trade_ret_train, z_l_ad, z_s_ad, FEE_BPS)
        oos_s_ad, oos_p_ad, oos_w_ad, oos_dd_ad, oos_tr_ad = fast_eval_signal(Z_comp_ad[oos_idx], trade_ret_oos, z_l_ad, z_s_ad, FEE_BPS)

        adaptive_res = {
            "weights": (round(w_ic_ad, 2), round(w_ir_ad, 2), round(w_mono_ad, 2)),
            "is_sharpe": is_s_ad,
            "is_pnl": is_p_ad,
            "oos_sharpe": oos_s_ad,
            "oos_pnl": oos_p_ad,
            "oos_win_rate": oos_w_ad,
            "oos_max_dd": oos_dd_ad,
            "oos_trades": oos_tr_ad
        }

        results_by_etf[etf] = {
            "grid": grid_evals,
            "adaptive": adaptive_res
        }

    print(f"\nGrid search completed in {time.time() - t0:.2f} seconds!")

    print("\n" + "=" * 105)
    print("                              EMPIRICAL GRID SEARCH RESULTS                               ")
    print("=" * 105)

    for etf in ETFS:
        if etf not in results_by_etf:
            continue
        grid_res = results_by_etf[etf]["grid"]
        adaptive_res = results_by_etf[etf]["adaptive"]

        base = next(r for r in grid_res if r["weights"] == baseline_w)
        is_opt = max(grid_res, key=lambda x: x["is_sharpe"])
        pure_ic = next(r for r in grid_res if r["weights"] == (1.0, 0.0, 0.0))

        print(f"\n>>> ETF: {etf}")
        print(f"{'Configuration':<32} | {'Weights (IC,IR,Mono)':<20} | {'IS Sharpe':<10} | {'OOS Sharpe':<10} | {'OOS PnL':<9} | {'OOS Win%':<8}")
        print("-" * 102)
        print(f"{'Baseline (Default)':<32} | {str(base['weights']):<20} | {base['is_sharpe']:10.3f} | {base['oos_sharpe']:10.3f} | {base['oos_pnl']:+9.4f} | {base['oos_win_rate']:7.1f}%")
        print(f"{'IS-Optimal (Train Tuned)':<32} | {str(is_opt['weights']):<20} | {is_opt['is_sharpe']:10.3f} | {is_opt['oos_sharpe']:10.3f} | {is_opt['oos_pnl']:+9.4f} | {is_opt['oos_win_rate']:7.1f}%")
        print(f"{'Pure Dynamic IC':<32} | {str(pure_ic['weights']):<20} | {pure_ic['is_sharpe']:10.3f} | {pure_ic['oos_sharpe']:10.3f} | {pure_ic['oos_pnl']:+9.4f} | {pure_ic['oos_win_rate']:7.1f}%")
        if adaptive_res:
            print(f"{'Adaptive Inverse-Variance':<32} | {str(adaptive_res['weights']):<20} | {adaptive_res['is_sharpe']:10.3f} | {adaptive_res['oos_sharpe']:10.3f} | {adaptive_res['oos_pnl']:+9.4f} | {adaptive_res['oos_win_rate']:7.1f}%")

    # Pooled Universal Optimization Across All ETFs
    print("\n" + "=" * 105)
    print("                    UNIVERSAL POOLED IS-WEIGHT OPTIMIZATION                     ")
    print("=" * 105)

    pooled_scores = {}
    for w in grid:
        avg_is_sharpe = np.mean([
            next(r for r in results_by_etf[etf]["grid"] if r["weights"] == w)["is_sharpe"]
            for etf in ETFS if etf in results_by_etf
        ])
        pooled_scores[w] = avg_is_sharpe

    best_univ_w = max(pooled_scores, key=pooled_scores.get)
    print(f"Universal In-Sample Optimal Weights (pooled across all ETFs): {best_univ_w} (Mean IS Sharpe = {pooled_scores[best_univ_w]:.3f})")

    print("\nUniversal Weight OOS Performance:")
    print(f"{'ETF':<12} | {'Weights':<20} | {'IS Sharpe':<10} | {'OOS Sharpe':<10} | {'OOS PnL':<9} | {'OOS Win%':<8}")
    print("-" * 80)
    for etf in ETFS:
        if etf in results_by_etf:
            univ_res = next(r for r in results_by_etf[etf]["grid"] if r["weights"] == best_univ_w)
            print(f"{etf:<12} | {str(best_univ_w):<20} | {univ_res['is_sharpe']:10.3f} | {univ_res['oos_sharpe']:10.3f} | {univ_res['oos_pnl']:+9.4f} | {univ_res['oos_win_rate']:7.1f}%")

if __name__ == "__main__":
    main()
