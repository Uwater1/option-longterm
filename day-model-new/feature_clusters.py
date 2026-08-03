#!/usr/bin/env python3
"""
ONC (Optimal Number of Clusters) Feature Clustering Module.

Implements de Prado's ONC algorithm to group admitted features into clusters
based on Spearman rank correlation structure. Used by newtrade's group-constrained
top-K selector to enforce diversity (max 1 feature per cluster per day).

Algorithm:
1. Compute Spearman rank correlation matrix on training-period feature values
2. Convert to angular distance: d(i,j) = sqrt(0.5 * (1 - corr(i,j)))
3. K-Means sweep K in [2, min(max_clusters, N-1)], pick best silhouette
4. Recursive re-split: clusters with below-avg silhouette get re-clustered
5. Output: cluster_assignments_{etf}_{side}.json

Reference: Lopez de Prado & Lewis, "Detection of False Investment Strategies
Using Unsupervised Learning" (Advances in Financial ML, ch.4).

Usage:
    python feature_clusters.py -e 300ETF -s single
    python feature_clusters.py -e all -s single
"""

import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples

# Path setup
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.append(str(REPO_ROOT / "day-model"))
sys.path.append(str(HERE / "mining"))

from build_features import FEATURES
from recipe_utils import compute_recipe

# Training end dates (cluster fit on training data only — no lookahead)
ADAPTIVE_DATES = {
    "588000ETF": ("2020-11-01", "2025-01-01"),
    "_default": ("2014-01-01", "2022-01-01"),
}

ALL_ETFS = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]


def onc(corr: pd.DataFrame, max_clusters: int = 25, max_cluster_size: int = 20, n_init: int = 10, random_state: int = 0) -> dict:
    """
    Optimal Number of Clusters (ONC) algorithm.

    Args:
        corr: pandas DataFrame, feature correlation matrix (Spearman recommended)
        max_clusters: maximum K to sweep
        max_cluster_size: maximum allowed cluster size before recursive re-splitting
        n_init: KMeans restarts per K
        random_state: fixed seed for reproducibility

    Returns:
        dict {cluster_id: [feature_names]}
    """
    dist = np.sqrt(0.5 * np.clip(1.0 - corr.values, 0.0, 2.0))  # angular distance, proper metric
    feats = corr.columns.tolist()
    n_feats = len(feats)

    if n_feats <= 2:
        # Cannot cluster meaningfully below 3 features
        return {0: feats}

    # Adaptive search range: k_min scales with pool size N up to floor(N/10)+1 (max 10)
    k_min_calc = int(n_feats // 10) + 1
    k_min = max(2, min(k_min_calc, 10))
    k_min = min(k_min, n_feats - 1)

    k_max = min(max(max_clusters, 25), n_feats - 1)
    if k_min > k_max:
        k_min = k_max

    best_kmeans, best_sil, best_sil_samples = None, -1.0, None

    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=n_init, random_state=random_state).fit(dist)
        sil = silhouette_samples(dist, km.labels_)
        score = sil.mean()
        if score > best_sil:
            best_sil, best_kmeans, best_sil_samples = score, km, sil

    if best_kmeans is None:
        return {0: feats}

    # Group features by cluster label
    clusters = {i: [] for i in range(best_kmeans.n_clusters)}
    for f, lbl in zip(feats, best_kmeans.labels_):
        clusters[lbl].append(f)

    # Recursive re-split: any cluster with avg silhouette < global avg or size > max_cluster_size gets re-clustered
    global_avg = best_sil_samples.mean() if best_sil_samples is not None else 0.0
    out = {}
    cid = 0
    for lbl, members in clusters.items():
        member_indices = [feats.index(m) for m in members]
        member_sil = best_sil_samples[member_indices].mean() if best_sil_samples is not None else 0.0
        should_split = (len(members) > max_cluster_size) or (member_sil < global_avg and len(members) > 2)
        if should_split and len(members) > 2:
            sub_corr = corr.loc[members, members]
            sub_k = min(len(members) - 1, max(2, int(np.ceil(len(members) / max_cluster_size))))
            sub = onc(sub_corr, max_clusters=sub_k, max_cluster_size=max_cluster_size,
                      n_init=n_init, random_state=random_state)
            for sub_members in sub.values():
                out[cid] = sub_members
                cid += 1
        else:
            out[cid] = members
            cid += 1

    return out


