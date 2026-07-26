# Scheme 5 — Simple Linear GLM (Expanding Ridge)

## 1. Objective

Replace the fixed-weight composite (Schemes 1–4) with a **learned** linear combination that adapts over time. The GLM assigns data-driven coefficients to each sign-aligned factor via expanding-window Ridge regression.

**Adoption rule**: GLM enters production **if and only if** it beats Scheme 4 (Rank Bounded Weight) on the same OOS evaluation period. No additional filters are added — all signal filtering remains upstream in `day-model-new`.

---

## 2. Design Principles

| Principle | Rationale |
|-----------|-----------|
| Expanding window (refit daily) | Zero lookahead; adapts to regime drift |
| Ridge (L2) only | Prevents coefficient explosion with N≈10–30 correlated factors |
| No feature selection inside GLM | Feature admission is already handled by day-model-new gates |
| No additional filters | Filters belong upstream; GLM is pure aggregation |
| Separate script | Keeps `weighting.py` stateless; GLM has internal state (coefficients) |
| Sign-aligned input | Reuse existing `signs` array so GLM coefficients are always ≥ 0 in expectation |

---

## 3. Mathematical Specification

### 3.1 Input

At each day $t$, the input is the sign-aligned z-scored matrix:

$$\tilde{Z}_{i,t} = z_{i,t} \times \text{sign}_i, \quad i = 1 \ldots N$$

where $z_{i,t}$ is the expanding-window z-score (already computed by `expanding_zscore_numba`).

### 3.2 Expanding Ridge Fit

For day $t$ (prediction target), fit on all history $[0, t-1]$:

$$\hat{\beta}_t = \arg\min_{\beta} \sum_{s=0}^{t-1} \left( y_s - \tilde{Z}_s^\top \beta \right)^2 + \lambda \|\beta\|_2^2$$

- $y_s$ = intraday trade return (10:00 → 14:35)
- $\lambda$ = Ridge penalty (see §4)
- No intercept (z-scores are zero-mean by construction)

### 3.3 Composite Signal

$$Z_{\text{composite},t} = \tilde{Z}_t^\top \hat{\beta}_t$$

The output feeds directly into the existing `generate_positions()` threshold/sizing logic — no changes to `strategy.py`.

### 3.4 Coefficient Constraint (Optional Soft Clamp)

To prevent sign-flipping of individual factors due to noise:

$$\beta_i^{\text{clamped}} = \max(0, \beta_i)$$

This enforces "every admitted factor contributes non-negatively after sign alignment." If a factor's expanding coefficient goes negative, it is zeroed out (effectively excluded until it recovers). This is a **soft** constraint — not a filter, just a regularization prior consistent with the admission pipeline's sign guarantee.

---

## 4. Hyperparameter Selection

| Parameter | Default | Selection Method |
|-----------|---------|-----------------|
| $\lambda$ (Ridge alpha) | Sweep `[0.01, 0.1, 1.0, 10.0, 100.0]` | Expanding 5-fold time-series CV on training portion; pick $\lambda$ with best cost-adjusted Sharpe |
| Burn-in | 504 days (2 years) | Same as existing `expanding_zscore_numba` burn-in; GLM starts predicting after burn-in |
| Refit cadence | Daily | Refit $\hat{\beta}$ every day (cheap for N≤30 features) |
| Coefficient clamp | `--no-clamp` to disable | Default: clamp $\beta_i \ge 0$ |

**No Optuna, no feature selection, no target transform.** Keep it dead simple.

---

## 5. Acceptance Threshold (vs Scheme 4)

GLM is adopted for an ETF **if and only if ALL** of the following hold on the standard OOS window (2022-01-01 → 2026-01-01):

| Metric | Condition | Rationale |
|--------|-----------|-----------|
| Cost-Adjusted Sharpe | $\text{Sharpe}_{\text{GLM}} \ge \text{Sharpe}_{\text{Rank}}$ | Must not degrade risk-adjusted return |
| Total PnL (net of 8bps) | $\text{PnL}_{\text{GLM}} \ge 0.8 \times \text{PnL}_{\text{Rank}}$ | Allow slight PnL drop if Sharpe improves |
| Max Drawdown | $\text{MaxDD}_{\text{GLM}} \le 1.5 \times \text{MaxDD}_{\text{Rank}}$ | Must not blow up drawdown |
| Win Rate | $\text{WR}_{\text{GLM}} \ge \text{WR}_{\text{Rank}} - 3\%$ | Tolerance of 3 percentage points |

