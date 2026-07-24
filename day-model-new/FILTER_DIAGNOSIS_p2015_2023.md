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
| 300ETF | single | 2 | 0 | 2 | 0 | 0% | 0.44 |
| 500ETF | single | 7 | 0 | 3 | 4 | 0% | 0.62 |
| 159915ETF | single | 2 | 0 | 0 | 2 | 0% | 0.88 |

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

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`bar_body_rng_0`** (Lock IC=+0.0666, Sharpe=-0.0761)
- Yearly ICs: 2015: +0.100 | 2016: +0.107 | 2017: +0.047 | 2018: +0.192 | 2019: +0.077 | 2020: -0.009 | 2021: +0.155 | 2022: +0.035
- IC CV=0.69, Neg years=1/8, Half ratio=0.62, Recency ratio=0.91
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.066, Q3_mid=+0.080, Q4=+0.095, Q5_high_vol=+0.152

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0662, Sharpe=-0.3946)
- Yearly ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109
- IC CV=1.02, Neg years=1/8, Half ratio=0.66, Recency ratio=0.75
- Regime ICs: Q1_low_vol=-0.037, Q2=+0.017, Q3_mid=+0.018, Q4=+0.198, Q5_high_vol=+0.167

### 500ETF — `single` Median Features

**`opening_drive_thrust_ratio`** (Lock IC=+0.0993, Sharpe=-0.2306)
- Yearly ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069
- IC CV=0.42, Neg years=0/8, Half ratio=0.66, Recency ratio=0.63
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.048, Q3_mid=+0.189, Q4=+0.158, Q5_high_vol=+0.241

**`close_vs_open_range`** (Lock IC=+0.0899, Sharpe=-0.2788)
- Yearly ICs: 2015: +0.188 | 2016: +0.070 | 2017: +0.191 | 2018: +0.104 | 2019: +0.055 | 2020: +0.104 | 2021: +0.061 | 2022: +0.086
- IC CV=0.47, Neg years=0/8, Half ratio=0.58, Recency ratio=0.57
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.006, Q3_mid=+0.153, Q4=+0.117, Q5_high_vol=+0.109

**`max_down_ret`** (Lock IC=+0.0828, Sharpe=-0.1758)
- Yearly ICs: 2015: +0.281 | 2016: +0.052 | 2017: +0.240 | 2018: +0.131 | 2019: +0.112 | 2020: +0.138 | 2021: +0.064 | 2022: +0.057
- IC CV=0.60, Neg years=0/8, Half ratio=0.61, Recency ratio=0.36
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.018, Q3_mid=+0.162, Q4=+0.119, Q5_high_vol=+0.193

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 500ETF — `single` True Positives

**`first_bar_return`** (Lock IC=+0.0699, Sharpe=+0.1945)
- Yearly ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063
- IC CV=0.41, Neg years=0/8, Half ratio=0.52, Recency ratio=0.50

**`max_up_ret`** (Lock IC=+0.0920, Sharpe=+0.1044)
- Yearly ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095
- IC CV=0.33, Neg years=0/8, Half ratio=0.57, Recency ratio=0.66

**`volatility_expansion_trend_vector`** (Lock IC=+0.0894, Sharpe=+0.0972)
- Yearly ICs: 2015: +0.165 | 2016: +0.061 | 2017: +0.201 | 2018: +0.129 | 2019: +0.076 | 2020: +0.097 | 2021: +0.073 | 2022: +0.093
- IC CV=0.41, Neg years=0/8, Half ratio=0.62, Recency ratio=0.74

**`first_30min_return`** (Lock IC=+0.0851, Sharpe=+0.0010)
- Yearly ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094
- IC CV=0.40, Neg years=0/8, Half ratio=0.64, Recency ratio=0.90

### 159915ETF — `single` True Positives

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1309, Sharpe=+0.6647)
- Yearly ICs: 2015: +0.179 | 2016: +0.104 | 2017: -0.004 | 2018: +0.114 | 2019: +0.160 | 2020: +0.124 | 2021: +0.142 | 2022: +0.160
- IC CV=0.44, Neg years=1/8, Half ratio=1.18, Recency ratio=1.07

