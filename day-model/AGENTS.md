# Day-Model Feature Expansion & Return Prediction Workflow

Workflow for day-model feature generation and multi-metric linear return predictor optimization.
Check day-model/day-model_plan.md for logic. Also update day-model/day-model_plan.md when the logic changes.

## Target Definition

* **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
* **Entry**: 10:00 (bar 5 closes at 10:00, entry at open of bar 6)
* **Exit**: 14:35 (close of bar 42)
* **Underlying**: Log return from 10:00 to 14:35 across all 5 ETFs.

## Workflow

```bash
# 1. Re-generate parquet feature datasets
python3 day-model/build_features.py -e all

# 2. Run first-principles Stability Selection + Optuna training
python3 day-model/train_model.py -e all --trials 100

# 3. Generate summary REPORT.md and tables
python3 day-model/generate_report.py
```

### train_model.py Performance Options

```bash
python day-model/train_model.py -e 300 -t 100             # cache ON, n_jobs=cpu_count
python day-model/train_model.py -e 300 --no-cache          # force recompute
python day-model/train_model.py -e 300 --optuna-jobs 8     # cap Optuna workers
python day-model/train_model.py -e 300 --optuna-jobs 1     # sequential (guarantees 100% determinism)
python day-model/train_model.py -e 300 --bootstrap-jobs 8  # cap stability-bootstrap workers
python day-model/train_model.py -e 300 --loyo-jobs 4       # cap LOYO fold workers per trial
```

Speedups: fp32 arrays; vectorized Spearman screen; joblib-parallel stability bootstrap & CPCV folds; disk caches (select/loyo/pilot); precomputed unweighted scaled matrix; numpy-vectorized yearly metrics (no pandas qcut); Optuna process-parallel optimization via joblib (loky backend) and JournalFileBackend storage to bypass Python GIL; BLAS threads pinned to 1; skglm `AndersonCD(max_epochs=2000)`; seeded TPESampler (42 pilot, 43 main).

- **CPCV parallelism**: `--loyo-jobs -1` (auto = `cpu_count // optuna-jobs`). Use when running single ETF with low `--optuna-jobs`; auto-throttles to avoid oversubscription when Optuna already saturates cores.

## Cache invalidation

`train_model.py` writes three disk caches per ETF in `day-model/data/`:

| File | Contents |
|---|---|
| `cache_select_{etf}_{hash}.joblib` | `screen_mask`, `p_vals`, `rhos`, `stability_selected_idx`, `stability_scores` (version `v6` cache key, isolated to selection train set) |
| `cache_loyo_{etf}_{hash}.joblib` | List of pre-scaled CPCV folds `(test_idx, X_tr_scaled, X_te_scaled, y_tr)` (version `v6` cache key) |
| `cache_pilot_{etf}_{hash}.joblib` | Pilot records `[{params, raw_metrics, val_metrics}, ...]` (version `v6` cache key) |

**Auto-invalidated** (key mismatch triggers recompute) when any of these change:
- ETF name
- `len(FEATURES)` (FEATURES list length)
- `features_{etf}.parquet` mtime (parquet regen via `build_features.py`)
- Selection Train row/col count
- `STABILITY_B`, `STABILITY_PI`, `SCREEN_FDR`, `SCREEN_FALLBACK_K`
- `SELECTION_VAL_DATE` constant
- `TARGET` column name
- Selected-feature index tuple (CPCV + pilot caches)
- `PILOT_N_TRIALS`, `PILOT_SEED` (pilot cache only)

**Manual clear required when**:
- Editing `FEATURES`/`EARLY_FEATURES`/`DAY_FEATURES`/`YESTERDAY_FEATURES` lists in `build_features.py` **without** regenerating parquet.
- Changing `METRIC_WEIGHTS` (affects pilot medians/MADs; clear `cache_pilot_*`).
- Changing the CPCV group/test window logic, embargo window, or scaling code in `_compute_loyo`.
- Changing `run_screening` / `run_stability_selection` internals.
- Changing hierarchical clustering thresholds or distance metrics for CSS.

**Purge all caches**:
```powershell
Remove-Item day-model\data\cache_*.joblib
```


## Remade Predictor Architecture (First Principles)

`train_model.py` implements the following robust modeling chain:

1. **Lockbox Split (Step 0)**: Hold out days from 2024-03-01 to last day (OOS lockbox data completely ignored during training).
2. **Selection Validation Split (Step 0.5)**: Dates from 2021-01-01 to 2021-12-31 carved out from working set for selection-blind validation.
3. **BH-FDR Screening (Step 1)**: Robust Spearman rank correlation on selection train subset. Keep features surviving FDR = 0.40. Fallback to top 50 by p-value if fewer pass.
4. **Cluster Stability Selection (CSS) + VIF Pruning (Step 2)**: Groups screened features using Complete Linkage hierarchical clustering (correlation distance threshold of 0.25, i.e., $|r| \ge 0.75$). During stability selection ($B=100$ subsamples), voting is aggregated at the cluster level. A single representative feature with the highest individual stability score is selected from each stable cluster ($\ge 0.60$ voting frequency). Then, **iterative VIF pruning** (VIF threshold of 10.0) is applied to these representatives to eliminate multivariate collinearity.
5. **Loss Weighting (Step 3)**: Power weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to focus model on tail days.
6. **CPCV with Embargo (Step 4)**: Combinatorial Purged Cross-Validation with 6 chronological groups and 2 test groups ($\binom{6}{2} = 15$ folds), with a 10-day embargo at test boundaries. Constructed ONLY on the selection train subset.
7. **Pilot Normalization (Step 4.1)**: Runs 50 pilot trials, computes median and MAD for each of the 4 selection validation metrics to calculate robust z-scores.
8. **Objective Function**: Maximizes weighted sum of normalized selection validation metrics, plus a soft penalty for ESS under 20% (`ess_penalty = -10.0 * (0.20 - ess_pct)`):
   - Val Overall IC: 40%
   - Val Tail IC: 40%
   - Val Monotonicity: 15%
   - Val Top-Bottom Spread: 5%
9. **Kill Switches / Hard Constraints**: Trial pruned (returns `-1e9`) if CV metrics violate constraints:
   - Overall IC <= 0
   - Hit Rate < 60%
   - Decile Monotonicity <= 0.25
   - Top-Bottom Spread <= 0
   - Active features count exceeds ESS-based cap ($active\_k > ESS / 25.0$)
10. **One-Shot Evaluation & Diagnostics Plotting (Step 6)**: Handled entirely in `generate_report.py`. Evaluates final model on 500-day lockbox, updates OOS metrics in results JSON/scaler bundles, and generates 2x2 diagnostics plots. Calculates regularized condition number.
11. **L2 Regularization Component**: Enforces 10% L2 Ridge regularization in both model families to stabilize joint-coefficient assignments under severe multicollinearity.
12. **Multiple comparison deflation**: Computes **Deflated CV Overall IC** to correct for multiple trials / search-budget inflation.
13. **Model Quality & Generalization Diagnostics**: Calculates condition numbers, ESS of tail-focus weights, Gini coefficient, and CV-to-OOS Generalization Gap for rank IC & decile monotonicity. Saves findings to `REPORT.md`.

