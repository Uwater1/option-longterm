# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Score Weight (75% TailIC + 25% Sortino)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.50/S:1.30 (train L:1.40/S:1.20) | 51 | 87 (30L/57S) | 0.344 | 1.110 | +0.0505 | +0.0283 | 1.218 | +0.0222 | 0.869 | 0.0659 | 51.7% (L:50.0%, S:52.6%) | 48.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 215 | 161 (96L/65S) | 0.738 | 1.859 | +0.1402 | -0.0252 | -0.527 | +0.1653 | 4.166 | 0.0520 | 54.0% (L:46.9%, S:64.6%) | 85.1x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 78 | 173 (130L/43S) | 1.296 | 1.943 | +0.4539 | +0.2928 | 2.236 | +0.1611 | 4.292 | 0.0988 | 52.0% (L:48.5%, S:62.8%) | 90.1x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.10/S:1.30) | 51 | 85 (54L/31S) | -0.148 | 0.693 | -0.0203 | +0.0025 | 0.073 | -0.0227 | -1.905 | 0.0815 | 47.1% (L:44.4%, S:51.6%) | 48.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.30 (train L:1.20/S:1.20) | 215 | 121 (57L/64S) | 1.124 | 2.012 | +0.1914 | +0.0050 | 0.186 | +0.1864 | 4.646 | 0.0426 | 57.9% (L:45.6%, S:68.8%) | 65.8x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 78 | 256 (137L/119S) | 1.404 | 2.289 | +0.5226 | +0.2958 | 2.215 | +0.2268 | 2.735 | 0.0861 | 52.7% (L:48.9%, S:57.1%) | 125.9x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.10/S:1.30) | 51 | 86 (55L/31S) | -0.079 | 0.763 | -0.0109 | +0.0121 | 0.353 | -0.0230 | -1.931 | 0.0816 | 47.7% (L:45.5%, S:51.6%) | 48.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 215 | 143 (78L/65S) | 0.813 | 1.826 | +0.1481 | -0.0479 | -1.282 | +0.1960 | 4.831 | 0.0460 | 55.2% (L:43.6%, S:69.2%) | 75.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 78 | 158 (105L/53S) | 1.365 | 2.035 | +0.4048 | +0.2124 | 2.302 | +0.1924 | 4.382 | 0.0814 | 53.8% (L:48.6%, S:64.2%) | 81.2x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.30 (train L:1.20/S:1.20) | 51 | 103 (44L/59S) | 0.241 | 1.130 | +0.0367 | +0.0203 | 0.686 | +0.0164 | 0.615 | 0.0709 | 50.5% (L:50.0%, S:50.8%) | 57.3x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 215 | 160 (106L/54S) | 0.656 | 1.802 | +0.1237 | -0.0473 | -0.928 | +0.1711 | 4.937 | 0.0575 | 53.8% (L:45.3%, S:70.4%) | 86.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 78 | 148 (129L/19S) | 1.195 | 1.785 | +0.3969 | +0.2590 | 2.069 | +0.1380 | 6.328 | 0.1252 | 50.0% (L:48.1%, S:63.2%) | 76.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | score | 0.344 | 0.173 | NOT_SIGNIFICANT | 0.346 | 0.349 | 80% |
| 500ETF | score | 0.738 | 0.424 | NOT_SIGNIFICANT | 1.085 | 0.457 | 93% |
| 159915ETF | score | 1.296 | 0.913 | MARGINAL | 0.995 | 0.362 | 100% |
| 300ETF | icw | -0.148 | 0.035 | NOT_SIGNIFICANT | 0.198 | 0.290 | 73% |
| 500ETF | icw | 1.124 | 0.779 | NOT_SIGNIFICANT | 0.884 | 0.417 | 100% |
| 159915ETF | icw | 1.404 | 0.933 | MARGINAL | 0.903 | 0.390 | 93% |
| 300ETF | sortino | -0.079 | 0.044 | NOT_SIGNIFICANT | 0.174 | 0.357 | 60% |
| 500ETF | sortino | 0.813 | 0.499 | NOT_SIGNIFICANT | 0.754 | 0.456 | 100% |
| 159915ETF | sortino | 1.365 | 0.911 | MARGINAL | 0.900 | 0.376 | 100% |
| 300ETF | ew | 0.241 | 0.126 | NOT_SIGNIFICANT | 0.202 | 0.324 | 80% |
| 500ETF | ew | 0.656 | 0.361 | NOT_SIGNIFICANT | 0.854 | 0.505 | 93% |
| 159915ETF | ew | 1.195 | 0.838 | NOT_SIGNIFICANT | 0.907 | 0.307 | 100% |

