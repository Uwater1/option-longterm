# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_linear`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 85 | 59 (22L/37S) | 0.572 | 1.217 | +0.0657 | +0.0392 | 2.116 | +0.0265 | 1.295 | 0.0472 | 42.4% (L:45.5%, S:40.5%) | 48.4x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 144 | 112 (70L/42S) | 0.714 | 1.780 | +0.1023 | -0.0162 | -0.415 | +0.1185 | 4.166 | 0.0546 | 55.4% (L:50.0%, S:64.3%) | 92.7x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 118 | 90 (70L/20S) | 1.367 | 1.903 | +0.2979 | +0.1552 | 2.299 | +0.1426 | 6.014 | 0.0769 | 51.1% (L:48.6%, S:60.0%) | 70.3x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.40/S:1.40) | 85 | 30 (19L/11S) | 0.537 | 0.953 | +0.0496 | +0.0302 | 1.854 | +0.0195 | 3.178 | 0.0401 | 46.7% (L:42.1%, S:54.5%) | 25.6x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 144 | 111 (76L/35S) | 0.690 | 1.743 | +0.1030 | -0.0179 | -0.403 | +0.1209 | 4.779 | 0.0600 | 55.9% (L:50.0%, S:68.6%) | 92.5x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.80/S:1.40) | 118 | 92 (84L/8S) | 0.919 | 1.563 | +0.1742 | +0.1288 | 1.770 | +0.0455 | 5.229 | 0.1076 | 48.9% (L:48.8%, S:50.0%) | 70.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.572 | 0.268 | NOT_SIGNIFICANT | 0.309 | 0.199 | 100% |
| 500ETF | icw | 0.714 | 0.313 | NOT_SIGNIFICANT | 0.599 | 0.429 | 93% |
| 159915ETF | icw | 1.367 | 0.782 | NOT_SIGNIFICANT | 1.011 | 0.402 | 100% |
| 300ETF | ew | 0.537 | 0.256 | NOT_SIGNIFICANT | 0.551 | 0.322 | 93% |
| 500ETF | ew | 0.690 | 0.295 | NOT_SIGNIFICANT | 0.675 | 0.405 | 93% |
| 159915ETF | ew | 0.919 | 0.434 | NOT_SIGNIFICANT | 0.989 | 0.258 | 100% |

