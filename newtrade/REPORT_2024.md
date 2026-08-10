# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.70/S:1.40 (train L:1.50/S:1.20) | 37 | 30 (12L/18S) | 0.403 | 0.795 | +0.0329 | +0.0482 | 3.988 | -0.0153 | -4.168 | 0.0276 | 43.3% (L:58.3%, S:33.3%) | 21.7x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.40/S:1.30) | 37 | 25 (14L/11S) | 0.450 | 0.798 | +0.0368 | +0.0433 | 3.244 | -0.0065 | -2.742 | 0.0307 | 48.0% (L:50.0%, S:45.5%) | 19.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.40/S:1.40 (train L:1.20/S:1.20) | 37 | 38 (22L/16S) | 0.190 | 0.712 | +0.0171 | +0.0318 | 1.709 | -0.0148 | -4.362 | 0.0352 | 39.5% (L:45.5%, S:31.2%) | 31.2x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.40/S:1.30 (train L:1.20/S:1.10) | 37 | 47 (23L/24S) | 0.265 | 0.848 | +0.0259 | +0.0195 | 1.022 | +0.0064 | 0.677 | 0.0366 | 38.3% (L:39.1%, S:37.5%) | 36.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.403 | 0.188 | NOT_SIGNIFICANT | 0.376 | 0.309 | 100% |
| 300ETF | icw | 0.450 | 0.216 | NOT_SIGNIFICANT | 0.434 | 0.294 | 100% |
| 300ETF | sortino | 0.190 | 0.098 | NOT_SIGNIFICANT | 0.387 | 0.324 | 93% |
| 300ETF | ew | 0.265 | 0.120 | NOT_SIGNIFICANT | 0.366 | 0.261 | 100% |

