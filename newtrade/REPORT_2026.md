# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2026-01-01 ~ 2026-07-17`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2026.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.30/S:1.60 (train L:1.20/S:1.50) | 99 | 8 (5L/3S) | -0.638 | -0.396 | -0.0150 | -0.0202 | -7.214 | +0.0052 | 1.962 | 0.0224 | 37.5% (L:40.0%, S:33.3%) | 29.3x |
| 500ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.20/S:1.40 (train L:1.10/S:1.30) | 126 | 32 (25L/7S) | -1.380 | -0.765 | -0.0566 | -0.0065 | -0.412 | -0.0501 | -13.898 | 0.0767 | 46.9% (L:56.0%, S:14.3%) | 115.3x |
| 50ETF | Spot ETF | single | 2026-01 ~ present | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.10/S:1.20 (train L:1.00/S:1.10) | 146 | 29 (14L/15S) | -2.613 | -2.185 | -0.1332 | -0.0294 | -2.598 | -0.1039 | -9.207 | 0.1572 | 27.6% (L:35.7%, S:20.0%) | 99.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.40/S:1.40 (train L:1.30/S:1.30) | 99 | 8 (5L/3S) | -0.638 | -0.396 | -0.0150 | -0.0202 | -7.214 | +0.0052 | 1.962 | 0.0224 | 37.5% (L:40.0%, S:33.3%) | 29.3x |
| 500ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 126 | 39 (32L/7S) | -1.919 | -1.243 | -0.0868 | -0.0367 | -1.825 | -0.0501 | -13.898 | 0.1180 | 46.2% (L:53.1%, S:14.3%) | 130.9x |
| 50ETF | Spot ETF | single | 2026-01 ~ present | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.10/S:1.20 (train L:1.00/S:1.10) | 146 | 29 (14L/15S) | -2.613 | -2.185 | -0.1332 | -0.0294 | -2.598 | -0.1039 | -9.207 | 0.1572 | 27.6% (L:35.7%, S:20.0%) | 99.6x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.638 | 0.021 | NOT_SIGNIFICANT | 0.403 | 0.283 | 80% |
| 500ETF | icw | -1.380 | 0.004 | NOT_SIGNIFICANT | 0.796 | 0.505 | 93% |
| 159915ETF | icw | -2.613 | 0.000 | NOT_SIGNIFICANT | 0.732 | 0.212 | 100% |
| 300ETF | ew | -0.638 | 0.021 | NOT_SIGNIFICANT | 0.346 | 0.306 | 87% |
| 500ETF | ew | -1.919 | 0.001 | NOT_SIGNIFICANT | 1.061 | 0.491 | 93% |
| 159915ETF | ew | -2.613 | 0.000 | NOT_SIGNIFICANT | 0.693 | 0.241 | 100% |

