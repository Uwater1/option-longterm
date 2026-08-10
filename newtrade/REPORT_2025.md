# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.70 (train L:1.40/S:1.50) | 34 | 5 (3L/2S) | 0.492 | 0.937 | +0.0049 | +0.0086 | 11.036 | -0.0037 | -9.581 | 0.0049 | 60.0% (L:66.7%, S:50.0%) | 6.9x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 60 (50L/10S) | -0.595 | 1.196 | -0.0251 | +0.0149 | 0.876 | -0.0400 | -13.292 | 0.0501 | 55.0% (L:60.0%, S:30.0%) | 88.2x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.80/S:0.90) | 122 | 61 (42L/19S) | 1.140 | 1.984 | +0.0977 | +0.0698 | 2.936 | +0.0279 | 1.585 | 0.0487 | 52.5% (L:54.8%, S:47.4%) | 87.2x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.70 (train L:1.40/S:1.50) | 34 | 4 (2L/2S) | 0.310 | 0.676 | +0.0035 | +0.0075 | 9.427 | -0.0039 | -9.785 | 0.0052 | 50.0% (L:50.0%, S:50.0%) | 6.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 61 (50L/11S) | -0.311 | 1.468 | -0.0134 | +0.0239 | 1.372 | -0.0373 | -10.893 | 0.0413 | 55.7% (L:60.0%, S:36.4%) | 90.2x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 122 | 67 (42L/25S) | 1.194 | 2.112 | +0.1029 | +0.0725 | 3.056 | +0.0304 | 1.488 | 0.0490 | 52.2% (L:54.8%, S:48.0%) | 95.1x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.70/S:1.20 (train L:1.50/S:1.00) | 34 | 15 (2L/13S) | -0.554 | 0.656 | -0.0089 | +0.0077 | 9.962 | -0.0166 | -6.183 | 0.0144 | 26.7% (L:50.0%, S:23.1%) | 24.0x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 63 (52L/11S) | -0.311 | 1.516 | -0.0134 | +0.0239 | 1.347 | -0.0373 | -10.894 | 0.0397 | 57.1% (L:61.5%, S:36.4%) | 91.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 122 | 68 (42L/26S) | 1.072 | 1.998 | +0.0930 | +0.0724 | 3.050 | +0.0206 | 0.975 | 0.0491 | 51.5% (L:54.8%, S:46.2%) | 96.2x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.40/S:1.30) | 34 | 8 (4L/4S) | -0.754 | -0.211 | -0.0114 | -0.0014 | -0.921 | -0.0100 | -9.329 | 0.0136 | 50.0% (L:50.0%, S:50.0%) | 10.8x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 59 (49L/10S) | -0.552 | 1.224 | -0.0228 | +0.0140 | 0.838 | -0.0367 | -13.193 | 0.0454 | 52.5% (L:57.1%, S:30.0%) | 86.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.80/S:1.00) | 122 | 53 (40L/13S) | 1.621 | 2.375 | +0.1320 | +0.0804 | 3.535 | +0.0516 | 3.942 | 0.0389 | 56.6% (L:57.5%, S:53.8%) | 75.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.492 | 0.145 | NOT_SIGNIFICANT | 0.362 | 0.242 | 100% |
| 500ETF | ensemble | -0.595 | 0.015 | NOT_SIGNIFICANT | 0.950 | 0.368 | 100% |
| 159915ETF | ensemble | 1.140 | 0.359 | NOT_SIGNIFICANT | 0.931 | 0.292 | 100% |
| 300ETF | icw | 0.310 | 0.107 | NOT_SIGNIFICANT | 0.518 | 0.272 | 93% |
| 500ETF | icw | -0.311 | 0.030 | NOT_SIGNIFICANT | 1.036 | 0.350 | 100% |
| 159915ETF | icw | 1.194 | 0.380 | NOT_SIGNIFICANT | 0.860 | 0.324 | 100% |
| 300ETF | sortino | -0.554 | 0.018 | NOT_SIGNIFICANT | 0.493 | 0.260 | 93% |
| 500ETF | sortino | -0.311 | 0.030 | NOT_SIGNIFICANT | 1.009 | 0.356 | 100% |
| 159915ETF | sortino | 1.072 | 0.328 | NOT_SIGNIFICANT | 0.849 | 0.309 | 100% |
| 300ETF | ew | -0.754 | 0.008 | NOT_SIGNIFICANT | 0.367 | 0.311 | 100% |
| 500ETF | ew | -0.552 | 0.017 | NOT_SIGNIFICANT | 0.960 | 0.351 | 100% |
| 159915ETF | ew | 1.621 | 0.595 | NOT_SIGNIFICANT | 0.967 | 0.262 | 100% |

