"""
Filter Indicator Statistical Validation Report
================================================
Validates whether the technical filters used in backtest_covered_call.py
(RSI, BBU, ROC, SMA50, MACD Hist) are logically sound by analyzing their
predictive power for forward ETF returns over ~1000 trading days per ETF.

Outputs:
  - Console statistical summary table
  - backtest/filter_validation_report.png    (scatter + bin plots)
  - backtest/filter_validation_report_2.png  (bar chart + heatmap + summary table)
"""

import os
import sys
import numpy as np
import pandas as pd
import pandas_ta as ta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy import stats
from itertools import product

# ── Configuration ─────────────────────────────────────────────────────────────
ETF_CONFIG = {
    "300ETF": {"path": "./data/510300_1d.parquet", "color": "#2196F3", "label": "300ETF"},
    "50ETF":  {"path": "./data/50ETF_1d.parquet",  "color": "#FF9800", "label": "50ETF"},
    "500ETF": {"path": "./data/500ETF_1d.parquet", "color": "#4CAF50", "label": "500ETF"},
}

FORWARD_HORIZONS = [5, 10, 20]  # trading days
PRIMARY_HORIZON = 20  # ~1 option cycle

# Filter definitions matching backtest_covered_call.py
# Each filter: (name, function that takes etf DataFrame and returns bool Series)
# The "pass" condition is what the backtest considers a valid entry
FILTER_DEFS = {
    "RSI < 66":       lambda df: df["rsi14"] < 66.0,
    "RSI < 72":       lambda df: df["rsi14"] < 72.0,
    "RSI > 25":       lambda df: df["rsi14"] > 25.0,
    "RSI > 30":       lambda df: df["rsi14"] > 30.0,
    "RSI > 35":       lambda df: df["rsi14"] > 35.0,
    "Close < BBU":    lambda df: df["close"] < df["bbu20"],
    "Close < BBU+0.5*ATR": lambda df: df["close"] < (df["bbu20"] + 0.5 * df["atr20"]),
    "Close > SMA50":  lambda df: df["close"] > df["sma50"],
    "ROC10 < 3%":     lambda df: df["roc10"] < 3.0,
    "ROC10 < 7%":     lambda df: df["roc10"] < 7.0,
    "ROC20 < 3%":     lambda df: df["roc20"] < 3.0,
    "ROC20 < 4%":     lambda df: df["roc20"] < 4.0,
    "MACD Hist < 0":  lambda df: df["macd_hist"] < 0.0,
    "Vol20 < Med":    lambda df: df["vol20"] < df["vol20_median"],
}

# RSI binning for scatter analysis
RSI_BINS = [0, 30, 40, 50, 60, 70, 80, 100]
RSI_LABELS = ["<30", "30-40", "40-50", "50-60", "60-70", "70-80", ">80"]

