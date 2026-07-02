# Day-Model Remake Optimization Report

This report summarizes the performance and features of the remade `day-model` return predictors, optimized using first-principles multi-metric objective functions and stability selection.

## Out-of-Sample Lockbox Performance (2024-03 to Last Day)

| ETF | Selected Features | Active Features | Best Model Type | Lockbox Overall IC | Lockbox Tail IC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 78 | 54 | `skglm_mcp` | +0.0519 | +0.0940 |
| 50ETF | 79 | 25 | `skglm_mcp` | +0.0265 | +0.1151 |
| 500ETF | 116 | 21 | `skglm_huber_l1` | +0.1224 | +0.0571 |
| 588000ETF | 82 | 25 | `skglm_huber_l1` | +0.0361 | -0.0156 |
| 159915ETF | 113 | 102 | `skglm_mcp` | +0.1318 | +0.1533 |

## Detailed Trial Metrics & Optimization Objectives

| ETF | Yearly Tail IC IR | Yearly Tail IC Mean | Hit Rate | Decile Monotonicity | Top-Bottom Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 300ETF | 1.7038 | +0.2461 | 100.0% | 0.4230 | +51.8696% |
| 50ETF | 1.7168 | +0.1946 | 90.0% | 0.4061 | +27.5717% |
| 500ETF | 2.0825 | +0.2352 | 100.0% | 0.5188 | +72.2358% |
| 588000ETF | 2.8326 | +0.3292 | 100.0% | 0.6242 | +99.3005% |
| 159915ETF | 4.4199 | +0.3234 | 100.0% | 0.5830 | +90.9861% |

## Selected Features per ETF

