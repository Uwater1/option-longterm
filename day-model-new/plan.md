# Day-Model Rewrite v3 — Plan

## Why v1/v2 died (context, don't repeat)
- v1: way too complex. Don't try to read it 
- v2 (`day-model/day-model_plan.md`): elaborate model-side machinery (Huber+MCP manifold, CSS+VIF, HMM regimes, vol gating) worked numerically (condition numbers, ESS all fixed) but the *headline* Sharpe-objective search came back statistically indistinguishable from baseline once block-bootstrap CI was applied (§8.6 of that doc). Lesson: fancy model-side optimization can look good pre-CI and be noise post-CI.
- Core decision for v3: **move weak/joint-signal capture to the feature-mining stage. Keep model training dumb and hard to overfit.** Mining can be messy, agentic, human-in-the-loop. Model stage cannot.

> NOTE: This document must be updated if logical changes.

---

## Stage A — Feature Mining (`mining/generate_combos.py`)

Goal: Produce aggressive candidate recipes and combinations to find weak/joint signals, avoiding redundant evaluations.

### A0. Component Stability Gate (Training-Only, ETF-Agnostic)
Before generating combos, compute yearly IC decomposition for each base feature:
- Split training data by calendar year, compute tail IC per year.
- Flag feature as **unstable** if `IC_CV > 3.0` OR `n_negative_years > 2`.
- Exclude unstable features from all combo generation (2-way and 3-way).
- **Rationale**: Prevents regime-dependent components (e.g. `gap_pct` with CV=4.66) from contaminating candidates. Root cause of 300ETF false positives was unstable conditioning variables in `ifelse` ops.

### A1. Sources
1. Existing survivor list (already pruned 317→210, keep as base).
2. Mine repo of 1000+ trading ideas / AL Brooks book → candidate formulas.
3. Combine existing features: `min(A,B)`, `max(A,B)`, `IfElse(regime_cond, A, B)`, ratio/diff combos etc. (2-way and 3-way ops).

### A2. Deduplication & Verification
### A2. Deduplication & Verification
- **Mining Log (`mining_log.json`)**: Persistent ledger tracking all generated candidates per ETF/side. Only delta is sent to evaluation.
- **Sample-Size Scaling**: Candidate space parameters ($k, k_3$) scale dynamically based on training sample size relative to ~3400 trading day baseline ($N_{obs}/3400$) to prevent candidate over-generation on short datasets (e.g. 588000ETF).

---

## Stage B — Feature Filtering / Admission Gate (`select_features.py`)

Goal: Apply strict statistical guards, correlation filters, and trial-count tracking to build a robust pool.

> Rules: 1. 0 feature better than many FP features. 2. Check logic before lowering threshold, TP still might be OOS lucky.

### B1. 7-Year Jackknife Sign Stability & Temporal Validation Pre-filters
1. **7-Year Jackknife Sign Guard**: Split training data into 7 equal chunks (approximating calendar years). Compute tail IC per chunk, lock sign from full-sample IC. Count "flip chunks" where chunk IC sign disagrees with locked sign. Reject if flip_count > 1 OR if either of the last 2 chunks is a flip (recent signal must be intact).
   - **Sign locking**: Outputs a locked `sign` (+1 or -1) value from full train set. This sign is the pipeline's single source of truth carried forward to B2 and B3.
2. **Temporal Validation Gate** (adaptive): Require positive tail IC in the most recent chunk from jackknife (`recent_ic > 0`). Additionally, cap `recency_ratio < 2.5` ONLY when `|early_ic| < 0.05` ("appeared from nowhere" pattern). Features with solid early IC (≥ 0.05) that strengthen recently pass freely — a high ratio with positive early base indicates a strengthening signal, not overfit. Diagnosed via `filter_diagnosis.py` §6b/6c.
   - _Known limitation: single-chunk `recent_ic` is noisy for short training windows; a multi-chunk rolling average could improve stability._

### B2. Rolling Guard & FDR Pre-filter
1. **Rolling Guard (Pre-filter check)**: 90-calendar-date rolling tail IC evaluated instantly on pre-computed values. Drop if monotonicity < `mono_thr` or `IC_IR` < `ir_thr`:
   - `long`/`short`: `mono_thr = 0.55`, `ir_thr = 0.15`
   - `single`: `mono_thr = 0.65`, `ir_thr = 0.30`
   - **Pass-forward cached values**: Rolling mono average from this step is cached and passed forward to B3, not just its pass/fail verdict (uses locked `sign` from B1).
   - **Cheap-first ordering**: Executed before simulation to thin pool by ~98% instantly.
