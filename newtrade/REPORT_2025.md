# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_linear`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 95 | 20 (5L/15S) | 0.017 | 1.233 | +0.0003 | +0.0089 | 4.885 | -0.0086 | -2.527 | 0.0130 | 35.0% (L:40.0%, S:33.3%) | 29.6x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 76 (59L/17S) | -0.285 | 1.801 | -0.0140 | +0.0019 | 0.090 | -0.0159 | -2.381 | 0.0429 | 55.3% (L:55.9%, S:52.9%) | 113.8x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 146 | 78 (49L/29S) | 1.406 | 2.527 | +0.1262 | +0.0692 | 2.451 | +0.0570 | 2.620 | 0.0645 | 50.0% (L:51.0%, S:48.3%) | 121.7x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 95 | 8 (1L/7S) | 0.358 | 1.204 | +0.0034 | +0.0055 | 0.000 | -0.0021 | -1.558 | 0.0063 | 50.0% (L:100.0%, S:42.9%) | 12.0x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 75 (58L/17S) | -0.224 | 1.857 | -0.0109 | +0.0120 | 0.586 | -0.0229 | -3.533 | 0.0414 | 54.7% (L:56.9%, S:47.1%) | 110.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 146 | 56 (41L/15S) | 1.492 | 2.336 | +0.1218 | +0.0803 | 3.352 | +0.0415 | 3.020 | 0.0515 | 55.4% (L:56.1%, S:53.3%) | 86.0x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.017 | 0.060 | NOT_SIGNIFICANT | 0.423 | 0.250 | 87% |
| 500ETF | icw | -0.285 | 0.032 | NOT_SIGNIFICANT | 0.802 | 0.418 | 93% |
| 159915ETF | icw | 1.406 | 0.477 | NOT_SIGNIFICANT | 0.933 | 0.358 | 100% |
| 300ETF | ew | 0.358 | 0.110 | NOT_SIGNIFICANT | 0.109 | 0.285 | 73% |
| 500ETF | ew | -0.224 | 0.036 | NOT_SIGNIFICANT | 0.602 | 0.454 | 87% |
| 159915ETF | ew | 1.492 | 0.524 | NOT_SIGNIFICANT | 0.882 | 0.405 | 100% |

