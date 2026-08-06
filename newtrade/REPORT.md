# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.40 (train L:1.10/S:1.20) | 32 | 65 (42L/23S) | 0.382 | 0.883 | +0.0618 | +0.0585 | 1.955 | +0.0033 | 0.295 | 0.0569 | 56.9% (L:54.8%, S:60.9%) | 27.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.00/S:1.20) | 366 | 142 (79L/63S) | 0.786 | 1.628 | +0.1612 | -0.0410 | -1.109 | +0.2022 | 5.249 | 0.0464 | 54.2% (L:44.3%, S:66.7%) | 56.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.70 (train L:0.70/S:1.50) | 37 | 123 (121L/2S) | 0.827 | 1.285 | +0.2697 | +0.2772 | 2.437 | -0.0074 | -6.513 | 0.0855 | 49.6% (L:49.6%, S:50.0%) | 43.9x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.00/S:1.10) | 32 | 101 (62L/39S) | 0.232 | 0.944 | +0.0407 | +0.0261 | 0.666 | +0.0146 | 0.897 | 0.0531 | 51.5% (L:48.4%, S:56.4%) | 40.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.60 (train L:1.00/S:1.40) | 366 | 130 (86L/44S) | 0.720 | 1.496 | +0.1404 | -0.0382 | -0.995 | +0.1785 | 6.146 | 0.0473 | 55.4% (L:45.3%, S:75.0%) | 48.4x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.70/S:1.00) | 37 | 202 (128L/74S) | 1.179 | 1.772 | +0.4650 | +0.3231 | 2.775 | +0.1419 | 2.307 | 0.0716 | 54.5% (L:51.6%, S:59.5%) | 70.9x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.80/S:1.00) | 32 | 165 (104L/61S) | -0.030 | 1.005 | -0.0059 | -0.0101 | -0.179 | +0.0042 | 0.170 | 0.0763 | 46.7% (L:45.2%, S:49.2%) | 63.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.00/S:1.30) | 366 | 138 (86L/52S) | 0.810 | 1.622 | +0.1621 | -0.0390 | -1.016 | +0.2011 | 6.051 | 0.0459 | 55.1% (L:45.3%, S:71.2%) | 52.7x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 37 | 235 (125L/110S) | 1.256 | 1.931 | +0.5057 | +0.3231 | 2.808 | +0.1826 | 2.290 | 0.0657 | 55.7% (L:51.2%, S:60.9%) | 82.4x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.70/S:1.40 (train L:1.50/S:1.20) | 32 | 36 (10L/26S) | 0.381 | 0.695 | +0.0478 | +0.0629 | 6.433 | -0.0150 | -1.304 | 0.0626 | 58.3% (L:70.0%, S:53.8%) | 13.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 366 | 228 (162L/66S) | 0.631 | 1.869 | +0.1487 | -0.0415 | -0.583 | +0.1902 | 4.785 | 0.0633 | 54.4% (L:50.0%, S:65.2%) | 84.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.70 (train L:0.70/S:1.50) | 37 | 118 (115L/3S) | 0.801 | 1.247 | +0.2627 | +0.2760 | 2.486 | -0.0133 | -7.121 | 0.0769 | 48.3% (L:48.7%, S:33.3%) | 42.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.382 | 0.224 | NOT_SIGNIFICANT | 0.566 | 0.198 | 100% |
| 500ETF | ensemble | 0.786 | 0.586 | NOT_SIGNIFICANT | 1.016 | 0.426 | 93% |
| 159915ETF | ensemble | 0.827 | 0.693 | NOT_SIGNIFICANT | 1.049 | 0.462 | 100% |
| 300ETF | icw | 0.232 | 0.136 | NOT_SIGNIFICANT | 0.580 | 0.229 | 100% |
| 500ETF | icw | 0.720 | 0.536 | NOT_SIGNIFICANT | 0.959 | 0.375 | 100% |
| 159915ETF | icw | 1.179 | 0.939 | MARGINAL | 1.017 | 0.353 | 100% |
| 300ETF | sortino | -0.030 | 0.051 | NOT_SIGNIFICANT | 0.598 | 0.247 | 100% |
| 500ETF | sortino | 0.810 | 0.621 | NOT_SIGNIFICANT | 0.834 | 0.354 | 100% |
| 159915ETF | sortino | 1.256 | 0.958 | SIGNIFICANT | 0.972 | 0.332 | 100% |
| 300ETF | ew | 0.381 | 0.233 | NOT_SIGNIFICANT | 0.595 | 0.362 | 87% |
| 500ETF | ew | 0.631 | 0.406 | NOT_SIGNIFICANT | 1.026 | 0.438 | 93% |
| 159915ETF | ew | 0.801 | 0.660 | NOT_SIGNIFICANT | 0.979 | 0.447 | 100% |

