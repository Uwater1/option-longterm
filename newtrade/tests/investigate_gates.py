#!/usr/bin/env python3
"""Quick investigation: what's wrong with day-model-new gates?"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "day-model-new" / "data"

for period in ["", "_p2015_2023", "_p2016_2024", "_p2017_2025"]:
    fpath = DATA / f"filter_effectiveness{period}.json"
    if not fpath.exists():
        continue
    d = json.load(open(fpath, encoding="utf-8"))
    label = period or "_original"
    print(f"\n{'='*80}")
    print(f"  PERIOD: {label}")
    print(f"{'='*80}")

    for etf in ["300ETF", "500ETF", "159915ETF"]:
        if etf not in d:
            continue
        gates = d[etf].get("single", {}).get("gate_effectiveness", {})
        if not gates:
            continue
        print(f"\n  {etf}:")
        for gname, gdata in gates.items():
            if gname.startswith("_"):
                continue
            n_rej = gdata.get("n_rejected", "?")
            fn = gdata.get("false_negative_rate", 0)
            mean_ic = gdata.get("mean_lock_ic", 0)
            mean_sr = gdata.get("mean_lock_sharpe", 0)
            print(f"    {gname:<45} rej={n_rej:>5} FN={fn:.1%} lock_ic={mean_ic:+.4f} lock_sr={mean_sr:+.3f}")
            # Show top rejects (features that were rejected but actually good)
            top_rej = gdata.get("top_rejects", [])
            if top_rej and fn > 0.2:
                for tr in top_rej[:3]:
                    print(f"      TOP REJECT: {tr['feature_name'][:55]} ic={tr['lock_ic']:.4f} sr={tr['lock_sharpe']:.3f}")

        adm = gates.get("_admitted_summary", {})
        if adm:
            print(f"    {'ADMITTED':<45} n={adm.get('n_admitted',0):>5} FP={adm.get('false_positive_rate',0):.1%} lock_ic={adm.get('mean_lock_ic',0):+.4f} lock_sr={adm.get('mean_lock_sharpe',0):+.3f}")

# Check: which old pool features are being rejected and by which gate?
print(f"\n\n{'='*80}")
print("  OLD POOL FEATURES: Rejection analysis (p2017_2025)")
print(f"{'='*80}")

import importlib.util, sys
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("old_pools", HERE / "data" / "old_admitted_pools_backup.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
OLD_POOLS = mod.POOLS

# Load trial ledgers to find rejection reasons
for etf in ["300ETF", "500ETF"]:
    old_pool = OLD_POOLS.get(etf, {}).get("single", [])
    if not old_pool:
        continue
    old_names = set(p["feature_name"] for p in old_pool)

    ledger_path = DATA / f"trial_ledger_{etf}_single_p2017_2025.json"
    if not ledger_path.exists():
        print(f"\n  {etf}: No trial ledger for p2017_2025")
        continue
    ledger = json.load(open(ledger_path, encoding="utf-8"))

    print(f"\n  {etf} (old pool = {len(old_names)} features):")
    found = 0
    not_found = []
    for feat_name in sorted(old_names):
        if feat_name in ledger:
            entry = ledger[feat_name]
            verdict = entry.get("verdict", "?")
            gate = entry.get("rejected_by", entry.get("gate", "?"))
            ic = entry.get("train_ic", entry.get("overall_ic", 0))
            print(f"    {feat_name[:60]:<62} verdict={verdict:<25} gate={gate}")
            found += 1
        else:
            not_found.append(feat_name)

    if not_found:
        print(f"\n    NOT IN LEDGER ({len(not_found)} features — not even evaluated!):")
        for f in not_found:
            print(f"      {f[:70]}")
