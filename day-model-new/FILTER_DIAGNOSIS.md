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
| 300ETF | single | 16 | 2 | 5 | 9 | 12% | 0.60 |
| 500ETF | single | 20 | 0 | 2 | 18 | 0% | 0.78 |
| 159915ETF | single | 9 | 0 | 0 | 9 | 0% | 0.97 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=2, TP=9)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| n_negative_years | 2.000 | 0.778 | 2.000 | 1.000 | +4.16 | 1.500 | 100% |
| weak_link_cv | 0.809 | 1.260 | 0.809 | 1.219 | -4.10 | 1.460 | 70% |
| recency_ratio | 1.849 | 0.855 | 1.849 | 0.744 | +3.54 | 1.389 | 91% |
| n_negative_regimes | 2.000 | 0.556 | 2.000 | 0.000 | +2.98 | 1.500 | 91% |
| ic_cv | 1.006 | 0.800 | 1.006 | 0.793 | +1.91 | 0.934 | 91% |
| half_ratio | 1.532 | 1.164 | 1.532 | 1.076 | +1.46 | 1.365 | 82% |
| ic_std_across_regimes | 0.070 | 0.075 | 0.070 | 0.082 | -0.30 | 0.101 | 73% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_product__volume_weighted_momentum_acceleration__opening_drive_thrust_ratio`** (Lock IC=-0.0676, Sharpe=-1.0544)
- Admission: Train IC=+0.1992, Deflated=+0.2027, IR=0.66, Mono=0.70, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.062 | 2016: -0.021 | 2017: +0.101 | 2018: -0.008 | 2019: +0.097 | 2020: +0.014 | 2021: +0.070 | 2022: -0.129 | 2023: -0.061 | 2024: -0.013 | 2025: +0.025 | 2026: -0.210
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.186 | 2017: +0.190 | 2018: +0.089 | 2019: +0.148 | 2020: +0.166 | 2021: +0.394 | 2022: -0.075 | 2023: -0.043 | 2024: +0.277 | 2025: -0.053 | 2026: -0.493
- IC CV=1.02, Neg years (linear/tail)=2/0 of 7, Half ratio=1.59, Recency ratio=2.04
- Early IC=+0.0205, Recent IC=+0.0419, 1st-half IC=+0.0316, 2nd-half IC=+0.0503, Neg regimes=2/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.119, Q2=-0.050, Q3_mid=+0.105, Q4=-0.035, Q5_high_vol=+0.026

**`combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`** (Lock IC=-0.0562, Sharpe=-0.9430)
- Admission: Train IC=+0.2002, Deflated=+0.2033, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.18
- Yearly Linear ICs: 2015: +0.076 | 2016: -0.018 | 2017: +0.100 | 2018: -0.017 | 2019: +0.089 | 2020: +0.024 | 2021: +0.072 | 2022: -0.102 | 2023: -0.076 | 2024: +0.005 | 2025: +0.035 | 2026: -0.178
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.167 | 2017: +0.199 | 2018: +0.087 | 2019: +0.215 | 2020: +0.273 | 2021: +0.246 | 2022: -0.201 | 2023: -0.100 | 2024: +0.306 | 2025: -0.195 | 2026: -0.605
- IC CV=0.99, Neg years (linear/tail)=2/0 of 7, Half ratio=1.47, Recency ratio=1.66
- Early IC=+0.0290, Recent IC=+0.0481, 1st-half IC=+0.0357, 2nd-half IC=+0.0526, Neg regimes=2/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.81, neg years=1)
- Regime ICs: Q1_low_vol=+0.122, Q2=-0.051, Q3_mid=+0.108, Q4=-0.033, Q5_high_vol=+0.037

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0555, Sharpe=-0.0703)
- Admission: Train IC=+0.1981, Deflated=+0.1972, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.071 | 2017: +0.065 | 2018: +0.201 | 2019: +0.057 | 2020: -0.013 | 2021: +0.171 | 2022: +0.057 | 2023: +0.176 | 2024: +0.006 | 2025: +0.101 | 2026: -0.144
- Yearly Tail ICs:   2015: +0.115 | 2016: -0.049 | 2017: +0.157 | 2018: +0.513 | 2019: +0.165 | 2020: +0.183 | 2021: +0.364 | 2022: +0.216 | 2023: +0.221 | 2024: +0.070 | 2025: +0.171 | 2026: -0.299
- IC CV=0.72, Neg years (linear/tail)=1/1 of 7, Half ratio=1.16, Recency ratio=0.94
- Early IC=+0.0842, Recent IC=+0.0790, 1st-half IC=+0.0880, 2nd-half IC=+0.1017, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.058, Q3_mid=+0.129, Q4=+0.052, Q5_high_vol=+0.169

**`combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0529, Sharpe=-0.0513)
- Admission: Train IC=+0.2522, Deflated=+0.2513, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.078 | 2017: +0.004 | 2018: +0.216 | 2019: +0.086 | 2020: +0.020 | 2021: +0.161 | 2022: +0.034 | 2023: +0.163 | 2024: +0.053 | 2025: +0.041 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.063 | 2016: +0.097 | 2017: +0.160 | 2018: +0.357 | 2019: +0.345 | 2020: +0.115 | 2021: +0.475 | 2022: +0.089 | 2023: +0.260 | 2024: +0.191 | 2025: -0.080 | 2026: -0.004
- IC CV=0.74, Neg years (linear/tail)=0/0 of 7, Half ratio=1.51, Recency ratio=1.07
- Early IC=+0.0846, Recent IC=+0.0908, 1st-half IC=+0.0843, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.037, Q3_mid=+0.127, Q4=+0.148, Q5_high_vol=+0.169

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0430, Sharpe=-0.1812)
- Admission: Train IC=+0.1466, Deflated=+0.1457, IR=0.59, Mono=0.73, p=0.0058, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.076 | 2016: +0.034 | 2017: -0.050 | 2018: +0.114 | 2019: +0.086 | 2020: +0.032 | 2021: +0.170 | 2022: +0.016 | 2023: +0.173 | 2024: +0.026 | 2025: +0.012 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.136 | 2017: -0.036 | 2018: +0.199 | 2019: +0.293 | 2020: +0.101 | 2021: +0.421 | 2022: +0.234 | 2023: +0.203 | 2024: +0.120 | 2025: -0.101 | 2026: +0.030
- IC CV=0.98, Neg years (linear/tail)=1/1 of 7, Half ratio=2.19, Recency ratio=1.84
- Early IC=+0.0546, Recent IC=+0.1006, 1st-half IC=+0.0450, 2nd-half IC=+0.0985, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=-0.043, Q2=+0.089, Q3_mid=+0.140, Q4=+0.030, Q5_high_vol=+0.132

