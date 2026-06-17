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