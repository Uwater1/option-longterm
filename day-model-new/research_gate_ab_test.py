#!/usr/bin/env python3
"""A/B test harness for candidate admission gates (ideas from claude_said.txt).

Methodology (mirrors filter_diagnosis.py):
  - Population: ADMITTED features (and optionally REJECTED_REDUNDANCY = pre-B4
    population) from mining_attempts_{etf}_{side}{suffix}.json.
  - Ground truth: OOS window after train_end. Labels:
      TP:     lock IC > 0 AND lock Sharpe > 0
      Median: lock IC > 0 AND lock Sharpe <= 0
      FP:     lock IC <= 0
  - All candidate gate metrics are TRAINING-ONLY (computed on train-window
    strategy returns), so the test answers: "had this gate existed, how many
    FPs would it have killed and how many TPs would it have collaterally
    rejected?"

Candidate gates tested (threshold sweeps):
  G1  PSR (Bailey & Lopez de Prado, SR*=0)         reject if psr < t
  G2  Negative skew of daily cost-returns          reject if skew < t
  G3  Excess kurtosis of daily cost-returns        reject if exkurt > t
  G4  Block-bootstrap Sortino CI lower bound       reject if ci_low <= 0
  G5  Payoff ratio (avg win / avg loss, active)    reject if payoff < t
  G6  IC-contribution concentration (top5% share)  reject if conc > t
  G7  Cost-stress Sortino (k x 8bps cost)          reject if sortino_kx <= 0
  G8  Regime-conditioned Sortino (vol quintiles)   reject if n_neg_regimes > t

Usage:
  python day-model-new/research_gate_ab_test.py                 # full sweep
  python day-model-new/research_gate_ab_test.py -e 300ETF --sides single
  python day-model-new/research_gate_ab_test.py --population preb4
  python day-model-new/research_gate_ab_test.py --report-only   # re-aggregate cache
"""

import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import rankdata, norm
from collections import defaultdict

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))

from build_features import FEATURES
from recipe_utils import compute_recipe, build_ecdf_grid_float32

ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

# Windows: suffix -> (train_start, train_end). Ground truth = date >= train_end.
WINDOWS = {
    "":             ("2014-01-01", "2022-01-01"),   # matches filter_diagnosis default
    "_p2015_2023":  ("2015-01-01", "2023-01-01"),
    "_p2016_2024":  ("2016-01-01", "2024-01-01"),
    "_p2017_2025":  ("2017-01-01", "2025-01-01"),
    "_p2018_2026":  ("2018-01-01", "2026-01-01"),
}

COST = 0.0008          # 8 bps per active day (matches recipe_utils.simulate_returns)
BOOT_B = 199
BOOT_BLOCK = 10
ANNUAL = 244


def _spearman(a, b):
    if len(a) < 5 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom >= 1e-12 else 0.0


def _positions(y, pred, side):
    """Binary tail positions WITHOUT absolute-sign enforcement
    (identical to filter_diagnosis.evaluate_feature labeling path)."""
    n = len(pred)
    order = np.argsort(pred, kind="quicksort")
    pos = np.zeros(n, dtype=np.float64)
    if side == "long":
        n_tail = max(5, int(n * 0.15))
        pos[order[-n_tail:]] = 1.0
    elif side == "short":
        n_tail = max(5, int(n * 0.15))
        pos[order[:n_tail]] = -1.0
    else:  # single: two-sided
        n_tail = max(5, int(n * 0.10))
        pos[order[-n_tail:]] = 1.0
        pos[order[:n_tail]] = -1.0
    return pos


def _sortino(returns):
    ann_ret = float(np.mean(returns) * ANNUAL)
    downside = np.minimum(returns, 0.0)
    downside_vol = float(np.std(downside) * np.sqrt(ANNUAL))
    return ann_ret / (downside_vol + 1e-10)


def _sharpe(returns):
    ann_ret = float(np.mean(returns) * ANNUAL)
    ann_vol = float(np.std(returns) * np.sqrt(ANNUAL))
    return ann_ret / (ann_vol + 1e-10)


def _feature_values(df, feat_name, recipe, means, stds, medians, ecdfs):
    if recipe:
        try:
            return compute_recipe(df, recipe, means, stds, medians, ecdfs)
        except Exception:
            return None
    if feat_name not in df.columns:
        return None
    return df[feat_name].values.astype(np.float64)


