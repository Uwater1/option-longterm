"""
Meta-Optuna: Treat the 5 feature-selection pipeline constants as Optuna
hyperparameters and let TPE intelligently explore the combined space.

Instead of a grid sweep (5 x 4-6 values = 1000+ full pipeline runs),
this runs ONE Optuna study (~200 trials) over all 5 pipeline constants
+ model hyperparameters simultaneously.

NOTE: SCREEN_FDR has been removed — BH screening is bypassed (fdr=0.99)
in train_model.py.  The remaining 5 tunable constants are:
STABILITY_B, STABILITY_PI, STABILITY_Q, ESS_DIVISOR, and CSS_CORR_THRESHOLD.

Usage
-----
    python day-model/sweep/meta_optuna.py -e all --trials 200 --jobs 5
    python day-model/sweep/meta_optuna.py -e 300 --side long --trials 200 --jobs 4

Output: day-model/sweep/meta_{etf}_{side}_results.csv + best config printout.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import warnings
from itertools import combinations
from pathlib import Path

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
from sklearn.preprocessing import StandardScaler
import joblib
import optuna
from optuna.storages import JournalStorage
from optuna.storages.journal import JournalFileBackend
from joblib import Parallel, delayed

optuna.logging.set_verbosity(optuna.logging.WARNING)

HERE = Path(__file__).resolve().parent
SWEEP_DIR = HERE  # Output CSVs and optuna logs go here
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import train_model as tm

# ─────────────────────────────────────────────────────────────────────────────
# Data Loading (once at startup)
# ─────────────────────────────────────────────────────────────────────────────

def load_and_split(etf_name: str):
    """Load features, compute splits, return all arrays needed."""
    features_path = tm.DATA_DIR / f"features_{etf_name}.parquet"
    if not features_path.exists():
        raise FileNotFoundError(f"Features file not found: {features_path}")

    df = pd.read_parquet(features_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])

    X_df = df[tm.FEATURES].ffill()
    col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(col_med)
    X = tm._to_f32(X_df.values)
    y = df[tm.TARGET].values.astype(np.float32)
    y_scaled = (y * np.float32(100.0)).astype(np.float32)

    # Working set (pre-lockbox)
    working_mask = df["date"] < tm.LOCKBOX_DATE
    working_idx = np.where(working_mask)[0]

    # Validation blocks
    sel_val_mask = np.zeros(len(df), dtype=bool)
    for s, e in tm.VAL_BLOCKS:
        sel_val_mask |= (df["date"] >= pd.Timestamp(s)) & (df["date"] < pd.Timestamp(e))

    # Inner validation
    inner_mask = np.zeros(len(df), dtype=bool)
    for s, e in tm.VAL_BLOCKS_INNER:
        inner_mask |= (df["date"] >= pd.Timestamp(s)) & (df["date"] < pd.Timestamp(e))

    # Selection train = working minus validation minus embargo
    sel_train_mask = working_mask & (~sel_val_mask)
    gap_days = 10
    sel_train_dates = df["date"][sel_train_mask]
    keep = np.ones(len(sel_train_dates), dtype=bool)
    for s, e in tm.VAL_BLOCKS:
        emb_s = pd.Timestamp(s) - pd.Timedelta(days=gap_days)
        emb_e = pd.Timestamp(e) + pd.Timedelta(days=gap_days)
        keep[(sel_train_dates >= emb_s) & (sel_train_dates <= emb_e)] = False
    sel_train_indices = df.index[sel_train_mask][keep]
    sel_train_mask_final = np.zeros(len(df), dtype=bool)
    sel_train_mask_final[sel_train_indices] = True

    st_idx = np.where(sel_train_mask_final)[0]
    sv_idx = np.where(sel_val_mask & working_mask)[0]
    si_idx = np.where(inner_mask & working_mask)[0]

    # Lockbox
    lb_idx = np.where(df["date"] >= pd.Timestamp(tm.LOCKBOX_DATE))[0]

    data = {
        "df": df,
        "X": X, "y_scaled": y_scaled,
        "X_st": tm._to_f32(X[st_idx]), "y_st": y_scaled[st_idx].astype(np.float32),
        "X_si": tm._to_f32(X[si_idx]), "y_si": y_scaled[si_idx].astype(np.float32),
        "X_lb": tm._to_f32(X[lb_idx]), "y_lb": y_scaled[lb_idx].astype(np.float32),
        "dates_st": df["date"].iloc[st_idx].reset_index(drop=True),
        "n_total_features": X.shape[1],
        "etf_name": etf_name,
    }
    return data


# ─────────────────────────────────────────────────────────────────────────────
# Cached Selection Pipeline
# ─────────────────────────────────────────────────────────────────────────────

_selection_cache = {}

def run_selection_cached(X_st, y_st,
                         stability_b, stability_pi, stability_q,
                         etf_name, bootstrap_jobs=1):
    """Run screen → CSS → VIF. Results cached in memory by constants tuple.
    SCREEN_FDR is fixed at 0.99 (bypass) — not a tunable constant."""
    vif_threshold = 5.0 if etf_name == "50ETF" else 10.0
    cache_key = (etf_name, X_st.shape,
                 stability_b, round(stability_pi, 2), stability_q, vif_threshold)

    if cache_key in _selection_cache:
        return _selection_cache[cache_key]

    # Patch globals temporarily
    orig_q = tm.STABILITY_Q
    tm.STABILITY_Q = stability_q

    try:
        # Step 1: Screening (bypassed — fdr=0.99 lets all features through)
        screen_mask, p_vals, rhos = tm.run_screening(X_st, y_st, fdr_level=0.99)
        n_screened = int(screen_mask.sum())

        if n_screened < 3:
            result = {"selected_idx": np.array([], dtype=int), "scores": np.array([]),
                      "n_screened": n_screened, "n_css": 0, "n_vif": 0}
            _selection_cache[cache_key] = result
            return result

        # Step 2: CSS
        stab_idx, stab_scores = tm.run_stability_selection(
            X_st, y_st, screen_mask, rhos,
            B=stability_b, pi=stability_pi, n_jobs=bootstrap_jobs,
        )

        if len(stab_idx) < 1:
            result = {"selected_idx": np.array([], dtype=int), "scores": stab_scores,
                      "n_screened": n_screened, "n_css": 0, "n_vif": 0}
            _selection_cache[cache_key] = result
            return result

        # Step 3: VIF
        vif_idx = tm.run_vif_pruning(X_st, stab_idx, tm.FEATURES, threshold=vif_threshold)

        # Step 3b: Condition pruning
        cond_idx = tm.run_cond_pruning(X_st, vif_idx, tm.FEATURES, cond_cap=100.0)

        result = {
            "selected_idx": np.asarray(cond_idx),
            "scores": stab_scores,
            "n_screened": n_screened,
            "n_css": len(stab_idx),
            "n_vif": len(cond_idx),
        }
    finally:
        tm.STABILITY_Q = orig_q

    _selection_cache[cache_key] = result
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Fast Model Evaluation (no LOYO — just train→predict→validate)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_config(data, selected_idx, model_type, model_params, k_weight,
                    ess_divisor, side="single"):
    """Fit model on selection train, predict on validation inner + lockbox.
    Returns objective metric and diagnostics dict."""
    X_st = data["X_st"][:, selected_idx]
    y_st = data["y_st"]
    X_si = data["X_si"][:, selected_idx]
    y_si = data["y_si"]
    X_lb = data["X_lb"][:, selected_idx]
    y_lb = data["y_lb"]

    k_sel = len(selected_idx)
    if k_sel < 2:
        return -1e9, {"error": "too few features"}

    # Standardize
    scaler = StandardScaler()
    X_st_sc = tm._to_f32(scaler.fit_transform(X_st))
    X_si_sc = tm._to_f32(scaler.transform(X_si))
    X_lb_sc = tm._to_f32(scaler.transform(X_lb))

    # Sample weights
    w = tm.compute_sample_weights(y_st, k_weight).astype(np.float32)
    sqrt_w = np.sqrt(w)[:, np.newaxis]
    X_st_w = X_st_sc * sqrt_w
    y_st_w = y_st * sqrt_w[:, 0]

    # ESS
    sum_w = w.sum()
    sum_w2 = (w ** 2).sum()
    ess = float((sum_w ** 2) / sum_w2) if sum_w2 > 1e-10 else float(len(w))
    ess_pct = ess / len(w)

    # Kill-switch: active feature cap
    max_active = max(3, int(ess / ess_divisor))

    # Fit model
    model = tm._build_model(model_type, model_params)
    model.fit(X_st_w, y_st_w)

    active_k = int(np.sum(np.abs(model.coef_) > 1e-5))

    # Regularized condition number check
    K_sel_vars = X_st_w.shape[1]
    if K_sel_vars > 1:
        s_vars = np.linalg.svd(X_st_w, compute_uv=False)
        s_max_sq = float(s_vars.max() ** 2)
        s_min_sq = float(s_vars.min() ** 2)
        
        N_samples = X_st_w.shape[0]
        if model_type == "ridge":
            reg_coef = float(model_params.get("ridge_alpha", 1.0))
        elif model_type == "skglm_huber_l1":
            reg_coef = float(N_samples * 0.1 * model_params.get("skglm_huber_l1_alpha", 1e-5))
        elif model_type == "skglm_mcp":
            reg_coef = float(N_samples * 0.1 * model_params.get("skglm_mcp_alpha", 1e-5))
        else:
            reg_coef = 0.0
            
        s_sq_max = s_max_sq + reg_coef
        s_sq_min = s_min_sq + reg_coef
        reg_kappa = float(np.sqrt(s_sq_max / s_sq_min)) if s_sq_min > 1e-10 else float("inf")
    else:
        reg_kappa = 1.0

    if reg_kappa > 10000.0:
        return -1e9, {"error": f"reg_kappa={reg_kappa:.2f} > 10000.0"}

    # Hard constraints
    if active_k > max_active:
        return -1e9, {"error": f"active_k={active_k} > cap={max_active}"}
    if active_k < min(3, max_active):
        return -1e9, {"error": f"active_k={active_k} < floor"}

    # Predict on validation inner
    pred_si = model.predict(X_si_sc).astype(np.float32)
    val_ic = tm.spearman_ic(y_si, pred_si)
    val_tail_ic = tm.side_tail_ic(y_si, pred_si, side)

    # Kill-switch: basic signal quality
    if val_ic <= 0:
        return -1e9, {"error": "val_ic <= 0"}

    # Predict on lockbox
    pred_lb = model.predict(X_lb_sc).astype(np.float32)
    lb_ic = float(spearmanr(pred_lb, y_lb)[0]) if len(y_lb) >= 5 else 0.0
    if np.isnan(lb_ic):
        lb_ic = 0.0
    lb_tail_ic = tm.side_tail_ic(y_lb, pred_lb, side)
    lb_mono = tm.compute_decile_monotonicity(y_lb, pred_lb)

    # Gini concentration
    coefs = model.coef_
    abs_coefs = np.abs(coefs)
    sum_abs = abs_coefs.sum()
    if sum_abs > 1e-10:
        sorted_c = np.sort(abs_coefs)
        idx = np.arange(1, len(sorted_c) + 1)
        gini = float((2.0 * (idx * sorted_c).sum()) / (len(sorted_c) * sum_abs) - (len(sorted_c) + 1) / len(sorted_c))
    else:
        gini = 0.0
    if gini > 0.85:
        return -1e9, {"error": f"gini={gini:.3f} > 0.85"}

    # Objective: weighted combination of validation metrics
    # Primary: Val Tail IC (tail prediction power)
    # Secondary: Val Overall IC (generalization)
    # Small parsimony bonus
    objective = 0.60 * val_tail_ic + 0.30 * val_ic + 0.10 * (-k_sel / 50.0)

    diag = {
        "val_ic": val_ic, "val_tail_ic": val_tail_ic,
        "lb_ic": lb_ic, "lb_tail_ic": lb_tail_ic, "lb_mono": lb_mono,
        "k_selected": k_sel, "active_k": active_k,
        "ess_pct": ess_pct, "gini": gini,
    }
    return objective, diag


# ─────────────────────────────────────────────────────────────────────────────
# Optuna Objective
# ─────────────────────────────────────────────────────────────────────────────

def make_objective(data, side, bootstrap_jobs):
    """Create the Optuna objective function with data pre-loaded."""
    etf_name = data["etf_name"]

    def objective(trial):
        # ── Pipeline constants (SCREEN_FDR removed — bypassed at 0.99) ──
        stability_b = trial.suggest_int("stability_b", 15, 80)
        stability_pi = trial.suggest_float("stability_pi", 0.65, 0.95)
        stability_q = trial.suggest_int("stability_q", 5, 30)
        ess_divisor = trial.suggest_float("ess_divisor", 4.0, 16.0)

        # ── Model hyperparameters ──
        model_type = trial.suggest_categorical("model_type", ["skglm_huber_l1", "skglm_mcp"])
        k_weight = trial.suggest_float("k_weight", 0.0, 1.5)

        if model_type == "skglm_huber_l1":
            alpha = trial.suggest_float("alpha", 1e-4, 10.0, log=True)
            model_params = {"skglm_huber_l1_alpha": alpha, "skglm_huber_delta": 1.35}
        else:
            alpha = trial.suggest_float("alpha", 1e-4, 10.0, log=True)
            gamma = trial.suggest_float("gamma", 3.0, 10.0)
            model_params = {"skglm_mcp_alpha": alpha, "skglm_mcp_gamma": gamma, "skglm_mcp_delta": 1.35}

        # ── Feature selection (cached) ──
        sel = run_selection_cached(
            data["X_st"], data["y_st"],
            stability_b, stability_pi, stability_q,
            etf_name, bootstrap_jobs=bootstrap_jobs,
        )

        selected_idx = sel["selected_idx"]
        trial.set_user_attr("n_screened", sel["n_screened"])
        trial.set_user_attr("n_css", sel["n_css"])
        trial.set_user_attr("n_vif", sel["n_vif"])

        if len(selected_idx) < 2:
            trial.set_user_attr("constraints", [1e9])
            return -1e9

        # ── Evaluate ──
        obj, diag = evaluate_config(
            data, selected_idx, model_type, model_params,
            k_weight, ess_divisor, side,
        )

        # Store diagnostics
        for k, v in diag.items():
            trial.set_user_attr(k, v)
        trial.set_user_attr("selected_features",
                            [tm.FEATURES[i] for i in selected_idx])

        # Constraints for TPE
        constraints = [0.0] if obj > -1e8 else [1e9]
        trial.set_user_attr("constraints", constraints)

        return obj

    return objective


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_etf_study(etf_name, side, n_trials, bootstrap_jobs, seed, jobs=1):
    """Run one meta-Optuna study for a single ETF."""
    tag = f"meta_{etf_name}_{side}"
    print(f"\n{'='*70}")
    print(f"Meta-Optuna: {etf_name} ({side}) | Trials: {n_trials}")
    print(f"{'='*70}")

    t0 = time.perf_counter()
    data = load_and_split(etf_name)
    print(f"Loaded {data['X_st'].shape[0]} train, {data['X_si'].shape[0]} val-inner, "
          f"{data['X_lb'].shape[0]} lockbox rows, {data['n_total_features']} features.")

    db_path = SWEEP_DIR / f"{tag}_optuna.log"
    if db_path.exists():
        db_path.unlink()
    storage = JournalStorage(JournalFileBackend(str(db_path)))

    def constraints_func(trial):
        return trial.user_attrs.get("constraints", [1e9])

    sampler = optuna.samplers.TPESampler(seed=seed, constraints_func=constraints_func)
    study = optuna.create_study(study_name=tag, storage=storage, direction="maximize",
                                sampler=sampler, load_if_exists=False)
    obj_fn = make_objective(data, side, bootstrap_jobs)

    t_study = time.perf_counter()
    if jobs > 1:
        def run_one(worker_seed):
            local_sampler = optuna.samplers.TPESampler(
                seed=worker_seed, constraints_func=constraints_func)
            local_study = optuna.load_study(
                study_name=tag, storage=storage, sampler=local_sampler)
            local_study.optimize(obj_fn, n_trials=1)
        Parallel(n_jobs=jobs, backend="loky")(
            delayed(run_one)(seed + i) for i in range(n_trials))
    else:
        study.optimize(obj_fn, n_trials=n_trials)

    study = optuna.load_study(study_name=tag, storage=storage)
    elapsed = time.perf_counter() - t_study
    print(f"Study completed in {elapsed:.1f}s ({elapsed/max(1,n_trials):.1f}s/trial)")

    # Results
    completed = [t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE
                 and t.value is not None and t.value > -1e8]
    print(f"\nTrials: {len(study.trials)} total, {len(completed)} feasible")

    if not completed:
        print(f"[{etf_name}] No feasible trials found!")
        return None

    # Sort by objective
    best = max(completed, key=lambda t: t.value)
    print(f"\n{'='*70}")
    print(f"BEST TRIAL (#{best.number}, objective={best.value:+.4f})")
    print(f"{'='*70}")

    # Pipeline constants
    print("\n  Pipeline Constants:")
    for name in ["stability_b",
                 "stability_pi", "stability_q", "ess_divisor"]:
        print(f"    {name:25s} = {best.params[name]}")

    # Model params
    print("\n  Model Hyperparameters:")
    for name in ["model_type", "k_weight", "alpha"]:
        if name in best.params:
            print(f"    {name:25s} = {best.params[name]}")
    if best.params.get("model_type") == "skglm_mcp" and "gamma" in best.params:
        print(f"    {'gamma':25s} = {best.params['gamma']}")

    # Diagnostics
    print("\n  Diagnostics:")
    for name in ["n_screened", "n_css", "n_vif", "k_selected", "active_k",
                 "val_ic", "val_tail_ic", "lb_ic", "lb_tail_ic", "lb_mono",
                 "ess_pct", "gini"]:
        val = best.user_attrs.get(name, "N/A")
        if isinstance(val, float):
            print(f"    {name:25s} = {val:+.4f}")
        else:
            print(f"    {name:25s} = {val}")

    sel_feats = best.user_attrs.get("selected_features", [])
    print(f"\n  Selected Features ({len(sel_feats)}):")
    for f in sel_feats:
        print(f"    - {f}")

    # Compare to current defaults
    print(f"\n{'='*70}")
    print("COMPARISON: Best vs Current Defaults")
    print(f"{'='*70}")
    defaults = {
        "stability_b": 100,
        "stability_pi": 0.55, "stability_q": 35, "ess_divisor": 8.0,
    }
    print(f"  {'Constant':25s} {'Current':>10s} {'Best':>10s} {'Change':>10s}")
    print(f"  {'-'*55}")
    for name, cur in defaults.items():
        best_val = best.params[name]
        if isinstance(cur, int):
            diff = f"{best_val - cur:+d}"
        else:
            diff = f"{best_val - cur:+.2f}"
        print(f"  {name:25s} {cur:>10} {best_val:>10} {diff:>10s}")

    # Save results CSV
    rows = []
    for t in completed:
        row = {"trial": t.number, "objective": t.value}
        row.update(t.params)
        for attr in ["n_screened", "n_css", "n_vif", "k_selected", "active_k",
                      "val_ic", "val_tail_ic", "lb_ic", "lb_tail_ic", "lb_mono",
                      "ess_pct", "gini"]:
            row[attr] = t.user_attrs.get(attr, np.nan)
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("objective", ascending=False)
    csv_path = SWEEP_DIR / f"{tag}_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to: {csv_path}")

    # Cleanup
    try:
        if db_path.exists():
            db_path.unlink()
    except Exception:
        pass

    return best.params


ALL_ETFS = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]


def main():
    ap = argparse.ArgumentParser(description="Meta-Optuna: pipeline constants as hyperparameters.")
    ap.add_argument("-e", "--etf", default="all",
                    help="ETF: 300|50|500|588000|159915|all (default: all)")
    ap.add_argument("--side", default="single", choices=["single", "long", "short"])
    ap.add_argument("--trials", type=int, default=200, help="Number of Optuna trials per ETF")
    ap.add_argument("--jobs", type=int, default=1, help="Parallel Optuna workers")
    ap.add_argument("--bootstrap-jobs", type=int, default=1, help="CSS bootstrap workers")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if args.etf == "all":
        etfs = ALL_ETFS
    else:
        etfs = [tm.ETF_CLI_MAP.get(args.etf, args.etf)]

    print(f"Meta-Optuna: {len(etfs)} ETFs x {args.trials} trials")
    print(f"Side: {args.side} | Bootstrap jobs: {args.bootstrap_jobs}")
    print(f"Ranges: B[15-80] PI[0.65-0.95] Q[5-30] ESS_DIV[4-16]")
    print(f"(SCREEN_FDR removed — BH screening bypassed at 0.99)")

    all_best = {}
    for etf in etfs:
        try:
            params = run_etf_study(etf, args.side, args.trials, args.bootstrap_jobs,
                                   args.seed, args.jobs)
            if params:
                all_best[etf] = params
        except Exception as e:
            print(f"  [{etf}] FAILED: {e}")
            import traceback
            traceback.print_exc()

    # Cross-ETF summary
    if all_best:
        print(f"\n{'='*70}")
        print("CROSS-ETF SUMMARY: Optimal Pipeline Constants")
        print(f"{'='*70}")
        consts = ["stability_b",
                  "stability_pi", "stability_q", "ess_divisor"]
        header = f"  {'Constant':25s}" + "".join(f" {e:>12s}" for e in all_best.keys())
        print(header)
        print(f"  {'-'*len(header)}")
        defaults = {"stability_b": 100,
                    "stability_pi": 0.55, "stability_q": 35, "ess_divisor": 8.0}
        for c in consts:
            vals = [all_best[e].get(c, float('nan')) for e in all_best.keys()]
            row = f"  {c:25s}" + "".join(f" {v:>12}" for v in vals)
            print(row)
        medians = {c: np.median([all_best[e].get(c, float('nan')) for e in all_best.keys()])
                   for c in consts}
        print(f"  {'MEDIAN':25s}" + "".join(f" {medians[c]:>12}" for c in consts))
        print(f"  {'CURRENT':25s}" + "".join(f" {defaults[c]:>12}" for c in consts))


if __name__ == "__main__":
    main()
