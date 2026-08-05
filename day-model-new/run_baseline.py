#!/usr/bin/env python3
"""Baseline runner for Day-Model Rewrite v3.
Runs generate_combos (--no-dedup), select_features.py, and evaluate_concept.py
for each ETF/side combination, then compiles a baseline performance report.

Execution strategy:
  - Each combination runs in its own subprocess (clean process isolation,
    no module-reload hacks, no shared-state pollution).
  - Stage 0 regenerates the full candidate space (--no-dedup) so the pipeline
    is self-contained and never starved by incremental dedup logic.
  - Default = sequential (one combo at a time). Each combo then uses ALL
    cores internally via joblib + numba prange. No oversubscription.
  - --max-parallel N runs up to N combos concurrently. When set, inner
    --n-jobs is capped so total workers ~= CPU count, and per-combo output
    is captured and printed on completion to avoid interleaved logs.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

ETFS = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]


def cpu_count():
    try:
        return max(1, os.cpu_count() or 1)
    except Exception:
        return 1


def run_stage(cmd, label, timeout=None, capture=False):
    """Run one pipeline stage as a subprocess.
    Returns (failed: bool, tail: str). tail holds the last output lines
    when captured or when the stage failed/timed out.
    """
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            capture_output=capture,
        )
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        tail = "\n".join(out.splitlines()[-10:]) if out else "(no output captured)"
        return True, f"{label} timed out after {timeout}s\n{tail}"
    except Exception as e:
        return True, f"{label} failed to launch: {e}"
    tail = ""
    if proc.stdout:
        tail = "\n".join(proc.stdout.splitlines()[-10:])
    if proc.returncode != 0:
        if not tail and proc.stderr:
            tail = "\n".join(proc.stderr.splitlines()[-10:])
        return True, f"{label} failed (exit code {proc.returncode})\n{tail}"
    return False, tail


def results_valid(etf: str, side: str, suffix: str) -> bool:
    """Check if valid Stage A (selected_pool) AND Stage B (results) outputs
    exist for this combo, so --skip-existing never skips a partially done combo."""
    pool_file = HERE / "data" / f"selected_pool_{etf}_{side}{suffix}.json"
    res_file = HERE / "data" / f"results_{etf}_{side}{suffix}.json"
    if not pool_file.exists() or not res_file.exists():
        return False
    try:
        with open(res_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Must have non-empty features_selected AND oos_metrics
        if not data.get("features_selected"):
            return False
        if not data.get("oos_metrics"):
            return False
        return True
    except Exception:
        return False


def run_combination(etf: str, side: str, early: bool, inner_n_jobs: int,
                    timeout: int = None, capture: bool = False) -> tuple:
    """Run generate_combos + select_features + feature_clusters + evaluate_concept
    as subprocesses for one combo. When capture=True, child output is captured
    and shown on failure/completion instead of streaming (parallel mode)."""
    tag = f"{etf} {side}{'_early' if early else ''}"

    # --- Stage 0: Candidate Generation (full space, no dedup) ---
    cmd_gen = [
        sys.executable,
        str(HERE / "mining" / "generate_combos.py"),
        "-e", etf,
        "-s", side,
        "--no-dedup",
    ]
    if early:
        cmd_gen.append("--early")

    print(f"\n>>> [Stage 0] generate_combos --no-dedup: ETF={etf}, Side={side}")
    failed, tail = run_stage(cmd_gen, f"generate_combos ({tag})", timeout, capture)
    if failed:
        print(f"WARNING: {tail} (continuing with existing candidates)")
    cand_file = HERE / "mining" / f"candidates_{etf}_{side}{'_early' if early else ''}.json"
    if not cand_file.exists():
        return False, f"generate_combos failed for {tag} and no candidates file exists at {cand_file}"

    # --- Stage A: Feature Selection ---
    cmd_a = [
        sys.executable,
        str(HERE / "select_features.py"),
        "-e", etf,
        "-s", side,
        "--n-jobs", str(inner_n_jobs),
    ]
    if early:
        cmd_a.append("--early")

    print(f"\n>>> [Stage A] select_features: ETF={etf}, Side={side}, inner n_jobs={inner_n_jobs}")
    failed, tail = run_stage(cmd_a, f"select_features ({tag})", timeout, capture)
    if failed:
        return False, f"select_features failed for {tag}\n{tail}"
    if capture and tail:
        print(tail)

    # --- Stage A2: ONC Feature Clustering ---
    cmd_ac = [
        sys.executable,
        str(HERE / "feature_clusters.py"),
        "-e", etf,
        "-s", side,
    ]
    if early:
        cmd_ac.extend(["--suffix", "_early"])

    print(f"\n>>> [Stage A2] feature_clusters: ETF={etf}, Side={side}")
    failed, tail = run_stage(cmd_ac, f"feature_clusters ({tag})", timeout, capture)
    if failed:
        print(f"WARNING: {tail} (continuing; downstream may use stale cluster data)")

    # --- Stage B: Evaluation ---
    cmd_b = [
        sys.executable,
        str(HERE / "evaluate_concept.py"),
        "-e", etf,
        "-s", side,
    ]
    if early:
        cmd_b.append("--early")

    print(f"\n>>> [Stage B] evaluate_concept: ETF={etf}, Side={side}")
    failed, tail = run_stage(cmd_b, f"evaluate_concept ({tag})", timeout, capture)
    if failed:
        return False, f"evaluate_concept failed for {tag}\n{tail}"
    if capture and tail:
        print(tail)

    return True, f"Success {etf} {side}"


def run_combinations_sequential(tasks, inner_n_jobs: int, skip_existing: bool, timeout: int = None):
    results = []
    for idx, (etf, side, early) in enumerate(tasks, 1):
        s = "_early" if early else ""
        if skip_existing and results_valid(etf, side, s):
            print(f"[{idx}/{len(tasks)}] SKIP (valid results exist): {etf} {side}{s}")
            results.append((True, f"Skipped {etf} {side}"))
            continue
        print(f"\n===== [{idx}/{len(tasks)}] {etf} {side} =====")
        ok, msg = run_combination(etf, side, early, inner_n_jobs, timeout=timeout, capture=False)
        results.append((ok, msg))
        if not ok:
            print(f"ERROR: {msg}")
    return results


def run_combinations_parallel(tasks, max_parallel: int, total_cpus: int, skip_existing: bool,
                              n_jobs: int = -1, timeout: int = None):
    """Run up to max_parallel combos concurrently. Inner n_jobs capped so
    total inner workers across concurrent combos ~= total_cpus.
    Per-combo output is captured and printed on completion (no interleaving)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    inner_n_jobs = max(1, total_cpus // max_parallel)
    if n_jobs > 0 and n_jobs != inner_n_jobs:
        print(f"WARNING: --n-jobs {n_jobs} ignored in parallel mode; capped to "
              f"{inner_n_jobs} (= cpu_count {total_cpus} // max_parallel {max_parallel}) "
              f"to avoid oversubscription.")

    # Build a filtered task list (skip existing checked upfront)
    pending = []
    results = []
    for etf, side, early in tasks:
        s = "_early" if early else ""
        if skip_existing and results_valid(etf, side, s):
            print(f"SKIP (valid results exist): {etf} {side}{s}")
            results.append((True, f"Skipped {etf} {side}"))
        else:
            pending.append((etf, side, early))

    if not pending:
        return results

    print(f"\nLaunching {len(pending)} combos, max_parallel={max_parallel}, inner n_jobs={inner_n_jobs}")

    with ThreadPoolExecutor(max_workers=max_parallel) as ex:
        futures = {
            ex.submit(run_combination, etf, side, early, inner_n_jobs, timeout, True): (etf, side, early)
            for etf, side, early in pending
        }
        for fut in as_completed(futures):
            etf, side, early = futures[fut]
            try:
                ok, msg = fut.result()
            except Exception as e:
                ok, msg = False, f"Exception for {etf} {side}: {e}"
            results.append((ok, msg))
            status = "OK" if ok else "FAIL"
            print(f"[{status}] {etf} {side}: {msg}")

    return results


def compile_report(etfs_to_run, sides_to_run, suffix: str):
    """Delegate report compilation to the standalone compile_report.py module
    to avoid duplicating the rendering logic."""
    import importlib
    here_str = str(HERE)
    if here_str not in sys.path:
        sys.path.insert(0, here_str)
    try:
        cr = importlib.import_module("compile_report")
    except Exception as e:
        print(f"WARNING: could not import compile_report module: {e}; falling back to subprocess")
        cmd = [sys.executable, str(HERE / "compile_report.py")]
        if etfs_to_run != ETFS:
            cmd += ["-e", ",".join(etfs_to_run) if etfs_to_run else "all"]
        if sides_to_run != SIDES:
            cmd += ["-s", ",".join(sides_to_run) if sides_to_run else "all"]
        if suffix:
            cmd.append("--early")
        try:
            subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
        except Exception as e2:
            print(f"ERROR running compile_report subprocess: {e2}")
        return

    print("\nCompiling baseline report via compile_report module...")
    lines = cr.build_report(etfs_to_run, sides_to_run, suffix)
    report_path = HERE / f"BASELINE_REPORT{suffix}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved baseline report to {report_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all", help="ETF: 300ETF, 50ETF, etc., or 'all'")
    parser.add_argument("-s", "--side", default="single", help="Side: single, long, short, or 'all'")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    parser.add_argument("--compile-only", action="store_true", help="Only compile the baseline report from existing JSON outputs")
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=-1,
        help="Inner worker count passed to select_features.py (-1 = all cores, sequential mode)",
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=1,
        help="Run up to N combinations concurrently (default 1 = sequential). "
             "When >1, inner n_jobs is capped to cpu_count // max_parallel.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip combos that already have a valid (non-empty) results JSON.",
    )
    parser.add_argument(
        "--stage-timeout",
        type=int,
        default=None,
        help="Per-stage subprocess timeout in seconds (default: no timeout).",
    )
    args = parser.parse_args()

    etfs_to_run = ETFS if args.etf == "all" else [args.etf]
    sides_to_run = SIDES if args.side == "all" else [args.side]
    suffix = "_early" if args.early else ""

    if args.compile_only:
        compile_report(etfs_to_run, sides_to_run, suffix)
        return

    tasks = [(etf, side, args.early) for etf in etfs_to_run for side in sides_to_run]

    print(
        f"Running baseline for ETFs={etfs_to_run} Sides={sides_to_run} "
        f"max_parallel={args.max_parallel} inner_n_jobs={args.n_jobs} skip_existing={args.skip_existing}"
    )

    total_cpus = cpu_count()

    if args.max_parallel <= 1:
        # Sequential: each combo uses all cores (or args.n_jobs if specified)
        inner_n_jobs = args.n_jobs if args.n_jobs > 0 else total_cpus
        results = run_combinations_sequential(tasks, inner_n_jobs, args.skip_existing, args.stage_timeout)
    else:
        # Parallel: cap inner workers to avoid oversubscription
        results = run_combinations_parallel(
            tasks,
            max_parallel=args.max_parallel,
            total_cpus=total_cpus,
            skip_existing=args.skip_existing,
            n_jobs=args.n_jobs,
            timeout=args.stage_timeout,
        )

    success_count = sum(1 for ok, _ in results if ok)
    print(f"\nCompleted {success_count}/{len(tasks)} combinations successfully.")
    for ok, msg in results:
        if not ok:
            print(f"ERROR: {msg}")

    if tasks and success_count == 0:
        print("WARNING: all combinations failed. Compiling report from stale/missing JSON outputs.")

    compile_report(etfs_to_run, sides_to_run, suffix)

    # Run filter diagnosis (scoped to the ETFs/sides actually run, only if something succeeded)
    if not args.early:
        if success_count == 0:
            print("\nSkipping trailing diagnostics: no combination succeeded.")
            return

        print("\nRunning filter deep diagnosis (filter_diagnosis.py)...")
        cmd_diag = [sys.executable, str(HERE / "filter_diagnosis.py"),
                    "-e", *etfs_to_run, "-s", *sides_to_run]
        try:
            subprocess.run(cmd_diag, cwd=str(REPO_ROOT), check=False)
        except Exception as e:
            print(f"WARNING: filter_diagnosis subprocess failed: {e}")

        if etfs_to_run == ETFS and sides_to_run == SIDES:
            print("\nRunning feature diagnostics (analyze_admitted_features.py)...")
            cmd_feat = [sys.executable, str(HERE / "analyze_admitted_features.py")]
            try:
                subprocess.run(cmd_feat, cwd=str(REPO_ROOT), check=False)
            except Exception as e:
                print(f"WARNING: analyze_admitted_features subprocess failed: {e}")
        else:
            print("\nSkipping analyze_admitted_features.py (runs over all ETFs/sides; "
                  "current run is scoped to a subset).")


if __name__ == "__main__":
    main()
