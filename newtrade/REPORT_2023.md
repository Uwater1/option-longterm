# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_linear`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `8.0 bps (+ 2.0 bps stop-loss execution slippage)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.20 (train L:1.50/S:1.10) | 72 | 84 (21L/63S) | 0.547 | 1.258 | +0.0834 | +0.0540 | 3.134 | +0.0293 | 0.890 | 0.0494 | 52.4% (L:61.9%, S:49.2%) | 46.3x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.30 (train L:0.80/S:1.20) | 196 | 204 (139L/65S) | 0.645 | 2.010 | +0.1287 | -0.0552 | -0.880 | +0.1839 | 4.620 | 0.0618 | 53.4% (L:46.8%, S:67.7%) | 105.1x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 84 | 213 (135L/78S) | 1.099 | 1.969 | +0.3539 | +0.1833 | 1.521 | +0.1706 | 3.350 | 0.0849 | 51.6% (L:47.4%, S:59.0%) | 108.2x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.50 (train L:1.20/S:1.40) | 72 | 56 (40L/16S) | 0.361 | 0.909 | +0.0483 | +0.0332 | 1.181 | +0.0152 | 1.726 | 0.0418 | 51.8% (L:52.5%, S:50.0%) | 31.6x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.90/S:1.10) | 196 | 194 (116L/78S) | 0.899 | 2.174 | +0.1812 | -0.0474 | -0.882 | +0.2286 | 4.867 | 0.0491 | 54.6% (L:47.4%, S:65.4%) | 104.1x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 84 | 213 (158L/55S) | 1.056 | 1.876 | +0.3728 | +0.2407 | 1.605 | +0.1321 | 3.433 | 0.1250 | 50.7% (L:46.8%, S:61.8%) | 108.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.547 | 0.313 | NOT_SIGNIFICANT | 0.313 | 0.256 | 93% |
| 500ETF | icw | 0.645 | 0.346 | NOT_SIGNIFICANT | 0.624 | 0.446 | 87% |
| 159915ETF | icw | 1.099 | 0.753 | NOT_SIGNIFICANT | 0.964 | 0.401 | 100% |
| 300ETF | ew | 0.361 | 0.183 | NOT_SIGNIFICANT | 0.393 | 0.360 | 93% |
| 500ETF | ew | 0.899 | 0.547 | NOT_SIGNIFICANT | 0.553 | 0.455 | 93% |
| 159915ETF | ew | 1.056 | 0.721 | NOT_SIGNIFICANT | 1.002 | 0.357 | 100% |

