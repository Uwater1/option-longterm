"""
Data Quality Audit — Detect anomalous option prices (vectorized)
================================================================
1. OTM options with high prices near maturity (last 3 trading days)
2. ITM options trading at near-zero prices (close <= 0.001)
3. ITM options with close = 0 exactly
4. General sanity checks
"""

import pandas as pd
import numpy as np

ETF_CONFIG = {
    "300ETF": {
        "inst": "./data/300ETF_instruments.parquet",
        "opt": "./data/300ETF_historical_prices.parquet",
        "etf": "./data/510300_1d.parquet",
    },
    "50ETF": {
        "inst": "./data/50ETF_instruments.parquet",
        "opt": "./data/50ETF_historical_prices.parquet",
        "etf": "./data/50ETF_1d.parquet",
    },
    "500ETF": {
        "inst": "./data/500ETF_instruments.parquet",
        "opt": "./data/500ETF_historical_prices.parquet",
        "etf": "./data/500ETF_1d.parquet",
    },
}

def load_data(etf_name):
    cfg = ETF_CONFIG[etf_name]
    inst = pd.read_parquet(cfg["inst"])
    opt = pd.read_parquet(cfg["opt"])
    etf = pd.read_parquet(cfg["etf"])
    
    inst["maturity_date"] = pd.to_datetime(inst["maturity_date"])
    opt["date"] = pd.to_datetime(opt["date"])
    etf["date"] = pd.to_datetime(etf["date"])
    
    inst_slim = inst[["order_book_id", "maturity_date", "option_type"]].drop_duplicates()
    opt = opt.merge(inst_slim, on="order_book_id", how="left")
    
    # Merge ETF close price
    etf_slim = etf[["date", "close"]].rename(columns={"close": "spot", "date": "date"})
    opt = opt.merge(etf_slim, on="date", how="left")
    
    # Compute DTE
    opt["DTE"] = (opt["maturity_date"] - opt["date"]).dt.days
    
    # Compute intrinsic and moneyness
    is_call = opt["option_type"] == "C"
    is_put = opt["option_type"] == "P"
    
    opt["intrinsic"] = np.where(
        is_call,
        np.maximum(opt["spot"] - opt["strike_price"], 0),
        np.where(is_put, np.maximum(opt["strike_price"] - opt["spot"], 0), 0)
    )
    
    opt["is_itm"] = np.where(is_call, opt["strike_price"] < opt["spot"],
                              np.where(is_put, opt["strike_price"] > opt["spot"], False))
    opt["is_otm"] = np.where(is_call, opt["strike_price"] > opt["spot"],
                              np.where(is_put, opt["strike_price"] < opt["spot"], False))
    
    opt["moneyness_pct"] = np.abs(opt["strike_price"] - opt["spot"]) / opt["spot"] * 100
    
    return opt

def audit_otm_high_price_at_maturity(opt, etf_name):
    """Find OTM options with suspiciously high prices in last 3 trading days before expiry."""
    print(f"\n{'='*80}")
    print(f"[{etf_name}] CHECK 1: OTM options with HIGH prices near maturity (last 3 days)")
    print(f"{'='*80}")
    
    # Mark last 3 trading days per contract
    opt_sorted = opt.sort_values(["order_book_id", "maturity_date", "option_type", "date"])
    opt_sorted["rank_from_end"] = opt_sorted.groupby(["order_book_id", "maturity_date", "option_type"])["date"].rank(ascending=False, method="first")
    last3 = opt_sorted[opt_sorted["rank_from_end"] <= 3].copy()
    
    # Filter: OTM and price > 0.01
    otm_high = last3[(last3["is_otm"]) & (last3["close"] > 0.01)].copy()
    
    if otm_high.empty:
        print("  No OTM options with price > 0.01 near maturity found.")
        return
    
    print(f"  Total OTM near-maturity records with price > 0.01: {len(otm_high)}")
    
    # Deeply OTM (>1%)
    deep_otm = otm_high[otm_high["moneyness_pct"] > 1.0].sort_values("close", ascending=False)
    print(f"  Deeply OTM (>1% OTM) with price > 0.01: {len(deep_otm)}")
    
    if len(deep_otm) > 0:
        show_cols = ["order_book_id", "option_type", "date", "maturity_date", "DTE",
                      "strike_price", "spot", "close", "moneyness_pct", "intrinsic", "volume", "open_interest"]
        print(f"\n  TOP 30 Deeply OTM with highest prices:")
        print(deep_otm[show_cols].head(30).to_string(index=False))
    
    # Last day specifically (DTE <= 1)
    dte0_otm = otm_high[otm_high["DTE"] <= 1].sort_values("close", ascending=False)
    if len(dte0_otm) > 0:
        print(f"\n  OTM on LAST DAY (DTE<=1) with price > 0.01: {len(dte0_otm)}")
        print(dte0_otm[show_cols].head(30).to_string(index=False))

