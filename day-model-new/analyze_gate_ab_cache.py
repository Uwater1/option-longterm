#!/usr/bin/env python3
"""Deeper aggregation of gate_ab_cache: strict-label view (bad = lock IC<=0 OR
Sharpe<=0, i.e. FP + median-fail), combined-gate unions, and per-combo breakdown.

Usage:
  python day-model-new/analyze_gate_ab_cache.py [--population admitted|preb4]
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent

# Single-gate reject predicates (threshold chosen from first sweep)
def rej_psr09(r):   return r["psr"] < 0.90
def rej_psr08(r):   return r["psr"] < 0.80
def rej_boot(r):    return r["sortino_ci_low"] is not None and r["sortino_ci_low"] <= 0.0
def rej_stress(r):  return r["stress_sortino"] <= 0.0
def rej_regime1(r): return r["n_neg_regimes"] is not None and r["n_neg_regimes"] > 1
def rej_skew(r):    return r["skew"] is not None and r["skew"] < -0.25
def rej_payoff(r):  return r["payoff"] < 0.8

SINGLE_GATES = {
    "G1 PSR<0.80": rej_psr08,
    "G1 PSR<0.90": rej_psr09,
    "G4 bootCI<=0": rej_boot,
    "G7 stress<=0": rej_stress,
    "G8 negreg>1": rej_regime1,
    "G2 skew<-0.25": rej_skew,
    "G5 payoff<0.8": rej_payoff,
}

COMBOS_GATES = {
    "G4+G7":                lambda r: rej_boot(r) or rej_stress(r),
    "G4+G7+G1(0.9)":        lambda r: rej_boot(r) or rej_stress(r) or rej_psr09(r),
    "G4+G7+G8":             lambda r: rej_boot(r) or rej_stress(r) or rej_regime1(r),
    "G4+G7+G1(0.9)+G8":     lambda r: rej_boot(r) or rej_stress(r) or rej_psr09(r) or rej_regime1(r),
}


def stats(rows, pred, strict):
    """strict: bad = FP or Median; else bad = FP only."""
    def is_bad(r):
        if r["tier"] == "FP":
            return True
        return strict and r["tier"] == "Median"
    n_bad = sum(1 for r in rows if is_bad(r))
    n_tp = sum(1 for r in rows if r["tier"] == "TP")
    rej = [r for r in rows if pred(r)]
    keep = [r for r in rows if not pred(r)]
    bad_killed = sum(1 for r in rej if is_bad(r))
    tp_killed = sum(1 for r in rej if r["tier"] == "TP")
    bad_after = sum(1 for r in keep if is_bad(r))
    base_rate = n_bad / len(rows) if rows else 0.0
    after_rate = bad_after / len(keep) if keep else 0.0
    return {
        "n": len(rows), "n_bad": n_bad, "n_tp": n_tp,
        "bad_kill": bad_killed / n_bad if n_bad else 0.0,
        "tp_kill": tp_killed / n_tp if n_tp else 0.0,
        "base_rate": base_rate, "after_rate": after_rate,
        "n_rej": len(rej),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", choices=["admitted", "preb4"], default="admitted")
    args = parser.parse_args()

    cache_file = HERE / "data" / f"gate_ab_cache_{args.population}.json"
    with open(cache_file, "r", encoding="utf-8") as f:
        combos = json.load(f)

    all_rows = []
    for c in combos:
        for r in c["rows"]:
            r2 = dict(r)
            r2["_combo"] = f"{c['etf']}/{c['side']}{c['suffix']}"
            r2["_suffix"] = c["suffix"]
            all_rows.append(r2)

    focus = [r for r in all_rows if r["_suffix"] in ("_p2016_2024", "_p2017_2025", "_p2018_2026")]

    for label, rows in [("ALL WINDOWS", all_rows), ("FOCUS PERIODS", focus)]:
        for strict_label, strict in [("tier-FP only", False), ("strict (FP + median-fail)", True)]:
            print(f"\n{'='*100}")
            print(f"{label} | label = {strict_label} | N={len(rows)}")
            print(f"{'='*100}")
            print(f"{'gate':<22} {'rej':>5} {'bad-kill':>9} {'TP-kill':>8} {'base bad%':>13} {'after bad%':>11}")
            for gname, pred in {**SINGLE_GATES, **COMBOS_GATES}.items():
                s = stats(rows, pred, strict)
                print(f"{gname:<22} {s['n_rej']:>5} {s['bad_kill']:>8.1%} {s['tp_kill']:>8.1%} "
                      f"{s['base_rate']:>12.1%} {s['after_rate']:>11.1%}")

    # Per-combo breakdown for the recommended stack (G4+G7), strict label
    print(f"\n{'='*100}")
    print("Per-combo effect of G4+G7 (strict label: bad = lock IC<=0 or Sharpe<=0)")
    print(f"{'='*100}")
    print(f"{'combo':<32} {'N':>4} {'bad':>4} {'TP':>4} {'bad-kill':>9} {'TP-kill':>8} {'base%':>7} {'after%':>8}")
    for c in combos:
        tag = f"{c['etf']}/{c['side']}{c['suffix']}"
        rows = c["rows"]
        s = stats(rows, COMBOS_GATES["G4+G7"], True)
        if s["n_bad"] == 0:
            continue
        print(f"{tag:<32} {s['n']:>4} {s['n_bad']:>4} {s['n_tp']:>4} {s['bad_kill']:>8.1%} "
              f"{s['tp_kill']:>8.1%} {s['base_rate']:>6.1%} {s['after_rate']:>8.1%}")

    # Discriminability: which train metrics separate FP vs TP in focus windows?
    print(f"\n{'='*100}")
    print("FOCUS PERIODS — train-metric distributions: FP vs TP (can ANY train signal see the FPs?)")
    print(f"{'='*100}")
    METRICS = ["train_ic", "train_sharpe", "train_sortino", "psr", "skew", "exkurt",
               "sortino_ci_low", "payoff", "concentration", "stress_sortino", "n_neg_regimes"]
    fp_rows = [r for r in focus if r["tier"] == "FP"]
    tp_rows = [r for r in focus if r["tier"] == "TP"]
    print(f"{'metric':<20} {'FP mean':>10} {'FP med':>10} {'TP mean':>10} {'TP med':>10} {'sep':>7}")
    import statistics
    for m in METRICS:
        fv = [r[m] for r in fp_rows if r.get(m) is not None]
        tv = [r[m] for r in tp_rows if r.get(m) is not None]
        if len(fv) < 5 or len(tv) < 5:
            continue
        fm, tm = statistics.mean(fv), statistics.mean(tv)
        fmed, tmed = statistics.median(fv), statistics.median(tv)
        pooled = (statistics.stdev(fv + tv)) or 1e-12
        sep = abs(tm - fm) / pooled
        print(f"{m:<20} {fm:>10.3f} {fmed:>10.3f} {tm:>10.3f} {tmed:>10.3f} {sep:>6.2f}\u03c3")
    # Same view on the two user-flagged worst windows
    for suff in ("_p2017_2025", "_p2018_2026"):
        sub = [r for r in all_rows if r["_suffix"] == suff]
        fps = [r for r in sub if r["tier"] == "FP"]
        tps = [r for r in sub if r["tier"] == "TP"]
        if len(fps) < 5 or len(tps) < 5:
            continue
        print(f"\n  window {suff}: FP={len(fps)} TP={len(tps)}")
        print(f"  {'metric':<20} {'FP med':>10} {'TP med':>10} {'sep':>7}")
        import statistics
        for m in METRICS:
            fv = [r[m] for r in fps if r.get(m) is not None]
            tv = [r[m] for r in tps if r.get(m) is not None]
            if len(fv) < 5 or len(tv) < 5:
                continue
            fmed, tmed = statistics.median(fv), statistics.median(tv)
            pooled = (statistics.stdev(fv + tv)) or 1e-12
            sep = abs(statistics.mean(tv) - statistics.mean(fv)) / pooled
            print(f"  {m:<20} {fmed:>10.3f} {tmed:>10.3f} {sep:>6.2f}\u03c3")


if __name__ == "__main__":
    main()
