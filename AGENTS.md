# Project JEPI-CN — Option Longterm Investment

Enhanced income strategy for Chinese ETFs: Covered Call + Bull Put Spread on 50ETF/300ETF/500ETF.

## Commands

```bash
source venv/bin/activate                    # Activate Python env (uses system miniconda for rqdatac)
python3 update_data.py                      # Refresh parquet data from rqdatac
python backtest_covered_call.py [50|300|500]  # Run backtest (generates .log + .png)
python research_otm_levels.py -e 300        # OTM level analysis with filters
python research_synthetic_otm.py -e 300     # OTM analysis on synthetic data
python alpha_finder.py                      # 30-day forward return distribution
python research_otm_no_filter.py -e 300     # Baseline OTM without filters
python eval_synth_filters.py -e 300        # Single filter eval on synthetic data
python eval_synth_combinations.py -e 300   # Filter combo search on synthetic data
python evaluate_combinations.py -e 300     # Filter combo search on real data
python diagnose_500etf.py -e 500           # 500ETF multi-variant diagnostic (10 variants)
python research_robustness.py -e 500       # Data completeness & robustness analysis (bootstrap, LOOCV)
```

## Project Structure

```
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

**Data flow:** rqdatac → `update_data.py` → `data/*.parquet` → all scripts

**Backtest logic** (`backtest_covered_call.py`):
- Cycles = monthly option expiries, enter after previous expiry
- IV Rank (252-day) drives OTM offset: high IVR → further OTM
- RSI < 66 + Close < Upper BB filter: pass → 2 call legs (OTM2+OTM3), fail → 1 call leg (OTM4)
- 500ETF exception: RSI < 70 (looser filter, 500ETF vol profile suits wider threshold)
- Long Put at Level 1 (closest OTM) as protective hedge
- Spread: ±2% from mid, commission 2 RMB/leg

**Spread model** (`spread.py`): LightGBM predicts `log(1+spread)` from midprice, IV, OTM depth, DTE, moneyness.

**Synthetic options:** Generated via `numba_utils.process_synthetic_strikes_loop()` — interpolates IV between two expiries to create constant-maturity synthetic contracts.

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

**10-variant diagnostic results** (`diagnose_500etf.py -e 500`):

| Variant | P&L | Wins | Assignments |
|---------|-----|------|-------------|
| RSI70+BBU (implemented) | 22,145 | 30/45 | 6 |
| Baseline RSI66+BBU | 21,448 | 29/45 | 6 |
| IVR-Driven (OTM1+2 low IVR) | 21,396 | 31/45 | 18 |
| Wider OTM3+4/5 | 14,047 | 20/45 | 3 |

**What was tried and failed:**
- IVR-driven OTM: Low IVR → sell closest strikes → catastrophic assignment losses (-18K worst cycle)
- Wider OTM3+4/5: Fewer assignments but too much premium sacrificed
- Put Level 2: Cheaper put but worse total P&L (-2,556 vs baseline)
- ROC<5% filter: Too restrictive, misses profitable cycles

**Implemented change:** RSI threshold for 500ETF raised from 66→70. Gains +697 RMB (1 extra trade cycle). **Statistically NOT significant** (P=64.3%, only 1 cycle differs). Keep as implemented but low confidence.

**Robustness findings** (`research_robustness.py -e 500`):
- 45 cycles only — bootstrap 95% CIs overlap across all variants
- LOOCV: single cycle swing = ~14,630 RMB (68% of baseline total)
- 500ETF vol regime matches 300ETF's worst 18% — cross-ETF transfer limited
- Need ~100 cycles (8+ years) for >80% confidence in variant ranking

**Fundamental limitation:** No filter-based approach can prevent the big losses because they occur when RSI is already low (market not overbought). The losses come from intra-cycle sharp rallies (+8-16%) that blow through all strike levels. Early roll management or delta hedging would be needed for further improvement.

**Full report:** `RESEARCH_500ETF.md`

## TODO

- [x] Explore data completeness for 500ETF and make research more robust → `research_robustness.py`
- [ ] Test early roll management for 500ETF — roll calls to higher strikes if underlying rallies >5% mid-cycle
- [ ] Explore weekly options for 500ETF if available — shorter DTE reduces rally exposure
- [ ] Revisit conclusions when 500ETF reaches 80+ cycles (~2029)
