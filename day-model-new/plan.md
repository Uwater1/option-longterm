# Day-Model Rewrite v3 — Plan

## Why v1/v2 died (context, don't repeat)
- v1: way too complex. Don't try to read it 
- v2 (`day-model/day-model_plan.md`): elaborate model-side machinery (Huber+MCP manifold, CSS+VIF, HMM regimes, vol gating) worked numerically (condition numbers, ESS all fixed) but the *headline* Sharpe-objective search came back statistically indistinguishable from baseline once block-bootstrap CI was applied (§8.6 of that doc). Lesson: fancy model-side optimization can look good pre-CI and be noise post-CI.
- Core decision for v3: **move weak/joint-signal capture to the feature-mining stage. Keep model training dumb and hard to overfit.** Mining can be messy, agentic, human-in-the-loop. Model stage cannot.

---

## Stage A — Feature Mining (`mining/generate_combos.py`)

Goal: Produce aggressive candidate recipes and combinations to find weak/joint signals, avoiding redundant evaluations.

### A1. Sources
1. Existing survivor list (already pruned 317→210, keep as base).
2. Mine repo of 1000+ trading ideas / AL Brooks book → candidate formulas.
3. Combine existing features: `min(A,B)`, `max(A,B)`, `IfElse(regime_cond, A, B)`, ratio/diff combos etc. (2-way and 3-way ops).

### A2. Deduplication & Verification
- **Mining Log (`mining_log.json`)**: Persistent ledger tracking all generated candidates per ETF/side. Only delta is sent to evaluation.
- Scales combinations dynamically on training sets to prevent lookahead leakage.

---

## Stage B — Feature Filtering / Admission Gate (`select_features.py`)

Goal: Apply strict statistical guards, correlation filters, and trial-count tracking to build a robust pool.

### B1. Pre-filters (Cheap gates & order of operations)
1. **Split-half sign stability**: Reject candidate if training IC sign disagrees between first/second halves of train set.
   - **Sign locking**: Split-half check outputs a locked `sign` (+1 or -1) value. This sign is the pipeline's single source of truth, locked here and carried forward to B2 and B3.
2. **Rolling Guard (Pre-filter check)**: 90-calendar-date rolling tail IC evaluated instantly on pre-computed values. Drop if monotonicity < `mono_thr` or `IC_IR` < `ir_thr`:
   - `long`/`short`: `mono_thr = 0.55`, `ir_thr = 0.15`
   - `single`: `mono_thr = 0.70`, `ir_thr = 0.30`
   - **Pass-forward cached values**: Rolling mono average from this step is cached and passed forward to B3, not just its pass/fail verdict (uses locked `sign` from B1).
   - **Cheap-first ordering**: Executed before BH-FDR simulation to thin pool by ~98% instantly.
3. **BH-FDR pre-filter**: Reject if empirical $p$-value fails Benjamini-Hochberg FDR at $q=0.30$ (via 5,000-trial single-feature block-shuffled simulation on compact survivor matrix `X_survivors`, cached per ETF/side).

### B3. Admission Floor (Composite score gate)
- **Rank-normalized Composite Score**:
  $$\text{score} = 0.4 \times \text{RollingMono}_{90\text{d}} + 0.3 \times \text{Sortino} + 0.2 \times |\text{Tail IC}| + 0.1 \times |\text{Overall IC}|$$
  - `RollingMono` (cached from B2) and `Sortino` consume locked `sign` from B1 (computed post sign-resolution, no $|\text{abs}|$ needed).
  - `Tail IC` and `Overall IC` use absolute values $|\text{IC}|$.
- **Per-candidate trade simulation**: Runs `simulate_returns()` (ported to shared module `recipe_utils.py`) per candidate using B1 locked sign to compute candidate Sortino.
- **Null-permutation-wrapped threshold**: Block-permute target $y$ (1000 trials), recompute entire composite score per permutation, and take 95th percentile as `empirical_95th` admission floor.
- Candidate must satisfy: $\text{composite\_score}(\text{candidate}) \ge \text{empirical\_95th}$.
- *Compute note*: Heavier compute per survivor, but B1 + B2 thin pool first (cheap-first order preserved).

