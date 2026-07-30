# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.40/S:1.00 (train L:1.30/S:0.90) | 10 | 6 (2L/4S) | 0.888 | 1.063 | +0.0204 | +0.0043 | 5.726 | +0.0161 | 6.366 | 0.0087 | 50.0% (L:50.0%, S:50.0%) | 12.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.40 (train L:0.70/S:1.30) | 32 | 60 (60L/0S) | 1.958 | 2.776 | +0.1073 | +0.1073 | 4.036 | +0.0000 | 0.000 | 0.0270 | 63.3% (L:63.3%, S:N/A) | 99.6x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:0.80 (train L:0.80/S:0.70) | 12 | 70 (38L/32S) | 2.045 | 2.619 | +0.1939 | +0.1152 | 4.892 | +0.0787 | 3.045 | 0.0406 | 58.6% (L:57.9%, S:59.4%) | 130.7x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 5 (3L/2S) | 0.235 | 0.400 | +0.0056 | -0.0045 | -3.348 | +0.0100 | 5.798 | 0.0125 | 40.0% (L:33.3%, S:50.0%) | 10.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 66 (60L/6S) | 1.684 | 2.586 | +0.0940 | +0.1073 | 4.036 | -0.0133 | -9.922 | 0.0270 | 60.6% (L:63.3%, S:33.3%) | 112.0x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:0.70 (train L:0.70/S:0.60) | 12 | 79 (41L/38S) | 1.930 | 2.573 | +0.1860 | +0.0976 | 3.865 | +0.0884 | 3.095 | 0.0406 | 57.0% (L:53.7%, S:60.5%) | 144.2x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.888 | 0.314 | NOT_SIGNIFICANT | 0.903 | 0.222 | 100% |
| 500ETF | icw | 1.958 | 0.669 | NOT_SIGNIFICANT | 1.005 | 0.413 | 100% |
| 159915ETF | icw | 2.045 | 0.752 | NOT_SIGNIFICANT | 1.017 | 0.310 | 100% |
| 300ETF | ew | 0.235 | 0.091 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 1.684 | 0.557 | NOT_SIGNIFICANT | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 1.930 | 0.703 | NOT_SIGNIFICANT | 0.839 | 0.269 | 100% |

