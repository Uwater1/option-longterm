"""
Phase 2: Train Optuna-tuned XGBoost regression predicting PM return per ETF.

Validation: Purged TimeSeriesSplit walk-forward (gap=N between train and test).
Optuna objective: mean Spearman rank IC across folds (robust to outliers).
Hyperparameters tuned per-ETF; final OOS metrics reported on the last holdout fold
plus walk-forward aggregation.

Also computes overfitting diagnostics:
  - IS vs OOS IC gap per fold
  - Year-by-year OOS IC
  - Permutation importance vs gain importance
  - Purge-gap sensitivity (gap=0 vs 5 vs 10)
  - Optuna hyperparameter importance

Outputs:
  - models/xgb_{ETF}.json                          (trained model, full data)
  - models/scaler_{ETF}.joblib                     (StandardScaler)
  - data/results_{ETF}.json                        (all metrics + diagnostics)
  - data/optuna_study_{ETF}.sqlite3                (Optuna history)
  - plots/{diagnostic}_{ETF}.png

Usage:
    python train_model.py -e all --gpu             # full run with GPU, n_trials=60
    python train_model.py -e all                   # full run, CPU, n_trials=60
    python train_model.py -e 300 --gpu --quick     # smoke test, GPU, n_trials=20
    python train_model.py -e 300 --trials 100      # custom trials
"""
import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge
from sklearn.inspection import permutation_importance
import xgboost as xgb
import optuna
import joblib

# GPU detection: try CUDA, fall back to CPU
_USE_GPU = False
def _detect_gpu(force: bool = False):
    global _USE_GPU
    try:
        X_test = np.random.randn(10, 2)
        y_test = np.random.randn(10)
        dmat = xgb.DMatrix(X_test, label=y_test)
        xgb.train({"device": "cuda", "tree_method": "hist"}, dmat, num_boost_round=1)
        _USE_GPU = True
        print("[GPU] CUDA device detected \u2014 using GPU acceleration")
    except Exception as e:
        _USE_GPU = False
        if force:
            raise RuntimeError(f"--gpu requested but CUDA not available: {e}")
        print("[GPU] No CUDA device \u2014 using CPU")

def _xgb_device_kwargs():
    """Return XGBoost kwargs for current device."""
    if _USE_GPU:
        return {"device": "cuda", "tree_method": "hist"}
    return {"n_jobs": -1}

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

ETF_CLI_MAP = {
    "300": "300ETF", "50": "50ETF", "500": "500ETF",
    "588000": "588000ETF", "159915": "159915ETF",
    "300ETF": "300ETF", "50ETF": "50ETF", "500ETF": "500ETF",
    "588000ETF": "588000ETF", "159915ETF": "159915ETF",
    "all": ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"],
}

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Feature columns (must match build_features.py output)
EARLY_FEATURES = [
    "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
    "early_volume_ratio", "early_trend", "early_momentum", "gap_direction",
    "first_bar_return", "first_bar_volume", "early_vwap_dev",
    "early_skew", "early_kurtosis",
]
DAY_FEATURES = [
    "rsi14", "macd_hist", "sma20_dist", "sma50_dist",
    "atr14_norm", "roc10", "bb_pctb", "vol20",
]
FEATURES = EARLY_FEATURES + DAY_FEATURES
TARGET = "pm_return"

# Defaults
DEFAULT_TRIALS = 60
DEFAULT_N_SPLITS = 5
DEFAULT_PURGE_GAP = 5
HOLDOUT_FRACTION = 0.20   # last 20% of data is the final OOS holdout


