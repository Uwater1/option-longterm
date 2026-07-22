# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `tanh`
- **Transaction Friction**: `8.0 bps`

## Equal Weight (EW)

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:0.90) | 10 | 24 | 0.679 | 0.791 | +0.0433 | 0.0066 | 70.8% | 2.6x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.50 (train:0.30) | 48 | 244 | 0.386 | 0.983 | +0.0476 | 0.0444 | 54.5% | 23.9x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.20) | 11 | 305 | 1.043 | 1.505 | +0.2527 | 0.0447 | 48.9% | 36.8x |

## IC Weight (ICW)

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.20 (train:1.00) | 10 | 30 | 0.691 | 0.814 | +0.0451 | 0.0068 | 66.7% | 2.9x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.50 (train:0.30) | 48 | 246 | 0.422 | 1.024 | +0.0543 | 0.0451 | 54.9% | 25.2x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.20) | 11 | 306 | 1.040 | 1.504 | +0.2497 | 0.0444 | 48.7% | 36.7x |

## Score Weighted

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.20 (train:1.00) | 10 | 26 | 0.682 | 0.800 | +0.0410 | 0.0059 | 69.2% | 2.5x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.50 (train:0.30) | 48 | 259 | 0.469 | 1.073 | +0.0639 | 0.0460 | 53.7% | 26.8x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.50 (train:0.30) | 11 | 263 | 1.058 | 1.494 | +0.2371 | 0.0385 | 49.4% | 32.3x |

## Rank Bounded Weight

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.20 (train:1.00) | 10 | 26 | 0.698 | 0.811 | +0.0431 | 0.0063 | 69.2% | 2.5x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.50 (train:0.30) | 48 | 253 | 0.435 | 1.040 | +0.0568 | 0.0454 | 53.8% | 25.6x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.50 (train:0.30) | 11 | 264 | 1.064 | 1.493 | +0.2381 | 0.0380 | 49.2% | 31.7x |
