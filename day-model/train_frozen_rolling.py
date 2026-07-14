"""
Frozen-vs-CSS Experiment Orchestrator.

Trains Arm B (handpicked frozen features) and Arm C (random frozen placebo)
over the same 8 quarters x 5 ETFs x 3 sides as production (Arm A).

For each (arm, ETF, side, quarter):
  - Loads the frozen feature list for that ETF (from data/frozen/)
  - Calls train_etf with frozen_features set, artifact_subdir=arm name,
    and variant_tag to isolate Optuna studies / caches / outputs.

Usage:
    python day-model/train_frozen_rolling.py                     # Train both arms
    python day-model/train_frozen_rolling.py --arm b             # Arm B only
    python day-model/train_frozen_rolling.py --arm c -e 300      # Arm C, single ETF
    python day-model/train_frozen_rolling.py --skip-existing     # Resume support
    python day-model/train_frozen_rolling.py --trials 100        # Optuna trials (default 100)
"""
import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

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

from train_model import (
    train_etf,
    ROLLING_QUARTERS,
    ROLLING_MODELS_DIR,
    ROLLING_DATA_DIR,
    quarter_label,
    ETF_CLI_MAP,
)
import joblib

FROZEN_DIR = HERE / "data" / "frozen"
ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
SIDES = ["single", "long", "short"]

ARM_CONFIG = {
    "b": {
        "list_file": FROZEN_DIR / "arm_b_handpicked.json",
        "subdir": "frozen_armB",
        "variant_tag": "_armB",
        "label": "Arm B (handpicked frozen)",
    },
    "c": {
        "list_file": FROZEN_DIR / "arm_c_random.json",
        "subdir": "frozen_armC",
        "variant_tag": "_armC",
        "label": "Arm C (random frozen placebo)",
    },
}


def load_frozen_lists(list_file: Path) -> dict:
    with open(list_file) as f:
        return json.load(f)


def check_model_exists(arm: str, etf: str, side: str, lb_date: str,
                       ratio_type: str = "sortino", blend_cpcv: bool = True) -> bool:
    """Check whether the rolling artifacts for one (arm, etf, side, quarter) exist."""
    cfg = ARM_CONFIG[arm]
    from train_model import rolling_tag
    tag = rolling_tag(etf, side, lb_date)
    tag_suffix = ""
    if ratio_type != "sharpe":
        tag_suffix += f"_{ratio_type}"
    if blend_cpcv:
        tag_suffix += "_blended"
    tag_suffix += cfg["variant_tag"]
    tag += tag_suffix

    model_dir = ROLLING_MODELS_DIR / cfg["subdir"]
    data_dir = ROLLING_DATA_DIR / cfg["subdir"]
    return (model_dir / f"linear_{tag}.joblib").exists() \
        and (model_dir / f"scaler_{tag}.joblib").exists() \
        and (data_dir / f"results_{tag}.json").exists()


