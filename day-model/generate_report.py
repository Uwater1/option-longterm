"""
Phase 3: Generate day-model/REPORT.md summary from training results.

Side-aware objective (long / short / single legacy):
- Lockbox Tail IC uses the same side-aware definition as the training objective.
- 15 diagnostic plots per ETF tag are emitted to day-model/plots/.
"""
import json
import os
import sys
import warnings
warnings.filterwarnings("ignore")
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, rankdata, norm

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent))
# Import custom penalty so joblib can deserialize the model successfully
from penalties import MCP_plus_L2

DATA_DIR = HERE / "data"
MODELS_DIR = HERE / "models"
PLOTS_DIR = HERE / "plots"
REPORT_PATH = HERE / "REPORT.md"
ROLLING_DATA_DIR = DATA_DIR / "rolling"
ROLLING_MODELS_DIR = MODELS_DIR / "rolling"
ROLLING_PLOTS_DIR = PLOTS_DIR / "rolling"
ROLLING_REPORT_PATH = HERE / "ROLLING_REPORT.md"

ETF_ORDER = ["300ETF", "500ETF", "588000ETF", "159915ETF"]
TARGET = "trade_return"
LOCKBOX_DATE = "2024-03-01"

# Mirror of train_model.py SIDE_CONFIG (kept local to avoid heavy optuna/skglm import).
SIDE_CONFIG = {
    "single": {"tail_def": "two_sided"},
    "long":   {"tail_def": "top_only"},
    "short":  {"tail_def": "bot_only"},
}

VAL_BLOCKS_INNER = [
    ("2016-10-01", "2017-01-01"),
    ("2018-07-01", "2018-10-01"),
    ("2020-04-01", "2020-07-01"),
    ("2022-10-01", "2023-01-01"),
]
VAL_BLOCKS_OUTER = [
    ("2021-07-01", "2021-10-01"),
    ("2023-07-01", "2023-10-01"),
]
VAL_BLOCKS = VAL_BLOCKS_INNER + VAL_BLOCKS_OUTER
SCREEN_FDR = 0.50
MIN_FEATURE = 15


# ============================================================
# Metric helpers
# ============================================================
def spearman_ic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 5 or np.std(y_pred) < 1e-12 or np.std(y_true) < 1e-12:
        return 0.0
    rho, _ = spearmanr(y_pred, y_true)
    return float(rho) if not np.isnan(rho) else 0.0


def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape[0] < 5:
        return 0.0
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    ra = rankdata(a); rb = rankdata(b)
    ra -= ra.mean(); rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom > 1e-12 else 0.0


