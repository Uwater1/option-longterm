#!/usr/bin/env python3
"""
FQ Comprehensive Sweep — maximize Top-10 TP' rate (target: >80% = 8+/10).

Judged by the scientific harness: meta-IC @63d + Top-10 TP'/FP' hit rates
(TP' = fwdIC>0 & fwdSortino>0), monthly snapshots from 2017.

Sweep groups:
  A. Single components (extended library incl. day-model-new ports):
     tailIC {240,480,960}, Sortino {240,480}, mono, -ic_cv, tail momentum,
     loo_min_ic (jackknife worst case), regime_sign (vol-regime consistency),
     -n_neg_blocks
  B. Hard-gate variants on tailIC_480 (ported gates: null-floor/deflated-IC,
     n-negative-periods, jackknife sign stability, regime uniformity)
  C. Rank blends x best gates
  Stage 2: block-shuffle null test on top-3 arms by TP' rate.

Usage:
    python newtrade/tests/test_fq_sweep.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from utils import (load_admitted_pool, load_etf_dataset, build_pool_feature_matrix,
                   expanding_zscore_numba, rolling_tail_ic_numba,
                   rolling_factor_risk_numba, _fast_rankdata_norm)
from factor_quality import (compute_fq_components, rolling_daily_ic_matrix,
                            rolling_block_stats_numba, rolling_regime_sign_numba, WINDOW)
from test_fq_diagnostic import forward_ic_matrix, AVAILABLE_ETFS, SNAPSHOT_STEP
from test_fq_validation import forward_sortino_matrix, spearman_row

START_YEAR = 2017
PRIMARY_H = 63
TOP_K = 10
NULL_SIMS = 300


def build_component_library(Z_std, signs, trade_ret, burn_in):
    """All score candidate matrices (T, N) + gate booleans."""
    lib = {}
    comps = compute_fq_components(Z_std, signs, trade_ret, window=WINDOW, burn_in=burn_in)
    lib["tailIC480"] = comps["tail_ic"]
    lib["sortino480"] = comps["sortino"]
    lib["mono"] = comps["mono"]
    lib["neg_ic_cv"] = -comps["ic_cv"]

    lib["tailIC240"] = rolling_tail_ic_numba(Z_std, signs, trade_ret, window=240,
                                             tail_pct=0.10, burn_in=burn_in)
    lib["tailIC960"] = rolling_tail_ic_numba(Z_std, signs, trade_ret, window=960,
                                             tail_pct=0.10, burn_in=burn_in)
    _, sort240 = rolling_factor_risk_numba(Z_std, signs, trade_ret, window=240, burn_in=burn_in)
    lib["sortino240"] = sort240
    lib["tailMom"] = lib["tailIC240"] - lib["tailIC480"]

    daily_ic = rolling_daily_ic_matrix(Z_std, signs, trade_ret)
    n_neg, loo_min = rolling_block_stats_numba(daily_ic, window=WINDOW, n_blocks=4,
                                               burn_in=burn_in)
    lib["neg_nNegBlocks"] = -n_neg
    lib["looMinIC"] = loo_min
    gates = {"n_neg_blocks": n_neg, "loo_min": loo_min}

    vol20 = pd.Series(trade_ret).rolling(20).std().bfill().values
    regime_sign = rolling_regime_sign_numba(daily_ic, vol20, window=WINDOW, burn_in=burn_in)
    lib["regimeSign"] = regime_sign
    gates["regime_sign"] = regime_sign
    return lib, gates, comps


def evaluate_arm(arm_name, score_mat, fwd63, fwd_sort, snapshots, out_rows, etf, dates):
    """Meta-IC + top-K tiers for one arm; appends to out_rows."""
    mis, tps, fps, pool_tps, pool_ns, n_pass = [], [], [], [], [], []
    for t in snapshots:
        mi = spearman_row(score_mat[t], fwd63[t])
        if np.isfinite(mi):
            mis.append(mi)
        f63, fs = fwd63[t], fwd_sort[t]
        ok = np.isfinite(f63) & np.isfinite(fs)
        if ok.sum() >= TOP_K + 1:
            sc = score_mat[t].copy()
            sc[~ok] = -np.inf
            top = np.argsort(sc)[::-1][:TOP_K]
            tps.append(int(((f63[top] > 0) & (fs[top] > 0)).sum()))
            fps.append(int((f63[top] <= 0).sum()))
            pool_tps.append(int(((f63[ok] > 0) & (fs[ok] > 0)).sum()))
            pool_ns.append(int(ok.sum()))
            n_pass.append(int((sc > 0).sum()) if np.isfinite(sc).all() else TOP_K)
    if not mis:
        return
    m = float(np.mean(mis))
    sd = float(np.std(mis))
    out_rows.append({
        "ETF": etf, "Arm": arm_name,
        "MetaIC": m, "Tstat": m / (sd / np.sqrt(len(mis))) if sd > 0 else 0.0,
        "AvgTP": float(np.mean(tps)), "AvgFP": float(np.mean(fps)),
        "PoolTP_per10": float(np.sum(pool_tps) / np.sum(pool_ns) * TOP_K),
        "NSnap": len(mis),
    })


def gated_tailic(lib, gates, gate_flags, etf_name):
    """tailIC480 rank score with cumulative hard gates; returns (score_mat, label)."""
    score = np.zeros_like(lib["tailIC480"])
    T = score.shape[0]
    gate = np.ones((T, lib["tailIC480"].shape[1]), dtype=bool)
    labels = []
    for flag in gate_flags:
        if flag == "gt0":
            gate &= lib["tailIC480"] > 0; labels.append("tailIC>0")
        elif flag == "sort0":
            gate &= lib["sortino480"] > 0; labels.append("sort>0")
        elif flag == "mono52":
            gate &= lib["mono"] >= 0.52; labels.append("mono>=.52")
        elif flag == "nneg0":
            gate &= gates["n_neg_blocks"] == 0; labels.append("nneg=0")
        elif flag == "loo0":
            gate &= gates["loo_min"] > 0; labels.append("loo>0")
        elif flag == "reg2":
            gate &= gates["regime_sign"] == 2; labels.append("reg=2")
        elif flag == "floor":
            floor = np.median(np.abs(lib["tailIC480"]), axis=1, keepdims=True)
            gate &= lib["tailIC480"] > floor; labels.append("IC>floor")
    for t in range(T):
        r = _fast_rankdata_norm(lib["tailIC480"][t])
        r[~gate[t]] = 0.0
        score[t] = r
    return score, "+".join(labels)


def blend_rank(lib, names, gate=None):
    """Equal-weight rank blend of components; optional boolean gate (score->0)."""
    T, N = lib[names[0]].shape
    out = np.zeros((T, N), dtype=np.float64)
    for t in range(T):
        r = np.zeros(N)
        for nm in names:
            r += _fast_rankdata_norm(lib[nm][t])
        out[t] = r / len(names)
    if gate is not None:
        out[~gate] = 0.0
    return out


def block_null_test(score_mat, fwd63, snapshots, obs_mean, n_sims, rng):
    T, N = fwd63.shape
    null_means = []
    for _ in range(n_sims):
        f = fwd63.copy()
        for j in range(N):
            shift = int(rng.integers(0, max(1, T // PRIMARY_H))) * PRIMARY_H
            f[:, j] = np.roll(f[:, j], shift)
        sim = [spearman_row(score_mat[t], f[t]) for t in snapshots]
        sim = [s for s in sim if np.isfinite(s)]
        if sim:
            null_means.append(float(np.mean(sim)))
    null_means = np.array(null_means)
    p = float((null_means >= obs_mean).mean())
    return null_means.mean(), null_means.std(), p


def main():
    rng = np.random.default_rng(7)
    print("=" * 100)
    print("FQ COMPREHENSIVE SWEEP — target: Top-10 TP' > 80% (judged by meta-IC harness)")
    print("=" * 100)

    rows = []
    stage2_payload = {}

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

        print(f"\n[{etf}] N={len(pool)} — building component library...")
        lib, gates, comps = build_component_library(Z_std, signs, trade_ret, burn_in)
        fwd63 = forward_ic_matrix(Z_std, signs, trade_ret, horizon=PRIMARY_H)
        fwd_sort = forward_sortino_matrix(Z_std, signs, trade_ret, horizon=PRIMARY_H)

        dates = df["date"]
        t_start = int(np.searchsorted(dates.values, np.datetime64(f"{START_YEAR}-01-01")))
        t_start = max(t_start, 970)  # tailIC960 needs 960d history
        snapshots = list(range(t_start, len(df) - PRIMARY_H - 1, SNAPSHOT_STEP))
        print(f"    snapshots: {len(snapshots)}")

        # ── Group A: single components ──
        singles = {
            "tailIC240": lib["tailIC240"], "tailIC480": lib["tailIC480"],
            "tailIC960": lib["tailIC960"], "sortino240": lib["sortino240"],
            "sortino480": lib["sortino480"], "mono": lib["mono"],
            "neg_ic_cv": lib["neg_ic_cv"], "tailMom": lib["tailMom"],
            "looMinIC": lib["looMinIC"], "regimeSign": lib["regimeSign"],
            "neg_nNegBlocks": lib["neg_nNegBlocks"],
        }
        for nm, mat in singles.items():
            evaluate_arm(f"A_{nm}", mat, fwd63, fwd_sort, snapshots, rows, etf, dates)

        # ── Group B: gated tailIC480 ──
        gate_sets = {
            "B0_raw": [],
            "B1_gt0": ["gt0"],
            "B2_gt0_sort": ["gt0", "sort0"],
            "B3_mono52": ["gt0", "sort0", "mono52"],
            "B4_nneg0": ["gt0", "sort0", "nneg0"],
            "B5_loo0": ["gt0", "sort0", "loo0"],
            "B6_reg2": ["gt0", "sort0", "reg2"],
            "B7_floor": ["gt0", "sort0", "floor"],
            "B8_kitchen": ["gt0", "sort0", "nneg0", "floor"],
        }
        for arm, flags in gate_sets.items():
            sc, lbl = gated_tailic(lib, gates, flags, etf)
            evaluate_arm(arm, sc, fwd63, fwd_sort, snapshots, rows, etf, dates)
            stage2_payload[(etf, arm)] = sc

        # ── Group C: blends (with B2 gate = tailIC>0 & sortino>0) ──
        gate_b2 = (lib["tailIC480"] > 0) & (lib["sortino480"] > 0)
        blends = {
            "C1_tail_sort": ["tailIC480", "sortino480"],
            "C2_FQv1": ["tailIC480", "sortino480", "mono"],
            "C3_multiwin": ["tailIC240", "tailIC480", "tailIC960"],
            "C4_tail_sort_loo": ["tailIC480", "sortino480", "looMinIC"],
            "C5_tail_sort_reg": ["tailIC480", "sortino480", "regimeSign"],
            "C6_tail_sort_mom": ["tailIC480", "sortino480", "tailMom"],
        }
        for arm, names in blends.items():
            sc = blend_rank(lib, names, gate=gate_b2)
            evaluate_arm(arm, sc, fwd63, fwd_sort, snapshots, rows, etf, dates)
            stage2_payload[(etf, arm)] = sc
        # Blend under kitchen-sink gate B8
        gate_b8 = gate_b2 & (gates["n_neg_blocks"] == 0)
        floor = np.median(np.abs(lib["tailIC480"]), axis=1, keepdims=True)
        gate_b8 &= lib["tailIC480"] > floor
        sc = blend_rank(lib, ["tailIC480", "sortino480", "mono"], gate=gate_b8)
        evaluate_arm("C7_FQv1_kitchenGate", sc, fwd63, fwd_sort, snapshots, rows, etf, dates)
        stage2_payload[(etf, "C7_FQv1_kitchenGate")] = sc

    df_all = pd.DataFrame(rows)
    agg = df_all.groupby("Arm").agg(MetaIC=("MetaIC", "mean"), Tstat=("Tstat", "mean"),
                                    AvgTP=("AvgTP", "mean"), AvgFP=("AvgFP", "mean"),
                                    PoolTP=("PoolTP_per10", "mean")).round(3)
    agg["TP_lift"] = (agg["AvgTP"] - agg["PoolTP"]).round(3)
    agg = agg.sort_values(["AvgTP", "MetaIC"], ascending=False)

    print("\n" + "=" * 100)
    print("SWEEP RESULTS (mean across ETFs) — sorted by Avg TP' count in top-10")
    print("=" * 100)
    print(agg.to_string())

    # ─── Stage 2: null test on top-3 arms by AvgTP ────────────────────────────
    top_arms = agg.index[:3].tolist()
    if "B0_raw" not in top_arms:
        top_arms.append("B0_raw")
    print("\n" + "-" * 100)
    print(f"STAGE 2 — BLOCK-SHUFFLE NULL ({NULL_SIMS} sims) for top arms: {top_arms}")
    print("-" * 100)
    # rebuild snapshots per ETF for null test
    for arm in top_arms:
        obs = []
        nulls = []
        for etf in AVAILABLE_ETFS:
            if (etf, arm) not in stage2_payload:
                continue
            # recompute fwd63/snapshots quickly by re-loading (cheap enough for 3 ETFs)
            pool = load_admitted_pool(etf, side="single", min_features=10)
            df = load_etf_dataset(etf)
            trade_ret = (df["trade_return"].values.astype(np.float64)
                         if "trade_return" in df.columns
                         else df["close"].pct_change().fillna(0.0).values)
            X_raw, signs, _ = build_pool_feature_matrix(df, pool)
            burn_in = 252 if len(df) > 500 else 100
            Z_std = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
            fwd63 = forward_ic_matrix(Z_std, signs, trade_ret, horizon=PRIMARY_H)
            dates = df["date"]
            t_start = int(np.searchsorted(dates.values, np.datetime64(f"{START_YEAR}-01-01")))
            t_start = max(t_start, 970)
            snapshots = list(range(t_start, len(df) - PRIMARY_H - 1, SNAPSHOT_STEP))
            sc = stage2_payload[(etf, arm)]
            sim = [spearman_row(sc[t], fwd63[t]) for t in snapshots]
            sim = [s for s in sim if np.isfinite(s)]
            if sim:
                obs.append(float(np.mean(sim)))
                nm, ns_, p = block_null_test(sc, fwd63, snapshots, obs[-1], NULL_SIMS, rng)
                nulls.append((nm, ns_, p))
        if obs:
            o = float(np.mean(obs))
            nm_avg = float(np.mean([x[0] for x in nulls]))
            p_avg = float(np.mean([x[2] for x in nulls]))
            print(f"  {arm:<22} obs meta-IC={o:+.4f} | null={nm_avg:+.4f} | avg p={p_avg:.3f}"
                  f" {'SIGNIFICANT' if p_avg < 0.05 else 'ns'}")

    df_all.to_csv(HERE / "fq_sweep_results.csv", index=False)
    print(f"\nSaved to {HERE / 'fq_sweep_results.csv'}")
    print("\n[OK] FQ sweep complete.")


if __name__ == "__main__":
    main()
