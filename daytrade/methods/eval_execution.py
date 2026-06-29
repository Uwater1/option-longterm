"""Comparative Execution Backtester for Deployed Daytrade Strategy Signals.

Evaluates trade placement variants on actual walk-forward deployed strategy trades (from calibration.json):
1. Direct ETF / Borrow Sell (Baseline 15bp)
2. Stock Index Futures (IH/IF/IC, ~8x leverage)
3. Naked Long Option (OTM1 Call/Put, 8 RMB cost/contract)
4. Vertical Debit Spread (OTM1/OTM2 Bull Call/Bear Put Spread, 14 RMB cost/spread, no margin)
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

from daytrade import ETFS, DEFAULT_COST_BPS
from daytrade.calibrate import replay_side_wf_trades
from .cost_model import calc_etf_net_return, calc_naked_option_pnl, calc_vertical_spread_pnl
from .option_pricing import get_option_prices_for_trade

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "daytrade" / "data"
CALIB_PATH = DATA_DIR / "calibration.json"

def load_deployed_configs() -> dict:
    if not CALIB_PATH.exists():
        raise SystemExit(f"Calibration file not found at {CALIB_PATH}. Run deploy first.")
    data = json.loads(CALIB_PATH.read_text())
    return data.get("results", {})

def run_execution_eval():
    configs = load_deployed_configs()
    results = {}
    
    for etf in ETFS:
        if etf not in configs:
            continue
        cfg = configs[etf]
        print(f"\n================ Evaluating Deployed Execution for {etf} ================")
        
        long_trades = replay_side_wf_trades(etf, "long", cfg.get("long"), DEFAULT_COST_BPS)
        short_trades = replay_side_wf_trades(etf, "short", cfg.get("short"), DEFAULT_COST_BPS)
        
        parts = []
        if len(long_trades) > 0:
            parts.append(long_trades)
        if len(short_trades) > 0:
            parts.append(short_trades)
            
        if not parts:
            print(f"No deployed trades for {etf}")
            continue
            
        deployed_df = pd.concat(parts).sort_index()
        
        etf_trades = []
        fut_trades = []
        naked_opt_trades = []
        spread_trades = []
        
        for dt, row in deployed_df.iterrows():
            spot_entry = float(row["entry"])
            spot_exit = float(row["exit"])
            direction = int(row["direction"])
            
            if spot_entry <= 0 or spot_exit <= 0:
                continue
                
            # 1. ETF Direct (already computed net_ret in backtest)
            net_etf_ret = float(row["net_ret"])
            etf_trades.append(net_etf_ret)
            
            # 2. Futures (~8x leverage)
            net_fut_ret = net_etf_ret * 8.0
            fut_trades.append(net_fut_ret)
            
            # 3. Naked Option OTM1
            opt_prices = get_option_prices_for_trade(spot_entry, spot_exit, direction)
            naked_res = calc_naked_option_pnl(opt_prices["otm1_entry"], opt_prices["otm1_exit"])
            naked_opt_trades.append(naked_res["net_ret_premium"])
            
            # 4. Vertical Debit Spread
            spread_res = calc_vertical_spread_pnl(
                opt_prices["otm1_entry"], opt_prices["otm1_exit"],
                opt_prices["otm2_entry"], opt_prices["otm2_exit"]
            )
            spread_trades.append(spread_res["net_ret_capital"])
            
        def stats(arr):
            if not arr:
                return {"trades": 0, "win_rate": 0.0, "mean_ret": 0.0, "sharpe": 0.0, "total_pnl": 0.0}
            arr = np.array(arr)
            win_rate = float(np.mean(arr > 0))
            mean_ret = float(np.mean(arr))
            std_ret = float(np.std(arr))
            sharpe = (mean_ret / std_ret * np.sqrt(252.0)) if std_ret > 1e-6 else 0.0
            return {
                "trades": len(arr),
                "win_rate": win_rate,
                "mean_ret": mean_ret,
                "sharpe": sharpe,
                "total_pnl": float(np.sum(arr)),
            }
            
        results[etf] = {
            "ETF Direct": stats(etf_trades),
            "Stock Index Futures": stats(fut_trades),
            "Naked Long Option": stats(naked_opt_trades),
            "Vertical Spread": stats(spread_trades),
        }
        
        print(f"{'Method':<20} | {'Trades':<7} | {'WinRate':<8} | {'Mean Return':<12} | {'Sharpe':<8}")
        print("-" * 65)
        for method, s in results[etf].items():
            print(f"{method:<20} | {s['trades']:<7} | {s['win_rate']*100:6.1f}% | {s['mean_ret']*100:10.2f}% | {s['sharpe']:8.2f}")
            
    return results

if __name__ == "__main__":
    run_execution_eval()
