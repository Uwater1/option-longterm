# Project JEPI-CN — Option Longterm Investment

Enhanced income strategy for Chinese ETFs: Covered Call + Bull Put Spread on 50ETF/300ETF/500ETF.

## Commands

```bash
source venv/bin/activate                    # Activate Python env (uses system miniconda for rqdatac)
python3 update_data.py                      # Refresh parquet data from rqdatac
python3 download_5m_data.py                # Download 5m ETF & option historical data
python backtest_covered_call.py [50|300|500]  # Run backtest (generates logs and charts under backtest/)
python backtest_covered_call.py --alpha 300  # Run backtest with dynamic alpha mode (indicator-based OTM switching)
python backtest_covered_call.py 300 --model-offset  # Run backtest with model-predicted limit order offsets (requires prior training)
python backtest_covered_call.py 300 --limit-entry                       # Run backtest with Black-Scholes mapping limit entry for protective puts
python predict_open_high.py -e 300          # Train open-high P10 prediction model (90% fill-rate limit orders)
python predict_open_high.py -e 300 --pool   # Train with cross-ETF pooled data (all 3 ETFs, ~7200 samples)
python predict_open_high.py -e 300 --predict # Predict today's limit order offset
python research_limit_entry.py -e 300       # Validate protective put limit entry via Black-Scholes mapping model
python research_open_high.py               # Static open-high distribution analysis (graphical)
python research_otm_levels.py -e 300        # OTM level analysis with filters
python research_synthetic_otm.py -e 300     # OTM analysis + combo alpha + dynamic signal search on synthetic data
python alpha_finder.py                      # 30-day forward return distribution
python research_otm_no_filter.py -e 300     # Baseline OTM without filters
python optimize_alpha_synthetic.py -e 300   # Alpha param grid search on synthetic data (6-component composite score)
python optimize_filters.py 300              # Filter grid search on real data (6-component composite score)
python eval_synth_filters.py -e 500        # Enhanced synthetic filter eval (63 filters, risk metrics, bootstrap CI, significance, multi-criteria scoring)
python eval_synth_combinations.py -e 300   # Filter combo search on synthetic data
python evaluate_combinations.py -e 300     # Filter combo search on real data
python diagnose_500etf.py -e 500           # 500ETF multi-variant diagnostic (10 variants)
python research_robustness.py -e 500       # Data completeness & robustness analysis (bootstrap, LOOCV)
```

## Project Structure

```
backtest/                      # Backtest output logs and PNG charts
├── open_high_model_{N}.json   # Trained open-high P10 model metadata (features, coefficients, vol-regime calibration)
├── open_high_lgb_{N}_bag{i}.txt  # 5 bagged LightGBM quantile model files per ETF (i=0..4)
├── open_high_predictions_{N}.png  # Open-high prediction visualizations
data/                          # Local Parquet database (rqdatac source)
├── {ETF}_instruments.parquet  # Option contract metadata (FINAL strike/mult after all adjustments)
├── {ETF}_historical_prices.parquet  # Option daily OHLC/OI (DAILY-CORRECT strike_price & contract_multiplier)
├── {ETF}_1d.parquet           # Underlying ETF daily prices
├── {ETF}_5m.parquet           # Underlying ETF 5m prices (510300_5m.parquet for 300ETF)
├── {ETF}_historical_prices_5m.parquet # Option 5m prices during 1 month before expiry
└── 30d_iv_cache_{N}.parquet   # Pre-computed 30-day interpolated ATM IV (auto-deleted on update)

backtest_covered_call.py       # Main backtest engine (CC + Put, IVR-driven, RSI+BB filter, --alpha dynamic mode, --model-offset)
alpha_finder.py                # Historical 30-day return distribution → strike selection
alpha.md                       # Dynamic alpha strategy research report (v2 indicator-based)
spread.py                      # LightGBM bid-ask spread prediction model
numba_utils.py                 # Numba-compiled BS pricing, IV solver, synthetic metrics
predict_open_high.py           # Open-to-High P10 prediction system (Statsmodels QR + LightGBM quantile, 90% fill-rate limit orders)
research_open_high.py          # Static open-high distribution analysis (graphical only)

research_otm_levels.py         # OTM level analysis (with RSI<66 + BB filter)
research_otm_no_filter.py      # OTM baseline (no filter)
research_synthetic_otm.py      # Synthetic OTM analysis + combo alpha (OTM2+3 vs OTM4) + 24-signal dynamic search
research_synthetic_no_filter.py # Synthetic baseline (no filter)
evaluate_combinations.py       # Filter combination search (on real data)
eval_synth_combinations.py     # Filter combination search (on synthetic data)
eval_synth_filters.py          # Individual filter evaluation (on synthetic data)
optimize_alpha_synthetic.py    # Alpha parameter grid search (synthetic data, 6-component composite scoring)
optimize_filters.py            # Filter condition grid search (real data, 6-component composite scoring)
diagnose_500etf.py              # 500ETF diagnostic: 10 variants, loss analysis, filter diff
research_robustness.py          # Data completeness, bootstrap CI, LOOCV, regime comparison

update_data.py                 # Data refresh script (uses rqdatac from system Python)
download_5m_data.py            # Download 5m ETF & option historical data for active cycles
备兑期权.md                     # Chinese README (full project docs)
STRATEGY.md                    # Legacy strategy reference
README.md                      # English README (links to Chinese docs)
```

