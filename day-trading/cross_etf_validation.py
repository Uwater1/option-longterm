"""
Task 6: Cross-ETF Validation
- Cluster each ETF independently with selected K, compare shapes
- Align clusters across ETFs (Hungarian algorithm)
- Pooled model: train on all ETFs, compare with per-ETF
- Transfer test: train on ETF A, predict on ETF B
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import json
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
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'
MODELS_DIR = OUTPUT_DIR / 'models'


MACRO_K = 3  # Fixed macro taxonomy


def _load_best_k(etf_name):
    """Load selected K from best_k_{etf}.json (saved by discover_patterns.py)."""
    path = DATA_DIR / f'best_k_{etf_name}.json'
    if path.exists():
        with open(path) as f:
            return json.load(f)['best_k']
    return MACRO_K  # fallback


def _consensus_k():
    """Consensus K for cross-ETF comparison = MACRO_K (fixed)."""
    return MACRO_K


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
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv',
                              index_col='date', parse_dates=True)
    
    price_curves = paths_npz['price']
    
    # Align
    n = min(len(price_curves), len(features_df))
    price_curves = price_curves[:n]
    features_df = features_df.iloc[:n]
    
    return price_curves, features_df


def cluster_etf(price_curves, k=None):
    """Run KMeans on PCA of price curves.

    Uses MACRO_K by default for cross-ETF consistency.
    """
    from sklearn.decomposition import PCA

    pca = PCA(n_components=8)
    X_pca = pca.fit_transform(price_curves)

    if k is None:
        k = MACRO_K
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_pca)

    return labels, km.cluster_centers_, pca


# ============================================================
# Cross-ETF Analysis
# ============================================================
def cross_etf_clustering():
    """Compare clusters across ETFs using macro K=3."""
    print("\n" + "="*60)
    print("Cross-ETF Clustering Comparison (Macro K=3)")
    print("="*60)

    consensus = MACRO_K
    print(f"  Macro K for cross-ETF comparison: {consensus}")

    etf_results = {}

    for etf_name in ETF_NAMES:
        print(f"\n  {etf_name}:")
        price_curves, features_df = load_etf_data(etf_name)
        labels, centroids, pca = cluster_etf(price_curves, k=consensus)

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
            alignment_map[etf_name] = {i: i for i in range(consensus)}
            continue

        mapping = align_clusters(ref_centroids, etf_results[etf_name]['centroids'])
        alignment_map[etf_name] = mapping
        print(f"    {etf_name}: {mapping}")

    # Plot aligned centroids
    fig, axes = plt.subplots(len(ETF_NAMES), consensus, figsize=(5*consensus, 4*len(ETF_NAMES)), squeeze=False)

    for i, etf_name in enumerate(ETF_NAMES):
        centroids = etf_results[etf_name]['centroids']
        mapping = alignment_map[etf_name]

        for aligned_id in range(consensus):
            # Find which original cluster maps to this aligned_id
            orig_id = [k for k, v in mapping.items() if v == aligned_id]
            if not orig_id:
                axes[i, aligned_id].axis('off')
                continue
            orig_id = orig_id[0]
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
def _build_consensus_labels(consensus_k):
    """Re-cluster each ETF with consensus_k, then align to 300ETF reference.

    Returns dict {etf_name: aligned_labels_array}.
    """
    ref_etf = '300ETF'
    ref_centroids = None
    etf_centroids = {}
    etf_price = {}

    for etf_name in ETF_NAMES:
        price_curves, _ = load_etf_data(etf_name)
        etf_price[etf_name] = price_curves
        labels, centroids, _ = cluster_etf(price_curves, k=consensus_k)
        etf_centroids[etf_name] = centroids
        if etf_name == ref_etf:
            ref_centroids = centroids

    # Align each ETF to reference
    aligned = {}
    for etf_name in ETF_NAMES:
        centroids = etf_centroids[etf_name]
        if etf_name == ref_etf:
            mapping = {i: i for i in range(consensus_k)}
        else:
            mapping = align_clusters(ref_centroids, centroids)
        # Build aligned labels
        labels, _, _ = cluster_etf(etf_price[etf_name], k=consensus_k)
        inv_map = {v: k for k, v in mapping.items()}
        aligned[etf_name] = np.array([inv_map.get(int(l), int(l)) for l in labels])
    return aligned


def extract_early_features_for_model(etf_name, consensus_labels=None):
    """Extract early features for prediction.

    If consensus_labels is provided, use those instead of the per-ETF cluster file.
    """
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz', allow_pickle=True)
    price_curves = paths_npz['price']
    volume_curves = paths_npz['volume']
    return_curves = paths_npz['returns']
    dates = pd.to_datetime(paths_npz['dates'])

    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv',
                              index_col='date', parse_dates=True)

    if consensus_labels is not None:
        # Use aligned labels (array aligned to price_curves index)
        date_to_label = dict(zip(dates, consensus_labels))
        cluster_df = pd.Series(date_to_label)
        cluster_df.index.name = 'date'
    else:
        cluster_file = DATA_DIR / f'clusters_{etf_name}_kmeans_pca.csv'
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

        if consensus_labels is not None:
            cluster_label = date_to_label.get(d)
            if cluster_label is None:
                continue
        else:
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
    """Train model on all ETFs combined using consensus-aligned labels."""
    print("\n" + "="*60)
    print("Pooled Model (All ETFs, consensus labels)")
    print("="*60)

    consensus = _consensus_k()
    print(f"  Consensus K: {consensus}")
    aligned = _build_consensus_labels(consensus)

    all_X = []
    all_y = []

    for etf_name in ETF_NAMES:
        X, y = extract_early_features_for_model(etf_name, consensus_labels=aligned[etf_name])
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
    """Train on ETF A, predict on ETF B (consensus-aligned labels)."""
    print("\n" + "="*60)
    print("Transfer Test (Train A -> Predict B)")
    print("="*60)

    consensus = _consensus_k()
    aligned = _build_consensus_labels(consensus)

    results = {}

    for train_etf in ETF_NAMES:
        X_train, y_train = extract_early_features_for_model(
            train_etf, consensus_labels=aligned[train_etf])
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        model = lgb.LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.05,
                                    random_state=42, verbose=-1)
        model.fit(X_train_scaled, y_train)

        results[train_etf] = {}

        for test_etf in ETF_NAMES:
            X_test, y_test = extract_early_features_for_model(
                test_etf, consensus_labels=aligned[test_etf])
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


def sub_cluster_transfer():
    """Test whether sub-types within each macro type transfer across broad-market ETFs.

    For each macro cluster (0,1,2): load sub-cluster labels from each ETF,
    align by centroid similarity, measure transfer accuracy.
    """
    print("\n" + "="*60)
    print("Sub-Cluster Transfer (within macro types)")
    print("="*60)

    from sklearn.decomposition import PCA
    ref_etf = '300ETF'
    macro_names = {0: 'Rally/Selloff/Neutral', 1: 'Rally/Selloff/Neutral', 2: 'Rally/Selloff/Neutral'}

    # Load macro + sub labels per ETF
    etf_sub = {}
    etf_pca = {}
    for etf_name in ETF_NAMES:
        price_curves, _ = load_etf_data(etf_name)
        pca = PCA(n_components=8)
        etf_pca[etf_name] = pca.fit_transform(price_curves)

        # Load macro labels
        macro_path = DATA_DIR / f'clusters_{etf_name}_kmeans_pca.csv'
        sub_path = DATA_DIR / f'clusters_{etf_name}_sub.csv'
        if not macro_path.exists() or not sub_path.exists():
            print(f"  {etf_name}: missing macro or sub labels, skipping")
            continue
        macro_df = pd.read_csv(macro_path, parse_dates=['date']).set_index('date')['cluster']
        sub_df = pd.read_csv(sub_path, parse_dates=['date']).set_index('date')['cluster'].astype(str)
        common = macro_df.index.intersection(sub_df.index)
        etf_sub[etf_name] = pd.DataFrame({
            'macro': macro_df.loc[common],
            'sub': sub_df.loc[common],
        })

    if ref_etf not in etf_sub:
        print("  Reference ETF missing, skipping sub-cluster transfer")
        return {}

    transfer_results = {}
    for macro_id in sorted(etf_sub[ref_etf]['macro'].unique()):
        macro_id_int = int(macro_id)
        print(f"\n  Macro {macro_id_int}:")
        # Get sub-labels and PCA embeddings for this macro cluster per ETF
        macro_sub = {}
        for etf_name, df in etf_sub.items():
            mask = df['macro'] == macro_id
            if mask.sum() < 20:
                continue
            macro_sub[etf_name] = {
                'sub_labels': df.loc[mask, 'sub'].values,
                'pca': etf_pca[etf_name][mask.values] if mask.values.dtype == bool
                     else etf_pca[etf_name][np.where(mask.values)[0]],
            }

        if ref_etf not in macro_sub or len(macro_sub) < 2:
            continue

        # Train LightGBM on ref ETF sub-types, predict on others
        ref_data = macro_sub[ref_etf]
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        y_ref = le.fit_transform(ref_data['sub_labels'])
        X_ref = ref_data['pca']

        if len(np.unique(y_ref)) < 2:
            print(f"    < 2 sub-types in ref, skipping")
            continue

        scaler = StandardScaler()
        X_ref_scaled = scaler.fit_transform(X_ref)
        model = lgb.LGBMClassifier(n_estimators=150, max_depth=5, learning_rate=0.05,
                                    random_state=42, verbose=-1)
        model.fit(X_ref_scaled, y_ref)

        transfer_results[macro_id_int] = {}
        for test_etf, test_data in macro_sub.items():
            X_test = scaler.transform(test_data['pca'])
            # Map test sub-labels to ref encoding for accuracy
            test_sub_labels = test_data['sub_labels']
            # Use Hungarian alignment if label sets differ
            try:
                y_test = le.transform(test_sub_labels)
            except ValueError:
                # Different label set — use accuracy as a rough proxy
                # (encode what we can, mark rest as -1)
                y_test = np.full(len(test_sub_labels), -1)
                for i, lbl in enumerate(test_sub_labels):
                    if lbl in le.classes_:
                        y_test[i] = le.transform([lbl])[0]
                valid = y_test >= 0
                if valid.sum() < 10:
                    transfer_results[macro_id_int][test_etf] = None
                    continue
                X_test = X_test[valid]
                y_test = y_test[valid]

            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            transfer_results[macro_id_int][test_etf] = acc
            print(f"    {ref_etf} -> {test_etf}: {acc:.4f}")

    return transfer_results


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("Cross-ETF Validation")
    print("=" * 60)
    
    # 1) Cross-ETF clustering comparison
    etf_results, alignment_map = cross_etf_clustering()
    
    # 2) Pooled model
    pooled_acc, model_pooled, scaler_pooled = run_pooled_model()
    
    # 3) Transfer test (macro-level, K=3)
    transfer_results = transfer_test()
    
    # 4) Sub-cluster transfer (within macro types)
    sub_transfer = sub_cluster_transfer()
    
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
    with open(DATA_DIR / 'cross_etf_results.txt', 'w') as f:
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

        if sub_transfer:
            f.write("\nSub-Cluster Transfer (within macro types, ref=300ETF):\n")
            for macro_id, etf_accs in sub_transfer.items():
                f.write(f"  Macro {macro_id}:\n")
                for test_etf, acc in etf_accs.items():
                    acc_str = f"{acc:.4f}" if acc is not None else "n/a"
                    f.write(f"    -> {test_etf}: {acc_str}\n")
    
    print("\nCross-ETF validation complete!")


if __name__ == '__main__':
    main()
