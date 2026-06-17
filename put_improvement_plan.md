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
* **Concept**: Run daily scans. Enter put positions only when specific alpha conditions trigger.
* **Execution**: Evaluate indicator score daily. If threshold met, execute long put entry.

### B. Multi-Dimensional Option Buying Matrix (4-Type Alpha Model)
To maximize hedging efficiency and minimize premium decay, entry decisions map behavior expectation (**How**) against horizon (**When**). Each quadrant runs a dedicated Alpha Model with optimized weightings.

#### 1. The Decision Matrix

| Horizon (When) \ Expected Behavior (How) | **Type 1: Falling (Expected Return < -a% in m days)** | **Type 2: Crash (Chance of >5% drop in m days is >= b%)** |
| :--- | :--- | :--- |
| **Type 1: Short-Term** <br> *m <= 14 calendar days* | **Regime 1: Short-Term Fall** <br> *Action: Buy ATM or OTM1 Put* | **Regime 3: Short-Term Crash** <br> *Action: Buy OTM2 or OTM3 Put* |
| **Type 2: Medium-Term** <br> *14 < m <= 40 calendar days* | **Regime 2: Medium-Term Fall** <br> *Action: Buy ATM or OTM1 Put* | **Regime 4: Medium-Term Crash** <br> *Action: Buy OTM2 or OTM3 Put* |

#### 2. Weighted Alpha Model Framework
For each regime, trigger condition uses a combined weighted score of multiple normalized indicators:
$$\text{Alpha Score} = \sum (w_i \times I_i)$$

Where:
* $I_i$: Normalized technical/statistical indicators (range $[0, 1]$ or $[-1, 1]$).
* $w_i$: Relative weight of indicator $i$, optimized per ETF.
* **Candidate Indicator Families**:
  * *Momentum*: RSI, MACD Histogram, SMA crossovers, ROC.
  * *Volatility / Risk Structure*: Skewness (`skew_20`), Kurtosis (`kurt_20`), Volatility Acceleration (`vol_accel`), IV-RV ratio (`iv_vol_ratio`).
  * *Structural Drawdown*: Realized drawdown (`dd_252`), distance to key moving averages (SMA50, SMA200).

#### 3. Regime Specifications & Instrument Selection
* **Regime 1 (Short-Term Fall)**: Protects against minor correction. High-delta near-term option captures short-term drop.
* **Regime 2 (Medium-Term Fall)**: Protects against ongoing down-trend. Medium DTE protects over weeks.
* **Regime 3 (Short-Term Crash)**: Lottery-like protection. Deep OTM near-term options expand dynamically under vol spikes.
* **Regime 4 (Medium-Term Crash)**: Systemic risk buffer. Deep OTM medium-term options hold value through multi-week declines.

### C. Active Exit Management (Take Profit & Stop Loss) (Optional: leave it for now)
* **Concept**: Lock in option gains before mean reversion or decay erodes them.
* **Rules**:
  * **Premium Multiplier**: Exit if put premium reaches a target multiple (e.g., 2x or 3x).
  * **Underlying Support Target**: Close put if ETF hits support indicators.
  * **Time-based Decay Cut**: Exit position if expected drop fails to materialize within $T$ days to limit Theta burn.

## 4. Implementation Checklist & Progress

* `[x]` **TODO 1: Data Completeness & Sync**
  * Check daily and 5-minute data availability for ETFs and options.
  * Status: **Completed**. Updated daily prices and 5m ETF/option historical data.
* `[ ]` **TODO 2: Signal / Indicator Enhancement**
  * Discover and evaluate daily indicators for predicting worst tail returns (P25/P10). (for Crash)
  * Discover and evaluate daily indicators for negative 14 calendar days, 30 calendar days returns. (for falls)
* `[ ]` **TODO 3: Engine Architecture Modifications**
  * Extend `backtest_engine.py` to support daily option evaluations and mid-cycle execution.
  * Update `BaseStrategy` to allow dynamic entry check (`should_enter_today()`) and exit check (`should_exit_today()`).
* `[ ]` **TODO 4: Alpha Model Integration & Weight Optimization**
  * Implement 4-Type Decision Matrix logic.
  * Backtest multi-indicator weighted score models. Optimize weights ($w_i$), thresholds ($a, b$), and horizons ($m$) per ETF.
* `[ ]` **TODO 5: Dynamic DTE / Contract Selection**
  * Build dynamic option selection matching regime horizons ($m$) to DTE.
  * Evaluate near-month vs. next-month performance dynamically.
* `[ ]` **TODO 6: Walkthrough & Optimization**
  * Run multi-criteria grid search on dynamic triggers, weights, and exit rules.
  * Compile results, compare with static baseline, and update default strategies.