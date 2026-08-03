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
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.20/S:1.40 (train L:1.10/S:1.30) | 51 | 85 (54L/31S) | -0.148 | 0.693 | -0.0203 | +0.0025 | 0.073 | -0.0227 | -1.905 | 0.0815 | 47.1% (L:44.4%, S:51.6%) | 48.7x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.30 (train L:1.20/S:1.20) | 215 | 121 (57L/64S) | 1.124 | 2.012 | +0.1914 | +0.0050 | 0.186 | +0.1864 | 4.646 | 0.0426 | 57.9% (L:45.6%, S:68.8%) | 65.8x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:0.90 (train L:0.70/S:0.80) | 78 | 256 (137L/119S) | 1.404 | 2.289 | +0.5226 | +0.2958 | 2.215 | +0.2268 | 2.735 | 0.0861 | 52.7% (L:48.9%, S:57.1%) | 125.9x |

<details>
<summary><b>Equal Weight (EW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.30/S:1.30 (train L:1.20/S:1.20) | 51 | 99 (44L/55S) | 0.307 | 1.166 | +0.0468 | +0.0296 | 1.012 | +0.0172 | 0.659 | 0.0688 | 52.5% (L:50.0%, S:54.5%) | 55.4x |
| 500ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:1.00/S:1.30 (train L:0.90/S:1.20) | 215 | 182 (116L/66S) | 0.674 | 1.914 | +0.1316 | -0.0595 | -1.103 | +0.1911 | 4.692 | 0.0687 | 52.7% (L:44.8%, S:66.7%) | 96.6x |
| 50ETF | Spot ETF | single | 2023-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2023-01 ~ 2025-12 | L:0.80/S:1.10 (train L:0.70/S:1.00) | 78 | 185 (131L/54S) | 1.137 | 1.858 | +0.3809 | +0.2660 | 2.011 | +0.1149 | 3.633 | 0.1093 | 52.4% (L:48.1%, S:63.0%) | 97.8x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | icw | -0.148 | 0.035 | NOT_SIGNIFICANT | 0.198 | 0.290 | 73% |
| 500ETF | icw | 1.124 | 0.779 | NOT_SIGNIFICANT | 0.884 | 0.417 | 100% |
| 159915ETF | icw | 1.404 | 0.933 | MARGINAL | 0.903 | 0.390 | 93% |
| 300ETF | ew | 0.307 | 0.154 | NOT_SIGNIFICANT | 0.136 | 0.353 | 67% |
| 500ETF | ew | 0.674 | 0.370 | NOT_SIGNIFICANT | 0.863 | 0.410 | 93% |
| 159915ETF | ew | 1.137 | 0.817 | NOT_SIGNIFICANT | 1.039 | 0.389 | 100% |

