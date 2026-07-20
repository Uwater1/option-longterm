#!/usr/bin/env python3
"""
Baseline runner for Day-Model Rewrite v3.
Runs select_features.py and evaluate_concept.py in parallel across all 5 ETFs and 3 sides,
then compiles a baseline performance report.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from joblib import Parallel, delayed

HERE = Path(__file__).resolve().parent

# Ensure day-model-new is importable
sys.path.insert(0, str(HERE))

ETFS = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

def run_combination(etf, side, early):
    """Run select_features and evaluate_concept in-process for a single combination."""
    import importlib
    
    suffix = "_early" if early else ""
    
    # --- Stage A: Feature Selection ---
    print(f"Starting feature selection: ETF={etf}, Side={side}")
    select_argv = ["select_features.py", "-e", etf, "-s", side, "--n-jobs", "1"]
    if early:
        select_argv.append("--early")
    
    old_argv = sys.argv
    try:
        sys.argv = select_argv
        import select_features
        importlib.reload(select_features)
        select_features.main()
    except SystemExit as e:
        if e.code not in (None, 0):
            return False, f"select_features failed for {etf} {side} (exit code {e.code})"
    except Exception as e:
        return False, f"select_features failed for {etf} {side}: {e}"
    finally:
        sys.argv = old_argv
        
    # --- Stage B: Evaluation ---
    print(f"Starting evaluation: ETF={etf}, Side={side}")
    eval_argv = ["evaluate_concept.py", "-e", etf, "-s", side]
    if early:
        eval_argv.append("--early")
    
    try:
        sys.argv = eval_argv
        import evaluate_concept
        importlib.reload(evaluate_concept)
        evaluate_concept.main()
    except SystemExit as e:
        if e.code not in (None, 0):
            return False, f"evaluate_concept failed for {etf} {side} (exit code {e.code})"
    except Exception as e:
        return False, f"evaluate_concept failed for {etf} {side}: {e}"
    finally:
        sys.argv = old_argv
        
    return True, f"Success {etf} {side}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all", help="ETF: 300ETF, 50ETF, etc., or 'all'")
    parser.add_argument("-s", "--side", default="all", help="Side: single, long, short, or 'all'")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    parser.add_argument("--compile-only", action="store_true", help="Only compile the baseline report from existing JSON outputs")
    parser.add_argument("--n-jobs", type=int, default=4, help="Number of parallel workers for baseline loop")
    args = parser.parse_args()

    etfs_to_run = ETFS if args.etf == "all" else [args.etf]
    sides_to_run = SIDES if args.side == "all" else [args.side]
    suffix = "_early" if args.early else ""

    if not args.compile_only:
        print(f"Running Baseline Selection & Evaluation in parallel for ETFs: {etfs_to_run}, Sides: {sides_to_run}")
        
        tasks = []
        for etf in etfs_to_run:
            for side in sides_to_run:
                tasks.append((etf, side, args.early))
                
        # Run in parallel (in-process, no subprocess overhead)
        results = Parallel(n_jobs=args.n_jobs, prefer="processes")(
            delayed(run_combination)(etf, side, early)
            for etf, side, early in tasks
        )
        
        # Report status
        success_count = sum(1 for success, _ in results if success)
        print(f"\nCompleted {success_count}/{len(tasks)} combinations successfully.")
        for success, msg in results:
            if not success:
                print(f"ERROR: {msg}")

    # Compile results into a Markdown report
    print("\nCompiling baseline report...")
    report_lines = [
        "# Day-Model Rewrite v3 — Baseline Performance Report",
        "",
        "This report summarizes the baseline performance of the simple IC-weighted combination model",
        "evaluated on existing candidate features.",
        "The selection train period is `2015-01-01` to `2022-01-01` (except `588000ETF` which uses `2020-11-01` to `2025-01-01`).",
        "Holdout OOS starts `2022-01-01` (`2025-01-01` for `588000ETF`), and OOS Lockbox starts `2024-03-01` (`2025-07-01` for `588000ETF`).",
        "",
        "## Performance Table (Holdout OOS)",
        "",
        "| ETF | Side | Features Admitted | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for etf in ETFS:
        for side in SIDES:
            res_file = HERE / "data" / f"results_{etf}_{side}{suffix}.json"
            if res_file.exists():
                with open(res_file, "r") as f:
                    data = json.load(f)
                
                oos = data["oos_metrics"]
                n_feats = len(data["features_selected"])
                
                overall_ic = f"{oos['overall_ic']:+.4f}"
                overall_ci = f"[{oos['overall_ic_ci'][0]:+.4f}, {oos['overall_ic_ci'][1]:+.4f}]"
                
                tail_ic = f"{oos['tail_ic']:+.4f}"
                tail_ci = f"[{oos['tail_ic_ci'][0]:+.4f}, {oos['tail_ic_ci'][1]:+.4f}]"
                
                # Check if CI spans zero (flag with *)
                if oos['overall_ic_ci'][0] * oos['overall_ic_ci'][1] <= 0:
                    overall_ic += "*"
                if oos['tail_ic_ci'][0] * oos['tail_ic_ci'][1] <= 0:
                    tail_ic += "*"
                    
                line = (
                    f"| {etf} | {side} | {n_feats} | "
                    f"{overall_ic} | {overall_ci} | "
                    f"{tail_ic} | {tail_ci} | "
                    f"{oos['monotonicity']:+.4f} | "
                    f"{oos['ann_ret']*100:.2f}% | "
                    f"{oos['sharpe']:.4f} | "
                    f"{oos['sortino']:.4f} | "
                    f"{oos['max_dd']*100:.2f}% |"
                )
                report_lines.append(line)

    report_lines.extend([
        "",
        "\\* indicates that the 95% circular block-bootstrap confidence interval spans zero (statistically indistinguishable from noise).",
        "",
        "## Performance Table (OOS Lockbox)",
        "",
        "| ETF | Side | Features Admitted | Overall IC | Overall IC 95% CI | Tail IC | Tail IC 95% CI | Monotonicity | Ann. Return | Sharpe | Sortino | Max DD |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for etf in ETFS:
        for side in SIDES:
            res_file = HERE / "data" / f"results_{etf}_{side}{suffix}.json"
            if res_file.exists():
                with open(res_file, "r") as f:
                    data = json.load(f)
                
                lock = data["lockbox_metrics"]
                n_feats = len(data["features_selected"])
                
                overall_ic = f"{lock['overall_ic']:+.4f}"
                overall_ci = f"[{lock['overall_ic_ci'][0]:+.4f}, {lock['overall_ic_ci'][1]:+.4f}]"
                
                tail_ic = f"{lock['tail_ic']:+.4f}"
                tail_ci = f"[{lock['tail_ic_ci'][0]:+.4f}, {lock['tail_ic_ci'][1]:+.4f}]"
                
                # Check if CI spans zero (flag with *)
                if lock['overall_ic_ci'][0] * lock['overall_ic_ci'][1] <= 0:
                    overall_ic += "*"
                if lock['tail_ic_ci'][0] * lock['tail_ic_ci'][1] <= 0:
                    tail_ic += "*"
                    
                line = (
                    f"| {etf} | {side} | {n_feats} | "
                    f"{overall_ic} | {overall_ci} | "
                    f"{tail_ic} | {tail_ci} | "
                    f"{lock['monotonicity']:+.4f} | "
                    f"{lock['ann_ret']*100:.2f}% | "
                    f"{lock['sharpe']:.4f} | "
                    f"{lock['sortino']:.4f} | "
                    f"{lock['max_dd']*100:.2f}% |"
                )
                report_lines.append(line)

    report_lines.extend([
        "",
        "\\* indicates that the 95% circular block-bootstrap confidence interval spans zero (statistically indistinguishable from noise).",
        "",
        "## Admitted Features Details",
        ""
    ])

    for etf in ETFS:
        for side in SIDES:
            pool_file = HERE / "data" / f"selected_pool_{etf}_{side}{suffix}.json"
            if pool_file.exists():
                with open(pool_file, "r") as f:
                    pool_data = json.load(f)
                
                heading = f"### {etf} ({side})"
                report_lines.append(heading)
                
                if not pool_data:
                    report_lines.append("No features admitted.")
                else:
                    for item in pool_data:
                        sign_str = f"{item['sign']:+d}"
                        line = f"- `{item['feature_name']}` (sign={sign_str}, overall_ic={item['overall_ic']:.4f}, deflated_ic={item['deflated_ic']:.4f})"
                        report_lines.append(line)
                report_lines.append("")

    report_path = HERE / f"BASELINE_REPORT{suffix}.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\nSaved baseline report to {report_path}")

if __name__ == "__main__":
    main()
