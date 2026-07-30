# Intraday Stop-Loss Research Report (NewTrade Framework)

## Executive Summary

This report investigates whether intraday stop-loss methods (Fixed, Today High/Low Anchor, Trailing Peak/Trough, Volatility ATR, Time-Decay Trailing) improve factor monetization returns.

**Strict Out-of-Sample Integrity Guardrail**:
- **Train Period (2010 – 2021-12-31)**: All stop-loss threshold parameters were swept and optimized exclusively on training data.
- **OOS Period (2022-01-01 – 2026-07-20)**: Evaluated **strictly once (single-pass)** using Train-locked parameters.
- **Friction**: Standard 8 bps position state transition + 2 bps execution slippage on stop-loss triggers.

## Overall Benchmark Matrix (OOS 2022–2026)

| ETF | Scheme | Method | Train Param | OOS Sharpe | Baseline Sharpe | Sharpe Lift | OOS PnL | Baseline PnL | OOS MaxDD | Stop Trigger Rate (%) | DSR p-value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 300ETF | ICW | `baseline` | 0.0 | 0.783 | 0.783 | **+0.000** | 0.1836 | 0.1836 | 0.0478 | 0.0% | 1.0000 |
| 300ETF | ICW | `fixed_pct` | 0.05 | 0.783 | 0.783 | **+0.000** | 0.1836 | 0.1836 | 0.0478 | 0.0% | 1.0000 |
| 300ETF | ICW | `early_high_low` | 0.01 | 0.605 | 0.783 | **-0.178** | 0.0940 | 0.1836 | 0.0439 | 32.7% | 1.0000 |
| 300ETF | ICW | `trailing_pct` | 0.012 | 0.551 | 0.783 | **-0.232** | 0.1114 | 0.1836 | 0.0732 | 26.0% | 1.0000 |
| 300ETF | ICW | `vol_atr` | 7.0 | 0.880 | 0.783 | **+0.097** | 0.1901 | 0.1836 | 0.0455 | 35.6% | 1.0000 |
| 300ETF | ICW | `time_decay_trailing` | 0.012 | 0.537 | 0.783 | **-0.246** | 0.1005 | 0.1836 | 0.0720 | 45.2% | 1.0000 |
| 300ETF | EW | `baseline` | 0.0 | 0.925 | 0.925 | **+0.000** | 0.2402 | 0.2402 | 0.0643 | 0.0% | 1.0000 |
| 300ETF | EW | `fixed_pct` | 0.05 | 0.925 | 0.925 | **+0.000** | 0.2402 | 0.2402 | 0.0643 | 0.0% | 1.0000 |
| 300ETF | EW | `early_high_low` | 0.01 | 0.710 | 0.925 | **-0.215** | 0.1304 | 0.2402 | 0.0478 | 27.3% | 1.0000 |
| 300ETF | EW | `trailing_pct` | 0.012 | 0.689 | 0.925 | **-0.236** | 0.1541 | 0.2402 | 0.0720 | 23.3% | 1.0000 |
| 300ETF | EW | `vol_atr` | 7.0 | 1.012 | 0.925 | **+0.087** | 0.2406 | 0.2402 | 0.0480 | 37.3% | 1.0000 |
| 300ETF | EW | `time_decay_trailing` | 0.012 | 0.759 | 0.925 | **-0.166** | 0.1582 | 0.2402 | 0.0657 | 38.7% | 1.0000 |
| 500ETF | ICW | `baseline` | 0.0 | 0.595 | 0.595 | **+0.000** | 0.2605 | 0.2605 | 0.1369 | 0.0% | 1.0000 |
| 500ETF | ICW | `fixed_pct` | 0.05 | 0.523 | 0.595 | **-0.072** | 0.2345 | 0.2605 | 0.1369 | 0.3% | 1.0000 |
| 500ETF | ICW | `early_high_low` | 0.04 | 0.474 | 0.595 | **-0.121** | 0.1990 | 0.2605 | 0.1369 | 1.1% | 1.0000 |
| 500ETF | ICW | `trailing_pct` | 0.035 | 0.637 | 0.595 | **+0.042** | 0.2716 | 0.2605 | 0.1333 | 2.5% | 1.0000 |
| 500ETF | ICW | `vol_atr` | 7.0 | 0.401 | 0.595 | **-0.194** | 0.1597 | 0.2605 | 0.1171 | 37.9% | 1.0000 |
| 500ETF | ICW | `time_decay_trailing` | 0.03 | 0.755 | 0.595 | **+0.160** | 0.3171 | 0.2605 | 0.1330 | 8.8% | 1.0000 |
| 500ETF | EW | `baseline` | 0.0 | 0.954 | 0.954 | **+0.000** | 0.3754 | 0.3754 | 0.0991 | 0.0% | 1.0000 |
| 500ETF | EW | `fixed_pct` | 0.04 | 0.900 | 0.954 | **-0.054** | 0.3594 | 0.3754 | 0.0991 | 0.4% | 1.0000 |
| 500ETF | EW | `early_high_low` | 0.04 | 0.777 | 0.954 | **-0.177** | 0.2937 | 0.3754 | 0.0991 | 1.1% | 1.0000 |
| 500ETF | EW | `trailing_pct` | 0.035 | 1.006 | 0.954 | **+0.052** | 0.3834 | 0.3754 | 0.0947 | 2.5% | 1.0000 |
| 500ETF | EW | `vol_atr` | 7.0 | 0.564 | 0.954 | **-0.390** | 0.2089 | 0.3754 | 0.0859 | 36.3% | 1.0000 |
| 500ETF | EW | `time_decay_trailing` | 0.03 | 1.027 | 0.954 | **+0.073** | 0.3893 | 0.3754 | 0.0848 | 8.3% | 1.0000 |
| 159915ETF | ICW | `baseline` | 0.0 | 1.389 | 1.389 | **+0.000** | 0.7174 | 0.7174 | 0.1207 | 0.0% | 1.0000 |
| 159915ETF | ICW | `fixed_pct` | 0.05 | 1.389 | 1.389 | **+0.000** | 0.7174 | 0.7174 | 0.1207 | 0.0% | 1.0000 |
| 159915ETF | ICW | `early_high_low` | 0.04 | 1.395 | 1.389 | **+0.006** | 0.7010 | 0.7174 | 0.1113 | 1.3% | 1.0000 |
| 159915ETF | ICW | `trailing_pct` | 0.03 | 1.432 | 1.389 | **+0.043** | 0.7186 | 0.7174 | 0.1079 | 5.1% | 1.0000 |
| 159915ETF | ICW | `vol_atr` | 7.0 | 1.351 | 1.389 | **-0.038** | 0.6357 | 0.7174 | 0.1094 | 29.7% | 1.0000 |
| 159915ETF | ICW | `time_decay_trailing` | 0.025 | 1.540 | 1.389 | **+0.151** | 0.7764 | 0.7174 | 0.1045 | 18.5% | 1.0000 |
| 159915ETF | EW | `baseline` | 0.0 | 1.488 | 1.488 | **+0.000** | 0.7808 | 0.7808 | 0.1053 | 0.0% | 1.0000 |
| 159915ETF | EW | `fixed_pct` | 0.025 | 1.604 | 1.488 | **+0.116** | 0.8194 | 0.7808 | 0.1002 | 3.8% | 1.0000 |
| 159915ETF | EW | `early_high_low` | 0.04 | 1.496 | 1.488 | **+0.008** | 0.7644 | 0.7808 | 0.1053 | 1.2% | 1.0000 |
| 159915ETF | EW | `trailing_pct` | 0.03 | 1.611 | 1.488 | **+0.123** | 0.8217 | 0.7808 | 0.1019 | 5.0% | 1.0000 |
| 159915ETF | EW | `vol_atr` | 7.0 | 1.478 | 1.488 | **-0.010** | 0.7041 | 0.7808 | 0.1165 | 29.4% | 1.0000 |
| 159915ETF | EW | `time_decay_trailing` | 0.025 | 1.672 | 1.488 | **+0.184** | 0.8564 | 0.7808 | 0.1051 | 17.8% | 1.0000 |

