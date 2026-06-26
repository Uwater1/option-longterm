# Day-Model Feature Expansion Workflow

This guide details how to add new features, run the training pipeline, and leverage Unified Time-Series Stability Selection to automatically filter out noisy inputs.

## Target

The model target is `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`, which mirrors the actual daytrade P&L exactly:
- decision at close of bar `decision_bar`
- entry at open of bar `decision_bar + 1` (next-bar open, realistic fill)
- exit at close of bar `EXIT_BAR = 41` (14:30)

`pm_return` (bars 24..47, 13:00→15:00) is retained as a **diagnostic** column in `features_{ETF}.parquet` for IC sanity-checks vs the old baseline. Do NOT train models on `pm_return` — it does not match the trade window.

Per-ETF `DECISION_BAR` and `EXIT_BAR` are defined in `build_features.py` as the single source of truth (imported by `daytrade/__init__.py`).

## Training Modes

```bash
# Default: single symmetric model (predicts raw trade_return)
python day-model/train_model.py -e all

# Dual asymmetric models (for daytrade hybrid/dual mode)
python day-model/train_model.py -e all --side both --trials 100
# Produces: linear_{ETF}_long.joblib, linear_{ETF}_short.joblib

# Train only one side
python day-model/train_model.py -e 300 --side long

# Bar-count experiment (re-pick per-ETF DECISION_BAR)
python day-model/run_experiment_bars.py -e 300,50,500,588000,159915 --trials 40
# Output: experiment_bars_results_trade_return.json
```

**`--side` parameter** controls the training target, feature selection, and Optuna objective:

| Side | Stability target (Phase 2.4) | Training target | Sample weights | Optuna objective (Phase 2.5) |
|:---|:---|:---|:---|:---|
| `single` (default) | `trade_return` (raw) | `trade_return` | uniform | overall Spearman IC |
| `long` | `max(0, trade_return)` (clipped) | `trade_return` (raw) | up-weight positive days (λ=0.5) | **tail-weighted IC** (50% overall + 50% top-30% tail) |
| `short` | `max(0, -trade_return)` (clipped) | `trade_return` (raw) | up-weight negative days (λ=0.5) | **tail-weighted IC** (50% overall + 50% top-30% tail) |

**Phase 2.4 fix**: Stability selection now uses the asymmetric clipped target (`y_clip_dev`) for dual models, so feature selection isolates regime-specific tail drivers instead of overall variance.

**Phase 2.5 fix**: Optuna objective for dual models blends 50% overall IC with 50% tail IC (computed on the top-30% of predictions by conviction). This aligns optimisation with the trading tail where signals fire.

Output files use suffix: `linear_{ETF}.joblib` (single) or `linear_{ETF}_long.joblib` / `linear_{ETF}_short.joblib` (dual).

**Note**: The `short` side model's coefficients predict raw `trade_return`. At load time (`scores.py`), the short score is **negated** to make it positive-oriented (high = strong downside conviction). This is transparent to the user.

---

## 1. How to Add New Features

Features are split into two groups in `day-model/build_features.py`.

### A. Intraday Early-Bar Features (computable by decision-bar close)
1. Open [day-model/build_features.py](file:///home/hallo/Documents/option-longterm/day-model/build_features.py).
2. Locate `extract_day_early_features`.
3. Compute your feature using the first `decision_bar + 1` five-minute bars (`bars` variable; only bars `[0..decision_bar]` are consumed; later bars are padded with 0.0).
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
# 1. Regenerate parquet feature datasets (writes both trade_return + pm_return)
python day-model/build_features.py

# 2. Run Parallel Stability Selection & Optuna tuning (100 trials, CPU)
#    TARGET = trade_return automatically
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

---

## 4. Tradability Gating Model (Option 1 Pre-Gate)

Separate binary classifiers (`gating_{ETF}_long.joblib` and `gating_{ETF}_short.joblib`) that pre-filter "untradable" chop days before direction/conviction models evaluate them.

### Commands

```bash
# 1. Train gating models (benchmarks Logistic, RF, and LightGBM with CV folds pre-scaled)
python day-model/gating_model.py -e all -t 30

# 2. Compile head-to-head comparison report
python day-model/evaluate_gating.py
```

### Outputs
- Save models & scalers: `day-model/gating_model/gating_{ETF}_{side}.joblib`
- JSON reports: `day-model/gating_model/report_{ETF}_{side}.json`
- Plots: `day-model/gating_model/plots/curves_{ETF}_{side}.png` (ROC and Precision-Recall)
- Comparison Markdown: `day-model/gating_model/GATING_REPORT.md`
