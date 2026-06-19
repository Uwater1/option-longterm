import sys
import os
import json
import time
import argparse
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge, Lasso, ElasticNet, HuberRegressor, LassoCV
from joblib import Parallel, delayed
import optuna
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Add path to import from build_features
HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))

from build_features import (
    compute_daylevel_indicators,
    get_cached_margin_data,
    get_cached_capital_flow,
    get_cached_stock_connect_quota,
    _linear_slope,
    extract_day_full_features,
    compute_pm_return,
    ETF_CONFIG,
    DATA_DIR,
    DAY_FEATURES,
    YESTERDAY_FEATURES
)

# Helper function to generate early features list dynamically
def get_features_for_bars(early_bars: int):
    early = [
        "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
        "early_volume_ratio", "early_trend", "early_momentum", "gap_direction",
        "first_bar_return", "first_bar_volume", "early_vwap_dev",
        "early_skew", "early_kurtosis"
    ]
    # Add bar-specific features
    for i in range(early_bars):
        early.append(f"bar_ret_{i}")
        early.append(f"bar_vol_{i}")
        early.append(f"bar_rng_{i}")
        early.append(f"bar_body_rng_{i}")
        early.append(f"bar_vwap_dev_{i}")
        
    early += ["num_up_bars", "max_up_ret", "max_down_ret", "cl_pos_in_range",
              "body_to_range_ratio", "total_path_length", "volume_slope"]
              
    return early

def get_full_features_list(early_bars: int):
    return get_features_for_bars(early_bars) + DAY_FEATURES + YESTERDAY_FEATURES

# Custom extract_day_early_features supporting variable bar counts & expected_bar_vol normalizer
def extract_day_early_features_param(day_5m: pd.DataFrame, prev_close: float, early_bars: int, expected_bar_vol: float) -> dict:
    bars = day_5m.head(early_bars)
    early_features_list = get_features_for_bars(early_bars)
    
    if len(bars) < early_bars or prev_close <= 0 or prev_close is None or np.isnan(prev_close):
        return {k: np.nan for k in early_features_list}

    day_open = float(bars.iloc[0]["open"])
    if day_open <= 0:
        return {k: np.nan for k in early_features_list}

    op = bars["open"].values
    hi = bars["high"].values
    lo = bars["low"].values
    cl = bars["close"].values
    vol = bars["volume"].values

    BARS_PER_DAY = 48
    bar_ret = np.log(cl / np.maximum(op, 1e-10))

    gap_pct = (day_open - prev_close) / prev_close
    first_30min_return = (cl[-1] - day_open) / day_open
    early_realized_vol = float(np.nanstd(bar_ret) * np.sqrt(BARS_PER_DAY))
    early_range = (hi.max() - lo.min()) / day_open
    
    # Normalize volume features by expected_bar_vol (historical average bar volume) to prevent look-ahead bias
    early_volume_ratio = vol.mean() / expected_bar_vol
    early_trend = _linear_slope(cl) / day_open
    early_momentum = (cl[-1] - cl[0]) / cl[0] if cl[0] > 0 else 0.0
    gap_direction = float(np.sign(gap_pct))
    first_bar_return = (cl[0] - op[0]) / op[0] if op[0] > 0 else 0.0
    first_bar_volume = vol[0] / expected_bar_vol
    
    vwap = (cl * vol).sum() / max(vol.sum(), 1.0)
    early_vwap_dev = (cl[-1] - vwap) / vwap if vwap > 0 else 0.0
    
    if len(bar_ret) >= 3 and np.std(bar_ret) > 1e-10:
        early_skew = float(skew(bar_ret))
        early_kurt = float(kurtosis(bar_ret, fisher=True))
    else:
        early_skew = 0.0
        early_kurt = 0.0

    res = {
        "gap_pct": gap_pct,
        "first_30min_return": first_30min_return,
        "early_realized_vol": early_realized_vol,
        "early_range": early_range,
        "early_volume_ratio": early_volume_ratio,
        "early_trend": early_trend,
        "early_momentum": early_momentum,
        "gap_direction": gap_direction,
        "first_bar_return": first_bar_return,
        "first_bar_volume": first_bar_volume,
        "early_vwap_dev": early_vwap_dev,
        "early_skew": early_skew,
        "early_kurtosis": early_kurt,
    }

    # Add bar-specific features
    for i in range(early_bars):
        res[f"bar_ret_{i}"] = float(np.log(cl[i] / max(op[i], 1e-10)))
        res[f"bar_vol_{i}"] = float(vol[i] / expected_bar_vol)
        res[f"bar_rng_{i}"] = float((hi[i] - lo[i]) / max(op[i], 1e-10))
        res[f"bar_body_rng_{i}"] = float((cl[i] - op[i]) / (hi[i] - lo[i] + 1e-8))
        
        cum_vol = max(vol[:i+1].sum(), 1.0)
        cum_vwap = (cl[:i+1] * vol[:i+1]).sum() / cum_vol
        res[f"bar_vwap_dev_{i}"] = float((cl[i] - cum_vwap) / max(cum_vwap, 1e-10))

    res["num_up_bars"] = float((cl > op).sum())
    res["max_up_ret"] = float((hi.max() - op[0]) / max(op[0], 1e-10))
    res["max_down_ret"] = float((lo.min() - op[0]) / max(op[0], 1e-10))
    res["cl_pos_in_range"] = float((cl[-1] - lo.min()) / (hi.max() - lo.min() + 1e-8))
    res["body_to_range_ratio"] = float(abs(cl[-1] - op[0]) / (hi.max() - lo.min() + 1e-8))
    res["total_path_length"] = float(np.sum(np.abs(bar_ret)))
    res["volume_slope"] = float(_linear_slope(vol) / expected_bar_vol)

    return res

