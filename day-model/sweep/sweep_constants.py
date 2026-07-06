"""
Sweep feature-selection pipeline constants and measure their impact on
lockbox IC, Tail IC, feature counts, and selection stability.

Usage
-----
    # Sweep one constant
    python day-model/sweep_constants.py -e 300 --side single --constant SCREEN_FDR --values 0.15,0.25,0.50,0.80

    # STABILITY_B sweep (also measures Jaccard stability across 3 seeds)
    python day-model/sweep_constants.py -e 300 --side single --constant STABILITY_B --values 40,60,80,120

    # Quick Optuna trials (default 20)
    python day-model/sweep_constants.py -e 300 --side single --constant STABILITY_PI --values 0.60,0.75,0.80,0.90 --trials 30

Output: CSV file with one row per sweep value.
"""
import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path

# Pin BLAS threads BEFORE any numpy import
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=Warning)

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

# Import from train_model
import train_model as tm

# Suppress optuna logging
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)


# ─────────────────────────────────────────────────────────────────────────────
# Constants that can be swept and their valid value types
# ─────────────────────────────────────────────────────────────────────────────
SWEEPABLE = {
    "STABILITY_B":               int,
    "STABILITY_PI":              float,
    "STABILITY_Q":               int,
    "SCREEN_FDR":                float,
    "ACTIVE_FEATURE_ESS_DIVISOR": float,
}

DEFAULT_RANGES = {
    "STABILITY_B":               [40, 60, 80, 120],
    "STABILITY_PI":              [0.60, 0.70, 0.75, 0.80, 0.85, 0.90],
    "STABILITY_Q":               [15, 25, 35, 50, 70],
    "SCREEN_FDR":                [0.15, 0.25, 0.35, 0.50, 0.65, 0.80],
    "ACTIVE_FEATURE_ESS_DIVISOR": [4.0, 6.0, 8.0, 10.0, 12.0, 16.0],
}


def _load_features_df(etf_name: str):
    """Load and preprocess features parquet (mirrors train_etf logic)."""
    features_path = tm.DATA_DIR / f"features_{etf_name}.parquet"
    if not features_path.exists():
        raise FileNotFoundError(f"Features file not found: {features_path}")
    df = pd.read_parquet(features_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    X_df = df[tm.FEATURES].ffill()
    _col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(_col_med)
    X = tm._to_f32(X_df.values)
    y = df[tm.TARGET].values.astype(np.float32)
    y_scaled = (y * np.float32(100.0)).astype(np.float32)
    return df, X, y, y_scaled


def compute_lockbox_metrics(etf_name: str, side: str):
    """After train_etf finishes, load the saved model/scaler and compute
    lockbox Overall IC, Tail IC, and Monotonicity. Returns dict."""
    tag = etf_name if side == "single" else f"{etf_name}_{side}"
    model_path = tm.MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = tm.MODELS_DIR / f"scaler_{tag}.joblib"

    if not (model_path.exists() and scaler_path.exists()):
        return {"lockbox_ic": np.nan, "lockbox_tail_ic": np.nan,
                "lockbox_mono": np.nan, "n_lockbox": 0}

    import joblib
    model = joblib.load(model_path)
    scaler_meta = joblib.load(scaler_path)
    selected_features = scaler_meta["selected_features"]
    scaler = scaler_meta["scaler"]

    df, _, _, y_scaled = _load_features_df(etf_name)
    X_df = df[selected_features].ffill()
    col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(col_med)
    X = tm._to_f32(X_df.values)

    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled).astype(np.float32)

    lockbox_mask = df["date"] >= pd.Timestamp(tm.LOCKBOX_DATE)
    y_lock = y_scaled[lockbox_mask]
    pred_lock = preds[lockbox_mask]

    if len(y_lock) < 5:
        return {"lockbox_ic": np.nan, "lockbox_tail_ic": np.nan,
                "lockbox_mono": np.nan, "n_lockbox": len(y_lock)}

    lockbox_ic = float(spearmanr(pred_lock, y_lock)[0])
    if np.isnan(lockbox_ic):
        lockbox_ic = 0.0
    lockbox_tail_ic = tm.side_tail_ic(y_lock, pred_lock, side)
    lockbox_mono = tm.compute_decile_monotonicity(y_lock, pred_lock)

    return {
        "lockbox_ic": lockbox_ic,
        "lockbox_tail_ic": lockbox_tail_ic,
        "lockbox_mono": lockbox_mono,
        "n_lockbox": int(len(y_lock)),
    }


