# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.10 (train L:1.10/S:1.00) | 37 | 143 (63L/80S) | 0.539 | 1.387 | +0.1186 | +0.0359 | 0.883 | +0.0826 | 1.916 | 0.0725 | 53.8% (L:49.2%, S:57.5%) | 59.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 377 | 150 (102L/48S) | 1.039 | 1.947 | +0.2176 | +0.0035 | 0.075 | +0.2142 | 6.775 | 0.0468 | 56.7% (L:48.0%, S:75.0%) | 60.3x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 31 | 254 (207L/47S) | 1.065 | 1.809 | +0.4805 | +0.3840 | 1.981 | +0.0965 | 2.764 | 0.1081 | 51.6% (L:49.8%, S:59.6%) | 92.0x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.10 (train L:1.10/S:1.00) | 37 | 145 (64L/81S) | 0.499 | 1.360 | +0.1097 | +0.0328 | 0.800 | +0.0768 | 1.769 | 0.0760 | 53.1% (L:48.4%, S:56.8%) | 60.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.50 (train L:1.00/S:1.40) | 377 | 151 (103L/48S) | 1.000 | 1.912 | +0.2100 | -0.0044 | -0.095 | +0.2144 | 6.782 | 0.0468 | 57.0% (L:48.5%, S:75.0%) | 60.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.00 (train L:0.60/S:0.90) | 31 | 352 (206L/146S) | 1.123 | 2.082 | +0.5483 | +0.3935 | 2.035 | +0.1548 | 1.628 | 0.1124 | 52.8% (L:50.0%, S:56.8%) | 130.3x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.10/S:1.30) | 37 | 67 (44L/23S) | 0.123 | 0.677 | +0.0196 | +0.0481 | 1.542 | -0.0285 | -3.072 | 0.0607 | 50.7% (L:52.3%, S:47.8%) | 28.5x |
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
| 300ETF | icw | 0.539 | 0.338 | NOT_SIGNIFICANT | 0.333 | 0.223 | 100% |
| 500ETF | icw | 1.039 | 0.810 | NOT_SIGNIFICANT | 1.041 | 0.440 | 93% |
| 159915ETF | icw | 1.065 | 0.832 | NOT_SIGNIFICANT | 1.136 | 0.359 | 100% |
| 300ETF | sortino | 0.499 | 0.304 | NOT_SIGNIFICANT | 0.426 | 0.154 | 100% |
| 500ETF | sortino | 1.000 | 0.778 | NOT_SIGNIFICANT | 1.034 | 0.417 | 100% |
| 159915ETF | sortino | 1.123 | 0.860 | NOT_SIGNIFICANT | 1.144 | 0.459 | 100% |
| 300ETF | ew | 0.123 | 0.092 | NOT_SIGNIFICANT | 0.481 | 0.238 | 100% |
| 500ETF | ew | 0.519 | 0.311 | NOT_SIGNIFICANT | 1.020 | 0.436 | 93% |
| 159915ETF | ew | 0.961 | 0.785 | NOT_SIGNIFICANT | 1.077 | 0.415 | 100% |

