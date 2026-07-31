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
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 213 (194L/19S) | 1.358 | 1.898 | +0.4168 | +0.3143 | 2.427 | +0.1025 | 8.736 | 0.0778 | 57.3% (L:56.7%, S:63.2%) | 88.4x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.10 (train L:1.00/S:1.00) | 11 | 188 (94L/94S) | 1.677 | 2.050 | +0.6589 | +0.4283 | 4.108 | +0.2305 | 4.002 | 0.0500 | 63.8% (L:60.6%, S:67.0%) | 87.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 (20L/27S) | 1.013 | 1.205 | +0.1808 | +0.1451 | 7.757 | +0.0357 | 2.059 | 0.0608 | 57.4% (L:70.0%, S:48.1%) | 23.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 214 (193L/21S) | 1.370 | 1.907 | +0.4258 | +0.2930 | 2.283 | +0.1328 | 9.188 | 0.0778 | 57.0% (L:56.5%, S:61.9%) | 88.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 11 | 272 (131L/141S) | 1.660 | 2.157 | +0.7177 | +0.5128 | 3.791 | +0.2049 | 2.537 | 0.0661 | 60.7% (L:59.5%, S:61.7%) | 122.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.119 | 0.894 | NOT_SIGNIFICANT | 0.851 | 0.239 | 100% |
| 500ETF | icw | 1.358 | 0.931 | MARGINAL | 0.923 | 0.438 | 100% |
| 159915ETF | icw | 1.677 | 0.994 | SIGNIFICANT | 0.837 | 0.228 | 100% |
| 300ETF | ew | 1.013 | 0.832 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.370 | 0.936 | MARGINAL | 0.953 | 0.427 | 100% |
| 159915ETF | ew | 1.660 | 0.989 | SIGNIFICANT | 0.833 | 0.208 | 100% |

