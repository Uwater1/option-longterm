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
def _check_model_exists(etf: str, side: str, lb_date: str, early: bool = False,
                        target_transform: str = "none", post_hoc_calibrate: bool = False,
                        sharpe_objective: bool = False, ratio_type: str = "sharpe",
                        sharpe_weight_override: float = None, embargo_days: int = 10,
                        blend_cpcv: bool = True) -> bool:
    """Check if rolling model artifacts already exist."""
    tag = rolling_tag(etf, side, lb_date)
    if early:
        tag += "_early"
    tag_suffix = ""
    if target_transform != "none":
        tag_suffix += f"_{target_transform}"
    if post_hoc_calibrate:
        tag_suffix += "_calibrated"
    if sharpe_objective:
        tag_suffix += "_sharpe"
    if ratio_type != "sharpe":
        tag_suffix += f"_{ratio_type}"
    if sharpe_weight_override is not None:
        tag_suffix += f"_sw{sharpe_weight_override:.2f}"
    if embargo_days != 10:
        tag_suffix += f"_emb{embargo_days}"
    if blend_cpcv:
        tag_suffix += "_blended"
    tag += tag_suffix
    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"
    result_path = ROLLING_DATA_DIR / f"results_{tag}.json"
    return model_path.exists() and scaler_path.exists() and result_path.exists()


def _load_existing_results(early: bool = False) -> dict:
    """Load all existing rolling results from disk."""
    all_results = {}
    if not ROLLING_DATA_DIR.exists():
        return all_results
    pattern = "results_*_early.json" if early else "results_*.json"
    for p in sorted(ROLLING_DATA_DIR.glob(pattern)):
        if not early and p.name.endswith("_early.json"):
            continue
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
    if getattr(args, "earlyNoGood", False):
        tag += "_early"
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
            target_transform=args.target_transform,
            post_hoc_calibrate=args.post_hoc_calibrate,
            early=getattr(args, "earlyNoGood", False),
            sharpe_objective=getattr(args, "sharpe_objective", False),
            blend_cpcv=getattr(args, "blend_cpcv", True),
            ratio_type=getattr(args, "ratio_type", "sortino"),
        )
        elapsed = time.perf_counter() - t0
        print(f"  [{tag}] elapsed {elapsed:.1f}s")
        return tag, res
    except Exception as e:
        print(f"  [ERROR] Failed {tag}: {e}")
        import traceback
        traceback.print_exc()
        return tag, None


