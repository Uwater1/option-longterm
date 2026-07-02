"""
Phase 3: Generate day-model/REPORT.md summary from training results.
"""
import json
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
REPORT_PATH = HERE / "REPORT.md"

ETF_ORDER = ["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"]
TARGET = "trade_return"
LOCKBOX_DATE = "2024-03-01"

def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 5 or np.std(y_pred) < 1e-12 or np.std(y_true) < 1e-12:
        return 0.0
    rho, _ = spearmanr(y_pred, y_true)
    return float(rho) if not np.isnan(rho) else 0.0

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

                # Write updated result to JSON
                with open(DATA_DIR / f"results_{tag}.json", "w") as f_json:
                    json.dump(r, f_json, indent=2, default=str)

                # Write updated lockbox ICs to scaler bundle so scores.py / deploy.py read them correctly
                scaler_meta["holdout_ic"] = lockbox_ic
                scaler_meta["holdout_tail_ic"] = lockbox_tail_ic
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
    lines.append("")
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
    lines.append("## Training Process Diagnostics & Execution Profiling")
    lines.append("")
    lines.append("### Stage Durations (seconds)")
    lines.append("")
    lines.append("| ETF | Data Load | Feature Select | LOYO Folds | Pilot Study | Main Study | Final Refit | Total |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for etf in ETF_ORDER:
        if etf not in results_dict:
            continue
        r = results_dict[etf]
        diag = r.get("diagnostics", {})
        timings = diag.get("timings", {})
        load_t = timings.get("data_loading", 0.0)
        sel_t = timings.get("feature_selection", 0.0)
        loyo_t = timings.get("loyo_folds", 0.0)
        pilot_t = timings.get("pilot_study", 0.0)
        main_t = timings.get("main_study", 0.0)
        refit_t = timings.get("final_refit", 0.0)
        total_t = load_t + sel_t + loyo_t + pilot_t + main_t + refit_t
        lines.append(f"| {etf} | {load_t:.1f}s | {sel_t:.1f}s | {loyo_t:.1f}s | {pilot_t:.1f}s | {main_t:.1f}s | {refit_t:.1f}s | {total_t:.1f}s |")

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
    lines.append("| ETF | Total Trials | Completed | Pruned / Failed | M4 Pruned | M3 Pruned | M5 Pruned | M6 Pruned |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
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
        
        lines.append(f"| {etf} | {tot} | {comp} | {pruned_failed} | {m4_p} | {m3_p} | {m5_p} | {m6_p} |")

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
    lines.append("2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.")
    lines.append("3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.")
    lines.append(r"4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.")
    lines.append("5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.")
    lines.append("6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).")
    
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))
        
    print(f"REPORT.md written to {REPORT_PATH}")

if __name__ == "__main__":
    main()


