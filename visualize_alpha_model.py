"""
Alpha Model Visualization — Why it works, how to improve, where to plug in
============================================================================
Generates graphs for the put_improvement_plan.md TODO 3 documentation.

Usage:
  python visualize_alpha_model.py           # Generate all plots for all ETFs
  python visualize_alpha_model.py -e 300    # Generate for 300ETF only
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.abspath("."))
from backtest_engine import select_underlying, load_data
from alpha_model import AlphaModel
from optimize_put_alpha import compute_forward_targets

OUT_DIR = "backtest"
os.makedirs(OUT_DIR, exist_ok=True)

REGIME_NAMES = {
    "reg1": "Regime 1: ST Fall",
    "reg2": "Regime 2: MT Fall",
    "reg3": "Regime 3: ST Crash",
    "reg4": "Regime 4: MT Crash",
}
REGIME_COLORS = {"reg1": "#2980b9", "reg2": "#27ae60", "reg3": "#e74c3c", "reg4": "#8e44ad"}

try:
    plt.style.use("seaborn-v0_8-muted")
except Exception:
    plt.style.use("ggplot")


def load_models():
    with open("backtest/alpha_put_models.json") as f:
        return json.load(f)


def plot_1_score_vs_return(etf_choice, df_norm, models, regime_key):
    """
    WHY IT WORKS: Scatter plot of alpha score vs forward return for Fall regimes,
    or vs worst drawdown for Crash regimes. Shows that high scores predict bad outcomes.
    """
    is_crash = regime_key in ("reg3", "reg4")
    m = models[etf_choice][regime_key]
    horizon = m["horizon"]
    threshold = m["threshold"]
    weights = m["weights"]

    # Compute score using optimized weights
    active_inds = [ind for ind in weights if ind in df_norm.columns]
    score = pd.Series(0.0, index=df_norm.index)
    w_sum = 0.0
    for ind in active_inds:
        score += df_norm[ind].fillna(0.0) * weights[ind]
        w_sum += weights[ind]
    score = score / w_sum if w_sum > 0 else score

    fwd_ret, worst_dd = compute_forward_targets(df_norm, horizon)
    target = worst_dd if is_crash else fwd_ret
    target_label = f"Worst Drawdown ({horizon}d)" if is_crash else f"Forward Return ({horizon}d)"

    valid = pd.DataFrame({"score": score, "target": target}).dropna()
    if len(valid) < 50:
        return

    triggered = valid["score"] > threshold
    corr = np.corrcoef(valid["score"], valid["target"])[0, 1]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Scatter with threshold line
    ax = axes[0]
    ax.scatter(valid.loc[~triggered, "score"], valid.loc[~triggered, "target"] * 100,
               alpha=0.15, s=8, color="#95a5a6", label="Below threshold")
    ax.scatter(valid.loc[triggered, "score"], valid.loc[triggered, "target"] * 100,
               alpha=0.5, s=12, color=REGIME_COLORS[regime_key], label=f"Triggered (score > {threshold:.3f})")
    ax.axvline(threshold, color="#e67e22", linestyle="--", linewidth=2, label=f"Threshold = {threshold:.3f}")
    ax.set_xlabel("Alpha Score", fontsize=11)
    ax.set_ylabel(f"{target_label} (%)", fontsize=11)
    ax.set_title(f"{REGIME_NAMES[regime_key]} — Score vs Outcome\n{etf_choice}ETF  corr={corr:.3f}  N={len(valid)}",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Right: Distribution comparison
    ax2 = axes[1]
    bins = np.linspace(valid["target"].quantile(0.01) * 100, valid["target"].quantile(0.99) * 100, 50)
    ax2.hist(valid.loc[~triggered, "target"] * 100, bins=bins, alpha=0.4, color="#95a5a6",
             density=True, label=f"Not triggered (N={(~triggered).sum()})")
    ax2.hist(valid.loc[triggered, "target"] * 100, bins=bins, alpha=0.6, color=REGIME_COLORS[regime_key],
             density=True, label=f"Triggered (N={triggered.sum()})")
    if not is_crash:
        mean_trig = valid.loc[triggered, "target"].mean() * 100
        mean_base = valid["target"].mean() * 100
        ax2.axvline(mean_trig, color=REGIME_COLORS[regime_key], linestyle="-", linewidth=2,
                    label=f"Mean triggered: {mean_trig:+.2f}%")
        ax2.axvline(mean_base, color="#95a5a6", linestyle="-", linewidth=2,
                    label=f"Mean baseline: {mean_base:+.2f}%")
    else:
        crash_trig = (valid.loc[triggered, "target"] <= -0.05).mean() * 100
        crash_base = (valid["target"] <= -0.05).mean() * 100
        ax2.axvline(-5, color="#e74c3c", linestyle=":", linewidth=2, label="Crash threshold (-5%)")
        title_extra = f"\nCrash prob: {crash_trig:.1f}% triggered vs {crash_base:.1f}% baseline"
        ax.set_title(ax.get_title() + title_extra, fontsize=12, fontweight="bold")

    ax2.set_xlabel(f"{target_label} (%)", fontsize=11)
    ax2.set_ylabel("Density", fontsize=11)
    ax2.set_title("Outcome Distribution: Triggered vs Baseline", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    out = f"{OUT_DIR}/alpha_score_vs_return_{etf_choice}_{regime_key}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {out}")


def plot_2_all_regimes_summary(etf_choice, df_norm, models):
    """
    WHY IT WORKS: 4-panel bar chart showing triggered vs baseline metrics for all regimes.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, reg_key in enumerate(["reg1", "reg2", "reg3", "reg4"]):
        ax = axes[i]
        m = models[etf_choice][reg_key]
        is_crash = reg_key in ("reg3", "reg4")
        metrics = m["metrics"]

        if is_crash:
            trig_prob = metrics["triggered_crash_prob"] * 100
            base_prob = metrics["baseline_crash_prob"] * 100
            lift = metrics["lift"]
            bars = ax.bar(["Baseline", "Triggered"], [base_prob, trig_prob],
                         color=["#bdc3c7", REGIME_COLORS[reg_key]], width=0.5)
            ax.set_ylabel("Crash Probability (%)", fontsize=11)
            ax.set_title(f"{REGIME_NAMES[reg_key]}\n{m['horizon']}d horizon, lift={lift:.2f}x",
                        fontsize=12, fontweight="bold")
            for bar, val in zip(bars, [base_prob, trig_prob]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       f"{val:.1f}%", ha="center", fontsize=11, fontweight="bold")
        else:
            trig_ret = metrics["mean_return_triggered"] * 100
            base_ret = metrics["mean_return_baseline"] * 100
            diff = trig_ret - base_ret
            bars = ax.bar(["Baseline", "Triggered"], [base_ret, trig_ret],
                         color=["#bdc3c7", REGIME_COLORS[reg_key]], width=0.5)
            ax.set_ylabel(f"Mean Return ({m['horizon']}d) %", fontsize=11)
            ax.set_title(f"{REGIME_NAMES[reg_key]}\n{m['horizon']}d horizon, diff={diff:+.2f}%",
                        fontsize=12, fontweight="bold")
            for bar, val in zip(bars, [base_ret, trig_ret]):
                ax.text(bar.get_x() + bar.get_width()/2, max(bar.get_height(), 0) + 0.05,
                       f"{val:+.2f}%", ha="center", fontsize=11, fontweight="bold")
            ax.axhline(0, color="black", linewidth=0.8)

        ax.grid(True, axis="y", linestyle="--", alpha=0.5)
        ax.set_xlabel("")

    plt.suptitle(f"{etf_choice}ETF — Alpha Model: Why It Works\nTriggered signals predict significantly worse outcomes",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out = f"{OUT_DIR}/alpha_regimes_summary_{etf_choice}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {out}")


