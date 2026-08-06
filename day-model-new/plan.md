# Day-Model Rewrite v3 — Plan

## Why v1/v2 died (context, don't repeat)
- v1: way too complex. Don't try to read it.
- v2 (`day-model/day-model_plan.md`): elaborate model-side machinery (Huber+MCP manifold, CSS+VIF, HMM regimes, vol gating) worked numerically (condition numbers, ESS all fixed) but headline Sharpe-objective search was statistically indistinguishable from baseline post block-bootstrap CI (§8.6).
- Core decision for v3: **move weak/joint-signal capture to feature-mining stage. Keep model training simple and hard to overfit.** Mining can be messy and agentic; model stage cannot.

> NOTE: Keep this document synchronized with implementation in `select_features.py` and `recipe_utils.py`.

---

## Stage A — Feature Mining (`mining/generate_combos.py`)

Goal: Produce aggressive candidate recipes and combinations to find weak/joint signals while avoiding redundant evaluations.

### A0. Component Stability Gate (Training-Only, ETF-Agnostic)
Before generating combos, compute yearly IC decomposition for base features:
- Split training data by calendar year; compute tail IC per year.
- Flag feature as **unstable** if `IC_CV > 3.0` OR `n_negative_years > 2`.
- Exclude unstable features from all 2-way and 3-way combo generation.

### A1. Sources & Combination Operators
1. **Base Primitives**: Existing survivor list (base technical, momentum, volume flow, and microstructure primitives) + domain candidate formulas.
2. **2-Way Combinations (13 operators)**:
   - **Bounds & Quantiles**: `min(A,B)`, `max(A,B)`, `rank_min(A,B)`, `rank_max(A,B)`
   - **Linear & Normalized Blends**: `mean(A,B)`, `z_sum(A,B)`, `z_diff(A,B)`
   - **Differences & Distances**: `diff(A,B)`, `abs_diff(A,B)`, `clamp_diff(A,B)`, `rel_diff(A,B)`
   - **Interactions & Ratios**: `product(A,B)`, `sig_product(A,B)`, `ratio(A,B)`
   - **Regime-Conditioned Branching**: `IfElse(regime_cond, A, B)` (gates feature $A$ vs $B$ based on volatility, VIX, GARCH, or trend regimes)
3. **3-Way Combinations (6 operators)**:
   - **Aggregations & Medians**: `tri_mean(A,B,C)`, `tri_min(A,B,C)`, `tri_max(A,B,C)`, `tri_median(A,B,C)`
   - **Normalized Composites**: `tri_z_mean(A,B,C)`, `tri_sig_max(A,B,C)`, `tri_ifelse(cond, A, B)`


### A2. Deduplication & Verification
- **Mining Ledger (`mining_log.json`)**: Persistent ledger tracking candidate formulas per ETF/side; evaluates only new deltas.
- **Sample-Size Scaling**: Candidate space parameters ($k, k_3$) scale dynamically based on training sample size relative to ~3400 trading day baseline ($N_{obs}/3400$).

---

## Stage B — Feature Filtering / Admission Gate (`select_features.py`)

Goal: Apply strict statistical guards, correlation filters, and trial-count tracking to build a robust pool.