**`combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0426, Sharpe=-0.3432)
- Admission: Train IC=+0.1816, Deflated=+0.1799, IR=0.67, Mono=0.76, p=0.0006, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.087 | 2017: -0.034 | 2018: +0.174 | 2019: +0.091 | 2020: +0.046 | 2021: +0.165 | 2022: +0.025 | 2023: +0.157 | 2024: +0.033 | 2025: +0.055 | 2026: -0.184
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.226 | 2017: +0.015 | 2018: +0.309 | 2019: +0.111 | 2020: +0.093 | 2021: +0.431 | 2022: +0.175 | 2023: +0.139 | 2024: +0.161 | 2025: -0.073 | 2026: -0.389
- IC CV=0.75, Neg years (linear/tail)=1/0 of 7, Half ratio=2.05, Recency ratio=1.27
- Early IC=+0.0833, Recent IC=+0.1058, 1st-half IC=+0.0583, 2nd-half IC=+0.1194, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=-0.025, Q2=+0.021, Q3_mid=+0.096, Q4=+0.177, Q5_high_vol=+0.147

**`combo_ratio__first_bar_sentiment__volume_surge_direction`** (Lock IC=+0.0120, Sharpe=-0.8294)
- Admission: Train IC=+0.1277, Deflated=+0.1278, IR=0.63, Mono=0.75, p=0.0154, MaxCorr=0.06
- Yearly Linear ICs: 2015: +0.083 | 2016: +0.112 | 2017: +0.044 | 2018: +0.089 | 2019: +0.064 | 2020: -0.038 | 2021: +0.135 | 2022: +0.019 | 2023: +0.058 | 2024: -0.051 | 2025: +0.006 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.250 | 2017: -0.084 | 2018: +0.104 | 2019: +0.145 | 2020: +0.030 | 2021: +0.411 | 2022: +0.051 | 2023: -0.030 | 2024: +0.059 | 2025: -0.149 | 2026: -0.034
- IC CV=0.75, Neg years (linear/tail)=1/1 of 7, Half ratio=0.87, Recency ratio=0.50
- Early IC=+0.0977, Recent IC=+0.0485, 1st-half IC=+0.0764, 2nd-half IC=+0.0665, Neg regimes=1/5
- Weak component: `volume_surge_direction` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.088, Q2=-0.007, Q3_mid=+0.119, Q4=+0.059, Q5_high_vol=+0.111

### 500ETF — `single` Median Features

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0702, Sharpe=-0.0287)
- Admission: Train IC=+0.3274, Deflated=+0.3260, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.120 | 2017: +0.197 | 2018: +0.186 | 2019: +0.120 | 2020: +0.115 | 2021: +0.090 | 2022: +0.055 | 2023: +0.027 | 2024: +0.084 | 2025: +0.133 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.174 | 2017: +0.334 | 2018: +0.177 | 2019: +0.333 | 2020: +0.149 | 2021: +0.117 | 2022: +0.152 | 2023: -0.119 | 2024: +0.186 | 2025: +0.247 | 2026: -0.229
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.51
- Early IC=+0.2027, Recent IC=+0.1027, 1st-half IC=+0.1819, 2nd-half IC=+0.1313, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.018, Q3_mid=+0.169, Q4=+0.138, Q5_high_vol=+0.267

**`combo_ratio__max_down_ret__net_volume_flow`** (Lock IC=+0.0543, Sharpe=-0.4855)
- Admission: Train IC=+0.2240, Deflated=+0.2235, IR=0.85, Mono=0.79, p=0.0002, MaxCorr=0.09
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.129 | 2017: +0.220 | 2018: +0.140 | 2019: +0.125 | 2020: +0.135 | 2021: +0.004 | 2022: -0.056 | 2023: +0.007 | 2024: +0.084 | 2025: +0.166 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.355 | 2016: +0.225 | 2017: +0.296 | 2018: +0.169 | 2019: +0.110 | 2020: +0.294 | 2021: +0.250 | 2022: -0.197 | 2023: -0.187 | 2024: +0.121 | 2025: +0.191 | 2026: -0.073
- IC CV=0.47, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.42
- Early IC=+0.1662, Recent IC=+0.0693, 1st-half IC=+0.1599, 2nd-half IC=+0.1020, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.001, Q3_mid=+0.137, Q4=+0.092, Q5_high_vol=+0.174

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0561, Sharpe=+0.6987)
- Admission: Train IC=+0.2124, Deflated=+0.2111, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.054 | 2017: +0.002 | 2018: +0.172 | 2019: +0.051 | 2020: -0.003 | 2021: +0.179 | 2022: +0.056 | 2023: +0.192 | 2024: +0.025 | 2025: +0.114 | 2026: -0.181
- Yearly Tail ICs:   2015: +0.038 | 2016: +0.199 | 2017: +0.157 | 2018: +0.396 | 2019: +0.182 | 2020: +0.066 | 2021: +0.365 | 2022: +0.373 | 2023: +0.353 | 2024: +0.078 | 2025: +0.083 | 2026: +0.023
- IC CV=0.86, Neg years (linear/tail)=1/0 of 7, Half ratio=1.26, Recency ratio=1.03
- Early IC=+0.0855, Recent IC=+0.0880, 1st-half IC=+0.0792, 2nd-half IC=+0.0996, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.054, Q3_mid=+0.101, Q4=+0.092, Q5_high_vol=+0.178

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0763, Sharpe=+0.6530)
- Admission: Train IC=+0.2667, Deflated=+0.2669, IR=0.68, Mono=0.71, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.76, Neg years (linear/tail)=1/0 of 7, Half ratio=1.08, Recency ratio=0.63
- Early IC=+0.1384, Recent IC=+0.0875, 1st-half IC=+0.1186, 2nd-half IC=+0.1276, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.032, Q3_mid=+0.111, Q4=+0.190, Q5_high_vol=+0.217

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0602, Sharpe=+0.5551)
- Admission: Train IC=+0.2660, Deflated=+0.2658, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.075 | 2018: +0.166 | 2019: +0.085 | 2020: +0.075 | 2021: +0.151 | 2022: +0.095 | 2023: +0.091 | 2024: +0.027 | 2025: +0.042 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.223 | 2017: -0.036 | 2018: +0.422 | 2019: +0.218 | 2020: +0.178 | 2021: +0.408 | 2022: +0.272 | 2023: +0.144 | 2024: +0.208 | 2025: +0.115 | 2026: +0.191
- IC CV=0.82, Neg years (linear/tail)=1/1 of 7, Half ratio=1.02, Recency ratio=0.74
- Early IC=+0.1530, Recent IC=+0.1131, 1st-half IC=+0.1144, 2nd-half IC=+0.1172, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.053, Q2=+0.037, Q3_mid=+0.103, Q4=+0.200, Q5_high_vol=+0.197

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0650, Sharpe=+0.4659)
- Admission: Train IC=+0.2949, Deflated=+0.2950, IR=0.76, Mono=0.73, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.095 | 2017: +0.008 | 2018: +0.184 | 2019: +0.116 | 2020: +0.042 | 2021: +0.132 | 2022: +0.038 | 2023: +0.176 | 2024: +0.054 | 2025: +0.049 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.333 | 2016: +0.093 | 2017: +0.101 | 2018: +0.399 | 2019: +0.266 | 2020: +0.235 | 2021: +0.493 | 2022: +0.150 | 2023: +0.324 | 2024: +0.235 | 2025: -0.040 | 2026: +0.148
- IC CV=0.65, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.50
- Early IC=+0.1745, Recent IC=+0.0867, 1st-half IC=+0.1480, 2nd-half IC=+0.1193, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.027, Q3_mid=+0.113, Q4=+0.191, Q5_high_vol=+0.227

**`combo_ratio__limit_down_proximity_early__volume_concentration`** (Lock IC=+0.0537, Sharpe=+0.3623)
- Admission: Train IC=+0.1928, Deflated=+0.1935, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.017 | 2017: -0.009 | 2018: +0.112 | 2019: +0.068 | 2020: +0.001 | 2021: +0.130 | 2022: +0.096 | 2023: +0.023 | 2024: -0.052 | 2025: +0.076 | 2026: +0.197
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.203 | 2017: +0.113 | 2018: +0.268 | 2019: +0.174 | 2020: +0.304 | 2021: +0.283 | 2022: +0.225 | 2023: -0.082 | 2024: +0.218 | 2025: +0.014 | 2026: +0.361
- IC CV=0.88, Neg years (linear/tail)=1/0 of 7, Half ratio=1.82, Recency ratio=1.12
- Early IC=+0.0585, Recent IC=+0.0654, 1st-half IC=+0.0384, 2nd-half IC=+0.0698, Neg regimes=2/5
- Weak component: `limit_down_proximity_early` (CV=1.62)
- Regime ICs: Q1_low_vol=-0.027, Q2=-0.051, Q3_mid=+0.035, Q4=+0.145, Q5_high_vol=+0.115

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0728, Sharpe=+0.3499)
- Admission: Train IC=+0.2294, Deflated=+0.2299, IR=0.55, Mono=0.74, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109 | 2023: +0.058 | 2024: +0.021 | 2025: +0.045 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.260 | 2017: -0.063 | 2018: +0.287 | 2019: +0.204 | 2020: +0.254 | 2021: +0.174 | 2022: +0.239 | 2023: -0.083 | 2024: +0.166 | 2025: -0.078 | 2026: +0.337
- IC CV=1.14, Neg years (linear/tail)=1/1 of 7, Half ratio=0.62, Recency ratio=0.50
- Early IC=+0.1357, Recent IC=+0.0678, 1st-half IC=+0.1151, 2nd-half IC=+0.0718, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.067, Q2=+0.000, Q3_mid=+0.053, Q4=+0.178, Q5_high_vol=+0.171

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0534, Sharpe=+0.2178)
- Admission: Train IC=+0.2240, Deflated=+0.2229, IR=0.80, Mono=0.79, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.030 | 2017: +0.039 | 2018: +0.150 | 2019: +0.044 | 2020: +0.011 | 2021: +0.194 | 2022: +0.045 | 2023: +0.196 | 2024: +0.038 | 2025: +0.106 | 2026: -0.206
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.101 | 2017: +0.156 | 2018: +0.425 | 2019: +0.208 | 2020: +0.213 | 2021: +0.325 | 2022: +0.238 | 2023: +0.225 | 2024: +0.102 | 2025: +0.226 | 2026: -0.338
- IC CV=0.79, Neg years (linear/tail)=0/0 of 7, Half ratio=1.62, Recency ratio=1.67
- Early IC=+0.0614, Recent IC=+0.1023, 1st-half IC=+0.0643, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.047, Q3_mid=+0.077, Q4=+0.098, Q5_high_vol=+0.153

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0513, Sharpe=+0.2085)
- Admission: Train IC=+0.2874, Deflated=+0.2868, IR=0.82, Mono=0.81, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.088 | 2017: -0.043 | 2018: +0.214 | 2019: +0.118 | 2020: +0.070 | 2021: +0.175 | 2022: +0.011 | 2023: +0.139 | 2024: +0.066 | 2025: +0.034 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.144 | 2017: +0.077 | 2018: +0.394 | 2019: +0.368 | 2020: +0.168 | 2021: +0.502 | 2022: +0.240 | 2023: +0.115 | 2024: +0.335 | 2025: -0.047 | 2026: +0.050
- IC CV=0.73, Neg years (linear/tail)=1/0 of 7, Half ratio=1.06, Recency ratio=0.74
- Early IC=+0.1646, Recent IC=+0.1224, 1st-half IC=+0.1329, 2nd-half IC=+0.1409, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.024, Q2=+0.008, Q3_mid=+0.133, Q4=+0.240, Q5_high_vol=+0.212

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0472, Sharpe=+0.0580)
- Admission: Train IC=+0.1898, Deflated=+0.1897, IR=0.65, Mono=0.75, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156 | 2022: +0.028 | 2023: +0.137 | 2024: +0.039 | 2025: +0.058 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.055 | 2017: +0.207 | 2018: +0.385 | 2019: +0.133 | 2020: +0.033 | 2021: +0.203 | 2022: +0.122 | 2023: +0.108 | 2024: +0.061 | 2025: +0.105 | 2026: -0.330
- IC CV=0.58, Neg years (linear/tail)=1/0 of 7, Half ratio=1.19, Recency ratio=0.77
- Early IC=+0.1003, Recent IC=+0.0769, 1st-half IC=+0.0926, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.052, Q3_mid=+0.124, Q4=+0.091, Q5_high_vol=+0.162

### 500ETF — `single` True Positives

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.0928, Sharpe=+1.0646)
- Admission: Train IC=+0.2664, Deflated=+0.2657, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.091 | 2022: +0.051 | 2023: +0.067 | 2024: +0.098 | 2025: +0.035 | 2026: +0.240
- Yearly Tail ICs:   2015: +0.318 | 2016: -0.063 | 2017: +0.332 | 2018: +0.260 | 2019: +0.360 | 2020: +0.206 | 2021: +0.281 | 2022: -0.064 | 2023: +0.259 | 2024: +0.213 | 2025: -0.016 | 2026: +0.281
- IC CV=0.51, Neg years (linear/tail)=0/1 of 7, Half ratio=0.88, Recency ratio=0.75
- Early IC=+0.1578, Recent IC=+0.1187, 1st-half IC=+0.1709, 2nd-half IC=+0.1510, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.069, Q3_mid=+0.133, Q4=+0.104, Q5_high_vol=+0.298

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1040, Sharpe=+0.8783)
- Admission: Train IC=+0.2789, Deflated=+0.2783, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.073 | 2017: +0.226 | 2018: +0.079 | 2019: +0.082 | 2020: +0.119 | 2021: +0.089 | 2022: +0.032 | 2023: +0.095 | 2024: +0.142 | 2025: +0.138 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.208 | 2017: +0.338 | 2018: +0.282 | 2019: +0.119 | 2020: +0.215 | 2021: +0.215 | 2022: +0.160 | 2023: +0.008 | 2024: +0.221 | 2025: +0.089 | 2026: +0.313
- IC CV=0.49, Neg years (linear/tail)=0/0 of 7, Half ratio=0.57, Recency ratio=0.71
- Early IC=+0.1481, Recent IC=+0.1050, 1st-half IC=+0.1663, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.021, Q3_mid=+0.075, Q4=+0.159, Q5_high_vol=+0.166

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0972, Sharpe=+0.8261)
- Admission: Train IC=+0.2552, Deflated=+0.2542, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140 | 2022: +0.076 | 2023: +0.053 | 2024: +0.120 | 2025: +0.138 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.471 | 2016: +0.195 | 2017: +0.217 | 2018: +0.389 | 2019: -0.049 | 2020: +0.108 | 2021: +0.319 | 2022: +0.065 | 2023: +0.203 | 2024: +0.172 | 2025: +0.259 | 2026: +0.331
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.73, Recency ratio=0.66
- Early IC=+0.1934, Recent IC=+0.1275, 1st-half IC=+0.1821, 2nd-half IC=+0.1331, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.047, Q3_mid=+0.127, Q4=+0.189, Q5_high_vol=+0.255

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1231, Sharpe=+0.7781)
- Admission: Train IC=+0.2059, Deflated=+0.2050, IR=0.54, Mono=0.67, p=0.0006, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.049 | 2017: +0.197 | 2018: +0.137 | 2019: +0.171 | 2020: +0.117 | 2021: +0.085 | 2022: +0.063 | 2023: +0.095 | 2024: +0.154 | 2025: +0.121 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.029 | 2017: +0.149 | 2018: +0.211 | 2019: +0.461 | 2020: +0.261 | 2021: +0.230 | 2022: +0.173 | 2023: +0.060 | 2024: +0.225 | 2025: +0.057 | 2026: +0.339
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.85
- Early IC=+0.1182, Recent IC=+0.1008, 1st-half IC=+0.1531, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.064, Q3_mid=+0.083, Q4=+0.120, Q5_high_vol=+0.224

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0858, Sharpe=+0.7450)
- Admission: Train IC=+0.3327, Deflated=+0.3325, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.48
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172 | 2022: +0.052 | 2023: +0.095 | 2024: +0.153 | 2025: +0.057 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.208 | 2017: +0.327 | 2018: +0.611 | 2019: +0.275 | 2020: +0.129 | 2021: +0.238 | 2022: +0.147 | 2023: +0.148 | 2024: +0.202 | 2025: +0.099 | 2026: +0.012
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.99, Recency ratio=0.89
- Early IC=+0.1934, Recent IC=+0.1721, 1st-half IC=+0.2037, 2nd-half IC=+0.2016, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.128, Q3_mid=+0.198, Q4=+0.162, Q5_high_vol=+0.330

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.1014, Sharpe=+0.6742)
- Admission: Train IC=+0.2721, Deflated=+0.2709, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113 | 2022: +0.116 | 2023: +0.080 | 2024: +0.149 | 2025: +0.116 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.543 | 2016: +0.168 | 2017: +0.280 | 2018: +0.201 | 2019: +0.261 | 2020: +0.072 | 2021: +0.310 | 2022: +0.226 | 2023: +0.106 | 2024: +0.236 | 2025: +0.069 | 2026: -0.077
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.74
- Early IC=+0.1904, Recent IC=+0.1405, 1st-half IC=+0.1985, 2nd-half IC=+0.1446, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.053, Q3_mid=+0.145, Q4=+0.173, Q5_high_vol=+0.266

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1030, Sharpe=+0.6526)
- Admission: Train IC=+0.3278, Deflated=+0.3273, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.194 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148 | 2022: +0.067 | 2023: +0.066 | 2024: +0.124 | 2025: +0.091 | 2026: +0.173
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.050 | 2017: +0.172 | 2018: +0.350 | 2019: +0.480 | 2020: +0.209 | 2021: +0.281 | 2022: -0.024 | 2023: +0.135 | 2024: +0.177 | 2025: +0.125 | 2026: +0.352
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=1.09, Recency ratio=1.10
- Early IC=+0.1593, Recent IC=+0.1745, 1st-half IC=+0.1769, 2nd-half IC=+0.1933, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.127, Q3_mid=+0.142, Q4=+0.125, Q5_high_vol=+0.303

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0799, Sharpe=+0.5160)
- Admission: Train IC=+0.2083, Deflated=+0.2078, IR=0.62, Mono=0.71, p=0.0006, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.099 | 2017: +0.263 | 2018: +0.229 | 2019: +0.143 | 2020: +0.129 | 2021: +0.080 | 2022: +0.086 | 2023: +0.045 | 2024: +0.129 | 2025: +0.103 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.253 | 2016: -0.005 | 2017: +0.209 | 2018: +0.421 | 2019: +0.111 | 2020: +0.210 | 2021: +0.198 | 2022: +0.202 | 2023: +0.201 | 2024: +0.222 | 2025: +0.037 | 2026: -0.223
- IC CV=0.40, Neg years (linear/tail)=0/1 of 7, Half ratio=0.78, Recency ratio=0.64
- Early IC=+0.1627, Recent IC=+0.1045, 1st-half IC=+0.1910, 2nd-half IC=+0.1492, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.021, Q3_mid=+0.154, Q4=+0.131, Q5_high_vol=+0.236

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1254, Sharpe=+0.4916)
- Admission: Train IC=+0.2007, Deflated=+0.1999, IR=0.34, Mono=0.66, p=0.0006, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089 | 2022: +0.105 | 2023: +0.057 | 2024: +0.162 | 2025: +0.063 | 2026: +0.204
- Yearly Tail ICs:   2015: +0.192 | 2016: -0.072 | 2017: +0.231 | 2018: +0.325 | 2019: +0.267 | 2020: +0.186 | 2021: +0.230 | 2022: +0.217 | 2023: -0.018 | 2024: +0.079 | 2025: -0.129 | 2026: +0.216
- IC CV=0.38, Neg years (linear/tail)=0/1 of 7, Half ratio=0.79, Recency ratio=0.76
- Early IC=+0.1304, Recent IC=+0.0989, 1st-half IC=+0.1628, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.044, Q3_mid=+0.093, Q4=+0.132, Q5_high_vol=+0.210

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0867, Sharpe=+0.4672)
- Admission: Train IC=+0.2549, Deflated=+0.2541, IR=0.91, Mono=0.80, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.100 | 2017: +0.147 | 2018: +0.200 | 2019: +0.067 | 2020: +0.125 | 2021: +0.058 | 2022: +0.113 | 2023: +0.087 | 2024: +0.124 | 2025: +0.091 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.212 | 2017: +0.248 | 2018: +0.292 | 2019: +0.116 | 2020: +0.235 | 2021: +0.206 | 2022: +0.130 | 2023: +0.136 | 2024: +0.269 | 2025: -0.136 | 2026: -0.330
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.58
- Early IC=+0.1575, Recent IC=+0.0915, 1st-half IC=+0.1763, 2nd-half IC=+0.1174, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.151, Q2=-0.013, Q3_mid=+0.161, Q4=+0.169, Q5_high_vol=+0.250

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0235, Sharpe=+0.4423)
- Admission: Train IC=+0.2636, Deflated=+0.2642, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.42
- Yearly Linear ICs: 2015: +0.149 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081 | 2022: +0.057 | 2023: -0.004 | 2024: +0.054 | 2025: -0.068 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.451 | 2016: +0.224 | 2017: +0.122 | 2018: +0.264 | 2019: +0.306 | 2020: +0.144 | 2021: +0.132 | 2022: -0.023 | 2023: -0.009 | 2024: +0.100 | 2025: -0.102 | 2026: +0.414
- IC CV=0.68, Neg years (linear/tail)=1/0 of 7, Half ratio=0.62, Recency ratio=0.39
- Early IC=+0.1439, Recent IC=+0.0554, 1st-half IC=+0.1027, 2nd-half IC=+0.0632, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.132, Q3_mid=+0.068, Q4=+0.036, Q5_high_vol=+0.186

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0837, Sharpe=+0.3731)
- Admission: Train IC=+0.2642, Deflated=+0.2624, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.23
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073 | 2025: +0.148 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.229 | 2017: +0.386 | 2018: +0.332 | 2019: +0.207 | 2020: +0.271 | 2021: +0.214 | 2022: -0.027 | 2023: +0.087 | 2024: +0.035 | 2025: +0.246 | 2026: +0.214
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.56
- Early IC=+0.1961, Recent IC=+0.1099, 1st-half IC=+0.1766, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.040, Q3_mid=+0.111, Q4=+0.129, Q5_high_vol=+0.273

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0677, Sharpe=+0.3299)
- Admission: Train IC=+0.1732, Deflated=+0.1723, IR=0.47, Mono=0.66, p=0.0016, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.146 | 2016: -0.049 | 2017: +0.116 | 2018: +0.052 | 2019: +0.111 | 2020: +0.099 | 2021: +0.059 | 2022: +0.031 | 2023: +0.014 | 2024: +0.206 | 2025: +0.045 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.366 | 2016: -0.072 | 2017: +0.120 | 2018: +0.289 | 2019: +0.301 | 2020: +0.036 | 2021: +0.277 | 2022: +0.172 | 2023: +0.004 | 2024: +0.350 | 2025: +0.081 | 2026: -0.170
- IC CV=0.78, Neg years (linear/tail)=1/1 of 7, Half ratio=0.96, Recency ratio=1.62
- Early IC=+0.0484, Recent IC=+0.0785, 1st-half IC=+0.0774, 2nd-half IC=+0.0742, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.082, Q3_mid=+0.074, Q4=+0.067, Q5_high_vol=+0.139

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0722, Sharpe=+0.2869)
- Admission: Train IC=+0.2749, Deflated=+0.2743, IR=0.98, Mono=0.78, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.206 | 2019: +0.122 | 2020: +0.138 | 2021: +0.144 | 2022: +0.049 | 2023: +0.082 | 2024: +0.082 | 2025: +0.036 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.138 | 2017: +0.392 | 2018: +0.365 | 2019: +0.340 | 2020: +0.091 | 2021: +0.204 | 2022: +0.072 | 2023: +0.148 | 2024: -0.046 | 2025: -0.056 | 2026: +0.117
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.76, Recency ratio=0.62
- Early IC=+0.2275, Recent IC=+0.1407, 1st-half IC=+0.2151, 2nd-half IC=+0.1629, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.090, Q3_mid=+0.187, Q4=+0.149, Q5_high_vol=+0.317

**`vwap_trend_channel_slope`** (Lock IC=+0.0822, Sharpe=+0.2133)
- Admission: Train IC=+0.1640, Deflated=+0.1634, IR=0.44, Mono=0.67, p=0.0028, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.87, Recency ratio=0.99
- Early IC=+0.0779, Recent IC=+0.0768, 1st-half IC=+0.1100, 2nd-half IC=+0.0960, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.063, Q3_mid=+0.120, Q4=+0.066, Q5_high_vol=+0.119

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0766, Sharpe=+0.1934)
- Admission: Train IC=+0.3397, Deflated=+0.3393, IR=1.05, Mono=0.84, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.124 | 2017: +0.192 | 2018: +0.197 | 2019: +0.140 | 2020: +0.173 | 2021: +0.106 | 2022: +0.060 | 2023: +0.072 | 2024: +0.083 | 2025: +0.103 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.325 | 2016: +0.264 | 2017: +0.363 | 2018: +0.460 | 2019: +0.190 | 2020: +0.344 | 2021: +0.046 | 2022: +0.063 | 2023: -0.009 | 2024: +0.191 | 2025: +0.028 | 2026: +0.081
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.65
- Early IC=+0.2133, Recent IC=+0.1391, 1st-half IC=+0.2280, 2nd-half IC=+0.1555, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.045, Q3_mid=+0.163, Q4=+0.237, Q5_high_vol=+0.255

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0479, Sharpe=+0.0410)
- Admission: Train IC=+0.2185, Deflated=+0.2177, IR=0.74, Mono=0.75, p=0.0004, MaxCorr=0.09
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022 | 2022: -0.017 | 2023: -0.025 | 2024: +0.066 | 2025: +0.145 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.012 | 2017: +0.223 | 2018: +0.364 | 2019: +0.285 | 2020: +0.243 | 2021: +0.162 | 2022: -0.008 | 2023: -0.037 | 2024: +0.089 | 2025: +0.216 | 2026: +0.070
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.44
- Early IC=+0.1622, Recent IC=+0.0708, 1st-half IC=+0.1680, 2nd-half IC=+0.1053, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.018, Q3_mid=+0.193, Q4=+0.079, Q5_high_vol=+0.219

**`combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0317, Sharpe=+0.0388)
- Admission: Train IC=+0.2254, Deflated=+0.2258, IR=0.64, Mono=0.71, p=0.0002, MaxCorr=0.60
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.031 | 2017: +0.038 | 2018: +0.083 | 2019: +0.134 | 2020: +0.109 | 2021: +0.111 | 2022: +0.009 | 2023: +0.017 | 2024: +0.060 | 2025: -0.043 | 2026: +0.180
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.035 | 2017: +0.446 | 2018: +0.249 | 2019: +0.260 | 2020: +0.316 | 2021: +0.032 | 2022: -0.110 | 2023: +0.042 | 2024: +0.107 | 2025: -0.109 | 2026: +0.430
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=1.55, Recency ratio=0.96
- Early IC=+0.1143, Recent IC=+0.1099, 1st-half IC=+0.0785, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.117, Q3_mid=+0.049, Q4=+0.035, Q5_high_vol=+0.208

