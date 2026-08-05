# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 103 (41L/62S) | 0.305 | 1.055 | +0.0542 | +0.0572 | 1.928 | -0.0030 | -0.116 | 0.0544 | 52.4% (L:56.1%, S:50.0%) | 43.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.10/S:1.40) | 366 | 138 (86L/52S) | 0.783 | 1.637 | +0.1594 | -0.0376 | -0.960 | +0.1970 | 5.820 | 0.0421 | 54.3% (L:45.3%, S:69.2%) | 56.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 37 | 273 (160L/113S) | 1.122 | 1.893 | +0.5122 | +0.3286 | 2.122 | +0.1836 | 2.186 | 0.0994 | 53.5% (L:48.8%, S:60.2%) | 102.2x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 104 (41L/63S) | 0.259 | 1.015 | +0.0462 | +0.0572 | 1.930 | -0.0111 | -0.419 | 0.0623 | 51.9% (L:56.1%, S:49.2%) | 43.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 366 | 159 (107L/52S) | 0.776 | 1.744 | +0.1643 | -0.0359 | -0.754 | +0.2002 | 5.911 | 0.0481 | 54.1% (L:46.7%, S:69.2%) | 62.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 37 | 234 (160L/74S) | 0.969 | 1.649 | +0.4328 | +0.3084 | 1.985 | +0.1244 | 1.990 | 0.1108 | 51.3% (L:48.1%, S:58.1%) | 87.9x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 32 | 81 (14L/67S) | 0.269 | 0.940 | +0.0404 | +0.0665 | 5.099 | -0.0261 | -1.013 | 0.0692 | 49.4% (L:64.3%, S:46.3%) | 30.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 366 | 218 (133L/85S) | 0.671 | 1.880 | +0.1617 | -0.0352 | -0.574 | +0.1969 | 3.911 | 0.0733 | 52.8% (L:50.4%, S:56.5%) | 85.3x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.60/S:1.20 (train L:0.50/S:1.10) | 37 | 291 (220L/71S) | 0.931 | 1.745 | +0.4518 | +0.3339 | 1.628 | +0.1179 | 1.981 | 0.1233 | 51.2% (L:49.1%, S:57.7%) | 105.9x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.305 | 0.173 | NOT_SIGNIFICANT | 0.371 | 0.255 | 100% |
| 500ETF | icw | 0.783 | 0.588 | NOT_SIGNIFICANT | 0.955 | 0.422 | 100% |
| 159915ETF | icw | 1.122 | 0.887 | NOT_SIGNIFICANT | 1.272 | 0.326 | 100% |
| 300ETF | sortino | 0.259 | 0.149 | NOT_SIGNIFICANT | 0.466 | 0.241 | 100% |
| 500ETF | sortino | 0.776 | 0.566 | NOT_SIGNIFICANT | 0.951 | 0.410 | 100% |
| 159915ETF | sortino | 0.969 | 0.787 | NOT_SIGNIFICANT | 1.034 | 0.365 | 100% |
| 300ETF | ew | 0.269 | 0.156 | NOT_SIGNIFICANT | 0.558 | 0.220 | 100% |
| 500ETF | ew | 0.671 | 0.439 | NOT_SIGNIFICANT | 0.991 | 0.453 | 93% |
| 159915ETF | ew | 0.931 | 0.735 | NOT_SIGNIFICANT | 0.702 | 0.514 | 93% |

