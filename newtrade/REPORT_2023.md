# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.70/S:1.40 (train L:1.50/S:1.20) | 47 | 28 (16L/12S) | 0.396 | 0.683 | +0.0413 | +0.0624 | 4.392 | -0.0211 | -5.503 | 0.0326 | 57.1% (L:68.8%, S:41.7%) | 13.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.40 (train L:1.10/S:1.20) | 297 | 104 (54L/50S) | 0.975 | 1.722 | +0.1626 | -0.0279 | -1.022 | +0.1906 | 5.800 | 0.0396 | 54.8% (L:42.6%, S:68.0%) | 54.1x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.70/S:1.00) | 77 | 139 (110L/29S) | 1.193 | 1.752 | +0.3557 | +0.2318 | 2.237 | +0.1240 | 4.974 | 0.0899 | 51.1% (L:47.3%, S:65.5%) | 66.7x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.30/S:1.30) | 47 | 31 (25L/6S) | 0.249 | 0.590 | +0.0272 | +0.0447 | 2.288 | -0.0175 | -9.362 | 0.0337 | 51.6% (L:56.0%, S:33.3%) | 16.8x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.60 (train L:1.10/S:1.40) | 297 | 86 (53L/33S) | 0.715 | 1.363 | +0.1138 | -0.0330 | -1.231 | +0.1468 | 5.898 | 0.0422 | 52.3% (L:41.5%, S:69.7%) | 43.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 77 | 149 (104L/45S) | 1.173 | 1.789 | +0.3396 | +0.2430 | 2.433 | +0.0966 | 3.509 | 0.0709 | 53.0% (L:48.1%, S:64.4%) | 72.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.30/S:1.30) | 47 | 31 (25L/6S) | 0.253 | 0.592 | +0.0276 | +0.0445 | 2.276 | -0.0170 | -9.229 | 0.0332 | 51.6% (L:56.0%, S:33.3%) | 16.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.40 (train L:1.10/S:1.20) | 297 | 105 (52L/53S) | 0.942 | 1.694 | +0.1566 | -0.0356 | -1.340 | +0.1922 | 5.655 | 0.0420 | 54.3% (L:40.4%, S:67.9%) | 53.6x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 77 | 148 (103L/45S) | 1.200 | 1.813 | +0.3472 | +0.2503 | 2.522 | +0.0968 | 3.519 | 0.0635 | 53.4% (L:48.5%, S:64.4%) | 72.1x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.30 (train L:1.10/S:1.10) | 47 | 55 (35L/20S) | 0.149 | 0.682 | +0.0188 | +0.0299 | 1.188 | -0.0111 | -1.321 | 0.0496 | 52.7% (L:54.3%, S:50.0%) | 29.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.80/S:1.20) | 297 | 162 (111L/51S) | 0.662 | 1.782 | +0.1234 | -0.0526 | -1.026 | +0.1760 | 5.294 | 0.0543 | 51.9% (L:45.0%, S:66.7%) | 80.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 77 | 162 (109L/53S) | 1.418 | 2.004 | +0.4656 | +0.2529 | 2.441 | +0.2128 | 4.339 | 0.0758 | 55.6% (L:48.6%, S:69.8%) | 78.0x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.396 | 0.227 | NOT_SIGNIFICANT | 0.568 | 0.219 | 100% |
| 500ETF | ensemble | 0.975 | 0.677 | NOT_SIGNIFICANT | 0.786 | 0.441 | 100% |
| 159915ETF | ensemble | 1.193 | 0.855 | NOT_SIGNIFICANT | 1.159 | 0.379 | 100% |
| 300ETF | icw | 0.249 | 0.136 | NOT_SIGNIFICANT | 0.496 | 0.224 | 100% |
| 500ETF | icw | 0.715 | 0.449 | NOT_SIGNIFICANT | 0.975 | 0.388 | 100% |
| 159915ETF | icw | 1.173 | 0.846 | NOT_SIGNIFICANT | 1.184 | 0.317 | 100% |
| 300ETF | sortino | 0.253 | 0.137 | NOT_SIGNIFICANT | 0.477 | 0.249 | 100% |
| 500ETF | sortino | 0.942 | 0.647 | NOT_SIGNIFICANT | 0.831 | 0.345 | 100% |
| 159915ETF | sortino | 1.200 | 0.863 | NOT_SIGNIFICANT | 1.163 | 0.357 | 100% |
| 300ETF | ew | 0.149 | 0.095 | NOT_SIGNIFICANT | 0.462 | 0.207 | 100% |
| 500ETF | ew | 0.662 | 0.366 | NOT_SIGNIFICANT | 0.944 | 0.447 | 93% |
| 159915ETF | ew | 1.418 | 0.958 | SIGNIFICANT | 1.192 | 0.423 | 100% |

