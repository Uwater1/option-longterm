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

## 4. Tradability / Big-Move Gating Model (v2)

Per-side classifiers that predict whether a day will see a large directional
move (big-up tail for long, big-down tail for short). Used as a **veto filter**
over the daytrade linear score (NOT as a standalone signal — see
`daytrade/GATING_ONLY_REPORT.md`: gate-only total OOS Sharpe = +9.08 vs
gated-daytrade +41.94).

### v2 improvements over v1
- **Feature curation** (was: all 130 raw, no selection). Three selectors
  benchmarked per cell, winner auto-picked:
  - `none` — all 130 features (legacy baseline).
  - `stability` — `feature_select.py`: regime-stratified block bootstrap +
    randomized ElasticNet + OOB Spearman IC screen + variance cap (σ ≤ 0.15).
    Yields ~14–25 features.
  - `lgbm` — walk-forward LightGBM gain + permutation importance, top-25.
- **Three target variants** (was: per-side binary only):
  - `two_sided` — per-side binary big-move (legacy).
  - `joint3` — shared 3-class softmax {big_up, neutral, big_down}; long uses
    P(big_up), short uses P(big_down). Shares signal between sides.
  - `gated` — big-move label ANDed with a tradability/regime mask
    (rolling vol20/early_range above p40). Two-stage filter collapsed into one
    binary classifier.
- **Honest IS/OOS reporting** (was: final model retrained on dev+holdout, leak).
  Deployed artifact still retrains on dev+holdout (more data = better), but two
  distinct metrics are now reported:
  - `dev_only_oos` — holdout metric of the dev-trained model (unbiased).
  - `forward_wf_estimate` — pooled purged walk-forward OOS over the full dataset
    (the deployed-model proxy; used for variant/selector/model selection).
- **Performance**: dropped RandomForest from default benchmark (rarely wins,
  3–4× slower), compute `forward_wf` only for the CV-winner (3×→1×), parallelize
  the 5 ETFs across processes. Full sweep (5 ETFs × 3 variants × 3 selectors ×
  20 Optuna trials) runs in **~100s** on a 12-core box (was 30+ min).

### Commands

```bash
# Full sweep (recommended): all ETFs, all variants × selectors, parallel
python day-model/gating_model.py -e all -t 20 --jobs 5

# Single ETF, quick smoke
python day-model/gating_model.py -e 300 -t 5

# Restrict variants / selectors / model types
python day-model/gating_model.py -e all --variants two_sided,joint3 --selectors stability,lgbm
python day-model/gating_model.py -e all --models logistic,rf,lightgbm   # re-enable RF

# Compile head-to-head comparison report (winner table + full WF PR-AUC grid)
python day-model/evaluate_gating.py
```

### Outputs
- Per-config artifacts (variant × selector):
  - `gating_model/gating_{ETF}_{side}_{variant}_{selector}.joblib`
  - `gating_model/gating_scaler_{ETF}_{side}_{variant}_{selector}.joblib`
  - `gating_model/report_{ETF}_{side}_{variant}_{selector}.json`
- Canonical promoted winner (backward-compatible, consumed by daytrade):
  - `gating_model/gating_{ETF}_{side}.joblib`
  - `gating_model/gating_scaler_{ETF}_{side}.joblib`
  - `gating_model/report_{ETF}_{side}.json` — carries `chosen_variant`,
    `chosen_selector`, `firing_threshold`, `features_used`, `selection_summary`.
- Plots: `gating_model/plots/curves_{ETF}_{side}_{variant}_{selector}.png`
- Comparison Markdown: `gating_model/GATING_REPORT.md`,
  `tradability_model_report.md` (project root mirror).

### Daytrade integration
The daytrade pipeline consumes the canonical promoted artifacts via
`daytrade/gating_loader.py`. Calibration auto-sweeps gated vs ungated
(`python -m daytrade.calibrate --mode single --sweep-gated`), and
`daytrade/deploy.py` mixed-mode picker treats `{mode}` and `{mode}+gated` as
candidates per side. See `daytrade/AGENTS.md` §"Gating Integration".