def audit_itm_low_price(opt, etf_name):
    """Find ITM options trading at near-zero prices."""
    print(f"\n{'='*80}")
    print(f"[{etf_name}] CHECK 2: ITM options with NEAR-ZERO prices (0 < close <= 0.001)")
    print(f"{'='*80}")
    
    itm_low = opt[(opt["is_itm"]) & (opt["close"] > 0) & (opt["close"] <= 0.001)].copy()
    
    if itm_low.empty:
        print("  No ITM options with near-zero prices found.")
        return
    
    itm_low = itm_low.sort_values("intrinsic", ascending=False)
    show_cols = ["order_book_id", "option_type", "date", "maturity_date", "DTE",
                  "strike_price", "spot", "close", "moneyness_pct", "intrinsic", "volume", "open_interest"]
    
    print(f"  Total ITM records with 0 < close <= 0.001: {len(itm_low)}")
    print(f"\n  TOP 30 by intrinsic value (biggest mispricing):")
    print(itm_low[show_cols].head(30).to_string(index=False))
    
    print(f"\n  Summary:")
    print(f"    Unique contracts affected: {itm_low['order_book_id'].nunique()}")
    print(f"    Date range: {itm_low['date'].min()} to {itm_low['date'].max()}")
    print(f"    Max intrinsic value: {itm_low['intrinsic'].max():.4f}")
    print(f"    Median intrinsic: {itm_low['intrinsic'].median():.4f}")
    print(f"    Mean DTE: {itm_low['DTE'].mean():.1f}")

def audit_itm_zero_price(opt, etf_name):
    """Find ITM options with close = 0 exactly."""
    print(f"\n{'='*80}")
    print(f"[{etf_name}] CHECK 2b: ITM options with close = 0 (exactly)")
    print(f"{'='*80}")
    
    itm_zero = opt[(opt["is_itm"]) & (opt["close"] == 0)].copy()
    
    if itm_zero.empty:
        print("  No ITM options with close = 0 found.")
        return
    
    itm_zero = itm_zero.sort_values("intrinsic", ascending=False)
    show_cols = ["order_book_id", "option_type", "date", "maturity_date", "DTE",
                  "strike_price", "spot", "close", "intrinsic", "volume", "open_interest"]
    
    print(f"  Total ITM records with close = 0: {len(itm_zero)}")
    print(itm_zero[show_cols].head(20).to_string(index=False))

def audit_general_sanity(opt, etf_name):
    """General price sanity checks."""
    print(f"\n{'='*80}")
    print(f"[{etf_name}] CHECK 3: General price sanity")
    print(f"{'='*80}")
    
    neg = opt[opt["close"] < 0]
    print(f"  Negative close prices: {len(neg)}")
    
    # Call price > spot, Put price > strike
    call_over = opt[(opt["option_type"] == "C") & (opt["close"] > opt["spot"] * 1.01)]
    put_over = opt[(opt["option_type"] == "P") & (opt["close"] > opt["strike_price"] * 1.01)]
    print(f"  Call close > spot (theoretical max violation): {len(call_over)}")
    print(f"  Put close > strike (theoretical max violation): {len(put_over)}")
    
    # ITM option price < intrinsic (arbitrage)
    itm_underpriced = opt[(opt["is_itm"]) & (opt["close"] < opt["intrinsic"] * 0.5) & (opt["close"] > 0)]
    print(f"  ITM options priced below 50% of intrinsic: {len(itm_underpriced)}")
    if len(itm_underpriced) > 0:
        show_cols = ["order_book_id", "option_type", "date", "DTE", "strike_price", "spot", "close", "intrinsic", "volume"]
        print(itm_underpriced.sort_values("intrinsic", ascending=False)[show_cols].head(20).to_string(index=False))
    
    # Zero volume with nonzero close
    zero_vol = opt[(opt["volume"] == 0) & (opt["close"] > 0)]
    print(f"  Zero-volume days with close > 0: {len(zero_vol)} ({len(zero_vol)/len(opt)*100:.1f}%)")

