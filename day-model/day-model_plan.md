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
- For an FDR-controlled alternative to stability selection: Barber & Candès knockoffs — a variable selection procedure that controls the false discovery rate in any finite-sample setting, though it's more finicky to construct correctly with only 230 real (non-Gaussian, non-synthetic) features.

---

## 3. First Principles

1. **Do feature screening/selection on the full distribution, not the tails.** Reserve the tail-focus for (a) the loss weighting and (b) the evaluation metric, not for defining the training rows.
2. **Huber's robustness and MCP's non-convex thresholding solve different problems and you want both, in sequence, not conflated.** Huber protects you from y-outliers (heavy-tailed noise in the response). MCP is about β-sparsity (removing dead features). Doing MCP on the tail-only subset makes it fight both the outlier problem *and* the small-n problem at once — separate the concerns.
3. **BH-FDR at the univariate screening stage is a dimensionality reducer, not a final answer.** It gets you from 230 → maybe 40–70 candidates cheaply, using the full n. It should never be your only selection step because it ignores joint/collinear structure (two correlated features can both pass, and MCP later has to figure out which one actually matters).
4. **Stability selection is what turns "MCP+Optuna picked these features" into something you can trust isn't a CV-tuning artifact.** With only 2700 rows, a single Optuna-tuned λ path is very likely to overfit its own hyperparameter search. Aggregating selections over many subsamples (Meinshausen–Bühlmann / CPSS) is the standard fix and gives you an actual error bound on false inclusions.
5. **Triple-dipping risk:** BH-screening + stability selection + Optuna tuning + tail-focus, all run on the same 2200 rows, will silently leak information into your "final" model unless you enforce strict sample separation between stages. This is the single most likely way your holdout ends up not meaning anything.

---

## 4. Practical Plan

**Step 0 — Lock the holdout first sequentially.**
Partition the entire dataset chronologically. Everything before **2024-03-01** (approx 2166 rows) forms the working training set. Everything from **2024-03-01 to the last day** (approx 556 rows) is the out-of-sample lockbox. Do not touch the lockbox again until step 6.

**Step 1 — Cheap screening on full working set.**
Compute robust marginal association per feature (Spearman rank correlation) between each of the 238 features and the target. Apply BH-FDR correction across the tests (FDR = 0.40). If fewer than 80 features pass, fallback to the top 80 features by p-value.

> Hierarchical Feature Clustering / correlation-based pre-filtering are useless:
> Clustering slightly correlated features ($|r| \ge 0.3$) and dropping them based on univariate ranking discards complementary multivariate features. This causes model collapse to $\le 2$ sparse active weights and a negative OOS Lockbox Tail IC ($-0.0207$). Removing this step and relying on ElasticNet stability selection to handle collinearity multivariately preserves 72 active weights and increases Lockbox Tail IC to $+0.0304$.

**Step 2 — Stability selection on survivors.**
Run repeated subsampling ($B=100$, subsample size $\lfloor N/2 \rfloor$) over the Step 1 survivors. Fit ElasticNet paths (l1_ratio = 0.5) and keep features selected in $\ge 0.60$ fraction of subsamples (fallback to top 5 if count < 3). Because ElasticNet has a grouping effect, it naturally handles collinearity multivariately without needing a separate clustering pre-filter.

**Step 3 — Loss Weighting via Input Scaling.**
For the final coefficient fit, use sample weights $w(y_i) = |y_i|^k$ (exponent $k$ tuned by Optuna) to upweight tail days. Implement weights by scaling inputs $X$ and targets $y$ by $\sqrt{w}$, which is mathematically exact for least squares and serves as a robust Huber weighting.

**Step 4 — Optuna over hyperparameters only, evaluated on a tail-specific metric.**
Nested Yearly CV (2015-2023) within the working set, applying a 10-day embargo at training year boundaries to prevent temporal leak. Optuna tunes MCP ($\lambda, \gamma$), Huber $\delta$, and loss weight exponent $k$.

### Step 4.1 — Define Metric Weights & Optimization Objective

$$ \text{Objective} = \sum_{i=1}^{8} w_i \cdot \widetilde{M}_i $$

Where each $\widetilde{M}_i$ is a **robust z-score normalized** metric (computed via a 50-trial Optuna pilot run using Median Absolute Deviation), and weights $w_i$ are pre-defined constants:

| ID | Metric ($\widetilde{M}_i$) | Definition | Sign | Category | Weight ($w_i$) |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **M₁** | **Yearly Tail IC IR** | $\frac{\overline{\text{IC}_{\text{tail, year}}}}{\sigma(\text{IC}_{\text{tail, year}})}$ — Mean divided by Standard Deviation of Spearman IC computed *only* on top/bottom 10% rows for each year. | + | Tail Stability | **0.20** |
| **M₂** | **Yearly Tail IC Mean** | Mean of the yearly tail ICs. Measures absolute strength of tail predictions. | + | Tail Power | **0.20** |
| **M₃** | **Yearly Hit Rate** | Percentage of years where Tail IC is strictly $> 0$. | + | Temporal Consistency | **0.15** |
| **M₄** | **Overall Rank IC** | Mean Spearman rank IC across all rows. | + | General Signal | **0.15** |
| **M₅** | **Decile Monotonicity** | Spearman correlation between decile rank and mean actual return. | + | Signal Structure | **0.10** |
| **M₆** | **Top-Bottom Spread** | Mean return spread (Top 10% minus Bottom 10%). | + | Factor Efficacy | **0.05** |
| **M₇** | **Feature Parsimony** | $-\log(1 + k)$ where $k$ is active model size (coefficients with absolute value $> 10^{-5}$). Penalizes bloated models. | + | Simplicity | **0.10** |
| **M₈** | **Coefficient Bloat** | $-\|\beta\|_2$. Penalizes large, unstable coefficients. | + | Simplicity | **0.05** |

Before computing the weighted objective, apply **Kill Switches**:
* Overall IC > 0 (M4 > 0)
* Minimum Hit Rate >= 60% (M3 >= 0.60)
* Decile Monotonicity > 0.4 (M5 > 0.4)
* Top-Bottom Spread > 0 (M6 > 0)
If any condition fails, return `-1e9` (pruned).

**Step 5 — Freeze feature set.**
Stability-selected features are frozen before Optuna tuning begins.

**Step 6 — One-shot evaluation on the lockbox.**
Refit final model on all working rows, predict on lockbox (2024-03-01 to last day), and report out-of-sample overall IC and tail-decile IC.
