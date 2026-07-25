"""
Phase 1: Feature engineering for Day-Model XGBoost/Linear trade_return prediction.

Combines:
  - Intraday early-bar features (50) from first 6 five-minute bars (9:30-10:00).
    Causality: per-ETF ``DECISION_BAR`` below controls how many bars are actually
    consumed (bars beyond ``decision_bar`` are padded with 0.0).
  - Day-level indicators (58) computed from prior day's close (shifted by 1 to prevent leakage),
    including technical indicators and option-derived features.
  - Yesterday's features (22) representing the full-day and early-day properties of day t-1.

Primary target: ``trade_return`` = log(close[EXIT_BAR] / open[decision_bar+1])
  - Mirrors actual trade P&L in daytrade/backtest.py exactly
  - Entry at open of bar after decision; exit at close of bar 42 (14:35)

Diagnostic target: ``pm_return`` = sum of log returns over bars 24..47 (13:00-15:00)
  - Retained for IC sanity-checks vs the old pm_return baseline.

Outputs: data/features_{ETF}.parquet per ETF.
"""
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Parse command line argument --include-deprecated first, before importing features_extra!
if "--include-deprecated" in sys.argv:
    os.environ["INCLUDE_DEPRECATED"] = "1"

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import math
import pandas_ta as ta
from scipy.stats import skew, kurtosis

# New feature module: 91 early-bar (numba njit) + 14 day-level + 3 yesterday-mirror
# features from feature.csv. See day-model/features_extra.py for impl details.
# NOTE: EARLY_EXTRA and YESTERDAY_EXTRA are dynamically filtered at import time
# to exclude deprecated features (never selected/active across all 5 ETFs) by default.
from numba_utils import black_iv
from features_extra import (
    EARLY_EXTRA,
    DAY_EXTRA,
    YESTERDAY_EXTRA,
    extract_early_extras,
    empty_early_extras,
    compute_daylevel_extras,
)
from deprecate_features import (
    INCLUDE_DEPRECATED,
    DEPRECATED_BASE_FEATURES,
)

warnings.filterwarnings("ignore")

