# Project JEPI-CN — Option Longterm Investment

Covered Call + Bull Put Spread on 50/300/500/588000/159915 ETF.

## Commands

```bash
source .venv/bin/activate                    # Activate env
python3 update_data.py                      # Pull ETF/option data from rqdatac
python3 download_5m_data.py                # Download 5m data
python3 download_1m_data.py                # Download 1m data (zstd level 5 compressed)
python3 download_index_data.py             # Download 1d, 5m, 1m Index data (for signals)
python backtest_put.py [50|300|500] --alpha    # Run daily alpha-hedging backtest
python backtest_put.py 300 --no-filter         # Run daily baseline (hedge every cycle)
python backtest_put.py 300 --limit-entry       # Run daily backtest with BS limit entry
python backtest_put.py 300                     # Run daily static filter backtest
python research_put_filters.py -e 300         # Evaluate put filters (synthetic)
python research_put_filters.py -e 300 --level 3  # Eval put filters OTM3
python optimize_put_filters.py 300            # Optimize put filters (real data)
python optimize_put_filters.py 300 --sweep-levels  # Sweep put OTM levels & filters
python research_filter_validation.py          # Validate filters on 30d forward returns
python research_indicator_scanner.py           # Scan indicator quantiles (no look-ahead)
python backtest_covered_call.py --alpha 300   # Call backtest (dynamic alpha mode)
python backtest_covered_call.py 300 --model-offset  # Call backtest with model limit orders
python predict_open_high.py -e 300          # Train open-high model
python predict_open_high.py -e 300 --pool   # Train pooled model (all ETFs)
python predict_open_high.py -e 300 --predict # Predict limit offset
python research_limit_entry.py -e 300       # Validate put limit entry
python research_open_high.py               # Open-to-high distribution plots
python research_otm_levels.py -e 300        # OTM level analysis with filters
python research_synthetic_otm.py -e 300     # Synthetic OTM & signal search
python alpha_finder.py                      # 30d forward return dist
python research_otm_no_filter.py -e 300     # Baseline OTM (no filter)
python optimize_alpha_synthetic.py -e 300   # Grid search synthetic alpha (6-score)
python optimize_filters.py 300              # Grid search real call filters (6-score)
python eval_synth_filters.py -e 500        # Eval synthetic filters (bootstrap)
python eval_synth_combinations.py -e 300   # Search synthetic filter combos
python evaluate_combinations.py -e 300     # Search real filter combos
python3 diagnose_500etf.py -e 500           # 500ETF multi-variant diagnostics
python3 optimize_put_alpha.py -e all        # Optimize put alpha weights/horizons (IS objective)
python3 optimize_put_alpha.py -e 300 --max-weight 0.5 # Run with weight cap (regularization)
python3 optimize_put_alpha.py -e 300 --walk-forward   # Walk-forward diagnostic (per-fold IS-opt -> OOS)
python3 optimize_put_alpha.py -e all --select-by-oos  # SELECT by mean OOS across purged folds
python3 optimize_put_alpha.py -e 300 --select-by-oos --expanding-pct  # Adaptive expanding-window percentiles
python alpha_model_ml.py -e all              # Train Phase 2 LightGBM regime models
python alpha_model_hybrid.py -e 300          # Phase 3 rule-anchored hybrid AUC report
python validate_alpha_pnl.py -e all --phase 1 --cadence cycle  # Put P&L validation, Phase 1
python validate_alpha_pnl.py -e 300 --phase 2 --cadence cycle  # Put P&L validation, Phase 2 (ML)
python validate_alpha_pnl.py -e 300 --phase 3 --cadence cycle  # Put P&L validation, Phase 3 (hybrid)
python validate_alpha_pnl.py -e 300 --phase 1 --cadence daily  # Daily-cadence validation
python compare_alpha_phases.py               # Cross-phase comparison -> backtest/alpha_phase_comparison.md
python day-model/gating_model.py -e all -t 20 --jobs 5   # Train gating models (3 variants x 3 selectors)
python day-model/evaluate_gating.py                     # Compile gating winner + WF PR-AUC report
python -m daytrade.calibrate --all-modes --sweep-gated   # Full sweep: 3 modes x 2 gated in one pool
python -m daytrade.deploy                                # Mixed-mode deploy (auto-picks +gated per side)
python -m daytrade.gating_only                           # Gate-only diagnostic backtest
python -m daytrade.methods.download_futures_data         # Download index futures 5m data
python -m daytrade.methods.report                        # Generate execution placement evaluation report
python day-model/sweep/meta_optuna.py -e all --trials 200 --bootstrap-jobs 4  # Meta-Optuna: tune 5 pipeline constants
python3 day-model/train_model.py -e 300 --trials 100 --skip-step 2  # Train with Step 2 filter skipped (Step 1 skipped by default)
python3 day-model/backtest_simulator.py --etf all --long-thr 70 --short-thr 70 [--type {ETF,Future}] # Run lightweight look-ahead free OOS backtest
python3 day-model/train_rolling.py -e all          # Train 8 quarterly rolling models (2024-2025)
python3 day-model/train_rolling.py -e all --skip-existing  # Resume: skip already-trained models
python3 day-model/generate_rolling_report.py         # Comprehensive rolling report (IC + strategy returns)
python3 day-model/backtest_simulator.py --etf all --rolling [--type {ETF,Future}]  # OOS backtest with rolling model selection
```

