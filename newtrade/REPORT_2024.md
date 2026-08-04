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
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.10 (train L:1.50/S:1.00) | 60 | 56 (17L/39S) | 0.512 | 1.267 | +0.0492 | +0.0205 | 1.622 | +0.0286 | 1.491 | 0.0429 | 42.9% (L:41.2%, S:43.6%) | 45.8x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 145 | 102 (55L/47S) | 1.187 | 2.156 | +0.1643 | -0.0007 | -0.025 | +0.1650 | 5.145 | 0.0539 | 59.8% (L:56.4%, S:63.8%) | 85.0x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 116 | 90 (70L/20S) | 1.161 | 1.777 | +0.2184 | +0.0823 | 1.537 | +0.1361 | 5.722 | 0.0758 | 51.1% (L:48.6%, S:60.0%) | 71.4x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.10 (train L:1.50/S:1.00) | 60 | 54 (15L/39S) | 0.469 | 1.206 | +0.0449 | +0.0166 | 1.400 | +0.0283 | 1.479 | 0.0430 | 42.6% (L:40.0%, S:43.6%) | 45.1x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 145 | 122 (75L/47S) | 1.027 | 2.136 | +0.1509 | -0.0142 | -0.362 | +0.1651 | 5.148 | 0.0585 | 54.9% (L:49.3%, S:63.8%) | 99.6x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 116 | 119 (99L/20S) | 0.975 | 1.658 | +0.2283 | +0.0920 | 1.026 | +0.1363 | 5.736 | 0.0993 | 47.9% (L:45.5%, S:60.0%) | 92.6x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.00 (train L:1.00/S:0.90) | 60 | 98 (50L/48S) | -0.117 | 0.908 | -0.0150 | -0.0343 | -1.062 | +0.0193 | 0.769 | 0.0789 | 37.8% (L:36.0%, S:39.6%) | 80.0x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 145 | 132 (99L/33S) | 0.665 | 1.859 | +0.1024 | -0.0024 | -0.044 | +0.1048 | 4.267 | 0.0677 | 53.8% (L:50.5%, S:63.6%) | 104.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 116 | 109 (82L/27S) | 0.974 | 1.723 | +0.1896 | +0.0496 | 0.811 | +0.1400 | 4.938 | 0.1084 | 50.5% (L:47.6%, S:59.3%) | 87.0x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.512 | 0.227 | NOT_SIGNIFICANT | 0.409 | 0.310 | 80% |
| 500ETF | icw | 1.187 | 0.633 | NOT_SIGNIFICANT | 0.679 | 0.345 | 93% |
| 159915ETF | icw | 1.161 | 0.612 | NOT_SIGNIFICANT | 0.842 | 0.385 | 100% |
| 300ETF | sortino | 0.469 | 0.204 | NOT_SIGNIFICANT | 0.495 | 0.262 | 93% |
| 500ETF | sortino | 1.027 | 0.512 | NOT_SIGNIFICANT | 0.719 | 0.341 | 93% |
| 159915ETF | sortino | 0.975 | 0.501 | NOT_SIGNIFICANT | 0.925 | 0.363 | 100% |
| 300ETF | ew | -0.117 | 0.042 | NOT_SIGNIFICANT | 0.153 | 0.246 | 80% |
| 500ETF | ew | 0.665 | 0.280 | NOT_SIGNIFICANT | 0.795 | 0.463 | 93% |
| 159915ETF | ew | 0.974 | 0.467 | NOT_SIGNIFICANT | 0.967 | 0.448 | 100% |

