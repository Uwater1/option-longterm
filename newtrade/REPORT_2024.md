# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.70/S:1.40 (train L:1.50/S:1.20) | 37 | 30 (12L/18S) | 0.403 | 0.795 | +0.0329 | +0.0482 | 3.988 | -0.0153 | -4.168 | 0.0276 | 43.3% (L:58.3%, S:33.3%) | 21.7x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:0.90/S:1.20) | 111 | 89 (55L/34S) | 0.428 | 1.250 | +0.0588 | -0.0605 | -1.849 | +0.1192 | 4.879 | 0.0758 | 53.9% (L:47.3%, S:64.7%) | 68.8x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.70 (train L:0.90/S:1.50) | 99 | 59 (58L/1S) | 1.224 | 1.653 | +0.2174 | +0.1724 | 3.041 | +0.0451 | 0.000 | 0.0557 | 54.2% (L:53.4%, S:100.0%) | 45.0x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.40/S:1.30) | 37 | 25 (14L/11S) | 0.450 | 0.798 | +0.0368 | +0.0433 | 3.244 | -0.0065 | -2.742 | 0.0307 | 48.0% (L:50.0%, S:45.5%) | 19.4x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:0.90/S:1.20) | 111 | 92 (55L/37S) | 0.471 | 1.285 | +0.0665 | -0.0671 | -2.030 | +0.1336 | 5.034 | 0.0869 | 53.3% (L:45.5%, S:64.9%) | 70.9x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.00/S:1.10) | 99 | 71 (52L/19S) | 1.422 | 1.869 | +0.2666 | +0.1506 | 3.093 | +0.1160 | 5.553 | 0.0578 | 59.2% (L:55.8%, S:68.4%) | 51.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.40/S:1.40 (train L:1.20/S:1.20) | 37 | 38 (22L/16S) | 0.190 | 0.712 | +0.0171 | +0.0318 | 1.709 | -0.0148 | -4.362 | 0.0352 | 39.5% (L:45.5%, S:31.2%) | 31.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:0.90/S:1.20) | 111 | 92 (55L/37S) | 0.456 | 1.273 | +0.0643 | -0.0684 | -2.069 | +0.1327 | 5.017 | 0.0869 | 52.2% (L:43.6%, S:64.9%) | 71.0x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.50/S:1.10) | 99 | 132 (113L/19S) | 1.038 | 1.685 | +0.2775 | +0.1615 | 1.379 | +0.1160 | 5.565 | 0.1204 | 48.5% (L:45.1%, S:68.4%) | 96.9x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.40/S:1.30 (train L:1.20/S:1.10) | 37 | 47 (23L/24S) | 0.265 | 0.848 | +0.0259 | +0.0195 | 1.022 | +0.0064 | 0.677 | 0.0366 | 38.3% (L:39.1%, S:37.5%) | 36.5x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.30/S:1.40 (train L:1.10/S:1.20) | 111 | 67 (33L/34S) | 0.756 | 1.394 | +0.0968 | -0.0402 | -1.891 | +0.1369 | 5.561 | 0.0471 | 55.2% (L:42.4%, S:67.6%) | 52.1x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.70 (train L:0.60/S:1.50) | 99 | 95 (94L/1S) | 1.131 | 1.659 | +0.2725 | +0.2274 | 2.235 | +0.0451 | 0.000 | 0.1006 | 48.4% (L:47.9%, S:100.0%) | 72.0x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.403 | 0.188 | NOT_SIGNIFICANT | 0.376 | 0.309 | 100% |
| 500ETF | ensemble | 0.428 | 0.172 | NOT_SIGNIFICANT | 0.870 | 0.435 | 100% |
| 159915ETF | ensemble | 1.224 | 0.672 | NOT_SIGNIFICANT | 1.089 | 0.247 | 100% |
| 300ETF | icw | 0.450 | 0.216 | NOT_SIGNIFICANT | 0.434 | 0.294 | 100% |
| 500ETF | icw | 0.471 | 0.190 | NOT_SIGNIFICANT | 0.880 | 0.436 | 100% |
| 159915ETF | icw | 1.422 | 0.787 | NOT_SIGNIFICANT | 0.852 | 0.331 | 100% |
| 300ETF | sortino | 0.190 | 0.098 | NOT_SIGNIFICANT | 0.387 | 0.324 | 93% |
| 500ETF | sortino | 0.456 | 0.183 | NOT_SIGNIFICANT | 0.867 | 0.416 | 100% |
| 159915ETF | sortino | 1.038 | 0.567 | NOT_SIGNIFICANT | 1.024 | 0.319 | 100% |
| 300ETF | ew | 0.265 | 0.120 | NOT_SIGNIFICANT | 0.366 | 0.261 | 100% |
| 500ETF | ew | 0.756 | 0.359 | NOT_SIGNIFICANT | 0.964 | 0.408 | 100% |
| 159915ETF | ew | 1.131 | 0.663 | NOT_SIGNIFICANT | 0.857 | 0.320 | 100% |

