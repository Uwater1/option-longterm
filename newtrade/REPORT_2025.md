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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 50 | 15 (3L/12S) | -0.057 | 1.067 | -0.0009 | +0.0125 | 11.591 | -0.0134 | -5.720 | 0.0102 | 33.3% (L:66.7%, S:25.0%) | 23.5x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 160 | 43 (30L/13S) | -0.889 | 0.712 | -0.0325 | +0.0012 | 0.113 | -0.0337 | -7.143 | 0.0438 | 53.5% (L:56.7%, S:46.2%) | 69.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.00 (train L:1.00/S:0.90) | 145 | 59 (31L/28S) | 2.217 | 3.059 | +0.1835 | +0.0941 | 5.231 | +0.0894 | 4.218 | 0.0503 | 57.6% (L:58.1%, S:57.1%) | 89.4x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 50 | 15 (3L/12S) | -0.062 | 1.058 | -0.0010 | +0.0126 | 11.649 | -0.0136 | -5.734 | 0.0102 | 33.3% (L:66.7%, S:25.0%) | 23.6x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 160 | 45 (30L/15S) | -0.656 | 0.949 | -0.0251 | +0.0011 | 0.106 | -0.0261 | -4.395 | 0.0438 | 53.3% (L:56.7%, S:46.7%) | 73.1x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.00 (train L:1.00/S:0.90) | 145 | 59 (31L/28S) | 1.904 | 2.753 | +0.1598 | +0.0913 | 5.082 | +0.0685 | 3.115 | 0.0502 | 55.9% (L:58.1%, S:53.6%) | 90.2x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 14 (3L/11S) | -0.014 | 1.031 | -0.0002 | +0.0121 | 11.672 | -0.0123 | -5.485 | 0.0089 | 35.7% (L:66.7%, S:27.3%) | 21.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 160 | 52 (36L/16S) | -0.940 | 0.784 | -0.0386 | -0.0184 | -1.532 | -0.0202 | -3.009 | 0.0519 | 48.1% (L:50.0%, S:43.8%) | 81.7x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 145 | 56 (43L/13S) | 1.637 | 2.509 | +0.1347 | +0.0695 | 2.806 | +0.0652 | 5.188 | 0.0415 | 53.6% (L:51.2%, S:61.5%) | 95.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.057 | 0.052 | NOT_SIGNIFICANT | 0.179 | 0.259 | 73% |
| 500ETF | icw | -0.889 | 0.007 | NOT_SIGNIFICANT | 0.584 | 0.408 | 93% |
| 159915ETF | icw | 2.217 | 0.838 | NOT_SIGNIFICANT | 0.755 | 0.362 | 100% |
| 300ETF | sortino | -0.062 | 0.051 | NOT_SIGNIFICANT | 0.316 | 0.301 | 73% |
| 500ETF | sortino | -0.656 | 0.013 | NOT_SIGNIFICANT | 0.643 | 0.438 | 93% |
| 159915ETF | sortino | 1.904 | 0.713 | NOT_SIGNIFICANT | 0.843 | 0.337 | 100% |
| 300ETF | ew | -0.014 | 0.056 | NOT_SIGNIFICANT | 0.269 | 0.232 | 93% |
| 500ETF | ew | -0.940 | 0.006 | NOT_SIGNIFICANT | 0.805 | 0.446 | 93% |
| 159915ETF | ew | 1.637 | 0.601 | NOT_SIGNIFICANT | 0.956 | 0.460 | 100% |

