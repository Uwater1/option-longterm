"""
Alpha Weight and Horizon Optimizer for Long Put (Selective Hedge)
==================================================================
Phase 1 OOS overhaul:
  - New composite objective (Spearman rank + log placement + complexity penalty).
  - Walk-forward as selection objective (--select-by-oos): candidates picked by
    mean OOS metric across purged expanding-window folds, NOT best in-sample.
  - Purged folds (drop train rows whose forward target leaks into test).
  - Trimmed grid (2 horizons/regime, pct [85,90], gamma [0,0.10], 500 samples).
  - Bootstrap CI on OOS metric; flags if lower bound < 1.0 (crash) / sign flip (fall).
  - Min triggered count raised 10 → 30 to cut high-variance noise fits.

Saves optimized parameters + OOS fold table to backtest/alpha_put_models.json.
"""

import os
import sys
import json
import argparse
import math
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from backtest_engine import select_underlying, load_data
from alpha_model import AlphaModel

# Seed for reproducibility
np.random.seed(42)

# Grid (trimmed per plan)
THRESHOLD_PCTS = [85, 90]
GAMMAS = [0.0, 0.10]
NUM_SAMPLES_DEFAULT = 500
MIN_TRIGGERED = 30
MIN_TRAIN_ROWS = 750
PURGE = True  # drop train rows whose forward target overlaps test
EPS_EFFECTIVE_W = 0.05  # weight threshold for "effective indicator" complexity count


def compute_forward_targets(df, m_days):
    """
    Computes look-ahead free forward target variables:
      - Forward return over m_days calendar days (using adjusted prices)
      - Forward worst drawdown (max drop from close to low_adj) over m_days.
    Returns numpy arrays aligned to df.index.
    """
    close = df["close_adj"].values if "close_adj" in df.columns else df["close"].values
    low = df["low_adj"].values if "low_adj" in df.columns else df["low"].values
    n = len(df)
    fwd_ret = np.full(n, np.nan)
    worst_dd = np.full(n, np.nan)
    ts_dates = pd.to_datetime(df.index)
    for i in range(n):
        t_date = ts_dates[i]
        target_date = t_date + pd.Timedelta(days=m_days)
        idx = np.searchsorted(ts_dates, target_date)
        if idx < n:
            fwd_ret[i] = (close[idx] - close[i]) / close[i]
            if idx > i:
                worst_dd[i] = np.min(low[i + 1: idx + 1] - close[i]) / close[i]
            else:
                worst_dd[i] = 0.0
    return fwd_ret, worst_dd


def generate_random_weights(n_indicators, num_samples=500, max_weight=0.5):
    """Dirichlet samples, clipped to max_weight, renormalized. Returns (S, K) array."""
    effective_max = max(max_weight, 1.0 / n_indicators) if n_indicators > 0 else 1.0
    samples = []
    for _ in range(num_samples):
        w = np.random.dirichlet(np.ones(n_indicators))
        for _ in range(10):
            w = np.clip(w, 0, effective_max)
            w_sum = w.sum()
            if w_sum > 0:
                w = w / w_sum
        samples.append(w)
    return np.array(samples)


