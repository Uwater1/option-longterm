"""Compare FP/Med/TP counts: old (git HEAD, pre-gate) vs new (gated rerun)."""
import json
import subprocess

SUFF = ["_p2015_2023", "_p2016_2024", "_p2017_2025", "_p2018_2026"]


def load(path, git=False):
    if git:
        r = subprocess.run(["git", "show", "HEAD:day-model-new/" + path],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def fmt(x):
    if not x:
        return "n/a"
    return "FP={:3d} Med={:3d} TP={:3d} rate={:.3f}".format(
        x["n_fp"], x["n_median"], x["n_tp"], x["fp_rate"])


for s in SUFF:
    path = f"data/filter_diagnosis{s}.json"
    new = load(path)
    old = load(path, git=True)
    if new is None:
        continue
    print("====", s)
    for etf in ["300ETF", "50ETF", "500ETF", "159915ETF"]:
        if etf not in new:
            continue
        for side, sn in new[etf].items():
            so = (old or {}).get(etf, {}).get(side, {})
            print(f"  {etf:10s} {side:7s} OLD[{fmt(so)}]  NEW[{fmt(sn)}]")
