# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 95 | 20 (5L/15S) | -0.118 | 1.184 | -0.0022 | +0.0054 | 2.855 | -0.0076 | -2.395 | 0.0152 | 35.0% (L:40.0%, S:33.3%) | 29.8x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 76 (59L/17S) | -0.181 | 1.920 | -0.0089 | +0.0052 | 0.251 | -0.0141 | -2.062 | 0.0409 | 55.3% (L:55.9%, S:52.9%) | 115.5x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 146 | 62 (49L/13S) | 1.415 | 2.361 | +0.1179 | +0.0616 | 2.205 | +0.0563 | 4.588 | 0.0528 | 51.6% (L:51.0%, S:53.8%) | 97.3x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 95 | 8 (1L/7S) | 0.333 | 1.163 | +0.0035 | +0.0054 | 0.000 | -0.0019 | -1.222 | 0.0068 | 50.0% (L:100.0%, S:42.9%) | 12.8x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 159 | 52 (35L/17S) | -0.756 | 1.013 | -0.0308 | -0.0072 | -0.596 | -0.0236 | -3.611 | 0.0442 | 50.0% (L:51.4%, S:47.1%) | 81.5x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 146 | 56 (41L/15S) | 1.516 | 2.362 | +0.1221 | +0.0774 | 3.263 | +0.0447 | 3.315 | 0.0513 | 55.4% (L:56.1%, S:53.3%) | 86.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.118 | 0.045 | NOT_SIGNIFICANT | 0.410 | 0.260 | 87% |
| 500ETF | icw | -0.181 | 0.040 | NOT_SIGNIFICANT | 0.822 | 0.418 | 93% |
| 159915ETF | icw | 1.415 | 0.491 | NOT_SIGNIFICANT | 0.900 | 0.352 | 100% |
| 300ETF | ew | 0.333 | 0.106 | NOT_SIGNIFICANT | 0.131 | 0.278 | 73% |
| 500ETF | ew | -0.756 | 0.010 | NOT_SIGNIFICANT | 0.619 | 0.453 | 93% |
| 159915ETF | ew | 1.516 | 0.542 | NOT_SIGNIFICANT | 0.887 | 0.418 | 100% |

