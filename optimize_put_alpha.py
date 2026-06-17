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

def generate_random_weights(n_indicators, num_samples=500, max_weight=0.5):
    """Generates weights from Dirichlet distribution and clips them to max_weight, then normalizes."""
    effective_max = max(max_weight, 1.0 / n_indicators) if n_indicators > 0 else 1.0
    samples = []
    for _ in range(num_samples):
        w = np.random.dirichlet(np.ones(n_indicators))
        # Iterative clipping & normalization to ensure sum=1 and all <= effective_max
        for _ in range(10):
            w = np.clip(w, 0, effective_max)
            w_sum = w.sum()
            if w_sum > 0:
                w = w / w_sum
        samples.append(w)
    return np.array(samples)

def optimize_regime(df_norm, regime_key, candidate_indicators, candidate_horizons, is_crash, num_samples=500, max_weight=0.5):
    """
    Grid searches horizons and random-samples indicator weights to maximize:
      - Negative correlation & deep negative mean return for Fall regimes
      - High crash probability lift and negative drawdown correlation for Crash regimes
    """
    best_score = -999999.0
    best_weights = None
    best_horizon = None
    best_threshold = None
    best_gamma = 0.0
    best_metrics = {}

    # Filter out indicators not in the dataframe columns
    active_indicators = [ind for ind in candidate_indicators if ind in df_norm.columns]
    if not active_indicators:
        print(f"  WARNING: No active indicators for {regime_key}!")
        return None

    # Generate random weight vectors with constraint
    weight_samples = generate_random_weights(len(active_indicators), num_samples, max_weight=max_weight)

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
        
        # Grab IV volume ratio for dynamic threshold
        iv_vol_ratio = valid_df["iv_vol_ratio"].values if "iv_vol_ratio" in valid_df.columns else np.ones(len(valid_df))
        iv_vol_ratio = np.nan_to_num(iv_vol_ratio, nan=1.0)

        for w_vec in weight_samples:
            # Create weight dict
            w_dict = {ind: w_vec[i] for i, ind in enumerate(active_indicators)}
            
            # Compute score
            weighted_sum = np.zeros(len(valid_df))
            for ind, w in w_dict.items():
                weighted_sum += valid_df[ind].values * w
            
            scores = weighted_sum

            # Evaluate base thresholds
            for pct in [75, 80, 85, 90]:
                thresh = np.percentile(scores, pct)
                
                # Try dynamic thresholds modulated by IV volume ratio
                for gamma in [0.0, 0.05, 0.1, 0.15, 0.2]:
                    thresholds_t = thresh + gamma * (iv_vol_ratio - 1.0)
                    triggered = scores > thresholds_t
                    n_trig = triggered.sum()
                    if n_trig < 10:
                        continue

                    if is_crash:
                        corr = np.corrcoef(scores, -valid_df["worst_dd"].values)[0, 1]
                        if np.isnan(corr):
                            corr = 0.0

                        crash_in_trig = (valid_df.loc[triggered, "worst_dd"] <= -0.05).mean()
                        lift = crash_in_trig / baseline_crash_prob if baseline_crash_prob > 0 else 1.0

                        obj_score = lift + 5.0 * corr

                        if obj_score > best_score:
                            best_score = obj_score
                            best_weights = w_dict
                            best_horizon = m
                            best_threshold = float(thresh)
                            best_gamma = float(gamma)
                            best_metrics = {
                                "correlation": corr,
                                "lift": lift,
                                "triggered_crash_prob": crash_in_trig,
                                "baseline_crash_prob": baseline_crash_prob,
                                "placement_rate": 1.0 - (pct / 100.0)
                            }
                    else:
                        corr = np.corrcoef(scores, valid_df["fwd_ret"].values)[0, 1]
                        if np.isnan(corr):
                            corr = 0.0

                        mean_ret_trig = valid_df.loc[triggered, "fwd_ret"].mean()
                        mean_ret_all = valid_df["fwd_ret"].mean()

                        obj_score = -corr - 200.0 * mean_ret_trig

                        if obj_score > best_score:
                            best_score = obj_score
                            best_weights = w_dict
                            best_horizon = m
                            best_threshold = float(thresh)
                            best_gamma = float(gamma)
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
        "gamma": best_gamma,
        "metrics": best_metrics
    }

