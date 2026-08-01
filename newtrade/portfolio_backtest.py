#!/usr/bin/env python3
"""
NewTrade Final Portfolio Backtest — Multi-ETF Ensemble.

Combines all live ETFs (159915ETF, 500ETF, 300ETF) into an equal-weight portfolio.
Reports combined Sharpe, PnL, MaxDD, and per-ETF attribution.

Usage:
    python newtrade/portfolio_backtest.py
    python newtrade/portfolio_backtest.py --fee-bps 15   # stress test
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from math import sqrt

from robustness import build_all_composites, compute_ensemble_composite, deflated_sharpe_ratio, run_cpcv_backtest
from strategy import sweep_optimal_threshold, compute_production_threshold, generate_positions, simulate_etf_spot

# Production config
ETFS = ["159915ETF", "500ETF", "300ETF"]
MODE = "binary"
Z_BUFFER = 0.15
BURN_IN = 252
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"
N_TRIALS = 10  # 4 schemes × 3 ETFs, pre-committed to ensemble


def run_portfolio(fee_bps: float = 0.0008, verbose: bool = True) -> dict:
    """Run multi-ETF portfolio backtest."""
    
    t_start = pd.Timestamp(START_DATE)
    
    etf_results = {}
    all_dates = {}
    all_net_returns = {}
    
    for etf in ETFS:
        Z_composites, trade_returns, df, pool = build_all_composites(etf, burn_in=BURN_IN)
        if not Z_composites:
            if verbose:
                print(f"  {etf}: SKIPPED")
            continue
        
        Z_ens = compute_ensemble_composite(Z_composites)
        
        train_mask = df["date"] < t_start
        if END_DATE:
            t_end = pd.Timestamp(END_DATE)
            oos_mask = (df["date"] >= t_start) & (df["date"] < t_end)
        else:
            oos_mask = df["date"] >= t_start
        
        ret_train = trade_returns[train_mask.values]
        ret_oos = trade_returns[oos_mask.values]
        Z_train = Z_ens[train_mask.values]
        Z_oos = Z_ens[oos_mask.values]
        
        # Train threshold
        sw = sweep_optimal_threshold(Z_train, ret_train, mode=MODE, fee_bps=fee_bps, long_only=False)
        zl, zs = compute_production_threshold(sw, z_buffer=Z_BUFFER)
        
        # OOS
        positions = generate_positions(Z_oos, z_th=zl, z_th_short=zs, mode=MODE, long_only=False)
        net_ret, raw_ret, fees = simulate_etf_spot(ret_oos, positions, fee_bps=fee_bps)
        
        dates_oos = df[oos_mask]["date"].values
        n_active = int((np.abs(positions) > 1e-5).sum())
        n_long = int((positions > 1e-5).sum())
        n_short = int((positions < -1e-5).sum())
        
        std_n = np.std(net_ret)
        sr = float((np.mean(net_ret) / std_n) * sqrt(252)) if std_n > 1e-12 else 0.0
        wr = float((net_ret[np.abs(positions) > 1e-5] > 0).mean() * 100) if n_active > 0 else 0.0
        
        sk_v = float(skew(net_ret))
        kt_v = float(kurtosis(net_ret))
        dsr = deflated_sharpe_ratio(sr, n_trials=N_TRIALS, n_obs=len(net_ret),
                                     skewness=sk_v, kurtosis_excess=kt_v)
        
        etf_results[etf] = {
            "sr": sr, "pnl": float(net_ret.sum()), "trades": n_active,
            "n_long": n_long, "n_short": n_short, "wr": wr,
            "z_th_l": zl, "z_th_s": zs, "dsr": dsr["dsr"],
            "dsr_verdict": dsr["verdict"], "n_features": len(pool),
        }
        all_dates[etf] = dates_oos
        all_net_returns[etf] = net_ret
        
        if verbose:
            print(f"  {etf}: SR={sr:.3f}, PnL={net_ret.sum():+.4f}, "
                  f"Trades={n_active}({n_long}L/{n_short}S), WR={wr:.1f}%, "
                  f"DSR={dsr['dsr']:.3f}({dsr['verdict']})")
    
    # Combine into portfolio (equal-weight by return)
    # Align dates across ETFs
    common_dates = None
    for etf, dates in all_dates.items():
        s = set(dates)
        common_dates = s if common_dates is None else common_dates & s
    
    if not common_dates:
        return {"status": "NO_COMMON_DATES"}
    
    common_dates_sorted = sorted(common_dates)
    n_days = len(common_dates_sorted)
    
    # Build aligned return matrix
    portfolio_returns = np.zeros(n_days, dtype=np.float64)
    etf_aligned = {}
    
    for etf, dates in all_dates.items():
        date_to_ret = dict(zip(dates, all_net_returns[etf]))
        aligned = np.array([date_to_ret.get(d, 0.0) for d in common_dates_sorted])
        etf_aligned[etf] = aligned
        portfolio_returns += aligned
    
    # Equal weight: divide by number of active ETFs
    n_etfs = len(etf_aligned)
    portfolio_returns /= n_etfs
    
    # Portfolio metrics
    std_p = np.std(portfolio_returns)
    mean_p = np.mean(portfolio_returns)
    port_sharpe = float((mean_p / std_p) * sqrt(252)) if std_p > 1e-12 else 0.0
    
    cum_ret = np.cumsum(portfolio_returns)
    running_max = np.maximum.accumulate(cum_ret)
    drawdowns = running_max - cum_ret
    max_dd = float(np.max(drawdowns))
    
    total_pnl = float(portfolio_returns.sum())
    
    # Win rate (daily)
    win_rate = float((portfolio_returns > 0).mean() * 100)
    
    # Annualized return
    years = n_days / 252.0
    ann_return = float(total_pnl / years) if years > 0 else 0.0
    
    # Calmar ratio
    calmar = float(ann_return / max_dd) if max_dd > 1e-12 else 0.0
    
    # DSR for portfolio
    sk_p = float(skew(portfolio_returns))
    kt_p = float(kurtosis(portfolio_returns))
    port_dsr = deflated_sharpe_ratio(port_sharpe, n_trials=N_TRIALS, n_obs=n_days,
                                      skewness=sk_p, kurtosis_excess=kt_p)
    
    # CPCV on portfolio (use 159915ETF composite as proxy for signal quality)
    # Actually run proper portfolio CPCV
    cpcv_result = None
    
    if verbose:
        print(f"\n  {'━'*60}")
        print(f"  PORTFOLIO (Equal-weight {n_etfs} ETFs, {n_days} common days)")
        print(f"  {'━'*60}")
        print(f"  Sharpe:     {port_sharpe:.3f}")
        print(f"  DSR(10):    {port_dsr['dsr']:.3f} ({port_dsr['verdict']})")
        print(f"  Total PnL:  {total_pnl:+.4f} (per unit capital)")
        print(f"  Ann Return: {ann_return:+.4f}")
        print(f"  Max DD:     {max_dd:.4f}")
        print(f"  Calmar:     {calmar:.3f}")
        print(f"  Win Rate:   {win_rate:.1f}%")
        print(f"  Skewness:   {sk_p:.3f}")
        print(f"  Kurtosis:   {kt_p:.3f}")
    
    # Per-ETF attribution
    if verbose:
        print(f"\n  Attribution:")
        for etf, aligned in etf_aligned.items():
            etf_pnl = float(aligned.sum()) / n_etfs
            print(f"    {etf}: PnL_contrib={etf_pnl:+.4f}")
    
    return {
        "status": "SUCCESS",
        "n_etfs": n_etfs,
        "n_days": n_days,
        "sharpe": round(port_sharpe, 4),
        "dsr": port_dsr,
        "total_pnl": round(total_pnl, 4),
        "ann_return": round(ann_return, 4),
        "max_drawdown": round(max_dd, 4),
        "calmar": round(calmar, 4),
        "win_rate": round(win_rate, 1),
        "skewness": round(sk_p, 4),
        "kurtosis": round(kt_p, 4),
        "etf_results": etf_results,
        "fee_bps": fee_bps * 10000,
    }


def main():
    parser = argparse.ArgumentParser(description="NewTrade Multi-ETF Portfolio Backtest")
    parser.add_argument("--fee-bps", type=float, default=8.0, help="Fee in bps (default: 8)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    
    fee_bps = args.fee_bps / 10000.0
    
    print("=" * 70)
    print("NEWTRADE MULTI-ETF PORTFOLIO BACKTEST")
    print(f"  Config: Ensemble + Binary L+S | Buffer={Z_BUFFER} | Fee={args.fee_bps}bps")
    print(f"  Period: {START_DATE} ~ {END_DATE}")
    print("=" * 70)
    
    result = run_portfolio(fee_bps=fee_bps, verbose=not args.quiet)
    
    if result["status"] == "SUCCESS":
        # Stress test at multiple fee levels
        print(f"\n\n{'='*70}")
        print("FEE STRESS TEST (Portfolio Level)")
        print(f"{'='*70}")
        print(f"  {'Fee(bps)':>10s} {'Sharpe':>8s} {'DSR10':>8s} {'PnL':>10s} {'MaxDD':>8s} {'Calmar':>8s}")
        
        for fee in [8.0, 12.0, 15.0, 20.0]:
            r = run_portfolio(fee_bps=fee/10000.0, verbose=False)
            if r["status"] == "SUCCESS":
                print(f"  {fee:>10.1f} {r['sharpe']:>8.3f} {r['dsr']['dsr']:>8.3f} "
                      f"{r['total_pnl']:>+10.4f} {r['max_drawdown']:>8.4f} {r['calmar']:>8.3f}")
    
    print("\nDone.")


if __name__ == "__main__":
    main()
