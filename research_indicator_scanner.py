"""
Massive Indicator Scanner for Chinese ETF Option Strategy Research
====================================================================
Evaluates ~30 technical/statistical indicators and their two-indicator
combinations for predictive power on 14-day and 30-day forward returns.

Usage:
    python research_indicator_scanner.py
"""
import os
import sys
import warnings
import itertools
import numpy as np
import pandas as pd
import pandas_ta as ta
from scipy import stats

warnings.filterwarnings('ignore')

ETF_CONFIG = {
    "50": {"path": "./data/50ETF_1d.parquet", "name": "50ETF"},
    "300": {"path": "./data/510300_1d.parquet", "name": "300ETF"},
    "500": {"path": "./data/500ETF_1d.parquet", "name": "500ETF"},
}

MIN_DAYS_SINGLE = 30
MIN_DAYS_COMBO = 20


def expanding_quantile(series, q, min_periods=252):
    """Compute expanding-window quantile to avoid look-ahead bias.

    Each day's threshold uses only data available up to that day.
    Returns NaN for the first ``min_periods`` rows.
    """
    return series.expanding(min_periods=min_periods).quantile(q)


# Pre-specified known combos from existing put strategy filters.
# These are always evaluated regardless of greedy top-10 selection.
KNOWN_COMBOS = {
    "300": [
        ("dd_252 < -0.15", "dist_sma50 < -1.0", "AND"),
        ("rsi14 > 65", "skew_20 < -0.3", "AND"),
    ],
    "50": [
        ("skew_20 < -0.5", "iv_vol_ratio < 0.9", "AND"),
    ],
    "500": [
        ("kurt_20 > 1.0", "iv_vol_ratio > 1.2", "AND"),
    ],
}


def load_etf_data(etf_key):
    """Load ETF daily parquet and return DataFrame with price columns."""
    config = ETF_CONFIG[etf_key]
    path = config["path"]
    df = pd.read_parquet(path)

    # Parse date and set as sorted index
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    else:
        df = df.reset_index()
        df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # Determine price columns (adjusted if available)
    if "close_adj" in df.columns:
        close_col = "close_adj"
        high_col = "high_adj" if "high_adj" in df.columns else "high"
        low_col = "low_adj" if "low_adj" in df.columns else "low"
    else:
        close_col = "close"
        high_col = "high"
        low_col = "low"

    # Try to add iv_vol_ratio from IV cache
    iv_cache_path = f"./data/30d_iv_cache_{etf_key if etf_key != '300' else '300'}.parquet"
    if "iv_vol_ratio" not in df.columns and os.path.exists(iv_cache_path):
        try:
            iv_df = pd.read_parquet(iv_cache_path)
            if "date" in iv_df.columns:
                iv_df["date"] = pd.to_datetime(iv_df["date"])
                iv_df = iv_df.set_index("date").sort_index()
            elif iv_df.index.name is not None and iv_df.index.name != "date":
                iv_df = iv_df.reset_index().rename(columns={iv_df.index.name: "date"})
                iv_df["date"] = pd.to_datetime(iv_df["date"])
                iv_df = iv_df.set_index("date").sort_index()
            if "iv_vol_ratio" in iv_df.columns:
                df["iv_vol_ratio"] = iv_df["iv_vol_ratio"]
        except Exception:
            pass

    return df, close_col, high_col, low_col


