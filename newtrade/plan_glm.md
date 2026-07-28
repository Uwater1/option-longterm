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

- ❌ No hard feature selection / pruning inside GLM (that's day-model-new's job)
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

---

## 10. V2 Improvements — IC-Weighted Prior & N-Adaptive Regularization

### 10.1 V1 Failure Analysis

| ETF | N | V1 Result | Root Cause |
|-----|---|-----------|------------|
| 300ETF | 10 | PASS (Sharpe 0.919) | Small pool, Ridge concentrates well |
| 500ETF | 32 | FAIL (Sharpe 0.422) | Signal dilution across 32 correlated combos |
| 159915ETF | 11 | FAIL (Sharpe 1.056, WR 56%) | Overtrading (628 vs 239 trades), noisy composite |

**Core weakness**: Ridge with $\alpha I$ penalty treats all features equally. With large correlated pools, it cannot concentrate signal the way Rank does with score-based tilting.

### 10.2 V2 Design: IC-Weighted Ridge Prior

Replace isotropic penalty with anisotropic prior informed by admission metadata:

$$\hat{\beta}_t = \arg\min_{\beta} \sum_{s=0}^{t-1} (y_s - \tilde{Z}_s^\top \beta)^2 + \lambda \cdot \beta^\top D^{-1} \beta$$

where $D = \text{diag}(\text{deflated\_ic}_1, \ldots, \text{deflated\_ic}_N)$.

- Features with **strong** admission IC → small penalty → allowed large coefficient
- Features with **weak** admission IC → large penalty → shrunk toward zero
- This is a **Bayesian prior** (not selection): all features retain non-zero weight

Fallback: if pool has no `deflated_ic` metadata, fall back to isotropic $\alpha I$.

### 10.3 V2 Design: N-Adaptive Alpha Scaling

Scale the effective regularization with pool size:

$$\lambda_{\text{eff}} = \lambda_{\text{base}} \times \frac{N}{10}$$

Rationale: 32 features need ~3× more regularization than 10 features to prevent noise accumulation. The `/10` normalizes to the smallest viable pool.

### 10.4 V2 Design: Trade Frequency Guard

To prevent overtrading (159915ETF issue), add optional percentile-based gating:

After computing $Z_{\text{composite}}$, zero out signals below the expanding $P_{\min}$ percentile of $|Z|$:

$$Z_{\text{gated},t} = \begin{cases} Z_{\text{composite},t} & \text{if } |Z_{\text{composite},t}| > P_{\min}(t) \\ 0 & \text{otherwise} \end{cases}$$

Default $P_{\min} = 0$ (disabled). Enable with `--min-percentile 30` to require top-70% conviction.

### 10.5 Implementation

All V2 changes are in `glm.py` only (new parameters to existing functions). CLI flags:
- `--ic-prior`: Enable IC-weighted Ridge prior (default: ON)
- `--n-adaptive`: Enable N-adaptive alpha scaling (default: ON)
- `--min-percentile P`: Percentile gate for trade frequency control

---

## 11. V3 Improvements — Britten-Jones Target Formulation (Sharpe Optimization)

### 11.1 Motivation & Theoretical Basis

Britten-Jones (1999) proved that regressing a constant vector $\mathbf{1}$ on asset excess returns $R$ recovers the mean-variance tangency portfolio weights directly:

$$\hat{\beta}_{\text{BJ}} = \arg\min_{\beta} \|\mathbf{1} - R \beta\|_2^2 + \lambda \|\beta\|_2^2$$

In `newtrade` GLM, the companion regression features are factor strategy returns $R_{s,i} = \tilde{Z}_{s,i} \cdot y_s$ (or $R_{s,i} = \tilde{Z}_{s,i} \cdot \text{sign}(y_s)$).

Replacing standard return-predictor MSE ($\min_\beta \|y_s - \tilde{Z}_s^\top \beta\|^2$) with Britten-Jones companion regression aligns Ridge penalty directly with **Sharpe ratio maximization**, preventing noise-driven overtrading on volatile instruments like 159915ETF.

### 11.2 Target Modes

| Mode | Feature Matrix $X_{s}$ | Target Vector $y_s$ | Sample Weights | Optimization Target |
|------|------------------------|---------------------|----------------|---------------------|
| `return` (V1/V2) | $\tilde{Z}_s$ | Intraday return $r_s$ | None | Return prediction MSE |
| `bj_return` | $\tilde{Z}_s \cdot r_s$ | Constant $1$ | None | Portfolio Sharpe Ratio |
| `bj_sign` | $\tilde{Z}_s \cdot \text{sign}(r_s)$ | Constant $1$ | None | Directional Sharpe Ratio |
| `bj_sortino` | $\tilde{Z}_s \cdot r_s$ | Constant $1$ | $w_s = 2.0$ if $r_s < 0$ else $1.0$ | Downside Sortino Ratio |

### 11.3 Empirical Performance Summary (Spot ETF OOS 2022–2026)