### Global Thresholds & Constants (`select_features.py:L35-L76`)
```python
MAX_FLIPS = 1                   # Max sign flip chunks allowed in 7-year jackknife
FDR_THRESHOLD = 0.20            # Benjamini-Hochberg (BH-FDR) q-value threshold
DEFAULT_THETA = 0.95            # Near-duplicate correlation threshold (B5 gate)

# Rolling Guard (90-calendar-day)
MONO_THR_SINGLE = 0.65          # Monotonicity threshold (single side)
MONO_THR_DIR = 0.60             # Monotonicity threshold (directional: long/short)
IR_THR_SINGLE = 0.30            # IC_IR threshold (single side)
IR_THR_DIR = 0.15               # IC_IR threshold (directional: long/short)

# Temporal & Quality Gate Thresholds
MAX_RECENCY_RATIO = 2.5         # Moderate recency spike cap (when |early_ic| < 0.03)
MAX_HALF_RATIO = 1.80           # Moderate half-ratio spike cap (when |early_ic| < 0.03)
MAX_EXTREME_RECENCY_RATIO = 4.0 # Universal extreme recency spike cap
MAX_EXTREME_HALF_RATIO = 2.50   # Universal extreme half-ratio spike cap
MIN_EARLY_IC_THRESHOLD = 0.03   # Minimum early IC required to bypass moderate ratio caps
MAX_YEARLY_IC_CV = 1.00         # Max yearly IC coefficient of variation
MIN_STABILITY_PRODUCT = 0.09    # Minimum (yearly_ic_cv * weak_link_cv) product for combos
MAX_NEGATIVE_REGIMES = 1        # Max vol-quintile regimes with negative IC
MIN_IC_STD_REGIMES = 0.030      # Min IC std across vol regimes (for regime uniformity check)
MAX_IC_CV_FOR_UNIFORM = 0.85    # Max yearly IC CV triggering regime uniformity rejection

# Robustness Gate (A/B-validated, see research_gate_ab_test.py)
BOOT_B = 199                    # Bootstrap resamples
BOOT_BLOCK = 10                 # Moving-block bootstrap block length (days)
BOOT_CI_PCT = 5.0               # One-sided CI lower-bound percentile
COST_BASE = 0.0008              # 8 bps per active day (sync w/ simulate_returns)
COST_STRESS_MULT = 2.5          # G7 base stress multiplier applied to COST_BASE (20bp)
DEEP_STRESS_MULT = 3.0          # B5 Deep-Stress Eliminator multiplier (24bp)
DEEP_STRESS_MIN_SPACE = 2500    # B5 fires only when candidate space size exceeds this
ANNUAL_DAYS = 244               # Trading days per year (sync w/ simulate_returns)
ROBUST_GATE_SEED = 42           # Bootstrap RNG seed (deterministic verdicts)
```

### B1. 7-Year Jackknife Sign Guard & Temporal Validation Pre-filters
1. **7-Year Jackknife Sign Guard**: Split training data into 7 equal chunks. Lock sign from full-sample IC. Count flip chunks where chunk IC sign disagrees with locked sign. Reject if `flip_count > MAX_FLIPS (1)` OR if either of the last 2 chunks is a flip.
2. **Temporal Validation Gate**:
   - Require `recent_ic > 0` (positive tail IC in recent training chunk).
   - Moderate spike rejection: Reject if (`recency_ratio >= 2.5` OR `half_ratio >= 1.80`) AND `|early_ic| < 0.03`. Solid early IC ($\ge 0.03$) passes freely.
   - Extreme spike rejection: Reject if `recency_ratio >= 4.0` OR `half_ratio >= 2.50` regardless of early IC.

### B2. Rolling Guard & BH-FDR Pre-filter
1. **Rolling Guard**: 90-calendar-date rolling tail IC evaluated on pre-computed values. Drop if `monotonicity < mono_thr` or `IC_IR < ir_thr` (`mono_thr`: 0.65 single / 0.60 dir; `ir_thr`: 0.30 single / 0.15 dir).
2. **BH-FDR Pre-filter**: Reject if empirical $p$-value fails Benjamini-Hochberg FDR at $q=0.20$. Uses full search-space correction `m_total = len(eval_results)` for rank denominator to account for candidate selection bias.

### B3. Admission Floor & Deflated IC
- **Composite Score**:
  $$\text{composite\_score} = 0.3 \times \text{mean\_tail\_ic} + 0.5 \times \text{sortino} + 0.15 \times |\text{overall\_ic}| + 0.05 \times |\text{raw\_ic}|$$
  `sortino` is calculated via `simulate_returns()` using the locked sign from B1.
- **Tiered Admission Floor** (via 500-trial block-permutation null):
  - 3-way combos (`combo_tri_*`): empirical 97th percentile
  - Symmetric 2-way combos (`max`, `min`, `mean`, `rank_max`, `rank_min`): interpolated 95th percentile
  - Conditional 2-way combos & base features: empirical 93rd percentile
- **Deflated IC**: `deflated_ic = max(0.0, cand_ic - ic_null_mean)`.

