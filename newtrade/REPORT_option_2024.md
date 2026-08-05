# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
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

![Cumulative Equity](artifacts/equity_curve_option_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 62 | 42 opt | 0.759 | 1.052 | +20,568 RMB | +0.1975 | 4.721 | +0.0082 | 0.260 | 0.0923 | 40.5% (L:47.1%, S:36.0%) | 35.8x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 256 | 87 opt | 1.233 | 1.460 | +48,585 RMB | +0.1176 | 1.101 | +0.3682 | 6.611 | 0.1104 | 52.9% (L:47.3%, S:62.5%) | 71.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 128 | 96 opt | 0.823 | 1.178 | +39,909 RMB | +0.2671 | 1.346 | +0.1320 | 0.000 | 0.1952 | 38.5% (L:37.9%, S:100.0%) | 73.8x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 62 | 49 opt | 0.943 | 1.244 | +29,132 RMB | +0.1652 | 4.151 | +0.1261 | 2.319 | 0.0770 | 42.9% (L:43.8%, S:42.4%) | 41.4x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 256 | 88 opt | 1.106 | 1.334 | +42,905 RMB | +0.0699 | 0.663 | +0.3592 | 6.456 | 0.1306 | 51.1% (L:45.5%, S:60.6%) | 73.5x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 128 | 96 opt | 0.823 | 1.178 | +39,909 RMB | +0.2671 | 1.346 | +0.1320 | 0.000 | 0.1952 | 38.5% (L:37.9%, S:100.0%) | 73.9x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:0.90 (train L:1.10/S:0.80) | 62 | 106 opt | 0.776 | 1.215 | +37,397 RMB | +0.2840 | 2.341 | +0.0900 | 0.954 | 0.1526 | 43.4% (L:42.2%, S:44.3%) | 85.9x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 256 | 107 opt | 1.033 | 1.292 | +42,639 RMB | +0.0703 | 0.551 | +0.3561 | 5.680 | 0.2784 | 50.5% (L:44.9%, S:60.5%) | 88.9x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 128 | 100 opt | 0.424 | 0.856 | +15,910 RMB | +0.0356 | 0.236 | +0.1235 | 8.780 | 0.2272 | 37.0% (L:35.8%, S:60.0%) | 78.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.759 | 0.357 | NOT_SIGNIFICANT | 0.551 | 0.325 | 100% |
| 500ETF | icw | 1.233 | 0.603 | NOT_SIGNIFICANT | 0.794 | 0.346 | 100% |
| 159915ETF | icw | 0.823 | 0.393 | NOT_SIGNIFICANT | 1.101 | 0.273 | 100% |
| 300ETF | sortino | 0.943 | 0.490 | NOT_SIGNIFICANT | 0.531 | 0.296 | 87% |
| 500ETF | sortino | 1.106 | 0.525 | NOT_SIGNIFICANT | 0.910 | 0.410 | 93% |
| 159915ETF | sortino | 0.823 | 0.393 | NOT_SIGNIFICANT | 1.179 | 0.253 | 100% |
| 300ETF | ew | 0.776 | 0.367 | NOT_SIGNIFICANT | 0.202 | 0.292 | 73% |
| 500ETF | ew | 1.033 | 0.480 | NOT_SIGNIFICANT | 1.149 | 0.492 | 93% |
| 159915ETF | ew | 0.424 | 0.169 | NOT_SIGNIFICANT | 1.045 | 0.319 | 100% |