# ── Data Loading & Indicator Computation ──────────────────────────────────────
def load_etf(path):
    """Load ETF daily data and compute indicators identical to backtest_covered_call.py."""
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # Indicators (same as backtest_covered_call.py lines 156-178)
    df["rsi14"] = ta.rsi(df["close"], length=14)
    df["sma20"] = ta.sma(df["close"], length=20)
    df["sma50"] = ta.sma(df["close"], length=50)
    df["atr20"] = ta.atr(df["high"], df["low"], df["close"], length=20)
    df["roc10"] = ta.roc(df["close"], length=10)
    df["roc20"] = ta.roc(df["close"], length=20)

    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None:
        df["bbu20"] = bb["BBU_20_2.0_2.0"]
        df["bbl20"] = bb["BBL_20_2.0_2.0"]
    else:
        df["bbu20"] = np.nan
        df["bbl20"] = np.nan

    df["vol20"] = df["close"].pct_change().rolling(20).std() * np.sqrt(252)
    df["vol20_median"] = df["vol20"].rolling(252).median()
    macd = ta.macd(df["close"])
    df["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan

    # Forward returns
    for h in FORWARD_HORIZONS:
        df[f"fwd_ret_{h}d"] = df["close"].shift(-h) / df["close"] - 1.0

    # BBU proximity (normalized by ATR)
    df["bbu_prox"] = (df["close"] - df["bbu20"]) / df["atr20"]

    return df


# ── Statistical Analysis ──────────────────────────────────────────────────────
def cohens_d(x, y):
    """Compute Cohen's d effect size."""
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = x.var(ddof=1), y.var(ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (x.mean() - y.mean()) / pooled_std


def analyze_filter(etf_df, filter_fn, horizon=PRIMARY_HORIZON):
    """Analyze a single filter's predictive power for forward returns."""
    ret_col = f"fwd_ret_{horizon}d"
    mask_valid = etf_df[ret_col].notna() & etf_df["rsi14"].notna()

    try:
        pass_mask = filter_fn(etf_df) & mask_valid
    except Exception:
        pass_mask = pd.Series(False, index=etf_df.index)
        pass_mask = pass_mask & mask_valid

    fail_mask = (~pass_mask) & mask_valid

    pass_rets = etf_df.loc[pass_mask, ret_col]
    fail_rets = etf_df.loc[fail_mask, ret_col]

    n_total = mask_valid.sum()
    n_pass = pass_mask.sum()
    placement = n_pass / n_total if n_total > 0 else 0

    if len(pass_rets) < 3 or len(fail_rets) < 3:
        return None

    # Statistical tests
    t_stat, p_ttest = stats.ttest_ind(pass_rets, fail_rets, equal_var=False)
    u_stat, p_mannwhitney = stats.mannwhitneyu(pass_rets, fail_rets, alternative='two-sided')
    d = cohens_d(pass_rets, fail_rets)

    return {
        "n_total": n_total,
        "n_pass": n_pass,
        "n_fail": len(fail_rets),
        "placement": placement,
        "pass_mean": pass_rets.mean(),
        "pass_median": pass_rets.median(),
        "pass_std": pass_rets.std(),
        "pass_winrate": (pass_rets > 0).mean(),
        "fail_mean": fail_rets.mean(),
        "fail_median": fail_rets.median(),
        "fail_std": fail_rets.std(),
        "fail_winrate": (fail_rets > 0).mean(),
        "t_stat": t_stat,
        "p_ttest": p_ttest,
        "p_mannwhitney": p_mannwhitney,
        "cohens_d": d,
        "pass_rets": pass_rets,
        "fail_rets": fail_rets,
    }


def verdict_str(p_val, d_val):
    """Classify filter as SOUND / MARGINAL / UNSOUND."""
    if p_val < 0.05 and abs(d_val) >= 0.1:
        return "SIGNIFICANT"
    elif p_val < 0.10:
        return "MARGINAL"
    else:
        return "NOT SIGNIFICANT"


# ── Console Report ────────────────────────────────────────────────────────────
def print_report(all_results):
    """Print structured console summary."""
    print("\n" + "=" * 110)
    print("  FILTER VALIDATION REPORT — Statistical Analysis of Technical Indicators")
    print("=" * 110)

    for horizon in FORWARD_HORIZONS:
        print(f"\n  Forward Return Horizon: {horizon} trading days")
        print("  " + "-" * 106)

        for etf_name, filters in all_results.items():
            cfg = ETF_CONFIG[etf_name]
            n = None
            for fname, res in filters.items():
                if horizon in res and res[horizon] is not None:
                    n = res[horizon]["n_total"]
                    break
            if n is None:
                continue

            print(f"\n  --- {etf_name} (N={n} trading days) ---")
            print(f"  {'Filter':<24} | {'Place%':>7} | {'Pass Avg':>9} | {'Fail Avg':>9} | "
                  f"{'p(t-test)':>9} | {'p(M-W)':>9} | {'Cohen d':>8} | {'Verdict'}")
            print("  " + "-" * 106)

            for fname, res in filters.items():
                if horizon not in res or res[horizon] is None:
                    continue
                r = res[horizon]
                v = verdict_str(r["p_ttest"], r["cohens_d"])
                print(f"  {fname:<24} | {r['placement']:>6.1%} | "
                      f"{r['pass_mean']:>+8.3%} | {r['fail_mean']:>+8.3%} | "
                      f"{r['p_ttest']:>9.4f} | {r['p_mannwhitney']:>9.4f} | "
                      f"{r['cohens_d']:>+7.3f}  | {v}")

    print("\n" + "=" * 110)
    print("  Interpretation Guide:")
    print("    SIGNIFICANT:    p < 0.05 and |Cohen's d| >= 0.10 — statistically reliable difference")
    print("    MARGINAL:       p < 0.10 — suggestive but not conclusive")
    print("    NOT SIGNIFICANT: p >= 0.10 — no reliable evidence the filter separates returns")
    print("    Cohen's d:  0.1=small, 0.3=medium, 0.5=large effect size")
    print("    Positive d: filter-pass days have HIGHER forward returns than fail days")
    print("    Negative d: filter-pass days have LOWER forward returns than fail days")
    print("=" * 110 + "\n")


# ── Figure 1: Scatter + Bin Plots ─────────────────────────────────────────────
def plot_report_1(etf_data, all_results):
    """3x3 grid: RSI / BBU proximity / ROC10 vs forward return, one column per ETF."""
    etf_names = list(ETF_CONFIG.keys())
    fig, axes = plt.subplots(3, 3, figsize=(20, 16))
    fig.suptitle("Filter Indicator Validation: Indicator Value vs 20-Day Forward ETF Return",
                 fontsize=16, fontweight="bold", y=0.98)

    indicators = [
        ("rsi14", "RSI(14)", RSI_BINS, RSI_LABELS,
         [(30, "#E53935", "RSI<30\n(oversold)"), (60, "#FFB300", "RSI 60"),
          (66, "#FF8F00", "RSI 66"), (70, "#E53935", "RSI>70\n(overbought)")]),
        ("bbu_prox", "(Close - BBU) / ATR", [-4, -2, -1, -0.5, 0, 0.5, 1, 2, 4],
         ["<-2", "-2~-1", "-1~-0.5", "-0.5~0", "0~0.5", "0.5~1", ">1"],
         [(0, "#E53935", "Close=BBU\n(threshold)")]),
        ("roc10", "ROC(10) %", [-10, -5, -3, 0, 3, 5, 7, 10, 15],
         ["<-5", "-5~-3", "-3~0", "0~3", "3~5", "5~7", ">7"],
         [(3, "#FFB300", "ROC=3%"), (7, "#E53935", "ROC=7%")]),
    ]

    for row, (col_name, title, bins, labels, vlines) in enumerate(indicators):
        for col_idx, etf_name in enumerate(etf_names):
            ax = axes[row][col_idx]
            df = etf_data[etf_name]
            ret_col = f"fwd_ret_{PRIMARY_HORIZON}d"

            valid = df[[col_name, ret_col]].dropna()
            if valid.empty:
                continue

            x = valid[col_name].values
            y = valid[ret_col].values * 100  # percent

            # Scatter with alpha
            color = ETF_CONFIG[etf_name]["color"]
            ax.scatter(x, y, alpha=0.15, s=8, color=color, edgecolors="none")

            # Bin statistics with boxplot-style bars
            if col_name == "bbu_prox":
                bin_edges = bins
            else:
                bin_edges = bins
            bin_indices = np.digitize(x, bin_edges[1:-1])  # 0 to len-2
            bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges) - 1)]

            for bi, bc in enumerate(bin_centers):
                mask = bin_indices == bi
                if mask.sum() < 5:
                    continue
                bin_y = y[mask]
                mean_y = bin_y.mean()
                ci95 = 1.96 * bin_y.std() / np.sqrt(len(bin_y))
                ax.errorbar(bc, mean_y, yerr=ci95, fmt='o', color='black',
                           markersize=6, capsize=4, capthick=2, elinewidth=2, zorder=5)

            # Vertical threshold lines
            for vpos, vcolor, vlabel in vlines:
                ax.axvline(vpos, color=vcolor, linestyle="--", linewidth=1.2, alpha=0.7)
                # Place label at top
                ax.text(vpos, ax.get_ylim()[1] * 0.95, vlabel, fontsize=7,
                       color=vcolor, ha="center", va="top", fontweight="bold",
                       bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor=vcolor))

            # Zero line
            ax.axhline(0, color="gray", linewidth=0.5, linestyle="-", alpha=0.5)

            ax.set_xlabel(title, fontsize=10, fontweight="bold")
            if col_idx == 0:
                ax.set_ylabel(f"{PRIMARY_HORIZON}-Day Forward Return (%)", fontsize=10, fontweight="bold")
            if row == 0:
                ax.set_title(ETF_CONFIG[etf_name]["label"], fontsize=13, fontweight="bold")

            ax.grid(True, linestyle=":", alpha=0.4)
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f%%'))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_path = os.path.join("backtest", "filter_validation_report.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[SAVED] {out_path}")
    plt.close(fig)


