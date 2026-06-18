# Improve Put Alpha Model (TODO 3) — Predictive Power Overhaul

## Problem Diagnosis (confirmed via walk-forward)

`optimize_put_alpha.py --walk-forward -e 300` shows **every regime is overfit**:

| Regime | IS avg | OOS avg | Degradation |
|--------|--------|---------|-------------|
| R1 ST Fall | -1.22% | **+3.12%** (wrong sign) | 356% |
| R2 MT Fall | -0.88% | **+3.21%** (wrong sign) | 465% |
| R3 ST Crash | lift 4.68x | **lift 0.81x** (worse than random) | 105% |
| R4 MT Crash | lift 3.21x | **lift 0.78x** (worse than random) | 110% |

Root causes:

1. **Objective chases in-sample noise** — `obj = -corr - 200*mean_ret_trig`; mean_ret_trig dominates 200:1, correlation (the generalizable part) effectively ignored.
2. **Multiple-testing inflation** — ~60k combos × ~1500 days; pure noise finds good IS scores.
3. **Linear weighted sum too weak** — best |corr| = 0.05–0.18 (R² ≈ 0.01); signals are non-linear/interactive.
4. **Walk-forward is diagnostic only** — never used as selection objective; 2-yr train window too short for 252-day rolling indicators.
5. **Bugs**: RSI not rolling-percentile normalized (`rsi14/100` instead of `roll_pct`); 50/500 ETFs in JSON still have 0.94 single-factor weights and missing `gamma` key (never re-optimized under cap).
6. **Threshold too tight** — Top 10% ≈ 150 days; baseline crash rate ~5% → expected ~7 positives (huge variance).
7. **Target mismatch** — optimizes forward return / crash prob, not actual put P&L.

---

## Goal

Lift OOS predictive power from "worse than random" to a useful, validated hedge signal — measured by both statistical metrics (Spearman, lift, AUC) AND realized put P&L on walk-forward folds. Keep the 4-regime framework. Deliver three progressively-stronger model variants and pick the winner per ETF/regime based on OOS performance.

---

## Design Principles (apply to all phases)

- **Walk-forward CV is the selection objective**, not diagnostic. Parameters are chosen by mean OOS metric across folds, not best IS.
- **Purged folds** — drop the `m` days after each train boundary from training to avoid label leakage (forward targets overlap).
- **Multiple-testing discipline** — limit grid size; report OOS metric with bootstrap CI; require OOS lift > 1.2 (crash) or OOS mean_ret < baseline (fall) at p<0.10 to accept.
- **No look-ahead** — keep 252-day `roll_pct`; also use **expanding-window** percentile (min 252) so thresholds adapt.
- **Minimum sample** — require ≥30 crash events in triggered set, not 10.
- **Three deliverables** scored on identical OOS metrics for apples-to-apples comparison.

---

## Phase 1 — Linear Optimizer Fixes (fast, low-risk)

**Files**: `alpha_model.py`, `optimize_put_alpha.py`.

### 1.1 Fix `alpha_model.py`

- **RSI normalization**: replace `ndf["ind_rsi_high"] = ndf["rsi14"] / 100.0` with `roll_pct(ndf["rsi14"])` and `ind_rsi_low = 1 - roll_pct(rsi14)`. Raw RSI's distribution drifts across regimes; rolling percentile restores cross-time comparability.
- **Expanding-window option**: add `window="expanding"` mode to `roll_pct` (min_periods=252) so early thresholds adapt; keep 252-day rolling as default.
- **New indicators** (look-ahead-free, normalized):
  - `ind_atr_ratio_high` — `atr20 / atr20.rolling(252).median` → range expansion.
  - `ind_vol_of_vol_high` — `vol20.rolling(20).std()` pct rank → vol regime instability.
  - `ind_range_expansion_high` — `(high-low)/close` rolling pct rank.
  - `ind_term_structure_neg` — `vol10 / vol60` pct rank (inverted) → inverted vol term = stress.
  - `ind_rsi_divergence_neg` — price ROC20 vs RSI ROC20 slope divergence.
