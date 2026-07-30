# Day-Model Rewrite v3 — Commands & Architecture

Simplified feature selection & IC-weighted return combination pipeline. Check [plan.md](day-model-new/plan.md) for detailed logic.

## Commands

```bash
# 0a. Single Base Primitive Digging & Screening (1b Document Protocol)
# Tests causality, computes 7Y-Jackknife stability + IC CV across all 5 ETFs, logs to mining/mined_candidates.csv
python3 day-model-new/test_feature_causality.py
python3 day-model-new/mining/dig_and_test_candidates.py
python3 day-model-new/mining/dig_multiday_candidates.py     # Multi-day (2-5d) trend/regime primitives
python3 day-model-new/mining/dig_trend_regime_candidates.py # Wave 4: big-trend/regime (Kaufman/Choppiness/MA-stack/Keltner/Brooks)
python3 day-model-new/mining/dig_wave5_candidates.py        # Wave 5: smart-money/path/liquidity/cross-asset/calendar/VIX

# 0b. Generate aggressive feature combination recipes (2-way + 3-way by default)
# Defaults: top-50 for 2-way, top-25 for 3-way, 11 + 5 ops, dedup via mining_log.json
python3 day-model-new/mining/generate_combos.py -e all -s all [--two-only]

# Custom top-K for broader search
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single [-k 60 (optional)] [--top-k-3 30 (optional)]

# Regenerate everything (ignore mining log dedup)
python3 day-model-new/mining/generate_combos.py -e all -s single --no-dedup

# 1. Run Stage A feature selection (saves selected_pool & mining_attempts JSONs to data/)
# Note: select_features.py processes ONE ETF/side combination. For all combinations, use run_baseline.py.
# Automatically loads and evaluates candidate recipes from mining/candidates_*.json if present
python3 day-model-new/select_features.py -e 300ETF -s single
python3 day-model-new/select_features.py -e 588000ETF -s long

# 2. Run Stage B evaluation (saves results JSONs to data/)
# Note: evaluate_concept.py processes ONE ETF/side combination. For all combinations, use run_baseline.py.
# Resolves recipes dynamically using training set statistics (means, stds, medians)
python3 day-model-new/evaluate_concept.py -e 300ETF -s single
python3 day-model-new/evaluate_concept.py -e 588000ETF -s long

# 3. Run baseline loop across ETFs and sides (runs select_features + evaluate_concept, saves BASELINE_REPORT.md)
# Default = sequential (each combo uses ALL cores internally via numba/joblib, no oversubscription).
# Pass --skip-existing to skip combos with valid (non-empty) results JSON.
# Use --max-parallel N to run N combos concurrently (inner n_jobs auto-capped to cpu_count // N).
python3 day-model-new/run_baseline.py
python3 day-model-new/run_baseline.py --skip-existing
python3 day-model-new/run_baseline.py --max-parallel 6 -e 300ETF

# 3b. Recompile BASELINE_REPORT.md from existing JSON outputs (no pipeline run, <1s)
# Supports -e/-s filters and custom -o output path
python3 day-model-new/compile_report.py
python3 day-model-new/compile_report.py -e 588000ETF -s long -o custom_report.md

# 4. Run filter effectiveness diagnostics (standalone & LOO feature analysis + gate evaluation)
python3 day-model-new/analyze_admitted_features.py

# 5. Run deep filter diagnosis (FP/FN causal analysis, training-only discriminators)
# Excludes 588000ETF (insufficient history). Uses lockbox as ground truth for labeling only.
python3 day-model-new/filter_diagnosis.py

# 6. Multi-period FP rate analysis (3 alternate training windows, OOS as ground truth)
# Periods: P2=2015-2023, P3=2016-2024, P4=2017-2025. Excludes 588000ETF.
# Jackknife uses n_chunks = training_years (1 chunk per calendar year).
python3 day-model-new/run_periods.py                    # All 3 periods, all ETFs/sides
python3 day-model-new/run_periods.py -e 300ETF          # Single ETF
python3 day-model-new/run_periods.py --periods p2,p3    # Subset of periods
python3 day-model-new/run_periods.py --compile-only     # Recompile MULTI_PERIOD_FP_REPORT.md
python3 day-model-new/run_periods.py --max-parallel 4   # Parallel combos
```