**`max_up_ret`** (Lock IC=+0.1014, Sharpe=+0.2773)
- Yearly ICs: 2015: +0.181 | 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116
- IC CV=0.39, Neg years=0/8, Half ratio=1.13, Recency ratio=1.08

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `bar_body_rng_0` | Median | gradual | +0.1535 | +0.0410 | -0.0623 | 1y |
| `rbreaker_sell_setup_proximity_early` | Median | persistent | +0.0576 | +0.0214 | +0.1515 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=1, persistent=1

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `max_up_ret` | TP | gradual | +0.1044 | +0.1427 | -0.0291 | 3y |
| `opening_drive_thrust_ratio` | Median | persistent | +0.1017 | +0.1521 | +0.0025 | 3y |
| `first_30min_return` | TP | gradual | +0.0954 | +0.1202 | -0.1128 | 3y |
| `volatility_expansion_trend_vector` | TP | gradual | +0.0889 | +0.1235 | -0.0850 | 3y |
| `close_vs_open_range` | Median | gradual | +0.0848 | +0.1265 | -0.0701 | 3y |
| `first_bar_return` | TP | gradual | +0.0618 | +0.1067 | -0.0114 | 3y |
| `max_down_ret` | Median | persistent | +0.0309 | +0.1149 | +0.0305 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=5, persistent=2

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `max_up_ret` | TP | gradual | +0.1753 | +0.0739 | -0.0753 | 1y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1181 | +0.0985 | +0.1637 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=1, persistent=1

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 3/20 top rejects are profitable (15%)

- `yesterday_lunch_gap`: Train IC=+0.1285, Lock IC=+0.0650, Sharpe=+0.4548
- `volume_surge_direction`: Train IC=+0.1031, Lock IC=+0.0498, Sharpe=+0.2960
- `close_location_in_range_3d`: Train IC=+0.0900, Lock IC=+0.0457, Sharpe=+0.2518

**B3 Composite Floor**: 1/4 top rejects are profitable (25%)

- `max_up_ret`: Train IC=+0.1676, Lock IC=+0.0460, Sharpe=+0.0930

### 500ETF — `single`

**7-Year Jackknife**: 4/20 top rejects are profitable (20%)

- `yesterday_early_vwap_dev`: Train IC=+0.1581, Lock IC=+0.0555, Sharpe=+0.3534
- `yesterday_early_momentum`: Train IC=+0.1455, Lock IC=+0.0434, Sharpe=+0.0930
- `star50_limit_proximity_early`: Train IC=+0.1953, Lock IC=+0.1184, Sharpe=+0.0205

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `iv`: Train IC=+0.0738, Lock IC=+0.0482, Sharpe=+0.5765
- `iv_diff_1d`: Train IC=+0.0355, Lock IC=+0.0707, Sharpe=+0.5676
- `iv_envelope_deviation`: Train IC=+0.0552, Lock IC=+0.0407, Sharpe=+0.4264

**BH-FDR Gate**: 1/4 top rejects are profitable (25%)

- `vol_ratio_10_60`: Train IC=+0.0962, Lock IC=+0.0274, Sharpe=+0.3927

**B3 Composite Floor**: 2/13 top rejects are profitable (15%)

- `morning_volume_weighted_momentum`: Train IC=+0.1578, Lock IC=+0.0856, Sharpe=+0.2563
- `trend_bar_close_consistency`: Train IC=+0.2230, Lock IC=+0.0642, Sharpe=+0.0032

**B4 Correlation Gate**: 2/6 top rejects are profitable (33%)

- `bar_ret_0`: Train IC=+0.1931, Lock IC=+0.0699, Sharpe=+0.1945
- `open_to_current_return`: Train IC=+0.1557, Lock IC=+0.0851, Sharpe=+0.0010

### 159915ETF — `single`

**7-Year Jackknife**: 12/20 top rejects are profitable (60%)

- `volume_surge_direction`: Train IC=+0.1127, Lock IC=+0.1108, Sharpe=+1.1372
- `morning_volume_weighted_momentum`: Train IC=+0.1002, Lock IC=+0.1119, Sharpe=+0.6047
- `trend_day_regime_conviction`: Train IC=+0.1107, Lock IC=+0.1116, Sharpe=+0.5538

**B2 Rolling Guard**: 9/20 top rejects are profitable (45%)

- `keltner_squeeze_width`: Train IC=+0.1380, Lock IC=+0.0640, Sharpe=+0.8000
- `first_bar_return`: Train IC=+0.1458, Lock IC=+0.0872, Sharpe=+0.6789
- `bar_ret_0`: Train IC=+0.1458, Lock IC=+0.0872, Sharpe=+0.6789

**BH-FDR Gate**: 2/4 top rejects are profitable (50%)

- `close_vs_open_range`: Train IC=+0.1106, Lock IC=+0.1197, Sharpe=+0.5916
- `shaved_bar_trend_conviction`: Train IC=+0.0990, Lock IC=+0.1148, Sharpe=+0.4006

**B3 Composite Floor**: 9/10 top rejects are profitable (90%)

- `opening_drive_thrust_ratio`: Train IC=+0.2418, Lock IC=+0.1176, Sharpe=+0.7695
- `volatility_expansion_trend_vector`: Train IC=+0.1531, Lock IC=+0.1157, Sharpe=+0.6581
- `star50_limit_proximity_early`: Train IC=+0.1849, Lock IC=+0.1286, Sharpe=+0.5989

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

_No combo features with sufficient data for primitive analysis._

---

## 9. Operator Class FP Rate


