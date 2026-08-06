# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
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

![Cumulative Equity](artifacts/equity_curve_option_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.30 (train L:1.50/S:1.20) | 34 | 12 opt | -1.176 | -0.792 | -5,671 RMB | -0.0302 | -40.049 | -0.0265 | -3.112 | 0.0589 | 25.0% (L:0.0%, S:30.0%) | 19.7x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 100 | 73 opt | 0.644 | 0.967 | +11,445 RMB | +0.1554 | 1.818 | -0.0409 | -4.055 | 0.0948 | 46.6% (L:49.2%, S:33.3%) | 109.8x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 122 | 61 opt | 1.437 | 1.852 | +35,249 RMB | +0.2383 | 3.000 | +0.1142 | 2.767 | 0.1119 | 47.5% (L:51.2%, S:38.9%) | 96.8x |

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.40 (train L:1.50/S:1.30) | 34 | 11 opt | -0.352 | 0.013 | -1,909 RMB | +0.0107 | 2.011 | -0.0298 | -7.451 | 0.0487 | 27.3% (L:33.3%, S:25.0%) | 18.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 100 | 73 opt | 0.857 | 1.182 | +15,261 RMB | +0.1937 | 2.274 | -0.0411 | -3.999 | 0.0948 | 47.9% (L:50.8%, S:33.3%) | 110.0x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:0.90 (train L:0.80/S:0.80) | 122 | 81 opt | 0.919 | 1.476 | +23,552 RMB | +0.2277 | 3.029 | +0.0078 | 0.109 | 0.1561 | 46.9% (L:51.2%, S:42.1%) | 122.3x |

</details>

<details>
<summary><b>Equal Weight (EW, Score-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.40/S:1.30) | 34 | 11 opt | -0.105 | 0.244 | -558 RMB | +0.0115 | 1.837 | -0.0171 | -5.020 | 0.0487 | 36.4% (L:50.0%, S:28.6%) | 18.1x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.80/S:1.30 (train L:0.70/S:1.20) | 100 | 75 opt | 0.800 | 1.110 | +15,958 RMB | +0.1233 | 1.436 | +0.0363 | 1.546 | 0.1184 | 45.3% (L:47.6%, S:33.3%) | 113.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.00 (train L:0.80/S:0.90) | 122 | 69 opt | 1.468 | 1.946 | +38,792 RMB | +0.2861 | 3.518 | +0.1019 | 1.766 | 0.1630 | 49.3% (L:52.4%, S:44.4%) | 108.4x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -1.176 | 0.003 | NOT_SIGNIFICANT | 0.495 | 0.237 | 93% |
| 500ETF | icw | 0.644 | 0.178 | NOT_SIGNIFICANT | 1.038 | 0.337 | 100% |
| 159915ETF | icw | 1.437 | 0.526 | NOT_SIGNIFICANT | 0.948 | 0.285 | 100% |
| 300ETF | sortino | -0.352 | 0.029 | NOT_SIGNIFICANT | 0.452 | 0.303 | 93% |
| 500ETF | sortino | 0.857 | 0.242 | NOT_SIGNIFICANT | 0.870 | 0.343 | 100% |
| 159915ETF | sortino | 0.919 | 0.275 | NOT_SIGNIFICANT | 0.964 | 0.256 | 100% |
| 300ETF | ew | -0.105 | 0.047 | NOT_SIGNIFICANT | 0.378 | 0.281 | 93% |
| 500ETF | ew | 0.800 | 0.229 | NOT_SIGNIFICANT | 1.018 | 0.377 | 100% |
| 159915ETF | ew | 1.468 | 0.531 | NOT_SIGNIFICANT | 1.027 | 0.356 | 100% |

