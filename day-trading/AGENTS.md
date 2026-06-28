# Day-Trading Research — Price Action Day-Type Discovery

Intraday pattern discovery and early day-type prediction for ETF universe (50/300/500/588000/159915).

## Commands

Run pipeline scripts in order:

```bash
# Phase 1: Feature Extraction
python extract_day_features.py          # Extract 48-bar paths + 22 scalar features per day

# Phase 2: Pattern Discovery
python discover_patterns.py             # PCA/UMAP/t-SNE/AE embeddings, multi-criteria K selection, KMeans/GMM/HDBSCAN/Spectral

# Phase 3: Cluster Characterization
python characterize_clusters.py         # Profile clusters, feature discrimination (ANOVA F, MI), temporal analysis

# Phase 4: Early Prediction
python predict_early.py                 # LightGBM/XGBoost/NeuralNet prediction + direction profitability + lunch strategy

# Phase 5: Cross-ETF Validation
python cross_etf_validation.py          # Consensus-K alignment, pooled model, transfer test

# Phase 6: Lunch Break Analysis
python lunch_break_analysis.py          # Chow test, CUSUM, AM/PM regime comparison

# Phase 7: Report Generation
python generate_report.py              # Generate REPORT.md with plots/tables
```

## Environment

- **Python 3.9+**
- **torch optional**: `discover_patterns.py` uses PyTorch for autoencoder embedding. If missing, comment out autoencoder section; PCA/UMAP/t-SNE work without it.
- **CPU sufficient**: LightGBM/XGBoost/sklearn run fast on CPU. Autoencoder runs on CPU in minutes.
- **Key dependencies**: `scikit-learn`, `lightgbm`, `xgboost`, `hdbscan`, `umap-learn`, `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `joblib`. Optional: `torch`, `ruptures`.

## Data Dependencies

- **5m bar data**: `../data/{ETF}_5m.parquet` (from parent `update_data.py` + `download_5m_data.py`).
- **1d bar data**: `../data/{ETF}_1d.parquet` (prev_close reference).
- Intermediate data saved to `./data/`. Plots saved to `./plots/`. Models saved to `./models/`.

## Architecture

### Pipeline Flow

```
extract_day_features.py    -> data/paths_{ETF}.npz, data/features_{ETF}.csv
discover_patterns.py       -> data/embeddings_*, data/k_selection_*, data/clusters_*
characterize_clusters.py   -> data/cluster_discrimination_*, plots/
predict_early.py           -> data/early_prediction_results.txt, models/early_lgb_*
cross_etf_validation.py    -> data/cross_etf_results.txt, models/early_lgb_pooled.joblib
lunch_break_analysis.py    -> data/lunch_break_results.json, plots/
generate_report.py         -> REPORT.md
```

### Key Design Decisions

- **Multi-criteria K selection**: Gap statistic (25%) + Silhouette (20%) + Calinski-Harabasz (15%) + Davies-Bouldin (15%) + BIC (15%) + Elbow proximity (10%). Reject degenerate clusters (<3% data).
- **Feature discrimination**: ANOVA F-test + mutual information per feature. Auto-name clusters by z-score deviation.
- **Direction profitability**: Evaluate clusters for long and short. Pick direction by highest absolute Sharpe. Assumes option shorts.
- **Consensus K**: Use median of per-ETF best_k values for pooled model. Align clusters via Hungarian algorithm.
- **Lunch break analysis**: Chow test + CUSUM change-point at bar 24 (11:30/13:00 boundary). Measure AM/PM regime independence via adjusted mutual information.

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
| PCA components | Top 8 |

## File Structure

```
day-trading/
├── extract_day_features.py       # Phase 1: Feature extraction
├── discover_patterns.py          # Phase 2: Embeddings + clustering + K selection
├── characterize_clusters.py      # Phase 3: Cluster profiling + discrimination
├── predict_early.py              # Phase 4: Early prediction + profitability
├── cross_etf_validation.py       # Phase 5: Cross-ETF alignment + transfer test
├── lunch_break_analysis.py       # Phase 6: Lunch break change-point analysis
├── generate_report.py            # Phase 7: REPORT.md generation
├── REPORT.md                     # Final research report
├── AGENTS.md                     # This file
├── data/                         # Intermediate data
├── plots/                        # Visualizations
└── models/                       # Trained models
```
