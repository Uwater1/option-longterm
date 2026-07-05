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

# 2. Run first-principles Stability Selection + Optuna training (takes 40s, Agent should always run full set)
python3 day-model/train_model.py -e all --trials 100 # 1Don't go beyond 100, overfit risk high
# IMPORTANT: Agent should always run full set

# 3. Generate summary REPORT.md and tables
python3 day-model/generate_report.py
```

### train_model.py Performance Options

```bash
python day-model/train_model.py -e 300 -t 200             # cache ON, n_jobs=cpu_count
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
2. **Selection Validation Split (Step 0.5)**: Six non-contiguous 3-month blocks carved out from the working set for selection-blind validation. They are partitioned into 4 **Inner Validation** blocks (for tuning) and 2 held-out **Outer Validation** blocks (for true generalization assessment), with a 10-day temporal embargo applied to training boundaries.
3. **BH-FDR Screening (Step 1)**: Robust Spearman rank correlation on selection train subset. Keep features surviving FDR = 0.15. Fallback to top 50 by p-value if fewer pass.
4. **Cluster Stability Selection (CSS) + VIF Pruning (Step 2)**: Groups screened features using Complete Linkage hierarchical clustering (correlation distance threshold of 0.25, i.e., $|r| \ge 0.75$). During stability selection ($B=100$ subsamples), voting is aggregated at the cluster level. A single representative feature with the highest individual stability score is selected from each stable cluster ($\ge 0.60$ voting frequency). Then, **iterative VIF pruning** (VIF threshold of 10.0) is applied to these representatives to eliminate multivariate collinearity.
5. **Loss Weighting (Step 3)**: Power weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to focus model on tail days.
6. **CPCV with Embargo (Step 4)**: Combinatorial Purged Cross-Validation with 6 chronological groups and 2 test groups ($\binom{6}{2} = 15$ folds), with a 10-day embargo at test boundaries. Constructed ONLY on the selection train subset.
7. **Pilot Normalization (Step 4.1)**: Runs 50 pilot trials, computes median and MAD for each of the 4 selection validation metrics (inner split only) to calculate robust z-scores.
8. **Objective Function**: Maximizes weighted sum of normalized selection validation metrics, plus a soft penalty for ESS under 20% (`ess_penalty = -10.0 * (0.20 - ess_pct)`):
   - Val Overall IC: 40%
   - Val Tail IC: 40%
   - Val Monotonicity: 15%
   - Val Top-Bottom Spread: 5%
9. **Signed Constraints & TPESampler Constrained Optimization**:
   - Hard constraints are evaluated via signed margins (negative = satisfied, positive = violated) and fed to Optuna's `constraints_func` on the `TPESampler`. This gives TPE the gradient information to steer trials into the feasible region, instead of collapsing infeasible trials to a flat `-1e9`.
   - Hard constraints include: Overall IC <= 0, Hit Rate < 60%, Decile Monotonicity <= 0.25, Top-Bottom Spread <= 0, Active features count exceeds ESS-based cap ($active\_k > ESS / 8.0$), and Active features count under floor ($active\_k < min\_active\_features$ where $min\_active\_features = min(5, max\_active\_features)$). Dynamic floor scaling prevents contradictory constraints on small-sample datasets (e.g. `588000ETF`).
   - Model weight concentration (Gini index) is converted from a hard switch to a soft, $k$-normalized penalty in the objective function to avoid collapsing the feasible region for sparse models: `gini_cap = 1.0 - 0.40 * (active_k / m_gini)` and `gini_penalty = -10.0 * (gini - gini_cap) if gini > gini_cap else 0.0`.
10. **One-Shot Evaluation & Diagnostics Plotting (Step 6)**: Handled entirely in `generate_report.py`. Evaluates final model on 500-day lockbox, updates OOS metrics in results JSON/scaler bundles, and generates 2x2 diagnostics plots. Calculates regularized condition number. Runs a 1000-sample block bootstrap (block size $B=10$) on lockbox OOS data to calculate 95% CIs and flags generalization gaps that are swallowed by the CI as Noise.
11. **L2 Regularization Component**: Enforces 10% L2 Ridge regularization in both model families to stabilize joint-coefficient assignments under severe multicollinearity.
12. **Multiple comparison deflation & Overfitting Diagnostics**: Computes running **Deflated Objective** and Deflated Val Overall IC to correct for multiple trials / search-budget inflation across completed trials. Selects best trial based on running deflated objective. Also computes **Probability of Backtest Overfitting (PBO)** and **Performance Degradation** using CSCV on the CPCV folds.
13. **Model Quality & Generalization Diagnostics**: Calculates condition numbers, ESS of tail-focus weights, Gini coefficient, and CV-to-OOS Generalization Gap for rank IC & decile monotonicity. Saves findings to `REPORT.md`.
14. **Plateau Stable Parameter Selection**: Instead of choosing hyperparameters based on a single point-optimal raw objective value, the model evaluates valid trials in a normalized hyperparameter space and selects the trial residing in the most stable "parameter plateau" (neighborhood radius $r=0.25$) using the running **deflated objective**, penalizing parameter cliffs.

