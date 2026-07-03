# Feature Proposals — Day-Model
Selected features derived from Al Brooks price action concepts (Al Brooks, *Trading Price Action Trading Ranges*, Wiley 2012; *Reading Price Charts Bar by Bar*, Wiley 2009).

---

## 1. opening_gap_reversal
| Field | Value |
|-------|-------|
| **Feature Name** | `opening_gap_reversal` |
| **Category** | `early_bar` |
| **Concept / Source** | Al Brooks, Chapter 6 "Gaps" — gap reversal pattern. A gap-up open where the first 5-minute bar trades back below the open, or a gap-down open where the first bar trades back above the open, signals absorption of the opening imbalance. |
| **Formula** | Let `prev_c` = prior trading day Index close. `gap_pct = (open_bar0 - prev_c) / prev_c`. For a bullish gap (`gap_pct > 0.002`): `up_reversal = max(0, open_bar0 - min(bar0_low, bar1_low)) / (open_bar0 - prev_c + 1e-8)`. For a bearish gap (`gap_pct < -0.002`): `down_reversal = max(0, max(bar0_high, bar1_high) - open_bar0) / (prev_c - open_bar0 + 1e-8)`. Final `opening_gap_reversal = up_reversal - down_reversal`. Returns a signed ratio in roughly (-1, 1). |
| **Input Data** | OHLC of bars [0, 1] (Index 5m); prior day Index close. |
| **Expected Signal Direction** | Negative. A positive value (bullish gap sold into) predicts fading of the gap and lower `trade_return`. A negative value (bearish gap bought into) predicts negative trade_return in the short side, i.e., afternoon bounce. Generally, high absolute gap reversal predicts mean reversion. |
| **Rationale** | Opening gaps reflect overnight sentiment, but early-bar reversal shows institutional limit orders absorbing the opening imbalance. The resulting local extreme tends to revert toward VWAP by 14:30. |
| **Normalization Method** | Ratio already bounded near [−1, 1] by construction. No further scaling needed. |
| **Known Limitations** | Unreliable in very low-volume sessions where gaps are thin. Requires at least 2 bars; the decision bar must be ≥ bar 1. |
| **Related Existing Features** | `gap_pct`, `yesterday_gap_pct`, `early_return`. |

---

## 2. spike_exhaustion_ratio
| Field | Value |
|-------|-------|
| **Feature Name** | `spike_exhaustion_ratio` |
| **Category** | `early_bar` |
| **Concept / Source** | Al Brooks, "Spike and Channel" — a strong initial impulse (spike) followed by a channel with diminishing momentum signals exhaustion. "Traditional gaps (breakout, measuring, and exhaustion) on daily charts have intraday equivalents in the form of various trend bars." |
| **Formula** | Let `bars = [0..decision_bar]`. `spike_strength = max(body_ratio(bar0), body_ratio(bar1))`. `channel_strength = mean(body_ratio(bar_i) for i in [2..decision_bar])` if `decision_bar >= 2`, else `body_ratio(bar1)`. `spike_exhaustion_ratio = spike_strength / (channel_strength + 1e-8) - 1`. High positive = strong spike then weak follow-through (exhaustion). High negative = weak spike then strong channel (momentum building). |
| **Input Data** | OHLC of bars [0..decision_bar] (Index 5m). |
| **Expected Signal Direction** | Negative when positive. A high `spike_exhaustion_ratio` predicts that the opening impulse was one-sided and unsustainable, leading to lower trade_return. A negative ratio predicts continuation. |
| **Rationale** | Early aggressive positioning without follow-through leaves a supply/demand vacuum that market makers exploit by fading the spike. Weak channel bars after a strong open indicate fading conviction. |
| **Normalization Method** | Divide by `early_realized_vol` or `ATR(20)` of the opening range to make stationary across volatility regimes. |
| **Known Limitations** | Sensitive to outlier bars; should winsorize at 95th percentile. Fails in trending markets where spike is genuine trend start. |
| **Related Existing Features** | `bar_body_rng_i`, `path_length`, `early_return`, `early_range`. |

---

