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
| 300ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 23 (7L/16S) | 0.916 | 1.638 | +0.0429 | +0.0391 | 8.523 | +0.0039 | 0.425 | 0.0363 | 52.2% (L:71.4%, S:43.8%) | 45.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 46 (39L/7S) | 1.422 | 2.564 | +0.0837 | +0.0208 | 1.100 | +0.0629 | 13.778 | 0.0409 | 63.0% (L:61.5%, S:71.4%) | 81.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2023-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.80/S:0.60 (train L:0.70/S:0.50) | 1 | 138 (59L/79S) | -0.232 | 1.170 | -0.0365 | +0.0464 | 0.966 | -0.0828 | -1.178 | 0.1858 | 50.7% (L:49.2%, S:51.9%) | 197.8x |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 11 | 62 (33L/29S) | 1.777 | 2.733 | +0.1714 | +0.1015 | 3.558 | +0.0699 | 3.696 | 0.0662 | 64.5% (L:66.7%, S:62.1%) | 118.7x |
