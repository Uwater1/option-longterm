#!/usr/bin/env python3
"""
Strategy & Backtest Engine for NewTrade framework.
Handles:
1. Conviction thresholding and position sizing (binary or tanh).
2. Train-optimized threshold sweep with production buffer.
3. ETF Spot simulation with 8 bps transaction friction.
4. Performance metric calculations (Sharpe, Max DD, Win Rate, Turnover).
"""

import numpy as np
import pandas as pd


def generate_positions(Z_composite: np.ndarray, z_th: float = 0.5, mode: str = "binary", gamma: float = 1.5,
                       long_only: bool = True, z_th_short: float = None, z_th_short_bias: float = 0.1) -> np.ndarray:
    """
    Generate target positions S_t from composite signal Z_composite.
    
    Args:
      - Z_composite: Composite signal Z array shape (T,)
      - z_th: Conviction threshold for long trades (z_th_long)
      - mode: Sizing mode ('binary', 'tanh', or 'quadratic')
      - gamma: Ramp parameter for tanh/quadratic mode
      - long_only: If True, clamp negative positions to 0.0 (Spot ETF default)
      - z_th_short: Explicit threshold for short trades. If None, uses z_th + z_th_short_bias
      - z_th_short_bias: Additional buffer for short conviction threshold (default +0.1)
    """
    T = len(Z_composite)
    positions = np.zeros(T, dtype=np.float64)
    
    z_th_long = z_th
    z_th_short_effective = z_th_short if z_th_short is not None else (z_th_long + z_th_short_bias)
    
    if mode == "binary":
        long_mask = Z_composite > z_th_long
        short_mask = Z_composite < -z_th_short_effective
        positions[long_mask] = 1.0
        positions[short_mask] = -1.0
        
    elif mode == "tanh":
        for t in range(T):
            z = Z_composite[t]
            if z > z_th_long:
                positions[t] = np.tanh((z - z_th_long) / gamma)
            elif z < -z_th_short_effective:
                positions[t] = np.tanh((z + z_th_short_effective) / gamma)
            else:
                positions[t] = 0.0

    elif mode == "quadratic":
        for t in range(T):
            z = Z_composite[t]
            if z > z_th_long:
                val = ((z - z_th_long) / gamma) ** 2
                positions[t] = min(1.0, val)
            elif z < -z_th_short_effective:
                val = ((-z - z_th_short_effective) / gamma) ** 2
                positions[t] = -min(1.0, val)
            else:
                positions[t] = 0.0
    else:
        raise ValueError(f"Unknown position mode '{mode}'. Choose 'binary', 'tanh', or 'quadratic'.")

    # Long-only clamping for Spot ETFs
    if long_only:
        positions = np.maximum(0.0, positions)

    return positions