## Project Structure

```
backtest/                      # Model files and plots
├── open_high_model_{N}.json   # P10 model metadata
├── open_high_lgb_{N}_bag{i}.txt  # LightGBM bags
validate/                      # Validation reports
data/                          # Parquet files
├── {ETF}_instruments.parquet  # Contract metadata
├── {ETF}_historical_prices.parquet  # Daily correct strike/multiplier
├── {ETF}_1d.parquet           # Underlying daily (unadjusted + post-adjusted)
├── {ETF}_5m.parquet           # 5m ETF prices
├── {ETF}_1m.parquet           # 1m ETF prices (zstd level 5 compressed)
├── {ETF}_historical_prices_5m.parquet # 5m Option prices
├── 30d_iv_cache_{N}.parquet   # ATM IV cache
└── rq_vix.parquet             # Ricequant VIX indices cache (all 5 ETFs)

backtest_engine.py                # Core backtest engine
backtest_strategies.py            # CallStrategy & PutStrategy definitions
backtest_covered_call.py          # Covered call script
backtest_put.py                   # Daily protective put script
backtest_put_old.py               # Cycle-centric put script (old)
alpha_model.py                 # 4-Type Decision Matrix indicators & scoring (Phase 1)
optimize_put_alpha.py          # Weight/horizon optimizer (OOS-select + IS objective)
alpha_model_ml.py              # Phase 2 LightGBM regime models (monotone+bagged+isotonic)
alpha_model_hybrid.py          # Phase 3 rule-anchored hybrid (logistic stack)
validate_alpha_pnl.py          # Put P&L validator vs 3 baselines (real option prices)
compare_alpha_phases.py        # Cross-phase P&L comparison report
predict_open_high.py           # Open-to-High prediction pipeline
numba_utils.py                 # Numba BS functions & IV solver
penalties.py                   # Custom skglm penalties (e.g., MCP_plus_L2)
day-model/                     # Day-Model 10:00-14:35 return predictor
├── REPORT.md                  # Comprehensive return prediction report (static)
├── ROLLING_REPORT.md          # Rolling strategy report (IC + P&L + Sharpe + warnings)
├── AGENTS.md                  # Feature expansion and workflow guide
├── day-model_plan.md          # First-principles modeling & selection plan
├── build_features.py          # Early-bar + day-level feature engineering (214 features by default, local caching)
├── features_extra.py          # 115 Numba njit extra features (early-bar, day-level, yesterday-mirror)
├── train_model.py             # Optuna-tuned linear model training & feature selection (first principles)
├── train_rolling.py           # Rolling quarterly training orchestrator (8 quarters, skip-existing, parallel)
├── gating_model.py            # Big-move gating classifier
├── evaluate_gating.py         # Compile gating winner table + WF PR-AUC grid report
├── generate_report.py         # Report markdown generator (static)
├── generate_rolling_report.py # Rolling strategy report (IC + P&L + Sharpe + plots + warnings)
├── backtest_simulator.py      # Lightweight OOS backtest (static + rolling model selection)
├── models/rolling/            # Rolling model artifacts (linear_{tag}_r{YYYYMM}.joblib)
├── data/rolling/              # Rolling results JSON
├── plots/rolling/{YYYY}Q{Q}/ # Rolling per-quarter diagnostic plots
└── sweep/                     # Pipeline constant tuning
    ├── meta_optuna.py         # Optuna study over all 5 pipeline constants + model hyperparams
    ├── sweep_constants.py     # Single-constant grid sweep (legacy)
    └── meta_*_results.csv     # Per-ETF sweep result CSVs
daytrade/                      # Frozen-Linear Intraday Alpha Strategy
├── AGENTS.md                  # Strategy details, parameters, guide
├── REPORT.md                  # Calibration and performance report
├── improvement_plan.md        # Dual-model research findings & v2 results
├── GATING_ONLY_REPORT.md      # Gate-only vs gated-daytrade comparison
├── __init__.py                # Strategy parameters and paths
├── scores.py                  # Frozen score compute + IC verification
├── rules.py                   # Signal rules (single/hybrid/dual modes)
├── backtest.py                # Daily 5m intraday simulator
├── calibrate.py               # Per-side threshold optimizer
├── deploy.py                  # Phase 4 best-of-mode deployment
├── gating_loader.py           # Loads gating artifacts -> boolean fire mask
├── gating_only.py             # Gate-only standalone diagnostic backtest
├── report.py                  # Report generator
└── methods/                   # Execution & placement research module (isolated)
    ├── AGENTS.md              # Workflow & script guide
    ├── download_futures_data.py # Futures 5m downloader via rqdatac
    ├── cost_model.py          # Transaction cost & slippage models
    ├── option_pricing.py      # Intraday option pricer (BS & real 5m quotes)
    ├── eval_execution.py      # Multi-instrument backtest engine
    └── report.py              # Comparative report generator
```