If GLM fails on **any** ETF, it is not adopted for that ETF (per-ETF decision). The comparison uses identical threshold sweep (`--z-th auto`) and position mode.

---

## 6. Implementation Architecture

```
newtrade/
├── glm_backtest.py       # Standalone CLI runner (separate from run_backtest.py)
├── glm.py                # Core expanding Ridge logic (fit, predict, clamp)
├── plan_glm.md           # This document
├── weighting.py          # UNCHANGED (Schemes 1-4 remain stateless)
├── strategy.py           # UNCHANGED (threshold & sizing reused as-is)
└── utils.py              # UNCHANGED (data loading & z-score reused as-is)
```

### 6.1 `glm.py` — Core Module

```python
def expanding_ridge_composite(
    Z_signed: np.ndarray,       # (T, N) sign-aligned z-scores
    trade_returns: np.ndarray,  # (T,) target
    alphas: list[float],        # Ridge lambda candidates
    burn_in: int = 504,
    clamp_nonneg: bool = True,
    refit_every: int = 1,       # refit cadence (1 = daily)
) -> tuple[np.ndarray, dict]:
    """
    Returns:
      - Z_composite: (T,) predicted signal
      - info: dict with chosen alpha, coefficient history, etc.
    """
```

Internal logic:
1. For each candidate $\lambda$, run expanding fit on training portion `[burn_in, t_start)`.
2. Evaluate cost-adjusted Sharpe on training portion → pick best $\lambda$.
3. Produce OOS composite using the chosen $\lambda$ with daily refit.

### 6.2 `glm_backtest.py` — CLI Runner

```bash
uv run python newtrade/glm_backtest.py -e 300ETF --scheme rank --compare
uv run python newtrade/glm_backtest.py -e all --compare
```

Flags:
- `-e`: ETF selection (same as `run_backtest.py`)
- `--compare`: Run both GLM and Rank side-by-side, print acceptance table
- `--no-clamp`: Disable non-negative coefficient clamp
- `--alphas`: Override Ridge alpha grid (comma-separated)
- `--z-th`, `--position-mode`, `--fee-bps`, `--start-date`, `--end-date`: Inherited from existing CLI conventions
- `--future`: Trade Index Futures (reuse `load_future_trade_returns`)

Output:
- Prints comparison table (GLM vs Rank) with PASS/FAIL per ETF
- Saves `newtrade/artifacts/glm_vs_rank.csv`
- Saves `newtrade/artifacts/glm_equity.png` (overlay with Rank equity)

---

## 7. Zero-Lookahead Guarantees

| Component | Guarantee |
|-----------|-----------|
| Z-scores | Expanding window `[0, t-1]` (existing `expanding_zscore_numba`) |
| Ridge fit | Trained on `[0, t-1]`; predicts day $t$ |
| Alpha selection | Chosen on training portion only (pre-OOS) |
| Threshold sweep | Same as existing: train portion only + production buffer |
| Coefficient clamp | Applied to $\hat{\beta}_t$ fitted on past data only |

---

## 8. What This Does NOT Do

- ❌ No feature selection / pruning inside GLM (that's day-model-new's job)
- ❌ No additional signal filters (RSI, MACD, vol gates, etc.)
- ❌ No non-linear terms, interactions, or polynomial features
- ❌ No Optuna / Bayesian hyperparameter search
- ❌ No target transformation (rank, Gaussian)
- ❌ No rolling window (only expanding — simpler, more stable)
- ❌ No modification to `weighting.py`, `strategy.py`, or `utils.py`

---

## 9. Success Criteria Summary

```
For each ETF:
  IF  Sharpe_GLM >= Sharpe_Rank
  AND PnL_GLM >= 0.8 * PnL_Rank
  AND MaxDD_GLM <= 1.5 * MaxDD_Rank
  AND WinRate_GLM >= WinRate_Rank - 3%
  THEN → GLM passes for this ETF
```

If GLM passes for ≥ 3 out of 5 ETFs, consider it production-viable and integrate into `run_backtest.py` as `--scheme glm`.
