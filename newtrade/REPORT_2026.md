# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2026.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.30/S:1.60 (train L:1.20/S:1.50) | 99 | 8 (6L/2S) | 0.358 | 0.669 | +0.0071 | +0.0138 | 5.216 | -0.0067 | -9.899 | 0.0087 | 62.5% (L:66.7%, S:50.0%) | 16.6x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.10/S:1.30) | 126 | 28 (22L/6S) | -0.350 | 0.241 | -0.0134 | -0.0021 | -0.193 | -0.0112 | -7.874 | 0.0391 | 46.4% (L:45.5%, S:50.0%) | 58.1x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.20 (train L:1.00/S:1.10) | 146 | 58 (37L/21S) | 1.046 | 1.621 | +0.0847 | +0.1063 | 4.004 | -0.0216 | -1.820 | 0.0406 | 53.4% (L:54.1%, S:52.4%) | 112.0x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.40/S:1.40 (train L:1.30/S:1.30) | 99 | 7 (5L/2S) | 0.889 | 1.155 | +0.0158 | +0.0225 | 13.180 | -0.0067 | -9.899 | 0.0087 | 71.4% (L:80.0%, S:50.0%) | 14.5x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.40 (train L:1.00/S:1.30) | 126 | 37 (31L/6S) | 0.671 | 1.320 | +0.0300 | +0.0412 | 2.686 | -0.0112 | -7.874 | 0.0330 | 54.1% (L:54.8%, S:50.0%) | 72.6x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.10/S:1.20 (train L:1.00/S:1.10) | 146 | 58 (37L/21S) | 1.046 | 1.621 | +0.0847 | +0.1063 | 4.004 | -0.0216 | -1.820 | 0.0406 | 53.4% (L:54.1%, S:52.4%) | 112.0x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.358 | 0.111 | NOT_SIGNIFICANT | 0.369 | 0.268 | 80% |
| 500ETF | icw | -0.350 | 0.028 | NOT_SIGNIFICANT | 0.796 | 0.505 | 93% |
| 159915ETF | icw | 1.046 | 0.313 | NOT_SIGNIFICANT | 0.732 | 0.199 | 100% |
| 300ETF | ew | 0.889 | 0.266 | NOT_SIGNIFICANT | 0.346 | 0.306 | 87% |
| 500ETF | ew | 0.671 | 0.183 | NOT_SIGNIFICANT | 1.061 | 0.491 | 93% |
| 159915ETF | ew | 1.046 | 0.313 | NOT_SIGNIFICANT | 0.693 | 0.241 | 100% |

