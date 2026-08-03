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

> **Caveat**: Lockbox spans ~1.0y. Sharpe-based TP/Median split has high variance at this horizon; some Median features may flip to TP with more data.

| ETF | Side | Admitted | Clusters | Cluster Sizes | Avg Sil | FP | Median | TP | FP Rate | Prod Score |
| :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 99 | 30 | `[17, 13, 9, 7, 5, 5, 4, 3, 3, 3, 2, 2, ... (30 clusters)]` | 0.1917 | 90 | 6 | 3 | 91% | 0.06 |
| 500ETF | single | 122 | 41 | `[9, 8, 7, 7, 7, 6, 6, 5, 4, 4, 3, 3, ... (41 clusters)]` | 0.2529 | 59 | 36 | 27 | 48% | 0.37 |
| 159915ETF | single | 140 | 41 | `[13, 13, 8, 7, 7, 6, 6, 5, 5, 5, 4, 4, ... (41 clusters)]` | 0.2677 | 62 | 31 | 47 | 44% | 0.45 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=90, TP=3)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.695 | 0.524 | 0.681 | 0.497 | +1.90 | 0.498 | 97% |
| n_negative_years | 0.433 | 0.000 | 0.000 | 0.000 | +0.97 | 0.000 | 96% |
| n_negative_regimes | 0.011 | 0.333 | 0.000 | 0.000 | -0.94 | 0.000 | 96% |
| ic_std_across_regimes | 0.048 | 0.057 | 0.045 | 0.055 | -0.79 | 0.025 | 96% |
| half_ratio | 0.802 | 0.723 | 0.760 | 0.737 | +0.50 | 0.454 | 96% |
| weak_link_cv | 0.857 | 0.843 | 0.731 | 0.899 | +0.08 | 0.660 | 95% |
| recency_ratio | 0.420 | 0.418 | 0.388 | 0.436 | +0.01 | 0.076 | 96% |

### 500ETF — `single` (FP=59, TP=27)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 0.987 | 0.814 | 0.956 | 0.742 | +0.61 | 0.578 | 74% |
| ic_std_across_regimes | 0.040 | 0.046 | 0.038 | 0.048 | -0.39 | 0.019 | 69% |
| ic_cv | 0.360 | 0.384 | 0.323 | 0.376 | -0.20 | 0.169 | 67% |
| recency_ratio | 0.957 | 0.901 | 0.899 | 0.786 | +0.15 | 0.474 | 71% |
| n_negative_years | 0.051 | 0.037 | 0.000 | 0.000 | +0.07 | 0.000 | 67% |
| n_negative_regimes | 0.051 | 0.037 | 0.000 | 0.000 | +0.07 | 0.000 | 67% |
| weak_link_cv | 0.467 | 0.472 | 0.482 | 0.482 | -0.04 | 0.310 | 67% |

### 159915ETF — `single` (FP=62, TP=47)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recency_ratio | 1.215 | 0.780 | 1.036 | 0.727 | +0.88 | 0.779 | 72% |
| half_ratio | 1.224 | 0.925 | 1.132 | 0.884 | +0.86 | 0.854 | 71% |
| ic_cv | 0.409 | 0.342 | 0.368 | 0.332 | +0.66 | 0.286 | 66% |
| n_negative_years | 0.048 | 0.000 | 0.000 | 0.000 | +0.32 | 0.000 | 56% |
| ic_std_across_regimes | 0.024 | 0.022 | 0.023 | 0.020 | +0.27 | 0.015 | 63% |
| weak_link_cv | 0.535 | 0.505 | 0.581 | 0.569 | +0.23 | 0.575 | 62% |
| n_negative_regimes | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 56% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.2114, Sharpe=-3.6368)
- Admission: Train IC=+0.2303, Deflated=+0.2293, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.037 | 2017: +0.038 | 2018: +0.152 | 2019: +0.040 | 2020: +0.012 | 2021: +0.187 | 2022: +0.042 | 2023: +0.199 | 2024: +0.041 | 2025: +0.106 | 2026: -0.211
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.154 | 2017: +0.194 | 2018: +0.448 | 2019: +0.247 | 2020: +0.184 | 2021: +0.335 | 2022: +0.239 | 2023: +0.190 | 2024: +0.133 | 2025: +0.140 | 2026: -0.419
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.0956, Recent IC=+0.0731, 1st-half IC=+0.0933, 2nd-half IC=+0.0951, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.094, Q3_mid=+0.055, Q4=+0.060, Q5_high_vol=+0.177

**`always_in_trend_persistence`** (Lock IC=-0.2597, Sharpe=-3.4587)
- Admission: Train IC=+0.1511, Deflated=+0.1496, IR=0.50, Mono=0.70, p=0.0034, MaxCorr=0.89
- Yearly Linear ICs: 2015: -0.030 | 2016: +0.075 | 2017: -0.026 | 2018: +0.074 | 2019: +0.026 | 2020: -0.016 | 2021: +0.128 | 2022: +0.110 | 2023: +0.093 | 2024: -0.004 | 2025: +0.051 | 2026: -0.260
- Yearly Tail ICs:   2015: -0.155 | 2016: +0.144 | 2017: -0.007 | 2018: +0.037 | 2019: +0.136 | 2020: +0.071 | 2021: +0.219 | 2022: +0.282 | 2023: +0.054 | 2024: +0.187 | 2025: +0.191 | 2026: -0.267
- IC CV=0.85, Neg years (linear/tail)=2/0 of 8, Half ratio=1.28, Recency ratio=0.47
- Early IC=+0.0503, Recent IC=+0.0237, 1st-half IC=+0.0543, 2nd-half IC=+0.0697, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.060, Q3_mid=+0.091, Q4=+0.116, Q5_high_vol=+0.021

**`combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.2002, Sharpe=-3.3600)
- Admission: Train IC=+0.1986, Deflated=+0.1980, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.087 | 2016: +0.065 | 2017: -0.025 | 2018: +0.158 | 2019: +0.063 | 2020: -0.011 | 2021: +0.164 | 2022: +0.069 | 2023: +0.192 | 2024: +0.010 | 2025: +0.095 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.097 | 2017: +0.128 | 2018: +0.352 | 2019: +0.151 | 2020: +0.030 | 2021: +0.404 | 2022: +0.227 | 2023: +0.218 | 2024: +0.175 | 2025: +0.194 | 2026: -0.148
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.09, Recency ratio=0.46
- Early IC=+0.1105, Recent IC=+0.0508, 1st-half IC=+0.0907, 2nd-half IC=+0.0991, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.096, Q3_mid=+0.043, Q4=+0.092, Q5_high_vol=+0.168

**`net_volume_flow`** (Lock IC=-0.1763, Sharpe=-3.3539)
- Admission: Train IC=+0.1397, Deflated=+0.1394, IR=0.45, Mono=0.66, p=0.0060, MaxCorr=0.88
- Yearly Linear ICs: 2015: -0.008 | 2016: +0.100 | 2017: -0.075 | 2018: +0.093 | 2019: +0.030 | 2020: +0.023 | 2021: +0.166 | 2022: +0.051 | 2023: +0.115 | 2024: +0.040 | 2025: +0.069 | 2026: -0.176
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.175 | 2017: +0.080 | 2018: +0.156 | 2019: +0.123 | 2020: -0.058 | 2021: +0.205 | 2022: +0.150 | 2023: +0.260 | 2024: +0.176 | 2025: +0.010 | 2026: -0.342
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=1.09, Recency ratio=0.89
- Early IC=+0.0616, Recent IC=+0.0548, 1st-half IC=+0.0776, 2nd-half IC=+0.0846, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.061, Q3_mid=+0.055, Q4=+0.097, Q5_high_vol=+0.121

**`combo_max__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1306, Sharpe=-2.9603)
- Admission: Train IC=+0.1690, Deflated=+0.1691, IR=0.55, Mono=0.70, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.106 | 2017: +0.012 | 2018: +0.182 | 2019: +0.079 | 2020: +0.040 | 2021: +0.181 | 2022: +0.033 | 2023: +0.186 | 2024: +0.043 | 2025: +0.081 | 2026: -0.131
- Yearly Tail ICs:   2015: +0.137 | 2016: +0.061 | 2017: -0.091 | 2018: +0.235 | 2019: +0.139 | 2020: -0.008 | 2021: +0.378 | 2022: +0.220 | 2023: +0.329 | 2024: +0.090 | 2025: +0.105 | 2026: -0.199
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.48
- Early IC=+0.1306, Recent IC=+0.0621, 1st-half IC=+0.1165, 2nd-half IC=+0.0950, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.106, Q3_mid=+0.056, Q4=+0.098, Q5_high_vol=+0.207

**`combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1994, Sharpe=-2.8678)
- Admission: Train IC=+0.2195, Deflated=+0.2191, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.061 | 2017: -0.007 | 2018: +0.167 | 2019: +0.067 | 2020: +0.015 | 2021: +0.184 | 2022: +0.056 | 2023: +0.198 | 2024: +0.010 | 2025: +0.097 | 2026: -0.199
- Yearly Tail ICs:   2015: +0.152 | 2016: -0.060 | 2017: +0.143 | 2018: +0.445 | 2019: +0.199 | 2020: +0.182 | 2021: +0.385 | 2022: +0.184 | 2023: +0.151 | 2024: +0.121 | 2025: +0.237 | 2026: -0.384
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.46
- Early IC=+0.1166, Recent IC=+0.0533, 1st-half IC=+0.1058, 2nd-half IC=+0.0916, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.100, Q3_mid=+0.050, Q4=+0.090, Q5_high_vol=+0.181

**`combo_tri_mean__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.1480, Sharpe=-2.8449)
- Admission: Train IC=+0.2186, Deflated=+0.2185, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.082 | 2017: -0.020 | 2018: +0.180 | 2019: +0.079 | 2020: +0.042 | 2021: +0.163 | 2022: +0.029 | 2023: +0.172 | 2024: +0.073 | 2025: +0.060 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.219 | 2016: +0.116 | 2017: -0.017 | 2018: +0.217 | 2019: +0.310 | 2020: +0.148 | 2021: +0.340 | 2022: +0.230 | 2023: +0.266 | 2024: +0.287 | 2025: +0.054 | 2026: -0.155
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.51
- Early IC=+0.1297, Recent IC=+0.0663, 1st-half IC=+0.1127, 2nd-half IC=+0.0872, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.072, Q3_mid=+0.054, Q4=+0.083, Q5_high_vol=+0.215

**`combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1967, Sharpe=-2.8312)
- Admission: Train IC=+0.1976, Deflated=+0.1966, IR=0.76, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.065 | 2017: -0.025 | 2018: +0.122 | 2019: +0.051 | 2020: +0.017 | 2021: +0.176 | 2022: +0.050 | 2023: +0.195 | 2024: +0.031 | 2025: +0.106 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.106 | 2016: +0.210 | 2017: +0.184 | 2018: +0.283 | 2019: +0.150 | 2020: +0.080 | 2021: +0.320 | 2022: +0.234 | 2023: +0.205 | 2024: +0.182 | 2025: +0.201 | 2026: -0.373
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=0.80
- Early IC=+0.0863, Recent IC=+0.0687, 1st-half IC=+0.0890, 2nd-half IC=+0.1008, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.073, Q3_mid=+0.040, Q4=+0.086, Q5_high_vol=+0.197

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.1395, Sharpe=-2.7529)
- Admission: Train IC=+0.1807, Deflated=+0.1814, IR=0.47, Mono=0.68, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.109 | 2017: -0.030 | 2018: +0.169 | 2019: +0.105 | 2020: +0.008 | 2021: +0.165 | 2022: +0.042 | 2023: +0.201 | 2024: -0.013 | 2025: +0.056 | 2026: -0.140
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.188 | 2017: -0.149 | 2018: +0.339 | 2019: +0.153 | 2020: +0.048 | 2021: +0.256 | 2022: +0.262 | 2023: +0.435 | 2024: +0.028 | 2025: +0.147 | 2026: -0.238
- IC CV=0.82, Neg years (linear/tail)=1/0 of 8, Half ratio=0.74, Recency ratio=0.16
- Early IC=+0.1371, Recent IC=+0.0215, 1st-half IC=+0.1095, 2nd-half IC=+0.0814, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.085, Q3_mid=+0.048, Q4=+0.105, Q5_high_vol=+0.175

**`combo_sig_product__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1294, Sharpe=-2.7464)
- Admission: Train IC=+0.1814, Deflated=+0.1819, IR=0.49, Mono=0.66, p=0.0004, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.060 | 2016: +0.043 | 2017: -0.014 | 2018: +0.165 | 2019: +0.062 | 2020: +0.014 | 2021: +0.174 | 2022: +0.064 | 2023: +0.243 | 2024: +0.026 | 2025: +0.085 | 2026: -0.129
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.087 | 2017: +0.020 | 2018: +0.328 | 2019: +0.170 | 2020: -0.030 | 2021: +0.281 | 2022: +0.197 | 2023: +0.361 | 2024: +0.051 | 2025: +0.019 | 2026: -0.333
- IC CV=0.73, Neg years (linear/tail)=0/1 of 8, Half ratio=1.01, Recency ratio=0.49
- Early IC=+0.1132, Recent IC=+0.0556, 1st-half IC=+0.1055, 2nd-half IC=+0.1067, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.144, Q3_mid=+0.052, Q4=+0.139, Q5_high_vol=+0.100

**`combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.1947, Sharpe=-2.7376)
- Admission: Train IC=+0.1400, Deflated=+0.1391, IR=0.51, Mono=0.68, p=0.0060, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.061 | 2016: +0.080 | 2017: -0.089 | 2018: +0.092 | 2019: +0.030 | 2020: +0.037 | 2021: +0.128 | 2022: +0.046 | 2023: +0.107 | 2024: +0.056 | 2025: +0.071 | 2026: -0.195
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.092 | 2017: -0.143 | 2018: +0.096 | 2019: -0.044 | 2020: +0.095 | 2021: +0.252 | 2022: +0.187 | 2023: +0.221 | 2024: +0.182 | 2025: +0.155 | 2026: -0.205
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=1.10, Recency ratio=1.04
- Early IC=+0.0611, Recent IC=+0.0633, 1st-half IC=+0.0703, 2nd-half IC=+0.0774, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.73, neg years=0)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.037, Q3_mid=+0.057, Q4=+0.080, Q5_high_vol=+0.146

**`combo_ratio__bar_ret_0__volume_surge_direction`** (Lock IC=-0.0934, Sharpe=-2.7239)
- Admission: Train IC=+0.1216, Deflated=+0.1213, IR=0.37, Mono=0.69, p=0.0130, MaxCorr=0.03
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.143 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.388 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.101
- IC CV=0.76, Neg years (linear/tail)=1/2 of 8, Half ratio=0.61, Recency ratio=0.27
- Early IC=+0.1185, Recent IC=+0.0324, 1st-half IC=+0.0942, 2nd-half IC=+0.0576, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.079, Q3_mid=+0.061, Q4=+0.060, Q5_high_vol=+0.144

**`combo_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1087, Sharpe=-2.7122)
- Admission: Train IC=+0.2138, Deflated=+0.2139, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.115 | 2017: +0.115 | 2018: +0.285 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.249 | 2024: +0.186 | 2025: +0.049 | 2026: -0.298
- IC CV=0.70, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.28
- Early IC=+0.1447, Recent IC=+0.0402, 1st-half IC=+0.1084, 2nd-half IC=+0.0644, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.093, Q3_mid=+0.045, Q4=+0.083, Q5_high_vol=+0.153

**`combo_min__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.0557, Sharpe=-2.7098)
- Admission: Train IC=+0.1700, Deflated=+0.1699, IR=0.73, Mono=0.79, p=0.0010, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.050 | 2017: -0.021 | 2018: +0.257 | 2019: +0.069 | 2020: -0.002 | 2021: +0.106 | 2022: +0.081 | 2023: +0.165 | 2024: -0.010 | 2025: +0.121 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.447 | 2016: -0.292 | 2017: +0.023 | 2018: +0.219 | 2019: +0.082 | 2020: +0.089 | 2021: +0.289 | 2022: +0.220 | 2023: +0.279 | 2024: +0.133 | 2025: +0.246 | 2026: -0.349
- IC CV=0.83, Neg years (linear/tail)=2/0 of 8, Half ratio=0.89, Recency ratio=0.34
- Early IC=+0.1629, Recent IC=+0.0557, 1st-half IC=+0.1035, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.122, Q3_mid=+0.023, Q4=+0.128, Q5_high_vol=+0.134

**`combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1823, Sharpe=-2.6806)
- Admission: Train IC=+0.1930, Deflated=+0.1922, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.040 | 2016: +0.007 | 2017: -0.037 | 2018: +0.097 | 2019: +0.012 | 2020: -0.012 | 2021: +0.176 | 2022: +0.041 | 2023: +0.180 | 2024: +0.030 | 2025: +0.039 | 2026: -0.182
- Yearly Tail ICs:   2015: -0.008 | 2016: -0.008 | 2017: +0.213 | 2018: +0.282 | 2019: +0.228 | 2020: +0.001 | 2021: +0.426 | 2022: +0.147 | 2023: +0.341 | 2024: +0.113 | 2025: +0.059 | 2026: -0.259
- IC CV=0.97, Neg years (linear/tail)=1/0 of 8, Half ratio=1.22, Recency ratio=0.64
- Early IC=+0.0544, Recent IC=+0.0348, 1st-half IC=+0.0637, 2nd-half IC=+0.0776, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.057, Q3_mid=+0.011, Q4=+0.126, Q5_high_vol=+0.082

**`combo_mean__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.1191, Sharpe=-2.6755)
- Admission: Train IC=+0.1724, Deflated=+0.1724, IR=0.62, Mono=0.72, p=0.0010, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.106 | 2016: +0.039 | 2017: +0.003 | 2018: +0.214 | 2019: +0.111 | 2020: -0.009 | 2021: +0.135 | 2022: +0.065 | 2023: +0.195 | 2024: -0.009 | 2025: +0.124 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.144 | 2016: -0.219 | 2017: +0.140 | 2018: +0.308 | 2019: +0.076 | 2020: +0.089 | 2021: +0.302 | 2022: +0.283 | 2023: +0.243 | 2024: +0.146 | 2025: +0.241 | 2026: -0.368
- IC CV=0.76, Neg years (linear/tail)=2/0 of 8, Half ratio=0.90, Recency ratio=0.35
- Early IC=+0.1623, Recent IC=+0.0575, 1st-half IC=+0.1066, 2nd-half IC=+0.0958, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.128, Q3_mid=+0.040, Q4=+0.115, Q5_high_vol=+0.122

**`combo_ratio__max_up_ret__bar_vol_0`** (Lock IC=-0.1432, Sharpe=-2.6027)
- Admission: Train IC=+0.1121, Deflated=+0.1122, IR=0.50, Mono=0.68, p=0.0220, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.110 | 2017: +0.021 | 2018: +0.150 | 2019: +0.052 | 2020: +0.036 | 2021: +0.202 | 2022: +0.006 | 2023: +0.139 | 2024: +0.051 | 2025: +0.044 | 2026: -0.143
- Yearly Tail ICs:   2015: +0.224 | 2016: -0.062 | 2017: +0.126 | 2018: +0.106 | 2019: +0.095 | 2020: -0.039 | 2021: +0.524 | 2022: +0.211 | 2023: +0.288 | 2024: +0.221 | 2025: +0.122 | 2026: -0.244
- IC CV=0.76, Neg years (linear/tail)=0/1 of 8, Half ratio=0.62, Recency ratio=0.47
- Early IC=+0.1009, Recent IC=+0.0473, 1st-half IC=+0.0971, 2nd-half IC=+0.0601, Neg regimes=0/5
- Weak component: `bar_vol_0` (CV=2.33, neg years=2)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.035, Q3_mid=+0.074, Q4=+0.047, Q5_high_vol=+0.197

**`combo_rank_max__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.1476, Sharpe=-2.5718)
- Admission: Train IC=+0.2146, Deflated=+0.2147, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.046 | 2018: +0.125 | 2019: +0.050 | 2020: +0.040 | 2021: +0.174 | 2022: +0.018 | 2023: +0.171 | 2024: +0.046 | 2025: +0.077 | 2026: -0.148
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.068 | 2017: -0.092 | 2018: +0.289 | 2019: +0.241 | 2020: +0.096 | 2021: +0.371 | 2022: +0.246 | 2023: +0.229 | 2024: +0.159 | 2025: +0.084 | 2026: -0.332
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.69
- Early IC=+0.0875, Recent IC=+0.0605, 1st-half IC=+0.0904, 2nd-half IC=+0.0853, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.066, Q3_mid=+0.042, Q4=+0.076, Q5_high_vol=+0.197

**`combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1526, Sharpe=-2.5270)
- Admission: Train IC=+0.1705, Deflated=+0.1703, IR=0.54, Mono=0.69, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.107 | 2017: -0.014 | 2018: +0.192 | 2019: +0.061 | 2020: +0.033 | 2021: +0.161 | 2022: +0.012 | 2023: +0.143 | 2024: +0.062 | 2025: +0.064 | 2026: -0.153
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.181 | 2017: -0.108 | 2018: +0.160 | 2019: +0.188 | 2020: +0.033 | 2021: +0.303 | 2022: +0.172 | 2023: +0.339 | 2024: +0.200 | 2025: +0.013 | 2026: -0.244
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.50
- Early IC=+0.1263, Recent IC=+0.0627, 1st-half IC=+0.1066, 2nd-half IC=+0.0763, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.072, Q3_mid=+0.043, Q4=+0.085, Q5_high_vol=+0.200

**`combo_tri_median__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1287, Sharpe=-2.4666)
- Admission: Train IC=+0.2028, Deflated=+0.2026, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.105 | 2017: -0.025 | 2018: +0.225 | 2019: +0.070 | 2020: +0.007 | 2021: +0.171 | 2022: +0.064 | 2023: +0.181 | 2024: +0.019 | 2025: +0.088 | 2026: -0.129
- Yearly Tail ICs:   2015: +0.165 | 2016: +0.163 | 2017: -0.149 | 2018: +0.342 | 2019: +0.237 | 2020: -0.039 | 2021: +0.464 | 2022: +0.347 | 2023: +0.305 | 2024: +0.137 | 2025: +0.100 | 2026: -0.163
- IC CV=0.72, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.36
- Early IC=+0.1473, Recent IC=+0.0536, 1st-half IC=+0.1162, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.109, Q3_mid=+0.071, Q4=+0.101, Q5_high_vol=+0.165

**`combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1421, Sharpe=-2.4325)
- Admission: Train IC=+0.1894, Deflated=+0.1891, IR=0.70, Mono=0.76, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.091 | 2017: +0.012 | 2018: +0.148 | 2019: +0.063 | 2020: +0.045 | 2021: +0.196 | 2022: +0.024 | 2023: +0.191 | 2024: +0.056 | 2025: +0.091 | 2026: -0.142
- Yearly Tail ICs:   2015: +0.061 | 2016: +0.055 | 2017: -0.093 | 2018: +0.275 | 2019: +0.142 | 2020: +0.062 | 2021: +0.415 | 2022: +0.196 | 2023: +0.359 | 2024: +0.173 | 2025: +0.054 | 2026: -0.353
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.70
- Early IC=+0.1059, Recent IC=+0.0736, 1st-half IC=+0.1103, 2nd-half IC=+0.0979, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.091, Q3_mid=+0.055, Q4=+0.083, Q5_high_vol=+0.212

**`combo_rank_max__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.1571, Sharpe=-2.4219)
- Admission: Train IC=+0.1808, Deflated=+0.1813, IR=0.69, Mono=0.75, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.026 | 2017: +0.003 | 2018: +0.134 | 2019: +0.115 | 2020: -0.021 | 2021: +0.130 | 2022: +0.048 | 2023: +0.198 | 2024: -0.025 | 2025: +0.092 | 2026: -0.152
- Yearly Tail ICs:   2015: -0.039 | 2016: -0.160 | 2017: +0.177 | 2018: +0.242 | 2019: +0.249 | 2020: +0.115 | 2021: +0.213 | 2022: +0.211 | 2023: +0.085 | 2024: +0.123 | 2025: +0.284 | 2026: -0.257
- IC CV=0.84, Neg years (linear/tail)=2/0 of 8, Half ratio=0.95, Recency ratio=0.34
- Early IC=+0.1235, Recent IC=+0.0414, 1st-half IC=+0.0902, 2nd-half IC=+0.0861, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.121, Q3_mid=+0.032, Q4=+0.086, Q5_high_vol=+0.069

**`morning_volume_weighted_momentum`** (Lock IC=-0.1752, Sharpe=-2.4148)
- Admission: Train IC=+0.1634, Deflated=+0.1619, IR=0.56, Mono=0.71, p=0.0014, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.047 | 2016: +0.001 | 2017: -0.097 | 2018: +0.060 | 2019: +0.016 | 2020: +0.033 | 2021: +0.153 | 2022: +0.045 | 2023: +0.123 | 2024: +0.053 | 2025: +0.088 | 2026: -0.175
- Yearly Tail ICs:   2015: -0.006 | 2016: +0.073 | 2017: +0.015 | 2018: +0.085 | 2019: +0.053 | 2020: +0.009 | 2021: +0.233 | 2022: +0.101 | 2023: +0.284 | 2024: +0.192 | 2025: +0.315 | 2026: -0.261
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.85
- Early IC=+0.0382, Recent IC=+0.0705, 1st-half IC=+0.0674, 2nd-half IC=+0.0852, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.040, Q3_mid=+0.052, Q4=+0.095, Q5_high_vol=+0.120

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1502, Sharpe=-2.3921)
- Admission: Train IC=+0.2207, Deflated=+0.2205, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.074 | 2017: +0.066 | 2018: +0.203 | 2019: +0.058 | 2020: -0.012 | 2021: +0.168 | 2022: +0.056 | 2023: +0.177 | 2024: +0.008 | 2025: +0.101 | 2026: -0.150
- Yearly Tail ICs:   2015: +0.123 | 2016: -0.028 | 2017: +0.155 | 2018: +0.513 | 2019: +0.178 | 2020: +0.202 | 2021: +0.365 | 2022: +0.224 | 2023: +0.190 | 2024: +0.100 | 2025: +0.188 | 2026: -0.307
- IC CV=0.80, Neg years (linear/tail)=1/0 of 8, Half ratio=0.85, Recency ratio=0.42
- Early IC=+0.1309, Recent IC=+0.0548, 1st-half IC=+0.1019, 2nd-half IC=+0.0868, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.098, Q3_mid=+0.066, Q4=+0.076, Q5_high_vol=+0.140

**`combo_rank_max__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1762, Sharpe=-2.3921)
- Admission: Train IC=+0.2113, Deflated=+0.2111, IR=0.60, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.032 | 2017: +0.051 | 2018: +0.189 | 2019: +0.057 | 2020: -0.007 | 2021: +0.167 | 2022: +0.055 | 2023: +0.189 | 2024: +0.001 | 2025: +0.086 | 2026: -0.174
- Yearly Tail ICs:   2015: +0.108 | 2016: -0.059 | 2017: +0.161 | 2018: +0.434 | 2019: +0.187 | 2020: +0.228 | 2021: +0.380 | 2022: +0.205 | 2023: +0.135 | 2024: +0.112 | 2025: +0.221 | 2026: -0.343
- IC CV=0.82, Neg years (linear/tail)=2/0 of 8, Half ratio=0.84, Recency ratio=0.34
- Early IC=+0.1225, Recent IC=+0.0421, 1st-half IC=+0.0987, 2nd-half IC=+0.0828, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.109, Q3_mid=+0.057, Q4=+0.077, Q5_high_vol=+0.125

**`combo_rank_max__first_bar_return__bar_body_rng_0`** (Lock IC=-0.0889, Sharpe=-2.3913)
- Admission: Train IC=+0.1979, Deflated=+0.1979, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.112 | 2017: +0.050 | 2018: +0.194 | 2019: +0.090 | 2020: -0.007 | 2021: +0.146 | 2022: +0.043 | 2023: +0.154 | 2024: +0.036 | 2025: +0.076 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.072 | 2017: +0.038 | 2018: +0.334 | 2019: +0.170 | 2020: +0.024 | 2021: +0.343 | 2022: +0.299 | 2023: +0.322 | 2024: +0.032 | 2025: +0.142 | 2026: -0.377
- IC CV=0.70, Neg years (linear/tail)=1/1 of 8, Half ratio=0.72, Recency ratio=0.39
- Early IC=+0.1436, Recent IC=+0.0555, 1st-half IC=+0.1090, 2nd-half IC=+0.0785, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.099, Q3_mid=+0.040, Q4=+0.101, Q5_high_vol=+0.165

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=-0.1615, Sharpe=-2.3451)
- Admission: Train IC=+0.2141, Deflated=+0.2132, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.074 | 2017: +0.051 | 2018: +0.174 | 2019: +0.059 | 2020: +0.029 | 2021: +0.172 | 2022: +0.011 | 2023: +0.161 | 2024: +0.060 | 2025: +0.077 | 2026: -0.162
- Yearly Tail ICs:   2015: +0.075 | 2016: +0.099 | 2017: +0.044 | 2018: +0.335 | 2019: +0.231 | 2020: +0.128 | 2021: +0.386 | 2022: +0.256 | 2023: +0.311 | 2024: +0.121 | 2025: +0.037 | 2026: -0.323
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.59
- Early IC=+0.1166, Recent IC=+0.0684, 1st-half IC=+0.1054, 2nd-half IC=+0.0758, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.078, Q3_mid=+0.046, Q4=+0.075, Q5_high_vol=+0.185

**`early_order_flow_imbalance`** (Lock IC=-0.2024, Sharpe=-2.3152)
- Admission: Train IC=+0.1502, Deflated=+0.1488, IR=0.49, Mono=0.66, p=0.0034, MaxCorr=0.73
- Yearly Linear ICs: 2015: -0.032 | 2016: +0.074 | 2017: -0.067 | 2018: +0.082 | 2019: +0.048 | 2020: -0.019 | 2021: +0.147 | 2022: +0.098 | 2023: +0.111 | 2024: -0.001 | 2025: +0.076 | 2026: -0.202
- Yearly Tail ICs:   2015: -0.115 | 2016: +0.147 | 2017: +0.009 | 2018: +0.142 | 2019: +0.189 | 2020: -0.092 | 2021: +0.406 | 2022: +0.190 | 2023: +0.100 | 2024: +0.087 | 2025: +0.113 | 2026: -0.121
- IC CV=0.78, Neg years (linear/tail)=2/1 of 8, Half ratio=1.30, Recency ratio=0.58
- Early IC=+0.0650, Recent IC=+0.0377, 1st-half IC=+0.0622, 2nd-half IC=+0.0811, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.089, Q3_mid=+0.096, Q4=+0.113, Q5_high_vol=+0.015

**`combo_ratio__volume_surge_direction__volume_weighted_price_position`** (Lock IC=-0.1192, Sharpe=-2.2557)
- Admission: Train IC=+0.1246, Deflated=+0.1255, IR=0.65, Mono=0.70, p=0.0114, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.026 | 2017: -0.042 | 2018: +0.171 | 2019: +0.146 | 2020: +0.020 | 2021: +0.075 | 2022: +0.043 | 2023: +0.154 | 2024: -0.009 | 2025: +0.081 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.196 | 2016: -0.135 | 2017: -0.002 | 2018: +0.160 | 2019: +0.165 | 2020: +0.169 | 2021: +0.191 | 2022: -0.027 | 2023: +0.159 | 2024: +0.165 | 2025: +0.220 | 2026: -0.269
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.71, Recency ratio=0.23
- Early IC=+0.1586, Recent IC=+0.0363, 1st-half IC=+0.0962, 2nd-half IC=+0.0687, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.077, Q3_mid=+0.021, Q4=+0.106, Q5_high_vol=+0.084

**`opening_drive_thrust_ratio`** (Lock IC=-0.1510, Sharpe=-2.2099)
- Admission: Train IC=+0.1983, Deflated=+0.1985, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.039 | 2018: +0.176 | 2019: +0.078 | 2020: +0.042 | 2021: +0.170 | 2022: +0.024 | 2023: +0.166 | 2024: +0.033 | 2025: +0.069 | 2026: -0.151
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.178 | 2017: -0.121 | 2018: +0.326 | 2019: +0.224 | 2020: +0.117 | 2021: +0.389 | 2022: +0.169 | 2023: +0.259 | 2024: +0.120 | 2025: +0.073 | 2026: -0.040
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.1273, Recent IC=+0.0512, 1st-half IC=+0.1123, 2nd-half IC=+0.0854, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.008, Q2=+0.079, Q3_mid=+0.067, Q4=+0.089, Q5_high_vol=+0.213

**`combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0828, Sharpe=-2.2099)
- Admission: Train IC=+0.2001, Deflated=+0.2005, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.044 | 2016: +0.076 | 2017: -0.045 | 2018: +0.158 | 2019: +0.129 | 2020: +0.016 | 2021: +0.145 | 2022: +0.033 | 2023: +0.175 | 2024: +0.017 | 2025: +0.010 | 2026: -0.083
- Yearly Tail ICs:   2015: -0.049 | 2016: +0.132 | 2017: -0.140 | 2018: +0.339 | 2019: +0.247 | 2020: +0.104 | 2021: +0.389 | 2022: +0.172 | 2023: +0.263 | 2024: +0.124 | 2025: +0.090 | 2026: -0.040
- IC CV=0.79, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.09
- Early IC=+0.1433, Recent IC=+0.0132, 1st-half IC=+0.1065, 2nd-half IC=+0.0666, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.102, Q3_mid=+0.063, Q4=+0.073, Q5_high_vol=+0.136

**`combo_tri_mean__bar_ret_0__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1078, Sharpe=-2.1999)
- Admission: Train IC=+0.2041, Deflated=+0.2042, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.113 | 2016: +0.098 | 2017: +0.011 | 2018: +0.206 | 2019: +0.091 | 2020: +0.025 | 2021: +0.154 | 2022: +0.040 | 2023: +0.159 | 2024: +0.047 | 2025: +0.069 | 2026: -0.108
- Yearly Tail ICs:   2015: +0.229 | 2016: -0.056 | 2017: -0.069 | 2018: +0.231 | 2019: +0.123 | 2020: +0.082 | 2021: +0.329 | 2022: +0.238 | 2023: +0.255 | 2024: +0.268 | 2025: +0.165 | 2026: -0.217
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.39
- Early IC=+0.1487, Recent IC=+0.0579, 1st-half IC=+0.1190, 2nd-half IC=+0.0856, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.099, Q3_mid=+0.057, Q4=+0.091, Q5_high_vol=+0.200

**`combo_mean__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1215, Sharpe=-2.1883)
- Admission: Train IC=+0.2017, Deflated=+0.2015, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.074 | 2017: +0.044 | 2018: +0.210 | 2019: +0.072 | 2020: -0.038 | 2021: +0.160 | 2022: +0.063 | 2023: +0.179 | 2024: +0.004 | 2025: +0.107 | 2026: -0.122
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.001 | 2017: +0.167 | 2018: +0.435 | 2019: +0.145 | 2020: -0.022 | 2021: +0.342 | 2022: +0.311 | 2023: +0.414 | 2024: +0.072 | 2025: +0.179 | 2026: -0.062
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=0.92, Recency ratio=0.39
- Early IC=+0.1411, Recent IC=+0.0551, 1st-half IC=+0.1009, 2nd-half IC=+0.0925, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.124, Q3_mid=+0.048, Q4=+0.101, Q5_high_vol=+0.130

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1964, Sharpe=-2.1840)
- Admission: Train IC=+0.2038, Deflated=+0.2027, IR=0.91, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.77, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.66
- Early IC=+0.0887, Recent IC=+0.0589, 1st-half IC=+0.0862, 2nd-half IC=+0.0892, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.065, Q3_mid=+0.037, Q4=+0.066, Q5_high_vol=+0.175

**`combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0581, Sharpe=-2.1391)
- Admission: Train IC=+0.2165, Deflated=+0.2165, IR=0.62, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.113 | 2017: -0.035 | 2018: +0.203 | 2019: +0.134 | 2020: +0.016 | 2021: +0.151 | 2022: +0.067 | 2023: +0.175 | 2024: +0.047 | 2025: +0.073 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.185 | 2017: -0.112 | 2018: +0.245 | 2019: +0.241 | 2020: +0.067 | 2021: +0.399 | 2022: +0.327 | 2023: +0.211 | 2024: +0.154 | 2025: +0.220 | 2026: -0.028
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.35
- Early IC=+0.1687, Recent IC=+0.0598, 1st-half IC=+0.1241, 2nd-half IC=+0.1002, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.108, Q3_mid=+0.060, Q4=+0.083, Q5_high_vol=+0.239

**`combo_rank_min__max_up_ret__volume_surge_direction`** (Lock IC=-0.0639, Sharpe=-2.1335)
- Admission: Train IC=+0.1903, Deflated=+0.1911, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.080 | 2017: -0.027 | 2018: +0.184 | 2019: +0.070 | 2020: +0.069 | 2021: +0.146 | 2022: +0.042 | 2023: +0.146 | 2024: +0.031 | 2025: +0.061 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.181 | 2016: -0.163 | 2017: -0.084 | 2018: +0.190 | 2019: +0.187 | 2020: +0.323 | 2021: +0.341 | 2022: +0.033 | 2023: +0.347 | 2024: +0.226 | 2025: +0.066 | 2026: -0.286
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.31
- Early IC=+0.1278, Recent IC=+0.0396, 1st-half IC=+0.1068, 2nd-half IC=+0.0674, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.069, Q2=+0.083, Q3_mid=+0.036, Q4=+0.093, Q5_high_vol=+0.150

**`combo_min__max_up_ret__volume_surge_direction`** (Lock IC=-0.0597, Sharpe=-2.1258)
- Admission: Train IC=+0.1895, Deflated=+0.1903, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.086 | 2017: -0.024 | 2018: +0.185 | 2019: +0.058 | 2020: +0.073 | 2021: +0.132 | 2022: +0.035 | 2023: +0.150 | 2024: +0.031 | 2025: +0.064 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.269 | 2016: -0.223 | 2017: -0.056 | 2018: +0.286 | 2019: +0.111 | 2020: +0.336 | 2021: +0.246 | 2022: +0.024 | 2023: +0.406 | 2024: +0.229 | 2025: +0.190 | 2026: -0.193
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.39
- Early IC=+0.1217, Recent IC=+0.0474, 1st-half IC=+0.1060, 2nd-half IC=+0.0707, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.073, Q3_mid=+0.050, Q4=+0.093, Q5_high_vol=+0.155

**`combo_tri_max__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1364, Sharpe=-2.1155)
- Admission: Train IC=+0.2060, Deflated=+0.2059, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.097 | 2017: +0.016 | 2018: +0.194 | 2019: +0.082 | 2020: +0.050 | 2021: +0.181 | 2022: +0.028 | 2023: +0.187 | 2024: +0.037 | 2025: +0.084 | 2026: -0.136
- Yearly Tail ICs:   2015: +0.179 | 2016: -0.031 | 2017: -0.043 | 2018: +0.350 | 2019: +0.159 | 2020: +0.213 | 2021: +0.359 | 2022: +0.200 | 2023: +0.253 | 2024: +0.117 | 2025: +0.209 | 2026: -0.326
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.44
- Early IC=+0.1380, Recent IC=+0.0606, 1st-half IC=+0.1228, 2nd-half IC=+0.0901, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.102, Q3_mid=+0.060, Q4=+0.100, Q5_high_vol=+0.208

**`combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1573, Sharpe=-1.9849)
- Admission: Train IC=+0.2265, Deflated=+0.2263, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.069 | 2017: +0.012 | 2018: +0.218 | 2019: +0.076 | 2020: +0.013 | 2021: +0.154 | 2022: +0.054 | 2023: +0.179 | 2024: +0.021 | 2025: +0.104 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.175 | 2016: -0.037 | 2017: +0.062 | 2018: +0.310 | 2019: +0.174 | 2020: +0.105 | 2021: +0.354 | 2022: +0.257 | 2023: +0.242 | 2024: +0.264 | 2025: +0.148 | 2026: -0.020
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.43
- Early IC=+0.1470, Recent IC=+0.0628, 1st-half IC=+0.1132, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.108, Q3_mid=+0.058, Q4=+0.094, Q5_high_vol=+0.183

**`combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1708, Sharpe=-1.9174)
- Admission: Train IC=+0.1684, Deflated=+0.1681, IR=0.66, Mono=0.73, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.070 | 2017: +0.038 | 2018: +0.173 | 2019: +0.062 | 2020: -0.009 | 2021: +0.184 | 2022: +0.055 | 2023: +0.189 | 2024: +0.024 | 2025: +0.112 | 2026: -0.171
- Yearly Tail ICs:   2015: +0.164 | 2016: -0.057 | 2017: +0.158 | 2018: +0.341 | 2019: +0.085 | 2020: -0.005 | 2021: +0.363 | 2022: +0.215 | 2023: +0.253 | 2024: +0.207 | 2025: +0.246 | 2026: -0.161
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=0.58
- Early IC=+0.1176, Recent IC=+0.0682, 1st-half IC=+0.0994, 2nd-half IC=+0.0994, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.102, Q3_mid=+0.053, Q4=+0.084, Q5_high_vol=+0.176

**`combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1298, Sharpe=-1.8873)
- Admission: Train IC=+0.1817, Deflated=+0.1814, IR=0.67, Mono=0.73, p=0.0004, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.052 | 2017: +0.016 | 2018: +0.112 | 2019: +0.045 | 2020: -0.069 | 2021: +0.149 | 2022: +0.070 | 2023: +0.198 | 2024: +0.055 | 2025: +0.063 | 2026: -0.130
- Yearly Tail ICs:   2015: -0.055 | 2016: +0.053 | 2017: -0.053 | 2018: +0.273 | 2019: +0.139 | 2020: -0.034 | 2021: +0.371 | 2022: +0.309 | 2023: +0.456 | 2024: +0.038 | 2025: +0.206 | 2026: +0.025
- IC CV=0.96, Neg years (linear/tail)=1/1 of 8, Half ratio=1.87, Recency ratio=0.75
- Early IC=+0.0782, Recent IC=+0.0587, 1st-half IC=+0.0551, 2nd-half IC=+0.1031, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.078, Q3_mid=+0.016, Q4=+0.102, Q5_high_vol=+0.077

**`combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.1148, Sharpe=-1.8175)
- Admission: Train IC=+0.2090, Deflated=+0.2095, IR=0.77, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.096 | 2017: -0.037 | 2018: +0.201 | 2019: +0.102 | 2020: +0.052 | 2021: +0.140 | 2022: +0.043 | 2023: +0.145 | 2024: +0.047 | 2025: +0.045 | 2026: -0.115
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.047 | 2017: +0.030 | 2018: +0.126 | 2019: +0.238 | 2020: +0.130 | 2021: +0.265 | 2022: +0.320 | 2023: +0.256 | 2024: +0.257 | 2025: +0.047 | 2026: -0.016
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.30
- Early IC=+0.1517, Recent IC=+0.0460, 1st-half IC=+0.1216, 2nd-half IC=+0.0776, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.018, Q2=+0.069, Q3_mid=+0.072, Q4=+0.082, Q5_high_vol=+0.215

**`combo_tri_median__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1563, Sharpe=-1.8076)
- Admission: Train IC=+0.1977, Deflated=+0.1977, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.061 | 2017: -0.005 | 2018: +0.189 | 2019: +0.056 | 2020: +0.017 | 2021: +0.171 | 2022: +0.026 | 2023: +0.174 | 2024: +0.032 | 2025: +0.069 | 2026: -0.156
- Yearly Tail ICs:   2015: +0.051 | 2016: +0.094 | 2017: -0.133 | 2018: +0.289 | 2019: +0.244 | 2020: -0.011 | 2021: +0.359 | 2022: +0.229 | 2023: +0.323 | 2024: +0.177 | 2025: +0.047 | 2026: +0.049
- IC CV=0.75, Neg years (linear/tail)=0/1 of 8, Half ratio=0.79, Recency ratio=0.41
- Early IC=+0.1226, Recent IC=+0.0506, 1st-half IC=+0.1033, 2nd-half IC=+0.0818, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.085, Q3_mid=+0.052, Q4=+0.066, Q5_high_vol=+0.182

**`combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1153, Sharpe=-1.6739)
- Admission: Train IC=+0.1910, Deflated=+0.1908, IR=0.74, Mono=0.73, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.129 | 2016: +0.075 | 2017: -0.019 | 2018: +0.196 | 2019: +0.074 | 2020: -0.005 | 2021: +0.169 | 2022: +0.038 | 2023: +0.170 | 2024: +0.017 | 2025: +0.071 | 2026: -0.115
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.018 | 2017: -0.185 | 2018: +0.297 | 2019: +0.163 | 2020: +0.021 | 2021: +0.408 | 2022: +0.255 | 2023: +0.382 | 2024: +0.136 | 2025: +0.080 | 2026: -0.069
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.73, Recency ratio=0.33
- Early IC=+0.1349, Recent IC=+0.0441, 1st-half IC=+0.1083, 2nd-half IC=+0.0794, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.084, Q3_mid=+0.033, Q4=+0.107, Q5_high_vol=+0.150

**`combo_mean__max_up_ret__volume_surge_direction`** (Lock IC=-0.1168, Sharpe=-1.6684)
- Admission: Train IC=+0.2212, Deflated=+0.2216, IR=0.86, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.062 | 2017: -0.014 | 2018: +0.167 | 2019: +0.102 | 2020: +0.030 | 2021: +0.136 | 2022: +0.030 | 2023: +0.161 | 2024: +0.042 | 2025: +0.081 | 2026: -0.117
- Yearly Tail ICs:   2015: +0.126 | 2016: +0.103 | 2017: +0.060 | 2018: +0.271 | 2019: +0.178 | 2020: +0.199 | 2021: +0.216 | 2022: +0.159 | 2023: +0.407 | 2024: +0.272 | 2025: +0.222 | 2026: -0.206
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.46
- Early IC=+0.1345, Recent IC=+0.0617, 1st-half IC=+0.1043, 2nd-half IC=+0.0842, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.069, Q2=+0.078, Q3_mid=+0.036, Q4=+0.086, Q5_high_vol=+0.175

**`combo_max__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=-0.1417, Sharpe=-1.6345)
- Admission: Train IC=+0.2104, Deflated=+0.2107, IR=0.73, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.061 | 2017: -0.034 | 2018: +0.172 | 2019: +0.130 | 2020: +0.018 | 2021: +0.135 | 2022: +0.034 | 2023: +0.204 | 2024: +0.016 | 2025: +0.086 | 2026: -0.142
- Yearly Tail ICs:   2015: +0.063 | 2016: -0.025 | 2017: +0.026 | 2018: +0.253 | 2019: +0.179 | 2020: +0.160 | 2021: +0.247 | 2022: +0.129 | 2023: +0.334 | 2024: +0.130 | 2025: +0.307 | 2026: -0.114
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.34
- Early IC=+0.1509, Recent IC=+0.0509, 1st-half IC=+0.1087, 2nd-half IC=+0.0902, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.113, Q3_mid=+0.044, Q4=+0.107, Q5_high_vol=+0.155

**`combo_min__bar_ret_0__volume_surge_direction`** (Lock IC=-0.0762, Sharpe=-1.6243)
- Admission: Train IC=+0.1874, Deflated=+0.1875, IR=0.57, Mono=0.69, p=0.0004, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.075 | 2016: +0.044 | 2017: +0.046 | 2018: +0.181 | 2019: +0.071 | 2020: +0.045 | 2021: +0.148 | 2022: +0.033 | 2023: +0.136 | 2024: -0.005 | 2025: +0.077 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.290 | 2016: -0.321 | 2017: +0.038 | 2018: +0.065 | 2019: +0.001 | 2020: +0.354 | 2021: +0.289 | 2022: +0.201 | 2023: +0.325 | 2024: +0.223 | 2025: +0.165 | 2026: -0.197
- IC CV=0.70, Neg years (linear/tail)=1/0 of 8, Half ratio=0.54, Recency ratio=0.28
- Early IC=+0.1261, Recent IC=+0.0357, 1st-half IC=+0.1086, 2nd-half IC=+0.0590, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.072, Q3_mid=+0.031, Q4=+0.086, Q5_high_vol=+0.150

**`combo_min__first_bar_return__first_bar_sentiment`** (Lock IC=-0.0691, Sharpe=-1.5273)
- Admission: Train IC=+0.1429, Deflated=+0.1430, IR=0.51, Mono=0.70, p=0.0054, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.090 | 2017: +0.042 | 2018: +0.161 | 2019: +0.087 | 2020: +0.032 | 2021: +0.136 | 2022: +0.029 | 2023: +0.126 | 2024: +0.010 | 2025: +0.057 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.150 | 2016: -0.197 | 2017: +0.009 | 2018: +0.173 | 2019: +0.117 | 2020: +0.277 | 2021: +0.328 | 2022: +0.244 | 2023: +0.287 | 2024: +0.085 | 2025: +0.161 | 2026: -0.108
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.27
- Early IC=+0.1240, Recent IC=+0.0333, 1st-half IC=+0.1020, 2nd-half IC=+0.0568, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.077, Q3_mid=+0.045, Q4=+0.068, Q5_high_vol=+0.158

**`combo_sig_product__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0908, Sharpe=-1.5036)
- Admission: Train IC=+0.1781, Deflated=+0.1776, IR=0.69, Mono=0.77, p=0.0008, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.083 | 2017: +0.010 | 2018: +0.202 | 2019: +0.114 | 2020: -0.021 | 2021: +0.142 | 2022: +0.035 | 2023: +0.127 | 2024: +0.000 | 2025: +0.023 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.021 | 2017: +0.167 | 2018: +0.256 | 2019: +0.180 | 2020: -0.034 | 2021: +0.382 | 2022: +0.328 | 2023: +0.203 | 2024: +0.059 | 2025: +0.205 | 2026: -0.163
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=0.51, Recency ratio=0.07
- Early IC=+0.1580, Recent IC=+0.0118, 1st-half IC=+0.1032, 2nd-half IC=+0.0527, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.056, Q3_mid=+0.023, Q4=+0.116, Q5_high_vol=+0.117

**`combo_sig_product__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0908, Sharpe=-1.5036)
- Admission: Train IC=+0.1781, Deflated=+0.1776, IR=0.69, Mono=0.77, p=0.0008, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.082 | 2017: +0.010 | 2018: +0.188 | 2019: +0.114 | 2020: -0.021 | 2021: +0.142 | 2022: +0.035 | 2023: +0.127 | 2024: +0.000 | 2025: +0.023 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.021 | 2017: +0.167 | 2018: +0.256 | 2019: +0.180 | 2020: -0.034 | 2021: +0.382 | 2022: +0.328 | 2023: +0.203 | 2024: +0.059 | 2025: +0.205 | 2026: -0.163
- IC CV=0.94, Neg years (linear/tail)=1/1 of 8, Half ratio=0.53, Recency ratio=0.08
- Early IC=+0.1511, Recent IC=+0.0118, 1st-half IC=+0.0995, 2nd-half IC=+0.0527, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.046, Q3_mid=+0.023, Q4=+0.116, Q5_high_vol=+0.117

**`volume_weighted_price_position`** (Lock IC=-0.1599, Sharpe=-1.5036)
- Admission: Train IC=+0.1779, Deflated=+0.1774, IR=0.67, Mono=0.77, p=0.0008, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.074 | 2016: +0.014 | 2017: +0.013 | 2018: +0.181 | 2019: +0.043 | 2020: -0.059 | 2021: +0.154 | 2022: +0.076 | 2023: +0.195 | 2024: -0.023 | 2025: +0.108 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.027 | 2016: -0.028 | 2017: +0.211 | 2018: +0.239 | 2019: +0.155 | 2020: -0.026 | 2021: +0.394 | 2022: +0.342 | 2023: +0.295 | 2024: +0.041 | 2025: +0.227 | 2026: -0.163
- IC CV=1.03, Neg years (linear/tail)=2/1 of 8, Half ratio=1.17, Recency ratio=0.38
- Early IC=+0.1122, Recent IC=+0.0423, 1st-half IC=+0.0782, 2nd-half IC=+0.0917, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.130, Q3_mid=+0.037, Q4=+0.094, Q5_high_vol=+0.076

**`combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1466, Sharpe=-1.4795)
- Admission: Train IC=+0.2224, Deflated=+0.2226, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.071 | 2016: +0.048 | 2017: +0.006 | 2018: +0.230 | 2019: +0.066 | 2020: -0.007 | 2021: +0.177 | 2022: +0.034 | 2023: +0.175 | 2024: +0.002 | 2025: +0.117 | 2026: -0.152
- Yearly Tail ICs:   2015: +0.062 | 2016: +0.071 | 2017: -0.065 | 2018: +0.212 | 2019: +0.322 | 2020: +0.079 | 2021: +0.452 | 2022: +0.290 | 2023: +0.380 | 2024: -0.075 | 2025: +0.093 | 2026: -0.005
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=0.77, Recency ratio=0.40
- Early IC=+0.1483, Recent IC=+0.0595, 1st-half IC=+0.1116, 2nd-half IC=+0.0864, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.120, Q3_mid=+0.069, Q4=+0.099, Q5_high_vol=+0.143

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=-0.0538, Sharpe=-1.4245)
- Admission: Train IC=+0.2098, Deflated=+0.2097, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.105 | 2017: -0.027 | 2018: +0.203 | 2019: +0.092 | 2020: +0.058 | 2021: +0.156 | 2022: +0.073 | 2023: +0.128 | 2024: +0.030 | 2025: +0.071 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.271 | 2016: +0.108 | 2017: -0.002 | 2018: +0.284 | 2019: +0.198 | 2020: +0.192 | 2021: +0.379 | 2022: +0.258 | 2023: +0.231 | 2024: +0.118 | 2025: +0.075 | 2026: +0.046
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.34
- Early IC=+0.1478, Recent IC=+0.0504, 1st-half IC=+0.1262, 2nd-half IC=+0.0781, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.065, Q3_mid=+0.054, Q4=+0.074, Q5_high_vol=+0.236

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0199, Sharpe=-1.3557)
- Admission: Train IC=+0.1628, Deflated=+0.1625, IR=0.54, Mono=0.69, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.071 | 2016: +0.107 | 2017: -0.051 | 2018: +0.120 | 2019: +0.016 | 2020: +0.062 | 2021: +0.154 | 2022: +0.089 | 2023: +0.109 | 2024: +0.024 | 2025: +0.052 | 2026: -0.020
- Yearly Tail ICs:   2015: -0.135 | 2016: +0.131 | 2017: +0.039 | 2018: +0.374 | 2019: +0.106 | 2020: -0.003 | 2021: +0.304 | 2022: +0.282 | 2023: +0.180 | 2024: +0.108 | 2025: +0.128 | 2026: -0.110
- IC CV=0.58, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.56
- Early IC=+0.0677, Recent IC=+0.0378, 1st-half IC=+0.0873, 2nd-half IC=+0.0753, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.042, Q3_mid=+0.006, Q4=+0.070, Q5_high_vol=+0.212

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0648, Sharpe=-1.3198)
- Admission: Train IC=+0.1916, Deflated=+0.1923, IR=0.52, Mono=0.69, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.086 | 2016: +0.111 | 2017: -0.010 | 2018: +0.159 | 2019: +0.087 | 2020: +0.031 | 2021: +0.116 | 2022: +0.060 | 2023: +0.150 | 2024: +0.008 | 2025: +0.033 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.024 | 2016: +0.269 | 2017: +0.115 | 2018: +0.144 | 2019: +0.207 | 2020: +0.036 | 2021: +0.142 | 2022: +0.323 | 2023: +0.340 | 2024: +0.052 | 2025: +0.111 | 2026: -0.046
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.16
- Early IC=+0.1229, Recent IC=+0.0203, 1st-half IC=+0.0975, 2nd-half IC=+0.0651, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.076, Q3_mid=+0.046, Q4=+0.090, Q5_high_vol=+0.136

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=-0.1611, Sharpe=-1.2733)
- Admission: Train IC=+0.2301, Deflated=+0.2290, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.087 | 2017: +0.035 | 2018: +0.169 | 2019: +0.060 | 2020: +0.041 | 2021: +0.170 | 2022: +0.015 | 2023: +0.166 | 2024: +0.060 | 2025: +0.078 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.033 | 2017: +0.026 | 2018: +0.412 | 2019: +0.206 | 2020: +0.193 | 2021: +0.360 | 2022: +0.306 | 2023: +0.290 | 2024: +0.141 | 2025: +0.095 | 2026: -0.308
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.60
- Early IC=+0.1152, Recent IC=+0.0689, 1st-half IC=+0.1068, 2nd-half IC=+0.0797, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.078, Q3_mid=+0.047, Q4=+0.080, Q5_high_vol=+0.189

**`combo_sig_product__bar_body_rng_0__volume_surge_direction`** (Lock IC=-0.0580, Sharpe=-1.2501)
- Admission: Train IC=+0.1495, Deflated=+0.1502, IR=0.54, Mono=0.66, p=0.0034, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.034 | 2017: -0.037 | 2018: +0.176 | 2019: +0.115 | 2020: +0.039 | 2021: +0.044 | 2022: +0.051 | 2023: +0.146 | 2024: -0.002 | 2025: +0.096 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.277 | 2016: -0.101 | 2017: -0.035 | 2018: +0.244 | 2019: +0.137 | 2020: +0.248 | 2021: +0.066 | 2022: +0.066 | 2023: +0.176 | 2024: +0.213 | 2025: +0.429 | 2026: -0.036
- IC CV=0.68, Neg years (linear/tail)=1/0 of 8, Half ratio=0.79, Recency ratio=0.32
- Early IC=+0.1453, Recent IC=+0.0470, 1st-half IC=+0.0882, 2nd-half IC=+0.0699, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.074, Q3_mid=+0.007, Q4=+0.101, Q5_high_vol=+0.090

**`combo_mean__first_bar_sentiment__volume_surge_direction`** (Lock IC=-0.0740, Sharpe=-1.2501)
- Admission: Train IC=+0.1445, Deflated=+0.1453, IR=0.55, Mono=0.67, p=0.0050, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.084 | 2016: +0.038 | 2017: -0.038 | 2018: +0.175 | 2019: +0.120 | 2020: +0.027 | 2021: +0.056 | 2022: +0.055 | 2023: +0.146 | 2024: -0.011 | 2025: +0.100 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.277 | 2016: -0.086 | 2017: -0.035 | 2018: +0.244 | 2019: +0.137 | 2020: +0.235 | 2021: +0.066 | 2022: +0.008 | 2023: +0.176 | 2024: +0.199 | 2025: +0.429 | 2026: -0.036
- IC CV=0.70, Neg years (linear/tail)=1/0 of 8, Half ratio=0.80, Recency ratio=0.30
- Early IC=+0.1474, Recent IC=+0.0444, 1st-half IC=+0.0906, 2nd-half IC=+0.0720, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.082, Q3_mid=+0.012, Q4=+0.105, Q5_high_vol=+0.089

**`combo_rank_min__max_up_ret__first_bar_return`** (Lock IC=-0.0956, Sharpe=-1.2359)
- Admission: Train IC=+0.1919, Deflated=+0.1927, IR=0.52, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.106 | 2017: -0.010 | 2018: +0.175 | 2019: +0.078 | 2020: +0.023 | 2021: +0.132 | 2022: +0.033 | 2023: +0.127 | 2024: +0.035 | 2025: +0.016 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.152 | 2016: -0.021 | 2017: -0.063 | 2018: +0.175 | 2019: +0.219 | 2020: +0.159 | 2021: +0.452 | 2022: +0.175 | 2023: +0.279 | 2024: +0.236 | 2025: +0.016 | 2026: -0.121
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.21
- Early IC=+0.1265, Recent IC=+0.0266, 1st-half IC=+0.1016, 2nd-half IC=+0.0591, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.068, Q3_mid=+0.034, Q4=+0.074, Q5_high_vol=+0.172

**`combo_mean__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=-0.1221, Sharpe=-1.2067)
- Admission: Train IC=+0.2345, Deflated=+0.2349, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.071 | 2017: -0.041 | 2018: +0.205 | 2019: +0.113 | 2020: +0.040 | 2021: +0.143 | 2022: +0.037 | 2023: +0.173 | 2024: +0.028 | 2025: +0.099 | 2026: -0.122
- Yearly Tail ICs:   2015: -0.009 | 2016: -0.057 | 2017: -0.047 | 2018: +0.295 | 2019: +0.106 | 2020: +0.202 | 2021: +0.388 | 2022: +0.132 | 2023: +0.318 | 2024: +0.302 | 2025: +0.283 | 2026: -0.283
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.1591, Recent IC=+0.0636, 1st-half IC=+0.1189, 2nd-half IC=+0.0902, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.094, Q3_mid=+0.050, Q4=+0.111, Q5_high_vol=+0.192

**`combo_sig_product__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1002, Sharpe=-1.2031)
- Admission: Train IC=+0.2142, Deflated=+0.2140, IR=0.81, Mono=0.82, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.059 | 2016: +0.099 | 2017: -0.078 | 2018: +0.172 | 2019: +0.081 | 2020: +0.022 | 2021: +0.133 | 2022: +0.012 | 2023: +0.160 | 2024: +0.048 | 2025: -0.004 | 2026: -0.100
- Yearly Tail ICs:   2015: -0.050 | 2016: -0.059 | 2017: -0.046 | 2018: +0.241 | 2019: +0.205 | 2020: -0.004 | 2021: +0.307 | 2022: +0.365 | 2023: +0.414 | 2024: +0.163 | 2025: +0.159 | 2026: -0.027
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=0.62, Recency ratio=0.17
- Early IC=+0.1260, Recent IC=+0.0216, 1st-half IC=+0.0979, 2nd-half IC=+0.0604, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.081, Q3_mid=+0.012, Q4=+0.111, Q5_high_vol=+0.128

**`combo_max__bar_ret_0__volume_surge_direction`** (Lock IC=-0.0832, Sharpe=-1.1822)
- Admission: Train IC=+0.2473, Deflated=+0.2480, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.63
- Yearly Linear ICs: 2015: +0.103 | 2016: +0.085 | 2017: -0.005 | 2018: +0.200 | 2019: +0.145 | 2020: -0.003 | 2021: +0.044 | 2022: +0.044 | 2023: +0.170 | 2024: +0.031 | 2025: +0.074 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.156 | 2016: -0.010 | 2017: -0.009 | 2018: +0.420 | 2019: +0.328 | 2020: +0.162 | 2021: +0.026 | 2022: +0.273 | 2023: +0.190 | 2024: +0.310 | 2025: +0.332 | 2026: -0.137
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=0.81, Recency ratio=0.30
- Early IC=+0.1724, Recent IC=+0.0523, 1st-half IC=+0.0957, 2nd-half IC=+0.0778, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.107, Q3_mid=+0.025, Q4=+0.103, Q5_high_vol=+0.122

**`combo_rank_max__first_bar_return__volume_surge_direction`** (Lock IC=-0.0811, Sharpe=-1.1822)
- Admission: Train IC=+0.2445, Deflated=+0.2454, IR=0.80, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.088 | 2017: -0.004 | 2018: +0.200 | 2019: +0.144 | 2020: -0.006 | 2021: +0.039 | 2022: +0.045 | 2023: +0.168 | 2024: +0.026 | 2025: +0.074 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.106 | 2016: -0.026 | 2017: -0.012 | 2018: +0.400 | 2019: +0.299 | 2020: +0.128 | 2021: -0.029 | 2022: +0.239 | 2023: +0.143 | 2024: +0.330 | 2025: +0.362 | 2026: -0.010
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=0.88, Recency ratio=0.35
- Early IC=+0.1659, Recent IC=+0.0585, 1st-half IC=+0.0870, 2nd-half IC=+0.0764, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.087, Q3_mid=+0.016, Q4=+0.100, Q5_high_vol=+0.121

**`combo_min__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0924, Sharpe=-1.1726)
- Admission: Train IC=+0.2257, Deflated=+0.2261, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.078 | 2016: +0.097 | 2017: -0.003 | 2018: +0.220 | 2019: +0.081 | 2020: +0.007 | 2021: +0.167 | 2022: +0.037 | 2023: +0.147 | 2024: +0.040 | 2025: +0.070 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.025 | 2016: +0.162 | 2017: -0.113 | 2018: +0.302 | 2019: +0.258 | 2020: +0.094 | 2021: +0.487 | 2022: +0.106 | 2023: +0.198 | 2024: +0.054 | 2025: +0.113 | 2026: -0.070
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.36
- Early IC=+0.1505, Recent IC=+0.0548, 1st-half IC=+0.1191, 2nd-half IC=+0.0823, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.089, Q3_mid=+0.068, Q4=+0.089, Q5_high_vol=+0.207

**`combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.0631, Sharpe=-1.1652)
- Admission: Train IC=+0.2144, Deflated=+0.2143, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.065 | 2017: +0.033 | 2018: +0.209 | 2019: +0.075 | 2020: -0.029 | 2021: +0.132 | 2022: +0.060 | 2023: +0.171 | 2024: +0.026 | 2025: +0.092 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.197 | 2016: -0.103 | 2017: +0.117 | 2018: +0.139 | 2019: +0.188 | 2020: +0.008 | 2021: +0.349 | 2022: +0.394 | 2023: +0.318 | 2024: +0.158 | 2025: +0.068 | 2026: -0.177
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.91, Recency ratio=0.42
- Early IC=+0.1417, Recent IC=+0.0590, 1st-half IC=+0.0993, 2nd-half IC=+0.0904, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.144, Q3_mid=+0.036, Q4=+0.099, Q5_high_vol=+0.137

**`combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0127, Sharpe=-1.1004)
- Admission: Train IC=+0.1853, Deflated=+0.1848, IR=0.56, Mono=0.70, p=0.0004, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.121 | 2017: -0.026 | 2018: +0.165 | 2019: +0.003 | 2020: +0.067 | 2021: +0.160 | 2022: +0.085 | 2023: +0.125 | 2024: +0.018 | 2025: +0.050 | 2026: -0.013
- Yearly Tail ICs:   2015: -0.093 | 2016: +0.075 | 2017: -0.134 | 2018: +0.359 | 2019: +0.077 | 2020: +0.091 | 2021: +0.281 | 2022: +0.314 | 2023: +0.220 | 2024: +0.147 | 2025: +0.098 | 2026: -0.043
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.0839, Recent IC=+0.0338, 1st-half IC=+0.0973, 2nd-half IC=+0.0738, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.063, Q3_mid=+0.008, Q4=+0.073, Q5_high_vol=+0.220

**`combo_rank_max__max_up_ret__volume_surge_direction`** (Lock IC=-0.1503, Sharpe=-1.0912)
- Admission: Train IC=+0.2219, Deflated=+0.2217, IR=0.78, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.060 | 2017: -0.046 | 2018: +0.147 | 2019: +0.111 | 2020: -0.002 | 2021: +0.109 | 2022: +0.031 | 2023: +0.150 | 2024: +0.023 | 2025: +0.073 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.060 | 2017: +0.088 | 2018: +0.317 | 2019: +0.297 | 2020: +0.141 | 2021: +0.117 | 2022: +0.289 | 2023: +0.112 | 2024: +0.255 | 2025: +0.268 | 2026: -0.080
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.42
- Early IC=+0.1283, Recent IC=+0.0537, 1st-half IC=+0.0889, 2nd-half IC=+0.0811, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.064, Q3_mid=+0.020, Q4=+0.090, Q5_high_vol=+0.140

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1853, Sharpe=-1.0717)
- Admission: Train IC=+0.2143, Deflated=+0.2137, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.056 | 2017: +0.004 | 2018: +0.173 | 2019: +0.049 | 2020: +0.002 | 2021: +0.181 | 2022: +0.048 | 2023: +0.189 | 2024: +0.030 | 2025: +0.110 | 2026: -0.185
- Yearly Tail ICs:   2015: +0.040 | 2016: +0.202 | 2017: +0.153 | 2018: +0.378 | 2019: +0.176 | 2020: +0.070 | 2021: +0.366 | 2022: +0.348 | 2023: +0.363 | 2024: +0.071 | 2025: +0.047 | 2026: +0.009
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.63
- Early IC=+0.1107, Recent IC=+0.0702, 1st-half IC=+0.0979, 2nd-half IC=+0.0947, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.098, Q3_mid=+0.041, Q4=+0.081, Q5_high_vol=+0.171

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0842, Sharpe=-1.0673)
- Admission: Train IC=+0.2009, Deflated=+0.2009, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.107 | 2017: -0.057 | 2018: +0.207 | 2019: +0.079 | 2020: +0.072 | 2021: +0.171 | 2022: +0.067 | 2023: +0.123 | 2024: +0.031 | 2025: +0.068 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.034 | 2016: +0.127 | 2017: +0.085 | 2018: +0.402 | 2019: +0.287 | 2020: +0.039 | 2021: +0.364 | 2022: +0.233 | 2023: +0.108 | 2024: +0.205 | 2025: +0.075 | 2026: +0.036
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.35
- Early IC=+0.1433, Recent IC=+0.0498, 1st-half IC=+0.1284, 2nd-half IC=+0.0789, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.060, Q3_mid=+0.050, Q4=+0.084, Q5_high_vol=+0.255

**`combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0691, Sharpe=-0.9513)
- Admission: Train IC=+0.2251, Deflated=+0.2262, IR=0.74, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.084 | 2017: +0.015 | 2018: +0.179 | 2019: +0.078 | 2020: +0.010 | 2021: +0.121 | 2022: +0.037 | 2023: +0.161 | 2024: +0.056 | 2025: +0.024 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.221 | 2016: -0.002 | 2017: +0.076 | 2018: +0.189 | 2019: +0.199 | 2020: +0.158 | 2021: +0.339 | 2022: +0.258 | 2023: +0.297 | 2024: +0.315 | 2025: +0.053 | 2026: -0.003
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.31
- Early IC=+0.1282, Recent IC=+0.0400, 1st-half IC=+0.0993, 2nd-half IC=+0.0716, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.077, Q3_mid=+0.046, Q4=+0.073, Q5_high_vol=+0.175

**`combo_max__max_up_ret__volume_surge_direction`** (Lock IC=-0.1457, Sharpe=-0.8783)
- Admission: Train IC=+0.2178, Deflated=+0.2176, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.042 | 2017: -0.035 | 2018: +0.154 | 2019: +0.107 | 2020: -0.000 | 2021: +0.120 | 2022: +0.032 | 2023: +0.160 | 2024: +0.029 | 2025: +0.077 | 2026: -0.146
- Yearly Tail ICs:   2015: +0.170 | 2016: +0.162 | 2017: +0.120 | 2018: +0.362 | 2019: +0.235 | 2020: +0.080 | 2021: +0.285 | 2022: +0.322 | 2023: +0.238 | 2024: +0.187 | 2025: +0.156 | 2026: -0.230
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=0.86, Recency ratio=0.41
- Early IC=+0.1304, Recent IC=+0.0532, 1st-half IC=+0.0925, 2nd-half IC=+0.0798, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.063, Q3_mid=+0.019, Q4=+0.081, Q5_high_vol=+0.152

**`combo_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=-0.0823, Sharpe=-0.8469)
- Admission: Train IC=+0.2133, Deflated=+0.2139, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.070 | 2017: -0.049 | 2018: +0.213 | 2019: +0.081 | 2020: +0.054 | 2021: +0.130 | 2022: +0.038 | 2023: +0.138 | 2024: +0.016 | 2025: +0.109 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.199 | 2016: +0.004 | 2017: -0.149 | 2018: +0.246 | 2019: +0.201 | 2020: +0.212 | 2021: +0.262 | 2022: +0.119 | 2023: +0.199 | 2024: +0.244 | 2025: +0.318 | 2026: -0.183
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.42
- Early IC=+0.1473, Recent IC=+0.0626, 1st-half IC=+0.1132, 2nd-half IC=+0.0833, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.075, Q3_mid=+0.053, Q4=+0.108, Q5_high_vol=+0.190

**`combo_min__bar_body_rng_0__volume_surge_direction`** (Lock IC=-0.0625, Sharpe=-0.7902)
- Admission: Train IC=+0.2509, Deflated=+0.2514, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.061 | 2016: +0.028 | 2017: -0.004 | 2018: +0.186 | 2019: +0.080 | 2020: +0.036 | 2021: +0.155 | 2022: +0.029 | 2023: +0.169 | 2024: +0.018 | 2025: +0.076 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.224 | 2016: -0.183 | 2017: +0.022 | 2018: +0.174 | 2019: +0.013 | 2020: +0.237 | 2021: +0.443 | 2022: -0.037 | 2023: +0.432 | 2024: +0.290 | 2025: +0.363 | 2026: -0.203
- IC CV=0.67, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.35
- Early IC=+0.1333, Recent IC=+0.0467, 1st-half IC=+0.1174, 2nd-half IC=+0.0772, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.107, Q3_mid=+0.051, Q4=+0.090, Q5_high_vol=+0.149

**`combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0539, Sharpe=-0.7695)
- Admission: Train IC=+0.2078, Deflated=+0.2076, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.112 | 2017: -0.021 | 2018: +0.217 | 2019: +0.134 | 2020: +0.026 | 2021: +0.129 | 2022: +0.058 | 2023: +0.168 | 2024: +0.053 | 2025: +0.062 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.084 | 2017: +0.031 | 2018: +0.262 | 2019: +0.268 | 2020: +0.275 | 2021: +0.220 | 2022: +0.175 | 2023: +0.217 | 2024: +0.285 | 2025: +0.137 | 2026: +0.003
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.33
- Early IC=+0.1754, Recent IC=+0.0573, 1st-half IC=+0.1263, 2nd-half IC=+0.0924, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.103, Q3_mid=+0.062, Q4=+0.068, Q5_high_vol=+0.245

**`combo_max__first_bar_return__first_bar_sentiment`** (Lock IC=-0.0930, Sharpe=-0.7198)
- Admission: Train IC=+0.1719, Deflated=+0.1720, IR=0.62, Mono=0.75, p=0.0010, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.078 | 2017: +0.023 | 2018: +0.190 | 2019: +0.109 | 2020: +0.021 | 2021: +0.110 | 2022: +0.037 | 2023: +0.157 | 2024: -0.009 | 2025: +0.078 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.049 | 2017: +0.026 | 2018: +0.341 | 2019: +0.202 | 2020: +0.240 | 2021: +0.136 | 2022: +0.196 | 2023: +0.286 | 2024: +0.144 | 2025: +0.184 | 2026: -0.243
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=0.57, Recency ratio=0.23
- Early IC=+0.1495, Recent IC=+0.0346, 1st-half IC=+0.1111, 2nd-half IC=+0.0630, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.109, Q3_mid=+0.049, Q4=+0.084, Q5_high_vol=+0.143

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0294, Sharpe=-0.6275)
- Admission: Train IC=+0.2621, Deflated=+0.2635, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.044 | 2017: -0.018 | 2018: +0.176 | 2019: +0.149 | 2020: +0.038 | 2021: +0.123 | 2022: +0.049 | 2023: +0.166 | 2024: +0.037 | 2025: +0.098 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.429 | 2016: -0.084 | 2017: +0.010 | 2018: +0.251 | 2019: +0.289 | 2020: +0.241 | 2021: +0.375 | 2022: +0.320 | 2023: +0.138 | 2024: +0.270 | 2025: +0.111 | 2026: +0.204
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.42
- Early IC=+0.1624, Recent IC=+0.0674, 1st-half IC=+0.1215, 2nd-half IC=+0.0884, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.101, Q3_mid=+0.073, Q4=+0.092, Q5_high_vol=+0.190

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=-0.0504, Sharpe=-0.6267)
- Admission: Train IC=+0.2353, Deflated=+0.2367, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.100 | 2017: -0.041 | 2018: +0.160 | 2019: +0.128 | 2020: +0.071 | 2021: +0.117 | 2022: +0.038 | 2023: +0.129 | 2024: +0.032 | 2025: +0.051 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.481 | 2016: -0.072 | 2017: -0.113 | 2018: +0.244 | 2019: +0.298 | 2020: +0.301 | 2021: +0.341 | 2022: +0.270 | 2023: +0.120 | 2024: +0.271 | 2025: +0.089 | 2026: +0.130
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.29
- Early IC=+0.1439, Recent IC=+0.0419, 1st-half IC=+0.1183, 2nd-half IC=+0.0671, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.061, Q3_mid=+0.073, Q4=+0.073, Q5_high_vol=+0.201

**`combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=-0.0969, Sharpe=-0.5930)
- Admission: Train IC=+0.1379, Deflated=+0.1378, IR=0.36, Mono=0.69, p=0.0066, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.057 | 2016: -0.018 | 2017: -0.054 | 2018: +0.132 | 2019: +0.060 | 2020: +0.038 | 2021: +0.076 | 2022: +0.023 | 2023: +0.148 | 2024: +0.038 | 2025: +0.078 | 2026: -0.097
- Yearly Tail ICs:   2015: +0.024 | 2016: -0.174 | 2017: -0.030 | 2018: +0.049 | 2019: +0.046 | 2020: +0.193 | 2021: +0.139 | 2022: -0.028 | 2023: +0.037 | 2024: +0.329 | 2025: +0.360 | 2026: -0.142
- IC CV=0.57, Neg years (linear/tail)=0/1 of 8, Half ratio=1.10, Recency ratio=0.60
- Early IC=+0.0960, Recent IC=+0.0580, 1st-half IC=+0.0656, 2nd-half IC=+0.0724, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.006, Q3_mid=+0.063, Q4=+0.071, Q5_high_vol=+0.121

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0712, Sharpe=-0.5845)
- Admission: Train IC=+0.2454, Deflated=+0.2463, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.054 | 2017: -0.048 | 2018: +0.208 | 2019: +0.130 | 2020: +0.058 | 2021: +0.154 | 2022: +0.046 | 2023: +0.131 | 2024: +0.030 | 2025: +0.082 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.380 | 2016: -0.045 | 2017: -0.018 | 2018: +0.279 | 2019: +0.291 | 2020: +0.218 | 2021: +0.418 | 2022: +0.321 | 2023: +0.104 | 2024: +0.253 | 2025: +0.050 | 2026: +0.239
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.33
- Early IC=+0.1690, Recent IC=+0.0564, 1st-half IC=+0.1366, 2nd-half IC=+0.0803, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.070, Q3_mid=+0.091, Q4=+0.105, Q5_high_vol=+0.214

**`combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0955, Sharpe=-0.5706)
- Admission: Train IC=+0.2233, Deflated=+0.2238, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.099 | 2017: -0.006 | 2018: +0.210 | 2019: +0.081 | 2020: +0.002 | 2021: +0.127 | 2022: +0.062 | 2023: +0.164 | 2024: +0.030 | 2025: +0.084 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.064 | 2016: -0.115 | 2017: +0.133 | 2018: +0.160 | 2019: +0.213 | 2020: +0.100 | 2021: +0.327 | 2022: +0.362 | 2023: +0.368 | 2024: +0.190 | 2025: +0.034 | 2026: -0.118
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.39
- Early IC=+0.1455, Recent IC=+0.0571, 1st-half IC=+0.1051, 2nd-half IC=+0.0869, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.130, Q3_mid=+0.043, Q4=+0.095, Q5_high_vol=+0.154

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=-0.0717, Sharpe=-0.5279)
- Admission: Train IC=+0.1653, Deflated=+0.1649, IR=0.52, Mono=0.68, p=0.0010, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.045 | 2016: +0.049 | 2017: -0.106 | 2018: +0.168 | 2019: +0.089 | 2020: +0.031 | 2021: +0.114 | 2022: -0.030 | 2023: +0.190 | 2024: +0.010 | 2025: +0.025 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.095 | 2016: -0.034 | 2017: -0.262 | 2018: +0.391 | 2019: +0.009 | 2020: +0.208 | 2021: +0.256 | 2022: +0.244 | 2023: +0.260 | 2024: +0.147 | 2025: +0.134 | 2026: -0.175
- IC CV=0.99, Neg years (linear/tail)=1/0 of 8, Half ratio=0.40, Recency ratio=0.14
- Early IC=+0.1286, Recent IC=+0.0176, 1st-half IC=+0.0996, 2nd-half IC=+0.0396, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.086, Q3_mid=+0.026, Q4=+0.074, Q5_high_vol=+0.112

**`combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1081, Sharpe=-0.5121)
- Admission: Train IC=+0.2009, Deflated=+0.2012, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.073 | 2017: +0.023 | 2018: +0.218 | 2019: +0.098 | 2020: -0.000 | 2021: +0.145 | 2022: +0.047 | 2023: +0.146 | 2024: +0.024 | 2025: +0.112 | 2026: -0.108
- Yearly Tail ICs:   2015: +0.109 | 2016: -0.020 | 2017: -0.001 | 2018: +0.087 | 2019: +0.182 | 2020: +0.076 | 2021: +0.328 | 2022: +0.396 | 2023: +0.342 | 2024: +0.094 | 2025: +0.064 | 2026: -0.118
- IC CV=0.69, Neg years (linear/tail)=1/0 of 8, Half ratio=0.79, Recency ratio=0.43
- Early IC=+0.1580, Recent IC=+0.0682, 1st-half IC=+0.1123, 2nd-half IC=+0.0885, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.115, Q3_mid=+0.054, Q4=+0.096, Q5_high_vol=+0.184

**`combo_rank_min__first_bar_return__first_bar_sentiment`** (Lock IC=-0.0638, Sharpe=-0.4085)
- Admission: Train IC=+0.2092, Deflated=+0.2091, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.078 | 2016: +0.115 | 2017: +0.042 | 2018: +0.176 | 2019: +0.069 | 2020: +0.027 | 2021: +0.125 | 2022: +0.039 | 2023: +0.127 | 2024: +0.016 | 2025: +0.053 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.133 | 2017: +0.002 | 2018: +0.279 | 2019: +0.063 | 2020: +0.145 | 2021: +0.121 | 2022: +0.337 | 2023: +0.272 | 2024: +0.142 | 2025: +0.188 | 2026: -0.104
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.28
- Early IC=+0.1227, Recent IC=+0.0347, 1st-half IC=+0.0982, 2nd-half IC=+0.0594, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.082, Q3_mid=+0.038, Q4=+0.077, Q5_high_vol=+0.140

**`combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=-0.0297, Sharpe=-0.2989)
- Admission: Train IC=+0.2135, Deflated=+0.2135, IR=0.62, Mono=0.73, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.106 | 2017: -0.070 | 2018: +0.209 | 2019: +0.090 | 2020: +0.068 | 2021: +0.151 | 2022: +0.081 | 2023: +0.111 | 2024: +0.028 | 2025: +0.058 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.200 | 2017: -0.050 | 2018: +0.446 | 2019: +0.316 | 2020: +0.053 | 2021: +0.345 | 2022: +0.240 | 2023: +0.054 | 2024: +0.207 | 2025: +0.098 | 2026: +0.130
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.29
- Early IC=+0.1496, Recent IC=+0.0428, 1st-half IC=+0.1279, 2nd-half IC=+0.0791, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.018, Q2=+0.065, Q3_mid=+0.047, Q4=+0.088, Q5_high_vol=+0.259

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0308, Sharpe=-0.1479)
- Admission: Train IC=+0.2192, Deflated=+0.2193, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.110 | 2017: -0.022 | 2018: +0.226 | 2019: +0.105 | 2020: +0.052 | 2021: +0.162 | 2022: +0.066 | 2023: +0.125 | 2024: +0.029 | 2025: +0.073 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.146 | 2017: -0.090 | 2018: +0.391 | 2019: +0.279 | 2020: +0.113 | 2021: +0.379 | 2022: +0.198 | 2023: +0.155 | 2024: +0.152 | 2025: +0.237 | 2026: +0.104
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.31
- Early IC=+0.1654, Recent IC=+0.0513, 1st-half IC=+0.1346, 2nd-half IC=+0.0838, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.084, Q3_mid=+0.049, Q4=+0.096, Q5_high_vol=+0.243

**`first_bar_return`** (Lock IC=-0.0827, Sharpe=+0.0937)
- Admission: Train IC=+0.1961, Deflated=+0.1962, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.095 | 2017: +0.061 | 2018: +0.191 | 2019: +0.095 | 2020: +0.014 | 2021: +0.121 | 2022: +0.040 | 2023: +0.142 | 2024: +0.029 | 2025: +0.055 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.198 | 2016: -0.089 | 2017: +0.049 | 2018: +0.237 | 2019: +0.141 | 2020: +0.237 | 2021: +0.277 | 2022: +0.340 | 2023: +0.278 | 2024: +0.201 | 2025: +0.144 | 2026: -0.129
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.30
- Early IC=+0.1432, Recent IC=+0.0424, 1st-half IC=+0.1070, 2nd-half IC=+0.0663, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.096, Q3_mid=+0.042, Q4=+0.084, Q5_high_vol=+0.159

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0169, Sharpe=+0.1548)
- Admission: Train IC=+0.2339, Deflated=+0.2337, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.109 | 2017: -0.076 | 2018: +0.171 | 2019: +0.084 | 2020: +0.074 | 2021: +0.154 | 2022: +0.090 | 2023: +0.095 | 2024: +0.025 | 2025: +0.042 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.225 | 2017: -0.037 | 2018: +0.413 | 2019: +0.183 | 2020: +0.205 | 2021: +0.414 | 2022: +0.269 | 2023: +0.165 | 2024: +0.191 | 2025: +0.119 | 2026: +0.187
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.26
- Early IC=+0.1272, Recent IC=+0.0337, 1st-half IC=+0.1208, 2nd-half IC=+0.0682, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.049, Q3_mid=+0.045, Q4=+0.066, Q5_high_vol=+0.235

**`combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=-0.0023, Sharpe=+0.4698)
- Admission: Train IC=+0.1891, Deflated=+0.1890, IR=0.59, Mono=0.72, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.083 | 2017: -0.074 | 2018: +0.183 | 2019: +0.096 | 2020: +0.051 | 2021: +0.146 | 2022: +0.067 | 2023: +0.096 | 2024: +0.018 | 2025: +0.056 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.165 | 2017: -0.128 | 2018: +0.433 | 2019: +0.337 | 2020: +0.101 | 2021: +0.297 | 2022: +0.169 | 2023: +0.029 | 2024: +0.064 | 2025: +0.182 | 2026: +0.134
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.27
- Early IC=+0.1397, Recent IC=+0.0372, 1st-half IC=+0.1183, 2nd-half IC=+0.0744, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.90, neg years=2)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.063, Q3_mid=+0.039, Q4=+0.089, Q5_high_vol=+0.242

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0293, Sharpe=+0.7925)
- Admission: Train IC=+0.1943, Deflated=+0.1946, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.096 | 2017: -0.072 | 2018: +0.144 | 2019: +0.091 | 2020: +0.062 | 2021: +0.138 | 2022: +0.048 | 2023: +0.132 | 2024: +0.044 | 2025: +0.060 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.312 | 2016: -0.044 | 2017: -0.042 | 2018: +0.223 | 2019: +0.226 | 2020: +0.119 | 2021: +0.429 | 2022: +0.245 | 2023: +0.115 | 2024: +0.334 | 2025: +0.057 | 2026: +0.045
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.44
- Early IC=+0.1173, Recent IC=+0.0519, 1st-half IC=+0.1061, 2nd-half IC=+0.0746, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.067, Q3_mid=+0.070, Q4=+0.036, Q5_high_vol=+0.221

**`combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=-0.0121, Sharpe=+0.8779)
- Admission: Train IC=+0.1844, Deflated=+0.1844, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.057 | 2017: -0.081 | 2018: +0.173 | 2019: +0.115 | 2020: +0.042 | 2021: +0.142 | 2022: +0.020 | 2023: +0.105 | 2024: +0.038 | 2025: +0.060 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.089 | 2017: -0.220 | 2018: +0.375 | 2019: +0.374 | 2020: +0.100 | 2021: +0.234 | 2022: +0.149 | 2023: +0.049 | 2024: +0.309 | 2025: +0.003 | 2026: +0.337
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.34
- Early IC=+0.1438, Recent IC=+0.0494, 1st-half IC=+0.1180, 2nd-half IC=+0.0704, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.90, neg years=2)
- Regime ICs: Q1_low_vol=-0.014, Q2=+0.075, Q3_mid=+0.072, Q4=+0.092, Q5_high_vol=+0.212

### 500ETF — `single` False Positives

**`combo_rank_max__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=-0.0914, Sharpe=-3.3937)
- Admission: Train IC=+0.2028, Deflated=+0.2021, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.107 | 2017: +0.208 | 2018: +0.218 | 2019: +0.104 | 2020: +0.126 | 2021: +0.123 | 2022: +0.115 | 2023: +0.089 | 2024: +0.131 | 2025: +0.123 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.424 | 2016: -0.156 | 2017: +0.242 | 2018: +0.210 | 2019: +0.275 | 2020: +0.194 | 2021: +0.188 | 2022: +0.298 | 2023: +0.373 | 2024: +0.219 | 2025: +0.003 | 2026: -0.427
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=0.80
- Early IC=+0.1592, Recent IC=+0.1270, 1st-half IC=+0.1388, 2nd-half IC=+0.1184, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.066, Q3_mid=+0.140, Q4=+0.134, Q5_high_vol=+0.176

**`combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=-0.0012, Sharpe=-3.2911)
- Admission: Train IC=+0.2130, Deflated=+0.2123, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.130 | 2017: +0.183 | 2018: +0.188 | 2019: +0.116 | 2020: +0.111 | 2021: +0.074 | 2022: +0.066 | 2023: +0.063 | 2024: +0.084 | 2025: +0.139 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.365 | 2016: +0.180 | 2017: +0.358 | 2018: +0.151 | 2019: +0.248 | 2020: +0.140 | 2021: +0.053 | 2022: +0.295 | 2023: +0.066 | 2024: +0.057 | 2025: +0.131 | 2026: -0.433
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.74
- Early IC=+0.1519, Recent IC=+0.1117, 1st-half IC=+0.1186, 2nd-half IC=+0.0933, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.128, Q2=-0.009, Q3_mid=+0.100, Q4=+0.133, Q5_high_vol=+0.166

**`vwap_close_divergence_trend`** (Lock IC=-0.0940, Sharpe=-3.2742)
- Admission: Train IC=+0.1609, Deflated=+0.1597, IR=0.63, Mono=0.73, p=0.0008, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.023 | 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107 | 2024: +0.092 | 2025: +0.133 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.081 | 2016: +0.019 | 2017: +0.138 | 2018: +0.210 | 2019: +0.269 | 2020: +0.030 | 2021: +0.253 | 2022: +0.060 | 2023: +0.292 | 2024: +0.110 | 2025: +0.182 | 2026: -0.357
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.52, Recency ratio=1.54
- Early IC=+0.0728, Recent IC=+0.1122, 1st-half IC=+0.0748, 2nd-half IC=+0.1139, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.098, Q3_mid=+0.143, Q4=+0.060, Q5_high_vol=+0.081

**`combo_rank_max__net_volume_flow__first_bar_sentiment`** (Lock IC=-0.0367, Sharpe=-3.0969)
- Admission: Train IC=+0.1819, Deflated=+0.1817, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.048 | 2017: +0.073 | 2018: +0.174 | 2019: +0.107 | 2020: +0.078 | 2021: +0.117 | 2022: +0.110 | 2023: +0.060 | 2024: +0.109 | 2025: +0.080 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.134 | 2016: -0.210 | 2017: +0.088 | 2018: +0.249 | 2019: +0.227 | 2020: +0.232 | 2021: +0.129 | 2022: +0.240 | 2023: +0.297 | 2024: +0.359 | 2025: +0.037 | 2026: -0.316
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.67
- Early IC=+0.1406, Recent IC=+0.0945, 1st-half IC=+0.1113, 2nd-half IC=+0.0964, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.027, Q3_mid=+0.148, Q4=+0.130, Q5_high_vol=+0.122

**`early_order_flow_imbalance`** (Lock IC=-0.1345, Sharpe=-3.0824)
- Admission: Train IC=+0.2192, Deflated=+0.2174, IR=0.58, Mono=0.74, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.093 | 2016: -0.043 | 2017: +0.093 | 2018: +0.101 | 2019: +0.121 | 2020: +0.038 | 2021: +0.122 | 2022: +0.141 | 2023: +0.079 | 2024: +0.107 | 2025: +0.091 | 2026: -0.135
- Yearly Tail ICs:   2015: +0.234 | 2016: -0.073 | 2017: +0.091 | 2018: +0.296 | 2019: +0.233 | 2020: +0.049 | 2021: +0.226 | 2022: +0.337 | 2023: +0.131 | 2024: +0.366 | 2025: +0.046 | 2026: -0.113
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=0.89
- Early IC=+0.1107, Recent IC=+0.0989, 1st-half IC=+0.0919, 2nd-half IC=+0.1108, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.057, Q3_mid=+0.115, Q4=+0.100, Q5_high_vol=+0.091

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0114, Sharpe=-2.9407)
- Admission: Train IC=+0.1677, Deflated=+0.1676, IR=0.48, Mono=0.70, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.150 | 2017: +0.182 | 2018: +0.240 | 2019: +0.135 | 2020: +0.137 | 2021: +0.083 | 2022: +0.102 | 2023: +0.072 | 2024: +0.083 | 2025: +0.097 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.302 | 2017: +0.378 | 2018: +0.505 | 2019: +0.129 | 2020: +0.123 | 2021: +0.004 | 2022: +0.124 | 2023: +0.117 | 2024: +0.064 | 2025: -0.049 | 2026: -0.277
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.48
- Early IC=+0.1874, Recent IC=+0.0902, 1st-half IC=+0.1480, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.003, Q3_mid=+0.098, Q4=+0.131, Q5_high_vol=+0.206

**`combo_sig_product__volatility_expansion_trend_vector__first_bar_return`** (Lock IC=-0.1430, Sharpe=-2.8810)
- Admission: Train IC=+0.1833, Deflated=+0.1815, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.006 | 2017: +0.151 | 2018: +0.174 | 2019: +0.085 | 2020: +0.041 | 2021: +0.092 | 2022: +0.103 | 2023: +0.083 | 2024: +0.111 | 2025: +0.161 | 2026: -0.143
- Yearly Tail ICs:   2015: +0.206 | 2016: -0.060 | 2017: +0.180 | 2018: +0.332 | 2019: +0.150 | 2020: +0.119 | 2021: +0.242 | 2022: +0.180 | 2023: +0.081 | 2024: +0.193 | 2025: +0.312 | 2026: -0.386
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.05
- Early IC=+0.1299, Recent IC=+0.1362, 1st-half IC=+0.0957, 2nd-half IC=+0.1206, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.097, Q3_mid=+0.147, Q4=+0.111, Q5_high_vol=+0.145

**`combo_sig_product__net_volume_flow__first_bar_return`** (Lock IC=-0.1006, Sharpe=-2.8810)
- Admission: Train IC=+0.1763, Deflated=+0.1758, IR=0.48, Mono=0.66, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.022 | 2017: +0.154 | 2018: +0.199 | 2019: +0.138 | 2020: +0.069 | 2021: +0.044 | 2022: +0.045 | 2023: +0.048 | 2024: +0.055 | 2025: +0.108 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.237 | 2016: -0.042 | 2017: +0.209 | 2018: +0.425 | 2019: +0.231 | 2020: +0.166 | 2021: +0.145 | 2022: +0.133 | 2023: +0.040 | 2024: +0.160 | 2025: +0.159 | 2026: -0.386
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.48
- Early IC=+0.1680, Recent IC=+0.0814, 1st-half IC=+0.1125, 2nd-half IC=+0.0622, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.004, Q3_mid=+0.093, Q4=+0.096, Q5_high_vol=+0.125

**`always_in_trend_persistence`** (Lock IC=-0.1600, Sharpe=-2.7442)
- Admission: Train IC=+0.1730, Deflated=+0.1705, IR=0.54, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.057 | 2016: -0.034 | 2017: +0.074 | 2018: +0.070 | 2019: +0.049 | 2020: +0.046 | 2021: +0.111 | 2022: +0.147 | 2023: +0.073 | 2024: +0.098 | 2025: +0.093 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.018 | 2016: -0.163 | 2017: +0.111 | 2018: +0.265 | 2019: +0.033 | 2020: +0.028 | 2021: +0.187 | 2022: +0.244 | 2023: +0.235 | 2024: +0.410 | 2025: -0.004 | 2026: -0.090
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=1.58, Recency ratio=1.60
- Early IC=+0.0594, Recent IC=+0.0953, 1st-half IC=+0.0680, 2nd-half IC=+0.1072, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.057, Q3_mid=+0.113, Q4=+0.094, Q5_high_vol=+0.053

**`vwap_trend_channel_slope`** (Lock IC=-0.0312, Sharpe=-2.6274)
- Admission: Train IC=+0.1273, Deflated=+0.1271, IR=0.57, Mono=0.69, p=0.0100, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.20, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.29
- Early IC=+0.0767, Recent IC=+0.0989, 1st-half IC=+0.0768, 2nd-half IC=+0.1042, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.085, Q3_mid=+0.127, Q4=+0.050, Q5_high_vol=+0.097

**`num_up_bars`** (Lock IC=-0.0474, Sharpe=-2.5885)
- Admission: Train IC=+0.1400, Deflated=+0.1391, IR=0.39, Mono=0.67, p=0.0048, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.077 | 2016: +0.103 | 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141 | 2025: +0.117 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.253 | 2017: +0.002 | 2018: +0.082 | 2019: +0.121 | 2020: +0.184 | 2021: -0.075 | 2022: +0.221 | 2023: +0.122 | 2024: +0.211 | 2025: -0.019 | 2026: -0.077
- IC CV=0.35, Neg years (linear/tail)=0/2 of 8, Half ratio=1.67, Recency ratio=1.35
- Early IC=+0.0951, Recent IC=+0.1286, 1st-half IC=+0.0751, 2nd-half IC=+0.1257, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.113, Q3_mid=+0.140, Q4=+0.079, Q5_high_vol=+0.093

**`combo_rank_min__first_bar_sentiment__bar_ret_0`** (Lock IC=-0.0261, Sharpe=-2.5653)
- Admission: Train IC=+0.1946, Deflated=+0.1937, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.148 | 2017: +0.146 | 2018: +0.232 | 2019: +0.124 | 2020: +0.121 | 2021: +0.095 | 2022: +0.065 | 2023: +0.058 | 2024: +0.102 | 2025: +0.125 | 2026: -0.026
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.202 | 2017: +0.372 | 2018: +0.527 | 2019: +0.070 | 2020: +0.250 | 2021: +0.008 | 2022: +0.268 | 2023: -0.001 | 2024: +0.153 | 2025: +0.160 | 2026: -0.223
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.64
- Early IC=+0.1779, Recent IC=+0.1135, 1st-half IC=+0.1389, 2nd-half IC=+0.0898, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.002, Q3_mid=+0.104, Q4=+0.122, Q5_high_vol=+0.181

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=-0.0526, Sharpe=-2.4640)
- Admission: Train IC=+0.1914, Deflated=+0.1914, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.062 | 2017: +0.234 | 2018: +0.135 | 2019: +0.087 | 2020: +0.163 | 2021: +0.092 | 2022: +0.107 | 2023: +0.115 | 2024: +0.080 | 2025: +0.097 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.063 | 2017: +0.387 | 2018: +0.242 | 2019: +0.055 | 2020: +0.236 | 2021: +0.282 | 2022: +0.218 | 2023: +0.068 | 2024: +0.292 | 2025: +0.095 | 2026: -0.203
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.79
- Early IC=+0.1109, Recent IC=+0.0880, 1st-half IC=+0.1187, 2nd-half IC=+0.1021, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.068, Q3_mid=+0.161, Q4=+0.084, Q5_high_vol=+0.135

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=-0.0473, Sharpe=-2.4121)
- Admission: Train IC=+0.1735, Deflated=+0.1725, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.63
- Yearly Linear ICs: 2015: +0.140 | 2016: -0.050 | 2017: +0.104 | 2018: +0.030 | 2019: +0.077 | 2020: +0.065 | 2021: +0.059 | 2022: +0.033 | 2023: +0.007 | 2024: +0.197 | 2025: +0.019 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.369 | 2016: -0.078 | 2017: +0.131 | 2018: +0.261 | 2019: +0.278 | 2020: +0.012 | 2021: +0.267 | 2022: +0.172 | 2023: +0.001 | 2024: +0.354 | 2025: +0.083 | 2026: -0.162
- IC CV=0.92, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=2.02
- Early IC=+0.0534, Recent IC=+0.1078, 1st-half IC=+0.0500, 2nd-half IC=+0.0728, Neg regimes=1/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.99, neg years=1)
- Regime ICs: Q1_low_vol=-0.021, Q2=+0.018, Q3_mid=+0.154, Q4=+0.090, Q5_high_vol=+0.039

**`volatility_expansion_trend_vector`** (Lock IC=-0.0850, Sharpe=-2.3631)
- Admission: Train IC=+0.2278, Deflated=+0.2263, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.061 | 2017: +0.201 | 2018: +0.129 | 2019: +0.076 | 2020: +0.097 | 2021: +0.073 | 2022: +0.093 | 2023: +0.089 | 2024: +0.123 | 2025: +0.155 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.306 | 2016: -0.052 | 2017: +0.291 | 2018: +0.219 | 2019: +0.292 | 2020: +0.226 | 2021: +0.227 | 2022: +0.241 | 2023: +0.284 | 2024: +0.228 | 2025: +0.065 | 2026: -0.099
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.29, Recency ratio=1.36
- Early IC=+0.1024, Recent IC=+0.1390, 1st-half IC=+0.0933, 2nd-half IC=+0.1204, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.081, Q3_mid=+0.139, Q4=+0.108, Q5_high_vol=+0.128

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0689, Sharpe=-2.3631)
- Admission: Train IC=+0.2158, Deflated=+0.2159, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.079 | 2017: +0.211 | 2018: +0.167 | 2019: +0.118 | 2020: +0.167 | 2021: +0.051 | 2022: +0.112 | 2023: +0.120 | 2024: +0.091 | 2025: +0.103 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.454 | 2016: -0.083 | 2017: +0.313 | 2018: +0.224 | 2019: +0.292 | 2020: +0.226 | 2021: +0.197 | 2022: +0.241 | 2023: +0.284 | 2024: +0.228 | 2025: -0.037 | 2026: -0.099
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.68
- Early IC=+0.1425, Recent IC=+0.0971, 1st-half IC=+0.1291, 2nd-half IC=+0.1115, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31, neg years=0)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.081, Q3_mid=+0.173, Q4=+0.104, Q5_high_vol=+0.155

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0132, Sharpe=-2.3509)
- Admission: Train IC=+0.2028, Deflated=+0.2029, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.094 | 2017: +0.235 | 2018: +0.223 | 2019: +0.107 | 2020: +0.153 | 2021: +0.154 | 2022: +0.123 | 2023: +0.098 | 2024: +0.145 | 2025: +0.078 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.103 | 2017: +0.148 | 2018: +0.362 | 2019: +0.318 | 2020: +0.098 | 2021: +0.316 | 2022: +0.211 | 2023: -0.005 | 2024: +0.273 | 2025: +0.022 | 2026: -0.232
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.68
- Early IC=+0.1651, Recent IC=+0.1117, 1st-half IC=+0.1558, 2nd-half IC=+0.1182, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31, neg years=0)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.065, Q3_mid=+0.128, Q4=+0.142, Q5_high_vol=+0.223

**`combo_max__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=-0.0520, Sharpe=-2.3176)
- Admission: Train IC=+0.2174, Deflated=+0.2166, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.116 | 2017: +0.167 | 2018: +0.160 | 2019: +0.083 | 2020: +0.113 | 2021: +0.137 | 2022: +0.127 | 2023: +0.051 | 2024: +0.118 | 2025: +0.119 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.375 | 2016: -0.018 | 2017: +0.157 | 2018: +0.189 | 2019: +0.298 | 2020: +0.207 | 2021: +0.181 | 2022: +0.229 | 2023: +0.145 | 2024: +0.243 | 2025: +0.063 | 2026: -0.193
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.97
- Early IC=+0.1216, Recent IC=+0.1183, 1st-half IC=+0.1174, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.038, Q3_mid=+0.145, Q4=+0.134, Q5_high_vol=+0.152

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=-0.0646, Sharpe=-2.3002)
- Admission: Train IC=+0.2178, Deflated=+0.2170, IR=0.69, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.76, Recency ratio=0.71
- Early IC=+0.1800, Recent IC=+0.1273, 1st-half IC=+0.1492, 2nd-half IC=+0.1140, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.034, Q3_mid=+0.117, Q4=+0.128, Q5_high_vol=+0.226

**`combo_mean__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=-0.0523, Sharpe=-2.2648)
- Admission: Train IC=+0.2381, Deflated=+0.2373, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.096 | 2017: +0.183 | 2018: +0.186 | 2019: +0.108 | 2020: +0.104 | 2021: +0.105 | 2022: +0.105 | 2023: +0.081 | 2024: +0.117 | 2025: +0.143 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.392 | 2016: -0.099 | 2017: +0.140 | 2018: +0.276 | 2019: +0.342 | 2020: +0.187 | 2021: +0.123 | 2022: +0.279 | 2023: +0.347 | 2024: +0.131 | 2025: +0.134 | 2026: -0.091
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.88
- Early IC=+0.1470, Recent IC=+0.1299, 1st-half IC=+0.1198, 2nd-half IC=+0.1164, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.041, Q3_mid=+0.141, Q4=+0.138, Q5_high_vol=+0.157

**`combo_max__close_vs_open_range__early_body_momentum`** (Lock IC=-0.0947, Sharpe=-2.2083)
- Admission: Train IC=+0.1723, Deflated=+0.1708, IR=0.38, Mono=0.66, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.147 | 2016: +0.065 | 2017: +0.161 | 2018: +0.111 | 2019: +0.041 | 2020: +0.097 | 2021: +0.059 | 2022: +0.103 | 2023: +0.078 | 2024: +0.129 | 2025: +0.144 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.136 | 2017: +0.209 | 2018: +0.116 | 2019: +0.095 | 2020: +0.228 | 2021: +0.234 | 2022: +0.144 | 2023: +0.107 | 2024: +0.340 | 2025: +0.035 | 2026: -0.064
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.59, Recency ratio=1.80
- Early IC=+0.0759, Recent IC=+0.1367, 1st-half IC=+0.0765, 2nd-half IC=+0.1220, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.079, Q3_mid=+0.152, Q4=+0.097, Q5_high_vol=+0.082

**`combo_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.0124, Sharpe=-2.1578)
- Admission: Train IC=+0.2336, Deflated=+0.2334, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.097 | 2017: +0.202 | 2018: +0.222 | 2019: +0.164 | 2020: +0.136 | 2021: +0.115 | 2022: +0.066 | 2023: +0.092 | 2024: +0.144 | 2025: +0.107 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.416 | 2016: -0.130 | 2017: +0.321 | 2018: +0.292 | 2019: +0.280 | 2020: +0.041 | 2021: +0.285 | 2022: +0.159 | 2023: +0.092 | 2024: +0.341 | 2025: +0.113 | 2026: -0.155
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.65
- Early IC=+0.1930, Recent IC=+0.1253, 1st-half IC=+0.1543, 2nd-half IC=+0.1104, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.017, Q3_mid=+0.163, Q4=+0.165, Q5_high_vol=+0.193

**`combo_tri_median__max_up_ret__net_volume_flow__body_size_progression`** (Lock IC=-0.0933, Sharpe=-2.1447)
- Admission: Train IC=+0.1797, Deflated=+0.1789, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.084 | 2017: +0.097 | 2018: +0.141 | 2019: +0.071 | 2020: +0.077 | 2021: +0.107 | 2022: +0.120 | 2023: +0.115 | 2024: +0.112 | 2025: +0.141 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.162 | 2017: +0.119 | 2018: +0.224 | 2019: +0.145 | 2020: +0.125 | 2021: +0.287 | 2022: +0.099 | 2023: +0.156 | 2024: +0.179 | 2025: +0.146 | 2026: -0.395
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=1.28, Recency ratio=1.19
- Early IC=+0.1063, Recent IC=+0.1269, 1st-half IC=+0.0973, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.070, Q3_mid=+0.144, Q4=+0.112, Q5_high_vol=+0.129

**`first_30min_return`** (Lock IC=-0.1128, Sharpe=-2.1381)
- Admission: Train IC=+0.1826, Deflated=+0.1808, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.32, Recency ratio=1.35
- Early IC=+0.1053, Recent IC=+0.1420, 1st-half IC=+0.0956, 2nd-half IC=+0.1262, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.093, Q3_mid=+0.140, Q4=+0.100, Q5_high_vol=+0.130

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=-0.0695, Sharpe=-2.1354)
- Admission: Train IC=+0.1709, Deflated=+0.1713, IR=0.57, Mono=0.74, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.142 | 2017: +0.115 | 2018: +0.276 | 2019: +0.086 | 2020: +0.115 | 2021: +0.110 | 2022: +0.109 | 2023: +0.023 | 2024: +0.102 | 2025: +0.094 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.142 | 2016: +0.092 | 2017: +0.306 | 2018: +0.468 | 2019: +0.081 | 2020: +0.215 | 2021: +0.204 | 2022: -0.008 | 2023: +0.021 | 2024: +0.172 | 2025: +0.155 | 2026: -0.305
- IC CV=0.59, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.54
- Early IC=+0.1807, Recent IC=+0.0980, 1st-half IC=+0.1425, 2nd-half IC=+0.0871, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.028, Q3_mid=+0.058, Q4=+0.132, Q5_high_vol=+0.176

**`combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=-0.0655, Sharpe=-2.0913)
- Admission: Train IC=+0.2060, Deflated=+0.2052, IR=0.67, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.044 | 2017: +0.220 | 2018: +0.157 | 2019: +0.078 | 2020: +0.136 | 2021: +0.094 | 2022: +0.085 | 2023: +0.101 | 2024: +0.139 | 2025: +0.116 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.249 | 2017: +0.377 | 2018: +0.238 | 2019: +0.148 | 2020: +0.220 | 2021: +0.247 | 2022: +0.181 | 2023: +0.201 | 2024: +0.324 | 2025: +0.081 | 2026: -0.169
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=1.08
- Early IC=+0.1177, Recent IC=+0.1271, 1st-half IC=+0.1181, 2nd-half IC=+0.1163, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.061, Q3_mid=+0.161, Q4=+0.117, Q5_high_vol=+0.149

**`combo_min__net_volume_flow__first_bar_sentiment`** (Lock IC=-0.0444, Sharpe=-2.0572)
- Admission: Train IC=+0.2859, Deflated=+0.2850, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.108 | 2017: +0.172 | 2018: +0.177 | 2019: +0.113 | 2020: +0.117 | 2021: +0.091 | 2022: +0.103 | 2023: +0.090 | 2024: +0.124 | 2025: +0.138 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.201 | 2016: -0.007 | 2017: +0.200 | 2018: +0.228 | 2019: +0.187 | 2020: +0.297 | 2021: +0.085 | 2022: +0.227 | 2023: +0.291 | 2024: +0.277 | 2025: +0.219 | 2026: -0.079
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.90
- Early IC=+0.1450, Recent IC=+0.1311, 1st-half IC=+0.1209, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.041, Q3_mid=+0.140, Q4=+0.131, Q5_high_vol=+0.156

**`combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=-0.0906, Sharpe=-2.0531)
- Admission: Train IC=+0.2109, Deflated=+0.2098, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.071 | 2017: +0.169 | 2018: +0.120 | 2019: +0.055 | 2020: +0.085 | 2021: +0.098 | 2022: +0.107 | 2023: +0.111 | 2024: +0.139 | 2025: +0.129 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.351 | 2016: +0.230 | 2017: +0.367 | 2018: +0.306 | 2019: +0.105 | 2020: +0.162 | 2021: +0.224 | 2022: +0.212 | 2023: +0.247 | 2024: +0.300 | 2025: -0.011 | 2026: -0.042
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=1.43, Recency ratio=1.53
- Early IC=+0.0877, Recent IC=+0.1339, 1st-half IC=+0.0901, 2nd-half IC=+0.1284, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.082, Q3_mid=+0.140, Q4=+0.097, Q5_high_vol=+0.139

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`** (Lock IC=-0.0468, Sharpe=-2.0328)
- Admission: Train IC=+0.2196, Deflated=+0.2187, IR=0.75, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.075 | 2017: +0.218 | 2018: +0.208 | 2019: +0.105 | 2020: +0.158 | 2021: +0.122 | 2022: +0.087 | 2023: +0.120 | 2024: +0.125 | 2025: +0.132 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.490 | 2016: +0.345 | 2017: +0.238 | 2018: +0.415 | 2019: +0.073 | 2020: +0.224 | 2021: +0.291 | 2022: +0.191 | 2023: +0.287 | 2024: +0.245 | 2025: +0.012 | 2026: -0.186
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.82
- Early IC=+0.1565, Recent IC=+0.1284, 1st-half IC=+0.1466, 2nd-half IC=+0.1260, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.062, Q3_mid=+0.160, Q4=+0.140, Q5_high_vol=+0.195

**`combo_sig_product__max_up_ret__early_body_momentum`** (Lock IC=-0.0107, Sharpe=-2.0201)
- Admission: Train IC=+0.1982, Deflated=+0.1985, IR=0.50, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.216 | 2017: +0.143 | 2018: +0.162 | 2019: +0.059 | 2020: +0.134 | 2021: +0.126 | 2022: +0.085 | 2023: +0.125 | 2024: +0.150 | 2025: +0.113 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.196 | 2017: +0.191 | 2018: +0.176 | 2019: +0.131 | 2020: +0.310 | 2021: +0.277 | 2022: +0.068 | 2023: +0.123 | 2024: +0.292 | 2025: +0.004 | 2026: -0.155
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.19
- Early IC=+0.1109, Recent IC=+0.1316, 1st-half IC=+0.1200, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.078, Q3_mid=+0.129, Q4=+0.086, Q5_high_vol=+0.187

**`combo_rank_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0104, Sharpe=-2.0137)
- Admission: Train IC=+0.2029, Deflated=+0.2025, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.275 | 2016: +0.102 | 2017: +0.200 | 2018: +0.210 | 2019: +0.141 | 2020: +0.146 | 2021: +0.129 | 2022: +0.045 | 2023: +0.112 | 2024: +0.158 | 2025: +0.098 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.503 | 2016: +0.293 | 2017: +0.257 | 2018: +0.337 | 2019: +0.215 | 2020: +0.184 | 2021: +0.339 | 2022: +0.100 | 2023: +0.140 | 2024: +0.207 | 2025: +0.026 | 2026: -0.084
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.73
- Early IC=+0.1764, Recent IC=+0.1292, 1st-half IC=+0.1535, 2nd-half IC=+0.1141, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31, neg years=0)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.047, Q3_mid=+0.174, Q4=+0.120, Q5_high_vol=+0.208

**`combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression`** (Lock IC=-0.0592, Sharpe=-1.9999)
- Admission: Train IC=+0.2469, Deflated=+0.2461, IR=0.76, Mono=0.81, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.054 | 2017: +0.132 | 2018: +0.132 | 2019: +0.095 | 2020: +0.121 | 2021: +0.106 | 2022: +0.097 | 2023: +0.111 | 2024: +0.145 | 2025: +0.132 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.350 | 2016: +0.136 | 2017: +0.155 | 2018: +0.273 | 2019: +0.217 | 2020: +0.271 | 2021: +0.252 | 2022: +0.320 | 2023: +0.227 | 2024: +0.290 | 2025: +0.026 | 2026: -0.190
- IC CV=0.14, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.22
- Early IC=+0.1135, Recent IC=+0.1385, 1st-half IC=+0.1115, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.070, Q3_mid=+0.152, Q4=+0.128, Q5_high_vol=+0.135

**`combo_min__close_vs_open_range__early_body_momentum`** (Lock IC=-0.0785, Sharpe=-1.9210)
- Admission: Train IC=+0.1744, Deflated=+0.1732, IR=0.42, Mono=0.65, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.064 | 2017: +0.155 | 2018: +0.108 | 2019: +0.052 | 2020: +0.095 | 2021: +0.051 | 2022: +0.112 | 2023: +0.094 | 2024: +0.107 | 2025: +0.142 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.199 | 2017: +0.312 | 2018: +0.237 | 2019: +0.098 | 2020: +0.283 | 2021: +0.226 | 2022: +0.125 | 2023: +0.071 | 2024: +0.225 | 2025: -0.042 | 2026: -0.062
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.52, Recency ratio=1.56
- Early IC=+0.0801, Recent IC=+0.1248, 1st-half IC=+0.0779, 2nd-half IC=+0.1187, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.096, Q3_mid=+0.126, Q4=+0.093, Q5_high_vol=+0.102

**`combo_rank_max__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=-0.0686, Sharpe=-1.8069)
- Admission: Train IC=+0.2229, Deflated=+0.2221, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.048 | 2017: +0.216 | 2018: +0.159 | 2019: +0.107 | 2020: +0.105 | 2021: +0.088 | 2022: +0.062 | 2023: +0.047 | 2024: +0.136 | 2025: +0.153 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.350 | 2016: -0.108 | 2017: +0.230 | 2018: +0.127 | 2019: +0.354 | 2020: +0.058 | 2021: +0.265 | 2022: +0.230 | 2023: +0.214 | 2024: +0.304 | 2025: +0.243 | 2026: -0.150
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=1.10
- Early IC=+0.1327, Recent IC=+0.1457, 1st-half IC=+0.1092, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.073, Q3_mid=+0.143, Q4=+0.122, Q5_high_vol=+0.127

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=-0.0337, Sharpe=-1.7738)
- Admission: Train IC=+0.2044, Deflated=+0.2043, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.110 | 2017: +0.192 | 2018: +0.241 | 2019: +0.135 | 2020: +0.113 | 2021: +0.137 | 2022: +0.101 | 2023: +0.097 | 2024: +0.141 | 2025: +0.077 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.127 | 2017: +0.255 | 2018: +0.465 | 2019: +0.112 | 2020: +0.232 | 2021: +0.269 | 2022: +0.107 | 2023: +0.148 | 2024: +0.138 | 2025: +0.043 | 2026: -0.239
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1882, Recent IC=+0.1091, 1st-half IC=+0.1518, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.032, Q3_mid=+0.110, Q4=+0.134, Q5_high_vol=+0.219

**`combo_sig_product__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=-0.0739, Sharpe=-1.7537)
- Admission: Train IC=+0.1786, Deflated=+0.1773, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.021 | 2017: +0.200 | 2018: +0.128 | 2019: +0.130 | 2020: +0.095 | 2021: +0.090 | 2022: +0.085 | 2023: +0.097 | 2024: +0.120 | 2025: +0.212 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.058 | 2016: -0.181 | 2017: +0.203 | 2018: +0.010 | 2019: +0.216 | 2020: +0.106 | 2021: +0.301 | 2022: +0.182 | 2023: +0.141 | 2024: +0.240 | 2025: +0.418 | 2026: -0.270
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.28
- Early IC=+0.1295, Recent IC=+0.1660, 1st-half IC=+0.1100, 2nd-half IC=+0.1328, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.087, Q3_mid=+0.191, Q4=+0.144, Q5_high_vol=+0.119

**`morning_volume_weighted_momentum`** (Lock IC=-0.0906, Sharpe=-1.7423)
- Admission: Train IC=+0.1720, Deflated=+0.1705, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.039 | 2017: +0.203 | 2018: +0.126 | 2019: +0.090 | 2020: +0.097 | 2021: +0.088 | 2022: +0.095 | 2023: +0.096 | 2024: +0.115 | 2025: +0.165 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.078 | 2017: +0.280 | 2018: +0.104 | 2019: +0.039 | 2020: +0.117 | 2021: +0.174 | 2022: +0.149 | 2023: +0.283 | 2024: +0.184 | 2025: +0.241 | 2026: -0.108
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=1.27, Recency ratio=1.29
- Early IC=+0.1081, Recent IC=+0.1398, 1st-half IC=+0.0985, 2nd-half IC=+0.1255, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.098, Q3_mid=+0.146, Q4=+0.100, Q5_high_vol=+0.125

**`combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=-0.0411, Sharpe=-1.7157)
- Admission: Train IC=+0.2235, Deflated=+0.2236, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.066 | 2017: +0.227 | 2018: +0.179 | 2019: +0.102 | 2020: +0.153 | 2021: +0.054 | 2022: +0.121 | 2023: +0.093 | 2024: +0.104 | 2025: +0.115 | 2026: -0.041
- Yearly Tail ICs:   2015: +0.460 | 2016: +0.097 | 2017: +0.227 | 2018: +0.249 | 2019: +0.166 | 2020: +0.274 | 2021: +0.176 | 2022: +0.245 | 2023: +0.334 | 2024: +0.260 | 2025: +0.032 | 2026: -0.115
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.78
- Early IC=+0.1407, Recent IC=+0.1097, 1st-half IC=+0.1213, 2nd-half IC=+0.1163, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31, neg years=0)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.053, Q3_mid=+0.168, Q4=+0.117, Q5_high_vol=+0.145

**`combo_max__net_volume_flow__max_down_ret`** (Lock IC=-0.0643, Sharpe=-1.7123)
- Admission: Train IC=+0.1832, Deflated=+0.1826, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.083 | 2017: +0.206 | 2018: +0.177 | 2019: +0.108 | 2020: +0.113 | 2021: +0.073 | 2022: +0.069 | 2023: +0.045 | 2024: +0.148 | 2025: +0.137 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.162 | 2017: +0.168 | 2018: +0.133 | 2019: +0.191 | 2020: +0.020 | 2021: +0.230 | 2022: +0.274 | 2023: +0.307 | 2024: +0.284 | 2025: +0.058 | 2026: -0.147
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=1.00
- Early IC=+0.1424, Recent IC=+0.1422, 1st-half IC=+0.1128, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.055, Q3_mid=+0.135, Q4=+0.124, Q5_high_vol=+0.124

**`first_bar_return`** (Lock IC=-0.0114, Sharpe=-1.5357)
- Admission: Train IC=+0.1817, Deflated=+0.1816, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.52
- Early IC=+0.1931, Recent IC=+0.0995, 1st-half IC=+0.1410, 2nd-half IC=+0.0829, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.005, Q3_mid=+0.091, Q4=+0.130, Q5_high_vol=+0.169

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`** (Lock IC=-0.0194, Sharpe=-1.4497)
- Admission: Train IC=+0.1973, Deflated=+0.1952, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.088 | 2016: +0.104 | 2017: +0.031 | 2018: +0.108 | 2019: +0.022 | 2020: +0.076 | 2021: -0.011 | 2022: +0.105 | 2023: +0.018 | 2024: +0.052 | 2025: +0.130 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.144 | 2016: +0.139 | 2017: +0.066 | 2018: +0.205 | 2019: +0.105 | 2020: +0.172 | 2021: +0.154 | 2022: +0.196 | 2023: -0.016 | 2024: +0.254 | 2025: +0.184 | 2026: -0.142
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=1.34, Recency ratio=1.40
- Early IC=+0.0650, Recent IC=+0.0911, 1st-half IC=+0.0592, 2nd-half IC=+0.0791, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.076, Q3_mid=+0.090, Q4=+0.033, Q5_high_vol=+0.101

**`combo_min__first_bar_sentiment__bar_ret_0`** (Lock IC=-0.0087, Sharpe=-1.4456)
- Admission: Train IC=+0.2208, Deflated=+0.2205, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.123 | 2017: +0.145 | 2018: +0.225 | 2019: +0.144 | 2020: +0.088 | 2021: +0.102 | 2022: +0.062 | 2023: +0.065 | 2024: +0.122 | 2025: +0.103 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.357 | 2016: -0.009 | 2017: +0.288 | 2018: +0.407 | 2019: +0.319 | 2020: +0.114 | 2021: +0.228 | 2022: +0.278 | 2023: +0.141 | 2024: +0.216 | 2025: +0.025 | 2026: -0.144
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.61
- Early IC=+0.1846, Recent IC=+0.1125, 1st-half IC=+0.1356, 2nd-half IC=+0.0908, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.002, Q3_mid=+0.088, Q4=+0.130, Q5_high_vol=+0.178

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=-0.0206, Sharpe=-1.4352)
- Admission: Train IC=+0.1748, Deflated=+0.1748, IR=0.45, Mono=0.70, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.142 | 2017: +0.075 | 2018: +0.165 | 2019: +0.094 | 2020: +0.135 | 2021: +0.075 | 2022: +0.096 | 2023: +0.080 | 2024: +0.096 | 2025: +0.076 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.075 | 2017: +0.081 | 2018: +0.208 | 2019: +0.185 | 2020: +0.209 | 2021: +0.000 | 2022: +0.172 | 2023: +0.259 | 2024: +0.112 | 2025: +0.086 | 2026: -0.078
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.67
- Early IC=+0.1293, Recent IC=+0.0862, 1st-half IC=+0.1152, 2nd-half IC=+0.0913, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.032, Q3_mid=+0.142, Q4=+0.086, Q5_high_vol=+0.145

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=-0.0323, Sharpe=-1.4349)
- Admission: Train IC=+0.2238, Deflated=+0.2230, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.115 | 2017: +0.228 | 2018: +0.188 | 2019: +0.103 | 2020: +0.143 | 2021: +0.125 | 2022: +0.125 | 2023: +0.104 | 2024: +0.143 | 2025: +0.119 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.556 | 2016: +0.392 | 2017: +0.254 | 2018: +0.305 | 2019: +0.148 | 2020: +0.239 | 2021: +0.410 | 2022: +0.105 | 2023: +0.176 | 2024: +0.194 | 2025: +0.058 | 2026: -0.144
- IC CV=0.20, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.90
- Early IC=+0.1455, Recent IC=+0.1307, 1st-half IC=+0.1363, 2nd-half IC=+0.1356, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.063, Q3_mid=+0.147, Q4=+0.145, Q5_high_vol=+0.215

**`combo_sig_product__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=-0.0019, Sharpe=-1.3928)
- Admission: Train IC=+0.1317, Deflated=+0.1313, IR=0.48, Mono=0.66, p=0.0084, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.043 | 2017: +0.223 | 2018: +0.135 | 2019: +0.137 | 2020: +0.191 | 2021: +0.108 | 2022: +0.022 | 2023: +0.089 | 2024: +0.119 | 2025: +0.136 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.269 | 2016: -0.091 | 2017: +0.205 | 2018: +0.062 | 2019: +0.246 | 2020: +0.060 | 2021: +0.325 | 2022: -0.023 | 2023: +0.128 | 2024: +0.267 | 2025: +0.261 | 2026: -0.174
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.94
- Early IC=+0.1362, Recent IC=+0.1278, 1st-half IC=+0.1386, 2nd-half IC=+0.0953, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.097, Q2=+0.068, Q3_mid=+0.167, Q4=+0.106, Q5_high_vol=+0.151

**`combo_max__close_vs_open_range__max_down_ret`** (Lock IC=-0.0673, Sharpe=-1.3419)
- Admission: Train IC=+0.1657, Deflated=+0.1651, IR=0.49, Mono=0.67, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.061 | 2017: +0.214 | 2018: +0.133 | 2019: +0.094 | 2020: +0.120 | 2021: +0.085 | 2022: +0.061 | 2023: +0.045 | 2024: +0.132 | 2025: +0.151 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.292 | 2016: +0.093 | 2017: +0.257 | 2018: +0.058 | 2019: +0.205 | 2020: +0.044 | 2021: +0.260 | 2022: +0.238 | 2023: +0.162 | 2024: +0.326 | 2025: +0.052 | 2026: -0.005
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=1.25
- Early IC=+0.1134, Recent IC=+0.1418, 1st-half IC=+0.1030, 2nd-half IC=+0.1071, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.080, Q3_mid=+0.138, Q4=+0.126, Q5_high_vol=+0.107

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=-0.0624, Sharpe=-1.3419)
- Admission: Train IC=+0.1519, Deflated=+0.1521, IR=0.49, Mono=0.67, p=0.0020, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.088 | 2017: +0.204 | 2018: +0.154 | 2019: +0.105 | 2020: +0.168 | 2021: +0.053 | 2022: +0.113 | 2023: +0.130 | 2024: +0.087 | 2025: +0.086 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.468 | 2016: +0.140 | 2017: +0.347 | 2018: +0.232 | 2019: +0.181 | 2020: +0.141 | 2021: +0.176 | 2022: +0.055 | 2023: +0.102 | 2024: +0.224 | 2025: -0.029 | 2026: +0.003
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.91, Recency ratio=0.67
- Early IC=+0.1298, Recent IC=+0.0867, 1st-half IC=+0.1213, 2nd-half IC=+0.1107, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31, neg years=0)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.075, Q3_mid=+0.174, Q4=+0.110, Q5_high_vol=+0.133

**`combo_sig_product__net_volume_flow__max_down_ret`** (Lock IC=-0.0458, Sharpe=-1.3179)
- Admission: Train IC=+0.1308, Deflated=+0.1306, IR=0.48, Mono=0.66, p=0.0090, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.043 | 2017: +0.204 | 2018: +0.107 | 2019: +0.130 | 2020: +0.129 | 2021: +0.037 | 2022: +0.036 | 2023: +0.061 | 2024: +0.083 | 2025: +0.141 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.133 | 2016: -0.181 | 2017: +0.165 | 2018: +0.048 | 2019: +0.122 | 2020: +0.047 | 2021: +0.286 | 2022: +0.168 | 2023: +0.079 | 2024: +0.268 | 2025: +0.240 | 2026: -0.124
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.94
- Early IC=+0.1186, Recent IC=+0.1118, 1st-half IC=+0.1023, 2nd-half IC=+0.0812, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.045, Q3_mid=+0.140, Q4=+0.125, Q5_high_vol=+0.075

**`combo_mean__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=-0.0002, Sharpe=-1.2847)
- Admission: Train IC=+0.2190, Deflated=+0.2189, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.091 | 2017: +0.234 | 2018: +0.257 | 2019: +0.155 | 2020: +0.157 | 2021: +0.134 | 2022: +0.084 | 2023: +0.090 | 2024: +0.152 | 2025: +0.090 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.265 | 2016: -0.003 | 2017: +0.219 | 2018: +0.456 | 2019: +0.157 | 2020: +0.230 | 2021: +0.302 | 2022: +0.205 | 2023: +0.161 | 2024: +0.225 | 2025: +0.049 | 2026: -0.224
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.2060, Recent IC=+0.1207, 1st-half IC=+0.1702, 2nd-half IC=+0.1100, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.035, Q3_mid=+0.142, Q4=+0.155, Q5_high_vol=+0.210

**`combo_mean__close_vs_open_range__bar_ret_0`** (Lock IC=-0.0383, Sharpe=-1.2349)
- Admission: Train IC=+0.2414, Deflated=+0.2405, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.094 | 2017: +0.212 | 2018: +0.196 | 2019: +0.106 | 2020: +0.116 | 2021: +0.098 | 2022: +0.096 | 2023: +0.079 | 2024: +0.154 | 2025: +0.119 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.026 | 2017: +0.245 | 2018: +0.357 | 2019: +0.140 | 2020: +0.182 | 2021: +0.367 | 2022: +0.278 | 2023: +0.233 | 2024: +0.329 | 2025: +0.057 | 2026: -0.203
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.91
- Early IC=+0.1510, Recent IC=+0.1367, 1st-half IC=+0.1278, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.055, Q3_mid=+0.130, Q4=+0.134, Q5_high_vol=+0.168

**`combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=-0.0123, Sharpe=-1.0051)
- Admission: Train IC=+0.2027, Deflated=+0.2022, IR=0.71, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.226 | 2018: +0.241 | 2019: +0.145 | 2020: +0.142 | 2021: +0.169 | 2022: +0.092 | 2023: +0.108 | 2024: +0.150 | 2025: +0.088 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.336 | 2016: -0.072 | 2017: +0.187 | 2018: +0.368 | 2019: +0.218 | 2020: +0.248 | 2021: +0.353 | 2022: +0.155 | 2023: +0.156 | 2024: +0.280 | 2025: -0.017 | 2026: -0.111
- IC CV=0.33, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.60
- Early IC=+0.1937, Recent IC=+0.1167, 1st-half IC=+0.1654, 2nd-half IC=+0.1172, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.037, Q3_mid=+0.145, Q4=+0.138, Q5_high_vol=+0.211

**`combo_min__trend_bar_close_consistency__first_bar_return`** (Lock IC=-0.0156, Sharpe=-0.9099)
- Admission: Train IC=+0.2116, Deflated=+0.2109, IR=0.65, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.055 | 2017: +0.156 | 2018: +0.155 | 2019: +0.101 | 2020: +0.048 | 2021: +0.050 | 2022: +0.064 | 2023: +0.075 | 2024: +0.125 | 2025: +0.123 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.025 | 2017: +0.341 | 2018: +0.401 | 2019: +0.086 | 2020: +0.043 | 2021: +0.313 | 2022: +0.266 | 2023: +0.043 | 2024: +0.325 | 2025: +0.165 | 2026: +0.022
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.97
- Early IC=+0.1282, Recent IC=+0.1240, 1st-half IC=+0.0896, 2nd-half IC=+0.0991, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.018, Q3_mid=+0.107, Q4=+0.099, Q5_high_vol=+0.130

**`combo_rank_min__max_up_ret__bar_ret_0`** (Lock IC=-0.0007, Sharpe=-0.8149)
- Admission: Train IC=+0.2046, Deflated=+0.2049, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.097 | 2017: +0.204 | 2018: +0.243 | 2019: +0.143 | 2020: +0.122 | 2021: +0.089 | 2022: +0.070 | 2023: +0.076 | 2024: +0.101 | 2025: +0.085 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.160 | 2016: +0.150 | 2017: +0.211 | 2018: +0.461 | 2019: +0.219 | 2020: +0.252 | 2021: +0.194 | 2022: +0.005 | 2023: +0.056 | 2024: +0.209 | 2025: +0.141 | 2026: -0.124
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.49
- Early IC=+0.1916, Recent IC=+0.0942, 1st-half IC=+0.1434, 2nd-half IC=+0.0873, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.035, Q3_mid=+0.115, Q4=+0.125, Q5_high_vol=+0.176

**`combo_mean__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=-0.0187, Sharpe=-0.7812)
- Admission: Train IC=+0.2111, Deflated=+0.2104, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.069 | 2017: +0.225 | 2018: +0.139 | 2019: +0.101 | 2020: +0.122 | 2021: +0.072 | 2022: +0.076 | 2023: +0.072 | 2024: +0.122 | 2025: +0.144 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.291 | 2016: -0.115 | 2017: +0.318 | 2018: +0.081 | 2019: +0.240 | 2020: +0.091 | 2021: +0.312 | 2022: +0.309 | 2023: +0.294 | 2024: +0.313 | 2025: +0.133 | 2026: -0.168
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=1.11
- Early IC=+0.1197, Recent IC=+0.1332, 1st-half IC=+0.1071, 2nd-half IC=+0.1116, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.063, Q3_mid=+0.148, Q4=+0.113, Q5_high_vol=+0.135

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression`** (Lock IC=-0.0136, Sharpe=-0.6200)
- Admission: Train IC=+0.1801, Deflated=+0.1782, IR=0.53, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.138 | 2017: -0.019 | 2018: +0.161 | 2019: +0.015 | 2020: +0.085 | 2021: -0.017 | 2022: +0.104 | 2023: +0.014 | 2024: +0.026 | 2025: +0.152 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.326 | 2017: +0.120 | 2018: +0.270 | 2019: +0.074 | 2020: +0.256 | 2021: +0.084 | 2022: +0.110 | 2023: -0.043 | 2024: +0.277 | 2025: +0.056 | 2026: -0.021
- IC CV=0.94, Neg years (linear/tail)=1/1 of 8, Half ratio=1.07, Recency ratio=1.01
- Early IC=+0.0882, Recent IC=+0.0888, 1st-half IC=+0.0713, 2nd-half IC=+0.0766, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.078, Q3_mid=+0.075, Q4=+0.033, Q5_high_vol=+0.138

**`combo_rank_min__trend_bar_close_consistency__bar_ret_0`** (Lock IC=-0.0002, Sharpe=-0.4417)
- Admission: Train IC=+0.2118, Deflated=+0.2112, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.045 | 2017: +0.156 | 2018: +0.171 | 2019: +0.101 | 2020: +0.037 | 2021: +0.062 | 2022: +0.066 | 2023: +0.062 | 2024: +0.112 | 2025: +0.116 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.006 | 2017: +0.316 | 2018: +0.395 | 2019: +0.113 | 2020: +0.057 | 2021: +0.252 | 2022: +0.293 | 2023: -0.003 | 2024: +0.322 | 2025: +0.094 | 2026: +0.158
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.97, Recency ratio=0.83
- Early IC=+0.1361, Recent IC=+0.1136, 1st-half IC=+0.0935, 2nd-half IC=+0.0906, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.008, Q3_mid=+0.101, Q4=+0.099, Q5_high_vol=+0.128

**`combo_min__net_volume_flow__first_bar_return`** (Lock IC=-0.0010, Sharpe=-0.2212)
- Admission: Train IC=+0.2435, Deflated=+0.2432, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: +0.181 | 2018: +0.177 | 2019: +0.120 | 2020: +0.094 | 2021: +0.083 | 2022: +0.086 | 2023: +0.078 | 2024: +0.134 | 2025: +0.124 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.015 | 2017: +0.228 | 2018: +0.376 | 2019: +0.143 | 2020: +0.116 | 2021: +0.288 | 2022: +0.224 | 2023: +0.316 | 2024: +0.337 | 2025: +0.140 | 2026: -0.073
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.87
- Early IC=+0.1487, Recent IC=+0.1290, 1st-half IC=+0.1184, 2nd-half IC=+0.1114, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.044, Q3_mid=+0.134, Q4=+0.115, Q5_high_vol=+0.151

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=-0.0061, Sharpe=+0.1883)
- Admission: Train IC=+0.1965, Deflated=+0.1957, IR=0.69, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.054 | 2017: +0.210 | 2018: +0.200 | 2019: +0.133 | 2020: +0.146 | 2021: +0.106 | 2022: +0.086 | 2023: +0.131 | 2024: +0.151 | 2025: +0.109 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.387 | 2016: +0.209 | 2017: +0.332 | 2018: +0.306 | 2019: +0.177 | 2020: +0.225 | 2021: +0.275 | 2022: +0.232 | 2023: +0.231 | 2024: +0.178 | 2025: +0.049 | 2026: -0.213
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.78
- Early IC=+0.1667, Recent IC=+0.1297, 1st-half IC=+0.1461, 2nd-half IC=+0.1278, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.075, Q3_mid=+0.171, Q4=+0.120, Q5_high_vol=+0.177

**`combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range`** (Lock IC=-0.0837, Sharpe=+1.3887)
- Admission: Train IC=+0.1441, Deflated=+0.1435, IR=0.62, Mono=0.75, p=0.0040, MaxCorr=0.48
- Yearly Linear ICs: 2015: -0.025 | 2016: -0.072 | 2017: +0.040 | 2018: +0.142 | 2019: +0.043 | 2020: +0.057 | 2021: +0.076 | 2022: +0.038 | 2023: +0.083 | 2024: -0.007 | 2025: +0.038 | 2026: -0.084
- Yearly Tail ICs:   2015: -0.017 | 2016: -0.143 | 2017: -0.119 | 2018: +0.259 | 2019: +0.035 | 2020: +0.251 | 2021: +0.170 | 2022: +0.162 | 2023: +0.071 | 2024: +0.077 | 2025: +0.242 | 2026: +0.077
- IC CV=0.69, Neg years (linear/tail)=1/0 of 8, Half ratio=0.40, Recency ratio=0.17
- Early IC=+0.0926, Recent IC=+0.0157, 1st-half IC=+0.0788, 2nd-half IC=+0.0316, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.31, neg years=0)
- Regime ICs: Q1_low_vol=-0.022, Q2=+0.027, Q3_mid=+0.039, Q4=+0.029, Q5_high_vol=+0.172

### 159915ETF — `single` False Positives

**`combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position`** (Lock IC=-0.1064, Sharpe=-4.3046)
- Admission: Train IC=+0.2173, Deflated=+0.2174, IR=0.68, Mono=0.76, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.006 | 2017: +0.035 | 2018: +0.002 | 2019: +0.098 | 2020: +0.044 | 2021: +0.145 | 2022: +0.076 | 2023: +0.163 | 2024: +0.087 | 2025: +0.195 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.298 | 2016: -0.007 | 2017: +0.135 | 2018: -0.059 | 2019: +0.380 | 2020: +0.209 | 2021: +0.219 | 2022: +0.279 | 2023: +0.335 | 2024: +0.198 | 2025: +0.185 | 2026: -0.492
- IC CV=0.59, Neg years (linear/tail)=0/1 of 8, Half ratio=2.15, Recency ratio=2.80
- Early IC=+0.0502, Recent IC=+0.1406, 1st-half IC=+0.0638, 2nd-half IC=+0.1373, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.147, Q3_mid=+0.137, Q4=+0.072, Q5_high_vol=+0.078

**`combo_rank_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0913, Sharpe=-4.2927)
- Admission: Train IC=+0.2254, Deflated=+0.2264, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.059 | 2017: +0.061 | 2018: +0.047 | 2019: +0.137 | 2020: +0.115 | 2021: +0.146 | 2022: +0.108 | 2023: +0.179 | 2024: +0.061 | 2025: +0.188 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.319 | 2016: -0.005 | 2017: +0.036 | 2018: +0.069 | 2019: +0.292 | 2020: +0.212 | 2021: +0.256 | 2022: +0.199 | 2023: +0.434 | 2024: +0.167 | 2025: +0.183 | 2026: -0.543
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.43
- Early IC=+0.0888, Recent IC=+0.1265, 1st-half IC=+0.1025, 2nd-half IC=+0.1391, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.172, Q3_mid=+0.119, Q4=+0.112, Q5_high_vol=+0.104

**`combo_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.1035, Sharpe=-4.2121)
- Admission: Train IC=+0.2332, Deflated=+0.2339, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.049 | 2017: +0.052 | 2018: +0.048 | 2019: +0.121 | 2020: +0.095 | 2021: +0.165 | 2022: +0.100 | 2023: +0.183 | 2024: +0.066 | 2025: +0.191 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.081 | 2017: +0.036 | 2018: +0.109 | 2019: +0.301 | 2020: +0.094 | 2021: +0.300 | 2022: +0.294 | 2023: +0.482 | 2024: +0.248 | 2025: +0.089 | 2026: -0.564
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.40, Recency ratio=1.52
- Early IC=+0.0847, Recent IC=+0.1287, 1st-half IC=+0.0998, 2nd-half IC=+0.1400, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.176, Q3_mid=+0.119, Q4=+0.111, Q5_high_vol=+0.104

**`combo_max__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=-0.0816, Sharpe=-4.0036)
- Admission: Train IC=+0.2264, Deflated=+0.2270, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.079 | 2017: +0.050 | 2018: +0.077 | 2019: +0.126 | 2020: +0.122 | 2021: +0.181 | 2022: +0.085 | 2023: +0.158 | 2024: +0.069 | 2025: +0.208 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.151 | 2016: -0.173 | 2017: +0.133 | 2018: +0.208 | 2019: +0.283 | 2020: +0.072 | 2021: +0.303 | 2022: +0.264 | 2023: +0.354 | 2024: +0.133 | 2025: +0.423 | 2026: -0.613
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.36
- Early IC=+0.1017, Recent IC=+0.1383, 1st-half IC=+0.1182, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.169, Q3_mid=+0.163, Q4=+0.093, Q5_high_vol=+0.102

**`combo_max__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0771, Sharpe=-3.6387)
- Admission: Train IC=+0.2417, Deflated=+0.2416, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.160 | 2017: -0.012 | 2018: +0.104 | 2019: +0.185 | 2020: +0.141 | 2021: +0.171 | 2022: +0.109 | 2023: +0.142 | 2024: +0.059 | 2025: +0.182 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.066 | 2016: +0.181 | 2017: +0.001 | 2018: +0.201 | 2019: +0.295 | 2020: +0.174 | 2021: +0.360 | 2022: +0.247 | 2023: +0.408 | 2024: +0.199 | 2025: +0.156 | 2026: -0.316
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.83
- Early IC=+0.1441, Recent IC=+0.1201, 1st-half IC=+0.1398, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.136, Q3_mid=+0.153, Q4=+0.105, Q5_high_vol=+0.131

**`combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=-0.0381, Sharpe=-3.2808)
- Admission: Train IC=+0.2801, Deflated=+0.2805, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.093 | 2017: +0.001 | 2018: +0.078 | 2019: +0.167 | 2020: +0.104 | 2021: +0.151 | 2022: +0.084 | 2023: +0.171 | 2024: +0.072 | 2025: +0.199 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.313 | 2016: -0.018 | 2017: +0.028 | 2018: +0.263 | 2019: +0.422 | 2020: +0.166 | 2021: +0.183 | 2022: +0.247 | 2023: +0.432 | 2024: +0.210 | 2025: +0.339 | 2026: -0.454
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.10
- Early IC=+0.1223, Recent IC=+0.1351, 1st-half IC=+0.1115, 2nd-half IC=+0.1357, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.156, Q3_mid=+0.151, Q4=+0.081, Q5_high_vol=+0.113

**`combo_mean__max_up_ret__impulse_bar_dominance`** (Lock IC=-0.0845, Sharpe=-3.1121)
- Admission: Train IC=+0.2192, Deflated=+0.2194, IR=0.81, Mono=0.78, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.037 | 2017: +0.045 | 2018: +0.061 | 2019: +0.100 | 2020: +0.091 | 2021: +0.169 | 2022: +0.141 | 2023: +0.182 | 2024: +0.074 | 2025: +0.162 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.032 | 2016: +0.198 | 2017: +0.064 | 2018: +0.196 | 2019: +0.275 | 2020: +0.133 | 2021: +0.329 | 2022: +0.260 | 2023: +0.363 | 2024: +0.153 | 2025: +0.141 | 2026: -0.254
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.42, Recency ratio=1.47
- Early IC=+0.0804, Recent IC=+0.1180, 1st-half IC=+0.0986, 2nd-half IC=+0.1405, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.158, Q3_mid=+0.114, Q4=+0.123, Q5_high_vol=+0.122

**`net_volume_flow`** (Lock IC=-0.0663, Sharpe=-3.0886)
- Admission: Train IC=+0.2076, Deflated=+0.2077, IR=0.65, Mono=0.74, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.053 | 2017: -0.019 | 2018: +0.036 | 2019: +0.116 | 2020: +0.049 | 2021: +0.139 | 2022: +0.063 | 2023: +0.165 | 2024: +0.072 | 2025: +0.205 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.110 | 2017: +0.061 | 2018: +0.026 | 2019: +0.301 | 2020: +0.192 | 2021: -0.005 | 2022: +0.332 | 2023: +0.452 | 2024: +0.160 | 2025: +0.185 | 2026: -0.324
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=1.80, Recency ratio=1.83
- Early IC=+0.0757, Recent IC=+0.1386, 1st-half IC=+0.0760, 2nd-half IC=+0.1368, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.156, Q3_mid=+0.135, Q4=+0.077, Q5_high_vol=+0.075

**`combo_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0695, Sharpe=-3.0723)
- Admission: Train IC=+0.2316, Deflated=+0.2317, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.058 | 2017: +0.039 | 2018: +0.070 | 2019: +0.176 | 2020: +0.101 | 2021: +0.181 | 2022: +0.107 | 2023: +0.189 | 2024: +0.082 | 2025: +0.172 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.123 | 2017: +0.052 | 2018: +0.197 | 2019: +0.332 | 2020: +0.154 | 2021: +0.274 | 2022: +0.252 | 2023: +0.392 | 2024: +0.225 | 2025: +0.109 | 2026: -0.261
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=1.03
- Early IC=+0.1230, Recent IC=+0.1271, 1st-half IC=+0.1260, 2nd-half IC=+0.1403, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.177, Q3_mid=+0.114, Q4=+0.141, Q5_high_vol=+0.145

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0534, Sharpe=-3.0723)
- Admission: Train IC=+0.2419, Deflated=+0.2417, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.097 | 2017: +0.005 | 2018: +0.084 | 2019: +0.214 | 2020: +0.123 | 2021: +0.165 | 2022: +0.108 | 2023: +0.149 | 2024: +0.080 | 2025: +0.152 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.067 | 2016: +0.147 | 2017: +0.027 | 2018: +0.203 | 2019: +0.298 | 2020: +0.145 | 2021: +0.319 | 2022: +0.261 | 2023: +0.425 | 2024: +0.255 | 2025: +0.122 | 2026: -0.322
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.78
- Early IC=+0.1490, Recent IC=+0.1164, 1st-half IC=+0.1359, 2nd-half IC=+0.1270, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.147, Q3_mid=+0.145, Q4=+0.112, Q5_high_vol=+0.155

**`combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=-0.0820, Sharpe=-3.0532)
- Admission: Train IC=+0.2248, Deflated=+0.2248, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.039 | 2017: +0.044 | 2018: +0.020 | 2019: +0.146 | 2020: +0.031 | 2021: +0.189 | 2022: +0.052 | 2023: +0.168 | 2024: +0.082 | 2025: +0.195 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.142 | 2016: -0.049 | 2017: +0.147 | 2018: +0.069 | 2019: +0.455 | 2020: +0.087 | 2021: +0.215 | 2022: +0.156 | 2023: +0.307 | 2024: +0.146 | 2025: +0.283 | 2026: -0.313
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.66
- Early IC=+0.0830, Recent IC=+0.1383, 1st-half IC=+0.0874, 2nd-half IC=+0.1315, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.157, Q3_mid=+0.144, Q4=+0.086, Q5_high_vol=+0.092

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0737, Sharpe=-3.0060)
- Admission: Train IC=+0.2261, Deflated=+0.2260, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.084 | 2017: +0.064 | 2018: +0.067 | 2019: +0.173 | 2020: +0.066 | 2021: +0.220 | 2022: +0.089 | 2023: +0.165 | 2024: +0.079 | 2025: +0.179 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.017 | 2017: +0.238 | 2018: +0.208 | 2019: +0.343 | 2020: -0.017 | 2021: +0.310 | 2022: +0.236 | 2023: +0.279 | 2024: +0.249 | 2025: +0.235 | 2026: -0.216
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=1.07
- Early IC=+0.1207, Recent IC=+0.1297, 1st-half IC=+0.1257, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.155, Q3_mid=+0.136, Q4=+0.125, Q5_high_vol=+0.133

**`max_up_ret`** (Lock IC=-0.0753, Sharpe=-2.9698)
- Admission: Train IC=+0.2319, Deflated=+0.2324, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074 | 2025: +0.164 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.198 | 2017: +0.106 | 2018: +0.212 | 2019: +0.279 | 2020: +0.177 | 2021: +0.343 | 2022: +0.267 | 2023: +0.389 | 2024: +0.190 | 2025: +0.128 | 2026: -0.261
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.13
- Early IC=+0.1048, Recent IC=+0.1187, 1st-half IC=+0.1197, 2nd-half IC=+0.1306, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.168, Q3_mid=+0.110, Q4=+0.123, Q5_high_vol=+0.121

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0854, Sharpe=-2.9019)
- Admission: Train IC=+0.2440, Deflated=+0.2438, IR=0.75, Mono=0.82, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.71, Recency ratio=2.05
- Early IC=+0.0722, Recent IC=+0.1480, 1st-half IC=+0.0848, 2nd-half IC=+0.1448, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.151, Q3_mid=+0.136, Q4=+0.096, Q5_high_vol=+0.107

**`combo_mean__impulse_bar_dominance__volatility_expansion_trend_vector`** (Lock IC=-0.1025, Sharpe=-2.8874)
- Admission: Train IC=+0.2110, Deflated=+0.2113, IR=0.70, Mono=0.78, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.010 | 2017: +0.025 | 2018: +0.020 | 2019: +0.081 | 2020: +0.055 | 2021: +0.141 | 2022: +0.121 | 2023: +0.171 | 2024: +0.082 | 2025: +0.193 | 2026: -0.103
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.081 | 2017: +0.039 | 2018: -0.005 | 2019: +0.259 | 2020: +0.157 | 2021: +0.180 | 2022: +0.331 | 2023: +0.347 | 2024: +0.162 | 2025: +0.276 | 2026: -0.286
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=2.40, Recency ratio=2.71
- Early IC=+0.0506, Recent IC=+0.1373, 1st-half IC=+0.0621, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.146, Q3_mid=+0.129, Q4=+0.085, Q5_high_vol=+0.096

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0595, Sharpe=-2.7716)
- Admission: Train IC=+0.2532, Deflated=+0.2535, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.10
- Early IC=+0.1138, Recent IC=+0.1250, 1st-half IC=+0.1234, 2nd-half IC=+0.1399, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.173, Q3_mid=+0.106, Q4=+0.143, Q5_high_vol=+0.142

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.1124, Sharpe=-2.6779)
- Admission: Train IC=+0.2139, Deflated=+0.2137, IR=0.69, Mono=0.77, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.086 | 2016: +0.045 | 2017: +0.069 | 2018: +0.084 | 2019: +0.206 | 2020: +0.077 | 2021: +0.111 | 2022: +0.057 | 2023: +0.173 | 2024: +0.119 | 2025: +0.169 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.081 | 2017: +0.039 | 2018: +0.002 | 2019: +0.273 | 2020: +0.174 | 2021: +0.151 | 2022: +0.352 | 2023: +0.381 | 2024: +0.160 | 2025: +0.280 | 2026: -0.291
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.30, Recency ratio=0.99
- Early IC=+0.1452, Recent IC=+0.1440, 1st-half IC=+0.1048, 2nd-half IC=+0.1359, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.151, Q3_mid=+0.148, Q4=+0.101, Q5_high_vol=+0.113

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0325, Sharpe=-2.6779)
- Admission: Train IC=+0.2159, Deflated=+0.2157, IR=0.70, Mono=0.78, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.041 | 2017: +0.004 | 2018: +0.033 | 2019: +0.128 | 2020: +0.102 | 2021: +0.111 | 2022: +0.075 | 2023: +0.138 | 2024: +0.116 | 2025: +0.195 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.210 | 2016: +0.105 | 2017: +0.098 | 2018: -0.016 | 2019: +0.319 | 2020: +0.179 | 2021: +0.151 | 2022: +0.361 | 2023: +0.373 | 2024: +0.169 | 2025: +0.260 | 2026: -0.291
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=1.53, Recency ratio=1.93
- Early IC=+0.0807, Recent IC=+0.1557, 1st-half IC=+0.0904, 2nd-half IC=+0.1381, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.173, Q3_mid=+0.111, Q4=+0.104, Q5_high_vol=+0.109

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0563, Sharpe=-2.6490)
- Admission: Train IC=+0.2775, Deflated=+0.2775, IR=0.87, Mono=0.78, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.149 | 2017: +0.001 | 2018: +0.089 | 2019: +0.181 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.152 | 2024: +0.062 | 2025: +0.186 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.024 | 2017: +0.040 | 2018: +0.261 | 2019: +0.408 | 2020: +0.180 | 2021: +0.310 | 2022: +0.269 | 2023: +0.345 | 2024: +0.233 | 2025: +0.245 | 2026: -0.185
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.86
- Early IC=+0.1418, Recent IC=+0.1224, 1st-half IC=+0.1369, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.134, Q3_mid=+0.143, Q4=+0.113, Q5_high_vol=+0.130

**`shaved_bar_trend_conviction`** (Lock IC=-0.0741, Sharpe=-2.4700)
- Admission: Train IC=+0.1554, Deflated=+0.1556, IR=0.57, Mono=0.69, p=0.0032, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.088 | 2016: +0.016 | 2017: +0.002 | 2018: +0.013 | 2019: +0.065 | 2020: +0.061 | 2021: +0.112 | 2022: -0.031 | 2023: +0.180 | 2024: +0.106 | 2025: +0.170 | 2026: -0.074
- Yearly Tail ICs:   2015: -0.012 | 2016: +0.112 | 2017: +0.042 | 2018: +0.160 | 2019: +0.303 | 2020: +0.123 | 2021: +0.020 | 2022: +0.063 | 2023: +0.180 | 2024: +0.161 | 2025: +0.137 | 2026: -0.327
- IC CV=0.80, Neg years (linear/tail)=1/0 of 8, Half ratio=1.84, Recency ratio=3.52
- Early IC=+0.0391, Recent IC=+0.1377, 1st-half IC=+0.0605, 2nd-half IC=+0.1115, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.180, Q3_mid=+0.130, Q4=+0.034, Q5_high_vol=+0.039

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=-0.0445, Sharpe=-2.4277)
- Admission: Train IC=+0.2112, Deflated=+0.2115, IR=0.68, Mono=0.73, p=0.0002, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.047 | 2016: +0.069 | 2017: -0.004 | 2018: +0.055 | 2019: +0.192 | 2020: +0.043 | 2021: +0.159 | 2022: +0.081 | 2023: +0.125 | 2024: +0.096 | 2025: +0.178 | 2026: -0.044
- Yearly Tail ICs:   2015: -0.021 | 2016: +0.181 | 2017: +0.163 | 2018: -0.026 | 2019: +0.316 | 2020: +0.279 | 2021: +0.076 | 2022: +0.332 | 2023: +0.234 | 2024: +0.145 | 2025: +0.216 | 2026: -0.275
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=1.22, Recency ratio=1.11
- Early IC=+0.1236, Recent IC=+0.1369, 1st-half IC=+0.1038, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.151, Q3_mid=+0.138, Q4=+0.129, Q5_high_vol=+0.055

**`combo_max__bar_body_rng_0__impulse_bar_dominance`** (Lock IC=-0.0248, Sharpe=-2.1848)
- Admission: Train IC=+0.2210, Deflated=+0.2214, IR=0.63, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.134 | 2017: -0.005 | 2018: +0.105 | 2019: +0.083 | 2020: +0.112 | 2021: +0.158 | 2022: +0.080 | 2023: +0.155 | 2024: +0.025 | 2025: +0.191 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.077 | 2017: +0.072 | 2018: +0.170 | 2019: +0.384 | 2020: +0.034 | 2021: +0.250 | 2022: +0.167 | 2023: +0.293 | 2024: +0.121 | 2025: +0.476 | 2026: -0.326
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=1.16
- Early IC=+0.0936, Recent IC=+0.1083, 1st-half IC=+0.1059, 2nd-half IC=+0.1132, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.125, Q3_mid=+0.120, Q4=+0.090, Q5_high_vol=+0.136

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0232, Sharpe=-2.1679)
- Admission: Train IC=+0.2640, Deflated=+0.2644, IR=0.75, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.133 | 2017: +0.004 | 2018: +0.113 | 2019: +0.211 | 2020: +0.115 | 2021: +0.145 | 2022: +0.058 | 2023: +0.175 | 2024: +0.079 | 2025: +0.162 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.065 | 2017: +0.117 | 2018: +0.209 | 2019: +0.405 | 2020: +0.204 | 2021: +0.208 | 2022: +0.145 | 2023: +0.347 | 2024: +0.318 | 2025: +0.259 | 2026: -0.084
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.74
- Early IC=+0.1617, Recent IC=+0.1202, 1st-half IC=+0.1337, 2nd-half IC=+0.1213, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.133, Q3_mid=+0.136, Q4=+0.093, Q5_high_vol=+0.148

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0177, Sharpe=-2.1380)
- Admission: Train IC=+0.1130, Deflated=+0.1133, IR=0.36, Mono=0.65, p=0.0242, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.244 | 2016: +0.095 | 2017: -0.027 | 2018: +0.075 | 2019: +0.172 | 2020: +0.164 | 2021: +0.131 | 2022: +0.048 | 2023: +0.087 | 2024: +0.056 | 2025: +0.083 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.242 | 2016: -0.262 | 2017: -0.038 | 2018: +0.355 | 2019: +0.243 | 2020: +0.291 | 2021: +0.281 | 2022: +0.162 | 2023: +0.181 | 2024: +0.055 | 2025: +0.121 | 2026: -0.195
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.56
- Early IC=+0.1233, Recent IC=+0.0694, 1st-half IC=+0.1286, 2nd-half IC=+0.0686, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.092, Q3_mid=+0.140, Q4=+0.063, Q5_high_vol=+0.104

**`combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0930, Sharpe=-2.1195)
- Admission: Train IC=+0.2483, Deflated=+0.2487, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.048 | 2017: +0.034 | 2018: +0.048 | 2019: +0.165 | 2020: +0.087 | 2021: +0.143 | 2022: +0.100 | 2023: +0.179 | 2024: +0.106 | 2025: +0.197 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.249 | 2016: -0.053 | 2017: +0.064 | 2018: +0.031 | 2019: +0.396 | 2020: +0.246 | 2021: +0.109 | 2022: +0.308 | 2023: +0.347 | 2024: +0.267 | 2025: +0.295 | 2026: -0.202
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.43
- Early IC=+0.1070, Recent IC=+0.1525, 1st-half IC=+0.1014, 2nd-half IC=+0.1518, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.165, Q3_mid=+0.134, Q4=+0.118, Q5_high_vol=+0.125

**`combo_max__bar_ret_0__impulse_bar_dominance`** (Lock IC=-0.0491, Sharpe=-2.0937)
- Admission: Train IC=+0.1797, Deflated=+0.1798, IR=0.62, Mono=0.74, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.055 | 2017: +0.021 | 2018: +0.071 | 2019: +0.054 | 2020: +0.094 | 2021: +0.163 | 2022: +0.075 | 2023: +0.151 | 2024: +0.069 | 2025: +0.147 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.040 | 2017: +0.062 | 2018: +0.242 | 2019: +0.135 | 2020: +0.093 | 2021: +0.308 | 2022: +0.100 | 2023: +0.273 | 2024: +0.074 | 2025: +0.366 | 2026: -0.381
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=1.73
- Early IC=+0.0625, Recent IC=+0.1078, 1st-half IC=+0.0877, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.135, Q3_mid=+0.088, Q4=+0.074, Q5_high_vol=+0.135

**`combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`** (Lock IC=-0.0102, Sharpe=-2.0687)
- Admission: Train IC=+0.1847, Deflated=+0.1848, IR=0.42, Mono=0.67, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.001 | 2017: +0.026 | 2018: +0.021 | 2019: +0.089 | 2020: +0.031 | 2021: +0.120 | 2022: +0.109 | 2023: +0.148 | 2024: +0.079 | 2025: +0.119 | 2026: -0.010
- Yearly Tail ICs:   2015: -0.029 | 2016: +0.041 | 2017: +0.087 | 2018: +0.083 | 2019: +0.258 | 2020: -0.152 | 2021: +0.269 | 2022: +0.191 | 2023: +0.255 | 2024: +0.307 | 2025: +0.130 | 2026: -0.145
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=2.07, Recency ratio=1.93
- Early IC=+0.0524, Recent IC=+0.1012, 1st-half IC=+0.0578, 2nd-half IC=+0.1195, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.129, Q3_mid=+0.082, Q4=+0.106, Q5_high_vol=+0.070

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=-0.0318, Sharpe=-2.0212)
- Admission: Train IC=+0.2512, Deflated=+0.2511, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.032 | 2017: +0.022 | 2018: +0.079 | 2019: +0.178 | 2020: +0.092 | 2021: +0.165 | 2022: +0.155 | 2023: +0.149 | 2024: +0.068 | 2025: +0.195 | 2026: -0.032
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.240 | 2017: +0.031 | 2018: +0.116 | 2019: +0.351 | 2020: +0.157 | 2021: +0.329 | 2022: +0.376 | 2023: +0.334 | 2024: +0.201 | 2025: +0.255 | 2026: -0.254
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.03
- Early IC=+0.1284, Recent IC=+0.1316, 1st-half IC=+0.1298, 2nd-half IC=+0.1472, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.160, Q3_mid=+0.143, Q4=+0.146, Q5_high_vol=+0.145

**`combo_min__first_bar_sentiment__volatility_expansion_trend_vector`** (Lock IC=-0.0329, Sharpe=-2.0105)
- Admission: Train IC=+0.2245, Deflated=+0.2249, IR=0.52, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.065 | 2017: +0.002 | 2018: +0.045 | 2019: +0.184 | 2020: +0.066 | 2021: +0.094 | 2022: +0.066 | 2023: +0.135 | 2024: +0.083 | 2025: +0.149 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.303 | 2016: -0.082 | 2017: +0.185 | 2018: +0.078 | 2019: +0.291 | 2020: -0.043 | 2021: +0.070 | 2022: +0.097 | 2023: +0.284 | 2024: +0.199 | 2025: +0.233 | 2026: -0.202
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=1.32, Recency ratio=1.01
- Early IC=+0.1145, Recent IC=+0.1160, 1st-half IC=+0.0852, 2nd-half IC=+0.1125, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.119, Q3_mid=+0.130, Q4=+0.053, Q5_high_vol=+0.086

**`combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=-0.0010, Sharpe=-1.9510)
- Admission: Train IC=+0.2328, Deflated=+0.2335, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.130 | 2017: +0.013 | 2018: +0.109 | 2019: +0.222 | 2020: +0.144 | 2021: +0.031 | 2022: +0.057 | 2023: +0.140 | 2024: +0.064 | 2025: +0.122 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.087 | 2017: -0.031 | 2018: -0.019 | 2019: +0.411 | 2020: +0.287 | 2021: +0.098 | 2022: +0.355 | 2023: +0.372 | 2024: +0.177 | 2025: +0.163 | 2026: -0.217
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.85, Recency ratio=0.56
- Early IC=+0.1654, Recent IC=+0.0930, 1st-half IC=+0.1151, 2nd-half IC=+0.0984, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.125, Q3_mid=+0.114, Q4=+0.078, Q5_high_vol=+0.104

**`combo_max__first_bar_sentiment__first_bar_return`** (Lock IC=-0.0145, Sharpe=-1.9086)
- Admission: Train IC=+0.1907, Deflated=+0.1917, IR=0.61, Mono=0.73, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.149 | 2017: -0.003 | 2018: +0.136 | 2019: +0.198 | 2020: +0.125 | 2021: +0.128 | 2022: +0.061 | 2023: +0.137 | 2024: +0.068 | 2025: +0.133 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.086 | 2017: +0.051 | 2018: +0.253 | 2019: +0.177 | 2020: +0.147 | 2021: +0.212 | 2022: +0.176 | 2023: +0.289 | 2024: +0.089 | 2025: +0.445 | 2026: -0.388
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.1672, Recent IC=+0.1005, 1st-half IC=+0.1339, 2nd-half IC=+0.0976, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.120, Q3_mid=+0.134, Q4=+0.058, Q5_high_vol=+0.126

**`trend_bar_close_consistency`** (Lock IC=-0.1362, Sharpe=-1.8903)
- Admission: Train IC=+0.1956, Deflated=+0.1955, IR=0.61, Mono=0.75, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.055 | 2016: +0.017 | 2017: -0.031 | 2018: +0.000 | 2019: +0.074 | 2020: +0.026 | 2021: +0.109 | 2022: +0.058 | 2023: +0.144 | 2024: +0.066 | 2025: +0.222 | 2026: -0.136
- Yearly Tail ICs:   2015: +0.047 | 2016: +0.226 | 2017: -0.086 | 2018: +0.030 | 2019: +0.233 | 2020: +0.182 | 2021: +0.058 | 2022: +0.382 | 2023: +0.352 | 2024: +0.099 | 2025: +0.249 | 2026: -0.074
- IC CV=0.75, Neg years (linear/tail)=0/0 of 8, Half ratio=2.76, Recency ratio=3.89
- Early IC=+0.0370, Recent IC=+0.1440, 1st-half IC=+0.0475, 2nd-half IC=+0.1313, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.158, Q3_mid=+0.121, Q4=+0.075, Q5_high_vol=+0.030

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0811, Sharpe=-1.8808)
- Admission: Train IC=+0.2099, Deflated=+0.2097, IR=0.69, Mono=0.77, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.084 | 2016: +0.036 | 2017: +0.087 | 2018: +0.104 | 2019: +0.173 | 2020: +0.046 | 2021: +0.139 | 2022: +0.087 | 2023: +0.166 | 2024: +0.120 | 2025: +0.124 | 2026: -0.081
- Yearly Tail ICs:   2015: -0.249 | 2016: +0.198 | 2017: +0.127 | 2018: +0.240 | 2019: +0.254 | 2020: +0.156 | 2021: +0.147 | 2022: +0.237 | 2023: +0.386 | 2024: +0.298 | 2025: +0.040 | 2026: -0.169
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.88
- Early IC=+0.1388, Recent IC=+0.1220, 1st-half IC=+0.1081, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.122, Q3_mid=+0.097, Q4=+0.118, Q5_high_vol=+0.137

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0421, Sharpe=-1.8255)
- Admission: Train IC=+0.2722, Deflated=+0.2726, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.118 | 2017: +0.014 | 2018: +0.121 | 2019: +0.200 | 2020: +0.117 | 2021: +0.157 | 2022: +0.100 | 2023: +0.188 | 2024: +0.077 | 2025: +0.178 | 2026: -0.042
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.143 | 2017: -0.004 | 2018: +0.285 | 2019: +0.390 | 2020: +0.231 | 2021: +0.265 | 2022: +0.230 | 2023: +0.565 | 2024: +0.269 | 2025: +0.093 | 2026: -0.230
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.79
- Early IC=+0.1605, Recent IC=+0.1274, 1st-half IC=+0.1381, 2nd-half IC=+0.1356, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.163, Q3_mid=+0.130, Q4=+0.122, Q5_high_vol=+0.141

**`combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=-0.0077, Sharpe=-1.8187)
- Admission: Train IC=+0.2724, Deflated=+0.2722, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.015 | 2017: +0.006 | 2018: +0.093 | 2019: +0.192 | 2020: +0.099 | 2021: +0.140 | 2022: +0.115 | 2023: +0.143 | 2024: +0.073 | 2025: +0.194 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.340 | 2016: -0.075 | 2017: +0.006 | 2018: -0.024 | 2019: +0.355 | 2020: +0.268 | 2021: +0.171 | 2022: +0.192 | 2023: +0.189 | 2024: +0.063 | 2025: +0.373 | 2026: -0.157
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=1.07, Recency ratio=0.94
- Early IC=+0.1426, Recent IC=+0.1340, 1st-half IC=+0.1295, 2nd-half IC=+0.1388, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.149, Q3_mid=+0.139, Q4=+0.142, Q5_high_vol=+0.157

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0192, Sharpe=-1.7777)
- Admission: Train IC=+0.2591, Deflated=+0.2590, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.073 | 2017: +0.025 | 2018: +0.078 | 2019: +0.188 | 2020: +0.134 | 2021: +0.148 | 2022: +0.123 | 2023: +0.187 | 2024: +0.105 | 2025: +0.189 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.069 | 2016: +0.182 | 2017: +0.197 | 2018: +0.207 | 2019: +0.364 | 2020: +0.165 | 2021: +0.331 | 2022: +0.263 | 2023: +0.402 | 2024: +0.247 | 2025: +0.257 | 2026: -0.059
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.11
- Early IC=+0.1327, Recent IC=+0.1470, 1st-half IC=+0.1370, 2nd-half IC=+0.1490, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.185, Q3_mid=+0.113, Q4=+0.134, Q5_high_vol=+0.159

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0026, Sharpe=-1.7519)
- Admission: Train IC=+0.2424, Deflated=+0.2432, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.128 | 2017: +0.017 | 2018: +0.123 | 2019: +0.204 | 2020: +0.125 | 2021: +0.129 | 2022: +0.089 | 2023: +0.151 | 2024: +0.054 | 2025: +0.119 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.247 | 2016: +0.063 | 2017: +0.107 | 2018: +0.067 | 2019: +0.351 | 2020: -0.005 | 2021: +0.199 | 2022: +0.097 | 2023: +0.392 | 2024: -0.001 | 2025: +0.286 | 2026: -0.142
- IC CV=0.33, Neg years (linear/tail)=0/2 of 8, Half ratio=0.75, Recency ratio=0.53
- Early IC=+0.1634, Recent IC=+0.0869, 1st-half IC=+0.1379, 2nd-half IC=+0.1029, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.142, Q3_mid=+0.132, Q4=+0.076, Q5_high_vol=+0.119

**`combo_min__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0036, Sharpe=-1.7032)
- Admission: Train IC=+0.2780, Deflated=+0.2786, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.096 | 2017: -0.003 | 2018: +0.128 | 2019: +0.200 | 2020: +0.124 | 2021: +0.142 | 2022: +0.099 | 2023: +0.177 | 2024: +0.076 | 2025: +0.180 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.399 | 2016: -0.116 | 2017: -0.057 | 2018: +0.243 | 2019: +0.515 | 2020: +0.263 | 2021: +0.349 | 2022: +0.080 | 2023: +0.370 | 2024: +0.149 | 2025: +0.277 | 2026: +0.008
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.78
- Early IC=+0.1638, Recent IC=+0.1280, 1st-half IC=+0.1394, 2nd-half IC=+0.1367, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.165, Q3_mid=+0.127, Q4=+0.129, Q5_high_vol=+0.138

**`combo_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=-0.0265, Sharpe=-1.7025)
- Admission: Train IC=+0.1980, Deflated=+0.1983, IR=0.57, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.079 | 2017: +0.035 | 2018: +0.100 | 2019: +0.191 | 2020: +0.101 | 2021: +0.168 | 2022: +0.052 | 2023: +0.184 | 2024: +0.080 | 2025: +0.156 | 2026: -0.026
- Yearly Tail ICs:   2015: +0.192 | 2016: -0.029 | 2017: +0.135 | 2018: +0.306 | 2019: +0.219 | 2020: +0.033 | 2021: +0.315 | 2022: +0.109 | 2023: +0.390 | 2024: +0.083 | 2025: +0.342 | 2026: -0.165
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.81
- Early IC=+0.1455, Recent IC=+0.1176, 1st-half IC=+0.1292, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.136, Q3_mid=+0.106, Q4=+0.101, Q5_high_vol=+0.154

**`combo_min__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0303, Sharpe=-1.6286)
- Admission: Train IC=+0.2037, Deflated=+0.2043, IR=0.50, Mono=0.69, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.099 | 2017: +0.052 | 2018: +0.061 | 2019: +0.188 | 2020: +0.072 | 2021: +0.157 | 2022: +0.027 | 2023: +0.182 | 2024: +0.074 | 2025: +0.151 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.096 | 2016: -0.035 | 2017: +0.137 | 2018: +0.133 | 2019: +0.376 | 2020: +0.133 | 2021: +0.197 | 2022: +0.062 | 2023: +0.453 | 2024: +0.007 | 2025: +0.236 | 2026: -0.162
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.91
- Early IC=+0.1245, Recent IC=+0.1129, 1st-half IC=+0.1145, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.159, Q3_mid=+0.123, Q4=+0.105, Q5_high_vol=+0.087

**`combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=-0.0221, Sharpe=-1.5636)
- Admission: Train IC=+0.2247, Deflated=+0.2245, IR=0.48, Mono=0.69, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.053 | 2017: +0.034 | 2018: +0.074 | 2019: +0.073 | 2020: +0.011 | 2021: +0.156 | 2022: +0.135 | 2023: +0.180 | 2024: +0.084 | 2025: +0.165 | 2026: -0.031
- Yearly Tail ICs:   2015: -0.095 | 2016: +0.160 | 2017: +0.121 | 2018: +0.123 | 2019: +0.285 | 2020: -0.088 | 2021: +0.215 | 2022: +0.270 | 2023: +0.272 | 2024: +0.343 | 2025: +0.121 | 2026: -0.085
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=1.78, Recency ratio=1.65
- Early IC=+0.0763, Recent IC=+0.1262, 1st-half IC=+0.0810, 2nd-half IC=+0.1440, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.149, Q3_mid=+0.090, Q4=+0.130, Q5_high_vol=+0.111

**`combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=-0.0561, Sharpe=-1.5551)
- Admission: Train IC=+0.2141, Deflated=+0.2141, IR=0.71, Mono=0.75, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.041 | 2017: +0.011 | 2018: +0.023 | 2019: +0.133 | 2020: -0.015 | 2021: +0.167 | 2022: +0.017 | 2023: +0.179 | 2024: +0.069 | 2025: +0.169 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.027 | 2016: +0.051 | 2017: +0.104 | 2018: +0.135 | 2019: +0.330 | 2020: +0.070 | 2021: +0.088 | 2022: +0.155 | 2023: +0.382 | 2024: +0.220 | 2025: +0.210 | 2026: -0.249
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=1.80, Recency ratio=1.71
- Early IC=+0.0720, Recent IC=+0.1233, 1st-half IC=+0.0654, 2nd-half IC=+0.1174, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.143, Q3_mid=+0.102, Q4=+0.066, Q5_high_vol=+0.082

**`combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=-0.0181, Sharpe=-1.3831)
- Admission: Train IC=+0.2633, Deflated=+0.2641, IR=0.89, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.162 | 2017: +0.001 | 2018: +0.131 | 2019: +0.198 | 2020: +0.138 | 2021: +0.144 | 2022: +0.090 | 2023: +0.172 | 2024: +0.049 | 2025: +0.147 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.120 | 2016: +0.166 | 2017: -0.002 | 2018: +0.280 | 2019: +0.376 | 2020: +0.249 | 2021: +0.259 | 2022: +0.226 | 2023: +0.539 | 2024: +0.232 | 2025: +0.081 | 2026: -0.090
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.60
- Early IC=+0.1641, Recent IC=+0.0981, 1st-half IC=+0.1446, 2nd-half IC=+0.1149, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.152, Q3_mid=+0.136, Q4=+0.104, Q5_high_vol=+0.131

**`combo_min__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0016, Sharpe=-1.2131)
- Admission: Train IC=+0.2055, Deflated=+0.2056, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.124 | 2017: +0.019 | 2018: +0.083 | 2019: +0.202 | 2020: +0.103 | 2021: +0.129 | 2022: +0.042 | 2023: +0.149 | 2024: +0.072 | 2025: +0.141 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.282 | 2016: -0.064 | 2017: -0.057 | 2018: +0.155 | 2019: +0.440 | 2020: +0.176 | 2021: +0.228 | 2022: -0.031 | 2023: +0.262 | 2024: +0.050 | 2025: +0.355 | 2026: -0.071
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.75
- Early IC=+0.1421, Recent IC=+0.1064, 1st-half IC=+0.1221, 2nd-half IC=+0.1049, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.144, Q3_mid=+0.158, Q4=+0.085, Q5_high_vol=+0.095

**`combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=-0.0770, Sharpe=-1.2111)
- Admission: Train IC=+0.2879, Deflated=+0.2881, IR=0.84, Mono=0.77, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.043 | 2017: +0.029 | 2018: +0.087 | 2019: +0.188 | 2020: +0.050 | 2021: +0.161 | 2022: +0.051 | 2023: +0.184 | 2024: +0.081 | 2025: +0.171 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.290 | 2016: -0.062 | 2017: -0.026 | 2018: +0.161 | 2019: +0.474 | 2020: +0.209 | 2021: +0.351 | 2022: +0.108 | 2023: +0.425 | 2024: +0.209 | 2025: +0.338 | 2026: -0.146
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=0.94
- Early IC=+0.1372, Recent IC=+0.1292, 1st-half IC=+0.1109, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.170, Q3_mid=+0.126, Q4=+0.118, Q5_high_vol=+0.122

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0689, Sharpe=-1.1833)
- Admission: Train IC=+0.2554, Deflated=+0.2557, IR=1.05, Mono=0.83, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.073 | 2017: +0.032 | 2018: +0.088 | 2019: +0.165 | 2020: +0.093 | 2021: +0.119 | 2022: +0.096 | 2023: +0.190 | 2024: +0.096 | 2025: +0.177 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.146 | 2017: +0.121 | 2018: +0.243 | 2019: +0.387 | 2020: +0.259 | 2021: +0.227 | 2022: +0.345 | 2023: +0.553 | 2024: +0.166 | 2025: +0.135 | 2026: -0.108
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.30, Recency ratio=1.09
- Early IC=+0.1262, Recent IC=+0.1369, 1st-half IC=+0.1081, 2nd-half IC=+0.1408, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.156, Q3_mid=+0.116, Q4=+0.124, Q5_high_vol=+0.120

**`combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.1027, Sharpe=-1.1404)
- Admission: Train IC=+0.2108, Deflated=+0.2101, IR=0.46, Mono=0.72, p=0.0002, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.129 | 2016: +0.060 | 2017: +0.071 | 2018: +0.147 | 2019: +0.152 | 2020: +0.103 | 2021: +0.133 | 2022: +0.048 | 2023: +0.194 | 2024: +0.102 | 2025: +0.140 | 2026: -0.103
- Yearly Tail ICs:   2015: +0.257 | 2016: -0.074 | 2017: -0.045 | 2018: +0.141 | 2019: +0.353 | 2020: +0.142 | 2021: +0.205 | 2022: +0.043 | 2023: +0.305 | 2024: +0.157 | 2025: +0.397 | 2026: +0.003
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.81
- Early IC=+0.1498, Recent IC=+0.1212, 1st-half IC=+0.1271, 2nd-half IC=+0.1204, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.120, Q3_mid=+0.089, Q4=+0.122, Q5_high_vol=+0.175

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=-0.0225, Sharpe=-1.1019)
- Admission: Train IC=+0.2071, Deflated=+0.2078, IR=0.62, Mono=0.76, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.097 | 2017: +0.042 | 2018: +0.107 | 2019: +0.184 | 2020: +0.095 | 2021: +0.159 | 2022: +0.105 | 2023: +0.168 | 2024: +0.065 | 2025: +0.165 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.166 | 2016: +0.102 | 2017: +0.175 | 2018: +0.156 | 2019: +0.228 | 2020: +0.081 | 2021: +0.304 | 2022: +0.251 | 2023: +0.364 | 2024: +0.111 | 2025: +0.136 | 2026: +0.003
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.79
- Early IC=+0.1453, Recent IC=+0.1151, 1st-half IC=+0.1273, 2nd-half IC=+0.1256, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.32, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.158, Q3_mid=+0.127, Q4=+0.105, Q5_high_vol=+0.121

**`combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0572, Sharpe=-1.0459)
- Admission: Train IC=+0.2567, Deflated=+0.2567, IR=0.84, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.018 | 2017: +0.016 | 2018: +0.050 | 2019: +0.132 | 2020: +0.054 | 2021: +0.144 | 2022: +0.071 | 2023: +0.196 | 2024: +0.078 | 2025: +0.206 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.178 | 2017: +0.104 | 2018: +0.021 | 2019: +0.278 | 2020: +0.168 | 2021: +0.151 | 2022: +0.380 | 2023: +0.504 | 2024: +0.190 | 2025: +0.216 | 2026: -0.202
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.74, Recency ratio=1.55
- Early IC=+0.0911, Recent IC=+0.1417, 1st-half IC=+0.0823, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.149, Q3_mid=+0.126, Q4=+0.097, Q5_high_vol=+0.114

**`combo_sig_product__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=-0.1070, Sharpe=-1.0195)
- Admission: Train IC=+0.1335, Deflated=+0.1328, IR=0.40, Mono=0.67, p=0.0072, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.068 | 2017: +0.101 | 2018: +0.140 | 2019: +0.150 | 2020: +0.076 | 2021: +0.127 | 2022: +0.041 | 2023: +0.186 | 2024: +0.106 | 2025: +0.129 | 2026: -0.107
- Yearly Tail ICs:   2015: -0.067 | 2016: -0.040 | 2017: +0.215 | 2018: +0.174 | 2019: +0.114 | 2020: +0.019 | 2021: +0.258 | 2022: +0.036 | 2023: +0.291 | 2024: +0.114 | 2025: +0.139 | 2026: -0.097
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.81
- Early IC=+0.1451, Recent IC=+0.1173, 1st-half IC=+0.1128, 2nd-half IC=+0.1104, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.096, Q3_mid=+0.085, Q4=+0.105, Q5_high_vol=+0.159

**`combo_sig_product__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0148, Sharpe=-1.0032)
- Admission: Train IC=+0.2553, Deflated=+0.2552, IR=0.58, Mono=0.75, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.068 | 2017: +0.037 | 2018: +0.154 | 2019: +0.138 | 2020: +0.129 | 2021: +0.150 | 2022: +0.067 | 2023: +0.190 | 2024: +0.054 | 2025: +0.168 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.279 | 2016: -0.106 | 2017: -0.059 | 2018: +0.221 | 2019: +0.426 | 2020: +0.251 | 2021: +0.207 | 2022: +0.050 | 2023: +0.359 | 2024: +0.150 | 2025: +0.367 | 2026: +0.203
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.76
- Early IC=+0.1457, Recent IC=+0.1111, 1st-half IC=+0.1420, 2nd-half IC=+0.1200, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.135, Q3_mid=+0.119, Q4=+0.122, Q5_high_vol=+0.143

**`combo_min__bar_body_rng_0__impulse_bar_dominance`** (Lock IC=-0.0179, Sharpe=-0.8876)
- Admission: Train IC=+0.2381, Deflated=+0.2381, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.059 | 2017: +0.015 | 2018: +0.089 | 2019: +0.143 | 2020: +0.060 | 2021: +0.152 | 2022: +0.105 | 2023: +0.182 | 2024: +0.089 | 2025: +0.156 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.302 | 2016: -0.210 | 2017: -0.059 | 2018: +0.179 | 2019: +0.396 | 2020: +0.195 | 2021: +0.115 | 2022: +0.089 | 2023: +0.274 | 2024: +0.098 | 2025: +0.133 | 2026: -0.013
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.33, Recency ratio=1.06
- Early IC=+0.1161, Recent IC=+0.1226, 1st-half IC=+0.1017, 2nd-half IC=+0.1349, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.154, Q3_mid=+0.123, Q4=+0.099, Q5_high_vol=+0.106

**`opening_drive_thrust_ratio`** (Lock IC=-0.0464, Sharpe=-0.7909)
- Admission: Train IC=+0.2628, Deflated=+0.2631, IR=0.92, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.045 | 2017: +0.030 | 2018: +0.088 | 2019: +0.188 | 2020: +0.095 | 2021: +0.133 | 2022: +0.085 | 2023: +0.199 | 2024: +0.100 | 2025: +0.166 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.041 | 2017: -0.006 | 2018: +0.191 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.198 | 2025: +0.229 | 2026: -0.077
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=0.97
- Early IC=+0.1377, Recent IC=+0.1332, 1st-half IC=+0.1162, 2nd-half IC=+0.1402, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.155, Q3_mid=+0.111, Q4=+0.134, Q5_high_vol=+0.148

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=-0.0120, Sharpe=-0.7424)
- Admission: Train IC=+0.1753, Deflated=+0.1755, IR=0.56, Mono=0.69, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.072 | 2017: +0.048 | 2018: +0.141 | 2019: +0.136 | 2020: +0.103 | 2021: +0.157 | 2022: +0.086 | 2023: +0.174 | 2024: +0.063 | 2025: +0.159 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.010 | 2017: +0.168 | 2018: +0.224 | 2019: +0.146 | 2020: +0.023 | 2021: +0.342 | 2022: +0.154 | 2023: +0.291 | 2024: +0.090 | 2025: +0.221 | 2026: +0.017
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.80
- Early IC=+0.1383, Recent IC=+0.1112, 1st-half IC=+0.1284, 2nd-half IC=+0.1167, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32, neg years=0)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.128, Q3_mid=+0.108, Q4=+0.104, Q5_high_vol=+0.143

**`combo_rank_max__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0256, Sharpe=-0.7046)
- Admission: Train IC=+0.1989, Deflated=+0.1995, IR=0.46, Mono=0.70, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.128 | 2017: +0.017 | 2018: +0.117 | 2019: +0.199 | 2020: +0.067 | 2021: +0.214 | 2022: +0.026 | 2023: +0.151 | 2024: +0.038 | 2025: +0.158 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.127 | 2016: -0.148 | 2017: +0.102 | 2018: +0.310 | 2019: +0.437 | 2020: -0.057 | 2021: +0.296 | 2022: +0.078 | 2023: +0.232 | 2024: +0.064 | 2025: +0.316 | 2026: -0.033
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.62
- Early IC=+0.1596, Recent IC=+0.0994, 1st-half IC=+0.1412, 2nd-half IC=+0.0975, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.133, Q3_mid=+0.125, Q4=+0.092, Q5_high_vol=+0.125

**`combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=-0.0113, Sharpe=-0.6553)
- Admission: Train IC=+0.2409, Deflated=+0.2412, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.040 | 2017: +0.025 | 2018: +0.074 | 2019: +0.111 | 2020: +0.092 | 2021: +0.137 | 2022: +0.102 | 2023: +0.192 | 2024: +0.083 | 2025: +0.168 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.158 | 2017: +0.022 | 2018: +0.108 | 2019: +0.306 | 2020: +0.150 | 2021: +0.140 | 2022: +0.174 | 2023: +0.414 | 2024: +0.275 | 2025: +0.390 | 2026: -0.121
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.49, Recency ratio=1.36
- Early IC=+0.0924, Recent IC=+0.1255, 1st-half IC=+0.0946, 2nd-half IC=+0.1412, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.148, Q3_mid=+0.086, Q4=+0.128, Q5_high_vol=+0.156

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=-0.0939, Sharpe=-0.6519)
- Admission: Train IC=+0.1824, Deflated=+0.1822, IR=0.52, Mono=0.66, p=0.0004, MaxCorr=0.46
- Yearly Linear ICs: 2015: -0.056 | 2016: +0.122 | 2017: +0.039 | 2018: +0.070 | 2019: +0.033 | 2020: +0.092 | 2021: +0.057 | 2022: +0.068 | 2023: +0.063 | 2024: -0.008 | 2025: +0.083 | 2026: -0.094
- Yearly Tail ICs:   2015: -0.035 | 2016: +0.360 | 2017: +0.106 | 2018: +0.267 | 2019: +0.035 | 2020: +0.262 | 2021: +0.307 | 2022: +0.190 | 2023: +0.227 | 2024: +0.141 | 2025: +0.220 | 2026: +0.118
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=0.59, Recency ratio=0.73
- Early IC=+0.0517, Recent IC=+0.0375, 1st-half IC=+0.0761, 2nd-half IC=+0.0449, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44, neg years=0)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.078, Q3_mid=+0.015, Q4=+0.103, Q5_high_vol=+0.074

**`combo_mean__bar_body_rng_0__impulse_bar_dominance`** (Lock IC=-0.0230, Sharpe=-0.3944)
- Admission: Train IC=+0.2224, Deflated=+0.2227, IR=0.61, Mono=0.75, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.078 | 2017: +0.009 | 2018: +0.090 | 2019: +0.132 | 2020: +0.107 | 2021: +0.149 | 2022: +0.102 | 2023: +0.152 | 2024: +0.065 | 2025: +0.179 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.347 | 2016: -0.080 | 2017: -0.042 | 2018: +0.192 | 2019: +0.387 | 2020: +0.184 | 2021: +0.192 | 2022: +0.051 | 2023: +0.305 | 2024: +0.148 | 2025: +0.369 | 2026: -0.010
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.10
- Early IC=+0.1107, Recent IC=+0.1221, 1st-half IC=+0.1103, 2nd-half IC=+0.1246, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.142, Q3_mid=+0.126, Q4=+0.096, Q5_high_vol=+0.127

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0570, Sharpe=-0.3265)
- Admission: Train IC=+0.2368, Deflated=+0.2369, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.093 | 2017: +0.067 | 2018: +0.066 | 2019: +0.189 | 2020: +0.059 | 2021: +0.197 | 2022: +0.058 | 2023: +0.172 | 2024: +0.094 | 2025: +0.172 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.042 | 2016: +0.036 | 2017: +0.148 | 2018: +0.180 | 2019: +0.343 | 2020: +0.115 | 2021: +0.263 | 2022: +0.121 | 2023: +0.434 | 2024: +0.181 | 2025: +0.218 | 2026: -0.058
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.04
- Early IC=+0.1278, Recent IC=+0.1328, 1st-half IC=+0.1230, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.169, Q3_mid=+0.136, Q4=+0.119, Q5_high_vol=+0.122

**`combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return`** (Lock IC=-0.0010, Sharpe=-0.2680)
- Admission: Train IC=+0.2323, Deflated=+0.2327, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.136 | 2017: +0.017 | 2018: +0.127 | 2019: +0.181 | 2020: +0.100 | 2021: +0.122 | 2022: +0.120 | 2023: +0.156 | 2024: +0.073 | 2025: +0.130 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.394 | 2016: -0.046 | 2017: +0.158 | 2018: +0.232 | 2019: +0.374 | 2020: +0.108 | 2021: +0.281 | 2022: +0.171 | 2023: +0.534 | 2024: +0.062 | 2025: +0.190 | 2026: +0.134
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.66
- Early IC=+0.1540, Recent IC=+0.1015, 1st-half IC=+0.1252, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.141, Q3_mid=+0.122, Q4=+0.104, Q5_high_vol=+0.125

**`combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=-0.0835, Sharpe=-0.1351)
- Admission: Train IC=+0.2722, Deflated=+0.2723, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.012 | 2017: +0.036 | 2018: +0.059 | 2019: +0.130 | 2020: +0.067 | 2021: +0.159 | 2022: +0.131 | 2023: +0.172 | 2024: +0.084 | 2025: +0.133 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.356 | 2016: -0.299 | 2017: +0.059 | 2018: +0.211 | 2019: +0.348 | 2020: +0.248 | 2021: +0.214 | 2022: +0.187 | 2023: +0.336 | 2024: +0.096 | 2025: +0.234 | 2026: +0.041
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.44, Recency ratio=1.15
- Early IC=+0.0944, Recent IC=+0.1086, 1st-half IC=+0.0926, 2nd-half IC=+0.1332, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.143, Q3_mid=+0.109, Q4=+0.104, Q5_high_vol=+0.130

**`combo_mean__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0010, Sharpe=+0.5553)
- Admission: Train IC=+0.1890, Deflated=+0.1896, IR=0.49, Mono=0.68, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.124 | 2017: +0.054 | 2018: +0.088 | 2019: +0.199 | 2020: +0.064 | 2021: +0.178 | 2022: +0.038 | 2023: +0.150 | 2024: +0.064 | 2025: +0.137 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.060 | 2016: -0.121 | 2017: +0.165 | 2018: +0.195 | 2019: +0.316 | 2020: +0.104 | 2021: +0.328 | 2022: +0.051 | 2023: +0.316 | 2024: +0.071 | 2025: +0.300 | 2026: +0.040
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.70
- Early IC=+0.1437, Recent IC=+0.1002, 1st-half IC=+0.1247, 2nd-half IC=+0.1004, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.138, Q3_mid=+0.130, Q4=+0.083, Q5_high_vol=+0.113

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0844, Sharpe=-0.8307)
- Admission: Train IC=+0.1651, Deflated=+0.1639, IR=0.46, Mono=0.70, p=0.0010, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.136 | 2017: +0.014 | 2018: +0.180 | 2019: +0.026 | 2020: +0.037 | 2021: +0.151 | 2022: +0.086 | 2023: +0.056 | 2024: +0.030 | 2025: +0.030 | 2026: +0.084
- Yearly Tail ICs:   2015: -0.120 | 2016: +0.095 | 2017: +0.005 | 2018: +0.322 | 2019: +0.051 | 2020: +0.163 | 2021: +0.213 | 2022: +0.361 | 2023: -0.043 | 2024: +0.122 | 2025: +0.063 | 2026: +0.003
- IC CV=0.75, Neg years (linear/tail)=0/1 of 8, Half ratio=0.60, Recency ratio=0.29
- Early IC=+0.1029, Recent IC=+0.0298, 1st-half IC=+0.1000, 2nd-half IC=+0.0602, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.050, Q3_mid=+0.001, Q4=+0.061, Q5_high_vol=+0.211

**`combo_mean__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0709, Sharpe=-1.0140)
- Admission: Train IC=+0.2116, Deflated=+0.2114, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.096 | 2017: -0.002 | 2018: +0.188 | 2019: +0.108 | 2020: +0.040 | 2021: +0.145 | 2022: +0.058 | 2023: +0.080 | 2024: +0.009 | 2025: +0.070 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.088 | 2016: -0.003 | 2017: -0.126 | 2018: +0.342 | 2019: +0.206 | 2020: +0.154 | 2021: +0.319 | 2022: +0.191 | 2023: +0.012 | 2024: +0.143 | 2025: +0.265 | 2026: +0.103
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.27
- Early IC=+0.1480, Recent IC=+0.0393, 1st-half IC=+0.1188, 2nd-half IC=+0.0638, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.069, Q3_mid=+0.025, Q4=+0.077, Q5_high_vol=+0.206

**`combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0628, Sharpe=-1.0546)
- Admission: Train IC=+0.2228, Deflated=+0.2225, IR=0.69, Mono=0.78, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.080 | 2016: +0.038 | 2017: -0.059 | 2018: +0.148 | 2019: +0.086 | 2020: +0.037 | 2021: +0.141 | 2022: +0.100 | 2023: +0.078 | 2024: -0.005 | 2025: +0.073 | 2026: +0.063
- Yearly Tail ICs:   2015: +0.053 | 2016: +0.072 | 2017: -0.142 | 2018: +0.326 | 2019: +0.208 | 2020: +0.140 | 2021: +0.514 | 2022: +0.343 | 2023: +0.200 | 2024: +0.116 | 2025: +0.032 | 2026: -0.004
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=0.72, Recency ratio=0.29
- Early IC=+0.1168, Recent IC=+0.0341, 1st-half IC=+0.1034, 2nd-half IC=+0.0742, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.077, Q3_mid=+0.042, Q4=+0.087, Q5_high_vol=+0.153

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0449, Sharpe=-0.4434)
- Admission: Train IC=+0.2156, Deflated=+0.2157, IR=0.57, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.114 | 2017: +0.001 | 2018: +0.209 | 2019: +0.104 | 2020: +0.047 | 2021: +0.143 | 2022: +0.084 | 2023: +0.106 | 2024: +0.017 | 2025: +0.066 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.122 | 2017: +0.031 | 2018: +0.276 | 2019: +0.240 | 2020: +0.156 | 2021: +0.436 | 2022: +0.268 | 2023: +0.063 | 2024: +0.162 | 2025: +0.227 | 2026: +0.111
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.26
- Early IC=+0.1567, Recent IC=+0.0412, 1st-half IC=+0.1264, 2nd-half IC=+0.0747, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.075, Q3_mid=+0.036, Q4=+0.075, Q5_high_vol=+0.229

**`combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0035, Sharpe=-0.5291)
- Admission: Train IC=+0.1334, Deflated=+0.1332, IR=0.45, Mono=0.69, p=0.0076, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.116 | 2017: -0.053 | 2018: +0.135 | 2019: +0.036 | 2020: +0.054 | 2021: +0.124 | 2022: +0.102 | 2023: +0.107 | 2024: +0.023 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: -0.075 | 2016: +0.136 | 2017: -0.077 | 2018: +0.162 | 2019: +0.111 | 2020: +0.082 | 2021: +0.179 | 2022: +0.191 | 2023: +0.154 | 2024: +0.082 | 2025: +0.186 | 2026: +0.024
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.50
- Early IC=+0.0859, Recent IC=+0.0426, 1st-half IC=+0.0871, 2nd-half IC=+0.0822, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.057, Q3_mid=+0.011, Q4=+0.057, Q5_high_vol=+0.232

**`combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0005, Sharpe=-0.7605)
- Admission: Train IC=+0.2501, Deflated=+0.2501, IR=0.86, Mono=0.82, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.095 | 2017: +0.021 | 2018: +0.206 | 2019: +0.107 | 2020: +0.039 | 2021: +0.137 | 2022: +0.068 | 2023: +0.128 | 2024: +0.016 | 2025: +0.091 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.019 | 2017: -0.030 | 2018: +0.318 | 2019: +0.156 | 2020: +0.270 | 2021: +0.383 | 2022: +0.324 | 2023: +0.229 | 2024: +0.151 | 2025: +0.278 | 2026: +0.096
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.34
- Early IC=+0.1564, Recent IC=+0.0536, 1st-half IC=+0.1257, 2nd-half IC=+0.0799, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.082, Q3_mid=+0.053, Q4=+0.099, Q5_high_vol=+0.205

### 500ETF — `single` Median Features

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1008, Sharpe=-0.4764)
- Admission: Train IC=+0.1726, Deflated=+0.1721, IR=0.63, Mono=0.71, p=0.0002, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.306 | 2016: +0.037 | 2017: +0.234 | 2018: +0.103 | 2019: +0.112 | 2020: +0.115 | 2021: +0.047 | 2022: +0.058 | 2023: +0.048 | 2024: +0.104 | 2025: +0.097 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.300 | 2016: +0.158 | 2017: +0.194 | 2018: +0.219 | 2019: +0.360 | 2020: +0.197 | 2021: +0.177 | 2022: +0.102 | 2023: +0.037 | 2024: +0.240 | 2025: +0.009 | 2026: +0.182
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.93
- Early IC=+0.1073, Recent IC=+0.1001, 1st-half IC=+0.0920, 2nd-half IC=+0.0847, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.037, Q3_mid=+0.121, Q4=+0.104, Q5_high_vol=+0.105

**`combo_clamp_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0988, Sharpe=-1.7785)
- Admission: Train IC=+0.2389, Deflated=+0.2402, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.323 | 2016: +0.111 | 2017: +0.189 | 2018: +0.218 | 2019: +0.122 | 2020: +0.148 | 2021: +0.153 | 2022: +0.060 | 2023: +0.093 | 2024: +0.126 | 2025: +0.012 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.442 | 2016: +0.250 | 2017: +0.401 | 2018: +0.324 | 2019: +0.401 | 2020: +0.165 | 2021: +0.163 | 2022: +0.195 | 2023: +0.074 | 2024: +0.214 | 2025: +0.011 | 2026: +0.015
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.41
- Early IC=+0.1699, Recent IC=+0.0692, 1st-half IC=+0.1524, 2nd-half IC=+0.0795, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.003, Q3_mid=+0.087, Q4=+0.129, Q5_high_vol=+0.210

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0832, Sharpe=-0.6640)
- Admission: Train IC=+0.2105, Deflated=+0.2116, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.038 | 2017: +0.197 | 2018: +0.197 | 2019: +0.185 | 2020: +0.169 | 2021: +0.124 | 2022: +0.053 | 2023: +0.102 | 2024: +0.112 | 2025: +0.042 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.069 | 2017: +0.244 | 2018: +0.343 | 2019: +0.427 | 2020: +0.180 | 2021: +0.177 | 2022: +0.220 | 2023: +0.183 | 2024: +0.256 | 2025: +0.102 | 2026: +0.024
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.40
- Early IC=+0.1912, Recent IC=+0.0771, 1st-half IC=+0.1640, 2nd-half IC=+0.0846, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.014, Q3_mid=+0.134, Q4=+0.134, Q5_high_vol=+0.198

**`combo_sig_product__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0770, Sharpe=-1.1229)
- Admission: Train IC=+0.1351, Deflated=+0.1332, IR=0.32, Mono=0.66, p=0.0070, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.033 | 2017: +0.170 | 2018: +0.017 | 2019: +0.057 | 2020: +0.092 | 2021: +0.065 | 2022: +0.072 | 2023: +0.104 | 2024: +0.166 | 2025: +0.077 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.017 | 2017: +0.208 | 2018: +0.083 | 2019: +0.148 | 2020: +0.233 | 2021: +0.080 | 2022: +0.059 | 2023: +0.230 | 2024: +0.221 | 2025: -0.035 | 2026: +0.049
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.92, Recency ratio=3.30
- Early IC=+0.0368, Recent IC=+0.1213, 1st-half IC=+0.0581, 2nd-half IC=+0.1118, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.109, Q3_mid=+0.060, Q4=+0.083, Q5_high_vol=+0.081

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0727, Sharpe=-0.4830)
- Admission: Train IC=+0.2243, Deflated=+0.2234, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.124 | 2017: +0.150 | 2018: +0.156 | 2019: +0.097 | 2020: +0.138 | 2021: +0.058 | 2022: +0.125 | 2023: +0.072 | 2024: +0.090 | 2025: +0.111 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.236 | 2016: +0.259 | 2017: +0.235 | 2018: +0.337 | 2019: +0.292 | 2020: +0.180 | 2021: +0.120 | 2022: +0.248 | 2023: +0.178 | 2024: +0.198 | 2025: +0.119 | 2026: +0.107
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.80
- Early IC=+0.1265, Recent IC=+0.1008, 1st-half IC=+0.1204, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.078, Q3_mid=+0.131, Q4=+0.083, Q5_high_vol=+0.158

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0695, Sharpe=-0.8397)
- Admission: Train IC=+0.1625, Deflated=+0.1614, IR=0.42, Mono=0.68, p=0.0006, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.097 | 2021: +0.025 | 2022: +0.154 | 2023: +0.090 | 2024: +0.103 | 2025: +0.093 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.377 | 2017: +0.216 | 2018: +0.137 | 2019: +0.181 | 2020: +0.126 | 2021: +0.107 | 2022: +0.164 | 2023: +0.128 | 2024: +0.236 | 2025: -0.002 | 2026: -0.189
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=0.77
- Early IC=+0.1257, Recent IC=+0.0965, 1st-half IC=+0.0984, 2nd-half IC=+0.1146, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.081, Q3_mid=+0.131, Q4=+0.066, Q5_high_vol=+0.142

**`combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0678, Sharpe=-0.4181)
- Admission: Train IC=+0.1677, Deflated=+0.1665, IR=0.43, Mono=0.69, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.080 | 2017: +0.215 | 2018: +0.137 | 2019: +0.110 | 2020: +0.128 | 2021: +0.033 | 2022: +0.111 | 2023: +0.054 | 2024: +0.109 | 2025: +0.125 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.113 | 2017: +0.199 | 2018: +0.134 | 2019: +0.246 | 2020: +0.137 | 2021: +0.114 | 2022: +0.290 | 2023: +0.072 | 2024: +0.095 | 2025: +0.097 | 2026: -0.030
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.95
- Early IC=+0.1232, Recent IC=+0.1168, 1st-half IC=+0.1039, 2nd-half IC=+0.1096, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.082, Q3_mid=+0.124, Q4=+0.088, Q5_high_vol=+0.147

**`combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0600, Sharpe=-2.2650)
- Admission: Train IC=+0.1877, Deflated=+0.1868, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.069 | 2017: +0.208 | 2018: +0.142 | 2019: +0.115 | 2020: +0.108 | 2021: +0.020 | 2022: +0.149 | 2023: +0.073 | 2024: +0.106 | 2025: +0.127 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.188 | 2016: -0.046 | 2017: +0.199 | 2018: +0.129 | 2019: +0.273 | 2020: +0.064 | 2021: +0.207 | 2022: +0.324 | 2023: +0.148 | 2024: +0.159 | 2025: +0.155 | 2026: -0.334
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=0.90
- Early IC=+0.1280, Recent IC=+0.1153, 1st-half IC=+0.0978, 2nd-half IC=+0.1234, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.091, Q3_mid=+0.125, Q4=+0.089, Q5_high_vol=+0.145

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0508, Sharpe=-0.9929)
- Admission: Train IC=+0.2144, Deflated=+0.2135, IR=0.79, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.126 | 2017: +0.220 | 2018: +0.215 | 2019: +0.107 | 2020: +0.162 | 2021: +0.106 | 2022: +0.112 | 2023: +0.085 | 2024: +0.107 | 2025: +0.138 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.313 | 2016: +0.229 | 2017: +0.231 | 2018: +0.361 | 2019: +0.319 | 2020: +0.194 | 2021: +0.264 | 2022: +0.246 | 2023: +0.177 | 2024: +0.201 | 2025: -0.040 | 2026: -0.043
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.79, Recency ratio=0.76
- Early IC=+0.1614, Recent IC=+0.1227, 1st-half IC=+0.1496, 2nd-half IC=+0.1181, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.30)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.080, Q3_mid=+0.135, Q4=+0.126, Q5_high_vol=+0.204

**`combo_sig_product__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0462, Sharpe=-0.0784)
- Admission: Train IC=+0.1271, Deflated=+0.1284, IR=0.47, Mono=0.67, p=0.0100, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.197 | 2017: +0.127 | 2018: +0.149 | 2019: +0.108 | 2020: +0.102 | 2021: +0.144 | 2022: +0.102 | 2023: +0.068 | 2024: +0.148 | 2025: +0.112 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.268 | 2016: +0.261 | 2017: +0.365 | 2018: +0.261 | 2019: +0.238 | 2020: +0.219 | 2021: +0.190 | 2022: -0.155 | 2023: +0.128 | 2024: +0.130 | 2025: +0.112 | 2026: +0.100
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=1.01
- Early IC=+0.1286, Recent IC=+0.1303, 1st-half IC=+0.1216, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.073, Q3_mid=+0.083, Q4=+0.102, Q5_high_vol=+0.174

**`combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0383, Sharpe=-0.6718)
- Admission: Train IC=+0.1960, Deflated=+0.1967, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.035 | 2017: +0.155 | 2018: +0.220 | 2019: +0.177 | 2020: +0.185 | 2021: +0.159 | 2022: +0.043 | 2023: +0.091 | 2024: +0.139 | 2025: +0.073 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.377 | 2016: +0.013 | 2017: +0.285 | 2018: +0.362 | 2019: +0.293 | 2020: -0.007 | 2021: +0.350 | 2022: +0.127 | 2023: +0.181 | 2024: +0.187 | 2025: +0.134 | 2026: +0.080
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.53
- Early IC=+0.1986, Recent IC=+0.1059, 1st-half IC=+0.1771, 2nd-half IC=+0.0942, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.032, Q3_mid=+0.139, Q4=+0.137, Q5_high_vol=+0.224

**`combo_rank_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0380, Sharpe=-0.7326)
- Admission: Train IC=+0.1772, Deflated=+0.1772, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.048 | 2017: +0.223 | 2018: +0.166 | 2019: +0.110 | 2020: +0.147 | 2021: +0.099 | 2022: +0.078 | 2023: +0.080 | 2024: +0.120 | 2025: +0.121 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.050 | 2017: +0.153 | 2018: +0.091 | 2019: +0.327 | 2020: +0.059 | 2021: +0.353 | 2022: +0.208 | 2023: +0.072 | 2024: +0.188 | 2025: +0.122 | 2026: -0.052
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.87
- Early IC=+0.1374, Recent IC=+0.1193, 1st-half IC=+0.1257, 2nd-half IC=+0.1043, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.047, Q3_mid=+0.159, Q4=+0.161, Q5_high_vol=+0.126

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0350, Sharpe=-0.6199)
- Admission: Train IC=+0.2348, Deflated=+0.2340, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.103 | 2017: +0.203 | 2018: +0.098 | 2019: +0.071 | 2020: +0.126 | 2021: +0.118 | 2022: +0.059 | 2023: +0.103 | 2024: +0.132 | 2025: +0.123 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.276 | 2017: +0.289 | 2018: +0.349 | 2019: +0.081 | 2020: +0.218 | 2021: +0.217 | 2022: +0.222 | 2023: -0.029 | 2024: +0.406 | 2025: +0.202 | 2026: +0.197
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=1.06, Recency ratio=1.52
- Early IC=+0.0842, Recent IC=+0.1276, 1st-half IC=+0.1016, 2nd-half IC=+0.1074, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.062, Q3_mid=+0.125, Q4=+0.087, Q5_high_vol=+0.151

**`combo_clamp_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0343, Sharpe=-1.7348)
- Admission: Train IC=+0.2108, Deflated=+0.2115, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.049 | 2017: +0.156 | 2018: +0.229 | 2019: +0.176 | 2020: +0.194 | 2021: +0.152 | 2022: +0.044 | 2023: +0.093 | 2024: +0.146 | 2025: +0.071 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.307 | 2016: -0.123 | 2017: +0.171 | 2018: +0.325 | 2019: +0.307 | 2020: +0.159 | 2021: +0.111 | 2022: +0.211 | 2023: +0.027 | 2024: +0.177 | 2025: +0.126 | 2026: -0.120
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.54
- Early IC=+0.2023, Recent IC=+0.1086, 1st-half IC=+0.1794, 2nd-half IC=+0.0963, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.027, Q3_mid=+0.139, Q4=+0.144, Q5_high_vol=+0.231

**`max_down_ret`** (Lock IC=+0.0305, Sharpe=-0.4315)
- Admission: Train IC=+0.1554, Deflated=+0.1554, IR=0.59, Mono=0.71, p=0.0016, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.052 | 2017: +0.240 | 2018: +0.131 | 2019: +0.112 | 2020: +0.138 | 2021: +0.064 | 2022: +0.057 | 2023: +0.031 | 2024: +0.115 | 2025: +0.129 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.013 | 2017: +0.236 | 2018: +0.099 | 2019: +0.326 | 2020: +0.060 | 2021: +0.325 | 2022: +0.141 | 2023: +0.096 | 2024: +0.230 | 2025: +0.240 | 2026: +0.035
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=1.00
- Early IC=+0.1213, Recent IC=+0.1218, 1st-half IC=+0.1057, 2nd-half IC=+0.0912, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.039, Q3_mid=+0.160, Q4=+0.126, Q5_high_vol=+0.111

**`combo_rank_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0298, Sharpe=-0.8460)
- Admission: Train IC=+0.1703, Deflated=+0.1704, IR=0.60, Mono=0.72, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.090 | 2017: +0.239 | 2018: +0.234 | 2019: +0.150 | 2020: +0.126 | 2021: +0.098 | 2022: +0.093 | 2023: +0.036 | 2024: +0.117 | 2025: +0.112 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.605 | 2016: -0.121 | 2017: +0.202 | 2018: +0.245 | 2019: +0.306 | 2020: +0.177 | 2021: +0.248 | 2022: +0.130 | 2023: +0.169 | 2024: +0.217 | 2025: +0.104 | 2026: -0.076
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.59
- Early IC=+0.1909, Recent IC=+0.1133, 1st-half IC=+0.1470, 2nd-half IC=+0.0977, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.015, Q3_mid=+0.141, Q4=+0.150, Q5_high_vol=+0.168

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.0274, Sharpe=-0.1044)
- Admission: Train IC=+0.1472, Deflated=+0.1485, IR=0.52, Mono=0.67, p=0.0028, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.189 | 2017: +0.110 | 2018: +0.146 | 2019: +0.095 | 2020: +0.102 | 2021: +0.103 | 2022: +0.077 | 2023: +0.045 | 2024: +0.150 | 2025: +0.106 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.378 | 2016: +0.305 | 2017: +0.085 | 2018: +0.217 | 2019: +0.090 | 2020: +0.198 | 2021: +0.167 | 2022: +0.008 | 2023: +0.036 | 2024: +0.116 | 2025: +0.161 | 2026: +0.238
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=1.06
- Early IC=+0.1205, Recent IC=+0.1278, 1st-half IC=+0.1118, 2nd-half IC=+0.1013, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.005, Q3_mid=+0.074, Q4=+0.115, Q5_high_vol=+0.174

**`combo_mean__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0243, Sharpe=-0.4315)
- Admission: Train IC=+0.1673, Deflated=+0.1673, IR=0.63, Mono=0.71, p=0.0004, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.090 | 2017: +0.193 | 2018: +0.172 | 2019: +0.140 | 2020: +0.121 | 2021: +0.094 | 2022: +0.078 | 2023: +0.032 | 2024: +0.113 | 2025: +0.135 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.369 | 2016: -0.029 | 2017: +0.117 | 2018: +0.185 | 2019: +0.327 | 2020: +0.036 | 2021: +0.312 | 2022: +0.148 | 2023: +0.158 | 2024: +0.290 | 2025: +0.176 | 2026: +0.035
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.80
- Early IC=+0.1556, Recent IC=+0.1240, 1st-half IC=+0.1247, 2nd-half IC=+0.0980, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.010, Q3_mid=+0.162, Q4=+0.141, Q5_high_vol=+0.140

**`combo_rank_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0234, Sharpe=-1.0720)
- Admission: Train IC=+0.1946, Deflated=+0.1942, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.077 | 2017: +0.236 | 2018: +0.132 | 2019: +0.097 | 2020: +0.142 | 2021: +0.054 | 2022: +0.084 | 2023: +0.081 | 2024: +0.112 | 2025: +0.135 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.285 | 2016: -0.076 | 2017: +0.295 | 2018: +0.113 | 2019: +0.263 | 2020: +0.207 | 2021: +0.349 | 2022: +0.282 | 2023: +0.266 | 2024: +0.142 | 2025: +0.162 | 2026: -0.067
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=1.08
- Early IC=+0.1149, Recent IC=+0.1241, 1st-half IC=+0.1058, 2nd-half IC=+0.1103, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.046, Q3_mid=+0.166, Q4=+0.122, Q5_high_vol=+0.131

**`combo_mean__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0234, Sharpe=-0.4926)
- Admission: Train IC=+0.1783, Deflated=+0.1784, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.245 | 2018: +0.188 | 2019: +0.133 | 2020: +0.163 | 2021: +0.115 | 2022: +0.080 | 2023: +0.083 | 2024: +0.134 | 2025: +0.111 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.413 | 2016: -0.042 | 2017: +0.113 | 2018: +0.128 | 2019: +0.303 | 2020: +0.009 | 2021: +0.362 | 2022: +0.238 | 2023: +0.119 | 2024: +0.235 | 2025: +0.101 | 2026: +0.006
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.76
- Early IC=+0.1604, Recent IC=+0.1225, 1st-half IC=+0.1429, 2nd-half IC=+0.1110, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.050, Q3_mid=+0.168, Q4=+0.146, Q5_high_vol=+0.166

**`combo_max__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0228, Sharpe=-1.4122)
- Admission: Train IC=+0.1689, Deflated=+0.1688, IR=0.47, Mono=0.67, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.109 | 2017: +0.107 | 2018: +0.258 | 2019: +0.128 | 2020: +0.091 | 2021: +0.110 | 2022: +0.109 | 2023: +0.049 | 2024: +0.101 | 2025: +0.058 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.120 | 2016: +0.043 | 2017: +0.258 | 2018: +0.430 | 2019: +0.179 | 2020: +0.233 | 2021: +0.216 | 2022: +0.091 | 2023: +0.163 | 2024: +0.148 | 2025: +0.040 | 2026: -0.171
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.41
- Early IC=+0.1926, Recent IC=+0.0794, 1st-half IC=+0.1420, 2nd-half IC=+0.0869, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.001, Q3_mid=+0.109, Q4=+0.136, Q5_high_vol=+0.163

**`volume_surge_direction`** (Lock IC=+0.0202, Sharpe=-0.0698)
- Admission: Train IC=+0.1500, Deflated=+0.1495, IR=0.48, Mono=0.68, p=0.0022, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.051 | 2017: +0.049 | 2018: +0.207 | 2019: +0.121 | 2020: +0.076 | 2021: +0.087 | 2022: +0.119 | 2023: +0.027 | 2024: +0.091 | 2025: +0.101 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.383 | 2016: +0.009 | 2017: -0.016 | 2018: +0.346 | 2019: +0.253 | 2020: +0.089 | 2021: -0.050 | 2022: +0.256 | 2023: +0.037 | 2024: +0.278 | 2025: +0.182 | 2026: +0.015
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.58
- Early IC=+0.1641, Recent IC=+0.0958, 1st-half IC=+0.1160, 2nd-half IC=+0.0888, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.098, Q2=-0.010, Q3_mid=+0.091, Q4=+0.132, Q5_high_vol=+0.149

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0187, Sharpe=-0.7444)
- Admission: Train IC=+0.2197, Deflated=+0.2199, IR=0.52, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.278 | 2016: +0.108 | 2017: +0.185 | 2018: +0.222 | 2019: +0.126 | 2020: +0.112 | 2021: +0.167 | 2022: +0.099 | 2023: +0.091 | 2024: +0.134 | 2025: +0.068 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.504 | 2016: +0.114 | 2017: +0.109 | 2018: +0.317 | 2019: +0.321 | 2020: +0.076 | 2021: +0.267 | 2022: +0.324 | 2023: +0.075 | 2024: +0.084 | 2025: +0.119 | 2026: +0.022
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.58
- Early IC=+0.1738, Recent IC=+0.1010, 1st-half IC=+0.1467, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.028, Q3_mid=+0.155, Q4=+0.143, Q5_high_vol=+0.180

**`combo_rank_min__net_volume_flow__bar_ret_0`** (Lock IC=+0.0185, Sharpe=-0.4696)
- Admission: Train IC=+0.2291, Deflated=+0.2288, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.073 | 2017: +0.177 | 2018: +0.188 | 2019: +0.128 | 2020: +0.087 | 2021: +0.081 | 2022: +0.079 | 2023: +0.072 | 2024: +0.123 | 2025: +0.123 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.012 | 2017: +0.207 | 2018: +0.394 | 2019: +0.169 | 2020: +0.107 | 2021: +0.257 | 2022: +0.254 | 2023: +0.269 | 2024: +0.310 | 2025: +0.104 | 2026: +0.027
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.79
- Early IC=+0.1573, Recent IC=+0.1239, 1st-half IC=+0.1202, 2nd-half IC=+0.1062, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.032, Q3_mid=+0.129, Q4=+0.120, Q5_high_vol=+0.150

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0177, Sharpe=-1.8813)
- Admission: Train IC=+0.1939, Deflated=+0.1931, IR=0.44, Mono=0.66, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.120 | 2017: +0.197 | 2018: +0.186 | 2019: +0.120 | 2020: +0.115 | 2021: +0.090 | 2022: +0.055 | 2023: +0.027 | 2024: +0.084 | 2025: +0.133 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.174 | 2017: +0.334 | 2018: +0.177 | 2019: +0.333 | 2020: +0.149 | 2021: +0.117 | 2022: +0.152 | 2023: -0.119 | 2024: +0.186 | 2025: +0.247 | 2026: -0.229
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.71
- Early IC=+0.1530, Recent IC=+0.1086, 1st-half IC=+0.1231, 2nd-half IC=+0.0808, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.098, Q2=-0.011, Q3_mid=+0.128, Q4=+0.143, Q5_high_vol=+0.145

**`combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0175, Sharpe=-1.1506)
- Admission: Train IC=+0.2320, Deflated=+0.2306, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.075 | 2017: +0.193 | 2018: +0.138 | 2019: +0.080 | 2020: +0.127 | 2021: +0.056 | 2022: +0.085 | 2023: +0.068 | 2024: +0.099 | 2025: +0.126 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.110 | 2017: +0.268 | 2018: +0.242 | 2019: +0.231 | 2020: +0.197 | 2021: +0.213 | 2022: +0.337 | 2023: +0.193 | 2024: +0.230 | 2025: +0.207 | 2026: -0.053
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=1.04
- Early IC=+0.1089, Recent IC=+0.1129, 1st-half IC=+0.1047, 2nd-half IC=+0.1036, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.068, Q3_mid=+0.130, Q4=+0.094, Q5_high_vol=+0.133

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0152, Sharpe=-1.5740)
- Admission: Train IC=+0.2799, Deflated=+0.2799, IR=1.03, Mono=0.85, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.055 | 2017: +0.164 | 2018: +0.247 | 2019: +0.175 | 2020: +0.159 | 2021: +0.151 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.095 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.454 | 2016: +0.046 | 2017: +0.194 | 2018: +0.402 | 2019: +0.230 | 2020: +0.216 | 2021: +0.337 | 2022: +0.240 | 2023: +0.314 | 2024: +0.298 | 2025: +0.112 | 2026: -0.326
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.57
- Early IC=+0.2108, Recent IC=+0.1202, 1st-half IC=+0.1756, 2nd-half IC=+0.1085, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.040, Q3_mid=+0.152, Q4=+0.139, Q5_high_vol=+0.221

**`combo_mean__first_bar_return__max_down_ret`** (Lock IC=+0.0117, Sharpe=-2.2371)
- Admission: Train IC=+0.2258, Deflated=+0.2255, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.103 | 2017: +0.227 | 2018: +0.202 | 2019: +0.132 | 2020: +0.121 | 2021: +0.082 | 2022: +0.071 | 2023: +0.054 | 2024: +0.128 | 2025: +0.132 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.043 | 2017: +0.264 | 2018: +0.377 | 2019: +0.188 | 2020: +0.192 | 2021: +0.285 | 2022: +0.190 | 2023: +0.137 | 2024: +0.250 | 2025: +0.177 | 2026: -0.251
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.78
- Early IC=+0.1671, Recent IC=+0.1297, 1st-half IC=+0.1301, 2nd-half IC=+0.1041, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.029, Q3_mid=+0.136, Q4=+0.132, Q5_high_vol=+0.158

**`combo_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0115, Sharpe=-0.8443)
- Admission: Train IC=+0.1987, Deflated=+0.1982, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.101 | 2017: +0.181 | 2018: +0.166 | 2019: +0.129 | 2020: +0.105 | 2021: +0.083 | 2022: +0.035 | 2023: +0.063 | 2024: +0.102 | 2025: +0.139 | 2026: +0.011
- Yearly Tail ICs:   2015: +0.308 | 2016: -0.041 | 2017: +0.306 | 2018: +0.194 | 2019: +0.316 | 2020: +0.200 | 2021: +0.417 | 2022: +0.149 | 2023: +0.068 | 2024: +0.244 | 2025: +0.174 | 2026: -0.025
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.82
- Early IC=+0.1473, Recent IC=+0.1204, 1st-half IC=+0.1173, 2nd-half IC=+0.0906, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.030, Q3_mid=+0.127, Q4=+0.120, Q5_high_vol=+0.128

**`combo_min__early_body_momentum__max_down_ret`** (Lock IC=+0.0091, Sharpe=-0.9128)
- Admission: Train IC=+0.1779, Deflated=+0.1777, IR=0.56, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.065 | 2017: +0.163 | 2018: +0.106 | 2019: +0.078 | 2020: +0.120 | 2021: +0.055 | 2022: +0.107 | 2023: +0.077 | 2024: +0.107 | 2025: +0.126 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.287 | 2016: -0.113 | 2017: +0.125 | 2018: +0.073 | 2019: +0.153 | 2020: +0.144 | 2021: +0.350 | 2022: +0.318 | 2023: +0.169 | 2024: +0.227 | 2025: +0.083 | 2026: -0.056
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.27
- Early IC=+0.0919, Recent IC=+0.1166, 1st-half IC=+0.0923, 2nd-half IC=+0.1113, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.052, Q3_mid=+0.163, Q4=+0.086, Q5_high_vol=+0.127

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0077, Sharpe=-1.6646)
- Admission: Train IC=+0.1859, Deflated=+0.1860, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.098 | 2017: +0.254 | 2018: +0.239 | 2019: +0.142 | 2020: +0.131 | 2021: +0.079 | 2022: +0.098 | 2023: +0.041 | 2024: +0.124 | 2025: +0.098 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.006 | 2017: +0.199 | 2018: +0.408 | 2019: +0.110 | 2020: +0.233 | 2021: +0.218 | 2022: +0.164 | 2023: +0.240 | 2024: +0.241 | 2025: +0.034 | 2026: -0.250
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1905, Recent IC=+0.1110, 1st-half IC=+0.1432, 2nd-half IC=+0.1012, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.025, Q3_mid=+0.135, Q4=+0.139, Q5_high_vol=+0.172

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0058, Sharpe=-0.5680)
- Admission: Train IC=+0.2152, Deflated=+0.2154, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.087 | 2017: +0.213 | 2018: +0.255 | 2019: +0.157 | 2020: +0.136 | 2021: +0.097 | 2022: +0.056 | 2023: +0.069 | 2024: +0.125 | 2025: +0.114 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.396 | 2016: +0.092 | 2017: +0.352 | 2018: +0.441 | 2019: +0.187 | 2020: +0.105 | 2021: +0.292 | 2022: +0.253 | 2023: +0.166 | 2024: +0.229 | 2025: +0.116 | 2026: -0.200
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.58
- Early IC=+0.2059, Recent IC=+0.1197, 1st-half IC=+0.1580, 2nd-half IC=+0.0966, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.036, Q3_mid=+0.135, Q4=+0.157, Q5_high_vol=+0.186

**`combo_rank_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0056, Sharpe=-0.6772)
- Admission: Train IC=+0.1947, Deflated=+0.1943, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.098 | 2017: +0.201 | 2018: +0.164 | 2019: +0.130 | 2020: +0.098 | 2021: +0.071 | 2022: +0.027 | 2023: +0.056 | 2024: +0.103 | 2025: +0.123 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.344 | 2016: -0.075 | 2017: +0.320 | 2018: +0.225 | 2019: +0.326 | 2020: +0.179 | 2021: +0.349 | 2022: +0.131 | 2023: +0.073 | 2024: +0.220 | 2025: +0.160 | 2026: -0.097
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.80
- Early IC=+0.1431, Recent IC=+0.1150, 1st-half IC=+0.1109, 2nd-half IC=+0.0855, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.027, Q3_mid=+0.127, Q4=+0.118, Q5_high_vol=+0.118

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0033, Sharpe=-1.5227)
- Admission: Train IC=+0.2805, Deflated=+0.2807, IR=1.02, Mono=0.83, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.041 | 2017: +0.163 | 2018: +0.219 | 2019: +0.178 | 2020: +0.161 | 2021: +0.163 | 2022: +0.059 | 2023: +0.088 | 2024: +0.124 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.424 | 2016: +0.022 | 2017: +0.200 | 2018: +0.388 | 2019: +0.253 | 2020: +0.224 | 2021: +0.333 | 2022: +0.235 | 2023: +0.304 | 2024: +0.296 | 2025: +0.107 | 2026: -0.345
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.55
- Early IC=+0.1981, Recent IC=+0.1096, 1st-half IC=+0.1735, 2nd-half IC=+0.0981, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.028, Q3_mid=+0.140, Q4=+0.141, Q5_high_vol=+0.207

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0028, Sharpe=-1.6259)
- Admission: Train IC=+0.2776, Deflated=+0.2782, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.102 | 2017: +0.141 | 2018: +0.284 | 2019: +0.177 | 2020: +0.174 | 2021: +0.172 | 2022: +0.055 | 2023: +0.093 | 2024: +0.158 | 2025: +0.058 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.423 | 2016: +0.093 | 2017: +0.312 | 2018: +0.607 | 2019: +0.292 | 2020: +0.045 | 2021: +0.311 | 2022: +0.215 | 2023: +0.097 | 2024: +0.280 | 2025: +0.147 | 2026: -0.132
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.47
- Early IC=+0.2304, Recent IC=+0.1078, 1st-half IC=+0.1916, 2nd-half IC=+0.1013, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.031, Q3_mid=+0.124, Q4=+0.144, Q5_high_vol=+0.268

**`opening_drive_thrust_ratio`** (Lock IC=+0.0025, Sharpe=-0.8862)
- Admission: Train IC=+0.1901, Deflated=+0.1901, IR=0.68, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102 | 2024: +0.152 | 2025: +0.088 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.517 | 2016: +0.047 | 2017: +0.205 | 2018: +0.244 | 2019: +0.347 | 2020: +0.069 | 2021: +0.321 | 2022: +0.278 | 2023: +0.019 | 2024: +0.151 | 2025: +0.052 | 2026: -0.026
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.70
- Early IC=+0.1718, Recent IC=+0.1199, 1st-half IC=+0.1588, 2nd-half IC=+0.1126, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.090, Q2=+0.050, Q3_mid=+0.164, Q4=+0.146, Q5_high_vol=+0.207

### 159915ETF — `single` Median Features

**`combo_mean__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1312, Sharpe=-0.0665)
- Admission: Train IC=+0.3023, Deflated=+0.3025, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.092 | 2017: -0.030 | 2018: +0.144 | 2019: +0.228 | 2020: +0.132 | 2021: +0.130 | 2022: +0.086 | 2023: +0.107 | 2024: +0.072 | 2025: +0.136 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.206 | 2016: +0.066 | 2017: +0.124 | 2018: +0.384 | 2019: +0.440 | 2020: +0.165 | 2021: +0.275 | 2022: +0.125 | 2023: +0.164 | 2024: +0.442 | 2025: +0.243 | 2026: +0.194
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.56
- Early IC=+0.1861, Recent IC=+0.1036, 1st-half IC=+0.1511, 2nd-half IC=+0.1066, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.107, Q3_mid=+0.155, Q4=+0.101, Q5_high_vol=+0.140

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1154, Sharpe=-0.0647)
- Admission: Train IC=+0.2178, Deflated=+0.2171, IR=0.56, Mono=0.73, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.152 | 2017: -0.073 | 2018: +0.153 | 2019: +0.109 | 2020: +0.124 | 2021: +0.064 | 2022: +0.159 | 2023: +0.150 | 2024: +0.081 | 2025: +0.076 | 2026: +0.115
- Yearly Tail ICs:   2015: +0.126 | 2016: +0.243 | 2017: +0.051 | 2018: +0.348 | 2019: +0.183 | 2020: +0.377 | 2021: +0.189 | 2022: +0.357 | 2023: -0.018 | 2024: +0.160 | 2025: +0.063 | 2026: +0.197
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.99, Recency ratio=0.60
- Early IC=+0.1310, Recent IC=+0.0785, 1st-half IC=+0.1176, 2nd-half IC=+0.1162, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.132, Q3_mid=+0.116, Q4=+0.165, Q5_high_vol=+0.089

**`combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0955, Sharpe=-0.7293)
- Admission: Train IC=+0.1785, Deflated=+0.1782, IR=0.51, Mono=0.68, p=0.0006, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.026 | 2017: -0.035 | 2018: -0.032 | 2019: +0.141 | 2020: +0.055 | 2021: +0.078 | 2022: +0.111 | 2023: +0.103 | 2024: +0.110 | 2025: +0.123 | 2026: +0.096
- Yearly Tail ICs:   2015: -0.063 | 2016: +0.006 | 2017: +0.074 | 2018: -0.035 | 2019: +0.169 | 2020: +0.249 | 2021: +0.079 | 2022: +0.369 | 2023: +0.261 | 2024: +0.161 | 2025: +0.298 | 2026: -0.069
- IC CV=0.59, Neg years (linear/tail)=1/1 of 8, Half ratio=1.89, Recency ratio=2.13
- Early IC=+0.0546, Recent IC=+0.1164, 1st-half IC=+0.0621, 2nd-half IC=+0.1174, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.120, Q3_mid=+0.148, Q4=+0.054, Q5_high_vol=+0.057

**`combo_mean__limit_down_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0909, Sharpe=-0.2991)
- Admission: Train IC=+0.1661, Deflated=+0.1658, IR=0.57, Mono=0.69, p=0.0012, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.172 | 2016: -0.028 | 2017: +0.006 | 2018: +0.073 | 2019: +0.112 | 2020: +0.070 | 2021: +0.132 | 2022: +0.149 | 2023: +0.090 | 2024: +0.093 | 2025: +0.122 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.059 | 2016: +0.053 | 2017: -0.022 | 2018: +0.121 | 2019: +0.374 | 2020: +0.056 | 2021: +0.277 | 2022: +0.091 | 2023: +0.153 | 2024: +0.271 | 2025: +0.036 | 2026: +0.117
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.34, Recency ratio=1.16
- Early IC=+0.0925, Recent IC=+0.1077, 1st-half IC=+0.0921, 2nd-half IC=+0.1235, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.108, Q3_mid=+0.110, Q4=+0.118, Q5_high_vol=+0.124

**`combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0898, Sharpe=-0.9819)
- Admission: Train IC=+0.1780, Deflated=+0.1771, IR=0.53, Mono=0.69, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.138 | 2017: -0.007 | 2018: +0.134 | 2019: +0.159 | 2020: +0.130 | 2021: +0.161 | 2022: +0.116 | 2023: +0.099 | 2024: +0.067 | 2025: +0.105 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.065 | 2017: +0.044 | 2018: +0.394 | 2019: +0.128 | 2020: +0.132 | 2021: +0.402 | 2022: +0.082 | 2023: +0.212 | 2024: +0.199 | 2025: +0.152 | 2026: +0.049
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.59
- Early IC=+0.1469, Recent IC=+0.0860, 1st-half IC=+0.1449, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.100, Q3_mid=+0.149, Q4=+0.089, Q5_high_vol=+0.121

**`combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0896, Sharpe=-1.6385)
- Admission: Train IC=+0.1624, Deflated=+0.1627, IR=0.41, Mono=0.66, p=0.0022, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.137 | 2016: -0.045 | 2017: +0.051 | 2018: -0.040 | 2019: +0.105 | 2020: +0.037 | 2021: +0.092 | 2022: +0.094 | 2023: +0.070 | 2024: +0.042 | 2025: +0.111 | 2026: +0.090
- Yearly Tail ICs:   2015: -0.011 | 2016: -0.084 | 2017: +0.117 | 2018: -0.005 | 2019: +0.147 | 2020: +0.123 | 2021: +0.174 | 2022: +0.429 | 2023: +0.193 | 2024: +0.066 | 2025: +0.196 | 2026: -0.210
- IC CV=0.74, Neg years (linear/tail)=1/1 of 8, Half ratio=2.10, Recency ratio=2.34
- Early IC=+0.0327, Recent IC=+0.0767, 1st-half IC=+0.0420, 2nd-half IC=+0.0881, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.127, Q3_mid=+0.106, Q4=+0.008, Q5_high_vol=+0.020

**`combo_max__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.0866, Sharpe=-1.4591)
- Admission: Train IC=+0.1650, Deflated=+0.1643, IR=0.54, Mono=0.71, p=0.0014, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.091 | 2017: +0.015 | 2018: +0.141 | 2019: +0.117 | 2020: +0.070 | 2021: +0.160 | 2022: +0.132 | 2023: +0.111 | 2024: +0.033 | 2025: +0.109 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.077 | 2016: +0.014 | 2017: +0.282 | 2018: +0.385 | 2019: +0.138 | 2020: +0.029 | 2021: +0.349 | 2022: +0.119 | 2023: +0.165 | 2024: +0.185 | 2025: +0.199 | 2026: +0.128
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.55
- Early IC=+0.1291, Recent IC=+0.0712, 1st-half IC=+0.1215, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.107, Q3_mid=+0.112, Q4=+0.075, Q5_high_vol=+0.114

**`combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0841, Sharpe=-1.2423)
- Admission: Train IC=+0.2039, Deflated=+0.2039, IR=0.76, Mono=0.78, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.011 | 2017: +0.020 | 2018: +0.065 | 2019: +0.155 | 2020: +0.058 | 2021: +0.141 | 2022: +0.114 | 2023: +0.125 | 2024: +0.100 | 2025: +0.177 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.152 | 2016: +0.062 | 2017: +0.130 | 2018: +0.127 | 2019: +0.423 | 2020: +0.009 | 2021: +0.110 | 2022: +0.237 | 2023: +0.258 | 2024: +0.357 | 2025: +0.177 | 2026: -0.033
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.26
- Early IC=+0.1099, Recent IC=+0.1387, 1st-half IC=+0.1010, 2nd-half IC=+0.1377, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.115, Q3_mid=+0.146, Q4=+0.113, Q5_high_vol=+0.123

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0821, Sharpe=-0.0542)
- Admission: Train IC=+0.3411, Deflated=+0.3412, IR=1.00, Mono=0.84, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.114 | 2017: +0.000 | 2018: +0.160 | 2019: +0.239 | 2020: +0.149 | 2021: +0.149 | 2022: +0.102 | 2023: +0.159 | 2024: +0.106 | 2025: +0.169 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.169 | 2016: +0.016 | 2017: +0.027 | 2018: +0.286 | 2019: +0.533 | 2020: +0.285 | 2021: +0.260 | 2022: +0.187 | 2023: +0.411 | 2024: +0.504 | 2025: +0.293 | 2026: +0.029
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.69
- Early IC=+0.1992, Recent IC=+0.1376, 1st-half IC=+0.1643, 2nd-half IC=+0.1379, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.141, Q3_mid=+0.152, Q4=+0.138, Q5_high_vol=+0.178

**`combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0809, Sharpe=-0.5341)
- Admission: Train IC=+0.2000, Deflated=+0.1994, IR=0.55, Mono=0.71, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.055 | 2017: +0.020 | 2018: +0.096 | 2019: +0.109 | 2020: +0.123 | 2021: +0.161 | 2022: +0.163 | 2023: +0.130 | 2024: +0.095 | 2025: +0.160 | 2026: +0.081
- Yearly Tail ICs:   2015: -0.058 | 2016: +0.146 | 2017: +0.095 | 2018: +0.122 | 2019: +0.310 | 2020: +0.156 | 2021: +0.350 | 2022: +0.186 | 2023: +0.090 | 2024: +0.157 | 2025: +0.052 | 2026: +0.070
- IC CV=0.21, Neg years (linear/tail)=0/0 of 8, Half ratio=1.16, Recency ratio=1.25
- Early IC=+0.1022, Recent IC=+0.1277, 1st-half IC=+0.1234, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.139, Q3_mid=+0.121, Q4=+0.159, Q5_high_vol=+0.157

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0762, Sharpe=-0.1130)
- Admission: Train IC=+0.2831, Deflated=+0.2832, IR=0.97, Mono=0.83, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.039 | 2017: -0.003 | 2018: +0.047 | 2019: +0.159 | 2020: +0.082 | 2021: +0.169 | 2022: +0.100 | 2023: +0.147 | 2024: +0.086 | 2025: +0.187 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.174 | 2016: +0.207 | 2017: +0.168 | 2018: +0.204 | 2019: +0.316 | 2020: +0.189 | 2021: +0.278 | 2022: +0.259 | 2023: +0.301 | 2024: +0.363 | 2025: +0.209 | 2026: +0.100
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=1.33
- Early IC=+0.1028, Recent IC=+0.1368, 1st-half IC=+0.1101, 2nd-half IC=+0.1378, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.156, Q3_mid=+0.122, Q4=+0.136, Q5_high_vol=+0.136

**`combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0719, Sharpe=-0.7386)
- Admission: Train IC=+0.2535, Deflated=+0.2534, IR=0.88, Mono=0.82, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.127 | 2017: -0.002 | 2018: +0.156 | 2019: +0.213 | 2020: +0.166 | 2021: +0.148 | 2022: +0.127 | 2023: +0.116 | 2024: +0.093 | 2025: +0.160 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.103 | 2016: +0.196 | 2017: +0.110 | 2018: +0.269 | 2019: +0.344 | 2020: +0.191 | 2021: +0.259 | 2022: +0.275 | 2023: +0.225 | 2024: +0.390 | 2025: +0.192 | 2026: +0.083
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.69
- Early IC=+0.1845, Recent IC=+0.1265, 1st-half IC=+0.1682, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.135, Q3_mid=+0.162, Q4=+0.123, Q5_high_vol=+0.172

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0712, Sharpe=-1.1060)
- Admission: Train IC=+0.1832, Deflated=+0.1827, IR=0.59, Mono=0.71, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.021 | 2017: +0.033 | 2018: +0.073 | 2019: +0.158 | 2020: +0.050 | 2021: +0.127 | 2022: +0.136 | 2023: +0.121 | 2024: +0.109 | 2025: +0.108 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.067 | 2017: +0.104 | 2018: +0.076 | 2019: +0.356 | 2020: -0.022 | 2021: +0.237 | 2022: +0.053 | 2023: +0.176 | 2024: +0.309 | 2025: +0.181 | 2026: -0.043
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.25, Recency ratio=0.94
- Early IC=+0.1150, Recent IC=+0.1077, 1st-half IC=+0.1001, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.107, Q3_mid=+0.100, Q4=+0.111, Q5_high_vol=+0.119

**`combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0623, Sharpe=-0.0060)
- Admission: Train IC=+0.1943, Deflated=+0.1942, IR=0.70, Mono=0.73, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.049 | 2017: +0.028 | 2018: +0.063 | 2019: +0.148 | 2020: +0.113 | 2021: +0.106 | 2022: +0.164 | 2023: +0.127 | 2024: +0.133 | 2025: +0.179 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.062 | 2016: -0.009 | 2017: +0.039 | 2018: +0.020 | 2019: +0.329 | 2020: +0.244 | 2021: +0.215 | 2022: +0.293 | 2023: +0.244 | 2024: +0.211 | 2025: +0.259 | 2026: -0.089
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.56
- Early IC=+0.0976, Recent IC=+0.1519, 1st-half IC=+0.1026, 2nd-half IC=+0.1538, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.130, Q3_mid=+0.145, Q4=+0.122, Q5_high_vol=+0.124

**`combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early`** (Lock IC=+0.0606, Sharpe=-1.7296)
- Admission: Train IC=+0.3020, Deflated=+0.3020, IR=0.93, Mono=0.82, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.072 | 2017: -0.012 | 2018: +0.137 | 2019: +0.218 | 2020: +0.137 | 2021: +0.151 | 2022: +0.113 | 2023: +0.136 | 2024: +0.077 | 2025: +0.176 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.066 | 2017: +0.028 | 2018: +0.197 | 2019: +0.503 | 2020: +0.391 | 2021: +0.322 | 2022: +0.200 | 2023: +0.305 | 2024: +0.232 | 2025: +0.404 | 2026: -0.360
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.71
- Early IC=+0.1775, Recent IC=+0.1266, 1st-half IC=+0.1541, 2nd-half IC=+0.1302, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.131, Q3_mid=+0.159, Q4=+0.120, Q5_high_vol=+0.167

**`combo_sig_product__yesterday_first_30min_return__yesterday_early_trend`** (Lock IC=+0.0597, Sharpe=-1.3636)
- Admission: Train IC=+0.1262, Deflated=+0.1256, IR=0.51, Mono=0.67, p=0.0116, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.145 | 2017: -0.024 | 2018: +0.105 | 2019: +0.047 | 2020: +0.071 | 2021: -0.039 | 2022: +0.117 | 2023: +0.110 | 2024: +0.084 | 2025: +0.060 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.209 | 2016: +0.191 | 2017: -0.035 | 2018: +0.231 | 2019: +0.039 | 2020: +0.120 | 2021: +0.146 | 2022: +0.317 | 2023: +0.079 | 2024: +0.220 | 2025: +0.058 | 2026: +0.020
- IC CV=0.68, Neg years (linear/tail)=1/0 of 8, Half ratio=1.69, Recency ratio=0.95
- Early IC=+0.0761, Recent IC=+0.0723, 1st-half IC=+0.0530, 2nd-half IC=+0.0894, Neg regimes=0/5
- Weak component: `yesterday_early_trend` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.091, Q3_mid=+0.099, Q4=+0.103, Q5_high_vol=+0.004

**`combo_sig_product__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0593, Sharpe=-1.4053)
- Admission: Train IC=+0.2111, Deflated=+0.2116, IR=0.39, Mono=0.68, p=0.0002, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.023 | 2017: -0.041 | 2018: +0.034 | 2019: +0.178 | 2020: +0.072 | 2021: +0.102 | 2022: +0.100 | 2023: +0.141 | 2024: +0.127 | 2025: +0.095 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.082 | 2016: -0.086 | 2017: -0.115 | 2018: +0.174 | 2019: +0.399 | 2020: +0.074 | 2021: +0.139 | 2022: +0.066 | 2023: +0.240 | 2024: +0.223 | 2025: +0.245 | 2026: -0.129
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=1.05
- Early IC=+0.1056, Recent IC=+0.1110, 1st-half IC=+0.0997, 2nd-half IC=+0.1164, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.076, Q3_mid=+0.103, Q4=+0.134, Q5_high_vol=+0.102

**`combo_rank_max__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0586, Sharpe=-0.7006)
- Admission: Train IC=+0.1855, Deflated=+0.1848, IR=0.63, Mono=0.70, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.040 | 2017: +0.033 | 2018: +0.085 | 2019: +0.130 | 2020: +0.074 | 2021: +0.174 | 2022: +0.173 | 2023: +0.138 | 2024: +0.083 | 2025: +0.135 | 2026: +0.066
- Yearly Tail ICs:   2015: -0.079 | 2016: +0.151 | 2017: +0.228 | 2018: +0.286 | 2019: +0.176 | 2020: +0.034 | 2021: +0.404 | 2022: +0.201 | 2023: +0.136 | 2024: +0.197 | 2025: +0.015 | 2026: -0.068
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.12, Recency ratio=1.01
- Early IC=+0.1069, Recent IC=+0.1084, 1st-half IC=+0.1205, 2nd-half IC=+0.1351, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.135, Q3_mid=+0.109, Q4=+0.142, Q5_high_vol=+0.112

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0567, Sharpe=-0.2824)
- Admission: Train IC=+0.2873, Deflated=+0.2878, IR=0.85, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.111 | 2017: +0.019 | 2018: +0.092 | 2019: +0.236 | 2020: +0.120 | 2021: +0.123 | 2022: +0.094 | 2023: +0.163 | 2024: +0.069 | 2025: +0.212 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.012 | 2017: +0.044 | 2018: +0.244 | 2019: +0.488 | 2020: +0.226 | 2021: +0.204 | 2022: +0.100 | 2023: +0.356 | 2024: +0.285 | 2025: +0.437 | 2026: +0.184
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.86
- Early IC=+0.1639, Recent IC=+0.1405, 1st-half IC=+0.1358, 2nd-half IC=+0.1376, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.156, Q3_mid=+0.141, Q4=+0.109, Q5_high_vol=+0.156

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0545, Sharpe=-1.0195)
- Admission: Train IC=+0.2337, Deflated=+0.2336, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.062 | 2017: +0.025 | 2018: +0.083 | 2019: +0.156 | 2020: +0.108 | 2021: +0.161 | 2022: +0.134 | 2023: +0.133 | 2024: +0.115 | 2025: +0.195 | 2026: +0.054
- Yearly Tail ICs:   2015: -0.047 | 2016: +0.154 | 2017: +0.143 | 2018: +0.089 | 2019: +0.405 | 2020: +0.118 | 2021: +0.196 | 2022: +0.227 | 2023: +0.278 | 2024: +0.389 | 2025: +0.217 | 2026: -0.043
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.30
- Early IC=+0.1191, Recent IC=+0.1548, 1st-half IC=+0.1251, 2nd-half IC=+0.1522, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.145, Q3_mid=+0.139, Q4=+0.145, Q5_high_vol=+0.157

**`combo_clamp_diff__volume_weighted_price_position__late_bar_momentum`** (Lock IC=+0.0458, Sharpe=-1.2891)
- Admission: Train IC=+0.1641, Deflated=+0.1648, IR=0.46, Mono=0.67, p=0.0016, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.056 | 2017: +0.050 | 2018: +0.076 | 2019: +0.238 | 2020: +0.061 | 2021: +0.100 | 2022: +0.034 | 2023: +0.148 | 2024: +0.057 | 2025: +0.069 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.153 | 2016: -0.105 | 2017: +0.046 | 2018: +0.193 | 2019: +0.445 | 2020: +0.048 | 2021: +0.195 | 2022: -0.003 | 2023: +0.185 | 2024: +0.042 | 2025: +0.174 | 2026: -0.144
- IC CV=0.63, Neg years (linear/tail)=0/1 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.1569, Recent IC=+0.0632, 1st-half IC=+0.1089, 2nd-half IC=+0.0833, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.103, Q3_mid=+0.089, Q4=+0.102, Q5_high_vol=+0.092

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.0426, Sharpe=-0.5756)
- Admission: Train IC=+0.2373, Deflated=+0.2381, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.124 | 2017: +0.032 | 2018: +0.087 | 2019: +0.187 | 2020: +0.124 | 2021: +0.164 | 2022: +0.127 | 2023: +0.154 | 2024: +0.046 | 2025: +0.175 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.182 | 2017: +0.118 | 2018: +0.272 | 2019: +0.240 | 2020: +0.126 | 2021: +0.407 | 2022: +0.229 | 2023: +0.208 | 2024: +0.171 | 2025: +0.261 | 2026: +0.067
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.81
- Early IC=+0.1373, Recent IC=+0.1105, 1st-half IC=+0.1388, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.175, Q3_mid=+0.120, Q4=+0.105, Q5_high_vol=+0.136

**`combo_max__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0279, Sharpe=-1.5933)
- Admission: Train IC=+0.1317, Deflated=+0.1313, IR=0.45, Mono=0.67, p=0.0084, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.113 | 2016: +0.000 | 2017: +0.022 | 2018: +0.048 | 2019: +0.119 | 2020: +0.046 | 2021: +0.123 | 2022: +0.142 | 2023: +0.132 | 2024: +0.097 | 2025: +0.175 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.022 | 2016: -0.011 | 2017: -0.001 | 2018: +0.045 | 2019: +0.204 | 2020: -0.016 | 2021: +0.120 | 2022: +0.120 | 2023: +0.170 | 2024: +0.289 | 2025: +0.154 | 2026: -0.182
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=1.83, Recency ratio=1.63
- Early IC=+0.0837, Recent IC=+0.1361, 1st-half IC=+0.0799, 2nd-half IC=+0.1462, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.110, Q3_mid=+0.144, Q4=+0.089, Q5_high_vol=+0.100

**`combo_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.0270, Sharpe=-0.4994)
- Admission: Train IC=+0.2870, Deflated=+0.2871, IR=0.86, Mono=0.83, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.039 | 2017: +0.017 | 2018: +0.124 | 2019: +0.187 | 2020: +0.107 | 2021: +0.159 | 2022: +0.129 | 2023: +0.158 | 2024: +0.059 | 2025: +0.193 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.128 | 2016: -0.037 | 2017: +0.074 | 2018: +0.163 | 2019: +0.452 | 2020: +0.249 | 2021: +0.277 | 2022: +0.271 | 2023: +0.304 | 2024: +0.263 | 2025: +0.291 | 2026: -0.065
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.81
- Early IC=+0.1557, Recent IC=+0.1262, 1st-half IC=+0.1422, 2nd-half IC=+0.1382, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.154, Q3_mid=+0.151, Q4=+0.122, Q5_high_vol=+0.153

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0262, Sharpe=-1.0933)
- Admission: Train IC=+0.1827, Deflated=+0.1822, IR=0.55, Mono=0.67, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.060 | 2017: +0.036 | 2018: +0.076 | 2019: +0.136 | 2020: +0.071 | 2021: +0.178 | 2022: +0.142 | 2023: +0.149 | 2024: +0.079 | 2025: +0.132 | 2026: +0.026
- Yearly Tail ICs:   2015: -0.094 | 2016: +0.164 | 2017: +0.098 | 2018: +0.225 | 2019: +0.219 | 2020: +0.022 | 2021: +0.389 | 2022: +0.195 | 2023: +0.254 | 2024: +0.256 | 2025: +0.080 | 2026: -0.094
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.99
- Early IC=+0.1063, Recent IC=+0.1052, 1st-half IC=+0.1141, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.128, Q3_mid=+0.112, Q4=+0.134, Q5_high_vol=+0.127

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0212, Sharpe=-1.1311)
- Admission: Train IC=+0.1980, Deflated=+0.1967, IR=0.63, Mono=0.72, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.139 | 2017: -0.014 | 2018: +0.123 | 2019: +0.141 | 2020: +0.114 | 2021: +0.165 | 2022: +0.157 | 2023: +0.104 | 2024: +0.058 | 2025: +0.142 | 2026: +0.021
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.182 | 2017: +0.117 | 2018: +0.337 | 2019: +0.159 | 2020: +0.096 | 2021: +0.473 | 2022: +0.139 | 2023: +0.241 | 2024: +0.283 | 2025: +0.056 | 2026: -0.146
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.76
- Early IC=+0.1325, Recent IC=+0.1004, 1st-half IC=+0.1335, 2nd-half IC=+0.1225, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.102, Q3_mid=+0.149, Q4=+0.121, Q5_high_vol=+0.120

**`combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0199, Sharpe=-0.2374)
- Admission: Train IC=+0.2547, Deflated=+0.2553, IR=0.59, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.138 | 2017: +0.012 | 2018: +0.141 | 2019: +0.206 | 2020: +0.126 | 2021: +0.146 | 2022: +0.070 | 2023: +0.165 | 2024: +0.061 | 2025: +0.150 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.415 | 2016: -0.113 | 2017: +0.073 | 2018: +0.276 | 2019: +0.425 | 2020: +0.047 | 2021: +0.271 | 2022: +0.067 | 2023: +0.393 | 2024: +0.229 | 2025: +0.390 | 2026: +0.168
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.61
- Early IC=+0.1735, Recent IC=+0.1054, 1st-half IC=+0.1425, 2nd-half IC=+0.1117, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.150, Q3_mid=+0.124, Q4=+0.082, Q5_high_vol=+0.138

**`combo_rank_min__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=+0.0154, Sharpe=-0.1510)
- Admission: Train IC=+0.2066, Deflated=+0.2073, IR=0.53, Mono=0.74, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.071 | 2017: +0.020 | 2018: +0.061 | 2019: +0.163 | 2020: +0.054 | 2021: +0.114 | 2022: +0.073 | 2023: +0.177 | 2024: +0.075 | 2025: +0.150 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.015 | 2016: +0.184 | 2017: +0.120 | 2018: +0.086 | 2019: +0.253 | 2020: +0.119 | 2021: +0.071 | 2022: +0.235 | 2023: +0.411 | 2024: +0.190 | 2025: +0.132 | 2026: +0.044
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.58, Recency ratio=1.13
- Early IC=+0.1039, Recent IC=+0.1172, 1st-half IC=+0.0797, 2nd-half IC=+0.1257, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.127, Q3_mid=+0.105, Q4=+0.061, Q5_high_vol=+0.111

**`combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0120, Sharpe=-0.2721)
- Admission: Train IC=+0.1789, Deflated=+0.1799, IR=0.56, Mono=0.74, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.127 | 2017: +0.020 | 2018: +0.127 | 2019: +0.201 | 2020: +0.099 | 2021: +0.135 | 2022: +0.083 | 2023: +0.148 | 2024: +0.057 | 2025: +0.111 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.357 | 2016: -0.023 | 2017: +0.141 | 2018: +0.172 | 2019: +0.269 | 2020: -0.019 | 2021: +0.222 | 2022: +0.216 | 2023: +0.391 | 2024: +0.043 | 2025: +0.136 | 2026: +0.136
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.51
- Early IC=+0.1640, Recent IC=+0.0841, 1st-half IC=+0.1302, 2nd-half IC=+0.1006, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.139, Q3_mid=+0.116, Q4=+0.077, Q5_high_vol=+0.121

**`combo_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0069, Sharpe=-0.4785)
- Admission: Train IC=+0.2695, Deflated=+0.2701, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.121 | 2017: +0.012 | 2018: +0.132 | 2019: +0.183 | 2020: +0.129 | 2021: +0.129 | 2022: +0.091 | 2023: +0.152 | 2024: +0.057 | 2025: +0.131 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.449 | 2016: -0.281 | 2017: +0.151 | 2018: +0.295 | 2019: +0.360 | 2020: +0.153 | 2021: +0.226 | 2022: +0.116 | 2023: +0.293 | 2024: +0.124 | 2025: +0.285 | 2026: +0.049
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.60
- Early IC=+0.1578, Recent IC=+0.0940, 1st-half IC=+0.1356, 2nd-half IC=+0.1106, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.147, Q3_mid=+0.120, Q4=+0.117, Q5_high_vol=+0.124

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0018, Sharpe=-2.0212)
- Admission: Train IC=+0.2583, Deflated=+0.2583, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.039 | 2017: +0.020 | 2018: +0.089 | 2019: +0.185 | 2020: +0.086 | 2021: +0.158 | 2022: +0.144 | 2023: +0.154 | 2024: +0.077 | 2025: +0.190 | 2026: +0.002
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.257 | 2017: -0.015 | 2018: +0.093 | 2019: +0.393 | 2020: +0.199 | 2021: +0.338 | 2022: +0.381 | 2023: +0.363 | 2024: +0.260 | 2025: +0.236 | 2026: -0.235
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.97
- Early IC=+0.1373, Recent IC=+0.1333, 1st-half IC=+0.1317, 2nd-half IC=+0.1464, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.159, Q3_mid=+0.141, Q4=+0.148, Q5_high_vol=+0.147

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0132, Sharpe=+0.8820)
- Admission: Train IC=+0.1968, Deflated=+0.1971, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.060 | 2017: -0.078 | 2018: +0.158 | 2019: +0.108 | 2020: +0.050 | 2021: +0.142 | 2022: +0.041 | 2023: +0.108 | 2024: +0.035 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.083 | 2017: -0.170 | 2018: +0.357 | 2019: +0.430 | 2020: +0.129 | 2021: +0.309 | 2022: +0.261 | 2023: +0.033 | 2024: +0.334 | 2025: -0.024 | 2026: +0.265
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.37
- Early IC=+0.1323, Recent IC=+0.0495, 1st-half IC=+0.1136, 2nd-half IC=+0.0765, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.90)
- Regime ICs: Q1_low_vol=-0.004, Q2=+0.078, Q3_mid=+0.075, Q4=+0.083, Q5_high_vol=+0.205

**`combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0272, Sharpe=+0.6075)
- Admission: Train IC=+0.2637, Deflated=+0.2645, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.073 | 2017: -0.029 | 2018: +0.185 | 2019: +0.143 | 2020: +0.035 | 2021: +0.133 | 2022: +0.044 | 2023: +0.155 | 2024: +0.045 | 2025: +0.097 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.112 | 2017: -0.040 | 2018: +0.347 | 2019: +0.172 | 2020: +0.139 | 2021: +0.406 | 2022: +0.237 | 2023: +0.269 | 2024: +0.254 | 2025: +0.078 | 2026: +0.239
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.45
- Early IC=+0.1622, Recent IC=+0.0722, 1st-half IC=+0.1242, 2nd-half IC=+0.0915, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.100, Q3_mid=+0.073, Q4=+0.090, Q5_high_vol=+0.210

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0147, Sharpe=+0.3204)
- Admission: Train IC=+0.2113, Deflated=+0.2119, IR=0.52, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.062 | 2017: -0.039 | 2018: +0.163 | 2019: +0.138 | 2020: +0.017 | 2021: +0.123 | 2022: +0.028 | 2023: +0.138 | 2024: +0.031 | 2025: +0.100 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.143 | 2016: +0.064 | 2017: -0.124 | 2018: +0.315 | 2019: +0.203 | 2020: +0.180 | 2021: +0.259 | 2022: +0.147 | 2023: +0.230 | 2024: +0.242 | 2025: +0.104 | 2026: +0.275
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.44
- Early IC=+0.1506, Recent IC=+0.0656, 1st-half IC=+0.1110, 2nd-half IC=+0.0842, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.106, Q3_mid=+0.048, Q4=+0.087, Q5_high_vol=+0.186

### 500ETF — `single` True Positives

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1800, Sharpe=+2.6093)
- Admission: Train IC=+0.2085, Deflated=+0.2090, IR=0.49, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.079 | 2017: +0.127 | 2018: +0.205 | 2019: +0.178 | 2020: +0.185 | 2021: +0.124 | 2022: +0.050 | 2023: +0.063 | 2024: +0.112 | 2025: +0.060 | 2026: +0.180
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.035 | 2017: +0.195 | 2018: +0.360 | 2019: +0.447 | 2020: +0.227 | 2021: +0.196 | 2022: -0.076 | 2023: +0.058 | 2024: +0.115 | 2025: +0.054 | 2026: +0.353
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.45, Recency ratio=0.45
- Early IC=+0.1919, Recent IC=+0.0861, 1st-half IC=+0.1729, 2nd-half IC=+0.0781, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.023, Q3_mid=+0.110, Q4=+0.133, Q5_high_vol=+0.207

**`combo_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1499, Sharpe=+2.5696)
- Admission: Train IC=+0.1083, Deflated=+0.1076, IR=0.36, Mono=0.66, p=0.0290, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.051 | 2017: +0.222 | 2018: +0.091 | 2019: +0.112 | 2020: +0.150 | 2021: +0.021 | 2022: +0.081 | 2023: +0.020 | 2024: +0.140 | 2025: +0.078 | 2026: +0.150
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.185 | 2017: +0.156 | 2018: +0.059 | 2019: +0.301 | 2020: +0.199 | 2021: +0.128 | 2022: +0.040 | 2023: -0.058 | 2024: +0.135 | 2025: -0.005 | 2026: +0.310
- IC CV=0.52, Neg years (linear/tail)=0/2 of 8, Half ratio=0.96, Recency ratio=1.08
- Early IC=+0.1014, Recent IC=+0.1093, 1st-half IC=+0.0948, 2nd-half IC=+0.0912, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.070, Q3_mid=+0.122, Q4=+0.101, Q5_high_vol=+0.110

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.0811, Sharpe=+2.5041)
- Admission: Train IC=+0.2157, Deflated=+0.2148, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.075 | 2017: +0.225 | 2018: +0.159 | 2019: +0.120 | 2020: +0.127 | 2021: +0.124 | 2022: +0.018 | 2023: +0.101 | 2024: +0.154 | 2025: +0.112 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.321 | 2016: +0.218 | 2017: +0.285 | 2018: +0.411 | 2019: +0.249 | 2020: +0.200 | 2021: +0.155 | 2022: +0.247 | 2023: +0.014 | 2024: +0.274 | 2025: +0.055 | 2026: +0.395
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.95
- Early IC=+0.1395, Recent IC=+0.1331, 1st-half IC=+0.1313, 2nd-half IC=+0.1029, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.050, Q3_mid=+0.142, Q4=+0.115, Q5_high_vol=+0.174

**`combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1783, Sharpe=+2.2572)
- Admission: Train IC=+0.2390, Deflated=+0.2395, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.080 | 2017: +0.128 | 2018: +0.205 | 2019: +0.176 | 2020: +0.187 | 2021: +0.125 | 2022: +0.049 | 2023: +0.062 | 2024: +0.116 | 2025: +0.062 | 2026: +0.178
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.066 | 2017: +0.224 | 2018: +0.345 | 2019: +0.418 | 2020: +0.296 | 2021: +0.223 | 2022: -0.085 | 2023: +0.040 | 2024: +0.222 | 2025: +0.118 | 2026: +0.380
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.46, Recency ratio=0.47
- Early IC=+0.1908, Recent IC=+0.0890, 1st-half IC=+0.1732, 2nd-half IC=+0.0795, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.021, Q3_mid=+0.113, Q4=+0.136, Q5_high_vol=+0.208

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1749, Sharpe=+2.0624)
- Admission: Train IC=+0.2417, Deflated=+0.2420, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.028 | 2017: +0.137 | 2018: +0.186 | 2019: +0.195 | 2020: +0.192 | 2021: +0.143 | 2022: +0.062 | 2023: +0.073 | 2024: +0.124 | 2025: +0.089 | 2026: +0.175
- Yearly Tail ICs:   2015: +0.234 | 2016: +0.071 | 2017: +0.189 | 2018: +0.330 | 2019: +0.485 | 2020: +0.235 | 2021: +0.268 | 2022: -0.025 | 2023: +0.129 | 2024: +0.155 | 2025: +0.117 | 2026: +0.384
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.53, Recency ratio=0.56
- Early IC=+0.1907, Recent IC=+0.1062, 1st-half IC=+0.1767, 2nd-half IC=+0.0942, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.035, Q3_mid=+0.115, Q4=+0.137, Q5_high_vol=+0.223

**`combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence`** (Lock IC=+0.1145, Sharpe=+1.8262)
- Admission: Train IC=+0.1535, Deflated=+0.1548, IR=0.44, Mono=0.66, p=0.0018, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.033 | 2017: +0.188 | 2018: +0.172 | 2019: +0.153 | 2020: +0.141 | 2021: +0.128 | 2022: +0.038 | 2023: +0.093 | 2024: +0.098 | 2025: +0.046 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.422 | 2016: +0.053 | 2017: +0.365 | 2018: +0.152 | 2019: +0.295 | 2020: +0.088 | 2021: +0.219 | 2022: +0.025 | 2023: +0.147 | 2024: +0.195 | 2025: +0.045 | 2026: +0.311
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.44
- Early IC=+0.1626, Recent IC=+0.0719, 1st-half IC=+0.1423, 2nd-half IC=+0.0741, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.012, Q3_mid=+0.106, Q4=+0.127, Q5_high_vol=+0.179

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1045, Sharpe=+1.6851)
- Admission: Train IC=+0.2174, Deflated=+0.2172, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.101 | 2017: +0.231 | 2018: +0.185 | 2019: +0.157 | 2020: +0.172 | 2021: +0.142 | 2022: +0.033 | 2023: +0.098 | 2024: +0.145 | 2025: +0.105 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.251 | 2017: +0.357 | 2018: +0.456 | 2019: +0.298 | 2020: +0.315 | 2021: +0.302 | 2022: +0.078 | 2023: -0.003 | 2024: +0.236 | 2025: +0.074 | 2026: +0.233
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.74
- Early IC=+0.1705, Recent IC=+0.1264, 1st-half IC=+0.1656, 2nd-half IC=+0.1040, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.027, Q3_mid=+0.142, Q4=+0.123, Q5_high_vol=+0.237

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0403, Sharpe=+1.5479)
- Admission: Train IC=+0.1758, Deflated=+0.1761, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.126 | 2017: +0.126 | 2018: +0.203 | 2019: +0.080 | 2020: +0.101 | 2021: +0.145 | 2022: +0.081 | 2023: +0.005 | 2024: +0.135 | 2025: +0.128 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.242 | 2017: +0.234 | 2018: +0.435 | 2019: +0.009 | 2020: +0.098 | 2021: +0.322 | 2022: +0.026 | 2023: +0.079 | 2024: +0.193 | 2025: +0.270 | 2026: +0.268
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.93
- Early IC=+0.1416, Recent IC=+0.1313, 1st-half IC=+0.1322, 2nd-half IC=+0.0981, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.004, Q3_mid=+0.076, Q4=+0.114, Q5_high_vol=+0.220

**`combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0765, Sharpe=+1.5322)
- Admission: Train IC=+0.2011, Deflated=+0.1999, IR=0.50, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.061 | 2017: +0.199 | 2018: +0.089 | 2019: +0.066 | 2020: +0.087 | 2021: +0.059 | 2022: +0.054 | 2023: +0.092 | 2024: +0.128 | 2025: +0.113 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.289 | 2016: +0.153 | 2017: +0.329 | 2018: +0.306 | 2019: +0.115 | 2020: +0.248 | 2021: +0.024 | 2022: +0.244 | 2023: +0.114 | 2024: +0.334 | 2025: +0.034 | 2026: +0.321
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.31, Recency ratio=1.55
- Early IC=+0.0774, Recent IC=+0.1204, 1st-half IC=+0.0779, 2nd-half IC=+0.1024, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.056, Q3_mid=+0.112, Q4=+0.094, Q5_high_vol=+0.122

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0947, Sharpe=+1.1715)
- Admission: Train IC=+0.1880, Deflated=+0.1866, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.126 | 2017: +0.180 | 2018: +0.099 | 2019: +0.051 | 2020: +0.098 | 2021: -0.004 | 2022: +0.095 | 2023: +0.049 | 2024: +0.074 | 2025: +0.119 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.106 | 2017: +0.342 | 2018: +0.258 | 2019: +0.109 | 2020: +0.195 | 2021: +0.128 | 2022: +0.198 | 2023: +0.046 | 2024: +0.246 | 2025: +0.105 | 2026: +0.208
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=1.31, Recency ratio=1.28
- Early IC=+0.0751, Recent IC=+0.0963, 1st-half IC=+0.0672, 2nd-half IC=+0.0877, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.060, Q3_mid=+0.101, Q4=+0.061, Q5_high_vol=+0.104

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0823, Sharpe=+1.1643)
- Admission: Train IC=+0.1667, Deflated=+0.1668, IR=0.67, Mono=0.72, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.113 | 2019: +0.122 | 2020: +0.121 | 2021: +0.073 | 2022: +0.056 | 2023: +0.064 | 2024: +0.085 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.111 | 2017: +0.267 | 2018: +0.360 | 2019: +0.324 | 2020: +0.217 | 2021: +0.340 | 2022: +0.063 | 2023: +0.041 | 2024: +0.147 | 2025: +0.082 | 2026: +0.223
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.94
- Early IC=+0.1165, Recent IC=+0.1101, 1st-half IC=+0.1001, 2nd-half IC=+0.0922, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.018, Q3_mid=+0.137, Q4=+0.113, Q5_high_vol=+0.123

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0865, Sharpe=+1.1116)
- Admission: Train IC=+0.1908, Deflated=+0.1895, IR=0.53, Mono=0.66, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.073 | 2017: +0.226 | 2018: +0.079 | 2019: +0.082 | 2020: +0.119 | 2021: +0.089 | 2022: +0.032 | 2023: +0.095 | 2024: +0.142 | 2025: +0.138 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.208 | 2017: +0.338 | 2018: +0.282 | 2019: +0.119 | 2020: +0.215 | 2021: +0.215 | 2022: +0.160 | 2023: +0.008 | 2024: +0.221 | 2025: +0.089 | 2026: +0.313
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=1.72
- Early IC=+0.0822, Recent IC=+0.1411, 1st-half IC=+0.0926, 2nd-half IC=+0.1080, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.051, Q3_mid=+0.114, Q4=+0.103, Q5_high_vol=+0.126

**`combo_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0708, Sharpe=+1.0762)
- Admission: Train IC=+0.1885, Deflated=+0.1872, IR=0.49, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.070 | 2017: +0.212 | 2018: +0.089 | 2019: +0.078 | 2020: +0.106 | 2021: +0.082 | 2022: +0.043 | 2023: +0.101 | 2024: +0.149 | 2025: +0.133 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.285 | 2016: +0.177 | 2017: +0.278 | 2018: +0.299 | 2019: +0.046 | 2020: +0.231 | 2021: +0.063 | 2022: +0.197 | 2023: +0.010 | 2024: +0.341 | 2025: +0.114 | 2026: +0.242
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.69
- Early IC=+0.0835, Recent IC=+0.1410, 1st-half IC=+0.0904, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.065, Q3_mid=+0.119, Q4=+0.098, Q5_high_vol=+0.122

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0674, Sharpe=+1.0606)
- Admission: Train IC=+0.2228, Deflated=+0.2222, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.116 | 2017: +0.229 | 2018: +0.213 | 2019: +0.142 | 2020: +0.186 | 2021: +0.125 | 2022: +0.094 | 2023: +0.080 | 2024: +0.131 | 2025: +0.106 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.221 | 2017: +0.273 | 2018: +0.397 | 2019: +0.325 | 2020: +0.129 | 2021: +0.233 | 2022: +0.331 | 2023: +0.159 | 2024: +0.226 | 2025: +0.008 | 2026: +0.077
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.67
- Early IC=+0.1774, Recent IC=+0.1184, 1st-half IC=+0.1666, 2nd-half IC=+0.1119, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.064, Q3_mid=+0.149, Q4=+0.135, Q5_high_vol=+0.211

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1466, Sharpe=+0.8696)
- Admission: Train IC=+0.1923, Deflated=+0.1918, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.031 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.030 | 2024: +0.178 | 2025: +0.302 | 2026: +0.147
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=1.15
- Early IC=+0.1071, Recent IC=+0.1235, 1st-half IC=+0.0993, 2nd-half IC=+0.1048, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.068, Q3_mid=+0.125, Q4=+0.115, Q5_high_vol=+0.128

**`combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0527, Sharpe=+0.7989)
- Admission: Train IC=+0.1637, Deflated=+0.1645, IR=0.45, Mono=0.68, p=0.0006, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.055 | 2017: +0.163 | 2018: +0.182 | 2019: +0.149 | 2020: +0.193 | 2021: +0.147 | 2022: +0.007 | 2023: +0.106 | 2024: +0.095 | 2025: +0.069 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.227 | 2016: +0.233 | 2017: +0.126 | 2018: +0.436 | 2019: +0.149 | 2020: +0.106 | 2021: +0.404 | 2022: +0.157 | 2023: -0.125 | 2024: +0.007 | 2025: +0.074 | 2026: +0.163
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.46, Recency ratio=0.50
- Early IC=+0.1654, Recent IC=+0.0819, 1st-half IC=+0.1656, 2nd-half IC=+0.0766, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.017, Q3_mid=+0.107, Q4=+0.092, Q5_high_vol=+0.232

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1067, Sharpe=+0.5671)
- Admission: Train IC=+0.2160, Deflated=+0.2157, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.127 | 2017: +0.217 | 2018: +0.213 | 2019: +0.132 | 2020: +0.171 | 2021: +0.103 | 2022: +0.083 | 2023: +0.071 | 2024: +0.095 | 2025: +0.117 | 2026: +0.107
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.145 | 2017: +0.266 | 2018: +0.403 | 2019: +0.276 | 2020: +0.221 | 2021: +0.173 | 2022: +0.172 | 2023: -0.031 | 2024: +0.136 | 2025: +0.138 | 2026: +0.143
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.61
- Early IC=+0.1729, Recent IC=+0.1059, 1st-half IC=+0.1559, 2nd-half IC=+0.0953, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.025, Q3_mid=+0.103, Q4=+0.141, Q5_high_vol=+0.192

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0759, Sharpe=+0.4853)
- Admission: Train IC=+0.1660, Deflated=+0.1662, IR=0.57, Mono=0.69, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.042 | 2017: +0.233 | 2018: +0.106 | 2019: +0.113 | 2020: +0.100 | 2021: +0.061 | 2022: +0.081 | 2023: +0.080 | 2024: +0.081 | 2025: +0.141 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.329 | 2016: +0.080 | 2017: +0.274 | 2018: +0.290 | 2019: +0.302 | 2020: +0.185 | 2021: +0.134 | 2022: +0.134 | 2023: +0.051 | 2024: +0.144 | 2025: +0.047 | 2026: +0.113
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=1.01
- Early IC=+0.1095, Recent IC=+0.1111, 1st-half IC=+0.0918, 2nd-half IC=+0.1015, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.025, Q3_mid=+0.134, Q4=+0.112, Q5_high_vol=+0.119

**`combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1323, Sharpe=+0.4708)
- Admission: Train IC=+0.1266, Deflated=+0.1261, IR=0.43, Mono=0.70, p=0.0104, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.135 | 2017: +0.226 | 2018: +0.160 | 2019: +0.120 | 2020: +0.189 | 2021: +0.091 | 2022: +0.120 | 2023: +0.073 | 2024: +0.116 | 2025: +0.080 | 2026: +0.132
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.389 | 2017: +0.114 | 2018: +0.137 | 2019: +0.260 | 2020: +0.134 | 2021: +0.159 | 2022: +0.053 | 2023: -0.137 | 2024: +0.148 | 2025: +0.055 | 2026: +0.143
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.70
- Early IC=+0.1398, Recent IC=+0.0980, 1st-half IC=+0.1400, 2nd-half IC=+0.1094, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.078, Q3_mid=+0.132, Q4=+0.129, Q5_high_vol=+0.183

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0755, Sharpe=+0.4554)
- Admission: Train IC=+0.2277, Deflated=+0.2280, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.58
- Early IC=+0.1857, Recent IC=+0.1081, 1st-half IC=+0.1517, 2nd-half IC=+0.0849, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.007, Q3_mid=+0.085, Q4=+0.146, Q5_high_vol=+0.198

**`combo_min__close_vs_open_range__first_bar_return`** (Lock IC=+0.0019, Sharpe=+0.4072)
- Admission: Train IC=+0.2002, Deflated=+0.1992, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.085 | 2017: +0.189 | 2018: +0.163 | 2019: +0.112 | 2020: +0.068 | 2021: +0.057 | 2022: +0.055 | 2023: +0.080 | 2024: +0.142 | 2025: +0.144 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.185 | 2017: +0.309 | 2018: +0.315 | 2019: +0.117 | 2020: +0.073 | 2021: +0.227 | 2022: +0.220 | 2023: +0.141 | 2024: +0.217 | 2025: +0.223 | 2026: +0.202
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.04
- Early IC=+0.1376, Recent IC=+0.1428, 1st-half IC=+0.0997, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.031, Q3_mid=+0.105, Q4=+0.109, Q5_high_vol=+0.145

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0571, Sharpe=+0.3372)
- Admission: Train IC=+0.2573, Deflated=+0.2569, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.089 | 2017: +0.215 | 2018: +0.189 | 2019: +0.136 | 2020: +0.152 | 2021: +0.150 | 2022: +0.044 | 2023: +0.100 | 2024: +0.142 | 2025: +0.113 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.220 | 2017: +0.350 | 2018: +0.463 | 2019: +0.292 | 2020: +0.246 | 2021: +0.237 | 2022: +0.207 | 2023: +0.180 | 2024: +0.355 | 2025: +0.033 | 2026: +0.277
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.79
- Early IC=+0.1623, Recent IC=+0.1276, 1st-half IC=+0.1579, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.042, Q3_mid=+0.150, Q4=+0.129, Q5_high_vol=+0.210

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0820, Sharpe=+0.3115)
- Admission: Train IC=+0.2351, Deflated=+0.2355, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.317 | 2016: +0.085 | 2017: +0.219 | 2018: +0.201 | 2019: +0.174 | 2020: +0.137 | 2021: +0.085 | 2022: +0.052 | 2023: +0.081 | 2024: +0.088 | 2025: +0.122 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.112 | 2017: +0.149 | 2018: +0.458 | 2019: +0.312 | 2020: +0.269 | 2021: +0.035 | 2022: +0.134 | 2023: +0.143 | 2024: +0.266 | 2025: +0.110 | 2026: +0.094
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.56
- Early IC=+0.1878, Recent IC=+0.1052, 1st-half IC=+0.1493, 2nd-half IC=+0.0847, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.008, Q3_mid=+0.080, Q4=+0.144, Q5_high_vol=+0.189

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0216, Sharpe=+0.1562)
- Admission: Train IC=+0.1947, Deflated=+0.1927, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.121 | 2017: +0.090 | 2018: +0.133 | 2019: +0.055 | 2020: +0.134 | 2021: +0.036 | 2022: +0.094 | 2023: +0.029 | 2024: +0.092 | 2025: +0.121 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.189 | 2016: +0.282 | 2017: +0.203 | 2018: +0.260 | 2019: +0.267 | 2020: +0.222 | 2021: +0.071 | 2022: +0.123 | 2023: -0.026 | 2024: +0.185 | 2025: +0.081 | 2026: +0.017
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.96, Recency ratio=1.13
- Early IC=+0.0939, Recent IC=+0.1065, 1st-half IC=+0.0980, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.079, Q3_mid=+0.121, Q4=+0.078, Q5_high_vol=+0.148

**`combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0670, Sharpe=+0.1096)
- Admission: Train IC=+0.1845, Deflated=+0.1832, IR=0.56, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.088 | 2017: +0.221 | 2018: +0.112 | 2019: +0.064 | 2020: +0.115 | 2021: +0.084 | 2022: +0.049 | 2023: +0.080 | 2024: +0.103 | 2025: +0.135 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.301 | 2017: +0.429 | 2018: +0.349 | 2019: +0.070 | 2020: +0.211 | 2021: +0.189 | 2022: +0.161 | 2023: -0.060 | 2024: +0.335 | 2025: +0.117 | 2026: +0.170
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=1.38
- Early IC=+0.0899, Recent IC=+0.1240, 1st-half IC=+0.0996, 2nd-half IC=+0.1011, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.056, Q3_mid=+0.104, Q4=+0.103, Q5_high_vol=+0.142

**`bar_body_rng_0`** (Lock IC=+0.0133, Sharpe=+0.1053)
- Admission: Train IC=+0.1260, Deflated=+0.1257, IR=0.43, Mono=0.67, p=0.0116, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.104 | 2017: +0.169 | 2018: +0.192 | 2019: +0.131 | 2020: +0.092 | 2021: +0.119 | 2022: +0.057 | 2023: +0.068 | 2024: +0.105 | 2025: +0.099 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.365 | 2016: -0.105 | 2017: +0.215 | 2018: +0.088 | 2019: +0.267 | 2020: +0.135 | 2021: +0.187 | 2022: +0.004 | 2023: +0.093 | 2024: +0.067 | 2025: +0.148 | 2026: -0.034
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.63
- Early IC=+0.1611, Recent IC=+0.1022, 1st-half IC=+0.1318, 2nd-half IC=+0.0876, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.124, Q2=-0.004, Q3_mid=+0.112, Q4=+0.140, Q5_high_vol=+0.145

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0069, Sharpe=+0.0524)
- Admission: Train IC=+0.1983, Deflated=+0.1983, IR=0.72, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.234 | 2018: +0.163 | 2019: +0.358 | 2020: +0.068 | 2021: +0.297 | 2022: +0.084 | 2023: +0.183 | 2024: +0.402 | 2025: +0.178 | 2026: -0.048
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.78
- Early IC=+0.1685, Recent IC=+0.1315, 1st-half IC=+0.1454, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.043, Q3_mid=+0.175, Q4=+0.123, Q5_high_vol=+0.195

### 159915ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1174, Sharpe=+2.8044)
- Admission: Train IC=+0.3231, Deflated=+0.3239, IR=1.01, Mono=0.83, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.124 | 2017: -0.001 | 2018: +0.125 | 2019: +0.213 | 2020: +0.067 | 2021: +0.189 | 2022: +0.060 | 2023: +0.148 | 2024: +0.120 | 2025: +0.140 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.063 | 2017: +0.103 | 2018: +0.280 | 2019: +0.527 | 2020: +0.305 | 2021: +0.389 | 2022: +0.110 | 2023: +0.381 | 2024: +0.281 | 2025: +0.148 | 2026: +0.325
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.78
- Early IC=+0.1683, Recent IC=+0.1321, 1st-half IC=+0.1477, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.158, Q3_mid=+0.135, Q4=+0.154, Q5_high_vol=+0.153

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1324, Sharpe=+2.7212)
- Admission: Train IC=+0.3107, Deflated=+0.3113, IR=1.02, Mono=0.82, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.072 | 2017: -0.009 | 2018: +0.097 | 2019: +0.229 | 2020: +0.041 | 2021: +0.151 | 2022: +0.035 | 2023: +0.151 | 2024: +0.139 | 2025: +0.135 | 2026: +0.132
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.061 | 2017: +0.119 | 2018: +0.278 | 2019: +0.576 | 2020: +0.299 | 2021: +0.326 | 2022: +0.252 | 2023: +0.365 | 2024: +0.313 | 2025: +0.125 | 2026: +0.366
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.84
- Early IC=+0.1626, Recent IC=+0.1368, 1st-half IC=+0.1276, 2nd-half IC=+0.1222, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.146, Q3_mid=+0.141, Q4=+0.129, Q5_high_vol=+0.133

**`combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1381, Sharpe=+2.7110)
- Admission: Train IC=+0.2634, Deflated=+0.2638, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.016 | 2017: -0.006 | 2018: +0.068 | 2019: +0.223 | 2020: +0.017 | 2021: +0.124 | 2022: +0.019 | 2023: +0.147 | 2024: +0.110 | 2025: +0.131 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.232 | 2016: -0.077 | 2017: +0.116 | 2018: +0.247 | 2019: +0.595 | 2020: +0.129 | 2021: +0.347 | 2022: +0.200 | 2023: +0.316 | 2024: +0.237 | 2025: +0.141 | 2026: +0.375
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.85
- Early IC=+0.1417, Recent IC=+0.1203, 1st-half IC=+0.1000, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.129, Q3_mid=+0.147, Q4=+0.100, Q5_high_vol=+0.098

**`combo_max__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1476, Sharpe=+2.6573)
- Admission: Train IC=+0.1602, Deflated=+0.1592, IR=0.42, Mono=0.65, p=0.0028, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.110 | 2017: -0.017 | 2018: +0.098 | 2019: +0.180 | 2020: +0.131 | 2021: +0.143 | 2022: +0.104 | 2023: +0.058 | 2024: +0.084 | 2025: +0.051 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.090 | 2016: +0.132 | 2017: +0.035 | 2018: +0.171 | 2019: +0.252 | 2020: +0.155 | 2021: +0.219 | 2022: +0.201 | 2023: +0.019 | 2024: +0.168 | 2025: +0.010 | 2026: +0.422
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.49
- Early IC=+0.1389, Recent IC=+0.0676, 1st-half IC=+0.1389, 2nd-half IC=+0.0812, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.076, Q3_mid=+0.159, Q4=+0.087, Q5_high_vol=+0.093

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.0766, Sharpe=+2.5089)
- Admission: Train IC=+0.3325, Deflated=+0.3324, IR=1.12, Mono=0.87, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.047 | 2017: +0.001 | 2018: +0.122 | 2019: +0.239 | 2020: +0.125 | 2021: +0.140 | 2022: +0.096 | 2023: +0.178 | 2024: +0.124 | 2025: +0.179 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.108 | 2017: +0.096 | 2018: +0.365 | 2019: +0.524 | 2020: +0.301 | 2021: +0.326 | 2022: +0.342 | 2023: +0.317 | 2024: +0.333 | 2025: +0.131 | 2026: +0.382
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.84
- Early IC=+0.1802, Recent IC=+0.1519, 1st-half IC=+0.1509, 2nd-half IC=+0.1481, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.163, Q3_mid=+0.134, Q4=+0.173, Q5_high_vol=+0.169

**`combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.1716, Sharpe=+2.0307)
- Admission: Train IC=+0.1815, Deflated=+0.1809, IR=0.47, Mono=0.68, p=0.0004, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.046 | 2017: -0.014 | 2018: +0.102 | 2019: +0.172 | 2020: +0.107 | 2021: +0.146 | 2022: +0.166 | 2023: +0.109 | 2024: +0.100 | 2025: +0.123 | 2026: +0.173
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.207 | 2017: +0.032 | 2018: +0.220 | 2019: +0.240 | 2020: +0.156 | 2021: +0.246 | 2022: +0.184 | 2023: -0.050 | 2024: +0.213 | 2025: +0.015 | 2026: +0.332
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.94, Recency ratio=0.80
- Early IC=+0.1372, Recent IC=+0.1093, 1st-half IC=+0.1392, 2nd-half IC=+0.1303, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.119, Q3_mid=+0.115, Q4=+0.164, Q5_high_vol=+0.147

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1495, Sharpe=+1.8753)
- Admission: Train IC=+0.3014, Deflated=+0.3022, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.056 | 2017: -0.039 | 2018: +0.098 | 2019: +0.257 | 2020: +0.142 | 2021: +0.107 | 2022: +0.043 | 2023: +0.124 | 2024: +0.106 | 2025: +0.151 | 2026: +0.150
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.002 | 2017: +0.015 | 2018: +0.338 | 2019: +0.526 | 2020: +0.302 | 2021: +0.233 | 2022: +0.167 | 2023: +0.243 | 2024: +0.452 | 2025: +0.151 | 2026: +0.443
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.72
- Early IC=+0.1776, Recent IC=+0.1286, 1st-half IC=+0.1410, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.137, Q3_mid=+0.145, Q4=+0.104, Q5_high_vol=+0.137

**`combo_mean__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1356, Sharpe=+1.7557)
- Admission: Train IC=+0.2364, Deflated=+0.2362, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.089 | 2017: -0.021 | 2018: +0.133 | 2019: +0.234 | 2020: +0.173 | 2021: +0.122 | 2022: +0.100 | 2023: +0.075 | 2024: +0.083 | 2025: +0.108 | 2026: +0.136
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.177 | 2017: +0.160 | 2018: +0.276 | 2019: +0.351 | 2020: +0.187 | 2021: +0.144 | 2022: +0.249 | 2023: +0.056 | 2024: +0.266 | 2025: +0.160 | 2026: +0.347
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.52
- Early IC=+0.1836, Recent IC=+0.0958, 1st-half IC=+0.1669, 2nd-half IC=+0.0988, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.111, Q3_mid=+0.164, Q4=+0.113, Q5_high_vol=+0.142

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.0866, Sharpe=+1.5177)
- Admission: Train IC=+0.3339, Deflated=+0.3340, IR=1.12, Mono=0.85, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.034 | 2017: -0.003 | 2018: +0.108 | 2019: +0.231 | 2020: +0.131 | 2021: +0.132 | 2022: +0.109 | 2023: +0.186 | 2024: +0.087 | 2025: +0.186 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.016 | 2017: +0.073 | 2018: +0.342 | 2019: +0.495 | 2020: +0.320 | 2021: +0.285 | 2022: +0.298 | 2023: +0.468 | 2024: +0.314 | 2025: +0.117 | 2026: +0.279
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.81
- Early IC=+0.1705, Recent IC=+0.1381, 1st-half IC=+0.1446, 2nd-half IC=+0.1457, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.160, Q3_mid=+0.130, Q4=+0.165, Q5_high_vol=+0.168

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0980, Sharpe=+1.3754)
- Admission: Train IC=+0.1643, Deflated=+0.1655, IR=0.40, Mono=0.65, p=0.0016, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.121 | 2016: -0.001 | 2017: -0.037 | 2018: +0.022 | 2019: +0.177 | 2020: +0.075 | 2021: +0.090 | 2022: +0.101 | 2023: +0.138 | 2024: +0.156 | 2025: +0.067 | 2026: +0.098
- Yearly Tail ICs:   2015: -0.080 | 2016: -0.128 | 2017: -0.014 | 2018: +0.032 | 2019: +0.411 | 2020: +0.047 | 2021: +0.189 | 2022: +0.144 | 2023: +0.238 | 2024: +0.324 | 2025: +0.004 | 2026: +0.358
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.12
- Early IC=+0.0991, Recent IC=+0.1112, 1st-half IC=+0.0961, 2nd-half IC=+0.1164, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.068, Q3_mid=+0.097, Q4=+0.132, Q5_high_vol=+0.112

**`combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1654, Sharpe=+1.0917)
- Admission: Train IC=+0.2556, Deflated=+0.2552, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.110 | 2017: -0.072 | 2018: +0.110 | 2019: +0.110 | 2020: +0.090 | 2021: +0.046 | 2022: +0.171 | 2023: +0.132 | 2024: +0.102 | 2025: +0.108 | 2026: +0.165
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.157 | 2017: +0.160 | 2018: +0.362 | 2019: +0.320 | 2020: +0.352 | 2021: +0.218 | 2022: +0.396 | 2023: +0.073 | 2024: +0.119 | 2025: +0.186 | 2026: +0.312
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=0.96
- Early IC=+0.1098, Recent IC=+0.1049, 1st-half IC=+0.0954, 2nd-half IC=+0.1322, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.128, Q3_mid=+0.117, Q4=+0.150, Q5_high_vol=+0.095

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.0961, Sharpe=+1.0753)
- Admission: Train IC=+0.2412, Deflated=+0.2410, IR=0.83, Mono=0.78, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.116 | 2017: +0.054 | 2018: +0.141 | 2019: +0.217 | 2020: +0.102 | 2021: +0.208 | 2022: +0.070 | 2023: +0.122 | 2024: +0.106 | 2025: +0.163 | 2026: +0.096
- Yearly Tail ICs:   2015: -0.136 | 2016: +0.112 | 2017: +0.199 | 2018: +0.202 | 2019: +0.573 | 2020: +0.092 | 2021: +0.382 | 2022: +0.127 | 2023: +0.270 | 2024: +0.321 | 2025: +0.137 | 2026: +0.111
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.75
- Early IC=+0.1790, Recent IC=+0.1345, 1st-half IC=+0.1719, 2nd-half IC=+0.1192, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.134, Q3_mid=+0.151, Q4=+0.159, Q5_high_vol=+0.176

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1425, Sharpe=+1.0019)
- Admission: Train IC=+0.2872, Deflated=+0.2881, IR=0.90, Mono=0.84, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.040 | 2017: -0.056 | 2018: +0.095 | 2019: +0.245 | 2020: +0.122 | 2021: +0.099 | 2022: +0.056 | 2023: +0.135 | 2024: +0.095 | 2025: +0.167 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.021 | 2017: -0.034 | 2018: +0.385 | 2019: +0.534 | 2020: +0.249 | 2021: +0.283 | 2022: +0.154 | 2023: +0.234 | 2024: +0.339 | 2025: +0.287 | 2026: +0.349
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.78
- Early IC=+0.1696, Recent IC=+0.1317, 1st-half IC=+0.1245, 2nd-half IC=+0.1228, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.143, Q3_mid=+0.136, Q4=+0.098, Q5_high_vol=+0.130

**`combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0944, Sharpe=+0.9523)
- Admission: Train IC=+0.2335, Deflated=+0.2340, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.005 | 2017: +0.012 | 2018: +0.022 | 2019: +0.160 | 2020: +0.070 | 2021: +0.115 | 2022: +0.084 | 2023: +0.140 | 2024: +0.058 | 2025: +0.171 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.129 | 2017: +0.187 | 2018: +0.251 | 2019: +0.282 | 2020: +0.169 | 2021: +0.215 | 2022: +0.195 | 2023: +0.333 | 2024: +0.310 | 2025: +0.212 | 2026: +0.109
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=1.26
- Early IC=+0.0904, Recent IC=+0.1142, 1st-half IC=+0.0860, 2nd-half IC=+0.1199, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.131, Q3_mid=+0.119, Q4=+0.102, Q5_high_vol=+0.102

**`combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1348, Sharpe=+0.9350)
- Admission: Train IC=+0.1744, Deflated=+0.1740, IR=0.47, Mono=0.65, p=0.0006, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.162 | 2016: -0.039 | 2017: +0.005 | 2018: +0.077 | 2019: +0.165 | 2020: +0.060 | 2021: +0.127 | 2022: +0.121 | 2023: +0.086 | 2024: +0.085 | 2025: +0.139 | 2026: +0.135
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.010 | 2017: +0.045 | 2018: +0.192 | 2019: +0.322 | 2020: +0.175 | 2021: +0.165 | 2022: +0.139 | 2023: +0.022 | 2024: +0.240 | 2025: +0.150 | 2026: +0.332
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=0.93
- Early IC=+0.1212, Recent IC=+0.1124, 1st-half IC=+0.1101, 2nd-half IC=+0.1184, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.102, Q3_mid=+0.136, Q4=+0.122, Q5_high_vol=+0.119

**`combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1224, Sharpe=+0.8794)
- Admission: Train IC=+0.3337, Deflated=+0.3345, IR=1.04, Mono=0.85, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.099 | 2017: -0.034 | 2018: +0.128 | 2019: +0.270 | 2020: +0.154 | 2021: +0.132 | 2022: +0.053 | 2023: +0.130 | 2024: +0.117 | 2025: +0.119 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.191 | 2017: +0.055 | 2018: +0.358 | 2019: +0.527 | 2020: +0.409 | 2021: +0.329 | 2022: +0.208 | 2023: +0.318 | 2024: +0.479 | 2025: +0.155 | 2026: +0.349
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.1992, Recent IC=+0.1180, 1st-half IC=+0.1679, 2nd-half IC=+0.1096, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.145, Q3_mid=+0.134, Q4=+0.127, Q5_high_vol=+0.159

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1093, Sharpe=+0.8621)
- Admission: Train IC=+0.3351, Deflated=+0.3365, IR=1.02, Mono=0.83, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.121 | 2017: -0.019 | 2018: +0.157 | 2019: +0.240 | 2020: +0.166 | 2021: +0.144 | 2022: +0.095 | 2023: +0.154 | 2024: +0.081 | 2025: +0.171 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.089 | 2017: -0.027 | 2018: +0.488 | 2019: +0.475 | 2020: +0.344 | 2021: +0.352 | 2022: +0.141 | 2023: +0.267 | 2024: +0.322 | 2025: +0.369 | 2026: +0.282
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.65
- Early IC=+0.1967, Recent IC=+0.1280, 1st-half IC=+0.1701, 2nd-half IC=+0.1322, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.173, Q3_mid=+0.119, Q4=+0.144, Q5_high_vol=+0.191

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0919, Sharpe=+0.8492)
- Admission: Train IC=+0.2985, Deflated=+0.2990, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.175 | 2017: -0.022 | 2018: +0.134 | 2019: +0.199 | 2020: +0.135 | 2021: +0.120 | 2022: +0.084 | 2023: +0.132 | 2024: +0.083 | 2025: +0.159 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.225 | 2017: +0.157 | 2018: +0.279 | 2019: +0.349 | 2020: +0.168 | 2021: +0.318 | 2022: +0.193 | 2023: +0.256 | 2024: +0.272 | 2025: +0.258 | 2026: +0.182
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.73
- Early IC=+0.1664, Recent IC=+0.1209, 1st-half IC=+0.1391, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.135, Q3_mid=+0.143, Q4=+0.088, Q5_high_vol=+0.133

**`combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1209, Sharpe=+0.7808)
- Admission: Train IC=+0.2412, Deflated=+0.2410, IR=0.62, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.044 | 2017: -0.054 | 2018: +0.073 | 2019: +0.131 | 2020: +0.100 | 2021: +0.042 | 2022: +0.180 | 2023: +0.112 | 2024: +0.081 | 2025: +0.126 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.166 | 2017: +0.014 | 2018: +0.359 | 2019: +0.259 | 2020: +0.391 | 2021: +0.172 | 2022: +0.463 | 2023: +0.068 | 2024: +0.023 | 2025: +0.066 | 2026: +0.302
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.02
- Early IC=+0.1034, Recent IC=+0.1059, 1st-half IC=+0.0883, 2nd-half IC=+0.1320, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.117, Q3_mid=+0.098, Q4=+0.121, Q5_high_vol=+0.140

**`combo_rank_min__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0850, Sharpe=+0.6640)
- Admission: Train IC=+0.2595, Deflated=+0.2603, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.068 | 2017: +0.003 | 2018: +0.069 | 2019: +0.212 | 2020: +0.149 | 2021: +0.125 | 2022: +0.111 | 2023: +0.156 | 2024: +0.108 | 2025: +0.170 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.140 | 2017: +0.069 | 2018: +0.291 | 2019: +0.442 | 2020: +0.162 | 2021: +0.354 | 2022: +0.262 | 2023: +0.226 | 2024: +0.237 | 2025: +0.120 | 2026: +0.056
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.99
- Early IC=+0.1405, Recent IC=+0.1387, 1st-half IC=+0.1368, 2nd-half IC=+0.1400, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.171, Q3_mid=+0.137, Q4=+0.137, Q5_high_vol=+0.160

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0503, Sharpe=+0.6600)
- Admission: Train IC=+0.2707, Deflated=+0.2710, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.140 | 2017: +0.020 | 2018: +0.094 | 2019: +0.236 | 2020: +0.148 | 2021: +0.128 | 2022: +0.100 | 2023: +0.138 | 2024: +0.104 | 2025: +0.188 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.201 | 2017: +0.311 | 2018: +0.163 | 2019: +0.495 | 2020: +0.306 | 2021: +0.135 | 2022: +0.273 | 2023: +0.303 | 2024: +0.236 | 2025: +0.336 | 2026: +0.174
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.89
- Early IC=+0.1652, Recent IC=+0.1462, 1st-half IC=+0.1493, 2nd-half IC=+0.1356, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.148, Q3_mid=+0.146, Q4=+0.133, Q5_high_vol=+0.168

**`combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0673, Sharpe=+0.6455)
- Admission: Train IC=+0.2012, Deflated=+0.2012, IR=0.60, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.157 | 2016: +0.015 | 2017: +0.017 | 2018: +0.040 | 2019: +0.121 | 2020: +0.054 | 2021: +0.146 | 2022: +0.097 | 2023: +0.132 | 2024: +0.111 | 2025: +0.123 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.023 | 2017: +0.006 | 2018: +0.196 | 2019: +0.341 | 2020: +0.179 | 2021: +0.285 | 2022: +0.117 | 2023: +0.270 | 2024: +0.333 | 2025: +0.100 | 2026: +0.267
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.45, Recency ratio=1.46
- Early IC=+0.0805, Recent IC=+0.1173, 1st-half IC=+0.0860, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.130, Q3_mid=+0.102, Q4=+0.122, Q5_high_vol=+0.117

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0827, Sharpe=+0.6302)
- Admission: Train IC=+0.3748, Deflated=+0.3754, IR=1.23, Mono=0.88, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.085 | 2017: -0.024 | 2018: +0.158 | 2019: +0.247 | 2020: +0.160 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.131 | 2025: +0.160 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.128 | 2017: +0.057 | 2018: +0.432 | 2019: +0.570 | 2020: +0.328 | 2021: +0.403 | 2022: +0.289 | 2023: +0.412 | 2024: +0.423 | 2025: +0.178 | 2026: +0.297
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.72
- Early IC=+0.2024, Recent IC=+0.1456, 1st-half IC=+0.1681, 2nd-half IC=+0.1434, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.172, Q3_mid=+0.138, Q4=+0.167, Q5_high_vol=+0.172

**`combo_diff__limit_down_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1236, Sharpe=+0.6182)
- Admission: Train IC=+0.1750, Deflated=+0.1746, IR=0.47, Mono=0.66, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.168 | 2016: -0.040 | 2017: +0.001 | 2018: +0.079 | 2019: +0.163 | 2020: +0.063 | 2021: +0.130 | 2022: +0.125 | 2023: +0.095 | 2024: +0.084 | 2025: +0.141 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.095 | 2016: +0.016 | 2017: +0.048 | 2018: +0.199 | 2019: +0.319 | 2020: +0.173 | 2021: +0.164 | 2022: +0.142 | 2023: +0.025 | 2024: +0.240 | 2025: +0.162 | 2026: +0.278
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=0.93
- Early IC=+0.1208, Recent IC=+0.1126, 1st-half IC=+0.1122, 2nd-half IC=+0.1203, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.102, Q3_mid=+0.137, Q4=+0.128, Q5_high_vol=+0.121

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1637, Sharpe=+0.5943)
- Admission: Train IC=+0.2042, Deflated=+0.2037, IR=0.48, Mono=0.66, p=0.0002, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.104 | 2017: -0.004 | 2018: +0.114 | 2019: +0.160 | 2020: +0.124 | 2021: +0.142 | 2022: +0.160 | 2023: +0.118 | 2024: +0.098 | 2025: +0.143 | 2026: +0.164
- Yearly Tail ICs:   2015: -0.025 | 2016: +0.251 | 2017: +0.133 | 2018: +0.320 | 2019: +0.186 | 2020: +0.196 | 2021: +0.302 | 2022: +0.171 | 2023: -0.033 | 2024: +0.201 | 2025: +0.018 | 2026: +0.304
- IC CV=0.16, Neg years (linear/tail)=0/1 of 8, Half ratio=0.91, Recency ratio=0.88
- Early IC=+0.1370, Recent IC=+0.1206, 1st-half IC=+0.1487, 2nd-half IC=+0.1359, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.137, Q3_mid=+0.119, Q4=+0.168, Q5_high_vol=+0.153

**`combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1144, Sharpe=+0.5302)
- Admission: Train IC=+0.2943, Deflated=+0.2957, IR=1.10, Mono=0.86, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.083 | 2017: -0.035 | 2018: +0.113 | 2019: +0.261 | 2020: +0.144 | 2021: +0.118 | 2022: +0.072 | 2023: +0.151 | 2024: +0.107 | 2025: +0.149 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.119 | 2017: +0.027 | 2018: +0.283 | 2019: +0.516 | 2020: +0.218 | 2021: +0.306 | 2022: +0.266 | 2023: +0.354 | 2024: +0.410 | 2025: +0.092 | 2026: +0.228
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1867, Recent IC=+0.1281, 1st-half IC=+0.1519, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.154, Q3_mid=+0.137, Q4=+0.123, Q5_high_vol=+0.156

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1000, Sharpe=+0.4816)
- Admission: Train IC=+0.3521, Deflated=+0.3534, IR=1.04, Mono=0.85, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.110 | 2017: -0.012 | 2018: +0.158 | 2019: +0.260 | 2020: +0.173 | 2021: +0.134 | 2022: +0.082 | 2023: +0.152 | 2024: +0.096 | 2025: +0.160 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.130 | 2017: +0.034 | 2018: +0.352 | 2019: +0.560 | 2020: +0.402 | 2021: +0.271 | 2022: +0.184 | 2023: +0.346 | 2024: +0.447 | 2025: +0.203 | 2026: +0.257
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.61
- Early IC=+0.2090, Recent IC=+0.1283, 1st-half IC=+0.1771, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.166, Q3_mid=+0.134, Q4=+0.154, Q5_high_vol=+0.182

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1062, Sharpe=+0.3404)
- Admission: Train IC=+0.3108, Deflated=+0.3111, IR=1.02, Mono=0.85, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.159 | 2017: -0.015 | 2018: +0.157 | 2019: +0.230 | 2020: +0.184 | 2021: +0.136 | 2022: +0.108 | 2023: +0.127 | 2024: +0.092 | 2025: +0.153 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.079 | 2016: +0.184 | 2017: +0.022 | 2018: +0.341 | 2019: +0.411 | 2020: +0.331 | 2021: +0.319 | 2022: +0.225 | 2023: +0.238 | 2024: +0.462 | 2025: +0.237 | 2026: +0.178
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.63
- Early IC=+0.1938, Recent IC=+0.1222, 1st-half IC=+0.1756, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.131, Q3_mid=+0.161, Q4=+0.124, Q5_high_vol=+0.167

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1174, Sharpe=+0.3404)
- Admission: Train IC=+0.2981, Deflated=+0.2982, IR=0.96, Mono=0.85, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.158 | 2017: -0.014 | 2018: +0.176 | 2019: +0.223 | 2020: +0.181 | 2021: +0.159 | 2022: +0.114 | 2023: +0.122 | 2024: +0.079 | 2025: +0.155 | 2026: +0.117
- Yearly Tail ICs:   2015: -0.026 | 2016: +0.184 | 2017: +0.022 | 2018: +0.359 | 2019: +0.435 | 2020: +0.280 | 2021: +0.329 | 2022: +0.210 | 2023: +0.219 | 2024: +0.429 | 2025: +0.188 | 2026: +0.178
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.59
- Early IC=+0.1997, Recent IC=+0.1172, 1st-half IC=+0.1852, 2nd-half IC=+0.1215, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.131, Q3_mid=+0.160, Q4=+0.136, Q5_high_vol=+0.182

**`combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0852, Sharpe=+0.3263)
- Admission: Train IC=+0.1835, Deflated=+0.1829, IR=0.44, Mono=0.68, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.123 | 2017: -0.015 | 2018: +0.135 | 2019: +0.135 | 2020: +0.081 | 2021: +0.140 | 2022: +0.124 | 2023: +0.090 | 2024: +0.025 | 2025: +0.113 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.117 | 2016: -0.005 | 2017: +0.114 | 2018: +0.315 | 2019: +0.265 | 2020: -0.028 | 2021: +0.346 | 2022: +0.053 | 2023: +0.089 | 2024: +0.218 | 2025: +0.168 | 2026: +0.074
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.51
- Early IC=+0.1350, Recent IC=+0.0688, 1st-half IC=+0.1197, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.083, Q3_mid=+0.124, Q4=+0.074, Q5_high_vol=+0.104

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1358, Sharpe=+0.2908)
- Admission: Train IC=+0.2041, Deflated=+0.2031, IR=0.49, Mono=0.66, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.177 | 2017: -0.014 | 2018: +0.140 | 2019: +0.155 | 2020: +0.151 | 2021: +0.143 | 2022: +0.133 | 2023: +0.105 | 2024: +0.046 | 2025: +0.138 | 2026: +0.136
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.158 | 2017: +0.136 | 2018: +0.342 | 2019: +0.277 | 2020: +0.067 | 2021: +0.394 | 2022: +0.100 | 2023: +0.080 | 2024: +0.165 | 2025: +0.041 | 2026: +0.185
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.63
- Early IC=+0.1474, Recent IC=+0.0922, 1st-half IC=+0.1488, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.105, Q3_mid=+0.150, Q4=+0.104, Q5_high_vol=+0.132

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0832, Sharpe=+0.2726)
- Admission: Train IC=+0.2831, Deflated=+0.2836, IR=0.83, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.131 | 2017: -0.010 | 2018: +0.179 | 2019: +0.223 | 2020: +0.149 | 2021: +0.151 | 2022: +0.098 | 2023: +0.146 | 2024: +0.084 | 2025: +0.161 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.033 | 2017: +0.181 | 2018: +0.280 | 2019: +0.406 | 2020: +0.205 | 2021: +0.393 | 2022: +0.145 | 2023: +0.200 | 2024: +0.349 | 2025: +0.251 | 2026: +0.170
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.61
- Early IC=+0.2009, Recent IC=+0.1223, 1st-half IC=+0.1651, 2nd-half IC=+0.1251, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.141, Q3_mid=+0.151, Q4=+0.107, Q5_high_vol=+0.175

**`first_bar_return`** (Lock IC=+0.0226, Sharpe=+0.2558)
- Admission: Train IC=+0.1648, Deflated=+0.1657, IR=0.60, Mono=0.73, p=0.0014, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.162 | 2017: +0.017 | 2018: +0.137 | 2019: +0.192 | 2020: +0.116 | 2021: +0.135 | 2022: +0.073 | 2023: +0.144 | 2024: +0.061 | 2025: +0.123 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.56
- Early IC=+0.1645, Recent IC=+0.0918, 1st-half IC=+0.1316, 2nd-half IC=+0.0981, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.130, Q3_mid=+0.113, Q4=+0.063, Q5_high_vol=+0.129

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0895, Sharpe=+0.2487)
- Admission: Train IC=+0.2787, Deflated=+0.2803, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.089 | 2017: -0.005 | 2018: +0.152 | 2019: +0.243 | 2020: +0.141 | 2021: +0.127 | 2022: +0.097 | 2023: +0.137 | 2024: +0.074 | 2025: +0.163 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.061 | 2017: +0.081 | 2018: +0.317 | 2019: +0.501 | 2020: +0.216 | 2021: +0.253 | 2022: +0.263 | 2023: +0.223 | 2024: +0.413 | 2025: +0.118 | 2026: +0.249
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.60
- Early IC=+0.1974, Recent IC=+0.1185, 1st-half IC=+0.1593, 2nd-half IC=+0.1236, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.159, Q3_mid=+0.120, Q4=+0.138, Q5_high_vol=+0.178

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0641, Sharpe=+0.2487)
- Admission: Train IC=+0.2804, Deflated=+0.2815, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.132 | 2017: -0.020 | 2018: +0.155 | 2019: +0.240 | 2020: +0.159 | 2021: +0.129 | 2022: +0.084 | 2023: +0.087 | 2024: +0.087 | 2025: +0.128 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.082 | 2017: +0.047 | 2018: +0.317 | 2019: +0.499 | 2020: +0.239 | 2021: +0.257 | 2022: +0.256 | 2023: +0.218 | 2024: +0.421 | 2025: +0.105 | 2026: +0.238
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.55
- Early IC=+0.1974, Recent IC=+0.1077, 1st-half IC=+0.1660, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.133, Q3_mid=+0.121, Q4=+0.133, Q5_high_vol=+0.172

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.2449)
- Admission: Train IC=+0.2506, Deflated=+0.2503, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.51
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.047 | 2017: -0.045 | 2018: +0.086 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.181 | 2023: +0.115 | 2024: +0.084 | 2025: +0.129 | 2026: +0.129
- Yearly Tail ICs:   2015: +0.142 | 2016: +0.229 | 2017: +0.092 | 2018: +0.360 | 2019: +0.281 | 2020: +0.401 | 2021: +0.125 | 2022: +0.494 | 2023: +0.111 | 2024: +0.061 | 2025: +0.103 | 2026: +0.261
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=0.98
- Early IC=+0.1084, Recent IC=+0.1064, 1st-half IC=+0.0883, 2nd-half IC=+0.1293, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.113, Q3_mid=+0.089, Q4=+0.122, Q5_high_vol=+0.143

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0486, Sharpe=+0.1892)
- Admission: Train IC=+0.3411, Deflated=+0.3414, IR=1.20, Mono=0.86, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.130 | 2017: -0.013 | 2018: +0.190 | 2019: +0.209 | 2020: +0.171 | 2021: +0.134 | 2022: +0.099 | 2023: +0.146 | 2024: +0.106 | 2025: +0.133 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.153 | 2016: +0.120 | 2017: +0.115 | 2018: +0.368 | 2019: +0.527 | 2020: +0.324 | 2021: +0.264 | 2022: +0.392 | 2023: +0.401 | 2024: +0.319 | 2025: +0.271 | 2026: +0.186
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.60
- Early IC=+0.1994, Recent IC=+0.1196, 1st-half IC=+0.1704, 2nd-half IC=+0.1231, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.158, Q3_mid=+0.124, Q4=+0.165, Q5_high_vol=+0.168

**`combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1158, Sharpe=+0.1892)
- Admission: Train IC=+0.2098, Deflated=+0.2088, IR=0.50, Mono=0.66, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.114 | 2017: -0.008 | 2018: +0.121 | 2019: +0.159 | 2020: +0.101 | 2021: +0.124 | 2022: +0.158 | 2023: +0.107 | 2024: +0.058 | 2025: +0.154 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.124 | 2016: -0.008 | 2017: +0.178 | 2018: +0.314 | 2019: +0.290 | 2020: +0.062 | 2021: +0.318 | 2022: +0.128 | 2023: +0.165 | 2024: +0.183 | 2025: +0.116 | 2026: -0.096
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.71
- Early IC=+0.1429, Recent IC=+0.1016, 1st-half IC=+0.1318, 2nd-half IC=+0.1176, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.105, Q3_mid=+0.145, Q4=+0.116, Q5_high_vol=+0.108

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0535, Sharpe=+0.1627)
- Admission: Train IC=+0.2624, Deflated=+0.2624, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.058 | 2017: +0.036 | 2018: +0.103 | 2019: +0.108 | 2020: +0.063 | 2021: +0.168 | 2022: +0.136 | 2023: +0.149 | 2024: +0.108 | 2025: +0.178 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.200 | 2017: +0.109 | 2018: +0.288 | 2019: +0.267 | 2020: +0.250 | 2021: +0.320 | 2022: +0.153 | 2023: +0.120 | 2024: +0.388 | 2025: +0.259 | 2026: +0.229
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.35, Recency ratio=1.36
- Early IC=+0.1052, Recent IC=+0.1430, 1st-half IC=+0.1093, 2nd-half IC=+0.1478, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.151, Q3_mid=+0.099, Q4=+0.162, Q5_high_vol=+0.159

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0646, Sharpe=+0.1352)
- Admission: Train IC=+0.2982, Deflated=+0.2982, IR=0.96, Mono=0.85, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.26
- Early IC=+0.1165, Recent IC=+0.1473, 1st-half IC=+0.1261, 2nd-half IC=+0.1540, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.169, Q3_mid=+0.123, Q4=+0.150, Q5_high_vol=+0.162

**`combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1013, Sharpe=+0.1249)
- Admission: Train IC=+0.2369, Deflated=+0.2367, IR=0.83, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.024 | 2017: +0.014 | 2018: +0.116 | 2019: +0.216 | 2020: +0.088 | 2021: +0.135 | 2022: +0.100 | 2023: +0.144 | 2024: +0.112 | 2025: +0.141 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.021 | 2017: +0.114 | 2018: +0.149 | 2019: +0.465 | 2020: +0.069 | 2021: +0.216 | 2022: +0.175 | 2023: +0.322 | 2024: +0.417 | 2025: +0.143 | 2026: +0.169
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.1660, Recent IC=+0.1263, 1st-half IC=+0.1300, 2nd-half IC=+0.1324, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.124, Q3_mid=+0.129, Q4=+0.141, Q5_high_vol=+0.149

**`combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1554, Sharpe=+0.1107)
- Admission: Train IC=+0.2406, Deflated=+0.2403, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.070 | 2017: -0.066 | 2018: +0.120 | 2019: +0.118 | 2020: +0.123 | 2021: +0.050 | 2022: +0.167 | 2023: +0.129 | 2024: +0.048 | 2025: +0.080 | 2026: +0.155
- Yearly Tail ICs:   2015: +0.092 | 2016: +0.241 | 2017: +0.021 | 2018: +0.415 | 2019: +0.337 | 2020: +0.371 | 2021: +0.126 | 2022: +0.465 | 2023: +0.109 | 2024: +0.012 | 2025: +0.071 | 2026: +0.170
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.53
- Early IC=+0.1190, Recent IC=+0.0636, 1st-half IC=+0.1013, 2nd-half IC=+0.1023, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.107, Q3_mid=+0.082, Q4=+0.126, Q5_high_vol=+0.139

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0431, Sharpe=+0.1011)
- Admission: Train IC=+0.2416, Deflated=+0.2424, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.122 | 2017: +0.026 | 2018: +0.091 | 2019: +0.207 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.175 | 2024: +0.041 | 2025: +0.186 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.172 | 2017: +0.144 | 2018: +0.389 | 2019: +0.275 | 2020: +0.048 | 2021: +0.333 | 2022: +0.199 | 2023: +0.371 | 2024: +0.174 | 2025: +0.362 | 2026: +0.097
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.76
- Early IC=+0.1490, Recent IC=+0.1136, 1st-half IC=+0.1439, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.168, Q3_mid=+0.133, Q4=+0.102, Q5_high_vol=+0.127

**`combo_mean__limit_down_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1186, Sharpe=+0.0733)
- Admission: Train IC=+0.2565, Deflated=+0.2561, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.065 | 2017: +0.036 | 2018: +0.117 | 2019: +0.221 | 2020: +0.039 | 2021: +0.171 | 2022: +0.041 | 2023: +0.114 | 2024: +0.095 | 2025: +0.141 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.163 | 2016: -0.114 | 2017: +0.150 | 2018: +0.113 | 2019: +0.565 | 2020: +0.079 | 2021: +0.336 | 2022: +0.103 | 2023: +0.304 | 2024: +0.311 | 2025: +0.172 | 2026: +0.183
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.70
- Early IC=+0.1690, Recent IC=+0.1180, 1st-half IC=+0.1347, 2nd-half IC=+0.1039, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.114, Q3_mid=+0.140, Q4=+0.117, Q5_high_vol=+0.132

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0307, Sharpe=+0.0580)
- Admission: Train IC=+0.2465, Deflated=+0.2477, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.098 | 2017: +0.025 | 2018: +0.117 | 2019: +0.191 | 2020: +0.105 | 2021: +0.139 | 2022: +0.076 | 2023: +0.195 | 2024: +0.059 | 2025: +0.146 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.057 | 2017: +0.053 | 2018: +0.316 | 2019: +0.340 | 2020: +0.162 | 2021: +0.170 | 2022: +0.123 | 2023: +0.503 | 2024: +0.150 | 2025: +0.256 | 2026: +0.117
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.67
- Early IC=+0.1537, Recent IC=+0.1027, 1st-half IC=+0.1318, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.173, Q3_mid=+0.105, Q4=+0.105, Q5_high_vol=+0.116

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0098, Sharpe=+0.0371)
- Admission: Train IC=+0.1642, Deflated=+0.1650, IR=0.55, Mono=0.73, p=0.0016, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.162 | 2017: +0.008 | 2018: +0.135 | 2019: +0.197 | 2020: +0.110 | 2021: +0.134 | 2022: +0.058 | 2023: +0.150 | 2024: +0.061 | 2025: +0.114 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.213 | 2016: -0.007 | 2017: +0.182 | 2018: +0.264 | 2019: +0.189 | 2020: +0.132 | 2021: +0.304 | 2022: +0.034 | 2023: +0.403 | 2024: +0.123 | 2025: +0.229 | 2026: +0.139
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.53
- Early IC=+0.1656, Recent IC=+0.0878, 1st-half IC=+0.1317, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.130, Q3_mid=+0.104, Q4=+0.062, Q5_high_vol=+0.125

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0587, Sharpe=+0.0073)
- Admission: Train IC=+0.2979, Deflated=+0.2987, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.151 | 2017: -0.006 | 2018: +0.182 | 2019: +0.231 | 2020: +0.184 | 2021: +0.134 | 2022: +0.085 | 2023: +0.125 | 2024: +0.087 | 2025: +0.127 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.162 | 2016: +0.286 | 2017: +0.029 | 2018: +0.408 | 2019: +0.413 | 2020: +0.270 | 2021: +0.271 | 2022: +0.269 | 2023: +0.192 | 2024: +0.326 | 2025: +0.271 | 2026: +0.184
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.52
- Early IC=+0.2063, Recent IC=+0.1068, 1st-half IC=+0.1778, 2nd-half IC=+0.1086, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.145, Q3_mid=+0.135, Q4=+0.135, Q5_high_vol=+0.186

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_max__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Median | persistent | +0.0844 | N/A | +0.0844 | ∞ |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Median | persistent | +0.0709 | N/A | +0.0709 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0628 | N/A | +0.0628 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0449 | N/A | +0.0449 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0272 | N/A | +0.0272 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0147 | N/A | +0.0147 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0132 | N/A | +0.0132 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0035 | N/A | +0.0035 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Median | persistent | +0.0005 | N/A | +0.0005 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | FP | immediate | -0.0023 | N/A | -0.0023 | ∞ |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | FP | immediate | -0.0121 | N/A | -0.0121 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0127 | N/A | -0.0127 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0169 | N/A | -0.0169 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | FP | immediate | -0.0199 | N/A | -0.0199 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0293 | N/A | -0.0293 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.0294 | N/A | -0.0294 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | FP | immediate | -0.0297 | N/A | -0.0297 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0308 | N/A | -0.0308 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | FP | immediate | -0.0504 | N/A | -0.0504 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | FP | immediate | -0.0538 | N/A | -0.0538 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0539 | N/A | -0.0539 | ∞ |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.0557 | N/A | -0.0557 | ∞ |
| `combo_sig_product__bar_body_rng_0__volume_surge_direction` | FP | immediate | -0.0580 | N/A | -0.0580 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0581 | N/A | -0.0581 | ∞ |
| `combo_min__max_up_ret__volume_surge_direction` | FP | immediate | -0.0597 | N/A | -0.0597 | ∞ |
| `combo_min__bar_body_rng_0__volume_surge_direction` | FP | immediate | -0.0625 | N/A | -0.0625 | ∞ |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.0631 | N/A | -0.0631 | ∞ |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0638 | N/A | -0.0638 | ∞ |
| `combo_rank_min__max_up_ret__volume_surge_direction` | FP | immediate | -0.0639 | N/A | -0.0639 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0648 | N/A | -0.0648 | ∞ |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.0691 | N/A | -0.0691 | ∞ |
| `combo_min__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0691 | N/A | -0.0691 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0712 | N/A | -0.0712 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | FP | immediate | -0.0717 | N/A | -0.0717 | ∞ |
| `combo_mean__first_bar_sentiment__volume_surge_direction` | FP | immediate | -0.0740 | N/A | -0.0740 | ∞ |
| `combo_min__bar_ret_0__volume_surge_direction` | FP | immediate | -0.0762 | N/A | -0.0762 | ∞ |
| `combo_rank_max__first_bar_return__volume_surge_direction` | FP | immediate | -0.0811 | N/A | -0.0811 | ∞ |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.0823 | N/A | -0.0823 | ∞ |
| `first_bar_return` | FP | immediate | -0.0827 | N/A | -0.0827 | ∞ |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0828 | N/A | -0.0828 | ∞ |
| `combo_max__bar_ret_0__volume_surge_direction` | FP | immediate | -0.0832 | N/A | -0.0832 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | FP | immediate | -0.0842 | N/A | -0.0842 | ∞ |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | FP | immediate | -0.0889 | N/A | -0.0889 | ∞ |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0908 | N/A | -0.0908 | ∞ |
| `combo_sig_product__bar_ret_0__volume_weighted_price_position` | FP | immediate | -0.0908 | N/A | -0.0908 | ∞ |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0924 | N/A | -0.0924 | ∞ |
| `combo_max__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0930 | N/A | -0.0930 | ∞ |
| `combo_ratio__bar_ret_0__volume_surge_direction` | FP | immediate | -0.0934 | N/A | -0.0934 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0955 | N/A | -0.0955 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_return` | FP | immediate | -0.0956 | N/A | -0.0956 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.0969 | N/A | -0.0969 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1002 | N/A | -0.1002 | ∞ |
| `combo_tri_mean__bar_ret_0__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1078 | N/A | -0.1078 | ∞ |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1081 | N/A | -0.1081 | ∞ |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1087 | N/A | -0.1087 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.1148 | N/A | -0.1148 | ∞ |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1153 | N/A | -0.1153 | ∞ |
| `combo_mean__max_up_ret__volume_surge_direction` | FP | immediate | -0.1168 | N/A | -0.1168 | ∞ |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.1191 | N/A | -0.1191 | ∞ |
| `combo_ratio__volume_surge_direction__volume_weighted_price_position` | FP | immediate | -0.1192 | N/A | -0.1192 | ∞ |
| `combo_mean__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1215 | N/A | -0.1215 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.1221 | N/A | -0.1221 | ∞ |
| `combo_tri_median__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1287 | N/A | -0.1287 | ∞ |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1294 | N/A | -0.1294 | ∞ |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1298 | N/A | -0.1298 | ∞ |
| `combo_max__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1306 | N/A | -0.1306 | ∞ |
| `combo_tri_max__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1364 | N/A | -0.1364 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | FP | immediate | -0.1395 | N/A | -0.1395 | ∞ |
| `combo_max__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.1417 | N/A | -0.1417 | ∞ |
| `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1421 | N/A | -0.1421 | ∞ |
| `combo_ratio__max_up_ret__bar_vol_0` | FP | immediate | -0.1432 | N/A | -0.1432 | ∞ |
| `combo_max__max_up_ret__volume_surge_direction` | FP | immediate | -0.1457 | N/A | -0.1457 | ∞ |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1466 | N/A | -0.1466 | ∞ |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | FP | immediate | -0.1476 | N/A | -0.1476 | ∞ |
| `combo_tri_mean__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.1480 | N/A | -0.1480 | ∞ |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1502 | N/A | -0.1502 | ∞ |
| `combo_rank_max__max_up_ret__volume_surge_direction` | FP | immediate | -0.1503 | N/A | -0.1503 | ∞ |
| `opening_drive_thrust_ratio` | FP | immediate | -0.1510 | N/A | -0.1510 | ∞ |
| `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1526 | N/A | -0.1526 | ∞ |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1563 | N/A | -0.1563 | ∞ |
| `combo_rank_max__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.1571 | N/A | -0.1571 | ∞ |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1573 | N/A | -0.1573 | ∞ |
| `volume_weighted_price_position` | FP | immediate | -0.1599 | N/A | -0.1599 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_return` | FP | immediate | -0.1611 | N/A | -0.1611 | ∞ |
| `combo_max__max_up_ret__first_bar_return` | FP | immediate | -0.1615 | N/A | -0.1615 | ∞ |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1708 | N/A | -0.1708 | ∞ |
| `morning_volume_weighted_momentum` | FP | immediate | -0.1752 | N/A | -0.1752 | ∞ |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1762 | N/A | -0.1762 | ∞ |
| `net_volume_flow` | FP | immediate | -0.1763 | N/A | -0.1763 | ∞ |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1823 | N/A | -0.1823 | ∞ |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1853 | N/A | -0.1853 | ∞ |
| `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.1947 | N/A | -0.1947 | ∞ |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1964 | N/A | -0.1964 | ∞ |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1967 | N/A | -0.1967 | ∞ |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1994 | N/A | -0.1994 | ∞ |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.2002 | N/A | -0.2002 | ∞ |
| `early_order_flow_imbalance` | FP | immediate | -0.2024 | N/A | -0.2024 | ∞ |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.2114 | N/A | -0.2114 | ∞ |
| `always_in_trend_persistence` | FP | immediate | -0.2597 | N/A | -0.2597 | ∞ |

**Decay distribution**: immediate=90, fast(1-2y)=0, gradual=0, persistent=9

**FP decay trajectories:**

- `always_in_trend_persistence`: Y1:-0.260
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.211
- `early_order_flow_imbalance`: Y1:-0.202
- `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.200
- `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.199
- `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.197
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:-0.196
- `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.195
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:-0.185
- `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position`: Y1:-0.182
- `net_volume_flow`: Y1:-0.176
- `combo_rank_max__first_bar_return__volume_weighted_price_position`: Y1:-0.176
- `morning_volume_weighted_momentum`: Y1:-0.175
- `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.171
- `combo_max__max_up_ret__first_bar_return`: Y1:-0.162
- `combo_rank_max__max_up_ret__first_bar_return`: Y1:-0.161
- `volume_weighted_price_position`: Y1:-0.160
- `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.157
- `combo_rank_max__volume_weighted_price_position__volume_surge_direction`: Y1:-0.157
- `combo_tri_median__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.156
- `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.153
- `opening_drive_thrust_ratio`: Y1:-0.151
- `combo_rank_max__max_up_ret__volume_surge_direction`: Y1:-0.150
- `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.150
- `combo_tri_mean__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.148
- `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`: Y1:-0.148
- `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.147
- `combo_max__max_up_ret__volume_surge_direction`: Y1:-0.146
- `combo_ratio__max_up_ret__bar_vol_0`: Y1:-0.143
- `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.142
- `combo_max__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.142
- `combo_max__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:-0.140
- `combo_tri_max__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.136
- `combo_max__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.131
- `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.130
- `combo_sig_product__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.129
- `combo_tri_median__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.129
- `combo_mean__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.122
- `combo_mean__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.122
- `combo_ratio__volume_surge_direction__volume_weighted_price_position`: Y1:-0.119
- `combo_mean__volume_weighted_price_position__volume_surge_direction`: Y1:-0.119
- `combo_mean__max_up_ret__volume_surge_direction`: Y1:-0.117
- `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.115
- `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.115
- `combo_ratio__first_bar_return__volume_weighted_price_position`: Y1:-0.109
- `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.108
- `combo_tri_mean__bar_ret_0__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.108
- `combo_sig_product__max_up_ret__volume_weighted_price_position`: Y1:-0.100
- `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.097
- `combo_rank_min__max_up_ret__first_bar_return`: Y1:-0.096
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.095
- `combo_ratio__bar_ret_0__volume_surge_direction`: Y1:-0.093
- `combo_max__first_bar_return__first_bar_sentiment`: Y1:-0.093
- `combo_min__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.092
- `combo_sig_product__first_bar_return__volume_weighted_price_position`: Y1:-0.091
- `combo_sig_product__bar_ret_0__volume_weighted_price_position`: Y1:-0.091
- `combo_rank_max__first_bar_return__bar_body_rng_0`: Y1:-0.089
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Y1:-0.084
- `combo_max__bar_ret_0__volume_surge_direction`: Y1:-0.083
- `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.083
- `first_bar_return`: Y1:-0.083
- `combo_min__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.082
- `combo_rank_max__first_bar_return__volume_surge_direction`: Y1:-0.081
- `combo_min__bar_ret_0__volume_surge_direction`: Y1:-0.076
- `combo_mean__first_bar_sentiment__volume_surge_direction`: Y1:-0.074
- `combo_sig_product__max_up_ret__first_bar_return`: Y1:-0.072
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.071
- `combo_min__first_bar_return__first_bar_sentiment`: Y1:-0.069
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Y1:-0.069
- `combo_rank_min__max_up_ret__first_bar_sentiment`: Y1:-0.065
- `combo_rank_min__max_up_ret__volume_surge_direction`: Y1:-0.064
- `combo_rank_min__first_bar_return__first_bar_sentiment`: Y1:-0.064
- `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.063
- `combo_min__bar_body_rng_0__volume_surge_direction`: Y1:-0.062
- `combo_min__max_up_ret__volume_surge_direction`: Y1:-0.060
- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.058
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Y1:-0.058
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Y1:-0.056
- `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.054
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Y1:-0.054
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Y1:-0.050
- `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.031
- `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Y1:-0.030
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Y1:-0.029
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.029
- `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Y1:-0.020
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.017
- `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.013
- `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Y1:-0.012
- `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Y1:-0.002

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1800 | N/A | +0.1800 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1783 | N/A | +0.1783 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1749 | N/A | +0.1749 | ∞ |
| `combo_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1499 | N/A | +0.1499 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1466 | N/A | +0.1466 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.1323 | N/A | +0.1323 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__early_late_momentum_divergence` | TP | persistent | +0.1145 | N/A | +0.1145 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1067 | N/A | +0.1067 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.1045 | N/A | +0.1045 | ∞ |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Median | persistent | +0.1008 | N/A | +0.1008 | ∞ |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0988 | N/A | +0.0988 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0947 | N/A | +0.0947 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0865 | N/A | +0.0865 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Median | persistent | +0.0832 | N/A | +0.0832 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0823 | N/A | +0.0823 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0820 | N/A | +0.0820 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | TP | persistent | +0.0811 | N/A | +0.0811 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.0770 | N/A | +0.0770 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | persistent | +0.0765 | N/A | +0.0765 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0759 | N/A | +0.0759 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0755 | N/A | +0.0755 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0727 | N/A | +0.0727 | ∞ |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0708 | N/A | +0.0708 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0695 | N/A | +0.0695 | ∞ |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0678 | N/A | +0.0678 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.0674 | N/A | +0.0674 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0670 | N/A | +0.0670 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0600 | N/A | +0.0600 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.0571 | N/A | +0.0571 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | TP | persistent | +0.0527 | N/A | +0.0527 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Median | persistent | +0.0508 | N/A | +0.0508 | ∞ |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0462 | N/A | +0.0462 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0403 | N/A | +0.0403 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Median | persistent | +0.0383 | N/A | +0.0383 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.0380 | N/A | +0.0380 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | persistent | +0.0350 | N/A | +0.0350 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Median | persistent | +0.0343 | N/A | +0.0343 | ∞ |
| `max_down_ret` | Median | persistent | +0.0305 | N/A | +0.0305 | ∞ |
| `combo_rank_max__bar_ret_0__max_down_ret` | Median | persistent | +0.0298 | N/A | +0.0298 | ∞ |
| `combo_sig_product__max_up_ret__body_size_progression` | Median | persistent | +0.0274 | N/A | +0.0274 | ∞ |
| `combo_mean__first_bar_sentiment__max_down_ret` | Median | persistent | +0.0243 | N/A | +0.0243 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Median | persistent | +0.0234 | N/A | +0.0234 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.0234 | N/A | +0.0234 | ∞ |
| `combo_max__first_bar_sentiment__bar_ret_0` | Median | persistent | +0.0228 | N/A | +0.0228 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0216 | N/A | +0.0216 | ∞ |
| `volume_surge_direction` | Median | persistent | +0.0202 | N/A | +0.0202 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0187 | N/A | +0.0187 | ∞ |
| `combo_rank_min__net_volume_flow__bar_ret_0` | Median | persistent | +0.0185 | N/A | +0.0185 | ∞ |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Median | persistent | +0.0177 | N/A | +0.0177 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | persistent | +0.0175 | N/A | +0.0175 | ∞ |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0152 | N/A | +0.0152 | ∞ |
| `bar_body_rng_0` | TP | persistent | +0.0133 | N/A | +0.0133 | ∞ |
| `combo_mean__first_bar_return__max_down_ret` | Median | persistent | +0.0117 | N/A | +0.0117 | ∞ |
| `combo_min__bar_ret_0__max_down_ret` | Median | persistent | +0.0115 | N/A | +0.0115 | ∞ |
| `combo_min__early_body_momentum__max_down_ret` | Median | persistent | +0.0091 | N/A | +0.0091 | ∞ |
| `combo_max__bar_ret_0__max_down_ret` | Median | persistent | +0.0077 | N/A | +0.0077 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0069 | N/A | +0.0069 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Median | persistent | +0.0058 | N/A | +0.0058 | ∞ |
| `combo_rank_min__bar_ret_0__max_down_ret` | Median | persistent | +0.0056 | N/A | +0.0056 | ∞ |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0033 | N/A | +0.0033 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0028 | N/A | +0.0028 | ∞ |
| `opening_drive_thrust_ratio` | Median | persistent | +0.0025 | N/A | +0.0025 | ∞ |
| `combo_min__close_vs_open_range__first_bar_return` | TP | persistent | +0.0019 | N/A | +0.0019 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | FP | immediate | -0.0002 | N/A | -0.0002 | ∞ |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | FP | immediate | -0.0002 | N/A | -0.0002 | ∞ |
| `combo_rank_min__max_up_ret__bar_ret_0` | FP | immediate | -0.0007 | N/A | -0.0007 | ∞ |
| `combo_min__net_volume_flow__first_bar_return` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | FP | immediate | -0.0012 | N/A | -0.0012 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | FP | immediate | -0.0019 | N/A | -0.0019 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | FP | immediate | -0.0061 | N/A | -0.0061 | ∞ |
| `combo_min__first_bar_sentiment__bar_ret_0` | FP | immediate | -0.0087 | N/A | -0.0087 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0104 | N/A | -0.0104 | ∞ |
| `combo_sig_product__max_up_ret__early_body_momentum` | FP | immediate | -0.0107 | N/A | -0.0107 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0114 | N/A | -0.0114 | ∞ |
| `first_bar_return` | FP | immediate | -0.0114 | N/A | -0.0114 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | FP | immediate | -0.0123 | N/A | -0.0123 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | FP | immediate | -0.0124 | N/A | -0.0124 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0132 | N/A | -0.0132 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | FP | immediate | -0.0136 | N/A | -0.0136 | ∞ |
| `combo_min__trend_bar_close_consistency__first_bar_return` | FP | immediate | -0.0156 | N/A | -0.0156 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0187 | N/A | -0.0187 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | FP | immediate | -0.0194 | N/A | -0.0194 | ∞ |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | FP | immediate | -0.0206 | N/A | -0.0206 | ∞ |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | FP | immediate | -0.0261 | N/A | -0.0261 | ∞ |
| `vwap_trend_channel_slope` | FP | immediate | -0.0312 | N/A | -0.0312 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | FP | immediate | -0.0323 | N/A | -0.0323 | ∞ |
| `combo_mean__max_up_ret__first_bar_return` | FP | immediate | -0.0337 | N/A | -0.0337 | ∞ |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | FP | immediate | -0.0367 | N/A | -0.0367 | ∞ |
| `combo_mean__close_vs_open_range__bar_ret_0` | FP | immediate | -0.0383 | N/A | -0.0383 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | FP | immediate | -0.0411 | N/A | -0.0411 | ∞ |
| `combo_min__net_volume_flow__first_bar_sentiment` | FP | immediate | -0.0444 | N/A | -0.0444 | ∞ |
| `combo_sig_product__net_volume_flow__max_down_ret` | FP | immediate | -0.0458 | N/A | -0.0458 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | FP | immediate | -0.0468 | N/A | -0.0468 | ∞ |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | FP | immediate | -0.0473 | N/A | -0.0473 | ∞ |
| `num_up_bars` | FP | immediate | -0.0474 | N/A | -0.0474 | ∞ |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | FP | immediate | -0.0520 | N/A | -0.0520 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | FP | immediate | -0.0523 | N/A | -0.0523 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | FP | immediate | -0.0526 | N/A | -0.0526 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | FP | immediate | -0.0592 | N/A | -0.0592 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | FP | immediate | -0.0624 | N/A | -0.0624 | ∞ |
| `combo_max__net_volume_flow__max_down_ret` | FP | immediate | -0.0643 | N/A | -0.0643 | ∞ |
| `combo_rank_max__max_up_ret__bar_ret_0` | FP | immediate | -0.0646 | N/A | -0.0646 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | FP | immediate | -0.0655 | N/A | -0.0655 | ∞ |
| `combo_max__close_vs_open_range__max_down_ret` | FP | immediate | -0.0673 | N/A | -0.0673 | ∞ |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0686 | N/A | -0.0686 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0689 | N/A | -0.0689 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | FP | immediate | -0.0695 | N/A | -0.0695 | ∞ |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0739 | N/A | -0.0739 | ∞ |
| `combo_min__close_vs_open_range__early_body_momentum` | FP | immediate | -0.0785 | N/A | -0.0785 | ∞ |
| `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` | FP | immediate | -0.0837 | N/A | -0.0837 | ∞ |
| `volatility_expansion_trend_vector` | FP | immediate | -0.0850 | N/A | -0.0850 | ∞ |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | FP | immediate | -0.0906 | N/A | -0.0906 | ∞ |
| `morning_volume_weighted_momentum` | FP | immediate | -0.0906 | N/A | -0.0906 | ∞ |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | FP | immediate | -0.0914 | N/A | -0.0914 | ∞ |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | FP | immediate | -0.0933 | N/A | -0.0933 | ∞ |
| `vwap_close_divergence_trend` | FP | immediate | -0.0940 | N/A | -0.0940 | ∞ |
| `combo_max__close_vs_open_range__early_body_momentum` | FP | immediate | -0.0947 | N/A | -0.0947 | ∞ |
| `combo_sig_product__net_volume_flow__first_bar_return` | FP | immediate | -0.1006 | N/A | -0.1006 | ∞ |
| `first_30min_return` | FP | immediate | -0.1128 | N/A | -0.1128 | ∞ |
| `early_order_flow_imbalance` | FP | immediate | -0.1345 | N/A | -0.1345 | ∞ |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | FP | immediate | -0.1430 | N/A | -0.1430 | ∞ |
| `always_in_trend_persistence` | FP | immediate | -0.1600 | N/A | -0.1600 | ∞ |

**Decay distribution**: immediate=59, fast(1-2y)=0, gradual=0, persistent=63

**FP decay trajectories:**

- `always_in_trend_persistence`: Y1:-0.160
- `combo_sig_product__volatility_expansion_trend_vector__first_bar_return`: Y1:-0.143
- `early_order_flow_imbalance`: Y1:-0.135
- `first_30min_return`: Y1:-0.113
- `combo_sig_product__net_volume_flow__first_bar_return`: Y1:-0.101
- `combo_max__close_vs_open_range__early_body_momentum`: Y1:-0.095
- `vwap_close_divergence_trend`: Y1:-0.094
- `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression`: Y1:-0.093
- `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0`: Y1:-0.091
- `morning_volume_weighted_momentum`: Y1:-0.091
- `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`: Y1:-0.091
- `volatility_expansion_trend_vector`: Y1:-0.085
- `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range`: Y1:-0.084
- `combo_min__close_vs_open_range__early_body_momentum`: Y1:-0.079
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.074
- `combo_sig_product__max_up_ret__bar_ret_0`: Y1:-0.069
- `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.069
- `combo_rank_max__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.069
- `combo_max__close_vs_open_range__max_down_ret`: Y1:-0.067
- `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency`: Y1:-0.065
- `combo_rank_max__max_up_ret__bar_ret_0`: Y1:-0.065
- `combo_max__net_volume_flow__max_down_ret`: Y1:-0.064
- `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`: Y1:-0.062
- `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression`: Y1:-0.059
- `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`: Y1:-0.053
- `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment`: Y1:-0.052
- `combo_max__volatility_expansion_trend_vector__first_bar_sentiment`: Y1:-0.052
- `num_up_bars`: Y1:-0.047
- `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`: Y1:-0.047
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`: Y1:-0.047
- `combo_sig_product__net_volume_flow__max_down_ret`: Y1:-0.046
- `combo_min__net_volume_flow__first_bar_sentiment`: Y1:-0.044
- `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`: Y1:-0.041
- `combo_mean__close_vs_open_range__bar_ret_0`: Y1:-0.038
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Y1:-0.037
- `combo_mean__max_up_ret__first_bar_return`: Y1:-0.034
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Y1:-0.032
- `vwap_trend_channel_slope`: Y1:-0.031
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Y1:-0.026
- `combo_sig_product__first_bar_sentiment__early_body_momentum`: Y1:-0.021
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`: Y1:-0.019
- `combo_mean__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.019
- `combo_min__trend_bar_close_consistency__first_bar_return`: Y1:-0.016
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression`: Y1:-0.014
- `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.013
- `combo_min__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:-0.012
- `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`: Y1:-0.012
- `first_bar_return`: Y1:-0.011
- `combo_rank_min__max_up_ret__first_bar_sentiment`: Y1:-0.011
- `combo_sig_product__max_up_ret__early_body_momentum`: Y1:-0.011
- `combo_rank_min__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.010
- `combo_min__first_bar_sentiment__bar_ret_0`: Y1:-0.009
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`: Y1:-0.006
- `combo_sig_product__opening_drive_thrust_ratio__max_down_ret`: Y1:-0.002
- `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment`: Y1:-0.001
- `combo_min__net_volume_flow__first_bar_return`: Y1:-0.001
- `combo_rank_min__max_up_ret__bar_ret_0`: Y1:-0.001
- `combo_rank_min__trend_bar_close_consistency__bar_ret_0`: Y1:-0.000
- `combo_mean__opening_drive_thrust_ratio__first_bar_return`: Y1:-0.000

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.1716 | N/A | +0.1716 | ∞ |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1654 | N/A | +0.1654 | ∞ |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1637 | N/A | +0.1637 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.1554 | N/A | +0.1554 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1495 | N/A | +0.1495 | ∞ |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1476 | N/A | +0.1476 | ∞ |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1425 | N/A | +0.1425 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1381 | N/A | +0.1381 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1358 | N/A | +0.1358 | ∞ |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1356 | N/A | +0.1356 | ∞ |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1348 | N/A | +0.1348 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1324 | N/A | +0.1324 | ∞ |
| `combo_mean__bar_body_rng_0__limit_down_proximity_early` | Median | persistent | +0.1312 | N/A | +0.1312 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1286 | N/A | +0.1286 | ∞ |
| `combo_diff__limit_down_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1236 | N/A | +0.1236 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1224 | N/A | +0.1224 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1209 | N/A | +0.1209 | ∞ |
| `combo_mean__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1186 | N/A | +0.1186 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1174 | N/A | +0.1174 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1174 | N/A | +0.1174 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1158 | N/A | +0.1158 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Median | persistent | +0.1154 | N/A | +0.1154 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1144 | N/A | +0.1144 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1093 | N/A | +0.1093 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1062 | N/A | +0.1062 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1013 | N/A | +0.1013 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1000 | N/A | +0.1000 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0980 | N/A | +0.0980 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.0961 | N/A | +0.0961 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0955 | N/A | +0.0955 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0944 | N/A | +0.0944 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0919 | N/A | +0.0919 | ∞ |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | Median | persistent | +0.0909 | N/A | +0.0909 | ∞ |
| `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Median | persistent | +0.0898 | N/A | +0.0898 | ∞ |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0896 | N/A | +0.0896 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0895 | N/A | +0.0895 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0866 | N/A | +0.0866 | ∞ |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Median | persistent | +0.0866 | N/A | +0.0866 | ∞ |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0852 | N/A | +0.0852 | ∞ |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.0850 | N/A | +0.0850 | ∞ |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0841 | N/A | +0.0841 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.0832 | N/A | +0.0832 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0827 | N/A | +0.0827 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0821 | N/A | +0.0821 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Median | persistent | +0.0809 | N/A | +0.0809 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0766 | N/A | +0.0766 | ∞ |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0762 | N/A | +0.0762 | ∞ |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Median | persistent | +0.0719 | N/A | +0.0719 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0712 | N/A | +0.0712 | ∞ |
| `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0673 | N/A | +0.0673 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0646 | N/A | +0.0646 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0641 | N/A | +0.0641 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0623 | N/A | +0.0623 | ∞ |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | Median | persistent | +0.0606 | N/A | +0.0606 | ∞ |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | Median | persistent | +0.0597 | N/A | +0.0597 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0593 | N/A | +0.0593 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0587 | N/A | +0.0587 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0586 | N/A | +0.0586 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0567 | N/A | +0.0567 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0545 | N/A | +0.0545 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0535 | N/A | +0.0535 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0503 | N/A | +0.0503 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0486 | N/A | +0.0486 | ∞ |
| `combo_clamp_diff__volume_weighted_price_position__late_bar_momentum` | Median | persistent | +0.0458 | N/A | +0.0458 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0431 | N/A | +0.0431 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Median | persistent | +0.0426 | N/A | +0.0426 | ∞ |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0307 | N/A | +0.0307 | ∞ |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0279 | N/A | +0.0279 | ∞ |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | Median | persistent | +0.0270 | N/A | +0.0270 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0262 | N/A | +0.0262 | ∞ |
| `first_bar_return` | TP | persistent | +0.0226 | N/A | +0.0226 | ∞ |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0212 | N/A | +0.0212 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | Median | persistent | +0.0199 | N/A | +0.0199 | ∞ |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Median | persistent | +0.0154 | N/A | +0.0154 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return` | Median | persistent | +0.0120 | N/A | +0.0120 | ∞ |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.0098 | N/A | +0.0098 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0069 | N/A | +0.0069 | ∞ |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Median | persistent | +0.0018 | N/A | +0.0018 | ∞ |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_mean__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0016 | N/A | -0.0016 | ∞ |
| `combo_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0026 | N/A | -0.0026 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0036 | N/A | -0.0036 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | FP | immediate | -0.0077 | N/A | -0.0077 | ∞ |
| `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` | FP | immediate | -0.0102 | N/A | -0.0102 | ∞ |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | FP | immediate | -0.0113 | N/A | -0.0113 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | FP | immediate | -0.0120 | N/A | -0.0120 | ∞ |
| `combo_max__first_bar_sentiment__first_bar_return` | FP | immediate | -0.0145 | N/A | -0.0145 | ∞ |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0148 | N/A | -0.0148 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0177 | N/A | -0.0177 | ∞ |
| `combo_min__bar_body_rng_0__impulse_bar_dominance` | FP | immediate | -0.0179 | N/A | -0.0179 | ∞ |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | FP | immediate | -0.0181 | N/A | -0.0181 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0192 | N/A | -0.0192 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | FP | immediate | -0.0221 | N/A | -0.0221 | ∞ |
| `combo_mean__max_up_ret__first_bar_return` | FP | immediate | -0.0225 | N/A | -0.0225 | ∞ |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | FP | immediate | -0.0230 | N/A | -0.0230 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0232 | N/A | -0.0232 | ∞ |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | FP | immediate | -0.0248 | N/A | -0.0248 | ∞ |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0256 | N/A | -0.0256 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | FP | immediate | -0.0265 | N/A | -0.0265 | ∞ |
| `combo_min__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0303 | N/A | -0.0303 | ∞ |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | FP | immediate | -0.0318 | N/A | -0.0318 | ∞ |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0325 | N/A | -0.0325 | ∞ |
| `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | FP | immediate | -0.0329 | N/A | -0.0329 | ∞ |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | FP | immediate | -0.0381 | N/A | -0.0381 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0421 | N/A | -0.0421 | ∞ |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | FP | immediate | -0.0445 | N/A | -0.0445 | ∞ |
| `opening_drive_thrust_ratio` | FP | immediate | -0.0464 | N/A | -0.0464 | ∞ |
| `combo_max__bar_ret_0__impulse_bar_dominance` | FP | immediate | -0.0491 | N/A | -0.0491 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0534 | N/A | -0.0534 | ∞ |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | FP | immediate | -0.0561 | N/A | -0.0561 | ∞ |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0563 | N/A | -0.0563 | ∞ |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0570 | N/A | -0.0570 | ∞ |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0572 | N/A | -0.0572 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0595 | N/A | -0.0595 | ∞ |
| `net_volume_flow` | FP | immediate | -0.0663 | N/A | -0.0663 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0689 | N/A | -0.0689 | ∞ |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0695 | N/A | -0.0695 | ∞ |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0737 | N/A | -0.0737 | ∞ |
| `shaved_bar_trend_conviction` | FP | immediate | -0.0741 | N/A | -0.0741 | ∞ |
| `max_up_ret` | FP | immediate | -0.0753 | N/A | -0.0753 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | FP | immediate | -0.0770 | N/A | -0.0770 | ∞ |
| `combo_max__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0771 | N/A | -0.0771 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0811 | N/A | -0.0811 | ∞ |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | FP | immediate | -0.0816 | N/A | -0.0816 | ∞ |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | FP | immediate | -0.0820 | N/A | -0.0820 | ∞ |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | FP | immediate | -0.0835 | N/A | -0.0835 | ∞ |
| `combo_mean__max_up_ret__impulse_bar_dominance` | FP | immediate | -0.0845 | N/A | -0.0845 | ∞ |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0854 | N/A | -0.0854 | ∞ |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0913 | N/A | -0.0913 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0930 | N/A | -0.0930 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | FP | immediate | -0.0939 | N/A | -0.0939 | ∞ |
| `combo_mean__impulse_bar_dominance__volatility_expansion_trend_vector` | FP | immediate | -0.1025 | N/A | -0.1025 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.1027 | N/A | -0.1027 | ∞ |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.1035 | N/A | -0.1035 | ∞ |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | FP | immediate | -0.1064 | N/A | -0.1064 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | FP | immediate | -0.1070 | N/A | -0.1070 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.1124 | N/A | -0.1124 | ∞ |
| `trend_bar_close_consistency` | FP | immediate | -0.1362 | N/A | -0.1362 | ∞ |

**Decay distribution**: immediate=62, fast(1-2y)=0, gradual=0, persistent=78

**FP decay trajectories:**

- `trend_bar_close_consistency`: Y1:-0.136
- `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.112
- `combo_sig_product__opening_drive_thrust_ratio__first_bar_return`: Y1:-0.107
- `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position`: Y1:-0.106
- `combo_max__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.104
- `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.103
- `combo_mean__impulse_bar_dominance__volatility_expansion_trend_vector`: Y1:-0.103
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Y1:-0.094
- `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.093
- `combo_rank_max__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.091
- `combo_rank_min__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.085
- `combo_mean__max_up_ret__impulse_bar_dominance`: Y1:-0.084
- `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Y1:-0.084
- `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector`: Y1:-0.082
- `combo_max__first_bar_return__volatility_expansion_trend_vector`: Y1:-0.082
- `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.081
- `combo_max__max_up_ret__bar_body_rng_0`: Y1:-0.077
- `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`: Y1:-0.077
- `max_up_ret`: Y1:-0.075
- `shaved_bar_trend_conviction`: Y1:-0.074
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:-0.074
- `combo_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.070
- `combo_min__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.069
- `net_volume_flow`: Y1:-0.066
- `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.060
- `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.057
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:-0.057
- `combo_rank_max__max_up_ret__bar_body_rng_0`: Y1:-0.056
- `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector`: Y1:-0.056
- `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`: Y1:-0.053
- `combo_max__bar_ret_0__impulse_bar_dominance`: Y1:-0.049
- `opening_drive_thrust_ratio`: Y1:-0.046
- `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`: Y1:-0.044
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`: Y1:-0.042
- `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`: Y1:-0.038
- `combo_min__first_bar_sentiment__volatility_expansion_trend_vector`: Y1:-0.033
- `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.033
- `combo_diff__max_up_ret__demark_setup_reversal_early`: Y1:-0.032
- `combo_min__max_up_ret__volume_weighted_price_position`: Y1:-0.030
- `combo_max__opening_drive_thrust_ratio__bar_ret_0`: Y1:-0.026
- `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.026
- `combo_max__bar_body_rng_0__impulse_bar_dominance`: Y1:-0.025
- `combo_max__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.023
- `combo_mean__bar_body_rng_0__impulse_bar_dominance`: Y1:-0.023
- `combo_mean__max_up_ret__first_bar_return`: Y1:-0.022
- `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Y1:-0.022
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.019
- `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`: Y1:-0.018
- `combo_min__bar_body_rng_0__impulse_bar_dominance`: Y1:-0.018
- `combo_rank_max__max_up_ret__first_bar_sentiment`: Y1:-0.018
- `combo_sig_product__max_up_ret__bar_body_rng_0`: Y1:-0.015
- `combo_max__first_bar_sentiment__first_bar_return`: Y1:-0.015
- `combo_sig_product__max_up_ret__bar_ret_0`: Y1:-0.012
- `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`: Y1:-0.011
- `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`: Y1:-0.010
- `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Y1:-0.008
- `combo_min__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.004
- `combo_min__max_up_ret__first_bar_sentiment`: Y1:-0.003
- `combo_min__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.002
- `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return`: Y1:-0.001
- `combo_mean__first_bar_return__volume_weighted_price_position`: Y1:-0.001
- `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector`: Y1:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.737±0.041 | 0.727±0.015 | 20% | USEFUL |
| ic_ir | 0.646±0.111 | 0.610±0.075 | 34% | USEFUL |
| p_value | 0.001±0.003 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.888±0.109 | 0.573±0.408 | 89% | USELESS |
| deflated_ic | 0.196±0.030 | 0.224±0.029 | 44% | USEFUL |
| overall_ic | 0.196±0.030 | 0.224±0.029 | 43% | USEFUL |
| raw_ic | 0.091±0.011 | 0.099±0.006 | 27% | USEFUL |

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.723±0.039 | 0.708±0.040 | 89% | USELESS |
| ic_ir | 0.594±0.098 | 0.582±0.127 | 92% | USELESS |
| p_value | 0.001±0.002 | 0.002±0.006 | 34% | USEFUL |
| max_corr | 0.890±0.081 | 0.874±0.059 | 45% | USEFUL |
| deflated_ic | 0.195±0.031 | 0.192±0.036 | 73% | WEAK |
| overall_ic | 0.196±0.031 | 0.193±0.036 | 73% | WEAK |
| raw_ic | 0.110±0.018 | 0.112±0.016 | 72% | WEAK |

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.746±0.042 | 0.771±0.068 | 74% | WEAK |
| ic_ir | 0.676±0.144 | 0.775±0.225 | 75% | WEAK |
| p_value | 0.001±0.003 | 0.000±0.001 | 12% | USEFUL |
| max_corr | 0.897±0.067 | 0.871±0.147 | 52% | WEAK |
| deflated_ic | 0.226±0.034 | 0.260±0.057 | 49% | USEFUL |
| overall_ic | 0.226±0.034 | 0.259±0.056 | 49% | USEFUL |
| raw_ic | 0.118±0.015 | 0.131±0.016 | 46% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**Temporal Validation Gate**: 2/20 top rejects are profitable (10%)

- `combo_sig_product__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.2020, Lock IC=+0.0146, Sharpe=+0.4344
- `combo_sig_product__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.2018, Lock IC=+0.0145, Sharpe=+0.4344

**B4 Correlation Gate**: 2/20 top rejects are profitable (10%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Sharpe=+0.4322
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Sharpe=+0.4322

### 500ETF — `single`

**7-Year Jackknife**: 10/20 top rejects are profitable (50%)

- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2184, Lock IC=+0.0565, Sharpe=+0.2974

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1769, Lock IC=+0.1949, Sharpe=+1.1683
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1796, Lock IC=+0.1227, Sharpe=+0.1858

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Sharpe=+0.1323
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Sharpe=+0.1323

**B6 Yearly IC CV Gate**: 5/10 top rejects are profitable (50%)

- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1487, Lock IC=+0.0208, Sharpe=+1.6556
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.1610, Lock IC=+0.0604, Sharpe=+0.3240
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.1610, Lock IC=+0.0604, Sharpe=+0.3240

**B6 Temporal Stability Gate**: 8/20 top rejects are profitable (40%)

- `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2431, Lock IC=+0.0860, Sharpe=+0.9409
- `combo_z_sum__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2431, Lock IC=+0.0860, Sharpe=+0.9409
- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2637, Lock IC=+0.0385, Sharpe=+0.8517

**B4 Correlation Gate**: 5/20 top rejects are profitable (25%)

- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2557, Lock IC=+0.0706, Sharpe=+0.8062
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2557, Lock IC=+0.0706, Sharpe=+0.8062
- `combo_tri_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`: Train IC=+0.2499, Lock IC=+0.0369, Sharpe=+0.4718

### 159915ETF — `single`

**7-Year Jackknife**: 5/20 top rejects are profitable (25%)

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2208, Lock IC=+0.1225, Sharpe=+1.4450
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2019, Lock IC=+0.0941, Sharpe=+0.6495
- `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2586, Lock IC=+0.0964, Sharpe=+0.3336

**B2 Rolling Guard**: 15/20 top rejects are profitable (75%)

- `combo_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1730, Lock IC=+0.1155, Sharpe=+1.0583
- `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.1722, Lock IC=+0.1037, Sharpe=+1.0583
- `combo_min__first_bar_sentiment__demark_setup_reversal_early`: Train IC=+0.2140, Lock IC=+0.0901, Sharpe=+0.9586

**Temporal Validation Gate**: 3/20 top rejects are profitable (15%)

- `combo_rank_min__demark_setup_reversal_early__late_bar_momentum`: Train IC=+0.1969, Lock IC=+0.1750, Sharpe=+0.7632
- `combo_abs_diff__limit_down_proximity_early__impulse_bar_dominance`: Train IC=+0.1863, Lock IC=+0.0582, Sharpe=+0.5871
- `combo_abs_diff__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.1863, Lock IC=+0.0582, Sharpe=+0.5871

**BH-FDR Gate**: 1/1 top rejects are profitable (100%)

- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Sharpe=+0.2891

**B3 Composite Floor**: 1/20 top rejects are profitable (5%)

- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`: Train IC=+0.1939, Lock IC=+0.0436, Sharpe=+0.3411

**B6 Temporal Stability Gate**: 11/20 top rejects are profitable (55%)

- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3177, Lock IC=+0.0619, Sharpe=+1.2230
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3527, Lock IC=+0.0637, Sharpe=+0.7890
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3082, Lock IC=+0.0585, Sharpe=+0.4764

**B4 Correlation Gate**: 16/20 top rejects are profitable (80%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3290, Lock IC=+0.0740, Sharpe=+2.5285
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3187, Lock IC=+0.1205, Sharpe=+2.3935
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.3095, Lock IC=+0.0868, Sharpe=+1.5647

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1022 | 78 | 54 | 12 | 12 | 69% | 15% |
| B2 Rolling Guard | 102 | 78 | 53 | 11 | 14 | 68% | 18% |
| Temporal Validation Gate | 83 | 78 | 51 | 6 | 21 | 65% | 27% |
| BH-FDR Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 7 | 7 | 4 | 3 | 0 | 57% | 0% |
| B6 Yearly IC CV Gate | 6 | 6 | 6 | 0 | 0 | 100% | 0% |
| B6 Quality Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 230 | 78 | 69 | 7 | 2 | 88% | 3% |

**Temporal Validation Gate** — top TP casualties:
- `ema12_dist`: Train IC=+0.0434, Lock IC=+0.1158, Sharpe=+3.3549
- `sma10_dist`: Train IC=+0.0453, Lock IC=+0.1136, Sharpe=+2.6363
- `sma20_dist`: Train IC=+0.0648, Lock IC=+0.1054, Sharpe=+2.5915

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1921 | 78 | 36 | 11 | 31 | 46% | 40% |
| B2 Rolling Guard | 256 | 78 | 60 | 6 | 12 | 77% | 15% |
| Temporal Validation Gate | 102 | 78 | 20 | 50 | 8 | 26% | 10% |
| B3 Composite Floor | 55 | 55 | 15 | 32 | 8 | 27% | 15% |
| B6 Yearly IC CV Gate | 10 | 10 | 3 | 2 | 5 | 30% | 50% |
| B6 Temporal Stability Gate | 172 | 78 | 51 | 6 | 21 | 65% | 27% |
| B4 Correlation Gate | 399 | 78 | 41 | 22 | 15 | 53% | 19% |

**7-Year Jackknife** — top TP casualties:
- `combo_max__early_late_momentum_divergence__first_bar_sentiment`: Train IC=+0.0000, Lock IC=+0.1884, Sharpe=+3.4503
- `combo_abs_diff__volume_weighted_momentum_acceleration__high_low_sequence_momentum`: Train IC=+0.0528, Lock IC=+0.1454, Sharpe=+2.9977
- `combo_abs_diff__volume_weighted_momentum_acceleration__rsi_opening`: Train IC=+0.0528, Lock IC=+0.1454, Sharpe=+2.9977

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1487, Lock IC=+0.0208, Sharpe=+1.6556
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.1610, Lock IC=+0.0604, Sharpe=+0.3240
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__max_up_ret__smooth_momentum_structure`: Train IC=+0.1610, Lock IC=+0.0604, Sharpe=+0.3240

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__high_low_sequence_momentum`: Train IC=+0.1799, Lock IC=+0.0778, Sharpe=+2.7693
- `combo_min__star50_limit_proximity_early__rsi_opening`: Train IC=+0.1799, Lock IC=+0.0778, Sharpe=+2.7693
- `combo_rank_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2119, Lock IC=+0.0910, Sharpe=+2.2390

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1079 | 78 | 41 | 24 | 13 | 53% | 17% |
| B2 Rolling Guard | 179 | 78 | 38 | 17 | 23 | 49% | 29% |
| Temporal Validation Gate | 51 | 51 | 31 | 12 | 8 | 61% | 16% |
| BH-FDR Gate | 1 | 1 | 0 | 0 | 1 | 0% | 100% |
| B3 Composite Floor | 65 | 65 | 16 | 42 | 7 | 25% | 11% |
| B6 Yearly IC CV Gate | 2 | 2 | 1 | 1 | 0 | 50% | 0% |
| B6 Temporal Stability Gate | 64 | 64 | 4 | 40 | 20 | 6% | 31% |
| B4 Correlation Gate | 306 | 78 | 14 | 22 | 42 | 18% | 54% |

**B2 Rolling Guard** — top TP casualties:
- `combo_rel_diff__limit_down_proximity_early__late_bar_momentum`: Train IC=+0.0936, Lock IC=+0.2260, Sharpe=+2.7295
- `combo_rel_diff__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.0936, Lock IC=+0.2260, Sharpe=+2.7295
- `yesterday_day_vwap_dev`: Train IC=+0.1158, Lock IC=+0.1282, Sharpe=+2.5172

**BH-FDR Gate** — top TP casualties:
- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Sharpe=+0.2891

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3177, Lock IC=+0.0619, Sharpe=+1.2230
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2573, Lock IC=+0.0958, Sharpe=+1.1483
- `combo_mean__star50_limit_proximity_early__bar_ret_0`: Train IC=+0.2820, Lock IC=+0.1124, Sharpe=+1.0660

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3290, Lock IC=+0.0740, Sharpe=+2.5285
- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3187, Lock IC=+0.1205, Sharpe=+2.3935
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.3014, Lock IC=+0.1495, Sharpe=+1.8753

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (83 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 64 | 50 | 37 | 13 | 0 | 74% | 26% |
| recency_ratio >= 2.5 (late-concentrated) | 9 | 9 | 8 | 0 | 1 | 89% | 0% |

### 500ETF — `single` (102 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 97 | 50 | 2 | 2 | 46 | 4% | 4% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 4 | 0 | 0 | 100% | 0% |

### 159915ETF — `single` (51 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 31 | 31 | 16 | 7 | 8 | 52% | 23% |
| recency_ratio >= 2.5 (late-concentrated) | 16 | 16 | 12 | 1 | 3 | 75% | 6% |

**Top TP killed by recency_ratio cap:**
- `volume_surge_direction`: Train IC=+0.1617, Lock IC=+0.1277, Sharpe=+2.7834

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+1.90). Threshold 0.498 → 97% accuracy.
- `n_negative_years`: FP is higher (d=+0.97). Threshold 0.000 → 96% accuracy.
- `n_negative_regimes`: FP is lower (d=-0.94). Threshold 0.000 → 96% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-0.79). Threshold 0.025 → 96% accuracy.
- `half_ratio`: FP is higher (d=+0.50). Threshold 0.454 → 96% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/90
- Decaying signal (half ratio < 0.3): 0/90
- Weak component (CV > 2.0): 1/90
- Regime-dependent (≥2 negative regimes): 0/90

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `half_ratio`: FP is higher (d=+0.61). Threshold 0.578 → 74% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/59
- Decaying signal (half ratio < 0.3): 0/59
- Weak component (CV > 2.0): 0/59
- Regime-dependent (≥2 negative regimes): 0/59

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `recency_ratio`: FP is higher (d=+0.88). Threshold 0.779 → 72% accuracy.
- `half_ratio`: FP is higher (d=+0.86). Threshold 0.854 → 71% accuracy.
- `ic_cv`: FP is higher (d=+0.66). Threshold 0.286 → 66% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/62
- Decaying signal (half ratio < 0.3): 0/62
- Weak component (CV > 2.0): 0/62
- Regime-dependent (≥2 negative regimes): 0/62

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `early_body_momentum` | 4 | 0 | 4 | 100% |  |
| `volume_surge_direction` | 20 | 0 | 20 | 100% | ⚠ TOXIC |
| `max_up_ret` | 69 | 5 | 74 | 93% | ⚠ TOXIC |
| `volatility_expansion_trend_vector` | 27 | 3 | 30 | 90% | ⚠ TOXIC |
| `first_bar_return` | 35 | 5 | 40 | 88% | ⚠ TOXIC |
| `volume_weighted_price_position` | 40 | 6 | 46 | 87% | ⚠ TOXIC |
| `body_size_progression` | 5 | 1 | 6 | 83% | ⚠ TOXIC |
| `impulse_bar_dominance` | 10 | 2 | 12 | 83% | ⚠ TOXIC |
| `net_volume_flow` | 10 | 2 | 12 | 83% | ⚠ TOXIC |
| `bar_ret_0` | 24 | 5 | 29 | 83% | ⚠ TOXIC |
| `opening_drive_thrust_ratio` | 71 | 17 | 88 | 81% | ⚠ TOXIC |
| `trend_bar_close_consistency` | 7 | 2 | 9 | 78% |  |
| `first_bar_sentiment` | 23 | 9 | 32 | 72% |  |
| `bar_body_rng_0` | 37 | 18 | 55 | 67% |  |
| `smooth_momentum_structure` | 2 | 1 | 3 | 67% |  |
| `close_vs_open_range` | 6 | 3 | 9 | 67% |  |
| `max_down_ret` | 7 | 5 | 12 | 58% |  |
| `double_bottom_bull_flag_early` | 1 | 1 | 2 | 50% |  |
| `demark_setup_reversal_early` | 2 | 2 | 4 | 50% |  |
| `rbreaker_sell_setup_proximity_early` | 15 | 26 | 41 | 37% |  |
| `rbreaker_buy_setup_proximity_early` | 2 | 5 | 7 | 29% |  |
| `volume_weighted_momentum_acceleration` | 1 | 4 | 5 | 20% |  |
| `limit_down_proximity_early` | 2 | 8 | 10 | 20% |  |
| `star50_limit_proximity_early` | 4 | 29 | 33 | 12% |  |
| `yesterday_first_30min_return` | 0 | 4 | 4 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=107, TP=46, FP rate=70%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=7, TP=5, FP rate=58%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=45, TP=18, FP rate=71%

