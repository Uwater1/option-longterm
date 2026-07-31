# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 72 | 61 (18L/43S) | 0.794 | 1.093 | +0.1246 | +0.0656 | 4.100 | +0.0590 | 2.094 | 0.0477 | 55.7% (L:66.7%, S:51.2%) | 40.2x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 196 | 179 (116L/63S) | 1.452 | 2.099 | +0.3104 | +0.0395 | 0.663 | +0.2709 | 6.439 | 0.0325 | 59.2% (L:54.3%, S:68.3%) | 110.9x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 84 | 189 (134L/55S) | 1.485 | 1.866 | +0.5861 | +0.4106 | 2.686 | +0.1755 | 4.032 | 0.0917 | 57.1% (L:53.0%, S:67.3%) | 114.4x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.50 (train L:1.20/S:1.40) | 72 | 56 (40L/16S) | 0.722 | 0.989 | +0.1175 | +0.0698 | 2.344 | +0.0477 | 3.268 | 0.0429 | 55.4% (L:57.5%, S:50.0%) | 37.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 196 | 167 (116L/51S) | 1.352 | 1.973 | +0.2818 | +0.0395 | 0.663 | +0.2424 | 6.794 | 0.0325 | 58.7% (L:54.3%, S:68.6%) | 102.6x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 84 | 213 (158L/55S) | 1.402 | 1.826 | +0.5622 | +0.3616 | 2.124 | +0.2005 | 4.698 | 0.1177 | 55.4% (L:50.6%, S:69.1%) | 124.1x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.794 | 0.543 | NOT_SIGNIFICANT | 0.217 | 0.350 | 73% |
| 500ETF | icw | 1.452 | 0.900 | MARGINAL | 0.782 | 0.353 | 93% |
| 159915ETF | icw | 1.485 | 0.967 | SIGNIFICANT | 1.008 | 0.380 | 100% |
| 300ETF | ew | 0.722 | 0.457 | NOT_SIGNIFICANT | 0.333 | 0.334 | 93% |
| 500ETF | ew | 1.352 | 0.865 | NOT_SIGNIFICANT | 0.636 | 0.453 | 93% |
| 159915ETF | ew | 1.402 | 0.940 | MARGINAL | 0.925 | 0.317 | 100% |

