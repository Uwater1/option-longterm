"""
Rolling Day-Model Training Orchestrator.

Trains 8 quarterly rolling models (2024Q1-Q4 + 2025Q1-Q4) per ETF/side,
each using a 6-year rolling window with relative validation blocks.
Produces ROLLING_REPORT.md with IC decay tables and model health warnings.

Usage:
    python3 day-model/train_rolling.py -e all                  # All 8 quarters, all ETFs
    python3 day-model/train_rolling.py -e 300 -q 2024Q1        # Single quarter
    python3 day-model/train_rolling.py -e all --window-years 6  # Custom window
    python3 day-model/train_rolling.py -e all --trials 50       # Fewer trials
    python3 day-model/train_rolling.py -e all --report-only     # Regenerate report only
"""
import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# Bootstrap path for imports
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

import numpy as np
import pandas as pd

from train_model import (
    train_etf,
    LOCKBOX_DATE as DEFAULT_LOCKBOX,
    ROLLING_QUARTERS,
    ROLLING_DATA_DIR,
    ROLLING_MODELS_DIR,
    ROLLING_PLOTS_DIR,
    DATA_DIR,
    MODELS_DIR,
    quarter_label,
    rolling_tag,
    ETF_CLI_MAP,
)

ROLLING_REPORT_PATH = HERE / "ROLLING_REPORT.md"

ETF_ORDER = ["300ETF", "500ETF", "588000ETF", "159915ETF", "50ETF"]


# ============================================================
# Warning System (pre-lockbox validation metrics only)
# ============================================================
def evaluate_warnings(all_results: dict) -> dict:
    """Evaluate model health using ONLY pre-lockbox validation metrics.

    Parameters
    ----------
    all_results : dict
        {quarter_date: {tag: results_dict}}

    Returns
    -------
    dict : {(quarter, tag): {"status": "OK"|"WARNING"|"ALERT", "reasons": [...]}}
    """
    warnings_out = {}
    prev_outer_ic = {}  # (etf, side) -> previous quarter outer IC

    for quarter in sorted(all_results.keys()):
        for tag, res in all_results[quarter].items():
            outer_ic = res.get("selection_val_outer_overall_ic", 0) or 0
            outer_tail_ic = res.get("selection_val_outer_tail_ic", 0) or 0

            status = "OK"
            reasons = []

            # Check outer validation IC (most recent held-out block before lockbox)
            if outer_ic < 0:
                reasons.append(f"outer_IC={outer_ic:+.4f}<0")
            if outer_tail_ic < 0:
                reasons.append(f"outer_tail_IC={outer_tail_ic:+.4f}<0")

            # Cross-model decay: compare to previous quarter's outer IC
            etf = res.get("etf", "")
            side = res.get("side", "single")
            prev = prev_outer_ic.get((etf, side))
            if prev is not None and prev > 0.005 and outer_ic < prev * 0.5:
                decay_pct = 100 * (1 - outer_ic / prev)
                reasons.append(f"IC_decay={decay_pct:.0f}%>50%")

            # Status determination
            if len(reasons) >= 2:
                status = "ALERT"
            elif any("decay" in r for r in reasons):
                status = "ALERT"
            elif reasons:
                status = "WARNING"

            warnings_out[(quarter, tag)] = {"status": status, "reasons": reasons}
            prev_outer_ic[(etf, side)] = outer_ic

    return warnings_out


