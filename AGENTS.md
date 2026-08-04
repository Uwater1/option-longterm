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
python optimize_put_filters.py 300            # Optimize put filters (real data)
python backtest_covered_call.py --alpha 300   # Call backtest (dynamic alpha mode)
python backtest_covered_call.py 300 --model-offset  # Call backtest with model limit orders
python predict_open_high.py -e 300          # Train open-high model
python optimize_alpha_synthetic.py -e 300   # Grid search synthetic alpha (6-score)
python optimize_filters.py 300              # Grid search real call filters (6-score)
python3 optimize_put_alpha.py -e all --select-by-oos  # Optimize put alpha (OOS-select)
python alpha_model_ml.py -e all              # Train Phase 2 LightGBM regime models
python validate_alpha_pnl.py -e all --phase 1 --cadence cycle  # Put P&L validation
python compare_alpha_phases.py               # Cross-phase comparison
```

> Day-model commands: see [day-model/AGENTS.md](file:///home/hallo/Documents/option-longterm/day-model/AGENTS.md)
> Day-model rewrite commands: see [day-model-new/AGENTS.md](file:///home/hallo/Documents/option-longterm/day-model-new/AGENTS.md)
> Daytrade commands: see [daytrade/AGENTS.md](file:///home/hallo/Documents/option-longterm/daytrade/AGENTS.md)
> Newtrade commands: see [newtrade/AGENTS.md](file:///home/hallo/Documents/option-longterm/newtrade/AGENTS.md)


## Project Structure

```
data/                          # Parquet files
├── {ETF}_instruments.parquet  # Contract metadata
├── {ETF}_historical_prices.parquet  # Daily correct strike/multiplier
├── {ETF}_1d.parquet           # Underlying daily (unadjusted + post-adjusted)
├── {ETF}_5m.parquet           # 5m ETF prices
├── {ETF}_1m.parquet           # 1m ETF prices (zstd compressed)
├── {ETF}_historical_prices_5m.parquet # 5m Option prices
├── 30d_iv_cache_{N}.parquet   # ATM IV cache
└── rq_vix.parquet             # Ricequant VIX indices cache (all 5 ETFs)

backtest/                      # Model files, plots, artifacts
validate/                      # Validation reports

final.md                       # Comprehensive master synthesis report
backtest_engine.py             # Core backtest engine
backtest_strategies.py         # CallStrategy & PutStrategy definitions
backtest_covered_call.py       # Covered call script
backtest_put.py                # Daily protective put script
alpha_model.py                 # 4-Type Decision Matrix (Phase 1)
alpha_model_ml.py              # Phase 2 LightGBM regime models
alpha_model_hybrid.py          # Phase 3 rule-anchored hybrid
optimize_put_alpha.py          # Weight/horizon optimizer (OOS-select)
validate_alpha_pnl.py          # Put P&L validator vs 3 baselines
compare_alpha_phases.py        # Cross-phase P&L comparison
predict_open_high.py           # Open-to-High prediction pipeline
numba_utils.py                 # Numba BS functions & IV solver
penalties.py                   # Custom skglm penalties (MCP_plus_L2)

