"""
Rolling Day-Model Training Orchestrator.

Trains 8 quarterly rolling models (2024Q1-Q4 + 2025Q1-Q4) per ETF/side,
each using a 6-year rolling window with relative validation blocks.

Usage:
    python3 day-model/train_rolling.py -e all                  # All 8 quarters, all ETFs
    python3 day-model/train_rolling.py -e 300 -q 2024Q1        # Single quarter
    python3 day-model/train_rolling.py -e all --window-years 6  # Custom window
    python3 day-model/train_rolling.py -e all --trials 50       # Fewer trials
    python3 day-model/train_rolling.py -e all --skip-existing   # Resume: skip already-trained models
    python3 day-model/train_rolling.py -e all -j 4              # Train 4 quarters in parallel
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
    DATA_DIR,
    quarter_label,
    rolling_tag,
    ETF_CLI_MAP,
)


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
# Main
# ============================================================
def _check_model_exists(etf: str, side: str, lb_date: str) -> bool:
    """Check if rolling model artifacts already exist."""
    tag = rolling_tag(etf, side, lb_date)
    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"
    result_path = ROLLING_DATA_DIR / f"results_{tag}.json"
    return model_path.exists() and scaler_path.exists() and result_path.exists()


def _load_existing_results() -> dict:
    """Load all existing rolling results from disk."""
    all_results = {}
    if not ROLLING_DATA_DIR.exists():
        return all_results
    for p in sorted(ROLLING_DATA_DIR.glob("results_*.json")):
        try:
            with open(p) as f:
                r = json.load(f)
            lb = r.get("lockbox_date", "")
            tag = r.get("tag", "")
            if lb and tag:
                all_results.setdefault(lb, {})[tag] = r
        except Exception as e:
            print(f"  [WARNING] Failed to load {p.name}: {e}")
    return all_results


def _train_single(etf: str, side: str, lb_date: str, args, skip_step1: bool,
                  skip_step2: bool, loyo_jobs: int) -> tuple:
    """Train a single (etf, side, quarter) model. Returns (tag, result_dict_or_None)."""
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
        elapsed = time.perf_counter() - t0
        print(f"  [{tag}] elapsed {elapsed:.1f}s")
        return tag, res
    except Exception as e:
        print(f"  [ERROR] Failed {tag}: {e}")
        import traceback
        traceback.print_exc()
        return tag, None


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
                    help="Parallel Optuna workers per model.")
    ap.add_argument("--bootstrap-jobs", type=int, default=max(1, (os.cpu_count() or 4)),
                    help="Parallel stability bootstrap workers.")
    ap.add_argument("--loyo-jobs", type=int, default=-1,
                    help="LOYO fold workers (-1 = auto).")
    ap.add_argument("-j", "--quarter-jobs", type=int, default=1,
                    help="Train N quarters in parallel (reduces optuna-jobs per quarter). "
                         "Default 1 (sequential, full CPU per model).")
    ap.add_argument("--skip-existing", action="store_true",
                    help="Skip models that already have artifacts on disk (resume support).")
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
        m = q * 3  # Q1=Mar, Q2=Jun, Q3=Sep, Q4=Dec
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

    # Resolve quarter parallelism: split CPU budget across parallel quarters
    quarter_jobs = max(1, min(args.quarter_jobs, len(quarters)))
    if quarter_jobs > 1:
        args.optuna_jobs = max(1, args.optuna_jobs // quarter_jobs)
        args.bootstrap_jobs = max(1, args.bootstrap_jobs // quarter_jobs)
        print(f"  [INFO] Quarter parallelism={quarter_jobs}: reduced per-model jobs to optuna={args.optuna_jobs}, bootstrap={args.bootstrap_jobs}")

    loyo_jobs = args.loyo_jobs
    if loyo_jobs < 1:
        loyo_jobs = max(1, (os.cpu_count() or 4) // max(1, args.optuna_jobs * quarter_jobs))

    print(f"Rolling Training Config:")
    print(f"  ETFs: {etfs}")
    print(f"  Sides: {sides}")
    print(f"  Quarters: {[quarter_label(q) for q in quarters]}")
    print(f"  Window: {args.window_years} years")
    print(f"  Trials: {args.trials}")
    print(f"  Jobs: optuna={args.optuna_jobs}, bootstrap={args.bootstrap_jobs}, loyo={loyo_jobs}")
    print(f"  Quarter parallelism: {quarter_jobs}")
    print(f"  Skip existing: {args.skip_existing}")
    print()

    # Pre-check: skip already-trained models
    if args.skip_existing:
        original_quarters = list(quarters)
        skip_count = 0
        new_quarters = []
        for lb_date in quarters:
            all_exist = all(_check_model_exists(e, s, lb_date) for e in etfs for s in sides)
            if all_exist:
                skip_count += 1
            else:
                new_quarters.append(lb_date)
        if skip_count > 0:
            print(f"  [SKIP] {skip_count} quarter(s) already trained, {len(new_quarters)} remaining.")
        quarters = new_quarters

    if not quarters:
        print("All models already trained. Use generate_rolling_report.py to produce the report.")
        return

    # Train models
    t_total = time.perf_counter()

    if quarter_jobs <= 1:
        # Sequential: one quarter at a time (max CPU per model)
        for lb_date in quarters:
            ql = quarter_label(lb_date)
            print(f"\n{'#' * 80}")
            print(f"# Rolling Quarter: {ql} (lockbox={lb_date})")
            print(f"{'#' * 80}")
            for etf in etfs:
                for side in sides:
                    _train_single(etf, side, lb_date, args, skip_step1, skip_step2, loyo_jobs)
    else:
        # Parallel: multiple quarters simultaneously
        # Build flat list of (quarter, etf, side) tasks
        tasks = [(lb, etf, side) for lb in quarters for etf in etfs for side in sides]

        # Group by quarter for parallel dispatch
        from concurrent.futures import ProcessPoolExecutor, as_completed
        quarter_groups = {}
        for lb, etf, side in tasks:
            quarter_groups.setdefault(lb, []).append((etf, side))

        for lb_date in sorted(quarter_groups.keys()):
            ql = quarter_label(lb_date)
            print(f"\n{'#' * 80}")
            print(f"# Rolling Quarter: {ql} (lockbox={lb_date})")
            print(f"{'#' * 80}")
            # Within a quarter, train sequentially (Optuna uses parallel workers internally)
            for etf, side in quarter_groups[lb_date]:
                _train_single(etf, side, lb_date, args, skip_step1, skip_step2, loyo_jobs)

    total_elapsed = time.perf_counter() - t_total
    print(f"\nTotal training time: {total_elapsed:.1f}s ({total_elapsed / 60:.1f}min)")

    # Load all results for warning summary
    all_results = _load_existing_results()

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

    print(f"\nTo generate the comprehensive strategy report, run:")
    print(f"  python3 day-model/generate_rolling_report.py")


if __name__ == "__main__":
    main()
