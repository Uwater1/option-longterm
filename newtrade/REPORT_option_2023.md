# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2023-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.1)
- **Position Mode**: `fast_ramp_quadratic`
- **Mode**: `Option Portfolio`
- **Initial Capital**: `100,000 RMB per ETF`
- **Trade Budget**: `10% of portfolio capital per signal`
- **Commission**: `4.0 RMB per contract per side (8.0 RMB round-trip per contract)`
- **Option Selection**: `Nearest OTM, >=7 DTM`

## IC Weight (ICW)

![Cumulative Equity](artifacts/equity_curve_option_2023.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.40 (train L:1.20/S:1.30) | 47 | 49 opt | 0.703 | 0.942 | +24,556 RMB | +0.2621 | 3.599 | -0.0165 | -1.251 | 0.0900 | 51.0% (L:50.0%, S:53.8%) | 28.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.50 (train L:1.10/S:1.40) | 297 | 110 opt | 0.865 | 1.096 | +44,037 RMB | +0.0232 | 0.195 | +0.4172 | 5.596 | 0.1723 | 50.9% (L:46.4%, S:58.5%) | 59.6x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 77 | 197 opt | 0.831 | 1.414 | +74,667 RMB | +0.3254 | 1.074 | +0.4212 | 2.596 | 0.2492 | 43.7% (L:37.9%, S:53.4%) | 102.8x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.50 (train L:1.20/S:1.40) | 47 | 42 opt | 0.658 | 0.854 | +22,132 RMB | +0.2587 | 3.605 | -0.0374 | -7.067 | 0.0849 | 50.0% (L:50.0%, S:50.0%) | 25.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.30 (train L:1.10/S:1.20) | 297 | 139 opt | 1.144 | 1.396 | +78,060 RMB | -0.0191 | -0.134 | +0.7996 | 5.413 | 0.2598 | 52.5% (L:45.7%, S:59.4%) | 74.7x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.00 (train L:0.70/S:0.90) | 77 | 196 opt | 0.851 | 1.430 | +77,724 RMB | +0.3299 | 1.071 | +0.4473 | 2.739 | 0.2535 | 43.9% (L:37.9%, S:54.2%) | 102.2x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 47 | 30 opt | 0.822 | 0.984 | +23,601 RMB | +0.1972 | 4.765 | +0.0388 | 3.030 | 0.0502 | 56.7% (L:52.6%, S:63.6%) | 17.0x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.80/S:1.10) | 297 | 210 opt | 1.555 | 1.829 | +180,938 RMB | +0.7632 | 2.002 | +1.0462 | 4.453 | 0.3470 | 52.4% (L:48.5%, S:58.8%) | 109.2x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 77 | 179 opt | 1.114 | 1.645 | +104,650 RMB | +0.5486 | 1.837 | +0.4979 | 3.068 | 0.2389 | 45.8% (L:40.4%, S:54.3%) | 92.1x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.703 | 0.415 | NOT_SIGNIFICANT | 0.483 | 0.278 | 93% |
| 500ETF | icw | 0.865 | 0.495 | NOT_SIGNIFICANT | 1.033 | 0.379 | 100% |
| 159915ETF | icw | 0.831 | 0.483 | NOT_SIGNIFICANT | 1.047 | 0.353 | 100% |
| 300ETF | sortino | 0.658 | 0.382 | NOT_SIGNIFICANT | 0.474 | 0.250 | 100% |
| 500ETF | sortino | 1.144 | 0.693 | NOT_SIGNIFICANT | 0.732 | 0.336 | 100% |
| 159915ETF | sortino | 0.851 | 0.499 | NOT_SIGNIFICANT | 1.072 | 0.338 | 100% |
| 300ETF | ew | 0.822 | 0.575 | NOT_SIGNIFICANT | 0.421 | 0.245 | 100% |
| 500ETF | ew | 1.555 | 0.923 | MARGINAL | 0.928 | 0.519 | 93% |
| 159915ETF | ew | 1.114 | 0.706 | NOT_SIGNIFICANT | 1.101 | 0.322 | 100% |

