# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 62 | 42 (17L/25S) | 0.689 | 1.211 | +0.0704 | +0.0530 | 3.397 | +0.0175 | 1.363 | 0.0321 | 45.2% (L:52.9%, S:40.0%) | 35.8x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 256 | 87 (55L/32S) | 0.988 | 1.855 | +0.1327 | -0.0099 | -0.324 | +0.1426 | 5.973 | 0.0375 | 58.6% (L:50.9%, S:71.9%) | 71.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 128 | 96 (95L/1S) | 1.124 | 1.666 | +0.2709 | +0.2258 | 2.207 | +0.0451 | 0.000 | 0.1038 | 49.0% (L:48.4%, S:100.0%) | 73.8x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 62 | 49 (16L/33S) | 0.766 | 1.347 | +0.0826 | +0.0509 | 3.368 | +0.0316 | 1.842 | 0.0395 | 44.9% (L:50.0%, S:42.4%) | 41.4x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 256 | 88 (55L/33S) | 0.976 | 1.852 | +0.1313 | -0.0093 | -0.303 | +0.1406 | 5.778 | 0.0374 | 58.0% (L:50.9%, S:69.7%) | 73.5x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 128 | 96 (95L/1S) | 1.125 | 1.666 | +0.2722 | +0.2271 | 2.211 | +0.0451 | 0.000 | 0.1035 | 49.0% (L:48.4%, S:100.0%) | 73.9x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:0.90 (train L:1.10/S:0.80) | 62 | 106 (45L/61S) | 0.260 | 1.347 | +0.0343 | +0.0162 | 0.526 | +0.0182 | 0.603 | 0.0616 | 41.5% (L:42.2%, S:41.0%) | 85.9x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 256 | 107 (69L/38S) | 0.760 | 1.802 | +0.1076 | -0.0273 | -0.736 | +0.1348 | 4.950 | 0.0546 | 56.1% (L:49.3%, S:68.4%) | 88.9x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.60 (train L:0.70/S:1.50) | 128 | 100 (95L/5S) | 0.750 | 1.389 | +0.1628 | +0.1129 | 1.242 | +0.0498 | 7.998 | 0.1231 | 47.0% (L:46.3%, S:60.0%) | 78.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.689 | 0.361 | NOT_SIGNIFICANT | 0.551 | 0.325 | 100% |
| 500ETF | icw | 0.988 | 0.515 | NOT_SIGNIFICANT | 0.794 | 0.346 | 100% |
| 159915ETF | icw | 1.124 | 0.651 | NOT_SIGNIFICANT | 1.101 | 0.273 | 100% |
| 300ETF | sortino | 0.766 | 0.417 | NOT_SIGNIFICANT | 0.531 | 0.296 | 87% |
| 500ETF | sortino | 0.976 | 0.505 | NOT_SIGNIFICANT | 0.910 | 0.410 | 93% |
| 159915ETF | sortino | 1.125 | 0.653 | NOT_SIGNIFICANT | 1.179 | 0.253 | 100% |
| 300ETF | ew | 0.260 | 0.116 | NOT_SIGNIFICANT | 0.202 | 0.292 | 73% |
| 500ETF | ew | 0.760 | 0.341 | NOT_SIGNIFICANT | 1.149 | 0.492 | 93% |
| 159915ETF | ew | 0.750 | 0.349 | NOT_SIGNIFICANT | 1.045 | 0.319 | 100% |

