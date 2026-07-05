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
]

# Yesterday extra features that are never stable or active across all 5 ETFs
DEPRECATED_YESTERDAY_EXTRA = [
    "yesterday_opening_gap_reversal",
    "yesterday_spike_exhaustion_ratio",
]

# Combined list of deprecated features
DEPRECATED_FEATURES = DEPRECATED_EARLY_EXTRA + DEPRECATED_YESTERDAY_EXTRA
