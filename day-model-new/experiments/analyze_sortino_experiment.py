#!/usr/bin/env python3
"""Analyze sortino fix experiment results - find unified config."""
import json
import numpy as np
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.load(open(HERE / "data" / "sortino_fix_experiment.json"))
results = data["results"]

# Aggregate across all ETF/sides for each (config, percentile)
agg = defaultdict(lambda: {"tp_adm": 0, "tp_total": 0, "fp_adm": 0, "fp_total": 0})

for r in results:
    key = (r["denom_mode"], r["sortino_weight"], r["percentile"])
    agg[key]["tp_adm"] += r["tp_admitted"]
    agg[key]["tp_total"] += r["tp_total"]
    agg[key]["fp_adm"] += r["fp_admitted"]
    agg[key]["fp_total"] += r["fp_total"]

print("=" * 95)
print("  AGGREGATED RESULTS (all ETF/sides pooled)")
print("=" * 95)
hdr = f"{'Config':<25} {'Pct':>4} {'TP_Adm':>7} {'TP_Tot':>7} {'TP_Rec':>7} {'FP_Adm':>7} {'FP_Tot':>7} {'FP_Rate':>8} {'Net':>5}"
print(hdr)
print("-" * 95)

for key in sorted(agg.keys(), key=lambda k: (k[0], k[1], k[2])):
    dm, sw, pct = key
    v = agg[key]
    tp_rec = v["tp_adm"] / max(1, v["tp_total"])
    fp_rate = v["fp_adm"] / max(1, v["fp_total"])
    net = v["tp_adm"] - v["fp_adm"]
    label = f"{dm}, w={sw:.1f}"
    print(f"{label:<25} {pct:>4} {v['tp_adm']:>7} {v['tp_total']:>7} {tp_rec:>7.1%} {v['fp_adm']:>7} {v['fp_total']:>7} {fp_rate:>8.1%} {net:>5}")

# Find unified config: maximize net (TP - FP) at 95th percentile tier
print("\n" + "=" * 95)
print("  UNIFIED CONFIG SELECTION (conservative: prioritize low FP rate)")
print("=" * 95)

# Baseline: current at 95th
baseline_key = ("n_tail", 0.3, 95)
bl = agg[baseline_key]
bl_fp_rate = bl["fp_adm"] / max(1, bl["fp_total"])
bl_tp_rec = bl["tp_adm"] / max(1, bl["tp_total"])
print(f"\n  Baseline (n_tail, w=0.3, pct=95): TP recall={bl_tp_rec:.1%}, FP rate={bl_fp_rate:.1%}, Net={bl['tp_adm']-bl['fp_adm']}")

# Candidate configs at 95th percentile (the production tier for conditional combos)
print("\n  Fixed configs at 95th percentile:")
candidates = []
for sw in [0.3, 0.65, 0.70, 0.75, 0.80, 0.85]:
    key = ("n", sw, 95)
    v = agg[key]
    tp_rec = v["tp_adm"] / max(1, v["tp_total"])
    fp_rate = v["fp_adm"] / max(1, v["fp_total"])
    net = v["tp_adm"] - v["fp_adm"]
    candidates.append({"weight": sw, "tp_recall": tp_rec, "fp_rate": fp_rate, "net": net,
                       "tp_adm": v["tp_adm"], "fp_adm": v["fp_adm"]})
    print(f"    w={sw:.1f}: TP recall={tp_rec:.1%}, FP rate={fp_rate:.1%}, Net={net:+d}")

# Selection criteria:
# 1. FP rate must be <= baseline FP rate (don't let more FP through)
# 2. Among those, maximize TP recall (let more TP through)
# 3. If tied, prefer lower weight (simpler, less Sortino-dependent)
print("\n  Selection: FP rate <= baseline, then max TP recall, then min weight")
acceptable = [c for c in candidates if c["fp_rate"] <= bl_fp_rate + 0.01]  # 1% tolerance
if not acceptable:
    acceptable = candidates
    print("  WARNING: No config meets FP constraint. Picking best net.")

best = max(acceptable, key=lambda c: (c["tp_recall"], -c["fp_rate"], -c["weight"]))
print(f"\n  >>> RECOMMENDED UNIFIED: denom=n, weight={best['weight']:.1f}, percentile=95 <<<")
print(f"      TP recall: {bl_tp_rec:.1%} -> {best['tp_recall']:.1%}")
print(f"      FP rate:   {bl_fp_rate:.1%} -> {best['fp_rate']:.1%}")
print(f"      Net:       {bl['tp_adm']-bl['fp_adm']} -> {best['net']}")

# Also check per-ETF breakdown for the recommended config
print("\n" + "=" * 95)
print(f"  PER-ETF BREAKDOWN: fixed w={best['weight']:.1f} @ 95th percentile")
print("=" * 95)
per_etf = defaultdict(lambda: {"tp_adm": 0, "tp_total": 0, "fp_adm": 0, "fp_total": 0})
for r in results:
    if r["denom_mode"] == "n" and r["sortino_weight"] == best["weight"] and r["percentile"] == 95:
        k = f"{r['etf']}_{r['side']}"
        per_etf[k]["tp_adm"] += r["tp_admitted"]
        per_etf[k]["tp_total"] += r["tp_total"]
        per_etf[k]["fp_adm"] += r["fp_admitted"]
        per_etf[k]["fp_total"] += r["fp_total"]

# Also get baseline per ETF
per_etf_bl = defaultdict(lambda: {"tp_adm": 0, "tp_total": 0, "fp_adm": 0, "fp_total": 0})
for r in results:
    if r["denom_mode"] == "n_tail" and r["sortino_weight"] == 0.3 and r["percentile"] == 95:
        k = f"{r['etf']}_{r['side']}"
        per_etf_bl[k]["tp_adm"] += r["tp_admitted"]
        per_etf_bl[k]["tp_total"] += r["tp_total"]
        per_etf_bl[k]["fp_adm"] += r["fp_admitted"]
        per_etf_bl[k]["fp_total"] += r["fp_total"]

print(f"  {'ETF_Side':<20} {'BL TP/FP':>12} {'New TP/FP':>12} {'BL FP%':>8} {'New FP%':>8}")
print("  " + "-" * 65)
for k in sorted(per_etf.keys()):
    v = per_etf[k]
    b = per_etf_bl[k]
    bl_fpr = b["fp_adm"] / max(1, b["fp_total"])
    new_fpr = v["fp_adm"] / max(1, v["fp_total"])
    print(f"  {k:<20} {b['tp_adm']:>3}/{b['fp_adm']:>3}      {v['tp_adm']:>3}/{v['fp_adm']:>3}      {bl_fpr:>7.0%} {new_fpr:>7.0%}")
