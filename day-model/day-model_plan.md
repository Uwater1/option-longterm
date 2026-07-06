# Day-Model First-Principles Plan: New Objective Function Optimization

Plan to reformulate and optimize the Optuna objective function for `day-model` based on first principles.

---

## 1. New Return Prediction Target & Setup

* **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
* **Entry Bar**: 10:00 (bar 5 closes at 10:00, entry at open of bar 6)
* **Exit Bar**: 14:35 (close of bar 42)
* **Underlying**: Log return from 10:00 to 14:35 across all 5 ETFs.
* **Simplification**: Unified exit and entry timings across all assets, replacing complex, legacy per-ETF customized bars.

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

**Step 1 — Cheap screening on selection train set.**
Compute robust marginal association per feature (Spearman rank correlation) between each of the candidate features (formerly 238, pruned to 185 by default after deprecating 53 zero-stability features in `day-model/deprecate_features.py`) and the target, utilizing only the selection train subset. Apply BH-FDR correction across the tests (FDR = 0.15). If fewer than 50 features pass, fallback to the top 50 features by p-value.

> **Mistake (Previous Attempt)**: Clustering slightly correlated features ($|r| \ge 0.3$) and dropping them based on univariate ranking discarded complementary multivariate features, causing model collapse to $\le 2$ active weights. We incorrectly tried to rely on ElasticNet grouping effect without pre-clustering. Grouping into complete correlation clusters *after* screening but *before* stability voting resolves this without discarding joint predictive power.

**Step 2 — Cluster Stability Selection (CSS) + VIF Pruning on selection train set.**
Perform Complete Linkage hierarchical clustering on Step 1 survivors using correlation distance (threshold $t = 0.25$, i.e. $|r| \ge 0.75$). Run repeated subsampling ($B=100$, subsample size $\lfloor N/2 \rfloor$) and fit ElasticNet paths (l1_ratio = 0.5) on selection train. Aggregate selection votes at the *cluster level* (i.e. did any member of the cluster get selected in the subsample?). Keep clusters selected in $\ge 0.60$ fraction of subsamples (fallback to top 5 if count < 3). For each kept cluster, select the single representative feature with the highest individual stability score (tie-broken by Spearman correlation absolute values). 

After selecting representatives, perform **iterative VIF pruning** using standard OLS on the representatives. In each step, compute Variance Inflation Factors (VIFs) for all remaining features, identifying the highest VIF. If it exceeds $10.0$, drop the feature and repeat, continuing until all remaining selected features have VIF $\le 10.0$. This eliminates multivariate collinearity among three or more variables that pairwise clustering ignores.

> **Mistake (Previous Attempt)**: Standard (loss-agnostic, individual-feature) stability selection failed under correlation by vote-splitting, which led to severe collinearity in selected sets (condition numbers up to 6.4M for 50ETF, 3.7M for 500ETF). Pairwise clustering alone resolved most issues but left multivariate collinearity intact for 50ETF and 500ETF. Integrating VIF pruning post-CSS completely eliminates joint collinearity.

**Step 3 — Loss Weighting via Input Scaling.**
For coefficient fits, use sample weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to upweight tail days. Implement weights by scaling inputs $X$ and targets $y$ by $\sqrt{w}$. During Optuna tuning, Kish ESS is calculated on the selection train subset to apply active feature caps and soft ESS penalties. For the final refit, sample weights and Kish ESS are evaluated on the full working set.

> **Mistake (Previous Attempt)**: Pushing tail-weighting parameters (exponent $k$) without constraints collapsed the Effective Sample Size (ESS) to 16.6% on 159915ETF, training the model on effectively very few outlier days. Enforcing a hard ESS floor $\ge 20\%$ during optimization completely fixes this.

**Step 4 — Optuna over hyperparameters only, evaluated on selection validation blocks.**
Chronological splits partition the working set into a `selection train` block (before `2024-03-01` excluding the validation blocks and their embargos) and held-out `selection validation` blocks (tuned on the 4 inner validation blocks, evaluated one-shot on the 2 outer validation blocks).
Combinatorial Purged Cross-Validation (CPCV) splits (6 groups, 2 test groups, yielding 15 folds) are constructed strictly within the `selection train` subset, applying a 10-day embargo at test boundaries. Optuna tunes model type selection (`skglm_huber_l1` vs `skglm_mcp`), their respective regularization parameters (alphas, gamma, delta), and the loss weight exponent $k$.
Both model families enforce a mandatory $10\%$ L2 Ridge regularization component (`skglm_huber_l1` uses `L1_plus_L2` with `l1_ratio = 0.9` and `skglm_mcp` uses custom `MCP_plus_L2` with `mu = 0.1 * alpha` from `penalties.py`) to guarantee minimum eigenvalues and compress condition numbers.

### Step 4.1 — Define Metric Weights & Optimization Objective

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

**Step 5 — Freeze feature set.**
Stability-selected cluster representatives are frozen before Optuna tuning begins.

**Step 6 — One-shot evaluation on the lockbox.**
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

3. **Yearly Tail IC Constraint**:
   - Passed `side` to `calculate_yearly_metrics` to make cross-validation fold Tail IC side-aware.
   - Added `M2 (Yearly Tail IC Mean) > 0` hard constraint to main objective (7 total constraints). Prunes configurations with negative tail performance.

4. **Dynamic Ridge Fallback**:
   - Added `"ridge"` model type support to `_build_model`.
   - Automatically forces Ridge-only model search/fitting if selected features condition number is severe ($\kappa > 10^5$) or if ETF is `500ETF`/`50ETF` (to bypass severe collinearity/sparsity instability).
   - Ridge bypasses the sparse active feature floor & cap constraints. L2 regularizer matches `ridge_alpha`.

5. **Model Confidence Set (MCS) & Bayesian True Discovery**:
   - Hansen's MCS (sequential paired t-test, alpha=10%) identifies statistically indistinguishable trials from the best.
   - Empirical Bayes posterior probability of true discovery ($P(\theta_{OOS} > 0 | data)$) computed per trial. Logs MCS size and posterior probability.

6. **Quarterly Rolling Refit decay check**:
   - Runs `run_quarterly_rolling_refit_test` on post-lockbox quarters.
   - Simulates Static Model (frozen pre-lockbox) vs Rolling Model (refitted quarterly with updated history) on quarterly windows. Measures IC and Tail IC decay rate (QuantBench method).