def plot_3_weight_importance(models):
    """
    HOW TO IMPROVE: Stacked bar chart showing optimized weights per regime per ETF.
    Shows which indicators dominate and where new alphas could help.
    """
    etfs = sorted(models.keys())
    fig, axes = plt.subplots(len(etfs), 4, figsize=(18, 4 * len(etfs)))
    if len(etfs) == 1:
        axes = axes.reshape(1, -1)

    INDICATOR_NAMES = {
        "ind_rsi_high": "RSI High",
        "ind_rsi_low": "RSI Low",
        "ind_skew_neg": "Skewness",
        "ind_kurt_high": "Kurtosis",
        "ind_vol_accel_high": "Vol Accel",
        "ind_iv_vol_low": "IV/RV Ratio",
        "ind_dd_deep": "Drawdown",
        "ind_dist_sma50_neg": "Dist SMA50",
        "ind_dist_sma200_neg": "Dist SMA200",
        "ind_roc5_neg": "ROC5",
        "ind_roc20_neg": "ROC20",
        "ind_macd_neg": "MACD Hist",
    }
    IND_COLORS = {
        "ind_rsi_high": "#e74c3c", "ind_rsi_low": "#3498db",
        "ind_skew_neg": "#2ecc71", "ind_kurt_high": "#9b59b6",
        "ind_vol_accel_high": "#f39c12", "ind_iv_vol_low": "#1abc9c",
        "ind_dd_deep": "#e67e22", "ind_dist_sma50_neg": "#34495e",
        "ind_dist_sma200_neg": "#7f8c8d", "ind_roc5_neg": "#c0392b",
        "ind_roc20_neg": "#2980b9", "ind_macd_neg": "#8e44ad",
    }

    for i, etf in enumerate(etfs):
        for j, reg_key in enumerate(["reg1", "reg2", "reg3", "reg4"]):
            ax = axes[i, j]
            weights = models[etf][reg_key]["weights"]
            # Sort by weight descending
            sorted_items = sorted(weights.items(), key=lambda x: -x[1])
            names = [INDICATOR_NAMES.get(k, k) for k, _ in sorted_items]
            vals = [v for _, v in sorted_items]
            colors = [IND_COLORS.get(k, "#bdc3c7") for k, _ in sorted_items]

            bars = ax.barh(names, vals, color=colors, height=0.6)
            ax.set_xlim(0, 1)
            ax.set_title(f"{REGIME_NAMES[reg_key]}", fontsize=10, fontweight="bold")
            if j == 0:
                ax.set_ylabel(f"{etf}ETF", fontsize=12, fontweight="bold")
            for bar, val in zip(bars, vals):
                if val > 0.05:
                    ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
                           f"{val:.0%}", va="center", fontsize=8)
            ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    plt.suptitle("Alpha Model: Optimized Indicator Weights per Regime\n"
                 "Dominant indicators (weight > 50%) indicate single-factor dependency — room for improvement",
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = f"{OUT_DIR}/alpha_weight_importance.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {out}")


