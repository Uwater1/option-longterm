#!/usr/bin/env python3
"""
Feature Correlation Diagnostic & Hierarchical Clustering Map for NewTrade.

Diagnoses pairwise correlations among features passed from day-model-new admitted pools.
Key capabilities:
  1. Computes raw or standardized (expanding z-score) & signed feature correlation matrix.
  2. Applies Ward/Average linkage hierarchical clustering to group similar features together.
  3. Draws and saves pairwise correlation heatmap with cluster dendrogram.
  4. Analyzes highly correlated pairs (|r| >= threshold) and effective independent feature dimensions (PCA).
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
import scipy.cluster.hierarchy as sch

# Path resolution
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

# Append day-model-new and utils paths
sys.path.append(str(REPO_ROOT / "day-model-new"))
sys.path.append(str(REPO_ROOT / "day-model-new" / "mining"))
sys.path.append(str(REPO_ROOT / "day-model"))

from utils import (
    load_admitted_pool,
    load_etf_dataset,
    build_pool_feature_matrix,
    expanding_zscore_numba,
)


def compute_correlation_matrix(
    df: pd.DataFrame,
    pool: list,
    standardize: bool = True,
    signed: bool = True,
    method: str = "pearson",
) -> tuple[pd.DataFrame, list[str], np.ndarray]:
    """
    Build feature matrix and compute pairwise correlation matrix.
    
    Returns:
      - df_corr: pd.DataFrame shape (N, N) correlation matrix
      - feature_names: list of feature names
      - signs: np.ndarray shape (N,)
    """
    X_raw, signs, feature_names = build_pool_feature_matrix(df, pool)
    if X_raw.shape[1] == 0:
        return pd.DataFrame(), [], np.array([])

    # Apply expanding z-score standardization if requested
    if standardize:
        burn_in = 252 if len(df) > 500 else 100
        X_mat = expanding_zscore_numba(X_raw, burn_in=burn_in, clip=3.0)
    else:
        X_mat = X_raw.copy()

    # Align feature sign if requested (so positive means positive signal direction)
    if signed:
        X_mat = X_mat * signs

    df_feats = pd.DataFrame(X_mat, columns=feature_names)
    
    # Calculate correlation matrix
    df_corr = df_feats.corr(method=method).fillna(0.0)
    
    return df_corr, feature_names, signs


def cluster_correlation_matrix(
    df_corr: pd.DataFrame,
    cluster_method: str = "ward"
) -> tuple[pd.DataFrame, list[int], np.ndarray]:
    """
    Perform hierarchical clustering on correlation matrix to group similar features together.
    
    Returns:
      - df_corr_reordered: pd.DataFrame with features reordered by dendrogram leaf order
      - reordered_indices: list of reordered leaf indices
      - Z_linkage: linkage matrix from scipy.cluster.hierarchy
    """
    if df_corr.empty or len(df_corr) <= 1:
        return df_corr, list(range(len(df_corr))), np.array([])

    corr = df_corr.values
    # Ensure symmetry & numerical stability
    corr = (corr + corr.T) / 2.0
    np.fill_diagonal(corr, 1.0)
    
    # Distance metric: d(x, y) = sqrt(2 * (1 - r))
    # Clip correlation to [-1, 1] defensively
    corr_clipped = np.clip(corr, -1.0, 1.0)
    dist = np.sqrt(np.maximum(0.0, 2.0 * (1.0 - corr_clipped)))
    
    # Convert square distance matrix to condensed vector form for scipy linkage
    condensed_dist = squareform(dist, checks=False)
    
    # Linkage algorithm (ward requires euclidean-like metric)
    if cluster_method.lower() == "ward":
        Z_linkage = sch.linkage(condensed_dist, method="ward")
    else:
        Z_linkage = sch.linkage(condensed_dist, method=cluster_method.lower())

    # Get reordered leaf indices from dendrogram
    dendro = sch.dendrogram(Z_linkage, no_plot=True)
    reordered_idx = dendro["leaves"]

    # Reorder correlation matrix
    df_corr_reordered = df_corr.iloc[reordered_idx, reordered_idx]

    return df_corr_reordered, reordered_idx, Z_linkage


def format_feature_shorthand(col_name: str) -> str:
    """
    Convert verbose feature name into clean, compact mathematical shorthand notation.
    """
    s = col_name
    # Shorten common long component tokens
    token_map = {
        "combo_": "",
        "rbreaker_sell_setup_proximity_early": "rbreaker_sell",
        "rbreaker_buy_setup_proximity_early": "rbreaker_buy",
        "star50_limit_proximity_early": "star50_limit",
        "volume_weighted_momentum_acceleration": "vol_mom_accel",
        "demark_setup_reversal_early": "demark_revers",
        "close_vs_open_range": "close_open_rng",
        "first_bar_sentiment": "first_bar_sent",
        "first_bar_return": "first_bar_ret",
        "early_body_momentum": "early_body_mom",
        "bar_body_rng_0": "bar_body",
        "bar_ret_0": "bar_ret_0",
        "max_up_ret": "max_up_ret",
        "max_down_ret": "max_down_ret",
        "net_volume_flow": "vol_flow",
    }
    
    for k, v in token_map.items():
        s = s.replace(k, v)

    # Format combo operations op__a__b -> op(a, b)
    if "__" in s:
        parts = s.split("__")
        op = parts[0]
        args = ", ".join(parts[1:])
        return f"{op}({args})"
    
    return s


def plot_pairwise_correlation_map(
    df_corr_reordered: pd.DataFrame,
    Z_linkage: np.ndarray,
    etf: str,
    side: str,
    output_path: Path,
    cluster_method: str = "ward",
    show_labels: bool = True
):
    """
    Draw & save ultra-readable pairwise correlation heatmap with hierarchical clustering dendrogram.
    """
    n_feats = len(df_corr_reordered)
    if n_feats <= 1:
        print(f"[SKIP] {etf} ({side}) has only {n_feats} feature (< 2 required for pairwise correlation map).")
        return

    # Build index labels F01..FN and compact formula shorthands
    f_indices = [f"F{i+1:02d}" for i in range(n_feats)]
    shorthands = [format_feature_shorthand(col) for col in df_corr_reordered.columns]
    
    # Tick labels combine index and compact formula: e.g. "F01: tri_min(rbreaker_sell, max_up_ret)"
    tick_labels = [f"[{idx}] {st}" for idx, st in zip(f_indices, shorthands)]

    # Dynamic plot dimensions
    if n_feats <= 12:
        cell_size = 0.8
        annot_font = 9
    elif n_feats <= 25:
        cell_size = 0.55
        annot_font = 7.5
    else:
        cell_size = 0.45
        annot_font = 6.0

    fig_w = max(12, min(24, n_feats * cell_size + 6))
    fig_h = max(10, min(22, n_feats * cell_size + 4))

    plt.rcParams["font.family"] = "DejaVu Sans"
    
    # Render Clustermap
    grid = sns.clustermap(
        df_corr_reordered,
        row_linkage=Z_linkage if len(Z_linkage) > 0 else None,
        col_linkage=Z_linkage if len(Z_linkage) > 0 else None,
        cmap="vlag",  # Red-blue diverging colormap
        vmin=-1.0,
        vmax=1.0,
        center=0.0,
        annot=n_feats <= 35,  # Display correlation values inside cells
        fmt=".2f",
        annot_kws={"size": annot_font, "weight": "bold"},
        linewidths=0.6,
        linecolor="#ffffff",
        figsize=(fig_w, fig_h),
        cbar_pos=(0.92, 0.3, 0.02, 0.4),  # Move vertical colorbar to right margin to prevent overlap
        cbar_kws={"label": "Pairwise Correlation (r)"},
        dendrogram_ratio=(0.12, 0.12),
    )

    grid.fig.suptitle(
        f"Feature Pairwise Correlation Map — {etf} ({side.upper()} Pool)\nHierarchical Grouping ({cluster_method.title()} Linkage, N={n_feats})",
        fontsize=14,
        fontweight="bold",
        y=1.02,
    )

    if show_labels:
        grid.ax_heatmap.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=9, fontweight="medium")
        grid.ax_heatmap.set_yticklabels(tick_labels, rotation=0, fontsize=9, fontweight="medium")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[PLOT SAVED] Clustered Correlation Map saved to {output_path}")


def analyze_correlation_structure(
    df_corr: pd.DataFrame,
    threshold: float = 0.70
) -> pd.DataFrame:
    """
    Extract diagnostic statistics on correlation structure:
    - Highly correlated pairs (|r| >= threshold)
    - Off-diagonal statistics
    """
    if df_corr.empty or len(df_corr) <= 1:
        return pd.DataFrame()

    feats = df_corr.columns.tolist()
    n = len(feats)
    
    pair_rows = []
    corr_mat = df_corr.values

    for i in range(n):
        for j in range(i + 1, n):
            r = corr_mat[i, j]
            if abs(r) >= threshold:
                pair_rows.append({
                    "feature_1": feats[i],
                    "feature_2": feats[j],
                    "corr": round(float(r), 4),
                    "abs_corr": round(float(abs(r)), 4),
                })

    df_pairs = pd.DataFrame(pair_rows)
    if not df_pairs.empty:
        df_pairs = df_pairs.sort_values("abs_corr", ascending=False).reset_index(drop=True)

    return df_pairs


def run_correlation_diagnosis(
    etf: str,
    side: str = "single",
    standardize: bool = True,
    signed: bool = True,
    method: str = "pearson",
    cluster_method: str = "ward",
    threshold: float = 0.70,
    artifacts_dir: Path = None,
):
    pool = load_admitted_pool(etf, side=side, min_features=1)
    if not pool:
        print(f"[SKIP] {etf} ({side}) has no admitted features.")
        return

    df = load_etf_dataset(etf)
    df_corr, feature_names, signs = compute_correlation_matrix(
        df, pool, standardize=standardize, signed=signed, method=method
    )

    if df_corr.empty:
        print(f"[SKIP] Empty feature matrix for {etf} ({side}).")
        return

    # Perform clustering
    df_corr_reordered, reordered_idx, Z_linkage = cluster_correlation_matrix(
        df_corr, cluster_method=cluster_method
    )

    # Calculate summary metrics
    corr_vals = df_corr.values
    upper_tri_indices = np.triu_indices_from(corr_vals, k=1)
    off_diag_corrs = corr_vals[upper_tri_indices]
    
    mean_abs_corr = np.mean(np.abs(off_diag_corrs)) if len(off_diag_corrs) > 0 else 0.0
    max_abs_corr = np.max(np.abs(off_diag_corrs)) if len(off_diag_corrs) > 0 else 0.0
    
    n_pairs_high = np.sum(np.abs(off_diag_corrs) >= threshold)
    n_pairs_very_high = np.sum(np.abs(off_diag_corrs) >= 0.85)
    n_pairs_extreme = np.sum(np.abs(off_diag_corrs) >= 0.95)

    print("=" * 80)
    print(f"FEATURE CORRELATION DIAGNOSIS — {etf} ({side.upper()} Pool)")
    print("=" * 80)
    print(f"Total Admitted Features : {len(feature_names)}")
    print(f"Total Pairwise Comparisons: {len(off_diag_corrs)}")
    print(f"Mean Pairwise |r|        : {mean_abs_corr:.4f}")
    print(f"Max Pairwise |r|         : {max_abs_corr:.4f}")
    print(f"High Correlation Pairs (|r| >= {threshold}): {n_pairs_high}")
    print(f"Very High Pairs (|r| >= 0.85): {n_pairs_very_high}")
    print(f"Extreme Pairs   (|r| >= 0.95): {n_pairs_extreme}")

    # Analyze highly correlated pairs table
    df_pairs = analyze_correlation_structure(df_corr, threshold=threshold)
    if not df_pairs.empty:
        print(f"\n--- Top Correlated Feature Pairs (|r| >= {threshold}) ---")
        print(df_pairs.head(15).to_string(index=False))
    else:
        print(f"\nNo feature pairs found with |r| >= {threshold}.")

    # Save visualization map
    if artifacts_dir is None:
        artifacts_dir = HERE / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    out_png = artifacts_dir / f"correlation_{etf}_{side}.png"
    plot_pairwise_correlation_map(
        df_corr_reordered,
        Z_linkage,
        etf=etf,
        side=side,
        output_path=out_png,
        cluster_method=cluster_method,
    )

    # Save summary CSV artifacts
    if not df_pairs.empty:
        out_csv = artifacts_dir / f"high_corr_pairs_{etf}_{side}.csv"
        df_pairs.to_csv(out_csv, index=False)
        print(f"[CSV SAVED] High correlation pairs exported to {out_csv}")


ETF_ALIAS_MAP = {
    "300": "300ETF",
    "300etf": "300ETF",
    "500": "500ETF",
    "500etf": "500ETF",
    "50": "50ETF",
    "50etf": "50ETF",
    "588000": "588000ETF",
    "588000etf": "588000ETF",
    "159915": "159915ETF",
    "159915etf": "159915ETF",
    "159914": "159915ETF",  # Common typo alias for Chinext 159915
    "159914etf": "159915ETF",
}


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose feature correlation & hierarchical clustering for NewTrade."
    )
    parser.add_argument("-e", "--etf", type=str, default="300ETF", help="Target ETF (300ETF, 500ETF, 50ETF, 588000ETF, 159915ETF, or 'all')")
    parser.add_argument("--side", type=str, default="single", choices=["single", "pair", "all"], help="Admitted pool side ('single', 'pair', or 'all')")
    parser.add_argument("--no-standardize", action="store_true", help="Disable expanding z-score standardization (use raw features)")
    parser.add_argument("--no-signed", action="store_true", help="Disable sign alignment (use unadjusted feature signs)")
    parser.add_argument("--method", type=str, default="pearson", choices=["pearson", "spearman"], help="Correlation calculation method")
    parser.add_argument("--cluster-method", type=str, default="ward", choices=["ward", "average", "complete", "single"], help="Hierarchical clustering linkage method")
    parser.add_argument("--threshold", type=float, default=0.70, help="Cutoff threshold for reporting highly correlated pairs")

    args = parser.parse_args()

    if args.etf.lower() == "all":
        etfs = ["300ETF", "500ETF", "50ETF", "588000ETF", "159915ETF"]
    else:
        norm_etf = ETF_ALIAS_MAP.get(args.etf.lower(), args.etf)
        etfs = [norm_etf]

    sides = ["single", "pair"] if args.side.lower() == "all" else [args.side]

    for etf in etfs:
        for side in sides:
            run_correlation_diagnosis(
                etf=etf,
                side=side,
                standardize=not args.no_standardize,
                signed=not args.no_signed,
                method=args.method,
                cluster_method=args.cluster_method,
                threshold=args.threshold,
            )


if __name__ == "__main__":
    main()
