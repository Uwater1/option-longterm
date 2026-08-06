# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2022-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Mode**: `Option Portfolio`
- **Initial Capital**: `100,000 RMB per ETF`
- **Trade Budget**: `10% of portfolio capital per signal`
- **Commission**: `4.0 RMB per contract per side (8.0 RMB round-trip per contract)`
- **Option Selection**: `Nearest OTM, >=7 DTM`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_option.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.70 (train L:1.00/S:1.50) | 26 | 60 opt | 0.585 | 0.766 | +26,263 RMB | +0.2528 | 2.432 | +0.0099 | 1.501 | 0.0928 | 46.7% (L:46.4%, S:50.0%) | 25.5x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.70 (train L:1.00/S:1.50) | 317 | 99 opt | 0.827 | 1.006 | +54,074 RMB | -0.0101 | -0.068 | +0.5508 | 8.712 | 0.3228 | 46.4% (L:40.2%, S:63.3%) | 39.9x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.70 (train L:0.70/S:1.50) | 37 | 97 opt | 0.121 | 0.462 | +5,723 RMB | +0.0623 | 0.375 | -0.0051 | -2.191 | 0.2034 | 30.1% (L:29.8%, S:50.0%) | 43.9x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.50/S:1.70 (train L:1.30/S:1.50) | 26 | 31 opt | 0.702 | 0.812 | +26,137 RMB | +0.3077 | 5.091 | -0.0463 | -60.223 | 0.0603 | 54.8% (L:58.6%, S:0.0%) | 12.9x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.60 (train L:1.00/S:1.40) | 317 | 112 opt | 0.933 | 1.128 | +65,004 RMB | -0.0050 | -0.032 | +0.6551 | 7.681 | 0.2862 | 46.4% (L:39.8%, S:59.5%) | 46.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.20 (train L:0.70/S:1.00) | 37 | 153 opt | 0.550 | 1.030 | +35,558 RMB | +0.1926 | 0.928 | +0.1630 | 1.958 | 0.1460 | 32.7% (L:29.7%, S:37.8%) | 70.9x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.30/S:1.70 (train L:1.10/S:1.50) | 26 | 51 opt | 0.491 | 0.650 | +20,241 RMB | +0.2470 | 2.737 | -0.0446 | -55.136 | 0.0892 | 45.1% (L:46.9%, S:0.0%) | 21.7x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.00/S:1.20) | 317 | 131 opt | 0.891 | 1.102 | +67,851 RMB | -0.0188 | -0.119 | +0.6973 | 5.319 | 0.3100 | 44.9% (L:39.8%, S:51.6%) | 56.0x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.70/S:0.90) | 37 | 177 opt | 0.649 | 1.184 | +46,249 RMB | +0.2280 | 1.055 | +0.2345 | 1.837 | 0.1555 | 34.5% (L:30.4%, S:39.1%) | 82.4x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.50/S:1.40 (train L:1.30/S:1.20) | 26 | 45 opt | 0.651 | 0.810 | +26,384 RMB | +0.2978 | 5.110 | -0.0340 | -1.451 | 0.0839 | 48.9% (L:55.6%, S:38.9%) | 17.6x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.00/S:1.40 (train L:0.80/S:1.20) | 317 | 182 opt | 1.028 | 1.271 | +102,500 RMB | +0.2284 | 0.734 | +0.7966 | 5.483 | 0.2670 | 45.2% (L:42.0%, S:52.2%) | 76.5x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.70 (train L:0.70/S:1.50) | 37 | 93 opt | 0.272 | 0.588 | +12,972 RMB | +0.1377 | 0.844 | -0.0080 | -2.663 | 0.1744 | 30.5% (L:30.4%, S:33.3%) | 42.3x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.585 | 0.378 | NOT_SIGNIFICANT | 0.507 | 0.214 | 100% |
| 500ETF | ensemble | 0.827 | 0.573 | NOT_SIGNIFICANT | 0.936 | 0.440 | 93% |
| 159915ETF | ensemble | 0.121 | 0.091 | NOT_SIGNIFICANT | 1.049 | 0.462 | 100% |
| 300ETF | icw | 0.702 | 0.548 | NOT_SIGNIFICANT | 0.746 | 0.268 | 100% |
| 500ETF | icw | 0.933 | 0.661 | NOT_SIGNIFICANT | 0.842 | 0.343 | 93% |
| 159915ETF | icw | 0.550 | 0.332 | NOT_SIGNIFICANT | 1.017 | 0.353 | 100% |
| 300ETF | sortino | 0.491 | 0.304 | NOT_SIGNIFICANT | 0.464 | 0.156 | 100% |
| 500ETF | sortino | 0.891 | 0.617 | NOT_SIGNIFICANT | 0.828 | 0.303 | 93% |
| 159915ETF | sortino | 0.649 | 0.410 | NOT_SIGNIFICANT | 0.972 | 0.332 | 100% |
| 300ETF | ew | 0.651 | 0.465 | NOT_SIGNIFICANT | 0.655 | 0.212 | 100% |
| 500ETF | ew | 1.028 | 0.724 | NOT_SIGNIFICANT | 1.030 | 0.422 | 93% |
| 159915ETF | ew | 0.272 | 0.153 | NOT_SIGNIFICANT | 0.979 | 0.447 | 100% |

