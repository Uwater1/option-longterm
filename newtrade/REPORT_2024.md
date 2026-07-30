# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2025-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 15 (7L/8S) | 1.857 | 1.994 | +0.1252 | +0.0920 | 10.371 | +0.0333 | 7.476 | 0.0139 | 66.7% (L:85.7%, S:50.0%) | 29.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.80/S:1.40 (train L:0.70/S:1.30) | 32 | 60 (59L/1S) | 1.346 | 1.744 | +0.1630 | +0.1538 | 2.604 | +0.0092 | 0.000 | 0.0793 | 51.7% (L:50.8%, S:100.0%) | 85.4x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.90/S:0.80 (train L:0.80/S:0.70) | 12 | 63 (32L/31S) | 1.835 | 2.175 | +0.2698 | +0.1328 | 2.742 | +0.1371 | 6.907 | 0.0436 | 60.3% (L:43.8%, S:77.4%) | 114.5x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 10 (7L/3S) | 1.803 | 1.886 | +0.1194 | +0.0920 | 10.371 | +0.0275 | 13.726 | 0.0139 | 80.0% (L:85.7%, S:66.7%) | 18.7x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 69 (59L/10S) | 1.843 | 2.267 | +0.2365 | +0.1538 | 2.604 | +0.0827 | 11.120 | 0.0778 | 53.6% (L:50.8%, S:70.0%) | 104.1x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2024-01 ~ 2025-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2024-12 | L:0.80/S:0.70 (train L:0.70/S:0.60) | 12 | 73 (34L/39S) | 1.719 | 2.105 | +0.2604 | +0.1322 | 2.564 | +0.1282 | 5.480 | 0.0500 | 58.9% (L:44.1%, S:71.8%) | 131.2x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.857 | 0.954 | SIGNIFICANT | 0.903 | 0.223 | 100% |
| 500ETF | icw | 1.346 | 0.469 | NOT_SIGNIFICANT | 1.005 | 0.415 | 100% |
| 159915ETF | icw | 1.835 | 0.832 | NOT_SIGNIFICANT | 1.044 | 0.332 | 100% |
| 300ETF | ew | 1.803 | 0.953 | SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.843 | 0.704 | NOT_SIGNIFICANT | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 1.719 | 0.751 | NOT_SIGNIFICANT | 0.839 | 0.269 | 100% |

