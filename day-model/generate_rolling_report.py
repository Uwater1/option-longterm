"""
Rolling Day-Model Comprehensive Report Generator.

Loads existing trained rolling models and evaluates them with:
- IC metrics (Spearman IC, Tail IC, decile monotonicity)
- Simulated strategy returns (P&L, Sharpe, win rate, max drawdown)
- Cross-quarter IC trajectory & feature stability
- Model health warnings (pre-lockbox only)
- Per-quarter diagnostic plots (15-panel)

Usage:
    python3 day-model/generate_rolling_report.py                  # All quarters, all ETFs
    python3 day-model/generate_rolling_report.py -q 2024Q1       # Single quarter
    python3 day-model/generate_rolling_report.py -e 300          # Single ETF
    python3 day-model/generate_rolling_report.py --no-plots       # Skip plot generation
    python3 day-model/generate_rolling_report.py --thr 80         # Signal threshold (default 80th pct)
"""
import argparse
import json
import os
import sys
import warnings
import bisect
from pathlib import Path

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

from train_model import (
    ROLLING_QUARTERS,
    ROLLING_DATA_DIR,
    ROLLING_MODELS_DIR,
    ROLLING_PLOTS_DIR,
    DATA_DIR,
    MODELS_DIR,
    quarter_label,
    rolling_tag,
)
from generate_report import (
    spearman_ic,
    side_tail_ic,
    compute_decile_monotonicity,
    side_tail_mask,
    _render_coefs,
    _render_decile_oos,
    _render_decile_all,
    _render_tail_hist,
    _render_tail_scatter,
    _render_yearly_overall_ic,
    _render_yearly_tail_ic,
    _render_yearly_hit_rate,
    _render_tail_vs_rest,
    _render_rolling_tail_ic,
    _render_rolling_overall_ic,
    _render_pred_dist,
    _render_tail_equity,
    _render_quantile_decay,
    _render_precision_at_k,
    SIDE_CONFIG,
)

REPORT_PATH = HERE / "ROLLING_REPORT.md"

ETF_ORDER = ["300ETF", "500ETF", "588000ETF", "159915ETF", "50ETF"]
TARGET = "trade_return"
DEFAULT_COST_BPS = 15.0
DEFAULT_SIGNAL_THR = 90.0  # percentile threshold for signal generation


# ============================================================
# Data loading
# ============================================================
def load_rolling_results(early: bool = False) -> dict:
    """Load all rolling results JSON grouped by lockbox_date -> {tag: results_dict}."""
    out = {}
    if not ROLLING_DATA_DIR.exists():
        return out
    pattern = "results_*_early.json" if early else "results_*.json"
    for p in sorted(ROLLING_DATA_DIR.glob(pattern)):
        if not early and p.name.endswith("_early.json"):
            continue
        try:
            with open(p) as f:
                r = json.load(f)
            lb = r.get("lockbox_date", "")
            tag = r.get("tag", "")
            if not lb or not tag:
                continue
            out.setdefault(lb, {})[tag] = r
        except Exception as e:
            print(f"  [WARN] Failed to load {p.name}: {e}")
    return out


def _load_features(etf: str, early: bool = False, _cache={}):
    """Load features parquet once per ETF (cached)."""
    cache_key = (etf, early)
    if cache_key in _cache:
        return _cache[cache_key]
    fname = f"features_{etf}_early.parquet" if early else f"features_{etf}.parquet"
    path = DATA_DIR / fname
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    _cache[cache_key] = df
    return df


# ============================================================
# Strategy simulation (per model OOS window)
# ============================================================
def expanding_pct_rank(series: pd.Series, min_periods: int = 60) -> pd.Series:
    """Walk-forward percentile rank. Output in [0, 1]."""
    vals = series.values
    n = len(vals)
    out = np.full(n, np.nan, dtype=float)
    sorted_buf = []
    for i in range(n):
        v = vals[i]
        if np.isnan(v):
            continue
        if len(sorted_buf) >= min_periods:
            out[i] = bisect.bisect_left(sorted_buf, v) / len(sorted_buf)
        bisect.insort(sorted_buf, float(v))
    return pd.Series(out, index=series.index)