def side_tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str = "single") -> float:
    """Side-aware Tail IC (matches train_model.side_tail_ic)."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    n = y_pred.shape[0]
    pct = 0.15 if side in ["long", "short"] else 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    if cfg["tail_def"] == "top_only":
        idx = np.argsort(y_pred, kind="quicksort")[-n_tail:]
    elif cfg["tail_def"] == "bot_only":
        idx = np.argsort(y_pred, kind="quicksort")[:n_tail]
    else:
        if n < n_tail * 2:
            return 0.0
        order = np.argsort(y_pred, kind="quicksort")
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
    return _spearman_from_arrays(y_true[idx], y_pred[idx])


def side_tail_mask(y_pred: np.ndarray, side: str) -> np.ndarray:
    """Boolean mask selecting side-tail rows from y_pred."""
    y_pred = np.asarray(y_pred, dtype=np.float64)
    n = y_pred.shape[0]
    pct = 0.15 if side in ["long", "short"] else 0.10
    n_tail = max(5, int(n * pct))
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    mask = np.zeros(n, dtype=bool)
    if cfg["tail_def"] == "top_only":
        idx = np.argsort(y_pred, kind="quicksort")[-n_tail:]
    elif cfg["tail_def"] == "bot_only":
        idx = np.argsort(y_pred, kind="quicksort")[:n_tail]
    else:
        order = np.argsort(y_pred, kind="quicksort")
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
    mask[idx] = True
    return mask


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


def benjamini_hochberg(p_values: np.ndarray, fdr_level: float = 0.20) -> np.ndarray:
    n = len(p_values)
    if n == 0:
        return np.zeros(0, dtype=bool)
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    
    thresholds = (np.arange(1, n + 1) / n) * fdr_level
    pass_idx = np.where(sorted_p <= thresholds)[0]
    
    mask = np.zeros(n, dtype=bool)
    if len(pass_idx) > 0:
        max_pass_rank = pass_idx.max()
        mask[sorted_idx[:max_pass_rank + 1]] = True
    return mask


def run_screening(X_working: np.ndarray, y_working: np.ndarray, fdr_level: float = SCREEN_FDR):
    n, p = X_working.shape
    X_f64 = X_working.astype(np.float64, copy=False)
    y_f64 = y_working.astype(np.float64, copy=False)

    X_rank = np.apply_along_axis(rankdata, 0, X_f64).astype(np.float64)
    y_rank = rankdata(y_f64).astype(np.float64)

    Xc = X_rank - X_rank.mean(axis=0, keepdims=True)
    yc = y_rank - y_rank.mean()
    sx = np.sqrt((Xc * Xc).sum(axis=0))
    sy = np.sqrt((yc * yc).sum())
    denom = sx * sy
    denom[denom < 1e-12] = np.nan
    rhos = (Xc.T @ yc) / denom
    rhos = np.nan_to_num(rhos, nan=0.0)

    with np.errstate(divide="ignore", invalid="ignore"):
        t_sq_denom = 1.0 - rhos * rhos
        t_stat = np.where(t_sq_denom > 1e-12,
                          rhos * np.sqrt(np.maximum((n - 2) / t_sq_denom, 0.0)),
                          0.0)
    p_vals = 2.0 * norm.sf(np.abs(t_stat))
    p_vals = np.nan_to_num(p_vals, nan=1.0, posinf=1.0, neginf=1.0)

    screen_mask = benjamini_hochberg(p_vals, fdr_level=fdr_level)

    return screen_mask, p_vals, rhos


def get_step1_passed_features(df, features_all, etf_name):
    X_df = df[features_all].ffill()
    _col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(_col_med)
    X = X_df.values.astype(np.float32)
    
    y = df[TARGET].values.astype(np.float32)
    y_scaled = (y * 100.0).astype(np.float32)
    
    sel_val_mask = np.zeros(len(df), dtype=bool)
    for start_val, end_val in VAL_BLOCKS:
        block_mask = (df["date"] >= pd.Timestamp(start_val)) & (df["date"] < pd.Timestamp(end_val))
        sel_val_mask |= block_mask
        
    sel_train_mask = (df["date"] < LOCKBOX_DATE) & (~sel_val_mask)
    
    gap_days = 10
    sel_train_dates = df["date"][sel_train_mask]
    keep_train = np.ones(len(sel_train_dates), dtype=bool)
    
    for start_val, end_val in VAL_BLOCKS:
        embargo_start = pd.Timestamp(start_val) - pd.Timedelta(days=gap_days)
        embargo_end = pd.Timestamp(end_val) + pd.Timedelta(days=gap_days)
        in_embargo = (sel_train_dates >= embargo_start) & (sel_train_dates <= embargo_end)
        keep_train[in_embargo] = False
        
    sel_train_indices = df.index[sel_train_mask][keep_train]
    sel_train_mask = np.zeros(len(df), dtype=bool)
    sel_train_mask[sel_train_indices] = True
    
    sel_train_idx = np.where(sel_train_mask)[0]
    X_sel_train = X[sel_train_idx]
    y_sel_train = y_scaled[sel_train_idx]
    
    fdr_level = 0.25 if etf_name == "588000ETF" else SCREEN_FDR
    screen_mask, p_vals, rhos = run_screening(X_sel_train, y_sel_train, fdr_level=fdr_level)
    
    passed_features = [features_all[i] for i in range(len(features_all)) if screen_mask[i]]
    return passed_features


# ============================================================
# Vectorized batch helpers (numpy-only, fp64 internally for stability)
# ============================================================
def _rank_rows(a: np.ndarray) -> np.ndarray:
    """Rank each row of (m, n) independently, returning ranks 1..n with
    AVERAGE rank for ties (Spearman convention). Uses pandas' C-implemented
    axis=1 rank (fast and correct), with a fast no-tie numpy path."""
    a = np.asarray(a, dtype=np.float64)
    m, n = a.shape
    if n == 0:
        return a.copy()
    # Fast path: integer ranks via argsort inverse (no ties).
    order = a.argsort(axis=1, kind="quicksort")
    rows = np.arange(m)[:, None]
    sorted_a = a[rows, order]
    has_ties_any = bool(np.any(sorted_a[:, 1:] == sorted_a[:, :-1]))
    if not has_ties_any:
        ranks = np.empty((m, n), dtype=np.float64)
        ranks[rows, order] = np.arange(1, n + 1, dtype=np.float64)[None, :]
        return ranks
    # Tie-aware path: delegate to pandas (C-implemented, vectorized).
    return pd.DataFrame(a).rank(axis=1, method="average").values


def _spearman_rows(y_b: np.ndarray, p_b: np.ndarray) -> np.ndarray:
    """Vectorized Spearman correlation per row. (m, n) -> (m,)."""
    m, n = y_b.shape
    if n < 5:
        return np.zeros(m, dtype=np.float64)
    yr = _rank_rows(y_b.astype(np.float64, copy=False))
    pr = _rank_rows(p_b.astype(np.float64, copy=False))
    yr = yr - yr.mean(axis=1, keepdims=True)
    pr = pr - pr.mean(axis=1, keepdims=True)
    denom = np.sqrt((yr * yr).sum(axis=1) * (pr * pr).sum(axis=1))
    out = np.zeros(m, dtype=np.float64)
    nz = denom > 1e-12
    out[nz] = (yr[nz] * pr[nz]).sum(axis=1) / denom[nz]
    return out


def _decile_mono_rows(y_b: np.ndarray, p_b: np.ndarray) -> np.ndarray:
    """Vectorized decile monotonicity per row. (m, n) -> (m,)."""
    m, n = y_b.shape
    out = np.zeros(m, dtype=np.float64)
    if n < 20:
        return out
    # Sort each row by p
    order = p_b.argsort(axis=1, kind="quicksort")
    rows = np.arange(m)[:, None]
    y_sorted = y_b[rows, order]
    # Reshape to (m, 10, chunk) ignoring remainder (approximation for fixed-size windows).
    chunk = n // 10
    if chunk < 2:
        return out
    y_reshaped = y_sorted[:, :chunk * 10].reshape(m, 10, chunk)
    means = y_reshaped.mean(axis=2)  # (m, 10)
    # Rank each row's 10 means (no ties expected for floats)
    m_order = means.argsort(axis=1, kind="quicksort")
    m_ranks = np.empty((m, 10), dtype=np.float64)
    m_ranks[rows[:, :10], m_order] = np.arange(1, 11, dtype=np.float64)[None, :]
    a = np.arange(1, 11, dtype=np.float64)
    a -= a.mean()
    m_ranks -= m_ranks.mean(axis=1, keepdims=True)
    denom = np.sqrt((a * a).sum() * (m_ranks * m_ranks).sum(axis=1))
    nz = denom > 1e-12
    out[nz] = (m_ranks[nz] * a).sum(axis=1) / denom[nz]
    return out


def block_bootstrap_ci(y_true, y_pred, block_size=10, n_bootstraps=1000):
    """Vectorized block-bootstrap CIs for Spearman IC and decile monotonicity.
    Returns (ci_ic, ci_mono) tuples."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    n = len(y_true)
    if n < block_size:
        block_size = max(1, n // 5)
    np.random.seed(42)
    num_blocks = int(np.ceil(n / block_size))
    possible_starts = n - block_size + 1
    if possible_starts <= 0:
        idx = np.random.choice(n, size=(n_bootstraps, n), replace=True)
    else:
        starts = np.random.choice(possible_starts, size=(n_bootstraps, num_blocks), replace=True)
        offsets = np.arange(block_size)
        idx = (starts[:, :, None] + offsets[None, None, :]).reshape(n_bootstraps, -1)[:, :n]
    y_b = y_true[idx]
    p_b = y_pred[idx]
    boot_ics = _spearman_rows(y_b, p_b)
    boot_monos = _decile_mono_rows(y_b, p_b)
    ci_ic = (float(np.percentile(boot_ics, 2.5)), float(np.percentile(boot_ics, 97.5)))
    ci_mono = (float(np.percentile(boot_monos, 2.5)), float(np.percentile(boot_monos, 97.5)))
    return ci_ic, ci_mono


# ============================================================
# 15 Plot renderers (drawn onto provided axes; combined into ONE figure per ETF tag).
# ============================================================
PLOT_TITLES = [
    "01 Coefficients",
    "02 Decile Spread (OOS)",
    "03 Decile Spread (All)",
    "04 Side-Tail Return Hist",
    "05 Tail Scatter",
    "06 Yearly Overall IC",
    "07 Yearly Tail IC",
    "08 Yearly Tail Hit Rate",
    "09 Tail vs Rest Mean",
    "10 Rolling Tail IC",
    "11 Rolling Overall IC",
    "12 Prediction Dist",
    "13 Tail Equity Curve",
    "14 Quantile Decay",
    "15 Precision @ k",
]


def _decile_bars(ax, y_true, y_pred, title):
    df_q = pd.DataFrame({"y": y_true, "p": y_pred})
    df_q["decile"] = pd.qcut(df_q["p"], 10, labels=False, duplicates="drop")
    stats = df_q.groupby("decile")["y"].agg(["mean", "median", "std"])
    deciles = stats.index + 1
    ax.bar(deciles, stats["mean"], color="green", alpha=0.9, label="Mean")
    ax.scatter(deciles, stats["median"], color="darkorange", marker="o", s=30, label="Median", zorder=3)
    ax.set_xlabel("Predicted Decile")
    ax.set_ylabel("Mean / Median ret (%)")
    ax.set_title(title, fontsize=10)
    ax.set_xticks(range(1, 11))
    twin = ax.twinx()
    twin.scatter(deciles, stats["std"], color="crimson", marker="x", s=30, label="S.D.", zorder=3)
    twin.set_ylabel("S.D. (%)", color="crimson")
    twin.tick_params(axis="y", labelcolor="crimson")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = twin.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7)


def _render_coefs(ax, model, selected_features):
    coefs = model.coef_
    abs_coefs = np.abs(coefs)
    sort_idx = np.argsort(abs_coefs)[-min(15, len(coefs)):]
    sorted_coefs = coefs[sort_idx]
    sorted_feats = [selected_features[i] for i in sort_idx]
    ax.barh(sorted_feats, sorted_coefs, color="royalblue")
    ax.axvline(0, color="gray", linestyle="--")
    ax.set_title(f"Coefficients (Top {len(sorted_feats)})", fontsize=10)


def _render_decile_oos(ax, y_lock, pred_lock):
    _decile_bars(ax, y_lock, pred_lock, "Decile Spread (OOS Lockbox)")