def train_single(arm: str, etf: str, side: str, lb_date: str,
                 frozen_feats: list, args, loyo_jobs: int):
    cfg = ARM_CONFIG[arm]
    tag_desc = f"[{arm.upper()}] {etf}/{side}/{quarter_label(lb_date)}"
    t0 = time.perf_counter()
    try:
        res = train_etf(
            etf, n_trials=args.trials, side=side,
            use_cache=not args.no_cache,
            optuna_n_jobs=args.optuna_jobs,
            bootstrap_n_jobs=args.bootstrap_jobs,
            loyo_n_jobs=loyo_jobs,
            skip_step1=True,
            skip_step2=False,
            lockbox_date=lb_date,
            window_years=args.window_years,
            rolling=True,
            target_transform="none",
            post_hoc_calibrate=False,
            early=False,
            sharpe_objective=False,
            blend_cpcv=True,
            ratio_type="sortino",
            frozen_features=frozen_feats,
            artifact_subdir=cfg["subdir"],
            variant_tag=cfg["variant_tag"],
        )
        elapsed = time.perf_counter() - t0
        print(f"  {tag_desc} elapsed {elapsed:.1f}s")
        return res
    except Exception as e:
        print(f"  [ERROR] {tag_desc} failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_arm(arm: str, args, etfs: list, sides: list, quarters: list):
    cfg = ARM_CONFIG[arm]
    print(f"\n{'#' * 80}")
    print(f"# {cfg['label']}")
    print(f"# subdir={cfg['subdir']}  variant_tag={cfg['variant_tag']}")
    print(f"{'#' * 80}")

    frozen_lists = load_frozen_lists(cfg["list_file"])

    loyo_jobs = args.loyo_jobs
    if loyo_jobs < 1:
        loyo_jobs = max(1, (os.cpu_count() or 4) // max(1, args.optuna_jobs))

    skipped = 0
    trained = 0
    failed = 0
    t_arm_start = time.perf_counter()

    for lb_date in quarters:
        ql = quarter_label(lb_date)
        print(f"\n=== Quarter {ql} (lockbox={lb_date}) ===")
        for etf in etfs:
            if etf not in frozen_lists:
                print(f"  [SKIP] No frozen list for {etf}")
                continue
            frozen_feats = frozen_lists[etf]
            for side in sides:
                if args.skip_existing and check_model_exists(
                        arm, etf, side, lb_date,
                        ratio_type="sortino", blend_cpcv=True):
                    print(f"  [{arm.upper()}] {etf}/{side}/{ql} exists, skipping.")
                    skipped += 1
                    continue
                res = train_single(arm, etf, side, lb_date, frozen_feats,
                                   args, loyo_jobs)
                if res is None:
                    failed += 1
                else:
                    trained += 1

    elapsed = time.perf_counter() - t_arm_start
    print(f"\n{cfg['label']} done in {elapsed/60:.1f}min "
          f"(trained={trained}, skipped={skipped}, failed={failed})")


def main():
    ap = argparse.ArgumentParser(description="Frozen-vs-CSS rolling trainer")
    ap.add_argument("--arm", default="both", choices=["b", "c", "both"],
                    help="Which arm to train. Default: both.")
    ap.add_argument("-e", "--etf", default="all",
                    help="300|50|500|588000|159915|all. Default: all.")
    ap.add_argument("--side", default=None,
                    choices=["single", "long", "short"],
                    help="Train one side only. Default: all three.")
    ap.add_argument("-q", "--quarter", default=None,
                    help="Single quarter e.g. 2024Q1. Default: all 8.")
    ap.add_argument("-t", "--trials", type=int, default=100,
                    help="Optuna trials per model. Default 100.")
    ap.add_argument("--window-years", type=int, default=6,
                    help="Training window years. Default 6.")
    ap.add_argument("--no-cache", action="store_true",
                    help="Disable disk caches (force recompute).")
    ap.add_argument("--skip-existing", action="store_true",
                    help="Skip (arm, etf, side, quarter) combos already on disk.")
    ap.add_argument("--optuna-jobs", type=int,
                    default=max(1, (os.cpu_count() or 4)),
                    help="Parallel Optuna workers per model.")
    ap.add_argument("--bootstrap-jobs", type=int,
                    default=max(1, (os.cpu_count() or 4)),
                    help="Parallel stability bootstrap workers.")
    ap.add_argument("--loyo-jobs", type=int, default=-1,
                    help="LOYO fold workers (-1 = auto).")
    args = ap.parse_args()

    # Resolve ETF list
    if args.etf == "all":
        etfs = list(ETFS)
    else:
        etfs = [ETF_CLI_MAP.get(args.etf, args.etf)]

    # Resolve sides
    if args.side is not None:
        sides = [args.side]
    else:
        sides = list(SIDES)

    # Resolve quarters
    if args.quarter:
        rq = args.quarter.upper()
        y = int(rq[:4])
        q = int(rq[5])
        m = q * 3
        quarters = [f"{y}-{m:02d}-01"]
    else:
        quarters = list(ROLLING_QUARTERS)

    print(f"Frozen-vs-CSS Experiment Config:")
    print(f"  Arms: {args.arm}")
    print(f"  ETFs: {etfs}")
    print(f"  Sides: {sides}")
    print(f"  Quarters: {[quarter_label(q) for q in quarters]}")
    print(f"  Trials: {args.trials}  Window: {args.window_years}y")
    print(f"  Jobs: optuna={args.optuna_jobs}, bootstrap={args.bootstrap_jobs}")
    print(f"  Skip existing: {args.skip_existing}")

    arms = ["b", "c"] if args.arm == "both" else [args.arm]
    for arm in arms:
        run_arm(arm, args, etfs, sides, quarters)

    print("\nDone. Run analyze_frozen_vs_css.py to evaluate.")


if __name__ == "__main__":
    main()
