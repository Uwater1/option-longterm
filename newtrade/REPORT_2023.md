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
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 72 | 84 (21L/63S) | 0.891 | 1.291 | +0.1439 | +0.0810 | 4.599 | +0.0629 | 1.785 | 0.0439 | 53.6% (L:66.7%, S:49.2%) | 54.1x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.30 (train L:0.80/S:1.20) | 196 | 204 (139L/65S) | 1.279 | 1.990 | +0.2873 | +0.0376 | 0.530 | +0.2496 | 5.681 | 0.0637 | 57.8% (L:53.2%, S:67.7%) | 120.6x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 84 | 213 (135L/78S) | 1.472 | 1.930 | +0.5407 | +0.2431 | 1.949 | +0.2976 | 4.154 | 0.0744 | 56.8% (L:51.1%, S:66.7%) | 127.9x |

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
| 300ETF | icw | 0.891 | 0.626 | NOT_SIGNIFICANT | 0.239 | 0.389 | 80% |
| 500ETF | icw | 1.279 | 0.805 | NOT_SIGNIFICANT | 0.667 | 0.500 | 87% |
| 159915ETF | icw | 1.472 | 0.951 | SIGNIFICANT | 0.887 | 0.366 | 93% |
| 300ETF | ew | 0.722 | 0.457 | NOT_SIGNIFICANT | 0.333 | 0.334 | 93% |
| 500ETF | ew | 1.352 | 0.865 | NOT_SIGNIFICANT | 0.636 | 0.453 | 93% |
| 159915ETF | ew | 1.402 | 0.940 | MARGINAL | 0.925 | 0.317 | 100% |