## Architecture

**Data loading (critical):** 
1. The opt parquet contains daily-correct `strike_price` and `contract_multiplier` (adjusted when underlying ETF pays dividends). The instruments parquet holds FINAL post-adjustment values. `load_data()` must only merge `maturity_date` and `option_type` from instruments — never overwrite opt's daily strike/mult.
2. **Underlying ETF Daily Prices must be unadjusted (不复权)** (pulled with `adjust_type="none"` in `update_data.py`). If pre-adjusted prices are used, it creates a mismatch with unadjusted option strikes/premiums, causing major look-ahead bias and false backtest performance.
3. **ATM 30d IV Speed Optimization**: Daily 30d IV calculation in `get_30d_iv` is optimized by passing a pre-grouped dictionary of calls instead of running slow boolean filters on the full DataFrame, reducing runtime by ~740x.

**Backtest logic** (`backtest_covered_call.py`):
- Cycles = monthly option expiries, enter on first trading day after previous expiry
- IV Rank (252-day) drives OTM offset: high IVR → further OTM
- RSI < 66 + Close < Upper BB filter: pass → 2 call legs (OTM2+OTM3), fail → 1 call leg (OTM4)
- 500ETF exception: RSI < 70 (looser filter, 500ETF vol profile suits wider threshold)
- Long Put at Level 1 (closest OTM) as protective hedge
- Spread: ±2% from mid, commission 2 RMB/leg
- **Dynamic Alpha Mode** (`--alpha`): Indicator-based combo switching — strong signal → Combo A (OTM2+OTM3), weak signal → Combo B (OTM4). Monthly rate of change (`roc20`) caution filters protect against vertical rallies:
  - 300ETF: `30 < RSI < 60` AND `roc20 < 4.0` (switches to Combo B if monthly growth $\ge 4\%$; P&L +13.8K $\to$ +16.1K)
  - 50ETF: `RSI > 30` AND `roc20 < 3.0` (switches to Combo B if monthly growth $\ge 3\%$; P&L +6.3K $\to$ +8.8K)
  - 500ETF: `RSI > 35 AND Close < BBU AND Close > SMA50` (remains unchanged)

**Spread model** (`spread.py`): LightGBM predicts `log(1+spread)` from midprice, IV, OTM depth, DTE, moneyness.

**Open-High P10 Prediction** (`predict_open_high.py`): Predicts the 10th percentile of `(High - Open) / Open` to set limit sell orders with ~90% fill probability. Pipeline:
- 25 candidate features from ETF daily data (gap, RSI, vol, ATR, MACD, ROC, BB width, volume, MA divergence, Stochastic %K, Williams %R, ADX, MFI, CCI, vol skewness, candlestick shadows, prev-day range/open-to-high, overnight gap from high)
- Forward feature selection via time-series CV pinball loss (selects best 3–6 features)
- Dual-model training: Statsmodels Quantile Regression (linear, interpretable) + LightGBM Quantile (nonlinear)
- Ensemble if models are within 5% CV loss; otherwise picks the winner
- **Adaptive quantile search**: Binary search for q' (typically 0.03–0.04) that natively achieves 90% coverage, replacing the fixed q=0.10
- **Coverage calibration**: Computes offset = P10(actual - predicted) from rolling validation, stored in model JSON and applied at prediction time. Achieves exactly 90.0% calibrated coverage.
- **Vol-regime-conditional calibration**: Separate calibration offsets for low-vol and high-vol regimes (split by median vol20). Applied based on current vol20 at prediction time.
- **Ensemble bagging**: 5 LightGBM models trained on bootstrap resamples, predictions averaged to reduce variance.
- **Block-bootstrap augmentation**: 20-day circular blocks, 1x ratio synthetic data to reduce overfitting
- **Cross-ETF pooling** (`--pool`): Optional mode that trains on all 3 ETFs' data (~7200 samples) for more robust models. Per-ETF calibration still applied.
- Rolling validation (expanding window, retrain every 60 days) with coverage calibration
- Best features across ETFs: `open_ema5_div`, `roc5`, `williams_r14`, `stoch_k14` (consistently selected); `rsi14`, `dow`, `prev_open_to_high`, `close_sma50_ratio` also selected per-ETF
- `--model-offset` in backtest: Uses BS mapping to set limit sell orders simulated against 5m bar data. Call fill rates: **92–100%** across ETFs. Unfilled legs fall back to last 5m close.

