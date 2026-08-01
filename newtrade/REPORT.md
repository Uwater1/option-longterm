# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-07-17`
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
| 300ETF | Spot ETF | single | 2022-01 ~ 2026-07 | L:1.20/S:1.20 (train L:1.10/S:1.10) | 22 | 103 (63L/40S) | 0.991 | 1.328 | +0.2294 | +0.1444 | 3.198 | +0.0850 | 3.513 | 0.0430 | 59.2% (L:61.9%, S:55.0%) | 45.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2026-07 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 193 | 179 (175L/4S) | 0.580 | 1.013 | +0.1942 | +0.1898 | 1.454 | +0.0044 | 1.085 | 0.0934 | 54.2% (L:54.3%, S:50.0%) | 65.6x |
| 50ETF | Spot ETF | single | 2022-01 ~ present | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2026-07 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 27 | 276 (193L/83S) | 1.217 | 1.616 | +0.6778 | +0.5558 | 2.674 | +0.1219 | 1.834 | 0.1117 | 55.4% (L:53.9%, S:59.0%) | 110.8x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2026-07 | L:1.30/S:1.10 (train L:1.20/S:1.00) | 22 | 121 (51L/70S) | 0.898 | 1.289 | +0.2132 | +0.1416 | 3.627 | +0.0716 | 1.923 | 0.0463 | 57.0% (L:64.7%, S:51.4%) | 53.0x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2026-07 | L:0.90/S:1.40 (train L:0.80/S:1.30) | 193 | 178 (174L/4S) | 0.564 | 0.994 | +0.1886 | +0.1842 | 1.416 | +0.0044 | 1.085 | 0.0934 | 53.9% (L:54.0%, S:50.0%) | 65.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ present | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2026-07 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 27 | 276 (193L/83S) | 1.177 | 1.578 | +0.6535 | +0.5315 | 2.566 | +0.1219 | 1.834 | 0.1117 | 55.1% (L:53.4%, S:59.0%) | 110.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.991 | 0.774 | NOT_SIGNIFICANT | 0.667 | 0.187 | 100% |
| 500ETF | icw | 0.580 | 0.386 | NOT_SIGNIFICANT | 0.830 | 0.396 | 100% |
| 159915ETF | icw | 1.217 | 0.935 | MARGINAL | 0.834 | 0.262 | 100% |
| 300ETF | ew | 0.898 | 0.690 | NOT_SIGNIFICANT | 0.670 | 0.171 | 100% |
| 500ETF | ew | 0.564 | 0.371 | NOT_SIGNIFICANT | 0.839 | 0.359 | 100% |
| 159915ETF | ew | 1.177 | 0.920 | MARGINAL | 0.762 | 0.288 | 100% |

