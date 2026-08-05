"""Offline simulation of the Robustness Gate on the STALE period pools (8/3, pre-gate)
using the PIPELINE's enforced-sign position model (matching select_features.py),
joined with OOS tiers from filter_diagnosis_p*.json.

Answers: had the gate run on these periods with threshold t, how many FPs/Medians/TPs
would it reject? Also sweeps thresholds to find the best FP leverage.
"""
import sys
import json
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "mining"))
sys.path.insert(0, str(HERE.parent / "day-model"))

import research_gate_ab_test as H
from select_features import _tail_positions_binary, _sortino_annual, _bootstrap_sortino_ci

COST = 0.0008
FOCUS = {
    "_p2015_2023": ("2015-01-01", "2023-01-01"),
    "_p2016_2024": ("2016-01-01", "2024-01-01"),
    "_p2017_2025": ("2017-01-01", "2025-01-01"),
    "_p2018_2026": ("2018-01-01", "2026-01-01"),
}
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]


def evaluate_enforced(train_df, lock_df, item, side, tstats, lstats):
    """Same as H.evaluate_one but with enforced-sign binary positions
    (matching select_features.py Robustness Gate)."""
    feat_name = item["feature_name"]
    sign = item.get("sign", 1)
    recipe = item.get("recipe", None)

    vals_tr = H._feature_values(train_df, feat_name, recipe, *tstats)
    if vals_tr is None:
        return None
    pred_tr = sign * vals_tr
    y_tr = train_df["trade_return"].values.astype(np.float64)
    if np.std(pred_tr) < 1e-12:
        return None

    pos = _tail_positions_binary(y_tr, pred_tr, side)
    raw = pos * y_tr
    abs_pos = np.abs(pos)
    cost_ret = raw - abs_pos * COST
    stress_ret = raw - abs_pos * COST * 2.0

    rng = np.random.default_rng(42)
    sortino_ci_low = _bootstrap_sortino_ci(cost_ret, rng)
    stress_sortino = _sortino_annual(stress_ret)
    sortino_train = _sortino_annual(cost_ret)

    # Non-enforced variant (A/B harness position model)
    pos_ne = H._positions(y_tr, pred_tr, side)
    raw_ne = pos_ne * y_tr
    abs_ne = np.abs(pos_ne)
    cost_ret_ne = raw_ne - abs_ne * COST
    rng_ne = np.random.default_rng(42)
    ci_ne = _bootstrap_sortino_ci(cost_ret_ne, rng_ne)
    stress_ne = _sortino_annual(raw_ne - abs_ne * COST * 2.0)

    # OOS tier (same labeling as H)
    vals_lk = H._feature_values(lock_df, feat_name, recipe, *lstats)
    tier = None
    lock_ic = lock_sharpe = None
    if vals_lk is not None:
        pred_lk = sign * vals_lk
        y_lk = lock_df["trade_return"].values.astype(np.float64)
        if np.std(pred_lk) >= 1e-12 and len(y_lk) >= 30:
            lock_ic = H._spearman(y_lk, pred_lk)
            pos_lk = _tail_positions_binary(y_lk, pred_lk, side)
            lk_ret = pos_lk * y_lk - np.abs(pos_lk) * COST
            lock_sharpe = H._sharpe(lk_ret)
            tier = "FP" if lock_ic <= 0 else ("Median" if lock_sharpe <= 0 else "TP")

    return {
        "feature_name": feat_name,
        "sortino": sortino_train,
        "sortino_ci_low": sortino_ci_low,
        "stress_sortino": stress_sortino,
        "sortino_ci_low_ne": ci_ne,
        "stress_sortino_ne": stress_ne,
        "lock_ic": lock_ic,
        "tier": tier,
    }


