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


def _day_bars_to_series(
    day_data: dict,
    decision_bar: int,
    exit_bar: int,
    direction: int = 0,
    stop_pct: Optional[float] = None,
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

    if stop_pct is not None and stop_pct > 0 and direction != 0:
        if direction > 0:  # long: stop hit when bar low <= stop level
            stop_level = entry_price * (1.0 - stop_pct)
            low_arr = day_data["low"]
            scan = low_arr[entry_idx:exit_bar + 1]
            hits = np.where(scan <= stop_level)[0]
            if len(hits) > 0:
                exit_price = stop_level
                exit_type = "stop"
        else:  # short: stop hit when bar high >= stop level
            stop_level = entry_price * (1.0 + stop_pct)
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
) -> dict:
    """Run backtest with INDEPENDENT long_model / short_model thresholds.

    Parameters
    ----------
    mode : {"single", "hybrid", "dual"}
        Signal mode passed through to ``get_long_short_signals``.
    stop_pct : float or None
        Fixed stop-loss as a fraction of entry (e.g. 0.01 = 1%).
        Mutually exclusive with ``stop_atr_k``.
    stop_atr_k : float or None
        ATR-based stop-loss: ``stop = k * ATR14 / entry``.
        Mutually exclusive with ``stop_pct``.
    """
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
    signals = signals[signals["direction"] != 0]
    if len(signals) == 0:
        return _empty_long_short_result(etf)

    by_date = get_grouped_bars(etf)

    decision_bar = DECISION_BAR[etf]
    exit_bar = EXIT_BAR

    # Pre-compute ATR14 series if ATR-based stop is requested
    atr_series = get_daily_atr14(etf) if stop_atr_k is not None else None

    rows = []
    for date, row in signals.iterrows():
        d = date.date()
        if d not in by_date:
            continue
        day = by_date[d]
        direction = int(row["direction"])

        # Resolve effective stop percentage for this date
        effective_stop = None
        if stop_atr_k is not None and atr_series is not None:
            atr_val = atr_series.get(d)
            if atr_val is None or np.isnan(atr_val):
                atr_val = atr_series.iloc[:atr_series.index.get_loc(d)].max() if len(atr_series) > 0 else None
            if atr_val is not None and not np.isnan(atr_val):
                # Retrieve entry_price directly to avoid calling the stop check logic twice
                entry_idx = decision_bar + 1
                if len(day["open"]) > entry_idx:
                    entry_tmp = float(day["open"][entry_idx])
                    if entry_tmp > 0:
                        effective_stop = stop_atr_k * atr_val / entry_tmp
        elif stop_pct is not None:
            effective_stop = stop_pct

        entry, exit_, exit_type = _day_bars_to_series(
            day, decision_bar, exit_bar, direction=direction, stop_pct=effective_stop,
        )
        if entry is None:
            continue
        gross = direction * (exit_ / entry - 1.0)
        net = gross - cost_bps / 1e4
        rows.append({
            "date": date,
            "direction": direction,
            "side": "long" if direction > 0 else "short",
            "entry": entry,
            "exit": exit_,
            "exit_type": exit_type,
            "score": row.get("fired_score", row.get("score", np.nan)),
            "long_score": row.get("long_score", np.nan),
            "short_score": row.get("short_score", np.nan),
            "gross_ret": gross,
            "net_ret": net,
        })

    if not rows:
        return _empty_long_short_result(etf)

    trades = pd.DataFrame(rows).set_index("date").sort_index()
    metrics = _summarize_long_short(trades, etf, cost_bps)
    metrics["trades"] = trades
    return metrics


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
