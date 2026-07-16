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
    "588000ETF": {
        "underlying": "588000.XSHG",
        "instruments": "588000ETF_instruments.parquet",
        "prices": "588000ETF_historical_prices.parquet",
        "etf_1d": "588000ETF_1d.parquet",
    },
    "159915ETF": {
        "underlying": "159915.XSHE",
        "instruments": "159915ETF_instruments.parquet",
        "prices": "159915ETF_historical_prices.parquet",
        "etf_1d": "159915ETF_1d.parquet",
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

    if os.path.exists(path):
        existing = pd.read_parquet(path)
        existing["date"] = pd.to_datetime(existing["date"])
        last_date = existing["date"].max()
        start = last_date + pd.Timedelta(days=1)
    else:
        existing = pd.DataFrame()
        listed_date_str = rq.instruments(underlying).listed_date
        start = max(pd.Timestamp("2010-01-04"), pd.Timestamp(listed_date_str))
        last_date = start - pd.Timedelta(days=1)

    today_date = pd.Timestamp.now().date()
    if start.date() > today_date:
        print(f"  ETF prices: already up to date ({last_date.date()})")
        return

    etf = rq.get_price(
        underlying, start_date=start.strftime("%Y-%m-%d"),
        end_date=pd.Timestamp.now().strftime("%Y-%m-%d"),
        frequency="1d",
        adjust_type="none"
    )

    if etf is None or etf.empty:
        print(f"  ETF prices: no new data since {last_date.date()}")
        return

    etf_adj = rq.get_price(
        underlying, start_date=start.strftime("%Y-%m-%d"),
        end_date=pd.Timestamp.now().strftime("%Y-%m-%d"),
        frequency="1d",
        adjust_type="post"
    )

    etf = etf.reset_index()
    etf.columns = [c.lower() if c != "order_book_id" else c for c in etf.columns]
    if "date" not in etf.columns and "datetime" in etf.columns:
        etf.rename(columns={"datetime": "date"}, inplace=True)
    etf["date"] = pd.to_datetime(etf["date"])

    if etf_adj is not None and not etf_adj.empty:
        etf_adj = etf_adj.reset_index()
        etf_adj.columns = [c.lower() if c != "order_book_id" else c for c in etf_adj.columns]
        if "date" not in etf_adj.columns and "datetime" in etf_adj.columns:
            etf_adj.rename(columns={"datetime": "date"}, inplace=True)
        etf_adj["date"] = pd.to_datetime(etf_adj["date"])

        etf_adj_slim = etf_adj[["date", "open", "high", "low", "close"]].rename(columns={
            "open": "open_adj",
            "high": "high_adj",
            "low": "low_adj",
            "close": "close_adj"
        })
        etf = etf.merge(etf_adj_slim, on="date", how="left")
    else:
        for col in ["open", "high", "low", "close"]:
            etf[f"{col}_adj"] = etf[col]

    combined = pd.concat([existing, etf], ignore_index=True)
    combined = combined.drop_duplicates(subset=["date"], keep="last").sort_values("date")
    combined.to_parquet(path, index=False)
    print(f"  ETF prices: +{len(etf)} days ({last_date.date()} -> {combined['date'].max().date()}) -> {path}")


def update_option_prices(cfg, inst):
    path = os.path.join(DATA_DIR, cfg["prices"])
    underlying = cfg["underlying"]

    if os.path.exists(path):
        existing = pd.read_parquet(path)
        existing["date"] = pd.to_datetime(existing["date"])
        last_date = existing["date"].max()
        start = last_date + pd.Timedelta(days=1)
    else:
        existing = pd.DataFrame()
        last_date = pd.Timestamp("2010-01-01")
        start = pd.to_datetime(inst["listed_date"].min())

    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    today_date = pd.Timestamp.now().date()
    if start.date() > today_date:
        print(f"  Option prices: already up to date ({last_date.date()})")
        return

    new_contracts = inst[inst["listed_date"] >= start]["order_book_id"].tolist()

    if not existing.empty:
        old_contracts = existing["order_book_id"].unique().tolist()
        contracts_to_update = [c for c in old_contracts if c in inst["order_book_id"].values]
    else:
        contracts_to_update = []

    all_new = []
    batch_size = 50

    if new_contracts:
        print(f"  Fetching prices for {len(new_contracts)} new contracts...")
        for i in range(0, len(new_contracts), batch_size):
            batch = new_contracts[i:i + batch_size]
            px = rq.get_price(batch, start_date=start.strftime("%Y-%m-%d"), end_date=today)
            if px is not None and not px.empty:
                all_new.append(px.reset_index())

    if contracts_to_update:
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


def update_vix_prices():
    path = os.path.join(DATA_DIR, "rq_vix.parquet")
    print("=== Updating VIX Indices (rq_vix.parquet) ===")
    symbols = {
        "vix_50": "VX0004.RI",
        "vix_300": "VX0005.RI",
        "vix_500": "VX0006.RI",
        "vix_588000": "VX0007.RI",
        "vix_159915": "VX0010.RI",
    }
    
    dfs = []
    for col, sym in symbols.items():
        try:
            inst = rq.instruments(sym)
            if inst is None:
                continue
            listed_date = pd.Timestamp(inst.listed_date)
            start_date = max(pd.Timestamp("2010-01-01"), listed_date)
            
            df = rq.get_price(
                sym,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=pd.Timestamp.now().strftime("%Y-%m-%d"),
                frequency="1d"
            )
            if df is not None and not df.empty:
                df = df.reset_index()
                # Close price is in percentage (e.g. 24.11), convert to decimal (e.g. 0.2411)
                df[col] = df["close"] / 100.0
                df["date"] = pd.to_datetime(df["date"])
                df = df[["date", col]].set_index("date")
                dfs.append(df)
                print(f"  VIX {col} ({sym}): downloaded {len(df)} rows from {df.index.min().date()} to {df.index.max().date()}")
        except Exception as e:
            print(f"  [WARN] Failed to fetch VIX data for {sym}: {e}")
            
    if dfs:
        vix_df = pd.concat(dfs, axis=1)
        vix_df = vix_df.sort_index()
        vix_df.to_parquet(path)
        print(f"  Saved VIX indices cache to {path} (shape: {vix_df.shape})")
    else:
        print("  Warning: No VIX data collected")


def main():
    rq.init()
    print("rqdatac connected.\n")

    for name, cfg in UNDERLYINGS.items():
        print(f"=== Updating {name} ({cfg['underlying']}) ===")
        inst = update_instruments(cfg)
        update_etf_prices(cfg)
        update_option_prices(cfg, inst)
        print()

    update_vix_prices()
    print()

    for f in os.listdir(DATA_DIR):
        if f.startswith("30d_iv_cache"):
            cache_path = os.path.join(DATA_DIR, f)
            os.remove(cache_path)
            print(f"  Removed IV cache: {f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
