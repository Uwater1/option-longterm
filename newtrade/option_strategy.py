#!/usr/bin/env python3
"""
Option Portfolio Simulation for NewTrade framework (optimized).
Simulates a capital-constrained option portfolio:
- 100k RMB initial capital per ETF
- Each signal deploys 10% of current portfolio capital into nearest OTM option (call=long, put=short)
- Nearest expiry with >= 7 days to maturity
- Fractional contracts allowed
- 4 RMB commission per contract per side (buy + sell)
- Bankrupt (capital <= 0) -> report all zeros afterward

Performance: pre-grouped dict lookups, numpy arrays, no per-trade DataFrame filtering.
"""

import math
from functools import lru_cache
from pathlib import Path
import numpy as np
import pandas as pd

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DATA_DIR = REPO_ROOT / "data"

# ETF 5m file mapping (same as day-model)
ETF_5M_FILE = {
    "50ETF": "50ETF_5m.parquet",
    "300ETF": "510300_5m.parquet",
    "500ETF": "500ETF_5m.parquet",
    "588000ETF": "588000ETF_5m.parquet",
    "159915ETF": "159915ETF_5m.parquet",
}

# Bar indices for 10:00-14:35 trading window
ENTRY_BAR = 6   # open of bar 6 = 10:00
EXIT_BAR = 42   # close of bar 42 = 14:35

# Default Option Stop-Loss Parameters (OOS-validated)
DEFAULT_OPT_STOPLOSS_MODE = "opt_time_decay_trailing"
DEFAULT_OPT_STOPLOSS_PARAM = 0.30           # Initial trailing gap (30%)
DEFAULT_OPT_TIME_TIGHTEN_FACTOR = 0.40      # Time tightening factor (40% decay by 14:35)


def _bs_price(S: float, K: float, T: float, r: float, sigma: float, is_call: bool) -> float:
    """Black-Scholes option price (spot-based)."""
    if T <= 1e-7 or sigma <= 1e-7:
        return max(0.0, S - K) if is_call else max(0.0, K - S)
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    if is_call:
        return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
    else:
        return K * math.exp(-r * T) * _cdf(-d2) - S * _cdf(-d1)


