# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_old.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.10 (train L:1.30/S:1.00) | 10 | 75 (23L/52S) | 0.726 | 1.255 | +0.1230 | +0.0957 | 5.212 | +0.0274 | 1.037 | 0.0529 | 58.7% (L:69.6%, S:53.8%) | 30.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.50 (train L:0.70/S:1.40) | 32 | 181 (167L/14S) | 0.493 | 1.419 | +0.1282 | +0.0706 | 0.693 | +0.0575 | 6.017 | 0.0767 | 53.6% (L:52.7%, S:64.3%) | 67.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 11 | 278 (165L/113S) | 1.035 | 1.917 | +0.4206 | +0.3268 | 2.173 | +0.0938 | 1.582 | 0.0781 | 52.2% (L:49.7%, S:55.8%) | 102.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 (20L/27S) | 0.835 | 1.178 | +0.1297 | +0.1099 | 6.339 | +0.0199 | 1.395 | 0.0581 | 57.4% (L:70.0%, S:48.1%) | 18.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 32 | 174 (170L/4S) | 0.548 | 1.461 | +0.1386 | +0.1082 | 1.042 | +0.0304 | 12.522 | 0.0623 | 54.0% (L:53.5%, S:75.0%) | 63.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 11 | 310 (166L/144S) | 1.174 | 2.132 | +0.4856 | +0.3438 | 2.299 | +0.1418 | 1.880 | 0.0924 | 53.2% (L:50.6%, S:56.2%) | 111.6x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.726 | 0.559 | NOT_SIGNIFICANT | 0.749 | 0.265 | 100% |
| 500ETF | icw | 0.493 | 0.295 | NOT_SIGNIFICANT | 1.091 | 0.522 | 93% |
| 159915ETF | icw | 1.035 | 0.783 | NOT_SIGNIFICANT | 1.052 | 0.339 | 100% |
| 300ETF | ew | 0.835 | 0.704 | NOT_SIGNIFICANT | 0.873 | 0.252 | 100% |
| 500ETF | ew | 0.548 | 0.342 | NOT_SIGNIFICANT | 0.949 | 0.434 | 100% |
| 159915ETF | ew | 1.174 | 0.868 | NOT_SIGNIFICANT | 0.999 | 0.366 | 100% |