def evaluate_one(train_df, lock_df, item, side, tstats, lstats):
    """Return dict of gate metrics (train-only) + OOS labels, or None."""
    feat_name = item["feature_name"]
    sign = item.get("sign", 1)
    recipe = item.get("recipe", None)

    # ---- Train window ----
    vals_tr = _feature_values(train_df, feat_name, recipe, *tstats)
    if vals_tr is None:
        return None
    pred_tr = sign * vals_tr
    y_tr = train_df["trade_return"].values.astype(np.float64)
    if np.std(pred_tr) < 1e-12:
        return None

    pos = _positions(y_tr, pred_tr, side)
    raw = pos * y_tr
    active = pos != 0
    cost_ret = raw - np.abs(pos) * COST
    stress_ret = raw - np.abs(pos) * COST * 2.0   # G7: 2x cost
    # Distributional gates must use ACTIVE days only: tail strategies are ~80-90%
    # flat, and the zero days would dominate skew/kurtosis/PSR statistics.
    act_ret = raw[active]
    act_cost_ret = cost_ret[active]

    train_ic = _spearman(y_tr, pred_tr)

    # G1: PSR (daily SR, SR* = 0) on active-day returns
    r = act_cost_ret
    mu, sd = float(np.mean(r)), float(np.std(r))
    T = len(r)
    if T < 30 or sd < 1e-12:
        psr = 0.0
    else:
        sr = mu / sd
        g3 = float(pd.Series(r).skew())
        g4 = float(pd.Series(r).kurtosis()) + 3.0  # non-excess kurtosis
        denom2 = 1.0 - g3 * sr + ((g4 - 1.0) / 4.0) * sr * sr
        psr = float(norm.cdf(sr * np.sqrt(max(T - 1, 1)) / np.sqrt(max(denom2, 1e-12))))

    # G2/G3: skew & excess kurtosis on active-day returns
    if T >= 30:
        skew = float(pd.Series(act_cost_ret).skew())
        exkurt = float(pd.Series(act_cost_ret).kurtosis())
    else:
        skew, exkurt = None, None

    # G4: block bootstrap Sortino CI lower bound (5th pct) on full daily series
    r_full = cost_ret
    T_full = len(r_full)
    nb = BOOT_BLOCK
    nblocks = int(np.ceil(T_full / nb))
    rng = np.random.default_rng(42)
    starts = rng.integers(0, max(T_full - nb, 1), size=(BOOT_B, nblocks))
    offs = np.arange(nb)
    idx = (starts[:, :, None] + offs[None, None, :]) % T_full
    boot_mat = r_full[idx].reshape(BOOT_B, -1)[:, :T_full]
    boot_sort = np.array([_sortino(boot_mat[i]) for i in range(BOOT_B)])
    sortino_ci_low = float(np.percentile(boot_sort, 5))
    sortino_train = float(_sortino(cost_ret))

    # G5: payoff ratio on active days
    wins = act_ret[act_ret > 0]
    losses = act_ret[act_ret < 0]
    if len(losses) == 0:
        payoff = 99.0
    elif len(wins) == 0:
        payoff = 0.0
    else:
        payoff = float(np.mean(wins) / abs(np.mean(losses)))

    # G6: per-day Spearman IC contribution concentration
    ra = rankdata(y_tr)
    rb = rankdata(pred_tr)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom >= 1e-12:
        contrib = (ra * rb) / denom
        pos_contrib = contrib[contrib > 0]
        if len(pos_contrib) > 10 and pos_contrib.sum() > 1e-12:
            k = max(1, int(np.ceil(0.05 * len(y_tr))))
            topk = np.sort(pos_contrib)[-k:]
            concentration = float(topk.sum() / pos_contrib.sum())
        else:
            concentration = 0.0
    else:
        concentration = 0.0

    # G7: cost-stress sortino (2x)
    stress_sortino = float(_sortino(stress_ret))

    # G8: regime-conditioned Sortino (vol20 quintiles, mirrors select_features).
    # Only regimes with enough ACTIVE days count; strictly-negative = reject side.
    vol20 = pd.Series(y_tr).rolling(20).std().values
    valid_vol = ~np.isnan(vol20)
    min_active_regime = 10
    try:
        pcts = np.percentile(vol20[valid_vol], [20, 40, 60, 80])
        masks = [
            valid_vol & (vol20 <= pcts[0]),
            valid_vol & (vol20 > pcts[0]) & (vol20 <= pcts[1]),
            valid_vol & (vol20 > pcts[1]) & (vol20 <= pcts[2]),
            valid_vol & (vol20 > pcts[2]) & (vol20 <= pcts[3]),
            valid_vol & (vol20 > pcts[3]),
        ]
        n_neg_regimes = 0
        n_valid_regimes = 0
        for m in masks:
            m_act = m & active
            if m.sum() < 20 or m_act.sum() < min_active_regime:
                continue
            n_valid_regimes += 1
            if _sortino(cost_ret[m_act]) < 0:
                n_neg_regimes += 1
        if n_valid_regimes < 3:
            n_neg_regimes = None
    except Exception:
        n_neg_regimes = None

    # ---- OOS (lockbox) ground truth ----
    vals_lk = _feature_values(lock_df, feat_name, recipe, *lstats)
    lock_ic, lock_sharpe = np.nan, np.nan
    tier = None
    if vals_lk is not None:
        pred_lk = sign * vals_lk
        y_lk = lock_df["trade_return"].values.astype(np.float64)
        if np.std(pred_lk) >= 1e-12 and len(y_lk) >= 30:
            lock_ic = _spearman(y_lk, pred_lk)
            pos_lk = _positions(y_lk, pred_lk, side)
            lk_ret = pos_lk * y_lk - np.abs(pos_lk) * COST
            lock_sharpe = _sharpe(lk_ret)
            if lock_ic <= 0:
                tier = "FP"
            elif lock_sharpe <= 0:
                tier = "Median"
            else:
                tier = "TP"

    return {
        "feature_name": feat_name,
        "verdict": item.get("verdict"),
        "train_ic": float(train_ic),
        "train_sharpe": float(_sharpe(cost_ret)),
        "train_sortino": sortino_train,
        "psr": psr,
        "skew": skew,
        "exkurt": exkurt,
        "sortino_ci_low": sortino_ci_low,
        "payoff": payoff,
        "concentration": concentration,
        "stress_sortino": stress_sortino,
        "n_neg_regimes": n_neg_regimes,
        "lock_ic": float(lock_ic) if not np.isnan(lock_ic) else None,
        "lock_sharpe": float(lock_sharpe) if not np.isnan(lock_sharpe) else None,
        "tier": tier,
    }


