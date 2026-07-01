# Day-Model Remake Optimization Report

This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.

## Out-of-Sample Lockbox Performance (2024-03 to Last Day)

| ETF | Selected Features | Active Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 78 | 72 | `skglm_mcp` | +0.0355 | +0.0330 |
| 50ETF | 79 | 12 | `skglm_mcp` | +0.0351 | +0.1364 |
| 500ETF | 116 | 79 | `skglm_huber_l1` | +0.1444 | +0.1162 |
| 588000ETF | 82 | 39 | `skglm_huber_l1` | +0.0235 | +0.0495 |
| 159915ETF | 113 | 109 | `skglm_mcp` | +0.1366 | +0.1573 |

## Detailed Trial Metrics & Optimization Objectives

| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 1.6426 | +0.2442 | 100.0% | 0.4909 | +55.4952% |
| 50ETF | 0.8165 | +0.1250 | 70.0% | 0.4048 | +16.7836% |
| 500ETF | 1.0557 | +0.2305 | 90.0% | 0.5685 | +85.4510% |
| 588000ETF | 7.6176 | +0.2811 | 100.0% | 0.6848 | +78.9148% |
| 159915ETF | 3.9139 | +0.3223 | 100.0% | 0.5976 | +93.9162% |

## Selected Features per ETF

### 300ETF
- **Total selected features (Stability Selection)**: 78
- **Active features (Non-zero weights)**: 72
- **Active features**: `first_30min_return`, `first_bar_return`, `bar_ret_0`, `bar_ret_2`, `bar_body_rng_0`, `bar_body_rng_1`, `bar_body_rng_2`, `bar_vwap_dev_1`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `num_up_bars`, `max_up_ret`, `max_down_ret`, `cl_pos_in_range`, `total_path_length`, `volume_slope`, `first_bar_sentiment`, `or_fill_ratio`, `close_vs_open_range`, `inside_bar_failure_bull`, `consecutive_higher_highs`, `consecutive_lower_lows`, `early_bearish_engulfing_count`, `volume_concentration`, `volume_trend_intraday`, `volume_acceleration`, `volume_surge_direction`, `rally_ratio`, `range_expansion_ratio`, `pullback_depth_ratio`, `pullback_depth_max`, `rally_strength_max`, `vwap_touch_count`, `volume_weighted_price_position`, `net_volume_flow`, `early_body_momentum`, `open_efficiency`, `late_bar_momentum`, `high_low_sequence_momentum`, `intraday_autocorr`, `opening_momentum_score`, `close_above_open_count`, `open_to_current_return`, `rsi_opening`, `opening_auction_imbalance`, `intraday_close_position`, `margin_balance`, `short_balance`, `short_balance_quantity`, `short_sell_quantity`, `total_balance`, `capital_net_value`, `capital_net_ratio`, `northbound_buy`, `northbound_net`, `vix`, `vix_iv_spread`, `vix_iv_ratio`, `yesterday_gap`, `yesterday_close_position`, `measured_move_proximity`, `yesterday_pm_return`, `yesterday_am_return`, `yesterday_gap_pct`, `yesterday_first_30min_return`, `yesterday_early_trend`, `yesterday_early_momentum`, `yesterday_early_vwap_dev`, `yesterday_day_close_pos`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

### 50ETF
- **Total selected features (Stability Selection)**: 79
- **Active features (Non-zero weights)**: 12
- **Active features**: `first_bar_return`, `bar_vol_2`, `bar_vwap_dev_0`, `consecutive_higher_highs`, `volume_concentration`, `sma100_dist`, `margin_net_buy`, `capital_net_ratio`, `northbound_net`, `yesterday_body_ratio`, `yesterday_gap`, `yesterday_early_trend`

### 500ETF
- **Total selected features (Stability Selection)**: 116
- **Active features (Non-zero weights)**: 79
- **Active features**: `early_trend`, `first_bar_return`, `bar_ret_0`, `bar_rng_0`, `bar_rng_2`, `bar_rng_3`, `bar_rng_5`, `bar_body_rng_0`, `bar_body_rng_1`, `bar_body_rng_2`, `bar_vwap_dev_0`, `bar_vwap_dev_1`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `max_up_ret`, `cl_pos_in_range`, `opening_range_size`, `or_fill_ratio`, `first_bar_body_ratio`, `close_vs_open_range`, `intraday_bullish_fvg`, `consecutive_down_closes`, `consecutive_lower_lows`, `volume_concentration`, `volume_surge_direction`, `pullback_ratio`, `rally_ratio`, `range_expansion_ratio`, `pullback_depth_ratio`, `pullback_depth_max`, `rally_strength_max`, `vwap_slope_intraday`, `vwap_deviation_decision_bar`, `vwap_touch_count`, `volume_weighted_price_position`, `early_body_momentum`, `high_low_sequence_momentum`, `intraday_slope`, `opening_momentum_score`, `opening_range_position`, `session_high_proximity`, `session_low_proximity`, `rsi_opening`, `stoch_opening`, `vwap_reversion_strength`, `momentum_strength_intraday`, `volatility_regime_intraday`, `momentum_divergence`, `intraday_close_position`, `vol20`, `sma100_dist`, `cci14`, `vol5`, `vol_ratio_10_60`, `bb_width`, `margin_balance`, `buy_on_margin_value`, `short_balance_quantity`, `short_repayment_quantity`, `margin_net_buy`, `capital_buy_volume`, `capital_sell_volume`, `northbound_sell`, `northbound_net`, `iv`, `vix`, `vix_vol_ratio`, `volatility_percentile_20d`, `measured_move_proximity`, `yesterday_pm_return`, `yesterday_first_30min_return`, `yesterday_early_realized_vol`, `yesterday_early_trend`, `yesterday_day_range`, `yesterday_day_realized_vol`, `yesterday_day_pm_am_vol_ratio`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