## Per-ETF Findings & Analysis

### 300ETF (ICW)

| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |
|---|---|---|---|---|---|---|---|
| `baseline` | 0.0 | 1.127 | 0.783 | 0.1836 | 0.0478 | 57.7% | 0.0% |
| `fixed_pct` | 0.05 | 1.127 | 0.783 | 0.1836 | 0.0478 | 57.7% | 0.0% |
| `early_high_low` | 0.01 | 0.974 | 0.605 | 0.0940 | 0.0439 | 48.1% | 32.7% |
| `trailing_pct` | 0.012 | 1.056 | 0.551 | 0.1114 | 0.0732 | 53.8% | 26.0% |
| `vol_atr` | 7.0 | 0.861 | 0.880 | 0.1901 | 0.0455 | 52.9% | 35.6% |
| `time_decay_trailing` | 0.012 | 1.105 | 0.537 | 0.1005 | 0.0720 | 51.9% | 45.2% |


### 300ETF (EW)

| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |
|---|---|---|---|---|---|---|---|
| `baseline` | 0.0 | 1.189 | 0.925 | 0.2402 | 0.0643 | 58.0% | 0.0% |
| `fixed_pct` | 0.05 | 1.176 | 0.925 | 0.2402 | 0.0643 | 58.0% | 0.0% |
| `early_high_low` | 0.01 | 1.033 | 0.710 | 0.1304 | 0.0478 | 50.0% | 27.3% |
| `trailing_pct` | 0.012 | 1.071 | 0.689 | 0.1541 | 0.0720 | 55.3% | 23.3% |
| `vol_atr` | 7.0 | 0.871 | 1.012 | 0.2406 | 0.0480 | 50.7% | 37.3% |
| `time_decay_trailing` | 0.012 | 1.144 | 0.759 | 0.1582 | 0.0657 | 54.7% | 38.7% |


