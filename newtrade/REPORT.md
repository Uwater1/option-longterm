# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Transaction Friction**: `8.0 bps`
- **Rank Mapping Options**: `mapping=linear, min_ratio=0.2, max_ratio=1.8, power=2.0`

## Rank Bounded Weight (Linear)

![Rank Bounded Weight Cumulative Equity](artifacts/rank_bounded_equity.png)

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.40 (train:1.30) | 10 | 17 | 0.945 | 1.144 | +0.1128 | 0.0153 | 76.5% | 8.8x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.60 (train:0.50) | 32 | 226 | 0.713 | 1.540 | +0.2357 | 0.1151 | 57.1% | 88.9x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 126 | 1.056 | 1.495 | +0.3937 | 0.0766 | 57.9% | 54.1x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.20 (train:1.10) | 10 | 20 | 0.885 | 1.089 | +0.1231 | 0.0191 | 70.0% | 9.9x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.70 (train:0.60) | 32 | 166 | 0.568 | 1.336 | +0.1612 | 0.1020 | 57.8% | 70.7x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 122 | 1.139 | 1.571 | +0.4159 | 0.0733 | 59.0% | 52.0x |

</details>

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.30 (train:1.20) | 10 | 20 | 0.885 | 1.089 | +0.1231 | 0.0191 | 70.0% | 9.9x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.70 (train:0.60) | 32 | 177 | 0.541 | 1.341 | +0.1551 | 0.1038 | 58.2% | 74.4x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 119 | 0.913 | 1.346 | +0.3269 | 0.0803 | 57.1% | 51.0x |

</details>

<details>
<summary><b>Score Weighted</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.30 (train:1.20) | 10 | 20 | 0.885 | 1.089 | +0.1231 | 0.0191 | 70.0% | 9.9x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.60 (train:0.50) | 32 | 226 | 0.728 | 1.556 | +0.2408 | 0.1164 | 57.1% | 88.9x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 125 | 1.018 | 1.466 | +0.3683 | 0.0766 | 58.4% | 53.6x |

</details>