### 300ETF
- **Total selected features (Stability Selection)**: 78
- **Active features (Non-zero weights)**: 54
- **Active features**: `first_bar_return`, `bar_ret_0`, `bar_ret_2`, `bar_body_rng_0`, `bar_body_rng_1`, `bar_body_rng_2`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `num_up_bars`, `max_up_ret`, `cl_pos_in_range`, `total_path_length`, `volume_slope`, `close_vs_open_range`, `inside_bar_failure_bull`, `consecutive_higher_highs`, `consecutive_lower_lows`, `early_bearish_engulfing_count`, `volume_concentration`, `volume_acceleration`, `volume_surge_direction`, `pullback_depth_max`, `rally_strength_max`, `vwap_touch_count`, `volume_weighted_price_position`, `net_volume_flow`, `early_body_momentum`, `open_efficiency`, `late_bar_momentum`, `intraday_autocorr`, `open_to_current_return`, `rsi_opening`, `opening_auction_imbalance`, `margin_balance`, `short_balance`, `short_balance_quantity`, `short_sell_quantity`, `total_balance`, `capital_net_ratio`, `northbound_net`, `vix`, `vix_iv_spread`, `vix_iv_ratio`, `yesterday_gap`, `yesterday_close_position`, `measured_move_proximity`, `yesterday_pm_return`, `yesterday_am_return`, `yesterday_early_trend`, `yesterday_early_momentum`, `yesterday_early_vwap_dev`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_intraday_close_position`

![300ETF Diagnostics](plots/diagnostics_300ETF.png)

### 50ETF
- **Total selected features (Stability Selection)**: 79
- **Active features (Non-zero weights)**: 25
- **Active features**: `first_bar_return`, `bar_rng_4`, `bar_vwap_dev_0`, `bar_vwap_dev_2`, `first_bar_sentiment`, `intraday_bullish_fvg`, `shark_32_signal`, `consecutive_higher_highs`, `consecutive_lower_lows`, `volume_surge_max`, `open_to_current_return`, `macd_hist`, `sma100_dist`, `rsi21`, `buy_on_margin_value`, `margin_net_buy`, `capital_net_ratio`, `northbound_net`, `iv`, `vix_iv_spread`, `vix_diff_1d`, `yesterday_body_ratio`, `yesterday_close_position`, `measured_move_proximity`, `yesterday_early_vwap_dev`

![50ETF Diagnostics](plots/diagnostics_50ETF.png)

### 500ETF
- **Total selected features (Stability Selection)**: 116
- **Active features (Non-zero weights)**: 21
- **Active features**: `first_bar_return`, `bar_ret_0`, `bar_rng_0`, `bar_rng_3`, `bar_vwap_dev_0`, `bar_vwap_dev_2`, `max_up_ret`, `opening_range_size`, `volume_concentration`, `volume_surge_direction`, `late_bar_momentum`, `sma100_dist`, `capital_sell_volume`, `capital_sell_value`, `northbound_net`, `iv`, `measured_move_proximity`, `yesterday_early_trend`, `yesterday_day_realized_vol`, `yesterday_day_vwap_dev`, `yesterday_intraday_close_position`

![500ETF Diagnostics](plots/diagnostics_500ETF.png)

### 588000ETF
- **Total selected features (Stability Selection)**: 82
- **Active features (Non-zero weights)**: 25
- **Active features**: `early_skew`, `early_kurtosis`, `bar_ret_0`, `bar_body_rng_2`, `max_up_ret`, `barbed_wire_intensity`, `or_fill_ratio`, `volume_concentration`, `rally_strength_max`, `range_expansion_final_bar`, `volume_weighted_price_position`, `late_bar_momentum`, `decision_bar_body`, `upper_shadow_rejection`, `upper_wick_dominance`, `sma20_dist`, `aroon_osc`, `vol60`, `capital_net_ratio`, `vix_iv_spread`, `volatility_percentile_20d`, `volume_percentile_20d`, `yesterday_first_bar_return`, `yesterday_first_bar_volume`, `yesterday_day_kurtosis`

![588000ETF Diagnostics](plots/diagnostics_588000ETF.png)

### 159915ETF
- **Total selected features (Stability Selection)**: 113
- **Active features (Non-zero weights)**: 102
- **Active features**: `gap_pct`, `first_30min_return`, `early_realized_vol`, `first_bar_return`, `early_vwap_dev`, `early_kurtosis`, `bar_ret_0`, `bar_ret_1`, `bar_ret_2`, `bar_vol_4`, `bar_vol_5`, `bar_rng_0`, `bar_rng_3`, `bar_body_rng_0`, `bar_vwap_dev_1`, `bar_vwap_dev_2`, `bar_vwap_dev_3`, `bar_vwap_dev_5`, `num_up_bars`, `max_up_ret`, `max_down_ret`, `cl_pos_in_range`, `body_to_range_ratio`, `total_path_length`, `volume_slope`, `first_bar_sentiment`, `opening_range_size`, `first_bar_body_ratio`, `inside_bar_failure_bull`, `gap_fill_ratio`, `early_doji_count`, `consecutive_higher_highs`, `consecutive_lower_lows`, `consecutive_bullish_engulfing`, `consecutive_bearish_engulfing`, `volume_concentration`, `volume_trend_intraday`, `volume_acceleration`, `volume_surge_direction`, `pullback_ratio`, `pullback_depth_ratio`, `pullback_depth_max`, `rally_strength_max`, `vwap_slope_intraday`, `vwap_deviation_decision_bar`, `volume_weighted_price_position`, `net_volume_flow`, `early_body_momentum`, `open_efficiency`, `late_bar_momentum`, `trend_strength_intraday`, `high_low_sequence_momentum`, `opening_momentum_score`, `trend_exhaustion_early`, `session_high_proximity`, `open_to_current_return`, `rsi_opening`, `vwap_reversion_strength`, `momentum_strength_intraday`, `volatility_regime_intraday`, `momentum_divergence`, `opening_auction_imbalance`, `macd_hist`, `sma20_dist`, `atr14_norm`, `bb_pctb`, `vol20`, `roc20`, `cci14`, `mfi14`, `aroon_osc`, `vol10`, `vol60`, `bb_width`, `vol_pk20`, `vol_gk10`, `vol_gk20`, `margin_net_buy`, `capital_net_value`, `capital_net_ratio`, `northbound_net`, `iv_vol_ratio`, `vix_vol_ratio`, `vix_iv_spread`, `vix_iv_ratio`, `vix_diff_1d`, `yesterday_gap`, `yesterday_close_position`, `volatility_percentile_20d`, `measured_move_proximity`, `yesterday_pm_return`, `yesterday_am_return`, `yesterday_gap_pct`, `yesterday_first_30min_return`, `yesterday_early_trend`, `yesterday_early_momentum`, `yesterday_early_vwap_dev`, `yesterday_day_realized_vol`, `yesterday_day_close_pos`, `yesterday_day_vwap_dev`, `yesterday_day_kurtosis`, `yesterday_opening_gap_reversal`

![159915ETF Diagnostics](plots/diagnostics_159915ETF.png)

## Methodology Overview
1. **Lockbox Split**: From 2024-03-01 to last day (OOS holdout).
2. **BH-FDR Screening**: Retains features with robust marginal Spearman correlation at FDR = 0.20.
3. **Hierarchical Clustering**: Groups collinear features (threshold = 0.7 distance) and keeps the single strongest feature per cluster.
4. **Stability Selection**: Runs Lasso path over $B=100$ subsamples, selecting features with frequency $\ge 0.60$.
5. **Weighted Fitting**: Employs sample weights $w(y) = |y|^k$ to focus on tail-day returns.
6. **Optuna Objective**: Standardized multi-metric maximization (Stability, General Signal, Signal Structure, Complexity Constraints).