def simulate_strategy(pred_series: pd.Series, actual_returns: pd.Series,
                      signal_thr: float = 80.0, cost_bps: float = 15.0,
                      side: str = "long") -> dict:
    """Simple strategy simulation using within-window percentile signals.

    For rolling models with short OOS windows (~63 days), uses simple
    percentile rank within the OOS window (no expanding warmup needed).

    For 'long': go long when pred_rank >= threshold.
    For 'short': go short (profit = -actual_return) when pred_rank >= threshold.
    For 'single': long on top tail, short on bottom tail.

    Returns dict with n_trades, total_ret, sharpe, win_rate, max_dd, mean_ret.
    """
    n = len(pred_series)
    if n < 10:
        return {"n_trades": 0, "total_ret": 0.0, "sharpe": 0.0,
                "win_rate": 0.0, "max_dd": 0.0, "mean_ret": 0.0}

    # Use simple within-window rank (no warmup needed)
    pred_vals = pred_series.values.astype(np.float64)
    rank = pd.Series(pred_vals, index=pred_series.index).rank(pct=True)

    thr = signal_thr / 100.0
    cost = cost_bps / 1e4

    trades_ret = []
    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])

    if cfg["tail_def"] == "top_only":
        mask = rank >= thr
        for i in np.where(mask.values)[0]:
            trades_ret.append(float(actual_returns.iloc[i]) - cost)
    elif cfg["tail_def"] == "bot_only":
        neg_rank = 1.0 - rank
        mask = neg_rank >= thr
        for i in np.where(mask.values)[0]:
            trades_ret.append(float(-actual_returns.iloc[i]) - cost)
    else:
        top_mask = rank >= thr
        bot_mask = rank <= (1.0 - thr)
        for i in np.where(top_mask.values)[0]:
            trades_ret.append(float(actual_returns.iloc[i]) - cost)
        for i in np.where(bot_mask.values)[0]:
            trades_ret.append(float(-actual_returns.iloc[i]) - cost)

    if not trades_ret:
        return {"n_trades": 0, "total_ret": 0.0, "sharpe": 0.0,
                "win_rate": 0.0, "max_dd": 0.0, "mean_ret": 0.0}

    rets = np.array(trades_ret)
    n_t = len(rets)
    win_rate = float((rets > 0).mean())
    total_ret = float(rets.sum())
    mean_ret = float(rets.mean())
    std_ret = float(rets.std(ddof=1)) if n_t > 1 else 0.0
    sharpe = mean_ret / std_ret * np.sqrt(252) if std_ret > 1e-8 else 0.0

    cum = np.cumsum(rets)
    peak = np.maximum.accumulate(cum)
    max_dd = float(np.max(peak - cum)) if len(cum) > 0 else 0.0

    return {
        "n_trades": n_t,
        "total_ret": total_ret,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "max_dd": max_dd,
        "mean_ret": mean_ret,
    }


