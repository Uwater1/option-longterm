# Option Intraday Stop-Loss A/B Testing Master Report

**Evaluation Period**: OOS [2022-01-01 ~ 2026-07-20] | **Weighting Scheme**: `ICW`

## Executive Summary

This report benchmarks 5 option-tailored intraday stop-loss strategies against the baseline (holding position to 14:35 close) across capital-constrained option portfolios (100k RMB starting capital, 10% capital per trade, nearest OTM contracts).

### 300ETF Performance Comparison

| Strategy Arm | Train Param | OOS Sharpe | Sharpe Lift | Net PnL (RMB) | Max DD (%) | Win Rate (%) | Stop Hit Rate (%) | DSR p-val |
|---|---|---|---|---|---|---|---|---|
| `baseline` | `N/A` | 1.046 | +0.000 | +225,034 | 22.87% | 54.5% | 0.0% | `1.000` |
| `opt_trailing_pct` | `0.3` | **1.173** | **+0.127** | +207,024 | 14.74% | 51.7% | 37.1% | `1.000` |
| `opt_profit_lock_trailing` | `0.2` | 0.869 | -0.177 | +90,064 | 13.56% | 52.2% | 51.7% | `1.000` |
| `opt_time_decay_trailing` | `0.3` | **1.251** | **+0.205** | +187,196 | 11.57% | 48.9% | 64.6% | `1.000` |
| `spot_trailing_pct` | `0.015` | **1.118** | **+0.072** | +222,314 | 22.29% | 53.9% | 13.5% | `1.000` |
| `spot_time_decay_trailing` | `0.012` | **1.188** | **+0.142** | +212,318 | 17.44% | 53.9% | 40.4% | `1.000` |


### 500ETF Performance Comparison

| Strategy Arm | Train Param | OOS Sharpe | Sharpe Lift | Net PnL (RMB) | Max DD (%) | Win Rate (%) | Stop Hit Rate (%) | DSR p-val |
|---|---|---|---|---|---|---|---|---|
| `baseline` | `N/A` | 1.017 | +0.000 | +414,541 | 22.51% | 51.8% | 0.0% | `1.000` |
| `opt_trailing_pct` | `0.2` | 0.616 | -0.401 | +80,202 | 20.53% | 40.6% | 72.2% | `1.000` |
| `opt_profit_lock_trailing` | `0.15` | 0.433 | -0.584 | +53,730 | 19.90% | 54.6% | 57.8% | `1.000` |
| `opt_time_decay_trailing` | `0.25` | 0.646 | -0.371 | +92,454 | 20.15% | 40.6% | 76.7% | `1.000` |
| `spot_trailing_pct` | `0.008` | 0.943 | -0.074 | +257,128 | 20.26% | 46.3% | 50.8% | `1.000` |
| `spot_time_decay_trailing` | `0.008` | 0.948 | -0.070 | +224,556 | 18.71% | 43.1% | 69.6% | `1.000` |


### 159915ETF Performance Comparison

| Strategy Arm | Train Param | OOS Sharpe | Sharpe Lift | Net PnL (RMB) | Max DD (%) | Win Rate (%) | Stop Hit Rate (%) | DSR p-val |
|---|---|---|---|---|---|---|---|---|
| `baseline` | `N/A` | 1.483 | +0.000 | +473,078 | 20.00% | 57.0% | 0.0% | `1.000` |
| `opt_trailing_pct` | `0.2` | **1.518** | **+0.035** | +214,507 | 14.31% | 51.2% | 63.3% | `1.000` |
| `opt_profit_lock_trailing` | `0.15` | 1.433 | -0.049 | +185,666 | 15.63% | 61.4% | 54.6% | `1.000` |
| `opt_time_decay_trailing` | `0.25` | 1.472 | -0.011 | +223,984 | 16.31% | 52.2% | 68.1% | `1.000` |
| `spot_trailing_pct` | `0.008` | **1.543** | **+0.060** | +348,123 | 11.97% | 50.2% | 67.1% | `1.000` |
| `spot_time_decay_trailing` | `0.008` | **1.649** | **+0.166** | +338,752 | 10.94% | 49.8% | 80.7% | `1.000` |


## Cross-ETF Synthesis & Recommendations

| Strategy Arm | Avg Sharpe Lift | Avg Net PnL (RMB) | Avg Max DD (%) | Strategy Recommendation |
|---|---|---|---|---|
| `baseline` | `+0.000` | `+370,884` | `21.79%` | Not Recommended |
| `opt_trailing_pct` | `-0.080` | `+167,244` | `16.53%` | Not Recommended |
| `opt_profit_lock_trailing` | `-0.270` | `+109,820` | `16.36%` | Not Recommended |
| `opt_time_decay_trailing` | `-0.059` | `+167,878` | `16.01%` | Not Recommended |
| `spot_trailing_pct` | `+0.019` | `+275,855` | `18.17%` | Viable |
| `spot_time_decay_trailing` | `+0.079` | `+258,542` | `15.70%` | **Recommended** |