def plot_4_architecture_diagram():
    """
    WHERE TO PLUG NEW ALPHAS: Architecture diagram showing extension points.
    """
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis("off")

    def draw_box(x, y, w, h, text, color="#3498db", fontsize=10, bold=False):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                             facecolor=color, edgecolor="white", linewidth=2, alpha=0.9)
        ax.add_patch(box)
        weight = "bold" if bold else "normal"
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, fontweight=weight, color="white", wrap=True)

    def draw_arrow(x1, y1, x2, y2, color="#2c3e50", style="->", lw=2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw))

    # Title
    ax.text(8, 11.5, "Alpha Model Architecture — Where to Plug New Alphas",
            ha="center", fontsize=16, fontweight="bold", color="#2c3e50")

    # Layer 1: Raw Data
    draw_box(0.5, 9.5, 3, 1.2, "Raw ETF Data\n(1d parquet)\nclose_adj, high_adj, low_adj", "#7f8c8d", 9)
    draw_box(4.5, 9.5, 3, 1.2, "Option Data\nIV cache, 5m prices\nstrike/multiplier", "#7f8c8d", 9)
    draw_box(8.5, 9.5, 3.5, 1.2, "External Data\n(Sentiment, Macro,\nSector Rotation)", "#95a5a6", 9)

    # Layer 2: Indicator Computation
    draw_box(1, 7.5, 14, 1.3, "AlphaModel.compute_normalized_indicators(df)\n"
             "Rolling 252d percentile rank → [0, 1] normalized, look-ahead free\n"
             "★ ADD NEW INDICATORS HERE: add column, update this method", "#2980b9", 10, True)

    # Layer 3: Regime Weights
    draw_box(0.5, 5.5, 3.2, 1.3, "Regime 1: ST Fall\nScore = Σ(w_i × I_i)\nHorizon: 5-14d", REGIME_COLORS["reg1"], 9, True)
    draw_box(4.2, 5.5, 3.2, 1.3, "Regime 2: MT Fall\nScore = Σ(w_i × I_i)\nHorizon: 21-40d", REGIME_COLORS["reg2"], 9, True)
    draw_box(8, 5.5, 3.2, 1.3, "Regime 3: ST Crash\nScore = Σ(w_i × I_i)\nHorizon: 5-14d", REGIME_COLORS["reg3"], 9, True)
    draw_box(11.8, 5.5, 3.2, 1.3, "Regime 4: MT Crash\nScore = Σ(w_i × I_i)\nHorizon: 21-40d", REGIME_COLORS["reg4"], 9, True)

    # Layer 4: Optimization
    draw_box(0.5, 3.5, 7, 1.3, "optimize_put_alpha.py\nGrid search: horizons × random weights × thresholds\n"
             "★ RETRAIN HERE after adding new indicators", "#e67e22", 9, True)
    draw_box(8.5, 3.5, 6.5, 1.3, "alpha_put_models.json\nOptimized weights, thresholds, horizons per ETF\n"
             "★ OUTPUT: consumed by backtest engine", "#f39c12", 9, True)

    # Layer 5: Backtest Integration
    draw_box(2, 1.2, 5, 1.5, "backtest_strategies.py\nPutStrategy.evaluate_filter()\n"
             "★ INTEGRATION POINT:\nReplace static filter with alpha score > threshold", "#27ae60", 9, True)
    draw_box(8, 1.2, 6, 1.5, "backtest_engine.py\nDaily signal scanning (TODO 4)\n"
             "should_enter_today() / should_exit_today()\n"
             "★ ARCHITECTURE: enable mid-cycle entries", "#8e44ad", 9, True)

    # Arrows
    for x in [2, 6, 10.25]:
        draw_arrow(x, 9.5, x, 8.8)
    for x in [2, 5.8, 9.6, 13.4]:
        draw_arrow(x, 7.5, x, 6.8)
    for x in [2, 5.8]:
        draw_arrow(x, 5.5, x, 4.8)
    for x in [9.6, 13.4]:
        draw_arrow(x, 5.5, x, 4.8)
    draw_arrow(4, 3.5, 4.5, 2.7)
    draw_arrow(11.75, 3.5, 11, 2.7)

    # Legend
    legend_items = [
        ("★ Extension Points", "#e74c3c"),
        ("Implemented", "#27ae60"),
        ("TODO (Not yet)", "#95a5a6"),
    ]
    for i, (label, color) in enumerate(legend_items):
        ax.add_patch(plt.Rectangle((0.5, 0.2 + i*0.4), 0.4, 0.3, facecolor=color, alpha=0.8))
        ax.text(1.1, 0.35 + i*0.4, label, fontsize=9, va="center")

    plt.tight_layout()
    out = f"{OUT_DIR}/alpha_architecture.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {out}")


