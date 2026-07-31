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
| 300ETF | single | 123 | 26 | `[17, 10, 9, 8, 7, 4, 3, 3, 3, 3, 3, 2, ... (26 clusters)]` | 0.1965 | 112 | 7 | 4 | 91% | 0.06 |
| 500ETF | single | 148 | 50 | `[9, 8, 7, 6, 5, 5, 4, 3, 3, 3, 3, 3, ... (50 clusters)]` | 0.2717 | 71 | 44 | 33 | 48% | 0.37 |
| 159915ETF | single | 178 | 53 | `[12, 10, 8, 8, 7, 7, 6, 6, 5, 4, 3, 2, ... (53 clusters)]` | 0.2630 | 79 | 39 | 60 | 44% | 0.45 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=112, TP=4)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ic_cv | 0.694 | 0.528 | 0.678 | 0.520 | +1.77 | 0.498 | 97% |
| n_negative_years | 0.393 | 0.000 | 0.000 | 0.000 | +0.90 | 0.000 | 96% |
| n_negative_regimes | 0.036 | 0.250 | 0.000 | 0.000 | -0.64 | 0.000 | 96% |
| ic_std_across_regimes | 0.049 | 0.056 | 0.045 | 0.054 | -0.61 | 0.025 | 96% |
| half_ratio | 0.811 | 0.717 | 0.754 | 0.718 | +0.54 | 0.454 | 96% |
| weak_link_cv | 0.841 | 0.815 | 0.731 | 0.815 | +0.17 | 0.660 | 95% |
| recency_ratio | 0.451 | 0.418 | 0.379 | 0.426 | +0.15 | 0.064 | 96% |

### 500ETF — `single` (FP=71, TP=33)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 1.020 | 0.822 | 0.947 | 0.751 | +0.62 | 0.578 | 73% |
| ic_std_across_regimes | 0.040 | 0.045 | 0.038 | 0.042 | -0.36 | 0.014 | 67% |
| recency_ratio | 1.013 | 0.902 | 0.899 | 0.817 | +0.22 | 0.474 | 70% |
| n_negative_years | 0.042 | 0.030 | 0.000 | 0.000 | +0.06 | 0.000 | 67% |
| n_negative_regimes | 0.042 | 0.030 | 0.000 | 0.000 | +0.06 | 0.000 | 67% |
| weak_link_cv | 0.466 | 0.458 | 0.482 | 0.482 | +0.05 | 0.334 | 69% |
| ic_cv | 0.366 | 0.371 | 0.326 | 0.365 | -0.05 | 0.169 | 67% |

### 159915ETF — `single` (FP=79, TP=60)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recency_ratio | 1.263 | 0.755 | 1.056 | 0.716 | +0.98 | 0.790 | 73% |
| half_ratio | 1.270 | 0.910 | 1.135 | 0.850 | +0.92 | 0.797 | 72% |
| ic_cv | 0.409 | 0.341 | 0.370 | 0.331 | +0.70 | 0.298 | 67% |
| n_negative_years | 0.051 | 0.000 | 0.000 | 0.000 | +0.33 | 0.000 | 56% |
| weak_link_cv | 0.537 | 0.500 | 0.581 | 0.436 | +0.28 | 0.575 | 63% |
| ic_std_across_regimes | 0.024 | 0.023 | 0.023 | 0.020 | +0.17 | 0.015 | 62% |
| n_negative_regimes | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 56% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0976, Sharpe=-3.9900)
- Admission: Train IC=+0.1500, Deflated=+0.1500, IR=0.53, Mono=0.71, p=0.0034, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156 | 2022: +0.028 | 2023: +0.137 | 2024: +0.039 | 2025: +0.058 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.055 | 2017: +0.207 | 2018: +0.385 | 2019: +0.133 | 2020: +0.033 | 2021: +0.203 | 2022: +0.122 | 2023: +0.108 | 2024: +0.061 | 2025: +0.105 | 2026: -0.330
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=0.62, Recency ratio=0.33
- Early IC=+0.1460, Recent IC=+0.0481, 1st-half IC=+0.1113, 2nd-half IC=+0.0691, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.085, Q3_mid=+0.052, Q4=+0.084, Q5_high_vol=+0.164

**`trend_bar_close_consistency`** (Lock IC=-0.2260, Sharpe=-3.9593)
- Admission: Train IC=+0.1205, Deflated=+0.1196, IR=0.32, Mono=0.67, p=0.0134, MaxCorr=0.90
- Yearly Linear ICs: 2015: -0.065 | 2016: +0.094 | 2017: -0.105 | 2018: +0.044 | 2019: -0.014 | 2020: +0.006 | 2021: +0.176 | 2022: +0.025 | 2023: +0.079 | 2024: +0.012 | 2025: +0.060 | 2026: -0.226
- Yearly Tail ICs:   2015: -0.005 | 2016: +0.207 | 2017: -0.096 | 2018: +0.005 | 2019: +0.024 | 2020: +0.028 | 2021: +0.161 | 2022: +0.176 | 2023: +0.075 | 2024: +0.159 | 2025: +0.132 | 2026: -0.289
- IC CV=1.15, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=2.42
- Early IC=+0.0148, Recent IC=+0.0359, 1st-half IC=+0.0514, 2nd-half IC=+0.0598, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.001, Q2=+0.031, Q3_mid=+0.062, Q4=+0.074, Q5_high_vol=+0.085

**`combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.2112, Sharpe=-3.6368)
- Admission: Train IC=+0.2304, Deflated=+0.2294, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.037 | 2017: +0.038 | 2018: +0.152 | 2019: +0.040 | 2020: +0.012 | 2021: +0.187 | 2022: +0.042 | 2023: +0.199 | 2024: +0.041 | 2025: +0.106 | 2026: -0.211
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.154 | 2017: +0.194 | 2018: +0.448 | 2019: +0.247 | 2020: +0.184 | 2021: +0.337 | 2022: +0.239 | 2023: +0.191 | 2024: +0.135 | 2025: +0.140 | 2026: -0.419
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.0958, Recent IC=+0.0732, 1st-half IC=+0.0933, 2nd-half IC=+0.0952, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.094, Q3_mid=+0.055, Q4=+0.060, Q5_high_vol=+0.177

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.2114, Sharpe=-3.6368)
- Admission: Train IC=+0.2303, Deflated=+0.2293, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.037 | 2017: +0.038 | 2018: +0.152 | 2019: +0.040 | 2020: +0.012 | 2021: +0.187 | 2022: +0.042 | 2023: +0.199 | 2024: +0.041 | 2025: +0.106 | 2026: -0.211
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.154 | 2017: +0.194 | 2018: +0.448 | 2019: +0.247 | 2020: +0.184 | 2021: +0.335 | 2022: +0.239 | 2023: +0.190 | 2024: +0.133 | 2025: +0.140 | 2026: -0.419
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.0956, Recent IC=+0.0731, 1st-half IC=+0.0933, 2nd-half IC=+0.0951, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.094, Q3_mid=+0.055, Q4=+0.060, Q5_high_vol=+0.177

**`combo_rank_max__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.1417, Sharpe=-3.5565)
- Admission: Train IC=+0.2194, Deflated=+0.2192, IR=0.61, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.091 | 2017: +0.001 | 2018: +0.189 | 2019: +0.081 | 2020: +0.043 | 2021: +0.179 | 2022: +0.023 | 2023: +0.193 | 2024: +0.037 | 2025: +0.074 | 2026: -0.141
- Yearly Tail ICs:   2015: +0.050 | 2016: -0.025 | 2017: -0.077 | 2018: +0.407 | 2019: +0.159 | 2020: +0.149 | 2021: +0.402 | 2022: +0.157 | 2023: +0.275 | 2024: +0.121 | 2025: +0.156 | 2026: -0.301
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.41
- Early IC=+0.1347, Recent IC=+0.0550, 1st-half IC=+0.1200, 2nd-half IC=+0.0853, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.104, Q3_mid=+0.053, Q4=+0.098, Q5_high_vol=+0.199

**`always_in_trend_persistence`** (Lock IC=-0.2597, Sharpe=-3.4587)
- Admission: Train IC=+0.1511, Deflated=+0.1496, IR=0.50, Mono=0.70, p=0.0034, MaxCorr=0.68
- Yearly Linear ICs: 2015: -0.030 | 2016: +0.075 | 2017: -0.026 | 2018: +0.074 | 2019: +0.026 | 2020: -0.016 | 2021: +0.128 | 2022: +0.110 | 2023: +0.093 | 2024: -0.004 | 2025: +0.051 | 2026: -0.260
- Yearly Tail ICs:   2015: -0.155 | 2016: +0.144 | 2017: -0.007 | 2018: +0.037 | 2019: +0.136 | 2020: +0.071 | 2021: +0.219 | 2022: +0.282 | 2023: +0.054 | 2024: +0.187 | 2025: +0.191 | 2026: -0.267
- IC CV=0.85, Neg years (linear/tail)=2/0 of 8, Half ratio=1.28, Recency ratio=0.47
- Early IC=+0.0503, Recent IC=+0.0237, 1st-half IC=+0.0543, 2nd-half IC=+0.0697, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.060, Q3_mid=+0.091, Q4=+0.116, Q5_high_vol=+0.021

**`combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.2002, Sharpe=-3.3600)
- Admission: Train IC=+0.1986, Deflated=+0.1980, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.91
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

**`combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.1637, Sharpe=-2.8975)
- Admission: Train IC=+0.2166, Deflated=+0.2163, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.083 | 2017: -0.017 | 2018: +0.154 | 2019: +0.062 | 2020: +0.049 | 2021: +0.179 | 2022: +0.032 | 2023: +0.199 | 2024: +0.038 | 2025: +0.089 | 2026: -0.164
- Yearly Tail ICs:   2015: +0.051 | 2016: +0.079 | 2017: -0.047 | 2018: +0.287 | 2019: +0.233 | 2020: +0.167 | 2021: +0.342 | 2022: +0.236 | 2023: +0.312 | 2024: +0.157 | 2025: +0.149 | 2026: -0.404
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.59
- Early IC=+0.1081, Recent IC=+0.0636, 1st-half IC=+0.1085, 2nd-half IC=+0.0912, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.088, Q3_mid=+0.064, Q4=+0.088, Q5_high_vol=+0.200

**`combo_tri_mean__volume_weighted_momentum_acceleration__max_up_ret__first_bar_return`** (Lock IC=-0.1212, Sharpe=-2.8806)
- Admission: Train IC=+0.1770, Deflated=+0.1764, IR=0.43, Mono=0.66, p=0.0008, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.044 | 2017: -0.070 | 2018: +0.034 | 2019: +0.003 | 2020: +0.027 | 2021: +0.083 | 2022: +0.014 | 2023: +0.073 | 2024: +0.071 | 2025: +0.002 | 2026: -0.121
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.111 | 2017: -0.133 | 2018: +0.205 | 2019: -0.085 | 2020: +0.029 | 2021: +0.243 | 2022: +0.458 | 2023: +0.141 | 2024: +0.301 | 2025: +0.184 | 2026: -0.203
- IC CV=0.81, Neg years (linear/tail)=0/1 of 8, Half ratio=1.29, Recency ratio=2.01
- Early IC=+0.0182, Recent IC=+0.0366, 1st-half IC=+0.0324, 2nd-half IC=+0.0419, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.73, neg years=0)
- Regime ICs: Q1_low_vol=+0.023, Q2=-0.003, Q3_mid=+0.031, Q4=+0.025, Q5_high_vol=+0.104

**`combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1994, Sharpe=-2.8678)
- Admission: Train IC=+0.2195, Deflated=+0.2191, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.061 | 2017: -0.007 | 2018: +0.167 | 2019: +0.067 | 2020: +0.015 | 2021: +0.184 | 2022: +0.056 | 2023: +0.198 | 2024: +0.010 | 2025: +0.097 | 2026: -0.199
- Yearly Tail ICs:   2015: +0.152 | 2016: -0.060 | 2017: +0.143 | 2018: +0.445 | 2019: +0.199 | 2020: +0.182 | 2021: +0.385 | 2022: +0.184 | 2023: +0.151 | 2024: +0.121 | 2025: +0.237 | 2026: -0.384
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.46
- Early IC=+0.1166, Recent IC=+0.0533, 1st-half IC=+0.1058, 2nd-half IC=+0.0916, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.100, Q3_mid=+0.050, Q4=+0.090, Q5_high_vol=+0.181

**`combo_max__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.1522, Sharpe=-2.8623)
- Admission: Train IC=+0.2181, Deflated=+0.2181, IR=0.60, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.086 | 2017: -0.014 | 2018: +0.189 | 2019: +0.080 | 2020: +0.048 | 2021: +0.173 | 2022: +0.033 | 2023: +0.192 | 2024: +0.030 | 2025: +0.073 | 2026: -0.152
- Yearly Tail ICs:   2015: +0.096 | 2016: -0.034 | 2017: -0.058 | 2018: +0.351 | 2019: +0.185 | 2020: +0.219 | 2021: +0.373 | 2022: +0.169 | 2023: +0.234 | 2024: +0.141 | 2025: +0.210 | 2026: -0.342
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.38
- Early IC=+0.1347, Recent IC=+0.0516, 1st-half IC=+0.1201, 2nd-half IC=+0.0854, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.098, Q3_mid=+0.062, Q4=+0.101, Q5_high_vol=+0.203

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

**`combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1697, Sharpe=-2.7982)
- Admission: Train IC=+0.2286, Deflated=+0.2282, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.069 | 2017: +0.029 | 2018: +0.195 | 2019: +0.064 | 2020: +0.003 | 2021: +0.165 | 2022: +0.050 | 2023: +0.178 | 2024: +0.047 | 2025: +0.095 | 2026: -0.170
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.069 | 2017: +0.104 | 2018: +0.369 | 2019: +0.145 | 2020: +0.144 | 2021: +0.412 | 2022: +0.278 | 2023: +0.261 | 2024: +0.215 | 2025: +0.048 | 2026: -0.146
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.55
- Early IC=+0.1296, Recent IC=+0.0711, 1st-half IC=+0.1036, 2nd-half IC=+0.0963, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.102, Q3_mid=+0.048, Q4=+0.085, Q5_high_vol=+0.185

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.1395, Sharpe=-2.7529)
- Admission: Train IC=+0.1299, Deflated=+0.1306, IR=0.47, Mono=0.68, p=0.0094, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.109 | 2017: -0.030 | 2018: +0.169 | 2019: +0.105 | 2020: +0.008 | 2021: +0.165 | 2022: +0.042 | 2023: +0.201 | 2024: -0.013 | 2025: +0.056 | 2026: -0.140
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.188 | 2017: -0.149 | 2018: +0.339 | 2019: +0.153 | 2020: +0.048 | 2021: +0.256 | 2022: +0.262 | 2023: +0.435 | 2024: +0.028 | 2025: +0.147 | 2026: -0.238
- IC CV=0.82, Neg years (linear/tail)=1/0 of 8, Half ratio=0.74, Recency ratio=0.16
- Early IC=+0.1371, Recent IC=+0.0215, 1st-half IC=+0.1095, 2nd-half IC=+0.0814, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.085, Q3_mid=+0.048, Q4=+0.105, Q5_high_vol=+0.175

**`combo_sig_product__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1294, Sharpe=-2.7464)
- Admission: Train IC=+0.1814, Deflated=+0.1819, IR=0.49, Mono=0.66, p=0.0004, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.060 | 2016: +0.043 | 2017: -0.014 | 2018: +0.165 | 2019: +0.062 | 2020: +0.014 | 2021: +0.174 | 2022: +0.064 | 2023: +0.243 | 2024: +0.026 | 2025: +0.085 | 2026: -0.129
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.087 | 2017: +0.020 | 2018: +0.328 | 2019: +0.170 | 2020: -0.030 | 2021: +0.281 | 2022: +0.197 | 2023: +0.361 | 2024: +0.051 | 2025: +0.019 | 2026: -0.333
- IC CV=0.73, Neg years (linear/tail)=0/1 of 8, Half ratio=1.01, Recency ratio=0.49
- Early IC=+0.1132, Recent IC=+0.0556, 1st-half IC=+0.1055, 2nd-half IC=+0.1067, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.144, Q3_mid=+0.052, Q4=+0.139, Q5_high_vol=+0.100

**`combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.1947, Sharpe=-2.7376)
- Admission: Train IC=+0.1400, Deflated=+0.1391, IR=0.51, Mono=0.68, p=0.0060, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.061 | 2016: +0.080 | 2017: -0.089 | 2018: +0.092 | 2019: +0.030 | 2020: +0.037 | 2021: +0.128 | 2022: +0.046 | 2023: +0.107 | 2024: +0.056 | 2025: +0.071 | 2026: -0.195
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.092 | 2017: -0.143 | 2018: +0.096 | 2019: -0.044 | 2020: +0.095 | 2021: +0.252 | 2022: +0.187 | 2023: +0.221 | 2024: +0.182 | 2025: +0.155 | 2026: -0.205
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=1.10, Recency ratio=1.04
- Early IC=+0.0611, Recent IC=+0.0633, 1st-half IC=+0.0703, 2nd-half IC=+0.0774, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.73, neg years=0)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.037, Q3_mid=+0.057, Q4=+0.080, Q5_high_vol=+0.146

**`combo_ratio__first_bar_return__volume_surge_direction`** (Lock IC=-0.0939, Sharpe=-2.7239)
- Admission: Train IC=+0.1217, Deflated=+0.1214, IR=0.37, Mono=0.69, p=0.0130, MaxCorr=0.03
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.144 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.393 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.114
- IC CV=0.76, Neg years (linear/tail)=1/2 of 8, Half ratio=0.61, Recency ratio=0.27
- Early IC=+0.1185, Recent IC=+0.0324, 1st-half IC=+0.0942, 2nd-half IC=+0.0576, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.080, Q3_mid=+0.061, Q4=+0.060, Q5_high_vol=+0.144

**`combo_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.1087, Sharpe=-2.7122)
- Admission: Train IC=+0.2138, Deflated=+0.2139, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.115 | 2017: +0.115 | 2018: +0.285 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.249 | 2024: +0.186 | 2025: +0.049 | 2026: -0.298
- IC CV=0.70, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.28
- Early IC=+0.1447, Recent IC=+0.0402, 1st-half IC=+0.1084, 2nd-half IC=+0.0644, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.093, Q3_mid=+0.045, Q4=+0.083, Q5_high_vol=+0.153

**`combo_min__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.0557, Sharpe=-2.7098)
- Admission: Train IC=+0.1700, Deflated=+0.1699, IR=0.73, Mono=0.79, p=0.0010, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.050 | 2017: -0.021 | 2018: +0.257 | 2019: +0.069 | 2020: -0.002 | 2021: +0.106 | 2022: +0.081 | 2023: +0.165 | 2024: -0.010 | 2025: +0.121 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.447 | 2016: -0.292 | 2017: +0.023 | 2018: +0.219 | 2019: +0.082 | 2020: +0.089 | 2021: +0.289 | 2022: +0.220 | 2023: +0.279 | 2024: +0.133 | 2025: +0.246 | 2026: -0.349
- IC CV=0.83, Neg years (linear/tail)=2/0 of 8, Half ratio=0.89, Recency ratio=0.34
- Early IC=+0.1629, Recent IC=+0.0557, 1st-half IC=+0.1035, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.122, Q3_mid=+0.023, Q4=+0.128, Q5_high_vol=+0.134

**`combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1823, Sharpe=-2.6806)
- Admission: Train IC=+0.1930, Deflated=+0.1922, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.82
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
- Admission: Train IC=+0.1121, Deflated=+0.1122, IR=0.50, Mono=0.68, p=0.0220, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.110 | 2017: +0.021 | 2018: +0.150 | 2019: +0.052 | 2020: +0.036 | 2021: +0.202 | 2022: +0.006 | 2023: +0.139 | 2024: +0.051 | 2025: +0.044 | 2026: -0.143
- Yearly Tail ICs:   2015: +0.224 | 2016: -0.062 | 2017: +0.126 | 2018: +0.106 | 2019: +0.095 | 2020: -0.039 | 2021: +0.524 | 2022: +0.211 | 2023: +0.288 | 2024: +0.221 | 2025: +0.122 | 2026: -0.244
- IC CV=0.76, Neg years (linear/tail)=0/1 of 8, Half ratio=0.62, Recency ratio=0.47
- Early IC=+0.1009, Recent IC=+0.0473, 1st-half IC=+0.0971, 2nd-half IC=+0.0601, Neg regimes=0/5
- Weak component: `bar_vol_0` (CV=2.33, neg years=2)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.035, Q3_mid=+0.074, Q4=+0.047, Q5_high_vol=+0.197

**`combo_rank_max__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.1476, Sharpe=-2.5718)
- Admission: Train IC=+0.2146, Deflated=+0.2147, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.046 | 2018: +0.125 | 2019: +0.050 | 2020: +0.040 | 2021: +0.174 | 2022: +0.018 | 2023: +0.171 | 2024: +0.046 | 2025: +0.077 | 2026: -0.148
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.068 | 2017: -0.092 | 2018: +0.289 | 2019: +0.241 | 2020: +0.096 | 2021: +0.371 | 2022: +0.246 | 2023: +0.229 | 2024: +0.159 | 2025: +0.084 | 2026: -0.332
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.69
- Early IC=+0.0875, Recent IC=+0.0605, 1st-half IC=+0.0904, 2nd-half IC=+0.0853, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.066, Q3_mid=+0.042, Q4=+0.076, Q5_high_vol=+0.197

**`combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0781, Sharpe=-2.5628)
- Admission: Train IC=+0.2167, Deflated=+0.2167, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.151 | 2016: +0.104 | 2017: -0.029 | 2018: +0.209 | 2019: +0.125 | 2020: +0.012 | 2021: +0.145 | 2022: +0.067 | 2023: +0.165 | 2024: +0.050 | 2025: +0.077 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.128 | 2016: +0.212 | 2017: -0.114 | 2018: +0.210 | 2019: +0.257 | 2020: +0.065 | 2021: +0.415 | 2022: +0.311 | 2023: +0.241 | 2024: +0.149 | 2025: +0.245 | 2026: -0.150
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.38
- Early IC=+0.1670, Recent IC=+0.0637, 1st-half IC=+0.1215, 2nd-half IC=+0.0968, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.102, Q3_mid=+0.058, Q4=+0.076, Q5_high_vol=+0.236

**`combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1526, Sharpe=-2.5270)
- Admission: Train IC=+0.1705, Deflated=+0.1703, IR=0.54, Mono=0.69, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.107 | 2017: -0.014 | 2018: +0.192 | 2019: +0.061 | 2020: +0.033 | 2021: +0.161 | 2022: +0.012 | 2023: +0.143 | 2024: +0.062 | 2025: +0.064 | 2026: -0.153
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.181 | 2017: -0.108 | 2018: +0.160 | 2019: +0.188 | 2020: +0.033 | 2021: +0.303 | 2022: +0.172 | 2023: +0.339 | 2024: +0.200 | 2025: +0.013 | 2026: -0.244
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.50
- Early IC=+0.1263, Recent IC=+0.0627, 1st-half IC=+0.1066, 2nd-half IC=+0.0763, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.072, Q3_mid=+0.043, Q4=+0.085, Q5_high_vol=+0.200

**`combo_tri_mean__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1436, Sharpe=-2.4584)
- Admission: Train IC=+0.2040, Deflated=+0.2039, IR=0.80, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.085 | 2017: +0.016 | 2018: +0.219 | 2019: +0.076 | 2020: -0.000 | 2021: +0.169 | 2022: +0.052 | 2023: +0.183 | 2024: +0.011 | 2025: +0.107 | 2026: -0.144
- Yearly Tail ICs:   2015: +0.144 | 2016: +0.019 | 2017: +0.034 | 2018: +0.371 | 2019: +0.179 | 2020: +0.004 | 2021: +0.408 | 2022: +0.305 | 2023: +0.451 | 2024: +0.062 | 2025: +0.148 | 2026: -0.049
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=0.84, Recency ratio=0.40
- Early IC=+0.1474, Recent IC=+0.0592, 1st-half IC=+0.1129, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.111, Q3_mid=+0.059, Q4=+0.099, Q5_high_vol=+0.175

**`combo_tri_median__bar_ret_0__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0883, Sharpe=-2.4409)
- Admission: Train IC=+0.2159, Deflated=+0.2160, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.111 | 2017: +0.014 | 2018: +0.189 | 2019: +0.097 | 2020: +0.005 | 2021: +0.146 | 2022: +0.045 | 2023: +0.155 | 2024: +0.036 | 2025: +0.063 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.049 | 2017: -0.098 | 2018: +0.232 | 2019: +0.183 | 2020: +0.063 | 2021: +0.342 | 2022: +0.263 | 2023: +0.306 | 2024: +0.186 | 2025: +0.135 | 2026: -0.301
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.34
- Early IC=+0.1430, Recent IC=+0.0491, 1st-half IC=+0.1117, 2nd-half IC=+0.0795, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.106, Q3_mid=+0.048, Q4=+0.098, Q5_high_vol=+0.167

**`combo_tri_median__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0881, Sharpe=-2.4409)
- Admission: Train IC=+0.2155, Deflated=+0.2156, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.111 | 2017: +0.013 | 2018: +0.189 | 2019: +0.097 | 2020: +0.005 | 2021: +0.146 | 2022: +0.045 | 2023: +0.155 | 2024: +0.036 | 2025: +0.063 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.049 | 2017: -0.098 | 2018: +0.232 | 2019: +0.183 | 2020: +0.061 | 2021: +0.340 | 2022: +0.263 | 2023: +0.302 | 2024: +0.187 | 2025: +0.135 | 2026: -0.301
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.34
- Early IC=+0.1430, Recent IC=+0.0493, 1st-half IC=+0.1116, 2nd-half IC=+0.0796, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.106, Q3_mid=+0.049, Q4=+0.098, Q5_high_vol=+0.167

**`combo_rank_max__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.1571, Sharpe=-2.4219)
- Admission: Train IC=+0.1808, Deflated=+0.1813, IR=0.69, Mono=0.75, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.026 | 2017: +0.003 | 2018: +0.134 | 2019: +0.115 | 2020: -0.021 | 2021: +0.130 | 2022: +0.048 | 2023: +0.198 | 2024: -0.025 | 2025: +0.092 | 2026: -0.152
- Yearly Tail ICs:   2015: -0.039 | 2016: -0.160 | 2017: +0.177 | 2018: +0.242 | 2019: +0.249 | 2020: +0.115 | 2021: +0.213 | 2022: +0.211 | 2023: +0.085 | 2024: +0.123 | 2025: +0.284 | 2026: -0.257
- IC CV=0.84, Neg years (linear/tail)=2/0 of 8, Half ratio=0.95, Recency ratio=0.34
- Early IC=+0.1235, Recent IC=+0.0414, 1st-half IC=+0.0902, 2nd-half IC=+0.0861, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.121, Q3_mid=+0.032, Q4=+0.086, Q5_high_vol=+0.069

**`morning_volume_weighted_momentum`** (Lock IC=-0.1752, Sharpe=-2.4148)
- Admission: Train IC=+0.1634, Deflated=+0.1619, IR=0.56, Mono=0.71, p=0.0014, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.047 | 2016: +0.001 | 2017: -0.097 | 2018: +0.060 | 2019: +0.016 | 2020: +0.033 | 2021: +0.153 | 2022: +0.045 | 2023: +0.123 | 2024: +0.053 | 2025: +0.088 | 2026: -0.175
- Yearly Tail ICs:   2015: -0.006 | 2016: +0.073 | 2017: +0.015 | 2018: +0.085 | 2019: +0.053 | 2020: +0.009 | 2021: +0.233 | 2022: +0.101 | 2023: +0.284 | 2024: +0.192 | 2025: +0.315 | 2026: -0.261
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.85
- Early IC=+0.0382, Recent IC=+0.0705, 1st-half IC=+0.0674, 2nd-half IC=+0.0852, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.040, Q3_mid=+0.052, Q4=+0.095, Q5_high_vol=+0.120

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1502, Sharpe=-2.3921)
- Admission: Train IC=+0.2207, Deflated=+0.2205, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.94
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

**`combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.1469, Sharpe=-2.3451)
- Admission: Train IC=+0.2092, Deflated=+0.2083, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.100 | 2017: +0.045 | 2018: +0.181 | 2019: +0.066 | 2020: +0.030 | 2021: +0.186 | 2022: +0.008 | 2023: +0.154 | 2024: +0.059 | 2025: +0.088 | 2026: -0.147
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.111 | 2017: +0.066 | 2018: +0.339 | 2019: +0.193 | 2020: +0.131 | 2021: +0.391 | 2022: +0.286 | 2023: +0.259 | 2024: +0.123 | 2025: +0.031 | 2026: -0.323
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.59
- Early IC=+0.1237, Recent IC=+0.0735, 1st-half IC=+0.1128, 2nd-half IC=+0.0804, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.085, Q3_mid=+0.046, Q4=+0.077, Q5_high_vol=+0.197

**`early_order_flow_imbalance`** (Lock IC=-0.2024, Sharpe=-2.3152)
- Admission: Train IC=+0.1502, Deflated=+0.1488, IR=0.49, Mono=0.66, p=0.0034, MaxCorr=0.89
- Yearly Linear ICs: 2015: -0.032 | 2016: +0.074 | 2017: -0.067 | 2018: +0.082 | 2019: +0.048 | 2020: -0.019 | 2021: +0.147 | 2022: +0.098 | 2023: +0.111 | 2024: -0.001 | 2025: +0.076 | 2026: -0.202
- Yearly Tail ICs:   2015: -0.115 | 2016: +0.147 | 2017: +0.009 | 2018: +0.142 | 2019: +0.189 | 2020: -0.092 | 2021: +0.406 | 2022: +0.190 | 2023: +0.100 | 2024: +0.087 | 2025: +0.113 | 2026: -0.121
- IC CV=0.78, Neg years (linear/tail)=2/1 of 8, Half ratio=1.30, Recency ratio=0.58
- Early IC=+0.0650, Recent IC=+0.0377, 1st-half IC=+0.0622, 2nd-half IC=+0.0811, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.089, Q3_mid=+0.096, Q4=+0.113, Q5_high_vol=+0.015

**`combo_max__first_bar_return__bar_body_rng_0`** (Lock IC=-0.0776, Sharpe=-2.3098)
- Admission: Train IC=+0.2212, Deflated=+0.2212, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.111 | 2017: +0.049 | 2018: +0.194 | 2019: +0.094 | 2020: +0.005 | 2021: +0.141 | 2022: +0.040 | 2023: +0.143 | 2024: +0.029 | 2025: +0.076 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.097 | 2016: +0.075 | 2017: +0.068 | 2018: +0.329 | 2019: +0.153 | 2020: +0.168 | 2021: +0.322 | 2022: +0.364 | 2023: +0.265 | 2024: +0.059 | 2025: +0.150 | 2026: -0.351
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.36
- Early IC=+0.1442, Recent IC=+0.0524, 1st-half IC=+0.1101, 2nd-half IC=+0.0762, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.099, Q3_mid=+0.045, Q4=+0.092, Q5_high_vol=+0.168

**`combo_ratio__volume_surge_direction__volume_weighted_price_position`** (Lock IC=-0.1192, Sharpe=-2.2557)
- Admission: Train IC=+0.1246, Deflated=+0.1255, IR=0.65, Mono=0.70, p=0.0114, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.026 | 2017: -0.042 | 2018: +0.171 | 2019: +0.146 | 2020: +0.020 | 2021: +0.075 | 2022: +0.043 | 2023: +0.154 | 2024: -0.009 | 2025: +0.081 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.196 | 2016: -0.135 | 2017: -0.002 | 2018: +0.160 | 2019: +0.165 | 2020: +0.169 | 2021: +0.191 | 2022: -0.027 | 2023: +0.159 | 2024: +0.165 | 2025: +0.220 | 2026: -0.269
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=0.71, Recency ratio=0.23
- Early IC=+0.1586, Recent IC=+0.0363, 1st-half IC=+0.0962, 2nd-half IC=+0.0687, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.077, Q3_mid=+0.021, Q4=+0.106, Q5_high_vol=+0.084

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0695, Sharpe=-2.2404)
- Admission: Train IC=+0.1875, Deflated=+0.1880, IR=0.58, Mono=0.72, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.085 | 2016: +0.085 | 2017: -0.019 | 2018: +0.156 | 2019: +0.094 | 2020: +0.038 | 2021: +0.162 | 2022: +0.047 | 2023: +0.139 | 2024: +0.034 | 2025: +0.031 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.158 | 2016: -0.082 | 2017: -0.016 | 2018: +0.278 | 2019: +0.253 | 2020: +0.102 | 2021: +0.406 | 2022: -0.003 | 2023: +0.266 | 2024: +0.168 | 2025: +0.028 | 2026: -0.278
- IC CV=0.61, Neg years (linear/tail)=0/1 of 8, Half ratio=0.64, Recency ratio=0.26
- Early IC=+0.1246, Recent IC=+0.0328, 1st-half IC=+0.1090, 2nd-half IC=+0.0694, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.092, Q3_mid=+0.045, Q4=+0.081, Q5_high_vol=+0.151

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=-0.1373, Sharpe=-2.2395)
- Admission: Train IC=+0.2049, Deflated=+0.2046, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.080 | 2017: +0.014 | 2018: +0.172 | 2019: +0.076 | 2020: +0.024 | 2021: +0.152 | 2022: +0.027 | 2023: +0.156 | 2024: +0.075 | 2025: +0.053 | 2026: -0.137
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.070 | 2017: -0.070 | 2018: +0.180 | 2019: +0.241 | 2020: +0.183 | 2021: +0.317 | 2022: +0.293 | 2023: +0.306 | 2024: +0.217 | 2025: +0.038 | 2026: -0.103
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.51
- Early IC=+0.1244, Recent IC=+0.0639, 1st-half IC=+0.1051, 2nd-half IC=+0.0790, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.070, Q3_mid=+0.046, Q4=+0.072, Q5_high_vol=+0.199

**`combo_mean__max_up_ret__bar_ret_0`** (Lock IC=-0.1373, Sharpe=-2.2395)
- Admission: Train IC=+0.2048, Deflated=+0.2045, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.080 | 2017: +0.014 | 2018: +0.173 | 2019: +0.076 | 2020: +0.024 | 2021: +0.152 | 2022: +0.027 | 2023: +0.156 | 2024: +0.075 | 2025: +0.053 | 2026: -0.137
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.070 | 2017: -0.070 | 2018: +0.180 | 2019: +0.241 | 2020: +0.183 | 2021: +0.317 | 2022: +0.293 | 2023: +0.305 | 2024: +0.217 | 2025: +0.038 | 2026: -0.103
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.51
- Early IC=+0.1245, Recent IC=+0.0638, 1st-half IC=+0.1052, 2nd-half IC=+0.0790, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.070, Q3_mid=+0.046, Q4=+0.072, Q5_high_vol=+0.199

**`combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0828, Sharpe=-2.2099)
- Admission: Train IC=+0.2001, Deflated=+0.2005, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.044 | 2016: +0.076 | 2017: -0.045 | 2018: +0.158 | 2019: +0.129 | 2020: +0.016 | 2021: +0.145 | 2022: +0.033 | 2023: +0.175 | 2024: +0.017 | 2025: +0.010 | 2026: -0.083
- Yearly Tail ICs:   2015: -0.049 | 2016: +0.132 | 2017: -0.140 | 2018: +0.339 | 2019: +0.247 | 2020: +0.104 | 2021: +0.389 | 2022: +0.172 | 2023: +0.263 | 2024: +0.124 | 2025: +0.090 | 2026: -0.040
- IC CV=0.79, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.09
- Early IC=+0.1433, Recent IC=+0.0132, 1st-half IC=+0.1065, 2nd-half IC=+0.0666, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.102, Q3_mid=+0.063, Q4=+0.073, Q5_high_vol=+0.136

**`opening_drive_thrust_ratio`** (Lock IC=-0.1510, Sharpe=-2.2099)
- Admission: Train IC=+0.1983, Deflated=+0.1985, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.039 | 2018: +0.176 | 2019: +0.078 | 2020: +0.042 | 2021: +0.170 | 2022: +0.024 | 2023: +0.166 | 2024: +0.033 | 2025: +0.069 | 2026: -0.151
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.178 | 2017: -0.121 | 2018: +0.326 | 2019: +0.224 | 2020: +0.117 | 2021: +0.389 | 2022: +0.169 | 2023: +0.259 | 2024: +0.120 | 2025: +0.073 | 2026: -0.040
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.1273, Recent IC=+0.0512, 1st-half IC=+0.1123, 2nd-half IC=+0.0854, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.008, Q2=+0.079, Q3_mid=+0.067, Q4=+0.089, Q5_high_vol=+0.213

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.1964, Sharpe=-2.1840)
- Admission: Train IC=+0.2038, Deflated=+0.2027, IR=0.91, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.77, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.66
- Early IC=+0.0887, Recent IC=+0.0589, 1st-half IC=+0.0862, 2nd-half IC=+0.0892, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.065, Q3_mid=+0.037, Q4=+0.066, Q5_high_vol=+0.175

**`combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=-0.1425, Sharpe=-2.1661)
- Admission: Train IC=+0.2261, Deflated=+0.2263, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.050 | 2017: -0.038 | 2018: +0.163 | 2019: +0.129 | 2020: +0.012 | 2021: +0.133 | 2022: +0.037 | 2023: +0.194 | 2024: +0.003 | 2025: +0.078 | 2026: -0.142
- Yearly Tail ICs:   2015: +0.102 | 2016: -0.130 | 2017: +0.011 | 2018: +0.275 | 2019: +0.170 | 2020: +0.112 | 2021: +0.223 | 2022: +0.168 | 2023: +0.258 | 2024: +0.168 | 2025: +0.254 | 2026: -0.117
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.33
- Early IC=+0.1460, Recent IC=+0.0483, 1st-half IC=+0.1068, 2nd-half IC=+0.0874, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.115, Q3_mid=+0.034, Q4=+0.101, Q5_high_vol=+0.154