### Day-Model Features & Caching
- **Index Signals**: Technical indicators use daily/intraday Index data (`000016.XSHG`, `000300.XSHG`, `000905.XSHG`, `000688.XSHG`, `399006.XSHE`) to prevent look-ahead bias. Execution uses ETF prices.
- **Local Cache**: Ricequant data (Margin, Capital Flow, Northbound Quota, VIX) cached in `data/*.parquet`.
- **214 Features**: 317 candidate features, pruned to 214 by default after moving 103 zero-stability features to deprecate_features.py.
- **Volume Normalization**: Early-morning volume normalized by rolling 20-day daily volume shifted by 1 day (`yesterday_rolling_20d_daily_volume / 48`).
- **Multicollinearity & Complexity Control**: Controls multivariate collinearity via iterative VIF pruning (threshold <= 10.0) on stable representatives. Overfitting is prevented via a dynamic active feature cap tied to Effective Sample Size (active_features <= ESS / 8.0) and a hard active feature floor (active_features >= 5) evaluated as signed constraints via Optuna's `constraints_func` for TPESampler. Gini weight concentration constraint is softened into the objective as a $k$-normalized soft penalty. Data leakage and search-budget overfitting are eliminated by:
  - Tightening univariate screening (BH-FDR = 0.15, loosened to 0.25 for 588000ETF to prevent feature starvation).
  - Nesting feature selection and CPCV folds strictly inside a chronological selection train split (excluding the validation blocks and a 10-day embargo).
  - Splitting the 6 validation blocks into 4 **Inner Validation** blocks (Optuna tuned) and 2 **Outer Validation** blocks (held-out holdout sanity check).
  - Tuning parameter `gamma` bounds for `MCP_plus_L2` in range `[1.5, 10000.0]` to allow smooth transition from aggressive non-convex thresholding to convex L1 shapes.
  - Selecting winning trial using running **Deflated Objective** (Lopez de Prado overfit adjustment) and robust parameter plateau search (requiring at least 8 total neighbors and 6 valid neighbors, gated dynamically at 15% and 10% of completed type counts to prevent isolated trials from scoring as plateaus; falls back to raw best trial if criteria not met).
  - Parallel Optuna worker samplers initialized with unique seeds (`PILOT_SEED + i` for pilot, `PILOT_SEED + 1 + i` for main study) to eliminate parallel race duplicate trials.

> Artifacts: `backtest/alpha_put_models.json`, `backtest/alpha_ml_models/`, `backtest/validate_pnl_phase{1,2,3}.json`, `backtest/alpha_phase_comparison.md`.

## Architecture

### Data Rules
- **Option strikes/multipliers**: Use daily-correct values from `_historical_prices.parquet`. Do NOT overwrite with instruments metadata.
- **ETF daily prices**: Option matching & settlement use unadjusted prices (`close`, `open`).
- **Technical indicators & forward returns**: Use post-adjusted prices (`close_adj`, `open_adj`).
- **`prev_close` calculation**: Shift `close_adj` (`df['prev_close'] = df['close_adj'].shift(1)`).
- **ATM 30d IV Speedup**: Pre-grouped dictionaries bypass slow filters.

