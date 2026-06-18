"""
Task 2+3: Dimensionality reduction + Clustering
- Embeddings: PCA, UMAP, t-SNE, Autoencoder
- Clustering: HDBSCAN, KMeans, GMM, Spectral
- Quality assessment and stability analysis
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score, calinski_harabasz_score,
    adjusted_mutual_info_score
)
import hdbscan
import umap

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

import matplotlib.pyplot as plt
import seaborn as sns
import json

# Configuration
ETF_NAMES = ['300ETF', '50ETF', '500ETF', '588000ETF', '159915ETF']
PRIMARY_ETF = '300ETF'

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / 'data'
PLOTS_DIR = OUTPUT_DIR / 'plots'
MODELS_DIR = OUTPUT_DIR / 'models'

# Device
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ============================================================
# Autoencoder Model
# ============================================================
class ConvAutoencoder(nn.Module):
    """1D Convolutional Autoencoder for intraday price curves"""
    
    def __init__(self, input_dim=48, bottleneck_dim=8):
        super().__init__()
        
        # Encoder: 48 -> 32 -> 16 -> 8
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=5, stride=2, padding=2),  # 48 -> 24
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=5, stride=2, padding=2),  # 24 -> 12
            nn.ReLU(),
            nn.Conv1d(32, 16, kernel_size=5, stride=2, padding=2),  # 12 -> 6
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(16 * 6, bottleneck_dim),
        )
        
        # Decoder: 8 -> 16 -> 32 -> 48
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, 16 * 6),
            nn.Unflatten(1, (16, 6)),
            nn.ConvTranspose1d(16, 32, kernel_size=5, stride=2, padding=2, output_padding=1),  # 6 -> 12
            nn.ReLU(),
            nn.ConvTranspose1d(32, 16, kernel_size=5, stride=2, padding=2, output_padding=1),  # 12 -> 24
            nn.ReLU(),
            nn.ConvTranspose1d(16, 1, kernel_size=5, stride=2, padding=2, output_padding=1),  # 24 -> 48
        )
    
    def forward(self, x):
        z = self.encoder(x)
        x_recon = self.decoder(z)
        return x_recon, z
    
    def encode(self, x):
        return self.encoder(x)


def train_autoencoder(price_curves, epochs=100, batch_size=128, lr=1e-3):
    """Train autoencoder on price curves"""
    print(f"\n  Training Autoencoder on {DEVICE}...")
    
    # Prepare data: (N, 1, 48)
    X = torch.FloatTensor(price_curves).unsqueeze(1).to(DEVICE)
    dataset = TensorDataset(X)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Model
    model = ConvAutoencoder(input_dim=48, bottleneck_dim=8).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    # Train
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for (batch,) in loader:
            optimizer.zero_grad()
            recon, _ = model(batch)
            loss = criterion(recon.squeeze(1), batch.squeeze(1))
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if (epoch + 1) % 20 == 0:
            avg_loss = total_loss / len(loader)
            print(f"    Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
    
    # Extract embeddings
    model.eval()
    with torch.no_grad():
        embeddings = model.encode(X).cpu().numpy()
    
    # Save model
    model_path = MODELS_DIR / 'autoencoder.pt'
    torch.save(model.state_dict(), model_path)
    print(f"  Saved model: {model_path}")
    
    return embeddings, model


# ============================================================
# Embedding Functions
# ============================================================
def compute_embeddings(price_curves, features_df):
    """Compute multiple embeddings"""
    n_samples = len(price_curves)
    print(f"\n  Computing embeddings for {n_samples} days...")
    
    embeddings = {}
    
    # 1) PCA
    print("  [1/4] PCA...")
    pca = PCA(n_components=min(20, n_samples - 1))
    emb_pca = pca.fit_transform(price_curves)
    embeddings['pca'] = emb_pca
    
    # Scree plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(1, len(pca.explained_variance_ratio_) + 1),
            np.cumsum(pca.explained_variance_ratio_), 'bo-')
    ax.axhline(0.9, color='r', linestyle='--', label='90%')
    ax.set_xlabel('Number of Components')
    ax.set_ylabel('Cumulative Explained Variance')
    ax.set_title('PCA Scree Plot')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'embedding_pca_scree.png', dpi=100)
    plt.close()
    
    # PCA 2D scatter
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = [features_df['gap_pct'], features_df['intraday_return'], features_df['realized_vol']]
    titles = ['Gap %', 'Intraday Return', 'Realized Vol']
    for ax, c, title in zip(axes, colors, titles):
        sc = ax.scatter(emb_pca[:, 0], emb_pca[:, 1], c=c, cmap='RdYlBu', alpha=0.5, s=10)
        ax.set_xlabel('PC1')
        ax.set_ylabel('PC2')
        ax.set_title(f'PCA colored by {title}')
        plt.colorbar(sc, ax=ax)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'embedding_pca.png', dpi=100)
    plt.close()
    
    # 2) UMAP
    print("  [2/4] UMAP...")
    reducer = umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.1, random_state=42)
    emb_umap = reducer.fit_transform(price_curves)
    embeddings['umap'] = emb_umap
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(emb_umap[:, 0], emb_umap[:, 1], c=features_df['gap_pct'],
                    cmap='RdYlBu', alpha=0.5, s=10)
    ax.set_title('UMAP Embedding (colored by Gap %)')
    plt.colorbar(sc, ax=ax)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'embedding_umap.png', dpi=100)
    plt.close()
    
    # 3) t-SNE
    print("  [3/4] t-SNE...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42, max_iter=1000)
    emb_tsne = tsne.fit_transform(price_curves)
    embeddings['tsne'] = emb_tsne
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(emb_tsne[:, 0], emb_tsne[:, 1], c=features_df['gap_pct'],
                    cmap='RdYlBu', alpha=0.5, s=10)
    ax.set_title('t-SNE Embedding (colored by Gap %)')
    plt.colorbar(sc, ax=ax)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'embedding_tsne.png', dpi=100)
    plt.close()
    
    # 4) Autoencoder
    print("  [4/4] Autoencoder...")
    emb_ae, model = train_autoencoder(price_curves, epochs=80, batch_size=128)
    embeddings['ae'] = emb_ae
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(emb_ae[:, 0], emb_ae[:, 1], c=features_df['gap_pct'],
                    cmap='RdYlBu', alpha=0.5, s=10)
    ax.set_title('Autoencoder Embedding (colored by Gap %)')
    plt.colorbar(sc, ax=ax)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'embedding_ae.png', dpi=100)
    plt.close()
    
    return embeddings


# ============================================================
# Multi-Criteria K Selection
# ============================================================
def _gap_statistic(data, k, n_refs=5):
    """Compute gap statistic for a given K using uniform reference datasets."""
    n, d = data.shape
    log_wks = []
    for ref_i in range(n_refs):
        rng = np.random.RandomState(ref_i)
        ref = rng.uniform(data.min(axis=0), data.max(axis=0), size=(n, d))
        km_ref = KMeans(n_clusters=k, random_state=ref_i, n_init=5, max_iter=200).fit(ref)
        log_wks.append(np.log(max(km_ref.inertia_, 1e-30)))
    log_wk_ref = np.mean(log_wks)

    km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300).fit(data)
    log_wk_data = np.log(max(km.inertia_, 1e-30))
    gap = log_wk_ref - log_wk_data

    s_k = np.std(log_wks) * np.sqrt(1 + 1.0 / n_refs) if len(log_wks) > 1 else 0.0
    return gap, s_k, km.inertia_, km.labels_


def _find_elbow(ks, inertias):
    """Find elbow (knee) in inertia curve via maximum curvature."""
    if len(ks) < 4:
        return ks[0]
    y = np.array(inertias)
    # second difference as curvature proxy
    d2 = np.diff(y, n=2)
    # elbow is where curvature magnitude is maximum (most negative d2)
    elbow_idx = int(np.argmin(d2)) + 1  # +1 because diff shrinks array
    return ks[min(elbow_idx, len(ks) - 1)]


def select_best_k(data, k_range=range(4, 16), etf_name=''):
    """
    Select optimal K via multi-criteria composite score.

    Metrics (higher-is-better after normalization):
      - Silhouette score          (weight 0.20)
      - Calinski-Harabasz index   (weight 0.15)
      - 1 - Davies-Bouldin index  (weight 0.15)
      - Gap statistic             (weight 0.25)
      - BIC (lower=better)        (weight 0.15)
      - Elbow proximity           (weight 0.10)

    Rejects any K where a cluster has < 3% of total samples.
    """
    n_samples = len(data)
    ks = list(k_range)
    scorecard = []
    inertias = []
    gaps = []

    print(f"  Computing metrics for K={ks[0]}..{ks[-1]} ({len(ks)} candidates)...")

    for k in ks:
        # Gap statistic (also runs KMeans and returns inertia + labels)
        gap, gap_se, inertia, labels = _gap_statistic(data, k, n_refs=5)
        inertias.append(inertia)
        gaps.append(gap)

        # Cluster metrics
        sil = silhouette_score(data, labels, sample_size=min(2000, n_samples))
        ch = calinski_harabasz_score(data, labels)
        db = davies_bouldin_score(data, labels)

        # Minimum cluster fraction
        _, counts = np.unique(labels, return_counts=True)
        min_frac = counts.min() / n_samples

        # GMM BIC
        gmm = GaussianMixture(n_components=k, random_state=42, covariance_type='full', max_iter=200)
        gmm.fit(data)
        bic = gmm.bic(data)
        aic = gmm.aic(data)

        scorecard.append({
            'k': k,
            'silhouette': sil,
            'calinski_harabasz': ch,
            'davies_bouldin': db,
            'gap': gap,
            'gap_se': gap_se,
            'inertia': inertia,
            'bic': bic,
            'aic': aic,
            'min_frac': min_frac,
        })
        print(f"    K={k:2d}: sil={sil:.3f}  CH={ch:.0f}  DB={db:.3f}  gap={gap:.3f}  BIC={bic:.0f}  min%={min_frac:.1%}")

    # Elbow detection
    elbow_k = _find_elbow(ks, inertias)
    print(f"  Elbow detected at K={elbow_k}")

    # --- Normalize each metric to [0, 1] rank space (higher = better) ---
    metrics = {
        'silhouette':          [s['silhouette'] for s in scorecard],
        'calinski_harabasz':   [s['calinski_harabasz'] for s in scorecard],
        'davies_bouldin':      [-s['davies_bouldin'] for s in scorecard],   # lower DB → higher score
        'gap':                 gaps,
        'bic':                 [-s['bic'] for s in scorecard],              # lower BIC → higher score
    }

    def _rank_norm(values):
        """Convert values to rank-based [0,1] scores (higher rank = higher score)."""
        arr = np.array(values, dtype=float)
        order = arr.argsort().argsort().astype(float)
        rng = order.max() - order.min()
        return order / rng if rng > 0 else np.full(len(arr), 0.5)

    rn = {name: _rank_norm(vals) for name, vals in metrics.items()}

    # Elbow proximity: give a boost to K near elbow_k
    elbow_scores = []
    for s in scorecard:
        dist = abs(s['k'] - elbow_k)
        elbow_scores.append(1.0 / (1.0 + dist))
    rn['elbow'] = _rank_norm(elbow_scores)

    # Composite score
    weights = {
        'silhouette': 0.20,
        'calinski_harabasz': 0.15,
        'davies_bouldin': 0.15,
        'gap': 0.25,
        'bic': 0.15,
        'elbow': 0.10,
    }

    best_k, best_score = ks[0], -1.0
    for i, s in enumerate(scorecard):
        # Degenerate cluster guard: reject K where any cluster < 3%
        if s['min_frac'] < 0.03:
            s['composite'] = -999.0
            continue
        score = sum(weights[m] * rn[m][i] for m in weights)
        s['composite'] = float(score)
        if score > best_score:
            best_score, best_k = score, s['k']

    print(f"  Best K selected: {best_k}  (composite score: {best_score:.3f})")

    # Save scorecard JSON
    sc_path = DATA_DIR / f'k_selection_scorecard_{etf_name}.json'
    with open(sc_path, 'w') as f:
        json.dump({'best_k': int(best_k), 'scorecard': scorecard}, f, indent=2, default=str)
    print(f"  Saved scorecard: {sc_path}")

    # Plot composite score vs K
    valid = [s for s in scorecard if s['composite'] > -998]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    for s in valid:
        color = 'green' if s['k'] == best_k else 'steelblue'
        marker = 'o' if s['k'] == best_k else 's'
        ax.scatter(s['k'], s['composite'], c=color, s=120, marker=marker, zorder=5)
        ax.annotate(f"K={s['k']}", (s['k'], s['composite']),
                    textcoords='offset points', xytext=(0, 8), fontsize=8, ha='center')
    ax.set_xlabel('Number of Clusters (K)')
    ax.set_ylabel('Composite Score (higher = better)')
    ax.set_title(f'K Selection — {etf_name}  (best K={best_k})')
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(ks, inertias, 'bo-', linewidth=1.5)
    ax.axvline(best_k, color='green', linestyle='--', label=f'Selected K={best_k}')
    ax.axvline(elbow_k, color='orange', linestyle=':', alpha=0.7, label=f'Elbow K={elbow_k}')
    ax.set_xlabel('K')
    ax.set_ylabel('Inertia')
    ax.set_title('Inertia Curve (elbow detection)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'cluster_k_selection_{etf_name}.png', dpi=120)
    plt.close()

    return best_k, scorecard


# ============================================================
# Clustering Functions
# ============================================================
def run_clustering(data_dict, data_name, best_k=None):
    """Run multiple clustering algorithms on one representation.

    If best_k is provided (from select_best_k), it is used as the primary K
    for KMeans / GMM / Spectral.  A silhouette sweep is still run for metrics.
    """
    print(f"\n  Clustering: {data_name} (shape: {data_dict.shape})" +
          (f"  [using K={best_k}]" if best_k else ""))
    results = {}

    # 1) HDBSCAN
    print("    [1/4] HDBSCAN...")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=30, min_samples=5, cluster_selection_method='eom')
    labels_hdbscan = clusterer.fit_predict(data_dict)
    n_clusters = len(set(labels_hdbscan)) - (1 if -1 in labels_hdbscan else 0)
    n_noise = (labels_hdbscan == -1).sum()
    print(f"      Found {n_clusters} clusters, {n_noise} noise points")
    results['hdbscan'] = labels_hdbscan

    # 2) KMeans (silhouette sweep kept for metrics; primary K from best_k)
    print("    [2/4] KMeans...")
    sweep_best_k, sweep_best_score, sweep_best_labels = 3, -1, None
    for k in range(3, 13):
        km = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels_k = km.fit_predict(data_dict)
        score = silhouette_score(data_dict, labels_k, sample_size=min(2000, len(data_dict)))
        if score > sweep_best_score:
            sweep_best_k, sweep_best_score, sweep_best_labels = k, score, labels_k
    print(f"      Silhouette-best K={sweep_best_k}, Sil={sweep_best_score:.4f}")

    # Use externally-selected K if provided, otherwise fall back to sweep
    primary_k = best_k if best_k else sweep_best_k
    if primary_k != sweep_best_k:
        km_primary = KMeans(n_clusters=primary_k, random_state=42, n_init=10, max_iter=300)
        labels_primary = km_primary.fit_predict(data_dict)
        sil_primary = silhouette_score(data_dict, labels_primary, sample_size=min(2000, len(data_dict)))
        print(f"      Using selected K={primary_k}, Sil={sil_primary:.4f}")
        results['kmeans'] = labels_primary
    else:
        results['kmeans'] = sweep_best_labels

    # 3) Gaussian Mixture (use same primary_k; BIC sweep kept for info)
    print("    [3/4] Gaussian Mixture...")
    bic_best_k, bic_best_bic = 3, float('inf')
    for k in range(3, 13):
        gmm = GaussianMixture(n_components=k, random_state=42, covariance_type='full')
        gmm.fit(data_dict)
        bic = gmm.bic(data_dict)
        if bic < bic_best_bic:
            bic_best_k, bic_best_bic = k, bic
    print(f"      BIC-best K={bic_best_k}, BIC={bic_best_bic:.1f}")
    gmm_primary = GaussianMixture(n_components=primary_k, random_state=42, covariance_type='full')
    gmm_primary.fit(data_dict)
    results['gmm'] = gmm_primary.predict(data_dict)

    # 4) Spectral Clustering (use primary_k)
    print("    [4/4] Spectral Clustering...")
    try:
        spec = SpectralClustering(n_clusters=primary_k, random_state=42, affinity='nearest_neighbors')
        labels_spec = spec.fit_predict(data_dict)
        results['spectral'] = labels_spec
        print(f"      Spectral K={primary_k}")
    except Exception as e:
        print(f"      Spectral failed: {e}")

    return results


def evaluate_clustering(labels, data, labels_name, data_name):
    """Evaluate cluster quality"""
    # Filter noise points for metrics
    mask = labels >= 0
    if mask.sum() < 10:
        return None
    
    labels_clean = labels[mask]
    data_clean = data[mask]
    n_clusters = len(set(labels_clean))
    
    if n_clusters < 2:
        return None
    
    try:
        sil = silhouette_score(data_clean, labels_clean, sample_size=min(2000, len(data_clean)))
        db = davies_bouldin_score(data_clean, labels_clean)
        ch = calinski_harabasz_score(data_clean, labels_clean)
    except Exception:
        return None
    
    return {
        'method': labels_name,
        'data': data_name,
        'n_clusters': n_clusters,
        'n_noise': (~mask).sum(),
        'silhouette': sil,
        'davies_bouldin': db,
        'calinski_harabasz': ch,
    }


def bootstrap_stability(data, cluster_func, n_boot=50):
    """Bootstrap stability analysis"""
    n = len(data)
    all_labels = []
    
    for i in range(n_boot):
        idx = np.random.choice(n, size=n, replace=True)
        boot_data = data[idx]
        labels = cluster_func(boot_data)
        all_labels.append(labels)
    
    # Measure pairwise agreement using AMI
    ami_scores = []
    for i in range(min(20, n_boot)):
        for j in range(i + 1, min(20, n_boot)):
            ami = adjusted_mutual_info_score(all_labels[i], all_labels[j])
            ami_scores.append(ami)
    
    return np.mean(ami_scores), np.std(ami_scores)


# ============================================================
# Main Pipeline
# ============================================================
def process_etf(etf_name):
    """Full pipeline for one ETF"""
    print(f"\n{'='*60}")
    print(f"Pattern Discovery: {etf_name}")
    print('='*60)
    
    # Load data
    paths_npz = np.load(DATA_DIR / f'paths_{etf_name}.npz')
    features_df = pd.read_csv(DATA_DIR / f'features_{etf_name}.csv', index_col='date', parse_dates=True)
    
    price_curves = paths_npz['price']
    
    # Align
    n = min(len(price_curves), len(features_df))
    price_curves = price_curves[:n]
    features_df = features_df.iloc[:n]
    
    print(f"  Loaded {n} days, {price_curves.shape[1]} bars/day")
    
    # Standardize features for clustering (impute NaN)
    features_clean = np.nan_to_num(features_df.values, nan=0.0, posinf=0.0, neginf=0.0)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_clean)
    
    # ---- EMBEDDINGS ----
    embeddings = compute_embeddings(price_curves, features_df)
    
    # Save embeddings
    for name, emb in embeddings.items():
        pd.DataFrame(emb, index=features_df.index).to_csv(
            DATA_DIR / f'embeddings_{etf_name}_{name}.csv'
        )
    
    # ---- CLUSTERING ----
    print("\n" + "="*40)
    print("Clustering Phase")
    print("="*40)

    # Multi-criteria K selection on PCA embeddings (top 8 PCs)
    pca_repr = embeddings['pca'][:, :8]
    best_k, k_scorecard = select_best_k(pca_repr, k_range=range(4, 16), etf_name=etf_name)

    # Save best_k for downstream scripts (cross_etf_validation, etc.)
    best_k_path = DATA_DIR / f'best_k_{etf_name}.json'
    with open(best_k_path, 'w') as f:
        json.dump({'etf': etf_name, 'best_k': int(best_k)}, f)

    # Data representations to cluster
    representations = {
        'raw_curves': price_curves,
        'pca': embeddings['pca'][:, :8],  # top 8 PCs
        'ae': embeddings['ae'],
        'features': features_scaled,
    }
    
    all_metrics = []
    all_cluster_results = {}
    
    for repr_name, repr_data in representations.items():
        cluster_results = run_clustering(repr_data, repr_name, best_k=best_k)
        
        for method_name, labels in cluster_results.items():
            metrics = evaluate_clustering(labels, repr_data, method_name, repr_name)
            if metrics:
                all_metrics.append(metrics)
            
            key = f"{method_name}_{repr_name}"
            all_cluster_results[key] = labels
            
            # Save cluster labels
            pd.DataFrame({'date': features_df.index, 'cluster': labels}).to_csv(
                DATA_DIR / f'clusters_{etf_name}_{key}.csv', index=False
            )
    
    # ---- QUALITY COMPARISON ----
    print("\n  Cluster Quality Summary:")
    df_metrics = pd.DataFrame(all_metrics)
    if not df_metrics.empty:
        print(df_metrics[['method', 'data', 'n_clusters', 'silhouette', 'davies_bouldin']].to_string(index=False))
        
        # Plot quality metrics
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Silhouette
        ax = axes[0]
        for method in df_metrics['method'].unique():
            subset = df_metrics[df_metrics['method'] == method]
            ax.bar([f"{method}\n{d}" for d in subset['data']], subset['silhouette'], alpha=0.7)
        ax.set_title('Silhouette Score (higher=better)')
        ax.tick_params(axis='x', rotation=45)
        
        # Davies-Bouldin
        ax = axes[1]
        for method in df_metrics['method'].unique():
            subset = df_metrics[df_metrics['method'] == method]
            ax.bar([f"{method}\n{d}" for d in subset['data']], subset['davies_bouldin'], alpha=0.7)
        ax.set_title('Davies-Bouldin (lower=better)')
        ax.tick_params(axis='x', rotation=45)
        
        # Number of clusters
        ax = axes[2]
        for method in df_metrics['method'].unique():
            subset = df_metrics[df_metrics['method'] == method]
            ax.bar([f"{method}\n{d}" for d in subset['data']], subset['n_clusters'], alpha=0.7)
        ax.set_title('Number of Clusters')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f'cluster_quality_{etf_name}.png', dpi=100)
        plt.close()
    
    # ---- BOOTSTRAP STABILITY ----
    print("\n  Bootstrap stability (50 iterations, best method)...")
    best_idx = df_metrics['silhouette'].idxmax() if not df_metrics.empty else None
    if best_idx is not None:
        best_method = df_metrics.loc[best_idx, 'method']
        best_data = df_metrics.loc[best_idx, 'data']
        best_repr = representations[best_data]

        # Define cluster function for bootstrap — use selected best_k
        def cluster_func(data):
            km = KMeans(n_clusters=int(best_k), random_state=42)
            return km.fit_predict(data)
        
        ami_mean, ami_std = bootstrap_stability(best_repr, cluster_func, n_boot=50)
        print(f"    Best: {best_method}_{best_data}, AMI={ami_mean:.4f} ± {ami_std:.4f}")
    
    # ---- TEMPORAL STABILITY ----
    print("\n  Temporal stability analysis...")
    # Use best clustering for temporal analysis
    if best_idx is not None:
        best_key = f"{best_method}_{best_data}"
        best_labels = all_cluster_results[best_key]
        
        # Year-by-year cluster proportions
        features_df['cluster'] = best_labels
        features_df['year'] = features_df.index.year
        
        year_props = features_df.groupby('year')['cluster'].value_counts(normalize=True).unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        year_props.plot(kind='bar', stacked=True, ax=ax, colormap='Set3')
        ax.set_title(f'Cluster Proportions by Year ({best_key})')
        ax.set_ylabel('Proportion')
        ax.legend(title='Cluster', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f'cluster_temporal_{etf_name}.png', dpi=100, bbox_inches='tight')
        plt.close()
    
    return df_metrics


def main():
    PLOTS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("Day-Type Discovery: Embeddings + Clustering")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    
    all_metrics = {}
    
    for etf_name in ETF_NAMES:
        try:
            metrics = process_etf(etf_name)
            all_metrics[etf_name] = metrics
        except Exception as e:
            print(f"  [ERROR] {etf_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # ---- SUMMARY ----
    print("\n" + "="*60)
    print("Summary: Best clustering per ETF")
    print("="*60)
    for etf_name, metrics in all_metrics.items():
        if metrics is not None and not metrics.empty:
            best = metrics.loc[metrics['silhouette'].idxmax()]
            print(f"  {etf_name}: {best['method']}_{best['data']} "
                  f"(K={best['n_clusters']:.0f}, Sil={best['silhouette']:.4f})")
    
    print("\nPattern discovery complete!")


if __name__ == '__main__':
    main()
