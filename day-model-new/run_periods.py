#!/usr/bin/env python3
"""Multi-period training orchestrator for Day-Model Rewrite v3.

Runs the feature selection + evaluation pipeline across multiple training windows
to produce a comprehensive cross-period FP rate comparison report.

Periods:
  P2: Train 2015-01-01 to 2023-01-01, OOS 2023-01-01 to present
  P3: Train 2016-01-01 to 2024-01-01, OOS 2024-01-01 to present
  P4: Train 2017-01-01 to 2025-01-01, OOS 2025-01-01 to present

Uses OOS as ground truth (no lockbox). Jackknife uses n_chunks = training_years.
588000ETF excluded (insufficient history for multi-period analysis).

Usage:
  python day-model-new/run_periods.py                    # All 3 periods, all ETFs/sides
  python day-model-new/run_periods.py -e 300ETF          # Single ETF
  python day-model-new/run_periods.py --periods p2,p3    # Subset of periods
  python day-model-new/run_periods.py --compile-only     # Recompile report from existing JSONs
  python day-model-new/run_periods.py --max-parallel 4   # Parallel combos
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# Period configurations: name -> (train_start, train_end)
PERIODS = {
    "p2": ("2015-01-01", "2023-01-01"),
    "p3": ("2016-01-01", "2024-01-01"),
    "p4": ("2017-01-01", "2025-01-01"),
    "p5": ("2018-01-01", "2026-01-01"),
}

# 588000ETF excluded — insufficient history for multi-period
ETFS = ["300ETF", "50ETF", "500ETF", "159915ETF"]
SIDES = ["single"]


def period_suffix(period_name: str) -> str:
    """Generate file suffix from period name: p2 -> _p2015_2023."""
    train_start, train_end = PERIODS[period_name]
    y0 = train_start[:4]
    y1 = train_end[:4]
    return f"_p{y0}_{y1}"


def cpu_count():
    try:
        return max(1, os.cpu_count() or 1)
    except Exception:
        return 1


def run_combo(etf: str, side: str, period_name: str, inner_n_jobs: int) -> tuple:
    """Run select_features + evaluate_concept for one ETF/side/period combo."""
    train_start, train_end = PERIODS[period_name]
    suffix = period_suffix(period_name)
    oos_start = train_end  # OOS starts where training ends

    # Stage 0: Ensure candidate combination file exists
    cand_file = HERE / "mining" / f"candidates_{etf}_{side}.json"
    if not cand_file.exists() or cand_file.stat().st_size < 100:
        print(f"\n>>> [Stage 0] generate_combos --no-dedup: ETF={etf}, Side={side} (candidates missing)")
        cmd_gen = [
            sys.executable,
            str(HERE / "mining" / "generate_combos.py"),
            "-e", etf,
            "-s", side,
            "--no-dedup",
        ]
        try:
            result_gen = subprocess.run(
                cmd_gen, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
            )
            if result_gen.returncode not in (0, None):
                print(f"WARNING: generate_combos exited {result_gen.returncode} for {etf} {side}")
        except Exception as e:
            print(f"WARNING: generate_combos failed to launch for {etf} {side}: {e}")

    # Stage A: Feature Selection
    cmd_a = [
        sys.executable,
        str(HERE / "select_features.py"),
        "-e", etf,
        "-s", side,
        "--n-jobs", str(inner_n_jobs),
        "--train-start", train_start,
        "--train-end", train_end,
        "--period-suffix", suffix,
    ]

    print(f"\n>>> [Stage A] select_features: ETF={etf}, Side={side}, Period={period_name}")
    try:
        result_a = subprocess.run(
            cmd_a, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        return False, f"select_features failed to launch for {etf} {side} {period_name}: {e}"
    if result_a.returncode not in (0, None):
        return False, f"select_features failed for {etf} {side} {period_name} (exit {result_a.returncode})"

    # Stage A2: ONC Feature Clustering
    cmd_ac = [
        sys.executable,
        str(HERE / "feature_clusters.py"),
        "-e", etf,
        "-s", side,
        "--suffix", suffix,
        "--train-start", train_start,
        "--train-end", train_end,
    ]

    print(f"\n>>> [Stage A2] feature_clusters: ETF={etf}, Side={side}, Period={period_name}")
    try:
        result_ac = subprocess.run(
            cmd_ac, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        print(f"WARNING: feature_clusters failed to launch for {etf} {side} {period_name}: {e}")

    # Stage B: Evaluation (OOS-only, no lockbox)
    cmd_b = [
        sys.executable,
        str(HERE / "evaluate_concept.py"),
        "-e", etf,
        "-s", side,
        "--train-start", train_start,
        "--train-end", train_end,
        "--oos-start", oos_start,
        "--period-suffix", suffix,
    ]

    print(f"\n>>> [Stage B] evaluate_concept: ETF={etf}, Side={side}, Period={period_name}")
    try:
        result_b = subprocess.run(
            cmd_b, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        return False, f"evaluate_concept failed to launch for {etf} {side} {period_name}: {e}"
    if result_b.returncode not in (0, None):
        return False, f"evaluate_concept failed for {etf} {side} {period_name} (exit {result_b.returncode})"

    return True, f"Success {etf} {side} {period_name}"


def run_diagnostics(period_name: str) -> bool:
    """Run analyze_admitted_features.py for a given period."""
    train_start, train_end = PERIODS[period_name]
    suffix = period_suffix(period_name)

    cmd = [
        sys.executable,
        str(HERE / "analyze_admitted_features.py"),
        "--period-suffix", suffix,
        "--train-start", train_start,
        "--train-end", train_end,
    ]

    print(f"\n>>> [Diagnostics] analyze_admitted_features: Period={period_name}")
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        print(f"WARNING: analyze_admitted_features failed for {period_name}: {e}")
        return False
    if result.returncode not in (0, None):
        print(f"WARNING: analyze_admitted_features exited {result.returncode} for {period_name}")
        return False
    return True


def run_filter_diagnosis(period_name: str) -> bool:
    """Run filter_diagnosis.py for a given period."""
    train_start, train_end = PERIODS[period_name]
    suffix = period_suffix(period_name)

    cmd = [
        sys.executable,
        str(HERE / "filter_diagnosis.py"),
        "--period-suffix", suffix,
        "--train-start", train_start,
        "--train-end", train_end,
    ]

    print(f"\n>>> [Filter Diagnosis] filter_diagnosis: Period={period_name}")
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        print(f"WARNING: filter_diagnosis failed for {period_name}: {e}")
        return False
    if result.returncode not in (0, None):
        print(f"WARNING: filter_diagnosis exited {result.returncode} for {period_name}")
        return False
    return True


def run_compile_report(period_name: str, etfs_to_run, sides_to_run) -> bool:
    """Run compile_report.py for a given period to generate BASELINE_REPORT{suffix}.md."""
    suffix = period_suffix(period_name)

    cmd = [
        sys.executable,
        str(HERE / "compile_report.py"),
        "--period-suffix", suffix,
    ]
    if etfs_to_run != ETFS:
        cmd += ["-e", etfs_to_run[0]]
    if sides_to_run != SIDES:
        cmd += ["-s", sides_to_run[0]]

    print(f"\n>>> [Compile Report] compile_report: Period={period_name}")
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT), text=True, encoding="utf-8", errors="replace",
        )
    except Exception as e:
        print(f"WARNING: compile_report failed for {period_name}: {e}")
        return False
    if result.returncode not in (0, None):
        print(f"WARNING: compile_report exited {result.returncode} for {period_name}")
        return False
    return True


def compile_cross_period_report(periods_to_run, etfs_to_run, sides_to_run):
    """Compile a cross-period FP rate comparison report from filter_effectiveness JSONs."""
    data_dir = HERE / "data"
    report_lines = [
        "# Multi-Period FP Rate Comparison Report",
        "",
        "Cross-period comparison of filter gate false positive/negative rates.",
        "Ground truth: OOS (post-training) performance. No lockbox used.",
        "",
        "---",
        "",
    ]

    # Load filter effectiveness data for each period
    period_data = {}
    for pname in periods_to_run:
        suffix = period_suffix(pname)
        fe_path = data_dir / f"filter_effectiveness{suffix}.json"
        if fe_path.exists():
            with open(fe_path, "r", encoding="utf-8") as f:
                period_data[pname] = json.load(f)
        else:
            print(f"WARNING: Missing {fe_path.name}, skipping period {pname}")

    # Also load original (default) filter effectiveness if available
    orig_path = data_dir / "filter_effectiveness.json"
    if orig_path.exists():
        with open(orig_path, "r", encoding="utf-8") as f:
            period_data["original"] = json.load(f)

    if not period_data:
        print("ERROR: No filter effectiveness data found. Run pipeline first.")
        return

    # Period labels for display
    period_labels = {"original": "2015-2022 (Original)"}
    for pname in periods_to_run:
        ts, te = PERIODS[pname]
        period_labels[pname] = f"{ts[:4]}-{te[:4]}"

    # For each ETF/side, compare FP rates across periods
    for etf in etfs_to_run:
        for side in sides_to_run:
            report_lines.append(f"## {etf} — `{side}`")
            report_lines.append("")

            # Collect admitted pool summary across periods
            header = "| Period | Pool Size | Clusters | Cluster Sizes | FP Rate | Mean OOS IC | Mean OOS Sharpe |"
            sep = "| :--- | ---: | ---: | :--- | ---: | ---: | ---: |"
            report_lines.append(header)
            report_lines.append(sep)

            for pname in ["original"] + periods_to_run:
                if pname not in period_data:
                    continue
                pdata = period_data[pname].get(etf, {}).get(side, {})
                gate_eff = pdata.get("gate_effectiveness")
                if not gate_eff:
                    continue
                adm = gate_eff.get("_admitted_summary", {})
                n_features = adm.get("n_admitted", 0)
                fp_rate = adm.get("false_positive_rate", 0.0)
                mean_ic = adm.get("mean_lock_ic", 0.0)
                mean_sharpe = adm.get("mean_lock_sharpe", 0.0)
                label = period_labels.get(pname, pname)

                psuffix = "" if pname == "original" else period_suffix(pname)
                cpath = data_dir / f"cluster_assignments_{etf}_{side}{psuffix}.json"
                n_clusters_str = "-"
                sizes_str = "-"
                if cpath.exists():
                    try:
                        with open(cpath, "r", encoding="utf-8") as f:
                            cdata = json.load(f)
                        cdict = cdata.get("clusters", {})
                        n_clusters_str = str(cdata.get("n_clusters", len(cdict)))
                        sizes = sorted([len(m) for m in cdict.values()], reverse=True)
                        if len(sizes) <= 15:
                            sizes_str = str(sizes)
                        else:
                            sizes_str = f"[{', '.join(map(str, sizes[:12]))}, ... ({len(sizes)} clusters)]"
                    except Exception:
                        pass

                report_lines.append(
                    f"| {label} | {n_features} | {n_clusters_str} | `{sizes_str}` | {fp_rate:.1%} | {mean_ic:+.4f} | {mean_sharpe:+.4f} |"
                )

            report_lines.append("")

            # Per-gate comparison
            gate_names = set()
            for pname in ["original"] + periods_to_run:
                if pname not in period_data:
                    continue
                pdata = period_data[pname].get(etf, {}).get(side, {})
                gate_eff = pdata.get("gate_effectiveness", {})
                for gname in gate_eff:
                    if not gname.startswith("_"):
                        gate_names.add(gname)

            if gate_names:
                report_lines.append("### Per-Gate False Negative Rate Comparison")
                report_lines.append("")
                gate_header = "| Gate | " + " | ".join(period_labels.get(p, p) for p in ["original"] + periods_to_run if p in period_data) + " |"
                gate_sep = "| :--- | " + " | ".join("---:" for p in ["original"] + periods_to_run if p in period_data) + " |"
                report_lines.append(gate_header)
                report_lines.append(gate_sep)

                for gname in sorted(gate_names):
                    row = f"| {gname} |"
                    for pname in ["original"] + periods_to_run:
                        if pname not in period_data:
                            continue
                        pdata = period_data[pname].get(etf, {}).get(side, {})
                        gate_eff = pdata.get("gate_effectiveness", {})
                        g = gate_eff.get(gname, {})
                        fn_rate = g.get("false_negative_rate", None)
                        if fn_rate is not None:
                            row += f" {fn_rate:.1%} |"
                        else:
                            row += " - |"
                    report_lines.append(row)

                report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

    # Write report
    report_path = HERE / "MULTI_PERIOD_FP_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"\nCross-period report written to: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Multi-period training orchestrator")
    parser.add_argument("-e", "--etf", default="all", help="ETF to run (or 'all')")
    parser.add_argument("-s", "--side", default="all", help="Side to run (or 'all')")
    parser.add_argument("--periods", default="p2,p3,p4", help="Comma-separated period names (p2,p3,p4)")
    parser.add_argument("--compile-only", action="store_true", help="Only compile the cross-period report")
    parser.add_argument("--max-parallel", type=int, default=1, help="Max concurrent combos")
    parser.add_argument("--n-jobs", type=int, default=-1, help="Inner worker count for select_features")
    parser.add_argument("--skip-diagnostics", action="store_true", help="Skip analyze_admitted_features step")
    args = parser.parse_args()

    periods_to_run = [p.strip() for p in args.periods.split(",")]
    for p in periods_to_run:
        if p not in PERIODS:
            print(f"ERROR: Unknown period '{p}'. Available: {list(PERIODS.keys())}")
            sys.exit(1)

    etfs_to_run = ETFS if args.etf == "all" else [args.etf]
    sides_to_run = SIDES if args.side == "all" else [args.side]

    # Validate ETFs
    for etf in etfs_to_run:
        if etf not in ETFS:
            print(f"ERROR: '{etf}' not supported for multi-period (available: {ETFS})")
            sys.exit(1)

    if args.compile_only:
        compile_cross_period_report(periods_to_run, etfs_to_run, sides_to_run)
        return

    # Build task list
    tasks = []
    for pname in periods_to_run:
        for etf in etfs_to_run:
            for side in sides_to_run:
                tasks.append((etf, side, pname))

    total_cpus = cpu_count()
    print(f"Multi-period training: {len(tasks)} combos across periods={periods_to_run}")
    print(f"ETFs={etfs_to_run}, Sides={sides_to_run}, max_parallel={args.max_parallel}")

    if args.max_parallel <= 1:
        inner_n_jobs = args.n_jobs if args.n_jobs > 0 else min(total_cpus, 6)  # Cap at 6 to avoid FDR sim crashes
        results = []
        for idx, (etf, side, pname) in enumerate(tasks, 1):
            print(f"\n===== [{idx}/{len(tasks)}] {etf} {side} {pname} =====")
            ok, msg = run_combo(etf, side, pname, inner_n_jobs)
            results.append((ok, msg))
            if not ok:
                print(f"ERROR: {msg}")
    else:
        inner_n_jobs = max(1, total_cpus // args.max_parallel)
        if args.n_jobs > 0:
            inner_n_jobs = min(inner_n_jobs, args.n_jobs)
        results = []
        with ThreadPoolExecutor(max_workers=args.max_parallel) as ex:
            futures = {
                ex.submit(run_combo, etf, side, pname, inner_n_jobs): (etf, side, pname)
                for etf, side, pname in tasks
            }
            for fut in as_completed(futures):
                etf, side, pname = futures[fut]
                try:
                    ok, msg = fut.result()
                except Exception as e:
                    ok, msg = False, f"Exception: {e}"
                results.append((ok, msg))
                status = "OK" if ok else "FAIL"
                print(f"[{status}] {etf} {side} {pname}: {msg}")

    success_count = sum(1 for ok, _ in results if ok)
    print(f"\nCompleted {success_count}/{len(tasks)} combinations successfully.")

    # Run diagnostics per period
    if not args.skip_diagnostics:
        for pname in periods_to_run:
            run_diagnostics(pname)
            run_filter_diagnosis(pname)
            run_compile_report(pname, etfs_to_run, sides_to_run)

    # Compile cross-period report
    compile_cross_period_report(periods_to_run, etfs_to_run, sides_to_run)


if __name__ == "__main__":
    main()
