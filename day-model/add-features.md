# Feature Proposal Specification — Day-Model (v2)

## Background

Intraday linear alpha model predicting single-session `trade_return` for Chinese equity
ETFs. This spec governs how new features get proposed and admitted into the pipeline.

v2 changes vs v1: adds pre-mining gates, per-ETF prioritization, redundancy checks,
mandatory leakage self-test, and batch-size limits. These exist because prior mining
rounds diluted an already-thin candidate pool (238 features / ~2200 selection-train rows)
without checking whether the pipeline could even use them — see `feature_pruning_plan.md`.

---

## 0. Gate: do not propose features until these are true

- [ ] MCP sparsity bug fixed (γ search range), confirmed active-feature-count < selected-
      feature-count on a clean run (not 28/29, 26/26, 12/12 — that's ridge behavior, not MCP).
- [ ] Plateau hyperparameter selector fixed (min-neighbor-count gate), confirmed it never
      again selects a trial with negative objective over a positive raw-best.
- [ ] Feature pruning pass complete (see `feature_pruning_plan.md`) — dead-weight tier-3
      features removed or deprecated, so new proposals aren't diluting an already-bloated pool.

If any box unchecked, do not run this spec. Fix pipeline, THEN mine.

---

## Target & Causality (unchanged from v1)

- **Target**: `trade_return = log(close[14:30] / open[decision_bar+1])`
- **Decision bar**: closes 10:00 (bar index 5). Entry at bar 6 open.
- **Causality constraints**:
  - Early-bar features: only consume 5m bars `[0..5]` (9:30–10:00).
  - Day-level features: shifted by 1 day.
  - Yesterday-mirror features: full-day/early-bar metrics from yesterday, shifted 1 day.

---

## 1. Mandatory leakage self-test (NEW — was missing in v1)

Every proposed feature ships with a passing result from this test before it enters
`build_features.py`. No exceptions, no "obviously causal" shortcuts — free-form JIT code
from multiple contributors is exactly where lookahead bugs hide.

**Perturbation test**: for early-bar features, shuffle/zero out bars `[6..end]` for a
sample of days and confirm the feature value is unchanged. For day-level/yesterday
features, shift the feature's source date forward by 1 day and confirm the joined value
in `build_features.py` output changes (proves the shift is actually applied, not a no-op
due to an indexing bug). Script this once (`test_feature_causality.py`), every new feature
runs through it in CI before merge.

---

## 2. Redundancy check against current active-feature set (NEW)

Before proposing, check `feature_pruning_plan.md` Tier 1 core-signal list for the target
ETF. A near-duplicate of an already-consistently-active feature (same underlying
mechanism, different window/normalization) is fine — encouraged even, per Section 4 — but
must be labeled `variant_of: <existing_feature_name>` in the proposal table, not submitted
as if novel. Reviewer prioritizes variants of Tier 1 features over entirely new mechanisms;
they have the best prior odds of surviving screening.

---

## 3. Batch size cap (NEW)

Max **+30% of current candidate count per ETF per mining round** (currently 238 →
propose ≤64 new features per round, across all contributors combined). Forces
prioritization instead of shotgun submission. Rationale: adding candidates without adding
training rows shrinks the many-weak-signals replication ratio — more features chasing the
same ~2200 rows makes OOS generalization worse on average, not better, unless each new
feature is high-conviction.

---

## Chinese Market Context (unchanged, now with per-ETF priority weighting)

1. **Market Segmentation & Dual Limits**: SSE 50 / CSI 300 / CSI 500 (±10% limit) vs
   STAR 50 (588000) / ChiNext (159915) (±20% limit, growth/tech, different vol regime).
2. **Lunch Break Split**: 11:30–13:00 halt, "intraday gap" for news accumulation.
3. **Ricequant Data**: Securities Margin, Capital Flow, Northbound Connect, ATM IV/VIX.

### Per-ETF mining priority (NEW)

| ETF | Status | Priority |
|---|---|---|
| 588000 (STAR50) | Structurally sick: Val IC -0.17, deflated -0.36, only 12 candidates survive screening. Generic-feature mining has failed here 4 runs running. | **Do not mine generic features.** Prioritize STAR50-specific mechanisms only: 20%-limit proximity, retail-liquidity-surge patterns, growth/tech sector rotation proxies. If a generic feature also happens to help here, fine, but don't submit generic proposals targeting this ETF specifically. |
| 159915 (ChiNext) | Best-performing, consistent core-feature set (5/5 hit rate on 7 features). | Good candidate for variant-mining (Section 2) — extend the working mechanisms, don't reinvent. |
| 300 / 500 | Moderate, mixed generalization gap flags. | Normal priority. |

---

## Required Fields for Proposals (extended)

| Field | Description |
|---|---|
| **Feature Name** | Short, unique `snake_case` identifier. |
| **Category** | `early_bar`, `day_level`, or `yesterday`. |
| **Target ETF(s)** | Which ETF(s) this is proposed for — no longer "all 5 by default." Justify if proposing universally. |
| **Variant Of** | Existing Tier-1 feature name if this is a variant (Section 2), else `novel`. |
| **Concept / Source** | Trading concept, paper, or book reference. |
| **Formula & Math** | Mathematical definition / JIT-compatible logic. |
| **Microstructure Mechanism** | Economic/behavioral reason the pattern should persist in this specific ETF's regime. |
| **Normalization Method** | Scale invariance approach (ATR-divided, rolling 20d volume, etc.). |
| **Causality Self-Test Result** | Pass/fail from Section 1 test, attach output. |
| **Expected Correlation Sign** | Pre-registered hypothesis (+ or -) before screening runs. Post-hoc sign-fitting after seeing screening results is not a valid proposal — the point is a falsifiable prior, not fitting to what worked. |

---

## Target Areas for New Features (trimmed to highest-conviction, per-ETF tagged)

### 1. STAR50/ChiNext limit-proximity & retail sentiment (588000, 159915 priority)
- Proximity of early high/low to the 20% limit-up/limit-down threshold.
- Early volume surges relative to 20d median, STAR50-specific liquidity regime.

### 2. Lunch Break Transition (all ETFs)
- Early-morning trend persistence (HHI of price direction) predicting afternoon
  fade/continuation. Variant of `intraday_autocorr` (300ETF Tier 1) — tag as variant.

### 3. Option IV/VIX Dynamics (300, 500 priority — `vix_iv_spread`/`iv_diff_1d` already Tier 1 for 300)
- Overnight VIX-IV spread change, 1d rate-of-change of Ricequant VIX vs historical
  quantiles. Propose as variants of existing IV features, not new mechanism.

### 4. Capital Flow / Northbound Momentum (300 priority — `northbound_net` Tier 1)
- Northbound net buy normalized by yesterday's total volume. Variant-tag against
  `northbound_net`.

---

## Changelog requirement (NEW)

Every merged feature gets one line in `FEATURE_CHANGELOG.md`: name, date added, target
ETF(s), proposing contributor, one-line mechanism summary. When a feature gets deprecated
via the pruning process, same file gets the deprecation entry with reason and last-active
run ID. This is the only way frequency-audits like `feature_pruning_plan.md` stay possible
without manually re-deriving history from old REPORT.md files.