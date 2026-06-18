"""
Task 4: Characterize discovered clusters
- Profile each cluster with paths, features, samples
- Auto-name clusters (z-score profiling)
- Feature discrimination scoring (ANOVA F, mutual information)
- Temporal analysis (transitions, regimes)
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import json
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.feature_selection import mutual_info_classif

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'


def load_best_clusters(etf_name):
    """Load best clustering results for an ETF.
    Prefer KMeans (partitions all data) over HDBSCAN (mostly noise).
    Returns macro labels (K=3) from kmeans_pca (updated by discover_patterns)."""
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


def load_sub_clusters(etf_name):
    """Load sub-cluster (hierarchical) labels for an ETF.

    Returns Series of str labels like '0.0', '0.1', '1.0', indexed by date,
    or (None, None) if file not found.
    """
    path = DATA_DIR / f'clusters_{etf_name}_sub.csv'
    if not path.exists():
        return None, None
    df = pd.read_csv(path, parse_dates=['date'])
    return df.set_index('date')['cluster'].astype(str), str(path.name)


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
    """Generate descriptive name based on z-score deviation from overall mean.

    Returns (name: str, top_feats: list of (feat_name, z_score)).
    """
    overall_mean = features_all.mean(numeric_only=True)
    overall_std = features_all.std(numeric_only=True)
    cluster_mean = features_cluster.mean(numeric_only=True)

    # z-score per feature
    deviations = (cluster_mean - overall_mean) / (overall_std + 1e-10)
    top_feats = deviations.abs().nlargest(5)

    name_parts = []
    top_feat_list = []
    for feat in top_feats.index:
        dev = deviations[feat]
        top_feat_list.append((feat, float(dev)))
        if abs(dev) < 1.0:
            continue
        name_parts.append(_feat_label(feat, dev))

    name = ' '.join(name_parts[:2]) if name_parts else 'Neutral'
    return name, top_feat_list


def _feat_label(feat, dev):
    """Map (feature, signed deviation) to a human-readable token."""
    mapping = {
        'gap_pct':           ('Gap-Up',      'Gap-Down'),
        'intraday_return':   ('Rally',       'Selloff'),
        'day_range':         ('High-Range',  'Low-Range'),
        'realized_vol':      ('Volatile',    'Calm'),
        'path_efficiency':   ('Trending',    'Choppy'),
        'am_return':         ('AM-Up',       'AM-Down'),
        'pm_return':         ('PM-Up',       'PM-Down'),
        'volume_spike_open': ('Open-Spike',  'Quiet-Open'),
        'max_drawdown_intra':('Shallow-DD',  'Deep-DD'),
        'max_rally_intra':   ('Strong-Rally','Weak-Rally'),
        'first_30min_return':('Fast-Open',   'Slow-Open'),
        'last_30min_return': ('Late-Push',   'Fade-Close'),
        'volume_ratio_am_pm':('AM-Heavy-Vol','PM-Heavy-Vol'),
        'vol_of_vol':        ('Vol-Accel',   'Vol-Stable'),
    }
    pos, neg = mapping.get(feat, (feat, feat))
    return pos if dev > 0 else neg


def compute_feature_discrimination(etf_name, cluster_labels, features_df, level='macro'):
    """Compute ANOVA F-test, mutual information, z-score heatmap, and auto-profiles.

    Parameters
    ----------
    level : str
        'macro' or 'sub' — controls saved filenames and z-score reference.

    Returns dict with discrimination summary; saves JSON + plots.
    """
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
    unique_clusters = sorted(cluster_labels.unique())
    n_clusters = len(unique_clusters)

    # --- ANOVA F-test per feature ---
    anova_results = {}
    for feat in numeric_cols:
        groups = [features_df.loc[cluster_labels == c, feat].dropna().values for c in unique_clusters]
        groups = [g for g in groups if len(g) > 1]
        if len(groups) >= 2:
            f_stat, p_val = stats.f_oneway(*groups)
            anova_results[feat] = {'F': float(f_stat), 'p': float(p_val)}
        else:
            anova_results[feat] = {'F': 0.0, 'p': 1.0}

    mean_f = np.mean([v['F'] for v in anova_results.values()])

    # --- Mutual information ---
    from sklearn.preprocessing import LabelEncoder
    X = features_df[numeric_cols].fillna(0).values
    le = LabelEncoder()
    y_labels = le.fit_transform(cluster_labels.values.astype(str))
    mi_scores = mutual_info_classif(X, y_labels, random_state=42)
    mi_dict = {feat: float(s) for feat, s in zip(numeric_cols, mi_scores)}
    total_mi = float(np.sum(mi_scores))

    # --- Z-score profiles per cluster ---
    overall_mean = features_df[numeric_cols].mean()
    overall_std = features_df[numeric_cols].std()
    z_profiles = {}
    cluster_names = {}
    for c in unique_clusters:
        mask = cluster_labels == c
        cluster_feats = features_df.loc[mask, numeric_cols]
        z = (cluster_feats.mean() - overall_mean) / (overall_std + 1e-10)
        # Use str key so both int and str labels work
        ckey = str(c)
        z_profiles[ckey] = {feat: float(z[feat]) for feat in numeric_cols}

        name, top = auto_name_cluster(cluster_feats, features_df[numeric_cols])
        cluster_names[ckey] = name

    # Unique auto-names count
    unique_names = len(set(cluster_names.values()))

    discrimination = {
        'etf': etf_name,
        'n_clusters': n_clusters,
        'mean_anova_F': mean_f,
        'total_mi': total_mi,
        'unique_auto_names': unique_names,
        'per_feature_anova': anova_results,
        'per_feature_mi': mi_dict,
        'cluster_z_profiles': z_profiles,
        'cluster_names': cluster_names,
    }

    out_path = DATA_DIR / f'cluster_discrimination_{etf_name}{"_sub" if level == "sub" else ""}.json'
    with open(out_path, 'w') as f:
        json.dump(discrimination, f, indent=2, default=str)
    print(f"  Saved discrimination scorecard: {out_path}")

    # --- Plot: z-score heatmap ---
    z_matrix = pd.DataFrame(z_profiles).T  # rows=clusters, cols=features
    z_matrix.index.name = 'Cluster'
    # Sort index for sub-clusters (string sort: "0.0", "0.1", "1.0" ...)
    z_matrix = z_matrix.sort_index()

    ylabels = [f"C{c}: {cluster_names.get(str(c), '')}" 
               for c in z_matrix.index]

    fig, ax = plt.subplots(figsize=(max(10, len(numeric_cols) * 0.5), max(4, n_clusters * 0.6)))
    sns.heatmap(
        z_matrix, annot=True, fmt='.1f', cmap='RdBu_r', center=0,
        xticklabels=numeric_cols,
        yticklabels=ylabels,
        ax=ax, cbar_kws={'label': 'z-score'},
        annot_kws={'size': 7},
    )
    ax.set_title(f'Cluster Feature Profiles (z-scores) — {etf_name} [{level}]')
    ax.tick_params(axis='x', rotation=45, labelsize=7)
    ax.tick_params(axis='y', rotation=0, labelsize=8)
    plt.tight_layout()
    suffix = '_sub' if level == 'sub' else '_macro'
    plt.savefig(PLOTS_DIR / f'cluster_zscore_heatmap_{etf_name}{suffix}.png', dpi=120)
    plt.close()

    # --- Plot: ANOVA F bar chart ---
    f_vals = [anova_results[f]['F'] for f in numeric_cols]
    fig, ax = plt.subplots(figsize=(max(10, len(numeric_cols) * 0.4), 5))
    colors = ['steelblue' if v < np.percentile(f_vals, 75) else 'orange' for v in f_vals]
    ax.barh(numeric_cols, f_vals, color=colors)
    ax.set_xlabel('ANOVA F-statistic (higher = more discriminative)')
    ax.set_title(f'Per-Feature Cluster Discrimination (ANOVA F) — {etf_name} [{level}]')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_anova_f_{etf_name}{suffix}.png', dpi=120)
    plt.close()

    return discrimination


def plot_cluster_profiles(etf_name, price_curves, dates, cluster_labels, features_df, level='macro'):
    """Generate comprehensive cluster profile plots.

    Parameters
    ----------
    level : str
        'macro' or 'sub' — controls plot filenames and label handling.
    """
    # Filter valid labels (int >= 0 for macro, non-empty str for sub)
    if cluster_labels.dtype == object:
        valid_mask = cluster_labels.notna() & (cluster_labels.astype(str).str.len() > 0)
    else:
        valid_mask = cluster_labels >= 0
    unique_clusters = sorted(set(cluster_labels[valid_mask]))
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
        name, _ = auto_name_cluster(cluster_feats, features_df)
        cluster_names[cid] = name
        
        ax.set_title(f'Cluster {cid}: {name}\n({mask.sum()} days, {mask.mean()*100:.1f}%)')
        ax.set_xlabel('Bar Index (0=9:30, 24=13:00, 47=15:00)')
        ax.set_ylabel('Normalized Price')
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(24, color='red', linestyle=':', alpha=0.5, label='Lunch')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    
    plt.tight_layout()
    suffix = '_sub' if level == 'sub' else '_macro'
    plt.savefig(PLOTS_DIR / f'cluster_profiles_{etf_name}{suffix}.png', dpi=150)
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
    plt.savefig(PLOTS_DIR / f'cluster_violins_{etf_name}{suffix}.png', dpi=100)
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
    plt.savefig(PLOTS_DIR / f'cluster_samples_{etf_name}{suffix}.png', dpi=100)
    plt.close()
    
    return cluster_names


def plot_temporal_analysis(etf_name, dates, cluster_labels, cluster_names, level='macro'):
    """Temporal analysis: calendar heatmap, transitions, regimes"""
    
    # Filter noise
    if cluster_labels.dtype == object:
        mask = cluster_labels.notna() & (cluster_labels.astype(str).str.len() > 0)
    else:
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
    suffix = '_sub' if level == 'sub' else '_macro'
    plt.savefig(PLOTS_DIR / f'cluster_calendar_{etf_name}{suffix}.png', dpi=100)
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
    suffix = '_sub' if level == 'sub' else '_macro'
    plt.savefig(PLOTS_DIR / f'cluster_transitions_{etf_name}{suffix}.png', dpi=100)
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
    plt.savefig(PLOTS_DIR / f'cluster_regimes_{etf_name}{suffix}.png', dpi=100, bbox_inches='tight')
    plt.close()


def process_etf(etf_name):
    """Characterize clusters for one ETF (macro + sub levels)."""
    print(f"\n{'='*60}")
    print(f"Characterizing Clusters: {etf_name}")
    print('='*60)
    
    # Load macro labels (K=3)
    cluster_labels, cluster_file = load_best_clusters(etf_name)
    if cluster_labels is None:
        print(f"  [SKIP] No cluster file found")
        return None, None, None, None
    
    # Load sub-cluster labels (may be None if not yet generated)
    sub_labels, sub_file = load_sub_clusters(etf_name)
    
    print(f"  Loaded macro: {cluster_file}")
    if sub_file:
        print(f"  Loaded sub:   {sub_file}")
    
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv', index_col='date', parse_dates=True)
    
    price_curves = paths_npz['price']
    dates = pd.to_datetime(paths_npz['dates'])
    
    # Align on common dates (macro always present)
    common_dates = cluster_labels.index.intersection(features_df.index).intersection(dates)
    cluster_labels = cluster_labels.loc[common_dates]
    features_df = features_df.loc[common_dates]
    if sub_labels is not None:
        sub_common = sub_labels.index.intersection(common_dates)
        sub_labels = sub_labels.loc[sub_common]
    
    # Map dates to indices
    date_to_idx = {d: i for i, d in enumerate(dates)}
    valid_idx = [date_to_idx[d] for d in common_dates if d in date_to_idx]
    price_curves = price_curves[valid_idx]
    dates = dates[valid_idx]
    
    print(f"  Aligned: {len(common_dates)} days")
    
    # ---- MACRO LEVEL ----
    print("\n  [MACRO LEVEL] Cluster distribution:")
    cluster_counts = cluster_labels.value_counts().sort_index()
    for cid, count in cluster_counts.items():
        print(f"    Cluster {cid}: {count} days ({count/len(cluster_labels)*100:.1f}%)")
    
    print("  [MACRO] Computing feature discrimination scores...")
    discrimination_macro = compute_feature_discrimination(
        etf_name, cluster_labels, features_df, level='macro'
    )

    print("  [MACRO] Generating profile plots...")
    macro_names = plot_cluster_profiles(
        etf_name, price_curves, dates, cluster_labels, features_df, level='macro'
    )

    if macro_names:
        print("  [MACRO] Generating temporal analysis plots...")
        plot_temporal_analysis(etf_name, dates, cluster_labels, macro_names, level='macro')

    # ---- SUB LEVEL ----
    sub_names = None
    discrimination_sub = None
    if sub_labels is not None and len(sub_labels) > 0:
        # Align sub_labels to same date index as macro
        sub_dates = sub_labels.index.intersection(cluster_labels.index)
        sub_labels = sub_labels.loc[sub_dates]

        print("\n  [SUB LEVEL] Cluster distribution:")
        sub_counts = sub_labels.value_counts().sort_index()
        for cid, count in sub_counts.items():
            print(f"    Sub-cluster {cid}: {count} days ({count/len(sub_labels)*100:.1f}%)")

        print("  [SUB] Computing feature discrimination scores...")
        discrimination_sub = compute_feature_discrimination(
            etf_name, sub_labels, features_df.loc[sub_dates], level='sub'
        )

        # Build sub-cluster index array aligned with price_curves
        sub_aligned = pd.Series(index=cluster_labels.index, dtype=object)
        sub_aligned.loc[sub_dates] = sub_labels
        # Fill unmatched with empty string (will be filtered in plot functions)
        sub_aligned = sub_aligned.fillna('')

        print("  [SUB] Generating profile plots...")
        sub_names = plot_cluster_profiles(
            etf_name, price_curves, dates, sub_aligned, features_df, level='sub'
        )

    return macro_names, discrimination_macro, sub_names, discrimination_sub


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    
    print("Cluster Characterization")
    print("=" * 60)
    
    all_macro_names = {}
    all_sub_names = {}
    all_macro_disc = {}
    all_sub_disc = {}

    for etf_name in ETF_NAMES:
        try:
            result = process_etf(etf_name)
            if result[0] is not None:
                macro_names, disc_macro, sub_names, disc_sub = result
                all_macro_names[etf_name] = macro_names
                all_macro_disc[etf_name] = disc_macro
                if sub_names:
                    all_sub_names[etf_name] = sub_names
                if disc_sub:
                    all_sub_disc[etf_name] = disc_sub
        except Exception as e:
            print(f"  [ERROR] {etf_name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*60)
    print("Summary: Macro Clusters (K=3)")
    print("="*60)
    for etf_name, names in all_macro_names.items():
        print(f"\n  {etf_name}:")
        for cid, name in names.items():
            print(f"    Cluster {cid}: {name}")
        if etf_name in all_macro_disc:
            d = all_macro_disc[etf_name]
            print(f"    mean_ANOVA_F={d['mean_anova_F']:.2f}  "
                  f"total_MI={d['total_mi']:.3f}  "
                  f"unique_names={d['unique_auto_names']}/{d['n_clusters']}")

    print("\n" + "="*60)
    print("Summary: Sub-Clusters (hierarchical)")
    print("="*60)
    for etf_name, names in all_sub_names.items():
        print(f"\n  {etf_name}:")
        for cid, name in names.items():
            print(f"    Sub {cid}: {name}")
        if etf_name in all_sub_disc:
            d = all_sub_disc[etf_name]
            print(f"    mean_ANOVA_F={d['mean_anova_F']:.2f}  "
                  f"total_MI={d['total_mi']:.3f}  "
                  f"unique_names={d['unique_auto_names']}/{d['n_clusters']}")

    print("\nCluster characterization complete!")


if __name__ == '__main__':
    main()
