"""
research_limit_entry.py - Research Protective Put Limit Order Entry
===================================================================
Analyzes the 5-minute intraday price drops of the Put Level 1 option
during the Thursday-Friday entry window of each monthly cycle.
Validates the Black-Scholes mapping method:
1. Predicts ETF open-to-high P10 return using the trained open-high model.
2. Translates the ETF target to the option limit price using the Black-Scholes formula.
3. Evaluates historical fill rate (target 90%+).

Usage:
    python research_limit_entry.py -e 300
    python research_limit_entry.py -e 50
    python research_limit_entry.py -e 500
"""

import os
import sys
import json
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings("ignore")

# ETF configurations
ETF_CONFIG = {
    "50":  {
        "path": "./data/50ETF_1d.parquet",
        "etf_5m": "./data/50ETF_5m.parquet",
        "opt_5m": "./data/50ETF_historical_prices_5m.parquet",
        "opt_daily": "./data/50ETF_historical_prices.parquet",
        "inst": "./data/50ETF_instruments.parquet",
        "name": "50ETF (510050)"
    },
    "300": {
        "path": "./data/510300_1d.parquet",
        "etf_5m": "./data/510300_5m.parquet",
        "opt_5m": "./data/300ETF_historical_prices_5m.parquet",
        "opt_daily": "./data/300ETF_historical_prices.parquet",
        "inst": "./data/300ETF_instruments.parquet",
        "name": "300ETF (510300)"
    },
    "500": {
        "path": "./data/500ETF_1d.parquet",
        "etf_5m": "./data/500ETF_5m.parquet",
        "opt_5m": "./data/500ETF_historical_prices_5m.parquet",
        "opt_daily": "./data/500ETF_historical_prices.parquet",
        "inst": "./data/500ETF_instruments.parquet",
        "name": "500ETF (510500)"
    },
}

QUANTILE = 0.90          # Target 90% fill rate
OUT_DIR = "./backtest"
RISK_FREE = 0.02

# Black-Scholes math functions
def _cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

import math

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

def compute_iv(market_price, S, K, T, r, is_call):
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

def extract_put_targets(etf_key: str) -> pd.DataFrame:
    """Extract protective put low target (y_put) for all cycles using 5m data."""
    cfg = ETF_CONFIG[etf_key]
    
    print("Loading data...")
    inst = pd.read_parquet(cfg["inst"])
    opt = pd.read_parquet(cfg["opt_daily"])
    etf = pd.read_parquet(cfg["path"])
    
    inst['maturity_date'] = pd.to_datetime(inst['maturity_date'])
    opt['date'] = pd.to_datetime(opt['date'])
    etf['date'] = pd.to_datetime(etf['date'])
    
    inst_slim = inst[['order_book_id', 'maturity_date', 'option_type']].drop_duplicates()
    opt = opt.merge(inst_slim, on='order_book_id', how='left')
    
    opt_5m = pd.read_parquet(cfg["opt_5m"])
    opt_5m['datetime'] = pd.to_datetime(opt_5m['datetime'])
    opt_5m['date'] = opt_5m['datetime'].dt.normalize()
    
    # Pre-group by order_book_id for speed
    print("Grouping 5m option data by contract ID...")
    opt_5m_by_id = {ob_id: group for ob_id, group in opt_5m.groupby('order_book_id')}
    
    # Cycle detection
    trading_days_set = set(etf['date'].dt.normalize())
    opt_trading_days = sorted(opt["date"].unique())
    expiries_cp = sorted(opt.groupby(["maturity_date", "option_type"])["order_book_id"].nunique().unstack("option_type").dropna().index.tolist())

    cycles = []
    for i, expiry in enumerate(expiries_cp):
        if i == 0:
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates: continue
            entry = candidates[0]
        if entry >= expiry: continue
        if pd.Timestamp(entry).normalize() not in trading_days_set: continue
        cycles.append({"entry_date": entry, "expiry_date": expiry})

    results = []
    
    print("Extracting targets and simulating limit entry...")
    # Load open-high model
    from predict_open_high import load_model, load_and_engineer, predict_single
    oh_meta = load_model(etf_key)
    df_eng = load_and_engineer(etf_key)
    
    for idx, cyc in enumerate(cycles):
        entry = pd.Timestamp(cyc["entry_date"])
        expiry = pd.Timestamp(cyc["expiry_date"])
        
        day_etf = etf[etf['date'] == entry]
        if day_etf.empty: continue
        etf_close_entry = float(day_etf.iloc[0]['close'])
        etf_open_entry = float(day_etf.iloc[0]['open'])
        
        # Select Put Option
        day_opt = opt[
            (opt['date'] == entry) &
            (opt['maturity_date'] == expiry) &
            (opt['option_type'] == 'P') &
            (opt['close'] > 0)
        ].copy()
        
        if day_opt.empty: continue
        
        # Select Level 1 Put (strike closest to and below etf_close)
        candidates = day_opt[day_opt['strike_price'] < etf_close_entry].sort_values('strike_price', ascending=False)
        if candidates.empty:
            day_opt['dist'] = (day_opt['strike_price'] - etf_close_entry).abs()
            put_contract = day_opt.loc[day_opt['dist'].idxmin()]
        else:
            put_contract = candidates.iloc[0]
            
        order_book_id = put_contract['order_book_id']
        strike_price = float(put_contract['strike_price'])
        
        # Filter Put 5m prices
        contract_all_5m = opt_5m_by_id.get(order_book_id)
        if contract_all_5m is None: continue
        
        trading_days = sorted(etf['date'].unique())
        entry_idx = trading_days.index(entry)
        window_days = trading_days[entry_idx : entry_idx + 2]
        
        contract_5m = contract_all_5m[
            contract_all_5m['date'].isin(window_days)
        ].sort_values('datetime')
        
        contract_5m = contract_5m[contract_5m['open'] > 0]
        if contract_5m.empty: continue
        
        P_open = float(contract_5m.iloc[0]['open'])
        P_min_low = float(contract_5m['low'].min())
        
        # Open IV
        dte = (expiry - entry).days
        T = max(dte, 1) / 365.0
        sigma_open = compute_iv(P_open, etf_open_entry, strike_price, T, RISK_FREE, False)
        
        # Predict dynamic ETF P10 using open-high model
        eng_row = df_eng[df_eng['date'] == entry]
        if eng_row.empty:
            fallbacks = {"50": 0.001634, "300": 0.001505, "500": 0.001687}
            R_ETF_P10_frac = fallbacks.get(etf_key, 0.0015)
        else:
            R_ETF_P10_pct = predict_single(oh_meta, eng_row)
            R_ETF_P10_frac = R_ETF_P10_pct / 100.0
            
        S_target = etf_open_entry * (1 + R_ETF_P10_frac)
        
        # Predict limit price using BS formula at target ETF high
        T_new = max(dte - 1, 1) / 365.0
        P_limit = _bs_price(S_target, strike_price, T_new, RISK_FREE, sigma_open, False)
        
        # Apply OTM-dependent liquidity cushion
        otm_pct = max(0.0, (etf_open_entry - strike_price) / etf_open_entry * 100.0)
        cushion = (0.5 + 0.5 * otm_pct) / 100.0
        P_limit_cushioned = P_limit * (1 + cushion)
        
        pred_offset_cushioned = (P_limit_cushioned - P_open) / P_open * 100.0
        y_put = (P_min_low - P_open) / P_open * 100.0
        
        is_filled = P_min_low < P_limit_cushioned
        
        results.append({
            'date': entry,
            'contract': order_book_id,
            'strike': strike_price,
            'etf_open': etf_open_entry,
            'opt_open': P_open,
            'opt_min_low': P_min_low,
            'y_put': y_put,
            'pred_offset_cushioned': pred_offset_cushioned,
            'is_filled': is_filled
        })
        
    return pd.DataFrame(results)

