"""Download CFFEX index futures 5m data from rqdatac.

Continuous contracts:
- IH88 (SSE 50 Futures) -> 50ETF
- IF88 (CSI 300 Futures) -> 300ETF / 510300
- IC88 (CSI 500 Futures) -> 500ETF
- IM88 (CSI 1000 Futures) -> Small-cap benchmark proxy
"""
import os
import sys
from pathlib import Path
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"

FUTURES_MAP = {
    "50ETF": "IH88",
    "300ETF": "IF88",
    "500ETF": "IC88",
}

def download_futures():
    try:
        import rqdatac as rq
        rq.init()
        print("rqdatac connected successfully.")
    except Exception as e:
        print(f"rqdatac init warning: {e}")
        return

    end_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    start_date = "2020-01-01"

    for etf, fut_symbol in FUTURES_MAP.items():
        out_path = DATA_DIR / f"{fut_symbol}_5m.parquet"
        print(f"Downloading 5m bars for {fut_symbol} ({etf})...")
        try:
            df = rq.get_price(fut_symbol, start_date=start_date, end_date=end_date, frequency="5m", fields=["open", "high", "low", "close", "volume"])
            if df is not None and not df.empty:
                if isinstance(df.index, pd.MultiIndex):
                    df = df.reset_index(level=0, drop=True)
                df = df.reset_index()
                if "index" in df.columns:
                    df.rename(columns={"index": "datetime"}, inplace=True)
                df.to_parquet(out_path)
                print(f"Saved {len(df)} rows to {out_path}")
            else:
                print(f"No data returned for {fut_symbol}")
        except Exception as err:
            print(f"Error fetching {fut_symbol}: {err}")

if __name__ == "__main__":
    download_futures()
