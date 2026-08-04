# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Score Weight (75% TailIC + 25% Sortino)

![Cumulative Equity](artifacts/equity_curve_old.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 107 (38L/69S) | 0.538 | 1.276 | +0.0958 | +0.0972 | 3.507 | -0.0014 | -0.050 | 0.0540 | 55.1% (L:63.2%, S:50.7%) | 41.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.40 (train L:0.70/S:1.30) | 32 | 192 (174L/18S) | 0.610 | 1.564 | +0.1629 | +0.0795 | 0.741 | +0.0834 | 8.052 | 0.0584 | 52.1% (L:50.0%, S:72.2%) | 69.8x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 11 | 293 (171L/122S) | 1.132 | 1.999 | +0.4941 | +0.3972 | 2.419 | +0.0969 | 1.466 | 0.0865 | 53.6% (L:51.5%, S:56.6%) | 107.2x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.10 (train L:1.30/S:1.00) | 10 | 75 (23L/52S) | 0.726 | 1.255 | +0.1230 | +0.0957 | 5.212 | +0.0274 | 1.037 | 0.0529 | 58.7% (L:69.6%, S:53.8%) | 30.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 32 | 305 (217L/88S) | 0.786 | 2.099 | +0.2462 | +0.0708 | 0.555 | +0.1754 | 3.725 | 0.0752 | 52.5% (L:49.8%, S:59.1%) | 115.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 11 | 260 (136L/124S) | 1.028 | 1.883 | +0.3999 | +0.2905 | 2.286 | +0.1094 | 1.659 | 0.0766 | 54.2% (L:51.5%, S:57.3%) | 95.9x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 107 (38L/69S) | 0.538 | 1.276 | +0.0958 | +0.0972 | 3.507 | -0.0014 | -0.050 | 0.0540 | 55.1% (L:63.2%, S:50.7%) | 41.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.30 (train L:0.60/S:1.20) | 32 | 248 (216L/32S) | 0.598 | 1.778 | +0.1713 | +0.1004 | 0.785 | +0.0709 | 4.347 | 0.0609 | 51.2% (L:50.0%, S:59.4%) | 92.1x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 11 | 293 (171L/122S) | 1.132 | 1.999 | +0.4941 | +0.3972 | 2.419 | +0.0969 | 1.466 | 0.0865 | 53.6% (L:51.5%, S:56.6%) | 107.2x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 (20L/27S) | 0.835 | 1.178 | +0.1297 | +0.1099 | 6.339 | +0.0199 | 1.395 | 0.0581 | 57.4% (L:70.0%, S:48.1%) | 18.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 32 | 164 (136L/28S) | 0.690 | 1.499 | +0.1786 | +0.0517 | 0.597 | +0.1269 | 6.992 | 0.0827 | 54.3% (L:52.2%, S:64.3%) | 61.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 11 | 303 (162L/141S) | 1.209 | 2.149 | +0.4986 | +0.3582 | 2.435 | +0.1404 | 1.886 | 0.0876 | 54.1% (L:51.2%, S:57.4%) | 110.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | score | 0.538 | 0.341 | NOT_SIGNIFICANT | 0.588 | 0.263 | 100% |
| 500ETF | score | 0.610 | 0.391 | NOT_SIGNIFICANT | 1.027 | 0.569 | 93% |
| 159915ETF | score | 1.132 | 0.861 | NOT_SIGNIFICANT | 1.052 | 0.367 | 100% |
| 300ETF | icw | 0.726 | 0.559 | NOT_SIGNIFICANT | 0.749 | 0.265 | 100% |
| 500ETF | icw | 0.786 | 0.535 | NOT_SIGNIFICANT | 1.040 | 0.482 | 100% |
| 159915ETF | icw | 1.028 | 0.785 | NOT_SIGNIFICANT | 1.066 | 0.303 | 100% |
| 300ETF | sortino | 0.538 | 0.341 | NOT_SIGNIFICANT | 0.588 | 0.263 | 100% |
| 500ETF | sortino | 0.598 | 0.374 | NOT_SIGNIFICANT | 0.876 | 0.470 | 93% |
| 159915ETF | sortino | 1.132 | 0.861 | NOT_SIGNIFICANT | 1.052 | 0.367 | 100% |
| 300ETF | ew | 0.835 | 0.704 | NOT_SIGNIFICANT | 0.873 | 0.252 | 100% |
| 500ETF | ew | 0.690 | 0.475 | NOT_SIGNIFICANT | 0.915 | 0.307 | 100% |
| 159915ETF | ew | 1.209 | 0.886 | NOT_SIGNIFICANT | 0.929 | 0.296 | 100% |

