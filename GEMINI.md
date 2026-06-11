# Project JEPI-CN — Option Longterm Investment

Enhanced income strategy for Chinese ETFs: Covered Call + Bull Put Spread on 50ETF/300ETF/500ETF.

## Commands

```bash
source venv/bin/activate                    # Activate Python env (uses system miniconda for rqdatac)
python3 update_data.py                      # Refresh parquet data from rqdatac
python backtest_covered_call.py [50|300|500]          # Run static backtest (logs/charts under backtest/)
python backtest_covered_call.py [50|300|500] --alpha  # Run dynamic alpha-based OTM backtest
python research_otm_levels.py -e 300        # OTM level analysis with filters
python research_synthetic_otm.py -e 300     # OTM analysis on synthetic data
python alpha_finder.py                      # 30-day forward return distribution
python research_otm_no_filter.py -e 300     # Baseline OTM without filters
python eval_synth_filters.py -e 500        # Enhanced synthetic filter eval (63 filters, risk metrics, bootstrap CI, significance, multi-criteria scoring)
python eval_synth_combinations.py -e 300   # Filter combo search on synthetic data
python evaluate_combinations.py -e 300     # Filter combo search on real data
python diagnose_500etf.py -e 500           # 500ETF multi-variant diagnostic (10 variants)
python research_robustness.py -e 500       # Data completeness & robustness analysis (bootstrap, LOOCV)
```

## Project Structure

```
backtest/                      # Backtest output logs and PNG charts
data/                          # Local Parquet database (rqdatac source)
├── {ETF}_instruments.parquet  # Option contract metadata (strike, expiry, multiplier)
├── {ETF}_historrical_prices.parquet  # Option daily OHLC/OI (order_book_id keyed)
├── {ETF}_1d.parquet           # Underlying ETF daily prices
└── 30d_iv_cache_{N}.parquet   # Pre-computed 30-day interpolated ATM IV (auto-deleted on update)

backtest_covered_call.py       # Main backtest engine (CC + Put, IVR-driven, RSI+BB filter)
alpha_finder.py                # Historical 30-day return distribution → strike selection
spread.py                      # LightGBM bid-ask spread prediction model
numba_utils.py                 # Numba-compiled BS pricing, IV solver, synthetic metrics

research_otm_levels.py         # OTM level analysis (with RSI<66 + BB filter)
research_otm_no_filter.py      # OTM baseline (no filter)
research_synthetic_otm.py      # Synthetic option OTM analysis (numba-accelerated)
research_synthetic_no_filter.py # Synthetic baseline (no filter)
evaluate_combinations.py       # Filter combination search (on real data)
eval_synth_combinations.py     # Filter combination search (on synthetic data)
eval_synth_filters.py          # Individual filter evaluation (on synthetic data)
diagnose_500etf.py              # 500ETF diagnostic: 10 variants, loss analysis, filter diff
research_robustness.py          # Data completeness, bootstrap CI, LOOCV, regime comparison

update_data.py                 # Data refresh script (uses rqdatac from system Python)
备兑期权.md                     # Chinese README (full project docs)
STRATEGY.md                    # Legacy strategy reference
README.md                      # English README (links to Chinese docs)
```

## Architecture

**Data loading & pricing rules (critical):**
1. **Underlying ETF Daily Prices must be unadjusted (不复权)** (downloaded with `adjust_type="none"` in `update_data.py`). Pre-adjusted prices create a severe mismatch with nominal option strikes, introducing look-ahead bias and invalidating the backtest.
2. The opt parquet contains daily-correct `strike_price` and `contract_multiplier`. `load_data()` must only merge `maturity_date` and `option_type` from instruments — never overwrite opt's daily strike/mult.
3. **ATM 30d IV Optimization**: Pre-groups options by date once into a dictionary (`day_calls_dict`) before iterating, achieving ~740x speedup in implied volatility lookup.

**Backtest logic** (`backtest_covered_call.py`):
- Cycles = monthly option expiries, enter after previous expiry
- IV Rank (252-day) drives OTM offset: high IVR → further OTM
- RSI < 66 + Close < Upper BB filter: pass → 2 call legs (OTM2+OTM3), fail → 1 call leg (OTM4)
- 500ETF exception: RSI < 70 (looser filter, 500ETF vol profile suits wider threshold)
- Long Put at Level 1 (closest OTM) as protective hedge
- Spread: ±2% from mid, commission 2 RMB/leg
- **Dynamic Alpha Mode (`--alpha`)**: Strike selection dynamically guided by historical 30d calendar forward return distribution. Corrected to prevent look-ahead bias by only utilizing forward return windows completed on or before the entry date.

**Spread model** (`spread.py`): LightGBM predicts `log(1+spread)` from midprice, IV, OTM depth, DTE, moneyness.

