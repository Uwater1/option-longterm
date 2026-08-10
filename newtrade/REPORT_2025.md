# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.70 (train L:1.40/S:1.50) | 34 | 5 (3L/2S) | 0.492 | 0.937 | +0.0049 | +0.0086 | 11.036 | -0.0037 | -9.581 | 0.0049 | 60.0% (L:66.7%, S:50.0%) | 6.9x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.70 (train L:1.40/S:1.50) | 34 | 4 (2L/2S) | 0.310 | 0.676 | +0.0035 | +0.0075 | 9.427 | -0.0039 | -9.785 | 0.0052 | 50.0% (L:50.0%, S:50.0%) | 6.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.70/S:1.20 (train L:1.50/S:1.00) | 34 | 15 (2L/13S) | -0.554 | 0.656 | -0.0089 | +0.0077 | 9.962 | -0.0166 | -6.183 | 0.0144 | 26.7% (L:50.0%, S:23.1%) | 24.0x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.40/S:1.30) | 34 | 8 (4L/4S) | -0.754 | -0.211 | -0.0114 | -0.0014 | -0.921 | -0.0100 | -9.329 | 0.0136 | 50.0% (L:50.0%, S:50.0%) | 10.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.492 | 0.145 | NOT_SIGNIFICANT | 0.362 | 0.242 | 100% |
| 300ETF | icw | 0.310 | 0.107 | NOT_SIGNIFICANT | 0.518 | 0.272 | 93% |
| 300ETF | sortino | -0.554 | 0.018 | NOT_SIGNIFICANT | 0.493 | 0.260 | 93% |
| 300ETF | ew | -0.754 | 0.008 | NOT_SIGNIFICANT | 0.367 | 0.311 | 100% |