def build_features_for_bars(etf_name: str, early_bars: int) -> pd.DataFrame:
    cfg = ETF_CONFIG[etf_name]
    path_5m = DATA_DIR / cfg["file_5m"]
    path_1d = DATA_DIR / cfg["file_1d"]

    if not path_5m.exists() or not path_1d.exists():
        print(f"  [SKIP] {etf_name}: missing parquet ({path_5m.name} / {path_1d.name})")
        return pd.DataFrame()

    df_5m = pd.read_parquet(path_5m)
    df_1d = pd.read_parquet(path_1d)

    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
    df_5m["date"] = df_5m["datetime"].dt.normalize()
    df_5m = df_5m.sort_values(["date", "datetime"]).reset_index(drop=True)

    # Load caches
    all_etf_ids = ["510300.XSHG", "510050.XSHG", "510500.XSHG", "588000.XSHG", "159915.XSHE"]
    margin_df = get_cached_margin_data(all_etf_ids, "2015-01-01", "2026-06-19")
    cap_df = get_cached_capital_flow(all_etf_ids, "2015-01-01", "2026-06-19")
    quota_df = get_cached_stock_connect_quota("2015-01-01", "2026-06-19")

    # Day-level indicators
    daylevel = compute_daylevel_indicators(df_1d, margin_df, cap_df, quota_df)

    # Compute expected daily volume of prior days (rolling 20-day mean shifted by 1)
    df_1d_sorted = df_1d.sort_values("date").reset_index(drop=True).copy()
    df_1d_sorted["rolling_volume_20d"] = df_1d_sorted["volume"].rolling(20).mean()
    df_1d_sorted["expected_daily_volume"] = df_1d_sorted["rolling_volume_20d"].shift(1)
    df_1d_sorted["date"] = pd.to_datetime(df_1d_sorted["date"])
    expected_vol_map = df_1d_sorted.set_index("date")["expected_daily_volume"].to_dict()
    
    # Calculate historical median of daily volume to use as fallback for early rows
    fallback_daily_vol = df_1d_sorted["volume"].median()
    if pd.isna(fallback_daily_vol) or fallback_daily_vol <= 0:
        fallback_daily_vol = 1000000.0  # safe default

    # Per-day early features + PM return
    df_1d_sorted["prev_close_adj"] = df_1d_sorted["close_adj"].shift(1)
    prev_close_map = df_1d_sorted.set_index("date")["prev_close_adj"].to_dict()

    BAR_LUNCH = 24
    WARMUP_DAYS = 60

    rows = []
    for date, day_df in df_5m.groupby("date", sort=True):
        date_ts = pd.Timestamp(date)
        prev_close = prev_close_map.get(date_ts, np.nan)
        
        # Calculate expected 5m bar volume using prior data to remove look-ahead bias
        expected_daily_vol = expected_vol_map.get(date_ts, np.nan)
        if pd.isna(expected_daily_vol) or expected_daily_vol <= 0:
            expected_daily_vol = fallback_daily_vol
        expected_bar_vol = expected_daily_vol / 48.0
        
        early = extract_day_early_features_param(day_df, prev_close, early_bars, expected_bar_vol)
        early["date"] = date_ts
        early["pm_return"] = compute_pm_return(day_df)
        
        # AM return for diagnostics
        am = day_df.reset_index(drop=True).iloc[:BAR_LUNCH]
        if len(am) >= 2:
            early["am_return"] = float(np.log(np.maximum(am["close"].iloc[-1], 1e-10) /
                                              np.maximum(am["open"].iloc[0], 1e-10)))
        else:
            early["am_return"] = np.nan
            
        full_feats = extract_day_full_features(day_df)
        for k, v in full_feats.items():
            early[k] = v
            
        rows.append(early)

    early_df = pd.DataFrame(rows).set_index("date").sort_index()

    # Shift yesterday features by 1 day
    cols_to_shift = [
        "pm_return", "am_return",
        "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
        "early_volume_ratio", "early_trend", "early_momentum", "first_bar_return",
        "first_bar_volume", "early_vwap_dev", "early_skew", "early_kurtosis",
        "day_range", "day_realized_vol", "day_close_pos", "day_pm_am_vol_ratio",
        "day_late_mom", "day_vwap_dev", "day_skew", "day_kurtosis"
    ]
    for col in cols_to_shift:
        early_df[f"yesterday_{col}"] = early_df[col].shift(1)

    # Join daylevel
    daylevel["date"] = pd.to_datetime(daylevel["date"])
    daylevel = daylevel.set_index("date").sort_index()

    feat = early_df.join(daylevel, how="inner")
    feat = feat.iloc[WARMUP_DAYS:].copy()

    # Drop NaN target
    feat = feat.dropna(subset=["pm_return"]).copy()
    
    return feat

