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
| 300ETF | single | 44 | 18 | `[10, 5, 4, 3, 2, 2, 2, 2, 2, 2, 2, 1, ... (18 clusters)]` | 0.2308 | 38 | 3 | 3 | 86% | 0.10 |
| 500ETF | single | 56 | 31 | `[4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (31 clusters)]` | 0.2358 | 24 | 16 | 16 | 43% | 0.43 |
| 159915ETF | single | 146 | 62 | `[9, 7, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, ... (62 clusters)]` | 0.3111 | 56 | 28 | 62 | 38% | 0.52 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=38, TP=3)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.650 | 0.524 | 0.641 | 0.497 | +1.53 | 0.498 | 93% |
| n_negative_regimes | 0.000 | 0.333 | 0.000 | 0.000 | -1.00 | 0.000 | 90% |
| recency_ratio | 0.512 | 0.418 | 0.440 | 0.436 | +0.68 | 0.282 | 90% |
| half_ratio | 0.824 | 0.723 | 0.817 | 0.737 | +0.65 | 0.578 | 90% |
| n_negative_years | 0.184 | 0.000 | 0.000 | 0.000 | +0.58 | 0.000 | 90% |
| ic_std_across_regimes | 0.051 | 0.057 | 0.050 | 0.055 | -0.55 | 0.025 | 90% |
| weak_link_cv | 0.816 | 0.843 | 0.731 | 0.899 | -0.21 | 0.612 | 90% |

### 500ETF — `single` (FP=24, TP=16)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 1.006 | 0.665 | 0.913 | 0.633 | +1.39 | 0.696 | 90% |
| ic_std_across_regimes | 0.039 | 0.054 | 0.040 | 0.056 | -1.34 | 0.018 | 57% |
| ic_cv | 0.308 | 0.361 | 0.291 | 0.355 | -0.87 | 0.221 | 57% |
| recency_ratio | 0.887 | 0.699 | 0.835 | 0.650 | +0.80 | 0.681 | 80% |
| n_negative_regimes | 0.000 | 0.062 | 0.000 | 0.000 | -0.37 | 0.000 | 57% |
| weak_link_cv | 0.433 | 0.447 | 0.482 | 0.482 | -0.18 | 0.334 | 59% |
| n_negative_years | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 57% |

### 159915ETF — `single` (FP=56, TP=62)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 1.084 | 0.832 | 1.026 | 0.821 | +1.07 | 0.858 | 72% |
| recency_ratio | 1.079 | 0.738 | 1.035 | 0.712 | +1.05 | 0.856 | 76% |
| ic_std_across_regimes | 0.024 | 0.026 | 0.022 | 0.026 | -0.22 | 0.040 | 53% |
| ic_cv | 0.397 | 0.380 | 0.369 | 0.358 | +0.20 | 0.494 | 58% |
| weak_link_cv | 0.595 | 0.598 | 0.581 | 0.570 | -0.02 | 0.575 | 57% |
| n_negative_years | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 52% |
| n_negative_regimes | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 52% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_max__bar_ret_0__morning_volume_weighted_momentum`** (Lock IC=-0.1961, Sharpe=-3.7281)
- Admission: Train IC=+0.2037, Deflated=+0.2023, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.046 | 2017: -0.042 | 2018: +0.142 | 2019: +0.030 | 2020: +0.033 | 2021: +0.146 | 2022: +0.036 | 2023: +0.148 | 2024: +0.065 | 2025: +0.102 | 2026: -0.196
- Yearly Tail ICs:   2015: +0.185 | 2016: -0.040 | 2017: -0.032 | 2018: +0.250 | 2019: +0.158 | 2020: +0.190 | 2021: +0.266 | 2022: +0.191 | 2023: +0.291 | 2024: +0.274 | 2025: +0.140 | 2026: -0.444
- IC CV=0.56, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.97
- Early IC=+0.0864, Recent IC=+0.0835, 1st-half IC=+0.0901, 2nd-half IC=+0.0893, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.082, Q3_mid=+0.065, Q4=+0.085, Q5_high_vol=+0.148

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.2114, Sharpe=-3.6368)
- Admission: Train IC=+0.2303, Deflated=+0.2293, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.037 | 2017: +0.038 | 2018: +0.152 | 2019: +0.040 | 2020: +0.012 | 2021: +0.187 | 2022: +0.042 | 2023: +0.199 | 2024: +0.041 | 2025: +0.106 | 2026: -0.211
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.154 | 2017: +0.194 | 2018: +0.448 | 2019: +0.247 | 2020: +0.184 | 2021: +0.335 | 2022: +0.239 | 2023: +0.190 | 2024: +0.133 | 2025: +0.140 | 2026: -0.419
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.0956, Recent IC=+0.0731, 1st-half IC=+0.0933, 2nd-half IC=+0.0951, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.094, Q3_mid=+0.055, Q4=+0.060, Q5_high_vol=+0.177

**`combo_rank_max__first_bar_return__morning_volume_weighted_momentum`** (Lock IC=-0.1934, Sharpe=-3.6188)
- Admission: Train IC=+0.1982, Deflated=+0.1969, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.047 | 2017: -0.046 | 2018: +0.143 | 2019: +0.031 | 2020: +0.032 | 2021: +0.147 | 2022: +0.030 | 2023: +0.148 | 2024: +0.065 | 2025: +0.100 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.212 | 2016: -0.034 | 2017: -0.056 | 2018: +0.332 | 2019: +0.176 | 2020: +0.094 | 2021: +0.329 | 2022: +0.149 | 2023: +0.302 | 2024: +0.229 | 2025: +0.136 | 2026: -0.460
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.94
- Early IC=+0.0888, Recent IC=+0.0833, 1st-half IC=+0.0913, 2nd-half IC=+0.0881, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.084, Q3_mid=+0.064, Q4=+0.084, Q5_high_vol=+0.144

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=-0.1637, Sharpe=-2.8975)
- Admission: Train IC=+0.2166, Deflated=+0.2163, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.083 | 2017: -0.017 | 2018: +0.154 | 2019: +0.062 | 2020: +0.049 | 2021: +0.179 | 2022: +0.032 | 2023: +0.199 | 2024: +0.038 | 2025: +0.089 | 2026: -0.164
- Yearly Tail ICs:   2015: +0.051 | 2016: +0.079 | 2017: -0.047 | 2018: +0.287 | 2019: +0.233 | 2020: +0.167 | 2021: +0.342 | 2022: +0.236 | 2023: +0.312 | 2024: +0.157 | 2025: +0.149 | 2026: -0.404
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.59
- Early IC=+0.1081, Recent IC=+0.0636, 1st-half IC=+0.1085, 2nd-half IC=+0.0912, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.088, Q3_mid=+0.064, Q4=+0.088, Q5_high_vol=+0.200

**`combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1994, Sharpe=-2.8678)
- Admission: Train IC=+0.2195, Deflated=+0.2191, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.061 | 2017: -0.007 | 2018: +0.167 | 2019: +0.067 | 2020: +0.015 | 2021: +0.184 | 2022: +0.056 | 2023: +0.198 | 2024: +0.010 | 2025: +0.097 | 2026: -0.199
- Yearly Tail ICs:   2015: +0.152 | 2016: -0.060 | 2017: +0.143 | 2018: +0.445 | 2019: +0.199 | 2020: +0.182 | 2021: +0.385 | 2022: +0.184 | 2023: +0.151 | 2024: +0.121 | 2025: +0.237 | 2026: -0.384
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.46
- Early IC=+0.1166, Recent IC=+0.0533, 1st-half IC=+0.1058, 2nd-half IC=+0.0916, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.100, Q3_mid=+0.050, Q4=+0.090, Q5_high_vol=+0.181

**`combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1697, Sharpe=-2.7982)
- Admission: Train IC=+0.2286, Deflated=+0.2282, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.069 | 2017: +0.029 | 2018: +0.195 | 2019: +0.064 | 2020: +0.003 | 2021: +0.165 | 2022: +0.050 | 2023: +0.178 | 2024: +0.047 | 2025: +0.095 | 2026: -0.170
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.069 | 2017: +0.104 | 2018: +0.369 | 2019: +0.145 | 2020: +0.144 | 2021: +0.412 | 2022: +0.278 | 2023: +0.261 | 2024: +0.215 | 2025: +0.048 | 2026: -0.146
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.55
- Early IC=+0.1296, Recent IC=+0.0711, 1st-half IC=+0.1036, 2nd-half IC=+0.0963, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.102, Q3_mid=+0.048, Q4=+0.085, Q5_high_vol=+0.185

**`combo_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1087, Sharpe=-2.7122)
- Admission: Train IC=+0.2138, Deflated=+0.2139, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.115 | 2017: +0.115 | 2018: +0.285 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.249 | 2024: +0.186 | 2025: +0.049 | 2026: -0.298
- IC CV=0.70, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.28
- Early IC=+0.1447, Recent IC=+0.0402, 1st-half IC=+0.1084, 2nd-half IC=+0.0644, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.093, Q3_mid=+0.045, Q4=+0.083, Q5_high_vol=+0.153

**`combo_mean__max_up_ret__morning_volume_weighted_momentum`** (Lock IC=-0.1658, Sharpe=-2.6771)
- Admission: Train IC=+0.2059, Deflated=+0.2050, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.042 | 2017: -0.067 | 2018: +0.099 | 2019: +0.033 | 2020: +0.034 | 2021: +0.172 | 2022: +0.025 | 2023: +0.139 | 2024: +0.082 | 2025: +0.063 | 2026: -0.166
- Yearly Tail ICs:   2015: -0.029 | 2016: +0.114 | 2017: +0.031 | 2018: +0.247 | 2019: +0.155 | 2020: -0.013 | 2021: +0.366 | 2022: +0.216 | 2023: +0.285 | 2024: +0.243 | 2025: +0.227 | 2026: -0.330
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.99, Recency ratio=1.10
- Early IC=+0.0659, Recent IC=+0.0725, 1st-half IC=+0.0837, 2nd-half IC=+0.0829, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.044, Q2=+0.041, Q3_mid=+0.049, Q4=+0.093, Q5_high_vol=+0.159

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.1476, Sharpe=-2.5718)
- Admission: Train IC=+0.2146, Deflated=+0.2147, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.046 | 2018: +0.125 | 2019: +0.050 | 2020: +0.040 | 2021: +0.174 | 2022: +0.018 | 2023: +0.171 | 2024: +0.046 | 2025: +0.077 | 2026: -0.148
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.068 | 2017: -0.092 | 2018: +0.289 | 2019: +0.241 | 2020: +0.096 | 2021: +0.371 | 2022: +0.246 | 2023: +0.229 | 2024: +0.159 | 2025: +0.084 | 2026: -0.332
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.69
- Early IC=+0.0875, Recent IC=+0.0605, 1st-half IC=+0.0904, 2nd-half IC=+0.0853, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.066, Q3_mid=+0.042, Q4=+0.076, Q5_high_vol=+0.197

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.1297, Sharpe=-2.5287)
- Admission: Train IC=+0.2011, Deflated=+0.2011, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.045 | 2016: +0.023 | 2017: +0.049 | 2018: +0.170 | 2019: +0.093 | 2020: +0.055 | 2021: +0.156 | 2022: +0.032 | 2023: +0.138 | 2024: +0.028 | 2025: +0.047 | 2026: -0.130
- Yearly Tail ICs:   2015: -0.123 | 2016: +0.038 | 2017: +0.026 | 2018: +0.361 | 2019: +0.227 | 2020: +0.092 | 2021: +0.383 | 2022: +0.260 | 2023: +0.301 | 2024: +0.080 | 2025: +0.077 | 2026: -0.315
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.29
- Early IC=+0.1312, Recent IC=+0.0376, 1st-half IC=+0.1122, 2nd-half IC=+0.0661, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.061, Q3_mid=+0.057, Q4=+0.061, Q5_high_vol=+0.200

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=-0.1526, Sharpe=-2.5270)
- Admission: Train IC=+0.1705, Deflated=+0.1703, IR=0.54, Mono=0.69, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.107 | 2017: -0.014 | 2018: +0.192 | 2019: +0.061 | 2020: +0.033 | 2021: +0.161 | 2022: +0.012 | 2023: +0.143 | 2024: +0.062 | 2025: +0.064 | 2026: -0.153
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.181 | 2017: -0.108 | 2018: +0.160 | 2019: +0.188 | 2020: +0.033 | 2021: +0.303 | 2022: +0.172 | 2023: +0.339 | 2024: +0.200 | 2025: +0.013 | 2026: -0.244
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.50
- Early IC=+0.1263, Recent IC=+0.0627, 1st-half IC=+0.1066, 2nd-half IC=+0.0763, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.072, Q3_mid=+0.043, Q4=+0.085, Q5_high_vol=+0.200

**`combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.1502, Sharpe=-2.3921)
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
- Admission: Train IC=+0.1979, Deflated=+0.1979, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.112 | 2017: +0.050 | 2018: +0.194 | 2019: +0.090 | 2020: -0.007 | 2021: +0.146 | 2022: +0.043 | 2023: +0.154 | 2024: +0.036 | 2025: +0.076 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.072 | 2017: +0.038 | 2018: +0.334 | 2019: +0.170 | 2020: +0.024 | 2021: +0.343 | 2022: +0.299 | 2023: +0.322 | 2024: +0.032 | 2025: +0.142 | 2026: -0.377
- IC CV=0.70, Neg years (linear/tail)=1/1 of 8, Half ratio=0.72, Recency ratio=0.39
- Early IC=+0.1436, Recent IC=+0.0555, 1st-half IC=+0.1090, 2nd-half IC=+0.0785, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.099, Q3_mid=+0.040, Q4=+0.101, Q5_high_vol=+0.165

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=-0.1613, Sharpe=-2.3451)
- Admission: Train IC=+0.2145, Deflated=+0.2135, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.074 | 2017: +0.051 | 2018: +0.174 | 2019: +0.059 | 2020: +0.029 | 2021: +0.172 | 2022: +0.011 | 2023: +0.160 | 2024: +0.060 | 2025: +0.077 | 2026: -0.161
- Yearly Tail ICs:   2015: +0.075 | 2016: +0.099 | 2017: +0.044 | 2018: +0.335 | 2019: +0.231 | 2020: +0.128 | 2021: +0.388 | 2022: +0.256 | 2023: +0.312 | 2024: +0.123 | 2025: +0.037 | 2026: -0.323
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.59
- Early IC=+0.1167, Recent IC=+0.0686, 1st-half IC=+0.1054, 2nd-half IC=+0.0758, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.078, Q3_mid=+0.046, Q4=+0.075, Q5_high_vol=+0.185

**`combo_mean__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.1215, Sharpe=-2.1883)
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

**`combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0581, Sharpe=-2.1391)
- Admission: Train IC=+0.2165, Deflated=+0.2165, IR=0.62, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.113 | 2017: -0.035 | 2018: +0.203 | 2019: +0.134 | 2020: +0.016 | 2021: +0.151 | 2022: +0.067 | 2023: +0.175 | 2024: +0.047 | 2025: +0.073 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.185 | 2017: -0.112 | 2018: +0.245 | 2019: +0.241 | 2020: +0.067 | 2021: +0.399 | 2022: +0.327 | 2023: +0.211 | 2024: +0.154 | 2025: +0.220 | 2026: -0.028
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.35
- Early IC=+0.1687, Recent IC=+0.0598, 1st-half IC=+0.1241, 2nd-half IC=+0.1002, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.108, Q3_mid=+0.060, Q4=+0.083, Q5_high_vol=+0.239

**`combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0`** (Lock IC=-0.1364, Sharpe=-2.1155)
- Admission: Train IC=+0.2060, Deflated=+0.2059, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.097 | 2017: +0.016 | 2018: +0.194 | 2019: +0.082 | 2020: +0.050 | 2021: +0.181 | 2022: +0.028 | 2023: +0.187 | 2024: +0.037 | 2025: +0.084 | 2026: -0.136
- Yearly Tail ICs:   2015: +0.179 | 2016: -0.031 | 2017: -0.043 | 2018: +0.350 | 2019: +0.159 | 2020: +0.213 | 2021: +0.359 | 2022: +0.200 | 2023: +0.253 | 2024: +0.117 | 2025: +0.209 | 2026: -0.326
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.44
- Early IC=+0.1380, Recent IC=+0.0606, 1st-half IC=+0.1228, 2nd-half IC=+0.0901, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.102, Q3_mid=+0.060, Q4=+0.100, Q5_high_vol=+0.208

**`combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.1298, Sharpe=-1.8873)
- Admission: Train IC=+0.1817, Deflated=+0.1814, IR=0.67, Mono=0.73, p=0.0004, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.052 | 2017: +0.016 | 2018: +0.112 | 2019: +0.045 | 2020: -0.069 | 2021: +0.149 | 2022: +0.070 | 2023: +0.198 | 2024: +0.055 | 2025: +0.063 | 2026: -0.130
- Yearly Tail ICs:   2015: -0.055 | 2016: +0.053 | 2017: -0.053 | 2018: +0.273 | 2019: +0.139 | 2020: -0.034 | 2021: +0.371 | 2022: +0.309 | 2023: +0.456 | 2024: +0.038 | 2025: +0.206 | 2026: +0.025
- IC CV=0.96, Neg years (linear/tail)=1/1 of 8, Half ratio=1.87, Recency ratio=0.75
- Early IC=+0.0782, Recent IC=+0.0587, 1st-half IC=+0.0551, 2nd-half IC=+0.1031, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.078, Q3_mid=+0.016, Q4=+0.102, Q5_high_vol=+0.077

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`** (Lock IC=-0.1072, Sharpe=-1.6552)
- Admission: Train IC=+0.2000, Deflated=+0.1999, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.106 | 2016: +0.044 | 2017: -0.057 | 2018: +0.172 | 2019: +0.086 | 2020: +0.058 | 2021: +0.143 | 2022: +0.035 | 2023: +0.164 | 2024: +0.057 | 2025: +0.100 | 2026: -0.107
- Yearly Tail ICs:   2015: -0.089 | 2016: +0.098 | 2017: +0.024 | 2018: +0.311 | 2019: +0.240 | 2020: +0.198 | 2021: +0.274 | 2022: +0.178 | 2023: +0.237 | 2024: +0.217 | 2025: +0.073 | 2026: -0.250
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.61
- Early IC=+0.1286, Recent IC=+0.0786, 1st-half IC=+0.1101, 2nd-half IC=+0.0943, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.90, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.084, Q3_mid=+0.048, Q4=+0.079, Q5_high_vol=+0.224

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1740, Sharpe=-1.4177)
- Admission: Train IC=+0.2218, Deflated=+0.2214, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.069 | 2017: -0.012 | 2018: +0.183 | 2019: +0.067 | 2020: +0.023 | 2021: +0.179 | 2022: +0.039 | 2023: +0.184 | 2024: +0.033 | 2025: +0.095 | 2026: -0.174
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.199 | 2017: +0.142 | 2018: +0.356 | 2019: +0.239 | 2020: +0.053 | 2021: +0.390 | 2022: +0.323 | 2023: +0.308 | 2024: +0.097 | 2025: +0.074 | 2026: +0.003
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.51
- Early IC=+0.1249, Recent IC=+0.0636, 1st-half IC=+0.1086, 2nd-half IC=+0.0921, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.087, Q3_mid=+0.053, Q4=+0.089, Q5_high_vol=+0.195

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=-0.1611, Sharpe=-1.2733)
- Admission: Train IC=+0.2301, Deflated=+0.2290, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.087 | 2017: +0.035 | 2018: +0.169 | 2019: +0.060 | 2020: +0.041 | 2021: +0.170 | 2022: +0.015 | 2023: +0.166 | 2024: +0.060 | 2025: +0.078 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.033 | 2017: +0.026 | 2018: +0.412 | 2019: +0.206 | 2020: +0.193 | 2021: +0.360 | 2022: +0.306 | 2023: +0.290 | 2024: +0.141 | 2025: +0.095 | 2026: -0.308
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.60
- Early IC=+0.1152, Recent IC=+0.0689, 1st-half IC=+0.1068, 2nd-half IC=+0.0797, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.078, Q3_mid=+0.047, Q4=+0.080, Q5_high_vol=+0.189

**`combo_min__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0924, Sharpe=-1.1726)
- Admission: Train IC=+0.2257, Deflated=+0.2261, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.078 | 2016: +0.097 | 2017: -0.003 | 2018: +0.220 | 2019: +0.081 | 2020: +0.007 | 2021: +0.167 | 2022: +0.037 | 2023: +0.147 | 2024: +0.040 | 2025: +0.070 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.025 | 2016: +0.162 | 2017: -0.113 | 2018: +0.302 | 2019: +0.258 | 2020: +0.094 | 2021: +0.487 | 2022: +0.106 | 2023: +0.198 | 2024: +0.054 | 2025: +0.113 | 2026: -0.070
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.36
- Early IC=+0.1505, Recent IC=+0.0548, 1st-half IC=+0.1191, 2nd-half IC=+0.0823, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.089, Q3_mid=+0.068, Q4=+0.089, Q5_high_vol=+0.207

**`combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0631, Sharpe=-1.1652)
- Admission: Train IC=+0.2144, Deflated=+0.2143, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.065 | 2017: +0.033 | 2018: +0.209 | 2019: +0.075 | 2020: -0.029 | 2021: +0.132 | 2022: +0.060 | 2023: +0.171 | 2024: +0.026 | 2025: +0.092 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.197 | 2016: -0.103 | 2017: +0.117 | 2018: +0.139 | 2019: +0.188 | 2020: +0.008 | 2021: +0.349 | 2022: +0.394 | 2023: +0.318 | 2024: +0.158 | 2025: +0.068 | 2026: -0.177
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.91, Recency ratio=0.42
- Early IC=+0.1417, Recent IC=+0.0590, 1st-half IC=+0.0993, 2nd-half IC=+0.0904, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.144, Q3_mid=+0.036, Q4=+0.099, Q5_high_vol=+0.137

**`combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum`** (Lock IC=-0.0775, Sharpe=-1.0627)
- Admission: Train IC=+0.2124, Deflated=+0.2122, IR=0.60, Mono=0.70, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.049 | 2016: +0.050 | 2017: +0.003 | 2018: +0.124 | 2019: +0.065 | 2020: +0.000 | 2021: +0.165 | 2022: +0.056 | 2023: +0.144 | 2024: +0.051 | 2025: +0.061 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.014 | 2017: -0.041 | 2018: +0.259 | 2019: +0.057 | 2020: -0.010 | 2021: +0.388 | 2022: +0.142 | 2023: +0.297 | 2024: +0.183 | 2025: +0.324 | 2026: -0.068
- IC CV=0.60, Neg years (linear/tail)=0/1 of 8, Half ratio=0.97, Recency ratio=0.58
- Early IC=+0.0952, Recent IC=+0.0552, 1st-half IC=+0.0905, 2nd-half IC=+0.0879, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.067, Q3_mid=+0.043, Q4=+0.115, Q5_high_vol=+0.145

**`combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0691, Sharpe=-0.9513)
- Admission: Train IC=+0.2251, Deflated=+0.2262, IR=0.74, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.084 | 2017: +0.015 | 2018: +0.179 | 2019: +0.078 | 2020: +0.010 | 2021: +0.121 | 2022: +0.037 | 2023: +0.161 | 2024: +0.056 | 2025: +0.024 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.221 | 2016: -0.002 | 2017: +0.076 | 2018: +0.189 | 2019: +0.199 | 2020: +0.158 | 2021: +0.339 | 2022: +0.258 | 2023: +0.297 | 2024: +0.315 | 2025: +0.053 | 2026: -0.003
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.31
- Early IC=+0.1282, Recent IC=+0.0400, 1st-half IC=+0.0993, 2nd-half IC=+0.0716, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.077, Q3_mid=+0.046, Q4=+0.073, Q5_high_vol=+0.175

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0294, Sharpe=-0.6275)
- Admission: Train IC=+0.2621, Deflated=+0.2635, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.88
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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=-0.0712, Sharpe=-0.5845)
- Admission: Train IC=+0.2454, Deflated=+0.2463, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.054 | 2017: -0.048 | 2018: +0.208 | 2019: +0.130 | 2020: +0.058 | 2021: +0.154 | 2022: +0.046 | 2023: +0.131 | 2024: +0.030 | 2025: +0.082 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.380 | 2016: -0.045 | 2017: -0.018 | 2018: +0.279 | 2019: +0.291 | 2020: +0.218 | 2021: +0.418 | 2022: +0.321 | 2023: +0.104 | 2024: +0.253 | 2025: +0.050 | 2026: +0.239
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.33
- Early IC=+0.1690, Recent IC=+0.0564, 1st-half IC=+0.1366, 2nd-half IC=+0.0803, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.070, Q3_mid=+0.091, Q4=+0.105, Q5_high_vol=+0.214

**`combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0955, Sharpe=-0.5706)
- Admission: Train IC=+0.2233, Deflated=+0.2238, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.099 | 2017: -0.006 | 2018: +0.210 | 2019: +0.081 | 2020: +0.002 | 2021: +0.127 | 2022: +0.062 | 2023: +0.164 | 2024: +0.030 | 2025: +0.084 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.064 | 2016: -0.115 | 2017: +0.133 | 2018: +0.160 | 2019: +0.213 | 2020: +0.100 | 2021: +0.327 | 2022: +0.362 | 2023: +0.368 | 2024: +0.190 | 2025: +0.034 | 2026: -0.118
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.39
- Early IC=+0.1455, Recent IC=+0.0571, 1st-half IC=+0.1051, 2nd-half IC=+0.0869, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.130, Q3_mid=+0.043, Q4=+0.095, Q5_high_vol=+0.154

**`combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0308, Sharpe=-0.1479)
- Admission: Train IC=+0.2192, Deflated=+0.2193, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.110 | 2017: -0.022 | 2018: +0.226 | 2019: +0.105 | 2020: +0.052 | 2021: +0.162 | 2022: +0.066 | 2023: +0.125 | 2024: +0.029 | 2025: +0.073 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.146 | 2017: -0.090 | 2018: +0.391 | 2019: +0.279 | 2020: +0.113 | 2021: +0.379 | 2022: +0.198 | 2023: +0.155 | 2024: +0.152 | 2025: +0.237 | 2026: +0.104
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.31
- Early IC=+0.1654, Recent IC=+0.0513, 1st-half IC=+0.1346, 2nd-half IC=+0.0838, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.084, Q3_mid=+0.049, Q4=+0.096, Q5_high_vol=+0.243

