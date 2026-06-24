# Unified Multi-Regime Time-Series Feature Stability Framework

Selecting robust features in financial time-series models is challenging due to noise, non‐stationarity, and correlated signals. Standard Lasso on a single sample often overfits, especially when predictors are collinear. To mitigate this, *stability selection* methods use resampling or randomization to identify features that are consistently selected across perturbations. In our context (daytrading ETF returns), we extend this idea by combining several modern techniques into a unified framework.  We propose to layer (A) randomization of penalties, (B) univariate information‐coefficient screening, (C) fold‐level stability measures, (D) regime‐stratified bootstrapping, and (E) combinatorial purged CV with importance‐distribution analysis into one pipeline. 

## A. Randomized Lasso/ElasticNet Selection  
**Key idea:** Randomly perturb the penalization to encourage selection diversity.  Meinshausen and Bühlmann (2010) introduced *Randomized Lasso*, which assigns each feature a random weight in its L1 penalty each trial.  Specifically, one multiplies the penalty for feature *j* by a random factor \(W_j\sim\text{Uniform}(\alpha,1)\), forcing the model to sometimes favor different variables in a collinear group.  As a result, over many trials features that are truly predictive tend to be selected consistently, while spurious ones drop out. This yields **asymptotic selection consistency** even when plain Lasso fails the irrepresentable condition.  In practice, we can implement a *Randomized ElasticNet* by applying the random weight to the L1 term of the ElasticNet penalty (retaining the L2 term for grouping).  

- *Related work:* Bolasso (Bach 2008) shows that intersecting supports over many bootstrap Lasso runs yields consistent selection. This is akin to Randomized Lasso in spirit. In essence, we fit Lasso/ElasticNet multiple times on bootstrap or subsampled data with random weights, and record selection frequencies. 

- *Benefit:* Randomization mitigates the “vote splitting” issue where correlated predictors share predictive power and only one is chosen. By occasionally down-weighting any given feature, the algorithm “forces” others to enter, improving joint stability. In aggregate, we obtain a more reliable set of candidate features.  

## B. Univariate IC-Based Screening  
**Key idea:** Augment selection by evaluating each feature’s predictive *Information Coefficient* (IC) stability.  In quantitative finance, the Spearman rank correlation between a feature and the next-day return (the IC) is a standard signal quality measure. Instead of using only multivariate coefficients, we also track each feature’s univariate correlation out-of-sample.  

- *Sure Independence Screening (SIS):*  Fan and Lv (2008) show that ranking predictors by marginal correlation can asymptotically retain all relevant features. Similarly, we compute each feature’s in-sample IC (e.g. via a single-factor regression) and then test its **out-of-bag IC** on held-out blocks.  

- *Stability rule:* We mark a feature “selected” in a bootstrap trial if its OOS IC is statistically significant (e.g. Spearman *p*<0.05) or exceeds a threshold (e.g. |IC|>0.02).  This way, a feature must demonstrate consistent predictive power even on unseen data to count toward its stability score.  

- *Benefit:* This approach filters out features that only fit noise in one period but fail to predict new data. It complements Lasso’s penalty-based selection by explicitly checking the sign and significance of each factor’s predictive signal (akin to a *sure screening* step).  

## C. Fold-Level Stability (Walk-Forward CV)  
**Key idea:** Assess selection consistency across walk-forward folds, not just within each bootstrap sample. After obtaining selection indicators from the randomized bootstrap (and IC tests) within each fold, we compute, for each feature, the *mean* and *variance* of its selection frequency across the k walk-forward folds.  

- *Implementation:* Within each of the 5 purged CV folds, independently run the block-bootstrapped Randomized ElasticNet + IC-screening procedure, yielding a per-fold stability score (0–1) for each feature. Then calculate each feature’s across-fold mean stability and its standard deviation.  

- *Filtering:* We can then discard features that are unstable *over time*—e.g. those with high variance (selected in some eras but not others) or low overall mean selection rate. For instance, only keep features whose fold-mean stability exceeds a threshold and whose stability variance is below a cap.  

- *Benefit:* This penalizes features that only look predictive in one market regime or subperiod but fail elsewhere. In non-stationary financial data, a feature might “pop up” by chance in one era; requiring consistent selection across all folds guards against such time-specific overfitting.  

## D. Regime-Stratified Block Bootstrap  
**Key idea:** Ensure rare market regimes are represented in the resampling. Financial time series exhibit distinct **market regimes** (e.g. bull vs bear, high-volatility vs low-volatility). If we sample blocks uniformly in time, common regimes (e.g. long bull market) will dominate and drown out features that only predict in crashes or spikes.  

- *Defining regimes:* We first classify each historical day into a regime, using thresholds or unsupervised methods. For example, one might label high-volatility days using VIX (e.g. VIX>30) or cluster returns (e.g. hidden Markov models or k-means on returns/volatility). Recent work uses Wasserstein-k-means or HMMs to segment regimes based on volatility clustering and returns.  

