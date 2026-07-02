# Day-Model Remake Optimization Report

This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.

## Out-of-Sample Lockbox Performance (2024-03 to Last Day)

| ETF | Selected Features | Active Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 30 | 30 | `skglm_mcp` | +0.0644 | +0.1145 |
| 50ETF | 38 | 31 | `skglm_huber_l1` | +0.0594 | +0.2816 |
| 500ETF | 13 | 13 | `skglm_huber_l1` | +0.1204 | +0.0706 |
| 588000ETF | 23 | 23 | `skglm_mcp` | -0.0068 | -0.0014 |
| 159915ETF | 15 | 15 | `skglm_huber_l1` | +0.1116 | +0.2919 |

## Detailed Trial Metrics & Optimization Objectives

| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 1.4080 | +0.1976 | 90.0% | 0.4873 | +43.2056% |
| 50ETF | 1.4749 | +0.2201 | 90.0% | 0.4497 | +40.4463% |
| 500ETF | 1.9575 | +0.2873 | 100.0% | 0.5382 | +95.0710% |
| 588000ETF | 3.2615 | +0.3175 | 100.0% | 0.6636 | +81.6407% |
| 159915ETF | 3.0478 | +0.3206 | 100.0% | 0.6182 | +101.5367% |

## Selected Features per ETF

### 300ETF
- **Total selected features (Stability Selection)**: 30
- **Active features (Non-zero weights)**: 30
- **Active features**: `first_30min_return`, `first_bar_return`, `bar_ret_0`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `inside_bar_failure_bull`, `consecutive_higher_highs`, `consecutive_lower_lows`, `early_bearish_engulfing_count`, `pullback_depth_max`, `rally_strength_max`, `vwap_touch_count`, `volume_weighted_price_position`, `intraday_autocorr`, `open_to_current_return`, `margin_balance`, `short_sell_quantity`, `capital_net_ratio`, `northbound_net`, `vix`, `vix_iv_spread`, `yesterday_close_position`, `yesterday_pm_return`, `yesterday_am_return`, `yesterday_early_trend`, `yesterday_early_vwap_dev`, `yesterday_day_close_pos`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

![300ETF Diagnostics](plots/diagnostics_300ETF.png)

### 50ETF
- **Total selected features (Stability Selection)**: 38
- **Active features (Non-zero weights)**: 31
- **Active features**: `first_30min_return`, `first_bar_return`, `bar_ret_0`, `bar_rng_4`, `bar_vwap_dev_0`, `num_up_bars`, `first_bar_sentiment`, `consecutive_higher_highs`, `volume_surge_max`, `volume_surge_direction`, `late_bar_momentum`, `trend_strength_intraday`, `close_above_open_count`, `open_to_current_return`, `opening_auction_imbalance`, `sma100_dist`, `stoch_d`, `buy_on_margin_value`, `margin_net_buy`, `capital_buy_volume`, `capital_net_value`, `capital_net_ratio`, `northbound_net`, `iv`, `vix_iv_spread`, `vix_iv_ratio`, `vix_diff_1d`, `yesterday_body_ratio`, `measured_move_proximity`, `yesterday_early_vwap_dev`, `yesterday_intraday_close_position`

![50ETF Diagnostics](plots/diagnostics_50ETF.png)

### 500ETF
- **Total selected features (Stability Selection)**: 13
- **Active features (Non-zero weights)**: 13
- **Active features**: `bar_ret_0`, `bar_rng_0`, `bar_rng_3`, `bar_vwap_dev_0`, `bar_vwap_dev_2`, `max_up_ret`, `volume_surge_direction`, `sma100_dist`, `northbound_net`, `yesterday_early_trend`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

![500ETF Diagnostics](plots/diagnostics_500ETF.png)

### 588000ETF
- **Total selected features (Stability Selection)**: 23
- **Active features (Non-zero weights)**: 23
- **Active features**: `early_skew`, `early_kurtosis`, `bar_body_rng_2`, `barbed_wire_intensity`, `consecutive_bullish_engulfing`, `volume_concentration`, `volume_acceleration`, `range_expansion_final_bar`, `volume_weighted_price_position`, `late_bar_momentum`, `decision_bar_body`, `upper_shadow_rejection`, `upper_wick_dominance`, `sma20_dist`, `vol60`, `capital_net_ratio`, `vix_iv_spread`, `volatility_percentile_20d`, `volume_percentile_20d`, `yesterday_first_bar_return`, `yesterday_first_bar_volume`, `yesterday_day_late_mom`, `yesterday_day_kurtosis`

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