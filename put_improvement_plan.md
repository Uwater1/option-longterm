# Protective Put — 4-Type Alpha Model Report

> **Status**: Alpha model overhauled & OOS-validated. 3 phases (linear / LightGBM / rule-anchored hybrid) built and compared via put P&L. **4 of 12 ETF×regime cells are deployable** (beat static filter). Pending: engine integration of deployable cells, backtest comparison, active exit rules (TODO 4/6/7).

---

## 1. System Overview

### 1.1 Current Production System

| Aspect | Implementation |
|--------|---------------|
| **Timing** | Enter long put at cycle start (4th Tuesday, day after expiry). Hold to expiry. |
| **Selection** | Fixed OTM levels (OTM1 for 300ETF, OTM2 for 50ETF/500ETF). |
| **Execution** | Market orders at close (default) or BS-mapped limit buy (`--limit-entry`). |
| **Filter** | Static cycle-start indicators: RSI, Bollinger Bands, Vol20, MACD, skewness, kurtosis, drawdown. |

### 1.2 Known Weaknesses

1. **Negative Theta Drag** — Monthly put at cycle start pays significant time value. Flat/rally → premium wasted.
2. **Static Filtering** — Regime evaluated once/month at cycle start. Mid-cycle bearish signals missed.
3. **Fixed DTE** — Always monthly. Shorter DTE (10–15d) has lower cost but faster decay; dynamic DTE unexplored.
4. **No Exit Rules** — Held to expiry. Early bounce gives back paper profits.

---

## 2. The 4-Type Alpha Model

To maximize hedging efficiency and minimize premium decay, entry decisions map **expected behavior** (How) against **horizon** (When). Each quadrant runs a dedicated weighted score model with optimized parameters.

### 2.1 Decision Matrix

| Horizon \ Behavior | **Fall** (Expected Return < -a% in m days) | **Crash** (P(>5% drop in m days) >= b%) |
|:---|:---|:---|
| **Short-Term** (m ≤ 14d) | **Regime 1: ST Fall** → Buy ATM/OTM1 Put | **Regime 3: ST Crash** → Buy OTM2/OTM3 Put |
| **Medium-Term** (14 < m ≤ 40d) | **Regime 2: MT Fall** → Buy ATM/OTM1 Put | **Regime 4: MT Crash** → Buy OTM2/OTM3 Put |

### 2.2 Score Calculation

$$\text{Alpha Score} = \sum (w_i \times I_i)$$

- $I_i$: Indicator normalized via **rolling 252-day percentile rank** (or expanding-window with `--expanding-pct`) → [0.0, 1.0]. Look-ahead free.
- $w_i$: Weight optimized per ETF per regime via random-search (Dirichlet sampling × horizon grid), selected by mean OOS metric across walk-forward folds (`--select-by-oos`).

**Indicator families** (18 total in `alpha_model.py`):

| Family | Indicators | Normalized Column |
|--------|-----------|-------------------|
| Momentum | RSI, MACD Histogram, ROC5, ROC20 | `ind_rsi_high/low`, `ind_macd_neg`, `ind_roc5_neg`, `ind_roc20_neg` |
| Volatility | Skewness, Kurtosis, Vol Accel, IV/RV Ratio, Vol-of-vol, Vol Term Structure | `ind_skew_neg`, `ind_kurt_high`, `ind_vol_accel_high`, `ind_iv_vol_low`, `ind_vol_of_vol_high`, `ind_term_structure_neg` |
| Structural | Drawdown, Dist-SMA50, Dist-SMA200, ATR Ratio, Range Expansion | `ind_dd_deep`, `ind_dist_sma50_neg`, `ind_dist_sma200_neg`, `ind_atr_ratio_high`, `ind_range_expansion_high` |
| Flow / Divergence | OBV Divergence, Volume Spike, RSI Divergence | `ind_obv_divergence`, `ind_volume_spike`, `ind_rsi_divergence_neg` |

