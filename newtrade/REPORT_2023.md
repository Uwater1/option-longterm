# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.10 (train L:1.20/S:1.00) | 11 | 57 (15L/42S) | 0.596 | 0.921 | +0.0819 | +0.0527 | 3.423 | +0.0292 | 1.467 | 0.0358 | 57.9% (L:66.7%, S:54.8%) | 37.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 18 | 168 (153L/15S) | 1.304 | 1.805 | +0.3432 | +0.2744 | 2.396 | +0.0689 | 6.697 | 0.0935 | 57.1% (L:56.2%, S:66.7%) | 95.0x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.70/S:1.20 (train L:0.60/S:1.10) | 10 | 119 (113L/6S) | 1.816 | 2.093 | +0.5942 | +0.4945 | 4.153 | +0.0997 | 13.939 | 0.0843 | 58.0% (L:56.6%, S:83.3%) | 67.2x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.10 (train L:1.10/S:1.00) | 11 | 63 (12L/51S) | 0.800 | 1.171 | +0.1040 | +0.0691 | 5.552 | +0.0349 | 1.652 | 0.0387 | 58.7% (L:66.7%, S:56.9%) | 41.6x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.60 (train L:0.80/S:1.50) | 18 | 129 (129L/0S) | 0.698 | 1.164 | +0.1549 | +0.1549 | 1.665 | +0.0000 | 0.000 | 0.0888 | 54.3% (L:54.3%, S:N/A) | 72.8x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.80/S:1.40) | 10 | 49 (49L/0S) | 1.008 | 1.162 | +0.2518 | +0.2518 | 3.994 | +0.0000 | 0.000 | 0.0531 | 57.1% (L:57.1%, S:N/A) | 28.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.596 | 0.334 | NOT_SIGNIFICANT | 0.727 | 0.184 | 100% |
| 500ETF | icw | 1.304 | 0.862 | NOT_SIGNIFICANT | 0.907 | 0.497 | 100% |
| 159915ETF | icw | 1.816 | 0.996 | SIGNIFICANT | 1.273 | 0.360 | 100% |
| 300ETF | ew | 0.800 | 0.536 | NOT_SIGNIFICANT | 0.508 | 0.277 | 100% |
| 500ETF | ew | 0.698 | 0.393 | NOT_SIGNIFICANT | 0.911 | 0.527 | 100% |
| 159915ETF | ew | 1.008 | 0.813 | NOT_SIGNIFICANT | 0.832 | 0.434 | 100% |