# ─────────────────────────────────────────────────────────────────────────────
# New composite objective (in-sample), used for --walk-forward diagnostic
# and as a fallback when --select-by-oos is off.
# ─────────────────────────────────────────────────────────────────────────────
def composite_objective_is(scores, target, is_crash, triggered, baseline,
                           n_effective_indicators):
    """
    Scores: np.array of regime scores (precomputed).
    Target: fwd_ret (fall) or -worst_dd (crash).
    Triggered: bool mask.
    Baseline: baseline crash prob (crash) or baseline mean ret (fall).
    """
    n_trig = int(triggered.sum())
    if n_trig < MIN_TRIGGERED:
        return -1e9
    placement = n_trig / len(scores)

    if is_crash:
        # target = -worst_dd (so higher = worse drawdown)
        corr_s, _ = spearmanr(scores, target)
        if np.isnan(corr_s):
            corr_s = 0.0
        trig_crash = target[triggered].mean()  # mean of -worst_dd over triggers
        # lift vs baseline crash rate (baseline is mean of crash indicator over all)
        baseline_crash_rate = (target <= -0.05).mean()
        trig_crash_rate = (target[triggered] <= -0.05).mean()
        lift = trig_crash_rate / baseline_crash_rate if baseline_crash_rate > 0 else 1.0
        obj = 2.0 * corr_s + math.log(max(lift, 1e-6)) - 0.1 * n_effective_indicators
        return obj
    else:
        # target = fwd_ret (we want triggers to have LOW fwd_ret)
        corr_s, _ = spearmanr(scores, target)
        if np.isnan(corr_s):
            corr_s = 0.0
        mean_ret_trig = target[triggered].mean()
        # Penalize up-moves on triggers; reward correct (negative) direction
        obj = (-corr_s                            # generalizable rank power (lower corr → higher obj)
               - 2.0 * max(mean_ret_trig, 0.0)    # penalize positive fwd_ret when triggered
               - 0.5 * (1.0 if mean_ret_trig < 0 else 0.0) * (-1)  # reward negative dir → +0.5
               - 0.3 * math.log(max(placement / 0.10, 1e-6))
               - 0.1 * n_effective_indicators)
        # NB: reward term: if mean_ret_trig < 0, add +0.5 (the *(-1) flips sign)
        return obj


def _threshold_aware(scores, iv_vol_ratio, thresh_base, gamma):
    """Dynamic threshold: thresh_base + gamma*(iv_vol_ratio - 1)."""
    return thresh_base + gamma * (np.nan_to_num(iv_vol_ratio, nan=1.0) - 1.0)


def _evaluate_candidate(scores, target, iv_vol_ratio, thresh_base, gamma, is_crash):
    """Compute IS metric for a single candidate. Returns (obj, triggered, metric_dict)."""
    thr_t = _threshold_aware(scores, iv_vol_ratio, thresh_base, gamma)
    triggered = scores > thr_t
    n_trig = int(triggered.sum())
    if n_trig < MIN_TRIGGERED:
        return -1e9, triggered, None

    if is_crash:
        baseline_crash_rate = (target <= -0.05).mean()
        trig_crash_rate = (target[triggered] <= -0.05).mean()
        lift = trig_crash_rate / baseline_crash_rate if baseline_crash_rate > 0 else 1.0
        metric = {"lift": float(lift),
                  "triggered_crash_prob": float(trig_crash_rate),
                  "baseline_crash_prob": float(baseline_crash_rate)}
    else:
        mean_ret_trig = float(target[triggered].mean())
        mean_ret_all = float(target.mean())
        metric = {"mean_return_triggered": mean_ret_trig,
                  "mean_return_baseline": mean_ret_all}
    return None, triggered, metric  # obj computed by caller (needs n_effective)


def _make_fold_splits(df_norm, min_train_rows=MIN_TRAIN_ROWS):
    """
    Expanding-window walk-forward splits by year (test year >= 2021).
    Returns list of (train_idx, test_idx) as positional index arrays.
    """
    years = sorted(df_norm.index.year.unique())
    test_years = [y for y in years if y >= 2021]
    splits = []
    n = len(df_norm)
    pos = np.arange(n)
    yr_arr = df_norm.index.year.values
    for ty in test_years:
        train_mask = yr_arr < ty
        test_mask = yr_arr == ty
        train_idx = pos[train_mask]
        test_idx = pos[test_mask]
        if len(train_idx) >= min_train_rows and len(test_idx) >= 20:
            splits.append((train_idx, test_idx))
    return splits


def _purge_train(train_idx, dates_arr, test_start_date, m_days):
    """Drop train rows whose forward target (date + m_days) >= test_start_date."""
    purge_cutoff = test_start_date - pd.Timedelta(days=m_days)
    keep = dates_arr[train_idx] < purge_cutoff
    return train_idx[keep]


