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
from joblib import Parallel, delayed
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
            # For rolling reports, only keep the champion sortino_blended configuration
            if "_sortino_blended" not in tag:
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
# Unified model loading + prediction (computed once, reused everywhere)
# ============================================================
def _compute_model_predictions(tag: str, r: dict, early: bool = False) -> dict | None:
    """Load model + scaler + features, compute full-history predictions.

    Returns dict with model, sel_feats, preds, y (scaled x100), dates, oos_mask,
    all_post_mask, etf, side, lb_date. Returns None on any failure.
    """
    etf = r.get("etf", "")
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
        oos_mask = ((df["date"] >= lb_ts) & (df["date"] < oos_end)).values
        all_post_mask = (df["date"] >= lb_ts).values

        return {
            "model": model,
            "sel_feats": sel_feats,
            "preds": preds,
            "y": y,
            "dates": dates,
            "oos_mask": oos_mask,
            "all_post_mask": all_post_mask,
            "etf": etf,
            "side": side,
            "lb_date": lb_date,
        }
    except Exception:
        return None


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


def simulate_strategy_fast(pred_vals: np.ndarray, actual_returns: np.ndarray,
                           signal_thr: float = 80.0, cost_bps: float = 15.0,
                           side: str = "long") -> float:
    n = len(pred_vals)
    if n < 10:
        return 0.0

    from scipy.stats import rankdata
    rank = rankdata(pred_vals, method='average') / n
    thr = signal_thr / 100.0
    cost = cost_bps / 1e4

    cfg = SIDE_CONFIG.get(side, SIDE_CONFIG["single"])
    
    if cfg["tail_def"] == "top_only":
        mask = rank >= thr
        trades_ret = actual_returns[mask] - cost
    elif cfg["tail_def"] == "bot_only":
        mask = (1.0 - rank) >= thr
        trades_ret = -actual_returns[mask] - cost
    else:
        top_mask = rank >= thr
        bot_mask = rank <= (1.0 - thr)
        trades_ret_top = actual_returns[top_mask] - cost
        trades_ret_bot = -actual_returns[bot_mask] - cost
        trades_ret = np.concatenate([trades_ret_top, trades_ret_bot])

    if len(trades_ret) == 0:
        return 0.0

    n_t = len(trades_ret)
    mean_ret = trades_ret.mean()
    std_ret = trades_ret.std(ddof=1) if n_t > 1 else 0.0
    sharpe = mean_ret / std_ret * np.sqrt(252) if std_ret > 1e-8 else 0.0
    return sharpe


