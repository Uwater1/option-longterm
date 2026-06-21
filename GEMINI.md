# Project JEPI-CN — Option Longterm Investment

Covered Call + Bull Put Spread on 50/300/500/588000/159915 ETF.

## Commands

```bash
source venv/bin/activate                    # Activate env
python3 update_data.py                      # Pull ETF/option data from rqdatac
python3 download_5m_data.py                # Download 5m data
python3 download_1m_data.py                # Download 1m data (zstd level 5 compressed)
python backtest_put.py [50|300|500] --alpha    # Run new daily alpha-hedging backtest
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
python3 optimize_put_alpha.py -e 300 --walk-forward   # Walk-forward diagnostic (per-fold IS-opt → OOS)
python3 optimize_put_alpha.py -e all --select-by-oos  # **SELECT by mean OOS across purged folds (recommended)**
python3 optimize_put_alpha.py -e 300 --select-by-oos --expanding-pct  # Adaptive expanding-window percentiles
python alpha_model_ml.py -e all              # Train Phase 2 LightGBM regime models (monotone+bagged+isotonic)
python alpha_model_hybrid.py -e 300          # Phase 3 rule-anchored hybrid AUC report
python validate_alpha_pnl.py -e all --phase 1 --cadence cycle  # Put P&L validation, Phase 1, cycle cadence
python validate_alpha_pnl.py -e 300 --phase 2 --cadence cycle  # Put P&L validation, Phase 2 (ML)
python validate_alpha_pnl.py -e 300 --phase 3 --cadence cycle  # Put P&L validation, Phase 3 (hybrid)
python validate_alpha_pnl.py -e 300 --phase 1 --cadence daily  # Daily-cadence (needs TODO 4)
python compare_alpha_phases.py               # Cross-phase comparison → backtest/alpha_phase_comparison.md

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
└── 30d_iv_cache_{N}.parquet   # ATM IV cache

backtest_engine.py                # Core backtest engine
backtest_strategies.py            # CallStrategy & PutStrategy definitions
backtest_covered_call.py          # Covered call script
backtest_put.py                   # Daily protective put script (new 4-regime)
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
├── build_features.py          # Early-bar + day-level feature engineering (127 features, local caching)
├── train_model.py             # Optuna-tuned linear model training & feature selection
└── generate_report.py         # Report markdown generator
daytrade/                      # Frozen-Linear Intraday Alpha Strategy
├── AGENTS.md                  # Strategy details, parameters, and developer guide
├── REPORT.md                  # Calibration and performance report (with corrected drawdown metrics)
├── __init__.py                # Strategy parameters and paths
├── scores.py                  # Frozen score compute + IC verification
├── rules.py                   # Masked expanding percentile signal rules
├── backtest.py                # Daily 5m intraday simulator
├── calibrate.py               # Independent per-side threshold optimizer
└── report.py                  # Report generator
```

### Day-Model Caching & Features (New)
- **Data Caching**: Ricequant 3rd-party data (Securities Margin, Capital Flow, Northbound Connect Quota) is cached locally to `data/securities_margin.parquet`, `data/capital_flow.parquet`, and `data/stock_connect_quota.parquet` to prevent slow network calls and minimize API quota usage.
- **127 Features**: Expanded feature space includes 50 early-bar intraday features, 55 day-level features (including technical indicators and 3rd party margin/flow), and 22 yesterday's features (shifted by 1 day to prevent leakage).
- **Look-Ahead Bias Correction**: Normalizing early-morning volume features using a rolling 20-day historical daily volume shifted by 1 day (i.e. expected bar volume = `yesterday_rolling_20d_daily_volume / 48`) instead of the current day's full volume, ensuring strict chronological boundaries and eliminating look-ahead leakage.


> Also: `backtest/alpha_put_models.json` (Phase 1 weights+OOS), `backtest/alpha_ml_models/` (Phase 2 bags+manifests), `backtest/validate_pnl_phase{1,2,3}.json`, `backtest/alpha_phase_comparison.md`.

## Architecture

### Data Rules (Critical)
- **Option strikes/multipliers**: Use daily-correct values from `_historical_prices.parquet`. Do NOT overwrite with instruments metadata.
- **ETF daily prices**: Option matching & settlement must use unadjusted prices (`close`, `open`). Avoid mismatch.
- **Technical indicators & forward returns**: Use post-adjusted prices (`close_adj`, `open_adj`) to avoid split artifacts.
- **`prev_close` calculation**: Shift `close_adj` (`df['prev_close'] = df['close_adj'].shift(1)`) before taking `.tail()`.
- **ATM 30d IV Speedup**: Use pre-grouped dictionaries to bypass slow boolean filters.