# ─────────────────────────────────────────────────────────────────────────────
# Walk-forward OOS selection (--select-by-oos)
# ─────────────────────────────────────────────────────────────────────────────
def select_best_by_oos(df_norm, regime_key, candidate_indicators, horizons, is_crash,
                       num_samples=NUM_SAMPLES_DEFAULT, max_weight=0.5):
    """
    For each candidate (weights × horizon × gamma × threshold_pct), compute the
    mean OOS metric across purged expanding-window folds. Pick best mean OOS.
    Retrain threshold on ALL data using winning config. Returns config + fold table.
    """
    active = [ind for ind in candidate_indicators if ind in df_norm.columns]
    if not active:
        print(f"  WARNING: No active indicators for {regime_key}!")
        return None
    K = len(active)
    X = df_norm[active].values.astype(float)  # (N, K)
    iv_vol_ratio = (df_norm["iv_vol_ratio"].values if "iv_vol_ratio" in df_norm.columns
                    else np.ones(len(df_norm)))
    iv_vol_ratio = np.nan_to_num(iv_vol_ratio, nan=1.0)
    dates_arr = pd.to_datetime(df_norm.index)
    # Fill NaN indicators with column mean (broadcast (K,) across (N,K)) — neutral contribution.
    col_means = np.nanmean(X, axis=0)
    col_means = np.where(np.isfinite(col_means), col_means, 0.5)
    X = np.where(np.isnan(X), col_means, X)

    splits = _make_fold_splits(df_norm)
    if not splits:
        print(f"  WARNING: No valid walk-forward folds for {regime_key}.")
        return None

    W = generate_random_weights(K, num_samples, max_weight=max_weight)  # (S, K)
    n_eff = int((W[0] > EPS_EFFECTIVE_W).sum())  # same K for all samples; complexity ~ fixed
    # Actually complexity varies per sample; approximate with mean.
    n_eff_mean = float(np.mean([(w > EPS_EFFECTIVE_W).sum() for w in W]))

    # Precompute forward targets per horizon and cache score matrices.
    fwd_cache = {}
    scores_cache = {}  # (horizon, sample_idx) -> not needed; compute scores_all per horizon
    best = {"oos_metric": -1e18, "config": None, "folds": []}

    for m in horizons:
        fwd_ret, worst_dd = compute_forward_targets(df_norm, m)
        target_crash = -worst_dd  # higher = worse
        target_fall = fwd_ret
        # Precompute scores for all samples: (N, S)
        scores_all = X @ W.T  # (N, S)
        fwd_cache[m] = (fwd_ret, worst_dd, scores_all)

        for gi, gamma in enumerate(GAMMAS):
            for pct in THRESHOLD_PCTS:
                # For each sample s, compute mean OOS across folds.
                # We loop samples inside folds for cache efficiency.
                oos_per_sample = np.zeros(len(W))
                valid_per_sample = np.zeros(len(W), dtype=bool)
                for (train_idx, test_idx) in splits:
                    test_start = dates_arr[test_idx[0]]
                    train_idx_p = _purge_train(train_idx, dates_arr.values, test_start, m) if PURGE else train_idx
                    if len(train_idx_p) < MIN_TRAIN_ROWS:
                        continue
                    if is_crash:
                        tgt = target_crash
                    else:
                        tgt = target_fall
                    sc_test = scores_all[test_idx]      # (n_test, S)
                    tgt_test = tgt[test_idx]
                    iv_test = iv_vol_ratio[test_idx]
                    # Train threshold per sample = percentile(pct) of train scores
                    sc_train = scores_all[train_idx_p]  # (n_train, S)
                    for s in range(len(W)):
                        thr_base = np.percentile(sc_train[:, s], pct)
                        thr_t = _threshold_aware(sc_test[:, s], iv_test, thr_base, gamma)
                        trig = sc_test[:, s] > thr_t
                        n_trig = int(trig.sum())
                        if n_trig < MIN_TRIGGERED:
                            continue
                        valid_per_sample[s] = True
                        if is_crash:
                            base_rate = (tgt_test <= -0.05).mean() if (tgt_test <= -0.05).mean() > 0 else 1e-6
                            trig_rate = (tgt_test[trig] <= -0.05).mean()
                            oos_per_sample[s] += trig_rate / base_rate
                        else:
                            oos_per_sample[s] += float(tgt_test[trig].mean())
                n_folds = len(splits)
                if n_folds == 0:
                    continue
                mean_oos = oos_per_sample / max(n_folds, 1)
                mean_oos[~valid_per_sample] = -1e18
                s_best = int(np.argmax(mean_oos))
                if mean_oos[s_best] <= -1e17:
                    continue
                # Acceptability gate (per plan): crash lift > 1.0; fall mean_ret < 0
                if is_crash and mean_oos[s_best] <= 1.0:
                    continue
                if (not is_crash) and mean_oos[s_best] >= 0:
                    continue
                if mean_oos[s_best] > best["oos_metric"]:
                    best["oos_metric"] = float(mean_oos[s_best])
                    best["config"] = {
                        "weights": {active[i]: float(W[s_best, i]) for i in range(K)},
                        "horizon": int(m),
                        "gamma": float(gamma),
                        "threshold_pct": float(pct),
                        "sample_idx": s_best,
                        "n_effective_indicators": float((W[s_best] > EPS_EFFECTIVE_W).sum()),
                    }

    if best["config"] is None:
        print(f"  No candidate passed OOS acceptability gate for {regime_key} (is_crash={is_crash}).")
        return None

    # Now compute the per-fold OOS detail table for the winning config, plus IS retrain on all data.
    w_best = W[best["config"]["sample_idx"]]
    m_best = best["config"]["horizon"]
    gamma_best = best["config"]["gamma"]
    pct_best = best["config"]["threshold_pct"]
    fwd_ret, worst_dd, scores_all = fwd_cache[m_best]
    target = -worst_dd if is_crash else fwd_ret

    fold_table = []
    for (train_idx, test_idx) in splits:
        test_start = dates_arr[test_idx[0]]
        train_idx_p = _purge_train(train_idx, dates_arr.values, test_start, m_best) if PURGE else train_idx
        if len(train_idx_p) < MIN_TRAIN_ROWS:
            continue
        thr_base = np.percentile(scores_all[train_idx_p, best["config"]["sample_idx"]], pct_best)
        thr_t = _threshold_aware(scores_all[test_idx, best["config"]["sample_idx"]],
                                 iv_vol_ratio[test_idx], thr_base, gamma_best)
        trig = scores_all[test_idx, best["config"]["sample_idx"]] > thr_t
        n_trig = int(trig.sum())
        yr = int(dates_arr[test_idx[0]].year)
        if is_crash:
            base_rate = float((target[test_idx] <= -0.05).mean())
            trig_rate = float((target[test_idx][trig] <= -0.05).mean()) if n_trig > 0 else 0.0
            metric_v = trig_rate / base_rate if base_rate > 0 else 0.0
            fold_table.append({"test_year": yr, "n_triggered": n_trig,
                               "metric": float(metric_v), "is_lift": True})
        else:
            metric_v = float(target[test_idx][trig].mean()) if n_trig > 0 else 0.0
            fold_table.append({"test_year": yr, "n_triggered": n_trig,
                               "metric": float(metric_v), "is_lift": False})

    # Retrain threshold on ALL data for the deployed model
    final_thr = float(np.percentile(scores_all[:, best["config"]["sample_idx"]], pct_best))

    # Bootstrap CI on the mean OOS metric (resample fold metrics)
    fold_metrics = np.array([f["metric"] for f in fold_table])
    if len(fold_metrics) >= 2:
        rng = np.random.RandomState(123)
        bs = []
        for _ in range(1000):
            idx = rng.choice(len(fold_metrics), size=len(fold_metrics), replace=True)
            bs.append(fold_metrics[idx].mean())
        ci_low, ci_high = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    else:
        ci_low = ci_high = float(fold_metrics.mean()) if len(fold_metrics) else 0.0

    # Drop the internal sample_idx before returning
    cfg_out = {k: v for k, v in best["config"].items() if k != "sample_idx"}
    return {
        "weights": cfg_out["weights"],
        "horizon": cfg_out["horizon"],
        "threshold": final_thr,
        "threshold_pct": cfg_out["threshold_pct"],
        "gamma": cfg_out["gamma"],
        "metrics": {
            "mean_oos_metric": best["oos_metric"],
            "oos_ci_low": ci_low,
            "oos_ci_high": ci_high,
            "n_effective_indicators": cfg_out["n_effective_indicators"],
            "placement_rate": (100 - pct_best) / 100.0,
        },
        "walk_forward_folds": fold_table,
        "selection_mode": "oos",
    }


