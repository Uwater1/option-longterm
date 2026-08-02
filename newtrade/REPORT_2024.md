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
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 85 | 59 (22L/37S) | 0.513 | 1.184 | +0.0577 | +0.0420 | 2.259 | +0.0156 | 0.813 | 0.0458 | 42.4% (L:45.5%, S:40.5%) | 48.5x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 144 | 112 (70L/42S) | 0.716 | 1.799 | +0.0998 | -0.0196 | -0.531 | +0.1194 | 4.181 | 0.0555 | 55.4% (L:50.0%, S:64.3%) | 92.2x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 118 | 90 (70L/20S) | 1.345 | 1.877 | +0.2922 | +0.1542 | 2.284 | +0.1380 | 5.859 | 0.0797 | 51.1% (L:48.6%, S:60.0%) | 71.0x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.40/S:1.40) | 85 | 30 (19L/11S) | 0.534 | 0.955 | +0.0488 | +0.0190 | 1.266 | +0.0298 | 4.008 | 0.0396 | 46.7% (L:42.1%, S:54.5%) | 25.4x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 144 | 111 (76L/35S) | 0.763 | 1.791 | +0.1133 | -0.0088 | -0.198 | +0.1221 | 4.827 | 0.0570 | 55.9% (L:50.0%, S:68.6%) | 91.7x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.80/S:1.40) | 118 | 92 (84L/8S) | 0.977 | 1.577 | +0.1976 | +0.1470 | 1.874 | +0.0506 | 5.935 | 0.1091 | 48.9% (L:48.8%, S:50.0%) | 71.7x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.513 | 0.230 | NOT_SIGNIFICANT | 0.357 | 0.231 | 93% |
| 500ETF | icw | 0.716 | 0.315 | NOT_SIGNIFICANT | 0.543 | 0.436 | 93% |
| 159915ETF | icw | 1.345 | 0.777 | NOT_SIGNIFICANT | 0.805 | 0.446 | 100% |
| 300ETF | ew | 0.534 | 0.247 | NOT_SIGNIFICANT | 0.418 | 0.323 | 87% |
| 500ETF | ew | 0.763 | 0.338 | NOT_SIGNIFICANT | 0.639 | 0.414 | 93% |
| 159915ETF | ew | 0.977 | 0.503 | NOT_SIGNIFICANT | 0.951 | 0.299 | 100% |