**`combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0581, Sharpe=-2.1391)
- Admission: Train IC=+0.2165, Deflated=+0.2165, IR=0.62, Mono=0.69, p=0.0000, MaxCorr=0.99
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

**`combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1073, Sharpe=-1.9857)
- Admission: Train IC=+0.2235, Deflated=+0.2233, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.079 | 2017: +0.045 | 2018: +0.208 | 2019: +0.081 | 2020: -0.014 | 2021: +0.149 | 2022: +0.053 | 2023: +0.169 | 2024: +0.024 | 2025: +0.098 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.224 | 2016: -0.076 | 2017: +0.130 | 2018: +0.379 | 2019: +0.124 | 2020: +0.080 | 2021: +0.406 | 2022: +0.284 | 2023: +0.273 | 2024: +0.221 | 2025: +0.172 | 2026: -0.102
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=0.83, Recency ratio=0.42
- Early IC=+0.1443, Recent IC=+0.0611, 1st-half IC=+0.1062, 2nd-half IC=+0.0885, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.118, Q3_mid=+0.049, Q4=+0.093, Q5_high_vol=+0.155

**`combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1573, Sharpe=-1.9849)
- Admission: Train IC=+0.2265, Deflated=+0.2263, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.069 | 2017: +0.012 | 2018: +0.218 | 2019: +0.076 | 2020: +0.013 | 2021: +0.154 | 2022: +0.054 | 2023: +0.179 | 2024: +0.021 | 2025: +0.104 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.175 | 2016: -0.037 | 2017: +0.062 | 2018: +0.310 | 2019: +0.174 | 2020: +0.105 | 2021: +0.354 | 2022: +0.257 | 2023: +0.242 | 2024: +0.264 | 2025: +0.148 | 2026: -0.020
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.43
- Early IC=+0.1470, Recent IC=+0.0628, 1st-half IC=+0.1132, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.108, Q3_mid=+0.058, Q4=+0.094, Q5_high_vol=+0.183

**`combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.1708, Sharpe=-1.9174)
- Admission: Train IC=+0.1684, Deflated=+0.1681, IR=0.66, Mono=0.73, p=0.0010, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.070 | 2017: +0.038 | 2018: +0.173 | 2019: +0.062 | 2020: -0.009 | 2021: +0.184 | 2022: +0.055 | 2023: +0.189 | 2024: +0.024 | 2025: +0.112 | 2026: -0.171
- Yearly Tail ICs:   2015: +0.164 | 2016: -0.057 | 2017: +0.158 | 2018: +0.341 | 2019: +0.085 | 2020: -0.005 | 2021: +0.363 | 2022: +0.215 | 2023: +0.253 | 2024: +0.207 | 2025: +0.246 | 2026: -0.161
- IC CV=0.73, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=0.58
- Early IC=+0.1176, Recent IC=+0.0682, 1st-half IC=+0.0994, 2nd-half IC=+0.0994, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.102, Q3_mid=+0.053, Q4=+0.084, Q5_high_vol=+0.176

**`combo_tri_median__volume_weighted_momentum_acceleration__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1305, Sharpe=-1.8873)
- Admission: Train IC=+0.1933, Deflated=+0.1929, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.067 | 2016: +0.035 | 2017: -0.001 | 2018: +0.103 | 2019: +0.042 | 2020: -0.069 | 2021: +0.150 | 2022: +0.078 | 2023: +0.216 | 2024: +0.054 | 2025: +0.079 | 2026: -0.131
- Yearly Tail ICs:   2015: -0.042 | 2016: +0.046 | 2017: -0.060 | 2018: +0.340 | 2019: +0.166 | 2020: -0.020 | 2021: +0.382 | 2022: +0.315 | 2023: +0.474 | 2024: +0.045 | 2025: +0.207 | 2026: +0.025
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=2.17, Recency ratio=0.92
- Early IC=+0.0725, Recent IC=+0.0665, 1st-half IC=+0.0520, 2nd-half IC=+0.1127, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.066, Q3_mid=+0.027, Q4=+0.112, Q5_high_vol=+0.073

**`combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1298, Sharpe=-1.8873)
- Admission: Train IC=+0.1817, Deflated=+0.1814, IR=0.67, Mono=0.73, p=0.0004, MaxCorr=0.99
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

**`combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_ret_0`** (Lock IC=-0.1339, Sharpe=-1.7857)
- Admission: Train IC=+0.1724, Deflated=+0.1722, IR=0.40, Mono=0.66, p=0.0010, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.082 | 2016: +0.082 | 2017: -0.022 | 2018: +0.074 | 2019: +0.052 | 2020: +0.025 | 2021: +0.156 | 2022: +0.007 | 2023: +0.187 | 2024: +0.013 | 2025: -0.006 | 2026: -0.134
- Yearly Tail ICs:   2015: +0.112 | 2016: -0.024 | 2017: -0.113 | 2018: +0.088 | 2019: +0.182 | 2020: +0.135 | 2021: +0.344 | 2022: +0.206 | 2023: +0.295 | 2024: +0.055 | 2025: +0.039 | 2026: -0.230
- IC CV=1.06, Neg years (linear/tail)=1/0 of 8, Half ratio=0.73, Recency ratio=0.05
- Early IC=+0.0630, Recent IC=+0.0034, 1st-half IC=+0.0736, 2nd-half IC=+0.0535, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.73, neg years=0)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.028, Q3_mid=+0.041, Q4=+0.056, Q5_high_vol=+0.117

**`combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.1153, Sharpe=-1.6739)
- Admission: Train IC=+0.1910, Deflated=+0.1908, IR=0.74, Mono=0.73, p=0.0002, MaxCorr=0.94
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
- Admission: Train IC=+0.2104, Deflated=+0.2107, IR=0.73, Mono=0.73, p=0.0000, MaxCorr=0.97
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
- Admission: Train IC=+0.1429, Deflated=+0.1430, IR=0.51, Mono=0.70, p=0.0054, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.090 | 2017: +0.042 | 2018: +0.161 | 2019: +0.087 | 2020: +0.032 | 2021: +0.136 | 2022: +0.029 | 2023: +0.126 | 2024: +0.010 | 2025: +0.057 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.150 | 2016: -0.197 | 2017: +0.009 | 2018: +0.173 | 2019: +0.117 | 2020: +0.277 | 2021: +0.328 | 2022: +0.244 | 2023: +0.287 | 2024: +0.085 | 2025: +0.161 | 2026: -0.108
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.27
- Early IC=+0.1240, Recent IC=+0.0333, 1st-half IC=+0.1020, 2nd-half IC=+0.0568, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.077, Q3_mid=+0.045, Q4=+0.068, Q5_high_vol=+0.158

**`combo_sig_product__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0908, Sharpe=-1.5036)
- Admission: Train IC=+0.1781, Deflated=+0.1776, IR=0.69, Mono=0.77, p=0.0008, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.083 | 2017: +0.010 | 2018: +0.202 | 2019: +0.114 | 2020: -0.021 | 2021: +0.142 | 2022: +0.035 | 2023: +0.127 | 2024: +0.000 | 2025: +0.023 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.021 | 2017: +0.167 | 2018: +0.256 | 2019: +0.180 | 2020: -0.034 | 2021: +0.382 | 2022: +0.328 | 2023: +0.203 | 2024: +0.059 | 2025: +0.205 | 2026: -0.163
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=0.51, Recency ratio=0.07
- Early IC=+0.1580, Recent IC=+0.0118, 1st-half IC=+0.1032, 2nd-half IC=+0.0527, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.056, Q3_mid=+0.023, Q4=+0.116, Q5_high_vol=+0.117

**`volume_weighted_price_position`** (Lock IC=-0.1599, Sharpe=-1.5036)
- Admission: Train IC=+0.1779, Deflated=+0.1774, IR=0.67, Mono=0.77, p=0.0008, MaxCorr=0.86
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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=-0.0541, Sharpe=-1.4245)
- Admission: Train IC=+0.2099, Deflated=+0.2098, IR=0.63, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.105 | 2017: -0.027 | 2018: +0.204 | 2019: +0.092 | 2020: +0.058 | 2021: +0.156 | 2022: +0.073 | 2023: +0.128 | 2024: +0.029 | 2025: +0.071 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.272 | 2016: +0.108 | 2017: -0.002 | 2018: +0.290 | 2019: +0.198 | 2020: +0.192 | 2021: +0.378 | 2022: +0.258 | 2023: +0.231 | 2024: +0.118 | 2025: +0.075 | 2026: +0.046
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.34
- Early IC=+0.1479, Recent IC=+0.0501, 1st-half IC=+0.1262, 2nd-half IC=+0.0779, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.065, Q3_mid=+0.053, Q4=+0.073, Q5_high_vol=+0.237

**`combo_tri_mean__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.1740, Sharpe=-1.4177)
- Admission: Train IC=+0.2218, Deflated=+0.2214, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.069 | 2017: -0.012 | 2018: +0.183 | 2019: +0.067 | 2020: +0.023 | 2021: +0.179 | 2022: +0.039 | 2023: +0.184 | 2024: +0.033 | 2025: +0.095 | 2026: -0.174
- Yearly Tail ICs:   2015: -0.008 | 2016: +0.199 | 2017: +0.142 | 2018: +0.356 | 2019: +0.239 | 2020: +0.053 | 2021: +0.390 | 2022: +0.323 | 2023: +0.308 | 2024: +0.097 | 2025: +0.074 | 2026: +0.003
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.51
- Early IC=+0.1249, Recent IC=+0.0636, 1st-half IC=+0.1086, 2nd-half IC=+0.0921, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.087, Q3_mid=+0.053, Q4=+0.089, Q5_high_vol=+0.195

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0199, Sharpe=-1.3557)
- Admission: Train IC=+0.1628, Deflated=+0.1625, IR=0.54, Mono=0.69, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.071 | 2016: +0.107 | 2017: -0.051 | 2018: +0.120 | 2019: +0.016 | 2020: +0.062 | 2021: +0.154 | 2022: +0.089 | 2023: +0.109 | 2024: +0.024 | 2025: +0.052 | 2026: -0.020
- Yearly Tail ICs:   2015: -0.135 | 2016: +0.131 | 2017: +0.039 | 2018: +0.374 | 2019: +0.106 | 2020: -0.003 | 2021: +0.304 | 2022: +0.282 | 2023: +0.180 | 2024: +0.108 | 2025: +0.128 | 2026: -0.110
- IC CV=0.58, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.56
- Early IC=+0.0677, Recent IC=+0.0378, 1st-half IC=+0.0873, 2nd-half IC=+0.0753, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.042, Q3_mid=+0.006, Q4=+0.070, Q5_high_vol=+0.212

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=-0.1611, Sharpe=-1.2733)
- Admission: Train IC=+0.2301, Deflated=+0.2290, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.087 | 2017: +0.035 | 2018: +0.169 | 2019: +0.060 | 2020: +0.041 | 2021: +0.170 | 2022: +0.015 | 2023: +0.166 | 2024: +0.060 | 2025: +0.078 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.033 | 2017: +0.026 | 2018: +0.412 | 2019: +0.206 | 2020: +0.193 | 2021: +0.360 | 2022: +0.306 | 2023: +0.290 | 2024: +0.141 | 2025: +0.095 | 2026: -0.308
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.60
- Early IC=+0.1152, Recent IC=+0.0689, 1st-half IC=+0.1068, 2nd-half IC=+0.0797, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.078, Q3_mid=+0.047, Q4=+0.080, Q5_high_vol=+0.189

**`combo_sig_product__bar_body_rng_0__volume_surge_direction`** (Lock IC=-0.0580, Sharpe=-1.2501)
- Admission: Train IC=+0.1495, Deflated=+0.1502, IR=0.54, Mono=0.66, p=0.0034, MaxCorr=0.91
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
- Admission: Train IC=+0.2345, Deflated=+0.2349, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.87
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

**`combo_rank_min__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.0433, Sharpe=-1.1960)
- Admission: Train IC=+0.1724, Deflated=+0.1722, IR=0.66, Mono=0.78, p=0.0010, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.050 | 2017: -0.022 | 2018: +0.255 | 2019: +0.069 | 2020: -0.004 | 2021: +0.106 | 2022: +0.085 | 2023: +0.167 | 2024: -0.019 | 2025: +0.130 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.410 | 2016: -0.276 | 2017: +0.043 | 2018: +0.231 | 2019: +0.112 | 2020: +0.094 | 2021: +0.362 | 2022: +0.177 | 2023: +0.337 | 2024: +0.096 | 2025: +0.331 | 2026: -0.158
- IC CV=0.87, Neg years (linear/tail)=2/0 of 8, Half ratio=0.94, Recency ratio=0.33
- Early IC=+0.1666, Recent IC=+0.0547, 1st-half IC=+0.0978, 2nd-half IC=+0.0916, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.120, Q3_mid=+0.024, Q4=+0.129, Q5_high_vol=+0.119

**`combo_max__bar_ret_0__volume_surge_direction`** (Lock IC=-0.0832, Sharpe=-1.1822)
- Admission: Train IC=+0.2473, Deflated=+0.2480, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.87
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

**`combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0942, Sharpe=-1.1726)
- Admission: Train IC=+0.2298, Deflated=+0.2301, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.098 | 2017: -0.003 | 2018: +0.221 | 2019: +0.077 | 2020: +0.007 | 2021: +0.166 | 2022: +0.036 | 2023: +0.152 | 2024: +0.039 | 2025: +0.071 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.034 | 2016: +0.182 | 2017: -0.104 | 2018: +0.330 | 2019: +0.176 | 2020: +0.076 | 2021: +0.474 | 2022: +0.096 | 2023: +0.285 | 2024: +0.027 | 2025: +0.121 | 2026: -0.130
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.37
- Early IC=+0.1495, Recent IC=+0.0546, 1st-half IC=+0.1194, 2nd-half IC=+0.0831, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.091, Q3_mid=+0.069, Q4=+0.090, Q5_high_vol=+0.208

**`combo_min__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0924, Sharpe=-1.1726)
- Admission: Train IC=+0.2257, Deflated=+0.2261, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.078 | 2016: +0.097 | 2017: -0.003 | 2018: +0.220 | 2019: +0.081 | 2020: +0.007 | 2021: +0.167 | 2022: +0.037 | 2023: +0.147 | 2024: +0.040 | 2025: +0.070 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.025 | 2016: +0.162 | 2017: -0.113 | 2018: +0.302 | 2019: +0.258 | 2020: +0.094 | 2021: +0.487 | 2022: +0.106 | 2023: +0.198 | 2024: +0.054 | 2025: +0.113 | 2026: -0.070
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.36
- Early IC=+0.1505, Recent IC=+0.0548, 1st-half IC=+0.1191, 2nd-half IC=+0.0823, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.089, Q3_mid=+0.068, Q4=+0.089, Q5_high_vol=+0.207

**`combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.0631, Sharpe=-1.1652)
- Admission: Train IC=+0.2142, Deflated=+0.2141, IR=0.66, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.065 | 2017: +0.033 | 2018: +0.209 | 2019: +0.075 | 2020: -0.029 | 2021: +0.132 | 2022: +0.061 | 2023: +0.171 | 2024: +0.026 | 2025: +0.092 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.197 | 2016: -0.103 | 2017: +0.117 | 2018: +0.137 | 2019: +0.185 | 2020: +0.008 | 2021: +0.349 | 2022: +0.394 | 2023: +0.315 | 2024: +0.158 | 2025: +0.068 | 2026: -0.177
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=0.91, Recency ratio=0.42
- Early IC=+0.1417, Recent IC=+0.0591, 1st-half IC=+0.0993, 2nd-half IC=+0.0904, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.145, Q3_mid=+0.036, Q4=+0.098, Q5_high_vol=+0.137

**`combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0127, Sharpe=-1.1004)
- Admission: Train IC=+0.1854, Deflated=+0.1849, IR=0.56, Mono=0.70, p=0.0004, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.121 | 2017: -0.027 | 2018: +0.165 | 2019: +0.003 | 2020: +0.067 | 2021: +0.160 | 2022: +0.085 | 2023: +0.125 | 2024: +0.017 | 2025: +0.050 | 2026: -0.013
- Yearly Tail ICs:   2015: -0.093 | 2016: +0.075 | 2017: -0.134 | 2018: +0.359 | 2019: +0.077 | 2020: +0.091 | 2021: +0.281 | 2022: +0.314 | 2023: +0.220 | 2024: +0.147 | 2025: +0.098 | 2026: -0.043
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.0840, Recent IC=+0.0338, 1st-half IC=+0.0974, 2nd-half IC=+0.0738, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.063, Q3_mid=+0.008, Q4=+0.073, Q5_high_vol=+0.220

**`combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0127, Sharpe=-1.1004)
- Admission: Train IC=+0.1853, Deflated=+0.1848, IR=0.56, Mono=0.70, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.121 | 2017: -0.026 | 2018: +0.165 | 2019: +0.003 | 2020: +0.067 | 2021: +0.160 | 2022: +0.085 | 2023: +0.125 | 2024: +0.018 | 2025: +0.050 | 2026: -0.013
- Yearly Tail ICs:   2015: -0.093 | 2016: +0.075 | 2017: -0.134 | 2018: +0.359 | 2019: +0.077 | 2020: +0.091 | 2021: +0.281 | 2022: +0.314 | 2023: +0.220 | 2024: +0.147 | 2025: +0.098 | 2026: -0.043
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.40
- Early IC=+0.0839, Recent IC=+0.0338, 1st-half IC=+0.0973, 2nd-half IC=+0.0738, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.032, Q2=+0.063, Q3_mid=+0.008, Q4=+0.073, Q5_high_vol=+0.220

**`combo_rank_max__max_up_ret__volume_surge_direction`** (Lock IC=-0.1503, Sharpe=-1.0912)
- Admission: Train IC=+0.2219, Deflated=+0.2217, IR=0.78, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.060 | 2017: -0.046 | 2018: +0.147 | 2019: +0.111 | 2020: -0.002 | 2021: +0.109 | 2022: +0.031 | 2023: +0.150 | 2024: +0.023 | 2025: +0.073 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.060 | 2017: +0.088 | 2018: +0.317 | 2019: +0.297 | 2020: +0.141 | 2021: +0.117 | 2022: +0.289 | 2023: +0.112 | 2024: +0.255 | 2025: +0.268 | 2026: -0.080
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.42
- Early IC=+0.1283, Recent IC=+0.0537, 1st-half IC=+0.0889, 2nd-half IC=+0.0811, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=0.70, neg years=1)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.064, Q3_mid=+0.020, Q4=+0.090, Q5_high_vol=+0.140

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0842, Sharpe=-1.0673)
- Admission: Train IC=+0.2009, Deflated=+0.2009, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.107 | 2017: -0.057 | 2018: +0.207 | 2019: +0.079 | 2020: +0.072 | 2021: +0.171 | 2022: +0.067 | 2023: +0.123 | 2024: +0.031 | 2025: +0.068 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.034 | 2016: +0.127 | 2017: +0.085 | 2018: +0.402 | 2019: +0.287 | 2020: +0.039 | 2021: +0.364 | 2022: +0.233 | 2023: +0.108 | 2024: +0.205 | 2025: +0.075 | 2026: +0.036
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.35
- Early IC=+0.1433, Recent IC=+0.0498, 1st-half IC=+0.1284, 2nd-half IC=+0.0789, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.060, Q3_mid=+0.050, Q4=+0.084, Q5_high_vol=+0.255

**`combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0691, Sharpe=-0.9513)
- Admission: Train IC=+0.2251, Deflated=+0.2262, IR=0.74, Mono=0.79, p=0.0000, MaxCorr=0.87
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
- Admission: Train IC=+0.2509, Deflated=+0.2514, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.061 | 2016: +0.028 | 2017: -0.004 | 2018: +0.186 | 2019: +0.080 | 2020: +0.036 | 2021: +0.155 | 2022: +0.029 | 2023: +0.169 | 2024: +0.018 | 2025: +0.076 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.224 | 2016: -0.183 | 2017: +0.022 | 2018: +0.174 | 2019: +0.013 | 2020: +0.237 | 2021: +0.443 | 2022: -0.037 | 2023: +0.432 | 2024: +0.290 | 2025: +0.363 | 2026: -0.203
- IC CV=0.67, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.35
- Early IC=+0.1333, Recent IC=+0.0467, 1st-half IC=+0.1174, 2nd-half IC=+0.0772, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.107, Q3_mid=+0.051, Q4=+0.090, Q5_high_vol=+0.149

**`combo_rank_min__bar_body_rng_0__volume_surge_direction`** (Lock IC=-0.0374, Sharpe=-0.7738)
- Admission: Train IC=+0.2608, Deflated=+0.2613, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.043 | 2016: +0.032 | 2017: +0.011 | 2018: +0.199 | 2019: +0.076 | 2020: +0.037 | 2021: +0.167 | 2022: +0.020 | 2023: +0.160 | 2024: +0.012 | 2025: +0.104 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.287 | 2016: -0.197 | 2017: +0.013 | 2018: +0.286 | 2019: +0.097 | 2020: +0.301 | 2021: +0.473 | 2022: +0.005 | 2023: +0.425 | 2024: +0.192 | 2025: +0.379 | 2026: -0.154
- IC CV=0.69, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.32
- Early IC=+0.1392, Recent IC=+0.0444, 1st-half IC=+0.1179, 2nd-half IC=+0.0744, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.105, Q3_mid=+0.044, Q4=+0.101, Q5_high_vol=+0.134

**`combo_tri_median__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0539, Sharpe=-0.7695)
- Admission: Train IC=+0.2081, Deflated=+0.2078, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.112 | 2017: -0.021 | 2018: +0.217 | 2019: +0.134 | 2020: +0.026 | 2021: +0.129 | 2022: +0.058 | 2023: +0.168 | 2024: +0.053 | 2025: +0.062 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.084 | 2017: +0.031 | 2018: +0.262 | 2019: +0.267 | 2020: +0.275 | 2021: +0.220 | 2022: +0.175 | 2023: +0.217 | 2024: +0.282 | 2025: +0.137 | 2026: +0.003
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.33
- Early IC=+0.1754, Recent IC=+0.0575, 1st-half IC=+0.1263, 2nd-half IC=+0.0924, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.103, Q3_mid=+0.062, Q4=+0.068, Q5_high_vol=+0.245

**`combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0539, Sharpe=-0.7695)
- Admission: Train IC=+0.2078, Deflated=+0.2076, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.112 | 2017: -0.021 | 2018: +0.217 | 2019: +0.134 | 2020: +0.026 | 2021: +0.129 | 2022: +0.058 | 2023: +0.168 | 2024: +0.053 | 2025: +0.062 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.084 | 2017: +0.031 | 2018: +0.262 | 2019: +0.268 | 2020: +0.275 | 2021: +0.220 | 2022: +0.175 | 2023: +0.217 | 2024: +0.285 | 2025: +0.137 | 2026: +0.003
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.33
- Early IC=+0.1754, Recent IC=+0.0573, 1st-half IC=+0.1263, 2nd-half IC=+0.0924, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.103, Q3_mid=+0.062, Q4=+0.068, Q5_high_vol=+0.245

**`combo_max__first_bar_return__first_bar_sentiment`** (Lock IC=-0.0930, Sharpe=-0.7198)
- Admission: Train IC=+0.1903, Deflated=+0.1903, IR=0.62, Mono=0.75, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.078 | 2017: +0.023 | 2018: +0.190 | 2019: +0.109 | 2020: +0.021 | 2021: +0.110 | 2022: +0.037 | 2023: +0.157 | 2024: -0.009 | 2025: +0.078 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.049 | 2017: +0.026 | 2018: +0.341 | 2019: +0.202 | 2020: +0.240 | 2021: +0.136 | 2022: +0.196 | 2023: +0.286 | 2024: +0.144 | 2025: +0.184 | 2026: -0.243
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=0.57, Recency ratio=0.23
- Early IC=+0.1495, Recent IC=+0.0346, 1st-half IC=+0.1111, 2nd-half IC=+0.0630, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.041, Q2=+0.109, Q3_mid=+0.049, Q4=+0.084, Q5_high_vol=+0.143

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=-0.0294, Sharpe=-0.6275)
- Admission: Train IC=+0.2621, Deflated=+0.2635, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.044 | 2017: -0.018 | 2018: +0.176 | 2019: +0.149 | 2020: +0.038 | 2021: +0.123 | 2022: +0.049 | 2023: +0.166 | 2024: +0.037 | 2025: +0.098 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.429 | 2016: -0.084 | 2017: +0.010 | 2018: +0.251 | 2019: +0.289 | 2020: +0.236 | 2021: +0.375 | 2022: +0.320 | 2023: +0.138 | 2024: +0.270 | 2025: +0.110 | 2026: +0.204
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.41
- Early IC=+0.1624, Recent IC=+0.0674, 1st-half IC=+0.1215, 2nd-half IC=+0.0885, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.064, Q2=+0.101, Q3_mid=+0.074, Q4=+0.092, Q5_high_vol=+0.189

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0294, Sharpe=-0.6275)
- Admission: Train IC=+0.2621, Deflated=+0.2635, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=1.00
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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=-0.0076, Sharpe=-0.5921)
- Admission: Train IC=+0.2591, Deflated=+0.2591, IR=0.80, Mono=0.81, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.108 | 2017: +0.021 | 2018: +0.215 | 2019: +0.106 | 2020: +0.039 | 2021: +0.142 | 2022: +0.071 | 2023: +0.132 | 2024: +0.015 | 2025: +0.083 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.243 | 2016: +0.052 | 2017: -0.006 | 2018: +0.302 | 2019: +0.179 | 2020: +0.235 | 2021: +0.437 | 2022: +0.310 | 2023: +0.240 | 2024: +0.097 | 2025: +0.161 | 2026: +0.049
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.30
- Early IC=+0.1609, Recent IC=+0.0490, 1st-half IC=+0.1268, 2nd-half IC=+0.0788, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.084, Q3_mid=+0.049, Q4=+0.097, Q5_high_vol=+0.208

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0712, Sharpe=-0.5845)
- Admission: Train IC=+0.2454, Deflated=+0.2463, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.054 | 2017: -0.048 | 2018: +0.208 | 2019: +0.130 | 2020: +0.058 | 2021: +0.154 | 2022: +0.046 | 2023: +0.131 | 2024: +0.030 | 2025: +0.082 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.380 | 2016: -0.045 | 2017: -0.018 | 2018: +0.279 | 2019: +0.291 | 2020: +0.218 | 2021: +0.418 | 2022: +0.321 | 2023: +0.104 | 2024: +0.253 | 2025: +0.050 | 2026: +0.239
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.33
- Early IC=+0.1690, Recent IC=+0.0564, 1st-half IC=+0.1366, 2nd-half IC=+0.0803, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.070, Q3_mid=+0.091, Q4=+0.105, Q5_high_vol=+0.214

**`combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0955, Sharpe=-0.5706)
- Admission: Train IC=+0.2233, Deflated=+0.2238, IR=0.72, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.099 | 2017: -0.005 | 2018: +0.210 | 2019: +0.081 | 2020: +0.002 | 2021: +0.127 | 2022: +0.062 | 2023: +0.164 | 2024: +0.030 | 2025: +0.085 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.064 | 2016: -0.115 | 2017: +0.137 | 2018: +0.160 | 2019: +0.210 | 2020: +0.103 | 2021: +0.327 | 2022: +0.362 | 2023: +0.365 | 2024: +0.190 | 2025: +0.034 | 2026: -0.118
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.39
- Early IC=+0.1454, Recent IC=+0.0572, 1st-half IC=+0.1051, 2nd-half IC=+0.0869, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.130, Q3_mid=+0.043, Q4=+0.095, Q5_high_vol=+0.154

**`combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0955, Sharpe=-0.5706)
- Admission: Train IC=+0.2233, Deflated=+0.2238, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.099 | 2017: -0.006 | 2018: +0.210 | 2019: +0.081 | 2020: +0.002 | 2021: +0.127 | 2022: +0.062 | 2023: +0.164 | 2024: +0.030 | 2025: +0.084 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.064 | 2016: -0.115 | 2017: +0.133 | 2018: +0.160 | 2019: +0.213 | 2020: +0.100 | 2021: +0.327 | 2022: +0.362 | 2023: +0.368 | 2024: +0.190 | 2025: +0.034 | 2026: -0.118
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.39
- Early IC=+0.1455, Recent IC=+0.0571, 1st-half IC=+0.1051, 2nd-half IC=+0.0869, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.03, neg years=2)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.130, Q3_mid=+0.043, Q4=+0.095, Q5_high_vol=+0.154

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=-0.0717, Sharpe=-0.5279)
- Admission: Train IC=+0.1653, Deflated=+0.1649, IR=0.52, Mono=0.68, p=0.0010, MaxCorr=0.86
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

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0627, Sharpe=-0.4458)
- Admission: Train IC=+0.2379, Deflated=+0.2380, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.106 | 2017: -0.040 | 2018: +0.233 | 2019: +0.093 | 2020: +0.064 | 2021: +0.155 | 2022: +0.077 | 2023: +0.144 | 2024: +0.030 | 2025: +0.082 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.097 | 2017: -0.028 | 2018: +0.384 | 2019: +0.257 | 2020: +0.260 | 2021: +0.344 | 2022: +0.265 | 2023: +0.203 | 2024: +0.136 | 2025: +0.192 | 2026: +0.078
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.34
- Early IC=+0.1629, Recent IC=+0.0556, 1st-half IC=+0.1359, 2nd-half IC=+0.0895, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.68, neg years=0)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.081, Q3_mid=+0.066, Q4=+0.099, Q5_high_vol=+0.247

**`combo_rank_min__first_bar_return__first_bar_sentiment`** (Lock IC=-0.0638, Sharpe=-0.4085)
- Admission: Train IC=+0.1000, Deflated=+0.0998, IR=0.57, Mono=0.71, p=0.0440, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.078 | 2016: +0.115 | 2017: +0.042 | 2018: +0.176 | 2019: +0.069 | 2020: +0.027 | 2021: +0.125 | 2022: +0.039 | 2023: +0.127 | 2024: +0.016 | 2025: +0.053 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.133 | 2017: +0.002 | 2018: +0.279 | 2019: +0.063 | 2020: +0.145 | 2021: +0.121 | 2022: +0.337 | 2023: +0.272 | 2024: +0.142 | 2025: +0.188 | 2026: -0.104
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.28
- Early IC=+0.1227, Recent IC=+0.0347, 1st-half IC=+0.0982, 2nd-half IC=+0.0594, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.082, Q3_mid=+0.038, Q4=+0.077, Q5_high_vol=+0.140

**`combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=-0.0297, Sharpe=-0.2989)
- Admission: Train IC=+0.2135, Deflated=+0.2135, IR=0.62, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.106 | 2017: -0.070 | 2018: +0.209 | 2019: +0.090 | 2020: +0.068 | 2021: +0.151 | 2022: +0.081 | 2023: +0.111 | 2024: +0.028 | 2025: +0.058 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.200 | 2017: -0.050 | 2018: +0.446 | 2019: +0.316 | 2020: +0.053 | 2021: +0.345 | 2022: +0.240 | 2023: +0.054 | 2024: +0.207 | 2025: +0.098 | 2026: +0.130
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.29
- Early IC=+0.1496, Recent IC=+0.0428, 1st-half IC=+0.1279, 2nd-half IC=+0.0791, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.018, Q2=+0.065, Q3_mid=+0.047, Q4=+0.088, Q5_high_vol=+0.259

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0466, Sharpe=-0.2373)
- Admission: Train IC=+0.2207, Deflated=+0.2208, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.116 | 2017: -0.020 | 2018: +0.233 | 2019: +0.099 | 2020: +0.054 | 2021: +0.164 | 2022: +0.065 | 2023: +0.130 | 2024: +0.028 | 2025: +0.075 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.181 | 2016: +0.119 | 2017: -0.026 | 2018: +0.361 | 2019: +0.282 | 2020: +0.122 | 2021: +0.394 | 2022: +0.234 | 2023: +0.107 | 2024: +0.195 | 2025: +0.200 | 2026: +0.079
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.31
- Early IC=+0.1662, Recent IC=+0.0515, 1st-half IC=+0.1370, 2nd-half IC=+0.0851, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.086, Q3_mid=+0.051, Q4=+0.094, Q5_high_vol=+0.247

**`combo_mean__bar_body_rng_0__volume_surge_direction`** (Lock IC=-0.0571, Sharpe=-0.1557)
- Admission: Train IC=+0.2585, Deflated=+0.2590, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.103 | 2016: +0.077 | 2017: +0.034 | 2018: +0.202 | 2019: +0.115 | 2020: +0.009 | 2021: +0.117 | 2022: +0.037 | 2023: +0.168 | 2024: +0.035 | 2025: +0.108 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.216 | 2016: -0.189 | 2017: -0.022 | 2018: +0.241 | 2019: +0.161 | 2020: +0.241 | 2021: +0.162 | 2022: +0.244 | 2023: +0.318 | 2024: +0.330 | 2025: +0.386 | 2026: -0.214
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.45
- Early IC=+0.1586, Recent IC=+0.0713, 1st-half IC=+0.1092, 2nd-half IC=+0.0890, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.107, Q3_mid=+0.038, Q4=+0.100, Q5_high_vol=+0.155

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=-0.0308, Sharpe=-0.1479)
- Admission: Train IC=+0.2192, Deflated=+0.2193, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.110 | 2017: -0.022 | 2018: +0.226 | 2019: +0.105 | 2020: +0.052 | 2021: +0.162 | 2022: +0.066 | 2023: +0.125 | 2024: +0.029 | 2025: +0.073 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.146 | 2017: -0.090 | 2018: +0.391 | 2019: +0.279 | 2020: +0.113 | 2021: +0.379 | 2022: +0.198 | 2023: +0.155 | 2024: +0.152 | 2025: +0.237 | 2026: +0.104
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.31
- Early IC=+0.1654, Recent IC=+0.0513, 1st-half IC=+0.1346, 2nd-half IC=+0.0838, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73, neg years=1)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.084, Q3_mid=+0.049, Q4=+0.096, Q5_high_vol=+0.243

**`combo_mean__first_bar_return__first_bar_sentiment`** (Lock IC=-0.0827, Sharpe=+0.0937)
- Admission: Train IC=+0.1961, Deflated=+0.1962, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.095 | 2017: +0.061 | 2018: +0.191 | 2019: +0.095 | 2020: +0.014 | 2021: +0.121 | 2022: +0.040 | 2023: +0.142 | 2024: +0.029 | 2025: +0.055 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.198 | 2016: -0.089 | 2017: +0.049 | 2018: +0.237 | 2019: +0.141 | 2020: +0.237 | 2021: +0.277 | 2022: +0.340 | 2023: +0.278 | 2024: +0.201 | 2025: +0.144 | 2026: -0.129
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.30
- Early IC=+0.1432, Recent IC=+0.0424, 1st-half IC=+0.1070, 2nd-half IC=+0.0663, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.89, neg years=2)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.096, Q3_mid=+0.042, Q4=+0.084, Q5_high_vol=+0.159

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0169, Sharpe=+0.1548)
- Admission: Train IC=+0.2339, Deflated=+0.2337, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.86
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
- Admission: Train IC=+0.1943, Deflated=+0.1946, IR=0.52, Mono=0.68, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.096 | 2017: -0.072 | 2018: +0.144 | 2019: +0.091 | 2020: +0.062 | 2021: +0.138 | 2022: +0.048 | 2023: +0.132 | 2024: +0.044 | 2025: +0.060 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.312 | 2016: -0.044 | 2017: -0.042 | 2018: +0.223 | 2019: +0.226 | 2020: +0.119 | 2021: +0.429 | 2022: +0.245 | 2023: +0.115 | 2024: +0.334 | 2025: +0.057 | 2026: +0.045
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.44
- Early IC=+0.1173, Recent IC=+0.0519, 1st-half IC=+0.1061, 2nd-half IC=+0.0746, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.031, Q2=+0.067, Q3_mid=+0.070, Q4=+0.036, Q5_high_vol=+0.221

**`combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=-0.0121, Sharpe=+0.8779)
- Admission: Train IC=+0.1844, Deflated=+0.1844, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.057 | 2017: -0.081 | 2018: +0.173 | 2019: +0.115 | 2020: +0.042 | 2021: +0.142 | 2022: +0.020 | 2023: +0.105 | 2024: +0.038 | 2025: +0.060 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.089 | 2017: -0.220 | 2018: +0.375 | 2019: +0.374 | 2020: +0.100 | 2021: +0.234 | 2022: +0.149 | 2023: +0.049 | 2024: +0.309 | 2025: +0.003 | 2026: +0.337
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.34
- Early IC=+0.1438, Recent IC=+0.0494, 1st-half IC=+0.1180, 2nd-half IC=+0.0704, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=0.90, neg years=2)
- Regime ICs: Q1_low_vol=-0.014, Q2=+0.075, Q3_mid=+0.072, Q4=+0.092, Q5_high_vol=+0.212

