# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Score Weight (75% TailIC + 25% Sortino)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 14 (3L/11S) | -0.103 | 0.956 | -0.0017 | +0.0119 | 11.465 | -0.0136 | -5.724 | 0.0091 | 35.7% (L:66.7%, S:27.3%) | 22.0x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 160 | 46 (33L/13S) | -0.771 | 0.899 | -0.0296 | +0.0051 | 0.447 | -0.0347 | -7.404 | 0.0507 | 54.3% (L:57.6%, S:46.2%) | 76.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 145 | 63 (44L/19S) | 1.805 | 2.750 | +0.1521 | +0.0813 | 3.266 | +0.0708 | 4.363 | 0.0401 | 54.0% (L:52.3%, S:57.9%) | 103.6x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 14 (3L/11S) | -0.051 | 0.987 | -0.0008 | +0.0120 | 11.488 | -0.0128 | -5.541 | 0.0090 | 35.7% (L:66.7%, S:27.3%) | 21.3x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 160 | 43 (30L/13S) | -0.889 | 0.712 | -0.0325 | +0.0012 | 0.113 | -0.0337 | -7.143 | 0.0438 | 53.5% (L:56.7%, S:46.2%) | 69.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.90/S:0.90) | 145 | 64 (36L/28S) | 2.269 | 3.178 | +0.1925 | +0.1031 | 4.987 | +0.0894 | 4.218 | 0.0504 | 57.8% (L:58.3%, S:57.1%) | 98.1x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 14 (3L/11S) | -0.059 | 0.977 | -0.0010 | +0.0120 | 11.519 | -0.0130 | -5.571 | 0.0090 | 35.7% (L:66.7%, S:27.3%) | 21.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 160 | 45 (30L/15S) | -0.656 | 0.949 | -0.0251 | +0.0011 | 0.106 | -0.0261 | -4.395 | 0.0438 | 53.3% (L:56.7%, S:46.7%) | 73.1x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.90/S:0.90) | 145 | 64 (36L/28S) | 1.993 | 2.906 | +0.1716 | +0.1031 | 4.986 | +0.0685 | 3.115 | 0.0503 | 56.2% (L:58.3%, S:53.6%) | 98.9x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 50 | 15 (3L/12S) | -0.111 | 1.060 | -0.0017 | +0.0111 | 11.372 | -0.0128 | -5.487 | 0.0096 | 33.3% (L:66.7%, S:25.0%) | 22.9x |
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
| 300ETF | score | -0.103 | 0.047 | NOT_SIGNIFICANT | 0.285 | 0.270 | 80% |
| 500ETF | score | -0.771 | 0.009 | NOT_SIGNIFICANT | 0.716 | 0.446 | 93% |
| 159915ETF | score | 1.805 | 0.678 | NOT_SIGNIFICANT | 1.099 | 0.396 | 100% |
| 300ETF | icw | -0.051 | 0.052 | NOT_SIGNIFICANT | 0.275 | 0.256 | 93% |
| 500ETF | icw | -0.889 | 0.007 | NOT_SIGNIFICANT | 0.616 | 0.411 | 93% |
| 159915ETF | icw | 2.269 | 0.851 | NOT_SIGNIFICANT | 0.911 | 0.351 | 100% |
| 300ETF | sortino | -0.059 | 0.051 | NOT_SIGNIFICANT | 0.273 | 0.231 | 100% |
| 500ETF | sortino | -0.656 | 0.013 | NOT_SIGNIFICANT | 0.643 | 0.434 | 93% |
| 159915ETF | sortino | 1.993 | 0.747 | NOT_SIGNIFICANT | 0.797 | 0.407 | 100% |
| 300ETF | ew | -0.111 | 0.046 | NOT_SIGNIFICANT | 0.316 | 0.174 | 100% |
| 500ETF | ew | -0.940 | 0.006 | NOT_SIGNIFICANT | 0.805 | 0.446 | 93% |
| 159915ETF | ew | 1.637 | 0.601 | NOT_SIGNIFICANT | 0.956 | 0.460 | 100% |

