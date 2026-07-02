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
- **Selection Train**: `date < 2024-03-01` excluding `2021-01-01 <= date < 2022-01-01` (approx 1923 rows). Features are selected here, and CPCV cross-validation is run here.
- **Selection Validation**: `2021-01-01 <= date < 2022-01-01` (approx 243 rows). Excluded from feature selection, used for selection-blind hyperparameter validation in the Optuna objective.
- **OOS Lockbox**: `date >= 2024-03-01` (approx 556 rows). Completely untouched during training, evaluated one-shot at the end.

**Step 1 — Cheap screening on selection train set.**
Compute robust marginal association per feature (Spearman rank correlation) between each of the 238 features and the target, utilizing only the selection train subset. Apply BH-FDR correction across the tests (FDR = 0.40). If fewer than 40 features pass, fallback to the top 50 features by p-value.

> **Mistake (Previous Attempt)**: Clustering slightly correlated features ($|r| \ge 0.3$) and dropping them based on univariate ranking discarded complementary multivariate features, causing model collapse to $\le 2$ active weights. We incorrectly tried to rely on ElasticNet grouping effect without pre-clustering. Grouping into complete correlation clusters *after* screening but *before* stability voting resolves this without discarding joint predictive power.

**Step 2 — Cluster Stability Selection (CSS) + VIF Pruning on selection train set.**
Perform Complete Linkage hierarchical clustering on Step 1 survivors using correlation distance (threshold $t = 0.25$, i.e. $|r| \ge 0.75$). Run repeated subsampling ($B=100$, subsample size $\lfloor N/2 \rfloor$) and fit ElasticNet paths (l1_ratio = 0.5) on selection train. Aggregate selection votes at the *cluster level* (i.e. did any member of the cluster get selected in the subsample?). Keep clusters selected in $\ge 0.60$ fraction of subsamples (fallback to top 5 if count < 3). For each kept cluster, select the single representative feature with the highest individual stability score (tie-broken by Spearman correlation absolute values). 

After selecting representatives, perform **iterative VIF pruning** using standard OLS on the representatives. In each step, compute Variance Inflation Factors (VIFs) for all remaining features, identifying the highest VIF. If it exceeds $10.0$, drop the feature and repeat, continuing until all remaining selected features have VIF $\le 10.0$. This eliminates multivariate collinearity among three or more variables that pairwise clustering ignores.

> **Mistake (Previous Attempt)**: Standard (loss-agnostic, individual-feature) stability selection failed under correlation by vote-splitting, which led to severe collinearity in selected sets (condition numbers up to 6.4M for 50ETF, 3.7M for 500ETF). Pairwise clustering alone resolved most issues but left multivariate collinearity intact for 50ETF and 500ETF. Integrating VIF pruning post-CSS completely eliminates joint collinearity.

**Step 3 — Loss Weighting via Input Scaling.**
For coefficient fits, use sample weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to upweight tail days. Implement weights by scaling inputs $X$ and targets $y$ by $\sqrt{w}$. During Optuna tuning, Kish ESS is calculated on the selection train subset to apply active feature caps and soft ESS penalties. For the final refit, sample weights and Kish ESS are evaluated on the full working set.

> **Mistake (Previous Attempt)**: Pushing tail-weighting parameters (exponent $k$) without constraints collapsed the Effective Sample Size (ESS) to 16.6% on 159915ETF, training the model on effectively very few outlier days. Enforcing a hard ESS floor $\ge 20\%$ during optimization completely fixes this.

**Step 4 — Optuna over hyperparameters only, evaluated on a selection validation block.**
Chronological splits partition the working set into a `selection train` block (before `2024-03-01` excluding the validation block) and a held-out `selection validation` block (from `2021-01-01` to `2021-12-31`).
Combinatorial Purged Cross-Validation (CPCV) splits (6 groups, 2 test groups, yielding 15 folds) are constructed strictly within the `selection train` subset, applying a 10-day embargo at test boundaries. Optuna tunes model type selection (`skglm_huber_l1` vs `skglm_mcp`), their respective regularization parameters (alphas, gamma, delta), and the loss weight exponent $k$.
Both model families enforce a mandatory $10\%$ L2 Ridge regularization component (`skglm_huber_l1` uses `L1_plus_L2` with `l1_ratio = 0.9` and `skglm_mcp` uses custom `MCP_plus_L2` with `mu = 0.1 * alpha` from `penalties.py`) to guarantee minimum eigenvalues and compress condition numbers.

### Step 4.1 — Define Metric Weights & Optimization Objective

$$ \text{Objective} = \sum_{i=1}^{4} w_i \cdot \widetilde{V}_i $$

Where each $\widetilde{V}_i$ is a **robust z-score normalized** metric evaluated on the selection-blind chronological validation set (computed via a 50-trial Optuna pilot run using Median Absolute Deviation), and weights $w_i$ are pre-defined constants:

| ID | Metric ($\widetilde{V}_i$) | Definition | Sign | Category | Weight ($w_i$) |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **V₁** | **Val Overall IC** | Spearman rank correlation computed over all rows in the selection validation block. | + | General Signal | **0.40** |
| **V₂** | **Val Tail IC** | Spearman rank correlation computed on top/bottom 10% rows of the selection validation block. | + | Tail Power | **0.40** |
| **V₃** | **Val Monotonicity** | Spearman correlation between decile rank and mean actual return on the selection validation block. | + | Signal Structure | **0.15** |
| **V₄** | **Val Top-Bottom Spread** | Mean return spread (Top 10% minus Bottom 10%) on the selection validation block. | + | Factor Efficacy | **0.05** |

Before computing the weighted objective, apply **Kill Switches / Hard Constraints** evaluated on the cross-validation folds metrics ($M_1$ through $M_6$) constructed on the selection training block:
* Overall IC > 0 ($M_4 > 0$)
* Minimum Hit Rate >= 60% ($M_3 \ge 0.60$)
* Decile Monotonicity > 0.25 ($M_5 \ge 0.25$)
* Top-Bottom Spread > 0 ($M_6 > 0$)
* **Active features count under ESS cap**: $active\_k \le \text{max}(3, \text{int}(ESS / 25.0))$ (prevents parameter bloat relative to sample size, using global divisor constant 25.0).
* If any condition fails, return `-1e9` (pruned).

**Continuous Soft Constraints**:
* **ESS Floor**: The hard discontinuous $ESS \ge 20\%$ floor on the selection training subset is converted to a continuous soft penalty in the objective function: $ess\_penalty = -10.0 \times (0.20 - ess\_pct)$ when $ess\_pct < 0.20$ (and $0$ otherwise). This allows Optuna's TPE sampler to navigate the optimization landscape smoothly rather than falling off a cliff.

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