**`combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`** (Lock IC=-0.0161, Sharpe=+0.0760)
- Admission: Train IC=+0.1909, Deflated=+0.1902, IR=0.57, Mono=0.73, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.027 | 2017: -0.063 | 2018: +0.066 | 2019: +0.066 | 2020: +0.049 | 2021: +0.198 | 2022: +0.081 | 2023: +0.113 | 2024: +0.004 | 2025: +0.079 | 2026: -0.026
- Yearly Tail ICs:   2015: +0.160 | 2016: +0.090 | 2017: -0.050 | 2018: +0.221 | 2019: +0.147 | 2020: +0.052 | 2021: +0.290 | 2022: +0.220 | 2023: +0.191 | 2024: +0.177 | 2025: +0.270 | 2026: +0.101
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.66
- Early IC=+0.0652, Recent IC=+0.0428, 1st-half IC=+0.0938, 2nd-half IC=+0.0781, Neg regimes=0/5
- Weak component: `morning_volume_weighted_momentum` (CV=0.61, neg years=0)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.057, Q3_mid=+0.085, Q4=+0.080, Q5_high_vol=+0.162

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early`** (Lock IC=-0.0701, Sharpe=+0.0945)
- Admission: Train IC=+0.2207, Deflated=+0.2206, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.089 | 2017: -0.059 | 2018: +0.195 | 2019: +0.086 | 2020: +0.068 | 2021: +0.165 | 2022: +0.062 | 2023: +0.127 | 2024: +0.044 | 2025: +0.068 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.135 | 2017: +0.065 | 2018: +0.428 | 2019: +0.262 | 2020: +0.122 | 2021: +0.251 | 2022: +0.208 | 2023: +0.118 | 2024: +0.190 | 2025: +0.207 | 2026: +0.121
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.40
- Early IC=+0.1403, Recent IC=+0.0563, 1st-half IC=+0.1271, 2nd-half IC=+0.0838, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.90, neg years=2)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.061, Q3_mid=+0.056, Q4=+0.091, Q5_high_vol=+0.255

**`combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`** (Lock IC=-0.0509, Sharpe=+0.5175)
- Admission: Train IC=+0.1962, Deflated=+0.1952, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.078 | 2017: -0.099 | 2018: +0.121 | 2019: +0.056 | 2020: +0.060 | 2021: +0.175 | 2022: +0.099 | 2023: +0.077 | 2024: +0.018 | 2025: +0.058 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.100 | 2016: +0.092 | 2017: -0.138 | 2018: +0.356 | 2019: +0.120 | 2020: +0.112 | 2021: +0.214 | 2022: +0.238 | 2023: +0.084 | 2024: +0.279 | 2025: +0.289 | 2026: +0.125
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.42
- Early IC=+0.0889, Recent IC=+0.0377, 1st-half IC=+0.1048, 2nd-half IC=+0.0744, Neg regimes=0/5
- Weak component: `morning_volume_weighted_momentum` (CV=0.61, neg years=0)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.040, Q3_mid=+0.043, Q4=+0.091, Q5_high_vol=+0.197

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0293, Sharpe=+0.7925)
- Admission: Train IC=+0.1943, Deflated=+0.1946, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.096 | 2017: -0.072 | 2018: +0.144 | 2019: +0.091 | 2020: +0.062 | 2021: +0.138 | 2022: +0.048 | 2023: +0.132 | 2024: +0.044 | 2025: +0.060 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.312 | 2016: -0.044 | 2017: -0.042 | 2018: +0.223 | 2019: +0.226 | 2020: +0.119 | 2021: +0.429 | 2022: +0.245 | 2023: +0.115 | 2024: +0.334 | 2025: +0.057 | 2026: +0.045
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.44
- Early IC=+0.1173, Recent IC=+0.0519, 1st-half IC=+0.1061, 2nd-half IC=+0.0746, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.067, Q3_mid=+0.070, Q4=+0.036, Q5_high_vol=+0.221

**`combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`** (Lock IC=-0.0317, Sharpe=+0.8606)
- Admission: Train IC=+0.2063, Deflated=+0.2057, IR=0.61, Mono=0.76, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.030 | 2017: -0.059 | 2018: +0.074 | 2019: +0.068 | 2020: +0.047 | 2021: +0.199 | 2022: +0.085 | 2023: +0.111 | 2024: +0.005 | 2025: +0.075 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.102 | 2017: +0.005 | 2018: +0.272 | 2019: +0.140 | 2020: +0.083 | 2021: +0.312 | 2022: +0.296 | 2023: +0.189 | 2024: +0.172 | 2025: +0.227 | 2026: +0.141
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.56
- Early IC=+0.0709, Recent IC=+0.0399, 1st-half IC=+0.0974, 2nd-half IC=+0.0775, Neg regimes=0/5
- Weak component: `morning_volume_weighted_momentum` (CV=0.61, neg years=0)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.053, Q3_mid=+0.081, Q4=+0.092, Q5_high_vol=+0.167

**`combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=-0.0273, Sharpe=+1.0319)
- Admission: Train IC=+0.2084, Deflated=+0.2089, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.072 | 2017: -0.033 | 2018: +0.208 | 2019: +0.106 | 2020: +0.028 | 2021: +0.147 | 2022: +0.020 | 2023: +0.110 | 2024: +0.044 | 2025: +0.080 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.111 | 2016: +0.082 | 2017: -0.119 | 2018: +0.388 | 2019: +0.317 | 2020: +0.139 | 2021: +0.295 | 2022: +0.133 | 2023: +0.057 | 2024: +0.256 | 2025: +0.044 | 2026: +0.278
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.40
- Early IC=+0.1570, Recent IC=+0.0620, 1st-half IC=+0.1242, 2nd-half IC=+0.0752, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.90, neg years=2)
- Regime ICs: Q1_low_vol=+0.016, Q2=+0.081, Q3_mid=+0.066, Q4=+0.090, Q5_high_vol=+0.211

### 500ETF — `single` False Positives

**`combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend`** (Lock IC=-0.1131, Sharpe=-3.2742)
- Admission: Train IC=+0.1737, Deflated=+0.1729, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.043 | 2016: +0.030 | 2017: +0.096 | 2018: +0.096 | 2019: +0.066 | 2020: +0.074 | 2021: +0.053 | 2022: +0.093 | 2023: +0.124 | 2024: +0.089 | 2025: +0.122 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.106 | 2016: +0.019 | 2017: +0.102 | 2018: +0.210 | 2019: +0.178 | 2020: +0.030 | 2021: +0.241 | 2022: +0.060 | 2023: +0.291 | 2024: +0.236 | 2025: +0.213 | 2026: -0.357
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.48, Recency ratio=1.30
- Early IC=+0.0813, Recent IC=+0.1054, 1st-half IC=+0.0743, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.083, Q3_mid=+0.140, Q4=+0.076, Q5_high_vol=+0.074

**`combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend`** (Lock IC=-0.0712, Sharpe=-3.2742)
- Admission: Train IC=+0.1839, Deflated=+0.1821, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.105 | 2016: -0.017 | 2017: +0.086 | 2018: +0.018 | 2019: +0.152 | 2020: +0.029 | 2021: +0.084 | 2022: +0.155 | 2023: +0.115 | 2024: +0.096 | 2025: +0.120 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.010 | 2016: -0.074 | 2017: +0.095 | 2018: +0.098 | 2019: +0.327 | 2020: +0.014 | 2021: +0.240 | 2022: +0.166 | 2023: +0.301 | 2024: +0.327 | 2025: +0.223 | 2026: -0.357
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.82, Recency ratio=1.27
- Early IC=+0.0850, Recent IC=+0.1081, 1st-half IC=+0.0686, 2nd-half IC=+0.1249, Neg regimes=0/5
- Weak component: `early_order_flow_imbalance` (CV=0.29, neg years=0)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.072, Q3_mid=+0.111, Q4=+0.080, Q5_high_vol=+0.100

**`combo_sig_product__early_body_momentum__vwap_close_divergence_trend`** (Lock IC=-0.0956, Sharpe=-3.2742)
- Admission: Train IC=+0.1710, Deflated=+0.1704, IR=0.68, Mono=0.75, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.072 | 2016: +0.042 | 2017: +0.086 | 2018: +0.090 | 2019: +0.105 | 2020: +0.060 | 2021: +0.052 | 2022: +0.104 | 2023: +0.122 | 2024: +0.087 | 2025: +0.137 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.019 | 2017: +0.102 | 2018: +0.210 | 2019: +0.234 | 2020: +0.012 | 2021: +0.240 | 2022: +0.070 | 2023: +0.291 | 2024: +0.202 | 2025: +0.213 | 2026: -0.357
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=1.16
- Early IC=+0.0971, Recent IC=+0.1123, 1st-half IC=+0.0798, 2nd-half IC=+0.1163, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.100, Q3_mid=+0.139, Q4=+0.103, Q5_high_vol=+0.053

**`combo_sig_product__max_down_ret__vwap_close_divergence_trend`** (Lock IC=-0.0915, Sharpe=-2.8218)
- Admission: Train IC=+0.1750, Deflated=+0.1753, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.141 | 2017: +0.110 | 2018: +0.129 | 2019: +0.055 | 2020: +0.086 | 2021: +0.073 | 2022: +0.139 | 2023: +0.134 | 2024: +0.105 | 2025: +0.130 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.166 | 2016: +0.199 | 2017: +0.083 | 2018: +0.149 | 2019: +0.178 | 2020: +0.056 | 2021: +0.169 | 2022: +0.163 | 2023: +0.270 | 2024: +0.283 | 2025: +0.275 | 2026: -0.258
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.60, Recency ratio=1.28
- Early IC=+0.0920, Recent IC=+0.1175, 1st-half IC=+0.0805, 2nd-half IC=+0.1286, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.093, Q3_mid=+0.131, Q4=+0.120, Q5_high_vol=+0.092

**`combo_mean__vwap_close_divergence_trend__bar_body_rng_0`** (Lock IC=-0.0705, Sharpe=-2.6077)
- Admission: Train IC=+0.2197, Deflated=+0.2186, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.095 | 2017: +0.201 | 2018: +0.177 | 2019: +0.139 | 2020: +0.097 | 2021: +0.128 | 2022: +0.075 | 2023: +0.095 | 2024: +0.106 | 2025: +0.154 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.065 | 2017: +0.141 | 2018: +0.376 | 2019: +0.284 | 2020: +0.020 | 2021: +0.273 | 2022: +0.285 | 2023: +0.288 | 2024: +0.186 | 2025: +0.129 | 2026: -0.338
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.82
- Early IC=+0.1578, Recent IC=+0.1301, 1st-half IC=+0.1301, 2nd-half IC=+0.1148, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.039, Q3_mid=+0.159, Q4=+0.119, Q5_high_vol=+0.134

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=-0.0646, Sharpe=-2.3002)
- Admission: Train IC=+0.2178, Deflated=+0.2170, IR=0.69, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.76, Recency ratio=0.71
- Early IC=+0.1800, Recent IC=+0.1273, 1st-half IC=+0.1492, 2nd-half IC=+0.1140, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.034, Q3_mid=+0.117, Q4=+0.128, Q5_high_vol=+0.226

**`combo_min__early_order_flow_imbalance__bar_body_rng_0`** (Lock IC=-0.0451, Sharpe=-1.9899)
- Admission: Train IC=+0.2411, Deflated=+0.2397, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.020 | 2017: +0.167 | 2018: +0.166 | 2019: +0.145 | 2020: +0.061 | 2021: +0.148 | 2022: +0.118 | 2023: +0.082 | 2024: +0.128 | 2025: +0.088 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.284 | 2016: +0.086 | 2017: +0.183 | 2018: +0.347 | 2019: +0.303 | 2020: +0.047 | 2021: +0.175 | 2022: +0.295 | 2023: +0.050 | 2024: +0.373 | 2025: +0.231 | 2026: -0.139
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.69
- Early IC=+0.1558, Recent IC=+0.1080, 1st-half IC=+0.1252, 2nd-half IC=+0.1117, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.034, Q3_mid=+0.113, Q4=+0.137, Q5_high_vol=+0.140

**`combo_rank_max__early_order_flow_imbalance__max_down_ret`** (Lock IC=-0.0706, Sharpe=-1.9365)
- Admission: Train IC=+0.2248, Deflated=+0.2233, IR=0.75, Mono=0.77, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.217 | 2016: -0.005 | 2017: +0.203 | 2018: +0.154 | 2019: +0.130 | 2020: +0.084 | 2021: +0.100 | 2022: +0.061 | 2023: +0.044 | 2024: +0.119 | 2025: +0.177 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.355 | 2016: -0.164 | 2017: +0.253 | 2018: +0.186 | 2019: +0.387 | 2020: +0.014 | 2021: +0.361 | 2022: +0.274 | 2023: +0.158 | 2024: +0.327 | 2025: +0.267 | 2026: -0.164
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=1.01
- Early IC=+0.1435, Recent IC=+0.1456, 1st-half IC=+0.1114, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.033, Q3_mid=+0.161, Q4=+0.127, Q5_high_vol=+0.109

**`combo_sig_product__max_up_ret__vwap_close_divergence_trend`** (Lock IC=-0.0518, Sharpe=-1.9303)
- Admission: Train IC=+0.1847, Deflated=+0.1849, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.142 | 2017: +0.154 | 2018: +0.199 | 2019: +0.131 | 2020: +0.110 | 2021: +0.042 | 2022: +0.099 | 2023: +0.089 | 2024: +0.092 | 2025: +0.071 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.250 | 2017: +0.166 | 2018: +0.319 | 2019: +0.310 | 2020: +0.076 | 2021: +0.254 | 2022: +0.087 | 2023: +0.281 | 2024: +0.313 | 2025: -0.006 | 2026: -0.112
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.50
- Early IC=+0.1646, Recent IC=+0.0815, 1st-half IC=+0.1241, 2nd-half IC=+0.0971, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.30, neg years=0)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.054, Q3_mid=+0.088, Q4=+0.088, Q5_high_vol=+0.171

**`combo_rank_max__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=-0.0686, Sharpe=-1.8069)
- Admission: Train IC=+0.2229, Deflated=+0.2221, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.048 | 2017: +0.216 | 2018: +0.159 | 2019: +0.107 | 2020: +0.105 | 2021: +0.088 | 2022: +0.062 | 2023: +0.047 | 2024: +0.136 | 2025: +0.153 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.350 | 2016: -0.108 | 2017: +0.230 | 2018: +0.127 | 2019: +0.354 | 2020: +0.058 | 2021: +0.265 | 2022: +0.230 | 2023: +0.214 | 2024: +0.304 | 2025: +0.243 | 2026: -0.150
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=1.10
- Early IC=+0.1327, Recent IC=+0.1457, 1st-half IC=+0.1092, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.073, Q3_mid=+0.143, Q4=+0.122, Q5_high_vol=+0.127

**`morning_volume_weighted_momentum`** (Lock IC=-0.0906, Sharpe=-1.7423)
- Admission: Train IC=+0.1720, Deflated=+0.1705, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.039 | 2017: +0.203 | 2018: +0.126 | 2019: +0.090 | 2020: +0.097 | 2021: +0.088 | 2022: +0.095 | 2023: +0.096 | 2024: +0.115 | 2025: +0.165 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.078 | 2017: +0.280 | 2018: +0.104 | 2019: +0.039 | 2020: +0.117 | 2021: +0.174 | 2022: +0.149 | 2023: +0.283 | 2024: +0.184 | 2025: +0.241 | 2026: -0.108
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=1.27, Recency ratio=1.29
- Early IC=+0.1081, Recent IC=+0.1398, 1st-half IC=+0.0985, 2nd-half IC=+0.1255, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.098, Q3_mid=+0.146, Q4=+0.100, Q5_high_vol=+0.125

**`combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0`** (Lock IC=-0.0298, Sharpe=-1.5915)
- Admission: Train IC=+0.2298, Deflated=+0.2291, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.075 | 2017: +0.238 | 2018: +0.220 | 2019: +0.131 | 2020: +0.143 | 2021: +0.116 | 2022: +0.097 | 2023: +0.092 | 2024: +0.151 | 2025: +0.111 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.367 | 2016: -0.010 | 2017: +0.233 | 2018: +0.393 | 2019: +0.216 | 2020: +0.187 | 2021: +0.256 | 2022: +0.230 | 2023: +0.249 | 2024: +0.242 | 2025: +0.076 | 2026: -0.290
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.75
- Early IC=+0.1756, Recent IC=+0.1312, 1st-half IC=+0.1492, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.060, Q3_mid=+0.150, Q4=+0.142, Q5_high_vol=+0.194

**`combo_min__first_bar_return__bar_body_rng_0`** (Lock IC=-0.0051, Sharpe=-1.4910)
- Admission: Train IC=+0.2178, Deflated=+0.2175, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.108 | 2017: +0.160 | 2018: +0.231 | 2019: +0.128 | 2020: +0.086 | 2021: +0.119 | 2022: +0.066 | 2023: +0.079 | 2024: +0.110 | 2025: +0.100 | 2026: -0.005
- Yearly Tail ICs:   2015: +0.390 | 2016: -0.045 | 2017: +0.304 | 2018: +0.458 | 2019: +0.130 | 2020: +0.090 | 2021: +0.318 | 2022: +0.170 | 2023: +0.186 | 2024: +0.154 | 2025: +0.179 | 2026: -0.174
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.1795, Recent IC=+0.1051, 1st-half IC=+0.1389, 2nd-half IC=+0.0909, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.005, Q3_mid=+0.093, Q4=+0.136, Q5_high_vol=+0.169

**`combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0`** (Lock IC=-0.0656, Sharpe=-1.4128)
- Admission: Train IC=+0.2029, Deflated=+0.2020, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.077 | 2017: +0.197 | 2018: +0.211 | 2019: +0.089 | 2020: +0.116 | 2021: +0.110 | 2022: +0.106 | 2023: +0.101 | 2024: +0.130 | 2025: +0.108 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.111 | 2017: +0.286 | 2018: +0.394 | 2019: +0.113 | 2020: +0.199 | 2021: +0.193 | 2022: +0.159 | 2023: +0.316 | 2024: +0.244 | 2025: -0.063 | 2026: -0.270
- IC CV=0.29, Neg years (linear/tail)=0/1 of 8, Half ratio=0.91, Recency ratio=0.79
- Early IC=+0.1502, Recent IC=+0.1188, 1st-half IC=+0.1296, 2nd-half IC=+0.1174, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.055, Q3_mid=+0.130, Q4=+0.119, Q5_high_vol=+0.182

**`combo_mean__bar_ret_0__close_vs_open_range`** (Lock IC=-0.0383, Sharpe=-1.2349)
- Admission: Train IC=+0.2414, Deflated=+0.2405, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.094 | 2017: +0.212 | 2018: +0.196 | 2019: +0.106 | 2020: +0.116 | 2021: +0.098 | 2022: +0.096 | 2023: +0.079 | 2024: +0.154 | 2025: +0.119 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.026 | 2017: +0.245 | 2018: +0.357 | 2019: +0.140 | 2020: +0.182 | 2021: +0.367 | 2022: +0.278 | 2023: +0.233 | 2024: +0.329 | 2025: +0.057 | 2026: -0.203
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.91
- Early IC=+0.1510, Recent IC=+0.1367, 1st-half IC=+0.1278, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.055, Q3_mid=+0.130, Q4=+0.134, Q5_high_vol=+0.168

**`combo_mean__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=-0.0676, Sharpe=-1.0649)
- Admission: Train IC=+0.2187, Deflated=+0.2177, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.064 | 2017: +0.222 | 2018: +0.182 | 2019: +0.128 | 2020: +0.108 | 2021: +0.123 | 2022: +0.094 | 2023: +0.091 | 2024: +0.130 | 2025: +0.132 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.040 | 2017: +0.144 | 2018: +0.393 | 2019: +0.217 | 2020: +0.090 | 2021: +0.280 | 2022: +0.240 | 2023: +0.275 | 2024: +0.151 | 2025: +0.186 | 2026: -0.246
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.84
- Early IC=+0.1553, Recent IC=+0.1311, 1st-half IC=+0.1337, 2nd-half IC=+0.1191, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.064, Q3_mid=+0.145, Q4=+0.113, Q5_high_vol=+0.164

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=-0.0068, Sharpe=-1.0463)
- Admission: Train IC=+0.2013, Deflated=+0.2009, IR=0.55, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.094 | 2017: +0.222 | 2018: +0.182 | 2019: +0.099 | 2020: +0.113 | 2021: +0.125 | 2022: +0.107 | 2023: +0.082 | 2024: +0.138 | 2025: +0.094 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.563 | 2016: +0.343 | 2017: +0.299 | 2018: +0.225 | 2019: +0.146 | 2020: +0.164 | 2021: +0.375 | 2022: +0.107 | 2023: +0.181 | 2024: +0.244 | 2025: +0.001 | 2026: -0.041
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.83
- Early IC=+0.1406, Recent IC=+0.1163, 1st-half IC=+0.1262, 2nd-half IC=+0.1161, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.061, Q3_mid=+0.147, Q4=+0.122, Q5_high_vol=+0.188

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=-0.0114, Sharpe=-0.9885)
- Admission: Train IC=+0.2031, Deflated=+0.2029, IR=0.71, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.097 | 2017: +0.234 | 2018: +0.253 | 2019: +0.145 | 2020: +0.148 | 2021: +0.143 | 2022: +0.095 | 2023: +0.097 | 2024: +0.160 | 2025: +0.085 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.139 | 2017: +0.259 | 2018: +0.451 | 2019: +0.128 | 2020: +0.189 | 2021: +0.341 | 2022: +0.118 | 2023: +0.155 | 2024: +0.182 | 2025: -0.024 | 2026: -0.214
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.62
- Early IC=+0.1990, Recent IC=+0.1225, 1st-half IC=+0.1675, 2nd-half IC=+0.1183, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.044, Q3_mid=+0.135, Q4=+0.147, Q5_high_vol=+0.233

**`combo_min__bar_ret_0__early_order_flow_imbalance`** (Lock IC=-0.0339, Sharpe=-0.8457)
- Admission: Train IC=+0.2402, Deflated=+0.2390, IR=0.78, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.005 | 2017: +0.137 | 2018: +0.160 | 2019: +0.157 | 2020: +0.064 | 2021: +0.165 | 2022: +0.125 | 2023: +0.077 | 2024: +0.121 | 2025: +0.102 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.007 | 2017: +0.319 | 2018: +0.436 | 2019: +0.207 | 2020: +0.014 | 2021: +0.248 | 2022: +0.246 | 2023: +0.145 | 2024: +0.369 | 2025: +0.264 | 2026: -0.144
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.70
- Early IC=+0.1587, Recent IC=+0.1117, 1st-half IC=+0.1328, 2nd-half IC=+0.1101, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.047, Q3_mid=+0.113, Q4=+0.125, Q5_high_vol=+0.151

**`combo_mean__max_up_ret__max_down_ret`** (Lock IC=-0.0160, Sharpe=-0.6629)
- Admission: Train IC=+0.1869, Deflated=+0.1868, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.068 | 2017: +0.243 | 2018: +0.206 | 2019: +0.121 | 2020: +0.136 | 2021: +0.105 | 2022: +0.105 | 2023: +0.092 | 2024: +0.157 | 2025: +0.107 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.213 | 2017: +0.325 | 2018: +0.285 | 2019: +0.177 | 2020: +0.135 | 2021: +0.329 | 2022: +0.134 | 2023: +0.256 | 2024: +0.275 | 2025: -0.033 | 2026: -0.157
- IC CV=0.27, Neg years (linear/tail)=0/1 of 8, Half ratio=0.90, Recency ratio=0.81
- Early IC=+0.1633, Recent IC=+0.1317, 1st-half IC=+0.1363, 2nd-half IC=+0.1233, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.059, Q3_mid=+0.142, Q4=+0.120, Q5_high_vol=+0.196

**`combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0`** (Lock IC=-0.0199, Sharpe=-0.4536)
- Admission: Train IC=+0.2227, Deflated=+0.2222, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.078 | 2017: +0.189 | 2018: +0.192 | 2019: +0.124 | 2020: +0.102 | 2021: +0.096 | 2022: +0.097 | 2023: +0.103 | 2024: +0.137 | 2025: +0.131 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.364 | 2016: +0.032 | 2017: +0.328 | 2018: +0.366 | 2019: +0.176 | 2020: +0.069 | 2021: +0.264 | 2022: +0.224 | 2023: +0.164 | 2024: +0.294 | 2025: +0.235 | 2026: +0.033
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.85
- Early IC=+0.1582, Recent IC=+0.1341, 1st-half IC=+0.1241, 2nd-half IC=+0.1202, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.076, Q3_mid=+0.134, Q4=+0.120, Q5_high_vol=+0.164

**`combo_rank_min__net_volume_flow__bar_body_rng_0`** (Lock IC=-0.0164, Sharpe=-0.4298)
- Admission: Train IC=+0.2253, Deflated=+0.2246, IR=0.55, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.065 | 2017: +0.183 | 2018: +0.173 | 2019: +0.117 | 2020: +0.094 | 2021: +0.092 | 2022: +0.087 | 2023: +0.087 | 2024: +0.129 | 2025: +0.124 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.361 | 2016: -0.034 | 2017: +0.115 | 2018: +0.275 | 2019: +0.139 | 2020: +0.127 | 2021: +0.224 | 2022: +0.203 | 2023: +0.151 | 2024: +0.298 | 2025: +0.205 | 2026: +0.038
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.87
- Early IC=+0.1451, Recent IC=+0.1258, 1st-half IC=+0.1171, 2nd-half IC=+0.1126, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.033, Q3_mid=+0.142, Q4=+0.122, Q5_high_vol=+0.137

**`combo_min__net_volume_flow__first_bar_return`** (Lock IC=-0.0010, Sharpe=-0.2212)
- Admission: Train IC=+0.2435, Deflated=+0.2432, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: +0.181 | 2018: +0.177 | 2019: +0.120 | 2020: +0.094 | 2021: +0.083 | 2022: +0.086 | 2023: +0.078 | 2024: +0.134 | 2025: +0.124 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.015 | 2017: +0.228 | 2018: +0.376 | 2019: +0.143 | 2020: +0.116 | 2021: +0.288 | 2022: +0.224 | 2023: +0.316 | 2024: +0.337 | 2025: +0.140 | 2026: -0.073
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.87
- Early IC=+0.1487, Recent IC=+0.1290, 1st-half IC=+0.1184, 2nd-half IC=+0.1114, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.044, Q3_mid=+0.134, Q4=+0.115, Q5_high_vol=+0.151

**`combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=-0.0197, Sharpe=+0.1617)
- Admission: Train IC=+0.2192, Deflated=+0.2184, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.119 | 2017: +0.216 | 2018: +0.219 | 2019: +0.139 | 2020: +0.146 | 2021: +0.080 | 2022: +0.114 | 2023: +0.088 | 2024: +0.126 | 2025: +0.146 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.136 | 2017: +0.239 | 2018: +0.328 | 2019: +0.234 | 2020: +0.274 | 2021: +0.103 | 2022: +0.157 | 2023: +0.206 | 2024: +0.354 | 2025: +0.024 | 2026: -0.252
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.76
- Early IC=+0.1785, Recent IC=+0.1361, 1st-half IC=+0.1472, 2nd-half IC=+0.1235, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.059, Q3_mid=+0.152, Q4=+0.127, Q5_high_vol=+0.212

### 159915ETF — `single` False Positives

**`combo_rank_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0913, Sharpe=-4.2927)
- Admission: Train IC=+0.2254, Deflated=+0.2264, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.059 | 2017: +0.061 | 2018: +0.047 | 2019: +0.137 | 2020: +0.115 | 2021: +0.146 | 2022: +0.108 | 2023: +0.179 | 2024: +0.061 | 2025: +0.188 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.319 | 2016: -0.005 | 2017: +0.036 | 2018: +0.069 | 2019: +0.292 | 2020: +0.212 | 2021: +0.256 | 2022: +0.199 | 2023: +0.434 | 2024: +0.167 | 2025: +0.183 | 2026: -0.543
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.43
- Early IC=+0.0888, Recent IC=+0.1265, 1st-half IC=+0.1025, 2nd-half IC=+0.1391, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.172, Q3_mid=+0.119, Q4=+0.112, Q5_high_vol=+0.104

**`combo_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.1035, Sharpe=-4.2121)
- Admission: Train IC=+0.2332, Deflated=+0.2339, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.92
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

**`combo_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0681, Sharpe=-3.8603)
- Admission: Train IC=+0.2232, Deflated=+0.2238, IR=0.69, Mono=0.73, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.073 | 2017: +0.042 | 2018: +0.065 | 2019: +0.114 | 2020: +0.116 | 2021: +0.149 | 2022: +0.125 | 2023: +0.172 | 2024: +0.068 | 2025: +0.139 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.198 | 2017: +0.116 | 2018: +0.188 | 2019: +0.331 | 2020: +0.198 | 2021: +0.354 | 2022: +0.282 | 2023: +0.312 | 2024: +0.290 | 2025: +0.103 | 2026: -0.370
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.16
- Early IC=+0.0892, Recent IC=+0.1038, 1st-half IC=+0.1090, 2nd-half IC=+0.1235, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.148, Q3_mid=+0.089, Q4=+0.124, Q5_high_vol=+0.114

**`combo_ratio__max_up_ret__keltner_squeeze_width`** (Lock IC=-0.0851, Sharpe=-3.6644)
- Admission: Train IC=+0.2014, Deflated=+0.2021, IR=0.62, Mono=0.74, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.055 | 2017: +0.032 | 2018: +0.028 | 2019: +0.120 | 2020: +0.113 | 2021: +0.149 | 2022: +0.110 | 2023: +0.150 | 2024: +0.057 | 2025: +0.127 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.084 | 2016: +0.084 | 2017: +0.055 | 2018: +0.093 | 2019: +0.379 | 2020: +0.196 | 2021: +0.168 | 2022: +0.133 | 2023: +0.250 | 2024: +0.184 | 2025: +0.173 | 2026: -0.348
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=1.24
- Early IC=+0.0740, Recent IC=+0.0921, 1st-half IC=+0.1003, 2nd-half IC=+0.1064, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68, neg years=1)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.148, Q3_mid=+0.101, Q4=+0.078, Q5_high_vol=+0.138

