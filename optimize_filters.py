import os
import sys
import pandas as pd
import numpy as np
import pandas_ta as ta

# Add current path to sys.path so we can import from backtest_covered_call
sys.path.append(os.path.abspath("."))

from backtest_covered_call import (
    select_underlying, load_data, get_cycles, get_otm_strikes,
    get_strike_by_level, calc_leg_pnl, PATH_IV_CACHE, IV_THRESHOLD
)

def precalculate_cycle_legs(opt, etf, cycles):
    print("Precalculating leg P&Ls for all cycles...")
    cycle_legs = []
    for idx, cyc in enumerate(cycles):
        entry = cyc["entry_date"]
        expiry = cyc["expiry_date"]
        
        # Get calls
        call_legs = get_otm_strikes(opt, etf, entry, expiry, "C", [2, 3, 4])
        call_otm2 = call_legs[0]
        call_otm3 = call_legs[1]
        call_otm4 = call_legs[2]
        
        # Get put
        put_leg = get_strike_by_level(opt, etf, entry, expiry, "P", 1)
        
        # Calculate P&L for each leg
        pnl_otm2 = calc_leg_pnl(call_otm2, opt, etf, expiry, "sell", False)
        pnl_otm3 = calc_leg_pnl(call_otm3, opt, etf, expiry, "sell", False)
        pnl_otm4 = calc_leg_pnl(call_otm4, opt, etf, expiry, "sell", False)
        pnl_put = calc_leg_pnl(put_leg, opt, etf, expiry, "buy", True)
        
        net_otm2 = pnl_otm2["net_rmb"] if pnl_otm2 is not None else 0.0
        net_otm3 = pnl_otm3["net_rmb"] if pnl_otm3 is not None else 0.0
        net_otm4 = pnl_otm4["net_rmb"] if pnl_otm4 is not None else 0.0
        net_put = pnl_put["net_rmb"] if pnl_put is not None else 0.0
        
        cycle_legs.append({
            "entry_date": entry,
            "expiry_date": expiry,
            "OTM2": net_otm2,
            "OTM3": net_otm3,
            "OTM4": net_otm4,
            "Put1": net_put
        })
    return pd.DataFrame(cycle_legs)