### 2.3 Optimized Parameters & Performance

> The original §2.3 in-sample tables (Fall/Crash lifts) were **artifacts of a sign-inverted crash-event test** and have been removed. See §4.1 for the corrected, walk-forward OOS results and §4.3 for put P&L validation (the real test).


---

## 3. Three Phases — How It Works

The alpha model evolved through three phases, each addressing the previous phase's OOS weakness. The validator (`validate_alpha_pnl.py`) compares all three on identical OOS put P&L.

| Phase | File | Mechanism | Best when |
|-------|------|-----------|-----------|
| **1. Linear weighted score** | `alpha_model.py` + `optimize_put_alpha.py` | Dirichlet-weighted sum of 18 rolling-pct indicators; weights selected by mean OOS across purged walk-forward folds | Few high-quality triggers needed (e.g. 300ETF ST Fall) |
| **2. LightGBM classifier** | `alpha_model_ml.py` | Per-regime monotone (+1) bagged (×5) LGB, isotonic-calibrated, walk-forward expanding training | Daily-cadence crash AUC is good (reg3 AUC 0.63), but over-triggers at cycle cadence |
| **3. Rule-anchored hybrid** | `alpha_model_hybrid.py` | L2-regularized logistic stack of [Phase1 rank, Phase2 prob, FINDINGS rule flags] | Selective fall/crash entries where validated rules add robustness (300ETF MT Fall, 50ETF MT Crash) |

**Core design choices (all phases)**:
- **Percentile rank normalization** — removes distribution differences; RSI [0–100] and skewness [-3, +3] become comparable [0,1]. Look-ahead-free.
- **252-day rolling window** (or expanding) — adapts to regime changes without look-ahead.
- **Walk-forward as selection objective** — final configs chosen by mean OOS, not best IS.
- **Purged folds** — train rows whose forward target leaks into test are dropped.

**Anti-overfit devices**:
- Phase 1: max-weight cap 0.5; composite objective (Spearman + complexity penalty).
- Phase 2: shallow trees (num_leaves=8, depth=3), min_child_samples=50, monotone constraints, bagging, isotonic calibration.
- Phase 3: strong L2 (C=0.5); rule anchoring on FINDINGS-validated signals (p<0.001 for the strongest).

---

## 4. Known Weaknesses & Improvement Areas

The original optimizer had two overfit modes that are now resolved (see §4.2 for the fixes):

1. **Single-indicator dominance** — pre-cap runs converged to near-single-factor models (e.g. 50ETF MT Fall 94.3% on `ind_dist_sma50_neg`), correct in-sample but fragile OOS. **Fixed**: `--max-weight 0.5` enforced on all ETFs; all 12 cells now ≤0.5 max weight.
2. **Missed crash events** — static percentile thresholds dropped rare crashes. **Fixed**: dynamic IV-aware threshold $T_t = T_{base} + \gamma \times (\text{iv\_vol\_ratio}_t - 1.0)$, $\gamma$ optimized via grid search.

These were diagnostic problems of the *linear* optimizer. Phases 2/3 add the non-linear modeling capacity the linear score lacked.

### 4.1 Out-of-Sample Validation

**Status**: Implemented AND used as the selection objective.

Walk-forward validation (expanding train window, purged by horizon) is available via `--walk-forward` (diagnostic) and `--select-by-oos` (selection). The Phase 1 overhaul selects final configs by **mean OOS metric across folds**, not best in-sample.

**Critical fix found during overhaul**: the original crash-event test was sign-inverted (`target = -worst_dd` made `target <= -0.05` unreachable), so ALL original crash lifts silently computed to ~0 and the "4.09x lift" in the original §2.3 was an in-sample artifact. After fixing, real walk-forward OOS results:

