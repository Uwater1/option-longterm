# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Mode**: `Option Portfolio`
- **Initial Capital**: `100,000 RMB per ETF`
- **Trade Budget**: `10% of portfolio capital per signal`
- **Commission**: `4.0 RMB per contract per side (8.0 RMB round-trip per contract)`
- **Option Selection**: `Nearest OTM, >=7 DTM`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_option.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.10 (train L:1.30/S:1.00) | 10 | 75 opt | 0.636 | 1.021 | +34,905 RMB | +0.3142 | 5.692 | +0.0348 | 0.379 | 0.1270 | 52.0% (L:56.5%, S:50.0%) | 30.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 32 | 208 opt | 0.809 | 1.232 | +114,139 RMB | +0.7200 | 1.251 | +0.4214 | 3.578 | 0.4243 | 41.4% (L:40.0%, S:48.6%) | 87.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 11 | 223 opt | 0.770 | 1.383 | +97,334 RMB | +0.8469 | 1.804 | +0.1264 | 0.686 | 0.3935 | 35.3% (L:31.5%, S:40.7%) | 102.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 opt | 0.882 | 1.080 | +45,054 RMB | +0.4646 | 8.052 | -0.0141 | -0.348 | 0.1683 | 48.9% (L:60.0%, S:40.7%) | 18.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 32 | 153 opt | 0.820 | 1.175 | +98,965 RMB | +0.9664 | 1.909 | +0.0232 | 9.165 | 0.2801 | 41.8% (L:42.2%, S:25.0%) | 64.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 11 | 246 opt | 0.801 | 1.478 | +111,461 RMB | +0.8852 | 1.747 | +0.2294 | 0.915 | 0.4073 | 36.1% (L:31.3%, S:41.7%) | 111.6x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.636 | 0.419 | NOT_SIGNIFICANT | 0.749 | 0.265 | 100% |
| 500ETF | icw | 0.809 | 0.566 | NOT_SIGNIFICANT | 1.199 | 0.579 | 100% |
| 159915ETF | icw | 0.770 | 0.539 | NOT_SIGNIFICANT | 1.052 | 0.339 | 100% |
| 300ETF | ew | 0.882 | 0.715 | NOT_SIGNIFICANT | 0.873 | 0.252 | 100% |
| 500ETF | ew | 0.820 | 0.591 | NOT_SIGNIFICANT | 1.117 | 0.406 | 100% |
| 159915ETF | ew | 0.801 | 0.565 | NOT_SIGNIFICANT | 0.999 | 0.366 | 100% |

