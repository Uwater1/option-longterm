"""
Backtest Engine — Shared infrastructure for Call and Put backtests
===================================================================
Provides data loading, cycle detection, IV computation, strike selection,
leg P&L calculation, 5m limit-order simulation, result aggregation, and plotting.

Usage: Called by backtest_covered_call.py (CallStrategy) or backtest_put.py (PutStrategy).
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
COMMISSION     = 2.0         # RMB per option leg
EXERCISE_COST  = 0.6         # RMB when WE exercise as buyer
ETF_SHARES     = 20_000      # equity leg (no cost modelled here)
NUM_CONTRACTS  = 1           # Default number of contracts to trade per leg
RISK_FREE      = 0.02        # annual risk-free rate for BS IV
IVR_HIGH       = 0.50        # IVR above this → go further OTM (offset 5)
IVR_LOW        = 0.10        # IVR below this → go closer OTM (offset 3)
IV_THRESHOLD   = 0.20        # Fallback ATM IV if calculation fails

# ── Underlying Config (Dynamic based on CLI) ─────────────────────────────────
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
    elif etf_choice == "588000":
        ETF_NAME = "588000ETF"
        PATH_INST = "./data/588000ETF_instruments.parquet"
        PATH_OPT  = "./data/588000ETF_historical_prices.parquet"
        PATH_ETF  = "./data/588000ETF_1d.parquet"
        PATH_IV_CACHE = "./data/30d_iv_cache_588000.parquet"
    elif etf_choice == "159915":
        ETF_NAME = "159915ETF"
        PATH_INST = "./data/159915ETF_instruments.parquet"
        PATH_OPT  = "./data/159915ETF_historical_prices.parquet"
        PATH_ETF  = "./data/159915ETF_1d.parquet"
        PATH_IV_CACHE = "./data/30d_iv_cache_159915.parquet"
    else:
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
        return 0.50
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

    # IMPORTANT: Only merge maturity_date and option_type from instruments.
    # The opt parquet already has daily-correct strike_price and contract_multiplier.
    inst_slim = inst[["order_book_id", "maturity_date", "option_type"]].drop_duplicates()
    opt = opt.merge(inst_slim, on="order_book_id", how="left")

    etf = etf.set_index("date").sort_index()

    # Calculate indicators
    if "close_adj" in etf.columns:
        close_for_ind = etf["close_adj"]
        high_for_ind = etf["high_adj"]
        low_for_ind = etf["low_adj"]
    else:
        close_for_ind = etf["close"]
        high_for_ind = etf["high"]
        low_for_ind = etf["low"]

    etf["rsi14"] = ta.rsi(close_for_ind, length=14)
    etf["sma20"] = ta.sma(close_for_ind, length=20)
    etf["ema20"] = ta.ema(close_for_ind, length=20)
    etf["sma50"] = ta.sma(close_for_ind, length=50)
    etf["atr20"] = ta.atr(high_for_ind, low_for_ind, close_for_ind, length=20)
    etf["roc10"] = ta.roc(close_for_ind, length=10)
    etf["roc20"] = ta.roc(close_for_ind, length=20)
    bb = ta.bbands(close_for_ind, length=20, std=2)
    if bb is not None:
        etf["bbu20"] = bb["BBU_20_2.0_2.0"]
        etf["bbl20"] = bb["BBL_20_2.0_2.0"]
    else:
        etf["bbu20"] = np.nan
        etf["bbl20"] = np.nan
    etf["vol20"] = close_for_ind.pct_change().rolling(20).std() * np.sqrt(252)
    etf["vol20_median"] = etf["vol20"].rolling(252).median()
    macd = ta.macd(close_for_ind)
    etf["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan

    # Tail risk indicators
    etf["skew_20"] = close_for_ind.pct_change().rolling(20).skew()
    etf["kurt_20"] = close_for_ind.pct_change().rolling(20).kurt()
    etf["vol10"] = close_for_ind.pct_change().rolling(10).std() * np.sqrt(252)
    etf["vol_accel"] = etf["vol10"] / etf["vol20"].rolling(60).mean()
    etf["dd_252"] = (close_for_ind - close_for_ind.rolling(252).max()) / close_for_ind.rolling(252).max()
    etf["sma200"] = ta.sma(close_for_ind, length=200)
    etf["dist_sma200"] = (close_for_ind - etf["sma200"]) / etf["atr20"]
    etf["dist_sma50"] = (close_for_ind - etf["sma50"]) / etf["atr20"]

    # Load 30d IV if cache exists
    if os.path.exists(PATH_IV_CACHE):
        daily_ivs = pd.read_parquet(PATH_IV_CACHE).iloc[:, 0]
        daily_ivs.index = pd.to_datetime(daily_ivs.index)
        etf["iv"] = daily_ivs.reindex(etf.index).ffill()
        etf["iv_vol_ratio"] = etf["iv"] / etf["vol20"]
    else:
        etf["iv"] = np.nan
        etf["iv_vol_ratio"] = np.nan

    return inst, opt, etf


# ── Cycle detection ───────────────────────────────────────────────────────────
def get_cycles(opt, etf):
    """Return a list of dicts with entry_date and expiry_date per monthly cycle."""
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt["date"].unique())

    expiries_cp = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()
        .index.tolist()
    )
    expiries_cp = sorted(expiries_cp)

    cycles = []
    for i, expiry in enumerate(expiries_cp):
        if i == 0:
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]
        if entry >= expiry:
            continue
        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue
        cycles.append({"entry_date": entry, "expiry_date": expiry})
    return cycles


# ── ATM IV on a given date ────────────────────────────────────────────────────
def get_atm_iv(opt, etf, entry_date, expiry_date):
    """Find ATM call IV for given expiry on entry date."""
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
    day_opt["dist"] = (day_opt["strike_price"] - etf_close).abs()
    row = day_opt.loc[day_opt["dist"].idxmin()]
    return compute_iv(float(row["close"]), float(etf_close),
                      float(row["strike_price"]), T, RISK_FREE, True)


def get_30d_iv(opt, etf, date):
    """Estimate 30-day interpolated ATM IV for a given date."""
    date_norm = date.normalize()
    if date_norm not in etf.index:
        return IV_THRESHOLD
    etf_close = float(etf.loc[date_norm, "close"])

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

    expiries = sorted(day_calls["maturity_date"].unique())
    iv_by_expiry = {}
    for exp in expiries:
        exp_opts = day_calls[day_calls["maturity_date"] == exp].copy()
        exp_opts["dist"] = (exp_opts["strike_price"] - etf_close).abs()
        row = exp_opts.loc[exp_opts["dist"].idxmin()]
        dte = (exp - date).days
        T = max(dte, 1) / 365.0
        iv = compute_iv(float(row["close"]), float(etf_close),
                        float(row["strike_price"]), T, RISK_FREE, True)
        iv_by_expiry[dte] = iv

    dtes = sorted(iv_by_expiry.keys())
    if not dtes:
        return IV_THRESHOLD
    t1_candidates = [d for d in dtes if d <= 30]
    t2_candidates = [d for d in dtes if d > 30]
    if t1_candidates and t2_candidates:
        t1 = t1_candidates[-1]
        t2 = t2_candidates[0]
        v1 = iv_by_expiry[t1]**2
        v2 = iv_by_expiry[t2]**2
        v30 = (v1 * (t2 - 30) + v2 * (30 - t1)) / (t2 - t1)
        return math.sqrt(max(0, v30))
    elif t1_candidates:
        return iv_by_expiry[t1_candidates[-1]]
    elif t2_candidates:
        return iv_by_expiry[t2_candidates[0]]
    return IV_THRESHOLD


# ── OTM strike selector ───────────────────────────────────────────────────────
def get_otm_strikes(opt, etf, entry_date, expiry_date, option_type, offsets):
    """Select contracts for given OTM offsets (1-indexed). Returns list of dicts or None."""
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
        otm = day_opt[day_opt["strike_price"] > etf_close].sort_values("strike_price")
    else:
        otm = day_opt[day_opt["strike_price"] < etf_close].sort_values(
            "strike_price", ascending=False)
    results = []
    for off in offsets:
        idx = off - 1
        if idx < len(otm):
            results.append(otm.iloc[idx].to_dict())
        else:
            results.append(None)
    return results


def get_strike_by_level(opt, etf, entry_date, expiry_date, option_type, level):
    """Select strike by level: 0=closest ITM-ish, 1=closest OTM, etc."""
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
        if level == 0:
            candidates = day_opt[day_opt["strike_price"] >= etf_close].sort_values("strike_price", ascending=True)
            idx = 0
        else:
            candidates = day_opt[day_opt["strike_price"] < etf_close].sort_values("strike_price", ascending=False)
            idx = level - 1
    if idx >= 0 and idx < len(candidates):
        return candidates.iloc[idx].to_dict()
    return None


# ── Model offset helpers ─────────────────────────────────────────────────────
_model_meta = None
_feature_cache = {}

def _load_model_offset():
    """Load the trained open-high model for limit order offset prediction."""
    global _model_meta
    if _model_meta is not None:
        return _model_meta
    try:
        from predict_open_high import load_model, load_and_engineer, predict_single
        etf_key = {"50ETF": "50", "300ETF": "300", "500ETF": "500", "588000ETF": "588000", "159915ETF": "159915"}.get(ETF_NAME, "300")
        _model_meta = load_model(etf_key)
        _model_meta["_predict_fn"] = predict_single
        _model_meta["_engineer_fn"] = load_and_engineer
        print(f"  Loaded open-high model: {_model_meta['features']}, "
              f"coverage={_model_meta['rolling_coverage']:.1f}%")
        return _model_meta
    except Exception as e:
        print(f"  WARNING: Could not load open-high model: {e}")
        return None


def _predict_model_offset(etf_df, entry_date):
    """Predict the P10 offset fraction for a given entry date. Returns >= 0.0 or None."""
    meta = _load_model_offset()
    if meta is None:
        return None
    try:
        etf_key = {"50ETF": "50", "300ETF": "300", "500ETF": "500", "588000ETF": "588000", "159915ETF": "159915"}.get(ETF_NAME, "300")
        if etf_key not in _feature_cache:
            _feature_cache[etf_key] = meta["_engineer_fn"](etf_key)
            _feature_cache[etf_key]["_dates_parsed"] = pd.to_datetime(_feature_cache[etf_key]["date"])
        df = _feature_cache[etf_key]
        df_dates = df["_dates_parsed"]
        entry_ts = pd.to_datetime(entry_date)
        mask = (df_dates - entry_ts).abs() < pd.Timedelta(days=1)
        if not mask.any():
            return None
        row = df[mask].iloc[[-1]]
        current_vol = float(row["vol20"].values[0]) if "vol20" in row.columns else None
        p10_pct = meta["_predict_fn"](meta, row, current_vol20=current_vol)
        return max(0.0, p10_pct / 100.0)
    except Exception:
        return None


# ── Per-leg P&L ───────────────────────────────────────────────────────────────
def calc_leg_pnl(leg, opt, etf, expiry_date, side, is_buyer_at_expiry,
                 sell_spread=None, override_exec_px=None):
    """
    Compute full P&L (RMB) for a single option leg.
    Returns dict with entry_mid, exec_px, K, mult, side, premium_rmb,
    exercise_pnl_rmb, commission_rmb, exercise_cost_rmb, net_rmb, note.
    """
    if leg is None:
        return None

    K          = float(leg["strike_price"])
    mult       = float(leg["contract_multiplier"])
    entry_mid  = float(leg["close"])
    otype      = leg["option_type"]
    contract   = str(leg.get("order_book_id", ""))
    if contract.endswith(".0"):
        contract = contract[:-2]

    # Execution price
    if override_exec_px is not None:
        exec_px = override_exec_px
    elif sell_spread is not None and side == "sell":
        exec_px = entry_mid   # limit order: sell at mid
    elif side == "sell":
        exec_px = entry_mid * (1 - SPREAD_HALF)
    else:
        exec_px = entry_mid * (1 + SPREAD_HALF)

    premium_rmb = exec_px * mult if side == "sell" else -exec_px * mult

    # Settlement
    etf_expiry_dates = etf.index[etf.index <= expiry_date]
    etf_settle = float(etf.loc[etf_expiry_dates[-1], "close"]) if not etf_expiry_dates.empty else None

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
                exercise_pnl_rmb  = -intrinsic * mult
                exercise_cost_rmb = 0.0
                note = f"assigned  ETF={etf_settle:.4f} K={K:.4f}"
            else:
                exercise_pnl_rmb  = intrinsic * mult
                exercise_cost_rmb = EXERCISE_COST
                note = f"exercised ETF={etf_settle:.4f} K={K:.4f}"

    commission_rmb = COMMISSION
    net_rmb = premium_rmb + exercise_pnl_rmb - commission_rmb - exercise_cost_rmb

    return {
        "entry_mid": entry_mid, "exec_px": exec_px, "K": K,
        "mult": mult, "otype": otype, "contract": contract, "side": side,
        "premium_rmb": premium_rmb, "exercise_pnl_rmb": exercise_pnl_rmb,
        "commission_rmb": commission_rmb, "exercise_cost_rmb": exercise_cost_rmb,
        "net_rmb": net_rmb, "note": note,
    }


# ── 5m Limit Order Simulation ─────────────────────────────────────────────────
def simulate_limit_order(leg, side, entry, expiry, etf, opt_5m, etf_5m,
                         predict_limit_fn, etf_close_entry):
    """
    Generic 5m limit order simulation.
    For sell: check if high >= limit_price → filled
    For buy:  check if low  <= limit_price → filled
    Returns: dict with filled (bool), limit_px, exec_px, or None entries.
    """
    if opt_5m is None or etf_5m is None or predict_limit_fn is None:
        return {"filled": None, "limit_px": None, "exec_px": None, "override_px": None}

    try:
        trading_days = list(etf.index.unique())
        entry_norm = entry.normalize()
        entry_idx = trading_days.index(entry_norm)
        window_days = trading_days[entry_idx : entry_idx + 2]

        order_book_id = leg["order_book_id"]
        contract_5m = opt_5m[
            (opt_5m["order_book_id"] == order_book_id) &
            (opt_5m["datetime"].dt.normalize().isin(window_days))
        ].sort_values("datetime")

        contract_5m = contract_5m[
            (contract_5m["open"] > 0) & (contract_5m["high"] > 0) &
            (contract_5m["low"] > 0) & (contract_5m["close"] > 0)
        ].sort_values("datetime")

        if contract_5m.empty:
            return {"filled": None, "limit_px": None, "exec_px": None, "override_px": None}

        P_open = contract_5m.iloc[0]["open"]
        strike = float(leg["strike_price"])
        etf_entry_5m = etf_5m[etf_5m["datetime"].dt.normalize() == entry_norm].sort_values("datetime")
        etf_open = float(etf_entry_5m.iloc[0]["open"]) if not etf_entry_5m.empty else float(etf_close_entry)

        dte = (expiry - entry).days
        T = max(dte, 1) / 365.0

        limit_px = predict_limit_fn(etf, entry, etf_open, strike, T, P_open)
        if limit_px is None or limit_px <= 0:
            return {"filled": None, "limit_px": None, "exec_px": None, "override_px": None}

        if side == "sell":
            fill_bars = contract_5m[contract_5m["high"] >= limit_px]
        else:  # buy
            fill_bars = contract_5m[contract_5m["low"] <= limit_px]

        if not fill_bars.empty:
            return {"filled": True, "limit_px": limit_px, "exec_px": limit_px, "override_px": limit_px}
        else:
            fallback_px = contract_5m.iloc[-1]["close"]
            return {"filled": False, "limit_px": limit_px, "exec_px": fallback_px, "override_px": fallback_px}
    except Exception as e:
        print(f"  WARNING: Error in limit order simulation: {e}")
        return {"filled": None, "limit_px": None, "exec_px": None, "override_px": None}


# ── Main backtest runner ─────────────────────────────────────────────────────
def run_backtest(strategy, opt, etf):
    """
    Main backtest loop. Delegates to strategy for filter evaluation,
    leg selection, and limit order computation.
    """
    # Load or compute 30d IV cache
    if os.path.exists(PATH_IV_CACHE):
        print(f"\nLoading pre-calculated 30-day IVs from {PATH_IV_CACHE}...")
        daily_ivs = pd.read_parquet(PATH_IV_CACHE).iloc[:, 0]
        daily_ivs.index = pd.to_datetime(daily_ivs.index)
    else:
        print("\nPre-calculating daily 30-day IVs...")
        trading_days = sorted(etf.index.unique())
        day_calls_dict = {d: group for d, group in
                          opt[(opt["option_type"] == "C") & (opt["close"] > 0)].groupby("date")}
        iv_data = {}
        for i, d in enumerate(trading_days):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(trading_days)}")
            iv_data[d] = get_30d_iv(day_calls_dict, etf, d)
        daily_ivs = pd.Series(iv_data).sort_index()
        os.makedirs(os.path.dirname(PATH_IV_CACHE), exist_ok=True)
        daily_ivs.to_frame("iv").to_parquet(PATH_IV_CACHE)
        print(f"  Saved IV cache to {PATH_IV_CACHE}")

    etf["iv"] = daily_ivs.reindex(etf.index).ffill()
    etf["iv_vol_ratio"] = etf["iv"] / etf["vol20"]

    # Load 5m data if strategy needs it
    opt_5m, etf_5m = None, None
    if strategy.needs_5m():
        opt_5m_path = {"50ETF": "./data/50ETF_historical_prices_5m.parquet",
                       "300ETF": "./data/300ETF_historical_prices_5m.parquet",
                       "500ETF": "./data/500ETF_historical_prices_5m.parquet",
                       "588000ETF": "./data/588000ETF_historical_prices_5m.parquet",
                       "159915ETF": "./data/159915ETF_historical_prices_5m.parquet"}.get(ETF_NAME)
        etf_5m_path = {"50ETF": "./data/50ETF_5m.parquet",
                       "300ETF": "./data/510300_5m.parquet",
                       "500ETF": "./data/500ETF_5m.parquet",
                       "588000ETF": "./data/588000ETF_5m.parquet",
                       "159915ETF": "./data/159915ETF_5m.parquet"}.get(ETF_NAME)
        if opt_5m_path and os.path.exists(opt_5m_path):
            print(f"Loading 5m option data from {opt_5m_path}...")
            opt_5m = pd.read_parquet(opt_5m_path)
            opt_5m["datetime"] = pd.to_datetime(opt_5m["datetime"])
            print(f"Loading 5m ETF data from {etf_5m_path}...")
            etf_5m = pd.read_parquet(etf_5m_path)
            etf_5m["datetime"] = pd.to_datetime(etf_5m["datetime"])
        else:
            print("  WARNING: 5m data not found, limit order simulation disabled.")

    cycles = get_cycles(opt, etf)
    results = []
    for cyc in cycles:
        res = _execute_cycle(strategy, cyc, opt, etf, daily_ivs, opt_5m, etf_5m)
        results.append(res)

    # ── Per-cycle detail printout ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"  {strategy.name} BACKTEST — Cycle Detail  [{strategy.mode_label()}]")
    print("=" * 70)
    for res in results:
        print(strategy.format_cycle(res))
        hdr = f"  {'Leg':<25} {'side':>4} {'K':>7} {'exec_px':>8} {'prem':>8}  {'exer':>9}  {'net':>8}"
        print(hdr)
        print("  " + "-" * (len(hdr) - 2))
        for r in res["legs"]:
            print(f"  {r['label']:<25} {r['side']:>4} {r['K']:>7.3f}"
                  f" {r['exec_px']:>8.4f} {r['premium_rmb']:>8.2f}"
                  f"  {r['exercise_pnl_rmb']:>9.2f}  {r['net_rmb']:>8.2f}"
                  f"  [{r['note']}]")
        print(f"  {'CYCLE TOTAL':>49}  {res['total_net_rmb']:>8.2f}")

    # ── Aggregate summary ─────────────────────────────────────────────────
    _print_summary(strategy, results)

    # ── Chart & CSV ───────────────────────────────────────────────────────
    os.makedirs("backtest", exist_ok=True)
    suffix = strategy.file_suffix()
    out_png = f"backtest/backtest_{suffix}.png"
    plot_backtest_results(results, etf, out_png, strategy)
    out_csv = f"backtest/backtest_{suffix}.csv"
    save_csv(results, out_csv, strategy)

    return results


def _execute_cycle(strategy, cyc, opt, etf, daily_ivs, opt_5m, etf_5m):
    """Execute a single backtest cycle using the strategy."""
    entry  = cyc["entry_date"]
    expiry = cyc["expiry_date"]
    idx = entry.normalize()

    iv = daily_ivs.get(entry, IV_THRESHOLD)

    # IV Rank (252-day lookback)
    history = daily_ivs[daily_ivs.index <= entry]
    if len(history) >= 20:
        lookback = history.tail(252)
        min_iv, max_iv = lookback.min(), lookback.max()
        ivr = (iv - min_iv) / (max_iv - min_iv) if max_iv > min_iv else 0.5
    else:
        ivr = 0.5

    # Gather indicators
    etf_close_entry = float(etf.loc[idx, "close"])
    etf_close_entry_for_filter = float(etf.loc[idx, "close_adj"]) if "close_adj" in etf.columns else etf_close_entry
    indicators = {
        "rsi": etf.loc[idx, "rsi14"],
        "bbu": etf.loc[idx, "bbu20"],
        "bbl": etf.loc[idx, "bbl20"],
        "sma20": etf.loc[idx, "sma20"],
        "sma50": etf.loc[idx, "sma50"],
        "atr20": etf.loc[idx, "atr20"],
        "roc10": etf.loc[idx, "roc10"],
        "roc20": etf.loc[idx, "roc20"],
        "vol20": etf.loc[idx, "vol20"],
        "vol20_median": etf.loc[idx, "vol20_median"],
        "macd_hist": etf.loc[idx, "macd_hist"],
        "skew_20": etf.loc[idx, "skew_20"],
        "kurt_20": etf.loc[idx, "kurt_20"],
        "vol_accel": etf.loc[idx, "vol_accel"],
        "dd_252": etf.loc[idx, "dd_252"],
        "dist_sma200": etf.loc[idx, "dist_sma200"],
        "dist_sma50": etf.loc[idx, "dist_sma50"],
        "iv_vol_ratio": etf.loc[idx, "iv_vol_ratio"],
    }

    # 1. Evaluate filter
    filter_passed, filter_would_pass = strategy.evaluate_filter(
        etf, idx, etf_close_entry_for_filter, indicators)

    # 2. Select legs
    legs_to_process = strategy.select_legs(
        opt, etf, entry, expiry, filter_passed, indicators, iv, ivr)

    # 3. Execute legs with optional limit orders
    num_contracts = NUM_CONTRACTS
    model_spread = strategy.get_model_spread(etf, entry) if filter_passed else None

    leg_results = []
    limit_details = {}

    for leg, side, label in legs_to_process:
        override_px = None
        # Strategy-specific limit order simulation
        if strategy.use_limit_order(side):
            predict_fn = strategy.get_predict_limit_fn(side)
            sim_result = simulate_limit_order(
                leg, side, entry, expiry, etf, opt_5m, etf_5m,
                predict_fn, etf_close_entry)
            override_px = sim_result["override_px"]
            # Track limit order details
            if side == "sell":
                limit_details.setdefault("call_limit_results", []).append({
                    "filled": sim_result["filled"],
                    "limit_px": sim_result["limit_px"],
                    "exec_px": sim_result["exec_px"],
                })
            else:
                limit_details["put_filled"] = sim_result["filled"]
                limit_details["put_limit_px"] = sim_result["limit_px"]
                limit_details["put_exec_px"] = sim_result["exec_px"]

        res = calc_leg_pnl(leg, opt, etf, expiry, side, side == "buy",
                           sell_spread=model_spread if side == "sell" else None,
                           override_exec_px=override_px)
        if res is not None:
            res["premium_rmb"] *= num_contracts
            res["exercise_pnl_rmb"] *= num_contracts
            res["commission_rmb"] *= num_contracts
            res["exercise_cost_rmb"] *= num_contracts
            res["net_rmb"] *= num_contracts
            res["mult"] *= num_contracts
            res["label"] = label
            leg_results.append(res)

    total_net = sum(r["net_rmb"] for r in leg_results)
    total_premium = sum(r["premium_rmb"] for r in leg_results)

    # Build call/put offset lists for logging
    call_offsets = []
    put_offsets = []
    for _leg, side, label in legs_to_process:
        # Extract offset number from label
        import re
        m = re.search(r'OTM(\d+)', label)
        if m:
            if side == "sell":
                call_offsets.append(int(m.group(1)))
        m2 = re.search(r'Level\s*(\d+)', label)
        if m2:
            put_offsets.append(int(m2.group(1)))

    return {
        "entry_date": entry, "expiry_date": expiry,
        "iv": iv, "ivr": ivr,
        "rsi": indicators["rsi"], "bbu": indicators["bbu"],
        "filter_passed": filter_passed,
        "filter_would_pass": filter_would_pass,
        "call_offsets": call_offsets,
        "put_offsets": put_offsets,
        "num_contracts": num_contracts,
        "etf_entry": etf_close_entry,
        "legs": leg_results,
        "total_premium": total_premium,
        "total_net_rmb": total_net,
        "put_filled": limit_details.get("put_filled"),
        "put_fill_time": None,
        "put_exec_px": limit_details.get("put_exec_px"),
        "put_limit_px": limit_details.get("put_limit_px"),
        "put_trigger_val": None,
        "call_limit_results": limit_details.get("call_limit_results", []),
    }


def _print_summary(strategy, results):
    """Print aggregate summary with placement rate and filter lift."""
    nets = [r["total_net_rmb"] for r in results]
    premiums = [r["total_premium"] for r in results]
    cumulative = list(np.cumsum(nets))
    total_net = sum(nets)
    win_rate = sum(1 for n in nets if n > 0) / len(nets) if nets else 0
    avg_prem = np.mean(premiums) if premiums else 0

    n_cycles = len(results)
    n_placed = sum(1 for r in results if r["filter_would_pass"])
    placement_rate = n_placed / n_cycles if n_cycles > 0 else 0.0
    placed_pnls = [r["total_net_rmb"] for r in results if r["filter_would_pass"]]
    avg_pnl_placed = np.mean(placed_pnls) if placed_pnls else 0.0
    avg_pnl_all = np.mean(nets) if nets else 0.0
    filter_lift = avg_pnl_placed - avg_pnl_all

    print("\n" + "=" * 70)
    print(f"  SUMMARY  [{strategy.mode_label()}]")
    print("=" * 70)
    print(f"  Cycles traded          : {n_cycles}")
    print(f"  Winning cycles         : {sum(1 for n in nets if n > 0)}/{n_cycles}"
          f"  ({win_rate:.0%})")
    print(f"  Avg gross premium/cyc  : {avg_prem:>8.2f} RMB")
    print(f"  Total net P&L          : {total_net:>8.2f} RMB")

    # Put limit fill rate
    put_fills = [r["put_filled"] for r in results if r.get("put_filled") is not None]
    if put_fills:
        fill_rate = sum(1 for f in put_fills if f) / len(put_fills)
        print(f"  Put limit fill rate    : {fill_rate:.1%} ({sum(1 for f in put_fills if f)}/{len(put_fills)} cycles)")

    # Call limit fill rate
    all_call_limits = []
    for r in results:
        all_call_limits.extend(r.get("call_limit_results", []))
    call_with_5m = [c for c in all_call_limits if c.get("filled") is not None]
    if call_with_5m:
        call_fill_rate = sum(1 for c in call_with_5m if c["filled"]) / len(call_with_5m)
        print(f"  Call limit fill rate   : {call_fill_rate:.1%} ({sum(1 for c in call_with_5m if c['filled'])}/{len(call_with_5m)} legs)")

    print(f"  Cumulative by cycle    : {[f'{v:.0f}' for v in cumulative]}")
    print(f"  ── Placement & Filter Lift ─────────────────────────────────────")
    print(f"  Placement rate         : {placement_rate:.1%}  ({n_placed}/{n_cycles} cycles)")
    print(f"  Avg P&L / placed cycle : {avg_pnl_placed:>+8.2f} RMB")
    print(f"  Avg P&L / all cycles   : {avg_pnl_all:>+8.2f} RMB")
    print(f"  Filter lift            : {filter_lift:>+8.2f} RMB/cycle")
    print(f"  ─────────────────────────────────────────────────────────────")

    # No-filter blocked cycle analysis
    if strategy.is_no_filter_mode():
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
            for r in blocked:
                tag = "WIN" if r['total_net_rmb'] > 0 else "LOSS"
                print(f"    {r['entry_date'].date()} → {r['expiry_date'].date()}  "
                      f"RSI={r['rsi']:.1f}  ETF={r['etf_entry']:.4f}  "
                      f"P&L={r['total_net_rmb']:>+10.2f}  [{tag}]")
        print(f"  ─────────────────────────────────────────────────────────────")


# ── CSV export ─────────────────────────────────────────────────────────────────
def save_csv(results, csv_path, strategy):
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
        if r.get("put_filled") is not None:
            row["put_filled"] = r["put_filled"]
            row["put_exec_px"] = round(r["put_exec_px"], 4) if r["put_exec_px"] else ""
            row["put_limit_px"] = round(r["put_limit_px"], 4) if r["put_limit_px"] else ""
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


# ── Plotting ──────────────────────────────────────────────────────────────────
def plot_backtest_results(results, etf, out_path, strategy):
    """Plot P&L, leg contribution, and drawdown."""
    dates = [r['expiry_date'] for r in results]
    nets = [r['total_net_rmb'] for r in results]
    cumulative = np.cumsum(nets)
    peaks = np.maximum.accumulate(cumulative)
    drawdown = np.zeros_like(cumulative, dtype=float)
    peak_mask = peaks > 0
    drawdown[peak_mask] = (cumulative[peak_mask] - peaks[peak_mask]) / peaks[peak_mask]
    max_dd = np.min(drawdown) if len(drawdown) > 0 else 0

    etf_sub = etf.reindex(dates, method='ffill')['close']
    etf_norm = (etf_sub / etf_sub.iloc[0] - 1) * 100

    total_net = cumulative[-1]
    win_rate = sum(1 for n in nets if n > 0) / len(results) if results else 0
    sharpe = np.sqrt(12) * np.mean(nets) / np.std(nets) if len(nets) > 1 and np.std(nets) > 0 else 0

    try:
        plt.style.use('seaborn-v0_8-muted')
    except:
        plt.style.use('ggplot')

    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 3, 2], hspace=0.3)

    COLOR_CUM, COLOR_BAR_UP, COLOR_BAR_DN, COLOR_ETF = "#2980b9", "#27ae60", "#e74c3c", "#f39c12"

    # TOP PANEL
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
    summary_text = (f" Total Net: {total_net/1e4:>6.2f}W\n"
                    f" Win Rate : {win_rate:>6.2%}\n"
                    f" Max DD   : {max_dd:>6.2%}\n"
                    f" Sharpe   : {sharpe:>6.2f}")
    ax1.text(0.98, 0.05, summary_text, transform=ax1.transAxes,
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
             fontsize=10, family='monospace')
    ax1.set_title(f"{strategy.name} Performance vs {ETF_NAME}  [{strategy.mode_label()}]",
                  fontsize=14, fontweight='bold', pad=15)

    # MIDDLE PANEL
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

    # BOTTOM PANEL
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
