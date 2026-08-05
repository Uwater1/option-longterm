"""Diff old (git HEAD) vs new selected pools, and map new-FP features to gate metrics."""
import json
import subprocess
import os

COMBOS = [
    ("300ETF", "_p2017_2025"),
    ("500ETF", "_p2017_2025"),
    ("300ETF", "_p2018_2026"),
    ("500ETF", "_p2018_2026"),
    ("300ETF", "_p2016_2024"),
]


def git_pool(path):
    r = subprocess.run(["git", "show", "HEAD:day-model-new/" + path],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


for etf, suffix in COMBOS:
    path = f"data/selected_pool_{etf}_single{suffix}.json"
    old = git_pool(path) or []
    new = json.load(open(path, encoding="utf-8"))
    old_names = {x["feature_name"] for x in old}
    new_names = {x["feature_name"] for x in new}
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)
    print(f"==== {etf}{suffix}: old={len(old_names)} new={len(new_names)} added={len(added)} removed={len(removed)}")

    # gate-rejected features from attempts
    att = json.load(open(f"data/mining_attempts_{etf}_single{suffix}.json", encoding="utf-8"))
    gate_rej = [a for a in att if a.get("verdict") in ("REJECTED_COST_STRESS", "REJECTED_BOOTSTRAP_CI")]
    gate_rej_names = {a["feature_name"] for a in gate_rej}
    print(f"  gate rejected {len(gate_rej)}: overlap-with-old-pool={len(gate_rej_names & old_names)} overlap-with-removed={len(gate_rej_names & set(removed))}")

    # new FP features: from filter_diagnosis
    diag = json.load(open(f"data/filter_diagnosis{suffix}.json", encoding="utf-8"))
    s = diag.get(etf, {}).get("single", {})
    fp_names = {x["feature_name"] for x in s.get("fp_features", [])}
    fp_new = fp_names & set(added)
    fp_kept = fp_names & (old_names & new_names)
    fp_old_gone = (fp_names & old_names) - new_names
    print(f"  FPs total={len(fp_names)}: NEW-in-pool={len(fp_new)} kept-old={len(fp_kept)} removed-old-FP={len(fp_old_gone)}")
    # gate metrics of the NEW FPs
    att_by_name = {a["feature_name"]: a for a in att}
    for fn in sorted(fp_new)[:10]:
        a = att_by_name.get(fn, {})
        ci = a.get("sortino_ci_low")
        ss = a.get("stress_sortino")
        cis = "None" if ci is None else f"{ci:.3f}"
        sss = "None" if ss is None else f"{ss:.3f}"
        print(f"    newFP {fn[:70]:70s} ci={cis} stress={sss}")
