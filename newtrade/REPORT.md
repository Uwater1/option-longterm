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
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 219 (195L/24S) | 1.460 | 2.003 | +0.4571 | +0.3213 | 2.477 | +0.1358 | 8.532 | 0.0778 | 57.1% (L:56.4%, S:62.5%) | 91.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 11 | 203 (115L/88S) | 1.832 | 2.214 | +0.7552 | +0.5332 | 4.347 | +0.2221 | 4.009 | 0.0500 | 65.5% (L:62.6%, S:69.3%) | 92.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 (20L/27S) | 1.013 | 1.205 | +0.1808 | +0.1451 | 7.757 | +0.0357 | 2.059 | 0.0608 | 57.4% (L:70.0%, S:48.1%) | 23.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 218 (193L/25S) | 1.415 | 1.960 | +0.4397 | +0.3047 | 2.379 | +0.1350 | 8.248 | 0.0778 | 56.9% (L:56.5%, S:60.0%) | 91.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.50 (train L:0.90/S:1.40) | 11 | 114 (113L/1S) | 1.475 | 1.711 | +0.5438 | +0.5285 | 4.347 | +0.0153 | 0.000 | 0.0493 | 62.3% (L:61.9%, S:100.0%) | 49.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.119 | 0.894 | NOT_SIGNIFICANT | 0.851 | 0.239 | 100% |
| 500ETF | icw | 1.460 | 0.960 | SIGNIFICANT | 1.005 | 0.414 | 100% |
| 159915ETF | icw | 1.832 | 0.998 | SIGNIFICANT | 0.836 | 0.274 | 100% |
| 300ETF | ew | 1.013 | 0.832 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.415 | 0.949 | MARGINAL | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 1.475 | 0.988 | SIGNIFICANT | 0.852 | 0.243 | 100% |