**`combo_max__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0771, Sharpe=-3.6387)
- Admission: Train IC=+0.2417, Deflated=+0.2416, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.160 | 2017: -0.012 | 2018: +0.104 | 2019: +0.185 | 2020: +0.141 | 2021: +0.171 | 2022: +0.109 | 2023: +0.142 | 2024: +0.059 | 2025: +0.182 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.066 | 2016: +0.181 | 2017: +0.001 | 2018: +0.201 | 2019: +0.295 | 2020: +0.174 | 2021: +0.360 | 2022: +0.247 | 2023: +0.408 | 2024: +0.199 | 2025: +0.156 | 2026: -0.316
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.83
- Early IC=+0.1441, Recent IC=+0.1201, 1st-half IC=+0.1398, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.136, Q3_mid=+0.153, Q4=+0.105, Q5_high_vol=+0.131

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct`** (Lock IC=-0.0930, Sharpe=-3.4843)
- Admission: Train IC=+0.2223, Deflated=+0.2230, IR=0.98, Mono=0.82, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.080 | 2017: +0.050 | 2018: +0.060 | 2019: +0.144 | 2020: +0.102 | 2021: +0.150 | 2022: +0.105 | 2023: +0.178 | 2024: +0.072 | 2025: +0.155 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.115 | 2016: +0.245 | 2017: +0.046 | 2018: +0.218 | 2019: +0.343 | 2020: +0.213 | 2021: +0.204 | 2022: +0.281 | 2023: +0.464 | 2024: +0.129 | 2025: +0.124 | 2026: -0.317
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=1.12
- Early IC=+0.1018, Recent IC=+0.1135, 1st-half IC=+0.1086, 2nd-half IC=+0.1267, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76, neg years=1)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.169, Q3_mid=+0.101, Q4=+0.118, Q5_high_vol=+0.109

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=-0.0654, Sharpe=-3.3106)
- Admission: Train IC=+0.2371, Deflated=+0.2371, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.098 | 2017: +0.035 | 2018: +0.092 | 2019: +0.185 | 2020: +0.107 | 2021: +0.187 | 2022: +0.094 | 2023: +0.184 | 2024: +0.070 | 2025: +0.173 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.115 | 2016: +0.106 | 2017: +0.122 | 2018: +0.243 | 2019: +0.298 | 2020: +0.049 | 2021: +0.322 | 2022: +0.310 | 2023: +0.380 | 2024: +0.184 | 2025: +0.223 | 2026: -0.340
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.88
- Early IC=+0.1384, Recent IC=+0.1214, 1st-half IC=+0.1330, 2nd-half IC=+0.1302, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.154, Q3_mid=+0.127, Q4=+0.125, Q5_high_vol=+0.137

**`combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=-0.0381, Sharpe=-3.2808)
- Admission: Train IC=+0.2801, Deflated=+0.2805, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.093 | 2017: +0.001 | 2018: +0.078 | 2019: +0.167 | 2020: +0.104 | 2021: +0.151 | 2022: +0.084 | 2023: +0.171 | 2024: +0.072 | 2025: +0.199 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.313 | 2016: -0.018 | 2017: +0.028 | 2018: +0.263 | 2019: +0.422 | 2020: +0.166 | 2021: +0.183 | 2022: +0.247 | 2023: +0.432 | 2024: +0.210 | 2025: +0.339 | 2026: -0.454
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.10
- Early IC=+0.1223, Recent IC=+0.1351, 1st-half IC=+0.1115, 2nd-half IC=+0.1357, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.156, Q3_mid=+0.151, Q4=+0.081, Q5_high_vol=+0.113

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0737, Sharpe=-3.0060)
- Admission: Train IC=+0.2261, Deflated=+0.2260, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.084 | 2017: +0.064 | 2018: +0.067 | 2019: +0.173 | 2020: +0.066 | 2021: +0.220 | 2022: +0.089 | 2023: +0.165 | 2024: +0.079 | 2025: +0.179 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.017 | 2017: +0.238 | 2018: +0.208 | 2019: +0.343 | 2020: -0.017 | 2021: +0.310 | 2022: +0.236 | 2023: +0.279 | 2024: +0.249 | 2025: +0.235 | 2026: -0.216
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=1.07
- Early IC=+0.1207, Recent IC=+0.1297, 1st-half IC=+0.1257, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.155, Q3_mid=+0.136, Q4=+0.125, Q5_high_vol=+0.133

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0854, Sharpe=-2.9019)
- Admission: Train IC=+0.2440, Deflated=+0.2438, IR=0.75, Mono=0.82, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.71, Recency ratio=2.05
- Early IC=+0.0722, Recent IC=+0.1480, 1st-half IC=+0.0848, 2nd-half IC=+0.1448, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.151, Q3_mid=+0.136, Q4=+0.096, Q5_high_vol=+0.107

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0595, Sharpe=-2.7716)
- Admission: Train IC=+0.2532, Deflated=+0.2535, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.10
- Early IC=+0.1138, Recent IC=+0.1250, 1st-half IC=+0.1234, 2nd-half IC=+0.1399, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.173, Q3_mid=+0.106, Q4=+0.143, Q5_high_vol=+0.142

**`combo_max__max_up_ret__rally_strength_max`** (Lock IC=-0.0883, Sharpe=-2.6944)
- Admission: Train IC=+0.2401, Deflated=+0.2402, IR=0.60, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.040 | 2017: +0.036 | 2018: +0.052 | 2019: +0.146 | 2020: +0.043 | 2021: +0.172 | 2022: +0.057 | 2023: +0.138 | 2024: +0.043 | 2025: +0.178 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.101 | 2016: +0.122 | 2017: -0.005 | 2018: +0.195 | 2019: +0.329 | 2020: +0.161 | 2021: +0.291 | 2022: +0.214 | 2023: +0.325 | 2024: +0.268 | 2025: +0.153 | 2026: -0.229
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=1.11
- Early IC=+0.0990, Recent IC=+0.1104, 1st-half IC=+0.1019, 2nd-half IC=+0.1027, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.157, Q3_mid=+0.133, Q4=+0.120, Q5_high_vol=+0.072

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0563, Sharpe=-2.6490)
- Admission: Train IC=+0.2775, Deflated=+0.2775, IR=0.87, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.149 | 2017: +0.001 | 2018: +0.089 | 2019: +0.181 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.152 | 2024: +0.062 | 2025: +0.186 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.024 | 2017: +0.040 | 2018: +0.261 | 2019: +0.408 | 2020: +0.180 | 2021: +0.310 | 2022: +0.269 | 2023: +0.345 | 2024: +0.233 | 2025: +0.245 | 2026: -0.185
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.86
- Early IC=+0.1418, Recent IC=+0.1224, 1st-half IC=+0.1369, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.134, Q3_mid=+0.143, Q4=+0.113, Q5_high_vol=+0.130

**`combo_rank_min__max_up_ret__rally_strength_max`** (Lock IC=-0.0714, Sharpe=-2.5162)
- Admission: Train IC=+0.2045, Deflated=+0.2046, IR=0.63, Mono=0.78, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.024 | 2017: +0.057 | 2018: +0.028 | 2019: +0.158 | 2020: +0.057 | 2021: +0.210 | 2022: +0.036 | 2023: +0.123 | 2024: +0.061 | 2025: +0.161 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.104 | 2017: +0.125 | 2018: +0.141 | 2019: +0.224 | 2020: +0.124 | 2021: +0.430 | 2022: +0.207 | 2023: +0.282 | 2024: +0.152 | 2025: +0.161 | 2026: -0.146
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=1.27
- Early IC=+0.0933, Recent IC=+0.1186, 1st-half IC=+0.1094, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.171, Q3_mid=+0.164, Q4=+0.106, Q5_high_vol=+0.067

**`combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration`** (Lock IC=-0.0159, Sharpe=-2.4481)
- Admission: Train IC=+0.2175, Deflated=+0.2176, IR=0.48, Mono=0.68, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.064 | 2017: +0.040 | 2018: +0.116 | 2019: +0.213 | 2020: +0.076 | 2021: +0.137 | 2022: +0.048 | 2023: +0.154 | 2024: +0.071 | 2025: +0.119 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.131 | 2016: -0.087 | 2017: +0.052 | 2018: +0.093 | 2019: +0.469 | 2020: +0.096 | 2021: +0.382 | 2022: +0.021 | 2023: +0.365 | 2024: +0.048 | 2025: +0.451 | 2026: -0.289
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.58
- Early IC=+0.1641, Recent IC=+0.0951, 1st-half IC=+0.1232, 2nd-half IC=+0.1020, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.108, Q3_mid=+0.108, Q4=+0.121, Q5_high_vol=+0.130

**`combo_mean__volatility_expansion_trend_vector__rally_strength_max`** (Lock IC=-0.0867, Sharpe=-2.3108)
- Admission: Train IC=+0.2340, Deflated=+0.2339, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.001 | 2017: +0.039 | 2018: +0.010 | 2019: +0.125 | 2020: +0.029 | 2021: +0.167 | 2022: +0.043 | 2023: +0.145 | 2024: +0.071 | 2025: +0.200 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.201 | 2016: +0.049 | 2017: -0.024 | 2018: +0.099 | 2019: +0.367 | 2020: +0.084 | 2021: +0.219 | 2022: +0.156 | 2023: +0.398 | 2024: +0.243 | 2025: +0.300 | 2026: -0.141
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=1.61, Recency ratio=2.01
- Early IC=+0.0676, Recent IC=+0.1358, 1st-half IC=+0.0751, 2nd-half IC=+0.1206, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.159, Q3_mid=+0.150, Q4=+0.080, Q5_high_vol=+0.063

**`combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0930, Sharpe=-2.1195)
- Admission: Train IC=+0.2483, Deflated=+0.2487, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.048 | 2017: +0.034 | 2018: +0.048 | 2019: +0.165 | 2020: +0.087 | 2021: +0.143 | 2022: +0.100 | 2023: +0.179 | 2024: +0.106 | 2025: +0.197 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.249 | 2016: -0.053 | 2017: +0.064 | 2018: +0.031 | 2019: +0.396 | 2020: +0.246 | 2021: +0.109 | 2022: +0.308 | 2023: +0.347 | 2024: +0.267 | 2025: +0.295 | 2026: -0.202
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.43
- Early IC=+0.1070, Recent IC=+0.1525, 1st-half IC=+0.1014, 2nd-half IC=+0.1518, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.165, Q3_mid=+0.134, Q4=+0.118, Q5_high_vol=+0.125

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=-0.0318, Sharpe=-2.0212)
- Admission: Train IC=+0.2512, Deflated=+0.2511, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.032 | 2017: +0.022 | 2018: +0.079 | 2019: +0.178 | 2020: +0.092 | 2021: +0.165 | 2022: +0.155 | 2023: +0.149 | 2024: +0.068 | 2025: +0.195 | 2026: -0.032
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.240 | 2017: +0.031 | 2018: +0.116 | 2019: +0.351 | 2020: +0.157 | 2021: +0.329 | 2022: +0.376 | 2023: +0.334 | 2024: +0.201 | 2025: +0.255 | 2026: -0.254
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.03
- Early IC=+0.1284, Recent IC=+0.1316, 1st-half IC=+0.1298, 2nd-half IC=+0.1472, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.160, Q3_mid=+0.143, Q4=+0.146, Q5_high_vol=+0.145

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early`** (Lock IC=-0.0776, Sharpe=-2.0006)
- Admission: Train IC=+0.2239, Deflated=+0.2244, IR=0.71, Mono=0.77, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.097 | 2017: +0.045 | 2018: +0.067 | 2019: +0.166 | 2020: +0.087 | 2021: +0.155 | 2022: +0.092 | 2023: +0.165 | 2024: +0.078 | 2025: +0.132 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.393 | 2016: +0.175 | 2017: +0.185 | 2018: +0.138 | 2019: +0.338 | 2020: +0.189 | 2021: +0.251 | 2022: +0.196 | 2023: +0.462 | 2024: +0.167 | 2025: +0.130 | 2026: -0.170
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=0.90
- Early IC=+0.1167, Recent IC=+0.1051, 1st-half IC=+0.1117, 2nd-half IC=+0.1187, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.149, Q3_mid=+0.106, Q4=+0.116, Q5_high_vol=+0.123

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0811, Sharpe=-1.8808)
- Admission: Train IC=+0.2099, Deflated=+0.2097, IR=0.69, Mono=0.77, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.084 | 2016: +0.036 | 2017: +0.087 | 2018: +0.104 | 2019: +0.173 | 2020: +0.046 | 2021: +0.139 | 2022: +0.087 | 2023: +0.166 | 2024: +0.120 | 2025: +0.124 | 2026: -0.081
- Yearly Tail ICs:   2015: -0.249 | 2016: +0.198 | 2017: +0.127 | 2018: +0.240 | 2019: +0.254 | 2020: +0.156 | 2021: +0.147 | 2022: +0.237 | 2023: +0.386 | 2024: +0.298 | 2025: +0.040 | 2026: -0.169
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.88
- Early IC=+0.1388, Recent IC=+0.1220, 1st-half IC=+0.1081, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.122, Q3_mid=+0.097, Q4=+0.118, Q5_high_vol=+0.137

**`combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0`** (Lock IC=-0.0711, Sharpe=-1.8622)
- Admission: Train IC=+0.2318, Deflated=+0.2318, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.132 | 2017: +0.015 | 2018: +0.116 | 2019: +0.180 | 2020: +0.131 | 2021: +0.137 | 2022: +0.053 | 2023: +0.170 | 2024: +0.057 | 2025: +0.104 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.348 | 2016: -0.011 | 2017: +0.033 | 2018: +0.214 | 2019: +0.430 | 2020: +0.199 | 2021: +0.152 | 2022: +0.038 | 2023: +0.304 | 2024: +0.264 | 2025: +0.359 | 2026: -0.044
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.54
- Early IC=+0.1479, Recent IC=+0.0802, 1st-half IC=+0.1277, 2nd-half IC=+0.0979, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.137, Q3_mid=+0.101, Q4=+0.095, Q5_high_vol=+0.132

**`combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0238, Sharpe=-1.8526)
- Admission: Train IC=+0.2562, Deflated=+0.2565, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.129 | 2017: +0.005 | 2018: +0.112 | 2019: +0.209 | 2020: +0.114 | 2021: +0.144 | 2022: +0.059 | 2023: +0.172 | 2024: +0.079 | 2025: +0.163 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.352 | 2016: -0.030 | 2017: +0.130 | 2018: +0.181 | 2019: +0.390 | 2020: +0.194 | 2021: +0.192 | 2022: +0.171 | 2023: +0.309 | 2024: +0.313 | 2025: +0.291 | 2026: -0.109
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.75
- Early IC=+0.1607, Recent IC=+0.1202, 1st-half IC=+0.1324, 2nd-half IC=+0.1210, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.134, Q3_mid=+0.134, Q4=+0.092, Q5_high_vol=+0.147

**`combo_min__max_up_ret__rally_strength_max`** (Lock IC=-0.0714, Sharpe=-1.8370)
- Admission: Train IC=+0.1903, Deflated=+0.1903, IR=0.59, Mono=0.73, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.046 | 2017: +0.051 | 2018: +0.044 | 2019: +0.180 | 2020: +0.067 | 2021: +0.179 | 2022: +0.053 | 2023: +0.132 | 2024: +0.074 | 2025: +0.182 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.321 | 2016: +0.116 | 2017: +0.110 | 2018: +0.120 | 2019: +0.341 | 2020: -0.030 | 2021: +0.268 | 2022: +0.101 | 2023: +0.379 | 2024: +0.198 | 2025: +0.175 | 2026: -0.189
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.00, Recency ratio=1.14
- Early IC=+0.1119, Recent IC=+0.1280, 1st-half IC=+0.1119, 2nd-half IC=+0.1119, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.172, Q3_mid=+0.144, Q4=+0.107, Q5_high_vol=+0.084

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

**`combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return`** (Lock IC=-0.0121, Sharpe=-1.7807)
- Admission: Train IC=+0.2224, Deflated=+0.2232, IR=0.72, Mono=0.78, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.145 | 2017: +0.007 | 2018: +0.124 | 2019: +0.199 | 2020: +0.113 | 2021: +0.150 | 2022: +0.093 | 2023: +0.169 | 2024: +0.059 | 2025: +0.157 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.163 | 2016: +0.100 | 2017: +0.068 | 2018: +0.216 | 2019: +0.272 | 2020: +0.119 | 2021: +0.289 | 2022: +0.175 | 2023: +0.386 | 2024: +0.127 | 2025: +0.183 | 2026: +0.006
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.67
- Early IC=+0.1615, Recent IC=+0.1080, 1st-half IC=+0.1375, 2nd-half IC=+0.1191, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.155, Q3_mid=+0.131, Q4=+0.099, Q5_high_vol=+0.128

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0192, Sharpe=-1.7777)
- Admission: Train IC=+0.2591, Deflated=+0.2590, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.073 | 2017: +0.025 | 2018: +0.078 | 2019: +0.188 | 2020: +0.134 | 2021: +0.148 | 2022: +0.123 | 2023: +0.187 | 2024: +0.105 | 2025: +0.189 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.069 | 2016: +0.182 | 2017: +0.197 | 2018: +0.207 | 2019: +0.364 | 2020: +0.165 | 2021: +0.331 | 2022: +0.263 | 2023: +0.402 | 2024: +0.247 | 2025: +0.257 | 2026: -0.059
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.11
- Early IC=+0.1327, Recent IC=+0.1470, 1st-half IC=+0.1370, 2nd-half IC=+0.1490, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.185, Q3_mid=+0.113, Q4=+0.134, Q5_high_vol=+0.159

**`combo_rel_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=-0.0322, Sharpe=-1.7594)
- Admission: Train IC=+0.2163, Deflated=+0.2154, IR=0.45, Mono=0.66, p=0.0002, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.121 | 2017: +0.114 | 2018: +0.055 | 2019: +0.070 | 2020: +0.101 | 2021: +0.110 | 2022: +0.078 | 2023: +0.160 | 2024: +0.125 | 2025: +0.157 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.237 | 2016: +0.068 | 2017: +0.219 | 2018: +0.107 | 2019: +0.268 | 2020: +0.073 | 2021: +0.274 | 2022: +0.315 | 2023: +0.380 | 2024: +0.135 | 2025: +0.257 | 2026: -0.203
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.60, Recency ratio=2.26
- Early IC=+0.0626, Recent IC=+0.1411, 1st-half IC=+0.0842, 2nd-half IC=+0.1348, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68, neg years=1)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.096, Q3_mid=+0.099, Q4=+0.121, Q5_high_vol=+0.063

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

**`combo_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=-0.0616, Sharpe=-1.6127)
- Admission: Train IC=+0.2037, Deflated=+0.2029, IR=0.51, Mono=0.67, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.119 | 2017: +0.114 | 2018: +0.058 | 2019: +0.081 | 2020: +0.109 | 2021: +0.110 | 2022: +0.109 | 2023: +0.155 | 2024: +0.136 | 2025: +0.153 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.239 | 2016: +0.067 | 2017: +0.171 | 2018: +0.138 | 2019: +0.222 | 2020: +0.078 | 2021: +0.271 | 2022: +0.347 | 2023: +0.302 | 2024: +0.108 | 2025: +0.280 | 2026: -0.113
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.67, Recency ratio=2.09
- Early IC=+0.0694, Recent IC=+0.1449, 1st-half IC=+0.0867, 2nd-half IC=+0.1444, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68, neg years=1)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.107, Q3_mid=+0.094, Q4=+0.131, Q5_high_vol=+0.077

**`combo_clamp_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=-0.0587, Sharpe=-1.5751)
- Admission: Train IC=+0.1887, Deflated=+0.1880, IR=0.45, Mono=0.66, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.121 | 2017: +0.114 | 2018: +0.056 | 2019: +0.080 | 2020: +0.107 | 2021: +0.110 | 2022: +0.107 | 2023: +0.155 | 2024: +0.135 | 2025: +0.149 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.079 | 2017: +0.173 | 2018: +0.103 | 2019: +0.285 | 2020: +0.048 | 2021: +0.283 | 2022: +0.278 | 2023: +0.301 | 2024: +0.107 | 2025: +0.171 | 2026: -0.172
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.68, Recency ratio=2.09
- Early IC=+0.0679, Recent IC=+0.1422, 1st-half IC=+0.0856, 2nd-half IC=+0.1435, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68, neg years=1)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.105, Q3_mid=+0.094, Q4=+0.128, Q5_high_vol=+0.071

**`combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0`** (Lock IC=-0.0399, Sharpe=-1.5508)
- Admission: Train IC=+0.2246, Deflated=+0.2251, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.144 | 2017: -0.009 | 2018: +0.103 | 2019: +0.172 | 2020: +0.141 | 2021: +0.146 | 2022: +0.074 | 2023: +0.132 | 2024: +0.061 | 2025: +0.125 | 2026: -0.040
- Yearly Tail ICs:   2015: +0.226 | 2016: +0.125 | 2017: +0.117 | 2018: +0.332 | 2019: +0.150 | 2020: +0.081 | 2021: +0.309 | 2022: +0.179 | 2023: +0.380 | 2024: +0.153 | 2025: +0.353 | 2026: -0.139
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.68
- Early IC=+0.1376, Recent IC=+0.0929, 1st-half IC=+0.1265, 2nd-half IC=+0.0990, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.133, Q3_mid=+0.110, Q4=+0.091, Q5_high_vol=+0.113

**`combo_rank_min__bar_body_rng_0__rally_strength_max`** (Lock IC=-0.0054, Sharpe=-1.4800)
- Admission: Train IC=+0.2386, Deflated=+0.2389, IR=0.90, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.059 | 2017: -0.005 | 2018: +0.086 | 2019: +0.210 | 2020: +0.053 | 2021: +0.178 | 2022: +0.012 | 2023: +0.115 | 2024: +0.066 | 2025: +0.144 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.246 | 2016: -0.010 | 2017: -0.116 | 2018: +0.361 | 2019: +0.456 | 2020: +0.073 | 2021: +0.193 | 2022: +0.051 | 2023: +0.247 | 2024: +0.171 | 2025: +0.248 | 2026: -0.161
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.67
- Early IC=+0.1571, Recent IC=+0.1058, 1st-half IC=+0.1265, 2nd-half IC=+0.0931, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.149, Q3_mid=+0.180, Q4=+0.080, Q5_high_vol=+0.074

**`combo_max__first_bar_return__rally_strength_max`** (Lock IC=-0.0599, Sharpe=-1.2485)
- Admission: Train IC=+0.2035, Deflated=+0.2038, IR=0.53, Mono=0.70, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.076 | 2017: +0.047 | 2018: +0.068 | 2019: +0.120 | 2020: +0.095 | 2021: +0.176 | 2022: +0.032 | 2023: +0.138 | 2024: +0.049 | 2025: +0.185 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.141 | 2016: +0.063 | 2017: +0.027 | 2018: +0.249 | 2019: +0.247 | 2020: +0.133 | 2021: +0.290 | 2022: +0.107 | 2023: +0.237 | 2024: +0.162 | 2025: +0.379 | 2026: -0.163
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=1.24
- Early IC=+0.0938, Recent IC=+0.1166, 1st-half IC=+0.1076, 2nd-half IC=+0.0983, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.170, Q3_mid=+0.120, Q4=+0.106, Q5_high_vol=+0.092

**`combo_min__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0016, Sharpe=-1.2131)
- Admission: Train IC=+0.2055, Deflated=+0.2056, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.88
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

**`combo_mean__max_up_ret__rally_strength_max`** (Lock IC=-0.0909, Sharpe=-1.0768)
- Admission: Train IC=+0.2426, Deflated=+0.2427, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.050 | 2017: +0.055 | 2018: +0.049 | 2019: +0.170 | 2020: +0.058 | 2021: +0.182 | 2022: +0.055 | 2023: +0.143 | 2024: +0.056 | 2025: +0.183 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.122 | 2016: +0.129 | 2017: +0.101 | 2018: +0.188 | 2019: +0.299 | 2020: +0.087 | 2021: +0.236 | 2022: +0.175 | 2023: +0.429 | 2024: +0.298 | 2025: +0.203 | 2026: -0.190
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=1.09
- Early IC=+0.1095, Recent IC=+0.1195, 1st-half IC=+0.1093, 2nd-half IC=+0.1111, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.171, Q3_mid=+0.140, Q4=+0.115, Q5_high_vol=+0.084

**`combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0572, Sharpe=-1.0459)
- Admission: Train IC=+0.2567, Deflated=+0.2567, IR=0.84, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.018 | 2017: +0.016 | 2018: +0.050 | 2019: +0.132 | 2020: +0.054 | 2021: +0.144 | 2022: +0.071 | 2023: +0.196 | 2024: +0.078 | 2025: +0.206 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.178 | 2017: +0.104 | 2018: +0.021 | 2019: +0.278 | 2020: +0.168 | 2021: +0.151 | 2022: +0.380 | 2023: +0.504 | 2024: +0.190 | 2025: +0.216 | 2026: -0.202
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.74, Recency ratio=1.55
- Early IC=+0.0911, Recent IC=+0.1417, 1st-half IC=+0.0823, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.149, Q3_mid=+0.126, Q4=+0.097, Q5_high_vol=+0.114

**`combo_sig_product__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0148, Sharpe=-1.0032)
- Admission: Train IC=+0.2553, Deflated=+0.2552, IR=0.58, Mono=0.75, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.068 | 2017: +0.037 | 2018: +0.154 | 2019: +0.138 | 2020: +0.129 | 2021: +0.150 | 2022: +0.067 | 2023: +0.190 | 2024: +0.054 | 2025: +0.168 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.279 | 2016: -0.106 | 2017: -0.059 | 2018: +0.221 | 2019: +0.426 | 2020: +0.251 | 2021: +0.207 | 2022: +0.050 | 2023: +0.359 | 2024: +0.150 | 2025: +0.367 | 2026: +0.203
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.76
- Early IC=+0.1457, Recent IC=+0.1111, 1st-half IC=+0.1420, 2nd-half IC=+0.1200, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.135, Q3_mid=+0.119, Q4=+0.122, Q5_high_vol=+0.143

**`combo_mean__bar_body_rng_0__rally_strength_max`** (Lock IC=-0.0159, Sharpe=-0.9259)
- Admission: Train IC=+0.2393, Deflated=+0.2395, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.107 | 2017: -0.003 | 2018: +0.104 | 2019: +0.194 | 2020: +0.099 | 2021: +0.169 | 2022: +0.036 | 2023: +0.124 | 2024: +0.049 | 2025: +0.173 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.245 | 2016: -0.046 | 2017: -0.118 | 2018: +0.292 | 2019: +0.448 | 2020: -0.005 | 2021: +0.194 | 2022: +0.119 | 2023: +0.367 | 2024: +0.246 | 2025: +0.338 | 2026: -0.130
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.75
- Early IC=+0.1486, Recent IC=+0.1111, 1st-half IC=+0.1300, 2nd-half IC=+0.1004, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.154, Q3_mid=+0.171, Q4=+0.084, Q5_high_vol=+0.095

