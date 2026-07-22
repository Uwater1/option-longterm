#!/usr/bin/env python3
"""
Strategy & Backtest Engine for NewTrade framework.
Handles:
1. Conviction thresholding and position sizing (binary or tanh).
2. ETF Spot simulation with 8 bps transaction friction.
3. Performance metric calculations (Sharpe, Max DD, Win Rate, Turnover).
"""

import numpy as np
import pandas as pd


def generate_positions(Z_composite: np.ndarray, z_th: float = 0.5, mode: str = "binary", gamma: float = 1.5, long_only: bool = True) -> np.ndarray:
    """
    Generate target positions S_t from composite signal Z_composite.
    
    Args:
      - Z_composite: Composite signal Z array shape (T,)
      - z_th: Conviction threshold (e.g. 0.5)
      - mode: Sizing mode ('binary' or 'tanh')
      - gamma: Ramp parameter for tanh mode
      - long_only: If True, clamp negative positions to 0.0 (Spot ETF default)
    """
    T = len(Z_composite)
    positions = np.zeros(T, dtype=np.float64)
    
    if mode == "binary":
        long_mask = Z_composite > z_th
        short_mask = Z_composite < -z_th
        positions[long_mask] = 1.0
        positions[short_mask] = -1.0
        
    elif mode == "tanh":
        for t in range(T):
            z = Z_composite[t]
            if z > z_th:
                positions[t] = np.tanh((z - z_th) / gamma)
            elif z < -z_th:
                positions[t] = np.tanh((z + z_th) / gamma)
            else:
                positions[t] = 0.0
    else:
        raise ValueError(f"Unknown position mode '{mode}'. Choose 'binary' or 'tanh'.")

    # Long-only clamping for Spot ETFs
    if long_only:
        positions = np.maximum(0.0, positions)

    return positions


def simulate_etf_spot(trade_returns: np.ndarray, positions: np.ndarray, fee_bps: float = 0.0008) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate ETF spot backtest with per-entry state transition fee.
    
    Args:
      - trade_returns: Intraday trade return (10:00 -> 14:35/Close) array shape (T,)
      - positions: S_t array shape (T,)
      - fee_bps: Friction per unit position change (default 8 bps = 0.0008)
      
    Returns:
      - net_returns: Daily net returns after fee shape (T,)
      - raw_returns: Daily gross returns before fee shape (T,)
      - fees: Daily transaction fees shape (T,)
    """
    T = len(trade_returns)
    raw_returns = positions * trade_returns
    
    # Calculate state transition fee: fee_t = |S_t - S_{t-1}| * fee_bps
    pos_prev = np.roll(positions, 1)
    pos_prev[0] = 0.0
    
    turnover = np.abs(positions - pos_prev)
    fees = turnover * fee_bps
    
    net_returns = raw_returns - fees
    
    return net_returns, raw_returns, fees


def calculate_metrics(net_returns: np.ndarray, raw_returns: np.ndarray, positions: np.ndarray, dates: pd.Series = None) -> dict:
    """
    Calculate comprehensive performance metrics.
    """
    T = len(net_returns)
    if T == 0:
        return {}

    # Active days mask
    active_mask = np.abs(positions) > 1e-5
    n_active = int(active_mask.sum())
    active_pct = (n_active / T) * 100.0 if T > 0 else 0.0

    # Cumulative P&L
    total_pnl = float(net_returns.sum())
    raw_total_pnl = float(raw_returns.sum())

    # Annualized Sharpe (assuming 252 trading days per year)
    std_net = np.std(net_returns)
    mean_net = np.mean(net_returns)
    cost_sharpe = float((mean_net / std_net) * np.sqrt(252)) if std_net > 1e-12 else 0.0

    std_raw = np.std(raw_returns)
    mean_raw = np.mean(raw_returns)
    raw_sharpe = float((mean_raw / std_raw) * np.sqrt(252)) if std_raw > 1e-12 else 0.0

    # Max Drawdown
    cum_returns = np.cumsum(net_returns)
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = running_max - cum_returns
    max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

    # Win Rate on active trading days
    if n_active > 0:
        active_returns = net_returns[active_mask]
        win_rate = float((active_returns > 0).sum() / n_active) * 100.0
        
        pos_wins = active_returns[active_returns > 0].sum()
        neg_losses = np.abs(active_returns[active_returns < 0].sum())
        profit_factor = float(pos_wins / neg_losses) if neg_losses > 1e-12 else 999.0
    else:
        win_rate = 0.0
        profit_factor = 0.0

    # Annualized Turnover (sum of turnover / years)
    pos_prev = np.roll(positions, 1)
    pos_prev[0] = 0.0
    total_turnover = float(np.abs(positions - pos_prev).sum())
    years = T / 252.0
    ann_turnover = float(total_turnover / years) if years > 0 else 0.0

    # Date range formatting
    if dates is not None and len(dates) > 0:
        start_str = pd.to_datetime(dates.iloc[0]).strftime("%Y-%m")
        end_str = pd.to_datetime(dates.iloc[-1]).strftime("%Y-%m")
        period_str = f"{start_str} ~ {end_str}"
    else:
        period_str = "N/A"

    return {
        "n_days": T,
        "n_active_days": n_active,
        "n_trades": n_active,  # Each active day is 1 intraday trade (10:00 -> 14:35)
        "trade_window": "10:00-14:35",
        "period": period_str,
        "active_pct": round(active_pct, 1),
        "total_pnl": round(total_pnl, 4),
        "raw_total_pnl": round(raw_total_pnl, 4),
        "cost_sharpe": round(cost_sharpe, 3),
        "raw_sharpe": round(raw_sharpe, 3),
        "max_drawdown": round(max_dd, 4),
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": round(profit_factor, 2),
        "ann_turnover": round(ann_turnover, 2),
    }