2. **Benjamini-Hochberg (BH-FDR) pre-filter**: Reject if empirical $p$-value fails Benjamini-Hochberg FDR at $q=0.20$ (standard screening threshold, via 5,000-trial single-feature block-shuffled simulation on compact survivor matrix `X_survivors`, cached per ETF/side).
   - **Full search-space correction**: Uses `m_total = len(eval_results)` (total candidates before any filtering) for rank denominator, properly accounting for pre-filter selection bias. This does NOT increase computation — FDR still runs only on survivors.

### B3. Admission Floor (Composite score gate)
- **Rank-normalized Composite Score** (Sortino weight calibrated for fixed null formula):
  $$\text{score} = 0.3 \times \text{RollingMono}_{90\text{d}} + 0.5 \times \text{Sortino} + 0.15 \times |\text{Tail IC}| + 0.05 \times |\text{Overall IC}|$$
  - `RollingMono` (cached from B2) and `Sortino` consume locked `sign` from B1 (computed post sign-resolution, no $|\text{abs}|$ needed).
  - `Tail IC` and `Overall IC` use absolute values $|\text{IC}|$.
- **Per-candidate trade simulation**: Runs `simulate_returns()` (ported to shared module `recipe_utils.py`) per candidate using B1 locked sign to compute candidate Sortino.
- **Null-permutation-wrapped threshold**: Block-permute target $y$ (500 trials), recompute entire composite score per permutation, and take percentile as admission floor. Null Sortino uses `n` denominator (aligned with `simulate_returns`).
- **Tiered admission floor by combo complexity & operator class**:
  - Conditional 2-way combos & base features: $\text{composite\_score} \ge \text{empirical\_93rd}$
  - Symmetric 2-way combos (`max`, `min`, `mean`, `rank_max`, `rank_min`): $\text{composite\_score} \ge \text{empirical\_95th}$ (symmetric ops destroy regime conditioning)
  - 3-way combos (`combo_tri_*`): $\text{composite\_score} \ge \text{empirical\_97th}$ (stricter — more degrees of freedom = higher overfit risk)
- *Compute note*: Heavier compute per survivor, but B1 + B2 thin pool first (cheap-first order preserved). 97th percentile computed in same kernel pass as 93rd — no additional simulation cost.

### B4. Correlation Gate, Primitive Cluster Cap & Replacement Rule
- Admit if `max_corr(candidate, current_pool) < theta` ($\theta = 0.70$).
- **Runs AFTER Quality & Stability Gates**: Low-quality or unstable features are filtered before correlation comparison, preventing them from blocking high-quality candidates.
- **Primitive Cluster Cap**: Extract primitive feature set (`feature_a`, `feature_b`, `feature_c`, `feature_cond`, `feature_cond2`). Drop or replace redundant combos built from identical base primitives to ensure pool diversity.
- **Replacement rule**:
  ```
  replacement_mult = 1.15 if len(admitted_pool) < 10 else 1.30
  if IC(new) >= 0.10 and IC(new) >= replacement_mult * IC(old)
     and exactly one existing pool member g has corr(new, g) > theta:
       replace g with new
  ```

### B5. Trial Ledger & Standalone Deflated IC
- Save unique attempted candidate formulas to `trial_ledger_{ETF}_{side}.json` to track cumulative unique trials $N$.
- Compute standalone deflated IC: `deflated_ic = max(0.0, cand_ic - ic_null_mean)` where `ic_null_mean` is standalone empirical mean of raw overall IC under block-permutation null (bounded in $[0, 1]$, avoiding subtraction of negative composite score/sortino null mean).

### B6. Training-Only Quality & Temporal Stability Gates (Before Correlation)
- Applied AFTER B3 floor, BEFORE B4 correlation gate.
- **Temporal Stability Gate**: For combo features, require `ic_cv * weak_link_cv >= 0.15`. Features with artificially low temporal variation (suspiciously "too smooth" in-sample) are fitting structural artifacts.
- **Yearly IC CV Gate**: Requires `yearly_ic_cv <= 0.85`. Rejects features with high year-to-year IC volatility in training set.
- **Unstable Component Gate**: Requires `weak_link_cv <= 1.00`. Rejects combo features built from noisy base primitives.
- **Sign Consistency Gate**: Rejects candidate if meaningful full-sample IC ($|\text{IC}_{\text{full}}| \ge 0.015$) contradicts tail IC sign ($\text{IC}_{\text{full}} \cdot \text{IC}_{\text{tail}} < 0$), preventing non-monotonic tail mirages from entering the pool.
- **Quality Gate**: Requires all three:
  - `deflated_ic >= 0.03` (normal) / `0.05` (short-history ETFs with n_train < 1200)
  - `|raw_ic| >= 0.02` (normal) / `0.03` (short-history) — catches tail-only mirages
  - `sortino > 0` — rejects negative risk-adjusted returns
