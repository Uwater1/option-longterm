# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.40/S:1.00 (train L:1.30/S:0.90) | 10 | 6 (2L/4S) | 0.729 | 1.055 | +0.0182 | +0.0029 | 3.786 | +0.0154 | 5.373 | 0.0101 | 50.0% (L:50.0%, S:50.0%) | 12.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.40 (train L:0.70/S:1.30) | 32 | 60 (60L/0S) | 1.717 | 3.384 | +0.0885 | +0.0885 | 3.520 | +0.0000 | 0.000 | 0.0235 | 61.7% (L:61.7%, S:N/A) | 99.6x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 1 | 39 (39L/0S) | -0.170 | 0.508 | -0.0156 | -0.0156 | -0.424 | +0.0000 | 0.000 | 0.0829 | 46.2% (L:46.2%, S:N/A) | 49.8x |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.20 (train L:1.00/S:1.10) | 11 | 38 (29L/9S) | 0.728 | 1.408 | +0.0630 | +0.0374 | 1.410 | +0.0256 | 3.443 | 0.0665 | 57.9% (L:55.2%, S:66.7%) | 72.6x |
