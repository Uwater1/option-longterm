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
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 72 | 24 (15L/9S) | 1.048 | 1.176 | +0.1381 | +0.1107 | 7.413 | +0.0274 | 3.883 | 0.0293 | 66.7% (L:73.3%, S:55.6%) | 15.9x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 196 | 161 (137L/24S) | 1.304 | 1.814 | +0.3230 | +0.2332 | 2.300 | +0.0899 | 6.903 | 0.0597 | 57.1% (L:55.5%, S:66.7%) | 92.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 84 | 170 (108L/62S) | 1.611 | 2.020 | +0.5262 | +0.3309 | 2.974 | +0.1953 | 4.757 | 0.0598 | 60.0% (L:52.8%, S:72.6%) | 105.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 72 | 21 (13L/8S) | 0.854 | 0.975 | +0.1086 | +0.1001 | 7.208 | +0.0086 | 1.447 | 0.0293 | 61.9% (L:69.2%, S:50.0%) | 13.9x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 196 | 160 (136L/24S) | 1.312 | 1.819 | +0.3249 | +0.2351 | 2.328 | +0.0899 | 6.903 | 0.0597 | 57.5% (L:55.9%, S:66.7%) | 91.5x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 84 | 172 (108L/64S) | 1.613 | 2.026 | +0.5268 | +0.3309 | 2.974 | +0.1959 | 4.690 | 0.0598 | 59.9% (L:52.8%, S:71.9%) | 106.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.048 | 0.819 | NOT_SIGNIFICANT | 0.650 | 0.193 | 100% |
| 500ETF | icw | 1.304 | 0.833 | NOT_SIGNIFICANT | 1.254 | 0.444 | 100% |
| 159915ETF | icw | 1.611 | 0.971 | SIGNIFICANT | 0.930 | 0.301 | 100% |
| 300ETF | ew | 0.854 | 0.648 | NOT_SIGNIFICANT | 0.645 | 0.163 | 100% |
| 500ETF | ew | 1.312 | 0.838 | NOT_SIGNIFICANT | 1.243 | 0.438 | 100% |
| 159915ETF | ew | 1.613 | 0.971 | SIGNIFICANT | 0.942 | 0.229 | 100% |

