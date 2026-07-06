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

### train_model.py Performance Options

```bash
python day-model/train_model.py -e 300 -t 200             # cache ON, n_jobs=cpu_count
python day-model/train_model.py -e 300 --no-cache          # force recompute
python day-model/train_model.py -e 300 --optuna-jobs 8     # cap Optuna workers
python day-model/train_model.py -e 300 --optuna-jobs 1     # sequential (100% deterministic)
python day-model/train_model.py -e 300 --bootstrap-jobs 8  # cap stability-bootstrap workers
python day-model/train_model.py -e 300 --loyo-jobs 4       # cap LOYO fold workers per trial
```

Speedups: fp32 arrays, vectorized Spearman screen, parallel stability bootstrap & CPCV folds, disk caches, precomputed unweighted scaled matrix, numpy-vectorized yearly metrics, GIL bypass via Optuna JournalStorage, local BLAS pin = 1, skglm `AndersonCD(max_epochs=2000)`, seeded TPESampler.

* **CPCV parallelism**: `--loyo-jobs -1` (auto = `cpu_count // optuna-jobs`). Cap to prevent core oversubscription.

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
* `STABILITY_B`, `STABILITY_PI`, `SCREEN_FDR`, `SCREEN_FALLBACK_K`
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
3. **BH-FDR Screening (Step 1)**: Spearman rank correlation on selection train. Keep features with FDR = 0.15. Fallback to top 50 by p-value.
4. **CSS + VIF Pruning (Step 2)**: Complete Linkage hierarchical clustering (threshold $t=0.25$, $|r| \ge 0.75$). Subsampling ($B=100$) ElasticNet path votes aggregated at cluster level. Keep clusters selected in $\ge 60\%$ subsamples. Pick representative with highest individual score. Apply iterative VIF pruning (VIF threshold 10.0) on representatives.
5. **Loss Weighting (Step 3)**: Power weights $w(y_i) = |y_i|^k$. Scale inputs by $\sqrt{w}$.
6. **CPCV with Embargo (Step 4)**: 6 groups, 2 test groups (15 folds), 10-day embargo at test boundaries. Run on selection train.
7. **Pilot Normalization (Step 4.1)**: Run 50 pilot trials to compute median and MAD for validation z-scores.
8. **Objective Function**: Maximize weighted sum of normalized validation metrics + ESS soft penalty under 20%.
9. **Signed Constraints & TPESampler**: Hard constraints (Overall IC > 0, Hit Rate $\ge 60\%$, Monotonicity > 0.25, Spread > 0, Active features $\le ESS / 8$, Gini concentration $\le 0.85$ soft limit). Violation prunes trial.
10. **One-Shot Evaluation & Plots (Step 6)**: Refit on working set using best parameters. Save final model and scaler. Evaluate OOS lockbox via `generate_report.py` (side-aware Tail IC). Plot 15 diagnostic panels. Run block bootstrap (B=1000, block size 10) for 95% CIs.
11. **L2 Regularization**: Mandatory 10% L2 regularization (`skglm_huber_l1` uses `l1_ratio = 0.9`, `skglm_mcp` uses `mu = 0.1 * alpha`) to stabilize design matrix condition number.
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

4. **Decoupled Ridge Fallback & Dynamic VIF**:
   - Decoupled `force_ridge` from hardcoded ETF blacklist. Forced purely by condition number (`kappa > 1e5`), freeing `500ETF` to explore sparse solvers (`skglm_mcp` / `skglm_huber_l1`).
   - Dynamic VIF thresholding: `5.0` for highly ill-conditioned `50ETF`, default `10.0` for other ETFs.
   - Raised `ridge_alpha` search upper bound to `10000.0`.

5. **Monthly Blocked Validation Bootstrap Regularization**:
   - Perform $B=100$ monthly blocked bootstrap resamples on the inner validation set.
   - Subtract standard deviation of bootstrapped tail ICs from raw validation Tail IC:
     $$V_{tail\_ic\_adj} = val\_tail\_ic - 1.0 \times \sigma_{boot\_tail\_ic}$$
   - Penalizes unstable validation scores and steers Optuna to robust configurations.

5. **Model Confidence Set (MCS) & Bayesian True Discovery**:
   - Hansen's MCS (sequential t-test, alpha=10%) identifies statistically indistinguishable trials.
   - Empirical Bayes posterior probability of true discovery $P(\theta_{OOS} > 0 | data)$ logs discovery confidence.

6. **Quarterly Rolling Refit decay check**:
   - Runs `run_quarterly_rolling_refit_test` post-lockbox.
   - Compares Static vs Rolling Model performance on quarterly windows (QuantBench method).
