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
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 103 opt | 0.852 | 1.147 | +56,652 RMB | +0.3072 | 3.047 | +0.2593 | 2.352 | 0.1895 | 50.5% (L:51.2%, S:50.0%) | 43.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.10/S:1.40) | 366 | 122 opt | 0.811 | 1.019 | +57,504 RMB | -0.0416 | -0.275 | +0.6166 | 5.708 | 0.2487 | 45.7% (L:39.5%, S:55.8%) | 56.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 37 | 208 opt | 0.594 | 1.120 | +55,983 RMB | +0.3360 | 0.981 | +0.2238 | 1.565 | 0.2525 | 34.1% (L:30.6%, S:38.9%) | 102.2x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 104 opt | 0.803 | 1.107 | +51,794 RMB | +0.3020 | 3.073 | +0.2159 | 2.009 | 0.1836 | 50.0% (L:51.2%, S:49.2%) | 43.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 366 | 140 opt | 0.801 | 1.027 | +66,899 RMB | +0.0245 | 0.115 | +0.6445 | 5.475 | 0.3164 | 44.7% (L:40.2%, S:53.8%) | 62.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 37 | 180 opt | 0.462 | 0.936 | +39,478 RMB | +0.2794 | 0.876 | +0.1153 | 1.256 | 0.2619 | 32.5% (L:30.6%, S:36.5%) | 87.9x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 32 | 81 opt | 0.928 | 1.197 | +53,993 RMB | +0.3187 | 7.674 | +0.2212 | 1.932 | 0.1005 | 50.6% (L:64.3%, S:47.8%) | 30.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 366 | 190 opt | 0.895 | 1.138 | +87,287 RMB | +0.1623 | 0.595 | +0.7105 | 3.849 | 0.3467 | 42.7% (L:39.8%, S:47.1%) | 85.3x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.60/S:1.20 (train L:0.50/S:1.10) | 37 | 232 opt | 0.375 | 0.932 | +32,030 RMB | +0.3060 | 0.799 | +0.0143 | 0.183 | 0.2574 | 32.6% (L:31.8%, S:35.2%) | 105.9x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.852 | 0.635 | NOT_SIGNIFICANT | 0.371 | 0.255 | 100% |
| 500ETF | icw | 0.811 | 0.551 | NOT_SIGNIFICANT | 0.955 | 0.422 | 100% |
| 159915ETF | icw | 0.594 | 0.384 | NOT_SIGNIFICANT | 1.272 | 0.326 | 100% |
| 300ETF | sortino | 0.803 | 0.587 | NOT_SIGNIFICANT | 0.466 | 0.241 | 100% |
| 500ETF | sortino | 0.801 | 0.540 | NOT_SIGNIFICANT | 0.951 | 0.410 | 100% |
| 159915ETF | sortino | 0.462 | 0.277 | NOT_SIGNIFICANT | 1.034 | 0.365 | 100% |
| 300ETF | ew | 0.928 | 0.722 | NOT_SIGNIFICANT | 0.558 | 0.220 | 100% |
| 500ETF | ew | 0.895 | 0.634 | NOT_SIGNIFICANT | 0.991 | 0.453 | 93% |
| 159915ETF | ew | 0.375 | 0.211 | NOT_SIGNIFICANT | 0.702 | 0.514 | 93% |

