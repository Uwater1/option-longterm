# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_old.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.00/S:0.80) | 10 | 78 (29L/49S) | 0.648 | 1.167 | +0.1042 | +0.0953 | 4.314 | +0.0089 | 0.432 | 0.0742 | 57.7% (L:65.5%, S:53.1%) | 28.1x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.70/S:1.30) | 32 | 156 (148L/8S) | 0.620 | 1.422 | +0.1490 | +0.1005 | 1.106 | +0.0485 | 10.819 | 0.0751 | 54.5% (L:53.4%, S:75.0%) | 54.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 11 | 198 (129L/69S) | 1.113 | 1.745 | +0.4053 | +0.3349 | 2.738 | +0.0704 | 2.014 | 0.0580 | 57.1% (L:52.7%, S:65.2%) | 68.7x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.10 (train L:1.10/S:0.90) | 10 | 85 (32L/53S) | 0.475 | 1.047 | +0.0785 | +0.0674 | 2.861 | +0.0111 | 0.475 | 0.0650 | 54.1% (L:59.4%, S:50.9%) | 30.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.40 (train L:0.60/S:1.20) | 32 | 217 (190L/27S) | 0.633 | 1.683 | +0.1662 | +0.0920 | 0.826 | +0.0742 | 6.368 | 0.0749 | 53.5% (L:52.1%, S:63.0%) | 76.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 11 | 273 (126L/147S) | 1.226 | 2.059 | +0.4654 | +0.3792 | 3.163 | +0.0861 | 1.281 | 0.0624 | 54.6% (L:54.8%, S:54.4%) | 93.6x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.20 (train L:1.10/S:1.00) | 10 | 56 (26L/30S) | 0.660 | 1.074 | +0.0939 | +0.0931 | 4.643 | +0.0007 | 0.064 | 0.0494 | 60.7% (L:65.4%, S:56.7%) | 20.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 32 | 178 (154L/24S) | 0.505 | 1.399 | +0.1264 | +0.0735 | 0.767 | +0.0529 | 5.144 | 0.0816 | 52.2% (L:51.3%, S:58.3%) | 63.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 11 | 273 (123L/150S) | 1.192 | 2.026 | +0.4518 | +0.3721 | 3.165 | +0.0797 | 1.149 | 0.0635 | 54.2% (L:53.7%, S:54.7%) | 93.8x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.10 (train L:1.10/S:0.90) | 10 | 29 (15L/14S) | 0.787 | 0.995 | +0.1058 | +0.0782 | 5.703 | +0.0276 | 3.537 | 0.0347 | 65.5% (L:73.3%, S:57.1%) | 10.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.50 (train L:0.60/S:1.30) | 32 | 183 (171L/12S) | 0.783 | 1.651 | +0.2010 | +0.1255 | 1.238 | +0.0756 | 8.968 | 0.0466 | 55.7% (L:55.0%, S:66.7%) | 62.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:0.80 (train L:0.70/S:0.60) | 11 | 323 (124L/199S) | 1.212 | 2.178 | +0.4918 | +0.3591 | 3.023 | +0.1327 | 1.296 | 0.0598 | 55.4% (L:54.0%, S:56.3%) | 112.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.648 | 0.465 | NOT_SIGNIFICANT | 0.758 | 0.310 | 100% |
| 500ETF | ensemble | 0.620 | 0.413 | NOT_SIGNIFICANT | 0.995 | 0.478 | 100% |
| 159915ETF | ensemble | 1.113 | 0.872 | NOT_SIGNIFICANT | 0.917 | 0.256 | 100% |
| 300ETF | icw | 0.475 | 0.297 | NOT_SIGNIFICANT | 0.755 | 0.197 | 100% |
| 500ETF | icw | 0.633 | 0.412 | NOT_SIGNIFICANT | 0.973 | 0.478 | 100% |
| 159915ETF | icw | 1.226 | 0.917 | MARGINAL | 0.998 | 0.214 | 100% |
| 300ETF | sortino | 0.660 | 0.526 | NOT_SIGNIFICANT | 0.748 | 0.364 | 87% |
| 500ETF | sortino | 0.505 | 0.308 | NOT_SIGNIFICANT | 0.935 | 0.514 | 93% |
| 159915ETF | sortino | 1.192 | 0.899 | NOT_SIGNIFICANT | 1.021 | 0.260 | 100% |
| 300ETF | ew | 0.787 | 0.737 | NOT_SIGNIFICANT | 0.838 | 0.185 | 100% |
| 500ETF | ew | 0.783 | 0.560 | NOT_SIGNIFICANT | 0.942 | 0.357 | 100% |
| 159915ETF | ew | 1.212 | 0.893 | NOT_SIGNIFICANT | 0.937 | 0.282 | 100% |