# ============================================================
# Per-model evaluation
# ============================================================
def evaluate_model(tag: str, r: dict, signal_thr: float, cost_bps: float, early: bool = False) -> dict:
    """Load model, predict OOS, compute IC + strategy metrics. Returns enriched results."""
    etf = r["etf"]
    side = r.get("side", "single")
    lb_date = r.get("lockbox_date", "")

    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"

    if not (model_path.exists() and scaler_path.exists()):
        return {"error": f"missing model/scaler for {tag}"}

    df = _load_features(etf, early=early)
    if df is None:
        return {"error": f"missing features for {etf}"}

    try:
        model = joblib.load(model_path)
        scaler_meta = joblib.load(scaler_path)
        sel_feats = scaler_meta["selected_features"]
        scaler = scaler_meta["scaler"]
        target_col = scaler_meta.get("target", TARGET)

        # Predict all dates
        X_df = df[sel_feats].ffill()
        X_df = X_df.fillna(X_df.median().fillna(0.0))
        X = X_df.values.astype(np.float32)
        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled).astype(np.float64)

        y = df[target_col].values.astype(np.float64)
        y_scaled = y * 100.0  # match training target scaling
        dates = df["date"].values

        # OOS window: lockbox to lockbox + 3 months
        lb_ts = pd.Timestamp(lb_date)
        oos_end = lb_ts + pd.DateOffset(months=3)
        oos_mask = (df["date"] >= lb_ts) & (df["date"] < oos_end)

        y_oos = y_scaled[oos_mask]
        pred_oos = preds[oos_mask]
        dates_oos = dates[oos_mask]

        if len(y_oos) < 5:
            return {"error": f"insufficient OOS data ({len(y_oos)} rows) for {tag}"}

        # IC metrics
        oos_ic = spearman_ic(y_oos, pred_oos)
        oos_tail_ic = side_tail_ic(y_oos, pred_oos, side)
        oos_mono = compute_decile_monotonicity(y_oos, pred_oos)

        # Strategy simulation
        pred_series = pd.Series(pred_oos, index=range(len(pred_oos)))
        actual_series = pd.Series(y_oos, index=range(len(y_oos)))
        strat = simulate_strategy(pred_series, actual_series, signal_thr, cost_bps, side)

        return {
            "oos_ic": oos_ic,
            "oos_tail_ic": oos_tail_ic,
            "oos_mono": oos_mono,
            "n_oos": len(y_oos),
            **{f"strat_{k}": v for k, v in strat.items()},
        }
    except Exception as ex:
        import traceback
        return {"error": f"{ex}\n{traceback.format_exc()}"}


# ============================================================
# Warning System (pre-lockbox validation metrics only)
# ============================================================
def evaluate_warnings(all_results: dict) -> dict:
    """Evaluate model health using ONLY pre-lockbox validation metrics."""
    warnings_out = {}
    prev_outer_ic = {}

    for quarter in sorted(all_results.keys()):
        for tag, res in all_results[quarter].items():
            outer_ic = res.get("selection_val_outer_overall_ic", 0) or 0
            outer_tail_ic = res.get("selection_val_outer_tail_ic", 0) or 0

            status = "OK"
            reasons = []

            if outer_ic < 0:
                reasons.append(f"outer_IC={outer_ic:+.4f}<0")
            if outer_tail_ic < 0:
                reasons.append(f"outer_tail_IC={outer_tail_ic:+.4f}<0")

            etf = res.get("etf", "")
            side = res.get("side", "single")
            prev = prev_outer_ic.get((etf, side))
            if prev is not None and prev > 0.005 and outer_ic < prev * 0.5:
                decay_pct = 100 * (1 - outer_ic / prev)
                reasons.append(f"IC_decay={decay_pct:.0f}%>50%")

            if len(reasons) >= 2:
                status = "ALERT"
            elif any("decay" in r for r in reasons):
                status = "ALERT"
            elif reasons:
                status = "WARNING"

            warnings_out[(quarter, tag)] = {"status": status, "reasons": reasons}
            prev_outer_ic[(etf, side)] = outer_ic

    return warnings_out


