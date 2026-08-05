# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 61 | 68 (31L/37S) | 0.556 | 1.170 | +0.0784 | +0.0426 | 1.844 | +0.0357 | 1.879 | 0.0464 | 52.9% (L:48.4%, S:56.8%) | 38.5x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 338 | 126 (80L/46S) | 0.802 | 1.760 | +0.1387 | -0.0289 | -0.764 | +0.1676 | 5.404 | 0.0475 | 54.0% (L:45.0%, S:69.6%) | 68.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.60 (train L:1.00/S:1.50) | 78 | 70 (66L/4S) | 1.353 | 1.690 | +0.3373 | +0.2874 | 4.185 | +0.0499 | 9.250 | 0.0485 | 58.6% (L:57.6%, S:75.0%) | 36.4x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 61 | 68 (30L/38S) | 0.579 | 1.194 | +0.0814 | +0.0492 | 2.185 | +0.0322 | 1.662 | 0.0416 | 52.9% (L:50.0%, S:55.3%) | 39.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 338 | 123 (79L/44S) | 0.781 | 1.723 | +0.1349 | -0.0301 | -0.802 | +0.1650 | 5.462 | 0.0476 | 53.7% (L:44.3%, S:70.5%) | 67.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 78 | 70 (66L/4S) | 1.342 | 1.674 | +0.3419 | +0.2915 | 4.144 | +0.0505 | 9.302 | 0.0486 | 58.6% (L:57.6%, S:75.0%) | 36.5x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 61 | 113 (61L/52S) | 0.341 | 1.293 | +0.0542 | +0.0295 | 0.780 | +0.0248 | 1.021 | 0.0666 | 51.3% (L:49.2%, S:53.8%) | 63.2x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 338 | 179 (121L/58S) | 0.545 | 1.791 | +0.1057 | -0.0496 | -0.894 | +0.1552 | 4.099 | 0.0593 | 52.0% (L:47.9%, S:60.3%) | 92.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.60 (train L:1.20/S:1.50) | 78 | 44 (42L/2S) | 1.039 | 1.366 | +0.1672 | +0.1223 | 3.680 | +0.0449 | 15.784 | 0.0538 | 56.8% (L:57.1%, S:50.0%) | 22.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.556 | 0.314 | NOT_SIGNIFICANT | 0.356 | 0.236 | 100% |
| 500ETF | icw | 0.802 | 0.498 | NOT_SIGNIFICANT | 0.895 | 0.314 | 100% |
| 159915ETF | icw | 1.353 | 0.968 | SIGNIFICANT | 1.105 | 0.256 | 100% |
| 300ETF | sortino | 0.579 | 0.334 | NOT_SIGNIFICANT | 0.338 | 0.253 | 100% |
| 500ETF | sortino | 0.781 | 0.480 | NOT_SIGNIFICANT | 0.834 | 0.330 | 100% |
| 159915ETF | sortino | 1.342 | 0.969 | SIGNIFICANT | 1.242 | 0.262 | 100% |
| 300ETF | ew | 0.341 | 0.169 | NOT_SIGNIFICANT | 0.177 | 0.222 | 87% |
| 500ETF | ew | 0.545 | 0.280 | NOT_SIGNIFICANT | 0.843 | 0.458 | 93% |
| 159915ETF | ew | 1.039 | 0.697 | NOT_SIGNIFICANT | 1.138 | 0.353 | 100% |