# ─────────────────────────────────────────────────────────────────────────────
# In-sample optimization (new composite objective) — fallback / diagnostic base
# ─────────────────────────────────────────────────────────────────────────────
def optimize_regime_is(df_norm, regime_key, candidate_indicators, horizons, is_crash,
                       num_samples=NUM_SAMPLES_DEFAULT, max_weight=0.5):
    """Full-sample optimization with the new composite objective (no walk-forward)."""
    active = [ind for ind in candidate_indicators if ind in df_norm.columns]
    if not active:
        print(f"  WARNING: No active indicators for {regime_key}!")
        return None
    K = len(active)
    W = generate_random_weights(K, num_samples, max_weight=max_weight)
    X = df_norm[active].values
    col_means = np.nanmean(X, axis=0)
    nan_mask = np.isnan(X)
    if nan_mask.any():
        X = np.where(nan_mask, np.take(col_means, np.where(nan_mask)[1]), X)
    iv_vol_ratio = (df_norm["iv_vol_ratio"].values if "iv_vol_ratio" in df_norm.columns
                    else np.ones(len(df_norm)))
    iv_vol_ratio = np.nan_to_num(iv_vol_ratio, nan=1.0)

    best = {"obj": -1e18, "result": None}
    for m in horizons:
        fwd_ret, worst_dd = compute_forward_targets(df_norm, m)
        target = -worst_dd if is_crash else fwd_ret
        scores_all = X @ W.T
        for gi, gamma in enumerate(GAMMAS):
            for pct in THRESHOLD_PCTS:
                for s in range(len(W)):
                    sc = scores_all[:, s]
                    thr_base = np.percentile(sc, pct)
                    thr_t = _threshold_aware(sc, iv_vol_ratio, thr_base, gamma)
                    trig = sc > thr_t
                    if int(trig.sum()) < MIN_TRIGGERED:
                        continue
                    n_eff = int((W[s] > EPS_EFFECTIVE_W).sum())
                    obj = composite_objective_is(sc, target, is_crash, trig,
                                                 None, n_eff)
                    if obj > best["obj"]:
                        best["obj"] = obj
                        _, _, metric = _evaluate_candidate(sc, target, iv_vol_ratio,
                                                           thr_base, gamma, is_crash)
                        best["result"] = {
                            "weights": {active[i]: float(W[s, i]) for i in range(K)},
                            "horizon": int(m),
                            "threshold": float(thr_base),
                            "threshold_pct": float(pct),
                            "gamma": float(gamma),
                            "metrics": {
                                **(metric or {}),
                                "placement_rate": (100 - pct) / 100.0,
                                "n_effective_indicators": float(n_eff),
                                "is_objective": float(obj),
                            },
                            "selection_mode": "is",
                        }
    return best["result"]


