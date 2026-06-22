# Day-Model Deployment & Data Guide

Specifications for data sources, required input files, and look-ahead bias prevention mechanisms.

---

## 1. Data Sources

The features are constructed from a combination of Ricequant API data (both standard and 3rd party) and self-calculated options derivatives:

| Dataset | Source | Details / API | Required Columns |
| :--- | :--- | :--- | :--- |
| **ETF Daily Prices** | Ricequant standard | fund daily price series | `close_adj`, `open_adj`, `high_adj`, `low_adj`, `volume` |
| **ETF Intraday (5m)** | Ricequant standard | fund 5-minute bars | `open`, `close`, `high`, `low`, `volume`, `datetime` |
| **Securities Margin** | Ricequant 3rd-party | `rqdatac.get_securities_margin` | `margin_balance`, `buy_on_margin_value`, `margin_repayment`, `short_balance`, etc. |
| **Capital Flow** | Ricequant 3rd-party | `rqdatac.get_capital_flow` | `buy_volume`, `buy_value`, `sell_volume`, `sell_value` |
| **Northbound Connect** | Ricequant 3rd-party | `rqdatac.get_stock_connect_quota` | `buy_turnover`, `sell_turnover` (filtered on `hk_to_sh`, `hk_to_sz`) |
| **Ricequant VIX** | Ricequant index | `rqdatac.get_price` on `VX000{N}.RI` | `close` (VIX index level) |
| **ATM 30d IV** | Self-Calculated | Interpolated ATM Black-Scholes IV | solved from daily option close price history |

---

## 2. Necessary Files (Deployment Directory Structure)

At deployment or training runtime, the following structure in the `data/` folder is required:

```
data/
├── {ETF}_1d.parquet                   # ETF daily historical price data
├── {ETF}_5m.parquet                   # ETF 5-minute bar data
├── 30d_iv_cache_{etf_key}.parquet     # Pre-calculated 30d ATM implied volatility cache
├── rq_vix.parquet                     # Cached Ricequant VIX index levels (5 ETFs)
├── securities_margin.parquet          # Cached daily margin trading data
├── capital_flow.parquet               # Cached daily stock capital flow data
└── stock_connect_quota.parquet        # Cached daily northbound connect quota
```

*Note: 3rd party datasets and VIX index parquets are cached locally to minimize API quota usage and prevent network lag during feature construction.*

---

## 3. Strict Look-Ahead Bias Mitigation

To ensure zero forward information leakage into the model, the feature engineering pipeline enforces three chronological boundaries:

### A. Intraday Early-Bar Feature Boundary
* Intraday features (momentum, realized volatility, price path length, VWAP deviations) are computed using **only the first 6 five-minute bars** (9:30 AM to 10:00 AM).
* All data points from the rest of the trading day are completely ignored for feature construction.

### B. Daily Feature Shift
* All day-level indicators (technical oscillators like RSI/MACD, realized volatilities, margin flows, northbound capital flows, VIX levels, and yesterday's performance diagnostics) are calculated on historical daily close data.
* These columns are explicitly **shifted by 1 day** (`df[col] = df[col].shift(1)`) in `build_features.py` before merging, ensuring that at any day $t$, only information finalized at the close of day $t-1$ is used.

### C. Volume Normalization (No Current-Day Leakage)
* Volume features (e.g. `early_volume_ratio`, `bar_vol_{i}`) are normalized relative to expected bar volume.
* Rather than normalizing by the current day's full volume (which would leak future daily volume into the 10:00 AM prediction), the pipeline calculates expected bar volume as:
  $$\text{Expected Bar Volume} = \frac{\text{Prior 20-day average daily volume shifted by 1 day}}{48}$$
  This maintains strict chronological limits.
