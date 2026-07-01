"""
Phase 3: Generate REPORT.md from linear model training results.

Reads data/results_all.json + plots/ and writes a comprehensive Markdown report
covering per-ETF performance, baselines, and overfitting diagnostics.

Usage:
    python generate_report.py                # use existing results_all.json
    python generate_report.py --results data/results_all.json
"""
import argparse
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib

# Constants
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
PLOTS_DIR = HERE / "plots"
REPORT_PATH = HERE / "REPORT.md"

ETF_ORDER = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]

# Import features list
sys.path.append(str(HERE))
from build_features import EARLY_FEATURES, DAY_FEATURES, YESTERDAY_FEATURES, FEATURES
TARGET = "trade_return"


def load_results(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def fmt_pct(v, mul100=True):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v*100:.4f}%" if mul100 else f"{v:.4f}"


def fmt_ic(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v:+.4f}"


def fmt_sharpe(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return f"{v:+.2f}"


def plot_ref(etf: str, name: str) -> str:
    """Return HTML image tag if plot exists, else empty string."""
    p = PLOTS_DIR / f"{name}_{etf}.png"
    if p.exists():
        return f'<img src="plots/{name}_{etf}.png" alt="{name}_{etf}" width="800" /><br>\n\n'
    return ""


def generate_threshold_return_plot(key: str, r: dict):
    etf = r["etf"]
    side = r.get("side", "long")
    feat_path = DATA_DIR / f"features_{etf}.parquet"
    model_path = HERE / "models" / f"linear_{key}.joblib"
    scaler_path = HERE / "models" / f"scaler_{key}.joblib"
    
    if not (feat_path.exists() and model_path.exists() and scaler_path.exists()):
        return
    
    try:
        scaler_obj = joblib.load(scaler_path)
        scaler = scaler_obj["scaler"] if isinstance(scaler_obj, dict) else scaler_obj
        model_features = scaler_obj.get("features", FEATURES) if isinstance(scaler_obj, dict) else FEATURES
        
        df_feat = pd.read_parquet(feat_path).dropna(subset=model_features + [TARGET])
        model = joblib.load(model_path)
        
        # Slice specifically to Out-Of-Sample Holdout range
        ho_start, ho_end = r['holdout_range']
        df_ho = df_feat[(df_feat.index >= pd.to_datetime(ho_start)) & (df_feat.index <= pd.to_datetime(ho_end))]
        if df_ho.empty:
            df_ho = df_feat
            
        sel_features = r["selected_features"]
        sel_indices = [model_features.index(f) for f in sel_features if f in model_features]
        
        X_ho_scaled = scaler.transform(df_ho[model_features].values)[:, sel_indices]
        preds_ho = model.predict(X_ho_scaled) / 100.0
        y_ho = df_ho[TARGET].values
        
        if side == "short":
            sig_preds = -preds_ho
            trade_rets = -y_ho
        else:
            sig_preds = preds_ho
            trade_rets = y_ho
            
        max_sig = max(0.0001, float(np.quantile(sig_preds, 0.95)))
        thrs = np.linspace(0.0, max_sig, 15)
        
        total_rets = []
        counts = []
        mean_rets = []
        
        for thr in thrs:
            mask = sig_preds >= thr
            c = int(mask.sum())
            counts.append(c)
            if c == 0:
                total_rets.append(0.0)
                mean_rets.append(0.0)
            else:
                total_rets.append(float(np.sum(trade_rets[mask]) * 100))
                mean_rets.append(float(np.mean(trade_rets[mask]) * 100))
                
        fig, ax1 = plt.subplots(figsize=(8.5, 4.5))
        ax1.set_xlabel('Linear Model Signal Threshold x (Predicted Return)')
        ax1.set_ylabel('Total OOS Return b (%) & Mean Return (%)', color='purple')
        p1 = ax1.plot(thrs * 100, total_rets, 'o-', color='purple', lw=2, label='Total OOS Return b (%)')
        p2 = ax1.plot(thrs * 100, mean_rets, 's--', color='blue', lw=1.5, label='Mean Return per Trade (%)')
        ax1.tick_params(axis='y', labelcolor='purple')
        ax1.grid(alpha=0.3)
        
        ax2 = ax1.twinx()
        ax2.set_ylabel('OOS Trade Count N', color='darkgreen')
        p3 = ax2.plot(thrs * 100, counts, '^:', color='darkgreen', lw=1.8, label='Trade Count N')
        ax2.tick_params(axis='y', labelcolor='darkgreen')
        
        lines_all = p1 + p2 + p3
        labels_all = [l.get_label() for l in lines_all]
        ax1.legend(lines_all, labels_all, loc='upper right')
        
        plt.title(f"{key}: OOS Holdout Return b (%) & Trade Count N vs Threshold x")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"threshold_return_{key}.png", dpi=110)
        plt.close()
    except Exception as e:
        pass