def compute_block_bootstrap_ci(y_oos: np.ndarray, pred_oos: np.ndarray, side: str,
                               block_size: int = 5, B: int = 1000, alpha: float = 0.05,
                               signal_thr: float = 90.0, cost_bps: float = 15.0) -> dict:
    """
    Computes a block-bootstrapped confidence interval for Spearman IC and Strategy Sharpe.
    Returns a dict with:
      - 'ic_ci_lower', 'ic_ci_upper', 'ic_spans_zero'
      - 'sh_ci_lower', 'sh_ci_upper', 'sh_spans_zero'
    """
    N = len(y_oos)
    if N <= block_size:
        block_size = max(1, N // 2)

    ic_boots = np.zeros(B)
    sh_boots = np.zeros(B)

    # Use a fixed seed for reproducible reports
    rng = np.random.default_rng(42)
    n_blocks = int(np.ceil(N / block_size))

    from scipy.stats import rankdata
    from generate_report import _spearman_from_arrays

    for b in range(B):
        # Sample start indices
        start_indices = rng.choice(N - block_size + 1, size=n_blocks, replace=True)
        # Reconstruct indices
        indices = np.zeros(n_blocks * block_size, dtype=int)
        for i, start in enumerate(start_indices):
            indices[i * block_size : (i + 1) * block_size] = np.arange(start, start + block_size)
        
        # Truncate to N
        indices = indices[:N]
        
        y_boot = y_oos[indices]
        pred_boot = pred_oos[indices]
        
        ic_boots[b] = _spearman_from_arrays(y_boot, pred_boot)
        sh_boots[b] = simulate_strategy_fast(pred_boot, y_boot, signal_thr, cost_bps, side)

    # Sort to compute percentiles
    ic_boots.sort()
    sh_boots.sort()

    lower_idx = int(B * (alpha / 2.0))
    upper_idx = int(B * (1.0 - alpha / 2.0))

    ic_lower = float(ic_boots[lower_idx])
    ic_upper = float(ic_boots[upper_idx])
    sh_lower = float(sh_boots[lower_idx])
    sh_upper = float(sh_boots[upper_idx])

    return {
        "ic_ci_lower": ic_lower,
        "ic_ci_upper": ic_upper,
        "ic_spans_zero": bool(ic_lower <= 0.0 <= ic_upper),
        "sh_ci_lower": sh_lower,
        "sh_ci_upper": sh_upper,
        "sh_spans_zero": bool(sh_lower <= 0.0 <= sh_upper),
    }


# ============================================================
# Per-model evaluation
# ============================================================
def evaluate_model(tag: str, r: dict, signal_thr: float, cost_bps: float,
                   early: bool = False, precomputed: dict | None = None) -> dict:
    """Load model, predict OOS, compute IC + strategy metrics. Returns enriched results."""
    side = r.get("side", "single")

    if precomputed is None:
        precomputed = _compute_model_predictions(tag, r, early=early)
    if precomputed is None:
        return {"error": f"missing model/scaler/features for {tag}"}

    y = precomputed["y"]
    preds = precomputed["preds"]
    oos_mask = precomputed["oos_mask"]

    y_oos = y[oos_mask]
    pred_oos = preds[oos_mask]

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

    # Block-bootstrap CIs (B=1000)
    boot = compute_block_bootstrap_ci(y_oos, pred_oos, side, signal_thr=signal_thr, cost_bps=cost_bps)

    return {
        "oos_ic": oos_ic,
        "oos_tail_ic": oos_tail_ic,
        "oos_mono": oos_mono,
        "n_oos": len(y_oos),
        **{f"strat_{k}": v for k, v in strat.items()},
        **boot,
    }
# ============================================================
# Warning System (pre-lockbox validation metrics only)
# ============================================================
def evaluate_warnings(all_results: dict, early: bool = False) -> dict:
    """Evaluate model health using ex-ante market-regime flags.
    
    Checks:
    - VIX level and percentile.
    - VIX acceleration (VIX vs 20-day SMA).
    - Cross-ETF return correlation over the preceding 60 days.
    """
    warnings_out = {}
    
    # Pre-cache ETF returns dataframes to avoid repeatedly loading them
    etf_dfs = {}
    for etf in ETF_ORDER:
        df = _load_features(etf, early=early)
        if df is not None:
            etf_dfs[etf] = df
            
    def get_cross_corr(lb_date_str: str) -> float:
        lb_ts = pd.Timestamp(lb_date_str)
        etf_returns = {}
        for etf, df in etf_dfs.items():
            # Filter to preceding 60 trading days leading up to lockbox
            mask = (df["date"] < lb_ts) & (df["date"] >= lb_ts - pd.Timedelta(days=90))
            sub_df = df[mask].sort_values("date").set_index("date")
            etf_returns[etf] = sub_df[TARGET]
            
        if not etf_returns:
            return 1.0
            
        merged_df = pd.DataFrame(etf_returns).ffill().dropna().tail(60)
        if len(merged_df) < 10:
            return 1.0
            
        corr_matrix = merged_df.corr(method="spearman")
        n = corr_matrix.shape[0]
        if n < 2:
            return 1.0
        corrs = []
        for i in range(n):
            for j in range(i + 1, n):
                corrs.append(corr_matrix.iloc[i, j])
        return float(np.mean(corrs))

    for quarter in sorted(all_results.keys()):
        lb_ts = pd.Timestamp(quarter)
        
        # Calculate cross-ETF correlation once per quarter
        cross_corr = get_cross_corr(quarter)
        
        for tag, res in all_results[quarter].items():
            etf = res.get("etf", "")
            
            # Fetch VIX metrics for this ETF at lockbox_date
            vix_level = 20.0
            vix_pct = 0.5
            vix_accel = 0.0
            
            df = etf_dfs.get(etf)
            if df is not None and "vix" in df.columns:
                sub_df = df[df["date"] < lb_ts].sort_values("date")
                if len(sub_df) >= 60:
                    vix_series = sub_df["vix"].ffill().dropna()
                    if len(vix_series) >= 60:
                        vix_level = float(vix_series.iloc[-1])
                        past_year = vix_series.tail(252)
                        vix_pct = float((past_year < vix_level).mean())
                        vix_sma20 = float(vix_series.tail(20).mean())
                        vix_accel = vix_level - vix_sma20
                        
            status = "OK"
            reasons = []
            
            # Warning conditions
            # VIX is in decimals (e.g. 0.25 represents 25% VIX)
            if vix_level > 0.25:
                reasons.append(f"VIX={vix_level * 100.0:.1f}%>25%")
            if vix_pct > 0.85:
                reasons.append(f"VIX_pct={vix_pct:.1%}>85%")
            if vix_accel > 0.03:
                reasons.append(f"VIX_accel={vix_accel * 100.0:+.1f}%>3%")
            if cross_corr < 0.65:
                reasons.append(f"cross_corr={cross_corr:.2f}<0.65")
                
            # Status determination
            # Alert conditions:
            # - VIX level extremely high (>30%) OR VIX percentile > 95%
            # - Cross-correlation completely broken down (<0.55)
            # - Or 2 or more warnings active
            is_alert = (
                vix_level > 0.30 or 
                vix_pct > 0.95 or 
                cross_corr < 0.55 or 
                len(reasons) >= 2
            )
            
            if is_alert:
                status = "ALERT"
            elif reasons:
                status = "WARNING"
                
            warnings_out[(quarter, tag)] = {
                "status": status,
                "reasons": reasons,
                "vix_level": vix_level,
                "vix_percentile": vix_pct,
                "vix_acceleration": vix_accel,
                "cross_corr": cross_corr
            }
            
    return warnings_out
# Diagnostic plots (per-quarter subdirectories)
# ============================================================
def render_quarter_diagnostics(tag: str, r: dict, quarter_dir: Path,
                               early: bool = False, precomputed: dict | None = None) -> str | None:
    """Render 15-panel diagnostic figure for one rolling model. Returns filename or None."""
    etf = r["etf"]
    side = r.get("side", "single")
    lb_date = r.get("lockbox_date", "")

    model_path = ROLLING_MODELS_DIR / f"linear_{tag}.joblib"
    scaler_path = ROLLING_MODELS_DIR / f"scaler_{tag}.joblib"

    out_dir = quarter_dir / "early" if early else quarter_dir
    fname = f"diagnostics_{tag.replace('ETF', '')}.png"
    out_path = out_dir / fname

    # Skip if plot already up-to-date (check before loading anything)
    if (model_path.exists() and scaler_path.exists()
            and out_path.exists()
            and out_path.stat().st_mtime > model_path.stat().st_mtime
            and out_path.stat().st_mtime > scaler_path.stat().st_mtime):
        return f"early/{fname}" if early else fname

    if precomputed is None:
        precomputed = _compute_model_predictions(tag, r, early=early)
    if precomputed is None:
        return None

    try:
        model = precomputed["model"]
        sel_feats = precomputed["sel_feats"]
        preds = precomputed["preds"]
        y = precomputed["y"]
        dates = precomputed["dates"]
        oos_mask = precomputed["oos_mask"]
        all_post_mask = precomputed["all_post_mask"]

        y_oos, pred_oos, dates_oos = y[oos_mask], preds[oos_mask], dates[oos_mask]
        y_post, pred_post = y[all_post_mask], preds[all_post_mask]

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
        out_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=110)
        plt.close(fig)
        return f"early/{fname}" if early else fname
    except Exception as ex:
        print(f"  [WARN] Plot failed for {tag}: {ex}")
        return None