## 3. barbed_wire_intensity
| Field | Value |
|-------|-------|
| **Feature Name** | `barbed_wire_intensity` |
| **Category** | `early_bar` |
| **Concept / Source** | Al Brooks glossary: "barbwire A trading range of three or more bars that largely overlap and one or more is a doji. It is a type of tight trading range with prominent tails." Represents extreme indecision with Visible buying and selling at nearby levels. |
| **Formula** | Scan bars [0..decision_bar] for the longest consecutive sequence `seq` of ≥3 bars where `high_i <= high_{i-1} + epsilon` and `low_i >= low_{i-1} - epsilon` (range overlap). `doji_count = sum(1 for b in seq if abs(open-close) < 0.2 * (high-low + 1e-8))`. `avg_tail = mean((high - max(open,close) + min(open,close) - low) / (high - low + 1e-8) for b in seq)`. `barbed_wire_intensity = len(seq) * doji_count * avg_tail / (decision_bar + 1)`. Returns 0 if no sequence detected. |
| **Input Data** | OHLC of bars [0..decision_bar] (Index 5m). |
| **Expected Signal Direction** | Negative. High intensity indicates market equilibrium with no net directional commitment, predicting a narrow intraday range and drift toward the mean (open/VWAP). |
| **Rationale** | Overlapping bars with long tails and small bodies show that traders are rejecting both higher and lower prices equally. This equilibrium dissipates into low-volatility drift rather than directional expansion. |
| **Normalization Method** | Already bounded in [0, 1] by dividing by `decision_bar + 1`. |
| **Known Limitations** | Rare in high-volatility regime days. Requires at least 3 bars (decision_bar ≥ 2). |
| **Related Existing Features** | `cl_pos_in_range`, `early_realized_vol`, `bar_body_rng_i`. |

---

## 4. wedge_open_flag
| Field | Value |
|-------|-------|
| **Feature Name** | `wedge_open_flag` |
| **Category** | `early_bar` |
| **Concept / Source** | Al Brooks, Chapter 18 "Wedge and Other Three-Push Pullbacks". High 3 / Low 3 patterns: three swing highs getting lower (bear wedge flag) or three swing lows getting higher (bull wedge flag) within a trend indicate a pullback that typically resolves in the trend's direction. |
| **Formula** | In bars [0..decision_bar], identify swing highs/lows using `pivot_high(i) = high_i > high_{i-1} and high_i > high_{i+1}` (and symmetric for low). If there are exactly 3 pivot highs with each lower than the prior: `wedge_open_flag = -1` (bear wedge, continuation up expected). If there are 3 pivot lows with each higher: `wedge_open_flag = +1` (bull wedge, continuation down expected if in bear trend, but in general bull wedge flag in bull trend = +1). If no wedge: 0. Simplified: `sign = +1` if 3 rising lows in existence, `−1` if 3 falling highs exist, else 0. |
| **Input Data** | OHLC of bars [0..decision_bar] (Index 5m). |
| **Expected Signal Direction** | Positive. A detected wedge flag (especially bull wedge in a bull regime) predicts higher trade_return as the trend resumes from consolidation. The exact sign depends on wedge type; for a signed feature `+1 = bull flag, −1 = bear flag`. |
| **Rationale** | Three-push wedges in the opening session are mechanical pullbacks within the dominant trend. Traders who faded the wedge leg get stopped out as the original trend resumes, accelerating the afternoon move. |
| **Normalization Method** | Already discrete/signed. For continuous use: multiply by `convergence = 1 - (|slope(upper)| - |slope(lower)|) / ATR(5m)` to capture tightness. |
| **Known Limitations** | Unreliable if fewer than 5 bars (decision_bar ≤ 4). Can fail in very choppy markets where wedges are nested. |
| **Related Existing Features** | `early_return`, `bar_body_rng_i`, `cl_pos_in_range`. |

---

## 5. inside_bar_compression
| Field | Value |
|-------|-------|
| **Feature Name** | `inside_bar_compression` |
| **Category** | `early_bar` |
| **Concept / Source** | Al Brooks, "ii" and "iii" patterns: "Consecutive inside bars... breakout mode setup where a trader looks to buy above the inside bar or sell below it." Also called coiling or volatility compression. |
| **Formula** | `inside = [i for i in [1..decision_bar] if high_i <= high_{i-1} and low_i >= low_{i-1}]`. `avg_range_inside = mean(high_i - low_i for i in inside)`. `avg_range_all = mean(high_i - low_i for i in [0..decision_bar])`. `inside_bar_compression = 1 - avg_range_inside / avg_range_all`. If no inside bars, return 0. |
| **Input Data** | OHLC of bars [0..decision_bar] (Index 5m). |
| **Expected Signal Direction** | Positive when interaction with breakout direction is favorable. High compression increases the probability of a larger afternoon range; the model should learn that `compression * sign(close_decision_bar - open_bar0)` predicts trade direction. Alone, it conditions volatility. |
| **Rationale** | Inside bars represent a coiling of price where supply and demand are in balance. When the coil breaks, the afternoon session often experiences a sweep of the opening range extremes before settling. |
| **Normalization Method** | Already bounded in [0, 1]. |
| **Known Limitations** | Directional sign must come from interaction term; standalone feature is volatility-only. |
| **Related Existing Features** | `early_realized_vol`, `path_length`, `vol_slope`. |

---

