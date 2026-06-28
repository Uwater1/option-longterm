"""Backtest engine: per-day 5m simulation.

For each ETF:
  1) Load signals (date, direction) from rules.get_signals
  2) Load 5m bars, group by trading day (48 bars expected)
  3) For each signal day:
       entry_price = close of decision bar (per ETF)
       exit_price  = close of EXIT_BAR (14:30)
       gross_ret   = direction * (exit/entry - 1)
       net_ret     = gross_ret - COST_BPS/1e4
  4) Aggregate to per-day returns aligned to the full calendar.

Output: per-ETF metrics dict + per-day P&L DataFrame.
"""
from __future__ import annotations

from typing import Optional

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from pathlib import Path

from . import (
    ETFS, DECISION_BAR, EXIT_BAR, DEFAULT_COST_BPS,
    ETF_5M_DIR, HOLDOUT_START,
)
from .rules import get_signals, get_long_short_signals


# 300ETF's 5m file uses the underlying ETF code
ETF_5M_FILE = {
    "50ETF": "50ETF_5m.parquet",
    "300ETF": "510300_5m.parquet",
    "500ETF": "500ETF_5m.parquet",
    "588000ETF": "588000ETF_5m.parquet",
    "159915ETF": "159915ETF_5m.parquet",
}


_5M_CACHE = {}
_GROUPED_BARS_CACHE = {}
_ATR_CACHE = {}
_DAY_TABLE_CACHE = {}

# Maximum exit bar supported by the precomputed DayTable (covers EXIT_BAR_GRID + headroom)
_MAX_EXIT_BAR_SUPPORTED = 47


def load_5m(etf: str) -> pd.DataFrame:
    """Load 5m bars; return DataFrame indexed by datetime with [open, high, low, close, volume]."""
    if etf in _5M_CACHE:
        return _5M_CACHE[etf]
    path = ETF_5M_DIR / ETF_5M_FILE[etf]
    df = pd.read_parquet(path)
    df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    # Cast to float32 to save memory and speed up numeric checks
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(np.float32)
    _5M_CACHE[etf] = df
    return df


def get_grouped_bars(etf: str) -> dict:
    if etf in _GROUPED_BARS_CACHE:
        return _GROUPED_BARS_CACHE[etf]
    bars = load_5m(etf)
    bars["date"] = bars.index.date
    grouped = {}
    for d, g in bars.groupby("date"):
        grouped[d] = {
            "open": g["open"].values,
            "high": g["high"].values,
            "low": g["low"].values,
            "close": g["close"].values,
        }
    _GROUPED_BARS_CACHE[etf] = grouped
    return grouped


def compute_daily_atr14(bars: pd.DataFrame, window: int = 14) -> pd.Series:
    """Compute rolling 14-day ATR from 5m bars.

    Uses daily high-low range (proxy for True Range when prev-close is unavailable)
    and takes a rolling mean over ``window`` prior trading days.
    Returns a Series indexed by date (datetime.date).
    """
    bars = bars.copy()
    bars["date"] = bars.index.date
    daily = bars.groupby("date").agg(hi=("high", "max"), lo=("low", "min"))
    daily["tr"] = daily["hi"] - daily["lo"]
    daily["atr14"] = daily["tr"].rolling(window=window, min_periods=1).mean()
    # Use prior day's ATR to avoid look-ahead
    daily["atr14"] = daily["atr14"].shift(1)
    return daily["atr14"]


def get_daily_atr14(etf: str) -> pd.Series:
    if etf in _ATR_CACHE:
        return _ATR_CACHE[etf]
    bars = load_5m(etf)
    atr = compute_daily_atr14(bars)
    _ATR_CACHE[etf] = atr
    return atr