def evaluate_model_oos(df_norm, model_params, candidate_indicators, is_crash):
    """
    Evaluates optimized model parameters on out-of-sample (test) data.
    """
    m = model_params["horizon"]
    w_dict = model_params["weights"]
    thresh = model_params["threshold"]
    gamma = model_params["gamma"]
    
    fwd_ret, worst_dd = compute_forward_targets(df_norm, m)
    df_temp = df_norm.copy()
    df_temp["fwd_ret"] = fwd_ret
    df_temp["worst_dd"] = worst_dd
    
    active_indicators = [ind for ind in candidate_indicators if ind in df_norm.columns]
    valid_df = df_temp.dropna(subset=["fwd_ret", "worst_dd"] + active_indicators)
    if len(valid_df) < 5:
        return 1.0 if is_crash else 0.0
        
    weighted_sum = np.zeros(len(valid_df))
    for ind, w in w_dict.items():
        weighted_sum += valid_df[ind].values * w
    scores = weighted_sum
    
    iv_vol_ratio = valid_df["iv_vol_ratio"].values if "iv_vol_ratio" in valid_df.columns else np.ones(len(valid_df))
    iv_vol_ratio = np.nan_to_num(iv_vol_ratio, nan=1.0)
    
    thresholds_t = thresh + gamma * (iv_vol_ratio - 1.0)
    triggered = scores > thresholds_t
    
    if triggered.sum() == 0:
        return 1.0 if is_crash else 0.0
        
    if is_crash:
        baseline_crash_prob = (valid_df["worst_dd"] <= -0.05).mean()
        crash_in_trig = (valid_df.loc[triggered, "worst_dd"] <= -0.05).mean()
        lift = crash_in_trig / baseline_crash_prob if baseline_crash_prob > 0 else 1.0
        return lift
    else:
        mean_ret_trig = valid_df.loc[triggered, "fwd_ret"].mean()
        return mean_ret_trig

def run_walk_forward_validation(df_norm, regime_configs, etf_choice, num_samples, max_weight):
    """
    Performs annual rolling walk-forward validation (Train: 2 years, Test: 1 year).
    """
    years = sorted(df_norm.index.year.unique())
    test_years = [y for y in years if y >= 2021]
    if not test_years:
        print("  WARNING: Not enough years in data for walk-forward validation!")
        return

    print("\n" + "=" * 80)
    print(f"  WALK-FORWARD VALIDATION SUMMARY FOR {etf_choice}ETF (max_weight={max_weight})")
    print("=" * 80)

    for r_key, config in regime_configs.items():
        print(f"\n  Regime: {config['name']}")
        print(f"  {'Test Year':<10} | {'IS Metric':<10} | {'OOS Metric':<10} | {'Degradation':<12} | {'Horizon':<8} | {'Gamma':<6}")
        print("  " + "-" * 65)

        is_metrics = []
        oos_metrics = []

        for test_yr in test_years:
            train_df = df_norm[(df_norm.index.year >= test_yr - 2) & (df_norm.index.year <= test_yr - 1)]
            test_df = df_norm[df_norm.index.year == test_yr]

            if len(train_df) < 100 or len(test_df) < 20:
                continue

            res_train = optimize_regime(
                train_df,
                r_key,
                config["indicators"],
                config["horizons"],
                config["is_crash"],
                num_samples=num_samples,
                max_weight=max_weight
            )

            if not res_train:
                continue

            is_metric = res_train["metrics"]["lift"] if config["is_crash"] else res_train["metrics"]["mean_return_triggered"]
            oos_metric = evaluate_model_oos(test_df, res_train, config["indicators"], config["is_crash"])

            # Degradation calculation
            degrad = 0.0
            if config["is_crash"]:
                if is_metric > 1.0:
                    degrad = (is_metric - oos_metric) / (is_metric - 1.0)
            else:
                if is_metric < 0.0:
                    degrad = (oos_metric - is_metric) / abs(is_metric)

            degrad_pct = f"{degrad:.1%}" if degrad != 0.0 else "0.0%"
            if degrad > 0.40:
                degrad_pct += " ⚠️"

            print(f"  {test_yr:<10} | {is_metric:<10.4f} | {oos_metric:<10.4f} | {degrad_pct:<12} | {res_train['horizon']:<8} | {res_train['gamma']:<6.2f}")
            
            is_metrics.append(is_metric)
            oos_metrics.append(oos_metric)

        if is_metrics:
            avg_is = np.mean(is_metrics)
            avg_oos = np.mean(oos_metrics)
            avg_degrad = 0.0
            if config["is_crash"]:
                if avg_is > 1.0:
                    avg_degrad = (avg_is - avg_oos) / (avg_is - 1.0)
            else:
                if avg_is < 0.0:
                    avg_degrad = (avg_oos - avg_is) / abs(avg_is)

            avg_degrad_pct = f"{avg_degrad:.1%}"
            if avg_degrad > 0.40:
                avg_degrad_pct += " ⚠️ [OVERFIT DETECTED]"
            print(f"  {'AVERAGE':<10} | {avg_is:<10.4f} | {avg_oos:<10.4f} | {avg_degrad_pct:<12}")