def compute_indicators(df, close_col, high_col, low_col):
    """Compute ~30 technical and statistical indicators using adjusted prices."""
    close = df[close_col]
    high = df[high_col] if high_col in df.columns else close
    low = df[low_col] if low_col in df.columns else close
    volume = df["volume"] if "volume" in df.columns else pd.Series(np.ones(len(df)), index=df.index)
    returns = close.pct_change()

    # ── Momentum ──
    df["rsi14"] = ta.rsi(close, length=14)
    df["rsi7"] = ta.rsi(close, length=7)

    macd = ta.macd(close)
    if macd is not None:
        df["macd_hist"] = macd.iloc[:, 1]
    else:
        df["macd_hist"] = pd.Series(np.nan, index=df.index)

    df["roc10"] = ta.roc(close, length=10)
    df["roc5"] = ta.roc(close, length=5)
    df["mom10"] = ta.mom(close, length=10)

    cci = ta.cci(high, low, close, length=20)
    df["cci20"] = cci if cci is not None else pd.Series(np.nan, index=df.index)

    stoch = ta.stoch(high, low, close, k=14, d=3, smooth_k=3)
    if stoch is not None:
        df["stoch_k"] = stoch.iloc[:, 0]
    else:
        df["stoch_k"] = pd.Series(np.nan, index=df.index)

    willr = ta.willr(high, low, close, length=14)
    df["williams_r14"] = willr if willr is not None else pd.Series(np.nan, index=df.index)

    cmo = ta.cmo(close, length=14)
    df["cmo14"] = cmo if cmo is not None else pd.Series(np.nan, index=df.index)

    # ── Trend ──
    df["sma20"] = ta.sma(close, length=20)
    df["sma50"] = ta.sma(close, length=50)
    df["sma200"] = ta.sma(close, length=200)
    df["ema20"] = ta.ema(close, length=20)
    df["ema10"] = ta.ema(close, length=10)

    adx = ta.adx(high, low, close, length=14)
    if adx is not None:
        df["adx14"] = adx.iloc[:, 0]
    else:
        df["adx14"] = pd.Series(np.nan, index=df.index)

    # ── Volatility ──
    bbands = ta.bbands(close, length=20, std=2)
    if bbands is not None:
        bb_upper = bbands.iloc[:, 2]
        bb_lower = bbands.iloc[:, 0]
        df["bb_width"] = (bb_upper - bb_lower) / df["sma20"]
        df["bb_percent_b"] = (close - bb_lower) / (bb_upper - bb_lower)
    else:
        df["bb_width"] = pd.Series(np.nan, index=df.index)
        df["bb_percent_b"] = pd.Series(np.nan, index=df.index)

    df["atr20"] = ta.atr(high, low, close, length=20)

    natr = ta.natr(high, low, close, length=14)
    df["natr14"] = natr if natr is not None else pd.Series(np.nan, index=df.index)

    df["vol20"] = returns.rolling(20).std() * np.sqrt(252)
    df["vol10"] = returns.rolling(10).std() * np.sqrt(252)

    # ── Volume ──
    obv = ta.obv(close, volume)
    df["obv"] = obv if obv is not None else pd.Series(np.nan, index=df.index)

    cmf = ta.cmf(high, low, close, volume, length=20)
    df["cmf20"] = cmf if cmf is not None else pd.Series(np.nan, index=df.index)

    mfi = ta.mfi(high, low, close, volume, length=14)
    df["mfi14"] = mfi if mfi is not None else pd.Series(np.nan, index=df.index)

    # ── Statistical / Tail ──
    df["skew_20"] = returns.rolling(20).skew()
    df["kurt_20"] = returns.rolling(20).kurt()
    df["zscore20"] = (close - close.rolling(20).mean()) / close.rolling(20).std()

    # ── Custom ──
    df["dd_252"] = close / close.rolling(252).max() - 1.0
    df["dist_sma50"] = (close - df["sma50"]) / df["atr20"]
    df["dist_sma200"] = (close - df["sma200"]) / df["atr20"]

    return df


def compute_forward_returns(df, close_col):
    """Compute 14d and 30d forward returns using vectorized calendar-day search."""
    dates = df.index.values
    closes = df[close_col].values

    target_14 = dates + np.timedelta64(14, 'D')
    target_30 = dates + np.timedelta64(30, 'D')

    idx_14 = np.searchsorted(dates, target_14)
    idx_30 = np.searchsorted(dates, target_30)

    fwd_14 = np.full(len(df), np.nan)
    fwd_30 = np.full(len(df), np.nan)

    valid_14 = idx_14 < len(dates)
    valid_30 = idx_30 < len(dates)

    fwd_14[valid_14] = closes[idx_14[valid_14]] / closes[np.where(valid_14)[0]] - 1.0
    fwd_30[valid_30] = closes[idx_30[valid_30]] / closes[np.where(valid_30)[0]] - 1.0

    df["fwd_ret_14d"] = fwd_14
    df["fwd_ret_30d"] = fwd_30
    return df


