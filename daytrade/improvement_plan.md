# Daytrade — Asymmetric Dual-Model Overhaul Plan

Transition day-trading layer from single regression model to two independent, asymmetric models per ETF: `long_model` (upside specialist) and `short_model` (downside specialist).

---

## 0. Status: IMPLEMENTED — Findings & Revised Architecture

**Date**: 2026-06-22  
**Verdict**: Dual-model training infrastructure fully implemented. Pure dual-model deployment does **not** improve OOS Sharpe over the proven single-model approach. A **hybrid mode** (single model for direction × dual model for conviction) is available but also does not consistently beat single-mode. **Single-model remains the deployed default.**

### What was built

| Component | Status | Files |
|:---|:---|:---|
| `train_model.py --side long\|short\|both` | ✅ Implemented | `day-model/train_model.py` |
| Dual-model artifacts (`linear_{ETF}_long.joblib` etc.) | ✅ Trained (100 trials each) | `day-model/models/` |
| `scores.compute_scores(etf, side)` | ✅ Implemented | `daytrade/scores.py` |
| `rules.get_long_short_signals(mode="single"\|"hybrid")` | ✅ Implemented | `daytrade/rules.py` |
| `calibrate --mode single\|hybrid` | ✅ Implemented | `daytrade/calibrate.py` |
| Wider calibration grid (thr up to 95, conv up to 90) | ✅ Implemented | `daytrade/calibrate.py` |

### Experiments run (4 dual-model training variants + 2 signal modes)

| Variant | Stability target | Training target | Sample weights | Optuna objective | Result |
|:---|:---|:---|:---|:---|:---|
| **A: Clipped target** (plan as written) | `max(0, ±pm_return)` | clipped | none | overall IC | ❌ 300ETF & 50ETF disabled |
| **B: Clipped stability + raw training** | clipped | raw `pm_return` | none | overall IC | ⚠️ 500ETF L improved +0.16; rest degraded |
| **C: Aggressive sample weighting** | clipped | raw | λ=2.0 | overall IC | ❌ ICs collapsed (overfits outliers) |
| **D: Raw stability + side-aware Optuna** | raw | raw | λ=0.5 | side-aware IC | ⚠️ holdout ICs good, trading Sharpe still worse |
| **Hybrid signal** (single×dual product) | — | — | — | — | ⚠️ comparable but not better than single |

### Why dual models underperform (root cause analysis)

**Diagnosis on 159915ETF long** (the strongest signal ETF, where degradation was most visible):

| Metric | Single model | Dual model |
|:---|:---|:---|
| OOS Spearman IC (overall) | +0.20 | +0.19 (dual long) |
| OOS Long-side IC (vs `max(0,pm_return)`) | +0.10 | **+0.19** (higher!) |
| Top-10% long picks: mean return | **+0.99%** | +0.29% |
| Top-10% long picks: win rate | **79.3%** | 61.8% |
| Trades selected at thr=90 | 29 | 55 |

The dual model has **higher side-specific IC** but **worse actual top picks**. Root cause:

1. **Threshold base dilution**: The single model computes the expanding percentile threshold over **positive-score days only** (~50% of all days). The dual model computes it over all days where `long_score > 0` (~67%+ for most ETFs). A lower percentile base → lower threshold → more trades selected → worse average quality.

2. **Feature selection information loss**: Clipping the target to `max(0, pm_return)` zeroes out ~50% of training labels. The Lasso block-bootstrap stability selection sees a target with many ties at zero, making feature importance noisier. The selected features are good at classifying "is this a positive day?" but worse at ranking "how positive will it be?"

3. **Score distribution shift**: The single model's score is centered near zero (mean ≈ 0, since `pm_return` has mean ≈ 0). Sign cleanly partitions long/short. Dual model scores are positive-biased (the model predicts "some upside" for most days), making percentile thresholds less discriminating.

### Conclusion

