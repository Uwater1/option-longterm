# Filter Pipeline Deep Diagnosis

**Purpose**: Understand WHY admission gates fail, using only training-period signals.
Lockbox is used solely for labeling TP/FP — all proposed fixes are training-only.

---

## 1. FP / Median / TP Summary

**TP** = Lock IC > 0 AND Sharpe > 0 (profitable standalone).  
**Median** = Lock IC > 0, Sharpe ≤ 0 (usable signal, contributes to IC-weighted ensemble).  
**FP** = Lock IC ≤ 0 (no predictive power, harmful).

**Decay multiplier** (assumes annual retraining): persistent=1.0, gradual=0.75, fast=0.25, immediate=0.0.  
**Prod Score** = mean(tier_score × decay_mult) where TP=1.0, Median=0.5, FP=0.0.

| ETF | Side | Admitted | FP | Median | TP | FP Rate | Prod Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 3 | 1 | 2 | 0 | 33% | 0.25 |
| 500ETF | single | 6 | 0 | 4 | 2 | 0% | 0.54 |
| 159915ETF | single | 1 | 0 | 1 | 0 | 0% | 0.38 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`max_up_ret`** (Lock IC=-0.0047, Sharpe=-0.0381)
- Yearly ICs: 2016: +0.084 | 2017: -0.040 | 2018: +0.136 | 2019: +0.049 | 2020: +0.048 | 2021: +0.166 | 2022: +0.013 | 2023: +0.149
- IC CV=0.89, Neg years=1/8, Half ratio=1.65, Recency ratio=3.65
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.073, Q3_mid=+0.045, Q4=+0.045, Q5_high_vol=+0.168

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`bar_body_rng_0`** (Lock IC=+0.0301, Sharpe=-0.6404)
- Yearly ICs: 2016: +0.107 | 2017: +0.047 | 2018: +0.192 | 2019: +0.077 | 2020: -0.009 | 2021: +0.155 | 2022: +0.035 | 2023: +0.153
- IC CV=0.68, Neg years=1/8, Half ratio=0.73, Recency ratio=1.22
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.073, Q3_mid=+0.082, Q4=+0.057, Q5_high_vol=+0.157

**`opening_drive_thrust_ratio`** (Lock IC=+0.0060, Sharpe=-1.0115)
- Yearly ICs: 2016: +0.086 | 2017: -0.039 | 2018: +0.176 | 2019: +0.078 | 2020: +0.042 | 2021: +0.170 | 2022: +0.024 | 2023: +0.166
- IC CV=0.83, Neg years=1/8, Half ratio=1.21, Recency ratio=4.07
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.097, Q3_mid=+0.086, Q4=+0.032, Q5_high_vol=+0.209

### 500ETF — `single` Median Features

**`close_vs_open_range`** (Lock IC=+0.0899, Sharpe=-0.2362)
- Yearly ICs: 2016: +0.070 | 2017: +0.191 | 2018: +0.104 | 2019: +0.055 | 2020: +0.104 | 2021: +0.061 | 2022: +0.086 | 2023: +0.085
- IC CV=0.42, Neg years=0/8, Half ratio=0.85, Recency ratio=0.66
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.030, Q3_mid=+0.100, Q4=+0.081, Q5_high_vol=+0.131

**`net_volume_flow`** (Lock IC=+0.0879, Sharpe=-0.0343)
- Yearly ICs: 2016: +0.063 | 2017: +0.165 | 2018: +0.154 | 2019: +0.088 | 2020: +0.107 | 2021: +0.085 | 2022: +0.104 | 2023: +0.088
- IC CV=0.31, Neg years=0/8, Half ratio=0.80, Recency ratio=0.85
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.020, Q3_mid=+0.107, Q4=+0.130, Q5_high_vol=+0.132

**`max_up_ret`** (Lock IC=+0.0813, Sharpe=-0.0733)
- Yearly ICs: 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104
- IC CV=0.30, Neg years=0/8, Half ratio=0.93, Recency ratio=0.64
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.009, Q3_mid=+0.112, Q4=+0.124, Q5_high_vol=+0.222

**`vwap_close_divergence_trend`** (Lock IC=+0.0582, Sharpe=-0.5326)
- Yearly ICs: 2016: +0.023 | 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107
- IC CV=0.50, Neg years=0/8, Half ratio=1.21, Recency ratio=0.97
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.016, Q3_mid=+0.092, Q4=+0.055, Q5_high_vol=+0.119

### 159915ETF — `single` Median Features

**`max_up_ret`** (Lock IC=+0.0765, Sharpe=-0.0485)
- Yearly ICs: 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175
- IC CV=0.38, Neg years=0/8, Half ratio=2.01, Recency ratio=2.24
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.126, Q3_mid=+0.106, Q4=+0.097, Q5_high_vol=+0.158

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`first_bar_return`** (Lock IC=+0.0686, Sharpe=+0.0195)
- Yearly ICs: 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062
- IC CV=0.46, Neg years=0/8, Half ratio=0.47, Recency ratio=0.47

