# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 12 | 50 (13L/37S) | 1.334 | 1.640 | +0.1592 | +0.0747 | 6.128 | +0.0845 | 3.508 | 0.0207 | 48.0% (L:69.2%, S:40.5%) | 47.8x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 11 | 128 (100L/28S) | 1.402 | 1.912 | +0.2796 | +0.2012 | 2.431 | +0.0784 | 4.328 | 0.0711 | 54.7% (L:53.0%, S:60.7%) | 110.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 11 | 78 (78L/0S) | 1.055 | 1.344 | +0.2291 | +0.2291 | 2.660 | +0.0000 | 0.000 | 0.0843 | 51.3% (L:51.3%, S:N/A) | 68.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.10 (train L:1.10/S:1.00) | 12 | 45 (13L/32S) | 1.465 | 1.736 | +0.1730 | +0.0731 | 5.990 | +0.0999 | 4.612 | 0.0129 | 51.1% (L:69.2%, S:43.8%) | 44.7x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 11 | 135 (115L/20S) | 1.529 | 2.058 | +0.3085 | +0.2181 | 2.404 | +0.0904 | 6.452 | 0.0585 | 55.6% (L:53.9%, S:65.0%) | 109.1x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.60 (train L:0.80/S:1.50) | 11 | 61 (61L/0S) | 1.414 | 1.641 | +0.2950 | +0.2950 | 4.102 | +0.0000 | 0.000 | 0.0690 | 55.7% (L:55.7%, S:N/A) | 55.1x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.334 | 0.922 | MARGINAL | 0.405 | 0.390 | 80% |
| 500ETF | icw | 1.402 | 0.738 | NOT_SIGNIFICANT | 1.049 | 0.433 | 100% |
| 159915ETF | icw | 1.055 | 0.621 | NOT_SIGNIFICANT | 0.994 | 0.303 | 100% |
| 300ETF | ew | 1.465 | 0.977 | SIGNIFICANT | 0.435 | 0.312 | 93% |
| 500ETF | ew | 1.529 | 0.804 | NOT_SIGNIFICANT | 1.102 | 0.422 | 100% |
| 159915ETF | ew | 1.414 | 0.903 | MARGINAL | 1.052 | 0.314 | 100% |

