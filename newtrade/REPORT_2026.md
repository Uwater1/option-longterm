# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.10/S:1.40) | 9 | 9 (7L/2S) | -0.341 | 0.045 | -0.0064 | +0.0003 | 0.121 | -0.0067 | -9.899 | 0.0108 | 55.6% (L:57.1%, S:50.0%) | 18.7x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 11 | 43 (35L/8S) | -0.150 | 0.616 | -0.0068 | +0.0278 | 1.772 | -0.0346 | -13.919 | 0.0348 | 53.5% (L:60.0%, S:25.0%) | 83.0x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:0.80 (train L:0.80/S:0.70) | 12 | 70 (38L/32S) | 2.045 | 2.619 | +0.1939 | +0.1152 | 4.892 | +0.0787 | 3.045 | 0.0406 | 58.6% (L:57.9%, S:59.4%) | 130.7x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.10 (train L:1.00/S:1.00) | 9 | 14 (5L/9S) | -0.521 | 0.174 | -0.0084 | -0.0005 | -0.259 | -0.0079 | -4.214 | 0.0129 | 42.9% (L:60.0%, S:33.3%) | 29.0x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 11 | 50 (40L/10S) | 0.244 | 1.107 | +0.0113 | +0.0431 | 2.525 | -0.0318 | -10.174 | 0.0348 | 60.0% (L:65.0%, S:40.0%) | 91.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:0.70 (train L:0.70/S:0.60) | 12 | 79 (41L/38S) | 1.930 | 2.573 | +0.1860 | +0.0976 | 3.865 | +0.0884 | 3.095 | 0.0406 | 57.0% (L:53.7%, S:60.5%) | 144.2x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.341 | 0.028 | NOT_SIGNIFICANT | 0.295 | 0.280 | 87% |
| 500ETF | icw | -0.150 | 0.043 | NOT_SIGNIFICANT | 0.809 | 0.567 | 87% |
| 159915ETF | icw | 2.045 | 0.752 | NOT_SIGNIFICANT | 1.017 | 0.310 | 100% |
| 300ETF | ew | -0.521 | 0.017 | NOT_SIGNIFICANT | 0.227 | 0.336 | 80% |
| 500ETF | ew | 0.244 | 0.091 | NOT_SIGNIFICANT | 0.914 | 0.505 | 100% |
| 159915ETF | ew | 1.930 | 0.703 | NOT_SIGNIFICANT | 0.839 | 0.269 | 100% |