def smooth_rolling_models(etfs, sides, target_transform="none", early=False, sharpe_objective=False, ratio_type="sortino", blend_cpcv=True):
    """Smoothes/blends rolling model coefficients sequentially over the last 2-3 quarters."""
    print(f"\nRunning Cross-Quarter Rolling Model Smoothing...")
    import joblib
    from sklearn.preprocessing import StandardScaler
    
    suffix = f"_{target_transform}" if target_transform != "none" else ""
    if sharpe_objective:
        suffix += "_sharpe"
    if ratio_type != "sharpe":
        suffix += f"_{ratio_type}"
    if blend_cpcv:
        suffix += "_blended"
    early_suffix = "_early" if early else ""
    
    # Sort the quarterly dates
    sorted_quarters = list(ROLLING_QUARTERS)
    
    for etf in etfs:
        for side in sides:
            for t_idx in range(len(sorted_quarters)):
                curr_date = sorted_quarters[t_idx]
                tag_t = rolling_tag(etf, side, curr_date) + early_suffix + suffix
                
                model_path_t = ROLLING_MODELS_DIR / f"linear_{tag_t}.joblib"
                scaler_path_t = ROLLING_MODELS_DIR / f"scaler_{tag_t}.joblib"
                if not (model_path_t.exists() and scaler_path_t.exists()):
                    continue
                
                prior_dates = []
                if t_idx - 1 >= 0:
                    prior_dates.append(sorted_quarters[t_idx - 1])
                if t_idx - 2 >= 0:
                    prior_dates.append(sorted_quarters[t_idx - 2])
                
                valid_priors = []
                for p_date in prior_dates:
                    tag_p = rolling_tag(etf, side, p_date) + early_suffix + suffix
                    m_p_path = ROLLING_MODELS_DIR / f"linear_{tag_p}.joblib"
                    s_p_path = ROLLING_MODELS_DIR / f"scaler_{tag_p}.joblib"
                    if m_p_path.exists() and s_p_path.exists():
                        valid_priors.append((tag_p, m_p_path, s_p_path))
                
                if not valid_priors:
                    print(f"  [{tag_t}] No prior rolling models found. Skipping smoothing.")
                    continue
                
                print(f"  [{tag_t}] Smoothing with {len(valid_priors)} prior models...")
                model_t = joblib.load(model_path_t)
                scaler_meta_t = joblib.load(scaler_path_t)
                
                feats_t = scaler_meta_t["selected_features"]
                coef_t = model_t.coef_
                intercept_t = getattr(model_t, "intercept_", 0.0)
                scaler_t = scaler_meta_t["scaler"]
                
                feats_map_t = dict(zip(feats_t, coef_t))
                means_map_t = dict(zip(feats_t, scaler_t.mean_))
                vars_map_t = dict(zip(feats_t, scaler_t.var_))
                
                if len(valid_priors) == 2:
                    weights = [0.5, 0.3, 0.2]
                else:
                    weights = [0.6, 0.4]
                
                priors_data = []
                for tag_p, m_p_path, s_p_path in valid_priors:
                    m_p = joblib.load(m_p_path)
                    s_p = joblib.load(s_p_path)
                    priors_data.append((m_p, s_p))
                
                union_feats = set(feats_t)
                for m_p, s_p in priors_data:
                    union_feats.update(s_p["selected_features"])
                union_feats = sorted(list(union_feats))
                
                smoothed_coefs = []
                smoothed_means = []
                smoothed_vars = []
                
                intercepts = [intercept_t]
                for m_p, s_p in priors_data:
                    intercepts.append(getattr(m_p, "intercept_", 0.0))
                smoothed_intercept = sum(w * intercept for w, intercept in zip(weights, intercepts))
                
                for f in union_feats:
                    vals_coef = []
                    vals_coef.append(feats_map_t.get(f, 0.0))
                    for m_p, s_p in priors_data:
                        feats_p = s_p["selected_features"]
                        coef_p = m_p.coef_
                        feats_map_p = dict(zip(feats_p, coef_p))
                        vals_coef.append(feats_map_p.get(f, 0.0))
                    
                    smoothed_c = sum(w * c for w, c in zip(weights, vals_coef))
                    smoothed_coefs.append(smoothed_c)
                    
                    if f in feats_map_t:
                        f_mean = means_map_t[f]
                        f_var = vars_map_t[f]
                    else:
                        found = False
                        for m_p, s_p in priors_data:
                            if f in s_p["selected_features"]:
                                feats_map_p = dict(zip(s_p["selected_features"], s_p["scaler"].mean_))
                                vars_map_p = dict(zip(s_p["selected_features"], s_p["scaler"].var_))
                                f_mean = feats_map_p[f]
                                f_var = vars_map_p[f]
                                found = True
                                break
                        if not found:
                            f_mean = 0.0
                            f_var = 1.0
                    
                    smoothed_means.append(f_mean)
                    smoothed_vars.append(f_var)
                
                new_scaler = StandardScaler()
                new_scaler.mean_ = np.array(smoothed_means, dtype=np.float64)
                new_scaler.var_ = np.array(smoothed_vars, dtype=np.float64)
                new_scaler.scale_ = np.sqrt(new_scaler.var_ + 1e-10)
                new_scaler.n_samples_seen_ = scaler_t.n_samples_seen_
                
                model_t.coef_ = np.array(smoothed_coefs, dtype=np.float64)
                model_t.intercept_ = float(smoothed_intercept)
                model_t.n_features_in_ = len(union_feats)
                
                scaler_meta_t["scaler"] = new_scaler
                scaler_meta_t["selected_features"] = union_feats
                
                joblib.dump(model_t, model_path_t)
                joblib.dump(scaler_meta_t, scaler_path_t)


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
    ap.add_argument("--target-transform", default="none", choices=["none", "rank", "gauss"],
                    help="Target transform: none|rank|gauss")
    ap.add_argument("--post-hoc-calibrate", action="store_true", default=False,
                    help="Enable post-hoc Spearman IC calibration of active coefficients")
    ap.add_argument("--earlyNoGood", action="store_true",
                    help="Predict early window (10:00 to 13:05, exiting at close of 13:00~13:05 bar) [ABORTED - DO NOT RUN]")
    ap.add_argument("--sharpe-objective", action="store_true", dest="sharpe_objective", default=False,
                    help="Optimizes Optuna hyperparameters using validation set tail-Sharpe objective instead of Tail IC. Set to False by default, use --sharpe-objective to enable.")
    ap.add_argument("--blend-cpcv", action="store_true", dest="blend_cpcv", default=True,
                    help="Enable CPCV out-of-sample path blending of single refit and bagged model (default True)")
    ap.add_argument("--no-blend-cpcv", action="store_false", dest="blend_cpcv",
                    help="Disable CPCV out-of-sample path blending of single refit and bagged model")
    ap.add_argument("--smooth-quarters", action="store_true", dest="smooth_quarters", default=True,
                    help="Enable cross-quarter EWMA smoothing of model coefficients (default True)")
    ap.add_argument("--no-smooth-quarters", action="store_false", dest="smooth_quarters",
                    help="Disable cross-quarter EWMA smoothing of model coefficients")
    ap.add_argument("--ratio-type", default="sortino", choices=["sharpe", "sortino"],
                    help="V5 ratio type: sharpe or sortino (default sortino)")
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
            all_exist = all(_check_model_exists(
                e, s, lb_date, early=args.earlyNoGood,
                target_transform=args.target_transform,
                post_hoc_calibrate=args.post_hoc_calibrate,
                sharpe_objective=args.sharpe_objective,
                ratio_type=getattr(args, "ratio_type", "sortino"),
                blend_cpcv=getattr(args, "blend_cpcv", True)
            ) for e in etfs for s in sides)
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

    if getattr(args, "smooth_quarters", True):
        smooth_rolling_models(
            etfs, sides,
            target_transform=args.target_transform,
            early=args.earlyNoGood,
            sharpe_objective=args.sharpe_objective,
            ratio_type=getattr(args, "ratio_type", "sortino"),
            blend_cpcv=getattr(args, "blend_cpcv", True)
        )

    # Load all results for warning summary
    all_results = _load_existing_results(early=args.earlyNoGood)

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
