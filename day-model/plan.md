Plan: Day-Model XGBoost PM Return Predictor
Goal
Build an XGBoost regression model per ETF (5 ETFs) that predicts PM return (13:00–15:00 log return) using:
- Early-bar features from first 6 five-minute bars (9:30–10:00) — the REPORT.md §6 idea
- Day-level indicators (RSI14 + 5 others) computed from prior day's close_adj — the extension
- Optuna hyperparameter tuning with purged time-series CV to address overfitting
Folder Structure
day-model/
├── build_features.py     # Phase 1: feature engineering (caches parquet)
├── train_model.py        # Phase 2: Optuna + XGBoost + OOS eval
├── generate_report.py    # Phase 3: write REPORT.md
├── REPORT.md             # Generated final report
├── AGENTS.md             # Mirror day-trading/ convention
├── data/                 # cached features + optuna studies
├── models/               # trained xgboost .json per ETF
└── plots/                # diagnostic PNGs
Phase 1: build_features.py
Inputs: data/{510300,50,500,588000,159915}ETF_1d.parquet + {...}_5m.parquet
Output: day-model/data/features_{ETF}.parquet with columns:
Group	Features	Source
Early-bar (13)	gap_pct, first_30min_return, early_realized_vol, early_range, early_volume_ratio, early_trend, early_momentum, gap_direction, first_bar_return, first_bar_volume, early_vwap_dev, early_skew, early_kurtosis	First 6 bars of 5m data (REPORT.md §6 design)
Day-level (7)	rsi14, macd_hist, sma20_dist, sma50_dist, atr14_norm, roc10, bb_pctb, vol20	close_adj shifted by 1 (NO lookahead — uses prior day's close only)
Target	pm_return	Sum of log returns bars 24→47 (13:00–15:00)
Critical data rules (per AGENTS.md):
- Indicators on close_adj (post-adjusted) → no split artifacts
- prev_close = close_adj.shift(1) before any .tail()
- Drop first 60 rows (warmup for SMA50/ATR14)
- Optional: also build a 3-bar early variant for ablation
Phase 2: train_model.py
Per ETF (5 models):
Validation Protocol — Purged Walk-Forward
- TimeSeriesSplit(n_splits=5) with custom purge gap = 5 trading days between train and test
- Expanding window (each fold trains on all data up to t, tests t+5..t2)
- Optuna objective = mean Spearman rank IC across folds (robust to outliers, standard alpha metric)
- n_trials = 60, TPE sampler, pruned with MedianPruner
Optuna Search Space
Param	Range
n_estimators	100–500 (log)
max_depth	3–7
learning_rate	0.01–0.1 (log)
subsample	0.6–1.0
colsample_bytree	0.5–1.0
min_child_weight	1–10
gamma	0–5
reg_alpha	1e-3–1.0 (log)
reg_lambda	1.0–10.0 (log)
Metrics Computed
- Primary: OOS Spearman IC, OOS RMSE/MAE
- Direction accuracy: % where sign(pred) == sign(actual)
- Quintile analysis: mean PM return of top vs bottom predicted quintile, long-short Sharpe
- Feature importance: gain importance + permutation importance (more reliable)
Baselines (for comparison)
1. Predict zero (no-skill)
2. Yesterday's PM return (autocorrelation baseline)
3. first_30min_return (simple momentum baseline)
4. Linear regression on same features (controls for XGBoost overfitting)
Phase 3: generate_report.py → REPORT.md
Structure:
1. Executive Summary (table: per-ETF IC, Sharpe, vs baselines)
2. Data & Features
3. Methodology (purged CV, Optuna setup)
4. Results (per-ETF tables + quintile plots)
5. Comparison to Baselines
6. Risk of Overfitting
   6.1 IS vs OOS gap (train IC vs test IC per fold)
   6.2 Regime breakdown (OOS IC by year)
   6.3 Purge-gap sensitivity (gap=0 vs 5 vs 10 — leakage bias diagnostic)
   6.4 Feature importance stability across folds
   6.5 Permutation importance vs gain importance
   6.6 Hyperparameter sensitivity (Optuna trial scatter)
7. Conclusions & Caveats
Plots (in plots/)
- ic_timeseries_{ETF}.png — rolling OOS IC over time
- quintile_returns_{ETF}.png — top/bottom quintile cumulative return
- feature_importance_{ETF}.png — gain + permutation
- optuna_param_importance_{ETF}.png — hyperparameter influence
- purge_sensitivity_{ETF}.png — IC vs purge gap
- learning_curve_{ETF}.png — IC vs train size
Overfitting Risk Mitigations (built-in)
1. Purge gap=5 between train/test (no short-term leakage)
2. Optuna on inner CV only (not on final test)
3. Spearman IC objective (rank-based, outlier-robust)
4. Permutation importance reported alongside gain importance
5. Per-fold stability of top features checked
6. Year-by-year OOS breakdown (regime shift diagnostic)
7. Linear regression baseline (isolates XGBoost-specific overfitting)
Runtime Estimate
- ~10 min per ETF × 5 ETFs = ~50 min for full Optuna search
- Can be reduced to ~20 min by lowering n_trials=30
Dependencies Verified
- ✅ optuna 4.9.0, xgboost 3.3.0, lightgbm 4.6.0, pandas_ta, all ETF parquets present
- ✅ Reuses extract_day_features.py's ETF_CONFIG mapping (300ETF→510300)
- ✅ Follows predict_open_high.py conventions (ETF_CONFIG dict, pandas_ta, TimeSeriesSplit)