def run_optimization(etf_choice, no_put_mode, skip_otm4):
    select_underlying(etf_choice)
    inst, opt, etf = load_data()
    
    # Calculate additional indicators on ETF daily data
    etf["ema20"] = ta.ema(etf["close"], length=20)
    etf["roc20"] = ta.roc(etf["close"], length=20)
    bb = ta.bbands(etf["close"], length=20, std=2)
    etf["bbu20"] = bb["BBU_20_2.0_2.0"]
    etf["bbl20"] = bb["BBL_20_2.0_2.0"]
    etf["sma50"] = ta.sma(etf["close"], length=50)
    etf["vol20"] = etf["close"].pct_change().rolling(20).std() * np.sqrt(252)
    etf["vol20_median"] = etf["vol20"].rolling(252).median()
    macd = ta.macd(etf["close"])
    etf["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan
    adx = ta.adx(etf["high"], etf["low"], etf["close"], length=14)
    etf["adx14"] = adx.iloc[:, 0] if adx is not None else np.nan
    
    cycles = get_cycles(opt, etf)
    print(f"Found {len(cycles)} cycles for {etf_choice}ETF.")
    
    # Pre-calculate leg P&Ls
    df_legs = precalculate_cycle_legs(opt, etf, cycles)
    
    # Align indicators with cycle entry dates
    cycle_indicators = []
    for cyc in cycles:
        idx = cyc["entry_date"].normalize()
        row = etf.loc[idx]
        cycle_indicators.append({
            "entry_date": cyc["entry_date"],
            "rsi14": row["rsi14"],
            "close": row["close"],
            "sma20": row["sma20"],
            "ema20": row["ema20"],
            "bbu20": row["bbu20"],
            "bbl20": row["bbl20"],
            "atr20": row["atr20"],
            "roc10": row["roc10"],
            "roc20": row["roc20"],
            "sma50": row["sma50"],
            "vol20": row["vol20"],
            "vol20_median": row["vol20_median"],
            "macd_hist": row["macd_hist"],
            "adx14": row["adx14"]
        })
    df_ind = pd.DataFrame(cycle_indicators)
    
    # Grids of filter parameters
    rsi_thresholds = [60, 62, 64, 66, 68, 70, 72, 75, 80, 999.0]
    rsi_lows = [0.0, 25.0, 30.0, 35.0]
    bb_offsets = [-0.5, 0.0, 0.5, 1.0, 999.0]
    trend_sma50s = [False, True]
    roc10_thresholds = [3.0, 5.0, 7.0, 999.0]
    vol_regimes = [False, True]
    macd_hist_checks = [False, True]
    
    results = []
    
    otm2_pnl = df_legs["OTM2"].values
    otm3_pnl = df_legs["OTM3"].values
    otm4_pnl = df_legs["OTM4"].values
    put_pnl = df_legs["Put1"].values
    
    for rsi_thresh in rsi_thresholds:
        for rsi_low in rsi_lows:
            for bb_offset in bb_offsets:
                for trend_sma50 in trend_sma50s:
                    for roc10_thresh in roc10_thresholds:
                        for vol_regime in vol_regimes:
                            for macd_hist_check in macd_hist_checks:
                                # Construct boolean condition series
                                cond_rsi = df_ind["rsi14"] < rsi_thresh
                                cond_rsi_low = df_ind["rsi14"] > rsi_low
                                
                                if bb_offset == 999.0:
                                    cond_bb = pd.Series(True, index=df_ind.index)
                                else:
                                    cond_bb = df_ind["close"] < (df_ind["bbu20"] + bb_offset * df_ind["atr20"])
                                
                                if trend_sma50:
                                    cond_trend = df_ind["close"] > df_ind["sma50"]
                                else:
                                    cond_trend = pd.Series(True, index=df_ind.index)
                                
                                if roc10_thresh == 999.0:
                                    cond_roc = pd.Series(True, index=df_ind.index)
                                else:
                                    cond_roc = df_ind["roc10"] < roc10_thresh
                                
                                if vol_regime:
                                    cond_vol = df_ind["vol20"] < df_ind["vol20_median"]
                                else:
                                    cond_vol = pd.Series(True, index=df_ind.index)
                                
                                if macd_hist_check:
                                    cond_macd = df_ind["macd_hist"] < 0
                                else:
                                    cond_macd = pd.Series(True, index=df_ind.index)
                                
                                filter_passed = cond_rsi & cond_rsi_low & cond_bb & cond_trend & cond_roc & cond_vol & cond_macd
                                filter_passed_arr = filter_passed.values
                                
                                # P&L calculation based on strategy configuration
                                if no_put_mode and skip_otm4:
                                    cycle_pnls = np.where(filter_passed_arr, otm2_pnl + otm3_pnl, 0.0)
                                elif no_put_mode and not skip_otm4:
                                    cycle_pnls = np.where(filter_passed_arr, otm2_pnl + otm3_pnl, otm4_pnl)
                                elif not no_put_mode and skip_otm4:
                                    cycle_pnls = np.where(filter_passed_arr, otm2_pnl + otm3_pnl + put_pnl, put_pnl)
                                else: # not no_put_mode and not skip_otm4
                                    cycle_pnls = np.where(filter_passed_arr, otm2_pnl + otm3_pnl + put_pnl, otm4_pnl + put_pnl)
                                
                                total_pnl = cycle_pnls.sum()
                                win_rate = np.mean(cycle_pnls > 0)
                                std_pnl = cycle_pnls.std()
                                mean_pnl = cycle_pnls.mean()
                                sharpe = (mean_pnl / std_pnl * np.sqrt(12)) if std_pnl > 0 else 0.0
                                
                                cum_pnl = np.cumsum(cycle_pnls)
                                max_dd = (cum_pnl - np.maximum.accumulate(cum_pnl)).min()
                                
                                placement_rate = np.mean(filter_passed_arr)
                                
                                # Ignore overly restrictive filters
                                if placement_rate < 0.30:
                                    continue
                                
                                score = sharpe * 1000 + total_pnl / 100
                                
                                results.append({
                                    "rsi_thresh": rsi_thresh,
                                    "rsi_low": rsi_low,
                                    "bb_offset": bb_offset,
                                    "trend_sma50": trend_sma50,
                                    "roc10_thresh": roc10_thresh,
                                    "vol_regime": vol_regime,
                                    "macd_hist_check": macd_hist_check,
                                    "placement_rate": placement_rate,
                                    "total_pnl": total_pnl,
                                    "win_rate": win_rate,
                                    "sharpe": sharpe,
                                    "max_dd": max_dd,
                                    "score": score
                                })
                                
    df_res = pd.DataFrame(results)
    df_res = df_res.sort_values(by="score", ascending=False).reset_index(drop=True)
    return df_res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python optimize_filters.py [50|300|500] [--with-put] [--no-skip-otm4]")
        sys.exit(1)
        
    choice = sys.argv[1]
    with_put = "--with-put" in sys.argv
    skip_otm4 = "--no-skip-otm4" not in sys.argv
    
    no_put_mode = not with_put
    
    print(f"Running optimization for {choice}ETF: with_put={with_put}, skip_otm4={skip_otm4}")
    df_res = run_optimization(choice, no_put_mode, skip_otm4)
    
    print("\nTop 10 Filters by Score (Sharpe*1000 + P&L/100):")
    print(df_res.head(10).to_string())
    
    # Save top 5 to csv/txt
    out_name = f"optimization_{choice}ETF_{'withput' if with_put else 'calls_only'}.csv"
    df_res.head(100).to_csv(out_name, index=False)
    print(f"\nSaved top 100 results to {out_name}")
