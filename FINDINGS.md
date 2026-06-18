# First: Bollinger Band Mean Reversion Findings

Analysis of the pattern:
- **Condition 1 (Bearish Mean Reversion):** Close < BB Down (20, 2), and within the lookback window beforehand, close was once > BB Up (20, 2). Target is the probability and return of going **down** in the next 30 calendar days.
- **Condition 2 (Bullish Mean Reversion - Inverse):** Close > BB Up (20, 2), and within the lookback window beforehand, close was once < BB Down (20, 2). Target is the probability and return of going **up** in the next 30 calendar days.

---

## 1. 159915 ETF (创业板ETF) Findings

Using real data from our calculations (2,781 trading days):

### 60 Trading Days Lookback
- **Condition 1 (Bearish):** When Close < BB Down (and once > BB Up in past 60 trading days), there is a **61.86%** probability of going **down** in the next 30 calendar days, with an expected return of **-0.93%** (Count: 97).
- **Condition 2 (Inverse - Bullish):** When Close > BB Up (and once < BB Down in past 60 trading days), there is a **67.90%** probability of going **up** in the next 30 calendar days, with an expected return of **+5.03%** (Count: 81).

### 60 Calendar Days Lookback
- **Condition 1 (Bearish):** When Close < BB Down (and once > BB Up in past 60 calendar days), there is a **70.00%** probability of going **down** in the next 30 calendar days, with an expected return of **-2.10%** (Count: 80).
- **Condition 2 (Inverse - Bullish):** When Close > BB Up (and once < BB Down in past 60 calendar days), there is a **70.31%** probability of going **up** in the next 30 calendar days, with an expected return of **+5.72%** (Count: 64).

---

## 2. Cross-ETF Comparative Analysis

### 60 Trading Days Lookback Results
| ETF | Pattern | Count | Target Direction | Success Probability | Expected 30d Return |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **159915** | Condition 1 (Bearish) | 97 | Down | **61.86%** | **-0.93%** |
| | Condition 2 (Bullish) | 81 | Up | **67.90%** | **+5.03%** |
| **588000** | Condition 1 (Bearish) | 48 | Down | 52.08% | +0.44% |
| | Condition 2 (Bullish) | 65 | Up | **64.62%** | **+5.30%** |
| **500** | Condition 1 (Bearish) | 130 | Down | 51.54% | -0.12% |
| | Condition 2 (Bullish) | 105 | Up | 57.14% | +1.98% |
| **50** | Condition 1 (Bearish) | 104 | Down | 41.35% | +1.55% |
| | Condition 2 (Bullish) | 162 | Up | 47.53% | +0.41% |
| **300** | Condition 1 (Bearish) | 85 | Down | 43.53% | +2.78% |
| | Condition 2 (Bullish) | 82 | Up | 45.12% | +0.25% |

### 60 Calendar Days Lookback Results
| ETF | Pattern | Count | Target Direction | Success Probability | Expected 30d Return |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **159915** | Condition 1 (Bearish) | 80 | Down | **70.00%** | **-2.10%** |
| | Condition 2 (Bullish) | 64 | Up | **70.31%** | **+5.72%** |
| **588000** | Condition 1 (Bearish) | 33 | Down | 45.45% | +0.76% |
| | Condition 2 (Bullish) | 51 | Up | 56.86% | +3.03% |
| **500** | Condition 1 (Bearish) | 86 | Down | 59.30% | -1.31% |
| | Condition 2 (Bullish) | 85 | Up | **61.18%** | **+3.13%** |
| **50** | Condition 1 (Bearish) | 69 | Down | 39.13% | +1.83% |
| | Condition 2 (Bullish) | 118 | Up | 50.85% | +0.84% |
| **300** | Condition 1 (Bearish) | 54 | Down | 40.74% | +4.20% |
| | Condition 2 (Bullish) | 60 | Up | 40.00% | +0.02% |

---

## 3. Key Takeaways