### 159915ETF — `single` True Positives

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1379, Sharpe=+1.4840)
- Admission: Train IC=+0.2945, Deflated=+0.2928, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.046 | 2017: +0.009 | 2018: +0.127 | 2019: +0.235 | 2020: +0.125 | 2021: +0.141 | 2022: +0.096 | 2023: +0.184 | 2024: +0.126 | 2025: +0.179 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.075 | 2017: +0.102 | 2018: +0.348 | 2019: +0.519 | 2020: +0.299 | 2021: +0.329 | 2022: +0.400 | 2023: +0.342 | 2024: +0.335 | 2025: +0.165 | 2026: +0.364
- IC CV=0.58, Neg years (linear/tail)=0/0 of 7, Half ratio=1.42, Recency ratio=1.13
- Early IC=+0.1182, Recent IC=+0.1331, 1st-half IC=+0.1155, 2nd-half IC=+0.1644, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.101, Q3_mid=+0.163, Q4=+0.164, Q5_high_vol=+0.162

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0993, Sharpe=+1.2019)
- Admission: Train IC=+0.2917, Deflated=+0.2894, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.171 | 2017: -0.008 | 2018: +0.180 | 2019: +0.206 | 2020: +0.202 | 2021: +0.114 | 2022: +0.080 | 2023: +0.113 | 2024: +0.071 | 2025: +0.120 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.178 | 2016: +0.262 | 2017: +0.079 | 2018: +0.366 | 2019: +0.399 | 2020: +0.286 | 2021: +0.183 | 2022: +0.287 | 2023: +0.190 | 2024: +0.287 | 2025: +0.288 | 2026: +0.135
- IC CV=0.50, Neg years (linear/tail)=1/0 of 7, Half ratio=1.09, Recency ratio=0.74
- Early IC=+0.2127, Recent IC=+0.1577, 1st-half IC=+0.1715, 2nd-half IC=+0.1876, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.065, Q3_mid=+0.152, Q4=+0.238, Q5_high_vol=+0.250

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1322, Sharpe=+1.1640)
- Admission: Train IC=+0.2557, Deflated=+0.2535, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.108 | 2017: +0.032 | 2018: +0.161 | 2019: +0.225 | 2020: +0.138 | 2021: +0.175 | 2022: +0.118 | 2023: +0.172 | 2024: +0.104 | 2025: +0.176 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.059 | 2017: +0.095 | 2018: +0.353 | 2019: +0.444 | 2020: +0.211 | 2021: +0.356 | 2022: +0.177 | 2023: +0.369 | 2024: +0.360 | 2025: +0.235 | 2026: +0.008
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=1.23, Recency ratio=0.94
- Early IC=+0.1667, Recent IC=+0.1562, 1st-half IC=+0.1533, 2nd-half IC=+0.1881, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.092, Q3_mid=+0.188, Q4=+0.218, Q5_high_vol=+0.212

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1171, Sharpe=+1.0935)
- Admission: Train IC=+0.2637, Deflated=+0.2612, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.078 | 2017: -0.023 | 2018: +0.106 | 2019: +0.259 | 2020: +0.133 | 2021: +0.110 | 2022: +0.073 | 2023: +0.152 | 2024: +0.091 | 2025: +0.148 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.178 | 2016: +0.083 | 2017: +0.045 | 2018: +0.286 | 2019: +0.500 | 2020: +0.173 | 2021: +0.294 | 2022: +0.258 | 2023: +0.211 | 2024: +0.394 | 2025: +0.080 | 2026: +0.232
- IC CV=0.69, Neg years (linear/tail)=1/0 of 7, Half ratio=1.25, Recency ratio=0.76
- Early IC=+0.1588, Recent IC=+0.1212, 1st-half IC=+0.1288, 2nd-half IC=+0.1607, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.035, Q3_mid=+0.115, Q4=+0.166, Q5_high_vol=+0.214

