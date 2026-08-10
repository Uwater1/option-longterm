# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.70/S:1.40 (train L:1.50/S:1.20) | 47 | 28 (16L/12S) | 0.396 | 0.683 | +0.0413 | +0.0624 | 4.392 | -0.0211 | -5.503 | 0.0326 | 57.1% (L:68.8%, S:41.7%) | 13.7x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.30/S:1.30) | 47 | 31 (25L/6S) | 0.249 | 0.590 | +0.0272 | +0.0447 | 2.288 | -0.0175 | -9.362 | 0.0337 | 51.6% (L:56.0%, S:33.3%) | 16.8x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.30/S:1.30) | 47 | 31 (25L/6S) | 0.253 | 0.592 | +0.0276 | +0.0445 | 2.276 | -0.0170 | -9.229 | 0.0332 | 51.6% (L:56.0%, S:33.3%) | 16.7x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.30 (train L:1.10/S:1.10) | 47 | 55 (35L/20S) | 0.149 | 0.682 | +0.0188 | +0.0299 | 1.188 | -0.0111 | -1.321 | 0.0496 | 52.7% (L:54.3%, S:50.0%) | 29.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.396 | 0.227 | NOT_SIGNIFICANT | 0.568 | 0.219 | 100% |
| 300ETF | icw | 0.249 | 0.136 | NOT_SIGNIFICANT | 0.496 | 0.224 | 100% |
| 300ETF | sortino | 0.253 | 0.137 | NOT_SIGNIFICANT | 0.477 | 0.249 | 100% |
| 300ETF | ew | 0.149 | 0.095 | NOT_SIGNIFICANT | 0.462 | 0.207 | 100% |

