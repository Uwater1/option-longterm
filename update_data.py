"""
Update local Parquet database with latest data from rqdatac.
Run: python3 update_data.py
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
    },
    "50ETF": {
        "underlying": "510050.XSHG",
        "instruments": "50ETF_instruments.parquet",
        "prices": "50ETF_historical_prices.parquet",
        "etf_1d": "50ETF_1d.parquet",
    },
    "500ETF": {
        "underlying": "510500.XSHG",
        "instruments": "500ETF_instruments.parquet",
        "prices": "500ETF_historical_prices.parquet",
        "etf_1d": "500ETF_1d.parquet",
    },
}


def update_instruments(cfg):
    path = os.path.join(DATA_DIR, cfg["instruments"])
    underlying = cfg["underlying"]

    all_opt = rq.all_instruments("Option")
    inst = all_opt[all_opt["underlying_symbol"] == underlying].copy()

    for col in ["listed_date", "de_listed_date", "maturity_date"]:
        if col in inst.columns:
            inst[col] = pd.to_datetime(inst[col])

    inst.to_parquet(path, index=False)
    print(f"  Instruments: {len(inst)} contracts -> {path}")
    return inst


def update_etf_prices(cfg):
    path = os.path.join(DATA_DIR, cfg["etf_1d"])
    underlying = cfg["underlying"]

    existing = pd.read_parquet(path)
    existing["date"] = pd.to_datetime(existing["date"])
    last_date = existing["date"].max()
    start = last_date + pd.Timedelta(days=1)

    etf = rq.get_price(
        underlying, start_date=start.strftime("%Y-%m-%d"),
        end_date=pd.Timestamp.now().strftime("%Y-%m-%d"),
        frequency="1d"
    )

    if etf is None or etf.empty:
        print(f"  ETF prices: no new data since {last_date.date()}")
        return

    etf = etf.reset_index()
    etf.columns = [c.lower() if c != "order_book_id" else c for c in etf.columns]
    if "date" not in etf.columns and "datetime" in etf.columns:
        etf.rename(columns={"datetime": "date"}, inplace=True)
    etf["date"] = pd.to_datetime(etf["date"])

    combined = pd.concat([existing, etf], ignore_index=True)
    combined = combined.drop_duplicates(subset=["date"], keep="last").sort_values("date")
    combined.to_parquet(path, index=False)
    print(f"  ETF prices: +{len(etf)} days ({last_date.date()} -> {combined['date'].max().date()}) -> {path}")


def update_option_prices(cfg, inst):
    path = os.path.join(DATA_DIR, cfg["prices"])
    underlying = cfg["underlying"]

    existing = pd.read_parquet(path)
    existing["date"] = pd.to_datetime(existing["date"])
    last_date = existing["date"].max()

    start = last_date + pd.Timedelta(days=1)
    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    new_contracts = inst[inst["listed_date"] > last_date]["order_book_id"].tolist()

    old_contracts = existing["order_book_id"].unique().tolist()
    contracts_to_update = [c for c in old_contracts if c in inst["order_book_id"].values]

    all_new = []
    batch_size = 50

    if new_contracts:
        print(f"  Fetching prices for {len(new_contracts)} new contracts...")
        for i in range(0, len(new_contracts), batch_size):
            batch = new_contracts[i:i + batch_size]
            px = rq.get_price(batch, start_date=start.strftime("%Y-%m-%d"), end_date=today)
            if px is not None and not px.empty:
                all_new.append(px.reset_index())

    print(f"  Fetching price updates for {len(contracts_to_update)} existing contracts since {start.date()}...")
    for i in range(0, len(contracts_to_update), batch_size):
        batch = contracts_to_update[i:i + batch_size]
        px = rq.get_price(batch, start_date=start.strftime("%Y-%m-%d"), end_date=today)
        if px is not None and not px.empty:
            all_new.append(px.reset_index())

    if not all_new:
        print(f"  Option prices: no new data since {last_date.date()}")
        return

    new_df = pd.concat(all_new, ignore_index=True)
    new_df.columns = [c.lower() if c != "order_book_id" else c for c in new_df.columns]
    if "date" not in new_df.columns and "datetime" in new_df.columns:
        new_df.rename(columns={"datetime": "date"}, inplace=True)
    new_df["date"] = pd.to_datetime(new_df["date"])

    combined = pd.concat([existing, new_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["order_book_id", "date"], keep="last")
    combined = combined.sort_values(["order_book_id", "date"])
    combined.to_parquet(path, index=False)
    print(f"  Option prices: +{len(new_df)} rows ({last_date.date()} -> {combined['date'].max().date()}) -> {path}")


def main():
    rq.init()
    print("rqdatac connected.\n")

    for name, cfg in UNDERLYINGS.items():
        print(f"=== Updating {name} ({cfg['underlying']}) ===")
        inst = update_instruments(cfg)
        update_etf_prices(cfg)
        update_option_prices(cfg, inst)
        print()

    for f in os.listdir(DATA_DIR):
        if f.startswith("30d_iv_cache"):
            cache_path = os.path.join(DATA_DIR, f)
            os.remove(cache_path)
            print(f"  Removed IV cache: {f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
