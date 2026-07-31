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
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.50 (train L:1.40/S:1.40) | 95 | 6 (3L/3S) | 1.392 | 1.604 | +0.0196 | +0.0151 | 12.606 | +0.0045 | 21.372 | 0.0038 | 66.7% (L:66.7%, S:66.7%) | 12.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 159 | 52 (35L/17S) | 0.280 | 1.147 | +0.0133 | +0.0204 | 1.424 | -0.0070 | -0.915 | 0.0356 | 51.9% (L:54.3%, S:47.1%) | 93.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.60 (train L:1.00/S:1.50) | 146 | 29 (28L/1S) | 1.826 | 2.109 | +0.1359 | +0.0903 | 4.614 | +0.0457 | 0.000 | 0.0203 | 62.1% (L:60.7%, S:100.0%) | 53.9x |

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
| 300ETF | icw | 1.392 | 0.721 | NOT_SIGNIFICANT | 0.085 | 0.310 | 60% |
| 500ETF | icw | 0.280 | 0.097 | NOT_SIGNIFICANT | 0.642 | 0.518 | 93% |
| 159915ETF | icw | 1.826 | 0.744 | NOT_SIGNIFICANT | 0.891 | 0.369 | 100% |
| 300ETF | ew | 0.698 | 0.193 | NOT_SIGNIFICANT | 0.152 | 0.281 | 67% |
| 500ETF | ew | 0.280 | 0.097 | NOT_SIGNIFICANT | 0.680 | 0.499 | 87% |
| 159915ETF | ew | 1.892 | 0.697 | NOT_SIGNIFICANT | 0.815 | 0.392 | 100% |

