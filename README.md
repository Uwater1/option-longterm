# Option Longterm Investment - Project JEPI-CN

[中文文档](备兑期权.md)

This directory contains scripts and research for long-term option investment strategies, specifically focusing on **Covered Call** with technical filters (and no protective put) on Chinese ETFs (50ETF, 300ETF, 500ETF).

## Core Strategy
The primary strategy is a **Covered Call with Technical Filters and Dynamic Alpha**, inspired by income-generating funds like JEPI, but adapted for the Chinese market (Project JEPI-CN) to optimize performance.

- **Covered Call**: Selling OTM calls against held ETF shares to generate premium income.
- **Technical Filters**: RSI, Bollinger Bands, ROC, and ATR indicators filter out overbought conditions. If the market is overbought, selling calls is skipped (Skip OTM4) to avoid assignment risk during sharp rallies.
- **Dynamic Alpha Mode** (`--alpha`): Indicator-based combo switching between aggressive (OTM2+OTM3) and conservative (OTM4) call legs. Signals are derived from synthetic options research — see [alpha.md](alpha.md) for details.
- **No Put**: Protective puts are removed to eliminate long-term premium drag, maximizing net income.
- **Strike Selection**: Driven by technical indicators (RSI, BBU, SMA50) in dynamic alpha mode, or by ATM Implied Volatility (IV) in standard mode.

## File Structure

### Backtesting
- `backtest_covered_call.py`: The main backtesting engine. Supports multiple ETFs (50, 300, 500) and modes: `--with-put`, `--no-skip-otm4`, `--alpha` (dynamic combo switching), `--no-filter`.
- `backtest_covered_call*.png`: Visualizations of backtest results (Equity curve, drawdown, etc.).
- `backtest_covered_call*.log`: Detailed logs of executed trades and performance metrics.

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

### 4. Analyze OTM Levels
Research the optimal OTM offsets:
```bash
python research_otm_levels.py -e 300
```

## Data Dependencies
The scripts expect data to be located in the `./data/` directory (relative to this folder).
