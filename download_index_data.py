"""
Download 1d, 5m, and 1m index data from rqdatac.
Run: python3 download_index_data.py
"""
import sys
import warnings
warnings.filterwarnings("ignore")

import rqdatac as rq
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

INDICES = {
    "000016.XSHG": {
        "name": "SSE 50",
        "file_1d": "000016_1d.parquet",
        "file_5m": "000016_5m.parquet",
        "file_1m": "000016_1m.parquet"
    },
    "000300.XSHG": {
        "name": "CSI 300",
        "file_1d": "000300_1d.parquet",
        "file_5m": "000300_5m.parquet",
        "file_1m": "000300_1m.parquet"
    },
    "000905.XSHG": {
        "name": "CSI 500",
        "file_1d": "000905_1d.parquet",
        "file_5m": "000905_5m.parquet",
        "file_1m": "000905_1m.parquet"
    },
    "000688.XSHG": {
        "name": "STAR 50",
        "file_1d": "000688_1d.parquet",
        "file_5m": "000688_5m.parquet",
        "file_1m": "000688_1m.parquet"
    },
    "399006.XSHE": {
        "name": "ChiNext",
        "file_1d": "399006_1d.parquet",
        "file_5m": "399006_5m.parquet",
        "file_1m": "399006_1m.parquet"
    }
}

def main():
    rq.init()
    print("rqdatac connected.\n")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    end_date = pd.Timestamp.now()
    
    for symbol, cfg in INDICES.items():
        name = cfg["name"]
        print(f"=== Process {name} ({symbol}) ===")
        if symbol == "000688.XSHG":
            start_date = pd.Timestamp("2019-12-31")
        else:
            inst_info = rq.instruments(symbol)
            listed_date = pd.Timestamp(inst_info.listed_date)
            start_date = max(pd.Timestamp("2015-01-05"), listed_date)
        
        # 1. Download 1d data
        path_1d = os.path.join(DATA_DIR, cfg["file_1d"])
        print(f"  Downloading 1d data from {start_date.date()} to {end_date.date()}...")
        df_1d = rq.get_price(
            symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            frequency="1d",
            adjust_type="none"
        )
        if df_1d is not None and not df_1d.empty:
            df_1d = df_1d.reset_index()
            df_1d.columns = [c.lower() if c != "order_book_id" else c for c in df_1d.columns]
            df_1d["date"] = pd.to_datetime(df_1d["date"])
            df_1d.to_parquet(path_1d, index=False)
            print(f"  Saved 1d to {path_1d} (shape: {df_1d.shape})")
        else:
            print("  Warning: 1d data returned empty")

        # 2. Download 5m data (year-by-year)
        path_5m = os.path.join(DATA_DIR, cfg["file_5m"])
        print(f"  Downloading 5m data from {start_date.date()} to {end_date.date()}...")
        years = range(start_date.year, end_date.year + 1)
        dfs_5m = []
        for year in years:
            year_start = max(start_date, pd.Timestamp(f"{year}-01-01"))
            year_end = min(end_date, pd.Timestamp(f"{year}-12-31"))
            if year_start > year_end:
                continue
            print(f"    Downloading 5m for {year}...")
            try:
                df = rq.get_price(
                    symbol,
                    start_date=year_start.strftime("%Y-%m-%d"),
                    end_date=year_end.strftime("%Y-%m-%d"),
                    frequency="5m",
                    adjust_type="none"
                )
                if df is not None and not df.empty:
                    df = df.reset_index()
                    dfs_5m.append(df)
                    print(f"      Got {len(df)} rows.")
            except Exception as e:
                print(f"      Error fetching 5m for {year}: {e}")
                
        if dfs_5m:
            df_5m = pd.concat(dfs_5m, ignore_index=True)
            df_5m.columns = [c.lower() if c != "order_book_id" else c for c in df_5m.columns]
            df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
            df_5m = df_5m.sort_values(["order_book_id", "datetime"])
            df_5m.to_parquet(path_5m, index=False)
            print(f"  Saved 5m to {path_5m} (shape: {df_5m.shape})")
        else:
            print("  Warning: 5m data returned empty")

        # 3. Download 1m data (year-by-year)
        path_1m = os.path.join(DATA_DIR, cfg["file_1m"])
        print(f"  Downloading 1m data from {start_date.date()} to {end_date.date()}...")
        dfs_1m = []
        for year in years:
            year_start = max(start_date, pd.Timestamp(f"{year}-01-01"))
            year_end = min(end_date, pd.Timestamp(f"{year}-12-31"))
            if year_start > year_end:
                continue
            print(f"    Downloading 1m for {year}...")
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
                    dfs_1m.append(df)
                    print(f"      Got {len(df)} rows.")
            except Exception as e:
                print(f"      Error fetching 1m for {year}: {e}")
                
        if dfs_1m:
            df_1m = pd.concat(dfs_1m, ignore_index=True)
            df_1m.columns = [c.lower() if c != "order_book_id" else c for c in df_1m.columns]
            df_1m["datetime"] = pd.to_datetime(df_1m["datetime"])
            df_1m = df_1m.sort_values(["order_book_id", "datetime"])
            df_1m.to_parquet(path_1m, index=False, compression="zstd", compression_level=5)
            print(f"  Saved 1m to {path_1m} (shape: {df_1m.shape})")
        else:
            print("  Warning: 1m data returned empty")
        print()

    print("All downloads completed successfully.")

if __name__ == "__main__":
    main()