# ============================================================
# Diagnostic plots (per-quarter subdirectories)
# ============================================================
def render_quarter_diagnostics(tag: str, r: dict, quarter_dir: Path, early: bool = False) -> str | None:
    """Render 15-panel diagnostic figure for one rolling model. Returns filename or None."""
    etf = r["etf"]
    side = r.get("side", "single")
    lb_date = r.get("lockbox_date", "")

    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"
    if not (model_path.exists() and scaler_path.exists()):
        return None

    df = _load_features(etf, early=early)
    if df is None:
        return None

    try:
        model = joblib.load(model_path)
        scaler_meta = joblib.load(scaler_path)
        sel_feats = scaler_meta["selected_features"]
        scaler = scaler_meta["scaler"]
        target_col = scaler_meta.get("target", TARGET)

        X_df = df[sel_feats].ffill().fillna(df[sel_feats].median().fillna(0.0))
        X = X_df.values.astype(np.float32)
        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled).astype(np.float64)

        y = df[target_col].values.astype(np.float64) * 100.0
        dates = df["date"].values

        lb_ts = pd.Timestamp(lb_date)
        oos_end = lb_ts + pd.DateOffset(months=3)
        oos_mask = (df["date"] >= lb_ts) & (df["date"] < oos_end)
        all_post = df["date"] >= lb_ts

        y_oos, pred_oos, dates_oos = y[oos_mask], preds[oos_mask], dates[oos_mask]
        y_post, pred_post = y[all_post], preds[all_post]

        if len(y_oos) < 5:
            return None

        ql = quarter_label(lb_date)
        oos_ic = spearman_ic(y_oos, pred_oos)
        oos_tail_ic = side_tail_ic(y_oos, pred_oos, side)
        oos_mono = compute_decile_monotonicity(y_oos, pred_oos)

        fig, axes = plt.subplots(5, 3, figsize=(22, 25))
        ax = axes.flatten()
        stat_txt = f"IC={oos_ic:+.4f} | TailIC[{side}]={oos_tail_ic:+.4f} | Mono={oos_mono:+.4f}"
        fig.suptitle(f"Rolling {ql} — {etf} (side={side})  |  {stat_txt}", fontsize=14, y=0.995)

        _render_coefs(ax[0], model, sel_feats)
        _render_decile_oos(ax[1], y_oos, pred_oos)
        _render_decile_all(ax[2], y_post, pred_post)
        _render_tail_hist(ax[3], y_oos, pred_oos, side)
        _render_tail_scatter(ax[4], y_oos, pred_oos, side)
        _render_yearly_overall_ic(ax[5], dates_oos, y_oos, pred_oos)
        _render_yearly_tail_ic(ax[6], dates_oos, y_oos, pred_oos, side)
        _render_yearly_hit_rate(ax[7], dates_oos, y_oos, pred_oos, side)
        _render_tail_vs_rest(ax[8], y_oos, pred_oos, side)
        _render_rolling_tail_ic(ax[9], dates_oos, y_oos, pred_oos, side)
        _render_rolling_overall_ic(ax[10], dates_oos, y_oos, pred_oos)
        _render_pred_dist(ax[11], pred_post, side)
        _render_tail_equity(ax[12], dates_oos, y_oos, pred_oos, side)
        _render_quantile_decay(ax[13], y_post, pred_post)
        _render_precision_at_k(ax[14], y_oos, pred_oos, side)

        fig.tight_layout(rect=(0, 0, 1, 0.985))
        quarter_dir.mkdir(parents=True, exist_ok=True)
        fname = f"diagnostics_{tag}.png"
        fig.savefig(quarter_dir / fname, dpi=110)
        plt.close(fig)
        return fname
    except Exception as ex:
        print(f"  [WARN] Plot failed for {tag}: {ex}")
        return None