### 500ETF (ICW)

| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |
|---|---|---|---|---|---|---|---|
| `baseline` | 0.0 | 1.683 | 0.595 | 0.2605 | 0.1369 | 54.5% | 0.0% |
| `fixed_pct` | 0.05 | 1.572 | 0.523 | 0.2345 | 0.1369 | 54.5% | 0.3% |
| `early_high_low` | 0.04 | 1.375 | 0.474 | 0.1990 | 0.1369 | 54.2% | 1.1% |
| `trailing_pct` | 0.035 | 1.491 | 0.637 | 0.2716 | 0.1333 | 54.8% | 2.5% |
| `vol_atr` | 7.0 | 1.326 | 0.401 | 0.1597 | 0.1171 | 49.2% | 37.9% |
| `time_decay_trailing` | 0.03 | 1.380 | 0.755 | 0.3171 | 0.1330 | 54.2% | 8.8% |


### 500ETF (EW)

| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |
|---|---|---|---|---|---|---|---|
| `baseline` | 0.0 | 1.651 | 0.954 | 0.3754 | 0.0991 | 55.8% | 0.0% |
| `fixed_pct` | 0.04 | 1.573 | 0.900 | 0.3594 | 0.0991 | 55.8% | 0.4% |
| `early_high_low` | 0.04 | 1.365 | 0.777 | 0.2937 | 0.0991 | 55.4% | 1.1% |
| `trailing_pct` | 0.035 | 1.488 | 1.006 | 0.3834 | 0.0947 | 56.1% | 2.5% |
| `vol_atr` | 7.0 | 1.330 | 0.564 | 0.2089 | 0.0859 | 50.0% | 36.3% |
| `time_decay_trailing` | 0.03 | 1.415 | 1.027 | 0.3893 | 0.0848 | 55.4% | 8.3% |


### 159915ETF (ICW)

| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |
|---|---|---|---|---|---|---|---|
| `baseline` | 0.0 | 1.762 | 1.389 | 0.7174 | 0.1207 | 58.5% | 0.0% |
| `fixed_pct` | 0.05 | 1.538 | 1.389 | 0.7174 | 0.1207 | 58.5% | 0.0% |
| `early_high_low` | 0.04 | 1.452 | 1.395 | 0.7010 | 0.1113 | 58.1% | 1.3% |
| `trailing_pct` | 0.03 | 1.641 | 1.432 | 0.7186 | 0.1079 | 58.5% | 5.1% |
| `vol_atr` | 7.0 | 1.380 | 1.351 | 0.6357 | 0.1094 | 55.3% | 29.7% |
| `time_decay_trailing` | 0.025 | 1.581 | 1.540 | 0.7764 | 0.1045 | 58.1% | 18.5% |


### 159915ETF (EW)

| Method | Train Param | Train Sharpe | OOS Sharpe | OOS PnL | OOS MaxDD | OOS WinRate (%) | Stop Trigger Rate (%) |
|---|---|---|---|---|---|---|---|
| `baseline` | 0.0 | 1.688 | 1.488 | 0.7808 | 0.1053 | 59.4% | 0.0% |
| `fixed_pct` | 0.025 | 1.459 | 1.604 | 0.8194 | 0.1002 | 59.4% | 3.8% |
| `early_high_low` | 0.04 | 1.397 | 1.496 | 0.7644 | 0.1053 | 59.1% | 1.2% |
| `trailing_pct` | 0.03 | 1.579 | 1.611 | 0.8217 | 0.1019 | 59.7% | 5.0% |
| `vol_atr` | 7.0 | 1.300 | 1.478 | 0.7041 | 0.1165 | 56.2% | 29.4% |
| `time_decay_trailing` | 0.025 | 1.528 | 1.672 | 0.8564 | 0.1051 | 59.1% | 17.8% |


## Core Research Conclusions & Production Recommendation

- **Average Sharpe Lift across all methods/ETFs**: `-0.040`
- **Positive Sharpe Lift Ratio**: `13/30` (`43.3%`)

> [!CAUTION]
> **CONCLUSION: Stop-loss degrades overall performance in NewTrade intraday monetization.**
> Intraday factor monetization trades operate on noisy 10:00-14:35 mean-reverting and trending micro-structure. Setting intraday stop-losses repeatedly cuts trades near local intraday extremes before full-day signal convergence, incurring fee friction and whipsaw losses.
> **RECOMMENDATION**: Keep baseline mode (hold position until 14:35) without intraday stop-loss.