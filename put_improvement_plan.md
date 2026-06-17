# Protective Put (Selective Hedge) Improvement Plan

## 1. Current Implementation Summary
* **Timing**: Enter long put at cycle start (usually 4th Tuesday, next day after option expiry). Held until next expiry.
* **Selection**: Fixed OTM levels (OTM1 for 300ETF, OTM2 for 50ETF/500ETF).
* **Execution**: Market orders at entry close (default) or BS-mapped limit buy orders (`--limit-entry`).
* **Condition**: Selective hedging based on cycle-start indicators (RSI, Bollinger Bands, Vol20, MACD).

## 2. Weaknesses & Target Areas for Improvement
* **Negative Theta Drag**: Puts suffer from time decay. Buying a monthly option at cycle start pays significant time value. If the market stays flat or rallies initially, premium is wasted.
* **Static Cycle-Start Filtering**: Risk regimes are evaluated only once a month at cycle start. Bearish indicators may develop mid-cycle, or entry-day signals might be short-lived spikes.
* **Inflexible DTE Selection**: Currently restricted to monthly cycles. Buying options with shorter DTE (e.g., 10–15 days) has lower premium cost (less capital at risk) but faster decay. Dynamic DTE selection (10 vs. 40 DTE) based on signal strength is unexplored.
* **Lack of Active Management / Exit Rules**: Holding all puts to expiry risks giving back profits if a sharp correction occurs early in the cycle and is followed by a bounce.

## 3. Deep Technical Insights & Solutions

### A. Dynamic Entry Timing (Daily Signal Scanning)
* **Concept**: Instead of a binary decision on Day 1 of the cycle, run daily scanning. Enter put position ONLY when the ETF triggers a defined crash condition during the cycle.
* **Triggers**:
  1. **Momentum Breakdown**: ETF close crosses below SMA20 or SMA50, or MACD Hist crosses below zero.
  2. **Vol Spike**: Daily return volatility crosses the 20-day rolling 80th percentile.
  3. **Overbought Reversal**: RSI14 drops below 50 from above 70.
* **Action**: When triggered, enter put leg. If no trigger occurs during the cycle, do not hedge.

### B. Dynamic DTE (Maturity) Selection
* **Concept**: Compare premium efficiency and decay profiles of different maturities.
* **Mechanics**:
  * If a crash signal triggers:
    * **Option A**: Buy front-month contract (standard monthly expiry).
    * **Option B**: Buy next-month contract (if front-month has < 10 DTE remaining).
    * **Option C (Short-term)**: If available, buy weekly or short-dated contract with ~10 DTE.
* **Trade-off**: Shorter DTE offers higher Delta/Premium ratio but faces accelerated Theta decay. Long DTE has slower decay but requires larger cash outlay.

### C. Active Exit Management (Take Profit & Stop Loss)
* **Concept**: Option prices are highly non-linear. Lock in gains on sudden drops.
* **Rules to Test**:
  1. **Premium Multiplier**: Exit put if its price reaches 2x or 3x the entry price.
  2. **ETF Target Support**: Exit put if the underlying ETF drops to a major support line (e.g., Bollinger Band Lower or SMA200) where a bounce is statistically likely.
  3. **Time-based Exit**: If the market does not drop within 5 days of entry, cut the position to limit Theta loss.

## 4. Implementation Checklist & Progress

* `[x]` **TODO 1: Data Completeness & Sync**
  * Check daily and 5-minute data availability for ETFs and options.
  * Run system-wide data updates via `download_5m_data.py`.
  * Status: **Completed**. Updated daily prices up to 2026-06-15 and downloading 5m ETF & option historical data.
* `[ ]` **TODO 2: Signal / Indicator Enhancement**
  * Evaluate daily indicators for predictive power on 30-day forward return tails (e.g., P10/P5 worst outcomes).
  * IMPORTANT: Populate FINDINGS.md with Indicator found before proceeding
  * Note: Previous research shows that single Traditional method, like MACD, RSI, cannot find these.
* `[ ]` **TODO 3: Engine Architecture Modifications**
  * Extend `backtest_engine.py` to support daily option evaluations and mid-cycle execution.
  * Update `BaseStrategy` to allow dynamic entry check (`should_enter_today()`) and exit check (`should_exit_today()`).
* `[ ]` **TODO 4: Dynamic DTE / Contract Selection**
  * Implement logic to load both near-month and next-month contracts.
  * Evaluate performance differences between short-dated (10 DTE) and standard-dated (40 DTE) put purchases under identical triggers.
* `[ ]` **TODO 5: Walkthrough & Optimization**
  * Run multi-criteria grid search on dynamic triggers and exit rules.
  * Compile results, compare with static baseline, and update default strategies.