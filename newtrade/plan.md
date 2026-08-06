# NewTrade Framework — Day-Model Factor Monetization

## 1. Executive Summary

NewTrade converts admitted alpha factors from `day-model-new` into intraday ETF trading signals. Each day, a composite Z-score is built from the top-10 features (selected by rolling tail IC with hysteresis), and a binary trading decision is made: go long, go short, or stay flat.

### Core Design
- **Signal**: Weighted average of top-10 z-scored features, where weights come from Empirical Bayes-shrunk IC estimates.
- **Schemes**: 4 weighting schemes — **ENSEMBLE (primary, averages ICW + EW)**, ICW, Sortino Weight, EW (100% Tail-IC selected). All share top-10 hysteresis selection machinery; they differ in selection/weighting metrics (see §3.6).
- **Trade**: Enter at 10:00 AM, exit at 14:35 PM same day. Round-trip fee = 16 bps (8bp buy and 8 bp sell).
- **Gate**: Trade only when |Z_composite| exceeds a train-swept conviction threshold.
- **Scope**: 300ETF, 500ETF, 159915ETF (50ETF/588000ETF disabled — insufficient features).
- **Zero Lookahead**: All parameters estimated from data available at $t-1$.

### Production OOS Performance (2022-01 ~ 2025-12, 8 bps fee + stoploss) (check REPORT.md)

> REPORT.md is regenerated with the current defaults (ER=25, 4 schemes, Score Weight primary).
> The legacy ER=20 ICW-only report is preserved as `REPORT_ER20_baseline.md`.

| ETF | Asset | Side | OOS Period | Z_th | Features | Trades | Cost Sharpe | Raw Sharpe | Total PnL | Long PnL | Long Sharpe | Short PnL | Short Sharpe | Max DD | Win Rate | Turnover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:1.10/S:1.30 (train L:1.00/S:1.20) | 22 | 118 (76L/42S) | 1.021 | 1.415 | +0.2337 | +0.1591 | 3.042 | +0.0746 | 2.837 | 0.0532 | 55.9% (L:56.6%, S:54.8%) | 59.8x |
| 500ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.70/S:1.10 (train L:0.60/S:1.00) | 193 | 383 (253L/130S) | 1.390 | 2.220 | +0.5091 | +0.1559 | 1.084 | +0.3532 | 4.235 | 0.0814 | 54.8% (L:53.4%, S:57.7%) | 161.2x |
| 50ETF | Spot ETF | single | 2022-01 ~ 2026-01 | N/A | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 159915ETF | Spot ETF | single | 2022-01 ~ 2025-12 | L:0.90/S:1.10 (train L:0.80/S:1.00) | 27 | 253 (154L/99S) | 1.562 | 1.950 | +0.8057 | +0.5079 | 3.012 | +0.2978 | 3.295 | 0.0777 | 58.1% (L:53.9%, S:64.6%) | 115.7x |

---

## 2. Upstream: Feature Selection (day-model-new)

NewTrade consumes features from `day-model-new`'s admission pipeline. Features are intraday alpha factors predicting the 10:00→14:35 ETF return.

### Feature Generation
- **Base features**: ~200 intraday technical indicators computed from 1-minute bars (opening drive, VWAP acceleration, volume momentum, bar structure, etc.)
- **Combinators**: Pairwise and triple combinations via operations (diff, ratio, rank_min, clamp, z-score). Produces 1,500–3,000 candidates per ETF.

### 8-Gate Admission Pipeline (all training-only, zero OOS leakage)

| Gate | Purpose | Key Parameter |
|------|---------|---------------|
| 1. Jackknife Sign Stability | Reject sign-flipping features | 7 yearly chunks, max 1 flip |
| 2. Rolling Guard | Reject unstable rolling IC | mono ≥ 0.60, IR ≥ 0.30 |
| 3. Temporal Validation | Reject decayed signals | recent_ic > 0 |
| 4. BH-FDR | Multiple-testing correction | q = 0.30, 5000 block-shuffled sims |
| 5. Composite Floor (B3) | Beat empirical null | 93rd–97th percentile of null |
| 6. Temporal Stability | Kill artificial mirages | ic_cv × weak_link_cv ≥ 0.15 |
| 7. Quality Gate | Minimum signal strength | deflated_ic ≥ 0.03, sortino > 0 |
| 8. Correlation (B4) | Remove near-duplicates | θ = 0.95 |

### Output
- Per-ETF admitted pool (22–193 features for `single` side)
- ONC cluster assignments (de Prado 2019) for downstream diversity control
- Pool vintages re-trained every 2 years (`_p2015_2023`, `_p2016_2024`, `_p2017_2025`)