## Architecture

- **Adaptive Dates**:
  - `588000ETF`: Train Nov 2020 ~ Jan 2025. OOS post-Jan 2025.
  - Other ETFs: Train 2015 ~ 2022. OOS post-2022.
- **Admitted Pools Registry**:
  - `admitted_pools.py` acts as the central, version-controlled Python registry of approved feature pools (and recipes) across all ETFs and sides, protecting them from volatile `data/` overwrites and providing a quick import for downstream strategies.
- **Aggressive Feature Mining** (`mining/`):
  - `generate_combos.py` exhaustively combines top-performing indicators (default: top-50 for 2-way, top-25 for 3-way) within correlation sweet-spots.
  - **Component Stability Gate** (training-only, ETF-agnostic): Before candidate generation, computes yearly IC decomposition for each base feature. Features with `IC_CV > 3.0` OR `n_negative_years > 2` are flagged unstable and excluded from all combos. Prevents regime-dependent components (e.g. `gap_pct`) from contaminating candidates.
  - **2-way ops (11)**: `min`, `max`, `diff`, `ratio`, `ifelse`, `mean`, `product`, `abs_diff`, `rank_min`, `rank_max`, `clamp_diff`. Correlation bounds: [0.15, 0.85].
  - **3-way ops (5)**: `tri_mean`, `tri_min`, `tri_max`, `tri_median`, `tri_ifelse`. Correlation bounds: [0.10, 0.90] (relaxed for broader exploration).
  - `recipe_utils.py` handles on-the-fly execution of combinations. Aligns scale via standardization, isolates parameters to training sets to prevent lookahead leakage.
  - **Mining Log** (`mining_log.json`): Persistent dedup guarantee — tracks all generated candidate names per ETF/side. Re-runs emit only the delta (new ops/combos), never duplicates. Batch summaries appended by `select_features.py`.
  - **Document-Mining Scripts** (1b protocol):
    - `dig_and_test_candidates.py` — 40 early-bar (5m) Al Brooks / microstructure primitives.
    - `dig_multiday_candidates.py` — 38 multi-day (2-5d) trend/regime primitives.
    - `dig_trend_regime_candidates.py` — 38 Wave-4 big-trend/regime primitives (Kaufman ER, Choppiness, MA stack alignment, Keltner position, SuperTrend proxy, Brooks trend-day count, MACD cross age, trend persistence composite). All use 4-gate screen (IC_CV≤3.0, n_neg_years≤2, 7Y-Jackknife, |IC|≥0.02). 11 gate-passing features integrated into `DAY_EXTRA` in `day-model/features_extra.py` (see `Wave 4` block).
    - `dig_wave5_candidates.py` — 41 Wave-5 multi-family primitives: smart-money (OBV, A/D, NVI, PVI, Force Index, MFI, PVT), path/distribution (skewness, kurtosis, Ulcer, Pain, drawdown, MFE/MAE), cross-asset regime (5-ETF breadth, rotation, dispersion, correlation), calendar (options expiry, month boundaries, pre-holiday), liquidity (Amihud, Roll spread, turnover), higher-timeframe (weekly/monthly/quarterly), and IV/VIX (rq_vix). 7 single-ETF winners integrated into `DAY_EXTRA` (cross-asset `relative_strength_vs_cross_5d` not yet integrated — needs separate plumbing in `build_features.py`).
    - **Lookahead lesson (Jul 2026)**: `climax_volume_reversal_3d` initially passed 4 ETFs at IC 0.07-0.09 but used `cl.shift(-1)` for next-day follow-through. Causal rewrite confirmed IC ~0. Family forbidden in `mining_memory_300ETF_single.json`. Do NOT re-mine climax-with-future-confirmation.

### Feature Selection Pipeline (8 Gates, All Training-Only)