def prep_split(df, train_start, train_end):
    train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
    lock_df = df[df["date"] >= train_end].reset_index(drop=True)
    if len(train_df) < 200 or len(lock_df) < 30:
        return None, None, None
    means = {c: float(train_df[c].mean()) for c in FEATURES}
    stds = {c: float(train_df[c].std()) for c in FEATURES}
    medians = {c: float(train_df[c].median()) for c in FEATURES}
    ecdfs = {c: build_ecdf_grid_float32(train_df[c].values.astype(np.float32), n_knots=128) for c in FEATURES}
    stats = (means, stds, medians, ecdfs)
    return train_df, lock_df, stats


def run_combo(etf, side, suffix, train_start, train_end, population, df_cache):
    attempts_path = HERE / "data" / f"mining_attempts_{etf}_{side}{suffix}.json"
    if not attempts_path.exists():
        return None
    with open(attempts_path, "r", encoding="utf-8") as f:
        attempts = json.load(f)

    if population == "admitted":
        pool = [a for a in attempts if a.get("verdict", "").startswith("ADMITTED")]
    else:  # preb4: reached correlation gate (ADMITTED + REJECTED_REDUNDANCY)
        pool = [a for a in attempts
                if a.get("verdict", "").startswith("ADMITTED") or a.get("verdict") == "REJECTED_REDUNDANCY"]
    if not pool:
        return None

    if etf not in df_cache:
        path = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
        if not path.exists():
            return None
        df = pd.read_parquet(path)
        if "date" not in df.columns:
            df = df.reset_index()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        for col in FEATURES:
            df[col] = df[col].ffill()
        df_cache[etf] = df
    df = df_cache[etf]

    # median-impute per window using train medians (like filter_diagnosis)
    train_df, lock_df, tstats = prep_split(df, train_start, train_end)
    if train_df is None:
        return None
    tr_med = tstats[2]
    for col in FEATURES:
        train_df[col] = train_df[col].fillna(tr_med[col])
        lock_df[col] = lock_df[col].fillna(tr_med[col])
    lstats = tstats  # normalization constants come from TRAIN window

    rows = []
    for item in pool:
        try:
            res = evaluate_one(train_df, lock_df, item, side, tstats, lstats)
        except Exception as e:
            print(f"    [warn] eval failed for {item.get('feature_name')}: {e}")
            res = None
        if res is not None and res["tier"] is not None:
            rows.append(res)
    return {
        "etf": etf, "side": side, "suffix": suffix,
        "n_pool": len(pool), "n_labeled": len(rows),
        "rows": rows,
    }


