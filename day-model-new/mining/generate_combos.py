#!/usr/bin/env python3
"""
Generate candidate feature combinations based on core pruning rules:
1. Top K absolute train IC pre-filter.
2. Correlation sweet-spot.
3. Domain-specific combination rules for min, max, diff, ratio, ifelse.
4. Forbidden-directions memory checking.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

# Paths
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.append(str(REPO_ROOT / "day-model"))

from build_features import FEATURES

REGIME_FEATURES = [
    "vol20", "vol10", "vol60", "vol_pk20", "vol_gk20", "vix", "iv", "garch_state", 
    "macd_hist", "sma20_dist", "gap_pct", "atr14_norm", "bb_width"
]

def load_mining_memory(etf, side, suffix):
    memory_path = HERE / f"mining_memory_{etf}_{side}{suffix}.json"
    if memory_path.exists():
        with open(memory_path, "r") as f:
            return json.load(f)
    return {"forbidden_features": [], "rejected_families": []}

def is_forbidden(recipe_name, recipe, memory):
    # Check if exact recipe name is forbidden
    if recipe_name in memory.get("forbidden_features", []):
        return True
        
    # Check family matches (e.g. if family was rejected)
    for fam in memory.get("rejected_families", []):
        if fam in recipe_name:
            return True
            
    return False

def is_vol_or_volume(feature_name):
    # Check if a feature name indicates a positive scaling volatility/volume indicator
    fn = feature_name.lower()
    for keyword in ["vol", "atr", "width", "vix", "volume", "balance", "capital", "northbound"]:
        if keyword in fn:
            return True
    return False

def _spearman_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape[0] < 5:
        return 0.0
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    from scipy.stats import rankdata
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if denom < 1e-12:
        return 0.0
    return float((ra * rb).sum() / denom)

def compute_side_tail_ic(y_true: np.ndarray, y_pred: np.ndarray, side: str) -> float:
    n = len(y_pred)
    if side in ["long", "short"]:
        pct = 0.15
    else:  # single (two-sided)
        pct = 0.10
    n_tail = max(5, int(n * pct))
    if n < n_tail:
        return 0.0
        
    order = np.argsort(y_pred)
    if side == "long":
        idx = order[-n_tail:]
    elif side == "short":
        idx = order[:n_tail]
    else:  # two-sided
        idx = np.concatenate([order[:n_tail], order[-n_tail:]])
        
    return _spearman_from_arrays(y_true[idx], y_pred[idx])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--etf", required=True, choices=["300ETF", "50ETF", "500ETF", "588000ETF", "159915ETF"])
    parser.add_argument("-s", "--side", required=True, choices=["single", "long", "short"])
    parser.add_argument("-k", "--top-k", type=int, default=30, help="Number of top base features to use for combinations")
    parser.add_argument("--early", action="store_true", help="Use early window return dataset")
    args = parser.parse_args()

    suffix = "_early" if args.early else ""
    
    # 1. Load dynamic dates
    if args.etf == "588000ETF":
        train_start = pd.Timestamp("2020-11-01")
        train_end = pd.Timestamp("2025-01-01")
    else:
        train_start = pd.Timestamp("2015-01-01")
        train_end = pd.Timestamp("2022-01-01")

    print(f"Generating combos for {args.etf} ({args.side})")
    
    # 2. Load dataset
    features_dir = REPO_ROOT / "day-model" / "data"
    fname = f"features_{args.etf}_early.parquet" if args.early else f"features_{args.etf}.parquet"
    path = features_dir / fname
    if not path.exists():
        print(f"ERROR: Dataset not found at {path}")
        sys.exit(1)
        
    df = pd.read_parquet(path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    train_df = df[(df["date"] >= train_start) & (df["date"] < train_end)].reset_index(drop=True)
    if len(train_df) == 0:
        print("ERROR: Empty train set.")
        sys.exit(1)

    y_train = train_df["trade_return"].values.astype(np.float64)
    X_df = train_df[FEATURES].ffill()
    col_med = X_df.median().fillna(0.0)
    X_df = X_df.fillna(col_med)
    
    # 3. Pre-evaluate single feature performance to select Top K
    print(f"Pre-evaluating {len(FEATURES)} features on train set...")
    feature_ics = []
    for feat in FEATURES:
        x = X_df[feat].values
        # Raw Spearman to determine sign
        raw_ic = _spearman_from_arrays(x, y_train)
        sign = -1.0 if raw_ic < 0 else 1.0
        x_flipped = x * sign
        tail_ic = compute_side_tail_ic(y_train, x_flipped, args.side)
        feature_ics.append((feat, abs(tail_ic), sign))
        
    feature_ics.sort(key=lambda x: x[1], reverse=True)
    
    top_k_features = [item[0] for item in feature_ics[:args.top_k]]
    print(f"Selected Top {args.top_k} features. Best: {feature_ics[0][0]} (IC={feature_ics[0][1]:.4f})")

    # 4. Compute pairwise correlation matrix for top K features
    corr_matrix = X_df[top_k_features].corr().abs()
    
    # Load mining memory
    memory = load_mining_memory(args.etf, args.side, suffix)
    
    candidates = []
    
    # Identify regime features in the top K
    regime_candidates = [f for f in top_k_features if f in REGIME_FEATURES]
    non_regime_candidates = [f for f in top_k_features if f not in REGIME_FEATURES][:15] # limit action features
    
    # 5. Generate Combinations
    for i in range(len(top_k_features)):
        feat_a = top_k_features[i]
        for j in range(i + 1, len(top_k_features)):
            feat_b = top_k_features[j]
            
            corr = corr_matrix.loc[feat_a, feat_b]
            # Prune if correlation is out of sweet-spot
            if corr > 0.85 or corr < 0.15:
                continue
                
            # min / max / diff
            for op in ["min", "max", "diff"]:
                name = f"combo_{op}__{feat_a}__{feat_b}"
                recipe = {"op": op, "feature_a": feat_a, "feature_b": feat_b}
                if not is_forbidden(name, recipe, memory):
                    candidates.append({"feature_name": name, "recipe": recipe})
                    
            # ratio: check if feat_b is vol/volume/scaling
            if is_vol_or_volume(feat_b):
                name = f"combo_ratio__{feat_a}__{feat_b}"
                recipe = {"op": "ratio", "feature_a": feat_a, "feature_b": feat_b}
                if not is_forbidden(name, recipe, memory):
                    candidates.append({"feature_name": name, "recipe": recipe})
            if is_vol_or_volume(feat_a):
                name = f"combo_ratio__{feat_b}__{feat_a}"
                recipe = {"op": "ratio", "feature_a": feat_b, "feature_b": feat_a}
                if not is_forbidden(name, recipe, memory):
                    candidates.append({"feature_name": name, "recipe": recipe})

    # ifelse combinations
    for cond in regime_candidates:
        for a_idx in range(len(non_regime_candidates)):
            feat_a = non_regime_candidates[a_idx]
            for b_idx in range(a_idx + 1, len(non_regime_candidates)):
                feat_b = non_regime_candidates[b_idx]
                
                name = f"combo_ifelse__{cond}__{feat_a}__{feat_b}"
                recipe = {
                    "op": "ifelse",
                    "feature_cond": cond,
                    "feature_a": feat_a,
                    "feature_b": feat_b
                }
                if not is_forbidden(name, recipe, memory):
                    candidates.append({"feature_name": name, "recipe": recipe})

    # Save candidates JSON
    os.makedirs(HERE, exist_ok=True)
    out_path = HERE / f"candidates_{args.etf}_{args.side}{suffix}.json"
    with open(out_path, "w") as f:
        json.dump(candidates, f, indent=2)
        
    print(f"Generated {len(candidates)} candidate combinations for {args.etf} ({args.side}). Saved to {out_path.name}")

if __name__ == "__main__":
    main()