def _build_day_table(etf: str) -> dict:
    """Per-ETF dense table of intraday bar slices for vectorized simulation.

    Once built, any (stop_type, stop_val, exit_bar) combo can be replayed as
    pure NumPy row-wise ops — no per-day Python loop.

    Layout (all arrays aligned by positional day index ``i``):
        entry_price[i]      = open[decision_bar + 1]
        struct_low[i]       = min(low[0 .. decision_bar])
        struct_high[i]      = max(high[0 .. decision_bar])
        low_scan[i, :]      = low[entry_idx .. max_exit_bar]  (fp32)
        high_scan[i, :]     = high[entry_idx .. max_exit_bar] (fp32)
        close_by_bar[i, b]  = close[b] for b in [0 .. max_exit_bar]
        valid[i]            = day has enough bars AND entry_price > 0
        atr_at[i]           = ATR14 for that day (NaN if missing)
        atr_fallback_max[i] = max of prior non-NaN ATR values (NaN if none)
    """
    if etf in _DAY_TABLE_CACHE:
        return _DAY_TABLE_CACHE[etf]

    decision_bar = DECISION_BAR[etf]
    max_exit_bar = _MAX_EXIT_BAR_SUPPORTED
    entry_idx = decision_bar + 1
    scan_len = max_exit_bar - entry_idx + 1

    grouped = get_grouped_bars(etf)
    dates = sorted(grouped.keys())
    n_days = len(dates)

    entry_price = np.full(n_days, np.nan, dtype=np.float64)
    struct_low = np.full(n_days, np.nan, dtype=np.float64)
    struct_high = np.full(n_days, np.nan, dtype=np.float64)
    low_scan = np.full((n_days, scan_len), np.nan, dtype=np.float32)
    high_scan = np.full((n_days, scan_len), np.nan, dtype=np.float32)
    close_by_bar = np.full((n_days, max_exit_bar + 1), np.nan, dtype=np.float32)
    valid = np.zeros(n_days, dtype=bool)

    for i, d in enumerate(dates):
        day = grouped[d]
        open_arr = day["open"]; high_arr = day["high"]
        low_arr = day["low"]; close_arr = day["close"]
        L = len(open_arr)
        # Need bars up to max_exit_bar; otherwise this day can never be simulated
        if L <= max_exit_bar or entry_idx >= L:
            continue
        ep = float(open_arr[entry_idx])
        if ep <= 0:
            continue
        entry_price[i] = ep
        struct_low[i] = float(np.min(low_arr[:entry_idx]))
        struct_high[i] = float(np.max(high_arr[:entry_idx]))
        low_scan[i] = low_arr[entry_idx:max_exit_bar + 1]
        high_scan[i] = high_arr[entry_idx:max_exit_bar + 1]
        close_by_bar[i] = close_arr[:max_exit_bar + 1]
        valid[i] = True

    # ATR14 per day; compute fallback (max of prior non-NaN values) for the
    # missing-value branch in the legacy _day_bars_to_series code path.
    atr = get_daily_atr14(etf)
    atr_at = np.full(n_days, np.nan, dtype=np.float64)
    for i, d in enumerate(dates):
        if d in atr.index:
            v = atr[d]
            if v is not None and not np.isnan(v):
                atr_at[i] = float(v)

    filled = np.where(np.isnan(atr_at), -np.inf, atr_at)
    atr_fallback_max = np.full(n_days, np.nan, dtype=np.float64)
    if n_days > 1:
        cummax = np.maximum.accumulate(filled[:-1])
        atr_fallback_max[1:] = np.where(np.isneginf(cummax), np.nan, cummax)

    table = dict(
        decision_bar=decision_bar, max_exit_bar=max_exit_bar,
        entry_idx=entry_idx, scan_len=scan_len,
        dates=dates,
        date_to_pos={d: i for i, d in enumerate(dates)},
        entry_price=entry_price, struct_low=struct_low, struct_high=struct_high,
        low_scan=low_scan, high_scan=high_scan, close_by_bar=close_by_bar,
        valid=valid, atr_at=atr_at, atr_fallback_max=atr_fallback_max,
    )
    _DAY_TABLE_CACHE[etf] = table
    return table