**`combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1414, Sharpe=+1.0375)
- Admission: Train IC=+0.2449, Deflated=+0.2443, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.107 | 2017: -0.074 | 2018: +0.108 | 2019: +0.116 | 2020: +0.092 | 2021: +0.053 | 2022: +0.172 | 2023: +0.132 | 2024: +0.102 | 2025: +0.109 | 2026: +0.174
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.145 | 2017: +0.151 | 2018: +0.370 | 2019: +0.316 | 2020: +0.289 | 2021: +0.222 | 2022: +0.373 | 2023: +0.090 | 2024: +0.107 | 2025: +0.186 | 2026: +0.310
- IC CV=0.88, Neg years (linear/tail)=1/0 of 7, Half ratio=0.76, Recency ratio=0.51
- Early IC=+0.1428, Recent IC=+0.0727, 1st-half IC=+0.1224, 2nd-half IC=+0.0929, Neg regimes=1/5
- Weak component: `yesterday_first_30min_return` (CV=1.04)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.090, Q3_mid=+0.108, Q4=+0.167, Q5_high_vol=+0.123

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1160, Sharpe=+1.0142)
- Admission: Train IC=+0.2885, Deflated=+0.2864, IR=0.50, Mono=0.66, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.175 | 2017: -0.028 | 2018: +0.143 | 2019: +0.206 | 2020: +0.138 | 2021: +0.124 | 2022: +0.090 | 2023: +0.137 | 2024: +0.080 | 2025: +0.169 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.227 | 2016: +0.190 | 2017: +0.043 | 2018: +0.295 | 2019: +0.402 | 2020: +0.222 | 2021: +0.331 | 2022: +0.223 | 2023: +0.248 | 2024: +0.269 | 2025: +0.348 | 2026: +0.114
- IC CV=0.55, Neg years (linear/tail)=1/0 of 7, Half ratio=1.22, Recency ratio=0.64
- Early IC=+0.2036, Recent IC=+0.1310, 1st-half IC=+0.1387, 2nd-half IC=+0.1697, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.051, Q3_mid=+0.182, Q4=+0.148, Q5_high_vol=+0.254

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1263, Sharpe=+0.6808)
- Admission: Train IC=+0.2510, Deflated=+0.2513, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034 | 2022: +0.178 | 2023: +0.116 | 2024: +0.078 | 2025: +0.128 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.190 | 2017: +0.027 | 2018: +0.354 | 2019: +0.280 | 2020: +0.401 | 2021: +0.167 | 2022: +0.459 | 2023: +0.095 | 2024: +0.032 | 2025: +0.061 | 2026: +0.267
- IC CV=0.90, Neg years (linear/tail)=1/0 of 7, Half ratio=0.89, Recency ratio=0.61
- Early IC=+0.1112, Recent IC=+0.0677, 1st-half IC=+0.0972, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `yesterday_first_30min_return` (CV=1.04)
- Regime ICs: Q1_low_vol=-0.035, Q2=+0.057, Q3_mid=+0.071, Q4=+0.110, Q5_high_vol=+0.159

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1152, Sharpe=+0.4306)
- Admission: Train IC=+0.1683, Deflated=+0.1674, IR=0.47, Mono=0.70, p=0.0024, MaxCorr=0.11
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139 | 2023: +0.083 | 2024: +0.083 | 2025: +0.120 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.017 | 2017: +0.138 | 2018: +0.257 | 2019: +0.117 | 2020: +0.189 | 2021: +0.114 | 2022: +0.057 | 2023: -0.092 | 2024: +0.146 | 2025: +0.162 | 2026: +0.240
- IC CV=0.73, Neg years (linear/tail)=0/1 of 7, Half ratio=0.82, Recency ratio=0.73
- Early IC=+0.0981, Recent IC=+0.0711, 1st-half IC=+0.1115, 2nd-half IC=+0.0914, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.004, Q3_mid=+0.061, Q4=+0.194, Q5_high_vol=+0.118

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.1009, Sharpe=+0.3747)
- Admission: Train IC=+0.2224, Deflated=+0.2203, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.141 | 2017: +0.038 | 2018: +0.099 | 2019: +0.184 | 2020: +0.122 | 2021: +0.175 | 2022: +0.110 | 2023: +0.160 | 2024: +0.073 | 2025: +0.171 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.091 | 2016: +0.131 | 2017: +0.180 | 2018: +0.206 | 2019: +0.219 | 2020: +0.109 | 2021: +0.378 | 2022: +0.299 | 2023: +0.364 | 2024: +0.106 | 2025: +0.246 | 2026: -0.363
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=1.37, Recency ratio=0.93
- Early IC=+0.1597, Recent IC=+0.1485, 1st-half IC=+0.1229, 2nd-half IC=+0.1688, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.083, Q3_mid=+0.204, Q4=+0.111, Q5_high_vol=+0.194

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1093 | +0.0576 | +0.1515 | 2y |
| `combo_ratio__limit_down_proximity_early__volume_concentration` | TP | persistent | +0.0960 | +0.0234 | +0.1970 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0951 | +0.0914 | +0.0035 | 2y |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0574 | +0.1761 | -0.1439 | 2y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0563 | +0.1922 | -0.1808 | 2y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0468 | +0.1703 | +0.0010 | 4y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.0447 | +0.1960 | -0.2064 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0377 | +0.1764 | -0.0345 | 4y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Median | gradual | +0.0339 | +0.1634 | -0.1046 | 4y |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.0283 | +0.1374 | -0.0976 | 4y |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Median | gradual | +0.0251 | +0.1565 | -0.1845 | 4y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Median | gradual | +0.0185 | +0.0578 | -0.0352 | 2y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | gradual | +0.0156 | +0.1733 | -0.1061 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | TP | gradual | +0.0115 | +0.1387 | -0.0735 | 4y |
| `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio` | FP | immediate | -0.1021 | -0.0764 | -0.1781 | ∞ |
| `combo_product__volume_weighted_momentum_acceleration__opening_drive_thrust_ratio` | FP | immediate | -0.1288 | -0.0612 | -0.2104 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=0, gradual=10, persistent=4

**FP decay trajectories:**

- `combo_product__volume_weighted_momentum_acceleration__opening_drive_thrust_ratio`: Y1:-0.129 → Y2:-0.061 → Y3:-0.013 → Y4:+0.025 → Y5:-0.210
- `combo_product__smooth_momentum_structure__opening_drive_thrust_ratio`: Y1:-0.102 → Y2:-0.076 → Y3:+0.005 → Y4:+0.035 → Y5:-0.178

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0796 | -0.0265 | 4y |
| `combo_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1130 | +0.0872 | -0.0648 | 4y |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `combo_max__bar_ret_0__max_down_ret` | TP | gradual | +0.0865 | +0.0449 | -0.0028 | 4y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0756 | +0.0530 | +0.0807 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0667 | +0.0659 | +0.1729 | ∞ |
| `vwap_trend_channel_slope` | TP | gradual | +0.0667 | +0.1186 | -0.0312 | 4y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0626 | +0.0952 | +0.1864 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0600 | +0.0723 | +0.0459 | ∞ |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | TP | fast | +0.0569 | -0.0040 | +0.1243 | 1y |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Median | persistent | +0.0553 | +0.0273 | +0.0177 | 1y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0514 | +0.0668 | +0.2403 | ∞ |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.0494 | +0.0815 | +0.1020 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0392 | +0.0958 | +0.0770 | ∞ |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | TP | gradual | +0.0315 | +0.0144 | -0.0292 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | persistent | +0.0093 | +0.0167 | +0.1802 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1016 | ∞ |
| `combo_ratio__max_down_ret__net_volume_flow` | Median | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=1, gradual=5, persistent=12

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1718 | +0.1322 | +0.1739 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1388 | +0.0826 | +0.1479 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1184 | +0.1719 | +0.0609 | ∞ |
| `combo_max__max_up_ret__first_bar_return` | TP | gradual | +0.1102 | +0.1603 | -0.0743 | 4y |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0959 | +0.1836 | +0.0723 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1369 | +0.0817 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0799 | +0.1128 | +0.0949 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0733 | +0.1517 | +0.1033 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=1, persistent=8

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.710±0.005 | 0.745±0.033 | 9% | USEFUL |
| ic_ir | 0.643±0.017 | 0.683±0.087 | 13% | USEFUL |
| p_value | 0.000±0.000 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.576±0.399 | 0.699±0.257 | 76% | WEAK |
| deflated_ic | 0.203±0.000 | 0.240±0.037 | 1% | USEFUL |
| overall_ic | 0.200±0.000 | 0.240±0.037 | 1% | USEFUL |
| raw_ic | 0.041±0.002 | 0.103±0.025 | 0% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0611, Sharpe=+0.7408
- `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.2263, Lock IC=+0.0582, Sharpe=+0.4998
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2392, Lock IC=+0.0724, Sharpe=+0.4279

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2064, Lock IC=+0.0549, Sharpe=+0.3658
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.2022, Lock IC=+0.0537, Sharpe=+0.2896
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Train IC=+0.2021, Lock IC=+0.0537, Sharpe=+0.2296

**Temporal Validation Gate**: 15/20 top rejects are profitable (75%)

- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0574, Sharpe=+0.6934
- `combo_rank_max__max_up_ret__first_bar_return`: Train IC=+0.1999, Lock IC=+0.0478, Sharpe=+0.4510
- `combo_rank_max__max_up_ret__bar_ret_0`: Train IC=+0.1999, Lock IC=+0.0478, Sharpe=+0.4510

**B3 Composite Floor**: 17/20 top rejects are profitable (85%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2120, Lock IC=+0.0697, Sharpe=+0.6724
- `combo_tri_mean__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.2193, Lock IC=+0.0613, Sharpe=+0.4615
- `combo_tri_z_mean__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.2193, Lock IC=+0.0613, Sharpe=+0.4615

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2690, Lock IC=+0.0602, Sharpe=+1.0194
- `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2660, Lock IC=+0.0602, Sharpe=+0.5551
- `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.2662, Lock IC=+0.0663, Sharpe=+0.5443

**Adaptive Correlation Gate**: 5/5 top rejects are profitable (100%)

- `combo_mean__max_up_ret__volume_surge_direction`: Train IC=+0.1816, Lock IC=+0.0540, Sharpe=+0.3602
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1600, Lock IC=+0.0717, Sharpe=+0.3059
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.2100, Lock IC=+0.0609, Sharpe=+0.2255

### 500ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_clamp_diff__max_up_ret__smooth_momentum_structure`: Train IC=+0.2923, Lock IC=+0.0884, Sharpe=+0.8893
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589
- `combo_min__star50_limit_proximity_early__opening_momentum_score`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589

