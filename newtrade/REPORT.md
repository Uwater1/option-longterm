# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `tanh`
- **Transaction Friction**: `8.0 bps`

## Equal Weight (EW)

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.00 (train:0.90) | 10 | 40 | 0.709 | 0.857 | +0.0491 | 0.0074 | 62.5% | 3.6x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 291 | 0.452 | 1.123 | +0.0620 | 0.0497 | 53.3% | 30.0x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.30 (train:0.20) | 11 | 353 | 1.010 | 1.514 | +0.2629 | 0.0523 | 47.3% | 43.0x |

## IC Weight (ICW)

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:1.00) | 10 | 40 | 0.705 | 0.865 | +0.0499 | 0.0076 | 62.5% | 4.0x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 295 | 0.486 | 1.159 | +0.0693 | 0.0503 | 52.5% | 31.2x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.30 (train:0.20) | 11 | 348 | 0.997 | 1.503 | +0.2575 | 0.0528 | 47.7% | 42.9x |

## Score Weighted

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:1.00) | 10 | 39 | 0.708 | 0.862 | +0.0466 | 0.0067 | 61.5% | 3.6x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 304 | 0.510 | 1.182 | +0.0765 | 0.0508 | 51.6% | 32.8x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 11 | 313 | 1.027 | 1.507 | +0.2481 | 0.0458 | 48.2% | 38.1x |

## Rank Bounded Weight

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:1.00) | 10 | 37 | 0.717 | 0.864 | +0.0483 | 0.0071 | 67.6% | 3.5x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 296 | 0.491 | 1.166 | +0.0708 | 0.0502 | 52.7% | 31.7x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 11 | 309 | 1.036 | 1.509 | +0.2499 | 0.0451 | 48.9% | 37.5x |