def _simulate_trades_vectorized(
    etf: str,
    signals: pd.DataFrame,
    eff_stop_type: Optional[str],
    eff_stop_val: Optional[float],
    eff_exit_bar: int,
    cost_bps: float,
) -> pd.DataFrame:
    """Vectorized trade simulation. Behavioural equivalent of the legacy
    per-day ``_day_bars_to_series`` loop, but runs as NumPy row-wise ops
    over the precomputed ``_DAY_TABLE_CACHE[etf]`` slices.

    Returns a trades DataFrame with the same columns / index as the legacy
    path. Empty DataFrame if no tradeable signal days.
    """
    if len(signals) == 0:
        return pd.DataFrame()

    table = _build_day_table(etf)
    if eff_exit_bar > table["max_exit_bar"]:
        # Out of supported range — caller should have caught this; defensive.
        return _simulate_trades_legacy(etf, signals, eff_stop_type, eff_stop_val, eff_exit_bar, cost_bps)

    date_to_pos = table["date_to_pos"]
    sig_index = signals.index
    sig_date_objs = sig_index.date
    positions = np.array([date_to_pos.get(d, -1) for d in sig_date_objs], dtype=np.int64)

    # Keep only days that exist in the day_table AND pass the valid flag AND
    # have a strictly-positive close at the requested exit_bar.
    keep = positions >= 0
    if not np.all(keep):
        positions = positions[keep]
        sig_date_objs = sig_date_objs[keep]
        signals = signals.iloc[keep]

    table_valid = table["valid"][positions]
    close_at_exit = table["close_by_bar"][positions, eff_exit_bar]
    keep2 = table_valid & (close_at_exit > 0)
    if not np.all(keep2):
        positions = positions[keep2]
        sig_date_objs = sig_date_objs[keep2]
        signals = signals.iloc[keep2]
        close_at_exit = close_at_exit[keep2]

    n = len(positions)
    if n == 0:
        return pd.DataFrame()

    entry_idx = table["entry_idx"]
    scan_len = eff_exit_bar - entry_idx + 1
    direction = signals["direction"].values.astype(np.int8)
    is_long = direction > 0
    is_short = ~is_long

    entry_price = table["entry_price"][positions]
    exit_price = close_at_exit.astype(np.float64).copy()
    hit_mask = np.zeros(n, dtype=bool)

    # Score columns (mirror the legacy .get(...) fallbacks)
    cols = signals.columns
    if "fired_score" in cols:
        score_arr = signals["fired_score"].values.astype(np.float64)
    elif "score" in cols:
        score_arr = signals["score"].values.astype(np.float64)
    else:
        score_arr = np.full(n, np.nan)
    long_score_arr = (signals["long_score"].values.astype(np.float64)
                      if "long_score" in cols else np.full(n, np.nan))
    short_score_arr = (signals["short_score"].values.astype(np.float64)
                       if "short_score" in cols else np.full(n, np.nan))

    stop_level = np.full(n, np.nan, dtype=np.float64)

    if eff_stop_type == "pct":
        if eff_stop_val is not None and eff_stop_val > 0:
            stop_level = np.where(is_long,
                                  entry_price * (1.0 - eff_stop_val),
                                  entry_price * (1.0 + eff_stop_val))
    elif eff_stop_type == "atr":
        if eff_stop_val is not None:
            atr_arr = table["atr_at"][positions]
            fallback = table["atr_fallback_max"][positions]
            atr_val = np.where(np.isnan(atr_arr), fallback, atr_arr)
            ok = ~np.isnan(atr_val)
            if np.any(ok):
                sl = np.where(is_long,
                              entry_price - eff_stop_val * atr_val,
                              entry_price + eff_stop_val * atr_val)
                stop_level = np.where(ok, sl, np.nan)
    elif eff_stop_type == "struct":
        sl = np.where(is_long,
                      np.minimum(table["struct_low"][positions], entry_price * 0.999),
                      np.maximum(table["struct_high"][positions], entry_price * 1.001))
        stop_level = sl
    elif eff_stop_type == "struct_atr":
        if eff_stop_val is not None:
            atr_arr = table["atr_at"][positions]
            fallback = table["atr_fallback_max"][positions]
            atr_val = np.where(np.isnan(atr_arr), fallback, atr_arr)
            ok = ~np.isnan(atr_val)
            if np.any(ok):
                sl = np.where(is_long,
                              table["struct_low"][positions] - eff_stop_val * atr_val,
                              table["struct_high"][positions] + eff_stop_val * atr_val)
                stop_level = np.where(ok, sl, np.nan)
    elif eff_stop_type == "struct_pct":
        sl = np.where(is_long,
                      table["struct_low"][positions] * (1.0 - eff_stop_val),
                      table["struct_high"][positions] * (1.0 + eff_stop_val))
        stop_level = sl
    # else: eff_stop_type is None → no stop, all target exits

    valid_stop = ~np.isnan(stop_level)
    if np.any(valid_stop):
        # Slice scan arrays to the requested exit window
        low_scan_slice = table["low_scan"][positions, :scan_len]
        high_scan_slice = table["high_scan"][positions, :scan_len]

        long_check = is_long & valid_stop
        if np.any(long_check):
            # NaN-aware: NaN <= x is False, so missing bars don't trigger a hit
            long_hit = long_check & np.any(low_scan_slice <= stop_level[:, None], axis=1)
        else:
            long_hit = np.zeros(n, dtype=bool)

        short_check = is_short & valid_stop
        if np.any(short_check):
            short_hit = short_check & np.any(high_scan_slice >= stop_level[:, None], axis=1)
        else:
            short_hit = np.zeros(n, dtype=bool)

        hit_mask = long_hit | short_hit
        exit_price = np.where(hit_mask, stop_level, exit_price)

    exit_type_arr = np.where(hit_mask, "stop", "target")

    direction_f64 = direction.astype(np.float64)
    gross = direction_f64 * (exit_price / entry_price - 1.0)
    net = gross - cost_bps / 1e4
    sides = np.where(is_long, "long", "short")

    trades = pd.DataFrame({
        "direction": direction.astype(np.int64),
        "side": sides,
        "entry": entry_price,
        "exit": exit_price,
        "exit_type": exit_type_arr,
        "score": score_arr,
        "long_score": long_score_arr,
        "short_score": short_score_arr,
        "gross_ret": gross,
        "net_ret": net,
    }, index=pd.DatetimeIndex(list(sig_date_objs), name="date")).sort_index()

    return trades