def audit_monotonicity(opt, etf_name):
    """Check call/put price monotonicity across strikes for same date+expiry.
    Call: lower strike should have higher (or equal) price.
    Put: higher strike should have higher (or equal) price.
    Uses small tolerance to accept tiny mispricing from bid-ask noise.
    """
    print(f"\n{'='*80}")
    print(f"[{etf_name}] CHECK 4: Strike-price monotonicity")
    print(f"{'='*80}")
    
    TOL = 0.005  # accept up to 0.005 RMB mispricing (tiny bid-ask noise)
    violations_call = []
    violations_put = []
    
    # Group by (date, maturity_date, option_type) and check adjacent strikes
    for (date, mat, otype), grp in opt.groupby(["date", "maturity_date", "option_type"]):
        if len(grp) < 2:
            continue
        grp_sorted = grp.sort_values("strike_price").reset_index(drop=True)
        strikes = grp_sorted["strike_price"].values
        prices = grp_sorted["close"].values
        volumes = grp_sorted["volume"].values
        ois = grp_sorted["open_interest"].values
        
        for i in range(len(strikes) - 1):
            if otype == "C":
                # Call: price[i] should >= price[i+1] (lower strike = higher price)
                if prices[i] + TOL < prices[i + 1]:
                    violations_call.append({
                        "date": date, "maturity": mat,
                        "K_low": strikes[i], "P_low": prices[i], "V_low": volumes[i],
                        "K_high": strikes[i+1], "P_high": prices[i+1], "V_high": volumes[i+1],
                        "gap": prices[i+1] - prices[i],
                    })
            else:
                # Put: price[i] should <= price[i+1] (higher strike = higher price)
                if prices[i] > prices[i + 1] + TOL:
                    violations_put.append({
                        "date": date, "maturity": mat,
                        "K_low": strikes[i], "P_low": prices[i], "V_low": volumes[i],
                        "K_high": strikes[i+1], "P_high": prices[i+1], "V_high": volumes[i+1],
                        "gap": prices[i] - prices[i+1],
                    })
    
    # Call violations
    if violations_call:
        cdf = pd.DataFrame(violations_call).sort_values("gap", ascending=False)
        print(f"\n  CALL violations (lower strike has LOWER price, tol={TOL}): {len(cdf)}")
        print(f"    Unique dates affected: {cdf['date'].nunique()}")
        print(f"    Top 20 by gap size:")
        print(cdf.head(20).to_string(index=False))
    else:
        print(f"\n  CALL violations: 0 (all monotonic within tol={TOL})")
    
    # Put violations
    if violations_put:
        pdf = pd.DataFrame(violations_put).sort_values("gap", ascending=False)
        print(f"\n  PUT violations (higher strike has LOWER price, tol={TOL}): {len(pdf)}")
        print(f"    Unique dates affected: {pdf['date'].nunique()}")
        print(f"    Top 20 by gap size:")
        print(pdf.head(20).to_string(index=False))
    else:
        print(f"\n  PUT violations: 0 (all monotonic within tol={TOL})")


def main():
    for etf_name in ["50ETF", "300ETF", "500ETF"]:
        print(f"\n{'#'*80}")
        print(f"# AUDITING {etf_name}")
        print(f"{'#'*80}")
        
        opt = load_data(etf_name)
        print(f"  Loaded {len(opt)} option records")
        
        audit_otm_high_price_at_maturity(opt, etf_name)
        audit_itm_low_price(opt, etf_name)
        audit_itm_zero_price(opt, etf_name)
        audit_general_sanity(opt, etf_name)
        audit_monotonicity(opt, etf_name)

if __name__ == "__main__":
    main()
