#!/usr/bin/env python3
"""
Selective pool update: Use new pipeline pools ONLY where they win.
- 159915ETF: Use p2017_2025 (new wins)
- 300ETF, 500ETF: Keep old vintage (old wins)
- 50ETF, 588000ETF: Keep whatever is available
"""
import json, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DATA_DIR = REPO_ROOT / "day-model-new" / "data"
OUTPUT = REPO_ROOT / "day-model-new" / "admitted_pools.py"

# Load old pools
spec = importlib.util.spec_from_file_location("old_pools", HERE / "data" / "old_admitted_pools_backup.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
OLD_POOLS = mod.POOLS

# Decision: which ETFs use new pipeline vs old
# Updated 2026-07-30: 159915ETF migrates to p2018_2026 (approved by migration protocol)
USE_NEW_PIPELINE = {"159915ETF"}
NEW_PERIOD_SUFFIX = "_p2018_2026"  # Latest approved period
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]
SIDES = ["single", "long", "short"]


def load_period_pool(etf, side, suffix=None):
    if suffix is None:
        suffix = NEW_PERIOD_SUFFIX
    fpath = DATA_DIR / f"selected_pool_{etf}_{side}{suffix}.json"
    if fpath.exists():
        with open(fpath, "r", encoding="utf-8") as f:
            pool = json.load(f)
        if pool:
            return pool, f"selected_pool_{etf}_{side}{suffix}.json"
    # Fallback to original
    fpath2 = DATA_DIR / f"selected_pool_{etf}_{side}.json"
    if fpath2.exists():
        with open(fpath2, "r", encoding="utf-8") as f:
            pool = json.load(f)
        if pool:
            return pool, f"selected_pool_{etf}_{side}.json"
    return [], "none"


def main():
    pools = {}
    for etf in ETFS:
        pools[etf] = {}
        for side in SIDES:
            if etf in USE_NEW_PIPELINE:
                pool, source = load_period_pool(etf, side)
                if pool:
                    pools[etf][side] = pool
                    print(f"  {etf}/{side}: {len(pool)} features from {source} [NEW]")
                else:
                    pools[etf][side] = OLD_POOLS.get(etf, {}).get(side, [])
                    print(f"  {etf}/{side}: {len(pools[etf][side])} features from old [FALLBACK]")
            else:
                pools[etf][side] = OLD_POOLS.get(etf, {}).get(side, [])
                print(f"  {etf}/{side}: {len(pools[etf][side])} features from old [KEEP]")

    # Generate admitted_pools.py
    lines = [
        '"""',
        'Central registry of admitted feature pools across all ETFs and trading sides.',
        'Serves as the single source of truth for downstream newtrade execution.',
        '',
        'Pool sources (validated 2026-07-30 via research_pool_comparison.py):',
        '  - 159915ETF: p2017_2025 pipeline output (new wins +0.44 Sharpe)',
        '  - 300ETF, 500ETF: Original vintage (old wins, features not in current candidates)',
        '  - 50ETF, 588000ETF: Original (insufficient features for trading)',
        '',
        'Regenerate with: python newtrade/regenerate_admitted_pools.py',
        '"""',
        '',
        'POOLS = {',
    ]

    for etf in ETFS:
        lines.append(f'    "{etf}": {{')
        for side in SIDES:
            pool = pools[etf][side]
            if not pool:
                lines.append(f'        "{side}": [],')
            else:
                lines.append(f'        "{side}": [')
                for item in pool:
                    lines.append('            {')
                    lines.append(f'                "feature_name": "{item["feature_name"]}",')
                    lines.append(f'                "sign": {item["sign"]},')
                    lines.append(f'                "overall_ic": {item["overall_ic"]},')
                    lines.append(f'                "deflated_ic": {item["deflated_ic"]},')
                    lines.append(f'                "ic_ir": {item["ic_ir"]},')
                    lines.append(f'                "monotonicity": {item["monotonicity"]},')
                    if "recipe" in item:
                        r = item["recipe"]
                        recipe_parts = [f'"op": "{r["op"]}"']
                        for key in ["feature_a", "feature_b", "feature_c", "feature_cond", "feature_cond2"]:
                            if key in r:
                                recipe_parts.append(f'"{key}": "{r[key]}"')
                        lines.append(f'                "recipe": {{{", ".join(recipe_parts)}}}')
                    lines.append('            },')
                lines.append('        ],')
        lines.append('    },')
    lines.append('}')
    lines.append('')
    lines.append('def get_admitted_pool(etf: str, side: str = "single"):')
    lines.append('    """Return admitted feature pool list for given ETF and side."""')
    lines.append('    return POOLS.get(etf, {}).get(side, [])')
    lines.append('')

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    total = sum(len(pools[e][s]) for e in ETFS for s in SIDES)
    print(f"\n  Written to: {OUTPUT}")
    print(f"  Total features: {total}")


if __name__ == "__main__":
    main()