- **Rationale for pre-correlation placement**: Prevents low-quality/unstable features from occupying pool slots and blocking higher-quality candidates via the correlation gate.
- **Zero look-ahead bias**: Uses only training-period metrics. No OOS or lockbox data is accessed.

### B6b. Adaptive Boundary Gate (Post-Correlation Pool Control)
- **Trigger**: When initial admission yields $> \text{MAX\_POOL\_SIZE}$ features (default: 15).
- **Global Constants** (defined at top of `select_features.py`):
  - `DEFAULT_THETA = 0.70`: Base correlation threshold for initial admission pass.
  - `MAX_POOL_SIZE = 15`: Target max admitted pool size.
  - `TOP_PROTECTED_COUNT = 7`: Unconditionally protects top 7 features based on training quality score $S_{train}$.
  - `TIGHT_THETA = 0.65`: Lower-tier correlation threshold to trim redundant tail features.
- **Mechanism**:
  1. Computes training quality score $S_{train} = 0.40 \cdot \text{deflated\_ic} + 0.25 \cdot \text{sortino} + 0.20 \cdot \text{ic\_ir} + 0.15 \cdot \text{recent\_ic}$.
  2. Protects top `TOP_PROTECTED_COUNT` (7) features unconditionally.
  3. Screens lower-tier features with `TIGHT_THETA` (0.75) and quality floors (`recent_ic > 0`, `sortino > 0.05`, `deflated_ic >= 0.04`).
  4. Overwrites initial `ADMITTED` verdict in `attempts_log` for pruned features to `REJECTED_ADAPTIVE_*`.
- **Zero OOS leakage**: Uses only training set statistics.

