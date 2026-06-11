"""
Download 5-minute interval options and ETF price data from rqdatac.
Only downloads for the active monthly option contract during its front-month period (1 month from expiry).
Run: python3 download_5m_data.py
"""
import sys
import warnings
warnings.filterwarnings("ignore")

import rqdatac as rq
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

UNDERLYINGS = {
    "300ETF": {
        "underlying": "510300.XSHG",
        "instruments": "300ETF_instruments.parquet",
        "prices": "300ETF_historical_prices.parquet",
        "etf_1d": "510300_1d.parquet",
        "etf_5m": "510300_5m.parquet",
        "opt_5m": "300ETF_historical_prices_5m.parquet",
    },
    "50ETF": {
        "underlying": "510050.XSHG",
        "instruments": "50ETF_instruments.parquet",
        "prices": "50ETF_historical_prices.parquet",
        "etf_1d": "50ETF_1d.parquet",
        "etf_5m": "50ETF_5m.parquet",
        "opt_5m": "50ETF_historical_prices_5m.parquet",
    },
    "500ETF": {
        "underlying": "510500.XSHG",
        "instruments": "500ETF_instruments.parquet",
        "prices": "500ETF_historical_prices.parquet",
        "etf_1d": "500ETF_1d.parquet",
        "etf_5m": "500ETF_5m.parquet",
        "opt_5m": "500ETF_historical_prices_5m.parquet",
    },
}

def get_cycles(opt, etf):
    trading_days_set = set(etf.index.normalize())
    opt_trading_days = sorted(opt["date"].unique())

    expiries_cp = (
        opt.groupby(["maturity_date", "option_type"])["order_book_id"]
        .nunique()
        .unstack("option_type")
        .dropna()
        .index.tolist()
    )
    expiries_cp = sorted(expiries_cp)

    cycles = []
    for i, expiry in enumerate(expiries_cp):
        if i == 0:
            entry = opt_trading_days[0]
        else:
            prev_expiry = expiries_cp[i - 1]
            candidates = [d for d in opt_trading_days if d > prev_expiry]
            if not candidates:
                continue
            entry = candidates[0]

        if entry >= expiry:
            continue

        entry_norm = pd.Timestamp(entry).normalize()
        if entry_norm not in trading_days_set:
            continue

        cycles.append({"entry_date": entry, "expiry_date": expiry})

    return cycles

def main():
    rq.init()
    print("rqdatac connected.\n")

    for name, cfg in UNDERLYINGS.items():
        print(f"=== Downloading 5m Data for {name} ===")
        
        inst_path = os.path.join(DATA_DIR, cfg["instruments"])
        prices_path = os.path.join(DATA_DIR, cfg["prices"])
        etf_path = os.path.join(DATA_DIR, cfg["etf_1d"])
        
        if not (os.path.exists(inst_path) and os.path.exists(prices_path) and os.path.exists(etf_path)):
            print(f"  Skipping {name} (daily parquet files missing)")
            continue

        # Load daily data
        inst = pd.read_parquet(inst_path)
        opt = pd.read_parquet(prices_path)
        etf = pd.read_parquet(etf_path)

        inst["maturity_date"] = pd.to_datetime(inst["maturity_date"])
        opt["date"] = pd.to_datetime(opt["date"])
        etf["date"] = pd.to_datetime(etf["date"])

        inst_slim = inst[["order_book_id", "maturity_date", "option_type"]].drop_duplicates()
        opt = opt.merge(inst_slim, on="order_book_id", how="left")
        etf = etf.set_index("date").sort_index()

        cycles = get_cycles(opt, etf)
        if not cycles:
            print(f"  No cycles found for {name}")
            continue

        print(f"  Found {len(cycles)} cycles. Range: {cycles[0]['entry_date'].date()} to {cycles[-1]['expiry_date'].date()}")

        # 1. Download ETF 5m prices
        etf_5m_path = os.path.join(DATA_DIR, cfg["etf_5m"])
        start_date = cycles[0]["entry_date"]
        # Use latest date or end of last cycle
        end_date = min(pd.Timestamp.now(), cycles[-1]["expiry_date"])
        print(f"  Downloading ETF 5m prices from {start_date.date()} to {end_date.date()}...")
        
        etf_df = rq.get_price(
            cfg["underlying"],
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            frequency="5m",
            adjust_type="none"
        )
        
        if etf_df is not None and not etf_df.empty:
            etf_df = etf_df.reset_index()
            etf_df.columns = [c.lower() if c != "order_book_id" else c for c in etf_df.columns]
            etf_df["datetime"] = pd.to_datetime(etf_df["datetime"])
            etf_df.to_parquet(etf_5m_path, index=False)
            print(f"  Saved ETF 5m prices to {etf_5m_path} (shape: {etf_df.shape})")
        else:
            print("  Warning: ETF 5m prices download returned empty")

        # 2. Download option contracts 5m prices
        opt_5m_path = os.path.join(DATA_DIR, cfg["opt_5m"])
        all_opt_dfs = []

        print("  Downloading option 5m prices cycle-by-cycle...")
        for idx, cyc in enumerate(cycles):
            entry = cyc["entry_date"]
            expiry = cyc["expiry_date"]
            
            # Find contracts maturing at this expiry
            # We filter from instruments to get all strikes of C and P
            cycle_contracts = inst[inst["maturity_date"] == expiry]["order_book_id"].unique().tolist()
            if not cycle_contracts:
                continue

            if idx % 10 == 0 or idx == len(cycles) - 1:
                print(f"    Cycle {idx+1}/{len(cycles)}: {entry.date()} -> {expiry.date()} ({len(cycle_contracts)} contracts)")

            # Fetch 5m data for this cycle's active period
            px = rq.get_price(
                cycle_contracts,
                start_date=entry.strftime("%Y-%m-%d"),
                end_date=expiry.strftime("%Y-%m-%d"),
                frequency="5m"
            )

            if px is not None and not px.empty:
                px = px.reset_index()
                px.columns = [c.lower() if c != "order_book_id" else c for c in px.columns]
                px["datetime"] = pd.to_datetime(px["datetime"])
                all_opt_dfs.append(px)

        if all_opt_dfs:
            combined_opt = pd.concat(all_opt_dfs, ignore_index=True)
            combined_opt = combined_opt.drop_duplicates(subset=["order_book_id", "datetime"])
            combined_opt = combined_opt.sort_values(["order_book_id", "datetime"])
            combined_opt.to_parquet(opt_5m_path, index=False)
            print(f"  Saved option 5m prices to {opt_5m_path} (shape: {combined_opt.shape})")
        else:
            print("  Warning: Option 5m prices download returned empty")
        print()

    print("All tasks finished successfully.")

if __name__ == "__main__":
    main()