**`combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0526, Sharpe=-0.9121)
- Admission: Train IC=+0.1870, Deflated=+0.1866, IR=0.57, Mono=0.73, p=0.0004, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.102 | 2017: +0.080 | 2018: +0.067 | 2019: +0.156 | 2020: +0.076 | 2021: +0.159 | 2022: +0.045 | 2023: +0.170 | 2024: +0.068 | 2025: +0.165 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.091 | 2016: +0.091 | 2017: +0.136 | 2018: +0.132 | 2019: +0.397 | 2020: +0.002 | 2021: +0.314 | 2022: +0.002 | 2023: +0.234 | 2024: +0.096 | 2025: +0.255 | 2026: -0.074
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.05
- Early IC=+0.1112, Recent IC=+0.1167, 1st-half IC=+0.1080, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76, neg years=1)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.162, Q3_mid=+0.106, Q4=+0.100, Q5_high_vol=+0.103

**`combo_max__max_up_ret__volume_price_confirmation`** (Lock IC=-0.0151, Sharpe=-0.8921)
- Admission: Train IC=+0.2441, Deflated=+0.2442, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.112 | 2017: +0.044 | 2018: +0.116 | 2019: +0.179 | 2020: +0.166 | 2021: +0.145 | 2022: +0.079 | 2023: +0.100 | 2024: +0.071 | 2025: +0.127 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.123 | 2017: +0.042 | 2018: +0.259 | 2019: +0.271 | 2020: +0.164 | 2021: +0.324 | 2022: +0.163 | 2023: +0.356 | 2024: +0.339 | 2025: +0.079 | 2026: -0.056
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.67
- Early IC=+0.1474, Recent IC=+0.0992, 1st-half IC=+0.1482, 2nd-half IC=+0.0980, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.133, Q3_mid=+0.128, Q4=+0.117, Q5_high_vol=+0.145

**`combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret`** (Lock IC=-0.0423, Sharpe=-0.8829)
- Admission: Train IC=+0.1516, Deflated=+0.1507, IR=0.59, Mono=0.71, p=0.0038, MaxCorr=0.59
- Yearly Linear ICs: 2015: +0.120 | 2016: +0.067 | 2017: -0.045 | 2018: +0.066 | 2019: +0.055 | 2020: +0.121 | 2021: +0.112 | 2022: +0.162 | 2023: +0.224 | 2024: +0.013 | 2025: +0.123 | 2026: -0.042
- Yearly Tail ICs:   2015: -0.047 | 2016: +0.112 | 2017: -0.128 | 2018: +0.226 | 2019: +0.139 | 2020: +0.243 | 2021: +0.133 | 2022: +0.293 | 2023: +0.301 | 2024: -0.028 | 2025: +0.011 | 2026: -0.035
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=1.37, Recency ratio=1.12
- Early IC=+0.0608, Recent IC=+0.0680, 1st-half IC=+0.0917, 2nd-half IC=+0.1252, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=0.78, neg years=0)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.145, Q3_mid=+0.108, Q4=+0.087, Q5_high_vol=+0.099

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

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0570, Sharpe=-0.3265)
- Admission: Train IC=+0.2368, Deflated=+0.2369, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.093 | 2017: +0.067 | 2018: +0.066 | 2019: +0.189 | 2020: +0.059 | 2021: +0.197 | 2022: +0.058 | 2023: +0.172 | 2024: +0.094 | 2025: +0.172 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.042 | 2016: +0.036 | 2017: +0.148 | 2018: +0.180 | 2019: +0.343 | 2020: +0.115 | 2021: +0.263 | 2022: +0.121 | 2023: +0.434 | 2024: +0.181 | 2025: +0.218 | 2026: -0.058
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.04
- Early IC=+0.1278, Recent IC=+0.1328, 1st-half IC=+0.1230, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.169, Q3_mid=+0.136, Q4=+0.119, Q5_high_vol=+0.122

**`combo_max__bar_body_rng_0__rally_strength_max`** (Lock IC=-0.0448, Sharpe=+0.0816)
- Admission: Train IC=+0.2422, Deflated=+0.2424, IR=0.58, Mono=0.69, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.123 | 2017: +0.012 | 2018: +0.079 | 2019: +0.144 | 2020: +0.103 | 2021: +0.167 | 2022: +0.039 | 2023: +0.132 | 2024: +0.023 | 2025: +0.211 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.367 | 2016: -0.077 | 2017: -0.002 | 2018: +0.189 | 2019: +0.448 | 2020: +0.066 | 2021: +0.249 | 2022: +0.160 | 2023: +0.300 | 2024: +0.246 | 2025: +0.405 | 2026: +0.044
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=1.05
- Early IC=+0.1116, Recent IC=+0.1169, 1st-half IC=+0.1147, 2nd-half IC=+0.1013, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.145, Q3_mid=+0.136, Q4=+0.101, Q5_high_vol=+0.098

**`combo_max__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=-0.0185, Sharpe=+0.1961)
- Admission: Train IC=+0.2259, Deflated=+0.2266, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.086 | 2017: +0.031 | 2018: +0.101 | 2019: +0.188 | 2020: +0.175 | 2021: +0.140 | 2022: +0.037 | 2023: +0.129 | 2024: +0.058 | 2025: +0.155 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.486 | 2016: -0.164 | 2017: +0.100 | 2018: +0.220 | 2019: +0.365 | 2020: +0.264 | 2021: +0.192 | 2022: +0.084 | 2023: +0.206 | 2024: +0.246 | 2025: +0.228 | 2026: +0.260
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.74
- Early IC=+0.1447, Recent IC=+0.1067, 1st-half IC=+0.1419, 2nd-half IC=+0.1001, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.147, Q3_mid=+0.180, Q4=+0.079, Q5_high_vol=+0.119

**`combo_max__opening_drive_thrust_ratio__rally_strength_max`** (Lock IC=-0.0405, Sharpe=+0.3146)
- Admission: Train IC=+0.2462, Deflated=+0.2465, IR=0.61, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.036 | 2017: +0.024 | 2018: +0.061 | 2019: +0.175 | 2020: +0.096 | 2021: +0.145 | 2022: +0.041 | 2023: +0.160 | 2024: +0.073 | 2025: +0.189 | 2026: -0.041
- Yearly Tail ICs:   2015: +0.384 | 2016: +0.042 | 2017: -0.015 | 2018: +0.104 | 2019: +0.411 | 2020: +0.175 | 2021: +0.259 | 2022: +0.066 | 2023: +0.346 | 2024: +0.335 | 2025: +0.284 | 2026: +0.056
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=1.11
- Early IC=+0.1181, Recent IC=+0.1308, 1st-half IC=+0.1123, 2nd-half IC=+0.1172, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.158, Q3_mid=+0.122, Q4=+0.128, Q5_high_vol=+0.106

**`combo_rank_min__opening_drive_thrust_ratio__rally_strength_max`** (Lock IC=-0.0825, Sharpe=+0.4014)
- Admission: Train IC=+0.2430, Deflated=+0.2428, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.138 | 2016: -0.014 | 2017: +0.043 | 2018: +0.071 | 2019: +0.151 | 2020: +0.020 | 2021: +0.201 | 2022: +0.040 | 2023: +0.144 | 2024: +0.066 | 2025: +0.170 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.279 | 2016: -0.126 | 2017: +0.073 | 2018: +0.159 | 2019: +0.304 | 2020: +0.149 | 2021: +0.334 | 2022: +0.188 | 2023: +0.383 | 2024: +0.072 | 2025: +0.091 | 2026: -0.042
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.16, Recency ratio=1.03
- Early IC=+0.1195, Recent IC=+0.1232, 1st-half IC=+0.1016, 2nd-half IC=+0.1176, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90, neg years=1)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.157, Q3_mid=+0.156, Q4=+0.121, Q5_high_vol=+0.090

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

**`combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0709, Sharpe=-1.0140)
- Admission: Train IC=+0.2116, Deflated=+0.2114, IR=0.56, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.096 | 2017: -0.002 | 2018: +0.188 | 2019: +0.108 | 2020: +0.040 | 2021: +0.145 | 2022: +0.058 | 2023: +0.080 | 2024: +0.009 | 2025: +0.070 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.088 | 2016: -0.003 | 2017: -0.126 | 2018: +0.342 | 2019: +0.206 | 2020: +0.154 | 2021: +0.319 | 2022: +0.191 | 2023: +0.012 | 2024: +0.143 | 2025: +0.265 | 2026: +0.103
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.27
- Early IC=+0.1480, Recent IC=+0.0393, 1st-half IC=+0.1188, 2nd-half IC=+0.0638, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.069, Q3_mid=+0.025, Q4=+0.077, Q5_high_vol=+0.206

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0449, Sharpe=-0.4434)
- Admission: Train IC=+0.2156, Deflated=+0.2157, IR=0.57, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.114 | 2017: +0.001 | 2018: +0.209 | 2019: +0.104 | 2020: +0.047 | 2021: +0.143 | 2022: +0.084 | 2023: +0.106 | 2024: +0.017 | 2025: +0.066 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.122 | 2017: +0.031 | 2018: +0.276 | 2019: +0.240 | 2020: +0.156 | 2021: +0.436 | 2022: +0.268 | 2023: +0.063 | 2024: +0.162 | 2025: +0.227 | 2026: +0.111
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.26
- Early IC=+0.1567, Recent IC=+0.0412, 1st-half IC=+0.1264, 2nd-half IC=+0.0747, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.075, Q3_mid=+0.036, Q4=+0.075, Q5_high_vol=+0.229

**`combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0005, Sharpe=-0.7605)
- Admission: Train IC=+0.2501, Deflated=+0.2501, IR=0.86, Mono=0.82, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.095 | 2017: +0.021 | 2018: +0.206 | 2019: +0.107 | 2020: +0.039 | 2021: +0.137 | 2022: +0.068 | 2023: +0.128 | 2024: +0.016 | 2025: +0.091 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.019 | 2017: -0.030 | 2018: +0.318 | 2019: +0.156 | 2020: +0.270 | 2021: +0.383 | 2022: +0.324 | 2023: +0.229 | 2024: +0.151 | 2025: +0.278 | 2026: +0.096
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.34
- Early IC=+0.1564, Recent IC=+0.0536, 1st-half IC=+0.1257, 2nd-half IC=+0.0799, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.082, Q3_mid=+0.053, Q4=+0.099, Q5_high_vol=+0.205

### 500ETF — `single` Median Features

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1105, Sharpe=-0.0489)
- Admission: Train IC=+0.2253, Deflated=+0.2248, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.092 | 2017: +0.221 | 2018: +0.181 | 2019: +0.125 | 2020: +0.169 | 2021: +0.085 | 2022: +0.064 | 2023: +0.064 | 2024: +0.088 | 2025: +0.125 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.093 | 2017: +0.272 | 2018: +0.375 | 2019: +0.310 | 2020: +0.203 | 2021: +0.170 | 2022: +0.224 | 2023: -0.025 | 2024: +0.194 | 2025: +0.141 | 2026: +0.143
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.70
- Early IC=+0.1532, Recent IC=+0.1067, 1st-half IC=+0.1411, 2nd-half IC=+0.0883, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.023, Q3_mid=+0.104, Q4=+0.134, Q5_high_vol=+0.164

**`combo_clamp_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0988, Sharpe=-1.7785)
- Admission: Train IC=+0.2389, Deflated=+0.2402, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.323 | 2016: +0.111 | 2017: +0.189 | 2018: +0.218 | 2019: +0.122 | 2020: +0.148 | 2021: +0.153 | 2022: +0.060 | 2023: +0.093 | 2024: +0.126 | 2025: +0.012 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.442 | 2016: +0.250 | 2017: +0.401 | 2018: +0.324 | 2019: +0.401 | 2020: +0.165 | 2021: +0.163 | 2022: +0.195 | 2023: +0.074 | 2024: +0.214 | 2025: +0.011 | 2026: +0.015
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.41
- Early IC=+0.1699, Recent IC=+0.0692, 1st-half IC=+0.1524, 2nd-half IC=+0.0795, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.003, Q3_mid=+0.087, Q4=+0.129, Q5_high_vol=+0.210

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0727, Sharpe=-0.4830)
- Admission: Train IC=+0.2243, Deflated=+0.2234, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.124 | 2017: +0.150 | 2018: +0.156 | 2019: +0.097 | 2020: +0.138 | 2021: +0.058 | 2022: +0.125 | 2023: +0.072 | 2024: +0.090 | 2025: +0.111 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.236 | 2016: +0.259 | 2017: +0.235 | 2018: +0.337 | 2019: +0.292 | 2020: +0.180 | 2021: +0.120 | 2022: +0.248 | 2023: +0.178 | 2024: +0.198 | 2025: +0.119 | 2026: +0.107
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.80
- Early IC=+0.1265, Recent IC=+0.1008, 1st-half IC=+0.1204, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.078, Q3_mid=+0.131, Q4=+0.083, Q5_high_vol=+0.158

**`combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction`** (Lock IC=+0.0600, Sharpe=-0.0172)
- Admission: Train IC=+0.2234, Deflated=+0.2223, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.066 | 2017: +0.203 | 2018: +0.080 | 2019: +0.015 | 2020: +0.120 | 2021: +0.016 | 2022: -0.005 | 2023: +0.093 | 2024: +0.066 | 2025: +0.135 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.248 | 2016: +0.204 | 2017: +0.255 | 2018: +0.334 | 2019: +0.077 | 2020: +0.331 | 2021: -0.021 | 2022: +0.076 | 2023: +0.011 | 2024: +0.385 | 2025: +0.276 | 2026: +0.154
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=1.15, Recency ratio=2.11
- Early IC=+0.0477, Recent IC=+0.1006, 1st-half IC=+0.0664, 2nd-half IC=+0.0764, Neg regimes=0/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.035, Q3_mid=+0.054, Q4=+0.097, Q5_high_vol=+0.107

**`combo_rel_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.0529, Sharpe=-1.5621)
- Admission: Train IC=+0.2185, Deflated=+0.2175, IR=0.63, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.090 | 2017: +0.221 | 2018: +0.175 | 2019: +0.153 | 2020: +0.148 | 2021: +0.105 | 2022: +0.082 | 2023: +0.116 | 2024: +0.124 | 2025: +0.156 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.010 | 2017: +0.242 | 2018: +0.223 | 2019: +0.244 | 2020: +0.217 | 2021: +0.128 | 2022: +0.232 | 2023: +0.245 | 2024: +0.194 | 2025: +0.104 | 2026: -0.071
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.85
- Early IC=+0.1642, Recent IC=+0.1397, 1st-half IC=+0.1458, 2nd-half IC=+0.1246, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.053, Q3_mid=+0.128, Q4=+0.143, Q5_high_vol=+0.199

**`combo_clamp_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.0514, Sharpe=-1.5211)
- Admission: Train IC=+0.2920, Deflated=+0.2912, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.068 | 2017: +0.243 | 2018: +0.195 | 2019: +0.134 | 2020: +0.157 | 2021: +0.085 | 2022: +0.095 | 2023: +0.129 | 2024: +0.128 | 2025: +0.155 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.358 | 2016: -0.015 | 2017: +0.220 | 2018: +0.337 | 2019: +0.280 | 2020: +0.382 | 2021: +0.160 | 2022: +0.302 | 2023: +0.296 | 2024: +0.286 | 2025: +0.201 | 2026: -0.132
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.86
- Early IC=+0.1643, Recent IC=+0.1415, 1st-half IC=+0.1445, 2nd-half IC=+0.1309, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.065, Q3_mid=+0.130, Q4=+0.146, Q5_high_vol=+0.192

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0350, Sharpe=-0.6199)
- Admission: Train IC=+0.2348, Deflated=+0.2340, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.103 | 2017: +0.203 | 2018: +0.098 | 2019: +0.071 | 2020: +0.126 | 2021: +0.118 | 2022: +0.059 | 2023: +0.103 | 2024: +0.132 | 2025: +0.123 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.276 | 2017: +0.289 | 2018: +0.349 | 2019: +0.081 | 2020: +0.218 | 2021: +0.217 | 2022: +0.222 | 2023: -0.029 | 2024: +0.406 | 2025: +0.202 | 2026: +0.197
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=1.06, Recency ratio=1.52
- Early IC=+0.0842, Recent IC=+0.1276, 1st-half IC=+0.1016, 2nd-half IC=+0.1074, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.062, Q3_mid=+0.125, Q4=+0.087, Q5_high_vol=+0.151

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum`** (Lock IC=+0.0277, Sharpe=-0.8653)
- Admission: Train IC=+0.2149, Deflated=+0.2142, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.129 | 2017: +0.174 | 2018: +0.210 | 2019: +0.106 | 2020: +0.162 | 2021: +0.094 | 2022: +0.133 | 2023: +0.087 | 2024: +0.096 | 2025: +0.137 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.349 | 2016: +0.299 | 2017: +0.262 | 2018: +0.372 | 2019: +0.200 | 2020: +0.257 | 2021: +0.224 | 2022: +0.280 | 2023: +0.155 | 2024: +0.212 | 2025: -0.045 | 2026: -0.062
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.74
- Early IC=+0.1578, Recent IC=+0.1163, 1st-half IC=+0.1463, 2nd-half IC=+0.1195, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.084, Q3_mid=+0.144, Q4=+0.112, Q5_high_vol=+0.195

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0177, Sharpe=-1.6384)
- Admission: Train IC=+0.1953, Deflated=+0.1954, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.129 | 2017: +0.226 | 2018: +0.242 | 2019: +0.166 | 2020: +0.180 | 2021: +0.134 | 2022: +0.082 | 2023: +0.080 | 2024: +0.143 | 2025: +0.094 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.358 | 2016: +0.162 | 2017: +0.252 | 2018: +0.444 | 2019: +0.223 | 2020: +0.240 | 2021: +0.156 | 2022: -0.026 | 2023: +0.150 | 2024: +0.279 | 2025: +0.013 | 2026: -0.291
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.58
- Early IC=+0.2044, Recent IC=+0.1183, 1st-half IC=+0.1773, 2nd-half IC=+0.1090, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.039, Q3_mid=+0.152, Q4=+0.126, Q5_high_vol=+0.245

**`combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.0175, Sharpe=-1.1506)
- Admission: Train IC=+0.2320, Deflated=+0.2306, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.075 | 2017: +0.193 | 2018: +0.138 | 2019: +0.080 | 2020: +0.127 | 2021: +0.056 | 2022: +0.085 | 2023: +0.068 | 2024: +0.099 | 2025: +0.126 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.110 | 2017: +0.268 | 2018: +0.242 | 2019: +0.231 | 2020: +0.197 | 2021: +0.213 | 2022: +0.337 | 2023: +0.193 | 2024: +0.230 | 2025: +0.207 | 2026: -0.053
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=1.04
- Early IC=+0.1089, Recent IC=+0.1129, 1st-half IC=+0.1047, 2nd-half IC=+0.1036, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.068, Q3_mid=+0.130, Q4=+0.094, Q5_high_vol=+0.133

**`combo_mean__first_bar_return__max_down_ret`** (Lock IC=+0.0117, Sharpe=-2.2371)
- Admission: Train IC=+0.2258, Deflated=+0.2255, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.103 | 2017: +0.227 | 2018: +0.202 | 2019: +0.132 | 2020: +0.121 | 2021: +0.082 | 2022: +0.071 | 2023: +0.054 | 2024: +0.128 | 2025: +0.132 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.043 | 2017: +0.264 | 2018: +0.377 | 2019: +0.188 | 2020: +0.192 | 2021: +0.285 | 2022: +0.190 | 2023: +0.137 | 2024: +0.250 | 2025: +0.177 | 2026: -0.251
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.78
- Early IC=+0.1671, Recent IC=+0.1297, 1st-half IC=+0.1301, 2nd-half IC=+0.1041, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.029, Q3_mid=+0.136, Q4=+0.132, Q5_high_vol=+0.158

**`combo_rank_min__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0095, Sharpe=-0.0517)
- Admission: Train IC=+0.2151, Deflated=+0.2143, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.075 | 2017: +0.191 | 2018: +0.189 | 2019: +0.131 | 2020: +0.076 | 2021: +0.068 | 2022: +0.049 | 2023: +0.067 | 2024: +0.109 | 2025: +0.131 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.070 | 2017: +0.308 | 2018: +0.297 | 2019: +0.272 | 2020: +0.175 | 2021: +0.291 | 2022: +0.185 | 2023: +0.210 | 2024: +0.119 | 2025: +0.147 | 2026: -0.075
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.78
- Early IC=+0.1575, Recent IC=+0.1231, 1st-half IC=+0.1149, 2nd-half IC=+0.0968, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.031, Q3_mid=+0.107, Q4=+0.121, Q5_high_vol=+0.149

**`combo_mean__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0078, Sharpe=-1.2156)
- Admission: Train IC=+0.2287, Deflated=+0.2284, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.100 | 2017: +0.225 | 2018: +0.233 | 2019: +0.144 | 2020: +0.147 | 2021: +0.137 | 2022: +0.071 | 2023: +0.092 | 2024: +0.138 | 2025: +0.110 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.580 | 2016: -0.000 | 2017: +0.196 | 2018: +0.174 | 2019: +0.353 | 2020: +0.085 | 2021: +0.438 | 2022: +0.120 | 2023: +0.090 | 2024: +0.228 | 2025: +0.158 | 2026: -0.049
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.66
- Early IC=+0.1883, Recent IC=+0.1237, 1st-half IC=+0.1608, 2nd-half IC=+0.1074, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.022, Q3_mid=+0.155, Q4=+0.158, Q5_high_vol=+0.192

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0077, Sharpe=-1.6646)
- Admission: Train IC=+0.1859, Deflated=+0.1860, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.098 | 2017: +0.254 | 2018: +0.239 | 2019: +0.142 | 2020: +0.131 | 2021: +0.079 | 2022: +0.098 | 2023: +0.041 | 2024: +0.124 | 2025: +0.098 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.006 | 2017: +0.199 | 2018: +0.408 | 2019: +0.110 | 2020: +0.233 | 2021: +0.218 | 2022: +0.164 | 2023: +0.240 | 2024: +0.241 | 2025: +0.034 | 2026: -0.250
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1905, Recent IC=+0.1110, 1st-half IC=+0.1432, 2nd-half IC=+0.1012, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.025, Q3_mid=+0.135, Q4=+0.139, Q5_high_vol=+0.172

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0028, Sharpe=-1.6259)
- Admission: Train IC=+0.2776, Deflated=+0.2782, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.102 | 2017: +0.141 | 2018: +0.284 | 2019: +0.177 | 2020: +0.174 | 2021: +0.172 | 2022: +0.055 | 2023: +0.093 | 2024: +0.158 | 2025: +0.058 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.423 | 2016: +0.093 | 2017: +0.312 | 2018: +0.607 | 2019: +0.292 | 2020: +0.045 | 2021: +0.311 | 2022: +0.215 | 2023: +0.097 | 2024: +0.280 | 2025: +0.147 | 2026: -0.132
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.47
- Early IC=+0.2304, Recent IC=+0.1078, 1st-half IC=+0.1916, 2nd-half IC=+0.1013, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.031, Q3_mid=+0.124, Q4=+0.144, Q5_high_vol=+0.268

**`combo_rank_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0003, Sharpe=-0.4714)
- Admission: Train IC=+0.2094, Deflated=+0.2094, IR=0.52, Mono=0.67, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.109 | 2017: +0.217 | 2018: +0.227 | 2019: +0.127 | 2020: +0.123 | 2021: +0.101 | 2022: +0.080 | 2023: +0.086 | 2024: +0.115 | 2025: +0.082 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.374 | 2016: +0.121 | 2017: +0.209 | 2018: +0.402 | 2019: +0.269 | 2020: +0.189 | 2021: +0.229 | 2022: +0.007 | 2023: +0.017 | 2024: +0.153 | 2025: +0.200 | 2026: -0.119
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.55
- Early IC=+0.1769, Recent IC=+0.0974, 1st-half IC=+0.1402, 2nd-half IC=+0.0974, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.035, Q3_mid=+0.120, Q4=+0.132, Q5_high_vol=+0.167

### 159915ETF — `single` Median Features

**`combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early`** (Lock IC=+0.1273, Sharpe=-0.4715)
- Admission: Train IC=+0.2047, Deflated=+0.2040, IR=0.45, Mono=0.68, p=0.0002, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.145 | 2016: +0.107 | 2017: -0.103 | 2018: +0.062 | 2019: +0.091 | 2020: +0.144 | 2021: +0.053 | 2022: +0.154 | 2023: +0.213 | 2024: +0.037 | 2025: +0.110 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.121 | 2017: -0.210 | 2018: +0.320 | 2019: +0.169 | 2020: +0.305 | 2021: +0.281 | 2022: +0.262 | 2023: +0.165 | 2024: +0.018 | 2025: +0.052 | 2026: +0.130
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.42, Recency ratio=0.96
- Early IC=+0.0766, Recent IC=+0.0736, 1st-half IC=+0.0895, 2nd-half IC=+0.1273, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=0.78)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.127, Q3_mid=+0.108, Q4=+0.096, Q5_high_vol=+0.125

**`combo_mean__max_up_ret__gap_pct`** (Lock IC=+0.1184, Sharpe=-0.2163)
- Admission: Train IC=+0.2274, Deflated=+0.2271, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.097 | 2017: +0.014 | 2018: +0.139 | 2019: +0.158 | 2020: +0.151 | 2021: +0.157 | 2022: +0.167 | 2023: +0.135 | 2024: +0.104 | 2025: +0.169 | 2026: +0.118
- Yearly Tail ICs:   2015: -0.046 | 2016: +0.276 | 2017: +0.065 | 2018: +0.343 | 2019: +0.304 | 2020: +0.168 | 2021: +0.352 | 2022: +0.182 | 2023: +0.043 | 2024: +0.244 | 2025: +0.068 | 2026: +0.223
- IC CV=0.14, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.92
- Early IC=+0.1483, Recent IC=+0.1366, 1st-half IC=+0.1618, 2nd-half IC=+0.1460, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.148, Q3_mid=+0.129, Q4=+0.175, Q5_high_vol=+0.180

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.1154, Sharpe=-0.0647)
- Admission: Train IC=+0.2178, Deflated=+0.2171, IR=0.56, Mono=0.73, p=0.0002, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.152 | 2017: -0.073 | 2018: +0.153 | 2019: +0.109 | 2020: +0.124 | 2021: +0.064 | 2022: +0.159 | 2023: +0.150 | 2024: +0.081 | 2025: +0.076 | 2026: +0.115
- Yearly Tail ICs:   2015: +0.126 | 2016: +0.243 | 2017: +0.051 | 2018: +0.348 | 2019: +0.183 | 2020: +0.377 | 2021: +0.189 | 2022: +0.357 | 2023: -0.018 | 2024: +0.160 | 2025: +0.063 | 2026: +0.197
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.99, Recency ratio=0.60
- Early IC=+0.1310, Recent IC=+0.0785, 1st-half IC=+0.1176, 2nd-half IC=+0.1162, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.132, Q3_mid=+0.116, Q4=+0.165, Q5_high_vol=+0.089

**`combo_rank_min__max_up_ret__directional_volume_signature`** (Lock IC=+0.0897, Sharpe=-0.0372)
- Admission: Train IC=+0.1909, Deflated=+0.1916, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.102 | 2017: +0.065 | 2018: +0.068 | 2019: +0.186 | 2020: +0.156 | 2021: +0.094 | 2022: +0.043 | 2023: +0.161 | 2024: +0.099 | 2025: +0.066 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.461 | 2016: +0.182 | 2017: +0.030 | 2018: +0.179 | 2019: +0.361 | 2020: +0.159 | 2021: +0.207 | 2022: +0.132 | 2023: +0.361 | 2024: +0.287 | 2025: +0.142 | 2026: +0.060
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.70
- Early IC=+0.1220, Recent IC=+0.0859, 1st-half IC=+0.1150, 2nd-half IC=+0.0895, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.140, Q3_mid=+0.069, Q4=+0.062, Q5_high_vol=+0.126

**`combo_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0888, Sharpe=-0.3243)
- Admission: Train IC=+0.2588, Deflated=+0.2591, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.202 | 2016: -0.002 | 2017: +0.011 | 2018: +0.028 | 2019: +0.152 | 2020: +0.059 | 2021: +0.147 | 2022: +0.074 | 2023: +0.134 | 2024: +0.068 | 2025: +0.164 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.017 | 2017: +0.132 | 2018: +0.225 | 2019: +0.351 | 2020: +0.184 | 2021: +0.230 | 2022: +0.205 | 2023: +0.307 | 2024: +0.320 | 2025: +0.173 | 2026: +0.209
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.35, Recency ratio=1.29
- Early IC=+0.0902, Recent IC=+0.1162, 1st-half IC=+0.0890, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.134, Q3_mid=+0.122, Q4=+0.108, Q5_high_vol=+0.105

**`combo_max__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.0866, Sharpe=-1.4591)
- Admission: Train IC=+0.1650, Deflated=+0.1643, IR=0.54, Mono=0.71, p=0.0014, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.091 | 2017: +0.015 | 2018: +0.141 | 2019: +0.117 | 2020: +0.070 | 2021: +0.160 | 2022: +0.132 | 2023: +0.111 | 2024: +0.033 | 2025: +0.109 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.077 | 2016: +0.014 | 2017: +0.282 | 2018: +0.385 | 2019: +0.138 | 2020: +0.029 | 2021: +0.349 | 2022: +0.119 | 2023: +0.165 | 2024: +0.185 | 2025: +0.199 | 2026: +0.128
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.55
- Early IC=+0.1291, Recent IC=+0.0712, 1st-half IC=+0.1215, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.107, Q3_mid=+0.112, Q4=+0.075, Q5_high_vol=+0.114