# ── Figure 2: Bar Chart + Heatmap + Summary Table ─────────────────────────────
def plot_report_2(etf_data, all_results):
    """Bar chart of mean forward return by filter + significance heatmap + summary table."""
    etf_names = list(ETF_CONFIG.keys())
    fig = plt.figure(figsize=(22, 18))

    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1, 1.2], hspace=0.35, wspace=0.3,
                          left=0.08, right=0.95, top=0.95, bottom=0.05)

    # ── Top: Bar chart (mean fwd return pass vs fail, per filter, grouped by ETF) ──
    ax_bar = fig.add_subplot(gs[0, :])
    filters_to_show = list(FILTER_DEFS.keys())
    n_filters = len(filters_to_show)
    n_etfs = len(etf_names)
    bar_w = 0.25
    x_pos = np.arange(n_filters)

    for etf_idx, etf_name in enumerate(etf_names):
        pass_means = []
        fail_means = []
        pass_cis = []
        fail_cis = []
        for fname in filters_to_show:
            res = all_results[etf_name].get(fname, {}).get(PRIMARY_HORIZON)
            if res is None:
                pass_means.append(0)
                fail_means.append(0)
                pass_cis.append(0)
                fail_cis.append(0)
            else:
                pass_means.append(res["pass_mean"] * 100)
                fail_means.append(res["fail_mean"] * 100)
                n_p = max(len(res["pass_rets"]), 1)
                n_f = max(len(res["fail_rets"]), 1)
                pass_cis.append(1.96 * res["pass_std"] / np.sqrt(n_p) * 100)
                fail_cis.append(1.96 * res["fail_std"] / np.sqrt(n_f) * 100)

        offset = (etf_idx - 1) * bar_w
        color = ETF_CONFIG[etf_name]["color"]
        ax_bar.bar(x_pos + offset - bar_w/2, pass_means, bar_w * 0.9,
                   yerr=pass_cis, capsize=3, color=color, alpha=0.7,
                   label=f"{etf_name} Pass", edgecolor="white", linewidth=0.5)
        ax_bar.bar(x_pos + offset + bar_w/2, fail_means, bar_w * 0.9,
                   yerr=fail_cis, capsize=3, color=color, alpha=0.35, hatch="//",
                   label=f"{etf_name} Fail", edgecolor="white", linewidth=0.5)

    ax_bar.axhline(0, color="black", linewidth=0.8)
    ax_bar.set_xticks(x_pos)
    ax_bar.set_xticklabels(filters_to_show, rotation=35, ha="right", fontsize=8)
    ax_bar.set_ylabel("Mean 20-Day Forward Return (%)", fontsize=11, fontweight="bold")
    ax_bar.set_title("Filter Pass vs Fail: Mean Forward Return with 95% CI", fontsize=14, fontweight="bold")
    ax_bar.legend(loc="upper right", fontsize=7, ncol=3, framealpha=0.9)
    ax_bar.grid(True, axis="y", linestyle=":", alpha=0.4)
    ax_bar.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f%%'))

    # ── Middle-left: Heatmap (p-values) ──
    ax_heat = fig.add_subplot(gs[1, 0])
    heat_filters = [f for f in filters_to_show if any(
        all_results[e].get(f, {}).get(PRIMARY_HORIZON) is not None for e in etf_names)]
    heat_data = np.full((len(heat_filters), n_etfs), np.nan)
    for fi, fname in enumerate(heat_filters):
        for ei, etf_name in enumerate(etf_names):
            res = all_results[etf_name].get(fname, {}).get(PRIMARY_HORIZON)
            if res is not None:
                heat_data[fi, ei] = res["p_ttest"]

    cmap = plt.cm.RdYlGn_r  # red=low p (significant), green=high p
    im = ax_heat.imshow(heat_data, cmap=cmap, aspect="auto", vmin=0, vmax=0.15)
    ax_heat.set_xticks(range(n_etfs))
    ax_heat.set_xticklabels(etf_names, fontsize=10, fontweight="bold")
    ax_heat.set_yticks(range(len(heat_filters)))
    ax_heat.set_yticklabels(heat_filters, fontsize=8)
    ax_heat.set_title("Statistical Significance Heatmap\n(Welch's t-test p-value)", fontsize=12, fontweight="bold")

    # Annotate cells
    for fi in range(len(heat_filters)):
        for ei in range(n_etfs):
            val = heat_data[fi, ei]
            if not np.isnan(val):
                txt_color = "white" if val < 0.05 else "black"
                marker = "***" if val < 0.01 else "**" if val < 0.05 else "*" if val < 0.10 else ""
                ax_heat.text(ei, fi, f"{val:.3f}{marker}", ha="center", va="center",
                            fontsize=7, color=txt_color, fontweight="bold")

    plt.colorbar(im, ax=ax_heat, shrink=0.8, label="p-value")

    # ── Middle-right: Cohen's d heatmap ──
    ax_d = fig.add_subplot(gs[1, 1])
    d_data = np.full((len(heat_filters), n_etfs), np.nan)
    for fi, fname in enumerate(heat_filters):
        for ei, etf_name in enumerate(etf_names):
            res = all_results[etf_name].get(fname, {}).get(PRIMARY_HORIZON)
            if res is not None:
                d_data[fi, ei] = res["cohens_d"]

    max_abs_d = max(0.5, np.nanmax(np.abs(d_data)))
    im2 = ax_d.imshow(d_data, cmap="RdBu_r", aspect="auto", vmin=-max_abs_d, vmax=max_abs_d)
    ax_d.set_xticks(range(n_etfs))
    ax_d.set_xticklabels(etf_names, fontsize=10, fontweight="bold")
    ax_d.set_yticks(range(len(heat_filters)))
    ax_d.set_yticklabels(heat_filters, fontsize=8)
    ax_d.set_title("Effect Size Heatmap\n(Cohen's d: + = pass > fail)", fontsize=12, fontweight="bold")

    for fi in range(len(heat_filters)):
        for ei in range(n_etfs):
            val = d_data[fi, ei]
            if not np.isnan(val):
                txt_color = "white" if abs(val) > 0.3 else "black"
                size_label = "L" if abs(val) >= 0.5 else "M" if abs(val) >= 0.3 else "S" if abs(val) >= 0.1 else "~"
                ax_d.text(ei, fi, f"{val:+.3f}\n({size_label})", ha="center", va="center",
                         fontsize=6.5, color=txt_color, fontweight="bold")

    plt.colorbar(im2, ax=ax_d, shrink=0.8, label="Cohen's d")

    # ── Bottom: Summary Table ──
    ax_tbl = fig.add_subplot(gs[2, :])
    ax_tbl.axis("off")
    ax_tbl.set_title("Comprehensive Filter Summary (20-Day Forward Return)", fontsize=13, fontweight="bold", pad=10)

    # Build table data — pick the most relevant filters per ETF based on backtest usage
    key_filters = {
        "300ETF": ["RSI < 66", "RSI > 25", "Close < BBU+0.5*ATR", "ROC10 < 7%", "MACD Hist < 0",
                    "RSI < 72", "ROC20 < 4%"],
        "50ETF":  ["RSI < 60", "RSI > 30", "ROC10 < 3%", "Vol20 < Med",
                    "Close < BBU", "ROC20 < 3%"],
        "500ETF": ["RSI > 30", "RSI > 35", "Close < BBU", "Close > SMA50",
                    "ROC20 < 4%"],
    }

    table_rows = []
    for etf_name in etf_names:
        for fname in key_filters.get(etf_name, []):
            res = all_results[etf_name].get(fname, {}).get(PRIMARY_HORIZON)
            if res is None:
                continue
            v = verdict_str(res["p_ttest"], res["cohens_d"])
            direction = "pass>fail" if res["cohens_d"] > 0 else "pass<fail"
            table_rows.append([
                etf_name, fname,
                f"{res['placement']:.1%}",
                f"{res['pass_mean']:+.3%}",
                f"{res['fail_mean']:+.3%}",
                f"{res['pass_mean'] - res['fail_mean']:+.3%}",
                f"{res['p_ttest']:.4f}",
                f"{res['cohens_d']:+.3f}",
                direction,
                v,
            ])

    col_labels = ["ETF", "Filter", "Placement", "Pass Avg", "Fail Avg", "Diff",
                  "p-value", "Cohen's d", "Direction", "Verdict"]

    if table_rows:
        tbl = ax_tbl.table(cellText=table_rows, colLabels=col_labels,
                          loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1, 1.5)

        # Color-code verdict cells
        for i, row in enumerate(table_rows):
            verdict = row[-1]
            cell = tbl[(i + 1, len(col_labels) - 1)]
            if verdict == "SIGNIFICANT":
                cell.set_facecolor("#C8E6C9")  # light green
            elif verdict == "MARGINAL":
                cell.set_facecolor("#FFF9C4")  # light yellow
            else:
                cell.set_facecolor("#FFCDD2")  # light red

            # Color p-value cell
            p_cell = tbl[(i + 1, 6)]
            p_val = float(row[6])
            if p_val < 0.05:
                p_cell.set_facecolor("#C8E6C9")
            elif p_val < 0.10:
                p_cell.set_facecolor("#FFF9C4")
            else:
                p_cell.set_facecolor("#FFCDD2")

    fig.suptitle("Filter Indicator Validation Report — Statistical Evidence",
                 fontsize=16, fontweight="bold", y=0.99)
    out_path = os.path.join("backtest", "filter_validation_report_2.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[SAVED] {out_path}")
    plt.close(fig)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n=== Loading ETF Data ===")
    etf_data = {}
    for etf_name, cfg in ETF_CONFIG.items():
        if not os.path.exists(cfg["path"]):
            print(f"  [WARN] {cfg['path']} not found, skipping {etf_name}")
            continue
        df = load_etf(cfg["path"])
        etf_data[etf_name] = df
        print(f"  {etf_name}: {len(df)} trading days "
              f"({df.index[0].date()} to {df.index[-1].date()})")

    if not etf_data:
        print("ERROR: No ETF data loaded. Exiting.")
        sys.exit(1)

    # Run analysis for all filters, all ETFs, all horizons
    print("\n=== Running Statistical Analysis ===")
    all_results = {}
    for etf_name, df in etf_data.items():
        all_results[etf_name] = {}
        for fname, ffn in FILTER_DEFS.items():
            all_results[etf_name][fname] = {}
            for h in FORWARD_HORIZONS:
                res = analyze_filter(df, ffn, horizon=h)
                all_results[etf_name][fname][h] = res

    # Console report
    print_report(all_results)

    # Generate plots
    print("=== Generating Report Charts ===")
    os.makedirs("backtest", exist_ok=True)
    plot_report_1(etf_data, all_results)
    plot_report_2(etf_data, all_results)

    print("\n=== Done ===")
    print("Reports saved to:")
    print("  backtest/filter_validation_report.png   (scatter + bin plots)")
    print("  backtest/filter_validation_report_2.png (bar chart + heatmap + table)")


if __name__ == "__main__":
    main()