## 6. volume_climax_exhaustion
| Field | Value |
|-------|-------|
| **Feature Name** | `volume_climax_exhaustion` |
| **Category** | `early_bar` |
| **Concept / Source** | Al Brooks, "climax: A move that has gone too far too fast and has now reversed direction to either a trading range or an opposite trend." Early-session climax often foreshadows a session-wide trading range. |
| **Formula** | `expected_vol = Index_daily_volume[T-1] / 48` (shifted by 1 day). `vol_ratio_i = volume(bar_i) / expected_vol`. `peak_bar = argmax(vol_ratio_i)` in bars [0..decision_bar]. `reversal_score = 1 - 2 * abs(close(peak_bar) - (high(peak_bar)+low(peak_bar))/2) / (high(peak_bar) - low(peak_bar) + 1e-8)`. `volume_climax_exhaustion = max(vol_ratio(peak_bar) - 1.0, 0) * reversal_score`. |
| **Input Data** | OHLCV of bars [0..decision_bar] (Index 5m); Index daily volume T-1 (shifted by 1 day). |
| **Expected Signal Direction** | Negative. High value indicates volume climax on a reversal bar in opening session, predicting mean reversion and lower trade_return in the direction of the spike. |
| **Rationale** | Climactic volume bars in the first 30-60 minutes reflect aggressive one-sided flow that quickly exhausts. The resulting equilibrium shifts the market into a range that persists through the afternoon exit time. |
| **Normalization Method** | Winsorize at 99th percentile across training days; then min-max scale to [0, 1]. |
| **Known Limitations** | Sensitive to corporate action days or index rebalance days with unusual volume. |
| **Related Existing Features** | `vol_ratio`, `vol_slope`, `vol_clustered_ratio`. |

---

## 7. twenty_gap_bars_regime
| Field | Value |
|-------|-------|
| **Feature Name** | `twenty_gap_bars_regime` |
| **Category** | `day_level` |
| **Concept / Source** | Al Brooks, Chapter 13 "Twenty Gap Bars" — "A bar that does not touch the moving average. The first pullback in a strong trend that results in a moving average gap bar is usually followed by a test of the trend's extreme." Extended gap-bar streaks build a trend channel. |
| **Formula** | Using daily Index closes T-252 to T-1: `ema20 = EMA(close, 20)`. `consec_bull = length of current streak where close > ema20` ending at T-1. `consec_bear = length of current streak where close < ema20` ending at T-1. `twenty_gap_bars_regime = (consec_bull - consec_bear) / 20`. Clip to [−1, 1]. |
| **Input Data** | Daily Index OHLC, T-252 to T-1 (at least 60 days minimum). |
| **Expected Signal Direction** | Positive. Extended bullish gap-bar streak conditions dip-buying behavior, making intraday pullbacks short-lived and boosting afternoon upside. Negative streak predicts fade. |
| **Rationale** | Prolonged separation from the moving average builds institutional trend-following positions. These algorithms add on dips, creating a floor under the index that persists into the intraday session. |
| **Normalization Method** | Divided by 20 (max lookback). Winsorized at ±1. |
| **Known Limitations** | Slow-changing regime variable; may have near-zero variance in flat markets. Minimum 20 days of history required. |
| **Related Existing Features** | `sma_dists` (cross-sectional distance), `rsi` (oscillator-based trend). |

---

## 8. measured_move_proximity
| Field | Value |
|-------|-------|
| **Feature Name** | `measured_move_proximity` |
| **Category** | `day_level` |
| **Concept / Source** | Al Brooks, Chapter 7 "Measured Moves Based on the Size of the First Leg (the Spike)". "Markets gravitate toward areas of support and resistance, which are usually some type of measured move away." |
| **Formula** | On daily Index chart T-252 to T-1, detect the most recent completed leg using 2-bar pivot rule: `swing_high(bar_i) = high_i >= high_{i-1} and high_i >= high_{i+1}`. Find last swing high `H` and last swing low `L` before T-2. If last move was up: `target = H + (H - L)`. If last move was down: `target = L - (L - H)`. `raw_proximity = (close[T-1] - target) / ATR(14, daily)`. `measured_move_proximity = max(min(raw_proximity, 2), -2)`. |
| **Input Data** | Daily Index OHLC, T-252 to T-1. |
| **Expected Signal Direction** | Negative when `proximity > 1` (overshoot). If T-1 closed above a bullish measured move target, expect profit-taking and lower trade_return. Negative proximity in a downtrend (near target) predicts bounce (positive trade_return). |
| **Rationale** | Measured move projections are common algorithmic profit-taking zones. When price reaches or exceeds these levels, trend-following orders reverse, causing a pause or pullback that spills into the next trading day's intraday session. |
| **Normalization Method** | Divided by 14-day ATR(daily) to make volatility-adjusted. Winsorized at ±2. |
| **Known Limitations** | Swing detection is noisy; use simplified 2-bar pivot to avoid overfitting. Fails in the absence of a clear recent leg (>10 bars). |
| **Related Existing Features** | `bollinger_pct_b`, `rsi`, `realized_vol_20d`. |
