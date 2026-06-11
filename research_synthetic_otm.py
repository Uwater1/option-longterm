import pandas as pd
import numpy as np
import argparse
import os
import pandas_ta as ta
from datetime import datetime, timedelta
from numba_utils import calculate_research_metrics_numba

# Constants for RMB calculation
MULTIPLIER = 10000
COMMISSION = 2.0  # Per contract
SLIPPAGE = 0.02   # 2% half-spread

# Global paths
PATH_PARQUET = "synthetic_options_300ETF.parquet"
ETF_NAME = "300ETF"
PATH_ETF = "./data/510300_1d.parquet"

def select_etf(choice):
    global ETF_NAME, PATH_PARQUET, PATH_ETF
    if choice == "50":
        ETF_NAME = "50ETF"
        PATH_PARQUET = "synthetic_options_50ETF.parquet"
        PATH_ETF = "./data/50ETF_1d.parquet"
    elif choice == "500":
        ETF_NAME = "500ETF"
        PATH_PARQUET = "synthetic_options_500ETF.parquet"
        PATH_ETF = "./data/500ETF_1d.parquet"
    else:
        ETF_NAME = "300ETF"
        PATH_PARQUET = "synthetic_options_300ETF.parquet"
        PATH_ETF = "./data/510300_1d.parquet"

def load_data():
    if not os.path.exists(PATH_PARQUET):
        print(f"Error: {PATH_PARQUET} not found.")
        return None, None
    
    df = pd.read_parquet(PATH_PARQUET)
    df["Date"] = pd.to_datetime(df["Date"])
    
    # Standardize column name
    if 'Target Expiry' in df.columns:
        df["Target Expiry"] = pd.to_datetime(df["Target Expiry"])
    elif 'Maturity' in df.columns:
        df["Target Expiry"] = pd.to_datetime(df["Maturity"])

    if 'Underlying Price at Date' not in df.columns and 'Underlying_Price' in df.columns:
        df['Underlying Price at Date'] = df['Underlying_Price']
        
    # Load ETF data for filter
    if not os.path.exists(PATH_ETF):
        print(f"Error: {PATH_ETF} not found.")
        return df, None
        
    etf = pd.read_parquet(PATH_ETF)
    etf["date"] = pd.to_datetime(etf["date"])
    etf = etf.set_index("date").sort_index()
    
    # Calculate indicators matching backtest_covered_call.py
    etf["rsi14"] = ta.rsi(etf["close"], length=14)
    bb = ta.bbands(etf["close"], length=20, std=2)
    if bb is not None:
        etf["bbu20"] = bb["BBU_20_2.0_2.0"]
        etf["bbl20"] = bb["BBL_20_2.0_2.0"]
    else:
        etf["bbu20"] = np.nan
        etf["bbl20"] = np.nan
    etf["sma20"] = ta.sma(etf["close"], length=20)
    etf["sma50"] = ta.sma(etf["close"], length=50)
    etf["atr20"] = ta.atr(etf["high"], etf["low"], etf["close"], length=20)
    etf["roc10"] = ta.roc(etf["close"], length=10)
    etf["roc20"] = ta.roc(etf["close"], length=20)
    etf["vol20"] = etf["close"].pct_change().rolling(20).std() * np.sqrt(252)
    etf["vol20_median"] = etf["vol20"].rolling(252).median()
    macd = ta.macd(etf["close"])
    etf["macd_hist"] = macd.iloc[:, 1] if macd is not None else np.nan

    return df, etf

