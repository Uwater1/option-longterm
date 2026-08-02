# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
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

![Cumulative Equity](artifacts/equity_curve_option_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 95 | 20 opt | 0.152 | 0.573 | +1,038 RMB | -0.0100 | -1.361 | +0.0204 | 1.840 | 0.0428 | 35.0% (L:40.0%, S:33.3%) | 29.8x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 76 opt | 0.438 | 0.779 | +7,376 RMB | +0.0492 | 0.658 | +0.0246 | 1.288 | 0.1230 | 47.4% (L:47.5%, S:47.1%) | 115.5x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 146 | 62 opt | 1.578 | 2.005 | +38,920 RMB | +0.1993 | 2.270 | +0.1899 | 5.840 | 0.0981 | 46.8% (L:46.9%, S:46.2%) | 97.3x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 95 | 8 opt | 1.085 | 1.248 | +6,086 RMB | +0.0437 | 0.000 | +0.0172 | 2.827 | 0.0177 | 50.0% (L:100.0%, S:42.9%) | 12.8x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 159 | 52 opt | 0.503 | 0.786 | +6,855 RMB | +0.0770 | 1.714 | -0.0084 | -0.478 | 0.1152 | 48.1% (L:51.4%, S:41.2%) | 81.5x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 146 | 56 opt | 1.820 | 2.194 | +45,653 RMB | +0.3029 | 3.777 | +0.1536 | 4.174 | 0.1033 | 51.8% (L:56.1%, S:40.0%) | 86.8x |

</details>
