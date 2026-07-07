# Day-Model Feature Expansion & Return Prediction Workflow

Workflow for day-model feature generation and multi-metric linear return predictor optimization.
Read [day-model_plan.md](file:///home/hallo/Documents/option-longterm/day-model/day-model_plan.md) for logic. Update both files when logic changes.

## Target Definition
* **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
* **Entry**: 10:00 (bar 5 closes at 10:00, entry at open of bar 6)
* **Exit**: 14:35 (close of bar 42)
* **Underlying**: Log return from 10:00 to 14:35 across all 5 ETFs.

## Workflow

```bash
# 1. Re-generate parquet feature datasets
python3 day-model/build_features.py -e all

# 2. Train BOTH long and short side models per ETF (DEFAULT)
python3 day-model/train_model.py -e all --trials 100
# Cap trials at 100 to prevent overfit risk.

# 3. Generate summary REPORT.md and plots
python3 day-model/generate_report.py
```

### Side-Specific Objective (`--both` default | `--side single|long|short`)

Feature pipeline (screening → CSS → VIF → CPCV) unchanged. Only validation objective (V2) and lockbox Tail IC side-aware:

| Side     | Tail IC definition (V2)                | V1..V4 weights              |
| :---     | :---                                   | :---                        |
| `single` | two-sided: top 10% + bottom 10% (legacy) | `[0.40, 0.40, 0.15, 0.05]` |
| `long`   | top-only: `pred >= P85(pred)` (top 15%) | `[0.35, 0.50, 0.15, 0.00]` (V4 dropped, renormalized) |
| `short`  | bot-only: `pred <= P15(pred)` (bot 15%) | `[0.35, 0.50, 0.15, 0.00]` (V4 dropped, renormalized) |

* CV fold metrics M1..M6 and kill-switches stay two-sided for all sides.
* Side stored in `results_{tag}.json` and `scaler_{tag}.joblib` under `side` field.
* `tag = {ETF}` for `single`, `{ETF}_long` / `{ETF}_short` otherwise.
* Pilot cache (`cache_pilot_*`) side-scoped via hash: cache key includes `"v11_side", side` when `side != "single"`. Selection and LOYO caches side-independent.
* Lockbox Tail IC in `generate_report.py` side-aware.

```bash
# Default: train both long and short for each ETF
python3 day-model/train_model.py -e 300 --trials 100
python3 day-model/train_model.py -e all --trials 100

# Train ONE specific side only (disables --both)
python3 day-model/train_model.py -e 300 --no-both --side single --trials 100
python3 day-model/train_model.py -e 300 --no-both --side long   --trials 100
python3 day-model/train_model.py -e 300 --no-both --side short  --trials 100
```

### train_model.py Performance & Experiment Options

```bash
python day-model/train_model.py -e 300 -t 200             # cache ON, n_jobs=cpu_count
python day-model/train_model.py -e 300 --no-cache          # force recompute
python day-model/train_model.py -e 300 --skip-step 2       # skip Step 2 (CSS/VIF/Condition) filter (Step 1 skipped by default)
python day-model/train_model.py -e 300 --optuna-jobs 8     # cap Optuna workers
python day-model/train_model.py -e 300 --optuna-jobs 1     # sequential (100% deterministic)
python day-model/train_model.py -e 300 --bootstrap-jobs 8  # cap stability-bootstrap workers
python day-model/train_model.py -e 300 --loyo-jobs 4       # cap LOYO fold workers per trial
```

Speedups: fp32 arrays, vectorized Spearman screen, parallel stability bootstrap & CPCV folds, disk caches, precomputed unweighted scaled matrix, numpy-vectorized yearly metrics, GIL bypass via Optuna JournalStorage, local BLAS pin = 1, skglm `AndersonCD(max_epochs=2000)`, seeded TPESampler.

* **CPCV parallelism**: `--loyo-jobs -1` (auto = `cpu_count // optuna-jobs`). Cap to prevent core oversubscription.

### Pipeline Constants Sweep (`day-model/sweep/`)

Tune the 5 feature-selection pipeline constants via Optuna instead of grid search:

```bash
# Meta-Optuna: all 5 constants + model hyperparams in one TPE study (~200 trials, < 2 min)
python day-model/sweep/meta_optuna.py -e all --side single --trials 200 --bootstrap-jobs 4

# Single-constant grid sweep (legacy)
python day-model/sweep/sweep_constants.py -e 300 --constant SCREEN_FDR --values 0.15,0.25,0.50,0.80
python day-model/sweep/sweep_constants.py -e 300 --constant STABILITY_B --values 40,60,80,120
```

Output CSVs and Optuna logs go to `day-model/sweep/`. See `day-model/day-model_plan.md` Section 8 for decision rules.

## Cache invalidation

`train_model.py` writes three caches per ETF in `day-model/data/`:

| File | Contents |
|---|---|
| `cache_select_{etf}_{hash}.joblib` | `screen_mask`, `p_vals`, `rhos`, `stability_selected_idx`, `stability_scores` (version `v10` key; side-independent) |
| `cache_loyo_{etf}_{hash}.joblib` | CPCV folds `(test_idx, X_tr_scaled, X_te_scaled, y_tr)` (version `v10` key; side-independent) |
| `cache_pilot_{etf}_{hash}.joblib` | Pilot records `[{params, raw_metrics, val_metrics}]` (version `v11_side` key for long/short; side-scoped) |

**Auto-invalidated** when these change:
* ETF name
* `len(FEATURES)`
* `features_{etf}.parquet` mtime
* Selection Train shape
* `STABILITY_B`, `STABILITY_PI`, `SCREEN_FDR`
* `SELECTION_VAL_DATE`
* `TARGET` column
* Selected-feature indices
* `PILOT_N_TRIALS`, `PILOT_SEED`
* `--side` (only for `long`/`short` via `"v11_side"`)

**Manual clear required when**:
* Editing `FEATURES` list in `build_features.py` without regenerating parquet.
* Changing `METRIC_WEIGHTS` or `SIDE_CONFIG` weights (clear `cache_pilot_*`).
* Editing `side_tail_ic` semantics in `train_model.py` (clear `cache_pilot_*`).
* Changing CPCV group/test window logic, embargo, or scaling in `_compute_loyo`.
* Changing screening or stability selection internals.
* Changing hierarchical clustering thresholds/metrics for CSS.

**Purge all caches**:
```powershell
Remove-Item day-model\data\cache_*.joblib
```

## Remade Predictor Architecture

1. **Lockbox Split (Step 0)**: Hold out days $\ge 2024-03-01$ (OOS data untouched during training).
2. **Selection Validation Split (Step 0.5)**: 6 non-contiguous 3-month blocks (~370 days) for validation. 4 Inner blocks for Optuna tuning; 2 Outer blocks for generalization check. 10-day embargo at boundaries.
3. **BH-FDR Screening (Step 1 - Bypassed)**: Bypassed by default. Univariate screening is not working because dropping features with low marginal linear correlation discards key joint predictive power, causing feature starvation and model collapse.
4. **CSS + VIF Pruning (Step 1)**: Complete Linkage hierarchical clustering (threshold $t=0.25$, $|r| \ge 0.75$) on all candidate features. Subsampling ($B=50$) ElasticNet path votes aggregated at cluster level. Keep clusters selected in $\ge 75\%$ subsamples with max $Q=18$ active clusters. Pick representative with highest individual score. Apply iterative VIF pruning (VIF threshold 10.0) on representatives.
5. **Loss Weighting (Step 2)**: Power weights $w(y_i) = |y_i|^k$. Scale inputs by $\sqrt{w}$.
6. **CPCV with Embargo (Step 3)**: 6 groups, 2 test groups (15 folds), 10-day embargo at test boundaries. Run on selection train.
7. **Pilot Normalization (Step 3.1)**: Run 50 pilot trials to compute median and MAD for validation z-scores.
8. **Objective Function**: Maximize weighted sum of normalized validation metrics + ESS soft penalty under 20%.
9. **Signed Constraints & TPESampler**: Hard constraints (Overall IC > 0, Hit Rate $\ge 60\%$, Monotonicity > 0.25, Spread > 0, Active features $\le ESS / 9$, Gini concentration $\le 0.85$ soft limit). Violation prunes trial.
10. **One-Shot Evaluation & Plots (Step 5)**: Refit on working set using best parameters. Save final model and scaler. Evaluate OOS lockbox via `generate_report.py` (side-aware Tail IC). Plot 15 diagnostic panels. Run block bootstrap (B=1000, block size 10) for 95% CIs.
11. **Unified L1/L2 Regularization Manifold**: Unified `GeneralizedLinearEstimator` using Huber datafit and `MCP_plus_L2(alpha*rho, gamma, alpha*(1-rho))` penalty. Regularization is continuously tuned via total budget (`unified_alpha`) and sparse-vs-ridge mix (`unified_rho`).
12. **Deflation & Overfit Diagnostics**: Compute running Deflated Objective. Compute PBO and Performance Degradation using CSCV.
13. **Model Quality**: Calculate condition numbers, ESS, and Gini coefficient.
14. **Plateau Parameter Selection**: Select trial residing in the most stable hyperparameter plateau (radius $r=0.25$) using deflated objective.

## Stability & Overfit Upgrades (July 2026)

Upgraded model training stability, tail performance, overfit diagnostics, and decay monitoring:

1. **Bootstrap Bagging Feature Selector (Soloff et al. 2024 JMLR)**:
   - Wraps final model fit in bootstrap aggregation ($B=100$) over Selection Train.
   - Computes feature inclusion frequency. Keeps features with inclusion frequency $> 50\%$.
   - Prevents sparse selector collapse to 2-3 active features on small samples.
   - Refits final model on Working set restricted to bagged features.

2. **Soften Tail IC to 15% (P85/P15)**:
   - Uses 15% threshold for `long` and `short` sides in `side_tail_ic` and `side_tail_mask`.
   - Long/short validation weights set to `[0.35, 0.50, 0.15, 0.00]`.

3. **Two-Sided CV Folds & Side consistency constraints**:
   - Standard CV fold metrics `m1..m6` and standard kill-switches are forced to stay two-sided (`side="single"`).
   - If `side != "single"`, two new side-specific consistency constraints are appended:
     - `side_m2 > 0` (side-specific Yearly Tail IC Mean > 0)
     - `side_m3 >= 50%` (side-specific Hit Rate >= 50%)
   - Prevents side-specific fold-level sign flips while keeping overfit guardrails intact.

4. **Decoupled Ridge Fallback, Unified Manifold & Live Conditioning**:
   - Removed legacy categorical models and static pre-decision `force_ridge`. The optimizer operates on a continuous unified manifold (`MCP_plus_L2` penalty) spanning Ridge ($\rho \to 0$) to aggressive non-convex MCP ($\rho \to 1$, small $\gamma$).
   - Live per-trial regularized condition number check: rejects/prunes trial if regularized Gram matrix condition number (`reg_kappa`) exceeds `10000.0`.
   - Added SVD-based condition number check post-VIF (`run_cond_pruning`) to iteratively drop the feature with the largest loading on the smallest singular vector until raw cond < 100.0, catching multi-feature near-collinearity.
   - Dynamic VIF thresholding: `5.0` for highly ill-conditioned `50ETF`, default `10.0` for other ETFs.
   - Added graduated soft penalty on the condition number `cond_penalty = -0.1 * max(0, log(reg_kappa) - log(1000.0))` to guide TPE sampler toward well-conditioned parameter spaces before hitting the hard prune cliff.

5. **No-Fallback Pipeline (July 2026)**:
   - Removed all safety-net fallbacks from the feature-selection pipeline:
     - `SCREEN_FALLBACK_K` (top-K by p-value when BH-FDR < 40) → removed. Pure BH-FDR.
     - CSS cluster force-top5 (when < 3 clusters pass pi) → removed. Pure pi threshold.
     - Bagging top-3 (when no features > 50% inclusion) → removed. Pure > 50% bagging.
   - Constants tuned via meta-Optuna (`day-model/sweep/meta_optuna.py`): 5 pipeline constants + model hyperparams in single TPE study.
   - **Tuned constants**: reference day-model/train_model.py

6. **Monthly Blocked Validation Bootstrap Regularization**:
   - Perform $B=100$ monthly blocked bootstrap resamples on the inner validation set.
   - Subtract standard deviation of bootstrapped tail ICs from raw validation Tail IC:
     $$V_{tail\_ic\_adj} = val\_tail\_ic - 1.0 \times \sigma_{boot\_tail\_ic}$$
   - Penalizes unstable validation scores and steers Optuna to robust configurations.

7. **Model Confidence Set (MCS) & Bayesian True Discovery**:
   - Hansen's MCS (sequential t-test, alpha=10%) identifies statistically indistinguishable trials.
   - Empirical Bayes posterior probability of true discovery $P(\theta_{OOS} > 0 | data)$ logs discovery confidence.

7. **Quarterly Rolling Refit decay check**:
   - Runs `run_quarterly_rolling_refit_test` post-lockbox.
   - Compares Static vs Rolling Model performance on quarterly windows (QuantBench method).
