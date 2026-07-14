# Frozen Feature Selection vs Quarterly CSS

> **Research question**: Can a manually curated, stable feature set outperform quarterly CSS for the production pipeline?

> **Scope**: Only the feature selection stage changes. Everything else (datasets, splits, Optuna search, model family, VIF, lockbox, metrics) is identical across arms.

## TL;DR

**Case 3 — Neither frozen arm beats CSS.** Feature reselection is NOT the source of instability. Investigate other causes (regime, model family, etc.).

- **Primary metric (OOS strategy Sharpe, paired Wilcoxon):**
  - Handpick vs CSS: median diff +0.000, p = 0.867 (not significant)
  - Random vs CSS: median diff -1.228, p = 0.371 (not significant)
- **Residual variance** (unexplained by quarter + ETF/side): Arm A 69.7%, Arm B 60.3%, Arm C 63.8%. Absolute residual variance is essentially identical across arms (~48.0 for A vs ~48.0 for B), so the frozen set does NOT meaningfully reduce unexplained variance.
- **Robustness:** Arm B trained 120/120 models successfully. Arm C collapsed on 8/120 (random features lack signal stability under bootstrap bagging). This is independent evidence that handpicked features are more stable than random ones — but stability alone does not translate into better OOS Sharpe.

---

## Experimental Setup

### Three Arms

| Arm | Feature Selection | Side-Independent | Frozen Across Quarters |
|-----|-------------------|------------------|-----------------------|
| **A (CSS baseline)** | Quarterly CSS + VIF + cond pruning | yes | no (re-selected each quarter) |
| **B (Handpicked)** | Features in >=6/8 historical quarters, topped up to median CSS size, then VIF+cond | yes | **yes** |
| **C (Random placebo)** | Random sample of same size as B (seed 42 + per-ETF hash), then VIF+cond | yes | **yes** |

All arms use the same:
- Datasets (`features_{ETF}.parquet`)
- Train/validation/test splits (6-year rolling window, 4 inner + 2 outer 3-month validation blocks, lockbox = quarter start)
- Optuna search space (`unified_alpha`, `unified_rho`, `unified_gamma`, `huber_delta`, `k_weight`)
- Model family (`MCP_plus_L2` Huber datafit, generalized linear estimator)
- VIF threshold (5.0 for 50/159915 ETFs, 12.0 otherwise) + condition number pruning (cond < 100)
- CPCV bagging, sortino V5 objective, CPCV path blending
- 8 quarters (2024Q1-2025Q4) x 5 ETFs x 3 sides = up to 120 observations per arm
- 100 Optuna main trials (+ 200 pilot trials for normalization)
- Signal threshold = P90, transaction cost = 15 bps

### Arm B Frozen Feature Lists

Built from historical CSS outputs (`results_*_r{quarter}_sortino_blended.json`). Count per-feature selection frequency across 8 quarters; keep features selected in >=6/8; top up to each ETF's median historical CSS size with highest-frequency remaining features.

| ETF | Unique in history | >=6/8 | Median CSS size | Arm B size |
|-----|------------------:|------:|----------------:|-----------:|
| 300ETF | 40 | 10 | 19 | 19 |
| 500ETF | 34 | 6 | 15 | 15 |
| 50ETF | 42 | 10 | 19 | 19 |
| 588000ETF | 41 | 15 | 23 | 23 |
| 159915ETF | 34 | 6 | 16 | 16 |

### Arm C Placebo

Random sample of `Arm B size` features from the 214-feature pool, per ETF. Seed = 42 + per-ETF hash offset (single canonical seed, per-ETF variation for independence).

---

## Results

### Model Training Status

Each arm targets 120 models (5 ETFs x 3 sides x 8 quarters).

| Arm | Trained OK | Failed during training | Total |
|-----|-----------:|-----------------------:|------:|
| Arm A (CSS (baseline)) | 120 | 0 | 120 |
| Arm B (Handpicked frozen) | 120 | 0 | 120 |
| Arm C (Random frozen (placebo)) | 112 | 8 | 120 |

**Models that failed to train** (all in Arm C; bootstrap bagging filtered all features due to <50% inclusion frequency — random features lack signal stability):

- Arm C / 300ETF / short / 2024Q4
- Arm C / 300ETF / short / 2025Q1
- Arm C / 300ETF / short / 2025Q2
- Arm C / 300ETF / short / 2025Q3
- Arm C / 300ETF / short / 2025Q4
- Arm C / 588000ETF / long / 2024Q2
- Arm C / 588000ETF / long / 2024Q3
- Arm C / 588000ETF / long / 2024Q4

These failures are themselves a finding: under the production bootstrap-bagging selector (Soloff et al. 2024, >50% inclusion threshold), random feature sets collapse to zero features in ~7% of (ETF, side, quarter) combos. The handpicked Arm B had **zero** such collapses, indicating its features carry more consistent signal — but this robustness advantage does not translate into better OOS Sharpe (see below).

