"""
Phase 1: Feature engineering for Day-Model XGBoost/Linear PM Return prediction.

Combines:
  - Intraday early-bar features (50) from first 6 five-minute bars (9:30-10:00).
  - Day-level indicators (58) computed from prior day's close (shifted by 1 to prevent leakage),
    including technical indicators and Ricequant 3rd-party margin/capital flow/northbound quota.
  - Yesterday's features (22) representing the full-day and early-day properties of day t-1.

Target: PM return = sum of log returns over bars 24..47 (13:00-15:00 session).
Outputs: data/features_{ETF}.parquet per ETF.
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_ta as ta
from scipy.stats import skew, kurtosis

warnings.filterwarnings("ignore")

# Feature lists
EARLY_FEATURES = [
    # Existing (13)
    "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
    "early_volume_ratio", "early_trend", "early_momentum", "gap_direction",
    "first_bar_return", "first_bar_volume", "early_vwap_dev",
    "early_skew", "early_kurtosis",
    # New bar-by-bar price returns (6)
    "bar_ret_0", "bar_ret_1", "bar_ret_2", "bar_ret_3", "bar_ret_4", "bar_ret_5",
    # New bar-by-bar volume ratios (6)
    "bar_vol_0", "bar_vol_1", "bar_vol_2", "bar_vol_3", "bar_vol_4", "bar_vol_5",
    # New bar-by-bar range normalized (6)
    "bar_rng_0", "bar_rng_1", "bar_rng_2", "bar_rng_3", "bar_rng_4", "bar_rng_5",
    # New bar-by-bar body-to-range (6)
    "bar_body_rng_0", "bar_body_rng_1", "bar_body_rng_2", "bar_body_rng_3", "bar_body_rng_4", "bar_body_rng_5",
    # New bar-by-bar VWAP dev (6)
    "bar_vwap_dev_0", "bar_vwap_dev_1", "bar_vwap_dev_2", "bar_vwap_dev_3", "bar_vwap_dev_4", "bar_vwap_dev_5",
    # New shape/trend indicators (7)
    "num_up_bars", "max_up_ret", "max_down_ret", "cl_pos_in_range",
    "body_to_range_ratio", "total_path_length", "volume_slope"
]

DAY_FEATURES = [
    # Existing (8)
    "rsi14", "macd_hist", "sma20_dist", "sma50_dist",
    "atr14_norm", "roc10", "bb_pctb", "vol20",
    # New trend/ma dist (5)
    "sma10_dist", "sma100_dist", "sma200_dist", "ema12_dist", "ema26_dist",
    # New momentum/osc (12)
    "rsi5", "rsi21", "roc5", "roc20", "roc60", "cci14", "willr14", "stoch_k", "stoch_d", "mfi14", "aroon_osc",
    # New realized vol/range (6)
    "vol5", "vol10", "vol60", "vol_ratio_5_20", "vol_ratio_10_60", "bb_width",
    # New advanced vol (4)
    "vol_pk10", "vol_pk20", "vol_gk10", "vol_gk20",
    # New volume ratio (2)
    "volume_sma_ratio", "volume_sma_ratio_long",
    # New 3rd party margin (10)
    "margin_balance", "buy_on_margin_value", "margin_repayment", "short_balance",
    "short_balance_quantity", "short_sell_quantity", "short_repayment_quantity",
    "total_balance", "margin_net_buy", "margin_short_ratio",
    # New 3rd party cap flow (6)
    "capital_buy_volume", "capital_buy_value", "capital_sell_volume", "capital_sell_value",
    "capital_net_value", "capital_net_ratio",
    # New 3rd party northbound (3)
    "northbound_buy", "northbound_sell", "northbound_net"
]

YESTERDAY_FEATURES = [
    "yesterday_pm_return", "yesterday_am_return",
    "yesterday_gap_pct", "yesterday_first_30min_return", "yesterday_early_realized_vol",
    "yesterday_early_range", "yesterday_early_volume_ratio", "yesterday_early_trend",
    "yesterday_early_momentum", "yesterday_first_bar_return", "yesterday_first_bar_volume",
    "yesterday_early_vwap_dev", "yesterday_early_skew", "yesterday_early_kurtosis",
    "yesterday_day_range", "yesterday_day_realized_vol", "yesterday_day_close_pos",
    "yesterday_day_pm_am_vol_ratio", "yesterday_day_late_mom", "yesterday_day_vwap_dev",
    "yesterday_day_skew", "yesterday_day_kurtosis"
]

FEATURES = EARLY_FEATURES + DAY_FEATURES + YESTERDAY_FEATURES

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
# Caching helpers for rqdatac
# ============================================================
def get_cached_margin_data(order_book_ids, start_date, end_date) -> pd.DataFrame:
    cache_path = DATA_DIR / "securities_margin.parquet"
    if cache_path.exists():
        try:
            return pd.read_parquet(cache_path)
        except Exception as e:
            print(f"    [WARN] Failed to read margin cache: {e}")
            
    print("    Downloading securities margin from Ricequant...")
    import rqdatac
    if not rqdatac.initialized():
        rqdatac.init()
    df_list = []
    for obid in order_book_ids:
        try:
            df = rqdatac.get_securities_margin(obid, start_date=start_date, end_date=end_date)
            if df is not None and not df.empty:
                df_list.append(df)
        except Exception as e:
            print(f"      [WARN] get_securities_margin failed for {obid}: {e}")
    if df_list:
        full_df = pd.concat(df_list)
        full_df.to_parquet(cache_path)
        return full_df
    return pd.DataFrame()


def get_cached_capital_flow(order_book_ids, start_date, end_date) -> pd.DataFrame:
    cache_path = DATA_DIR / "capital_flow.parquet"
    if cache_path.exists():
        try:
            return pd.read_parquet(cache_path)
        except Exception as e:
            print(f"    [WARN] Failed to read capital flow cache: {e}")
            
    print("    Downloading capital flow from Ricequant...")
    import rqdatac
    if not rqdatac.initialized():
        rqdatac.init()
    df_list = []
    for obid in order_book_ids:
        try:
            df = rqdatac.get_capital_flow(obid, start_date=start_date, end_date=end_date)
            if df is not None and not df.empty:
                df_list.append(df)
        except Exception as e:
            print(f"      [WARN] get_capital_flow failed for {obid}: {e}")
    if df_list:
        full_df = pd.concat(df_list)
        full_df.to_parquet(cache_path)
        return full_df
    return pd.DataFrame()


def get_cached_stock_connect_quota(start_date, end_date) -> pd.DataFrame:
    cache_path = DATA_DIR / "stock_connect_quota.parquet"
    if cache_path.exists():
        try:
            return pd.read_parquet(cache_path)
        except Exception as e:
            print(f"    [WARN] Failed to read stock connect quota cache: {e}")
            
    print("    Downloading stock connect quota from Ricequant...")
    import rqdatac
    if not rqdatac.initialized():
        rqdatac.init()
    try:
        df = rqdatac.get_stock_connect_quota(start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            df.to_parquet(cache_path)
            return df
    except Exception as e:
        print(f"    [WARN] get_stock_connect_quota failed: {e}")
    return pd.DataFrame()


# ============================================================
# Day-level indicators (computed on full history, then shifted by 1)
# ============================================================
def compute_daylevel_indicators(df_1d: pd.DataFrame, margin_cache: pd.DataFrame, cap_flow_cache: pd.DataFrame, quota_cache: pd.DataFrame) -> pd.DataFrame:
    """Compute technical and 3rd party indicators on daily close_adj, shift by 1 to avoid look-ahead."""
    df = df_1d.sort_values("date").reset_index(drop=True).copy()
    px = df["close_adj"]

    # 1) Technical Indicators
    # RSI(14)
    df["rsi14"] = ta.rsi(px, length=14)
    # MACD(12,26,9)
    macd = ta.macd(px, fast=12, slow=26, signal=9)
    df["macd_hist"] = macd["MACDh_12_26_9"] if macd is not None else np.nan

    # SMA distances
    sma20 = ta.sma(px, length=20)
    sma50 = ta.sma(px, length=50)
    df["sma20_dist"] = (px - sma20) / sma20
    df["sma50_dist"] = (px - sma50) / sma50

    # ATR(14)
    hlcv = pd.DataFrame({
        "high": df["high_adj"], "low": df["low_adj"],
        "close": df["close_adj"],
    })
    atr14 = ta.atr(hlcv["high"], hlcv["low"], hlcv["close"], length=14)
    df["atr14_norm"] = atr14 / px

    # ROC 10
    df["roc10"] = ta.roc(px, length=10) / 100.0

    # BB %B
    bbands = ta.bbands(px, length=20, std=2)
    if bbands is not None:
        upper = bbands.iloc[:, 0]
        mid = bbands.iloc[:, 1]
        lower = bbands.iloc[:, 2]
        df["bb_pctb"] = (px - lower) / (upper - lower + 1e-8)
        df["bb_width"] = (upper - lower) / (mid + 1e-8)
    else:
        df["bb_pctb"] = np.nan
        df["bb_width"] = np.nan

    # Realized volatility
    log_ret = np.log(px / px.shift(1))
    df["vol20"] = log_ret.rolling(20).std() * np.sqrt(252)

    # 2) New Technical Indicators
    sma10 = ta.sma(px, length=10)
    df["sma10_dist"] = (px - sma10) / sma10
    sma100 = ta.sma(px, length=100)
    df["sma100_dist"] = (px - sma100) / sma100
    sma200 = ta.sma(px, length=200)
    df["sma200_dist"] = (px - sma200) / sma200
    ema12 = ta.ema(px, length=12)
    df["ema12_dist"] = (px - ema12) / ema12
    ema26 = ta.ema(px, length=26)
    df["ema26_dist"] = (px - ema26) / ema26

    df["rsi5"] = ta.rsi(px, length=5)
    df["rsi21"] = ta.rsi(px, length=21)
    df["roc5"] = ta.roc(px, length=5) / 100.0
    df["roc20"] = ta.roc(px, length=20) / 100.0
    df["roc60"] = ta.roc(px, length=60) / 100.0

    df["vol5"] = log_ret.rolling(5).std() * np.sqrt(252)
    df["vol10"] = log_ret.rolling(10).std() * np.sqrt(252)
    df["vol60"] = log_ret.rolling(60).std() * np.sqrt(252)
    df["vol_ratio_5_20"] = df["vol5"] / (df["vol20"] + 1e-8)
    df["vol_ratio_10_60"] = df["vol10"] / (df["vol60"] + 1e-8)

    # Parkinson range-based volatility
    hl_ratio = np.log(df["high_adj"] / df["low_adj"])
    pk = (hl_ratio ** 2) / (4 * np.log(2))
    df["vol_pk10"] = np.sqrt(pk.rolling(10).mean()) * np.sqrt(252)
    df["vol_pk20"] = np.sqrt(pk.rolling(20).mean()) * np.sqrt(252)

    # Garman-Klass range-and-close volatility
    co_ratio = np.log(df["close_adj"] / df["open_adj"])
    gk = 0.5 * (hl_ratio ** 2) - (2 * np.log(2) - 1) * (co_ratio ** 2)
    gk = np.maximum(gk, 0.0)
    df["vol_gk10"] = np.sqrt(gk.rolling(10).mean()) * np.sqrt(252)
    df["vol_gk20"] = np.sqrt(gk.rolling(20).mean()) * np.sqrt(252)

    # ADX, DMP, DMN
    adx = ta.adx(high=df["high_adj"], low=df["low_adj"], close=df["close_adj"], length=14)
    if adx is not None:
        df["adx14"] = adx["ADX_14"] / 100.0
        df["dmp14"] = adx["DMP_14"] / 100.0
        df["dmn14"] = adx["DMN_14"] / 100.0
    else:
        df["adx14"] = np.nan
        df["dmp14"] = np.nan
        df["dmn14"] = np.nan

    df["cci14"] = ta.cci(high=df["high_adj"], low=df["low_adj"], close=df["close_adj"], length=14) / 100.0
    df["willr14"] = ta.willr(high=df["high_adj"], low=df["low_adj"], close=df["close_adj"], length=14) / 100.0
    
    stoch = ta.stoch(high=df["high_adj"], low=df["low_adj"], close=df["close_adj"], k=14, d=3)
    if stoch is not None:
        df["stoch_k"] = stoch["STOCHk_14_3_3"] / 100.0
        df["stoch_d"] = stoch["STOCHd_14_3_3"] / 100.0
    else:
        df["stoch_k"] = np.nan
        df["stoch_d"] = np.nan

    df["mfi14"] = ta.mfi(high=df["high_adj"], low=df["low_adj"], close=df["close_adj"], volume=df["volume"], length=14) / 100.0
    
    aroon = ta.aroon(high=df["high_adj"], low=df["low_adj"], length=14)
    df["aroon_osc"] = aroon["AROONOSC_14"] / 100.0 if aroon is not None else np.nan

    df["volume_sma_ratio"] = df["volume"] / df["volume"].rolling(20).mean()
    df["volume_sma_ratio_long"] = df["volume"].rolling(5).mean() / df["volume"].rolling(60).mean()

    # 3) Ricequant 3rd Party Indicators from Caches
    order_book_id = df["order_book_id"].iloc[0]
    df["date"] = pd.to_datetime(df["date"])

    # Securities Margin
    if margin_cache is not None and not margin_cache.empty:
        try:
            margin = margin_cache.reset_index()
            margin["date"] = pd.to_datetime(margin["date"])
            etf_margin = margin[margin["order_book_id"] == order_book_id].copy()
            if not etf_margin.empty:
                etf_margin = etf_margin.set_index("date").drop(columns=["order_book_id"], errors="ignore")
                etf_margin = etf_margin.rename(columns={
                    "short_sell_quantity": "short_sell_quantity",
                    "short_repayment_quantity": "short_repayment_quantity",
                    "short_balance_quantity": "short_balance_quantity"
                })
                etf_margin["margin_net_buy"] = etf_margin["buy_on_margin_value"] - etf_margin["margin_repayment"]
                etf_margin["margin_short_ratio"] = etf_margin["margin_balance"] / (etf_margin["short_balance"] + 1e-8)
                margin_cols = [c for c in etf_margin.columns if c in DAY_FEATURES]
                df = df.merge(etf_margin[margin_cols], on="date", how="left")
        except Exception as e:
            print(f"    [WARN] Failed to merge margin cache: {e}")

    # Active Capital Flow
    if cap_flow_cache is not None and not cap_flow_cache.empty:
        try:
            cap_flow = cap_flow_cache.reset_index()
            cap_flow["date"] = pd.to_datetime(cap_flow["date"])
            etf_cap = cap_flow[cap_flow["order_book_id"] == order_book_id].copy()
            if not etf_cap.empty:
                etf_cap = etf_cap.set_index("date").drop(columns=["order_book_id"], errors="ignore")
                etf_cap = etf_cap.rename(columns={
                    "buy_volume": "capital_buy_volume",
                    "buy_value": "capital_buy_value",
                    "sell_volume": "capital_sell_volume",
                    "sell_value": "capital_sell_value"
                })
                etf_cap["capital_net_value"] = etf_cap["capital_buy_value"] - etf_cap["capital_sell_value"]
                etf_cap["capital_net_ratio"] = (etf_cap["capital_buy_value"] - etf_cap["capital_sell_value"]) / (etf_cap["capital_buy_value"] + etf_cap["capital_sell_value"] + 1e-8)
                cap_cols = [c for c in etf_cap.columns if c in DAY_FEATURES]
                df = df.merge(etf_cap[cap_cols], on="date", how="left")
        except Exception as e:
            print(f"    [WARN] Failed to merge capital flow cache: {e}")

    # Market-Wide Northbound Flow
    if quota_cache is not None and not quota_cache.empty:
        try:
            quota = quota_cache.reset_index()
            quota["datetime"] = pd.to_datetime(quota["datetime"])
            nb_quota = quota[quota["connect"].isin(["hk_to_sh", "hk_to_sz"])]
            nb_grouped = nb_quota.groupby("datetime")[["buy_turnover", "sell_turnover"]].sum()
            nb_grouped.index.name = "date"
            nb_grouped["northbound_net"] = nb_grouped["buy_turnover"] - nb_grouped["sell_turnover"]
            nb_grouped = nb_grouped.rename(columns={
                "buy_turnover": "northbound_buy",
                "sell_turnover": "northbound_sell"
            })
            nb_cols = [c for c in nb_grouped.columns if c in DAY_FEATURES]
            df = df.merge(nb_grouped[nb_cols], on="date", how="left")
        except Exception as e:
            print(f"    [WARN] Failed to merge northbound cache: {e}")

    # Check and fill missing columns/NaNs robustly
    for col in DAY_FEATURES:
        if col not in df.columns:
            df[col] = np.nan
        col_mean = df[col].mean()
        if pd.isna(col_mean):
            col_mean = 0.0
        df[col] = df[col].fillna(col_mean)

    # Shift all daily indicators by 1 to prevent leakage
    for col in DAY_FEATURES:
        df[col] = df[col].shift(1)

    return df[["date"] + DAY_FEATURES]


# ============================================================
# Early-bar features (first 6 bars of 5m data)
# ============================================================
def extract_day_early_features(day_5m: pd.DataFrame, prev_close: float, expected_bar_vol: float) -> dict:
    """Extract early features from first 6 bars of one trading day (computable by 10:00 AM)."""
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

    gap_pct = (day_open - prev_close) / prev_close
    first_30min_return = (cl[-1] - day_open) / day_open
    early_realized_vol = float(np.nanstd(bar_ret) * np.sqrt(BARS_PER_DAY))
    early_range = (hi.max() - lo.min()) / day_open
    early_volume_ratio = vol.mean() / expected_bar_vol
    early_trend = _linear_slope(cl) / day_open
    early_momentum = (cl[-1] - cl[0]) / cl[0] if cl[0] > 0 else 0.0
    gap_direction = float(np.sign(gap_pct))
    first_bar_return = (cl[0] - op[0]) / op[0] if op[0] > 0 else 0.0
    first_bar_volume = vol[0] / expected_bar_vol
    
    # VWAP of first 6 bars
    vwap = (cl * vol).sum() / max(vol.sum(), 1.0)
    early_vwap_dev = (cl[-1] - vwap) / vwap if vwap > 0 else 0.0
    
    if len(bar_ret) >= 3 and np.std(bar_ret) > 1e-10:
        early_skew = float(skew(bar_ret))
        early_kurt = float(kurtosis(bar_ret, fisher=True))
    else:
        early_skew = 0.0
        early_kurt = 0.0

    res = {
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

    # Add 37 new early-bar/price action features
    for i in range(6):
        res[f"bar_ret_{i}"] = float(np.log(cl[i] / max(op[i], 1e-10)))
    for i in range(6):
        res[f"bar_vol_{i}"] = float(vol[i] / expected_bar_vol)
    for i in range(6):
        res[f"bar_rng_{i}"] = float((hi[i] - lo[i]) / max(op[i], 1e-10))
    for i in range(6):
        res[f"bar_body_rng_{i}"] = float((cl[i] - op[i]) / (hi[i] - lo[i] + 1e-8))
    for i in range(6):
        cum_vol = max(vol[:i+1].sum(), 1.0)
        cum_vwap = (cl[:i+1] * vol[:i+1]).sum() / cum_vol
        res[f"bar_vwap_dev_{i}"] = float((cl[i] - cum_vwap) / max(cum_vwap, 1e-10))

    res["num_up_bars"] = float((cl > op).sum())
    res["max_up_ret"] = float((hi.max() - op[0]) / max(op[0], 1e-10))
    res["max_down_ret"] = float((lo.min() - op[0]) / max(op[0], 1e-10))
    res["cl_pos_in_range"] = float((cl[-1] - lo.min()) / (hi.max() - lo.min() + 1e-8))
    res["body_to_range_ratio"] = float(abs(cl[-1] - op[0]) / (hi.max() - lo.min() + 1e-8))
    res["total_path_length"] = float(np.sum(np.abs(bar_ret)))
    res["volume_slope"] = float(_linear_slope(vol) / expected_bar_vol)

    return res


def _empty_early_features() -> dict:
    return {k: np.nan for k in EARLY_FEATURES}


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
# Full-day features (to be shifted for yesterday features)
# ============================================================
def extract_day_full_features(day_5m: pd.DataFrame) -> dict:
    closes = day_5m["close"].values
    highs = day_5m["high"].values
    lows = day_5m["low"].values
    opens = day_5m["open"].values
    vols = day_5m["volume"].values
    
    if len(closes) < 2:
        return {
            "day_range": np.nan, "day_realized_vol": np.nan, "day_close_pos": np.nan,
            "day_pm_am_vol_ratio": np.nan, "day_late_mom": np.nan, "day_vwap_dev": np.nan,
            "day_skew": np.nan, "day_kurtosis": np.nan
        }
        
    day_open = opens[0]
    day_range = (highs.max() - lows.min()) / day_open if day_open > 0 else np.nan
    
    log_rets = np.log(closes[1:] / np.maximum(closes[:-1], 1e-10))
    day_realized_vol = float(np.nanstd(log_rets) * np.sqrt(BARS_PER_DAY))
    
    day_close_pos = (closes[-1] - lows.min()) / (highs.max() - lows.min() + 1e-8)
    
    am_vol = vols[:BAR_LUNCH].mean()
    pm_vol = vols[BAR_LUNCH:].mean()
    day_pm_am_vol_ratio = pm_vol / am_vol if am_vol > 0 else np.nan
    
    day_late_mom = (closes[-1] - closes[-7]) / closes[-7] if len(closes) >= 7 and closes[-7] > 0 else np.nan
    
    day_vwap = (closes * vols).sum() / max(vols.sum(), 1.0)
    day_vwap_dev = (closes[-1] - day_vwap) / day_vwap if day_vwap > 0 else np.nan
    
    day_skew = float(skew(log_rets)) if len(log_rets) >= 3 and np.std(log_rets) > 1e-10 else 0.0
    day_kurtosis = float(kurtosis(log_rets, fisher=True)) if len(log_rets) >= 3 and np.std(log_rets) > 1e-10 else 0.0
    
    return {
        "day_range": day_range,
        "day_realized_vol": day_realized_vol,
        "day_close_pos": day_close_pos,
        "day_pm_am_vol_ratio": day_pm_am_vol_ratio,
        "day_late_mom": day_late_mom,
        "day_vwap_dev": day_vwap_dev,
        "day_skew": day_skew,
        "day_kurtosis": day_kurtosis
    }


# ============================================================
# PM return target (bars 24..47)
# ============================================================
def compute_pm_return(day_5m: pd.DataFrame) -> float:
    """Sum of intraday log returns over the PM session (bars 24..47)."""
    bars = day_5m.reset_index(drop=True)
    if len(bars) < BARS_PER_DAY:
        pm = bars.iloc[BAR_LUNCH:]
    else:
        pm = bars.iloc[BAR_LUNCH:BARS_PER_DAY]
    if len(pm) < 2:
        return np.nan
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

    # ── Fetch/Load caches once for all ETFs ──
    all_etf_ids = ["510300.XSHG", "510050.XSHG", "510500.XSHG", "588000.XSHG", "159915.XSHE"]
    margin_df = get_cached_margin_data(all_etf_ids, "2015-01-01", "2026-06-19")
    cap_df = get_cached_capital_flow(all_etf_ids, "2015-01-01", "2026-06-19")
    quota_df = get_cached_stock_connect_quota("2015-01-01", "2026-06-19")

    # ── Day-level indicators (shifted to prior day) ──
    daylevel = compute_daylevel_indicators(df_1d, margin_df, cap_df, quota_df)

    # ── Per-day early features + PM return ──
    df_1d_sorted = df_1d.sort_values("date").reset_index(drop=True).copy()
    df_1d_sorted["prev_close_adj"] = df_1d_sorted["close_adj"].shift(1)
    df_1d_sorted["rolling_volume_20d"] = df_1d_sorted["volume"].rolling(20).mean()
    df_1d_sorted["expected_daily_volume"] = df_1d_sorted["rolling_volume_20d"].shift(1)
    df_1d_sorted["date"] = pd.to_datetime(df_1d_sorted["date"])
    prev_close_map = df_1d_sorted.set_index("date")["prev_close_adj"].to_dict()
    expected_vol_map = df_1d_sorted.set_index("date")["expected_daily_volume"].to_dict()

    fallback_daily_vol = df_1d_sorted["volume"].median()
    if pd.isna(fallback_daily_vol) or fallback_daily_vol <= 0:
        fallback_daily_vol = 1000000.0

    rows = []
    for date, day_df in df_5m.groupby("date", sort=True):
        date_ts = pd.Timestamp(date)
        prev_close = prev_close_map.get(date_ts, np.nan)
        
        expected_daily_vol = expected_vol_map.get(date_ts, np.nan)
        if pd.isna(expected_daily_vol) or expected_daily_vol <= 0:
            expected_daily_vol = fallback_daily_vol
        expected_bar_vol = expected_daily_vol / 48.0
        
        early = extract_day_early_features(day_df, prev_close, expected_bar_vol)
        early["date"] = date_ts
        early["pm_return"] = compute_pm_return(day_df)
        
        # AM return for diagnostics
        am = day_df.reset_index(drop=True).iloc[:BAR_LUNCH]
        if len(am) >= 2:
            early["am_return"] = float(np.log(np.maximum(am["close"].iloc[-1], 1e-10) /
                                              np.maximum(am["open"].iloc[0], 1e-10)))
        else:
            early["am_return"] = np.nan
            
        # Compute day full features (to be shifted later)
        full_feats = extract_day_full_features(day_df)
        for k, v in full_feats.items():
            early[k] = v
            
        rows.append(early)

    early_df = pd.DataFrame(rows).set_index("date").sort_index()

    # Shift yesterday features by 1 day
    cols_to_shift = [
        "pm_return", "am_return",
        "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
        "early_volume_ratio", "early_trend", "early_momentum", "first_bar_return",
        "first_bar_volume", "early_vwap_dev", "early_skew", "early_kurtosis",
        "day_range", "day_realized_vol", "day_close_pos", "day_pm_am_vol_ratio",
        "day_late_mom", "day_vwap_dev", "day_skew", "day_kurtosis"
    ]
    for col in cols_to_shift:
        early_df[f"yesterday_{col}"] = early_df[col].shift(1)

    # ── Merge with day-level indicators ──
    daylevel["date"] = pd.to_datetime(daylevel["date"])
    daylevel = daylevel.set_index("date").sort_index()

    feat = early_df.join(daylevel, how="inner")

    # ── Drop warmup rows ──
    feat = feat.iloc[WARMUP_DAYS:].copy()

    # ── Drop any rows with NaN target ──
    n_before = len(feat)
    feat = feat.dropna(subset=["pm_return"]).copy()
    n_after = len(feat)

    print(f"  samples: {n_after} (dropped {n_before - n_after} NaN-target), "
          f"features: {len(FEATURES)}")
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