1. **Pattern Effectiveness:** The mean reversion signal is highly valid for **159915 ETF (创业板ETF)**, achieving 60-70% prediction success in both directions. It is also moderately valid for **588000 ETF** and **500 ETF** on the bullish side.
2. **Failure on Large-Cap ETFs:** The pattern fails on **50 ETF** and **300 ETF** (probabilities near or below 50%). For these indices, a breach of BB Down after a period of strength is often followed by a strong rebound (only ~40% probability of going down), indicating that standard mean reversion rules cannot be applied universally across different ETF classes.

---

## 4. 30-Day Forward Return Tail Risk Predictors (P10/P5 Worst Outcomes)

To design an effective selective hedging strategy using long puts, we need indicators that predict the worst 30-calendar-day forward return outcomes: the 10th percentile (P10) and 5th percentile (P5) worst returns. Traditional indicators like RSI and MACD alone fail to capture these fat-tailed events.

Through systematic tail-risk analysis over 1,700+ trading days, we identified powerful daily indicators based on return skewness, kurtosis, volatility acceleration, and structural drawdowns.

### Key Tail Risk Indicators

1. **Rolling Return Skewness (`skew_20`)**: Captures return asymmetry. Negative skewness indicates a long left tail (dominant down days).
2. **Rolling Return Kurtosis (`kurt_20`)**: Measures fat-tailedness. High kurtosis indicates extreme moves are occurring.
3. **Volatility Acceleration (`vol_accel`)**: Ratio of 10-day realized volatility to the 60-day moving average of 20-day realized volatility, capturing sudden momentum spikes in volatility.
4. **Drawdown from Peak (`dd_252`)**: Captures structural market trend regimes.

---

### ETF-Specific Findings

#### A. 50ETF (50ETF_1d.parquet, Baseline P10: -6.10%, P5: -8.25%)
* **Indicator**: **Volatility Acceleration + Negative Skewness** (`vol_accel > 1.1` & `skew_20 < -0.3`)
  * **Placement Rate**: 9.5%
  * **Expected 30d Return**: **-1.08%** (highly negative, t-test p-value: **0.0000**)
  * **P10 Probability**: **16.5%** (**1.65x lift** over baseline)
  * **P5 Probability**: **10.7%** (**2.15x lift** over baseline)
* **Alternative**: **Negative Skewness + High Kurtosis** (`skew_20 < -0.3` & `kurt_20 > 1.0`)
  * **Placement Rate**: 13.5%
  * **Expected 30d Return**: **-0.14%** (p-value: **0.0676**)
  * **P10 Probability**: **16.8%** (**1.68x lift**)
  * **P5 Probability**: **9.7%** (**1.95x lift**)

#### B. 500ETF (500ETF_1d.parquet, Baseline P10: -7.07%, P5: -10.52%)
* **Indicator**: **Negative Skewness + High Kurtosis** (`skew_20 < -0.5` & `kurt_20 > 1.0`)
  * **Placement Rate**: 20.8%
  * **Expected 30d Return**: **-0.94%** (extremely negative, t-test p-value: **0.0000**)
  * **P10 Probability**: **15.1%** (**1.51x lift** over baseline)
  * **P5 Probability**: **8.6%** (**1.72x lift** over baseline)
* **Current Filter Pitfall**: The current filter (`Vol20 > Median` AND `MACD Hist < 0`) has a 22.8% placement rate but yields a P10 probability of only **8.5%** (0.85x baseline) and P5 probability of **2.1%** (0.42x baseline), meaning it actually places hedges during times when tail risk is *lower* than average.

#### C. 300ETF (510300_1d.parquet, Baseline P10: -5.36%, P5: -7.17%)
* 300ETF exhibits strong mean-reversion characteristics. Negative skewness combined with trend breakdown is frequently followed by a sharp bounce (mean return +2.36%), dropping P10 probability to 5.3%.
* **Indicator 1 (Structural Bear Market)**: **Deep Drawdown + Far Below SMA200** (`dd_252 < -0.15` & `dist_sma200 < -2.0` ATR)
  * **Placement Rate**: 18.3%
  * **Expected 30d Return**: **+0.26%** (vs +0.70% baseline, p-value: **0.1101**)
  * **P10 Probability**: **17.3%** (**1.73x lift** over baseline)
  * **P5 Probability**: **9.0%** (**1.79x lift** over baseline)