def _cdf(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


@lru_cache(maxsize=16)
def load_option_data(etf: str) -> dict:
    """
    Load and pre-index all option data for fast simulation.
    
    Returns dict with:
      - strike_lookup: dict[(date_ts, expiry_ts, opt_type)] -> (strikes_fp32, contracts, mults, volumes)
      - prev_vol_lookup: dict[(date_ts, contract_id)] -> previous day volume (float)
      - intraday_vol_lookup: dict[(contract_id, date)] -> cumulative volume before 10:00
      - opt_5m_lookup: dict[(contract_id, date)] -> (opens, highs, lows, closes, datetimes)
      - etf_spots: dict[date] -> (spot_entry, spot_exit, entry_dt, exit_dt)
      - expiries: sorted list of expiry Timestamps
    """
    # Load instruments
    inst_path = DATA_DIR / f"{etf}_instruments.parquet"
    if not inst_path.exists():
        raise FileNotFoundError(f"Instruments not found: {inst_path}")
    inst = pd.read_parquet(inst_path)
    inst["maturity_date"] = pd.to_datetime(inst["maturity_date"])
    inst_slim = inst[["order_book_id", "maturity_date", "option_type"]].drop_duplicates()
    
    # Load daily option prices
    prices_path = DATA_DIR / f"{etf}_historical_prices.parquet"
    if not prices_path.exists():
        raise FileNotFoundError(f"Daily option prices not found: {prices_path}")
    opt_daily = pd.read_parquet(prices_path)
    opt_daily["date"] = pd.to_datetime(opt_daily["date"])
    opt_daily = opt_daily.merge(inst_slim, on="order_book_id", how="left")
    
    # Deduplicate: keep highest volume per (date, strike, type, maturity)
    opt_daily = (
        opt_daily.sort_values("volume", ascending=False)
        .drop_duplicates(subset=["date", "strike_price", "option_type", "maturity_date"], keep="first")
    )
    # Filter to valid prices only
    opt_daily = opt_daily[opt_daily["close"] > 0]
    
    # Get expiries (dates with both C and P)
    expiries = (
        opt_daily.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()
        .index.tolist()
    )
    expiries = sorted(expiries)
    
    # Pre-build strike lookup: (date, expiry, opt_type) -> sorted arrays (with volume)
    strike_lookup = {}
    has_mult = "contract_multiplier" in opt_daily.columns
    
    for (date, expiry, opt_type), grp in opt_daily.groupby(["date", "maturity_date", "option_type"]):
        strikes = grp["strike_price"].values.astype(np.float32)
        contracts = grp["order_book_id"].values
        mults = grp["contract_multiplier"].values.astype(np.float32) if has_mult else np.full(len(grp), 10000.0, dtype=np.float32)
        vols = grp["volume"].values.astype(np.float32)
        
        # Sort by strike ascending
        sort_idx = np.argsort(strikes)
        strike_lookup[(date, expiry, opt_type)] = (strikes[sort_idx], contracts[sort_idx], mults[sort_idx], vols[sort_idx])
    
    # Build T-1 volume lookup: (date, contract_id) -> previous trading day's volume
    prev_vol_lookup = {}
    opt_daily_sorted = opt_daily.sort_values(["order_book_id", "date"])
    for cid, grp in opt_daily_sorted.groupby("order_book_id"):
        dates_arr = grp["date"].values
        vols_arr = grp["volume"].values.astype(np.float32)
        for i in range(1, len(dates_arr)):
            prev_vol_lookup[(pd.Timestamp(dates_arr[i]), cid)] = float(vols_arr[i - 1])
    
    # Pre-extract ETF 5m spots: date -> (spot_entry, spot_exit, entry_dt, exit_dt)
    etf_5m_file = ETF_5M_FILE.get(etf)
    if etf_5m_file is None:
        raise ValueError(f"No 5m file mapping for ETF: {etf}")
    etf_5m_path = DATA_DIR / etf_5m_file
    if not etf_5m_path.exists():
        raise FileNotFoundError(f"ETF 5m data not found: {etf_5m_path}")
    
    df_etf_5m = pd.read_parquet(etf_5m_path, columns=["datetime", "open", "high", "low", "close"])
    df_etf_5m["datetime"] = pd.to_datetime(df_etf_5m["datetime"])
    df_etf_5m["date"] = df_etf_5m["datetime"].dt.date
    df_etf_5m = df_etf_5m.sort_values(["date", "datetime"]).reset_index(drop=True)
    
    etf_spots = {}
    etf_5m_bars = {}
    for d, g in df_etf_5m.groupby("date"):
        if len(g) <= EXIT_BAR:
            continue
        g_reset = g.reset_index(drop=True)
        spot_entry = float(g_reset.iloc[ENTRY_BAR]["open"])
        spot_exit = float(g_reset.iloc[EXIT_BAR]["close"])
        if spot_entry > 0 and spot_exit > 0:
            etf_spots[d] = (spot_entry, spot_exit, g_reset.iloc[ENTRY_BAR]["datetime"], g_reset.iloc[EXIT_BAR]["datetime"])
            sub = g_reset.iloc[ENTRY_BAR:EXIT_BAR+1]
            etf_5m_bars[d] = (
                sub["open"].values.astype(np.float32),
                sub["high"].values.astype(np.float32),
                sub["low"].values.astype(np.float32),
                sub["close"].values.astype(np.float32),
                sub["datetime"].values,
            )
    
    # Load option 5m data - build (contract_id, date) -> (opens, highs, lows, closes, datetimes) lookup
    # Also build intraday_vol_lookup: (contract_id, date) -> cumulative volume before 10:00
    opt_5m_path = DATA_DIR / f"{etf}_historical_prices_5m.parquet"
    opt_5m_lookup = {}
    intraday_vol_lookup = {}
    if opt_5m_path.exists():
        print(f"    [OPTION] Loading 5m option data from {opt_5m_path.name}...")
        opt_5m = pd.read_parquet(opt_5m_path, columns=["order_book_id", "datetime", "open", "high", "low", "close", "volume"])
        opt_5m["datetime"] = pd.to_datetime(opt_5m["datetime"])
        opt_5m["date"] = opt_5m["datetime"].dt.date
        
        # Group by (contract, date) for O(1) lookup
        for (cid, d), g in opt_5m.groupby(["order_book_id", "date"]):
            g_sorted = g.sort_values("datetime")
            opt_5m_lookup[(cid, d)] = (
                g_sorted["open"].values.astype(np.float32),
                g_sorted["high"].values.astype(np.float32),
                g_sorted["low"].values.astype(np.float32),
                g_sorted["close"].values.astype(np.float32),
                g_sorted["datetime"].values,  # numpy datetime64
            )
            # Cumulative volume before 10:00 (first ENTRY_BAR=6 bars: 09:35-10:00)
            vol_vals = g_sorted["volume"].values
            intraday_vol_lookup[(cid, d)] = float(vol_vals[:ENTRY_BAR].sum()) if len(vol_vals) > 0 else 0.0
        
        print(f"    [OPTION] Built {len(opt_5m_lookup)} (contract, day) price lookups")
    else:
        print(f"    [OPTION] 5m option data not found ({opt_5m_path.name}), using Black-Scholes fallback")
    
    return {
        "strike_lookup": strike_lookup,
        "prev_vol_lookup": prev_vol_lookup,
        "intraday_vol_lookup": intraday_vol_lookup,
        "opt_5m_lookup": opt_5m_lookup,
        "etf_spots": etf_spots,
        "etf_5m_bars": etf_5m_bars,
        "expiries": expiries,
    }


def _find_otm_strike(
    strike_lookup: dict,
    expiries: list,
    date_ts: pd.Timestamp,
    spot: float,
    direction: int,
    min_dtm: int,
):
    """
    Fast OTM strike selection using pre-sorted arrays and binary search.
    Returns (contract_id, strike, expiry, multiplier, dtm) or None.
    """
    expiry_date = None
    for exp in expiries:
        if exp > date_ts and (exp - date_ts).days >= min_dtm:
            expiry_date = exp
            break
    if expiry_date is None:
        return None
    
    opt_type = "C" if direction > 0 else "P"
    key = (date_ts, expiry_date, opt_type)
    
    if key not in strike_lookup:
        return None
    
    strikes_sorted, contracts_sorted, mults_sorted, _vols = strike_lookup[key]
    
    if opt_type == "C":
        idx = np.searchsorted(strikes_sorted, spot, side="right")
        if idx >= len(strikes_sorted):
            return None
    else:
        idx = np.searchsorted(strikes_sorted, spot, side="left") - 1
        if idx < 0:
            return None
    
    return (contracts_sorted[idx], float(strikes_sorted[idx]), expiry_date, float(mults_sorted[idx]), (expiry_date - date_ts).days)


STRIKE_MODES = ["otm", "nearest", "vol_t1", "vol_intraday", "cascade"]

# ETF-adaptive default strike modes (A/B validated on _p2016_2024 OOS 2024-2025)
STRIKE_MODE_DEFAULTS = {
    "300ETF": "cascade",      # Shanghai, large gaps → distance + gamma guard
    "500ETF": "nearest",      # Shanghai, large gaps → simple closest
    "50ETF": "cascade",       # Shanghai, similar to 300ETF
    "159915ETF": "vol_t1",    # Shenzhen, liquidity matters more
    "588000ETF": "cascade",   # Shanghai, default cascade
}


def resolve_strike_mode(etf: str, user_mode: str = "auto") -> str:
    """Resolve ETF-adaptive strike mode. 'auto' uses per-ETF default from A/B test."""
    if user_mode != "auto":
        return user_mode
    return STRIKE_MODE_DEFAULTS.get(etf, "cascade")


def _find_strike(
    strike_lookup: dict,
    expiries: list,
    date_ts: pd.Timestamp,
    spot: float,
    direction: int,
    min_dtm: int,
    mode: str = "otm",
    prev_vol_lookup: dict = None,
    intraday_vol_lookup: dict = None,
    gamma_threshold: float = 0.4,
    tie_ratio: float = 1.3,
):
    """
    Unified strike selector supporting multiple A/B modes.
    Returns (contract_id, strike, expiry, multiplier, dtm) or None.
    
    Modes:
      otm          - Always nearest OTM (baseline)
      nearest      - Pick closer of ITM1/OTM1 by distance to spot
      vol_t1       - Pick ITM1/OTM1 with higher T-1 daily volume
      vol_intraday - Pick ITM1/OTM1 with higher pre-10:00 cumulative volume
      cascade      - Distance-first + gamma guard + volume tie-breaker
    """
    # Fast path for baseline
    if mode == "otm":
        return _find_otm_strike(strike_lookup, expiries, date_ts, spot, direction, min_dtm)
    
    # Find expiry
    expiry_date = None
    for exp in expiries:
        if exp > date_ts and (exp - date_ts).days >= min_dtm:
            expiry_date = exp
            break
    if expiry_date is None:
        return None
    
    opt_type = "C" if direction > 0 else "P"
    key = (date_ts, expiry_date, opt_type)
    if key not in strike_lookup:
        return None
    
    strikes_sorted, contracts_sorted, mults_sorted, vols_sorted = strike_lookup[key]
    n = len(strikes_sorted)
    dtm = (expiry_date - date_ts).days
    date_d = date_ts.date()
    
    # Locate OTM1 and ITM1 indices
    if opt_type == "C":
        # Calls: OTM = first strike > spot, ITM = last strike < spot
        otm_idx = int(np.searchsorted(strikes_sorted, spot, side="right"))
        itm_idx = otm_idx - 1
    else:
        # Puts: OTM = last strike < spot, ITM = first strike > spot
        otm_idx = int(np.searchsorted(strikes_sorted, spot, side="left")) - 1
        itm_idx = otm_idx + 1
    
    # Validate indices
    otm_valid = 0 <= otm_idx < n
    itm_valid = 0 <= itm_idx < n
    
    # If only one side available, use it
    if otm_valid and not itm_valid:
        idx = otm_idx
    elif itm_valid and not otm_valid:
        idx = itm_idx
    elif not otm_valid and not itm_valid:
        return None
    else:
        # Both available — apply mode logic
        strike_otm = float(strikes_sorted[otm_idx])
        strike_itm = float(strikes_sorted[itm_idx])
        dist_otm = abs(spot - strike_otm)
        dist_itm = abs(spot - strike_itm)
        contract_otm = contracts_sorted[otm_idx]
        contract_itm = contracts_sorted[itm_idx]
        
        if mode == "nearest":
            idx = otm_idx if dist_otm <= dist_itm else itm_idx
        
        elif mode == "vol_t1":
            vol_otm = prev_vol_lookup.get((date_ts, contract_otm), 0.0) if prev_vol_lookup else 0.0
            vol_itm = prev_vol_lookup.get((date_ts, contract_itm), 0.0) if prev_vol_lookup else 0.0
            idx = otm_idx if vol_otm >= vol_itm else itm_idx
        
        elif mode == "vol_intraday":
            vol_otm = intraday_vol_lookup.get((contract_otm, date_d), 0.0) if intraday_vol_lookup else 0.0
            vol_itm = intraday_vol_lookup.get((contract_itm, date_d), 0.0) if intraday_vol_lookup else 0.0
            idx = otm_idx if vol_otm >= vol_itm else itm_idx
        
        elif mode == "cascade":
            # Gamma guard: if OTM is close enough to spot, keep OTM for gamma benefit
            strike_gap = abs(strike_otm - strike_itm) if strike_otm != strike_itm else 1.0
            if dist_otm <= gamma_threshold * strike_gap:
                idx = otm_idx
            else:
                # Pick closer strike
                if dist_otm <= dist_itm:
                    idx = otm_idx
                elif dist_itm < dist_otm / tie_ratio:
                    # ITM clearly closer
                    idx = itm_idx
                else:
                    # Similar distance — volume tie-breaker
                    vol_otm = prev_vol_lookup.get((date_ts, contract_otm), 0.0) if prev_vol_lookup else 0.0
                    vol_itm = prev_vol_lookup.get((date_ts, contract_itm), 0.0) if prev_vol_lookup else 0.0
                    idx = otm_idx if vol_otm >= vol_itm else itm_idx
        else:
            # Unknown mode fallback to OTM
            idx = otm_idx
    
    return (contracts_sorted[idx], float(strikes_sorted[idx]), expiry_date, float(mults_sorted[idx]), dtm)


def _get_5m_price(
    opt_5m_lookup: dict,
    contract_id: str,
    date_d,
    bar_dt_np: np.datetime64,
    is_entry: bool,
    spot: float,
    strike: float,
    opt_type: str,
    dtm: int,
    iv: float,
) -> float:
    """Fast 5m price lookup using numpy arrays. Falls back to BS."""
    key = (contract_id, date_d)
    if key in opt_5m_lookup:
        opens, highs, lows, closes, dts = opt_5m_lookup[key]
        if len(dts) > 0:
            closest_idx = int(np.argmin(np.abs(dts - bar_dt_np)))
            val = float(opens[closest_idx]) if is_entry else float(closes[closest_idx])
            if val > 0:
                return val
    
    # Black-Scholes fallback
    is_call = (opt_type == "C")
    T = max(1e-5, dtm / 365.0)
    return max(0.0001, _bs_price(spot, strike, T, 0.02, iv, is_call))


def _get_option_5m_series(
    opt_5m_lookup: dict,
    contract_id: str,
    date_d,
    etf_bar_dts: np.ndarray,
    etf_opens: np.ndarray,
    etf_highs: np.ndarray,
    etf_lows: np.ndarray,
    etf_closes: np.ndarray,
    strike: float,
    opt_type: str,
    dtm: int,
    iv: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns (opens, highs, lows, closes) float32 arrays for option 5m bars aligned with ETF 5m datetimes.
    Vectorized: uses searchsorted for O(n log m) datetime matching instead of per-bar argmin.
    """
    n_bars = len(etf_bar_dts)
    opens = np.zeros(n_bars, dtype=np.float32)
    highs = np.zeros(n_bars, dtype=np.float32)
    lows = np.zeros(n_bars, dtype=np.float32)
    closes = np.zeros(n_bars, dtype=np.float32)
    
    key = (contract_id, date_d)
    has_opt = key in opt_5m_lookup
    matched = np.zeros(n_bars, dtype=np.bool_)
    
    if has_opt:
        opt_o, opt_h, opt_l, opt_c, opt_dts = opt_5m_lookup[key]
        if len(opt_dts) > 0:
            # Vectorized closest-index matching via searchsorted
            idx = np.searchsorted(opt_dts, etf_bar_dts, side='left')
            idx = np.clip(idx, 0, len(opt_dts) - 1)
            # Check if idx-1 is closer
            idx_m1 = np.maximum(idx - 1, 0)
            diff_idx = np.abs(opt_dts[idx].astype(np.int64) - etf_bar_dts.astype(np.int64))
            diff_m1 = np.abs(opt_dts[idx_m1].astype(np.int64) - etf_bar_dts.astype(np.int64))
            use_prev = diff_m1 < diff_idx
            idx = np.where(use_prev, idx_m1, idx)
            # Validate within 300s tolerance
            diff_sec = np.abs(opt_dts[idx].astype(np.int64) - etf_bar_dts.astype(np.int64)) / 1_000_000_000
            valid = (diff_sec <= 300)
            # Check prices positive
            o_vals = opt_o[idx]
            c_vals = opt_c[idx]
            price_ok = (o_vals > 0) & (c_vals > 0)
            matched = valid & price_ok
            # Fill matched bars
            if matched.any():
                h_vals = opt_h[idx[matched]]
                l_vals = opt_l[idx[matched]]
                o_m = o_vals[matched]
                c_m = c_vals[matched]
                opens[matched] = o_m
                highs[matched] = np.maximum(h_vals, np.maximum(o_m, c_m))
                l_safe = np.where(l_vals > 0, l_vals, np.minimum(o_m, c_m))
                lows[matched] = np.minimum(l_safe, np.minimum(o_m, c_m))
                closes[matched] = c_m
    
    # BS fallback for unmatched bars
    if not matched.all():
        is_call = (opt_type == "C")
        T = max(1e-5, dtm / 365.0)
        um = ~matched
        um_idx = np.where(um)[0]
        for k in um_idx:
            opens[k] = max(0.0001, _bs_price(float(etf_opens[k]), strike, T, 0.02, iv, is_call))
            h_bs = _bs_price(float(etf_highs[k]), strike, T, 0.02, iv, is_call) if is_call else _bs_price(float(etf_lows[k]), strike, T, 0.02, iv, is_call)
            l_bs = _bs_price(float(etf_lows[k]), strike, T, 0.02, iv, is_call) if is_call else _bs_price(float(etf_highs[k]), strike, T, 0.02, iv, is_call)
            highs[k] = max(0.0001, h_bs)
            lows[k] = max(0.0001, l_bs)
            closes[k] = max(0.0001, _bs_price(float(etf_closes[k]), strike, T, 0.02, iv, is_call))
            
    return opens, highs, lows, closes


def simulate_option_portfolio(
    etf: str,
    positions_oos: np.ndarray,
    dates_oos: pd.Series,
    iv_series: np.ndarray = None,
    initial_capital: float = 100_000.0,
    trade_budget: float = None,
    trade_budget_pct: float = 0.10,
    commission_per_side: float = 4.0,
    min_days_to_maturity: int = 7,
    use_stoploss: bool = True,
    stoploss_mode: str = DEFAULT_OPT_STOPLOSS_MODE,
    stoploss_param: float = DEFAULT_OPT_STOPLOSS_PARAM,
    time_tighten_factor: float = DEFAULT_OPT_TIME_TIGHTEN_FACTOR,
    strike_mode: str = "otm",
) -> dict:
    """
    Simulate option portfolio with capital constraints & intraday stop-loss support.
    """
    opt_data = load_option_data(etf)
    strike_lookup = opt_data["strike_lookup"]
    opt_5m_lookup = opt_data["opt_5m_lookup"]
    etf_spots = opt_data["etf_spots"]
    etf_5m_bars = opt_data.get("etf_5m_bars", {})
    expiries = opt_data["expiries"]
    prev_vol_lookup = opt_data.get("prev_vol_lookup", {})
    intraday_vol_lookup = opt_data.get("intraday_vol_lookup", {})
    
    T = len(positions_oos)
    daily_pnl = np.zeros(T, dtype=np.float32)
    daily_gross_pnl = np.zeros(T, dtype=np.float32)
    capital = initial_capital
    bankrupt_day = None
    trade_records = []
    n_trades = 0
    n_stop_hits = 0
    commission_per_contract_side = commission_per_side  # RMB per contract per side
    
    dates_np = dates_oos.values  # numpy datetime64 array
    
    for i in range(T):
        pos = positions_oos[i]
        
        # Skip flat days
        if abs(pos) < 1e-5:
            continue
        
        # Bankruptcy check
        if capital <= 0:
            if bankrupt_day is None:
                bankrupt_day = i
            continue
        
        # Get date info
        date_ts = pd.Timestamp(dates_np[i])
        date_d = date_ts.date()
        
        # Get ETF spot
        if date_d not in etf_spots:
            continue
        spot_entry, spot_exit, entry_dt, exit_dt = etf_spots[date_d]
        
        # Direction: +1 -> Call, -1 -> Put
        direction = 1 if pos > 0 else -1
        
        # Find option strike using selected mode
        result = _find_strike(
            strike_lookup, expiries, date_ts, spot_entry, direction, min_days_to_maturity,
            mode=strike_mode, prev_vol_lookup=prev_vol_lookup, intraday_vol_lookup=intraday_vol_lookup,
        )
        if result is None:
            continue
        
        contract_id, strike, expiry, multiplier, dtm = result
        opt_type = "C" if direction > 0 else "P"
        
        # Get IV for BS fallback
        iv = 0.20
        if iv_series is not None and i < len(iv_series):
            iv_val = iv_series[i]
            if not np.isnan(iv_val) and iv_val > 0:
                iv = float(iv_val)
        
        # Get entry option price
        entry_px = _get_5m_price(opt_5m_lookup, contract_id, date_d, np.datetime64(entry_dt), True,
                                  spot_entry, strike, opt_type, dtm, iv)
        if entry_px <= 0:
            continue
            
        # Calculate contracts
        cost_per_contract = entry_px * multiplier
        if cost_per_contract <= 0:
            continue
        budget_for_trade = capital * trade_budget_pct if trade_budget_pct is not None else trade_budget
        contracts = budget_for_trade / cost_per_contract
        
        # Determine exit price & stoploss status
        stop_hit = False
        exit_px = _get_5m_price(opt_5m_lookup, contract_id, date_d, np.datetime64(exit_dt), False,
                                 spot_exit, strike, opt_type, dtm, iv)
        
        if use_stoploss and stoploss_mode != "baseline" and date_d in etf_5m_bars:
            e_opens, e_highs, e_lows, e_closes, e_dts = etf_5m_bars[date_d]
            o_opens, o_highs, o_lows, o_closes = _get_option_5m_series(
                opt_5m_lookup, contract_id, date_d, e_dts, e_opens, e_highs, e_lows, e_closes, strike, opt_type, dtm, iv
            )
            
            n_bars = len(e_dts)
            P_0 = entry_px
            P_peak = float(o_highs[0])
            S_peak = float(e_highs[0])
            S_trough = float(e_lows[0])
            
            for k in range(n_bars):
                o_h = float(o_highs[k])
                o_l = float(o_lows[k])
                e_h = float(e_highs[k])
                e_l = float(e_lows[k])
                
                if o_h > P_peak:
                    P_peak = o_h
                if e_h > S_peak:
                    S_peak = e_h
                if e_l < S_trough:
                    S_trough = e_l
                    
                if stoploss_mode == "opt_trailing_pct":
                    L_stop = P_peak * (1.0 - stoploss_param)
                    if o_l <= L_stop:
                        stop_hit = True
                        exit_px = max(L_stop, o_l)
                        break
                        
                elif stoploss_mode == "opt_profit_lock_trailing":
                    gamma_lock = 0.20
                    theta_init = max(stoploss_param, 0.25)
                    theta_trail = stoploss_param
                    max_gain = (P_peak - P_0) / P_0
                    L_stop = P_peak * (1.0 - theta_trail) if max_gain >= gamma_lock else P_0 * (1.0 - theta_init)
                    if o_l <= L_stop:
                        stop_hit = True
                        exit_px = max(L_stop, o_l)
                        break
                        
                elif stoploss_mode == "opt_time_decay_trailing":
                    frac_time = k / float(max(1, n_bars - 1))
                    param_curr = stoploss_param * (1.0 - time_tighten_factor * frac_time)
                    L_stop = P_peak * (1.0 - param_curr)
                    if o_l <= L_stop:
                        stop_hit = True
                        exit_px = max(L_stop, o_l)
                        break
                        
                elif stoploss_mode == "spot_trailing_pct":
                    if direction > 0:  # Call
                        S_stop = S_peak * (1.0 - stoploss_param)
                        if e_l <= S_stop:
                            stop_hit = True
                            exit_px = float(o_closes[k])
                            break
                    else:  # Put
                        S_stop = S_trough * (1.0 + stoploss_param)
                        if e_h >= S_stop:
                            stop_hit = True
                            exit_px = float(o_closes[k])
                            break
                            
                elif stoploss_mode == "spot_time_decay_trailing":
                    frac_time = k / float(max(1, n_bars - 1))
                    param_curr = stoploss_param * (1.0 - 0.4 * frac_time)
                    if direction > 0:
                        S_stop = S_peak * (1.0 - param_curr)
                        if e_l <= S_stop:
                            stop_hit = True
                            exit_px = float(o_closes[k])
                            break
                    else:
                        S_stop = S_trough * (1.0 + param_curr)
                        if e_h >= S_stop:
                            stop_hit = True
                            exit_px = float(o_closes[k])
                            break
        
        # P&L calculation
        gross_pnl = (exit_px - entry_px) * contracts * multiplier
        commission_total = commission_per_contract_side * contracts * 2.0  # per-contract, both sides
        net_pnl = gross_pnl - commission_total
        
        if stop_hit:
            n_stop_hits += 1
        
        # Update capital
        capital += net_pnl
        daily_pnl[i] = net_pnl
        daily_gross_pnl[i] = gross_pnl
        n_trades += 1
        
        trade_records.append({
            "date": date_ts.strftime("%Y-%m-%d"),
            "direction": "Long" if direction > 0 else "Short",
            "option_type": opt_type,
            "contract": contract_id,
            "strike": strike,
            "expiry": expiry.strftime("%Y-%m-%d"),
            "dtm": dtm,
            "contracts": round(contracts, 4),
            "entry_px": round(entry_px, 4),
            "exit_px": round(exit_px, 4),
            "spot_entry": round(spot_entry, 4),
            "spot_exit": round(spot_exit, 4),
            "gross_pnl": round(gross_pnl, 2),
            "commission": commission_total,
            "net_pnl": round(net_pnl, 2),
            "capital": round(capital, 2),
            "stop_hit": stop_hit,
        })
    
    # Build trade log DataFrame
    if trade_records:
        trade_log_df = pd.DataFrame(trade_records)
    else:
        trade_log_df = pd.DataFrame(columns=[
            "date", "direction", "option_type", "contract", "strike", "expiry",
            "dtm", "contracts", "entry_px", "exit_px", "spot_entry", "spot_exit",
            "gross_pnl", "commission", "net_pnl", "capital", "stop_hit"
        ])
    
    # Daily returns relative to initial capital (for Sharpe calculation)
    daily_returns = daily_pnl.astype(np.float64) / initial_capital
    daily_gross_returns = daily_gross_pnl.astype(np.float64) / initial_capital
    
    return {
        "daily_pnl": daily_pnl.astype(np.float64),
        "daily_gross_pnl": daily_gross_pnl.astype(np.float64),
        "daily_returns": daily_returns,
        "daily_gross_returns": daily_gross_returns,
        "trade_log_df": trade_log_df,
        "final_capital": round(capital, 2),
        "n_trades": n_trades,
        "n_stop_hits": n_stop_hits,
        "bankrupt_day": bankrupt_day,
        "initial_capital": initial_capital,
    }

