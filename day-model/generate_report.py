"""
Phase 3: Generate day-model/REPORT.md summary from training results.
"""
import json
import sys
import warnings
warnings.filterwarnings("ignore")
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, rankdata

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent))
# Import custom penalty so joblib can deserialize the model successfully
from penalties import MCP_plus_L2

DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
REPORT_PATH = HERE / "REPORT.md"

ETF_ORDER = ["300ETF", "500ETF", "588000ETF", "159915ETF"]
TARGET = "trade_return"
LOCKBOX_DATE = "2024-03-01"

def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 5 or np.std(y_pred) < 1e-12 or np.std(y_true) < 1e-12:
        return 0.0
    rho, _ = spearmanr(y_pred, y_true)
    return float(rho) if not np.isnan(rho) else 0.0

def compute_decile_monotonicity(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    n = len(y_true)
    if n < 20 or np.std(y_pred) < 1e-12:
        return 0.0
    order = np.argsort(np.asarray(y_pred, dtype=np.float64), kind="quicksort")
    yt_sorted = np.asarray(y_true, dtype=np.float64)[order]
    chunks = np.array_split(yt_sorted, 10)
    means = np.array([c.mean() if c.size else np.nan for c in chunks])
    valid = ~np.isnan(means)
    if valid.sum() < 3:
        return 0.0
    m = means[valid]
    r = rankdata(m)
    k = m.shape[0]
    a = np.arange(1, k + 1, dtype=np.float64)
    a -= a.mean()
    r -= r.mean()
    denom = np.sqrt((a * a).sum() * (r * r).sum())
    if denom < 1e-12:
        return 0.0
    return float((a * r).sum() / denom)


def block_bootstrap_ci(y_true, y_pred, block_size=10, n_bootstraps=1000):
    n = len(y_true)
    if n < block_size:
        block_size = max(1, n // 5)
        
    boot_ics = []
    boot_monos = []
    
    # Generate all starting indices for blocks
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = n - block_size + 1
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    if possible_starts <= 0:
        for _ in range(n_bootstraps):
            idx = np.random.choice(n, size=n, replace=True)
            y_b = y_true[idx]
            p_b = y_pred[idx]
            boot_ics.append(spearman_ic(y_b, p_b))
            boot_monos.append(compute_decile_monotonicity(y_b, p_b))
    else:
        for _ in range(n_bootstraps):
            starts = np.random.choice(possible_starts, size=num_blocks, replace=True)
            boot_idx = []
            for s in starts:
                boot_idx.extend(range(s, s + block_size))
            boot_idx = np.array(boot_idx[:n])
            
            y_b = y_true[boot_idx]
            p_b = y_pred[boot_idx]
            boot_ics.append(spearman_ic(y_b, p_b))
            boot_monos.append(compute_decile_monotonicity(y_b, p_b))
            
    ci_ic = (float(np.percentile(boot_ics, 2.5)), float(np.percentile(boot_ics, 97.5)))
    ci_mono = (float(np.percentile(boot_monos, 2.5)), float(np.percentile(boot_monos, 97.5)))
    
    return ci_ic, ci_mono


def main():
    print("Generating day-model REPORT.md...")
    
    results_dict = {}
    for p in DATA_DIR.glob("results_*.json"):
        try:
            with open(p) as f:
                r = json.load(f)
                results_dict[r["etf"]] = r
        except Exception as e:
            print(f"  [WARNING] Failed to load {p.name}: {e}")
            
    if not results_dict:
        print("  [ERROR] No results files found in data directory. Run train_model.py first.")
        return

    PLOTS_DIR.mkdir(exist_ok=True)

    # 1. First Pass: Load data/models/scalers, evaluate OOS lockbox metrics, update JSONs, and plot diagnostics
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        tag = r.get("tag", etf)
        features_path = DATA_DIR / f"features_{etf}.parquet"
        model_path = MODELS_DIR / f"linear_{tag}.joblib"
        scaler_path = MODELS_DIR / f"scaler_{tag}.joblib"

        if features_path.exists() and model_path.exists() and scaler_path.exists():
            try:
                print(f"Processing and generating diagnostics plot for {etf}...")
                # Load features parquet
                df = pd.read_parquet(features_path)
                if "date" not in df.columns:
                    df = df.reset_index()
                df = df.sort_values("date").reset_index(drop=True)
                df["date"] = pd.to_datetime(df["date"])

                # Load model & scaler metadata
                model = joblib.load(model_path)
                scaler_meta = joblib.load(scaler_path)
                selected_features = scaler_meta["selected_features"]
                scaler = scaler_meta["scaler"]
                target_col = scaler_meta.get("target", TARGET)

                # Prep features & target
                y = df[target_col].values.astype(np.float32)
                y_scaled = (y * 100.0).astype(np.float32)
                X_df = df[selected_features].ffill().fillna(df[selected_features].median())
                X = X_df.values.astype(np.float32)

                # Scale & Predict all data
                X_scaled = scaler.transform(X)
                preds = model.predict(X_scaled)

                # Split out OOS data (lockbox)
                lockbox_mask = df["date"] >= LOCKBOX_DATE
                y_lockbox = y_scaled[lockbox_mask]
                preds_lockbox = preds[lockbox_mask]

                # Compute OOS lockbox metrics
                lockbox_ic = spearman_ic(y_lockbox, preds_lockbox)
                
                n_tail_lock = max(5, int(len(y_lockbox) * 0.10))
                top_idx_lock = np.argsort(preds_lockbox)[-n_tail_lock:]
                bot_idx_lock = np.argsort(preds_lockbox)[:n_tail_lock]
                tail_idx_lock = np.concatenate([bot_idx_lock, top_idx_lock])
                lockbox_tail_ic = spearman_ic(y_lockbox[tail_idx_lock], preds_lockbox[tail_idx_lock])

                # Update memory cache
                r["lockbox_overall_ic"] = lockbox_ic
                r["lockbox_tail_ic"] = lockbox_tail_ic
                r["n_samples_lockbox"] = len(y_lockbox)

                # Compute Generalization Gap
                deflated_val_ic = r.get("deflated_val_ic", np.nan)
                cv_ic_target = deflated_val_ic
                if np.isnan(cv_ic_target):
                    cv_ic_target = r.get("selection_val_overall_ic", np.nan)
                if np.isnan(cv_ic_target):
                    cv_ic_target = float(r["best_raw_metrics"][3])
                
                ic_generalization_gap = cv_ic_target - lockbox_ic
                
                lockbox_mono = compute_decile_monotonicity(y_lockbox, preds_lockbox)
                cv_mono = float(r["best_raw_metrics"][4])
                mono_generalization_gap = cv_mono - lockbox_mono
                
                r["lockbox_monotonicity"] = lockbox_mono
                r["ic_generalization_gap"] = ic_generalization_gap
                r["mono_generalization_gap"] = mono_generalization_gap

                # Lockbox block bootstrap
                ci_ic, ci_mono = block_bootstrap_ci(y_lockbox, preds_lockbox, block_size=10, n_bootstraps=1000)
                ic_swallowed = ci_ic[0] <= cv_ic_target <= ci_ic[1]
                mono_swallowed = ci_mono[0] <= cv_mono <= ci_mono[1]
                
                r["lockbox_ic_ci"] = ci_ic
                r["lockbox_mono_ci"] = ci_mono
                r["lockbox_ic_swallowed"] = ic_swallowed
                r["lockbox_mono_swallowed"] = mono_swallowed
                
                print(f"    OOS Lockbox IC: {lockbox_ic:+.4f} | 95% Block Bootstrap CI: [{ci_ic[0]:+.4f}, {ci_ic[1]:+.4f}]")
                print(f"      CV IC Target: {cv_ic_target:+.4f} | Swallowed (Noise)? {'YES (Noise)' if ic_swallowed else 'NO (Signal)'}")
                print(f"    OOS Monotonicity: {lockbox_mono:+.4f} | 95% Block Bootstrap CI: [{ci_mono[0]:+.4f}, {ci_mono[1]:+.4f}]")
                print(f"      CV Monotonicity: {cv_mono:+.4f} | Swallowed (Noise)? {'YES (Noise)' if mono_swallowed else 'NO (Signal)'}")

                # Write updated result to JSON
                with open(DATA_DIR / f"results_{tag}.json", "w") as f_json:
                    json.dump(r, f_json, indent=2, default=str)

                # Write updated lockbox ICs to scaler bundle so scores.py / deploy.py read them correctly
                scaler_meta["holdout_ic"] = lockbox_ic
                scaler_meta["holdout_tail_ic"] = lockbox_tail_ic
                scaler_meta["holdout_mono"] = lockbox_mono
                scaler_meta["ic_gen_gap"] = ic_generalization_gap
                scaler_meta["mono_gen_gap"] = mono_generalization_gap
                scaler_meta["deflated_val_ic"] = deflated_val_ic
                scaler_meta["deflated_val_tail_ic"] = r.get("deflated_val_tail_ic", np.nan)
                joblib.dump(scaler_meta, scaler_path)

                # ─── Generate 2x2 Diagnostics Plot ───
                fig = plt.figure(figsize=(15, 12))
                gs = fig.add_gridspec(2, 2)
                
                # Plot 1: Feature coefficients (left column, spans both rows)
                ax1 = fig.add_subplot(gs[:, 0])
                coefs = model.coef_
                abs_coefs = np.abs(coefs)
                sort_idx = np.argsort(abs_coefs)
                
                # Cap to max 20 coefficients to avoid crowding
                max_coefs = 20
                if len(sort_idx) > max_coefs:
                    sort_idx = sort_idx[-max_coefs:]
                    
                sorted_coefs = coefs[sort_idx]
                sorted_feats = [selected_features[i] for i in sort_idx]
                
                ax1.barh(sorted_feats, sorted_coefs, color="royalblue")
                ax1.set_title(f"Model Coefficients (Top {len(sorted_feats)})")
                ax1.axvline(0, color="gray", linestyle="--")
                
                # Plot 2: Decile actual vs prediction (OOS data) (top right)
                ax2 = fig.add_subplot(gs[0, 1])
                df_oos = pd.DataFrame({"y_true": y_lockbox, "y_pred": preds_lockbox})
                df_oos["decile"] = pd.qcut(df_oos["y_pred"], 10, labels=False, duplicates="drop")
                decile_stats_oos = df_oos.groupby("decile")["y_true"].agg(["mean", "median", "std"])
                deciles_oos = decile_stats_oos.index + 1
                
                # Mean as bars (LHS)
                ax2.bar(deciles_oos, decile_stats_oos["mean"], color="green", alpha=0.9, label="Mean")
                # Median as points (LHS)
                ax2.scatter(deciles_oos, decile_stats_oos["median"], color="darkorange", marker="o", s=50, label="Median", zorder=3)
                ax2.set_xlabel("Predicted Decile (1=Low, 10=High)")
                ax2.set_ylabel("Mean / Median return (%)")
                ax2.set_title("Decile Performance Spread (OOS data)")
                ax2.set_xticks(range(1, 11))
                
                # S.d as points (RHS axis)
                ax2_twin = ax2.twinx()
                ax2_twin.scatter(deciles_oos, decile_stats_oos["std"], color="crimson", marker="x", s=50, label="S.D.", zorder=3)
                ax2_twin.set_ylabel("S.D. of return (%)", color="crimson")
                ax2_twin.tick_params(axis='y', labelcolor="crimson")
                
                # Combined legend
                h1, l1 = ax2.get_legend_handles_labels()
                h2, l2 = ax2_twin.get_legend_handles_labels()
                ax2.legend(h1 + h2, l1 + l2, loc="upper left")
                
                # Plot 3: Decile actual vs prediction (All data) (bottom right)
                ax3 = fig.add_subplot(gs[1, 1])
                df_all = pd.DataFrame({"y_true": y_scaled, "y_pred": preds})
                df_all["decile"] = pd.qcut(df_all["y_pred"], 10, labels=False, duplicates="drop")
                decile_stats_all = df_all.groupby("decile")["y_true"].agg(["mean", "median", "std"])
                deciles_all = decile_stats_all.index + 1
                
                # Mean as bars (LHS)
                ax3.bar(deciles_all, decile_stats_all["mean"], color="green", alpha=0.9, label="Mean")
                # Median as points (LHS)
                ax3.scatter(deciles_all, decile_stats_all["median"], color="darkorange", marker="o", s=50, label="Median", zorder=3)
                ax3.set_xlabel("Predicted Decile (1=Low, 10=High)")
                ax3.set_ylabel("Mean / Median return (%)")
                ax3.set_title("Decile Performance Spread (All data)")
                ax3.set_xticks(range(1, 11))
                
                # S.d as points (RHS axis)
                ax3_twin = ax3.twinx()
                ax3_twin.scatter(deciles_all, decile_stats_all["std"], color="crimson", marker="x", s=50, label="S.D.", zorder=3)
                ax3_twin.set_ylabel("S.D. of return (%)", color="crimson")
                ax3_twin.tick_params(axis='y', labelcolor="crimson")
                
                # Combined legend
                h3, l3 = ax3.get_legend_handles_labels()
                h4, l4 = ax3_twin.get_legend_handles_labels()
                ax3.legend(h3 + h4, l3 + l4, loc="upper left")
                
                plt.tight_layout()
                diagnostics_plot_name = f"diagnostics_{tag}.png"
                plt.savefig(PLOTS_DIR / diagnostics_plot_name, dpi=150)
                plt.close()
            except Exception as ex:
                print(f"  [WARNING] Failed to generate diagnostics plot for {etf}: {ex}")
        else:
            print(f"  [WARNING] Missing files for plot generation for {etf}")

    # 2. Second Pass: Start writing report
    lines = []
    lines.append("# Day-Model Remake Optimization Report")
    lines.append("> Generated by day-model/generate_report.py")
    lines.append("This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.")
    lines.append("")
    lines.append("## Out-of-Sample Lockbox Performance (2024-03 to Last Day)")
    lines.append("")
    lines.append("| ETF | Selected Features | Active Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        feats_count = len(r["selected_features"])
        active_count = len(r.get("active_features", r["selected_features"]))
        model_type = r["best_params"]["model_type"]
        overall_ic = r["lockbox_overall_ic"]
        tail_ic = r["lockbox_tail_ic"]
        lines.append(f"| {etf} | {feats_count} | {active_count} | `{model_type}` | {overall_ic:+.4f} | {tail_ic:+.4f} |")
        
    lines.append("")
    lines.append("## Detailed Trial Metrics & Optimization Objectives")
    lines.append("")
    lines.append("| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        m = r["best_raw_metrics"]
        # M1 (IR), M2 (Mean), M3 (Hit Rate), M5 (Monotonicity), M6 (Spread)
        lines.append(f"| {etf} | {m[0]:.4f} | {m[1]:+.4f} | {m[2]*100:.1f}% | {m[4]:.4f} | {m[5]*100:+.4f}% |")
        
    lines.append("")
    lines.append("## Model Quality & Generalization Diagnostics")
    lines.append("")
    lines.append("### Model Multi-Collinearity & Weight Concentration")
    lines.append("")
    lines.append("| ETF | Raw X Cond | Reg normal eq kappa | Collinear Pairs ($\\ge 0.85$) | Gini (Weight Concentration) | Tail Weight ESS | Tail Weight ESS % |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        diag = r.get("diagnostics", {})
        mq = diag.get("model_quality", {})
        
        cond_raw = mq.get("condition_number_raw", mq.get("condition_number"))
        cond_raw_str = f"{cond_raw:.2f}" if cond_raw is not None else "N/A"
        
        cond_reg = mq.get("condition_number_regularized", mq.get("condition_number"))
        cond_reg_str = f"{cond_reg:.2f}" if cond_reg is not None else "N/A"
        if cond_reg is not None and cond_reg > 100:
            cond_reg_str += " [SEVERE]"
        elif cond_reg is not None and cond_reg > 30:
            cond_reg_str += " [MODERATE]"
            
        coll = mq.get("collinear_pairs")
        coll_str = str(len(coll)) if coll is not None else "N/A"
        if coll is not None and len(coll) > 0:
            coll_str += " [WARNING]"
            
        gini = mq.get("gini_coefficient")
        gini_str = f"{gini:.4f}" if gini is not None else "N/A"
        if gini is not None and gini > 0.85:
            gini_str += " [HIGH]"
            
        ess = mq.get("effective_sample_size")
        ess_str = f"{ess:.1f}" if ess is not None else "N/A"
        
        ess_pct = mq.get("effective_sample_size_pct")
        ess_pct_str = f"{ess_pct*100:.1f}%" if ess_pct is not None else "N/A"
        if ess_pct is not None and ess_pct < 0.05:
            ess_pct_str += " [CRITICAL]"
        elif ess_pct is not None and ess_pct < 0.20:
            ess_pct_str += " [LOW]"
            
        lines.append(f"| {etf} | {cond_raw_str} | {cond_reg_str} | {coll_str} | {gini_str} | {ess_str} | {ess_pct_str} |")

    lines.append("")
    lines.append("### Generalization Gap (CV vs Selection Validation vs Out-of-Sample)")
    lines.append("")
    lines.append("| ETF | CV Overall IC | Deflated CV IC | Selection Val IC | Deflated Val IC | OOS Lockbox IC | IC Gen Gap (DefVal-OOS) | CV Monotonicity | OOS Monotonicity | Mono Gen Gap |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        
        cv_ic = r["best_raw_metrics"][3]
        deflated_cv_ic = r.get("deflated_cv_ic", np.nan)
        sel_val_ic = r.get("selection_val_overall_ic", np.nan)
        deflated_val_ic = r.get("deflated_val_ic", np.nan)
        oos_ic = r.get("lockbox_overall_ic", np.nan)
        ic_gap = r.get("ic_generalization_gap", np.nan)
        
        cv_mono = r["best_raw_metrics"][4]
        oos_mono = r.get("lockbox_monotonicity", np.nan)
        mono_gap = r.get("mono_generalization_gap", np.nan)
        
        deflated_cv_ic_str = f"{deflated_cv_ic:+.4f}" if not np.isnan(deflated_cv_ic) else "N/A"
        sel_val_ic_str = f"{sel_val_ic:+.4f}" if not np.isnan(sel_val_ic) else "N/A"
        deflated_val_ic_str = f"{deflated_val_ic:+.4f}" if not np.isnan(deflated_val_ic) else "N/A"
        oos_ic_str = f"{oos_ic:+.4f}" if not np.isnan(oos_ic) else "N/A"
        ic_gap_str = f"{ic_gap:+.4f}" if not np.isnan(ic_gap) else "N/A"
        if not np.isnan(ic_gap) and ic_gap > 0.05:
            ic_gap_str += " [OVERFIT]"
            
        oos_mono_str = f"{oos_mono:+.4f}" if not np.isnan(oos_mono) else "N/A"
        mono_gap_str = f"{mono_gap:+.4f}" if not np.isnan(mono_gap) else "N/A"
        if not np.isnan(mono_gap) and mono_gap > 0.20:
            mono_gap_str += " [DEGRADED]"
            
        lines.append(f"| {etf} | {cv_ic:+.4f} | {deflated_cv_ic_str} | {sel_val_ic_str} | {deflated_val_ic_str} | {oos_ic_str} | {ic_gap_str} | {cv_mono:+.4f} | {oos_mono_str} | {mono_gap_str} |")

    lines.append("")
    lines.append("### Overfitting Diagnostics (PBO & Lockbox Bootstrap CIs)")
    lines.append("")
    lines.append("| ETF | PBO | Perf Degradation | OOS Lockbox IC 95% CI | CV IC Target | IC Gen Gap Sig? | OOS Mono 95% CI | CV Mono | Mono Gen Gap Sig? |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        
        pbo = r.get("pbo", np.nan)
        perf_deg = r.get("performance_degradation", np.nan)
        pbo_str = f"{pbo*100:.1f}%" if not np.isnan(pbo) else "N/A"
        perf_deg_str = f"{perf_deg:+.4f}" if not np.isnan(perf_deg) else "N/A"
        
        ci_ic = r.get("lockbox_ic_ci")
        ci_ic_str = f"[{ci_ic[0]:+.4f}, {ci_ic[1]:+.4f}]" if ci_ic is not None else "N/A"
        
        cv_ic_target = r.get("deflated_val_ic", np.nan)
        if np.isnan(cv_ic_target):
            cv_ic_target = r.get("selection_val_overall_ic", np.nan)
        if np.isnan(cv_ic_target):
            cv_ic_target = float(r["best_raw_metrics"][3])
        cv_ic_target_str = f"{cv_ic_target:+.4f}" if not np.isnan(cv_ic_target) else "N/A"
        
        ic_swallowed = r.get("lockbox_ic_swallowed")
        ic_sig_str = "Noise (Not Sig)" if ic_swallowed else ("Signal (Sig)" if ic_swallowed is not None else "N/A")
        
        ci_mono = r.get("lockbox_mono_ci")
        ci_mono_str = f"[{ci_mono[0]:+.4f}, {ci_mono[1]:+.4f}]" if ci_mono is not None else "N/A"
        
        cv_mono = float(r["best_raw_metrics"][4])
        cv_mono_str = f"{cv_mono:+.4f}"
        
        mono_swallowed = r.get("lockbox_mono_swallowed")
        mono_sig_str = "Noise (Not Sig)" if mono_swallowed else ("Signal (Sig)" if mono_swallowed is not None else "N/A")
        
        lines.append(f"| {etf} | {pbo_str} | {perf_deg_str} | {ci_ic_str} | {cv_ic_target_str} | **{ic_sig_str}** | {ci_mono_str} | {cv_mono_str} | **{mono_sig_str}** |")

    lines.append("")
    lines.append("### Lockbox Noise vs Signal Assessment Details")
    lines.append("")
    lines.append("Detailed analysis comparing OOS lockbox metrics to their CV target estimates under block bootstrap:")
    lines.append("")
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        
        cv_ic_target = r.get("deflated_val_ic", np.nan)
        if np.isnan(cv_ic_target):
            cv_ic_target = r.get("selection_val_overall_ic", np.nan)
        if np.isnan(cv_ic_target):
            cv_ic_target = float(r["best_raw_metrics"][3])
            
        ci_ic = r.get("lockbox_ic_ci")
        ic_swallowed = r.get("lockbox_ic_swallowed")
        ic_status = "Noise (not statistically significant)" if ic_swallowed else "Signal (statistically significant)"
        ic_swallowed_str = "swallowed" if ic_swallowed else "not swallowed"
        
        cv_mono = float(r["best_raw_metrics"][4])
        ci_mono = r.get("lockbox_mono_ci")
        mono_swallowed = r.get("lockbox_mono_swallowed")
        mono_status = "Noise (not statistically significant)" if mono_swallowed else "Signal (statistically significant)"
        mono_swallowed_str = "swallowed" if mono_swallowed else "not swallowed"
        
        ci_ic_str = f"`[{ci_ic[0]:+.4f}, {ci_ic[1]:+.4f}]`" if ci_ic is not None else "N/A"
        ci_mono_str = f"`[{ci_mono[0]:+.4f}, {ci_mono[1]:+.4f}]`" if ci_mono is not None else "N/A"
        
        lines.append(f"#### {etf}")
        lines.append(f"- **Rank IC Generalization**: OOS Lockbox IC of **{r['lockbox_overall_ic']:+.4f}** (95% CI: {ci_ic_str}) vs CV Target of **{cv_ic_target:+.4f}**. The CV target is **{ic_swallowed_str}** by the OOS CI, indicating the generalization gap is **{ic_status}**.")
        lines.append(f"- **Decile Monotonicity Generalization**: OOS Monotonicity of **{r['lockbox_monotonicity']:+.4f}** (95% CI: {ci_mono_str}) vs CV Monotonicity of **{cv_mono:+.4f}**. The CV estimate is **{mono_swallowed_str}** by the OOS CI, indicating the generalization gap is **{mono_status}**.")
        lines.append("")

    lines.append("### Feature Selection Metrics & Fallbacks")
    lines.append("")
    lines.append("| ETF | Screening Input | BH-FDR Pass | Screen Fallback? | Stability Input | Stability Pass | Stability Fallback? | Kept Features |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        diag = r.get("diagnostics", {})
        scr = diag.get("screening", {})
        stab = diag.get("stability", {})
        
        scr_in = scr.get("total_features", "N/A")
        scr_pass = scr.get("bh_pass_count", "N/A")
        scr_fb = "YES [WARNING]" if scr.get("fallback_triggered", False) else "NO"
        
        stab_in = scr.get("keep_count", "N/A")
        stab_pass = stab.get("pass_pi_count", "N/A")
        stab_fb = "YES [WARNING]" if stab.get("fallback_triggered", False) else "NO"
        
        kept = stab.get("keep_count", len(r["selected_features"]))
        lines.append(f"| {etf} | {scr_in} | {scr_pass} | {scr_fb} | {stab_in} | {stab_pass} | {stab_fb} | **{kept}** |")

    lines.append("")
    lines.append("### Optuna Main Study & Pruning Reasons")
    lines.append("")
    lines.append("| ETF | Total Trials | Completed | Pruned / Failed | M4 Pruned | M3 Pruned | M5 Pruned | M6 Pruned | ESS Pruned | Floor Pruned | Gini Pruned |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        diag = r.get("diagnostics", {})
        opt = diag.get("optuna_main", {})
        
        tot = opt.get("total_trials", 0)
        comp = opt.get("completed_count", 0)
        pruned_failed = opt.get("pruned_count", 0) + opt.get("failed_count", 0)
        
        reasons = opt.get("pruning_reasons", {})
        m4_p = reasons.get("M4 (Overall IC <= 0)", 0)
        m3_p = reasons.get("M3 (Hit Rate < 60%)", 0)
        m5_p = reasons.get("M5 (Monotonicity <= 0.25)", 0)
        m6_p = reasons.get("M6 (Top-Bottom Spread <= 0)", 0)
        ess_p = reasons.get("exceeds ESS-based cap", 0)
        floor_p = reasons.get("active feature floor", 0)
        gini_p = reasons.get("Gini coefficient", 0)
        
        lines.append(f"| {etf} | {tot} | {comp} | {pruned_failed} | {m4_p} | {m3_p} | {m5_p} | {m6_p} | {ess_p} | {floor_p} | {gini_p} |")

    lines.append("")
    lines.append("### Hyperparameter Parameter Plateau Selection")
    lines.append("")
    lines.append("Instead of selecting hyperparameters based on point-optimal peak objective values, we select hyperparameter configurations that reside on a stable parameter plateau (evaluating trial neighborhoods at radius $r=0.25$).")
    lines.append("")
    lines.append("| ETF | Selected Plateau Trial | Plateau Objective | Raw Best Trial | Raw Best Objective |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        
        plat_trial = r.get("plateau_trial")
        plat_val = r.get("plateau_val")
        raw_trial = r.get("raw_best_trial")
        raw_val = r.get("raw_best_val")
        
        plat_trial_str = str(plat_trial) if plat_trial is not None else "N/A"
        plat_val_str = f"{plat_val:+.4f}" if plat_val is not None else "N/A"
        raw_trial_str = str(raw_trial) if raw_trial is not None else "N/A"
        raw_val_str = f"{raw_val:+.4f}" if raw_val is not None else "N/A"
        
        lines.append(f"| {etf} | {plat_trial_str} | {plat_val_str} | {raw_trial_str} | {raw_val_str} |")

    lines.append("")
    lines.append("## Selected Features per ETF")
    lines.append("")
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        tag = r.get("tag", etf)
        lines.append(f"### {etf}")
        lines.append(f"- **Total selected features (Stability Selection)**: {len(r['selected_features'])}")
        active_feats = r.get("active_features", r["selected_features"])
        lines.append(f"- **Active features (Non-zero weights)**: {len(active_feats)}")
        lines.append("- **Active features**: " + ", ".join([f"`{f}`" for f in active_feats]))
        lines.append("")
        
        # Embed the generated diagnostics plot
        lines.append(f"![{etf} Diagnostics](plots/diagnostics_{tag}.png)")
        lines.append("")
        
    lines.append("## Methodology Overview")
    lines.append("1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).")
    lines.append("2. **Selection Validation Split**: Six non-contiguous 3-month blocks (totaling ~18 months or ~370 trading days) carved out from the working set for selection-blind validation, with a 10-day embargo applied to training boundaries to prevent temporal data leakage.")
    lines.append("3. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.40 (run only on selection training set, excluding validation blocks).")
    lines.append("4. **Hierarchical Clustering**: Groups collinear features (correlation threshold |r| >= 0.75, distance = 0.25) and aggregates bootstrap votes at cluster level.")
    lines.append(r"5. **Stability Selection**: Runs ElasticNet path (l1_ratio = 0.5) over $B=100$ subsamples on screened features, selecting clusters with frequency $\ge 0.60$, then selecting the most stable representative.")
    lines.append("6. **VIF Pruning**: Iteratively drops features with Variance Inflation Factor (VIF) > 10.0 to eliminate multi-collinearity.")
    lines.append("7. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.")
    lines.append("8. **Optuna Objective**: Standardized multi-metric maximization evaluated on the selection-blind validation blocks, deflated using Marcos Lopez de Prado method, and subject to hard CV constraints, Gini weight concentration limit (Gini <= 0.85), and continuous ESS penalties.")
    
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))
        
    print(f"REPORT.md written to {REPORT_PATH}")

if __name__ == "__main__":
    main()


