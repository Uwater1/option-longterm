import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.append(os.path.abspath("."))
import backtest_engine as engine

def evaluate_etf_filters(etf_choice):
    print(f"\n==================== Validating Filters for {etf_choice}ETF ====================")
    engine.select_underlying(etf_choice)
    inst, opt, etf = engine.load_data()
    
    # Calculate 30-day forward return (calendar days)
    dates = etf.index.values
    closes = etf["close_adj"].values if "close_adj" in etf.columns else etf["close"].values
    fwd_rets = np.full(len(etf), np.nan)
    for i, dt in enumerate(dates):
        target_dt = dt + np.timedelta64(30, 'D')
        idx = np.searchsorted(dates, target_dt)
        if idx < len(dates):
            fwd_rets[i] = closes[idx] / closes[i] - 1.0
    etf["fwd_ret_30d"] = fwd_rets
    
    # Drop NaNs
    valid_df = etf.dropna(subset=["fwd_ret_30d", "rsi14", "vol20", "skew_20", "kurt_20", "dd_252", "dist_sma50", "iv_vol_ratio"])
    n_obs = len(valid_df)
    rets = valid_df["fwd_ret_30d"].values
    
    # Baseline stats
    baseline_mean = rets.mean()
    baseline_std = rets.std()
    baseline_win = (rets < 0).mean() # Win rate for put (market drops)
    
    print(f"Total trading days evaluated: {n_obs}")
    print(f"Baseline 30d Forward Return: {baseline_mean:+.2%} (std: {baseline_std:.2%})")
    print(f"Baseline Put Win Rate (Return < 0): {baseline_win:.1%}")
    
    # Filters to evaluate
    filters = {}
    if etf_choice == "50":
        filters["VRP Compression + Negative Skewness"] = (
            (valid_df["skew_20"] < -0.5) & (valid_df["iv_vol_ratio"] < 0.9)
        )
    elif etf_choice == "500":
        filters["Kurtosis Expansion + Expensive IV"] = (
            (valid_df["kurt_20"] > 1.0) & (valid_df["iv_vol_ratio"] > 1.2)
        )
    elif etf_choice == "300":
        filters["Bear Market Trend (DD + SMA50)"] = (
            (valid_df["dd_252"] < -0.15) & (valid_df["dist_sma50"] < -1.0)
        )
        filters["Overbought Reversal (RSI + Skew)"] = (
            (valid_df["rsi14"] > 65) & (valid_df["skew_20"] < -0.3)
        )
        filters["Composite Put Filter (Trend OR Reversal)"] = (
            ((valid_df["dd_252"] < -0.15) & (valid_df["dist_sma50"] < -1.0)) |
            ((valid_df["rsi14"] > 65) & (valid_df["skew_20"] < -0.3))
        )
        
    for name, mask in filters.items():
        placement = mask.mean()
        triggers = mask.sum()
        if triggers == 0:
            print(f"\nFilter: {name} - NO TRIGGERS")
            continue
            
        sub_rets = rets[mask]
        filter_mean = sub_rets.mean()
        filter_win = (sub_rets < 0).mean()
        
        # t-test vs non-triggered days
        non_rets = rets[~mask]
        t_stat, p_val = stats.ttest_ind(sub_rets, non_rets, equal_var=False)
        
        print(f"\nFilter: {name}")
        print(f"  Triggers: {triggers} ({placement:.1%} placement rate)")
        print(f"  Mean 30d Forward Return: {filter_mean:+.2%} (Diff vs Baseline: {filter_mean - baseline_mean:+.2%})")
        print(f"  Put Win Rate (Return < 0): {filter_win:.1%} (vs {baseline_win:.1%} baseline)")
        print(f"  t-statistic vs Rest: {t_stat:.2f} (p-value: {p_val:.4f})")

def main():
    for choice in ["50", "300", "500"]:
        evaluate_etf_filters(choice)

if __name__ == "__main__":
    main()
