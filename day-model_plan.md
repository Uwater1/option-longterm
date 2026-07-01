# Day-Model First-Principles Plan: New Objective Function Optimization

Plan to reformulate and optimize the Optuna objective function for `day-model` based on first principles.

---

## 1. Current Settings Baseline

### Linear model:
Existing target, features, selection, and tuning objective in `day-model/train_model.py`:

*   **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
*   **Features**: 238 engineered features (early 9:30-10:00 intraday features + shifted day-level indicators from margin, capital flows, connect quota, VIX, ATM 30d IV).
*   **Feature Selection**: Unified Time-Series Stability Selection (regime-stratified bootstrap, randomized ElasticNet, OOB IC).
*   **Optuna Objective (Current)**:
    *   `single` side: overall Spearman rank IC.
    *   `long`/`short` side: `0.5 * overall_ic + 0.5 * tail_ic` (top 30% tail).

### Filter model: (will throw away, way too complex and slow)
* **Target**: `y_true`
* **Features**: 238 features
* **Selection**:
    *   BH-FDR (overall): FDR = 0.2
    *   Stability selection:
    *   Algorithm: Subsampling + Randomized Lasso
    *   Bootstrap subsamples: 200
    *   Subsample size: ⌊n/2⌋ = 1350
    *   Selection probability threshold (π): 0.60
    *   Lambda path: log-uniform between 0.0001 and 0.2 (log10 scale, 100 points)
* **Hyperparameters:**
    *   L1 ratio: 0.70 (ElasticNet)
    *   Tuning method: Optuna Hyperband
    *   Early stopping: 3 trials
    *   Evaluated metrics: overall IC, tail IC (top 30%), model size
* **Optuna objective:**
    *   `single` side: `0.6 * overall_ic + 0.4 * tail_ic - 0.002 * size`
    *   `long`/`short` side: `0.6 * tail_ic + 0.4 * overall_ic - 0.002 * size`
* **Evaluation:**
    *   Lockbox: held-out 500 days
    *   Metrics: lockbox IC, lockbox tail IC, lockbox Sharpe (single), lockbox sorted Sharpe (long/short)


## New plan:
* See below Stage
* for simplicity, will only have 10:00 (open bar entry) ~ 14:35 (close bar exit) return (in log return )

---


## Relevant research

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

## First principles

1. **n/p is not actually terrible (2700/230 ≈ 11.7), but your tail-focus quietly shrinks it.** If you *hard-filter* to bottom-10%+top-10% of x before fitting, you're down to ~20% of rows. After removing your 500-point lockbox, you have 2200 left, and 20% of that is ~440 rows for 230 features — a ratio of ~1.9. That's now genuinely high-dimensional and MCP/Lasso will overfit badly if you screen and fit on the tail-only subset.
   → **Do feature screening/selection on the full distribution, not the tails.** Reserve the tail-focus for (a) the loss weighting and (b) the evaluation metric, not for defining the training rows.

2. **Huber's robustness and MCP's non-convex thresholding solve different problems and you want both, in sequence, not conflated.** Huber protects you from y-outliers (heavy-tailed noise in the response). MCP is about β-sparsity (removing dead features). Doing MCP on the tail-only subset makes it fight both the outlier problem *and* the small-n problem at once — separate the concerns.

3. **BH-FDR at the univariate screening stage is a dimensionality reducer, not a final answer.** It gets you from 230 → maybe 40–70 candidates cheaply, using the full n. It should never be your only selection step because it ignores joint/collinear structure (two correlated features can both pass, and MCP later has to figure out which one actually matters).

4. **Stability selection is what turns "MCP+Optuna picked these features" into something you can trust isn't a CV-tuning artifact.** With only 2700 rows, a single Optuna-tuned λ path is very likely to overfit its own hyperparameter search. Aggregating selections over many subsamples (Meinshausen–Bühlmann / CPSS) is the standard fix and gives you an actual error bound on false inclusions.

5. **Triple-dipping risk:** BH-screening + stability selection + Optuna tuning + tail-focus, all run on the same 2200 rows, will silently leak information into your "final" model unless you enforce strict sample separation between stages. This is the single most likely way your 500-point holdout ends up not meaning anything.

