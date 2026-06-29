# Project JEPI-CN — Option Longterm Investment

Covered Call + Bull Put Spread on 50/300/500/588000/159915 ETF.

## Commands

```bash
source venv/bin/activate                    # Activate env
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
day-model/                     # Day-Model PM session return predictor
├── REPORT.md                  # Comprehensive PM return prediction report
├── AGENTS.md                  # Feature expansion and workflow guide
├── build_features.py          # Early-bar + day-level feature engineering (130 features, local caching)
├── features_extra.py          # 115 Numba njit extra features (early-bar, day-level, yesterday-mirror)
├── train_model.py             # Optuna-tuned linear model training & feature selection
├── feature_select.py          # Stability + LightGBM-importance selectors
├── gating_model.py            # Big-move gating classifier
├── evaluate_gating.py         # Compile gating winner table + WF PR-AUC grid report
└── generate_report.py         # Report markdown generator
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
- **130 Features**: 48 early-bar intraday, 60 day-level, 22 prior-day features (shifted 1 day).
- **Volume Normalization**: Early-morning volume normalized by rolling 20-day daily volume shifted by 1 day (`yesterday_rolling_20d_daily_volume / 48`).
- **VIX/IV Spread**: `vix_iv_spread = vix - iv`. Missing VIX backfilled via `iv + mean_bias`.

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