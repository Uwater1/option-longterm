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
| 300ETF | single | 3 | 2 | 1 | 0 | 67% | 0.04 |
| 500ETF | single | 6 | 1 | 5 | 0 | 17% | 0.10 |
| 159915ETF | single | 3 | 0 | 3 | 0 | 0% | 0.25 |

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

**`max_up_ret`** (Lock IC=-0.0463, Sharpe=-2.3158)
- Yearly ICs: 2017: -0.040 | 2018: +0.136 | 2019: +0.049 | 2020: +0.048 | 2021: +0.166 | 2022: +0.013 | 2023: +0.149 | 2024: +0.056
- IC CV=0.94, Neg years=1/8, Half ratio=2.29, Recency ratio=2.13
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.064, Q3_mid=+0.014, Q4=+0.050, Q5_high_vol=+0.186

**`opening_drive_thrust_ratio`** (Lock IC=-0.0172, Sharpe=-1.4760)
- Yearly ICs: 2017: -0.039 | 2018: +0.176 | 2019: +0.078 | 2020: +0.042 | 2021: +0.170 | 2022: +0.024 | 2023: +0.166 | 2024: +0.033
- IC CV=0.93, Neg years=1/8, Half ratio=1.62, Recency ratio=1.45
- Regime ICs: Q1_low_vol=-0.010, Q2=+0.096, Q3_mid=+0.047, Q4=+0.058, Q5_high_vol=+0.212

### 500ETF — `single` False Positives

**`early_order_flow_imbalance`** (Lock IC=-0.0041, Sharpe=-2.4279)
- Yearly ICs: 2017: +0.093 | 2018: +0.101 | 2019: +0.121 | 2020: +0.038 | 2021: +0.122 | 2022: +0.141 | 2023: +0.079 | 2024: +0.107
- IC CV=0.29, Neg years=0/8, Half ratio=1.40, Recency ratio=0.96
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.072, Q3_mid=+0.065, Q4=+0.113, Q5_high_vol=+0.095

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`first_bar_return`** (Lock IC=+0.0007, Sharpe=-1.2814)
- Yearly ICs: 2017: +0.061 | 2018: +0.191 | 2019: +0.095 | 2020: +0.014 | 2021: +0.121 | 2022: +0.040 | 2023: +0.142 | 2024: +0.029
- IC CV=0.67, Neg years=0/8, Half ratio=0.93, Recency ratio=0.68
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.091, Q3_mid=+0.045, Q4=+0.070, Q5_high_vol=+0.164

### 500ETF — `single` Median Features

**`volatility_expansion_trend_vector`** (Lock IC=+0.0564, Sharpe=-1.6519)
- Yearly ICs: 2017: +0.201 | 2018: +0.129 | 2019: +0.076 | 2020: +0.097 | 2021: +0.073 | 2022: +0.093 | 2023: +0.089 | 2024: +0.123
- IC CV=0.36, Neg years=0/8, Half ratio=0.89, Recency ratio=0.64
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.015, Q3_mid=+0.111, Q4=+0.090, Q5_high_vol=+0.124

**`num_up_bars`** (Lock IC=+0.0459, Sharpe=-1.5665)
- Yearly ICs: 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141
- IC CV=0.40, Neg years=0/8, Half ratio=1.47, Recency ratio=1.31
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.054, Q3_mid=+0.097, Q4=+0.105, Q5_high_vol=+0.089

**`first_bar_return`** (Lock IC=+0.0404, Sharpe=-0.7263)
- Yearly ICs: 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107
- IC CV=0.46, Neg years=0/8, Half ratio=0.55, Recency ratio=0.43
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.027, Q3_mid=+0.096, Q4=+0.144, Q5_high_vol=+0.166

**`vwap_close_divergence_trend`** (Lock IC=+0.0323, Sharpe=-0.6894)
- Yearly ICs: 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107 | 2024: +0.092
- IC CV=0.38, Neg years=0/8, Half ratio=1.19, Recency ratio=0.83
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.058, Q3_mid=+0.094, Q4=+0.045, Q5_high_vol=+0.084

**`max_up_ret`** (Lock IC=+0.0308, Sharpe=-2.1159)
- Yearly ICs: 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143
- IC CV=0.28, Neg years=0/8, Half ratio=0.90, Recency ratio=0.61
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.016, Q3_mid=+0.113, Q4=+0.122, Q5_high_vol=+0.206

### 159915ETF — `single` Median Features

**`bar_body_rng_0`** (Lock IC=+0.0977, Sharpe=-0.3725)
- Yearly ICs: 2017: -0.020 | 2018: +0.141 | 2019: +0.203 | 2020: +0.134 | 2021: +0.136 | 2022: +0.062 | 2023: +0.141 | 2024: +0.047
- IC CV=0.63, Neg years=1/8, Half ratio=0.99, Recency ratio=1.55
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.083, Q3_mid=+0.074, Q4=+0.084, Q5_high_vol=+0.154

