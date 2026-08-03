# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 14 (3L/11S) | -0.051 | 0.987 | -0.0008 | +0.0120 | 11.488 | -0.0128 | -5.541 | 0.0090 | 35.7% (L:66.7%, S:27.3%) | 21.3x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 160 | 43 (30L/13S) | -0.889 | 0.712 | -0.0325 | +0.0012 | 0.113 | -0.0337 | -7.143 | 0.0438 | 53.5% (L:56.7%, S:46.2%) | 69.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.90/S:0.90) | 145 | 64 (36L/28S) | 2.269 | 3.178 | +0.1925 | +0.1031 | 4.987 | +0.0894 | 4.218 | 0.0504 | 57.8% (L:58.3%, S:57.1%) | 98.1x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 14 (3L/11S) | -0.268 | 0.855 | -0.0041 | +0.0096 | 10.895 | -0.0137 | -5.647 | 0.0093 | 35.7% (L:66.7%, S:27.3%) | 21.2x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.70/S:1.40 (train L:0.60/S:1.30) | 160 | 84 (70L/14S) | -0.358 | 1.768 | -0.0197 | +0.0079 | 0.299 | -0.0276 | -5.011 | 0.0470 | 53.6% (L:55.7%, S:42.9%) | 124.5x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.20 (train L:0.70/S:1.10) | 145 | 68 (54L/14S) | 1.579 | 2.606 | +0.1349 | +0.0696 | 2.364 | +0.0653 | 4.891 | 0.0416 | 52.9% (L:51.9%, S:57.1%) | 108.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.051 | 0.052 | NOT_SIGNIFICANT | 0.275 | 0.256 | 93% |
| 500ETF | icw | -0.889 | 0.007 | NOT_SIGNIFICANT | 0.616 | 0.411 | 93% |
| 159915ETF | icw | 2.269 | 0.851 | NOT_SIGNIFICANT | 0.911 | 0.351 | 100% |
| 300ETF | ew | -0.268 | 0.033 | NOT_SIGNIFICANT | 0.351 | 0.260 | 87% |
| 500ETF | ew | -0.358 | 0.027 | NOT_SIGNIFICANT | 0.609 | 0.449 | 93% |
| 159915ETF | ew | 1.579 | 0.564 | NOT_SIGNIFICANT | 0.901 | 0.374 | 100% |

