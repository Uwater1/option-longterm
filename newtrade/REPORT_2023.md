# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 72 | 84 (21L/63S) | 0.502 | 1.231 | +0.0748 | +0.0572 | 3.325 | +0.0175 | 0.555 | 0.0483 | 52.4% (L:61.9%, S:49.2%) | 45.9x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 196 | 177 (112L/65S) | 0.667 | 1.906 | +0.1253 | -0.0595 | -1.226 | +0.1849 | 4.549 | 0.0565 | 53.7% (L:45.5%, S:67.7%) | 92.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 84 | 213 (135L/78S) | 1.114 | 1.965 | +0.3674 | +0.1747 | 1.456 | +0.1927 | 3.419 | 0.0788 | 51.6% (L:47.4%, S:59.0%) | 109.3x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.50 (train L:1.20/S:1.40) | 72 | 56 (40L/16S) | 0.466 | 0.987 | +0.0644 | +0.0407 | 1.470 | +0.0237 | 2.275 | 0.0413 | 51.8% (L:52.5%, S:50.0%) | 31.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 196 | 194 (116L/78S) | 0.920 | 2.189 | +0.1843 | -0.0416 | -0.777 | +0.2259 | 4.831 | 0.0522 | 54.6% (L:47.4%, S:65.4%) | 103.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 84 | 213 (158L/55S) | 1.087 | 1.889 | +0.3865 | +0.2454 | 1.620 | +0.1412 | 3.696 | 0.1234 | 50.7% (L:46.8%, S:61.8%) | 107.7x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.502 | 0.276 | NOT_SIGNIFICANT | 0.350 | 0.343 | 93% |
| 500ETF | icw | 0.667 | 0.365 | NOT_SIGNIFICANT | 0.617 | 0.491 | 87% |
| 159915ETF | icw | 1.114 | 0.773 | NOT_SIGNIFICANT | 0.950 | 0.411 | 100% |
| 300ETF | ew | 0.466 | 0.250 | NOT_SIGNIFICANT | 0.436 | 0.325 | 100% |
| 500ETF | ew | 0.920 | 0.566 | NOT_SIGNIFICANT | 0.664 | 0.459 | 93% |
| 159915ETF | ew | 1.087 | 0.753 | NOT_SIGNIFICANT | 0.965 | 0.356 | 100% |

