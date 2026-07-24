# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `tanh`
- **Transaction Friction**: `8.0 bps`
- **Rank Mapping Options**: `mapping=linear, min_ratio=0.2, max_ratio=1.8, power=2.0`

## Rank Bounded Weight (Linear)

![Rank Bounded Weight Cumulative Equity](artifacts/rank_bounded_equity.png)

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:1.00) | 10 | 42 | 0.722 | 0.894 | +0.0502 | 0.0082 | 61.9% | 4.2x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 300 | 0.514 | 1.186 | +0.0764 | 0.0505 | 52.0% | 32.5x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 11 | 314 | 1.018 | 1.504 | +0.2394 | 0.0461 | 49.0% | 37.5x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.00 (train:0.90) | 10 | 40 | 0.709 | 0.856 | +0.0490 | 0.0073 | 62.5% | 3.6x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 291 | 0.458 | 1.125 | +0.0630 | 0.0497 | 53.6% | 29.8x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.30 (train:0.20) | 11 | 353 | 1.005 | 1.514 | +0.2575 | 0.0525 | 48.2% | 42.8x |

</details>

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:1.00) | 10 | 40 | 0.705 | 0.864 | +0.0497 | 0.0076 | 62.5% | 3.9x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 294 | 0.495 | 1.162 | +0.0706 | 0.0503 | 52.7% | 31.0x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 11 | 310 | 1.028 | 1.497 | +0.2417 | 0.0451 | 48.4% | 36.3x |

</details>

<details>
<summary><b>Score Weighted</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.10 (train:1.00) | 10 | 39 | 0.708 | 0.862 | +0.0464 | 0.0067 | 61.5% | 3.6x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 48 | 303 | 0.520 | 1.185 | +0.0780 | 0.0507 | 51.8% | 32.5x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.40 (train:0.30) | 11 | 314 | 1.016 | 1.502 | +0.2401 | 0.0465 | 48.4% | 37.8x |

</details>