def _render_decile_all(ax, y_all, pred_all):
    _decile_bars(ax, y_all, pred_all, "Decile Spread (All Data)")


def _render_tail_hist(ax, y_lock, pred_lock, side):
    mask = side_tail_mask(pred_lock, side)
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    if cfg["tail_def"] == "two_sided":
        order = np.argsort(pred_lock, kind="quicksort")
        n_tail = max(5, int(len(pred_lock) * 0.10))
        top_idx = order[-n_tail:]; bot_idx = order[:n_tail]
        ax.hist(y_lock[top_idx], bins=20, alpha=0.65, color="seagreen", label=f"Top 10% (n={top_idx.size})")
        ax.hist(y_lock[bot_idx], bins=20, alpha=0.65, color="firebrick", label=f"Bot 10% (n={bot_idx.size})")
    elif cfg["tail_def"] == "top_only":
        ax.hist(y_lock[mask], bins=20, alpha=0.8, color="seagreen", label=f"Top 10% (n={mask.sum()})")
    else:
        ax.hist(y_lock[mask], bins=20, alpha=0.8, color="firebrick", label=f"Bot 10% (n={mask.sum()})")
    ax.axvline(0.0, color="black", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Actual ret (%)")
    ax.set_ylabel("Freq")
    ax.set_title(f"Side-Tail Return Hist [{side}]", fontsize=10)
    ax.legend(fontsize=7)


def _render_tail_scatter(ax, y_lock, pred_lock, side):
    mask = side_tail_mask(pred_lock, side)
    ax.scatter(pred_lock[~mask], y_lock[~mask], s=6, alpha=0.25, color="lightgray", label="Rest")
    ax.scatter(pred_lock[mask], y_lock[mask], s=10, alpha=0.75, color="navy", label="Side-Tail")
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Pred ret (%)")
    ax.set_ylabel("Actual ret (%)")
    ax.set_title(f"Tail Scatter [{side}]", fontsize=10)
    ax.legend(fontsize=7)


def _render_yearly_overall_ic(ax, dates_lock, y_lock, pred_lock):
    years = pd.Series(pd.to_datetime(dates_lock)).dt.year
    ics, yr_labels = [], []
    for yr in sorted(years.unique()):
        m = (years == yr).values
        if m.sum() < 5:
            continue
        ics.append(spearman_ic(y_lock[m], pred_lock[m]))
        yr_labels.append(int(yr))
    if ics:
        ax.bar(yr_labels, ics, color="steelblue")
        ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
        for x, v in zip(yr_labels, ics):
            ax.text(x, v, f"{v:+.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
    ax.set_title("Yearly Overall IC (two-sided)", fontsize=10)
    ax.set_xlabel("Year")
    ax.set_ylabel("Overall IC")


def _render_yearly_tail_ic(ax, dates_lock, y_lock, pred_lock, side):
    years = pd.Series(pd.to_datetime(dates_lock)).dt.year
    ics, yr_labels = [], []
    for yr in sorted(years.unique()):
        m = (years == yr).values
        if m.sum() < 20:
            continue
        ics.append(side_tail_ic(y_lock[m], pred_lock[m], side))
        yr_labels.append(int(yr))
    if ics:
        ax.bar(yr_labels, ics, color="darkorange")
        ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
        for x, v in zip(yr_labels, ics):
            ax.text(x, v, f"{v:+.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
    ax.set_title(f"Yearly Tail IC [{side}]", fontsize=10)
    ax.set_xlabel("Year")
    ax.set_ylabel(f"Tail IC [{side}]")


def _render_yearly_hit_rate(ax, dates_lock, y_lock, pred_lock, side):
    years = pd.Series(pd.to_datetime(dates_lock)).dt.year
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    bench = float(np.mean(y_lock))
    hits, yr_labels = [], []
    for yr in sorted(years.unique()):
        m = (years == yr).values
        if m.sum() < 20:
            continue
        sub_pred = pred_lock[m]; sub_y = y_lock[m]
        tail_idx = side_tail_mask(sub_pred, side)
        if tail_idx.sum() == 0:
            continue
        if cfg["tail_def"] == "top_only":
            hit = float(np.mean(sub_y[tail_idx] > bench))
        elif cfg["tail_def"] == "bot_only":
            hit = float(np.mean(sub_y[tail_idx] < bench))
        else:
            order = np.argsort(sub_pred, kind="quicksort")
            n_tail = max(5, int(len(sub_pred) * 0.10))
            top_idx = order[-n_tail:]; bot_idx = order[:n_tail]
            hit = 0.5 * (float(np.mean(sub_y[top_idx] > bench)) + float(np.mean(sub_y[bot_idx] < bench)))
        hits.append(hit)
        yr_labels.append(int(yr))
    if hits:
        ax.bar(yr_labels, hits, color="mediumseagreen")
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, label="Random (0.5)")
        ax.set_ylim(0, 1)
        for x, v in zip(yr_labels, hits):
            ax.text(x, v, f"{v*100:.0f}%", ha="center", va="bottom", fontsize=8)
        ax.legend(fontsize=7)
    ax.set_title(f"Yearly Tail Hit Rate [{side}]", fontsize=10)
    ax.set_xlabel("Year")
    ax.set_ylabel("Hit rate")


def _render_tail_vs_rest(ax, y_lock, pred_lock, side):
    mask = side_tail_mask(pred_lock, side)
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    if cfg["tail_def"] == "two_sided":
        order = np.argsort(pred_lock, kind="quicksort")
        n_tail = max(5, int(len(pred_lock) * 0.10))
        top_idx = order[-n_tail:]; bot_idx = order[:n_tail]
        rest_idx = np.ones(len(pred_lock), dtype=bool)
        rest_idx[top_idx] = False; rest_idx[bot_idx] = False
        labels = ["Bot 10%", "Rest", "Top 10%"]
        means = [float(y_lock[bot_idx].mean()), float(y_lock[rest_idx].mean()), float(y_lock[top_idx].mean())]
    elif cfg["tail_def"] == "top_only":
        labels = ["Rest", "Top 10%"]
        means = [float(y_lock[~mask].mean()), float(y_lock[mask].mean())]
    else:
        labels = ["Bot 10%", "Rest"]
        means = [float(y_lock[mask].mean()), float(y_lock[~mask].mean())]
    colors = ["firebrick" if "Bot" in l else ("seagreen" if "Top" in l else "lightgray") for l in labels]
    ax.bar(labels, means, color=colors)
    ax.axhline(0.0, color="black", linestyle="--", linewidth=0.8)
    for i, v in enumerate(means):
        ax.text(i, v, f"{v:+.3f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=9)
    ax.set_title(f"Tail Mean vs Rest [{side}]", fontsize=10)
    ax.set_ylabel("Mean ret (%)")


def _rolling_ic(dates, y, pred, window, side=None):
    """Vectorized rolling IC via sliding_window_view.
    For side-aware (long/short) we still loop because tail-row selection
    differs per window, but use the vectorized Spearman for two-sided."""
    from numpy.lib.stride_tricks import sliding_window_view
    y = np.asarray(y, dtype=np.float64)
    pred = np.asarray(pred, dtype=np.float64)
    n = len(y)
    if n < window:
        window = max(20, n // 2)
    if n < window:
        return [], []
    y_w = sliding_window_view(y, window)   # (m, window)
    p_w = sliding_window_view(pred, window)
    if side is None:
        ics = _spearman_rows(y_w, p_w)
    else:
        # Loop side-aware (only m=n-window+1 iterations).
        ics = np.array([side_tail_ic(y_w[i], p_w[i], side) for i in range(y_w.shape[0])])
    return list(dates[window - 1:]), list(ics)


def _render_rolling_tail_ic(ax, dates_lock, y_lock, pred_lock, side, window=252):
    if len(y_lock) < window:
        window = max(20, len(y_lock) // 2)
    rd, rv = _rolling_ic(dates_lock, y_lock, pred_lock, window, side=side)
    ax.plot(rd, rv, color="darkorange", linewidth=1.2)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.fill_between(rd, 0, rv, where=[v >= 0 for v in rv], alpha=0.18, color="seagreen")
    ax.fill_between(rd, 0, rv, where=[v < 0 for v in rv], alpha=0.18, color="firebrick")
    ax.set_title(f"Rolling {window}d Tail IC [{side}]", fontsize=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Tail IC")


def _render_rolling_overall_ic(ax, dates_lock, y_lock, pred_lock, window=252):
    if len(y_lock) < window:
        window = max(20, len(y_lock) // 2)
    rd, rv = _rolling_ic(dates_lock, y_lock, pred_lock, window, side=None)
    ax.plot(rd, rv, color="steelblue", linewidth=1.2)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.fill_between(rd, 0, rv, where=[v >= 0 for v in rv], alpha=0.18, color="seagreen")
    ax.fill_between(rd, 0, rv, where=[v < 0 for v in rv], alpha=0.18, color="firebrick")
    ax.set_title(f"Rolling {window}d Overall IC", fontsize=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Overall IC")


def _render_pred_dist(ax, pred_all, side):
    ax.hist(pred_all, bins=50, color="slateblue", alpha=0.75)
    p10, p50, p90 = np.percentile(pred_all, [10, 50, 90])
    ax.axvline(p10, color="firebrick", linestyle="--", linewidth=1.0, label=f"P10={p10:+.2f}")
    ax.axvline(p50, color="gray", linestyle="--", linewidth=1.0, label=f"P50={p50:+.2f}")
    ax.axvline(p90, color="seagreen", linestyle="--", linewidth=1.0, label=f"P90={p90:+.2f}")
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    if cfg["tail_def"] == "top_only":
        ax.axvspan(p90, max(pred_all), alpha=0.12, color="seagreen")
    elif cfg["tail_def"] == "bot_only":
        ax.axvspan(min(pred_all), p10, alpha=0.12, color="firebrick")
    ax.set_xlabel("Pred ret (%)")
    ax.set_ylabel("Freq")
    ax.set_title(f"Prediction Dist [{side}]", fontsize=10)
    ax.legend(fontsize=7)


def _render_tail_equity(ax, dates_lock, y_lock, pred_lock, side):
    s = pd.Series(y_lock, index=pd.to_datetime(dates_lock)).sort_index()
    p = pd.Series(pred_lock, index=s.index).sort_index()
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    if cfg["tail_def"] in ("top_only", "bot_only"):
        mask = pd.Series(side_tail_mask(p.values, side), index=s.index)
        sel_y = s.where(mask, 0.0) if cfg["tail_def"] == "top_only" else (-s).where(mask, 0.0)
        cum = sel_y.cumsum()
        ax.plot(cum.index, cum.values,
                color="seagreen" if cfg["tail_def"] == "top_only" else "firebrick",
                linewidth=1.2, label=f"{side} cum return")
    else:
        order = np.argsort(p.values, kind="quicksort")
        n_tail = max(5, int(len(p) * 0.10))
        top_idx = order[-n_tail:]; bot_idx = order[:n_tail]
        mask_top = pd.Series(False, index=s.index); mask_top.iloc[top_idx] = True
        mask_bot = pd.Series(False, index=s.index); mask_bot.iloc[bot_idx] = True
        long_pnl = s.where(mask_top, 0.0)
        short_pnl = (-s).where(mask_bot, 0.0)
        cum = (long_pnl + short_pnl).cumsum()
        ax.plot(cum.index, cum.values, color="navy", linewidth=1.2, label="Top long + Bot short cum")
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title(f"Tail Equity Curve [{side}]", fontsize=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cum ret (%)")
    ax.legend(fontsize=7)


def _render_quantile_decay(ax, y_all, pred_all):
    df_q = pd.DataFrame({"y": y_all, "p": pred_all})
    df_q["q"] = pd.qcut(df_q["p"], 10, labels=False, duplicates="drop")
    means = df_q.groupby("q")["y"].mean()
    stds = df_q.groupby("q")["y"].std()
    qs = means.index + 1
    ax.bar(qs, means, color="indigo", alpha=0.85, label="Mean actual")
    ax.errorbar(qs, means, yerr=stds, fmt="none", color="black", capsize=3, label="± 1 S.D.")
    ax.axhline(float(df_q["y"].mean()), color="gray", linestyle="--", linewidth=0.8, label="Global mean")
    ax.set_xlabel("Pred Quantile (1=Low)")
    ax.set_ylabel("Actual ret (%)")
    ax.set_title("Quantile Decay (All Data)", fontsize=10)
    ax.set_xticks(range(1, 11))
    ax.legend(fontsize=7)


def _render_precision_at_k(ax, y_lock, pred_lock, side):
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    bench = float(np.mean(y_lock))
    ks = list(range(1, 11))
    precisions = []
    order = np.argsort(pred_lock, kind="quicksort")
    n = len(pred_lock)
    for k in ks:
        n_k = max(1, int(n * k / 100.0))
        if cfg["tail_def"] == "top_only":
            sel = order[-n_k:]
            delta = float(np.mean(y_lock[sel])) - bench
        elif cfg["tail_def"] == "bot_only":
            sel = order[:n_k]
            delta = bench - float(np.mean(y_lock[sel]))
        else:
            top_sel = order[-n_k:]; bot_sel = order[:n_k]
            delta = float(np.mean(y_lock[top_sel])) - float(np.mean(y_lock[bot_sel]))
        precisions.append(delta)
    ax.plot(ks, precisions, marker="o", color="darkcyan", linewidth=1.2)
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Top-k% (or Bot-k% short)")
    ax.set_ylabel("Spread vs bench (%)")
    ax.set_title(f"Precision @ k [{side}]", fontsize=10)
    ax.set_xticks(ks)


def render_diagnostics_figure(etf, side, model, selected_features,
                              dates_all, y_all, pred_all,
                              dates_lock, y_lock, pred_lock,
                              extra_stats=None):
    """Build ONE figure with 15 subplots (5 rows x 3 cols). Save as
    `diagnostics_{etf}_{side}.png` in PLOTS_DIR. Returns the filename."""
    PLOTS_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(5, 3, figsize=(22, 25))
    axes_flat = axes.flatten()

    # Header / stats panel as suptitle
    stat_txt = ""
    if extra_stats:
        stat_txt = " | ".join(f"{k}={v:+.4f}" if isinstance(v, float) else f"{k}={v}"
                              for k, v in extra_stats.items())
    fig.suptitle(f"Diagnostics — {etf} (side={side}){('  |  ' + stat_txt) if stat_txt else ''}",
                 fontsize=14, y=0.995)

    _render_coefs(axes_flat[0], model, selected_features)
    _render_decile_oos(axes_flat[1], y_lock, pred_lock)
    _render_decile_all(axes_flat[2], y_all, pred_all)
    _render_tail_hist(axes_flat[3], y_lock, pred_lock, side)
    _render_tail_scatter(axes_flat[4], y_lock, pred_lock, side)
    _render_yearly_overall_ic(axes_flat[5], dates_lock, y_lock, pred_lock)
    _render_yearly_tail_ic(axes_flat[6], dates_lock, y_lock, pred_lock, side)
    _render_yearly_hit_rate(axes_flat[7], dates_lock, y_lock, pred_lock, side)
    _render_tail_vs_rest(axes_flat[8], y_lock, pred_lock, side)
    _render_rolling_tail_ic(axes_flat[9], dates_lock, y_lock, pred_lock, side)
    _render_rolling_overall_ic(axes_flat[10], dates_lock, y_lock, pred_lock)
    _render_pred_dist(axes_flat[11], pred_all, side)
    _render_tail_equity(axes_flat[12], dates_lock, y_lock, pred_lock, side)
    _render_quantile_decay(axes_flat[13], y_all, pred_all)
    _render_precision_at_k(axes_flat[14], y_lock, pred_lock, side)

    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fname = f"diagnostics_{etf}_{side}.png"
    fig.savefig(PLOTS_DIR / fname, dpi=110)
    plt.close(fig)
    return fname


# ============================================================
# Main
# ============================================================
def _load_results_dict():
    """Load all results_*.json keyed by tag."""
    out = {}
    for p in DATA_DIR.glob("results_*.json"):
        try:
            with open(p) as f:
                r = json.load(f)
            out[r.get("tag", r.get("etf"))] = r
        except Exception as e:
            print(f"  [WARNING] Failed to load {p.name}: {e}")
    return out


def _ordered_tags(results_dict):
    """Return tags sorted by (ETF_ORDER index, side). Single side first."""
    side_order = {"single": 0, "long": 1, "short": 2}
    def key(t):
        r = results_dict[t]
        etf = r.get("etf", "")
        side = r.get("side", "single")
        etf_idx = ETF_ORDER.index(etf) if etf in ETF_ORDER else len(ETF_ORDER)
        return (etf_idx, side_order.get(side, 99), t)
    return sorted(results_dict.keys(), key=key)


_ETF_FEATURES_CACHE: dict = {}  # ETF name -> (dates_all, y_scaled, X_df) for reuse across sides


def _load_etf_features(etf: str):
    """Load + prep ETF features parquet once, cache for reuse across sides."""
    if etf in _ETF_FEATURES_CACHE:
        return _ETF_FEATURES_CACHE[etf]
    features_path = DATA_DIR / f"features_{etf}.parquet"
    if not features_path.exists():
        return None
    df = pd.read_parquet(features_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])
    out = (df, features_path)
    _ETF_FEATURES_CACHE[etf] = out
    return out


def _process_tag(tag: str, r: dict):
    """Worker: process ONE tag (load features, predict, compute metrics,
    emit 15-panel figure). Returns updated results dict + diagnostics filename."""
    import warnings
    warnings.filterwarnings("ignore")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as _plt
    from joblib import load as _jload
    from scipy.stats import spearmanr as _spearmanr

    etf = r["etf"]
    side = r.get("side", "single")
    model_path = MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = MODELS_DIR / f"scaler_{tag}.joblib"
    cached = _load_etf_features(etf)
    if cached is None or not (model_path.exists() and scaler_path.exists()):
        return tag, r, None, "missing files"

    df, _ = cached
    try:
        model = _jload(model_path)
        scaler_meta = _jload(scaler_path)
        selected_features = scaler_meta["selected_features"]
        scaler = scaler_meta["scaler"]
        target_col = scaler_meta.get("target", TARGET)

        y = df[target_col].values.astype(np.float32)
        y_scaled = (y * 100.0).astype(np.float32)
        # Fill missing values: ffill, then per-column median, then 0.0 for any column
        # that is entirely NaN (defensive — should not happen after the model-retrain
        # fix that purged stale/deprecated features from selected_features).
        X_df = df[selected_features].ffill()
        col_med = X_df.median().fillna(0.0)
        X_df = X_df.fillna(col_med)
        X = X_df.values.astype(np.float32)

        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled).astype(np.float32)

        lockbox_mask = df["date"] >= pd.Timestamp(LOCKBOX_DATE)
        dates_all = df["date"].values
        dates_lock = df["date"][lockbox_mask].values
        y_lock = y_scaled[lockbox_mask]
        pred_lock = preds[lockbox_mask]

        # Lockbox metrics (side-aware Tail IC).
        lockbox_ic = float(_spearmanr(pred_lock, y_lock)[0]) if len(y_lock) >= 5 else 0.0
        if np.isnan(lockbox_ic):
            lockbox_ic = 0.0
        lockbox_tail_ic = side_tail_ic(y_lock, pred_lock, side)
        lockbox_mono = compute_decile_monotonicity(y_lock, pred_lock)

        r["lockbox_overall_ic"] = lockbox_ic
        r["lockbox_tail_ic"] = lockbox_tail_ic
        r["lockbox_tail_ic_def"] = side
        r["lockbox_monotonicity"] = lockbox_mono
        r["n_samples_lockbox"] = int(len(y_lock))

        deflated_val_ic = r.get("deflated_val_ic", np.nan)
        cv_ic_target = deflated_val_ic
        if np.isnan(cv_ic_target):
            cv_ic_target = r.get("selection_val_overall_ic", np.nan)
        if np.isnan(cv_ic_target):
            cv_ic_target = float(r["best_raw_metrics"][3])
        r["ic_generalization_gap"] = cv_ic_target - lockbox_ic

        cv_mono = float(r["best_raw_metrics"][4])
        r["mono_generalization_gap"] = cv_mono - lockbox_mono

        ci_ic, ci_mono = block_bootstrap_ci(y_lock, pred_lock, block_size=10, n_bootstraps=1000)
        r["lockbox_ic_ci"] = ci_ic
        r["lockbox_mono_ci"] = ci_mono
        r["lockbox_ic_swallowed"] = bool(ci_ic[0] <= cv_ic_target <= ci_ic[1])
        r["lockbox_mono_swallowed"] = bool(ci_mono[0] <= cv_mono <= ci_mono[1])

        # Compute pruned features list
        skip_step1 = scaler_meta.get("skip_step1", False)
        skip_step2 = scaler_meta.get("skip_step2", False)
        features_all = scaler_meta.get("features", [])
        if features_all:
            if skip_step1:
                stopped_by_step1 = []
                passed_step1 = features_all
            else:
                passed_step1 = get_step1_passed_features(df, features_all, etf)
                stopped_by_step1 = [f for f in features_all if f not in passed_step1]
            stopped_by_step2 = [f for f in passed_step1 if f not in selected_features]
            r["features_stopped_by_step1"] = stopped_by_step1
            r["features_stopped_by_step2"] = stopped_by_step2
        else:
            r["features_stopped_by_step1"] = []
            r["features_stopped_by_step2"] = []
        r["skip_step1"] = skip_step1
        r["skip_step2"] = skip_step2

        # Check Step 2 fallback status from the training diagnostics
        diag = r.get("diagnostics", {})
        stability = diag.get("stability", {})
        stability_fallback_used = stability.get("fallback_triggered", False)
        if stability_fallback_used:
            print(f"  [WARNING] Step 2 Stability Selection Fallback was triggered for {tag} (fewer than {MIN_FEATURE} clusters selected).")

        # Persist results JSON + scaler metadata.
        with open(DATA_DIR / f"results_{tag}.json", "w") as f_json:
            json.dump(r, f_json, indent=2, default=str)
        scaler_meta["holdout_ic"] = lockbox_ic
        scaler_meta["holdout_tail_ic"] = lockbox_tail_ic
        scaler_meta["holdout_tail_ic_def"] = side
        scaler_meta["holdout_mono"] = lockbox_mono
        scaler_meta["ic_gen_gap"] = r["ic_generalization_gap"]
        scaler_meta["mono_gen_gap"] = r["mono_generalization_gap"]
        scaler_meta["deflated_val_ic"] = deflated_val_ic
        scaler_meta["deflated_val_tail_ic"] = r.get("deflated_val_tail_ic", np.nan)
        scaler_meta["skip_step1"] = skip_step1
        scaler_meta["skip_step2"] = skip_step2
        joblib.dump(scaler_meta, scaler_path)

        extra_stats = {
            "IC": float(lockbox_ic),
            f"TailIC[{side}]": float(lockbox_tail_ic),
            "Mono": float(lockbox_mono),
        }
        fname = render_diagnostics_figure(
            etf, side, model, selected_features,
            dates_all, y_scaled, preds,
            dates_lock, y_lock, pred_lock,
            extra_stats=extra_stats,
        )
        r["diagnostics_plot"] = fname
        msg = (f"IC={lockbox_ic:+.4f} TailIC[{side}]={lockbox_tail_ic:+.4f} "
               f"CI=[{ci_ic[0]:+.4f},{ci_ic[1]:+.4f}] -> plots/{fname}")
        return tag, r, fname, msg
    except Exception as ex:
        import traceback
        return tag, r, None, f"FAILED: {ex}\n{traceback.format_exc()}"


def main():
    print("Generating day-model REPORT.md (side-aware, ONE 15-panel figure per ETF side)...")
    results_dict = _load_results_dict()
    if not results_dict:
        print("  [ERROR] No results files found in data directory. Run train_model.py first.")
        return

    PLOTS_DIR.mkdir(exist_ok=True)
    tags = _ordered_tags(results_dict)

    # 1. Parallel per-tag processing. Worker processes are independent;
    # matplotlib 'Agg' backend is process-safe and we save each figure inside the worker.
    n_jobs = min(len(tags), max(1, (os.cpu_count() or 4) - 1))
    print(f"Processing {len(tags)} tag(s) across {n_jobs} parallel workers...")
    try:
        from joblib import Parallel, delayed
        results = Parallel(n_jobs=n_jobs, backend="loky", verbose=0)(
            delayed(_process_tag)(t, results_dict[t]) for t in tags
        )
    except Exception as e:
        print(f"  [WARNING] Parallel processing failed ({e}); falling back to sequential.")
        results = [_process_tag(t, results_dict[t]) for t in tags]

    for tag, r_updated, _fname, msg in results:
        results_dict[tag] = r_updated
        print(f"  [{tag}] {msg}")

    # 2. Second pass: write REPORT.md
    _write_report(results_dict)
    print(f"REPORT.md written to {REPORT_PATH}")


def _write_report(results_dict):
    lines = []
    lines.append("# Day-Model Remake Optimization Report")
    lines.append("> Generated by day-model/generate_report.py")
    lines.append("")

    # Check if fallback was used anywhere
    fallback_tags = []
    ordered_tags = _ordered_tags(results_dict)
    for tag in ordered_tags:
        r = results_dict[tag]
        diag = r.get("diagnostics", {})
        stab = diag.get("stability", {})
        if stab.get("fallback_triggered", False):
            fallback_tags.append(tag)

    if fallback_tags:
        lines.append("> [!WARNING]")
        lines.append(f"> Step 2 stability selection fallback was triggered for tags: {', '.join([f'`{t}`' for t in fallback_tags])} (selected fewer than {MIN_FEATURE} clusters, fell back to top {MIN_FEATURE} clusters).")
        lines.append("")

    lines.append("Side-aware objective: `single` (legacy two-sided Tail IC), `long` "
                 "(top-only, `pred >= P85(pred)`), `short` (bot-only, `pred <= P15(pred)`). "
                 "Tail IC and lockbox Tail IC are side-aware; CV M1..M6 metrics stay two-sided.")
    lines.append("")
    lines.append("This report summarizes the performance and features of the remade `day-model` return predictors, "
                 "optimized using first-principles multi-metric objective functions and stability selection.")
    lines.append("")

    ordered_tags = _ordered_tags(results_dict)

    # ----- Lockbox summary -----
    lines.append("## Out-of-Sample Lockbox Performance (2024-03 to Last Day)")
    lines.append("")
    lines.append("| Tag | ETF | Side | Selected | Active | Model Type | Lockbox IC | Lockbox Tail IC | Tail IC Def |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
        feats_count = len(r["selected_features"])
        active_count = len(r.get("active_features", r["selected_features"]))
        model_type = r["best_params"]["model_type"]
        side = r.get("side", "single")
        ic = r.get("lockbox_overall_ic", float("nan"))
        tic = r.get("lockbox_tail_ic", float("nan"))
        ic_str = f"{ic:+.4f}" if not np.isnan(ic) else "N/A"
        tic_str = f"{tic:+.4f}" if not np.isnan(tic) else "N/A"
        lines.append(f"| {tag} | {r['etf']} | `{side}` | {feats_count} | {active_count} | `{model_type}` | {ic_str} | {tic_str} | {side} |")
    lines.append("")

    # ----- Detailed trial metrics -----
    lines.append("## Detailed Trial Metrics & Optimization Objectives")
    lines.append("")
    lines.append("CV fold metrics M1..M6 are two-sided for all sides (per side-aware spec). "
                 "V1..V4 weights: single `[0.40, 0.40, 0.15, 0.05]`; long/short `[0.45, 0.45, 0.10, 0.00]` "
                 "(V4 dropped, renormalized).")
    lines.append("")
    lines.append("| Tag | Side | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
        m = r["best_raw_metrics"]
        side = r.get("side", "single")
        lines.append(f"| {tag} | `{side}` | {m[0]:.4f} | {m[1]:+.4f} | {m[2]*100:.1f}% | {m[4]:.4f} | {m[5]*100:+.4f}% |")
    lines.append("")

    # ----- Model quality -----
    lines.append("## Model Quality & Generalization Diagnostics")
    lines.append("")
    lines.append("### Multi-Collinearity & Weight Concentration")
    lines.append("")
    lines.append("| Tag | Side | Raw X Cond | Reg kappa | Collinear Pairs (>=0.85) | Gini | Tail ESS | Tail ESS % |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
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
        lines.append(f"| {tag} | `{r.get('side','single')}` | {cond_raw_str} | {cond_reg_str} | {coll_str} | {gini_str} | {ess_str} | {ess_pct_str} |")
    lines.append("")

    # ----- Generalization gap -----
    lines.append("### Generalization Gap (CV vs Selection Val vs OOS)")
    lines.append("")
    lines.append("| Tag | Side | CV IC | Deflated CV IC | Sel Val IC | Deflated Val IC | OOS IC | IC Gen Gap | CV Mono | OOS Mono | Mono Gen Gap |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
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
        lines.append(f"| {tag} | `{r.get('side','single')}` | {cv_ic:+.4f} | {deflated_cv_ic_str} | {sel_val_ic_str} | {deflated_val_ic_str} | {oos_ic_str} | {ic_gap_str} | {cv_mono:+.4f} | {oos_mono_str} | {mono_gap_str} |")
    lines.append("")

    # ----- PBO & bootstrap -----
    lines.append("### Overfitting Diagnostics (PBO & Lockbox Bootstrap CIs)")
    lines.append("")
    lines.append("| Tag | Side | PBO | Perf Deg | OOS IC 95% CI | CV IC Target | IC Sig? | OOS Mono 95% CI | CV Mono | Mono Sig? |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
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
        ic_sig_str = "Noise" if ic_swallowed else ("Signal" if ic_swallowed is not None else "N/A")
        ci_mono = r.get("lockbox_mono_ci")
        ci_mono_str = f"[{ci_mono[0]:+.4f}, {ci_mono[1]:+.4f}]" if ci_mono is not None else "N/A"
        cv_mono = float(r["best_raw_metrics"][4])
        cv_mono_str = f"{cv_mono:+.4f}"
        mono_swallowed = r.get("lockbox_mono_swallowed")
        mono_sig_str = "Noise" if mono_swallowed else ("Signal" if mono_swallowed is not None else "N/A")
        lines.append(f"| {tag} | `{r.get('side','single')}` | {pbo_str} | {perf_deg_str} | {ci_ic_str} | {cv_ic_target_str} | **{ic_sig_str}** | {ci_mono_str} | {cv_mono_str} | **{mono_sig_str}** |")
    lines.append("")

    # ----- Selection metrics -----
    lines.append("### Feature Selection Metrics & Fallbacks")
    lines.append("")
    lines.append("| Tag | Side | Screen In | BH Pass | Screen FB? | Stability In | Stability Pass | Stability FB? | Kept |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
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
        lines.append(f"| {tag} | `{r.get('side','single')}` | {scr_in} | {scr_pass} | {scr_fb} | {stab_in} | {stab_pass} | {stab_fb} | **{kept}** |")
    lines.append("")

    # ----- Optuna pruning -----
    lines.append("### Optuna Main Study & Pruning Reasons")
    lines.append("")
    lines.append("| Tag | Side | Total | Completed | Pruned/Failed | M4 | M3 | M5 | M6 | ESS | Floor | Gini |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
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
        lines.append(f"| {tag} | `{r.get('side','single')}` | {tot} | {comp} | {pruned_failed} | {m4_p} | {m3_p} | {m5_p} | {m6_p} | {ess_p} | {floor_p} | {gini_p} |")
    lines.append("")

    # ----- Plateau -----
    lines.append("### Hyperparameter Plateau Selection")
    lines.append("")
    lines.append("| Tag | Side | Plateau Trial | Plateau Objective | Raw Best Trial | Raw Best Objective |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for tag in ordered_tags:
        r = results_dict[tag]
        plat_trial = r.get("plateau_trial")
        plat_val = r.get("plateau_val")
        raw_trial = r.get("raw_best_trial")
        raw_val = r.get("raw_best_val")
        plat_trial_str = str(plat_trial) if plat_trial is not None else "N/A"
        plat_val_str = f"{plat_val:+.4f}" if plat_val is not None else "N/A"
        raw_trial_str = str(raw_trial) if raw_trial is not None else "N/A"
        raw_val_str = f"{raw_val:+.4f}" if raw_val is not None else "N/A"
        lines.append(f"| {tag} | `{r.get('side','single')}` | {plat_trial_str} | {plat_val_str} | {raw_trial_str} | {raw_val_str} |")
    lines.append("")

    # ----- Per-tag section: ONE diagnostics figure (15 subplots) per ETF side -----
    lines.append("## Per-Tag Diagnostics (15-Panel Figure per Side)")
    lines.append("")
    lines.append("Each tag has ONE combined diagnostics figure with 15 subplots (5 rows x 3 cols):")
    lines.append("coefficients, OOS decile spread, all-data decile spread, side-tail return hist, "
                 "tail scatter, yearly overall IC, yearly side-aware tail IC, yearly tail hit rate, "
                 "tail vs rest mean, rolling 252d tail IC, rolling 252d overall IC, prediction dist, "
                 "tail equity curve, quantile decay, precision @ k.")
    lines.append("")
    for tag in ordered_tags:
        r = results_dict[tag]
        side = r.get("side", "single")
        etf = r["etf"]
        active_feats = r.get("active_features", r["selected_features"])
        lines.append(f"### {tag} ({etf}, side=`{side}`)")
        lines.append(f"- **Selected features**: {len(r['selected_features'])}")
        lines.append(f"- **Active features**: {len(active_feats)}")
        lines.append(f"- **Active**: " + ", ".join([f"`{f}`" for f in active_feats]))
        
        stopped_1 = r.get("features_stopped_by_step1", [])
        stopped_2 = r.get("features_stopped_by_step2", [])
        
        lines.append(f"- **Stopped by Step 1 (FDR Screening)** ({len(stopped_1)} features):")
        if stopped_1:
            lines.append("  <details>")
            lines.append(f"  <summary>Show {len(stopped_1)} features</summary>")
            lines.append("  ")
            lines.append("  " + ", ".join([f"`{f}`" for f in stopped_1]))
            lines.append("  </details>")
        else:
            lines.append("  None")
            
        lines.append(f"- **Stopped by Step 2 (Stability & VIF Pruning)** ({len(stopped_2)} features):")
        if stopped_2:
            lines.append("  <details>")
            lines.append(f"  <summary>Show {len(stopped_2)} features</summary>")
            lines.append("  ")
            lines.append("  " + ", ".join([f"`{f}`" for f in stopped_2]))
            lines.append("  </details>")
        else:
            lines.append("  None")
        lines.append("")
        plot_file = r.get("diagnostics_plot") or f"diagnostics_{etf}_{side}.png"
        if (PLOTS_DIR / plot_file).exists():
            lines.append(f"![Diagnostics {tag}](plots/{plot_file})")
        else:
            lines.append(f"_(diagnostics plot missing: plots/{plot_file})_")
        lines.append("")
        lines.append("")

    # ----- Methodology -----
    lines.append("## Methodology Overview")
    lines.append("1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).")
    lines.append("2. **Selection Validation Split**: Six non-contiguous 3-month blocks carved out from the working set, partitioned into 4 inner (tuning) + 2 outer (held-out) blocks, with a 10-day embargo.")
    lines.append("3. **BH-FDR Screening**: Robust marginal Spearman correlation at FDR = 0.15 on selection train.")
    lines.append("4. **Hierarchical Clustering**: Groups collinear features (|r| >= 0.75).")
    lines.append("5. **Cluster Stability Selection + VIF Pruning**: B=100 subsamples, pi=0.60 cluster threshold, then VIF <= 10 pruning.")
    lines.append("6. **Weighted Fitting**: Sample weights w(y) = |y|^k.")
    lines.append("7. **Side-Aware Optuna Objective**:")
    lines.append("   - `single` (legacy): Tail IC two-sided (top10% U bot10%). Weights V1..V4 = [0.40, 0.40, 0.15, 0.05].")
    lines.append("   - `long`: Tail IC top-only (`pred >= P85(pred)`). Weights [0.35, 0.50, 0.15, 0.00] (V4 dropped).")
    lines.append("   - `short`: Tail IC bot-only (`pred <= P15(pred)`). Weights [0.35, 0.50, 0.15, 0.00] (V4 dropped).")
    lines.append("   - CV fold kill-switches (M1..M6: hit rate, monotonicity, spread, ESS, Gini) stay **two-sided** for all sides.")
    lines.append("8. **Deflated Objective + Plateau Selection**: Running Lopez de Prado deflation; final trial chosen via plateau search (r=0.25).")
    lines.append("9. **15-Panel Diagnostics Figure per Tag**: One combined PNG (`diagnostics_{etf}_{side}.png`) with 15 subplots, saved to `day-model/plots/` and embedded above.")
    lines.append("")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))


# ============================================================
# Rolling Report
# ============================================================
def _quarter_label(lockbox_date: str) -> str:
    dt = pd.Timestamp(lockbox_date)
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}Q{q}"


def _load_rolling_results() -> dict:
    """Load all rolling results from ROLLING_DATA_DIR, grouped by lockbox_date."""
    out = {}
    if not ROLLING_DATA_DIR.exists():
        return out
    for p in sorted(ROLLING_DATA_DIR.glob("results_*.json")):
        try:
            with open(p) as f:
                r = json.load(f)
            lb = r.get("lockbox_date", "")
            if lb not in out:
                out[lb] = {}
            out[lb][r.get("tag", "")] = r
        except Exception as e:
            print(f"  [WARNING] Failed to load {p.name}: {e}")
    return out


def _process_rolling_tag(tag: str, r: dict, quarter_dir: Path):
    """Process ONE rolling tag: load model, predict on OOS window, compute metrics, plot."""
    import joblib as _jlib
    from scipy.stats import spearmanr as _sr

    etf = r["etf"]
    side = r.get("side", "single")
    lb_date = r.get("lockbox_date", LOCKBOX_DATE)
    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"

    if not (model_path.exists() and scaler_path.exists()):
        return tag, None, f"missing model/scaler files"

    cached = _load_etf_features(etf)
    if cached is None:
        return tag, None, "missing features parquet"

    df, _ = cached
    try:
        model = _jlib.load(model_path)
        scaler_meta = _jlib.load(scaler_path)
        selected_features = scaler_meta["selected_features"]
        scaler = scaler_meta["scaler"]
        target_col = scaler_meta.get("target", TARGET)

        y = df[target_col].values.astype(np.float32)
        y_scaled = (y * 100.0).astype(np.float32)
        X_df = df[selected_features].ffill()
        col_med = X_df.median().fillna(0.0)
        X_df = X_df.fillna(col_med)
        X = X_df.values.astype(np.float32)

        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled).astype(np.float32)

        # OOS window: lockbox to lockbox + 3 months (or end of data)
        lb_ts = pd.Timestamp(lb_date)
        oos_end = lb_ts + pd.DateOffset(months=3)
        oos_mask = (df["date"] >= lb_ts) & (df["date"] < oos_end)
        all_post_lb = df["date"] >= lb_ts

        dates_all = df["date"].values
        y_oos = y_scaled[oos_mask]
        pred_oos = preds[oos_mask]
        dates_oos = df["date"][oos_mask].values
        y_post = y_scaled[all_post_lb]
        pred_post = preds[all_post_lb]

        # OOS metrics
        oos_ic = float(_sr(pred_oos, y_oos)[0]) if len(y_oos) >= 5 else 0.0
        if np.isnan(oos_ic):
            oos_ic = 0.0
        oos_tail_ic = side_tail_ic(y_oos, pred_oos, side)
        oos_mono = compute_decile_monotonicity(y_oos, pred_oos)

        r["oos_ic"] = oos_ic
        r["oos_tail_ic"] = oos_tail_ic
        r["oos_mono"] = oos_mono
        r["n_oos_samples"] = int(len(y_oos))

        # Persist updated results
        with open(ROLLING_DATA_DIR / f"results_{tag}.json", "w") as f_json:
            json.dump(r, f_json, indent=2, default=str)

        # Render diagnostic plot for this quarter
        quarter_dir.mkdir(parents=True, exist_ok=True)
        ql = _quarter_label(lb_date)
        extra_stats = {
            "IC": float(oos_ic),
            f"TailIC[{side}]": float(oos_tail_ic),
            "Mono": float(oos_mono),
        }

        fig, axes = plt.subplots(5, 3, figsize=(22, 25))
        axes_flat = axes.flatten()
        stat_txt = " | ".join(f"{k}={v:+.4f}" if isinstance(v, float) else f"{k}={v}"
                              for k, v in extra_stats.items())
        fig.suptitle(f"Rolling {ql} — {etf} (side={side})  |  {stat_txt}", fontsize=14, y=0.995)

        _render_coefs(axes_flat[0], model, selected_features)
        _render_decile_oos(axes_flat[1], y_oos, pred_oos)
        _render_decile_all(axes_flat[2], y_post, pred_post)
        _render_tail_hist(axes_flat[3], y_oos, pred_oos, side)
        _render_tail_scatter(axes_flat[4], y_oos, pred_oos, side)
        _render_yearly_overall_ic(axes_flat[5], dates_oos, y_oos, pred_oos)
        _render_yearly_tail_ic(axes_flat[6], dates_oos, y_oos, pred_oos, side)
        _render_yearly_hit_rate(axes_flat[7], dates_oos, y_oos, pred_oos, side)
        _render_tail_vs_rest(axes_flat[8], y_oos, pred_oos, side)
        _render_rolling_tail_ic(axes_flat[9], dates_oos, y_oos, pred_oos, side)
        _render_rolling_overall_ic(axes_flat[10], dates_oos, y_oos, pred_oos)
        _render_pred_dist(axes_flat[11], pred_post, side)
        _render_tail_equity(axes_flat[12], dates_oos, y_oos, pred_oos, side)
        _render_quantile_decay(axes_flat[13], y_post, pred_post)
        _render_precision_at_k(axes_flat[14], y_oos, pred_oos, side)

        fig.tight_layout(rect=(0, 0, 1, 0.985))
        fname = f"diagnostics_{tag}.png"
        fig.savefig(quarter_dir / fname, dpi=110)
        plt.close(fig)

        return tag, fname, f"IC={oos_ic:+.4f} TailIC={oos_tail_ic:+.4f}"
    except Exception as ex:
        import traceback
        return tag, None, f"FAILED: {ex}\n{traceback.format_exc()}"


def main_rolling(quarter_filter: str = None):
    """Generate rolling report with per-quarter diagnostic plots."""
    print("Generating rolling day-model report...")
    all_results = _load_rolling_results()
    if not all_results:
        print("  [ERROR] No rolling results found in", ROLLING_DATA_DIR)
        print("  Run `python3 day-model/train_rolling.py -e all` first.")
        return

    ROLLING_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Filter quarters if requested
    if quarter_filter:
        rq = quarter_filter.upper()
        y = int(rq[:4])
        q = int(rq[5])
        m = (q - 1) * 3 + 1
        target_date = f"{y}-{m:02d}-01"
        all_results = {k: v for k, v in all_results.items() if k == target_date}

    # Process each quarter
    for lb_date in sorted(all_results.keys()):
        ql = _quarter_label(lb_date)
        quarter_dir = ROLLING_PLOTS_DIR / ql
        quarter_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nProcessing {ql} ({lb_date}): {len(all_results[lb_date])} models")

        for tag, r in sorted(all_results[lb_date].items()):
            tag_out, fname, msg = _process_rolling_tag(tag, r, quarter_dir)
            print(f"  {tag_out}: {msg}")

    # Generate summary report using train_rolling's warning system + report generator
    try:
        sys.path.insert(0, str(HERE))
        from train_rolling import evaluate_warnings, generate_rolling_report
        warnings_dict = evaluate_warnings(all_results)
        generate_rolling_report(all_results, warnings_dict)
    except ImportError as e:
        print(f"  [WARNING] Could not import train_rolling for warning system: {e}")
        print("  Report generation incomplete.")

    print("\nRolling report generation complete.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Generate day-model reports")
    ap.add_argument("--rolling", action="store_true",
                    help="Generate rolling report instead of static report")
    ap.add_argument("-q", "--quarter", default=None,
                    help="Filter to single quarter (e.g. 2024Q1)")
    args = ap.parse_args()

    if args.rolling or args.quarter:
        main_rolling(quarter_filter=args.quarter)
    else:
        main()
