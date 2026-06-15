# Option Longterm Investment - Project JEPI-CN

[中文文档](备兑期权.md)

This directory contains scripts and research for long-term option investment strategies on Chinese ETFs (50ETF, 300ETF, 500ETF). The system uses an **Engine + Strategy pattern** to support multiple option strategies with shared infrastructure:

- **Covered Call** (`backtest_covered_call.py`): Selling OTM calls with technical filters and dynamic alpha
- **Protective Put** (`backtest_put.py`): Selective put buying with optimized filters (only hedges when signals align)

## Core Strategy

### Covered Call (Short Calls)
The primary strategy is a **Covered Call with Technical Filters and Dynamic Alpha**, inspired by income-generating funds like JEPI, but adapted for the Chinese market (Project JEPI-CN).

- **Covered Call**: Selling OTM calls against held ETF shares to generate premium income.
- **Technical Filters**: RSI, Bollinger Bands, ROC, and ATR indicators filter out overbought conditions. If the market is overbought, selling calls is skipped (Skip OTM4) to avoid assignment risk during sharp rallies.
- **Dynamic Alpha Mode** (`--alpha`): Indicator-based combo switching between aggressive (OTM2+OTM3) and conservative (OTM4) call legs. Signals are derived from synthetic options research — see [alpha.md](alpha.md) for details.
- **Model-Based Limit Orders** (`--model-offset`): Replaces the fixed ±2% spread assumption with a data-driven limit order offset predicted by a quantile regression model, targeting 90% fill probability. Uses Black-Scholes mapping to set call sell limit prices, simulated against 5m bar data. Requires a pre-trained model (see below).
- **Strike Selection**: Driven by technical indicators (RSI, BBU, SMA50) in dynamic alpha mode, or by ATM Implied Volatility (IV) in standard mode.

### Protective Put (Long Puts, Selective Hedge)
A complementary strategy that **selectively buys protective puts** only when filter signals suggest market vulnerability:

- **Selective Hedging**: Filter pass → buy put at configured OTM level; filter fail → skip (P&L = 0). This avoids the constant premium drag of always-buying puts.
- **Optimized Filters**: Per-ETF conditions (e.g. 300ETF: `RSI < 60 AND Vol20 > median`) found via synthetic research → real-data validation pipeline.
- **Put Limit Entry** (`--limit-entry`): Uses the same open-high P10 model via BS mapping to set limit buy orders for protective puts, achieving ~95% fill rate.
- **Configurable OTM Level**: `--level N` controls how far OTM to buy (default Level 1 = closest OTM put).

## File Structure

### Reusable Backtest Architecture (Engine + Strategy Pattern)

The backtest system is split into a **shared engine** and **pluggable strategies**, making it easy to add new strategies without duplicating infrastructure code:

| File | Role | Reusable Components |
|------|------|--------------------|
| `backtest_engine.py` (~900 lines) | **Shared engine** — all infrastructure | `run_backtest()`, `calc_leg_pnl()`, `simulate_limit_order()`, `get_cycles()`, `load_data()`, BS/IV helpers (numba), plotting, CSV export |
| `backtest_strategies.py` (~360 lines) | **Strategy classes** | `CallStrategy`, `PutStrategy` — each implements a 5-method interface |
| `backtest_covered_call.py` (~50 lines) | **Thin wrapper** | CLI parsing + `CallStrategy` instantiation |
| `backtest_put.py` (~50 lines) | **Thin wrapper** | CLI parsing + `PutStrategy` instantiation |

**Adding a new strategy** (e.g. straddle, iron condor) requires only: (1) a new class in `backtest_strategies.py` implementing the 5-method interface (`evaluate_filter()`, `select_legs()`, `get_predict_limit_fn()`, `format_cycle()`, `mode_label()`), and (2) a thin wrapper `.py`. No engine changes needed.

### Backtest Output
- `backtest/backtest_cc_{ETF}*.png`: Covered Call visualizations (Equity curve, per-leg contribution, drawdown).
- `backtest/backtest_put_{ETF}*.png`: Protective Put visualizations.
- `backtest/backtest_*.csv`: Detailed trade logs with per-leg P&L.

### Limit Order Prediction (Open-High P10)
- `predict_open_high.py`: Production quantile prediction system that predicts the 10th percentile of the intraday `(High - Open) / Open` move. Supports cross-ETF pooled training (`--pool`), ensemble bagging (5 models), and vol-regime-conditional calibration. Used by the backtest via `--model-offset` (calls) and `--limit-entry` (puts).
- `research_open_high.py`: Static graphical analysis of the open-to-high distribution segmented by 5 overnight gap regimes.
- `backtest/open_high_model_{N}.json`: Trained model metadata (features, coefficients, coverage stats, vol-regime calibration offsets, bagged model paths).
- `backtest/open_high_lgb_{N}_bag{i}.txt`: Trained bagged LightGBM quantile model files (5 per ETF).
- `backtest/open_high_predictions_{N}.png`: Model validation visualizations (scatter, coverage calibration, feature importance).

