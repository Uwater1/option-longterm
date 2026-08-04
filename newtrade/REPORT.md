# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Score Weight (75% TailIC + 25% Sortino)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 37 | 160 (47L/113S) | -0.078 | 1.014 | -0.0151 | +0.0422 | 1.286 | -0.0573 | -1.363 | 0.0888 | 48.8% (L:51.1%, S:47.8%) | 63.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 377 | 173 (106L/67S) | 0.554 | 1.561 | +0.1256 | -0.0273 | -0.536 | +0.1529 | 3.571 | 0.0740 | 50.3% (L:46.2%, S:56.7%) | 69.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.30 (train L:0.80/S:1.20) | 31 | 189 (141L/48S) | 1.070 | 1.683 | +0.4201 | +0.3124 | 2.364 | +0.1077 | 2.731 | 0.0809 | 52.4% (L:50.4%, S:58.3%) | 71.5x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.10 (train L:1.10/S:1.00) | 37 | 151 (65L/86S) | 0.204 | 1.212 | +0.0399 | +0.0411 | 1.007 | -0.0012 | -0.036 | 0.0703 | 51.7% (L:49.2%, S:53.5%) | 62.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 377 | 150 (102L/48S) | 1.039 | 1.947 | +0.2176 | +0.0035 | 0.075 | +0.2142 | 6.775 | 0.0468 | 56.7% (L:48.0%, S:75.0%) | 60.3x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.40 (train L:0.60/S:1.30) | 31 | 241 (208L/33S) | 0.930 | 1.645 | +0.4162 | +0.3638 | 1.874 | +0.0524 | 1.885 | 0.1192 | 50.2% (L:49.5%, S:54.5%) | 86.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.10 (train L:1.10/S:1.00) | 37 | 152 (65L/87S) | 0.313 | 1.286 | +0.0640 | +0.0225 | 0.560 | +0.0415 | 1.046 | 0.0705 | 52.0% (L:47.7%, S:55.2%) | 62.2x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 377 | 151 (103L/48S) | 1.000 | 1.912 | +0.2100 | -0.0044 | -0.095 | +0.2144 | 6.782 | 0.0468 | 57.0% (L:48.5%, S:75.0%) | 60.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.00 (train L:0.60/S:0.90) | 31 | 356 (208L/148S) | 1.090 | 2.057 | +0.5353 | +0.3669 | 1.887 | +0.1683 | 1.716 | 0.1135 | 52.8% (L:49.5%, S:57.4%) | 132.1x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.60 (train L:1.10/S:1.50) | 37 | 54 (45L/9S) | 0.335 | 0.800 | +0.0505 | +0.0406 | 1.290 | +0.0099 | 2.885 | 0.0405 | 50.0% (L:48.9%, S:55.6%) | 23.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 377 | 216 (136L/80S) | 0.519 | 1.720 | +0.1255 | -0.0697 | -1.123 | +0.1952 | 3.984 | 0.0792 | 51.4% (L:47.8%, S:57.5%) | 84.4x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.50 (train L:0.70/S:1.40) | 31 | 189 (168L/21S) | 0.961 | 1.553 | +0.4040 | +0.3312 | 2.055 | +0.0728 | 3.181 | 0.0913 | 48.7% (L:48.2%, S:52.4%) | 72.1x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | score | -0.078 | 0.042 | NOT_SIGNIFICANT | 0.373 | 0.216 | 93% |
| 500ETF | score | 0.554 | 0.346 | NOT_SIGNIFICANT | 0.792 | 0.381 | 93% |
| 159915ETF | score | 1.070 | 0.860 | NOT_SIGNIFICANT | 1.112 | 0.384 | 100% |
| 300ETF | icw | 0.204 | 0.122 | NOT_SIGNIFICANT | 0.116 | 0.205 | 87% |
| 500ETF | icw | 1.039 | 0.810 | NOT_SIGNIFICANT | 1.041 | 0.440 | 93% |
| 159915ETF | icw | 0.930 | 0.725 | NOT_SIGNIFICANT | 1.021 | 0.331 | 100% |
| 300ETF | sortino | 0.313 | 0.175 | NOT_SIGNIFICANT | 0.281 | 0.192 | 93% |
| 500ETF | sortino | 1.000 | 0.778 | NOT_SIGNIFICANT | 1.034 | 0.417 | 100% |
| 159915ETF | sortino | 1.090 | 0.840 | NOT_SIGNIFICANT | 1.153 | 0.406 | 100% |
| 300ETF | ew | 0.335 | 0.197 | NOT_SIGNIFICANT | 0.406 | 0.182 | 100% |
| 500ETF | ew | 0.519 | 0.311 | NOT_SIGNIFICANT | 1.020 | 0.436 | 93% |
| 159915ETF | ew | 0.961 | 0.785 | NOT_SIGNIFICANT | 1.077 | 0.415 | 100% |