def plot_5_improvement_areas(etf_choice, df_norm, models):
    """
    HOW TO FURTHER IMPROVE: Show where the model fails — score distribution overlap,
    missed signals, and single-indicator dominance risk.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Score time series with crash events marked
    ax = axes[0, 0]
    m = models[etf_choice]["reg3"]
    active_inds = [ind for ind in m["weights"] if ind in df_norm.columns]
    score = pd.Series(0.0, index=df_norm.index)
    w_sum = sum(m["weights"][ind] for ind in active_inds)
    for ind in active_inds:
        score += df_norm[ind].fillna(0.0) * m["weights"][ind]
    score = score / w_sum if w_sum > 0 else score

    fwd_ret, worst_dd = compute_forward_targets(df_norm, m["horizon"])
    valid = pd.DataFrame({"score": score, "worst_dd": worst_dd}).dropna()
    crash_events = valid[valid["worst_dd"] <= -0.05].index

    ax.plot(valid.index, valid["score"], linewidth=0.5, alpha=0.6, color=REGIME_COLORS["reg3"])
    ax.axhline(m["threshold"], color="#e67e22", linestyle="--", linewidth=2, label=f"Threshold={m['threshold']:.3f}")
    ax.scatter(crash_events, valid.loc[crash_events, "score"], color="#e74c3c", s=30, zorder=5,
              label=f"Crash events (>{m['horizon']}d, >5% drop)", marker="v")
    ax.set_title(f"Regime 3 Score Time Series — {etf_choice}ETF\nDo crash events cluster above threshold?",
                fontsize=11, fontweight="bold")
    ax.set_ylabel("Alpha Score")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Panel 2: Single-indicator dominance analysis
    ax2 = axes[0, 1]
    dominance_data = {}
    for reg_key in ["reg1", "reg2", "reg3", "reg4"]:
        w = models[etf_choice][reg_key]["weights"]
        max_w = max(w.values())
        max_ind = max(w, key=w.get)
        dominance_data[REGIME_NAMES[reg_key].split(":")[1].strip()] = {
            "max_weight": max_w,
            "max_indicator": max_ind,
            "n_above_20pct": sum(1 for v in w.values() if v > 0.20),
        }

    regimes = list(dominance_data.keys())
    max_weights = [dominance_data[r]["max_weight"] for r in regimes]
    n_active = [dominance_data[r]["n_above_20pct"] for r in regimes]
    colors = ["#e74c3c" if mw > 0.8 else "#f39c12" if mw > 0.5 else "#27ae60" for mw in max_weights]

    bars = ax2.bar(regimes, max_weights, color=colors, width=0.6, alpha=0.8)
    ax2.axhline(0.5, color="#e67e22", linestyle="--", linewidth=1.5, label="50% dominance warning")
    ax2.axhline(0.8, color="#e74c3c", linestyle="--", linewidth=1.5, label="80% single-factor risk")
    for bar, mw, na in zip(bars, max_weights, n_active):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{mw:.0%}\n({na} active)", ha="center", fontsize=9)
    ax2.set_ylabel("Max Single-Indicator Weight", fontsize=11)
    ax2.set_title("Single-Indicator Dominance Risk\nHigh weight = model relies on one factor (fragile)",
                 fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)

    # Panel 3: Missed crashes (false negatives)
    ax3 = axes[1, 0]
    triggered = valid["score"] > m["threshold"]
    missed = valid[(valid["worst_dd"] <= -0.05) & (~triggered)]
    caught = valid[(valid["worst_dd"] <= -0.05) & (triggered)]
    total_crash = len(missed) + len(caught)

    sizes = [len(caught), len(missed)]
    labels_pie = [f"Caught\n({len(caught)})", f"Missed\n({len(missed)})"]
    pie_colors = [REGIME_COLORS["reg3"], "#bdc3c7"]
    if total_crash > 0:
        ax3.pie(sizes, labels=labels_pie, colors=pie_colors, autopct="%1.0f%%",
               startangle=90, textprops={"fontsize": 12})
        ax3.set_title(f"Crash Detection Rate (Regime 3, {etf_choice}ETF)\n"
                     f"Total crash events: {total_crash}",
                     fontsize=11, fontweight="bold")
    else:
        ax3.text(0.5, 0.5, "No crash events found", transform=ax3.transAxes, ha="center", fontsize=14)

    # Panel 4: Improvement roadmap scores
    ax4 = axes[1, 1]
    improvements = [
        "Add volume/money\nflow indicators",
        "Add macro signals\n(credit spread, VIX)",
        "Walk-forward\nvalidation",
        "Regime-aware\nthreshold (dynamic)",
        "Active exit rules\n(TP/SL/time-cut)",
        "Multi-DTE\ncontract selection",
    ]
    # Estimated impact (qualitative based on findings)
    impact = [3.5, 4.0, 4.5, 3.0, 4.0, 3.5]
    difficulty = [2, 4, 3, 2, 3, 4]
    colors_imp = [plt.cm.RdYlGn(i / max(impact)) for i in impact]

    ax4.scatter(difficulty, impact, s=200, c=colors_imp, edgecolors="black", linewidth=1.5, zorder=5)
    for i, (imp, d, label) in enumerate(zip(impact, difficulty, improvements)):
        ax4.annotate(label, (d, imp), textcoords="offset points", xytext=(15, 0),
                    fontsize=8, va="center")
    ax4.set_xlabel("Implementation Difficulty →", fontsize=11)
    ax4.set_ylabel("Estimated Impact →", fontsize=11)
    ax4.set_title("Improvement Roadmap\n(upper-right = highest priority)", fontsize=11, fontweight="bold")
    ax4.grid(True, linestyle="--", alpha=0.5)
    ax4.set_xlim(0, 6)
    ax4.set_ylim(2, 5.5)

    plt.suptitle(f"{etf_choice}ETF — Alpha Model: How to Further Improve",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    out = f"{OUT_DIR}/alpha_improvement_areas_{etf_choice}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {out}")


def plot_6_cross_etf_comparison(models):
    """
    Cross-ETF comparison of model effectiveness.
    """
    etfs = sorted(models.keys())
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Fall regimes — mean return differential
    ax = axes[0]
    x = np.arange(len(etfs))
    width = 0.35
    for i, reg in enumerate(["reg1", "reg2"]):
        diffs = []
        for etf in etfs:
            m = models[etf][reg]
            diffs.append((m["metrics"]["mean_return_triggered"] - m["metrics"]["mean_return_baseline"]) * 100)
        bars = ax.bar(x + i * width, diffs, width, label=REGIME_NAMES[reg], color=REGIME_COLORS[reg], alpha=0.8)
        for bar, val in zip(bars, diffs):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.1 if val < 0 else bar.get_height() + 0.05,
                   f"{val:+.2f}%", ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x + width/2)
    ax.set_xticklabels([f"{e}ETF" for e in etfs])
    ax.set_ylabel("Return Differential (Triggered - Baseline)", fontsize=10)
    ax.set_title("Fall Regimes: Negative = Model Works", fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)

    # Right: Crash regimes — lift
    ax2 = axes[1]
    for i, reg in enumerate(["reg3", "reg4"]):
        lifts = [models[etf][reg]["metrics"]["lift"] for etf in etfs]
        bars = ax2.bar(x + i * width, lifts, width, label=REGIME_NAMES[reg], color=REGIME_COLORS[reg], alpha=0.8)
        for bar, val in zip(bars, lifts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f"{val:.2f}x", ha="center", fontsize=9, fontweight="bold")

    ax2.set_xticks(x + width/2)
    ax2.set_xticklabels([f"{e}ETF" for e in etfs])
    ax2.set_ylabel("Crash Probability Lift", fontsize=10)
    ax2.set_title("Crash Regimes: Higher Lift = Better Prediction", fontsize=12, fontweight="bold")
    ax2.axhline(1, color="#e74c3c", linestyle="--", linewidth=1.5, label="No lift (baseline)")
    ax2.legend(fontsize=9)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)

    plt.suptitle("Cross-ETF Alpha Model Effectiveness Comparison", fontsize=14, fontweight="bold")
    plt.tight_layout()
    out = f"{OUT_DIR}/alpha_cross_etf_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", type=str, default="all",
                       choices=["50", "300", "500", "all"])
    args = parser.parse_args()

    models = load_models()
    etfs = ["50", "300", "500"] if args.etf == "all" else [args.etf]

    # Architecture diagram (ETF-independent)
    print("\n=== Plotting architecture diagram ===")
    plot_4_architecture_diagram()

    # Cross-ETF comparison
    if len(models) >= 2:
        print("\n=== Plotting cross-ETF comparison ===")
        plot_6_cross_etf_comparison(models)

    # Weight importance (all ETFs)
    print("\n=== Plotting weight importance ===")
    plot_3_weight_importance(models)

    for etf_choice in etfs:
        if etf_choice not in models:
            print(f"  SKIP {etf_choice}ETF — no model data in alpha_put_models.json")
            continue

        print(f"\n{'='*60}")
        print(f"  Processing {etf_choice}ETF")
        print(f"{'='*60}")

        select_underlying(etf_choice)
        _, _, etf = load_data()
        model = AlphaModel()
        df_norm = model.compute_normalized_indicators(etf)

        # Plot 1: Score vs Return for each regime
        for reg_key in ["reg1", "reg2", "reg3", "reg4"]:
            print(f"\n  === Score vs Return: {REGIME_NAMES[reg_key]} ===")
            plot_1_score_vs_return(etf_choice, df_norm, models, reg_key)

        # Plot 2: All regimes summary
        print(f"\n  === All Regimes Summary ===")
        plot_2_all_regimes_summary(etf_choice, df_norm, models)

        # Plot 5: Improvement areas
        print(f"\n  === Improvement Areas ===")
        plot_5_improvement_areas(etf_choice, df_norm, models)

    print(f"\n{'='*60}")
    print(f"  ALL DONE — Plots saved to {OUT_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
