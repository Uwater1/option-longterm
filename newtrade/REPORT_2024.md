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
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 37 | 36 (19L/17S) | 0.231 | 0.738 | +0.0210 | +0.0316 | 1.815 | -0.0106 | -2.734 | 0.0324 | 41.7% (L:47.4%, S:35.3%) | 30.7x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 111 | 114 (72L/42S) | 0.937 | 1.921 | +0.1442 | -0.0465 | -1.128 | +0.1907 | 6.299 | 0.1063 | 55.3% (L:47.2%, S:69.0%) | 91.8x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.20 (train L:1.10/S:1.10) | 99 | 75 (52L/23S) | 1.522 | 1.964 | +0.3271 | +0.1820 | 3.352 | +0.1451 | 5.247 | 0.0534 | 57.3% (L:55.8%, S:60.9%) | 59.4x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.30 (train L:1.40/S:1.20) | 37 | 44 (20L/24S) | 0.218 | 0.828 | +0.0202 | +0.0384 | 2.137 | -0.0182 | -3.255 | 0.0328 | 43.2% (L:50.0%, S:37.5%) | 36.9x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 111 | 99 (57L/42S) | 0.889 | 1.775 | +0.1315 | -0.0578 | -1.713 | +0.1892 | 6.277 | 0.0875 | 55.6% (L:45.6%, S:69.0%) | 82.0x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.70/S:1.20 (train L:0.60/S:1.10) | 99 | 135 (112L/23S) | 1.094 | 1.740 | +0.3144 | +0.1698 | 1.388 | +0.1446 | 5.258 | 0.1220 | 48.1% (L:45.5%, S:60.9%) | 105.0x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.50/S:1.40) | 37 | 24 (14L/10S) | 0.461 | 0.828 | +0.0384 | +0.0406 | 2.982 | -0.0022 | -0.888 | 0.0323 | 50.0% (L:50.0%, S:50.0%) | 20.9x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 111 | 91 (55L/36S) | 0.817 | 1.667 | +0.1175 | -0.0255 | -0.747 | +0.1430 | 5.454 | 0.0694 | 57.1% (L:50.9%, S:66.7%) | 75.3x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.50 (train L:0.70/S:1.40) | 99 | 99 (93L/6S) | 0.965 | 1.556 | +0.2221 | +0.1561 | 1.639 | +0.0660 | 9.444 | 0.0985 | 48.5% (L:47.3%, S:66.7%) | 77.7x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.231 | 0.110 | NOT_SIGNIFICANT | 0.392 | 0.311 | 93% |
| 500ETF | icw | 0.937 | 0.444 | NOT_SIGNIFICANT | 1.014 | 0.353 | 100% |
| 159915ETF | icw | 1.522 | 0.886 | NOT_SIGNIFICANT | 0.846 | 0.337 | 100% |
| 300ETF | sortino | 0.218 | 0.106 | NOT_SIGNIFICANT | 0.414 | 0.271 | 87% |
| 500ETF | sortino | 0.889 | 0.420 | NOT_SIGNIFICANT | 0.923 | 0.345 | 100% |
| 159915ETF | sortino | 1.094 | 0.616 | NOT_SIGNIFICANT | 0.859 | 0.353 | 100% |
| 300ETF | ew | 0.461 | 0.218 | NOT_SIGNIFICANT | 0.278 | 0.305 | 93% |
| 500ETF | ew | 0.817 | 0.377 | NOT_SIGNIFICANT | 0.997 | 0.479 | 100% |
| 159915ETF | ew | 0.965 | 0.524 | NOT_SIGNIFICANT | 0.995 | 0.378 | 100% |