def compute_combo_pnl_by_date(df, etf):
    """
    Compute per-date P&L for:
      - Combo A (Aggressive): Short OTM2 + Short OTM3
      - Combo B (Conservative): Short OTM4
      - Individual levels OTM0-OTM5
    Returns a DataFrame indexed by Date with columns for each combo/level.
    """
    calls = df[df["Option Type"] == "C"].copy()
    if calls.empty:
        return pd.DataFrame()

    # Merge additional indicators from etf (skip cols already in df)
    indicator_cols = ["rsi14", "bbu20", "bbl20", "sma20", "sma50", "atr20",
                      "roc10", "roc20", "vol20", "vol20_median", "macd_hist", "close"]
    available = [c for c in indicator_cols if c in etf.columns and c not in calls.columns]
    if available:
        calls = calls.merge(etf[available], left_on="Date", right_index=True, how="left")
    # Also pick up columns already in calls from earlier merges
    available_all = [c for c in indicator_cols if c in calls.columns]

    records = []
    for date, grp in calls.groupby("Date"):
        s0 = grp["Underlying Price at Date"].iloc[0]
        otm = grp[grp["Strike"] > s0].sort_values("Strike")

        row = {"Date": date, "s0": s0}
        # Copy indicators
        for col in available_all:
            row[col] = grp[col].iloc[0]

        # Compute per-level P&L (levels 0=ATM, 1-5=OTM)
        # ATM: closest strike <= s0
        itm = grp[grp["Strike"] <= s0].sort_values("Strike", ascending=False)
        if not itm.empty:
            r = itm.iloc[0]
            sell_p = r["Price"] * (1 - SLIPPAGE)
            row["L0_pnl"] = r["Exp Ret Short"] * sell_p * MULTIPLIER - COMMISSION
        else:
            row["L0_pnl"] = np.nan

        pnl_vals = otm.apply(
            lambda r: r["Exp Ret Short"] * r["Price"] * (1 - SLIPPAGE) * MULTIPLIER - COMMISSION,
            axis=1
        ).values

        for lv in range(1, 6):
            idx = lv - 1
            if idx < len(pnl_vals):
                row[f"L{lv}_pnl"] = pnl_vals[idx]
            else:
                row[f"L{lv}_pnl"] = np.nan

        # Combos: require at least 3 OTM for comboA, 4 OTM for comboB
        pnl2 = row.get("L2_pnl", np.nan)
        pnl3 = row.get("L3_pnl", np.nan)
        pnl4 = row.get("L4_pnl", np.nan)
        row["comboA"] = (pnl2 if not np.isnan(pnl2) else 0) + (pnl3 if not np.isnan(pnl3) else 0)
        row["comboB"] = pnl4 if not np.isnan(pnl4) else 0
        row["has_3otm"] = len(pnl_vals) >= 3
        row["has_4otm"] = len(pnl_vals) >= 4

        records.append(row)

    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records).set_index("Date").sort_index()