**`combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=-0.0121, Sharpe=+0.8779)
- Admission: Train IC=+0.1844, Deflated=+0.1844, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=1.00
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
- Admission: Train IC=+0.1635, Deflated=+0.1628, IR=0.55, Mono=0.72, p=0.0006, MaxCorr=0.95
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
- Admission: Train IC=+0.1315, Deflated=+0.1314, IR=0.48, Mono=0.70, p=0.0086, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.150 | 2017: +0.182 | 2018: +0.240 | 2019: +0.135 | 2020: +0.137 | 2021: +0.083 | 2022: +0.102 | 2023: +0.072 | 2024: +0.083 | 2025: +0.097 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.302 | 2017: +0.378 | 2018: +0.505 | 2019: +0.129 | 2020: +0.123 | 2021: +0.004 | 2022: +0.124 | 2023: +0.117 | 2024: +0.064 | 2025: -0.049 | 2026: -0.277
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.48
- Early IC=+0.1874, Recent IC=+0.0902, 1st-half IC=+0.1480, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.003, Q3_mid=+0.098, Q4=+0.131, Q5_high_vol=+0.206

**`combo_sig_product__high_low_sequence_momentum__first_bar_return`** (Lock IC=-0.1226, Sharpe=-2.8810)
- Admission: Train IC=+0.1870, Deflated=+0.1851, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.003 | 2017: +0.149 | 2018: +0.179 | 2019: +0.078 | 2020: +0.065 | 2021: +0.080 | 2022: +0.090 | 2023: +0.069 | 2024: +0.140 | 2025: +0.126 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.227 | 2016: -0.060 | 2017: +0.180 | 2018: +0.332 | 2019: +0.150 | 2020: +0.187 | 2021: +0.193 | 2022: +0.180 | 2023: +0.052 | 2024: +0.193 | 2025: +0.290 | 2026: -0.386
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.15, Recency ratio=1.03
- Early IC=+0.1287, Recent IC=+0.1327, 1st-half IC=+0.0998, 2nd-half IC=+0.1144, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.078, Q3_mid=+0.143, Q4=+0.108, Q5_high_vol=+0.161

**`combo_sig_product__volatility_expansion_trend_vector__first_bar_return`** (Lock IC=-0.1430, Sharpe=-2.8810)
- Admission: Train IC=+0.1833, Deflated=+0.1815, IR=0.53, Mono=0.72, p=0.0000, MaxCorr=0.98
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
- Admission: Train IC=+0.1730, Deflated=+0.1705, IR=0.54, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.057 | 2016: -0.034 | 2017: +0.074 | 2018: +0.070 | 2019: +0.049 | 2020: +0.046 | 2021: +0.111 | 2022: +0.147 | 2023: +0.073 | 2024: +0.098 | 2025: +0.093 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.018 | 2016: -0.163 | 2017: +0.111 | 2018: +0.265 | 2019: +0.033 | 2020: +0.028 | 2021: +0.187 | 2022: +0.244 | 2023: +0.235 | 2024: +0.410 | 2025: -0.004 | 2026: -0.090
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=1.58, Recency ratio=1.60
- Early IC=+0.0594, Recent IC=+0.0953, 1st-half IC=+0.0680, 2nd-half IC=+0.1072, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.057, Q3_mid=+0.113, Q4=+0.094, Q5_high_vol=+0.053

**`range_progression_trend`** (Lock IC=-0.1829, Sharpe=-2.7117)
- Admission: Train IC=+0.1869, Deflated=+0.1845, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.082 | 2016: -0.030 | 2017: +0.063 | 2018: +0.063 | 2019: +0.071 | 2020: +0.033 | 2021: +0.100 | 2022: +0.158 | 2023: +0.056 | 2024: +0.086 | 2025: +0.101 | 2026: -0.183
- Yearly Tail ICs:   2015: +0.062 | 2016: -0.063 | 2017: +0.088 | 2018: +0.231 | 2019: +0.184 | 2020: +0.104 | 2021: +0.204 | 2022: +0.310 | 2023: +0.152 | 2024: +0.295 | 2025: +0.024 | 2026: -0.028
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.60, Recency ratio=1.39
- Early IC=+0.0670, Recent IC=+0.0934, 1st-half IC=+0.0663, 2nd-half IC=+0.1060, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.067, Q3_mid=+0.097, Q4=+0.094, Q5_high_vol=+0.072

**`vwap_trend_channel_slope`** (Lock IC=-0.0312, Sharpe=-2.6274)
- Admission: Train IC=+0.1273, Deflated=+0.1271, IR=0.57, Mono=0.69, p=0.0100, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.20, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.29
- Early IC=+0.0767, Recent IC=+0.0989, 1st-half IC=+0.0768, 2nd-half IC=+0.1042, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.085, Q3_mid=+0.127, Q4=+0.050, Q5_high_vol=+0.097

**`num_up_bars`** (Lock IC=-0.0474, Sharpe=-2.5885)
- Admission: Train IC=+0.1263, Deflated=+0.1254, IR=0.39, Mono=0.67, p=0.0110, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.077 | 2016: +0.103 | 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141 | 2025: +0.117 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.253 | 2017: +0.002 | 2018: +0.082 | 2019: +0.121 | 2020: +0.184 | 2021: -0.075 | 2022: +0.221 | 2023: +0.122 | 2024: +0.211 | 2025: -0.019 | 2026: -0.077
- IC CV=0.35, Neg years (linear/tail)=0/2 of 8, Half ratio=1.67, Recency ratio=1.35
- Early IC=+0.0951, Recent IC=+0.1286, 1st-half IC=+0.0751, 2nd-half IC=+0.1257, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.113, Q3_mid=+0.140, Q4=+0.079, Q5_high_vol=+0.093

**`combo_rank_min__first_bar_sentiment__bar_ret_0`** (Lock IC=-0.0261, Sharpe=-2.5653)
- Admission: Train IC=+0.1520, Deflated=+0.1512, IR=0.61, Mono=0.72, p=0.0020, MaxCorr=0.95
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

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0112, Sharpe=-2.4432)
- Admission: Train IC=+0.1717, Deflated=+0.1716, IR=0.59, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.138 | 2017: +0.182 | 2018: +0.236 | 2019: +0.137 | 2020: +0.139 | 2021: +0.082 | 2022: +0.106 | 2023: +0.072 | 2024: +0.085 | 2025: +0.104 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.208 | 2017: +0.379 | 2018: +0.328 | 2019: +0.214 | 2020: +0.144 | 2021: -0.019 | 2022: +0.280 | 2023: +0.114 | 2024: +0.081 | 2025: +0.141 | 2026: -0.253
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=0.51
- Early IC=+0.1861, Recent IC=+0.0943, 1st-half IC=+0.1466, 2nd-half IC=+0.0985, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.004, Q3_mid=+0.099, Q4=+0.141, Q5_high_vol=+0.200

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=-0.0473, Sharpe=-2.4121)
- Admission: Train IC=+0.1735, Deflated=+0.1725, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.63
- Yearly Linear ICs: 2015: +0.140 | 2016: -0.050 | 2017: +0.104 | 2018: +0.030 | 2019: +0.077 | 2020: +0.065 | 2021: +0.059 | 2022: +0.033 | 2023: +0.007 | 2024: +0.197 | 2025: +0.019 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.369 | 2016: -0.078 | 2017: +0.131 | 2018: +0.261 | 2019: +0.278 | 2020: +0.012 | 2021: +0.267 | 2022: +0.172 | 2023: +0.001 | 2024: +0.354 | 2025: +0.083 | 2026: -0.162
- IC CV=0.92, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=2.02
- Early IC=+0.0534, Recent IC=+0.1078, 1st-half IC=+0.0500, 2nd-half IC=+0.0728, Neg regimes=1/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.99, neg years=1)
- Regime ICs: Q1_low_vol=-0.021, Q2=+0.018, Q3_mid=+0.154, Q4=+0.090, Q5_high_vol=+0.039

**`early_body_momentum`** (Lock IC=-0.0993, Sharpe=-2.3762)
- Admission: Train IC=+0.1782, Deflated=+0.1769, IR=0.41, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.056 | 2017: +0.120 | 2018: +0.113 | 2019: +0.038 | 2020: +0.083 | 2021: +0.046 | 2022: +0.118 | 2023: +0.087 | 2024: +0.107 | 2025: +0.135 | 2026: -0.099
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.133 | 2017: +0.081 | 2018: +0.142 | 2019: +0.132 | 2020: +0.274 | 2021: +0.217 | 2022: +0.118 | 2023: +0.118 | 2024: +0.211 | 2025: +0.009 | 2026: -0.159
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.61, Recency ratio=1.61
- Early IC=+0.0752, Recent IC=+0.1208, 1st-half IC=+0.0721, 2nd-half IC=+0.1162, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.087, Q3_mid=+0.139, Q4=+0.082, Q5_high_vol=+0.080

**`volatility_expansion_trend_vector`** (Lock IC=-0.0850, Sharpe=-2.3631)
- Admission: Train IC=+0.2278, Deflated=+0.2263, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.061 | 2017: +0.201 | 2018: +0.129 | 2019: +0.076 | 2020: +0.097 | 2021: +0.073 | 2022: +0.093 | 2023: +0.089 | 2024: +0.123 | 2025: +0.155 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.306 | 2016: -0.052 | 2017: +0.291 | 2018: +0.219 | 2019: +0.292 | 2020: +0.226 | 2021: +0.227 | 2022: +0.241 | 2023: +0.284 | 2024: +0.228 | 2025: +0.065 | 2026: -0.099
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.29, Recency ratio=1.36
- Early IC=+0.1024, Recent IC=+0.1390, 1st-half IC=+0.0933, 2nd-half IC=+0.1204, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.081, Q3_mid=+0.139, Q4=+0.108, Q5_high_vol=+0.128

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0689, Sharpe=-2.3631)
- Admission: Train IC=+0.2158, Deflated=+0.2159, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.95
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
- Admission: Train IC=+0.2018, Deflated=+0.2010, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.94
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
- Admission: Train IC=+0.1797, Deflated=+0.1789, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.084 | 2017: +0.097 | 2018: +0.141 | 2019: +0.071 | 2020: +0.077 | 2021: +0.107 | 2022: +0.120 | 2023: +0.115 | 2024: +0.112 | 2025: +0.141 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.162 | 2017: +0.119 | 2018: +0.224 | 2019: +0.145 | 2020: +0.125 | 2021: +0.287 | 2022: +0.099 | 2023: +0.156 | 2024: +0.179 | 2025: +0.146 | 2026: -0.395
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=1.28, Recency ratio=1.19
- Early IC=+0.1063, Recent IC=+0.1269, 1st-half IC=+0.0973, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.070, Q3_mid=+0.144, Q4=+0.112, Q5_high_vol=+0.129

**`first_30min_return`** (Lock IC=-0.1128, Sharpe=-2.1381)
- Admission: Train IC=+0.1826, Deflated=+0.1808, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.32, Recency ratio=1.35
- Early IC=+0.1053, Recent IC=+0.1420, 1st-half IC=+0.0956, 2nd-half IC=+0.1262, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.093, Q3_mid=+0.140, Q4=+0.100, Q5_high_vol=+0.130

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=-0.0710, Sharpe=-2.1354)
- Admission: Train IC=+0.1709, Deflated=+0.1714, IR=0.57, Mono=0.74, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.142 | 2017: +0.116 | 2018: +0.276 | 2019: +0.086 | 2020: +0.115 | 2021: +0.110 | 2022: +0.109 | 2023: +0.023 | 2024: +0.102 | 2025: +0.095 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.143 | 2016: +0.092 | 2017: +0.306 | 2018: +0.468 | 2019: +0.081 | 2020: +0.215 | 2021: +0.204 | 2022: -0.009 | 2023: +0.021 | 2024: +0.172 | 2025: +0.155 | 2026: -0.305
- IC CV=0.58, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.54
- Early IC=+0.1808, Recent IC=+0.0985, 1st-half IC=+0.1425, 2nd-half IC=+0.0872, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.029, Q3_mid=+0.059, Q4=+0.132, Q5_high_vol=+0.176

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=-0.0695, Sharpe=-2.1354)
- Admission: Train IC=+0.1709, Deflated=+0.1713, IR=0.57, Mono=0.74, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.142 | 2017: +0.115 | 2018: +0.276 | 2019: +0.086 | 2020: +0.115 | 2021: +0.110 | 2022: +0.109 | 2023: +0.023 | 2024: +0.102 | 2025: +0.094 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.142 | 2016: +0.092 | 2017: +0.306 | 2018: +0.468 | 2019: +0.081 | 2020: +0.215 | 2021: +0.204 | 2022: -0.008 | 2023: +0.021 | 2024: +0.172 | 2025: +0.155 | 2026: -0.305
- IC CV=0.59, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.54
- Early IC=+0.1807, Recent IC=+0.0980, 1st-half IC=+0.1425, 2nd-half IC=+0.0871, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.028, Q3_mid=+0.058, Q4=+0.132, Q5_high_vol=+0.176

**`combo_max__first_bar_sentiment__high_low_sequence_momentum`** (Lock IC=-0.0160, Sharpe=-2.1082)
- Admission: Train IC=+0.1573, Deflated=+0.1572, IR=0.46, Mono=0.66, p=0.0012, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.081 | 2017: +0.144 | 2018: +0.180 | 2019: +0.097 | 2020: +0.108 | 2021: +0.108 | 2022: +0.135 | 2023: +0.045 | 2024: +0.130 | 2025: +0.097 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.103 | 2017: -0.017 | 2018: +0.120 | 2019: +0.294 | 2020: +0.294 | 2021: -0.012 | 2022: +0.282 | 2023: +0.077 | 2024: +0.327 | 2025: -0.008 | 2026: -0.092
- IC CV=0.32, Neg years (linear/tail)=0/2 of 8, Half ratio=0.94, Recency ratio=0.82
- Early IC=+0.1385, Recent IC=+0.1134, 1st-half IC=+0.1157, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43, neg years=0)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.053, Q3_mid=+0.146, Q4=+0.121, Q5_high_vol=+0.152

**`combo_min__net_volume_flow__first_bar_sentiment`** (Lock IC=-0.0444, Sharpe=-2.0572)
- Admission: Train IC=+0.2859, Deflated=+0.2850, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.00
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
- Admission: Train IC=+0.2196, Deflated=+0.2187, IR=0.75, Mono=0.79, p=0.0000, MaxCorr=0.93
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
- Admission: Train IC=+0.2469, Deflated=+0.2461, IR=0.76, Mono=0.81, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.054 | 2017: +0.132 | 2018: +0.132 | 2019: +0.095 | 2020: +0.121 | 2021: +0.106 | 2022: +0.097 | 2023: +0.111 | 2024: +0.145 | 2025: +0.132 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.350 | 2016: +0.136 | 2017: +0.155 | 2018: +0.273 | 2019: +0.217 | 2020: +0.271 | 2021: +0.252 | 2022: +0.320 | 2023: +0.227 | 2024: +0.290 | 2025: +0.026 | 2026: -0.190
- IC CV=0.14, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.22
- Early IC=+0.1135, Recent IC=+0.1385, 1st-half IC=+0.1115, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71, neg years=1)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.070, Q3_mid=+0.152, Q4=+0.128, Q5_high_vol=+0.135

**`combo_min__close_vs_open_range__early_body_momentum`** (Lock IC=-0.0785, Sharpe=-1.9210)
- Admission: Train IC=+0.1744, Deflated=+0.1732, IR=0.42, Mono=0.65, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.064 | 2017: +0.155 | 2018: +0.108 | 2019: +0.052 | 2020: +0.095 | 2021: +0.051 | 2022: +0.112 | 2023: +0.094 | 2024: +0.107 | 2025: +0.142 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.199 | 2017: +0.312 | 2018: +0.237 | 2019: +0.098 | 2020: +0.283 | 2021: +0.226 | 2022: +0.125 | 2023: +0.071 | 2024: +0.225 | 2025: -0.042 | 2026: -0.062
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.52, Recency ratio=1.56
- Early IC=+0.0801, Recent IC=+0.1248, 1st-half IC=+0.0779, 2nd-half IC=+0.1187, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.096, Q3_mid=+0.126, Q4=+0.093, Q5_high_vol=+0.102

**`micro_gap_trend_continuation`** (Lock IC=-0.0765, Sharpe=-1.9190)
- Admission: Train IC=+0.1137, Deflated=+0.1129, IR=0.36, Mono=0.65, p=0.0228, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.025 | 2017: +0.110 | 2018: +0.011 | 2019: +0.032 | 2020: +0.062 | 2021: +0.024 | 2022: +0.076 | 2023: +0.098 | 2024: +0.046 | 2025: +0.178 | 2026: -0.077
- Yearly Tail ICs:   2015: -0.023 | 2016: +0.144 | 2017: +0.187 | 2018: -0.093 | 2019: -0.001 | 2020: +0.050 | 2021: +0.278 | 2022: +0.185 | 2023: +0.045 | 2024: +0.326 | 2025: +0.126 | 2026: +0.078
- IC CV=0.76, Neg years (linear/tail)=0/2 of 8, Half ratio=2.88, Recency ratio=5.15
- Early IC=+0.0217, Recent IC=+0.1119, 1st-half IC=+0.0364, 2nd-half IC=+0.1049, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.070, Q3_mid=+0.132, Q4=+0.047, Q5_high_vol=+0.025

**`combo_rank_max__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=-0.0686, Sharpe=-1.8069)
- Admission: Train IC=+0.2229, Deflated=+0.2221, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.048 | 2017: +0.216 | 2018: +0.159 | 2019: +0.107 | 2020: +0.105 | 2021: +0.088 | 2022: +0.062 | 2023: +0.047 | 2024: +0.136 | 2025: +0.153 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.350 | 2016: -0.108 | 2017: +0.230 | 2018: +0.127 | 2019: +0.354 | 2020: +0.058 | 2021: +0.265 | 2022: +0.230 | 2023: +0.214 | 2024: +0.304 | 2025: +0.243 | 2026: -0.150
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=1.10
- Early IC=+0.1327, Recent IC=+0.1457, 1st-half IC=+0.1092, 2nd-half IC=+0.1056, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39, neg years=0)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.073, Q3_mid=+0.143, Q4=+0.122, Q5_high_vol=+0.127

**`combo_mean__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=-0.0328, Sharpe=-1.7902)
- Admission: Train IC=+0.2606, Deflated=+0.2598, IR=0.88, Mono=0.77, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.086 | 2017: +0.212 | 2018: +0.202 | 2019: +0.113 | 2020: +0.115 | 2021: +0.105 | 2022: +0.092 | 2023: +0.077 | 2024: +0.137 | 2025: +0.129 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.250 | 2016: -0.023 | 2017: +0.238 | 2018: +0.361 | 2019: +0.233 | 2020: +0.254 | 2021: +0.279 | 2022: +0.303 | 2023: +0.340 | 2024: +0.209 | 2025: +0.180 | 2026: -0.232
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.85
- Early IC=+0.1574, Recent IC=+0.1334, 1st-half IC=+0.1306, 2nd-half IC=+0.1143, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.057, Q3_mid=+0.126, Q4=+0.129, Q5_high_vol=+0.173

**`combo_mean__volatility_expansion_trend_vector__first_bar_return`** (Lock IC=-0.0328, Sharpe=-1.7902)
- Admission: Train IC=+0.2605, Deflated=+0.2597, IR=0.88, Mono=0.77, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.086 | 2017: +0.212 | 2018: +0.202 | 2019: +0.113 | 2020: +0.115 | 2021: +0.105 | 2022: +0.092 | 2023: +0.077 | 2024: +0.138 | 2025: +0.129 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.251 | 2016: -0.020 | 2017: +0.238 | 2018: +0.361 | 2019: +0.233 | 2020: +0.257 | 2021: +0.279 | 2022: +0.303 | 2023: +0.340 | 2024: +0.213 | 2025: +0.178 | 2026: -0.232
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.85
- Early IC=+0.1573, Recent IC=+0.1334, 1st-half IC=+0.1306, 2nd-half IC=+0.1143, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.058, Q3_mid=+0.126, Q4=+0.129, Q5_high_vol=+0.173

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
- Admission: Train IC=+0.1720, Deflated=+0.1705, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.039 | 2017: +0.203 | 2018: +0.126 | 2019: +0.090 | 2020: +0.097 | 2021: +0.088 | 2022: +0.095 | 2023: +0.096 | 2024: +0.115 | 2025: +0.165 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.078 | 2017: +0.280 | 2018: +0.104 | 2019: +0.039 | 2020: +0.117 | 2021: +0.174 | 2022: +0.149 | 2023: +0.283 | 2024: +0.184 | 2025: +0.241 | 2026: -0.108
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=1.27, Recency ratio=1.29
- Early IC=+0.1081, Recent IC=+0.1398, 1st-half IC=+0.0985, 2nd-half IC=+0.1255, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.098, Q3_mid=+0.146, Q4=+0.100, Q5_high_vol=+0.125

**`combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=-0.0411, Sharpe=-1.7157)
- Admission: Train IC=+0.2235, Deflated=+0.2236, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.88
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

**`combo_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=-0.0473, Sharpe=-1.6789)
- Admission: Train IC=+0.2058, Deflated=+0.2050, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.088 | 2017: +0.215 | 2018: +0.161 | 2019: +0.087 | 2020: +0.153 | 2021: +0.106 | 2022: +0.108 | 2023: +0.074 | 2024: +0.151 | 2025: +0.115 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.375 | 2016: +0.246 | 2017: +0.356 | 2018: +0.165 | 2019: +0.236 | 2020: +0.261 | 2021: +0.220 | 2022: +0.194 | 2023: +0.232 | 2024: +0.288 | 2025: -0.009 | 2026: -0.193
- IC CV=0.25, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=1.07
- Early IC=+0.1238, Recent IC=+0.1325, 1st-half IC=+0.1261, 2nd-half IC=+0.1195, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36, neg years=0)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.084, Q3_mid=+0.165, Q4=+0.141, Q5_high_vol=+0.144

**`combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=-0.0503, Sharpe=-1.6591)
- Admission: Train IC=+0.2357, Deflated=+0.2348, IR=0.69, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.042 | 2017: +0.183 | 2018: +0.163 | 2019: +0.075 | 2020: +0.104 | 2021: +0.092 | 2022: +0.071 | 2023: +0.115 | 2024: +0.139 | 2025: +0.109 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.395 | 2016: +0.235 | 2017: +0.265 | 2018: +0.295 | 2019: +0.232 | 2020: +0.157 | 2021: +0.305 | 2022: +0.290 | 2023: +0.220 | 2024: +0.322 | 2025: +0.059 | 2026: +0.050
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=1.04
- Early IC=+0.1188, Recent IC=+0.1239, 1st-half IC=+0.1082, 2nd-half IC=+0.1168, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.061, Q3_mid=+0.144, Q4=+0.102, Q5_high_vol=+0.161

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
- Admission: Train IC=+0.2208, Deflated=+0.2205, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.85
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
- Admission: Train IC=+0.2414, Deflated=+0.2405, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.98
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

**`combo_min__trend_bar_close_consistency__bar_ret_0`** (Lock IC=-0.0156, Sharpe=-0.9099)
- Admission: Train IC=+0.2117, Deflated=+0.2111, IR=0.65, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.055 | 2017: +0.156 | 2018: +0.155 | 2019: +0.101 | 2020: +0.048 | 2021: +0.050 | 2022: +0.064 | 2023: +0.075 | 2024: +0.125 | 2025: +0.123 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.024 | 2017: +0.342 | 2018: +0.399 | 2019: +0.085 | 2020: +0.043 | 2021: +0.314 | 2022: +0.266 | 2023: +0.043 | 2024: +0.325 | 2025: +0.165 | 2026: +0.022
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.96
- Early IC=+0.1283, Recent IC=+0.1237, 1st-half IC=+0.0896, 2nd-half IC=+0.0990, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.018, Q3_mid=+0.107, Q4=+0.099, Q5_high_vol=+0.130

**`combo_min__trend_bar_close_consistency__first_bar_return`** (Lock IC=-0.0156, Sharpe=-0.9099)
- Admission: Train IC=+0.2116, Deflated=+0.2109, IR=0.65, Mono=0.70, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.055 | 2017: +0.156 | 2018: +0.155 | 2019: +0.101 | 2020: +0.048 | 2021: +0.050 | 2022: +0.064 | 2023: +0.075 | 2024: +0.125 | 2025: +0.123 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.025 | 2017: +0.341 | 2018: +0.401 | 2019: +0.086 | 2020: +0.043 | 2021: +0.313 | 2022: +0.266 | 2023: +0.043 | 2024: +0.325 | 2025: +0.165 | 2026: +0.022
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.97
- Early IC=+0.1282, Recent IC=+0.1240, 1st-half IC=+0.0896, 2nd-half IC=+0.0991, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.018, Q3_mid=+0.107, Q4=+0.099, Q5_high_vol=+0.130

**`combo_rank_min__max_up_ret__bar_ret_0`** (Lock IC=-0.0007, Sharpe=-0.8149)
- Admission: Train IC=+0.2046, Deflated=+0.2049, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.91
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

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=-0.0016, Sharpe=-0.3308)
- Admission: Train IC=+0.2091, Deflated=+0.2082, IR=0.70, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.076 | 2017: +0.206 | 2018: +0.203 | 2019: +0.147 | 2020: +0.157 | 2021: +0.112 | 2022: +0.092 | 2023: +0.133 | 2024: +0.137 | 2025: +0.113 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.449 | 2016: +0.230 | 2017: +0.305 | 2018: +0.304 | 2019: +0.186 | 2020: +0.207 | 2021: +0.268 | 2022: +0.211 | 2023: +0.255 | 2024: +0.234 | 2025: +0.061 | 2026: -0.207
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.72
- Early IC=+0.1748, Recent IC=+0.1252, 1st-half IC=+0.1538, 2nd-half IC=+0.1276, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49, neg years=0)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.067, Q3_mid=+0.175, Q4=+0.119, Q5_high_vol=+0.199

**`combo_min__net_volume_flow__bar_ret_0`** (Lock IC=-0.0010, Sharpe=-0.2212)
- Admission: Train IC=+0.2435, Deflated=+0.2432, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.072 | 2017: +0.181 | 2018: +0.177 | 2019: +0.120 | 2020: +0.094 | 2021: +0.083 | 2022: +0.085 | 2023: +0.078 | 2024: +0.134 | 2025: +0.124 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.015 | 2017: +0.228 | 2018: +0.378 | 2019: +0.143 | 2020: +0.115 | 2021: +0.287 | 2022: +0.225 | 2023: +0.314 | 2024: +0.341 | 2025: +0.140 | 2026: -0.072
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.87
- Early IC=+0.1487, Recent IC=+0.1291, 1st-half IC=+0.1184, 2nd-half IC=+0.1115, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48, neg years=0)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.044, Q3_mid=+0.133, Q4=+0.115, Q5_high_vol=+0.151

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=-0.0061, Sharpe=+0.1883)
- Admission: Train IC=+0.1965, Deflated=+0.1957, IR=0.69, Mono=0.81, p=0.0000, MaxCorr=0.99
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
- Admission: Train IC=+0.2332, Deflated=+0.2339, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.049 | 2017: +0.052 | 2018: +0.048 | 2019: +0.121 | 2020: +0.095 | 2021: +0.165 | 2022: +0.100 | 2023: +0.183 | 2024: +0.066 | 2025: +0.191 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.081 | 2017: +0.036 | 2018: +0.109 | 2019: +0.301 | 2020: +0.094 | 2021: +0.300 | 2022: +0.294 | 2023: +0.482 | 2024: +0.248 | 2025: +0.089 | 2026: -0.564
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.40, Recency ratio=1.52
- Early IC=+0.0847, Recent IC=+0.1287, 1st-half IC=+0.0998, 2nd-half IC=+0.1400, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.176, Q3_mid=+0.119, Q4=+0.111, Q5_high_vol=+0.104

**`combo_rank_max__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=-0.0746, Sharpe=-4.0254)
- Admission: Train IC=+0.2272, Deflated=+0.2277, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.104 | 2017: +0.038 | 2018: +0.076 | 2019: +0.133 | 2020: +0.131 | 2021: +0.170 | 2022: +0.106 | 2023: +0.156 | 2024: +0.073 | 2025: +0.187 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.325 | 2016: -0.103 | 2017: +0.112 | 2018: +0.122 | 2019: +0.266 | 2020: +0.099 | 2021: +0.262 | 2022: +0.326 | 2023: +0.376 | 2024: +0.114 | 2025: +0.296 | 2026: -0.399
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.29
- Early IC=+0.1039, Recent IC=+0.1340, 1st-half IC=+0.1198, 2nd-half IC=+0.1365, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.170, Q3_mid=+0.161, Q4=+0.092, Q5_high_vol=+0.110

**`combo_max__bar_ret_0__volatility_expansion_trend_vector`** (Lock IC=-0.0815, Sharpe=-4.0036)
- Admission: Train IC=+0.2266, Deflated=+0.2271, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.079 | 2017: +0.049 | 2018: +0.077 | 2019: +0.126 | 2020: +0.122 | 2021: +0.181 | 2022: +0.085 | 2023: +0.157 | 2024: +0.069 | 2025: +0.208 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.148 | 2016: -0.173 | 2017: +0.133 | 2018: +0.208 | 2019: +0.283 | 2020: +0.072 | 2021: +0.303 | 2022: +0.264 | 2023: +0.354 | 2024: +0.133 | 2025: +0.422 | 2026: -0.613
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.36
- Early IC=+0.1019, Recent IC=+0.1383, 1st-half IC=+0.1183, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.169, Q3_mid=+0.163, Q4=+0.093, Q5_high_vol=+0.102

**`combo_max__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=-0.0816, Sharpe=-4.0036)
- Admission: Train IC=+0.2264, Deflated=+0.2270, IR=0.69, Mono=0.76, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.079 | 2017: +0.050 | 2018: +0.077 | 2019: +0.126 | 2020: +0.122 | 2021: +0.181 | 2022: +0.085 | 2023: +0.158 | 2024: +0.069 | 2025: +0.208 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.151 | 2016: -0.173 | 2017: +0.133 | 2018: +0.208 | 2019: +0.283 | 2020: +0.072 | 2021: +0.303 | 2022: +0.264 | 2023: +0.354 | 2024: +0.133 | 2025: +0.423 | 2026: -0.613
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.36
- Early IC=+0.1017, Recent IC=+0.1383, 1st-half IC=+0.1182, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.169, Q3_mid=+0.163, Q4=+0.093, Q5_high_vol=+0.102

**`combo_tri_max__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=-0.0730, Sharpe=-3.6387)
- Admission: Train IC=+0.2430, Deflated=+0.2429, IR=0.81, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.159 | 2017: -0.011 | 2018: +0.113 | 2019: +0.196 | 2020: +0.141 | 2021: +0.177 | 2022: +0.102 | 2023: +0.147 | 2024: +0.055 | 2025: +0.168 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.066 | 2016: +0.202 | 2017: +0.013 | 2018: +0.210 | 2019: +0.288 | 2020: +0.136 | 2021: +0.382 | 2022: +0.269 | 2023: +0.416 | 2024: +0.241 | 2025: +0.138 | 2026: -0.371
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.72
- Early IC=+0.1542, Recent IC=+0.1117, 1st-half IC=+0.1474, 2nd-half IC=+0.1203, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.130, Q3_mid=+0.159, Q4=+0.111, Q5_high_vol=+0.131

**`combo_max__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0771, Sharpe=-3.6387)
- Admission: Train IC=+0.2417, Deflated=+0.2416, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.160 | 2017: -0.012 | 2018: +0.104 | 2019: +0.185 | 2020: +0.141 | 2021: +0.171 | 2022: +0.109 | 2023: +0.142 | 2024: +0.059 | 2025: +0.182 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.066 | 2016: +0.181 | 2017: +0.001 | 2018: +0.201 | 2019: +0.295 | 2020: +0.174 | 2021: +0.360 | 2022: +0.247 | 2023: +0.408 | 2024: +0.199 | 2025: +0.156 | 2026: -0.316
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.83
- Early IC=+0.1441, Recent IC=+0.1201, 1st-half IC=+0.1398, 2nd-half IC=+0.1258, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.136, Q3_mid=+0.153, Q4=+0.105, Q5_high_vol=+0.131

**`combo_max__impulse_bar_dominance__volatility_expansion_trend_vector`** (Lock IC=-0.1105, Sharpe=-3.4044)
- Admission: Train IC=+0.2414, Deflated=+0.2412, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.145 | 2016: +0.017 | 2017: +0.029 | 2018: +0.055 | 2019: +0.063 | 2020: +0.044 | 2021: +0.123 | 2022: +0.110 | 2023: +0.165 | 2024: +0.104 | 2025: +0.170 | 2026: -0.110
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.057 | 2017: -0.034 | 2018: -0.014 | 2019: +0.169 | 2020: +0.127 | 2021: +0.132 | 2022: +0.352 | 2023: +0.312 | 2024: +0.230 | 2025: +0.328 | 2026: -0.417
- IC CV=0.43, Neg years (linear/tail)=0/1 of 8, Half ratio=2.42, Recency ratio=2.32
- Early IC=+0.0590, Recent IC=+0.1369, 1st-half IC=+0.0602, 2nd-half IC=+0.1457, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.137, Q3_mid=+0.113, Q4=+0.084, Q5_high_vol=+0.112

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`** (Lock IC=-0.0653, Sharpe=-3.3106)
- Admission: Train IC=+0.2366, Deflated=+0.2366, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.098 | 2017: +0.035 | 2018: +0.092 | 2019: +0.185 | 2020: +0.107 | 2021: +0.187 | 2022: +0.094 | 2023: +0.184 | 2024: +0.070 | 2025: +0.173 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.106 | 2017: +0.122 | 2018: +0.242 | 2019: +0.298 | 2020: +0.049 | 2021: +0.316 | 2022: +0.310 | 2023: +0.380 | 2024: +0.184 | 2025: +0.223 | 2026: -0.334
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.88
- Early IC=+0.1383, Recent IC=+0.1215, 1st-half IC=+0.1329, 2nd-half IC=+0.1301, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.153, Q3_mid=+0.128, Q4=+0.125, Q5_high_vol=+0.137

**`combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=-0.0381, Sharpe=-3.2808)
- Admission: Train IC=+0.2801, Deflated=+0.2805, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.90
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

