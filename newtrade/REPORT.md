# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 32 | 95 (56L/39S) | 0.360 | 1.062 | +0.0635 | +0.0428 | 1.166 | +0.0208 | 1.180 | 0.0526 | 53.7% (L:51.8%, S:56.4%) | 41.2x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 103 (41L/62S) | 0.305 | 1.055 | +0.0542 | +0.0572 | 1.928 | -0.0030 | -0.116 | 0.0544 | 52.4% (L:56.1%, S:50.0%) | 43.5x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 32 | 103 (42L/61S) | 0.267 | 1.020 | +0.0473 | +0.0552 | 1.836 | -0.0079 | -0.311 | 0.0571 | 51.5% (L:54.8%, S:49.2%) | 43.6x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 32 | 56 (13L/43S) | 0.316 | 0.797 | +0.0457 | +0.0689 | 5.568 | -0.0232 | -1.226 | 0.0622 | 53.6% (L:69.2%, S:48.8%) | 23.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.360 | 0.205 | NOT_SIGNIFICANT | 0.563 | 0.261 | 100% |
| 300ETF | icw | 0.305 | 0.173 | NOT_SIGNIFICANT | 0.371 | 0.255 | 100% |
| 300ETF | sortino | 0.267 | 0.153 | NOT_SIGNIFICANT | 0.354 | 0.282 | 93% |
| 300ETF | ew | 0.316 | 0.185 | NOT_SIGNIFICANT | 0.591 | 0.255 | 100% |