### B4. Correlation Gate & Replacement Rule
- Admit if `max_corr(candidate, current_pool) < theta` (theta = 0.50).
- **Replacement rule**:
  ```
  if IC(new) >= 0.10 and IC(new) >= 1.3 * IC(old)
     and exactly one existing pool member g has corr(new, g) > theta:
       replace g with new
  ```

### B5. Trial Ledger & Deflated IC
- Save unique attempted candidate formulas to `trial_ledger_{ETF}_{side}.json` to track cumulative unique trials $N$.
- Compute deflated IC: `deflated_ic = max(0.0, overall_ic - empirical_mean)` where `empirical_mean` is simulation average max IC.

### B6. Outputs
- Version-controlled admitted pools registry in [admitted_pools.py](file:///home/hallo/Documents/option-longterm/day-model-new/admitted_pools.py).
- Detailed log of attempts in `data/mining_attempts_{ETF}_{side}.json`.

---

## Stage C — Model Training & Evaluation (`evaluate_concept.py`)

Goal: Combine surviving features and evaluate performance under strict cross-validation.

### C1. Baseline Model: IC-weighted Linear Sum
```
signal = sum_i( sign(IC_i) * |IC_i|^k * z(feature_i) )
```
- `k` optional mild tilt toward higher-IC features (k=1 default).
- Avoids orthogonalization (retains noise-canceling properties).

### C2. Light VIF Sanity Check
- One VIF pass on the final pool, drop only if VIF > 12.

### C3. Guardrails & Validation
- **Chronological split**: Train / inner validation / outer validation / OOS lockbox.
- **Block-bootstrap CI**: Report OOS metrics via CI (block size 10) instead of point estimates.
- **Kill switches**: Overall IC > 0, Hit Rate ≥ 60%, Monotonicity ≥ 0.25, Spread > 0.

### C4. Escalation Rule
- Only use more complex models (e.g. ElasticNet, LightGBM) if they statistically outperform the baseline weighted sum within the block-bootstrap CI.

---

## Checklist
- [ ] Replace B3 IC-threshold with rank-normalized composite (Mono 0.4 / Sortino 0.3 / TailIC 0.2 / OverallIC 0.1), sign locked from B1, null-permutation-wrapped.
- [ ] Port `simulate_returns()` to shared module (`recipe_utils.py`) and run per-candidate Sortino in B3 using B1 locked sign.
- [ ] Reconcile `feature-mining.md` step numbering with new A/B/C stage names — still on old "Step 1/Step 2" scheme, will confuse anyone cross-referencing.
- [ ] Build admission-gate mining harness (`select_features.py`) — IC threshold + max-corr + replacement rule.
- [ ] Add trial-count logging + deflated-IC calc (`select_features.py`) before anything leaves Stage B.
- [ ] Port v2's chronological split + block-bootstrap CI report code (`evaluate_concept.py`) for Stage C eval.
- [ ] Run Stage B filtering on existing 210-feature pool first (no new mining yet) → get baseline pool in `admitted_pools.py`.
- [ ] Run Stage C weighted-sum evaluation on baseline pool → get baseline OOS benchmark.
- [ ] Generate recipe combos (`mining/generate_combos.py`) and write `feature-mining.md`.
- [ ] Re-run Stage B admission + Stage C evaluation on old+mined pool, compare vs baseline via CI.
- [ ] Only then consider C4 escalation.

## References
- Wang et al. 2026, *FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery*, arXiv:2602.14670 — admission gate, replacement rule, IC-weighted vs orthogonal vs learned-selection comparison.
- Bailey & López de Prado 2014, *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*, Journal of Portfolio Management 40(5) — deflate IC/Sharpe by trial count.
- `day-model_plan.md` (this repo, v2) — chronological split design, CSS+VIF mechanics, block-bootstrap CI reporting, all reused as-is where noted above.
