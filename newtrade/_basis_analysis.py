"""Analyze futures basis (discount/premium) vs ETF spot and its impact on intraday strategy."""
import pandas as pd
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / "data"

# ETF 5m file mapping (some use ticker code, some use ETF name)
ETF_5M_FILE = {
    "300ETF": "510300_5m.parquet",
    "500ETF": "500ETF_5m.parquet",
    "50ETF": "50ETF_5m.parquet",
}

pairs = [
    ("300ETF", "IF88_5m.parquet", "IF88"),
    ("500ETF", "IC88_5m.parquet", "IC88"),
    ("50ETF", "IH88_5m.parquet", "IH88"),
]

for etf, fut_file, fut_name in pairs:
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"{etf} vs {fut_name} — Basis & Return Drag Analysis")
    print(sep)

    # Load ETF 5m data to compute daily close
    etf_5m = pd.read_parquet(DATA / ETF_5M_FILE[etf])
    etf_5m["datetime"] = pd.to_datetime(etf_5m["datetime"])
    etf_5m["date"] = etf_5m["datetime"].dt.date
    etf_daily_close = etf_5m.groupby("date").agg(etf_close=("close", "last")).reset_index()
    etf_daily_close["date"] = pd.to_datetime(etf_daily_close["date"])
    etf_daily_close = etf_daily_close.set_index("date").sort_index()

    # Load futures 5m
    df_5m = pd.read_parquet(DATA / fut_file)
    df_5m["datetime"] = pd.to_datetime(df_5m["datetime"])
    df_5m["date"] = df_5m["datetime"].dt.date

    # Daily futures close for basis measurement
    daily_fut = df_5m.groupby("date").agg(
        fut_open=("open", "first"), fut_close=("close", "last"),
    ).reset_index()
    daily_fut["date"] = pd.to_datetime(daily_fut["date"])
    daily_fut = daily_fut.set_index("date").sort_index()

    # Merge ETF close with futures close
    merged = etf_daily_close[["etf_close"]].join(daily_fut[["fut_close"]], how="inner").dropna()
    merged = merged.rename(columns={"etf_close": "close"})

    # Basis = (Fut - Spot) / Spot * 100 (negative = discount/backwardation)
    merged["basis_pct"] = (merged["fut_close"] / merged["close"] - 1) * 100

    print(f"  Data range: {merged.index[0].date()} to {merged.index[-1].date()} ({len(merged)} days)")
    print(f"  Mean basis: {merged['basis_pct'].mean():.3f}%")
    print(f"  Median basis: {merged['basis_pct'].median():.3f}%")
    print(f"  Min basis: {merged['basis_pct'].min():.3f}%")
    print(f"  Max basis: {merged['basis_pct'].max():.3f}%")
    print(f"  % days in discount (basis<0): {(merged['basis_pct'] < 0).mean() * 100:.1f}%")

    # By year
    merged["year"] = merged.index.year
    print(f"\n  Basis by Year:")
    for yr, g in merged.groupby("year"):
        print(f"    {yr}: mean={g['basis_pct'].mean():.3f}%, median={g['basis_pct'].median():.3f}%, "
              f"discount_days={(g['basis_pct'] < 0).mean() * 100:.0f}%")

    # --- Intraday return comparison (10:00 -> 14:35) ---
    fut_ret = {}
    for d, g in df_5m.groupby("date"):
        g = g.sort_values("datetime").reset_index(drop=True)
        if len(g) > 42:
            entry = float(g.iloc[6]["open"])
            exit_ = float(g.iloc[42]["close"])
            if entry > 0:
                fut_ret[pd.Timestamp(d)] = np.log(exit_ / entry)
    fut_s = pd.Series(fut_ret, name="fut_intraday")

    # ETF intraday from 5m (reuse etf_5m loaded above)
    etf_ret = {}
    for d, g in etf_5m.groupby("date"):
        g = g.sort_values("datetime").reset_index(drop=True)
        if len(g) > 42:
            entry = float(g.iloc[6]["open"])
            exit_ = float(g.iloc[42]["close"])
            if entry > 0:
                etf_ret[pd.Timestamp(d)] = np.log(exit_ / entry)
    etf_s = pd.Series(etf_ret, name="etf_intraday")

    comp = pd.concat([etf_s, fut_s], axis=1).dropna()
    comp["diff"] = comp["fut_intraday"] - comp["etf_intraday"]
    comp["year"] = comp.index.year

    print(f"\n  Intraday Return Comparison (10:00->14:35, {len(comp)} overlapping days):")
    print(f"    ETF mean daily: {comp['etf_intraday'].mean() * 100:.5f}%")
    print(f"    Fut mean daily: {comp['fut_intraday'].mean() * 100:.5f}%")
    print(f"    Diff (Fut-ETF) mean: {comp['diff'].mean() * 100:.5f}% per day")
    print(f"    Diff annualized: {comp['diff'].mean() * 252 * 100:.2f}%/yr")
    print(f"    Cumulative gap over period: {comp['diff'].sum() * 100:.2f}%")

    # Who benefits: long or short?
    # If basis < 0 (discount), long futures UNDERPERFORM spot (bad for long)
    # Short futures would OUTPERFORM short spot (good for short)
    long_days = comp[comp["diff"] < 0]
    short_benefit_days = comp[comp["diff"] > 0]
    print(f"\n  Impact on Long vs Short:")
    print(f"    Days Fut < ETF (hurts long): {len(long_days)} ({len(long_days)/len(comp)*100:.1f}%)")
    print(f"    Days Fut > ETF (helps long): {len(short_benefit_days)} ({len(short_benefit_days)/len(comp)*100:.1f}%)")
    print(f"    Mean drag on long days: {long_days['diff'].mean()*100:.5f}%")
    print(f"    Mean boost on short-benefit days: {short_benefit_days['diff'].mean()*100:.5f}%")

    print(f"\n    By Year (annualized intraday drag):")
    for yr, g in comp.groupby("year"):
        etf_ann = g["etf_intraday"].mean() * 252 * 100
        fut_ann = g["fut_intraday"].mean() * 252 * 100
        drag = g["diff"].mean() * 252 * 100
        print(f"      {yr}: ETF={etf_ann:+.2f}%/yr, Fut={fut_ann:+.2f}%/yr, Drag={drag:+.2f}%/yr")

print("\n" + "=" * 70)
print("SUMMARY & RECOMMENDATION")
print("=" * 70)
print("""
KEY FINDINGS:
- Futures basis (discount) systematically HURTS long positions and BENEFITS short positions.
- The 88 continuous contract embeds roll cost: in backwardation, rolling long positions 
  locks in a loss (sell low near-month, buy higher far-month... actually in backwardation 
  you sell the cheaper near-month and buy the more expensive far-month = negative roll yield).
- For INTRADAY strategies (10:00-14:35 hold), the daily basis change matters less than 
  the level, but the continuous contract stitching still introduces small daily gaps.

SUITABILITY FOR THIS PROJECT:
- This project trades INTRADAY (10:00 open -> 14:35 close), NOT overnight.
- For pure intraday, the basis LEVEL doesn't directly cost you (you enter and exit same day).
- The drag comes from: (1) continuous contract roll gaps in the data, (2) slightly different 
  intraday dynamics of futures vs ETF.
- If the measured drag is small (<0.5%/yr), futures are STILL SUITABLE because:
  * Lower transaction costs in practice (futures: ~0.5 bps vs ETF: ~3-5 bps stamp duty + commission)
  * T+0 trading (no settlement delay)
  * Leverage capital efficiency
- If drag is large (>2%/yr), the continuous contract data may be introducing artifacts.
""")
