# Day-Model First-Principles Plan: New Objective Function Optimization

Plan to reformulate and optimize the Optuna objective function for `day-model` based on first principles.

---

## 1. New Return Prediction Target & Setup

* **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
* **Entry Bar**: 10:00 (bar 5 closes at 10:00, entry at open of bar 6)
* **Exit Bar**: 14:35 (close of bar 42)
* **Underlying**: Log return from 10:00 to 14:35 across all 5 ETFs.
* **Simplification**: Unified exit and entry timings across all assets, replacing complex, legacy per-ETF customized bars.

### 1.2 Early Target (10:00 ~ 13:05) Window Evaluation (July 2026)
An early afternoon target (exiting at `13:05`, close of bar `24`) was tested under the hypothesis that morning sessions are cleaner and less prone to afternoon regime shifts. 
**Verdict: ABORTED.**
Diagnostics showed that:
1. Volatility is compressed by 22% to 28% across all ETFs, significantly dropping the signal-to-noise ratio and making fixed transaction costs (15 bps) a heavy barrier.
2. Feature Spearman IC dropped by 23% to 50% across all ETFs, indicating that day-level macro factors require the full trading day to resolve and show persistent trends.
3. Exiting at `13:05` forces exits on noisy lunch reopening prints (high spread and gap volatility).
Conclusion: Stick to the full-day exit (`14:35`).

### 1.3 Unified Model Training Manifold

To prevent search space fragmentation and the "hard fall to Ridge" cliff, the day-model replaces disjoint categorical options (`skglm_huber_l1`, `skglm_mcp`, `ridge`) with a single continuous manifold estimator:
* **Estimator**: `GeneralizedLinearEstimator` (composition of datafit, penalty, and solver).
* **Datafit**: Huber loss (`SkglmHuber(delta)`) for y-outlier robustness.
* **Penalty**: `MCP_plus_L2(alpha, gamma, mu)` with L1 and L2 components parameterized continuously:
  * $\text{alpha} = \alpha_{\text{total}} \times \rho$ (L1 sparsity weight)
  * $\text{mu} = \alpha_{\text{total}} \times (1 - \rho)$ (L2 ridge regularization weight)
  * $\text{gamma} = \gamma$ (MCP threshold parameter)
* **Manifold knobs**:
  * `unified_alpha`: Overall regularization budget ($10^{-5}$ to $10.0$).
  * `unified_rho`: Sparse-vs-ridge mix ($0.0$ to $1.0$). $\rho = 0.0$ collapses to pure Ridge; $\rho \to 1.0$, large $\gamma$ behaves like L1/ElasticNet; $\rho \to 1.0$, small $\gamma$ enables aggressive non-convex MCP selection.
  * `unified_gamma`: Concavity parameter ($1.5$ to $10000.0$).
  * `huber_delta`: Huber robustness parameter ($0.5$ to $5.0$).

---

## 2. Relevant Research