def define_conditions(df, close_col):
    """Define all threshold conditions for each indicator.

    Quantile-based thresholds use expanding-window (252-day minimum) to avoid
    look-ahead bias.  Fixed-threshold conditions used by KNOWN_COMBOS are also
    included.
    """
    conditions = {}
    eq = expanding_quantile  # shorthand

    # RSI
    conditions["rsi14 > 70"] = df["rsi14"] > 70
    conditions["rsi14 < 30"] = df["rsi14"] < 30
    conditions["rsi14 > 65"] = df["rsi14"] > 65   # known-combo fixed threshold
    conditions["rsi7 > 70"]  = df["rsi7"]  > 70
    conditions["rsi7 < 30"]  = df["rsi7"]  < 30

    # MACD
    conditions["macd_hist > 0"] = df["macd_hist"] > 0
    conditions["macd_hist < 0"] = df["macd_hist"] < 0

    # ROC  (expanding-window quantiles)
    conditions["roc10 > q90"] = df["roc10"] > eq(df["roc10"], 0.90)
    conditions["roc10 < q10"] = df["roc10"] < eq(df["roc10"], 0.10)
    conditions["roc5 > q90"]  = df["roc5"]  > eq(df["roc5"],  0.90)
    conditions["roc5 < q10"]  = df["roc5"]  < eq(df["roc5"],  0.10)

    # Momentum
    conditions["mom10 > 0"] = df["mom10"] > 0
    conditions["mom10 < 0"] = df["mom10"] < 0

    # CCI
    conditions["cci20 > 100"]  = df["cci20"] > 100
    conditions["cci20 < -100"] = df["cci20"] < -100

    # Stochastic
    conditions["stoch_k > 80"] = df["stoch_k"] > 80
    conditions["stoch_k < 20"] = df["stoch_k"] < 20

    # Williams %R
    conditions["williams_r14 > -20"] = df["williams_r14"] > -20
    conditions["williams_r14 < -80"] = df["williams_r14"] < -80

    # CMO  (expanding-window quantiles)
    conditions["cmo14 > q90"] = df["cmo14"] > eq(df["cmo14"], 0.90)
    conditions["cmo14 < q10"] = df["cmo14"] < eq(df["cmo14"], 0.10)

    # ADX
    conditions["adx14 > 25"] = df["adx14"] > 25
    conditions["adx14 < 25"] = df["adx14"] < 25

    # Bollinger Bands
    conditions["bb_percent_b > 0.8"] = df["bb_percent_b"] > 0.8
    conditions["bb_percent_b < 0.2"] = df["bb_percent_b"] < 0.2
    conditions["bb_width > q90"] = df["bb_width"] > eq(df["bb_width"], 0.90)
    conditions["bb_width < q10"] = df["bb_width"] < eq(df["bb_width"], 0.10)

    # ATR / NATR  (expanding-window quantiles)
    conditions["atr20 > q90"] = df["atr20"] > eq(df["atr20"], 0.90)
    conditions["atr20 < q10"] = df["atr20"] < eq(df["atr20"], 0.10)
    conditions["natr14 > q90"] = df["natr14"] > eq(df["natr14"], 0.90)
    conditions["natr14 < q10"] = df["natr14"] < eq(df["natr14"], 0.10)

    # Volatility  (expanding-window quantiles)
    conditions["vol20 > q90"] = df["vol20"] > eq(df["vol20"], 0.90)
    conditions["vol20 < q10"] = df["vol20"] < eq(df["vol20"], 0.10)
    conditions["vol10 > q90"] = df["vol10"] > eq(df["vol10"], 0.90)
    conditions["vol10 < q10"] = df["vol10"] < eq(df["vol10"], 0.10)

    # Volume-based
    conditions["cmf20 > 0"]  = df["cmf20"] > 0
    conditions["cmf20 < 0"]  = df["cmf20"] < 0
    conditions["mfi14 > 80"] = df["mfi14"] > 80
    conditions["mfi14 < 20"] = df["mfi14"] < 20

    # Statistical / Tail  (expanding-window quantiles + known-combo fixed thresholds)
    conditions["skew_20 > q90"]  = df["skew_20"] > eq(df["skew_20"], 0.90)
    conditions["skew_20 < q10"]  = df["skew_20"] < eq(df["skew_20"], 0.10)
    conditions["skew_20 < -0.3"] = df["skew_20"] < -0.3   # known-combo fixed threshold
    conditions["skew_20 < -0.5"] = df["skew_20"] < -0.5   # known-combo fixed threshold
    conditions["kurt_20 > q90"]  = df["kurt_20"] > eq(df["kurt_20"], 0.90)
    conditions["kurt_20 < q10"]  = df["kurt_20"] < eq(df["kurt_20"], 0.10)
    conditions["kurt_20 > 1.0"]  = df["kurt_20"] > 1.0    # known-combo fixed threshold
    conditions["zscore20 > 2"]   = df["zscore20"] > 2
    conditions["zscore20 < -2"]  = df["zscore20"] < -2

    # Custom
    conditions["dd_252 < -0.15"] = df["dd_252"] < -0.15
    conditions["dd_252 > q90"] = df["dd_252"] > eq(df["dd_252"], 0.90)  # less negative
    conditions["dist_sma50 < -1.0"] = df["dist_sma50"] < -1.0
    conditions["dist_sma50 > 1.0"]  = df["dist_sma50"] > 1.0
    conditions["dist_sma200 < -2.0"] = df["dist_sma200"] < -2.0
    conditions["dist_sma200 > 2.0"]  = df["dist_sma200"] > 2.0

    # Trend distance from SMA
    conditions["close > sma20"] = df[close_col] > df["sma20"]
    conditions["close < sma20"] = df[close_col] < df["sma20"]
    conditions["close > sma50"] = df[close_col] > df["sma50"]
    conditions["close < sma50"] = df[close_col] < df["sma50"]

    # IV/Vol ratio  (expanding-window quantiles + known-combo fixed thresholds)
    if "iv_vol_ratio" in df.columns:
        conditions["iv_vol_ratio > q90"]  = df["iv_vol_ratio"] > eq(df["iv_vol_ratio"], 0.90)
        conditions["iv_vol_ratio < q10"]  = df["iv_vol_ratio"] < eq(df["iv_vol_ratio"], 0.10)
        conditions["iv_vol_ratio < 0.9"]  = df["iv_vol_ratio"] < 0.9   # known-combo fixed threshold
        conditions["iv_vol_ratio > 1.2"]  = df["iv_vol_ratio"] > 1.2   # known-combo fixed threshold

    return conditions