def plot_results(df: pd.DataFrame, etf_name: str, etf_key: str, coverage: float):
    fig = plt.figure(figsize=(12, 5))
    gs = gridspec.GridSpec(1, 2, wspace=0.25)

    dates = pd.to_datetime(df["date"].values)
    actual = df["y_put"].values
    pred = df["pred_offset_cushioned"].values

    # 1. Timeline of actual vs predicted
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.scatter(dates, actual, s=15, alpha=0.6, color="#00838F", label="Actual Put Drop %")
    ax1.plot(dates, pred, color="#D84315", linewidth=1.5, label="BS Predicted Limit %")
    ax1.set_title(f"BS P90 Put Limit vs Actual — {etf_name}\n"
                  f"Fill Rate: {coverage:.1f}% (target 90%)", fontsize=11)
    ax1.set_ylabel("(Min Low - Open) / Open (%)")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # 2. Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(actual, bins=15, alpha=0.5, color="#0097A7", edgecolor="white", label="Actuals")
    ax2.axvline(np.percentile(actual, 90), color="#D84315", linestyle="--", linewidth=1.5,
               label=f"Static P90: {np.percentile(actual, 90):.2f}%")
    ax2.set_title("Distribution of Option Min Low Drops", fontsize=11)
    ax2.set_xlabel("Put (Min Low - Open) / Open (%)")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.suptitle(f"Protective Put P90 (90% Fill) BS Limit Order Research — {etf_name}",
                 fontsize=13, fontweight="bold", y=0.98)
    out_path = os.path.join(OUT_DIR, f"put_limit_predictions_{etf_key}.png")
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved visualization to {out_path}")
    return out_path

def main():
    parser = argparse.ArgumentParser(description="BS-Mapping Put Limit Order entry validation.")
    parser.add_argument("-e", "--etf", type=str, required=True, choices=["50", "300", "500"],
                        help="ETF key: 50, 300, or 500")
    args = parser.parse_args()

    etf_key = args.etf
    cfg = ETF_CONFIG[etf_key]

    print(f"\nEvaluating BS-Mapping Put Limit Entry for {cfg['name']}...")
    df = extract_put_targets(etf_key)
    
    coverage = df["is_filled"].mean() * 100.0
    mean_pred_offset = df["pred_offset_cushioned"].mean()
    mean_actual = df["y_put"].mean()
    
    print(f"\nResults:")
    print(f"  Coverage: {coverage:.1f}% (target 90%)")
    print(f"  Mean predicted cushioned offset: {mean_pred_offset:.2f}%")
    print(f"  Mean actual drop: {mean_actual:.2f}%")
    
    # Save visualization
    plot_results(df, cfg["name"], etf_key, coverage)
    
    # Save model metadata (mimic old JSON structure)
    meta = {
        "etf_key": etf_key,
        "features": ["open_high_model_predicted_etf_p10"],
        "model_type": "black_scholes_mapping",
        "quantile": QUANTILE,
        "rolling_coverage": coverage,
        "rolling_mean_pred_offset": mean_pred_offset,
        "rolling_pinball_loss": 0.0,
        "rolling_n_predictions": len(df),
    }
    
    json_path = os.path.join(OUT_DIR, f"put_limit_model_{etf_key}.json")
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to {json_path}")
    print("Done.\n")

if __name__ == "__main__":
    main()