def run_single_sweep_value(etf_name: str, side: str, constant: str, value,
                           n_trials: int = 20, use_cache: bool = False,
                           optuna_jobs: int = 1, bootstrap_jobs: int = 1,
                           loyo_jobs: int = 1, seed_override: int = None):
    """
    Monkey-patch ONE constant, run train_etf, compute lockbox metrics.
    Returns a result dict for this sweep point.
    """
    # Save original value
    original_value = getattr(tm, constant)
    cast_fn = SWEEPABLE[constant]
    patched_value = cast_fn(value)

    # Apply monkey-patch
    setattr(tm, constant, patched_value)

    # Override seed for stability measurement (STABILITY_B sweep)
    original_seed = tm.PILOT_SEED
    if seed_override is not None:
        tm.PILOT_SEED = seed_override
        np.random.seed(seed_override)
        import random
        random.seed(seed_override)

    tag = etf_name if side == "single" else f"{etf_name}_{side}"
    result = {
        "etf": etf_name,
        "side": side,
        "constant": constant,
        "value": patched_value,
        "seed": seed_override if seed_override is not None else original_seed,
    }

    t0 = time.perf_counter()
    try:
        train_result = tm.train_etf(
            etf_name,
            n_trials=n_trials,
            side=side,
            use_cache=use_cache,
            optuna_n_jobs=optuna_jobs,
            bootstrap_n_jobs=bootstrap_jobs,
            loyo_n_jobs=loyo_jobs,
        )

        if train_result is None:
            result["status"] = "FAILED"
            result["error"] = "train_etf returned None"
        else:
            result["status"] = "OK"

            # Extract pipeline diagnostics from train_result
            diag = train_result.get("diagnostics", {})
            screening = diag.get("screening", {})
            stability = diag.get("stability", {})
            model_quality = diag.get("model_quality", {})

            result["screen_keep"] = screening.get("keep_count", np.nan)
            result["css_keep"] = stability.get("keep_count", np.nan)
            result["final_features"] = len(train_result.get("selected_features", []))
            result["active_features"] = len(train_result.get("active_features", []))
            result["val_ic"] = train_result.get("selection_val_overall_ic", np.nan)
            result["val_tail_ic"] = train_result.get("selection_val_tail_ic", np.nan)
            result["val_outer_ic"] = train_result.get("selection_val_outer_overall_ic", np.nan)
            result["val_outer_tail_ic"] = train_result.get("selection_val_outer_tail_ic", np.nan)
            result["condition_number"] = model_quality.get("condition_number", np.nan)
            result["ess_pct"] = model_quality.get("effective_sample_size_pct", np.nan)
            result["gini"] = model_quality.get("gini_coefficient", np.nan)

            # Compute lockbox metrics
            lockbox = compute_lockbox_metrics(etf_name, side)
            result.update(lockbox)

            # Store selected feature names for Jaccard computation
            result["_selected_features"] = train_result.get("selected_features", [])

    except Exception as e:
        import traceback
        result["status"] = "ERROR"
        result["error"] = str(e)
        traceback.print_exc()
    finally:
        # Restore original value
        setattr(tm, constant, original_value)
        if seed_override is not None:
            tm.PILOT_SEED = original_seed
            np.random.seed(original_seed)
            import random
            random.seed(original_seed)

    result["elapsed_sec"] = round(time.perf_counter() - t0, 1)
    return result


