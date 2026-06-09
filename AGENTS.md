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
python eval_synth_filters.py                # Single filter eval on synthetic data
python eval_synth_combinations.py           # Filter combo search on synthetic data
python evaluate_combinations.py             # Filter combo search on real data
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