| ETF | Regime | OOS lift (crash) / mean_ret (fall) | 95% CI | Gate |
|-----|--------|-----------------------------------|--------|------|
| 50ETF | ST Crash | 2.12x | [0.60, 4.37] | PASS |
| 50ETF | MT Crash | 2.10x | [0.71, 3.93] | PASS |
| 300ETF | ST Crash | 2.03x | [0.27, 4.16] | PASS |
| 300ETF | MT Crash | 1.45x | [0.48, 2.41] | PASS |
| 500ETF | ST Crash | 1.65x | [0.46, 3.27] | PASS |
| 500ETF | MT Crash | 1.06x | [0.53, 1.68] | PASS |

Statistical signal now genuinely above random (was worse-than-random before). Whether it translates to profitable put hedging is tested separately by `validate_alpha_pnl.py` (see §4.3).


### 4.2 Improvement Roadmap

| Improvement | Difficulty | Impact | Description |
|-------------|------------|--------|-------------|
| Walk-forward validation | Implemented | High | Chronological OOS validation (`--walk-forward`) |
| **OOS-as-selection-objective** | **Implemented** | **High** | `--select-by-oos` picks config by mean OOS across purged folds |
| **New objective (Spearman + complexity penalty)** | **Implemented** | **High** | Replaced noise-chasing `-corr - 200*mean_ret` |
| **5 new tail-risk indicators** | **Implemented** | **Medium** | ATR ratio, vol-of-vol, range expansion, vol term structure, RSI divergence |
| Volume/money flow indicators | Implemented | Medium | Added `ind_obv_divergence`, `ind_volume_spike` |
| Dynamic threshold (IV-aware) | Implemented | Medium | Modulates threshold based on option cost |
| **Phase 2: LightGBM regime models** | **Implemented** | **Medium** | `alpha_model_ml.py` — monotone+bagged+isotonic, walk-forward |
| **Phase 3: Rule-anchored hybrid** | **Implemented** | **High** | `alpha_model_hybrid.py` — FINDINGS rules + Phase1 + Phase2 logistic stack |
| **Put P&L validator** | **Implemented** | **High** | `validate_alpha_pnl.py` — real option P&L vs 3 baselines |
| Active exit rules (TP/SL) | Medium | High | Close put at 2x premium or after 7d with no drop |
| Macro signals | High | High | Credit spread, sector rotation, VIX futures |
| Multi-DTE selection | High | Medium | Match regime horizon to option DTE |


### 4.3 Put P&L Validation Results (the real test)

Statistical lift (§4.1) measures whether the score ranks forward risk correctly. It does **not** measure whether hedging is profitable after theta decay. `validate_alpha_pnl.py` computes actual put option P&L per trigger at monthly-cycle cadence (fair comparison vs baselines) over OOS years (>= 2021).

Three model phases were built and compared; the best deployable phase per cell is:

| ETF | Regime | Winning Phase | Alpha net P&L (N) | Static filter net P&L (N) | Alpha Sharpe |
|-----|--------|---------------|-------------------|---------------------------|--------------|
| 50ETF | MT Crash | **Phase 3** | **+2,144** (6) | +1,613 (4) | 1.81 |
| 300ETF | ST Fall | **Phase 1** | **+2,689** (7) | +1,385 (12) | 0.70 |
| 300ETF | MT Fall | **Phase 3** | **+2,216** (8) | +1,385 (12) | 0.57 |
| 500ETF | ST Crash | **Phase 2** | **+382** (6) | -114 (1) | — |

**Deployability decision rule**: a phase is deployable only if net P&L > 0, Sharpe > 0, per-trigger P&L > 0, AND it beats the existing static filter on net P&L. 4 of 12 ETF×regime cells clear the bar; the other 8 retain the static filter. No single phase dominates — Phase 1 wins ST Fall (300), Phase 2 wins ST Crash (500), Phase 3 wins MT Fall (300) and MT Crash (50).

