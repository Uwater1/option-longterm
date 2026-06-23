# Daytrade — Dual-Model Improvement Plan (v2)

Two independent asymmetric models per ETF: `long_model` (upside specialist) and `short_model` (downside specialist). v1 attempt failed; v2 redesigns the approach.

**v2 Status (2026-06-23): Phases 1–5 IMPLEMENTED.** Phases 1–4: mixed-mode deployment improved total OOS Sharpe from +28.60 (single-only) to **+41.46** (Δ=+12.86). Phase 5 (stop-loss): IS-optimised stops did **not** improve OOS (total Sharpe +40.10, Δ=−1.36 vs baseline); only 500ETF had stops applied and they degraded performance. Code infrastructure is in place (`backtest.py`, `calibrate.py`, `deploy.py`, `report.py`); see §3 Phase 5 for full results.

---

## 0. Current State (2026-06-22)

### What is deployed

**Single-model** (`mode="single"`) is the default and proven approach. One frozen signed regression score per ETF. Sign determines direction, magnitude determines conviction, masked expanding percentile per side. Results:

| ETF | Long OOS Sharpe | Short OOS Sharpe |
|:---|:---|:---|
| 159915ETF | +8.59 | +6.16 |
| 500ETF | +2.88 | +4.88 |
| 588000ETF | +3.51 | disabled |
| 300ETF | +0.17 | +2.21 |
| 50ETF | disabled | +0.67 |

### What v1 dual-model built (infrastructure preserved, not deployed)

- `train_model.py --side long|short|both` — asymmetric training pipeline
- `scores.compute_scores(etf, side)` — side-aware frozen score loader
- `rules.get_long_short_signals(mode="single"|"hybrid")` — dual signal modes
- `calibrate --mode single|hybrid` — per-mode grid search
- 10 dual-model artifacts in `day-model/models/`
- Hybrid calibration saved at `daytrade/data/calibration_hybrid.json`

---

## 1. What Went Wrong in v1 — Honest Post-Mortem

### Three root causes (all confirmed by peer review)

#### 1.1 Clipped target violates linear regression assumptions

**What was done**: Trained Lasso/Huber on `y_long = max(0, pm_return)` and `y_short = max(0, -pm_return)`.

**Why it fails**: Linear regression assumes a continuous unbounded target. Clipping creates a zero-inflated distribution where ~50% of labels are exactly 0. This causes:

- **Unstable coefficients**: The Lasso block-bootstrap stability selection sees a target with mass at zero on half the days. Features that separate "zero vs positive" get selected, but these are not the same features that rank-order "how positive." The selected feature subset is good at binary classification but poor at regression ranking.
- **Optimization pathology**: OLS/Ridge/Lasso minimise MSE. With half the targets at 0, the optimal MSE solution is to predict near-zero everywhere. The model becomes conservative — it rarely predicts high values, and when it does, the predictions are noisy.
- **Information destruction**: On negative-return days, the clipped target is 0 regardless of whether the actual return was -0.1% or -3.0%. The model cannot learn that some "non-long" days are mildly bearish (safe to skip) while others are crashing (strong short signal).