# ─────────────────────────── Aggregation ───────────────────────────

GATES = {
    "G1_psr":              {"metric": "psr",             "dir": "lt", "thresholds": [0.50, 0.60, 0.70, 0.80, 0.90]},
    "G2_neg_skew":         {"metric": "skew",            "dir": "lt", "thresholds": [0.0, -0.25, -0.50, -0.75, -1.0]},
    "G3_exkurt":           {"metric": "exkurt",          "dir": "gt", "thresholds": [1.0, 2.0, 3.0, 5.0, 8.0]},
    "G4_boot_sortino_ci":  {"metric": "sortino_ci_low",  "dir": "lt", "thresholds": [0.0]},
    "G5_payoff":           {"metric": "payoff",          "dir": "lt", "thresholds": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]},
    "G6_ic_concentration": {"metric": "concentration",   "dir": "gt", "thresholds": [0.30, 0.40, 0.50, 0.60, 0.70]},
    "G7_cost_stress":      {"metric": "stress_sortino",  "dir": "lt", "thresholds": [0.0]},
    "G8_regime_sortino":   {"metric": "n_neg_regimes",   "dir": "gt", "thresholds": [0, 1, 2]},
}


def _rejects(gate, row, thr):
    v = row.get(gate["metric"])
    if v is None:
        return False
    if gate["dir"] == "lt":
        if thr == 0 and gate["metric"] in ("sortino_ci_low", "stress_sortino"):
            return v <= thr  # "must be strictly positive" gates
        return v < thr
    return v > thr


def aggregate(combos, focus_suffixes):
    """Produce per-gate summary tables."""
    # Flatten with combo tag
    all_rows = []
    for c in combos:
        tag = f"{c['etf']}/{c['side']}{c['suffix']}"
        for r in c["rows"]:
            r2 = dict(r)
            r2["_combo"] = tag
            r2["_suffix"] = c["suffix"]
            all_rows.append(r2)

    tiers = defaultdict(int)
    for r in all_rows:
        tiers[r["tier"]] += 1
    n_all = len(all_rows)
    summary = {
        "population_size": n_all,
        "tiers": dict(tiers),
        "baseline_fp_rate": tiers["FP"] / n_all if n_all else 0.0,
        "gates": {},
    }

    for gname, gate in GATES.items():
        gate_out = {"thresholds": {}}
        for thr in gate["thresholds"]:
            rej = [r for r in all_rows if _rejects(gate, r, thr)]
            keep = [r for r in all_rows if not _rejects(gate, r, thr)]
            n_rej = len(rej)
            rej_t = defaultdict(int)
            for r in rej:
                rej_t[r["tier"]] += 1
            keep_t = defaultdict(int)
            for r in keep:
                keep_t[r["tier"]] += 1
            n_fp, n_tp, n_md = tiers["FP"], tiers["TP"], tiers["Median"]
            fp_kill = rej_t["FP"] / n_fp if n_fp else 0.0
            tp_kill = rej_t["TP"] / n_tp if n_tp else 0.0
            md_kill = rej_t["Median"] / n_md if n_md else 0.0
            fp_rate_after = keep_t["FP"] / len(keep) if keep else 0.0
            # consistency on focus periods
            focus_rows = [r for r in all_rows if r["_suffix"] in focus_suffixes]
            f_rej = [r for r in focus_rows if _rejects(gate, r, thr)]
            f_keep = [r for r in focus_rows if not _rejects(gate, r, thr)]
            ft = defaultdict(int)
            for r in focus_rows:
                ft[r["tier"]] += 1
            frt = defaultdict(int)
            for r in f_rej:
                frt[r["tier"]] += 1
            fkt = defaultdict(int)
            for r in f_keep:
                fkt[r["tier"]] += 1
            gate_out["thresholds"][str(thr)] = {
                "n_rejected": n_rej,
                "fp_kill_rate": fp_kill,
                "tp_kill_rate": tp_kill,
                "median_kill_rate": md_kill,
                "fp_killed": rej_t["FP"], "tp_killed": rej_t["TP"], "median_killed": rej_t["Median"],
                "baseline_fp_rate": tiers["FP"] / n_all if n_all else 0.0,
                "fp_rate_after": fp_rate_after,
                "focus_fp_kill_rate": frt["FP"] / ft["FP"] if ft["FP"] else 0.0,
                "focus_tp_kill_rate": frt["TP"] / ft["TP"] if ft["TP"] else 0.0,
                "focus_fp_rate_after": fkt["FP"] / len(f_keep) if f_keep else 0.0,
                "focus_baseline_fp_rate": ft["FP"] / len(focus_rows) if focus_rows else 0.0,
            }
        summary["gates"][gname] = gate_out
    return summary