def main():
    df_cache = {}
    all_rows = []
    for suffix, (t0, t1) in FOCUS.items():
        diag_path = HERE / "data" / f"filter_diagnosis{suffix}.json"
        if not diag_path.exists():
            continue
        diag = json.load(open(diag_path, encoding="utf-8"))
        for etf in ETFS:
            if etf not in diag:
                continue
            for side, s in diag[etf].items():
                tier_of = {}
                for tier in ("FP", "Median", "TP"):
                    for it in s.get(tier.lower() + "_features", []):
                        tier_of[(it["feature_name"], it.get("sign", 1))] = tier
                if not tier_of:
                    continue
                apath = HERE / "data" / f"mining_attempts_{etf}_{side}{suffix}.json"
                if not apath.exists():
                    continue
                attempts = json.load(open(apath, encoding="utf-8"))
                pool = [a for a in attempts if (a["feature_name"], a.get("sign", 1)) in tier_of]
                if not pool:
                    continue
                if etf not in df_cache:
                    path = HERE.parent / "day-model" / "data" / f"features_{etf}.parquet"
                    df = H.pd.read_parquet(path)
                    if "date" not in df.columns:
                        df = df.reset_index()
                    df["date"] = H.pd.to_datetime(df["date"])
                    df = df.sort_values("date").reset_index(drop=True)
                    for col in H.FEATURES:
                        df[col] = df[col].ffill()
                    df_cache[etf] = df
                df = df_cache[etf]
                train_df, lock_df, tstats = H.prep_split(df, t0, t1)
                if train_df is None:
                    continue
                tr_med = tstats[2]
                for col in H.FEATURES:
                    train_df[col] = train_df[col].fillna(tr_med[col])
                    lock_df[col] = lock_df[col].fillna(tr_med[col])
                for item in pool:
                    try:
                        res = evaluate_enforced(train_df, lock_df, item, side, tstats, tstats)
                    except Exception as e:
                        res = None
                    if res is not None and res["tier"] is not None:
                        res["etf"] = etf
                        res["suffix"] = suffix
                        res["true_tier"] = tier_of[(item["feature_name"], item.get("sign", 1))]
                        all_rows.append(res)
        print(f"done {suffix}, cumulative rows={len(all_rows)}")

    # sanity: recomputed tier should match filter_diagnosis tier
    mismatch = sum(1 for r in all_rows if r["tier"] != r["true_tier"])
    print(f"\nrows={len(all_rows)}  tier mismatch vs filter_diagnosis: {mismatch}")

    out = HERE / "scratch" / "gate_focus_rows.json"
    json.dump(all_rows, open(out, "w", encoding="utf-8"), indent=0)
    print("saved", out)

    for grp in [None] + list(FOCUS.keys()):
        sel = all_rows if grp is None else [r for r in all_rows if r["suffix"] == grp]
        if not sel:
            continue
        tiers = {t: [r for r in sel if r["tier"] == t] for t in ["FP", "Median", "TP"]}
        n_fp, n_med, n_tp = len(tiers["FP"]), len(tiers["Median"]), len(tiers["TP"])
        if n_fp + n_med + n_tp == 0:
            continue
        print(f"\n=== {grp or 'ALL FOCUS'}  N={len(sel)} FP={n_fp} Med={n_med} TP={n_tp}  FPrate={n_fp/len(sel):.3f}")
        for t, rs in tiers.items():
            if not rs:
                continue
            ci = np.array([r["sortino_ci_low"] for r in rs])
            ss = np.array([r["stress_sortino"] for r in rs])
            print(f"  {t:6s} n={len(rs):3d} ci med={np.median(ci):6.3f} p25={np.percentile(ci,25):6.3f} | stress med={np.median(ss):6.3f}")
        print("  sweep ci_low<t :")
        for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5]:
            fk = sum(1 for r in tiers["FP"] if r["sortino_ci_low"] <= t)
            mk = sum(1 for r in tiers["Median"] if r["sortino_ci_low"] <= t)
            tk = sum(1 for r in tiers["TP"] if r["sortino_ci_low"] <= t)
            print(f"    t={t:4.1f}  FP {fk:2d}/{n_fp}  Med {mk:2d}/{n_med}  TP {tk:2d}/{n_tp}")
        print("  sweep stress<t :")
        for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            fk = sum(1 for r in tiers["FP"] if r["stress_sortino"] <= t)
            mk = sum(1 for r in tiers["Median"] if r["stress_sortino"] <= t)
            tk = sum(1 for r in tiers["TP"] if r["stress_sortino"] <= t)
            print(f"    t={t:4.1f}  FP {fk:2d}/{n_fp}  Med {mk:2d}/{n_med}  TP {tk:2d}/{n_tp}")
        # NON-ENFORCED variant (A/B harness model)
        print("  [non-enforced] sweep ci_ne<=t :")
        for t in [0.0, 0.2, 0.4, 0.6]:
            fk = sum(1 for r in tiers["FP"] if r["sortino_ci_low_ne"] <= t)
            mk = sum(1 for r in tiers["Median"] if r["sortino_ci_low_ne"] <= t)
            tk = sum(1 for r in tiers["TP"] if r["sortino_ci_low_ne"] <= t)
            print(f"    t={t:4.1f}  FP {fk:2d}/{n_fp}  Med {mk:2d}/{n_med}  TP {tk:2d}/{n_tp}")
        print("  [non-enforced] sweep stress_ne<=t :")
        for t in [0.0, 0.2, 0.4, 0.6]:
            fk = sum(1 for r in tiers["FP"] if r["stress_sortino_ne"] <= t)
            mk = sum(1 for r in tiers["Median"] if r["stress_sortino_ne"] <= t)
            tk = sum(1 for r in tiers["TP"] if r["stress_sortino_ne"] <= t)
            print(f"    t={t:4.1f}  FP {fk:2d}/{n_fp}  Med {mk:2d}/{n_med}  TP {tk:2d}/{n_tp}")


if __name__ == "__main__":
    main()
