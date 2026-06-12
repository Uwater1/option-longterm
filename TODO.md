# Limit Order Mechanism

This document describes the limit order execution system for both call selling and put buying.

## Default: Price Taker (implied execution model)

### Entry timing
- **Entry date**: first available option trading day after the previous cycle's expiry (or the very first data day for cycle 1, since no prior expiry exists).
- Filter logic is evaluated on the entry date using that day's ETF close (`entry_date.normalize()`).

### Option execution price (price taker model)
- Uses `opt["close"]` on the **entry date** as the **midprice proxy**.
- **Sell side** (written call legs): `exec_px = close × (1 − SPREAD_HALF)` = `close × 0.98` (effective bid, i.e., we receive less than mid).
- **Buy side** (protective put leg): `exec_px = close × (1 + SPREAD_HALF)` = `close × 1.02` (effective ask, i.e., we pay more than mid).
- `SPREAD_HALF = 0.02` (±2 % slippage from mid, applied symmetrically per leg).

### Commission & exercise cost
- **Commission**: flat `2.0 RMB` per option leg (open + close merged as one flat cost).
- **Exercise cost**: `0.6 RMB` per exercise event when WE are the buyer (put spread buy leg); `0 RMB` if assigned (seller side, call write).
- No transaction cost on the equity leg (ETF shares).

### Settlement at expiry
- Settlement price = last ETF closing price on or before `expiry_date`:
  `etf.loc[etf.index[etf.index <= expiry_date][-1], "close"]`
- Exercise/flagship decision uses unadjusted ETF close vs. (unadjusted) contract strike.
- Premium is realized at entry; exercise P&L settled at expiry close.

### Position sizing (constant)
- `NUM_CONTRACTS = 1` contract per option leg (multiplied per-result after calculation).
- `ETF_SHARES = 20,000` shares per cycle (equity leg, no modeled cost).

### What is NOT modeled (in default mode)
- Intraday order execution (open → close → open timing not simulated).
- Real bid-ask depth / limit order fills.
- Partial fills or slippage beyond the fixed ±2 % mid assumption.
- Cash interest on margin / collateral.

---

## Limit Order Mode (Implemented)

### Overview
The `predict_open_high.py` model predicts the 10th percentile of ETF `(High - Open) / Open`. This prediction is mapped to option limit prices via Black-Scholes, then simulated against 5-minute bar data.

### Call Sell Limit Orders (`--model-offset`)
1. Predict `R_ETF_P10_frac` = P10 of ETF max return over 2-day entry window
2. Compute `σ_open` = implied vol from call's open price via BS inverse
3. Target ETF high: `S_target = S_open × (1 + R_ETF_P10_frac)`
4. Limit sell price: `P_limit = BS(S_target, K, T_new, r, σ_open) × (1 - 0.3% cushion)`
5. Simulate against 5m bars: if any bar's `high ≥ P_limit` in 2-day window → filled at `P_limit`
6. Unfilled → fallback to last 5m bar close

### Put Buy Limit Orders (`--limit-entry`)
1. Same `R_ETF_P10_frac` prediction
2. Compute `σ_open` from put's open price
3. Target ETF high: `S_target = S_open × (1 + R_ETF_P10_frac)`
4. Limit buy price: `P_limit = BS(S_target, K, T_new, r, σ_open) × (1 + OTM-dependent cushion)`
5. Simulate: if any 5m bar's `low ≤ P_limit` → filled at `P_limit`

### Prediction Model Details
- **Features**: 25 candidates, forward selection picks 5–6 per ETF
- **Models**: Statsmodels QR + LightGBM Quantile (ensemble if within 5% CV loss)
- **Bagging**: 5 LightGBM models on bootstrap resamples, averaged
- **Calibration**: Vol-regime-conditional offsets (low-vol vs high-vol, split by median vol20)
- **Adaptive quantile**: Binary search for q' (~0.03–0.04) that natively achieves 90% coverage
- **Augmentation**: Block-bootstrap (20-day blocks, 1x ratio) to reduce overfitting

### Backtest Results (Jun 2026)

| ETF | Mode | P&L | Call Fill Rate | Put Fill Rate |
|-----|------|-----|----------------|---------------|
| 300ETF | Calls-only + Model Offset | +20,492 RMB | 99.0% (95/96) | N/A |
| 300ETF | Combined + Both Limits | +11,469 RMB | 99.3% (139/140) | 94.9% (74/78) |
| 50ETF | Calls-only + Model Offset | +9,119 RMB | 100.0% (98/98) | N/A |
| 500ETF | Calls-only + Model Offset | +19,046 RMB | 92.1% (35/38) | N/A |

---

## Completed TODO
- [x] Download option datas (5m bars, 1 month before expiry) and ETF data
- [x] Research daily relationship between Open and High (Distribution plots, 90% fill rate)
- [x] Predict max(Thursday High, Friday High) for 90%+ entry confidence
- [x] Compare ETF High prediction vs Option High prediction → chose ETF + BS mapping
- [x] Implement Black-Scholes mapping limit entry for protective puts
- [x] Validate BS-mapping limit entry across all 3 ETFs (50/300/500) — 90%+ fill rates confirmed
- [x] Add call-side limit orders with 5m simulation (`--model-offset`)
- [x] Expand candidate features from 14 to 25 (momentum oscillators, prev-day features, tail risk)
- [x] Implement ensemble bagging (5 models) and vol-regime-conditional calibration
- [x] Add cross-ETF pooled training mode (`--pool`)

## Remaining TODO
- [ ] Test early roll management for 500ETF — roll calls to higher strikes if underlying rallies >5% mid-cycle
- [ ] Explore weekly options for 500ETF if available — shorter DTE reduces rally exposure
- [ ] Revisit conclusions when 500ETF reaches 80+ cycles (~2029)


