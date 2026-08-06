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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 34 | 12 (2L/10S) | -0.341 | 0.661 | -0.0055 | +0.0067 | 8.014 | -0.0122 | -5.115 | 0.0116 | 33.3% (L:50.0%, S:30.0%) | 19.7x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 100 | 73 (61L/12S) | -0.152 | 1.865 | -0.0075 | +0.0228 | 1.024 | -0.0303 | -7.041 | 0.0387 | 56.2% (L:59.0%, S:41.7%) | 109.8x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 122 | 61 (43L/18S) | 1.146 | 2.070 | +0.1009 | +0.0672 | 2.603 | +0.0337 | 1.994 | 0.0559 | 52.5% (L:53.5%, S:50.0%) | 96.8x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 34 | 11 (3L/8S) | -0.188 | 0.754 | -0.0028 | +0.0109 | 11.166 | -0.0137 | -8.426 | 0.0093 | 36.4% (L:66.7%, S:25.0%) | 18.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 100 | 73 (61L/12S) | -0.006 | 2.025 | -0.0003 | +0.0300 | 1.361 | -0.0303 | -7.035 | 0.0387 | 57.5% (L:60.7%, S:41.7%) | 110.0x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:0.90 (train L:0.80/S:0.80) | 122 | 81 (43L/38S) | 0.846 | 1.995 | +0.0794 | +0.0664 | 2.568 | +0.0130 | 0.467 | 0.0665 | 49.4% (L:53.5%, S:44.7%) | 122.3x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 34 | 11 (4L/7S) | -0.188 | 0.775 | -0.0027 | +0.0098 | 8.592 | -0.0125 | -8.224 | 0.0093 | 36.4% (L:50.0%, S:28.6%) | 18.1x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 100 | 75 (63L/12S) | -0.032 | 1.890 | -0.0017 | +0.0091 | 0.411 | -0.0107 | -1.698 | 0.0359 | 54.7% (L:57.1%, S:41.7%) | 113.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 122 | 69 (42L/27S) | 1.094 | 2.102 | +0.0992 | +0.0690 | 2.746 | +0.0303 | 1.358 | 0.0567 | 53.6% (L:54.8%, S:51.9%) | 108.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.341 | 0.028 | NOT_SIGNIFICANT | 0.495 | 0.237 | 93% |
| 500ETF | icw | -0.152 | 0.042 | NOT_SIGNIFICANT | 1.038 | 0.337 | 100% |
| 159915ETF | icw | 1.146 | 0.358 | NOT_SIGNIFICANT | 0.948 | 0.285 | 100% |
| 300ETF | sortino | -0.188 | 0.039 | NOT_SIGNIFICANT | 0.452 | 0.303 | 93% |
| 500ETF | sortino | -0.006 | 0.057 | NOT_SIGNIFICANT | 0.870 | 0.343 | 100% |
| 159915ETF | sortino | 0.846 | 0.240 | NOT_SIGNIFICANT | 0.964 | 0.256 | 100% |
| 300ETF | ew | -0.188 | 0.039 | NOT_SIGNIFICANT | 0.378 | 0.281 | 93% |
| 500ETF | ew | -0.032 | 0.054 | NOT_SIGNIFICANT | 1.018 | 0.377 | 100% |
| 159915ETF | ew | 1.094 | 0.333 | NOT_SIGNIFICANT | 1.027 | 0.356 | 100% |

