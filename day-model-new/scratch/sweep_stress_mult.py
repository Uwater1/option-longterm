"""A/B sweep of G7 COST_STRESS_MULT on the currently-labeled focus pools.

Population: features in the current (gated) pools with OOS tier labels from
filter_diagnosis_p*.json. Since the current gate uses MULT=2.0, the pools only
contain 2x-survivors, so this sweep tests TIGHTENING (MULT > 2): at each
multiplier, how many additional FP/Median/TP pool members would be killed?

Relaxation (MULT < 2) is untestable here: features killed at 2x never entered
the pool and have no OOS labels.
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
from select_features import _tail_positions_binary, _sortino_annual

COST = 0.0008
MULTS = [2.0, 2.5, 3.0, 4.0]
FOCUS = {
    "_p2015_2023": ("2015-01-01", "2023-01-01"),
    "_p2016_2024": ("2016-01-01", "2024-01-01"),
    "_p2017_2025": ("2017-01-01", "2025-01-01"),
    "_p2018_2026": ("2018-01-01", "2026-01-01"),
}
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]


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
                        feat_name = item["feature_name"]
                        sign = item.get("sign", 1)
                        recipe = item.get("recipe", None)
                        vals_tr = H._feature_values(train_df, feat_name, recipe, *tstats)
                        if vals_tr is None:
                            continue
                        pred_tr = sign * vals_tr
                        y_tr = train_df["trade_return"].values.astype(np.float64)
                        if np.std(pred_tr) < 1e-12:
                            continue
                        pos = _tail_positions_binary(y_tr, pred_tr, side)
                        raw = pos * y_tr
                        abs_pos = np.abs(pos)
                        stresses = {m: _sortino_annual(raw - abs_pos * COST * m) for m in MULTS}
                    except Exception:
                        continue
                    tier = tier_of[(item["feature_name"], item.get("sign", 1))]
                    row = {"feature_name": feat_name, "etf": etf, "suffix": suffix,
                           "tier": tier}
                    row.update({f"stress_{m}": v for m, v in stresses.items()})
                    all_rows.append(row)
        print(f"done {suffix}, cumulative rows={len(all_rows)}")

    for grp in list(FOCUS.keys()) + [None]:
        sel = all_rows if grp is None else [r for r in all_rows if r["suffix"] == grp]
        if not sel:
            continue
        tiers = {t: [r for r in sel if r["tier"] == t] for t in ["FP", "Median", "TP"]}
        n_fp, n_med, n_tp = (len(tiers["FP"]), len(tiers["Median"]), len(tiers["TP"]))
        if n_fp + n_med + n_tp == 0:
            continue
        print(f"\n=== {grp or 'ALL FOCUS'}  pool N={len(sel)} FP={n_fp} Med={n_med} TP={n_tp}")
        print(f"  {'MULT':>5} {'addFP':>6} {'addMed':>7} {'addTP':>6} {'FP/TP':>6} {'FPrate_after':>12}")
        for m in MULTS:
            key = f"stress_{m}"
            fk = sum(1 for r in tiers["FP"] if r[key] <= 0)
            mk = sum(1 for r in tiers["Median"] if r[key] <= 0)
            tk = sum(1 for r in tiers["TP"] if r[key] <= 0)
            rem = max(1, n_fp - fk + n_med - mk + n_tp - tk)
            ratio = (fk / max(1, n_fp)) / (tk / max(1, n_tp)) if tk > 0 else float("inf") if fk > 0 else 1.0
            print(f"  {m:5.2f} {fk:3d}/{n_fp:<3d} {mk:3d}/{n_med:<3d} {tk:3d}/{n_tp:<3d} {ratio:6.2f} {(n_fp - fk)/rem:12.3f}")


if __name__ == "__main__":
    main()