# ============================================================
# Purged TimeSeriesSplit
# ============================================================
def purged_tssplit(n: int, n_splits: int, gap: int):
    """Yield (train_idx, test_idx) for expanding-window walk-forward with a purge gap.

    Train is [0, t_end]; test is [t_end + gap, t_end + gap + test_size].
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    for train_idx, test_idx in tscv.split(np.arange(n)):
        # Train excludes the last `gap` rows that could leak into test
        if gap > 0:
            train_end = train_idx[-1] - gap
            if train_end < 1:
                continue
            train_idx = train_idx[train_idx <= train_end]
        if len(train_idx) < 50 or len(test_idx) < 30:
            continue
        yield train_idx, test_idx


# ============================================================
# Metrics
# ============================================================
def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 5 or np.std(y_pred) < 1e-12:
        return 0.0
    rho, _ = spearmanr(y_pred, y_true)
    return float(rho) if not np.isnan(rho) else 0.0


def direction_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(np.sign(y_true) == np.sign(y_pred)))


def long_short_sharpe(returns: np.ndarray, preds: np.ndarray, n_quant: int = 5) -> dict:
    """Stratify predictions into quintiles, compute long (top) - short (bottom) return."""
    if len(returns) < n_quant * 5:
        return {"ls_mean": 0.0, "ls_sharpe": 0.0, "top_mean": 0.0, "bot_mean": 0.0}
    q = pd.qcut(preds, n_quant, labels=False, duplicates="drop")
    valid = ~np.isnan(q)
    if valid.sum() < n_quant * 5:
        return {"ls_mean": 0.0, "ls_sharpe": 0.0, "top_mean": 0.0, "bot_mean": 0.0}
    q = q[valid]
    r = returns[valid]
    top = r[q == q.max()]
    bot = r[q == q.min()]
    # Long top quintile + short bottom quintile
    ls = np.concatenate([top, -bot])
    return {
        "ls_mean": float(ls.mean()),
        "ls_sharpe": float(ls.mean() / (ls.std() + 1e-10) * np.sqrt(252)),
        "top_mean": float(top.mean()),
        "bot_mean": float(bot.mean()),
    }


# ============================================================
# Optuna objective
# ============================================================
def make_objective(X, y, n_splits, gap):
    dev_kwargs = _xgb_device_kwargs()
    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "gamma": trial.suggest_float("gamma", 0.0, 2.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 1.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1.0, 10.0, log=True),
        }
        ics = []
        for train_idx, test_idx in purged_tssplit(len(y), n_splits, gap):
            scaler = StandardScaler().fit(X[train_idx])
            Xtr = scaler.transform(X[train_idx])
            Xte = scaler.transform(X[test_idx])
            model = xgb.XGBRegressor(
                **params, objective="reg:squarederror",
                random_state=42, verbosity=0, **dev_kwargs,
            )
            model.fit(Xtr, y[train_idx])
            preds = model.predict(Xte)
            ics.append(spearman_ic(y[test_idx], preds))
        return float(np.mean(ics)) if ics else -1.0
    return objective


# ============================================================
# Train + evaluate one ETF
# ============================================================
def train_etf(etf_name: str, n_trials: int, n_splits: int, gap: int) -> dict:
    dev_kwargs = _xgb_device_kwargs()
    t0 = time.time()
    feat_path = DATA_DIR / f"features_{etf_name}.parquet"
    if not feat_path.exists():
        print(f"  [SKIP] {etf_name}: missing {feat_path.name}. Run build_features.py first.")
        return {}

    feat = pd.read_parquet(feat_path).sort_index()
    feat = feat.dropna(subset=FEATURES + [TARGET]).copy()
    X = feat[FEATURES].values
    # Scale target by 100 (PM return → % form) so hyperparameters like gamma
    # behave naturally. IC and direction accuracy are scale-invariant.
    Y_SCALE = 100.0
    y_raw = feat[TARGET].values
    y = y_raw * Y_SCALE
    dates = feat.index
    n = len(feat)

    print(f"\n[{etf_name}] {n} samples, {len(FEATURES)} features, "
          f"target Sharpe={y_raw.mean()/y_raw.std()*np.sqrt(252):.2f} "
          f"(target scaled x{Y_SCALE:.0f} for training)")

    # ── 1) Holdout: last 20% is final OOS (never used in Optuna) ──
    holdout_n = int(n * HOLDOUT_FRACTION)
    train_dev_idx = np.arange(0, n - holdout_n)
    holdout_idx = np.arange(n - holdout_n, n)
    X_dev, y_dev, dates_dev = X[train_dev_idx], y[train_dev_idx], dates[train_dev_idx]
    X_ho, y_ho, dates_ho = X[holdout_idx], y[holdout_idx], dates[holdout_idx]
    print(f"  dev (Optuna): {len(X_dev)}, holdout (final OOS): {len(X_ho)}")

    # ── 2) Optuna hyperparameter search on dev set with purged TS-CV ──
    print(f"  Optuna: {n_trials} trials, {n_splits} folds, purge_gap={gap} ...")
    study_path = DATA_DIR / f"optuna_study_{etf_name}.sqlite3"
    if study_path.exists():
        study_path.unlink()
    storage = f"sqlite:///{study_path}"
    study = optuna.create_study(
        study_name=f"xgb_{etf_name}", direction="maximize",
        storage=storage, load_if_exists=False,
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=10),
    )
    obj = make_objective(X_dev, y_dev, n_splits, gap)
    study.optimize(obj, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_cv_ic = study.best_value
    print(f"  best CV IC: {best_cv_ic:.4f}  params: {best_params}")

    # ── 3) Final model: train on all dev data, evaluate on holdout ──
    scaler = StandardScaler().fit(X_dev)
    X_dev_s = scaler.transform(X_dev)
    X_ho_s = scaler.transform(X_ho)
    final_model = xgb.XGBRegressor(
        **best_params, objective="reg:squarederror",
        random_state=42, verbosity=0, **dev_kwargs,
    )
    final_model.fit(X_dev_s, y_dev)
    preds_ho = final_model.predict(X_ho_s)

    # IS fit (train) predictions for overfitting diagnostic
    preds_is = final_model.predict(X_dev_s)

    # ── 4) Metrics ──
    # NOTE: y was scaled x100 for training; undo for reporting RMSE in original units.
    preds_ho_raw = preds_ho / Y_SCALE
    preds_is_raw = preds_is / Y_SCALE
    y_ho_raw = y_ho / Y_SCALE
    y_dev_raw = y_dev / Y_SCALE

    holdout_ic = spearman_ic(y_ho_raw, preds_ho_raw)
    holdout_dir = direction_accuracy(y_ho_raw, preds_ho_raw)
    holdout_rmse = float(np.sqrt(np.mean((y_ho_raw - preds_ho_raw) ** 2)))
    holdout_ls = long_short_sharpe(y_ho_raw, preds_ho_raw)

    is_ic = spearman_ic(y_dev_raw, preds_is_raw)

    print(f"  HOLDOUT: IC={holdout_ic:.4f}  Dir={holdout_dir:.3f}  "
          f"RMSE={holdout_rmse*100:.4f}%  L/S Sharpe={holdout_ls['ls_sharpe']:.2f}")
    print(f"  OVERFITTING GAP: IS IC={is_ic:.4f} vs OOS IC={holdout_ic:.4f}  "
          f"(gap={is_ic - holdout_ic:+.4f})")

    # ── 5) Walk-forward OOS predictions across all folds (purged) ──
    wf_preds = np.full(n, np.nan)
    wf_is_ic_per_fold = []
    wf_oos_ic_per_fold = []
    for train_idx, test_idx in purged_tssplit(n, n_splits, gap):
        sc = StandardScaler().fit(X[train_idx])
        Xtr = sc.transform(X[train_idx])
        Xte = sc.transform(X[test_idx])
        m = xgb.XGBRegressor(
            **best_params, objective="reg:squarederror",
            random_state=42, verbosity=0, **dev_kwargs,
        )
        m.fit(Xtr, y[train_idx])
        wf_preds[test_idx] = m.predict(Xte) / Y_SCALE
        wf_is_ic_per_fold.append(spearman_ic(y[train_idx] / Y_SCALE, m.predict(Xtr) / Y_SCALE))
        wf_oos_ic_per_fold.append(spearman_ic(y[test_idx] / Y_SCALE, wf_preds[test_idx]))

    wf_valid = ~np.isnan(wf_preds)
    wf_overall_ic = spearman_ic(y_raw[wf_valid], wf_preds[wf_valid])

    # ── 6) Year-by-year OOS IC ──
    wf_df = pd.DataFrame({"date": dates, "y": y_raw, "pred": wf_preds})
    wf_df["year"] = wf_df["date"].dt.year
    yearly_ic = {}
    for yr, g in wf_df.dropna(subset=["pred"]).groupby("year"):
        if len(g) >= 20:
            yearly_ic[int(yr)] = {
                "ic": spearman_ic(g["y"].values, g["pred"].values),
                "dir": direction_accuracy(g["y"].values, g["pred"].values),
                "n": len(g),
                "ls_sharpe": long_short_sharpe(g["y"].values, g["pred"].values)["ls_sharpe"],
            }

    # ── 7) Baselines (on holdout, unscaled units) ──
    baselines = {}
    # B1: predict 0 (no-skill)
    baselines["zero"] = {
        "ic": 0.0, "dir": 0.5,
        "rmse": float(np.sqrt(np.mean(y_ho_raw ** 2))),
    }
    # B2: yesterday's PM return (autocorrelation baseline)
    full_y_raw = pd.Series(y_raw, index=dates)
    ylag = full_y_raw.shift(1).reindex(dates_ho).values
    valid_lag = ~np.isnan(ylag)
    baselines["yesterday_pm"] = {
        "ic": spearman_ic(y_ho_raw[valid_lag], ylag[valid_lag]) if valid_lag.sum() > 5 else 0.0,
        "dir": direction_accuracy(y_ho_raw[valid_lag], ylag[valid_lag]) if valid_lag.sum() > 5 else 0.5,
        "rmse": float(np.sqrt(np.mean((y_ho_raw[valid_lag] - ylag[valid_lag]) ** 2))) if valid_lag.sum() > 5 else 0.0,
    }
    # B3: first_30min_return as prediction (momentum baseline)
    col = FEATURES.index("first_30min_return")
    baselines["first_30min_mom"] = {
        "ic": spearman_ic(y_ho_raw, X_ho[:, col]),
        "dir": direction_accuracy(y_ho_raw, X_ho[:, col]),
        "rmse": float(np.sqrt(np.mean((y_ho_raw - X_ho[:, col]) ** 2))),
    }
    # B4: Ridge regression on same features (controls for XGBoost-specific overfitting)
    ridge = Ridge(alpha=1.0, random_state=42)
    ridge.fit(X_dev_s, y_dev)
    ridge_ho = ridge.predict(X_ho_s) / Y_SCALE
    baselines["ridge"] = {
        "ic": spearman_ic(y_ho_raw, ridge_ho),
        "dir": direction_accuracy(y_ho_raw, ridge_ho),
        "rmse": float(np.sqrt(np.mean((y_ho_raw - ridge_ho) ** 2))),
        "ls_sharpe": long_short_sharpe(y_ho_raw, ridge_ho)["ls_sharpe"],
    }

    print(f"  Baselines: zero={baselines['zero']['ic']:.3f}  "
          f"yesterday={baselines['yesterday_pm']['ic']:.3f}  "
          f"first_30m={baselines['first_30min_mom']['ic']:.3f}  "
          f"ridge={baselines['ridge']['ic']:.3f}")

    # ── 8) Feature importances ──
    gain_imp = dict(zip(FEATURES, final_model.feature_importances_.tolist()))
    # Permutation importance on holdout (XGBoost expects scaled y for loss)
    perm = permutation_importance(
        final_model, X_ho_s, y_ho, n_repeats=10, random_state=42,
        scoring="neg_mean_squared_error", n_jobs=-1,
    )
    perm_imp = dict(zip(FEATURES, perm.importances_mean.tolist()))

    # ── 9) Purge-gap sensitivity ──
    purge_sens = {}
    for g in [0, 5, 10]:
        ics_g = []
        for train_idx, test_idx in purged_tssplit(n, n_splits, g):
            sc = StandardScaler().fit(X[train_idx])
            Xtr = sc.transform(X[train_idx])
            Xte = sc.transform(X[test_idx])
            m = xgb.XGBRegressor(
                **best_params, objective="reg:squarederror",
                random_state=42, verbosity=0, **dev_kwargs,
            )
            m.fit(Xtr, y[train_idx])
            preds = m.predict(Xte) / Y_SCALE
            ics_g.append(spearman_ic(y_raw[test_idx], preds))
        purge_sens[g] = {"mean_ic": float(np.mean(ics_g)) if ics_g else 0.0,
                         "n_folds": len(ics_g)}

    # ── 10) Optuna hyperparameter importance ──
    try:
        optuna_param_imp = optuna.importance.get_param_importances(study)
        optuna_param_imp = {k: float(v) for k, v in optuna_param_imp.items()}
    except Exception:
        optuna_param_imp = {}

    # ── 11) Save model + scaler ──
    final_model.save_model(str(MODELS_DIR / f"xgb_{etf_name}.json"))
    joblib.dump({"scaler": scaler, "features": FEATURES,
                 "best_params": best_params, "holdout_ic": holdout_ic,
                 "train_end_date": str(dates_dev[-1].date()),
                 "holdout_start_date": str(dates_ho[0].date()),
                 "y_scale": Y_SCALE},
                MODELS_DIR / f"scaler_{etf_name}.joblib")

    # ── 12) Plots ──
    _plot_diagnostics(etf_name, dates_ho, y_ho_raw, preds_ho_raw,
                      wf_df, gain_imp, perm_imp, optuna_param_imp,
                      purge_sens, yearly_ic, study)

    elapsed = time.time() - t0
    print(f"  [{etf_name}] done in {elapsed:.0f}s ({elapsed/60:.1f}min)")

    return {
        "etf": etf_name,
        "n_samples": int(n),
        "n_features": len(FEATURES),
        "date_range": [str(dates[0].date()), str(dates[-1].date())],
        "holdout_n": int(len(X_ho)),
        "holdout_range": [str(dates_ho[0].date()), str(dates_ho[-1].date())],
        "best_cv_ic": float(best_cv_ic),
        "best_params": best_params,
        "is_ic": float(is_ic),
        "holdout_ic": float(holdout_ic),
        "holdout_dir_acc": float(holdout_dir),
        "holdout_rmse": holdout_rmse,
        "holdout_long_short": holdout_ls,
        "walk_forward_overall_ic": float(wf_overall_ic),
        "walk_forward_is_ic_per_fold": wf_is_ic_per_fold,
        "walk_forward_oos_ic_per_fold": wf_oos_ic_per_fold,
        "yearly_ic": yearly_ic,
        "baselines": baselines,
        "gain_importance": gain_imp,
        "permutation_importance": perm_imp,
        "purge_sensitivity": purge_sens,
        "optuna_param_importance": optuna_param_imp,
        "target_stats": {
            "mean_pct": float(y_raw.mean() * 100),
            "std_pct": float(y_raw.std() * 100),
            "sharpe_ann": float(y_raw.mean() / y_raw.std() * np.sqrt(252)),
        },
        "y_scale": Y_SCALE,
        "elapsed_sec": elapsed,
    }


# ============================================================
# Plots
# ============================================================
def _plot_diagnostics(etf, dates_ho, y_ho, preds_ho, wf_df,
                      gain_imp, perm_imp, optuna_imp, purge_sens,
                      yearly_ic, study):
    # 1) Predicted vs Actual scatter on holdout
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    ax.scatter(preds_ho * 100, y_ho * 100, alpha=0.3, s=10, c="steelblue")
    lim = max(abs(y_ho).max(), abs(preds_ho).max()) * 100 * 1.05
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.axhline(0, color="black", lw=0.5); ax.axvline(0, color="black", lw=0.5)
    ax.plot([-lim, lim], [-lim, lim], "r--", lw=0.8)
    ax.set_xlabel("Predicted PM return (%)"); ax.set_ylabel("Actual PM return (%)")
    ic = spearman_ic(y_ho, preds_ho)
    ax.set_title(f"{etf} Holdout: IC={ic:.3f}")
    ax.grid(alpha=0.3)

    # 2) Cumulative long-short on holdout (top quintile - bottom quintile)
    ax = axes[1]
    q = pd.qcut(preds_ho, 5, labels=False, duplicates="drop")
    valid = ~np.isnan(q)
    if valid.sum() > 50:
        idx_top = np.where((q == q[valid].max()) & valid)[0]
        idx_bot = np.where((q == q[valid].min()) & valid)[0]
        # Daily L/S PnL: long top, short bottom (position-size=1 unit each side)
        ls = np.zeros(len(y_ho))
        ls[idx_top] = y_ho[idx_top]
        ls[idx_bot] = -y_ho[idx_bot]
        cum = np.cumsum(ls)
        ax.plot(pd.to_datetime(dates_ho), cum * 100, color="purple", lw=1.2)
        ax.axhline(0, color="black", lw=0.5)
        ax.set_xlabel("Date"); ax.set_ylabel("Cumulative L/S return (%)")
        ax.set_title(f"{etf} TopQ - BotQ Cumulative")
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"holdout_scatter_{etf}.png", dpi=110)
    plt.close()

    # 3) Walk-forward rolling IC (90-day rolling)
    fig, ax = plt.subplots(figsize=(12, 4))
    wf_v = wf_df.dropna(subset=["pred"]).copy()
    if len(wf_v) > 90:
        # Manual rolling Spearman IC over a 90-day window
        y_arr = wf_v["y"].values
        p_arr = wf_v["pred"].values
        dates_arr = wf_v["date"].values
        win = 90
        rolling_ics = []
        rolling_dates = []
        for i in range(win, len(wf_v)):
            window_y = y_arr[i - win:i]
            window_p = p_arr[i - win:i]
            if len(window_y) >= 30 and np.std(window_p) > 1e-12:
                rolling_ics.append(spearman_ic(window_y, window_p))
                rolling_dates.append(dates_arr[i])
        if rolling_dates:
            ax.plot(rolling_dates, rolling_ics, color="steelblue", lw=1)
            ax.axhline(0, color="black", lw=0.5)
            ax.set_title(f"{etf}: {win}-day rolling OOS Spearman IC")
            ax.set_ylabel("Spearman IC"); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"ic_timeseries_{etf}.png", dpi=110)
    plt.close()

    # 4) Feature importance: gain vs permutation (side by side)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, imp, title in [
        (axes[0], gain_imp, "Gain Importance"),
        (axes[1], perm_imp, "Permutation Importance (OOS)"),
    ]:
        s = pd.Series(imp).sort_values()
        ax.barh(s.index, s.values, color="steelblue")
        ax.set_title(f"{etf}: {title}")
        ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"feature_importance_{etf}.png", dpi=110)
    plt.close()

    # 5) Year-by-year IC bar
    if yearly_ic:
        fig, ax = plt.subplots(figsize=(9, 4))
        yrs = sorted(yearly_ic.keys())
        ics = [yearly_ic[y]["ic"] for y in yrs]
        colors = ["green" if v > 0 else "red" for v in ics]
        ax.bar(yrs, ics, color=colors)
        ax.axhline(0, color="black", lw=0.5)
        ax.set_title(f"{etf}: OOS Spearman IC by Year (walk-forward)")
        ax.set_ylabel("Spearman IC"); ax.grid(alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"yearly_ic_{etf}.png", dpi=110)
        plt.close()

    # 6) Purge gap sensitivity
    fig, ax = plt.subplots(figsize=(6, 4))
    keys = sorted(purge_sens.keys())
    ax.plot(keys, [purge_sens[k]["mean_ic"] for k in keys], "o-", color="purple")
    ax.set_xticks(keys); ax.set_xlabel("Purge gap (trading days)")
    ax.set_ylabel("Mean OOS IC")
    ax.set_title(f"{etf}: Purge-gap sensitivity (leakage diagnostic)")
    ax.axhline(0, color="black", lw=0.5)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"purge_sensitivity_{etf}.png", dpi=110)
    plt.close()

    # 7) Optuna param importance (if any)
    if optuna_imp:
        fig, ax = plt.subplots(figsize=(8, 5))
        s = pd.Series(optuna_imp).sort_values()
        ax.barh(s.index, s.values, color="orange")
        ax.set_title(f"{etf}: Optuna hyperparameter importance")
        ax.grid(alpha=0.3, axis="x")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"optuna_param_importance_{etf}.png", dpi=110)
        plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="all")
    ap.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    ap.add_argument("--quick", action="store_true", help="smoke test (20 trials)")
    ap.add_argument("--splits", type=int, default=DEFAULT_N_SPLITS)
    ap.add_argument("--gap", type=int, default=DEFAULT_PURGE_GAP)
    ap.add_argument("--gpu", action="store_true", help="use CUDA GPU for XGBoost")
    args = ap.parse_args()

    _detect_gpu(force=args.gpu)  # auto-detect CUDA; --gpu forces error if missing

    if args.quick:
        args.trials = min(args.trials, 20)

    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]

    print(f"Training XGBoost day-models for: {etfs}")
    print(f"  trials={args.trials}  splits={args.splits}  purge_gap={args.gap}  "
          f"holdout_frac={HOLDOUT_FRACTION}")

    t_start = time.time()
    all_results = {}
    for etf in etfs:
        try:
            res = train_etf(etf, n_trials=args.trials, n_splits=args.splits, gap=args.gap)
            if res:
                all_results[etf] = res
                with open(DATA_DIR / f"results_{etf}.json", "w") as f:
                    json.dump(res, f, indent=2, default=str)
        except Exception as e:
            print(f"  [ERROR] {etf}: {e}")
            import traceback; traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print(f"{'ETF':<10} {'Holdout IC':>12} {'Holdout Dir':>12} {'L/S Sharpe':>12} "
          f"{'Ridge IC':>10} {'Gap IS-OOS':>12}")
    print("-" * 70)
    for etf, r in all_results.items():
        gap = r["is_ic"] - r["holdout_ic"]
        ridge_ic = r["baselines"]["ridge"]["ic"]
        print(f"{etf:<10} {r['holdout_ic']:>12.4f} {r['holdout_dir_acc']:>12.3f} "
              f"{r['holdout_long_short']['ls_sharpe']:>12.2f} {ridge_ic:>10.4f} "
              f"{gap:>+12.4f}")
    print("=" * 70)

    # Save combined results
    with open(DATA_DIR / "results_all.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    total_time = time.time() - t_start
    print(f"\nTotal wall time: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Combined results → {DATA_DIR / 'results_all.json'}")


if __name__ == "__main__":
    main()