# TimeSeriesSplit walk-forward with a purge gap
def purged_tssplit(n: int, n_splits: int, gap: int):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    for train_idx, test_idx in tscv.split(np.arange(n)):
        if gap > 0:
            train_end = train_idx[-1] - gap
            if train_end < 1:
                continue
            train_idx = train_idx[train_idx <= train_end]
        if len(train_idx) < 50 or len(test_idx) < 30:
            continue
        yield train_idx, test_idx

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
    ls = np.concatenate([top, -bot])
    return {
        "ls_mean": float(ls.mean()),
        "ls_sharpe": float(ls.mean() / (ls.std() + 1e-10) * np.sqrt(252)),
        "top_mean": float(top.mean()),
        "bot_mean": float(bot.mean()),
    }

# Stability selection
def _run_bootstrap_trial(X, y, block_size, random_seed):
    N, D = X.shape
    n_blocks = int(np.ceil(N / block_size))
    rng = np.random.default_rng(random_seed)
    start_indices = rng.integers(0, N - block_size + 1, size=n_blocks)
    boot_indices = []
    for start in start_indices:
        boot_indices.extend(range(start, start + block_size))
    boot_indices = boot_indices[:N]
    
    X_boot = X[boot_indices]
    y_boot = y[boot_indices]
    
    scaler = StandardScaler()
    X_boot_s = scaler.fit_transform(X_boot)
    
    lasso = LassoCV(cv=5, random_state=random_seed, max_iter=3000)
    lasso.fit(X_boot_s, y_boot)
    
    return np.abs(lasso.coef_) > 1e-5

def compute_stability_scores(X, y, features, block_size=20, n_bootstraps=30):
    results = Parallel(n_jobs=-1)(
        delayed(_run_bootstrap_trial)(X, y, block_size, 42 + i)
        for i in range(n_bootstraps)
    )
    selection_counts = np.sum(results, axis=0)
    scores = selection_counts / n_bootstraps
    return scores

