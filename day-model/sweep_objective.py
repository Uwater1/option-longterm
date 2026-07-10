"""Sweep V5 objective variants: ratio_type × sharpe_weight × embargo_days.

Trains all 5 ETFs × 3 sides for each config, then compares OOS IC and
tail metrics against the baseline (default sharpe, weight=0.40, embargo=10).

Usage:
    python day-model/sweep_objective.py                  # Run all configs
    python day-model/sweep_objective.py --configs sortino  # Run specific config
    python day-model/sweep_objective.py --report         # Report only (no training)
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from itertools import product

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_DIR = HERE / "data"

# ── Sweep configs ──────────────────────────────────────────────────
# Each: (label, extra_args_list)
# Baseline (no extra args) is always included as reference.
CONFIGS = {
    "baseline":   [],
    "sortino":     ["--ratio-type", "sortino"],
    "sw0.20":     ["--sharpe-weight", "0.20"],
    "sw0.30":     ["--sharpe-weight", "0.30"],
    "sw0.50":     ["--sharpe-weight", "0.50"],
    "emb20":      ["--embargo-days", "20"],
    "sortino+sw50": ["--ratio-type", "sortino", "--sharpe-weight", "0.50"],
}


def run_config(label: str, extra_args: list, trials: int, etf: str):
    """Run train_model.py with given args for all ETFs."""
    cmd = [
        sys.executable, str(HERE / "train_model.py"),
        "-e", etf,
        "--trials", str(trials),
        "--no-cache",
    ] + extra_args

    print(f"\n{'='*80}")
    print(f"[SWEEP] Config: {label}")
    print(f"  Args: {' '.join(extra_args) if extra_args else '(default)'}")
    print(f"  Command: {' '.join(cmd)}")
    print(f"{'='*80}\n")

    t0 = time.perf_counter()
    result = subprocess.run(cmd, cwd=str(ROOT))
    elapsed = time.perf_counter() - t0

    if result.returncode != 0:
        print(f"  [ERROR] Config '{label}' failed (rc={result.returncode})")
        return False

    print(f"  [OK] Config '{label}' completed in {elapsed:.0f}s")
    return True


def load_results():
    """Load all results_*.json files, return dict keyed by (etf, side, label)."""
    results = {}
    for p in DATA_DIR.glob("results_*.json"):
        if p.name.endswith("_early.json"):
            continue
        try:
            with open(p) as f:
                r = json.load(f)
        except Exception:
            continue

        etf = r.get("etf", "")
        side = r.get("side", "single")
        tag = r.get("tag", "")

        # Determine config label from tag suffix
        base_tag = etf if side == "single" else f"{etf}_{side}"
        suffix = tag[len(base_tag):] if tag.startswith(base_tag) else ""

        # Parse suffix components
        components = _parse_suffix(suffix)

        # Match to config
        label = _match_config(components)
        results[(etf, side, label)] = r
    return results


def _parse_suffix(suffix: str) -> dict:
    """Parse tag suffix into components."""
    import re
    comp = {"ratio_type": "sharpe", "sw": None, "emb": 10, "sharpe": False,
            "transform": None, "calibrated": False, "early": False}
    if "_early" in suffix:
        comp["early"] = True
        suffix = suffix.replace("_early", "")
    if "_calibrated" in suffix:
        comp["calibrated"] = True
        suffix = suffix.replace("_calibrated", "")
    if "_sharpe" in suffix:
        comp["sharpe"] = True
        suffix = suffix.replace("_sharpe", "")
    m = re.search(r"_sortino", suffix)
    if m:
        comp["ratio_type"] = "sortino"
        suffix = suffix.replace("_sortino", "")
    m = re.search(r"_sw([0-9.]+)", suffix)
    if m:
        comp["sw"] = float(m.group(1))
        suffix = suffix[:m.start()] + suffix[m.end():]
    m = re.search(r"_emb([0-9]+)", suffix)
    if m:
        comp["emb"] = int(m.group(1))
        suffix = suffix[:m.start()] + suffix[m.end():]
    if "_rank" in suffix:
        comp["transform"] = "rank"
    elif "_gauss" in suffix:
        comp["transform"] = "gauss"
    return comp


def _match_config(comp: dict) -> str:
    """Match parsed suffix components to a sweep config label."""
    rt = comp["ratio_type"]
    sw = comp["sw"]
    emb = comp["emb"]
    # Check each config
    for label, args in CONFIGS.items():
        if label == "baseline":
            continue
        exp = _parse_expected(args)
        if exp["ratio_type"] == rt and exp["sw"] == sw and exp["emb"] == emb:
            return label
    return "baseline"


def _parse_expected(args: list) -> dict:
    """Parse expected config from args list."""
    comp = {"ratio_type": "sharpe", "sw": None, "emb": 10}
    i = 0
    while i < len(args):
        if args[i] == "--ratio-type" and i + 1 < len(args):
            comp["ratio_type"] = args[i + 1]
            i += 2
        elif args[i] == "--sharpe-weight" and i + 1 < len(args):
            comp["sw"] = float(args[i + 1])
            i += 2
        elif args[i] == "--embargo-days" and i + 1 < len(args):
            comp["emb"] = int(args[i + 1])
            i += 2
        else:
            i += 1
    return comp


def print_report(results: dict):
    """Print comparison table: configs as rows, metrics as columns."""
    etfs = sorted(set(k[0] for k in results))
    sides = sorted(set(k[1] for k in results))
    labels = [l for l in CONFIGS.keys() if any((e, s, l) in results for e in etfs for s in sides)]

    print(f"\n{'='*120}")
    print("SWEEP COMPARISON REPORT")
    print(f"{'='*120}")

    # Per-ETF×side detail table
    print(f"\n{'Config':<14}", end="")
    for side in sides:
        for etf in etfs:
            col = f"{etf}_{side[:1]}" if side != "single" else etf
            print(f"  {col:>16}", end="")
    print()
    print("-" * (14 + 18 * len(sides) * len(etfs)))

    # Row: Outer Tail IC
    print(f"{'Out Tail IC':<14}", end="")
    for side in sides:
        for etf in etfs:
            best_val, best_lbl = np.nan, ""
            for label in labels:
                r = results.get((etf, side, label))
                if r is None:
                    continue
                v = r.get("selection_val_outer_tail_ic", np.nan)
                if not np.isnan(v) and (np.isnan(best_val) or v > best_val):
                    best_val, best_lbl = v, label
            # Print baseline and best
            for label in labels:
                if label != "baseline" and label != best_lbl:
                    continue
                r = results.get((etf, side, label))
                if r is None:
                    print(f"  {'N/A':>16}", end="")
                    continue
                v = r.get("selection_val_outer_tail_ic", np.nan)
                marker = " *" if label == best_lbl and not np.isnan(v) else ""
                if np.isnan(v):
                    print(f"  {'N/A':>16}", end="")
                else:
                    print(f"  {v:>14.4f}{marker}", end="")
    print()

    # Row: Outer IC
    print(f"{'Out IC':<14}", end="")
    for side in sides:
        for etf in etfs:
            r = results.get((etf, side, "baseline"))
            v = r.get("selection_val_outer_overall_ic", np.nan) if r else np.nan
            print(f"  {v:>16.4f}" if not np.isnan(v) else f"  {'N/A':>16}", end="")
    print()

    # Aggregate summary table
    print(f"\n{'='*120}")
    print("AGGREGATE SCORES (mean across all ETF×side)")
    print(f"{'='*120}")
    header = f"{'Config':<14}  {'Out TIC':>8}  {'Out IC':>8}  {'PBO':>8}  {'PerfDeg':>8}  {'#Feat':>6}"
    print(header)
    print("-" * len(header))

    for label in labels:
        tic_vals, ic_vals, pbo_vals, deg_vals, feat_vals = [], [], [], [], []
        for etf in etfs:
            for side in sides:
                r = results.get((etf, side, label))
                if r is None:
                    continue
                v = r.get("selection_val_outer_tail_ic", np.nan)
                if not np.isnan(v): tic_vals.append(v)
                v = r.get("selection_val_outer_overall_ic", np.nan)
                if not np.isnan(v): ic_vals.append(v)
                v = r.get("pbo", np.nan)
                if not np.isnan(v): pbo_vals.append(v)
                v = r.get("performance_degradation", np.nan)
                if not np.isnan(v): deg_vals.append(v)
                feat_vals.append(len(r.get("active_features", [])))

        tic = np.mean(tic_vals) if tic_vals else np.nan
        ic = np.mean(ic_vals) if ic_vals else np.nan
        pbo = np.mean(pbo_vals) if pbo_vals else np.nan
        deg = np.mean(deg_vals) if deg_vals else np.nan
        feat = np.mean(feat_vals) if feat_vals else np.nan

        def _fmt(v, w, d=4):
            return f"{v:>{w}.{d}f}" if not np.isnan(v) else f"{'N/A':>{w}}"
        print(f"{label:<14}  {_fmt(tic,8)}  {_fmt(ic,8)}  {_fmt(pbo,8,1)}%  {_fmt(deg,8)}  {_fmt(feat,6,1)}")

    print(f"\n* = best Outer Tail IC per ETF×side")


if __name__ == "__main__":
    import numpy as np

    ap = argparse.ArgumentParser(description="Sweep V5 objective variants")
    ap.add_argument("--configs", nargs="*", default=None,
                    help="Specific configs to run (default: all). E.g.: sortino sw0.30")
    ap.add_argument("--report", action="store_true",
                    help="Print report only (no training)")
    ap.add_argument("--trials", type=int, default=100,
                    help="Optuna trials per run (default 100)")
    ap.add_argument("--etf", default="all",
                    help="ETF filter (default: all)")
    args = ap.parse_args()

    if args.report:
        results = load_results()
        print_report(results)
        sys.exit(0)

    configs_to_run = args.configs if args.configs else list(CONFIGS.keys())
    # Baseline is reference only - skip training if results already exist
    if "baseline" in configs_to_run:
        baseline_results = list(DATA_DIR.glob("results_*ETF.json"))
        if baseline_results:
            print("[INFO] Baseline results already exist, skipping baseline training.")
            configs_to_run.remove("baseline")

    t_total = time.perf_counter()
    for label in configs_to_run:
        if label not in CONFIGS:
            print(f"[WARNING] Unknown config '{label}', skipping")
            continue
        extra = CONFIGS[label]
        success = run_config(label, extra, args.trials, args.etf)
        if not success:
            print(f"[ERROR] Config '{label}' failed, continuing...")

    print(f"\nTotal sweep elapsed: {time.perf_counter() - t_total:.0f}s")

    # Generate report
    results = load_results()
    print_report(results)
