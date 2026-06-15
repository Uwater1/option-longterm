"""
Filter Indicator Statistical Validation Report
================================================
Validates whether the technical filters used in backtest_covered_call.py
(RSI, BBU, ROC, SMA50, MACD Hist) are logically sound by analyzing their
predictive power for forward ETF returns over ~1000 trading days per ETF.

Outputs:
  - Console statistical summary table
  - validate/filter_validation_report.png    (scatter + bin plots)
  - validate/filter_validation_report_2.png  (bar chart + heatmap + summary table)
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

FORWARD_HORIZONS = [7, 14, 30]  # calendar days
PRIMARY_HORIZON = 30  # ~1 option cycle (30 calendar days)

# Filter definitions matching backtest_covered_call.py
# Each filter: (name, function that takes etf DataFrame and returns bool Series)
# The "pass" condition is what the backtest considers a valid entry
FILTER_DEFS = {
    # ── Call-side filters (used in CallStrategy) ──
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
    # ── Put-side filters (used in PutStrategy — selective hedge) ──
    "RSI < 55":       lambda df: df["rsi14"] < 55.0,
    "RSI < 60":       lambda df: df["rsi14"] < 60.0,
    "Vol20 > Med":    lambda df: df["vol20"] > df["vol20_median"],
    "Close < SMA50":  lambda df: df["close"] < df["sma50"],
}

# ── Put Strategy Combined Filters (per-ETF, from optimize_put_filters.py) ──
PUT_FILTER_DEFS = {
    "300ETF": {
        "RSI<60 & Vol20>Med": lambda df: (df["rsi14"] < 60.0) & (df["vol20"] > df["vol20_median"]),
    },
    "50ETF": {
        "RSI<55 & Close<SMA50": lambda df: (df["rsi14"] < 55.0) & (df["close"] < df["sma50"]),
    },
    "500ETF": {
        "RSI<55 & Vol20>Med": lambda df: (df["rsi14"] < 55.0) & (df["vol20"] > df["vol20_median"]),
    },
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

    # Forward returns (calendar days)
    dates = df.index.values
    closes = df["close"].values
    for h in FORWARD_HORIZONS:
        fwd_rets = np.full(len(df), np.nan)
        for i, dt in enumerate(dates):
            target_dt = dt + np.timedelta64(h, 'D')
            idx = np.searchsorted(dates, target_dt)
            if idx < len(dates):
                fwd_rets[i] = closes[idx] / closes[i] - 1.0
        df[f"fwd_ret_{h}d"] = fwd_rets

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
        print(f"\n  Forward Return Horizon: {horizon} calendar days")
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
    fig, axes = plt.subplots(3, 3, figsize=(20, 16), facecolor="#F8F9FA")
    fig.suptitle(f"Filter Indicator Validation: Indicator Value vs {PRIMARY_HORIZON}-Calendar-Day Forward ETF Return",
                 fontsize=16, fontweight="bold", y=0.98, color="#1D2939")

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

            ax.set_facecolor("#FFFFFF")
            color = ETF_CONFIG[etf_name]["color"]
            ax.scatter(x, y, alpha=0.35, s=16, color=color, edgecolors="white", linewidth=0.3, label="Daily Obs")

            # Fit 2nd-degree polynomial trend line
            try:
                poly_mask = np.isfinite(x) & np.isfinite(y)
                if poly_mask.sum() > 10:
                    x_poly = x[poly_mask]
                    y_poly = y[poly_mask]
                    coefs = np.polyfit(x_poly, y_poly, 2)
                    p_fn = np.poly1d(coefs)
                    x_grid = np.linspace(x_poly.min(), x_poly.max(), 100)
                    ax.plot(x_grid, p_fn(x_grid), color="#E53935", linestyle="-", linewidth=2.0, label="Trend (Poly d2)", zorder=6)
            except Exception:
                pass

            # Bin statistics with boxplot-style bars
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
                           markersize=5, capsize=3, capthick=1.5, elinewidth=1.5, zorder=5)

            # Vertical threshold lines
            for vpos, vcolor, vlabel in vlines:
                ax.axvline(vpos, color=vcolor, linestyle="--", linewidth=1.2, alpha=0.7)
                ax.text(vpos, ax.get_ylim()[1] * 0.92, vlabel, fontsize=7,
                       color=vcolor, ha="center", va="top", fontweight="bold",
                       bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85, edgecolor=vcolor))

            # Zero line
            ax.axhline(0, color="gray", linewidth=0.5, linestyle="-", alpha=0.5)

            ax.set_xlabel(title, fontsize=10, fontweight="bold", color="#344054")
            if col_idx == 0:
                ax.set_ylabel(f"{PRIMARY_HORIZON}-Calendar-Day Return (%)", fontsize=10, fontweight="bold", color="#344054")
            if row == 0:
                ax.set_title(ETF_CONFIG[etf_name]["label"], fontsize=13, fontweight="bold", color="#1D2939")

            # Clean borders and grid
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#D0D5DD')
            ax.spines['bottom'].set_color('#D0D5DD')
            ax.grid(True, linestyle="--", linewidth=0.5, color="#E4E7EC")
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f%%'))
            if row == 0 and col_idx == 0:
                ax.legend(loc="lower left", fontsize=8, framealpha=0.9)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_path = os.path.join("validate", "filter_validation_report.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[SAVED] {out_path}")
    plt.close(fig)


# ── Figure 2: Bar Chart + Heatmap + Summary Table ─────────────────────────────
def plot_report_2(etf_data, all_results):
    """Bar chart of mean forward return by filter + significance heatmap + summary table + explanation."""
    etf_names = list(ETF_CONFIG.keys())
    fig = plt.figure(figsize=(22, 22), facecolor="#F8F9FA")

    gs = fig.add_gridspec(4, 2, height_ratios=[1.2, 1.0, 1.2, 0.4], hspace=0.38, wspace=0.3,
                          left=0.08, right=0.95, top=0.95, bottom=0.03)

    # ── Top: Bar chart (mean fwd return pass vs fail, per filter, grouped by ETF) ──
    ax_bar = fig.add_subplot(gs[0, :])
    ax_bar.set_facecolor("#FFFFFF")
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
                   yerr=pass_cis, capsize=3, color=color, alpha=0.75,
                   label=f"{etf_name} Pass", edgecolor="white", linewidth=0.5)
        ax_bar.bar(x_pos + offset + bar_w/2, fail_means, bar_w * 0.9,
                   yerr=fail_cis, capsize=3, color=color, alpha=0.35, hatch="//",
                   label=f"{etf_name} Fail", edgecolor="white", linewidth=0.5)

    ax_bar.axhline(0, color="black", linewidth=0.8)
    ax_bar.set_xticks(x_pos)
    ax_bar.set_xticklabels(filters_to_show, rotation=30, ha="right", fontsize=9, fontweight="bold", color="#344054")
    ax_bar.set_ylabel(f"Mean {PRIMARY_HORIZON}-Calendar-Day Return (%)", fontsize=11, fontweight="bold", color="#344054")
    ax_bar.set_title(f"Filter Pass vs Fail: Mean {PRIMARY_HORIZON}-Calendar-Day Forward Return with 95% Confidence Interval", fontsize=14, fontweight="bold", color="#1D2939")
    ax_bar.legend(loc="upper right", fontsize=8, ncol=3, framealpha=0.9)
    ax_bar.grid(True, axis="y", linestyle="--", linewidth=0.5, color="#E4E7EC")
    ax_bar.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f%%'))
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    ax_bar.spines['left'].set_color('#D0D5DD')
    ax_bar.spines['bottom'].set_color('#D0D5DD')

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

    # Use Blues_r colormap for intuitive interpretation (darker blue = lower p-value / more significant)
    im = ax_heat.imshow(heat_data, cmap=plt.cm.Blues_r, aspect="auto", vmin=0, vmax=0.10)
    ax_heat.set_xticks(range(n_etfs))
    ax_heat.set_xticklabels(etf_names, fontsize=10, fontweight="bold", color="#344054")
    ax_heat.set_yticks(range(len(heat_filters)))
    ax_heat.set_yticklabels(heat_filters, fontsize=9, fontweight="bold", color="#344054")
    ax_heat.set_title("Statistical Significance Heatmap\n(Welch's t-test p-value, Dark Blue = More Significant)", fontsize=12, fontweight="bold", color="#1D2939")

    # Annotate cells
    for fi in range(len(heat_filters)):
        for ei in range(n_etfs):
            val = heat_data[fi, ei]
            if not np.isnan(val):
                txt_color = "white" if val < 0.05 else "black"
                marker = "***" if val < 0.01 else "**" if val < 0.05 else "*" if val < 0.10 else ""
                ax_heat.text(ei, fi, f"{val:.3f}{marker}", ha="center", va="center",
                            fontsize=8, color=txt_color, fontweight="bold")

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
    ax_d.set_xticklabels(etf_names, fontsize=10, fontweight="bold", color="#344054")
    ax_d.set_yticks(range(len(heat_filters)))
    ax_d.set_yticklabels(heat_filters, fontsize=9, fontweight="bold", color="#344054")
    ax_d.set_title("Effect Size Heatmap\n(Cohen's d: Blue = Pass > Fail, Red = Pass < Fail)", fontsize=12, fontweight="bold", color="#1D2939")

    for fi in range(len(heat_filters)):
        for ei in range(n_etfs):
            val = d_data[fi, ei]
            if not np.isnan(val):
                txt_color = "white" if abs(val) > 0.3 else "black"
                size_label = "L" if abs(val) >= 0.5 else "M" if abs(val) >= 0.3 else "S" if abs(val) >= 0.1 else "~"
                ax_d.text(ei, fi, f"{val:+.3f}\n({size_label})", ha="center", va="center",
                         fontsize=7.5, color=txt_color, fontweight="bold")

    plt.colorbar(im2, ax=ax_d, shrink=0.8, label="Cohen's d")

    # ── Bottom: Summary Table ──
    ax_tbl = fig.add_subplot(gs[2, :])
    ax_tbl.axis("off")
    ax_tbl.set_title(f"Comprehensive Filter Summary ({PRIMARY_HORIZON}-Calendar-Day Forward Return)", fontsize=13, fontweight="bold", color="#1D2939", pad=10)

    # Build table data — pick the most relevant filters per ETF based on backtest usage
    key_filters = {
        "300ETF": ["RSI < 66", "RSI > 25", "Close < BBU+0.5*ATR", "ROC10 < 7%", "MACD Hist < 0",
                    "RSI < 72", "ROC20 < 4%",
                    "RSI < 60", "Vol20 > Med"],
        "50ETF":  ["RSI < 60", "RSI > 30", "ROC10 < 3%", "Vol20 < Med",
                    "Close < BBU", "ROC20 < 3%",
                    "RSI < 55", "Close < SMA50"],
        "500ETF": ["RSI > 30", "RSI > 35", "Close < BBU", "Close > SMA50",
                    "ROC20 < 4%",
                    "RSI < 55", "Vol20 > Med"],
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
        tbl.set_fontsize(8.5)
        tbl.scale(1, 1.5)

        # Color-code cells
        for i, row in enumerate(table_rows):
            verdict = row[-1]
            cell = tbl[(i + 1, len(col_labels) - 1)]
            if verdict == "SIGNIFICANT":
                cell.set_facecolor("#E2F0D9")  # soft light green
            elif verdict == "MARGINAL":
                cell.set_facecolor("#FFF2CC")  # soft light yellow
            else:
                cell.set_facecolor("#F2F2F2")  # soft light grey

            p_cell = tbl[(i + 1, 6)]
            p_val = float(row[6])
            if p_val < 0.05:
                p_cell.set_facecolor("#E2F0D9")
            elif p_val < 0.10:
                p_cell.set_facecolor("#FFF2CC")
            else:
                p_cell.set_facecolor("#F2F2F2")

    # ── Executive Summary & Interpretation Guide (Bottom panel) ──
    ax_exp = fig.add_subplot(gs[3, :])
    ax_exp.axis("off")
    
    explanation_text = (
        "EXECUTIVE SUMMARY & STATISTICAL INTERPRETATION GUIDE\n"
        "• Cohen's d: Standardized effect size. Indicates how many standard deviations separate the 'Pass' and 'Fail' day returns.\n"
        "  - Positive d: Filtering conditions associated with HIGHER forward returns (good for long/trend entry).\n"
        "  - Negative d: Filtering conditions associated with LOWER forward returns (supports RSI/BBU cap to avoid overbought assignments).\n"
        "  - Effect Size Guide: |d| >= 0.1 is small (S), |d| >= 0.3 is medium (M), |d| >= 0.5 is large (L).\n"
        "• p-value: Welch's t-test significance. p < 0.05 is significant.\n"
        "• Call Strategy Validation:\n"
        "  - 300ETF/500ETF: RSI and BBU ceiling filters show significant NEGATIVE d — overbought days have lower fwd returns, validating call OTM switching.\n"
        "  - 50ETF: Vol20 < Med and RSI range filters validate bull-trend entry conditions.\n"
        "• Put Strategy Validation (Selective Hedge):\n"
        "  - Put filters seek NEGATIVE fwd returns (market drops) so NEGATIVE d means the hedge timing is effective.\n"
        "  - 300ETF: RSI<60 & Vol20>Med targets high-volatility weakness periods.\n"
        "  - 50ETF: RSI<55 & Close<SMA50 targets below-trend weakness.\n"
        "  - 500ETF: RSI<55 & Vol20>Med targets elevated-vol sell-offs."
    )
    
    ax_exp.text(0.005, 0.95, explanation_text, fontsize=9.5, va="top", ha="left",
                fontproperties="monospace",
                bbox=dict(boxstyle="round,pad=0.8", facecolor="#FFFFFF", edgecolor="#D0D5DD", alpha=0.9))

    fig.suptitle(f"Filter Indicator Validation Report — {PRIMARY_HORIZON}-Calendar-Day Forward Return",
                 fontsize=16, fontweight="bold", y=0.99, color="#1D2939")
    out_path = os.path.join("validate", "filter_validation_report_2.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[SAVED] {out_path}")
    plt.close(fig)


def generate_markdown_report(all_results, put_results, out_md_path="validate/filter_validation_report.md"):
    """Generate markdown report with embedded charts and statistical results.
    
    all_results: dict[etf_name][filter_name][horizon] for individual call/put filters
    put_results: dict[etf_name][combined_filter_name][horizon] for per-ETF combined put strategy filters
    """
    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("# Filter Indicator Statistical Validation Report\n\n")
        f.write(f"Generated on: `{now_str}`  \n")
        f.write(f"Primary Horizon: `{PRIMARY_HORIZON}` calendar days  \n")
        f.write(f"Horizons: `{[f'{h}d' for h in FORWARD_HORIZONS]}`  \n\n")

        f.write("> [!NOTE]\n")
        f.write("> Validates technical indicators used in both the **Call Strategy** (`backtest_covered_call.py`) ")
        f.write("and the **Put Strategy** (`backtest_put.py`) ")
        f.write("(RSI, BBU, ROC, SMA50, MACD Hist, Vol20 regime) against forward ETF returns. ")
        f.write("Determines if filter conditions have statistical edge.\n\n")

        f.write("## Visualizations\n\n")
        f.write("### Figure 1: Indicator Value vs 30-Calendar-Day Forward Return Scatter & Bin Plots\n")
        f.write("![Scatter & Bin Plots](filter_validation_report.png)\n\n")
        f.write("### Figure 2: Filter Pass/Fail Bar Chart, Significance Heatmap, and Summary Table\n")
        f.write("![Bar Chart + Heatmap + Table](filter_validation_report_2.png)\n\n")

        f.write("## Interpretation Guide\n\n")
        f.write("- **Cohen's d (Effect Size)**: Standard deviation difference between Pass and Fail returns.\n")
        f.write("  - Positive: Filter-pass has higher forward returns (good for trend entry checks).\n")
        f.write("  - Negative: Filter-pass has lower forward returns (supports RSI/BBU cap to avoid overbought assignments).\n")
        f.write("  - Size: 0.1 = small, 0.3 = medium, 0.5 = large.\n")
        f.write("- **p-value**: Welch's t-test / Mann-Whitney U test significance. p < 0.05 is statistically reliable.\n")
        f.write("- **Verdict**:\n")
        f.write("  - `SIGNIFICANT`: p < 0.05 and |Cohen's d| >= 0.1\n")
        f.write("  - `MARGINAL`: p < 0.10\n")
        f.write("  - `NOT SIGNIFICANT`: p >= 0.10\n\n")

        f.write("## Individual Filter Analysis (Call + Put Indicators)\n\n")

        for horizon in FORWARD_HORIZONS:
            f.write(f"### {horizon}-Calendar-Day Forward Return Horizon\n\n")
            f.write("| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")

            for etf_name, filters in all_results.items():
                for fname, res in filters.items():
                    if horizon not in res or res[horizon] is None:
                        continue
                    r = res[horizon]
                    v = verdict_str(r["p_ttest"], r["cohens_d"])
                    diff = r["pass_mean"] - r["fail_mean"]
                    
                    if v == "SIGNIFICANT":
                        verdict_md = "**SIGNIFICANT**"
                    elif v == "MARGINAL":
                        verdict_md = "*MARGINAL*"
                    else:
                        verdict_md = "NOT SIGNIFICANT"
                        
                    f.write(f"| {etf_name} | {fname} | {r['placement']:.1%} | "
                            f"{r['pass_mean']:+.3%} | {r['fail_mean']:+.3%} | "
                            f"{diff:+.3%} | {r['p_ttest']:.4f} | {r['p_mannwhitney']:.4f} | "
                            f"{r['cohens_d']:+.3f} | {verdict_md} |\n")
            f.write("\n")

        # ── Put Strategy Combined Filter Section ──────────────────────────────────────────────
        f.write("## Put Strategy Combined Filter Analysis\n\n")
        f.write("> Per-ETF combined conditions as implemented in `PutStrategy.evaluate_filter()` (`backtest_strategies.py`).\n")
        f.write("> Optimized via `optimize_put_filters.py` (real data, 6-component composite score).\n")
        f.write("> For put timing, **negative** Cohen's d is desired — pass days should have *lower* forward returns (i.e. the market drops after the signal, validating hedge timing).\n\n")

        # Strategy description table
        f.write("| ETF | Combined Filter | Condition |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write("| 300ETF | `RSI<60 & Vol20>Med` | `RSI(14) < 60` AND `Vol20 > Vol20_252d_median` |\n")
        f.write("| 50ETF  | `RSI<55 & Close<SMA50` | `RSI(14) < 55` AND `Close < SMA(50)` |\n")
        f.write("| 500ETF | `RSI<55 & Vol20>Med` | `RSI(14) < 55` AND `Vol20 > Vol20_252d_median` |\n\n")

        for horizon in FORWARD_HORIZONS:
            f.write(f"### Put Combined Filter — {horizon}-Calendar-Day Forward Return\n\n")
            f.write("| ETF | Filter | Placement % | Pass Avg | Fail Avg | Diff | p(t-test) | p(M-W) | Cohen's d | Verdict |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")

            for etf_name, filters in put_results.items():
                for fname, res in filters.items():
                    if horizon not in res or res[horizon] is None:
                        continue
                    r = res[horizon]
                    v = verdict_str(r["p_ttest"], r["cohens_d"])
                    diff = r["pass_mean"] - r["fail_mean"]

                    if v == "SIGNIFICANT":
                        verdict_md = "**SIGNIFICANT**"
                    elif v == "MARGINAL":
                        verdict_md = "*MARGINAL*"
                    else:
                        verdict_md = "NOT SIGNIFICANT"

                    f.write(f"| {etf_name} | {fname} | {r['placement']:.1%} | "
                            f"{r['pass_mean']:+.3%} | {r['fail_mean']:+.3%} | "
                            f"{diff:+.3%} | {r['p_ttest']:.4f} | {r['p_mannwhitney']:.4f} | "
                            f"{r['cohens_d']:+.3f} | {verdict_md} |\n")
            f.write("\n")

        # Interpretation note
        f.write("### Put Combined Filter Interpretation\n\n")
        f.write("For the protective put strategy, we buy puts when the filter passes and skip when it fails. ")
        f.write("A **negative** `Pass Avg - Fail Avg` (Diff) means the market tends to drop more on filter-pass days, ")
        f.write("which makes the put hedge more valuable — this validates the timing signal. ")
        f.write("Conversely, a positive Diff suggests the filter triggers before rallies, making the put a drag.\n\n")
        f.write("**Placement rate** is important: too low (<20%) means the hedge rarely activates, too high (>80%) ")
        f.write("means the filter provides little selectivity. The optimized filters target 30–50% placement.\n")


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

    # Run put combined filter analysis (per-ETF strategy filters)
    print("\n=== Running Put Combined Filter Analysis ===")
    put_results = {}
    for etf_name, df in etf_data.items():
        put_results[etf_name] = {}
        if etf_name in PUT_FILTER_DEFS:
            for fname, ffn in PUT_FILTER_DEFS[etf_name].items():
                put_results[etf_name][fname] = {}
                for h in FORWARD_HORIZONS:
                    res = analyze_filter(df, ffn, horizon=h)
                    put_results[etf_name][fname][h] = res
                    if res is not None:
                        v = verdict_str(res["p_ttest"], res["cohens_d"])
                        print(f"  {etf_name} | {fname} | {h}d | "
                              f"place={res['placement']:.1%} | "
                              f"pass={res['pass_mean']:+.3%} | "
                              f"fail={res['fail_mean']:+.3%} | "
                              f"p={res['p_ttest']:.4f} | d={res['cohens_d']:+.3f} | {v}")

    # Console report
    print_report(all_results)

    # Generate plots and markdown
    print("=== Generating Report Charts & Markdown ===")
    os.makedirs("validate", exist_ok=True)
    plot_report_1(etf_data, all_results)
    plot_report_2(etf_data, all_results)
    
    md_path = os.path.join("validate", "filter_validation_report.md")
    generate_markdown_report(all_results, put_results, md_path)

    print("\n=== Done ===")
    print("Reports saved to:")
    print("  validate/filter_validation_report.png   (scatter + bin plots)")
    print("  validate/filter_validation_report_2.png (bar chart + heatmap + table)")
    print(f"  {md_path} (markdown report)")

    # ── Generate separate Call and Put reports ──
    print("\n=== Generating Separate Call & Put Reports ===")
    from generate_call_report import generate_all as generate_call_all
    from generate_put_report import generate_all as generate_put_all
    generate_call_all(all_results, etf_data)
    generate_put_all(all_results, put_results, etf_data)

    print("\n=== All Reports Complete ===")
    print("  validate/filter_cover_call.md      (English call report)")
    print("  validate/filter_cover_call_cn.md   (Chinese call report)")
    print("  validate/filter_put.md             (English put report)")
    print("  validate/filter_put_cn.md          (Chinese put report)")
    print("  validate/filter_call_scatter.png   (call scatter plots)")
    print("  validate/filter_call_dashboard.png (call dashboard)")
    print("  validate/filter_call_horizon.png   (call horizon comparison)")
    print("  validate/filter_put_dashboard.png  (put dashboard)")
    print("  validate/filter_put_horizon.png    (put horizon comparison)")
    print("  validate/filter_put_tail_risk.png  (put tail risk analysis)")


if __name__ == "__main__":
    main()

