# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.70 (train L:1.00/S:1.50) | 26 | 60 (56L/4S) | 0.407 | 0.893 | +0.0630 | +0.0518 | 1.451 | +0.0112 | 4.351 | 0.0385 | 55.0% (L:53.6%, S:75.0%) | 25.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.70 (train L:1.00/S:1.50) | 317 | 112 (82L/30S) | 0.545 | 1.220 | +0.1037 | -0.0442 | -1.157 | +0.1479 | 6.619 | 0.0603 | 52.7% (L:45.1%, S:73.3%) | 39.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.70 (train L:0.70/S:1.50) | 37 | 123 (121L/2S) | 0.827 | 1.285 | +0.2697 | +0.2772 | 2.437 | -0.0074 | -6.513 | 0.0855 | 49.6% (L:49.6%, S:50.0%) | 43.9x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.50/S:1.70 (train L:1.30/S:1.50) | 26 | 31 (29L/2S) | 0.675 | 0.937 | +0.0906 | +0.0941 | 4.339 | -0.0034 | -2.247 | 0.0319 | 64.5% (L:65.5%, S:50.0%) | 12.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.60 (train L:1.00/S:1.40) | 317 | 125 (83L/42S) | 0.620 | 1.369 | +0.1205 | -0.0458 | -1.206 | +0.1663 | 5.891 | 0.0473 | 52.8% (L:44.6%, S:69.0%) | 46.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.70/S:1.00) | 37 | 202 (128L/74S) | 1.179 | 1.772 | +0.4650 | +0.3231 | 2.775 | +0.1419 | 2.307 | 0.0716 | 54.5% (L:51.6%, S:59.5%) | 70.9x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.70 (train L:1.10/S:1.50) | 26 | 51 (49L/2S) | 0.462 | 0.891 | +0.0679 | +0.0713 | 2.241 | -0.0034 | -2.247 | 0.0411 | 54.9% (L:55.1%, S:50.0%) | 21.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.00/S:1.20) | 317 | 147 (83L/64S) | 0.727 | 1.583 | +0.1491 | -0.0467 | -1.230 | +0.1957 | 5.040 | 0.0477 | 53.1% (L:44.6%, S:64.1%) | 56.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 37 | 235 (125L/110S) | 1.256 | 1.931 | +0.5057 | +0.3231 | 2.808 | +0.1826 | 2.290 | 0.0657 | 55.7% (L:51.2%, S:60.9%) | 82.4x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.30/S:1.20) | 26 | 45 (27L/18S) | 0.704 | 1.019 | +0.1086 | +0.0813 | 3.913 | +0.0273 | 2.350 | 0.0509 | 60.0% (L:63.0%, S:55.6%) | 17.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.80/S:1.20) | 317 | 210 (143L/67S) | 0.652 | 1.787 | +0.1480 | -0.0503 | -0.806 | +0.1983 | 4.976 | 0.0789 | 55.2% (L:50.3%, S:65.7%) | 76.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.70 (train L:0.70/S:1.50) | 37 | 118 (115L/3S) | 0.801 | 1.247 | +0.2627 | +0.2760 | 2.486 | -0.0133 | -7.121 | 0.0769 | 48.3% (L:48.7%, S:33.3%) | 42.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.407 | 0.247 | NOT_SIGNIFICANT | 0.507 | 0.214 | 100% |
| 500ETF | ensemble | 0.545 | 0.362 | NOT_SIGNIFICANT | 0.936 | 0.440 | 93% |
| 159915ETF | ensemble | 0.827 | 0.693 | NOT_SIGNIFICANT | 1.049 | 0.462 | 100% |
| 300ETF | icw | 0.675 | 0.594 | NOT_SIGNIFICANT | 0.746 | 0.268 | 100% |
| 500ETF | icw | 0.620 | 0.432 | NOT_SIGNIFICANT | 0.842 | 0.343 | 93% |
| 159915ETF | icw | 1.179 | 0.939 | MARGINAL | 1.017 | 0.353 | 100% |
| 300ETF | sortino | 0.462 | 0.302 | NOT_SIGNIFICANT | 0.464 | 0.156 | 100% |
| 500ETF | sortino | 0.727 | 0.531 | NOT_SIGNIFICANT | 0.828 | 0.303 | 93% |
| 159915ETF | sortino | 1.256 | 0.958 | SIGNIFICANT | 0.972 | 0.332 | 100% |
| 300ETF | ew | 0.704 | 0.545 | NOT_SIGNIFICANT | 0.655 | 0.212 | 100% |
| 500ETF | ew | 0.652 | 0.428 | NOT_SIGNIFICANT | 1.030 | 0.422 | 93% |
| 159915ETF | ew | 0.801 | 0.660 | NOT_SIGNIFICANT | 0.979 | 0.447 | 100% |

