# Feature Proposal Specification — Day-Model

## Background

This project operates an intraday linear alpha model ("day-model") that predicts the **trade return** of Chinese equity ETFs within a single trading session. The prediction is used to drive a systematic day-trading strategy that enters positions at the open of a 5-minute bar and exits at 14:30.

### What the Model Does

- **Target**: `trade_return = log(close[14:30] / open[decision_bar + 1])`  
  This is the log return from entry (next-bar open after the decision point) to exit (14:30 close). It mirrors actual trade P&L exactly.

- **Decision timing**: A signal is computed at the close of an early-morning 5-minute bar (the "decision bar"). Entry happens at the open of the following bar. The decision bar varies per ETF (typically 9:45–9:55).

- **Instruments**: 5 Chinese ETFs — SSE 50, CSI 300, CSI 500, STAR 50 (588000), ChiNext (159915).

- **Signal source**: Features are computed from the corresponding **Index** data (e.g. 000300 for 300ETF) to eliminate look-ahead bias. Trade P&L is calculated using **ETF** prices.

- **Model family**: Sparse robust linear regression (skglm with Huber loss + L1/MCP penalty). The pipeline loads 238+ candidate features; stability selection automatically prunes weak ones to ~3–12 final features per ETF.

### Current Feature Space (238 features)

| Group | Count | Description |
|-------|-------|-------------|
| **Early-bar** (139) | Computed from the first 2–6 five-minute bars of the trading day (up to the decision bar). Includes gap %, early return, early realized vol, early range, bar-by-bar returns/volume/range/body-ratio/VWAP-deviation, shape indicators (num up bars, close position in range, path length, volume slope). |
| **Day-level** (74) | Technical indicators and external data computed from **yesterday's** daily close (shifted by 1 day to prevent look-ahead). Includes SMA distances, RSI, MACD, Bollinger %B, realized vol (multiple windows + Parkinson/Garman-Klass), volume ratios, securities margin, capital flow, northbound connect, and option-derived factors (IV, VIX, VIX-IV spread). |
| **Yesterday** (25) | The full-day and early-bar features of the **previous trading day** (shifted by 1 day). Captures serial autocorrelation in intraday patterns. |

### Feature Quality Requirements

Every feature must satisfy these constraints:

1. **No look-ahead bias**: The feature value must be computable using only data available at or before the decision bar close. Day-level features use yesterday's close. Early-bar features use only bars `[0..decision_bar]`.
2. **Numeric and continuous**: The model is linear; features should be real-valued (not categorical).
3. **Stationary or normalized**: Features should be approximately stationary over time. Ratios, percentage changes, and rolling-window normalizations are preferred over raw prices or cumulative values.
4. **Non-degenerate**: The feature must have meaningful variance across trading days. A feature that is constant or near-constant for most days will be dropped by stability selection.
5. **Plausible signal**: There should be a reasoned hypothesis for why this feature predicts the direction of the ETF's intraday return between ~10:00 and 14:30.

---

## What a Deliverable Feature Proposal Looks Like

Each feature proposal must include the following fields. Proposals that omit required fields will be returned for completion.

### Required Fields

| Field | Description |
|-------|-------------|
| **Feature Name** | A short, snake_case identifier (e.g. `pinbar_open_rejection`, `inside_bar_breakout`, `vol_climax_exhaustion`). Must be unique. |
| **Category** | One of: `early_bar`, `day_level`, or `yesterday`. See category definitions below. |
| **Concept / Source** | The price-action pattern, trading concept, or book reference that motivates this feature. Cite the specific book, chapter, or author if applicable. |
| **Formula** | A precise mathematical or algorithmic definition. Use pseudocode or a clear step-by-step description. The formula must be implementable in Python using only OHLCV bars and standard math operations (numpy, scipy). |
| **Input Data** | Exactly what data the feature consumes: which bars (e.g. "first 3 five-minute bars"), which fields (O/H/L/C/V), and whether it needs daily data, intraday data, or both. |
| **Expected Signal Direction** | Whether a high feature value predicts a positive or negative `trade_return`, and why. If the relationship is non-linear or regime-dependent, describe the conditions. |
| **Rationale** | A 2–5 sentence explanation of the economic or behavioral mechanism. Why would market participants' actions cause this pattern to persist intraday? |

### Optional but Valued Fields

| Field | Description |
|-------|-------------|
| **Lookback Window** | If the feature uses a rolling window (e.g. 20-day percentile rank of some intraday metric), specify the window length and why. |
| **Normalization Method** | How the feature should be scaled (e.g. "divide by ATR(14)", "rolling 20-day z-score", "percentile rank over 252 days"). |
| **Known Limitations** | Conditions under which the feature may fail or produce misleading signals (e.g. "unreliable in low-volume sessions", "requires minimum 3 bars of data"). |
| **Related Existing Features** | Which of the current 238 features this is most similar to or might interact with. Helps us check for collinearity. |
| **Supporting Evidence** | Any empirical observation, chart pattern example, or backtest result from the source material. |

### Category Definitions

**`early_bar`** — Computed from the first N five-minute bars of the current trading day (bars 0 through `decision_bar`, typically 2–6 bars covering 9:30–10:00). These features capture opening auction dynamics, early momentum, and intraday price-action patterns.

- Available data per bar: open, high, low, close, volume.
- Previous day's close is available (for gap calculation).
- Expected bar volume is available (rolling 20-day daily volume / 48, shifted by 1 day).
- Bars are 0-indexed, end-timestamped (bar 0 closes at 9:35, bar 5 closes at 10:00).

**`day_level`** — Computed from the full daily price history up to and including **yesterday's close**. These features capture the market regime, trend context, and volatility environment that condition intraday behavior.