def _compute_metrics(valid_df, mask, etf_name, cond_label, cond_type,
                     p10_thresh, p25_thresh, baseline_p10, baseline_p25,
                     n_total, min_triggers):
    """Compute all metrics for a boolean condition mask.

    Rows where the underlying indicator is NaN (early rolling-window warmup)
    are excluded from *both* the triggered and non-triggered groups so that
    NaN is never silently treated as ``False``.

    Returns a result dict, or ``None`` when ``n_triggered < min_triggers``.
    """
    # Exclude NaN-indicator rows from both groups
    nan_mask = mask.isna().reindex(valid_df.index).fillna(False)
    mask_clean = mask.reindex(valid_df.index).fillna(False) & ~nan_mask
    n_trig = int(mask_clean.sum())

    if n_trig < min_triggers:
        return None

    triggered     = valid_df[mask_clean]
    non_triggered = valid_df[~mask_clean & ~nan_mask.reindex(valid_df.index).fillna(False)]

    # 14d metrics
    t_14  = triggered["fwd_ret_14d"].dropna()
    nt_14 = non_triggered["fwd_ret_14d"].dropna()
    mean_14     = t_14.mean() if len(t_14) > 0 else np.nan
    prob_neg_14 = (t_14 < 0).mean() if len(t_14) > 0 else np.nan
    if len(t_14) > 0 and len(nt_14) > 0:
        _, p_val_14 = stats.ttest_ind(t_14, nt_14, equal_var=False)
    else:
        p_val_14 = np.nan

    # 30d metrics
    t_30  = triggered["fwd_ret_30d"].dropna()
    nt_30 = non_triggered["fwd_ret_30d"].dropna()
    mean_30     = t_30.mean() if len(t_30) > 0 else np.nan
    prob_neg_30 = (t_30 < 0).mean() if len(t_30) > 0 else np.nan
    if len(t_30) > 0 and len(nt_30) > 0:
        _, p_val_30 = stats.ttest_ind(t_30, nt_30, equal_var=False)
    else:
        p_val_30 = np.nan

    # Tail metrics
    prob_p10 = (t_30 <= p10_thresh).mean() if len(t_30) > 0 else np.nan
    prob_p25 = (t_30 <= p25_thresh).mean() if len(t_30) > 0 else np.nan
    lift_p10 = prob_p10 / baseline_p10 if baseline_p10 > 0 and not np.isnan(prob_p10) else np.nan
    lift_p25 = prob_p25 / baseline_p25 if baseline_p25 > 0 and not np.isnan(prob_p25) else np.nan

    return {
        "etf": etf_name,
        "type": cond_type,
        "condition": cond_label,
        "n_triggered": n_trig,
        "placement_rate": n_trig / n_total,
        "mean_14d": mean_14,
        "prob_neg_14d": prob_neg_14,
        "p_val_14d": p_val_14,
        "mean_30d": mean_30,
        "prob_neg_30d": prob_neg_30,
        "p_val_30d": p_val_30,
        "prob_p10": prob_p10,
        "prob_p25": prob_p25,
        "lift_p10": lift_p10,
        "lift_p25": lift_p25,
    }