### Put Filter Research
- `research_put_filters.py`: Synthetic put filter evaluation — 30+ filters, per-OTM-level breakdown, bootstrap CI, significance testing against baseline. Uses synthetic option data to prevent overfitting.
- `optimize_put_filters.py`: Real-data put filter optimizer — grid search over synthetic-informed filter space, 6-component composite score (Sharpe 20%, Total 15%, MaxDD 15%, WinRate 15%, Placement 15%, FilterLift 20%).

### Call Filter Research
- `research_synthetic_otm.py`: Synthetic OTM research with combo alpha analysis (OTM2+OTM3 vs OTM4 P&L) and 24-signal dynamic search.
- `research_otm_levels.py`: Research script to evaluate the performance of different OTM strike offsets under various market conditions.
- `research_otm_no_filter.py`: Baseline OTM performance research without technical filters.
- `optimize_filters.py`: Call filter grid search on real data (6-component composite scoring).
- `eval_synth_filters.py`: Evaluates individual filters on synthetic data (14 technical indicators).
- `evaluate_combinations.py`: Searches filter combinations on real option data.
- `eval_synth_combinations.py`: Searches filter combinations on synthetic data (27 combos, scores and ranks top 5).

### Documentation
- `alpha.md`: Dynamic alpha strategy research report — combo analysis, best signals per ETF, and real backtest validation.
- `备兑期权.md`: Comprehensive Chinese documentation — strategy details, backtest results, project structure, filter research, and architecture.
- `STRATEGY.md`: Legacy strategy reference.

### Utilities
- `numba_utils.py`: Performance-optimized functions for option pricing and metric calculations.

## Getting Started

### 1. Run Dynamic Alpha Research
Analyze combo P&L and find the best indicator signals for dynamic OTM switching:
```bash
python research_synthetic_otm.py -e 300   # Combo alpha + 24-signal dynamic search
```

### 2. Run Covered Call Backtest
Run a standard backtest for the 300ETF covered call strategy:
```bash
python backtest_covered_call.py 300
```

### 3. Run Dynamic Alpha Backtest
Run with indicator-based dynamic combo switching:
```bash
python backtest_covered_call.py --alpha 300
```

### 4. Train the Open-High Limit Order Model
Train the P10 quantile model that predicts the safe limit order offset with ~90% fill probability:
```bash
python predict_open_high.py -e 300   # Train for 300ETF (per-ETF, saves 5 bagged models)
python predict_open_high.py -e 50    # Train for 50ETF
python predict_open_high.py -e 500   # Train for 500ETF
python predict_open_high.py -e 300 --pool  # Optional: cross-ETF pooled training (~7200 samples)
```

### 5. Run Backtest with Model-Based Limit Orders
Use the trained model to set data-driven limit orders instead of the fixed ±2% spread:
```bash
python backtest_covered_call.py 300 --model-offset                 # Call limit orders (sell side)
python backtest_put.py 300 --limit-entry                           # Put limit orders (buy side)
```

### 6. Predict Today's Limit Order Offset
Get the model-predicted offset for today's market conditions:
```bash
python predict_open_high.py -e 300 --predict
```

### 7. Run Protective Put Backtest
Run a selective hedge put backtest (only buys when filter signals):
```bash
python backtest_put.py 300                   # Filtered put backtest
python backtest_put.py 300 --no-filter       # Always-buy baseline
python backtest_put.py 300 --limit-entry     # With BS mapping limit entry
```

### 8. Research Put Filters
Evaluate put filters on synthetic data, then validate on real data:
```bash
python research_put_filters.py -e 300        # Synthetic eval (30+ filters, bootstrap CI)
python optimize_put_filters.py 300           # Real-data grid search (composite score)
```

### 9. Analyze OTM Levels
Research the optimal OTM offsets:
```bash
python research_otm_levels.py -e 300
```

## Data Dependencies
The scripts expect data to be located in the `./data/` directory (relative to this folder).

## Open-High P10 Prediction Model

### Problem
When selling a covered call at market open, you place a limit sell order. The standard backtest assumes a fixed ±2% bid-ask spread (`exec_px = mid * 0.98`). In practice, you can set a tighter limit and still get filled if the underlying ETF rises enough during the day. The question is: **how high can you set your limit and still fill with 90% confidence?**

### Approach
`predict_open_high.py` predicts the **10th percentile** of `y = (High - Open) / Open × 100%`. If the ETF rises at least `p10%` from open with 90% probability, then a limit sell at `open × (1 + p10/100)` fills 90% of the time — giving you a better execution price than the fixed spread assumption.

### Pipeline
1. **Feature Engineering** — 25 candidate features from ETF daily data:
   - Overnight gap (`gap_pct`), RSI(14), realized vol(20d), normalized ATR(14)
   - Close/SMA50 ratio, MACD histogram, ROC at 5/10/20 days
   - Bollinger band width, volume ratio, day of week
   - **MA divergence**: `(open - EMA5) / EMA5` and `(open - EMA20) / EMA20` — measures how far the open price deviates from the trend
   - **Previous day features**: `prev_day_range`, `prev_open_to_high`, `overnight_gap_from_high`, `upper_shadow`, `lower_shadow`
   - **Momentum oscillators**: `stoch_k14` (Stochastic %K), `williams_r14` (Williams %R), `adx14` (ADX), `mfi14` (Money Flow Index), `cci20` (CCI)
   - **Tail risk**: `vol_skew20` (rolling 20d return skewness)