---

## Practical plan

**Step 0 — Lock the holdout first, stratified.**
Split 2700 → 2200 (working) / 500 (frozen holdout), stratifying the split by decile of x so the lockbox has proportional tail representation. Do not touch the 500 again until step 6.

**Step 1 — Cheap screening on full 2200 (not tail-restricted).**
Compute a robust marginal association per feature (Spearman or a Huber-weighted correlation, since you're already committed to Huber-style robustness) between each of the 230 features and x. Apply BH-FDR correction across the 230 tests. Keep the surviving set (expect 60~100 features or even). This step uses *all* 2200 rows — you want maximum power here, not tail-restricted power.

**Step 1.5: Hierarchical Feature Clustering.**
Cluster the surviving ~40–80 features from Step 1 into groups based on correlation distance (e.g., threshold at 0.7).
From each cluster, keep the feature with the highest marginal association (or run a quick univariate robust regression).
This reduces the feature set to about 30~50 non-collinear candidates. This makes Step 2 (Stability Selection) much more stable and ensures \piπ reflects true predictive power rather than survival against highly correlated substitutes.

**Step 2 — Stability selection on the survivors.**
Using skglm's MCP (or Lasso as a comparison baseline), run repeated subsampling (B ≈ 100–200, subsample size ⌊n/2⌋) over the screened feature set. For each subsample, fit across a λ path, record selected features. Keep features selected in ≥ π (e.g., 0.6–0.8) fraction of subsamples. This is your actual feature set — it's now robust to the specific 2200-row sample you happened to have.

**Step 3 — Reintroduce the tail focus as a loss weight, not a filter.**
For the final coefficient fit, use sample weights w(x) that upweight |x| near the extremes (e.g., w ∝ |x|^k, or a step weight for the outer deciles vs. inner) rather than deleting the inner 80% of rows. Such weight should be fine tuned by Optuna, given Metric Weights is good enough. This keeps n large enough for stable estimation while still optimizing for what you actually care about (tail behavior). skglm's weighted Huber/MCP objective supports this directly.

**Step 4 — Optuna over hyperparameters only, evaluated on a tail-specific metric.**
Nested CV within the 2200 (5-fold, or purged/embargoed CV if rows are time-ordered/autocorrelated). Optuna optimizes over MCP's (λ, γ) or Huber's δ, but the *objective function* should be focused on the top/bottom 10% decile rows of each validation fold — e.g., rank-IC saparated to TailIC (top/bottom 10%) and total IC. This directly targets what you said you care about, without ever shrinking the training rows.

### Step 4.1 — Define Metric Weights & Optimization Objective

**Philosophy:** This model acts as an *input factor* for a downstream trading system, not the trading system itself. Therefore, we do **not** optimize for simulated trading metrics (Sharpe, Turnover, Drawdown), which belong to the execution layer. Instead, we strictly optimize for **maximum predictive power on tail days**, **clean ranking structure**, **temporal stability across market regimes**, and **model simplicity** to prevent overfitting.

#### 1. The Objective Function

$$ \text{Objective} = \sum_{i=1}^{8} w_i \cdot \widetilde{M}_i $$

Where each $\widetilde{M}_i$ is a **robust z-score normalized** metric (computed via a 50-trial Optuna pilot run using Median Absolute Deviation), and weights $w_i$ are pre-defined constants that sum to `1.0`.

#### 2. Evaluation Scheme: Yearly Blocked Purged CV
To ensure the factor's predictive power is stable over time and survives market regime changes (e.g., 2015 volatility, 2020 pandemic, 2022 rate hikes), standard random K-Fold CV is abandoned. Instead, we use **Yearly Blocked Evaluation (2015–2023)**:
*   The data is split into 9 distinct yearly blocks.
*   An **embargo period** (e.g., 5–10 trading days) is applied at the end of each training year to prevent data leakage from autocorrelated features.
*   All metrics below are calculated **independently for each year**, and then aggregated (Mean, Std, Hit Rate) across the 9 years.

#### 3. Metric Definitions

| ID | Metric ($\widetilde{M}_i$) | Definition | Sign | Category | Weight ($w_i$) |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **M₁** | **Yearly Tail IC IR** | $\frac{\overline{\text{IC}_{\text{tail, year}}}}{\sigma(\text{IC}_{\text{tail, year}})}$ — Mean divided by Standard Deviation of Spearman IC computed *only* on top/bottom 10% rows for each year (2015–2023). The ultimate measure of stable tail power. | + | Tail Stability | **0.2** |
| **M₂** | **Yearly Tail IC Mean** | Mean of the yearly tail ICs. Measures the absolute strength of tail predictions regardless of variance. | + | Tail Power | **0.2** |
| **M₃** | **Yearly Hit Rate** | Percentage of years (out of 9) where the Tail IC is strictly $> 0$. A factor that works 8 out of 9 years is vastly superior to one that has a high average but fails in 4 years. | + | Temporal Consistency | **0.15** |
| **M₄** | **Overall Rank IC** | Mean Spearman rank IC across *all* rows, averaged across the 9 years. Ensures the model retains general market awareness and isn't purely overfit to the extremes. | + | General Signal | **0.15** |
| **M₅** | **Decile Monotonicity** | Spearman $\rho$ between decile rank (1–10) and mean actual return, averaged across years. A high score ensures the factor provides a smooth, usable ranking for the downstream trading system. | + | Signal Structure | **0.10** |
| **M₆** | **Top-Bottom Spread** | Mean return spread (Top 10% minus Bottom 10%), averaged across years. Standard factor efficacy metric to ensure the factor creates actual directional separation. | + | Factor Efficacy | **0.05** |
| **M₇** | **Feature Parsimony** | $\log(1 + k)$ where $k$ = number of selected features. Heavily penalizes bloated models. | − | Simplicity | **0.10** |
| **M₈** | **Coefficient Bloat** | L2 norm of standardized model coefficients ($\|\beta\|_2$). Penalizes models that rely on a few massive, unstable coefficients. | − | Simplicity | **0.05** |

#### 4. Hard Constraints (Kill Switches)

Before computing the weighted objective, apply hard rejection criteria. If any condition fails, the Optuna trial is immediately pruned (return `-inf`):

*   **Overall IC > 0:** (`M₄ > 0`) A model with negative overall rank correlation across its lifetime is worse than random.
*   **Minimum Hit Rate ≥ 60%:** (`M₃ >= 0.60`) The factor must have a positive Tail IC in at least 6 out of the 9 years. Factors that "die" for multiple years are rejected.
*   **Decile Monotonicity > 0.4:** (`M₅ > 0.4`) Below this threshold, the factor's ranking is too noisy for a trading system to use reliably.
*   **Feature count ∈ [3, 50]:** With $n \approx 2200$ (per year), more than 50 features risks severe overfitting and multicollinearity.
*   **Top-Bottom Spread > 0:** (`M₆ > 0`) The top decile must outperform the bottom decile on average across the testing period.

**Step 5 — Sanity check the stability-selected set didn't get re-litigated by Optuna.**
Freeze the feature set from Step 2 before Step 4 starts. Don't let Optuna re-select features (no per-trial re-screening) — it should only tune penalty strength/shape on a fixed feature set. If you want to test sensitivity, do it as a separate ablation, not inside the main tuning loop.

**Step 6 — One-shot evaluation on the 500-point lockbox.**
Refit the final model (final feature set + final hyperparameters) on all 2200 rows, then evaluate once on the 500. Report both overall IC and tail-decile IC on the lockbox. If it fails here, the fix is going back to Step 1 with a more conservative π or FDR level — not tweaking hyperparameters against the lockbox itself (that would defeat its purpose).

**One naming note:** with 230 features and this row count, you're in "moderately high-dimensional," not "ultra-high-dimensional" (SIS-type papers usually target p in the thousands+). That's good news — it means stability selection + BH-screening will likely be enough; you probably don't need knockoffs' extra construction complexity unless the lockbox result disappoints and you need a hard FDR guarantee on the surviving set.