- *Stratified bootstrapping:* When forming each bootstrap sample, we stratify by regime: that is, draw blocks such that the overall frequency of each regime in the bootstrap matches (or deliberately oversamples) its frequency in the historical timeline. Concretely, one can pre-generate block start indices separately for each regime cluster, then concatenate blocks to form a full sample.  

- *Benefit:* This prevents a single prevalent regime from dominating. Features that are only predictive in, say, crashes will still be sampled enough times to register stability. For example, a simple regime-split strategy illustrates how feature efficacy changes drastically by regime: in calm bull regimes (VIX≤15), ~66% of short-volatility trades profit, whereas in a high-volatility crash regime (VIX>15, SPY down) only ~32% do. By resampling within regimes, we can capture such conditional effects and avoid “washing out” rare-regime predictors.  

 *Figure: A simple regime-splitting decision tree showing how short-volatility strategy success rates differ by market regime (adapted from Macrosynergy). In low-volatility up-markets ~66% of trades win, whereas in a high-volatility downturn only ~32% do. Regime-stratified sampling preserves information from each segment.*  

## E. CPCV and Feature Importance Distributions  
**Key idea:** Leverage multiple out-of-sample backtests to gauge importance variability. Marcos López de Prado’s *Combinatorial Purged CV* (CPCV) generates many distinct walk-forward paths instead of one, effectively multiplying the number of out-of-sample evaluations.  

- *CPCV:* In CPCV, one defines groups (e.g. 6 sequential blocks) and systematically leaves different combinations of blocks for testing, yielding \(N-1\choose k\) possible backtest paths (practically, we sample a fixed number of paths). Each path is truly out-of-sample with no overlap with its training data. The result is multiple independent OOS performance profiles for the same model.  

- *Importance metrics:* We can apply this to feature selection by computing each feature’s *Mean Decrease in Accuracy (MDA)* or *Single Feature Importance (SFI)* on each OOS path. (For example, for each path, measure the drop in predictive performance when permuting that feature.) This yields a distribution of importances across paths, not just a single value.  

- *Benefit:* Examining these distributions yields confidence intervals for each feature’s importance. If a feature is truly valuable, its MDA (or Spearman IC) will consistently be high; if not, it will vary or include zero. López de Prado notes that CPCV can drastically reduce false discoveries by requiring features to be important across many distinct paths. In short, CPCV turns selection into a statistical exercise: we keep features with significantly positive mean importance and low variance across the generated OOS paths.  

## Proposed Unified Framework and Implementation  
Combining all directions yields a *multi-criteria stability selector*. A schematic pipeline is: **(1)** Label regimes in the historical data (e.g. via thresholds or clustering). **(2)** For \(B\) bootstrap trials: sample blocks stratified by regime, then apply a *Randomized ElasticNet* (randomized L1 penalties) to that bootstrap sample. Also compute each feature’s single-variable OOS Spearman IC on that sample (or simple regression). Record for each trial whether feature *j* is selected (nonzero coeff) **and** whether its IC is significant. **(3)** Repeat over all folds of walk-forward CV. For each feature, aggregate: (a) its overall bootstrap selection frequency, (b) its OOB IC significance frequency, (c) per-fold mean selection and variance, and (d) the distribution of its importance under CPCV paths. Finally, apply thresholds: e.g. require selection rate ≥0.5, IC frequency ≥0.5, fold-variance below cap, etc.  

We plan to implement this as a scikit-learn‑style `TimeSeriesStabilitySelector` class. It will take parameters like `n_bootstraps`, `block_size`, `randomization_alpha`, `regime_labels`, `ic_threshold`, `fold_variance_cap`, etc. Its `.fit()` will perform the stratified bootstrap + randomized ElasticNet + IC tests per fold, and its output will be a DataFrame of feature statistics (Pearson r, Spearman ρ, mean bootstrap selection, IC frequency, fold-variance, etc.) and a Boolean mask of selected features.  

**Expected outcomes:** Compared to the original stability procedure, this unified approach should (i) reduce the variance of the chosen feature set across folds (more consistent stability scores); (ii) improve out-of-sample IC (higher mean rank correlation and lower volatility of ICs); (iii) shrink the gap between in-sample and OOS IC (less overfitting); and (iv) better handle collinearity by selecting correlated predictors jointly when appropriate. In academic practice, each of these claims will be validated by backtest tables: e.g. showing that after selection, a holdout set yields more stable factor performance, and that walk-forward selected sets have higher overlap stability.  

**Summary:** By integrating randomized penalties, OOS correlation testing, fold-level aggregation, regime awareness, and multiple OOS paths, this framework aims to yield a parsimonious yet robust feature subset tailored for time-series models. Each component is grounded in recent research, making the overall selector both theoretically sound and practically effective for quantitative trading strategies.  

**Sources:** We build on the literature of stability selection, sure-screening, regime detection, and financial ML validation techniques. Recent advances (e.g. Nouraie & Müller 2024 on stability calibration) inform our design. The chosen components have all been validated in prior work and are adapted here for a cohesive time-series feature selection pipeline.  