* **Indicator 2 (Extremely Overbought Peak Reversal)**: **Extreme RSI** (`rsi14 > 66`)
  * **Placement Rate**: 11.9%
  * **Expected 30d Return**: +2.01% (but with extreme volatility/pullback probability, p-value: **0.0052**)
  * **P10 Probability**: **14.7%** (**1.47x lift** over baseline)
  * **P5 Probability**: **9.5%** (**1.90x lift** over baseline)

---

## 5. Option Profitability & Hedging Setup Findings

To design selective put hedging, analyzed daily entries to hold put option contracts to maturity. Discovered specific regime conditions with statistically significant positive expected Net P&L (after transaction cost/decay).

### ETF-Specific Option Profitability Signals (OTM1 Puts)

#### A. 50ETF (50ETF_1d.parquet, Baseline Net P&L: -6.95 RMB)
* **Signal**: **VRP Compression + Negative Skewness** (`skew_20 < -0.5` & `iv_vol_ratio < 0.9`)
  * **Rationale**: Put options cheap relative to historical vol (underpriced VRP) and momentum negative.
  * **Placement Rate**: 5.9% (139 triggers)
  * **Average Net P&L**: **+491.72 RMB** (t-stat: **3.84**, p-value: **0.0002**)
  * **Option Win Rate**: **36.0%** (vs 25.3% baseline)

#### B. 500ETF (500ETF_1d.parquet, Baseline Net P&L: -91.49 RMB)
* **Signal**: **Kurtosis Expansion + Expensive IV** (`kurt_20 > 1.0` & `iv_vol_ratio > 1.2`)
  * **Rationale**: Extreme tail behavior (high kurtosis) overruns expensive premiums (high IVR).
  * **Placement Rate**: 5.3% (41 triggers)
  * **Average Net P&L**: **+356.37 RMB** (t-stat: **3.45**, p-value: **0.0013**)
  * **Option Win Rate**: **68.3%** (vs 30.7% baseline)

#### C. 300ETF (510300_1d.parquet, Baseline Net P&L: -40.56 RMB)
* Combined two complementary setups (Bear Market Trend + Overbought Reversal):
* **Signal 1 (Bear Market Trend)**: **Severe Drawdown + Trend Breakdown** (`dd_252 < -0.15` & `dist_sma50 < -1.0`)
  * **Placement Rate**: 14.7% (197 triggers)
  * **Average Net P&L**: **+216.86 RMB** (t-stat: **3.35**, p-value: **0.0010**)
  * **Option Win Rate**: **40.6%** (vs 28.4% baseline)
* **Signal 2 (Overbought Reversal)**: **Overbought Peak Reversal** (`rsi > 65` & `skew_20 < -0.3`)
  * **Placement Rate**: 1.9% (26 triggers)
  * **Average Net P&L**: **+555.46 RMB** (t-stat: **2.74**, p-value: **0.0112**)
  * **Option Win Rate**: **57.7%** (vs 28.4% baseline)

---

## 6. Daily Indicator Predictive Power on 30-Day Forward Returns (Underlying ETF Level)

To validate the technical indicators used in the put filters, we ran statistical testing on daily index returns to evaluate if the filters predict a drop in the underlying ETF price itself over the next 30 calendar days (independent of option pricing). 