### B4. Training-Only Quality & Temporal Stability Gates
- **Yearly IC CV Gate**: Require `yearly_ic_cv <= MAX_YEARLY_IC_CV (1.00)`.
- **Temporal Stability Gate**: For combo features, require `ic_cv * weak_link_cv >= MIN_STABILITY_PRODUCT (0.09)`.
- **Negative Vol-Regime Gate**: Reject if IC is negative in $> 1$ vol-quintile regimes (`n_neg_reg > MAX_NEGATIVE_REGIMES (1)`).
- **Regime Uniformity Gate**: Reject if combo feature has `ic_std_across_regimes < MIN_IC_STD_REGIMES (0.030)` AND `ic_cv > MAX_IC_CV_FOR_UNIFORM (0.85)` (catches suspiciously regime-uniform yet yearly-erratic overfit signals).
- **Quality Gate**: Require `deflated_ic >= min_deflated_ic` (0.03 normal / 0.05 short-history), `sortino > 0`, and `|raw_ic| >= min_raw_ic` (0.02 normal / 0.03 short-history).
- **Robustness Gate** (immediately after Quality Gate, before B5/B6 — all badness gates run before redundancy resolution, filter → dedupe):
  - **G7 Cost-Stress Sortino**: Rebuild train-window daily strategy returns with the exact `simulate_returns` binary position logic (`_tail_positions_binary` + `enforce_absolute_sign`). Reject with verdict `REJECTED_COST_STRESS` if Sortino at `COST_STRESS_MULT × COST_BASE` (2.5× cost, 20bp) is `<= 0`. Runs first (cheap, O(n)).
  - **G4 Block-Bootstrap Sortino CI**: Reject with verdict `REJECTED_BOOTSTRAP_CI` if the `BOOT_CI_PCT`-th percentile (5th) of `BOOT_B` (199) moving-block (`BOOT_BLOCK = 10`) bootstrap Sortinos on the base-cost return series is `<= 0`. Fully vectorized; deterministic RNG (`ROBUST_GATE_SEED`).
  - Both metrics stored on the candidate and logged into `ADMITTED*` attempt entries for downstream diagnosis.
  - **Placement rationale (pre-B6, filter → dedupe)**: rejected features never enter the B6 cascade, so they can neither evict good members nor leave holes; each correlation cluster admits its best *robust* representative. Post-B6 enforcement was tried and reverted: under it a bad feature could evict a good pool member via the Q-score replacement rule and then die at the gate, silently losing the good feature. Empirically the two placements are near-identical (500ETF p2017_2025: pool 258/FP 10 pre-B6 vs 253/FP 9 post-B6); the apparent late-window regression vs the 8/3 baseline was a search-space artifact (candidate space grew 3,037 → 4,744 on 8/3 16:05, after that baseline was produced) — a same-space no-gate control admits 299, so the gate shrinks every pool.
  - **A/B evidence** (`research_gate_ab_test.py`, reports `GATE_AB_TEST_{admitted,preb4}.md`): G7 FP-kill 14.7% admitted / 8.9% preb4 vs TP-kill 2.9% / 1.8%; G4 FP-kill 15.2% / 8.2% vs TP-kill 4.4% / 2.6%. Other claude_said.txt candidates (PSR, skew/kurtosis, payoff, IC-concentration, regime Sortino) were rejected by the A/B evidence.

### B5. Deep Cost-Stress Eliminator (conditional)
- Fires **only when the candidate space size exceeds `DEEP_STRESS_MIN_SPACE` (2500)**; otherwise skipped (logged). Candidate space size is used instead of the B4 survivor count because the latter varies too much across windows (~100–160 for 300ETF) to separate ETFs reliably.
- Rejects with verdict `REJECTED_DEEP_STRESS` if Sortino at `DEEP_STRESS_MULT × COST_BASE` (3× cost, 24bp) is `<= 0`.
- **Rationale**: stress strictness should scale with multiple-testing pressure. A/B sweeps (2.5-era labeled pools) show 3.0× kills 60% of residual FPs at a 2.6× FP:TP ratio in large spaces (500ETF ~4.7k candidates, 159915ETF ~3k), but over-purges small spaces (300ETF ~1.8k: pool collapsed 62→6, all 4 TPs lost in p2017_2025). Upstream-gate loosening was ruled out as an alternative: a full OOS-labeling diagnosis found ~0 robust-TP supply recoverable from B2–B4 rejects (their kills are redundant with the Sortino gates).
- **Optimization**: reuses `_raw_ret`/`_abs_pos` arrays already computed at the base Robustness Gate — one extra O(n) Sortino per entrant, no position recomputation.
- **Logging**: every entrant gets `deep_stress_sortino` in its attempt entry (B6 `ADMITTED*`/`REJECTED_REDUNDANCY` entries carry `stress_sortino`, `sortino_ci_low`, `deep_stress_sortino`; rejects get full `REJECTED_DEEP_STRESS` entries).

