# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 22 | 118 (76L/42S) | 0.609 | 1.353 | +0.1255 | +0.0860 | 1.795 | +0.0395 | 1.676 | 0.0503 | 53.4% (L:52.6%, S:54.8%) | 50.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.60/S:1.10 (train L:0.50/S:1.00) | 193 | 414 (284L/130S) | 0.636 | 2.340 | +0.2156 | -0.0327 | -0.227 | +0.2484 | 3.303 | 0.1044 | 50.5% (L:47.2%, S:57.7%) | 152.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 27 | 253 (154L/99S) | 1.207 | 1.919 | +0.5528 | +0.3642 | 2.461 | +0.1886 | 2.256 | 0.0881 | 54.2% (L:50.0%, S:60.6%) | 96.9x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.40/S:1.20 (train L:1.30/S:1.10) | 22 | 98 (39L/59S) | 0.451 | 1.160 | +0.0787 | +0.0840 | 2.889 | -0.0053 | -0.227 | 0.0540 | 56.1% (L:59.0%, S:54.2%) | 40.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.20 (train L:0.60/S:1.10) | 193 | 358 (247L/111S) | 0.678 | 2.303 | +0.2065 | -0.0689 | -0.587 | +0.2753 | 4.277 | 0.0969 | 52.5% (L:48.2%, S:62.2%) | 131.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 27 | 248 (152L/96S) | 1.081 | 1.847 | +0.4514 | +0.3773 | 2.602 | +0.0741 | 1.220 | 0.0770 | 54.4% (L:52.0%, S:58.3%) | 94.9x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.609 | 0.407 | NOT_SIGNIFICANT | 0.517 | 0.174 | 100% |
| 500ETF | icw | 0.636 | 0.392 | NOT_SIGNIFICANT | 0.656 | 0.405 | 93% |
| 159915ETF | icw | 1.207 | 0.925 | MARGINAL | 1.092 | 0.311 | 100% |
| 300ETF | ew | 0.451 | 0.271 | NOT_SIGNIFICANT | 0.434 | 0.227 | 100% |
| 500ETF | ew | 0.678 | 0.427 | NOT_SIGNIFICANT | 0.792 | 0.367 | 93% |
| 159915ETF | ew | 1.081 | 0.846 | NOT_SIGNIFICANT | 1.095 | 0.325 | 100% |

