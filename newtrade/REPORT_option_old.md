# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Mode**: `Option Portfolio`
- **Initial Capital**: `100,000 RMB per ETF`
- **Trade Budget**: `10% of portfolio capital per signal`
- **Commission**: `4.0 RMB per contract per side (8.0 RMB round-trip per contract)`
- **Option Selection**: `Nearest OTM, >=7 DTM`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_option_old.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.00/S:0.80) | 10 | 78 opt | 0.917 | 1.136 | +52,030 RMB | +0.4088 | 5.320 | +0.1115 | 1.549 | 0.1237 | 53.8% (L:58.6%, S:51.0%) | 28.1x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.70/S:1.30) | 32 | 135 opt | 1.031 | 1.208 | +87,097 RMB | +0.7630 | 2.385 | +0.1079 | 7.383 | 0.1439 | 44.2% (L:43.9%, S:50.0%) | 54.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 11 | 155 opt | 1.235 | 1.597 | +137,285 RMB | +0.7001 | 2.041 | +0.6727 | 4.462 | 0.2803 | 39.4% (L:36.4%, S:44.9%) | 68.7x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.10 (train L:1.10/S:0.90) | 10 | 85 opt | 0.770 | 1.024 | +44,724 RMB | +0.2418 | 3.139 | +0.2054 | 2.283 | 0.1209 | 50.6% (L:50.0%, S:50.9%) | 30.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.40 (train L:0.60/S:1.20) | 32 | 190 opt | 1.073 | 1.290 | +133,789 RMB | +1.0779 | 2.056 | +0.2600 | 4.399 | 0.2388 | 42.9% (L:41.6%, S:51.9%) | 76.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 11 | 221 opt | 1.125 | 1.654 | +139,809 RMB | +0.7486 | 2.124 | +0.6495 | 2.211 | 0.2473 | 41.0% (L:34.9%, S:46.3%) | 93.6x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.20 (train L:1.10/S:1.00) | 10 | 56 opt | 0.793 | 0.992 | +35,018 RMB | +0.3262 | 5.462 | +0.0240 | 0.629 | 0.0947 | 55.4% (L:57.7%, S:53.3%) | 20.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 32 | 156 opt | 0.994 | 1.187 | +90,353 RMB | +0.7371 | 2.147 | +0.1665 | 3.977 | 0.1820 | 43.8% (L:42.9%, S:50.0%) | 63.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 11 | 219 opt | 1.156 | 1.675 | +146,471 RMB | +0.8215 | 2.324 | +0.6432 | 2.116 | 0.2678 | 41.0% (L:35.8%, S:45.3%) | 93.8x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.10 (train L:1.10/S:0.90) | 10 | 29 opt | 1.046 | 1.142 | +42,075 RMB | +0.3663 | 9.782 | +0.0545 | 2.363 | 0.0681 | 58.6% (L:66.7%, S:50.0%) | 10.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.50 (train L:0.60/S:1.30) | 32 | 159 opt | 1.190 | 1.374 | +146,706 RMB | +1.3242 | 2.658 | +0.1429 | 4.686 | 0.2648 | 44.3% (L:44.4%, S:41.7%) | 62.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:0.80 (train L:0.70/S:0.60) | 11 | 260 opt | 0.917 | 1.531 | +107,942 RMB | +0.7861 | 2.482 | +0.2933 | 0.846 | 0.2295 | 39.9% (L:37.1%, S:41.7%) | 112.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.917 | 0.719 | NOT_SIGNIFICANT | 0.758 | 0.310 | 100% |
| 500ETF | ensemble | 1.031 | 0.758 | NOT_SIGNIFICANT | 0.995 | 0.478 | 100% |
| 159915ETF | ensemble | 1.235 | 0.899 | NOT_SIGNIFICANT | 0.917 | 0.256 | 100% |
| 300ETF | icw | 0.770 | 0.562 | NOT_SIGNIFICANT | 0.755 | 0.197 | 100% |
| 500ETF | icw | 1.073 | 0.779 | NOT_SIGNIFICANT | 0.973 | 0.478 | 100% |
| 159915ETF | icw | 1.125 | 0.826 | NOT_SIGNIFICANT | 0.998 | 0.214 | 100% |
| 300ETF | sortino | 0.793 | 0.604 | NOT_SIGNIFICANT | 0.748 | 0.364 | 87% |
| 500ETF | sortino | 0.994 | 0.723 | NOT_SIGNIFICANT | 0.935 | 0.514 | 93% |
| 159915ETF | sortino | 1.156 | 0.847 | NOT_SIGNIFICANT | 1.021 | 0.260 | 100% |
| 300ETF | ew | 1.046 | 0.897 | NOT_SIGNIFICANT | 0.838 | 0.185 | 100% |
| 500ETF | ew | 1.190 | 0.873 | NOT_SIGNIFICANT | 0.942 | 0.357 | 100% |
| 159915ETF | ew | 0.917 | 0.657 | NOT_SIGNIFICANT | 0.937 | 0.282 | 100% |