### 1. Paired Sharpe Comparison (Primary Metric)

OOS strategy Sharpe (per-trade, annualized by sqrt(252)) over each quarter's 3-month OOS window.

| Arm | N | Mean Sharpe | Median Sharpe | Std |
|-----|--:|------------:|--------------:|----:|
| Arm A (CSS (baseline)) | 120 | +2.3598 | +1.9258 | +8.3023 |
| Arm B (Handpicked frozen) | 120 | +2.3160 | +1.6185 | +8.9207 |
| Arm C (Random frozen (placebo)) | 112 | +2.2881 | +1.9298 | +7.9789 |

#### Wilcoxon Signed-Rank Tests (paired by ETF/quarter/side)

| Comparison | N pairs | Median Arm X | Median Arm A | Median diff (X-A) | Mean diff | X better / A better / ties | p-value |
|------------|--------:|-------------:|-------------:|------------------:|----------:|----------------------------|--------:|
| B vs A (Handpick vs CSS) | 120 | +1.6185 | +1.9258 | +0.0000 | -0.0438 | 58 / 58 / 4 | 0.8665 |
| C vs A (Random vs CSS) | 112 | +1.9298 | +1.9496 | -1.2280 | -0.3508 | 51 / 61 / 0 | 0.3712 |

**Interpretation:** Both p-values are far above 0.05. Neither frozen arm is statistically distinguishable from CSS. The win/loss counts are near 50/50 (58/58 for B vs A; 51/61 for C vs A), exactly what would be expected if freezing has no effect on Sharpe.

#### Secondary Metrics (Wilcoxon paired)

**OOS Overall IC**:

| Comparison | N | Median X | Median A | Median diff | p-value |
|------------|---:|---------:|---------:|------------:|--------:|
| B vs A | 120 | +0.0909 | +0.0635 | +0.0113 | 0.1831 |
| C vs A | 112 | +0.0214 | +0.0588 | -0.0432 | 0.0511 |

**OOS Tail IC**:

| Comparison | N | Median X | Median A | Median diff | p-value |
|------------|---:|---------:|---------:|------------:|--------:|
| B vs A | 120 | +0.0753 | +0.0476 | +0.0303 | 0.7675 |
| C vs A | 112 | +0.0648 | +0.0483 | +0.0261 | 0.8640 |

**OOS Total Return**:

| Comparison | N | Median X | Median A | Median diff | p-value |
|------------|---:|---------:|---------:|------------:|--------:|
| B vs A | 120 | +0.7361 | +0.8457 | -0.0563 | 0.6554 |
| C vs A | 112 | +0.7059 | +0.9088 | -0.0711 | 0.5892 |

**OOS Win Rate**:

| Comparison | N | Median X | Median A | Median diff | p-value |
|------------|---:|---------:|---------:|------------:|--------:|
| B vs A | 120 | +0.5420 | +0.5455 | +0.0000 | 0.9718 |
| C vs A | 112 | +0.5192 | +0.5584 | +0.0000 | 0.2241 |

### 2. Per-ETF x Side Sharpe Breakdown

Median OOS Sharpe per (ETF, side, arm), aggregated across 8 quarters.

#### 300ETF

| Side | Arm A | Arm B | Arm B - A | Arm C | Arm C - A |
|------|------:|------:|----------:|------:|----------:|
| single | +2.965 | +0.634 | -2.330 | -3.081 | -6.045 |
| long | +1.029 | +1.053 | +0.024 | -2.391 | -3.420 |
| short | +1.250 | +0.918 | -0.332 | +0.709 | -0.540 |

#### 500ETF

| Side | Arm A | Arm B | Arm B - A | Arm C | Arm C - A |
|------|------:|------:|----------:|------:|----------:|
| single | +1.478 | +3.095 | +1.616 | +0.964 | -0.515 |
| long | +1.801 | +0.725 | -1.076 | +2.916 | +1.115 |
| short | +5.097 | +2.317 | -2.779 | +1.718 | -3.379 |

#### 50ETF

| Side | Arm A | Arm B | Arm B - A | Arm C | Arm C - A |
|------|------:|------:|----------:|------:|----------:|
| single | +3.615 | +1.475 | -2.140 | -1.275 | -4.890 |
| long | -0.818 | +0.951 | +1.769 | +0.346 | +1.164 |
| short | +5.047 | -1.012 | -6.058 | -1.298 | -6.344 |

#### 588000ETF

| Side | Arm A | Arm B | Arm B - A | Arm C | Arm C - A |
|------|------:|------:|----------:|------:|----------:|
| single | -0.342 | +1.371 | +1.713 | +1.337 | +1.680 |
| long | +0.494 | +2.121 | +1.627 | +2.284 | +1.789 |
| short | +1.391 | +0.233 | -1.158 | +10.324 | +8.933 |

#### 159915ETF

