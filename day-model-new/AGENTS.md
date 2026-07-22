# Day-Model Rewrite v3 — Commands & Architecture

Simplified feature selection & IC-weighted return combination pipeline. Check [plan.md](day-model-new/plan.md) for detailed logic.

## Commands

```bash
# 0a. Single Base Primitive Digging & Screening (1b Document Protocol)
# Tests causality, computes 7Y-Jackknife stability + IC CV across all 5 ETFs, logs to mining/mined_candidates.csv
python3 day-model-new/test_feature_causality.py
python3 day-model-new/mining/dig_and_test_candidates.py

# 0b. Generate aggressive feature combination recipes (2-way + 3-way by default)
# Defaults: top-50 for 2-way, top-25 for 3-way, 11 + 5 ops, dedup via mining_log.json
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single [--two-only]

# Custom top-K for broader search
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single [-k 60 (optional)] [--top-k-3 30 (optional)]

# Regenerate everything (ignore mining log dedup)
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single --no-dedup

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

### Feature Selection Pipeline (8 Gates, All Training-Only)

| # | Gate | Key Parameters | Purpose |
|---|------|---------------|---------|
| 1 | 7-Year Jackknife Sign Stability | max_flips=2 (1 for 588000ETF), last 2 chunks must not flip | Reject sign-flipping features |
| 2 | B2 Rolling Guard | mono_thr=0.60 (single) / 0.55 (L/S), ir_thr=0.30 / 0.15 | Reject unstable rolling IC |
| 3 | Temporal Validation | recent 30% IC > 0 | Reject decayed signals |
| 4 | BH-FDR | q=0.30, 5000 block-shuffled sims | Multiple-testing correction |
| 5 | B3 Composite Floor | 95th (cond) / 97th (symmetric) / 99th (3-way) | Beat empirical null |
| 6 | Temporal Stability Gate | ic_cv × weak_link_cv ≥ 0.15 (combo features) | Kill artificially smooth mirages |
| 7 | Quality Gate | deflated_ic≥0.03/0.05, raw_ic≥0.02/0.03, sortino>0 | Kill tail-only mirages |
| 8 | B4 Correlation Gate | θ=0.85, replacement rule (1.15× if pool < 10 else 1.30×) | Reject redundancy |

- **B3 Composite Score**: $0.4 \times \text{RollingMono} + 0.3 \times \text{Sortino} + 0.2 \times |\text{Tail IC}| + 0.1 \times |\text{Overall IC}|$. Deflation haircut: `cand_ic - ic_null_mean` using standalone raw IC null mean. Uses 95th-pct for conditional 2-way, 97th-pct for symmetric 2-way (`max`, `min`, `mean`, `rank_max`, `rank_min`), and 99th-pct for 3-way (`combo_tri_*`).
- **Temporal Stability & Quality Gates (Steps 6 & 7)**: Training-only gates applied BEFORE correlation gate. `ic_cv * weak_link_cv >= 0.15` filters out features with artificially uniform IC (structural mirages). Quality gate enforces minimum deflated IC, raw IC, and positive Sortino. Running before B4 prevents low-quality/unstable features from blocking high-quality ones in correlation comparison. **No OOS/lockbox data is used — zero look-ahead bias.**
- **Cumulative Ledger**: Saves unique tried feature names to `data/trial_ledger_{ETF}_{side}{suffix}.json` to track overall unique trials $N$ across sequential mining rounds (prevents under-deflation). Seeds from existing attempts JSON logs.
- **VIF Safety Net & Leakage Prevention**: Dropped collinear features if VIF > 5.0 in `evaluate_concept.py`. Stats prebuilding includes `feature_c` and `feature_cond2` for 3-way recipes (`tri_*`), preventing OOS lookahead leakage.
- **Sample-Size Scaled Mining**: `generate_combos.py` scales `top_k` / `top_k_3` proportionally to training sample size relative to ~3400 trading day baseline.
- **Z-Score Blending**: IC-weighted combination on standardized features (`weights = max(0.0, deflated_ic)**k`).
- **Conviction-Weighted Position Sizing** (default mode in `evaluate_concept.py`): Combines conviction gating + smooth tanh sizing. Only trades when prediction z-score > `conviction_z` (default 0.5). Position size = `tanh((z - conviction_z) / 1.5)`, giving smooth ramp from 0 at threshold to ~1.0 for strong signals. Reduces turnover by skipping low-conviction days where expected trade return < friction. Configurable via `--position-mode conviction_weighted --conviction-z 0.5`.
- **Per-Entry Transaction Cost**: `simulate_returns` computes 8 bps friction per position state transition (`np.abs(pos - pos_prev) * 0.0008`), charging per-entry/turnover event rather than flat-fee per active day.
- **Raw vs Cost Sharpe Reporting**: `simulate_returns` computes both raw Sharpe (pre-cost) and cost-adjusted Sharpe. `compile_report.py` displays both side-by-side to distinguish raw signal quality from transaction cost drag.
- **Parallel baseline runner**: Optimized using `joblib.Parallel` and `sys.executable` for safe execution.
- **Filter Effectiveness Diagnostics** (`analyze_admitted_features.py`): Evaluates each gate's false positive/negative rate against lockbox performance (read-only, never fed back into selection). Outputs: per-gate FN rate, threshold sensitivity sweep (mono_thr × ir_thr grid), IC decay curves (rolling 126-day IC across train→OOS→lockbox), and data-driven filter tuning recommendations. Results saved to `data/filter_effectiveness.json` and appended to `FEATURE_DIAGNOSTICS.md`.
- **Deep Filter Diagnosis** (`filter_diagnosis.py`): Causal analysis of false acceptance/rejection. Computes temporal IC decomposition, component stability, regime concentration, and training-only discriminators (Cohen's d) to identify WHY filters fail. Excludes 588000ETF (insufficient history). Outputs `FILTER_DIAGNOSIS.md` and `data/filter_diagnosis.json`. Lockbox used for labeling only — never fed back into selection logic.
