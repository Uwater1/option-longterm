# Day-Model Feature Expansion & Return Prediction Workflow

Workflow for day-model feature generation and multi-metric linear return predictor optimization.

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
python3 day-model/train_model.py -e all --trials 50

# 3. Generate summary REPORT.md and tables
python3 day-model/generate_report.py
```

### train_model.py Performance Options

```bash
python day-model/train_model.py -e 300 -t 50              # cache ON, n_jobs=cpu_count
python day-model/train_model.py -e 300 --no-cache          # force recompute
python day-model/train_model.py -e 300 --optuna-jobs 8     # cap Optuna workers
python day-model/train_model.py -e 300 --bootstrap-jobs 8  # cap stability-bootstrap workers
python day-model/train_model.py -e 300 --loyo-jobs 4       # cap LOYO fold workers per trial
```

Speedups: fp32 arrays; vectorized Spearman screen; joblib-parallel stability bootstrap & LOYO folds; disk caches (select/loyo/pilot); precomputed unweighted scaled matrix; numpy-vectorized yearly metrics (no pandas qcut); Optuna process-parallel optimization via joblib (loky backend) and JournalFileBackend storage to bypass Python GIL; BLAS threads pinned to 1; skglm `AndersonCD(max_epochs=2000)`; seeded TPESampler (42 pilot, 43 main).

- **LOYO parallelism**: `--loyo-jobs -1` (auto = `cpu_count // optuna-jobs`). Use when running single ETF with low `--optuna-jobs`; auto-throttles to avoid oversubscription when Optuna already saturates cores.

## Cache invalidation

`train_model.py` writes three disk caches per ETF in `day-model/data/`:

| File | Contents |
|---|---|
| `cache_select_{etf}_{hash}.joblib` | `screen_mask`, `p_vals`, `rhos`, `stability_selected_idx`, `stability_scores` (version `v3` cache key) |
| `cache_loyo_{etf}_{hash}.joblib` | List of pre-scaled LOYO folds `(test_idx, X_tr_scaled, X_te_scaled, y_tr)` (version `v3` cache key) |
| `cache_pilot_{etf}_{hash}.joblib` | Pilot records `[{params, raw_metrics}, ...]` (version `v3` cache key) |

**Auto-invalidated** (key mismatch triggers recompute) when any of these change:
- ETF name
- `len(FEATURES)` (FEATURES list length)
- `features_{etf}.parquet` mtime (parquet regen via `build_features.py`)
- Working-set row/col count
- `STABILITY_B`, `STABILITY_PI`, `SCREEN_FDR`, `SCREEN_FALLBACK_K`
- `LOCKBOX_DATE` constant
- `TARGET` column name
- Selected-feature index tuple (LOYO + pilot caches)
- `PILOT_N_TRIALS`, `PILOT_SEED` (pilot cache only)

**Manual clear required when**:
- Editing `FEATURES`/`EARLY_FEATURES`/`DAY_FEATURES`/`YESTERDAY_FEATURES` lists in `build_features.py` **without** regenerating parquet (cache only sees `len(FEATURES)`, not the names).
- Changing `METRIC_WEIGHTS` (affects main study scoring, not caches — but stale pilot medians/MADs may bias normalization; clear `cache_pilot_*`).
- Changing the LOYO embargo window, year-block logic, or scaling code in `_compute_loyo`.
- Changing `run_screening` / `run_stability_selection` internals (e.g. enet `l1_ratio`, alpha count).
- Changing hierarchical clustering thresholds or distance metrics for CSS.

**Purge all caches**:
```powershell
Remove-Item day-model\data\cache_*.joblib
```


## Remade Predictor Architecture (First Principles)

`train_model.py` implements the following robust modeling chain:

1. **Lockbox Split (Step 0)**: Hold out days from 2024-03-01 to last day (OOS lockbox data completely ignored during training to ensure isolation).
2. **BH-FDR Screening (Step 1)**: Robust Spearman rank correlation on 2200 training days. Keep features surviving FDR = 0.40. Fallback to top 40 by p-value if fewer pass.
3. **Cluster Stability Selection (CSS) (Step 2)**: Groups screened features using Complete Linkage hierarchical clustering (correlation distance threshold of 0.25, i.e., $|r| \ge 0.75$). During stability selection ($B=100$ subsamples), voting is aggregated at the cluster level. A single representative feature with the highest individual stability score is selected from each stable cluster ($\ge 0.60$ voting frequency), structurally preventing pairwise collinearity in the selected support.
4. **Loss Weighting (Step 3)**: Power weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to focus model on tail days.
5. **LOYO CV with Embargo (Step 4)**: 9 Yearly blocks (2015-2023) with a 10-day embargo at test block boundaries.
6. **Pilot Normalization (Step 4.1)**: Runs 50 pilot trials, computes median and MAD for each of the 8 metrics to calculate robust z-scores.
7. **Objective Function**: Maximizes weighted sum of normalized metrics ($w_i$):
   - $M_1$ (Tail IC IR): 25%
   - $M_2$ (Tail IC Mean): 25%
   - $M_3$ (Yearly Hit Rate): 15%
   - $M_4$ (Overall Rank IC): 15%
   - $M_5$ (Decile Monotonicity): 15%
   - $M_6$ (Top-Bottom Spread): 5%
   - $M_7$ (Feature Parsimony): 0% (sparsity controlled at Step 2)
   - $M_8$ (Coefficient Bloat): 0% (regularized by CV)
8. **Kill Switches**: Trial pruned (returns `-1e9`) if:
   - Overall IC <= 0
   - Hit Rate < 60%
   - Decile Monotonicity <= 0.25
   - Top-Bottom Spread <= 0
   - Tail Weight ESS % < 20% (prevents training size collapse on outliers)
9. **One-Shot Evaluation & Diagnostics Plotting (Step 6)**: Handled entirely in `generate_report.py` to keep training fast. Evaluates final model on 500-day lockbox, updates OOS metrics in results JSON/scaler bundles on disk, and generates 2x2 diagnostics plots (`plots/diagnostics_{tag}.png`) containing Coefficients, OOS decile spread, and All data decile spread.
10. **L2 Regularization Component**: Enforces $10\%$ L2 Ridge regularization in both model families (`skglm_huber_l1` uses `L1_plus_L2(alpha, l1_ratio=0.9)` and `skglm_mcp` uses custom `MCP_plus_L2(alpha, gamma, mu=0.1 * alpha)` from `penalties.py`) to stabilize joint-coefficient assignments under severe multicollinearity.
11. **Model Quality & Generalization Diagnostics**: `train_model.py` calculates condition number ($\kappa$) & collinearity alerts, Effective Sample Size (ESS) of tail-focus weights, and Gini coefficient index. Saves to `results_*.json`. `generate_report.py` computes CV-to-OOS Generalization Gap for rank IC & decile monotonicity, compiling findings into `REPORT.md`.

