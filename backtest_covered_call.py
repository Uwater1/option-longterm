"""
备兑期权 Backtest — Covered Call + Bull Put Spread on 300ETF (510300.XSHG)
=========================================================================
Assumptions:
  - Spread: options only — buy at close*1.02 (ask), sell at close*0.98 (bid)
  - Commission: 5 RMB per option leg (open or close)
  - Exercise cost: 2 RMB if WE exercise (buyer); 0 RMB if assigned (seller)
  - Always hold to last trading day of the contract; exercise at ETF close price
  - ETF stock: no spread, no commission
  - Strike selection (OTM offset 3 or 4) driven by ATM IV of the cycle contract:
      IV > IV_THRESHOLD  → use offset 4 (further OTM)
      IV ≤ IV_THRESHOLD  → use offset 3 (closer OTM)
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import math
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from numba import njit
import os
import sys
import pandas_ta as ta

# ── Constants ────────────────────────────────────────────────────────────────
SPREAD_HALF    = 0.02        # ±2% → bid = mid*0.98, ask = mid*1.02
COMMISSION     = 2.0         # RMB per option leg, muti legs are cheaper, so on averge set 2
EXERCISE_COST  = 0.6         # RMB when WE exercise as buyer
ETF_SHARES     = 20_000      # equity leg (no cost modelled here)
NUM_CONTRACTS  = 1           # Default number of contracts to trade per leg
RISK_FREE      = 0.02        # annual risk-free rate for BS IV
IVR_HIGH       = 0.50        # IVR above this → go further OTM (offset 5)
IVR_LOW        = 0.10        # IVR below this → go closer OTM (offset 3)
IV_THRESHOLD   = 0.20        # Fallback ATM IV if calculation fails
MIN_PUT_CREDIT = 5.0         # Minimum expected net credit (RMB) for put spread per contract
PUT_BUY_LEVEL  = 1           # 0=closest ITM, 1=closest OTM
# ── Global control flags (overridden by CLI) ──────────────────────────────────
NO_FILTER_MODE = False
NO_PUT_MODE    = True
SKIP_OTM4      = True
DYNAMIC_ALPHA_MODE = False
USE_MODEL_OFFSET = False  # --model-offset: use trained open-high P10 model for limit orders
_model_meta = None        # Loaded lazily when USE_MODEL_OFFSET is True
# ── Underlying Config (Dynamic based on CLI) ───────────────────────────────────
# Default: 300ETF
ETF_NAME = "300ETF"
PATH_INST = "./data/300ETF_instruments.parquet"
PATH_OPT  = "./data/300ETF_historical_prices.parquet"
PATH_ETF  = "./data/510300_1d.parquet"
PATH_IV_CACHE = "./data/30d_iv_cache_300.parquet"

def select_underlying(etf_choice):
    global ETF_NAME, PATH_INST, PATH_OPT, PATH_ETF, PATH_IV_CACHE
    if etf_choice == "50":
        ETF_NAME = "50ETF"
        PATH_INST = "./data/50ETF_instruments.parquet"
        PATH_OPT  = "./data/50ETF_historical_prices.parquet"
        PATH_ETF  = "./data/50ETF_1d.parquet"
        PATH_IV_CACHE = "./data/30d_iv_cache_50.parquet"
    elif etf_choice == "500":
        ETF_NAME = "500ETF"
        PATH_INST = "./data/500ETF_instruments.parquet"
        PATH_OPT  = "./data/500ETF_historical_prices.parquet"
        PATH_ETF  = "./data/500ETF_1d.parquet"
        PATH_IV_CACHE = "./data/30d_iv_cache_500.parquet"
    else:
        # Default 300
        ETF_NAME = "300ETF"
        PATH_INST = "./data/300ETF_instruments.parquet"
        PATH_OPT  = "./data/300ETF_historical_prices.parquet"
        PATH_ETF  = "./data/510300_1d.parquet"
        PATH_IV_CACHE = "./data/30d_iv_cache_300.parquet"
    print(f"  Selected Underlying: {ETF_NAME}")
    print(f"  ETF Data Path      : {PATH_ETF}")


# ── Black-Scholes / IV helpers (numba-compiled) ───────────────────────────────
@njit(cache=True)
def _cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


@njit(cache=True)
def _bs_price(S, K, T, r, sigma, is_call):
    if T <= 1e-7 or sigma <= 1e-7:
        return max(0.0, S - K) if is_call else max(0.0, K - S)
    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    if is_call:
        return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
    else:
        return K * math.exp(-r * T) * _cdf(-d2) - S * _cdf(-d1)


class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()


@njit(cache=True)
def compute_iv(market_price, S, K, T, r, is_call):
    """Bisection IV solver; returns 0.5 as fallback."""
    intrinsic = max(0.0, S - K) if is_call else max(0.0, K - S)
    if market_price <= intrinsic * 0.9999 or market_price <= 0:
        return 0.50
    lo, hi = 1e-4, 10.0
    if (_bs_price(S, K, T, r, hi, is_call) - market_price) < 0:
        return 0.50          # price > BS at max vol — fallback
    for _ in range(60):
        mid = (lo + hi) * 0.5
        if _bs_price(S, K, T, r, mid, is_call) < market_price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) * 0.5




# ── Data loading ──────────────────────────────────────────────────────────────
def load_data():
    """Return (inst, opt, etf) DataFrames with parsed dates."""
    inst = pd.read_parquet(PATH_INST)
    opt  = pd.read_parquet(PATH_OPT)
    etf  = pd.read_parquet(PATH_ETF)

    inst["maturity_date"] = pd.to_datetime(inst["maturity_date"])
    opt["date"]           = pd.to_datetime(opt["date"])
    etf["date"]           = pd.to_datetime(etf["date"])

    # Merge instrument metadata into daily option prices
    # IMPORTANT: Only merge maturity_date and option_type from instruments.
    # The opt parquet already has daily-correct strike_price and contract_multiplier
    # (which change when the underlying pays dividends and contracts are adjusted).
    # Using instruments' strike/mult would give post-adjustment values for ALL dates,
    # causing incorrect OTM classification and P&L for adjusted contracts.
    inst_slim = inst[["order_book_id", "maturity_date", "option_type"]].drop_duplicates()
    opt = opt.merge(inst_slim, on="order_book_id", how="left")

    etf = etf.set_index("date").sort_index()

    # Calculate indicators
    etf["rsi14"] = ta.rsi(etf["close"], length=14)
    etf["sma20"] = ta.sma(etf["close"], length=20)
    etf["ema20"] = ta.ema(etf["close"], length=20)
    etf["sma50"] = ta.sma(etf["close"], length=50)
    etf["atr20"] = ta.atr(etf["high"], etf["low"], etf["close"], length=20)
    etf["roc10"] = ta.roc(etf["close"], length=10)
    etf["roc20"] = ta.roc(etf["close"], length=20)
    
    # Bollinger Bands
    bb = ta.bbands(etf["close"], length=20, std=2)
    if bb is not None:
        etf["bbu20"] = bb["BBU_20_2.0_2.0"]
        etf["bbl20"] = bb["BBL_20_2.0_2.0"]
    else:
        etf["bbu20"] = np.nan
        etf["bbl20"] = np.nan

    # Volatility and MACD
    etf["vol20"] = etf["close"].pct_change().rolling(20).std() * np.sqrt(252)
    etf["vol20_median"] = etf["vol20"].rolling(252).median()
    macd = ta.macd(etf["close"])
    etf["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan

    # 30d_fwd_pt no longer needed — dynamic alpha now uses indicator-based signals

    return inst, opt, etf


# ── Cycle detection ───────────────────────────────────────────────────────────
def get_cycles(opt, etf):
    """
    Return a list of dicts, one per tradeable monthly cycle:
      entry_date  – first available trading day in this cycle
      expiry_date – the contract's maturity_date (last trading day)
    Only include cycles where we have:
      - at least one call AND one put in the option data
      - ETF price data on entry_date
      - at least one trading day between entry and expiry
    We use the front-month expiry (the next expiry after data starts).
    Specifically, for each monthly expiry that is ≥ 30 days away from
    the first data date, compute entry as the trading day after the
    PRECEDING expiry (or data start if none).
    """
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt["date"].unique())

    # Find all distinct monthly expiry dates with both C and P contracts
    expiries_cp = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()                    # must have both C and P
        .index.tolist()
    )
    expiries_cp = sorted(expiries_cp)

    cycles = []
    for i, expiry in enumerate(expiries_cp):
        # Entry date = first opt trading day AFTER previous expiry
        # (or first available day for the very first cycle)
        if i == 0:
            # First cycle: enter on the first trading day in dataset
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]

        # Skip if entry >= expiry (no room to trade)
        if entry >= expiry:
            continue

        # Skip if ETF data missing on entry date
        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue

        cycles.append({"entry_date": entry, "expiry_date": expiry})

    return cycles


# ── ATM IV on a given date ────────────────────────────────────────────────────
def get_atm_iv(opt, etf, entry_date, expiry_date):
    """
    Find the ATM call option for `expiry_date` on `entry_date`
    and return its implied volatility (annualised).
    Falls back to IV_THRESHOLD if data is missing.
    """
    etf_close = etf.loc[entry_date.normalize(), "close"]
    dte = (expiry_date - entry_date).days
    T = max(dte, 1) / 365.0

    day_opt = opt[
        (opt["date"] == entry_date) &
        (opt["maturity_date"] == expiry_date) &
        (opt["option_type"] == "C") &
        (opt["close"] > 0)
    ].copy()

    if day_opt.empty:
        return IV_THRESHOLD

    # Find the call whose strike is closest to current ETF price
    day_opt["dist"] = (day_opt["strike_price"] - etf_close).abs()
    row = day_opt.loc[day_opt["dist"].idxmin()]

    iv = compute_iv(
        float(row["close"]),
        float(etf_close),
        float(row["strike_price"]),
        T,
        RISK_FREE,
        True   # call
    )
    return iv


def get_30d_iv(opt, etf, date):
    """
    Estimate the 30-day interpolated ATM IV for a given date.
    Uses linear interpolation of variance: sigma_30^2 = (sigma1^2 * (T2-30) + sigma2^2 * (30-T1)) / (T2-T1)
    """
    date_norm = date.normalize()
    if date_norm not in etf.index:
        return IV_THRESHOLD
    etf_close = float(etf.loc[date_norm, "close"])

    # All calls for this date (support fast dict lookup)
    if isinstance(opt, dict):
        day_calls = opt.get(date)
    else:
        day_calls = opt[
            (opt["date"] == date) &
            (opt["option_type"] == "C") &
            (opt["close"] > 0)
        ].copy()

    if day_calls is None or day_calls.empty:
        return IV_THRESHOLD

    # Group by expiry and find ATM strike for each
    expiries = sorted(day_calls["maturity_date"].unique())
    iv_by_expiry = {}

    for exp in expiries:
        exp_opts = day_calls[day_calls["maturity_date"] == exp].copy()
        exp_opts["dist"] = (exp_opts["strike_price"] - etf_close).abs()
        row = exp_opts.loc[exp_opts["dist"].idxmin()]
        
        dte = (exp - date).days
        T = max(dte, 1) / 365.0
        
        iv = compute_iv(
            float(row["close"]),
            float(etf_close),
            float(row["strike_price"]),
            T,
            RISK_FREE,
            True
        )
        iv_by_expiry[dte] = iv

    dtes = sorted(iv_by_expiry.keys())
    if not dtes:
        return IV_THRESHOLD

    # Select T1 (<= 30) and T2 (> 30)
    t1_candidates = [d for d in dtes if d <= 30]
    t2_candidates = [d for d in dtes if d > 30]

    if t1_candidates and t2_candidates:
        t1 = t1_candidates[-1]
        t2 = t2_candidates[0]
        v1 = iv_by_expiry[t1]**2
        v2 = iv_by_expiry[t2]**2
        # Interpolate variance
        v30 = (v1 * (t2 - 30) + v2 * (30 - t1)) / (t2 - t1)
        return math.sqrt(max(0, v30))
    elif t1_candidates:
        # Only shorter expiries available
        return iv_by_expiry[t1_candidates[-1]]
    elif t2_candidates:
        # Only longer expiries available
        return iv_by_expiry[t2_candidates[0]]
    
    return IV_THRESHOLD


# ── OTM strike selector ───────────────────────────────────────────────────────
def get_otm_strikes(opt, etf, entry_date, expiry_date, option_type, offsets):
    """
    Select actual contracts for the given OTM offsets (1-indexed rank).
    option_type: 'C' or 'P'
    offsets: list of ints, e.g. [3, 4] for call legs A and B

    Returns a list of rows (dicts) from opt, one per offset.
    Missing contracts return None at that position.
    """
    etf_close = float(etf.loc[entry_date.normalize(), "close"])

    day_opt = opt[
        (opt["date"] == entry_date) &
        (opt["maturity_date"] == expiry_date) &
        (opt["option_type"] == option_type) &
        (opt["close"] > 0)
    ].copy()

    if day_opt.empty:
        return [None] * len(offsets)

    if option_type == "C":
        # OTM calls: strike > ETF price, sorted ascending
        otm = day_opt[day_opt["strike_price"] > etf_close].sort_values("strike_price")
    else:
        # OTM puts: strike < ETF price, sorted descending (OTM1 = closest to spot)
        otm = day_opt[day_opt["strike_price"] < etf_close].sort_values(
            "strike_price", ascending=False
        )

    results = []
    for off in offsets:
        idx = off - 1          # 0-based
        if idx < len(otm):
            results.append(otm.iloc[idx].to_dict())
        else:
            results.append(None)
    return results


def get_strike_by_level(opt, etf, entry_date, expiry_date, option_type, level):
    """
    Select strike by level:
    level 0: Closest ITM (Strike >= Spot for Call, Strike <= Spot for Put)
              (Note: For puts, 'ITM' in this context means strike >= spot, 
               though strictly Puts are ITM when strike > spot)
    level 1: Closest OTM (Strike < Spot for Puts, Strike > Spot for Calls)
    """
    etf_close = float(etf.loc[entry_date.normalize(), "close"])

    day_opt = opt[
        (opt["date"] == entry_date) &
        (opt["maturity_date"] == expiry_date) &
        (opt["option_type"] == option_type) &
        (opt["close"] > 0)
    ].copy()

    if day_opt.empty:
        return None

    if option_type == "C":
        if level == 0:
            candidates = day_opt[day_opt["strike_price"] <= etf_close].sort_values("strike_price", ascending=False)
            idx = 0
        else:
            candidates = day_opt[day_opt["strike_price"] > etf_close].sort_values("strike_price")
            idx = level - 1
    else:
        # Puts
        if level == 0:
            # Research Level 0 for Puts is Strike >= Spot (Closest ITMish)
            candidates = day_opt[day_opt["strike_price"] >= etf_close].sort_values("strike_price", ascending=True)
            idx = 0
        else:
            # OTM Levels: Strike < Spot
            candidates = day_opt[day_opt["strike_price"] < etf_close].sort_values("strike_price", ascending=False)
            idx = level - 1

    if idx >= 0 and idx < len(candidates):
        return candidates.iloc[idx].to_dict()
    return None



# ── Per-cycle P&L ─────────────────────────────────────────────────────────────
def _load_model_offset():
    """Load the trained open-high model for limit order offset prediction."""
    global _model_meta
    if _model_meta is not None:
        return _model_meta
    try:
        from predict_open_high import load_model, load_and_engineer, predict_single
        etf_key = {"50ETF": "50", "300ETF": "300", "500ETF": "500"}.get(ETF_NAME, "300")
        _model_meta = load_model(etf_key)
        _model_meta["_predict_fn"] = predict_single
        _model_meta["_engineer_fn"] = load_and_engineer
        print(f"  Loaded open-high model: {_model_meta['features']}, "
              f"coverage={_model_meta['rolling_coverage']:.1f}%")
        return _model_meta
    except Exception as e:
        print(f"  WARNING: Could not load open-high model: {e}")
        print(f"  Run: python predict_open_high.py -e {etf_key}  to train first.")
        return None


def _predict_model_offset(etf_df, entry_date):
    """Predict the P10 offset (%) for a given entry date using the open-high model.
    Returns the predicted offset as a fraction (e.g., 0.003 for 0.3%), or None if unavailable."""
    meta = _load_model_offset()
    if meta is None:
        return None
    try:
        etf_key = {"50ETF": "50", "300ETF": "300", "500ETF": "500"}.get(ETF_NAME, "300")
        df = meta["_engineer_fn"](etf_key)
        # Find the row matching entry_date
        df_dates = pd.to_datetime(df["date"])
        entry_ts = pd.to_datetime(entry_date)
        mask = (df_dates - entry_ts).abs() < pd.Timedelta(days=1)
        if not mask.any():
            return None
        row = df[mask].iloc[[-1]]
        p10_pct = meta["_predict_fn"](meta, row)  # in percent
        return max(0.0, p10_pct / 100.0)  # Convert to fraction, floor at 0
    except Exception as e:
        return None


def calc_leg_pnl(leg, opt, etf, expiry_date, side, is_buyer_at_expiry, sell_spread=None):
    # NO_FILTER_MODE is set globally from CLI
    """
    Compute the full P&L (in RMB) for a single option leg.

    Parameters
    ----------
    leg                : dict (row from opt on entry date), or None
    opt                : full option DataFrame
    etf                : ETF DataFrame (indexed by date)
    expiry_date        : pd.Timestamp
    side               : 'sell' or 'buy'
    is_buyer_at_expiry : True if WE are the option buyer (put spread buy leg)
    sell_spread        : Override SPREAD_HALF for sell-side execution (from model)

    Returns dict with: entry_px, exec_px, premium_rmb, exercise_pnl_rmb,
                       commission_rmb, exercise_cost_rmb, net_rmb, note
    """
    if leg is None:
        return None

    K          = float(leg["strike_price"])
    mult       = float(leg["contract_multiplier"])
    entry_mid  = float(leg["close"])
    otype      = leg["option_type"]   # 'C' or 'P'
    contract   = str(leg.get("order_book_id", ""))
    if contract.endswith(".0"):
        contract = contract[:-2]

    # Execution price with spread
    # sell_spread is not None when model-offset limit orders are active:
    #   Limit orders don't cross the bid-ask spread — we sell at mid price.
    #   The model only predicts whether the limit will fill (90% confidence),
    #   not a price discount. Only commission applies as transaction cost.
    if sell_spread is not None and side == "sell":
        exec_px = entry_mid   # limit order: sell at mid, no spread slippage
    elif side == "sell":
        exec_px = entry_mid * (1 - SPREAD_HALF)   # market order: sell at bid
    else:
        exec_px = entry_mid * (1 + SPREAD_HALF)   # buy at ask

    # Premium in RMB (positive = cash received, negative = paid)
    if side == "sell":
        premium_rmb = exec_px * mult
    else:
        premium_rmb = -exec_px * mult

    # Last ETF close price (settlement)
    # Use the last available ETF date on or before expiry
    etf_expiry_dates = etf.index[etf.index <= expiry_date]
    if etf_expiry_dates.empty:
        etf_settle = None
    else:
        etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"])

    # Exercise outcome
    exercise_pnl_rmb = 0.0
    exercise_cost_rmb = 0.0
    note = "expires_worthless"

    if etf_settle is not None:
        if otype == "C":
            in_the_money = etf_settle > K
            intrinsic = max(0.0, etf_settle - K)
        else:
            in_the_money = etf_settle < K
            intrinsic = max(0.0, K - etf_settle)

        if in_the_money:
            if side == "sell":
                # We are ASSIGNED (seller): we pay the intrinsic, no exercise fee
                exercise_pnl_rmb  = -intrinsic * mult
                exercise_cost_rmb = 0.0
                note = f"assigned  ETF={etf_settle:.4f} K={K:.4f}"
            else:
                # We EXERCISE (buyer): we receive the intrinsic, pay exercise fee
                exercise_pnl_rmb  = intrinsic * mult
                exercise_cost_rmb = EXERCISE_COST
                note = f"exercised ETF={etf_settle:.4f} K={K:.4f}"

    commission_rmb = COMMISSION   # flat 5 RMB per leg regardless of direction

    net_rmb = (premium_rmb
               + exercise_pnl_rmb
               - commission_rmb
               - exercise_cost_rmb)

    return {
        "entry_mid":          entry_mid,
        "exec_px":            exec_px,
        "K":                  K,
        "mult":               mult,
        "otype":              otype,
        "contract":           contract,
        "side":               side,
        "premium_rmb":        premium_rmb,
        "exercise_pnl_rmb":   exercise_pnl_rmb,
        "commission_rmb":     commission_rmb,
        "exercise_cost_rmb":  exercise_cost_rmb,
        "net_rmb":            net_rmb,
        "note":               note,
    }


def calc_cycle_pnl(cyc, opt, etf, daily_ivs):
    """
    Run a full cycle and return a summary dict.
    daily_ivs is a pd.Series of 30-day interpolated IVs indexed by date.
    """
    entry  = cyc["entry_date"]
    expiry = cyc["expiry_date"]

    # Use the pre-calculated 30-day IV for signal generation
    iv = daily_ivs.get(entry, IV_THRESHOLD)

    # 1. IV Rank calculation (using 252-day daily lookback = 1 year)
    history = daily_ivs[daily_ivs.index <= entry]
    if len(history) >= 20:   # Require at least some history
        lookback = history.tail(252)
        min_iv = lookback.min()
        max_iv = lookback.max()
        if max_iv > min_iv:
            ivr = (iv - min_iv) / (max_iv - min_iv)
        else:
            ivr = 0.5
    else:
        ivr = 0.5

    # 2. Optimized Filter Logic per ETF
    idx = entry.normalize()
    rsi = etf.loc[idx, "rsi14"]
    bbu = etf.loc[idx, "bbu20"]
    bbl = etf.loc[idx, "bbl20"]
    sma20 = etf.loc[idx, "sma20"]
    sma50 = etf.loc[idx, "sma50"]
    atr20 = etf.loc[idx, "atr20"]
    roc10 = etf.loc[idx, "roc10"]
    vol20 = etf.loc[idx, "vol20"]
    vol20_median = etf.loc[idx, "vol20_median"]
    macd_hist = etf.loc[idx, "macd_hist"]
    roc20 = etf.loc[idx, "roc20"]
    etf_close_entry = float(etf.loc[idx, "close"])

    filter_would_pass = False
    if NO_PUT_MODE:
        # Calls-only Mode Optimal Filters
        if etf_choice == "50":
            # Optimized Calls-only 50ETF: RSI < 60 AND RSI > 30 AND ROC10 < 3% AND Vol20 < Vol20_median
            if pd.notna(rsi) and pd.notna(roc10) and pd.notna(vol20) and pd.notna(vol20_median):
                filter_would_pass = (rsi < 60.0) and (rsi > 30.0) and (roc10 < 3.0) and (vol20 < vol20_median)
        elif etf_choice == "500":
            # Optimized Calls-only 500ETF: RSI > 30 AND Close < BBU AND Close > SMA50
            if pd.notna(rsi) and pd.notna(bbu) and pd.notna(sma50):
                filter_would_pass = (rsi > 30.0) and (etf_close_entry < bbu) and (etf_close_entry > sma50)
        else: # 300ETF
            # Optimized Calls-only 300ETF: RSI < 72 AND RSI > 25 AND MACD Histogram < 0
            if pd.notna(rsi) and pd.notna(macd_hist):
                filter_would_pass = (rsi < 72.0) and (rsi > 25.0) and (macd_hist < 0.0)
    else:
        # With-Put Mode Optimal Filters
        if etf_choice == "50":
            # Optimized With-Put 50ETF: RSI > 30 AND Close < BBU - 0.5 * ATR20 AND ROC10 < 7%
            if pd.notna(rsi) and pd.notna(bbu) and pd.notna(atr20) and pd.notna(roc10):
                filter_would_pass = (rsi > 30.0) and (etf_close_entry < (bbu - 0.5 * atr20)) and (roc10 < 7.0)
        elif etf_choice == "500":
            # Optimized With-Put 500ETF: RSI > 35 AND Close < BBU AND Close > SMA50
            if pd.notna(rsi) and pd.notna(bbu) and pd.notna(sma50):
                filter_would_pass = (rsi > 35.0) and (etf_close_entry < bbu) and (etf_close_entry > sma50)
        else: # 300ETF
            # Optimized With-Put 300ETF: RSI < 66 AND RSI > 25 AND Close < BBU + 0.5 * ATR20 AND ROC10 < 7%
            if pd.notna(rsi) and pd.notna(bbu) and pd.notna(atr20) and pd.notna(roc10):
                filter_would_pass = (rsi < 66.0) and (rsi > 25.0) and (etf_close_entry < (bbu + 0.5 * atr20)) and (roc10 < 7.0)

    # In no-filter mode, always pass (sell OTM2+OTM3); otherwise use actual filter
    filter_passed = True if NO_FILTER_MODE else filter_would_pass

    # 3. Constant Sizing
    num_contracts = NUM_CONTRACTS

    # Call Selection
    if DYNAMIC_ALPHA_MODE:
        # Dynamic Alpha: signal-based OTM switching (always trade)
        # Best signals from research_synthetic_otm.py combo analysis:
        #   300ETF: 30 < RSI < 60  -> Combo A (OTM2+OTM3), else -> Combo B (OTM4)
        #   50ETF:  RSI > 30       -> Combo A, else -> Combo B
        #   500ETF: RSI>35 + Close<BBU + Close>SMA50 -> Combo A, else -> Combo B
        # Add roc20 caution filters for vertical rallies (roc20 < threshold):
        if etf_choice == "50":
            signal_strong = pd.notna(rsi) and rsi > 30 and (pd.isna(roc20) or roc20 < 3.0)
        elif etf_choice == "500":
            signal_strong = (pd.notna(rsi) and pd.notna(bbu) and pd.notna(sma50)
                             and rsi > 35 and etf_close_entry < bbu and etf_close_entry > sma50)
        else:  # 300ETF
            signal_strong = pd.notna(rsi) and 30 < rsi < 60 and (pd.isna(roc20) or roc20 < 4.0)

        if signal_strong:
            call_offsets = [2, 3]  # Combo A (Aggressive)
        else:
            call_offsets = [4]     # Combo B (Conservative)

        call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", call_offsets)
        legs_to_process = []
        for i, off in enumerate(call_offsets):
            if i < len(call_legs) and call_legs[i] is not None:
                tag = "A" if signal_strong else "B"
                legs_to_process.append((call_legs[i], "sell", f"Call OTM{off} (Dyn-{tag})"))
        # In dynamic mode, override filter_passed to True (always trade)
        filter_passed = True
    elif filter_passed:
        call_offsets = [2, 3]
        call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", call_offsets)
        legs_to_process = []
        if len(call_offsets) > 0 and call_legs[0] is not None:
            legs_to_process.append((call_legs[0], "sell", f"Call Leg A (OTM{call_offsets[0]})"))
        if len(call_offsets) > 1 and call_legs[1] is not None:
            legs_to_process.append((call_legs[1], "sell", f"Call Leg B (OTM{call_offsets[1]})"))
    else:
        if not SKIP_OTM4:
            call_offsets = [4]
            call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", call_offsets)
            legs_to_process = []
            if call_legs[0] is not None:
                legs_to_process.append((call_legs[0], "sell", "Call Leg C (OTM4)"))
        else:
            call_offsets = []
            legs_to_process = []
    
    # 4. Put Selection (V7: Long Put driven by research "Buyer Advantage")
    # Buy one put option at either closest ITM (level 0) or closest OTM (level 1)
    if not NO_PUT_MODE:
        put_leg = get_strike_by_level(opt, etf, entry, expiry, "P", PUT_BUY_LEVEL)
        put_valid = (put_leg is not None)
        put_offsets = [PUT_BUY_LEVEL, PUT_BUY_LEVEL] # reuse list for logging

        if put_valid:
            legs_to_process.append((put_leg, "buy", f"Put Buy    (Level {PUT_BUY_LEVEL})"))
    else:
        put_offsets = []

    # Model-based limit order offset (if enabled)
    model_spread = None
    if USE_MODEL_OFFSET:
        p10_frac = _predict_model_offset(etf, entry)
        if p10_frac is not None:
            # Sell at mid * (1 - p10_frac): the limit order that fills 90% of the time
            # p10_frac is how much the ETF rises → option price rises → our limit fills
            # Effective spread = p10_frac (smaller = better for seller)
            model_spread = max(0.0, p10_frac)

    results = []
    
    for leg, side, label in legs_to_process:
        res = calc_leg_pnl(leg, opt, etf, expiry, side, side == "buy",
                           sell_spread=model_spread if side == "sell" else None)
        if res is not None:
            # Scale exactly by the number of contracts
            res["premium_rmb"] *= num_contracts
            res["exercise_pnl_rmb"] *= num_contracts
            res["commission_rmb"] *= num_contracts
            res["exercise_cost_rmb"] *= num_contracts
            res["net_rmb"] *= num_contracts
            res["mult"] *= num_contracts
            
            res["label"] = label
            results.append(res)

    total_net = sum(r["net_rmb"] for r in results)
    total_premium = sum(r["premium_rmb"] for r in results)

    return {
        "entry_date":     entry,
        "expiry_date":    expiry,
        "iv":             iv,
        "ivr":            ivr,
        "rsi":            rsi,
        "bbu":            bbu,
        "filter_passed":  filter_passed,
        "filter_would_pass": filter_would_pass,
        "call_offsets":   call_offsets,
        "put_offsets":    put_offsets,
        "num_contracts":  num_contracts,
        "etf_entry":      etf_close_entry,
        "legs":           results,
        "total_premium":  total_premium,
        "total_net_rmb":  total_net,
    }




# ── Main backtest runner ───────────────────────────────────────────────────────
def save_csv(results, csv_path):
    rows = []
    for r in results:
        row = {
            "entry_date": r["entry_date"].strftime("%Y-%m-%d"),
            "expiry_date": r["expiry_date"].strftime("%Y-%m-%d"),
            "etf_entry": round(r["etf_entry"], 4),
            "iv": round(r["iv"], 4),
            "ivr": round(r["ivr"], 4),
            "rsi": round(r["rsi"], 2) if pd.notna(r["rsi"]) else "",
            "bbu": round(r["bbu"], 4) if pd.notna(r["bbu"]) else "",
            "filter_passed": r["filter_passed"],
            "filter_would_pass": r["filter_would_pass"],
            "call_offsets": "+".join(str(o) for o in r["call_offsets"]) if r["call_offsets"] else "",
            "put_offsets": "+".join(str(o) for o in r["put_offsets"]) if r["put_offsets"] else "",
            "num_contracts": r["num_contracts"],
            "total_premium": round(r["total_premium"], 2),
            "total_net_rmb": round(r["total_net_rmb"], 2),
        }
        for leg in r["legs"]:
            label_clean = leg["label"].replace(" ", "_")
            row[f"{label_clean}_contract"] = leg.get("contract", "")
            row[f"{label_clean}_K"] = round(leg["K"], 4)
            row[f"{label_clean}_side"] = leg["side"]
            row[f"{label_clean}_exec_px"] = round(leg["exec_px"], 4)
            row[f"{label_clean}_premium"] = round(leg["premium_rmb"], 2)
            row[f"{label_clean}_exercise"] = round(leg["exercise_pnl_rmb"], 2)
            row[f"{label_clean}_net"] = round(leg["net_rmb"], 2)
            row[f"{label_clean}_note"] = leg["note"]
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"  CSV  saved → {csv_path}")


def run_backtest(opt, etf):
    if os.path.exists(PATH_IV_CACHE):
        print(f"\nLoading pre-calculated 30-day IVs from {PATH_IV_CACHE}...")
        daily_ivs = pd.read_parquet(PATH_IV_CACHE).iloc[:, 0]
        # Ensure it's indexed by datetime
        daily_ivs.index = pd.to_datetime(daily_ivs.index)
    else:
        print("\nPre-calculating daily 30-day IVs (this may take a moment)...")
        trading_days = sorted(etf.index.unique())
        # Pre-group options by date for 740x speedup
        day_calls_dict = {d: group for d, group in opt[(opt["option_type"] == "C") & (opt["close"] > 0)].groupby("date")}
        iv_data = {}
        for i, d in enumerate(trading_days):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(trading_days)}")
            iv_data[d] = get_30d_iv(day_calls_dict, etf, d)
        daily_ivs = pd.Series(iv_data).sort_index()
        # Save cache
        os.makedirs(os.path.dirname(PATH_IV_CACHE), exist_ok=True)
        daily_ivs.to_frame("iv").to_parquet(PATH_IV_CACHE)
        print(f"  Saved IV cache to {PATH_IV_CACHE}")

    cycles  = get_cycles(opt, etf)
    results = []
    for cyc in cycles:
        res = calc_cycle_pnl(cyc, opt, etf, daily_ivs)
        results.append(res)

    # ── Per-cycle detail printout ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    # Build mode label from active flags
    mode_parts = []
    if DYNAMIC_ALPHA_MODE:
        mode_parts.append("DYNAMIC ALPHA (dynamic OTM offsets)")
    if USE_MODEL_OFFSET:
        mode_parts.append("MODEL OFFSET (open-high P10 limit orders)")
    if not mode_parts:
        mode_parts.append("NO-FILTER (always sell OTM2+OTM3)" if NO_FILTER_MODE else "FILTERED (RSI+BBU)")
    mode_label = " + ".join(mode_parts)
    print(f"  备兑期权 BACKTEST — Cycle Detail  [{mode_label}]")
    print("=" * 70)

    for res in results:
        call_str = "+".join([f"OTM{o}" for o in res['call_offsets']])
        total_legs_contracts = sum(res['num_contracts'] for _ in res['legs'])
        unit_str = "contract" if res['num_contracts'] == 1 else "contracts"
        # Show what filter WOULD have decided (even in no-filter mode)
        if NO_FILTER_MODE and not res['filter_would_pass']:
            filter_tag = "[FILTER WOULD FAIL — overridden to OTM2+OTM3]"
        else:
            filter_tag = "[FILTER PASS]" if res['filter_would_pass'] else "[FILTER FAIL]"
        puts_str = "None" if NO_PUT_MODE else f"Level{PUT_BUY_LEVEL}"
        print(f"\nCycle  {res['entry_date'].date()} → {res['expiry_date'].date()}"
              f"   IV={res['iv']:.1%} (IVR={res['ivr']:.2f})  calls={call_str} puts={puts_str}"
              f"   ETF={res['etf_entry']:.4f} RSI={res['rsi']:.1f} BBU={res['bbu']:.3f} "
              f"(Total {total_legs_contracts} contracts) {filter_tag}")
        hdr = f"  {'Leg':<25} {'side':>4} {'K':>7} {'exec_px':>8} {'prem':>8}  {'exer':>9}  {'net':>8}"
        print(hdr)
        print("  " + "-" * (len(hdr) - 2))
        for r in res["legs"]:
            print(f"  {r['label']:<25} {r['side']:>4} {r['K']:>7.3f}"
                  f" {r['exec_px']:>8.4f} {r['premium_rmb']:>8.2f}"
                  f"  {r['exercise_pnl_rmb']:>9.2f}  {r['net_rmb']:>8.2f}"
                  f"  [{r['note']}]")
        print(f"  {'CYCLE TOTAL':>49}  {res['total_net_rmb']:>8.2f}")

    # ── Aggregate summary ─────────────────────────────────────────────────────
    nets       = [r["total_net_rmb"]  for r in results]
    premiums   = [r["total_premium"]  for r in results]
    cumulative = list(np.cumsum(nets))
    total_net  = sum(nets)
    win_rate   = sum(1 for n in nets if n > 0) / len(nets) if nets else 0
    avg_prem   = np.mean(premiums) if premiums else 0

    # ── Placement rate & filter lift metrics ──────────────────────────────
    n_cycles_total = len(results)
    n_placed = sum(1 for r in results if r["filter_would_pass"])
    placement_rate = n_placed / n_cycles_total if n_cycles_total > 0 else 0.0

    # Filter lift: avg P&L per placed cycle minus avg P&L per total cycle
    # (positive = filter adds value by blocking losing cycles)
    placed_pnls = [r["total_net_rmb"] for r in results if r["filter_would_pass"]]
    avg_pnl_placed = np.mean(placed_pnls) if placed_pnls else 0.0
    avg_pnl_all = np.mean(nets) if nets else 0.0
    filter_lift = avg_pnl_placed - avg_pnl_all

    print("\n" + "=" * 70)
    # Build summary label from active flags
    sum_parts = []
    if DYNAMIC_ALPHA_MODE:
        sum_parts.append("DYNAMIC ALPHA")
    if USE_MODEL_OFFSET:
        sum_parts.append("MODEL OFFSET")
    if not sum_parts:
        sum_parts.append("NO-FILTER" if NO_FILTER_MODE else "FILTERED")
    mode_label_sum = " + ".join(sum_parts)
    print(f"  SUMMARY  [{mode_label_sum}]")
    print("=" * 70)
    print(f"  Cycles traded          : {len(results)}")
    print(f"  Winning cycles         : {sum(1 for n in nets if n > 0)}/{len(nets)}"
          f"  ({win_rate:.0%})")
    print(f"  Avg gross premium/cyc  : {avg_prem:>8.2f} RMB")
    print(f"  Total net P&L          : {total_net:>8.2f} RMB")
    print(f"  Cumulative by cycle    : {[f'{v:.0f}' for v in cumulative]}")
    print(f"  ── Placement & Filter Lift ─────────────────────────────────────")
    print(f"  Placement rate         : {placement_rate:.1%}  ({n_placed}/{n_cycles_total} cycles)")
    print(f"  Avg P&L / placed cycle : {avg_pnl_placed:>+8.2f} RMB")
    print(f"  Avg P&L / all cycles   : {avg_pnl_all:>+8.2f} RMB")
    print(f"  Filter lift            : {filter_lift:>+8.2f} RMB/cycle")
    print(f"  ─────────────────────────────────────────────────────────────")

    # ── No-Filter: Blocked cycle analysis ─────────────────────────────────────────
    if NO_FILTER_MODE:
        blocked = [r for r in results if not r['filter_would_pass']]
        passed  = [r for r in results if r['filter_would_pass']]
        blocked_pnl = sum(r['total_net_rmb'] for r in blocked)
        passed_pnl  = sum(r['total_net_rmb'] for r in passed)
        blocked_win = sum(1 for r in blocked if r['total_net_rmb'] > 0)
        print(f"\n  ── Filter Would-Block Analysis ─────────────────────────────")
        print(f"  Cycles filter WOULD pass : {len(passed)}/{len(results)}  (P&L = {passed_pnl:>+.2f} RMB)")
        print(f"  Cycles filter WOULD block: {len(blocked)}/{len(results)}  (P&L = {blocked_pnl:>+.2f} RMB)")
        if blocked:
            print(f"  Blocked win rate         : {blocked_win}/{len(blocked)} ({blocked_win/len(blocked):.0%})")
            print(f"\n  Blocked cycle detail:")
            for r in blocked:
                tag = "WIN" if r['total_net_rmb'] > 0 else "LOSS"
                print(f"    {r['entry_date'].date()} → {r['expiry_date'].date()}  "
                      f"RSI={r['rsi']:.1f}  ETF={r['etf_entry']:.4f}  "
                      f"P&L={r['total_net_rmb']:>+10.2f}  [{tag}]")
        print(f"  ─────────────────────────────────────────────────────────────")

    # ── Chart ─────────────────────────────────────────────────────────────────
    filter_suffix = "_nofilter" if NO_FILTER_MODE else ""
    put_suffix = "_withput" if not NO_PUT_MODE else ""
    otm4_suffix = "_noskipotm4" if not SKIP_OTM4 else ""
    alpha_suffix = "_alpha" if DYNAMIC_ALPHA_MODE else ""
    model_suffix = "_modeloffset" if USE_MODEL_OFFSET else ""
    out_file = f"backtest/backtest_cc_{ETF_NAME}{filter_suffix}{put_suffix}{otm4_suffix}{alpha_suffix}{model_suffix}.png"
    os.makedirs("backtest", exist_ok=True)
    plot_backtest_results(results, etf, out_file)

    csv_file = f"backtest/backtest_cc_{ETF_NAME}{filter_suffix}{put_suffix}{otm4_suffix}{alpha_suffix}{model_suffix}.csv"
    save_csv(results, csv_file)

    return results


def plot_backtest_results(results, etf, out_path):
    """
    Advanced plotting for backtest results including P&L, Drawdown, and Leg Breakdown.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    
    # 1. Prepare Data
    dates = [r['expiry_date'] for r in results]
    nets = [r['total_net_rmb'] for r in results]
    cumulative = np.cumsum(nets)
    
    # Calculate Drawdown
    peaks = np.maximum.accumulate(cumulative)
    drawdown = np.zeros_like(cumulative)
    peak_mask = peaks > 0
    drawdown[peak_mask] = (cumulative[peak_mask] - peaks[peak_mask]) / peaks[peak_mask]
    max_dd = np.min(drawdown) if len(drawdown) > 0 else 0
    
    # Normalize ETF for overlay
    etf_sub = etf.reindex(dates, method='ffill')['close']
    etf_norm = (etf_sub / etf_sub.iloc[0] - 1) * 100 # % change
    
    # Calculate key metrics
    total_net = cumulative[-1]
    win_rate = sum(1 for n in nets if n > 0) / len(results) if results else 0
    sharpe = np.sqrt(12) * np.mean(nets) / np.std(nets) if len(nets) > 1 and np.std(nets) > 0 else 0
    
    # 2. Setup Figure
    try:
        plt.style.use('seaborn-v0_8-muted')
    except:
        plt.style.use('ggplot')
        
    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 3, 2], hspace=0.3)
    
    COLOR_CUM = "#2980b9"
    COLOR_BAR_UP = "#27ae60"
    COLOR_BAR_DN = "#e74c3c"
    COLOR_ETF = "#f39c12"
    
    # ── TOP PANEL ─────────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    x = np.arange(len(results))
    bar_colors = [COLOR_BAR_UP if n >= 0 else COLOR_BAR_DN for n in nets]
    ax1.bar(x, nets, color=bar_colors, alpha=0.3, label="Net P&L per Cycle")
    ax1.plot(x, cumulative, color=COLOR_CUM, linewidth=2.5, marker='o', markersize=4, label="Cumulative P&L")
    ax1.set_ylabel("P&L (RMB)", fontsize=10, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(x, etf_norm, color=COLOR_ETF, linestyle='--', linewidth=1.5, alpha=0.7, label="Underlying ETF (%)")
    ax1_twin.set_ylabel("ETF Return (%)", color=COLOR_ETF, fontsize=10, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor=COLOR_ETF)
    
    cycle_labels = [r['expiry_date'].strftime('%y-%m') for r in results]
    ax1.set_xticks(x)
    ax1.set_xticklabels(cycle_labels, rotation=45 if len(x) > 15 else 0, fontsize=8)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, fontsize=9)
    
    summary_text = (
        f" Total Net: {total_net/1e4:>6.2f}W\n"
        f" Win Rate : {win_rate:>6.2%}\n"
        f" Max DD   : {max_dd:>6.2%}\n"
        f" Sharpe   : {sharpe:>6.2f}"
    )
    ax1.text(0.98, 0.05, summary_text, transform=ax1.transAxes, 
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
             fontsize=10, family='monospace')
    
    chart_parts = []
    if DYNAMIC_ALPHA_MODE:
        chart_parts.append("ALPHA")
    if USE_MODEL_OFFSET:
        chart_parts.append("MODEL-OFFSET")
    if not chart_parts:
        chart_parts.append("NO-FILTER" if NO_FILTER_MODE else "FILTERED")
    mode_str = "+".join(chart_parts)
    ax1.set_title(f"Covered Call Strategy Performance vs {ETF_NAME}  [{mode_str}]", fontsize=14, fontweight='bold', pad=15)

    # ── MIDDLE PANEL ──────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    leg_labels = sorted(list(set(l['label'] for res in results for l in res['legs'])))
    palette = ["#1abc9c", "#3498db", "#9b59b6", "#34495e", "#f1c40f", "#e67e22"]
    bottom_pos = np.zeros(len(results))
    bottom_neg = np.zeros(len(results))
    
    for i, label in enumerate(leg_labels):
        vals = np.array([next((l['net_rmb'] for l in res['legs'] if l['label'] == label), 0.0) for res in results])
        pos_vals = np.where(vals > 0, vals, 0)
        neg_vals = np.where(vals < 0, vals, 0)
        ax2.bar(x, pos_vals, bottom=bottom_pos, color=palette[i % len(palette)], label=label, alpha=0.8)
        ax2.bar(x, neg_vals, bottom=bottom_neg, color=palette[i % len(palette)], alpha=0.8)
        bottom_pos += pos_vals
        bottom_neg += neg_vals

    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_ylabel("Leg Contribution (RMB)", fontsize=10, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(cycle_labels, rotation=45 if len(x) > 15 else 0, fontsize=8)
    ax2.legend(loc='upper right', frameon=True, fontsize=8, ncol=2)
    ax2.grid(True, axis='y', linestyle=':', alpha=0.5)
    ax2.set_title("Per-Leg Net P&L Contribution", fontsize=12, fontweight='bold')

    # ── BOTTOM PANEL ──────────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    ax3.fill_between(x, drawdown * 100, 0, color=COLOR_BAR_DN, alpha=0.3)
    ax3.plot(x, drawdown * 100, color=COLOR_BAR_DN, linewidth=1.5, alpha=0.7)
    ax3.set_ylabel("Drawdown (%)", fontsize=10, fontweight='bold')
    ax3.set_ylim(min(drawdown * 100) * 1.2 if len(drawdown) > 0 else -10, 1)
    ax3.grid(True, linestyle=':', alpha=0.5)
    ax3.set_title("Strategy Drawdown Profile", fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(cycle_labels, rotation=45 if len(x) > 15 else 0, fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    print(f"\n  Chart saved → {out_path}")


    return results


if __name__ == "__main__":
    # Handle command line arguments for ETF choice
    etf_choice = "300"
    NO_FILTER_MODE = "--no-filter" in sys.argv
    if "--with-put" in sys.argv:
        NO_PUT_MODE = False
    if "--no-skip-otm4" in sys.argv:
        SKIP_OTM4 = False
    if "--alpha" in sys.argv:
        DYNAMIC_ALPHA_MODE = True
    if "--model-offset" in sys.argv:
        USE_MODEL_OFFSET = True
    # Remove flags from argv before parsing ETF choice
    sys.argv = [a for a in sys.argv if a not in ["--no-filter", "--with-put", "--no-skip-otm4", "--alpha", "--model-offset"]]
    if len(sys.argv) > 1:
        etf_choice = sys.argv[1]
    
    select_underlying(etf_choice)
    
    # Redirect output to log file
    filter_suffix = "_nofilter" if NO_FILTER_MODE else ""
    put_suffix = "_withput" if not NO_PUT_MODE else ""
    otm4_suffix = "_noskipotm4" if not SKIP_OTM4 else ""
    alpha_suffix = "_alpha" if DYNAMIC_ALPHA_MODE else ""
    model_suffix = "_modeloffset" if USE_MODEL_OFFSET else ""
    log_file = f"backtest/backtest_cc_{ETF_NAME}{filter_suffix}{put_suffix}{otm4_suffix}{alpha_suffix}{model_suffix}.log"
    os.makedirs("backtest", exist_ok=True)
    f = open(log_file, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.stdout, f)
    
    inst, opt, etf = load_data()
    run_backtest(opt, etf)