**`combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=-0.0820, Sharpe=-3.0532)
- Admission: Train IC=+0.2248, Deflated=+0.2248, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.039 | 2017: +0.044 | 2018: +0.020 | 2019: +0.146 | 2020: +0.031 | 2021: +0.189 | 2022: +0.052 | 2023: +0.168 | 2024: +0.082 | 2025: +0.195 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.142 | 2016: -0.049 | 2017: +0.147 | 2018: +0.069 | 2019: +0.455 | 2020: +0.087 | 2021: +0.215 | 2022: +0.156 | 2023: +0.307 | 2024: +0.146 | 2025: +0.283 | 2026: -0.313
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.66
- Early IC=+0.0830, Recent IC=+0.1383, 1st-half IC=+0.0874, 2nd-half IC=+0.1315, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.157, Q3_mid=+0.144, Q4=+0.086, Q5_high_vol=+0.092

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0737, Sharpe=-3.0060)
- Admission: Train IC=+0.2261, Deflated=+0.2260, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.084 | 2017: +0.064 | 2018: +0.067 | 2019: +0.173 | 2020: +0.066 | 2021: +0.220 | 2022: +0.089 | 2023: +0.165 | 2024: +0.079 | 2025: +0.179 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.017 | 2017: +0.238 | 2018: +0.208 | 2019: +0.343 | 2020: -0.017 | 2021: +0.310 | 2022: +0.236 | 2023: +0.279 | 2024: +0.249 | 2025: +0.235 | 2026: -0.216
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=1.02, Recency ratio=1.07
- Early IC=+0.1207, Recent IC=+0.1297, 1st-half IC=+0.1257, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.155, Q3_mid=+0.136, Q4=+0.125, Q5_high_vol=+0.133

**`max_up_ret`** (Lock IC=-0.0753, Sharpe=-2.9698)
- Admission: Train IC=+0.2319, Deflated=+0.2324, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074 | 2025: +0.164 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.198 | 2017: +0.106 | 2018: +0.212 | 2019: +0.279 | 2020: +0.177 | 2021: +0.343 | 2022: +0.267 | 2023: +0.389 | 2024: +0.190 | 2025: +0.128 | 2026: -0.261
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.13
- Early IC=+0.1048, Recent IC=+0.1187, 1st-half IC=+0.1197, 2nd-half IC=+0.1306, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.168, Q3_mid=+0.110, Q4=+0.123, Q5_high_vol=+0.121

**`combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`** (Lock IC=-0.1124, Sharpe=-2.9139)
- Admission: Train IC=+0.2411, Deflated=+0.2415, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.139 | 2016: -0.016 | 2017: +0.025 | 2018: -0.001 | 2019: +0.101 | 2020: +0.029 | 2021: +0.131 | 2022: +0.121 | 2023: +0.163 | 2024: +0.076 | 2025: +0.195 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.220 | 2016: -0.087 | 2017: +0.168 | 2018: +0.072 | 2019: +0.301 | 2020: -0.023 | 2021: +0.045 | 2022: +0.211 | 2023: +0.258 | 2024: +0.196 | 2025: +0.274 | 2026: -0.335
- IC CV=0.60, Neg years (linear/tail)=1/1 of 8, Half ratio=2.78, Recency ratio=2.71
- Early IC=+0.0501, Recent IC=+0.1359, 1st-half IC=+0.0521, 2nd-half IC=+0.1446, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.142, Q3_mid=+0.131, Q4=+0.083, Q5_high_vol=+0.076

**`combo_max__first_bar_sentiment__volatility_expansion_trend_vector`** (Lock IC=-0.0844, Sharpe=-2.9139)
- Admission: Train IC=+0.2041, Deflated=+0.2044, IR=0.58, Mono=0.72, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.074 | 2017: -0.000 | 2018: +0.067 | 2019: +0.163 | 2020: +0.129 | 2021: +0.102 | 2022: +0.080 | 2023: +0.132 | 2024: +0.089 | 2025: +0.170 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.322 | 2016: -0.009 | 2017: -0.026 | 2018: -0.086 | 2019: +0.382 | 2020: +0.266 | 2021: +0.138 | 2022: +0.306 | 2023: +0.359 | 2024: +0.119 | 2025: +0.305 | 2026: -0.321
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=1.21, Recency ratio=1.12
- Early IC=+0.1152, Recent IC=+0.1294, 1st-half IC=+0.1047, 2nd-half IC=+0.1269, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.138, Q3_mid=+0.167, Q4=+0.069, Q5_high_vol=+0.104

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0854, Sharpe=-2.9019)
- Admission: Train IC=+0.2440, Deflated=+0.2438, IR=0.75, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.71, Recency ratio=2.05
- Early IC=+0.0722, Recent IC=+0.1480, 1st-half IC=+0.0848, 2nd-half IC=+0.1448, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.151, Q3_mid=+0.136, Q4=+0.096, Q5_high_vol=+0.107

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0595, Sharpe=-2.7716)
- Admission: Train IC=+0.2532, Deflated=+0.2535, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.10
- Early IC=+0.1138, Recent IC=+0.1250, 1st-half IC=+0.1234, 2nd-half IC=+0.1399, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.124, Q2=+0.173, Q3_mid=+0.106, Q4=+0.143, Q5_high_vol=+0.142

**`combo_rank_min__max_up_ret__impulse_bar_dominance`** (Lock IC=-0.1166, Sharpe=-2.7310)
- Admission: Train IC=+0.1796, Deflated=+0.1797, IR=0.68, Mono=0.74, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.036 | 2017: +0.034 | 2018: +0.058 | 2019: +0.074 | 2020: +0.030 | 2021: +0.158 | 2022: +0.146 | 2023: +0.176 | 2024: +0.092 | 2025: +0.166 | 2026: -0.116
- Yearly Tail ICs:   2015: -0.161 | 2016: +0.189 | 2017: +0.145 | 2018: +0.158 | 2019: +0.172 | 2020: +0.018 | 2021: +0.124 | 2022: +0.357 | 2023: +0.418 | 2024: +0.282 | 2025: +0.215 | 2026: -0.226
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=2.02, Recency ratio=1.95
- Early IC=+0.0676, Recent IC=+0.1318, 1st-half IC=+0.0731, 2nd-half IC=+0.1479, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.147, Q3_mid=+0.128, Q4=+0.080, Q5_high_vol=+0.115

**`combo_mean__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0430, Sharpe=-2.7211)
- Admission: Train IC=+0.2137, Deflated=+0.2143, IR=0.74, Mono=0.77, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.123 | 2017: +0.019 | 2018: +0.111 | 2019: +0.180 | 2020: +0.145 | 2021: +0.151 | 2022: +0.099 | 2023: +0.157 | 2024: +0.058 | 2025: +0.146 | 2026: -0.043
- Yearly Tail ICs:   2015: +0.067 | 2016: +0.237 | 2017: +0.106 | 2018: +0.237 | 2019: +0.279 | 2020: +0.171 | 2021: +0.286 | 2022: +0.250 | 2023: +0.389 | 2024: +0.155 | 2025: +0.060 | 2026: -0.205
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.70
- Early IC=+0.1457, Recent IC=+0.1020, 1st-half IC=+0.1410, 2nd-half IC=+0.1132, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.150, Q3_mid=+0.136, Q4=+0.100, Q5_high_vol=+0.129

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0325, Sharpe=-2.6779)
- Admission: Train IC=+0.2159, Deflated=+0.2157, IR=0.70, Mono=0.78, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.041 | 2017: +0.004 | 2018: +0.033 | 2019: +0.128 | 2020: +0.102 | 2021: +0.111 | 2022: +0.075 | 2023: +0.138 | 2024: +0.116 | 2025: +0.195 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.210 | 2016: +0.105 | 2017: +0.098 | 2018: -0.016 | 2019: +0.319 | 2020: +0.179 | 2021: +0.151 | 2022: +0.361 | 2023: +0.373 | 2024: +0.169 | 2025: +0.260 | 2026: -0.291
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=1.53, Recency ratio=1.93
- Early IC=+0.0807, Recent IC=+0.1557, 1st-half IC=+0.0904, 2nd-half IC=+0.1381, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.173, Q3_mid=+0.111, Q4=+0.104, Q5_high_vol=+0.109

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.1124, Sharpe=-2.6779)
- Admission: Train IC=+0.2139, Deflated=+0.2137, IR=0.69, Mono=0.77, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.086 | 2016: +0.045 | 2017: +0.069 | 2018: +0.084 | 2019: +0.206 | 2020: +0.077 | 2021: +0.111 | 2022: +0.057 | 2023: +0.173 | 2024: +0.119 | 2025: +0.169 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.081 | 2017: +0.039 | 2018: +0.002 | 2019: +0.273 | 2020: +0.174 | 2021: +0.151 | 2022: +0.352 | 2023: +0.381 | 2024: +0.160 | 2025: +0.280 | 2026: -0.291
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.30, Recency ratio=0.99
- Early IC=+0.1452, Recent IC=+0.1440, 1st-half IC=+0.1048, 2nd-half IC=+0.1359, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.151, Q3_mid=+0.148, Q4=+0.101, Q5_high_vol=+0.113

**`combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector`** (Lock IC=-0.1117, Sharpe=-2.6779)
- Admission: Train IC=+0.2136, Deflated=+0.2140, IR=0.71, Mono=0.78, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.008 | 2017: +0.010 | 2018: +0.034 | 2019: +0.077 | 2020: +0.055 | 2021: +0.129 | 2022: +0.144 | 2023: +0.147 | 2024: +0.070 | 2025: +0.178 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.081 | 2017: +0.039 | 2018: -0.016 | 2019: +0.254 | 2020: +0.179 | 2021: +0.151 | 2022: +0.353 | 2023: +0.381 | 2024: +0.160 | 2025: +0.265 | 2026: -0.291
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=2.36, Recency ratio=2.23
- Early IC=+0.0556, Recent IC=+0.1242, 1st-half IC=+0.0607, 2nd-half IC=+0.1434, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.136, Q3_mid=+0.121, Q4=+0.086, Q5_high_vol=+0.102

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0563, Sharpe=-2.6490)
- Admission: Train IC=+0.2775, Deflated=+0.2775, IR=0.87, Mono=0.78, p=0.0000, MaxCorr=0.91
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

**`combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0833, Sharpe=-2.2128)
- Admission: Train IC=+0.2557, Deflated=+0.2559, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.033 | 2017: +0.028 | 2018: +0.050 | 2019: +0.152 | 2020: +0.069 | 2021: +0.147 | 2022: +0.092 | 2023: +0.191 | 2024: +0.098 | 2025: +0.198 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.265 | 2016: +0.128 | 2017: +0.060 | 2018: -0.075 | 2019: +0.403 | 2020: +0.214 | 2021: +0.104 | 2022: +0.382 | 2023: +0.527 | 2024: +0.224 | 2025: +0.220 | 2026: -0.253
- IC CV=0.42, Neg years (linear/tail)=0/1 of 8, Half ratio=1.60, Recency ratio=1.47
- Early IC=+0.1009, Recent IC=+0.1481, 1st-half IC=+0.0935, 2nd-half IC=+0.1495, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.159, Q3_mid=+0.132, Q4=+0.109, Q5_high_vol=+0.119

**`combo_max__bar_body_rng_0__impulse_bar_dominance`** (Lock IC=-0.0248, Sharpe=-2.1848)
- Admission: Train IC=+0.2211, Deflated=+0.2215, IR=0.63, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.134 | 2017: -0.005 | 2018: +0.105 | 2019: +0.083 | 2020: +0.112 | 2021: +0.158 | 2022: +0.080 | 2023: +0.155 | 2024: +0.025 | 2025: +0.191 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.077 | 2017: +0.072 | 2018: +0.170 | 2019: +0.384 | 2020: +0.034 | 2021: +0.250 | 2022: +0.167 | 2023: +0.293 | 2024: +0.121 | 2025: +0.476 | 2026: -0.326
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=1.16
- Early IC=+0.0936, Recent IC=+0.1083, 1st-half IC=+0.1059, 2nd-half IC=+0.1132, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.125, Q3_mid=+0.120, Q4=+0.090, Q5_high_vol=+0.136

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0232, Sharpe=-2.1679)
- Admission: Train IC=+0.2640, Deflated=+0.2644, IR=0.75, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.133 | 2017: +0.004 | 2018: +0.113 | 2019: +0.211 | 2020: +0.115 | 2021: +0.145 | 2022: +0.058 | 2023: +0.175 | 2024: +0.079 | 2025: +0.162 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.065 | 2017: +0.117 | 2018: +0.209 | 2019: +0.405 | 2020: +0.204 | 2021: +0.208 | 2022: +0.145 | 2023: +0.347 | 2024: +0.318 | 2025: +0.259 | 2026: -0.084
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.74
- Early IC=+0.1617, Recent IC=+0.1202, 1st-half IC=+0.1337, 2nd-half IC=+0.1213, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.133, Q3_mid=+0.136, Q4=+0.093, Q5_high_vol=+0.148

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0177, Sharpe=-2.1380)
- Admission: Train IC=+0.1130, Deflated=+0.1133, IR=0.36, Mono=0.65, p=0.0242, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.244 | 2016: +0.095 | 2017: -0.027 | 2018: +0.075 | 2019: +0.172 | 2020: +0.164 | 2021: +0.131 | 2022: +0.048 | 2023: +0.087 | 2024: +0.056 | 2025: +0.083 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.242 | 2016: -0.262 | 2017: -0.038 | 2018: +0.355 | 2019: +0.243 | 2020: +0.291 | 2021: +0.281 | 2022: +0.162 | 2023: +0.181 | 2024: +0.055 | 2025: +0.121 | 2026: -0.195
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.53, Recency ratio=0.56
- Early IC=+0.1233, Recent IC=+0.0694, 1st-half IC=+0.1286, 2nd-half IC=+0.0686, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.092, Q3_mid=+0.140, Q4=+0.063, Q5_high_vol=+0.104

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.0066, Sharpe=-2.1355)
- Admission: Train IC=+0.2346, Deflated=+0.2348, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.096 | 2017: +0.007 | 2018: +0.085 | 2019: +0.224 | 2020: +0.127 | 2021: +0.111 | 2022: +0.067 | 2023: +0.145 | 2024: +0.086 | 2025: +0.126 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.452 | 2016: +0.163 | 2017: -0.009 | 2018: +0.061 | 2019: +0.407 | 2020: +0.259 | 2021: +0.144 | 2022: +0.189 | 2023: +0.391 | 2024: +0.215 | 2025: +0.315 | 2026: -0.302
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.69
- Early IC=+0.1545, Recent IC=+0.1064, 1st-half IC=+0.1266, 2nd-half IC=+0.1102, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.122, Q3_mid=+0.122, Q4=+0.094, Q5_high_vol=+0.158

**`combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0930, Sharpe=-2.1195)
- Admission: Train IC=+0.2483, Deflated=+0.2487, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.048 | 2017: +0.034 | 2018: +0.048 | 2019: +0.165 | 2020: +0.087 | 2021: +0.143 | 2022: +0.100 | 2023: +0.179 | 2024: +0.106 | 2025: +0.197 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.249 | 2016: -0.053 | 2017: +0.064 | 2018: +0.031 | 2019: +0.396 | 2020: +0.246 | 2021: +0.109 | 2022: +0.308 | 2023: +0.347 | 2024: +0.267 | 2025: +0.295 | 2026: -0.202
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.43
- Early IC=+0.1070, Recent IC=+0.1525, 1st-half IC=+0.1014, 2nd-half IC=+0.1518, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.165, Q3_mid=+0.134, Q4=+0.118, Q5_high_vol=+0.125

**`combo_max__first_bar_return__impulse_bar_dominance`** (Lock IC=-0.0491, Sharpe=-2.0937)
- Admission: Train IC=+0.1797, Deflated=+0.1798, IR=0.62, Mono=0.74, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.055 | 2017: +0.021 | 2018: +0.071 | 2019: +0.054 | 2020: +0.094 | 2021: +0.163 | 2022: +0.075 | 2023: +0.151 | 2024: +0.069 | 2025: +0.147 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.040 | 2017: +0.062 | 2018: +0.242 | 2019: +0.135 | 2020: +0.093 | 2021: +0.308 | 2022: +0.100 | 2023: +0.273 | 2024: +0.074 | 2025: +0.366 | 2026: -0.381
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=1.72
- Early IC=+0.0626, Recent IC=+0.1078, 1st-half IC=+0.0877, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.135, Q3_mid=+0.088, Q4=+0.074, Q5_high_vol=+0.135

**`combo_max__bar_ret_0__impulse_bar_dominance`** (Lock IC=-0.0491, Sharpe=-2.0937)
- Admission: Train IC=+0.1797, Deflated=+0.1798, IR=0.62, Mono=0.74, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.055 | 2017: +0.021 | 2018: +0.071 | 2019: +0.054 | 2020: +0.094 | 2021: +0.163 | 2022: +0.075 | 2023: +0.151 | 2024: +0.069 | 2025: +0.147 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.040 | 2017: +0.062 | 2018: +0.242 | 2019: +0.135 | 2020: +0.093 | 2021: +0.308 | 2022: +0.100 | 2023: +0.273 | 2024: +0.074 | 2025: +0.366 | 2026: -0.381
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=1.73
- Early IC=+0.0625, Recent IC=+0.1078, 1st-half IC=+0.0877, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.135, Q3_mid=+0.088, Q4=+0.074, Q5_high_vol=+0.135

**`combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`** (Lock IC=-0.0102, Sharpe=-2.0687)
- Admission: Train IC=+0.1184, Deflated=+0.1184, IR=0.42, Mono=0.67, p=0.0182, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.001 | 2017: +0.026 | 2018: +0.021 | 2019: +0.089 | 2020: +0.031 | 2021: +0.120 | 2022: +0.109 | 2023: +0.148 | 2024: +0.079 | 2025: +0.119 | 2026: -0.010
- Yearly Tail ICs:   2015: -0.029 | 2016: +0.041 | 2017: +0.087 | 2018: +0.083 | 2019: +0.258 | 2020: -0.152 | 2021: +0.269 | 2022: +0.191 | 2023: +0.255 | 2024: +0.307 | 2025: +0.130 | 2026: -0.145
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=2.07, Recency ratio=1.93
- Early IC=+0.0524, Recent IC=+0.1012, 1st-half IC=+0.0578, 2nd-half IC=+0.1195, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.129, Q3_mid=+0.082, Q4=+0.106, Q5_high_vol=+0.070

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=-0.0318, Sharpe=-2.0212)
- Admission: Train IC=+0.2512, Deflated=+0.2511, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.91
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
- Admission: Train IC=+0.1740, Deflated=+0.1750, IR=0.61, Mono=0.73, p=0.0008, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.149 | 2017: -0.003 | 2018: +0.136 | 2019: +0.198 | 2020: +0.125 | 2021: +0.128 | 2022: +0.061 | 2023: +0.137 | 2024: +0.068 | 2025: +0.133 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.086 | 2017: +0.051 | 2018: +0.253 | 2019: +0.177 | 2020: +0.147 | 2021: +0.212 | 2022: +0.176 | 2023: +0.289 | 2024: +0.089 | 2025: +0.445 | 2026: -0.388
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.1672, Recent IC=+0.1005, 1st-half IC=+0.1339, 2nd-half IC=+0.0976, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.120, Q3_mid=+0.134, Q4=+0.058, Q5_high_vol=+0.126

**`trend_bar_close_consistency`** (Lock IC=-0.1362, Sharpe=-1.8903)
- Admission: Train IC=+0.1956, Deflated=+0.1955, IR=0.61, Mono=0.75, p=0.0002, MaxCorr=0.91
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

**`combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=-0.0238, Sharpe=-1.8526)
- Admission: Train IC=+0.2562, Deflated=+0.2565, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.129 | 2017: +0.005 | 2018: +0.112 | 2019: +0.209 | 2020: +0.114 | 2021: +0.144 | 2022: +0.059 | 2023: +0.172 | 2024: +0.079 | 2025: +0.163 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.352 | 2016: -0.030 | 2017: +0.130 | 2018: +0.181 | 2019: +0.390 | 2020: +0.194 | 2021: +0.192 | 2022: +0.171 | 2023: +0.309 | 2024: +0.313 | 2025: +0.291 | 2026: -0.109
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.75
- Early IC=+0.1607, Recent IC=+0.1202, 1st-half IC=+0.1324, 2nd-half IC=+0.1210, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.134, Q3_mid=+0.134, Q4=+0.092, Q5_high_vol=+0.147

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0421, Sharpe=-1.8255)
- Admission: Train IC=+0.2722, Deflated=+0.2726, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.118 | 2017: +0.014 | 2018: +0.121 | 2019: +0.200 | 2020: +0.117 | 2021: +0.157 | 2022: +0.100 | 2023: +0.188 | 2024: +0.077 | 2025: +0.178 | 2026: -0.042
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.143 | 2017: -0.004 | 2018: +0.285 | 2019: +0.390 | 2020: +0.231 | 2021: +0.265 | 2022: +0.230 | 2023: +0.565 | 2024: +0.269 | 2025: +0.093 | 2026: -0.230
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.79
- Early IC=+0.1605, Recent IC=+0.1274, 1st-half IC=+0.1381, 2nd-half IC=+0.1356, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.163, Q3_mid=+0.130, Q4=+0.122, Q5_high_vol=+0.141

**`combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return`** (Lock IC=-0.0121, Sharpe=-1.7807)
- Admission: Train IC=+0.2224, Deflated=+0.2232, IR=0.72, Mono=0.78, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.145 | 2017: +0.007 | 2018: +0.124 | 2019: +0.199 | 2020: +0.113 | 2021: +0.150 | 2022: +0.093 | 2023: +0.169 | 2024: +0.059 | 2025: +0.157 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.163 | 2016: +0.100 | 2017: +0.068 | 2018: +0.216 | 2019: +0.272 | 2020: +0.119 | 2021: +0.289 | 2022: +0.175 | 2023: +0.386 | 2024: +0.127 | 2025: +0.183 | 2026: +0.006
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.67
- Early IC=+0.1615, Recent IC=+0.1080, 1st-half IC=+0.1375, 2nd-half IC=+0.1191, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.155, Q3_mid=+0.131, Q4=+0.099, Q5_high_vol=+0.128

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=-0.0192, Sharpe=-1.7777)
- Admission: Train IC=+0.2591, Deflated=+0.2590, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.073 | 2017: +0.025 | 2018: +0.078 | 2019: +0.188 | 2020: +0.134 | 2021: +0.148 | 2022: +0.123 | 2023: +0.187 | 2024: +0.105 | 2025: +0.189 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.069 | 2016: +0.182 | 2017: +0.197 | 2018: +0.207 | 2019: +0.364 | 2020: +0.165 | 2021: +0.331 | 2022: +0.263 | 2023: +0.402 | 2024: +0.247 | 2025: +0.257 | 2026: -0.059
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.11
- Early IC=+0.1327, Recent IC=+0.1470, 1st-half IC=+0.1370, 2nd-half IC=+0.1490, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.185, Q3_mid=+0.113, Q4=+0.134, Q5_high_vol=+0.159

**`close_vs_open_range`** (Lock IC=-0.0831, Sharpe=-1.7682)
- Admission: Train IC=+0.1374, Deflated=+0.1374, IR=0.59, Mono=0.73, p=0.0058, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.029 | 2017: +0.037 | 2018: +0.002 | 2019: +0.076 | 2020: +0.040 | 2021: +0.122 | 2022: +0.087 | 2023: +0.162 | 2024: +0.093 | 2025: +0.219 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.077 | 2016: +0.121 | 2017: +0.163 | 2018: -0.055 | 2019: +0.196 | 2020: +0.115 | 2021: +0.052 | 2022: +0.358 | 2023: +0.228 | 2024: +0.144 | 2025: +0.219 | 2026: -0.030
- IC CV=0.64, Neg years (linear/tail)=0/1 of 8, Half ratio=3.07, Recency ratio=4.00
- Early IC=+0.0390, Recent IC=+0.1559, 1st-half IC=+0.0485, 2nd-half IC=+0.1488, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.148, Q3_mid=+0.131, Q4=+0.065, Q5_high_vol=+0.072

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0026, Sharpe=-1.7519)
- Admission: Train IC=+0.2423, Deflated=+0.2431, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.128 | 2017: +0.017 | 2018: +0.123 | 2019: +0.204 | 2020: +0.125 | 2021: +0.129 | 2022: +0.089 | 2023: +0.151 | 2024: +0.054 | 2025: +0.119 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.247 | 2016: +0.063 | 2017: +0.107 | 2018: +0.067 | 2019: +0.351 | 2020: -0.005 | 2021: +0.199 | 2022: +0.097 | 2023: +0.392 | 2024: -0.001 | 2025: +0.286 | 2026: -0.142
- IC CV=0.33, Neg years (linear/tail)=0/2 of 8, Half ratio=0.75, Recency ratio=0.53
- Early IC=+0.1634, Recent IC=+0.0869, 1st-half IC=+0.1379, 2nd-half IC=+0.1029, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.142, Q3_mid=+0.132, Q4=+0.076, Q5_high_vol=+0.119

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0029, Sharpe=-1.7032)
- Admission: Train IC=+0.3013, Deflated=+0.3020, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.100 | 2017: +0.006 | 2018: +0.124 | 2019: +0.194 | 2020: +0.109 | 2021: +0.134 | 2022: +0.105 | 2023: +0.200 | 2024: +0.077 | 2025: +0.166 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.369 | 2016: +0.020 | 2017: +0.083 | 2018: +0.352 | 2019: +0.422 | 2020: +0.196 | 2021: +0.341 | 2022: +0.246 | 2023: +0.589 | 2024: +0.141 | 2025: +0.185 | 2026: +0.008
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.76
- Early IC=+0.1591, Recent IC=+0.1214, 1st-half IC=+0.1306, 2nd-half IC=+0.1372, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37, neg years=0)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.174, Q3_mid=+0.124, Q4=+0.126, Q5_high_vol=+0.119

**`combo_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=-0.0265, Sharpe=-1.7025)
- Admission: Train IC=+0.1980, Deflated=+0.1983, IR=0.57, Mono=0.68, p=0.0002, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.079 | 2017: +0.035 | 2018: +0.100 | 2019: +0.191 | 2020: +0.101 | 2021: +0.168 | 2022: +0.052 | 2023: +0.184 | 2024: +0.080 | 2025: +0.156 | 2026: -0.026
- Yearly Tail ICs:   2015: +0.192 | 2016: -0.029 | 2017: +0.135 | 2018: +0.306 | 2019: +0.219 | 2020: +0.033 | 2021: +0.315 | 2022: +0.109 | 2023: +0.390 | 2024: +0.083 | 2025: +0.342 | 2026: -0.165
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.81
- Early IC=+0.1455, Recent IC=+0.1176, 1st-half IC=+0.1292, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.136, Q3_mid=+0.106, Q4=+0.101, Q5_high_vol=+0.154

**`combo_rank_min__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0414, Sharpe=-1.6895)
- Admission: Train IC=+0.2231, Deflated=+0.2236, IR=0.51, Mono=0.72, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.086 | 2017: +0.045 | 2018: +0.052 | 2019: +0.178 | 2020: +0.080 | 2021: +0.171 | 2022: +0.030 | 2023: +0.165 | 2024: +0.074 | 2025: +0.148 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.032 | 2017: +0.134 | 2018: +0.192 | 2019: +0.259 | 2020: +0.225 | 2021: +0.320 | 2022: +0.124 | 2023: +0.344 | 2024: +0.033 | 2025: +0.281 | 2026: -0.183
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.94
- Early IC=+0.1156, Recent IC=+0.1085, 1st-half IC=+0.1160, 2nd-half IC=+0.1068, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.158, Q3_mid=+0.125, Q4=+0.103, Q5_high_vol=+0.091

**`combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return`** (Lock IC=-0.0208, Sharpe=-1.6549)
- Admission: Train IC=+0.2006, Deflated=+0.2008, IR=0.55, Mono=0.67, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.102 | 2017: +0.008 | 2018: +0.108 | 2019: +0.205 | 2020: +0.114 | 2021: +0.145 | 2022: +0.054 | 2023: +0.160 | 2024: +0.072 | 2025: +0.150 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.152 | 2016: -0.028 | 2017: +0.137 | 2018: +0.309 | 2019: +0.218 | 2020: +0.004 | 2021: +0.345 | 2022: +0.082 | 2023: +0.385 | 2024: +0.094 | 2025: +0.386 | 2026: -0.273
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.71
- Early IC=+0.1562, Recent IC=+0.1109, 1st-half IC=+0.1323, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.127, Q3_mid=+0.118, Q4=+0.087, Q5_high_vol=+0.156

**`combo_min__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0303, Sharpe=-1.6286)
- Admission: Train IC=+0.2037, Deflated=+0.2043, IR=0.50, Mono=0.69, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.099 | 2017: +0.052 | 2018: +0.061 | 2019: +0.188 | 2020: +0.072 | 2021: +0.157 | 2022: +0.027 | 2023: +0.182 | 2024: +0.074 | 2025: +0.151 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.096 | 2016: -0.035 | 2017: +0.137 | 2018: +0.133 | 2019: +0.376 | 2020: +0.133 | 2021: +0.197 | 2022: +0.062 | 2023: +0.453 | 2024: +0.007 | 2025: +0.236 | 2026: -0.162
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.91
- Early IC=+0.1245, Recent IC=+0.1129, 1st-half IC=+0.1145, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.159, Q3_mid=+0.123, Q4=+0.105, Q5_high_vol=+0.087

**`combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0`** (Lock IC=-0.0120, Sharpe=-1.5997)
- Admission: Train IC=+0.2718, Deflated=+0.2721, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.125 | 2017: +0.000 | 2018: +0.133 | 2019: +0.209 | 2020: +0.141 | 2021: +0.138 | 2022: +0.075 | 2023: +0.172 | 2024: +0.065 | 2025: +0.149 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.415 | 2016: -0.073 | 2017: -0.040 | 2018: +0.188 | 2019: +0.465 | 2020: +0.251 | 2021: +0.245 | 2022: +0.107 | 2023: +0.346 | 2024: +0.232 | 2025: +0.288 | 2026: -0.084
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.62
- Early IC=+0.1710, Recent IC=+0.1069, 1st-half IC=+0.1463, 2nd-half IC=+0.1189, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57, neg years=0)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.146, Q3_mid=+0.134, Q4=+0.106, Q5_high_vol=+0.149

**`combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=-0.0221, Sharpe=-1.5636)
- Admission: Train IC=+0.1784, Deflated=+0.1782, IR=0.48, Mono=0.69, p=0.0006, MaxCorr=0.91
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

**`combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=-0.0067, Sharpe=-1.4339)
- Admission: Train IC=+0.2680, Deflated=+0.2679, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.011 | 2017: +0.014 | 2018: +0.093 | 2019: +0.194 | 2020: +0.097 | 2021: +0.147 | 2022: +0.123 | 2023: +0.168 | 2024: +0.089 | 2025: +0.191 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.038 | 2017: +0.091 | 2018: -0.039 | 2019: +0.361 | 2020: +0.225 | 2021: +0.225 | 2022: +0.284 | 2023: +0.443 | 2024: +0.255 | 2025: +0.266 | 2026: -0.148
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.13, Recency ratio=0.97
- Early IC=+0.1435, Recent IC=+0.1396, 1st-half IC=+0.1318, 2nd-half IC=+0.1492, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.155, Q3_mid=+0.144, Q4=+0.150, Q5_high_vol=+0.158

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=-0.0163, Sharpe=-1.4339)
- Admission: Train IC=+0.2661, Deflated=+0.2659, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.015 | 2017: +0.018 | 2018: +0.084 | 2019: +0.206 | 2020: +0.091 | 2021: +0.139 | 2022: +0.122 | 2023: +0.166 | 2024: +0.101 | 2025: +0.183 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.265 | 2016: +0.028 | 2017: +0.079 | 2018: -0.029 | 2019: +0.359 | 2020: +0.228 | 2021: +0.224 | 2022: +0.293 | 2023: +0.440 | 2024: +0.248 | 2025: +0.275 | 2026: -0.166
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=1.16, Recency ratio=0.98
- Early IC=+0.1453, Recent IC=+0.1423, 1st-half IC=+0.1284, 2nd-half IC=+0.1487, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.34, neg years=0)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.151, Q3_mid=+0.138, Q4=+0.150, Q5_high_vol=+0.159

**`combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0527, Sharpe=-1.2264)
- Admission: Train IC=+0.2477, Deflated=+0.2477, IR=0.84, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.138 | 2016: +0.015 | 2017: +0.015 | 2018: +0.053 | 2019: +0.131 | 2020: +0.053 | 2021: +0.144 | 2022: +0.073 | 2023: +0.195 | 2024: +0.075 | 2025: +0.198 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.117 | 2017: +0.069 | 2018: +0.044 | 2019: +0.275 | 2020: +0.150 | 2021: +0.132 | 2022: +0.338 | 2023: +0.503 | 2024: +0.167 | 2025: +0.167 | 2026: -0.108
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.69, Recency ratio=1.52
- Early IC=+0.0902, Recent IC=+0.1371, 1st-half IC=+0.0830, 2nd-half IC=+0.1404, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.150, Q3_mid=+0.123, Q4=+0.095, Q5_high_vol=+0.117

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

**`combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=-0.0572, Sharpe=-1.0459)
- Admission: Train IC=+0.2567, Deflated=+0.2567, IR=0.84, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.018 | 2017: +0.016 | 2018: +0.050 | 2019: +0.132 | 2020: +0.054 | 2021: +0.144 | 2022: +0.071 | 2023: +0.196 | 2024: +0.078 | 2025: +0.206 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.178 | 2017: +0.104 | 2018: +0.021 | 2019: +0.278 | 2020: +0.168 | 2021: +0.151 | 2022: +0.380 | 2023: +0.504 | 2024: +0.190 | 2025: +0.216 | 2026: -0.202
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.74, Recency ratio=1.55
- Early IC=+0.0911, Recent IC=+0.1417, 1st-half IC=+0.0823, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58, neg years=0)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.149, Q3_mid=+0.126, Q4=+0.097, Q5_high_vol=+0.114

**`combo_sig_product__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=-0.1064, Sharpe=-1.0195)
- Admission: Train IC=+0.1336, Deflated=+0.1329, IR=0.40, Mono=0.67, p=0.0072, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.067 | 2017: +0.101 | 2018: +0.141 | 2019: +0.150 | 2020: +0.077 | 2021: +0.127 | 2022: +0.041 | 2023: +0.187 | 2024: +0.106 | 2025: +0.129 | 2026: -0.106
- Yearly Tail ICs:   2015: -0.067 | 2016: -0.040 | 2017: +0.215 | 2018: +0.174 | 2019: +0.114 | 2020: +0.022 | 2021: +0.258 | 2022: +0.033 | 2023: +0.291 | 2024: +0.114 | 2025: +0.139 | 2026: -0.097
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.81
- Early IC=+0.1454, Recent IC=+0.1175, 1st-half IC=+0.1130, 2nd-half IC=+0.1105, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.33, neg years=0)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.097, Q3_mid=+0.085, Q4=+0.105, Q5_high_vol=+0.159

**`combo_sig_product__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=-0.1070, Sharpe=-1.0195)
- Admission: Train IC=+0.1335, Deflated=+0.1328, IR=0.40, Mono=0.67, p=0.0072, MaxCorr=1.00
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
- Admission: Train IC=+0.2381, Deflated=+0.2381, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.059 | 2017: +0.015 | 2018: +0.089 | 2019: +0.143 | 2020: +0.060 | 2021: +0.152 | 2022: +0.105 | 2023: +0.182 | 2024: +0.089 | 2025: +0.156 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.302 | 2016: -0.210 | 2017: -0.059 | 2018: +0.179 | 2019: +0.396 | 2020: +0.195 | 2021: +0.115 | 2022: +0.089 | 2023: +0.274 | 2024: +0.098 | 2025: +0.133 | 2026: -0.013
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.33, Recency ratio=1.06
- Early IC=+0.1161, Recent IC=+0.1226, 1st-half IC=+0.1017, 2nd-half IC=+0.1349, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.154, Q3_mid=+0.123, Q4=+0.099, Q5_high_vol=+0.106

**`opening_drive_thrust_ratio`** (Lock IC=-0.0464, Sharpe=-0.7909)
- Admission: Train IC=+0.2628, Deflated=+0.2631, IR=0.92, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.045 | 2017: +0.030 | 2018: +0.088 | 2019: +0.188 | 2020: +0.095 | 2021: +0.133 | 2022: +0.085 | 2023: +0.199 | 2024: +0.100 | 2025: +0.166 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.041 | 2017: -0.006 | 2018: +0.191 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.198 | 2025: +0.229 | 2026: -0.077
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=0.97
- Early IC=+0.1377, Recent IC=+0.1332, 1st-half IC=+0.1162, 2nd-half IC=+0.1402, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.155, Q3_mid=+0.111, Q4=+0.134, Q5_high_vol=+0.148

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=-0.0120, Sharpe=-0.7424)
- Admission: Train IC=+0.1754, Deflated=+0.1756, IR=0.56, Mono=0.69, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.073 | 2017: +0.047 | 2018: +0.140 | 2019: +0.136 | 2020: +0.103 | 2021: +0.156 | 2022: +0.087 | 2023: +0.173 | 2024: +0.062 | 2025: +0.160 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.009 | 2017: +0.168 | 2018: +0.224 | 2019: +0.146 | 2020: +0.023 | 2021: +0.342 | 2022: +0.155 | 2023: +0.291 | 2024: +0.090 | 2025: +0.221 | 2026: +0.017
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.81
- Early IC=+0.1380, Recent IC=+0.1111, 1st-half IC=+0.1284, 2nd-half IC=+0.1168, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.32, neg years=0)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.127, Q3_mid=+0.108, Q4=+0.104, Q5_high_vol=+0.143

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=-0.0120, Sharpe=-0.7424)
- Admission: Train IC=+0.1753, Deflated=+0.1755, IR=0.56, Mono=0.69, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.072 | 2017: +0.048 | 2018: +0.141 | 2019: +0.136 | 2020: +0.103 | 2021: +0.157 | 2022: +0.086 | 2023: +0.174 | 2024: +0.063 | 2025: +0.159 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.010 | 2017: +0.168 | 2018: +0.224 | 2019: +0.146 | 2020: +0.023 | 2021: +0.342 | 2022: +0.154 | 2023: +0.291 | 2024: +0.090 | 2025: +0.221 | 2026: +0.017
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.80
- Early IC=+0.1383, Recent IC=+0.1112, 1st-half IC=+0.1284, 2nd-half IC=+0.1167, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32, neg years=0)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.128, Q3_mid=+0.108, Q4=+0.104, Q5_high_vol=+0.143

