# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.40 (train L:1.20/S:1.30) | 47 | 49 (36L/13S) | 0.027 | 0.569 | +0.0033 | +0.0258 | 1.004 | -0.0225 | -5.071 | 0.0451 | 51.0% (L:52.8%, S:46.2%) | 28.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.10/S:1.40) | 297 | 110 (69L/41S) | 0.792 | 1.633 | +0.1345 | -0.0353 | -1.057 | +0.1697 | 5.817 | 0.0445 | 51.8% (L:42.0%, S:68.3%) | 59.6x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 77 | 197 (124L/73S) | 1.079 | 1.870 | +0.3515 | +0.1946 | 1.705 | +0.1569 | 2.943 | 0.0938 | 51.3% (L:46.0%, S:60.3%) | 102.8x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.50 (train L:1.20/S:1.40) | 47 | 42 (36L/6S) | 0.029 | 0.505 | +0.0034 | +0.0256 | 0.995 | -0.0221 | -9.185 | 0.0449 | 50.0% (L:52.8%, S:33.3%) | 25.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 297 | 139 (70L/69S) | 0.894 | 1.864 | +0.1655 | -0.0413 | -1.224 | +0.2068 | 4.667 | 0.0457 | 54.0% (L:41.4%, S:66.7%) | 74.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 77 | 196 (124L/72S) | 1.077 | 1.865 | +0.3507 | +0.1947 | 1.706 | +0.1560 | 2.949 | 0.0935 | 51.0% (L:46.0%, S:59.7%) | 102.2x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 47 | 30 (19L/11S) | 0.386 | 0.719 | +0.0436 | +0.0485 | 3.002 | -0.0050 | -0.823 | 0.0340 | 56.7% (L:57.9%, S:54.5%) | 17.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 297 | 210 (130L/80S) | 0.688 | 2.027 | +0.1470 | -0.0101 | -0.160 | +0.1571 | 3.156 | 0.0662 | 53.8% (L:49.2%, S:61.3%) | 109.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 77 | 179 (109L/70S) | 1.257 | 1.969 | +0.4077 | +0.2185 | 2.193 | +0.1891 | 3.171 | 0.0872 | 53.6% (L:47.7%, S:62.9%) | 92.1x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.027 | 0.063 | NOT_SIGNIFICANT | 0.483 | 0.278 | 93% |
| 500ETF | icw | 0.792 | 0.499 | NOT_SIGNIFICANT | 1.033 | 0.379 | 100% |
| 159915ETF | icw | 1.079 | 0.752 | NOT_SIGNIFICANT | 1.047 | 0.353 | 100% |
| 300ETF | sortino | 0.029 | 0.064 | NOT_SIGNIFICANT | 0.474 | 0.250 | 100% |
| 500ETF | sortino | 0.894 | 0.562 | NOT_SIGNIFICANT | 0.732 | 0.336 | 100% |
| 159915ETF | sortino | 1.077 | 0.751 | NOT_SIGNIFICANT | 1.072 | 0.338 | 100% |
| 300ETF | ew | 0.386 | 0.208 | NOT_SIGNIFICANT | 0.421 | 0.245 | 100% |
| 500ETF | ew | 0.688 | 0.372 | NOT_SIGNIFICANT | 0.928 | 0.519 | 93% |
| 159915ETF | ew | 1.257 | 0.874 | NOT_SIGNIFICANT | 1.101 | 0.322 | 100% |

