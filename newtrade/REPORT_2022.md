# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2023-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2022.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 23 (7L/16S) | 1.448 | 1.806 | +0.0673 | +0.0474 | 10.970 | +0.0199 | 2.232 | 0.0337 | 56.5% (L:71.4%, S:50.0%) | 45.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 46 (39L/7S) | 1.563 | 2.154 | +0.0926 | +0.0420 | 2.105 | +0.0506 | 11.400 | 0.0367 | 56.5% (L:56.4%, S:57.1%) | 81.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2023-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2023-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.90/S:0.80 (train L:0.80/S:0.70) | 12 | 82 (30L/52S) | 0.920 | 1.568 | +0.0961 | +0.0774 | 3.586 | +0.0186 | 0.482 | 0.0595 | 59.8% (L:63.3%, S:57.7%) | 143.7x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 22 (7L/15S) | 1.521 | 1.859 | +0.0705 | +0.0474 | 10.970 | +0.0231 | 2.700 | 0.0337 | 59.1% (L:71.4%, S:53.3%) | 43.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 44 (37L/7S) | 1.351 | 1.954 | +0.0760 | +0.0254 | 1.405 | +0.0506 | 11.400 | 0.0342 | 56.8% (L:56.8%, S:57.1%) | 79.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2023-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2023-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2022-12 | L:0.80/S:0.70 (train L:0.70/S:0.60) | 12 | 88 (33L/55S) | 0.937 | 1.617 | +0.0998 | +0.0772 | 3.359 | +0.0226 | 0.553 | 0.0595 | 59.1% (L:60.6%, S:58.2%) | 147.9x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.448 | 0.511 | NOT_SIGNIFICANT | 0.851 | 0.239 | 100% |
| 500ETF | icw | 1.563 | 0.515 | NOT_SIGNIFICANT | 1.005 | 0.414 | 100% |
| 159915ETF | icw | 0.920 | 0.245 | NOT_SIGNIFICANT | 0.982 | 0.313 | 100% |
| 300ETF | ew | 1.521 | 0.547 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.351 | 0.419 | NOT_SIGNIFICANT | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 0.937 | 0.250 | NOT_SIGNIFICANT | 0.839 | 0.269 | 100% |

