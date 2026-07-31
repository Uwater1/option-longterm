# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 95 | 7 (4L/3S) | 0.596 | 0.805 | +0.0148 | +0.0027 | 1.512 | +0.0121 | 5.643 | 0.0087 | 57.1% (L:50.0%, S:66.7%) | 14.5x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 58 (51L/7S) | 0.428 | 1.236 | +0.0245 | +0.0364 | 1.414 | -0.0119 | -7.635 | 0.0703 | 53.4% (L:54.9%, S:42.9%) | 93.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.40/S:1.40 (train L:1.30/S:1.30) | 146 | 25 (21L/4S) | 0.685 | 1.046 | +0.0385 | +0.0503 | 3.346 | -0.0119 | -4.655 | 0.0264 | 56.0% (L:52.4%, S:75.0%) | 47.7x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 95 | 7 (4L/3S) | 0.596 | 0.805 | +0.0148 | +0.0027 | 1.512 | +0.0121 | 5.643 | 0.0087 | 57.1% (L:50.0%, S:66.7%) | 14.5x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 60 (53L/7S) | 0.393 | 1.227 | +0.0225 | +0.0344 | 1.308 | -0.0119 | -7.635 | 0.0703 | 53.3% (L:54.7%, S:42.9%) | 95.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.40/S:1.10 (train L:1.30/S:1.00) | 146 | 48 (21L/27S) | 1.434 | 1.874 | +0.1230 | +0.0503 | 3.346 | +0.0726 | 3.254 | 0.0284 | 56.2% (L:52.4%, S:59.3%) | 92.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.596 | 0.177 | NOT_SIGNIFICANT | 0.674 | 0.232 | 100% |
| 500ETF | icw | 0.428 | 0.125 | NOT_SIGNIFICANT | 1.247 | 0.415 | 100% |
| 159915ETF | icw | 0.685 | 0.187 | NOT_SIGNIFICANT | 0.809 | 0.338 | 100% |
| 300ETF | ew | 0.596 | 0.177 | NOT_SIGNIFICANT | 0.680 | 0.223 | 100% |
| 500ETF | ew | 0.393 | 0.117 | NOT_SIGNIFICANT | 1.262 | 0.401 | 100% |
| 159915ETF | ew | 1.434 | 0.505 | NOT_SIGNIFICANT | 0.543 | 0.318 | 100% |