## OOS Lockbox Performance & Leakage Verification (July 2026)

We conducted a rigorous verification of the out-of-sample (OOS) lockbox performance for `500ETF` and `159915ETF` to rule out leakage and investigate the underlying mechanism.

### 1. Embargo Asymmetry Check at Lockbox Boundary
To verify if the lack of a temporal embargo at the transition into the lockbox (`2024-03-01`) artificially inflated the lockbox scores (since features at the beginning of the lockbox look back into training data), we re-fit the models with a 10-day and 20-day temporal embargo before `LOCKBOX_DATE` (completely excluding those days from the final model refit):
- **500ETF**:
  - Baseline (No Embargo) Lockbox IC: `+0.1257`
  - 10-day Embargo Lockbox IC: `+0.1255`
  - 20-day Embargo Lockbox IC: `+0.1250`
- **159915ETF**:
  - Baseline (No Embargo) Lockbox IC: `+0.1300`
  - 10-day Embargo Lockbox IC: `+0.1303`
  - 20-day Embargo Lockbox IC: `+0.1308`

*Conclusion*: The impact of the boundary embargo is negligible (<0.0004 for 10d), confirming that there is no boundary leak inflating lockbox performance.

### 2. Validation Block & COVID (2020-Q2) Regime Analysis
We evaluated individual validation block performances using the best parameters to see if validation averages were dragged down by a specific regime:
- **500ETF**:
  - Block 1 (2016-10 to 2017-01): `IC = -0.1076`
  - Block 2 (2018-07 to 2018-10): `IC = +0.2738`
  - Block 3 (2020-04 to 2020-07) (COVID): `IC = +0.3733`
  - Block 4 (2022-10 to 2023-01): `IC = +0.1463`
  - Block 5 (2021-07 to 2021-10): `IC = +0.3344`
  - Block 6 (2023-07 to 2023-10): `IC = +0.1420`
  - *Average*: `+0.1937`
- **159915ETF**:
  - Block 1 (2016-10 to 2017-01): `IC = +0.0657`
  - Block 2 (2018-07 to 2018-10): `IC = +0.1856`
  - Block 3 (2020-04 to 2020-07) (COVID): `IC = +0.2605`
  - Block 4 (2022-10 to 2023-01): `IC = +0.2001`
  - Block 5 (2021-07 to 2021-10): `IC = +0.1899`
  - Block 6 (2023-07 to 2023-10): `IC = +0.0894`
  - *Average*: `+0.1652`

*Conclusion*:
- The COVID block (Block 3) was actually the highest-performing validation block for both ETFs, so it does not drag down validation.
- Some individual blocks (like Block 1 for 500ETF at `-0.1076`) drag validation down, indicating validation averages are somewhat conservative.
- The raw (undeflated) pooled outer validation ICs (`+0.1682` for 500ETF, `+0.1341` for 159915ETF) are very close to the raw lockbox ICs (`+0.1257` and `+0.1300`), which shows normal, healthy generalization.
- The apparent "OOS beats validation" gap is a statistical artifact of multiple-testing adjustment: the validation IC is heavily deflated using Marcos Lopez de Prado deflation (to correct for the 100 trials search space), whereas the lockbox is evaluated once and is undeflated.

### 3. Hand Trader Consensus
Hand traders report that trading signals during the 2024–2026 lockbox period were structurally "stronger" and more pronounced. This matches our empirical lockbox results, confirming that the strong lockbox performance is a real regime-driven effect, not a leak.

## Feature Deprecation & Compatibility (July 2026)

- Deprecated 49 early extra and 2 yesterday extra features that were never active or stable across all 5 ETFs.
- Defined in `day-model/deprecate_features.py`.
- Backward compatibility: Use `--include-deprecated` flag with `build_features.py` or set `INCLUDE_DEPRECATED=1` environment variable to include them.