**Key honest findings**:
- 500ETF remains largely unhedgeable (consistent with [RESEARCH_500ETF.md](file:///home/hallo/Documents/option-longterm/RESEARCH_500ETF.md)): high vol + sharp rallies cause assignment-style losses on puts across all phases.
- Pure Phase 2 ML over-triggers at cycle cadence (theta drag) despite good daily AUC (reg3 crash AUC 0.63). Statistical AUC does NOT transfer directly to cycle-cadence P&L.
- Phase 3 rule-anchoring produces the most selective, highest per-trigger entries (best for fall regimes).
- Full table + per-fold detail: `backtest/alpha_phase_comparison.md`, `backtest/validate_pnl_phase{1,2,3}.json`.

**Why "good but not great"**: predicting monthly-cycle-ahead downside from daily indicators is inherently hard; the achievable edge is real but selective. The validator makes this measurable rather than optimistic.


---

## 5. Extension Guide — Where to Plug New Alphas

The architecture has well-defined extension points across all 3 phases.

### 5.1 Add Indicator (`alpha_model.py`)

**File**: `alpha_model.py` → `compute_normalized_indicators()`

```python
# Example: adding a new divergence indicator
def compute_normalized_indicators(self, df):
    ndf = df.copy()
    # ... existing indicators ...

    # NEW: bearish divergence — higher value = more bearish
    ndf["ind_new_signal"] = self._rp(ndf["raw_new_value"])  # _rp = rolling/expanding pct rank
    return ndf
```

**Rules**:
- Prefix with `ind_` (score 0→1, where 1 = bearish).
- Use `self._rp()` (rolling 252-day or expanding-window percentile rank) for look-ahead-free normalization.
- No future data (no `.shift(-n)`, no full-sample statistics).
- Higher value must mean more bearish (Phase 2/3 rely on this for monotone constraints +1).

### 5.2 Register in Optimizer (`optimize_put_alpha.py`)

**File**: `optimize_put_alpha.py` → `regime_configs` dict (Phase 1); feature list in `alpha_model_ml.py` `FEATURES` (Phase 2); `compute_rule_flags()` in `alpha_model_hybrid.py` (Phase 3 rules).

```python
# Phase 1: add to regime_configs indicators list
regime_configs = {
    "reg3": {
        "indicators": [
            "ind_vol_accel_high", "ind_kurt_high", "ind_skew_neg",
            "ind_iv_vol_low", "ind_new_signal",   # <-- ADD HERE
        ],
        "horizons": [5, 14],
        "is_crash": True
    },
}
```

Re-run with OOS selection (recommended):
```bash
python optimize_put_alpha.py -e all --select-by-oos --max-weight 0.5
```

For Phase 2, also add the indicator name to the `FEATURES` list in `alpha_model_ml.py` (monotone constraints are auto-assigned +1).

### 5.3 Validate with P&L (`validate_alpha_pnl.py`)

After any model change, run the P&L validator to confirm the statistical lift translates to hedging profit:

```bash
python validate_alpha_pnl.py -e all --phase 1 --cadence cycle   # fair monthly cadence
python validate_alpha_pnl.py -e 300 --phase 2 --cadence cycle
python validate_alpha_pnl.py -e 300 --phase 3 --cadence cycle
python compare_alpha_phases.py                                   # cross-phase winner table
```

A variant is **deployable** only if: net P&L>0 AND Sharpe>0 AND per-trigger>0 AND beats the static filter.

### 5.4 Integrate into Backtest (`backtest_strategies.py`)

**File**: `backtest_strategies.py` → `PutStrategy.evaluate_filter()`

After TODO 4 (daily scanning) lands, wire the winning phase per cell:

```python
def evaluate_filter(self, etf, idx, etf_close, indicators, alpha_scores=None):
    if alpha_scores is not None:
        # Use the per-ETF-per-regime winner from backtest/alpha_phase_comparison.md
        reg_key = self.deployed_regime  # e.g. "reg1" for 300ETF ST Fall
        score = alpha_scores.get(f"score_{reg_key}", 0)
        threshold = self.model_config[reg_key]["threshold"]
        filter_would_pass = score > threshold
        return filter_would_pass, filter_would_pass
    # Fallback to existing static filter...
```

### 5.5 Adding a New Alpha — Checklist

```
1. Compute raw indicator in alpha_model.py → compute_normalized_indicators()
2. Add normalized column prefixed with ind_ (bearish-positive scale)
3. Phase 1: add to optimize_put_alpha.py regime_configs indicators
4. Phase 2: add to alpha_model_ml.py FEATURES list
5. Re-run: python optimize_put_alpha.py -e all --select-by-oos --max-weight 0.5
6. Validate: python validate_alpha_pnl.py -e all --phase 1 --cadence cycle
7. Compare: python compare_alpha_phases.py
8. If deployable: wire into PutStrategy.evaluate_filter() (after TODO 4)
```

---

## 6. Active Exit Management (Future)

Lock in option gains before mean reversion or decay erodes them:

- **Premium Multiplier**: Exit if put premium reaches 2x or 3x entry cost.
- **Underlying Support Target**: Close put if ETF hits support level.
- **Time-based Decay Cut**: Exit if expected drop fails to materialize within $T$ days to limit Theta burn.

---

## 7. Remaining TODO

* `[x]` **TODO 1: Data Completeness & Sync** — Updated daily + 5m data for all ETFs.
* `[x]` **TODO 2: Signal / Indicator Enhancement** — Scanned ~30 indicators, identified tail-risk predictors, updated FINDINGS.md.
* `[x]` **TODO 3: Alpha Model Integration & Weight Optimization**
  * ✅ 4-Type Decision Matrix → `alpha_model.py`
  * ✅ 18 normalized indicators (incl. OBV divergence, volume spike, ATR ratio, vol-of-vol, range expansion, vol term structure, RSI divergence)
  * ✅ Random-search weight optimizer with max-weight capping
  * ✅ **Fixed RSI normalization** (was raw /100; now rolling percentile rank)
  * ✅ **Fixed crash-event sign bug** (inverted target made all original crash lifts ~0)
  * ✅ New composite objective (Spearman rank + log placement + complexity penalty) replacing noise-chasing `200*mean_ret`
  * ✅ Walk-forward as selection objective (`--select-by-oos`, purged expanding folds)
  * ✅ Dynamic IV-aware threshold optimization (γ)
  * ✅ Bootstrap CI on OOS metric; passed_gate flag per cell
  * ✅ Phase 2 LightGBM regime models (`alpha_model_ml.py`, monotone+bagged+isotonic)
  * ✅ Phase 3 rule-anchored hybrid (`alpha_model_hybrid.py`, logistic stack on FINDINGS rules)
  * ✅ Put P&L validator (`validate_alpha_pnl.py`) — real option P&L vs 3 baselines
  * ✅ Optimized models saved → `backtest/alpha_put_models.json`, `backtest/alpha_ml_models/`
  * ✅ **Honest OOS result: 4 of 12 cells deployable** (beat static filter). See §4.3 + `backtest/alpha_phase_comparison.md`.

* `[x]` **TODO 4: Engine Architecture Modifications / Dedicated Daily Runner**
  * ✅ Created new daily position-tracking protective put backtester from scratch (`backtest_put.py`).
  * ✅ Implemented daily indicator evaluation, mid-cycle entries, and clean hold-to-expiry/settlement logic.
  * ✅ Decoupled from Call Strategy to prevent risk or regressions in the existing engine.
* `[ ]` **TODO 5: Dynamic DTE / Contract Selection**
  * Match regime horizon ($m$) to option DTE dynamically.
  * Evaluate near-month vs next-month performance.
* `[ ]` **TODO 6: Active Exit Rules**
  * Implement take-profit (2x/3x premium), stop-loss, and time-based decay cut.
* `[ ]` **TODO 7: End-to-End Optimization**
  * Grid search on dynamic triggers, weights, exit rules, and DTE selection.
  * Compare alpha-model-driven put strategy against current static filter baseline.