**B2 Rolling Guard**: 18/20 top rejects are profitable (90%)

- `combo_mean__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.0871, Sharpe=+0.7496
- `combo_z_sum__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.0871, Sharpe=+0.7496
- `combo_mean__first_bar_return__max_down_ret`: Train IC=+0.2253, Lock IC=+0.0871, Sharpe=+0.7496

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721
- `combo_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__first_bar_sentiment__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2751, Lock IC=+0.0976, Sharpe=+1.1058
- `combo_tri_mean__max_up_ret__net_volume_flow__first_bar_sentiment`: Train IC=+0.2731, Lock IC=+0.0995, Sharpe=+0.9173
- `combo_tri_z_mean__max_up_ret__net_volume_flow__first_bar_sentiment`: Train IC=+0.2731, Lock IC=+0.0995, Sharpe=+0.9173

**B6 Temporal Stability Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3044, Lock IC=+0.1042, Sharpe=+1.0863
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3044, Lock IC=+0.1042, Sharpe=+1.0863
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Train IC=+0.3432, Lock IC=+0.1013, Sharpe=+0.9131

**B4 Correlation Gate**: 19/20 top rejects are profitable (95%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__first_bar_sentiment`: Train IC=+0.2964, Lock IC=+0.0992, Sharpe=+1.0127
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.2964, Lock IC=+0.0992, Sharpe=+1.0127
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.3140, Lock IC=+0.0983, Sharpe=+0.8497