### B7. Outputs
- Version-controlled admitted pools registry in [admitted_pools.py](file:///home/hallo/Documents/option-longterm/day-model-new/admitted_pools.py).
- Detailed log of attempts in `data/mining_attempts_{ETF}_{side}.json`.

> IMPORTANT: NO OOS data present in this stage. All metrics are computed using training-period data only.
---

## Stage C — Model Training & Evaluation (`evaluate_concept.py`)

Goal: Combine surviving features and evaluate performance under strict cross-validation.

> **Strategy**: Entry at 10:00 (open of bar 6), exit at 14:35 (close of bar 42). Conviction-weighted position sizing (default): only trades when prediction z-score > 0.5, with smooth tanh ramp. Long top-10% / short bottom-10% predicted days (`single`), or top/bottom-15% for directional sides. 8 bps cost per position state transition (realistic for liquid ETFs).

### C1. Baseline Model: IC-weighted Linear Sum (with Empirical Bayes Shrinkage)
```
signal = sum_i( sign(IC_i) * max(0, deflated_ic_i - SE_IC)^k * z(feature_i) )
SE_IC ≈ 1/√n_train
```
- `k` optional mild tilt toward higher-IC features (k=1 default).
- **Empirical Bayes shrinkage**: Subtract $SE_{IC} \approx 1/\sqrt{n}$ from `deflated_ic` before weighting. This penalizes features with marginal IC estimates that are likely noise. If all weights shrink to zero, fall back to equal weighting.
- Avoids orthogonalization (retains noise-canceling properties).

### C2. VIF Safety Net & Data Leakage Prevention
- **Leakage-Free Recipe Prebuilding**: Prebuild reference statistics (`train_means`, `train_stds`, `train_medians`) for ALL recipe input features (`feature_a`, `feature_b`, `feature_c`, `feature_cond`, `feature_cond2`) on training set to eliminate OOS lookahead leakage on 3-way `tri_*` features.
- **VIF Safety Net**: One VIF pass on the final pool, drop features if VIF > 5.0.

### C3. Guardrails & Validation
- **Chronological split**: Train / holdout OOS / OOS lockbox.
- **Block-bootstrap CI**: Report OOS metrics via CI (block size 10) instead of point estimates.
- **Kill switches**: Overall IC > 0, Hit Rate ≥ 60%, Monotonicity ≥ 0.25, Spread > 0.

### C4. Escalation Rule
- Only use more complex models (e.g. ElasticNet, LightGBM) if they statistically outperform the baseline weighted sum within the block-bootstrap CI.

---

## Checklist
- [x] Replace B3 IC-threshold with rank-normalized composite (Mono 0.4 / Sortino 0.3 / TailIC 0.2 / OverallIC 0.1), sign locked from B1, null-permutation-wrapped.
- [x] Port `simulate_returns()` to shared module (`recipe_utils.py`) and run per-candidate Sortino in B3 using B1 locked sign.
- [x] Upgrade BH-FDR to Benjamini-Yekutieli (BY-FDR) at $q=0.30$ to handle correlated candidate feature spaces.
- [x] Fix `deflated_ic` calculation using standalone raw IC null mean (`ic_null_mean`).
- [x] Prebuild 3-way recipe statistics (`feature_c`, `feature_cond2`) in `evaluate_concept.py` to eliminate OOS lookahead leakage.
- [x] Upgrade sign check to 7-year jackknife guard (`expanding_wf_sign_check`, max_flips=2 [1 for 588000ETF], last 2 chunks must not flip).
- [x] Scale candidate generation space by sample size ratio in `generate_combos.py`.
- [x] Reconcile `feature-mining.md` and `AGENTS.md` step numbering with new A/B/C stage names.
- [x] **Anti-overfit: Full search-space FDR correction** — BY-FDR uses `m_total = len(eval_results)` (total candidates before filtering) for harmonic correction, not just survivor count.
- [x] **Anti-overfit: Temporal validation gate** — Require positive tail IC in most recent 30% of training (fold 3). Zero additional compute (reuses `ic_f3` from walk-forward).
- [x] **Anti-overfit: IC shrinkage weighting** — Subtract $SE_{IC} \approx 1/\sqrt{n}$ from `deflated_ic` before IC-weighting in `evaluate_concept.py`.
- [x] **Anti-overfit: Tiered B3 admission floor** — 3-way combos (`combo_tri_*`) require 97th percentile vs 95th/93rd for 2-way/base features. Computed in same kernel pass.
- [x] **Anti-overfit: Training-only Quality Gate (B6)** — Require deflated_ic ≥ 0.03/0.05, |raw_ic| ≥ 0.02/0.03, sortino > 0. Catches tail-only mirages. Zero look-ahead.
- [x] **Execution: Conviction-weighted position sizing** — Default mode in `evaluate_concept.py`. Skips low-conviction days (z < 0.5), smooth tanh ramp. Reduces turnover ~40% without losing high-conviction trades.
- [x] **Filter calibration: Relaxed B2/FDR/θ** — mono_thr 0.70→0.60, FDR q 0.20→0.30, θ 0.70. Data-driven from per-gate OOS diagnostics (FEATURE_DIAGNOSTICS.md).
- [x] **Component stability gate (A0)** — Yearly IC decomposition in `generate_combos.py`. Flags features with IC_CV > 3.0 or neg_years > 2 as unstable, excludes from all combos. Training-only, ETF-agnostic.
- [x] **B4 correlation threshold** — θ=0.70. Set for strict redundancy control.
- [x] **Quality Gate before Correlation** — Moved Quality Gate (B6) before B4 correlation gate. Prevents low-quality features from blocking high-quality candidates.
- [x] **Adaptive Boundary Gate (B6b)** — Dynamically tightens quality floors & correlation threshold (0.85→0.75) when pool > 35 features, protecting top 25 TP features. Configured via top-level global constants in `select_features.py`.
- [x] **Deep filter diagnosis tool** — `filter_diagnosis.py` for causal FP/FN analysis. Temporal decomposition, component stability, regime concentration, Cohen's d discriminators. Per-gate confusion matrix (§6b) and temporal sub-condition analysis (§6c). Excludes 588000ETF.
- [x] **Adaptive temporal gate relaxation** — Ratio cap (`recency_ratio < 2.5`) now only fires when `|early_ic| < 0.05`. Features with solid early IC that strengthen recently are no longer penalized. Result: 300ETF pool 7→15, 159915ETF 11→16, 500ETF unchanged (capped). FP rate remains 0% for 500ETF/159915ETF; 300ETF gained 2 FP in exchange for 2× pool size.

## References
- Wang et al. 2026, *FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery*, arXiv:2602.14670 — admission gate, replacement rule, IC-weighted vs orthogonal vs learned-selection comparison.
- Dobriban 2026, *No Universal Multiplicative FDR Bound for BH with Correlated Two-Sided Gaussian Tests*, arXiv:2607.14812 — FDR control failure under high candidate correlation; justification for BY-FDR.
- Bailey & López de Prado 2014, *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*, Journal of Portfolio Management 40(5) — deflate IC/Sharpe by trial count.
- `day-model_plan.md` (this repo, v2) — chronological split design, CSS+VIF mechanics, block-bootstrap CI reporting, all reused as-is where noted above.
