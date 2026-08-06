# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 32 | 95 (56L/39S) | 0.360 | 1.062 | +0.0635 | +0.0428 | 1.166 | +0.0208 | 1.180 | 0.0526 | 53.7% (L:51.8%, S:56.4%) | 41.2x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 366 | 185 (105L/80S) | 0.647 | 1.734 | +0.1445 | -0.0391 | -0.818 | +0.1837 | 3.878 | 0.0526 | 52.4% (L:45.7%, S:61.3%) | 73.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 37 | 223 (152L/71S) | 1.084 | 1.738 | +0.4789 | +0.3517 | 2.342 | +0.1272 | 2.143 | 0.1188 | 53.4% (L:50.0%, S:60.6%) | 83.6x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 103 (41L/62S) | 0.305 | 1.055 | +0.0542 | +0.0572 | 1.928 | -0.0030 | -0.116 | 0.0544 | 52.4% (L:56.1%, S:50.0%) | 43.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.10/S:1.40) | 366 | 138 (86L/52S) | 0.783 | 1.637 | +0.1594 | -0.0376 | -0.960 | +0.1970 | 5.820 | 0.0421 | 54.3% (L:45.3%, S:69.2%) | 56.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 37 | 273 (160L/113S) | 1.122 | 1.893 | +0.5122 | +0.3286 | 2.122 | +0.1836 | 2.186 | 0.0994 | 53.5% (L:48.8%, S:60.2%) | 102.2x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 103 (42L/61S) | 0.267 | 1.020 | +0.0473 | +0.0552 | 1.836 | -0.0079 | -0.311 | 0.0571 | 51.5% (L:54.8%, S:49.2%) | 43.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 366 | 159 (107L/52S) | 0.789 | 1.755 | +0.1674 | -0.0404 | -0.845 | +0.2079 | 6.173 | 0.0481 | 54.7% (L:46.7%, S:71.2%) | 62.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 37 | 197 (125L/72S) | 1.061 | 1.690 | +0.4205 | +0.2999 | 2.598 | +0.1207 | 1.961 | 0.0750 | 53.8% (L:51.2%, S:58.3%) | 75.0x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 32 | 56 (13L/43S) | 0.316 | 0.797 | +0.0457 | +0.0689 | 5.568 | -0.0232 | -1.226 | 0.0622 | 53.6% (L:69.2%, S:48.8%) | 23.3x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 366 | 215 (136L/79S) | 0.761 | 1.963 | +0.1799 | -0.0195 | -0.320 | +0.1993 | 4.201 | 0.0454 | 54.4% (L:50.0%, S:62.0%) | 84.8x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 37 | 148 (145L/3S) | 0.875 | 1.386 | +0.3375 | +0.3505 | 2.386 | -0.0130 | -6.113 | 0.1075 | 49.3% (L:49.7%, S:33.3%) | 54.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.360 | 0.205 | NOT_SIGNIFICANT | 0.563 | 0.261 | 100% |
| 500ETF | ensemble | 0.647 | 0.429 | NOT_SIGNIFICANT | 0.932 | 0.398 | 100% |
| 159915ETF | ensemble | 1.084 | 0.879 | NOT_SIGNIFICANT | 0.964 | 0.438 | 100% |
| 300ETF | icw | 0.305 | 0.173 | NOT_SIGNIFICANT | 0.371 | 0.255 | 100% |
| 500ETF | icw | 0.783 | 0.588 | NOT_SIGNIFICANT | 0.955 | 0.422 | 100% |
| 159915ETF | icw | 1.122 | 0.887 | NOT_SIGNIFICANT | 1.164 | 0.324 | 100% |
| 300ETF | sortino | 0.267 | 0.153 | NOT_SIGNIFICANT | 0.354 | 0.282 | 93% |
| 500ETF | sortino | 0.789 | 0.579 | NOT_SIGNIFICANT | 0.935 | 0.410 | 100% |
| 159915ETF | sortino | 1.061 | 0.869 | NOT_SIGNIFICANT | 0.900 | 0.469 | 100% |
| 300ETF | ew | 0.316 | 0.185 | NOT_SIGNIFICANT | 0.591 | 0.255 | 100% |
| 500ETF | ew | 0.761 | 0.526 | NOT_SIGNIFICANT | 1.025 | 0.465 | 93% |
| 159915ETF | ew | 0.875 | 0.720 | NOT_SIGNIFICANT | 0.913 | 0.430 | 100% |

