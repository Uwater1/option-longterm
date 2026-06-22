# Daytrade — Asymmetric Dual-Model Overhaul Plan

Transition day-trading layer from single regression model to two independent, asymmetric models per ETF: `long_model` (upside specialist) and `short_model` (downside specialist).

---

## 1. Architecture Comparison

```
Current Single-Model Architecture:
  Features ──▶ Scaler ──▶ Single Model (Lasso/Huber) ──▶ Continuous Score
                                                             │
                                      ┌──────────────────────┴──────────────────────┐
                                      ▼                                             ▼
                                  Score > 0                                     Score < 0
                                      │                                             │
                        long_thr (expanding pct)                      short_thr (expanding pct)
                                      │                                             │
                                      ▼                                             ▼
                                  Long Fire                                     Short Fire

Proposed Dual-Model Architecture:
  Features ──▶ Scaler Long  ──▶ Long Model  ──▶ Long Conviction Score ──▶ long_thr  ──▶ Long Fire
  Features ──▶ Scaler Short ──▶ Short Model ──▶ Short Conviction Score ──▶ short_thr ──▶ Short Fire
                                                                                     │
                                                                           [Conflict Resolution]
```

| Axis | Single Model (Current) | Dual Model (Proposed) |
| :--- | :--- | :--- |
| **Model Files** | `linear_{ETF}.joblib`, `scaler_{ETF}.joblib` | `linear_{ETF}_long.joblib`, `linear_{ETF}_short.joblib`<br>`scaler_{ETF}_long.joblib`, `scaler_{ETF}_short.joblib` |
| **Target Variable** | `pm_return` (continuous) | Long: `pm_return_long = max(0.0, pm_return)`<br>Short: `pm_return_short = max(0.0, -pm_return)` |
| **Loss Optimizer** | Fits symmetric errors across full range | Long: optimizes positive-return prediction accuracy<br>Short: optimizes downside/crash prediction accuracy |
| **Feature Selection** | Stability selection on `pm_return` | Independent stability selection per side |
| **Calibration** | Grid search over single score signs | Grid search over two positive-oriented conviction scores |

---

## 2. Phase-by-Phase Execution Details

### Phase 2.1: Target Definition & Feature Selection (`day-model/train_model.py`)

*   **Target Modification**:
    *   Create targets inside `train_etf()`:
        *   `y_long = np.maximum(0.0, y_raw) * Y_SCALE`
        *   `y_short = np.maximum(0.0, -y_raw) * Y_SCALE`
*   **Asymmetric Stability Selection**:
    *   Run `compute_stability_scores()` independently:
        *   Long side uses `y_long`
        *   Short side uses `y_short`
    *   Features like `first_30min_return` will get large positive weights in long model, and volume spikes/drawdowns will dominate short model.
*   **Optuna Search & Saving**:
    *   Add `--side` parameter to `train_model.py` (`long` or `short` or `both` to train both sequentially).
    *   Optuna study optimizes hyperparameters separately.
    *   Save files separately:
        *   `linear_{ETF}_long.joblib` and `scaler_{ETF}_long.joblib`
        *   `linear_{ETF}_short.joblib` and `scaler_{ETF}_short.joblib`

### Phase 2.2: Score Computation (`daytrade/scores.py`)

*   **Modify `load_model(etf)` to `load_model(etf, side)`**:
    *   Load `linear_{etf}_{side}.joblib` and `scaler_{etf}_{side}.joblib`.
*   **Modify `compute_scores(etf)` to `compute_scores(etf, side)`**:
    *   Apply side-specific scaler transform.
    *   Multiply by side-specific coefficients.
    *   Return side-specific score series (both long/short scores will be positive-oriented, representing conviction).

### Phase 2.3: Signal Rules & Conflict Resolution (`daytrade/rules.py`)

*   **Modify `get_long_short_signals`**:
    *   Load independent scores:
        *   `long_score = compute_scores(etf, "long")`
        *   `short_score = compute_scores(etf, "short")`
    *   Compute thresholds:
        *   `long_thr = expanding_pct_masked(long_score, long_threshold_pct / 100.0, min_periods)`
        *   `short_thr = expanding_pct_masked(short_score, short_threshold_pct / 100.0, min_periods)`
    *   Fires:
        *   `long_fires = long_score >= long_thr` and `long_score >= long_conviction`
        *   `short_fires = short_score >= short_thr` and `short_score >= short_conviction`
*   **Conflict Resolution**:
    *   If both `long_fires` and `short_fires` are True on same day:
        *   **Rule**: Pick side with highest normalized margin: `margin = score / threshold`.
        *   `long_margin = long_score / long_thr`
        *   `short_margin = short_score / short_thr`
        *   If `long_margin > short_margin` $\rightarrow$ Long, else Short.

### Phase 2.4: Backtesting & Calibration (`daytrade/backtest.py` & `daytrade/calibrate.py`)

*   **Backtest Engine**:
    *   Update `backtest_long_short()` to pass `long_score` and `short_score` to rules.
*   **Calibration**:
    *   Run independent grid search for `long_threshold_pct`/`long_conviction_pct` using long model.
    *   Run independent grid search for `short_threshold_pct`/`short_conviction_pct` using short model.
    *   Write optimized thresholds to `daytrade/data/calibration.json`.

---

## 3. Step-by-Step Task Checklist

- [ ] **Step 1: Modify `day-model/train_model.py`**
  - [ ] Add `--side` parameter.
  - [ ] Implement `y_long` and `y_short` targets.
  - [ ] Run stability selection per side.
  - [ ] Train, tune with Optuna, and save `_long.joblib` and `_short.joblib` models/scalers.
- [ ] **Step 2: Train all models**
  - [ ] Run `python day-model/train_model.py -e all --side long`
  - [ ] Run `python day-model/train_model.py -e all --side short`
- [ ] **Step 3: Modify `daytrade/scores.py`**
  - [ ] Update `load_model` to accept `side`.
  - [ ] Update `compute_scores` to accept `side` and load appropriate files.
- [ ] **Step 4: Modify `daytrade/rules.py`**
  - [ ] Update `get_long_short_signals` to load dual scores and apply conflict resolution.
- [ ] **Step 5: Modify `daytrade/calibrate.py`**
  - [ ] Update `_calibrate_one_side` to fetch side-specific scores.
- [ ] **Step 6: Run Calibrate & Report**
  - [ ] Run `python -m daytrade.calibrate`
  - [ ] Run `python -m daytrade.report`
  - [ ] Verify that OOS Sharpe ratios improve.
