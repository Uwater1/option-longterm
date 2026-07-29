# Scheme 5 — Simple Linear GLM (Expanding Ridge with Britten-Jones Target)

## 1. Objective & Current Setting

Replace fixed-weight composite schemes with a **learned linear combination** that adapts over time. Scheme 5 fits an expanding-window regularized linear model on sign-aligned z-scored factors without lookahead.

### Current Production & Research Setup:
- **Target Formulation**: Britten-Jones Directional Sharpe Regression (`--target-mode bj_sign`). Regresses constant vector $\mathbf{1}$ on direction-scaled features $X_s = \tilde{Z}_s \cdot \text{sign}(r_s)$, aligning Ridge penalization directly with Sharpe Ratio maximization.
- **Prior Formulation**: IC-Weighted Ridge Prior (`--prior-mode ic`). Scales regularization per feature inversely with its admission `deflated_ic`, shrinking weak factors while allowing strong factors larger weights.
- **Coefficient Constraint**: Non-negative coefficient clamp ($\hat{\beta}_{i,t} = \max(0, \hat{\beta}_{i,t})$), ensuring all sign-aligned factors contribute non-negatively.
- **Downstream Feature Selection Policy**: **No downstream feature selection or stability gate inside GLM.** All factor admission and filtering are handled upstream in `day-model-new` gates. Downstream stability pre-filtering was empirically proven to degrade OOS performance (500ETF Sharpe dropped from 0.836 to 0.607) by removing beneficial signal diversification across admitted pools.

---

## 2. Mathematical Specification

### 2.1 Input

At each day $t$, the input is the sign-aligned z-scored matrix:

$$\tilde{Z}_{i,t} = z_{i,t} \times \text{sign}_i, \quad i = 1 \ldots N$$

where $z_{i,t}$ is the expanding-window z-score (computed zero-lookahead from past history $[0, t-1]$).

### 2.2 Britten-Jones Target & IC-Weighted Ridge Fit

For day $t$, fit on expanding window $[0, t-1]$:

$$\hat{\beta}_t = \arg\min_{\beta} \|\mathbf{1} - X_{\text{BJ}, :t-1} \beta\|_2^2 + \lambda \sum_{i=1}^N d_i \beta_i^2$$

where:
- $X_{\text{BJ}, s} = \tilde{Z}_s \times \text{sign}(r_{\text{trade}, s})$
- $d_i = \frac{1}{\text{deflated\_ic}_i} \Big/ \text{mean}\left(\frac{1}{\text{deflated\_ic}}\right)$ (normalized IC penalty diagonal)
- $\lambda = \lambda_{\text{base}} \times \frac{N}{10}$ (N-adaptive regularization scaling)
- $\beta_i \ge 0$ (non-negative soft clamp)

### 2.3 Composite Signal

$$Z_{\text{composite},t} = \tilde{Z}_t^\top \hat{\beta}_t$$

The output $Z_{\text{composite}}$ is expanding-standardized to unit variance and fed directly into `generate_positions()`.

---

## 3. Downstream Feature Selection Policy: Why No Stability Gate

Empirical evaluation proved that adding downstream stability selection (via `skglm` time-block subsampling or rolling IC gates) inside `newtrade` **degrades out-of-sample performance**:

| ETF | Raw Admitted Pool (`bj_sign`) | With Downstream Stability Select ($\tau=0.50$) | Impact |
|-----|-------------------------------|------------------------------------------------|--------|
| **300ETF** | Sharpe 0.680, PnL +0.0797 | Sharpe 0.652, PnL +0.1163 | Degraded Sharpe |
| **500ETF** | **Sharpe 0.836, PnL +0.3192** | Sharpe 0.607, PnL +0.2067 | Severe Signal Loss (-0.229 SR) |
| **159915ETF** | **Sharpe 1.502, PnL +0.7879** | Sharpe 1.199, PnL +0.6020 | Severe Signal Loss (-0.303 SR) |

**Root Cause**: Upstream `day-model-new` gates already apply strict pre-correlation quality screening, rolling monotonicity checks, jackknife sign stabilization, and dendrogram correlation pruning. The remaining $N \approx 10\text{--}32$ features form a clean, non-redundant signal pool. Adding secondary downstream stability filtering causes over-pruning and destroys signal diversification.

---

## 4. Empirical Acceptance Gate Results & Adoption Verdict

Per `plan_glm.md` §5, GLM is evaluated against Scheme 4 (Rank Bounded Weight baseline) on the standard OOS window (`2022-01-01 ~ 2026-01-01`):

### 4.1 OOS Results Table (Spot ETF Mode)

| ETF | GLM Sharpe | Rank Sharpe | GLM PnL | Rank PnL | GLM MaxDD | Rank MaxDD | GLM WR | Rank WR | Gate Verdict |
|-----|------------|-------------|---------|----------|-----------|------------|--------|---------|--------------|
| **300ETF** | 0.680 | **0.687** | +0.0797 | **+0.1240** | **0.0243** | 0.0603 | **69.2%** | 55.6% | **FAIL** (PnL < 0.8×Rank) |
| **500ETF** | **0.836** | 0.806 | **+0.3192** | +0.2780 | **0.1232** | 0.1547 | **58.3%** | 57.6% | **PASS** |
| **159915ETF** | **1.502** | 1.456 | **+0.7879** | +0.6210 | 0.1058 | **0.0885** | 58.1% | **61.1%** | **PASS** |
| **50ETF** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIP (<10 features) |
| **588000ETF** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | SKIP (<10 features) |

### 4.2 Global Adoption Verdict: REJECTED

- **Global Adoption Rule**: Requires $\ge 3$ active ETFs to PASS. Achieved 2/3 PASS.
- **Global Primary Scheme**: Retain **Rank Bounded Weight (`--scheme rank` / `icw`)** as the primary default across the framework.
- **Per-ETF Allocation**: GLM is **production-viable for 500ETF and 159915ETF**, but **NOT** for 300ETF (where Rank remains primary).

---

## 5. Usage & Verification Commands

```bash
# Run standard GLM backtest with Britten-Jones Sharpe target and compare against Rank
uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --compare

# Run GLM on Index Futures (IF88 / IC88)
uv run python newtrade/glm_backtest.py -e all --target-mode bj_sign --compare --future
```
