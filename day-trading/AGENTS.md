# Day-Trading Research — Price Action Day-Type Discovery

Intraday pattern discovery and early day-type prediction for Chinese A-share ETFs (50/300/500/588000/159915).

## Commands

Run scripts in pipeline order:

```bash
# Phase 1: Feature Extraction
python extract_day_features.py          # Extract 48-bar paths + 22 scalar features per day

# Phase 2: Pattern Discovery (embeddings + clustering)
python discover_patterns.py             # PCA/UMAP/t-SNE/AE embeddings, multi-criteria K selection, KMeans/GMM/HDBSCAN/Spectral

# Phase 3: Cluster Characterization
python characterize_clusters.py         # Auto-profile clusters, feature discrimination (ANOVA F, MI), temporal analysis

# Phase 4: Early Prediction (first 30 min)
python predict_early.py                 # LightGBM/XGBoost/NeuralNet prediction + direction-aware profitability + lunch strategy

# Phase 5: Cross-ETF Validation
python cross_etf_validation.py          # Consensus-K alignment, pooled model, transfer test

# Phase 6: Lunch Break Analysis (standalone)
python lunch_break_analysis.py          # Chow test, CUSUM, AM/PM regime comparison

# Phase 7: Report Generation
python generate_report.py              # Produces REPORT.md with all plots/tables
```

## Environment

- **Python 3.9+**
- **torch is optional**: Only `discover_patterns.py` uses PyTorch for the autoencoder embedding. If torch is not installed, comment out the autoencoder section in `discover_patterns.py`; all other embeddings (PCA, UMAP, t-SNE) and all other scripts work without it.
- **No GPU required**: CPU is sufficient for all models. LightGBM/XGBoost/sklearn run fast on CPU. The autoencoder (if used) runs on CPU in minutes.
- **Key dependencies**: `scikit-learn`, `lightgbm`, `xgboost`, `hdbscan`, `umap-learn`, `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `joblib`
- **Optional**: `torch` (for autoencoder), `ruptures` (for advanced change-point detection)

## Data Dependencies

- **5m bar data**: `../data/{ETF}_5m.parquet` (from parent project `update_data.py` + `download_5m_data.py`)
- **1d bar data**: `../data/{ETF}_1d.parquet` (for prev_close reference)
- All intermediate data saved to `./data/` (paths NPZ, features CSV, cluster CSV, embeddings, scorecards)
- All plots saved to `./plots/`
- Trained models saved to `./models/`

## Architecture

### Pipeline Flow

```
extract_day_features.py
    → data/paths_{ETF}.npz (48-bar price/volume/return curves)
    → data/features_{ETF}.csv (22 scalar features per day)

discover_patterns.py
    → data/embeddings_{ETF}_{method}.csv (PCA/UMAP/tSNE/AE)
    → data/k_selection_scorecard_{ETF}.json (multi-criteria K scoring)
    → data/best_k_{ETF}.json (selected K per ETF)
    → data/clusters_{ETF}_{method}_{repr}.csv (cluster labels)
    → plots/cluster_k_selection_{ETF}.png

characterize_clusters.py
    → data/cluster_discrimination_{ETF}.json (ANOVA F, MI, z-profiles, auto-names)
    → plots/cluster_zscore_heatmap_{ETF}.png
    → plots/cluster_anova_f_{ETF}.png

predict_early.py
    → data/early_prediction_results.txt (accuracy + profitability + lunch strategy)
    → models/early_lgb_{ETF}.joblib
    → plots/lunch_strategy_{ETF}.png

cross_etf_validation.py
    → data/cross_etf_results.txt (pooled + transfer matrix)
    → models/early_lgb_pooled.joblib

lunch_break_analysis.py
    → data/lunch_break_results.json (Chow/CUSUM/AMI per ETF)
    → plots/lunch_analysis_{ETF}.png, lunch_summary.png

generate_report.py
    → REPORT.md (reads all above outputs)
```

### Key Design Decisions

- **Multi-criteria K selection**: Gap statistic (25%) + Silhouette (20%) + Calinski-Harabasz (15%) + Davies-Bouldin (15%) + BIC (15%) + Elbow proximity (10%). Degenerate clusters (<3% of data) rejected.
- **Feature discrimination**: ANOVA F-test per feature + mutual information. Clusters auto-named by z-score deviation from overall mean.
- **Direction-aware profitability**: Each cluster evaluated for both long and short. Optimal direction picked by highest absolute Sharpe. Assumes short-selling via options.
- **Consensus K for cross-ETF**: Median of per-ETF best_k values used for pooled model and transfer tests. Clusters aligned via Hungarian algorithm.
- **Lunch break analysis**: Chow test + CUSUM change-point detection at bar 24 (11:30/13:00 boundary). AM/PM regime independence measured by adjusted mutual information.

## Key Parameters

| Parameter | Value |
|-----------|-------|
| Bars per day | 48 (24 AM + 24 PM, 5-min intervals) |
| Trading hours | 9:30–11:30, 13:00–15:00 |
| Lunch bar index | 24 |
| ETF list | 300ETF, 50ETF, 500ETF, 588000ETF, 159915ETF |
| Early prediction window | First 6 bars (9:30–10:00) |
| K selection range | 4–15 |
| Autoencoder bottleneck | 8 dimensions |
| PCA components for clustering | Top 8 |

## File Structure

```
day-trading/
├── extract_day_features.py       # Phase 1: Feature extraction
├── discover_patterns.py          # Phase 2: Embeddings + clustering + K selection
├── characterize_clusters.py      # Phase 3: Cluster profiling + discrimination
├── predict_early.py              # Phase 4: Early prediction + profitability + lunch strategy
├── cross_etf_validation.py       # Phase 5: Cross-ETF alignment + transfer test
├── lunch_break_analysis.py       # Phase 6: Lunch break change-point analysis
├── generate_report.py            # Phase 7: REPORT.md generation
├── REPORT.md                     # Final research report
├── AGENTS.md                     # This file
├── data/                         # Intermediate data (NPZ, CSV, JSON)
├── plots/                        # All visualizations (PNG)
└── models/                       # Trained models (joblib, pt)
```