# ============================================================
# Rolling Report Generator
# ============================================================
def generate_rolling_report(all_results: dict, warnings_dict: dict):
    """Generate ROLLING_REPORT.md from collected rolling results."""
    lines = []
    lines.append("# Day-Model Rolling Training Report")
    lines.append("")
    lines.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Quarters: {sorted(all_results.keys())}")
    lines.append(f"Window: 6 years (rolling)")
    lines.append("")

    # Summary table
    lines.append("## Model Health Summary")
    lines.append("")
    lines.append("| Quarter | Tag | ETF | Side | Outer IC | Outer Tail IC | Deflated Val IC | Status | Reason |")
    lines.append("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

    for quarter in sorted(all_results.keys()):
        ql = quarter_label(quarter)
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            etf = res.get("etf", "")
            side = res.get("side", "single")
            outer_ic = res.get("selection_val_outer_overall_ic", 0) or 0
            outer_tail_ic = res.get("selection_val_outer_tail_ic", 0) or 0
            deflated_ic = res.get("deflated_val_ic", 0) or 0
            w = warnings_dict.get((quarter, tag), {"status": "OK", "reasons": []})
            status = w["status"]
            reason = ", ".join(w["reasons"]) if w["reasons"] else "-"
            status_icon = {"OK": "OK", "WARNING": "WARN", "ALERT": "ALERT"}.get(status, status)
            lines.append(
                f"| {ql} | {tag} | {etf} | `{side}` | {outer_ic:+.4f} | {outer_tail_ic:+.4f} "
                f"| {deflated_ic:+.4f} | {status_icon} | {reason} |"
            )
    lines.append("")

    # Warning legend
    lines.append("### Warning Levels")
    lines.append("")
    lines.append("- **OK**: Outer validation IC >= 0 and no significant decay.")
    lines.append("- **WARNING**: Outer IC < 0 OR outer Tail IC < 0 (single metric negative).")
    lines.append("- **ALERT**: Both outer IC and Tail IC negative, OR IC decay > 50% vs previous quarter.")
    lines.append("")

    # Per-ETF IC timeline
    lines.append("## IC Timeline by ETF")
    lines.append("")
    for etf in ETF_ORDER:
        etf_quarters = []
        for quarter in sorted(all_results.keys()):
            for tag, res in all_results[quarter].items():
                if res.get("etf") == etf and res.get("side") == "long":
                    etf_quarters.append((quarter, tag, res))
        if not etf_quarters:
            continue

        lines.append(f"### {etf} (long side)")
        lines.append("")
        lines.append("| Quarter | Outer IC | Outer Tail IC | Inner IC | # Selected | # Active |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
        for quarter, tag, res in etf_quarters:
            ql = quarter_label(quarter)
            outer_ic = res.get("selection_val_outer_overall_ic", 0) or 0
            outer_tail = res.get("selection_val_outer_tail_ic", 0) or 0
            inner_ic = res.get("selection_val_overall_ic", 0) or 0
            n_sel = len(res.get("selected_features", []))
            n_act = len(res.get("active_features", []))
            lines.append(f"| {ql} | {outer_ic:+.4f} | {outer_tail:+.4f} | {inner_ic:+.4f} | {n_sel} | {n_act} |")
        lines.append("")

    # Feature stability across quarters
    lines.append("## Feature Stability Across Quarters")
    lines.append("")
    for etf in ETF_ORDER:
        etf_features = {}
        for quarter in sorted(all_results.keys()):
            for tag, res in all_results[quarter].items():
                if res.get("etf") == etf and res.get("side") == "long":
                    active = set(res.get("active_features", []))
                    etf_features[quarter_label(quarter)] = active
        if not etf_features:
            continue

        all_feats = set()
        for s in etf_features.values():
            all_feats |= s

        lines.append(f"### {etf} (long side)")
        lines.append("")
        qls = sorted(etf_features.keys())
        header = "| Feature | " + " | ".join(qls) + " | Freq |"
        sep = "| :--- | " + " | ".join([":---:" for _ in qls]) + " | :---: |"
        lines.append(header)
        lines.append(sep)

        feat_counts = {}
        for f in sorted(all_feats):
            row = [f]
            count = 0
            for ql in qls:
                present = f in etf_features[ql]
                row.append("Y" if present else "-")
                if present:
                    count += 1
            row.append(f"{count}/{len(qls)}")
            feat_counts[f] = count
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append("1. **Rolling Window**: Each model trains on the most recent 6 years of data before the lockbox date.")
    lines.append("2. **Relative Validation Blocks**: 6 non-overlapping 3-month blocks placed backward from the lockbox with 10-day embargo gaps.")
    lines.append("   - 4 inner blocks (for Optuna tuning)")
    lines.append("   - 2 outer blocks (held-out, closest to lockbox — most recent and most relevant)")
    lines.append("3. **Warning System**: Based on pre-lockbox outer validation IC only (no OOS peeking).")
    lines.append("4. **Artifacts**: Models in `models/rolling/`, results in `data/rolling/`, plots in `plots/rolling/`.")
    lines.append("")

    report_text = "\n".join(lines)
    with open(ROLLING_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nRolling report written to: {ROLLING_REPORT_PATH}")
    return report_text


# ============================================================
# Main
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="Rolling day-model training orchestrator")
    ap.add_argument("-e", "--etf", default="all", help="300|50|500|588000|159915|all")
    ap.add_argument("-q", "--quarter", default=None,
                    help="Single quarter (e.g. 2024Q1). Default: all 8 quarters.")
    ap.add_argument("-t", "--trials", type=int, default=100, help="Optuna trials per model")
    ap.add_argument("--window-years", type=int, default=6, help="Training window (default 6)")
    ap.add_argument("--side", default=None, choices=["single", "long", "short"],
                    help="Train ONE side only. Default: all three sides.")
    ap.add_argument("--no-both", action="store_true", help="Disable training all 3 sides (requires --side).")
    ap.add_argument("--no-cache", action="store_true", help="Disable disk caches.")
    ap.add_argument("--skip-step", nargs="+", choices=["1", "2", "12"], default=[],
                    help="Skip feature selection steps.")
    ap.add_argument("--optuna-jobs", type=int, default=max(1, (os.cpu_count() or 4)),
                    help="Parallel Optuna workers.")
    ap.add_argument("--bootstrap-jobs", type=int, default=max(1, (os.cpu_count() or 4)),
                    help="Parallel stability bootstrap workers.")
    ap.add_argument("--loyo-jobs", type=int, default=-1,
                    help="LOYO fold workers (-1 = auto).")
    ap.add_argument("--report-only", action="store_true",
                    help="Skip training, just regenerate ROLLING_REPORT.md from existing results.")
    args = ap.parse_args()

    # Resolve ETFs
    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]

    # Resolve sides
    if args.no_both or args.side is not None:
        if args.side is None:
            print("[ERROR] --no-both requires --side to be set.")
            sys.exit(2)
        sides = [args.side]
    else:
        sides = ["single", "long", "short"]

    # Resolve quarters
    if args.quarter:
        rq = args.quarter.upper()
        y = int(rq[:4])
        q = int(rq[5])
        m = (q - 1) * 3 + 1
        quarters = [f"{y}-{m:02d}-01"]
    else:
        quarters = list(ROLLING_QUARTERS)

    # Resolve skip steps
    skip_step1 = True
    skip_step2 = False
    if args.skip_step:
        for s in args.skip_step:
            if "1" in s:
                skip_step1 = True
            if "2" in s:
                skip_step2 = True

    loyo_jobs = args.loyo_jobs
    if loyo_jobs < 1:
        loyo_jobs = max(1, (os.cpu_count() or 4) // max(1, args.optuna_jobs))

    print(f"Rolling Training Config:")
    print(f"  ETFs: {etfs}")
    print(f"  Sides: {sides}")
    print(f"  Quarters: {[quarter_label(q) for q in quarters]}")
    print(f"  Window: {args.window_years} years")
    print(f"  Trials: {args.trials}")
    print(f"  Jobs: optuna={args.optuna_jobs}, bootstrap={args.bootstrap_jobs}, loyo={loyo_jobs}")
    print()

    # Collect all results: {lockbox_date: {tag: results_dict}}
    all_results = {}

    if not args.report_only:
        for lb_date in quarters:
            ql = quarter_label(lb_date)
            print(f"\n{'#' * 80}")
            print(f"# Rolling Quarter: {ql} (lockbox={lb_date})")
            print(f"{'#' * 80}")

            quarter_results = {}
            for etf in etfs:
                for side in sides:
                    tag = rolling_tag(etf, side, lb_date)
                    t0 = time.perf_counter()
                    try:
                        res = train_etf(
                            etf, n_trials=args.trials, side=side,
                            use_cache=not args.no_cache,
                            optuna_n_jobs=args.optuna_jobs,
                            bootstrap_n_jobs=args.bootstrap_jobs,
                            loyo_n_jobs=loyo_jobs,
                            skip_step1=skip_step1,
                            skip_step2=skip_step2,
                            lockbox_date=lb_date,
                            window_years=args.window_years,
                            rolling=True,
                        )
                        if res is not None:
                            quarter_results[tag] = res
                    except Exception as e:
                        print(f"  [ERROR] Failed {tag}: {e}")
                        import traceback
                        traceback.print_exc()
                    print(f"  [{tag}] elapsed {time.perf_counter() - t0:.1f}s")

            all_results[lb_date] = quarter_results
    else:
        # Load existing results from rolling data dir
        print("Loading existing rolling results from:", ROLLING_DATA_DIR)
        for p in sorted(ROLLING_DATA_DIR.glob("results_*.json")):
            try:
                with open(p) as f:
                    r = json.load(f)
                lb = r.get("lockbox_date", "")
                tag = r.get("tag", "")
                if lb not in all_results:
                    all_results[lb] = {}
                all_results[lb][tag] = r
            except Exception as e:
                print(f"  [WARNING] Failed to load {p.name}: {e}")

    # Evaluate warnings
    print("\nEvaluating model health warnings...")
    warnings_dict = evaluate_warnings(all_results)

    # Print warning summary
    n_warn = sum(1 for v in warnings_dict.values() if v["status"] == "WARNING")
    n_alert = sum(1 for v in warnings_dict.values() if v["status"] == "ALERT")
    print(f"  Total models: {len(warnings_dict)}")
    print(f"  WARNING: {n_warn}")
    print(f"  ALERT: {n_alert}")
    for (quarter, tag), w in sorted(warnings_dict.items()):
        if w["status"] != "OK":
            print(f"  [{w['status']}] {quarter_label(quarter)} / {tag}: {', '.join(w['reasons'])}")

    # Generate report
    generate_rolling_report(all_results, warnings_dict)


if __name__ == "__main__":
    main()