def load_pool(etf: str, side: str, suffix: str = "") -> list:
    """Load admitted pool JSON."""
    pool_path = HERE / "data" / f"selected_pool_{etf}_{side}{suffix}.json"
    if not pool_path.exists():
        print(f"[SKIP] Pool file not found: {pool_path}")
        return []
    with open(pool_path, "r") as f:
        return json.load(f)


def build_feature_matrix(df: pd.DataFrame, pool: list, train_end_ts: pd.Timestamp = None) -> tuple:
    """
    Build feature matrix for pool features (handles recipe combos).
    Returns (X_df: pd.DataFrame with feature columns, feature_names: list).
    """
    train_end = train_end_ts if train_end_ts is not None else pd.Timestamp("2022-01-01")
    train_mask = df["date"] < train_end
    train_df = df[train_mask] if train_mask.sum() > 252 else df.iloc[:500]

    train_means, train_stds, train_medians = {}, {}, {}
    for item in pool:
        if "recipe" in item:
            r = item["recipe"]
            for key in ["feature_a", "feature_b", "feature_c", "feature_cond", "feature_cond2"]:
                if key in r:
                    col = r[key]
                    if col not in train_means and col in df.columns:
                        train_means[col] = train_df[col].mean()
                        train_stds[col] = train_df[col].std()
                        train_medians[col] = train_df[col].median()

    feature_data = {}
    feature_names = []
    for item in pool:
        feat_name = item["feature_name"]
        if "recipe" in item:
            val = compute_recipe(df, item["recipe"], train_means, train_stds, train_medians)
        elif feat_name in df.columns:
            val = df[feat_name].values.astype(np.float64)
        else:
            print(f"[WARNING] Feature {feat_name} not found. Skipping.")
            continue
        feature_data[feat_name] = val
        feature_names.append(feat_name)

    X_df = pd.DataFrame(feature_data, index=df.index)
    return X_df, feature_names


def run_clustering(etf: str, side: str, suffix: str = "", max_clusters: int = 10,
                   train_start_str: str = None, train_end_str: str = None) -> dict:
    """
    Full ONC pipeline for one ETF/side.

    Returns cluster assignments dict or None if skipped.
    """
    pool = load_pool(etf, side, suffix)
    if len(pool) < 3:
        print(f"[SKIP] {etf} ({side}) has < 3 features. Clustering not meaningful.")
        return None

    # Determine training window dates
    if not train_start_str or not train_end_str:
        # Check if suffix encodes period (e.g., _p2015_2023)
        import re
        m = re.match(r".*_p(\d{4})_(\d{4})", suffix)
        if m:
            train_start_str, train_end_str = f"{m.group(1)}-01-01", f"{m.group(2)}-01-01"
        else:
            train_start_str, train_end_str = ADAPTIVE_DATES.get(etf, ADAPTIVE_DATES["_default"])

    # Load feature dataset
    features_path = REPO_ROOT / "day-model" / "data" / f"features_{etf}.parquet"
    if not features_path.exists():
        print(f"[SKIP] Feature dataset not found: {features_path}")
        return None

    df = pd.read_parquet(features_path)
    if "date" not in df.columns:
        df = df.reset_index()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Fill base features defensively
    base_cols = [c for c in FEATURES if c in df.columns]
    if base_cols:
        base_med = df[base_cols].median().fillna(0.0)
        df[base_cols] = df[base_cols].ffill().fillna(base_med)

    train_start = pd.Timestamp(train_start_str)
    train_end = pd.Timestamp(train_end_str)

    # Build feature matrix
    X_df, feature_names = build_feature_matrix(df, pool, train_end_ts=train_end)
    if len(feature_names) < 3:
        print(f"[SKIP] {etf} ({side}) has < 3 valid features after build.")
        return None

    # Restrict to training period only (no lookahead)
    train_mask = (df["date"] >= train_start) & (df["date"] < train_end)
    X_train = X_df[train_mask.values]

    if len(X_train) < 100:
        print(f"[SKIP] {etf} ({side}) has < 100 training rows. Cannot cluster reliably.")
        return None

    # Compute Spearman rank correlation matrix
    corr_matrix = X_train.rank().corr()  # Spearman = Pearson on ranks

    # Handle NaN/inf in correlation (constant features)
    corr_matrix = corr_matrix.fillna(0.0)
    corr_vals = corr_matrix.to_numpy().copy()
    np.fill_diagonal(corr_vals, 1.0)
    corr_matrix = pd.DataFrame(corr_vals, index=corr_matrix.index, columns=corr_matrix.columns)

    print(f"\n{'='*60}")
    print(f"ONC Clustering: {etf} ({side}){suffix}")
    print(f"  Features: {len(feature_names)}")
    print(f"  Training rows: {len(X_train)} ({train_start_str} to {train_end_str})")
    print(f"  Max clusters sweep: {max_clusters}")
    print(f"{'='*60}")

    # Run ONC
    clusters = onc(corr_matrix, max_clusters=max_clusters)

    # Compute summary stats
    n_clusters = len(clusters)
    avg_sil = _compute_avg_silhouette(corr_matrix, clusters)

    print(f"\n  Result: {n_clusters} clusters")
    for cid, members in sorted(clusters.items()):
        print(f"    Cluster {cid}: {len(members)} features")
        for m in members[:3]:
            print(f"      - {m}")
        if len(members) > 3:
            print(f"      ... ({len(members) - 3} more)")
    print(f"  Avg silhouette: {avg_sil:.4f}")

    # Build output
    output = {
        "etf": etf,
        "side": side,
        "n_features": len(feature_names),
        "n_clusters": n_clusters,
        "avg_silhouette": round(avg_sil, 4),
        "max_clusters_param": max_clusters,
        "train_period": [train_start_str, train_end_str],
        "clusters": {str(k): v for k, v in clusters.items()},
    }

    # Save
    out_path = HERE / "data" / f"cluster_assignments_{etf}_{side}{suffix}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Saved cluster assignments to {out_path}")

    return output