**`opening_drive_thrust_ratio`** (Lock IC=+0.0792, Sharpe=-0.1046)
- Yearly ICs: 2017: +0.030 | 2018: +0.088 | 2019: +0.188 | 2020: +0.095 | 2021: +0.133 | 2022: +0.085 | 2023: +0.199 | 2024: +0.100
- IC CV=0.46, Neg years=0/8, Half ratio=1.44, Recency ratio=2.54
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.087, Q3_mid=+0.131, Q4=+0.097, Q5_high_vol=+0.133

**`max_up_ret`** (Lock IC=+0.0682, Sharpe=-0.9705)
- Yearly ICs: 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074
- IC CV=0.39, Neg years=0/8, Half ratio=1.68, Recency ratio=2.15
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.098, Q3_mid=+0.115, Q4=+0.089, Q5_high_vol=+0.126

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | FP | fast | +0.0693 | -0.1510 | -0.1510 | 1y |
| `first_bar_return` | Median | fast | +0.0554 | -0.0827 | -0.0827 | 1y |
| `max_up_ret` | FP | fast | +0.0327 | -0.1524 | -0.1524 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=3, gradual=0, persistent=0

**FP decay trajectories:**

- `max_up_ret`: Y1:+0.033 → Y2:-0.152
- `opening_drive_thrust_ratio`: Y1:+0.069 → Y2:-0.151

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `volatility_expansion_trend_vector` | Median | fast | +0.1545 | -0.0850 | -0.0850 | 1y |
| `vwap_close_divergence_trend` | Median | fast | +0.1327 | -0.0940 | -0.0940 | 1y |
| `num_up_bars` | Median | fast | +0.1166 | -0.0474 | -0.0474 | 1y |
| `first_bar_return` | Median | fast | +0.0924 | -0.0114 | -0.0114 | 1y |
| `early_order_flow_imbalance` | FP | fast | +0.0913 | -0.1345 | -0.1345 | 1y |
| `max_up_ret` | Median | fast | +0.0801 | -0.0291 | -0.0291 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=6, gradual=0, persistent=0

**FP decay trajectories:**

- `early_order_flow_imbalance`: Y1:+0.091 → Y2:-0.135

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `opening_drive_thrust_ratio` | Median | fast | +0.1663 | -0.0464 | -0.0464 | 1y |
| `max_up_ret` | Median | fast | +0.1636 | -0.0753 | -0.0753 | 1y |
| `bar_body_rng_0` | Median | persistent | +0.1580 | +0.0207 | +0.0207 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=2, gradual=0, persistent=1

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 2/20 top rejects are profitable (10%)

- `limit_down_proximity_early`: Train IC=+0.0992, Lock IC=+0.0932, Sharpe=+0.2652
- `rbreaker_buy_setup_proximity_early`: Train IC=+0.0992, Lock IC=+0.0932, Sharpe=+0.2652

### 500ETF — `single`

**7-Year Jackknife**: 1/20 top rejects are profitable (5%)

- `rbreaker_sell_setup_proximity_early`: Train IC=+0.1293, Lock IC=+0.1243, Sharpe=+0.3509

**B2 Rolling Guard**: 3/20 top rejects are profitable (15%)

- `double_bottom_bull_flag_early`: Train IC=+0.0827, Lock IC=+0.0586, Sharpe=+0.6526
- `vix_iv_ratio`: Train IC=+0.0665, Lock IC=+0.0599, Sharpe=+0.3749
- `iv_diff_1d`: Train IC=+0.0902, Lock IC=+0.0868, Sharpe=+0.1562

### 159915ETF — `single`

**7-Year Jackknife**: 11/20 top rejects are profitable (55%)

- `volume_surge_direction`: Train IC=+0.1270, Lock IC=+0.1223, Sharpe=+1.0579
- `yesterday_afternoon_momentum`: Train IC=+0.1273, Lock IC=+0.0912, Sharpe=+0.9937
- `max_down_ret`: Train IC=+0.1243, Lock IC=+0.0913, Sharpe=+0.7609

**B2 Rolling Guard**: 4/20 top rejects are profitable (20%)

- `vol_ratio_10_60`: Train IC=+0.0509, Lock IC=+0.0521, Sharpe=+0.9211
- `keltner_squeeze_width`: Train IC=+0.0808, Lock IC=+0.0365, Sharpe=+0.8477
- `option_oi_growth`: Train IC=+0.0484, Lock IC=+0.0507, Sharpe=+0.6472

**B3 Composite Floor**: 1/6 top rejects are profitable (17%)

- `volatility_expansion_trend_vector`: Train IC=+0.1817, Lock IC=+0.0926, Sharpe=+0.0096

**B4 Correlation Gate**: 2/2 top rejects are profitable (100%)

- `first_bar_return`: Train IC=+0.1526, Lock IC=+0.0748, Sharpe=+0.4370
- `bar_ret_0`: Train IC=+0.1526, Lock IC=+0.0748, Sharpe=+0.4370

---

## 7. Root Cause Synthesis & Training-Only Fixes

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

_No combo features with sufficient data for primitive analysis._

---

## 9. Operator Class FP Rate