**`combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0844, Sharpe=-0.0130)
- Admission: Train IC=+0.2075, Deflated=+0.2076, IR=0.65, Mono=0.74, p=0.0002, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.140 | 2017: -0.006 | 2018: +0.057 | 2019: +0.185 | 2020: +0.165 | 2021: +0.110 | 2022: +0.073 | 2023: +0.063 | 2024: +0.124 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.181 | 2016: +0.136 | 2017: +0.163 | 2018: +0.166 | 2019: +0.189 | 2020: +0.082 | 2021: +0.388 | 2022: +0.173 | 2023: +0.109 | 2024: +0.234 | 2025: +0.329 | 2026: -0.078
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=1.06
- Early IC=+0.1205, Recent IC=+0.1283, 1st-half IC=+0.1234, 2nd-half IC=+0.1040, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.153, Q3_mid=+0.124, Q4=+0.091, Q5_high_vol=+0.079

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

**`combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0741, Sharpe=-1.3949)
- Admission: Train IC=+0.1788, Deflated=+0.1791, IR=0.59, Mono=0.70, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.126 | 2017: -0.023 | 2018: +0.069 | 2019: +0.169 | 2020: +0.166 | 2021: +0.112 | 2022: +0.076 | 2023: +0.094 | 2024: +0.137 | 2025: +0.121 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.137 | 2016: +0.056 | 2017: +0.215 | 2018: +0.085 | 2019: +0.222 | 2020: +0.090 | 2021: +0.360 | 2022: +0.153 | 2023: +0.191 | 2024: +0.322 | 2025: +0.138 | 2026: +0.055
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=1.08
- Early IC=+0.1193, Recent IC=+0.1289, 1st-half IC=+0.1248, 2nd-half IC=+0.1102, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.164, Q3_mid=+0.124, Q4=+0.082, Q5_high_vol=+0.096

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

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0578, Sharpe=-0.9696)
- Admission: Train IC=+0.2851, Deflated=+0.2849, IR=0.87, Mono=0.83, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.072 | 2017: -0.002 | 2018: +0.076 | 2019: +0.158 | 2020: +0.084 | 2021: +0.182 | 2022: +0.118 | 2023: +0.148 | 2024: +0.083 | 2025: +0.204 | 2026: +0.058
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.210 | 2017: +0.158 | 2018: +0.169 | 2019: +0.321 | 2020: +0.216 | 2021: +0.220 | 2022: +0.279 | 2023: +0.309 | 2024: +0.375 | 2025: +0.284 | 2026: +0.063
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.18, Recency ratio=1.23
- Early IC=+0.1171, Recent IC=+0.1435, 1st-half IC=+0.1236, 2nd-half IC=+0.1464, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.169, Q3_mid=+0.120, Q4=+0.155, Q5_high_vol=+0.151

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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0510, Sharpe=-0.4248)
- Admission: Train IC=+0.3045, Deflated=+0.3047, IR=0.86, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.151 | 2017: +0.006 | 2018: +0.158 | 2019: +0.211 | 2020: +0.164 | 2021: +0.173 | 2022: +0.125 | 2023: +0.140 | 2024: +0.067 | 2025: +0.180 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.029 | 2016: +0.196 | 2017: +0.052 | 2018: +0.310 | 2019: +0.337 | 2020: +0.239 | 2021: +0.349 | 2022: +0.261 | 2023: +0.291 | 2024: +0.396 | 2025: +0.223 | 2026: -0.087
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.67
- Early IC=+0.1844, Recent IC=+0.1235, 1st-half IC=+0.1708, 2nd-half IC=+0.1326, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.147, Q3_mid=+0.159, Q4=+0.141, Q5_high_vol=+0.169

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0426, Sharpe=-0.5756)
- Admission: Train IC=+0.2372, Deflated=+0.2381, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.124 | 2017: +0.031 | 2018: +0.087 | 2019: +0.188 | 2020: +0.124 | 2021: +0.164 | 2022: +0.126 | 2023: +0.154 | 2024: +0.046 | 2025: +0.175 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.178 | 2017: +0.118 | 2018: +0.272 | 2019: +0.239 | 2020: +0.126 | 2021: +0.407 | 2022: +0.228 | 2023: +0.208 | 2024: +0.171 | 2025: +0.261 | 2026: +0.067
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.80
- Early IC=+0.1372, Recent IC=+0.1104, 1st-half IC=+0.1389, 2nd-half IC=+0.1265, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.175, Q3_mid=+0.120, Q4=+0.105, Q5_high_vol=+0.136

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev`** (Lock IC=+0.0354, Sharpe=-0.7039)
- Admission: Train IC=+0.1722, Deflated=+0.1726, IR=0.54, Mono=0.67, p=0.0010, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.065 | 2017: +0.036 | 2018: +0.126 | 2019: +0.173 | 2020: +0.116 | 2021: +0.098 | 2022: +0.072 | 2023: +0.104 | 2024: +0.057 | 2025: +0.096 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.021 | 2017: +0.250 | 2018: +0.227 | 2019: +0.091 | 2020: +0.193 | 2021: +0.159 | 2022: +0.300 | 2023: +0.167 | 2024: +0.175 | 2025: +0.052 | 2026: +0.071
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.51
- Early IC=+0.1497, Recent IC=+0.0766, 1st-half IC=+0.1250, 2nd-half IC=+0.0786, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.093, Q3_mid=+0.098, Q4=+0.165, Q5_high_vol=+0.056

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0307, Sharpe=-1.8947)
- Admission: Train IC=+0.2170, Deflated=+0.2173, IR=0.67, Mono=0.72, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.104 | 2017: +0.014 | 2018: +0.044 | 2019: +0.121 | 2020: +0.146 | 2021: +0.148 | 2022: +0.085 | 2023: +0.154 | 2024: +0.104 | 2025: +0.189 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.053 | 2016: +0.148 | 2017: +0.080 | 2018: +0.223 | 2019: +0.256 | 2020: +0.115 | 2021: +0.434 | 2022: +0.197 | 2023: +0.154 | 2024: +0.299 | 2025: +0.162 | 2026: -0.109
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=1.78
- Early IC=+0.0824, Recent IC=+0.1465, 1st-half IC=+0.1208, 2nd-half IC=+0.1334, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.181, Q3_mid=+0.115, Q4=+0.110, Q5_high_vol=+0.126

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0262, Sharpe=-1.0933)
- Admission: Train IC=+0.1827, Deflated=+0.1822, IR=0.55, Mono=0.67, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.060 | 2017: +0.036 | 2018: +0.076 | 2019: +0.136 | 2020: +0.071 | 2021: +0.178 | 2022: +0.142 | 2023: +0.149 | 2024: +0.079 | 2025: +0.132 | 2026: +0.026
- Yearly Tail ICs:   2015: -0.094 | 2016: +0.164 | 2017: +0.098 | 2018: +0.225 | 2019: +0.219 | 2020: +0.022 | 2021: +0.389 | 2022: +0.195 | 2023: +0.254 | 2024: +0.256 | 2025: +0.080 | 2026: -0.094
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.99
- Early IC=+0.1063, Recent IC=+0.1052, 1st-half IC=+0.1141, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.128, Q3_mid=+0.112, Q4=+0.134, Q5_high_vol=+0.127

**`combo_mean__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.0262, Sharpe=-1.2196)
- Admission: Train IC=+0.2868, Deflated=+0.2873, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.070 | 2017: +0.055 | 2018: +0.089 | 2019: +0.166 | 2020: +0.144 | 2021: +0.108 | 2022: +0.074 | 2023: +0.150 | 2024: +0.081 | 2025: +0.166 | 2026: +0.026
- Yearly Tail ICs:   2015: +0.408 | 2016: -0.193 | 2017: +0.013 | 2018: +0.305 | 2019: +0.344 | 2020: +0.154 | 2021: +0.193 | 2022: +0.136 | 2023: +0.479 | 2024: +0.223 | 2025: +0.331 | 2026: -0.029
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=0.97
- Early IC=+0.1274, Recent IC=+0.1236, 1st-half IC=+0.1136, 2nd-half IC=+0.1230, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.142, Q3_mid=+0.128, Q4=+0.081, Q5_high_vol=+0.138

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0212, Sharpe=-1.1311)
- Admission: Train IC=+0.1980, Deflated=+0.1967, IR=0.63, Mono=0.72, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.139 | 2017: -0.014 | 2018: +0.123 | 2019: +0.141 | 2020: +0.114 | 2021: +0.165 | 2022: +0.157 | 2023: +0.104 | 2024: +0.058 | 2025: +0.142 | 2026: +0.021
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.182 | 2017: +0.117 | 2018: +0.337 | 2019: +0.159 | 2020: +0.096 | 2021: +0.473 | 2022: +0.139 | 2023: +0.241 | 2024: +0.283 | 2025: +0.056 | 2026: -0.146
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.76
- Early IC=+0.1325, Recent IC=+0.1004, 1st-half IC=+0.1335, 2nd-half IC=+0.1225, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.102, Q3_mid=+0.149, Q4=+0.121, Q5_high_vol=+0.120

**`bar_body_rng_0`** (Lock IC=+0.0207, Sharpe=-0.3858)
- Admission: Train IC=+0.2273, Deflated=+0.2279, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.151 | 2017: -0.020 | 2018: +0.141 | 2019: +0.203 | 2020: +0.134 | 2021: +0.136 | 2022: +0.062 | 2023: +0.141 | 2024: +0.047 | 2025: +0.158 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.308 | 2016: -0.108 | 2017: -0.022 | 2018: +0.220 | 2019: +0.459 | 2020: +0.173 | 2021: +0.164 | 2022: +0.076 | 2023: +0.316 | 2024: +0.127 | 2025: +0.347 | 2026: +0.011
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.1722, Recent IC=+0.1027, 1st-half IC=+0.1426, 2nd-half IC=+0.1038, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.131, Q3_mid=+0.131, Q4=+0.081, Q5_high_vol=+0.128

**`combo_ifelse__gap_pct__max_up_ret__first_bar_return`** (Lock IC=+0.0162, Sharpe=-1.2979)
- Admission: Train IC=+0.1906, Deflated=+0.1909, IR=0.73, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.145 | 2017: +0.053 | 2018: +0.126 | 2019: +0.141 | 2020: +0.120 | 2021: +0.137 | 2022: +0.080 | 2023: +0.158 | 2024: +0.017 | 2025: +0.120 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.097 | 2017: +0.258 | 2018: +0.256 | 2019: +0.171 | 2020: +0.058 | 2021: +0.331 | 2022: +0.142 | 2023: +0.296 | 2024: +0.154 | 2025: +0.216 | 2026: +0.040
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.51
- Early IC=+0.1337, Recent IC=+0.0686, 1st-half IC=+0.1232, 2nd-half IC=+0.0941, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.129, Q3_mid=+0.100, Q4=+0.072, Q5_high_vol=+0.113

**`combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration`** (Lock IC=+0.0109, Sharpe=-1.8509)
- Admission: Train IC=+0.2051, Deflated=+0.2057, IR=0.45, Mono=0.66, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.102 | 2017: +0.028 | 2018: +0.161 | 2019: +0.212 | 2020: +0.123 | 2021: +0.114 | 2022: +0.093 | 2023: +0.140 | 2024: +0.071 | 2025: +0.109 | 2026: +0.011
- Yearly Tail ICs:   2015: +0.277 | 2016: -0.051 | 2017: +0.092 | 2018: +0.294 | 2019: +0.385 | 2020: +0.012 | 2021: +0.247 | 2022: +0.045 | 2023: +0.244 | 2024: +0.208 | 2025: +0.358 | 2026: -0.277
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.48
- Early IC=+0.1866, Recent IC=+0.0901, 1st-half IC=+0.1361, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.116, Q3_mid=+0.108, Q4=+0.096, Q5_high_vol=+0.157

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
- Admission: Train IC=+0.2113, Deflated=+0.2119, IR=0.52, Mono=0.71, p=0.0000, MaxCorr=0.95
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

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0815, Sharpe=+2.0046)
- Admission: Train IC=+0.2205, Deflated=+0.2202, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.094 | 2017: +0.247 | 2018: +0.225 | 2019: +0.151 | 2020: +0.192 | 2021: +0.119 | 2022: +0.077 | 2023: +0.084 | 2024: +0.126 | 2025: +0.118 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.054 | 2017: +0.195 | 2018: +0.368 | 2019: +0.305 | 2020: +0.211 | 2021: +0.265 | 2022: +0.122 | 2023: +0.056 | 2024: +0.187 | 2025: +0.086 | 2026: +0.164
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.65
- Early IC=+0.1880, Recent IC=+0.1220, 1st-half IC=+0.1724, 2nd-half IC=+0.1096, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.037, Q3_mid=+0.146, Q4=+0.157, Q5_high_vol=+0.207

**`combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.0765, Sharpe=+1.5322)
- Admission: Train IC=+0.2011, Deflated=+0.1999, IR=0.50, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.061 | 2017: +0.199 | 2018: +0.089 | 2019: +0.066 | 2020: +0.087 | 2021: +0.059 | 2022: +0.054 | 2023: +0.092 | 2024: +0.128 | 2025: +0.113 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.289 | 2016: +0.153 | 2017: +0.329 | 2018: +0.306 | 2019: +0.115 | 2020: +0.248 | 2021: +0.024 | 2022: +0.244 | 2023: +0.114 | 2024: +0.334 | 2025: +0.034 | 2026: +0.321
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.31, Recency ratio=1.55
- Early IC=+0.0774, Recent IC=+0.1204, 1st-half IC=+0.0779, 2nd-half IC=+0.1024, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.078, Q2=+0.056, Q3_mid=+0.112, Q4=+0.094, Q5_high_vol=+0.122

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1278, Sharpe=+1.3992)
- Admission: Train IC=+0.2092, Deflated=+0.2085, IR=0.54, Mono=0.68, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.123 | 2017: +0.190 | 2018: +0.164 | 2019: +0.148 | 2020: +0.145 | 2021: +0.100 | 2022: +0.057 | 2023: +0.049 | 2024: +0.096 | 2025: +0.106 | 2026: +0.128
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.158 | 2017: +0.220 | 2018: +0.292 | 2019: +0.405 | 2020: +0.134 | 2021: +0.241 | 2022: +0.121 | 2023: -0.076 | 2024: +0.215 | 2025: +0.193 | 2026: +0.357
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.65
- Early IC=+0.1557, Recent IC=+0.1013, 1st-half IC=+0.1384, 2nd-half IC=+0.0846, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.010, Q3_mid=+0.109, Q4=+0.131, Q5_high_vol=+0.153

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0876, Sharpe=+1.1299)
- Admission: Train IC=+0.2566, Deflated=+0.2568, IR=0.92, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.076 | 2017: +0.229 | 2018: +0.223 | 2019: +0.178 | 2020: +0.146 | 2021: +0.110 | 2022: +0.031 | 2023: +0.079 | 2024: +0.128 | 2025: +0.124 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.113 | 2017: +0.330 | 2018: +0.509 | 2019: +0.290 | 2020: +0.209 | 2021: +0.215 | 2022: +0.151 | 2023: +0.199 | 2024: +0.263 | 2025: +0.262 | 2026: +0.237
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.63
- Early IC=+0.2004, Recent IC=+0.1259, 1st-half IC=+0.1662, 2nd-half IC=+0.0948, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.019, Q3_mid=+0.122, Q4=+0.163, Q5_high_vol=+0.205

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.0674, Sharpe=+1.0606)
- Admission: Train IC=+0.2228, Deflated=+0.2222, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.116 | 2017: +0.229 | 2018: +0.213 | 2019: +0.142 | 2020: +0.186 | 2021: +0.125 | 2022: +0.094 | 2023: +0.080 | 2024: +0.131 | 2025: +0.106 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.221 | 2017: +0.273 | 2018: +0.397 | 2019: +0.325 | 2020: +0.129 | 2021: +0.233 | 2022: +0.331 | 2023: +0.159 | 2024: +0.226 | 2025: +0.008 | 2026: +0.077
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.67
- Early IC=+0.1774, Recent IC=+0.1184, 1st-half IC=+0.1666, 2nd-half IC=+0.1119, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.064, Q3_mid=+0.149, Q4=+0.135, Q5_high_vol=+0.211

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0849, Sharpe=+0.9197)
- Admission: Train IC=+0.2157, Deflated=+0.2156, IR=0.54, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.068 | 2017: +0.192 | 2018: +0.151 | 2019: +0.175 | 2020: +0.115 | 2021: +0.088 | 2022: +0.034 | 2023: +0.063 | 2024: +0.109 | 2025: +0.131 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.125 | 2017: +0.237 | 2018: +0.379 | 2019: +0.339 | 2020: +0.227 | 2021: +0.058 | 2022: +0.122 | 2023: +0.116 | 2024: +0.312 | 2025: +0.130 | 2026: +0.185
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.74
- Early IC=+0.1628, Recent IC=+0.1198, 1st-half IC=+0.1279, 2nd-half IC=+0.0850, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.008, Q3_mid=+0.084, Q4=+0.130, Q5_high_vol=+0.163

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0955, Sharpe=+0.7908)
- Admission: Train IC=+0.2531, Deflated=+0.2531, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.116 | 2017: +0.223 | 2018: +0.204 | 2019: +0.159 | 2020: +0.162 | 2021: +0.125 | 2022: +0.044 | 2023: +0.097 | 2024: +0.106 | 2025: +0.133 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.195 | 2017: +0.227 | 2018: +0.405 | 2019: +0.246 | 2020: +0.335 | 2021: +0.177 | 2022: +0.041 | 2023: +0.162 | 2024: +0.223 | 2025: +0.257 | 2026: +0.178
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.67
- Early IC=+0.1799, Recent IC=+0.1202, 1st-half IC=+0.1577, 2nd-half IC=+0.0995, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.005, Q3_mid=+0.107, Q4=+0.144, Q5_high_vol=+0.206

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1016, Sharpe=+0.5964)
- Admission: Train IC=+0.2533, Deflated=+0.2535, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.312 | 2016: +0.096 | 2017: +0.217 | 2018: +0.211 | 2019: +0.151 | 2020: +0.129 | 2021: +0.127 | 2022: +0.046 | 2023: +0.090 | 2024: +0.104 | 2025: +0.117 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.264 | 2016: +0.245 | 2017: +0.285 | 2018: +0.452 | 2019: +0.340 | 2020: +0.323 | 2021: +0.044 | 2022: +0.038 | 2023: +0.143 | 2024: +0.269 | 2025: +0.121 | 2026: +0.195
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.61
- Early IC=+0.1811, Recent IC=+0.1108, 1st-half IC=+0.1523, 2nd-half IC=+0.0931, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.142, Q2=-0.001, Q3_mid=+0.090, Q4=+0.144, Q5_high_vol=+0.191

**`combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0733, Sharpe=+0.5393)
- Admission: Train IC=+0.2590, Deflated=+0.2585, IR=0.81, Mono=0.75, p=0.0000, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.070 | 2017: +0.211 | 2018: +0.174 | 2019: +0.130 | 2020: +0.109 | 2021: +0.111 | 2022: +0.047 | 2023: +0.101 | 2024: +0.119 | 2025: +0.138 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.296 | 2016: +0.109 | 2017: +0.285 | 2018: +0.371 | 2019: +0.304 | 2020: +0.198 | 2021: +0.094 | 2022: +0.147 | 2023: +0.273 | 2024: +0.331 | 2025: +0.238 | 2026: +0.197
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.85
- Early IC=+0.1518, Recent IC=+0.1286, 1st-half IC=+0.1286, 2nd-half IC=+0.1037, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.034, Q3_mid=+0.098, Q4=+0.138, Q5_high_vol=+0.165

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0617, Sharpe=+0.3905)
- Admission: Train IC=+0.2152, Deflated=+0.2149, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.298 | 2016: +0.138 | 2017: +0.218 | 2018: +0.251 | 2019: +0.141 | 2020: +0.163 | 2021: +0.125 | 2022: +0.104 | 2023: +0.082 | 2024: +0.117 | 2025: +0.105 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.206 | 2017: +0.174 | 2018: +0.455 | 2019: +0.173 | 2020: +0.251 | 2021: +0.257 | 2022: +0.121 | 2023: +0.045 | 2024: +0.090 | 2025: +0.049 | 2026: +0.117
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.57
- Early IC=+0.1959, Recent IC=+0.1112, 1st-half IC=+0.1695, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.042, Q3_mid=+0.115, Q4=+0.147, Q5_high_vol=+0.228

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0`** (Lock IC=+0.0419, Sharpe=+0.3646)
- Admission: Train IC=+0.2328, Deflated=+0.2321, IR=0.76, Mono=0.78, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.125 | 2017: +0.173 | 2018: +0.212 | 2019: +0.127 | 2020: +0.145 | 2021: +0.102 | 2022: +0.108 | 2023: +0.077 | 2024: +0.108 | 2025: +0.137 | 2026: +0.042
- Yearly Tail ICs:   2015: +0.289 | 2016: +0.111 | 2017: +0.216 | 2018: +0.380 | 2019: +0.179 | 2020: +0.230 | 2021: +0.159 | 2022: +0.302 | 2023: +0.251 | 2024: +0.238 | 2025: +0.017 | 2026: +0.089
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.72
- Early IC=+0.1693, Recent IC=+0.1221, 1st-half IC=+0.1489, 2nd-half IC=+0.1135, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.059, Q3_mid=+0.138, Q4=+0.126, Q5_high_vol=+0.184

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.0571, Sharpe=+0.3372)
- Admission: Train IC=+0.2573, Deflated=+0.2569, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.089 | 2017: +0.215 | 2018: +0.189 | 2019: +0.136 | 2020: +0.152 | 2021: +0.150 | 2022: +0.044 | 2023: +0.100 | 2024: +0.142 | 2025: +0.113 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.220 | 2017: +0.350 | 2018: +0.463 | 2019: +0.292 | 2020: +0.246 | 2021: +0.237 | 2022: +0.207 | 2023: +0.180 | 2024: +0.355 | 2025: +0.033 | 2026: +0.277
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.79
- Early IC=+0.1623, Recent IC=+0.1276, 1st-half IC=+0.1579, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.042, Q3_mid=+0.150, Q4=+0.129, Q5_high_vol=+0.210

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0846, Sharpe=+0.3115)
- Admission: Train IC=+0.2444, Deflated=+0.2450, IR=0.69, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.329 | 2016: +0.096 | 2017: +0.223 | 2018: +0.179 | 2019: +0.155 | 2020: +0.154 | 2021: +0.114 | 2022: +0.041 | 2023: +0.098 | 2024: +0.105 | 2025: +0.104 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.123 | 2017: +0.156 | 2018: +0.466 | 2019: +0.266 | 2020: +0.283 | 2021: +0.178 | 2022: +0.126 | 2023: +0.099 | 2024: +0.257 | 2025: +0.119 | 2026: +0.119
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.63
- Early IC=+0.1669, Recent IC=+0.1044, 1st-half IC=+0.1487, 2nd-half IC=+0.0871, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.025, Q3_mid=+0.111, Q4=+0.123, Q5_high_vol=+0.190

### 159915ETF — `single` True Positives

**`combo_rank_min__limit_down_proximity_early__volume_price_confirmation`** (Lock IC=+0.1801, Sharpe=+3.6713)
- Admission: Train IC=+0.2159, Deflated=+0.2161, IR=0.64, Mono=0.73, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.017 | 2017: -0.001 | 2018: +0.104 | 2019: +0.182 | 2020: +0.121 | 2021: +0.014 | 2022: +0.052 | 2023: +0.097 | 2024: +0.105 | 2025: +0.116 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.377 | 2016: -0.077 | 2017: -0.121 | 2018: +0.335 | 2019: +0.471 | 2020: +0.241 | 2021: +0.148 | 2022: +0.130 | 2023: +0.026 | 2024: +0.368 | 2025: +0.168 | 2026: +0.440
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.77
- Early IC=+0.1415, Recent IC=+0.1092, 1st-half IC=+0.0958, 2nd-half IC=+0.0967, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.088, Q3_mid=+0.080, Q4=+0.079, Q5_high_vol=+0.142

**`combo_mean__opening_drive_thrust_ratio__directional_volume_signature`** (Lock IC=+0.1004, Sharpe=+3.1023)
- Admission: Train IC=+0.1895, Deflated=+0.1898, IR=0.68, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.080 | 2017: +0.012 | 2018: +0.077 | 2019: +0.198 | 2020: +0.157 | 2021: +0.073 | 2022: +0.046 | 2023: +0.148 | 2024: +0.110 | 2025: +0.111 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.477 | 2016: +0.069 | 2017: -0.142 | 2018: -0.024 | 2019: +0.230 | 2020: +0.142 | 2021: +0.192 | 2022: +0.094 | 2023: +0.407 | 2024: +0.305 | 2025: +0.191 | 2026: +0.370
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.91, Recency ratio=0.80
- Early IC=+0.1374, Recent IC=+0.1105, 1st-half IC=+0.1172, 2nd-half IC=+0.1067, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.131, Q3_mid=+0.085, Q4=+0.087, Q5_high_vol=+0.139

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

**`combo_rank_min__volume_weighted_price_position__limit_down_proximity_early`** (Lock IC=+0.1381, Sharpe=+2.7110)
- Admission: Train IC=+0.2634, Deflated=+0.2638, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.016 | 2017: -0.006 | 2018: +0.068 | 2019: +0.223 | 2020: +0.017 | 2021: +0.124 | 2022: +0.019 | 2023: +0.147 | 2024: +0.110 | 2025: +0.131 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.232 | 2016: -0.077 | 2017: +0.116 | 2018: +0.247 | 2019: +0.595 | 2020: +0.129 | 2021: +0.347 | 2022: +0.200 | 2023: +0.316 | 2024: +0.237 | 2025: +0.141 | 2026: +0.375
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=0.85
- Early IC=+0.1417, Recent IC=+0.1203, 1st-half IC=+0.1000, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.129, Q3_mid=+0.147, Q4=+0.100, Q5_high_vol=+0.098

**`combo_min__star50_limit_proximity_early__volume_price_confirmation`** (Lock IC=+0.1908, Sharpe=+2.5310)
- Admission: Train IC=+0.2951, Deflated=+0.2959, IR=0.84, Mono=0.78, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.063 | 2017: +0.029 | 2018: +0.138 | 2019: +0.183 | 2020: +0.166 | 2021: +0.029 | 2022: +0.057 | 2023: +0.117 | 2024: +0.123 | 2025: +0.106 | 2026: +0.191
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.079 | 2017: +0.004 | 2018: +0.418 | 2019: +0.477 | 2020: +0.330 | 2021: +0.168 | 2022: +0.202 | 2023: +0.124 | 2024: +0.452 | 2025: +0.208 | 2026: +0.419
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.71
- Early IC=+0.1604, Recent IC=+0.1143, 1st-half IC=+0.1261, 2nd-half IC=+0.1036, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.094, Q3_mid=+0.074, Q4=+0.096, Q5_high_vol=+0.192

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.0766, Sharpe=+2.5089)
- Admission: Train IC=+0.3325, Deflated=+0.3324, IR=1.12, Mono=0.87, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.047 | 2017: +0.001 | 2018: +0.122 | 2019: +0.239 | 2020: +0.125 | 2021: +0.140 | 2022: +0.096 | 2023: +0.178 | 2024: +0.124 | 2025: +0.179 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.108 | 2017: +0.096 | 2018: +0.365 | 2019: +0.524 | 2020: +0.301 | 2021: +0.326 | 2022: +0.342 | 2023: +0.317 | 2024: +0.333 | 2025: +0.131 | 2026: +0.382
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.84
- Early IC=+0.1802, Recent IC=+0.1519, 1st-half IC=+0.1509, 2nd-half IC=+0.1481, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.163, Q3_mid=+0.134, Q4=+0.173, Q5_high_vol=+0.169

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0889, Sharpe=+2.1594)
- Admission: Train IC=+0.3099, Deflated=+0.3100, IR=1.00, Mono=0.84, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.053 | 2017: +0.041 | 2018: +0.131 | 2019: +0.210 | 2020: +0.144 | 2021: +0.165 | 2022: +0.104 | 2023: +0.170 | 2024: +0.063 | 2025: +0.187 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.016 | 2017: +0.237 | 2018: +0.345 | 2019: +0.319 | 2020: +0.424 | 2021: +0.323 | 2022: +0.365 | 2023: +0.225 | 2024: +0.235 | 2025: +0.184 | 2026: +0.350
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.74
- Early IC=+0.1704, Recent IC=+0.1254, 1st-half IC=+0.1610, 2nd-half IC=+0.1320, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.140, Q3_mid=+0.104, Q4=+0.180, Q5_high_vol=+0.202

**`combo_z_sum__max_up_ret__directional_volume_signature`** (Lock IC=+0.0868, Sharpe=+2.0454)
- Admission: Train IC=+0.2093, Deflated=+0.2096, IR=0.61, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.094 | 2017: +0.021 | 2018: +0.071 | 2019: +0.156 | 2020: +0.180 | 2021: +0.095 | 2022: +0.068 | 2023: +0.148 | 2024: +0.093 | 2025: +0.114 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.122 | 2017: -0.046 | 2018: +0.078 | 2019: +0.189 | 2020: +0.170 | 2021: +0.217 | 2022: +0.284 | 2023: +0.493 | 2024: +0.247 | 2025: +0.116 | 2026: +0.273
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.91
- Early IC=+0.1135, Recent IC=+0.1036, 1st-half IC=+0.1224, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.150, Q3_mid=+0.086, Q4=+0.080, Q5_high_vol=+0.131

**`combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.1716, Sharpe=+2.0307)
- Admission: Train IC=+0.1815, Deflated=+0.1809, IR=0.47, Mono=0.68, p=0.0004, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.046 | 2017: -0.014 | 2018: +0.102 | 2019: +0.172 | 2020: +0.107 | 2021: +0.146 | 2022: +0.166 | 2023: +0.109 | 2024: +0.100 | 2025: +0.123 | 2026: +0.173
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.207 | 2017: +0.032 | 2018: +0.220 | 2019: +0.240 | 2020: +0.156 | 2021: +0.246 | 2022: +0.184 | 2023: -0.050 | 2024: +0.213 | 2025: +0.015 | 2026: +0.332
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.94, Recency ratio=0.80
- Early IC=+0.1372, Recent IC=+0.1093, 1st-half IC=+0.1392, 2nd-half IC=+0.1303, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.119, Q3_mid=+0.115, Q4=+0.164, Q5_high_vol=+0.147

