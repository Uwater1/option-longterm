# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Score Weight (75% TailIC + 25% Sortino)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.10 (train L:1.50/S:1.00) | 60 | 55 (16L/39S) | 0.641 | 1.268 | +0.0722 | +0.0356 | 2.436 | +0.0366 | 1.666 | 0.0430 | 41.8% (L:43.8%, S:41.0%) | 45.8x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.60 (train L:1.00/S:1.50) | 145 | 99 (73L/26S) | 0.684 | 1.644 | +0.0949 | +0.0059 | 0.145 | +0.0890 | 4.426 | 0.0439 | 54.5% (L:50.7%, S:65.4%) | 79.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.60 (train L:0.90/S:1.50) | 116 | 70 (68L/2S) | 0.982 | 1.485 | +0.1842 | +0.1375 | 2.091 | +0.0467 | 17.100 | 0.0794 | 48.6% (L:47.1%, S:100.0%) | 55.7x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 60 | 49 (16L/33S) | 0.349 | 1.006 | +0.0329 | +0.0184 | 1.384 | +0.0145 | 0.943 | 0.0427 | 38.8% (L:37.5%, S:39.4%) | 39.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 145 | 102 (55L/47S) | 1.187 | 2.156 | +0.1643 | -0.0007 | -0.025 | +0.1650 | 5.145 | 0.0539 | 59.8% (L:56.4%, S:63.8%) | 85.0x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 116 | 90 (70L/20S) | 1.161 | 1.777 | +0.2184 | +0.0823 | 1.537 | +0.1361 | 5.722 | 0.0758 | 51.1% (L:48.6%, S:60.0%) | 71.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 60 | 51 (19L/32S) | 0.460 | 1.107 | +0.0465 | +0.0313 | 1.935 | +0.0152 | 1.012 | 0.0419 | 41.2% (L:42.1%, S:40.6%) | 41.7x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 145 | 122 (75L/47S) | 1.027 | 2.136 | +0.1509 | -0.0142 | -0.362 | +0.1651 | 5.148 | 0.0585 | 54.9% (L:49.3%, S:63.8%) | 99.6x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 116 | 119 (99L/20S) | 0.975 | 1.658 | +0.2283 | +0.0920 | 1.026 | +0.1363 | 5.736 | 0.0993 | 47.9% (L:45.5%, S:60.0%) | 92.6x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.20 (train L:1.10/S:1.10) | 60 | 71 (41L/30S) | 0.301 | 1.106 | +0.0341 | +0.0118 | 0.424 | +0.0223 | 1.482 | 0.0717 | 39.4% (L:39.0%, S:40.0%) | 56.6x |
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
| 300ETF | score | 0.641 | 0.326 | NOT_SIGNIFICANT | 0.291 | 0.323 | 87% |
| 500ETF | score | 0.684 | 0.298 | NOT_SIGNIFICANT | 0.858 | 0.414 | 93% |
| 159915ETF | score | 0.982 | 0.513 | NOT_SIGNIFICANT | 0.958 | 0.281 | 100% |
| 300ETF | icw | 0.349 | 0.151 | NOT_SIGNIFICANT | 0.095 | 0.371 | 73% |
| 500ETF | icw | 1.187 | 0.633 | NOT_SIGNIFICANT | 0.679 | 0.345 | 93% |
| 159915ETF | icw | 1.161 | 0.612 | NOT_SIGNIFICANT | 0.894 | 0.334 | 100% |
| 300ETF | sortino | 0.460 | 0.205 | NOT_SIGNIFICANT | 0.242 | 0.343 | 73% |
| 500ETF | sortino | 1.027 | 0.512 | NOT_SIGNIFICANT | 0.719 | 0.341 | 93% |
| 159915ETF | sortino | 0.975 | 0.501 | NOT_SIGNIFICANT | 0.885 | 0.342 | 100% |
| 300ETF | ew | 0.301 | 0.131 | NOT_SIGNIFICANT | 0.221 | 0.203 | 87% |
| 500ETF | ew | 0.665 | 0.280 | NOT_SIGNIFICANT | 0.795 | 0.463 | 93% |
| 159915ETF | ew | 0.974 | 0.467 | NOT_SIGNIFICANT | 0.967 | 0.448 | 100% |

