# Day-Model Rewrite v3 — Plan

## Why v1/v2 died (context, don't repeat)
- v1: way too complex. Don't try to read it 
- v2 (`day-model/day-model_plan.md`): elaborate model-side machinery (Huber+MCP manifold, CSS+VIF, HMM regimes, vol gating) worked numerically (condition numbers, ESS all fixed) but the *headline* Sharpe-objective search came back statistically indistinguishable from baseline once block-bootstrap CI was applied (§8.6 of that doc). Lesson: fancy model-side optimization can look good pre-CI and be noise post-CI.
- Core decision for v3: **move weak/joint-signal capture to the feature-mining stage. Keep model training dumb and hard to overfit.** Mining can be messy, agentic, human-in-the-loop. Model stage cannot.

---

## Stage A — Feature Mining (messy zone, agents + human OK)

Goal: produce a pool of features/combos, each with a defensible standalone IC, low redundancy with the rest of the pool, and no exploding trial-count debt.

### A1. Sources
1. Existing survivor list (already pruned 317→210, keep as base).
2. Mine repo of 1000+ trading ideas / AL Brooks book (already downloaded) → candidate formulas.
3. Combine existing features: `min(A,B)`, `max(A,B)`, `IfElse(regime_cond, A, B)`, ratio/diff combos etc.

### A2. Admission gate (per candidate, run at mining time, not after)
Based on FactorMiner (Wang et al. 2026, arXiv:2602.14670) admission protocol:
```
admit(candidate) iff:
  rolling_IC(candidate) >= tau_IC          # e.g. 0.03-0.04, tune per ETF
  AND max_corr(candidate, current_pool) < theta   # e.g. 0.5
```
Replacement rule (lets a better candidate bump a redundant old one instead of just getting rejected):
```
if IC(new) >= 0.10 and IC(new) >= 1.3 * IC(old)
   and exactly one existing pool member g has corr(new, g) > theta:
     replace g with new
```
Notes:
- Don't orthogonalize the pool (Gram-Schmidt tested worse than plain IC-weighted / equal-weight in the same paper — correlated features carry noise-cancelling info, don't throw it away).
- Complexity penalty = the correlation gate itself, not a separate fudge factor. A combo only survives if it's *both* predictive *and* not a repackaging of something already in the pool. That's a real anti-overfit constraint, not a vague "soft penalize complexity."

### A3. Rolling guard (pre-filter only — do NOT use as sole/final filter)
- 90-calendar-date rolling tail IC: drop if monotonicity < 70-90% or IC_IR < 0.3.
- **Lesson from v2** (its own pipeline note): pure univariate/marginal screening was ripped out of v2 because it kills features with weak solo signal but strong joint value. Same trap applies here if this guard is the only gate — use it to thin the herd before the correlation-gate above, never as the final word.

### A4. Trial-count / selection-bias tracking (new, was missing in v1/v2 — this is what actually burned v2's Sharpe-objective result)
- Every combo *attempted* (admitted or not) gets logged: formula, IC, ICIR, max_corr, verdict.
- Maintain running trial count `N`. Before anything from this batch reaches Stage B, compute a **deflated IC** (Bailey & López de Prado 2014, Deflated Sharpe Ratio methodology, adapted to IC) using `N` and the IC distribution across trials. Raw best-of-N IC is optimistic; deflated IC is the number that matters.
- Keep a memory file of "forbidden directions" — feature families that reliably end up correlated with the existing pool (e.g. v2 already knows VWAP-deviation variants are a dense cluster) so agents/humans stop rediscovering the same signal in new algebra.

### A5. Output
`feature-mining.md` — final pool with: formula, standalone IC, ICIR, max_corr to nearest pool neighbor, deflated IC, source (hand-picked / mined / combo).

---

## Stage B — Model Training (must be simple, must resist overfit)

**No feature selection happens here.** Selection already happened in Stage A via the admission gate. Model stage only combines what survived.

### B1. Baseline model: IC-weighted linear sum
```
signal = sum_i( sign(IC_i) * |IC_i|^k * z(feature_i) )
```
- `k` optional mild tilt toward higher-IC features (k=1 default = plain IC-weighting, don't overfit this exponent — if tuned, tune on inner validation blocks only, same chronological split discipline as v2 §Step 0).
- This is deliberately close to FactorMiner's IC-weighted combination result, which beat learned selection (Lasso/XGBoost) on their best (low-redundancy) library — because Stage A's correlation gate is doing the redundancy-control job that Lasso/XGBoost would otherwise be needed for.

### B2. Light sanity check only (not a selection step)
- One VIF pass on the final pool, drop only if VIF > 12 (rare if A2's correlation gate worked). This is a safety net, not a selection mechanism.

### B3. Guardrails carried over from v2 (proven, keep as-is)
- Chronological split: selection train / inner validation (tuned) / outer validation (untouched holdout) / OOS lockbox — reuse v2's exact block structure (`Step 0` in `day-model_plan.md`), don't rebuild.
- Report OOS metrics via block-bootstrap CI (v2's `generate_report.py` machinery), not raw point estimates. A result only counts if the CI excludes zero — this is the check that caught v2's false-positive Sharpe objective.
- Kill switches stay two-sided: Overall IC > 0, Hit Rate ≥ 60%, Monotonicity ≥ 0.25, Spread > 0.

### B4. Escalation rule
Only reach for anything more complex than the weighted sum (e.g. ElasticNet/MCP on the Stage-A pool) if it beats the weighted-sum baseline by a margin that survives the block-bootstrap CI. Default assumption: it won't need to, if Stage A did its job.

---

## Checklist
- [ ] Build admission-gate mining harness (A2) — IC threshold + max-corr + replacement rule.
- [ ] Add trial-count logging + deflated-IC calc (A4) before anything leaves Stage A.
- [ ] Port v2's chronological split + block-bootstrap CI report code as-is for Stage B eval.
- [ ] Run Stage A on existing 210-feature pool first (no new mining yet) → get IC-weighted baseline OOS number. This is the new benchmark to beat.
- [ ] Write `feature-mining.md`, hand to mining agents (repo of 1000+ ideas, AL Brooks book) with the A2/A3/A4 rules baked in.
- [ ] Re-run Stage A admission + Stage B weighted-sum on old+mined pool, compare vs baseline via CI, not raw IC.
- [ ] Only then consider B4 escalation.

## References
- Wang et al. 2026, *FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery*, arXiv:2602.14670 — admission gate, replacement rule, IC-weighted vs orthogonal vs learned-selection comparison.
- Bailey & López de Prado 2014, *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*, Journal of Portfolio Management 40(5) — deflate IC/Sharpe by trial count.
- `day-model_plan.md` (this repo, v2) — chronological split design, CSS+VIF mechanics, block-bootstrap CI reporting, all reused as-is where noted above.
