# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Transaction Friction**: `8.0 bps`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.00 (train L:1.20/S:0.90) | 10 | 62 (20L/42S) | 0.816 | 1.334 | +0.1435 | +0.1215 | 6.808 | +0.0220 | 0.939 | 0.0644 | 54.8% (L:70.0%, S:47.6%) | 31.2x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 219 (195L/24S) | 0.879 | 1.935 | +0.2810 | +0.1830 | 1.388 | +0.0980 | 5.285 | 0.1136 | 55.3% (L:54.9%, S:58.3%) | 91.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.90/S:1.00) | 11 | 203 (115L/88S) | 1.422 | 2.191 | +0.5653 | +0.4042 | 3.370 | +0.1611 | 3.016 | 0.0662 | 63.1% (L:60.0%, S:67.0%) | 92.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.00 (train L:1.10/S:0.90) | 10 | 47 (20L/27S) | 0.780 | 1.176 | +0.1346 | +0.1215 | 6.808 | +0.0131 | 0.729 | 0.0716 | 55.3% (L:70.0%, S:44.4%) | 23.4x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 32 | 218 (193L/25S) | 0.835 | 1.893 | +0.2657 | +0.1699 | 1.302 | +0.0958 | 5.032 | 0.1136 | 55.0% (L:54.9%, S:56.0%) | 91.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 588000ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.50 (train L:0.90/S:1.40) | 11 | 114 (113L/1S) | 1.158 | 1.636 | +0.4122 | +0.3983 | 3.351 | +0.0139 | 0.000 | 0.0549 | 59.6% (L:59.3%, S:100.0%) | 49.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.816 | 0.605 | NOT_SIGNIFICANT | 0.851 | 0.239 | 100% |
| 500ETF | icw | 0.879 | 0.611 | NOT_SIGNIFICANT | 1.005 | 0.414 | 100% |
| 159915ETF | icw | 1.422 | 0.929 | MARGINAL | 0.836 | 0.274 | 100% |
| 300ETF | ew | 0.780 | 0.573 | NOT_SIGNIFICANT | 0.705 | 0.257 | 100% |
| 500ETF | ew | 0.835 | 0.573 | NOT_SIGNIFICANT | 0.967 | 0.404 | 100% |
| 159915ETF | ew | 1.158 | 0.833 | NOT_SIGNIFICANT | 0.852 | 0.243 | 100% |

