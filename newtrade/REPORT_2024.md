# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2025-01-01`
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
| 300ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 12 | 30 (8L/22S) | 1.519 | 2.135 | +0.1054 | +0.0595 | 7.756 | +0.0460 | 3.008 | 0.0232 | 53.3% (L:75.0%, S:45.5%) | 56.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 11 | 73 (55L/18S) | 1.326 | 2.170 | +0.1771 | +0.1000 | 1.712 | +0.0771 | 5.708 | 0.0988 | 56.2% (L:50.9%, S:72.2%) | 117.7x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 11 | 38 (38L/0S) | 0.405 | 0.883 | +0.0509 | +0.0509 | 1.023 | +0.0000 | 0.000 | 0.0907 | 42.1% (L:42.1%, S:N/A) | 64.6x |