- Add these to all 4 `regime_configs` indicator lists as candidates.

### 1.2 Rewrite `optimize_regime()` objective

Replace `obj_score` with a **composite, OOS-friendly objective**:

```
# Fall regime
spearman = spearmanr(scores, fwd_ret).correlation
mean_ret_trig = fwd_ret[triggered].mean()
placement = triggered.mean()
# Require signal direction correctness; penalize tiny placement
obj = (-spearman)                       # generalizable ranking power
      + (-2.0) * max(mean_ret_trig, 0)  # penalize UP moves when triggered
      - 0.5 * (mean_ret_trig < 0)       # reward correct direction
      - 0.3 * log(placement / 0.10)     # softer placement preference (log)
      - 0.1 * effective_n_indicators    # complexity penalty

# Crash regime
spearman = spearmanr(scores, -worst_dd).correlation
lift = crash_in_trig / baseline_crash_prob
obj = spearman * 2.0 + log(lift) - 0.1 * n_indicators
```

Key changes:
- **Spearman** (rank) not Pearson — robust to fat tails & outliers.
- **Log placement** preference — softer than hard percentile cuts; avoids cherry-picking 10%.
- **Complexity penalty** — discourages many-indicator noise fits.
- Min-triggered count raised 10 → 30.

### 1.3 Walk-forward as selection objective

Add `--select-by-oos` flag to `optimize_put_alpha.py`. New `optimize_regime_wf()`:
1. For each candidate config (weights × horizon × γ), compute mean OOS metric across walk-forward folds (purged).
2. Pick config with best **mean OOS**, not best IS.
3. Save full fold table to JSON for inspection.

Train window expanded 2y → **expanding** (start at year-3, grow to all-available-before-test). Min train size 750 days.

### 1.4 Reduce grid; add bootstrap CI

