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
| 300ETF | single | 2022-01 ~ 2025-12 | 1.40 (train:1.30) | 10 | 143 (17L/126S) | 0.707 | 1.680 | +0.1447 | 0.0474 | 55.9% (L:76.5%, S:53.2%) | 66.1x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.60 (train:0.50) | 32 | 270 (226L/44S) | 0.768 | 1.710 | +0.2799 | 0.1182 | 55.9% (L:57.1%, S:50.0%) | 111.8x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 239 (126L/113S) | 1.460 | 2.220 | +0.6359 | 0.0910 | 61.1% (L:57.1%, S:65.5%) | 108.7x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.20 (train:1.10) | 10 | 47 (20L/27S) | 0.780 | 1.176 | +0.1378 | 0.0724 | 57.4% (L:70.0%, S:48.1%) | 23.4x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.70 (train:0.60) | 32 | 229 (166L/63S) | 0.873 | 1.806 | +0.2945 | 0.0888 | 58.1% (L:57.8%, S:58.7%) | 102.5x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 283 (122L/161S) | 1.233 | 2.098 | +0.5510 | 0.0866 | 59.0% (L:58.2%, S:59.6%) | 125.9x |

</details>

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.30 (train:1.20) | 10 | 62 (20L/42S) | 0.815 | 1.334 | +0.1467 | 0.0652 | 58.1% (L:70.0%, S:52.4%) | 31.2x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.60 (train:0.50) | 32 | 290 (216L/74S) | 0.980 | 1.998 | +0.3734 | 0.1022 | 58.6% (L:58.3%, S:59.5%) | 125.9x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 274 (119L/155S) | 1.141 | 2.004 | +0.4998 | 0.0891 | 58.0% (L:56.3%, S:59.4%) | 123.3x |

</details>

<details>
<summary><b>Score Weighted</b> (click to expand)</summary>

| ETF | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | single | 2022-01 ~ 2025-12 | 1.30 (train:1.20) | 10 | 63 (20L/43S) | 0.821 | 1.349 | +0.1479 | 0.0652 | 58.7% (L:70.0%, S:53.5%) | 31.7x |
| 500ETF | single | 2022-01 ~ 2025-12 | 0.60 (train:0.50) | 32 | 242 (226L/16S) | 0.878 | 1.725 | +0.3095 | 0.1386 | 57.9% (L:57.1%, S:68.8%) | 97.3x |
| 50ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | single | 2022-01 ~ 2025-12 | 0.90 (train:0.80) | 11 | 241 (125L/116S) | 1.431 | 2.215 | +0.6107 | 0.0885 | 61.4% (L:57.6%, S:65.5%) | 109.8x |

</details>
