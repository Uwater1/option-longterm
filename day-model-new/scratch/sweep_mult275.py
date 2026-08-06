"""Fine-grained point-stress sweep 2.5->3.0 (20->24bp), per-ETF, on the 2.5-era
labeled pools (rows from ab_bc_rows.json). Answers: is there a multiplier that
keeps 300ETF's thin TPs alive while retaining most 500/159915 FP kills?"""
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
MULTS = [2.5, 2.625, 2.75, 2.875, 3.0]
FOCUS = {
    "_p2016_2024": ("2016-01-01", "2024-01-01"),
    "_p2017_2025": ("2017-01-01", "2025-01-01"),
}
ETFS = ["300ETF", "500ETF", "159915ETF"]


def main():
    rows = json.load(open(HERE / "scratch" / "ab_bc_rows.json", encoding="utf-8"))
    df_cache = {}
    results = []  # (suffix, etf, tier, {mult: sortino})
    for suffix, (t0, t1) in FOCUS.items():
        pop = {(r["feature_name"], r["etf"], r["tier"]) for r in rows if r["suffix"] == suffix}
        by_etf = {}
        for name, etf, tier in pop:
            by_etf.setdefault(etf, []).append((name, tier))
        for etf in ETFS:
            if etf not in by_etf:
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
            tr_med = tstats[2]
            for col in H.FEATURES:
                train_df[col] = train_df[col].fillna(tr_med[col])
            # attempts for recipes/signs
            att = json.load(open(HERE / "data" / f"mining_attempts_{etf}_single{suffix}.json",
                                 encoding="utf-8"))
            att_by_name = {a["feature_name"]: a for a in att}
            y_tr = train_df["trade_return"].values.astype(np.float64)
            for name, tier in by_etf[etf]:
                a = att_by_name.get(name)
                if a is None:
                    continue
                try:
                    vals = H._feature_values(train_df, name, a.get("recipe"), *tstats)
                    if vals is None:
                        continue
                    pred = a.get("sign", 1) * vals
                    if np.std(pred) < 1e-12:
                        continue
                    pos = _tail_positions_binary(y_tr, pred, "single")
                    raw = pos * y_tr
                    abs_pos = np.abs(pos)
                    ss = {m: _sortino_annual(raw - abs_pos * COST * m) for m in MULTS}
                except Exception:
                    continue
                results.append((suffix, etf, tier, ss))
        print("done", suffix, "rows:", len(results), flush=True)

    for suffix in FOCUS:
        print(f"\n#### {suffix}")
        for etf in ETFS:
            sel = [r for r in results if r[0] == suffix and r[1] == etf]
            if not sel:
                continue
            tiers = {t: [r for r in sel if r[2] == t] for t in ["FP", "Median", "TP"]}
            n_fp, n_med, n_tp = len(tiers["FP"]), len(tiers["Median"]), len(tiers["TP"])
            print(f"  {etf:10s} pool(2.5-era): FP={n_fp} Med={n_med} TP={n_tp}")
            for m in MULTS:
                fk = sum(1 for r in tiers["FP"] if r[3][m] <= 0)
                mk = sum(1 for r in tiers["Median"] if r[3][m] <= 0)
                tk = sum(1 for r in tiers["TP"] if r[3][m] <= 0)
                print(f"    @{m*8:5.1f}bp  FP {fk:2d}/{n_fp:<2d}  Med {mk:3d}/{n_med:<3d}  TP {tk:2d}/{n_tp:<2d}")


if __name__ == "__main__":
    main()
