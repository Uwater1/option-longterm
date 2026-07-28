# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `SCORE`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Transaction Friction**: `8.0 bps`
- **Rank Mapping Options**: `mapping=linear, min_ratio=0.2, max_ratio=1.8, power=2.0`

<details>
<summary><b>Score Weighted</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.50/S:0.80 (train L:1.40/S:0.70) | 10 | 145 (10L/135S) | 0.673 | 1.633 | +0.1384 | 0.0559 | 55.2% (L:70.0%, S:54.1%) | 65.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:0.90 (train L:0.60/S:0.80) | 32 | 328 (210L/118S) | 0.754 | 1.858 | +0.2943 | 0.0958 | 57.9% (L:58.1%, S:57.6%) | 139.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:0.90 (train L:0.60/S:0.80) | 11 | 352 (195L/157S) | 1.187 | 2.158 | +0.5650 | 0.1231 | 55.4% (L:51.8%, S:59.9%) | 150.1x |

</details>