**`combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1814, Sharpe=+1.9841)
- Admission: Train IC=+0.2052, Deflated=+0.2052, IR=0.46, Mono=0.66, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.048 | 2017: +0.037 | 2018: +0.157 | 2019: +0.218 | 2020: +0.151 | 2021: +0.068 | 2022: +0.070 | 2023: +0.057 | 2024: +0.083 | 2025: +0.086 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.258 | 2016: -0.051 | 2017: -0.159 | 2018: +0.311 | 2019: +0.402 | 2020: +0.169 | 2021: +0.257 | 2022: -0.013 | 2023: +0.016 | 2024: +0.446 | 2025: +0.103 | 2026: +0.443
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=0.56, Recency ratio=0.45
- Early IC=+0.1872, Recent IC=+0.0843, 1st-half IC=+0.1419, 2nd-half IC=+0.0800, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.078, Q3_mid=+0.115, Q4=+0.096, Q5_high_vol=+0.161

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum`** (Lock IC=+0.2070, Sharpe=+1.9797)
- Admission: Train IC=+0.2086, Deflated=+0.2093, IR=0.46, Mono=0.69, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.097 | 2017: +0.008 | 2018: +0.117 | 2019: +0.243 | 2020: +0.121 | 2021: +0.094 | 2022: +0.156 | 2023: +0.155 | 2024: +0.111 | 2025: +0.084 | 2026: +0.207
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.006 | 2017: -0.004 | 2018: +0.118 | 2019: +0.424 | 2020: +0.144 | 2021: +0.224 | 2022: +0.129 | 2023: +0.214 | 2024: +0.263 | 2025: +0.032 | 2026: +0.128
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.54
- Early IC=+0.1799, Recent IC=+0.0976, 1st-half IC=+0.1434, 2nd-half IC=+0.1319, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.83)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.110, Q3_mid=+0.095, Q4=+0.156, Q5_high_vol=+0.162

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1842, Sharpe=+1.9520)
- Admission: Train IC=+0.2279, Deflated=+0.2280, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.123 | 2017: +0.064 | 2018: +0.205 | 2019: +0.217 | 2020: +0.214 | 2021: +0.101 | 2022: +0.099 | 2023: +0.079 | 2024: +0.080 | 2025: +0.105 | 2026: +0.184
- Yearly Tail ICs:   2015: -0.016 | 2016: +0.169 | 2017: -0.056 | 2018: +0.294 | 2019: +0.415 | 2020: +0.287 | 2021: +0.288 | 2022: +0.094 | 2023: +0.069 | 2024: +0.361 | 2025: +0.083 | 2026: +0.394
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.44
- Early IC=+0.2108, Recent IC=+0.0927, 1st-half IC=+0.1828, 2nd-half IC=+0.0941, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.102, Q3_mid=+0.117, Q4=+0.132, Q5_high_vol=+0.204

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression`** (Lock IC=+0.2095, Sharpe=+1.8853)
- Admission: Train IC=+0.2371, Deflated=+0.2377, IR=0.42, Mono=0.68, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.110 | 2017: +0.024 | 2018: +0.169 | 2019: +0.270 | 2020: +0.155 | 2021: +0.089 | 2022: +0.100 | 2023: +0.114 | 2024: +0.085 | 2025: +0.070 | 2026: +0.209
- Yearly Tail ICs:   2015: +0.087 | 2016: +0.124 | 2017: -0.075 | 2018: +0.195 | 2019: +0.482 | 2020: +0.197 | 2021: +0.323 | 2022: +0.108 | 2023: +0.229 | 2024: +0.276 | 2025: +0.243 | 2026: +0.337
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.35
- Early IC=+0.2195, Recent IC=+0.0772, 1st-half IC=+0.1680, 2nd-half IC=+0.0985, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.85)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.107, Q3_mid=+0.092, Q4=+0.155, Q5_high_vol=+0.171

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1495, Sharpe=+1.8753)
- Admission: Train IC=+0.3014, Deflated=+0.3022, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.056 | 2017: -0.039 | 2018: +0.098 | 2019: +0.257 | 2020: +0.142 | 2021: +0.107 | 2022: +0.043 | 2023: +0.124 | 2024: +0.106 | 2025: +0.151 | 2026: +0.150
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.002 | 2017: +0.015 | 2018: +0.338 | 2019: +0.526 | 2020: +0.302 | 2021: +0.233 | 2022: +0.167 | 2023: +0.243 | 2024: +0.452 | 2025: +0.151 | 2026: +0.443
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.72
- Early IC=+0.1776, Recent IC=+0.1286, 1st-half IC=+0.1410, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.137, Q3_mid=+0.145, Q4=+0.104, Q5_high_vol=+0.137

**`combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.2171, Sharpe=+1.8343)
- Admission: Train IC=+0.2485, Deflated=+0.2488, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.105 | 2017: +0.009 | 2018: +0.102 | 2019: +0.203 | 2020: +0.188 | 2021: +0.068 | 2022: +0.041 | 2023: +0.119 | 2024: +0.115 | 2025: +0.088 | 2026: +0.217
- Yearly Tail ICs:   2015: +0.272 | 2016: +0.189 | 2017: +0.124 | 2018: +0.301 | 2019: +0.393 | 2020: +0.358 | 2021: -0.041 | 2022: +0.092 | 2023: +0.349 | 2024: +0.497 | 2025: +0.072 | 2026: +0.357
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.67
- Early IC=+0.1524, Recent IC=+0.1017, 1st-half IC=+0.1429, 2nd-half IC=+0.0919, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.146, Q3_mid=+0.055, Q4=+0.111, Q5_high_vol=+0.170

**`combo_mean__volatility_expansion_trend_vector__directional_volume_signature`** (Lock IC=+0.0689, Sharpe=+1.7273)
- Admission: Train IC=+0.2253, Deflated=+0.2255, IR=0.84, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.065 | 2017: +0.015 | 2018: +0.019 | 2019: +0.146 | 2020: +0.151 | 2021: +0.091 | 2022: +0.055 | 2023: +0.144 | 2024: +0.114 | 2025: +0.146 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.414 | 2016: +0.013 | 2017: -0.150 | 2018: -0.030 | 2019: +0.314 | 2020: +0.141 | 2021: +0.120 | 2022: +0.254 | 2023: +0.449 | 2024: +0.266 | 2025: +0.383 | 2026: +0.262
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=1.34, Recency ratio=1.57
- Early IC=+0.0826, Recent IC=+0.1297, 1st-half IC=+0.0906, 2nd-half IC=+0.1215, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.140, Q3_mid=+0.109, Q4=+0.053, Q5_high_vol=+0.123

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1561, Sharpe=+1.6600)
- Admission: Train IC=+0.2807, Deflated=+0.2813, IR=0.69, Mono=0.79, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.094 | 2017: +0.035 | 2018: +0.170 | 2019: +0.182 | 2020: +0.185 | 2021: +0.051 | 2022: +0.068 | 2023: +0.128 | 2024: +0.091 | 2025: +0.131 | 2026: +0.156
- Yearly Tail ICs:   2015: +0.343 | 2016: +0.085 | 2017: -0.088 | 2018: +0.440 | 2019: +0.444 | 2020: +0.358 | 2021: +0.143 | 2022: -0.001 | 2023: +0.120 | 2024: +0.415 | 2025: +0.176 | 2026: +0.357
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.63
- Early IC=+0.1743, Recent IC=+0.1101, 1st-half IC=+0.1428, 2nd-half IC=+0.1052, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.105, Q3_mid=+0.070, Q4=+0.097, Q5_high_vol=+0.216

**`combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.1724, Sharpe=+1.6445)
- Admission: Train IC=+0.1881, Deflated=+0.1876, IR=0.45, Mono=0.66, p=0.0004, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.036 | 2017: -0.021 | 2018: +0.094 | 2019: +0.182 | 2020: +0.115 | 2021: +0.130 | 2022: +0.161 | 2023: +0.094 | 2024: +0.104 | 2025: +0.113 | 2026: +0.172
- Yearly Tail ICs:   2015: -0.048 | 2016: +0.231 | 2017: +0.019 | 2018: +0.255 | 2019: +0.231 | 2020: +0.183 | 2021: +0.296 | 2022: +0.167 | 2023: -0.025 | 2024: +0.206 | 2025: +0.005 | 2026: +0.355
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=0.79
- Early IC=+0.1380, Recent IC=+0.1085, 1st-half IC=+0.1357, 2nd-half IC=+0.1288, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.121, Q3_mid=+0.112, Q4=+0.157, Q5_high_vol=+0.146

**`combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.2079, Sharpe=+1.6092)
- Admission: Train IC=+0.2475, Deflated=+0.2477, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.111 | 2017: +0.010 | 2018: +0.095 | 2019: +0.197 | 2020: +0.196 | 2021: +0.058 | 2022: +0.044 | 2023: +0.120 | 2024: +0.108 | 2025: +0.098 | 2026: +0.203
- Yearly Tail ICs:   2015: +0.292 | 2016: +0.230 | 2017: +0.058 | 2018: +0.252 | 2019: +0.337 | 2020: +0.397 | 2021: -0.024 | 2022: +0.093 | 2023: +0.301 | 2024: +0.471 | 2025: +0.106 | 2026: +0.453
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.73
- Early IC=+0.1446, Recent IC=+0.1060, 1st-half IC=+0.1384, 2nd-half IC=+0.0953, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.150, Q3_mid=+0.055, Q4=+0.109, Q5_high_vol=+0.170

**`combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1120, Sharpe=+1.5982)
- Admission: Train IC=+0.2564, Deflated=+0.2564, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.071 | 2017: -0.001 | 2018: +0.158 | 2019: +0.207 | 2020: +0.121 | 2021: +0.137 | 2022: +0.095 | 2023: +0.136 | 2024: +0.066 | 2025: +0.154 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.050 | 2017: +0.130 | 2018: +0.338 | 2019: +0.410 | 2020: +0.077 | 2021: +0.369 | 2022: +0.109 | 2023: +0.166 | 2024: +0.380 | 2025: +0.228 | 2026: +0.260
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.60
- Early IC=+0.1826, Recent IC=+0.1100, 1st-half IC=+0.1475, 2nd-half IC=+0.1152, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.130, Q3_mid=+0.138, Q4=+0.094, Q5_high_vol=+0.164

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.0866, Sharpe=+1.5177)
- Admission: Train IC=+0.3339, Deflated=+0.3340, IR=1.12, Mono=0.85, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.034 | 2017: -0.003 | 2018: +0.108 | 2019: +0.231 | 2020: +0.131 | 2021: +0.132 | 2022: +0.109 | 2023: +0.186 | 2024: +0.087 | 2025: +0.186 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.016 | 2017: +0.073 | 2018: +0.342 | 2019: +0.495 | 2020: +0.320 | 2021: +0.285 | 2022: +0.298 | 2023: +0.468 | 2024: +0.314 | 2025: +0.117 | 2026: +0.279
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.81
- Early IC=+0.1705, Recent IC=+0.1381, 1st-half IC=+0.1446, 2nd-half IC=+0.1457, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.160, Q3_mid=+0.130, Q4=+0.165, Q5_high_vol=+0.168

**`combo_mean__rally_strength_max__volume_price_confirmation`** (Lock IC=+0.0445, Sharpe=+1.4513)
- Admission: Train IC=+0.2288, Deflated=+0.2290, IR=0.51, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.062 | 2017: +0.076 | 2018: +0.110 | 2019: +0.198 | 2020: +0.130 | 2021: +0.119 | 2022: +0.012 | 2023: +0.092 | 2024: +0.066 | 2025: +0.128 | 2026: +0.044
- Yearly Tail ICs:   2015: +0.437 | 2016: -0.168 | 2017: -0.128 | 2018: +0.282 | 2019: +0.345 | 2020: +0.098 | 2021: +0.289 | 2022: +0.049 | 2023: +0.136 | 2024: +0.283 | 2025: +0.165 | 2026: +0.200
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.63
- Early IC=+0.1544, Recent IC=+0.0971, 1st-half IC=+0.1270, 2nd-half IC=+0.0775, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.140, Q3_mid=+0.144, Q4=+0.080, Q5_high_vol=+0.115

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return`** (Lock IC=+0.1274, Sharpe=+1.4311)
- Admission: Train IC=+0.1971, Deflated=+0.1982, IR=0.66, Mono=0.71, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.226 | 2017: +0.036 | 2018: +0.197 | 2019: +0.131 | 2020: +0.123 | 2021: +0.125 | 2022: +0.052 | 2023: +0.028 | 2024: +0.071 | 2025: +0.034 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.167 | 2017: +0.067 | 2018: +0.379 | 2019: +0.301 | 2020: +0.196 | 2021: +0.378 | 2022: +0.120 | 2023: +0.240 | 2024: +0.221 | 2025: +0.118 | 2026: +0.242
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.35, Recency ratio=0.32
- Early IC=+0.1643, Recent IC=+0.0528, 1st-half IC=+0.1325, 2nd-half IC=+0.0468, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.064, Q3_mid=+0.051, Q4=+0.065, Q5_high_vol=+0.146

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0980, Sharpe=+1.3754)
- Admission: Train IC=+0.1643, Deflated=+0.1655, IR=0.40, Mono=0.65, p=0.0016, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.121 | 2016: -0.001 | 2017: -0.037 | 2018: +0.022 | 2019: +0.177 | 2020: +0.075 | 2021: +0.090 | 2022: +0.101 | 2023: +0.138 | 2024: +0.156 | 2025: +0.067 | 2026: +0.098
- Yearly Tail ICs:   2015: -0.080 | 2016: -0.128 | 2017: -0.014 | 2018: +0.032 | 2019: +0.411 | 2020: +0.047 | 2021: +0.189 | 2022: +0.144 | 2023: +0.238 | 2024: +0.324 | 2025: +0.004 | 2026: +0.358
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.12
- Early IC=+0.0991, Recent IC=+0.1112, 1st-half IC=+0.0961, 2nd-half IC=+0.1164, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.068, Q3_mid=+0.097, Q4=+0.132, Q5_high_vol=+0.112

**`combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1060, Sharpe=+1.2898)
- Admission: Train IC=+0.2440, Deflated=+0.2451, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.125 | 2017: +0.024 | 2018: +0.067 | 2019: +0.179 | 2020: +0.152 | 2021: +0.112 | 2022: +0.095 | 2023: +0.161 | 2024: +0.086 | 2025: +0.164 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.225 | 2017: +0.174 | 2018: +0.329 | 2019: +0.371 | 2020: +0.145 | 2021: +0.282 | 2022: +0.264 | 2023: +0.189 | 2024: +0.199 | 2025: +0.168 | 2026: +0.255
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.02
- Early IC=+0.1230, Recent IC=+0.1250, 1st-half IC=+0.1267, 2nd-half IC=+0.1304, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.153, Q3_mid=+0.113, Q4=+0.140, Q5_high_vol=+0.146

**`combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1039, Sharpe=+1.1602)
- Admission: Train IC=+0.2639, Deflated=+0.2637, IR=0.88, Mono=0.82, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.063 | 2017: +0.036 | 2018: +0.086 | 2019: +0.181 | 2020: +0.058 | 2021: +0.182 | 2022: +0.056 | 2023: +0.127 | 2024: +0.087 | 2025: +0.155 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.057 | 2017: +0.105 | 2018: +0.236 | 2019: +0.276 | 2020: +0.199 | 2021: +0.344 | 2022: +0.219 | 2023: +0.345 | 2024: +0.284 | 2025: +0.166 | 2026: +0.168
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.81
- Early IC=+0.1430, Recent IC=+0.1164, 1st-half IC=+0.1367, 2nd-half IC=+0.1154, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.158, Q3_mid=+0.144, Q4=+0.148, Q5_high_vol=+0.127

**`combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration`** (Lock IC=+0.0299, Sharpe=+1.0761)
- Admission: Train IC=+0.1408, Deflated=+0.1411, IR=0.47, Mono=0.65, p=0.0050, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.113 | 2017: +0.029 | 2018: +0.145 | 2019: +0.226 | 2020: +0.129 | 2021: +0.118 | 2022: +0.077 | 2023: +0.149 | 2024: +0.072 | 2025: +0.106 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.004 | 2017: +0.150 | 2018: +0.184 | 2019: +0.291 | 2020: +0.001 | 2021: +0.359 | 2022: -0.067 | 2023: +0.500 | 2024: +0.102 | 2025: +0.281 | 2026: +0.246
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.73, Recency ratio=0.48
- Early IC=+0.1853, Recent IC=+0.0891, 1st-half IC=+0.1383, 2nd-half IC=+0.1006, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.113, Q3_mid=+0.093, Q4=+0.093, Q5_high_vol=+0.159

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.0961, Sharpe=+1.0753)
- Admission: Train IC=+0.2412, Deflated=+0.2410, IR=0.83, Mono=0.78, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.116 | 2017: +0.054 | 2018: +0.141 | 2019: +0.217 | 2020: +0.102 | 2021: +0.208 | 2022: +0.070 | 2023: +0.122 | 2024: +0.106 | 2025: +0.163 | 2026: +0.096
- Yearly Tail ICs:   2015: -0.136 | 2016: +0.112 | 2017: +0.199 | 2018: +0.202 | 2019: +0.573 | 2020: +0.092 | 2021: +0.382 | 2022: +0.127 | 2023: +0.270 | 2024: +0.321 | 2025: +0.137 | 2026: +0.111
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.75
- Early IC=+0.1790, Recent IC=+0.1345, 1st-half IC=+0.1719, 2nd-half IC=+0.1192, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.134, Q3_mid=+0.151, Q4=+0.159, Q5_high_vol=+0.176

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0`** (Lock IC=+0.1482, Sharpe=+1.0680)
- Admission: Train IC=+0.1785, Deflated=+0.1790, IR=0.46, Mono=0.70, p=0.0006, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.254 | 2017: -0.022 | 2018: +0.191 | 2019: +0.183 | 2020: +0.185 | 2021: +0.106 | 2022: +0.040 | 2023: +0.045 | 2024: +0.073 | 2025: +0.040 | 2026: +0.148
- Yearly Tail ICs:   2015: -0.010 | 2016: +0.250 | 2017: -0.075 | 2018: +0.244 | 2019: +0.303 | 2020: +0.224 | 2021: +0.285 | 2022: +0.073 | 2023: +0.098 | 2024: +0.253 | 2025: +0.233 | 2026: +0.296
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.31, Recency ratio=0.30
- Early IC=+0.1869, Recent IC=+0.0566, 1st-half IC=+0.1571, 2nd-half IC=+0.0489, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.072, Q3_mid=+0.086, Q4=+0.078, Q5_high_vol=+0.143

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1425, Sharpe=+1.0019)
- Admission: Train IC=+0.2872, Deflated=+0.2881, IR=0.90, Mono=0.84, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.040 | 2017: -0.056 | 2018: +0.095 | 2019: +0.245 | 2020: +0.122 | 2021: +0.099 | 2022: +0.056 | 2023: +0.135 | 2024: +0.095 | 2025: +0.167 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.021 | 2017: -0.034 | 2018: +0.385 | 2019: +0.534 | 2020: +0.249 | 2021: +0.283 | 2022: +0.154 | 2023: +0.234 | 2024: +0.339 | 2025: +0.287 | 2026: +0.349
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=0.78
- Early IC=+0.1696, Recent IC=+0.1317, 1st-half IC=+0.1245, 2nd-half IC=+0.1228, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.143, Q3_mid=+0.136, Q4=+0.098, Q5_high_vol=+0.130

**`combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0944, Sharpe=+0.9523)
- Admission: Train IC=+0.2335, Deflated=+0.2340, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.005 | 2017: +0.012 | 2018: +0.022 | 2019: +0.160 | 2020: +0.070 | 2021: +0.115 | 2022: +0.084 | 2023: +0.140 | 2024: +0.058 | 2025: +0.171 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.129 | 2017: +0.187 | 2018: +0.251 | 2019: +0.282 | 2020: +0.169 | 2021: +0.215 | 2022: +0.195 | 2023: +0.333 | 2024: +0.310 | 2025: +0.212 | 2026: +0.109
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=1.26
- Early IC=+0.0904, Recent IC=+0.1142, 1st-half IC=+0.0860, 2nd-half IC=+0.1199, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.131, Q3_mid=+0.119, Q4=+0.102, Q5_high_vol=+0.102

**`combo_max__volatility_expansion_trend_vector__directional_volume_signature`** (Lock IC=+0.0206, Sharpe=+0.8649)
- Admission: Train IC=+0.1848, Deflated=+0.1852, IR=0.54, Mono=0.68, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.044 | 2017: +0.005 | 2018: +0.037 | 2019: +0.140 | 2020: +0.158 | 2021: +0.074 | 2022: +0.012 | 2023: +0.104 | 2024: +0.105 | 2025: +0.155 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.378 | 2016: -0.013 | 2017: -0.107 | 2018: -0.054 | 2019: +0.259 | 2020: +0.159 | 2021: +0.092 | 2022: +0.221 | 2023: +0.246 | 2024: +0.214 | 2025: +0.217 | 2026: +0.339
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=1.08, Recency ratio=1.48
- Early IC=+0.0883, Recent IC=+0.1303, 1st-half IC=+0.0965, 2nd-half IC=+0.1038, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.131, Q3_mid=+0.133, Q4=+0.029, Q5_high_vol=+0.118

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1093, Sharpe=+0.8621)
- Admission: Train IC=+0.3351, Deflated=+0.3365, IR=1.02, Mono=0.83, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.121 | 2017: -0.019 | 2018: +0.157 | 2019: +0.240 | 2020: +0.166 | 2021: +0.144 | 2022: +0.095 | 2023: +0.154 | 2024: +0.081 | 2025: +0.171 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.089 | 2017: -0.027 | 2018: +0.488 | 2019: +0.475 | 2020: +0.344 | 2021: +0.352 | 2022: +0.141 | 2023: +0.267 | 2024: +0.322 | 2025: +0.369 | 2026: +0.282
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.65
- Early IC=+0.1967, Recent IC=+0.1280, 1st-half IC=+0.1701, 2nd-half IC=+0.1322, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.173, Q3_mid=+0.119, Q4=+0.144, Q5_high_vol=+0.191

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1343, Sharpe=+0.7340)
- Admission: Train IC=+0.3076, Deflated=+0.3077, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.120 | 2017: -0.024 | 2018: +0.163 | 2019: +0.230 | 2020: +0.158 | 2021: +0.146 | 2022: +0.107 | 2023: +0.116 | 2024: +0.081 | 2025: +0.143 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.162 | 2017: +0.100 | 2018: +0.372 | 2019: +0.462 | 2020: +0.230 | 2021: +0.299 | 2022: +0.180 | 2023: +0.157 | 2024: +0.447 | 2025: +0.232 | 2026: +0.173
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.57
- Early IC=+0.1961, Recent IC=+0.1125, 1st-half IC=+0.1690, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.124, Q3_mid=+0.157, Q4=+0.122, Q5_high_vol=+0.161

**`combo_rank_min__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0850, Sharpe=+0.6640)
- Admission: Train IC=+0.2595, Deflated=+0.2603, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.068 | 2017: +0.003 | 2018: +0.069 | 2019: +0.212 | 2020: +0.149 | 2021: +0.125 | 2022: +0.111 | 2023: +0.156 | 2024: +0.108 | 2025: +0.170 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.140 | 2017: +0.069 | 2018: +0.291 | 2019: +0.442 | 2020: +0.162 | 2021: +0.354 | 2022: +0.262 | 2023: +0.226 | 2024: +0.237 | 2025: +0.120 | 2026: +0.056
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.99
- Early IC=+0.1405, Recent IC=+0.1387, 1st-half IC=+0.1368, 2nd-half IC=+0.1400, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.171, Q3_mid=+0.137, Q4=+0.137, Q5_high_vol=+0.160

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0827, Sharpe=+0.6302)
- Admission: Train IC=+0.3748, Deflated=+0.3754, IR=1.23, Mono=0.88, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.085 | 2017: -0.024 | 2018: +0.158 | 2019: +0.247 | 2020: +0.160 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.131 | 2025: +0.160 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.128 | 2017: +0.057 | 2018: +0.432 | 2019: +0.570 | 2020: +0.328 | 2021: +0.403 | 2022: +0.289 | 2023: +0.412 | 2024: +0.423 | 2025: +0.178 | 2026: +0.297
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.72
- Early IC=+0.2024, Recent IC=+0.1456, 1st-half IC=+0.1681, 2nd-half IC=+0.1434, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.172, Q3_mid=+0.138, Q4=+0.167, Q5_high_vol=+0.172

**`combo_rank_min__rally_strength_max__volume_price_confirmation`** (Lock IC=+0.0963, Sharpe=+0.5919)
- Admission: Train IC=+0.2254, Deflated=+0.2252, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.012 | 2017: +0.057 | 2018: +0.108 | 2019: +0.178 | 2020: +0.062 | 2021: +0.128 | 2022: +0.020 | 2023: +0.083 | 2024: +0.082 | 2025: +0.095 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.363 | 2016: -0.060 | 2017: -0.059 | 2018: +0.285 | 2019: +0.337 | 2020: +0.093 | 2021: +0.239 | 2022: +0.093 | 2023: +0.206 | 2024: +0.290 | 2025: +0.011 | 2026: +0.110
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.60
- Early IC=+0.1502, Recent IC=+0.0908, 1st-half IC=+0.1130, 2nd-half IC=+0.0784, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.102, Q3_mid=+0.119, Q4=+0.077, Q5_high_vol=+0.122

**`combo_rank_min__max_up_ret__gap_pct`** (Lock IC=+0.0926, Sharpe=+0.5706)
- Admission: Train IC=+0.2344, Deflated=+0.2350, IR=0.62, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.045 | 2017: -0.018 | 2018: +0.036 | 2019: +0.226 | 2020: +0.136 | 2021: +0.125 | 2022: +0.078 | 2023: +0.085 | 2024: +0.060 | 2025: +0.128 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.177 | 2016: +0.107 | 2017: +0.108 | 2018: +0.286 | 2019: +0.470 | 2020: +0.117 | 2021: +0.354 | 2022: +0.076 | 2023: +0.154 | 2024: +0.197 | 2025: +0.081 | 2026: +0.111
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.74
- Early IC=+0.1293, Recent IC=+0.0952, 1st-half IC=+0.1341, 2nd-half IC=+0.0934, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.141, Q3_mid=+0.117, Q4=+0.131, Q5_high_vol=+0.119

**`combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1144, Sharpe=+0.5302)
- Admission: Train IC=+0.2943, Deflated=+0.2957, IR=1.10, Mono=0.86, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.083 | 2017: -0.035 | 2018: +0.113 | 2019: +0.261 | 2020: +0.144 | 2021: +0.118 | 2022: +0.072 | 2023: +0.151 | 2024: +0.107 | 2025: +0.149 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.119 | 2017: +0.027 | 2018: +0.283 | 2019: +0.516 | 2020: +0.218 | 2021: +0.306 | 2022: +0.266 | 2023: +0.354 | 2024: +0.410 | 2025: +0.092 | 2026: +0.228
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1867, Recent IC=+0.1281, 1st-half IC=+0.1519, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.154, Q3_mid=+0.137, Q4=+0.123, Q5_high_vol=+0.156

**`combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev`** (Lock IC=+0.0339, Sharpe=+0.5163)
- Admission: Train IC=+0.1846, Deflated=+0.1857, IR=0.51, Mono=0.71, p=0.0004, MaxCorr=0.54
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.151 | 2017: +0.010 | 2018: +0.106 | 2019: +0.139 | 2020: +0.131 | 2021: +0.056 | 2022: +0.075 | 2023: +0.074 | 2024: +0.071 | 2025: +0.071 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.173 | 2017: +0.128 | 2018: +0.285 | 2019: +0.206 | 2020: +0.074 | 2021: +0.165 | 2022: +0.380 | 2023: +0.050 | 2024: +0.233 | 2025: +0.079 | 2026: +0.156
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.58
- Early IC=+0.1226, Recent IC=+0.0709, 1st-half IC=+0.1069, 2nd-half IC=+0.0722, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.100, Q3_mid=+0.100, Q4=+0.142, Q5_high_vol=+0.022

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1000, Sharpe=+0.4816)
- Admission: Train IC=+0.3521, Deflated=+0.3534, IR=1.04, Mono=0.85, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.110 | 2017: -0.012 | 2018: +0.158 | 2019: +0.260 | 2020: +0.173 | 2021: +0.134 | 2022: +0.082 | 2023: +0.152 | 2024: +0.096 | 2025: +0.160 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.130 | 2017: +0.034 | 2018: +0.352 | 2019: +0.560 | 2020: +0.402 | 2021: +0.271 | 2022: +0.184 | 2023: +0.346 | 2024: +0.447 | 2025: +0.203 | 2026: +0.257
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.61
- Early IC=+0.2090, Recent IC=+0.1283, 1st-half IC=+0.1771, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.166, Q3_mid=+0.134, Q4=+0.154, Q5_high_vol=+0.182