**`combo_rank_max__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0256, Sharpe=-0.7046)
- Admission: Train IC=+0.1989, Deflated=+0.1995, IR=0.46, Mono=0.70, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.128 | 2017: +0.017 | 2018: +0.117 | 2019: +0.199 | 2020: +0.067 | 2021: +0.214 | 2022: +0.026 | 2023: +0.151 | 2024: +0.038 | 2025: +0.158 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.127 | 2016: -0.148 | 2017: +0.102 | 2018: +0.310 | 2019: +0.437 | 2020: -0.057 | 2021: +0.296 | 2022: +0.078 | 2023: +0.232 | 2024: +0.064 | 2025: +0.316 | 2026: -0.033
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.62
- Early IC=+0.1596, Recent IC=+0.0994, 1st-half IC=+0.1412, 2nd-half IC=+0.0975, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.133, Q3_mid=+0.125, Q4=+0.092, Q5_high_vol=+0.125

**`combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=-0.0113, Sharpe=-0.6553)
- Admission: Train IC=+0.2168, Deflated=+0.2172, IR=0.70, Mono=0.76, p=0.0002, MaxCorr=0.90
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
- Admission: Train IC=+0.2224, Deflated=+0.2227, IR=0.61, Mono=0.75, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.078 | 2017: +0.009 | 2018: +0.090 | 2019: +0.132 | 2020: +0.107 | 2021: +0.149 | 2022: +0.102 | 2023: +0.152 | 2024: +0.065 | 2025: +0.179 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.347 | 2016: -0.080 | 2017: -0.042 | 2018: +0.192 | 2019: +0.387 | 2020: +0.184 | 2021: +0.192 | 2022: +0.051 | 2023: +0.305 | 2024: +0.148 | 2025: +0.369 | 2026: -0.010
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.10
- Early IC=+0.1107, Recent IC=+0.1221, 1st-half IC=+0.1103, 2nd-half IC=+0.1246, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64, neg years=0)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.142, Q3_mid=+0.126, Q4=+0.096, Q5_high_vol=+0.127

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0570, Sharpe=-0.3265)
- Admission: Train IC=+0.2368, Deflated=+0.2369, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.093 | 2017: +0.067 | 2018: +0.066 | 2019: +0.189 | 2020: +0.059 | 2021: +0.197 | 2022: +0.058 | 2023: +0.172 | 2024: +0.094 | 2025: +0.172 | 2026: -0.057
- Yearly Tail ICs:   2015: +0.042 | 2016: +0.036 | 2017: +0.148 | 2018: +0.180 | 2019: +0.343 | 2020: +0.115 | 2021: +0.263 | 2022: +0.121 | 2023: +0.434 | 2024: +0.181 | 2025: +0.218 | 2026: -0.058
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.04
- Early IC=+0.1278, Recent IC=+0.1328, 1st-half IC=+0.1230, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69, neg years=0)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.169, Q3_mid=+0.136, Q4=+0.119, Q5_high_vol=+0.122

**`combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=-0.0835, Sharpe=-0.1351)
- Admission: Train IC=+0.2722, Deflated=+0.2723, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.82
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
- Admission: Train IC=+0.2228, Deflated=+0.2225, IR=0.69, Mono=0.78, p=0.0000, MaxCorr=0.66
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
- Admission: Train IC=+0.1334, Deflated=+0.1332, IR=0.45, Mono=0.69, p=0.0076, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.116 | 2017: -0.053 | 2018: +0.135 | 2019: +0.036 | 2020: +0.054 | 2021: +0.124 | 2022: +0.102 | 2023: +0.107 | 2024: +0.023 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: -0.075 | 2016: +0.136 | 2017: -0.077 | 2018: +0.162 | 2019: +0.111 | 2020: +0.082 | 2021: +0.179 | 2022: +0.191 | 2023: +0.154 | 2024: +0.082 | 2025: +0.186 | 2026: +0.024
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.50
- Early IC=+0.0859, Recent IC=+0.0426, 1st-half IC=+0.0871, 2nd-half IC=+0.0822, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.057, Q3_mid=+0.011, Q4=+0.057, Q5_high_vol=+0.232

**`combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0006, Sharpe=-0.7605)
- Admission: Train IC=+0.2502, Deflated=+0.2502, IR=0.86, Mono=0.82, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.095 | 2017: +0.021 | 2018: +0.206 | 2019: +0.107 | 2020: +0.039 | 2021: +0.137 | 2022: +0.068 | 2023: +0.127 | 2024: +0.016 | 2025: +0.091 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.021 | 2017: -0.030 | 2018: +0.318 | 2019: +0.158 | 2020: +0.270 | 2021: +0.379 | 2022: +0.325 | 2023: +0.227 | 2024: +0.151 | 2025: +0.277 | 2026: +0.102
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.34
- Early IC=+0.1564, Recent IC=+0.0536, 1st-half IC=+0.1257, 2nd-half IC=+0.0798, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.082, Q3_mid=+0.053, Q4=+0.099, Q5_high_vol=+0.206

**`combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0005, Sharpe=-0.7605)
- Admission: Train IC=+0.2501, Deflated=+0.2501, IR=0.86, Mono=0.82, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.095 | 2017: +0.021 | 2018: +0.206 | 2019: +0.107 | 2020: +0.039 | 2021: +0.137 | 2022: +0.068 | 2023: +0.128 | 2024: +0.016 | 2025: +0.091 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.019 | 2017: -0.030 | 2018: +0.318 | 2019: +0.156 | 2020: +0.270 | 2021: +0.383 | 2022: +0.324 | 2023: +0.229 | 2024: +0.151 | 2025: +0.278 | 2026: +0.096
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.34
- Early IC=+0.1564, Recent IC=+0.0536, 1st-half IC=+0.1257, 2nd-half IC=+0.0799, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.082, Q3_mid=+0.053, Q4=+0.099, Q5_high_vol=+0.205

### 500ETF — `single` Median Features

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1105, Sharpe=-0.0489)
- Admission: Train IC=+0.2253, Deflated=+0.2248, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.092 | 2017: +0.221 | 2018: +0.181 | 2019: +0.125 | 2020: +0.169 | 2021: +0.085 | 2022: +0.064 | 2023: +0.064 | 2024: +0.088 | 2025: +0.125 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.093 | 2017: +0.272 | 2018: +0.375 | 2019: +0.310 | 2020: +0.203 | 2021: +0.170 | 2022: +0.224 | 2023: -0.025 | 2024: +0.194 | 2025: +0.141 | 2026: +0.143
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.70
- Early IC=+0.1532, Recent IC=+0.1067, 1st-half IC=+0.1411, 2nd-half IC=+0.0883, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.023, Q3_mid=+0.104, Q4=+0.134, Q5_high_vol=+0.164

**`combo_mean__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1096, Sharpe=-0.0489)
- Admission: Train IC=+0.2257, Deflated=+0.2252, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.092 | 2017: +0.221 | 2018: +0.182 | 2019: +0.125 | 2020: +0.169 | 2021: +0.085 | 2022: +0.065 | 2023: +0.063 | 2024: +0.088 | 2025: +0.126 | 2026: +0.110
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.091 | 2017: +0.272 | 2018: +0.375 | 2019: +0.310 | 2020: +0.213 | 2021: +0.170 | 2022: +0.224 | 2023: -0.025 | 2024: +0.194 | 2025: +0.136 | 2026: +0.123
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.63, Recency ratio=0.70
- Early IC=+0.1532, Recent IC=+0.1066, 1st-half IC=+0.1410, 2nd-half IC=+0.0883, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.023, Q3_mid=+0.104, Q4=+0.133, Q5_high_vol=+0.164

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1008, Sharpe=-0.4764)
- Admission: Train IC=+0.1726, Deflated=+0.1721, IR=0.63, Mono=0.71, p=0.0002, MaxCorr=0.83
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

**`combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0887, Sharpe=-0.7597)
- Admission: Train IC=+0.1619, Deflated=+0.1612, IR=0.43, Mono=0.68, p=0.0008, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.095 | 2017: +0.256 | 2018: +0.120 | 2019: +0.120 | 2020: +0.160 | 2021: +0.070 | 2022: +0.115 | 2023: +0.043 | 2024: +0.112 | 2025: +0.099 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.164 | 2016: +0.139 | 2017: +0.205 | 2018: +0.171 | 2019: +0.266 | 2020: +0.132 | 2021: +0.126 | 2022: +0.225 | 2023: +0.020 | 2024: +0.108 | 2025: +0.050 | 2026: -0.023
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.88
- Early IC=+0.1202, Recent IC=+0.1055, 1st-half IC=+0.1180, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.084, Q3_mid=+0.127, Q4=+0.111, Q5_high_vol=+0.160

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0832, Sharpe=-0.6640)
- Admission: Train IC=+0.2305, Deflated=+0.2316, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.038 | 2017: +0.197 | 2018: +0.197 | 2019: +0.185 | 2020: +0.169 | 2021: +0.124 | 2022: +0.053 | 2023: +0.102 | 2024: +0.112 | 2025: +0.042 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.069 | 2017: +0.244 | 2018: +0.343 | 2019: +0.427 | 2020: +0.180 | 2021: +0.177 | 2022: +0.220 | 2023: +0.183 | 2024: +0.256 | 2025: +0.102 | 2026: +0.024
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.40
- Early IC=+0.1912, Recent IC=+0.0771, 1st-half IC=+0.1640, 2nd-half IC=+0.0846, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.014, Q3_mid=+0.134, Q4=+0.134, Q5_high_vol=+0.198

**`combo_max__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.0823, Sharpe=-1.0596)
- Admission: Train IC=+0.1513, Deflated=+0.1502, IR=0.40, Mono=0.67, p=0.0022, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.074 | 2017: +0.156 | 2018: +0.165 | 2019: +0.101 | 2020: +0.116 | 2021: +0.048 | 2022: +0.117 | 2023: +0.065 | 2024: +0.108 | 2025: +0.086 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.158 | 2017: +0.147 | 2018: +0.189 | 2019: +0.194 | 2020: +0.041 | 2021: +0.197 | 2022: +0.243 | 2023: +0.144 | 2024: +0.082 | 2025: +0.048 | 2026: -0.220
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.73
- Early IC=+0.1328, Recent IC=+0.0971, 1st-half IC=+0.1110, 2nd-half IC=+0.1044, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.064, Q3_mid=+0.121, Q4=+0.089, Q5_high_vol=+0.132

**`combo_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0772, Sharpe=-0.7771)
- Admission: Train IC=+0.1612, Deflated=+0.1601, IR=0.46, Mono=0.69, p=0.0008, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.275 | 2016: +0.070 | 2017: +0.199 | 2018: +0.121 | 2019: +0.120 | 2020: +0.115 | 2021: +0.022 | 2022: +0.122 | 2023: +0.053 | 2024: +0.099 | 2025: +0.114 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.086 | 2017: +0.188 | 2018: +0.100 | 2019: +0.245 | 2020: +0.067 | 2021: +0.111 | 2022: +0.286 | 2023: +0.049 | 2024: +0.229 | 2025: +0.022 | 2026: -0.109
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=0.88
- Early IC=+0.1204, Recent IC=+0.1064, 1st-half IC=+0.0969, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.082, Q3_mid=+0.124, Q4=+0.094, Q5_high_vol=+0.125

**`combo_sig_product__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0770, Sharpe=-1.1229)
- Admission: Train IC=+0.1351, Deflated=+0.1332, IR=0.32, Mono=0.66, p=0.0070, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.033 | 2017: +0.170 | 2018: +0.017 | 2019: +0.057 | 2020: +0.092 | 2021: +0.065 | 2022: +0.072 | 2023: +0.104 | 2024: +0.166 | 2025: +0.077 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.133 | 2016: +0.017 | 2017: +0.208 | 2018: +0.083 | 2019: +0.148 | 2020: +0.233 | 2021: +0.080 | 2022: +0.059 | 2023: +0.230 | 2024: +0.221 | 2025: -0.035 | 2026: +0.049
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.92, Recency ratio=3.30
- Early IC=+0.0368, Recent IC=+0.1213, 1st-half IC=+0.0581, 2nd-half IC=+0.1118, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.109, Q3_mid=+0.060, Q4=+0.083, Q5_high_vol=+0.081

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0727, Sharpe=-0.4830)
- Admission: Train IC=+0.2243, Deflated=+0.2234, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.124 | 2017: +0.150 | 2018: +0.156 | 2019: +0.097 | 2020: +0.138 | 2021: +0.058 | 2022: +0.125 | 2023: +0.072 | 2024: +0.090 | 2025: +0.111 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.236 | 2016: +0.259 | 2017: +0.235 | 2018: +0.337 | 2019: +0.292 | 2020: +0.180 | 2021: +0.120 | 2022: +0.248 | 2023: +0.178 | 2024: +0.198 | 2025: +0.119 | 2026: +0.107
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.80
- Early IC=+0.1265, Recent IC=+0.1008, 1st-half IC=+0.1204, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.078, Q3_mid=+0.131, Q4=+0.083, Q5_high_vol=+0.158

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0695, Sharpe=-0.8397)
- Admission: Train IC=+0.1625, Deflated=+0.1614, IR=0.42, Mono=0.68, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.097 | 2021: +0.025 | 2022: +0.154 | 2023: +0.090 | 2024: +0.103 | 2025: +0.093 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.377 | 2017: +0.216 | 2018: +0.137 | 2019: +0.181 | 2020: +0.126 | 2021: +0.107 | 2022: +0.164 | 2023: +0.128 | 2024: +0.236 | 2025: -0.002 | 2026: -0.189
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=0.77
- Early IC=+0.1257, Recent IC=+0.0965, 1st-half IC=+0.0984, 2nd-half IC=+0.1146, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.081, Q3_mid=+0.131, Q4=+0.066, Q5_high_vol=+0.142

**`combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0678, Sharpe=-0.4181)
- Admission: Train IC=+0.1677, Deflated=+0.1665, IR=0.43, Mono=0.69, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.080 | 2017: +0.215 | 2018: +0.137 | 2019: +0.110 | 2020: +0.128 | 2021: +0.033 | 2022: +0.111 | 2023: +0.054 | 2024: +0.109 | 2025: +0.125 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.113 | 2017: +0.199 | 2018: +0.134 | 2019: +0.246 | 2020: +0.137 | 2021: +0.114 | 2022: +0.290 | 2023: +0.072 | 2024: +0.095 | 2025: +0.097 | 2026: -0.030
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.95
- Early IC=+0.1232, Recent IC=+0.1168, 1st-half IC=+0.1039, 2nd-half IC=+0.1096, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.082, Q3_mid=+0.124, Q4=+0.088, Q5_high_vol=+0.147

**`combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0600, Sharpe=-2.2650)
- Admission: Train IC=+0.1877, Deflated=+0.1868, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.87
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

**`combo_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0473, Sharpe=-0.2857)
- Admission: Train IC=+0.1843, Deflated=+0.1842, IR=0.61, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.038 | 2017: +0.223 | 2018: +0.175 | 2019: +0.122 | 2020: +0.154 | 2021: +0.123 | 2022: +0.078 | 2023: +0.080 | 2024: +0.124 | 2025: +0.119 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.393 | 2016: -0.058 | 2017: +0.212 | 2018: +0.134 | 2019: +0.353 | 2020: +0.075 | 2021: +0.359 | 2022: +0.190 | 2023: +0.099 | 2024: +0.281 | 2025: +0.189 | 2026: +0.066
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.82
- Early IC=+0.1483, Recent IC=+0.1212, 1st-half IC=+0.1394, 2nd-half IC=+0.1050, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.046, Q3_mid=+0.172, Q4=+0.163, Q5_high_vol=+0.144

**`combo_sig_product__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0462, Sharpe=-0.0784)
- Admission: Train IC=+0.1271, Deflated=+0.1284, IR=0.47, Mono=0.67, p=0.0100, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.197 | 2017: +0.127 | 2018: +0.149 | 2019: +0.108 | 2020: +0.102 | 2021: +0.144 | 2022: +0.102 | 2023: +0.068 | 2024: +0.148 | 2025: +0.112 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.268 | 2016: +0.261 | 2017: +0.365 | 2018: +0.261 | 2019: +0.238 | 2020: +0.219 | 2021: +0.190 | 2022: -0.155 | 2023: +0.128 | 2024: +0.130 | 2025: +0.112 | 2026: +0.100
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=1.01
- Early IC=+0.1286, Recent IC=+0.1303, 1st-half IC=+0.1216, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.073, Q3_mid=+0.083, Q4=+0.102, Q5_high_vol=+0.174

**`combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0383, Sharpe=-0.6718)
- Admission: Train IC=+0.1960, Deflated=+0.1967, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.93
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
- Admission: Train IC=+0.2348, Deflated=+0.2340, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.103 | 2017: +0.203 | 2018: +0.098 | 2019: +0.071 | 2020: +0.126 | 2021: +0.118 | 2022: +0.059 | 2023: +0.103 | 2024: +0.132 | 2025: +0.123 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.276 | 2017: +0.289 | 2018: +0.349 | 2019: +0.081 | 2020: +0.218 | 2021: +0.217 | 2022: +0.222 | 2023: -0.029 | 2024: +0.406 | 2025: +0.202 | 2026: +0.197
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=1.06, Recency ratio=1.52
- Early IC=+0.0842, Recent IC=+0.1276, 1st-half IC=+0.1016, 2nd-half IC=+0.1074, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.062, Q3_mid=+0.125, Q4=+0.087, Q5_high_vol=+0.151

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

**`combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0249, Sharpe=-1.9563)
- Admission: Train IC=+0.2226, Deflated=+0.2235, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.050 | 2017: +0.148 | 2018: +0.200 | 2019: +0.174 | 2020: +0.196 | 2021: +0.148 | 2022: +0.045 | 2023: +0.109 | 2024: +0.143 | 2025: +0.061 | 2026: +0.025
- Yearly Tail ICs:   2015: +0.250 | 2016: -0.060 | 2017: +0.165 | 2018: +0.331 | 2019: +0.319 | 2020: +0.177 | 2021: +0.054 | 2022: +0.250 | 2023: +0.143 | 2024: +0.250 | 2025: +0.171 | 2026: -0.193
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.55
- Early IC=+0.1867, Recent IC=+0.1018, 1st-half IC=+0.1728, 2nd-half IC=+0.0982, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.031, Q3_mid=+0.149, Q4=+0.134, Q5_high_vol=+0.219

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
- Admission: Train IC=+0.1783, Deflated=+0.1784, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.97
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
- Admission: Train IC=+0.1801, Deflated=+0.1802, IR=0.52, Mono=0.71, p=0.0000, MaxCorr=0.93
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
- Admission: Train IC=+0.1365, Deflated=+0.1357, IR=0.44, Mono=0.66, p=0.0060, MaxCorr=0.92
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
- Admission: Train IC=+0.2799, Deflated=+0.2799, IR=1.03, Mono=0.85, p=0.0000, MaxCorr=0.90
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

**`combo_max__first_bar_return__max_down_ret`** (Lock IC=+0.0078, Sharpe=-1.6646)
- Admission: Train IC=+0.1860, Deflated=+0.1861, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.097 | 2017: +0.254 | 2018: +0.239 | 2019: +0.142 | 2020: +0.131 | 2021: +0.079 | 2022: +0.098 | 2023: +0.041 | 2024: +0.125 | 2025: +0.098 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.006 | 2017: +0.204 | 2018: +0.408 | 2019: +0.109 | 2020: +0.233 | 2021: +0.218 | 2022: +0.164 | 2023: +0.240 | 2024: +0.240 | 2025: +0.034 | 2026: -0.250
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1907, Recent IC=+0.1113, 1st-half IC=+0.1431, 2nd-half IC=+0.1014, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.025, Q3_mid=+0.135, Q4=+0.139, Q5_high_vol=+0.172

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0077, Sharpe=-1.6646)
- Admission: Train IC=+0.1859, Deflated=+0.1860, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.098 | 2017: +0.254 | 2018: +0.239 | 2019: +0.142 | 2020: +0.131 | 2021: +0.079 | 2022: +0.098 | 2023: +0.041 | 2024: +0.124 | 2025: +0.098 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.248 | 2016: -0.006 | 2017: +0.199 | 2018: +0.408 | 2019: +0.110 | 2020: +0.233 | 2021: +0.218 | 2022: +0.164 | 2023: +0.240 | 2024: +0.241 | 2025: +0.034 | 2026: -0.250
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1905, Recent IC=+0.1110, 1st-half IC=+0.1432, 2nd-half IC=+0.1012, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.025, Q3_mid=+0.135, Q4=+0.139, Q5_high_vol=+0.172

**`combo_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0059, Sharpe=-0.5680)
- Admission: Train IC=+0.2153, Deflated=+0.2155, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.087 | 2017: +0.213 | 2018: +0.255 | 2019: +0.157 | 2020: +0.136 | 2021: +0.097 | 2022: +0.056 | 2023: +0.069 | 2024: +0.126 | 2025: +0.114 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.396 | 2016: +0.092 | 2017: +0.352 | 2018: +0.440 | 2019: +0.187 | 2020: +0.105 | 2021: +0.293 | 2022: +0.255 | 2023: +0.167 | 2024: +0.238 | 2025: +0.113 | 2026: -0.200
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.58
- Early IC=+0.2058, Recent IC=+0.1201, 1st-half IC=+0.1580, 2nd-half IC=+0.0966, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.036, Q3_mid=+0.135, Q4=+0.157, Q5_high_vol=+0.186

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0058, Sharpe=-0.5680)
- Admission: Train IC=+0.2152, Deflated=+0.2154, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=1.00
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
- Admission: Train IC=+0.2805, Deflated=+0.2807, IR=1.02, Mono=0.83, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.041 | 2017: +0.163 | 2018: +0.219 | 2019: +0.178 | 2020: +0.161 | 2021: +0.163 | 2022: +0.059 | 2023: +0.088 | 2024: +0.124 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.424 | 2016: +0.022 | 2017: +0.200 | 2018: +0.388 | 2019: +0.253 | 2020: +0.224 | 2021: +0.333 | 2022: +0.235 | 2023: +0.304 | 2024: +0.296 | 2025: +0.107 | 2026: -0.345
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.55
- Early IC=+0.1981, Recent IC=+0.1096, 1st-half IC=+0.1735, 2nd-half IC=+0.0981, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.028, Q3_mid=+0.140, Q4=+0.141, Q5_high_vol=+0.207

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0028, Sharpe=-1.6259)
- Admission: Train IC=+0.2776, Deflated=+0.2782, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.92
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
- Admission: Train IC=+0.1780, Deflated=+0.1771, IR=0.53, Mono=0.69, p=0.0006, MaxCorr=0.92
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

**`combo_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0888, Sharpe=-0.3243)
- Admission: Train IC=+0.2588, Deflated=+0.2591, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.202 | 2016: -0.002 | 2017: +0.011 | 2018: +0.028 | 2019: +0.152 | 2020: +0.059 | 2021: +0.147 | 2022: +0.074 | 2023: +0.134 | 2024: +0.068 | 2025: +0.164 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.017 | 2017: +0.132 | 2018: +0.225 | 2019: +0.351 | 2020: +0.184 | 2021: +0.230 | 2022: +0.205 | 2023: +0.307 | 2024: +0.320 | 2025: +0.173 | 2026: +0.209
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.35, Recency ratio=1.29
- Early IC=+0.0902, Recent IC=+0.1162, 1st-half IC=+0.0890, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.134, Q3_mid=+0.122, Q4=+0.108, Q5_high_vol=+0.105

**`combo_max__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.0866, Sharpe=-1.4591)
- Admission: Train IC=+0.1650, Deflated=+0.1643, IR=0.54, Mono=0.71, p=0.0014, MaxCorr=0.94
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
- Admission: Train IC=+0.2000, Deflated=+0.1994, IR=0.55, Mono=0.71, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.055 | 2017: +0.020 | 2018: +0.096 | 2019: +0.109 | 2020: +0.123 | 2021: +0.161 | 2022: +0.163 | 2023: +0.130 | 2024: +0.095 | 2025: +0.160 | 2026: +0.081
- Yearly Tail ICs:   2015: -0.058 | 2016: +0.146 | 2017: +0.095 | 2018: +0.122 | 2019: +0.310 | 2020: +0.156 | 2021: +0.350 | 2022: +0.186 | 2023: +0.090 | 2024: +0.157 | 2025: +0.052 | 2026: +0.070
- IC CV=0.21, Neg years (linear/tail)=0/0 of 8, Half ratio=1.16, Recency ratio=1.25
- Early IC=+0.1022, Recent IC=+0.1277, 1st-half IC=+0.1234, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.139, Q3_mid=+0.121, Q4=+0.159, Q5_high_vol=+0.157

**`combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0737, Sharpe=-0.6721)
- Admission: Train IC=+0.2301, Deflated=+0.2305, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.160 | 2017: +0.025 | 2018: +0.138 | 2019: +0.207 | 2020: +0.119 | 2021: +0.127 | 2022: +0.086 | 2023: +0.134 | 2024: +0.067 | 2025: +0.147 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.173 | 2016: +0.053 | 2017: +0.166 | 2018: +0.169 | 2019: +0.282 | 2020: +0.170 | 2021: +0.296 | 2022: +0.205 | 2023: +0.214 | 2024: +0.314 | 2025: +0.107 | 2026: +0.096
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.62
- Early IC=+0.1724, Recent IC=+0.1070, 1st-half IC=+0.1381, 2nd-half IC=+0.1100, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.140, Q3_mid=+0.137, Q4=+0.074, Q5_high_vol=+0.127

**`combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0719, Sharpe=-0.7386)
- Admission: Train IC=+0.2535, Deflated=+0.2534, IR=0.88, Mono=0.82, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.127 | 2017: -0.002 | 2018: +0.156 | 2019: +0.213 | 2020: +0.166 | 2021: +0.148 | 2022: +0.127 | 2023: +0.116 | 2024: +0.093 | 2025: +0.160 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.103 | 2016: +0.196 | 2017: +0.110 | 2018: +0.269 | 2019: +0.344 | 2020: +0.191 | 2021: +0.259 | 2022: +0.275 | 2023: +0.225 | 2024: +0.390 | 2025: +0.192 | 2026: +0.083
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.69
- Early IC=+0.1845, Recent IC=+0.1265, 1st-half IC=+0.1682, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.135, Q3_mid=+0.162, Q4=+0.123, Q5_high_vol=+0.172

**`combo_rank_max__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.0712, Sharpe=-1.1060)
- Admission: Train IC=+0.1832, Deflated=+0.1827, IR=0.59, Mono=0.71, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.021 | 2017: +0.033 | 2018: +0.073 | 2019: +0.158 | 2020: +0.050 | 2021: +0.127 | 2022: +0.136 | 2023: +0.121 | 2024: +0.109 | 2025: +0.108 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.067 | 2017: +0.104 | 2018: +0.076 | 2019: +0.356 | 2020: -0.022 | 2021: +0.237 | 2022: +0.053 | 2023: +0.176 | 2024: +0.309 | 2025: +0.181 | 2026: -0.043
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.25, Recency ratio=0.94
- Early IC=+0.1150, Recent IC=+0.1077, 1st-half IC=+0.1001, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.107, Q3_mid=+0.100, Q4=+0.111, Q5_high_vol=+0.119

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0712, Sharpe=-1.1060)
- Admission: Train IC=+0.1832, Deflated=+0.1827, IR=0.59, Mono=0.71, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.021 | 2017: +0.033 | 2018: +0.073 | 2019: +0.158 | 2020: +0.050 | 2021: +0.127 | 2022: +0.136 | 2023: +0.121 | 2024: +0.109 | 2025: +0.108 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.067 | 2017: +0.104 | 2018: +0.076 | 2019: +0.356 | 2020: -0.022 | 2021: +0.237 | 2022: +0.053 | 2023: +0.176 | 2024: +0.309 | 2025: +0.181 | 2026: -0.043
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.25, Recency ratio=0.94
- Early IC=+0.1150, Recent IC=+0.1077, 1st-half IC=+0.1001, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.107, Q3_mid=+0.100, Q4=+0.111, Q5_high_vol=+0.119

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0655, Sharpe=-0.2014)
- Admission: Train IC=+0.2350, Deflated=+0.2355, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.166 | 2017: +0.008 | 2018: +0.135 | 2019: +0.201 | 2020: +0.126 | 2021: +0.111 | 2022: +0.088 | 2023: +0.122 | 2024: +0.077 | 2025: +0.152 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.199 | 2016: +0.153 | 2017: +0.150 | 2018: +0.263 | 2019: +0.313 | 2020: +0.209 | 2021: +0.269 | 2022: +0.191 | 2023: +0.198 | 2024: +0.397 | 2025: +0.154 | 2026: +0.161
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.68
- Early IC=+0.1684, Recent IC=+0.1145, 1st-half IC=+0.1357, 2nd-half IC=+0.1126, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.141, Q3_mid=+0.131, Q4=+0.076, Q5_high_vol=+0.134

**`combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0623, Sharpe=-0.0060)
- Admission: Train IC=+0.1943, Deflated=+0.1942, IR=0.70, Mono=0.73, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.049 | 2017: +0.028 | 2018: +0.063 | 2019: +0.148 | 2020: +0.113 | 2021: +0.106 | 2022: +0.164 | 2023: +0.127 | 2024: +0.133 | 2025: +0.179 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.062 | 2016: -0.009 | 2017: +0.039 | 2018: +0.020 | 2019: +0.329 | 2020: +0.244 | 2021: +0.215 | 2022: +0.293 | 2023: +0.244 | 2024: +0.211 | 2025: +0.259 | 2026: -0.089
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.56
- Early IC=+0.0976, Recent IC=+0.1519, 1st-half IC=+0.1026, 2nd-half IC=+0.1538, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.130, Q3_mid=+0.145, Q4=+0.122, Q5_high_vol=+0.124

**`combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early`** (Lock IC=+0.0606, Sharpe=-1.7296)
- Admission: Train IC=+0.3020, Deflated=+0.3020, IR=0.93, Mono=0.82, p=0.0000, MaxCorr=0.85
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
- Admission: Train IC=+0.1855, Deflated=+0.1848, IR=0.63, Mono=0.70, p=0.0004, MaxCorr=0.90
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

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0574, Sharpe=-0.3480)
- Admission: Train IC=+0.3874, Deflated=+0.3880, IR=1.15, Mono=0.88, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.110 | 2017: -0.016 | 2018: +0.189 | 2019: +0.247 | 2020: +0.159 | 2021: +0.152 | 2022: +0.096 | 2023: +0.186 | 2024: +0.121 | 2025: +0.169 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.179 | 2016: +0.065 | 2017: +0.067 | 2018: +0.408 | 2019: +0.581 | 2020: +0.355 | 2021: +0.416 | 2022: +0.235 | 2023: +0.457 | 2024: +0.364 | 2025: +0.264 | 2026: +0.114
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.66
- Early IC=+0.2182, Recent IC=+0.1447, 1st-half IC=+0.1763, 2nd-half IC=+0.1459, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.178, Q3_mid=+0.136, Q4=+0.182, Q5_high_vol=+0.178

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0567, Sharpe=-0.2824)
- Admission: Train IC=+0.2873, Deflated=+0.2878, IR=0.85, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.111 | 2017: +0.019 | 2018: +0.092 | 2019: +0.236 | 2020: +0.120 | 2021: +0.123 | 2022: +0.094 | 2023: +0.163 | 2024: +0.069 | 2025: +0.212 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.262 | 2016: +0.012 | 2017: +0.044 | 2018: +0.244 | 2019: +0.488 | 2020: +0.226 | 2021: +0.204 | 2022: +0.100 | 2023: +0.356 | 2024: +0.285 | 2025: +0.437 | 2026: +0.184
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.86
- Early IC=+0.1639, Recent IC=+0.1405, 1st-half IC=+0.1358, 2nd-half IC=+0.1376, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.156, Q3_mid=+0.141, Q4=+0.109, Q5_high_vol=+0.156

**`combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0556, Sharpe=-1.3831)
- Admission: Train IC=+0.1741, Deflated=+0.1738, IR=0.62, Mono=0.71, p=0.0008, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.012 | 2017: +0.028 | 2018: +0.057 | 2019: +0.140 | 2020: +0.067 | 2021: +0.101 | 2022: +0.167 | 2023: +0.122 | 2024: +0.127 | 2025: +0.168 | 2026: +0.070
- Yearly Tail ICs:   2015: +0.197 | 2016: -0.000 | 2017: +0.041 | 2018: +0.020 | 2019: +0.275 | 2020: +0.116 | 2021: +0.128 | 2022: +0.257 | 2023: +0.191 | 2024: +0.228 | 2025: +0.276 | 2026: -0.207
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.77, Recency ratio=1.60
- Early IC=+0.0925, Recent IC=+0.1478, 1st-half IC=+0.0874, 2nd-half IC=+0.1545, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.127, Q3_mid=+0.142, Q4=+0.109, Q5_high_vol=+0.109

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0545, Sharpe=-1.0195)
- Admission: Train IC=+0.2337, Deflated=+0.2336, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.062 | 2017: +0.025 | 2018: +0.083 | 2019: +0.156 | 2020: +0.108 | 2021: +0.161 | 2022: +0.134 | 2023: +0.133 | 2024: +0.115 | 2025: +0.195 | 2026: +0.054
- Yearly Tail ICs:   2015: -0.047 | 2016: +0.154 | 2017: +0.143 | 2018: +0.089 | 2019: +0.405 | 2020: +0.118 | 2021: +0.196 | 2022: +0.227 | 2023: +0.278 | 2024: +0.389 | 2025: +0.217 | 2026: -0.043
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.30
- Early IC=+0.1191, Recent IC=+0.1548, 1st-half IC=+0.1251, 2nd-half IC=+0.1522, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.145, Q3_mid=+0.139, Q4=+0.145, Q5_high_vol=+0.157

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0540, Sharpe=-0.4595)
- Admission: Train IC=+0.2657, Deflated=+0.2660, IR=0.75, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.134 | 2017: +0.033 | 2018: +0.078 | 2019: +0.199 | 2020: +0.145 | 2021: +0.148 | 2022: +0.128 | 2023: +0.153 | 2024: +0.089 | 2025: +0.171 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.146 | 2016: +0.209 | 2017: +0.135 | 2018: +0.295 | 2019: +0.383 | 2020: +0.169 | 2021: +0.423 | 2022: +0.329 | 2023: +0.371 | 2024: +0.287 | 2025: +0.045 | 2026: +0.135
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.94
- Early IC=+0.1385, Recent IC=+0.1300, 1st-half IC=+0.1467, 2nd-half IC=+0.1351, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.169, Q3_mid=+0.150, Q4=+0.112, Q5_high_vol=+0.134

**`combo_diff__bar_body_rng_0__demark_setup_reversal_early`** (Lock IC=+0.0528, Sharpe=-1.7296)
- Admission: Train IC=+0.3003, Deflated=+0.3003, IR=0.91, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.073 | 2017: -0.015 | 2018: +0.130 | 2019: +0.215 | 2020: +0.139 | 2021: +0.152 | 2022: +0.117 | 2023: +0.146 | 2024: +0.065 | 2025: +0.190 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.236 | 2016: +0.039 | 2017: +0.034 | 2018: +0.189 | 2019: +0.497 | 2020: +0.379 | 2021: +0.318 | 2022: +0.204 | 2023: +0.305 | 2024: +0.205 | 2025: +0.399 | 2026: -0.367
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.74
- Early IC=+0.1728, Recent IC=+0.1277, 1st-half IC=+0.1518, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.146, Q3_mid=+0.164, Q4=+0.127, Q5_high_vol=+0.156

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0510, Sharpe=-0.4248)
- Admission: Train IC=+0.3045, Deflated=+0.3047, IR=0.86, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.151 | 2017: +0.006 | 2018: +0.158 | 2019: +0.211 | 2020: +0.164 | 2021: +0.173 | 2022: +0.125 | 2023: +0.140 | 2024: +0.067 | 2025: +0.180 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.029 | 2016: +0.196 | 2017: +0.052 | 2018: +0.310 | 2019: +0.337 | 2020: +0.239 | 2021: +0.349 | 2022: +0.261 | 2023: +0.291 | 2024: +0.396 | 2025: +0.223 | 2026: -0.087
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.67
- Early IC=+0.1844, Recent IC=+0.1235, 1st-half IC=+0.1708, 2nd-half IC=+0.1326, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.147, Q3_mid=+0.159, Q4=+0.141, Q5_high_vol=+0.169

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

**`bar_body_rng_0`** (Lock IC=+0.0207, Sharpe=-0.3858)
- Admission: Train IC=+0.2273, Deflated=+0.2279, IR=0.58, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.151 | 2017: -0.020 | 2018: +0.141 | 2019: +0.203 | 2020: +0.134 | 2021: +0.136 | 2022: +0.062 | 2023: +0.141 | 2024: +0.047 | 2025: +0.158 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.308 | 2016: -0.108 | 2017: -0.022 | 2018: +0.220 | 2019: +0.459 | 2020: +0.173 | 2021: +0.164 | 2022: +0.076 | 2023: +0.316 | 2024: +0.127 | 2025: +0.347 | 2026: +0.011
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.60
- Early IC=+0.1722, Recent IC=+0.1027, 1st-half IC=+0.1426, 2nd-half IC=+0.1038, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.131, Q3_mid=+0.131, Q4=+0.081, Q5_high_vol=+0.128