**`opening_drive_thrust_ratio`** (Lock IC=+0.0962, Sharpe=+0.0157)
- Yearly ICs: 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102
- IC CV=0.40, Neg years=0/8, Half ratio=0.76, Recency ratio=0.57

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `max_up_ret` | FP | gradual | +0.0557 | +0.0327 | -0.1524 | 2y |
| `bar_body_rng_0` | Median | gradual | +0.0410 | +0.0721 | -0.0623 | 2y |
| `opening_drive_thrust_ratio` | Median | gradual | +0.0331 | +0.0693 | -0.1510 | 2y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=3, persistent=0

**FP decay trajectories:**

- `max_up_ret`: Y1:+0.056 → Y2:+0.033 → Y3:-0.152

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | TP | persistent | +0.1521 | +0.0877 | +0.0025 | 2y |
| `max_up_ret` | Median | gradual | +0.1427 | +0.0801 | -0.0291 | 2y |
| `net_volume_flow` | Median | gradual | +0.1322 | +0.1312 | -0.0580 | 2y |
| `close_vs_open_range` | Median | gradual | +0.1265 | +0.1509 | -0.0701 | 2y |
| `first_bar_return` | TP | gradual | +0.1067 | +0.0924 | -0.0114 | 2y |
| `vwap_close_divergence_trend` | Median | gradual | +0.0918 | +0.1327 | -0.0940 | 2y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=5, persistent=1

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `max_up_ret` | Median | gradual | +0.0739 | +0.1636 | -0.0753 | 2y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=1, persistent=0

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 4/20 top rejects are profitable (20%)

- `volume_surge_direction`: Train IC=+0.0916, Lock IC=+0.0184, Sharpe=+0.5209
- `yesterday_lunch_gap`: Train IC=+0.0939, Lock IC=+0.1015, Sharpe=+0.3427
- `star50_limit_proximity_early`: Train IC=+0.1111, Lock IC=+0.0658, Sharpe=+0.0841

**B3 Composite Floor**: 2/5 top rejects are profitable (40%)

- `first_bar_return`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.1226
- `bar_ret_0`: Train IC=+0.1429, Lock IC=+0.0107, Sharpe=+0.1226

### 500ETF — `single`

**7-Year Jackknife**: 6/20 top rejects are profitable (30%)

- `volume_surge_direction`: Train IC=+0.1196, Lock IC=+0.0758, Sharpe=+0.9137
- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1661, Lock IC=+0.1196, Sharpe=+0.3997
- `yesterday_early_vwap_dev`: Train IC=+0.1282, Lock IC=+0.0585, Sharpe=+0.2202

**B2 Rolling Guard**: 7/20 top rejects are profitable (35%)

- `iv_diff_1d`: Train IC=+0.0776, Lock IC=+0.0677, Sharpe=+0.7137
- `vix`: Train IC=+0.0841, Lock IC=+0.0426, Sharpe=+0.6645
- `iv`: Train IC=+0.1352, Lock IC=+0.0577, Sharpe=+0.6249

**BH-FDR Gate**: 1/12 top rejects are profitable (8%)

- `vol_ratio_10_60`: Train IC=+0.0761, Lock IC=+0.0275, Sharpe=+0.2531

**B3 Composite Floor**: 3/13 top rejects are profitable (23%)

- `morning_volume_weighted_momentum`: Train IC=+0.1465, Lock IC=+0.0778, Sharpe=+0.4041
- `max_down_ret`: Train IC=+0.1238, Lock IC=+0.0972, Sharpe=+0.0240
- `trend_bar_close_consistency`: Train IC=+0.1816, Lock IC=+0.0550, Sharpe=+0.0093

**B4 Correlation Gate**: 3/7 top rejects are profitable (43%)

- `first_30min_return`: Train IC=+0.1415, Lock IC=+0.0774, Sharpe=+0.2720
- `open_to_current_return`: Train IC=+0.1415, Lock IC=+0.0774, Sharpe=+0.2720
- `bar_ret_0`: Train IC=+0.1959, Lock IC=+0.0686, Sharpe=+0.0195

### 159915ETF — `single`

**7-Year Jackknife**: 11/20 top rejects are profitable (55%)

- `first_bar_sentiment`: Train IC=+0.1181, Lock IC=+0.0517, Sharpe=+0.7982
- `star50_limit_proximity_early`: Train IC=+0.1712, Lock IC=+0.1383, Sharpe=+0.4865
- `bar_body_rng_0`: Train IC=+0.1398, Lock IC=+0.0851, Sharpe=+0.4545

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `keltner_squeeze_width`: Train IC=+0.0922, Lock IC=+0.0586, Sharpe=+0.8035

**BH-FDR Gate**: 4/8 top rejects are profitable (50%)

- `close_vs_open_range`: Train IC=+0.1148, Lock IC=+0.1017, Sharpe=+0.3854
- `shaved_bar_trend_conviction`: Train IC=+0.1127, Lock IC=+0.0933, Sharpe=+0.1556
- `vol_gk20`: Train IC=+0.0370, Lock IC=+0.0210, Sharpe=+0.0601

**B3 Composite Floor**: 5/14 top rejects are profitable (36%)

- `first_bar_return`: Train IC=+0.1377, Lock IC=+0.0706, Sharpe=+0.5991
- `bar_ret_0`: Train IC=+0.1377, Lock IC=+0.0706, Sharpe=+0.5991
- `first_30min_return`: Train IC=+0.1313, Lock IC=+0.0981, Sharpe=+0.3030

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

_No combo features with sufficient data for primitive analysis._

---

## 9. Operator Class FP Rate


