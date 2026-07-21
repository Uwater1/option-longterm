# Feature Mining Plan — Day-Model Rewrite v3

Mining stage is messy/agentic/human-in-the-loop by design (per v3 plan.md). Gating that decides
what survives into the model is NOT messy — it's the validated `select_features.py` pipeline
(block-permutation null, BH-FDR q=0.20, dynamic simulation floor, persistent ledger), extended
with the additions below that baseline runs surfaced as necessary. No separate pre-mining phase —
these run inline, as part of Step 1 (generation) and Step 2 (admission).

Listing-date verification (was Phase 0.3) is confirmed done — all ETF date ranges in
`select_features.py`/`evaluate_concept.py` are trade-history-verified, not assumed. No open item here.

---

## Step 1 — Candidate Generation (messy zone, agents + human OK)

### 1a. Document mining
Source: repo of 1000+ trading ideas, AL Brooks book (already downloaded). Agents translate
written setups into candidate formulas against existing feature/price primitives. Human review of
translated formulas before they enter Step 2 (sanity check units, lookback windows, no
forward-looking references).

### 1b. Programmatic combination — gated by pool-size loop
Before generating combos for a given ETF/side, check current admitted pool size against a floor
(suggest ≥3). Loop logic per batch:
```
for etf, side in all_combos:
    pool = load_admitted_pool(etf, side)
    if len(pool) >= MIN_POOL_TO_COMBINE:
        generate_combos(pool)   # all ops below
    else:
        skip combo-generation for this etf/side this round
        (1a document-mining and single-feature mining still allowed)
```
This makes 0.2 self-enforcing every batch rather than a one-time gate — as the pool grows from
admissions, combo-generation switches on automatically for that ETF/side, no manual re-check needed.

#### 2-Way Combo Types (11 ops)

| Op | Formula | Rationale |
|----|---------|-----------|
| `min` | min(A, B) | Conservative consensus |
| `max` | max(A, B) | At-least-one-strong |
| `diff` | A - B | Directional divergence |
| `ratio` | A / |B| | Scale-normalized (B must be vol/volume-type) |
| `ifelse` | IfElse(regime_cond, A, B) | Regime-conditioned switching |
| `mean` | (A + B) / 2 | Smoothed consensus signal |
| `product` | A * B | Interaction/amplification term |
| `abs_diff` | |A - B| | Divergence magnitude (direction-agnostic) |
| `rank_min` | min(rank(A), rank(B)) | Non-parametric consensus |
| `rank_max` | max(rank(A), rank(B)) | Non-parametric at-least-one-strong |
| `clamp_diff` | clip(A - B, -2, 2) | Bounded difference, outlier-resistant |

- Correlation sweet-spot: **[0.15, 0.85]** — pairs outside this range are skipped.
- Top-K default: **50** features (by absolute tail-IC on train set).
- `ratio` only generated when denominator is a vol/volume/scaling feature.
- `ifelse` uses regime features (vol20, vix, gap_pct, etc.) as condition, non-regime as actions.

#### 3-Way Combo Types (5 ops)

| Op | Formula | Rationale |
|----|---------|-----------|
| `tri_mean` | (A + B + C) / 3 | 3-signal consensus |
| `tri_min` | min(A, B, C) | All-agree-strong |
| `tri_max` | max(A, B, C) | At-least-one-strong |
| `tri_median` | median(A, B, C) | Robust central tendency |
| `tri_ifelse` | IfElse(cond1, A, IfElse(cond2, B, C)) | Nested regime branching |

- Correlation sweet-spot: **[0.10, 0.90]** (relaxed vs 2-way to allow broader exploration).
- Additional filter: skip triple if any pair has corr > 0.90 (redundant pair within triple).
- Top-K default: **25** features — C(25,3) = 2300 triples x 4 ops = ~9200 candidates max (plus tri_ifelse).
- `tri_ifelse` picks 2 regime conditions + 3 action features from the top-K_3 pool.

#### CLI Usage
```bash
# Default: 2-way + 3-way (aggressive mode)
python mining/generate_combos.py -e 300ETF -s single

# 2-way only (skip 3-way combos)
python mining/generate_combos.py -e 300ETF -s single --two-only

# Custom top-K for broader search
python mining/generate_combos.py -e 300ETF -s single -k 60 --top-k-3 30

# Regenerate everything (ignore mining log dedup)
python mining/generate_combos.py -e 300ETF -s single --no-dedup
```

Only generate combos within an ETF/side's own pool. Don't cross-pollinate across ETFs — different
listing histories, different regimes, keep it clean.

### 1c. Forbidden-directions memory
Maintain `mining_memory_{ETF}_{side}.json`: feature families that repeatedly land in
`REJECTED_REDUNDANCY` (e.g. VWAP-deviation variants, `yesterday_*` timing variants once one is in
pool). Agents check this before proposing new formulas in the same family — don't re-mine the same
signal in new algebra.