| Side | Arm A | Arm B | Arm B - A | Arm C | Arm C - A |
|------|------:|------:|----------:|------:|----------:|
| single | +2.462 | +3.966 | +1.504 | +6.574 | +4.112 |
| long | +3.289 | +1.865 | -1.424 | +6.498 | +3.209 |
| short | +9.368 | +7.723 | -1.645 | +5.914 | -3.454 |

### 3. Residual Variance Decomposition

Total Sharpe variance decomposed (sequential Type I SS): quarter effect first, then ETF+side effect, then unexplained residual.

| Arm | N | Var(Sharpe) | Quarter % | ETF+Side % | **Residual %** |
|-----|--:|------------:|-----------:|------------:|---------------:|
| Arm A (CSS (baseline)) | 120 | 68.9276 | 20.0% | 10.3% | **69.7%** |
| Arm B (Handpicked frozen) | 120 | 79.5797 | 33.3% | 6.4% | **60.3%** |
| Arm C (Random frozen (placebo)) | 112 | 63.6623 | 16.5% | 19.7% | **63.8%** |

**Important nuance — absolute vs relative residual variance:**

The relative residual % is slightly lower for Arm B than Arm A, which superficially suggests freezing reduces unexplained variance. However, this is driven by Arm B having *higher* total variance, not lower absolute residual variance:

| Arm | Var(total) | Residual % | **Var(residual) = total * pct** |
|-----|-----------:|-----------:|-------------------------------:|
| Arm A (CSS (baseline)) | 68.9276 | 69.7% | **48.0149** |
| Arm B (Handpicked frozen) | 79.5797 | 60.3% | **47.9809** |
| Arm C (Random frozen (placebo)) | 63.6623 | 63.8% | **40.6217** |

Absolute residual variance is essentially identical between Arm A (48.01) and Arm B (47.98). The frozen feature set does NOT meaningfully reduce unexplained Sharpe variance.

The dominant variance component is the **quarter effect** (~17-33% across arms), reflecting strong temporal regime shifts. This suggests if instability is the concern, the lever to pull is regime modeling, not feature selection stability.

---

## Decision

Applying the pre-specified decision rules from the experiment plan:

- Handpick > CSS (median diff > 0 AND p < 0.05): **NO** (median diff +0.000, p = 0.867)
- Random > CSS (median diff > 0 AND p < 0.05): **NO** (median diff -1.228, p = 0.371)
- Random ≈ CSS (not significant): **YES**

### Verdict: **Case 3 — Neither frozen arm beats CSS.** Feature reselection is NOT the source of instability. Investigate other causes (regime, model family, etc.).

**Practical implications:**

1. **Do not replace quarterly CSS with a frozen feature set.** The experiment provides no evidence that freezing improves OOS Sharpe.
2. **Do not invest engineering effort in hand-curating a stable feature list** for this pipeline. The signal is not there.
3. **If pipeline instability is the real concern, look elsewhere:** the quarter effect dominates the variance decomposition (~17-33%). Candidate next experiments (all explicitly excluded from this one per the plan):
   - Regime conditioning / VIX conditioning of the model
   - Ensemble of model families rather than feature-set stability
   - Hyperparameter search stability (plateau selection, deflated objective)
   - Different validation block construction (the current 6 non-contiguous 3-month blocks may be the source of instability)
4. **Side note on robustness:** Arm B's zero training-failure rate vs Arm C's ~7% failure rate is real evidence that handpicked features carry more consistent joint signal than random ones. If training-time robustness (not OOS Sharpe) is operationally important, this is a minor point in favor of freezing — but it does not affect the headline conclusion.

---

## Methodology Notes

- **OOS window**: Each rolling model's OOS period is the 3 months following its lockbox date (e.g. 2024Q1 lockbox = 2024-03-01, OOS = 2024-03-01 to 2024-06-01).
- **Strategy simulation**: Within-window percentile rank; long top tail (P85+ for `long`, bot P15- for `short`, both for `single`). Per-trade Sharpe annualized by sqrt(252).
- **Failed models** (Arm C only): excluded from paired tests. Their absence biases Arm C means slightly upward (worst cases dropped), making this a **conservative** test for Arm B's advantage — yet Arm B still does not significantly beat Arm A.
- **Wilcoxon test**: two-sided, paired by (ETF, side, quarter). Reports median difference (X - A).
- **Variance decomposition**: sequential (Type I) sum of squares. `quarter` fitted first, then `etf+side` on residual, leaving unexplained residual variance.
- **Pilot cache reuse:** The Optuna pilot (200 trials for normalization medians/MADs) is keyed by selected-feature indices and reused across quarters within an (arm, etf, side) — this is the existing production behavior and applies identically to all three arms.
- All code: `day-model/build_frozen_features.py`, `day-model/train_frozen_rolling.py`, `day-model/analyze_frozen_vs_css.py`.
- Per-observation metrics: `day-model/data/frozen/arm_metrics_thr90.csv`.