def jaccard_similarity(list_a, list_b):
    """Jaccard index between two lists of feature names."""
    set_a, set_b = set(list_a), set(list_b)
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def run_sweep(etf_name: str, side: str, constant: str, values: list,
              n_trials: int = 20, use_cache: bool = False,
              optuna_jobs: int = 1, bootstrap_jobs: int = 1,
              loyo_jobs: int = 1, measure_stability: bool = False):
    """
    Run the sweep over all values. For STABILITY_B, optionally measures
    Jaccard stability across 3 seeds.
    Returns a list of result dicts and the output DataFrame.
    """
    results = []

    if measure_stability and constant == "STABILITY_B":
        # Run each value 3 times with different seeds, compute Jaccard
        seeds = [42, 123, 456]
        for value in values:
            print(f"\n{'='*70}")
            print(f"[SWEEP] {constant} = {value} (stability measurement, 3 seeds)")
            print(f"{'='*70}")
            seed_results = []
            for seed in seeds:
                r = run_single_sweep_value(
                    etf_name, side, constant, value,
                    n_trials=n_trials, use_cache=use_cache,
                    optuna_jobs=optuna_jobs, bootstrap_jobs=bootstrap_jobs,
                    loyo_jobs=loyo_jobs, seed_override=seed,
                )
                seed_results.append(r)

            # Compute pairwise Jaccard similarities
            feature_sets = [r.get("_selected_features", []) for r in seed_results]
            jaccards = []
            for i in range(len(feature_sets)):
                for j in range(i + 1, len(feature_sets)):
                    jaccards.append(jaccard_similarity(feature_sets[i], feature_sets[j]))

            # Aggregate: mean of 3 runs
            agg = {k: np.nanmean([r.get(k, np.nan) for r in seed_results])
                   for k in ["lockbox_ic", "lockbox_tail_ic", "lockbox_mono",
                             "screen_keep", "css_keep", "final_features",
                             "active_features", "val_ic", "val_tail_ic",
                             "condition_number", "elapsed_sec"]}
            agg.update({
                "etf": etf_name,
                "side": side,
                "constant": constant,
                "value": value,
                "seed": "mean(42,123,456)",
                "jaccard_mean": float(np.mean(jaccards)) if jaccards else np.nan,
                "jaccard_min": float(np.min(jaccards)) if jaccards else np.nan,
                "status": "OK" if all(r.get("status") == "OK" for r in seed_results) else "PARTIAL",
            })
            results.append(agg)

    else:
        for value in values:
            print(f"\n{'='*70}")
            print(f"[SWEEP] {constant} = {value}")
            print(f"{'='*70}")
            r = run_single_sweep_value(
                etf_name, side, constant, value,
                n_trials=n_trials, use_cache=use_cache,
                optuna_jobs=optuna_jobs, bootstrap_jobs=bootstrap_jobs,
                loyo_jobs=loyo_jobs,
            )
            results.append(r)

    # Build DataFrame (drop internal keys)
    rows = []
    for r in results:
        row = {k: v for k, v in r.items() if not k.startswith("_")}
        rows.append(row)

    df = pd.DataFrame(rows)
    return results, df