### Call Strategy
- Cycles: Monthly expiry. Enter first trading day after expiry.
- IV Rank (252-day): High IVR -> wider OTM offset.
- Dynamic Alpha Mode (`--alpha`): Signal strong -> Combo A (OTM2+OTM3). Signal weak -> Combo B (OTM4). `roc20` protects against sharp rally.

### Put Strategy (Selective Hedge)
- Cadence: Daily indicator scanning. Mid-cycle entry, hold to expiry.
- Trigger: Dynamic alpha threshold or daily static filter.
- OTM Level: Level 1 (OTM1/ATM) for Fall regimes (`reg1`/`reg2`), Level 2 (OTM2) for Crash regimes (`reg3`/`reg4`).

### Limit Entry Models
- **Calls (`--model-offset`)**: Predict open-to-high P10 (bagged LightGBM + vol-regime calibration). Set sell limit order.
- **Puts (`--limit-entry`)**: Predict max ETF high return via daily model. Solve open option IV. Map to target option limit price.

### Put Alpha Model (4-Type Decision Matrix)
- 4 regimes: ST/MT Fall, ST/MT Crash.
- Rolling 252-day percentile rank: Normalizes indicators to `[0.0, 1.0]`. `--expanding-pct` switches to adaptive expanding window.
- Score: Weighted sum of active normalized indicators. Capped maximum weight (`--max-weight 0.5`).
- Dynamic Threshold: $T_t = T_{base} + \gamma \times (\text{iv\_vol\_ratio}_t - 1.0)$.
- Selection: `--select-by-oos` picks config by mean OOS metric across purged expanding folds. Saved in `backtest/alpha_put_models.json`.

### Put Alpha Model — 3 Phases
- **Phase 1** (`alpha_model.py` + `optimize_put_alpha.py`): Linear weighted score. Composite objective (Spearman rank + log placement + complexity penalty).
- **Phase 2** (`alpha_model_ml.py`): LightGBM binary classifier per regime. Monotone constraints, 5-bag bootstrap ensemble, isotonic calibration, walk-forward training.
- **Phase 3** (`alpha_model_hybrid.py`): Logistic stack of Phase 1 rank, Phase 2 prob, FINDINGS rule flags.
- **Validator** (`validate_alpha_pnl.py`): Real put option P&L vs 3 baselines. `deployable = net_pnl > 0 AND Sharpe > 0 AND per_trig > 0 AND beats_static`.

### Scoring
- **Call filters**: 6-component score (Sharpe 20%, P&L 15%, MaxDD 15%, WinRate 15%, Placement 15%, FilterLift 20%).
- **Put filters**: Profit-first score (P&L 35%, FilterLift 30%, Sharpe 15%, MaxDD 10%, WinRate 5%, Placement 5%).

## Backtest Results

### Calls-Only Mode
| ETF | Win Rate | Baseline P&L | Optimized P&L | Filter Condition |
|-----|----------|--------------|---------------|------------------|
| 300ETF | 56% | +19,178 | +16,868 | RSI 25-72 & MACD < 0 |
| 500ETF | 42% | +12,201 | +16,954 | RSI > 30 & Close < BBU & Close > SMA50 |
| 50ETF | 32% | +11,922 | +7,317 | RSI 30-60 & ROC10 < 3% & Vol20 < Vol20_med |

### Put Hedging & Limit Entry
| ETF | Mode | Win Rate | P&L | Call Fill | Put Fill |
|-----|------|----------|-----|-----------|----------|
| 300ETF | Calls + Model Offset | 56% | +20,492 | 99.0% | - |
| 300ETF | Calls + Put + Limits | 46% | +11,469 | 99.3% | 94.9% |
| 500ETF | Calls + Model Offset | 42% | +19,046 | 92.1% | - |
| 50ETF | Calls + Model Offset | 32% | +9,119 | 100.0% | - |

## Key Parameters
- `SPREAD_HALF = 0.01` (1% slippage)
- `COMMISSION = 2.0 RMB` (per leg)
- `ETF_SHARES = 20,000`
- `IV_THRESHOLD = 0.20`
- `RISK_FREE = 0.02`

## Data Dependencies
- Requires `rqdatac`. Run `python3 update_data.py`, `python3 download_5m_data.py`, `python3 download_1m_data.py`, `python3 download_index_data.py`.