def analyze_combos(date_pnl):
    """Print combination alpha analysis (Combo A, Combo B), both unfiltered and filtered."""
    if date_pnl.empty:
        return

    title = "COMBINATION ALPHA ANALYSIS (SHORT CALL LEGS)"
    print("\n" + "=" * 95)
    print(" " * ((95 - len(title)) // 2) + title)
    print("=" * 95)

    def print_stats(label, vals):
        if vals.empty:
            return
        n = len(vals)
        total = vals.sum()
        avg = vals.mean()
        wins = (vals > 0).sum()
        wr = wins / n
        sharpe = np.sqrt(252) * vals.mean() / vals.std() if vals.std() > 0 else 0
        max_loss = vals.min()
        print(f"  {label:<35}  N={n:>5}  Total={total:>+12,.0f}  Avg={avg:>+8,.1f}  "
              f"WR={wr:.1%}  Sharpe={sharpe:.3f}  MaxLoss={max_loss:>+10,.0f}")

    # --- All dates (no filter) ---
    print("  [All dates - no filter]")
    for label, col in [("Combo A (OTM2+OTM3)", "comboA"), ("Combo B (OTM4)", "comboB")]:
        vals = date_pnl[col].dropna()
        print_stats(label, vals)

    # --- Filter-passed dates (matching individual analysis filter) ---
    if "rsi14" in date_pnl.columns and "bbu20" in date_pnl.columns:
        close = date_pnl["close"] if "close" in date_pnl.columns else date_pnl["s0"]
        rsi = date_pnl["rsi14"]
        bbu = date_pnl["bbu20"]
        filt = (rsi < 70) & (rsi > 30) & (close < bbu)
        filt = filt.fillna(True)
        passed = date_pnl[filt]
        if not passed.empty:
            print(f"\n  [Filter-passed dates: RSI 30-70, Close<BBU (N={len(passed)})]")
            for label, col in [("Combo A (OTM2+OTM3)", "comboA"), ("Combo B (OTM4)", "comboB")]:
                vals = passed[col].dropna()
                print_stats(label, vals)

    # Also print individual levels for reference
    print()
    for lv in range(6):
        col = f"L{lv}_pnl"
        if col not in date_pnl.columns:
            continue
        vals = date_pnl[col].dropna()
        if vals.empty:
            continue
        print_stats(f"Level {lv}", vals)
    print("=" * 95)


def analyze_dynamic_signals(date_pnl):
    """
    Test multiple indicator-based signals for dynamic OTM switching.
    Signal pass (strong) -> Combo A (OTM2+OTM3)
    Signal fail (weak)   -> Combo B (OTM4)
    """
    if date_pnl.empty:
        return

    # Drop rows with NaN combos
    sub = date_pnl[["comboA", "comboB"]].dropna().copy()
    if sub.empty:
        return

    # Copy indicators (already merged in compute_combo_pnl_by_date)
    for col in ["rsi14", "bbu20", "sma20", "sma50", "atr20", "roc10", "roc20",
                "vol20", "vol20_median", "macd_hist", "close"]:
        if col in date_pnl.columns:
            sub[col] = date_pnl.loc[sub.index, col]

    # Compute close-based derived signals
    close = sub["close"] if "close" in sub.columns else pd.Series(np.nan, index=sub.index)
    rsi = sub["rsi14"] if "rsi14" in sub.columns else pd.Series(np.nan, index=sub.index)
    bbu = sub["bbu20"] if "bbu20" in sub.columns else pd.Series(np.nan, index=sub.index)
    atr = sub["atr20"] if "atr20" in sub.columns else pd.Series(np.nan, index=sub.index)
    sma20 = sub["sma20"] if "sma20" in sub.columns else pd.Series(np.nan, index=sub.index)
    sma50 = sub["sma50"] if "sma50" in sub.columns else pd.Series(np.nan, index=sub.index)
    macd_h = sub["macd_hist"] if "macd_hist" in sub.columns else pd.Series(np.nan, index=sub.index)
    roc10 = sub["roc10"] if "roc10" in sub.columns else pd.Series(np.nan, index=sub.index)
    vol20 = sub["vol20"] if "vol20" in sub.columns else pd.Series(np.nan, index=sub.index)
    vol20_med = sub["vol20_median"] if "vol20_median" in sub.columns else pd.Series(np.nan, index=sub.index)

    # Define candidate signals: name -> boolean Series (True = strong -> Combo A)
    signals = {}
    signals["RSI<70"] = rsi < 70
    signals["RSI<66"] = rsi < 66
    signals["RSI<60"] = rsi < 60
    signals["RSI>30"] = rsi > 30
    signals["30<RSI<70"] = (rsi > 30) & (rsi < 70)
    signals["30<RSI<60"] = (rsi > 30) & (rsi < 60)
    signals["Close<BBU"] = close < bbu
    signals["Close<BBU+0.5ATR"] = close < (bbu + 0.5 * atr)
    signals["MACD<0"] = macd_h < 0
    signals["MACD>0"] = macd_h > 0
    signals["Close>SMA50"] = close > sma50
    signals["Close>SMA20"] = close > sma20
    signals["ROC10<3%"] = roc10 < 3.0
    signals["ROC10<7%"] = roc10 < 7.0
    signals["Vol20<VolMed"] = vol20 < vol20_med
    # Composite signals (AND logic, matching backtest patterns)
    signals["RSI<70+BBU"] = (rsi < 70) & (close < bbu)
    signals["RSI<66+BBU"] = (rsi < 66) & (close < bbu)
    signals["RSI>30+BBU+SMA50"] = (rsi > 30) & (close < bbu) & (close > sma50)
    signals["RSI>30+BBU"] = (rsi > 30) & (close < bbu)
    signals["30<RSI<60+ROC<3+LowVol"] = (rsi > 30) & (rsi < 60) & (roc10 < 3.0) & (vol20 < vol20_med)
    signals["RSI<72+MACD<0"] = (rsi < 72) & (macd_h < 0)
    signals["25<RSI<72+MACD<0"] = (rsi > 25) & (rsi < 72) & (macd_h < 0)
    signals["RSI>30+BBU-0.5ATR+ROC<7"] = (rsi > 30) & (close < (bbu - 0.5 * atr)) & (roc10 < 7.0)
    signals["25<RSI<66+BBU+0.5ATR+ROC<7"] = (rsi > 25) & (rsi < 66) & (close < (bbu + 0.5 * atr)) & (roc10 < 7.0)
    signals["RSI>35+BBU+SMA50"] = (rsi > 35) & (close < bbu) & (close > sma50)

    # Baseline: always Combo A, always Combo B
    always_a = sub["comboA"]
    always_b = sub["comboB"]
    n_total = len(sub)

    def summary_stats(vals):
        n = len(vals)
        total = vals.sum()
        avg = vals.mean()
        wins = (vals > 0).sum()
        wr = wins / n if n > 0 else 0
        sharpe = np.sqrt(252) * vals.mean() / vals.std() if n > 1 and vals.std() > 0 else 0
        max_dd = vals.cumsum().cummax() - vals.cumsum()
        max_dd_val = -max_dd.max() if len(max_dd) > 0 else 0
        return n, total, avg, wr, sharpe, max_dd_val

    base_a_n, base_a_total, base_a_avg, base_a_wr, base_a_sharpe, base_a_dd = summary_stats(always_a)
    base_b_n, base_b_total, base_b_avg, base_b_wr, base_b_sharpe, base_b_dd = summary_stats(always_b)
    best_static = max(base_a_total, base_b_total)

    results = []
    for name, mask in signals.items():
        mask_clean = mask.fillna(False)
        n_strong = mask_clean.sum()
        n_weak = n_total - n_strong
        if n_strong < 10 or n_weak < 10:
            continue  # skip unbalanced signals

        dyn_pnl = sub.loc[mask_clean, "comboA"].sum() + sub.loc[~mask_clean, "comboB"].sum()
        dyn_vals = pd.concat([sub.loc[mask_clean, "comboA"], sub.loc[~mask_clean, "comboB"]])
        _, _, dyn_avg, dyn_wr, dyn_sharpe, dyn_dd = summary_stats(dyn_vals)
        placement = n_strong / n_total
        lift = dyn_pnl - best_static

        results.append({
            "Signal": name,
            "Strong%": f"{placement:.0%}",
            "N_strong": int(n_strong),
            "N_weak": int(n_weak),
            "Dyn Total": round(dyn_pnl),
            "Dyn Avg": round(dyn_avg, 1),
            "Dyn WR": f"{dyn_wr:.1%}",
            "Dyn Sharpe": round(dyn_sharpe, 3),
            "MaxDD": round(dyn_dd),
            "Lift": round(lift),
        })

    if not results:
        print("\n  No valid signals found for dynamic analysis.")
        return

    res_df = pd.DataFrame(results).sort_values("Dyn Total", ascending=False)

    title = "DYNAMIC SIGNAL SEARCH (Strong=Combo A / Weak=Combo B)"
    print("\n" + "=" * 120)
    print(" " * ((120 - len(title)) // 2) + title)
    print("=" * 120)

    # Print baselines first
    print(f"  {'BASELINE: Always A':<30}  N={base_a_n:>5}  Total={base_a_total:>+12,.0f}  "
          f"Avg={base_a_avg:>+8,.1f}  WR={base_a_wr:.1%}  Sharpe={base_a_sharpe:.3f}  MaxDD={base_a_dd:>+10,.0f}")
    print(f"  {'BASELINE: Always B':<30}  N={base_b_n:>5}  Total={base_b_total:>+12,.0f}  "
          f"Avg={base_b_avg:>+8,.1f}  WR={base_b_wr:.1%}  Sharpe={base_b_sharpe:.3f}  MaxDD={base_b_dd:>+10,.0f}")
    print("-" * 120)

    print(res_df.to_string(index=False))
    print("=" * 120)

    # Print top 3 detail
    top3 = res_df.head(3)
    if not top3.empty:
        print("\n  TOP 3 SIGNALS DETAIL:")
        for _, row in top3.iterrows():
            print(f"    {row['Signal']}: Strong={row['N_strong']} Weak={row['N_weak']}  "
                  f"Total={row['Dyn Total']:>+10,}  Sharpe={row['Dyn Sharpe']:.3f}  Lift={row['Lift']:>+8,}")


def analyze_synthetic_otm(years=None):
    print(f"Analyzing {ETF_NAME} (Synthetic - Numba Accelerated)...")
    df, etf = load_data()
    if df is None:
        return

    if years:
        latest_date = df["Date"].max()
        start_date = latest_date - pd.Timedelta(days=years * 365)
        df = df[df["Date"] >= start_date].copy()
        print(f"Filtering for data after: {start_date.date()}")

    # Merge filter indicators
    if etf is not None:
        df = df.merge(etf[["rsi14", "bbu20"]], left_on="Date", right_index=True, how="left")
        # Define filter: RSI < 70 AND RSI > 30 AND Spot < Upper BB
        df["Pass Filter"] = (df["rsi14"] < 70.0) & (df["rsi14"] > 30.0) & (df["Underlying Price at Date"] < df["bbu20"])
        # Fill NAs with True to be safe (though shouldn't happen for most of the history)
        df["Pass Filter"] = df["Pass Filter"].fillna(True)
    else:
        df["Pass Filter"] = True

    # Prepare for Numba
    # 1. Sort by Option Type, then Date, then Strike to ensure group continuity
    df = df.sort_values(['Option Type', 'Date', 'Strike']).reset_index(drop=True)
    
    results_data = []
    filter_effectiveness_data = []

    for option_type in ["C", "P"]:
        mask = df["Option Type"] == option_type
        sub_df = df[mask].reset_index(drop=True)
        if sub_df.empty: continue
        
        # Find boundaries where Date changes
        dates = sub_df['Date'].values
        diff = np.where(dates[1:] != dates[:-1])[0] + 1
        boundaries = np.zeros(len(diff) + 2, dtype=np.int64)
        boundaries[0] = 0
        boundaries[1:-1] = diff
        boundaries[-1] = len(sub_df)
        
        # Prepare filter mask per group (Date)
        # We need one boolean per group
        group_filter_mask = np.zeros(len(boundaries) - 1, dtype=bool)
        for g in range(len(boundaries) - 1):
            group_filter_mask[g] = sub_df["Pass Filter"].values[boundaries[g]]
        
        # Prepare arrays for Numba
        strikes = sub_df["Strike"].values.astype(np.float64)
        s0s = sub_df["Underlying Price at Date"].values.astype(np.float64)
        prices = sub_df["Price"].values.astype(np.float64)
        worthless = sub_df["Expire_worthless"].values.astype(np.int8)
        
        if option_type == "C":
            ret_val = sub_df["Exp Ret Short"].values.astype(np.float64)
            is_call = True
        else:
            ret_val = sub_df["Exp Ret Long"].values.astype(np.float64)
            is_call = False
            
        # Execute Numba core aggregation
        # returns (metrics_passed, metrics_filtered)
        metrics_p, metrics_f = calculate_research_metrics_numba(
            strikes, s0s, ret_val, prices, worthless, boundaries, is_call, group_filter_mask
        )
        
        # Process Passed Metrics
        for lv in range(6):
            count = metrics_p[lv, 0]
            if count == 0: continue
            
            pnl_sum = metrics_p[lv, 1]
            wins = metrics_p[lv, 2]
            total_wins = metrics_p[lv, 3]
            min_pnl = metrics_p[lv, 4]
            
            winrate = wins / count
            total_winrate = total_wins / count
            expected_return = pnl_sum / count
            
            results_data.append({
                "Option Type": "Short Call" if option_type == "C" else "Long Put",
                "OTM Level": lv,
                "Samples": int(count),
                "Winrate": f"{winrate:.2%}",
                "Expire Worthless Rate": f"{total_winrate:.2%}",
                "Expected Return (RMB)": round(expected_return, 2),
                "Max Loss (RMB)": round(min_pnl, 2)
            })

        # Process Filtered Metrics (Short Call only)
        if option_type == "C":
            for lv in range(6):
                count = metrics_f[lv, 0]
                if count == 0: continue
                
                pnl_sum = metrics_f[lv, 1]
                wins = metrics_f[lv, 2]
                total_wins = metrics_f[lv, 3]
                
                winrate = wins / count
                total_winrate = total_wins / count
                expected_return = pnl_sum / count
                
                filter_effectiveness_data.append({
                    "OTM Level": lv,
                    "Samples": int(count),
                    "Winrate": f"{winrate:.2%}",
                    "Expire Worthless Rate": f"{total_winrate:.2%}",
                    "Expected Return (RMB)": round(expected_return, 2)
                })
            
    if not results_data:
        print("No valid data found for analysis.")
        return

    df_res = pd.DataFrame(results_data)
    
    title = f"ALPHA RESEARCH (SYNTHETIC): OTM OPTIONS ({ETF_NAME}) (0 = ATM)"
    if years:
        title += f" - Last {years} Years"
        
    print("\n" + "="*95)
    print(" " * ((95 - len(title)) // 2) + title)
    print("="*95)
    print(df_res.to_string(index=False))
    print("="*95)
    
    if filter_effectiveness_data:
        f_df = pd.DataFrame(filter_effectiveness_data)
        f_title = "FILTER EFFECTIVENESS (FILTERED OUT SHORT CALL SAMPLES)"
        print("\n" + "="*95)
        print(" " * ((95 - len(f_title)) // 2) + f_title)
        print("="*95)
        print(f_df.to_string(index=False))
        print("="*95)

    # ── Combination Alpha Analysis ──────────────────────────────────────────
    if etf is not None:
        date_pnl = compute_combo_pnl_by_date(df, etf)
        if not date_pnl.empty:
            if years:
                latest = date_pnl.index.max()
                cutoff = latest - pd.Timedelta(days=years * 365)
                date_pnl = date_pnl[date_pnl.index >= cutoff]
            analyze_combos(date_pnl)
            analyze_dynamic_signals(date_pnl)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Research Synthetic OTM Alpha (Short Call & Long Put).")
    parser.add_argument("-t", "--years", type=int, help="Limit analysis to last N years")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500"], default="300", help="ETF choice (default: 300)")
    args = parser.parse_args()
    
    select_etf(args.etf)
    analyze_synthetic_otm(years=args.years)
