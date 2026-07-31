#!/usr/bin/env python3
"""Regenerate day-model-new/admitted_pools.py from pipeline JSON output."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]

pools = {}
for etf in ETFS:
    single_path = DATA / f"selected_pool_{etf}_single.json"
    feats = json.load(open(single_path, encoding="utf-8")) if single_path.exists() else []
    pools[etf] = {"single": feats, "long": [], "short": []}
    print(f"  {etf}: {len(feats)} single features")

# Write admitted_pools.py
out = HERE / "admitted_pools.py"
with open(out, "w", encoding="utf-8") as f:
    f.write('"""\n')
    f.write("Central registry of admitted feature pools across all ETFs and trading sides.\n")
    f.write("Serves as the single source of truth for downstream newtrade execution.\n\n")
    f.write("Pool sources: day-model-new pipeline output (original training vintage, pre-2022).\n")
    f.write("Regenerated: 2026-07-31 from selected_pool_{ETF}_single.json\n")
    f.write('"""\n\n')
    f.write("POOLS = ")
    f.write(json.dumps(pools, indent=4))
    f.write("\n")

print(f"\nWritten {out} ({out.stat().st_size:,} bytes)")