### B6. Correlation Gate & Recalibrated $Q$-Score Replacement Rule
- Pre-sort candidates by $Q$-score descending so highest quality features enter B6 first.
- Admit candidate if `max_corr(candidate, current_pool) < DEFAULT_THETA (0.95)`.
- If `max_corr >= 0.95`, candidate replaces correlated pool member(s) ONLY IF its $Q$-score strictly beats ALL correlated pool members (`cand_q > old_q` for all correlated members).
- **Recalibrated $Q$-Score Formula** (`select_features.py:L1335-L1377`):
  $$\text{q\_score} = 0.50 \times \text{DeflatedIC} + 0.25 \times \text{Sortino} + 0.15 \times \text{RecentIC} + 0.10 \times \text{IC\_IR} - \text{TotalPenalty}$$
  where $\text{TotalPenalty} = \min(0.03, \text{cv\_penalty} + \text{half\_penalty} + \text{complexity\_penalty})$:
  - $\text{complexity\_penalty} = 0.03$ (3-way `combo_tri_*`), $0.01$ (2-way `combo_*`), $0.00$ (base)
  - $\text{cv\_penalty} = 0.02 \times \max(0.0, \text{ic\_cv} - 0.50)$
  - $\text{half\_penalty} = 0.02 \times |\text{half\_ratio} - 1.0|$

### B6. Downstream ONC Feature Clustering (`feature_clusters.py`)
- Computes Spearman rank correlation matrix on training feature values, converted to angular distance $d(i,j) = \sqrt{0.5 \cdot (1 - \rho_{ij})}$.
- Runs K-Means sweep $K \in [2, \min(10, N-1)]$, selecting $K$ by silhouette score with recursive re-splitting.
- Outputs `data/cluster_assignments_{etf}_{side}.json`.
- Diversity is enforced downstream in `newtrade` (picks max 1 feature per cluster per day via rolling EMA IC).