def sweep_optimal_threshold(Z_composite_train: np.ndarray, trade_returns_train: np.ndarray,
                            mode: str = "binary", gamma: float = 1.5, long_only: bool = True,
                            fee_bps: float = 0.0008, z_range: tuple = (0.5, 1.5), z_step: float = 0.1,
                            min_active_pct: float = 8.0) -> dict:
    """
    Sweep conviction thresholds on training data for long and short sides independently.
    Finds optimal Z_th_long and Z_th_short that maximize cost-adjusted Sharpe ratio.
    Enforces min_active_pct constraint to prevent low-sample overfitting & high-friction noise.
    """
    z_min, z_max = z_range
    thresholds = np.arange(z_min, z_max + z_step * 0.5, z_step)
    
    sweep_results = []
    best_sharpe_long = -np.inf
    optimal_z_th_long = z_min
    
    # 1. Sweep Long side (Z > z_th)
    for z_th in thresholds:
        positions = generate_positions(Z_composite_train, z_th=z_th, mode=mode, gamma=gamma, long_only=True)
        net_returns, _, _ = simulate_etf_spot(trade_returns_train, positions, fee_bps=fee_bps)
        
        std_net = np.std(net_returns)
        sharpe = float((np.mean(net_returns) / std_net) * np.sqrt(252)) if std_net > 1e-12 else 0.0
        n_active = int((np.abs(positions) > 1e-5).sum())
        active_pct = (n_active / len(positions) * 100.0) if len(positions) > 0 else 0.0
        
        sweep_results.append({
            "z_th": round(float(z_th), 2),
            "cost_sharpe": round(sharpe, 4),
            "n_active_days": n_active,
            "active_pct": round(active_pct, 1),
        })
        
        if active_pct >= min_active_pct and sharpe > best_sharpe_long:
            best_sharpe_long = sharpe
            optimal_z_th_long = float(z_th)

    # 2. Sweep Short side (Z < -z_th)
    best_sharpe_short = -np.inf
    optimal_z_th_short = z_min
    for z_th in thresholds:
        pos_short = np.zeros(len(Z_composite_train), dtype=np.float64)
        if mode == "binary":
            pos_short[Z_composite_train < -z_th] = -1.0
        elif mode == "tanh":
            for t in range(len(Z_composite_train)):
                z = Z_composite_train[t]
                if z < -z_th:
                    pos_short[t] = np.tanh((z + z_th) / gamma)
        elif mode == "quadratic":
            for t in range(len(Z_composite_train)):
                z = Z_composite_train[t]
                if z < -z_th:
                    pos_short[t] = -min(1.0, ((-z - z_th) / gamma) ** 2)
        
        net_returns, _, _ = simulate_etf_spot(trade_returns_train, pos_short, fee_bps=fee_bps)
        std_net = np.std(net_returns)
        sharpe = float((np.mean(net_returns) / std_net) * np.sqrt(252)) if std_net > 1e-12 else 0.0
        n_active = int((np.abs(pos_short) > 1e-5).sum())
        active_pct = (n_active / len(pos_short) * 100.0) if len(pos_short) > 0 else 0.0
        
        if active_pct >= min_active_pct and sharpe > best_sharpe_short:
            best_sharpe_short = sharpe
            optimal_z_th_short = float(z_th)
    
    # 3. 2D search if long_only is False
    best_sharpe_2d = -np.inf
    if not long_only:
        for zl in thresholds:
            for zs in thresholds:
                positions = generate_positions(Z_composite_train, z_th=zl, z_th_short=zs, mode=mode, gamma=gamma, long_only=False)
                n_active = int((np.abs(positions) > 1e-5).sum())
                active_pct = (n_active / len(positions) * 100.0) if len(positions) > 0 else 0.0
                if active_pct < min_active_pct:
                    continue
                
                net_returns, _, _ = simulate_etf_spot(trade_returns_train, positions, fee_bps=fee_bps)
                std_net = np.std(net_returns)
                sharpe = float((np.mean(net_returns) / std_net) * np.sqrt(252)) if std_net > 1e-12 else 0.0
                if sharpe > best_sharpe_2d:
                    best_sharpe_2d = sharpe
                    optimal_z_th_long = float(zl)
                    optimal_z_th_short = float(zs)

    return {
        "optimal_z_th": round(optimal_z_th_long, 2),
        "optimal_z_th_long": round(optimal_z_th_long, 2),
        "optimal_z_th_short": round(optimal_z_th_short, 2),
        "best_sharpe": round(best_sharpe_long, 4),
        "best_sharpe_short": round(best_sharpe_short, 4),
        "sweep_results": sweep_results,
    }


