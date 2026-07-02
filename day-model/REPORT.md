# Day-Model Remake Optimization Report

This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.

## Out-of-Sample Lockbox Performance (2024-03 to Last Day)

| ETF | Selected Features | Active Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 78 | 3 | `skglm_mcp` | -0.0097 | +0.0328 |
| 50ETF | 79 | 26 | `skglm_mcp` | +0.0461 | +0.0881 |
| 500ETF | 116 | 1 | `skglm_huber_l1` | +0.0792 | +0.0273 |
| 588000ETF | 82 | 21 | `skglm_mcp` | +0.0296 | -0.0239 |
| 159915ETF | 113 | 9 | `skglm_mcp` | +0.1488 | +0.2065 |

## Detailed Trial Metrics & Optimization Objectives

| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 0.8613 | +0.1594 | 70.0% | 0.4315 | +44.2767% |
| 50ETF | 1.4417 | +0.2101 | 90.0% | 0.3103 | +39.0613% |
| 500ETF | 1.7790 | +0.2333 | 90.0% | 0.4497 | +58.5152% |
| 588000ETF | 5.0543 | +0.2970 | 100.0% | 0.4939 | +107.1350% |
| 159915ETF | 1.0953 | +0.1943 | 80.0% | 0.5636 | +74.9584% |

## Selected Features per ETF

### 300ETF
- **Total selected features (Stability Selection)**: 78
- **Active features (Non-zero weights)**: 3
- **Active features**: `first_bar_return`, `yesterday_am_return`, `yesterday_early_trend`

![300ETF Diagnostics](plots/diagnostics_300ETF.png)

### 50ETF
- **Total selected features (Stability Selection)**: 79
- **Active features (Non-zero weights)**: 26
- **Active features**: `first_30min_return`, `first_bar_return`, `bar_vol_2`, `bar_rng_4`, `bar_vwap_dev_0`, `bar_vwap_dev_2`, `first_bar_sentiment`, `intraday_bullish_fvg`, `gap_fill_ratio`, `shark_32_signal`, `consecutive_higher_highs`, `consecutive_lower_lows`, `macd_hist`, `sma100_dist`, `rsi21`, `buy_on_margin_value`, `margin_net_buy`, `capital_sell_value`, `capital_net_ratio`, `northbound_net`, `iv`, `vix_diff_1d`, `yesterday_body_ratio`, `yesterday_close_position`, `measured_move_proximity`, `yesterday_early_trend`

![50ETF Diagnostics](plots/diagnostics_50ETF.png)

### 500ETF
- **Total selected features (Stability Selection)**: 116
- **Active features (Non-zero weights)**: 1
- **Active features**: `max_up_ret`

![500ETF Diagnostics](plots/diagnostics_500ETF.png)

### 588000ETF
- **Total selected features (Stability Selection)**: 82
- **Active features (Non-zero weights)**: 21
- **Active features**: `early_skew`, `early_kurtosis`, `bar_body_rng_2`, `max_up_ret`, `barbed_wire_intensity`, `volume_concentration`, `range_expansion_final_bar`, `volume_weighted_price_position`, `late_bar_momentum`, `decision_bar_body`, `upper_shadow_rejection`, `upper_wick_dominance`, `sma20_dist`, `aroon_osc`, `vol60`, `capital_net_ratio`, `vix_iv_spread`, `volatility_percentile_20d`, `volume_percentile_20d`, `yesterday_first_bar_return`, `yesterday_first_bar_volume`

![588000ETF Diagnostics](plots/diagnostics_588000ETF.png)

### 159915ETF
- **Total selected features (Stability Selection)**: 113
- **Active features (Non-zero weights)**: 9
- **Active features**: `gap_pct`, `first_bar_return`, `early_kurtosis`, `bar_vol_5`, `inside_bar_failure_bull`, `vol10`, `yesterday_gap_pct`, `yesterday_early_vwap_dev`, `yesterday_day_vwap_dev`

![159915ETF Diagnostics](plots/diagnostics_159915ETF.png)

## Methodology Overview
1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).
2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.
3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.
4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.
5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.
6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).