### B7. Outputs & Trial Ledger
- Saves cumulative unique trials $N$ to `trial_ledger_{ETF}_{side}.json`.
- Registry of admitted pools in [admitted_pools.py](file:///home/hallo/Documents/option-longterm/day-model-new/admitted_pools.py).
- Detailed execution logs in `data/mining_attempts_{ETF}_{side}.json`.

---

## Stage C — Model Training & Evaluation (`evaluate_concept.py`)

Goal: Combine surviving features and evaluate performance under strict cross-validation.

> **Execution Setting**: Entry at 10:00 (bar 6 open), exit at 14:35 (bar 42 close). Conviction-weighted position sizing with smooth tanh ramp (z > 0.5). 8 bps transaction cost per state change.

### C1. Baseline Model: IC-Weighted Linear Sum (with Empirical Bayes Shrinkage)
```
signal = sum_i( sign(IC_i) * max(0, deflated_ic_i - SE_IC)^k * z(feature_i) )
SE_IC ≈ 1 / sqrt(n_train)
```
- Empirical Bayes shrinkage subtracts $SE_{\text{IC}} \approx 1/\sqrt{n}$ from `deflated_ic` before weighting.
- Fallback to equal weighting if all weights shrink to zero.

### C2. VIF Safety Net & Data Leakage Prevention
- **Leakage-Free Recipe Prebuilding**: Reference statistics (`train_means`, `train_stds`, `train_medians`) prebuilt on training set for all recipe input features.
- **VIF Safety Net**: Single VIF pass on final pool, dropping features with VIF > 5.0.

### C3. Guardrails & Validation
- **Chronological Split**: Train / holdout OOS / OOS lockbox.
- **Block-Bootstrap CI**: Report OOS metrics via block-bootstrap confidence intervals (block size 10).
- **Kill Switches**: Overall IC > 0, Hit Rate $\ge 60\%$, Monotonicity $\ge 0.25$, Spread > 0.

---

## Compacted Progress Checklist

### Stage A — Mining
- [x] Base primitive feature generation & persistent candidate logging (`mining_log.json`).
- [x] Candidate search space auto-scaling by training sample size ratio.
- [x] Training-only Component Stability Gate (A0: `IC_CV > 3.0` or `n_neg_years > 2`).

### Stage B — Selection & Admission Gate
- [x] **B1 Sign & Temporal**: 7-year jackknife sign guard (`MAX_FLIPS = 1`, last 2 chunks intact) & adaptive temporal gate (`recent_ic > 0`, ratio caps with `MIN_EARLY_IC_THRESHOLD = 0.03`).
- [x] **B2 Rolling & FDR**: 90d rolling guard (`mono_thr` 0.65/0.60, `ir_thr` 0.30/0.15) & BH-FDR gate ($q=0.20$) with full search space correction ($m_{\text{total}}$).
- [x] **B3 Composite Floor**: Sign-locked composite score ($0.3\text{Mono} + 0.5\text{Sortino} + 0.15\text{TailIC} + 0.05\text{RawIC}$) with tiered admission floor (97th tri / 95th sym / 93rd cond & base) and standalone `deflated_ic`.
- [x] **B4 Quality & Stability**: Pre-correlation Quality Gate (`deflated_ic \ge 0.03/0.05`, `sortino > 0`, `|raw_ic| \ge 0.02/0.03`), Yearly IC CV gate (`\le 1.00`), Stability Product gate (`\ge 0.09`), Negative Regime gate (`\le 1`), Regime Uniformity gate (`ic_std < 0.030` & `ic_cv > 0.85`), and Robustness Gate (G7 cost-stress Sortino `> 0` at 2.5× cost; G4 block-bootstrap Sortino CI 5th-pct `> 0`).
- [x] **B5 Deep-Stress Eliminator**: conditional (fires when candidate space > 2500) extra stress test at 3× cost (24bp), verdict `REJECTED_DEEP_STRESS`; reuses base-gate return arrays; every entrant logged with `deep_stress_sortino`.
- [x] **B6 Correlation & Q-Score**: Pre-sort pool candidates by recalibrated $Q$-score ($50\%\text{DefIC} + 25\%\text{Sortino} + 15\%\text{RecentIC} + 10\%\text{IC\_IR} - \text{TotalPenalty}_{\le 0.03}$) and strict correlated replacement at $\theta = 0.95$.
- [x] **B7 Downstream Diversity**: de Prado ONC feature clustering (`feature_clusters.py`) for downstream group-constrained selection in `newtrade`.
- [x] **B8 Ledger & Logging**: Persistent trial ledger tracking cumulative trials $N$ and versioned pool output registry (`admitted_pools.py`).

### Stage C — Model Training & Evaluation
- [x] Empirical Bayes IC shrinkage weighting (`evaluate_concept.py`).
- [x] Leakage-free recipe prebuilding for 3-way combo statistics.
- [x] Conviction-weighted position sizing (tanh ramp, z-threshold 0.5).

### Diagnostics & Validation Tools
- [x] Deep filter diagnosis tool (`filter_diagnosis.py`) for causal FP/FN analysis, Cohen's d discriminators, and temporal sub-condition tracking.

---

## References
- Wang et al. 2026, *FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery*, arXiv:2602.14670.
- Dobriban 2026, *No Universal Multiplicative FDR Bound for BH with Correlated Two-Sided Gaussian Tests*, arXiv:2607.14812.
- Bailey & López de Prado 2014, *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*, Journal of Portfolio Management 40(5).
- López de Prado & Lewis 2019, *Detection of False Investment Strategies Using Unsupervised Learning*, SSRN 3517595.
- `day-model_plan.md` (v2 plan, preserved historical reference).