The original single-model architecture already provides effective asymmetric signal:
- **Sign of score → direction** (natural long/short separation)
- **|Score| → conviction** (magnitude as confidence)
- **Masked expanding percentile → per-side threshold** (conditioned on each side's own history)

The plan's premise that separate models would improve this was not supported by the data. The single-model approach is retained as default, with the dual-model infrastructure preserved for future research.

### Genuine improvement delivered

The wider calibration grid (`THRESHOLD_GRID` extended to 95, `CONVICTION_GRID` to 90) improved **500ETF Short from +2.91 to +4.88 OOS Sharpe** (at thr=95, selecting only 40 high-conviction trades).

---

## 1. Architecture Comparison

```
Current Single-Model Architecture (DEFAULT, PROVEN):
  Features ──▶ Scaler ──▶ Single Model (Lasso/Huber) ──▶ Signed Score
                                                             │
                                     ┌───────────────────────┴───────────────────────┐
                                     ▼                                               ▼
                                 Score > 0                                        Score < 0
                                     │                                               │
                       long_thr (expanding pct on pos-score days)     short_thr (expanding pct on neg-score days)
                                     │                                               │
                                     ▼                                               ▼
                                 Long Fire                                       Short Fire

Dual-Model Architecture (IMPLEMENTED, not deployed by default):
  Features ──▶ Scaler Long  ──▶ Long Model  ──▶ Long Conviction Score ──▶ long_thr ──▶ Long Fire
  Features ──▶ Scaler Short ──▶ Short Model ──▶ Short Conviction Score ──▶ short_thr ──▶ Short Fire
                                                                                      │
                                                                            [Conflict Resolution]

Hybrid Mode (OPTIONAL via mode="hybrid"):
  Single Score ──▶ direction (sign)
  Single Score ──▶ |score| ──┐
  Dual Long Score ──────────▶│ product ──▶ long_thr ──▶ Long Fire (requires both models to agree)
  Dual Short Score ─────────▶│ product ──▶ short_thr ──▶ Short Fire
```

| Axis | Single Model (Default) | Dual Model (Available) |
| :--- | :--- | :--- |
| **Model Files** | `linear_{ETF}.joblib`, `scaler_{ETF}.joblib` | `linear_{ETF}_long.joblib`, `linear_{ETF}_short.joblib`<br>`scaler_{ETF}_long.joblib`, `scaler_{ETF}_short.joblib` |
| **Training Target** | `pm_return` (continuous, signed) | Same raw target; stability selection uses clipped target for asymmetric feature selection |
| **Direction** | Sign of score | Sign of single-model score (hybrid) or score sign (pure dual) |
| **Conviction** | \|score\| (masked per side) | \|single\| × dual_score (hybrid) or dual_score (pure) |
| **Threshold Base** | Same-sign history only | All positive-conviction days |
| **Conflict Resolution** | Not needed (mutually exclusive by sign) | Margin-based (score/threshold) |
| **OOS Sharpe** | **Proven** (159915 L: +8.59, 500 L: +2.88) | Worse or comparable, never better on average |

---

## 2. Deployed Results (single-mode, 15 bps RT)

| ETF | Long OOS Sharpe | Short OOS Sharpe | Notes |
|:---|:---|:---|:---|
| **159915ETF** | thr=50 c=90, S=+8.59 | thr=50 c=80, S=+6.16 | **Best name, both sides robust** |
| **500ETF** | thr=50 c=40, S=+2.88 | **thr=95 c=40, S=+4.88** | Short improved via wider grid (+2.91→+4.88) |
| **588000ETF** | thr=50 c=90, S=+3.51 | disabled | Long-only |
| **300ETF** | thr=50 c=80, S=+0.17 | thr=50 c=90, S=+2.21 | Short side is the edge |
| **50ETF** | disabled | thr=50 c=80, S=+0.67 | Fragile (short only) |

---

## 3. How to Use Dual Models (for future research)

```bash
# 1. Train dual models (already done, but to re-train):
python day-model/train_model.py -e all --side both --trials 100

# 2. Calibrate in hybrid mode:
python -m daytrade.calibrate --mode hybrid

# 3. Generate report (reads mode from calibration.json):
python -m daytrade.report

# 4. To revert to single-model:
python -m daytrade.calibrate --mode single
python -m daytrade.report
```

Dual model artifacts:
- `day-model/models/linear_{ETF}_long.joblib`, `scaler_{ETF}_long.joblib`
- `day-model/models/linear_{ETF}_short.joblib`, `scaler_{ETF}_short.joblib`
- `day-model/data/results_{ETF}_long.json`, `results_{ETF}_short.json`

---

## 4. Step-by-Step Task Checklist (COMPLETED)

- [x] **Step 1: Modify `day-model/train_model.py`** — Added `--side` parameter, asymmetric stability targets, sample-weighted training
- [x] **Step 2: Train all models** — `python day-model/train_model.py -e all --side both --trials 100`
- [x] **Step 3: Modify `daytrade/scores.py`** — `load_model(etf, side)`, `compute_scores(etf, side)`, short-score negation
- [x] **Step 4: Modify `daytrade/rules.py`** — `get_long_short_signals(mode="single"|"hybrid")` with conflict resolution
- [x] **Step 5: Modify `daytrade/backtest.py` & `calibrate.py`** — `mode` parameter threaded through
- [x] **Step 6: Run Calibrate & Report** — Both single and hybrid modes calibrated and compared
- [x] **Finding**: Single-mode retained as default; hybrid available but not better

---

## 5. Future Research Directions

If revisiting dual models, consider:

1. **Expanding-window percentile rank** instead of raw-score percentile for threshold — normalizes the score distribution, may fix the threshold-base dilution issue
2. **Quantile regression** (`QuantileRegressor` with `quantile=0.9` for long, `0.1` for short) — directly models tail behavior without clipping
3. **Classification objective** — train as binary classifier (positive-return day vs not) instead of regression on clipped target
4. **Ensemble weighting** — tune the single/dual blend weight per ETF via Optuna rather than fixed product