### 588000ETF
- **Total selected features (Stability Selection)**: 82
- **Active features (Non-zero weights)**: 39
- **Active features**: `early_trend`, `early_skew`, `early_kurtosis`, `bar_ret_0`, `bar_body_rng_2`, `bar_vwap_dev_1`, `cl_pos_in_range`, `barbed_wire_intensity`, `consecutive_down_closes`, `consecutive_lower_lows`, `consecutive_bullish_engulfing`, `volume_concentration`, `pullback_ratio`, `rally_ratio`, `pullback_depth_ratio`, `rally_strength_max`, `range_expansion_final_bar`, `vwap_cross_count`, `volume_weighted_price_position`, `intraday_slope`, `opening_range_position`, `session_high_proximity`, `session_low_proximity`, `decision_bar_body`, `upper_shadow_rejection`, `upper_wick_dominance`, `stoch_opening`, `sma20_dist`, `willr14`, `aroon_osc`, `vol60`, `capital_net_value`, `capital_net_ratio`, `vix_iv_spread`, `vix_iv_ratio`, `volatility_percentile_20d`, `volume_percentile_20d`, `yesterday_first_bar_return`, `yesterday_first_bar_volume`

### 159915ETF
- **Total selected features (Stability Selection)**: 113
- **Active features (Non-zero weights)**: 109
- **Active features**: `gap_pct`, `first_30min_return`, `early_realized_vol`, `first_bar_return`, `early_vwap_dev`, `early_kurtosis`, `bar_ret_0`, `bar_ret_1`, `bar_ret_2`, `bar_vol_4`, `bar_vol_5`, `bar_rng_0`, `bar_rng_3`, `bar_body_rng_0`, `bar_vwap_dev_1`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `bar_vwap_dev_5`, `num_up_bars`, `max_up_ret`, `max_down_ret`, `cl_pos_in_range`, `body_to_range_ratio`, `total_path_length`, `volume_slope`, `first_bar_sentiment`, `opening_range_size`, `first_bar_body_ratio`, `close_vs_open_range`, `inside_bar_failure_bull`, `gap_fill_ratio`, `early_doji_count`, `consecutive_higher_highs`, `consecutive_lower_lows`, `consecutive_bullish_engulfing`, `consecutive_bearish_engulfing`, `volume_concentration`, `volume_trend_intraday`, `volume_acceleration`, `volume_surge_direction`, `pullback_ratio`, `rally_ratio`, `pullback_depth_ratio`, `pullback_depth_max`, `rally_strength_max`, `vwap_slope_intraday`, `vwap_deviation_decision_bar`, `volume_weighted_price_position`, `net_volume_flow`, `early_body_momentum`, `open_efficiency`, `late_bar_momentum`, `trend_strength_intraday`, `high_low_sequence_momentum`, `opening_momentum_score`, `trend_exhaustion_early`, `opening_range_position`, `session_high_proximity`, `session_low_proximity`, `close_above_open_count`, `open_to_current_return`, `upper_wick_dominance`, `rsi_opening`, `stoch_opening`, `vwap_reversion_strength`, `momentum_strength_intraday`, `volatility_regime_intraday`, `momentum_divergence`, `opening_auction_imbalance`, `macd_hist`, `sma20_dist`, `atr14_norm`, `bb_pctb`, `vol20`, `roc20`, `cci14`, `mfi14`, `aroon_osc`, `vol10`, `vol60`, `bb_width`, `vol_pk20`, `vol_gk10`, `vol_gk20`, `margin_net_buy`, `capital_net_value`, `capital_net_ratio`, `northbound_net`, `iv_vol_ratio`, `vix_vol_ratio`, `vix_iv_spread`, `vix_iv_ratio`, `vix_diff_1d`, `yesterday_gap`, `yesterday_close_position`, `volatility_percentile_20d`, `measured_move_proximity`, `yesterday_pm_return`, `yesterday_am_return`, `yesterday_gap_pct`, `yesterday_first_30min_return`, `yesterday_early_trend`, `yesterday_early_momentum`, `yesterday_early_vwap_dev`, `yesterday_day_realized_vol`, `yesterday_day_close_pos`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_opening_gap_reversal`

## Methodology Overview
1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).
2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.
3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.
4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.
5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.
6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).