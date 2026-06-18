"""
Task 6: Cross-ETF Validation
- Cluster each ETF independently, compare shapes
- Align clusters across ETFs (Hungarian algorithm)
- Pooled model: train on all ETFs, compare with per-ETF
- Transfer test: train on ETF A, predict on ETF B
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
from scipy.optimize import linear_sum_assignment
import lightgbm as lgb
import joblib

import matplotlib.pyplot as plt
import seaborn as sns

ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']

OUTPUT_DIR = Path(__file__).resolve().parent
PLOTS_DIR = OUTPUT_DIR / 'plots'
MODELS_DIR = OUTPUT_DIR / 'models'


# ============================================================
# Cluster Alignment
# ============================================================
def align_clusters(centroids_a, centroids_b):
    """Align clusters from two ETFs using Hungarian algorithm"""
    from scipy.spatial.distance import cdist
    
    # Compute cost matrix (distances between centroids)
    cost_matrix = cdist(centroids_a, centroids_b, metric='euclidean')
    
    # Hungarian algorithm for optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    return dict(zip(row_ind, col_ind))


def load_etf_data(etf_name):
    """Load paths and features for one ETF"""
    paths_npz = np.load(OUTPUT_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    features_df = pd.read_csv(OUTPUT_DIR / f'features_{etf_name}.csv', 
                              index_col='date', parse_dates=True)
    
    price_curves = paths_npz['price']
    
    # Align
    n = min(len(price_curves), len(features_df))
    price_curves = price_curves[:n]
    features_df = features_df.iloc[:n]
    
    return price_curves, features_df


def cluster_etf(price_curves, k=3):
    """Run KMeans on PCA of price curves"""
    from sklearn.decomposition import PCA
    
    pca = PCA(n_components=8)
    X_pca = pca.fit_transform(price_curves)
    
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_pca)
    
    return labels, km.cluster_centers_, pca


# ============================================================
# Cross-ETF Analysis
# ============================================================
def cross_etf_clustering():
    """Compare clusters across ETFs"""
    print("\n" + "="*60)
    print("Cross-ETF Clustering Comparison")
    print("="*60)
    
    etf_results = {}
    
    for etf_name in ETF_NAMES:
        print(f"\n  {etf_name}:")
        price_curves, features_df = load_etf_data(etf_name)
        labels, centroids, pca = cluster_etf(price_curves, k=3)
        
        etf_results[etf_name] = {
            'labels': labels,
            'centroids': centroids,
            'pca': pca,
            'price_curves': price_curves,
            'features_df': features_df,
        }
        
        # Cluster distribution
        unique, counts = np.unique(labels, return_counts=True)
        for u, c in zip(unique, counts):
            print(f"    Cluster {u}: {c} days ({c/len(labels)*100:.1f}%)")
    
    # Align clusters to 300ETF as reference
    ref_etf = '300ETF'
    ref_centroids = etf_results[ref_etf]['centroids']
    
    print(f"\n  Aligning clusters to {ref_etf} reference...")
    
    alignment_map = {}
    for etf_name in ETF_NAMES:
        if etf_name == ref_etf:
            alignment_map[etf_name] = {0: 0, 1: 1, 2: 2}
            continue
        
        mapping = align_clusters(ref_centroids, etf_results[etf_name]['centroids'])
        alignment_map[etf_name] = mapping
        print(f"    {etf_name}: {mapping}")
    
    # Plot aligned centroids
    fig, axes = plt.subplots(len(ETF_NAMES), 3, figsize=(15, 4*len(ETF_NAMES)), squeeze=False)
    
    for i, etf_name in enumerate(ETF_NAMES):
        centroids = etf_results[etf_name]['centroids']
        mapping = alignment_map[etf_name]
        
        for aligned_id in range(3):
            # Find which original cluster maps to this aligned_id
            orig_id = [k for k, v in mapping.items() if v == aligned_id][0]
            centroid = centroids[orig_id]
            
            ax = axes[i, aligned_id]
            ax.plot(centroid, 'b-', linewidth=2)
            ax.axhline(0, color='gray', linestyle='--', alpha=0.3)
            ax.axvline(24, color='red', linestyle=':', alpha=0.3)
            ax.set_title(f'{etf_name} - Aligned Cluster {aligned_id}')
            ax.set_xlabel('Bar Index')
            if aligned_id == 0:
                ax.set_ylabel('Normalized Price')
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'cross_etf_alignment.png', dpi=150)
    plt.close()
    
    return etf_results, alignment_map


# ============================================================
# Early Prediction Models
# ============================================================
def extract_early_features_for_model(etf_name):
    """Extract early features for prediction"""
    paths_npz = np.load(OUTPUT_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    price_curves = paths_npz['price']
    volume_curves = paths_npz['volume']
    return_curves = paths_npz['returns']
    dates = pd.to_datetime(paths_npz['dates'])
    
    features_df = pd.read_csv(OUTPUT_DIR / f'features_{etf_name}.csv', 
                              index_col='date', parse_dates=True)
    
    cluster_file = OUTPUT_DIR / f'clusters_{etf_name}_kmeans_pca.csv'
    cluster_df = pd.read_csv(cluster_file, parse_dates=['date']).set_index('date')['cluster']
    
    # Align
    date_set_paths = set(dates)
    date_set_feat = set(features_df.index)
    date_set_clust = set(cluster_df.index)
    common = sorted(date_set_paths & date_set_feat & date_set_clust)
    
    path_idx_map = {d: i for i, d in enumerate(dates)}
    
    early_features = []
    y_list = []
    
    for d in common:
        pi = path_idx_map.get(d)
        if pi is None:
            continue
        
        cluster_label = cluster_df.loc[d]
        if pd.isna(cluster_label):
            continue
        
        feat_row = features_df.loc[d]
        early_returns = return_curves[pi, :6]
        early_volume = volume_curves[pi, :6]
        early_price = price_curves[pi, :6]
        
        feat_dict = {
            'gap_pct': feat_row['gap_pct'],
            'first_30min_return': early_price[-1],
            'first_30min_vol': early_volume.mean(),
            'volume_spike_open': early_volume[0],
            'early_realized_vol': np.nanstd(early_returns) * np.sqrt(48),
            'prev_day_vol': feat_row['prev_day_vol'],
            'am_return': feat_row['am_return'],
        }
        
        for j, val in enumerate(early_returns):
            feat_dict[f'early_bar_{j}'] = val
        
        early_features.append(feat_dict)
        y_list.append(int(cluster_label))
    
    X = pd.DataFrame(early_features)
    y = np.array(y_list)
    
    # Drop NaN
    nan_mask = np.isnan(X.values).any(axis=1) | np.isnan(y)
    X = X[~nan_mask].values
    y = y[~nan_mask]
    
    return X, y


def run_pooled_model():
    """Train model on all ETFs combined"""
    print("\n" + "="*60)
    print("Pooled Model (All ETFs)")
    print("="*60)
    
    all_X = []
    all_y = []
    
    for etf_name in ETF_NAMES:
        X, y = extract_early_features_for_model(etf_name)
        all_X.append(X)
        all_y.append(y)
        print(f"  {etf_name}: {len(X)} samples")
    
    X_pooled = np.vstack(all_X)
    y_pooled = np.concatenate(all_y)
    
    print(f"\n  Total: {len(X_pooled)} samples")
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_pooled)
    
    # 5-fold CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    preds = np.zeros(len(y_pooled))
    
    for train_idx, val_idx in skf.split(X_scaled, y_pooled):
        model = lgb.LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, 
                                    random_state=42, verbose=-1)
        model.fit(X_scaled[train_idx], y_pooled[train_idx])
        preds[val_idx] = model.predict(X_scaled[val_idx])
    
    acc = accuracy_score(y_pooled, preds)
    print(f"  Pooled Accuracy: {acc:.4f}")
    
    joblib.dump(model, MODELS_DIR / 'early_lgb_pooled.joblib')
    
    return acc, model, scaler


def transfer_test():
    """Train on ETF A, predict on ETF B"""
    print("\n" + "="*60)
    print("Transfer Test (Train A -> Predict B)")
    print("="*60)
    
    results = {}
    
    for train_etf in ETF_NAMES:
        X_train, y_train = extract_early_features_for_model(train_etf)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        model = lgb.LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.05,
                                    random_state=42, verbose=-1)
        model.fit(X_train_scaled, y_train)
        
        results[train_etf] = {}
        
        for test_etf in ETF_NAMES:
            X_test, y_test = extract_early_features_for_model(test_etf)
            X_test_scaled = scaler.transform(X_test)
            
            preds = model.predict(X_test_scaled)
            acc = accuracy_score(y_test, preds)
            
            results[train_etf][test_etf] = acc
            
            if train_etf == test_etf:
                print(f"  {train_etf} -> {test_etf}: {acc:.4f} (self)")
            else:
                print(f"  {train_etf} -> {test_etf}: {acc:.4f}")
    
    # Plot transfer matrix
    fig, ax = plt.subplots(figsize=(10, 8))
    
    matrix = np.array([[results[t][e] for e in ETF_NAMES] for t in ETF_NAMES])
    
    sns.heatmap(matrix, annot=True, fmt='.3f', cmap='YlOrRd',
                xticklabels=ETF_NAMES, yticklabels=ETF_NAMES, ax=ax)
    ax.set_title('Transfer Accuracy (Train ETF -> Test ETF)')
    ax.set_xlabel('Test ETF')
    ax.set_ylabel('Train ETF')
    
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'cross_etf_transfer.png', dpi=150)
    plt.close()
    
    return results


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("Cross-ETF Validation")
    print("=" * 60)
    
    # 1) Cross-ETF clustering comparison
    etf_results, alignment_map = cross_etf_clustering()
    
    # 2) Pooled model
    pooled_acc, model_pooled, scaler_pooled = run_pooled_model()
    
    # 3) Transfer test
    transfer_results = transfer_test()
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"\n  Pooled Model Accuracy: {pooled_acc:.4f}")
    
    print("\n  Per-ETF vs Pooled:")
    for etf_name in ETF_NAMES:
        self_acc = transfer_results[etf_name][etf_name]
        print(f"    {etf_name}: Self={self_acc:.4f}")
    
    print("\n  Average Transfer Accuracy:")
    for train_etf in ETF_NAMES:
        transfer_accs = [transfer_results[train_etf][test_etf] 
                        for test_etf in ETF_NAMES if test_etf != train_etf]
        avg_transfer = np.mean(transfer_accs)
        print(f"    {train_etf}: {avg_transfer:.4f}")
    
    # Save results
    with open(OUTPUT_DIR / 'cross_etf_results.txt', 'w') as f:
        f.write("Cross-ETF Validation Results\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Pooled Model Accuracy: {pooled_acc:.4f}\n\n")
        
        f.write("Transfer Accuracy Matrix:\n")
        f.write("Train\\Test  " + "  ".join(f"{e:>10s}" for e in ETF_NAMES) + "\n")
        for train_etf in ETF_NAMES:
            row = f"{train_etf:>10s}"
            for test_etf in ETF_NAMES:
                acc = transfer_results[train_etf][test_etf]
                row += f"  {acc:10.4f}"
            f.write(row + "\n")
        
        f.write("\nAverage Transfer Accuracy (excluding self):\n")
        for train_etf in ETF_NAMES:
            transfer_accs = [transfer_results[train_etf][test_etf] 
                            for test_etf in ETF_NAMES if test_etf != train_etf]
            avg_transfer = np.mean(transfer_accs)
            f.write(f"  {train_etf}: {avg_transfer:.4f}\n")
    
    print("\nCross-ETF validation complete!")


if __name__ == '__main__':
    main()
