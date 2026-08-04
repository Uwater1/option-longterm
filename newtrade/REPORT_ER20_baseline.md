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
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:0.90 (train L:1.20/S:0.80) | 37 | 195 (54L/141S) | 0.145 | 1.286 | +0.0333 | +0.0265 | 0.736 | +0.0068 | 0.104 | 0.0842 | 48.2% (L:48.1%, S:48.2%) | 75.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.50 (train L:0.90/S:1.40) | 377 | 181 (132L/49S) | 0.942 | 1.991 | +0.2107 | +0.0032 | 0.054 | +0.2075 | 6.387 | 0.0368 | 55.8% (L:50.0%, S:71.4%) | 70.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 31 | 173 (140L/33S) | 0.965 | 1.554 | +0.3590 | +0.2690 | 2.133 | +0.0900 | 3.026 | 0.0906 | 51.4% (L:49.3%, S:60.6%) | 65.2x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.20 (train L:1.10/S:1.10) | 37 | 117 (46L/71S) | 0.143 | 0.991 | +0.0251 | +0.0404 | 1.269 | -0.0153 | -0.580 | 0.0487 | 52.1% (L:50.0%, S:53.5%) | 47.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.30 (train L:0.80/S:1.20) | 377 | 247 (169L/78S) | 0.587 | 1.899 | +0.1471 | -0.0443 | -0.578 | +0.1914 | 4.078 | 0.0639 | 53.4% (L:49.7%, S:61.5%) | 94.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 31 | 224 (176L/48S) | 1.056 | 1.722 | +0.4624 | +0.3507 | 2.095 | +0.1116 | 2.703 | 0.1110 | 52.7% (L:50.0%, S:62.5%) | 84.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.145 | 0.100 | NOT_SIGNIFICANT | 0.152 | 0.269 | 87% |
| 500ETF | icw | 0.942 | 0.708 | NOT_SIGNIFICANT | 1.031 | 0.395 | 100% |
| 159915ETF | icw | 0.965 | 0.788 | NOT_SIGNIFICANT | 0.979 | 0.348 | 100% |
| 300ETF | ew | 0.143 | 0.099 | NOT_SIGNIFICANT | 0.352 | 0.325 | 73% |
| 500ETF | ew | 0.587 | 0.362 | NOT_SIGNIFICANT | 1.022 | 0.370 | 93% |
| 159915ETF | ew | 1.056 | 0.852 | NOT_SIGNIFICANT | 1.109 | 0.366 | 100% |