# ============================================================
# Report generator
# ============================================================
def generate_report(all_results: dict, eval_metrics: dict, warnings_dict: dict,
                    signal_thr: float, cost_bps: float, early: bool = False):
    """Generate comprehensive ROLLING_REPORT.md."""
    L = []
    L.append("# Day-Model Rolling Strategy Report")
    L.append("")
    L.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    L.append(f"Quarters: {sorted(all_results.keys())}")
    L.append(f"Window: 6 years (rolling)")
    L.append(f"Signal threshold: {signal_thr}th percentile")
    L.append(f"Transaction cost: {cost_bps} bps")
    if early:
        L.append(f"Target: `trade_return` = log(close@13:05 / open@10:05) (early target)")
    else:
        L.append(f"Target: `trade_return` = log(close@14:35 / open@10:05)")
    L.append("")

    # === Strategy Performance Summary ===
    L.append("## Strategy Performance (OOS Simulated)")
    L.append("")
    L.append("Each model is evaluated on its 3-month OOS deployment window using within-window percentile rank signals.")
    L.append("")
    L.append("| Quarter | ETF | Side | Trades | WinRate | Total Ret | Sharpe | MaxDD | Mean Ret/Trade |")
    L.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for quarter in sorted(all_results.keys()):
        ql = quarter_label(quarter)
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            etf = res.get("etf", "")
            side = res.get("side", "single")
            ev = eval_metrics.get(quarter, {}).get(tag, {})
            if "error" in ev:
                L.append(f"| {ql} | {etf} | `{side}` | ERR | - | - | - | - | {ev['error'][:40]} |")
                continue
            n_t = ev.get("strat_n_trades", 0)
            wr = ev.get("strat_win_rate", 0)
            tr = ev.get("strat_total_ret", 0)
            sh = ev.get("strat_sharpe", 0)
            dd = ev.get("strat_max_dd", 0)
            mr = ev.get("strat_mean_ret", 0)
            L.append(f"| {ql} | {etf} | `{side}` | {n_t} | {wr:.1%} | {tr*1e4:+.0f}bps | {sh:+.2f} | {dd*1e4:.0f}bps | {mr*1e4:+.1f}bps |")
    L.append("")

    # === Portfolio-level aggregation ===
    L.append("### Portfolio Aggregation (Equal-Weight per Day)")
    L.append("")
    L.append("Aggregated daily returns across all ETFs/sides, equal-weighted on active signal days.")
    L.append("")

    # Collect all daily strategy returns for portfolio aggregation
    port_daily = {}  # {date: list of daily returns}
    for quarter in sorted(all_results.keys()):
        lb_ts = pd.Timestamp(quarter)
        oos_end = lb_ts + pd.DateOffset(months=3)
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            etf = res.get("etf", "")
            side = res.get("side", "single")
            ev = eval_metrics.get(quarter, {}).get(tag, {})
            if "error" in ev or ev.get("strat_n_trades", 0) == 0:
                continue
            # Reconstruct daily returns for aggregation
            try:
                daily_rets = _compute_daily_returns(tag, res, signal_thr, cost_bps, side, early=early)
                for dt, ret in daily_rets.items():
                    port_daily.setdefault(dt, []).append(ret)
            except Exception:
                pass

    if port_daily:
        port_dates = sorted(port_daily.keys())
        port_rets = np.array([np.mean(port_daily[d]) for d in port_dates])
        port_total = float(port_rets.sum())
        port_sharpe = float(port_rets.mean() / port_rets.std(ddof=1) * np.sqrt(252)) if len(port_rets) > 1 and port_rets.std() > 1e-8 else 0.0
        port_wr = float((port_rets > 0).mean())
        cum = np.cumsum(port_rets)
        peak = np.maximum.accumulate(cum)
        port_dd = float(np.max(peak - cum)) if len(cum) > 0 else 0.0

        L.append(f"| Metric | Value |")
        L.append(f"| :--- | :---: |")
        L.append(f"| Active Days | {len(port_dates)} |")
        L.append(f"| Win Rate | {port_wr:.1%} |")
        L.append(f"| Total Return | {port_total*1e4:+.0f} bps |")
        L.append(f"| Sharpe | {port_sharpe:+.2f} |")
        L.append(f"| Max Drawdown | {port_dd*1e4:.0f} bps |")
        L.append(f"| Mean Daily Ret | {port_rets.mean()*1e4:+.2f} bps |")
        L.append("")

        # Yearly breakdown
        yearly = {}
        for d, r in zip(port_dates, port_rets):
            yr = d.year
            yearly.setdefault(yr, []).append(r)
        if yearly:
            L.append("#### Yearly Breakdown")
            L.append("")
            L.append("| Year | Days | WinRate | P&L | Sharpe |")
            L.append("| :--- | :---: | :---: | :---: | :---: |")
            for yr in sorted(yearly.keys()):
                yr_rets = np.array(yearly[yr])
                yr_wr = float((yr_rets > 0).mean())
                yr_pnl = float(yr_rets.sum())
                yr_sh = float(yr_rets.mean() / yr_rets.std(ddof=1) * np.sqrt(252)) if len(yr_rets) > 1 and yr_rets.std() > 1e-8 else 0.0
                L.append(f"| {yr} | {len(yr_rets)} | {yr_wr:.1%} | {yr_pnl*1e4:+.0f}bps | {yr_sh:+.2f} |")
            L.append("")
    else:
        L.append("_(No strategy returns available for aggregation.)_")
        L.append("")

    # === IC Metrics ===
    L.append("## OOS IC Metrics (Per Model)")
    L.append("")
    L.append("| Quarter | ETF | Side | N_OOS | Spearman IC | Tail IC | Decile Mono |")
    L.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
    for quarter in sorted(all_results.keys()):
        ql = quarter_label(quarter)
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            etf = res.get("etf", "")
            side = res.get("side", "single")
            ev = eval_metrics.get(quarter, {}).get(tag, {})
            if "error" in ev:
                L.append(f"| {ql} | {etf} | `{side}` | - | ERR | ERR | ERR |")
                continue
            n_oos = ev.get("n_oos", 0)
            L.append(f"| {ql} | {etf} | `{side}` | {n_oos} | {ev.get('oos_ic', 0):+.4f} | {ev.get('oos_tail_ic', 0):+.4f} | {ev.get('oos_mono', 0):+.4f} |")
    L.append("")

    # === Model Health ===
    L.append("## Model Health Warnings")
    L.append("")
    L.append("| Quarter | Tag | Outer IC | Outer Tail IC | Deflated Val IC | Status | Reason |")
    L.append("| :--- | :--- | :---: | :---: | :---: | :---: | :--- |")
    for quarter in sorted(all_results.keys()):
        ql = quarter_label(quarter)
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            outer_ic = res.get("selection_val_outer_overall_ic", 0) or 0
            outer_tail_ic = res.get("selection_val_outer_tail_ic", 0) or 0
            deflated_ic = res.get("deflated_val_ic", 0) or 0
            w = warnings_dict.get((quarter, tag), {"status": "OK", "reasons": []})
            reason = ", ".join(w["reasons"]) if w["reasons"] else "-"
            L.append(f"| {ql} | {tag} | {outer_ic:+.4f} | {outer_tail_ic:+.4f} | {deflated_ic:+.4f} | {w['status']} | {reason} |")
    L.append("")
    L.append("### Warning Levels")
    L.append("")
    L.append("- **OK**: Outer validation IC >= 0 and no significant decay.")
    L.append("- **WARNING**: Outer IC < 0 OR outer Tail IC < 0 (single metric negative).")
    L.append("- **ALERT**: Both outer IC and Tail IC negative, OR IC decay > 50% vs previous quarter.")
    L.append("")

    # === IC Timeline by ETF ===
    L.append("## IC & Return Timeline by ETF")
    L.append("")
    for etf in ETF_ORDER:
        for side_label in ["long", "short"]:
            rows = []
            for quarter in sorted(all_results.keys()):
                for tag, res in all_results[quarter].items():
                    if res.get("etf") == etf and res.get("side") == side_label:
                        ev = eval_metrics.get(quarter, {}).get(tag, {})
                        rows.append((quarter, tag, res, ev))
            if not rows:
                continue

            L.append(f"### {etf} ({side_label})")
            L.append("")
            L.append("| Quarter | IC | Tail IC | Trades | P&L | Sharpe | WR |")
            L.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
            for quarter, tag, res, ev in rows:
                ql = quarter_label(quarter)
                ic = ev.get("oos_ic", 0) if "error" not in ev else 0
                tic = ev.get("oos_tail_ic", 0) if "error" not in ev else 0
                nt = ev.get("strat_n_trades", 0) if "error" not in ev else 0
                pnl = ev.get("strat_total_ret", 0) * 1e4 if "error" not in ev else 0
                sh = ev.get("strat_sharpe", 0) if "error" not in ev else 0
                wr = ev.get("strat_win_rate", 0) if "error" not in ev else 0
                L.append(f"| {ql} | {ic:+.4f} | {tic:+.4f} | {nt} | {pnl:+.0f}bps | {sh:+.2f} | {wr:.0%} |")
            L.append("")

    # === Feature Stability ===
    L.append("## Feature Stability Across Quarters")
    L.append("")
    for etf in ETF_ORDER:
        for side_label in ["long", "short"]:
            etf_features = {}
            for quarter in sorted(all_results.keys()):
                for tag, res in all_results[quarter].items():
                    if res.get("etf") == etf and res.get("side") == side_label:
                        active = set(res.get("active_features", []))
                        etf_features[quarter_label(quarter)] = active
            if not etf_features:
                continue

            all_feats = set()
            for s in etf_features.values():
                all_feats |= s
            if not all_feats:
                continue

            L.append(f"### {etf} ({side_label})")
            L.append("")
            qls = sorted(etf_features.keys())
            header = "| Feature | " + " | ".join(qls) + " | Freq |"
            sep = "| :--- | " + " | ".join([":---:" for _ in qls]) + " | :---: |"
            L.append(header)
            L.append(sep)

            feat_counts = {}
            for f in sorted(all_feats):
                row = [f]
                count = 0
                for ql in qls:
                    present = f in etf_features[ql]
                    row.append("Y" if present else "-")
                    if present:
                        count += 1
                row.append(f"{count}/{len(qls)}")
                feat_counts[f] = count
                L.append("| " + " | ".join(row) + " |")
            L.append("")

    # === Methodology ===
    L.append("## Methodology")
    L.append("")
    L.append("1. **Rolling Window**: Each model trains on 6 years of data before the lockbox date.")
    L.append("2. **OOS Evaluation**: Each model is tested on its 3-month deployment window (lockbox to lockbox+3m).")
    L.append("3. **Signal Generation**: Within-window percentile rank of model predictions; signal fires when rank >= threshold.")
    L.append("4. **Strategy Returns**: On signal days, P&L = actual `trade_return` (long) or `-trade_return` (short), minus transaction cost.")
    L.append("5. **Warning System**: Based on pre-lockbox outer validation IC only (no OOS peeking).")
    L.append("6. **Artifacts**: Models in `models/rolling/`, results in `data/rolling/`, plots in `plots/rolling/`.")
    L.append("")

    report_text = "\n".join(L)
    report_file = HERE / "ROLLING_REPORT_early.md" if early else REPORT_PATH
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nRolling report written to: {report_file}")
    return report_text


