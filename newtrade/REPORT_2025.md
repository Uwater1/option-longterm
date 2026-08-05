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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 60 | 11 (2L/9S) | -0.469 | 0.574 | -0.0067 | +0.0067 | 7.901 | -0.0134 | -7.895 | 0.0086 | 36.4% (L:50.0%, S:33.3%) | 19.5x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 258 | 43 (33L/10S) | -0.691 | 0.926 | -0.0255 | -0.0006 | -0.053 | -0.0249 | -6.217 | 0.0408 | 53.5% (L:57.6%, S:40.0%) | 68.0x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 168 | 69 (55L/14S) | 0.993 | 2.017 | +0.0895 | +0.0535 | 1.723 | +0.0360 | 2.446 | 0.0564 | 50.7% (L:50.9%, S:50.0%) | 110.3x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.30 (train L:1.40/S:1.20) | 60 | 13 (4L/9S) | -0.765 | 0.409 | -0.0114 | +0.0021 | 1.468 | -0.0135 | -7.886 | 0.0127 | 30.8% (L:25.0%, S:33.3%) | 22.7x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 258 | 43 (33L/10S) | -0.696 | 0.920 | -0.0257 | -0.0007 | -0.062 | -0.0250 | -6.237 | 0.0408 | 53.5% (L:57.6%, S:40.0%) | 68.0x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 168 | 69 (55L/14S) | 0.996 | 2.020 | +0.0899 | +0.0532 | 1.715 | +0.0367 | 2.485 | 0.0564 | 50.7% (L:50.9%, S:50.0%) | 110.4x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 60 | 15 (3L/12S) | 0.398 | 1.276 | +0.0085 | +0.0064 | 5.913 | +0.0022 | 0.519 | 0.0119 | 40.0% (L:33.3%, S:41.7%) | 24.5x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.50 (train L:0.90/S:1.40) | 258 | 40 (33L/7S) | -0.585 | 0.930 | -0.0210 | +0.0081 | 0.679 | -0.0291 | -15.617 | 0.0372 | 55.0% (L:60.6%, S:28.6%) | 60.6x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 168 | 67 (47L/20S) | 0.983 | 1.996 | +0.0873 | +0.0466 | 1.666 | +0.0406 | 2.315 | 0.0570 | 50.7% (L:48.9%, S:55.0%) | 111.2x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.469 | 0.022 | NOT_SIGNIFICANT | 0.546 | 0.168 | 100% |
| 500ETF | icw | -0.691 | 0.012 | NOT_SIGNIFICANT | 0.785 | 0.384 | 93% |
| 159915ETF | icw | 0.993 | 0.294 | NOT_SIGNIFICANT | 1.162 | 0.380 | 100% |
| 300ETF | sortino | -0.765 | 0.011 | NOT_SIGNIFICANT | 0.402 | 0.209 | 100% |
| 500ETF | sortino | -0.696 | 0.011 | NOT_SIGNIFICANT | 0.747 | 0.452 | 93% |
| 159915ETF | sortino | 0.996 | 0.295 | NOT_SIGNIFICANT | 1.075 | 0.356 | 100% |
| 300ETF | ew | 0.398 | 0.122 | NOT_SIGNIFICANT | 0.486 | 0.190 | 100% |
| 500ETF | ew | -0.585 | 0.015 | NOT_SIGNIFICANT | 1.024 | 0.511 | 93% |
| 159915ETF | ew | 0.983 | 0.293 | NOT_SIGNIFICANT | 0.948 | 0.364 | 100% |

