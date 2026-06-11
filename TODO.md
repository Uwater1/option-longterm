# Limit order machenism

It should be separated from main logic (extract into a dedicated function/module).

## Current code: price taker (implied execution model)

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

### What is NOT modeled
- Intraday order execution (open → close → open timing not simulated).
- Real bid-ask depth / limit order fills.
- Partial fills or slippage beyond the fixed ±2 % mid assumption.
- Cash interest on margin / collateral.

### Improvements:
Enter using limit orders:

## Things we know:
- Thursday Open price (of both ETF and options)
- Data beforehead

## Things we want to perdict:
- low of min(Thursday Low, Friday Low), as we must enter within 2 days
- We want to have 90%+ confidence that we can enter