# Optuna objective creator
def make_objective(X, y, n_splits, gap, stability_scores):
    def objective(trial: optuna.Trial) -> float:
        model_type = trial.suggest_categorical("model_type", ["ridge", "lasso", "elasticnet", "huber"])
        stability_threshold = trial.suggest_float("stability_threshold", 0.4, 0.9, step=0.05)

        selected_indices = np.where(stability_scores >= stability_threshold)[0]
        if len(selected_indices) < 3:
            selected_indices = np.argsort(stability_scores)[::-1][:3]

        if model_type == "ridge":
            alpha = trial.suggest_float("ridge_alpha", 1e-3, 1e4, log=True)
            model = Ridge(alpha=alpha, random_state=42)
        elif model_type == "lasso":
            alpha = trial.suggest_float("lasso_alpha", 1e-5, 1.0, log=True)
            model = Lasso(alpha=alpha, random_state=42, max_iter=5000)
        elif model_type == "elasticnet":
            alpha = trial.suggest_float("en_alpha", 1e-5, 1.0, log=True)
            l1_ratio = trial.suggest_float("en_l1_ratio", 0.0, 1.0)
            model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42, max_iter=5000)
        elif model_type == "huber":
            alpha = trial.suggest_float("huber_alpha", 1e-4, 1e4, log=True)
            epsilon = trial.suggest_float("huber_epsilon", 1.0, 2.0)
            model = HuberRegressor(alpha=alpha, epsilon=epsilon, max_iter=2000)

        ics = []
        for train_idx, test_idx in purged_tssplit(len(y), n_splits, gap):
            scaler = StandardScaler().fit(X[train_idx])
            Xtr_s = scaler.transform(X[train_idx])
            Xte_s = scaler.transform(X[test_idx])

            Xtr_sel = Xtr_s[:, selected_indices]
            Xte_sel = Xte_s[:, selected_indices]

            model.fit(Xtr_sel, y[train_idx])
            preds = model.predict(Xte_sel)
            ics.append(spearman_ic(y[test_idx], preds))

        return float(np.mean(ics)) if ics else -1.0
    return objective