**Adaptive Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2777, Lock IC=+0.0958, Sharpe=+0.8790
- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2965, Lock IC=+0.0792, Sharpe=+0.7590
- `combo_sig_product__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2569, Lock IC=+0.1013, Sharpe=+0.6867

### 159915ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3003, Lock IC=+0.0937, Sharpe=+1.0170
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2770, Lock IC=+0.0944, Sharpe=+0.8916
- `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early`: Train IC=+0.2925, Lock IC=+0.1215, Sharpe=+0.8804

**B2 Rolling Guard**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1282, Sharpe=+1.4615
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1282, Sharpe=+1.4615
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2801, Lock IC=+0.1270, Sharpe=+1.2519

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2090, Lock IC=+0.1339, Sharpe=+1.3910
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2090, Lock IC=+0.1339, Sharpe=+1.3910
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2088, Lock IC=+0.1185, Sharpe=+1.3814

**BH-FDR Gate**: 4/5 top rejects are profitable (80%)

- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.1156, Sharpe=+0.8924
- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0046, Sharpe=+0.4587
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0046, Sharpe=+0.4587

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1225, Sharpe=+1.6000
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1225, Sharpe=+1.6000
- `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2895, Lock IC=+0.1109, Sharpe=+1.5491

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2576, Lock IC=+0.1298, Sharpe=+1.5527
- `combo_tri_z_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2576, Lock IC=+0.1298, Sharpe=+1.5527
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1228, Sharpe=+1.5491

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1039 | 78 | 31 | 21 | 26 | 40% | 33% |
| B2 Rolling Guard | 240 | 78 | 19 | 25 | 34 | 24% | 44% |
| Temporal Validation Gate | 124 | 78 | 11 | 25 | 42 | 14% | 54% |
| BH-FDR Gate | 2 | 2 | 1 | 1 | 0 | 50% | 0% |
| B3 Composite Floor | 57 | 57 | 0 | 8 | 49 | 0% | 86% |
| B4 Correlation Gate | 86 | 78 | 0 | 3 | 75 | 0% | 96% |
| Adaptive Correlation Gate | 5 | 5 | 0 | 0 | 5 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0611, Sharpe=+0.7408
- `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.2263, Lock IC=+0.0582, Sharpe=+0.4998
- `combo_mean__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.1754, Lock IC=+0.0638, Sharpe=+0.4438

**B2 Rolling Guard** — top TP casualties:
- `combo_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1337, Lock IC=+0.0639, Sharpe=+0.9014
- `combo_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1333, Lock IC=+0.0639, Sharpe=+0.9014
- `combo_tri_min__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`: Train IC=+0.1342, Lock IC=+0.0623, Sharpe=+0.6029

**Temporal Validation Gate** — top TP casualties:
- `combo_rank_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0574, Sharpe=+0.6934

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2120, Lock IC=+0.0697, Sharpe=+0.6724
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.1746, Lock IC=+0.0614, Sharpe=+0.6539
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1742, Lock IC=+0.0615, Sharpe=+0.6539

