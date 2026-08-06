# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2025-01-01 ~ 2026-01-01`
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

![Cumulative Equity](artifacts/equity_curve_option_2025.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.70 (train L:1.40/S:1.50) | 34 | 5 opt | 0.018 | 0.175 | +92 RMB | +0.0111 | 2.033 | -0.0102 | -6.958 | 0.0494 | 40.0% (L:33.3%, S:50.0%) | 6.9x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 60 opt | 0.296 | 0.605 | +4,261 RMB | +0.1240 | 1.972 | -0.0814 | -17.829 | 0.1404 | 45.0% (L:50.0%, S:20.0%) | 88.2x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.10 (train L:0.80/S:0.90) | 122 | 61 opt | 1.402 | 1.810 | +34,763 RMB | +0.2716 | 3.493 | +0.0760 | 1.721 | 0.1361 | 47.5% (L:52.4%, S:36.8%) | 87.2x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.70 (train L:1.40/S:1.50) | 34 | 4 opt | -1.414 | -1.301 | -4,084 RMB | -0.0314 | -38.886 | -0.0095 | -6.682 | 0.0474 | 25.0% (L:0.0%, S:50.0%) | 6.4x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 61 opt | 0.854 | 1.147 | +14,107 RMB | +0.2099 | 2.933 | -0.0689 | -9.307 | 0.1039 | 47.5% (L:52.0%, S:27.3%) | 90.2x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 122 | 67 opt | 1.465 | 1.941 | +36,186 RMB | +0.2673 | 3.473 | +0.0946 | 1.856 | 0.1340 | 49.3% (L:52.4%, S:44.0%) | 95.1x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.70/S:1.20 (train L:1.50/S:1.00) | 34 | 15 opt | -1.375 | -0.944 | -6,638 RMB | -0.0299 | -40.049 | -0.0365 | -3.769 | 0.0685 | 20.0% (L:0.0%, S:23.1%) | 24.0x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 63 opt | 0.775 | 1.077 | +12,736 RMB | +0.1957 | 2.687 | -0.0684 | -9.349 | 0.1181 | 47.6% (L:51.9%, S:27.3%) | 91.4x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.00 (train L:0.80/S:0.80) | 122 | 68 opt | 1.298 | 1.776 | +32,342 RMB | +0.2671 | 3.492 | +0.0563 | 1.051 | 0.1340 | 48.5% (L:52.4%, S:42.3%) | 96.2x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.60/S:1.50 (train L:1.40/S:1.30) | 34 | 8 opt | -0.354 | -0.143 | -2,032 RMB | -0.0109 | -1.584 | -0.0095 | -3.762 | 0.0630 | 37.5% (L:25.0%, S:50.0%) | 10.8x |
| 500ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:0.90/S:1.40 (train L:0.70/S:1.20) | 100 | 59 opt | 0.330 | 0.637 | +4,762 RMB | +0.1297 | 2.076 | -0.0821 | -17.799 | 0.1261 | 44.1% (L:49.0%, S:20.0%) | 86.3x |
| 50ETF | Spot ETF | single | 2025-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2025-01 ~ 2025-12 | L:1.00/S:1.20 (train L:0.80/S:1.00) | 122 | 53 opt | 1.983 | 2.344 | +49,653 RMB | +0.3269 | 4.169 | +0.1697 | 4.993 | 0.0837 | 52.8% (L:55.0%, S:46.2%) | 75.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | 0.018 | 0.060 | NOT_SIGNIFICANT | 0.362 | 0.242 | 100% |
| 500ETF | ensemble | 0.296 | 0.100 | NOT_SIGNIFICANT | 0.950 | 0.368 | 100% |
| 159915ETF | ensemble | 1.402 | 0.505 | NOT_SIGNIFICANT | 0.931 | 0.292 | 100% |
| 300ETF | icw | -1.414 | 0.000 | NOT_SIGNIFICANT | 0.518 | 0.272 | 93% |
| 500ETF | icw | 0.854 | 0.243 | NOT_SIGNIFICANT | 1.036 | 0.350 | 100% |
| 159915ETF | icw | 1.465 | 0.540 | NOT_SIGNIFICANT | 0.860 | 0.324 | 100% |
| 300ETF | sortino | -1.375 | 0.002 | NOT_SIGNIFICANT | 0.493 | 0.260 | 93% |
| 500ETF | sortino | 0.775 | 0.217 | NOT_SIGNIFICANT | 1.009 | 0.356 | 100% |
| 159915ETF | sortino | 1.298 | 0.450 | NOT_SIGNIFICANT | 0.849 | 0.309 | 100% |
| 300ETF | ew | -0.354 | 0.028 | NOT_SIGNIFICANT | 0.367 | 0.311 | 100% |
| 500ETF | ew | 0.330 | 0.106 | NOT_SIGNIFICANT | 0.960 | 0.351 | 100% |
| 159915ETF | ew | 1.983 | 0.802 | NOT_SIGNIFICANT | 0.967 | 0.262 | 100% |

