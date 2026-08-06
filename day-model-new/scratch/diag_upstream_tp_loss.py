"""Upstream gate TP-loss diagnosis (option 3).

For every feature rejected by an upstream gate (B1-B4), compute:
  - OOS tier (TP/Median/FP via lock IC & Sharpe, forced-sign positions)
  - would it have passed G7 (stress Sortino @ COST_STRESS_MULT) ?
  - for TPs passing G7: would it also pass G4 (bootstrap CI) ?

Per-gate output:
  TP_loss   = TPs killed that would have PASSED the full robustness gate
                (pure loss: redundant gate killing supply the Sortino gates keep)
  FP_redund = FPs killed that would have FAILED the robustness gate anyway
                (the gate adds nothing over the Sortino gates for these)
  FP_unique = FPs killed that would have PASSED the robustness gate
                (the gate's genuine unique FP contribution)
"""
import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "mining"))
sys.path.insert(0, str(HERE.parent / "day-model"))

import research_gate_ab_test as H
from select_features import (_tail_positions_binary, _sortino_annual,
                             _bootstrap_sortino_ci, COST_STRESS_MULT)

COST = 0.0008
ETFS = ["300ETF"]
WINDOWS = {
    "_p2016_2024": ("2016-01-01", "2024-01-01"),
    "_p2017_2025": ("2017-01-01", "2025-01-01"),
}
VERDICTS = [
    "REJECTED_SPLIT_HALF", "REJECTED_ROLLING_GUARD", "REJECTED_TEMPORAL",
    "REJECTED_FDR_GATE", "REJECTED_ADMISSION_FLOOR", "REJECTED_HIGH_YEARLY_IC_CV",
    "REJECTED_STABILITY_GATE", "REJECTED_NEGATIVE_REGIMES",
    "REJECTED_REGIME_UNIFORMITY", "REJECTED_QUALITY_GATE",
]


def main():
    for suffix, (t0, t1) in WINDOWS.items():
        for etf in ETFS:
            apath = HERE / "data" / f"mining_attempts_{etf}_single{suffix}.json"
            att = json.load(open(apath, encoding="utf-8"))
            pool = [a for a in att if a.get("verdict") in VERDICTS]
            path = HERE.parent / "day-model" / "data" / f"features_{etf}.parquet"
            df = H.pd.read_parquet(path)
            if "date" not in df.columns:
                df = df.reset_index()
            df["date"] = H.pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
            for col in H.FEATURES:
                df[col] = df[col].ffill()
            train_df, lock_df, tstats = H.prep_split(df, t0, t1)
            tr_med = tstats[2]
            for col in H.FEATURES:
                train_df[col] = train_df[col].fillna(tr_med[col])
                lock_df[col] = lock_df[col].fillna(tr_med[col])
            y_tr = train_df["trade_return"].values.astype(np.float64)
            y_lk = lock_df["trade_return"].values.astype(np.float64)

            stats = defaultdict(lambda: {"n": 0, "TP": 0, "Median": 0, "FP": 0,
                                         "TP_pass_robust": 0, "TP_pass_g7": 0,
                                         "FP_fail_robust": 0, "FP_pass_robust": 0,
                                         "TP_loss_names": []})
            done = 0
            for item in pool:
                v = item["verdict"]
                st = stats[v]
                st["n"] += 1
                try:
                    name = item["feature_name"]
                    sign = item.get("sign", 1)
                    recipe = item.get("recipe")
                    vals_tr = H._feature_values(train_df, name, recipe, *tstats)
                    if vals_tr is None:
                        continue
                    pred_tr = sign * vals_tr
                    if np.std(pred_tr) < 1e-12:
                        continue
                    # train: G7 stress sortino @ current mult
                    pos = _tail_positions_binary(y_tr, pred_tr, "single")
                    raw = pos * y_tr
                    abs_pos = np.abs(pos)
                    stress = _sortino_annual(raw - abs_pos * COST * COST_STRESS_MULT)
                    pass_g7 = stress > 0
                    # OOS label
                    vals_lk = H._feature_values(lock_df, name, recipe, *tstats)
                    if vals_lk is None:
                        continue
                    pred_lk = sign * vals_lk
                    if np.std(pred_lk) < 1e-12 or len(y_lk) < 30:
                        continue
                    lock_ic = H._spearman(y_lk, pred_lk)
                    pos_lk = _tail_positions_binary(y_lk, pred_lk, "single")
                    lk_ret = pos_lk * y_lk - np.abs(pos_lk) * COST
                    lock_sharpe = H._sharpe(lk_ret)
                    tier = "FP" if lock_ic <= 0 else ("Median" if lock_sharpe <= 0 else "TP")
                except Exception:
                    continue
                st[tier] += 1
                if tier == "FP":
                    if pass_g7:
                        st["FP_pass_robust"] += 1
                    else:
                        st["FP_fail_robust"] += 1
                elif tier == "TP" and pass_g7:
                    st["TP_pass_g7"] += 1
                    # full robustness = G7 AND G4
                    rng = np.random.default_rng(42)
                    ci = _bootstrap_sortino_ci(raw - abs_pos * COST, rng)
                    if ci > 0:
                        st["TP_pass_robust"] += 1
                        if len(st["TP_loss_names"]) < 8:
                            st["TP_loss_names"].append(f"{name[:55]}(s={stress:.2f})")
                done += 1
                if done % 200 == 0:
                    print(f"  {etf}{suffix}: {done}/{len(pool)}", flush=True)

            print(f"\n#### {etf} {suffix}  (mult={COST_STRESS_MULT})")
            hdr = f"{'gate':28s} {'n':>5s} {'TP':>4s} {'Med':>4s} {'FP':>4s} | {'TPloss':>6s} {'TP>G7':>5s} {'FPred':>5s} {'FPuniq':>6s}"
            print(hdr)
            for v in VERDICTS:
                if v not in stats:
                    continue
                s = stats[v]
                print(f"{v.replace('REJECTED_',''):28s} {s['n']:5d} {s['TP']:4d} {s['Median']:4d} {s['FP']:4d} | "
                      f"{s['TP_pass_robust']:6d} {s['TP_pass_g7']:5d} {s['FP_fail_robust']:5d} {s['FP_pass_robust']:6d}")
            for v in VERDICTS:
                if v in stats and stats[v]["TP_loss_names"]:
                    print(f"  {v} example TP losses: " + "; ".join(stats[v]["TP_loss_names"][:5]))


if __name__ == "__main__":
    main()