def _simulate_trades_legacy(
    etf: str,
    signals: pd.DataFrame,
    eff_stop_type: Optional[str],
    eff_stop_val: Optional[float],
    eff_exit_bar: int,
    cost_bps: float,
) -> pd.DataFrame:
    """Legacy per-day loop fallback (used only if exit_bar exceeds the
    DayTable's precomputed range, which should not happen in practice)."""
    by_date = get_grouped_bars(etf)
    decision_bar = DECISION_BAR[etf]
    need_atr = eff_stop_type in ("atr", "struct_atr")
    atr_series = get_daily_atr14(etf) if need_atr else None

    rows = []
    for date, row in signals.iterrows():
        d = date.date()
        if d not in by_date:
            continue
        day = by_date[d]
        direction = int(row["direction"])
        atr_val = None
        if need_atr and atr_series is not None:
            atr_val = atr_series.get(d)
            if atr_val is None or np.isnan(atr_val):
                atr_val = (atr_series.iloc[:atr_series.index.get_loc(d)].max()
                           if len(atr_series) > 0 else None)
        entry, exit_, exit_type = _day_bars_to_series(
            day, decision_bar, eff_exit_bar, direction=direction,
            stop_type=eff_stop_type, stop_val=eff_stop_val, atr_val=atr_val,
        )
        if entry is None:
            continue
        gross = direction * (exit_ / entry - 1.0)
        net = gross - cost_bps / 1e4
        rows.append({
            "date": date, "direction": direction,
            "side": "long" if direction > 0 else "short",
            "entry": entry, "exit": exit_, "exit_type": exit_type,
            "score": row.get("fired_score", row.get("score", np.nan)),
            "long_score": row.get("long_score", np.nan),
            "short_score": row.get("short_score", np.nan),
            "gross_ret": gross, "net_ret": net,
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).set_index("date").sort_index()


def _day_bars_to_series(
    day_data: dict,
    decision_bar: int,
    exit_bar: int,
    direction: int = 0,
    stop_pct: Optional[float] = None,
    stop_type: Optional[str] = None,
    stop_val: Optional[float] = None,
    atr_val: Optional[float] = None,
):
    """Extract entry & exit prices from a single day's 48 bars.

    Optionally simulates an intraday stop-loss by scanning 5m bar lows/highs
    between entry and exit.  Returns (entry_price, exit_price, exit_type)
    or (None, None, None) if bars are missing.

    Entry timing matches the trade_return target in build_features.py:
        decision at close of bar (decision_bar)
        entry    at open  of bar (decision_bar + 1)
        exit     at close of bar (exit_bar), or stop price if triggered earlier.
    """
    entry_idx = decision_bar + 1
    open_arr = day_data["open"]
    close_arr = day_data["close"]
    if len(open_arr) <= max(entry_idx, exit_bar):
        return None, None, None
    entry_price = float(open_arr[entry_idx])
    exit_price = float(close_arr[exit_bar])
    if entry_price <= 0 or exit_price <= 0:
        return None, None, None

    exit_type = "target"

    eff_stop_type = stop_type
    eff_stop_val = stop_val
    if eff_stop_type is None and stop_pct is not None and stop_pct > 0:
        eff_stop_type = "pct"
        eff_stop_val = stop_pct

    if eff_stop_type is not None and direction != 0:
        stop_level = None
        if eff_stop_type == "pct":
            if direction > 0:
                stop_level = entry_price * (1.0 - eff_stop_val)
            else:
                stop_level = entry_price * (1.0 + eff_stop_val)
        elif eff_stop_type == "atr":
            if atr_val is not None and not np.isnan(atr_val):
                if direction > 0:
                    stop_level = entry_price - eff_stop_val * atr_val
                else:
                    stop_level = entry_price + eff_stop_val * atr_val
        elif eff_stop_type == "struct":
            if direction > 0:
                struct_low = float(np.min(day_data["low"][:entry_idx]))
                stop_level = min(struct_low, entry_price * 0.999)
            else:
                struct_high = float(np.max(day_data["high"][:entry_idx]))
                stop_level = max(struct_high, entry_price * 1.001)
        elif eff_stop_type == "struct_atr":
            if atr_val is not None and not np.isnan(atr_val):
                if direction > 0:
                    struct_low = float(np.min(day_data["low"][:entry_idx]))
                    stop_level = struct_low - eff_stop_val * atr_val
                else:
                    struct_high = float(np.max(day_data["high"][:entry_idx]))
                    stop_level = struct_high + eff_stop_val * atr_val
        elif eff_stop_type == "struct_pct":
            if direction > 0:
                struct_low = float(np.min(day_data["low"][:entry_idx]))
                stop_level = struct_low * (1.0 - eff_stop_val)
            else:
                struct_high = float(np.max(day_data["high"][:entry_idx]))
                stop_level = struct_high * (1.0 + eff_stop_val)

        if stop_level is not None:
            if direction > 0:
                low_arr = day_data["low"]
                scan = low_arr[entry_idx:exit_bar + 1]
                hits = np.where(scan <= stop_level)[0]
                if len(hits) > 0:
                    exit_price = stop_level
                    exit_type = "stop"
            else:
                high_arr = day_data["high"]
                scan = high_arr[entry_idx:exit_bar + 1]
                hits = np.where(scan >= stop_level)[0]
                if len(hits) > 0:
                    exit_price = stop_level
                    exit_type = "stop"

    return entry_price, exit_price, exit_type


def _day_bars_to_series_legacy(day_data: dict, decision_bar: int, exit_bar: int):
    """Backward-compatible wrapper returning (entry, exit) only."""
    entry, exit_, _ = _day_bars_to_series(day_data, decision_bar, exit_bar)
    return entry, exit_


def backtest_etf(
    etf: str,
    threshold_pct: float = 70.0,
    min_conviction_pct: float = 60.0,
    cost_bps: float = DEFAULT_COST_BPS,
    direction_mode: str = "both",
) -> dict:
    """[Legacy] Symmetric-threshold backtest. Use `backtest_long_short` for new work."""
    signals = get_signals(etf, threshold_pct=threshold_pct,
                          min_conviction_pct=min_conviction_pct,
                          direction_mode=direction_mode)
    signals = signals[signals["direction"] != 0]
    if len(signals) == 0:
        return _empty_result(etf)

    by_date = get_grouped_bars(etf)

    decision_bar = DECISION_BAR[etf]
    exit_bar = EXIT_BAR

    rows = []
    for date, row in signals.iterrows():
        d = date.date()
        if d not in by_date:
            continue
        day = by_date[d]
        entry, exit_ = _day_bars_to_series_legacy(day, decision_bar, exit_bar)
        if entry is None:
            continue
        direction = int(row["direction"])
        gross = direction * (exit_ / entry - 1.0)
        net = gross - cost_bps / 1e4
        rows.append({
            "date": date,
            "direction": direction,
            "entry": entry,
            "exit": exit_,
            "score": row["score"],
            "gross_ret": gross,
            "net_ret": net,
        })

    if not rows:
        return _empty_result(etf)

    trades = pd.DataFrame(rows).set_index("date").sort_index()
    metrics = _summarize(trades, etf, cost_bps)
    metrics["trades"] = trades
    return metrics


def backtest_long_short(
    etf: str,
    long_threshold_pct: float = 70.0,
    long_conviction_pct: float = 60.0,
    short_threshold_pct: float = 70.0,
    short_conviction_pct: float = 60.0,
    cost_bps: float = DEFAULT_COST_BPS,
    long_enabled: bool = True,
    short_enabled: bool = True,
    min_periods: int = 60,
    mode: str = "single",
    stop_pct: Optional[float] = None,
    stop_atr_k: Optional[float] = None,
    stop_type: Optional[str] = None,
    stop_val: Optional[float] = None,
    exit_bar: Optional[int] = None,
    gated: bool = False,
) -> dict:
    """Run backtest with INDEPENDENT long_model / short_model thresholds.

    Parameters
    ----------
    mode : {"single", "hybrid", "dual"}
        Signal mode passed through to ``get_long_short_signals``.
    stop_pct : float or None
        Fixed stop-loss as a fraction of entry (e.g. 0.01 = 1%). Legacy parameter.
    stop_atr_k : float or None
        ATR-based stop-loss: ``stop = k * ATR14 / entry``. Legacy parameter.
    stop_type : str or None
        Stop loss type: {"pct", "atr", "struct", "struct_atr", "struct_pct"}.
    stop_val : float or None
        Stop loss parameter value (e.g. fraction or ATR multiplier or cushion).
    exit_bar : int or None
        Custom exit bar index (defaults to EXIT_BAR=41, i.e. 14:30 close).
    gated : bool
        If True, apply the day-model gating model as a post-hoc veto filter.

    Notes
    -----
    Results are memoised in ``_BT_CACHE`` keyed by every parameter below —
    calibration re-runs the same (etf, thr, conv, stop, exit_bar) combos
    repeatedly so this is a large win. Returns the same dict every call;
    callers must copy ``trades`` before mutating (all current callers do).
    """
    eff_exit_bar = exit_bar if exit_bar is not None else EXIT_BAR
    eff_stop_type = stop_type
    eff_stop_val = stop_val
    if eff_stop_type is None:
        if stop_atr_k is not None:
            eff_stop_type = "atr"
            eff_stop_val = stop_atr_k
        elif stop_pct is not None:
            eff_stop_type = "pct"
            eff_stop_val = stop_pct

    key = (etf, float(long_threshold_pct), float(long_conviction_pct),
           float(short_threshold_pct), float(short_conviction_pct),
           float(cost_bps), bool(long_enabled), bool(short_enabled),
           int(min_periods), mode,
           eff_stop_type, None if eff_stop_val is None else float(eff_stop_val),
           int(eff_exit_bar), bool(gated))
    cached = _BT_CACHE.get(key)
    if cached is not None:
        return cached

    signals = get_long_short_signals(
        etf,
        long_threshold_pct=long_threshold_pct,
        long_conviction_pct=long_conviction_pct,
        short_threshold_pct=short_threshold_pct,
        short_conviction_pct=short_conviction_pct,
        min_periods=min_periods,
        long_enabled=long_enabled,
        short_enabled=short_enabled,
        mode=mode,
    )

    if gated:
        signals = _apply_gating_veto(etf, signals)

    signals = signals[signals["direction"] != 0]
    if len(signals) == 0:
        result = _empty_long_short_result(etf)
        _BT_CACHE[key] = result
        return result

    trades = _simulate_trades_vectorized(
        etf, signals, eff_stop_type, eff_stop_val, eff_exit_bar, cost_bps,
    )
    if len(trades) == 0:
        result = _empty_long_short_result(etf)
        _BT_CACHE[key] = result
        return result

    metrics = _summarize_long_short(trades, etf, cost_bps)
    metrics["trades"] = trades
    _BT_CACHE[key] = metrics
    return metrics


_BT_CACHE = {}


def _apply_gating_veto(etf: str, signals: pd.DataFrame) -> pd.DataFrame:
    """Apply the day-model gating model as a post-hoc veto over signals.

    Long directions are zeroed on days the long-gate does NOT fire; short
    directions on days the short-gate does NOT fire. Days absent from the gate
    mask are kept (no veto). If no gating model exists, signals are returned
    unchanged.
    """
    try:
        from .gating_loader import load_gating_mask
    except Exception:
        return signals

    out = signals.copy()
    for side, sign in (("long", 1), ("short", -1)):
        mask = load_gating_mask(etf, side)
        if mask is None:
            continue
        # Align mask to signal index (dates). mask is indexed by date (DatetimeIndex).
        aligned = mask.reindex(out.index)
        side_rows = out["direction"] == sign
        # Veto: zero direction where gate did not fire; NaN in reindex → keep
        veto = aligned.fillna(True) == False
        out.loc[side_rows & veto, "direction"] = 0
    return out


def _empty_result(etf: str) -> dict:
    return {
        "etf": etf, "n_trades": 0, "win_rate": float("nan"),
        "sharpe": float("nan"), "pnl_total": 0.0, "max_dd": float("nan"),
        "mean_ret": float("nan"), "long_n": 0, "short_n": 0,
        "trades": pd.DataFrame(),
    }


def _empty_long_short_result(etf: str) -> dict:
    return {
        "etf": etf, "n_trades": 0,
        "long_n": 0, "short_n": 0,
        "combined_sharpe": float("nan"), "combined_pnl_bps": 0.0,
        "combined_max_dd_bps": float("nan"), "combined_win_rate": float("nan"),
        "long_sharpe": float("nan"), "long_pnl_bps": 0.0,
        "long_max_dd_bps": float("nan"), "long_win_rate": float("nan"),
        "long_mean_ret_bps": float("nan"),
        "short_sharpe": float("nan"), "short_pnl_bps": 0.0,
        "short_max_dd_bps": float("nan"), "short_win_rate": float("nan"),
        "short_mean_ret_bps": float("nan"),
        "trades": pd.DataFrame(),
    }


def _metrics_from_rets(rets: np.ndarray) -> dict:
    n = len(rets)
    if n == 0:
        return {"n": 0, "sharpe": float("nan"), "pnl_bps": 0.0,
                "max_dd_bps": float("nan"), "win_rate": float("nan"),
                "mean_ret_bps": float("nan")}
    cum = np.insert(np.cumsum(rets), 0, 0.0)
    sharpe = (float(np.mean(rets) / np.std(rets, ddof=1) * np.sqrt(252))
              if n > 1 and np.std(rets, ddof=1) > 0 else float("nan"))
    max_dd = float(np.min(cum - np.maximum.accumulate(cum)))
    return {
        "n": n,
        "sharpe": sharpe,
        "pnl_bps": float(rets.sum() * 1e4),
        "max_dd_bps": float(max_dd * 1e4),
        "win_rate": float((rets > 0).mean()),
        "mean_ret_bps": float(np.mean(rets) * 1e4),
    }


def _summarize_long_short(trades: pd.DataFrame, etf: str, cost_bps: float) -> dict:
    """Compute combined + per-side metrics."""
    long_t = trades[trades["direction"] > 0]
    short_t = trades[trades["direction"] < 0]

    long_m = _metrics_from_rets(long_t["net_ret"].values)
    short_m = _metrics_from_rets(short_t["net_ret"].values)
    combined_m = _metrics_from_rets(trades["net_ret"].values)

    return {
        "etf": etf,
        "n_trades": combined_m["n"],
        "long_n": long_m["n"],
        "short_n": short_m["n"],
        "combined_sharpe": combined_m["sharpe"],
        "combined_pnl_bps": combined_m["pnl_bps"],
        "combined_max_dd_bps": combined_m["max_dd_bps"],
        "combined_win_rate": combined_m["win_rate"],
        "long_sharpe": long_m["sharpe"],
        "long_pnl_bps": long_m["pnl_bps"],
        "long_max_dd_bps": long_m["max_dd_bps"],
        "long_win_rate": long_m["win_rate"],
        "long_mean_ret_bps": long_m["mean_ret_bps"],
        "short_sharpe": short_m["sharpe"],
        "short_pnl_bps": short_m["pnl_bps"],
        "short_max_dd_bps": short_m["max_dd_bps"],
        "short_win_rate": short_m["win_rate"],
        "short_mean_ret_bps": short_m["mean_ret_bps"],
        "cost_bps": cost_bps,
    }


def _summarize(trades: pd.DataFrame, etf: str, cost_bps: float) -> dict:
    rets = trades["net_ret"].values
    n = len(rets)
    wins = (rets > 0).sum()
    cum = np.insert(np.cumsum(rets), 0, 0.0)
    max_dd = float(np.min(cum - np.maximum.accumulate(cum))) if n else float("nan")
    sharpe = float(np.mean(rets) / np.std(rets, ddof=1) * np.sqrt(252)) if n > 1 and np.std(rets, ddof=1) > 0 else float("nan")
    long_rets = trades.loc[trades["direction"] > 0, "net_ret"]
    short_rets = trades.loc[trades["direction"] < 0, "net_ret"]
    return {
        "etf": etf,
        "n_trades": n,
        "long_n": int((trades["direction"] > 0).sum()),
        "short_n": int((trades["direction"] < 0).sum()),
        "win_rate": float(wins / n) if n else float("nan"),
        "mean_ret": float(np.mean(rets)) if n else float("nan"),
        "pnl_total": float(cum[-1]) if n else 0.0,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "cost_bps": cost_bps,
        "long_mean_ret": float(long_rets.mean()) if len(long_rets) else float("nan"),
        "short_mean_ret": float(short_rets.mean()) if len(short_rets) else float("nan"),
    }


def split_holdout(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split trades into IS (pre-holdout) and OOS (holdout)."""
    cutoff = pd.Timestamp(HOLDOUT_START)
    is_ = trades[trades.index < cutoff]
    oos = trades[trades.index >= cutoff]
    return is_, oos


def summarize_oos(etf: str, trades: pd.DataFrame) -> dict:
    """Per-year OOS metrics for stability check."""
    if len(trades) == 0:
        return {}
    out = {}
    for year, g in trades.groupby(trades.index.year):
        r = g["net_ret"].values
        n = len(r)
        if n == 0:
            continue
        sharpe = (float(np.mean(r) / np.std(r, ddof=1) * np.sqrt(252))
                  if n > 1 and np.std(r, ddof=1) > 0 else float("nan"))
        out[int(year)] = {
            "n": n, "win_rate": float((r > 0).mean()),
            "mean_ret_bps": float(np.mean(r) * 1e4),
            "pnl_bps": float(r.sum() * 1e4),
            "sharpe": sharpe,
        }
    return out


if __name__ == "__main__":
    print("Smoke test: 300ETF long/short backtest with stop-loss (cost=15bps)")
    print("=" * 72)

    # Baseline: no stop-loss
    r = backtest_long_short("300ETF")
    print(f"  [no stop] combined: n={r['n_trades']}, Sharpe={r['combined_sharpe']:+.2f}, "
          f"P&L={r['combined_pnl_bps']:+.0f}bps")

    # With fixed 0.5% stop-loss
    r2 = backtest_long_short("300ETF", stop_pct=0.005)
    n_stopped = int((r2["trades"]["exit_type"] == "stop").sum()) if len(r2["trades"]) > 0 else 0
    print(f"  [stop=0.5%] combined: n={r2['n_trades']}, Sharpe={r2['combined_sharpe']:+.2f}, "
          f"P&L={r2['combined_pnl_bps']:+.0f}bps, stopped={n_stopped}")

    # With ATR-based stop (k=1.0)
    r3 = backtest_long_short("300ETF", stop_atr_k=1.0)
    n_stopped3 = int((r3["trades"]["exit_type"] == "stop").sum()) if len(r3["trades"]) > 0 else 0
    print(f"  [stop=1.0xATR] combined: n={r3['n_trades']}, Sharpe={r3['combined_sharpe']:+.2f}, "
          f"P&L={r3['combined_pnl_bps']:+.0f}bps, stopped={n_stopped3}")

    is_, oos = split_holdout(r["trades"])
    print(f"\n  [no stop] IS={len(is_)} trades, P&L={is_['net_ret'].sum()*1e4:+.0f}bps")
    print(f"  [no stop] OOS={len(oos)} trades, P&L={oos['net_ret'].sum()*1e4:+.0f}bps")
    print("\n  Per-year OOS (no stop):")
    for y, m in summarize_oos("300ETF", oos).items():
        print(f"    {y}: n={m['n']:>3}, wr={m['win_rate']:.1%}, "
              f"mean={m['mean_ret_bps']:+.1f}bps, sharpe={m['sharpe']:+.2f}")