def train_and_eval(feat: pd.DataFrame, early_bars: int, n_trials: int = 50, n_splits: int = 5, gap: int = 5) -> dict:
    features_list = get_full_features_list(early_bars)
    feat = feat.dropna(subset=features_list + ["pm_return"]).copy()
    X = feat[features_list].values
    y_raw = feat["pm_return"].values
    Y_SCALE = 100.0
    y = y_raw * Y_SCALE
    dates = feat.index
    n = len(feat)

    holdout_fraction = 0.20
    holdout_n = int(n * holdout_fraction)
    train_dev_idx = np.arange(0, n - holdout_n)
    holdout_idx = np.arange(n - holdout_n, n)
    X_dev, y_dev = X[train_dev_idx], y[train_dev_idx]
    X_ho, y_ho = X[holdout_idx], y[holdout_idx]

    # Stability Selection on dev set
    stability_scores = compute_stability_scores(X_dev, y_dev, features_list, n_bootstraps=30)

    # Optuna study (in-memory)
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    obj = make_objective(X_dev, y_dev, n_splits, gap, stability_scores)
    study.optimize(obj, n_trials=n_trials, show_progress_bar=False)

    best_params = study.best_params
    best_cv_ic = study.best_value

    # Final model on holdout
    scaler = StandardScaler().fit(X_dev)
    X_dev_s = scaler.transform(X_dev)
    X_ho_s = scaler.transform(X_ho)

    best_threshold = best_params["stability_threshold"]
    selected_indices = np.where(stability_scores >= best_threshold)[0]
    if len(selected_indices) < 3:
        selected_indices = np.argsort(stability_scores)[::-1][:3]
    selected_features = [features_list[i] for i in selected_indices]

    X_dev_sel = X_dev_s[:, selected_indices]
    X_ho_sel = X_ho_s[:, selected_indices]

    model_type = best_params["model_type"]
    if model_type == "ridge":
        final_model = Ridge(alpha=best_params["ridge_alpha"], random_state=42)
    elif model_type == "lasso":
        final_model = Lasso(alpha=best_params["lasso_alpha"], random_state=42, max_iter=5000)
    elif model_type == "elasticnet":
        final_model = ElasticNet(alpha=best_params["en_alpha"], l1_ratio=best_params["en_l1_ratio"], random_state=42, max_iter=5000)
    elif model_type == "huber":
        final_model = HuberRegressor(alpha=best_params["huber_alpha"], epsilon=best_params["huber_epsilon"], max_iter=2000)

    final_model.fit(X_dev_sel, y_dev)
    preds_ho = final_model.predict(X_ho_sel)

    # Metrics
    preds_ho_raw = preds_ho / Y_SCALE
    y_ho_raw = y_ho / Y_SCALE

    holdout_ic = spearman_ic(y_ho_raw, preds_ho_raw)
    holdout_dir = direction_accuracy(y_ho_raw, preds_ho_raw)
    holdout_rmse = float(np.sqrt(np.mean((y_ho_raw - preds_ho_raw) ** 2)))
    holdout_ls = long_short_sharpe(y_ho_raw, preds_ho_raw)

    return {
        "model_type": model_type,
        "n_selected": len(selected_features),
        "selected_features": selected_features,
        "best_cv_ic": best_cv_ic,
        "holdout_ic": holdout_ic,
        "holdout_dir": holdout_dir,
        "holdout_rmse": holdout_rmse,
        "holdout_ls_sharpe": holdout_ls["ls_sharpe"]
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etfs", default="300,50,500,588000,159915", help="Comma separated ETFs or 'all'")
    ap.add_argument("--trials", type=int, default=40, help="Number of Optuna trials")
    args = ap.parse_args()

    etf_list = []
    for item in args.etfs.split(","):
        item = item.strip()
        if not item:
            continue
        if "ETF" not in item:
            if item in ["300", "50", "500", "588000", "159915"]:
                if item == "300":
                    etf_list.append("300ETF")
                elif item == "50":
                    etf_list.append("50ETF")
                elif item == "500":
                    etf_list.append("500ETF")
                elif item == "588000":
                    etf_list.append("588000ETF")
                elif item == "159915":
                    etf_list.append("159915ETF")
            else:
                etf_list.append(item)
        else:
            etf_list.append(item)

    bar_configs = [3, 4, 5, 6]
    results = {}

    for etf in etf_list:
        print(f"\n==================================================")
        print(f"Starting experiment for {etf}...")
        print(f"==================================================")
        results[etf] = {}
        
        # We build the features once for each bar configuration, then train
        for bars in bar_configs:
            time_start = time.time()
            bar_time_str = {3: "9:45 (3 bar)", 4: "9:50 (4 bar)", 5: "9:55 (5 bar)", 6: "10:00 (6 bar)"}[bars]
            print(f"  -> Building features & training for {bar_time_str} ...")
            try:
                feat = build_features_for_bars(etf, bars)
                if feat.empty:
                    print(f"     [WARN] Empty feature dataset for {etf} @ {bars} bars.")
                    continue
                
                res = train_and_eval(feat, bars, n_trials=args.trials)
                elapsed = time.time() - time_start
                print(f"     Done in {elapsed:.1f}s | Holdout IC: {res['holdout_ic']:+.4f} | L/S Sharpe: {res['holdout_ls_sharpe']:+.2f} | Model: {res['model_type'].upper()} ({res['n_selected']} feats)")
                results[etf][bars] = res
            except Exception as e:
                print(f"     [ERROR] Failed for {etf} @ {bars} bars: {e}")
                import traceback
                traceback.print_exc()

    # Save results to JSON
    out_path = DATA_DIR / "experiment_bars_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved experiment results to {out_path}")

    # Generate Markdown Table Comparison
    print("\n\n=== EXPERIMENT COMPARISON SUMMARY ===")
    for etf in results:
        print(f"\n--- {etf} ---")
        print("| Bar Count | Prediction Time | Selected Model | Features | Holdout IC | Holdout Dir | L/S Sharpe |")
        print("|-----------|-----------------|----------------|----------|------------|-------------|------------|")
        for bars in bar_configs:
            if bars not in results[etf]:
                continue
            r = results[etf][bars]
            time_str = {3: "9:45 (3 bar)", 4: "9:50 (4 bar)", 5: "9:55 (5 bar)", 6: "10:00 (6 bar)"}[bars]
            print(f"| {bars} | {time_str} | {r['model_type'].upper()} | {r['n_selected']} | {r['holdout_ic']:+.4f} | {r['holdout_dir']:.3f} | {r['holdout_ls_sharpe']:+.2f} |")

if __name__ == "__main__":
    main()