day-model/                     # See day-model/AGENTS.md for details
daytrade/                      # See daytrade/AGENTS.md for details
daytrade/methods/              # See daytrade/methods/AGENTS.md for details
```

## Architecture

### Data Rules
- **Option strikes/multipliers**: Use daily-correct values from `_historical_prices.parquet`. Do NOT overwrite with instruments metadata.
- **ETF daily prices**: Option matching & settlement use unadjusted prices (`close`, `open`).
- **Technical indicators & forward returns**: Use post-adjusted prices (`close_adj`, `open_adj`).
- **Position Sizing**: Implemented `fast_ramp_linear` ($m=0.50, \Delta Z_{\text{full}}=0.30$) as default in `newtrade/run_backtest.py` (`strategy.py`). Achieves **1.339 Avg Sharpe vs 1.324 Binary Baseline (+0.015 Sharpe lift)** while **slashing MaxDD by 43.9% (3.97% vs 7.08%)**. Strictly beats Binary Baseline across ALL 3 ETFs simultaneously.
- **Option Intraday Stop-Loss**: Integrated 5 option-tailored intraday stoploss strategies in `newtrade/option_strategy.py` & `newtrade/research_option_stoploss.py`. `opt_time_decay_trailing` achieved **+0.205 Sharpe Lift** (1.251 vs 1.046) and reduced MaxDD by **49.4% (11.57% vs 22.87%)** on 300ETF.
- **Option Strike Selection**: ETF-adaptive ITM/OTM choice (`--strike-mode auto`): 300ETF/50ETF=cascade (distance+gamma guard), 500ETF=nearest, 159915ETF=vol_t1 (T-1 liquidity). **+83% avg Sharpe** vs always-OTM baseline. Commission: 4 RMB per contract per side.
- **ATM 30d IV Speedup**: Pre-grouped dictionaries bypass slow filters.
- **Historical Date Limits**: The day-model dataset spans from `2010-01-04` (or listing date) to present. Missing option prices and VIX data prior to February 2015 are forward-filled and median-imputed dynamically.

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

### Put Alpha Model — 3 Phases
- **Phase 1** (`alpha_model.py` + `optimize_put_alpha.py`): Linear weighted score. 4 regimes (ST/MT Fall, ST/MT Crash). Rolling 252-day percentile rank. Dynamic threshold. `--select-by-oos` picks by mean OOS metric.
- **Phase 2** (`alpha_model_ml.py`): LightGBM binary classifier per regime. Monotone constraints, 5-bag bootstrap ensemble, isotonic calibration.
- **Phase 3** (`alpha_model_hybrid.py`): Logistic stack of Phase 1 rank, Phase 2 prob, FINDINGS rule flags.
- **Validator** (`validate_alpha_pnl.py`): Real put option P&L vs 3 baselines. `deployable = net_pnl > 0 AND Sharpe > 0 AND per_trig > 0 AND beats_static`.

### Scoring
- **Call filters**: 6-component score (Sharpe 20%, P&L 15%, MaxDD 15%, WinRate 15%, Placement 15%, FilterLift 20%).
- **Put filters**: Profit-first score (P&L 35%, FilterLift 30%, Sharpe 15%, MaxDD 10%, WinRate 5%, Placement 5%).

> Artifacts: `backtest/alpha_put_models.json`, `backtest/alpha_ml_models/`, `backtest/validate_pnl_phase{1,2,3}.json`, `backtest/alpha_phase_comparison.md`.

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
- **500ETF**: High volatility (~26.8%). Sharp rallies trigger assignment loss. Details in [RESEARCH_500ETF.md](file:///home/hallo/Documents/option-longterm/RESEARCH_500ETF.md).
- **Tail Risk (Puts)**: Vol acceleration + negative skewness predict downside. Details in [FINDINGS.md](file:///home/hallo/Documents/option-longterm/FINDINGS.md).
- **Day-Model**: 10:00-14:35 return prediction. See [day-model/AGENTS.md](file:///home/hallo/Documents/option-longterm/day-model/AGENTS.md).
- **Daytrade**: Frozen-linear intraday alpha. See [daytrade/AGENTS.md](file:///home/hallo/Documents/option-longterm/daytrade/AGENTS.md).
- **Top-K & Hysteresis Selection**: Large TP pools ($N > 100$) suffer from signal dilution if unconstrained. Optimal hysteresis bandwidth $\Delta K = \text{ER} - K \in [5, 7]$ (e.g. $K=10, \text{ER}=17$). Hard cliff drop at $\text{ER} \ge 26$.

## TODO
- [ ] Improve put buy strategy: [put_improvement_plan.md](file:///home/hallo/Documents/option-longterm/put_improvement_plan.md)
- [x] Fix Commit 820d7fc correlation regression in `day-model-new/select_features.py` (re-weight Q-score: 50% Deflated IC + 25% Sortino + 15% Recent IC + 10% IR, fix fallback bug, fix multi-correlation pool leakage)