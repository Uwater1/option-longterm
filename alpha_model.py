"""
Alpha Model — Indicator normalization and regime score calculation
==================================================================
Defines the 4-Type Decision Matrix score calculation using look-ahead free
rolling percentile ranks.

Phase 1 improvements (OOS overhaul):
  - RSI normalized via rolling percentile rank (was raw /100 — distribution drift).
  - Expanding-window percentile option (min_periods=252) for adaptive thresholds.
  - 5 new tail-risk / structural indicators (look-ahead-free, [0,1] bearish scale).
"""

import pandas as pd
import numpy as np
import pandas_ta as ta


def _roll_pct(series, window=252, min_periods=252, expanding=False):
    """Rolling (or expanding) percentile rank, look-ahead free.

    Returns values in [0,1] where 1.0 = largest value seen so far.
    Expanding mode grows the window up to the current index (min_periods warmup).
    """
    if expanding:
        return series.expanding(min_periods=min_periods).rank(pct=True)
    return series.rolling(window=window, min_periods=min_periods).rank(pct=True)


class AlphaModel:
    """
    Computes look-ahead free normalized indicators and weighted scores
    for the 4 put-buying regimes:
      - Regime 1: Short-Term Fall
      - Regime 2: Medium-Term Fall
      - Regime 3: Short-Term Crash
      - Regime 4: Medium-Term Crash
    """

    def __init__(self, weights=None, expanding_pct=False):
        # Default weights if none provided (informed by TODO 2 research).
        # Used as fallback when no optimized weights are supplied.
        self.expanding_pct = expanding_pct
        self.weights = weights or {
            "reg1": {  # ST Fall
                "ind_rsi_high": 0.2,
                "ind_skew_neg": 0.3,
                "ind_roc5_neg": 0.2,
                "ind_macd_neg": 0.1,
                "ind_dist_sma50_neg": 0.2
            },
            "reg2": {  # MT Fall
                "ind_rsi_low": 0.2,
                "ind_dist_sma50_neg": 0.3,
                "ind_roc20_neg": 0.3,
                "ind_macd_neg": 0.2
            },
            "reg3": {  # ST Crash
                "ind_vol_accel_high": 0.3,
                "ind_kurt_high": 0.2,
                "ind_skew_neg": 0.3,
                "ind_iv_vol_low": 0.2
            },
            "reg4": {  # MT Crash
                "ind_dd_deep": 0.3,
                "ind_dist_sma200_neg": 0.2,
                "ind_vol_accel_high": 0.2,
                "ind_kurt_high": 0.1,
                "ind_skew_neg": 0.2
            }
        }

    def _rp(self, series):
        """Convenience: rolling percentile rank with current mode."""
        return _roll_pct(series, expanding=self.expanding_pct)

    def compute_normalized_indicators(self, df):
        """
        Takes raw ETF DataFrame and returns a copy with normalized indicator columns.
        Uses look-ahead free rolling percentile rank over 252 days.
        Normalized values range from 0.0 (lowest risk) to 1.0 (highest bearish/crash risk).
        """
        ndf = df.copy()

        # Extract adjusted price columns if available, else raw.
        close_col = "close_adj" if "close_adj" in ndf.columns else "close"
        high_col = "high_adj" if "high_adj" in ndf.columns else "high"
        low_col = "low_adj" if "low_adj" in ndf.columns else "low"

        # Ensure derived raw indicators exist (idempotent — only fill if missing).
        if "roc5" not in ndf.columns:
            ndf["roc5"] = ta.roc(ndf[close_col], length=5)
        if "vol60" not in ndf.columns:
            ndf["vol60"] = ndf[close_col].pct_change().rolling(60).std() * np.sqrt(252)
        if "vol10" not in ndf.columns:
            ndf["vol10"] = ndf[close_col].pct_change().rolling(10).std() * np.sqrt(252)
        if "atr20" not in ndf.columns:
            try:
                ndf["atr20"] = ta.atr(ndf[high_col], ndf[low_col], ndf[close_col], length=20)
            except Exception:
                ndf["atr20"] = np.nan
        if "vol20" not in ndf.columns:
            ndf["vol20"] = ndf[close_col].pct_change().rolling(20).std() * np.sqrt(252)
        if "rsi14" not in ndf.columns:
            ndf["rsi14"] = ta.rsi(ndf[close_col], length=14)

        # ── 1. RSI (rolling percentile rank — was raw /100, which drifts across regimes)
        ndf["ind_rsi_high"] = self._rp(ndf["rsi14"])
        ndf["ind_rsi_low"] = 1.0 - self._rp(ndf["rsi14"])

        # ── 2. Skewness (negative = high score)
        if "skew_20" in ndf.columns:
            ndf["ind_skew_neg"] = 1.0 - self._rp(ndf["skew_20"])
        else:
            ndf["ind_skew_neg"] = np.nan

        # ── 3. Kurtosis (high = high score)
        if "kurt_20" in ndf.columns:
            ndf["ind_kurt_high"] = self._rp(ndf["kurt_20"])
        else:
            ndf["ind_kurt_high"] = np.nan

        # ── 4. Volatility Acceleration (high = high score)
        if "vol_accel" in ndf.columns:
            ndf["ind_vol_accel_high"] = self._rp(ndf["vol_accel"])
        else:
            ndf["ind_vol_accel_high"] = np.nan

        # ── 5. IV-RV Ratio (low ratio / cheap option = high score)
        if "iv_vol_ratio" in ndf.columns and ndf["iv_vol_ratio"].notna().any():
            ndf["ind_iv_vol_low"] = 1.0 - self._rp(ndf["iv_vol_ratio"])
        else:
            ndf["ind_iv_vol_low"] = np.nan

        # ── 6. Drawdown (deeper negative drawdown = high score)
        if "dd_252" in ndf.columns:
            ndf["ind_dd_deep"] = 1.0 - self._rp(ndf["dd_252"])
        else:
            ndf["ind_dd_deep"] = np.nan

        # ── 7. Distance to SMA50 (negative/far below SMA50 = high score)
        if "dist_sma50" in ndf.columns:
            ndf["ind_dist_sma50_neg"] = 1.0 - self._rp(ndf["dist_sma50"])
        else:
            ndf["ind_dist_sma50_neg"] = np.nan

        # ── 8. Distance to SMA200 (negative/far below SMA200 = high score)
        if "dist_sma200" in ndf.columns:
            ndf["ind_dist_sma200_neg"] = 1.0 - self._rp(ndf["dist_sma200"])
        else:
            ndf["ind_dist_sma200_neg"] = np.nan

        # ── 9. ROC5 (negative short-term return = high score)
        if "roc5" in ndf.columns:
            ndf["ind_roc5_neg"] = 1.0 - self._rp(ndf["roc5"])
        else:
            ndf["ind_roc5_neg"] = np.nan

        # ── 10. ROC20 (negative medium-term return = high score)
        if "roc20" in ndf.columns:
            ndf["ind_roc20_neg"] = 1.0 - self._rp(ndf["roc20"])
        else:
            ndf["ind_roc20_neg"] = np.nan

        # ── 11. MACD Histogram (negative histogram = high score)
        if "macd_hist" in ndf.columns:
            ndf["ind_macd_neg"] = 1.0 - self._rp(ndf["macd_hist"])
        else:
            ndf["ind_macd_neg"] = np.nan

        # ── 12. Volume OBV Divergence (OBV slope negative = high score)
        if "volume" in ndf.columns and ndf["volume"].notna().any():
            try:
                ndf["obv"] = ta.obv(ndf[close_col], ndf["volume"])
                ndf["obv_slope"] = ndf["obv"].rolling(10).mean() - ndf["obv"].rolling(30).mean()
                ndf["ind_obv_divergence"] = 1.0 - self._rp(ndf["obv_slope"])
            except Exception:
                ndf["ind_obv_divergence"] = np.nan
        else:
            ndf["ind_obv_divergence"] = np.nan

        # ── 13. Volume Spike (high volume relative to SMA = high score)
        if "volume" in ndf.columns and ndf["volume"].notna().any():
            try:
                ndf["volume_ratio"] = ndf["volume"] / ndf["volume"].rolling(20).mean()
                ndf["ind_volume_spike"] = self._rp(ndf["volume_ratio"])
            except Exception:
                ndf["ind_volume_spike"] = np.nan
        else:
            ndf["ind_volume_spike"] = np.nan

        # ── NEW 14. ATR range expansion (atr20 / rolling median — range blowout)
        if ndf["atr20"].notna().any():
            atr_med = ndf["atr20"].rolling(252, min_periods=50).median()
            atr_ratio = ndf["atr20"] / atr_med.replace(0.0, np.nan)
            ndf["ind_atr_ratio_high"] = self._rp(atr_ratio)
        else:
            ndf["ind_atr_ratio_high"] = np.nan

        # ── NEW 15. Vol-of-vol (volatility instability: std of 20d vol over 20d)
        if ndf["vol20"].notna().any():
            vov = ndf["vol20"].rolling(20).std()
            ndf["ind_vol_of_vol_high"] = self._rp(vov)
        else:
            ndf["ind_vol_of_vol_high"] = np.nan

        # ── NEW 16. Range expansion (daily range normalized by close)
        if ndf[high_col].notna().any() and ndf[low_col].notna().any():
            day_range = (ndf[high_col] - ndf[low_col]) / ndf[close_col].replace(0.0, np.nan)
            ndf["ind_range_expansion_high"] = self._rp(day_range)
        else:
            ndf["ind_range_expansion_high"] = np.nan

        # ── NEW 17. Vol term structure (vol10/vol60 — inverted vol term = stress)
        if ndf["vol10"].notna().any() and ndf["vol60"].notna().any():
            vol_term = ndf["vol10"] / ndf["vol60"].replace(0.0, np.nan)
            # High vol_term (short vol >> long vol) = inverted/stress = bearish
            ndf["ind_term_structure_neg"] = self._rp(vol_term)
        else:
            ndf["ind_term_structure_neg"] = np.nan

        # ── NEW 18. RSI divergence (price up but RSI slope down = bearish divergence)
        if ndf["rsi14"].notna().any() and "roc20" in ndf.columns:
            try:
                rsi_slope = ndf["rsi14"].diff(10)
                # Bearish divergence: price ROC20 high but RSI slope low (rolling rank of -divergence)
                # divergence score = -(price_rank - rsi_slope_rank); higher = more bearish divergence
                price_rank = self._rp(ndf["roc20"])
                rsi_rank = self._rp(rsi_slope)
                divergence = price_rank - rsi_rank  # high price rank, low rsi rank → positive = bearish
                ndf["ind_rsi_divergence_neg"] = self._rp(divergence)
            except Exception:
                ndf["ind_rsi_divergence_neg"] = np.nan
        else:
            ndf["ind_rsi_divergence_neg"] = np.nan

        return ndf

    def compute_regime_score(self, df, regime_key):
        """
        Computes the weighted score for a given regime name.
        Gracefully handles NaNs by dynamically re-weighting remaining active indicators.
        """
        if regime_key not in self.weights:
            raise KeyError(f"Unknown regime key: {regime_key}")
        reg_weights = self.weights[regime_key]
        weighted_sum = pd.Series(0.0, index=df.index)
        sum_weights = pd.Series(0.0, index=df.index)

        for col, w in reg_weights.items():
            if col in df.columns:
                valid_mask = df[col].notna()
                weighted_sum += df[col].fillna(0.0) * w
                sum_weights += valid_mask.astype(float) * w

        # Avoid division by zero by replacing 0.0 with NaN
        return weighted_sum / sum_weights.replace(0.0, np.nan)

    def compute_all_scores(self, df):
        """
        Computes all scores for the 4 regimes and returns DataFrame with score columns.
        """
        df_norm = self.compute_normalized_indicators(df)
        df_norm["score_reg1"] = self.compute_regime_score(df_norm, "reg1")
        df_norm["score_reg2"] = self.compute_regime_score(df_norm, "reg2")
        df_norm["score_reg3"] = self.compute_regime_score(df_norm, "reg3")
        df_norm["score_reg4"] = self.compute_regime_score(df_norm, "reg4")
        return df_norm
