"""
Task 4: Characterize discovered clusters
- Profile each cluster with paths, features, samples
- Auto-name clusters
- Temporal analysis (transitions, regimes)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'


def load_best_clusters(etf_name):
    """Load best clustering results for an ETF.
    Prefer KMeans (partitions all data) over HDBSCAN (mostly noise)."""
    # Try KMeans first (partitions all data meaningfully)
    candidates = [
        f'clusters_{etf_name}_kmeans_pca.csv',
        f'clusters_{etf_name}_kmeans_ae.csv',
        f'clusters_{etf_name}_kmeans_raw_curves.csv',
        f'clusters_{etf_name}_gmm_pca.csv',
        f'clusters_{etf_name}_gmm_ae.csv',
    ]
    
    for fname in candidates:
        path = DATA_DIR / fname
        if path.exists():
            df = pd.read_csv(path, parse_dates=['date'])
            return df.set_index('date')['cluster'], fname
    
    return None, None


def characterize_cluster_paths(price_curves, dates, cluster_labels, cluster_id):
    """Analyze intraday paths for one cluster"""
    mask = cluster_labels == cluster_id
    cluster_paths = price_curves[mask]
    
    if len(cluster_paths) == 0:
        return None
    
    mean_path = cluster_paths.mean(axis=0)
    std_path = cluster_paths.std(axis=0)
    
    return {
        'mean': mean_path,
        'std': std_path,
        'n_days': len(cluster_paths),
        'paths': cluster_paths
    }


def auto_name_cluster(features_cluster, features_all):
    """Generate descriptive name based on dominant characteristics"""
    overall_mean = features_all.mean()
    overall_std = features_all.std()
    
    cluster_mean = features_cluster.mean()
    
    # Find features that deviate > 1 std from overall mean
    deviations = (cluster_mean - overall_mean) / (overall_std + 1e-10)
    
    # Top 3 most deviated features
    top_feats = deviations.abs().nlargest(3)
    
    name_parts = []
    for feat in top_feats.index:
        dev = deviations[feat]
        if abs(dev) < 0.5:
            continue
        
        if feat == 'gap_pct':
            name_parts.append('Gap-Up' if dev > 0 else 'Gap-Down')
        elif feat == 'intraday_return':
            name_parts.append('Rally' if dev > 0 else 'Selloff')
        elif feat == 'day_range':
            name_parts.append('High-Range' if dev > 0 else 'Low-Range')
        elif feat == 'realized_vol':
            name_parts.append('Volatile' if dev > 0 else 'Calm')
        elif feat == 'path_efficiency':
            name_parts.append('Trending' if dev > 0 else 'Choppy')
        elif feat == 'am_return':
            name_parts.append('AM-Up' if dev > 0 else 'AM-Down')
        elif feat == 'pm_return':
            name_parts.append('PM-Up' if dev > 0 else 'PM-Down')
        elif feat == 'volume_spike_open':
            name_parts.append('Open-Spike' if dev > 0 else 'Quiet-Open')
    
    if not name_parts:
        return 'Neutral'
    
    return ' '.join(name_parts[:2])


def plot_cluster_profiles(etf_name, price_curves, dates, cluster_labels, features_df):
    """Generate comprehensive cluster profile plots"""
    unique_clusters = sorted(set(cluster_labels[cluster_labels >= 0]))
    n_clusters = len(unique_clusters)
    
    if n_clusters == 0:
        print(f"  No clusters to plot for {etf_name}")
        return
    
    # 1) Average intraday paths
    fig, axes = plt.subplots(1, n_clusters, figsize=(5*n_clusters, 4), squeeze=False)
    
    cluster_names = {}
    for i, cid in enumerate(unique_clusters):
        ax = axes[0, i]
        mask = cluster_labels.values == cid
        cluster_paths = price_curves[mask]
        
        mean_path = cluster_paths.mean(axis=0)
        std_path = cluster_paths.std(axis=0)
        
        # Plot mean +/- std
        x = np.arange(48)
        ax.plot(x, mean_path, 'b-', linewidth=2, label='Mean')
        ax.fill_between(x, mean_path - std_path, mean_path + std_path, alpha=0.3, color='blue')
        
        # Auto-name
        cluster_feats = features_df.iloc[mask]
        name = auto_name_cluster(cluster_feats, features_df)
        cluster_names[cid] = name
        
        ax.set_title(f'Cluster {cid}: {name}\n({mask.sum()} days, {mask.mean()*100:.1f}%)')
        ax.set_xlabel('Bar Index (0=9:30, 24=13:00, 47=15:00)')
        ax.set_ylabel('Normalized Price')
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(24, color='red', linestyle=':', alpha=0.5, label='Lunch')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_profiles_{etf_name}.png', dpi=150)
    plt.close()
    
    # 2) Feature distributions (violin plots)
    key_features = ['gap_pct', 'intraday_return', 'day_range', 'realized_vol', 'path_efficiency']
    fig, axes = plt.subplots(len(key_features), 1, figsize=(10, 3*len(key_features)))
    
    for i, feat in enumerate(key_features):
        ax = axes[i]
        data_by_cluster = [features_df.loc[cluster_labels == cid, feat].values 
                          for cid in unique_clusters]
        
        parts = ax.violinplot(data_by_cluster, positions=range(len(unique_clusters)), 
                             showmeans=True, showmedians=True)
        
        ax.set_xticks(range(len(unique_clusters)))
        ax.set_xticklabels([f'C{cid}\n{cluster_names[cid]}' for cid in unique_clusters])
        ax.set_ylabel(feat)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_violins_{etf_name}.png', dpi=100)
    plt.close()
    
    # 3) Sample days (5 representative examples per cluster)
    fig, axes = plt.subplots(n_clusters, 5, figsize=(15, 3*n_clusters), squeeze=False)
    
    for i, cid in enumerate(unique_clusters):
        mask = cluster_labels.values == cid
        cluster_paths = price_curves[mask]
        
        # Pick 5 random samples (or all if < 5)
        n_samples = min(5, len(cluster_paths))
        if n_samples > 0:
            sample_idx = np.random.choice(len(cluster_paths), size=n_samples, replace=False)
            
            for j, idx in enumerate(sample_idx):
                ax = axes[i, j]
                ax.plot(cluster_paths[idx], alpha=0.7)
                ax.axhline(0, color='gray', linestyle='--', alpha=0.3)
                ax.axvline(24, color='red', linestyle=':', alpha=0.3)
                ax.set_title(f'Cluster {cid} - Sample {j+1}')
                ax.set_xlabel('Bar Index')
                if j == 0:
                    ax.set_ylabel('Norm Price')
                ax.grid(True, alpha=0.3)
        
        # Fill empty slots
        for j in range(n_samples, 5):
            axes[i, j].axis('off')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_samples_{etf_name}.png', dpi=100)
    plt.close()
    
    return cluster_names


def plot_temporal_analysis(etf_name, dates, cluster_labels, cluster_names):
    """Temporal analysis: calendar heatmap, transitions, regimes"""
    
    # Filter noise
    mask = cluster_labels >= 0
    dates_clean = dates[mask]
    labels_clean = cluster_labels[mask]
    
    if len(labels_clean) < 10:
        print(f"  Not enough data for temporal analysis")
        return
    
    df = pd.DataFrame({'date': dates_clean, 'cluster': labels_clean})
    df = df.set_index('date').sort_index()
    
    # 1) Calendar heatmap (year x month)
    df['year'] = df.index.year
    df['month'] = df.index.month
    
    pivot = df.groupby(['year', 'month'])['cluster'].apply(
        lambda x: x.mode().iloc[0] if len(x) > 0 else -1
    ).unstack(fill_value=-1)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, cmap='Set3', cbar_kws={'label': 'Dominant Cluster'}, ax=ax)
    ax.set_title(f'Cluster Calendar Heatmap ({etf_name})')
    ax.set_ylabel('Year')
    ax.set_xlabel('Month')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_calendar_{etf_name}.png', dpi=100)
    plt.close()
    
    # 2) Transition matrix
    unique_clusters = sorted(set(labels_clean))
    n_clusters = len(unique_clusters)
    
    trans_matrix = np.zeros((n_clusters, n_clusters))
    cluster_to_idx = {c: i for i, c in enumerate(unique_clusters)}
    
    for i in range(len(labels_clean) - 1):
        c1 = labels_clean.iloc[i]
        c2 = labels_clean.iloc[i + 1]
        if c1 in cluster_to_idx and c2 in cluster_to_idx:
            trans_matrix[cluster_to_idx[c1], cluster_to_idx[c2]] += 1
    
    # Normalize rows
    row_sums = trans_matrix.sum(axis=1, keepdims=True)
    trans_prob = trans_matrix / (row_sums + 1e-10)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(trans_prob, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=[f'C{c}\n{cluster_names.get(c, "")}' for c in unique_clusters],
                yticklabels=[f'C{c}\n{cluster_names.get(c, "")}' for c in unique_clusters],
                ax=ax)
    ax.set_title(f'Cluster Transition Probabilities ({etf_name})')
    ax.set_ylabel('From Cluster')
    ax.set_xlabel('To Cluster')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_transitions_{etf_name}.png', dpi=100)
    plt.close()
    
    # 3) Rolling regime (60-day window)
    window = 60
    rolling_props = []
    
    for i in range(window, len(labels_clean)):
        window_labels = labels_clean.iloc[i-window:i]
        props = window_labels.value_counts(normalize=True)
        rolling_props.append(props)
    
    df_rolling = pd.DataFrame(rolling_props, index=dates_clean[window:])
    df_rolling = df_rolling.fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    df_rolling.plot(kind='area', stacked=True, alpha=0.7, ax=ax, colormap='Set3')
    ax.set_title(f'Rolling Cluster Proportions (60-day window, {etf_name})')
    ax.set_ylabel('Proportion')
    ax.set_xlabel('Date')
    ax.legend([f'C{c} {cluster_names.get(c, "")}' for c in df_rolling.columns], 
              bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_regimes_{etf_name}.png', dpi=100, bbox_inches='tight')
    plt.close()


def process_etf(etf_name):
    """Characterize clusters for one ETF"""
    print(f"\n{'='*60}")
    print(f"Characterizing Clusters: {etf_name}")
    print('='*60)
    
    # Load data
    cluster_labels, cluster_file = load_best_clusters(etf_name)
    if cluster_labels is None:
        print(f"  [SKIP] No cluster file found")
        return
    
    print(f"  Loaded: {cluster_file}")
    
    paths_npz = np.load(OUTPUT_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    features_df = pd.read_csv(OUTPUT_DIR / f'features_{etf_name}.csv', index_col='date', parse_dates=True)
    
    price_curves = paths_npz['price']
    dates = pd.to_datetime(paths_npz['dates'])
    
    # Align
    common_dates = cluster_labels.index.intersection(features_df.index).intersection(dates)
    cluster_labels = cluster_labels.loc[common_dates]
    features_df = features_df.loc[common_dates]
    
    # Map dates to indices
    date_to_idx = {d: i for i, d in enumerate(dates)}
    valid_idx = [date_to_idx[d] for d in common_dates if d in date_to_idx]
    price_curves = price_curves[valid_idx]
    dates = dates[valid_idx]
    
    print(f"  Aligned: {len(common_dates)} days")
    
    # Cluster distribution
    cluster_counts = cluster_labels.value_counts().sort_index()
    print(f"\n  Cluster distribution:")
    for cid, count in cluster_counts.items():
        print(f"    Cluster {cid}: {count} days ({count/len(cluster_labels)*100:.1f}%)")
    
    # Plot profiles
    print("\n  Generating profile plots...")
    cluster_names = plot_cluster_profiles(etf_name, price_curves, dates, cluster_labels, features_df)
    
    # Temporal analysis
    if cluster_names:
        print("  Generating temporal analysis plots...")
        plot_temporal_analysis(etf_name, dates, cluster_labels, cluster_names)
    
    return cluster_names


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    
    print("Cluster Characterization")
    print("=" * 60)
    
    all_names = {}
    
    for etf_name in ETF_NAMES:
        try:
            names = process_etf(etf_name)
            if names:
                all_names[etf_name] = names
        except Exception as e:
            print(f"  [ERROR] {etf_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("Summary: Cluster Names")
    print("="*60)
    for etf_name, names in all_names.items():
        print(f"\n  {etf_name}:")
        for cid, name in names.items():
            print(f"    Cluster {cid}: {name}")
    
    print("\nCluster characterization complete!")


if __name__ == '__main__':
    main()