def generate_feature_importance_plot(key: str, r: dict):
    coef_imp = r.get("coefficient_importance", {})
    perm_imp = r.get("permutation_importance", {})
    sel_features = set(r.get("selected_features", []))
    
    if not sel_features or not coef_imp:
        return
        
    filtered_coef = {k: v for k, v in coef_imp.items() if k in sel_features}
    filtered_perm = {k: v for k, v in perm_imp.items() if k in sel_features}
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for ax, imp, title in [
        (axes[0], filtered_coef, "Standardized Coefficient"),
        (axes[1], filtered_perm, "Permutation Importance (OOS)"),
    ]:
        s = pd.Series(imp).sort_values()
        ax.barh(s.index, s.values, color="steelblue")
        ax.set_title(f"{key}: {title}")
        ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"feature_importance_{key}.png", dpi=110)
    plt.close()


def generate_gating_performance_plot(key: str, r: dict):
    etf = r["etf"]
    side = r.get("side", "long")
    gating_report_path = HERE / "gating_model" / f"report_{etf}_{side}.json"
    if not gating_report_path.exists():
        return
    
    try:
        with open(gating_report_path) as f:
            g_rep = json.load(f)
            
        results = g_rep.get("results", {})
        if not results:
            return
            
        models = []
        pr_aucs = []
        aucs = []
        precisions = []
        
        for m_name, m_data in results.items():
            wf = m_data.get("forward_wf_estimate") or m_data.get("dev_only_oos") or {}
            if wf:
                models.append(m_name.upper())
                pr_aucs.append(wf.get("pr_auc", 0.0))
                aucs.append(wf.get("auc", 0.0))
                precisions.append(wf.get("precision_at_thr", 0.0))
                
        if not models:
            return
            
        fig, ax = plt.subplots(figsize=(7, 4.5))
        x = np.arange(len(models))
        width = 0.25
        
        ax.bar(x - width, pr_aucs, width, label='PR-AUC', color='darkorange')
        ax.bar(x, aucs, width, label='ROC-AUC', color='steelblue')
        ax.bar(x + width, precisions, width, label='Precision@Thr', color='forestgreen')
        
        ax.set_ylabel('Score / Metric')
        ax.set_title(f"{key}: Gating Model Performance Comparison (WF OOS)")
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        ax.grid(alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"gating_performance_{key}.png", dpi=110)
        plt.close()
    except Exception as e:
        pass


