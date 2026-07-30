# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2024-01-01`
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
| 300ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 17 (3L/14S) | -0.035 | 0.429 | -0.0010 | +0.0102 | 6.023 | -0.0112 | -1.877 | 0.0325 | 58.8% (L:66.7%, S:57.1%) | 35.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:0.80/S:1.40 (train L:0.70/S:1.30) | 32 | 37 (37L/0S) | 0.540 | 1.393 | +0.0182 | +0.0182 | 1.384 | +0.0000 | 0.000 | 0.0272 | 54.1% (L:54.1%, S:N/A) | 63.5x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2024-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2023-01 ~ 2024-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:0.90/S:0.80 (train L:0.80/S:0.70) | 12 | 60 (19L/41S) | 2.275 | 2.909 | +0.1580 | +0.0863 | 7.339 | +0.0718 | 3.376 | 0.0454 | 61.7% (L:57.9%, S:63.4%) | 108.3x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 10 (3L/7S) | -0.518 | -0.233 | -0.0147 | +0.0102 | 6.023 | -0.0249 | -6.802 | 0.0390 | 40.0% (L:66.7%, S:28.6%) | 20.8x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 39 (37L/2S) | 0.922 | 1.747 | +0.0332 | +0.0182 | 1.384 | +0.0150 | 21.780 | 0.0272 | 56.4% (L:54.1%, S:100.0%) | 67.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2024-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2023-01 ~ 2024-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2023-12 | L:0.80/S:0.70 (train L:0.70/S:0.60) | 12 | 88 (25L/63S) | 2.329 | 3.215 | +0.1747 | +0.0980 | 6.947 | +0.0767 | 2.593 | 0.0440 | 60.2% (L:60.0%, S:60.3%) | 149.9x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.035 | 0.054 | NOT_SIGNIFICANT | 0.895 | 0.220 | 100% |
| 500ETF | icw | 0.540 | 0.151 | NOT_SIGNIFICANT | 1.005 | 0.414 | 100% |
| 159915ETF | icw | 2.275 | 0.776 | NOT_SIGNIFICANT | 1.054 | 0.336 | 100% |
| 300ETF | ew | -0.518 | 0.017 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 0.922 | 0.269 | NOT_SIGNIFICANT | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 2.329 | 0.783 | NOT_SIGNIFICANT | 0.839 | 0.269 | 100% |

