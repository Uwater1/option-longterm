# Day-Model Remake Optimization Report

This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.

## Out-of-Sample Lockbox Performance (2024-03 to Last Day)

| ETF | Selected Features | Active Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 30 | 30 | `skglm_mcp` | +0.0622 | +0.1151 |
| 50ETF | 31 | 31 | `skglm_huber_l1` | +0.0080 | +0.1588 |
| 500ETF | 13 | 13 | `skglm_mcp` | +0.1153 | +0.0679 |
| 588000ETF | 22 | 22 | `skglm_mcp` | +0.0150 | +0.0164 |
| 159915ETF | 15 | 15 | `skglm_mcp` | +0.1085 | +0.2631 |

## Detailed Trial Metrics & Optimization Objectives

| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 1.4238 | +0.1995 | 100.0% | 0.3976 | +42.8162% |
| 50ETF | 1.6018 | +0.2314 | 90.0% | 0.4376 | +34.2737% |
| 500ETF | 1.9777 | +0.2898 | 100.0% | 0.5636 | +88.7673% |
| 588000ETF | 4.6823 | +0.3319 | 100.0% | 0.7030 | +112.8968% |
| 159915ETF | 2.9028 | +0.3305 | 100.0% | 0.6012 | +97.3393% |

## Model Quality & Generalization Diagnostics

### Model Multi-Collinearity & Weight Concentration

| ETF | Condition Number ($\kappa$) | Collinear Pairs ($\ge 0.85$) | Gini (Weight Concentration) | Tail Weight ESS | Tail Weight ESS % |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 523664.94 [SEVERE] | 4 [WARNING] | 0.3546 | 1077.9 | 49.8% |
| 50ETF | 6422142.50 [SEVERE] | 3 [WARNING] | 0.3218 | 1646.1 | 76.0% |
| 500ETF | 3675897.75 [SEVERE] | 0 | 0.3747 | 2030.8 | 93.8% |
| 588000ETF | 8.76 | 1 [WARNING] | 0.2959 | 700.4 | 94.9% |
| 159915ETF | 964.82 [SEVERE] | 2 [WARNING] | 0.2401 | 359.0 | 16.6% [LOW] |

### Generalization Gap (CV vs Out-of-Sample)

| ETF | CV Overall IC | OOS Lockbox IC | IC Gen Gap | CV Monotonicity | OOS Monotonicity | Mono Gen Gap |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 300ETF | +0.1033 | +0.0622 | +0.0411 | +0.3976 | +0.6727 | -0.2752 |
| 50ETF | +0.1059 | +0.0080 | +0.0978 [OVERFIT] | +0.4376 | +0.4303 | +0.0073 |
| 500ETF | +0.1520 | +0.1153 | +0.0367 | +0.5636 | +0.9152 | -0.3515 |
| 588000ETF | +0.1955 | +0.0150 | +0.1805 [OVERFIT] | +0.7030 | +0.3333 | +0.3697 [DEGRADED] |
| 159915ETF | +0.1817 | +0.1085 | +0.0732 [OVERFIT] | +0.6012 | +0.6848 | -0.0836 |

### Feature Selection Metrics & Fallbacks

| ETF | Screening Input | BH-FDR Pass | Screen Fallback? | Stability Input | Stability Pass | Stability Fallback? | Kept Features |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 238 | 63 | NO | 63 | 30 | NO | **30** |
| 50ETF | 238 | 8 | YES [WARNING] | 50 | 31 | NO | **31** |
| 500ETF | 238 | 115 | NO | 115 | 13 | NO | **13** |
| 588000ETF | 238 | 85 | NO | 85 | 22 | NO | **22** |
| 159915ETF | 238 | 114 | NO | 114 | 15 | NO | **15** |

### Optuna Main Study & Pruning Reasons

| ETF | Total Trials | Completed | Pruned / Failed | M4 Pruned | M3 Pruned | M5 Pruned | M6 Pruned |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 50 | 34 | 16 | 14 | 14 | 16 | 14 |
| 50ETF | 50 | 40 | 10 | 7 | 7 | 10 | 7 |
| 500ETF | 50 | 44 | 6 | 6 | 6 | 6 | 6 |
| 588000ETF | 50 | 45 | 5 | 4 | 5 | 4 | 4 |
| 159915ETF | 50 | 42 | 8 | 8 | 8 | 8 | 8 |

