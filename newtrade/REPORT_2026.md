# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2026-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2026.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 4 (1L/3S) | -0.489 | -0.114 | -0.0064 | -0.0039 | 0.000 | -0.0025 | -1.299 | 0.0193 | 50.0% (L:0.0%, S:66.7%) | 10.2x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 8 (5L/3S) | -1.205 | -0.714 | -0.0186 | -0.0146 | -9.250 | -0.0040 | -2.148 | 0.0323 | 50.0% (L:40.0%, S:66.7%) | 18.3x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 8 (5L/3S) | -1.572 | -1.103 | -0.0251 | -0.0226 | -17.837 | -0.0025 | -1.305 | 0.0380 | 37.5% (L:20.0%, S:66.7%) | 16.3x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 3 (1L/2S) | -0.964 | -0.658 | -0.0121 | -0.0041 | 0.000 | -0.0080 | -5.555 | 0.0195 | 33.3% (L:0.0%, S:50.0%) | 8.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | -0.489 | 0.025 | NOT_SIGNIFICANT | 0.619 | 0.331 | 93% |
| 300ETF | icw | -1.205 | 0.004 | NOT_SIGNIFICANT | 0.535 | 0.339 | 93% |
| 300ETF | sortino | -1.572 | 0.002 | NOT_SIGNIFICANT | 0.548 | 0.316 | 93% |
| 300ETF | ew | -0.964 | 0.008 | NOT_SIGNIFICANT | 0.563 | 0.358 | 87% |