### 1d. Mining progress log (dedup guarantee)
`mining/mining_log.json` is the single source of truth for what has been generated and evaluated.

**Structure:**
- `generated_space.{ETF}_{side}`: ops used, top-K values, total generated count, SHA-256 hash of
  candidate names, full list of candidate names ever generated.
- `batches[]`: per-batch summary appended by `select_features.py` after each evaluation run —
  batch_id, ETF/side, timestamp, candidate count, admitted/rejected breakdowns, admitted names.

**Dedup logic:** On each `generate_combos.py` run, previously generated candidate names are loaded
from the log and excluded from output. Re-running with expanded ops only emits the *delta* (new
ops / new triples), never the same candidates twice. Use `--no-dedup` to override.

This eliminates redundant digging: any agent or human can check `mining_log.json` to see exactly
what combination space has been explored and what the results were.

---

## Step 2 — Admission

Candidate volume from Step 1 can run into the thousands. Order matters: cheapest, highest-rejection
filters run first so compute isn't wasted running block-permutation simulation + BH-FDR on candidates
that were always going to fail. Every candidate, in order:

1. **Rolling tail-IC pre-filter** (A3) — monotonicity/IC_IR thresholds, side-aware. Cheap, thins the
   herd first, not a final filter.

2. **7-Year Jackknife sign stability — universal cheap block, runs before any simulation.** Split training
   data into 7 equal chunks, compute tail IC per chunk, lock sign from full sample, reject if flip_count > 1
   or recent 2 chunks flip. This is a very cheap check (no resampling) and catches features whose in-sample
   IC is real-looking but internally unstable. Running this *before* the null-simulation step keeps a 10,000+ candidate
   flood from reaching the expensive stage at all. Applies to every ETF/side.

3. **Empirical null via block-permutation** — shuffle `y_train` in blocks of 10, pair with real
   (resampled) `x`, generate tail-IC null distribution per ETF/side. Only candidates that survived
   1-2 reach this.

4. **BH-FDR filter at q=0.20** against that null — reject before correlation check, so noise doesn't
   get a chance to displace a real feature via the replacement rule.

5. **Dynamic simulation-based admission floor** (95th percentile of multi-trial null, N = current
   ledger count) — final bar a surviving candidate's deflated IC must clear.

6. **Correlation gate + replacement rule** (A2, θ=0.5, replacement if new IC≥0.10 and ≥1.3×old and
   corr>θ with exactly one pool member).

7. **Ledger update** — every attempt (admitted or not) logged, N persists across batches, seeded
   from prior `mining_attempts_*.json` runs.

Nothing here changes the underlying thresholds from the original 221-feature baseline — same
pipeline, reordered so the cheap universal filter (step 2) protects the expensive ones (steps 3-5)
from flood volume.

---

## Step 3 — Batch Cadence

- Run Step 1 in batches (suggest 50-100 candidates at a time, mixed 1a/1b), not one giant dump —
  keeps ledger/N growth traceable.
- After each batch: re-run `evaluate_concept.py` on the updated pool, compare OOS/lockbox CI vs.
  the pre-batch baseline. Only keep the batch's admissions if the comparison is CI-robust, not just
  "pool got bigger."
- Stop condition per ETF/side: N batches with no net admissions, or pool hits a size where VIF
  safety net starts triggering regularly (diminishing returns / redundancy exhausted).

---

## Step 4 — Model (unchanged from v3 baseline)

IC-weighted (deflated-IC-weighted) linear sum, light VIF pass. No selection logic moves into this
stage — Step 2 already did all of it. If mining meaningfully grows the pools (1b threshold met),
reassess whether weighted-sum is still sufficient (per v3 plan.md §B4 escalation rule) — but don't
preemptively complicate the model in anticipation of that.

---

## Checklist
- [x] Implement 7-year jackknife sign stability as Step 2.2 (universal, pre-simulation).
- [ ] Implement pool-size loop gating combo-generation (1b) per batch.
- [ ] Confirm ledger seeding covers all historical `mining_attempts_*.json` before batch 1.
- [ ] Stand up `mining_memory_{ETF}_{side}.json` forbidden-directions tracking.
- [ ] Run batch 1 (50-100 candidates, mixed sources) across all ETFs — 588000ETF included, now
      protected by the universal 7-year jackknife gate rather than excluded.
- [ ] Compare post-batch OOS/lockbox CI vs. current baseline before accepting the batch.
- [x] Expand 2-way ops from 5 to 11 (added mean, product, abs_diff, rank_min, rank_max, clamp_diff).
- [x] Add 3-way combo generation (tri_mean, tri_min, tri_max, tri_median, tri_ifelse).
- [x] Implement mining_log.json dedup — no combination space explored twice.
- [x] Integrate batch summary logging into select_features.py.
- [x] Set aggressive defaults: top-50 (2-way), top-25 (3-way), 3-way enabled by default.
- [ ] Run aggressive mining across all 5 ETFs x 3 sides.