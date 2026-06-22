# Day-Model Feature Expansion Workflow

This guide details how to add new features, run the training pipeline, and leverage the Lasso Block Bootstrap Stability Selection to automatically filter out noisy inputs.

## Training Modes

```bash
# Default: single symmetric model (predicts raw pm_return)
python day-model/train_model.py -e all

# Dual asymmetric models (for daytrade hybrid mode)
python day-model/train_model.py -e all --side both --trials 100
# Produces: linear_{ETF}_long.joblib, linear_{ETF}_short.joblib

# Train only one side
python day-model/train_model.py -e 300 --side long
```

**`--side` parameter** controls the training target and feature selection:

| Side | Stability target | Training target | Sample weights | Optuna objective |
|:---|:---|:---|:---|:---|
| `single` (default) | `pm_return` | `pm_return` | uniform | overall Spearman IC |
| `long` | `max(0, pm_return)` | `pm_return` (raw) | up-weight positive days (λ=0.5) | upside IC (`pred` vs `max(0,y)`) |
| `short` | `max(0, -pm_return)` | `pm_return` (raw) | up-weight negative days (λ=0.5) | downside IC (`-pred` vs `max(0,-y)`) |

Output files use suffix: `linear_{ETF}.joblib` (single) or `linear_{ETF}_long.joblib` / `linear_{ETF}_short.joblib` (dual).

**Note**: The `short` side model's coefficients predict raw `pm_return`. At load time (`scores.py`), the short score is **negated** to make it positive-oriented (high = strong downside conviction). This is transparent to the user.

---

## 1. How to Add New Features

Features are split into two groups in `day-model/build_features.py`.

### A. Intraday Early-Bar Features (computable by 10:00 AM)
1. Open [day-model/build_features.py](file:///home/hallo/Documents/option-longterm/day-model/build_features.py).
2. Locate `extract_day_early_features`.
3. Compute your feature using the first 6 five-minute bars (`bars` variable).
4. Add your computed feature key/value to the returned dictionary.
5. In [day-model/train_model.py](file:///home/hallo/Documents/option-longterm/day-model/train_model.py), add your feature name to the `EARLY_FEATURES` list.

### B. Day-Level Features (shifted to yesterday's close)
1. Open [day-model/build_features.py](file:///home/hallo/Documents/option-longterm/day-model/build_features.py).
2. Locate `compute_daylevel_indicators`.
3. Compute your indicator on the daily dataframe `df` (using `ta` indicators or pandas operations).
4. Add the column name to `day_cols`. (The script automatically shifts these columns by 1 to prevent future leakage).
5. In [day-model/train_model.py](file:///home/hallo/Documents/option-longterm/day-model/train_model.py), add the feature name to the `DAY_FEATURES` list.

---

## 2. Running the Pipeline

After adding your features:

```bash
# 1. Regenerate parquet feature datasets
python day-model/build_features.py

# 2. Run Parallel Stability Selection & Optuna tuning (100 trials, CPU)
python day-model/train_model.py

# 3. Re-generate report markdown
python day-model/generate_report.py
```

---

## 3. How to Evaluate & Decide (Keep or Discard)

Since Lasso Stability Selection is aggressive, you can load **100+ features** into the model. The pipeline will automatically filter out the weak ones.

Decide whether to keep or discard using the following protocol:

1. **Check Stability Score**:
   - Open the regenerated [REPORT.md](file:///home/hallo/Documents/option-longterm/day-model/REPORT.md).
   - Locate the **Feature Stability Scores (Block Bootstrap)** table for each ETF.
   - If a feature has a stability score **below** the tuned threshold (typically $< 50\%$), it is automatically pruned from the final model.
   - If a feature ranks poorly (e.g. selection probability $< 20\%$) across all ETFs, delete it from `build_features.py` to keep the code clean.

2. **Verify Holdout Performance**:
   - Verify that the OOS **Holdout IC** and **L/S Sharpe** have improved compared to the previous baseline report.
   - Confirm that the **IS-OOS Gap** (overfitting diagnostic) remains low. If a feature causes the gap to explode, it is leaking information or causing extreme variance.
