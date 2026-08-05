"""
Download 1-minute interval ETF prices from rqdatac and save as separate compressed Parquet files.
Run: python3 download_1m_data.py
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
        "symbol": "510300.XSHG",
        "output": "510300_1m.parquet",
    },
    "50ETF": {
        "symbol": "510050.XSHG",
        "output": "50ETF_1m.parquet",
    },
    "500ETF": {
        "symbol": "510500.XSHG",
        "output": "500ETF_1m.parquet",
    },
    "588000ETF": {
        "symbol": "588000.XSHG",
        "output": "588000ETF_1m.parquet",
    },
    "159915ETF": {
        "symbol": "159915.XSHE",
        "output": "159915ETF_1m.parquet",
    },
}

def main():
    rq.init()
    print("rqdatac connected.\n")

    for name, cfg in UNDERLYINGS.items():
        symbol = cfg["symbol"]
        output_file = cfg["output"]
        output_path = os.path.join(DATA_DIR, output_file)
        
        print(f"=== Fetching 1m Data for {name} ({symbol}) ===")
        inst_info = rq.instruments(symbol)
        listed_date = pd.Timestamp(inst_info.listed_date)
        start_date = max(pd.Timestamp("2010-01-04"), listed_date)
        end_date = pd.Timestamp.now()
        
        if os.path.exists(output_path):
            existing = pd.read_parquet(output_path)
            existing["datetime"] = pd.to_datetime(existing["datetime"])
            last_dt = existing["datetime"].max()
            start_date = last_dt.floor("D")
            print(f"  Existing 1m max datetime: {last_dt}, updating from {start_date.date()} to {end_date.date()}")
        else:
            existing = pd.DataFrame()
            inst_info = rq.instruments(symbol)
            listed_date = pd.Timestamp(inst_info.listed_date)
            start_date = max(pd.Timestamp("2010-01-04"), listed_date)
            print(f"  Listing date: {listed_date.date()}, downloading from {start_date.date()} to {end_date.date()}")
        
        years = range(start_date.year, end_date.year + 1)
        etf_dfs = []
        for year in years:
            year_start = max(start_date, pd.Timestamp(f"{year}-01-01"))
            year_end = min(end_date, pd.Timestamp(f"{year}-12-31"))
            if year_start > year_end:
                continue
            
            print(f"    Downloading {year_start.date()} to {year_end.date()}...")
            try:
                df = rq.get_price(
                    symbol,
                    start_date=year_start.strftime("%Y-%m-%d"),
                    end_date=year_end.strftime("%Y-%m-%d"),
                    frequency="1m",
                    adjust_type="none"
                )
                if df is not None and not df.empty:
                    df = df.reset_index()
                    etf_dfs.append(df)
                    print(f"      Got {len(df)} rows.")
                else:
                    print("      No data returned.")
            except Exception as e:
                print(f"      Error fetching data: {e}")

        if etf_dfs:
            new_etf = pd.concat(etf_dfs, ignore_index=True)
            new_etf.columns = [c.lower() if c != "order_book_id" else c for c in new_etf.columns]
            new_etf["datetime"] = pd.to_datetime(new_etf["datetime"])
            
            if not existing.empty:
                combined_etf = pd.concat([existing, new_etf], ignore_index=True)
            else:
                combined_etf = new_etf

            combined_etf = combined_etf.drop_duplicates(subset=["order_book_id", "datetime"], keep="last")
            combined_etf = combined_etf.sort_values(["order_book_id", "datetime"])
            
            os.makedirs(DATA_DIR, exist_ok=True)
            print(f"  Saving to {output_path} (shape: {combined_etf.shape})...")
            combined_etf.to_parquet(
                output_path,
                index=False,
                compression="zstd",
                compression_level=5
            )
            print(f"  Saved successfully.\n")
        else:
            print(f"  1m Data already up to date or no new rows for {name}\n")

    print("All tasks finished successfully.")

if __name__ == "__main__":
    main()
