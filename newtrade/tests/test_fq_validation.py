#!/usr/bin/env python3
"""
Phase 2 — Meta-IC Validation Harness for the FQ Score system.

Scientific judging rule: a score definition is good iff FQ(t, f) correlates
with factor f's REALIZED performance over the next 63 trading days — measured
as meta-IC at monthly snapshots, tested against a block-shuffled null.

Arms (judged ONLY by OOS meta-IC + top-K hit rate):
  (a) tailIC_480d only
  (b) Sortino_480d only
  (c) FQ v1 blend (mandatory gates: tailIC>0 & Sortino>0)
  (d) FQ v1 + extra gates (ic_cv<0.50, recency<0.80)

Outputs: mean meta-IC + t-stat + per-year table, decay profile (21/63/126d),
top-10 TP'/Median'/FP' hit rates vs pool average, block-shuffle p-values,
FP' rate comparison (FQ top-10 vs tailIC top-10).

Usage:
    python newtrade/tests/test_fq_validation.py
    python newtrade/tests/test_fq_validation.py --n-sims 200
"""

import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba)
from factor_quality import compute_fq_components, fq_from_components, WINDOW
from test_fq_diagnostic import forward_ic_matrix, AVAILABLE_ETFS, SNAPSHOT_STEP

START_YEAR = 2017
HORIZONS = [21, 63, 126]
PRIMARY_H = 63
TOP_K = 10


def forward_sortino_matrix(Z_std: np.ndarray, signs: np.ndarray, trade_returns: np.ndarray,
                           horizon: int = PRIMARY_H) -> np.ndarray:
    """fwd_sortino[t, j] = factor Sortino over [t, t+horizon-1], annualized sqrt(252)."""
    T, N = Z_std.shape
    out = np.full((T, N), np.nan, dtype=np.float64)
    Z_signed = Z_std * signs
    for t in range(0, T - horizon):
        fr = Z_signed[t:t + horizon] * trade_returns[t:t + horizon, None]
        mean_r = fr.mean(axis=0)
        neg = np.where(fr < 0.0, fr, 0.0)
        dd = np.sqrt(np.maximum((neg ** 2).mean(axis=0), 1e-18))
        out[t] = (mean_r / dd) * np.sqrt(252.0)
    return out


