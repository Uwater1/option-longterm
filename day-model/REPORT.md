# Day-Model Remake Optimization Report

This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.

## Out-of-Sample Lockbox Performance (2024-03 to Last Day)

| ETF | Selected Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |
| :--- | :---: | :---: | :---: | :---: |
| 300ETF | 14 | `skglm_mcp` | +0.0169 | -0.0143 |
| 50ETF | 17 | `skglm_mcp` | +0.0041 | +0.0469 |
| 500ETF | 17 | `skglm_huber_l1` | +0.1338 | +0.0271 |
| 588000ETF | 11 | `skglm_mcp` | +0.0777 | +0.1236 |
| 159915ETF | 21 | `skglm_mcp` | +0.1406 | +0.2781 |

## Detailed Trial Metrics & Optimization Objectives

| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 1.1795 | +0.1870 | 80.0% | 0.4085 | +35.8259% |
| 50ETF | 1.4612 | +0.2032 | 90.0% | 0.4121 | +34.8819% |
| 500ETF | 2.8625 | +0.3232 | 100.0% | 0.4473 | +82.3453% |
| 588000ETF | 13.6757 | +0.3281 | 100.0% | 0.6576 | +57.3877% |
| 159915ETF | 1.5412 | +0.2885 | 90.0% | 0.6097 | +89.9731% |

## Selected Features per ETF

### 300ETF
- **Total selected features**: 14
- **Features**: `bar_body_rng_0`, `max_down_ret`, `early_bearish_engulfing_count`, `volume_concentration`, `volume_weighted_price_position`, `net_volume_flow`, `intraday_autocorr`, `short_balance_quantity`, `capital_net_value`, `northbound_net`, `vix`, `vix_iv_ratio`, `yesterday_day_vwap_dev`, `yesterday_intraday_close_position`

### 50ETF
- **Total selected features**: 17
- **Features**: `bar_vwap_dev_0`, `max_down_ret`, `volume_slope`, `consecutive_higher_highs`, `volume_weighted_price_position`, `sma100_dist`, `buy_on_margin_value`, `margin_net_buy`, `capital_buy_volume`, `capital_net_value`, `northbound_net`, `vix_iv_ratio`, `vix_diff_1d`, `yesterday_body_ratio`, `measured_move_proximity`, `yesterday_day_vwap_dev`, `yesterday_intraday_close_position`

### 500ETF
- **Total selected features**: 17
- **Features**: `bar_vwap_dev_2`, `max_up_ret`, `max_down_ret`, `body_to_range_ratio`, `range_expansion_ratio`, `rally_strength_max`, `vwap_touch_count`, `net_volume_flow`, `late_bar_momentum`, `sma100_dist`, `vol_ratio_10_60`, `margin_balance`, `capital_sell_volume`, `iv`, `yesterday_day_close_pos`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

### 588000ETF
- **Total selected features**: 11
- **Features**: `first_30min_return`, `bar_vwap_dev_1`, `bar_vwap_dev_2`, `volume_acceleration`, `range_expansion_final_bar`, `volume_weighted_price_position`, `upper_wick_dominance`, `capital_net_ratio`, `vix_iv_ratio`, `volatility_percentile_20d`, `yesterday_day_kurtosis`

### 159915ETF
- **Total selected features**: 21
- **Features**: `gap_pct`, `early_range`, `first_bar_return`, `early_kurtosis`, `bar_vol_5`, `max_down_ret`, `body_to_range_ratio`, `close_vs_open_range`, `inside_bar_failure_bull`, `consecutive_bearish_engulfing`, `volume_trend_intraday`, `late_bar_momentum`, `roc20`, `margin_net_buy`, `capital_net_ratio`, `vix_iv_ratio`, `yesterday_gap`, `yesterday_pm_return`, `yesterday_early_momentum`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

## Methodology Overview
1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).
2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.
3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.
4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.
5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.
6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).