def _compute_daily_returns(tag: str, r: dict, signal_thr: float, cost_bps: float,
                           side: str, early: bool = False) -> dict:
    """Reconstruct daily returns for portfolio aggregation. Returns {date: return}."""
    etf = r["etf"]
    lb_date = r.get("lockbox_date", "")
    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"

    df = _load_features(etf, early=early)
    if df is None or not (model_path.exists() and scaler_path.exists()):
        return {}

    model = joblib.load(model_path)
    scaler_meta = joblib.load(scaler_path)
    sel_feats = scaler_meta["selected_features"]
    scaler = scaler_meta["scaler"]
    target_col = scaler_meta.get("target", TARGET)

    X_df = df[sel_feats].ffill().fillna(df[sel_feats].median().fillna(0.0))
    X = X_df.values.astype(np.float32)
    preds = model.predict(scaler.transform(X)).astype(np.float64)

    y = df[target_col].values.astype(np.float64) * 100.0
    dates = pd.to_datetime(df["date"])

    lb_ts = pd.Timestamp(lb_date)
    oos_end = lb_ts + pd.DateOffset(months=3)
    oos_mask = (dates >= lb_ts) & (dates < oos_end)

    pred_oos = pd.Series(preds[oos_mask], index=dates[oos_mask])
    y_oos = pd.Series(y[oos_mask], index=dates[oos_mask])

    rank = pd.Series(pred_oos.values, index=pred_oos.index).rank(pct=True)
    thr = signal_thr / 100.0
    cost = cost_bps / 1e4

    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    daily = {}

    if cfg["tail_def"] == "top_only":
        for dt, rk in rank.items():
            if rk >= thr:
                daily[dt] = float(y_oos[dt]) - cost
    elif cfg["tail_def"] == "bot_only":
        for dt, rk in rank.items():
            if (1.0 - rk) >= thr:
                daily[dt] = float(-y_oos[dt]) - cost
    else:
        for dt, rk in rank.items():
            if rk >= thr:
                daily[dt] = float(y_oos[dt]) - cost
            elif rk <= (1.0 - thr):
                daily[dt] = float(-y_oos[dt]) - cost

    return daily