def _compute_avg_silhouette(corr: pd.DataFrame, clusters: dict) -> float:
    """Compute average silhouette score for final clustering."""
    feats = corr.columns.tolist()
    dist = np.sqrt(0.5 * np.clip(1.0 - corr.values, 0.0, 2.0))
    labels = np.zeros(len(feats), dtype=int)
    for cid, members in clusters.items():
        for m in members:
            if m in feats:
                labels[feats.index(m)] = int(cid)
    if len(set(labels)) < 2:
        return 0.0
    return float(silhouette_samples(dist, labels).mean())


def main():
    parser = argparse.ArgumentParser(description="ONC Feature Clustering for Day-Model pools")
    parser.add_argument("-e", "--etf", type=str, default="all",
                        choices=ALL_ETFS + ["all"],
                        help="Target ETF (default: all)")
    parser.add_argument("-s", "--side", type=str, default="single",
                        choices=["single", "long", "short"],
                        help="Trading side (default: single)")
    parser.add_argument("--max-clusters", type=int, default=10,
                        help="Max clusters to sweep in ONC (default: 10)")
    parser.add_argument("--suffix", type=str, default="",
                        help="Pool file suffix for multi-period runs (e.g., _p2015_2023)")
    parser.add_argument("--train-start", type=str, default=None,
                        help="Optional training start date (YYYY-MM-DD)")
    parser.add_argument("--train-end", type=str, default=None,
                        help="Optional training end date (YYYY-MM-DD)")
    args = parser.parse_args()

    etfs = ALL_ETFS if args.etf == "all" else [args.etf]

    results = {}
    for etf in etfs:
        result = run_clustering(
            etf,
            args.side,
            suffix=args.suffix,
            max_clusters=args.max_clusters,
            train_start_str=args.train_start,
            train_end_str=args.train_end,
        )
        if result:
            results[etf] = result

    # Summary
    print(f"\n{'='*60}")
    print("ONC CLUSTERING SUMMARY")
    print(f"{'='*60}")
    for etf, res in results.items():
        print(f"  {etf}: {res['n_clusters']} clusters, {res['n_features']} features, silhouette={res['avg_silhouette']:.4f}")


if __name__ == "__main__":
    main()
