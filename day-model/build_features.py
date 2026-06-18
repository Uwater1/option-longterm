"""
Phase 1: Feature engineering for Day-Model XGBoost PM Return prediction.

Combines:
  - Early-bar features from first 6 five-minute bars (9:30-10:00) — extends day-trading/REPORT.md sec.6
  - Day-level indicators (RSI14, MACD, SMA20/50, ATR14, ROC10, BB%B, vol20) computed from
    PRIOR day's close_adj (NO look-ahead — values as of yesterday's close).

Target: PM return = sum of log returns over bars 24..47 (13:00-15:00 session).

Outputs: data/features_{ETF}.parquet per ETF.

Usage:
    python build_features.py                  # all ETFs
    python build_features.py -e 300           # one ETF
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_ta as ta
from scipy.stats import skew, kurtosis

warnings.filterwarnings("ignore")

ETF_CONFIG = {
    "300ETF":    {"file_5m": "510300_5m.parquet",   "file_1d": "510300_1d.parquet"},
    "50ETF":     {"file_5m": "50ETF_5m.parquet",    "file_1d": "50ETF_1d.parquet"},
    "500ETF":    {"file_5m": "500ETF_5m.parquet",   "file_1d": "500ETF_1d.parquet"},
    "588000ETF": {"file_5m": "588000ETF_5m.parquet","file_1d": "588000ETF_1d.parquet"},
    "159915ETF": {"file_5m": "159915ETF_5m.parquet","file_1d": "159915ETF_1d.parquet"},
}

ETF_CLI_MAP = {
    "300": "300ETF", "50": "50ETF", "500": "500ETF",
    "588000": "588000ETF", "159915": "159915ETF",
    "300ETF": "300ETF", "50ETF": "50ETF", "500ETF": "500ETF",
    "588000ETF": "588000ETF", "159915ETF": "159915ETF",
    "all": list(ETF_CONFIG.keys()),
}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR = Path(__file__).resolve().parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EARLY_BARS = 6          # 9:35..10:00 (matches REPORT.md sec.6)
BARS_PER_DAY = 48
BAR_LUNCH = 24          # first PM bar (13:00)
WARMUP_DAYS = 60        # drop first 60 days (SMA50/ATR14 warmup)


# ============================================================
# Day-level indicators (computed on full history, then shifted by 1)
# ============================================================
def compute_daylevel_indicators(df_1d: pd.DataFrame) -> pd.DataFrame:
    """Compute technical indicators on daily close_adj, shift by 1 to avoid look-ahead."""
    df = df_1d.sort_values("date").reset_index(drop=True).copy()
    px = df["close_adj"]

    # RSI(14)
    df["rsi14"] = ta.rsi(px, length=14)

    # MACD(12,26,9): histogram is signal-line divergence
    macd = ta.macd(px, fast=12, slow=26, signal=9)
    df["macd_hist"] = macd["MACDh_12_26_9"] if macd is not None else np.nan

    # SMA distances (trend context)
    sma20 = ta.sma(px, length=20)
    sma50 = ta.sma(px, length=50)
    df["sma20_dist"] = (px - sma20) / sma20
    df["sma50_dist"] = (px - sma50) / sma50

    # ATR(14) normalized by close
    hlcv = pd.DataFrame({
        "high": df["high_adj"], "low": df["low_adj"],
        "close": df["close_adj"],
    })
    atr14 = ta.atr(hlcv["high"], hlcv["low"], hlcv["close"], length=14)
    df["atr14_norm"] = atr14 / px

    # Rate of change 10d
    df["roc10"] = ta.roc(px, length=10) / 100.0  # decimal return

    # Bollinger Bands %B (20, 2σ)
    bbands = ta.bbands(px, length=20, std=2)
    if bbands is not None:
        upper = bbands.iloc[:, 0]   # BBU
        mid = bbands.iloc[:, 1]     # BBM
        lower = bbands.iloc[:, 2]   # BBL
        df["bb_pctb"] = (px - lower) / (upper - lower)
    else:
        df["bb_pctb"] = np.nan

    # 20-day realized volatility (log returns)
    log_ret = np.log(px / px.shift(1))
    df["vol20"] = log_ret.rolling(20).std() * np.sqrt(252)

    # ── Critical: shift ALL day-level features by 1 so they reflect prior day's close ──
    day_cols = ["rsi14", "macd_hist", "sma20_dist", "sma50_dist",
                "atr14_norm", "roc10", "bb_pctb", "vol20"]
    for col in day_cols:
        df[col] = df[col].shift(1)

    return df[["date"] + day_cols]


# ============================================================
# Early-bar features (first 6 bars of 5m data)
# ============================================================
def extract_day_early_features(day_5m: pd.DataFrame, prev_close: float) -> dict:
    """Extract 13 early features from first EARLY_BARS bars of one trading day.

    All features are computable by 10:00 AM (no look-ahead within the day).
    Returns NaN dict if insufficient data.
    """
    bars = day_5m.head(EARLY_BARS)
    if len(bars) < EARLY_BARS or prev_close <= 0 or prev_close is None or np.isnan(prev_close):
        return _empty_early_features()

    day_open = float(bars.iloc[0]["open"])
    if day_open <= 0:
        return _empty_early_features()

    op = bars["open"].values
    hi = bars["high"].values
    lo = bars["low"].values
    cl = bars["close"].values
    vol = bars["volume"].values

    # Bar log returns
    bar_ret = np.log(cl / np.maximum(op, 1e-10))

    full_day_vol = day_5m["volume"].mean()
    full_day_vol = full_day_vol if full_day_vol > 0 else 1.0

    gap_pct = (day_open - prev_close) / prev_close
    first_30min_return = (cl[-1] - day_open) / day_open
    early_realized_vol = float(np.nanstd(bar_ret) * np.sqrt(BARS_PER_DAY))
    early_range = (hi.max() - lo.min()) / day_open
    early_volume_ratio = vol.mean() / full_day_vol
    early_trend = _linear_slope(cl) / day_open
    early_momentum = (cl[-1] - cl[0]) / cl[0] if cl[0] > 0 else 0.0
    gap_direction = float(np.sign(gap_pct))
    first_bar_return = (cl[0] - op[0]) / op[0] if op[0] > 0 else 0.0
    first_bar_volume = vol[0] / full_day_vol
    # VWAP of first EARLY_BARS bars
    vwap = (cl * vol).sum() / max(vol.sum(), 1.0)
    early_vwap_dev = (cl[-1] - vwap) / vwap if vwap > 0 else 0.0
    # Higher-order moments of bar returns
    if len(bar_ret) >= 3 and np.std(bar_ret) > 1e-10:
        early_skew = float(skew(bar_ret))
        early_kurt = float(kurtosis(bar_ret, fisher=True))
    else:
        early_skew = 0.0
        early_kurt = 0.0

    return {
        "gap_pct": gap_pct,
        "first_30min_return": first_30min_return,
        "early_realized_vol": early_realized_vol,
        "early_range": early_range,
        "early_volume_ratio": early_volume_ratio,
        "early_trend": early_trend,
        "early_momentum": early_momentum,
        "gap_direction": gap_direction,
        "first_bar_return": first_bar_return,
        "first_bar_volume": first_bar_volume,
        "early_vwap_dev": early_vwap_dev,
        "early_skew": early_skew,
        "early_kurtosis": early_kurt,
    }


def _empty_early_features() -> dict:
    return {k: np.nan for k in [
        "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
        "early_volume_ratio", "early_trend", "early_momentum", "gap_direction",
        "first_bar_return", "first_bar_volume", "early_vwap_dev",
        "early_skew", "early_kurtosis",
    ]}


def _linear_slope(y: np.ndarray) -> float:
    """OLS slope of y against x = [0..n-1]."""
    n = len(y)
    if n < 2:
        return 0.0
    x = np.arange(n, dtype=float)
    x_mean = x.mean()
    y_mean = y.mean()
    denom = ((x - x_mean) ** 2).sum()
    if denom < 1e-12:
        return 0.0
    return float(((x - x_mean) * (y - y_mean)).sum() / denom)


# ============================================================
# PM return target (bars 24..47)
# ============================================================
def compute_pm_return(day_5m: pd.DataFrame) -> float:
    """Sum of intraday log returns over the PM session (bars 24..47)."""
    bars = day_5m.reset_index(drop=True)
    if len(bars) < BARS_PER_DAY:
        # use whatever exists after lunch
        pm = bars.iloc[BAR_LUNCH:]
    else:
        pm = bars.iloc[BAR_LUNCH:BARS_PER_DAY]
    if len(pm) < 2:
        return np.nan
    # Use close-to-close log returns of consecutive PM bars
    closes = pm["close"].values
    log_rets = np.log(closes[1:] / np.maximum(closes[:-1], 1e-10))
    return float(log_rets.sum())


# ============================================================
# Pipeline per ETF
# ============================================================
def build_features_for_etf(etf_name: str, save: bool = True) -> pd.DataFrame:
    cfg = ETF_CONFIG[etf_name]
    path_5m = DATA_DIR / cfg["file_5m"]
    path_1d = DATA_DIR / cfg["file_1d"]

    if not path_5m.exists() or not path_1d.exists():
        print(f"  [SKIP] {etf_name}: missing parquet ({path_5m.name} / {path_1d.name})")
        return pd.DataFrame()

    print(f"\n[{etf_name}] loading 5m + 1d ...")
    df_5m = pd.read_parquet(path_5m)
    df_1d = pd.read_parquet(path_1d)

    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
    df_5m["date"] = df_5m["datetime"].dt.normalize()
    df_5m = df_5m.sort_values(["date", "datetime"]).reset_index(drop=True)

    # ── Day-level indicators (shifted to prior day) ──
    daylevel = compute_daylevel_indicators(df_1d)

    # ── Per-day early features + PM return ──
    # prev_close on adjusted prices (per AGENTS.md rule)
    df_1d_sorted = df_1d.sort_values("date").reset_index(drop=True).copy()
    df_1d_sorted["prev_close_adj"] = df_1d_sorted["close_adj"].shift(1)
    df_1d_sorted["date"] = pd.to_datetime(df_1d_sorted["date"])
    prev_close_map = df_1d_sorted.set_index("date")["prev_close_adj"].to_dict()

    rows = []
    for date, day_df in df_5m.groupby("date", sort=True):
        date_ts = pd.Timestamp(date)
        prev_close = prev_close_map.get(date_ts, np.nan)
        early = extract_day_early_features(day_df, prev_close)
        early["date"] = date_ts
        early["pm_return"] = compute_pm_return(day_df)
        # AM return for diagnostics
        am = day_df.reset_index(drop=True).iloc[:BAR_LUNCH]
        if len(am) >= 2:
            am_closes = am["close"].values
            early["am_return"] = float(np.log(am_closes[-1] / np.maximum(am_closes[0], 1e-10)).sum() if False else
                                       np.log(np.maximum(am["close"].iloc[-1], 1e-10) /
                                              np.maximum(am["open"].iloc[0], 1e-10)))
        else:
            early["am_return"] = np.nan
        rows.append(early)

    early_df = pd.DataFrame(rows).set_index("date").sort_index()

    # ── Merge with day-level indicators ──
    daylevel["date"] = pd.to_datetime(daylevel["date"])
    daylevel = daylevel.set_index("date").sort_index()

    feat = early_df.join(daylevel, how="inner")

    # ── Drop warmup rows ──
    feat = feat.iloc[WARMUP_DAYS:].copy()

    # ── Drop any rows with NaN target (cannot use for training) ──
    n_before = len(feat)
    feat = feat.dropna(subset=["pm_return"]).copy()
    n_after = len(feat)

    day_cols = ["rsi14", "macd_hist", "sma20_dist", "sma50_dist",
                "atr14_norm", "roc10", "bb_pctb", "vol20"]
    early_cols = [c for c in feat.columns if c not in day_cols + ["pm_return", "am_return"]]

    print(f"  samples: {n_after} (dropped {n_before - n_after} NaN-target), "
          f"features: {len(early_cols)} early + {len(day_cols)} day-level = {len(early_cols) + len(day_cols)}")
    print(f"  target pm_return: mean={feat['pm_return'].mean()*100:.4f}%  "
          f"std={feat['pm_return'].std()*100:.4f}%  "
          f"Sharpe={feat['pm_return'].mean()/feat['pm_return'].std()*np.sqrt(252):.2f}")

    if save:
        out_path = OUT_DIR / f"features_{etf_name}.parquet"
        feat.to_parquet(out_path)
        print(f"  saved → {out_path}")

    return feat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="all",
                    help="ETF code: 300/50/500/588000/159915 or 'all'")
    args = ap.parse_args()

    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]

    print(f"Building day-model features for: {etfs}")
    print(f"  early window: first {EARLY_BARS} bars (9:30-10:00)")
    print(f"  warmup dropped: {WARMUP_DAYS} days")

    summary = []
    for etf in etfs:
        feat = build_features_for_etf(etf)
        if not feat.empty:
            summary.append({
                "ETF": etf,
                "n_days": len(feat),
                "date_start": feat.index.min().strftime("%Y-%m-%d"),
                "date_end": feat.index.max().strftime("%Y-%m-%d"),
                "pm_mean_pct": feat["pm_return"].mean() * 100,
                "pm_std_pct": feat["pm_return"].std() * 100,
                "pm_sharpe_ann": feat["pm_return"].mean() / feat["pm_return"].std() * np.sqrt(252),
            })

    if summary:
        sdf = pd.DataFrame(summary)
        print("\n=== Summary ===")
        print(sdf.to_string(index=False))


if __name__ == "__main__":
    main()