**`combo_rank_min__first_bar_return__volatility_expansion_trend_vector`** (Lock IC=+0.0154, Sharpe=-0.1510)
- Admission: Train IC=+0.2066, Deflated=+0.2073, IR=0.53, Mono=0.74, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.071 | 2017: +0.020 | 2018: +0.061 | 2019: +0.163 | 2020: +0.054 | 2021: +0.114 | 2022: +0.073 | 2023: +0.177 | 2024: +0.075 | 2025: +0.150 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.015 | 2016: +0.184 | 2017: +0.120 | 2018: +0.086 | 2019: +0.253 | 2020: +0.119 | 2021: +0.071 | 2022: +0.235 | 2023: +0.411 | 2024: +0.190 | 2025: +0.132 | 2026: +0.044
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.58, Recency ratio=1.13
- Early IC=+0.1039, Recent IC=+0.1172, 1st-half IC=+0.0797, 2nd-half IC=+0.1257, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.127, Q3_mid=+0.105, Q4=+0.061, Q5_high_vol=+0.111

**`combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0120, Sharpe=-0.2721)
- Admission: Train IC=+0.1789, Deflated=+0.1799, IR=0.56, Mono=0.74, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.127 | 2017: +0.020 | 2018: +0.127 | 2019: +0.201 | 2020: +0.099 | 2021: +0.135 | 2022: +0.083 | 2023: +0.148 | 2024: +0.057 | 2025: +0.111 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.357 | 2016: -0.023 | 2017: +0.141 | 2018: +0.172 | 2019: +0.269 | 2020: -0.019 | 2021: +0.222 | 2022: +0.216 | 2023: +0.391 | 2024: +0.043 | 2025: +0.136 | 2026: +0.136
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.51
- Early IC=+0.1640, Recent IC=+0.0841, 1st-half IC=+0.1302, 2nd-half IC=+0.1006, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.139, Q3_mid=+0.116, Q4=+0.077, Q5_high_vol=+0.121

**`combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0085, Sharpe=-0.0010)
- Admission: Train IC=+0.2503, Deflated=+0.2510, IR=0.76, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.113 | 2017: +0.014 | 2018: +0.129 | 2019: +0.189 | 2020: +0.105 | 2021: +0.131 | 2022: +0.109 | 2023: +0.183 | 2024: +0.085 | 2025: +0.172 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.352 | 2016: -0.084 | 2017: +0.123 | 2018: +0.234 | 2019: +0.371 | 2020: +0.149 | 2021: +0.286 | 2022: +0.172 | 2023: +0.526 | 2024: +0.169 | 2025: +0.276 | 2026: +0.262
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=0.81
- Early IC=+0.1591, Recent IC=+0.1283, 1st-half IC=+0.1293, 2nd-half IC=+0.1382, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.162, Q3_mid=+0.131, Q4=+0.121, Q5_high_vol=+0.124

**`combo_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0069, Sharpe=-0.4785)
- Admission: Train IC=+0.2695, Deflated=+0.2701, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.121 | 2017: +0.012 | 2018: +0.132 | 2019: +0.183 | 2020: +0.129 | 2021: +0.129 | 2022: +0.091 | 2023: +0.152 | 2024: +0.057 | 2025: +0.131 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.449 | 2016: -0.281 | 2017: +0.151 | 2018: +0.295 | 2019: +0.360 | 2020: +0.153 | 2021: +0.226 | 2022: +0.116 | 2023: +0.293 | 2024: +0.124 | 2025: +0.285 | 2026: +0.049
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.60
- Early IC=+0.1578, Recent IC=+0.0940, 1st-half IC=+0.1356, 2nd-half IC=+0.1106, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.147, Q3_mid=+0.120, Q4=+0.117, Q5_high_vol=+0.124

**`combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0056, Sharpe=-1.4645)
- Admission: Train IC=+0.2885, Deflated=+0.2887, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.117 | 2017: -0.001 | 2018: +0.135 | 2019: +0.191 | 2020: +0.125 | 2021: +0.145 | 2022: +0.100 | 2023: +0.159 | 2024: +0.057 | 2025: +0.142 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.317 | 2016: -0.292 | 2017: +0.065 | 2018: +0.167 | 2019: +0.466 | 2020: +0.235 | 2021: +0.344 | 2022: +0.034 | 2023: +0.373 | 2024: +0.017 | 2025: +0.205 | 2026: -0.092
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.61
- Early IC=+0.1631, Recent IC=+0.0997, 1st-half IC=+0.1417, 2nd-half IC=+0.1182, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.149, Q3_mid=+0.126, Q4=+0.123, Q5_high_vol=+0.133

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0018, Sharpe=-2.0212)
- Admission: Train IC=+0.2583, Deflated=+0.2583, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.89
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
- Admission: Train IC=+0.2637, Deflated=+0.2645, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.073 | 2017: -0.029 | 2018: +0.185 | 2019: +0.143 | 2020: +0.035 | 2021: +0.133 | 2022: +0.044 | 2023: +0.155 | 2024: +0.045 | 2025: +0.097 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.112 | 2017: -0.040 | 2018: +0.347 | 2019: +0.172 | 2020: +0.139 | 2021: +0.406 | 2022: +0.237 | 2023: +0.269 | 2024: +0.254 | 2025: +0.078 | 2026: +0.239
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.45
- Early IC=+0.1622, Recent IC=+0.0722, 1st-half IC=+0.1242, 2nd-half IC=+0.0915, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.100, Q3_mid=+0.073, Q4=+0.090, Q5_high_vol=+0.210

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0062, Sharpe=+0.4946)
- Admission: Train IC=+0.2816, Deflated=+0.2826, IR=0.62, Mono=0.73, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.42
- Early IC=+0.1725, Recent IC=+0.0719, 1st-half IC=+0.1310, 2nd-half IC=+0.0915, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.098, Q3_mid=+0.085, Q4=+0.094, Q5_high_vol=+0.209

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
- Admission: Train IC=+0.2228, Deflated=+0.2222, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.98
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

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0706, Sharpe=+0.8062)
- Admission: Train IC=+0.2557, Deflated=+0.2548, IR=0.78, Mono=0.82, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.089 | 2017: +0.240 | 2018: +0.181 | 2019: +0.128 | 2020: +0.173 | 2021: +0.101 | 2022: +0.078 | 2023: +0.079 | 2024: +0.136 | 2025: +0.117 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.137 | 2017: +0.231 | 2018: +0.306 | 2019: +0.416 | 2020: +0.148 | 2021: +0.222 | 2022: +0.298 | 2023: +0.152 | 2024: +0.240 | 2025: +0.097 | 2026: +0.049
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.82
- Early IC=+0.1546, Recent IC=+0.1262, 1st-half IC=+0.1479, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.070, Q3_mid=+0.147, Q4=+0.137, Q5_high_vol=+0.190

**`combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0527, Sharpe=+0.7989)
- Admission: Train IC=+0.1637, Deflated=+0.1645, IR=0.45, Mono=0.68, p=0.0006, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.055 | 2017: +0.163 | 2018: +0.182 | 2019: +0.149 | 2020: +0.193 | 2021: +0.147 | 2022: +0.007 | 2023: +0.106 | 2024: +0.095 | 2025: +0.069 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.227 | 2016: +0.233 | 2017: +0.126 | 2018: +0.436 | 2019: +0.149 | 2020: +0.106 | 2021: +0.404 | 2022: +0.157 | 2023: -0.125 | 2024: +0.007 | 2025: +0.074 | 2026: +0.163
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.46, Recency ratio=0.50
- Early IC=+0.1654, Recent IC=+0.0819, 1st-half IC=+0.1656, 2nd-half IC=+0.0766, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.017, Q3_mid=+0.107, Q4=+0.092, Q5_high_vol=+0.232

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1061, Sharpe=+0.5671)
- Admission: Train IC=+0.2165, Deflated=+0.2161, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.127 | 2017: +0.217 | 2018: +0.214 | 2019: +0.132 | 2020: +0.171 | 2021: +0.103 | 2022: +0.083 | 2023: +0.071 | 2024: +0.095 | 2025: +0.116 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.145 | 2017: +0.270 | 2018: +0.403 | 2019: +0.277 | 2020: +0.221 | 2021: +0.173 | 2022: +0.172 | 2023: -0.031 | 2024: +0.137 | 2025: +0.133 | 2026: +0.143
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.61, Recency ratio=0.61
- Early IC=+0.1731, Recent IC=+0.1058, 1st-half IC=+0.1558, 2nd-half IC=+0.0953, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.024, Q3_mid=+0.103, Q4=+0.141, Q5_high_vol=+0.193

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1067, Sharpe=+0.5671)
- Admission: Train IC=+0.2160, Deflated=+0.2157, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=1.00
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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0369, Sharpe=+0.4718)
- Admission: Train IC=+0.2499, Deflated=+0.2486, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.086 | 2017: +0.208 | 2018: +0.120 | 2019: +0.067 | 2020: +0.101 | 2021: +0.084 | 2022: +0.068 | 2023: +0.109 | 2024: +0.120 | 2025: +0.126 | 2026: +0.037
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.229 | 2017: +0.381 | 2018: +0.355 | 2019: +0.126 | 2020: +0.242 | 2021: +0.147 | 2022: +0.232 | 2023: +0.140 | 2024: +0.385 | 2025: +0.176 | 2026: +0.248
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=1.16, Recency ratio=1.31
- Early IC=+0.0938, Recent IC=+0.1232, 1st-half IC=+0.0967, 2nd-half IC=+0.1126, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.49)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.065, Q3_mid=+0.111, Q4=+0.110, Q5_high_vol=+0.146

**`combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1323, Sharpe=+0.4708)
- Admission: Train IC=+0.1266, Deflated=+0.1261, IR=0.43, Mono=0.70, p=0.0104, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.135 | 2017: +0.226 | 2018: +0.160 | 2019: +0.120 | 2020: +0.189 | 2021: +0.091 | 2022: +0.120 | 2023: +0.073 | 2024: +0.116 | 2025: +0.080 | 2026: +0.132
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.389 | 2017: +0.114 | 2018: +0.137 | 2019: +0.260 | 2020: +0.134 | 2021: +0.159 | 2022: +0.053 | 2023: -0.137 | 2024: +0.148 | 2025: +0.055 | 2026: +0.143
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.70
- Early IC=+0.1398, Recent IC=+0.0980, 1st-half IC=+0.1400, 2nd-half IC=+0.1094, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.078, Q3_mid=+0.132, Q4=+0.129, Q5_high_vol=+0.183

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0755, Sharpe=+0.4554)
- Admission: Train IC=+0.2277, Deflated=+0.2280, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.58
- Early IC=+0.1857, Recent IC=+0.1081, 1st-half IC=+0.1517, 2nd-half IC=+0.0849, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.007, Q3_mid=+0.085, Q4=+0.146, Q5_high_vol=+0.198

**`combo_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0024, Sharpe=+0.4072)
- Admission: Train IC=+0.2006, Deflated=+0.1996, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.085 | 2017: +0.189 | 2018: +0.163 | 2019: +0.113 | 2020: +0.068 | 2021: +0.057 | 2022: +0.055 | 2023: +0.080 | 2024: +0.142 | 2025: +0.144 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.183 | 2017: +0.309 | 2018: +0.316 | 2019: +0.120 | 2020: +0.071 | 2021: +0.229 | 2022: +0.220 | 2023: +0.141 | 2024: +0.217 | 2025: +0.224 | 2026: +0.210
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.04
- Early IC=+0.1378, Recent IC=+0.1427, 1st-half IC=+0.0996, 2nd-half IC=+0.1090, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.031, Q3_mid=+0.105, Q4=+0.109, Q5_high_vol=+0.145

**`combo_min__close_vs_open_range__first_bar_return`** (Lock IC=+0.0019, Sharpe=+0.4072)
- Admission: Train IC=+0.2002, Deflated=+0.1992, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.085 | 2017: +0.189 | 2018: +0.163 | 2019: +0.112 | 2020: +0.068 | 2021: +0.057 | 2022: +0.055 | 2023: +0.080 | 2024: +0.142 | 2025: +0.144 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.185 | 2017: +0.309 | 2018: +0.315 | 2019: +0.117 | 2020: +0.073 | 2021: +0.227 | 2022: +0.220 | 2023: +0.141 | 2024: +0.217 | 2025: +0.223 | 2026: +0.202
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.04
- Early IC=+0.1376, Recent IC=+0.1428, 1st-half IC=+0.0997, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.031, Q3_mid=+0.105, Q4=+0.109, Q5_high_vol=+0.145

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0571, Sharpe=+0.3372)
- Admission: Train IC=+0.2573, Deflated=+0.2569, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.089 | 2017: +0.215 | 2018: +0.189 | 2019: +0.136 | 2020: +0.152 | 2021: +0.150 | 2022: +0.044 | 2023: +0.100 | 2024: +0.142 | 2025: +0.113 | 2026: +0.057
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.220 | 2017: +0.350 | 2018: +0.463 | 2019: +0.292 | 2020: +0.246 | 2021: +0.237 | 2022: +0.207 | 2023: +0.180 | 2024: +0.355 | 2025: +0.033 | 2026: +0.277
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.79
- Early IC=+0.1623, Recent IC=+0.1276, 1st-half IC=+0.1579, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.098, Q2=+0.042, Q3_mid=+0.150, Q4=+0.129, Q5_high_vol=+0.210

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0820, Sharpe=+0.3115)
- Admission: Train IC=+0.2351, Deflated=+0.2355, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.317 | 2016: +0.085 | 2017: +0.219 | 2018: +0.201 | 2019: +0.174 | 2020: +0.137 | 2021: +0.085 | 2022: +0.052 | 2023: +0.081 | 2024: +0.088 | 2025: +0.122 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.112 | 2017: +0.149 | 2018: +0.458 | 2019: +0.312 | 2020: +0.269 | 2021: +0.035 | 2022: +0.134 | 2023: +0.143 | 2024: +0.266 | 2025: +0.110 | 2026: +0.094
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.56
- Early IC=+0.1878, Recent IC=+0.1052, 1st-half IC=+0.1493, 2nd-half IC=+0.0847, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.008, Q3_mid=+0.080, Q4=+0.144, Q5_high_vol=+0.189

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.0739, Sharpe=+0.2096)
- Admission: Train IC=+0.2286, Deflated=+0.2276, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.085 | 2017: +0.239 | 2018: +0.186 | 2019: +0.129 | 2020: +0.169 | 2021: +0.092 | 2022: +0.080 | 2023: +0.075 | 2024: +0.139 | 2025: +0.106 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.150 | 2017: +0.255 | 2018: +0.250 | 2019: +0.385 | 2020: +0.081 | 2021: +0.129 | 2022: +0.298 | 2023: +0.101 | 2024: +0.244 | 2025: +0.100 | 2026: +0.091
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.78
- Early IC=+0.1576, Recent IC=+0.1224, 1st-half IC=+0.1469, 2nd-half IC=+0.1094, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.093, Q2=+0.075, Q3_mid=+0.149, Q4=+0.130, Q5_high_vol=+0.188

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0441, Sharpe=+0.1744)
- Admission: Train IC=+0.2670, Deflated=+0.2661, IR=0.83, Mono=0.78, p=0.0000, MaxCorr=0.69
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.094 | 2017: +0.222 | 2018: +0.187 | 2019: +0.124 | 2020: +0.134 | 2021: +0.150 | 2022: +0.045 | 2023: +0.111 | 2024: +0.146 | 2025: +0.122 | 2026: +0.044
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.231 | 2017: +0.319 | 2018: +0.440 | 2019: +0.324 | 2020: +0.263 | 2021: +0.262 | 2022: +0.226 | 2023: +0.202 | 2024: +0.300 | 2025: +0.085 | 2026: +0.240
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.86
- Early IC=+0.1551, Recent IC=+0.1341, 1st-half IC=+0.1482, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.048, Q3_mid=+0.141, Q4=+0.127, Q5_high_vol=+0.200

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
- Admission: Train IC=+0.3231, Deflated=+0.3239, IR=1.01, Mono=0.83, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.124 | 2017: -0.001 | 2018: +0.125 | 2019: +0.213 | 2020: +0.067 | 2021: +0.189 | 2022: +0.060 | 2023: +0.148 | 2024: +0.120 | 2025: +0.140 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.063 | 2017: +0.103 | 2018: +0.280 | 2019: +0.527 | 2020: +0.305 | 2021: +0.389 | 2022: +0.110 | 2023: +0.381 | 2024: +0.281 | 2025: +0.148 | 2026: +0.325
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.78
- Early IC=+0.1683, Recent IC=+0.1321, 1st-half IC=+0.1477, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.158, Q3_mid=+0.135, Q4=+0.154, Q5_high_vol=+0.153

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1324, Sharpe=+2.7212)
- Admission: Train IC=+0.3107, Deflated=+0.3113, IR=1.02, Mono=0.82, p=0.0000, MaxCorr=0.97
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

**`combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1205, Sharpe=+2.3935)
- Admission: Train IC=+0.3187, Deflated=+0.3195, IR=0.99, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.157 | 2016: +0.125 | 2017: +0.004 | 2018: +0.128 | 2019: +0.229 | 2020: +0.056 | 2021: +0.174 | 2022: +0.046 | 2023: +0.146 | 2024: +0.129 | 2025: +0.147 | 2026: +0.120
- Yearly Tail ICs:   2015: -0.016 | 2016: +0.050 | 2017: +0.133 | 2018: +0.239 | 2019: +0.604 | 2020: +0.319 | 2021: +0.338 | 2022: +0.199 | 2023: +0.398 | 2024: +0.275 | 2025: +0.167 | 2026: +0.295
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.77
- Early IC=+0.1786, Recent IC=+0.1380, 1st-half IC=+0.1472, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.157, Q3_mid=+0.135, Q4=+0.153, Q5_high_vol=+0.148

**`combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.1716, Sharpe=+2.0307)
- Admission: Train IC=+0.1815, Deflated=+0.1809, IR=0.47, Mono=0.68, p=0.0004, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.046 | 2017: -0.014 | 2018: +0.102 | 2019: +0.172 | 2020: +0.107 | 2021: +0.146 | 2022: +0.166 | 2023: +0.109 | 2024: +0.100 | 2025: +0.123 | 2026: +0.173
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.207 | 2017: +0.032 | 2018: +0.220 | 2019: +0.240 | 2020: +0.156 | 2021: +0.246 | 2022: +0.184 | 2023: -0.050 | 2024: +0.213 | 2025: +0.015 | 2026: +0.332
- IC CV=0.23, Neg years (linear/tail)=0/1 of 8, Half ratio=0.94, Recency ratio=0.80
- Early IC=+0.1372, Recent IC=+0.1093, 1st-half IC=+0.1392, 2nd-half IC=+0.1303, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.119, Q3_mid=+0.115, Q4=+0.164, Q5_high_vol=+0.147

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1495, Sharpe=+1.8753)
- Admission: Train IC=+0.3014, Deflated=+0.3022, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.056 | 2017: -0.039 | 2018: +0.098 | 2019: +0.257 | 2020: +0.142 | 2021: +0.107 | 2022: +0.043 | 2023: +0.124 | 2024: +0.106 | 2025: +0.151 | 2026: +0.150
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.002 | 2017: +0.015 | 2018: +0.338 | 2019: +0.526 | 2020: +0.302 | 2021: +0.233 | 2022: +0.167 | 2023: +0.243 | 2024: +0.452 | 2025: +0.151 | 2026: +0.443
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.72
- Early IC=+0.1776, Recent IC=+0.1286, 1st-half IC=+0.1410, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.137, Q3_mid=+0.145, Q4=+0.104, Q5_high_vol=+0.137

**`combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`** (Lock IC=+0.1724, Sharpe=+1.6445)
- Admission: Train IC=+0.1881, Deflated=+0.1876, IR=0.45, Mono=0.66, p=0.0004, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.036 | 2017: -0.021 | 2018: +0.094 | 2019: +0.182 | 2020: +0.115 | 2021: +0.130 | 2022: +0.161 | 2023: +0.094 | 2024: +0.104 | 2025: +0.113 | 2026: +0.172
- Yearly Tail ICs:   2015: -0.048 | 2016: +0.231 | 2017: +0.019 | 2018: +0.255 | 2019: +0.231 | 2020: +0.183 | 2021: +0.296 | 2022: +0.167 | 2023: -0.025 | 2024: +0.206 | 2025: +0.005 | 2026: +0.355
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=0.79
- Early IC=+0.1380, Recent IC=+0.1085, 1st-half IC=+0.1357, 2nd-half IC=+0.1288, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.121, Q3_mid=+0.112, Q4=+0.157, Q5_high_vol=+0.146

**`combo_mean__first_bar_return__limit_down_proximity_early`** (Lock IC=+0.1120, Sharpe=+1.5982)
- Admission: Train IC=+0.2564, Deflated=+0.2564, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.071 | 2017: -0.001 | 2018: +0.158 | 2019: +0.207 | 2020: +0.121 | 2021: +0.137 | 2022: +0.095 | 2023: +0.136 | 2024: +0.066 | 2025: +0.154 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.050 | 2017: +0.130 | 2018: +0.338 | 2019: +0.410 | 2020: +0.077 | 2021: +0.369 | 2022: +0.109 | 2023: +0.166 | 2024: +0.380 | 2025: +0.228 | 2026: +0.260
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.60
- Early IC=+0.1826, Recent IC=+0.1100, 1st-half IC=+0.1475, 2nd-half IC=+0.1152, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.130, Q3_mid=+0.138, Q4=+0.094, Q5_high_vol=+0.164

**`combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1120, Sharpe=+1.5982)
- Admission: Train IC=+0.2564, Deflated=+0.2564, IR=0.73, Mono=0.79, p=0.0000, MaxCorr=1.00
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

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0980, Sharpe=+1.3754)
- Admission: Train IC=+0.1643, Deflated=+0.1655, IR=0.40, Mono=0.65, p=0.0016, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.121 | 2016: -0.001 | 2017: -0.037 | 2018: +0.022 | 2019: +0.177 | 2020: +0.075 | 2021: +0.090 | 2022: +0.101 | 2023: +0.138 | 2024: +0.156 | 2025: +0.067 | 2026: +0.098
- Yearly Tail ICs:   2015: -0.080 | 2016: -0.128 | 2017: -0.014 | 2018: +0.032 | 2019: +0.411 | 2020: +0.047 | 2021: +0.189 | 2022: +0.144 | 2023: +0.238 | 2024: +0.324 | 2025: +0.004 | 2026: +0.358
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.21, Recency ratio=1.12
- Early IC=+0.0991, Recent IC=+0.1112, 1st-half IC=+0.0961, 2nd-half IC=+0.1164, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.068, Q3_mid=+0.097, Q4=+0.132, Q5_high_vol=+0.112

**`combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1654, Sharpe=+1.0917)
- Admission: Train IC=+0.2556, Deflated=+0.2552, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.55
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.110 | 2017: -0.072 | 2018: +0.110 | 2019: +0.110 | 2020: +0.090 | 2021: +0.046 | 2022: +0.171 | 2023: +0.132 | 2024: +0.102 | 2025: +0.108 | 2026: +0.165
- Yearly Tail ICs:   2015: +0.139 | 2016: +0.157 | 2017: +0.160 | 2018: +0.362 | 2019: +0.320 | 2020: +0.352 | 2021: +0.218 | 2022: +0.396 | 2023: +0.073 | 2024: +0.119 | 2025: +0.186 | 2026: +0.312
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=0.96
- Early IC=+0.1098, Recent IC=+0.1049, 1st-half IC=+0.0954, 2nd-half IC=+0.1322, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.128, Q3_mid=+0.117, Q4=+0.150, Q5_high_vol=+0.095

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.0961, Sharpe=+1.0753)
- Admission: Train IC=+0.2412, Deflated=+0.2410, IR=0.83, Mono=0.78, p=0.0000, MaxCorr=0.98
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
- Admission: Train IC=+0.2335, Deflated=+0.2340, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.88
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

**`combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1209, Sharpe=+0.7808)
- Admission: Train IC=+0.2412, Deflated=+0.2410, IR=0.62, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.044 | 2017: -0.054 | 2018: +0.073 | 2019: +0.131 | 2020: +0.100 | 2021: +0.042 | 2022: +0.180 | 2023: +0.112 | 2024: +0.081 | 2025: +0.126 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.166 | 2017: +0.014 | 2018: +0.359 | 2019: +0.259 | 2020: +0.391 | 2021: +0.172 | 2022: +0.463 | 2023: +0.068 | 2024: +0.023 | 2025: +0.066 | 2026: +0.302
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.50, Recency ratio=1.02
- Early IC=+0.1034, Recent IC=+0.1059, 1st-half IC=+0.0883, 2nd-half IC=+0.1320, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.117, Q3_mid=+0.098, Q4=+0.121, Q5_high_vol=+0.140

**`combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1170, Sharpe=+0.7340)
- Admission: Train IC=+0.3252, Deflated=+0.3256, IR=0.95, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.127 | 2017: -0.022 | 2018: +0.145 | 2019: +0.235 | 2020: +0.164 | 2021: +0.126 | 2022: +0.105 | 2023: +0.124 | 2024: +0.100 | 2025: +0.147 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.135 | 2017: +0.100 | 2018: +0.338 | 2019: +0.432 | 2020: +0.273 | 2021: +0.287 | 2022: +0.208 | 2023: +0.242 | 2024: +0.476 | 2025: +0.259 | 2026: +0.173
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.65
- Early IC=+0.1904, Recent IC=+0.1234, 1st-half IC=+0.1633, 2nd-half IC=+0.1222, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.128, Q3_mid=+0.160, Q4=+0.114, Q5_high_vol=+0.155

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1343, Sharpe=+0.7340)
- Admission: Train IC=+0.3076, Deflated=+0.3077, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.120 | 2017: -0.024 | 2018: +0.163 | 2019: +0.230 | 2020: +0.158 | 2021: +0.146 | 2022: +0.107 | 2023: +0.116 | 2024: +0.081 | 2025: +0.143 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.162 | 2017: +0.100 | 2018: +0.372 | 2019: +0.462 | 2020: +0.230 | 2021: +0.299 | 2022: +0.180 | 2023: +0.157 | 2024: +0.447 | 2025: +0.232 | 2026: +0.173
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.57
- Early IC=+0.1961, Recent IC=+0.1125, 1st-half IC=+0.1690, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.124, Q3_mid=+0.157, Q4=+0.122, Q5_high_vol=+0.161

**`combo_mean__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1135, Sharpe=+0.7209)
- Admission: Train IC=+0.2564, Deflated=+0.2562, IR=0.80, Mono=0.80, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.090 | 2017: +0.044 | 2018: +0.133 | 2019: +0.220 | 2020: +0.069 | 2021: +0.191 | 2022: +0.060 | 2023: +0.115 | 2024: +0.105 | 2025: +0.147 | 2026: +0.113
- Yearly Tail ICs:   2015: -0.019 | 2016: +0.005 | 2017: +0.199 | 2018: +0.189 | 2019: +0.588 | 2020: +0.121 | 2021: +0.326 | 2022: +0.120 | 2023: +0.254 | 2024: +0.356 | 2025: +0.147 | 2026: +0.161
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.71
- Early IC=+0.1770, Recent IC=+0.1260, 1st-half IC=+0.1541, 2nd-half IC=+0.1127, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.125, Q3_mid=+0.145, Q4=+0.142, Q5_high_vol=+0.154

**`combo_mean__first_bar_sentiment__limit_down_proximity_early`** (Lock IC=+0.1358, Sharpe=+0.6902)
- Admission: Train IC=+0.2284, Deflated=+0.2282, IR=0.58, Mono=0.66, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.050 | 2017: -0.027 | 2018: +0.120 | 2019: +0.226 | 2020: +0.136 | 2021: +0.105 | 2022: +0.083 | 2023: +0.053 | 2024: +0.067 | 2025: +0.095 | 2026: +0.136
- Yearly Tail ICs:   2015: +0.137 | 2016: +0.044 | 2017: +0.126 | 2018: +0.238 | 2019: +0.390 | 2020: +0.118 | 2021: +0.114 | 2022: +0.188 | 2023: +0.065 | 2024: +0.352 | 2025: +0.150 | 2026: +0.390
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.47
- Early IC=+0.1732, Recent IC=+0.0810, 1st-half IC=+0.1457, 2nd-half IC=+0.0838, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.084, Q3_mid=+0.156, Q4=+0.091, Q5_high_vol=+0.121

**`combo_rank_min__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0850, Sharpe=+0.6640)
- Admission: Train IC=+0.2595, Deflated=+0.2603, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.068 | 2017: +0.003 | 2018: +0.069 | 2019: +0.212 | 2020: +0.149 | 2021: +0.125 | 2022: +0.111 | 2023: +0.156 | 2024: +0.108 | 2025: +0.170 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.140 | 2017: +0.069 | 2018: +0.291 | 2019: +0.442 | 2020: +0.162 | 2021: +0.354 | 2022: +0.262 | 2023: +0.226 | 2024: +0.237 | 2025: +0.120 | 2026: +0.056
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.99
- Early IC=+0.1405, Recent IC=+0.1387, 1st-half IC=+0.1368, 2nd-half IC=+0.1400, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.31)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.171, Q3_mid=+0.137, Q4=+0.137, Q5_high_vol=+0.160

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0503, Sharpe=+0.6600)
- Admission: Train IC=+0.2638, Deflated=+0.2641, IR=0.85, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.140 | 2017: +0.020 | 2018: +0.094 | 2019: +0.236 | 2020: +0.148 | 2021: +0.128 | 2022: +0.100 | 2023: +0.138 | 2024: +0.104 | 2025: +0.188 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.201 | 2017: +0.311 | 2018: +0.163 | 2019: +0.495 | 2020: +0.306 | 2021: +0.135 | 2022: +0.273 | 2023: +0.303 | 2024: +0.236 | 2025: +0.336 | 2026: +0.174
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.89
- Early IC=+0.1652, Recent IC=+0.1462, 1st-half IC=+0.1493, 2nd-half IC=+0.1356, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.148, Q3_mid=+0.146, Q4=+0.133, Q5_high_vol=+0.168

**`combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0673, Sharpe=+0.6455)
- Admission: Train IC=+0.1928, Deflated=+0.1928, IR=0.60, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.157 | 2016: +0.015 | 2017: +0.017 | 2018: +0.040 | 2019: +0.121 | 2020: +0.054 | 2021: +0.146 | 2022: +0.097 | 2023: +0.132 | 2024: +0.111 | 2025: +0.123 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.023 | 2017: +0.006 | 2018: +0.196 | 2019: +0.341 | 2020: +0.179 | 2021: +0.285 | 2022: +0.117 | 2023: +0.270 | 2024: +0.333 | 2025: +0.100 | 2026: +0.267
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.45, Recency ratio=1.46
- Early IC=+0.0805, Recent IC=+0.1173, 1st-half IC=+0.0860, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.130, Q3_mid=+0.102, Q4=+0.122, Q5_high_vol=+0.117

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0827, Sharpe=+0.6302)
- Admission: Train IC=+0.3748, Deflated=+0.3754, IR=1.23, Mono=0.88, p=0.0000, MaxCorr=0.98
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
- Admission: Train IC=+0.2943, Deflated=+0.2957, IR=1.10, Mono=0.86, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.083 | 2017: -0.035 | 2018: +0.113 | 2019: +0.261 | 2020: +0.144 | 2021: +0.118 | 2022: +0.072 | 2023: +0.151 | 2024: +0.107 | 2025: +0.149 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.119 | 2017: +0.027 | 2018: +0.283 | 2019: +0.516 | 2020: +0.218 | 2021: +0.306 | 2022: +0.266 | 2023: +0.354 | 2024: +0.410 | 2025: +0.092 | 2026: +0.228
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1867, Recent IC=+0.1281, 1st-half IC=+0.1519, 2nd-half IC=+0.1253, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.154, Q3_mid=+0.137, Q4=+0.123, Q5_high_vol=+0.156

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1000, Sharpe=+0.4816)
- Admission: Train IC=+0.3521, Deflated=+0.3534, IR=1.04, Mono=0.85, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.110 | 2017: -0.012 | 2018: +0.158 | 2019: +0.260 | 2020: +0.173 | 2021: +0.134 | 2022: +0.082 | 2023: +0.152 | 2024: +0.096 | 2025: +0.160 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.130 | 2017: +0.034 | 2018: +0.352 | 2019: +0.560 | 2020: +0.402 | 2021: +0.271 | 2022: +0.184 | 2023: +0.346 | 2024: +0.447 | 2025: +0.203 | 2026: +0.257
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.61
- Early IC=+0.2090, Recent IC=+0.1283, 1st-half IC=+0.1771, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.166, Q3_mid=+0.134, Q4=+0.154, Q5_high_vol=+0.182

**`combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`** (Lock IC=+0.1488, Sharpe=+0.4556)
- Admission: Train IC=+0.2500, Deflated=+0.2497, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.138 | 2016: +0.082 | 2017: -0.053 | 2018: +0.113 | 2019: +0.112 | 2020: +0.135 | 2021: +0.035 | 2022: +0.179 | 2023: +0.123 | 2024: +0.051 | 2025: +0.097 | 2026: +0.149
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.238 | 2017: +0.019 | 2018: +0.411 | 2019: +0.240 | 2020: +0.403 | 2021: +0.122 | 2022: +0.396 | 2023: +0.108 | 2024: +0.062 | 2025: +0.178 | 2026: +0.197
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.15, Recency ratio=0.66
- Early IC=+0.1125, Recent IC=+0.0740, 1st-half IC=+0.0990, 2nd-half IC=+0.1138, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=0.78)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.104, Q3_mid=+0.091, Q4=+0.139, Q5_high_vol=+0.131

**`combo_min__max_up_ret__first_bar_return`** (Lock IC=+0.0299, Sharpe=+0.3733)
- Admission: Train IC=+0.1766, Deflated=+0.1781, IR=0.63, Mono=0.77, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.087 | 2017: +0.047 | 2018: +0.098 | 2019: +0.172 | 2020: +0.096 | 2021: +0.138 | 2022: +0.087 | 2023: +0.172 | 2024: +0.059 | 2025: +0.137 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.003 | 2017: +0.139 | 2018: +0.196 | 2019: +0.232 | 2020: +0.022 | 2021: +0.227 | 2022: +0.200 | 2023: +0.386 | 2024: +0.145 | 2025: +0.170 | 2026: +0.223
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.73
- Early IC=+0.1350, Recent IC=+0.0981, 1st-half IC=+0.1178, 2nd-half IC=+0.1141, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.165, Q3_mid=+0.102, Q4=+0.089, Q5_high_vol=+0.122

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1062, Sharpe=+0.3404)
- Admission: Train IC=+0.3108, Deflated=+0.3111, IR=1.02, Mono=0.85, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.159 | 2017: -0.015 | 2018: +0.157 | 2019: +0.230 | 2020: +0.184 | 2021: +0.136 | 2022: +0.108 | 2023: +0.127 | 2024: +0.092 | 2025: +0.153 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.079 | 2016: +0.184 | 2017: +0.022 | 2018: +0.341 | 2019: +0.411 | 2020: +0.331 | 2021: +0.319 | 2022: +0.225 | 2023: +0.238 | 2024: +0.462 | 2025: +0.237 | 2026: +0.178
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.63
- Early IC=+0.1938, Recent IC=+0.1222, 1st-half IC=+0.1756, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.131, Q3_mid=+0.161, Q4=+0.124, Q5_high_vol=+0.167

**`combo_max__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0852, Sharpe=+0.3263)
- Admission: Train IC=+0.1835, Deflated=+0.1829, IR=0.44, Mono=0.68, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.123 | 2017: -0.015 | 2018: +0.135 | 2019: +0.135 | 2020: +0.081 | 2021: +0.140 | 2022: +0.124 | 2023: +0.090 | 2024: +0.025 | 2025: +0.113 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.117 | 2016: -0.005 | 2017: +0.114 | 2018: +0.315 | 2019: +0.265 | 2020: -0.028 | 2021: +0.346 | 2022: +0.053 | 2023: +0.089 | 2024: +0.218 | 2025: +0.168 | 2026: +0.074
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.51
- Early IC=+0.1350, Recent IC=+0.0688, 1st-half IC=+0.1197, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.083, Q3_mid=+0.124, Q4=+0.074, Q5_high_vol=+0.104

**`combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0852, Sharpe=+0.3263)
- Admission: Train IC=+0.1835, Deflated=+0.1829, IR=0.44, Mono=0.68, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.123 | 2017: -0.015 | 2018: +0.135 | 2019: +0.135 | 2020: +0.081 | 2021: +0.140 | 2022: +0.124 | 2023: +0.090 | 2024: +0.025 | 2025: +0.113 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.117 | 2016: -0.005 | 2017: +0.114 | 2018: +0.315 | 2019: +0.265 | 2020: -0.028 | 2021: +0.346 | 2022: +0.053 | 2023: +0.089 | 2024: +0.218 | 2025: +0.168 | 2026: +0.074
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.77, Recency ratio=0.51
- Early IC=+0.1350, Recent IC=+0.0688, 1st-half IC=+0.1197, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.083, Q3_mid=+0.124, Q4=+0.074, Q5_high_vol=+0.104

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1358, Sharpe=+0.2908)
- Admission: Train IC=+0.2041, Deflated=+0.2031, IR=0.49, Mono=0.66, p=0.0002, MaxCorr=0.86
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

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0877, Sharpe=+0.2567)
- Admission: Train IC=+0.3523, Deflated=+0.3536, IR=1.07, Mono=0.84, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.121 | 2017: +0.000 | 2018: +0.167 | 2019: +0.237 | 2020: +0.163 | 2021: +0.140 | 2022: +0.076 | 2023: +0.177 | 2024: +0.108 | 2025: +0.156 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.092 | 2016: +0.153 | 2017: -0.002 | 2018: +0.403 | 2019: +0.532 | 2020: +0.389 | 2021: +0.244 | 2022: +0.196 | 2023: +0.421 | 2024: +0.444 | 2025: +0.198 | 2026: +0.181
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.65
- Early IC=+0.2019, Recent IC=+0.1321, 1st-half IC=+0.1708, 2nd-half IC=+0.1352, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.178, Q3_mid=+0.126, Q4=+0.159, Q5_high_vol=+0.184

