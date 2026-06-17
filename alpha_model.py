"""
Alpha Model — Indicator normalization and regime score calculation
==================================================================
Defines the 4-Type Decision Matrix score calculation using look-ahead free
rolling percentile ranks.
"""

import pandas as pd
import numpy as np
import pandas_ta as ta

class AlphaModel:
    """
    Computes look-ahead free normalized indicators and weighted scores
    for the 4 put-buying regimes:
      - Regime 1: Short-Term Fall
      - Regime 2: Medium-Term Fall
      - Regime 3: Short-Term Crash
      - Regime 4: Medium-Term Crash
    """
    def __init__(self, weights=None):
        # Default weights if none provided (informed by TODO 2 research)
        self.weights = weights or {
            "reg1": { # ST Fall
                "ind_rsi_high": 0.2,
                "ind_skew_neg": 0.3,
                "ind_roc5_neg": 0.2,
                "ind_macd_neg": 0.1,
                "ind_dist_sma50_neg": 0.2
            },
            "reg2": { # MT Fall
                "ind_rsi_low": 0.2,
                "ind_dist_sma50_neg": 0.3,
                "ind_roc20_neg": 0.3,
                "ind_macd_neg": 0.2
            },
            "reg3": { # ST Crash
                "ind_vol_accel_high": 0.3,
                "ind_kurt_high": 0.2,
                "ind_skew_neg": 0.3,
                "ind_iv_vol_low": 0.2
            },
            "reg4": { # MT Crash
                "ind_dd_deep": 0.3,
                "ind_dist_sma200_neg": 0.2,
                "ind_vol_accel_high": 0.2,
                "ind_kurt_high": 0.1,
                "ind_skew_neg": 0.2
            }
        }

    def compute_normalized_indicators(self, df):
        """
        Takes raw ETF DataFrame and returns a copy with normalized indicator columns.
        Uses look-ahead free rolling percentile rank over 252 days.
        Normalized values range from 0.0 (lowest risk) to 1.0 (highest bearish/crash risk).
        """
        ndf = df.copy()

        # Extract adjusted price columns if available, else raw
        close_col = "close_adj" if "close_adj" in ndf.columns else "close"
        
        # Ensure roc5 is computed
        if "roc5" not in ndf.columns:
            ndf["roc5"] = ta.roc(ndf[close_col], length=5)

        # Helper function for rolling percentile rank
        def roll_pct(series, window=252, min_periods=50):
            return series.rolling(window=window, min_periods=min_periods).rank(pct=True)

        # 1. RSI (High and Low variants)
        ndf["ind_rsi_high"] = ndf["rsi14"] / 100.0
        ndf["ind_rsi_low"] = 1.0 - (ndf["rsi14"] / 100.0)

        # 2. Skewness (negative = high score)
        ndf["ind_skew_neg"] = 1.0 - roll_pct(ndf["skew_20"])

        # 3. Kurtosis (high = high score)
        ndf["ind_kurt_high"] = roll_pct(ndf["kurt_20"])

        # 4. Volatility Acceleration (high = high score)
        ndf["ind_vol_accel_high"] = roll_pct(ndf["vol_accel"])

        # 5. IV-RV Ratio (low ratio/cheap option = high score)
        if "iv_vol_ratio" in ndf.columns and ndf["iv_vol_ratio"].notna().any():
            ndf["ind_iv_vol_low"] = 1.0 - roll_pct(ndf["iv_vol_ratio"])
        else:
            ndf["ind_iv_vol_low"] = np.nan

        # 6. Drawdown (deeper negative drawdown = high score)
        ndf["ind_dd_deep"] = 1.0 - roll_pct(ndf["dd_252"])

        # 7. Distance to SMA50 (negative/far below SMA50 = high score)
        ndf["ind_dist_sma50_neg"] = 1.0 - roll_pct(ndf["dist_sma50"])

        # 8. Distance to SMA200 (negative/far below SMA200 = high score)
        ndf["ind_dist_sma200_neg"] = 1.0 - roll_pct(ndf["dist_sma200"])

        # 9. ROC5 (negative short-term return = high score)
        ndf["ind_roc5_neg"] = 1.0 - roll_pct(ndf["roc5"])

        # 10. ROC20 (negative medium-term return = high score)
        ndf["ind_roc20_neg"] = 1.0 - roll_pct(ndf["roc20"])

        # 11. MACD Histogram (negative histogram = high score)
        ndf["ind_macd_neg"] = 1.0 - roll_pct(ndf["macd_hist"])

        # 12. Volume OBV Divergence (OBV slope negative = high score)
        if "volume" in ndf.columns and ndf["volume"].notna().any():
            try:
                ndf["obv"] = ta.obv(ndf[close_col], ndf["volume"])
                ndf["obv_slope"] = ndf["obv"].rolling(10).mean() - ndf["obv"].rolling(30).mean()
                ndf["ind_obv_divergence"] = 1.0 - roll_pct(ndf["obv_slope"])
            except Exception:
                ndf["ind_obv_divergence"] = np.nan
        else:
            ndf["ind_obv_divergence"] = np.nan

        # 13. Volume Spike (high volume relative to SMA = high score)
        if "volume" in ndf.columns and ndf["volume"].notna().any():
            try:
                ndf["volume_ratio"] = ndf["volume"] / ndf["volume"].rolling(20).mean()
                ndf["ind_volume_spike"] = roll_pct(ndf["volume_ratio"])
            except Exception:
                ndf["ind_volume_spike"] = np.nan
        else:
            ndf["ind_volume_spike"] = np.nan

        return ndf


    def compute_regime_score(self, df, regime_key):
        """
        Computes the weighted score for a given regime name.
        Gracefully handles NaNs by dynamically re-weighting remaining active indicators.
        """
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
