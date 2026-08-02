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
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 85 | 59 opt | 0.492 | 0.870 | +14,025 RMB | +0.1085 | 2.179 | +0.0318 | 0.717 | 0.1023 | 42.4% (L:40.9%, S:43.2%) | 48.5x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 144 | 112 opt | 0.984 | 1.254 | +43,104 RMB | +0.1096 | 0.796 | +0.3214 | 4.603 | 0.2650 | 50.0% (L:44.3%, S:59.5%) | 92.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 118 | 90 opt | 1.244 | 1.627 | +57,667 RMB | +0.2873 | 1.924 | +0.2893 | 6.286 | 0.1458 | 43.3% (L:40.0%, S:55.0%) | 71.0x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.40/S:1.40) | 85 | 30 opt | 0.565 | 0.777 | +13,584 RMB | +0.0338 | 0.807 | +0.1020 | 6.435 | 0.0896 | 40.0% (L:31.6%, S:54.5%) | 25.4x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 144 | 111 opt | 1.046 | 1.297 | +47,950 RMB | +0.1956 | 1.246 | +0.2839 | 4.811 | 0.1868 | 48.6% (L:43.4%, S:60.0%) | 91.7x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.80/S:1.40) | 118 | 92 opt | 0.791 | 1.158 | +35,862 RMB | +0.1945 | 1.139 | +0.1641 | 7.325 | 0.1729 | 38.0% (L:36.9%, S:50.0%) | 71.7x |

</details>