- Available data: daily OHLCV (open, high, low, close, volume) for all historical trading days up to T-1.
- Must NOT use today's daily OHLCV (that would be look-ahead bias).
- Typical implementations: rolling indicators (SMA, RSI, ATR, Bollinger), cross-day ratios, percentile ranks.

**`yesterday`** — A mirror of an `early_bar` or full-day feature from the **previous trading day**. Captures day-to-day serial dependence.

- Available data: all 48 five-minute bars of yesterday's session + yesterday's daily OHLCV.

---

## Example Proposals

### Example 1: Pin Bar Rejection (early_bar)

| Field | Value |
|-------|-------|
| **Feature Name** | `pin_bar_rejection` |
| **Category** | `early_bar` |
| **Concept / Source** | Pin bar / hammer candle pattern. Price Action Vol. 1, Al Brooks — rejection of a price level evidenced by a long lower shadow and small body near the high. |
| **Formula** | For bar `i` in `[0..decision_bar]`: `lower_shadow = min(open, close) - low`; `body = abs(close - open)`; `upper_shadow = high - max(open, close)`; `pin_score_i = lower_shadow / (high - low + 1e-8) - upper_shadow / (high - low + 1e-8)`. Final feature = max(pin_score_i) across available bars. High positive value = strong bullish pin bar (long lower shadow, small body near high). |
| **Input Data** | OHLCV of bars `[0..decision_bar]` (Index 5m data). |
| **Expected Signal Direction** | Positive. A bullish pin bar in the first 30 minutes suggests buyers rejected lower prices, predicting upward drift into the afternoon. |
| **Rationale** | Early-session pin bars reflect institutional limit-buy orders absorbing selling pressure at a support level. The rejection creates a local floor, and mean-reversion toward the VWAP drives afternoon upside. |
| **Normalization Method** | Divide by bar range `(high - low)` already normalizes to [−1, +1]. |
| **Related Existing Features** | `bar_body_rng_i` (body-to-range ratio), `cl_pos_in_range` (close position in range). |

### Example 2: Overnight Gap Fill Tendency (day_level)

| Field | Value |
|-------|-------|
| **Feature Name** | `gap_fill_tendency_20d` |
| **Category** | `day_level` |
| **Concept / Source** | Gap-fill trading — gaps tend to fill within the session. Common in multiple price-action and mean-reference literature. |
| **Formula** | Over the last 20 trading days (ending at T-1): count the fraction of days where `|close - prev_close| / prev_close > 0.003` (gap days) AND the same-day range `(high - low)` exceeds `|open - prev_close|` (gap filled). Feature = gap_fill_count / total_gap_days (or 0.5 if no gap days in window). |
| **Input Data** | Daily OHLCV for T-1 through T-21 (Index 1d data). |
| **Expected Signal Direction** | Contextual. When gap-fill tendency is high AND today opens with a gap, expect intraday reversal toward yesterday's close. Interaction with `gap_pct`. |
| **Rationale** | Markets with high gap-fill rates exhibit mean-reversion at the open. Knowing the base rate of gap filling conditions position sizing for gap-fade trades. |
| **Lookback Window** | 20 trading days (~1 calendar month). Short enough to capture regime changes, long enough for statistical stability. |
| **Normalization Method** | Already a ratio in [0, 1]. |
| **Known Limitations** | Low sample size when the market has been range-bound (few gap days). |
| **Related Existing Features** | `gap_pct`, `yesterday_gap_pct`. |

---

## What to Send Back

For each proposed feature, deliver:

1. **The completed proposal table** (all required fields filled in).
2. **Source citation**: Book title, author, edition, and relevant page/chapter. If the concept is synthesized from multiple sources, list all of them.
3. **Pseudocode or formula**: Unambiguous enough to implement directly in Python. If the concept involves subjective judgment (e.g. "identify a head-and-shoulders pattern"), provide objective, quantifiable criteria that approximate the pattern.

### Delivery Format

Send proposals as a structured list (one per feature). Markdown, JSON, or CSV are all acceptable. If sending many features, a table with columns matching the required fields above is preferred.

### Priority Guidance

Focus on features derived from:
- **Opening-range price action** (first 5–30 minutes): patterns that institutional traders react to during the early session and that persist into the afternoon.
- **Intraday regime conditioning**: daily-level context features that change the interpretation of early-bar signals (e.g. "this pin bar matters more when the daily trend is up and volatility is contracting").
- **Volume-price dynamics**: relationships between early volume surges/exhaustion and subsequent directional moves.
- **Multi-day pattern sequences**: features that capture 2–5 day price-action sequences (e.g. "three consecutive inside days followed by a breakout").

Avoid:
- Features that require real-time order book data, tick data, or news sentiment (not available in this pipeline).
- Features that are simple re-combinations of existing features (check the current 130 first).
- Features with very long lookback windows (>252 days) unless the signal is well-documented in literature.

---

## Evaluation Process (What Happens After Submission)

1. **Implementation**: Each proposal is implemented in `build_features.py`.
2. **Stability Selection**: The feature enters the 130+ candidate pool. The `TimeSeriesStabilitySelector` runs 50 stratified block-bootstrap trials with randomized ElasticNet, OOB Spearman IC screening, and cross-fold variance filtering. Features with stability score below the tuned threshold (~40–50%) are pruned.
3. **Walk-Forward IC**: Surviving features are evaluated by purged walk-forward Spearman IC across 5 expanding-window folds.
4. **Holdout Verification**: Final check on a 20% holdout (last ~544 trading days) that was never used in selection or tuning.
5. **Decision**: A feature is **kept** if it achieves: stability score ≥ threshold AND positive mean walk-forward IC AND does not degrade the holdout Long/Short Sharpe of the existing model.

Results will be shared back so the proposing project can see which features survived and their quantitative impact.