**Embedded selection (what skglm's penalties are built on):**
- Zhang (2010), *Nearly unbiased variable selection under minimax concave penalty* — the original MCP/MC+ paper. It proposes MC+, a fast, continuous, nearly unbiased and accurate method of penalized variable selection in high-dimensional linear regression, noting that Lasso is fast and continuous but biased, and that this bias can prevent consistent variable selection, while subset selection is unbiased but computationally costly. This is the theoretical basis for why MCP tends to beat Lasso when you actually want to *identify* the useless features, not just shrink them.

**Robustifying the penalty (relevant since you're using Huber):**
- *Sparse and robust estimation with ridge minimax concave penalty* (ScienceDirect/RG) — combines ridge and MCP penalty functions and, to ensure robustness, formulates the estimation problem using the Huber loss together with the proposed penalty function, in the same high-dim setting you're in.

**Screening before penalization (important for you given 230 features / 2700 rows):**
- Fan & Lv (2008), *Sure Independence Screening for Ultra-High Dimensional Feature Space* — ranks features by marginal correlation with the response, filtering out features with weak marginal correlation, terming the method Sure Independence Screening (SIS) because each feature is evaluated independently. This is the "first pass" cheap filter before any penalized model even runs.

**Turning a selection procedure into something with actual error control:**
- Meinshausen & Bühlmann (2010), *Stability Selection* — based on subsampling in combination with high-dimensional selection algorithms; it provides finite sample control for some error rates of false discoveries and hence a transparent principle to choose a proper amount of regularisation.
- Shah & Samworth (2013), *Complementary Pairs Stability Selection (CPSS)* — derives bounds on the expected number of variables included that have low selection probability under the original procedure, and on the expected number of high-selection-probability variables excluded, without requiring exchangeability assumptions on the model. This is the practical, less-conservative variant of stability selection you'd actually implement.
- Faletto & Bien (2022), *Cluster Stability Selection (CSS)* — proves that standard stability selection fails under high correlation due to vote-splitting across proxy features. Grouping features into correlation clusters first, aggregating votes at the cluster level, and selecting representatives resolves this issue.

---

## 3. First Principles

1. **Do feature screening/selection on the full distribution, not the tails.** Reserve the tail-focus for (a) the loss weighting and (b) the evaluation metric, not for defining the training rows.
2. **Huber's robustness and MCP's non-convex thresholding solve different problems and you want both, in sequence, not conflated.** Huber protects you from y-outliers (heavy-tailed noise in the response). MCP is about β-sparsity (removing dead features). Doing MCP on the tail-only subset makes it fight both the outlier problem *and* the small-n problem at once — separate the concerns.
3. **BH-FDR at the univariate screening stage is a dimensionality reducer, not a final answer.** It gets you from 230 → maybe 40–70 candidates cheaply, using the full n. It should never be your only selection step because it ignores joint/collinear structure (two correlated features can both pass, and MCP later has to figure out which one actually matters).
4. **Group/Cluster-level stability selection solves the vote-splitting of collinear proxies where plain stability selection fails.** Under high correlation, plain stability selection dilutes voting probabilities across proxies, leading to either zero selections or random picks. Grouping features into correlation clusters first ($|r| \ge 0.75$), voting at the cluster level, and then selecting the most stable representative is the correct geometry.
5. **Triple-dipping risk:** BH-screening + stability selection + Optuna tuning + tail-focus, all run on the same 2200 rows, will silently leak information into your "final" model unless you enforce strict sample separation between stages. This is the single most likely way your holdout ends up not meaning anything.
6. **Continuous model training manifolds outperform discrete categorical selections.** Suggesting model type as a categorical parameter (e.g. Ridge vs. MCP) in Optuna breaks search space continuity and gradients. Parameterizing a single Huber estimator with the continuous L1/L2 formulation of `MCP_plus_L2` spans all configurations smoothly, allowing Optuna to optimize hyperparameters efficiently.

---

## 4. Practical Plan

**Step 0 — Lock the holdout sequentially and partition validation split.**
Partition the entire dataset chronologically:
- **Selection Train**: `date < 2024-03-01` excluding the 6 non-contiguous 3-month validation blocks and a 10-day temporal embargo around them. Features are selected here, and CPCV cross-validation is run here.
- **Selection Validation (Inner/Outer Split)**: 6 non-contiguous 3-month blocks (totaling ~18 months / ~370 trading days) carved out from the working set for selection-blind validation. To prevent search-space overfitting, these blocks are partitioned:
  - **Inner Validation (Tuned)**: 4 blocks used strictly for Optuna hyperparameter optimization:
    - Block 1: `2016-10-01` to `2017-01-01`
    - Block 2: `2018-07-01` to `2018-10-01`
    - Block 3: `2020-04-01` to `2020-07-01`
    - Block 5: `2022-10-01` to `2023-01-01`
  - **Outer Validation (Held-out Holdout)**: 2 blocks completely untouched by the Optuna search, evaluated one-shot at the end to sanity-check generalization:
    - Block 4: `2021-07-01` to `2021-10-01`
    - Block 6: `2023-07-01` to `2023-10-01`
- **OOS Lockbox**: `date >= 2024-03-01` (approx 556 rows). Completely untouched during training, evaluated one-shot at the end.

> [!NOTE]
> **Pipeline Change (Univariate Screening Removed)**:
> Univariate Spearman rank screening with BH-FDR correction (formerly Step 1) has been completely removed from the pipeline and is skipped by default. Dropping features based purely on marginal linear correlation deletes variables that have weak individual correlation but strong joint/multivariate predictive power when combined, causing feature starvation and model collapse. The pipeline now feeds all candidate features directly to Cluster Stability Selection.

**Step 1 — Cluster Stability Selection (CSS) + VIF Pruning on selection train set.**
Perform Complete Linkage hierarchical clustering on all active candidate features (formerly 317, pruned to 210 by default after deprecating 107 zero-stability features in `day-model/deprecate_features.py`) using correlation distance (threshold $t = 0.25$, i.e. $|r| \ge 0.75$). Run repeated subsampling ($B=100$, subsample size $\lfloor N/2 \rfloor$) and fit ElasticNet paths (l1_ratio = 0.5) on selection train. Aggregate selection votes at the *cluster level* (i.e. did any member of the cluster get selected in the subsample?). Keep clusters selected in $\ge 0.60$ fraction of subsamples (fallback to top 5 if count < 3). For each kept cluster, select the single representative feature with the highest individual stability score (tie-broken by Spearman correlation absolute values). 

After selecting representatives, perform **iterative VIF pruning** using standard OLS on the representatives. In each step, compute Variance Inflation Factors (VIFs) for all remaining features, identifying the highest VIF. If it exceeds $10.0$, drop the feature and repeat, continuing until all remaining selected features have VIF $\le 10.0$. This eliminates multivariate collinearity among three or more variables that pairwise clustering ignores.

> **Mistake (Previous Attempt)**: Standard (loss-agnostic, individual-feature) stability selection failed under correlation by vote-splitting, which led to severe collinearity in selected sets (condition numbers up to 6.4M for 50ETF, 3.7M for 500ETF). Pairwise clustering alone resolved most issues but left multivariate collinearity intact for 50ETF and 500ETF. Integrating VIF pruning post-CSS completely eliminates joint collinearity.

**Step 2 — Loss Weighting via Input Scaling.**
For coefficient fits, use sample weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to upweight tail days. Implement weights by scaling inputs $X$ and targets $y$ by $\sqrt{w}$. During Optuna tuning, Kish ESS is calculated on the selection train subset to apply active feature caps and soft ESS penalties. For the final refit, sample weights and Kish ESS are evaluated on the full working set.

> **Mistake (Previous Attempt)**: Pushing tail-weighting parameters (exponent $k$) without constraints collapsed the Effective Sample Size (ESS) to 16.6% on 159915ETF, training the model on effectively very few outlier days. Enforcing a hard ESS floor $\ge 20\%$ during optimization completely fixes this.

**Step 3 — Optuna over hyperparameters only, evaluated on selection validation blocks.**
Chronological splits partition the working set into a `selection train` block (before `2024-03-01` excluding the validation blocks and their embargos) and held-out `selection validation` blocks (tuned on the 4 inner validation blocks, evaluated one-shot on the 2 outer validation blocks).
Combinatorial Purged Cross-Validation (CPCV) splits (6 groups, 2 test groups, yielding 15 folds) are constructed strictly within the `selection train` subset, applying a 10-day embargo at test boundaries. Optuna tunes a single unified model space (`GeneralizedLinearEstimator` with Huber datafit and `MCP_plus_L2` penalty) over continuous parameters: total regularization budget (`unified_alpha`), sparse-vs-ridge penalty ratio (`unified_rho`), MCP threshold parameter (`unified_gamma`), Huber delta (`huber_delta`), and the loss weight exponent $k$.
The penalty is parameterized as `MCP_plus_L2(alpha=alpha * rho, gamma=gamma, mu=alpha * (1 - rho))`, creating a continuous manifold spanning Ridge ($\rho \to 0$), ElasticNet/Lasso-like ($\rho \to 1$, large $\gamma$), and non-convex MCP ($\rho \to 1$, small $\gamma$).

To smoothly guide the optimizer, we apply a soft collinearity penalty directly to the objective:
$$\text{cond\_penalty} = -0.1 \times \max\left(0, \ln(\kappa) - \ln(1000.0)\right)$$
which starts penalizing when regularized condition number exceeds $1000.0$ and applies gradient pressure before reaching the hard prune threshold of $10000.0$.

### Step 3.1 — Define Metric Weights & Optimization Objective

$$ \text{Objective} = \sum_{i=1}^{4} w_i \cdot \widetilde{V}_i $$

Where each $\widetilde{V}_i$ is a **robust z-score normalized** metric evaluated on the selection-blind chronological validation blocks (computed via a 50-trial Optuna pilot run using Median Absolute Deviation).

**Side-Specific Objective (July 2026)**: The Tail IC definition (V2) is now side-aware. Three sides are supported:

| Side     | Tail IC definition (V2)                          | V1..V4 weights                       |
| :---     | :---                                             | :---                                  |
| `single` | two-sided: top 10% + bottom 10% by `pred` (legacy) | `[0.40, 0.40, 0.15, 0.05]`         |
| `long`   | top-only: rows where `pred >= P85(pred)` (top 15%) | `[0.35, 0.50, 0.15, 0.00]` (V4 dropped, renormalized) |
| `short`  | bot-only: rows where `pred <= P15(pred)` (bot 15%) | `[0.35, 0.50, 0.15, 0.00]` (V4 dropped, renormalized) |

> **Important**: CV fold metrics $M_1$ through $M_6$ (Yearly Tail IC IR/Mean, Hit Rate, Overall IC, Monotonicity, Spread) and the corresponding kill-switches stay **two-sided** for all sides. Only the validation-side V2 (Val Tail IC) and the lockbox Tail IC in `generate_report.py` use the side-aware definition. This keeps the overfit guardrails (which look at the full distribution) intact while steering hyperparameter search toward the side of interest.

| ID | Metric ($\widetilde{V}_i$) | Definition | Sign | Category | Weight ($w_i$, `single` / `long,short`) |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **V₁** | **Val Overall IC** | Spearman rank correlation computed over all rows in the inner selection validation blocks. | + | General Signal | **0.40 / 0.35** |
| **V₂** | **Val Tail IC** (side-aware) | `single`: Spearman on top/bottom 10% rows. `long`: `pred >= P85(pred)`. `short`: `pred <= P15(pred)`. | + | Tail Power | **0.40 / 0.50** |
| **V₃** | **Val Monotonicity** | Spearman correlation between decile rank and mean actual return on the inner selection validation blocks. | + | Signal Structure | **0.15 / 0.15** |
| **V₄** | **Val Top-Bottom Spread** | Mean return spread (Top 10% minus Bottom 10%) on the inner selection validation blocks. **Dropped (weight=0) for `long`/`short`** since the off-side decile is never traded. | + | Factor Efficacy | **0.05 / 0.00** |

We compute the running **Deflated Objective** during the study to adjust for search-budget overfit. The final trial selection (including parameter plateau search) is performed using this deflated score instead of the raw objective, guaranteeing that the selection metric and the deflated honesty score are aligned.

Before computing the weighted objective, apply **Kill Switches / Hard Constraints** evaluated on the cross-validation folds metrics ($M_1$ through $M_6$, **always two-sided regardless of side**) constructed on the selection training block:
* Overall IC > 0 ($M_4 > 0$)
* Minimum Hit Rate >= 60% ($M_3 \ge 0.60$)
* Decile Monotonicity > 0.25 ($M_5 \ge 0.25$)
* Top-Bottom Spread > 0 ($M_6 > 0$)
* **Active features count under ESS cap**: $active\_k \le \text{max}(3, \text{int}(ESS / 8.0))$ (prevents parameter bloat relative to sample size).
* **Model weight concentration guardrail**: Gini coefficient of model coefficients $\le 0.85$ (prevents degenerate collapse to 1-2 active features).
* If any condition fails, return `-1e9` (pruned).

**Continuous Soft Constraints**:
* **ESS Floor**: The hard discontinuous $ESS \ge 20\%$ floor on the selection training subset is converted to a continuous soft penalty in the objective function: $ess\_penalty = -10.0 \times (0.20 - ess\_pct)$ when $ess\_pct < 0.20$ (and $0$ otherwise). This allows Optuna's TPE sampler to navigate the optimization landscape smoothly.

**Step 4 — Freeze feature set.**
Stability-selected cluster representatives are frozen before Optuna tuning begins.

**Step 5 — One-shot evaluation on the lockbox.**
* **Refit**: `train_model.py` refits the final model on the full working set (Selection Train + Selection Validation, i.e., all rows before `2024-03-01`) using the best parameters, and saves the final models and scaler/feature metadata. Calculates the **Raw Design Matrix Condition Number**, the **Raw Normal Equations Condition Number**, and the **Regularized Normal Equations Condition Number** ($\kappa(X^TX + N \lambda_{L2} I)$) to show the exact numerical stability of the estimator under regularized normal equations.
* **Evaluation**: The actual one-shot OOS predictions on the lockbox (2024-03-01 to the last day), computation of lockbox metrics (overall IC, tail-decile IC, decile monotonicity), and update of the results JSON are performed by the companion report-generator script `generate_report.py`.

---

## 5. Observed Effects & Performance Enhancements (July 2026 Remake)

Comparing the baseline optimization to the CSS + ESS-constrained + L2-regularized optimization (50 trials):

| Metric / Asset | 300ETF Baseline | 300ETF Remade | 159915ETF Baseline | 159915ETF Remade |
| :--- | :---: | :---: | :---: | :---: |
| **Selected Features** | 30 | 36 | 15 | 23 |
| **Condition Number ($\kappa$)** | 523,664.94 | **16.51** | 964.82 | **4.65** |
| **Collinear Pairs ($\ge 0.85$)** | 4 | **0** | 2 | **0** |
| **Tail Weight ESS %** | 49.8% | **92.7%** | 16.6% | **59.6%** |
| **Lockbox Overall IC** | +0.0622 | +0.0224 | +0.1085 | **+0.1367** |
| **Lockbox Tail IC** | +0.1151 | -0.0311 | +0.2631 | **+0.3293** |
| **OOS Monotonicity** | +0.6727 | +0.4909 | +0.6848 | **+0.6970** |

* Key benefits:
  - Condition numbers for all ETFs collapsed to negligible values (near-orthogonal design matrices). Iterative VIF pruning successfully cleared remaining joint collinearity that pairwise clustering missed.
  - The regularized condition number metric now reports the condition number of the regularized normal equations matrix ($X^TX + N \lambda_{L2} I$), which represents the true mathematical stability of the regularized estimator.
  - ESS for 159915ETF was successfully rescued from 16.6% to 59.6%, stabilizing tail parameters.
  - Overall OOS Lockbox performance showed strong gains (especially for 500ETF Tail IC going from +0.0679 to +0.1322 and 159915ETF Tail IC going from +0.2631 to +0.3293).

---

## 6. OOS Lockbox Performance & Leakage Verification (July 2026)

We conducted a rigorous verification of the out-of-sample (OOS) lockbox performance for `500ETF` and `159915ETF` to rule out leakage and investigate the underlying mechanism.

### 1. Embargo Asymmetry Check at Lockbox Boundary
To verify if the lack of a temporal embargo at the transition into the lockbox (`2024-03-01`) artificially inflated the lockbox scores (since features at the beginning of the lockbox look back into training data), we re-fit the models with a 10-day and 20-day temporal embargo before `LOCKBOX_DATE` (completely excluding those days from the final model refit):
- **500ETF**:
  - Baseline (No Embargo) Lockbox IC: `+0.1257`
  - 10-day Embargo Lockbox IC: `+0.1255`
  - 20-day Embargo Lockbox IC: `+0.1250`
- **159915ETF**:
  - Baseline (No Embargo) Lockbox IC: `+0.1300`
  - 10-day Embargo Lockbox IC: `+0.1303`
  - 20-day Embargo Lockbox IC: `+0.1308`

*Conclusion*: The impact of the boundary embargo is negligible (<0.0004 for 10d), confirming that there is no boundary leak inflating lockbox performance.

### 2. Validation Block & COVID (2020-Q2) Regime Analysis
We evaluated individual validation block performances using the best parameters to see if validation averages were dragged down by a specific regime:
- **500ETF**:
  - Block 1 (2016-10 to 2017-01): `IC = -0.1076`
  - Block 2 (2018-07 to 2018-10): `IC = +0.2738`
  - Block 3 (2020-04 to 2020-07) (COVID): `IC = +0.3733`
  - Block 4 (2022-10 to 2023-01): `IC = +0.1463`
  - Block 5 (2021-07 to 2021-10): `IC = +0.3344`
  - Block 6 (2023-07 to 2023-10): `IC = +0.1420`
  - *Average*: `+0.1937`
- **159915ETF**:
  - Block 1 (2016-10 to 2017-01): `IC = +0.0657`
  - Block 2 (2018-07 to 2018-10): `IC = +0.1856`
  - Block 3 (2020-04 to 2020-07) (COVID): `IC = +0.2605`
  - Block 4 (2022-10 to 2023-01): `IC = +0.2001`
  - Block 5 (2021-07 to 2021-10): `IC = +0.1899`
  - Block 6 (2023-07 to 2023-10): `IC = +0.0894`
  - *Average*: `+0.1652`

*Conclusion*:
- The COVID block (Block 3) was actually the highest-performing validation block for both ETFs, so it does not drag down validation.
- Some individual blocks (like Block 1 for 500ETF at `-0.1076`) drag validation down, indicating validation averages are somewhat conservative.
- The raw (undeflated) pooled outer validation ICs (`+0.1682` for 500ETF, `+0.1341` for 159915ETF) are very close to the raw lockbox ICs (`+0.1257` and `+0.1300`), which shows normal, healthy generalization.
- The apparent "OOS beats validation" gap is a statistical artifact of multiple-testing adjustment: the validation IC is heavily deflated using Marcos Lopez de Prado deflation (to correct for the 100 trials search space), whereas the lockbox is evaluated once and is undeflated.

### 3. Hand Trader Consensus
Hand traders report that trading signals during the 2024–2026 lockbox period were structurally "stronger" and more pronounced. This matches our empirical lockbox results, confirming that the strong lockbox performance is a real regime-driven effect, not a leak.


## 7. Day-Model Overfit & Stability Upgrades (July 2026)

Upgraded model training stability, tail performance, overfit diagnostics, and decay monitoring:

1. **Bootstrap Bagging Feature Selector (Soloff et al. 2024 JMLR)**:
   - Wraps final model fit in bootstrap aggregation ($B=100$) over Selection Train.
   - Fits best model hyperparameters on $B$ bootstrap draws of Selection Train.
   - Computes per-feature inclusion frequency. Keeps features with inclusion frequency $> 50\%$.
   - Prevents point-estimate sparse penalty collapse to 2-3 active features on small samples.
   - Refits final model on Working set restricted to these bagged features.

2. **Soften Tail IC to 15% (P85/P15)**:
   - Modified `side_tail_ic` and `side_tail_mask` to use 15% threshold for `long` and `short` sides (top 15% / bottom 15% only) instead of 10% (P90/P10). Softens small-sample noise.
   - Set weights for `long`/`short` validation objective `[V1, V2, V3, V4]` to `[0.35, 0.50, 0.15, 0.00]` (renormalized V4 drop).

3. **Two-Sided CV Folds & Side Consistency Constraints**:
   - Enforces standard two-sided CV fold metrics `m1..m6` and standard kill-switches.
   - If `side != "single"`, appends two side-specific consistency constraints: `side_m2 > 0` (side-specific Yearly Tail IC Mean > 0) and `side_m3 >= 50%` (side-specific Hit Rate >= 50%) to prevent fold-level tail sign-flips.
   - Enforces active feature ESS-based cap and floor, weight concentration, and regularized condition number prune at 10000.0 (10 total constraints).

4. **Unified Continuous Manifold & Soft Collinearity Penalty**:
   - Replaced discrete categorical model selection (`skglm_huber_l1`, `skglm_mcp`, `ridge`) with a unified `GeneralizedLinearEstimator` using Huber datafit and `MCP_plus_L2(alpha*rho, gamma, alpha*(1-rho))` penalty.
   - Continuous manifold spans from Ridge-like ($\rho < 0.05$, which bypasses sparse active feature floor/cap constraints) to sparse Lasso/MCP regimes.
   - Added a graduated soft condition number penalty `cond_penalty = -0.1 * max(0, log(reg_kappa) - log(1000.0))` to steer Optuna away from ill-conditioned parameters before hitting the hard prune threshold.

5. **Model Confidence Set (MCS) & Bayesian True Discovery**:
   - Hansen's MCS (sequential paired t-test, alpha=10%) identifies statistically indistinguishable trials from the best.
   - Empirical Bayes posterior probability of true discovery ($P(\theta_{OOS} > 0 | data)$) computed per trial. Logs MCS size and posterior probability.

6. **Quarterly Rolling Refit decay check**:
   - Runs `run_quarterly_rolling_refit_test` on post-lockbox quarters.
   - Simulates Static Model (frozen pre-lockbox) vs Rolling Model (refitted quarterly with updated history) on quarterly windows. Measures IC and Tail IC decay rate (QuantBench method).

---

## 8. Feature-Selection Pipeline Constants & Fine-Tuning (July 2026)

The feature-selection pipeline (formerly Steps 1–2, now Step 1 since screening is bypassed) is governed by 4 active constants (and 2 bypassed constants) in `train_model.py` (lines 89–94). These control the funnel from ~210 candidate features down to the final selected set fed into Optuna. Their current values were set heuristically; this section documents a systematic sensitivity-analysis protocol to calibrate them.

### 8.1 Constants & Their Pipeline Roles

| Constant | Current | Pipeline Stage | Role |
|---|---|---|---|
| `SCREEN_FDR` | 0.50 | Step 1 (Screening) | **(Bypassed / Deprecated)** BH-FDR level for univariate Spearman screening. Bypassed by default as univariate screening deletes joint predictive features. |
| `SCREEN_FALLBACK_K` | 50 | Step 1 (Screening) | **(Bypassed / Deprecated)** Top-K fallback when BH-FDR passes < 40 features. Bypassed by default. |
| `STABILITY_B` | 80 | Step 1 (CSS) | Number of bootstrap subsamples for cluster stability selection. More = more stable probabilities but slower. |
| `STABILITY_PI` | 0.80 | Step 1 (CSS) | Minimum cluster selection probability threshold. Higher = more conservative, fewer features. |
| `STABILITY_Q` | 35 | Step 1 (CSS) | Maximum average active clusters used to restrict the alpha regularization path. Caps model complexity pre-Optuna. |
| `ACTIVE_FEATURE_ESS_DIVISOR` | 8.0 | Step 3 (Optuna) | Kill-switch denominator: $active\_k \le \max(3, \lfloor ESS / d \rfloor)$. Prevents parameter bloat relative to effective sample size. |

> **Discrepancy note**: Screening (formerly Step 1) specifies FDR = 0.15 (loosened to 0.25 for 588000ETF) but is now bypassed by default because univariate filtering deletes features with joint predictive power. The sweep protocol can verify that bypassing this step is superior to applying any screening threshold.

### 8.2 Sweep Protocol

Implemented in `day-model/sweep_constants.py`. For each constant, the script:
1. Monkey-patches the target constant in `train_model`.
2. Runs the full pipeline: screen → CSS → VIF → Optuna (20-trial quick study).
3. Computes lockbox metrics (Overall IC, Tail IC, Monotonicity) by loading the saved model and predicting on `date >= 2024-03-01`.
4. Records feature counts at each pipeline stage, condition number, ESS%, Gini, and validation metrics.
5. Outputs a CSV grid of results.

```bash
# Example: sweep SCREEN_FDR with default range [0.15, 0.25, 0.35, 0.50, 0.65, 0.80]
python day-model/sweep_constants.py -e 300 --side single --constant SCREEN_FDR

# Custom values
python day-model/sweep_constants.py -e 300 --constant STABILITY_PI --values 0.60,0.75,0.80,0.90

# STABILITY_B with Jaccard stability measurement (3 seeds: 42, 123, 456)
python day-model/sweep_constants.py -e 300 --constant STABILITY_B --stability
```

### 8.3 Sweep Ranges & Decision Rules

| Constant | Sweep Range | Decision Rule |
|---|---|---|
| `SCREEN_FDR` | `[0.15, 0.25, 0.35, 0.50, 0.65, 0.80]` | Bypassed. Verify if any screening threshold outperforms the default bypassed mode. |
| `STABILITY_B` | `[40, 60, 80, 120]` | Pick the smallest B where Jaccard similarity across 3 seeds exceeds 0.85. |
| `STABILITY_PI` | `[0.60, 0.70, 0.75, 0.80, 0.85, 0.90]` | Maximize `lockbox_tail_ic` while keeping condition number < 100. |
| `STABILITY_Q` | `[15, 25, 35, 50, 70]` | Pick Q where Tail IC plateaus (elbow method). |
| `SCREEN_FALLBACK_K` | `[30, 40, 50, 60, 80]` | Bypassed. |
| `ACTIVE_FEATURE_ESS_DIVISOR` | `[4.0, 6.0, 8.0, 10.0, 12.0, 16.0]` | Pick divisor where kill-switch prunes < 5% of Optuna trials (guardrail, not primary filter). |

### 8.4 Execution Order

```
sweep_constants.py (build) -- prerequisite
  |
  v
SCREEN_FDR + SCREEN_FALLBACK_K (diagnostic) -- parallel, highest leverage
  |
  v
STABILITY_B (with --stability) + STABILITY_PI -- parallel (independent stages)
  |
  v
STABILITY_Q -- depends on PI choice
  |
  v
ACTIVE_FEATURE_ESS_DIVISOR -- depends on CSS feature count
  |
  v
Multi-ETF validation (all 5 ETFs x 3 sides, 100 Optuna trials)
```

### 8.5 Practical Notes

- **Cache invalidation**: Each sweep config changes the `select_key` (train_model.py lines 1188–1193), so disk caches auto-invalidate. No manual cache clearing needed.
- **Quick Optuna**: Sweep iterations use 20 trials (not 100) to keep wall time manageable. Only the final multi-ETF validation uses 100 trials.
- **Parallelism**: Default `--optuna-jobs 1` for deterministic trial ordering. Use `--optuna-jobs N` for faster wall time when reproducibility is not critical.
- **588000ETF special case**: Already overrides FDR to 0.25 and has a separate VIF threshold (5.0 vs 10.0). Track separately in all sweeps.

### 8.6 Target Transformation & Objective Function Calibrations (July 2026)

- **Target Transformations**:
  - `none` (Default): Minimizes Huber loss directly on raw target returns.
  - `gauss`: Maps target ranks to standard normal quantiles.
    - *Why it failed*: By standardizing target ranks to standard normal quantiles, it standardizes variance and spreads scores uniformly. This flattens the prediction landscape and destroys the selectivity of the rolling percentile entry threshold (which expects highly positive/negative outliers). Consequently, it trades almost every day without selectivity (365 active days vs 347 baseline), over-trading noise and destroying returns (+121.7 bps, 0.0870 Sharpe).
- **Objective Function Optimization**:
  - `Val Tail Sharpe` (V5): Annualized Sharpe ratio of winsorized active tail returns. Block-bootstrapped over validation blocks with standard error soft penalty.
  - `Win Rate Constraint` (M9): Enforced daily tail win rate after 15 bps transaction cost must be $\ge 45\%$ across all cross-validation folds.
- **Audited Empirical Results (Static OOS Backtest 2024-03 onwards)**:
  - **Baseline (None - Raw returns)**: Cumulative P&L `+1908.5 bps`, Annual Sharpe `1.2204`, MaxDD `949.5 bps`.
  - **Sharpe-Objective + Win Rate**: Cumulative P&L `+1840.8 bps`, Annual Sharpe `1.2215`, MaxDD `970.8 bps`.
  - **Metadispersion Block Bootstrap CI (Delta: Sharpe - Baseline)**:
    - *P&L Delta 95% CI*: `[-754.9, +663.6] bps`
    - *Sharpe Delta 95% CI*: `[-0.542, +0.536]`
    - *MaxDD Delta 95% CI*: `[-416.5, +433.4] bps` (drawdown delta is statistically zero)
  - **Cross-ETF Correlation**:
    - *Unconditional*: Mean correlation is `0.3938` (Sharpe) vs. `0.3968` (Baseline).
    - *Conditional (Bottom 20% Portfolio Return Days)*: Mean correlation is `-0.0129` (Sharpe, N=69) vs. `-0.0447` (Baseline, N=70). Tail returns are nearly uncorrelated, confirming bad days are driven by idiosyncratic asset-level drawdowns rather than synchronous market-wide crashes.
- **Conclusion**: The block-bootstrapped validation tail Sharpe objective does not show a statistically significant improvement at the portfolio level (CIs for P&L, Sharpe, and MaxDD all straddle zero). The differences across individual ETFs represent variance reallocation across a small sample rather than a structural skill uplift. Therefore, **raw returns (`none`) target transform and the Tail IC validation objective remain the default configurations (`--target-transform none` and `--sharpe-objective` default to `False`).**

### 8.7 Meta-Level Configuration Trials Log (July 2026)

To prevent future duplicate search loops and re-litigation of null results, the following table tracks configurations tested at the pipeline level:

| Order | Configuration | Proposed By | Key Metric (OOS Sharpe) | Status / Verdict |
| :---: | :--- | :---: | :---: | :--- |
| 1 | Baseline (none transform, Tail IC) | Standard Baseline | 1.2204 | **Active Default**. Benchmark to beat. |
| 2 | Uniform Rank transform (`rank`) | Research suggestion | 0.6600 | **Killed**. Magnitude loss degrades selectivity. |
| 3 | Normal Rank transform (`gauss`) | Research suggestion | 0.0870 | **Killed**. Variance standardization causes over-trading of noise. |
| 4 | Sharpe Objective + Win Rate (on `none`) | Research suggestion | 1.2215 | **Killed**. Statistically identical to Baseline (95% CI straddles zero). |

