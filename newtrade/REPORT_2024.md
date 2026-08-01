# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 85 | 59 (22L/37S) | 0.776 | 1.151 | +0.0951 | +0.0568 | 2.869 | +0.0382 | 1.782 | 0.0430 | 45.8% (L:54.5%, S:40.5%) | 58.2x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 144 | 98 (56L/42S) | 1.175 | 1.698 | +0.1733 | +0.0167 | 0.476 | +0.1565 | 5.322 | 0.0434 | 60.2% (L:57.1%, S:64.3%) | 93.5x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 118 | 90 (70L/20S) | 1.538 | 1.806 | +0.4065 | +0.2226 | 2.778 | +0.1839 | 6.193 | 0.0786 | 54.4% (L:51.4%, S:65.0%) | 84.2x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.40/S:1.40) | 85 | 30 (19L/11S) | 0.745 | 0.948 | +0.0841 | +0.0283 | 1.653 | +0.0558 | 5.425 | 0.0363 | 50.0% (L:47.4%, S:54.5%) | 30.1x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.90/S:1.30) | 144 | 111 (76L/35S) | 1.313 | 1.858 | +0.2094 | +0.0515 | 1.060 | +0.1579 | 6.148 | 0.0511 | 58.6% (L:53.9%, S:68.6%) | 102.9x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.90/S:1.50 (train L:0.80/S:1.40) | 118 | 92 (84L/8S) | 1.184 | 1.482 | +0.2913 | +0.2289 | 2.374 | +0.0623 | 6.860 | 0.1082 | 52.2% (L:51.2%, S:62.5%) | 84.2x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.776 | 0.411 | NOT_SIGNIFICANT | 0.335 | 0.214 | 93% |
| 500ETF | icw | 1.175 | 0.623 | NOT_SIGNIFICANT | 0.635 | 0.458 | 93% |
| 159915ETF | icw | 1.538 | 0.922 | MARGINAL | 0.776 | 0.413 | 93% |
| 300ETF | ew | 0.745 | 0.417 | NOT_SIGNIFICANT | 0.378 | 0.247 | 93% |
| 500ETF | ew | 1.313 | 0.693 | NOT_SIGNIFICANT | 0.482 | 0.429 | 93% |
| 159915ETF | ew | 1.184 | 0.717 | NOT_SIGNIFICANT | 0.943 | 0.316 | 100% |