### Call Strategy
- Cycles: Monthly expiry. Enter first trading day after expiry.
- IV Rank (252-day): High IVR -> wider OTM offset.
- Dynamic Alpha Mode (`--alpha`): Signal strong -> Combo A (OTM2+OTM3). Signal weak -> Combo B (OTM4). `roc20` protect against sharp rally.

### Put Strategy (Selective Hedge)
- Cadence: Daily indicator scanning. Mid-cycle entry, holds to expiry.
- Trigger: Dynamic alpha threshold or daily static filter.
- OTM Level: Level 1 (OTM1/ATM) for Fall regimes (`reg1`/`reg2`), Level 2 (OTM2) for Crash regimes (`reg3`/`reg4`).
- Level defaults: optimal OTM levels per ETF set by sweep optimizer.

### Limit Entry Models (Black-Scholes Mapping)
- **Calls (`--model-offset`)**: Predict open-to-high P10 (bagged LightGBM + vol-regime calibration). Set sell limit order.
- **Puts (`--limit-entry`)**: Predict max ETF high return via daily model. Solve open option IV. Map to target option limit price. Apply OTM cushion.

### Put Alpha Model (4-Type Decision Matrix)
- 4 regimes: ST/MT Fall, ST/MT Crash.
- Rolling 252-day percentile rank: Normalizes indicators to `[0.0, 1.0]` (no look-ahead). `--expanding-pct` switches to adaptive expanding-window percentiles.
- Score calculation: Weighted sum of active normalized indicators. Rescale weights if indicator missing.
- **Regularization**: Capped maximum weight (`--max-weight 0.5`) to prevent single-indicator dominance.
- **Dynamic Threshold**: Trigger threshold adjusted daily based on option cost: $T_t = T_{base} + \gamma \times (\text{iv\_vol\_ratio}_t - 1.0)$.
- **OOS Validation**: Expanding window walk-forward validation (`--walk-forward`) checks chronological test year stability.
- **OOS Selection** (recommended): `--select-by-oos` picks final config by mean OOS metric across **purged** expanding folds (drops train rows whose forward target leaks into test), not best in-sample.
- Config stored in `backtest/alpha_put_models.json`.

### Put Alpha Model — 3 Phases (OOS-validated)
**Phase 1** (`alpha_model.py` + `optimize_put_alpha.py`): linear weighted score. New composite objective (Spearman rank + log placement + complexity penalty). 18 normalized indicators incl. ATR ratio, vol-of-vol, range expansion, vol term structure, RSI divergence.
**Phase 2** (`alpha_model_ml.py`): per-regime LightGBM binary classifier (crash→`worst_dd<=-0.05`, fall→`fwd_ret<0`). Monotone constraints (+1 all features), 5-bag bootstrap ensemble, isotonic calibration, walk-forward expanding training. Outputs calibrated probability; threshold = avg per-fold train p85.
**Phase 3** (`alpha_model_hybrid.py`): logistic stack of [Phase1 rank, Phase2 prob, FINDINGS rule flags]. L2-reg (C=0.5), walk-forward. Rule anchoring = anti-overfit.
**Validator** (`validate_alpha_pnl.py`): real put option P&L per trigger vs 3 baselines (no-hedge / all-hedge / static filter). `--cadence cycle` (fair, monthly) or `daily` (needs TODO 4). Deployable = net P&L>0 AND Sharpe>0 AND per-trig>0 AND beats static filter.
**Result**: 4 of 12 ETF×regime cells deployable. See `backtest/alpha_phase_comparison.md`. Run `python compare_alpha_phases.py` to regenerate.


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
- `rqdatac` needed. Run `python3 update_data.py`, `python3 download_5m_data.py`, and `python3 download_1m_data.py`.

## Research Notes
- **500ETF**: Volatility too high (~26.8%). Sharp rallies cause major assignment loss. Raising RSI threshold to 70 helps slightly. Detailed in [RESEARCH_500ETF.md](file:///home/hallo/Documents/option-longterm/RESEARCH_500ETF.md).
- **Tail Risk (Puts)**: Vol acceleration + negative skewness predict downside. Detailed in [FINDINGS.md](file:///home/hallo/Documents/option-longterm/FINDINGS.md).
- **Day Trading**: [day-trading/AGENTS.md](file:///home/hallo/Documents/option-longterm/day-trading/AGENTS.md) [day-trading/REPORT.md](file:///home/hallo/Documents/option-longterm/day-trading/REPORT.md)

## TODO
- [ ] Improve put buy strategy: [put_improvement_plan.md](file:///home/hallo/Documents/option-longterm/put_improvement_plan.md)
- [ ] TBD