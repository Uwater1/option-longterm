# Day-Model Rewrite v3 — Commands & Architecture

Simplified feature selection & IC-weighted return combination pipeline.

## Commands

```bash
# 0. Generate aggressive feature combination recipes (2-way + 3-way by default)
# Defaults: top-50 for 2-way, top-25 for 3-way, 11 + 5 ops, dedup via mining_log.json
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single

# 2-way only (skip 3-way combos)
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single --two-only

# Custom top-K for broader search
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single -k 60 --top-k-3 30

# Regenerate everything (ignore mining log dedup)
python3 day-model-new/mining/generate_combos.py -e 300ETF -s single --no-dedup

# 1. Run Stage A feature selection (saves selected_pool & mining_attempts JSONs to data/)
# Automatically loads and evaluates candidate recipes from mining/candidates_*.json if present
python3 day-model-new/select_features.py -e 300ETF -s single
python3 day-model-new/select_features.py -e 588000ETF -s long

# 2. Run Stage B evaluation (saves results JSONs to data/)
# Resolves recipes dynamically using training set statistics (means, stds, medians)
python3 day-model-new/evaluate_concept.py -e 300ETF -s single
python3 day-model-new/evaluate_concept.py -e 588000ETF -s long

# 3. Run full baseline loop across all 5 ETFs and 3 sides in parallel (saves BASELINE_REPORT.md)
python3 day-model-new/run_baseline.py --n-jobs 4
```

## Architecture

- **Adaptive Dates**:
  - `588000ETF`: Train Nov 2020 ~ Jan 2025. OOS post-Jan 2025.
  - Other ETFs: Train 2015 ~ 2022. OOS post-2022.
- **Admitted Pools Registry**:
  - `admitted_pools.py` acts as the central, version-controlled Python registry of approved feature pools (and recipes) across all ETFs and sides, protecting them from volatile `data/` overwrites and providing a quick import for downstream strategies.
- **Aggressive Feature Mining** (`mining/`):
  - `generate_combos.py` exhaustively combines top-performing indicators (default: top-50 for 2-way, top-25 for 3-way) within correlation sweet-spots.
  - **2-way ops (11)**: `min`, `max`, `diff`, `ratio`, `ifelse`, `mean`, `product`, `abs_diff`, `rank_min`, `rank_max`, `clamp_diff`. Correlation bounds: [0.15, 0.85].
  - **3-way ops (5)**: `tri_mean`, `tri_min`, `tri_max`, `tri_median`, `tri_ifelse`. Correlation bounds: [0.10, 0.90] (relaxed for broader exploration).
  - `recipe_utils.py` handles on-the-fly execution of combinations. Aligns scale via standardization, isolates parameters to training sets to prevent lookahead leakage.
  - **Mining Log** (`mining_log.json`): Persistent dedup guarantee — tracks all generated candidate names per ETF/side. Re-runs emit only the delta (new ops/combos), never duplicates. Batch summaries appended by `select_features.py`.
- **BH-FDR Pre-Filter**: Runs 5,000 single-trial empirical null simulations (block-shuffled target, block size 10) to compute empirical p-values. Filters at $q = 0.20$ before sorting/correlation.
- **Cumulative Ledger**: Saves unique tried feature names to `data/trial_ledger_{ETF}_{side}{suffix}.json` to track overall unique trials $N$ across sequential mining rounds (prevents under-deflation). Seeds from existing attempts JSON logs.
- **Empirical Null Simulation Gate**: Runs 1,000 multi-trial simulations with actual feature matrix columns and block-shuffled targets. Set 95th-percentile max tail IC as admission floor. Deflation haircut: `overall_ic - empirical_mean`.
- **Z-Score Blending**: IC-weighted combination on standardized features.
- **Parallel baseline runner**: Optimized using `joblib.Parallel` and `sys.executable` for safe execution.