def main():
    parser = argparse.ArgumentParser(description="Alpha Model Parameter and Weight Optimizer")
    parser.add_argument("-e", "--etf", type=str, choices=["50", "300", "500", "all"], default="300",
                        help="ETF to optimize (or 'all' to run optimization for 50, 300, 500)")
    parser.add_argument("-n", "--num-samples", type=int, default=1000,
                        help="Number of random weight samples per regime")
    parser.add_argument("--max-weight", type=float, default=0.5,
                        help="Maximum weight allowed for any single indicator to avoid overfit")
    parser.add_argument("--walk-forward", action="store_true", default=False,
                        help="Run annual rolling walk-forward validation instead of full-sample training")
    args = parser.parse_args()

    etfs_to_run = ["50", "300", "500"] if args.etf == "all" else [args.etf]
    all_results = {}

    # Load existing models if any
    out_file = "backtest/alpha_put_models.json"
    if os.path.exists(out_file) and not args.walk_forward:
        try:
            with open(out_file, "r") as f:
                all_results = json.load(f)
        except Exception:
            pass

    for etf_choice in etfs_to_run:
        print("\n" + "=" * 80)
        print(f"  PROCESSING ALPHA WEIGHTS FOR {etf_choice}ETF (max_weight={args.max_weight})")
        print("=" * 80)

        select_underlying(etf_choice)
        inst, opt, etf = load_data()

        # Compute normalized indicators using our AlphaModel
        model = AlphaModel()
        df_norm = model.compute_normalized_indicators(etf)

        # Regimes definitions (updated with obv divergence and volume spike)
        regime_configs = {
            "reg1": {
                "name": "Regime 1: Short-Term Fall",
                "indicators": ["ind_rsi_high", "ind_skew_neg", "ind_roc5_neg", "ind_macd_neg", "ind_dist_sma50_neg", "ind_obv_divergence", "ind_volume_spike"],
                "horizons": [5, 10, 14],
                "is_crash": False
            },
            "reg2": {
                "name": "Regime 2: Medium-Term Fall",
                "indicators": ["ind_rsi_low", "ind_dist_sma50_neg", "ind_roc20_neg", "ind_macd_neg", "ind_obv_divergence", "ind_volume_spike"],
                "horizons": [21, 30, 40],
                "is_crash": False
            },
            "reg3": {
                "name": "Regime 3: Short-Term Crash",
                "indicators": ["ind_vol_accel_high", "ind_kurt_high", "ind_skew_neg", "ind_iv_vol_low", "ind_obv_divergence", "ind_volume_spike"],
                "horizons": [5, 10, 14],
                "is_crash": True
            },
            "reg4": {
                "name": "Regime 4: Medium-Term Crash",
                "indicators": ["ind_dd_deep", "ind_dist_sma200_neg", "ind_vol_accel_high", "ind_kurt_high", "ind_skew_neg", "ind_obv_divergence", "ind_volume_spike"],
                "horizons": [21, 30, 40],
                "is_crash": True
            }
        }

        if args.walk_forward:
            run_walk_forward_validation(df_norm, regime_configs, etf_choice, args.num_samples, args.max_weight)
        else:
            etf_results = {}
            for r_key, config in regime_configs.items():
                print(f"\n  Running optimization for {config['name']}...")
                res = optimize_regime(
                    df_norm, 
                    r_key, 
                    config["indicators"], 
                    config["horizons"], 
                    config["is_crash"], 
                    num_samples=args.num_samples,
                    max_weight=args.max_weight
                )
                if res:
                    etf_results[r_key] = res
                    print(f"    Best Horizon  : {res['horizon']} calendar days")
                    print(f"    Best Threshold: {res['threshold']:.4f}")
                    print(f"    Best Gamma    : {res['gamma']:.2f}")
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

    if not args.walk_forward:
        # Save to file
        os.makedirs("backtest", exist_ok=True)
        with open(out_file, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n  Saved all optimized models to {out_file}")

if __name__ == "__main__":
    main()