**`first_bar_return`** (Lock IC=+0.0226, Sharpe=+0.2558)
- Admission: Train IC=+0.1648, Deflated=+0.1657, IR=0.60, Mono=0.73, p=0.0014, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.162 | 2017: +0.017 | 2018: +0.137 | 2019: +0.192 | 2020: +0.116 | 2021: +0.135 | 2022: +0.073 | 2023: +0.144 | 2024: +0.061 | 2025: +0.123 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.56
- Early IC=+0.1645, Recent IC=+0.0918, 1st-half IC=+0.1316, 2nd-half IC=+0.0981, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.130, Q3_mid=+0.113, Q4=+0.063, Q5_high_vol=+0.129

**`combo_sig_product__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0219, Sharpe=+0.2558)
- Admission: Train IC=+0.1648, Deflated=+0.1657, IR=0.60, Mono=0.73, p=0.0014, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.157 | 2017: +0.019 | 2018: +0.138 | 2019: +0.193 | 2020: +0.115 | 2021: +0.133 | 2022: +0.072 | 2023: +0.143 | 2024: +0.060 | 2025: +0.120 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.54
- Early IC=+0.1658, Recent IC=+0.0900, 1st-half IC=+0.1316, 2nd-half IC=+0.0969, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.131, Q3_mid=+0.114, Q4=+0.061, Q5_high_vol=+0.127

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0641, Sharpe=+0.2487)
- Admission: Train IC=+0.2804, Deflated=+0.2815, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.132 | 2017: -0.020 | 2018: +0.155 | 2019: +0.240 | 2020: +0.159 | 2021: +0.129 | 2022: +0.084 | 2023: +0.087 | 2024: +0.087 | 2025: +0.128 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.082 | 2017: +0.047 | 2018: +0.317 | 2019: +0.499 | 2020: +0.239 | 2021: +0.257 | 2022: +0.256 | 2023: +0.218 | 2024: +0.421 | 2025: +0.105 | 2026: +0.238
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.55
- Early IC=+0.1974, Recent IC=+0.1077, 1st-half IC=+0.1660, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.133, Q3_mid=+0.121, Q4=+0.133, Q5_high_vol=+0.172

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0892, Sharpe=+0.2487)
- Admission: Train IC=+0.2787, Deflated=+0.2803, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.090 | 2017: -0.004 | 2018: +0.152 | 2019: +0.243 | 2020: +0.142 | 2021: +0.127 | 2022: +0.097 | 2023: +0.137 | 2024: +0.074 | 2025: +0.163 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.064 | 2017: +0.081 | 2018: +0.317 | 2019: +0.501 | 2020: +0.216 | 2021: +0.253 | 2022: +0.258 | 2023: +0.225 | 2024: +0.413 | 2025: +0.110 | 2026: +0.249
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.60
- Early IC=+0.1975, Recent IC=+0.1182, 1st-half IC=+0.1593, 2nd-half IC=+0.1234, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.159, Q3_mid=+0.120, Q4=+0.139, Q5_high_vol=+0.178

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0895, Sharpe=+0.2487)
- Admission: Train IC=+0.2787, Deflated=+0.2803, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.089 | 2017: -0.005 | 2018: +0.152 | 2019: +0.243 | 2020: +0.141 | 2021: +0.127 | 2022: +0.097 | 2023: +0.137 | 2024: +0.074 | 2025: +0.163 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.061 | 2017: +0.081 | 2018: +0.317 | 2019: +0.501 | 2020: +0.216 | 2021: +0.253 | 2022: +0.263 | 2023: +0.223 | 2024: +0.413 | 2025: +0.118 | 2026: +0.249
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.60
- Early IC=+0.1974, Recent IC=+0.1185, 1st-half IC=+0.1593, 2nd-half IC=+0.1236, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.159, Q3_mid=+0.120, Q4=+0.138, Q5_high_vol=+0.178

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.2449)
- Admission: Train IC=+0.2506, Deflated=+0.2503, IR=0.67, Mono=0.77, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.047 | 2017: -0.045 | 2018: +0.086 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.181 | 2023: +0.115 | 2024: +0.084 | 2025: +0.129 | 2026: +0.129
- Yearly Tail ICs:   2015: +0.142 | 2016: +0.229 | 2017: +0.092 | 2018: +0.360 | 2019: +0.281 | 2020: +0.401 | 2021: +0.125 | 2022: +0.494 | 2023: +0.111 | 2024: +0.061 | 2025: +0.103 | 2026: +0.261
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.46, Recency ratio=0.98
- Early IC=+0.1084, Recent IC=+0.1064, 1st-half IC=+0.0883, 2nd-half IC=+0.1293, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.076, Q2=+0.113, Q3_mid=+0.089, Q4=+0.122, Q5_high_vol=+0.143

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0486, Sharpe=+0.1892)
- Admission: Train IC=+0.3411, Deflated=+0.3414, IR=1.20, Mono=0.86, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.130 | 2017: -0.013 | 2018: +0.190 | 2019: +0.209 | 2020: +0.171 | 2021: +0.134 | 2022: +0.099 | 2023: +0.146 | 2024: +0.106 | 2025: +0.133 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.153 | 2016: +0.120 | 2017: +0.115 | 2018: +0.368 | 2019: +0.527 | 2020: +0.324 | 2021: +0.264 | 2022: +0.392 | 2023: +0.401 | 2024: +0.319 | 2025: +0.271 | 2026: +0.186
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.60
- Early IC=+0.1994, Recent IC=+0.1196, 1st-half IC=+0.1704, 2nd-half IC=+0.1231, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.57)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.158, Q3_mid=+0.124, Q4=+0.165, Q5_high_vol=+0.168

**`combo_rank_max__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1158, Sharpe=+0.1892)
- Admission: Train IC=+0.2098, Deflated=+0.2088, IR=0.50, Mono=0.66, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.114 | 2017: -0.008 | 2018: +0.121 | 2019: +0.159 | 2020: +0.101 | 2021: +0.124 | 2022: +0.158 | 2023: +0.107 | 2024: +0.058 | 2025: +0.154 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.124 | 2016: -0.008 | 2017: +0.178 | 2018: +0.314 | 2019: +0.290 | 2020: +0.062 | 2021: +0.318 | 2022: +0.128 | 2023: +0.165 | 2024: +0.183 | 2025: +0.116 | 2026: -0.096
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.71
- Early IC=+0.1429, Recent IC=+0.1016, 1st-half IC=+0.1318, 2nd-half IC=+0.1176, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.105, Q3_mid=+0.145, Q4=+0.116, Q5_high_vol=+0.108

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0535, Sharpe=+0.1627)
- Admission: Train IC=+0.2666, Deflated=+0.2666, IR=0.66, Mono=0.73, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.058 | 2017: +0.036 | 2018: +0.103 | 2019: +0.108 | 2020: +0.063 | 2021: +0.168 | 2022: +0.136 | 2023: +0.149 | 2024: +0.108 | 2025: +0.178 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.200 | 2017: +0.109 | 2018: +0.288 | 2019: +0.267 | 2020: +0.250 | 2021: +0.320 | 2022: +0.153 | 2023: +0.120 | 2024: +0.388 | 2025: +0.259 | 2026: +0.229
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.35, Recency ratio=1.36
- Early IC=+0.1052, Recent IC=+0.1430, 1st-half IC=+0.1093, 2nd-half IC=+0.1478, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.151, Q3_mid=+0.099, Q4=+0.162, Q5_high_vol=+0.159

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0646, Sharpe=+0.1352)
- Admission: Train IC=+0.2982, Deflated=+0.2982, IR=0.96, Mono=0.85, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.26
- Early IC=+0.1165, Recent IC=+0.1473, 1st-half IC=+0.1261, 2nd-half IC=+0.1540, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.58)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.169, Q3_mid=+0.123, Q4=+0.150, Q5_high_vol=+0.162

**`combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.1013, Sharpe=+0.1249)
- Admission: Train IC=+0.2369, Deflated=+0.2367, IR=0.83, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.024 | 2017: +0.014 | 2018: +0.116 | 2019: +0.216 | 2020: +0.088 | 2021: +0.135 | 2022: +0.100 | 2023: +0.144 | 2024: +0.112 | 2025: +0.141 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.021 | 2017: +0.114 | 2018: +0.149 | 2019: +0.465 | 2020: +0.069 | 2021: +0.216 | 2022: +0.175 | 2023: +0.322 | 2024: +0.417 | 2025: +0.143 | 2026: +0.169
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.1660, Recent IC=+0.1263, 1st-half IC=+0.1300, 2nd-half IC=+0.1324, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.124, Q3_mid=+0.129, Q4=+0.141, Q5_high_vol=+0.149

**`combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1013, Sharpe=+0.1249)
- Admission: Train IC=+0.2369, Deflated=+0.2367, IR=0.83, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.024 | 2017: +0.014 | 2018: +0.116 | 2019: +0.216 | 2020: +0.088 | 2021: +0.135 | 2022: +0.100 | 2023: +0.144 | 2024: +0.112 | 2025: +0.141 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.021 | 2017: +0.114 | 2018: +0.149 | 2019: +0.465 | 2020: +0.069 | 2021: +0.216 | 2022: +0.175 | 2023: +0.322 | 2024: +0.417 | 2025: +0.143 | 2026: +0.169
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=1.02, Recency ratio=0.76
- Early IC=+0.1660, Recent IC=+0.1263, 1st-half IC=+0.1300, 2nd-half IC=+0.1324, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.124, Q3_mid=+0.129, Q4=+0.141, Q5_high_vol=+0.149

**`combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1554, Sharpe=+0.1107)
- Admission: Train IC=+0.2406, Deflated=+0.2403, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.070 | 2017: -0.066 | 2018: +0.120 | 2019: +0.118 | 2020: +0.123 | 2021: +0.050 | 2022: +0.167 | 2023: +0.129 | 2024: +0.048 | 2025: +0.080 | 2026: +0.155
- Yearly Tail ICs:   2015: +0.092 | 2016: +0.241 | 2017: +0.021 | 2018: +0.415 | 2019: +0.337 | 2020: +0.371 | 2021: +0.126 | 2022: +0.465 | 2023: +0.109 | 2024: +0.012 | 2025: +0.071 | 2026: +0.170
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.53
- Early IC=+0.1190, Recent IC=+0.0636, 1st-half IC=+0.1013, 2nd-half IC=+0.1023, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.66)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.107, Q3_mid=+0.082, Q4=+0.126, Q5_high_vol=+0.139

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0431, Sharpe=+0.1011)
- Admission: Train IC=+0.2416, Deflated=+0.2424, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.122 | 2017: +0.026 | 2018: +0.091 | 2019: +0.207 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.175 | 2024: +0.041 | 2025: +0.186 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.171 | 2016: +0.172 | 2017: +0.144 | 2018: +0.389 | 2019: +0.275 | 2020: +0.048 | 2021: +0.333 | 2022: +0.199 | 2023: +0.371 | 2024: +0.174 | 2025: +0.362 | 2026: +0.097
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.88, Recency ratio=0.76
- Early IC=+0.1490, Recent IC=+0.1136, 1st-half IC=+0.1439, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.168, Q3_mid=+0.133, Q4=+0.102, Q5_high_vol=+0.127

**`combo_mean__limit_down_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1186, Sharpe=+0.0733)
- Admission: Train IC=+0.2565, Deflated=+0.2561, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.065 | 2017: +0.036 | 2018: +0.117 | 2019: +0.221 | 2020: +0.039 | 2021: +0.171 | 2022: +0.041 | 2023: +0.114 | 2024: +0.095 | 2025: +0.141 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.163 | 2016: -0.114 | 2017: +0.150 | 2018: +0.113 | 2019: +0.565 | 2020: +0.079 | 2021: +0.336 | 2022: +0.103 | 2023: +0.304 | 2024: +0.311 | 2025: +0.172 | 2026: +0.183
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.70
- Early IC=+0.1690, Recent IC=+0.1180, 1st-half IC=+0.1347, 2nd-half IC=+0.1039, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.114, Q3_mid=+0.140, Q4=+0.117, Q5_high_vol=+0.132

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0307, Sharpe=+0.0580)
- Admission: Train IC=+0.2465, Deflated=+0.2477, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.96
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

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0487, Sharpe=+0.0203)
- Admission: Train IC=+0.2523, Deflated=+0.2531, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.133 | 2017: +0.043 | 2018: +0.088 | 2019: +0.188 | 2020: +0.131 | 2021: +0.160 | 2022: +0.122 | 2023: +0.164 | 2024: +0.045 | 2025: +0.184 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.237 | 2017: +0.127 | 2018: +0.361 | 2019: +0.295 | 2020: +0.127 | 2021: +0.404 | 2022: +0.228 | 2023: +0.369 | 2024: +0.161 | 2025: +0.344 | 2026: +0.083
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.83
- Early IC=+0.1379, Recent IC=+0.1147, 1st-half IC=+0.1433, 2nd-half IC=+0.1284, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.170, Q3_mid=+0.130, Q4=+0.115, Q5_high_vol=+0.121

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0587, Sharpe=+0.0073)
- Admission: Train IC=+0.2979, Deflated=+0.2987, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.95
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
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0062 | N/A | +0.0062 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0035 | N/A | +0.0035 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | Median | persistent | +0.0006 | N/A | +0.0006 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0` | Median | persistent | +0.0005 | N/A | +0.0005 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | FP | immediate | -0.0023 | N/A | -0.0023 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | FP | immediate | -0.0076 | N/A | -0.0076 | ∞ |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | FP | immediate | -0.0121 | N/A | -0.0121 | ∞ |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | FP | immediate | -0.0121 | N/A | -0.0121 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.0127 | N/A | -0.0127 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0127 | N/A | -0.0127 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0169 | N/A | -0.0169 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | FP | immediate | -0.0199 | N/A | -0.0199 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0293 | N/A | -0.0293 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | FP | immediate | -0.0294 | N/A | -0.0294 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.0294 | N/A | -0.0294 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | FP | immediate | -0.0297 | N/A | -0.0297 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0308 | N/A | -0.0308 | ∞ |
| `combo_rank_min__bar_body_rng_0__volume_surge_direction` | FP | immediate | -0.0374 | N/A | -0.0374 | ∞ |
| `combo_rank_min__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.0433 | N/A | -0.0433 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0466 | N/A | -0.0466 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | FP | immediate | -0.0504 | N/A | -0.0504 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.0539 | N/A | -0.0539 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0539 | N/A | -0.0539 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | FP | immediate | -0.0541 | N/A | -0.0541 | ∞ |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.0557 | N/A | -0.0557 | ∞ |
| `combo_mean__bar_body_rng_0__volume_surge_direction` | FP | immediate | -0.0571 | N/A | -0.0571 | ∞ |
| `combo_sig_product__bar_body_rng_0__volume_surge_direction` | FP | immediate | -0.0580 | N/A | -0.0580 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0581 | N/A | -0.0581 | ∞ |
| `combo_min__max_up_ret__volume_surge_direction` | FP | immediate | -0.0597 | N/A | -0.0597 | ∞ |
| `combo_min__bar_body_rng_0__volume_surge_direction` | FP | immediate | -0.0625 | N/A | -0.0625 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0627 | N/A | -0.0627 | ∞ |
| `combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.0631 | N/A | -0.0631 | ∞ |
| `combo_rank_min__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0638 | N/A | -0.0638 | ∞ |
| `combo_rank_min__max_up_ret__volume_surge_direction` | FP | immediate | -0.0639 | N/A | -0.0639 | ∞ |
| `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.0691 | N/A | -0.0691 | ∞ |
| `combo_min__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0691 | N/A | -0.0691 | ∞ |
| `combo_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0695 | N/A | -0.0695 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.0712 | N/A | -0.0712 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | FP | immediate | -0.0717 | N/A | -0.0717 | ∞ |
| `combo_mean__first_bar_sentiment__volume_surge_direction` | FP | immediate | -0.0740 | N/A | -0.0740 | ∞ |
| `combo_min__bar_ret_0__volume_surge_direction` | FP | immediate | -0.0762 | N/A | -0.0762 | ∞ |
| `combo_max__first_bar_return__bar_body_rng_0` | FP | immediate | -0.0776 | N/A | -0.0776 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0781 | N/A | -0.0781 | ∞ |
| `combo_rank_max__first_bar_return__volume_surge_direction` | FP | immediate | -0.0811 | N/A | -0.0811 | ∞ |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.0823 | N/A | -0.0823 | ∞ |
| `combo_mean__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0827 | N/A | -0.0827 | ∞ |
| `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0828 | N/A | -0.0828 | ∞ |
| `combo_max__bar_ret_0__volume_surge_direction` | FP | immediate | -0.0832 | N/A | -0.0832 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | FP | immediate | -0.0842 | N/A | -0.0842 | ∞ |
| `combo_tri_median__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0881 | N/A | -0.0881 | ∞ |
| `combo_tri_median__bar_ret_0__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0883 | N/A | -0.0883 | ∞ |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0908 | N/A | -0.0908 | ∞ |
| `combo_min__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0924 | N/A | -0.0924 | ∞ |
| `combo_max__first_bar_return__first_bar_sentiment` | FP | immediate | -0.0930 | N/A | -0.0930 | ∞ |
| `combo_ratio__first_bar_return__volume_surge_direction` | FP | immediate | -0.0939 | N/A | -0.0939 | ∞ |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.0942 | N/A | -0.0942 | ∞ |
| `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position` | FP | immediate | -0.0955 | N/A | -0.0955 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0955 | N/A | -0.0955 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_return` | FP | immediate | -0.0956 | N/A | -0.0956 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.0969 | N/A | -0.0969 | ∞ |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0976 | N/A | -0.0976 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1002 | N/A | -0.1002 | ∞ |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1073 | N/A | -0.1073 | ∞ |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1081 | N/A | -0.1081 | ∞ |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1087 | N/A | -0.1087 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.1148 | N/A | -0.1148 | ∞ |
| `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1153 | N/A | -0.1153 | ∞ |
| `combo_mean__max_up_ret__volume_surge_direction` | FP | immediate | -0.1168 | N/A | -0.1168 | ∞ |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.1191 | N/A | -0.1191 | ∞ |
| `combo_ratio__volume_surge_direction__volume_weighted_price_position` | FP | immediate | -0.1192 | N/A | -0.1192 | ∞ |
| `combo_tri_mean__volume_weighted_momentum_acceleration__max_up_ret__first_bar_return` | FP | immediate | -0.1212 | N/A | -0.1212 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.1221 | N/A | -0.1221 | ∞ |
| `combo_sig_product__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1294 | N/A | -0.1294 | ∞ |
| `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1298 | N/A | -0.1298 | ∞ |
| `combo_tri_median__volume_weighted_momentum_acceleration__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1305 | N/A | -0.1305 | ∞ |
| `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_ret_0` | FP | immediate | -0.1339 | N/A | -0.1339 | ∞ |
| `combo_mean__max_up_ret__first_bar_return` | FP | immediate | -0.1373 | N/A | -0.1373 | ∞ |
| `combo_mean__max_up_ret__bar_ret_0` | FP | immediate | -0.1373 | N/A | -0.1373 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | FP | immediate | -0.1395 | N/A | -0.1395 | ∞ |
| `combo_max__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.1417 | N/A | -0.1417 | ∞ |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.1417 | N/A | -0.1417 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | FP | immediate | -0.1425 | N/A | -0.1425 | ∞ |
| `combo_ratio__max_up_ret__bar_vol_0` | FP | immediate | -0.1432 | N/A | -0.1432 | ∞ |
| `combo_tri_mean__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1436 | N/A | -0.1436 | ∞ |
| `combo_max__max_up_ret__volume_surge_direction` | FP | immediate | -0.1457 | N/A | -0.1457 | ∞ |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1466 | N/A | -0.1466 | ∞ |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | FP | immediate | -0.1469 | N/A | -0.1469 | ∞ |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | FP | immediate | -0.1476 | N/A | -0.1476 | ∞ |
| `combo_tri_mean__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.1480 | N/A | -0.1480 | ∞ |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | FP | immediate | -0.1502 | N/A | -0.1502 | ∞ |
| `combo_rank_max__max_up_ret__volume_surge_direction` | FP | immediate | -0.1503 | N/A | -0.1503 | ∞ |
| `opening_drive_thrust_ratio` | FP | immediate | -0.1510 | N/A | -0.1510 | ∞ |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | FP | immediate | -0.1522 | N/A | -0.1522 | ∞ |
| `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1526 | N/A | -0.1526 | ∞ |
| `combo_rank_max__volume_weighted_price_position__volume_surge_direction` | FP | immediate | -0.1571 | N/A | -0.1571 | ∞ |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1573 | N/A | -0.1573 | ∞ |
| `volume_weighted_price_position` | FP | immediate | -0.1599 | N/A | -0.1599 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_return` | FP | immediate | -0.1611 | N/A | -0.1611 | ∞ |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.1637 | N/A | -0.1637 | ∞ |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1697 | N/A | -0.1697 | ∞ |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | FP | immediate | -0.1708 | N/A | -0.1708 | ∞ |
| `combo_tri_mean__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1740 | N/A | -0.1740 | ∞ |
| `morning_volume_weighted_momentum` | FP | immediate | -0.1752 | N/A | -0.1752 | ∞ |
| `combo_rank_max__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.1762 | N/A | -0.1762 | ∞ |
| `net_volume_flow` | FP | immediate | -0.1763 | N/A | -0.1763 | ∞ |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1823 | N/A | -0.1823 | ∞ |
| `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio` | FP | immediate | -0.1947 | N/A | -0.1947 | ∞ |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.1964 | N/A | -0.1964 | ∞ |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1967 | N/A | -0.1967 | ∞ |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.1994 | N/A | -0.1994 | ∞ |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | immediate | -0.2002 | N/A | -0.2002 | ∞ |
| `early_order_flow_imbalance` | FP | immediate | -0.2024 | N/A | -0.2024 | ∞ |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | FP | immediate | -0.2112 | N/A | -0.2112 | ∞ |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.2114 | N/A | -0.2114 | ∞ |
| `trend_bar_close_consistency` | FP | immediate | -0.2260 | N/A | -0.2260 | ∞ |
| `always_in_trend_persistence` | FP | immediate | -0.2597 | N/A | -0.2597 | ∞ |

**Decay distribution**: immediate=112, fast(1-2y)=0, gradual=0, persistent=11

**FP decay trajectories:**

- `always_in_trend_persistence`: Y1:-0.260
- `trend_bar_close_consistency`: Y1:-0.226
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.211
- `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`: Y1:-0.211
- `early_order_flow_imbalance`: Y1:-0.202
- `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.200
- `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.199
- `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.197
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:-0.196
- `combo_tri_mean__volume_weighted_momentum_acceleration__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.195
- `combo_tri_median__smooth_momentum_structure__max_up_ret__volume_weighted_price_position`: Y1:-0.182
- `net_volume_flow`: Y1:-0.176
- `combo_rank_max__first_bar_return__volume_weighted_price_position`: Y1:-0.176
- `morning_volume_weighted_momentum`: Y1:-0.175
- `combo_tri_mean__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.174
- `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.171
- `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.170
- `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.164
- `combo_rank_max__max_up_ret__first_bar_return`: Y1:-0.161
- `volume_weighted_price_position`: Y1:-0.160
- `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.157
- `combo_rank_max__volume_weighted_price_position__volume_surge_direction`: Y1:-0.157
- `combo_tri_median__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.153
- `combo_max__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.152
- `opening_drive_thrust_ratio`: Y1:-0.151
- `combo_rank_max__max_up_ret__volume_surge_direction`: Y1:-0.150
- `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.150
- `combo_tri_mean__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.148
- `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`: Y1:-0.148
- `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`: Y1:-0.147
- `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.147
- `combo_max__max_up_ret__volume_surge_direction`: Y1:-0.146
- `combo_tri_mean__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.144
- `combo_ratio__max_up_ret__bar_vol_0`: Y1:-0.143
- `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.143
- `combo_rank_max__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.142
- `combo_max__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.142
- `combo_max__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:-0.140
- `combo_mean__max_up_ret__first_bar_return`: Y1:-0.137
- `combo_mean__max_up_ret__bar_ret_0`: Y1:-0.137
- `combo_tri_median__volume_weighted_momentum_acceleration__max_up_ret__bar_ret_0`: Y1:-0.134
- `combo_tri_median__volume_weighted_momentum_acceleration__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.131
- `combo_tri_median__smooth_momentum_structure__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.130
- `combo_sig_product__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.129
- `combo_mean__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.122
- `combo_tri_mean__volume_weighted_momentum_acceleration__max_up_ret__first_bar_return`: Y1:-0.121
- `combo_ratio__volume_surge_direction__volume_weighted_price_position`: Y1:-0.119
- `combo_mean__volume_weighted_price_position__volume_surge_direction`: Y1:-0.119
- `combo_mean__max_up_ret__volume_surge_direction`: Y1:-0.117
- `combo_tri_median__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.115
- `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.115
- `combo_ratio__first_bar_return__volume_weighted_price_position`: Y1:-0.109
- `combo_tri_min__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:-0.108
- `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.107
- `combo_sig_product__max_up_ret__volume_weighted_price_position`: Y1:-0.100
- `combo_ratio__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.098
- `combo_sig_product__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.097
- `combo_rank_min__max_up_ret__first_bar_return`: Y1:-0.096
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Y1:-0.095
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:-0.095
- `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.094
- `combo_ratio__first_bar_return__volume_surge_direction`: Y1:-0.094
- `combo_max__first_bar_return__first_bar_sentiment`: Y1:-0.093
- `combo_min__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.092
- `combo_sig_product__first_bar_return__volume_weighted_price_position`: Y1:-0.091
- `combo_tri_median__bar_ret_0__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.088
- `combo_tri_median__first_bar_return__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.088
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Y1:-0.084
- `combo_max__bar_ret_0__volume_surge_direction`: Y1:-0.083
- `combo_sig_product__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.083
- `combo_mean__first_bar_return__first_bar_sentiment`: Y1:-0.083
- `combo_min__opening_drive_thrust_ratio__volume_surge_direction`: Y1:-0.082
- `combo_rank_max__first_bar_return__volume_surge_direction`: Y1:-0.081
- `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.078
- `combo_max__first_bar_return__bar_body_rng_0`: Y1:-0.078
- `combo_min__bar_ret_0__volume_surge_direction`: Y1:-0.076
- `combo_mean__first_bar_sentiment__volume_surge_direction`: Y1:-0.074
- `combo_sig_product__max_up_ret__first_bar_return`: Y1:-0.072
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.071
- `combo_min__max_up_ret__first_bar_sentiment`: Y1:-0.069
- `combo_min__first_bar_return__first_bar_sentiment`: Y1:-0.069
- `combo_tri_min__max_up_ret__bar_ret_0__bar_body_rng_0`: Y1:-0.069
- `combo_rank_min__max_up_ret__volume_surge_direction`: Y1:-0.064
- `combo_rank_min__first_bar_return__first_bar_sentiment`: Y1:-0.064
- `combo_tri_min__bar_ret_0__volume_weighted_price_position__bar_body_rng_0`: Y1:-0.063
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.063
- `combo_min__bar_body_rng_0__volume_surge_direction`: Y1:-0.062
- `combo_min__max_up_ret__volume_surge_direction`: Y1:-0.060
- `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.058
- `combo_sig_product__bar_body_rng_0__volume_surge_direction`: Y1:-0.058
- `combo_mean__bar_body_rng_0__volume_surge_direction`: Y1:-0.057
- `combo_min__volume_weighted_price_position__volume_surge_direction`: Y1:-0.056
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`: Y1:-0.054
- `combo_tri_median__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.054
- `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.054
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Y1:-0.050
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.047
- `combo_rank_min__volume_weighted_price_position__volume_surge_direction`: Y1:-0.043
- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Y1:-0.037
- `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`: Y1:-0.031
- `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Y1:-0.030
- `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Y1:-0.029
- `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`: Y1:-0.029
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.029
- `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Y1:-0.020
- `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.017
- `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio`: Y1:-0.013
- `combo_tri_max__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`: Y1:-0.013
- `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Y1:-0.012
- `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Y1:-0.012
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`: Y1:-0.008
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
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.1105 | N/A | +0.1105 | ∞ |
| `combo_mean__star50_limit_proximity_early__first_bar_return` | Median | persistent | +0.1096 | N/A | +0.1096 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1067 | N/A | +0.1067 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1061 | N/A | +0.1061 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.1045 | N/A | +0.1045 | ∞ |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | Median | persistent | +0.1008 | N/A | +0.1008 | ∞ |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0988 | N/A | +0.0988 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0947 | N/A | +0.0947 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0887 | N/A | +0.0887 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0865 | N/A | +0.0865 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Median | persistent | +0.0832 | N/A | +0.0832 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0823 | N/A | +0.0823 | ∞ |
| `combo_max__net_volume_flow__star50_limit_proximity_early` | Median | persistent | +0.0823 | N/A | +0.0823 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0820 | N/A | +0.0820 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | TP | persistent | +0.0811 | N/A | +0.0811 | ∞ |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.0772 | N/A | +0.0772 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.0770 | N/A | +0.0770 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | persistent | +0.0765 | N/A | +0.0765 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0759 | N/A | +0.0759 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0755 | N/A | +0.0755 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction` | TP | persistent | +0.0739 | N/A | +0.0739 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0727 | N/A | +0.0727 | ∞ |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0708 | N/A | +0.0708 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0706 | N/A | +0.0706 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0695 | N/A | +0.0695 | ∞ |
| `combo_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0678 | N/A | +0.0678 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.0674 | N/A | +0.0674 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0670 | N/A | +0.0670 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0600 | N/A | +0.0600 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.0571 | N/A | +0.0571 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | TP | persistent | +0.0527 | N/A | +0.0527 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Median | persistent | +0.0508 | N/A | +0.0508 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.0473 | N/A | +0.0473 | ∞ |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0462 | N/A | +0.0462 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | persistent | +0.0441 | N/A | +0.0441 | ∞ |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0403 | N/A | +0.0403 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Median | persistent | +0.0383 | N/A | +0.0383 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.0380 | N/A | +0.0380 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | persistent | +0.0369 | N/A | +0.0369 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | persistent | +0.0350 | N/A | +0.0350 | ∞ |
| `max_down_ret` | Median | persistent | +0.0305 | N/A | +0.0305 | ∞ |
| `combo_rank_max__bar_ret_0__max_down_ret` | Median | persistent | +0.0298 | N/A | +0.0298 | ∞ |
| `combo_sig_product__max_up_ret__body_size_progression` | Median | persistent | +0.0274 | N/A | +0.0274 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0249 | N/A | +0.0249 | ∞ |
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
| `combo_max__first_bar_return__max_down_ret` | Median | persistent | +0.0078 | N/A | +0.0078 | ∞ |
| `combo_max__bar_ret_0__max_down_ret` | Median | persistent | +0.0077 | N/A | +0.0077 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0069 | N/A | +0.0069 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Median | persistent | +0.0059 | N/A | +0.0059 | ∞ |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Median | persistent | +0.0058 | N/A | +0.0058 | ∞ |
| `combo_rank_min__bar_ret_0__max_down_ret` | Median | persistent | +0.0056 | N/A | +0.0056 | ∞ |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0033 | N/A | +0.0033 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0028 | N/A | +0.0028 | ∞ |
| `opening_drive_thrust_ratio` | Median | persistent | +0.0025 | N/A | +0.0025 | ∞ |
| `combo_min__close_vs_open_range__bar_ret_0` | TP | persistent | +0.0024 | N/A | +0.0024 | ∞ |
| `combo_min__close_vs_open_range__first_bar_return` | TP | persistent | +0.0019 | N/A | +0.0019 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | FP | immediate | -0.0002 | N/A | -0.0002 | ∞ |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | FP | immediate | -0.0002 | N/A | -0.0002 | ∞ |
| `combo_rank_min__max_up_ret__bar_ret_0` | FP | immediate | -0.0007 | N/A | -0.0007 | ∞ |
| `combo_min__net_volume_flow__bar_ret_0` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment` | FP | immediate | -0.0012 | N/A | -0.0012 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency` | FP | immediate | -0.0016 | N/A | -0.0016 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | FP | immediate | -0.0019 | N/A | -0.0019 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | FP | immediate | -0.0061 | N/A | -0.0061 | ∞ |
| `combo_min__first_bar_sentiment__bar_ret_0` | FP | immediate | -0.0087 | N/A | -0.0087 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0104 | N/A | -0.0104 | ∞ |
| `combo_sig_product__max_up_ret__early_body_momentum` | FP | immediate | -0.0107 | N/A | -0.0107 | ∞ |
| `combo_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0112 | N/A | -0.0112 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0114 | N/A | -0.0114 | ∞ |
| `first_bar_return` | FP | immediate | -0.0114 | N/A | -0.0114 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | FP | immediate | -0.0123 | N/A | -0.0123 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | FP | immediate | -0.0124 | N/A | -0.0124 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0132 | N/A | -0.0132 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | FP | immediate | -0.0136 | N/A | -0.0136 | ∞ |
| `combo_min__trend_bar_close_consistency__bar_ret_0` | FP | immediate | -0.0156 | N/A | -0.0156 | ∞ |
| `combo_min__trend_bar_close_consistency__first_bar_return` | FP | immediate | -0.0156 | N/A | -0.0156 | ∞ |
| `combo_max__first_bar_sentiment__high_low_sequence_momentum` | FP | immediate | -0.0160 | N/A | -0.0160 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0187 | N/A | -0.0187 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression` | FP | immediate | -0.0194 | N/A | -0.0194 | ∞ |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | FP | immediate | -0.0206 | N/A | -0.0206 | ∞ |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | FP | immediate | -0.0261 | N/A | -0.0261 | ∞ |
| `vwap_trend_channel_slope` | FP | immediate | -0.0312 | N/A | -0.0312 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | FP | immediate | -0.0323 | N/A | -0.0323 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__bar_ret_0` | FP | immediate | -0.0328 | N/A | -0.0328 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__first_bar_return` | FP | immediate | -0.0328 | N/A | -0.0328 | ∞ |
| `combo_mean__max_up_ret__first_bar_return` | FP | immediate | -0.0337 | N/A | -0.0337 | ∞ |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | FP | immediate | -0.0367 | N/A | -0.0367 | ∞ |
| `combo_mean__close_vs_open_range__bar_ret_0` | FP | immediate | -0.0383 | N/A | -0.0383 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | FP | immediate | -0.0411 | N/A | -0.0411 | ∞ |
| `combo_min__net_volume_flow__first_bar_sentiment` | FP | immediate | -0.0444 | N/A | -0.0444 | ∞ |
| `combo_sig_product__net_volume_flow__max_down_ret` | FP | immediate | -0.0458 | N/A | -0.0458 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | FP | immediate | -0.0468 | N/A | -0.0468 | ∞ |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | FP | immediate | -0.0473 | N/A | -0.0473 | ∞ |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | FP | immediate | -0.0473 | N/A | -0.0473 | ∞ |
| `num_up_bars` | FP | immediate | -0.0474 | N/A | -0.0474 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | FP | immediate | -0.0503 | N/A | -0.0503 | ∞ |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | FP | immediate | -0.0520 | N/A | -0.0520 | ∞ |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | FP | immediate | -0.0523 | N/A | -0.0523 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | FP | immediate | -0.0526 | N/A | -0.0526 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression` | FP | immediate | -0.0592 | N/A | -0.0592 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | FP | immediate | -0.0624 | N/A | -0.0624 | ∞ |
| `combo_max__net_volume_flow__max_down_ret` | FP | immediate | -0.0643 | N/A | -0.0643 | ∞ |
| `combo_rank_max__max_up_ret__bar_ret_0` | FP | immediate | -0.0646 | N/A | -0.0646 | ∞ |
| `combo_max__close_vs_open_range__max_down_ret` | FP | immediate | -0.0673 | N/A | -0.0673 | ∞ |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0686 | N/A | -0.0686 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0689 | N/A | -0.0689 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | FP | immediate | -0.0695 | N/A | -0.0695 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | FP | immediate | -0.0710 | N/A | -0.0710 | ∞ |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | FP | immediate | -0.0739 | N/A | -0.0739 | ∞ |
| `micro_gap_trend_continuation` | FP | immediate | -0.0765 | N/A | -0.0765 | ∞ |
| `combo_min__close_vs_open_range__early_body_momentum` | FP | immediate | -0.0785 | N/A | -0.0785 | ∞ |
| `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range` | FP | immediate | -0.0837 | N/A | -0.0837 | ∞ |
| `volatility_expansion_trend_vector` | FP | immediate | -0.0850 | N/A | -0.0850 | ∞ |
| `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | FP | immediate | -0.0906 | N/A | -0.0906 | ∞ |
| `morning_volume_weighted_momentum` | FP | immediate | -0.0906 | N/A | -0.0906 | ∞ |
| `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0` | FP | immediate | -0.0914 | N/A | -0.0914 | ∞ |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | FP | immediate | -0.0933 | N/A | -0.0933 | ∞ |
| `vwap_close_divergence_trend` | FP | immediate | -0.0940 | N/A | -0.0940 | ∞ |
| `combo_max__close_vs_open_range__early_body_momentum` | FP | immediate | -0.0947 | N/A | -0.0947 | ∞ |
| `early_body_momentum` | FP | immediate | -0.0993 | N/A | -0.0993 | ∞ |
| `combo_sig_product__net_volume_flow__first_bar_return` | FP | immediate | -0.1006 | N/A | -0.1006 | ∞ |
| `first_30min_return` | FP | immediate | -0.1128 | N/A | -0.1128 | ∞ |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | FP | immediate | -0.1226 | N/A | -0.1226 | ∞ |
| `early_order_flow_imbalance` | FP | immediate | -0.1345 | N/A | -0.1345 | ∞ |
| `combo_sig_product__volatility_expansion_trend_vector__first_bar_return` | FP | immediate | -0.1430 | N/A | -0.1430 | ∞ |
| `always_in_trend_persistence` | FP | immediate | -0.1600 | N/A | -0.1600 | ∞ |
| `range_progression_trend` | FP | immediate | -0.1829 | N/A | -0.1829 | ∞ |

