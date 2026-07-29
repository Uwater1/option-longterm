# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Mode**: `Option Portfolio`
- **Initial Capital**: `100,000 RMB per ETF`
- **Trade Budget**: `10,000 RMB per signal`
- **Commission**: `4 RMB per side (8 RMB round-trip)`
- **Option Selection**: `Nearest OTM, >=7 DTM`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_option.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 62 opt | 1.341 | 1.341 | +77,724 RMB | +0.4878 | 9.188 | +0.2894 | 3.609 | 0.0959 | 56.5% (L:70.0%, S:50.0%) | 31.2x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 188 opt | 1.654 | 1.654 | +167,039 RMB | +1.4554 | 3.435 | +0.2150 | 4.559 | 0.1963 | 46.1% (L:46.7%, S:41.7%) | 91.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 11 | 154 opt | 1.971 | 1.971 | +163,689 RMB | +1.0019 | 4.245 | +0.6349 | 4.971 | 0.1070 | 45.8% (L:41.7%, S:51.1%) | 92.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 opt | 1.117 | 1.117 | +61,787 RMB | +0.4878 | 9.188 | +0.1301 | 2.222 | 0.1862 | 55.3% (L:70.0%, S:44.4%) | 23.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 188 opt | 1.625 | 1.625 | +163,921 RMB | +1.4297 | 3.394 | +0.2095 | 4.334 | 0.1963 | 45.9% (L:46.6%, S:40.0%) | 91.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.50 (train L:0.90/S:1.40) | 11 | 86 opt | 1.412 | 1.412 | +99,688 RMB | +0.9969 | 4.264 | +0.0000 | 0.000 | 0.0962 | 41.2% (L:41.6%, S:0.0%) | 49.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.341 | 0.955 | SIGNIFICANT | 0.851 | 0.239 | 100% |
| 500ETF | icw | 1.654 | 0.991 | SIGNIFICANT | 1.005 | 0.414 | 100% |
| 159915ETF | icw | 1.971 | 0.999 | SIGNIFICANT | 0.836 | 0.274 | 100% |
| 300ETF | ew | 1.117 | 0.862 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.625 | 0.989 | SIGNIFICANT | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 1.412 | 0.966 | SIGNIFICANT | 0.852 | 0.243 | 100% |

