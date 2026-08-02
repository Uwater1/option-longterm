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

![Cumulative Equity](artifacts/equity_curve_option_old.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.10 (train L:1.30/S:1.00) | 10 | 75 opt | 0.981 | 1.211 | +56,198 RMB | +0.3874 | 6.421 | +0.1746 | 1.954 | 0.1221 | 54.7% (L:60.9%, S:51.9%) | 30.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 32 | 208 opt | 1.045 | 1.257 | +140,970 RMB | +0.9302 | 1.685 | +0.4795 | 4.391 | 0.3539 | 42.6% (L:40.5%, S:54.1%) | 87.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 11 | 223 opt | 0.961 | 1.428 | +118,398 RMB | +0.6955 | 1.613 | +0.4885 | 2.226 | 0.3062 | 36.3% (L:31.5%, S:43.4%) | 102.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 opt | 0.916 | 1.055 | +45,441 RMB | +0.4791 | 8.776 | -0.0247 | -0.611 | 0.1587 | 48.9% (L:65.0%, S:37.0%) | 18.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 32 | 153 opt | 0.892 | 1.077 | +93,922 RMB | +0.9150 | 2.074 | +0.0242 | 9.165 | 0.2733 | 41.8% (L:42.2%, S:25.0%) | 64.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 11 | 246 opt | 1.039 | 1.533 | +150,762 RMB | +0.8069 | 1.616 | +0.7008 | 2.289 | 0.3457 | 37.7% (L:31.3%, S:45.1%) | 111.6x |

</details>