def evaluate_single_conditions(df, conditions, etf_name,
                               p10_thresh, p25_thresh, baseline_p10, baseline_p25):
    """Evaluate all single-indicator conditions. Returns list of dicts."""
    valid_df = df.dropna(subset=["fwd_ret_14d", "fwd_ret_30d"])
    n_total = len(valid_df)
    results = []

    for label, mask_series in conditions.items():
        r = _compute_metrics(
            valid_df, mask_series, etf_name, label, "single",
            p10_thresh, p25_thresh, baseline_p10, baseline_p25,
            n_total, MIN_DAYS_SINGLE,
        )
        if r is not None:
            results.append(r)

    return results


def get_top_conditions(results, metric, n=10):
    """Get top N single conditions for a given metric."""
    if metric == "crash":
        # Lowest p-value for P10 tail lift, then highest prob_p10
        sorted_r = sorted(results, key=lambda x: (
            np.isnan(x["p_val_30d"]),
            x["p_val_30d"],
            -x["prob_p10"] if not np.isnan(x["prob_p10"]) else 0
        ))
    elif metric == "fall_14d":
        # Highest prob_neg_14d with lowest p_val_14d
        sorted_r = sorted(results, key=lambda x: (
            np.isnan(x["p_val_14d"]),
            -x["prob_neg_14d"] if not np.isnan(x["prob_neg_14d"]) else 0,
            x["p_val_14d"],
        ))
    else:  # fall_30d
        sorted_r = sorted(results, key=lambda x: (
            np.isnan(x["p_val_30d"]),
            -x["prob_neg_30d"] if not np.isnan(x["prob_neg_30d"]) else 0,
            x["p_val_30d"],
        ))
    return sorted_r[:n]


