#!/usr/bin/env python3
"""
Deep investigation: Why do admitted_pools.py and period pools diverge?
And: signal distribution analysis for threshold coupling.
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "day-model-new"))

from admitted_pools import POOLS
from utils import load_etf_dataset, build_pool_feature_matrix, expanding_zscore_numba

DAY_MODEL_DATA = REPO_ROOT / "day-model-new" / "data"

def load_json_pool(etf, suffix=""):
    fpath = DAY_MODEL_DATA / f"selected_pool_{etf}_single{suffix}.json"
    if not fpath.exists():
        return []
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)


def investigate_divergence(etf):
    print(f"\n{'═' * 90}")
    print(f"  POOL DIVERGENCE ANALYSIS: {etf}")
    print(f"{'═' * 90}")

    # 1. Compare admitted_pools.py vs selected_pool original
    admitted = POOLS.get(etf, {}).get("single", [])
    original = load_json_pool(etf, "")
    p2015_2023 = load_json_pool(etf, "_p2015_2023")
    p2016_2024 = load_json_pool(etf, "_p2016_2024")
    p2017_2025 = load_json_pool(etf, "_p2017_2025")

    admitted_names = [p["feature_name"] for p in admitted]
    original_names = [p["feature_name"] for p in original]
    p23_names = [p["feature_name"] for p in p2015_2023]
    p24_names = [p["feature_name"] for p in p2016_2024]
    p25_names = [p["feature_name"] for p in p2017_2025]

    print(f"\n  Pool sizes:")
    print(f"    admitted_pools.py:     {len(admitted)}")
    print(f"    selected_pool (orig):  {len(original)}")
    print(f"    p2015_2023:            {len(p2015_2023)}")
    print(f"    p2016_2024:            {len(p2016_2024)}")
    print(f"    p2017_2025:            {len(p2017_2025)}")

    # 2. Overlap matrix
    sets = {
        "admitted": set(admitted_names),
        "original": set(original_names),
        "p2015_2023": set(p23_names),
        "p2016_2024": set(p24_names),
        "p2017_2025": set(p25_names),
    }

    print(f"\n  Overlap matrix (shared features):")
    names_list = list(sets.keys())
    header = f"    {'':15}" + "".join(f"{n:>13}" for n in names_list)
    print(header)
    for n1 in names_list:
        row = f"    {n1:<15}"
        for n2 in names_list:
            overlap = len(sets[n1] & sets[n2])
            row += f"{overlap:>13}"
        print(row)

    # 3. Which admitted features appear in ANY period pool?
    print(f"\n  admitted_pools.py features → presence in period pools:")
    all_period = set(p23_names) | set(p24_names) | set(p25_names) | set(original_names)
    for feat in admitted_names:
        in_orig = "✓" if feat in sets["original"] else "✗"
        in_p23 = "✓" if feat in sets["p2015_2023"] else "✗"
        in_p24 = "✓" if feat in sets["p2016_2024"] else "✗"
        in_p25 = "✓" if feat in sets["p2017_2025"] else "✗"
        in_any = "✓" if feat in all_period else "✗"
        short = feat[:60]
        print(f"    {short:<62} orig={in_orig} p23={in_p23} p24={in_p24} p25={in_p25}")

    # 4. IC comparison for shared features
    shared_with_orig = sets["admitted"] & sets["original"]
    if shared_with_orig:
        print(f"\n  IC comparison for features in BOTH admitted & original (N={len(shared_with_orig)}):")
        admitted_ic = {p["feature_name"]: p["deflated_ic"] for p in admitted}
        original_ic = {p["feature_name"]: p["deflated_ic"] for p in original}
        for feat in sorted(shared_with_orig):
            a_ic = admitted_ic.get(feat, 0)
            o_ic = original_ic.get(feat, 0)
            print(f"    {feat[:55]:<57} admitted={a_ic:.4f}  original={o_ic:.4f}  Δ={a_ic-o_ic:+.4f}")

    # 5. Check candidate pool
    cand_file = REPO_ROOT / "day-model-new" / "mining" / f"candidates_{etf}_single.json"
    if cand_file.exists():
        with open(cand_file, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        cand_names = set(c["feature_name"] if isinstance(c, dict) else c for c in candidates)
        admitted_in_cand = sets["admitted"] & cand_names
        p23_in_cand = sets["p2015_2023"] & cand_names
        print(f"\n  Candidate pool size: {len(cand_names)}")
        print(f"    admitted features in candidates: {len(admitted_in_cand)}/{len(sets['admitted'])}")
        print(f"    p2015_2023 features in candidates: {len(p23_in_cand)}/{len(sets['p2015_2023'])}")
        missing_admitted = sets["admitted"] - cand_names
        if missing_admitted:
            print(f"    admitted features NOT in candidates ({len(missing_admitted)}):")
            for m in sorted(missing_admitted)[:5]:
                print(f"      {m[:70]}")
    else:
        print(f"\n  [WARNING] Candidate file not found: {cand_file}")


def investigate_signal_distribution(etf):
    """Analyze signal distribution differences that cause threshold coupling."""
    print(f"\n{'═' * 90}")
    print(f"  SIGNAL DISTRIBUTION ANALYSIS: {etf}")
    print(f"{'═' * 90}")

    df = load_etf_dataset(etf)
    full_trade_ret = df["trade_return"].values.astype(np.float64)
    dates = df["date"]

    admitted = POOLS.get(etf, {}).get("single", [])
    if not admitted:
        return

    # Build static signal
    X_s, signs_s, _ = build_pool_feature_matrix(df, admitted)
    Z_s = expanding_zscore_numba(X_s, burn_in=252, clip=3.0)
    Z_signed_s = Z_s * signs_s
    Z_comp_s = np.mean(Z_signed_s, axis=1)  # EW composite

    # Build yearly signals
    suffixes = {"2022": "", "2023": "_p2015_2023", "2024": "_p2016_2024", "2025": "_p2017_2025"}

    print(f"\n  Signal distribution (EW composite) per year:")
    print(f"  {'Year':<6} | {'Source':<10} | {'Mean':>8} {'Std':>8} {'P10':>8} {'P25':>8} {'P75':>8} {'P90':>8} | {'IC':>7}")
    print(f"  {'-'*6}-+-{'-'*10}-+-{'-'*56}-+-{'-'*7}")

    for y in [2022, 2023, 2024, 2025]:
        yr_mask = dates.dt.year == y
        if yr_mask.sum() < 20:
            continue

        # Static
        z_y = Z_comp_s[yr_mask.values]
        r_y = full_trade_ret[yr_mask.values]
        ic_s = np.corrcoef(z_y, r_y)[0, 1] if np.std(z_y) > 1e-12 else 0
        pcts = np.percentile(z_y, [10, 25, 75, 90])
        print(f"  {y:<6} | {'Static':<10} | {np.mean(z_y):>8.4f} {np.std(z_y):>8.4f} {pcts[0]:>8.3f} {pcts[1]:>8.3f} {pcts[2]:>8.3f} {pcts[3]:>8.3f} | {ic_s:>7.4f}")

        # Yearly
        pool_y = load_json_pool(etf, suffixes[str(y)])
        if pool_y and len(pool_y) >= 5:
            X_y, signs_y, _ = build_pool_feature_matrix(df, pool_y)
            Z_y = expanding_zscore_numba(X_y, burn_in=252, clip=3.0)
            Z_comp_y = np.mean(Z_y * signs_y, axis=1)
            z_yy = Z_comp_y[yr_mask.values]
            ic_y = np.corrcoef(z_yy, r_y)[0, 1] if np.std(z_yy) > 1e-12 else 0
            pcts_y = np.percentile(z_yy, [10, 25, 75, 90])
            print(f"  {'':6} | {'Yearly':<10} | {np.mean(z_yy):>8.4f} {np.std(z_yy):>8.4f} {pcts_y[0]:>8.3f} {pcts_y[1]:>8.3f} {pcts_y[2]:>8.3f} {pcts_y[3]:>8.3f} | {ic_y:>7.4f}")

    # Threshold-free comparison: signal IC × signal std = expected return per trade
    print(f"\n  Threshold-free quality metric: IC × Std(Z) = expected return magnitude")
    print(f"  {'Year':<6} | {'Static':>12} | {'Yearly':>12} | {'Winner':>10}")
    print(f"  {'-'*6}-+-{'-'*12}-+-{'-'*12}-+-{'-'*10}")
    for y in [2022, 2023, 2024, 2025]:
        yr_mask = dates.dt.year == y
        if yr_mask.sum() < 20:
            continue
        z_s = Z_comp_s[yr_mask.values]
        r_y = full_trade_ret[yr_mask.values]
        ic_s = np.corrcoef(z_s, r_y)[0, 1] if np.std(z_s) > 1e-12 else 0
        quality_s = abs(ic_s) * np.std(z_s)

        pool_y = load_json_pool(etf, suffixes[str(y)])
        if pool_y and len(pool_y) >= 5:
            X_y, signs_y, _ = build_pool_feature_matrix(df, pool_y)
            Z_y = expanding_zscore_numba(X_y, burn_in=252, clip=3.0)
            Z_comp_y = np.mean(Z_y * signs_y, axis=1)
            z_yy = Z_comp_y[yr_mask.values]
            ic_y = np.corrcoef(z_yy, r_y)[0, 1] if np.std(z_yy) > 1e-12 else 0
            quality_y = abs(ic_y) * np.std(z_yy)
            winner = "Yearly" if quality_y > quality_s else "Static"
            print(f"  {y:<6} | {quality_s:>12.5f} | {quality_y:>12.5f} | {winner:>10}")
        else:
            print(f"  {y:<6} | {quality_s:>12.5f} | {'N/A':>12} | {'Static':>10}")

    # Percentile-based threshold analysis
    print(f"\n  Percentile-based threshold (trade at |Z| > P75 of own distribution):")
    print(f"  This removes threshold coupling by normalizing to each signal's own distribution.")
    print(f"  {'Year':<6} | {'Static SR':>10} {'N_trades':>9} | {'Yearly SR':>10} {'N_trades':>9}")
    print(f"  {'-'*6}-+-{'-'*21}-+-{'-'*21}")

    for y in [2022, 2023, 2024, 2025]:
        yr_mask = dates.dt.year == y
        yr_idx = np.where(yr_mask.values)[0]
        if len(yr_idx) < 20:
            continue
        r_y = full_trade_ret[yr_idx]

        # Static: use expanding percentile (zero-lookahead)
        z_s_full = Z_comp_s
        results_s = []
        for i, t in enumerate(yr_idx):
            # P75 from history up to t
            hist = z_s_full[max(0, t-504):t]
            if len(hist) < 100:
                results_s.append(0.0)
                continue
            p75 = np.percentile(np.abs(hist), 75)
            if abs(z_s_full[t]) > p75:
                pos = np.sign(z_s_full[t])
                results_s.append(pos * r_y[i])
            else:
                results_s.append(0.0)
        results_s = np.array(results_s)
        active_s = results_s != 0
        sr_s = np.mean(results_s[active_s]) / np.std(results_s[active_s]) * np.sqrt(252) if active_s.sum() > 5 and np.std(results_s[active_s]) > 1e-12 else 0

        # Yearly
        pool_y = load_json_pool(etf, suffixes[str(y)])
        if pool_y and len(pool_y) >= 5:
            X_y, signs_y, _ = build_pool_feature_matrix(df, pool_y)
            Z_y = expanding_zscore_numba(X_y, burn_in=252, clip=3.0)
            Z_comp_y = np.mean(Z_y * signs_y, axis=1)
            results_y = []
            for i, t in enumerate(yr_idx):
                hist = Z_comp_y[max(0, t-504):t]
                if len(hist) < 100:
                    results_y.append(0.0)
                    continue
                p75 = np.percentile(np.abs(hist), 75)
                if abs(Z_comp_y[t]) > p75:
                    pos = np.sign(Z_comp_y[t])
                    results_y.append(pos * r_y[i])
                else:
                    results_y.append(0.0)
            results_y = np.array(results_y)
            active_y = results_y != 0
            sr_y = np.mean(results_y[active_y]) / np.std(results_y[active_y]) * np.sqrt(252) if active_y.sum() > 5 and np.std(results_y[active_y]) > 1e-12 else 0
            print(f"  {y:<6} | {sr_s:>10.3f} {active_s.sum():>9} | {sr_y:>10.3f} {active_y.sum():>9}")
        else:
            print(f"  {y:<6} | {sr_s:>10.3f} {active_s.sum():>9} | {'N/A':>10} {'N/A':>9}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all")
    args = parser.parse_args()
    etfs = ["300ETF", "500ETF", "159915ETF"] if args.etf == "all" else [args.etf]

    for etf in etfs:
        investigate_divergence(etf)
        investigate_signal_distribution(etf)


if __name__ == "__main__":
    main()