# ============================================================
# Main
# ============================================================
def main():
    ap = argparse.ArgumentParser(description="Generate rolling day-model comprehensive strategy report")
    ap.add_argument("-e", "--etf", default=None, help="Filter to specific ETF (e.g. 300ETF)")
    ap.add_argument("-q", "--quarter", default=None, help="Filter to single quarter (e.g. 2024Q1)")
    ap.add_argument("--thr", type=float, default=DEFAULT_SIGNAL_THR,
                    help=f"Signal percentile threshold (default {DEFAULT_SIGNAL_THR})")
    ap.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS,
                    help=f"Transaction cost in bps (default {DEFAULT_COST_BPS})")
    ap.add_argument("--no-plots", action="store_true", help="Skip diagnostic plot generation")
    ap.add_argument("-j", "--jobs", type=int, default=0,
                    help="Parallel workers for plot generation (0 = auto)")
    ap.add_argument("--early", action="store_true",
                    help="Generate early-window report (10:00 to 13:05)")
    args = ap.parse_args()

    print("=" * 80)
    print("Rolling Day-Model Comprehensive Report Generator")
    print(f"Signal threshold: {args.thr}th percentile | Cost: {args.cost_bps} bps | Early: {args.early}")
    print("=" * 80)

    # Load results
    all_results = load_rolling_results(early=args.early)
    if not all_results:
        print("  [ERROR] No rolling results found in", ROLLING_DATA_DIR)
        print("  Run `python3 day-model/train_rolling.py -e all` first.")
        return

    # Filter
    if args.quarter:
        rq = args.quarter.upper()
        y = int(rq[:4]); q = int(rq[5]); m = q * 3  # Q1=Mar, Q2=Jun, Q3=Sep, Q4=Dec
        target = f"{y}-{m:02d}-01"
        all_results = {k: v for k, v in all_results.items() if k == target}

    if args.etf:
        etf_name = args.etf if args.etf.endswith("ETF") else f"{args.etf}ETF"
        for lb in all_results:
            all_results[lb] = {t: r for t, r in all_results[lb].items() if r.get("etf") == etf_name}
        all_results = {k: v for k, v in all_results.items() if v}

    total_models = sum(len(v) for v in all_results.values())
    print(f"Loaded {total_models} models across {len(all_results)} quarters.")

    # 1. Evaluate each model (IC + strategy returns)
    print("\nEvaluating models (IC + strategy simulation)...")
    eval_metrics = {}
    for quarter in sorted(all_results.keys()):
        eval_metrics[quarter] = {}
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            ev = evaluate_model(tag, res, args.thr, args.cost_bps, early=args.early)
            eval_metrics[quarter][tag] = ev
            if "error" not in ev:
                nt = ev.get("strat_n_trades", 0)
                pnl = ev.get("strat_total_ret", 0) * 1e4
                ic = ev.get("oos_ic", 0)
                print(f"  [{quarter_label(quarter)}] {tag}: IC={ic:+.4f} trades={nt} P&L={pnl:+.0f}bps")
            else:
                print(f"  [{quarter_label(quarter)}] {tag}: ERROR - {ev['error'][:60]}")

    # 2. Warnings
    print("\nEvaluating model health warnings...")
    warnings_dict = evaluate_warnings(all_results)
    n_warn = sum(1 for v in warnings_dict.values() if v["status"] == "WARNING")
    n_alert = sum(1 for v in warnings_dict.values() if v["status"] == "ALERT")
    print(f"  WARNING: {n_warn} | ALERT: {n_alert}")

    # 3. Diagnostic plots
    if not args.no_plots:
        ROLLING_PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        print("\nGenerating diagnostic plots...")
        for quarter in sorted(all_results.keys()):
            ql = quarter_label(quarter)
            qdir = ROLLING_PLOTS_DIR / ql
            qdir.mkdir(parents=True, exist_ok=True)
            for tag in sorted(all_results[quarter].keys()):
                fname = render_quarter_diagnostics(tag, all_results[quarter][tag], qdir, early=args.early)
                if fname:
                    print(f"  {ql}/{fname}")
    else:
        print("\nSkipping plots (--no-plots).")

    # 4. Generate report
    generate_report(all_results, eval_metrics, warnings_dict, args.thr, args.cost_bps, early=args.early)


if __name__ == "__main__":
    main()