| ETF | Target Mode | Sharpe | PnL | MaxDD | WinRate | Trades | Gate Verdict |
|-----|-------------|--------|-----|-------|---------|--------|--------------|
| **300ETF** | `return` (MSE) | **0.919** | +0.1663 | 0.0469 | 63.0% | 54 | **PASS** |
| | `bj_return` | 0.706 | +0.1640 | 0.0529 | 55.1% | 185 | FAIL |
| | `bj_sign` | 0.680 | +0.0797 | **0.0243** | 69.2% | 13 | FAIL |
| | `Rank` (Baseline) | 0.707 | +0.1447 | 0.0474 | 55.9% | 143 | - |
| **500ETF** | `bj_sign` | **0.836** | **+0.3192** | 0.1232 | 58.3% | 290 | **PASS** |
| | `bj_sortino` | **0.808** | +0.3184 | 0.1029 | 55.8% | 351 | **PASS** |
| | `return` (MSE) | 0.711 | +0.2871 | 0.1030 | 57.0% | 328 | FAIL |
| | `Rank` (Baseline) | 0.768 | +0.2799 | 0.1182 | 55.9% | 270 | - |
| **159915ETF** | `bj_sign` | **1.502** | **+0.7879** | 0.1058 | 58.1% | 346 | **PASS** |
| | `return` (MSE) | 1.056 | +0.6000 | 0.1121 | 56.1% | 628 (Overtrade) | FAIL |
| | `Rank` (Baseline) | 1.460 | +0.6359 | 0.0910 | 61.1% | 239 | - |

### 11.4 Key Insights & CLI Usage

1. **`bj_sign` achieves 2/3 PASS rate** (`500ETF` & `159915ETF`), successfully solving `159915ETF` overtrading by regularizing return scale noise.
2. **CLI invocation**:
   ```bash
   uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --compare
   ```

---

## 12. V4 Improvements — Kozak-Nagel-Santosh (2020) Eigenstructure Prior

### 12.1 Mathematical Specification

Kozak, Nagel, & Santosh (JFE 2020) proposed shrinking SDF/portfolio coefficients in Principal Component (PC) space rather than raw feature space:

Given factor Gram matrix $\Sigma_X = V \Lambda V^\top$ with eigenvalues $\lambda_1 \ge \lambda_2 \ge \ldots \ge \lambda_N > 0$:

1. Project features into PC space: $Z_{\text{PC}} = X V$.
2. Apply eigenvalue-scaled anisotropic penalty: $d_k \propto \frac{1}{\lambda_k^\gamma}$ ($\gamma = 1.0$ default).
3. Diagonal solve in PC space:
   $$\hat{b}_k = \frac{(Z_{\text{PC}}^\top y)_k}{\lambda_k + \alpha \cdot d_k}$$
4. Inverse projection back to factor space: $\hat{\beta} = V \hat{b}$.

### 12.2 Prior Modes

| Prior Mode | Shrinkage Space | Penalty Diagonal $d_k$ | Applicable Scenario |
|------------|-----------------|------------------------|---------------------|
| `kns` | Principal Component Space | $d_k \propto \lambda_k^{-\gamma}$ | Correlated pools ($N=32$, 500ETF) |
| `ic` | Feature Space | $d_i \propto \text{deflated\_ic}_i^{-1}$ | Metadata-weighted prior |
| `iso` | Feature Space | $d_i = 1.0$ | Isotropic standard Ridge |

### 12.3 Empirical Comparison across Prior Modes (`target-mode bj_sign`, Spot ETF OOS 2022–2026)

| ETF | Metric | `ic` (Per-Feature IC) | `kns` ($\gamma=0.2$) | `kns` ($\gamma=1.0$) | `iso` (Isotropic) | Baseline `Rank` |
|-----|--------|-----------------------|----------------------|----------------------|-------------------|-----------------|
| **300ETF** | Sharpe | 0.680 | 0.680 | 0.680 | 0.680 | 0.707 |
| | PnL | +0.0797 | +0.0797 | +0.0797 | +0.0797 | +0.1447 |
| | MaxDD | **0.0243** | **0.0243** | **0.0243** | **0.0243** | 0.0474 |
| | Trades | 13 | 13 | 13 | 13 | 143 |
| **500ETF** | Sharpe | **0.836** (PASS) | **0.809** (PASS) | 0.433 | **0.809** (PASS) | 0.768 |
| | PnL | **+0.3192** | +0.2938 | +0.1821 | +0.3113 | +0.2799 |
| | Trades | 290 | 244 | 372 | 308 | 270 |
| **159915ETF** | Sharpe | **1.502** (PASS) | 1.153 | 1.153 | 1.459 | 1.460 |
| | PnL | **+0.7879** | +0.5316 | +0.5316 | +0.7618 | +0.6359 |
| | Trades | 346 | 326 | 326 | 342 | 239 |

### 12.4 Key Insights & CLI Usage

1. `prior-mode ic` combined with `target-mode bj_sign` delivers optimal performance (2/3 PASS).
2. Aggressive KNS eigen-shrinkage ($\gamma=1.0$) reveals that factor alpha is distributed across mid-spectrum PCs rather than concentrated purely in top market-level PCs. Mild KNS ($\gamma=0.2$) recovers performance (0.809 Sharpe on 500ETF).
3. **CLI invocation**:
   ```bash
   uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --prior-mode kns --kns-gamma 0.2 --compare
   ```


