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