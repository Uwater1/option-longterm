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
| `cache_select_{etf}_{hash}.joblib` | `screen_mask`, `p_vals`, `rhos`, `stability_selected_idx`, `stability_scores` |
| `cache_loyo_{etf}_{hash}.joblib` | List of pre-scaled LOYO folds `(test_idx, X_tr_scaled, X_te_scaled, y_tr)` |
| `cache_pilot_{etf}_{hash}.joblib` | Pilot records `[{params, raw_metrics}, ...]` |

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

**Purge all caches**:
```powershell
Remove-Item day-model\data\cache_*.joblib
```


## Remade Predictor Architecture (First Principles)

`train_model.py` implements the following robust modeling chain:

1. **Lockbox Split (Step 0)**: Hold out days from 2024-03-01 to last day (OOS lockbox data completely ignored during training to ensure isolation).
2. **BH-FDR Screening (Step 1)**: Robust Spearman rank correlation on 2200 training days. Keep features surviving FDR = 0.40. Fallback to top 40 by p-value if fewer pass.
3. **Stability Selection (Step 2)**: ElasticNet path selection (l1_ratio = 0.5) across $B=100$ subsamples of size $\lfloor N/2 \rfloor$ of Step 1 survivors. Restricts alpha path to alphas yielding at most 35 features on average (`STABILITY_Q = 35`). Keep features with selection probability $\ge 0.60$ (fallback to top 5 if count < 3). Handles collinearity grouping naturally via ElasticNet grouping effect.
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
9. **One-Shot Evaluation & Diagnostics Plotting (Step 6)**: Handled entirely in `generate_report.py` to keep training fast. Evaluates final model on 500-day lockbox, updates OOS metrics in results JSON/scaler bundles on disk, and generates 2x2 diagnostics plots (`plots/diagnostics_{tag}.png`) containing Coefficients, OOS decile spread, and All data decile spread.
10. **Diagnostics & Timing Profiling**: `train_model.py` performs step-by-step diagnostics (screening correlation details, stability scores percentiles, LOYO CV fold shapes, pilot metric distributions, Optuna main pruning reason breakdowns, execution timings). Saves metadata to `results_*.json`. `generate_report.py` compiles metadata into markdown timing, fallback, and pruning tables in `REPORT.md`.