## Selected Features per ETF

### 300ETF
- **Total selected features (Stability Selection)**: 30
- **Active features (Non-zero weights)**: 30
- **Active features**: `first_30min_return`, `first_bar_return`, `bar_ret_0`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `inside_bar_failure_bull`, `consecutive_higher_highs`, `consecutive_lower_lows`, `early_bearish_engulfing_count`, `pullback_depth_max`, `rally_strength_max`, `vwap_touch_count`, `volume_weighted_price_position`, `intraday_autocorr`, `open_to_current_return`, `margin_balance`, `short_sell_quantity`, `capital_net_ratio`, `northbound_net`, `vix`, `vix_iv_spread`, `yesterday_close_position`, `yesterday_pm_return`, `yesterday_am_return`, `yesterday_early_trend`, `yesterday_early_vwap_dev`, `yesterday_day_close_pos`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

![300ETF Diagnostics](plots/diagnostics_300ETF.png)

### 50ETF
- **Total selected features (Stability Selection)**: 31
- **Active features (Non-zero weights)**: 31
- **Active features**: `first_30min_return`, `first_bar_return`, `bar_ret_0`, `bar_rng_4`, `bar_vwap_dev_0`, `first_bar_sentiment`, `consecutive_higher_highs`, `volume_concentration`, `volume_surge_direction`, `rally_strength_max`, `volume_weighted_price_position`, `late_bar_momentum`, `open_to_current_return`, `sma20_dist`, `sma100_dist`, `roc20`, `buy_on_margin_value`, `margin_net_buy`, `capital_buy_value`, `capital_net_ratio`, `northbound_net`, `iv`, `iv_vol_ratio`, `vix_iv_spread`, `vix_iv_ratio`, `vix_diff_1d`, `yesterday_body_ratio`, `measured_move_proximity`, `yesterday_early_vwap_dev`, `yesterday_day_vwap_dev`, `yesterday_intraday_close_position`

![50ETF Diagnostics](plots/diagnostics_50ETF.png)

### 500ETF
- **Total selected features (Stability Selection)**: 13
- **Active features (Non-zero weights)**: 13
- **Active features**: `bar_ret_0`, `bar_rng_0`, `bar_rng_3`, `bar_vwap_dev_0`, `bar_vwap_dev_2`, `max_up_ret`, `volume_surge_direction`, `sma100_dist`, `northbound_net`, `yesterday_early_trend`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

![500ETF Diagnostics](plots/diagnostics_500ETF.png)

### 588000ETF
- **Total selected features (Stability Selection)**: 22
- **Active features (Non-zero weights)**: 22
- **Active features**: `early_skew`, `early_kurtosis`, `bar_body_rng_2`, `barbed_wire_intensity`, `consecutive_bullish_engulfing`, `volume_concentration`, `volume_acceleration`, `range_expansion_final_bar`, `volume_weighted_price_position`, `late_bar_momentum`, `decision_bar_body`, `upper_shadow_rejection`, `upper_wick_dominance`, `sma20_dist`, `vol60`, `capital_net_ratio`, `vix_iv_spread`, `volatility_percentile_20d`, `volume_percentile_20d`, `yesterday_first_bar_return`, `yesterday_first_bar_volume`, `yesterday_day_kurtosis`

![588000ETF Diagnostics](plots/diagnostics_588000ETF.png)

### 159915ETF
- **Total selected features (Stability Selection)**: 15
- **Active features (Non-zero weights)**: 15
- **Active features**: `gap_pct`, `first_bar_return`, `early_kurtosis`, `bar_ret_0`, `bar_vol_5`, `max_up_ret`, `inside_bar_failure_bull`, `gap_fill_ratio`, `margin_net_buy`, `northbound_net`, `yesterday_gap`, `yesterday_gap_pct`, `yesterday_early_vwap_dev`, `yesterday_day_vwap_dev`, `yesterday_opening_gap_reversal`

![159915ETF Diagnostics](plots/diagnostics_159915ETF.png)

## Methodology Overview
1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).
2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.
3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.
4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.
5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.
6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).