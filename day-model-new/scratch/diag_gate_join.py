"""Diagnostic: join Robustness-Gate metrics (default window rerun) with OOS tiers
from filter_diagnosis, and sweep thresholds on sortino_ci_low / stress_sortino."""
import json
import os
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

diag = json.load(open(os.path.join(DATA, "filter_diagnosis.json"), encoding="utf-8"))
rows = []
for etf, sides in diag.items():
    for side, s in sides.items():
        tier_of = {}
        for tier in ("FP", "Median", "TP"):
            for it in s.get(tier.lower() + "_features", []):
                tier_of[(it["feature_name"], it.get("sign", 1))] = tier
        apath = os.path.join(DATA, f"mining_attempts_{etf}_{side}.json")
        if not os.path.exists(apath):
            continue
        att = json.load(open(apath, encoding="utf-8"))
        for a in att:
            if not a.get("verdict", "").startswith("ADMITTED"):
                continue
            key = (a["feature_name"], a.get("sign", 1))
            if key not in tier_of:
                continue
            ci = a.get("sortino_ci_low")
            ss = a.get("stress_sortino")
            if ci is None:
                continue
            rows.append((etf, tier_of[key], ci, ss if ss is not None else np.nan))

print("joined default-window admitted:", len(rows))
tiers = {t: [r for r in rows if r[1] == t] for t in ["FP", "Median", "TP"]}
for t, rs in tiers.items():
    ci = np.array([r[2] for r in rs])
    ss = np.array([r[3] for r in rs])
    print(f"{t:6s} n={len(rs):3d} ci: p10={np.percentile(ci,10):.3f} p25={np.percentile(ci,25):.3f} med={np.median(ci):.3f} | stress med={np.nanmedian(ss):.3f}")

n_fp, n_med, n_tp = len(tiers["FP"]), len(tiers["Median"]), len(tiers["TP"])
print(f"\nFP rate before any gate: {n_fp/(n_fp+n_med+n_tp):.3f}")
print("\nThreshold sweep on ci_low: reject if ci_low < t")
print(f"{'t':>6} {'FPkill':>8} {'Medkill':>9} {'TPkill':>8} {'FPrate':>8}")
for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]:
    fk = sum(1 for r in tiers["FP"] if r[2] < t)
    mk = sum(1 for r in tiers["Median"] if r[2] < t)
    tk = sum(1 for r in tiers["TP"] if r[2] < t)
    fr = (n_fp - fk) / max(1, (n_fp - fk + n_med - mk + n_tp - tk))
    print(f"{t:6.2f} {fk:>3d}/{n_fp:<3d} {mk:>3d}/{n_med:<3d}  {tk:>3d}/{n_tp:<3d}  {fr:8.3f}")

print("\nThreshold sweep on stress_sortino: reject if stress < t")
print(f"{'t':>6} {'FPkill':>8} {'Medkill':>9} {'TPkill':>8} {'FPrate':>8}")
for t in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    fk = sum(1 for r in tiers["FP"] if r[3] < t)
    mk = sum(1 for r in tiers["Median"] if r[3] < t)
    tk = sum(1 for r in tiers["TP"] if r[3] < t)
    fr = (n_fp - fk) / max(1, (n_fp - fk + n_med - mk + n_tp - tk))
    print(f"{t:6.2f} {fk:>3d}/{n_fp:<3d} {mk:>3d}/{n_med:<3d}  {tk:>3d}/{n_tp:<3d}  {fr:8.3f}")

# Combined: reject if ci_low < t1 OR stress < t2
print("\nCombined (ci<t1 OR stress<t2):")
for t1, t2 in [(0.2, 0.4), (0.3, 0.5), (0.5, 0.8), (0.3, 0.0), (0.0, 0.5)]:
    fk = sum(1 for r in tiers["FP"] if r[2] < t1 or r[3] < t2)
    mk = sum(1 for r in tiers["Median"] if r[2] < t1 or r[3] < t2)
    tk = sum(1 for r in tiers["TP"] if r[2] < t1 or r[3] < t2)
    fr = (n_fp - fk) / max(1, (n_fp - fk + n_med - mk + n_tp - tk))
    print(f"ci<{t1:.1f} OR stress<{t2:.1f}: FP {fk}/{n_fp}  Med {mk}/{n_med}  TP {tk}/{n_tp}  FPrate={fr:.3f}")

# Detail: which FPs exist and their metrics
print("\nFP detail:")
for r in sorted(tiers["FP"], key=lambda x: x[2]):
    print(f"  {r[0]:12s} ci={r[2]:.3f} stress={r[3]:.3f}")
