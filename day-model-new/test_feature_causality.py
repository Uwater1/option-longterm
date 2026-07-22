"""
Causality & Stationary Units Verification Test for New Base Primitives.
Tests perturbation invariance of early-bar features to post-decision bars.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from features_extra import extract_early_extras, FULL_EARLY_EXTRA

def test_causality():
    np.random.seed(42)
    # Mock 5m bars for a 48-bar day
    times = pd.date_range("2024-01-02 09:30", periods=48, freq="5min")
    prices = 3.0 + np.cumsum(np.random.randn(48) * 0.005)
    highs = prices + np.abs(np.random.randn(48) * 0.002)
    lows = prices - np.abs(np.random.randn(48) * 0.002)
    opens = prices - np.random.randn(48) * 0.001
    closes = prices + np.random.randn(48) * 0.001
    volumes = np.random.randint(1000, 50000, 48)

    df_original = pd.DataFrame({
        "open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes
    }, index=times)

    prev_close = 3.0
    exp_bar_vol = 25000.0
    decision_bar = 5

    res_orig = extract_early_extras(df_original, prev_close, exp_bar_vol, decision_bar, is_20pct=True)

    # Perturb bars post-decision bar [6..47]
    df_perturbed = df_original.copy()
    df_perturbed.iloc[decision_bar+1:, df_perturbed.columns.get_loc("open")] += 1.0
    df_perturbed.iloc[decision_bar+1:, df_perturbed.columns.get_loc("high")] += 2.0
    df_perturbed.iloc[decision_bar+1:, df_perturbed.columns.get_loc("low")] -= 2.0
    df_perturbed.iloc[decision_bar+1:, df_perturbed.columns.get_loc("close")] += 1.5
    df_perturbed.iloc[decision_bar+1:, df_perturbed.columns.get_loc("volume")] *= 10

    res_pert = extract_early_extras(df_perturbed, prev_close, exp_bar_vol, decision_bar, is_20pct=True)

    new_feats = [
        "star50_limit_proximity_early",
        "double_bottom_bull_flag_early",
        "moving_average_gap_bar_early",
        "tight_trading_range_breakout_thrust"
    ]

    print("--- Causality Perturbation Test Results ---")
    all_passed = True
    for f in new_feats:
        val1 = res_orig[f]
        val2 = res_pert[f]
        diff = abs(val1 - val2)
        passed = (diff < 1e-6) or (np.isnan(val1) and np.isnan(val2))
        if not passed:
            all_passed = False
        print(f"Feature '{f}': Orig={val1:.6f}, Pert={val2:.6f}, Diff={diff:.6e} => {'PASS' if passed else 'FAIL'}")

    assert all_passed, "Causality test failed: early features depended on post-decision bars!"
    print("ALL CAUSALITY TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_causality()