| # | Gate | Key Parameters | Purpose |
|---|------|---------------|---------|
| 1 | Yearly Jackknife Sign Stability | n_chunks=training_years (~1yr/chunk), max_flips=1, last 2 chunks must not flip; sign locked from early chunks only (excl. last 2) | Reject sign-flipping features |
| 2 | B2 Rolling Guard | mono_thr=0.60 (single) / 0.55 (L/S), ir_thr=0.30 / 0.15 | Reject unstable rolling IC |
| 3 | Temporal Validation | recent IC > 0; recency_ratio < 2.5 only when early_ic < 0.05 | Reject decayed / late-concentrated signals |
| 4 | BH-FDR | q=0.30, 5000 block-shuffled sims | Multiple-testing correction |
| 5 | B3 Composite Floor | 93rd (cond) / 95th (symmetric) / 97th (3-way) | Beat empirical null |
| 6 | Temporal Stability Gate | ic_cv × weak_link_cv ≥ 0.15 (combo features) | Kill artificially smooth mirages |
| 7 | Quality Gate | deflated_ic≥0.03/0.05, raw_ic≥0.02/0.03, sortino>0 | Kill tail-only mirages |
| 8 | B4 Correlation Gate | θ=0.95 (near-duplicate only) | Reject exact duplicates |

