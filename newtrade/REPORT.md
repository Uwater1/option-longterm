# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 62 (20L/42S) | 1.119 | 1.368 | +0.2032 | +0.1451 | 7.757 | +0.0581 | 2.566 | 0.0470 | 58.1% (L:70.0%, S:52.4%) | 31.2x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 208 (167L/41S) | 1.336 | 1.841 | +0.4300 | +0.1819 | 1.675 | +0.2480 | 7.043 | 0.0768 | 57.7% (L:55.7%, S:65.9%) | 91.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 11 | 278 (165L/113S) | 1.473 | 1.964 | +0.6655 | +0.4509 | 2.799 | +0.2146 | 2.898 | 0.0831 | 56.8% (L:53.3%, S:61.9%) | 122.8x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 (20L/27S) | 1.013 | 1.205 | +0.1808 | +0.1451 | 7.757 | +0.0357 | 2.059 | 0.0608 | 57.4% (L:70.0%, S:48.1%) | 23.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 32 | 177 (173L/4S) | 1.005 | 1.505 | +0.2801 | +0.2450 | 2.130 | +0.0351 | 14.388 | 0.0579 | 57.6% (L:57.2%, S:75.0%) | 75.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 11 | 310 (166L/144S) | 1.658 | 2.190 | +0.7666 | +0.4704 | 2.904 | +0.2962 | 3.261 | 0.0958 | 58.1% (L:54.2%, S:62.5%) | 133.9x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.119 | 0.894 | NOT_SIGNIFICANT | 0.851 | 0.239 | 100% |
| 500ETF | icw | 1.336 | 0.930 | MARGINAL | 0.823 | 0.409 | 93% |
| 159915ETF | icw | 1.473 | 0.965 | SIGNIFICANT | 1.088 | 0.346 | 100% |
| 300ETF | ew | 1.013 | 0.832 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.005 | 0.744 | NOT_SIGNIFICANT | 1.117 | 0.394 | 100% |
| 159915ETF | ew | 1.658 | 0.987 | SIGNIFICANT | 0.894 | 0.397 | 100% |