def print_summary(df: pd.DataFrame, constant: str):
    """Print a compact summary table to stdout."""
    print(f"\n{'='*70}")
    print(f"SWEEP SUMMARY: {constant}")
    print(f"{'='*70}")
    cols = [c for c in ["value", "status", "screen_keep", "css_keep",
                        "final_features", "active_features",
                        "val_ic", "val_tail_ic",
                        "lockbox_ic", "lockbox_tail_ic", "lockbox_mono",
                        "condition_number", "elapsed_sec"]
            if c in df.columns]
    if "jaccard_mean" in df.columns:
        cols.append("jaccard_mean")
    print(df[cols].to_string(index=False, float_format=lambda x: f"{x:.4f}" if isinstance(x, float) else str(x)))

    # Highlight best lockbox_tail_ic
    if "lockbox_tail_ic" in df.columns and df["lockbox_tail_ic"].notna().any():
        best_idx = df["lockbox_tail_ic"].idxmax()
        best_val = df.loc[best_idx, "value"]
        best_ic = df.loc[best_idx, "lockbox_tail_ic"]
        print(f"\n  >> Best Tail IC: value={best_val}, lockbox_tail_ic={best_ic:+.4f}")

    if "lockbox_ic" in df.columns and df["lockbox_ic"].notna().any():
        best_idx = df["lockbox_ic"].idxmax()
        best_val = df.loc[best_idx, "value"]
        best_ic = df.loc[best_idx, "lockbox_ic"]
        print(f"  >> Best Overall IC: value={best_val}, lockbox_ic={best_ic:+.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Sweep day-model feature-selection pipeline constants.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("-e", "--etf", default="300",
                    help="ETF identifier: 300|50|500|588000|159915 (default: 300)")
    ap.add_argument("--side", default="single", choices=["single", "long", "short"],
                    help="Model side (default: single)")
    ap.add_argument("--constant", required=True, choices=list(SWEEPABLE.keys()),
                    help="Which constant to sweep")
    ap.add_argument("--values", default=None,
                    help="Comma-separated values to sweep. "
                         "If omitted, uses the default range for that constant.")
    ap.add_argument("--trials", type=int, default=20,
                    help="Optuna trials per sweep value (default: 20)")
    ap.add_argument("--no-cache", action="store_true",
                    help="Disable disk caches (recommended for sweeps)")
    ap.add_argument("--optuna-jobs", type=int, default=1,
                    help="Parallel Optuna workers (default: 1 for stability)")
    ap.add_argument("--bootstrap-jobs", type=int, default=1,
                    help="Parallel bootstrap workers for CSS (default: 1)")
    ap.add_argument("--loyo-jobs", type=int, default=1,
                    help="Parallel LOYO fold workers (default: 1)")
    ap.add_argument("--stability", action="store_true",
                    help="For STABILITY_B: measure Jaccard stability across 3 seeds")
    ap.add_argument("-o", "--output", default=None,
                    help="Output CSV path (default: day-model/sweep_{constant}_{etf}.csv)")
    args = ap.parse_args()

    etf_name = tm.ETF_CLI_MAP.get(args.etf, args.etf)

    if args.values:
        cast_fn = SWEEPABLE[args.constant]
        values = [cast_fn(v.strip()) for v in args.values.split(",")]
    else:
        values = DEFAULT_RANGES[args.constant]

    output_path = args.output or str(HERE / f"sweep_{args.constant}_{etf_name}.csv")

    print(f"Sweep Configuration:")
    print(f"  ETF:       {etf_name}")
    print(f"  Side:      {args.side}")
    print(f"  Constant:  {args.constant} (current={getattr(tm, args.constant)})")
    print(f"  Values:    {values}")
    print(f"  Trials:    {args.trials}")
    print(f"  Cache:     {'OFF' if args.no_cache else 'ON'}")
    print(f"  Stability: {'YES' if args.stability else 'NO'}")
    print(f"  Output:    {output_path}")
    print()

    t_start = time.perf_counter()
    results, df = run_sweep(
        etf_name=etf_name,
        side=args.side,
        constant=args.constant,
        values=values,
        n_trials=args.trials,
        use_cache=not args.no_cache,
        optuna_jobs=args.optuna_jobs,
        bootstrap_jobs=args.bootstrap_jobs,
        loyo_jobs=args.loyo_jobs,
        measure_stability=args.stability,
    )

    df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")
    print(f"Total sweep time: {time.perf_counter() - t_start:.1f}s")

    print_summary(df, args.constant)


if __name__ == "__main__":
    main()