def evaluate_combinations(df, top_conditions, conditions_dict, etf_name,
                          p10_thresh, p25_thresh, baseline_p10, baseline_p25):
    """Evaluate AND/OR combinations of top single conditions."""
    valid_df = df.dropna(subset=["fwd_ret_14d", "fwd_ret_30d"])
    n_total = len(valid_df)
    results = []

    labels = [r["condition"] for r in top_conditions]
    masks  = [conditions_dict[label] for label in labels]

    for i, j in itertools.combinations(range(len(labels)), 2):
        for op_name, op in [("AND", lambda a, b: a & b), ("OR", lambda a, b: a | b)]:
            label = f"{labels[i]} {op_name} {labels[j]}"
            mask  = op(masks[i], masks[j])
            r = _compute_metrics(
                valid_df, mask, etf_name, label, "combo",
                p10_thresh, p25_thresh, baseline_p10, baseline_p25,
                n_total, MIN_DAYS_COMBO,
            )
            if r is not None:
                results.append(r)

    return results


def print_results(results, etf_name):
    """Print concise console tables."""
    print(f"\n{'='*80}")
    print(f"  {etf_name} - Top Single-Indicator Conditions")
    print(f"{'='*80}")

    for metric_name, metric_key in [
        ("Crash (P10 Tail)", "crash"),
        ("Fall-14d", "fall_14d"),
        ("Fall-30d", "fall_30d"),
    ]:
        top = get_top_conditions(results, metric_key, n=5)
        print(f"\n  --- {metric_name} ---")
        print(f"  {'Condition':<35} {'N':>5} {'Place%':>7} {'Mean14':>8} {'P<014':>7} {'p-val14':>8} "
              f"{'Mean30':>8} {'P<030':>7} {'p-val30':>8} {'P10%':>6} {'Lift10':>7}")
        print("  " + "-" * 120)
        for r in top:
            print(f"  {r['condition']:<35} {r['n_triggered']:>5} "
                  f"{r['placement_rate']:>6.1%} {r['mean_14d']:>+7.2%} {r['prob_neg_14d']:>6.1%} "
                  f"{r['p_val_14d']:>7.4f} {r['mean_30d']:>+7.2%} {r['prob_neg_30d']:>6.1%} "
                  f"{r['p_val_30d']:>7.4f} {r['prob_p10']:>5.1%} {r['lift_p10']:>6.2f}")


def write_csv(all_results, etf_name):
    """Write results to CSV."""
    os.makedirs("./backtest", exist_ok=True)
    df = pd.DataFrame(all_results)
    if not df.empty:
        df = df.sort_values(by=["p_val_30d", "prob_p10"], ascending=[True, False])
    path = f"./backtest/indicator_scan_{etf_name}.csv"
    df.to_csv(path, index=False, float_format="%.6f")
    print(f"\n  CSV saved: {path}")


