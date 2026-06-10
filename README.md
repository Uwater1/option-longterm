# Option Longterm Investment - Project JEPI-CN

[中文文档](备兑期权.md)

This directory contains scripts and research for long-term option investment strategies, specifically focusing on **Covered Call** with technical filters (and no protective put) on Chinese ETFs (50ETF, 300ETF, 500ETF).

## Core Strategy
The primary strategy is a **Covered Call with Technical Filters (No Put)**, inspired by income-generating funds like JEPI, but adapted for the Chinese market (Project JEPI-CN) to optimize performance.

- **Covered Call**: Selling OTM calls against held ETF shares to generate premium income.
- **Technical Filters**: RSI, Bollinger Bands, ROC, and ATR indicators filter out overbought conditions. If the market is overbought, selling calls is skipped (Skip OTM4) to avoid assignment risk during sharp rallies.
- **No Put**: Protective puts are removed to eliminate long-term premium drag, maximizing net income.
- **Strike Selection**: Driven by historical probability distributions (Alpha Finder) and ATM Implied Volatility (IV).

## File Structure

### Backtesting
- `backtest_covered_call.py`: The main backtesting engine. Supports multiple ETFs (50, 300, 500) and options like `--with-put` and `--no-skip-otm4`.
- `backtest_covered_call*.png`: Visualizations of backtest results (Equity curve, drawdown, etc.).
- `backtest_covered_call*.log`: Detailed logs of executed trades and performance metrics.

### Research & Analysis
- `alpha_finder.py`: Calculates historical 30-day calendar forward return distributions for indices to identify high-probability "alpha" zones for strike selection.
- `research_otm_levels.py`: Research script to evaluate the performance of different OTM strike offsets under various market conditions.
- `research_otm_no_filter.py`: Baseline OTM performance research without technical filters.
- `research_synthetic_otm.py`: Evaluates OTM strategies using synthetic option pricing data.
- `evaluate_combinations.py`: Searches filter combinations on real option data.
- `eval_synth_combinations.py`: Searches filter combinations on synthetic data (27 combos, scores and ranks top 5).
- `eval_synth_filters.py`: Evaluates individual filters on synthetic data (14 technical indicators).

### Documentation
- `备兑期权.md`: Comprehensive Chinese documentation — strategy details, backtest results, project structure, filter research, and architecture.
- `STRATEGY.md`: Legacy strategy reference.

### Utilities
- `numba_utils.py`: Performance-optimized functions for option pricing and metric calculations.

## Getting Started

### 1. Run Alpha Analysis
Identify the historical probabilities for index moves:
```bash
python alpha_finder.py
```

### 2. Run Backtest
Run a backtest for the 300ETF covered call strategy:
```bash
python backtest_covered_call.py 300
```

### 3. Analyze OTM Levels
Research the optimal OTM offsets:
```bash
python research_otm_levels.py -e 300
```

## Data Dependencies
The scripts expect data to be located in the `./data/` directory (relative to this folder).
