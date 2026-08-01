# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.20 (train L:1.40/S:1.10) | 95 | 20 (5L/15S) | 0.368 | 1.052 | +0.0083 | +0.0066 | 2.877 | +0.0017 | 0.446 | 0.0165 | 40.0% (L:60.0%, S:33.3%) | 37.3x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 159 | 76 (59L/17S) | 1.091 | 2.126 | +0.0624 | +0.0574 | 2.413 | +0.0050 | 0.632 | 0.0368 | 56.6% (L:57.6%, S:52.9%) | 132.7x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 146 | 54 (41L/13S) | 2.109 | 2.572 | +0.1864 | +0.1156 | 4.485 | +0.0708 | 5.310 | 0.0406 | 61.1% (L:58.5%, S:69.2%) | 101.6x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 95 | 8 (1L/7S) | 0.698 | 1.078 | +0.0104 | +0.0081 | 0.000 | +0.0024 | 1.106 | 0.0087 | 50.0% (L:100.0%, S:42.9%) | 16.6x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 159 | 52 (35L/17S) | 0.280 | 1.147 | +0.0133 | +0.0204 | 1.424 | -0.0070 | -0.915 | 0.0356 | 51.9% (L:54.3%, S:47.1%) | 93.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 146 | 56 (41L/15S) | 1.892 | 2.370 | +0.1721 | +0.1118 | 4.184 | +0.0603 | 4.026 | 0.0598 | 62.5% (L:61.0%, S:66.7%) | 105.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.368 | 0.114 | NOT_SIGNIFICANT | 0.356 | 0.263 | 80% |
| 500ETF | icw | 1.091 | 0.312 | NOT_SIGNIFICANT | 0.769 | 0.466 | 93% |
| 159915ETF | icw | 2.109 | 0.802 | NOT_SIGNIFICANT | 0.905 | 0.364 | 100% |
| 300ETF | ew | 0.698 | 0.193 | NOT_SIGNIFICANT | 0.152 | 0.281 | 67% |
| 500ETF | ew | 0.280 | 0.097 | NOT_SIGNIFICANT | 0.680 | 0.499 | 87% |
| 159915ETF | ew | 1.892 | 0.697 | NOT_SIGNIFICANT | 0.815 | 0.392 | 100% |

