# Day-Model Feature Expansion Workflow

Add new features, run training pipeline, filter noisy inputs via Time-Series Stability Selection.

## Target

Target: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`. Matches daytrade P&L exactly:
- Decision at close of `decision_bar`.
- Entry at open of `decision_bar + 1` (next-bar open fill).
- Exit at close of `EXIT_BAR = 41` (14:30).

`pm_return` (bars 24..47, 13:00->15:00) retained as diagnostic column in `features_{ETF}.parquet` for IC checks. Do NOT train models on `pm_return`.

Per-ETF `DECISION_BAR` and `EXIT_BAR` defined in `build_features.py` (imported by `daytrade/__init__.py`).

## Training Modes

```bash
# Default: single symmetric model (raw trade_return)
python day-model/train_model.py -e all

# Dual asymmetric models (for daytrade hybrid/dual mode)
python day-model/train_model.py -e all --side both --trials 100
# Output: linear_{ETF}_long.joblib, linear_{ETF}_short.joblib

# Train single side
python day-model/train_model.py -e 300 --side long

# Bar-count experiment (re-pick per-ETF DECISION_BAR)
python day-model/run_experiment_bars.py -e 300,50,500,588000,159915 --trials 40
# Output: experiment_bars_results_trade_return.json
```

**`--side` parameter details**:

| Side | Stability target | Training target | Sample weights | Optuna objective |
|:---|:---|:---|:---|:---|
| `single` (default) | `trade_return` (raw) | `trade_return` | uniform | overall Spearman IC |
| `long` | `max(0, trade_return)` (clipped) | `trade_return` (raw) | up-weight positive days (λ=0.5) | tail-weighted IC (50% overall + 50% top-30% tail) |
| `short` | `max(0, -trade_return)` (clipped) | `trade_return` (raw) | up-weight negative days (λ=0.5) | tail-weighted IC (50% overall + 50% top-30% tail) |

Output files suffix: `linear_{ETF}.joblib` (single) or `linear_{ETF}_long.joblib` / `linear_{ETF}_short.joblib` (dual).

Note: `short` side coefficients predict raw `trade_return`. At load time (`scores.py`), short score negated for positive-orientation.

---

## 1. Add New Features

Features split into two groups in `day-model/build_features.py`.

### A. Intraday Early-Bar Features (computable by decision-bar close)
1. Open `day-model/build_features.py`.
2. Locate `extract_day_early_features`.
3. Compute feature using first `decision_bar + 1` bars (`bars` variable; consume bars `[0..decision_bar]`).
4. Add feature key/value to returned dictionary.
5. In `day-model/train_model.py`, add feature name to `EARLY_FEATURES` list.

### B. Day-Level Features (shifted to yesterday close)
1. Open `day-model/build_features.py`.
2. Locate `compute_daylevel_indicators`.
3. Compute indicator on daily dataframe `df`.
4. Add column name to `day_cols` (automatically shifted by 1 day to prevent leakage).
5. In `day-model/train_model.py`, add feature name to `DAY_FEATURES` list.

---

## 2. Run Pipeline

```bash
# 1. Regenerate parquet feature datasets (writes trade_return + pm_return)
python day-model/build_features.py

# 2. Run Stability Selection & Optuna tuning (100 trials, CPU)
python day-model/train_model.py

# 3. Regenerate report markdown
python day-model/generate_report.py
```

---

## 3. Evaluate & Decide

Filter weak features automatically via Lasso Stability Selection:

1. **Check Stability Score**:
   - Open `day-model/REPORT.md`.
   - Check **Feature Stability Scores (Block Bootstrap)** table.
   - Features below threshold (< 50%) pruned automatically.
   - If selection probability < 20% across all ETFs, delete from `build_features.py`.

2. **Verify Holdout Performance**:
   - Verify OOS **Holdout IC** and **L/S Sharpe** improvement.
   - Confirm **IS-OOS Gap** remains low (prevents overfitting/leakage).

---

## 4. Tradability / Big-Move Gating Model (v2)

Per-side classifiers predict large directional move (big-up for long, big-down for short). Used as veto filter over daytrade linear score.

### v2 Improvements
- **Feature curation**: Three selectors benchmarked per cell, winner auto-picked:
  - `none`: all 130 features.
  - `stability`: `feature_select.py` block bootstrap + randomized ElasticNet + OOB IC screen + variance cap (σ ≤ 0.15). Yields ~14–25 features.
  - `lgbm`: walk-forward LightGBM gain + permutation importance, top-25.
- **Target variants**:
  - `two_sided`: per-side binary big-move.
  - `joint3`: shared 3-class softmax {big_up, neutral, big_down}.
  - `gated`: big-move label ANDed with tradability/regime mask.
- **Reporting**: Reports `dev_only_oos` and `forward_wf_estimate`.
- **Performance**: Parallelized 5 ETFs across processes. Full sweep runs in ~100s.

### Commands

```bash
# Full sweep: all ETFs, all variants x selectors, parallel
python day-model/gating_model.py -e all -t 20 --jobs 5

# Single ETF test
python day-model/gating_model.py -e 300 -t 5

# Restrict variants / selectors / models
python day-model/gating_model.py -e all --variants two_sided,joint3 --selectors stability,lgbm
python day-model/gating_model.py -e all --models logistic,rf,lightgbm

# Compile comparison report
python day-model/evaluate_gating.py
```

### Outputs
- Config artifacts: `gating_model/gating_{ETF}_{side}_{variant}_{selector}.joblib`, etc.
- Promoted winners: `gating_model/gating_{ETF}_{side}.joblib`, `gating_model/gating_scaler_{ETF}_{side}.joblib`, `gating_model/report_{ETF}_{side}.json`.
- Plots: `gating_model/plots/curves_{ETF}_{side}_{variant}_{selector}.png`.
- Markdown report: `gating_model/GATING_REPORT.md`, `tradability_model_report.md`.

### Daytrade Integration
Daytrade consumes promoted artifacts via `daytrade/gating_loader.py`. Calibration sweeps gated vs ungated (`python -m daytrade.calibrate --mode single --sweep-gated`), and `daytrade/deploy.py` mixed-mode picker treats `{mode}` and `{mode}+gated` as candidates per side.
