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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.30 (train L:1.40/S:1.20) | 14 | 10 (3L/7S) | -1.890 | -0.908 | -0.0271 | -0.0147 | -23.937 | -0.0123 | -7.810 | 0.0271 | 20.0% (L:0.0%, S:28.6%) | 20.7x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 12 | 67 (64L/3S) | 0.073 | 1.894 | +0.0042 | +0.0187 | 0.643 | -0.0145 | -18.362 | 0.0571 | 52.2% (L:54.7%, S:0.0%) | 103.7x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 13 | 63 (41L/22S) | 1.831 | 2.776 | +0.1811 | +0.1246 | 4.357 | +0.0566 | 2.781 | 0.0765 | 60.3% (L:61.0%, S:59.1%) | 116.2x |
