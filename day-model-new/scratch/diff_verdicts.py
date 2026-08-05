import json
import subprocess
from collections import Counter

r = subprocess.run(["git", "show",
                    "HEAD:day-model-new/data/mining_attempts_500ETF_single_p2017_2025.json"],
                   capture_output=True, text=True, encoding="utf-8")
old = json.loads(r.stdout)
new = json.load(open("data/mining_attempts_500ETF_single_TEST_NOGATE.json", encoding="utf-8"))

def norm(v):
    if v.startswith("ADMITTED_REPLACED"):
        return "ADMITTED_REPLACED"
    if v.startswith("DROPPED_REPLACED_BY"):
        return "DROPPED_REPLACED"
    return v

co = Counter(norm(a.get("verdict", "?")) for a in old)
cn = Counter(norm(a.get("verdict", "?")) for a in new)
keys = sorted(set(co) | set(cn))
print(f"{'verdict':28s} {'OLD':>7s} {'NEW':>7s} {'diff':>6s}")
for k in keys:
    print(f"{k:28s} {co.get(k,0):7d} {cn.get(k,0):7d} {cn.get(k,0)-co.get(k,0):+6d}")
print(f"{'TOTAL':28s} {len(old):7d} {len(new):7d}")