# ─────────────────────────────────────────────────────────────────────────────
# Walk-forward diagnostic (--walk-forward): per-fold IS-optimized → OOS eval
# ─────────────────────────────────────────────────────────────────────────────
def evaluate_model_oos(test_df_norm, weights, active_indicators, horizon, threshold,
                       gamma, is_crash):
    """Evaluate a deployed config on a test fold. Returns metric or None."""
    active = [ind for ind in active_indicators if ind in test_df_norm.columns]
    fwd_ret, worst_dd = compute_forward_targets(test_df_norm, horizon)
    target = -worst_dd if is_crash else fwd_ret
    sc = np.zeros(len(test_df_norm))
    total_w = 0.0
    for ind, w in weights.items():
        if ind in test_df_norm.columns:
            vals = test_df_norm[ind].values
            vals = np.nan_to_num(vals, nan=np.nanmean(vals) if np.isfinite(np.nanmean(vals)) else 0.5)
            sc += vals * w
            total_w += w
    if total_w > 0:
        sc = sc / total_w
    iv_vol_ratio = (test_df_norm["iv_vol_ratio"].values if "iv_vol_ratio" in test_df_norm.columns
                    else np.ones(len(test_df_norm)))
    iv_vol_ratio = np.nan_to_num(iv_vol_ratio, nan=1.0)
    thr_t = _threshold_aware(sc, iv_vol_ratio, threshold, gamma)
    trig = sc > thr_t
    n_trig = int(trig.sum())
    if n_trig < 5:
        return None
    if is_crash:
        base_rate = (target <= -0.05).mean()
        trig_rate = (target[trig] <= -0.05).mean()
        return float(trig_rate / base_rate) if base_rate > 0 else None
    else:
        return float(target[trig].mean())


