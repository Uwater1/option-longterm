# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_linear`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 22 | 217 (121L/96S) | 0.347 | 1.509 | +0.0844 | +0.0470 | 0.673 | +0.0374 | 0.844 | 0.0680 | 48.4% (L:45.5%, S:52.1%) | 83.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 22 | 98 (39L/59S) | 0.481 | 1.179 | +0.0837 | +0.0864 | 2.989 | -0.0027 | -0.116 | 0.0510 | 56.1% (L:59.0%, S:54.2%) | 40.0x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.347 | 0.195 | NOT_SIGNIFICANT | 0.561 | 0.228 | 100% |
| 300ETF | ew | 0.481 | 0.293 | NOT_SIGNIFICANT | 0.461 | 0.210 | 100% |

