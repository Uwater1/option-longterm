"""Compare Stage B (evaluate_concept) results old vs new for all periods/ETFs."""
import json
import subprocess

SUFF = ["_p2015_2023", "_p2016_2024", "_p2017_2025", "_p2018_2026"]
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]


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


def pick(d, keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d


def fmt_metrics(res):
    if not res:
        return "n/a"
    oos = res.get("oos_metrics") or {}
    tr = res.get("training_metrics") or {}
    n = len(res.get("features_selected") or [])
    def r(x):
        return "None" if x is None else f"{x:+.3f}"
    return "n={:3d} trainIC={} oosIC={} oosSharpe={} oosTailIC={}".format(
        n, r(tr.get("overall_ic")), r(oos.get("overall_ic")),
        r(oos.get("sharpe")), r(oos.get("tail_ic")))


for s in SUFF:
    print("====", s)
    for etf in ETFS:
        path = f"data/results_{etf}_single{s}.json"
        new = load(path)
        old = load(path, git=True)
        if new is None and old is None:
            continue
        print(f"  {etf:10s} OLD[{fmt_metrics(old)}]")
        print(f"  {'':10s} NEW[{fmt_metrics(new)}]")
    print()