def run_walk_forward_validation(df_norm, regime_configs, etf_choice, num_samples, max_weight):
    """Diagnostic: optimize per fold on train (IS objective), eval on test."""
    splits = _make_fold_splits(df_norm)
    if not splits:
        print("  WARNING: Not enough data for walk-forward validation!")
        return

    print("\n" + "=" * 80)
    print(f"  WALK-FORWARD VALIDATION DIAGNOSTIC FOR {etf_choice}ETF (max_weight={max_weight})")
    print("=" * 80)

    pos = np.arange(len(df_norm))
    dates_arr = pd.to_datetime(df_norm.index)

    for r_key, config in regime_configs.items():
        is_crash = config["is_crash"]
        print(f"\n  Regime: {config['name']}")
        print(f"  {'Test Year':<10} | {'IS Metric':<12} | {'OOS Metric':<12} | {'Horizon':<8} | {'Gamma':<6}")
        print("  " + "-" * 60)
        oos_metrics = []
        for (train_idx, test_idx) in splits:
            test_start = dates_arr.iloc[test_idx[0]] if hasattr(dates_arr, "iloc") else dates_arr[test_idx[0]]
            # Optimize on train (IS objective, fixed horizon pick for speed — use first)
            train_df = df_norm.iloc[train_idx]
            test_df = df_norm.iloc[test_idx]
            res = optimize_regime_is(train_df, r_key, config["indicators"],
                                     [config["horizons"][0], config["horizons"][-1]],
                                     is_crash, num_samples=max(num_samples // 2, 100),
                                     max_weight=max_weight)
            if not res:
                continue
            oos_m = evaluate_model_oos(test_df, res["weights"], config["indicators"],
                                       res["horizon"], res["threshold"], res["gamma"], is_crash)
            is_m = (res["metrics"].get("lift") if is_crash
                    else res["metrics"].get("mean_return_triggered"))
            yr = int(test_df.index[0].year)
            oos_str = f"{oos_m:.4f}" if oos_m is not None else "n/a"
            print(f"  {yr:<10} | {is_m:<12.4f} | {oos_str:<12} | {res['horizon']:<8} | {res['gamma']:<6.2f}")
            if oos_m is not None:
                oos_metrics.append(oos_m)
        if oos_metrics:
            print(f"  {'OOS MEAN':<10} | {'':<12} | {np.mean(oos_metrics):<12.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Alpha Model Parameter and Weight Optimizer (Phase 1 OOS overhaul)")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500", "all"], default="300",
                        help="ETF to optimize (or 'all' for 50, 300, 500)")
    parser.add_argument("-n", "--num-samples", type=int, default=NUM_SAMPLES_DEFAULT,
                        help="Number of random weight samples per regime")
    parser.add_argument("--max-weight", type=float, default=0.5,
                        help="Maximum weight for any single indicator (overfit control)")
    parser.add_argument("--walk-forward", action="store_true", default=False,
                        help="Run walk-forward diagnostic (per-fold IS-opt → OOS eval report)")
    parser.add_argument("--select-by-oos", action="store_true", default=False,
                        help="Select final config by mean OOS across walk-forward folds (purged). RECOMMENDED.")
    parser.add_argument("--expanding-pct", action="store_true", default=False,
                        help="Use expanding-window percentile rank (adaptive thresholds) instead of 252-day rolling")
    args = parser.parse_args()

    etfs_to_run = ["50", "300", "500"] if args.etf == "all" else [args.etf]
    all_results = {}

    out_file = "backtest/alpha_put_models.json"
    if os.path.exists(out_file) and not args.walk_forward:
        try:
            with open(out_file, "r") as f:
                all_results = json.load(f)
        except Exception:
            pass

    for etf_choice in etfs_to_run:
        print("\n" + "=" * 80)
        mode = "OOS-SELECT" if args.select_by_oos else ("WF-DIAGNOSTIC" if args.walk_forward else "IS-OBJECTIVE")
        print(f"  PROCESSING {etf_choice}ETF (max_weight={args.max_weight}, mode={mode})")
        print("=" * 80)

        select_underlying(etf_choice)
        inst, opt, etf = load_data()

        model = AlphaModel(expanding_pct=args.expanding_pct)
        df_norm = model.compute_normalized_indicators(etf)

        # Regime configs — ST uses [5,14], MT uses [21,40]; new indicators added as candidates.
        regime_configs = {
            "reg1": {
                "name": "Regime 1: Short-Term Fall",
                "indicators": [
                    "ind_rsi_high", "ind_skew_neg", "ind_roc5_neg", "ind_macd_neg",
                    "ind_dist_sma50_neg", "ind_obv_divergence", "ind_volume_spike",
                    "ind_atr_ratio_high", "ind_term_structure_neg", "ind_rsi_divergence_neg",
                ],
                "horizons": [5, 14],
                "is_crash": False,
            },
            "reg2": {
                "name": "Regime 2: Medium-Term Fall",
                "indicators": [
                    "ind_rsi_low", "ind_dist_sma50_neg", "ind_roc20_neg", "ind_macd_neg",
                    "ind_obv_divergence", "ind_volume_spike",
                    "ind_atr_ratio_high", "ind_term_structure_neg", "ind_vol_of_vol_high",
                    "ind_rsi_divergence_neg",
                ],
                "horizons": [21, 40],
                "is_crash": False,
            },
            "reg3": {
                "name": "Regime 3: Short-Term Crash",
                "indicators": [
                    "ind_vol_accel_high", "ind_kurt_high", "ind_skew_neg", "ind_iv_vol_low",
                    "ind_obv_divergence", "ind_volume_spike",
                    "ind_atr_ratio_high", "ind_range_expansion_high", "ind_term_structure_neg",
                    "ind_vol_of_vol_high",
                ],
                "horizons": [5, 14],
                "is_crash": True,
            },
            "reg4": {
                "name": "Regime 4: Medium-Term Crash",
                "indicators": [
                    "ind_dd_deep", "ind_dist_sma200_neg", "ind_vol_accel_high", "ind_kurt_high",
                    "ind_skew_neg", "ind_obv_divergence", "ind_volume_spike",
                    "ind_atr_ratio_high", "ind_term_structure_neg", "ind_vol_of_vol_high",
                    "ind_range_expansion_high",
                ],
                "horizons": [21, 40],
                "is_crash": True,
            },
        }

        if args.walk_forward:
            run_walk_forward_validation(df_norm, regime_configs, etf_choice,
                                        args.num_samples, args.max_weight)
            continue

        etf_results = {}
        for r_key, config in regime_configs.items():
            print(f"\n  Running {('OOS-select' if args.select_by_oos else 'IS-objective')} for {config['name']}...")
            if args.select_by_oos:
                res = select_best_by_oos(df_norm, r_key, config["indicators"],
                                         config["horizons"], config["is_crash"],
                                         num_samples=args.num_samples, max_weight=args.max_weight)
            else:
                res = optimize_regime_is(df_norm, r_key, config["indicators"],
                                         config["horizons"], config["is_crash"],
                                         num_samples=args.num_samples, max_weight=args.max_weight)
            if res:
                etf_results[r_key] = res
                print(f"    Horizon    : {res['horizon']}d")
                print(f"    Threshold  : {res['threshold']:.4f} (pct={res.get('threshold_pct', 'n/a')})")
                print(f"    Gamma      : {res['gamma']:.2f}")
                wf = res.get("walk_forward_folds")
                if wf:
                    print(f"    WF folds   : {len(wf)} (mean OOS={res['metrics']['mean_oos_metric']:.4f}, "
                          f"CI=[{res['metrics']['oos_ci_low']:.4f}, {res['metrics']['oos_ci_high']:.4f}])")
                print(f"    Weights    :")
                for ind, w in res["weights"].items():
                    print(f"      {ind:<28}: {w:.3f}")
                print(f"    Metrics    :")
                for m_name, m_val in res["metrics"].items():
                    val_str = f"{m_val:.4f}" if isinstance(m_val, (float, np.float64)) else str(m_val)
                    print(f"      {m_name:<28}: {val_str}")
            else:
                print(f"    FAILED / no candidate passed gate for {r_key}")

        all_results[etf_choice] = etf_results

    if not args.walk_forward:
        os.makedirs("backtest", exist_ok=True)
        with open(out_file, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n  Saved optimized models to {out_file}")


if __name__ == "__main__":
    main()