**B4 Correlation Gate** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2690, Lock IC=+0.0602, Sharpe=+1.0194
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2121, Lock IC=+0.0750, Sharpe=+0.7601
- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1836, Lock IC=+0.0751, Sharpe=+0.7326

**Adaptive Correlation Gate** — top TP casualties:
- `combo_mean__max_up_ret__volume_surge_direction`: Train IC=+0.1816, Lock IC=+0.0540, Sharpe=+0.3602
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Train IC=+0.1600, Lock IC=+0.0717, Sharpe=+0.3059
- `combo_rel_diff__limit_down_proximity_early__volume_concentration`: Train IC=+0.2100, Lock IC=+0.0609, Sharpe=+0.2255

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1583 | 78 | 32 | 19 | 27 | 41% | 35% |
| B2 Rolling Guard | 322 | 78 | 20 | 7 | 51 | 26% | 65% |
| Temporal Validation Gate | 249 | 78 | 16 | 18 | 44 | 21% | 56% |
| BH-FDR Gate | 11 | 11 | 8 | 3 | 0 | 73% | 0% |
| B3 Composite Floor | 276 | 78 | 2 | 10 | 66 | 3% | 85% |
| B6 Yearly IC CV Gate | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B6 Temporal Stability Gate | 249 | 78 | 0 | 8 | 70 | 0% | 90% |
| B4 Correlation Gate | 484 | 78 | 0 | 12 | 66 | 0% | 85% |
| Adaptive Correlation Gate | 33 | 33 | 0 | 2 | 31 | 0% | 94% |