- **B3 Composite Score**: $0.3 \times \text{RollingMono} + 0.5 \times \text{Sortino} + 0.15 \times |\text{Tail IC}| + 0.05 \times |\text{Overall IC}|$. Deflation haircut: `cand_ic - ic_null_mean` using standalone raw IC null mean. Uses 93rd-pct for conditional 2-way, 95th-pct for symmetric 2-way (`max`, `min`, `mean`, `rank_max`, `rank_min`), and 97th-pct for 3-way (`combo_tri_*`). Sortino weight calibrated at 0.50 with null formula aligned to `simulate_returns` (both use `n` denominator for downside deviation).
- **B4 Correlation Gate (Step 8)**: Relaxed to θ=0.95 — only rejects near-perfect duplicates. Pool size is unconstrained. **Feature diversity is enforced downstream** by ONC clustering (`feature_clusters.py`) + newtrade group-constrained top-K selection (max 1 feature per cluster per day).
- **ONC Feature Clustering** (`feature_clusters.py`): Implements de Prado's Optimal Number of Clusters algorithm. Computes Spearman rank correlation on training features, converts to angular distance, sweeps K-Means K with silhouette selection, and recursively re-splits weak clusters. Outputs `data/cluster_assignments_{etf}_{side}.json`. Run after `select_features.py` to generate clusters for newtrade.
- **Temporal Stability & Quality Gates (Steps 6 & 7)**: Training-only gates applied BEFORE correlation gate. `ic_cv * weak_link_cv >= 0.15` filters out features with artificially uniform IC (structural mirages). Quality gate enforces minimum deflated IC, raw IC, and positive Sortino. Running before B4 prevents low-quality/unstable features from blocking high-quality ones in correlation comparison. **No OOS/lockbox data is used — zero look-ahead bias.**
- **Temporal Validation Gate (Step 3)**: Adaptive design — `recent_ic > 0` catches decayed signals (strong FP precision); `recency_ratio < 2.5` cap applies ONLY when `|early_ic| < 0.05` ("appeared from nowhere" pattern). Features with solid early IC that strengthen recently pass freely. Diagnosed via `filter_diagnosis.py` §6b/6c (per-gate confusion matrix + sub-condition breakdown). _Known limitation: the single-chunk `recent_ic` is noisy for short training windows; a multi-chunk rolling recent-IC average could improve stability._
- **ECDF Engine Alignment & Recipe Cache**: All pipeline scripts (`select_features.py`, `evaluate_concept.py`, `filter_diagnosis.py`, `analyze_admitted_features.py`) strictly use Numba 128-knot ECDF grid (`recipe_utils.build_ecdf_grid_float32`) for `rank_min`/`rank_max` operations and pass `train_ecdfs` across splits to eliminate out-of-sample knot leakage. If recipe formulas are modified, stale `recipe_cache_*.parquet` files must be invalidated.
- **Sign Consistency Gate (B2/B6)**: Rejects candidate features where meaningful full-sample linear IC ($|\text{IC}_{\text{full}}| \ge 0.015$) directly contradicts locked tail IC sign ($\text{IC}_{\text{full}} \cdot \text{IC}_{\text{tail}} < 0$), eliminating non-monotonic tail mirages at step B2 before correlation processing.
- **Cumulative Ledger**: Saves unique tried feature names to `data/trial_ledger_{ETF}_{side}{suffix}.json` to track overall unique trials $N$ across sequential mining rounds (prevents under-deflation). Seeds from existing attempts JSON logs.
- **VIF Safety Net & Leakage Prevention**: Dropped collinear features if VIF > 5.0 in `evaluate_concept.py`. Stats prebuilding includes `feature_c` and `feature_cond2` for 3-way recipes (`tri_*`), preventing OOS lookahead leakage.
- **Sample-Size Scaled Mining**: `generate_combos.py` scales `top_k` / `top_k_3` proportionally to training sample size relative to ~3400 trading day baseline.
- **Z-Score Blending**: IC-weighted combination on standardized features (`weights = max(0.0, deflated_ic)**k`).
- **Conviction-Weighted Position Sizing** (default mode in `evaluate_concept.py`): Combines conviction gating + smooth tanh sizing. Only trades when prediction z-score > `conviction_z` (default 0.5). Position size = `tanh((z - conviction_z) / 1.5)`, giving smooth ramp from 0 at threshold to ~1.0 for strong signals. Reduces turnover by skipping low-conviction days where expected trade return < friction. Configurable via `--position-mode conviction_weighted --conviction-z 0.5`.
- **Intraday Transaction Cost**: Under strict intraday trading (10:00-14:35 daily position opening/closing), `simulate_returns` computes flat 8 bps friction per unit active position (`np.abs(pos) * 0.0008`), aligning with null kernel's flat friction logic.
- **Raw vs Cost Sharpe Reporting**: `simulate_returns` computes both raw Sharpe (pre-cost) and cost-adjusted Sharpe. `compile_report.py` displays both side-by-side to distinguish raw signal quality from transaction cost drag.
- **Deprecated Features**: All `northbound_*` daily indicators deprecated due to HKEX Aug 2024 discontinuation of daily Northbound turnover disclosure. Listed in `day-model/deprecate_features.py`.
- **Parallel baseline runner**: Optimized using `joblib.Parallel` and `sys.executable` for safe execution.
- **Filter Effectiveness Diagnostics** (`analyze_admitted_features.py`): Evaluates each gate's false positive/negative rate against lockbox performance (read-only, never fed back into selection). Outputs: per-gate FN rate, threshold sensitivity sweep (mono_thr × ir_thr grid), IC decay curves (rolling 126-day IC across train→OOS→lockbox), and data-driven filter tuning recommendations. Results saved to `data/filter_effectiveness.json` and appended to `FEATURE_DIAGNOSTICS.md`.
- **Deep Filter Diagnosis** (`filter_diagnosis.py`): Causal analysis of false acceptance/rejection. Computes temporal IC decomposition, component stability, regime concentration, and training-only discriminators (Cohen's d) to identify WHY filters fail. Includes per-gate confusion matrix (§6b: precision/collateral from stratified full-population sampling) and temporal gate sub-condition analysis (§6c: `recent_ic≤0` vs `ratio≥2.5` breakdown). Excludes 588000ETF (insufficient history). Outputs `FILTER_DIAGNOSIS.md` and `data/filter_diagnosis.json`. Lockbox used for labeling only — never fed back into selection logic.
- **Multi-Period FP Analysis** (`run_periods.py`): Runs the full pipeline across 3 alternate training windows (P2: 2015-2023, P3: 2016-2024, P4: 2017-2025) to assess temporal robustness of filter gates. Uses OOS as ground truth (no lockbox — insufficient future data for later periods). Outputs: per-period `FEATURE_DIAGNOSTICS{suffix}.md`, `data/filter_effectiveness{suffix}.json`, and consolidated `MULTI_PERIOD_FP_REPORT.md`. Does NOT modify `admitted_pools.py` — purely diagnostic. Supports `--train-start`/`--train-end`/`--period-suffix` CLI overrides on `select_features.py`, `evaluate_concept.py`, and `analyze_admitted_features.py`.

