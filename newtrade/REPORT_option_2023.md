# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Mode**: `Option Portfolio`
- **Initial Capital**: `100,000 RMB per ETF`
- **Trade Budget**: `10% of portfolio capital per signal`
- **Commission**: `4.0 RMB per contract per side (8.0 RMB round-trip per contract)`
- **Option Selection**: `Nearest OTM, >=7 DTM`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_option_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 61 | 68 opt | 1.162 | 1.438 | +59,019 RMB | +0.2603 | 3.156 | +0.3299 | 5.015 | 0.1299 | 55.9% (L:51.6%, S:59.5%) | 38.5x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 338 | 126 opt | 1.243 | 1.485 | +85,398 RMB | +0.1740 | 0.994 | +0.6800 | 6.620 | 0.2437 | 53.2% (L:48.8%, S:60.9%) | 68.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.60 (train L:1.00/S:1.50) | 78 | 70 opt | 1.376 | 1.591 | +96,116 RMB | +0.7815 | 4.284 | +0.1797 | 8.832 | 0.1195 | 48.6% (L:48.5%, S:50.0%) | 36.4x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 61 | 68 opt | 1.207 | 1.479 | +61,588 RMB | +0.2962 | 3.654 | +0.3197 | 4.757 | 0.1320 | 55.9% (L:53.3%, S:57.9%) | 39.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 338 | 123 opt | 1.197 | 1.435 | +81,059 RMB | +0.1654 | 0.963 | +0.6451 | 6.532 | 0.2388 | 52.8% (L:48.1%, S:61.4%) | 67.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 78 | 70 opt | 1.376 | 1.591 | +96,116 RMB | +0.7815 | 4.284 | +0.1797 | 8.832 | 0.1195 | 48.6% (L:48.5%, S:50.0%) | 36.5x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 61 | 113 opt | 1.094 | 1.431 | +95,138 RMB | +0.6463 | 2.957 | +0.3051 | 2.805 | 0.1772 | 51.3% (L:49.2%, S:53.8%) | 63.2x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 338 | 179 opt | 1.033 | 1.306 | +81,508 RMB | +0.1842 | 0.728 | +0.6309 | 4.764 | 0.2024 | 48.0% (L:45.5%, S:53.4%) | 92.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.60 (train L:1.20/S:1.50) | 78 | 44 opt | 0.754 | 0.956 | +30,917 RMB | +0.1794 | 2.207 | +0.1297 | 14.868 | 0.1775 | 45.5% (L:45.2%, S:50.0%) | 22.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.162 | 0.791 | NOT_SIGNIFICANT | 0.356 | 0.236 | 100% |
| 500ETF | icw | 1.243 | 0.767 | NOT_SIGNIFICANT | 0.895 | 0.314 | 100% |
| 159915ETF | icw | 1.376 | 0.913 | MARGINAL | 1.105 | 0.256 | 100% |
| 300ETF | sortino | 1.207 | 0.826 | NOT_SIGNIFICANT | 0.338 | 0.253 | 100% |
| 500ETF | sortino | 1.197 | 0.740 | NOT_SIGNIFICANT | 0.834 | 0.330 | 100% |
| 159915ETF | sortino | 1.376 | 0.913 | MARGINAL | 1.242 | 0.262 | 100% |
| 300ETF | ew | 1.094 | 0.790 | NOT_SIGNIFICANT | 0.177 | 0.222 | 87% |
| 500ETF | ew | 1.033 | 0.632 | NOT_SIGNIFICANT | 0.843 | 0.458 | 93% |
| 159915ETF | ew | 0.754 | 0.468 | NOT_SIGNIFICANT | 1.138 | 0.353 | 100% |