# Feature lists
BASE_EARLY_FEATURES = [
    # Existing (11)
    "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
    "early_trend", "early_momentum",
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

BASE_DAY_FEATURES = [
    # Existing (7)
    "macd_hist", "sma20_dist", "sma50_dist",
    "atr14_norm", "roc10", "bb_pctb", "vol20",
    # New trend/ma dist (4)
    "sma10_dist", "sma100_dist", "sma200_dist", "ema12_dist",
    # New momentum/osc (11)
    "rsi5", "rsi21", "roc5", "roc20", "roc60", "cci14", "willr14", "stoch_k", "stoch_d", "mfi14", "aroon_osc",
    # New realized vol/range (6)
    "vol5", "vol10", "vol60", "vol_ratio_5_20", "vol_ratio_10_60", "bb_width",
    # New advanced vol (3)
    "vol_pk20", "vol_gk10", "vol_gk20",
    # New volume ratio (2)
    "volume_sma_ratio", "volume_sma_ratio_long",
    # New Option Derived Features (8)
    "iv", "iv_vol_ratio", "vix", "vix_vol_ratio", "vix_iv_spread", "vix_iv_ratio",
    "iv_diff_1d", "vix_diff_1d",
    # --- Mined Features v1 (44) ---
    "tech_value_rotation", "yesterday_limit_up_touch", "limit_up_proximity_day", "limit_down_proximity_day",
    "yesterday_limit_down_touch", "growth_momentum_ratio", "high_beta_vol_ratio", "retail_turnover_acceleration",
    "vix_skew_proxy", "iv_term_structure", "vix_rolling_percentile_60d", "iv_corridor_width",
    "yesterday_vix_early_drift", "vix_realized_spread", "iv_acceleration_1d", "option_volume_pc_ratio",
    "option_oi_growth", "iv_envelope_deviation",
    "demark_setup_count_day", "consecutive_inside_bars_3d", "outside_bar_reversal_day", "wavetrend_osc_day",
    "wavetrend_cross_day", "keltner_squeeze_width", "stoch_rsi_divergence", "yesterday_wavetrend_osc",
    "yesterday_stoch_rsi_cross", "cvd_divergence_day", "yesterday_illiquidity_amihud", "turtle_channel_proximity_day",
    "chande_momentum_osc_day", "coppock_curve_day", "elder_ray_power_spread",
    # GARCH Volatility and HMM Regime Features
    "garch_vol_daily", "garch_vol_2h", "garch_vol_1h", "garch_state",
    "garch_vol_daily_diff", "garch_vol_2h_diff", "garch_vol_1h_diff"
]

BASE_YESTERDAY_FEATURES = [
    "yesterday_pm_return", "yesterday_am_return",
    "yesterday_gap_pct", "yesterday_first_30min_return", "yesterday_early_realized_vol",
    "yesterday_early_range", "yesterday_early_volume_ratio", "yesterday_early_trend",
    "yesterday_early_momentum", "yesterday_first_bar_return", "yesterday_first_bar_volume",
    "yesterday_early_vwap_dev", "yesterday_early_skew", "yesterday_early_kurtosis",
    "yesterday_day_range", "yesterday_day_realized_vol", "yesterday_day_close_pos",
    "yesterday_day_pm_am_vol_ratio", "yesterday_day_late_mom", "yesterday_day_vwap_dev",
    "yesterday_day_skew", "yesterday_day_kurtosis",
    # --- Mined Features v1 Yesterday (6) ---
    "yesterday_afternoon_reversal", "yesterday_lunch_gap", "yesterday_pm_am_vol_ratio",
    "yesterday_afternoon_momentum", "yesterday_midday_drawdown", "yesterday_cvd_close"
]

EARLY_FEATURES = (
    BASE_EARLY_FEATURES
    if INCLUDE_DEPRECATED
    else [f for f in BASE_EARLY_FEATURES if f not in DEPRECATED_BASE_FEATURES]
) + EARLY_EXTRA

DAY_FEATURES = (
    BASE_DAY_FEATURES
    if INCLUDE_DEPRECATED
    else [f for f in BASE_DAY_FEATURES if f not in DEPRECATED_BASE_FEATURES]
) + DAY_EXTRA

YESTERDAY_FEATURES = (
    BASE_YESTERDAY_FEATURES
    if INCLUDE_DEPRECATED
    else [f for f in BASE_YESTERDAY_FEATURES if f not in DEPRECATED_BASE_FEATURES]
) + YESTERDAY_EXTRA

FEATURES = EARLY_FEATURES + DAY_FEATURES + YESTERDAY_FEATURES

ETF_CONFIG = {
    "300ETF":    {"file_5m": "510300_5m.parquet",   "file_1d": "510300_1d.parquet"},
    "50ETF":     {"file_5m": "50ETF_5m.parquet",    "file_1d": "50ETF_1d.parquet"},
    "500ETF":    {"file_5m": "500ETF_5m.parquet",   "file_1d": "500ETF_1d.parquet"},
    "588000ETF": {"file_5m": "588000ETF_5m.parquet","file_1d": "588000ETF_1d.parquet"},
    "159915ETF": {"file_5m": "159915ETF_5m.parquet","file_1d": "159915ETF_1d.parquet"},
}

INDEX_CONFIG = {
    "300ETF":    {"file_5m": "000300_5m.parquet",   "file_1d": "000300_1d.parquet"},
    "50ETF":     {"file_5m": "000016_5m.parquet",   "file_1d": "000016_1d.parquet"},
    "500ETF":    {"file_5m": "000905_5m.parquet",   "file_1d": "000905_1d.parquet"},
    "588000ETF": {"file_5m": "000688_5m.parquet",   "file_1d": "000688_1d.parquet"},
    "159915ETF": {"file_5m": "399006_5m.parquet",   "file_1d": "399006_1d.parquet"},
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

# ── Per-ETF decision/exit bars (single source of truth) ──────────────
# Decision bar = the 5m bar whose CLOSE triggers the signal.
# Bars are 0-indexed, END-timestamped (bar 0 closes at 9:35, bar 5 closes at 10:00).
# Entry happens at OPEN of bar (decision_bar + 1).
# EXIT_BAR = 42 closes at 14:35.
#
# Picked by first-principles plan: 10:00 entry, 14:35 exit.
EXIT_BAR = 42
DECISION_BAR = {
    "300ETF":    5,   # 10:00 (bar 5 closes at 10:00, entry at 10:00 open of bar 6)
    "50ETF":     5,
    "500ETF":    5,
    "588000ETF": 5,
    "159915ETF": 5,
}


# ============================================================
# Day-level indicators (computed on full history, then shifted by 1)
# ============================================================
def compute_daylevel_indicators(df_1d: pd.DataFrame) -> pd.DataFrame:
    """Compute technical indicators on daily close_adj, shift by 1 to avoid look-ahead."""
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

    # 3) Prepare date column
    order_book_id = df["order_book_id"].iloc[0]
    df["date"] = pd.to_datetime(df["date"])

    # 4) Option Derived Features
    order_book_id = df["order_book_id"].iloc[0]
    etf_key = {
        "510050.XSHG": "50",
        "510300.XSHG": "300",
        "510500.XSHG": "500",
        "588000.XSHG": "588000",
        "159915.XSHE": "159915",
        "000016.XSHG": "50",
        "000300.XSHG": "300",
        "000905.XSHG": "500",
        "000688.XSHG": "588000",
        "399006.XSHE": "159915"
    }.get(order_book_id, "300")

    # Load calculated ATM 30d IV cache
    iv_path = DATA_DIR / f"30d_iv_cache_{etf_key}.parquet"
    if iv_path.exists():
        iv_df = pd.read_parquet(iv_path)
        iv_df.columns = ["iv"]
        iv_df.index = pd.to_datetime(iv_df.index)
        df = df.merge(iv_df, left_on="date", right_index=True, how="left")
    else:
        df["iv"] = np.nan

    # Load Ricequant VIX cache
    vix_path = DATA_DIR / "rq_vix.parquet"
    vix_col = f"vix_{etf_key}"
    if vix_path.exists():
        vix_df = pd.read_parquet(vix_path)
        vix_df.index = pd.to_datetime(vix_df.index)
        if vix_col in vix_df.columns:
            df = df.merge(vix_df[[vix_col]].rename(columns={vix_col: "vix"}), left_on="date", right_index=True, how="left")
        else:
            df["vix"] = np.nan
    else:
        df["vix"] = np.nan

    # Keep VIX as NaN before launch date (no synthetic backfill)

    # Compute factors
    df["iv_vol_ratio"] = df["iv"] / (df["vol20"] + 1e-8)
    df["vix_vol_ratio"] = df["vix"] / (df["vol20"] + 1e-8)
    df["vix_iv_spread"] = df["vix"] - df["iv"]
    df["vix_iv_ratio"] = df["vix"] / (df["iv"] + 1e-8)
    df["iv_diff_1d"] = df["iv"].diff(1)
    df["vix_diff_1d"] = df["vix"].diff(1)

    # ── GARCH volatility and regime features ──
    try:
        from garch_regime import generate_garch_regimes
        garch_df = generate_garch_regimes(f"{etf_key}ETF", force=False)
        garch_df = garch_df[["date", "vol_daily", "vol_2h", "vol_1h", "state"]].copy()
        garch_df["date"] = pd.to_datetime(garch_df["date"])
        garch_df = garch_df.rename(columns={
            "vol_daily": "garch_vol_daily",
            "vol_2h": "garch_vol_2h",
            "vol_1h": "garch_vol_1h",
            "state": "garch_state"
        })
        # Calculate differences (vol-of-vol)
        garch_df = garch_df.sort_values("date").reset_index(drop=True)
        garch_df["garch_vol_daily_diff"] = garch_df["garch_vol_daily"].diff(1)
        garch_df["garch_vol_2h_diff"] = garch_df["garch_vol_2h"].diff(1)
        garch_df["garch_vol_1h_diff"] = garch_df["garch_vol_1h"].diff(1)
        
        df = df.merge(garch_df, on="date", how="left")
    except Exception as e:
        print(f"    [WARN] Failed to load GARCH features for {etf_key}ETF: {e}")
        df["garch_vol_daily"] = np.nan
        df["garch_vol_2h"] = np.nan
        df["garch_vol_1h"] = np.nan
        df["garch_state"] = np.nan
        df["garch_vol_daily_diff"] = np.nan
        df["garch_vol_2h_diff"] = np.nan
        df["garch_vol_1h_diff"] = np.nan

    # ── Mined daily option-derived features ──
    opt_prices_file = f"{etf_key}ETF_historical_prices.parquet" if etf_key != "50" else "50ETF_historical_prices.parquet"
    opt_inst_file = f"{etf_key}ETF_instruments.parquet" if etf_key != "50" else "50ETF_instruments.parquet"
    etf_1d_file = {"50": "50ETF_1d.parquet", "300": "510300_1d.parquet", "500": "500ETF_1d.parquet", "588000": "588000ETF_1d.parquet", "159915": "159915ETF_1d.parquet"}[etf_key]
    
    try:
        opt_prices = pd.read_parquet(DATA_DIR / opt_prices_file)
        opt_inst = pd.read_parquet(DATA_DIR / opt_inst_file)
        df_etf_1d = pd.read_parquet(DATA_DIR / etf_1d_file)
        
        opt_merged = opt_prices.merge(
            opt_inst[["order_book_id", "option_type", "maturity_date"]],
            on="order_book_id",
            how="inner"
        )
        opt_merged["date"] = pd.to_datetime(opt_merged["date"])
        opt_merged["maturity_date"] = pd.to_datetime(opt_merged["maturity_date"])
        opt_merged["days_to_maturity"] = (opt_merged["maturity_date"] - opt_merged["date"]).dt.days
        
        und_close = df_etf_1d.set_index(pd.to_datetime(df_etf_1d["date"]))["close"]
        opt_merged["s0"] = opt_merged["date"].map(und_close)
        opt_merged["strike_dist"] = (opt_merged["strike_price"] - opt_merged["s0"]).abs()
        
        # 1. Option volume pc ratio & OI growth (vectorized)
        vol_by_type = opt_merged.groupby(["date", "option_type"])["volume"].sum().unstack()
        pc_ratio_series = vol_by_type["P"] / (vol_by_type["C"] + 1e-8)
        
        total_oi_series = opt_merged.groupby("date")["open_interest"].sum()
        oi_growth_series = total_oi_series.pct_change()
        
        # 2. Term structure & corridor width
        term_struct = {}
        corr_width = {}
        
        for date, day_df in opt_merged.groupby("date"):
            s0 = day_df["s0"].iloc[0]
            if pd.isna(s0) or s0 <= 0:
                continue
                
            valid_df = day_df[(day_df["days_to_maturity"] >= 10) & (day_df["days_to_maturity"] <= 120)]
            mats = sorted(valid_df["maturity_date"].unique())
            if len(mats) < 2:
                continue
            
            T1_dt, T2_dt = mats[0], mats[1]
            T1_days = (T1_dt - date).days
            T2_days = (T2_dt - date).days
            T1 = max(T1_days, 2) / 365.0
            T2 = max(T2_days, 2) / 365.0
            
            near_df = valid_df[valid_df["maturity_date"] == T1_dt]
            idx_atm = near_df["strike_dist"].idxmin()
            atm_strike = near_df.loc[idx_atm, "strike_price"]
            
            near_atm = near_df[near_df["strike_price"] == atm_strike]
            c1_row = near_atm[near_atm["option_type"] == "C"]
            p1_row = near_atm[near_atm["option_type"] == "P"]
            if c1_row.empty or p1_row.empty:
                continue
            c1 = c1_row["close"].iloc[0]
            p1 = p1_row["close"].iloc[0]
            
            next_df = valid_df[valid_df["maturity_date"] == T2_dt]
            idx_atm_next = next_df["strike_dist"].idxmin()
            atm_strike_next = next_df.loc[idx_atm_next, "strike_price"]
            
            next_atm = next_df[next_df["strike_price"] == atm_strike_next]
            c2_row = next_atm[next_atm["option_type"] == "C"]
            p2_row = next_atm[next_atm["option_type"] == "P"]
            if c2_row.empty or p2_row.empty:
                continue
            c2 = c2_row["close"].iloc[0]
            p2 = p2_row["close"].iloc[0]
            
            straddle_1 = c1 + p1
            straddle_2 = c2 + p2
            iv1 = straddle_1 / (s0 * math.sqrt(T1) + 1e-8)
            iv2 = straddle_2 / (s0 * math.sqrt(T2) + 1e-8)
            
            term_struct[date] = iv1 / (iv2 + 1e-8)
            
            strike_target_up = 1.05 * s0
            strike_target_dn = 0.95 * s0
            
            near_calls = near_df[near_df["option_type"] == "C"]
            near_puts = near_df[near_df["option_type"] == "P"]
            if near_calls.empty or near_puts.empty:
                continue
                
            idx_up = (near_calls["strike_price"] - strike_target_up).abs().idxmin()
            strike_up = near_calls.loc[idx_up, "strike_price"]
            c_up = near_calls.loc[idx_up, "close"]
            
            idx_dn = (near_puts["strike_price"] - strike_target_dn).abs().idxmin()
            strike_dn = near_puts.loc[idx_dn, "strike_price"]
            p_dn = near_puts.loc[idx_dn, "close"]
            
            r_rate = 0.02
            iv_up = black_iv(c_up, s0, strike_up, T1, r_rate, True)
            iv_dn = black_iv(p_dn, s0, strike_dn, T1, r_rate, False)
            iv_atm = (iv1 + iv2) / 2.0
            
            corr_width[date] = (iv_up - iv_dn) / (iv_atm + 1e-8)
            
        df["date_dt"] = pd.to_datetime(df["date"])
        df["option_volume_pc_ratio"] = df["date_dt"].map(pc_ratio_series)
        df["option_oi_growth"] = df["date_dt"].map(oi_growth_series)
        df["iv_term_structure"] = df["date_dt"].map(term_struct)
        df["iv_corridor_width"] = df["date_dt"].map(corr_width)
        
    except Exception as e:
        print(f"    [WARN] Failed to compute option features: {e}")
        df["option_volume_pc_ratio"] = np.nan
        df["option_oi_growth"] = np.nan
        df["iv_term_structure"] = np.nan
        df["iv_corridor_width"] = np.nan

    # ── Mined daily technical/regime indicators ──
    df["date_dt"] = pd.to_datetime(df["date"])
    df["vix_skew_proxy"] = (df["vix"] - df["vix"].shift(1)) / (df["vix"].shift(1) + 1e-8)
    df["vix_rolling_percentile_60d"] = df["vix"].rolling(60, min_periods=20).apply(
        lambda x: pd.Series(x).dropna().rank(pct=True).iloc[-1] if (len(pd.Series(x).dropna()) >= 20 and not np.isnan(x[-1])) else np.nan, raw=True
    )
    df["vix_realized_spread"] = df["vix"] - df["vol20"]
    df["iv_acceleration_1d"] = df["iv"].diff(1).diff(1)
    
    iv_sma20 = df["iv"].rolling(20).mean()
    df["iv_envelope_deviation"] = (df["iv"] - iv_sma20) / (iv_sma20 + 1e-8)
    
    df["yesterday_vix_early_drift"] = df["vix_diff_1d"]
    
    # TD Sequential Setup Count
    consec_buy = (df["close_adj"] < df["close_adj"].shift(4)).astype(int)
    consec_sell = (df["close_adj"] > df["close_adj"].shift(4)).astype(int)
    buy_count = np.zeros(len(df))
    sell_count = np.zeros(len(df))
    b_run = 0
    s_run = 0
    for i in range(len(df)):
        if consec_buy.iloc[i]:
            b_run = min(b_run + 1, 9)
            s_run = 0
        elif consec_sell.iloc[i]:
            s_run = min(s_run + 1, 9)
            b_run = 0
        else:
            b_run = 0
            s_run = 0
        buy_count[i] = b_run
        sell_count[i] = s_run
    df["demark_setup_count_day"] = sell_count - buy_count
    
    # Inside/Outside Bars
    inside_bar = (df["high_adj"] <= df["high_adj"].shift(1)) & (df["low_adj"] >= df["low_adj"].shift(1))
    inside_count = np.zeros(len(df))
    run = 0
    for i in range(len(df)):
        if inside_bar.iloc[i]:
            run += 1
        else:
            run = 0
        inside_count[i] = run
    df["consecutive_inside_bars_3d"] = inside_count
    df["outside_bar_reversal_day"] = ((df["high_adj"] > df["high_adj"].shift(1)) & (df["low_adj"] < df["low_adj"].shift(1))).astype(float)
    
    # WaveTrend Day
    ap = (df["high_adj"] + df["low_adj"] + df["close_adj"]) / 3.0
    esa = ap.ewm(span=10, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=10, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d + 1e-8)
    wt1 = ci.ewm(span=21, adjust=False).mean()
    df["wavetrend_osc_day"] = wt1 / 100.0
    wt2 = df["wavetrend_osc_day"].rolling(4).mean()
    df["wavetrend_cross_day"] = df["wavetrend_osc_day"] - wt2
    
    # Keltner Squeeze Width
    kc_mid = df["close_adj"].ewm(span=20, adjust=False).mean()
    kc_tr = pd.concat([(df["high_adj"] - df["low_adj"]).abs(),
                       (df["high_adj"] - df["close_adj"].shift(1)).abs(),
                       (df["low_adj"] - df["close_adj"].shift(1)).abs()], axis=1).max(axis=1)
    kc_atr = kc_tr.rolling(20).mean()
    keltner_width = (3.0 * kc_atr) / (kc_mid + 1e-8)
    df["keltner_squeeze_width"] = df["bb_width"] / (keltner_width + 1e-8)
    
    # Stochastic RSI
    rsi = df["rsi14"]
    rsi_min = rsi.rolling(14).min()
    rsi_max = rsi.rolling(14).max()
    stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min + 1e-8)
    df["stoch_rsi_divergence"] = df["close_adj"] / (df["close_adj"].rolling(14).mean() + 1e-8) - stoch_rsi
    
    # Cross-ETF sentiment rotations
    try:
        df_300 = pd.read_parquet(DATA_DIR / "000300_1d.parquet")
        df_159915 = pd.read_parquet(DATA_DIR / "399006_1d.parquet")
        df_588000 = pd.read_parquet(DATA_DIR / "000688_1d.parquet")
        
        df_300["date"] = pd.to_datetime(df_300["date"])
        df_159915["date"] = pd.to_datetime(df_159915["date"])
        df_588000["date"] = pd.to_datetime(df_588000["date"])
        
        c300_s = df_300.set_index("date")["close"]
        c159915_s = df_159915.set_index("date")["close"]
        
        c300_aligned = df["date_dt"].map(c300_s)
        c159915_aligned = df["date_dt"].map(c159915_s)
        df["tech_value_rotation"] = c159915_aligned / (c300_aligned + 1e-8)
        
        roc_300 = ta.roc(df_300["close"], length=10) / 100.0
        roc_588000 = ta.roc(df_588000["close"], length=10) / 100.0
        roc_300_s = pd.Series(roc_300.values, index=df_300["date"])
        roc_588000_s = pd.Series(roc_588000.values, index=df_588000["date"])
        
        df["growth_momentum_ratio"] = df["date_dt"].map(roc_588000_s) - df["date_dt"].map(roc_300_s)
        
        lr_300 = np.log(df_300["close"] / df_300["close"].shift(1))
        lr_588000 = np.log(df_588000["close"] / df_588000["close"].shift(1))
        v300_s = pd.Series((lr_300.rolling(20).std() * np.sqrt(252)).values, index=df_300["date"])
        v588000_s = pd.Series((lr_588000.rolling(20).std() * np.sqrt(252)).values, index=df_588000["date"])
        
        df["high_beta_vol_ratio"] = df["date_dt"].map(v588000_s) / (df["date_dt"].map(v300_s) + 1e-8)
    except Exception as e:
        print(f"    [WARN] Failed cross-ETF rotation: {e}")
        df["tech_value_rotation"] = np.nan
        df["growth_momentum_ratio"] = np.nan
        df["high_beta_vol_ratio"] = np.nan
        
    df["retail_turnover_acceleration"] = df["volume"] / (df["volume"].rolling(20).mean() + 1e-8)
    
    # Yesterday limits
    limit_up_mult = 1.20 if etf_key in ["588000", "159915"] else 1.10
    limit_down_mult = 0.80 if etf_key in ["588000", "159915"] else 0.90
    prev_close_adj = df["close_adj"].shift(1)
    
    df["yesterday_limit_up_touch"] = (df["high_adj"] >= prev_close_adj * limit_up_mult - 1e-5).astype(float)
    df["yesterday_limit_down_touch"] = (df["low_adj"] <= prev_close_adj * limit_down_mult + 1e-5).astype(float)
    df["limit_up_proximity_day"] = (df["close_adj"] - prev_close_adj * limit_up_mult) / (prev_close_adj * limit_up_mult + 1e-8)
    df["limit_down_proximity_day"] = (df["close_adj"] - prev_close_adj * limit_down_mult) / (prev_close_adj * limit_down_mult + 1e-8)
    
    df["yesterday_wavetrend_osc"] = df["wavetrend_osc_day"]
    
    # Stochastic RSI cross
    stoch_k = df["stoch_k"]
    stoch_d = df["stoch_d"]
    df["yesterday_stoch_rsi_cross"] = stoch_k - stoch_d
    
    # CVD divergence
    daily_cvd = (df["close_adj"] - df["open_adj"]) * df["volume"]
    df["cvd_divergence_day"] = df["close_adj"] / (df["close_adj"].shift(4) + 1e-8) - daily_cvd / (daily_cvd.shift(4) + 1e-8)
    
    # Amihud yesterday illiquidity
    yesterday_return_inline = (df["close_adj"] - df["close_adj"].shift(1)) / (df["close_adj"].shift(1) + 1e-8)
    df["yesterday_illiquidity_amihud"] = yesterday_return_inline.abs() / (df["volume"] + 1e-8)
    
    # Turtle channel
    high20 = df["high_adj"].rolling(20).max()
    low20 = df["low_adj"].rolling(20).min()
    df["turtle_channel_proximity_day"] = (df["close_adj"] - (high20 + low20) / 2.0) / (high20 - low20 + 1e-8)
    
    # Chande
    diff = df["close_adj"].diff(1)
    su = diff.clip(lower=0).rolling(14).sum()
    sd = (-diff).clip(lower=0).rolling(14).sum()
    df["chande_momentum_osc_day"] = (su - sd) / (su + sd + 1e-8)
    
    # Coppock
    roc14 = ta.roc(df["close_adj"], length=14)
    roc11 = ta.roc(df["close_adj"], length=11)
    cc = (roc14 + roc11) if roc14 is not None and roc11 is not None else np.nan
    df["coppock_curve_day"] = ta.wma(cc, length=10) / 100.0 if cc is not None else np.nan
    
    # Elder ray
    ema13 = df["close_adj"].ewm(span=13, adjust=False).mean()
    bull_power = df["high_adj"] - ema13
    bear_power = df["low_adj"] - ema13
    df["elder_ray_power_spread"] = (bull_power - bear_power) / (atr14 + 1e-8)

    # ── New 14 day-level features from features_extra.py ──
    # Computed on full daily Index history ending at T-1 (shifted by 1 below).
    try:
        day_extras = compute_daylevel_extras(df)
        for col in day_extras.columns:
            df[col] = day_extras[col].values
    except Exception as e:
        print(f"    [WARN] compute_daylevel_extras failed: {e}")
        for col in DAY_EXTRA:
            df[col] = np.nan

    # Check and fill missing columns/NaNs robustly (exempt VIX features under Option A)
    for col in DAY_FEATURES:
        if col not in df.columns:
            df[col] = np.nan
        if "vix" in col.lower():
            continue  # Option A: Preserve authentic NaNs for pre-launch VIX dates
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
def extract_day_early_features(day_5m: pd.DataFrame, prev_close: float, expected_bar_vol: float,
                               decision_bar: int = EARLY_BARS - 1,
                               is_20pct: bool = False, atr14_prev: float = 0.0,
                               bb_width_prev_price: float = 0.0, buy_break: float = 0.0,
                               sell_break: float = 0.0, sell_setup: float = 0.0,
                               buy_setup: float = 0.0, high20: float = 0.0,
                               low20: float = 0.0, atr20: float = 0.0) -> dict:
    """Extract early features strictly causally — only bars [0..decision_bar] are consumed.

    Parameters
    ----------
    decision_bar : int
        Index of the 5m bar whose CLOSE triggers the decision. Features use bars
        ``[0..decision_bar]`` inclusive; entry happens at OPEN of bar
        ``decision_bar + 1`` (handled by ``compute_trade_return``).

    Bar-by-bar features ``bar_*_{decision_bar+1..5}`` are padded with 0.0 so the
    feature schema stays uniform across ETFs (StandardScaler handles constant
    columns by setting scale=1; stability selection prunes them automatically).
    Summary features (``first_30min_return`` etc.) are computed only from the
    available bars, so for ETFs with ``decision_bar < 5`` they effectively
    become "return up to decision time" rather than "first 30 minutes".
    """
    n_use = decision_bar + 1
    bars = day_5m.head(n_use)
    if len(bars) < n_use or prev_close <= 0 or prev_close is None or np.isnan(prev_close):
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

    # VWAP of available bars
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

    # Bar-by-bar features for all 6 slots; pad indices > decision_bar with 0.0
    # (causality: those bars are in the future at decision time)
    for i in range(EARLY_BARS):
        if i <= decision_bar:
            res[f"bar_ret_{i}"] = float(np.log(cl[i] / max(op[i], 1e-10)))
            res[f"bar_vol_{i}"] = float(vol[i] / expected_bar_vol)
            res[f"bar_rng_{i}"] = float((hi[i] - lo[i]) / max(op[i], 1e-10))
            res[f"bar_body_rng_{i}"] = float((cl[i] - op[i]) / (hi[i] - lo[i] + 1e-8))
            cum_vol = max(vol[:i+1].sum(), 1.0)
            cum_vwap = (cl[:i+1] * vol[:i+1]).sum() / cum_vol
            res[f"bar_vwap_dev_{i}"] = float((cl[i] - cum_vwap) / max(cum_vwap, 1e-10))
        else:
            # Future bar from decision's perspective — pad with 0.0 (constant).
            # Stability selection / L1 will drop these; StandardScaler sets
            # scale=1 for std=0 columns, producing transformed value 0.0.
            res[f"bar_ret_{i}"] = 0.0
            res[f"bar_vol_{i}"] = 0.0
            res[f"bar_rng_{i}"] = 0.0
            res[f"bar_body_rng_{i}"] = 0.0
            res[f"bar_vwap_dev_{i}"] = 0.0

    res["num_up_bars"] = float((cl > op).sum())
    res["max_up_ret"] = float((hi.max() - op[0]) / max(op[0], 1e-10))
    res["max_down_ret"] = float((lo.min() - op[0]) / max(op[0], 1e-10))
    res["cl_pos_in_range"] = float((cl[-1] - lo.min()) / (hi.max() - lo.min() + 1e-8))
    res["body_to_range_ratio"] = float(abs(cl[-1] - op[0]) / (hi.max() - lo.min() + 1e-8))
    res["total_path_length"] = float(np.sum(np.abs(bar_ret)))
    res["volume_slope"] = float(_linear_slope(vol) / expected_bar_vol)

    # ── New 121 early-bar features from features_extra.py (numba njit, fp32) ──
    # Reuses already-sliced op/hi/lo/cl/vol (float64); extract_early_extras
    # casts to float32 and dispatches to the compiled helper.
    try:
        res.update(extract_early_extras(
            bars, prev_close, expected_bar_vol, decision_bar,
            is_20pct=is_20pct, atr14_prev=atr14_prev,
            bb_width_prev_price=bb_width_prev_price, buy_break=buy_break,
            sell_break=sell_break, sell_setup=sell_setup,
            buy_setup=buy_setup, high20=high20,
            low20=low20, atr20=atr20
        ))
    except Exception:
        # On any failure, fill NaN so the schema stays uniform
        res.update(empty_early_extras())

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
            "day_skew": np.nan, "day_kurtosis": np.nan,
            "afternoon_reversal": np.nan, "lunch_gap": np.nan, "pm_am_vol_ratio": np.nan,
            "pm_momentum": np.nan, "midday_liquidity_fade": np.nan, "midday_drawdown": np.nan,
            "cvd_close": np.nan,
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
    
    afternoon_reversal = np.nan
    lunch_gap = np.nan
    pm_momentum = np.nan
    midday_liquidity_fade = np.nan
    if len(closes) >= 48:
        morn_ret = (closes[23] - opens[0]) / (opens[0] + 1e-8)
        aft_ret = (closes[47] - opens[24]) / (opens[24] + 1e-8)
        afternoon_reversal = aft_ret - morn_ret
        
        lunch_gap = (opens[24] - closes[23]) / (closes[23] + 1e-8)
        pm_momentum = float(np.log(closes[42] / opens[24]))
        midday_liquidity_fade = (float(vols[22]) + float(vols[25])) / (float(np.mean(vols)) + 1e-8)

    midday_drawdown = (float(np.min(lows)) - float(opens[0])) / (float(opens[0]) + 1e-8)
    
    cvd_close = 0.0
    for i in range(len(closes)):
        cvd_close += float(np.sign(closes[i] - opens[i]) * vols[i])

    return {
        "day_range": day_range,
        "day_realized_vol": day_realized_vol,
        "day_close_pos": day_close_pos,
        "day_pm_am_vol_ratio": day_pm_am_vol_ratio,
        "day_late_mom": day_late_mom,
        "day_vwap_dev": day_vwap_dev,
        "day_skew": day_skew,
        "day_kurtosis": day_kurtosis,
        "afternoon_reversal": afternoon_reversal,
        "lunch_gap": lunch_gap,
        "pm_am_vol_ratio": day_pm_am_vol_ratio,
        "pm_momentum": pm_momentum,
        "midday_liquidity_fade": midday_liquidity_fade,
        "midday_drawdown": midday_drawdown,
        "cvd_close": cvd_close,
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
# Trade return target (entry-to-exit)
# ============================================================
def compute_trade_return(day_5m: pd.DataFrame, decision_bar: int, exit_bar: int = EXIT_BAR) -> float:
    """Entry-to-exit log return = log(close[exit_bar] / open[decision_bar + 1]).

    Mirrors actual trade execution in daytrade/backtest.py:
        decision at close of bar (decision_bar)
        entry    at open  of bar (decision_bar + 1)   <- next bar open after decision
        exit     at close of bar (exit_bar)

    The model now trains on exactly what the trade captures — no window mismatch.
    """
    bars = day_5m.reset_index(drop=True)
    entry_idx = decision_bar + 1
    if len(bars) <= exit_bar or entry_idx >= len(bars):
        return np.nan
    entry_open = float(bars.iloc[entry_idx]["open"])
    exit_close = float(bars.iloc[exit_bar]["close"])
    if entry_open <= 0 or exit_close <= 0:
        return np.nan
    return float(np.log(exit_close / entry_open))


# ============================================================
# Pipeline per ETF
# ============================================================
def build_features_for_etf(etf_name: str, save: bool = True, early: bool = False) -> pd.DataFrame:
    cfg = ETF_CONFIG[etf_name]
    idx_cfg = INDEX_CONFIG[etf_name]
    
    path_etf_5m = DATA_DIR / cfg["file_5m"]
    path_idx_5m = DATA_DIR / idx_cfg["file_5m"]
    path_idx_1d = DATA_DIR / idx_cfg["file_1d"]

    if not (path_etf_5m.exists() and path_idx_5m.exists() and path_idx_1d.exists()):
        print(f"  [SKIP] {etf_name}: missing parquet ({path_etf_5m.name} / {path_idx_5m.name} / {path_idx_1d.name})")
        return pd.DataFrame()

    print(f"\n[{etf_name}] loading Index 5m + 1d (for features) and ETF 5m (for trades) ...")
    df_idx_5m = pd.read_parquet(path_idx_5m)
    df_idx_1d = pd.read_parquet(path_idx_1d)
    df_etf_5m = pd.read_parquet(path_etf_5m)

    df_idx_5m["datetime"] = pd.to_datetime(df_idx_5m["datetime"])
    df_idx_5m["date"] = df_idx_5m["datetime"].dt.normalize()
    df_idx_5m = df_idx_5m.sort_values(["date", "datetime"]).reset_index(drop=True)

    df_etf_5m["datetime"] = pd.to_datetime(df_etf_5m["datetime"])
    df_etf_5m["date"] = df_etf_5m["datetime"].dt.normalize()
    df_etf_5m = df_etf_5m.sort_values(["date", "datetime"]).reset_index(drop=True)

    # Add adjusted columns to daily Index data for compatibility with compute_daylevel_indicators
    for col in ["open", "high", "low", "close"]:
        if f"{col}_adj" not in df_idx_1d.columns:
            df_idx_1d[f"{col}_adj"] = df_idx_1d[col]

    # ── Day-level indicators (shifted to prior day) ──
    daylevel = compute_daylevel_indicators(df_idx_1d)
    daylevel["date"] = pd.to_datetime(daylevel["date"])
    daylevel = daylevel.set_index("date").sort_index()
    daylevel_dict = daylevel.to_dict(orient="index")

    # ── Per-day early features + PM return ──
    df_idx_1d_sorted = df_idx_1d.sort_values("date").reset_index(drop=True).copy()
    df_idx_1d_sorted["prev_close_adj"] = df_idx_1d_sorted["close_adj"].shift(1)
    df_idx_1d_sorted["rolling_volume_20d"] = df_idx_1d_sorted["volume"].rolling(20).mean()
    df_idx_1d_sorted["expected_daily_volume"] = df_idx_1d_sorted["rolling_volume_20d"].shift(1)
    df_idx_1d_sorted["date"] = pd.to_datetime(df_idx_1d_sorted["date"])
    prev_close_map = df_idx_1d_sorted.set_index("date")["prev_close_adj"].to_dict()
    expected_vol_map = df_idx_1d_sorted.set_index("date")["expected_daily_volume"].to_dict()

    fallback_daily_vol = df_idx_1d_sorted["volume"].median()
    if pd.isna(fallback_daily_vol) or fallback_daily_vol <= 0:
        fallback_daily_vol = 1000000.0

    exit_bar = 24 if early else EXIT_BAR
    decision_bar = DECISION_BAR[etf_name]
    print(f"  decision_bar={decision_bar} (features use bars [0..{decision_bar}], "
          f"entry at open of bar {decision_bar + 1}, exit at close of bar {exit_bar})")

    etf_5m_by_date = {d: g for d, g in df_etf_5m.groupby("date")}

    rows = []
    for date, day_idx_df in df_idx_5m.groupby("date", sort=True):
        date_ts = pd.Timestamp(date)
        if date not in etf_5m_by_date:
            day_etf_df = day_idx_df
        else:
            day_etf_df = etf_5m_by_date[date]
        
        prev_close = prev_close_map.get(date_ts, np.nan)
        
        expected_daily_vol = expected_vol_map.get(date_ts, np.nan)
        if pd.isna(expected_daily_vol) or expected_daily_vol <= 0:
            expected_daily_vol = fallback_daily_vol
        expected_bar_vol = expected_daily_vol / 48.0
        
        # Get indicators from T-1 daily indicators
        ctx = daylevel_dict.get(date_ts, {})
        is_20pct = etf_name in ["588000ETF", "159915ETF"]
        
        atr14_prev = ctx.get("atr14", 0.0)
        if pd.isna(atr14_prev) or atr14_prev <= 0.0:
            atr14_prev = prev_close * 0.02 if not pd.isna(prev_close) else 0.02
            
        bb_width_val = ctx.get("bb_width", 0.0)
        bb_width_prev_price = bb_width_val * prev_close if not pd.isna(prev_close) else 0.0
        
        buy_break = ctx.get("buy_break", 0.0)
        sell_break = ctx.get("sell_break", 0.0)
        sell_setup = ctx.get("sell_setup", 0.0)
        buy_setup = ctx.get("buy_setup", 0.0)
        
        high20 = ctx.get("high20", 0.0)
        low20 = ctx.get("low20", 0.0)
        atr20 = ctx.get("atr20", 0.0)
        
        # Calculate early features on Index 5m data
        early_dict = extract_day_early_features(
            day_idx_df, prev_close, expected_bar_vol, decision_bar=decision_bar,
            is_20pct=is_20pct, atr14_prev=atr14_prev,
            bb_width_prev_price=bb_width_prev_price, buy_break=buy_break,
            sell_break=sell_break, sell_setup=sell_setup,
            buy_setup=buy_setup, high20=high20,
            low20=low20, atr20=atr20
        )
        early_dict["date"] = date_ts
        
        # Target/diagnostics calculated on ETF 5m data
        early_dict["pm_return"] = compute_pm_return(day_etf_df)                              # diagnostic only
        early_dict["trade_return"] = compute_trade_return(day_etf_df, decision_bar, exit_bar)  # target
        
        # AM return of ETF (diagnostic)
        am_etf = day_etf_df.reset_index(drop=True).iloc[:BAR_LUNCH]
        if len(am_etf) >= 2:
            early_dict["am_return"] = float(np.log(np.maximum(am_etf["close"].iloc[-1], 1e-10) /
                                              np.maximum(am_etf["open"].iloc[0], 1e-10)))
        else:
            early_dict["am_return"] = np.nan
            
        # Compute day full features (to be shifted later) on Index 5m data
        full_feats = extract_day_full_features(day_idx_df)
        for k, v in full_feats.items():
            early_dict[k] = v
            
        rows.append(early_dict)

    early_df = pd.DataFrame(rows).set_index("date").sort_index()

    # Shift yesterday features by 1 day
    cols_to_shift = [
        "pm_return", "am_return", "trade_return",
        "gap_pct", "first_30min_return", "early_realized_vol", "early_range",
        "early_volume_ratio", "early_trend", "early_momentum", "first_bar_return",
        "first_bar_volume", "early_vwap_dev", "early_skew", "early_kurtosis",
        "day_range", "day_realized_vol", "day_close_pos", "day_pm_am_vol_ratio",
        "day_late_mom", "day_vwap_dev", "day_skew", "day_kurtosis",
        # Bases for YESTERDAY_EXTRA (yesterday_intraday_close_position,
        # yesterday_opening_gap_reversal, yesterday_spike_exhaustion_ratio)
        "intraday_close_position", "opening_gap_reversal", "spike_exhaustion_ratio",
        # New full day features
        "afternoon_reversal", "lunch_gap", "pm_am_vol_ratio",
        "midday_liquidity_fade", "midday_drawdown", "cvd_close",
    ]
    cols_to_shift = [col for col in cols_to_shift if col in early_df.columns]
    for col in cols_to_shift:
        early_df[f"yesterday_{col}"] = early_df[col].shift(1)
        
    # Custom yesterday shift for afternoon momentum
    if "pm_momentum" in early_df.columns:
        early_df["yesterday_afternoon_momentum"] = early_df["pm_momentum"].shift(1)

    # ── Merge with day-level indicators ──
    feat = early_df.join(daylevel, how="inner")

    # ── Drop warmup rows ──
    feat = feat.iloc[WARMUP_DAYS:].copy()

    # ── Drop any rows with NaN target (trade_return is the model target; pm_return kept for diagnostics) ──
    n_before = len(feat)
    feat = feat.dropna(subset=["trade_return"]).copy()
    n_after = len(feat)
    
    # Subset to keep only declared features + target + diagnostics
    all_out_cols = [c for c in FEATURES + ["trade_return", "pm_return"] if c in feat.columns]
    feat = feat[all_out_cols].copy()

    print(f"  samples: {n_after} (dropped {n_before - n_after} NaN-target), "
          f"features: {len(all_out_cols) - 2}")
    print(f"  target trade_return: mean={feat['trade_return'].mean()*100:.4f}%  "
          f"std={feat['trade_return'].std()*100:.4f}%  "
          f"Sharpe={feat['trade_return'].mean()/feat['trade_return'].std()*np.sqrt(252):.2f}")
    print(f"  diagnostic pm_return: mean={feat['pm_return'].mean()*100:.4f}%  "
          f"std={feat['pm_return'].std()*100:.4f}%  "
          f"Sharpe={feat['pm_return'].mean()/feat['pm_return'].std()*np.sqrt(252):.2f}")

    if save:
        fname = f"features_{etf_name}_early.parquet" if early else f"features_{etf_name}.parquet"
        out_path = OUT_DIR / fname
        feat.to_parquet(out_path)
        print(f"  saved → {out_path}")

    return feat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-e", "--etf", default="all",
                    help="ETF code: 300/50/500/588000/159915 or 'all'")
    ap.add_argument("--include-deprecated", action="store_true",
                    help="Include deprecated features for backward compatibility")
    ap.add_argument("--early", action="store_true",
                    help="Predict early window (exiting at close of 13:00~13:05 bar, i.e., bar 24)")
    args = ap.parse_args()

    etf_arg = args.etf
    if etf_arg in ETF_CLI_MAP and isinstance(ETF_CLI_MAP[etf_arg], list):
        etfs = ETF_CLI_MAP[etf_arg]
    else:
        etfs = [ETF_CLI_MAP.get(etf_arg, etf_arg)]

    exit_bar = 24 if args.early else EXIT_BAR
    print(f"Building day-model features for: {etfs}")
    print(f"  early window: per-ETF decision_bar (see DECISION_BAR dict in build_features.py)")
    print(f"  exit bar: {exit_bar} ({'13:05' if args.early else '14:35'} close)")
    print(f"  warmup dropped: {WARMUP_DAYS} days")

    summary = []
    for etf in etfs:
        feat = build_features_for_etf(etf, early=args.early)
        if not feat.empty:
            summary.append({
                "ETF": etf,
                "decision_bar": DECISION_BAR[etf],
                "n_days": len(feat),
                "date_start": feat.index.min().strftime("%Y-%m-%d"),
                "date_end": feat.index.max().strftime("%Y-%m-%d"),
                "trade_mean_pct": feat["trade_return"].mean() * 100,
                "trade_std_pct": feat["trade_return"].std() * 100,
                "trade_sharpe_ann": feat["trade_return"].mean() / feat["trade_return"].std() * np.sqrt(252),
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
