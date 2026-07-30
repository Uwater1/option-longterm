# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2023-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ICW`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Disabled (Hold to 14:35 Close)`
- **Transaction Friction**: `8.0 bps`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:1.30/S:1.20 (train L:1.20/S:1.10) | 13 | 30 (16L/14S) | 0.255 | 1.253 | +0.0119 | +0.0262 | 2.816 | -0.0143 | -2.071 | 0.0389 | 50.0% (L:62.5%, S:35.7%) | 62.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.90/S:0.90 (train L:0.80/S:0.80) | 19 | 62 (26L/36S) | -1.042 | 0.343 | -0.0747 | -0.0104 | -0.827 | -0.0644 | -2.784 | 0.1124 | 45.2% (L:61.5%, S:33.3%) | 120.8x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2023-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.60/S:0.60 (train L:0.50/S:0.50) | 4 | 134 (61L/73S) | -0.412 | 0.956 | -0.0645 | -0.0208 | -0.419 | -0.0437 | -0.655 | 0.1978 | 51.5% (L:45.9%, S:56.2%) | 196.8x |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.90/S:1.60 (train L:0.80/S:1.50) | 8 | 32 (28L/4S) | -0.059 | 0.735 | -0.0038 | -0.0034 | -0.170 | -0.0004 | -0.110 | 0.0565 | 53.1% (L:53.6%, S:50.0%) | 58.3x |
