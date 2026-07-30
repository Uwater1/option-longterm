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
| 300ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 15 (7L/8S) | 1.733 | 2.029 | +0.1081 | +0.0820 | 10.020 | +0.0261 | 5.772 | 0.0160 | 66.7% (L:85.7%, S:50.0%) | 29.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.80/S:1.40 (train L:0.70/S:1.30) | 32 | 60 (59L/1S) | 0.488 | 1.234 | +0.0620 | +0.0840 | 1.363 | -0.0220 | 0.000 | 0.1249 | 48.3% (L:49.2%, S:0.0%) | 85.4x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 1 | 56 (41L/15S) | 1.125 | 1.719 | +0.1644 | +0.1669 | 2.861 | -0.0025 | -0.373 | 0.0889 | 50.0% (L:53.7%, S:40.0%) | 95.8x |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 11 | 44 (32L/12S) | 1.381 | 1.898 | +0.1776 | +0.1238 | 2.726 | +0.0539 | 12.367 | 0.0525 | 59.1% (L:50.0%, S:83.3%) | 77.1x |