def write_markdown_report(all_etf_results):
    """Write a summary markdown report."""
    os.makedirs("./validate", exist_ok=True)
    path = "./validate/indicator_scan_report.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Indicator Scanner Report\n\n")
        f.write("## Methodology\n\n")
        f.write("- Forward returns computed using vectorized calendar-day search (`np.searchsorted`).\n")
        f.write("- 14d and 30d forward returns calculated from `close_adj` (or `close`).\n")
        f.write("- ~30 indicators computed using `pandas-ta` and native pandas.\n")
        f.write("- Quantile-based thresholds use **expanding-window** (252-day minimum lookback) to eliminate look-ahead bias.\n")
        f.write("- Single-indicator conditions use both fixed and expanding-quantile thresholds.\n")
        f.write("- NaN indicator rows (early rolling-window warmup) are explicitly excluded from both triggered and non-triggered groups.\n")
        f.write("- Combinations: AND/OR of top 10 conditions per metric per ETF (greedy) plus pre-specified known strategy combos.\n")
        f.write("- Minimum trigger days: 30 (singles), 20 (combinations).\n")
        f.write("- p-values from Welch's t-test vs non-triggered days.\n")
        f.write("- Lift = triggered P10 rate / baseline P10 rate.\n\n")

        for etf_key in ETF_CONFIG:
            etf_name = ETF_CONFIG[etf_key]["name"]
            results = [r for r in all_etf_results if r["etf"] == etf_name and r["type"] == "single"]
            combos  = [r for r in all_etf_results if r["etf"] == etf_name and r["type"] in ("combo", "known_combo")]

            f.write(f"## {etf_name}\n\n")

            for metric_name, metric_key in [
                ("Crash (P10 Tail)", "crash"),
                ("Short-term Fall (14d)", "fall_14d"),
                ("Medium-term Fall (30d)", "fall_30d"),
            ]:
                f.write(f"### Top 5 Single-Indicator Filters - {metric_name}\n\n")
                f.write(f"| Rank | Condition | N | Place% | Mean14d | P<014d | p-val | Mean30d | P<030d | p-val | P10% | Lift |\n")
                f.write(f"|------|-----------|---|--------|---------|--------|-------|---------|--------|-------|------|------|\n")
                top = get_top_conditions(results, metric_key, n=5)
                for i, r in enumerate(top, 1):
                    f.write(f"| {i} | {r['condition']} | {r['n_triggered']} | "
                              f"{r['placement_rate']:.1%} | {r['mean_14d']:+.2%} | {r['prob_neg_14d']:.1%} | "
                              f"{r['p_val_14d']:.4f} | {r['mean_30d']:+.2%} | {r['prob_neg_30d']:.1%} | "
                              f"{r['p_val_30d']:.4f} | {r['prob_p10']:.1%} | {r['lift_p10']:.2f} |\n")
                f.write("\n")

                # Top 3 combos for this metric (greedy + known)
                combo_list = get_top_conditions(combos, metric_key, n=3)
                if combo_list:
                    f.write(f"### Top 3 Combinations - {metric_name}\n\n")
                    f.write(f"| Rank | Condition | N | Place% | Mean14d | P<014d | p-val | Mean30d | P<030d | p-val | P10% | Lift |\n")
                    f.write(f"|------|-----------|---|--------|---------|--------|-------|---------|--------|-------|------|------|\n")
                    for i, r in enumerate(combo_list, 1):
                        f.write(f"| {i} | {r['condition']} | {r['n_triggered']} | "
                                  f"{r['placement_rate']:.1%} | {r['mean_14d']:+.2%} | {r['prob_neg_14d']:.1%} | "
                                  f"{r['p_val_14d']:.4f} | {r['mean_30d']:+.2%} | {r['prob_neg_30d']:.1%} | "
                                  f"{r['p_val_30d']:.4f} | {r['prob_p10']:.1%} | {r['lift_p10']:.2f} |\n")
                    f.write("\n")

            # Known combos section (always shown, not ranked against greedy combos)
            known = [r for r in all_etf_results if r["etf"] == etf_name and r["type"] == "known_combo"]
            if known:
                f.write(f"### Pre-Specified Known Strategy Combos\n\n")
                f.write(f"| Condition | N | Place% | Mean14d | P<014d | p-val | Mean30d | P<030d | p-val | P10% | Lift |\n")
                f.write(f"|-----------|---|--------|---------|--------|-------|---------|--------|-------|------|------|\n")
                for r in known:
                    f.write(f"| {r['condition']} | {r['n_triggered']} | "
                              f"{r['placement_rate']:.1%} | {r['mean_14d']:+.2%} | {r['prob_neg_14d']:.1%} | "
                              f"{r['p_val_14d']:.4f} | {r['mean_30d']:+.2%} | {r['prob_neg_30d']:.1%} | "
                              f"{r['p_val_30d']:.4f} | {r['prob_p10']:.1%} | {r['lift_p10']:.2f} |\n")
                f.write("\n")

    print(f"  Markdown report saved: {path}")