**`combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.0974, Sharpe=+0.3863)
- Admission: Train IC=+0.2481, Deflated=+0.2479, IR=0.79, Mono=0.78, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.065 | 2017: +0.020 | 2018: +0.105 | 2019: +0.239 | 2020: +0.057 | 2021: +0.188 | 2022: +0.055 | 2023: +0.123 | 2024: +0.080 | 2025: +0.132 | 2026: +0.097
- Yearly Tail ICs:   2015: +0.209 | 2016: +0.114 | 2017: +0.081 | 2018: +0.209 | 2019: +0.428 | 2020: +0.114 | 2021: +0.329 | 2022: +0.190 | 2023: +0.343 | 2024: +0.350 | 2025: +0.097 | 2026: +0.160
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.61
- Early IC=+0.1720, Recent IC=+0.1057, 1st-half IC=+0.1480, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=0.90)
- Regime ICs: Q1_low_vol=+0.097, Q2=+0.162, Q3_mid=+0.146, Q4=+0.144, Q5_high_vol=+0.125

**`combo_min__max_up_ret__first_bar_return`** (Lock IC=+0.0299, Sharpe=+0.3733)
- Admission: Train IC=+0.1766, Deflated=+0.1781, IR=0.63, Mono=0.77, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.087 | 2017: +0.047 | 2018: +0.098 | 2019: +0.172 | 2020: +0.096 | 2021: +0.138 | 2022: +0.087 | 2023: +0.172 | 2024: +0.059 | 2025: +0.137 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.003 | 2017: +0.139 | 2018: +0.196 | 2019: +0.232 | 2020: +0.022 | 2021: +0.227 | 2022: +0.200 | 2023: +0.386 | 2024: +0.145 | 2025: +0.170 | 2026: +0.223
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.73
- Early IC=+0.1350, Recent IC=+0.0981, 1st-half IC=+0.1178, 2nd-half IC=+0.1141, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.165, Q3_mid=+0.102, Q4=+0.089, Q5_high_vol=+0.122

**`combo_rank_max__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0057, Sharpe=+0.3634)
- Admission: Train IC=+0.2257, Deflated=+0.2258, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.109 | 2017: +0.040 | 2018: +0.104 | 2019: +0.185 | 2020: +0.152 | 2021: +0.148 | 2022: +0.074 | 2023: +0.104 | 2024: +0.068 | 2025: +0.124 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.029 | 2017: -0.034 | 2018: +0.273 | 2019: +0.276 | 2020: +0.150 | 2021: +0.289 | 2022: +0.175 | 2023: +0.237 | 2024: +0.317 | 2025: +0.082 | 2026: +0.008
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.67
- Early IC=+0.1428, Recent IC=+0.0952, 1st-half IC=+0.1451, 2nd-half IC=+0.0946, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.135, Q3_mid=+0.132, Q4=+0.113, Q5_high_vol=+0.137

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1358, Sharpe=+0.2908)
- Admission: Train IC=+0.2041, Deflated=+0.2031, IR=0.49, Mono=0.66, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.177 | 2017: -0.014 | 2018: +0.140 | 2019: +0.155 | 2020: +0.151 | 2021: +0.143 | 2022: +0.133 | 2023: +0.105 | 2024: +0.046 | 2025: +0.138 | 2026: +0.136
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.158 | 2017: +0.136 | 2018: +0.342 | 2019: +0.277 | 2020: +0.067 | 2021: +0.394 | 2022: +0.100 | 2023: +0.080 | 2024: +0.165 | 2025: +0.041 | 2026: +0.185
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.63
- Early IC=+0.1474, Recent IC=+0.0922, 1st-half IC=+0.1488, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.105, Q3_mid=+0.150, Q4=+0.104, Q5_high_vol=+0.132

**`combo_mean__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0389, Sharpe=+0.2894)
- Admission: Train IC=+0.2166, Deflated=+0.2172, IR=0.60, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.111 | 2017: +0.075 | 2018: +0.141 | 2019: +0.177 | 2020: +0.161 | 2021: +0.116 | 2022: +0.079 | 2023: +0.140 | 2024: +0.067 | 2025: +0.125 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.087 | 2017: -0.031 | 2018: +0.282 | 2019: +0.277 | 2020: +0.135 | 2021: +0.291 | 2022: +0.123 | 2023: +0.410 | 2024: +0.172 | 2025: +0.121 | 2026: +0.136
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.60
- Early IC=+0.1591, Recent IC=+0.0961, 1st-half IC=+0.1413, 2nd-half IC=+0.1058, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.133, Q3_mid=+0.110, Q4=+0.106, Q5_high_vol=+0.155

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0832, Sharpe=+0.2726)
- Admission: Train IC=+0.2831, Deflated=+0.2836, IR=0.83, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.131 | 2017: -0.010 | 2018: +0.179 | 2019: +0.223 | 2020: +0.149 | 2021: +0.151 | 2022: +0.098 | 2023: +0.146 | 2024: +0.084 | 2025: +0.161 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.033 | 2017: +0.181 | 2018: +0.280 | 2019: +0.406 | 2020: +0.205 | 2021: +0.393 | 2022: +0.145 | 2023: +0.200 | 2024: +0.349 | 2025: +0.251 | 2026: +0.170
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.61
- Early IC=+0.2009, Recent IC=+0.1223, 1st-half IC=+0.1651, 2nd-half IC=+0.1251, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.141, Q3_mid=+0.151, Q4=+0.107, Q5_high_vol=+0.175

**`first_bar_return`** (Lock IC=+0.0226, Sharpe=+0.2558)
- Admission: Train IC=+0.1648, Deflated=+0.1657, IR=0.60, Mono=0.73, p=0.0014, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.162 | 2017: +0.017 | 2018: +0.137 | 2019: +0.192 | 2020: +0.116 | 2021: +0.135 | 2022: +0.073 | 2023: +0.144 | 2024: +0.061 | 2025: +0.123 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.56
- Early IC=+0.1645, Recent IC=+0.0918, 1st-half IC=+0.1316, 2nd-half IC=+0.0981, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.130, Q3_mid=+0.113, Q4=+0.063, Q5_high_vol=+0.129

**`combo_max__max_up_ret__directional_volume_signature`** (Lock IC=+0.0276, Sharpe=+0.2544)
- Admission: Train IC=+0.2235, Deflated=+0.2233, IR=0.73, Mono=0.76, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.083 | 2017: -0.036 | 2018: +0.048 | 2019: +0.141 | 2020: +0.168 | 2021: +0.105 | 2022: +0.072 | 2023: +0.098 | 2024: +0.081 | 2025: +0.123 | 2026: +0.028
- Yearly Tail ICs:   2015: +0.055 | 2016: +0.157 | 2017: -0.163 | 2018: +0.007 | 2019: +0.083 | 2020: +0.233 | 2021: +0.333 | 2022: +0.328 | 2023: +0.312 | 2024: +0.295 | 2025: +0.017 | 2026: +0.030
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=1.07
- Early IC=+0.0945, Recent IC=+0.1016, 1st-half IC=+0.1147, 2nd-half IC=+0.0984, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.126, Q3_mid=+0.107, Q4=+0.069, Q5_high_vol=+0.126

**`combo_rank_max__max_up_ret__directional_volume_signature`** (Lock IC=+0.0384, Sharpe=+0.2544)
- Admission: Train IC=+0.2061, Deflated=+0.2061, IR=0.58, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.086 | 2017: -0.036 | 2018: +0.050 | 2019: +0.136 | 2020: +0.177 | 2021: +0.095 | 2022: +0.058 | 2023: +0.090 | 2024: +0.084 | 2025: +0.120 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.137 | 2016: +0.116 | 2017: -0.180 | 2018: -0.005 | 2019: +0.111 | 2020: +0.217 | 2021: +0.272 | 2022: +0.271 | 2023: +0.244 | 2024: +0.219 | 2025: -0.009 | 2026: +0.284
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=1.04
- Early IC=+0.0966, Recent IC=+0.1008, 1st-half IC=+0.1164, 2nd-half IC=+0.0957, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.130, Q3_mid=+0.104, Q4=+0.071, Q5_high_vol=+0.124

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0895, Sharpe=+0.2487)
- Admission: Train IC=+0.2787, Deflated=+0.2803, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.089 | 2017: -0.005 | 2018: +0.152 | 2019: +0.243 | 2020: +0.141 | 2021: +0.127 | 2022: +0.097 | 2023: +0.137 | 2024: +0.074 | 2025: +0.163 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.061 | 2017: +0.081 | 2018: +0.317 | 2019: +0.501 | 2020: +0.216 | 2021: +0.253 | 2022: +0.263 | 2023: +0.223 | 2024: +0.413 | 2025: +0.118 | 2026: +0.249
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.60
- Early IC=+0.1974, Recent IC=+0.1185, 1st-half IC=+0.1593, 2nd-half IC=+0.1236, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.159, Q3_mid=+0.120, Q4=+0.138, Q5_high_vol=+0.178

**`combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1158, Sharpe=+0.1892)
- Admission: Train IC=+0.2098, Deflated=+0.2088, IR=0.50, Mono=0.66, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.114 | 2017: -0.008 | 2018: +0.121 | 2019: +0.159 | 2020: +0.101 | 2021: +0.124 | 2022: +0.158 | 2023: +0.107 | 2024: +0.058 | 2025: +0.154 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.124 | 2016: -0.008 | 2017: +0.178 | 2018: +0.314 | 2019: +0.290 | 2020: +0.062 | 2021: +0.318 | 2022: +0.128 | 2023: +0.165 | 2024: +0.183 | 2025: +0.116 | 2026: -0.096
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.71
- Early IC=+0.1429, Recent IC=+0.1016, 1st-half IC=+0.1318, 2nd-half IC=+0.1176, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.105, Q3_mid=+0.145, Q4=+0.116, Q5_high_vol=+0.108

**`combo_rank_min__bar_body_rng_0__directional_volume_signature`** (Lock IC=+0.0911, Sharpe=+0.1720)
- Admission: Train IC=+0.1760, Deflated=+0.1764, IR=0.51, Mono=0.68, p=0.0006, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.131 | 2017: -0.005 | 2018: +0.087 | 2019: +0.190 | 2020: +0.178 | 2021: +0.096 | 2022: +0.039 | 2023: +0.123 | 2024: +0.095 | 2025: +0.084 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.102 | 2017: -0.008 | 2018: +0.164 | 2019: +0.310 | 2020: +0.309 | 2021: +0.069 | 2022: -0.030 | 2023: +0.242 | 2024: +0.218 | 2025: +0.307 | 2026: +0.175
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.63
- Early IC=+0.1382, Recent IC=+0.0873, 1st-half IC=+0.1253, 2nd-half IC=+0.0820, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=0.91)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.124, Q3_mid=+0.072, Q4=+0.056, Q5_high_vol=+0.124

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

**`combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.1554, Sharpe=+0.1107)
- Admission: Train IC=+0.2406, Deflated=+0.2403, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.46
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

**`combo_mean__volume_weighted_price_position__limit_down_proximity_early`** (Lock IC=+0.1186, Sharpe=+0.0733)
- Admission: Train IC=+0.2565, Deflated=+0.2561, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.065 | 2017: +0.036 | 2018: +0.117 | 2019: +0.221 | 2020: +0.039 | 2021: +0.171 | 2022: +0.041 | 2023: +0.114 | 2024: +0.095 | 2025: +0.141 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.163 | 2016: -0.114 | 2017: +0.150 | 2018: +0.113 | 2019: +0.565 | 2020: +0.079 | 2021: +0.336 | 2022: +0.103 | 2023: +0.304 | 2024: +0.311 | 2025: +0.172 | 2026: +0.183
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.70
- Early IC=+0.1690, Recent IC=+0.1180, 1st-half IC=+0.1347, 2nd-half IC=+0.1039, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.114, Q3_mid=+0.140, Q4=+0.117, Q5_high_vol=+0.132

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0307, Sharpe=+0.0580)
- Admission: Train IC=+0.2465, Deflated=+0.2477, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.93
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

**`combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0433, Sharpe=+0.0061)
- Admission: Train IC=+0.1857, Deflated=+0.1865, IR=0.57, Mono=0.72, p=0.0004, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.137 | 2017: +0.034 | 2018: +0.132 | 2019: +0.193 | 2020: +0.136 | 2021: +0.138 | 2022: +0.078 | 2023: +0.130 | 2024: +0.048 | 2025: +0.146 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.048 | 2017: +0.207 | 2018: +0.229 | 2019: +0.222 | 2020: +0.161 | 2021: +0.291 | 2022: +0.094 | 2023: +0.338 | 2024: +0.029 | 2025: +0.284 | 2026: +0.199
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.1620, Recent IC=+0.0967, 1st-half IC=+0.1387, 2nd-half IC=+0.1006, Neg regimes=0/5
- Weak component: `gap_pct` (CV=0.76)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.133, Q3_mid=+0.124, Q4=+0.065, Q5_high_vol=+0.132

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0709 | N/A | +0.0709 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0449 | N/A | +0.0449 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0272 | N/A | +0.0272 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0147 | N/A | +0.0147 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0132 | N/A | +0.0132 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Median | persistent | +0.0005 | N/A | +0.0005 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | FP | immediate | -0.0161 | N/A | -0.0161 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | FP | immediate | -0.0273 | N/A | -0.0273 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0293 | N/A | -0.0293 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.0294 | N/A | -0.0294 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0308 | N/A | -0.0308 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | FP | immediate | -0.0317 | N/A | -0.0317 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | FP | immediate | -0.0504 | N/A | -0.0504 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum` | FP | immediate | -0.0509 | N/A | -0.0509 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0581 | N/A | -0.0581 | ∞ |
| `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0631 | N/A | -0.0631 | ∞ |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.0691 | N/A | -0.0691 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early` | FP | immediate | -0.0701 | N/A | -0.0701 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | FP | immediate | -0.0712 | N/A | -0.0712 | ∞ |
| `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum` | FP | immediate | -0.0775 | N/A | -0.0775 | ∞ |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | FP | immediate | -0.0889 | N/A | -0.0889 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0924 | N/A | -0.0924 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0955 | N/A | -0.0955 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | FP | immediate | -0.1072 | N/A | -0.1072 | ∞ |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1087 | N/A | -0.1087 | ∞ |
| `combo_mean__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.1215 | N/A | -0.1215 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.1297 | N/A | -0.1297 | ∞ |
| `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.1298 | N/A | -0.1298 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0` | FP | immediate | -0.1364 | N/A | -0.1364 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.1476 | N/A | -0.1476 | ∞ |
| `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.1502 | N/A | -0.1502 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | FP | immediate | -0.1526 | N/A | -0.1526 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_return` | FP | immediate | -0.1611 | N/A | -0.1611 | ∞ |
| `combo_max__max_up_ret__bar_ret_0` | FP | immediate | -0.1613 | N/A | -0.1613 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | FP | immediate | -0.1637 | N/A | -0.1637 | ∞ |
| `combo_mean__max_up_ret__morning_volume_weighted_momentum` | FP | immediate | -0.1658 | N/A | -0.1658 | ∞ |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1697 | N/A | -0.1697 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1740 | N/A | -0.1740 | ∞ |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1762 | N/A | -0.1762 | ∞ |
| `combo_rank_max__first_bar_return__morning_volume_weighted_momentum` | FP | immediate | -0.1934 | N/A | -0.1934 | ∞ |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | FP | immediate | -0.1961 | N/A | -0.1961 | ∞ |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1964 | N/A | -0.1964 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1994 | N/A | -0.1994 | ∞ |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.2114 | N/A | -0.2114 | ∞ |

**Decay distribution**: immediate=38, fast(1-2y)=0, gradual=0, persistent=6

**FP decay trajectories:**

- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.211
- `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Y1:-0.199
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:-0.196
- `combo_max__bar_ret_0__morning_volume_weighted_momentum`: Y1:-0.196
- `combo_rank_max__first_bar_return__morning_volume_weighted_momentum`: Y1:-0.193
- `combo_rank_max__first_bar_return__volume_weighted_price_position`: Y1:-0.176
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`: Y1:-0.174
- `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.170
- `combo_mean__max_up_ret__morning_volume_weighted_momentum`: Y1:-0.166
- `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`: Y1:-0.164
- `combo_max__max_up_ret__bar_ret_0`: Y1:-0.161
- `combo_rank_max__max_up_ret__first_bar_return`: Y1:-0.161
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`: Y1:-0.153
- `combo_tri_max__first_bar_return__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.150
- `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.148
- `combo_tri_max__opening_drive_thrust_ratio__first_bar_return__bar_body_rng_0`: Y1:-0.136
- `combo_tri_median__smooth_momentum_structure__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.130
- `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.130
- `combo_mean__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.122
- `combo_ratio__first_bar_return__volume_weighted_price_position`: Y1:-0.109
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`: Y1:-0.107
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.095
- `combo_min__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.092
- `combo_rank_max__first_bar_return__bar_body_rng_0`: Y1:-0.089
- `combo_rank_min__bar_body_rng_0__morning_volume_weighted_momentum`: Y1:-0.078
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return`: Y1:-0.071
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__limit_down_proximity_early`: Y1:-0.070
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Y1:-0.069
- `combo_tri_min__first_bar_return__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.063
- `combo_tri_median__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.058
- `combo_mean__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Y1:-0.051
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Y1:-0.050
- `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Y1:-0.032
- `combo_tri_mean__star50_limit_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.031
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Y1:-0.029
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.029
- `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Y1:-0.027
- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Y1:-0.016

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1800 | N/A | +0.1800 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1783 | N/A | +0.1783 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1749 | N/A | +0.1749 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1278 | N/A | +0.1278 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.1105 | N/A | +0.1105 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1016 | N/A | +0.1016 | ∞ |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0988 | N/A | +0.0988 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0955 | N/A | +0.0955 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0876 | N/A | +0.0876 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0849 | N/A | +0.0849 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.0846 | N/A | +0.0846 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0815 | N/A | +0.0815 | ∞ |
| `combo_tri_min__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.0765 | N/A | +0.0765 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.0733 | N/A | +0.0733 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0727 | N/A | +0.0727 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.0674 | N/A | +0.0674 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.0617 | N/A | +0.0617 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__shaved_bar_trend_conviction` | Median | persistent | +0.0600 | N/A | +0.0600 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.0571 | N/A | +0.0571 | ∞ |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | Median | persistent | +0.0529 | N/A | +0.0529 | ∞ |
| `combo_clamp_diff__first_bar_return__demark_setup_reversal_early` | Median | persistent | +0.0514 | N/A | +0.0514 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | TP | persistent | +0.0419 | N/A | +0.0419 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | persistent | +0.0350 | N/A | +0.0350 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__early_body_momentum` | Median | persistent | +0.0277 | N/A | +0.0277 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Median | persistent | +0.0177 | N/A | +0.0177 | ∞ |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | Median | persistent | +0.0175 | N/A | +0.0175 | ∞ |
| `combo_mean__first_bar_return__max_down_ret` | Median | persistent | +0.0117 | N/A | +0.0117 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | Median | persistent | +0.0095 | N/A | +0.0095 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | Median | persistent | +0.0078 | N/A | +0.0078 | ∞ |
| `combo_max__bar_ret_0__max_down_ret` | Median | persistent | +0.0077 | N/A | +0.0077 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0028 | N/A | +0.0028 | ∞ |
| `combo_rank_min__max_up_ret__bar_body_rng_0` | Median | persistent | +0.0003 | N/A | +0.0003 | ∞ |
| `combo_min__net_volume_flow__first_bar_return` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_min__first_bar_return__bar_body_rng_0` | FP | immediate | -0.0051 | N/A | -0.0051 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | FP | immediate | -0.0068 | N/A | -0.0068 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | FP | immediate | -0.0114 | N/A | -0.0114 | ∞ |
| `combo_mean__max_up_ret__max_down_ret` | FP | immediate | -0.0160 | N/A | -0.0160 | ∞ |
| `combo_rank_min__net_volume_flow__bar_body_rng_0` | FP | immediate | -0.0164 | N/A | -0.0164 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | FP | immediate | -0.0197 | N/A | -0.0197 | ∞ |
| `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0` | FP | immediate | -0.0199 | N/A | -0.0199 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0` | FP | immediate | -0.0298 | N/A | -0.0298 | ∞ |
| `combo_min__bar_ret_0__early_order_flow_imbalance` | FP | immediate | -0.0339 | N/A | -0.0339 | ∞ |
| `combo_mean__bar_ret_0__close_vs_open_range` | FP | immediate | -0.0383 | N/A | -0.0383 | ∞ |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | FP | immediate | -0.0451 | N/A | -0.0451 | ∞ |
| `combo_sig_product__max_up_ret__vwap_close_divergence_trend` | FP | immediate | -0.0518 | N/A | -0.0518 | ∞ |
| `combo_rank_max__max_up_ret__bar_ret_0` | FP | immediate | -0.0646 | N/A | -0.0646 | ∞ |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0` | FP | immediate | -0.0656 | N/A | -0.0656 | ∞ |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | FP | immediate | -0.0676 | N/A | -0.0676 | ∞ |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0686 | N/A | -0.0686 | ∞ |
| `combo_mean__vwap_close_divergence_trend__bar_body_rng_0` | FP | immediate | -0.0705 | N/A | -0.0705 | ∞ |
| `combo_rank_max__early_order_flow_imbalance__max_down_ret` | FP | immediate | -0.0706 | N/A | -0.0706 | ∞ |
| `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend` | FP | immediate | -0.0712 | N/A | -0.0712 | ∞ |
| `morning_volume_weighted_momentum` | FP | immediate | -0.0906 | N/A | -0.0906 | ∞ |
| `combo_sig_product__max_down_ret__vwap_close_divergence_trend` | FP | immediate | -0.0915 | N/A | -0.0915 | ∞ |
| `combo_sig_product__early_body_momentum__vwap_close_divergence_trend` | FP | immediate | -0.0956 | N/A | -0.0956 | ∞ |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | FP | immediate | -0.1131 | N/A | -0.1131 | ∞ |

**Decay distribution**: immediate=24, fast(1-2y)=0, gradual=0, persistent=32

**FP decay trajectories:**

- `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend`: Y1:-0.113
- `combo_sig_product__early_body_momentum__vwap_close_divergence_trend`: Y1:-0.096
- `combo_sig_product__max_down_ret__vwap_close_divergence_trend`: Y1:-0.092
- `morning_volume_weighted_momentum`: Y1:-0.091
- `combo_sig_product__early_order_flow_imbalance__vwap_close_divergence_trend`: Y1:-0.071
- `combo_rank_max__early_order_flow_imbalance__max_down_ret`: Y1:-0.071
- `combo_mean__vwap_close_divergence_trend__bar_body_rng_0`: Y1:-0.071
- `combo_rank_max__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.069
- `combo_mean__bar_ret_0__vwap_close_divergence_trend`: Y1:-0.068
- `combo_tri_mean__max_up_ret__trend_bar_close_consistency__bar_ret_0`: Y1:-0.066
- `combo_rank_max__max_up_ret__bar_ret_0`: Y1:-0.065
- `combo_sig_product__max_up_ret__vwap_close_divergence_trend`: Y1:-0.052
- `combo_min__early_order_flow_imbalance__bar_body_rng_0`: Y1:-0.045
- `combo_mean__bar_ret_0__close_vs_open_range`: Y1:-0.038
- `combo_min__bar_ret_0__early_order_flow_imbalance`: Y1:-0.034
- `combo_tri_mean__opening_drive_thrust_ratio__trend_day_regime_conviction__bar_ret_0`: Y1:-0.030
- `combo_tri_min__max_up_ret__trend_day_regime_conviction__bar_ret_0`: Y1:-0.020
- `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`: Y1:-0.020
- `combo_rank_min__net_volume_flow__bar_body_rng_0`: Y1:-0.016
- `combo_mean__max_up_ret__max_down_ret`: Y1:-0.016
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`: Y1:-0.011
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`: Y1:-0.007
- `combo_min__first_bar_return__bar_body_rng_0`: Y1:-0.005
- `combo_min__net_volume_flow__first_bar_return`: Y1:-0.001

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.2171 | N/A | +0.2171 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | TP | persistent | +0.2095 | N/A | +0.2095 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.2079 | N/A | +0.2079 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | TP | persistent | +0.2070 | N/A | +0.2070 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | TP | persistent | +0.1908 | N/A | +0.1908 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1842 | N/A | +0.1842 | ∞ |
| `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1814 | N/A | +0.1814 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | TP | persistent | +0.1801 | N/A | +0.1801 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.1724 | N/A | +0.1724 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.1716 | N/A | +0.1716 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1561 | N/A | +0.1561 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.1554 | N/A | +0.1554 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1495 | N/A | +0.1495 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__bar_body_rng_0` | TP | persistent | +0.1482 | N/A | +0.1482 | ∞ |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1425 | N/A | +0.1425 | ∞ |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | TP | persistent | +0.1381 | N/A | +0.1381 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1358 | N/A | +0.1358 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1343 | N/A | +0.1343 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1324 | N/A | +0.1324 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early__first_bar_return` | TP | persistent | +0.1274 | N/A | +0.1274 | ∞ |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | Median | persistent | +0.1273 | N/A | +0.1273 | ∞ |
| `combo_mean__volume_weighted_price_position__limit_down_proximity_early` | TP | persistent | +0.1186 | N/A | +0.1186 | ∞ |
| `combo_mean__max_up_ret__gap_pct` | Median | persistent | +0.1184 | N/A | +0.1184 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1174 | N/A | +0.1174 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1158 | N/A | +0.1158 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | Median | persistent | +0.1154 | N/A | +0.1154 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1144 | N/A | +0.1144 | ∞ |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1120 | N/A | +0.1120 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1093 | N/A | +0.1093 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1060 | N/A | +0.1060 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.1039 | N/A | +0.1039 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1013 | N/A | +0.1013 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__directional_volume_signature` | TP | persistent | +0.1004 | N/A | +0.1004 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1000 | N/A | +0.1000 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0980 | N/A | +0.0980 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.0974 | N/A | +0.0974 | ∞ |
| `combo_rank_min__rally_strength_max__volume_price_confirmation` | TP | persistent | +0.0963 | N/A | +0.0963 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.0961 | N/A | +0.0961 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0944 | N/A | +0.0944 | ∞ |
| `combo_rank_min__max_up_ret__gap_pct` | TP | persistent | +0.0926 | N/A | +0.0926 | ∞ |
| `combo_rank_min__bar_body_rng_0__directional_volume_signature` | TP | persistent | +0.0911 | N/A | +0.0911 | ∞ |
| `combo_rank_min__max_up_ret__directional_volume_signature` | Median | persistent | +0.0897 | N/A | +0.0897 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0895 | N/A | +0.0895 | ∞ |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0889 | N/A | +0.0889 | ∞ |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0888 | N/A | +0.0888 | ∞ |
| `combo_z_sum__max_up_ret__directional_volume_signature` | TP | persistent | +0.0868 | N/A | +0.0868 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0866 | N/A | +0.0866 | ∞ |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Median | persistent | +0.0866 | N/A | +0.0866 | ∞ |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.0850 | N/A | +0.0850 | ∞ |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0844 | N/A | +0.0844 | ∞ |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0841 | N/A | +0.0841 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.0832 | N/A | +0.0832 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0827 | N/A | +0.0827 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0821 | N/A | +0.0821 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0766 | N/A | +0.0766 | ∞ |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | Median | persistent | +0.0741 | N/A | +0.0741 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0712 | N/A | +0.0712 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__directional_volume_signature` | TP | persistent | +0.0689 | N/A | +0.0689 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0646 | N/A | +0.0646 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0623 | N/A | +0.0623 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0593 | N/A | +0.0593 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0586 | N/A | +0.0586 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0578 | N/A | +0.0578 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0567 | N/A | +0.0567 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0545 | N/A | +0.0545 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | persistent | +0.0510 | N/A | +0.0510 | ∞ |
| `combo_mean__rally_strength_max__volume_price_confirmation` | TP | persistent | +0.0445 | N/A | +0.0445 | ∞ |
| `combo_ifelse__gap_pct__bar_body_rng_0__first_bar_return` | TP | persistent | +0.0433 | N/A | +0.0433 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0431 | N/A | +0.0431 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Median | persistent | +0.0426 | N/A | +0.0426 | ∞ |
| `combo_mean__max_up_ret__volume_price_confirmation` | TP | persistent | +0.0389 | N/A | +0.0389 | ∞ |
| `combo_rank_max__max_up_ret__directional_volume_signature` | TP | persistent | +0.0384 | N/A | +0.0384 | ∞ |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__yesterday_early_vwap_dev` | Median | persistent | +0.0354 | N/A | +0.0354 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__yesterday_early_vwap_dev` | TP | persistent | +0.0339 | N/A | +0.0339 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__demark_setup_reversal_early` | Median | persistent | +0.0307 | N/A | +0.0307 | ∞ |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0307 | N/A | +0.0307 | ∞ |
| `combo_min__max_up_ret__first_bar_return` | TP | persistent | +0.0299 | N/A | +0.0299 | ∞ |
| `combo_rel_diff__bar_ret_0__volume_weighted_momentum_acceleration` | TP | persistent | +0.0299 | N/A | +0.0299 | ∞ |
| `combo_max__max_up_ret__directional_volume_signature` | TP | persistent | +0.0276 | N/A | +0.0276 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0262 | N/A | +0.0262 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__volume_price_confirmation` | Median | persistent | +0.0262 | N/A | +0.0262 | ∞ |
| `first_bar_return` | TP | persistent | +0.0226 | N/A | +0.0226 | ∞ |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0212 | N/A | +0.0212 | ∞ |
| `bar_body_rng_0` | Median | persistent | +0.0207 | N/A | +0.0207 | ∞ |
| `combo_max__volatility_expansion_trend_vector__directional_volume_signature` | TP | persistent | +0.0206 | N/A | +0.0206 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__first_bar_return` | Median | persistent | +0.0162 | N/A | +0.0162 | ∞ |
| `combo_clamp_diff__first_bar_return__volume_weighted_momentum_acceleration` | Median | persistent | +0.0109 | N/A | +0.0109 | ∞ |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.0098 | N/A | +0.0098 | ∞ |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | TP | persistent | +0.0057 | N/A | +0.0057 | ∞ |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Median | persistent | +0.0018 | N/A | +0.0018 | ∞ |
| `combo_mean__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0016 | N/A | -0.0016 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0036 | N/A | -0.0036 | ∞ |
| `combo_rank_min__bar_body_rng_0__rally_strength_max` | FP | immediate | -0.0054 | N/A | -0.0054 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | FP | immediate | -0.0077 | N/A | -0.0077 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | FP | immediate | -0.0120 | N/A | -0.0120 | ∞ |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | FP | immediate | -0.0121 | N/A | -0.0121 | ∞ |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0148 | N/A | -0.0148 | ∞ |
| `combo_max__max_up_ret__volume_price_confirmation` | FP | immediate | -0.0151 | N/A | -0.0151 | ∞ |
| `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration` | FP | immediate | -0.0159 | N/A | -0.0159 | ∞ |
| `combo_mean__bar_body_rng_0__rally_strength_max` | FP | immediate | -0.0159 | N/A | -0.0159 | ∞ |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | FP | immediate | -0.0185 | N/A | -0.0185 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0192 | N/A | -0.0192 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0238 | N/A | -0.0238 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | FP | immediate | -0.0265 | N/A | -0.0265 | ∞ |
| `combo_min__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0303 | N/A | -0.0303 | ∞ |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | FP | immediate | -0.0318 | N/A | -0.0318 | ∞ |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | FP | immediate | -0.0322 | N/A | -0.0322 | ∞ |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | FP | immediate | -0.0381 | N/A | -0.0381 | ∞ |
| `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0` | FP | immediate | -0.0399 | N/A | -0.0399 | ∞ |
| `combo_max__opening_drive_thrust_ratio__rally_strength_max` | FP | immediate | -0.0405 | N/A | -0.0405 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0421 | N/A | -0.0421 | ∞ |
| `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret` | FP | immediate | -0.0423 | N/A | -0.0423 | ∞ |
| `combo_max__bar_body_rng_0__rally_strength_max` | FP | immediate | -0.0448 | N/A | -0.0448 | ∞ |
| `opening_drive_thrust_ratio` | FP | immediate | -0.0464 | N/A | -0.0464 | ∞ |
| `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0526 | N/A | -0.0526 | ∞ |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0563 | N/A | -0.0563 | ∞ |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0570 | N/A | -0.0570 | ∞ |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0572 | N/A | -0.0572 | ∞ |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | FP | immediate | -0.0587 | N/A | -0.0587 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0595 | N/A | -0.0595 | ∞ |
| `combo_max__first_bar_return__rally_strength_max` | FP | immediate | -0.0599 | N/A | -0.0599 | ∞ |
| `combo_diff__max_up_ret__keltner_squeeze_width` | FP | immediate | -0.0616 | N/A | -0.0616 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | FP | immediate | -0.0654 | N/A | -0.0654 | ∞ |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0681 | N/A | -0.0681 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0689 | N/A | -0.0689 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0` | FP | immediate | -0.0711 | N/A | -0.0711 | ∞ |
| `combo_rank_min__max_up_ret__rally_strength_max` | FP | immediate | -0.0714 | N/A | -0.0714 | ∞ |
| `combo_min__max_up_ret__rally_strength_max` | FP | immediate | -0.0714 | N/A | -0.0714 | ∞ |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0737 | N/A | -0.0737 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | FP | immediate | -0.0770 | N/A | -0.0770 | ∞ |
| `combo_max__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0771 | N/A | -0.0771 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | FP | immediate | -0.0776 | N/A | -0.0776 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0811 | N/A | -0.0811 | ∞ |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | FP | immediate | -0.0816 | N/A | -0.0816 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | FP | immediate | -0.0825 | N/A | -0.0825 | ∞ |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | FP | immediate | -0.0851 | N/A | -0.0851 | ∞ |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0854 | N/A | -0.0854 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__rally_strength_max` | FP | immediate | -0.0867 | N/A | -0.0867 | ∞ |
| `combo_max__max_up_ret__rally_strength_max` | FP | immediate | -0.0883 | N/A | -0.0883 | ∞ |
| `combo_mean__max_up_ret__rally_strength_max` | FP | immediate | -0.0909 | N/A | -0.0909 | ∞ |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0913 | N/A | -0.0913 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | FP | immediate | -0.0930 | N/A | -0.0930 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0930 | N/A | -0.0930 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.1027 | N/A | -0.1027 | ∞ |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.1035 | N/A | -0.1035 | ∞ |

