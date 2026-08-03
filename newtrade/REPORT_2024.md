# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 60 | 49 (16L/33S) | 0.349 | 1.006 | +0.0329 | +0.0184 | 1.384 | +0.0145 | 0.943 | 0.0427 | 38.8% (L:37.5%, S:39.4%) | 39.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 145 | 102 (55L/47S) | 1.187 | 2.156 | +0.1643 | -0.0007 | -0.025 | +0.1650 | 5.145 | 0.0539 | 59.8% (L:56.4%, S:63.8%) | 85.0x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 116 | 90 (70L/20S) | 1.161 | 1.777 | +0.2184 | +0.0823 | 1.537 | +0.1361 | 5.722 | 0.0758 | 51.1% (L:48.6%, S:60.0%) | 71.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.30/S:1.60 (train L:1.20/S:1.50) | 60 | 35 (29L/6S) | -0.372 | 0.158 | -0.0329 | -0.0190 | -0.885 | -0.0139 | -13.831 | 0.0669 | 28.6% (L:31.0%, S:16.7%) | 29.0x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 145 | 120 (76L/44S) | 0.798 | 1.882 | +0.1211 | -0.0236 | -0.539 | +0.1447 | 4.814 | 0.0696 | 54.2% (L:48.7%, S:63.6%) | 98.8x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.60 (train L:0.80/S:1.50) | 116 | 86 (84L/2S) | 0.909 | 1.485 | +0.1828 | +0.1524 | 1.938 | +0.0304 | 8.095 | 0.1144 | 50.0% (L:50.0%, S:50.0%) | 68.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.349 | 0.151 | NOT_SIGNIFICANT | 0.095 | 0.371 | 73% |
| 500ETF | icw | 1.187 | 0.633 | NOT_SIGNIFICANT | 0.679 | 0.345 | 93% |
| 159915ETF | icw | 1.161 | 0.612 | NOT_SIGNIFICANT | 0.894 | 0.334 | 100% |
| 300ETF | ew | -0.372 | 0.021 | NOT_SIGNIFICANT | 0.218 | 0.297 | 60% |
| 500ETF | ew | 0.798 | 0.358 | NOT_SIGNIFICANT | 0.671 | 0.408 | 93% |
| 159915ETF | ew | 0.909 | 0.454 | NOT_SIGNIFICANT | 0.884 | 0.283 | 100% |

