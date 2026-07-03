# Feature Proposal Specification — Day-Model

## Background

This project operates an intraday linear alpha model ("day-model") that predicts the **trade return** of Chinese equity ETFs within a single trading session. This guide is designed for feature-seeking agents to propose high-quality, context-specific features that can be integrated into our pipeline.

### Target & Causality

- **Target**: `trade_return = log(close[14:30] / open[decision_bar + 1])`  
  This is the log return from the entry bar open (immediately after the decision bar close at 10:00) to the exit at 14:30 (bar 41 close / bar 42 open). It mirrors actual trade P&L exactly.
- **Decision Timing**: Decision bar closes at 10:00 (bar index 5). Position entry is at 10:00 (bar 6 open).
- **Causality Constraint**: All features must be strictly causal.
  - **Early-bar features**: Must only consume 5m bars `[0..5]` (9:30 to 10:00).
  - **Day-level features**: Must be shifted by 1 day (e.g. using yesterday's daily close or yesterday's summary indicators) to prevent look-ahead bias.
  - **Yesterday-mirror features**: Full-day or early-bar metrics from yesterday (shifted 1 day).

### Chinese Market Context

Features should leverage the specific microstructure and macroeconomic characteristics of the Chinese A-share market:

1. **Market Segmentation & Dual Limits**:
   - **SSE 50, CSI 300, CSI 500**: Underlyings have a $\pm 10\%$ daily price limit.
   - **STAR 50 (588000), ChiNext (159915)**: Underlyings have a $\pm 20\%$ daily price limit. Growth and tech-oriented. Volatility regimes and momentum persistence are structurally different.
2. **Lunch Break Split**:
   - Trading halts from 11:30 to 13:00. This creates an "intraday gap" where news can accumulate. Reversal or continuation patterns across the lunch break are common.
3. **Ricequant Data Availability**:
   - The pipeline caches daily/intraday Ricequant data: **Securities Margin** (leveraged retail balance), **Capital Flow** (large order net buy), **Northbound Connect** (foreign institutional flow), and **ATM IV / Ricequant VIX** (option implied volatility).

---

## Code Structure

### 1. `day-model/features_extra.py`
Contains the JIT-compiled Numba implementations for early-bar and daily indicators to ensure high performance.
- **`EARLY_EXTRA` registry**: Add your feature name to the list.
- **`_early_extras` dispatcher**: Numba JIT function (`@njit(cache=True, fastmath=True)`) that calculates early-bar features for a single day.
  - Inputs: `op` (open), `hi` (high), `lo` (low), `cl` (close), `vol` (volume), `prev_close`, `exp_bar_vol`.
  - Outputs: Returns a float32 array in the exact order of the registry.

### 2. `day-model/build_features.py`
Calculates and joins all features, saving them in `data/features_{ETF}.parquet`.
- Registered list of `EARLY_FEATURES`, `DAY_FEATURES`, and `YESTERDAY_FEATURES`.

---

## Required Fields for Proposals

Every proposed feature must be submitted as a table containing:

| Field | Description |
| :--- | :--- |
| **Feature Name** | Short, unique `snake_case` identifier. |
| **Category** | `early_bar`, `day_level`, or `yesterday`. |
| **Concept / Source** | Trading concept, paper, or book reference (e.g., Al Brooks Price Action, Larry Williams, etc.). |
| **Formula & Math** | Mathematical definition or step-by-step JIT-compatible logic. |
| **Microstructure Mechanism** | The economic or behavioral reason why this pattern should persist in the Chinese ETF market. |
| **Normalization Method** | How scale invariance is achieved (e.g., divided by ATR, normalized by rolling 20d daily volume). |

---

## Target Areas for New Features

### 1. Growth vs Value Divergence (ChiNext / STAR 50)
- **Concept**: ChiNext/STAR 50 are highly sensitive to retail sentiment, liquidity shifts, and limit-up price magnets.
- **Example Ideas**: Proximity of early high/low to the 20% limit-up/limit-down threshold, or early volume surges relative to the 20d median on STAR 50.

### 2. Lunch Break Transition / Intraday Reversals
- **Concept**: The 11:30 - 13:00 halt often triggers momentum exhaustion.
- **Example Ideas**: Early-morning trend persistence (e.g., HHI of price directions) predicting afternoon fade or continuation.

### 3. Option IV and VIX Dynamics
- **Concept**: Implied volatility shifts ahead of price.
- **Example Ideas**: Overnight VIX-IV spread change, or 1d rate-of-change of the Ricequant VIX index relative to historical quantiles.

### 4. Capital Flow and Northbound Momentum
- **Concept**: Net capital flows from large transactions indicate institutional buying.
- **Example Ideas**: Northbound net buy volume normalized by yesterday's total volume.