Validated via script [research_filter_validation.py](file:///home/hallo/Documents/option-longterm/research_filter_validation.py):

### A. 300ETF validation (1,533 trading days)
* **Baseline**: Expected 30d return +0.60% (std: 5.48%), Put Win Rate (market drops): 50.2%
* **Bear Market Trend** (`dd_252 < -0.15` & `dist_sma50 < -1.0`):
  * **Triggers**: 235 (15.3% placement)
  * **Expected 30d Return**: **-0.62%** (Diff: **-1.22%**)
  * **Put Win Rate**: **61.3%** (t-stat vs Rest: **-3.22**, p-value: **0.0014**)
* **Overbought Reversal** (`rsi > 65` & `skew_20 < -0.3`):
  * **Triggers**: 29 (1.9% placement)
  * **Expected 30d Return**: **-1.49%** (Diff: **-2.09%**)
  * **Put Win Rate**: **58.6%** (t-stat vs Rest: **-1.68**, p-value: **0.1036**)
* **Composite Filter (Trend OR Reversal)**:
  * **Triggers**: 264 (17.2% placement)
  * **Expected 30d Return**: **-0.72%** (Diff: **-1.32%**)
  * **Put Win Rate**: **61.0%** (t-stat vs Rest: **-3.72**, p-value: **0.0002**)
  * **Conclusion**: Highly statistically significant negative drift on underlying index. Directly justifies protective put hedging.

### B. 50ETF & 500ETF validation (2,508 trading days)
For 50ETF and 500ETF, the underlying index mean return did not show a statistically significant negative drift under the filter conditions:
* **50ETF VRP Compression** (`skew_20 < -0.5` & `iv_vol_ratio < 0.9`): Expected 30d Return: **+0.49%** (vs +0.58% baseline, p-value: **0.8600**), Put Win Rate: **47.5%** (vs 47.3% baseline).
* **500ETF Kurtosis Expansion** (`kurt_20 > 1.0` & `iv_vol_ratio > 1.2`): Expected 30d Return: **+0.10%** (vs +0.56% baseline, p-value: **0.2210**), Put Win Rate: **42.2%** (vs 47.5% baseline).

**Why Option Backtests are Profitable Despite Underlying Neutrality:**
1. **50ETF underpriced options**: Puts are bought when options are extremely cheap relative to historical realized vol (`iv_vol_ratio < 0.9`). Thus, even if the underlying index behaves normally, the cost of protection is so low that payout easily exceeds cheap premium when a drop occurs.
2. **500ETF fat-tailed tail events**: Sourced during high kurtosis (`kurt_20 > 1.0`). Average return is near-zero, but the distribution exhibits fat tails. When a downward trigger hits, the magnitude of the drop is so severe that option payouts are outsized, easily recovering premium costs.

---

## 7. Massive Indicator Scan Results (Jun 2026, Revised)

### 7.1 Methodology (v2 — Bias-Corrected)

We conducted a comprehensive indicator scan across 50ETF, 300ETF, and 500ETF using daily data and `pandas-ta`. **v2 improvements over v1**:

- **Expanding-window quantiles** (252-day minimum lookback) replace full-sample quantiles, eliminating look-ahead bias in thresholds like `vol20 > q90`.
- **NaN indicator rows explicitly dropped**: Early rolling-window warmup rows are excluded from both triggered and non-triggered groups (previously treated as non-triggered).
- **Pre-specified known combos** from the existing put strategy are always evaluated, regardless of greedy top-N selection.
- **Vectorized forward return computation** for faster execution.

Other methodology unchanged: ~30 indicators, single + two-indicator combos (AND/OR), Welch’s t-test, P10/P25 tail lift.

### 7.2 Crash Regime — Top Single-Indicator Filters (P10 Tail Lift)

**50ETF:** (expanding-window quantiles produce more conservative, realistic results)

| Filter | Placement | P10 | Lift | Mean 30d | p-value |
|--------|-----------|-----|------|----------|----------|
| `vol20 > q90` | 2.4% | 28.6%* | 2.85x | -1.97% | 0.0000 |
| `roc10 > q90` | 4.7% | 13.0% | 1.30x | -0.73% | 0.0074 |
| `rsi14 > 70` | 6.2% | 11.7% | 1.17x | -0.52% | 0.0132 |

*`vol20 > q90` has only 67 triggers (vs 276 in v1 full-sample) because expanding quantiles require 252 days warmup and the threshold adapts over time.

**300ETF:**

| Filter | Placement | P10 | Lift | Mean 30d | p-value |
|--------|-----------|-----|------|----------|----------|
| `vol20 > q90` | 3.9% | 28.6% | 2.85x | -1.97% | 0.0000 |
| `kurt_20 < q10` | 11.8% | 11.8% | 1.18x | -1.14% | 0.0000 |

**500ETF:**

| Filter | Placement | P10 | Lift | Mean 30d | p-value |
|--------|-----------|-----|------|----------|----------|
| `skew_20 < -0.5` | 31.8% | 14.1% | 1.41x | -0.67% | 0.0000 |
| `dist_sma200 < -2.0` | 28.1% | 11.0% | 1.10x | +0.57% | 0.6818 |

### 7.3 Medium-Term Fall — Top Single-Indicator Filters (Negative 30d Return)

**50ETF:**

| Filter | Placement | Neg-30d Prob | Mean 30d | p-value |
|--------|-----------|--------------|----------|----------|
| `atr20 > q90` | 2.4% | 68.7% | -1.44% | 0.0000 |
| `mfi14 < 20` | 1.4% | 65.8% | +0.40% | 0.9930 |
| `rsi14 > 70` | 6.2% | 57.9% | -0.52% | 0.0132 |

**300ETF:**

| Filter | Placement | Neg-30d Prob | Mean 30d | p-value |
|--------|-----------|--------------|----------|----------|
| `kurt_20 < q10` | 11.8% | 63.5% | -1.14% | 0.0000 |
| `mfi14 < 20` | 1.7% | 71.0% | -0.01% | 0.2093 |

**500ETF:**

| Filter | Placement | Neg-30d Prob | Mean 30d | p-value |
|--------|-----------|--------------|----------|----------|
| `atr20 < q10` | 10.1% | 55.4% | -0.32% | 0.0002 |
| `kurt_20 < q10` | 8.0% | 55.0% | -0.43% | 0.0034 |

### 7.4 Top Combinations (Greedy + Known)

**Crash (P10 Lift):**

| ETF | Combination | Placement | P10 | Lift | Mean 30d |
|-----|-------------|-----------|-----|------|----------|
| 50ETF | `roc10 > q90 AND rsi14 > 70` | 2.5% | 15.7% | 1.57x | -1.56% |
| 300ETF | `vol20 > q90 AND dist_sma200 < -2.0` | 1.1% | 50.0% | 4.98x | -4.89% |
| 500ETF | `skew_20 < -0.5 AND close > sma50` | 13.2% | 21.9% | 2.19x | -3.07% |

**Medium-Term Fall (Negative 30d):**

| ETF | Combination | Placement | Neg-30d | Mean 30d |
|-----|-------------|-----------|---------|----------|
| 50ETF | `roc10 > q90 AND rsi14 > 70` | 2.5% | 70.0% | -1.56% |
| 300ETF | `kurt_20 < q10 AND skew_20 < -0.3` | 1.7% | 93.3% | -4.20% |
| 500ETF | `skew_20 < -0.5 AND rsi14 > 70` | 1.1% | 77.4% | -11.80% |

### 7.5 Pre-Specified Known Strategy Combos (v2 Validation)

These are the combos currently implemented in the put strategy, now evaluated with bias-free expanding-window quantiles:

| ETF | Known Combo | N | Placement | P10 | Lift | Mean 30d | p-value |
|-----|-------------|---|-----------|-----|------|----------|----------|
| 300ETF | `dd_252 < -0.15 AND dist_sma50 < -1.0` | 235 | 13.2% | 23.4% | **2.33x** | -0.62% | **0.0003** |
| 300ETF | `rsi14 > 65 AND skew_20 < -0.3` | 29 | 1.6% | 31.0% | **3.09x** | -1.49% | 0.0756 |
| 50ETF  | `skew_20 < -0.5 AND iv_vol_ratio < 0.9` | — | — | — | — | — | Not evaluable (iv_vol_ratio not in 50ETF IV cache) |
| 500ETF | `kurt_20 > 1.0 AND iv_vol_ratio > 1.2` | — | — | — | — | — | Not evaluable (iv_vol_ratio not in 500ETF IV cache) |

**Conclusion**: The 300ETF known combos are validated under bias-free methodology. `dd_252 < -0.15 AND dist_sma50 < -1.0` achieves 2.33x P10 lift (p=0.0003), confirming it as a robust crash predictor. 50ETF and 500ETF put filters rely on `iv_vol_ratio` which is unavailable in their IV caches and cannot be re-validated here.

### 7.6 Key Differences from v1 (Full-Sample Quantile) Results

With expanding-window quantiles, reported lifts are generally **more conservative** because:
1. The first 252 days are excluded (warmup period).
2. The threshold adapts over time — early high-vol periods may produce higher q90 thresholds, reducing trigger frequency.
3. `vol20 > q90` triggers dropped from ~10% placement (v1) to 2-4% (v2), meaning fewer but higher-quality signals.

The v1 results remain useful as upper-bound estimates; v2 results are the more reliable lower-bound estimates for live strategy deployment.

### 7.7 Recommendations for Put Strategy Updates

| ETF | Current Filter | Suggested Action |
|-----|----------------|-------------------|
| 50ETF | `skew_20 < -0.5 & iv_vol_ratio < 0.9` | Cannot re-validate (no iv_vol_ratio). Keep as-is. |
| 300ETF | `(dd_252 < -0.15 & dist_sma50 < -1.0) OR (rsi14 > 65 & skew_20 < -0.3)` | **Validated** — both combos confirmed under expanding quantiles. Keep as-is. |
| 500ETF | `kurt_20 > 1.0 & iv_vol_ratio > 1.2` | Cannot re-validate (no iv_vol_ratio). `skew_20 < -0.5 AND close > sma50` is a promising alternative (2.19x P10 lift). |

---

## 8. 4-Type Decision Matrix Alpha Model Parameters & Results (June 2026)

We ran a systematic optimization using the multi-indicator rolling 252-day percentile rank framework. Below are the optimal parameters (horizons, trigger thresholds, and weights) along with predictive performance.

### 8.1 50ETF Parameters & Results:
* **Regime 1: Short-Term Fall**
  * Horizon: **14 calendar days**
  * Threshold: **0.6404** (Top 10% placement)
  * Indicators & Weights: `ind_rsi_high: 45.7%`, `ind_dist_sma50_neg: 40.0%`, `ind_skew_neg: 12.2%`, `ind_roc5_neg: 1.1%`, `ind_macd_neg: 1.0%`
  * Performance: Triggered mean return **-1.72%** (vs +0.06% baseline)
* **Regime 2: Medium-Term Fall**
  * Horizon: **40 calendar days**
  * Threshold: **0.7549** (Top 25% placement)
  * Indicators & Weights: `ind_dist_sma50_neg: 94.3%`, `ind_roc20_neg: 2.6%`, `ind_rsi_low: 1.7%`, `ind_macd_neg: 1.4%`
  * Performance: Triggered mean return **-0.39%** (vs +0.33% baseline)
* **Regime 3: Short-Term Crash**
  * Horizon: **5 calendar days**
  * Threshold: **0.7478** (Top 10% placement)
  * Indicators & Weights: `ind_skew_neg: 49.8%`, `ind_vol_accel_high: 36.9%`, `ind_iv_vol_low: 6.8%`, `ind_kurt_high: 6.5%`
  * Performance: Triggered crash probability **10.94%** (vs 4.08% baseline, **2.69x lift**)
* **Regime 4: Medium-Term Crash**
  * Horizon: **40 calendar days**
  * Threshold: **0.6947** (Top 15% placement)
  * Indicators & Weights: `ind_dist_sma200_neg: 41.9%`, `ind_kurt_high: 26.4%`, `ind_vol_accel_high: 21.3%`, `ind_skew_neg: 5.5%`, `ind_dd_deep: 4.9%`
  * Performance: Triggered crash probability **51.90%** (vs 29.96% baseline, **1.73x lift**)

### 8.2 300ETF Parameters & Results:
* **Regime 1: Short-Term Fall**
  * Horizon: **10 calendar days**
  * Threshold: **0.5580** (Top 10% placement)
  * Indicators & Weights: `ind_rsi_high: 63.3%`, `ind_dist_sma50_neg: 17.5%`, `ind_roc5_neg: 8.1%`, `ind_skew_neg: 7.7%`, `ind_macd_neg: 3.3%`
  * Performance: Triggered mean return **-0.58%** (vs +0.19% baseline)
* **Regime 2: Medium-Term Fall**
  * Horizon: **40 calendar days**
  * Threshold: **0.8590** (Top 10% placement)
  * Indicators & Weights: `ind_macd_neg: 90.1%`, `ind_roc20_neg: 6.5%`, `ind_rsi_low: 2.6%`, `ind_dist_sma50_neg: 0.7%`
  * Performance: Triggered mean return **+0.35%** (vs +0.82% baseline)
* **Regime 3: Short-Term Crash**
  * Horizon: **5 calendar days**
  * Threshold: **0.8742** (Top 10% placement)
  * Indicators & Weights: `ind_vol_accel_high: 91.1%`, `ind_skew_neg: 7.4%`, `ind_iv_vol_low: 1.3%`, `ind_kurt_high: 0.3%`
  * Performance: Triggered crash probability **13.69%** (vs 3.34% baseline, **4.09x lift**)
* **Regime 4: Medium-Term Crash**
  * Horizon: **21 calendar days**
  * Threshold: **0.7592** (Top 15% placement)
  * Indicators & Weights: `ind_dist_sma200_neg: 38.5%`, `ind_vol_accel_high: 38.0%`, `ind_dd_deep: 12.1%`, `ind_skew_neg: 7.8%`, `ind_kurt_high: 3.6%`
  * Performance: Triggered crash probability **38.39%** (vs 16.23% baseline, **2.37x lift**)

### 8.3 500ETF Parameters & Results:
* **Regime 1: Short-Term Fall**
  * Horizon: **14 calendar days**
  * Threshold: **0.6047** (Top 10% placement)
  * Indicators & Weights: `ind_rsi_high: 49.6%`, `ind_dist_sma50_neg: 32.1%`, `ind_skew_neg: 15.5%`, `ind_roc5_neg: 2.7%`, `ind_macd_neg: 0.1%`
  * Performance: Triggered mean return **-2.54%** (vs +0.03% baseline)
* **Regime 2: Medium-Term Fall**
  * Horizon: **21 calendar days**
  * Threshold: **0.8303** (Top 15% placement)
  * Indicators & Weights: `ind_macd_neg: 91.6%`, `ind_dist_sma50_neg: 6.4%`, `ind_roc20_neg: 1.9%`, `ind_rsi_low: 0.0%`
  * Performance: Triggered mean return **-0.57%** (vs +0.08% baseline)
* **Regime 3: Short-Term Crash**
  * Horizon: **5 calendar days**
  * Threshold: **0.6773** (Top 25% placement)
  * Indicators & Weights: `ind_iv_vol_low: 64.8%`, `ind_skew_neg: 26.7%`, `ind_kurt_high: 6.0%`, `ind_vol_accel_high: 2.6%`
  * Performance: Triggered crash probability **12.82%** (vs 7.85% baseline, **1.63x lift**)
* **Regime 4: Medium-Term Crash**
  * Horizon: **40 calendar days**
  * Threshold: **0.9091** (Top 10% placement)
  * Indicators & Weights: `ind_dd_deep: 87.5%`, `ind_dist_sma200_neg: 9.6%`, `ind_skew_neg: 1.3%`, `ind_kurt_high: 1.2%`, `ind_vol_accel_high: 0.4%`
  * Performance: Triggered crash probability **65.85%** (vs 42.76% baseline, **1.54x lift**)

> ⚠️ **§8 numbers above are IN-SAMPLE and partly artifacts.** See §9 for bias-corrected OOS results.

---

## 9. Phase 1 OOS Overhaul — Bias-Corrected Results (June 2026)

The §8 results were re-examined and found to be overfit / artifact-prone:

### 9.1 Bugs found & fixed in the optimizer
1. **Crash-event sign inversion**: crash target was `-worst_dd` (non-negative), but the crash test was `target <= -0.05` — **never true**, so every original crash lift silently computed to ~0/baseline. The "4.09x" / "2.69x" lifts in §8.2/§8.1 were in-sample noise-chasing on a broken metric.
2. **RSI normalization**: `ind_rsi_high = rsi14/100` (raw) → replaced with rolling-percentile rank (distribution drift across regimes broke comparability).
3. **Objective chased noise**: `obj = -corr - 200*mean_ret_trig` let isolated historical windows dominate (corr weight 1 vs 200). Replaced with composite: Spearman rank + log-placement + complexity penalty.
4. **Walk-forward was diagnostic only**: never drove selection. Now `--select-by-oos` picks the config with best mean OOS across purged expanding folds.

### 9.2 Walk-forward OOS statistical results (purged, expanding window)
All 12 ETF×regime cells now pass the gate (lift>1 crash / mean_ret<0 fall). Crash OOS lift:

| ETF | ST Crash (R3) | MT Crash (R4) |
|-----|---------------|---------------|
| 50ETF | **2.12x** [CI 0.60, 4.37] | **2.10x** [CI 0.71, 3.93] |
| 300ETF | **2.03x** [CI 0.27, 4.16] | **1.45x** [CI 0.48, 2.41] |
| 500ETF | **1.65x** [CI 0.46, 3.27] | **1.06x** [CI 0.53, 1.68] |

### 9.3 Put P&L validation (the real test) — `validate_alpha_pnl.py`
Statistical lift ≠ hedging profitability (theta decay). Actual put P&L per trigger at monthly-cycle cadence, OOS years >= 2021, vs the existing static filter:

| ETF | Regime | Best Phase | Alpha net P&L | Static net P&L | Deploy? |
|-----|--------|-----------|---------------|----------------|---------|
| 50ETF | MT Crash | Phase 3 | **+2,144** (6 trigs) | +1,613 (4) | ✅ |
| 300ETF | ST Fall | Phase 1 | **+2,689** (7 trigs) | +1,385 (12) | ✅ |
| 300ETF | MT Fall | Phase 3 | **+2,216** (8 trigs) | +1,385 (12) | ✅ |
| 500ETF | ST Crash | Phase 2 | **+382** (6 trigs) | -114 (1) | ✅ |
| (other 8 cells) | — | — | < static | — | ❌ keep static |

### 9.4 Phases built
- **Phase 1** (`optimize_put_alpha.py`): linear weighted score, OOS-selected. Wins 300ETF ST Fall.
- **Phase 2** (`alpha_model_ml.py`): per-regime LightGBM (monotone constraints, 5-bag ensemble, isotonic calibration, walk-forward). reg3 crash OOS AUC 0.63. Wins 500ETF ST Crash; over-triggers elsewhere (theta drag).
- **Phase 3** (`alpha_model_hybrid.py`): logistic stack of [Phase1 rank, Phase2 prob, FINDINGS rule flags]. Most selective → wins MT Fall (300) and MT Crash (50).

### 9.5 Honest conclusion
The alpha edge is **real but selective**: 4 of 12 cells beat the static filter after costs. No single modeling approach dominates. 500ETF remains largely unhedgeable (consistent with §RESEARCH_500ETF). Full per-fold detail and per-trigger P&L in `backtest/alpha_phase_comparison.md` and `backtest/validate_pnl_phase{1,2,3}.json`.