**Decay distribution**: immediate=71, fast(1-2y)=0, gradual=0, persistent=77

**FP decay trajectories:**

- `range_progression_trend`: Y1:-0.183
- `always_in_trend_persistence`: Y1:-0.160
- `combo_sig_product__volatility_expansion_trend_vector__first_bar_return`: Y1:-0.143
- `early_order_flow_imbalance`: Y1:-0.135
- `combo_sig_product__high_low_sequence_momentum__first_bar_return`: Y1:-0.123
- `first_30min_return`: Y1:-0.113
- `combo_sig_product__net_volume_flow__first_bar_return`: Y1:-0.101
- `early_body_momentum`: Y1:-0.099
- `combo_max__close_vs_open_range__early_body_momentum`: Y1:-0.095
- `vwap_close_divergence_trend`: Y1:-0.094
- `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression`: Y1:-0.093
- `combo_rank_max__volatility_expansion_trend_vector__bar_ret_0`: Y1:-0.091
- `morning_volume_weighted_momentum`: Y1:-0.091
- `combo_tri_min__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`: Y1:-0.091
- `volatility_expansion_trend_vector`: Y1:-0.085
- `combo_rel_diff__volatility_expansion_trend_vector__close_vs_open_range`: Y1:-0.084
- `combo_min__close_vs_open_range__early_body_momentum`: Y1:-0.079
- `micro_gap_trend_continuation`: Y1:-0.077
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.074
- `combo_sig_product__max_up_ret__first_bar_return`: Y1:-0.071
- `combo_sig_product__max_up_ret__bar_ret_0`: Y1:-0.069
- `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.069
- `combo_rank_max__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.069
- `combo_max__close_vs_open_range__max_down_ret`: Y1:-0.067
- `combo_rank_max__max_up_ret__bar_ret_0`: Y1:-0.065
- `combo_max__net_volume_flow__max_down_ret`: Y1:-0.064
- `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`: Y1:-0.062
- `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__body_size_progression`: Y1:-0.059
- `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`: Y1:-0.053
- `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment`: Y1:-0.052
- `combo_max__volatility_expansion_trend_vector__first_bar_sentiment`: Y1:-0.052
- `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector`: Y1:-0.050
- `num_up_bars`: Y1:-0.047
- `combo_max__opening_drive_thrust_ratio__early_body_momentum`: Y1:-0.047
- `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`: Y1:-0.047
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`: Y1:-0.047
- `combo_sig_product__net_volume_flow__max_down_ret`: Y1:-0.046
- `combo_min__net_volume_flow__first_bar_sentiment`: Y1:-0.044
- `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`: Y1:-0.041
- `combo_mean__close_vs_open_range__bar_ret_0`: Y1:-0.038
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Y1:-0.037
- `combo_mean__max_up_ret__first_bar_return`: Y1:-0.034
- `combo_mean__volatility_expansion_trend_vector__bar_ret_0`: Y1:-0.033
- `combo_mean__volatility_expansion_trend_vector__first_bar_return`: Y1:-0.033
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`: Y1:-0.032
- `vwap_trend_channel_slope`: Y1:-0.031
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Y1:-0.026
- `combo_sig_product__first_bar_sentiment__early_body_momentum`: Y1:-0.021
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__net_volume_flow__body_size_progression`: Y1:-0.019
- `combo_mean__volatility_expansion_trend_vector__max_down_ret`: Y1:-0.019
- `combo_max__first_bar_sentiment__high_low_sequence_momentum`: Y1:-0.016
- `combo_min__trend_bar_close_consistency__bar_ret_0`: Y1:-0.016
- `combo_min__trend_bar_close_consistency__first_bar_return`: Y1:-0.016
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression`: Y1:-0.014
- `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.013
- `combo_min__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:-0.012
- `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`: Y1:-0.012
- `first_bar_return`: Y1:-0.011
- `combo_rank_min__max_up_ret__first_bar_sentiment`: Y1:-0.011
- `combo_min__max_up_ret__first_bar_sentiment`: Y1:-0.011
- `combo_sig_product__max_up_ret__early_body_momentum`: Y1:-0.011
- `combo_rank_min__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.010
- `combo_min__first_bar_sentiment__bar_ret_0`: Y1:-0.009
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`: Y1:-0.006
- `combo_sig_product__opening_drive_thrust_ratio__max_down_ret`: Y1:-0.002
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__trend_bar_close_consistency`: Y1:-0.002
- `combo_rank_min__volatility_expansion_trend_vector__first_bar_sentiment`: Y1:-0.001
- `combo_min__net_volume_flow__bar_ret_0`: Y1:-0.001
- `combo_rank_min__max_up_ret__bar_ret_0`: Y1:-0.001
- `combo_rank_min__trend_bar_close_consistency__bar_ret_0`: Y1:-0.000
- `combo_mean__opening_drive_thrust_ratio__first_bar_return`: Y1:-0.000

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.1724 | N/A | +0.1724 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | TP | persistent | +0.1716 | N/A | +0.1716 | ∞ |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1654 | N/A | +0.1654 | ∞ |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1637 | N/A | +0.1637 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.1554 | N/A | +0.1554 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1495 | N/A | +0.1495 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | TP | persistent | +0.1488 | N/A | +0.1488 | ∞ |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1476 | N/A | +0.1476 | ∞ |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1425 | N/A | +0.1425 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1381 | N/A | +0.1381 | ∞ |
| `combo_mean__first_bar_sentiment__limit_down_proximity_early` | TP | persistent | +0.1358 | N/A | +0.1358 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1358 | N/A | +0.1358 | ∞ |
| `combo_rel_diff__rbreaker_buy_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1348 | N/A | +0.1348 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1343 | N/A | +0.1343 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1324 | N/A | +0.1324 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1286 | N/A | +0.1286 | ∞ |
| `combo_diff__limit_down_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1236 | N/A | +0.1236 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1224 | N/A | +0.1224 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1209 | N/A | +0.1209 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1205 | N/A | +0.1205 | ∞ |
| `combo_mean__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1186 | N/A | +0.1186 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1174 | N/A | +0.1174 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1170 | N/A | +0.1170 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1158 | N/A | +0.1158 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Median | persistent | +0.1154 | N/A | +0.1154 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1144 | N/A | +0.1144 | ∞ |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1135 | N/A | +0.1135 | ∞ |
| `combo_mean__first_bar_return__limit_down_proximity_early` | TP | persistent | +0.1120 | N/A | +0.1120 | ∞ |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1120 | N/A | +0.1120 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1093 | N/A | +0.1093 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1062 | N/A | +0.1062 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.1013 | N/A | +0.1013 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1013 | N/A | +0.1013 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1000 | N/A | +0.1000 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0980 | N/A | +0.0980 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.0961 | N/A | +0.0961 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0955 | N/A | +0.0955 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0944 | N/A | +0.0944 | ∞ |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | Median | persistent | +0.0909 | N/A | +0.0909 | ∞ |
| `combo_tri_max__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Median | persistent | +0.0898 | N/A | +0.0898 | ∞ |
| `combo_sig_product__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0896 | N/A | +0.0896 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0895 | N/A | +0.0895 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0892 | N/A | +0.0892 | ∞ |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0888 | N/A | +0.0888 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0877 | N/A | +0.0877 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0866 | N/A | +0.0866 | ∞ |
| `combo_max__bar_ret_0__limit_down_proximity_early` | Median | persistent | +0.0866 | N/A | +0.0866 | ∞ |
| `combo_max__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0852 | N/A | +0.0852 | ∞ |
| `combo_max__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0852 | N/A | +0.0852 | ∞ |
| `combo_rank_min__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.0850 | N/A | +0.0850 | ∞ |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0841 | N/A | +0.0841 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.0832 | N/A | +0.0832 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0827 | N/A | +0.0827 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0821 | N/A | +0.0821 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | Median | persistent | +0.0809 | N/A | +0.0809 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0766 | N/A | +0.0766 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | Median | persistent | +0.0737 | N/A | +0.0737 | ∞ |
| `combo_tri_mean__max_up_ret__star50_limit_proximity_early__first_bar_sentiment` | Median | persistent | +0.0719 | N/A | +0.0719 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__limit_down_proximity_early` | Median | persistent | +0.0712 | N/A | +0.0712 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0712 | N/A | +0.0712 | ∞ |
| `combo_min__rbreaker_buy_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0673 | N/A | +0.0673 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | Median | persistent | +0.0655 | N/A | +0.0655 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0646 | N/A | +0.0646 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0641 | N/A | +0.0641 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0623 | N/A | +0.0623 | ∞ |
| `combo_rel_diff__bar_body_rng_0__demark_setup_reversal_early` | Median | persistent | +0.0606 | N/A | +0.0606 | ∞ |
| `combo_sig_product__yesterday_first_30min_return__yesterday_early_trend` | Median | persistent | +0.0597 | N/A | +0.0597 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0593 | N/A | +0.0593 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0587 | N/A | +0.0587 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0586 | N/A | +0.0586 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0578 | N/A | +0.0578 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0574 | N/A | +0.0574 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0567 | N/A | +0.0567 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0556 | N/A | +0.0556 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0545 | N/A | +0.0545 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | Median | persistent | +0.0540 | N/A | +0.0540 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.0535 | N/A | +0.0535 | ∞ |
| `combo_diff__bar_body_rng_0__demark_setup_reversal_early` | Median | persistent | +0.0528 | N/A | +0.0528 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | persistent | +0.0510 | N/A | +0.0510 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0503 | N/A | +0.0503 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0487 | N/A | +0.0487 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0486 | N/A | +0.0486 | ∞ |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0431 | N/A | +0.0431 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Median | persistent | +0.0426 | N/A | +0.0426 | ∞ |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | persistent | +0.0307 | N/A | +0.0307 | ∞ |
| `combo_min__max_up_ret__first_bar_return` | TP | persistent | +0.0299 | N/A | +0.0299 | ∞ |
| `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0279 | N/A | +0.0279 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.0262 | N/A | +0.0262 | ∞ |
| `first_bar_return` | TP | persistent | +0.0226 | N/A | +0.0226 | ∞ |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0219 | N/A | +0.0219 | ∞ |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.0212 | N/A | +0.0212 | ∞ |
| `bar_body_rng_0` | Median | persistent | +0.0207 | N/A | +0.0207 | ∞ |
| `combo_rank_min__first_bar_return__volatility_expansion_trend_vector` | Median | persistent | +0.0154 | N/A | +0.0154 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_sentiment__first_bar_return` | Median | persistent | +0.0120 | N/A | +0.0120 | ∞ |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.0098 | N/A | +0.0098 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | Median | persistent | +0.0085 | N/A | +0.0085 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0069 | N/A | +0.0069 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | Median | persistent | +0.0056 | N/A | +0.0056 | ∞ |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Median | persistent | +0.0018 | N/A | +0.0018 | ∞ |
| `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_mean__first_bar_return__volume_weighted_price_position` | FP | immediate | -0.0010 | N/A | -0.0010 | ∞ |
| `combo_min__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0016 | N/A | -0.0016 | ∞ |
| `combo_min__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0026 | N/A | -0.0026 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0029 | N/A | -0.0029 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | FP | immediate | -0.0066 | N/A | -0.0066 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | FP | immediate | -0.0067 | N/A | -0.0067 | ∞ |
| `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance` | FP | immediate | -0.0102 | N/A | -0.0102 | ∞ |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | FP | immediate | -0.0113 | N/A | -0.0113 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0` | FP | immediate | -0.0120 | N/A | -0.0120 | ∞ |
| `combo_sig_product__max_up_ret__bar_ret_0` | FP | immediate | -0.0120 | N/A | -0.0120 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | FP | immediate | -0.0120 | N/A | -0.0120 | ∞ |
| `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return` | FP | immediate | -0.0121 | N/A | -0.0121 | ∞ |
| `combo_max__first_bar_sentiment__first_bar_return` | FP | immediate | -0.0145 | N/A | -0.0145 | ∞ |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0148 | N/A | -0.0148 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | FP | immediate | -0.0163 | N/A | -0.0163 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0177 | N/A | -0.0177 | ∞ |
| `combo_min__bar_body_rng_0__impulse_bar_dominance` | FP | immediate | -0.0179 | N/A | -0.0179 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | FP | immediate | -0.0192 | N/A | -0.0192 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | FP | immediate | -0.0208 | N/A | -0.0208 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | FP | immediate | -0.0221 | N/A | -0.0221 | ∞ |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | FP | immediate | -0.0230 | N/A | -0.0230 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0232 | N/A | -0.0232 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.0238 | N/A | -0.0238 | ∞ |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | FP | immediate | -0.0248 | N/A | -0.0248 | ∞ |
| `combo_rank_max__bar_body_rng_0__volume_weighted_price_position` | FP | immediate | -0.0256 | N/A | -0.0256 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | FP | immediate | -0.0265 | N/A | -0.0265 | ∞ |
| `combo_min__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0303 | N/A | -0.0303 | ∞ |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | FP | immediate | -0.0318 | N/A | -0.0318 | ∞ |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0325 | N/A | -0.0325 | ∞ |
| `combo_min__first_bar_sentiment__volatility_expansion_trend_vector` | FP | immediate | -0.0329 | N/A | -0.0329 | ∞ |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | FP | immediate | -0.0381 | N/A | -0.0381 | ∞ |
| `combo_rank_min__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0414 | N/A | -0.0414 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0421 | N/A | -0.0421 | ∞ |
| `combo_mean__max_up_ret__first_bar_sentiment` | FP | immediate | -0.0430 | N/A | -0.0430 | ∞ |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | FP | immediate | -0.0445 | N/A | -0.0445 | ∞ |
| `opening_drive_thrust_ratio` | FP | immediate | -0.0464 | N/A | -0.0464 | ∞ |
| `combo_max__first_bar_return__impulse_bar_dominance` | FP | immediate | -0.0491 | N/A | -0.0491 | ∞ |
| `combo_max__bar_ret_0__impulse_bar_dominance` | FP | immediate | -0.0491 | N/A | -0.0491 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0527 | N/A | -0.0527 | ∞ |
| `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector` | FP | immediate | -0.0561 | N/A | -0.0561 | ∞ |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0563 | N/A | -0.0563 | ∞ |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0570 | N/A | -0.0570 | ∞ |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0572 | N/A | -0.0572 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0595 | N/A | -0.0595 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | FP | immediate | -0.0653 | N/A | -0.0653 | ∞ |
| `net_volume_flow` | FP | immediate | -0.0663 | N/A | -0.0663 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0689 | N/A | -0.0689 | ∞ |
| `combo_tri_max__max_up_ret__first_bar_sentiment__bar_body_rng_0` | FP | immediate | -0.0730 | N/A | -0.0730 | ∞ |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | immediate | -0.0737 | N/A | -0.0737 | ∞ |
| `shaved_bar_trend_conviction` | FP | immediate | -0.0741 | N/A | -0.0741 | ∞ |
| `combo_rank_max__first_bar_return__volatility_expansion_trend_vector` | FP | immediate | -0.0746 | N/A | -0.0746 | ∞ |
| `max_up_ret` | FP | immediate | -0.0753 | N/A | -0.0753 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | FP | immediate | -0.0770 | N/A | -0.0770 | ∞ |
| `combo_max__max_up_ret__bar_body_rng_0` | FP | immediate | -0.0771 | N/A | -0.0771 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | FP | immediate | -0.0811 | N/A | -0.0811 | ∞ |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | FP | immediate | -0.0815 | N/A | -0.0815 | ∞ |
| `combo_max__first_bar_return__volatility_expansion_trend_vector` | FP | immediate | -0.0816 | N/A | -0.0816 | ∞ |
| `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector` | FP | immediate | -0.0820 | N/A | -0.0820 | ∞ |
| `close_vs_open_range` | FP | immediate | -0.0831 | N/A | -0.0831 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0833 | N/A | -0.0833 | ∞ |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | FP | immediate | -0.0835 | N/A | -0.0835 | ∞ |
| `combo_max__first_bar_sentiment__volatility_expansion_trend_vector` | FP | immediate | -0.0844 | N/A | -0.0844 | ∞ |
| `combo_mean__max_up_ret__impulse_bar_dominance` | FP | immediate | -0.0845 | N/A | -0.0845 | ∞ |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0854 | N/A | -0.0854 | ∞ |
| `combo_rank_max__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0913 | N/A | -0.0913 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.0930 | N/A | -0.0930 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early` | FP | immediate | -0.0939 | N/A | -0.0939 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | FP | immediate | -0.1027 | N/A | -0.1027 | ∞ |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.1035 | N/A | -0.1035 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0` | FP | immediate | -0.1064 | N/A | -0.1064 | ∞ |
| `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position` | FP | immediate | -0.1064 | N/A | -0.1064 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | FP | immediate | -0.1070 | N/A | -0.1070 | ∞ |
| `combo_max__impulse_bar_dominance__volatility_expansion_trend_vector` | FP | immediate | -0.1105 | N/A | -0.1105 | ∞ |
| `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector` | FP | immediate | -0.1117 | N/A | -0.1117 | ∞ |
| `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector` | FP | immediate | -0.1124 | N/A | -0.1124 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | FP | immediate | -0.1124 | N/A | -0.1124 | ∞ |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | FP | immediate | -0.1166 | N/A | -0.1166 | ∞ |
| `trend_bar_close_consistency` | FP | immediate | -0.1362 | N/A | -0.1362 | ∞ |

**Decay distribution**: immediate=79, fast(1-2y)=0, gradual=0, persistent=99

**FP decay trajectories:**

- `trend_bar_close_consistency`: Y1:-0.136
- `combo_rank_min__max_up_ret__impulse_bar_dominance`: Y1:-0.117
- `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.112
- `combo_min__impulse_bar_dominance__volatility_expansion_trend_vector`: Y1:-0.112
- `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector`: Y1:-0.112
- `combo_max__impulse_bar_dominance__volatility_expansion_trend_vector`: Y1:-0.110
- `combo_sig_product__opening_drive_thrust_ratio__first_bar_return`: Y1:-0.107
- `combo_ratio__volatility_expansion_trend_vector__volume_weighted_price_position`: Y1:-0.106
- `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0`: Y1:-0.106
- `combo_max__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.104
- `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.103
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Y1:-0.094
- `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.093
- `combo_rank_max__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.091
- `combo_rank_min__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.085
- `combo_mean__max_up_ret__impulse_bar_dominance`: Y1:-0.084
- `combo_max__first_bar_sentiment__volatility_expansion_trend_vector`: Y1:-0.084
- `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`: Y1:-0.084
- `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.083
- `close_vs_open_range`: Y1:-0.083
- `combo_mean__volume_weighted_price_position__volatility_expansion_trend_vector`: Y1:-0.082
- `combo_max__first_bar_return__volatility_expansion_trend_vector`: Y1:-0.082
- `combo_max__bar_ret_0__volatility_expansion_trend_vector`: Y1:-0.081
- `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.081
- `combo_max__max_up_ret__bar_body_rng_0`: Y1:-0.077
- `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`: Y1:-0.077
- `max_up_ret`: Y1:-0.075
- `combo_rank_max__first_bar_return__volatility_expansion_trend_vector`: Y1:-0.075
- `shaved_bar_trend_conviction`: Y1:-0.074
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:-0.074
- `combo_tri_max__max_up_ret__first_bar_sentiment__bar_body_rng_0`: Y1:-0.073
- `combo_min__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.069
- `net_volume_flow`: Y1:-0.066
- `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`: Y1:-0.065
- `combo_rank_max__opening_drive_thrust_ratio__max_up_ret`: Y1:-0.060
- `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.057
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:-0.057
- `combo_rank_max__max_up_ret__bar_body_rng_0`: Y1:-0.056
- `combo_rank_min__volume_weighted_price_position__volatility_expansion_trend_vector`: Y1:-0.056
- `combo_rank_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`: Y1:-0.053
- `combo_max__first_bar_return__impulse_bar_dominance`: Y1:-0.049
- `combo_max__bar_ret_0__impulse_bar_dominance`: Y1:-0.049
- `opening_drive_thrust_ratio`: Y1:-0.046
- `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`: Y1:-0.044
- `combo_mean__max_up_ret__first_bar_sentiment`: Y1:-0.043
- `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`: Y1:-0.042
- `combo_rank_min__max_up_ret__volume_weighted_price_position`: Y1:-0.041
- `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`: Y1:-0.038
- `combo_min__first_bar_sentiment__volatility_expansion_trend_vector`: Y1:-0.033
- `combo_sig_product__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.033
- `combo_diff__max_up_ret__demark_setup_reversal_early`: Y1:-0.032
- `combo_min__max_up_ret__volume_weighted_price_position`: Y1:-0.030
- `combo_max__opening_drive_thrust_ratio__bar_ret_0`: Y1:-0.026
- `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.026
- `combo_max__bar_body_rng_0__impulse_bar_dominance`: Y1:-0.025
- `combo_rank_max__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.024
- `combo_max__opening_drive_thrust_ratio__bar_body_rng_0`: Y1:-0.023
- `combo_mean__bar_body_rng_0__impulse_bar_dominance`: Y1:-0.023
- `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`: Y1:-0.022
- `combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return`: Y1:-0.021
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`: Y1:-0.019
- `combo_min__bar_body_rng_0__impulse_bar_dominance`: Y1:-0.018
- `combo_rank_max__max_up_ret__first_bar_sentiment`: Y1:-0.018
- `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Y1:-0.016
- `combo_sig_product__max_up_ret__bar_body_rng_0`: Y1:-0.015
- `combo_max__first_bar_sentiment__first_bar_return`: Y1:-0.015
- `combo_tri_mean__max_up_ret__bar_body_rng_0__first_bar_return`: Y1:-0.012
- `combo_sig_product__max_up_ret__first_bar_return`: Y1:-0.012
- `combo_sig_product__max_up_ret__bar_ret_0`: Y1:-0.012
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_sentiment__bar_body_rng_0`: Y1:-0.012
- `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`: Y1:-0.011
- `combo_rank_min__limit_down_proximity_early__impulse_bar_dominance`: Y1:-0.010
- `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`: Y1:-0.007
- `combo_max__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:-0.007
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`: Y1:-0.003
- `combo_min__max_up_ret__first_bar_sentiment`: Y1:-0.003
- `combo_min__bar_body_rng_0__volume_weighted_price_position`: Y1:-0.002
- `combo_mean__first_bar_return__volume_weighted_price_position`: Y1:-0.001
- `combo_sig_product__bar_body_rng_0__volatility_expansion_trend_vector`: Y1:-0.001

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.739±0.042 | 0.727±0.013 | 20% | USEFUL |
| ic_ir | 0.648±0.118 | 0.612±0.065 | 31% | USEFUL |
| p_value | 0.002±0.005 | 0.000±0.000 | 0% | USEFUL |
| max_corr | 0.906±0.104 | 0.674±0.394 | 94% | USELESS |
| deflated_ic | 0.199±0.034 | 0.239±0.035 | 36% | USEFUL |
| overall_ic | 0.199±0.034 | 0.238±0.035 | 36% | USEFUL |
| raw_ic | 0.091±0.012 | 0.102±0.007 | 23% | USEFUL |

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.723±0.040 | 0.719±0.046 | 88% | USELESS |
| ic_ir | 0.596±0.111 | 0.609±0.131 | 99% | USELESS |
| p_value | 0.001±0.004 | 0.002±0.006 | 79% | WEAK |
| max_corr | 0.892±0.132 | 0.896±0.074 | 31% | USEFUL |
| deflated_ic | 0.193±0.034 | 0.200±0.038 | 86% | USELESS |
| overall_ic | 0.193±0.034 | 0.201±0.038 | 86% | USELESS |
| raw_ic | 0.109±0.018 | 0.113±0.016 | 72% | WEAK |

### 159915ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.746±0.042 | 0.768±0.065 | 74% | WEAK |
| ic_ir | 0.673±0.139 | 0.766±0.217 | 75% | WEAK |
| p_value | 0.001±0.004 | 0.000±0.001 | 12% | USEFUL |
| max_corr | 0.910±0.067 | 0.918±0.070 | 82% | USELESS |
| deflated_ic | 0.222±0.039 | 0.257±0.057 | 54% | WEAK |
| overall_ic | 0.222±0.038 | 0.256±0.057 | 54% | WEAK |
| raw_ic | 0.118±0.014 | 0.131±0.016 | 46% | USEFUL |

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

**7-Year Jackknife**: 9/20 top rejects are profitable (45%)

- `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_min__opening_drive_thrust_ratio__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2339, Lock IC=+0.0881, Sharpe=+1.7265
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`: Train IC=+0.2184, Lock IC=+0.0565, Sharpe=+0.2974

**B2 Rolling Guard**: 3/20 top rejects are profitable (15%)

- `combo_sig_product__volume_weighted_momentum_acceleration__double_bottom_bull_flag_early`: Train IC=+0.1791, Lock IC=+0.1113, Sharpe=+1.6232
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

**B4 Correlation Gate**: 2/20 top rejects are profitable (10%)

- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2557, Lock IC=+0.0706, Sharpe=+0.8062
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2573, Lock IC=+0.0571, Sharpe=+0.3372

### 159915ETF — `single`

**7-Year Jackknife**: 5/20 top rejects are profitable (25%)

- `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2171, Lock IC=+0.1225, Sharpe=+1.4450
- `combo_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.1849, Lock IC=+0.1624, Sharpe=+0.7707
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2085, Lock IC=+0.0941, Sharpe=+0.6495

**B2 Rolling Guard**: 15/20 top rejects are profitable (75%)

- `combo_max__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.1730, Lock IC=+0.1155, Sharpe=+1.0583
- `combo_min__first_bar_sentiment__demark_setup_reversal_early`: Train IC=+0.2140, Lock IC=+0.0901, Sharpe=+0.9586
- `combo_min__demark_setup_reversal_early__impulse_bar_dominance`: Train IC=+0.1757, Lock IC=+0.1511, Sharpe=+0.7444

**Temporal Validation Gate**: 3/20 top rejects are profitable (15%)

- `combo_rank_min__demark_setup_reversal_early__late_bar_momentum`: Train IC=+0.1969, Lock IC=+0.1750, Sharpe=+0.7632
- `combo_abs_diff__limit_down_proximity_early__impulse_bar_dominance`: Train IC=+0.1863, Lock IC=+0.0582, Sharpe=+0.5871
- `combo_abs_diff__rbreaker_buy_setup_proximity_early__impulse_bar_dominance`: Train IC=+0.1863, Lock IC=+0.0582, Sharpe=+0.5871

**BH-FDR Gate**: 1/1 top rejects are profitable (100%)

- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Sharpe=+0.2891

**B3 Composite Floor**: 2/20 top rejects are profitable (10%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2636, Lock IC=+0.0919, Sharpe=+0.8492
- `combo_tri_median__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.2387, Lock IC=+0.0969, Sharpe=+0.2227

**B6 Temporal Stability Gate**: 11/20 top rejects are profitable (55%)

- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3177, Lock IC=+0.0619, Sharpe=+1.2230
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.3527, Lock IC=+0.0637, Sharpe=+0.7890
- `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`: Train IC=+0.3082, Lock IC=+0.0585, Sharpe=+0.4764

**B4 Correlation Gate**: 13/20 top rejects are profitable (65%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3290, Lock IC=+0.0740, Sharpe=+2.5285
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.3014, Lock IC=+0.1495, Sharpe=+1.8753
- `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`: Train IC=+0.3095, Lock IC=+0.0868, Sharpe=+1.5647

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1021 | 78 | 54 | 12 | 12 | 69% | 15% |
| B2 Rolling Guard | 103 | 78 | 52 | 11 | 15 | 67% | 19% |
| Temporal Validation Gate | 77 | 77 | 50 | 5 | 22 | 65% | 29% |
| BH-FDR Gate | 2 | 2 | 2 | 0 | 0 | 100% | 0% |
| B3 Composite Floor | 7 | 7 | 4 | 3 | 0 | 57% | 0% |
| B6 Yearly IC CV Gate | 1 | 1 | 0 | 1 | 0 | 0% | 0% |
| B6 Quality Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 214 | 78 | 73 | 3 | 2 | 94% | 3% |

**Temporal Validation Gate** — top TP casualties:
- `ema12_dist`: Train IC=+0.0434, Lock IC=+0.1158, Sharpe=+3.3549
- `sma10_dist`: Train IC=+0.0453, Lock IC=+0.1136, Sharpe=+2.6363
- `sma20_dist`: Train IC=+0.0648, Lock IC=+0.1054, Sharpe=+2.5915

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1921 | 78 | 36 | 11 | 31 | 46% | 40% |
| B2 Rolling Guard | 256 | 78 | 60 | 6 | 12 | 77% | 15% |
| Temporal Validation Gate | 101 | 78 | 18 | 52 | 8 | 23% | 10% |
| BH-FDR Gate | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B3 Composite Floor | 56 | 56 | 16 | 32 | 8 | 29% | 14% |
| B6 Yearly IC CV Gate | 10 | 10 | 3 | 2 | 5 | 30% | 50% |
| B6 Temporal Stability Gate | 172 | 78 | 51 | 6 | 21 | 65% | 27% |
| B4 Correlation Gate | 371 | 78 | 45 | 22 | 11 | 58% | 14% |

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
| 7-Year Jackknife | 1079 | 78 | 43 | 22 | 13 | 55% | 17% |
| B2 Rolling Guard | 179 | 78 | 37 | 16 | 25 | 47% | 32% |
| Temporal Validation Gate | 42 | 42 | 25 | 9 | 8 | 60% | 19% |
| BH-FDR Gate | 1 | 1 | 0 | 0 | 1 | 0% | 100% |
| B3 Composite Floor | 70 | 70 | 17 | 44 | 9 | 24% | 13% |
| B6 Yearly IC CV Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B6 Temporal Stability Gate | 64 | 64 | 4 | 40 | 20 | 6% | 31% |
| B4 Correlation Gate | 273 | 78 | 16 | 25 | 37 | 21% | 47% |

**B2 Rolling Guard** — top TP casualties:
- `combo_rel_diff__limit_down_proximity_early__late_bar_momentum`: Train IC=+0.0936, Lock IC=+0.2260, Sharpe=+2.7295
- `combo_rel_diff__rbreaker_buy_setup_proximity_early__late_bar_momentum`: Train IC=+0.0936, Lock IC=+0.2260, Sharpe=+2.7295
- `yesterday_day_vwap_dev`: Train IC=+0.1158, Lock IC=+0.1282, Sharpe=+2.5172

**BH-FDR Gate** — top TP casualties:
- `volume_trend_intraday`: Train IC=+0.0820, Lock IC=+0.1004, Sharpe=+0.2891

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`: Train IC=+0.3177, Lock IC=+0.0619, Sharpe=+1.2230
- `combo_min__max_up_ret__star50_limit_proximity_early`: Train IC=+0.2573, Lock IC=+0.0958, Sharpe=+1.1483
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2821, Lock IC=+0.1124, Sharpe=+1.0660

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.2975, Lock IC=+0.1253, Sharpe=+2.7133
- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3290, Lock IC=+0.0740, Sharpe=+2.5285
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.3014, Lock IC=+0.1495, Sharpe=+1.8753

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (77 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 64 | 50 | 37 | 13 | 0 | 74% | 26% |
| recency_ratio >= 2.5 (late-concentrated) | 7 | 7 | 7 | 0 | 0 | 100% | 0% |

### 500ETF — `single` (101 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 97 | 50 | 2 | 2 | 46 | 4% | 4% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 4 | 0 | 0 | 100% | 0% |

### 159915ETF — `single` (42 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 31 | 31 | 16 | 7 | 8 | 52% | 23% |
| recency_ratio >= 2.5 (late-concentrated) | 11 | 11 | 9 | 1 | 1 | 82% | 9% |

**Top TP killed by recency_ratio cap:**
- `volume_surge_direction`: Train IC=+0.1617, Lock IC=+0.1277, Sharpe=+2.7834

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `ic_cv`: FP is higher (d=+1.77). Threshold 0.498 → 97% accuracy.
- `n_negative_years`: FP is higher (d=+0.90). Threshold 0.000 → 96% accuracy.
- `n_negative_regimes`: FP is lower (d=-0.64). Threshold 0.000 → 96% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-0.61). Threshold 0.025 → 96% accuracy.
- `half_ratio`: FP is higher (d=+0.54). Threshold 0.454 → 96% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/112
- Decaying signal (half ratio < 0.3): 0/112
- Weak component (CV > 2.0): 1/112
- Regime-dependent (≥2 negative regimes): 0/112

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `half_ratio`: FP is higher (d=+0.62). Threshold 0.578 → 73% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/71
- Decaying signal (half ratio < 0.3): 0/71
- Weak component (CV > 2.0): 0/71
- Regime-dependent (≥2 negative regimes): 0/71

### 159915ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `recency_ratio`: FP is higher (d=+0.98). Threshold 0.790 → 73% accuracy.
- `half_ratio`: FP is higher (d=+0.92). Threshold 0.797 → 72% accuracy.
- `ic_cv`: FP is higher (d=+0.70). Threshold 0.298 → 67% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/79
- Decaying signal (half ratio < 0.3): 0/79
- Weak component (CV > 2.0): 0/79
- Regime-dependent (≥2 negative regimes): 0/79

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `volume_surge_direction` | 24 | 0 | 24 | 100% | ⚠ TOXIC |
| `high_low_sequence_momentum` | 2 | 0 | 2 | 100% |  |
| `early_body_momentum` | 5 | 0 | 5 | 100% | ⚠ TOXIC |
| `max_up_ret` | 81 | 8 | 89 | 91% | ⚠ TOXIC |
| `impulse_bar_dominance` | 14 | 2 | 16 | 88% | ⚠ TOXIC |
| `volatility_expansion_trend_vector` | 37 | 6 | 43 | 86% | ⚠ TOXIC |
| `volume_weighted_price_position` | 45 | 8 | 53 | 85% | ⚠ TOXIC |
| `first_bar_return` | 51 | 10 | 61 | 84% | ⚠ TOXIC |
| `bar_ret_0` | 35 | 7 | 42 | 83% | ⚠ TOXIC |
| `body_size_progression` | 5 | 1 | 6 | 83% | ⚠ TOXIC |
| `net_volume_flow` | 10 | 2 | 12 | 83% | ⚠ TOXIC |
| `opening_drive_thrust_ratio` | 88 | 21 | 109 | 81% | ⚠ TOXIC |
| `trend_bar_close_consistency` | 9 | 3 | 12 | 75% |  |
| `first_bar_sentiment` | 29 | 10 | 39 | 74% |  |
| `bar_body_rng_0` | 48 | 22 | 70 | 69% |  |
| `smooth_momentum_structure` | 2 | 1 | 3 | 67% |  |
| `close_vs_open_range` | 6 | 4 | 10 | 60% |  |
| `demark_setup_reversal_early` | 3 | 2 | 5 | 60% |  |
| `max_down_ret` | 7 | 5 | 12 | 58% |  |
| `double_bottom_bull_flag_early` | 1 | 1 | 2 | 50% |  |
| `volume_weighted_momentum_acceleration` | 4 | 4 | 8 | 50% |  |
| `rbreaker_sell_setup_proximity_early` | 22 | 33 | 55 | 40% |  |
| `rbreaker_buy_setup_proximity_early` | 2 | 6 | 8 | 25% |  |
| `limit_down_proximity_early` | 3 | 13 | 16 | 19% |  |
| `star50_limit_proximity_early` | 5 | 34 | 39 | 13% |  |
| `yesterday_first_30min_return` | 0 | 5 | 5 | 0% |  |
| `trend_day_regime_conviction` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=128, TP=58, FP rate=69%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=8, TP=5, FP rate=62%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=65, TP=25, FP rate=72%