**Synthetic options:** Generated via `numba_utils.process_synthetic_strikes_loop()` — interpolates IV between two expiries to create constant-maturity synthetic contracts.
- **Synthetic Alpha Optimization**: Dynamic alpha parameters (forward return units, probability thresholds, offsets) are optimized on large-sample synthetic data (1,223 dates) using `optimize_alpha_synthetic.py` to prevent overfitting.

**Corrected & Optimized backtest results (Jun 2026):**

### Calls-Only Mode (NO_PUT_MODE = True, SKIP_OTM4 = True)
| ETF | Win Rate | Baseline P&L | Optimized P&L | Optimized Filter Condition |
|-----|----------|--------------|---------------|----------------------------|
| 300ETF | 56% (44/78) | +19,178 RMB | **+16,868 RMB** | `25 < RSI < 72` AND `MACD Hist < 0` (Sharpe 1.21 → 1.27, Drawdown -2.7k) |
| 500ETF | 42% (19/45) | +12,201 RMB | **+16,954 RMB** | `RSI > 30` AND `Close < BBU` AND `Close > SMA50` (Sharpe 1.92, Drawdown 0.0!) |
| 50ETF | 32% (44/136) | +11,922 RMB | **+7,317 RMB** | `30 < RSI < 60` AND `ROC10 < 3%` AND `Vol20 < Vol20_med` (Sharpe 0.53 → 0.58) |

### Dynamic Alpha Mode (NO_PUT_MODE = True, SKIP_OTM4 = True, --alpha)
| ETF | Win Rate | P&L | Sharpe | Max DD | Assignments |
|-----|----------|-----|--------|--------|-------------|
| 300ETF | 58% (45/78) | **+15,017 RMB** | **1.29** | **-2,773 RMB** | 8 (+$5,013 RMB or +50% P&L improvement vs old dynamic baseline) |
| 500ETF | 42% (19/45) | **+13,539 RMB** | **1.91** | **0.00 RMB** | 1 (Sharpe 1.91, zero drawdown!) |
| 50ETF | 32% (44/136) | **+6,945 RMB** | **0.55** | **-2,676 RMB** | 12 (+$2,062 RMB or +42% P&L improvement vs old dynamic baseline) |

### With-Put Mode (NO_PUT_MODE = False, SKIP_OTM4 = False)
| ETF | Win Rate | Baseline P&L | Optimized P&L | Optimized Filter Condition |
|-----|----------|--------------|---------------|----------------------------|
| 300ETF | 47% (37/78) | +6,420 RMB | **+6,420 RMB** | `25 < RSI < 66` AND `Close < BBU + 0.5*ATR` AND `ROC10 < 7%` |
| 500ETF | 36% (16/45) | -4,628 RMB | **+879 RMB** | `RSI > 35` AND `Close < BBU` AND `Close > SMA50` (Flipped to positive!) |
| 50ETF | 39% (53/136) | +1,054 RMB | **+3,821 RMB** | `RSI > 30` AND `Close < BBU - 0.5*ATR` AND `ROC10 < 7%` (3.6x improvement!) |

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

- **rqdatac** (system miniconda): `python3 update_data.py`
- IV caches auto-regenerate on first backtest run after deletion

## 500ETF Research Findings (Jun 2026)

**Problem:** 500ETF underperforms 300ETF — lower win rate (67% vs 88%), bigger drawdowns.

**Root causes:**
1. **Higher vol (26.8% ann)** — ~40% more than 300ETF → strikes hit more often
2. **Big loss cycles from sharp rallies** — 2025-01 (-3,375), 2025-12 (-4,057), 2026-03 (-7,261). All had LOW RSI (37-46), filter can't prevent
3. **Expensive put hedge** — Level 1 put often costs 500-1500 RMB, creating drag on flat/rally months

**10-variant diagnostic results** (True results after fixing adjusted ETF price mismatch):

| Variant | P&L | Wins | Assignments |
|---------|-----|------|-------------|
| Baseline | -4,628 | 16/45 | 1 |
| RSI70+BBU | -3,931 | 17/45 | 1 |
| IVR-Driven | -3,873 | 16/45 | 3 |
| Wider OTM3+4/5 | -5,720 | 12/45 | 0 |

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
- [x] Audit backtest and fix adjusted vs unadjusted ETF price data quality mismatch (Jun 2026)
- [x] Grid search and optimize option selling filters for 50/300/500 ETF (Jun 2026) → `optimize_filters.py`
- [x] Test and implement mode-specific optimal filters (calls-only vs with-put) in `backtest_covered_call.py` (Jun 2026)
- [ ] Test early roll management for 500ETF — roll calls to higher strikes if underlying rallies >5% mid-cycle
- [ ] Explore weekly options for 500ETF if available — shorter DTE reduces rally exposure
- [ ] Revisit conclusions when 500ETF reaches 80+ cycles (~2029)
