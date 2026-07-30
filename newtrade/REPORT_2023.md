# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2024-01-01`
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
| 300ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:1.30/S:1.10 (train L:1.20/S:1.00) | 11 | 31 (5L/26S) | -0.854 | 0.467 | -0.0321 | +0.0105 | 4.832 | -0.0426 | -3.911 | 0.0506 | 54.8% (L:80.0%, S:50.0%) | 58.3x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 18 | 41 (36L/5S) | 0.840 | 2.317 | +0.0346 | +0.0064 | 0.508 | +0.0282 | 8.999 | 0.0221 | 53.7% (L:50.0%, S:80.0%) | 71.8x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2024-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2023-01 ~ 2024-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:0.70/S:1.20 (train L:0.60/S:1.10) | 10 | 26 (25L/1S) | 1.508 | 2.217 | +0.0764 | +0.0707 | 4.522 | +0.0057 | 0.000 | 0.0247 | 53.8% (L:52.0%, S:100.0%) | 43.7x |