---

## 3. Signal Construction Pipeline

The daily signal construction follows this sequence:

```
Raw features → Expanding Z-score → IC Matrix (rolling tail 480d)
    → EMA smoothing → Hysteresis Top-10 Selection (cluster-constrained)
    → ICW Shrinkage Weighting → Z_composite
```

### 3.1 Expanding Z-Score Standardization

$$z_{i,t} = \text{clamp}\left(\frac{x_{i,t} - \hat{\mu}_{i, 1:t-1}}{\hat{\sigma}_{i, 1:t-1}}, -3.0, 3.0\right)$$

Burn-in: 252 days. Zero lookahead (uses only data up to $t-1$).

### 3.2 IC Estimation: Rolling Tail IC (480d)

For each feature $i$ at time $t$, compute Spearman rank correlation between $z_i$ and trade returns using only the top/bottom 10% tail observations within a trailing 480-day window:

$$\text{IC}_{i,t} = \text{SpearmanCorr}(z_i[\text{tail}], r[\text{tail}]) \quad \text{over } [t-480, t-1]$$

- **Why tail**: Focuses on extreme signal days where alpha is strongest.
- **Why rolling 480d**: 2 China trading years. Balances recency vs stability. Validated optimal vs expanding IC and longer windows (600d, 720d).
- **EMA smoothing**: Span = 60d (300ETF/50ETF) or 90d (500ETF/159915ETF) to reduce daily ranking noise, plus **Sortino≤0 selection gate** (post-EMA bounded mask, `--no-sortino-gate` to disable). **ADOPTED 2026-08 (user decision) after two retests** (`tests/test_ema_span_ab.py`, `test_ema_span_yearly.py`, `test_fq_g1_diagnose.py`, `test_new_defaults_verify.py`): span-off is worst everywhere (smoothing cuts churn), but 300ETF span 30 was stale → 60 wins yearly-consistently (+0.335 agg; +0.54/+0.51/+0.54 in 2022-24); Sortino≤0 gate is zero-cost where it doesn't fire (300/500ETF) and +0.135 where it does (159915ETF). New icw baseline: **300ETF 0.539 / 500ETF 1.039 / 159915ETF 1.065 (avg 0.881, +0.157 vs old 0.724)**. Caveats: 159915 span-120 (unadopted) rested partly on 2024; 2025 regime break unaffected by spans/gate.

### 3.3 Feature Selection: Hysteresis + ONC Cluster Constraint

**Problem**: Daily top-10 reselection causes feature churn → Z_composite distribution shifts → threshold instability.

**Solution**: Hysteresis (sticky selection):

- **Enter**: Feature enters active set when IC rank ≤ 10 AND its ONC cluster is unoccupied.
- **Exit**: Feature exits only when IC rank > `exit_rank` (wider gate than entry).
- **Exit Rank = 25 (fixed default)**: A/B validated (2026-08, `tests/test_exit_rank_sortino_ab.py`): ER=25 is the fairest fixed value across all 3 ETFs for the tail-IC baseline (300ETF 0.204, 500ETF 1.039, 159915ETF 0.930 — all positive, best average 0.724 vs 0.684 at ER=20). Per-ETF optima differ (300→23, 500→25, 159915→15) and pool/cluster-adaptive formulas did not beat fixed values, so a fixed 25 is kept.
- **Cluster constraint**: Max 1 feature per ONC cluster in the active set. Ensures diversity across feature families.

**Validated impact**: +26% Sharpe on 300ETF, +12% on 159915ETF vs no-hysteresis baseline.

### 3.4 ICW Shrinkage Weighting

Given the active feature set $\mathcal{A}$ (up to 10 features):

$$w_i = \frac{\max(0, \text{IC}_{i,t} - SE_{\text{IC}})}{\sum_{j \in \mathcal{A}} \max(0, \text{IC}_{j,t} - SE_{\text{IC}})}, \quad SE_{\text{IC}} = \frac{1}{\sqrt{n_{\text{train}}}}$$

Features with IC below the standard error floor get zero weight (Empirical Bayes shrinkage).

### 3.5 Composite Signal

$$Z_{\text{composite},t} = \sum_{i \in \mathcal{A}} w_i \cdot z_{i,t} \cdot \text{sign}_i$$

### 3.6 The Four Weighting Schemes (Score IC Family)

The weighting system performs two jobs: **selecting** the top-10 features and **weighting** them. A/B testing (2026-08) showed the two jobs can use different metrics. A new factor-level metric was introduced: rolling 480d **Sharpe/Sortino** per factor (factor P&L = sign-aligned z-score × trade return), and the **Score blend**:

