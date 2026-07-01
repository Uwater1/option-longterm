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
python day-model/train_model.py -e 300 -t 50            # default: cache ON, n_jobs=cpu_count
python day-model/train_model.py -e 300 --no-cache        # force recompute (ignore caches)
python day-model/train_model.py -e 300 --optuna-jobs 8   # cap Optuna workers
python day-model/train_model.py -e 300 --bootstrap-jobs 8 # cap stability-bootstrap workers
```

Speedups applied:
- **fp32 downcast** of feature/target arrays (BLAS-friendly, ~50% memory).
- **Vectorized Spearman screening** (single matmul over column ranks; replaces 238-call Python loop).
- **Parallel stability bootstrap** (B=100 fits across `--bootstrap-jobs` workers via joblib).
- **Disk caches** for selection, LOYO folds, pilot calibration (see below).
- **Precomputed unweighted scaled matrix** — per-trial cost only re-applies `sqrt(w)`.
- **Optuna `n_jobs=cpu_count`** with BLAS threads pinned to 1 per worker (env guards `OMP_NUM_THREADS` etc set at import).
- **Seeded TPESampler** (`seed=42` pilot, `seed=43` main) for reproducibility.

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

1. **Lockbox Split (Step 0)**: Hold out days from 2024-03-01 to last day.
2. **BH-FDR Screening (Step 1)**: Robust Spearman rank correlation on 2200 training days. Keep features surviving FDR = 0.40. Fallback to top 80 by p-value if fewer pass.
3. **Stability Selection (Step 2)**: ElasticNet path selection (l1_ratio = 0.5) across $B=100$ subsamples of size $\lfloor N/2 \rfloor$ of Step 1 survivors. Keep features with selection probability $\ge 0.60$ (fallback to top 5 if count < 3). Handles collinearity grouping naturally via ElasticNet grouping effect.
4. **Loss Weighting (Step 3)**: Power weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to focus model on tail days.
5. **LOYO CV with Embargo (Step 4)**: 9 Yearly blocks (2015-2023) with a 10-day embargo at test block boundaries.
6. **Pilot Normalization (Step 4.1)**: Runs 50 pilot trials, computes median and MAD for each of the 8 metrics to calculate robust z-scores.
7. **Objective Function**: Maximizes weighted sum of normalized metrics ($w_i$):
   - $M_1$ (Tail IC IR): 20%
   - $M_2$ (Tail IC Mean): 20%
   - $M_3$ (Yearly Hit Rate): 15%
   - $M_4$ (Overall Rank IC): 15%
   - $M_5$ (Decile Monotonicity): 10%
   - $M_6$ (Top-Bottom Spread): 5%
   - $M_7$ (Feature Parsimony): 10%
   - $M_8$ (Coefficient Bloat): 5%
8. **Kill Switches**: Trial pruned (returns `-1e9`) if:
   - Overall IC <= 0
   - Hit Rate < 60%
   - Decile Monotonicity <= 0.4
   - Top-Bottom Spread <= 0
9. **One-Shot Evaluation (Step 6)**: Fits final model on all 2200 training rows and evaluates on the 500-day lockbox.