**7-Year Jackknife** — top TP casualties:
- `combo_clamp_diff__max_up_ret__smooth_momentum_structure`: Train IC=+0.2923, Lock IC=+0.0884, Sharpe=+0.8893
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589
- `combo_min__star50_limit_proximity_early__opening_momentum_score`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0000, Lock IC=+0.0579, Sharpe=+0.9730
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1336, Lock IC=+0.0625, Sharpe=+0.8248
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1336, Lock IC=+0.0625, Sharpe=+0.8248

**Temporal Validation Gate** — top TP casualties:
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721
- `combo_z_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721
- `combo_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721

**B3 Composite Floor** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2046, Lock IC=+0.0318, Sharpe=+1.3184
- `combo_tri_min__rbreaker_sell_setup_proximity_early__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2046, Lock IC=+0.0318, Sharpe=+1.3184
- `combo_min__net_volume_flow__max_down_ret`: Train IC=+0.2096, Lock IC=+0.1011, Sharpe=+1.1572

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.3044, Lock IC=+0.1042, Sharpe=+1.0863
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_auction_imbalance`: Train IC=+0.3044, Lock IC=+0.1042, Sharpe=+1.0863
- `combo_min__opening_drive_thrust_ratio__first_bar_sentiment`: Train IC=+0.2088, Lock IC=+0.0905, Sharpe=+1.0186

**B4 Correlation Gate** — top TP casualties:
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1044, Sharpe=+1.3464
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1044, Sharpe=+1.3464
- `combo_tri_min__net_volume_flow__first_bar_sentiment__star50_limit_proximity_early`: Train IC=+0.2914, Lock IC=+0.1012, Sharpe=+1.2611

**Adaptive Correlation Gate** — top TP casualties:
- `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`: Train IC=+0.2777, Lock IC=+0.0958, Sharpe=+0.8790
- `combo_min__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2965, Lock IC=+0.0792, Sharpe=+0.7590
- `combo_sig_product__max_up_ret__trend_bar_close_consistency`: Train IC=+0.2569, Lock IC=+0.1013, Sharpe=+0.6867

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1128 | 78 | 28 | 9 | 41 | 36% | 53% |
| B2 Rolling Guard | 382 | 78 | 18 | 6 | 54 | 23% | 69% |
| Temporal Validation Gate | 41 | 41 | 3 | 1 | 37 | 7% | 90% |
| BH-FDR Gate | 5 | 5 | 1 | 0 | 4 | 20% | 80% |
| B3 Composite Floor | 268 | 78 | 0 | 10 | 68 | 0% | 87% |
| B4 Correlation Gate | 54 | 54 | 0 | 0 | 54 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.2065, Lock IC=+0.1213, Sharpe=+1.0303
- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3003, Lock IC=+0.0937, Sharpe=+1.0170
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2770, Lock IC=+0.0944, Sharpe=+0.8916

**B2 Rolling Guard** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1282, Sharpe=+1.4615
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2342, Lock IC=+0.1282, Sharpe=+1.4615
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2801, Lock IC=+0.1270, Sharpe=+1.2519

**Temporal Validation Gate** — top TP casualties:
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2090, Lock IC=+0.1339, Sharpe=+1.3910
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2090, Lock IC=+0.1339, Sharpe=+1.3910
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.2088, Lock IC=+0.1185, Sharpe=+1.3814

**BH-FDR Gate** — top TP casualties:
- `close_vs_open_range`: Train IC=+0.0863, Lock IC=+0.1156, Sharpe=+0.8924
- `combo_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0046, Sharpe=+0.4587
- `combo_z_diff__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.0987, Lock IC=+0.0046, Sharpe=+0.4587

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2228, Lock IC=+0.1187, Sharpe=+1.7804
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2228, Lock IC=+0.1187, Sharpe=+1.7804
- `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2720, Lock IC=+0.1225, Sharpe=+1.6000

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2576, Lock IC=+0.1298, Sharpe=+1.5527
- `combo_tri_z_mean__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2576, Lock IC=+0.1298, Sharpe=+1.5527
- `combo_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2841, Lock IC=+0.1228, Sharpe=+1.5491

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (124 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 84 | 50 | 14 | 26 | 10 | 28% | 52% |
| recency_ratio >= 2.5 (late-concentrated) | 40 | 40 | 0 | 33 | 7 | 0% | 82% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0574, Sharpe=+0.6934
- `combo_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1663, Lock IC=+0.0681, Sharpe=+0.5038
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1663, Lock IC=+0.0681, Sharpe=+0.5038

### 500ETF — `single` (249 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 231 | 50 | 0 | 48 | 2 | 0% | 96% |
| recency_ratio >= 2.5 (late-concentrated) | 18 | 18 | 5 | 9 | 4 | 28% | 50% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.2296, Lock IC=+0.0765, Sharpe=+0.6052
- `combo_rank_max__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.2296, Lock IC=+0.0765, Sharpe=+0.6052
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1208, Lock IC=+0.0756, Sharpe=+0.5940
- `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment`: Train IC=+0.2199, Lock IC=+0.0763, Sharpe=+0.5337
- `combo_sig_product__high_low_sequence_momentum__max_down_ret`: Train IC=+0.1331, Lock IC=+0.0836, Sharpe=+0.3403

### 159915ETF — `single` (41 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 24 | 24 | 3 | 20 | 1 | 12% | 83% |
| recency_ratio >= 2.5 (late-concentrated) | 17 | 17 | 0 | 17 | 0 | 0% | 100% |

**Top TP killed by recency_ratio cap:**
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2090, Lock IC=+0.1339, Sharpe=+1.3910
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2090, Lock IC=+0.1339, Sharpe=+1.3910
- `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2102, Lock IC=+0.1325, Sharpe=+1.3078
- `combo_z_sum__opening_drive_thrust_ratio__star50_limit_proximity_early`: Train IC=+0.2102, Lock IC=+0.1325, Sharpe=+1.3078
- `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.2334, Lock IC=+0.1214, Sharpe=+1.2901

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `n_negative_years`: FP is higher (d=+4.16). Threshold 1.500 → 100% accuracy.
- `weak_link_cv`: FP is lower (d=-4.10). Threshold 1.460 → 70% accuracy.
- `recency_ratio`: FP is higher (d=+3.54). Threshold 1.389 → 91% accuracy.
- `n_negative_regimes`: FP is higher (d=+2.98). Threshold 1.500 → 91% accuracy.
- `ic_cv`: FP is higher (d=+1.91). Threshold 0.934 → 91% accuracy.
- `half_ratio`: FP is higher (d=+1.46). Threshold 1.365 → 82% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/2
- Decaying signal (half ratio < 0.3): 0/2
- Weak component (CV > 2.0): 0/2
- Regime-dependent (≥2 negative regimes): 2/2

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `opening_drive_thrust_ratio` | 2 | 6 | 8 | 25% |  |
| `volume_weighted_momentum_acceleration` | 1 | 4 | 5 | 20% |  |
| `first_bar_return` | 0 | 3 | 3 | 0% |  |
| `bar_body_rng_0` | 0 | 4 | 4 | 0% |  |
| `first_bar_sentiment` | 0 | 3 | 3 | 0% |  |
| `max_down_ret` | 0 | 4 | 4 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `bar_ret_0` | 0 | 3 | 3 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 8 | 8 | 0% |  |
| `close_vs_open_range` | 0 | 2 | 2 | 0% |  |
| `volume_weighted_price_position` | 0 | 3 | 3 | 0% |  |
| `star50_limit_proximity_early` | 0 | 10 | 10 | 0% |  |
| `max_up_ret` | 0 | 13 | 13 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 2 | 2 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=12, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=6, FP rate=25%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=7, FP rate=0%