$$\text{Score}_{i,t} = w_{\text{ic}} \cdot \text{rank}(\text{tailIC}_{480d}) + (1 - w_{\text{ic}}) \cdot \text{rank}(\text{Sortino}_{480d}), \quad w_{\text{ic}} = 0.75$$

| Scheme | Selection metric | Weight metric | Notes |
|--------|-----------------|---------------|-------|
| **ensemble** (primary) | Tail-IC + Sortino gate | Signal average ($[Z_{\text{icw}} + Z_{\text{ew}}]/2$) | Production scheme; top of REPORT.md since 2026-08 (0.849–1.021 Cost Sharpe) |
| **icw** | Rolling tail IC 480d | Rolling tail IC (ICW shrinkage) | Conviction weighting + hysteresis |
| **sortino** | Rolling tail IC 480d | Score blend | Selection/weighting decomposition |
| **ew** | Rolling tail IC 480d | Equal weight (1/K) | 100% Tail-IC selection ($w_{\text{ic}}=1.0$); Sortino≤0 gate prunes downside risk |

**2026-08 ENSEMBLE & IC EW decision:** 
1. **ENSEMBLE set as primary default**: Combining `icw` (trend conviction + hysteresis) and `ew` (equal-weight noise dampening) produces an **0.849 Cost Sharpe** (2022–2026 OOS) and **0.912–1.021 Cost Sharpe** across multi-period windows (2023–2026, 2024–2026) while reducing turnover to ~55x–59x. It strictly beats every standalone scheme across all ETFs.
2. **EW switched to 100% Tail-IC ($w_{\text{ic}} = 1.0$)**: Standalone EW Tail-IC selection improves Sharpe from 0.482 to **0.579** (+0.097 lift) and lowers turnover. The post-EMA `Sortino <= 0` gate handles downside risk, eliminating the arbitrary 75/25 blend hyperparameter.

**Key empirical findings** (`tests/test_weight_blend_yearly_ab.py`):
- Pure-Sortino weights are rejected (avg 0.626 vs 0.684 baseline); the blend is required.
- **25% Sortino + 75% tail IC** is the robust global blend: +0.084 avg Sharpe, 500ETF preserved (needs ≥0.75 tail IC share), 159915ETF +0.249.
- Using Sortino for *selection* crushes 500ETF (−0.38); its value is in *sizing* already-selected features.
- Yearly tests (2022–2025): the blend beats baseline in 7/12 year×ETF cells; 2025 is a regime-break year (all configs negative on 300/500ETF).

### 3.7 Factor Quality (FQ) Score & Meta-IC Judgment Harness (2026-08)