def spearman_row(score: np.ndarray, fwd: np.ndarray):
    """Cross-sectional Spearman ignoring NaN fwd entries."""
    ok = np.isfinite(fwd)
    if ok.sum() < 10:
        return np.nan
    s, f = score[ok], fwd[ok]
    if np.std(s) < 1e-12:
        return np.nan
    rs = rankdata(s) - rankdata(s).mean()
    rf = rankdata(f) - rankdata(f).mean()
    denom = np.sqrt((rs ** 2).sum() * (rf ** 2).sum())
    return float((rs * rf).sum() / max(denom, 1e-12))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sims", type=int, default=500, help="Block-shuffle null sims")
    args = parser.parse_args()
    rng = np.random.default_rng(42)

    print("=" * 100)
    print(f"PHASE 2 — FQ META-IC VALIDATION (snapshots monthly from {START_YEAR}, primary horizon {PRIMARY_H}d, top_k={TOP_K})")
    print("=" * 100)

    rows = []
    etf_payloads = {}

    for etf in AVAILABLE_ETFS:
        pool = load_admitted_pool(etf, side="single", min_features=10)
        if not pool:
            continue
        df = load_etf_dataset(etf)
        trade_ret = (df["trade_return"].values.astype(np.float64)
                     if "trade_return" in df.columns
                     else df["close"].pct_change().fillna(0.0).values)
        X_raw, signs, feat_names = build_pool_feature_matrix(df, pool)
        burn_in = 252 if len(df) > 500 else 100
        Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)

        print(f"\n[{etf}] N={len(pool)}, T={len(df)} — computing FQ components & forward targets...")
        comps = compute_fq_components(Z_std, signs, trade_ret, window=WINDOW, burn_in=burn_in)
        fq = fq_from_components(comps, use_extra_gates=False)
        fq_gated = fq_from_components(comps, use_extra_gates=True)

        fwd = {h: forward_ic_matrix(Z_std, signs, trade_ret, horizon=h) for h in HORIZONS}
        fwd_sort = forward_sortino_matrix(Z_std, signs, trade_ret, horizon=PRIMARY_H)

        dates = df["date"]
        t_start = int(np.searchsorted(dates.values, np.datetime64(f"{START_YEAR}-01-01")))
        t_start = max(t_start, WINDOW + 10)
        snapshots = list(range(t_start, len(df) - max(HORIZONS) - 1, SNAPSHOT_STEP))
        print(f"    snapshots: {len(snapshots)} ({dates.iloc[snapshots[0]].date()} .. {dates.iloc[snapshots[-1]].date()})")

        arms = {"tailIC_only": comps["tail_ic"], "sortino_only": comps["sortino"],
                "FQ_v1": fq, "FQ_v1_gates": fq_gated}

        for arm_name, score_mat in arms.items():
            for t in snapshots:
                year = dates.iloc[t].year
                for h in HORIZONS:
                    mi = spearman_row(score_mat[t], fwd[h][t])
                    if np.isfinite(mi):
                        rows.append({"ETF": etf, "Arm": arm_name, "Year": year,
                                     "Horizon": h, "Snapshot": str(dates.iloc[t].date()),
                                     "MetaIC": mi})
                # Top-K tiers at primary horizon
                f63, fs = fwd[PRIMARY_H][t], fwd_sort[t]
                ok = np.isfinite(f63) & np.isfinite(fs)
                if ok.sum() >= TOP_K + 1:
                    sc = score_mat[t].copy()
                    sc[~ok] = -np.inf
                    top = np.argsort(sc)[::-1][:TOP_K]
                    tp = int(((f63[top] > 0) & (fs[top] > 0)).sum())
                    fp = int((f63[top] <= 0).sum())
                    pool_tp = int(((f63[ok] > 0) & (fs[ok] > 0)).sum())
                    rows.append({"ETF": etf, "Arm": arm_name, "Year": year,
                                 "Horizon": -1,  # tier rows marker
                                 "Snapshot": str(dates.iloc[t].date()),
                                 "MetaIC": np.nan, "TopK_TP": tp, "TopK_FP": fp,
                                 "TopK_medFwdIC": float(np.median(f63[top])),
                                 "PoolTPcount": pool_tp, "PoolSize": int(ok.sum())})

        etf_payloads[etf] = {"scores": arms, "fwd63": fwd[PRIMARY_H], "snapshots": snapshots}

    df_all = pd.DataFrame(rows)
    df_mi = df_all[df_all["Horizon"] > 0]
    df_tier = df_all[df_all["Horizon"] == -1]

    # ─── 1. Meta-IC summary at primary horizon ────────────────────────────────
    print("\n" + "=" * 100)
    print(f"META-IC SUMMARY @ {PRIMARY_H}d horizon (monthly snapshots)")
    print("=" * 100)
    sub = df_mi[df_mi["Horizon"] == PRIMARY_H]
    agg = sub.groupby("Arm")["MetaIC"].agg(["mean", "std", "count"])
    agg["tstat"] = agg["mean"] / (agg["std"] / np.sqrt(agg["count"]))
    agg = agg.sort_values("mean", ascending=False)
    print(agg.round(4).to_string())

    # ─── 2. Per-year meta-IC for best arm ─────────────────────────────────────
    best_arm = agg.index[0]
    print("\n" + "-" * 100)
    print(f"PER-YEAR META-IC — {best_arm} @ {PRIMARY_H}d")
    print("-" * 100)
    yr = sub[sub["Arm"] == best_arm].groupby("Year")["MetaIC"].agg(["mean", "count"])
    print(yr.round(4).to_string())
    pct_pos = float((sub[sub["Arm"] == best_arm]["MetaIC"] > 0).mean())
    print(f"  fraction of snapshots with meta-IC > 0: {pct_pos:.1%}")

    # ─── 3. Decay profile ─────────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print(f"DECAY PROFILE — mean meta-IC by horizon ({best_arm})")
    print("-" * 100)
    dec = df_mi[df_mi["Arm"] == best_arm].groupby("Horizon")["MetaIC"].mean()
    print(dec.round(4).to_string())

    # ─── 4. Top-K hit rates ───────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print(f"TOP-{TOP_K} HIT RATES (TP' = fwdIC>0 & fwdSortino>0; FP' = fwdIC<=0)")
    print("-" * 100)
    tier_agg = df_tier.groupby("Arm").agg(
        AvgTP=("TopK_TP", "mean"), AvgFP=("TopK_FP", "mean"),
        MedFwdIC=("TopK_medFwdIC", "mean"),
        PoolTP_rate=("PoolTPcount", lambda x: x.sum()),
        PoolN=("PoolSize", "sum"),
    )
    tier_agg["PoolTP_per10"] = tier_agg["PoolTP_rate"] / tier_agg["PoolN"] * TOP_K
    tier_agg = tier_agg.sort_values("AvgTP", ascending=False)
    print(tier_agg[["AvgTP", "AvgFP", "MedFwdIC", "PoolTP_per10"]].round(3).to_string())

    # ─── 5. Block-shuffle null for best arm ───────────────────────────────────
    print("\n" + "-" * 100)
    print(f"BLOCK-SHUFFLE NULL — {best_arm} ({args.n_sims} sims, per-factor 63d-block circular shifts)")
    print("-" * 100)
    obs = float(sub[sub["Arm"] == best_arm]["MetaIC"].mean())
    null_means = []
    for s in range(args.n_sims):
        sim_mi = []
        for etf, pay in etf_payloads.items():
            fwd63 = pay["fwd63"].copy()
            T, N = fwd63.shape
            for j in range(N):
                shift = int(rng.integers(0, max(1, T // PRIMARY_H))) * PRIMARY_H
                fwd63[:, j] = np.roll(fwd63[:, j], shift)
            score_mat = pay["scores"][best_arm]
            for t in pay["snapshots"]:
                mi = spearman_row(score_mat[t], fwd63[t])
                if np.isfinite(mi):
                    sim_mi.append(mi)
        if sim_mi:
            null_means.append(float(np.mean(sim_mi)))
    null_means = np.array(null_means)
    p_val = float((null_means >= obs).mean())
    print(f"  observed mean meta-IC = {obs:+.4f}")
    print(f"  null mean = {null_means.mean():+.4f} ± {null_means.std():.4f}")
    print(f"  p-value (one-sided) = {p_val:.4f}  ->  {'SIGNIFICANT' if p_val < 0.05 else 'NOT SIGNIFICANT'}")

    # ─── 6. FP' rate: FQ top-10 vs tailIC top-10 ──────────────────────────────
    print("\n" + "-" * 100)
    print("GATE VALUE — FP' share among top-10: FQ_v1 vs tailIC_only")
    print("-" * 100)
    for arm in ["tailIC_only", "FQ_v1", "FQ_v1_gates"]:
        a = tier_agg.loc[arm]
        print(f"  {arm:<14} top-10 FP' rate = {a['AvgFP']/TOP_K:.1%}  (avg FP count {a['AvgFP']:.2f}/10)")

    df_all.to_csv(HERE / "fq_meta_ic_results.csv", index=False)
    print(f"\nSaved snapshot-level results to {HERE / 'fq_meta_ic_results.csv'}")
    print("\n[OK] Phase 2 FQ validation complete.")


if __name__ == "__main__":
    main()