**Decay distribution**: immediate=56, fast(1-2y)=0, gradual=0, persistent=90

**FP decay trajectories:**

- `combo_max__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.104
- `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.103
- `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.093
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct`: Y1:-0.093
- `combo_rank_max__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.091
- `combo_mean__max_up_ret__rally_strength_max`: Y1:-0.091
- `combo_max__max_up_ret__rally_strength_max`: Y1:-0.088
- `combo_mean__volatility_expansion_trend_vector__rally_strength_max`: Y1:-0.087
- `combo_rank_min__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.085
- `combo_ratio__max_up_ret__keltner_squeeze_width`: Y1:-0.085
- `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max`: Y1:-0.083
- `combo_max__first_bar_return__volatility_expansion_trend_vector`: Y1:-0.082
- `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.081
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early`: Y1:-0.078
- `combo_max__max_up_ret__bar_body_rng_0`: Y1:-0.077
- `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`: Y1:-0.077
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:-0.074
- `combo_min__max_up_ret__rally_strength_max`: Y1:-0.071
- `combo_rank_min__max_up_ret__rally_strength_max`: Y1:-0.071
- `combo_tri_median__opening_drive_thrust_ratio__demark_setup_reversal_early__bar_body_rng_0`: Y1:-0.071
- `combo_min__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.069
- `combo_ratio__max_up_ret__volume_weighted_price_position`: Y1:-0.068
- `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`: Y1:-0.065
- `combo_diff__max_up_ret__keltner_squeeze_width`: Y1:-0.062
- `combo_max__first_bar_return__rally_strength_max`: Y1:-0.060
- `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.060
- `combo_clamp_diff__max_up_ret__keltner_squeeze_width`: Y1:-0.059
- `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.057
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:-0.057
- `combo_rank_max__max_up_ret__bar_body_rng_0`: Y1:-0.056
- `combo_ifelse__gap_pct__max_up_ret__volume_weighted_price_position`: Y1:-0.053
- `opening_drive_thrust_ratio`: Y1:-0.046
- `combo_max__bar_body_rng_0__rally_strength_max`: Y1:-0.045
- `combo_ifelse__gap_pct__yesterday_early_momentum__max_up_ret`: Y1:-0.042
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`: Y1:-0.042
- `combo_max__opening_drive_thrust_ratio__rally_strength_max`: Y1:-0.041
- `combo_tri_median__max_up_ret__demark_setup_reversal_early__bar_body_rng_0`: Y1:-0.040
- `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`: Y1:-0.038
- `combo_rel_diff__max_up_ret__keltner_squeeze_width`: Y1:-0.032
- `combo_diff__max_up_ret__demark_setup_reversal_early`: Y1:-0.032
- `combo_min__max_up_ret__volume_weighted_price_position`: Y1:-0.030
- `combo_max__opening_drive_thrust_ratio__bar_ret_0`: Y1:-0.026
- `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.024
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.019
- `combo_max__volatility_expansion_trend_vector__volume_price_confirmation`: Y1:-0.019
- `combo_mean__bar_body_rng_0__rally_strength_max`: Y1:-0.016
- `combo_clamp_diff__volume_weighted_price_position__volume_weighted_momentum_acceleration`: Y1:-0.016
- `combo_max__max_up_ret__volume_price_confirmation`: Y1:-0.015
- `combo_sig_product__max_up_ret__bar_body_rng_0`: Y1:-0.015
- `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return`: Y1:-0.012
- `combo_sig_product__max_up_ret__bar_ret_0`: Y1:-0.012
- `combo_clamp_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Y1:-0.008
- `combo_rank_min__bar_body_rng_0__rally_strength_max`: Y1:-0.005
- `combo_min__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.004
- `combo_min__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.002
- `combo_mean__first_bar_return__volume_weighted_price_position`: Y1:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.744±0.031 | 0.727±0.015 | 24% | USEFUL |
| ic_ir | 0.668±0.081 | 0.610±0.075 | 46% | USEFUL |
| p_value | 0.000±0.000 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.894±0.051 | 0.583±0.416 | 24% | USEFUL |
| deflated_ic | 0.213±0.017 | 0.224±0.029 | 71% | WEAK |
| overall_ic | 0.213±0.017 | 0.224±0.029 | 70% | WEAK |
| raw_ic | 0.095±0.008 | 0.099±0.006 | 39% | USEFUL |

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.745±0.027 | 0.736±0.045 | 75% | WEAK |
| ic_ir | 0.676±0.073 | 0.683±0.135 | 72% | WEAK |
| p_value | 0.000±0.000 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.893±0.046 | 0.888±0.060 | 76% | WEAK |
| deflated_ic | 0.209±0.023 | 0.233±0.019 | 49% | USEFUL |
| overall_ic | 0.210±0.023 | 0.233±0.019 | 48% | USEFUL |
| raw_ic | 0.117±0.013 | 0.124±0.014 | 92% | USELESS |

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.743±0.045 | 0.753±0.061 | 73% | WEAK |
| ic_ir | 0.683±0.142 | 0.712±0.202 | 72% | WEAK |
| p_value | 0.000±0.001 | 0.000±0.001 | 76% | WEAK |
| max_corr | 0.895±0.063 | 0.869±0.139 | 38% | USEFUL |
| deflated_ic | 0.231±0.028 | 0.242±0.052 | 59% | WEAK |
| overall_ic | 0.231±0.028 | 0.242±0.052 | 58% | WEAK |
| raw_ic | 0.121±0.010 | 0.124±0.017 | 65% | WEAK |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**B2 Rolling Guard**: 1/20 top rejects are profitable (5%)

- `combo_sig_product__star50_limit_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1588, Lock IC=+0.1188, Sharpe=+0.7891

**Temporal Validation Gate**: 2/20 top rejects are profitable (10%)

- `combo_sig_product__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.2020, Lock IC=+0.0146, Sharpe=+0.4344
- `combo_sig_product__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.2018, Lock IC=+0.0145, Sharpe=+0.4344

**BH-FDR Gate**: 2/2 top rejects are profitable (100%)

- `combo_diff__early_vwap_acceleration__early_late_momentum_divergence`: Train IC=+0.0663, Lock IC=+0.0565, Sharpe=+0.2261
- `combo_z_diff__early_vwap_acceleration__early_late_momentum_divergence`: Train IC=+0.0663, Lock IC=+0.0565, Sharpe=+0.2261

**B3 Composite Floor**: 2/11 top rejects are profitable (18%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.1403, Lock IC=+0.1448, Sharpe=+0.9422
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1403, Lock IC=+0.1448, Sharpe=+0.9422

**B4 Correlation Gate**: 2/20 top rejects are profitable (10%)

- `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Sharpe=+0.4322
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2546, Lock IC=+0.0510, Sharpe=+0.4322

### 500ETF — `single`

**7-Year Jackknife**: 6/20 top rejects are profitable (30%)

- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2279, Lock IC=+0.1062, Sharpe=+1.3424

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_rel_diff__max_up_ret__shaved_bar_trend_conviction`: Train IC=+0.1876, Lock IC=+0.0337, Sharpe=+0.2895
- `combo_rank_max__demark_setup_reversal_early__body_size_progression`: Train IC=+0.2054, Lock IC=+0.1227, Sharpe=+0.0641

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Sharpe=+0.1323
- `combo_tri_z_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2348, Lock IC=+0.0667, Sharpe=+0.1323

**B6 Yearly IC CV Gate**: 9/20 top rejects are profitable (45%)

- `combo_tri_min__smooth_momentum_structure__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1487, Lock IC=+0.0208, Sharpe=+1.6556
- `combo_tri_mean__max_up_ret__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1510, Lock IC=+0.0703, Sharpe=+0.4003
- `combo_tri_z_mean__max_up_ret__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1510, Lock IC=+0.0703, Sharpe=+0.4003

**B6 Temporal Stability Gate**: 9/20 top rejects are profitable (45%)

- `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2637, Lock IC=+0.0385, Sharpe=+0.8517
- `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2513, Lock IC=+0.0798, Sharpe=+0.7199
- `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2513, Lock IC=+0.0798, Sharpe=+0.7199

**B4 Correlation Gate**: 7/20 top rejects are profitable (35%)

- `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.2557, Lock IC=+0.0706, Sharpe=+0.8062
- `combo_tri_z_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.2557, Lock IC=+0.0706, Sharpe=+0.8062
- `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0`: Train IC=+0.2515, Lock IC=+0.0869, Sharpe=+0.6688

### 159915ETF — `single`

**7-Year Jackknife**: 10/20 top rejects are profitable (50%)

- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Sharpe=+3.8591
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Sharpe=+3.8591
- `combo_mean__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2233, Lock IC=+0.2142, Sharpe=+3.5556

**B2 Rolling Guard**: 16/20 top rejects are profitable (80%)

- `combo_diff__star50_limit_proximity_early__early_late_momentum_divergence`: Train IC=+0.1899, Lock IC=+0.2161, Sharpe=+2.5866
- `combo_z_diff__star50_limit_proximity_early__early_late_momentum_divergence`: Train IC=+0.1899, Lock IC=+0.2161, Sharpe=+2.5866
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression`: Train IC=+0.2549, Lock IC=+0.1835, Sharpe=+2.4160

**BH-FDR Gate**: 1/3 top rejects are profitable (33%)

- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Sharpe=+0.2891

**B3 Composite Floor**: 3/20 top rejects are profitable (15%)

- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.2093, Lock IC=+0.0868, Sharpe=+2.0454
- `combo_min__rally_strength_max__volume_price_confirmation`: Train IC=+0.2305, Lock IC=+0.0793, Sharpe=+0.3427
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2240, Lock IC=+0.0112, Sharpe=+0.0064

**B6 Temporal Stability Gate**: 11/20 top rejects are profitable (55%)

- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3177, Lock IC=+0.0619, Sharpe=+1.2230
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3527, Lock IC=+0.0637, Sharpe=+0.7890
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3082, Lock IC=+0.0585, Sharpe=+0.4764

**B4 Correlation Gate**: 12/20 top rejects are profitable (60%)

- `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.3187, Lock IC=+0.1205, Sharpe=+2.3935
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.3014, Lock IC=+0.1495, Sharpe=+1.8753
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.3095, Lock IC=+0.0868, Sharpe=+1.5647

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1192 | 78 | 49 | 12 | 17 | 63% | 22% |
| B2 Rolling Guard | 121 | 78 | 48 | 11 | 19 | 62% | 24% |
| Temporal Validation Gate | 91 | 78 | 50 | 6 | 22 | 64% | 28% |
| BH-FDR Gate | 2 | 2 | 0 | 0 | 2 | 0% | 100% |
| B3 Composite Floor | 11 | 11 | 4 | 5 | 2 | 36% | 18% |
| B6 Yearly IC CV Gate | 6 | 6 | 5 | 1 | 0 | 83% | 0% |
| B4 Correlation Gate | 107 | 78 | 67 | 8 | 3 | 86% | 4% |

**7-Year Jackknife** — top TP casualties:
- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0002, Lock IC=+0.2376, Sharpe=+2.4816
- `combo_tri_min__smooth_momentum_structure__opening_drive_thrust_ratio__volume_concentration`: Train IC=+0.0547, Lock IC=+0.2366, Sharpe=+2.4008
- `combo_min__volume_weighted_momentum_acceleration__opening_drive_thrust_ratio`: Train IC=-0.0068, Lock IC=+0.2186, Sharpe=+2.3735

**B2 Rolling Guard** — top TP casualties:
- `volume_acceleration`: Train IC=+0.0666, Lock IC=+0.0695, Sharpe=+1.5046
- `volume_trend_intraday`: Train IC=+0.0506, Lock IC=+0.0482, Sharpe=+0.9660
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__rbreaker_buy_setup_proximity_early`: Train IC=+0.1412, Lock IC=+0.1517, Sharpe=+0.9530

**Temporal Validation Gate** — top TP casualties:
- `ema12_dist`: Train IC=+0.0434, Lock IC=+0.1158, Sharpe=+3.3549
- `sma10_dist`: Train IC=+0.0453, Lock IC=+0.1136, Sharpe=+2.6363
- `sma20_dist`: Train IC=+0.0648, Lock IC=+0.1054, Sharpe=+2.5915

**BH-FDR Gate** — top TP casualties:
- `combo_diff__early_vwap_acceleration__early_late_momentum_divergence`: Train IC=+0.0663, Lock IC=+0.0565, Sharpe=+0.2261
- `combo_z_diff__early_vwap_acceleration__early_late_momentum_divergence`: Train IC=+0.0663, Lock IC=+0.0565, Sharpe=+0.2261

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2753 | 78 | 48 | 9 | 21 | 62% | 27% |
| B2 Rolling Guard | 442 | 78 | 50 | 12 | 16 | 64% | 21% |
| Temporal Validation Gate | 148 | 78 | 29 | 39 | 10 | 37% | 13% |
| B3 Composite Floor | 63 | 63 | 22 | 30 | 11 | 35% | 17% |
| B6 Yearly IC CV Gate | 22 | 22 | 4 | 8 | 10 | 18% | 45% |
| B6 Temporal Stability Gate | 396 | 78 | 49 | 9 | 20 | 63% | 26% |
| B4 Correlation Gate | 266 | 78 | 38 | 13 | 27 | 49% | 35% |

**7-Year Jackknife** — top TP casualties:
- `star50_limit_proximity_early`: Train IC=+0.0530, Lock IC=+0.1859, Sharpe=+2.6499
- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265

**B2 Rolling Guard** — top TP casualties:
- `combo_sig_product__star50_limit_proximity_early__max_down_ret`: Train IC=+0.1769, Lock IC=+0.1949, Sharpe=+1.1683
- `combo_abs_diff__early_body_momentum__max_down_ret`: Train IC=+0.0325, Lock IC=+0.1804, Sharpe=+1.1222
- `combo_abs_diff__opening_momentum_score__max_down_ret`: Train IC=+0.0325, Lock IC=+0.1804, Sharpe=+1.1222

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1487, Lock IC=+0.0208, Sharpe=+1.6556
- `combo_z_sum__trend_day_regime_conviction__h2_l2_pullback_continuation`: Train IC=+0.1133, Lock IC=+0.0488, Sharpe=+1.1565
- `combo_tri_mean__max_up_ret__smooth_momentum_structure__star50_limit_proximity_early`: Train IC=+0.1510, Lock IC=+0.0703, Sharpe=+0.4003

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1197, Lock IC=+0.1695, Sharpe=+2.4568
- `combo_z_diff__star50_limit_proximity_early__demark_setup_reversal_early`: Train IC=+0.1197, Lock IC=+0.1695, Sharpe=+2.4568
- `combo_rank_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2119, Lock IC=+0.0910, Sharpe=+2.2390

**B4 Correlation Gate** — top TP casualties:
- `combo_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1745, Lock IC=+0.1332, Sharpe=+1.6190
- `combo_z_sum__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.1745, Lock IC=+0.1332, Sharpe=+1.6190
- `combo_tri_min__star50_limit_proximity_early__trend_day_regime_conviction__bar_ret_0`: Train IC=+0.2241, Lock IC=+0.0746, Sharpe=+1.3197

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1950 | 78 | 33 | 11 | 34 | 42% | 44% |
| B2 Rolling Guard | 246 | 78 | 37 | 11 | 30 | 47% | 38% |
| Temporal Validation Gate | 95 | 78 | 25 | 33 | 20 | 32% | 26% |
| BH-FDR Gate | 3 | 3 | 2 | 0 | 1 | 67% | 33% |
| B3 Composite Floor | 112 | 78 | 19 | 36 | 23 | 24% | 29% |
| B6 Yearly IC CV Gate | 4 | 4 | 2 | 2 | 0 | 50% | 0% |
| B6 Temporal Stability Gate | 88 | 78 | 6 | 43 | 29 | 8% | 37% |
| B4 Correlation Gate | 258 | 78 | 17 | 25 | 36 | 22% | 46% |

**7-Year Jackknife** — top TP casualties:
- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Sharpe=+3.8591
- `combo_z_sum__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Sharpe=+3.8591
- `combo_mean__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.2092, Sharpe=+3.8591

**B2 Rolling Guard** — top TP casualties:
- `combo_min__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1815, Lock IC=+0.2385, Sharpe=+2.9556
- `combo_min__rbreaker_buy_setup_proximity_early__directional_volume_signature`: Train IC=+0.1815, Lock IC=+0.2385, Sharpe=+2.9556
- `combo_diff__star50_limit_proximity_early__early_late_momentum_divergence`: Train IC=+0.1899, Lock IC=+0.2161, Sharpe=+2.5866

**Temporal Validation Gate** — top TP casualties:
- `volume_surge_direction`: Train IC=+0.1617, Lock IC=+0.1277, Sharpe=+2.7834
- `turtle_breakout_strength_early`: Train IC=+0.0414, Lock IC=+0.1809, Sharpe=+2.1497
- `combo_rel_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1814, Lock IC=+0.1408, Sharpe=+2.1053

**BH-FDR Gate** — top TP casualties:
- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Sharpe=+0.2891

**B3 Composite Floor** — top TP casualties:
- `combo_rank_max__bar_body_rng_0__directional_volume_signature`: Train IC=+0.1709, Lock IC=+0.1571, Sharpe=+3.0812
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__yesterday_pm_return`: Train IC=+0.1378, Lock IC=+0.0042, Sharpe=+2.7545
- `combo_product__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`: Train IC=+0.1221, Lock IC=+0.2220, Sharpe=+2.5354

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3177, Lock IC=+0.0619, Sharpe=+1.2230
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2573, Lock IC=+0.0958, Sharpe=+1.1483
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2821, Lock IC=+0.1124, Sharpe=+1.0660

**B4 Correlation Gate** — top TP casualties:
- `combo_mean__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2330, Lock IC=+0.1841, Sharpe=+2.8972
- `combo_z_sum__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2330, Lock IC=+0.1841, Sharpe=+2.8972
- `combo_min__star50_limit_proximity_early__directional_volume_signature`: Train IC=+0.2350, Lock IC=+0.2336, Sharpe=+2.7172

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (91 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 73 | 50 | 44 | 6 | 0 | 88% | 12% |
| recency_ratio >= 2.5 (late-concentrated) | 8 | 8 | 7 | 0 | 1 | 88% | 0% |

### 500ETF — `single` (148 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 139 | 50 | 8 | 4 | 38 | 16% | 8% |
| recency_ratio >= 2.5 (late-concentrated) | 8 | 8 | 8 | 0 | 0 | 100% | 0% |

### 159915ETF — `single` (95 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 80 | 50 | 11 | 12 | 27 | 22% | 24% |
| recency_ratio >= 2.5 (late-concentrated) | 13 | 13 | 9 | 1 | 3 | 69% | 8% |

**Top TP killed by recency_ratio cap:**
- `volume_surge_direction`: Train IC=+0.1617, Lock IC=+0.1277, Sharpe=+2.7834

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+1.53). Threshold 0.498 → 93% accuracy.
- `n_negative_regimes`: FP is lower (d=-1.00). Threshold 0.000 → 90% accuracy.
- `recency_ratio`: FP is higher (d=+0.68). Threshold 0.282 → 90% accuracy.
- `half_ratio`: FP is higher (d=+0.65). Threshold 0.578 → 90% accuracy.
- `n_negative_years`: FP is higher (d=+0.58). Threshold 0.000 → 90% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-0.55). Threshold 0.025 → 90% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/38
- Decaying signal (half ratio < 0.3): 0/38
- Weak component (CV > 2.0): 0/38
- Regime-dependent (≥2 negative regimes): 0/38

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `half_ratio`: FP is higher (d=+1.39). Threshold 0.696 → 90% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-1.34). Threshold 0.018 → 57% accuracy.
- `ic_cv`: FP is lower (d=-0.87). Threshold 0.221 → 57% accuracy.
- `recency_ratio`: FP is higher (d=+0.80). Threshold 0.681 → 80% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/24
- Decaying signal (half ratio < 0.3): 0/24
- Weak component (CV > 2.0): 0/24
- Regime-dependent (≥2 negative regimes): 0/24

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `half_ratio`: FP is higher (d=+1.07). Threshold 0.858 → 72% accuracy.
- `recency_ratio`: FP is higher (d=+1.05). Threshold 0.856 → 76% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/56
- Decaying signal (half ratio < 0.3): 0/56
- Weak component (CV > 2.0): 0/56
- Regime-dependent (≥2 negative regimes): 0/56

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `keltner_squeeze_width` | 4 | 0 | 4 | 100% |  |
| `trend_day_regime_conviction` | 2 | 0 | 2 | 100% |  |
| `smooth_momentum_structure` | 2 | 0 | 2 | 100% |  |
| `vwap_close_divergence_trend` | 7 | 0 | 7 | 100% | ⚠ TOXIC |
| `max_down_ret` | 4 | 0 | 4 | 100% |  |
| `early_order_flow_imbalance` | 4 | 0 | 4 | 100% |  |
| `morning_volume_weighted_momentum` | 7 | 0 | 7 | 100% | ⚠ TOXIC |
| `max_up_ret` | 56 | 14 | 70 | 80% | ⚠ TOXIC |
| `volume_weighted_price_position` | 21 | 6 | 27 | 78% |  |
| `opening_drive_thrust_ratio` | 35 | 11 | 46 | 76% |  |
| `first_bar_return` | 19 | 6 | 25 | 76% |  |
| `rally_strength_max` | 11 | 4 | 15 | 73% |  |
| `demark_setup_reversal_early` | 5 | 2 | 7 | 71% |  |
| `trend_bar_close_consistency` | 2 | 1 | 3 | 67% |  |
| `volatility_expansion_trend_vector` | 11 | 6 | 17 | 65% |  |
| `bar_body_rng_0` | 33 | 20 | 53 | 62% |  |
| `bar_ret_0` | 18 | 11 | 29 | 62% |  |
| `net_volume_flow` | 2 | 2 | 4 | 50% |  |
| `early_body_momentum` | 1 | 1 | 2 | 50% |  |
| `gap_pct` | 3 | 5 | 8 | 38% |  |
| `rbreaker_buy_setup_proximity_early` | 2 | 4 | 6 | 33% |  |
| `rbreaker_sell_setup_proximity_early` | 10 | 29 | 39 | 26% |  |
| `volume_weighted_momentum_acceleration` | 1 | 4 | 5 | 20% |  |
| `volume_price_confirmation` | 2 | 9 | 11 | 18% |  |
| `limit_down_proximity_early` | 1 | 9 | 10 | 10% |  |
| `star50_limit_proximity_early` | 2 | 22 | 24 | 8% |  |
| `directional_volume_signature` | 0 | 9 | 9 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=61, TP=51, FP rate=54%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=11, TP=8, FP rate=58%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=33, TP=16, FP rate=67%

