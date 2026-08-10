# NewTrade OOS Backtest Report

- **OOS Evaluation Period**: `2026-01-01 ~ 2026-01-01`
- **Intraday Trade Session**: `10:00 AM Open -> 14:35 PM Close`
- **Scheme(s)**: `ALL`
- **Conviction Threshold**: `auto` (buffer=+0.2)
- **Position Mode**: `fast_ramp_quadratic`
- **Stop-Loss Execution**: `Enabled (time_decay_trailing=0.03)`
- **Transaction Friction**: `16.0 bps roundtrip (8.0 bps/leg)`

## Ensemble (Equal-Weight Average)

![Cumulative Equity](artifacts/equity_curve_2026.png)

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 4 (1L/3S) | -0.489 | -0.114 | -0.0064 | -0.0039 | 0.000 | -0.0025 | -1.299 | 0.0193 | 50.0% (L:0.0%, S:66.7%) | 10.2x |
| 500ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.00/S:1.40 (train L:0.80/S:1.20) | 56 | 39 (29L/10S) | -1.101 | 0.094 | -0.0484 | -0.0480 | -3.003 | -0.0004 | -0.050 | 0.0921 | 46.2% (L:41.4%, S:60.0%) | 100.6x |
| 50ETF | Spot ETF | single | 2026-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:0.90/S:1.20 (train L:0.70/S:1.00) | 146 | 31 (14L/17S) | 0.937 | 1.633 | +0.0489 | +0.0145 | 1.733 | +0.0344 | 2.096 | 0.0795 | 54.8% (L:64.3%, S:47.1%) | 80.8x |

<details>
<summary><b>IC Weight (ICW)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 8 (5L/3S) | -1.205 | -0.714 | -0.0186 | -0.0146 | -9.250 | -0.0040 | -2.148 | 0.0323 | 50.0% (L:40.0%, S:66.7%) | 18.3x |
| 500ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:0.90/S:1.30 (train L:0.70/S:1.10) | 56 | 47 (32L/15S) | -1.217 | 0.132 | -0.0586 | -0.0503 | -2.793 | -0.0083 | -0.779 | 0.0991 | 48.9% (L:46.9%, S:53.3%) | 125.6x |
| 50ETF | Spot ETF | single | 2026-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:0.80/S:1.20 (train L:0.60/S:1.00) | 146 | 34 (18L/16S) | 0.754 | 1.524 | +0.0399 | +0.0360 | 3.214 | +0.0039 | 0.254 | 0.0810 | 55.9% (L:66.7%, S:43.8%) | 89.4x |

</details>

<details>
<summary><b>Sortino Weight (tail-IC selection + Score-blend weights)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 8 (5L/3S) | -1.572 | -1.103 | -0.0251 | -0.0226 | -17.837 | -0.0025 | -1.305 | 0.0380 | 37.5% (L:20.0%, S:66.7%) | 16.3x |
| 500ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:0.90/S:1.30 (train L:0.70/S:1.10) | 56 | 48 (32L/16S) | -1.513 | -0.165 | -0.0749 | -0.0509 | -2.832 | -0.0239 | -2.043 | 0.1147 | 47.9% (L:46.9%, S:50.0%) | 129.7x |
| 50ETF | Spot ETF | single | 2026-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:0.80/S:1.10 (train L:0.60/S:0.90) | 146 | 38 (18L/20S) | 0.344 | 1.174 | +0.0192 | +0.0353 | 3.157 | -0.0160 | -0.870 | 0.1016 | 52.6% (L:66.7%, S:40.0%) | 100.5x |

</details>

<details>
<summary><b>Equal Weight (EW, TailIC-selected top-K)</b> (click to expand)</summary>

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.60/S:1.60 (train L:1.40/S:1.40) | 43 | 3 (1L/2S) | -0.964 | -0.658 | -0.0121 | -0.0041 | 0.000 | -0.0080 | -5.555 | 0.0195 | 33.3% (L:0.0%, S:50.0%) | 8.3x |
| 500ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.00/S:1.50 (train L:0.80/S:1.30) | 56 | 37 (29L/8S) | -0.692 | 0.479 | -0.0288 | -0.0306 | -1.969 | +0.0018 | 0.280 | 0.0700 | 51.4% (L:44.8%, S:75.0%) | 92.6x |
| 50ETF | Spot ETF | single | 2026-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2026-01 ~ 2026-07 | L:1.00/S:1.20 (train L:0.80/S:1.00) | 146 | 25 (9L/16S) | 0.471 | 1.075 | +0.0237 | -0.0207 | -3.915 | +0.0444 | 2.779 | 0.0951 | 48.0% (L:44.4%, S:50.0%) | 67.5x |

</details>

---

## Validation (DSR + CPCV)

- **DSR Trials**: `10`
- **CPCV**: `6` splits, `2` test chunks, purge=5

| ETF | Scheme | Sharpe | DSR | Verdict | CPCV Median | CPCV Std | % Positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | ensemble | -0.489 | 0.025 | NOT_SIGNIFICANT | 0.619 | 0.331 | 93% |
| 500ETF | ensemble | -1.101 | 0.009 | NOT_SIGNIFICANT | 1.044 | 0.497 | 100% |
| 159915ETF | ensemble | 0.937 | 0.187 | NOT_SIGNIFICANT | 1.003 | 0.270 | 100% |
| 300ETF | icw | -1.205 | 0.004 | NOT_SIGNIFICANT | 0.535 | 0.339 | 93% |
| 500ETF | icw | -1.217 | 0.007 | NOT_SIGNIFICANT | 0.898 | 0.511 | 100% |
| 159915ETF | icw | 0.754 | 0.151 | NOT_SIGNIFICANT | 1.001 | 0.292 | 100% |
| 300ETF | sortino | -1.572 | 0.002 | NOT_SIGNIFICANT | 0.548 | 0.316 | 93% |
| 500ETF | sortino | -1.513 | 0.004 | NOT_SIGNIFICANT | 0.921 | 0.516 | 100% |
| 159915ETF | sortino | 0.344 | 0.092 | NOT_SIGNIFICANT | 0.948 | 0.263 | 100% |
| 300ETF | ew | -0.964 | 0.008 | NOT_SIGNIFICANT | 0.563 | 0.358 | 87% |
| 500ETF | ew | -0.692 | 0.019 | NOT_SIGNIFICANT | 1.001 | 0.423 | 100% |
| 159915ETF | ew | 0.471 | 0.109 | NOT_SIGNIFICANT | 0.936 | 0.248 | 100% |

