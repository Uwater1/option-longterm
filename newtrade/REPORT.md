# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `binary`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.20 (train L:1.10/S:1.10) | 22 | 90 (55L/35S) | 1.095 | 1.431 | +0.2221 | +0.1613 | 4.070 | +0.0607 | 2.992 | 0.0430 | 60.0% (L:63.6%, S:54.3%) | 45.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 193 | 139 (136L/3S) | 0.913 | 1.299 | +0.2618 | +0.2359 | 2.247 | +0.0259 | 12.266 | 0.0624 | 55.4% (L:55.1%, S:66.7%) | 58.8x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 27 | 239 (166L/73S) | 1.318 | 1.705 | +0.6513 | +0.5001 | 2.700 | +0.1513 | 2.799 | 0.0925 | 56.9% (L:54.2%, S:63.0%) | 109.2x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.10 (train L:1.20/S:1.00) | 22 | 107 (45L/62S) | 0.993 | 1.387 | +0.2071 | +0.1397 | 3.983 | +0.0674 | 2.161 | 0.0463 | 57.0% (L:64.4%, S:51.6%) | 53.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 193 | 138 (135L/3S) | 0.895 | 1.278 | +0.2562 | +0.2304 | 2.203 | +0.0259 | 12.266 | 0.0624 | 55.1% (L:54.8%, S:66.7%) | 58.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 27 | 239 (166L/73S) | 1.274 | 1.663 | +0.6270 | +0.4758 | 2.579 | +0.1513 | 2.799 | 0.0925 | 56.5% (L:53.6%, S:63.0%) | 109.2x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 1.095 | 0.825 | NOT_SIGNIFICANT | 0.667 | 0.187 | 100% |
| 500ETF | icw | 0.913 | 0.675 | NOT_SIGNIFICANT | 0.830 | 0.396 | 100% |
| 159915ETF | icw | 1.318 | 0.956 | SIGNIFICANT | 0.834 | 0.262 | 100% |
| 300ETF | ew | 0.993 | 0.741 | NOT_SIGNIFICANT | 0.670 | 0.171 | 100% |
| 500ETF | ew | 0.895 | 0.658 | NOT_SIGNIFICANT | 0.839 | 0.359 | 100% |
| 159915ETF | ew | 1.274 | 0.944 | MARGINAL | 0.762 | 0.288 | 100% |