## Research Notes
- **500ETF**: High volatility (~26.8%). Sharp rallies trigger assignment loss. Raising RSI threshold to 70 helps. Details in [RESEARCH_500ETF.md](file:///home/hallo/Documents/option-longterm/RESEARCH_500ETF.md).
- **Tail Risk (Puts)**: Vol acceleration + negative skewness predict downside. Details in [FINDINGS.md](file:///home/hallo/Documents/option-longterm/FINDINGS.md).
- **Day Trading**: See [day-trading/AGENTS.md](file:///home/hallo/Documents/option-longterm/day-trading/AGENTS.md) and [day-trading/REPORT.md](file:///home/hallo/Documents/option-longterm/day-trading/REPORT.md).
- **Daytrade v2**: Mixed-mode deployment with baseline-guided safety stops improves total OOS Sharpe from +28.60 to +37.47. Details in [daytrade/improvement_plan.md](file:///home/hallo/Documents/option-longterm/daytrade/improvement_plan.md).
- **Daytrade v5**: Added structural opening support/resistance stop loss and dynamic take-profit exit bar sweeping. Deployed pooled WF Sharpe increased to +42.13.

## TODO
- [ ] Improve put buy strategy: [put_improvement_plan.md](file:///home/hallo/Documents/option-longterm/put_improvement_plan.md)

## Daytrade Features Expansion (Mined Features)
- Added 30 early-bar intraday features using Numba njit (features_extra.py).
- Added daily options indicators (Volume P/C, Open Interest growth, Term Structure, Corridor Width) in compute_daylevel_indicators (build_features.py).
- Added technical indicators (TD setup, BB width, inside/outside bars, WaveTrend, Keltner squeeze, Stochastic RSI, sentiment rotations) to daily indicators.
- Total active day-model features pruned from 264 to 214. Verification completed on all 5 ETFs.
- Re-trained linear Optuna-tuned prediction models successfully (saved in day-model/models/).

## Day-Model Side-Specific Objective (July 2026)
- Feature pipeline (screening → CSS → VIF → CPCV) **unchanged**. Only validation objective and lockbox Tail IC are side-aware.
- Sides: `single` (legacy two-sided), `long` (`pred >= P90(pred)`), `short` (`pred <= P10(pred)`).
- `--both` flag is **default** in `train_model.py`: trains all three sides (`single`, `long`, and `short`) per ETF in one invocation. Use `--no-both --side {single|long|short}` to train one side only.
- Weights: `single` `[0.40, 0.40, 0.15, 0.05]`; `long`/`short` `[0.45, 0.45, 0.10, 0.00]` (V4 dropped, renormalized).
- CV fold M1..M6 metrics and kill-switches stay two-sided for all sides.
- Tag becomes `{ETF}_{side}` for long/short (e.g., `300ETF_long`); models/scalers/results live side-by-side with `single`.
- Pilot cache key is side-scoped via hash: `"v10"` for `single` (preserves legacy cache byte-identical), `"v11_side", side` prefix for long/short.
- `generate_report.py` emits ONE 15-panel diagnostics figure per ETF per side: `diagnostics_{etf}_{side}.png`. Lockbox Tail IC is side-aware.
- Run: `python3 day-model/train_model.py -e all --trials 100` (default trains all 5 ETFs and all 3 models/sides each).

## STAR 50 Index Proxy Fallback (July 2026)
- Modified index downloader to fetch `000688.XSHG` daily price history starting from its base date `2019-12-31`.
- Added fallback proxy logic to `build_features.py` to use index 5m data when ETF 5m data is missing.
- Expands the `588000ETF` dataset from 1294 to 1371 samples and starts training history on `2020-10-23` (after 60 days warmup) instead of `2021-02-09`.

## Early Target (10:00 ~ 13:05) Window (July 2026)
- Exit Bar changed from 42 (14:35 close) to 24 (13:05 close, close of the 13:00~13:05 bar).
- Pipeline commands support `--early` parameter to execute the early target flow.
- Early output files suffix everything with `_early` to isolate them (e.g. `features_{ETF}_early.parquet`, `linear_{tag}_early.joblib`, `REPORT_early.md`, `plots/diagnostics_{tag}_early.png`).
- Run: `python3 day-model/build_features.py -e all --early`, `python3 day-model/train_model.py -e all --trials 100 --early`, `python3 day-model/generate_report.py --early`, `python3 day-model/backtest_simulator.py --etf all --early [--type {ETF,Future}]`.

## Day-Model Tail-Sharpe Optimization & Win Rate Kill-Switch (July 2026)
- **Validation Tail Sharpe Objective**: Optimizes Optuna hyperparameters using validation set tail-Sharpe (winsorized 1-99% clip on active days, annualized by $\sqrt{244}$) instead of Tail IC. It uses month-block bootstrap resamples to penalize standard error. Default weights: `single` `[0.10, 0.35, 0.10, 0.05, 0.40]`; `long`/`short` `[0.10, 0.40, 0.10, 0.00, 0.40]`.
- **CV Fold Win Rate Kill-Switch**: Adds a hard constraint that the CV fold average tail win rate after 15 bps cost must be $\ge 45\%$. Add side-specific win rate constraint for `long` and `short` sides.
- **CLI Defaults**: `PILOT_N_TRIALS = 200` for stability. Default `--target-transform` is set to `"none"`. Default `--sharpe-objective` is set to `False` (Validation Tail IC remains the standard default).
- **Performance**: No significant uplift. OOS P&L delta 95% CI `[-755, +664] bps`, Sharpe delta CI `[-0.54, +0.54]` — statistically indistinguishable from zero. Default (Tail IC + raw returns) remains recommended; `--sharpe-objective` is experimental only.
- Run: `python3 day-model/train_model.py -e all --trials 100 --sharpe-objective` to enable the Sharpe-objective model training.
- Backtest: `python3 day-model/backtest_simulator.py --etf all` (loads the standard raw-return baseline by default). Use `--sharpe-objective` to load Sharpe-objective models.

## Sortino Ratio as Default V5 Objective (July 2026)
- **Sortino Ratio**: $S(\tau) = \frac{E[R]-\tau}{\sqrt{E[\min(R-\tau,0)^2]}} \times \sqrt{244}$. Uses downside deviation (only negative returns count as risk), so upside volatility is not penalized. (Note: the previous label "Kappa Ratio" was incorrect — Kaplan & Knowles Kappa₂ uses $\sqrt{E[(R-\tau)^+{}^2]}$ in the numerator, not $E[R]-\tau$.)
- **Sweep Results** (aggregate across 5 ETF × 3 sides): Default weight 0.40 is the best sortino variant — OutTIC +23% over Sharpe baseline (0.1085 vs 0.0882), IC generalization gap tightened 34% (-0.040 vs -0.060). Lower sortino weights (0.20, 0.30) dilute the tail benefit. Sharpe weight overrides (`_sw*`) and `--sharpe-objective` both underperform sortino on OutTIC.
- **Default**: `--ratio-type sortino` (was `sharpe`). Use `--ratio-type sharpe` to revert to total-volatility ratio.
- **Report cleanup**: `_sharpe`, `_sw*`, `_sortino_sw*`, `_emb*` suffix variants are filtered from `generate_report.py` (underperform parent configs). Only baseline + sortino appear in REPORT.md.

## Deflated Sharpe Ratio — PSR/DSR Overfit Correction (July 2026)
- **Probabilistic Sharpe Ratio (PSR)**: López de Prado & Bailey (2014) formula with skewness and excess-kurtosis terms: $\Phi\!\left(\frac{(\hat{SR} - SR_0)\sqrt{T-1}}{\sqrt{1 - S\cdot\hat{SR} + \frac{K+2}{4}\hat{SR}^2}}\right)$. Replaces the ad-hoc Gaussian-only correction.
- **Deflated Sharpe Ratio (DSR)**: Sets $SR_0 = E[\max_N(SR)]$ via Gumbel approximation.
- **Trial Correlation Correction**: `dynamic_rho` (average off-diagonal correlation of per-fold CV OOS IC vectors) reduces the overfit penalty via $\sqrt{1-\rho}$. The search-budget term $\sqrt{2\ln N}$ uses **raw trial count** N, NOT the ONC effective-N (which collapses to ~1 for correlated Optuna trials and removes the overfit guard). Effective-N is printed as a diagnostic only.
- **Target-Transform Variants**: `_rank` and `_gauss` target transforms consistently degrade OOS performance and are filtered from the report. `--target-transform` remains available for research but is not recommended.
- **Output**: `results_{tag}.json` contains `dsr.probability`, `dsr.sr_benchmark`, `dsr.sr_hat`, `dsr.effective_n_trials`, `dsr.dynamic_rho`. Console prints DSR probability and trial correlation diagnostics.