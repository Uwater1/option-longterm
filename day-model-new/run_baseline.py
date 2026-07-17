#!/usr/bin/env python3
"""
Baseline runner for Day-Model Rewrite v3.
Runs select_features.py and evaluate_concept.py across all 5 ETFs and all 3 sides,
then compiles a baseline performance report.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

ETFS = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

def run_cmd(cmd):
    """Run a shell command and print its output."""
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error executing command: {cmd}")
        print(res.stderr)
        return False
    print(res.stdout)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", default="all", help="ETF: 300ETF, 50ETF, etc., or 'all'")
    parser.add_argument("-s", "--side", default="all", help="Side: single, long, short, or 'all'")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    args = parser.parse_args()

    etfs_to_run = ETFS if args.etf == "all" else [args.etf]
    sides_to_run = SIDES if args.side == "all" else [args.side]
    suffix = "_early" if args.early else ""

    print(f"Running Baseline Selection & Evaluation for ETFs: {etfs_to_run}, Sides: {sides_to_run}")

    for etf in etfs_to_run:
        for side in sides_to_run:
            print(f"\n=======================================================")
            print(f"Running ETF={etf}, Side={side}")
            print(f"=======================================================")
            
            # Step 1: Run feature selection
            select_cmd = f"python3 {HERE}/select_features.py -e {etf} -s {side}"
            if args.early:
                select_cmd += " --early"
            if not run_cmd(select_cmd):
                continue
                
            # Step 2: Run evaluation
            eval_cmd = f"python3 {HERE}/evaluate_concept.py -e {etf} -s {side}"
            if args.early:
                eval_cmd += " --early"
            run_cmd(eval_cmd)

    # Compile results into a Markdown report
    print("\nCompiling baseline report...")
    report_lines = [
        "# Day-Model Rewrite v3 — Baseline Performance Report",
        "",
        "This report summarizes the baseline performance of the simple IC-weighted combination model",
        "evaluated on existing 221 candidate features (no feature mining yet).",
        "The selection train period is `2015-01-01` to `2022-01-01`. Holdout OOS is `2022-01-01` to present,",
        "and OOS Lockbox is `2024-03-01` to present.",
        "",
        "## Performance Table (Holdout OOS: 2022-present)",
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
        "## Performance Table (OOS Lockbox: 2024-present)",
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
        ""
    ])

    report_path = HERE / f"BASELINE_REPORT{suffix}.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\nSaved baseline report to {report_path}")

if __name__ == "__main__":
    main()
