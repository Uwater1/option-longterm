#!/usr/bin/env python3
"""Test: Does 500ETF improve with fewer features? (EW, fixed threshold)"""
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import load_admitted_pool, load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba
from strategy import generate_positions, simulate_etf_spot

ETFS = ["500ETF", "159915ETF", "300ETF"]
Z_TH = 0.8
BURN_IN = 252

for etf in ETFS:
    pool = load_admitted_pool(etf, side="single", min_features=10)
    if not pool or len(pool) < 10:
        continue
    pool_sorted = sorted(pool, key=lambda p: -abs(p["deflated_ic"]))
    df = load_etf_dataset(etf)
    full_trade_ret = df["trade_return"].values.astype(np.float64) if "trade_return" in df.columns else df["close"].pct_change().fillna(0).values
    dates = df["date"]
    tr_mask = (dates < pd.Timestamp("2022-01-01")).values
    oos_mask = ~tr_mask

    print(f"\n{etf} — EW feature-count sensitivity (Z_th={Z_TH}, binary L+S, 8bps)")
    print(f"  {'N':<5} {'Full':<8} {'Train':<8} {'OOS':<8} {'Trades':<7} {'WR%':<7} | Per-year (2019-2026)")
    print(f"  {'─'*5} {'─'*8} {'─'*8} {'─'*8} {'─'*7} {'─'*7} | {'─'*50}")

    counts = [5, 8, 10, 12, 15, 20, len(pool_sorted)] if len(pool_sorted) > 15 else [5, 8, 10, len(pool_sorted)]
    counts = sorted(set(c for c in counts if c <= len(pool_sorted)))

    for n in counts:
        sub_pool = pool_sorted[:n]
        X_raw, signs, fn = build_pool_feature_matrix(df, sub_pool)
        Z_std = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
        Z_comp = np.mean(Z_std * signs, axis=1)
        pos = generate_positions(Z_comp, z_th=Z_TH, z_th_short=Z_TH, mode="binary", long_only=False)
        net_ret, _, _ = simulate_etf_spot(full_trade_ret, pos, fee_bps=0.0008)

        s_full = np.mean(net_ret[BURN_IN:]) / np.std(net_ret[BURN_IN:]) * np.sqrt(252)
        tr_ret = net_ret[tr_mask]
        s_tr = np.mean(tr_ret[BURN_IN:]) / np.std(tr_ret[BURN_IN:]) * np.sqrt(252) if np.std(tr_ret[BURN_IN:]) > 1e-12 else 0
        oos_ret = net_ret[oos_mask]
        s_oos = np.mean(oos_ret) / np.std(oos_ret) * np.sqrt(252) if np.std(oos_ret) > 1e-12 else 0
        nt = int((np.abs(pos) > 1e-5).sum())
        wr = (net_ret[np.abs(pos) > 1e-5] > 0).mean() * 100

        # Per-year 2019+
        yr_df = pd.DataFrame({"ret": net_ret, "date": dates})
        yr_df["year"] = yr_df["date"].dt.year
        yr_str = ""
        for y in range(2019, 2027):
            grp = yr_df[yr_df["year"] == y]["ret"]
            if len(grp) < 20:
                continue
            sr = grp.mean() / grp.std() * np.sqrt(252) if grp.std() > 1e-12 else 0
            yr_str += f"{y}:{sr:+.1f} "

        print(f"  {n:<5} {s_full:<8.3f} {s_tr:<8.3f} {s_oos:<8.3f} {nt:<7} {wr:<7.1f} | {yr_str}")
