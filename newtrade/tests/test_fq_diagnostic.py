#!/usr/bin/env python3
"""
Phase 0 — Persistence Diagnostic (go/no-go) for the FQ Score system.

Questions:
  1. Do factor metrics PERSIST? Cross-sectional rank autocorrelation of each
     component at lags 21 / 63 / 126 days (monthly snapshots).
  2. Do factor metrics PREDICT? Per-component raw meta-IC:
     Spearman(component at t, forward full-sample Spearman IC over [t, t+63]).

GO criterion: 63d rank persistence > 0.15 for at least one component AND that
component has positive mean meta-IC. Otherwise: stop, redesign toward
faster-decay reweighting.

Usage:
    python newtrade/tests/test_fq_diagnostic.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, rolling_tail_ic_numba, rolling_factor_risk_numba)
from factor_quality import compute_fq_components, WINDOW

AVAILABLE_ETFS = ["300ETF", "500ETF", "159915ETF"]
LAGS = [21, 63, 126]
SNAPSHOT_STEP = 21          # monthly snapshots
FWD_HORIZON = 63            # 3 months
START_YEAR = 2016

COMPONENTS = ["tail_ic", "sortino", "ic_cv", "recency", "half_ratio", "mono"]


def forward_ic_matrix(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray,
                      horizon: int = FWD_HORIZON) -> np.ndarray:
    """fwd_ic[t, j] = Spearman(z_signed[j] over [t, t+horizon-1], returns over same span).
    Vectorized: rank both axes, then Pearson-along-axis."""
    T, N = Z_std.shape
    out = np.full((T, N), np.nan, dtype=np.float64)
    Z_signed = Z_std * signs
    for t in range(0, T - horizon):
        y = trade_returns[t:t + horizon]
        if np.std(y) < 1e-12:
            continue
        X = Z_signed[t:t + horizon]
        col_std = X.std(axis=0)
        valid = col_std > 1e-12
        if valid.sum() < 10:
            continue
        ry = rankdata(y)
        ry = ry - ry.mean()
        rx = rankdata(X[:, valid], axis=0)
        rx = rx - rx.mean(axis=0, keepdims=True)
        denom = np.sqrt((rx ** 2).sum(axis=0) * (ry ** 2).sum())
        corr = (rx * ry[:, None]).sum(axis=0) / np.maximum(denom, 1e-12)
        out[t, valid] = corr
    return out


def main():
    print("=" * 100)
    print(f"PHASE 0 — FQ PERSISTENCE DIAGNOSTIC (lags={LAGS}, fwd={FWD_HORIZON}d, snapshots every {SNAPSHOT_STEP}d from {START_YEAR})")
    print("=" * 100)

    all_rows = []
    go_pass = False

    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            print(f"  [{etf}] SKIP (pool < 10)")
            continue
        df = load_etf_dataset(etf)
        trade_ret = (df["trade_return"].values.astype(np.float64)
                     if "trade_return" in df.columns
                     else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        print(f"\n[{etf}] N={len(pool)}, T={len(df)} — computing components...")
        comps = compute_fq_components(Z_std, signs, trade_ret, window=WINDOW, burn_in=burn_in)
        fwd = forward_ic_matrix(Z_std, signs, trade_ret)

        dates = df["date"]
        t_start = int(np.searchsorted(dates.values, np.datetime64(f"{START_YEAR}-01-01")))
        t_start = max(t_start, WINDOW + 10)
        snapshots = list(range(t_start, len(df) - max(LAGS) - 1, SNAPSHOT_STEP))
        print(f"    snapshots: {len(snapshots)} ({dates.iloc[snapshots[0]].date()} .. {dates.iloc[snapshots[-1]].date()})")

        # Rank matrices per component (for persistence)
        rank_mats = {}
        for name in COMPONENTS:
            m = comps[name]
            rm = np.zeros_like(m)
            for t in snapshots:
                rm[t] = rankdata(m[t])
            rank_mats[name] = rm

        for name in COMPONENTS:
            persist = {lag: [] for lag in LAGS}
            meta_ics = []
            for t in snapshots:
                r_t = rank_mats[name][t]
                # Persistence
                for lag in LAGS:
                    if t + lag < len(df):
                        r_fwd = rank_mats[name][t + lag] if rank_mats[name][t + lag].sum() > 0 else rankdata(comps[name][t + lag])
                        c = np.corrcoef(r_t, rankdata(comps[name][t + lag]))[0, 1]
                        if np.isfinite(c):
                            persist[lag].append(c)
                # Raw meta-IC vs forward IC
                f = fwd[t]
                ok = np.isfinite(f)
                if ok.sum() >= 10:
                    c, _ = spearmanr(comps[name][t][ok], f[ok])
                    if np.isfinite(c):
                        meta_ics.append(c)
                        all_rows.append({"ETF": etf, "Component": name,
                                         "Snapshot": str(dates.iloc[t].date()),
                                         "MetaIC": c})
            means = {lag: float(np.mean(v)) if v else np.nan for lag, v in persist.items()}
            m_meta = float(np.mean(meta_ics)) if meta_ics else np.nan
            print(f"    {name:<12} persist 21d={means[21]:+.3f}  63d={means[63]:+.3f}  126d={means[126]:+.3f} | meta-IC={m_meta:+.4f} (n={len(meta_ics)})")
            if np.isfinite(means[63]) and means[63] > 0.15 and np.isfinite(m_meta) and m_meta > 0:
                go_pass = True

    pd.DataFrame(all_rows).to_csv(HERE / "fq_diagnostic_results.csv", index=False)
    print(f"\nSaved snapshot-level meta-IC to {HERE / 'fq_diagnostic_results.csv'}")

    # Aggregate verdict
    df_all = pd.DataFrame(all_rows)
    if not df_all.empty:
        agg = df_all.groupby("Component")["MetaIC"].agg(["mean", "std", "count"])
        agg["tstat"] = agg["mean"] / (agg["std"] / np.sqrt(agg["count"]))
        print("\n" + "=" * 100)
        print("AGGREGATE meta-IC (pooled across ETFs & snapshots)")
        print("=" * 100)
        print(agg.round(4).to_string())

    print("\n" + "=" * 100)
    if go_pass:
        print("VERDICT: GO — at least one component shows 63d persistence > 0.15 with positive meta-IC.")
        print("Proceed to Phase 2 (test_fq_validation.py).")
    else:
        print("VERDICT: NO-GO — no component shows 63d persistence > 0.15 WITH positive meta-IC.")
        print("Redesign toward faster-decay reweighting (shorter horizons).")
    print("=" * 100)


if __name__ == "__main__":
    main()