- Horizons: keep [5, 10, 14] / [21, 30, 40] but **fix one per regime family** chosen ex-ante from FINDINGS (don't grid both).
- Thresholds: percentiles [85, 90] only (drop 75, 80 — too noisy).
- γ: [0.0, 0.10] only.
- Random samples: 500 (down from 1000) since OOS-CV is more expensive.
- Bootstrap (1000 resamples) CI on OOS lift; flag if lower bound < 1.0.

### 1.5 Re-run all ETFs

- `python optimize_put_alpha.py -e all --select-by-oos --max-weight 0.5`
- Verify JSON has `gamma` key and no weight >0.5 for 50/500 ETFs.
- Update `FINDINGS.md` §8 with new params + OOS metrics.

**Exit criteria Phase 1**: OOS degradation < 50% on at least 2/3 ETFs for crash regimes; OOS lift > 1.0 (above random) for ≥4 of 12 ETF×regime cells.

---

## Phase 2 — LightGBM Classifier/Regressor Layer (more power)

**New file**: `alpha_model_ml.py`. **Modified**: `optimize_put_alpha.py` (add `--ml` flag).

### 2.1 Per-regime supervised model

For each regime, train a LightGBM model on the same normalized indicators:

- **Fall regimes (R1, R2)** → `LGBMRegressor` predicting `fwd_ret` (or `LGBMClassifier` on `fwd_ret < -threshold`).
- **Crash regimes (R3, R4)** → `LGBMClassifier` on `worst_dd <= -0.05` (positive class). Use `is_unbalance=True` or `scale_pos_weight` for class imbalance.

Hyperparameters (anti-overfit):
```python
LGBMClassifier(
    objective="binary",
    num_leaves=8,              # very shallow
    max_depth=3,
    n_estimators=150,
    learning_rate=0.03,
    min_child_samples=50,      # large for ~1500-day dataset
    reg_alpha=1.0, reg_lambda=1.0,
    subsample=0.7, colsample_bytree=0.7,
    monotone_constraints=...,  # see below
)
```

### 2.2 Monotonic constraints

All indicators are designed so higher = more bearish/crash risk. Enforce monotonicity:
```python
monotone_constraints = [1] * len(features)
```
This prevents the model from learning spurious inversions on small samples and aligns with the documented indicator semantics.

### 2.3 Bagged ensemble

Reuse `train_lightgbm_bagged` pattern from `predict_open_high.py`: N=5 bootstrap bags, average probabilities. Reduces variance.

### 2.4 Walk-forward training & selection

- For each fold: train on expanding window, predict on test year.
- Hyperparameter tuning via inner TimeSeriesSplit (nested CV) on train only.
- Threshold (probability cutoff) selected on train fold to maximize F1 / lift at fixed placement (~10–15%).
- Save per-fold predictions; compute OOS AUC, OOS lift, OOS Sharpe of triggered P&L.

### 2.5 Calibration

- Apply **isotonic regression** on a held-out fold to map raw LGB probability → calibrated P(crash).
- Calibrated probability is what gets thresholded.

**Exit criteria Phase 2**: OOS AUC > 0.60 for crash regimes on ≥2 ETFs; OOS lift > 1.3 (CI lower bound > 1.0) for ≥4 cells. Otherwise Phase 2 not deployed for that ETF/regime.

---

## Phase 3 — Hybrid: Rules + ML (robustness anchor)

**New file**: `alpha_model_hybrid.py`. Reuses Phases 1 & 2.

### 3.1 Anchor features from validated rules

From `FINDINGS.md` §6/§7, hard-coded rule signals (statistically validated, bias-free) become binary/numeric features fed into the ML layer:

- 300ETF: `rule_bear_trend = (dd_252 < -0.15) & (dist_sma50 < -1.0)` (p=0.0003, 2.33x lift)
- 300ETF: `rule_overbought_reversal = (rsi14 > 65) & (skew_20 < -0.3)` (p=0.076, 3.09x lift)
- 500ETF: `rule_skew_close = (skew_20 < -0.5) & (close > sma50)` (2.19x lift)
- 50ETF: `rule_vol_spike = vol20 > rolling_q90(vol20, 252)` (2.85x lift)
- Generic: `rule_kurt_skew = (kurt_20 < q10) & (skew_20 < -0.3)` (300ETF 93.3% neg-30d)

Add the rule's `int` (0/1) output + its components as features alongside the Phase-1 normalized indicators.

### 3.2 Stacking

Two-layer model:
- **Layer 1**: Phase-1 linear score + Phase-2 LGB probability + rule binary flags (all look-ahead-free).
- **Layer 2**: Logistic regression (L2-regularized, monotonic where possible) combines the three into final P(crash) / expected return.

Logistic regression chosen because it's high-bias/low-variance — appropriate for the tiny sample.

### 3.3 Same walk-forward discipline

Same expanding-window purged CV; same OOS metrics; same threshold selection.

**Exit criteria Phase 3**: Hybrid OOS metric ≥ max(Phase 1, Phase 2) on ≥2/3 ETFs. Otherwise declare no improvement and keep simpler winner.

---

## Validation Layer — Put P&L Backtest (all phases)

**New file**: `validate_alpha_pnl.py`.

For each candidate model (Phase 1/2/3 × 4 regimes × 3 ETFs), compute **actual put P&L per trigger** using historical option prices — not just statistical metrics.

### What it does

For each walk-forward test fold:
1. Identify days where model triggers (score > threshold).
2. For each trigger day, find the next monthly put contract at the regime-appropriate OTM level (R1/R2 → OTM1, R3/R4 → OTM2/OTM3).
3. Compute entry premium (mid + slippage), exit at expiry using `calc_leg_pnl` from `backtest_engine.py`.
4. Aggregate: net P&L, win rate, Sharpe, max DD, placement rate.
5. Compare against:
   - **Baseline A**: filter never triggers (no hedge).
   - **Baseline B**: filter always triggers (hedge every cycle).
   - **Baseline C**: existing static filter in `PutStrategy.evaluate_filter`.

### Reported metrics

| Metric | Why |
|--------|-----|
| Net P&L per trigger | Direct hedging value. |
| Win rate | Fraction of triggers profitable. |
| Sharpe (annualized) | Risk-adjusted. |
| Max DD | Tail behavior of strategy itself. |
| Placement rate | Trade frequency. |
| OOS statistical lift | Cross-check vs P&L. |

### Decision rule

A model variant is **deployable** for an ETF/regime only if:
- OOS put P&L per trigger > 0,
- OOS lift CI lower bound > 1.0 (crash) OR OOS mean_ret < baseline (fall) at p<0.10,
- OOS Sharpe > 0 (no negative-drift hedging),
- Beats Baseline C (existing static filter) on net P&L.

If none of Phase 1/2/3 clears the bar for an ETF/regime → keep the existing static filter (documented in `FINDINGS.md`) and mark that cell "no alpha improvement found".

---

## Implementation Order & Effort

| Step | Phase | Est. effort | Files |
|------|-------|-------------|-------|
| 1 | 1.1 RSI fix + new indicators | S | `alpha_model.py` |
| 2 | 1.2 Objective rewrite | M | `optimize_put_alpha.py` |
| 3 | 1.3–1.4 Walk-forward selection + grid trim | M | `optimize_put_alpha.py` |
| 4 | 1.5 Re-run all ETFs | S | run command |
| 5 | Validate Phase 1 | M | `validate_alpha_pnl.py` (new) |
| 6 | 2.1–2.5 LightGBM regime models | L | `alpha_model_ml.py` (new) |
| 7 | Validate Phase 2 | S | reuse validator |
| 8 | 3.1–3.3 Hybrid stack | M | `alpha_model_hybrid.py` (new) |
| 9 | Validate Phase 3 | S | reuse validator |
| 10 | Comparison report + update docs | S | `put_improvement_plan.md`, `FINDINGS.md`, `AGENTS.md` |

Run sequence after each phase:
```bash
python optimize_put_alpha.py -e all --select-by-oos --max-weight 0.5
python validate_alpha_pnl.py -e all --phase {1|2|3}
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Phase 2 LGB still overfits (small N, rare events) | Shallow trees, monotone constraints, bagging, min_child_samples=50, nested CV. |
| No model clears deploy bar for some ETFs | Keep existing static filter; document as "no alpha edge found". Honest null result. |
| Walk-forward too few folds (only 2021–2026) | Use expanding train, purge only `m` days, accept lower statistical power. |
| Option data gaps for some trigger days | Skip trigger; report coverage %; require ≥80% coverage to publish P&L. |
| Overfitting to P&L backtest itself | Use walk-forward P&L only; never full-sample. Lock validator before tuning. |

---

## Deliverables

1. Refactored `alpha_model.py` (RSI fix + 5 new indicators + expanding option).
2. Refactored `optimize_put_alpha.py` (new objective, walk-forward selection, grid trim, bootstrap CI).
3. New `alpha_model_ml.py` (per-regime LGB classifier/regressor, monotone + bagged + isotonic).
4. New `alpha_model_hybrid.py` (rules + Phase 1 + Phase 2 stacked via logistic).
5. New `validate_alpha_pnl.py` (P&L backtest validator with 3 baselines).
6. Updated `backtest/alpha_put_models.json` (per-ETF per-regime: winning variant, weights/model ref, OOS metrics, fold table).
7. Updated `put_improvement_plan.md` §4.3 & TODO 3 — replace "implemented/working" with honest OOS results + per-ETF winner table.
8. Updated `FINDINGS.md` §8 with revised parameters and **OOS** metrics.
9. `AGENTS.md` — add new commands + architecture notes.

## Definition of Done

- Walk-forward OOS report shows ≥4 of 12 ETF×regime cells with lift > 1.3 (crash) or mean_ret below baseline (fall), CI lower bound > 1.0 / p<0.10.
- Put P&L validator shows the winning variant beats Baseline C (existing static filter) on net P&L for ≥2 ETFs.
- All non-deployable cells explicitly documented with reason.
- TODO 3 status in `put_improvement_plan.md` reflects actual OOS performance, not in-sample optimism.
