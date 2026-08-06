#!/usr/bin/env python3
"""
Tests for Part A deliverables (newtrade/data/qmt_selection_{ETF}.json).

1. Selection validity: exactly 10 features, signs match source pools, no
   duplicates, ONC cluster cap (<=2) and corr cap (<=0.7) hold on the
   train-window z-scores.
2. No lookahead: thresholds are reproducible from pre-2023 rows only.
3. Reproducibility (--slow): full greedy rerun reproduces the committed
   selection (deterministic tie-breaking).

Run:  python newtrade/tests/test_qmt_selection.py [--slow]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NEWTRADE = HERE.parent
REPO_ROOT = NEWTRADE.parent
sys.path.insert(0, str(NEWTRADE))

from utils import (  # noqa: E402
    load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba,
    load_cluster_assignments, REPO_ROOT as _RR,
)
from strategy import (  # noqa: E402
    sweep_optimal_threshold, compute_production_threshold,
)

ETFS = ["500ETF", "159915ETF"]
DATA_DIR = NEWTRADE / "data"
TRAIN_END = pd.Timestamp("2023-01-01")
POOL_SUFFIXES = ["", "_p2015_2023", "_p2016_2024", "_p2017_2025", "_p2018_2026"]


def load_selection(etf: str) -> dict:
    path = DATA_DIR / f"qmt_selection_{etf}.json"
    assert path.exists(), f"missing {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def source_pools(etf: str) -> dict:
    """feature_name -> sign across all source pools."""
    out = {}
    for sfx in POOL_SUFFIXES:
        p = _RR / "day-model-new" / "data" / f"selected_pool_{etf}_single{sfx}.json"
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            for item in json.load(f):
                out.setdefault(item["feature_name"], set()).add(int(item.get("sign", 1)))
    return out


def test_validity(etf: str):
    sel = load_selection(etf)
    feats = sel["features"]
    assert len(feats) == 10, f"{etf}: expected 10 features, got {len(feats)}"

    names = [f["feature_name"] for f in feats]
    assert len(set(names)) == 10, f"{etf}: duplicate features"

    # signs must match every source pool the feature appears in
    pools = source_pools(etf)
    for f in feats:
        n = f["feature_name"]
        assert n in pools, f"{etf}: {n} not found in any source pool"
        assert f["sign"] in pools[n], f"{etf}: {n} sign {f['sign']} conflicts with pools {pools[n]}"

    # weights equal
    ws = [f["weight"] for f in feats]
    assert all(abs(w - 0.1) < 1e-9 for w in ws), f"{etf}: weights not equal 0.1"

    # cluster + corr caps on train-window z-scores
    df = load_etf_dataset(etf)
    X_raw, signs, fnames = build_pool_feature_matrix(df, feats)
    Z = expanding_zscore_numba(X_raw, burn_in=252, clip=3.0)
    train_mask = (df["date"] < TRAIN_END).values
    Zt = Z[train_mask]

    clusters = load_cluster_assignments(etf, side="single", suffix="") or {}
    counts = {}
    for n in names:
        cid = clusters.get(n)
        if cid is not None:
            counts[cid] = counts.get(cid, 0) + 1
    assert all(c <= 2 for c in counts.values()), f"{etf}: cluster cap violated: {counts}"

    corr = np.corrcoef(Zt.T)
    off = corr[~np.eye(len(names), dtype=bool)]
    assert np.abs(off).max() <= 0.70 + 1e-9, f"{etf}: corr cap violated max={np.abs(off).max():.3f}"

    print(f"  [PASS] {etf} validity: 10 unique features, signs consistent, "
          f"cluster cap ok, max|corr|={np.abs(off).max():.3f}")
    return sel, df, feats, Z, train_mask


def test_no_lookahead(etf: str, sel: dict, df: pd.DataFrame, feats: list,
                      Z: np.ndarray, train_mask: np.ndarray):
    """Recompute thresholds from pre-2023 rows only and compare."""
    signs = np.array([f["sign"] for f in feats], dtype=np.float64)
    Zc = (Z * signs[None, :]).mean(axis=1)
    trade_returns = df["trade_return"].values.astype(np.float64)

    sweep = sweep_optimal_threshold(
        Zc[train_mask], trade_returns[train_mask], mode="binary",
        long_only=False, fee_bps=0.0008, z_range=(0.5, 1.5), z_step=0.1)
    zl, zs = compute_production_threshold(sweep, z_buffer=0.10, z_short_buffer=0.20)

    th = sel["thresholds"]
    assert abs(zl - th["z_th_long"]) < 1e-9, f"{etf}: z_th_long {zl} != {th['z_th_long']}"
    assert abs(zs - th["z_th_short"]) < 1e-9, f"{etf}: z_th_short {zs} != {th['z_th_short']}"
    print(f"  [PASS] {etf} no-lookahead: thresholds reproducible from pre-2023 "
          f"(L={zl}, S={zs})")


def test_reproducibility(etf: str):
    """Full greedy rerun must reproduce the committed selection."""
    import tempfile
    import research_qmt_selection as R

    sel_ref = load_selection(etf)
    with tempfile.TemporaryDirectory() as tmp:
        out = R.run_etf(etf, Path(tmp))
    names_ref = [f["feature_name"] for f in sel_ref["features"]]
    names_new = [f["feature_name"] for f in out["features"]]
    assert names_ref == names_new, f"{etf}: rerun diverged\nref={names_ref}\nnew={names_new}"
    assert out["thresholds"] == sel_ref["thresholds"], f"{etf}: thresholds diverged"
    print(f"  [PASS] {etf} reproducibility: greedy rerun identical")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slow", action="store_true",
                        help="also run the full greedy reproducibility check")
    args = parser.parse_args()

    for etf in ETFS:
        print(f"== test_validity {etf} ==")
        sel, df, feats, Z, train_mask = test_validity(etf)
        print(f"== test_no_lookahead {etf} ==")
        test_no_lookahead(etf, sel, df, feats, Z, train_mask)

    if args.slow:
        for etf in ETFS:
            print(f"== test_reproducibility {etf} ==")
            test_reproducibility(etf)

    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()
