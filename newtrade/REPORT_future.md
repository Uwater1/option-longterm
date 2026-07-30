# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `4.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_future.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Future (IF88 (CSI 300 Futures)) | single | 2022-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 62 (20L/42S) | 1.244 | 1.368 | +0.2280 | +0.1531 | 8.184 | +0.0749 | 3.308 | 0.0390 | 61.3% (L:70.0%, S:57.1%) | 31.2x |
| 500ETF | Future (IC88 (CSI 500 Futures)) | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 219 (195L/24S) | 1.574 | 1.851 | +0.4935 | +0.3655 | 2.848 | +0.1280 | 7.390 | 0.0734 | 58.4% (L:57.9%, S:62.5%) | 92.1x |
| 50ETF | Future | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Future | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Future (N/A) | single | 2022-01 ~ 2026-01 | N/A | 11 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Future (IF88 (CSI 300 Futures)) | single | 2022-01 ~ 2025-12 | L:1.20/S:0.80 (train L:1.10/S:0.70) | 10 | 105 (20L/85S) | 1.415 | 1.602 | +0.2964 | +0.1531 | 8.184 | +0.1433 | 3.272 | 0.0567 | 61.0% (L:70.0%, S:58.8%) | 49.4x |
| 500ETF | Future (IC88 (CSI 500 Futures)) | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 221 (194L/27S) | 1.551 | 1.834 | +0.4820 | +0.3554 | 2.807 | +0.1265 | 6.767 | 0.0734 | 58.4% (L:58.2%, S:59.3%) | 92.6x |
| 50ETF | Future | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Future | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Future (N/A) | single | 2022-01 ~ 2026-01 | N/A | 11 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.244 | 0.952 | SIGNIFICANT | 1.179 | 0.233 | 100% |
| 500ETF | icw | 1.574 | 0.980 | SIGNIFICANT | 1.456 | 0.614 | 100% |
| 300ETF | ew | 1.415 | 0.970 | SIGNIFICANT | 1.049 | 0.280 | 100% |
| 500ETF | ew | 1.551 | 0.977 | SIGNIFICANT | 1.350 | 0.605 | 100% |

