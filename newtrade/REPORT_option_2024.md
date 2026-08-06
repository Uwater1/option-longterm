# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2024-01-01 ~ 2026-01-01`
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

![Cumulative Equity](artifacts/equity_curve_option_2024.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 37 | 36 opt | 0.752 | 0.988 | +20,093 RMB | +0.1349 | 2.900 | +0.0660 | 2.988 | 0.0732 | 38.9% (L:42.1%, S:35.3%) | 30.7x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 111 | 114 opt | 1.340 | 1.588 | +64,274 RMB | +0.1750 | 1.220 | +0.4678 | 5.540 | 0.2433 | 50.0% (L:44.4%, S:59.5%) | 91.8x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.20/S:1.20 (train L:1.10/S:1.10) | 99 | 75 opt | 1.410 | 1.731 | +66,483 RMB | +0.3341 | 2.680 | +0.3307 | 5.919 | 0.1191 | 48.0% (L:44.2%, S:56.5%) | 59.4x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.50/S:1.30 (train L:1.40/S:1.20) | 37 | 44 opt | 0.450 | 0.754 | +12,255 RMB | +0.1241 | 2.615 | -0.0016 | -0.053 | 0.1189 | 36.4% (L:40.0%, S:33.3%) | 36.9x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 111 | 99 opt | 1.187 | 1.415 | +52,636 RMB | +0.0522 | 0.473 | +0.4742 | 5.567 | 0.1744 | 49.5% (L:42.1%, S:59.5%) | 82.0x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.70/S:1.20 (train L:0.60/S:1.10) | 99 | 135 opt | 0.778 | 1.261 | +40,215 RMB | +0.1213 | 0.546 | +0.2809 | 5.929 | 0.1851 | 40.7% (L:37.5%, S:56.5%) | 105.0x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.50/S:1.40) | 37 | 24 opt | 0.943 | 1.114 | +22,437 RMB | +0.1345 | 3.884 | +0.0899 | 5.893 | 0.0500 | 45.8% (L:42.9%, S:50.0%) | 20.9x |
| 500ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 111 | 91 opt | 1.552 | 1.754 | +82,343 RMB | +0.2781 | 2.049 | +0.5453 | 6.239 | 0.1996 | 51.6% (L:45.5%, S:61.1%) | 75.3x |
| 50ETF | Spot ETF | single | 2024-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2024-01 ~ 2025-12 | L:0.80/S:1.50 (train L:0.70/S:1.40) | 99 | 99 opt | 0.713 | 1.119 | +29,328 RMB | +0.1029 | 0.648 | +0.1904 | 10.523 | 0.1794 | 40.4% (L:38.7%, S:66.7%) | 77.7x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | 0.752 | 0.355 | NOT_SIGNIFICANT | 0.392 | 0.311 | 93% |
| 500ETF | icw | 1.340 | 0.690 | NOT_SIGNIFICANT | 1.014 | 0.353 | 100% |
| 159915ETF | icw | 1.410 | 0.787 | NOT_SIGNIFICANT | 0.846 | 0.337 | 100% |
| 300ETF | sortino | 0.450 | 0.184 | NOT_SIGNIFICANT | 0.414 | 0.271 | 87% |
| 500ETF | sortino | 1.187 | 0.603 | NOT_SIGNIFICANT | 0.923 | 0.345 | 100% |
| 159915ETF | sortino | 0.778 | 0.352 | NOT_SIGNIFICANT | 0.859 | 0.353 | 100% |
| 300ETF | ew | 0.943 | 0.536 | NOT_SIGNIFICANT | 0.278 | 0.305 | 93% |
| 500ETF | ew | 1.552 | 0.841 | NOT_SIGNIFICANT | 0.997 | 0.479 | 100% |
| 159915ETF | ew | 0.713 | 0.306 | NOT_SIGNIFICANT | 0.995 | 0.378 | 100% |

