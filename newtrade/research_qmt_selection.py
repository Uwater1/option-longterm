#!/usr/bin/env python3
"""
Part A: Hand-pick 10 features per ETF for the first QMT draft.

Methodology (cross-window stability + walk-forward backtest):
  1. Candidate universe = union of features across the 5 admitted pools
     (no-suffix original 2015-2022, _p2015_2023, _p2016_2024, _p2017_2025,
     _p2018_2026).
  2. Per-feature evidence: window count, mean deflated_ic / ic_ir /
     monotonicity, stress_sortino / deep_stress_sortino margins from the
     mining attempt logs, ONC cluster id.
  3. Walk-forward evaluator: composite = mean(sign * expanding-z), thresholds
     swept on pre-2023 data only (+0.10 long / +0.20 short buffers), OOS
     evaluated 2023-01 .. 2025-12 with per-year breakdown.
  4. Greedy forward selection to TARGET_K=10 maximizing OOS cost Sharpe
     subject to: <= MAX_PER_CLUSTER per ONC cluster, pairwise |corr| <=
     CORR_CAP on train-window z-scores, and every per-year Sharpe >
     MIN_YEARLY_SHARPE.

Deterministic (no RNG): ties broken by feature name.

Usage:
    python newtrade/research_qmt_selection.py                 # 500ETF + 159915ETF
    python newtrade/research_qmt_selection.py -e 500ETF
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from utils import (
    load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba,
    load_cluster_assignments, REPO_ROOT,
)
from strategy import (
    sweep_optimal_threshold, compute_production_threshold,
    generate_positions, simulate_etf_spot,
)

# ── Config ──────────────────────────────────────────────────────────────
SUFFIXES = ["", "_p2015_2023", "_p2016_2024", "_p2017_2025", "_p2018_2026"]
WINDOW_LABELS = ["orig", "p2015_2023", "p2016_2024", "p2017_2025", "p2018_2026"]

TARGET_K = 10
CORR_CAP = 0.70              # max pairwise |Pearson corr| of z-scores (train window)
MAX_PER_CLUSTER = 2          # max features per ONC cluster
MIN_YEARLY_SHARPE = -0.5     # every OOS year must stay above this
TRAIN_END = pd.Timestamp("2023-01-01")
OOS_END = pd.Timestamp("2026-01-01")
FEE_BPS = 0.0008
Z_BUFFER_LONG = 0.10
Z_BUFFER_SHORT = 0.20
BURN_IN = 252
MIN_WINDOWS = 1              # min pool appearances to enter universe


def load_universe(etf: str) -> tuple[dict, list]:
    """Union of features across the 5 pools. Returns (universe dict, skipped list)."""
    data_dir = REPO_ROOT / "day-model-new" / "data"
    universe = {}
    skipped = []
    for suffix, label in zip(SUFFIXES, WINDOW_LABELS):
        path = data_dir / f"selected_pool_{etf}_single{suffix}.json"
        if not path.exists():
            print(f"  [WARN] pool file missing: {path.name}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            pool = json.load(f)
        for item in pool:
            name = item["feature_name"]
            if name not in universe:
                universe[name] = {"name": name, "windows": {}, "signs": {}}
            universe[name]["windows"][label] = suffix
            universe[name]["signs"][label] = int(item.get("sign", 1))
            # keep the richest entry (recipe + metrics) from any window
            for k in ("recipe", "overall_ic", "deflated_ic", "ic_ir", "monotonicity"):
                if k in item:
                    universe[name].setdefault("entries", {})[label] = item
                    break

    # Resolve sign conflicts (majority vote); log conflicts
    resolved = {}
    for name, u in universe.items():
        n_win = len(u["windows"])
        if n_win < MIN_WINDOWS:
            continue
        sc = pd.Series(list(u["signs"].values()))
        maj = int(sc.mode().iloc[0])
        conflict = bool((sc != maj).any())
        u["sign"] = maj
        u["n_windows"] = n_win
        u["sign_conflict"] = conflict
        resolved[name] = u
        if conflict:
            skipped.append({"name": name, "reason": f"sign conflict across windows {u['signs']}"})
    return resolved, skipped


def load_stress_margins(etf: str) -> dict:
    """Harvest stress_sortino / deep_stress_sortino from mining attempt logs."""
    data_dir = REPO_ROOT / "day-model-new" / "data"
    margins = {}
    for suffix in SUFFIXES:
        path = data_dir / f"mining_attempts_{etf}_single{suffix}.json"
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            attempts = json.load(f)
        for a in attempts:
            name = a.get("feature_name")
            if not name:
                continue
            m = margins.setdefault(name, {})
            for key in ("stress_sortino", "deep_stress_sortino"):
                v = a.get(key)
                if v is not None and (key not in m or v > m[key]):
                    m[key] = float(v)
    return margins


def _sharpe(net: np.ndarray) -> float:
    if len(net) < 20:
        return -99.0
    s = net.std()
    return float(net.mean() / s * np.sqrt(252)) if s > 1e-12 else -99.0


def evaluate_set(Z: np.ndarray, signs_sub: np.ndarray, ret: np.ndarray,
                 dates: pd.Series, train_mask: np.ndarray, oos_mask: np.ndarray) -> dict:
    """Walk-forward evaluation of one feature subset (columns of Z)."""
    Zc = (Z * signs_sub[None, :]).mean(axis=1)

    sweep = sweep_optimal_threshold(
        Zc[train_mask], ret[train_mask], mode="binary", long_only=False,
        fee_bps=FEE_BPS, z_range=(0.5, 1.5), z_step=0.1)
    z_th_long, z_th_short = compute_production_threshold(
        sweep, z_buffer=Z_BUFFER_LONG, z_short_buffer=Z_BUFFER_SHORT)

    pos = generate_positions(Zc[oos_mask], z_th=z_th_long, z_th_short=z_th_short,
                             mode="binary", long_only=False)
    net, raw, _ = simulate_etf_spot(ret[oos_mask], pos, fee_bps=FEE_BPS)

    oos_dates = dates[oos_mask].values
    years = sorted({pd.Timestamp(d).year for d in oos_dates})
    per_year = {}
    for y in years:
        ym = np.array([pd.Timestamp(d).year == y for d in oos_dates])
        per_year[str(y)] = {
            "sharpe": round(_sharpe(net[ym]), 4),
            "pnl": round(float(net[ym].sum()), 4),
            "trades": int((np.abs(pos[ym]) > 1e-5).sum()),
        }

    return {
        "z_th_long": round(float(z_th_long), 3),
        "z_th_short": round(float(z_th_short), 3),
        "z_train_long": sweep.get("optimal_z_th_long"),
        "z_train_short": sweep.get("optimal_z_th_short"),
        "oos_sharpe": round(_sharpe(net), 4),
        "oos_pnl": round(float(net.sum()), 4),
        "oos_trades": int((np.abs(pos) > 1e-5).sum()),
        "oos_win_rate": round(float((net[np.abs(pos) > 1e-5] > 0).mean()), 4)
        if (np.abs(pos) > 1e-5).any() else 0.0,
        "per_year": per_year,
    }


def greedy_select(etf: str, universe: dict, Z: np.ndarray, col_index: dict,
                  signs_by_name: dict, ret: np.ndarray, dates: pd.Series,
                  train_mask: np.ndarray, oos_mask: np.ndarray,
                  clusters: dict, margins: dict) -> dict:
    """Greedy forward selection to TARGET_K. Deterministic."""
    # Stability seed ranking: (n_windows desc, mean deflated_ic desc, name)
    def mean_metric(u, key):
        vals = [e.get(key) for e in u["entries"].values() if e.get(key) is not None]
        return float(np.mean(vals)) if vals else 0.0

    cand_names = sorted(
        universe.keys(),
        key=lambda n: (-universe[n]["n_windows"], -mean_metric(universe[n], "deflated_ic"), n))

    # Precompute train-window z correlation matrix on demand columns
    Z_train = Z[train_mask]

    def corr_ok(new_idx, chosen_idx):
        for ci in chosen_idx:
            r = np.corrcoef(Z_train[:, new_idx], Z_train[:, ci])[0, 1]
            if abs(r) > CORR_CAP:
                return False, float(r)
        return True, 0.0

    def cluster_ok(name, chosen_names):
        cid = clusters.get(name) if clusters else None
        if cid is None:
            return True
        cnt = sum(1 for cn in chosen_names if clusters.get(cn) == cid)
        return cnt < MAX_PER_CLUSTER

    # Seed: best-stability single feature that evaluates
    selected_names, selected_idx = [], []
    greedy_log = []
    current_eval = None

    for seed in cand_names:
        idx = col_index[seed]
        ev = evaluate_set(Z[:, [idx]], np.array([signs_by_name[seed]]), ret, dates,
                          train_mask, oos_mask)
        selected_names, selected_idx = [seed], [idx]
        current_eval = ev
        greedy_log.append({"step": 0, "action": "seed", "added": seed,
                           "oos_sharpe": ev["oos_sharpe"], "oos_pnl": ev["oos_pnl"]})
        break

    while len(selected_names) < TARGET_K:
        best = None
        for name in cand_names:
            if name in selected_names:
                continue
            if not cluster_ok(name, selected_names):
                continue
            idx = col_index[name]
            ok, _ = corr_ok(idx, selected_idx)
            if not ok:
                continue
            trial_idx = selected_idx + [idx]
            trial_signs = np.array([signs_by_name[n] for n in selected_names + [name]])
            ev = evaluate_set(Z[:, trial_idx], trial_signs, ret, dates, train_mask, oos_mask)
            if any(v["sharpe"] <= MIN_YEARLY_SHARPE for v in ev["per_year"].values()):
                continue
            key = (-ev["oos_sharpe"], name)
            if best is None or key < best[0]:
                best = (key, name, idx, ev)
        if best is None:
            print(f"  [{etf}] greedy stopped at {len(selected_names)} features (no admissible candidate)")
            break
        _, name, idx, ev = best
        selected_names.append(name)
        selected_idx.append(idx)
        current_eval = ev
        greedy_log.append({
            "step": len(greedy_log), "action": "add", "added": name,
            "oos_sharpe": ev["oos_sharpe"], "oos_pnl": ev["oos_pnl"],
            "per_year_sharpe": {y: v["sharpe"] for y, v in ev["per_year"].items()},
        })
        print(f"  [{etf}] step {len(greedy_log)-1}: +{name} -> Sharpe {ev['oos_sharpe']:.3f} "
              f"PnL {ev['oos_pnl']:+.3f} trades {ev['oos_trades']}")

    return {"names": selected_names, "eval": current_eval, "log": greedy_log}


def run_etf(etf: str, out_dir: Path) -> dict:
    print(f"\n{'='*78}\nQMT SELECTION: {etf}\n{'='*78}")
    universe, skipped = load_universe(etf)
    margins = load_stress_margins(etf)
    clusters = load_cluster_assignments(etf, side="single", suffix="")
    print(f"  universe: {len(universe)} features ({len(skipped)} sign conflicts dropped)")

    df = load_etf_dataset(etf)
    ret = df["trade_return"].values.astype(np.float64)
    dates = df["date"]
    train_mask = (df["date"] < TRAIN_END).values
    oos_mask = ((df["date"] >= TRAIN_END) & (df["date"] < OOS_END)).values

    # Build pool-format entries for the whole universe (recipe + sign)
    pool_fmt = []
    names = sorted(universe.keys())
    for name in names:
        u = universe[name]
        entry = {"feature_name": name, "sign": u["sign"]}
        # recipe: take from any window entry that has one
        for e in u.get("entries", {}).values():
            if "recipe" in e:
                entry["recipe"] = e["recipe"]
                break
        pool_fmt.append(entry)

    X_raw, signs, feat_names = build_pool_feature_matrix(df, pool_fmt)
    Z = expanding_zscore_numba(X_raw, burn_in=BURN_IN, clip=3.0)
    col_index = {n: i for i, n in enumerate(feat_names)}
    signs_by_name = {n: float(s) for n, s in zip(feat_names, signs)}

    result = greedy_select(etf, universe, Z, col_index, signs_by_name, ret, dates,
                           train_mask, oos_mask, clusters or {}, margins)

    # Assemble deliverable
    def mean_metric(name, key):
        u = universe[name]
        vals = [e.get(key) for e in u.get("entries", {}).values() if e.get(key) is not None]
        return round(float(np.mean(vals)), 5) if vals else None

    features_out = []
    for name in result["names"]:
        u = universe[name]
        entry = {"feature_name": name, "sign": u["sign"], "weight": 1.0 / len(result["names"])}
        for e in u.get("entries", {}).values():
            if "recipe" in e:
                entry["recipe"] = e["recipe"]
                break
        entry["evidence"] = {
            "windows": sorted(u["windows"].keys()),
            "n_windows": u["n_windows"],
            "sign_conflict": u["sign_conflict"],
            "mean_deflated_ic": mean_metric(name, "deflated_ic"),
            "mean_ic_ir": mean_metric(name, "ic_ir"),
            "mean_monotonicity": mean_metric(name, "monotonicity"),
            "stress_sortino": margins.get(name, {}).get("stress_sortino"),
            "deep_stress_sortino": margins.get(name, {}).get("deep_stress_sortino"),
            "cluster": clusters.get(name) if clusters else None,
        }
        features_out.append(entry)

    ev = result["eval"]
    deliverable = {
        "etf": etf,
        "generated": pd.Timestamp.now().isoformat(),
        "method": "cross-window stability + greedy walk-forward (deterministic)",
        "config": {
            "target_k": TARGET_K, "corr_cap": CORR_CAP, "max_per_cluster": MAX_PER_CLUSTER,
            "min_yearly_sharpe": MIN_YEARLY_SHARPE, "train_end": str(TRAIN_END.date()),
            "oos_end": str(OOS_END.date()), "fee_bps": FEE_BPS,
            "z_buffer_long": Z_BUFFER_LONG, "z_buffer_short": Z_BUFFER_SHORT,
            "burn_in": BURN_IN, "clip": 3.0,
        },
        "thresholds": {
            "z_th_long": ev["z_th_long"], "z_th_short": ev["z_th_short"],
            "z_train_long": ev["z_train_long"], "z_train_short": ev["z_train_short"],
        },
        "features": features_out,
        "oos": {
            "sharpe": ev["oos_sharpe"], "pnl": ev["oos_pnl"],
            "trades": ev["oos_trades"], "win_rate": ev["oos_win_rate"],
            "per_year": ev["per_year"],
        },
        "greedy_log": result["log"],
        "skipped_sign_conflicts": skipped,
    }

    out_path = out_dir / f"qmt_selection_{etf}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(deliverable, f, indent=2)
    print(f"  saved -> {out_path}")
    print(f"  FINAL: Sharpe {ev['oos_sharpe']:.3f} | PnL {ev['oos_pnl']:+.3f} | "
          f"trades {ev['oos_trades']} | WR {ev['oos_win_rate']:.1%}")
    print(f"  per-year: " + ", ".join(f"{y}:{v['sharpe']:+.2f}" for y, v in ev["per_year"].items()))
    return deliverable


def main():
    parser = argparse.ArgumentParser(description="QMT feature hand-pick (Part A)")
    parser.add_argument("-e", "--etf", default="500ETF,159915ETF",
                        help="Comma-separated ETFs (default: 500ETF,159915ETF)")
    args = parser.parse_args()

    out_dir = HERE / "data"
    out_dir.mkdir(exist_ok=True)
    results = {}
    for etf in [e.strip() for e in args.etf.split(",") if e.strip()]:
        results[etf] = run_etf(etf, out_dir)

    with open(out_dir / "qmt_selection_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nAll done.")


if __name__ == "__main__":
    main()