2. **Forward Feature Selection** — Greedy forward selection via 5-fold time-series cross-validation, minimizing pinball loss (quantile loss at q=0.10). Evaluates feature set sizes 1–6; picks the size with the best CV score.

3. **Dual-Model Training**:
   - **Statsmodels Quantile Regression** (linear, fully interpretable coefficients)
   - **LightGBM Quantile** (`objective='quantile'` — nonlinear, handles feature interactions)
   - If CV losses are within 5%, uses **ensemble average**; otherwise picks the winner

4. **Adaptive Quantile Search** — Binary search for q' (typically 0.03–0.04) that natively achieves 90% coverage, replacing the fixed q=0.10. This reduces systematic bias in the quantile prediction.

5. **Ensemble Bagging** — 5 LightGBM models trained on different bootstrap resamples, predictions averaged to reduce variance and overfitting.

6. **Vol-Regime-Conditional Calibration** — Separate calibration offsets for low-vol and high-vol regimes (split by median vol20). Applied based on current vol20 at prediction time. Achieves exactly 90.0% calibrated coverage.

7. **Block-Bootstrap Augmentation** — 20-day circular blocks, 1x ratio synthetic data to further reduce overfitting.

8. **Cross-ETF Pooling** (`--pool`) — Optional mode that trains on all 3 ETFs' data (~7200 samples) for more robust feature learning. Per-ETF calibration still applied via rolling validation.

9. **Rolling Validation** — Expanding-window backtest (retrain every 60 trading days) with bagged models. Reports empirical coverage (target: ~90%), mean predicted offset vs static per-regime baseline, and pinball loss.

10. **Model Serialization** — Saves to `backtest/open_high_model_{ETF}.json` (metadata + Statsmodels coefficients + vol-regime calibration) and `backtest/open_high_lgb_{ETF}_bag{0-4}.txt` (5 bagged LightGBM booster files) for use by the backtest engine.

### Trained Model Results (Jun 2026, v2 — bagged + vol-regime calibrated)

**Best features selected (per-ETF training):**

| ETF | Best Features | Model | Adaptive q | Calibrated Coverage |
|-----|--------------|-------|-----------|---------------------|
| 300ETF | `open_ema5_div`, `roc5`, `williams_r14`, `stoch_k14`, `rsi14`, `dow` | LightGBM (bagged x5) | 0.0362 | **90.0%** |
| 50ETF | `open_ema5_div`, `roc5`, `williams_r14`, `stoch_k14`, `close_sma50_ratio` | Ensemble (bagged x5) | 0.0362 | **90.0%** |
| 500ETF | `open_ema5_div`, `roc5`, `williams_r14`, `prev_open_to_high`, `overnight_gap_from_high`, `roc20` | LightGBM (bagged x5) | 0.0362 | **90.0%** |

**Key insights:**
- `open_ema5_div` (divergence of open from EMA5) is the #1 feature across all three ETFs. When open > EMA5 (gap up from trend), the intraday high tends to be relatively close to open (smaller high-open move). When open < EMA5 (gap down from trend), the high tends to be much higher due to mean-reversion bounces.
- `williams_r14` and `stoch_k14` are consistently selected across all ETFs, capturing momentum/overbought signals.
- 500ETF uniquely selects `prev_open_to_high` (autocorrelation of target) and `roc20` (medium-term momentum), reflecting its higher-volatility profile.

**Vol-regime calibration offsets:**

| ETF | Low-vol offset (vol20 ≤ median) | High-vol offset (vol20 > median) | Vol threshold |
|-----|-------------------------------|--------------------------------|---------------|
| 300ETF | -0.069% | -0.080% | 0.15 |
| 50ETF | -0.060% | -0.007% | 0.15 |
| 500ETF | -0.108% | -0.088% | 0.18 |

**Backtest call limit fill rates and P&L (`--model-offset`):**

| ETF | Mode | P&L | Call Fill Rate |
|-----|------|-----|----------------|
| 300ETF | Calls-only | **+20,492 RMB** | **99.0%** (95/96) |
| 300ETF | With-Put + Limit Entry | **+11,469 RMB** | **99.3%** (139/140) |
| 50ETF | Calls-only | **+9,119 RMB** | **100.0%** (98/98) |
| 500ETF | Calls-only | **+19,046 RMB** | **92.1%** (35/38) |

With limit orders there is no bid-ask spread slippage — the model predicts the P10 of the ETF's intraday high via BS mapping, then simulates against 5m bar data. The only transaction cost is commission (2 RMB/leg). This means you sell options at mid price instead of mid × 0.98, gaining ~2% premium per sell leg.