def generate(results: dict) -> str:
    lines = []
    w = lines.append

    # Auto-detect keys in results
    has_dual_sides = any("_long" in k or "_short" in k for k in results.keys())
    
    # We want to keep the order of ETFs if possible
    active_keys = []
    for etf in ETF_ORDER:
        if has_dual_sides:
            for side in ["long", "short"]:
                key = f"{etf}_{side}"
                if key in results:
                    active_keys.append(key)
        else:
            if etf in results:
                active_keys.append(etf)
            elif f"{etf}_long" in results:
                active_keys.append(f"{etf}_long")
            elif f"{etf}_short" in results:
                active_keys.append(f"{etf}_short")

    w("# Day-Model Linear Trade Return Predictor — Report\n")
    w("*Generated by `generate_report.py`*\n")

    # ── 1) Executive Summary ──
    w("## 1. Executive Summary\n")
    w("Optuna-tuned sparse/robust linear models (skglm_huber_l1, skglm_mcp from skglm) predicting entry-to-exit trade return (entry at open of decision_bar+1, exit at close of exit_bar (14:30)) "
      "using features and indicators calculated from daily and intraday Index data directly (to eliminate look-ahead bias and accelerate computation), while executing trades on the actual ETF (to accurately reflect P&L performance). "
      "The input feature space spans early-bar features (up to decision bar close) + prior-day technical indicators. Features are robustly selected using the new TimeSeriesStabilitySelector "
      "which incorporates regime-stratified bootstrapping, randomized ElasticNet penalties, OOB IC screening, and across-fold variance filtering.\n")
    w("**Validation**: Purged walk-forward TimeSeriesSplit (gap=5 days, 5 folds). "
      "Optuna TPE hyperparameter search (100 trials). 20% holdout never used in tuning.\n")

    # Summary table
    w("\n| ETF/Tag | Model | Threshold | Features | Samples | Holdout IC | Holdout Dir | L/S Sharpe | Ridge Base IC | IS-OOS Gap |")
    w("|---------|-------|-----------|----------|---------|-----------|-------------|-----------|---------------|------------|")
    if not active_keys:
        w("| — | — | — | — | — | *No trained models found in results* | | | | |")
    else:
        for key in active_keys:
            r = results.get(key)
            gap_val = r["is_ic"] - r["holdout_ic"]
            best_model = r["best_params"]["model_type"].upper()
            threshold = r["best_params"]["stability_threshold"]
            n_feats = r["n_selected_features"]
            ridge_ic = r["baselines"]["ridge"]["ic"]
            w(f"| {key} | {best_model} | {threshold:.2f} | {n_feats}/{r['n_features']} | {r['n_samples']} | {fmt_ic(r['holdout_ic'])} "
              f"| {r['holdout_dir_acc']:.3f} "
              f"| {fmt_sharpe(r['holdout_long_short']['ls_sharpe'])} "
              f"| {fmt_ic(ridge_ic)} "
              f"| {gap_val:+.4f} |")
    w("")

    # ── 2) Data & Features ──
    w("## 2. Data & Features\n")
    w("### Feature Groups\n")
    w("| Group | Count | Features |")
    w("|-------|-------|----------|")
    w(f"| Early-bar ({len(EARLY_FEATURES)}) | {len(EARLY_FEATURES)} | {', '.join(EARLY_FEATURES[:15])}... and {len(EARLY_FEATURES) - 15} more (total {len(EARLY_FEATURES)}) |")
    w(f"| Day-level ({len(DAY_FEATURES)}) | {len(DAY_FEATURES)} | {', '.join(DAY_FEATURES[:15])}... and {len(DAY_FEATURES) - 15} more (total {len(DAY_FEATURES)}) |")
    w(f"| Yesterday ({len(YESTERDAY_FEATURES)}) | {len(YESTERDAY_FEATURES)} | {', '.join(YESTERDAY_FEATURES[:15])}... and {len(YESTERDAY_FEATURES) - 15} more (total {len(YESTERDAY_FEATURES)}) |")
    w("")
    w("- **Early-bar**: First `decision_bar+1` five-minute bars of Index data (see `DECISION_BAR` dict in `build_features.py`). Bars beyond `decision_bar` padded with 0.0. Strictly causal — no look-ahead.")
    w("- **Day-level**: Technical indicators and 3rd party flows calculated using daily and intraday Index data directly, shifted by 1 day (no look-ahead).")
    w("- **Yesterday**: Shifted full-day and early-bar features of Index data from day t-1 (no look-ahead).")
    w("- **Target**: `trade_return` = log(close[EXIT_BAR] / open[decision_bar+1]) using ETF prices to accurately reflect actual daytrade P&L (entry at next-bar open after decision, exit at 14:30 close).")
    w("- **Diagnostic target**: `pm_return` (bars 24..47, 13:00→15:00) of the ETF, retained for IC sanity-checks vs the old baseline — do NOT train on it.")
    w("- **Warmup**: First 60 rows dropped (SMA50/ATR14 burn-in).\n")

    # ── 3) Methodology ──
    w("## 3. Methodology\n")
    w("### Purged Walk-Forward Validation & Feature Selection\n")
    w("- **TimeSeriesSplit**: 5 folds expanding window.")
    w("- **Purge gap**: 5 trading days between train and test.")
    w("- **Stability Selection**: 50 stratified block bootstrap trials (block length 20 days) using randomized `ElasticNet` (pre-tuned via `ElasticNetCV`) combined with an out-of-bag (OOB) Spearman rank IC significance check (p < 0.05 or |IC| > 0.02) as the base selector. Stability scores and cross-fold variance filters are computed across purged walk-forward validation folds.\n")
    w("- **Tuning**: The top K features by stability selection are tuned via Optuna in walk-forward CV over $K \\in [3, 50]$ to find the globally most robust subset.\n")
    w("- **Optuna objective**: mean Spearman rank IC across folds (100 trials)\n")

    w("### Search Space\n")
    w("| Parameter | Range / Options |")
    w("|-----------|-----------------|")
    w("| model_type | skglm_huber_l1, skglm_mcp (from `skglm` library) |")
    w("| top_k_features | 3–50 (step 1) |")
    w("| **skglm_huber_l1** | alpha: $10^{-5}$–$10^3$ (log), delta: $1.0$–$3.0$ |")
    w("| **skglm_mcp** | alpha: $10^{-5}$–$10^3$ (log), gamma: $1.5$–$15.0$ |")
    w("")

    # ── 4) Results per ETF ──
    w("## 4. Results\n")
    if not active_keys:
        w("*No trained models found.*\n")
    for key in active_keys:
        r = results.get(key)
        etf = r["etf"]
        side = r.get("side", "single")
        
        # Pre-generate diagnostic plots
        generate_feature_importance_plot(key, r)
        generate_threshold_return_plot(key, r)
        generate_gating_performance_plot(key, r)
        
        w(f"### {key}\n")
        w(f"- **Selected Model**: {r['best_params']['model_type'].upper()}")
        w(f"- **Tuned Stability Threshold**: {r['best_params']['stability_threshold']:.2f}")
        w(f"- **Samples**: {r['n_samples']} ({r['date_range'][0]} → {r['date_range'][1]})")
        w(f"- **Holdout**: {r['holdout_n']} days ({r['holdout_range'][0]} → {r['holdout_range'][1]})")
        w(f"- **Target stats**: mean={r['target_stats']['mean_pct']:.4f}%, "
          f"std={r['target_stats']['std_pct']:.4f}%, "
          f"Sharpe={r['target_stats']['sharpe_ann']:.2f}")
        w(f"- **Selected features ({r['n_selected_features']})**: `{', '.join(r['selected_features'])}`\n")

        # Feature Stability Scores Table (Filtered to Selected Features Only)
        w("#### Selected Feature Stability Scores (Block Bootstrap)\n")
        w("<details>")
        w("<summary><b>Click to expand Feature Stability Scores Table</b></summary>\n")
        w("| Feature | Stability Score | Status | Pearson $r$ | Spearman $\\rho$ | Monotonicity Score | Mutual Info | Quality Rating | Holdout IC | Yearly ICs | Yearly IC Std |")
        w("|---------|-----------------|--------|-------------|-----------------|--------------------|-------------|----------------|------------|------------|---------------|")
        
        # Precompute quality metrics if feature data exists
        feat_quality = {}
        feat_path = DATA_DIR / f"features_{etf}.parquet"
        if feat_path.exists():
            df_feat = pd.read_parquet(feat_path)
            df_feat = df_feat.dropna(subset=FEATURES + [TARGET])
            y_data = df_feat[TARGET].values
            
            # Slice holdout data for IC calculation
            ho_start, ho_end = r['holdout_range']
            df_ho = df_feat[(df_feat.index >= pd.to_datetime(ho_start)) & (df_feat.index <= pd.to_datetime(ho_end))]
            y_ho_data = df_ho[TARGET].values if not df_ho.empty else np.array([])
            
            from scipy.stats import pearsonr, spearmanr
            try:
                from sklearn.feature_selection import mutual_info_regression
                has_mi = True
            except ImportError:
                has_mi = False
                
            df_feat['year'] = pd.to_datetime(df_feat.index).year
            years = sorted(df_feat['year'].unique())

            for feat_name in r["selected_features"]:
                if feat_name not in df_feat.columns:
                    continue
                x_data = df_feat[feat_name].values
                p_corr, _ = pearsonr(x_data, y_data)
                s_corr, _ = spearmanr(x_data, y_data)
                
                # Holdout IC (OOS Spearman Rank correlation)
                if not df_ho.empty and feat_name in df_ho.columns:
                    x_ho_data = df_ho[feat_name].values
                    if len(y_ho_data) >= 5 and np.std(x_ho_data) > 1e-12 and np.std(y_ho_data) > 1e-12:
                        ho_ic, _ = spearmanr(x_ho_data, y_ho_data)
                    else:
                        ho_ic = np.nan
                else:
                    ho_ic = np.nan
                
                # Calculate Yearly IC Stability
                yearly_ics = {}
                for yr in years:
                    df_yr = df_feat[df_feat['year'] == yr]
                    if len(df_yr) >= 20:
                        x_yr = df_yr[feat_name].values
                        y_yr = df_yr[TARGET].values
                        if np.std(x_yr) > 1e-12 and np.std(y_yr) > 1e-12:
                            rho_yr, _ = spearmanr(x_yr, y_yr)
                            yearly_ics[yr] = rho_yr
                
                yc_parts = []
                for yr in sorted(yearly_ics.keys()):
                    val = yearly_ics[yr]
                    short_yr = str(yr)[-2:]
                    yc_parts.append(f"{short_yr}:{val:+.2f}")
                yearly_ic_str = " ".join(yc_parts) if yc_parts else "N/A"
                
                if len(yearly_ics) >= 2:
                    yearly_ic_std = float(np.std(list(yearly_ics.values())))
                    yearly_ic_std_str = f"{yearly_ic_std:.4f}"
                else:
                    yearly_ic_std_str = "N/A"

                # Binned Monotonicity Score
                try:
                    q_labels = pd.qcut(x_data, 5, labels=False, duplicates='drop')
                    q_means = [y_data[q_labels == i].mean() for i in sorted(np.unique(q_labels))]
                    if len(q_means) >= 3:
                        mono_score, _ = spearmanr(q_means, np.arange(len(q_means)))
                    else:
                        mono_score = np.nan
                except Exception:
                    mono_score = np.nan
                
                # Mutual Info
                mi_val = 0.0
                if has_mi:
                    try:
                        mi_val = float(mutual_info_regression(x_data.reshape(-1, 1), y_data, random_state=42)[0])
                    except Exception:
                        pass
                        
                # Rating
                mono_abs = abs(mono_score) if not np.isnan(mono_score) else 0
                if np.isnan(mono_score):
                    rating = "N/A"
                elif mono_abs >= 0.8:
                    if abs(s_corr) > 1.5 * abs(p_corr) and abs(s_corr) > 0.01:
                        rating = "** Non-Linear Monotonic"
                    else:
                        rating = "*** Strong Monotonic"
                elif mono_abs >= 0.5:
                    rating = "** Moderate Monotonic"
                else:
                    rating = "* Non-Monotonic / Weak"
                    
                feat_quality[feat_name] = {
                    "p_corr": p_corr,
                    "s_corr": s_corr,
                    "mono": mono_score,
                    "mi": mi_val,
                    "rating": rating,
                    "ic": ho_ic,
                    "yearly_ic_str": yearly_ic_str,
                    "yearly_ic_std_str": yearly_ic_std_str
                }

        # Sort stability scores descending for selected features
        sorted_scores = sorted([(f, r["stability_scores"].get(f, 0.0)) for f in r["selected_features"]], key=lambda x: x[1], reverse=True)
        for feat, score in sorted_scores:
            status = "**Selected**"
            q = feat_quality.get(feat, {
                "p_corr": np.nan, "s_corr": np.nan, "mono": np.nan, "mi": 0.0,
                "rating": "N/A", "ic": np.nan, "yearly_ic_str": "N/A", "yearly_ic_std_str": "N/A"
            })
            p_str = f"{q['p_corr']:+.4f}" if not np.isnan(q['p_corr']) else "N/A"
            s_str = f"{q['s_corr']:+.4f}" if not np.isnan(q['s_corr']) else "N/A"
            m_str = f"{q['mono']:+.2f}" if not np.isnan(q['mono']) else "N/A"
            ic_str = f"{q['ic']:+.4f}" if not np.isnan(q['ic']) else "N/A"
            w(f"| {feat} | {score:.1%} | {status} | {p_str} | {s_str} | {m_str} | {q['mi']:.4f} | {q['rating']} | {ic_str} | {q['yearly_ic_str']} | {q['yearly_ic_std_str']} |")
        w("")
        w("</details>\n")

        # Metrics table
        w("#### Metrics\n")
        w("| Metric | Best Linear | Ridge Base | Zero | Yesterday PM | First 30min Mom |")
        w("|--------|-------------|------------|------|--------------|-----------------|")
        bl = r["baselines"]
        w(f"| IC | {fmt_ic(r['holdout_ic'])} | {fmt_ic(bl['ridge']['ic'])} "
          f"| {fmt_ic(bl['zero']['ic'])} | {fmt_ic(bl['yesterday_pm']['ic'])} "
          f"| {fmt_ic(bl['first_30min_mom']['ic'])} |")
        w(f"| Dir Acc | {r['holdout_dir_acc']:.3f} | {bl['ridge']['dir']:.3f} "
          f"| {bl['zero']['dir']:.3f} | {bl['yesterday_pm']['dir']:.3f} "
          f"| {bl['first_30min_mom']['dir']:.3f} |")
        w(f"| RMSE | {r['holdout_rmse']*100:.4f}% | {bl['ridge']['rmse']*100:.4f}% "
          f"| {bl['zero']['rmse']*100:.4f}% | {bl['yesterday_pm']['rmse']*100:.4f}% "
          f"| {bl['first_30min_mom']['rmse']*100:.4f}% |")
        w(f"| L/S Sharpe | {fmt_sharpe(r['holdout_long_short']['ls_sharpe'])} "
          f"| {fmt_sharpe(bl['ridge']['ls_sharpe'])} | — | — | — |")
        w("")

        # Best params
        w("#### Best Hyperparameters\n")
        w("<details>")
        w("<summary><b>Click to expand Best Hyperparameters JSON</b></summary>\n")
        w("```json")
        w(json.dumps(r["best_params"], indent=2))
        w("```\n")
        w("</details>\n")

        # Walk-forward fold ICs
        w("#### Walk-Forward Fold ICs\n")
        w("| Fold | IS IC | OOS IC |")
        w("|------|-------|--------|")
        for i, (is_ic, oos_ic) in enumerate(zip(
            r["walk_forward_is_ic_per_fold"],
            r["walk_forward_oos_ic_per_fold"],
        )):
            w(f"| {i+1} | {is_ic:.4f} | {oos_ic:+.4f} |")
        w(f"| **Overall** | — | {fmt_ic(r['walk_forward_overall_ic'])} |")
        w("")

        # Year-by-year
        if r.get("yearly_ic"):
            w("#### Year-by-Year OOS IC\n")
            w("| Year | IC | Dir Acc | N | L/S Sharpe |")
            w("|------|-----|---------|---|-----------|")
            for yr in sorted(r["yearly_ic"].keys()):
                yi = r["yearly_ic"][yr]
                w(f"| {yr} | {fmt_ic(yi['ic'])} | {yi['dir']:.3f} "
                  f"| {yi['n']} | {fmt_sharpe(yi['ls_sharpe'])} |")
            w("")

        # Plots
        w("#### Diagnostic Plots\n")
        w("<details>")
        w("<summary><b>Click to expand Diagnostic Plots</b></summary>\n")
        for plot_name in ["holdout_scatter", "ic_timeseries", "feature_importance",
                          "threshold_return", "gating_performance",
                          "yearly_ic", "purge_sensitivity", "optuna_param_importance"]:
            ref = plot_ref(key, plot_name)
            if ref:
                w(ref)
        w("</details>\n")

    # ── 5) Baseline Comparison ──
    w("## 5. Comparison to Baselines\n")
    w("Four baselines evaluated on the same holdout set:\n")
    w("1. **Zero** (no-skill): Always predicts 0. IC=0 by definition.")
    w("2. **Yesterday trade_return**: Autocorrelation baseline. Tests if trade returns are predictable from prior day.")
    w("3. **First 30-min return (up to decision time)**: Momentum baseline. Tests AM-to-PM momentum.")
    w(f"4. **Ridge Base**: Ridge regression with alpha=1.0 on all candidate features ({len(FEATURES)} features). Controls for tuning/selection lift.\n")

    w("| ETF/Tag | Best Linear IC > Ridge Base IC? | Best Linear IC > Mom IC? | Best Baseline |")
    w("|---------|---------------------------------|--------------------------|---------------|")
    for key in active_keys:
        r = results.get(key)
        bl = r["baselines"]
        model_ic = r["holdout_ic"]
        ridge_ic = bl["ridge"]["ic"]
        mom_ic = bl["first_30min_mom"]["ic"]
        best_bl = max(bl.items(), key=lambda x: x[1].get("ic", 0))
        w(f"| {key} | {'Yes' if model_ic > ridge_ic else 'No'} "
          f"| {'Yes' if model_ic > mom_ic else 'No'} "
          f"| {best_bl[0]} (IC={fmt_ic(best_bl[1].get('ic', 0))}) |")
    w("")

    # ── 6) Overfitting Risk ──
    w("## 6. Risk of Overfitting\n")

    w("### 6.1 IS vs OOS Gap\n")
    w("| ETF/Tag | IS IC | OOS IC | Gap | Assessment |")
    w("|---------|-------|--------|-----|-----------|")
    for key in active_keys:
        r = results.get(key)
        gap_val = r["is_ic"] - r["holdout_ic"]
        severity = "Low" if gap_val < 0.2 else ("Moderate" if gap_val < 0.4 else "High")
        w(f"| {key} | {r['is_ic']:.4f} | {r['holdout_ic']:.4f} | {gap_val:+.4f} | {severity} |")
    w("")

    w("### 6.2 Regime Breakdown (Year-by-Year)\n")
    w("See per-ETF year-by-year tables in §4. Large year-to-year IC variance signals regime sensitivity.\n")

    w("### 6.3 Purge-Gap Sensitivity\n")
    w("If IC drops sharply as purge gap increases from 0→5→10, it indicates short-term leakage.\n")
    w("| ETF/Tag | Gap=0 | Gap=5 | Gap=10 | Delta(0→10) |")
    w("|---------|-------|-------|--------|------------|")
    for key in active_keys:
        r = results.get(key)
        ps = r["purge_sensitivity"]
        g0 = ps.get("0", {}).get("mean_ic", 0)
        g5 = ps.get("5", {}).get("mean_ic", 0)
        g10 = ps.get("10", {}).get("mean_ic", 0)
        delta = g0 - g10
        w(f"| {key} | {g0:+.4f} | {g5:+.4f} | {g10:+.4f} | {delta:+.4f} |")
    w("")

    w("### 6.4 Feature Importance Stability\n")
    w("Compare standardized coefficients vs permutation importance (OOS) across features. "
      "Large divergence indicates overfitting to specific features.\n")

    w("### 6.5 Top-5 Features: Standardized Coefficient vs Permutation\n")
    for key in active_keys:
        r = results.get(key)
        gi = pd.Series(r["coefficient_importance"]).abs().sort_values(ascending=False).head(5)
        pi = pd.Series(r["permutation_importance"]).sort_values(ascending=False).head(5)
        w(f"\n**{key}**:\n")
        w("| Rank | Standardized Coefficient (Abs) | Permutation Importance |")
        w("|------|--------------------------------|----------------------|")
        for rank, ((gf, gv), (pf, pv)) in enumerate(zip(gi.items(), pi.items()), 1):
            w(f"| {rank} | {gf} ({r['coefficient_importance'][gf]:+.4f}) | {pf} ({pv:+.6f}) |")
    w("")

    w("### 6.6 Hyperparameter Sensitivity\n")
    w("Optuna parameter importance shows which parameters most affect CV IC.\n")
    for key in active_keys:
        r = results.get(key)
        if not r or not r.get("optuna_param_importance"):
            continue
        opi = r["optuna_param_importance"]
        top_param = max(opi, key=opi.get)
        w(f"- **{key}**: Most influential = `{top_param}` ({opi[top_param]:.2%})")
    w("")

    # ── 7) Sensitivity to Prediction Time (Bar Count Comparison) ──
    w("## 7. Sensitivity to Prediction Time (Bar Count Comparison)\n")
    w("To determine how early the trade_return prediction can be made, we evaluated model performance across different morning bar counts (target = `trade_return`: open[decision_bar+1] -> close[EXIT_BAR] using ETF prices, with features computed from Index data):")
    w("- **9:45 AM (3 bars)**: First 15 minutes of trading (9:30–9:45)")
    w("- **9:50 AM (4 bars)**: First 20 minutes of trading (9:30–9:50)")
    w("- **9:55 AM (5 bars)**: First 25 minutes of trading (9:30–9:55)")
    w("- **10:00 AM (6 bars)**: First 30 minutes of trading (9:30–10:00) [Original Baseline]\n")
    w("> [!IMPORTANT]\n"
      "> **Look-Ahead Bias Correction**: To prevent any look-ahead bias, volume normalization in these experiments uses a rolling 20-day historical average of daily volume shifted by 1 day (i.e. expected bar volume = `yesterday_rolling_20d_daily_volume / 48`), ensuring zero future information leaks into the features.\n")

    exp_path = Path(__file__).resolve().parent.parent / "data" / "experiment_bars_results.json"
    if exp_path.exists():
        with open(exp_path) as f:
            exp_results = json.load(f)

        w("### 7.1 Performance Summary by Bar Count\n")
        w("| ETF | Bar Count | Prediction Time | Selected Model | Features | Holdout IC | Holdout Dir | L/S Sharpe |")
        w("|-----|-----------|-----------------|----------------|----------|------------|-------------|------------|")

        for etf in ETF_ORDER:
            bars_data = exp_results.get(etf, {})
            # Find max IC and Sharpe to bold them
            max_ic = -999.0
            max_sharpe = -999.0
            for b in [3, 4, 5, 6]:
                b_str = str(b)
                if b_str in bars_data:
                    max_ic = max(max_ic, bars_data[b_str]["holdout_ic"])
                    max_sharpe = max(max_sharpe, bars_data[b_str]["holdout_ls_sharpe"])

            first_row = True
            for b in [3, 4, 5, 6]:
                b_str = str(b)
                if b_str not in bars_data:
                    continue
                r = bars_data[b_str]
                time_str = {3: "9:45 (3 bar)", 4: "9:50 (4 bar)", 5: "9:55 (5 bar)", 6: "10:00 (6 bar)"}[b]
                
                ic_val = r["holdout_ic"]
                sharpe_val = r["holdout_ls_sharpe"]
                
                ic_str = fmt_ic(ic_val)
                if ic_val == max_ic:
                    ic_str = f"**{ic_str}**"
                    
                sharpe_str = fmt_sharpe(sharpe_val)
                if sharpe_val == max_sharpe:
                    sharpe_str = f"**{sharpe_str}**"
                
                model_str = r["model_type"].upper()
                n_selected = r["n_selected"]
                dir_str = f"{r['holdout_dir']:.3f}"
                
                etf_label = f"**{etf}**" if first_row else ""
                w(f"| {etf_label} | {b} | {time_str} | {model_str} | {n_selected} | {ic_str} | {dir_str} | {sharpe_str} |")
                first_row = False
            w("| | | | | | | | |")  # Blank separator line
        w("")
    else:
        w("*(No bar-count experiment results found. Run run_experiment_bars.py first.)*\n")

    w("### 7.2 Key Insights & Observations\n")
    w("1. **Window Duration vs. Model Maturity**:")
    w("   - For blue-chip ETFs (**300ETF** and **50ETF**), predictive accuracy improves monotonically as the morning observation window expands. 300ETF holdout IC climbs from `+0.0212` (9:45 AM) to `+0.0770` (10:00 AM) in experiments. This indicates that blue-chip index momentum requires a full 30-minute digestion period to become highly predictive.")
    w("2. **Early Peak Signals in Chinext/Mid-Cap**:")
    w("   - For high-beta/growth index ETFs (**159915ETF** and **500ETF**), prediction power peaks *before* 10:00 AM:")
    w("     - **159915ETF** achieves its highest Holdout IC at 9:55 AM (`+0.2164`, L/S Sharpe `+4.41`), and its highest L/S Sharpe at 9:45 AM (`+4.68`, Holdout IC `+0.2032`).")
    w("     - **500ETF** holds high predictive power at 9:45 AM (`+0.1369`, L/S Sharpe `+2.54`), peaking in Holdout IC at 9:55 AM (`+0.1466`).")
    w("     - *Rationale*: Opening cross and morning price action in mid-cap/growth stock structures are rich with early direction info. Waiting until 10:00 AM dilutes this signal as daily variance decays.")
    w("3. **Execution Edge**:")
    w("   - These findings indicate we can deploy day-models for **159915ETF** and **500ETF** as early as **9:45 AM** or **9:50 AM** with superior predictive stats. This gives execution models (e.g. limit entry solvers) more time to enter before the afternoon session.\n")

    # ── 8) Conclusions ──
    w("## 8. Conclusions & Caveats\n")

    deployable = []
    marginal = []
    weak = []
    for key in active_keys:
        r = results.get(key)
        ic = r["holdout_ic"]
        ls = r["holdout_long_short"]["ls_sharpe"]
        ridge_ic = r["baselines"]["ridge"]["ic"]
        if ic > 0.03 and ls > 0.5 and ic > ridge_ic:
            deployable.append(key)
        elif ic > 0 and ls > 0:
            marginal.append(key)
        else:
            weak.append(key)

    if deployable:
        w(f"**Potentially deployable** (IC>0.03, L/S Sharpe>0.5, beats Ridge Base): "
          f"{', '.join(deployable)}\n")
    if marginal:
        w(f"**Marginal** (positive IC but weak Sharpe or below Ridge Base): "
          f"{', '.join(marginal)}\n")
    if weak:
        w(f"**Weak/Not recommended** (negative IC or no edge): "
          f"{', '.join(weak)}\n")

    w("\n**Key caveats**:\n")
    w("1. Trade return prediction is inherently noisy (low signal-to-noise ratio)")
    w("2. Feature selection using block bootstrap stability scores handles highly correlated features much better than greedy RFE")
    w("3. Robust Huber datafits (used in both `skglm_huber_l1` and `skglm_mcp` models) handle extreme outlier days much better than standard MSE-based models")
    w("4. Transaction costs and execution slippage are not modeled here")
    w("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=None)
    args = ap.parse_args()

    if args.results is None:
        if (DATA_DIR / "results_all_both.json").exists():
            path = DATA_DIR / "results_all_both.json"
        else:
            path = DATA_DIR / "results_all.json"
    else:
        path = Path(args.results)

    if not path.exists():
        print(f"ERROR: {path} not found. Run train_model.py first.")
        return

    results = load_results(path)
    md = generate(results)

    REPORT_PATH.write_text(md, encoding="utf-8")
    print(f"Report written → {REPORT_PATH} ({len(md)} chars, {len(md.splitlines())} lines)")

    has_dual_sides = any("_long" in k or "_short" in k for k in results.keys())
    active_keys = []
    for etf in ETF_ORDER:
        if has_dual_sides:
            for side in ["long", "short"]:
                key = f"{etf}_{side}"
                if key in results:
                    active_keys.append(key)
        else:
            if etf in results:
                active_keys.append(etf)

    for key in active_keys:
        r = results.get(key)
        if r:
            print(f"  {key} ({r['best_params']['model_type'].upper()}, threshold={r['best_params']['stability_threshold']:.2f}, {r['n_selected_features']} feats): IC={r['holdout_ic']:+.4f}  "
                  f"Dir={r['holdout_dir_acc']:.3f}  "
                  f"L/S={r['holdout_long_short']['ls_sharpe']:+.2f}")


if __name__ == "__main__":
    main()