def main():
    all_results = []

    for etf_key in ETF_CONFIG:
        etf_name = ETF_CONFIG[etf_key]["name"]
        print(f"\n{'='*80}")
        print(f"  Processing {etf_name}")
        print(f"{'='*80}")

        # Load data
        df, close_col, high_col, low_col = load_etf_data(etf_key)
        print(f"  Loaded {len(df)} rows from {ETF_CONFIG[etf_key]['path']}")

        # Compute indicators
        df = compute_indicators(df, close_col, high_col, low_col)
        print(f"  Computed indicators.")

        # Compute forward returns
        df = compute_forward_returns(df, close_col)

        # Define conditions
        conditions = define_conditions(df, close_col)
        print(f"  Defined {len(conditions)} threshold conditions.")

        # Baseline tail thresholds (computed once, shared across all evaluations)
        valid_df = df.dropna(subset=["fwd_ret_14d", "fwd_ret_30d"])
        all_30 = valid_df["fwd_ret_30d"]
        p10_thresh  = all_30.quantile(0.10)
        p25_thresh  = all_30.quantile(0.25)
        baseline_p10 = (all_30 <= p10_thresh).mean()
        baseline_p25 = (all_30 <= p25_thresh).mean()

        # Evaluate single conditions
        single_results = evaluate_single_conditions(
            df, conditions, etf_name,
            p10_thresh, p25_thresh, baseline_p10, baseline_p25,
        )
        print(f"  Evaluated {len(single_results)} single-indicator conditions (>= {MIN_DAYS_SINGLE} triggers).")

        # Evaluate greedy combinations for each metric
        combo_results = []
        for metric_key in ["crash", "fall_14d", "fall_30d"]:
            top = get_top_conditions(single_results, metric_key, n=10)
            if len(top) >= 2:
                combo_results += evaluate_combinations(
                    df, top, conditions, etf_name,
                    p10_thresh, p25_thresh, baseline_p10, baseline_p25,
                )

        # Evaluate pre-specified KNOWN_COMBOS (always, regardless of greedy selection)
        known_results = []
        if etf_key in KNOWN_COMBOS:
            for cond_a_label, cond_b_label, op_name in KNOWN_COMBOS[etf_key]:
                if cond_a_label not in conditions or cond_b_label not in conditions:
                    print(f"  [WARN] Known combo skipped: {cond_a_label} / {cond_b_label} not in conditions")
                    continue
                label = f"{cond_a_label} {op_name} {cond_b_label}"
                op = (lambda a, b: a & b) if op_name == "AND" else (lambda a, b: a | b)
                mask = op(conditions[cond_a_label], conditions[cond_b_label])
                r = _compute_metrics(
                    valid_df, mask, etf_name, label, "known_combo",
                    p10_thresh, p25_thresh, baseline_p10, baseline_p25,
                    len(valid_df), MIN_DAYS_COMBO,
                )
                if r is not None:
                    known_results.append(r)
                    print(f"  Known combo: {label}  N={r['n_triggered']}  "
                          f"P10={r['prob_p10']:.1%}  Lift={r['lift_p10']:.2f}x  "
                          f"Mean30d={r['mean_30d']:+.2%}  p={r['p_val_30d']:.4f}")

        # Deduplicate combos: known combos always keep their type label so they
        # appear in the Known Combos report section even if the greedy search
        # also discovered them independently.
        known_labels = {r["condition"] for r in known_results}
        combo_results_relabelled = []
        for r in combo_results:
            if r["condition"] in known_labels:
                r = dict(r, type="known_combo")   # promote to known type
            combo_results_relabelled.append(r)

        seen = set()
        combo_results_deduped = []
        for r in combo_results_relabelled + known_results:
            if r["condition"] not in seen:
                seen.add(r["condition"])
                combo_results_deduped.append(r)

        print(f"  Evaluated {len(combo_results_deduped)} combination conditions "
              f"(greedy + {len(known_results)} known, >= {MIN_DAYS_COMBO} triggers).")

        all_etf_results = single_results + combo_results_deduped
        all_results.extend(all_etf_results)

        # Console output
        print_results(single_results, etf_name)

        # Write CSV
        write_csv(all_etf_results, etf_name)

    # Write Markdown report
    write_markdown_report(all_results)

    print(f"\n{'='*80}")
    print("  Indicator scanner complete.")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
