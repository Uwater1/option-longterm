#!/usr/bin/env python3
"""
Option Portfolio Simulation for NewTrade framework (optimized).
Simulates a capital-constrained option portfolio:
- 100k RMB initial capital per ETF
- Each signal deploys 10k RMB into nearest OTM option (call=long, put=short)
- Nearest expiry with >= 7 days to maturity
- Fractional contracts allowed
- 4 RMB commission per side (buy + sell)
- Bankrupt (capital <= 0) -> report all zeros afterward

Performance: pre-grouped dict lookups, numpy arrays, no per-trade DataFrame filtering.
"""

import math
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


def load_option_data(etf: str) -> dict:
    """
    Load and pre-index all option data for fast simulation.
    
    Returns dict with:
      - strike_lookup: dict[(date_ts, expiry_ts, opt_type)] -> (strikes_fp32, contracts, mults)
      - opt_5m_lookup: dict[(contract_id, date)] -> (opens_fp32, closes_fp32, datetimes_np)
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
    
    # Pre-build strike lookup: (date, expiry, opt_type) -> sorted arrays
    strike_lookup = {}
    has_mult = "contract_multiplier" in opt_daily.columns
    
    for (date, expiry, opt_type), grp in opt_daily.groupby(["date", "maturity_date", "option_type"]):
        strikes = grp["strike_price"].values.astype(np.float32)
        contracts = grp["order_book_id"].values
        mults = grp["contract_multiplier"].values.astype(np.float32) if has_mult else np.full(len(grp), 10000.0, dtype=np.float32)
        
        # Sort by strike ascending
        sort_idx = np.argsort(strikes)
        strike_lookup[(date, expiry, opt_type)] = (strikes[sort_idx], contracts[sort_idx], mults[sort_idx])
    
    # Pre-extract ETF 5m spots: date -> (spot_entry, spot_exit, entry_dt, exit_dt)
    etf_5m_file = ETF_5M_FILE.get(etf)
    if etf_5m_file is None:
        raise ValueError(f"No 5m file mapping for ETF: {etf}")
    etf_5m_path = DATA_DIR / etf_5m_file
    if not etf_5m_path.exists():
        raise FileNotFoundError(f"ETF 5m data not found: {etf_5m_path}")
    
    df_etf_5m = pd.read_parquet(etf_5m_path, columns=["datetime", "open", "close"])
    df_etf_5m["datetime"] = pd.to_datetime(df_etf_5m["datetime"])
    df_etf_5m["date"] = df_etf_5m["datetime"].dt.date
    df_etf_5m = df_etf_5m.sort_values(["date", "datetime"]).reset_index(drop=True)
    
    etf_spots = {}
    for d, g in df_etf_5m.groupby("date"):
        if len(g) <= EXIT_BAR:
            continue
        g_reset = g.reset_index(drop=True)
        spot_entry = float(g_reset.iloc[ENTRY_BAR]["open"])
        spot_exit = float(g_reset.iloc[EXIT_BAR]["close"])
        if spot_entry > 0 and spot_exit > 0:
            etf_spots[d] = (spot_entry, spot_exit, g_reset.iloc[ENTRY_BAR]["datetime"], g_reset.iloc[EXIT_BAR]["datetime"])
    
    # Load option 5m data - build (contract_id, date) -> (opens, closes, datetimes) lookup
    opt_5m_path = DATA_DIR / f"{etf}_historical_prices_5m.parquet"
    opt_5m_lookup = {}
    if opt_5m_path.exists():
        print(f"    [OPTION] Loading 5m option data from {opt_5m_path.name}...")
        opt_5m = pd.read_parquet(opt_5m_path, columns=["order_book_id", "datetime", "open", "close"])
        opt_5m["datetime"] = pd.to_datetime(opt_5m["datetime"])
        opt_5m["date"] = opt_5m["datetime"].dt.date
        
        # Group by (contract, date) for O(1) lookup
        for (cid, d), g in opt_5m.groupby(["order_book_id", "date"]):
            g_sorted = g.sort_values("datetime")
            opt_5m_lookup[(cid, d)] = (
                g_sorted["open"].values.astype(np.float32),
                g_sorted["close"].values.astype(np.float32),
                g_sorted["datetime"].values,  # numpy datetime64
            )
        
        print(f"    [OPTION] Built {len(opt_5m_lookup)} (contract, day) price lookups")
    else:
        print(f"    [OPTION] 5m option data not found ({opt_5m_path.name}), using Black-Scholes fallback")
    
    return {
        "strike_lookup": strike_lookup,
        "opt_5m_lookup": opt_5m_lookup,
        "etf_spots": etf_spots,
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
    
    strikes_sorted, contracts_sorted, mults_sorted = strike_lookup[key]
    
    if opt_type == "C":
        idx = np.searchsorted(strikes_sorted, spot, side="right")
        if idx >= len(strikes_sorted):
            return None
    else:
        idx = np.searchsorted(strikes_sorted, spot, side="left") - 1
        if idx < 0:
            return None
    
    return (contracts_sorted[idx], float(strikes_sorted[idx]), expiry_date, float(mults_sorted[idx]), (expiry_date - date_ts).days)


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
        opens, closes, dts = opt_5m_lookup[key]
        if len(dts) > 0:
            closest_idx = int(np.argmin(np.abs(dts - bar_dt_np)))
            val = float(opens[closest_idx]) if is_entry else float(closes[closest_idx])
            if val > 0:
                return val
    
    # Black-Scholes fallback
    is_call = (opt_type == "C")
    T = max(1e-5, dtm / 365.0)
    return max(0.0001, _bs_price(spot, strike, T, 0.02, iv, is_call))


def simulate_option_portfolio(
    etf: str,
    positions_oos: np.ndarray,
    dates_oos: pd.Series,
    iv_series: np.ndarray = None,
    initial_capital: float = 100_000.0,
    trade_budget: float = 10_000.0,
    commission_per_side: float = 4.0,
    min_days_to_maturity: int = 7,
) -> dict:
    """
    Simulate option portfolio with capital constraints (optimized).
    """
    opt_data = load_option_data(etf)
    strike_lookup = opt_data["strike_lookup"]
    opt_5m_lookup = opt_data["opt_5m_lookup"]
    etf_spots = opt_data["etf_spots"]
    expiries = opt_data["expiries"]
    
    T = len(positions_oos)
    daily_pnl = np.zeros(T, dtype=np.float32)
    capital = initial_capital
    bankrupt_day = None
    trade_records = []
    n_trades = 0
    commission_total = commission_per_side * 2.0
    
    # Pre-convert dates to numpy for speed
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
        
        # Get ETF spot (O(1) dict lookup)
        if date_d not in etf_spots:
            continue
        spot_entry, spot_exit, entry_dt, exit_dt = etf_spots[date_d]
        
        # Direction: +1 -> Call, -1 -> Put
        direction = 1 if pos > 0 else -1
        
        # Find nearest OTM option (binary search)
        result = _find_otm_strike(strike_lookup, expiries, date_ts, spot_entry, direction, min_days_to_maturity)
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
        
        # Get option prices (numpy lookup)
        entry_px = _get_5m_price(opt_5m_lookup, contract_id, date_d, np.datetime64(entry_dt), True,
                                  spot_entry, strike, opt_type, dtm, iv)
        exit_px = _get_5m_price(opt_5m_lookup, contract_id, date_d, np.datetime64(exit_dt), False,
                                 spot_exit, strike, opt_type, dtm, iv)
        
        if entry_px <= 0:
            continue
        
        # Calculate contracts (fractional allowed)
        cost_per_contract = entry_px * multiplier
        if cost_per_contract <= 0:
            continue
        contracts = trade_budget / cost_per_contract
        
        # P&L calculation
        gross_pnl = (exit_px - entry_px) * contracts * multiplier
        net_pnl = gross_pnl - commission_total
        
        # Update capital
        capital += net_pnl
        daily_pnl[i] = net_pnl
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
        })
    
    # Build trade log DataFrame
    if trade_records:
        trade_log_df = pd.DataFrame(trade_records)
    else:
        trade_log_df = pd.DataFrame(columns=[
            "date", "direction", "option_type", "contract", "strike", "expiry",
            "dtm", "contracts", "entry_px", "exit_px", "spot_entry", "spot_exit",
            "gross_pnl", "commission", "net_pnl", "capital"
        ])
    
    # Daily returns relative to initial capital (for Sharpe calculation)
    daily_returns = daily_pnl.astype(np.float64) / initial_capital
    
    return {
        "daily_pnl": daily_pnl.astype(np.float64),
        "daily_returns": daily_returns,
        "trade_log_df": trade_log_df,
        "final_capital": round(capital, 2),
        "n_trades": n_trades,
        "bankrupt_day": bankrupt_day,
        "initial_capital": initial_capital,
    }
