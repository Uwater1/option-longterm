"""
Phase 3: Generate day-model/REPORT.md summary from training results.
"""
import json
import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
REPORT_PATH = HERE / "REPORT.md"

ETF_ORDER = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]

def main():
    print("Generating day-model REPORT.md...")
    
    results_dict = {}
    for p in DATA_DIR.glob("results_*.json"):
        try:
            with open(p) as f:
                r = json.load(f)
                results_dict[r["etf"]] = r
        except Exception as e:
            print(f"  [WARNING] Failed to load {p.name}: {e}")
            
    if not results_dict:
        print("  [ERROR] No results files found in data directory. Run train_model.py first.")
        return

    # Start writing report
    lines = []
    lines.append("# Day-Model Remake Optimization Report")
    lines.append("")
    lines.append("This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.")
    lines.append("")
    lines.append("## Out-of-Sample Lockbox Performance (2024-03 to Last Day)")
    lines.append("")
    lines.append("| ETF | Selected Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        feats_count = len(r["selected_features"])
        model_type = r["best_params"]["model_type"]
        overall_ic = r["lockbox_overall_ic"]
        tail_ic = r["lockbox_tail_ic"]
        lines.append(f"| {etf} | {feats_count} | `{model_type}` | {overall_ic:+.4f} | {tail_ic:+.4f} |")
        
    lines.append("")
    lines.append("## Detailed Trial Metrics & Optimization Objectives")
    lines.append("")
    lines.append("| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        m = r["best_raw_metrics"]
        # M1 (IR), M2 (Mean), M3 (Hit Rate), M5 (Monotonicity), M6 (Spread)
        lines.append(f"| {etf} | {m[0]:.4f} | {m[1]:+.4f} | {m[2]*100:.1f}% | {m[4]:.4f} | {m[5]*100:+.4f}% |")
        
    lines.append("")
    lines.append("## Selected Features per ETF")
    lines.append("")
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        lines.append(f"### {etf}")
        lines.append(f"- **Total selected features**: {len(r['selected_features'])}")
        lines.append("- **Features**: " + ", ".join([f"`{f}`" for f in r["selected_features"]]))
        lines.append("")
        
    lines.append("## Methodology Overview")
    lines.append("1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).")
    lines.append("2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.")
    lines.append("3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.")
    lines.append("4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.")
    lines.append("5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.")
    lines.append("6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).")
    
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))
        
    print(f"REPORT.md written to {REPORT_PATH}")

if __name__ == "__main__":
    main()