def render_markdown(summary, focus_suffixes, population):
    lines = [
        "# Candidate Gate A/B Test (claude_said.txt ideas)",
        "",
        f"Population: **{population}** | N={summary['population_size']} | "
        f"TP={summary['tiers'].get('TP', 0)} Median={summary['tiers'].get('Median', 0)} FP={summary['tiers'].get('FP', 0)} | "
        f"Baseline FP rate: **{summary['baseline_fp_rate']:.1%}**",
        "",
        f"Focus periods (user-flagged FP-heavy): `{', '.join(focus_suffixes)}`",
        "",
        "Kill rates are fractions of each tier rejected by the gate. "
        "`FP rate after` = FP share among survivors. Focus columns restrict to focus periods.",
        "",
        "| Gate | Threshold | Rej | FP kill | TP kill | Med kill | FP rate after | Focus FP kill | Focus TP kill | Focus FP after |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for gname, gate in summary["gates"].items():
        for thr, s in gate["thresholds"].items():
            lines.append(
                f"| {gname} | {thr} | {s['n_rejected']} | {s['fp_kill_rate']:.1%} | {s['tp_kill_rate']:.1%} | "
                f"{s['median_kill_rate']:.1%} | {s['fp_rate_after']:.1%} | {s['focus_fp_kill_rate']:.1%} | "
                f"{s['focus_tp_kill_rate']:.1%} | {s['focus_fp_rate_after']:.1%} |"
            )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etfs", nargs="*", default=ETFS)
    parser.add_argument("--sides", nargs="*", default=SIDES)
    parser.add_argument("--suffixes", nargs="*", default=list(WINDOWS.keys()),
                        help="Window suffixes to test ('' = default window)")
    parser.add_argument("--population", choices=["admitted", "preb4"], default="admitted")
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    data_dir = HERE / "data"
    cache_file = data_dir / f"gate_ab_cache_{args.population}.json"
    focus_suffixes = ["_p2016_2024", "_p2017_2025", "_p2018_2026"]

    combos = []
    if not args.report_only:
        tasks = []
        for suffix in args.suffixes:
            if suffix not in WINDOWS:
                continue
            ts, te = WINDOWS[suffix]
            for etf in args.etfs:
                for side in args.sides:
                    tasks.append((etf, side, suffix, ts, te))


        # Existing cache reuse
        cached = {}
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    for c in json.load(f):
                        cached[(c["etf"], c["side"], c["suffix"])] = c
            except Exception:
                cached = {}

        df_cache = {}
        for i, (etf, side, suffix, ts, te) in enumerate(tasks, 1):
            key = (etf, side, suffix)
            if key in cached:
                combos.append(cached[key])
                print(f"[{i}/{len(tasks)}] cache hit {etf}/{side}{suffix}")
                continue
            print(f"[{i}/{len(tasks)}] evaluating {etf}/{side}{suffix} ...")
            res = run_combo(etf, side, suffix, ts, te, args.population, df_cache)
            if res:
                combos.append(res)
                t = defaultdict(int)
                for r in res["rows"]:
                    t[r["tier"]] += 1
                print(f"    labeled {res['n_labeled']}/{res['n_pool']} "
                      f"(TP={t['TP']} Med={t['Median']} FP={t['FP']})")
            else:
                print("    skipped (no attempts / insufficient data)")

        # Merge with cached combos not re-run this pass (only within requested scope)
        seen = {(c["etf"], c["side"], c["suffix"]) for c in combos}
        req_etfs, req_sides, req_suffs = set(args.etfs), set(args.sides), set(args.suffixes)
        for key, c in cached.items():
            if key not in seen and key[0] in req_etfs and key[1] in req_sides and key[2] in req_suffs:
                combos.append(c)

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(combos, f)
        print(f"\nSaved cache ({len(combos)} combos) to {cache_file.name}")
    else:
        if not cache_file.exists():
            print("No cache found; run without --report-only first.")
            return
        with open(cache_file, "r", encoding="utf-8") as f:
            combos = json.load(f)

    summary = aggregate(combos, focus_suffixes)
    md = render_markdown(summary, focus_suffixes, args.population)
    out_md = HERE / f"GATE_AB_TEST_{args.population}.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    with open(data_dir / f"gate_ab_summary_{args.population}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("\n" + md)
    print(f"Saved report to {out_md}")


if __name__ == "__main__":
    main()
