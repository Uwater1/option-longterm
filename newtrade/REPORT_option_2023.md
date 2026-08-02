# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
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

![Cumulative Equity](artifacts/equity_curve_option_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 72 | 84 opt | 0.864 | 1.236 | +42,362 RMB | +0.2479 | 4.429 | +0.1758 | 1.705 | 0.1567 | 48.8% (L:52.4%, S:47.6%) | 45.9x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 196 | 177 opt | 1.226 | 1.484 | +115,517 RMB | +0.1212 | 0.433 | +1.0340 | 5.947 | 0.2054 | 51.4% (L:44.6%, S:63.1%) | 92.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 84 | 213 opt | 0.738 | 1.357 | +59,805 RMB | +0.1744 | 0.607 | +0.4237 | 2.843 | 0.2159 | 43.7% (L:37.8%, S:53.8%) | 109.3x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.50 (train L:1.20/S:1.40) | 72 | 56 opt | 0.751 | 0.990 | +30,218 RMB | +0.2621 | 3.041 | +0.0400 | 1.814 | 0.1016 | 51.8% (L:50.0%, S:56.2%) | 31.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 196 | 194 opt | 1.159 | 1.456 | +104,432 RMB | +0.1752 | 0.635 | +0.8692 | 4.756 | 0.2494 | 51.0% (L:45.7%, S:59.0%) | 103.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 84 | 213 opt | 0.907 | 1.433 | +94,000 RMB | +0.4222 | 1.007 | +0.5178 | 3.750 | 0.3401 | 43.7% (L:39.2%, S:56.4%) | 107.7x |

</details>