**Black-Scholes Mapping Put Limit Entry** (`--limit-entry`): Predicts the 90%+ fill-rate limit buy order for protective puts.
- Uses the trained daily ETF open-to-high model to predict the 10th percentile of the ETF's maximum return over the 2-day entry window ($R_{ETF\_P10\_frac}$).
- Solves for the option's entry implied volatility ($\sigma_{open}$) from the option open price $P_{open}$ and ETF open price $S_{open}$ at entry.
- Maps the predicted target ETF high price ($S_{target} = S_{open} \times (1 + R_{ETF\_P10\_frac})$) to the target Put option limit price ($P_{limit}$) via the Black-Scholes pricing formula.
- Applies an OTM-dependent liquidity cushion ($0.5\% + 0.5\% \times OTM\%$) to secure execution.
- Completely avoids overfitting to small option price datasets by leveraging the robust daily ETF model and closed-form Black-Scholes mapping.

**Synthetic options:** Generated via [generate_synthetic_options.py](file:///home/hallo/Documents/option-longterm/generate_synthetic_options.py) (calling `numba_utils.process_synthetic_strikes_loop()`). Interpolates IV between two expiries to create constant-maturity synthetic contracts.
- **Data Pricing & Dividend Adjustment (Critical)**: Must use unadjusted ETF prices and daily-correct option strikes at entry to calculate option prices/IVs. At expiry, options are adjusted for dividends by scaling the unadjusted underlying price by $\frac{f_{expiry}}{f_{entry}}$ (where $f_t = S_{post, t} / S_{none, t}$ is the daily cumulative adjustment factor downloaded from `rqdatac`), keeping the nominal strikes clean and unadjusted.

**Optimization scoring (v2, Jun 2026):** Both `optimize_alpha_synthetic.py` and `optimize_filters.py` use a 6-component normalized composite score: Sharpe (20%), Total P&L (15%), MaxDD (15%), WinRate (15%), PlacementRate (15%), FilterLift (20%). FilterLift = avg P&L on filter-placed cycles minus avg P&L if always trading — measures whether the filter genuinely adds alpha vs cherry-picking. PlacementRate penalizes overly restrictive filters. `backtest_covered_call.py` aggregate summary now reports placement rate and filter lift for every run.

## Backtest Audit (Jun 2026)

**No look-ahead bias found.** All signals use only data available at entry time:
- RSI (14-bar), BB (20-bar): purely backward-looking windows
- IV Rank: `daily_ivs[index <= entry]` — historical only
- Cycle detection: entry = first opt trading day after previous expiry; no outcome-based filtering
- Settlement: `etf.index[<= expiry_date][-1]` — last ETF close on or before expiry
- Option pricing: entry-day close (known at market close, standard assumption)

**Pricing bug fixed (strike/mult from wrong source).** The old merge used instruments table values (final post-adjustment) instead of opt parquet's daily-correct values. For 22% of contracts with dividend adjustments, this used the wrong strike and multiplier on pre-adjustment dates, understating P&L by ~6K total for 300ETF (6 cycles affected, 2 flipped loss→win).

**Corrected backtest results (True results after fixing adjusted ETF price mismatch):**

**Corrected & Optimized backtest results (Jun 2026):**

### Calls-Only Mode (NO_PUT_MODE = True, SKIP_OTM4 = True)
| ETF | Win Rate | Baseline P&L | Optimized P&L | Optimized Filter Condition |
|-----|----------|--------------|---------------|----------------------------|
| 300ETF | 56% (44/78) | +19,178 RMB | **+16,868 RMB** | `25 < RSI < 72` AND `MACD Hist < 0` (Sharpe 1.21 → 1.27, Drawdown -2.7k) |
| 500ETF | 42% (19/45) | +12,201 RMB | **+16,954 RMB** | `RSI > 30` AND `Close < BBU` AND `Close > SMA50` (Sharpe 1.92, Drawdown 0.0!) |
| 50ETF | 32% (44/136) | +11,922 RMB | **+7,317 RMB** | `30 < RSI < 60` AND `ROC10 < 3%` AND `Vol20 < Vol20_med` (Sharpe 0.53 → 0.58) |

### With-Put Mode (NO_PUT_MODE = False, SKIP_OTM4 = False)
| ETF | Win Rate | Baseline P&L | Optimized P&L | Optimized Filter Condition |
|-----|----------|--------------|---------------|----------------------------|
| 300ETF | 47% (37/78) | +6,420 RMB | **+6,420 RMB** | `25 < RSI < 66` AND `Close < BBU + 0.5*ATR` AND `ROC10 < 7%` |
| 500ETF | 36% (16/45) | -4,628 RMB | **+879 RMB** | `RSI > 35` AND `Close < BBU` AND `Close > SMA50` (Flipped to positive!) |
| 50ETF | 39% (53/136) | +1,054 RMB | **+3,821 RMB** | `RSI > 30` AND `Close < BBU - 0.5*ATR` AND `ROC10 < 7%` (3.6x improvement!) |

### With-Put Mode + Put Limit Entry (BS Mapping model, Jun 2026)
| ETF | Win Rate | P&L (Baseline + Put Limit) | P&L (Alpha + Put Limit) | Put Limit Fill Rate |
|-----|----------|----------------------------|-------------------------|---------------------|
| 300ETF | 44% (34/78) | **+7,178.24 RMB** | **+4,176.58 RMB** | **93.6%** (73/78) |
| 500ETF | 33% (15/45) | **+2,401.07 RMB** | **+1,661.96 RMB** | **97.8%** (44/45) |
| 50ETF | 44% (61/136) | **+7,768.45 RMB** | **+2,467.22 RMB** | **94.1%** (130/136) |

### With Call Limit Orders (5m BS mapping, v2 features, bagged + vol-regime calibration, Jun 2026)
| ETF | Mode | Win Rate | P&L | Call Fill Rate | Put Fill Rate |
|-----|------|----------|-----|----------------|---------------|
| 300ETF | Calls-only + Model Offset | 56% (44/78) | **+20,492 RMB** | **99.0%** (95/96) | N/A |
| 300ETF | With-Put + Model Offset + Put Limit | 46% (36/78) | **+11,469 RMB** | **99.3%** (139/140) | **94.9%** (74/78) |
| 500ETF | Calls-only + Model Offset | 42% (19/45) | **+19,046 RMB** | **92.1%** (35/38) | N/A |
| 50ETF | Calls-only + Model Offset | 32% (44/136) | **+9,119 RMB** | **100.0%** (98/98) | N/A |

**Known approximation (not a bug):** ±2% spread from mid is a simplification; real bid-ask spreads vary by liquidity, DTE, and moneyness. Conservative for liquid ATM/near-OTM contracts, possibly optimistic for deep OTM.


## Key Parameters

| Param | Value | Notes |
|-------|-------|-------|
| SPREAD_HALF | 0.02 | ±2% slippage |
| COMMISSION | 2.0 RMB | Per option leg |
| ETF_SHARES | 20,000 | Equity leg size |
| IV_THRESHOLD | 0.20 | Fallback ATM IV |
| RISK_FREE | 0.02 | BS risk-free rate |

## Data Dependencies

- **rqdatac** (system miniconda): `python3 update_data.py` and `python3 download_5m_data.py`
- IV caches auto-regenerate on first backtest run after deletion

## 500ETF Research Findings (Jun 2026)

**Problem:** 500ETF underperforms 300ETF — lower win rate (67% vs 91%), bigger drawdowns.

**Root causes:**
1. **Higher vol (26.8% ann)** — ~40% more than 300ETF → strikes hit more often
2. **Big loss cycles from sharp rallies** — 2025-01 (-3,375), 2025-12 (-4,057), 2026-03 (-7,261). All had LOW RSI (37-46), filter can't prevent
3. **Expensive put hedge** — Level 1 put often costs 500-1500 RMB, creating drag on flat/rally months

**10-variant diagnostic results** (`diagnose_500etf.py -e 500`):

| Variant | P&L | Wins | Assignments |
|---------|-----|------|-------------|
| RSI70+BBU (implemented) | 22,182 | 30/45 | 6 |
| Baseline RSI66+BBU | 21,448 | 29/45 | 6 |
| IVR-Driven (OTM1+2 low IVR) | 21,396 | 31/45 | 18 |
| Wider OTM3+4/5 | 14,047 | 20/45 | 3 |

**What was tried and failed:**
- IVR-driven OTM: Low IVR → sell closest strikes → catastrophic assignment losses (-18K worst cycle)
- Wider OTM3+4/5: Fewer assignments but too much premium sacrificed
- Put Level 2: Cheaper put but worse total P&L (-2,556 vs baseline)
- ROC<5% filter: Too restrictive, misses profitable cycles

**Implemented change:** RSI threshold for 500ETF raised from 66→70. Gains +697 RMB (1 extra trade cycle). **Statistically NOT significant** (P=64.3%, only 1 cycle differs). Keep as implemented but low confidence.

**Synthetic filter research findings** (`eval_synth_filters.py -e 500`, 692 samples, 63 filters):
- f4_AND_f6 (RSI>30 AND BBU) is #1 ranked by composite score (Total 20%, Sharpe 20%, MaxDD 20%, Calmar 15%, WinRate 10%, WorstLoss 10%, PF 5%)
- 13 filters beat baseline on both total P&L and max drawdown, but none reaches 95% significance
- f5 (MACD<0) has best Sharpe (0.000) and shallowest MaxDD (-265K) but too restrictive (47.5% placement)
- Combined strategy (calls+put) is net negative on synthetic — Put L1 drag ~45K overwhelms call income
- Adding CCI to f4_AND_f6 provides negligible improvement
- New promising filters: f_roc5 (ROC<3%), f_sma50 (Close>SMA50), f_atr_low (low ATR), f_vol_low (low vol regime)

**Robustness findings** (`research_robustness.py -e 500`):
- 45 cycles only — bootstrap 95% CIs overlap across all variants
- LOOCV: single cycle swing = ~14,630 RMB (68% of baseline total)
- 500ETF vol regime matches 300ETF's worst 18% — cross-ETF transfer limited
- Need ~100 cycles (8+ years) for >80% confidence in variant ranking

**Fundamental limitation:** No filter-based approach can prevent the big losses because they occur when RSI is already low (market not overbought). The losses come from intra-cycle sharp rallies (+8-16%) that blow through all strike levels. Early roll management or delta hedging would be needed for further improvement.

**Full report:** `RESEARCH_500ETF.md`

## TODO

- [x] Explore data completeness for 500ETF and make research more robust → `research_robustness.py`
- [x] Audit backtest for look-ahead bias and pricing correctness (Jun 2026) → strike/mult bug fixed
- [x] Audit, fix pricing mismatch, and regenerate synthetic options data using unadjusted prices & daily strikes adjusted for dividends at expiry (Jun 2026)
- [x] Grid search and optimize option selling filters for 50/300/500 ETF (Jun 2026) → `optimize_filters.py`
- [x] Test and implement mode-specific optimal filters (calls-only vs with-put) in `backtest_covered_call.py` (Jun 2026)
- [x] Upgrade optimization scoring to 6-component composite (Sharpe/Total/MaxDD/WinRate/PlacementRate/FilterLift) in `optimize_alpha_synthetic.py` and `optimize_filters.py` (Jun 2026)
- [x] Implement indicator-based dynamic alpha mode in `backtest_covered_call.py` — combo switching (OTM2+3 vs OTM4) based on RSI/BBU/SMA signals from synthetic research (Jun 2026)
- [x] Build production open-high P10 prediction system (`predict_open_high.py`) with quantile models, feature selection, and backtest integration via `--model-offset` (Jun 2026)
- [x] Add call-side 5m limit order simulation (`--model-offset`), expand features 14→25, ensemble bagging (x5), vol-regime calibration, cross-ETF pooling (`--pool`) (Jun 2026)
- [ ] Test early roll management for 500ETF — roll calls to higher strikes if underlying rallies >5% mid-cycle
- [ ] Explore weekly options for 500ETF if available — shorter DTE reduces rally exposure
- [ ] Revisit conclusions when 500ETF reaches 80+ cycles (~2029)