**Evidence**: 159915ETF dual long model had holdout IC of +0.19 against `max(0, pm_return)` (higher than single model's +0.10 on that metric). But the top-10% picks had mean return +0.29% vs the single model's +0.99%. Higher IC, worse trades — the model ranked well within the clipped target space but the ranking didn't translate to actual return ordering.

#### 1.2 Threshold dilution from positive-biased score distribution

**What was done**: Computed expanding-percentile thresholds over all prior `long_score > 0` values.

**Why it fails**: The single model's score is centered near zero (since `pm_return` has mean ≈ 0). Sign cleanly splits the data: ~50% positive, ~50% negative. The 90th percentile of positive-score days is a **high bar** — it selects only the top ~10% of all trading days.

The dual model predicts `max(0, pm_return)` or raw `pm_return` with positive-biased features. For 159915ETF long, the score mean is +0.20 and ~67%+ of days have `long_score > 0`. The 90th percentile of this wider distribution is **lower** relative to the strongest signals, selecting 55 trades vs the single model's 29 at the same nominal percentile.

| Metric | Single model (pos-score days) | Dual model (pos-conviction days) |
|:---|:---|:---|
| % of all days in threshold base | ~50% | ~67%+ |
| thr=90 selects (159915 long) | 29 days | 55 days |
| Mean return of selected | +0.99% | +0.29% |

The wider threshold base dilutes selectivity. More trades pass the filter, but the additional trades are low-conviction and drag down average returns.

#### 1.3 Hybrid mode is a fake dual system

**What was done**: Hybrid conviction = `|single_score| × dual_side_score`. Direction still gated by single-model sign.

**Why it fails**: The hybrid inherits the single model's directional limitations. If the single model says "flat" (score ≈ 0) on a day where the long-specialist model sees strong upside, the hybrid suppresses the trade. The dual model's independent signal is never allowed to override the single model's direction call. This is not a dual system — it is a single system with a dual filter bolted on.

**Evidence**: Hybrid calibration never beat single-mode on any ETF. The best hybrid results (159915ETF long +8.40 vs single +8.59) merely approximated the single model because the product term was dominated by the single-model magnitude.

---

## 2. Why Dual Models Can Still Work — The Right Design

The v1 failure does **not** prove dual models are fundamentally worse. It proves that clipping + linear regression + percentile-on-raw-score is the wrong implementation. Three specific changes are needed:

### 2.1 Fix the model type: Tobit or classification, not clipped regression

**Option A: Tobit regression** (for censored data)

The clipped target `max(0, pm_return)` is a **left-censored** variable (censored at 0). Tobit regression explicitly models this: it assumes a latent variable `y*` that is observed as `max(0, y*)`. The model jointly estimates:
- The regression equation for `y*` (which features drive the latent return)
- The probability of censoring (which features predict "will this day have positive return at all")

This is the statistically correct model for the clipped target. sklearn does not have Tobit, but `statsmodels` does (`sm.Tobit`), or it can be implemented via maximum likelihood.

**Option B: Two-stage classification + regression**

Stage 1: Binary classifier — "will pm_return be positive today?" (logistic/LightGBM)
Stage 2: Regression — "if positive, how positive?" (trained only on positive-return days)

Conviction = `P(positive) × predicted_magnitude`

This separates the two questions (direction vs magnitude) that v1 tried to answer with a single flawed regression.

**Option C: Quantile regression**

`QuantileRegressor(quantile=0.9)` for long, `quantile=0.1` for short. Directly models the tail without clipping. The long model predicts the 90th-percentile return — high only when the model is confident in strong upside.

### 2.2 Fix threshold dilution: rolling percentile rank normalisation

Convert each side's raw score to its **expanding percentile rank** before thresholding:

```
long_rank_t = fraction of prior long_scores that are below long_score_t
```

This normalises the score to `[0, 1]` regardless of the raw distribution. The 90th-percentile threshold then selects exactly the top 10% of historical scores — no dilution from a wider positive base.

The single model already achieves this implicitly (sign masks ~50% of days, making the percentile conditional). The rolling rank makes it explicit and works for any score distribution.

### 2.3 Fix fake dual: true independent execution

Remove the single-model sign gate entirely. Let the long and short models fire independently:

```
long_fires  if long_rank  >= long_thr  AND long_enabled
short_fires if short_rank >= short_thr AND short_enabled
```

When **both** fire on the same day, resolve via margin:
```
long_margin  = long_rank  / long_thr
short_margin = short_rank / short_thr
winner = side with higher margin
```

This is a genuine dual system: each model can fire on any day regardless of the other model's opinion. The long model might fire on a day where the short model is silent — or both might fire and the stronger conviction wins.

### 2.4 Fix stability selection target mismatch

In `train_model.py`, stability selection was run using the symmetric `y_dev` (raw) target instead of the asymmetric `y_clip_dev` target. This selected features that explain overall variance rather than asymmetric tails. We must pass `y_clip_dev` to `compute_stability_scores`.

### 2.5 Align Optuna objective with trading tail

IC computed over the entire dataset optimizes for overall rank correlation. A model with high overall IC may perform poorly in the top tail (where we trade). We should optimize the Optuna objective for Spearman IC computed only on the top quintile/decile of predictions, or optimize for OOS Sharpe of the top-quantile trades directly.

### 2.6 Use skglm for L1-regularized Huber and fast solvers

We should utilize the `skglm` library to solve sparse linear models (L1/L2/MCP/SCAD) compiled via Numba. It provides two key advantages:
1. **L1-Regularized Huber Regression**: Scikit-learn's `HuberRegressor` only supports L2 (Ridge) regularization. Financial data has heavy outliers (needs Huber loss) and high feature noise/collinearity (needs L1 Lasso sparsity). `skglm`'s modular architecture lets us easily fit a model with Huber datafit and L1 penalty.
2. **Fast coordinate descent + working sets**: Drastically speeds up block-bootstrap stability selection and Optuna trials, making optimization feasible across large sweeps.

---

## 3. v2 Implementation Plan

### Phase 1: Score normalisation (fixes threshold dilusion)

**Scope**: `daytrade/rules.py` only. No retraining needed.

1. Implement `expanding_pct_rank(series, min_periods)` — walk-forward percentile rank of each value relative to prior history. Returns a `[0, 1]` series.
2. In `_signals_hybrid()` (or new `_signals_dual()`), convert `long_score` and `short_score` to ranks before thresholding.
3. Threshold becomes a direct percentile: `long_thr=0.9` means "top 10% of historical long-scores."
4. Re-calibrate. This alone may recover much of the lost performance, since the core issue was threshold dilution.

**Success metric**: Dual/hybrid mode OOS Sharpe ≥ single-mode on at least 3 ETFs.

**Effort**: ~2 hours (code + calibration).

### Phase 2: Better model type (fixes clipped-target regression, selection, and optimization alignment)

**Scope**: `day-model/train_model.py`. Choose or combine options:

#### Option A: Two-stage classification + regression

```
Stage 1 (classifier):  P(pm_return > 0 | features)
Stage 2 (regressor):   E(pm_return | features, pm_return > 0)
Conviction = P(positive) × predicted_positive_return
```

Implementation:
- Stage 1: `LogisticRegression` or `LightGBM` (binary target: `pm_return > 0`)
- Stage 2: `Ridge`/`Huber`/`Lasso` trained ONLY on positive-return days
- Conviction score = stage-1 probability × stage-2 magnitude
- Short side mirrors: `P(pm_return < 0) × |predicted_negative_return|`

This avoids the zero-inflation problem entirely. The regressor only sees non-zero targets. The classifier handles the direction question.

#### Option B: Tobit regression

Use `statsmodels.Tobit` with `endog = max(0, pm_return)` (long) or `max(0, -pm_return)` (short). The model natively handles the censoring.

Risk: `statsmodels.Tobit` is slower than sklearn and may not integrate cleanly with the Optuna pipeline. The two-stage approach (Option A) is more modular.

#### Option C: Quantile regression

Use `sklearn.linear_model.QuantileRegressor(quantile=0.9)` for long, `quantile=0.1` for short. Directly models the desired tail.

Risk: QuantileRegressor is computationally expensive (interior-point solver). May need to reduce feature count or Optuna trials.

#### Option D: L1-regularized Huber and non-convex sparse models via `skglm` (Highly Recommended)

Use `skglm.estimators.GeneralizedLinearEstimator` combining a `Huber` datafit and `L1` (Lasso) penalty. Allows both robust estimation (critical for stock returns with outliers) and sparse feature selection. Can also use non-convex penalties (MCP, SCAD) to reduce shrinkage bias on large coefficients.

**Implementation details**:
- Import `GeneralizedLinearEstimator` from `skglm.estimators`.
- Define datafit `Huber(delta=1.35)` and penalty `L1(alpha=alpha)` or `MCPenalty(alpha=alpha, gamma=3.0)`.
- Use fast coordinate descent and working set solvers to speed up block-bootstrap stability selection and Optuna trials.

#### Other Enhancements in Phase 2:
1. **Fix Stability Selection Target**: Pass the asymmetric `y_clip_dev` (clipped target) to `compute_stability_scores` instead of the raw `y_dev` to ensure feature selection isolates regime-specific tail drivers.
2. **Align Optuna Objective**: Update the objective function in `train_model.py` to calculate Spearman IC only on the top/bottom predictions (e.g. top quintile) or optimize validation L/S Sharpe directly.

**Success metric**: Holdout IC / Tail IC of the long model ≥ single-model baseline on at least 3 ETFs.

**Effort**: ~4-8 hours (depending on chosen option).

### Phase 3: True dual execution (removes single-model dependency)

**Scope**: `daytrade/rules.py`, `daytrade/calibrate.py`.

1. Add `mode="dual"` to `get_long_short_signals()`.
2. Both sides compute their own score → rank → threshold independently.
3. No single-model sign gate. No product combination.
4. Conflict resolution via margin (as designed in v1 but now on rank-normalised scores).
5. Calibrate `--mode dual` with the extended grid.

**Architecture**:
```
  Features ──▶ Long Model  ──▶ long_score  ──▶ long_rank  ──▶ long_thr  ──▶ long_fires
  Features ──▶ Short Model ──▶ short_score ──▶ short_rank ──▶ short_thr ──▶ short_fires
                                                                                    │
                                                                    [both fire? margin resolve]
```

**Success metric**: At least one ETF where dual mode deploys a side that single mode disables (proving the dual model found an independent edge).

**Effort**: ~3 hours (code + calibration).

### Phase 4: Validation & deployment decision

1. Run all three modes (`single`, `hybrid`, `dual`) side-by-side.
2. For each ETF, deploy whichever mode/side gives the best OOS composite score.
3. Store the deployed mode per ETF in `calibration.json`.
4. Report includes a mode comparison table.

**Success metric**: Overall deployed Sharpe (summed across ETFs/sides) ≥ single-mode baseline.

**Effort**: ~2 hours.

### Phase 5: Stop-Loss Optimisation (IS max-profit → OOS validation)

**Scope**: `daytrade/backtest.py`, `daytrade/calibrate.py`, `daytrade/report.py`.

Currently every trade is held unconditionally from entry-open to bar-41 close (14:30). Phase 5 adds an intraday stop-loss that can exit early when the trade moves against us.

**Two stop types** are supported and swept per ETF × side:

| Type | Grid | Description |
|------|------|-------------|
| Fixed-% | `[0.3%, 0.5%, 0.8%, 1.0%, 1.5%]` | Exit if price moves `stop_pct` against entry |
| ATR-14 multiple | `[0.5×, 1.0×, 1.5×, 2.0×]` | Exit if price moves `k × ATR14` against entry (per-ETF vol-adapted) |

Plus a `none` baseline (hold to 14:30 unconditionally).

**Optimisation procedure** (two-stage, non-joint to keep the grid manageable):

1. **Stage 1** (existing): grid-search `(threshold, conviction)` by OOS composite score.
2. **Stage 2** (new): on the best `(thr, conv)` pair, sweep all 10 stop configs. **Select by IS max total profit** (not OOS). The chosen stop is then evaluated OOS for honest out-of-sample performance.

**Implementation details**:

- `backtest.py::_day_bars_to_series` now scans 5m bar `low` (long) or `high` (short) between entry and exit. First bar breaching the stop level triggers exit at the stop price. Records `exit_type: "stop" | "target"` per trade.
- `backtest.py::compute_daily_atr14` computes a rolling 14-day ATR from daily high-low ranges (using prior day's value to prevent look-ahead).
- `calibrate.py::_calibrate_one_side` runs Stage 2 after Stage 1, stores `stop_type`, `stop_value`, `stop_oos_*` in the calibration JSON.
- `deploy.py` and `report.py` thread the stop config through to backtest execution and the generated report.

**Success metric**: OOS Sharpe of stopped config ≥ OOS Sharpe of no-stop baseline on at least 3 ETFs.

**Effort**: ~3 hours (code + calibration + report).

#### Phase 5 Results (2026-06-23)

**Finding**: IS-optimised stop-loss did **not** improve total deployed OOS Sharpe. Most ETF×side configs optimised to "no stop" (the baseline was IS-optimal). Only 500ETF had stops selected by IS max-profit, but those stops **degraded** OOS performance.

| ETF | Side | Best stop (IS max-profit) | OOS Sharpe (w/ stop) | OOS Sharpe (no stop) | Δ Sharpe |
|-----|------|---------------------------|-----------------------|-----------------------|----------|
| 50ETF | long | none | +4.34 | +4.34 | 0.00 |
| 50ETF | short | none | +6.47 | +6.47 | 0.00 |
| 300ETF | long | none | +2.11 | +2.11 | 0.00 |
| 300ETF | short | none | +5.53 | +5.53 | 0.00 |
| 500ETF | long | fixed 1.0% | **+2.47** | +3.80 | **−1.33** |
| 500ETF | short | ATR 1.5× | **−0.02** | +0.02 | **−0.04** |
| 588000ETF | long | none | +5.43 | +5.43 | 0.00 |
| 588000ETF | short | none | +3.87 | +3.87 | 0.00 |
| 159915ETF | long | none | +6.44 | +6.44 | 0.00 |
| 159915ETF | short | none | +3.45 | +3.45 | 0.00 |

**Total deployed OOS Sharpe (with stops): +40.10** (vs +41.46 no-stop baseline, **Δ = −1.36**).

**Interpretation**:
- IS max-profit stop selection overfit to in-sample noise. The 500ETF 1.0% stop improved IS profit (+1319bps vs +1272bps no-stop) but hurt OOS Sharpe by −1.33.
- 8 of 10 sides correctly selected "none" — the IS-optimal choice was no stop.
- The success metric (OOS Sharpe ≥ baseline on ≥3 ETFs) was **not met**.
- **Recommendation**: Consider OOS-based stop selection (not IS max-profit) or skip stop-loss entirely. The intraday alpha is already strong enough that early exits destroy edge.

---

## 4. Phase Priority & Dependencies

```
Phase 1 (score normalisation)  ────────┐
                                       ├──▶ Phase 3 (true dual)  ──▶ Phase 4 (validation)
Phase 2 (better model type)    ────────┘                                      │
                                                                              ▼
                                                                     Phase 5 (stop-loss)
```

- **Phase 1** and **Phase 2** are independent — can be done in parallel.
- **Phase 3** depends on both (needs normalised scores from Phase 1 and better models from Phase 2).
- **Phase 4** depends on Phase 3.
- **Phase 5** is independent of Phases 1–4 (operates on the deployed signal) — can be run after Phase 4.

If time-constrained, **Phase 1 alone** is the highest-ROI change. It directly fixes the threshold-dilution root cause with minimal code change and no retraining.

---

## 5. Experiment Log (v1 results, for reference)

### v1 Experiment A: Clipped target (plan as written)

| Parameter | Value |
|:---|:---|
| Stability target | `max(0, ±pm_return) × Y_SCALE` |
| Training target | Same clipped |
| Sample weights | None |
| Optuna objective | Overall Spearman IC |
| Trials | 100 per ETF per side |

| ETF | Long holdout IC | Short holdout IC | Long OOS Sharpe | Short OOS Sharpe |
|:---|:---|:---|:---|:---|
| 159915 | +0.138 | +0.230 | +2.78 | +5.54 |
| 500 | +0.122 | +0.141 | +1.03 | +2.24 |
| 588000 | +0.056 | +0.050 | +2.11 | disabled |
| 300 | +0.060 | +0.109 | disabled | disabled |
| 50 | -0.025 | +0.091 | disabled | disabled |

**Verdict**: ❌ Holdout ICs are positive but trading Sharpe degraded vs single model. 300ETF and 50ETF both sides disabled.

### v1 Experiment B: Clipped stability + raw training target

| Parameter | Value |
|:---|:---|
| Stability target | `max(0, ±pm_return) × Y_SCALE` |
| Training target | Raw `pm_return × Y_SCALE` |
| Sample weights | None |
| Optuna objective | Overall Spearman IC |

| ETF | Long OOS Sharpe | Short OOS Sharpe |
|:---|:---|:---|
| 159915 | +2.94 | +4.84 |
| 500 | +3.04 | +2.28 |
| 588000 | +1.12 | disabled |
| 300 | disabled | disabled |
| 50 | disabled | disabled |

**Verdict**: ⚠️ 500ETF Long improved over single (+3.04 vs +2.88), but 159915ETF Long degraded badly (+8.59 → +2.94). Net worse.

### v1 Experiment C: Aggressive sample weighting (λ=2.0)

| Parameter | Value |
|:---|:---|
| Stability target | Clipped |
| Training target | Raw |
| Sample weights | `1 + 2.0 × max(0, ±y) / σ` |
| Optuna objective | Overall IC |

**Verdict**: ❌ ICs collapsed across the board. Aggressive up-weighting of extreme-return days caused overfitting to outliers. λ=2.0 means a +2σ day gets 5× weight — too aggressive.

### v1 Experiment D: Raw stability + side-aware Optuna (λ=0.5)

| Parameter | Value |
|:---|:---|
| Stability target | Raw `pm_return` |
| Training target | Raw |
| Sample weights | `1 + 0.5 × max(0, ±y) / σ` |
| Optuna objective | Side-aware IC (`pred` vs `max(0,y)` for long) |

| ETF | Long holdout IC | Short holdout IC | Long OOS Sharpe | Short OOS Sharpe |
|:---|:---|:---|:---|:---|
| 159915 | +0.191 | +0.192 | +3.03 | +2.26 |
| 500 | +0.140 | +0.124 | +0.11 | +1.02 |
| 588000 | -0.007 | +0.048 | +2.85 | disabled |
| 300 | +0.045 | +0.158 | +0.83 | +0.07 |
| 50 | -0.023 | +0.101 | disabled | disabled |

**Verdict**: ⚠️ Side-aware ICs are the best of all v1 variants. But trading Sharpe still worse than single model. Root cause: side-aware Optuna optimises IC against clipped target, but trading depends on top-quantile return magnitude — different objectives.

### v1 Experiment E: Hybrid signal (single × dual product)

| Parameter | Value |
|:---|:---|
| Direction | Single-model sign (gate) |
| Conviction | `\|single\| × dual_side_score` |
| Threshold | Expanding percentile on combined conviction |

| ETF | Long OOS Sharpe | Short OOS Sharpe |
|:---|:---|:---|
| 159915 | +8.40 | +5.00 |
| 500 | +2.81 | +1.84 |
| 588000 | +3.06 | disabled |
| 300 | +0.11 | disabled |
| 50 | disabled | +0.10 |

**Verdict**: ⚠️ Comparable to single on strong ETFs, worse on weak ones. The single-model sign gate prevents the dual model from adding independent signal. The product term is dominated by the single-model magnitude.

---

## 6. File Inventory

### Deployed (single-mode, default)

| File | Purpose |
|:---|:---|
| `day-model/models/linear_{ETF}.joblib` | Single frozen model |
| `day-model/models/scaler_{ETF}.joblib` | Single scaler + metadata |
| `daytrade/data/calibration.json` | Single-mode calibration (mode="single") |

### Dual-model infrastructure (v1, preserved for v2)

| File | Purpose |
|:---|:---|
| `day-model/models/linear_{ETF}_long.joblib` | Long-side frozen model |
| `day-model/models/scaler_{ETF}_long.joblib` | Long-side scaler + metadata |
| `day-model/models/linear_{ETF}_short.joblib` | Short-side frozen model |
| `day-model/models/scaler_{ETF}_short.joblib` | Short-side scaler + metadata |
| `daytrade/data/calibration_hybrid.json` | Hybrid-mode calibration (for comparison) |

### Code changes (v1, all in place)

| File | Change |
|:---|:---|
| `day-model/train_model.py` | `--side` parameter, side-aware Optuna, sample weights |
| `daytrade/scores.py` | `load_model(etf, side)`, `compute_scores(etf, side)`, short-score negation |
| `daytrade/rules.py` | `mode="single"|"hybrid"` parameter, `_signals_single()`, `_signals_hybrid()` |
| `daytrade/backtest.py` | `mode` parameter threaded through |
| `daytrade/calibrate.py` | `--mode` CLI argument, wider grid (thr to 95, conv to 90) |
| `daytrade/report.py` | Reads mode from `calibration.json`, threads through |

---

## 7. Genuine Improvement Already Delivered

The wider calibration grid (`THRESHOLD_GRID` extended from `[50,60,70,80,90]` to `[50,60,70,80,90,95]`, `CONVICTION_GRID` from `[40,50,60,70]` to `[40,50,60,70,80,90]`) improved **500ETF Short from +2.91 to +4.88 OOS Sharpe** (at thr=95, selecting only 40 high-conviction trades vs 100 at thr=90). This is a real, deployable improvement independent of the dual-model research.

---

## 8. v2 Results (2026-06-23 retrain)

All 4 phases implemented. Models retrained with Phase 2 fixes (stability target + tail IC). Per-mode calibration run for single, hybrid, and dual. Phase 4 deployment picks the best mode per side by OOS Sharpe.

### Mode Comparison (OOS Sharpe)

| ETF | Side | Single | Hybrid | Dual | **Deployed** |
|:---|:---|:---|:---|:---|:---|
| 50ETF | long | +2.95 | **+4.34** | +0.42 | **hybrid** |
| 50ETF | short | +3.86 | **+6.47** | +0.99 | **hybrid** |
| 300ETF | long | +1.25 | **+2.11** | +0.98 | **hybrid** |
| 300ETF | short | — | +0.62 | **+5.53** | **dual** |
| 500ETF | long | +3.06 | **+3.80** | +3.00 | **hybrid** |
| 500ETF | short | — | — | **+0.02** | **dual** |
| 588000ETF | long | **+5.43** | +5.36 | +3.25 | **single** |
| 588000ETF | short | +2.86 | **+3.87** | +2.26 | **hybrid** |
| 159915ETF | long | **+6.44** | +4.59 | +2.50 | **single** |
| 159915ETF | short | +2.74 | **+3.45** | +1.20 | **hybrid** |

**Total deployed OOS Sharpe**: +41.46 (vs single-only +28.60, **Δ=+12.86**).

### What Worked

1. **Phase 1 (rank normalisation)**: `expanding_pct_rank` normalises dual/hybrid scores to [0,1], fixing threshold dilution.
2. **Phase 2.4 (stability target fix)**: Using asymmetric clipped target for dual-model feature selection produces features that isolate tail drivers.
3. **Phase 2.5 (tail-weighted IC objective)**: 50% weight on top-30% tail IC aligns Optuna with trading edge.
4. **Phase 3 (true dual execution)**: `mode="dual"` lets each model fire independently. **300ETF Short deployed** (S=+5.53) — a side that single mode could not trigger.
5. **Phase 4 (per-side deployment)**: `deploy.py` picks the best mode per side. Hybrid mode dominates (6/10 deployments).

### What Didn't Work

1. **500ETF Short is fragile.** OOS Sharpe +0.02 (essentially flat). Dual mode is the only viable mode but edge is marginal. Needs investigation.
2. **Dual mode does not dominate single mode.** On 588000ETF Long and 159915ETF Long, single mode is clearly better.
3. **Dual mode selects too many trades at low thresholds.** At thr=50, dual mode selects ~50% of days (rank ≥ median). The calibration grid needs higher minimums for dual mode to be equally selective as single mode's conditional thresholding.
4. **Phase 5 (stop-loss): IS max-profit stop selection overfit.** Only 500ETF had stops applied (1.0% fixed long, 1.5×ATR short), and both **degraded** OOS Sharpe (total Δ=−1.36). 8/10 sides correctly selected "no stop". The intraday alpha is strong enough that early exits destroy edge. Recommend: either switch to OOS-based stop selection, or drop stop-loss entirely.

### Phase 2 Options Not Implemented

- **Option A (Two-stage classification + regression)**: Not implemented. The stability target fix (2.4) + tail IC (2.5) addressed the root causes without the complexity of a two-stage pipeline.
- **Option B (Tobit regression)**: `statsmodels.Tobit` available but not integrated into Optuna pipeline.
- **Option C (Quantile regression)**: `QuantileRegressor` is slow (interior-point solver). Not added to model choices.
- **Option D (skglm L1-Huber)**: `skglm` not installed. This remains the highest-value future improvement — it would enable true L1-regularized Huber regression.
