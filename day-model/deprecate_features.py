"""
Registry of deprecated custom features.

RATIONALE:
These features are custom early-bar and yesterday-mirror indicators that never
achieved a non-zero stability score and were never selected or active in the
final model for any of the 5 ETFs (50, 300, 500, 588000, 159915).
Pruning them reduces candidate-to-sample dimensionality bloat, controlling
overfitting and collinearity, without degrading validation or OOS metrics.
"""
import os

# Flag to include deprecated features for backward compatibility
INCLUDE_DEPRECATED = os.environ.get("INCLUDE_DEPRECATED", "0") == "1"

# Early extra features that are never stable or active across all 5 ETFs
DEPRECATED_EARLY_EXTRA = [
    "opening_gap_reversal",
    "barbed_wire_intensity",
    "wedge_open_flag",
    "inside_bar_compression",
    "volume_climax_exhaustion",
    "opening_range_size",
    "first_bar_body_ratio",
    "intraday_bullish_fvg",
    "intraday_bearish_fvg",
    "inside_bar_failure_bear",
    "gap_fill_ratio",
    "early_bullish_hammer",
    "early_bearish_shooting_star",
    "early_doji_count",
    "shark_32_signal",
    "decision_bar_reversal_signal",
    "consecutive_up_closes",
    "consecutive_down_closes",
    "consecutive_lower_lows",
    "consecutive_same_close_dir",
    "consecutive_bullish_engulfing",
    "consecutive_bearish_engulfing",
    "consolidation_bars_count",
    "early_bullish_engulfing_count",
    "volume_dryup_ratio",
    "volume_per_bar_regime",
    "volume_price_corr",
    "range_compression_ratio",
    "range_expansion_final_bar",
    "breakout_strength_ratio",
    "vwap_deviation_max",
    "vwap_cross_count",
    "vwap_touch_count",
    "vwap_deviation_decision_bar",
    "open_efficiency",
    "trend_bar_dominance",
    "trend_adherence",
    "trend_exhaustion_early",
    "early_trend_consistency",
    "orb_breakout_sentiment",
    "opening_range_position",
    "decision_bar_body",
    "decision_bar_range_rank",
    "upper_shadow_rejection",
    "lower_shadow_rejection",
    "bar_size_trend",
    "body_size_trend",
    "adx_opening",
    "vwap_reversion_strength",
    "volatility_regime_intraday",
    "momentum_divergence",
    # Mined Features v1 that are never stable or active across all 5 ETFs
    "limit_up_proximity_early",
    "morning_hhi_persistence",
    "early_bar_hhi_volume",
    "morning_mean_reversion_score",
    "brooks_high_low_2_early",
    "price_action_thrust_ratio",
    "doji_cluster_intensity",
    "shaved_bars_ratio",
    "climax_reversal_followthrough",
    "early_wavetrend_osc",
    "early_cvd_slope",
    "early_volume_imbalance_ratio",
    "volume_concentration_slope",
    "liquidity_density_early",
    "rbreaker_buy_break_dist_early",
    "rbreaker_sell_break_dist_early",
]

# Yesterday extra features that are never stable or active across all 5 ETFs
DEPRECATED_YESTERDAY_EXTRA = [
    "yesterday_opening_gap_reversal",
    "yesterday_spike_exhaustion_ratio",
    "yesterday_intraday_close_position",
]

# Base/Standard features (from build_features.py) that are never stable or active across all 5 ETFs
DEPRECATED_BASE_FEATURES = [
    "bar_ret_3",
    "bar_ret_4",
    "bar_ret_5",
    "bar_vol_1",
    "bar_vol_2",
    "bar_vol_3",
    "bar_rng_1",
    "bar_rng_4",
    "bar_body_rng_3",
    "bar_body_rng_4",
    "bar_body_rng_5",
    "bar_vwap_dev_4",
    "bar_vwap_dev_5",
    "bb_pctb",
    "volume_sma_ratio_long",
    "yesterday_limit_down_touch",
    "retail_turnover_acceleration",
    "iv_term_structure",
    "iv_acceleration_1d",
    "option_volume_pc_ratio",
    "northbound_net_accel",
    "northbound_momentum_5d",
    "demark_setup_count_day",
    "wavetrend_cross_day",
    "stoch_rsi_divergence",
    "turtle_channel_proximity_day",
    "chande_momentum_osc_day",
    "elder_ray_power_spread",
    "yesterday_volume_ratio",
    "sma_distance_5d",
    "yearly_high_distance",
    "measured_move_proximity",
    "yesterday_early_volume_ratio",
    "yesterday_first_bar_return",
    "yesterday_early_skew",
    "yesterday_early_kurtosis",
    "yesterday_day_late_mom",
    "yesterday_midday_drawdown",
]

# Combined list of deprecated features
DEPRECATED_FEATURES = DEPRECATED_EARLY_EXTRA + DEPRECATED_YESTERDAY_EXTRA + DEPRECATED_BASE_FEATURES
