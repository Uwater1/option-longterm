# Day-Model Feature Expansion & Return Prediction Workflow

Workflow for day-model feature generation and multi-metric linear return predictor optimization.
Read [day-model_plan.md](file:///home/hallo/Documents/option-longterm/day-model/day-model_plan.md) for logic. Update both files when logic changes.

## Target Definition
* **Target**: `trade_return = log(close[EXIT_BAR] / open[decision_bar+1])`
* **Entry**: 10:00 (bar 5 closes at 10:00, entry at open of bar 6)
* **Exit**: 14:35 (close of bar 42)
* **Underlying**: Log return from 10:00 to 14:35 across all 5 ETFs.

## Workflow (--early flag indicate Early Target (10:00 ~ 13:05))

```bash
# 1. Re-generate parquet feature datasets
python3 day-model/build_features.py -e all (--early)

# 2. Train BOTH long and short side models per ETF (DEFAULT)
python3 day-model/train_model.py -e all --trials 100 (--early)
# Cap trials at 100 to prevent overfit risk.

# 3. Generate summary REPORT.md and plots (displays only champion `_sortino_blended` configs to reduce size)
python3 day-model/generate_report.py (--early)

# 4. Run out-of-sample backtest simulator
python3 day-model/backtest_simulator.py --etf all (--early) (--type {ETF,Future}) (--option)
```

(--early : Outputs will be saved with `_early` suffixes)
### Rolling Model Training (Quarterly Retraining)

Trains 8 quarterly rolling models (2024Q1-Q4 + 2025Q1-Q4) per ETF, each using a 6-year rolling window with relative validation blocks.

```bash
# Train rolling models (supports -e, -q, -j, --trials, --window-years, --skip-existing)
python3 day-model/train_rolling.py -e all -j 4 --skip-existing --trials 100 --window-years 6

# Alternatively, train rolling directly via train_model.py
python3 day-model/train_model.py -e all --rolling --window-years 6
```

Generate comprehensive rolling strategy report (IC + P&L + Sharpe + warnings):
```bash
python3 day-model/generate_rolling_report.py                 # All quarters, all ETFs
python3 day-model/generate_rolling_report.py -e 300          # Single ETF
python3 day-model/generate_rolling_report.py -q 2024Q1       # Single quarter
python3 day-model/generate_rolling_report.py --no-plots      # Skip diagnostic plots
python3 day-model/generate_rolling_report.py --thr 70        # Custom signal threshold
```

Run backtest with rolling models (auto-selects per date):
```bash
python3 day-model/backtest_simulator.py --etf all --rolling (--type {ETF,Future}) (--option)
```

**Rolling Artifact Layout**:
```
day-model/
  models/rolling/linear_{tag}_r{YYYYMM}.joblib
  data/rolling/results_{tag}_r{YYYYMM}.json
  plots/rolling/{YYYY}Q{Q}/diagnostics_{tag}_r{YYYYMM}.png
  ROLLING_REPORT.md
```

**Warning System** (pre-lockbox validation metrics only):
- **OK**: Outer validation IC >= 0 and no significant decay.
- **WARNING**: Outer IC < 0 OR outer Tail IC < 0 (single metric negative).
- **ALERT**: Both outer IC and Tail IC negative, OR IC decay > 50% vs previous quarter.

### Side-Specific Objective (`--both` default | `--side single|long|short`)

Feature pipeline (screening → CSS → VIF → CPCV) unchanged. Only validation objective (V2) and lockbox Tail IC side-aware:

| Side     | Tail IC definition (V2)                | V1..V4 weights              |
| :---     | :---                                   | :---                        |
| `single` | two-sided: top 10% + bottom 10% (legacy) | `[0.40, 0.40, 0.15, 0.05]` |
| `long`   | top-only: `pred >= P85(pred)` (top 15%) | `[0.35, 0.50, 0.15, 0.00]` (V4 dropped, renormalized) |
| `short`  | bot-only: `pred <= P15(pred)` (bot 15%) | `[0.35, 0.50, 0.15, 0.00]` (V4 dropped, renormalized) |

* CV fold metrics M1..M6 and kill-switches stay two-sided for all sides.
* Side stored in `results_{tag}.json` and `scaler_{tag}.joblib` under `side` field.
* `tag = {ETF}` for `single`, `{ETF}_long` / `{ETF}_short` otherwise.
* Pilot cache (`cache_pilot_*`) side-scoped via hash: cache key includes `"v11_side", side` when `side != "single"`. Selection and LOYO caches side-independent.
* Lockbox Tail IC in `generate_report.py` side-aware.

```bash
# Default: train both long and short for each ETF
python3 day-model/train_model.py -e 300 --trials 100
python3 day-model/train_model.py -e all --trials 100

# Train ONE specific side only (disables --both)
python3 day-model/train_model.py -e 300 --no-both --side single --trials 100
python3 day-model/train_model.py -e 300 --no-both --side long   --trials 100
python3 day-model/train_model.py -e 300 --no-both --side short  --trials 100
```

### train_model.py Performance & Experiment Options

```bash
python day-model/train_model.py -e 300 -t 200             # cache ON, n_jobs=cpu_count
python day-model/train_model.py -e 300 --no-cache          # force recompute
python day-model/train_model.py -e 300 --skip-step 2       # skip Step 2 (CSS/VIF/Condition) filter (Step 1 skipped by default)
python day-model/train_model.py -e 300 --optuna-jobs 8     # cap Optuna workers
python day-model/train_model.py -e 300 --optuna-jobs 1     # sequential (100% deterministic)
python day-model/train_model.py -e 300 --bootstrap-jobs 8  # cap stability-bootstrap workers
python day-model/train_model.py -e 300 --loyo-jobs 4       # cap LOYO fold workers per trial
```

Speedups: fp32 arrays, vectorized Spearman screen, parallel stability bootstrap & CPCV folds, disk caches, precomputed unweighted scaled matrix, numpy-vectorized yearly metrics, GIL bypass via Optuna JournalStorage, local BLAS pin = 1, skglm `AndersonCD(max_epochs=2000)`, seeded TPESampler.

* **CPCV parallelism**: `--loyo-jobs -1` (auto = `cpu_count // optuna-jobs`). Cap to prevent core oversubscription.

### Pipeline Constants Sweep (`day-model/sweep/`)

> [!NOTE]
> The parameter sweep module (`day-model/sweep/`) is legacy and no longer used.

## Cache invalidation

`train_model.py` writes three caches per ETF in `day-model/data/`:

| File | Contents |
|---|---|
| `cache_select_{etf}_{hash}.joblib` | `screen_mask`, `p_vals`, `rhos`, `stability_selected_idx`, `stability_scores` (version `v15_vif_cond` key; side-independent) |
| `cache_loyo_{etf}_{hash}.joblib` | CPCV folds `(test_idx, X_tr_scaled, X_te_scaled, y_tr)` (version `v10` key; side-independent) |
| `cache_pilot_{etf}_{hash}.joblib` | Pilot records `[{params, raw_metrics, val_metrics}]` (version `v14_unified` key for single, `v14_unified_side` key for long/short; side-scoped) |

**Auto-invalidated** when these change:
* ETF name
* `len(FEATURES)`
* `features_{etf}.parquet` mtime
* Selection Train shape
* `STABILITY_B`, `STABILITY_PI`, `SCREEN_FDR`
* `SELECTION_VAL_DATE`
* `TARGET` column
* Selected-feature indices
* `PILOT_N_TRIALS`, `PILOT_SEED`
* `--side` (only for `long`/`short` via `"v14_unified_side"`)

**Manual clear required when**:
* Editing `FEATURES` list in `build_features.py` without regenerating parquet.
* Changing `METRIC_WEIGHTS` or `SIDE_CONFIG` weights (clear `cache_pilot_*`).
* Editing `side_tail_ic` semantics in `train_model.py` (clear `cache_pilot_*`).
* Changing CPCV group/test window logic, embargo, or scaling in `_compute_loyo`.
* Changing screening or stability selection internals.
* Changing hierarchical clustering thresholds/metrics for CSS.

**Purge all caches**:
```powershell
Remove-Item day-model\data\cache_*.joblib
```

## Remade Predictor Architecture

1. **Lockbox Split (Step 0)**: Hold out days $\ge 2024-03-01$ (OOS data untouched during training).
2. **Selection Validation Split (Step 0.5)**: 6 non-contiguous 3-month blocks (~370 days) for validation. 4 Inner blocks for Optuna tuning; 2 Outer blocks for generalization check. 10-day embargo at boundaries.
3. **BH-FDR Screening (Step 1 - Bypassed)**: Bypassed by default. Univariate screening is not working because dropping features with low marginal linear correlation discards key joint predictive power, causing feature starvation and model collapse.
4. **CSS + VIF + Condition Pruning (Step 2)**: Complete Linkage hierarchical clustering (threshold $t=0.20$, $|r| \ge 0.80$) on all candidate features. Subsampling ($B=200$) ElasticNet path votes aggregated at cluster level. Keep clusters selected in $\ge 55\%$ subsamples with max $Q=35$ active clusters. Pick representative with highest individual stability score, tie-breaking by absolute Spearman correlation. Apply iterative VIF pruning (VIF threshold 10.0, dynamically adjusted to 5.0 for 50ETF) and SVD-based condition number pruning post-VIF (iteratively drops the feature with the largest loading on the smallest singular vector until condition number < 100.0).
5. **Loss Weighting (Step 2)**: Power weights $w(y_i) = |y_i|^k$. Scale inputs by $\sqrt{w}$.
6. **CPCV with Embargo (Step 3)**: 6 groups, 2 test groups (15 folds), 10-day embargo at test boundaries. Run on selection train.
7. **Pilot Normalization (Step 3.1)**: Run 50 pilot trials to compute median and MAD for validation z-scores.
8. **Objective Function**: Maximize weighted sum of normalized validation metrics + ESS soft penalty under 20%.
9. **Signed Constraints & TPESampler**: Hard constraints (Overall IC > 0, Hit Rate $\ge 60\%$, Monotonicity > 0.25, Spread > 0, Active features $\le ESS / 9$, Gini concentration $\le 0.85$ soft limit). Violation prunes trial.
10. **One-Shot Evaluation & Plots (Step 5)**: Refit on working set using best parameters. Save final model and scaler. Evaluate OOS lockbox via `generate_report.py` (side-aware Tail IC). Plot 15 diagnostic panels. Run block bootstrap (B=1000, block size 10) for 95% CIs.
11. **Unified L1/L2 Regularization Manifold**: Unified `GeneralizedLinearEstimator` using Huber datafit and `MCP_plus_L2(alpha*rho, gamma, alpha*(1-rho))` penalty. Regularization is continuously tuned via total budget (`unified_alpha`) and sparse-vs-ridge mix (`unified_rho`).
12. **Deflation & Overfit Diagnostics**: Compute running Deflated Objective. Compute PBO and Performance Degradation using CSCV.
13. **Model Quality**: Calculate condition numbers, ESS, and Gini coefficient.
14. **Plateau Parameter Selection**: Select trial residing in the most stable hyperparameter plateau (radius $r=0.25$) using deflated objective.

## Stability & Overfit Upgrades (July 2026)

Upgraded model training stability, tail performance, overfit diagnostics, and decay monitoring:

1. **Bootstrap Bagging Feature Selector (Soloff et al. 2024 JMLR)**:
   - Wraps final model fit in bootstrap aggregation ($B=100$) over Selection Train.
   - Computes feature inclusion frequency. Keeps features with inclusion frequency $> 50\%$.
   - Prevents sparse selector collapse to 2-3 active features on small samples.
   - Refits final model on Working set restricted to bagged features.

2. **Soften Tail IC to 15% (P85/P15)**:
   - Uses 15% threshold for `long` and `short` sides in `side_tail_ic` and `side_tail_mask`.
   - Long/short validation weights set to `[0.35, 0.50, 0.15, 0.00]`.

3. **Two-Sided CV Folds & Side consistency constraints**:
   - Standard CV fold metrics `m1..m6` and standard kill-switches are forced to stay two-sided (`side="single"`).
   - If `side != "single"`, two new side-specific consistency constraints are appended:
     - `side_m2 > 0` (side-specific Yearly Tail IC Mean > 0)
     - `side_m3 >= 50%` (side-specific Hit Rate >= 50%)
   - Prevents side-specific fold-level sign flips while keeping overfit guardrails intact.

4. **Decoupled Ridge Fallback, Unified Manifold & Live Conditioning (July 2026)**:
   - Removed legacy categorical models and static pre-decision `force_ridge`. The optimizer operates on a continuous unified manifold (`MCP_plus_L2` penalty) spanning Ridge ($\rho \to 0$) to aggressive non-convex MCP ($\rho \to 1$, small $\gamma$).
   - Live per-trial regularized condition number check: rejects/prunes trial if regularized Gram matrix condition number (`reg_kappa`) exceeds `HARD_KAPPA` (defined as `10.0 * SAFE_KAPPA`).
   - Added SVD-based condition number check post-VIF (`run_cond_pruning`) to iteratively drop the feature with the largest loading on the smallest singular vector until raw cond < 100.0, catching multi-feature near-collinearity.
   - Dynamic VIF thresholding: tightened to `5.0` for highly ill-conditioned `50ETF` and `159915ETF`, default `10.0` for other ETFs.
   - Added graduated soft penalty on the condition number `cond_penalty = -0.1 * max(0, log(reg_kappa) - log(SAFE_KAPPA))` to guide TPE sampler toward well-conditioned parameter spaces before hitting the hard prune cliff.
   - **Relative Condition Number Guardrails**: Rather than one-size-fits-all values, thresholds are scaled to the trial's raw active condition number: `SAFE_KAPPA = 40.0 * raw_X_cond` and `HARD_KAPPA = 10.0 * SAFE_KAPPA`.
   - **Dynamic Ridge Floor / rho Cap**: When baseline design matrix condition number (`raw_base_cond`) exceeds 15.0, `unified_rho` is capped at `max_rho = clip(1.0 - 0.005 * (raw_base_cond - 15.0), 0.5, 0.95)`, forcing a minimum amount of L2 ridge regularization to stabilize the ill-conditioned features.

5. **No-Fallback Pipeline & Screening Fallback (July 2026)**:
   - Removed most legacy safety-net fallbacks from feature-selection pipeline:
     - CSS cluster force-top5 (when < 3 clusters pass pi) → removed. Pure pi threshold.
     - Bagging top-3 (when no features > 50% inclusion) → removed. Pure > 50% bagging.
   - **Step 2 Stability Selection MIN_FEATURE Fallback**: Added `MIN_FEATURE = 15`. If Step 2 Stability Selection selects fewer than `MIN_FEATURE` clusters, select top `MIN_FEATURE` clusters sorted by stability score and maximum absolute correlation.
   - Constants tuned via meta-Optuna (`day-model/sweep/meta_optuna.py`): 5 pipeline constants + model hyperparams in single TPE study.
   - **Tuned constants**: reference day-model/train_model.py

6. **Monthly Blocked Validation Bootstrap Regularization**:
   - Perform $B=100$ monthly blocked bootstrap resamples on the inner validation set.
   - Subtract standard deviation of bootstrapped tail ICs from raw validation Tail IC:
     $$V_{tail\_ic\_adj} = val\_tail\_ic - 1.0 \times \sigma_{boot\_tail\_ic}$$
   - Penalizes unstable validation scores and steers Optuna to robust configurations.

7. **Model Confidence Set (MCS) & Bayesian True Discovery**:
   - Hansen's MCS (sequential t-test, alpha=10%) identifies statistically indistinguishable trials.
   - Empirical Bayes posterior probability of true discovery $P(\theta_{OOS} > 0 | data)$ logs discovery confidence.

7. **Quarterly Rolling Refit decay check**:
   - Runs `run_quarterly_rolling_refit_test` post-lockbox.
   - Compares Static vs Rolling Model performance on quarterly windows (QuantBench method).

8. **Target Transformation & Post-Hoc Calibration (July 2026)**:
   - Fix train-eval mismatch between Huber loss and Spearman IC.
   - Command-line arguments:
     - `--target-transform`: choices `none` (default), `rank` (Pearson-on-ranks), `gauss` (normal quantile mapping of ranks).
     - `--post-hoc-calibrate`: optimize active coefficients post-hoc using SciPy Nelder-Mead on Spearman IC.
     - `--sharpe-objective`: use validation tail-Sharpe (winsorized, annualized) instead of tail-IC as Optuna objective. **Performance note**: no significant OOS uplift (P&L CI `[-755, +664] bps`, Sharpe CI `[-0.54, +0.54]`); default Tail IC remains recommended.
    - Saves model and results with `_rank`, `_gauss`, and `_calibrated` suffixes to run A-B tests side-by-side.

## Sortino Ratio as Default V5 Objective (July 2026)
- **Sortino Ratio**: $S(\tau) = \frac{E[R]-\tau}{\sqrt{E[\min(R-\tau,0)^2]}} \times \sqrt{244}$. Downside deviation only; upside volatility not penalized.
- Default weight 0.40 is best sortino variant — OutTIC +23% over Sharpe baseline. IC generalization gap tightened 34%.
- **Default**: `--ratio-type sortino`. Use `--ratio-type sharpe` to revert.
- Report cleanup: `_sharpe`, `_sw*`, `_sortino_sw*`, `_emb*` suffix variants filtered from reports.

## Deflated Sharpe Ratio — PSR/DSR Overfit Correction (July 2026)
- **PSR**: López de Prado & Bailey (2014) formula with skewness/kurtosis terms. Replaces ad-hoc Gaussian correction.
- **DSR**: Sets $SR_0 = E[\max_N(SR)]$ via Gumbel approximation.
- **Trial Correlation**: `dynamic_rho` reduces overfit penalty via $\sqrt{1-\rho}$. Search-budget uses raw trial count N (not ONC effective-N).
- **Output**: `results_{tag}.json` contains `dsr.probability`, `dsr.sr_benchmark`, `dsr.sr_hat`, `dsr.effective_n_trials`, `dsr.dynamic_rho`.

## CPCV-Bagging Refits, Coef Dispersion & Rolling EWMA Smoothing (July 2026)
- **CPCV-Bagged Refit & Blending**: Bagging over all 15 validation folds. Blending parameter `w` tuned OOS to combine single refit and bagged model.
- **Coefficient Dispersion**: Saves std of active coefficients across CPCV folds and bootstrap samples to JSON and joblib.
- **Cross-Quarter EWMA Smoothing**: `train_rolling.py` applies EWMA smoothing ($[0.5, 0.3, 0.2]$ weight decay) to model coefficients and scaler statistics.
- **Smart Plot/Report Skips & Parallelization**: Skip existing plots. `generate_rolling_report.py` parallelizes via `joblib.Parallel(backend="loky")`.
- Run full rolling retraining: `python3 day-model/train_rolling.py -e all --trials 200`

## Rolling Model Selection Filtering (July 2026)
- **Precedence Bug**: Previously, `backtest_simulator.py` glob-matched all rolling models. Alphabetical sorting caused the baseline model (`linear_..._r{quarter}.joblib`) to take precedence over the blended model (`linear_..._r{quarter}_sortino_blended.joblib`), blocking the latter during date-range stitching.
- **Filtering Fix**: Both `backtest_simulator.py` and `generate_rolling_report.py` are updated to filter for and load only the champion `_sortino_blended` configuration. Non-blended baseline models remain untouched on disk and are still loaded for static model comparisons.
- **Short-side Mapping**: Fixed potential path mismatches in `backtest_simulator.py` for rolling early models by directly mapping the long tag to the short tag via string replacement of `_long` with `_short`.

## Frozen-vs-CSS Experiment (July 2026)
A/B/C test of feature selection stability. Answers: does a frozen handpicked feature set beat quarterly CSS? See [frozen_vs_css.md](file:///home/hallo/Documents/option-longterm/day-model/frozen_vs_css.md).

**Verdict: Case 3** — neither frozen arm significantly beats CSS (Wilcoxon p = 0.87 for handpick, p = 0.37 for random). Feature reselection is NOT the source of pipeline instability. Quarter effect dominates variance decomposition (~17-33%). Do not invest in frozen feature sets for this pipeline.

- `train_etf` extended with three optional params (defaults preserve production behavior):
  - `frozen_features: list = None` — bypass CSS, use provided feature names; VIF + cond pruning still apply
  - `artifact_subdir: str = ""` — write model/scaler/results to `{ROLLING_MODELS_DIR,ROLLING_DATA_DIR}/{subdir}/`
  - `variant_tag: str = ""` — appended to model tag, isolates Optuna studies + caches
- Workflow:
  ```bash
  python3 day-model/build_frozen_features.py            # Build Arm B/C feature lists from historical CSS
  python3 day-model/train_frozen_rolling.py --arm both --trials 100 --skip-existing  # Train 240 models
  python3 day-model/analyze_frozen_vs_css.py            # Wilcoxon + variance decomp + report
  ```
- **Arm B (Handpicked)**: features selected in >=6/8 historical quarters, topped up to median CSS size. 120/120 trained OK. Stored in `data/rolling/frozen_armB/`, `models/rolling/frozen_armB/`.
- **Arm C (Random placebo)**: random sample of same size, seed 42 + per-ETF hash. 112/120 trained (8 collapses — random features lack bootstrap stability).
- Artifacts: `data/frozen/{arm_b_handpicked,arm_c_random,frozen_features_summary,arm_metrics_thr90}.json/.csv`.

## Block-Bootstrap CIs & Regime warnings for OOS (July 2026)
- **Problem**: Per-quarter out-of-sample (OOS) metrics have high noise ($n \approx 60$ days). Pre-lockbox validation IC decay warning system is anti-correlated with reality.
- **Solution**: 
  - Wrap 95% circular block-bootstrap confidence intervals (block size $= 5$ days, $B = 1000$) around quarterly Sharpe and Spearman IC. Flag any interval spanning zero with `*`.
  - Replace warning system with ex-ante market-state indicators: VIX level (>25% warning, >30% alert), VIX percentile (>85% warning, >95% alert), VIX acceleration (>3% warning), and average cross-ETF returns correlation breakdown (<0.65 warning, <0.55 alert).
- **Parallelized Evaluation**: Model evaluation step in `generate_rolling_report.py` parallelized using `joblib.Parallel` (`backend="loky"`) to offset cost of $B=1000$ bootstrap iterations.
- **Findings**: Most quarterly metrics span zero, confirming high uncertainty of short-term point estimates. VIX/cross-ETF warnings properly flag periods of market stress (e.g. ALERT status in 2024Q1).

## HMM Regime Tagging Research (July 2026)
- **Problem**: Rolling model evaluation is highly variable across quarters (due to regime shifts).
- **HMM Setup**: Fit Gaussian HMM with $K \in \{2, 3, 4\}$ states on CSI 300 returns and volatility features (`yesterday_return` + `vol20` or `vix`).
- **Fit Scopes**: Tested on OOS only (2024-2026) and 10-year extended history (2016-2026). Quarter assignments are identical and highly stable between both.
- **Variance Explained**: On the 10-year history (41 quarters), `yesterday_return` + `vol20` ($K=4$) explains **10.4%** of the quarterly Sharpe ratio variance (unbiased variance reduction is **+3.1%**).
- **State mapping ($K=4$)**:
  - Regime 1 (10 quarters): Chop/drawdown. Mean Sharpe: **-0.82**. (Avoid/gate state).
  - Regime 0 (13 quarters): Med/flat. Mean Sharpe: **+0.50**.
  - Regime 3 (8 quarters): Strong bull. Mean Sharpe: **+1.77**.
  - Regime 2 (10 quarters): Super trend. Mean Sharpe: **+3.49**. (Maximize exposure state).
- **Verdict**: Yes, Sharpe variance shrinks significantly within HMM regimes. Proceed to MS-GARCH vol-regime gating.

## Multi-scale GARCH Volatility Gating (July 2026)
- **Concept**: A look-ahead free gating layer based on multi-scale volatility states to scale trade sizes and thresholds dynamically.
- **Workflow**:
  1. `garch_regime.py` resamples 5m index bars to Daily, 2-hourly, and 1-hourly returns.
  2. Fits GARCH(1,1) conditional volatility on each scale and annualizes them.
  3. Fits a 3-state HMM on GARCH vol features, dynamically sorting states: State 0 (Calm, ~14% vol), State 1 (Turbulent, ~20% vol), State 2 (Crisis, ~35% vol).
  4. Saves look-ahead free signal (yesterday's state applies to today's trade) to `data/garch_regimes_{etf}.parquet`.
- **Gating Rules (`backtest_simulator.py` + `generate_rolling_report.py`)**:
  - Calm (State 0): default threshold (e.g. 90%), size = 1.0.
  - Turbulent (State 1): `--turbulent-thr` (default 92%), `--turbulent-size` (default 0.8).
  - Crisis (State 2): `--crisis-thr` (default 98%), `--crisis-size` (default 0.2).
- **Commands**:
  ```bash
  python3 day-model/garch_regime.py -e all -f                            # Rebuild all GARCH caches
  python3 day-model/backtest_simulator.py --etf 300ETF --garch-gate      # Sim with gating active
  python3 day-model/generate_rolling_report.py --no-plots --garch-gate   # Compile report with gating
  ```
- **Results**: On `300ETF` OOS, GARCH gating reduces Max Drawdown by **33.7%** (from 662.39 bps to 439.36 bps) and improves 2025 Sharpe from **0.33** to **2.25**.

## Multi-scale GARCH Volatility Features (July 2026)
- **Predictor Features Added**:
  - `garch_vol_daily`, `garch_vol_2h`, `garch_vol_1h`: Annualized GARCH(1,1) conditional volatilities from Daily, 2-hourly, and 1-hourly scales.
  - `garch_state`: 3-state HMM volatility regime state (0=Calm, 1=Turbulent, 2=Crisis).
  - `garch_vol_daily_diff`, `garch_vol_2h_diff`, `garch_vol_1h_diff`: 1-day change in GARCH volatility at each scale (vol-of-vol velocity).
- **Look-Ahead Safety**: Features are merged on daily indicators and shifted by 1 day (`T-1`), ensuring zero forward leakage at entry time.

