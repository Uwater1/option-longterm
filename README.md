# Option Longterm Investment - Project JEPI-CN

[中文文档](备兑期权.md)

This directory contains scripts and research for long-term option investment strategies, specifically focusing on **Covered Call** with technical filters (and no protective put) on Chinese ETFs (50ETF, 300ETF, 500ETF).

## Core Strategy
The primary strategy is a **Covered Call with Technical Filters and Dynamic Alpha**, inspired by income-generating funds like JEPI, but adapted for the Chinese market (Project JEPI-CN) to optimize performance.

- **Covered Call**: Selling OTM calls against held ETF shares to generate premium income.
- **Technical Filters**: RSI, Bollinger Bands, ROC, and ATR indicators filter out overbought conditions. If the market is overbought, selling calls is skipped (Skip OTM4) to avoid assignment risk during sharp rallies.
- **Dynamic Alpha Mode** (`--alpha`): Indicator-based combo switching between aggressive (OTM2+OTM3) and conservative (OTM4) call legs. Signals are derived from synthetic options research — see [alpha.md](alpha.md) for details.
- **Model-Based Limit Orders** (`--model-offset`): Replaces the fixed ±2% spread assumption with a data-driven limit order offset predicted by a quantile regression model, targeting 90% fill probability. Requires a pre-trained model (see below).
- **No Put**: Protective puts are removed to eliminate long-term premium drag, maximizing net income.
- **Strike Selection**: Driven by technical indicators (RSI, BBU, SMA50) in dynamic alpha mode, or by ATM Implied Volatility (IV) in standard mode.

## File Structure

### Backtesting
- `backtest_covered_call.py`: The main backtesting engine. Supports multiple ETFs (50, 300, 500) and modes: `--with-put`, `--no-skip-otm4`, `--alpha` (dynamic combo switching), `--no-filter`, `--model-offset` (data-driven limit orders).
- `backtest_covered_call*.png`: Visualizations of backtest results (Equity curve, drawdown, etc.).
- `backtest_covered_call*.log`: Detailed logs of executed trades and performance metrics.

### Limit Order Prediction (Open-High P10)
- `predict_open_high.py`: Production quantile prediction system that predicts the 10th percentile of the intraday `(High - Open) / Open` move. A limit sell order placed at `open * (1 + predicted_p10)` fills with ~90% probability. Used by the backtest via `--model-offset`.
- `research_open_high.py`: Static graphical analysis of the open-to-high distribution segmented by 5 overnight gap regimes.
- `backtest/open_high_model_{N}.json`: Trained model metadata (features, coefficients, coverage stats).
- `backtest/open_high_lgb_{N}.txt`: Trained LightGBM quantile model file.
- `backtest/open_high_predictions_{N}.png`: Model validation visualizations (scatter, coverage calibration, feature importance).

### Research & Analysis
- `alpha_finder.py`: Calculates historical 30-day calendar forward return distributions for indices to identify high-probability "alpha" zones for strike selection.
- `research_synthetic_otm.py`: Synthetic OTM research with combo alpha analysis (OTM2+OTM3 vs OTM4 P&L) and 24-signal dynamic search to find the best indicator for switching between aggressive and conservative combos.
- `research_otm_levels.py`: Research script to evaluate the performance of different OTM strike offsets under various market conditions.
- `research_otm_no_filter.py`: Baseline OTM performance research without technical filters.
- `evaluate_combinations.py`: Searches filter combinations on real option data.
- `eval_synth_combinations.py`: Searches filter combinations on synthetic data (27 combos, scores and ranks top 5).
- `eval_synth_filters.py`: Evaluates individual filters on synthetic data (14 technical indicators).

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

### 2. Run Backtest
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
python predict_open_high.py -e 300   # Train for 300ETF (saves model to backtest/)
python predict_open_high.py -e 50    # Train for 50ETF
python predict_open_high.py -e 500   # Train for 500ETF
```

### 5. Run Backtest with Model-Based Limit Orders
Use the trained model to set data-driven limit orders instead of the fixed ±2% spread:
```bash
python backtest_covered_call.py 300 --model-offset
```

### 6. Predict Today's Limit Order Offset
Get the model-predicted offset for today's market conditions:
```bash
python predict_open_high.py -e 300 --predict
```

### 7. Analyze OTM Levels
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
1. **Feature Engineering** — 14 candidate features from ETF daily data:
   - Overnight gap (`gap_pct`), RSI(14), realized vol(20d), normalized ATR(14)
   - Close/SMA50 ratio, MACD histogram, ROC at 5/10/20 days
   - Bollinger band width, volume ratio, day of week
   - **MA divergence**: `(open - EMA5) / EMA5` and `(open - EMA20) / EMA20` — measures how far the open price deviates from the trend

2. **Forward Feature Selection** — Greedy forward selection via 5-fold time-series cross-validation, minimizing pinball loss (quantile loss at q=0.10). Evaluates feature set sizes 2, 3, and 4; picks the size with the best CV score.

3. **Dual-Model Training**:
   - **Statsmodels Quantile Regression** (linear, fully interpretable coefficients)
   - **LightGBM Quantile** (`objective='quantile', alpha=0.10` — nonlinear, handles feature interactions)
   - If CV losses are within 5%, uses **ensemble average**; otherwise picks the winner

4. **Rolling Validation** — Expanding-window backtest (retrain every 60 trading days). Reports empirical coverage (target: ~90%), mean predicted offset vs static per-regime baseline, and pinball loss.

5. **Model Serialization** — Saves to `backtest/open_high_model_{ETF}.json` (metadata + Statsmodels coefficients) and `backtest/open_high_lgb_{ETF}.txt` (LightGBM booster file) for use by the backtest engine.

### Trained Model Results (Jun 2026)

**Best features selected:**

| ETF | Best Features | Model | Rolling Coverage |
|-----|--------------|-------|------------------|
| 300ETF | `open_ema5_div`, `roc5`, `roc10`, `gap_pct` | Ensemble | 88.7% |
| 50ETF | `open_ema5_div`, `roc5`, `gap_pct`, `rsi14` | Ensemble | 87.6% |
| 500ETF | `open_ema5_div`, `roc5`, `roc10` | LightGBM | 83.9% |

**Key insight**: `open_ema5_div` (divergence of open from EMA5) is the #1 feature across all three ETFs. When open > EMA5 (gap up from trend), the intraday high tends to be relatively close to open (smaller high-open move). When open < EMA5 (gap down from trend), the high tends to be much higher due to mean-reversion bounces.

**Backtest P&L comparison (`--model-offset` vs fixed ±2% spread):**

| ETF | Standard P&L | Model Offset P&L | Improvement |
|-----|-------------|-----------------|-------------|
| 300ETF | 16,868 RMB | 17,374 RMB | **+506 (+3.0%)** |
| 50ETF | 7,317 RMB | 7,623 RMB | **+306 (+4.2%)** |
| 500ETF | 16,954 RMB | 17,305 RMB | **+351 (+2.1%)** |

With limit orders there is no bid-ask spread slippage — the model only predicts whether the limit will fill (90% confidence). The only transaction cost is commission (2 RMB/leg). This means you sell options at mid price instead of mid * 0.98, gaining ~2% premium per sell leg.
