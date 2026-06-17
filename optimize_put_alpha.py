"""
Alpha Weight and Horizon Optimizer for Long Put (Selective Hedge)
===================================================================
Optimizes indicator weights, horizons, and trigger thresholds for the 4 regimes:
  - Regime 1: Short-Term Fall (ST Fall)
  - Regime 2: Medium-Term Fall (MT Fall)
  - Regime 3: Short-Term Crash (ST Crash)
  - Regime 4: Medium-Term Crash (MT Crash)

Saves optimized parameters to backtest/alpha_put_models.json.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from backtest_engine import select_underlying, load_data, get_cycles
from alpha_model import AlphaModel

# Seed for reproducibility
np.random.seed(42)

def compute_forward_targets(df, m_days):
    """
    Computes look-ahead free forward target variables:
      - Forward return over m_days calendar days (using adjusted prices)
      - Forward worst drawdown (maximum drop from close to low_adj) over m_days calendar days
    """
    dates = df.index.values
    close = df["close_adj"].values if "close_adj" in df.columns else df["close"].values
    low = df["low_adj"].values if "low_adj" in df.columns else df["low"].values
    
    n = len(df)
    fwd_ret = np.full(n, np.nan)
    worst_dd = np.full(n, np.nan)
    
    ts_dates = pd.to_datetime(df.index)
    
    for i in range(n):
        t_date = ts_dates[i]
        target_date = t_date + pd.Timedelta(days=m_days)
        
        # Binary search for first index >= target_date
        idx = np.searchsorted(ts_dates, target_date)
        
        if idx < n:
            fwd_ret[i] = (close[idx] - close[i]) / close[i]
            if idx > i:
                worst_dd[i] = np.min(low[i+1 : idx+1] - close[i]) / close[i]
            else:
                worst_dd[i] = 0.0
                
    return fwd_ret, worst_dd

def generate_random_weights(n_indicators, num_samples=500):
    """Generates weights from Dirichlet distribution to sum to 1.0."""
    return np.random.dirichlet(np.ones(n_indicators), size=num_samples)

def optimize_regime(df_norm, regime_key, candidate_indicators, candidate_horizons, is_crash, num_samples=500):
    """
    Grid searches horizons and random-samples indicator weights to maximize:
      - Negative correlation & deep negative mean return for Fall regimes
      - High crash probability lift and negative drawdown correlation for Crash regimes
    """
    best_score = -999999.0
    best_weights = None
    best_horizon = None
    best_threshold = None
    best_metrics = {}

    # Filter out indicators not in the dataframe columns
    active_indicators = [ind for ind in candidate_indicators if ind in df_norm.columns]
    if not active_indicators:
        print(f"  WARNING: No active indicators for {regime_key}!")
        return None

    # Generate random weight vectors
    weight_samples = generate_random_weights(len(active_indicators), num_samples)

    for m in candidate_horizons:
        fwd_ret, worst_dd = compute_forward_targets(df_norm, m)
        df_temp = df_norm.copy()
        df_temp["fwd_ret"] = fwd_ret
        df_temp["worst_dd"] = worst_dd

        # Drop warmup or incomplete end dates
        valid_df = df_temp.dropna(subset=["fwd_ret", "worst_dd"] + active_indicators)
        if len(valid_df) < 100:
            continue

        baseline_crash_prob = (valid_df["worst_dd"] <= -0.05).mean()

        for w_vec in weight_samples:
            # Create weight dict
            w_dict = {ind: w_vec[i] for i, ind in enumerate(active_indicators)}
            
            # Compute score
            weighted_sum = np.zeros(len(valid_df))
            for ind, w in w_dict.items():
                weighted_sum += valid_df[ind].values * w
            
            # Since active indicators all exist in valid_df, sum of weights is 1.0
            scores = weighted_sum

            # Evaluate thresholds (try 75th, 80th, 85th, 90th percentiles of scores)
            for pct in [75, 80, 85, 90]:
                thresh = np.percentile(scores, pct)
                triggered = scores > thresh
                n_trig = triggered.sum()
                if n_trig < 10:
                    continue

                if is_crash:
                    # Target: Crash prediction (drawdown <= -5%)
                    # Correlation between score and negative worst drawdown
                    corr = np.corrcoef(scores, -valid_df["worst_dd"].values)[0, 1]
                    if np.isnan(corr):
                        corr = 0.0

                    crash_in_trig = (valid_df.loc[triggered, "worst_dd"] <= -0.05).mean()
                    lift = crash_in_trig / baseline_crash_prob if baseline_crash_prob > 0 else 1.0

                    # Composite score: Lift + 5.0 * correlation
                    obj_score = lift + 5.0 * corr

                    if obj_score > best_score:
                        best_score = obj_score
                        best_weights = w_dict
                        best_horizon = m
                        best_threshold = float(thresh)
                        best_metrics = {
                            "correlation": corr,
                            "lift": lift,
                            "triggered_crash_prob": crash_in_trig,
                            "baseline_crash_prob": baseline_crash_prob,
                            "placement_rate": 1.0 - (pct / 100.0)
                        }
                else:
                    # Target: Fall prediction (negative return)
                    corr = np.corrcoef(scores, valid_df["fwd_ret"].values)[0, 1]
                    if np.isnan(corr):
                        corr = 0.0

                    mean_ret_trig = valid_df.loc[triggered, "fwd_ret"].mean()
                    mean_ret_all = valid_df["fwd_ret"].mean()

                    # Composite score: negative correlation - 200.0 * mean_ret_trig
                    # (since we want highly negative returns)
                    obj_score = -corr - 200.0 * mean_ret_trig

                    if obj_score > best_score:
                        best_score = obj_score
                        best_weights = w_dict
                        best_horizon = m
                        best_threshold = float(thresh)
                        best_metrics = {
                            "correlation": corr,
                            "mean_return_triggered": mean_ret_trig,
                            "mean_return_baseline": mean_ret_all,
                            "placement_rate": 1.0 - (pct / 100.0)
                        }

    return {
        "weights": best_weights,
        "horizon": int(best_horizon) if best_horizon else None,
        "threshold": best_threshold,
        "metrics": best_metrics
    }

def main():
    parser = argparse.ArgumentParser(description="Alpha Model Parameter and Weight Optimizer")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500", "all"], default="300",
                        help="ETF to optimize (or 'all' to run optimization for 50, 300, 500)")
    parser.add_argument("-n", "--num-samples", type=int, default=1000,
                        help="Number of random weight samples per regime")
    args = parser.parse_args()

    etfs_to_run = ["50", "300", "500"] if args.etf == "all" else [args.etf]
    all_results = {}

    # Load existing models if any
    out_file = "backtest/alpha_put_models.json"
    if os.path.exists(out_file):
        try:
            with open(out_file, "r") as f:
                all_results = json.load(f)
        except Exception:
            pass

    for etf_choice in etfs_to_run:
        print("\n" + "=" * 80)
        print(f"  OPTIMIZING ALPHA WEIGHTS FOR {etf_choice}ETF")
        print("=" * 80)

        select_underlying(etf_choice)
        inst, opt, etf = load_data()

        # Compute normalized indicators using our AlphaModel
        model = AlphaModel()
        df_norm = model.compute_normalized_indicators(etf)

        # Regimes definitions
        regime_configs = {
            "reg1": {
                "name": "Regime 1: Short-Term Fall",
                "indicators": ["ind_rsi_high", "ind_skew_neg", "ind_roc5_neg", "ind_macd_neg", "ind_dist_sma50_neg"],
                "horizons": [5, 10, 14],
                "is_crash": False
            },
            "reg2": {
                "name": "Regime 2: Medium-Term Fall",
                "indicators": ["ind_rsi_low", "ind_dist_sma50_neg", "ind_roc20_neg", "ind_macd_neg"],
                "horizons": [21, 30, 40],
                "is_crash": False
            },
            "reg3": {
                "name": "Regime 3: Short-Term Crash",
                "indicators": ["ind_vol_accel_high", "ind_kurt_high", "ind_skew_neg", "ind_iv_vol_low"],
                "horizons": [5, 10, 14],
                "is_crash": True
            },
            "reg4": {
                "name": "Regime 4: Medium-Term Crash",
                "indicators": ["ind_dd_deep", "ind_dist_sma200_neg", "ind_vol_accel_high", "ind_kurt_high", "ind_skew_neg"],
                "horizons": [21, 30, 40],
                "is_crash": True
            }
        }

        etf_results = {}
        for r_key, config in regime_configs.items():
            print(f"\n  Running optimization for {config['name']}...")
            res = optimize_regime(
                df_norm, 
                r_key, 
                config["indicators"], 
                config["horizons"], 
                config["is_crash"], 
                num_samples=args.num_samples
            )
            if res:
                etf_results[r_key] = res
                print(f"    Best Horizon  : {res['horizon']} calendar days")
                print(f"    Best Threshold: {res['threshold']:.4f}")
                print(f"    Weights       :")
                for ind, w in res["weights"].items():
                    print(f"      {ind:<20}: {w:.3f}")
                print(f"    Metrics       :")
                for m_name, m_val in res["metrics"].items():
                    val_str = f"{m_val:.4f}" if isinstance(m_val, (float, np.float64)) else str(m_val)
                    print(f"      {m_name:<20}: {val_str}")
            else:
                print(f"    FAILED optimization for {r_key}")

        all_results[etf_choice] = etf_results

    # Save to file
    os.makedirs("backtest", exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Saved all optimized models to {out_file}")

if __name__ == "__main__":
    main()
