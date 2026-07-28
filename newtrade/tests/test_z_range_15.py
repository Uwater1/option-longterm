#!/usr/bin/env python3
"""
Test z_range=(0.5, 1.5) with min_active_pct=8.0% across all ETFs.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEWTRADE_DIR = HERE.parent
if str(NEWTRADE_DIR) not in sys.path:
    sys.path.insert(0, str(NEWTRADE_DIR))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba, expanding_factor_ic_numba
from weighting import compute_rank_w
from strategy import generate_positions, simulate_etf_spot, calculate_metrics

FEE_BPS = 0.0008
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"

def test_z_range_15(etf: str, min_active_pct: float = 8.0):
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool:
        return None

    df = load_etf_dataset(etf)
    trade_ret = df["trade_return"].values.astype(np.float64)
    X_raw, signs, _ = build_pool_feature_matrix(df, pool)
    burn_in = 252 if len(df) > 500 else 100
    Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

    exp_ic = expanding_factor_ic_numba(Z_std, signs, trade_ret, burn_in=burn_in)
    Z_composite = compute_rank_w(Z_std, signs, pool=pool, w_min_ratio=0.2, w_max_ratio=1.8, mapping_shape="linear", ic_ema_span=30, expanding_ic=exp_ic)

    t_start_ts = pd.Timestamp(START_DATE)
    train_mask = df["date"] < t_start_ts
    Z_train = Z_composite[train_mask.values]
    ret_train = trade_ret[train_mask.values]

    thresholds = np.arange(0.5, 1.55, 0.1)
    best_sharpe = -np.inf
    opt_l, opt_s = 0.5, 0.5

    for zl in thresholds:
        for zs in thresholds:
            pos = generate_positions(Z_train, z_th=zl, z_th_short=zs, mode="binary", long_only=False)
            n_active = int((np.abs(pos) > 1e-5).sum())
            active_pct = (n_active / len(pos) * 100.0) if len(pos) > 0 else 0.0
            if active_pct < min_active_pct:
                continue

            net_ret, _, _ = simulate_etf_spot(ret_train, pos, fee_bps=FEE_BPS)
            std_net = np.std(net_ret)
            sharpe = float((np.mean(net_ret) / std_net) * np.sqrt(252)) if std_net > 1e-12 else 0.0
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                opt_l, opt_s = float(zl), float(zs)

    z_prod_l = round(opt_l + 0.1, 2)
    z_prod_s = round(opt_s + 0.1, 2)

    positions = generate_positions(Z_composite, z_th=z_prod_l, z_th_short=z_prod_s, mode="binary", long_only=False)

    t_start = pd.Timestamp(START_DATE)
    t_end = pd.Timestamp(END_DATE)
    mask = (df["date"] >= t_start) & (df["date"] < t_end)
    df_oos = df[mask].reset_index(drop=True)
    pos_oos = positions[mask]
    ret_oos = trade_ret[mask.values]

    net_ret, raw_ret, _ = simulate_etf_spot(ret_oos, pos_oos, fee_bps=FEE_BPS)
    m = calculate_metrics(net_ret, raw_ret, pos_oos, dates=df_oos["date"])

    return {
        "etf": etf,
        "opt_train_l": round(opt_l, 2),
        "opt_train_s": round(opt_s, 2),
        "z_prod_l": z_prod_l,
        "z_prod_s": z_prod_s,
        "trades": m["n_trades"],
        "cost_sharpe": m["cost_sharpe"],
        "raw_sharpe": m["raw_sharpe"],
        "pnl": m["total_pnl"],
        "max_dd": m["max_drawdown"],
    }

def main():
    print("================================================================================")
    print("TESTING Z_RANGE (0.5, 1.5) WITH MIN_ACTIVE_PCT = 8.0%")
    print("================================================================================")
    for etf in ["300ETF", "500ETF", "159915ETF"]:
        res = test_z_range_15(etf, min_active_pct=8.0)
        if res:
            print(f"  {etf:<10} | Train Opt: L:{res['opt_train_l']}/S:{res['opt_train_s']} -> Prod: L:{res['z_prod_l']}/S:{res['z_prod_s']} | Trades: {res['trades']:<3} | Cost Sharpe: {res['cost_sharpe']:.3f} | Raw Sharpe: {res['raw_sharpe']:.3f} | PnL: {res['pnl']:+.4f} | MaxDD: {res['max_dd']:.4f}")

if __name__ == "__main__":
    main()