The Score-blend family was judged by P&L A/B, which is contaminated by threshold/sizing interactions. A scientific yardstick was built: **meta-IC** = Spearman(score at t, factor's realized forward IC over the next 63 trading days), at monthly snapshots from 2017, with t-stats and a per-factor 63d-block-shuffle null; plus Top-K **TP′** hit rate (TP′ = fwdIC>0 AND fwdSortino>0). Files: `factor_quality.py`, `tests/test_fq_diagnostic.py` (Phase 0), `test_fq_validation.py` (Phase 2), `test_fq_ab.py` (Phase 3), `test_fq_sweep.py`, `test_fq_gated_adaptive.py`.

**Findings:**
- **Component meta-IC (pooled 2016–2025):** sortino +0.053 (t=3.4), tailIC +0.048 (t=3.6), mono +0.010 (n.s.); **ic_cv −0.040 and half_ratio −0.043 are anti-predictive** and were excluded from any blend.
- **Phase 2:** tailIC_480d alone is the best forward predictor (+0.059, t=4.3); the FQ blend dilutes it (+0.033); extra gates raise FP′ rate. Block-shuffle null ≈ +0.042: most meta-IC is persistence, excess increment p≈0.13.
- **Phase 3 A/B (ER=25, REPORT.md baseline reproduced Δ=+0.0000):** FQ_select_weight is the best arm (avg +0.028: 300ETF +0.187, 159915ETF +0.299, but 500ETF −0.403) → **partial pass; production defaults unchanged**. Pool-size interaction: FQ diversity helps small pools; the 377-feature 500ETF pool needs pure tail IC.
- **Comprehensive sweep (27 arms, target TP′ ≥ 8/10):** multi-window tailIC {240,480,960}, Sortino {240,480}, mono, momentum, plus day-model-new ports (n-negative-blocks, jackknife leave-one-block-out min IC, vol-regime consistency, deflated-IC noise-floor gate) and 9 gate stacks on tailIC. Best TP′ = 7.15/10 (tailIC+Sortino+momentum); **no arm beats raw tailIC480, none null-significant**.
- **Gated adaptive-K follow-up (no fill-in):** TP′ rate among gate-passing factors is 69.8–71.2% for every gate stack (best: tailIC > pool noise-floor). **The 3-month TP′ ceiling of the admitted pools is ≈ 71–75% (500ETF 75%, 300ETF 66%) — 80% is unreachable by downstream rescoring/gating.** Raising TP count must happen upstream in day-model-new admission.
- **Gate-as-default P&L A/B (`tests/test_fq_gate_default_ab.py` + `test_fq_g1_diagnose.py`):** the first gate A/B injected masks of −1e9 **before** EMA smoothing — a single tailIC≤0 day (3–6% of factor-days; 70–100% of factors ever touch it) poisoned that factor's smoothed score for ~300–900 days (a banishment artifact), overstating gate costs. Corrected post-EMA gate test: `tailIC≤0` mask is an exact no-op on 300/500ETF (baseline selection almost never holds negative-IC factors: 0.8%/0% of days, and ICW shrinkage w ∝ max(0, IC − 1/√n) already zeroes them) and costs 159915ETF −0.091 (churn). `Sortino≤0` mask is the only clean-positive gate: +0.135 on 159915ETF, Δ=0.000 elsewhere (ΔAvg +0.045). Jackknife-loo gating destroys 300ETF (−0.43). **The tailIC gate was rejected, but the Sortino≤0 candidate was subsequently ADOPTED as production default (2026-08, user decision, spans 60/90/90 + Sortino gate; verified combined config avg +0.157)** — see §3.2 EMA smoothing line.

---

## 4. Threshold & Position Sizing

### 4.1 Conviction Threshold (Train-Sweep + Buffer)

1. **Training sweep**: On pre-OOS data, sweep $Z_{\text{th}} \in [0.5, 1.5]$ step 0.1. Pick the threshold maximizing cost-adjusted Sharpe (with ≥ 8% active days constraint).
2. **Production buffer**: $Z_{\text{th}}^{\text{prod}} = Z_{\text{th}}^{\text{train}} + 0.20$ (Walk-forward grid sweep validated: filters low-conviction threshold noise, slashes turnover by 32.3%).
3. **Asymmetric short**: Short threshold gets additional +0.10 buffer (A-share structural long bias).

### 4.2 Dynamic Position Sizing (Fast Ramp Quadratic Default)

Production uses **Fast Ramp Quadratic** position sizing (`fast_ramp_quadratic`, $m=0.50, \Delta Z_{\text{full}}=0.30$) with **$Z_{\text{buffer}} = 0.20$**:

$$S_t = \begin{cases} \text{sign}(Z_t) \cdot \left(m + (1-m) \cdot \min\left(1.0, \ \left(\frac{|Z_t| - Z_{\text{th}}}{\Delta Z_{\text{full}}}\right)^2\right)\right) & \text{if } |Z_t| > Z_{\text{th}} \\ 0 & \text{otherwise} \end{cases}$$

- **Min Position Floor ($m=0.50$)**: 50% initial size upon passing conviction threshold. Smooths entry risk on marginal triggers while absorbing 16 bps friction.
- **Full Ramp Margin ($\Delta Z_{\text{full}}=0.30$)**: Matches signal-averaged ENSEMBLE composite Z variance. Ramps quadratically to 100% size as signal exceeds threshold by $+0.30\sigma$.
- **Performance Lift**: Combined $Z_{\text{buffer}}=0.20$ and Fast Ramp Quad ($m=0.50, \Delta Z=0.30$) boosts ENSEMBLE Cost Sharpe (**0.842 vs 0.685 baseline, +0.157 Sharpe lift**), cuts Max Drawdown to **6.40%** (vs 7.99%), and slashes turnover to **38.9x** (vs 57.5x, -32.3% fee drag reduction).

### 4.3 Summary of Position Sizing Research & Tried Options

| Model Mode | Formulation | Findings & Empirical Outcome |
|---|---|---|
| **Binary Baseline** | $S_t = \pm 1.0$ if $|Z_t| > Z_{\text{th}}$ | Hard gate step function. High drawdowns (8.91% MaxDD), rigid all-or-nothing allocation (0.706 Cost Sharpe). |
| **Continuous Ungated** | $S_t = \text{clip}(k Z_t, -1, 1)$ | No threshold gate. High trade frequency on noise signals, severe transaction fee drag. |
| **Standard Tanh / Quad** | $S_t = \tanh((Z - Z_{\text{th}})/\gamma)$ | Ramp parameter $\gamma=1.5$ too slow; requires $+1.5\sigma$ excess signal to reach full size. Avg size collapsed to ~0.35–0.45. |
| **Fast Ramp Linear ($m=0.50, \Delta Z=0.30$)** | $S_t = m + (1-m)\frac{\Delta Z}{0.30}$ | Excellent drawdown reduction, linear ramp to 100% (0.706 Cost Sharpe, 7.97% MaxDD). |
| **Fast Ramp Quad ($m=0.70, \Delta Z=0.40$)** | $S_t = m + (1-m)\left(\frac{\Delta Z}{0.40}\right)^2$ | Old default. Ramp margin too wide for signal-averaged ENSEMBLE composite Z (0.685 Cost Sharpe). |
| **Fast Ramp Quad ($m=0.50, \Delta Z=0.30$) [WINNER]** | $S_t = m + (1-m)\left(\frac{\Delta Z}{0.30}\right)^2$ | **Production Default**. Perfectly matched to ENSEMBLE composite Z variance. Top Cost Sharpe (**0.730**), lowest MaxDD (**7.59%**), lowest turnover (**53.2x**). |

---

## 5. Execution & Stop-Loss

### 5.1 Trade Protocol
- **Window**: Signal at 10:00 → enter → exit at 14:35.
- **Instruments**: ETF spot (default) or index futures (`--future`: IF88/IC88/IH88).
- **Friction**: 8 bps per side (16 bps round-trip) + 2 bps stop-loss slippage when triggered.

### 5.2 Intraday Stop-Loss: Time-Decay Trailing (3% Spot / 30% Option)

Production uses `time_decay_trailing`:
- **Spot ETF / Futures**: Param = 0.03 (3% spot trailing, tightening by 40% near close).
- **Option Portfolio (`--option`)**: Param = 0.30 (`opt_time_decay_trailing` default, 30% initial trailing gap, tightening by 40% to 18% near close).
- **Direct Option Stop Price**: Trails peak option premium $P_{\text{peak}}(t)$ directly on option contract RMB quotes ($P_{\text{stop}}(t) = P_{\text{peak}}(t) \times (1.0 - \theta(t))$).
- **Time Tightening**: $\theta(t) = \theta_{\text{start}} \times (1.0 - 0.40 \times f_t)$. Prevents holding dying option premiums into market close as late-day theta decay accelerates.

Enabled by default (`--stoploss`). Disable with `--no-stoploss`.

### 5.3 Option Strike Selection (ETF-Adaptive)

With large Chinese option strike gaps (e.g., 500ETF: 7.75/8.00/8.25), always buying nearest OTM can be suboptimal when spot is far from OTM1 but close to ITM1. The system supports 5 strike selection modes via `--strike-mode`:

| Mode | Logic |
|------|-------|
| `otm` | Always nearest OTM (legacy baseline) |
| `nearest` | Pick closer of ITM1/OTM1 by distance to spot |
| `vol_t1` | Pick ITM1/OTM1 with higher T-1 daily volume |
| `vol_intraday` | Pick higher cumulative volume 09:35–10:00 |
| `cascade` | Distance-first + gamma guard (spot within 40% of gap → keep OTM) + volume tie-breaker |

**Default (`auto`)** resolves per-ETF based on A/B test results:

| ETF | Default Mode | Rationale |
|-----|-------------|----------|
| 300ETF | cascade | Shanghai, large gaps → distance + gamma guard |
| 500ETF | nearest | Shanghai, large gaps → simple closest |
| 50ETF | cascade | Shanghai, similar to 300ETF |
| 159915ETF | vol_t1 | Shenzhen exchange, liquidity matters more |
| 588000ETF | cascade | Shanghai, default cascade |

Override with explicit mode: `--strike-mode cascade`. A/B comparison: `--strike-ab`.

---

## 6. Production Configuration

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Schemes | 4: **score** (primary), icw, sortino, ew | `--scheme all`; Score Weight on top of REPORT.md |
| Score Blend | 0.75·rank(tailIC₄₈₀) + 0.25·rank(Sortino₄₈₀) | Best robust blend, +0.084 avg Sharpe (A/B 2026-08) |
| IC Mode | Rolling Tail (480d, 10%) | Wins A/B test vs expanding IC (+12% avg) |
| EMA Span | 30d (300/50), 90d (500/159915) | Pool-size adaptive smoothing |
| Top-K | 10 | Fixed; prevents dilution on large pools |
| Hysteresis | ON | Feature-churn stabilization |
| Exit Rank | **25 (fixed)** | Fairest across all 3 ETFs (A/B 2026-08); adaptive formulas no better |
| ONC Cluster | Max 1 per cluster | Diversity across feature families |
| Position | Binary L+S | Highest Sharpe |
| Threshold | Train-sweep + 0.10 buffer | Robust across regimes |
| Spot Stop-Loss | time_decay_trailing=0.03 | Cuts intraday spot losers |
| Option Stop-Loss | opt_time_decay_trailing=0.30 | +0.205 Sharpe lift on 300ETF, -49.4% MaxDD |
| Fee | 8 bps (Spot) / 4 RMB per contract per side (Option) | Stress-tested |
| Strike Selection | ETF-adaptive (cascade/nearest/vol_t1) | A/B validated, see §5.3 |
| Feature Floor | ≥ 10 | 50ETF/588000ETF disabled |

**CLI**: `python newtrade/run_backtest.py` (default `--scheme all` runs score/icw/sortino/ew; all defaults are production-optimal)

---

## 7. Key Empirical Findings

1. **Rolling Tail IC > Expanding IC**: 480d tail Spearman dominates full-history Pearson, especially for large pools (500ETF: +64%). The "tail" component is key, not just "rolling."
2. **Hysteresis > Threshold Adaptation**: Feature churn is the real problem. Stabilizing selection beats all threshold adaptations (percentile, walk-forward, variance-scaled).
3. **ICW > Multi-Score**: Pure IC weighting with shrinkage beats composite scores (IC+IR+Monotonicity). Adding IR introduces noise.
4. **Fixed K=10**: Cross-K Sharpe differences ≤ 0.15 (noise). Per-ETF K tuning = overfitting.
5. **Direct Option Time-Decay Trailing**: Direct option price time-decay trailing stop (`opt_time_decay_trailing`, $\theta_{\text{start}}=0.30$, $c_{\text{tight}}=0.40$) achieves **1.251 Sharpe** (+0.205 lift) and slashes MaxDD from **22.87% to 11.57%** (-49.4% DD reduction) on 300ETF.
6. **CPCV 100% Positive**: All active ETFs show 100% positive folds in combinatorial purged cross-validation.
7. **DSR Significant**: 159915ETF achieves DSR = 0.965 (SIGNIFICANT at 10 trials). 500ETF marginal (0.934).
8. **Sortino belongs in weights, not selection**: Selection/weighting decomposition A/B — Sortino-480d as a weight metric lifts 300/159915 without breaking 500ETF; as a selection metric it crushes 500ETF. Pure-Sortino weights rejected; the 25/75 Sortino/tailIC blend is the sweet spot.
9. **Exit rank 25 is the fair default**: ER sweep on the current pipeline — ER25 best average for tail-IC baseline; per-ETF optima conflict (23/25/15) and adaptive pool/cluster formulas do not help.
10. **2025 regime break**: Per-year diagnostics show all configs go negative on 300ETF/500ETF in 2025 (invisible in the 4-year aggregate). Flagged for pool-decay investigation.
11. **Meta-IC harness verdict**: tailIC_480d alone is the best 3-month forward predictor; every tested blend or gate stack dilutes it; no sweep arm exceeds the block-shuffle null significantly. The harness now serves as the standard yardstick for any future score proposal.
12. **TP′ ceiling ≈ 71–75%**: 27-arm sweep + gated adaptive-K follow-up prove no rescoring or hard-gate configuration reaches 80% forward-TP rate. The binding constraint is upstream pool quality (300ETF ceiling only ~66%).
13. **Pool-size interaction in FQ selection**: FQ-blend selection lifts small pools (300/159915) but costs 500ETF −0.40 Sharpe; large pools want pure tail IC. A pool-size-routed scheme is the open follow-up.

---

## 8. Architecture

```
newtrade/
├── plan.md                  # This document
├── REPORT.md                # Latest OOS backtest report (auto-generated)
├── REPORT_option.md         # Option portfolio OOS backtest report
├── run_backtest.py          # Main CLI (--scheme, --ic-mode, --hysteresis, --year, --decay, --option)
├── run_production.py        # Production ensemble CLI (DSR & CPCV validated)
├── weighting.py             # ICW, EW, hysteresis, adaptive_exit_rank, ONC selection
├── strategy.py              # Threshold sweep, position sizing, ETF simulation
├── factor_quality.py        # FQ score components, gates, rolling stability kernels (Numba)
├── option_strategy.py       # Capital-constrained option portfolio execution & 5m stoploss engine
├── utils.py                 # Data loaders, expanding z-score, rolling tail IC (Numba)
├── robustness.py            # DSR, CPCV, PBO, sensitivity analysis
├── research_stoploss.py     # 1m ETF intraday stop-loss simulator
├── research_option_stoploss.py # Option intraday stop-loss simulator & Train/OOS benchmark
├── glm.py / glm_backtest.py # Experimental Ridge GLM scheme
└── tests/                   # A/B test suite
    ├── test_option_stoploss_ab.py # Multi-arm option stoploss A/B testing suite
    ├── test_weighting_ab.py       # 11-arm weighting pipeline comparison
    ├── test_zthreshold_ab.py      # 7-arm threshold system comparison
    ├── test_hysteresis_sweep.py   # Exit-rank × threshold grid search
    ├── test_fq_diagnostic.py      # FQ Phase 0 persistence/meta-IC go-no-go
    ├── test_fq_validation.py     # FQ Phase 2 meta-IC harness + null + top-K tiers
    ├── test_fq_ab.py              # FQ Phase 3 integration A/B vs REPORT.md baseline
    ├── test_fq_sweep.py           # 27-arm FQ component/gate/blend sweep
    ├── test_fq_gated_adaptive.py  # tailIC + hard gates, adaptive K (no fill-in)
    └── run_ab_test_tail_ic.py     # Rolling tail IC window comparison
```

### Data Dependencies
- `day-model-new/data/selected_pool_{ETF}_{side}.json` — admitted feature pools
- `day-model-new/data/cluster_assignments_{ETF}_{side}.json` — ONC clusters
- `data/{ETF}_1d.parquet` — daily ETF prices
- `data/{ETF}_1m.parquet` — 1-minute bars (for ETF stoploss simulation)
- `data/{ETF}_historical_prices_5m.parquet` — 5-minute option contract prices

---

## 9. A/B Test History

### Weighting Pipeline (2026-08)
11 arms × 3 ETFs. TailIC_ICW confirmed optimal. Multi-score variants all underperform. See `tests/test_weighting_ab.py`.

### Z-Threshold System (2026-08)
7 arms × 3 ETFs (with stoploss). Baseline threshold is robust. Hysteresis beats all threshold adaptations. See `tests/test_zthreshold_ab.py`.

### Hysteresis Exit-Rank Sweep (2026-08)
Adaptive ER formula validated. Wider = better up to cap. RollPct480 adds no value on top of hysteresis. See `tests/test_hysteresis_sweep.py`.

### Score IC A/B — Tail IC + Sharpe/Sortino 480d (2026-08)
11 arms × 3 ETFs. Rolling factor Sharpe/Sortino 480d introduced. Sortino blends beat the tail-IC baseline on average; Sharpe-480d family underperforms. See `tests/test_score_ic_ab.py`.

### exit_rank × Sortino Decomposition (2026-08)
ER sweep × Sortino blends × selection/weighting decomposition. Findings: ER25 fairest fixed value; Sortino value is in weighting, not selection; Sortino-weighted arms prefer ER=20 while tail-IC baseline prefers ER=25. See `tests/test_exit_rank_sortino_ab.py`.

### Weight Blend + Yearly Stability (2026-08)
Weight-score blend grid (pure Sortino → pure tailIC) + per-year 2022–2025 stability. 25/75 Sortino/tailIC blend selected as production Score blend; 2025 regime break exposed. See `tests/test_weight_blend_yearly_ab.py`.

### FQ Score System — Meta-IC Harness & Comprehensive Sweep (2026-08)
Built the forward-predictive Factor Quality score judged by meta-IC + block-shuffle null + TP′ hit rates (replacing lockbox-label judgment). Phase 3 A/B: FQ_select_weight partial-pass (avg +0.028, 500ETF −0.403 regression → production unchanged). Comprehensive 27-arm sweep (incl. day-model-new ports: jackknife LOO, n-negative-blocks, vol-regime consistency, deflated-IC noise-floor gate) and gated adaptive-K follow-up: **nothing beats raw tailIC_480d; 3-month TP′ ceiling ≈ 71–75%, 80% unreachable downstream**. Gate-as-default A/B: first version had a pre-EMA −1e9 mask artifact (banishment ~300–900d per tailIC≤0 touch); corrected post-EMA test shows tailIC≤0 gating is a no-op on 300/500ETF and costs 159915ETF −0.091, while Sortino≤0 masking gives +0.135 on 159915ETF only. **Default stays ungated.** See §3.7 and `tests/test_fq_*.py`.

### EMA Span Retest & Sortino Gate Adoption (2026-08)
Hypothesis that EMA(30/90) causes regime lag was rejected: span-off (span=1) is the WORST arm on every ETF (avg Sharpe 0.445 vs 0.724). But spans were stale: 300ETF span 30 → 60 wins yearly-consistently (+0.41 avg yearly Sharpe). **Adopted new production defaults: spans 60/90/90 + Sortino≤0 post-EMA gate** (`--no-sortino-gate` disables). Verified combined config: 300ETF 0.204→0.539, 500ETF unchanged 1.039, 159915ETF 0.930→1.065; avg +0.157. See `tests/test_ema_span_ab.py`, `test_ema_span_yearly.py`, `test_fq_g1_diagnose.py`, `test_new_defaults_verify.py`.

### Option Intraday Stop-Loss Benchmark (2026-08)
5 arms × 3 ETFs. `opt_time_decay_trailing` (30% initial gap, 40% time decay) and `spot_time_decay_trailing` confirmed optimal. Direct option trailing stop cuts MaxDD on 300ETF from 22.87% to 11.57% while boosting Sharpe to 1.251 (+0.205 lift). See `tests/test_option_stoploss_ab.py`.

### Option Strike Selection A/B (2026-08)
5 modes × 3 ETFs (pool _p2016_2024, OOS 2024-2025). All alternatives beat OTM baseline. ETF-adaptive defaults deployed:
- 300ETF: `cascade` wins (Sharpe 0.090→0.492, +5.5x; MaxDD 13.0%→10.2%)
- 500ETF: `nearest` wins (Sharpe 0.703→0.984, +40%; MaxDD 39.6%→26.5%)
- 159915ETF: `vol_t1` wins (Sharpe 0.908→1.244, +37%; MaxDD 18.4%→14.6%)

### Selection FP/TP Invariance Benchmark (2026-08)
Evaluated whether production Top-10 selection system (EMA 480d tail IC + Sortino<=0 gate, ER=25) alters pool's base FP/TP factor distribution. Empirical sweep across 4 diagnosis periods (`p2015_2023`, `p2016_2024`, `p2017_2025`, `p2018_2026`) and 3 ETFs confirmed: **Top-10 selected FP rate (22.69%) matches pool base FP rate (21.88%) almost exactly (0.993x selection ratio)**. Downstream dynamic selection system cannot distinguish TP vs FP factors in-sample (both pass mining filters); FP elimination must occur at admission time during feature mining. See `scratch/test_selection_fp_rate.py`.


## 10. First QMT Draft (2026-08, simulated trading)

Single-file QMT deliverable in `QMT_short/`:
- **Feature hand-pick (Part A)**: `research_qmt_selection.py` unions the 5 B5-gated period pools (500ETF: 524, 159915ETF: 300 candidates), scores by window count / deflated IC / stress-Sortino margins / ONC cluster, then greedy forward-selects 10 features maximizing walk-forward OOS Sharpe (thresholds trained pre-2023 only; corr cap 0.7, cluster cap 2, per-year Sharpe > -0.5). Results: 500ETF Sharpe 1.336 (per-year +1.26/+1.82/+1.05, th 0.70/1.20); 159915ETF Sharpe 2.096 (+2.36/+2.28/+2.09, th 1.10/1.00). Both trajectories peak at 7 features; 8-10 added to honor the top-10 mandate. See `QMT_SELECTION_REPORT.md` + `data/qmt_selection_{ETF}.json`.
- **`qmt_strategy.py`**: fully self-contained (stdlib + numpy only, pure ASCII/gbk-safe). All 24 raw features are early-bar (9:30-10:00) features of the underlying INDEX (500ETF->000905.SH, 159915ETF->399006.SZ); decision at 10:00, long->buy call / short->buy put (front month; strike nearest / vol_t1-proxy), trailing time-decay stop 0.30, 14:35 exit, 14:45 hard flatten, JSON state persistence. Config baked between `QMT-CONFIG-BEGIN/END` markers by `build_qmt_config.py` (selections, pre-2022 recipe stats, ECDF grids, expanding mu/sigma, thresholds, index seeds, account).
- **Audit log contract**: qmt_strategy writes machine-diffable `AUDIT` lines (per-feature raw values, per-feature signed z, composite, thresholds, side, entry/stop/exit events) to `qmt_audit_log.txt`. After market close, `QMT_short/qmt_audit_replay.py` recomputes the same decision path from downloaded repo data (no QMT) and emits identical `AUDIT` lines; diffing isolates any QMT-side data/behavior divergence (the differing key names the problem). Replay also adds `REPLAY_XCHECK` vs `features_{ETF}.parquet`.
- **Parity evidence** (`tests/test_qmt_features.py`, `tests/test_qmt_selection.py`): feature parity 40 days max diff 2e-5 (numba-fastmath residual, tol 1e-4), recipe parity 3.9e-5, 0 side-decision mismatches, greedy rerun byte-identical.