def compute_production_threshold(train_sweep_result: dict, z_buffer: float = 0.1, z_short_buffer: float = None) -> tuple[float, float]:
    """
    Compute production threshold for long and short sides.
    z_th_long = z_th_long_train + z_buffer
    z_th_short = z_th_short_train + (z_short_buffer if z_short_buffer is not None else z_buffer)
    
    Args:
      - train_sweep_result: Output from sweep_optimal_threshold()
      - z_buffer: Conservative buffer added to train-optimal threshold for long (default 0.1)
      - z_short_buffer: Conservative buffer for short threshold (default z_buffer if None)
      
    Returns:
      - (z_th_long, z_th_short)
    """
    z_th_long_train = train_sweep_result.get("optimal_z_th_long", train_sweep_result.get("optimal_z_th", 0.5))
    z_th_short_train = train_sweep_result.get("optimal_z_th_short", z_th_long_train)
    
    effective_short_buf = z_short_buffer if z_short_buffer is not None else z_buffer
    z_th_long = z_th_long_train + z_buffer
    z_th_short = z_th_short_train + effective_short_buf
    return round(z_th_long, 2), round(z_th_short, 2)



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

    # Long vs Short breakdown
    long_mask = positions > 1e-5
    short_mask = positions < -1e-5
    n_long = int(long_mask.sum())
    n_short = int(short_mask.sum())

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

    win_rate_long = float((net_returns[long_mask] > 0).sum() / n_long * 100.0) if n_long > 0 else 0.0
    win_rate_short = float((net_returns[short_mask] > 0).sum() / n_short * 100.0) if n_short > 0 else 0.0

    # Long-side PnL & Sharpe
    long_net = net_returns[long_mask]
    long_pnl = float(long_net.sum()) if n_long > 0 else 0.0
    long_std = float(np.std(long_net)) if n_long > 1 else 0.0
    long_sharpe = float((np.mean(long_net) / long_std) * np.sqrt(252)) if long_std > 1e-12 else 0.0

    # Short-side PnL & Sharpe
    short_net = net_returns[short_mask]
    short_pnl = float(short_net.sum()) if n_short > 0 else 0.0
    short_std = float(np.std(short_net)) if n_short > 1 else 0.0
    short_sharpe = float((np.mean(short_net) / short_std) * np.sqrt(252)) if short_std > 1e-12 else 0.0

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
        "n_long_trades": n_long,
        "n_short_trades": n_short,
        "trade_window": "10:00-14:35",
        "period": period_str,
        "active_pct": round(active_pct, 1),
        "total_pnl": round(total_pnl, 4),
        "raw_total_pnl": round(raw_total_pnl, 4),
        "cost_sharpe": round(cost_sharpe, 3),
        "raw_sharpe": round(raw_sharpe, 3),
        "max_drawdown": round(max_dd, 4),
        "win_rate_pct": round(win_rate, 1),
        "win_rate_long_pct": round(win_rate_long, 1) if n_long > 0 else None,
        "win_rate_short_pct": round(win_rate_short, 1) if n_short > 0 else None,
        "long_pnl": round(long_pnl, 4),
        "long_sharpe": round(long_sharpe, 3),
        "short_pnl": round(short_pnl, 4),
        "short_sharpe": round(short_sharpe, 3),
        "profit_factor": round(profit_factor, 2),
        "ann_turnover": round(ann_turnover, 2),
    }


def build_trade_log_df(df_oos: pd.DataFrame, Z_composite_oos: np.ndarray, positions_oos: np.ndarray,
                       net_returns: np.ndarray, raw_returns: np.ndarray, fees: np.ndarray,
                       etf: str, scheme: str, z_th: float, asset_type: str = "Spot ETF",
                       trade_returns_arr: np.ndarray = None) -> pd.DataFrame:
    """
    Build detailed date-level trade log DataFrame for CSV export and AI/text inspection.
    """
    dates = pd.to_datetime(df_oos["date"]).dt.strftime("%Y-%m-%d") if "date" in df_oos.columns else pd.Series([f"day_{i}" for i in range(len(df_oos))])
    if trade_returns_arr is not None:
        trade_returns = trade_returns_arr
    else:
        trade_returns = df_oos["trade_return"].values.astype(np.float64) if "trade_return" in df_oos.columns else df_oos["close"].pct_change().fillna(0.0).values
    
    cum_pnl = np.cumsum(net_returns)
    is_trade = (np.abs(positions_oos) > 1e-5).astype(int)

    trade_log = pd.DataFrame({
        "date": dates,
        "etf": etf,
        "asset_type": asset_type,
        "scheme": scheme,
        "z_composite": np.round(Z_composite_oos, 4),
        "z_th": round(float(z_th), 2),
        "position": np.round(positions_oos, 4),
        "is_trade": is_trade,
        "trade_return": np.round(trade_returns, 6),
        "raw_pnl": np.round(raw_returns, 6),
        "fee": np.round(fees, 6),
        "net_pnl": np.round(net_returns, 6),
        "cum_pnl": np.round(cum_pnl, 6),
    })

    return trade_log