# ============================================================
# Report generator
# ============================================================
def generate_report(all_results: dict, eval_metrics: dict, warnings_dict: dict,
                    signal_thr: float, cost_bps: float, early: bool = False,
                    pred_data: dict | None = None):
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
            sh_lower = ev.get("sh_ci_lower", 0.0)
            sh_upper = ev.get("sh_ci_upper", 0.0)
            sh_flag = "*" if ev.get("sh_spans_zero", False) else ""
            sh_str = f"{sh:+.2f} [{sh_lower:+.2f}, {sh_upper:+.2f}]{sh_flag}"
            dd = ev.get("strat_max_dd", 0)
            mr = ev.get("strat_mean_ret", 0)
            L.append(f"| {ql} | {etf} | `{side}` | {n_t} | {wr:.1%} | {tr*1e4:+.0f}bps | {sh_str} | {dd*1e4:.0f}bps | {mr*1e4:+.1f}bps |")
    L.append("")
    L.append("- \* Note: \* indicates 95% block-bootstrap confidence interval (block_size=5 days, B=1000) spans zero.")
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
                daily_rets = _compute_daily_returns(
                    tag, res, signal_thr, cost_bps, side,
                    early=early,
                    precomputed=pred_data.get(tag) if pred_data else None)
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
            ic = ev.get("oos_ic", 0)
            ic_lower = ev.get("ic_ci_lower", 0.0)
            ic_upper = ev.get("ic_ci_upper", 0.0)
            ic_flag = "*" if ev.get("ic_spans_zero", False) else ""
            ic_str = f"{ic:+.4f} [{ic_lower:+.4f}, {ic_upper:+.4f}]{ic_flag}"
            L.append(f"| {ql} | {etf} | `{side}` | {n_oos} | {ic_str} | {ev.get('oos_tail_ic', 0):+.4f} | {ev.get('oos_mono', 0):+.4f} |")
    L.append("")
    L.append("- \* Note: \* indicates 95% block-bootstrap confidence interval (block_size=5 days, B=1000) spans zero.")
    L.append("")

    # === Model Health ===
    L.append("## Model Health Warnings (Regime-Based)")
    L.append("")
    L.append("Evaluating ex-ante market-state indicators leading up to each lockbox date.")
    L.append("")
    L.append("| Quarter | Tag | VIX Level | VIX %tile | VIX Accel | Cross-Corr | Status | Reason |")
    L.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |")
    for quarter in sorted(all_results.keys()):
        ql = quarter_label(quarter)
        for tag in sorted(all_results[quarter].keys()):
            w = warnings_dict.get((quarter, tag), {
                "status": "OK", "reasons": [], 
                "vix_level": 20.0, "vix_percentile": 0.5, 
                "vix_acceleration": 0.0, "cross_corr": 1.0
            })
            reason = ", ".join(w["reasons"]) if w["reasons"] else "-"
            vl = w["vix_level"] * 100.0
            vp = w["vix_percentile"]
            va = w["vix_acceleration"] * 100.0
            cc = w["cross_corr"]
            L.append(f"| {ql} | {tag} | {vl:.1f}% | {vp:.1%} | {va:+.1f}% | {cc:.2f} | **{w['status']}** | {reason} |")
    L.append("")
    L.append("### Warning Trigger Levels")
    L.append("")
    L.append("- **WARNING**: Triggered if any one of the following holds:")
    L.append("  - VIX Level > 25.0% or VIX past-year percentile > 85%")
    L.append("  - VIX Acceleration > 3.0% (rising sharply above 20-day SMA)")
    L.append("  - Cross-ETF correlation breakdown (average Spearman correlation < 0.65)")
    L.append("- **ALERT**: Triggered if VIX is extremely high (>30.0% or percentile > 95%), cross-ETF correlation completely breaks down (<0.55), or 2 or more warnings are active.")
    L.append("")

    # === IC Timeline by ETF ===
    L.append("## IC & Return Timeline by ETF")
    L.append("")
    L.append("- \* Note: \* indicates 95% block-bootstrap confidence interval (block_size=5 days, B=1000) spans zero.")
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
                if "error" in ev:
                    L.append(f"| {ql} | ERR | - | - | - | - | - |")
                    continue
                ic = ev.get("oos_ic", 0)
                ic_lower = ev.get("ic_ci_lower", 0.0)
                ic_upper = ev.get("ic_ci_upper", 0.0)
                ic_flag = "*" if ev.get("ic_spans_zero", False) else ""
                ic_str = f"{ic:+.4f} [{ic_lower:+.4f}, {ic_upper:+.4f}]{ic_flag}"

                tic = ev.get("oos_tail_ic", 0)
                nt = ev.get("strat_n_trades", 0)
                pnl = ev.get("strat_total_ret", 0) * 1e4
                
                sh = ev.get("strat_sharpe", 0)
                sh_lower = ev.get("sh_ci_lower", 0.0)
                sh_upper = ev.get("sh_ci_upper", 0.0)
                sh_flag = "*" if ev.get("sh_spans_zero", False) else ""
                sh_str = f"{sh:+.2f} [{sh_lower:+.2f}, {sh_upper:+.2f}]{sh_flag}"

                wr = ev.get("strat_win_rate", 0)
                L.append(f"| {ql} | {ic_str} | {tic:+.4f} | {nt} | {pnl:+.0f}bps | {sh_str} | {wr:.0%} |")
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
                        etf_features[quarter_label(quarter)] = res
            if not etf_features:
                continue

            all_feats = set()
            for res_q in etf_features.values():
                active = set(res_q.get("active_features", res_q.get("selected_features", [])))
                all_feats |= active
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
                    res_q = etf_features[ql]
                    active_feats = set(res_q.get("active_features", res_q.get("selected_features", [])))
                    present = f in active_feats
                    if present:
                        coef_mean = res_q.get("bagged_coef_mean", {}).get(f)
                        coef_cv_std = res_q.get("bagged_coef_cv_std", {}).get(f)
                        if coef_mean is not None and coef_cv_std is not None:
                            row.append(f"{coef_mean:+.3f} ({coef_cv_std:.3f})")
                        else:
                            row.append("Y")
                        count += 1
                    else:
                        row.append("-")
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
                           side: str, early: bool = False,
                           precomputed: dict | None = None) -> dict:
    """Reconstruct daily returns for portfolio aggregation. Returns {date: return}."""
    if precomputed is None:
        precomputed = _compute_model_predictions(tag, r, early=early)
    if precomputed is None:
        return {}

    oos_mask = precomputed["oos_mask"]
    dates = precomputed["dates"]
    preds = precomputed["preds"]
    y = precomputed["y"]

    oos_dates = pd.to_datetime(dates[oos_mask])
    pred_oos = pd.Series(preds[oos_mask], index=oos_dates)
    y_oos = pd.Series(y[oos_mask], index=oos_dates)

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

    # 0. Precompute model predictions once (eliminates triple-loading redundancy)
    print("\nPrecomputing model predictions (single pass)...")
    pred_data = {}
    all_tags = []
    for quarter in sorted(all_results.keys()):
        for tag in sorted(all_results[quarter].keys()):
            r = all_results[quarter][tag]
            data = _compute_model_predictions(tag, r, early=args.early)
            if data is not None:
                pred_data[tag] = data
            all_tags.append((quarter, tag))
    print(f"  Predictions cached for {len(pred_data)}/{len(all_tags)} models.")

    # 1. Evaluate each model (IC + strategy returns)
    print("\nEvaluating models (IC + strategy simulation + block-bootstrap)...")
    eval_tasks = []
    for quarter in sorted(all_results.keys()):
        for tag in sorted(all_results[quarter].keys()):
            res = all_results[quarter][tag]
            eval_tasks.append((quarter, tag, res))

    n_eval_jobs = args.jobs if args.jobs > 0 else min(
        len(eval_tasks), max(1, (os.cpu_count() or 4) - 1))

    print(f"  Running {len(eval_tasks)} evaluations in parallel ({n_eval_jobs} workers)...")
    eval_results = Parallel(n_jobs=n_eval_jobs, backend="loky")(
        delayed(evaluate_model)(
            tag, res, args.thr, args.cost_bps,
            early=args.early, precomputed=pred_data.get(tag)
        ) for quarter, tag, res in eval_tasks
    )

    eval_metrics = {}
    for (quarter, tag, res), ev in zip(eval_tasks, eval_results):
        eval_metrics.setdefault(quarter, {})[tag] = ev
        if "error" not in ev:
            nt = ev.get("strat_n_trades", 0)
            pnl = ev.get("strat_total_ret", 0) * 1e4
            ic = ev.get("oos_ic", 0)
            sh = ev.get("strat_sharpe", 0)
            print(f"  [{quarter_label(quarter)}] {tag}: IC={ic:+.4f} Sharpe={sh:+.2f} trades={nt} P&L={pnl:+.0f}bps")
        else:
            print(f"  [{quarter_label(quarter)}] {tag}: ERROR - {ev['error'][:60]}")

    # 2. Warnings
    print("\nEvaluating model health warnings...")
    warnings_dict = evaluate_warnings(all_results, early=args.early)
    n_warn = sum(1 for v in warnings_dict.values() if v["status"] == "WARNING")
    n_alert = sum(1 for v in warnings_dict.values() if v["status"] == "ALERT")
    print(f"  WARNING: {n_warn} | ALERT: {n_alert}")

    # 3. Diagnostic plots (parallelized via joblib loky backend)
    if not args.no_plots:
        ROLLING_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

        # Build task list: (tag, result, quarter_dir, quarter_label)
        plot_tasks = []
        for quarter in sorted(all_results.keys()):
            ql = quarter_label(quarter)
            qdir = ROLLING_PLOTS_DIR / ql
            for tag in sorted(all_results[quarter].keys()):
                plot_tasks.append((tag, all_results[quarter][tag], qdir, ql))

        n_jobs = args.jobs if args.jobs > 0 else min(
            len(plot_tasks), max(1, (os.cpu_count() or 4) - 1))

        if n_jobs > 1 and len(plot_tasks) > 1:
            print(f"\nGenerating {len(plot_tasks)} diagnostic plots ({n_jobs} parallel workers)...")
            try:
                plot_results = Parallel(n_jobs=n_jobs, backend="loky")(
                    delayed(render_quarter_diagnostics)(
                        tag, r, qdir, early=args.early,
                        precomputed=pred_data.get(tag))
                    for tag, r, qdir, ql in plot_tasks
                )
            except Exception as e:
                print(f"  [WARNING] Parallel plot generation failed ({e}); falling back to sequential.")
                plot_results = [
                    render_quarter_diagnostics(
                        tag, r, qdir, early=args.early,
                        precomputed=pred_data.get(tag))
                    for tag, r, qdir, ql in plot_tasks
                ]
        else:
            print(f"\nGenerating {len(plot_tasks)} diagnostic plots (sequential)...")
            plot_results = [
                render_quarter_diagnostics(
                    tag, r, qdir, early=args.early,
                    precomputed=pred_data.get(tag))
                for tag, r, qdir, ql in plot_tasks
            ]

        for (tag, r, qdir, ql), fname in zip(plot_tasks, plot_results):
            if fname:
                print(f"  {ql}/{fname}")
    else:
        print("\nSkipping plots (--no-plots).")

    # 4. Generate report
    generate_report(all_results, eval_metrics, warnings_dict, args.thr, args.cost_bps,
                    early=args.early, pred_data=pred_data)


if __name__ == "__main__":
    main()
