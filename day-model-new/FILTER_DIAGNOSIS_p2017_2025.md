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

> **Caveat**: Lockbox spans ~2.0y. Sharpe-based TP/Median split has high variance at this horizon; some Median features may flip to TP with more data.

| ETF | Side | Admitted | Clusters | Cluster Sizes | Avg Sil | FP | Median | TP | FP Rate | Prod Score |
| :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 35 | 14 | `[5, 4, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1]` | 0.2806 | 20 | 11 | 4 | 57% | 0.15 |
| 500ETF | single | 100 | 44 | `[6, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, ... (44 clusters)]` | 0.2085 | 2 | 74 | 24 | 2% | 0.40 |
| 159915ETF | single | 125 | 49 | `[9, 6, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, ... (49 clusters)]` | 0.3293 | 0 | 28 | 97 | 0% | 0.75 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=20, TP=4)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| weak_link_cv | 1.146 | 1.930 | 1.209 | 2.001 | -1.83 | 0.935 | 78% |
| half_ratio | 1.611 | 1.082 | 1.514 | 1.025 | +1.78 | 1.087 | 92% |
| ic_std_across_regimes | 0.055 | 0.074 | 0.055 | 0.069 | -1.47 | 0.035 | 79% |
| recency_ratio | 1.233 | 0.983 | 1.129 | 0.951 | +0.59 | 0.654 | 92% |
| n_negative_regimes | 0.050 | 0.250 | 0.000 | 0.000 | -0.58 | 0.000 | 79% |
| ic_cv | 0.832 | 0.783 | 0.870 | 0.790 | +0.54 | 0.630 | 79% |
| n_negative_years | 0.650 | 0.500 | 1.000 | 0.500 | +0.28 | 0.000 | 79% |

### 500ETF — `single` (FP=2, TP=24)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recency_ratio | 0.720 | 0.545 | 0.720 | 0.507 | +1.73 | 0.772 | 92% |
| n_negative_regimes | 0.000 | 0.500 | 0.000 | 0.500 | -1.41 | 1.000 | 88% |
| half_ratio | 0.761 | 0.629 | 0.761 | 0.589 | +1.19 | 0.950 | 88% |
| ic_std_across_regimes | 0.060 | 0.073 | 0.060 | 0.072 | -1.18 | 0.092 | 88% |
| weak_link_cv | 0.421 | 0.465 | 0.421 | 0.459 | -0.98 | 0.547 | 88% |
| ic_cv | 0.355 | 0.397 | 0.355 | 0.399 | -0.79 | 0.509 | 88% |
| n_negative_years | 0.000 | 0.000 | 0.000 | 0.000 | +0.00 | 0.000 | 88% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0136, Sharpe=-1.9227)
- Admission: Train IC=+0.2095, Deflated=+0.2097, IR=0.71, Mono=0.75, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.115 | 2017: +0.115 | 2018: +0.285 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.249 | 2024: +0.186 | 2025: +0.049 | 2026: -0.298
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.68
- Early IC=+0.1311, Recent IC=+0.0894, 1st-half IC=+0.0925, 2nd-half IC=+0.0860, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.091, Q3_mid=+0.051, Q4=+0.072, Q5_high_vol=+0.160

**`max_up_ret`** (Lock IC=-0.0463, Sharpe=-1.8589)
- Admission: Train IC=+0.2051, Deflated=+0.2056, IR=0.62, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.084 | 2017: -0.040 | 2018: +0.136 | 2019: +0.049 | 2020: +0.048 | 2021: +0.166 | 2022: +0.013 | 2023: +0.149 | 2024: +0.056 | 2025: +0.033 | 2026: -0.152
- Yearly Tail ICs:   2015: +0.070 | 2016: +0.035 | 2017: +0.015 | 2018: +0.265 | 2019: +0.208 | 2020: +0.110 | 2021: +0.462 | 2022: +0.221 | 2023: +0.279 | 2024: +0.213 | 2025: -0.013 | 2026: -0.315
- IC CV=0.94, Neg years (linear/tail)=1/0 of 8, Half ratio=2.29, Recency ratio=2.13
- Early IC=+0.0481, Recent IC=+0.1023, 1st-half IC=+0.0452, 2nd-half IC=+0.1036, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.064, Q3_mid=+0.014, Q4=+0.050, Q5_high_vol=+0.186

**`combo_max__bar_ret_0__morning_volume_weighted_momentum`** (Lock IC=-0.0225, Sharpe=-1.7645)
- Admission: Train IC=+0.2023, Deflated=+0.2029, IR=0.63, Mono=0.72, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.103 | 2016: +0.046 | 2017: -0.042 | 2018: +0.142 | 2019: +0.030 | 2020: +0.033 | 2021: +0.145 | 2022: +0.036 | 2023: +0.148 | 2024: +0.066 | 2025: +0.101 | 2026: -0.198
- Yearly Tail ICs:   2015: +0.179 | 2016: -0.040 | 2017: -0.032 | 2018: +0.250 | 2019: +0.161 | 2020: +0.187 | 2021: +0.266 | 2022: +0.193 | 2023: +0.290 | 2024: +0.279 | 2025: +0.140 | 2026: -0.444
- IC CV=0.93, Neg years (linear/tail)=1/1 of 8, Half ratio=2.30, Recency ratio=2.14
- Early IC=+0.0500, Recent IC=+0.1070, 1st-half IC=+0.0460, 2nd-half IC=+0.1057, Neg regimes=0/5
- Weak component: `morning_volume_weighted_momentum` (CV=1.45, neg years=1)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.063, Q3_mid=+0.048, Q4=+0.063, Q5_high_vol=+0.152

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0061, Sharpe=-1.6781)
- Admission: Train IC=+0.2384, Deflated=+0.2392, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.066 | 2017: -0.010 | 2018: +0.230 | 2019: +0.070 | 2020: +0.021 | 2021: +0.179 | 2022: +0.034 | 2023: +0.162 | 2024: +0.011 | 2025: +0.094 | 2026: -0.143
- Yearly Tail ICs:   2015: +0.014 | 2016: +0.099 | 2017: +0.167 | 2018: +0.271 | 2019: +0.324 | 2020: +0.182 | 2021: +0.426 | 2022: +0.281 | 2023: +0.376 | 2024: -0.055 | 2025: -0.049 | 2026: -0.194
- IC CV=0.97, Neg years (linear/tail)=1/1 of 8, Half ratio=1.37, Recency ratio=0.79
- Early IC=+0.1102, Recent IC=+0.0866, 1st-half IC=+0.0770, 2nd-half IC=+0.1057, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.102, Q3_mid=+0.061, Q4=+0.072, Q5_high_vol=+0.161

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0365, Sharpe=-1.6583)
- Admission: Train IC=+0.2523, Deflated=+0.2529, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.080 | 2017: -0.034 | 2018: +0.160 | 2019: +0.072 | 2020: +0.053 | 2021: +0.175 | 2022: +0.015 | 2023: +0.160 | 2024: +0.064 | 2025: +0.057 | 2026: -0.166
- Yearly Tail ICs:   2015: -0.023 | 2016: +0.177 | 2017: +0.157 | 2018: +0.341 | 2019: +0.358 | 2020: +0.125 | 2021: +0.374 | 2022: +0.208 | 2023: +0.245 | 2024: +0.290 | 2025: -0.131 | 2026: -0.344
- IC CV=0.85, Neg years (linear/tail)=1/0 of 8, Half ratio=1.81, Recency ratio=1.78
- Early IC=+0.0627, Recent IC=+0.1118, 1st-half IC=+0.0615, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.085, Q3_mid=+0.028, Q4=+0.054, Q5_high_vol=+0.212

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`** (Lock IC=-0.0457, Sharpe=-1.6553)
- Admission: Train IC=+0.1856, Deflated=+0.1856, IR=0.69, Mono=0.72, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.088 | 2016: +0.097 | 2017: -0.016 | 2018: +0.146 | 2019: +0.053 | 2020: +0.049 | 2021: +0.164 | 2022: -0.008 | 2023: +0.157 | 2024: +0.055 | 2025: +0.047 | 2026: -0.166
- Yearly Tail ICs:   2015: +0.032 | 2016: +0.269 | 2017: +0.061 | 2018: +0.307 | 2019: +0.077 | 2020: +0.250 | 2021: +0.334 | 2022: +0.090 | 2023: +0.319 | 2024: +0.203 | 2025: -0.058 | 2026: -0.370
- IC CV=0.90, Neg years (linear/tail)=2/0 of 8, Half ratio=1.76, Recency ratio=1.64
- Early IC=+0.0646, Recent IC=+0.1062, 1st-half IC=+0.0552, 2nd-half IC=+0.0971, Neg regimes=0/5
- Weak component: `volume_concentration` (CV=1.19, neg years=1)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.072, Q3_mid=+0.033, Q4=+0.051, Q5_high_vol=+0.179

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0157, Sharpe=-1.4403)
- Admission: Train IC=+0.2163, Deflated=+0.2166, IR=0.69, Mono=0.73, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.096 | 2017: +0.025 | 2018: +0.190 | 2019: +0.080 | 2020: +0.016 | 2021: +0.173 | 2022: +0.029 | 2023: +0.173 | 2024: +0.061 | 2025: +0.054 | 2026: -0.114
- Yearly Tail ICs:   2015: +0.028 | 2016: +0.135 | 2017: +0.078 | 2018: +0.299 | 2019: +0.165 | 2020: +0.051 | 2021: +0.304 | 2022: +0.247 | 2023: +0.406 | 2024: +0.179 | 2025: -0.004 | 2026: -0.080
- IC CV=0.74, Neg years (linear/tail)=0/0 of 8, Half ratio=1.48, Recency ratio=1.09
- Early IC=+0.1077, Recent IC=+0.1173, 1st-half IC=+0.0774, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.087, Q3_mid=+0.043, Q4=+0.061, Q5_high_vol=+0.205

**`combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0344, Sharpe=-1.3884)
- Admission: Train IC=+0.2318, Deflated=+0.2326, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.038 | 2017: +0.041 | 2018: +0.151 | 2019: +0.039 | 2020: +0.015 | 2021: +0.189 | 2022: +0.041 | 2023: +0.200 | 2024: +0.042 | 2025: +0.105 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.160 | 2017: +0.196 | 2018: +0.484 | 2019: +0.257 | 2020: +0.182 | 2021: +0.316 | 2022: +0.224 | 2023: +0.183 | 2024: +0.129 | 2025: +0.146 | 2026: -0.463
- IC CV=0.80, Neg years (linear/tail)=0/0 of 8, Half ratio=2.24, Recency ratio=1.26
- Early IC=+0.0959, Recent IC=+0.1209, 1st-half IC=+0.0548, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.116, Q3_mid=+0.040, Q4=+0.035, Q5_high_vol=+0.185

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0223, Sharpe=-1.3571)
- Admission: Train IC=+0.2655, Deflated=+0.2657, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.091 | 2017: +0.020 | 2018: +0.182 | 2019: +0.073 | 2020: -0.000 | 2021: +0.133 | 2022: +0.045 | 2023: +0.170 | 2024: +0.055 | 2025: +0.022 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.099 | 2017: +0.153 | 2018: +0.375 | 2019: +0.259 | 2020: +0.087 | 2021: +0.371 | 2022: +0.168 | 2023: +0.386 | 2024: +0.231 | 2025: -0.048 | 2026: -0.016
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.46, Recency ratio=1.12
- Early IC=+0.1009, Recent IC=+0.1127, 1st-half IC=+0.0718, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.079, Q3_mid=+0.041, Q4=+0.072, Q5_high_vol=+0.177

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0223, Sharpe=-1.3181)
- Admission: Train IC=+0.1963, Deflated=+0.1971, IR=0.71, Mono=0.75, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.049 | 2016: +0.024 | 2017: +0.045 | 2018: +0.174 | 2019: +0.086 | 2020: +0.054 | 2021: +0.154 | 2022: +0.033 | 2023: +0.139 | 2024: +0.030 | 2025: +0.050 | 2026: -0.130
- Yearly Tail ICs:   2015: -0.123 | 2016: +0.042 | 2017: +0.026 | 2018: +0.339 | 2019: +0.227 | 2020: +0.092 | 2021: +0.383 | 2022: +0.260 | 2023: +0.301 | 2024: +0.085 | 2025: +0.083 | 2026: -0.315
- IC CV=0.61, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=0.77
- Early IC=+0.1096, Recent IC=+0.0845, 1st-half IC=+0.0821, 2nd-half IC=+0.0928, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.069, Q2=+0.072, Q3_mid=+0.057, Q4=+0.031, Q5_high_vol=+0.200

**`combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=-0.0022, Sharpe=-1.3090)
- Admission: Train IC=+0.2499, Deflated=+0.2501, IR=0.67, Mono=0.78, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.084 | 2017: +0.039 | 2018: +0.222 | 2019: +0.068 | 2020: -0.023 | 2021: +0.147 | 2022: +0.065 | 2023: +0.177 | 2024: +0.018 | 2025: +0.070 | 2026: -0.099
- Yearly Tail ICs:   2015: +0.041 | 2016: -0.023 | 2017: +0.223 | 2018: +0.299 | 2019: +0.295 | 2020: +0.057 | 2021: +0.441 | 2022: +0.309 | 2023: +0.375 | 2024: +0.061 | 2025: -0.061 | 2026: -0.163
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.36, Recency ratio=0.75
- Early IC=+0.1305, Recent IC=+0.0974, 1st-half IC=+0.0789, 2nd-half IC=+0.1075, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.098, Q3_mid=+0.062, Q4=+0.075, Q5_high_vol=+0.151

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=-0.0225, Sharpe=-1.2669)
- Admission: Train IC=+0.2147, Deflated=+0.2148, IR=0.75, Mono=0.76, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.075 | 2017: +0.049 | 2018: +0.172 | 2019: +0.060 | 2020: +0.030 | 2021: +0.175 | 2022: +0.012 | 2023: +0.162 | 2024: +0.060 | 2025: +0.078 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.078 | 2016: +0.097 | 2017: +0.040 | 2018: +0.355 | 2019: +0.236 | 2020: +0.128 | 2021: +0.394 | 2022: +0.254 | 2023: +0.299 | 2024: +0.125 | 2025: +0.044 | 2026: -0.321
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=1.00
- Early IC=+0.1106, Recent IC=+0.1109, 1st-half IC=+0.0691, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.085, Q3_mid=+0.038, Q4=+0.053, Q5_high_vol=+0.190

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0091, Sharpe=-1.2289)
- Admission: Train IC=+0.2119, Deflated=+0.2119, IR=0.68, Mono=0.75, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.080 | 2017: -0.049 | 2018: +0.160 | 2019: +0.085 | 2020: +0.045 | 2021: +0.139 | 2022: +0.031 | 2023: +0.162 | 2024: +0.046 | 2025: +0.067 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.101 | 2016: +0.097 | 2017: +0.043 | 2018: +0.270 | 2019: +0.241 | 2020: +0.095 | 2021: +0.316 | 2022: +0.190 | 2023: +0.271 | 2024: +0.328 | 2025: -0.023 | 2026: -0.233
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.72, Recency ratio=1.87
- Early IC=+0.0558, Recent IC=+0.1042, 1st-half IC=+0.0592, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21, neg years=1)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.069, Q3_mid=+0.027, Q4=+0.037, Q5_high_vol=+0.221

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=-0.0223, Sharpe=-1.1680)
- Admission: Train IC=+0.2309, Deflated=+0.2312, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.087 | 2017: +0.035 | 2018: +0.169 | 2019: +0.060 | 2020: +0.041 | 2021: +0.170 | 2022: +0.015 | 2023: +0.166 | 2024: +0.060 | 2025: +0.078 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.033 | 2017: +0.026 | 2018: +0.412 | 2019: +0.206 | 2020: +0.193 | 2021: +0.360 | 2022: +0.306 | 2023: +0.290 | 2024: +0.141 | 2025: +0.095 | 2026: -0.308
- IC CV=0.69, Neg years (linear/tail)=0/0 of 8, Half ratio=1.62, Recency ratio=1.14
- Early IC=+0.1001, Recent IC=+0.1142, 1st-half IC=+0.0683, 2nd-half IC=+0.1108, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.083, Q3_mid=+0.041, Q4=+0.057, Q5_high_vol=+0.195

**`combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0009, Sharpe=-1.0800)
- Admission: Train IC=+0.2124, Deflated=+0.2130, IR=0.73, Mono=0.78, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.069 | 2017: +0.012 | 2018: +0.217 | 2019: +0.075 | 2020: +0.013 | 2021: +0.153 | 2022: +0.054 | 2023: +0.179 | 2024: +0.021 | 2025: +0.104 | 2026: -0.158
- Yearly Tail ICs:   2015: +0.189 | 2016: -0.042 | 2017: +0.064 | 2018: +0.314 | 2019: +0.173 | 2020: +0.110 | 2021: +0.356 | 2022: +0.256 | 2023: +0.238 | 2024: +0.260 | 2025: +0.140 | 2026: -0.030
- IC CV=0.84, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=0.87
- Early IC=+0.1146, Recent IC=+0.1002, 1st-half IC=+0.0821, 2nd-half IC=+0.1114, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.114, Q3_mid=+0.055, Q4=+0.059, Q5_high_vol=+0.187

**`combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0151, Sharpe=-0.9549)
- Admission: Train IC=+0.1997, Deflated=+0.1998, IR=0.62, Mono=0.70, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.129 | 2016: +0.082 | 2017: +0.022 | 2018: +0.206 | 2019: +0.063 | 2020: -0.007 | 2021: +0.156 | 2022: +0.033 | 2023: +0.165 | 2024: +0.014 | 2025: +0.069 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.092 | 2016: -0.015 | 2017: +0.085 | 2018: +0.326 | 2019: +0.250 | 2020: +0.165 | 2021: +0.381 | 2022: +0.239 | 2023: +0.252 | 2024: +0.151 | 2025: +0.004 | 2026: -0.221
- IC CV=0.94, Neg years (linear/tail)=1/0 of 8, Half ratio=1.42, Recency ratio=0.79
- Early IC=+0.1137, Recent IC=+0.0895, 1st-half IC=+0.0690, 2nd-half IC=+0.0977, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.090, Q3_mid=+0.010, Q4=+0.074, Q5_high_vol=+0.157

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=-0.0055, Sharpe=-0.8914)
- Admission: Train IC=+0.2709, Deflated=+0.2714, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.093 | 2017: -0.053 | 2018: +0.213 | 2019: +0.115 | 2020: +0.070 | 2021: +0.177 | 2022: +0.016 | 2023: +0.135 | 2024: +0.064 | 2025: +0.032 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.273 | 2016: +0.159 | 2017: +0.041 | 2018: +0.355 | 2019: +0.363 | 2020: +0.165 | 2021: +0.504 | 2022: +0.223 | 2023: +0.109 | 2024: +0.318 | 2025: -0.060 | 2026: +0.071
- IC CV=0.88, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=1.24
- Early IC=+0.0798, Recent IC=+0.0991, 1st-half IC=+0.0929, 2nd-half IC=+0.1080, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21, neg years=1)
- Regime ICs: Q1_low_vol=-0.018, Q2=+0.054, Q3_mid=+0.091, Q4=+0.070, Q5_high_vol=+0.243

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=-0.0082, Sharpe=-0.8893)
- Admission: Train IC=+0.2183, Deflated=+0.2179, IR=0.59, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.103 | 2017: -0.057 | 2018: +0.197 | 2019: +0.111 | 2020: +0.026 | 2021: +0.160 | 2022: +0.049 | 2023: +0.165 | 2024: +0.058 | 2025: +0.062 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.080 | 2017: -0.007 | 2018: +0.227 | 2019: +0.255 | 2020: +0.134 | 2021: +0.372 | 2022: +0.229 | 2023: +0.300 | 2024: +0.282 | 2025: +0.037 | 2026: -0.008
- IC CV=0.90, Neg years (linear/tail)=1/1 of 8, Half ratio=1.46, Recency ratio=1.59
- Early IC=+0.0701, Recent IC=+0.1117, 1st-half IC=+0.0775, 2nd-half IC=+0.1131, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21, neg years=1)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.057, Q3_mid=+0.060, Q4=+0.069, Q5_high_vol=+0.221

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0261, Sharpe=-0.8875)
- Admission: Train IC=+0.2199, Deflated=+0.2204, IR=0.80, Mono=0.78, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.056 | 2017: +0.004 | 2018: +0.173 | 2019: +0.050 | 2020: +0.003 | 2021: +0.181 | 2022: +0.048 | 2023: +0.189 | 2024: +0.031 | 2025: +0.109 | 2026: -0.185
- Yearly Tail ICs:   2015: +0.043 | 2016: +0.201 | 2017: +0.165 | 2018: +0.386 | 2019: +0.181 | 2020: +0.074 | 2021: +0.369 | 2022: +0.343 | 2023: +0.364 | 2024: +0.068 | 2025: +0.041 | 2026: +0.010
- IC CV=0.90, Neg years (linear/tail)=0/0 of 8, Half ratio=2.24, Recency ratio=1.24
- Early IC=+0.0886, Recent IC=+0.1097, 1st-half IC=+0.0540, 2nd-half IC=+0.1210, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.102, Q3_mid=+0.023, Q4=+0.054, Q5_high_vol=+0.177

**`combo_rank_max__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0214, Sharpe=-0.7372)
- Admission: Train IC=+0.2155, Deflated=+0.2166, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.032 | 2017: +0.051 | 2018: +0.189 | 2019: +0.057 | 2020: -0.007 | 2021: +0.167 | 2022: +0.055 | 2023: +0.189 | 2024: +0.001 | 2025: +0.086 | 2026: -0.174
- Yearly Tail ICs:   2015: +0.108 | 2016: -0.059 | 2017: +0.161 | 2018: +0.434 | 2019: +0.187 | 2020: +0.228 | 2021: +0.380 | 2022: +0.205 | 2023: +0.135 | 2024: +0.112 | 2025: +0.221 | 2026: -0.343
- IC CV=0.86, Neg years (linear/tail)=1/0 of 8, Half ratio=1.55, Recency ratio=0.78
- Early IC=+0.1210, Recent IC=+0.0945, 1st-half IC=+0.0694, 2nd-half IC=+0.1075, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.127, Q3_mid=+0.049, Q4=+0.055, Q5_high_vol=+0.134

### 500ETF — `single` False Positives

**`combo_sig_product__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=-0.0157, Sharpe=-2.3289)
- Admission: Train IC=+0.1899, Deflated=+0.1889, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.094 | 2017: +0.054 | 2018: +0.193 | 2019: +0.180 | 2020: +0.098 | 2021: +0.070 | 2022: +0.126 | 2023: +0.116 | 2024: +0.083 | 2025: +0.067 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.276 | 2016: +0.131 | 2017: -0.041 | 2018: +0.293 | 2019: +0.359 | 2020: +0.049 | 2021: +0.075 | 2022: +0.262 | 2023: +0.275 | 2024: +0.226 | 2025: -0.110 | 2026: +0.010
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.79, Recency ratio=0.81
- Early IC=+0.1232, Recent IC=+0.0996, 1st-half IC=+0.1294, 2nd-half IC=+0.1020, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46, neg years=0)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.017, Q3_mid=+0.097, Q4=+0.142, Q5_high_vol=+0.165

**`combo_sig_product__net_volume_flow__vwap_close_divergence_trend`** (Lock IC=-0.0041, Sharpe=-1.0439)
- Admission: Train IC=+0.1604, Deflated=+0.1593, IR=0.66, Mono=0.71, p=0.0020, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.047 | 2017: +0.134 | 2018: +0.148 | 2019: +0.145 | 2020: +0.076 | 2021: +0.060 | 2022: +0.102 | 2023: +0.105 | 2024: +0.073 | 2025: +0.078 | 2026: -0.122
- Yearly Tail ICs:   2015: +0.109 | 2016: +0.019 | 2017: +0.102 | 2018: +0.096 | 2019: +0.236 | 2020: -0.023 | 2021: +0.241 | 2022: +0.155 | 2023: +0.285 | 2024: +0.316 | 2025: +0.130 | 2026: -0.357
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.73, Recency ratio=0.63
- Early IC=+0.1410, Recent IC=+0.0890, 1st-half IC=+0.1175, 2nd-half IC=+0.0861, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.38, neg years=0)
- Regime ICs: Q1_low_vol=+0.224, Q2=+0.018, Q3_mid=+0.063, Q4=+0.113, Q5_high_vol=+0.105

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0736, Sharpe=-0.4035)
- Admission: Train IC=+0.1946, Deflated=+0.1941, IR=0.56, Mono=0.71, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.068 | 2017: -0.029 | 2018: +0.171 | 2019: +0.139 | 2020: +0.017 | 2021: +0.123 | 2022: +0.040 | 2023: +0.157 | 2024: +0.042 | 2025: +0.111 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.060 | 2017: +0.018 | 2018: +0.315 | 2019: +0.216 | 2020: +0.150 | 2021: +0.197 | 2022: +0.186 | 2023: +0.163 | 2024: +0.252 | 2025: -0.022 | 2026: +0.244
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=1.20, Recency ratio=1.40
- Early IC=+0.0711, Recent IC=+0.0995, 1st-half IC=+0.0822, 2nd-half IC=+0.0989, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.056, Q3_mid=+0.087, Q4=+0.063, Q5_high_vol=+0.200

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0544, Sharpe=-0.0805)
- Admission: Train IC=+0.2766, Deflated=+0.2766, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.80, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=1.31
- Early IC=+0.0834, Recent IC=+0.1090, 1st-half IC=+0.0944, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.023, Q2=+0.054, Q3_mid=+0.094, Q4=+0.081, Q5_high_vol=+0.219

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0463, Sharpe=-0.5117)
- Admission: Train IC=+0.2881, Deflated=+0.2875, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.058 | 2017: -0.016 | 2018: +0.189 | 2019: +0.144 | 2020: +0.031 | 2021: +0.133 | 2022: +0.047 | 2023: +0.177 | 2024: +0.042 | 2025: +0.096 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.332 | 2016: +0.110 | 2017: +0.091 | 2018: +0.383 | 2019: +0.217 | 2020: +0.188 | 2021: +0.513 | 2022: +0.200 | 2023: +0.302 | 2024: +0.230 | 2025: -0.006 | 2026: +0.299
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=1.12, Recency ratio=1.27
- Early IC=+0.0866, Recent IC=+0.1097, 1st-half IC=+0.0932, 2nd-half IC=+0.1049, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.062, Q3_mid=+0.086, Q4=+0.082, Q5_high_vol=+0.204

**`combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0408, Sharpe=-0.2406)
- Admission: Train IC=+0.1882, Deflated=+0.1881, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.073 | 2017: -0.035 | 2018: +0.208 | 2019: +0.106 | 2020: +0.029 | 2021: +0.148 | 2022: +0.021 | 2023: +0.111 | 2024: +0.043 | 2025: +0.079 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.087 | 2017: -0.124 | 2018: +0.370 | 2019: +0.321 | 2020: +0.140 | 2021: +0.296 | 2022: +0.141 | 2023: +0.035 | 2024: +0.257 | 2025: +0.039 | 2026: +0.271
- IC CV=0.93, Neg years (linear/tail)=1/1 of 8, Half ratio=1.01, Recency ratio=0.89
- Early IC=+0.0865, Recent IC=+0.0767, 1st-half IC=+0.0876, 2nd-half IC=+0.0888, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.063, Q3_mid=+0.065, Q4=+0.066, Q5_high_vol=+0.220

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0259, Sharpe=-0.2846)
- Admission: Train IC=+0.2430, Deflated=+0.2433, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.054 | 2017: -0.045 | 2018: +0.209 | 2019: +0.132 | 2020: +0.059 | 2021: +0.155 | 2022: +0.046 | 2023: +0.129 | 2024: +0.031 | 2025: +0.082 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.372 | 2016: -0.042 | 2017: -0.012 | 2018: +0.261 | 2019: +0.298 | 2020: +0.214 | 2021: +0.412 | 2022: +0.328 | 2023: +0.093 | 2024: +0.250 | 2025: +0.056 | 2026: +0.218
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=0.98
- Early IC=+0.0816, Recent IC=+0.0802, 1st-half IC=+0.0967, 2nd-half IC=+0.0964, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.060, Q3_mid=+0.077, Q4=+0.085, Q5_high_vol=+0.222

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0244, Sharpe=-0.2554)
- Admission: Train IC=+0.2628, Deflated=+0.2633, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.26, Recency ratio=1.41
- Early IC=+0.0674, Recent IC=+0.0948, 1st-half IC=+0.0879, 2nd-half IC=+0.1110, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.032, Q2=+0.068, Q3_mid=+0.113, Q4=+0.074, Q5_high_vol=+0.235

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0229, Sharpe=-0.5791)
- Admission: Train IC=+0.2826, Deflated=+0.2824, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.072 | 2017: -0.020 | 2018: +0.232 | 2019: +0.117 | 2020: +0.046 | 2021: +0.179 | 2022: +0.026 | 2023: +0.145 | 2024: +0.046 | 2025: +0.072 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.064 | 2017: +0.062 | 2018: +0.372 | 2019: +0.343 | 2020: +0.149 | 2021: +0.582 | 2022: +0.177 | 2023: +0.156 | 2024: +0.188 | 2025: -0.085 | 2026: +0.280
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.06, Recency ratio=0.90
- Early IC=+0.1058, Recent IC=+0.0956, 1st-half IC=+0.1002, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.064, Q3_mid=+0.084, Q4=+0.086, Q5_high_vol=+0.228

**`combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0168, Sharpe=-0.5135)
- Admission: Train IC=+0.2186, Deflated=+0.2190, IR=0.70, Mono=0.77, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.079 | 2017: +0.045 | 2018: +0.207 | 2019: +0.081 | 2020: -0.013 | 2021: +0.149 | 2022: +0.052 | 2023: +0.169 | 2024: +0.024 | 2025: +0.098 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.080 | 2017: +0.130 | 2018: +0.378 | 2019: +0.123 | 2020: +0.093 | 2021: +0.426 | 2022: +0.289 | 2023: +0.280 | 2024: +0.222 | 2025: +0.176 | 2026: -0.085
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=1.27, Recency ratio=0.77
- Early IC=+0.1261, Recent IC=+0.0969, 1st-half IC=+0.0835, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.117, Q3_mid=+0.049, Q4=+0.070, Q5_high_vol=+0.162

**`combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0164, Sharpe=-0.7568)
- Admission: Train IC=+0.2578, Deflated=+0.2581, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.054 | 2017: -0.066 | 2018: +0.214 | 2019: +0.120 | 2020: +0.054 | 2021: +0.169 | 2022: +0.026 | 2023: +0.133 | 2024: +0.052 | 2025: +0.044 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.165 | 2017: +0.008 | 2018: +0.372 | 2019: +0.363 | 2020: +0.149 | 2021: +0.501 | 2022: +0.251 | 2023: +0.084 | 2024: +0.271 | 2025: -0.060 | 2026: +0.199
- IC CV=0.95, Neg years (linear/tail)=1/0 of 8, Half ratio=1.15, Recency ratio=1.25
- Early IC=+0.0737, Recent IC=+0.0923, 1st-half IC=+0.0904, 2nd-half IC=+0.1043, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.029, Q2=+0.052, Q3_mid=+0.104, Q4=+0.071, Q5_high_vol=+0.233

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.0158, Sharpe=-0.4533)
- Admission: Train IC=+0.2365, Deflated=+0.2367, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.099 | 2017: -0.039 | 2018: +0.161 | 2019: +0.126 | 2020: +0.068 | 2021: +0.115 | 2022: +0.040 | 2023: +0.128 | 2024: +0.032 | 2025: +0.050 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.476 | 2016: -0.076 | 2017: -0.108 | 2018: +0.238 | 2019: +0.304 | 2020: +0.298 | 2021: +0.332 | 2022: +0.276 | 2023: +0.120 | 2024: +0.256 | 2025: +0.096 | 2026: +0.122
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=1.31
- Early IC=+0.0611, Recent IC=+0.0798, 1st-half IC=+0.0846, 2nd-half IC=+0.0849, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.004, Q2=+0.048, Q3_mid=+0.067, Q4=+0.059, Q5_high_vol=+0.207

**`combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0053, Sharpe=-0.2216)
- Admission: Train IC=+0.2028, Deflated=+0.2027, IR=0.65, Mono=0.78, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.091 | 2017: +0.054 | 2018: +0.208 | 2019: +0.097 | 2020: +0.002 | 2021: +0.136 | 2022: +0.043 | 2023: +0.141 | 2024: +0.034 | 2025: +0.049 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.180 | 2016: -0.020 | 2017: +0.011 | 2018: +0.269 | 2019: +0.163 | 2020: +0.199 | 2021: +0.342 | 2022: +0.270 | 2023: +0.359 | 2024: +0.109 | 2025: +0.057 | 2026: -0.031
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.67
- Early IC=+0.1310, Recent IC=+0.0878, 1st-half IC=+0.0903, 2nd-half IC=+0.0911, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.085, Q3_mid=+0.050, Q4=+0.076, Q5_high_vol=+0.177

### 500ETF — `single` Median Features

**`combo_rel_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1090, Sharpe=-0.2440)
- Admission: Train IC=+0.2310, Deflated=+0.2299, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.092 | 2017: +0.220 | 2018: +0.177 | 2019: +0.153 | 2020: +0.149 | 2021: +0.106 | 2022: +0.079 | 2023: +0.116 | 2024: +0.128 | 2025: +0.156 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.284 | 2016: +0.018 | 2017: +0.246 | 2018: +0.232 | 2019: +0.242 | 2020: +0.217 | 2021: +0.129 | 2022: +0.229 | 2023: +0.246 | 2024: +0.198 | 2025: +0.088 | 2026: -0.073
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.61
- Early IC=+0.1989, Recent IC=+0.1222, 1st-half IC=+0.1682, 2nd-half IC=+0.1123, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.201, Q2=+0.005, Q3_mid=+0.138, Q4=+0.155, Q5_high_vol=+0.194

**`combo_clamp_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1062, Sharpe=-0.9378)
- Admission: Train IC=+0.2573, Deflated=+0.2555, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.082 | 2017: +0.251 | 2018: +0.190 | 2019: +0.123 | 2020: +0.172 | 2021: +0.092 | 2022: +0.117 | 2023: +0.137 | 2024: +0.118 | 2025: +0.149 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.117 | 2017: +0.362 | 2018: +0.232 | 2019: +0.120 | 2020: +0.069 | 2021: +0.167 | 2022: +0.163 | 2023: +0.226 | 2024: +0.205 | 2025: +0.141 | 2026: -0.300
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.2203, Recent IC=+0.1275, 1st-half IC=+0.1715, 2nd-half IC=+0.1220, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.029, Q3_mid=+0.134, Q4=+0.145, Q5_high_vol=+0.199

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1051, Sharpe=-0.1201)
- Admission: Train IC=+0.2432, Deflated=+0.2416, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.088 | 2017: +0.203 | 2018: +0.109 | 2019: +0.104 | 2020: +0.126 | 2021: +0.059 | 2022: +0.080 | 2023: +0.061 | 2024: +0.114 | 2025: +0.113 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.193 | 2017: +0.302 | 2018: +0.272 | 2019: +0.323 | 2020: +0.210 | 2021: +0.203 | 2022: +0.234 | 2023: +0.012 | 2024: +0.264 | 2025: +0.078 | 2026: +0.031
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.56
- Early IC=+0.1560, Recent IC=+0.0873, 1st-half IC=+0.1245, 2nd-half IC=+0.0855, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.015, Q3_mid=+0.082, Q4=+0.099, Q5_high_vol=+0.127

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1043, Sharpe=-0.3294)
- Admission: Train IC=+0.2433, Deflated=+0.2421, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.068 | 2017: +0.245 | 2018: +0.194 | 2019: +0.135 | 2020: +0.150 | 2021: +0.084 | 2022: +0.096 | 2023: +0.129 | 2024: +0.127 | 2025: +0.153 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.314 | 2016: -0.036 | 2017: +0.246 | 2018: +0.239 | 2019: +0.248 | 2020: +0.226 | 2021: +0.120 | 2022: +0.235 | 2023: +0.295 | 2024: +0.222 | 2025: +0.149 | 2026: -0.088
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.58
- Early IC=+0.2195, Recent IC=+0.1278, 1st-half IC=+0.1744, 2nd-half IC=+0.1136, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.230, Q2=+0.021, Q3_mid=+0.134, Q4=+0.154, Q5_high_vol=+0.183

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0952, Sharpe=-0.1966)
- Admission: Train IC=+0.2298, Deflated=+0.2285, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.094 | 2017: +0.246 | 2018: +0.224 | 2019: +0.151 | 2020: +0.191 | 2021: +0.117 | 2022: +0.078 | 2023: +0.084 | 2024: +0.126 | 2025: +0.119 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.063 | 2017: +0.196 | 2018: +0.358 | 2019: +0.302 | 2020: +0.214 | 2021: +0.257 | 2022: +0.118 | 2023: +0.057 | 2024: +0.184 | 2025: +0.081 | 2026: +0.175
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.45
- Early IC=+0.2349, Recent IC=+0.1049, 1st-half IC=+0.1935, 2nd-half IC=+0.1055, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.226, Q2=-0.002, Q3_mid=+0.126, Q4=+0.162, Q5_high_vol=+0.208

**`combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.0950, Sharpe=-0.0776)
- Admission: Train IC=+0.2668, Deflated=+0.2654, IR=0.85, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.090 | 2017: +0.240 | 2018: +0.181 | 2019: +0.128 | 2020: +0.172 | 2021: +0.100 | 2022: +0.076 | 2023: +0.077 | 2024: +0.135 | 2025: +0.116 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.143 | 2017: +0.232 | 2018: +0.322 | 2019: +0.417 | 2020: +0.148 | 2021: +0.225 | 2022: +0.284 | 2023: +0.145 | 2024: +0.244 | 2025: +0.101 | 2026: +0.058
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.50
- Early IC=+0.2105, Recent IC=+0.1062, 1st-half IC=+0.1693, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.018, Q3_mid=+0.117, Q4=+0.131, Q5_high_vol=+0.195

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.0942, Sharpe=-0.2127)
- Admission: Train IC=+0.2523, Deflated=+0.2504, IR=0.98, Mono=0.84, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.128 | 2017: +0.198 | 2018: +0.224 | 2019: +0.118 | 2020: +0.165 | 2021: +0.115 | 2022: +0.116 | 2023: +0.081 | 2024: +0.107 | 2025: +0.128 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.250 | 2017: +0.233 | 2018: +0.429 | 2019: +0.250 | 2020: +0.222 | 2021: +0.206 | 2022: +0.268 | 2023: +0.151 | 2024: +0.215 | 2025: -0.102 | 2026: +0.032
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.45
- Early IC=+0.2107, Recent IC=+0.0940, 1st-half IC=+0.1704, 2nd-half IC=+0.1080, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.020, Q3_mid=+0.098, Q4=+0.148, Q5_high_vol=+0.204

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0933, Sharpe=-0.2396)
- Admission: Train IC=+0.2385, Deflated=+0.2369, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.125 | 2017: +0.152 | 2018: +0.158 | 2019: +0.096 | 2020: +0.139 | 2021: +0.058 | 2022: +0.126 | 2023: +0.073 | 2024: +0.090 | 2025: +0.110 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.233 | 2016: +0.265 | 2017: +0.234 | 2018: +0.351 | 2019: +0.286 | 2020: +0.171 | 2021: +0.124 | 2022: +0.256 | 2023: +0.184 | 2024: +0.182 | 2025: +0.111 | 2026: +0.113
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.52
- Early IC=+0.1549, Recent IC=+0.0812, 1st-half IC=+0.1349, 2nd-half IC=+0.0919, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.031, Q3_mid=+0.082, Q4=+0.112, Q5_high_vol=+0.155

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0883, Sharpe=-0.5698)
- Admission: Train IC=+0.2689, Deflated=+0.2675, IR=1.07, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.123 | 2017: +0.222 | 2018: +0.178 | 2019: +0.172 | 2020: +0.171 | 2021: +0.141 | 2022: +0.008 | 2023: +0.106 | 2024: +0.163 | 2025: +0.094 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.247 | 2017: +0.328 | 2018: +0.514 | 2019: +0.346 | 2020: +0.235 | 2021: +0.278 | 2022: +0.140 | 2023: +0.112 | 2024: +0.297 | 2025: -0.002 | 2026: +0.151
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.67
- Early IC=+0.2002, Recent IC=+0.1341, 1st-half IC=+0.1783, 2nd-half IC=+0.1107, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.005, Q3_mid=+0.122, Q4=+0.123, Q5_high_vol=+0.235

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.0849, Sharpe=-0.1619)
- Admission: Train IC=+0.2897, Deflated=+0.2885, IR=1.10, Mono=0.85, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.106 | 2017: +0.204 | 2018: +0.139 | 2019: +0.132 | 2020: +0.154 | 2021: +0.155 | 2022: +0.078 | 2023: +0.108 | 2024: +0.134 | 2025: +0.118 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.238 | 2017: +0.235 | 2018: +0.365 | 2019: +0.237 | 2020: +0.309 | 2021: +0.222 | 2022: +0.245 | 2023: +0.248 | 2024: +0.405 | 2025: +0.085 | 2026: +0.257
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.71
- Early IC=+0.1712, Recent IC=+0.1209, 1st-half IC=+0.1428, 2nd-half IC=+0.1188, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.012, Q3_mid=+0.107, Q4=+0.132, Q5_high_vol=+0.177

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0829, Sharpe=-0.5054)
- Admission: Train IC=+0.2255, Deflated=+0.2236, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.298 | 2016: +0.138 | 2017: +0.218 | 2018: +0.251 | 2019: +0.141 | 2020: +0.163 | 2021: +0.126 | 2022: +0.103 | 2023: +0.082 | 2024: +0.117 | 2025: +0.105 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.206 | 2017: +0.170 | 2018: +0.461 | 2019: +0.173 | 2020: +0.249 | 2021: +0.254 | 2022: +0.120 | 2023: +0.045 | 2024: +0.090 | 2025: +0.049 | 2026: +0.117
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.42
- Early IC=+0.2346, Recent IC=+0.0997, 1st-half IC=+0.1819, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.006, Q3_mid=+0.091, Q4=+0.167, Q5_high_vol=+0.220

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0774, Sharpe=-0.9150)
- Admission: Train IC=+0.1841, Deflated=+0.1827, IR=0.51, Mono=0.70, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.128 | 2017: +0.208 | 2018: +0.237 | 2019: +0.146 | 2020: +0.136 | 2021: +0.116 | 2022: +0.086 | 2023: +0.083 | 2024: +0.133 | 2025: +0.109 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.136 | 2017: +0.221 | 2018: +0.397 | 2019: +0.111 | 2020: +0.297 | 2021: +0.096 | 2022: +0.057 | 2023: +0.146 | 2024: +0.187 | 2025: -0.013 | 2026: +0.144
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.48
- Early IC=+0.2226, Recent IC=+0.1079, 1st-half IC=+0.1680, 2nd-half IC=+0.1079, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.022, Q3_mid=+0.095, Q4=+0.135, Q5_high_vol=+0.202

**`combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0729, Sharpe=-0.5299)
- Admission: Train IC=+0.1919, Deflated=+0.1911, IR=0.73, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.216 | 2016: +0.104 | 2017: +0.182 | 2018: +0.222 | 2019: +0.139 | 2020: +0.125 | 2021: +0.062 | 2022: +0.102 | 2023: +0.084 | 2024: +0.126 | 2025: +0.144 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.361 | 2016: +0.136 | 2017: +0.256 | 2018: +0.317 | 2019: +0.178 | 2020: +0.231 | 2021: +0.029 | 2022: +0.152 | 2023: +0.232 | 2024: +0.227 | 2025: -0.023 | 2026: -0.096
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.52
- Early IC=+0.2023, Recent IC=+0.1050, 1st-half IC=+0.1598, 2nd-half IC=+0.1005, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.221, Q2=+0.032, Q3_mid=+0.118, Q4=+0.153, Q5_high_vol=+0.147

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0726, Sharpe=-0.1470)
- Admission: Train IC=+0.2488, Deflated=+0.2476, IR=0.90, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.085 | 2017: +0.209 | 2018: +0.194 | 2019: +0.150 | 2020: +0.160 | 2021: +0.117 | 2022: +0.096 | 2023: +0.118 | 2024: +0.155 | 2025: +0.133 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.412 | 2016: +0.294 | 2017: +0.293 | 2018: +0.338 | 2019: +0.208 | 2020: +0.273 | 2021: +0.215 | 2022: +0.225 | 2023: +0.200 | 2024: +0.291 | 2025: +0.004 | 2026: -0.226
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.68
- Early IC=+0.2015, Recent IC=+0.1363, 1st-half IC=+0.1686, 2nd-half IC=+0.1283, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.240, Q2=+0.012, Q3_mid=+0.151, Q4=+0.129, Q5_high_vol=+0.207

**`combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0702, Sharpe=-0.0334)
- Admission: Train IC=+0.2353, Deflated=+0.2343, IR=0.83, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.119 | 2017: +0.225 | 2018: +0.221 | 2019: +0.143 | 2020: +0.145 | 2021: +0.077 | 2022: +0.118 | 2023: +0.088 | 2024: +0.122 | 2025: +0.151 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.282 | 2016: +0.129 | 2017: +0.259 | 2018: +0.326 | 2019: +0.255 | 2020: +0.258 | 2021: +0.118 | 2022: +0.154 | 2023: +0.240 | 2024: +0.346 | 2025: +0.014 | 2026: -0.268
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.47
- Early IC=+0.2226, Recent IC=+0.1051, 1st-half IC=+0.1707, 2nd-half IC=+0.1044, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.010, Q3_mid=+0.135, Q4=+0.145, Q5_high_vol=+0.199

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0650, Sharpe=-0.4634)
- Admission: Train IC=+0.2387, Deflated=+0.2377, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.105 | 2017: +0.208 | 2018: +0.244 | 2019: +0.160 | 2020: +0.141 | 2021: +0.106 | 2022: +0.067 | 2023: +0.088 | 2024: +0.120 | 2025: +0.122 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.391 | 2016: +0.088 | 2017: +0.341 | 2018: +0.464 | 2019: +0.163 | 2020: +0.145 | 2021: +0.263 | 2022: +0.276 | 2023: +0.183 | 2024: +0.210 | 2025: +0.098 | 2026: -0.177
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.46
- Early IC=+0.2258, Recent IC=+0.1041, 1st-half IC=+0.1768, 2nd-half IC=+0.1001, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.001, Q3_mid=+0.134, Q4=+0.141, Q5_high_vol=+0.191

**`combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0`** (Lock IC=+0.0637, Sharpe=-0.3821)
- Admission: Train IC=+0.2523, Deflated=+0.2515, IR=0.88, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.077 | 2017: +0.181 | 2018: +0.186 | 2019: +0.133 | 2020: +0.107 | 2021: +0.115 | 2022: +0.115 | 2023: +0.099 | 2024: +0.134 | 2025: +0.128 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.333 | 2016: +0.010 | 2017: +0.213 | 2018: +0.404 | 2019: +0.140 | 2020: +0.124 | 2021: +0.245 | 2022: +0.224 | 2023: +0.278 | 2024: +0.332 | 2025: +0.130 | 2026: -0.053
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.63
- Early IC=+0.1832, Recent IC=+0.1164, 1st-half IC=+0.1373, 2nd-half IC=+0.1173, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.014, Q3_mid=+0.112, Q4=+0.139, Q5_high_vol=+0.159

**`combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0`** (Lock IC=+0.0627, Sharpe=-0.6281)
- Admission: Train IC=+0.1876, Deflated=+0.1864, IR=0.58, Mono=0.68, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.137 | 2017: +0.140 | 2018: +0.191 | 2019: +0.065 | 2020: +0.115 | 2021: +0.070 | 2022: +0.125 | 2023: +0.061 | 2024: +0.106 | 2025: +0.086 | 2026: +0.055
- Yearly Tail ICs:   2015: +0.147 | 2016: +0.251 | 2017: +0.174 | 2018: +0.249 | 2019: +0.141 | 2020: +0.025 | 2021: +0.373 | 2022: +0.182 | 2023: +0.147 | 2024: +0.096 | 2025: -0.038 | 2026: -0.155
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.50
- Early IC=+0.1656, Recent IC=+0.0835, 1st-half IC=+0.1250, 2nd-half IC=+0.0972, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.023, Q3_mid=+0.105, Q4=+0.123, Q5_high_vol=+0.140

**`combo_min__net_volume_flow__bar_body_rng_0`** (Lock IC=+0.0618, Sharpe=-0.3714)
- Admission: Train IC=+0.2439, Deflated=+0.2441, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.066 | 2017: +0.185 | 2018: +0.180 | 2019: +0.118 | 2020: +0.093 | 2021: +0.095 | 2022: +0.084 | 2023: +0.087 | 2024: +0.124 | 2025: +0.119 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.351 | 2016: -0.053 | 2017: +0.142 | 2018: +0.304 | 2019: +0.147 | 2020: +0.165 | 2021: +0.207 | 2022: +0.228 | 2023: +0.204 | 2024: +0.314 | 2025: +0.196 | 2026: -0.025
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.58
- Early IC=+0.1824, Recent IC=+0.1056, 1st-half IC=+0.1323, 2nd-half IC=+0.1003, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.017, Q3_mid=+0.110, Q4=+0.154, Q5_high_vol=+0.133

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0598, Sharpe=-0.3728)
- Admission: Train IC=+0.2198, Deflated=+0.2185, IR=0.70, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.129 | 2017: +0.227 | 2018: +0.245 | 2019: +0.170 | 2020: +0.182 | 2021: +0.132 | 2022: +0.086 | 2023: +0.080 | 2024: +0.140 | 2025: +0.096 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.141 | 2017: +0.270 | 2018: +0.437 | 2019: +0.231 | 2020: +0.259 | 2021: +0.158 | 2022: -0.022 | 2023: +0.164 | 2024: +0.262 | 2025: +0.013 | 2026: -0.280
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.59, Recency ratio=0.47
- Early IC=+0.2361, Recent IC=+0.1100, 1st-half IC=+0.1945, 2nd-half IC=+0.1151, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.024, Q3_mid=+0.143, Q4=+0.135, Q5_high_vol=+0.241

**`combo_rank_max__max_up_ret__max_down_ret`** (Lock IC=+0.0594, Sharpe=-0.3475)
- Admission: Train IC=+0.2062, Deflated=+0.2054, IR=0.80, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.079 | 2017: +0.232 | 2018: +0.240 | 2019: +0.123 | 2020: +0.132 | 2021: +0.128 | 2022: +0.077 | 2023: +0.052 | 2024: +0.142 | 2025: +0.111 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.520 | 2016: -0.023 | 2017: +0.192 | 2018: +0.193 | 2019: +0.374 | 2020: +0.193 | 2021: +0.307 | 2022: +0.142 | 2023: +0.092 | 2024: +0.311 | 2025: +0.202 | 2026: -0.142
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.43
- Early IC=+0.2311, Recent IC=+0.1004, 1st-half IC=+0.1649, 2nd-half IC=+0.1054, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.221, Q2=-0.012, Q3_mid=+0.130, Q4=+0.114, Q5_high_vol=+0.206

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction`** (Lock IC=+0.0565, Sharpe=-0.8039)
- Admission: Train IC=+0.2145, Deflated=+0.2134, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.069 | 2017: +0.204 | 2018: +0.199 | 2019: +0.112 | 2020: +0.136 | 2021: +0.093 | 2022: +0.139 | 2023: +0.113 | 2024: +0.168 | 2025: +0.151 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.245 | 2016: +0.155 | 2017: +0.223 | 2018: +0.281 | 2019: +0.286 | 2020: +0.210 | 2021: +0.137 | 2022: +0.283 | 2023: +0.120 | 2024: +0.298 | 2025: -0.093 | 2026: -0.254
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.70
- Early IC=+0.2018, Recent IC=+0.1403, 1st-half IC=+0.1482, 2nd-half IC=+0.1329, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.024, Q3_mid=+0.130, Q4=+0.117, Q5_high_vol=+0.210

**`combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0560, Sharpe=-1.0726)
- Admission: Train IC=+0.2588, Deflated=+0.2581, IR=0.85, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.060 | 2017: +0.153 | 2018: +0.135 | 2019: +0.084 | 2020: +0.118 | 2021: +0.094 | 2022: +0.099 | 2023: +0.100 | 2024: +0.139 | 2025: +0.125 | 2026: -0.040
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.183 | 2017: +0.178 | 2018: +0.259 | 2019: +0.216 | 2020: +0.270 | 2021: +0.265 | 2022: +0.304 | 2023: +0.228 | 2024: +0.291 | 2025: +0.016 | 2026: -0.173
- IC CV=0.20, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.83
- Early IC=+0.1441, Recent IC=+0.1197, 1st-half IC=+0.1132, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.001, Q3_mid=+0.112, Q4=+0.126, Q5_high_vol=+0.127

**`combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0534, Sharpe=-1.3411)
- Admission: Train IC=+0.2578, Deflated=+0.2570, IR=0.94, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.277 | 2016: +0.075 | 2017: +0.263 | 2018: +0.146 | 2019: +0.117 | 2020: +0.157 | 2021: +0.109 | 2022: +0.095 | 2023: +0.073 | 2024: +0.149 | 2025: +0.112 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.436 | 2016: -0.023 | 2017: +0.320 | 2018: +0.251 | 2019: +0.393 | 2020: +0.170 | 2021: +0.222 | 2022: +0.274 | 2023: +0.267 | 2024: +0.278 | 2025: -0.051 | 2026: -0.181
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.54
- Early IC=+0.2044, Recent IC=+0.1113, 1st-half IC=+0.1560, 2nd-half IC=+0.1159, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.010, Q3_mid=+0.140, Q4=+0.132, Q5_high_vol=+0.181

**`combo_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0525, Sharpe=-0.4214)
- Admission: Train IC=+0.2540, Deflated=+0.2534, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.073 | 2017: +0.175 | 2018: +0.136 | 2019: +0.075 | 2020: +0.098 | 2021: +0.065 | 2022: +0.078 | 2023: +0.091 | 2024: +0.127 | 2025: +0.140 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.308 | 2016: +0.118 | 2017: +0.321 | 2018: +0.251 | 2019: +0.204 | 2020: +0.247 | 2021: +0.221 | 2022: +0.111 | 2023: +0.216 | 2024: +0.234 | 2025: -0.012 | 2026: -0.010
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.70
- Early IC=+0.1554, Recent IC=+0.1089, 1st-half IC=+0.1081, 2nd-half IC=+0.0965, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.004, Q3_mid=+0.103, Q4=+0.106, Q5_high_vol=+0.112

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0524, Sharpe=-0.6914)
- Admission: Train IC=+0.2127, Deflated=+0.2112, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.140 | 2017: +0.227 | 2018: +0.215 | 2019: +0.111 | 2020: +0.183 | 2021: +0.149 | 2022: +0.103 | 2023: +0.117 | 2024: +0.171 | 2025: +0.097 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.278 | 2017: +0.266 | 2018: +0.326 | 2019: +0.260 | 2020: +0.291 | 2021: +0.349 | 2022: -0.026 | 2023: +0.105 | 2024: +0.338 | 2025: -0.051 | 2026: -0.093
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.65
- Early IC=+0.2210, Recent IC=+0.1437, 1st-half IC=+0.1670, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.043, Q3_mid=+0.135, Q4=+0.133, Q5_high_vol=+0.231

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0518, Sharpe=-0.2853)
- Admission: Train IC=+0.2053, Deflated=+0.2054, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.093 | 2017: +0.259 | 2018: +0.235 | 2019: +0.142 | 2020: +0.133 | 2021: +0.080 | 2022: +0.095 | 2023: +0.039 | 2024: +0.124 | 2025: +0.101 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.246 | 2016: -0.006 | 2017: +0.243 | 2018: +0.406 | 2019: +0.109 | 2020: +0.236 | 2021: +0.186 | 2022: +0.169 | 2023: +0.222 | 2024: +0.235 | 2025: +0.034 | 2026: -0.250
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.33
- Early IC=+0.2472, Recent IC=+0.0813, 1st-half IC=+0.1692, 2nd-half IC=+0.0931, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.023, Q3_mid=+0.137, Q4=+0.136, Q5_high_vol=+0.176

**`combo_mean__max_up_ret__max_down_ret`** (Lock IC=+0.0502, Sharpe=-0.6875)
- Admission: Train IC=+0.2117, Deflated=+0.2107, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.068 | 2017: +0.242 | 2018: +0.209 | 2019: +0.120 | 2020: +0.135 | 2021: +0.107 | 2022: +0.105 | 2023: +0.091 | 2024: +0.157 | 2025: +0.106 | 2026: -0.016
- Yearly Tail ICs:   2015: +0.340 | 2016: +0.213 | 2017: +0.324 | 2018: +0.285 | 2019: +0.181 | 2020: +0.133 | 2021: +0.325 | 2022: +0.131 | 2023: +0.256 | 2024: +0.278 | 2025: -0.035 | 2026: -0.157
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.55
- Early IC=+0.2256, Recent IC=+0.1238, 1st-half IC=+0.1564, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.228, Q2=+0.014, Q3_mid=+0.115, Q4=+0.128, Q5_high_vol=+0.191

**`combo_mean__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0478, Sharpe=-0.8584)
- Admission: Train IC=+0.2406, Deflated=+0.2401, IR=0.85, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.091 | 2017: +0.234 | 2018: +0.258 | 2019: +0.155 | 2020: +0.157 | 2021: +0.133 | 2022: +0.084 | 2023: +0.089 | 2024: +0.150 | 2025: +0.089 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.265 | 2016: -0.002 | 2017: +0.223 | 2018: +0.464 | 2019: +0.155 | 2020: +0.239 | 2021: +0.295 | 2022: +0.208 | 2023: +0.161 | 2024: +0.222 | 2025: +0.048 | 2026: -0.217
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.49
- Early IC=+0.2458, Recent IC=+0.1197, 1st-half IC=+0.1882, 2nd-half IC=+0.1190, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.222, Q2=-0.007, Q3_mid=+0.146, Q4=+0.158, Q5_high_vol=+0.211

**`combo_mean__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0473, Sharpe=-1.1154)
- Admission: Train IC=+0.2148, Deflated=+0.2153, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.124 | 2017: +0.171 | 2018: +0.222 | 2019: +0.135 | 2020: +0.092 | 2021: +0.108 | 2022: +0.065 | 2023: +0.066 | 2024: +0.113 | 2025: +0.094 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.280 | 2016: -0.030 | 2017: +0.336 | 2018: +0.399 | 2019: +0.162 | 2020: +0.186 | 2021: +0.334 | 2022: +0.132 | 2023: +0.129 | 2024: +0.246 | 2025: +0.049 | 2026: -0.212
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.45
- Early IC=+0.1967, Recent IC=+0.0893, 1st-half IC=+0.1499, 2nd-half IC=+0.0873, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.032, Q3_mid=+0.103, Q4=+0.160, Q5_high_vol=+0.161

**`combo_rank_max__max_up_ret__net_volume_flow`** (Lock IC=+0.0469, Sharpe=-1.4510)
- Admission: Train IC=+0.2350, Deflated=+0.2339, IR=0.72, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.102 | 2017: +0.185 | 2018: +0.218 | 2019: +0.083 | 2020: +0.125 | 2021: +0.095 | 2022: +0.106 | 2023: +0.095 | 2024: +0.139 | 2025: +0.102 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.221 | 2017: +0.239 | 2018: +0.288 | 2019: +0.129 | 2020: +0.309 | 2021: +0.299 | 2022: +0.153 | 2023: +0.212 | 2024: +0.308 | 2025: -0.033 | 2026: -0.308
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.59
- Early IC=+0.2023, Recent IC=+0.1189, 1st-half IC=+0.1402, 2nd-half IC=+0.1158, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.000, Q3_mid=+0.103, Q4=+0.136, Q5_high_vol=+0.193

**`combo_mean__bar_ret_0__close_vs_open_range`** (Lock IC=+0.0469, Sharpe=-1.2311)
- Admission: Train IC=+0.2594, Deflated=+0.2588, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.095 | 2017: +0.214 | 2018: +0.198 | 2019: +0.106 | 2020: +0.115 | 2021: +0.099 | 2022: +0.097 | 2023: +0.078 | 2024: +0.153 | 2025: +0.120 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.039 | 2017: +0.255 | 2018: +0.345 | 2019: +0.137 | 2020: +0.180 | 2021: +0.374 | 2022: +0.269 | 2023: +0.219 | 2024: +0.337 | 2025: +0.063 | 2026: -0.260
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.56
- Early IC=+0.2060, Recent IC=+0.1156, 1st-half IC=+0.1444, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.229, Q2=+0.005, Q3_mid=+0.124, Q4=+0.126, Q5_high_vol=+0.159

**`num_up_bars`** (Lock IC=+0.0459, Sharpe=-1.1323)
- Admission: Train IC=+0.1213, Deflated=+0.1198, IR=0.36, Mono=0.65, p=0.0144, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.077 | 2016: +0.103 | 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141 | 2025: +0.117 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.253 | 2017: +0.002 | 2018: +0.082 | 2019: +0.121 | 2020: +0.184 | 2021: -0.075 | 2022: +0.221 | 2023: +0.122 | 2024: +0.211 | 2025: -0.019 | 2026: -0.077
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=1.47, Recency ratio=1.31
- Early IC=+0.0851, Recent IC=+0.1118, 1st-half IC=+0.0732, 2nd-half IC=+0.1074, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.054, Q3_mid=+0.097, Q4=+0.105, Q5_high_vol=+0.089

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0453, Sharpe=-0.8924)
- Admission: Train IC=+0.2303, Deflated=+0.2293, IR=0.99, Mono=0.85, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.102 | 2017: +0.203 | 2018: +0.217 | 2019: +0.144 | 2020: +0.152 | 2021: +0.126 | 2022: +0.062 | 2023: +0.118 | 2024: +0.155 | 2025: +0.097 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.529 | 2016: +0.284 | 2017: +0.348 | 2018: +0.372 | 2019: +0.202 | 2020: +0.194 | 2021: +0.265 | 2022: +0.183 | 2023: +0.221 | 2024: +0.180 | 2025: -0.155 | 2026: -0.059
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.65
- Early IC=+0.2099, Recent IC=+0.1365, 1st-half IC=+0.1642, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.015, Q3_mid=+0.146, Q4=+0.118, Q5_high_vol=+0.217

**`combo_mean__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0450, Sharpe=-0.0326)
- Admission: Train IC=+0.2166, Deflated=+0.2163, IR=0.66, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.064 | 2017: +0.222 | 2018: +0.182 | 2019: +0.128 | 2020: +0.108 | 2021: +0.123 | 2022: +0.094 | 2023: +0.091 | 2024: +0.130 | 2025: +0.133 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.040 | 2017: +0.144 | 2018: +0.392 | 2019: +0.212 | 2020: +0.088 | 2021: +0.281 | 2022: +0.245 | 2023: +0.276 | 2024: +0.151 | 2025: +0.186 | 2026: -0.246
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.55
- Early IC=+0.2020, Recent IC=+0.1102, 1st-half IC=+0.1427, 2nd-half IC=+0.1154, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.224, Q2=+0.019, Q3_mid=+0.121, Q4=+0.119, Q5_high_vol=+0.161

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0449, Sharpe=-0.9665)
- Admission: Train IC=+0.1993, Deflated=+0.1979, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.097 | 2017: +0.225 | 2018: +0.174 | 2019: +0.098 | 2020: +0.114 | 2021: +0.125 | 2022: +0.110 | 2023: +0.086 | 2024: +0.139 | 2025: +0.094 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.547 | 2016: +0.311 | 2017: +0.285 | 2018: +0.192 | 2019: +0.167 | 2020: +0.147 | 2021: +0.360 | 2022: +0.096 | 2023: +0.184 | 2024: +0.216 | 2025: +0.010 | 2026: -0.029
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.56
- Early IC=+0.1991, Recent IC=+0.1123, 1st-half IC=+0.1335, 2nd-half IC=+0.1225, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.023, Q3_mid=+0.123, Q4=+0.125, Q5_high_vol=+0.181

**`combo_clamp_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0447, Sharpe=-0.9029)
- Admission: Train IC=+0.2463, Deflated=+0.2457, IR=0.72, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.315 | 2016: +0.116 | 2017: +0.191 | 2018: +0.217 | 2019: +0.121 | 2020: +0.146 | 2021: +0.154 | 2022: +0.059 | 2023: +0.095 | 2024: +0.130 | 2025: +0.016 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.425 | 2016: +0.126 | 2017: +0.414 | 2018: +0.340 | 2019: +0.327 | 2020: +0.081 | 2021: +0.217 | 2022: +0.160 | 2023: +0.123 | 2024: +0.212 | 2025: -0.059 | 2026: -0.043
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.55
- Early IC=+0.2041, Recent IC=+0.1125, 1st-half IC=+0.1578, 2nd-half IC=+0.1092, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.002, Q3_mid=+0.078, Q4=+0.159, Q5_high_vol=+0.211

**`combo_mean__first_bar_return__shaved_bar_trend_conviction`** (Lock IC=+0.0435, Sharpe=-1.0554)
- Admission: Train IC=+0.1832, Deflated=+0.1827, IR=0.55, Mono=0.68, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.065 | 2017: +0.172 | 2018: +0.188 | 2019: +0.069 | 2020: +0.116 | 2021: +0.072 | 2022: +0.037 | 2023: +0.085 | 2024: +0.094 | 2025: +0.116 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.298 | 2016: -0.018 | 2017: +0.161 | 2018: +0.249 | 2019: +0.118 | 2020: +0.181 | 2021: +0.054 | 2022: +0.165 | 2023: +0.128 | 2024: +0.188 | 2025: +0.197 | 2026: -0.302
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.50
- Early IC=+0.1799, Recent IC=+0.0898, 1st-half IC=+0.1304, 2nd-half IC=+0.0712, Neg regimes=1/5
- Weak component: `shaved_bar_trend_conviction` (CV=1.11)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.023, Q3_mid=+0.086, Q4=+0.111, Q5_high_vol=+0.139

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0426, Sharpe=-0.2324)
- Admission: Train IC=+0.2524, Deflated=+0.2516, IR=1.00, Mono=0.82, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.091 | 2017: +0.133 | 2018: +0.260 | 2019: +0.169 | 2020: +0.173 | 2021: +0.170 | 2022: +0.068 | 2023: +0.082 | 2024: +0.141 | 2025: +0.069 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.147 | 2017: +0.318 | 2018: +0.603 | 2019: +0.185 | 2020: +0.175 | 2021: +0.302 | 2022: +0.166 | 2023: +0.260 | 2024: +0.201 | 2025: -0.037 | 2026: +0.018
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.57
- Early IC=+0.1963, Recent IC=+0.1112, 1st-half IC=+0.1767, 2nd-half IC=+0.1173, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.015, Q3_mid=+0.105, Q4=+0.119, Q5_high_vol=+0.256

**`combo_min__first_bar_return__early_order_flow_imbalance`** (Lock IC=+0.0421, Sharpe=-0.1392)
- Admission: Train IC=+0.2335, Deflated=+0.2334, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.004 | 2017: +0.134 | 2018: +0.159 | 2019: +0.156 | 2020: +0.064 | 2021: +0.162 | 2022: +0.125 | 2023: +0.076 | 2024: +0.121 | 2025: +0.102 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.232 | 2016: +0.019 | 2017: +0.313 | 2018: +0.424 | 2019: +0.220 | 2020: +0.016 | 2021: +0.247 | 2022: +0.243 | 2023: +0.125 | 2024: +0.352 | 2025: +0.248 | 2026: -0.111
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.67
- Early IC=+0.1469, Recent IC=+0.0987, 1st-half IC=+0.1226, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.049, Q3_mid=+0.082, Q4=+0.136, Q5_high_vol=+0.158

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction`** (Lock IC=+0.0419, Sharpe=-1.0138)
- Admission: Train IC=+0.2381, Deflated=+0.2375, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.071 | 2017: +0.182 | 2018: +0.186 | 2019: +0.117 | 2020: +0.126 | 2021: +0.119 | 2022: +0.074 | 2023: +0.122 | 2024: +0.154 | 2025: +0.122 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.395 | 2016: +0.237 | 2017: +0.291 | 2018: +0.267 | 2019: +0.276 | 2020: +0.133 | 2021: +0.264 | 2022: +0.223 | 2023: +0.190 | 2024: +0.313 | 2025: +0.009 | 2026: +0.101
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.75
- Early IC=+0.1840, Recent IC=+0.1378, 1st-half IC=+0.1381, 2nd-half IC=+0.1240, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.031, Q3_mid=+0.128, Q4=+0.093, Q5_high_vol=+0.182

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0406, Sharpe=-1.4083)
- Admission: Train IC=+0.2700, Deflated=+0.2690, IR=1.19, Mono=0.87, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.084 | 2017: +0.227 | 2018: +0.211 | 2019: +0.123 | 2020: +0.152 | 2021: +0.131 | 2022: +0.092 | 2023: +0.112 | 2024: +0.158 | 2025: +0.106 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.239 | 2017: +0.276 | 2018: +0.342 | 2019: +0.238 | 2020: +0.198 | 2021: +0.307 | 2022: +0.234 | 2023: +0.347 | 2024: +0.214 | 2025: -0.113 | 2026: -0.303
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.61
- Early IC=+0.2193, Recent IC=+0.1347, 1st-half IC=+0.1653, 2nd-half IC=+0.1298, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.012, Q3_mid=+0.139, Q4=+0.142, Q5_high_vol=+0.202

**`combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0`** (Lock IC=+0.0397, Sharpe=-0.6619)
- Admission: Train IC=+0.2370, Deflated=+0.2365, IR=0.60, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.077 | 2017: +0.178 | 2018: +0.177 | 2019: +0.090 | 2020: +0.110 | 2021: +0.087 | 2022: +0.107 | 2023: +0.083 | 2024: +0.135 | 2025: +0.125 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.373 | 2016: +0.016 | 2017: +0.165 | 2018: +0.274 | 2019: +0.141 | 2020: +0.177 | 2021: +0.211 | 2022: +0.253 | 2023: +0.297 | 2024: +0.308 | 2025: +0.112 | 2026: -0.177
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.61
- Early IC=+0.1773, Recent IC=+0.1088, 1st-half IC=+0.1286, 2nd-half IC=+0.1078, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.016, Q3_mid=+0.118, Q4=+0.119, Q5_high_vol=+0.149

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0387, Sharpe=-0.3937)
- Admission: Train IC=+0.2409, Deflated=+0.2406, IR=0.85, Mono=0.83, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.267 | 2016: +0.093 | 2017: +0.218 | 2018: +0.243 | 2019: +0.123 | 2020: +0.124 | 2021: +0.118 | 2022: +0.088 | 2023: +0.110 | 2024: +0.100 | 2025: +0.078 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.077 | 2017: +0.331 | 2018: +0.431 | 2019: +0.160 | 2020: +0.183 | 2021: +0.214 | 2022: +0.064 | 2023: +0.262 | 2024: +0.098 | 2025: +0.095 | 2026: +0.038
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.45
- Early IC=+0.2303, Recent IC=+0.1048, 1st-half IC=+0.1619, 2nd-half IC=+0.1042, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.014, Q3_mid=+0.119, Q4=+0.169, Q5_high_vol=+0.162

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0379, Sharpe=-0.2953)
- Admission: Train IC=+0.2458, Deflated=+0.2455, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.140 | 2017: +0.199 | 2018: +0.249 | 2019: +0.128 | 2020: +0.116 | 2021: +0.133 | 2022: +0.091 | 2023: +0.094 | 2024: +0.137 | 2025: +0.097 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.169 | 2017: +0.345 | 2018: +0.475 | 2019: +0.112 | 2020: +0.193 | 2021: +0.326 | 2022: +0.128 | 2023: +0.206 | 2024: +0.180 | 2025: +0.021 | 2026: -0.233
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.52
- Early IC=+0.2236, Recent IC=+0.1159, 1st-half IC=+0.1635, 2nd-half IC=+0.1170, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.201, Q2=-0.026, Q3_mid=+0.119, Q4=+0.171, Q5_high_vol=+0.200

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0376, Sharpe=-1.6484)
- Admission: Train IC=+0.2120, Deflated=+0.2108, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.094 | 2017: +0.235 | 2018: +0.223 | 2019: +0.107 | 2020: +0.153 | 2021: +0.154 | 2022: +0.123 | 2023: +0.098 | 2024: +0.145 | 2025: +0.078 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.103 | 2017: +0.148 | 2018: +0.362 | 2019: +0.318 | 2020: +0.098 | 2021: +0.316 | 2022: +0.211 | 2023: -0.005 | 2024: +0.273 | 2025: +0.022 | 2026: -0.232
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=0.53
- Early IC=+0.2282, Recent IC=+0.1214, 1st-half IC=+0.1660, 2nd-half IC=+0.1349, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.245, Q2=+0.007, Q3_mid=+0.125, Q4=+0.154, Q5_high_vol=+0.217

**`combo_max__max_up_ret__max_down_ret`** (Lock IC=+0.0367, Sharpe=-0.9414)
- Admission: Train IC=+0.2098, Deflated=+0.2091, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.082 | 2017: +0.242 | 2018: +0.245 | 2019: +0.120 | 2020: +0.138 | 2021: +0.111 | 2022: +0.080 | 2023: +0.056 | 2024: +0.140 | 2025: +0.093 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.270 | 2016: +0.216 | 2017: +0.256 | 2018: +0.375 | 2019: +0.187 | 2020: +0.182 | 2021: +0.273 | 2022: +0.128 | 2023: +0.178 | 2024: +0.232 | 2025: -0.119 | 2026: -0.284
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.40
- Early IC=+0.2433, Recent IC=+0.0981, 1st-half IC=+0.1705, 2nd-half IC=+0.1016, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.214, Q2=-0.011, Q3_mid=+0.119, Q4=+0.116, Q5_high_vol=+0.207

**`combo_mean__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0363, Sharpe=-1.0873)
- Admission: Train IC=+0.2071, Deflated=+0.2061, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.043 | 2017: +0.212 | 2018: +0.123 | 2019: +0.096 | 2020: +0.126 | 2021: +0.110 | 2022: +0.109 | 2023: +0.116 | 2024: +0.141 | 2025: +0.125 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.208 | 2016: +0.124 | 2017: +0.224 | 2018: +0.333 | 2019: +0.300 | 2020: +0.102 | 2021: +0.276 | 2022: +0.177 | 2023: +0.365 | 2024: +0.230 | 2025: +0.043 | 2026: -0.376
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=0.77
- Early IC=+0.1675, Recent IC=+0.1283, 1st-half IC=+0.1208, 2nd-half IC=+0.1277, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.047, Q3_mid=+0.115, Q4=+0.098, Q5_high_vol=+0.152

**`combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend`** (Lock IC=+0.0356, Sharpe=-0.2960)
- Admission: Train IC=+0.1879, Deflated=+0.1873, IR=0.67, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.128 | 2016: +0.021 | 2017: +0.153 | 2018: +0.124 | 2019: +0.091 | 2020: +0.082 | 2021: +0.056 | 2022: +0.110 | 2023: +0.116 | 2024: +0.117 | 2025: +0.128 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.019 | 2017: +0.138 | 2018: +0.210 | 2019: +0.269 | 2020: +0.030 | 2021: +0.253 | 2022: +0.114 | 2023: +0.291 | 2024: +0.316 | 2025: +0.169 | 2026: -0.357
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.84
- Early IC=+0.1382, Recent IC=+0.1167, 1st-half IC=+0.0982, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.049, Q3_mid=+0.108, Q4=+0.079, Q5_high_vol=+0.125

**`combo_mean__max_up_ret__close_vs_open_range`** (Lock IC=+0.0355, Sharpe=-1.8429)
- Admission: Train IC=+0.2162, Deflated=+0.2150, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.093 | 2017: +0.212 | 2018: +0.171 | 2019: +0.086 | 2020: +0.132 | 2021: +0.101 | 2022: +0.108 | 2023: +0.101 | 2024: +0.141 | 2025: +0.115 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.281 | 2016: +0.302 | 2017: +0.261 | 2018: +0.328 | 2019: +0.142 | 2020: +0.186 | 2021: +0.276 | 2022: +0.067 | 2023: +0.173 | 2024: +0.248 | 2025: -0.060 | 2026: -0.161
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.63
- Early IC=+0.1914, Recent IC=+0.1211, 1st-half IC=+0.1340, 2nd-half IC=+0.1203, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.222, Q2=+0.019, Q3_mid=+0.123, Q4=+0.106, Q5_high_vol=+0.164

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0337, Sharpe=-1.4167)
- Admission: Train IC=+0.2577, Deflated=+0.2564, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.106 | 2017: +0.201 | 2018: +0.209 | 2019: +0.129 | 2020: +0.142 | 2021: +0.089 | 2022: +0.105 | 2023: +0.119 | 2024: +0.137 | 2025: +0.119 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.254 | 2017: +0.358 | 2018: +0.384 | 2019: +0.236 | 2020: +0.249 | 2021: +0.298 | 2022: +0.163 | 2023: +0.132 | 2024: +0.354 | 2025: -0.127 | 2026: -0.132
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.62
- Early IC=+0.2048, Recent IC=+0.1279, 1st-half IC=+0.1552, 2nd-half IC=+0.1139, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.010, Q3_mid=+0.120, Q4=+0.127, Q5_high_vol=+0.210

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0316, Sharpe=-0.2324)
- Admission: Train IC=+0.2424, Deflated=+0.2416, IR=0.93, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.109 | 2017: +0.142 | 2018: +0.285 | 2019: +0.176 | 2020: +0.171 | 2021: +0.171 | 2022: +0.054 | 2023: +0.100 | 2024: +0.158 | 2025: +0.057 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.204 | 2017: +0.304 | 2018: +0.602 | 2019: +0.184 | 2020: +0.130 | 2021: +0.293 | 2022: +0.165 | 2023: +0.256 | 2024: +0.191 | 2025: -0.034 | 2026: +0.013
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.60
- Early IC=+0.2138, Recent IC=+0.1293, 1st-half IC=+0.1855, 2nd-half IC=+0.1228, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.006, Q3_mid=+0.128, Q4=+0.134, Q5_high_vol=+0.260

**`max_up_ret`** (Lock IC=+0.0308, Sharpe=-1.6524)
- Admission: Train IC=+0.2006, Deflated=+0.1991, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.61
- Early IC=+0.2011, Recent IC=+0.1236, 1st-half IC=+0.1370, 2nd-half IC=+0.1238, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.016, Q3_mid=+0.113, Q4=+0.122, Q5_high_vol=+0.206

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0301, Sharpe=-1.2625)
- Admission: Train IC=+0.2369, Deflated=+0.2361, IR=0.76, Mono=0.80, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.110 | 2017: +0.228 | 2018: +0.249 | 2019: +0.128 | 2020: +0.166 | 2021: +0.176 | 2022: +0.108 | 2023: +0.095 | 2024: +0.149 | 2025: +0.099 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.172 | 2017: +0.169 | 2018: +0.477 | 2019: +0.136 | 2020: +0.287 | 2021: +0.359 | 2022: +0.161 | 2023: +0.116 | 2024: +0.294 | 2025: -0.058 | 2026: -0.385
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.51
- Early IC=+0.2384, Recent IC=+0.1220, 1st-half IC=+0.1779, 2nd-half IC=+0.1382, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.273, Q2=-0.018, Q3_mid=+0.133, Q4=+0.161, Q5_high_vol=+0.223

**`combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0`** (Lock IC=+0.0299, Sharpe=-1.1446)
- Admission: Train IC=+0.2440, Deflated=+0.2432, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.095 | 2017: +0.174 | 2018: +0.216 | 2019: +0.108 | 2020: +0.116 | 2021: +0.117 | 2022: +0.123 | 2023: +0.097 | 2024: +0.139 | 2025: +0.106 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.113 | 2017: +0.232 | 2018: +0.362 | 2019: +0.133 | 2020: +0.214 | 2021: +0.194 | 2022: +0.130 | 2023: +0.352 | 2024: +0.248 | 2025: -0.096 | 2026: -0.170
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.61
- Early IC=+0.1947, Recent IC=+0.1179, 1st-half IC=+0.1418, 2nd-half IC=+0.1235, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.015, Q3_mid=+0.115, Q4=+0.141, Q5_high_vol=+0.180

**`combo_min__early_order_flow_imbalance__bar_body_rng_0`** (Lock IC=+0.0295, Sharpe=-1.5145)
- Admission: Train IC=+0.2361, Deflated=+0.2364, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.155 | 2016: +0.020 | 2017: +0.167 | 2018: +0.166 | 2019: +0.145 | 2020: +0.061 | 2021: +0.149 | 2022: +0.119 | 2023: +0.082 | 2024: +0.128 | 2025: +0.087 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.285 | 2016: +0.108 | 2017: +0.198 | 2018: +0.344 | 2019: +0.291 | 2020: +0.043 | 2021: +0.176 | 2022: +0.309 | 2023: +0.040 | 2024: +0.380 | 2025: +0.216 | 2026: -0.146
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.63
- Early IC=+0.1663, Recent IC=+0.1051, 1st-half IC=+0.1264, 2nd-half IC=+0.1204, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.031, Q3_mid=+0.087, Q4=+0.160, Q5_high_vol=+0.142

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0289, Sharpe=-0.4555)
- Admission: Train IC=+0.2882, Deflated=+0.2875, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.103 | 2017: +0.142 | 2018: +0.284 | 2019: +0.177 | 2020: +0.173 | 2021: +0.171 | 2022: +0.055 | 2023: +0.093 | 2024: +0.161 | 2025: +0.060 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.093 | 2017: +0.301 | 2018: +0.612 | 2019: +0.247 | 2020: +0.024 | 2021: +0.311 | 2022: +0.155 | 2023: +0.095 | 2024: +0.368 | 2025: +0.165 | 2026: -0.193
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.2133, Recent IC=+0.1268, 1st-half IC=+0.1870, 2nd-half IC=+0.1223, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.005, Q3_mid=+0.133, Q4=+0.139, Q5_high_vol=+0.259

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0288, Sharpe=-1.9401)
- Admission: Train IC=+0.2306, Deflated=+0.2300, IR=0.86, Mono=0.82, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.66
- Early IC=+0.1956, Recent IC=+0.1299, 1st-half IC=+0.1403, 2nd-half IC=+0.1288, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.004, Q3_mid=+0.110, Q4=+0.141, Q5_high_vol=+0.218

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=+0.0281, Sharpe=-0.9455)
- Admission: Train IC=+0.2184, Deflated=+0.2177, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.110 | 2017: +0.192 | 2018: +0.241 | 2019: +0.136 | 2020: +0.113 | 2021: +0.138 | 2022: +0.101 | 2023: +0.098 | 2024: +0.142 | 2025: +0.077 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.127 | 2017: +0.255 | 2018: +0.462 | 2019: +0.112 | 2020: +0.236 | 2021: +0.269 | 2022: +0.108 | 2023: +0.143 | 2024: +0.138 | 2025: +0.044 | 2026: -0.239
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.55
- Early IC=+0.2165, Recent IC=+0.1196, 1st-half IC=+0.1561, 2nd-half IC=+0.1182, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.207, Q2=-0.013, Q3_mid=+0.109, Q4=+0.148, Q5_high_vol=+0.211

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0`** (Lock IC=+0.0276, Sharpe=-1.1415)
- Admission: Train IC=+0.2052, Deflated=+0.2045, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.096 | 2017: +0.220 | 2018: +0.243 | 2019: +0.128 | 2020: +0.136 | 2021: +0.125 | 2022: +0.072 | 2023: +0.097 | 2024: +0.159 | 2025: +0.051 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.110 | 2017: +0.259 | 2018: +0.471 | 2019: +0.113 | 2020: +0.212 | 2021: +0.310 | 2022: +0.002 | 2023: +0.131 | 2024: +0.238 | 2025: -0.203 | 2026: -0.222
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.55
- Early IC=+0.2317, Recent IC=+0.1279, 1st-half IC=+0.1680, 2nd-half IC=+0.1183, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.007, Q3_mid=+0.135, Q4=+0.131, Q5_high_vol=+0.218

**`combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0274, Sharpe=-1.6166)
- Admission: Train IC=+0.2499, Deflated=+0.2492, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.087 | 2017: +0.253 | 2018: +0.213 | 2019: +0.119 | 2020: +0.158 | 2021: +0.145 | 2022: +0.130 | 2023: +0.060 | 2024: +0.144 | 2025: +0.094 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.226 | 2016: -0.024 | 2017: +0.255 | 2018: +0.368 | 2019: +0.225 | 2020: +0.282 | 2021: +0.265 | 2022: +0.216 | 2023: +0.287 | 2024: +0.220 | 2025: -0.038 | 2026: -0.359
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.44
- Early IC=+0.2332, Recent IC=+0.1020, 1st-half IC=+0.1700, 2nd-half IC=+0.1294, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.249, Q2=+0.004, Q3_mid=+0.136, Q4=+0.150, Q5_high_vol=+0.201

**`combo_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0264, Sharpe=-1.6594)
- Admission: Train IC=+0.2013, Deflated=+0.2001, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.097 | 2017: +0.210 | 2018: +0.207 | 2019: +0.096 | 2020: +0.140 | 2021: +0.083 | 2022: +0.118 | 2023: +0.096 | 2024: +0.131 | 2025: +0.082 | 2026: -0.042
- Yearly Tail ICs:   2015: +0.315 | 2016: +0.260 | 2017: +0.185 | 2018: +0.337 | 2019: +0.159 | 2020: +0.179 | 2021: +0.212 | 2022: +0.082 | 2023: +0.178 | 2024: +0.297 | 2025: -0.243 | 2026: -0.416
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.54
- Early IC=+0.2084, Recent IC=+0.1134, 1st-half IC=+0.1515, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.005, Q3_mid=+0.134, Q4=+0.120, Q5_high_vol=+0.188

**`combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend`** (Lock IC=+0.0240, Sharpe=-0.7203)
- Admission: Train IC=+0.1654, Deflated=+0.1646, IR=0.64, Mono=0.72, p=0.0014, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.038 | 2016: +0.029 | 2017: +0.098 | 2018: +0.096 | 2019: +0.066 | 2020: +0.074 | 2021: +0.049 | 2022: +0.092 | 2023: +0.126 | 2024: +0.088 | 2025: +0.122 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.019 | 2017: +0.100 | 2018: +0.210 | 2019: +0.179 | 2020: +0.030 | 2021: +0.241 | 2022: +0.060 | 2023: +0.291 | 2024: +0.236 | 2025: +0.213 | 2026: -0.357
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=1.10
- Early IC=+0.0971, Recent IC=+0.1069, 1st-half IC=+0.0766, 2nd-half IC=+0.0908, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.038, Q3_mid=+0.097, Q4=+0.058, Q5_high_vol=+0.074

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum`** (Lock IC=+0.0237, Sharpe=-1.6714)
- Admission: Train IC=+0.2216, Deflated=+0.2203, IR=0.82, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.244 | 2016: +0.108 | 2017: +0.212 | 2018: +0.206 | 2019: +0.089 | 2020: +0.170 | 2021: +0.110 | 2022: +0.126 | 2023: +0.077 | 2024: +0.142 | 2025: +0.078 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.226 | 2016: +0.262 | 2017: +0.363 | 2018: +0.325 | 2019: +0.072 | 2020: +0.216 | 2021: +0.178 | 2022: +0.175 | 2023: +0.180 | 2024: +0.248 | 2025: -0.170 | 2026: -0.307
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.52
- Early IC=+0.2091, Recent IC=+0.1097, 1st-half IC=+0.1606, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.009, Q3_mid=+0.129, Q4=+0.164, Q5_high_vol=+0.183

**`combo_rank_max__bar_ret_0__close_vs_open_range`** (Lock IC=+0.0231, Sharpe=-2.4234)
- Admission: Train IC=+0.2430, Deflated=+0.2424, IR=1.01, Mono=0.85, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.113 | 2017: +0.209 | 2018: +0.216 | 2019: +0.103 | 2020: +0.141 | 2021: +0.128 | 2022: +0.124 | 2023: +0.086 | 2024: +0.140 | 2025: +0.119 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.042 | 2017: +0.263 | 2018: +0.327 | 2019: +0.151 | 2020: +0.314 | 2021: +0.258 | 2022: +0.267 | 2023: +0.316 | 2024: +0.271 | 2025: -0.123 | 2026: -0.469
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.53
- Early IC=+0.2095, Recent IC=+0.1107, 1st-half IC=+0.1511, 2nd-half IC=+0.1235, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.014, Q3_mid=+0.150, Q4=+0.145, Q5_high_vol=+0.156

**`combo_rank_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0224, Sharpe=-1.5381)
- Admission: Train IC=+0.1943, Deflated=+0.1932, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.103 | 2017: +0.203 | 2018: +0.170 | 2019: +0.101 | 2020: +0.139 | 2021: +0.094 | 2022: +0.120 | 2023: +0.128 | 2024: +0.134 | 2025: +0.095 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.255 | 2016: +0.139 | 2017: +0.157 | 2018: +0.289 | 2019: +0.203 | 2020: +0.112 | 2021: +0.111 | 2022: +0.114 | 2023: +0.408 | 2024: +0.211 | 2025: -0.160 | 2026: -0.477
- IC CV=0.24, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.70
- Early IC=+0.1881, Recent IC=+0.1323, 1st-half IC=+0.1352, 2nd-half IC=+0.1314, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.054, Q3_mid=+0.116, Q4=+0.100, Q5_high_vol=+0.177

**`combo_mean__bar_ret_0__early_order_flow_imbalance`** (Lock IC=+0.0219, Sharpe=-1.0783)
- Admission: Train IC=+0.2516, Deflated=+0.2518, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.031 | 2017: +0.138 | 2018: +0.194 | 2019: +0.136 | 2020: +0.074 | 2021: +0.130 | 2022: +0.120 | 2023: +0.074 | 2024: +0.118 | 2025: +0.088 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.189 | 2016: -0.084 | 2017: +0.139 | 2018: +0.389 | 2019: +0.256 | 2020: +0.104 | 2021: +0.358 | 2022: +0.275 | 2023: +0.318 | 2024: +0.294 | 2025: +0.089 | 2026: -0.292
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.58
- Early IC=+0.1661, Recent IC=+0.0958, 1st-half IC=+0.1309, 2nd-half IC=+0.1125, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.038, Q3_mid=+0.086, Q4=+0.133, Q5_high_vol=+0.161

**`combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0`** (Lock IC=+0.0212, Sharpe=-2.2125)
- Admission: Train IC=+0.2354, Deflated=+0.2348, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.104 | 2017: +0.179 | 2018: +0.210 | 2019: +0.078 | 2020: +0.128 | 2021: +0.098 | 2022: +0.125 | 2023: +0.073 | 2024: +0.124 | 2025: +0.127 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.101 | 2017: +0.239 | 2018: +0.221 | 2019: +0.125 | 2020: +0.330 | 2021: +0.165 | 2022: +0.254 | 2023: +0.415 | 2024: +0.226 | 2025: -0.110 | 2026: -0.546
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.51
- Early IC=+0.1945, Recent IC=+0.0984, 1st-half IC=+0.1381, 2nd-half IC=+0.1109, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.012, Q3_mid=+0.132, Q4=+0.142, Q5_high_vol=+0.149

**`combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0`** (Lock IC=+0.0201, Sharpe=-1.9420)
- Admission: Train IC=+0.2448, Deflated=+0.2443, IR=0.80, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.115 | 2017: +0.150 | 2018: +0.259 | 2019: +0.109 | 2020: +0.116 | 2021: +0.107 | 2022: +0.119 | 2023: +0.077 | 2024: +0.141 | 2025: +0.107 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.266 | 2017: +0.186 | 2018: +0.393 | 2019: +0.163 | 2020: +0.276 | 2021: +0.212 | 2022: +0.212 | 2023: +0.399 | 2024: +0.276 | 2025: -0.162 | 2026: -0.401
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.78, Recency ratio=0.53
- Early IC=+0.2045, Recent IC=+0.1091, 1st-half IC=+0.1494, 2nd-half IC=+0.1158, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.010, Q3_mid=+0.107, Q4=+0.152, Q5_high_vol=+0.201

**`combo_max__first_bar_return__vwap_close_divergence_trend`** (Lock IC=+0.0170, Sharpe=-1.9514)
- Admission: Train IC=+0.1999, Deflated=+0.1994, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.110 | 2017: +0.176 | 2018: +0.192 | 2019: +0.101 | 2020: +0.109 | 2021: +0.157 | 2022: +0.114 | 2023: +0.118 | 2024: +0.122 | 2025: +0.132 | 2026: -0.110
- Yearly Tail ICs:   2015: +0.291 | 2016: -0.052 | 2017: +0.100 | 2018: +0.309 | 2019: +0.234 | 2020: +0.143 | 2021: +0.202 | 2022: +0.169 | 2023: +0.412 | 2024: +0.127 | 2025: -0.109 | 2026: -0.558
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=0.65
- Early IC=+0.1838, Recent IC=+0.1201, 1st-half IC=+0.1242, 2nd-half IC=+0.1343, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.038, Q3_mid=+0.135, Q4=+0.105, Q5_high_vol=+0.158

**`combo_max__max_up_ret__vwap_close_divergence_trend`** (Lock IC=+0.0170, Sharpe=-2.4149)
- Admission: Train IC=+0.1896, Deflated=+0.1885, IR=0.86, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.106 | 2017: +0.199 | 2018: +0.171 | 2019: +0.103 | 2020: +0.131 | 2021: +0.091 | 2022: +0.124 | 2023: +0.124 | 2024: +0.129 | 2025: +0.092 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.176 | 2017: +0.165 | 2018: +0.311 | 2019: +0.209 | 2020: +0.110 | 2021: +0.213 | 2022: +0.113 | 2023: +0.417 | 2024: +0.219 | 2025: -0.168 | 2026: -0.484
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.68
- Early IC=+0.1848, Recent IC=+0.1264, 1st-half IC=+0.1361, 2nd-half IC=+0.1280, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.060, Q3_mid=+0.115, Q4=+0.090, Q5_high_vol=+0.174

**`combo_rank_max__bar_ret_0__vwap_close_divergence_trend`** (Lock IC=+0.0161, Sharpe=-2.1485)
- Admission: Train IC=+0.2046, Deflated=+0.2042, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.114 | 2017: +0.179 | 2018: +0.194 | 2019: +0.102 | 2020: +0.110 | 2021: +0.153 | 2022: +0.110 | 2023: +0.122 | 2024: +0.124 | 2025: +0.132 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.258 | 2016: -0.034 | 2017: +0.134 | 2018: +0.351 | 2019: +0.208 | 2020: +0.214 | 2021: +0.196 | 2022: +0.233 | 2023: +0.407 | 2024: +0.103 | 2025: -0.061 | 2026: -0.476
- IC CV=0.23, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.66
- Early IC=+0.1853, Recent IC=+0.1216, 1st-half IC=+0.1262, 2nd-half IC=+0.1326, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.039, Q3_mid=+0.137, Q4=+0.103, Q5_high_vol=+0.159

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0126, Sharpe=-2.1701)
- Admission: Train IC=+0.2447, Deflated=+0.2444, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.125 | 2017: +0.154 | 2018: +0.226 | 2019: +0.083 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.126 | 2025: +0.122 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.099 | 2017: +0.215 | 2018: +0.264 | 2019: +0.075 | 2020: +0.348 | 2021: +0.179 | 2022: +0.303 | 2023: +0.395 | 2024: +0.216 | 2025: -0.102 | 2026: -0.544
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.54
- Early IC=+0.1898, Recent IC=+0.1018, 1st-half IC=+0.1402, 2nd-half IC=+0.1035, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.016, Q3_mid=+0.129, Q4=+0.151, Q5_high_vol=+0.147

**`combo_diff__max_up_ret__h2_l2_pullback_continuation`** (Lock IC=+0.0087, Sharpe=-2.1212)
- Admission: Train IC=+0.1950, Deflated=+0.1938, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.095 | 2017: +0.174 | 2018: +0.128 | 2019: +0.083 | 2020: +0.122 | 2021: +0.065 | 2022: +0.112 | 2023: +0.116 | 2024: +0.134 | 2025: +0.086 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.295 | 2016: +0.342 | 2017: +0.129 | 2018: +0.303 | 2019: +0.146 | 2020: +0.104 | 2021: +0.236 | 2022: +0.139 | 2023: +0.316 | 2024: +0.252 | 2025: -0.199 | 2026: -0.187
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.83
- Early IC=+0.1511, Recent IC=+0.1252, 1st-half IC=+0.1149, 2nd-half IC=+0.1147, Neg regimes=0/5
- Weak component: `h2_l2_pullback_continuation` (CV=0.45)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.010, Q3_mid=+0.138, Q4=+0.104, Q5_high_vol=+0.135

### 159915ETF — `single` Median Features

**`combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1224, Sharpe=-0.2137)
- Admission: Train IC=+0.1943, Deflated=+0.1936, IR=0.48, Mono=0.67, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.048 | 2017: +0.032 | 2018: +0.054 | 2019: +0.123 | 2020: +0.107 | 2021: +0.157 | 2022: +0.084 | 2023: +0.071 | 2024: +0.090 | 2025: +0.192 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.085 | 2016: +0.156 | 2017: -0.080 | 2018: +0.142 | 2019: +0.312 | 2020: +0.157 | 2021: +0.320 | 2022: +0.184 | 2023: +0.033 | 2024: +0.211 | 2025: -0.019 | 2026: -0.054
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=1.32, Recency ratio=1.89
- Early IC=+0.0429, Recent IC=+0.0809, 1st-half IC=+0.0834, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.029, Q3_mid=+0.139, Q4=+0.180, Q5_high_vol=+0.097

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1193, Sharpe=-0.2201)
- Admission: Train IC=+0.2001, Deflated=+0.1990, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.161 | 2017: +0.030 | 2018: +0.132 | 2019: +0.123 | 2020: +0.132 | 2021: +0.160 | 2022: +0.154 | 2023: +0.136 | 2024: +0.080 | 2025: +0.147 | 2026: +0.107
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.148 | 2017: +0.200 | 2018: +0.323 | 2019: +0.164 | 2020: +0.081 | 2021: +0.457 | 2022: +0.123 | 2023: +0.282 | 2024: +0.169 | 2025: +0.125 | 2026: +0.096
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.28, Recency ratio=1.32
- Early IC=+0.0818, Recent IC=+0.1079, 1st-half IC=+0.1090, 2nd-half IC=+0.1393, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.130, Q3_mid=+0.090, Q4=+0.118, Q5_high_vol=+0.167

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1106, Sharpe=-0.0225)
- Admission: Train IC=+0.2480, Deflated=+0.2465, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.058 | 2017: +0.017 | 2018: +0.079 | 2019: +0.182 | 2020: +0.098 | 2021: +0.155 | 2022: +0.144 | 2023: +0.152 | 2024: +0.075 | 2025: +0.182 | 2026: -0.004
- Yearly Tail ICs:   2015: -0.021 | 2016: +0.267 | 2017: -0.021 | 2018: +0.116 | 2019: +0.383 | 2020: +0.205 | 2021: +0.341 | 2022: +0.349 | 2023: +0.332 | 2024: +0.263 | 2025: +0.229 | 2026: -0.221
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.53, Recency ratio=2.35
- Early IC=+0.0482, Recent IC=+0.1135, 1st-half IC=+0.0936, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.118, Q3_mid=+0.110, Q4=+0.107, Q5_high_vol=+0.159

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0939, Sharpe=-0.4022)
- Admission: Train IC=+0.2165, Deflated=+0.2165, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.100 | 2017: +0.028 | 2018: +0.120 | 2019: +0.193 | 2020: +0.109 | 2021: +0.137 | 2022: +0.077 | 2023: +0.192 | 2024: +0.058 | 2025: +0.147 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.055 | 2017: +0.048 | 2018: +0.293 | 2019: +0.344 | 2020: +0.167 | 2021: +0.174 | 2022: +0.124 | 2023: +0.496 | 2024: +0.175 | 2025: +0.282 | 2026: +0.072
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.69
- Early IC=+0.0741, Recent IC=+0.1249, 1st-half IC=+0.1057, 2nd-half IC=+0.1200, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.108, Q3_mid=+0.082, Q4=+0.083, Q5_high_vol=+0.145

**`combo_rank_max__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0919, Sharpe=-0.8343)
- Admission: Train IC=+0.2039, Deflated=+0.2024, IR=0.75, Mono=0.72, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.040 | 2017: +0.033 | 2018: +0.085 | 2019: +0.130 | 2020: +0.074 | 2021: +0.174 | 2022: +0.173 | 2023: +0.138 | 2024: +0.083 | 2025: +0.135 | 2026: +0.066
- Yearly Tail ICs:   2015: -0.079 | 2016: +0.151 | 2017: +0.228 | 2018: +0.286 | 2019: +0.176 | 2020: +0.034 | 2021: +0.404 | 2022: +0.201 | 2023: +0.136 | 2024: +0.197 | 2025: +0.015 | 2026: -0.068
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.85, Recency ratio=1.86
- Early IC=+0.0596, Recent IC=+0.1108, 1st-half IC=+0.0801, 2nd-half IC=+0.1485, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.124, Q3_mid=+0.076, Q4=+0.117, Q5_high_vol=+0.146

**`combo_max__bar_ret_0__volatility_expansion_trend_vector`** (Lock IC=+0.0894, Sharpe=-0.0643)
- Admission: Train IC=+0.1936, Deflated=+0.1931, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.082 | 2017: +0.048 | 2018: +0.080 | 2019: +0.128 | 2020: +0.122 | 2021: +0.182 | 2022: +0.084 | 2023: +0.159 | 2024: +0.070 | 2025: +0.205 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.147 | 2016: -0.188 | 2017: +0.139 | 2018: +0.220 | 2019: +0.259 | 2020: +0.048 | 2021: +0.310 | 2022: +0.198 | 2023: +0.386 | 2024: +0.140 | 2025: +0.366 | 2026: -0.590
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.56, Recency ratio=1.78
- Early IC=+0.0640, Recent IC=+0.1141, 1st-half IC=+0.0835, 2nd-half IC=+0.1298, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.083, Q3_mid=+0.143, Q4=+0.081, Q5_high_vol=+0.110

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0890, Sharpe=-0.9988)
- Admission: Train IC=+0.2466, Deflated=+0.2467, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.142 | 2017: +0.007 | 2018: +0.120 | 2019: +0.193 | 2020: +0.128 | 2021: +0.160 | 2022: +0.095 | 2023: +0.173 | 2024: +0.058 | 2025: +0.173 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.164 | 2017: -0.001 | 2018: +0.271 | 2019: +0.369 | 2020: +0.256 | 2021: +0.256 | 2022: +0.228 | 2023: +0.533 | 2024: +0.192 | 2025: +0.073 | 2026: -0.090
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.27, Recency ratio=1.83
- Early IC=+0.0633, Recent IC=+0.1156, 1st-half IC=+0.1027, 2nd-half IC=+0.1300, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.103, Q3_mid=+0.101, Q4=+0.097, Q5_high_vol=+0.143

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0888, Sharpe=-0.2203)
- Admission: Train IC=+0.2380, Deflated=+0.2374, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=3.58, Recency ratio=7.87
- Early IC=+0.0162, Recent IC=+0.1273, 1st-half IC=+0.0393, 2nd-half IC=+0.1406, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.081, Q3_mid=+0.125, Q4=+0.048, Q5_high_vol=+0.091

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0882, Sharpe=-1.0149)
- Admission: Train IC=+0.2457, Deflated=+0.2456, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.149 | 2017: +0.001 | 2018: +0.089 | 2019: +0.181 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.152 | 2024: +0.062 | 2025: +0.186 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.024 | 2017: +0.040 | 2018: +0.261 | 2019: +0.408 | 2020: +0.180 | 2021: +0.310 | 2022: +0.269 | 2023: +0.345 | 2024: +0.233 | 2025: +0.245 | 2026: -0.185
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.47, Recency ratio=2.43
- Early IC=+0.0440, Recent IC=+0.1067, 1st-half IC=+0.0878, 2nd-half IC=+0.1293, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.090, Q3_mid=+0.099, Q4=+0.098, Q5_high_vol=+0.129

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0864, Sharpe=-0.0202)
- Admission: Train IC=+0.2387, Deflated=+0.2388, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.133 | 2017: +0.004 | 2018: +0.112 | 2019: +0.211 | 2020: +0.115 | 2021: +0.146 | 2022: +0.058 | 2023: +0.175 | 2024: +0.078 | 2025: +0.162 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.404 | 2016: +0.065 | 2017: +0.104 | 2018: +0.208 | 2019: +0.407 | 2020: +0.215 | 2021: +0.196 | 2022: +0.136 | 2023: +0.340 | 2024: +0.313 | 2025: +0.257 | 2026: -0.091
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.19
- Early IC=+0.0577, Recent IC=+0.1265, 1st-half IC=+0.0977, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.065, Q3_mid=+0.116, Q4=+0.081, Q5_high_vol=+0.149

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0824, Sharpe=-0.6121)
- Admission: Train IC=+0.2351, Deflated=+0.2346, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.75, Recency ratio=2.75
- Early IC=+0.0487, Recent IC=+0.1341, 1st-half IC=+0.0845, 2nd-half IC=+0.1480, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.098, Q3_mid=+0.118, Q4=+0.089, Q5_high_vol=+0.146

**`combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0814, Sharpe=-0.3638)
- Admission: Train IC=+0.1828, Deflated=+0.1810, IR=0.66, Mono=0.72, p=0.0004, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.065 | 2017: +0.024 | 2018: +0.078 | 2019: +0.119 | 2020: +0.111 | 2021: +0.163 | 2022: +0.155 | 2023: +0.156 | 2024: +0.093 | 2025: +0.140 | 2026: +0.036
- Yearly Tail ICs:   2015: -0.150 | 2016: +0.187 | 2017: +0.080 | 2018: +0.247 | 2019: +0.261 | 2020: +0.009 | 2021: +0.353 | 2022: +0.233 | 2023: +0.220 | 2024: +0.211 | 2025: -0.070 | 2026: -0.211
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.79, Recency ratio=2.45
- Early IC=+0.0510, Recent IC=+0.1249, 1st-half IC=+0.0817, 2nd-half IC=+0.1465, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.140, Q3_mid=+0.077, Q4=+0.112, Q5_high_vol=+0.159

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0811, Sharpe=-0.6874)
- Admission: Train IC=+0.2034, Deflated=+0.2027, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.087 | 2017: +0.027 | 2018: +0.118 | 2019: +0.128 | 2020: +0.090 | 2021: +0.173 | 2022: +0.157 | 2023: +0.131 | 2024: +0.081 | 2025: +0.139 | 2026: +0.016
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.151 | 2017: +0.167 | 2018: +0.301 | 2019: +0.161 | 2020: +0.121 | 2021: +0.462 | 2022: +0.224 | 2023: +0.219 | 2024: +0.193 | 2025: +0.109 | 2026: -0.204
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.58, Recency ratio=1.46
- Early IC=+0.0724, Recent IC=+0.1058, 1st-half IC=+0.0903, 2nd-half IC=+0.1425, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.107, Q3_mid=+0.085, Q4=+0.122, Q5_high_vol=+0.144

**`combo_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0776, Sharpe=-0.3109)
- Admission: Train IC=+0.1777, Deflated=+0.1777, IR=0.49, Mono=0.66, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.086 | 2017: +0.034 | 2018: +0.102 | 2019: +0.189 | 2020: +0.103 | 2021: +0.167 | 2022: +0.052 | 2023: +0.185 | 2024: +0.081 | 2025: +0.154 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.186 | 2016: -0.025 | 2017: +0.139 | 2018: +0.308 | 2019: +0.197 | 2020: +0.033 | 2021: +0.314 | 2022: +0.050 | 2023: +0.381 | 2024: +0.107 | 2025: +0.301 | 2026: -0.177
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.28, Recency ratio=1.96
- Early IC=+0.0677, Recent IC=+0.1326, 1st-half IC=+0.0974, 2nd-half IC=+0.1245, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.065, Q3_mid=+0.113, Q4=+0.081, Q5_high_vol=+0.155

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0772, Sharpe=-0.5386)
- Admission: Train IC=+0.2313, Deflated=+0.2317, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.084 | 2017: +0.064 | 2018: +0.067 | 2019: +0.173 | 2020: +0.066 | 2021: +0.220 | 2022: +0.089 | 2023: +0.165 | 2024: +0.079 | 2025: +0.179 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.017 | 2017: +0.238 | 2018: +0.208 | 2019: +0.343 | 2020: -0.017 | 2021: +0.310 | 2022: +0.236 | 2023: +0.279 | 2024: +0.249 | 2025: +0.235 | 2026: -0.216
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.77, Recency ratio=1.84
- Early IC=+0.0661, Recent IC=+0.1215, 1st-half IC=+0.0833, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.100, Q3_mid=+0.135, Q4=+0.115, Q5_high_vol=+0.121

**`combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0738, Sharpe=-0.4608)
- Admission: Train IC=+0.2167, Deflated=+0.2161, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.048 | 2017: +0.034 | 2018: +0.052 | 2019: +0.170 | 2020: +0.084 | 2021: +0.138 | 2022: +0.103 | 2023: +0.181 | 2024: +0.111 | 2025: +0.189 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.235 | 2016: -0.022 | 2017: +0.072 | 2018: +0.002 | 2019: +0.387 | 2020: +0.241 | 2021: +0.134 | 2022: +0.318 | 2023: +0.381 | 2024: +0.250 | 2025: +0.281 | 2026: -0.189
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.80, Recency ratio=3.40
- Early IC=+0.0429, Recent IC=+0.1461, 1st-half IC=+0.0778, 2nd-half IC=+0.1399, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.082, Q3_mid=+0.146, Q4=+0.068, Q5_high_vol=+0.115

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0732, Sharpe=-0.9166)
- Admission: Train IC=+0.2401, Deflated=+0.2408, IR=0.66, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.084 | 2017: +0.059 | 2018: +0.069 | 2019: +0.178 | 2020: +0.049 | 2021: +0.219 | 2022: +0.083 | 2023: +0.163 | 2024: +0.082 | 2025: +0.177 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.063 | 2017: +0.216 | 2018: +0.221 | 2019: +0.339 | 2020: +0.069 | 2021: +0.343 | 2022: +0.241 | 2023: +0.367 | 2024: +0.254 | 2025: +0.200 | 2026: -0.243
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.87, Recency ratio=1.92
- Early IC=+0.0637, Recent IC=+0.1225, 1st-half IC=+0.0786, 2nd-half IC=+0.1470, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.103, Q3_mid=+0.128, Q4=+0.117, Q5_high_vol=+0.120

**`combo_mean__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0727, Sharpe=-0.3605)
- Admission: Train IC=+0.2438, Deflated=+0.2433, IR=1.00, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.066 | 2017: +0.046 | 2018: +0.087 | 2019: +0.175 | 2020: +0.094 | 2021: +0.153 | 2022: +0.105 | 2023: +0.197 | 2024: +0.088 | 2025: +0.175 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.105 | 2017: +0.127 | 2018: +0.249 | 2019: +0.346 | 2020: +0.204 | 2021: +0.254 | 2022: +0.306 | 2023: +0.592 | 2024: +0.208 | 2025: +0.055 | 2026: -0.308
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.57, Recency ratio=2.14
- Early IC=+0.0666, Recent IC=+0.1425, 1st-half IC=+0.0911, 2nd-half IC=+0.1426, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.101, Q3_mid=+0.133, Q4=+0.100, Q5_high_vol=+0.130

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`** (Lock IC=+0.0717, Sharpe=-1.1315)
- Admission: Train IC=+0.2299, Deflated=+0.2298, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.104 | 2017: +0.033 | 2018: +0.088 | 2019: +0.181 | 2020: +0.104 | 2021: +0.190 | 2022: +0.097 | 2023: +0.184 | 2024: +0.074 | 2025: +0.172 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.115 | 2017: +0.094 | 2018: +0.212 | 2019: +0.301 | 2020: +0.078 | 2021: +0.332 | 2022: +0.298 | 2023: +0.372 | 2024: +0.166 | 2025: +0.220 | 2026: -0.367
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.52, Recency ratio=2.13
- Early IC=+0.0606, Recent IC=+0.1293, 1st-half IC=+0.0941, 2nd-half IC=+0.1427, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.081, Q3_mid=+0.140, Q4=+0.100, Q5_high_vol=+0.135

**`combo_rank_min__opening_drive_thrust_ratio__rally_strength_max`** (Lock IC=+0.0711, Sharpe=-0.1790)
- Admission: Train IC=+0.2444, Deflated=+0.2446, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.138 | 2016: -0.014 | 2017: +0.043 | 2018: +0.071 | 2019: +0.151 | 2020: +0.020 | 2021: +0.201 | 2022: +0.040 | 2023: +0.144 | 2024: +0.066 | 2025: +0.170 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.279 | 2016: -0.126 | 2017: +0.073 | 2018: +0.159 | 2019: +0.304 | 2020: +0.149 | 2021: +0.334 | 2022: +0.188 | 2023: +0.383 | 2024: +0.072 | 2025: +0.091 | 2026: -0.042
- IC CV=0.63, Neg years (linear/tail)=0/0 of 8, Half ratio=1.97, Recency ratio=1.96
- Early IC=+0.0569, Recent IC=+0.1113, 1st-half IC=+0.0635, 2nd-half IC=+0.1251, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.076, Q3_mid=+0.173, Q4=+0.104, Q5_high_vol=+0.073

**`combo_max__max_up_ret__rally_strength_max`** (Lock IC=+0.0701, Sharpe=-0.7883)
- Admission: Train IC=+0.2262, Deflated=+0.2255, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.040 | 2017: +0.040 | 2018: +0.056 | 2019: +0.150 | 2020: +0.043 | 2021: +0.166 | 2022: +0.063 | 2023: +0.145 | 2024: +0.041 | 2025: +0.186 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.107 | 2016: +0.107 | 2017: +0.004 | 2018: +0.184 | 2019: +0.338 | 2020: +0.185 | 2021: +0.308 | 2022: +0.224 | 2023: +0.346 | 2024: +0.259 | 2025: +0.146 | 2026: -0.260
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=1.72, Recency ratio=1.94
- Early IC=+0.0478, Recent IC=+0.0927, 1st-half IC=+0.0645, 2nd-half IC=+0.1109, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.055, Q3_mid=+0.126, Q4=+0.126, Q5_high_vol=+0.069

**`combo_rank_min__max_up_ret__rally_strength_max`** (Lock IC=+0.0683, Sharpe=-0.5163)
- Admission: Train IC=+0.1964, Deflated=+0.1959, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.024 | 2017: +0.057 | 2018: +0.028 | 2019: +0.158 | 2020: +0.057 | 2021: +0.210 | 2022: +0.036 | 2023: +0.123 | 2024: +0.061 | 2025: +0.161 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.104 | 2017: +0.125 | 2018: +0.141 | 2019: +0.224 | 2020: +0.124 | 2021: +0.430 | 2022: +0.207 | 2023: +0.282 | 2024: +0.152 | 2025: +0.161 | 2026: -0.146
- IC CV=0.62, Neg years (linear/tail)=0/0 of 8, Half ratio=1.84, Recency ratio=2.11
- Early IC=+0.0452, Recent IC=+0.0956, 1st-half IC=+0.0663, 2nd-half IC=+0.1223, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.071, Q3_mid=+0.186, Q4=+0.083, Q5_high_vol=+0.068

**`combo_max__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0655, Sharpe=-0.4261)
- Admission: Train IC=+0.2299, Deflated=+0.2306, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.113 | 2017: +0.043 | 2018: +0.114 | 2019: +0.179 | 2020: +0.160 | 2021: +0.148 | 2022: +0.086 | 2023: +0.103 | 2024: +0.070 | 2025: +0.131 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.144 | 2016: +0.144 | 2017: +0.036 | 2018: +0.270 | 2019: +0.275 | 2020: +0.202 | 2021: +0.336 | 2022: +0.174 | 2023: +0.323 | 2024: +0.325 | 2025: +0.067 | 2026: -0.109
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=1.11
- Early IC=+0.0784, Recent IC=+0.0869, 1st-half IC=+0.1179, 2nd-half IC=+0.1127, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.081, Q3_mid=+0.118, Q4=+0.110, Q5_high_vol=+0.150

**`combo_min__bar_ret_0__directional_volume_signature`** (Lock IC=+0.0625, Sharpe=-0.1555)
- Admission: Train IC=+0.1572, Deflated=+0.1579, IR=0.59, Mono=0.73, p=0.0026, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.135 | 2017: +0.017 | 2018: +0.071 | 2019: +0.202 | 2020: +0.143 | 2021: +0.083 | 2022: +0.053 | 2023: +0.120 | 2024: +0.109 | 2025: +0.059 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.494 | 2016: +0.098 | 2017: +0.044 | 2018: +0.049 | 2019: +0.255 | 2020: +0.200 | 2021: +0.113 | 2022: +0.138 | 2023: +0.466 | 2024: +0.252 | 2025: +0.121 | 2026: +0.359
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=2.61
- Early IC=+0.0439, Recent IC=+0.1145, 1st-half IC=+0.1015, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=1.20)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.088, Q3_mid=+0.040, Q4=+0.076, Q5_high_vol=+0.144

**`combo_ratio__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0578, Sharpe=-1.3521)
- Admission: Train IC=+0.2064, Deflated=+0.2048, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.073 | 2017: +0.042 | 2018: +0.065 | 2019: +0.114 | 2020: +0.116 | 2021: +0.149 | 2022: +0.125 | 2023: +0.172 | 2024: +0.068 | 2025: +0.139 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.155 | 2016: +0.198 | 2017: +0.116 | 2018: +0.188 | 2019: +0.331 | 2020: +0.198 | 2021: +0.354 | 2022: +0.282 | 2023: +0.312 | 2024: +0.290 | 2025: +0.103 | 2026: -0.370
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.77, Recency ratio=2.25
- Early IC=+0.0533, Recent IC=+0.1201, 1st-half IC=+0.0753, 2nd-half IC=+0.1335, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.095, Q3_mid=+0.094, Q4=+0.082, Q5_high_vol=+0.122

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.0500, Sharpe=-0.8383)
- Admission: Train IC=+0.2344, Deflated=+0.2339, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.101 | 2017: +0.050 | 2018: +0.069 | 2019: +0.165 | 2020: +0.095 | 2021: +0.159 | 2022: +0.095 | 2023: +0.169 | 2024: +0.076 | 2025: +0.135 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.381 | 2016: +0.139 | 2017: +0.175 | 2018: +0.143 | 2019: +0.340 | 2020: +0.179 | 2021: +0.283 | 2022: +0.213 | 2023: +0.481 | 2024: +0.214 | 2025: +0.109 | 2026: -0.155
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.64, Recency ratio=2.07
- Early IC=+0.0592, Recent IC=+0.1225, 1st-half IC=+0.0803, 2nd-half IC=+0.1321, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.075, Q3_mid=+0.120, Q4=+0.100, Q5_high_vol=+0.112

**`combo_ratio__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0378, Sharpe=-1.7135)
- Admission: Train IC=+0.1858, Deflated=+0.1848, IR=0.62, Mono=0.72, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.055 | 2017: +0.032 | 2018: +0.028 | 2019: +0.120 | 2020: +0.113 | 2021: +0.149 | 2022: +0.110 | 2023: +0.150 | 2024: +0.057 | 2025: +0.127 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.084 | 2016: +0.084 | 2017: +0.055 | 2018: +0.093 | 2019: +0.379 | 2020: +0.196 | 2021: +0.168 | 2022: +0.133 | 2023: +0.250 | 2024: +0.184 | 2025: +0.173 | 2026: -0.348
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=2.04, Recency ratio=3.43
- Early IC=+0.0302, Recent IC=+0.1036, 1st-half IC=+0.0623, 2nd-half IC=+0.1269, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.058, Q3_mid=+0.109, Q4=+0.046, Q5_high_vol=+0.132

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0366, Sharpe=-0.6946)
- Admission: Train IC=+0.1947, Deflated=+0.1949, IR=0.88, Mono=0.81, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.083 | 2016: +0.041 | 2017: +0.086 | 2018: +0.110 | 2019: +0.176 | 2020: +0.053 | 2021: +0.141 | 2022: +0.085 | 2023: +0.175 | 2024: +0.128 | 2025: +0.123 | 2026: -0.082
- Yearly Tail ICs:   2015: -0.248 | 2016: +0.198 | 2017: +0.162 | 2018: +0.240 | 2019: +0.254 | 2020: +0.156 | 2021: +0.147 | 2022: +0.191 | 2023: +0.389 | 2024: +0.298 | 2025: -0.010 | 2026: -0.104
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.47, Recency ratio=1.54
- Early IC=+0.0983, Recent IC=+0.1515, 1st-half IC=+0.0939, 2nd-half IC=+0.1380, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.078, Q3_mid=+0.115, Q4=+0.096, Q5_high_vol=+0.136

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0592, Sharpe=+0.5373)
- Admission: Train IC=+0.2034, Deflated=+0.2025, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.114 | 2017: +0.000 | 2018: +0.208 | 2019: +0.104 | 2020: +0.048 | 2021: +0.143 | 2022: +0.085 | 2023: +0.105 | 2024: +0.016 | 2025: +0.065 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.119 | 2017: +0.028 | 2018: +0.272 | 2019: +0.237 | 2020: +0.158 | 2021: +0.424 | 2022: +0.269 | 2023: +0.077 | 2024: +0.168 | 2025: +0.225 | 2026: +0.111
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.58
- Early IC=+0.1045, Recent IC=+0.0606, 1st-half IC=+0.0953, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.058, Q3_mid=+0.045, Q4=+0.067, Q5_high_vol=+0.233

**`combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0559, Sharpe=+0.3783)
- Admission: Train IC=+0.2333, Deflated=+0.2327, IR=0.65, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.094 | 2017: +0.021 | 2018: +0.206 | 2019: +0.107 | 2020: +0.039 | 2021: +0.136 | 2022: +0.069 | 2023: +0.126 | 2024: +0.016 | 2025: +0.091 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.011 | 2017: -0.032 | 2018: +0.313 | 2019: +0.160 | 2020: +0.262 | 2021: +0.378 | 2022: +0.326 | 2023: +0.222 | 2024: +0.158 | 2025: +0.282 | 2026: +0.096
- IC CV=0.69, Neg years (linear/tail)=0/1 of 8, Half ratio=0.92, Recency ratio=0.63
- Early IC=+0.1136, Recent IC=+0.0711, 1st-half IC=+0.1004, 2nd-half IC=+0.0927, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.068, Q3_mid=+0.055, Q4=+0.082, Q5_high_vol=+0.212

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0808, Sharpe=+0.3659)
- Admission: Train IC=+0.2286, Deflated=+0.2287, IR=0.48, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=1.04, Recency ratio=1.45
- Early IC=+0.0589, Recent IC=+0.0855, 1st-half IC=+0.0825, 2nd-half IC=+0.0862, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.064, Q3_mid=+0.070, Q4=+0.060, Q5_high_vol=+0.200

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0181, Sharpe=+0.2156)
- Admission: Train IC=+0.2167, Deflated=+0.2164, IR=0.73, Mono=0.74, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.090 | 2017: -0.060 | 2018: +0.193 | 2019: +0.085 | 2020: +0.068 | 2021: +0.164 | 2022: +0.063 | 2023: +0.126 | 2024: +0.043 | 2025: +0.068 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.133 | 2017: +0.065 | 2018: +0.421 | 2019: +0.261 | 2020: +0.125 | 2021: +0.246 | 2022: +0.201 | 2023: +0.120 | 2024: +0.194 | 2025: +0.206 | 2026: +0.145
- IC CV=0.86, Neg years (linear/tail)=1/0 of 8, Half ratio=1.35, Recency ratio=1.28
- Early IC=+0.0662, Recent IC=+0.0844, 1st-half IC=+0.0787, 2nd-half IC=+0.1064, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=-0.027, Q2=+0.070, Q3_mid=+0.032, Q4=+0.068, Q5_high_vol=+0.256

### 500ETF — `single` True Positives

**`combo_clamp_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1143, Sharpe=+1.3960)
- Admission: Train IC=+0.2159, Deflated=+0.2145, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.069 | 2017: +0.189 | 2018: +0.152 | 2019: +0.186 | 2020: +0.127 | 2021: +0.070 | 2022: +0.047 | 2023: +0.060 | 2024: +0.096 | 2025: +0.019 | 2026: +0.261
- Yearly Tail ICs:   2015: +0.394 | 2016: +0.243 | 2017: +0.302 | 2018: +0.294 | 2019: +0.330 | 2020: +0.193 | 2021: +0.262 | 2022: -0.025 | 2023: +0.141 | 2024: +0.247 | 2025: -0.014 | 2026: +0.530
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=0.44, Recency ratio=0.46
- Early IC=+0.1706, Recent IC=+0.0778, 1st-half IC=+0.1585, 2nd-half IC=+0.0695, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.005, Q3_mid=+0.062, Q4=+0.151, Q5_high_vol=+0.162

**`combo_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1117, Sharpe=+1.3824)
- Admission: Train IC=+0.2043, Deflated=+0.2028, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.299 | 2016: +0.061 | 2017: +0.189 | 2018: +0.152 | 2019: +0.188 | 2020: +0.128 | 2021: +0.068 | 2022: +0.047 | 2023: +0.061 | 2024: +0.091 | 2025: +0.016 | 2026: +0.257
- Yearly Tail ICs:   2015: +0.170 | 2016: +0.004 | 2017: +0.290 | 2018: +0.278 | 2019: +0.352 | 2020: +0.204 | 2021: +0.222 | 2022: -0.060 | 2023: +0.161 | 2024: +0.130 | 2025: -0.079 | 2026: +0.357
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.43, Recency ratio=0.45
- Early IC=+0.1704, Recent IC=+0.0761, 1st-half IC=+0.1596, 2nd-half IC=+0.0684, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.004, Q3_mid=+0.061, Q4=+0.148, Q5_high_vol=+0.163

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1106, Sharpe=+1.0183)
- Admission: Train IC=+0.2351, Deflated=+0.2348, IR=0.80, Mono=0.79, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.116 | 2017: +0.223 | 2018: +0.204 | 2019: +0.159 | 2020: +0.162 | 2021: +0.125 | 2022: +0.044 | 2023: +0.097 | 2024: +0.106 | 2025: +0.133 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.195 | 2017: +0.227 | 2018: +0.405 | 2019: +0.246 | 2020: +0.335 | 2021: +0.177 | 2022: +0.041 | 2023: +0.162 | 2024: +0.223 | 2025: +0.257 | 2026: +0.178
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.47
- Early IC=+0.2137, Recent IC=+0.1005, 1st-half IC=+0.1776, 2nd-half IC=+0.0873, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.210, Q2=-0.036, Q3_mid=+0.091, Q4=+0.173, Q5_high_vol=+0.203

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1095, Sharpe=+0.7916)
- Admission: Train IC=+0.2252, Deflated=+0.2238, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.099 | 2017: +0.233 | 2018: +0.132 | 2019: +0.098 | 2020: +0.133 | 2021: +0.117 | 2022: +0.056 | 2023: +0.096 | 2024: +0.118 | 2025: +0.140 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.228 | 2017: +0.343 | 2018: +0.291 | 2019: +0.226 | 2020: +0.281 | 2021: +0.290 | 2022: +0.057 | 2023: +0.199 | 2024: +0.212 | 2025: +0.046 | 2026: +0.090
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1821, Recent IC=+0.1052, 1st-half IC=+0.1377, 2nd-half IC=+0.0981, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.001, Q3_mid=+0.097, Q4=+0.107, Q5_high_vol=+0.174

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0980, Sharpe=+0.7580)
- Admission: Train IC=+0.2481, Deflated=+0.2472, IR=0.91, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.078 | 2017: +0.229 | 2018: +0.225 | 2019: +0.175 | 2020: +0.145 | 2021: +0.113 | 2022: +0.027 | 2023: +0.080 | 2024: +0.126 | 2025: +0.120 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.407 | 2016: +0.119 | 2017: +0.319 | 2018: +0.510 | 2019: +0.267 | 2020: +0.204 | 2021: +0.233 | 2022: +0.147 | 2023: +0.198 | 2024: +0.242 | 2025: +0.256 | 2026: +0.238
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.47, Recency ratio=0.45
- Early IC=+0.2271, Recent IC=+0.1031, 1st-half IC=+0.1868, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.022, Q3_mid=+0.106, Q4=+0.162, Q5_high_vol=+0.211

**`combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1065, Sharpe=+0.7497)
- Admission: Train IC=+0.2334, Deflated=+0.2321, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.308 | 2016: +0.078 | 2017: +0.129 | 2018: +0.204 | 2019: +0.175 | 2020: +0.184 | 2021: +0.123 | 2022: +0.050 | 2023: +0.061 | 2024: +0.114 | 2025: +0.063 | 2026: +0.185
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.066 | 2017: +0.219 | 2018: +0.347 | 2019: +0.418 | 2020: +0.276 | 2021: +0.215 | 2022: -0.085 | 2023: +0.020 | 2024: +0.214 | 2025: +0.135 | 2026: +0.397
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.53
- Early IC=+0.1664, Recent IC=+0.0880, 1st-half IC=+0.1748, 2nd-half IC=+0.0881, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.009, Q3_mid=+0.099, Q4=+0.144, Q5_high_vol=+0.203

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1041, Sharpe=+0.7497)
- Admission: Train IC=+0.2181, Deflated=+0.2169, IR=0.54, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.299 | 2016: +0.077 | 2017: +0.129 | 2018: +0.203 | 2019: +0.177 | 2020: +0.184 | 2021: +0.122 | 2022: +0.050 | 2023: +0.062 | 2024: +0.112 | 2025: +0.060 | 2026: +0.185
- Yearly Tail ICs:   2015: +0.118 | 2016: +0.035 | 2017: +0.204 | 2018: +0.364 | 2019: +0.443 | 2020: +0.228 | 2021: +0.190 | 2022: -0.063 | 2023: +0.042 | 2024: +0.116 | 2025: +0.057 | 2026: +0.377
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.53
- Early IC=+0.1659, Recent IC=+0.0872, 1st-half IC=+0.1748, 2nd-half IC=+0.0876, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.012, Q3_mid=+0.094, Q4=+0.141, Q5_high_vol=+0.204

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1136, Sharpe=+0.6574)
- Admission: Train IC=+0.2469, Deflated=+0.2455, IR=0.63, Mono=0.71, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.032 | 2017: +0.137 | 2018: +0.190 | 2019: +0.195 | 2020: +0.194 | 2021: +0.142 | 2022: +0.064 | 2023: +0.067 | 2024: +0.123 | 2025: +0.089 | 2026: +0.175
- Yearly Tail ICs:   2015: +0.232 | 2016: +0.078 | 2017: +0.198 | 2018: +0.320 | 2019: +0.485 | 2020: +0.246 | 2021: +0.258 | 2022: -0.023 | 2023: +0.116 | 2024: +0.156 | 2025: +0.105 | 2026: +0.387
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.58, Recency ratio=0.58
- Early IC=+0.1639, Recent IC=+0.0952, 1st-half IC=+0.1775, 2nd-half IC=+0.1021, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.028, Q3_mid=+0.110, Q4=+0.137, Q5_high_vol=+0.223

**`combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0`** (Lock IC=+0.1163, Sharpe=+0.4767)
- Admission: Train IC=+0.2529, Deflated=+0.2522, IR=0.99, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.075 | 2017: +0.218 | 2018: +0.168 | 2019: +0.142 | 2020: +0.127 | 2021: +0.117 | 2022: +0.069 | 2023: +0.080 | 2024: +0.116 | 2025: +0.148 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.351 | 2016: +0.098 | 2017: +0.185 | 2018: +0.388 | 2019: +0.246 | 2020: +0.187 | 2021: +0.135 | 2022: +0.186 | 2023: +0.288 | 2024: +0.367 | 2025: +0.179 | 2026: +0.145
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.51
- Early IC=+0.1933, Recent IC=+0.0982, 1st-half IC=+0.1465, 2nd-half IC=+0.0953, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.218, Q2=-0.032, Q3_mid=+0.080, Q4=+0.146, Q5_high_vol=+0.178

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0977, Sharpe=+0.3748)
- Admission: Train IC=+0.2403, Deflated=+0.2389, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.124 | 2017: +0.222 | 2018: +0.218 | 2019: +0.127 | 2020: +0.157 | 2021: +0.104 | 2022: +0.093 | 2023: +0.076 | 2024: +0.114 | 2025: +0.142 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.252 | 2016: +0.073 | 2017: +0.244 | 2018: +0.368 | 2019: +0.255 | 2020: +0.249 | 2021: +0.225 | 2022: +0.243 | 2023: +0.242 | 2024: +0.183 | 2025: +0.079 | 2026: +0.043
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.43
- Early IC=+0.2204, Recent IC=+0.0951, 1st-half IC=+0.1729, 2nd-half IC=+0.1014, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.222, Q2=+0.012, Q3_mid=+0.101, Q4=+0.144, Q5_high_vol=+0.189

**`combo_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1060, Sharpe=+0.3487)
- Admission: Train IC=+0.2512, Deflated=+0.2503, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.061 | 2017: +0.230 | 2018: +0.103 | 2019: +0.129 | 2020: +0.120 | 2021: +0.095 | 2022: +0.065 | 2023: +0.083 | 2024: +0.138 | 2025: +0.136 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.194 | 2017: +0.222 | 2018: +0.324 | 2019: +0.281 | 2020: +0.268 | 2021: -0.009 | 2022: +0.189 | 2023: +0.192 | 2024: +0.372 | 2025: +0.031 | 2026: +0.270
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.66
- Early IC=+0.1662, Recent IC=+0.1102, 1st-half IC=+0.1261, 2nd-half IC=+0.0982, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.211, Q2=-0.009, Q3_mid=+0.099, Q4=+0.123, Q5_high_vol=+0.147

**`combo_rank_min__net_volume_flow__vwap_close_divergence_trend`** (Lock IC=+0.0441, Sharpe=+0.3212)
- Admission: Train IC=+0.2179, Deflated=+0.2177, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.036 | 2017: +0.190 | 2018: +0.115 | 2019: +0.094 | 2020: +0.102 | 2021: +0.068 | 2022: +0.085 | 2023: +0.100 | 2024: +0.112 | 2025: +0.135 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.180 | 2016: +0.051 | 2017: +0.201 | 2018: +0.197 | 2019: +0.283 | 2020: +0.179 | 2021: +0.194 | 2022: +0.204 | 2023: +0.270 | 2024: +0.147 | 2025: +0.112 | 2026: -0.207
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.70
- Early IC=+0.1510, Recent IC=+0.1062, 1st-half IC=+0.1113, 2nd-half IC=+0.1001, Neg regimes=0/5
- Weak component: `vwap_close_divergence_trend` (CV=0.38)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.014, Q3_mid=+0.115, Q4=+0.100, Q5_high_vol=+0.110

**`combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.0817, Sharpe=+0.3027)
- Admission: Train IC=+0.2502, Deflated=+0.2492, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.075 | 2017: +0.193 | 2018: +0.139 | 2019: +0.080 | 2020: +0.127 | 2021: +0.055 | 2022: +0.084 | 2023: +0.069 | 2024: +0.100 | 2025: +0.126 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.359 | 2016: +0.110 | 2017: +0.268 | 2018: +0.242 | 2019: +0.237 | 2020: +0.193 | 2021: +0.210 | 2022: +0.340 | 2023: +0.197 | 2024: +0.238 | 2025: +0.209 | 2026: -0.053
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.51
- Early IC=+0.1663, Recent IC=+0.0841, 1st-half IC=+0.1269, 2nd-half IC=+0.0820, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.018, Q3_mid=+0.087, Q4=+0.095, Q5_high_vol=+0.135

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0867, Sharpe=+0.2984)
- Admission: Train IC=+0.2699, Deflated=+0.2686, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.093 | 2017: +0.220 | 2018: +0.191 | 2019: +0.123 | 2020: +0.135 | 2021: +0.152 | 2022: +0.043 | 2023: +0.113 | 2024: +0.145 | 2025: +0.122 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.324 | 2016: +0.237 | 2017: +0.318 | 2018: +0.445 | 2019: +0.311 | 2020: +0.263 | 2021: +0.249 | 2022: +0.229 | 2023: +0.195 | 2024: +0.288 | 2025: +0.082 | 2026: +0.241
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.63
- Early IC=+0.2057, Recent IC=+0.1289, 1st-half IC=+0.1555, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.228, Q2=+0.016, Q3_mid=+0.102, Q4=+0.111, Q5_high_vol=+0.201

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1138, Sharpe=+0.2628)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.064 | 2017: +0.196 | 2018: +0.105 | 2019: +0.176 | 2020: +0.076 | 2021: +0.087 | 2022: +0.089 | 2023: +0.057 | 2024: +0.164 | 2025: +0.058 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.201 | 2016: -0.078 | 2017: +0.194 | 2018: +0.319 | 2019: +0.255 | 2020: +0.061 | 2021: +0.195 | 2022: +0.202 | 2023: -0.020 | 2024: +0.075 | 2025: -0.152 | 2026: +0.171
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.74
- Early IC=+0.1505, Recent IC=+0.1107, 1st-half IC=+0.1298, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.066, Q3_mid=+0.094, Q4=+0.137, Q5_high_vol=+0.151

**`combo_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0418, Sharpe=+0.2392)
- Admission: Train IC=+0.2281, Deflated=+0.2271, IR=0.97, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.105 | 2017: +0.198 | 2018: +0.221 | 2019: +0.150 | 2020: +0.159 | 2021: +0.140 | 2022: +0.066 | 2023: +0.102 | 2024: +0.127 | 2025: +0.021 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.214 | 2017: +0.417 | 2018: +0.376 | 2019: +0.327 | 2020: +0.122 | 2021: +0.258 | 2022: +0.158 | 2023: +0.198 | 2024: +0.027 | 2025: -0.043 | 2026: +0.030
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.55
- Early IC=+0.2092, Recent IC=+0.1145, 1st-half IC=+0.1725, 2nd-half IC=+0.1087, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.005, Q3_mid=+0.101, Q4=+0.150, Q5_high_vol=+0.223

**`combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early`** (Lock IC=+0.0926, Sharpe=+0.2336)
- Admission: Train IC=+0.2467, Deflated=+0.2454, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.113 | 2017: +0.210 | 2018: +0.089 | 2019: +0.112 | 2020: +0.118 | 2021: +0.141 | 2022: +0.045 | 2023: +0.107 | 2024: +0.151 | 2025: +0.108 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.188 | 2017: +0.289 | 2018: +0.312 | 2019: +0.253 | 2020: +0.248 | 2021: +0.183 | 2022: +0.177 | 2023: +0.214 | 2024: +0.275 | 2025: +0.035 | 2026: +0.321
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.96, Recency ratio=0.86
- Early IC=+0.1493, Recent IC=+0.1291, 1st-half IC=+0.1168, 2nd-half IC=+0.1126, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.232, Q2=+0.014, Q3_mid=+0.096, Q4=+0.098, Q5_high_vol=+0.142

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0857, Sharpe=+0.2203)
- Admission: Train IC=+0.2415, Deflated=+0.2406, IR=0.66, Mono=0.71, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.327 | 2016: +0.092 | 2017: +0.223 | 2018: +0.185 | 2019: +0.155 | 2020: +0.153 | 2021: +0.109 | 2022: +0.037 | 2023: +0.095 | 2024: +0.103 | 2025: +0.103 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.128 | 2017: +0.154 | 2018: +0.463 | 2019: +0.272 | 2020: +0.280 | 2021: +0.165 | 2022: +0.130 | 2023: +0.133 | 2024: +0.252 | 2025: +0.101 | 2026: +0.122
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.49
- Early IC=+0.2041, Recent IC=+0.0990, 1st-half IC=+0.1650, 2nd-half IC=+0.0833, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.232, Q2=-0.033, Q3_mid=+0.084, Q4=+0.141, Q5_high_vol=+0.190

**`combo_mean__first_bar_return__max_down_ret`** (Lock IC=+0.0745, Sharpe=+0.2028)
- Admission: Train IC=+0.2194, Deflated=+0.2195, IR=0.72, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.104 | 2017: +0.226 | 2018: +0.203 | 2019: +0.133 | 2020: +0.121 | 2021: +0.084 | 2022: +0.072 | 2023: +0.053 | 2024: +0.127 | 2025: +0.132 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.041 | 2017: +0.263 | 2018: +0.390 | 2019: +0.184 | 2020: +0.181 | 2021: +0.280 | 2022: +0.190 | 2023: +0.134 | 2024: +0.251 | 2025: +0.165 | 2026: -0.251
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.42
- Early IC=+0.2146, Recent IC=+0.0903, 1st-half IC=+0.1515, 2nd-half IC=+0.0896, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.010, Q3_mid=+0.115, Q4=+0.135, Q5_high_vol=+0.158

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0970, Sharpe=+0.1808)
- Admission: Train IC=+0.1833, Deflated=+0.1822, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.305 | 2016: +0.036 | 2017: +0.233 | 2018: +0.100 | 2019: +0.110 | 2020: +0.116 | 2021: +0.047 | 2022: +0.058 | 2023: +0.046 | 2024: +0.103 | 2025: +0.097 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.307 | 2016: +0.162 | 2017: +0.189 | 2018: +0.226 | 2019: +0.360 | 2020: +0.204 | 2021: +0.175 | 2022: +0.096 | 2023: +0.021 | 2024: +0.249 | 2025: +0.008 | 2026: +0.179
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.45
- Early IC=+0.1665, Recent IC=+0.0746, 1st-half IC=+0.1201, 2nd-half IC=+0.0674, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.001, Q3_mid=+0.092, Q4=+0.116, Q5_high_vol=+0.108

**`combo_mean__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0626, Sharpe=+0.1369)
- Admission: Train IC=+0.2379, Deflated=+0.2378, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.099 | 2017: +0.225 | 2018: +0.233 | 2019: +0.144 | 2020: +0.147 | 2021: +0.137 | 2022: +0.070 | 2023: +0.093 | 2024: +0.137 | 2025: +0.110 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.582 | 2016: -0.000 | 2017: +0.196 | 2018: +0.178 | 2019: +0.350 | 2020: +0.085 | 2021: +0.440 | 2022: +0.118 | 2023: +0.085 | 2024: +0.228 | 2025: +0.150 | 2026: -0.049
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.50
- Early IC=+0.2289, Recent IC=+0.1148, 1st-half IC=+0.1744, 2nd-half IC=+0.1126, Neg regimes=1/5
- Weak component: `bar_body_rng_0` (CV=0.37)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.023, Q3_mid=+0.145, Q4=+0.175, Q5_high_vol=+0.191

**`combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum`** (Lock IC=+0.0900, Sharpe=+0.1337)
- Admission: Train IC=+0.2612, Deflated=+0.2599, IR=0.80, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.095 | 2017: +0.208 | 2018: +0.124 | 2019: +0.085 | 2020: +0.106 | 2021: +0.104 | 2022: +0.087 | 2023: +0.121 | 2024: +0.109 | 2025: +0.131 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.251 | 2017: +0.327 | 2018: +0.339 | 2019: +0.198 | 2020: +0.308 | 2021: +0.133 | 2022: +0.215 | 2023: +0.182 | 2024: +0.379 | 2025: +0.193 | 2026: +0.216
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.69
- Early IC=+0.1658, Recent IC=+0.1149, 1st-half IC=+0.1143, 2nd-half IC=+0.1070, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.011, Q3_mid=+0.082, Q4=+0.102, Q5_high_vol=+0.149

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0977, Sharpe=+0.1120)
- Admission: Train IC=+0.2620, Deflated=+0.2617, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.099 | 2017: +0.216 | 2018: +0.213 | 2019: +0.153 | 2020: +0.130 | 2021: +0.129 | 2022: +0.044 | 2023: +0.089 | 2024: +0.107 | 2025: +0.119 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.254 | 2017: +0.297 | 2018: +0.447 | 2019: +0.338 | 2020: +0.338 | 2021: +0.042 | 2022: +0.040 | 2023: +0.141 | 2024: +0.286 | 2025: +0.126 | 2026: +0.185
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.46
- Early IC=+0.2143, Recent IC=+0.0982, 1st-half IC=+0.1682, 2nd-half IC=+0.0866, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.207, Q2=-0.037, Q3_mid=+0.074, Q4=+0.168, Q5_high_vol=+0.192

**`combo_clamp_diff__first_bar_return__body_size_progression`** (Lock IC=+0.0511, Sharpe=+0.0657)
- Admission: Train IC=+0.2269, Deflated=+0.2269, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.060 | 2017: +0.167 | 2018: +0.231 | 2019: +0.205 | 2020: +0.121 | 2021: +0.102 | 2022: +0.065 | 2023: +0.072 | 2024: +0.109 | 2025: +0.033 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.355 | 2016: -0.019 | 2017: +0.436 | 2018: +0.401 | 2019: +0.188 | 2020: +0.135 | 2021: +0.063 | 2022: +0.199 | 2023: +0.082 | 2024: +0.244 | 2025: +0.013 | 2026: +0.048
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.51, Recency ratio=0.45
- Early IC=+0.1986, Recent IC=+0.0903, 1st-half IC=+0.1730, 2nd-half IC=+0.0878, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.185, Q2=-0.033, Q3_mid=+0.093, Q4=+0.170, Q5_high_vol=+0.197

### 159915ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1243, Sharpe=+2.0348)
- Admission: Train IC=+0.3122, Deflated=+0.3118, IR=0.98, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.124 | 2017: -0.001 | 2018: +0.125 | 2019: +0.213 | 2020: +0.067 | 2021: +0.189 | 2022: +0.060 | 2023: +0.148 | 2024: +0.120 | 2025: +0.140 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.063 | 2017: +0.103 | 2018: +0.280 | 2019: +0.527 | 2020: +0.305 | 2021: +0.389 | 2022: +0.110 | 2023: +0.381 | 2024: +0.281 | 2025: +0.148 | 2026: +0.325
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.32, Recency ratio=2.19
- Early IC=+0.0604, Recent IC=+0.1324, 1st-half IC=+0.1037, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.124, Q3_mid=+0.101, Q4=+0.111, Q5_high_vol=+0.205

**`combo_rank_min__rbreaker_buy_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1411, Sharpe=+1.7639)
- Admission: Train IC=+0.1836, Deflated=+0.1843, IR=0.46, Mono=0.66, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.017 | 2017: -0.001 | 2018: +0.104 | 2019: +0.182 | 2020: +0.121 | 2021: +0.014 | 2022: +0.052 | 2023: +0.097 | 2024: +0.105 | 2025: +0.116 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.377 | 2016: -0.077 | 2017: -0.121 | 2018: +0.335 | 2019: +0.471 | 2020: +0.241 | 2021: +0.148 | 2022: +0.130 | 2023: +0.026 | 2024: +0.368 | 2025: +0.168 | 2026: +0.440
- IC CV=0.66, Neg years (linear/tail)=1/1 of 8, Half ratio=0.72, Recency ratio=2.00
- Early IC=+0.0501, Recent IC=+0.1004, 1st-half IC=+0.0972, 2nd-half IC=+0.0695, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.061, Q3_mid=+0.059, Q4=+0.066, Q5_high_vol=+0.155

**`combo_rank_min__limit_down_proximity_early__volume_price_confirmation`** (Lock IC=+0.1411, Sharpe=+1.7639)
- Admission: Train IC=+0.1836, Deflated=+0.1843, IR=0.46, Mono=0.66, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.017 | 2017: -0.001 | 2018: +0.104 | 2019: +0.182 | 2020: +0.121 | 2021: +0.014 | 2022: +0.052 | 2023: +0.097 | 2024: +0.105 | 2025: +0.116 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.377 | 2016: -0.077 | 2017: -0.121 | 2018: +0.335 | 2019: +0.471 | 2020: +0.241 | 2021: +0.148 | 2022: +0.130 | 2023: +0.026 | 2024: +0.368 | 2025: +0.168 | 2026: +0.440
- IC CV=0.66, Neg years (linear/tail)=1/1 of 8, Half ratio=0.72, Recency ratio=2.00
- Early IC=+0.0501, Recent IC=+0.1004, 1st-half IC=+0.0972, 2nd-half IC=+0.0695, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.061, Q3_mid=+0.059, Q4=+0.066, Q5_high_vol=+0.155

**`combo_rank_min__volume_weighted_price_position__limit_down_proximity_early`** (Lock IC=+0.1471, Sharpe=+1.7038)
- Admission: Train IC=+0.2498, Deflated=+0.2501, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.016 | 2017: -0.006 | 2018: +0.068 | 2019: +0.223 | 2020: +0.017 | 2021: +0.124 | 2022: +0.019 | 2023: +0.147 | 2024: +0.110 | 2025: +0.131 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.232 | 2016: -0.077 | 2017: +0.116 | 2018: +0.247 | 2019: +0.595 | 2020: +0.129 | 2021: +0.347 | 2022: +0.200 | 2023: +0.316 | 2024: +0.237 | 2025: +0.141 | 2026: +0.375
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.48, Recency ratio=4.47
- Early IC=+0.0279, Recent IC=+0.1246, 1st-half IC=+0.0718, 2nd-half IC=+0.1065, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.085, Q3_mid=+0.109, Q4=+0.082, Q5_high_vol=+0.108

**`combo_min__star50_limit_proximity_early__volume_price_confirmation`** (Lock IC=+0.1332, Sharpe=+1.6808)
- Admission: Train IC=+0.2836, Deflated=+0.2837, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.068 | 2017: +0.027 | 2018: +0.139 | 2019: +0.183 | 2020: +0.165 | 2021: +0.030 | 2022: +0.055 | 2023: +0.115 | 2024: +0.123 | 2025: +0.106 | 2026: +0.189
- Yearly Tail ICs:   2015: +0.420 | 2016: +0.101 | 2017: -0.028 | 2018: +0.391 | 2019: +0.472 | 2020: +0.327 | 2021: +0.167 | 2022: +0.165 | 2023: +0.120 | 2024: +0.444 | 2025: +0.228 | 2026: +0.442
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=1.43
- Early IC=+0.0830, Recent IC=+0.1191, 1st-half IC=+0.1305, 2nd-half IC=+0.0867, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.070, Q3_mid=+0.067, Q4=+0.067, Q5_high_vol=+0.231

**`combo_min__max_up_ret__gap_pct`** (Lock IC=+0.1305, Sharpe=+1.6653)
- Admission: Train IC=+0.1870, Deflated=+0.1853, IR=0.54, Mono=0.68, p=0.0004, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.079 | 2017: +0.024 | 2018: +0.028 | 2019: +0.211 | 2020: +0.151 | 2021: +0.133 | 2022: +0.074 | 2023: +0.100 | 2024: +0.069 | 2025: +0.136 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.105 | 2016: +0.140 | 2017: +0.081 | 2018: +0.292 | 2019: +0.506 | 2020: +0.133 | 2021: +0.202 | 2022: -0.013 | 2023: +0.127 | 2024: +0.124 | 2025: +0.111 | 2026: +0.256
- IC CV=0.61, Neg years (linear/tail)=0/1 of 8, Half ratio=0.99, Recency ratio=3.26
- Early IC=+0.0258, Recent IC=+0.0842, 1st-half IC=+0.1055, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.084, Q3_mid=+0.126, Q4=+0.126, Q5_high_vol=+0.105

**`combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1396, Sharpe=+1.6504)
- Admission: Train IC=+0.2889, Deflated=+0.2884, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.088 | 2017: -0.029 | 2018: +0.142 | 2019: +0.227 | 2020: +0.127 | 2021: +0.132 | 2022: +0.088 | 2023: +0.105 | 2024: +0.070 | 2025: +0.135 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.201 | 2016: +0.062 | 2017: +0.125 | 2018: +0.386 | 2019: +0.442 | 2020: +0.175 | 2021: +0.276 | 2022: +0.126 | 2023: +0.143 | 2024: +0.432 | 2025: +0.251 | 2026: +0.245
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=0.94, Recency ratio=1.55
- Early IC=+0.0565, Recent IC=+0.0874, 1st-half IC=+0.1148, 2nd-half IC=+0.1074, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.068, Q3_mid=+0.071, Q4=+0.121, Q5_high_vol=+0.167

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1527, Sharpe=+1.5226)
- Admission: Train IC=+0.2931, Deflated=+0.2931, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.203 | 2016: -0.012 | 2017: -0.014 | 2018: +0.077 | 2019: +0.224 | 2020: +0.104 | 2021: +0.111 | 2022: +0.092 | 2023: +0.164 | 2024: +0.067 | 2025: +0.174 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.210 | 2016: -0.107 | 2017: +0.066 | 2018: +0.349 | 2019: +0.484 | 2020: +0.155 | 2021: +0.309 | 2022: +0.301 | 2023: +0.392 | 2024: +0.284 | 2025: +0.131 | 2026: +0.337
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=3.62
- Early IC=+0.0310, Recent IC=+0.1125, 1st-half IC=+0.0963, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.077, Q3_mid=+0.132, Q4=+0.105, Q5_high_vol=+0.117

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1491, Sharpe=+1.4472)
- Admission: Train IC=+0.2433, Deflated=+0.2432, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.112 | 2017: +0.020 | 2018: +0.091 | 2019: +0.236 | 2020: +0.119 | 2021: +0.123 | 2022: +0.093 | 2023: +0.164 | 2024: +0.068 | 2025: +0.215 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.026 | 2017: +0.037 | 2018: +0.218 | 2019: +0.458 | 2020: +0.239 | 2021: +0.253 | 2022: +0.137 | 2023: +0.345 | 2024: +0.303 | 2025: +0.428 | 2026: +0.234
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=2.08
- Early IC=+0.0557, Recent IC=+0.1160, 1st-half IC=+0.1118, 2nd-half IC=+0.1205, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.111, Q3_mid=+0.108, Q4=+0.090, Q5_high_vol=+0.140

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1279, Sharpe=+1.4471)
- Admission: Train IC=+0.2691, Deflated=+0.2682, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.096 | 2017: +0.048 | 2018: +0.173 | 2019: +0.238 | 2020: +0.154 | 2021: +0.122 | 2022: +0.150 | 2023: +0.168 | 2024: +0.119 | 2025: +0.144 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.097 | 2016: -0.006 | 2017: -0.056 | 2018: +0.462 | 2019: +0.506 | 2020: +0.259 | 2021: +0.186 | 2022: +0.148 | 2023: +0.370 | 2024: +0.307 | 2025: +0.181 | 2026: +0.109
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.93, Recency ratio=1.30
- Early IC=+0.1108, Recent IC=+0.1436, 1st-half IC=+0.1553, 2nd-half IC=+0.1438, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.114, Q3_mid=+0.083, Q4=+0.169, Q5_high_vol=+0.236

**`combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.1348, Sharpe=+1.4350)
- Admission: Train IC=+0.2363, Deflated=+0.2352, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.123 | 2017: -0.004 | 2018: +0.140 | 2019: +0.198 | 2020: +0.224 | 2021: +0.085 | 2022: +0.079 | 2023: +0.073 | 2024: +0.114 | 2025: +0.090 | 2026: +0.210
- Yearly Tail ICs:   2015: +0.016 | 2016: +0.240 | 2017: -0.098 | 2018: +0.195 | 2019: +0.354 | 2020: +0.272 | 2021: +0.260 | 2022: +0.170 | 2023: +0.158 | 2024: +0.432 | 2025: -0.001 | 2026: +0.397
- IC CV=0.60, Neg years (linear/tail)=1/1 of 8, Half ratio=0.67, Recency ratio=1.38
- Early IC=+0.0676, Recent IC=+0.0936, 1st-half IC=+0.1472, 2nd-half IC=+0.0983, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=1.20)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.105, Q3_mid=+0.053, Q4=+0.117, Q5_high_vol=+0.221

**`combo_min__volume_weighted_price_position__limit_down_proximity_early`** (Lock IC=+0.1345, Sharpe=+1.4216)
- Admission: Train IC=+0.2796, Deflated=+0.2799, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.028 | 2017: -0.006 | 2018: +0.076 | 2019: +0.222 | 2020: +0.013 | 2021: +0.132 | 2022: +0.010 | 2023: +0.146 | 2024: +0.116 | 2025: +0.124 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.225 | 2016: -0.071 | 2017: +0.112 | 2018: +0.298 | 2019: +0.599 | 2020: +0.182 | 2021: +0.322 | 2022: +0.231 | 2023: +0.297 | 2024: +0.281 | 2025: +0.104 | 2026: +0.483
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=1.47, Recency ratio=3.76
- Early IC=+0.0349, Recent IC=+0.1313, 1st-half IC=+0.0745, 2nd-half IC=+0.1098, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.085, Q3_mid=+0.115, Q4=+0.084, Q5_high_vol=+0.115

**`combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression`** (Lock IC=+0.1226, Sharpe=+1.3869)
- Admission: Train IC=+0.2401, Deflated=+0.2391, IR=0.44, Mono=0.65, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.088 | 2017: +0.021 | 2018: +0.149 | 2019: +0.280 | 2020: +0.153 | 2021: +0.077 | 2022: +0.114 | 2023: +0.158 | 2024: +0.094 | 2025: +0.089 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.040 | 2017: -0.091 | 2018: +0.211 | 2019: +0.528 | 2020: +0.262 | 2021: +0.237 | 2022: +0.147 | 2023: +0.292 | 2024: +0.254 | 2025: +0.081 | 2026: +0.143
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=1.48
- Early IC=+0.0852, Recent IC=+0.1258, 1st-half IC=+0.1523, 2nd-half IC=+0.1190, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.84)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.120, Q3_mid=+0.053, Q4=+0.159, Q5_high_vol=+0.209

**`combo_mean__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.1382, Sharpe=+1.3500)
- Admission: Train IC=+0.2434, Deflated=+0.2430, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.071 | 2017: -0.002 | 2018: +0.159 | 2019: +0.207 | 2020: +0.121 | 2021: +0.137 | 2022: +0.095 | 2023: +0.135 | 2024: +0.066 | 2025: +0.154 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.046 | 2017: +0.130 | 2018: +0.339 | 2019: +0.412 | 2020: +0.080 | 2021: +0.368 | 2022: +0.106 | 2023: +0.164 | 2024: +0.384 | 2025: +0.224 | 2026: +0.269
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=0.90, Recency ratio=1.28
- Early IC=+0.0784, Recent IC=+0.1006, 1st-half IC=+0.1259, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.089, Q3_mid=+0.063, Q4=+0.114, Q5_high_vol=+0.188

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation`** (Lock IC=+0.1321, Sharpe=+1.3408)
- Admission: Train IC=+0.2195, Deflated=+0.2187, IR=0.47, Mono=0.66, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.122 | 2017: +0.064 | 2018: +0.204 | 2019: +0.218 | 2020: +0.210 | 2021: +0.103 | 2022: +0.101 | 2023: +0.080 | 2024: +0.081 | 2025: +0.105 | 2026: +0.182
- Yearly Tail ICs:   2015: -0.002 | 2016: +0.180 | 2017: -0.047 | 2018: +0.313 | 2019: +0.417 | 2020: +0.276 | 2021: +0.296 | 2022: +0.106 | 2023: +0.064 | 2024: +0.358 | 2025: +0.071 | 2026: +0.355
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=0.60, Recency ratio=0.61
- Early IC=+0.1337, Recent IC=+0.0809, 1st-half IC=+0.1731, 2nd-half IC=+0.1031, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.084, Q3_mid=+0.068, Q4=+0.153, Q5_high_vol=+0.243

**`combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1199, Sharpe=+1.3117)
- Admission: Train IC=+0.2512, Deflated=+0.2503, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.118 | 2017: +0.032 | 2018: +0.180 | 2019: +0.220 | 2020: +0.159 | 2021: +0.144 | 2022: +0.141 | 2023: +0.129 | 2024: +0.110 | 2025: +0.122 | 2026: +0.135
- Yearly Tail ICs:   2015: -0.025 | 2016: +0.022 | 2017: -0.010 | 2018: +0.427 | 2019: +0.520 | 2020: +0.196 | 2021: +0.223 | 2022: +0.132 | 2023: +0.235 | 2024: +0.295 | 2025: +0.125 | 2026: +0.104
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.91, Recency ratio=1.13
- Early IC=+0.1063, Recent IC=+0.1197, 1st-half IC=+0.1502, 2nd-half IC=+0.1373, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.094, Q3_mid=+0.080, Q4=+0.180, Q5_high_vol=+0.226

**`combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.1367, Sharpe=+1.2430)
- Admission: Train IC=+0.2515, Deflated=+0.2510, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.106 | 2017: +0.005 | 2018: +0.100 | 2019: +0.200 | 2020: +0.191 | 2021: +0.064 | 2022: +0.035 | 2023: +0.117 | 2024: +0.117 | 2025: +0.086 | 2026: +0.217
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.181 | 2017: +0.074 | 2018: +0.302 | 2019: +0.384 | 2020: +0.362 | 2021: -0.062 | 2022: +0.075 | 2023: +0.352 | 2024: +0.479 | 2025: +0.084 | 2026: +0.379
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.70, Recency ratio=2.23
- Early IC=+0.0526, Recent IC=+0.1171, 1st-half IC=+0.1320, 2nd-half IC=+0.0926, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=1.20)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.124, Q3_mid=+0.052, Q4=+0.075, Q5_high_vol=+0.216

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1303, Sharpe=+1.1938)
- Admission: Train IC=+0.3174, Deflated=+0.3167, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.094 | 2017: +0.026 | 2018: +0.158 | 2019: +0.224 | 2020: +0.126 | 2021: +0.163 | 2022: +0.113 | 2023: +0.175 | 2024: +0.106 | 2025: +0.175 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.007 | 2017: +0.102 | 2018: +0.296 | 2019: +0.467 | 2020: +0.222 | 2021: +0.351 | 2022: +0.190 | 2023: +0.325 | 2024: +0.425 | 2025: +0.272 | 2026: +0.064
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=1.52
- Early IC=+0.0923, Recent IC=+0.1405, 1st-half IC=+0.1307, 2nd-half IC=+0.1446, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.101, Q3_mid=+0.108, Q4=+0.127, Q5_high_vol=+0.196

**`combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.1426, Sharpe=+1.1691)
- Admission: Train IC=+0.2774, Deflated=+0.2769, IR=0.79, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.006 | 2017: -0.001 | 2018: +0.093 | 2019: +0.229 | 2020: +0.098 | 2021: +0.121 | 2022: +0.077 | 2023: +0.169 | 2024: +0.098 | 2025: +0.169 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.227 | 2016: -0.063 | 2017: +0.024 | 2018: +0.385 | 2019: +0.505 | 2020: +0.182 | 2021: +0.275 | 2022: +0.167 | 2023: +0.391 | 2024: +0.284 | 2025: +0.167 | 2026: +0.522
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=2.90
- Early IC=+0.0461, Recent IC=+0.1337, 1st-half IC=+0.1048, 2nd-half IC=+0.1218, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.080, Q3_mid=+0.152, Q4=+0.117, Q5_high_vol=+0.123

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression`** (Lock IC=+0.1217, Sharpe=+1.1554)
- Admission: Train IC=+0.2033, Deflated=+0.2024, IR=0.37, Mono=0.66, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.113 | 2017: +0.023 | 2018: +0.167 | 2019: +0.266 | 2020: +0.154 | 2021: +0.088 | 2022: +0.100 | 2023: +0.114 | 2024: +0.086 | 2025: +0.072 | 2026: +0.208
- Yearly Tail ICs:   2015: +0.141 | 2016: +0.194 | 2017: -0.106 | 2018: +0.163 | 2019: +0.499 | 2020: +0.202 | 2021: +0.253 | 2022: +0.090 | 2023: +0.202 | 2024: +0.286 | 2025: +0.248 | 2026: +0.349
- IC CV=0.54, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=1.05
- Early IC=+0.0951, Recent IC=+0.0999, 1st-half IC=+0.1546, 2nd-half IC=+0.1073, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.84)
- Regime ICs: Q1_low_vol=+0.096, Q2=+0.103, Q3_mid=+0.054, Q4=+0.158, Q5_high_vol=+0.209

**`combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature`** (Lock IC=+0.1421, Sharpe=+1.1452)
- Admission: Train IC=+0.2390, Deflated=+0.2386, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.111 | 2017: +0.010 | 2018: +0.095 | 2019: +0.197 | 2020: +0.196 | 2021: +0.058 | 2022: +0.044 | 2023: +0.120 | 2024: +0.108 | 2025: +0.098 | 2026: +0.203
- Yearly Tail ICs:   2015: +0.292 | 2016: +0.230 | 2017: +0.058 | 2018: +0.252 | 2019: +0.337 | 2020: +0.397 | 2021: -0.024 | 2022: +0.093 | 2023: +0.301 | 2024: +0.471 | 2025: +0.106 | 2026: +0.453
- IC CV=0.62, Neg years (linear/tail)=0/1 of 8, Half ratio=0.67, Recency ratio=2.22
- Early IC=+0.0492, Recent IC=+0.1094, 1st-half IC=+0.1291, 2nd-half IC=+0.0866, Neg regimes=0/5
- Weak component: `directional_volume_signature` (CV=1.20)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.132, Q3_mid=+0.043, Q4=+0.067, Q5_high_vol=+0.216

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1277, Sharpe=+1.1407)
- Admission: Train IC=+0.3360, Deflated=+0.3352, IR=1.05, Mono=0.83, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.092 | 2017: -0.005 | 2018: +0.166 | 2019: +0.223 | 2020: +0.135 | 2021: +0.148 | 2022: +0.127 | 2023: +0.186 | 2024: +0.081 | 2025: +0.182 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.022 | 2017: +0.048 | 2018: +0.386 | 2019: +0.452 | 2020: +0.337 | 2021: +0.367 | 2022: +0.294 | 2023: +0.467 | 2024: +0.301 | 2025: +0.195 | 2026: +0.190
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.07, Recency ratio=1.68
- Early IC=+0.0789, Recent IC=+0.1327, 1st-half IC=+0.1338, 2nd-half IC=+0.1438, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.138, Q3_mid=+0.123, Q4=+0.139, Q5_high_vol=+0.199

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1617, Sharpe=+1.1078)
- Admission: Train IC=+0.2468, Deflated=+0.2472, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.040 | 2017: -0.056 | 2018: +0.095 | 2019: +0.245 | 2020: +0.122 | 2021: +0.099 | 2022: +0.056 | 2023: +0.135 | 2024: +0.095 | 2025: +0.167 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.021 | 2017: -0.034 | 2018: +0.385 | 2019: +0.534 | 2020: +0.249 | 2021: +0.283 | 2022: +0.154 | 2023: +0.234 | 2024: +0.339 | 2025: +0.287 | 2026: +0.349
- IC CV=0.79, Neg years (linear/tail)=1/1 of 8, Half ratio=1.08, Recency ratio=6.24
- Early IC=+0.0184, Recent IC=+0.1147, 1st-half IC=+0.0949, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.088, Q3_mid=+0.077, Q4=+0.090, Q5_high_vol=+0.131

**`combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1285, Sharpe=+1.1054)
- Admission: Train IC=+0.3352, Deflated=+0.3344, IR=1.24, Mono=0.89, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.092 | 2017: +0.005 | 2018: +0.159 | 2019: +0.232 | 2020: +0.130 | 2021: +0.146 | 2022: +0.109 | 2023: +0.185 | 2024: +0.118 | 2025: +0.194 | 2026: +0.043
- Yearly Tail ICs:   2015: +0.234 | 2016: +0.100 | 2017: +0.115 | 2018: +0.320 | 2019: +0.547 | 2020: +0.348 | 2021: +0.285 | 2022: +0.378 | 2023: +0.420 | 2024: +0.334 | 2025: +0.219 | 2026: +0.174
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=1.84
- Early IC=+0.0819, Recent IC=+0.1511, 1st-half IC=+0.1329, 2nd-half IC=+0.1461, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.132, Q3_mid=+0.139, Q4=+0.151, Q5_high_vol=+0.177

**`combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1518, Sharpe=+1.0662)
- Admission: Train IC=+0.2819, Deflated=+0.2822, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.056 | 2017: -0.042 | 2018: +0.097 | 2019: +0.256 | 2020: +0.141 | 2021: +0.105 | 2022: +0.045 | 2023: +0.125 | 2024: +0.107 | 2025: +0.152 | 2026: +0.145
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.013 | 2017: -0.032 | 2018: +0.383 | 2019: +0.507 | 2020: +0.238 | 2021: +0.249 | 2022: +0.178 | 2023: +0.248 | 2024: +0.467 | 2025: +0.157 | 2026: +0.412
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=0.94, Recency ratio=4.18
- Early IC=+0.0278, Recent IC=+0.1160, 1st-half IC=+0.1109, 2nd-half IC=+0.1044, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.087, Q3_mid=+0.087, Q4=+0.101, Q5_high_vol=+0.146

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1518, Sharpe=+1.0662)
- Admission: Train IC=+0.2819, Deflated=+0.2822, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.056 | 2017: -0.042 | 2018: +0.097 | 2019: +0.256 | 2020: +0.141 | 2021: +0.105 | 2022: +0.045 | 2023: +0.125 | 2024: +0.107 | 2025: +0.152 | 2026: +0.145
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.013 | 2017: -0.032 | 2018: +0.383 | 2019: +0.507 | 2020: +0.238 | 2021: +0.249 | 2022: +0.178 | 2023: +0.248 | 2024: +0.467 | 2025: +0.157 | 2026: +0.412
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=0.94, Recency ratio=4.18
- Early IC=+0.0278, Recent IC=+0.1160, 1st-half IC=+0.1109, 2nd-half IC=+0.1044, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.087, Q3_mid=+0.087, Q4=+0.101, Q5_high_vol=+0.146

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+1.0456)
- Admission: Train IC=+0.2890, Deflated=+0.2872, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.143 | 2017: +0.023 | 2018: +0.124 | 2019: +0.198 | 2020: +0.163 | 2021: +0.160 | 2022: +0.117 | 2023: +0.158 | 2024: +0.094 | 2025: +0.170 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.051 | 2016: +0.275 | 2017: +0.036 | 2018: +0.381 | 2019: +0.375 | 2020: +0.235 | 2021: +0.366 | 2022: +0.273 | 2023: +0.196 | 2024: +0.353 | 2025: +0.152 | 2026: +0.278
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=1.71
- Early IC=+0.0736, Recent IC=+0.1260, 1st-half IC=+0.1315, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.112, Q3_mid=+0.111, Q4=+0.137, Q5_high_vol=+0.196

**`combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1454, Sharpe=+1.0413)
- Admission: Train IC=+0.2847, Deflated=+0.2837, IR=0.97, Mono=0.83, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.059 | 2017: +0.024 | 2018: +0.138 | 2019: +0.206 | 2020: +0.141 | 2021: +0.164 | 2022: +0.101 | 2023: +0.153 | 2024: +0.061 | 2025: +0.192 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.078 | 2016: +0.007 | 2017: +0.136 | 2018: +0.337 | 2019: +0.325 | 2020: +0.408 | 2021: +0.318 | 2022: +0.364 | 2023: +0.189 | 2024: +0.258 | 2025: +0.180 | 2026: +0.343
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.31
- Early IC=+0.0813, Recent IC=+0.1066, 1st-half IC=+0.1276, 2nd-half IC=+0.1282, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.106, Q2=+0.097, Q3_mid=+0.123, Q4=+0.141, Q5_high_vol=+0.191

**`combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1258, Sharpe=+1.0333)
- Admission: Train IC=+0.3197, Deflated=+0.3193, IR=1.03, Mono=0.84, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.126 | 2017: +0.006 | 2018: +0.127 | 2019: +0.227 | 2020: +0.059 | 2021: +0.178 | 2022: +0.044 | 2023: +0.149 | 2024: +0.126 | 2025: +0.143 | 2026: +0.112
- Yearly Tail ICs:   2015: -0.006 | 2016: +0.023 | 2017: +0.116 | 2018: +0.216 | 2019: +0.629 | 2020: +0.300 | 2021: +0.345 | 2022: +0.180 | 2023: +0.384 | 2024: +0.256 | 2025: +0.209 | 2026: +0.265
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=2.06
- Early IC=+0.0667, Recent IC=+0.1374, 1st-half IC=+0.1060, 2nd-half IC=+0.1322, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.124, Q3_mid=+0.106, Q4=+0.114, Q5_high_vol=+0.196

**`combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend`** (Lock IC=+0.1321, Sharpe=+1.0237)
- Admission: Train IC=+0.2482, Deflated=+0.2482, IR=0.66, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.062 | 2017: -0.038 | 2018: +0.117 | 2019: +0.089 | 2020: +0.122 | 2021: +0.030 | 2022: +0.174 | 2023: +0.129 | 2024: +0.073 | 2025: +0.113 | 2026: +0.153
- Yearly Tail ICs:   2015: +0.125 | 2016: +0.222 | 2017: +0.054 | 2018: +0.449 | 2019: +0.292 | 2020: +0.383 | 2021: +0.181 | 2022: +0.410 | 2023: +0.130 | 2024: +0.073 | 2025: +0.082 | 2026: +0.209
- IC CV=0.71, Neg years (linear/tail)=1/0 of 8, Half ratio=1.08, Recency ratio=2.58
- Early IC=+0.0393, Recent IC=+0.1014, 1st-half IC=+0.0842, 2nd-half IC=+0.0912, Neg regimes=0/5
- Weak component: `yesterday_early_trend` (CV=1.18)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.147, Q3_mid=+0.065, Q4=+0.112, Q5_high_vol=+0.156

**`combo_rank_max__star50_limit_proximity_early__volume_price_confirmation`** (Lock IC=+0.1187, Sharpe=+1.0234)
- Admission: Train IC=+0.1884, Deflated=+0.1876, IR=0.53, Mono=0.66, p=0.0004, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.073 | 2017: +0.051 | 2018: +0.114 | 2019: +0.199 | 2020: +0.147 | 2021: +0.138 | 2022: +0.132 | 2023: +0.073 | 2024: +0.053 | 2025: +0.085 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.036 | 2017: +0.038 | 2018: +0.209 | 2019: +0.241 | 2020: +0.088 | 2021: +0.383 | 2022: +0.065 | 2023: +0.088 | 2024: +0.229 | 2025: -0.087 | 2026: +0.444
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.77
- Early IC=+0.0818, Recent IC=+0.0627, 1st-half IC=+0.1316, 2nd-half IC=+0.1065, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.103, Q3_mid=+0.069, Q4=+0.161, Q5_high_vol=+0.153

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1310, Sharpe=+1.0164)
- Admission: Train IC=+0.2854, Deflated=+0.2851, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.130 | 2017: -0.009 | 2018: +0.180 | 2019: +0.223 | 2020: +0.148 | 2021: +0.151 | 2022: +0.099 | 2023: +0.145 | 2024: +0.084 | 2025: +0.161 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.041 | 2017: +0.189 | 2018: +0.293 | 2019: +0.389 | 2020: +0.197 | 2021: +0.393 | 2022: +0.143 | 2023: +0.198 | 2024: +0.351 | 2025: +0.251 | 2026: +0.170
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=1.34
- Early IC=+0.0856, Recent IC=+0.1146, 1st-half IC=+0.1328, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.097, Q3_mid=+0.076, Q4=+0.119, Q5_high_vol=+0.203

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1207, Sharpe=+0.9917)
- Admission: Train IC=+0.2476, Deflated=+0.2467, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.121 | 2017: +0.034 | 2018: +0.179 | 2019: +0.219 | 2020: +0.159 | 2021: +0.143 | 2022: +0.139 | 2023: +0.126 | 2024: +0.109 | 2025: +0.122 | 2026: +0.137
- Yearly Tail ICs:   2015: +0.118 | 2016: +0.114 | 2017: -0.022 | 2018: +0.411 | 2019: +0.512 | 2020: +0.234 | 2021: +0.192 | 2022: +0.223 | 2023: +0.172 | 2024: +0.279 | 2025: +0.191 | 2026: +0.132
- IC CV=0.37, Neg years (linear/tail)=0/1 of 8, Half ratio=0.90, Recency ratio=1.10
- Early IC=+0.1066, Recent IC=+0.1173, 1st-half IC=+0.1501, 2nd-half IC=+0.1355, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.112, Q2=+0.094, Q3_mid=+0.081, Q4=+0.177, Q5_high_vol=+0.226

**`combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum`** (Lock IC=+0.1150, Sharpe=+0.9916)
- Admission: Train IC=+0.2143, Deflated=+0.2134, IR=0.35, Mono=0.65, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.099 | 2017: +0.012 | 2018: +0.150 | 2019: +0.236 | 2020: +0.131 | 2021: +0.093 | 2022: +0.122 | 2023: +0.120 | 2024: +0.106 | 2025: +0.057 | 2026: +0.218
- Yearly Tail ICs:   2015: +0.096 | 2016: +0.060 | 2017: +0.072 | 2018: +0.190 | 2019: +0.381 | 2020: +0.105 | 2021: +0.233 | 2022: +0.135 | 2023: +0.100 | 2024: +0.262 | 2025: -0.022 | 2026: +0.158
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=1.39
- Early IC=+0.0811, Recent IC=+0.1127, 1st-half IC=+0.1350, 2nd-half IC=+0.1215, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.096, Q3_mid=+0.049, Q4=+0.162, Q5_high_vol=+0.197

**`combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1473, Sharpe=+0.9583)
- Admission: Train IC=+0.2280, Deflated=+0.2264, IR=0.59, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.112 | 2017: +0.050 | 2018: +0.063 | 2019: +0.184 | 2020: +0.149 | 2021: +0.114 | 2022: +0.099 | 2023: +0.141 | 2024: +0.086 | 2025: +0.174 | 2026: +0.107
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.226 | 2017: +0.152 | 2018: +0.327 | 2019: +0.384 | 2020: +0.118 | 2021: +0.284 | 2022: +0.264 | 2023: +0.131 | 2024: +0.217 | 2025: +0.187 | 2026: +0.256
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=2.01
- Early IC=+0.0564, Recent IC=+0.1134, 1st-half IC=+0.1094, 2nd-half IC=+0.1203, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.077, Q3_mid=+0.094, Q4=+0.123, Q5_high_vol=+0.148

**`combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1265, Sharpe=+0.9284)
- Admission: Train IC=+0.2666, Deflated=+0.2649, IR=0.89, Mono=0.83, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.063 | 2017: +0.036 | 2018: +0.086 | 2019: +0.181 | 2020: +0.058 | 2021: +0.182 | 2022: +0.056 | 2023: +0.127 | 2024: +0.087 | 2025: +0.155 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.057 | 2017: +0.105 | 2018: +0.236 | 2019: +0.276 | 2020: +0.199 | 2021: +0.344 | 2022: +0.219 | 2023: +0.345 | 2024: +0.284 | 2025: +0.166 | 2026: +0.168
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.84
- Early IC=+0.0591, Recent IC=+0.1085, 1st-half IC=+0.0940, 2nd-half IC=+0.1277, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.121, Q3_mid=+0.115, Q4=+0.112, Q5_high_vol=+0.149

**`combo_min__bar_ret_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1467, Sharpe=+0.8978)
- Admission: Train IC=+0.2469, Deflated=+0.2472, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.054 | 2017: -0.028 | 2018: +0.080 | 2019: +0.250 | 2020: +0.116 | 2021: +0.094 | 2022: +0.059 | 2023: +0.126 | 2024: +0.082 | 2025: +0.154 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.051 | 2017: +0.019 | 2018: +0.254 | 2019: +0.498 | 2020: +0.129 | 2021: +0.347 | 2022: +0.262 | 2023: +0.135 | 2024: +0.443 | 2025: +0.037 | 2026: +0.272
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=0.90, Recency ratio=4.00
- Early IC=+0.0259, Recent IC=+0.1038, 1st-half IC=+0.1058, 2nd-half IC=+0.0954, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.085, Q3_mid=+0.078, Q4=+0.093, Q5_high_vol=+0.131

**`combo_min__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.1467, Sharpe=+0.8978)
- Admission: Train IC=+0.2469, Deflated=+0.2472, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.054 | 2017: -0.028 | 2018: +0.080 | 2019: +0.250 | 2020: +0.116 | 2021: +0.094 | 2022: +0.059 | 2023: +0.126 | 2024: +0.082 | 2025: +0.154 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.051 | 2017: +0.019 | 2018: +0.254 | 2019: +0.498 | 2020: +0.129 | 2021: +0.347 | 2022: +0.262 | 2023: +0.135 | 2024: +0.443 | 2025: +0.037 | 2026: +0.272
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=0.90, Recency ratio=4.00
- Early IC=+0.0260, Recent IC=+0.1038, 1st-half IC=+0.1058, 2nd-half IC=+0.0954, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.085, Q3_mid=+0.078, Q4=+0.093, Q5_high_vol=+0.131

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1428, Sharpe=+0.8973)
- Admission: Train IC=+0.2881, Deflated=+0.2871, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.157 | 2017: -0.015 | 2018: +0.175 | 2019: +0.223 | 2020: +0.182 | 2021: +0.158 | 2022: +0.116 | 2023: +0.122 | 2024: +0.081 | 2025: +0.156 | 2026: +0.123
- Yearly Tail ICs:   2015: -0.038 | 2016: +0.188 | 2017: +0.025 | 2018: +0.362 | 2019: +0.438 | 2020: +0.276 | 2021: +0.318 | 2022: +0.195 | 2023: +0.211 | 2024: +0.430 | 2025: +0.180 | 2026: +0.168
- IC CV=0.53, Neg years (linear/tail)=1/0 of 8, Half ratio=0.89, Recency ratio=1.27
- Early IC=+0.0802, Recent IC=+0.1016, 1st-half IC=+0.1435, 2nd-half IC=+0.1277, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.103, Q3_mid=+0.078, Q4=+0.145, Q5_high_vol=+0.221

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1319, Sharpe=+0.8890)
- Admission: Train IC=+0.2533, Deflated=+0.2532, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.116 | 2017: +0.052 | 2018: +0.141 | 2019: +0.216 | 2020: +0.104 | 2021: +0.210 | 2022: +0.071 | 2023: +0.121 | 2024: +0.107 | 2025: +0.162 | 2026: +0.102
- Yearly Tail ICs:   2015: -0.124 | 2016: +0.121 | 2017: +0.194 | 2018: +0.202 | 2019: +0.566 | 2020: +0.083 | 2021: +0.372 | 2022: +0.121 | 2023: +0.269 | 2024: +0.317 | 2025: +0.143 | 2026: +0.127
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=1.18
- Early IC=+0.0968, Recent IC=+0.1142, 1st-half IC=+0.1329, 2nd-half IC=+0.1343, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.099, Q3_mid=+0.111, Q4=+0.160, Q5_high_vol=+0.198

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1339, Sharpe=+0.8863)
- Admission: Train IC=+0.3394, Deflated=+0.3392, IR=0.93, Mono=0.81, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.117 | 2017: -0.012 | 2018: +0.160 | 2019: +0.258 | 2020: +0.178 | 2021: +0.136 | 2022: +0.081 | 2023: +0.154 | 2024: +0.096 | 2025: +0.158 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.071 | 2016: +0.130 | 2017: +0.024 | 2018: +0.370 | 2019: +0.557 | 2020: +0.403 | 2021: +0.292 | 2022: +0.189 | 2023: +0.340 | 2024: +0.441 | 2025: +0.243 | 2026: +0.237
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=0.84, Recency ratio=1.69
- Early IC=+0.0738, Recent IC=+0.1250, 1st-half IC=+0.1509, 2nd-half IC=+0.1271, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.118, Q3_mid=+0.086, Q4=+0.130, Q5_high_vol=+0.223

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1344, Sharpe=+0.8852)
- Admission: Train IC=+0.2925, Deflated=+0.2914, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.123 | 2017: +0.009 | 2018: +0.185 | 2019: +0.200 | 2020: +0.148 | 2021: +0.174 | 2022: +0.129 | 2023: +0.138 | 2024: +0.072 | 2025: +0.163 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.124 | 2017: +0.112 | 2018: +0.408 | 2019: +0.383 | 2020: +0.221 | 2021: +0.448 | 2022: +0.155 | 2023: +0.174 | 2024: +0.396 | 2025: +0.178 | 2026: +0.145
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.08
- Early IC=+0.0971, Recent IC=+0.1048, 1st-half IC=+0.1373, 2nd-half IC=+0.1369, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.120, Q3_mid=+0.077, Q4=+0.139, Q5_high_vol=+0.216

**`combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0`** (Lock IC=+0.0906, Sharpe=+0.8830)
- Admission: Train IC=+0.2151, Deflated=+0.2159, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.142 | 2017: +0.009 | 2018: +0.141 | 2019: +0.207 | 2020: +0.126 | 2021: +0.144 | 2022: +0.069 | 2023: +0.161 | 2024: +0.064 | 2025: +0.154 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.390 | 2016: -0.080 | 2017: +0.071 | 2018: +0.275 | 2019: +0.431 | 2020: +0.069 | 2021: +0.280 | 2022: +0.033 | 2023: +0.367 | 2024: +0.255 | 2025: +0.401 | 2026: +0.073
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=1.50
- Early IC=+0.0753, Recent IC=+0.1127, 1st-half IC=+0.1145, 2nd-half IC=+0.1151, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.095, Q3_mid=+0.089, Q4=+0.080, Q5_high_vol=+0.163

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1533, Sharpe=+0.8711)
- Admission: Train IC=+0.2780, Deflated=+0.2763, IR=0.94, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.77, Recency ratio=2.85
- Early IC=+0.0424, Recent IC=+0.1209, 1st-half IC=+0.0818, 2nd-half IC=+0.1451, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.133, Q3_mid=+0.085, Q4=+0.101, Q5_high_vol=+0.163

**`combo_rank_min__max_up_ret__gap_pct`** (Lock IC=+0.1241, Sharpe=+0.8669)
- Admission: Train IC=+0.2276, Deflated=+0.2265, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.045 | 2017: -0.018 | 2018: +0.036 | 2019: +0.226 | 2020: +0.136 | 2021: +0.125 | 2022: +0.078 | 2023: +0.085 | 2024: +0.060 | 2025: +0.128 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.177 | 2016: +0.107 | 2017: +0.108 | 2018: +0.286 | 2019: +0.470 | 2020: +0.117 | 2021: +0.354 | 2022: +0.076 | 2023: +0.154 | 2024: +0.197 | 2025: +0.081 | 2026: +0.111
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=8.18
- Early IC=+0.0085, Recent IC=+0.0697, 1st-half IC=+0.1033, 2nd-half IC=+0.0982, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.096, Q3_mid=+0.113, Q4=+0.121, Q5_high_vol=+0.111

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1289, Sharpe=+0.8597)
- Admission: Train IC=+0.2864, Deflated=+0.2852, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.151 | 2017: +0.006 | 2018: +0.159 | 2019: +0.210 | 2020: +0.165 | 2021: +0.174 | 2022: +0.127 | 2023: +0.140 | 2024: +0.068 | 2025: +0.180 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.033 | 2016: +0.202 | 2017: +0.058 | 2018: +0.304 | 2019: +0.342 | 2020: +0.238 | 2021: +0.348 | 2022: +0.265 | 2023: +0.287 | 2024: +0.397 | 2025: +0.228 | 2026: -0.061
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=1.26
- Early IC=+0.0827, Recent IC=+0.1039, 1st-half IC=+0.1291, 2nd-half IC=+0.1368, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.107, Q3_mid=+0.094, Q4=+0.133, Q5_high_vol=+0.191

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1497, Sharpe=+0.8445)
- Admission: Train IC=+0.2769, Deflated=+0.2751, IR=0.90, Mono=0.84, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.073 | 2017: -0.002 | 2018: +0.076 | 2019: +0.157 | 2020: +0.087 | 2021: +0.183 | 2022: +0.118 | 2023: +0.148 | 2024: +0.084 | 2025: +0.207 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.080 | 2016: +0.205 | 2017: +0.158 | 2018: +0.182 | 2019: +0.344 | 2020: +0.248 | 2021: +0.237 | 2022: +0.277 | 2023: +0.319 | 2024: +0.382 | 2025: +0.301 | 2026: +0.105
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=1.80, Recency ratio=3.12
- Early IC=+0.0372, Recent IC=+0.1160, 1st-half IC=+0.0791, 2nd-half IC=+0.1428, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.126, Q3_mid=+0.089, Q4=+0.113, Q5_high_vol=+0.151

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1419, Sharpe=+0.8351)
- Admission: Train IC=+0.3040, Deflated=+0.3035, IR=0.84, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.121 | 2017: -0.019 | 2018: +0.157 | 2019: +0.240 | 2020: +0.166 | 2021: +0.144 | 2022: +0.095 | 2023: +0.154 | 2024: +0.081 | 2025: +0.171 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.089 | 2017: -0.027 | 2018: +0.488 | 2019: +0.475 | 2020: +0.344 | 2021: +0.352 | 2022: +0.141 | 2023: +0.267 | 2024: +0.322 | 2025: +0.369 | 2026: +0.282
- IC CV=0.57, Neg years (linear/tail)=1/1 of 8, Half ratio=0.94, Recency ratio=1.74
- Early IC=+0.0673, Recent IC=+0.1174, 1st-half IC=+0.1361, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.123, Q3_mid=+0.067, Q4=+0.110, Q5_high_vol=+0.235

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1275, Sharpe=+0.8333)
- Admission: Train IC=+0.3801, Deflated=+0.3803, IR=1.24, Mono=0.88, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.084 | 2017: -0.024 | 2018: +0.157 | 2019: +0.245 | 2020: +0.161 | 2021: +0.143 | 2022: +0.085 | 2023: +0.178 | 2024: +0.127 | 2025: +0.159 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.123 | 2017: +0.052 | 2018: +0.432 | 2019: +0.562 | 2020: +0.344 | 2021: +0.410 | 2022: +0.264 | 2023: +0.420 | 2024: +0.408 | 2025: +0.166 | 2026: +0.332
- IC CV=0.55, Neg years (linear/tail)=1/0 of 8, Half ratio=1.05, Recency ratio=2.29
- Early IC=+0.0665, Recent IC=+0.1524, 1st-half IC=+0.1341, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.110, Q3_mid=+0.113, Q4=+0.143, Q5_high_vol=+0.196

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+0.7977)
- Admission: Train IC=+0.2636, Deflated=+0.2619, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.131 | 2017: +0.009 | 2018: +0.116 | 2019: +0.207 | 2020: +0.160 | 2021: +0.158 | 2022: +0.128 | 2023: +0.164 | 2024: +0.081 | 2025: +0.174 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.177 | 2017: +0.053 | 2018: +0.295 | 2019: +0.445 | 2020: +0.180 | 2021: +0.368 | 2022: +0.285 | 2023: +0.268 | 2024: +0.296 | 2025: +0.125 | 2026: +0.032
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.98
- Early IC=+0.0624, Recent IC=+0.1232, 1st-half IC=+0.1271, 2nd-half IC=+0.1435, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.126, Q3_mid=+0.107, Q4=+0.134, Q5_high_vol=+0.198

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1135, Sharpe=+0.7682)
- Admission: Train IC=+0.2885, Deflated=+0.2871, IR=0.94, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.074 | 2017: +0.031 | 2018: +0.130 | 2019: +0.196 | 2020: +0.124 | 2021: +0.157 | 2022: +0.130 | 2023: +0.164 | 2024: +0.116 | 2025: +0.178 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.132 | 2017: +0.091 | 2018: +0.225 | 2019: +0.533 | 2020: +0.127 | 2021: +0.272 | 2022: +0.322 | 2023: +0.436 | 2024: +0.349 | 2025: +0.154 | 2026: +0.022
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.74
- Early IC=+0.0805, Recent IC=+0.1398, 1st-half IC=+0.1165, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.099, Q3_mid=+0.114, Q4=+0.130, Q5_high_vol=+0.185

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1249, Sharpe=+0.7559)
- Admission: Train IC=+0.3315, Deflated=+0.3315, IR=1.04, Mono=0.84, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.062 | 2017: -0.013 | 2018: +0.140 | 2019: +0.238 | 2020: +0.131 | 2021: +0.127 | 2022: +0.106 | 2023: +0.177 | 2024: +0.118 | 2025: +0.164 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.061 | 2017: +0.012 | 2018: +0.369 | 2019: +0.503 | 2020: +0.210 | 2021: +0.279 | 2022: +0.296 | 2023: +0.453 | 2024: +0.370 | 2025: +0.128 | 2026: +0.206
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=2.32
- Early IC=+0.0637, Recent IC=+0.1478, 1st-half IC=+0.1248, 2nd-half IC=+0.1373, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.111, Q3_mid=+0.118, Q4=+0.127, Q5_high_vol=+0.185

**`combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1093, Sharpe=+0.7465)
- Admission: Train IC=+0.2577, Deflated=+0.2562, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.058 | 2017: +0.024 | 2018: +0.099 | 2019: +0.234 | 2020: +0.055 | 2021: +0.191 | 2022: +0.052 | 2023: +0.123 | 2024: +0.077 | 2025: +0.131 | 2026: +0.098
- Yearly Tail ICs:   2015: +0.207 | 2016: +0.085 | 2017: +0.070 | 2018: +0.192 | 2019: +0.436 | 2020: +0.121 | 2021: +0.345 | 2022: +0.164 | 2023: +0.349 | 2024: +0.329 | 2025: +0.116 | 2026: +0.136
- IC CV=0.64, Neg years (linear/tail)=0/0 of 8, Half ratio=1.15, Recency ratio=1.63
- Early IC=+0.0613, Recent IC=+0.1001, 1st-half IC=+0.1050, 2nd-half IC=+0.1208, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.092, Q2=+0.108, Q3_mid=+0.124, Q4=+0.122, Q5_high_vol=+0.147

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0659, Sharpe=+0.7397)
- Admission: Train IC=+0.1602, Deflated=+0.1611, IR=0.50, Mono=0.73, p=0.0022, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.162 | 2017: +0.008 | 2018: +0.135 | 2019: +0.197 | 2020: +0.110 | 2021: +0.134 | 2022: +0.058 | 2023: +0.150 | 2024: +0.061 | 2025: +0.114 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.213 | 2016: -0.007 | 2017: +0.182 | 2018: +0.264 | 2019: +0.189 | 2020: +0.132 | 2021: +0.304 | 2022: +0.034 | 2023: +0.403 | 2024: +0.123 | 2025: +0.229 | 2026: +0.139
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=1.48
- Early IC=+0.0715, Recent IC=+0.1055, 1st-half IC=+0.1115, 2nd-half IC=+0.1046, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.086, Q3_mid=+0.070, Q4=+0.066, Q5_high_vol=+0.157

**`combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1248, Sharpe=+0.7342)
- Admission: Train IC=+0.2593, Deflated=+0.2579, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.063 | 2017: +0.017 | 2018: +0.130 | 2019: +0.211 | 2020: +0.112 | 2021: +0.147 | 2022: +0.119 | 2023: +0.149 | 2024: +0.123 | 2025: +0.153 | 2026: +0.097
- Yearly Tail ICs:   2015: +0.046 | 2016: +0.048 | 2017: +0.071 | 2018: +0.226 | 2019: +0.453 | 2020: +0.164 | 2021: +0.240 | 2022: +0.205 | 2023: +0.325 | 2024: +0.375 | 2025: +0.113 | 2026: +0.173
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.17, Recency ratio=1.85
- Early IC=+0.0737, Recent IC=+0.1361, 1st-half IC=+0.1204, 2nd-half IC=+0.1414, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.093, Q3_mid=+0.116, Q4=+0.138, Q5_high_vol=+0.180

**`combo_clamp_diff__volume_weighted_price_position__body_size_progression`** (Lock IC=+0.0607, Sharpe=+0.7191)
- Admission: Train IC=+0.2219, Deflated=+0.2236, IR=0.39, Mono=0.66, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.070 | 2017: +0.054 | 2018: +0.101 | 2019: +0.253 | 2020: +0.079 | 2021: +0.097 | 2022: +0.032 | 2023: +0.144 | 2024: +0.045 | 2025: +0.087 | 2026: +0.036
- Yearly Tail ICs:   2015: +0.108 | 2016: -0.099 | 2017: +0.018 | 2018: +0.076 | 2019: +0.541 | 2020: +0.009 | 2021: +0.217 | 2022: +0.162 | 2023: +0.215 | 2024: +0.072 | 2025: +0.174 | 2026: -0.313
- IC CV=0.66, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=1.22
- Early IC=+0.0773, Recent IC=+0.0943, 1st-half IC=+0.1107, 2nd-half IC=+0.0888, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.84)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.072, Q3_mid=+0.088, Q4=+0.128, Q5_high_vol=+0.103

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1308, Sharpe=+0.7043)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.46, Mono=0.68, p=0.0004, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.009 | 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103 | 2024: +0.117 | 2025: +0.125 | 2026: +0.147
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.030 | 2017: +0.155 | 2018: +0.235 | 2019: +0.268 | 2020: +0.153 | 2021: +0.188 | 2022: +0.076 | 2023: +0.066 | 2024: +0.234 | 2025: +0.025 | 2026: +0.202
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.38, Recency ratio=3.68
- Early IC=+0.0299, Recent IC=+0.1100, 1st-half IC=+0.0914, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.131, Q3_mid=+0.066, Q4=+0.120, Q5_high_vol=+0.153

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1428, Sharpe=+0.6972)
- Admission: Train IC=+0.1916, Deflated=+0.1896, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.038 | 2017: -0.003 | 2018: +0.098 | 2019: +0.181 | 2020: +0.120 | 2021: +0.143 | 2022: +0.150 | 2023: +0.108 | 2024: +0.090 | 2025: +0.161 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.138 | 2017: +0.068 | 2018: +0.192 | 2019: +0.334 | 2020: +0.162 | 2021: +0.248 | 2022: +0.108 | 2023: +0.106 | 2024: +0.018 | 2025: +0.421 | 2026: +0.241
- IC CV=0.46, Neg years (linear/tail)=1/0 of 8, Half ratio=1.20, Recency ratio=2.09
- Early IC=+0.0473, Recent IC=+0.0988, 1st-half IC=+0.1106, 2nd-half IC=+0.1328, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.121, Q3_mid=+0.097, Q4=+0.116, Q5_high_vol=+0.189

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1356, Sharpe=+0.6928)
- Admission: Train IC=+0.2920, Deflated=+0.2917, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.073 | 2017: -0.020 | 2018: +0.100 | 2019: +0.254 | 2020: +0.122 | 2021: +0.109 | 2022: +0.080 | 2023: +0.148 | 2024: +0.090 | 2025: +0.155 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.072 | 2017: +0.019 | 2018: +0.277 | 2019: +0.481 | 2020: +0.204 | 2021: +0.300 | 2022: +0.244 | 2023: +0.203 | 2024: +0.379 | 2025: +0.089 | 2026: +0.270
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=0.98, Recency ratio=2.98
- Early IC=+0.0399, Recent IC=+0.1191, 1st-half IC=+0.1170, 2nd-half IC=+0.1147, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.107, Q3_mid=+0.065, Q4=+0.100, Q5_high_vol=+0.182

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1308, Sharpe=+0.6052)
- Admission: Train IC=+0.2322, Deflated=+0.2318, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.117 | 2017: +0.048 | 2018: +0.105 | 2019: +0.222 | 2020: +0.126 | 2021: +0.135 | 2022: +0.095 | 2023: +0.154 | 2024: +0.083 | 2025: +0.205 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.128 | 2016: +0.081 | 2017: +0.211 | 2018: +0.258 | 2019: +0.330 | 2020: +0.214 | 2021: +0.227 | 2022: +0.152 | 2023: +0.346 | 2024: +0.274 | 2025: +0.264 | 2026: +0.077
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=1.54
- Early IC=+0.0767, Recent IC=+0.1184, 1st-half IC=+0.1202, 2nd-half IC=+0.1260, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.105, Q3_mid=+0.096, Q4=+0.104, Q5_high_vol=+0.159

**`combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1353, Sharpe=+0.5812)
- Admission: Train IC=+0.3064, Deflated=+0.3065, IR=0.93, Mono=0.83, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.082 | 2017: -0.037 | 2018: +0.111 | 2019: +0.260 | 2020: +0.142 | 2021: +0.120 | 2022: +0.069 | 2023: +0.150 | 2024: +0.106 | 2025: +0.150 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.211 | 2016: +0.099 | 2017: +0.020 | 2018: +0.287 | 2019: +0.512 | 2020: +0.208 | 2021: +0.306 | 2022: +0.245 | 2023: +0.352 | 2024: +0.400 | 2025: +0.093 | 2026: +0.237
- IC CV=0.67, Neg years (linear/tail)=1/0 of 8, Half ratio=0.98, Recency ratio=3.46
- Early IC=+0.0370, Recent IC=+0.1282, 1st-half IC=+0.1217, 2nd-half IC=+0.1190, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.099, Q3_mid=+0.082, Q4=+0.111, Q5_high_vol=+0.185

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1421, Sharpe=+0.5695)
- Admission: Train IC=+0.2358, Deflated=+0.2340, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.062 | 2017: +0.024 | 2018: +0.086 | 2019: +0.155 | 2020: +0.111 | 2021: +0.160 | 2022: +0.135 | 2023: +0.131 | 2024: +0.114 | 2025: +0.193 | 2026: +0.064
- Yearly Tail ICs:   2015: -0.049 | 2016: +0.155 | 2017: +0.141 | 2018: +0.115 | 2019: +0.416 | 2020: +0.103 | 2021: +0.203 | 2022: +0.233 | 2023: +0.268 | 2024: +0.375 | 2025: +0.216 | 2026: -0.023
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=2.24
- Early IC=+0.0548, Recent IC=+0.1226, 1st-half IC=+0.0917, 2nd-half IC=+0.1423, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.087, Q3_mid=+0.107, Q4=+0.106, Q5_high_vol=+0.172

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.1100, Sharpe=+0.5568)
- Admission: Train IC=+0.2297, Deflated=+0.2299, IR=0.78, Mono=0.81, p=0.0000, MaxCorr=0.36
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.112 | 2017: -0.039 | 2018: +0.156 | 2019: +0.124 | 2020: +0.144 | 2021: +0.056 | 2022: +0.185 | 2023: +0.124 | 2024: +0.055 | 2025: +0.080 | 2026: +0.143
- Yearly Tail ICs:   2015: +0.074 | 2016: +0.385 | 2017: +0.158 | 2018: +0.385 | 2019: +0.386 | 2020: +0.301 | 2021: +0.156 | 2022: +0.438 | 2023: +0.126 | 2024: +0.007 | 2025: +0.073 | 2026: +0.091
- IC CV=0.67, Neg years (linear/tail)=1/0 of 8, Half ratio=0.87, Recency ratio=1.54
- Early IC=+0.0581, Recent IC=+0.0895, 1st-half IC=+0.1131, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.29)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.161, Q3_mid=+0.052, Q4=+0.134, Q5_high_vol=+0.190

**`combo_mean__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0849, Sharpe=+0.5225)
- Admission: Train IC=+0.1889, Deflated=+0.1892, IR=0.54, Mono=0.69, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.110 | 2017: +0.075 | 2018: +0.140 | 2019: +0.178 | 2020: +0.160 | 2021: +0.117 | 2022: +0.080 | 2023: +0.141 | 2024: +0.069 | 2025: +0.126 | 2026: +0.037
- Yearly Tail ICs:   2015: +0.150 | 2016: +0.086 | 2017: -0.024 | 2018: +0.288 | 2019: +0.276 | 2020: +0.127 | 2021: +0.290 | 2022: +0.127 | 2023: +0.412 | 2024: +0.162 | 2025: +0.096 | 2026: +0.112
- IC CV=0.32, Neg years (linear/tail)=0/1 of 8, Half ratio=0.86, Recency ratio=0.98
- Early IC=+0.1076, Recent IC=+0.1051, 1st-half IC=+0.1273, 2nd-half IC=+0.1097, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.086, Q3_mid=+0.094, Q4=+0.103, Q5_high_vol=+0.169

**`combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1340, Sharpe=+0.5076)
- Admission: Train IC=+0.2549, Deflated=+0.2555, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.060 | 2017: +0.036 | 2018: +0.120 | 2019: +0.221 | 2020: +0.040 | 2021: +0.168 | 2022: +0.043 | 2023: +0.112 | 2024: +0.095 | 2025: +0.141 | 2026: +0.121
- Yearly Tail ICs:   2015: +0.156 | 2016: -0.109 | 2017: +0.135 | 2018: +0.141 | 2019: +0.574 | 2020: +0.091 | 2021: +0.327 | 2022: +0.112 | 2023: +0.291 | 2024: +0.310 | 2025: +0.149 | 2026: +0.183
- IC CV=0.59, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=1.33
- Early IC=+0.0778, Recent IC=+0.1035, 1st-half IC=+0.1042, 2nd-half IC=+0.1125, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.066, Q3_mid=+0.108, Q4=+0.129, Q5_high_vol=+0.142

**`combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1133, Sharpe=+0.4549)
- Admission: Train IC=+0.2413, Deflated=+0.2405, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.011 | 2017: +0.014 | 2018: +0.093 | 2019: +0.194 | 2020: +0.097 | 2021: +0.147 | 2022: +0.123 | 2023: +0.168 | 2024: +0.089 | 2025: +0.191 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.038 | 2017: +0.091 | 2018: -0.042 | 2019: +0.361 | 2020: +0.225 | 2021: +0.225 | 2022: +0.284 | 2023: +0.443 | 2024: +0.255 | 2025: +0.266 | 2026: -0.148
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.38, Recency ratio=2.40
- Early IC=+0.0535, Recent IC=+0.1284, 1st-half IC=+0.1009, 2nd-half IC=+0.1397, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.104, Q3_mid=+0.134, Q4=+0.099, Q5_high_vol=+0.159

**`combo_max__volatility_expansion_trend_vector__volume_price_confirmation`** (Lock IC=+0.0823, Sharpe=+0.4441)
- Admission: Train IC=+0.2105, Deflated=+0.2107, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.086 | 2017: +0.031 | 2018: +0.100 | 2019: +0.189 | 2020: +0.174 | 2021: +0.141 | 2022: +0.036 | 2023: +0.128 | 2024: +0.057 | 2025: +0.156 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.486 | 2016: -0.163 | 2017: +0.096 | 2018: +0.220 | 2019: +0.371 | 2020: +0.251 | 2021: +0.209 | 2022: +0.087 | 2023: +0.213 | 2024: +0.245 | 2025: +0.228 | 2026: +0.251
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=1.42
- Early IC=+0.0654, Recent IC=+0.0925, 1st-half IC=+0.1159, 2nd-half IC=+0.0986, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.125, Q2=+0.070, Q3_mid=+0.144, Q4=+0.080, Q5_high_vol=+0.130

**`combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1024, Sharpe=+0.4428)
- Admission: Train IC=+0.2029, Deflated=+0.2030, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.127 | 2017: -0.022 | 2018: +0.068 | 2019: +0.172 | 2020: +0.165 | 2021: +0.111 | 2022: +0.079 | 2023: +0.094 | 2024: +0.136 | 2025: +0.118 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.046 | 2017: +0.222 | 2018: +0.095 | 2019: +0.236 | 2020: +0.100 | 2021: +0.336 | 2022: +0.155 | 2023: +0.180 | 2024: +0.324 | 2025: +0.135 | 2026: +0.062
- IC CV=0.58, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=5.06
- Early IC=+0.0227, Recent IC=+0.1148, 1st-half IC=+0.1003, 2nd-half IC=+0.1146, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.100, Q3_mid=+0.094, Q4=+0.095, Q5_high_vol=+0.118

**`combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1066, Sharpe=+0.4207)
- Admission: Train IC=+0.1878, Deflated=+0.1863, IR=0.57, Mono=0.68, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.052 | 2017: +0.029 | 2018: +0.069 | 2019: +0.159 | 2020: +0.077 | 2021: +0.126 | 2022: +0.154 | 2023: +0.127 | 2024: +0.128 | 2025: +0.133 | 2026: +0.094
- Yearly Tail ICs:   2015: +0.095 | 2016: +0.100 | 2017: +0.102 | 2018: +0.074 | 2019: +0.343 | 2020: +0.004 | 2021: +0.288 | 2022: +0.085 | 2023: +0.199 | 2024: +0.256 | 2025: +0.133 | 2026: +0.046
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.67, Recency ratio=2.71
- Early IC=+0.0479, Recent IC=+0.1296, 1st-half IC=+0.0830, 2nd-half IC=+0.1389, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.107, Q3_mid=+0.067, Q4=+0.114, Q5_high_vol=+0.152

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1058, Sharpe=+0.4149)
- Admission: Train IC=+0.2452, Deflated=+0.2443, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.015 | 2017: +0.016 | 2018: +0.085 | 2019: +0.204 | 2020: +0.098 | 2021: +0.135 | 2022: +0.123 | 2023: +0.167 | 2024: +0.100 | 2025: +0.184 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.263 | 2016: +0.032 | 2017: +0.065 | 2018: -0.023 | 2019: +0.361 | 2020: +0.235 | 2021: +0.220 | 2022: +0.300 | 2023: +0.472 | 2024: +0.256 | 2025: +0.279 | 2026: -0.152
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.37, Recency ratio=2.62
- Early IC=+0.0509, Recent IC=+0.1332, 1st-half IC=+0.1020, 2nd-half IC=+0.1398, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.106, Q3_mid=+0.130, Q4=+0.100, Q5_high_vol=+0.166

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1296, Sharpe=+0.3365)
- Admission: Train IC=+0.2847, Deflated=+0.2842, IR=0.84, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.096 | 2017: -0.001 | 2018: +0.155 | 2019: +0.246 | 2020: +0.145 | 2021: +0.127 | 2022: +0.095 | 2023: +0.139 | 2024: +0.074 | 2025: +0.159 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.152 | 2016: +0.057 | 2017: +0.092 | 2018: +0.305 | 2019: +0.509 | 2020: +0.194 | 2021: +0.254 | 2022: +0.253 | 2023: +0.208 | 2024: +0.405 | 2025: +0.130 | 2026: +0.237
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.83, Recency ratio=1.38
- Early IC=+0.0771, Recent IC=+0.1062, 1st-half IC=+0.1414, 2nd-half IC=+0.1180, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.117, Q3_mid=+0.071, Q4=+0.114, Q5_high_vol=+0.217

**`combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early`** (Lock IC=+0.1102, Sharpe=+0.3258)
- Admission: Train IC=+0.2173, Deflated=+0.2164, IR=0.36, Mono=0.65, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.107 | 2017: -0.083 | 2018: +0.058 | 2019: +0.093 | 2020: +0.158 | 2021: +0.065 | 2022: +0.157 | 2023: +0.211 | 2024: +0.037 | 2025: +0.104 | 2026: +0.128
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.120 | 2017: -0.154 | 2018: +0.309 | 2019: +0.169 | 2020: +0.323 | 2021: +0.283 | 2022: +0.263 | 2023: +0.121 | 2024: +0.011 | 2025: +0.059 | 2026: +0.131
- IC CV=0.98, Neg years (linear/tail)=1/1 of 8, Half ratio=1.51, Recency ratio=-9.60
- Early IC=-0.0129, Recent IC=+0.1241, 1st-half IC=+0.0738, 2nd-half IC=+0.1110, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.131, Q3_mid=+0.089, Q4=+0.068, Q5_high_vol=+0.166

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1056, Sharpe=+0.3256)
- Admission: Train IC=+0.2367, Deflated=+0.2353, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.033 | 2017: +0.023 | 2018: +0.078 | 2019: +0.178 | 2020: +0.092 | 2021: +0.165 | 2022: +0.155 | 2023: +0.149 | 2024: +0.068 | 2025: +0.196 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.001 | 2016: +0.245 | 2017: +0.029 | 2018: +0.111 | 2019: +0.352 | 2020: +0.158 | 2021: +0.338 | 2022: +0.376 | 2023: +0.334 | 2024: +0.198 | 2025: +0.255 | 2026: -0.249
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=2.15
- Early IC=+0.0506, Recent IC=+0.1086, 1st-half IC=+0.0925, 2nd-half IC=+0.1437, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.114, Q3_mid=+0.115, Q4=+0.098, Q5_high_vol=+0.157

**`combo_rel_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0872, Sharpe=+0.2933)
- Admission: Train IC=+0.2116, Deflated=+0.2104, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=0.64
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.116 | 2017: +0.115 | 2018: +0.053 | 2019: +0.076 | 2020: +0.106 | 2021: +0.117 | 2022: +0.082 | 2023: +0.158 | 2024: +0.132 | 2025: +0.149 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.236 | 2016: +0.074 | 2017: +0.226 | 2018: +0.114 | 2019: +0.276 | 2020: +0.089 | 2021: +0.293 | 2022: +0.315 | 2023: +0.381 | 2024: +0.098 | 2025: +0.271 | 2026: -0.194
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=1.47, Recency ratio=1.72
- Early IC=+0.0841, Recent IC=+0.1447, 1st-half IC=+0.0801, 2nd-half IC=+0.1181, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.087, Q3_mid=+0.105, Q4=+0.085, Q5_high_vol=+0.089

**`combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1453, Sharpe=+0.2923)
- Admission: Train IC=+0.2057, Deflated=+0.2041, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.009 | 2017: +0.018 | 2018: +0.064 | 2019: +0.156 | 2020: +0.059 | 2021: +0.140 | 2022: +0.112 | 2023: +0.124 | 2024: +0.099 | 2025: +0.174 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.064 | 2017: +0.129 | 2018: +0.125 | 2019: +0.411 | 2020: +0.019 | 2021: +0.130 | 2022: +0.233 | 2023: +0.231 | 2024: +0.362 | 2025: +0.141 | 2026: -0.031
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.75, Recency ratio=2.72
- Early IC=+0.0412, Recent IC=+0.1118, 1st-half IC=+0.0723, 2nd-half IC=+0.1267, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.059, Q3_mid=+0.110, Q4=+0.086, Q5_high_vol=+0.125

**`combo_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0690, Sharpe=+0.2563)
- Admission: Train IC=+0.1969, Deflated=+0.1959, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.119 | 2017: +0.114 | 2018: +0.059 | 2019: +0.081 | 2020: +0.110 | 2021: +0.111 | 2022: +0.109 | 2023: +0.156 | 2024: +0.135 | 2025: +0.153 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.235 | 2016: +0.069 | 2017: +0.182 | 2018: +0.139 | 2019: +0.225 | 2020: +0.075 | 2021: +0.275 | 2022: +0.347 | 2023: +0.308 | 2024: +0.109 | 2025: +0.279 | 2026: -0.101
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.52, Recency ratio=1.68
- Early IC=+0.0864, Recent IC=+0.1455, 1st-half IC=+0.0813, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.089, Q3_mid=+0.093, Q4=+0.096, Q5_high_vol=+0.102

**`combo_mean__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1319, Sharpe=+0.2487)
- Admission: Train IC=+0.2459, Deflated=+0.2439, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.076 | 2017: +0.021 | 2018: +0.132 | 2019: +0.164 | 2020: +0.128 | 2021: +0.161 | 2022: +0.153 | 2023: +0.139 | 2024: +0.112 | 2025: +0.177 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.041 | 2016: +0.205 | 2017: +0.125 | 2018: +0.280 | 2019: +0.362 | 2020: +0.165 | 2021: +0.295 | 2022: +0.265 | 2023: +0.170 | 2024: +0.314 | 2025: +0.159 | 2026: +0.112
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.33, Recency ratio=1.64
- Early IC=+0.0763, Recent IC=+0.1254, 1st-half IC=+0.1122, 2nd-half IC=+0.1493, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.115, Q3_mid=+0.089, Q4=+0.135, Q5_high_vol=+0.199

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`** (Lock IC=+0.0936, Sharpe=+0.2427)
- Admission: Train IC=+0.2163, Deflated=+0.2151, IR=0.51, Mono=0.73, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.152 | 2017: -0.074 | 2018: +0.153 | 2019: +0.109 | 2020: +0.124 | 2021: +0.065 | 2022: +0.159 | 2023: +0.150 | 2024: +0.081 | 2025: +0.076 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.126 | 2016: +0.243 | 2017: +0.039 | 2018: +0.350 | 2019: +0.181 | 2020: +0.377 | 2021: +0.191 | 2022: +0.359 | 2023: -0.018 | 2024: +0.160 | 2025: +0.067 | 2026: +0.190
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=1.07, Recency ratio=2.90
- Early IC=+0.0397, Recent IC=+0.1150, 1st-half IC=+0.0999, 2nd-half IC=+0.1070, Neg regimes=1/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.29)
- Regime ICs: Q1_low_vol=-0.005, Q2=+0.148, Q3_mid=+0.069, Q4=+0.139, Q5_high_vol=+0.155

**`combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1003, Sharpe=+0.2207)
- Admission: Train IC=+0.1889, Deflated=+0.1875, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.084 | 2017: +0.029 | 2018: +0.075 | 2019: +0.150 | 2020: +0.123 | 2021: +0.146 | 2022: +0.142 | 2023: +0.146 | 2024: +0.122 | 2025: +0.126 | 2026: +0.099
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.176 | 2017: +0.067 | 2018: +0.217 | 2019: +0.251 | 2020: +0.099 | 2021: +0.327 | 2022: +0.131 | 2023: +0.252 | 2024: +0.165 | 2025: +0.096 | 2026: +0.143
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.51, Recency ratio=2.57
- Early IC=+0.0521, Recent IC=+0.1338, 1st-half IC=+0.0950, 2nd-half IC=+0.1436, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.085, Q3_mid=+0.086, Q4=+0.116, Q5_high_vol=+0.182

**`combo_min__max_up_ret__bar_ret_0`** (Lock IC=+0.0839, Sharpe=+0.2124)
- Admission: Train IC=+0.1748, Deflated=+0.1745, IR=0.60, Mono=0.76, p=0.0012, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.088 | 2017: +0.044 | 2018: +0.107 | 2019: +0.173 | 2020: +0.097 | 2021: +0.136 | 2022: +0.086 | 2023: +0.173 | 2024: +0.057 | 2025: +0.136 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.224 | 2016: +0.008 | 2017: +0.130 | 2018: +0.194 | 2019: +0.244 | 2020: +0.023 | 2021: +0.235 | 2022: +0.201 | 2023: +0.365 | 2024: +0.124 | 2025: +0.179 | 2026: +0.205
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.24, Recency ratio=1.52
- Early IC=+0.0756, Recent IC=+0.1149, 1st-half IC=+0.0939, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.087, Q3_mid=+0.086, Q4=+0.068, Q5_high_vol=+0.149

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0724, Sharpe=+0.2056)
- Admission: Train IC=+0.2233, Deflated=+0.2230, IR=0.84, Mono=0.77, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.094 | 2017: +0.056 | 2018: +0.107 | 2019: +0.186 | 2020: +0.126 | 2021: +0.128 | 2022: +0.105 | 2023: +0.187 | 2024: +0.077 | 2025: +0.134 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.076 | 2016: +0.038 | 2017: +0.103 | 2018: +0.271 | 2019: +0.272 | 2020: +0.167 | 2021: +0.310 | 2022: +0.169 | 2023: +0.524 | 2024: +0.203 | 2025: +0.153 | 2026: -0.198
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.18, Recency ratio=1.62
- Early IC=+0.0816, Recent IC=+0.1323, 1st-half IC=+0.1110, 2nd-half IC=+0.1308, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.090, Q3_mid=+0.099, Q4=+0.120, Q5_high_vol=+0.155

**`combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1073, Sharpe=+0.1834)
- Admission: Train IC=+0.1852, Deflated=+0.1839, IR=0.53, Mono=0.68, p=0.0004, MaxCorr=0.67
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.070 | 2017: +0.032 | 2018: +0.121 | 2019: +0.197 | 2020: +0.150 | 2021: +0.137 | 2022: +0.137 | 2023: +0.160 | 2024: +0.139 | 2025: +0.101 | 2026: +0.130
- Yearly Tail ICs:   2015: -0.119 | 2016: +0.179 | 2017: +0.085 | 2018: +0.307 | 2019: +0.408 | 2020: +0.114 | 2021: +0.174 | 2022: +0.002 | 2023: +0.261 | 2024: +0.242 | 2025: +0.081 | 2026: +0.335
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=1.94
- Early IC=+0.0768, Recent IC=+0.1493, 1st-half IC=+0.1341, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.111, Q3_mid=+0.045, Q4=+0.160, Q5_high_vol=+0.261

**`combo_rank_max__max_up_ret__volume_price_confirmation`** (Lock IC=+0.0663, Sharpe=+0.1804)
- Admission: Train IC=+0.2214, Deflated=+0.2220, IR=0.59, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.109 | 2017: +0.040 | 2018: +0.104 | 2019: +0.185 | 2020: +0.152 | 2021: +0.148 | 2022: +0.074 | 2023: +0.104 | 2024: +0.068 | 2025: +0.124 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.203 | 2016: -0.029 | 2017: -0.034 | 2018: +0.273 | 2019: +0.276 | 2020: +0.150 | 2021: +0.289 | 2022: +0.175 | 2023: +0.237 | 2024: +0.317 | 2025: +0.082 | 2026: +0.008
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.99, Recency ratio=1.22
- Early IC=+0.0716, Recent IC=+0.0873, 1st-half IC=+0.1139, 2nd-half IC=+0.1131, Neg regimes=0/5
- Weak component: `volume_price_confirmation` (CV=0.60)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.083, Q3_mid=+0.116, Q4=+0.109, Q5_high_vol=+0.143

**`combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1138, Sharpe=+0.1660)
- Admission: Train IC=+0.1709, Deflated=+0.1697, IR=0.48, Mono=0.67, p=0.0012, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.051 | 2017: +0.034 | 2018: +0.055 | 2019: +0.129 | 2020: +0.102 | 2021: +0.115 | 2022: +0.137 | 2023: +0.140 | 2024: +0.120 | 2025: +0.166 | 2026: +0.055
- Yearly Tail ICs:   2015: -0.025 | 2016: +0.071 | 2017: +0.127 | 2018: +0.126 | 2019: +0.276 | 2020: +0.113 | 2021: +0.205 | 2022: +0.131 | 2023: +0.131 | 2024: +0.205 | 2025: +0.034 | 2026: -0.063
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.79, Recency ratio=2.92
- Early IC=+0.0445, Recent IC=+0.1298, 1st-half IC=+0.0758, 2nd-half IC=+0.1358, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.070, Q3_mid=+0.117, Q4=+0.068, Q5_high_vol=+0.147

**`combo_clamp_diff__max_up_ret__keltner_squeeze_width`** (Lock IC=+0.0633, Sharpe=+0.1638)
- Admission: Train IC=+0.1917, Deflated=+0.1907, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.119 | 2017: +0.114 | 2018: +0.059 | 2019: +0.080 | 2020: +0.110 | 2021: +0.110 | 2022: +0.107 | 2023: +0.155 | 2024: +0.134 | 2025: +0.146 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.004 | 2017: +0.194 | 2018: +0.160 | 2019: +0.316 | 2020: +0.059 | 2021: +0.264 | 2022: +0.286 | 2023: +0.293 | 2024: +0.195 | 2025: +0.123 | 2026: -0.144
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=1.53, Recency ratio=1.67
- Early IC=+0.0865, Recent IC=+0.1446, 1st-half IC=+0.0806, 2nd-half IC=+0.1234, Neg regimes=0/5
- Weak component: `keltner_squeeze_width` (CV=0.68)
- Regime ICs: Q1_low_vol=+0.094, Q2=+0.089, Q3_mid=+0.093, Q4=+0.093, Q5_high_vol=+0.097

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1162, Sharpe=+0.1600)
- Admission: Train IC=+0.2326, Deflated=+0.2319, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.123 | 2017: +0.038 | 2018: +0.089 | 2019: +0.201 | 2020: +0.122 | 2021: +0.157 | 2022: +0.119 | 2023: +0.187 | 2024: +0.045 | 2025: +0.171 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.103 | 2016: +0.114 | 2017: +0.179 | 2018: +0.308 | 2019: +0.241 | 2020: +0.103 | 2021: +0.354 | 2022: +0.184 | 2023: +0.307 | 2024: +0.188 | 2025: +0.210 | 2026: +0.063
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.83
- Early IC=+0.0635, Recent IC=+0.1160, 1st-half IC=+0.1102, 2nd-half IC=+0.1339, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.138, Q3_mid=+0.091, Q4=+0.089, Q5_high_vol=+0.138

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1259, Sharpe=+0.1557)
- Admission: Train IC=+0.2356, Deflated=+0.2340, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.095 | 2017: +0.037 | 2018: +0.095 | 2019: +0.149 | 2020: +0.075 | 2021: +0.149 | 2022: +0.145 | 2023: +0.133 | 2024: +0.126 | 2025: +0.134 | 2026: +0.114
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.234 | 2017: +0.082 | 2018: +0.290 | 2019: +0.320 | 2020: +0.160 | 2021: +0.235 | 2022: +0.298 | 2023: +0.339 | 2024: +0.340 | 2025: -0.069 | 2026: +0.277
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.64, Recency ratio=1.97
- Early IC=+0.0659, Recent IC=+0.1298, 1st-half IC=+0.0881, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.118, Q3_mid=+0.092, Q4=+0.110, Q5_high_vol=+0.207

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct`** (Lock IC=+0.0515, Sharpe=+0.1414)
- Admission: Train IC=+0.2087, Deflated=+0.2078, IR=1.03, Mono=0.82, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.080 | 2017: +0.050 | 2018: +0.058 | 2019: +0.142 | 2020: +0.102 | 2021: +0.147 | 2022: +0.102 | 2023: +0.177 | 2024: +0.072 | 2025: +0.153 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.184 | 2016: +0.232 | 2017: +0.050 | 2018: +0.213 | 2019: +0.330 | 2020: +0.226 | 2021: +0.202 | 2022: +0.279 | 2023: +0.452 | 2024: +0.131 | 2025: +0.141 | 2026: -0.331
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.77, Recency ratio=2.32
- Early IC=+0.0539, Recent IC=+0.1249, 1st-half IC=+0.0752, 2nd-half IC=+0.1332, Neg regimes=0/5
- Weak component: `gap_pct` (CV=1.43)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.088, Q3_mid=+0.121, Q4=+0.080, Q5_high_vol=+0.103

**`combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0673, Sharpe=+0.1332)
- Admission: Train IC=+0.2480, Deflated=+0.2489, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.043 | 2017: +0.029 | 2018: +0.087 | 2019: +0.188 | 2020: +0.050 | 2021: +0.161 | 2022: +0.051 | 2023: +0.184 | 2024: +0.081 | 2025: +0.171 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.290 | 2016: -0.062 | 2017: -0.026 | 2018: +0.161 | 2019: +0.474 | 2020: +0.209 | 2021: +0.351 | 2022: +0.108 | 2023: +0.425 | 2024: +0.209 | 2025: +0.338 | 2026: -0.146
- IC CV=0.57, Neg years (linear/tail)=0/1 of 8, Half ratio=1.59, Recency ratio=2.30
- Early IC=+0.0572, Recent IC=+0.1314, 1st-half IC=+0.0796, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.092, Q3_mid=+0.134, Q4=+0.093, Q5_high_vol=+0.117

**`combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early`** (Lock IC=+0.0786, Sharpe=+0.0918)
- Admission: Train IC=+0.2137, Deflated=+0.2129, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.136 | 2017: +0.040 | 2018: +0.131 | 2019: +0.182 | 2020: +0.133 | 2021: +0.089 | 2022: +0.060 | 2023: +0.137 | 2024: +0.143 | 2025: +0.074 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.091 | 2016: +0.096 | 2017: -0.027 | 2018: +0.268 | 2019: +0.376 | 2020: +0.045 | 2021: +0.279 | 2022: +0.154 | 2023: +0.050 | 2024: +0.350 | 2025: -0.067 | 2026: +0.353
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=1.64
- Early IC=+0.0854, Recent IC=+0.1402, 1st-half IC=+0.1149, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.055, Q3_mid=+0.082, Q4=+0.153, Q5_high_vol=+0.136

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1015, Sharpe=+0.0872)
- Admission: Train IC=+0.2638, Deflated=+0.2625, IR=1.03, Mono=0.84, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.075 | 2017: +0.028 | 2018: +0.075 | 2019: +0.188 | 2020: +0.140 | 2021: +0.149 | 2022: +0.122 | 2023: +0.186 | 2024: +0.110 | 2025: +0.181 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.076 | 2016: +0.172 | 2017: +0.198 | 2018: +0.207 | 2019: +0.338 | 2020: +0.236 | 2021: +0.323 | 2022: +0.282 | 2023: +0.397 | 2024: +0.256 | 2025: +0.197 | 2026: -0.002
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=2.89
- Early IC=+0.0512, Recent IC=+0.1476, 1st-half IC=+0.1056, 2nd-half IC=+0.1471, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.120, Q3_mid=+0.113, Q4=+0.120, Q5_high_vol=+0.153

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0755, Sharpe=+0.0763)
- Admission: Train IC=+0.2190, Deflated=+0.2189, IR=0.83, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.091 | 2017: +0.042 | 2018: +0.115 | 2019: +0.193 | 2020: +0.111 | 2021: +0.135 | 2022: +0.109 | 2023: +0.175 | 2024: +0.079 | 2025: +0.148 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.078 | 2017: +0.118 | 2018: +0.276 | 2019: +0.278 | 2020: +0.141 | 2021: +0.318 | 2022: +0.173 | 2023: +0.525 | 2024: +0.193 | 2025: +0.103 | 2026: -0.182
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.24, Recency ratio=1.61
- Early IC=+0.0786, Recent IC=+0.1267, 1st-half IC=+0.1075, 2nd-half IC=+0.1337, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.091, Q3_mid=+0.112, Q4=+0.124, Q5_high_vol=+0.147

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0948, Sharpe=+0.0510)
- Admission: Train IC=+0.2031, Deflated=+0.2023, IR=0.48, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.164 | 2017: +0.000 | 2018: +0.123 | 2019: +0.160 | 2020: +0.132 | 2021: +0.157 | 2022: +0.124 | 2023: +0.140 | 2024: +0.087 | 2025: +0.109 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.087 | 2016: +0.159 | 2017: +0.088 | 2018: +0.303 | 2019: +0.342 | 2020: +0.042 | 2021: +0.401 | 2022: +0.055 | 2023: +0.173 | 2024: +0.182 | 2025: -0.037 | 2026: +0.052
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.84
- Early IC=+0.0619, Recent IC=+0.1139, 1st-half IC=+0.0991, 2nd-half IC=+0.1350, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.067, Q3_mid=+0.093, Q4=+0.118, Q5_high_vol=+0.174

**`combo_rank_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0930, Sharpe=+0.0368)
- Admission: Train IC=+0.2553, Deflated=+0.2560, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.097 | 2017: +0.024 | 2018: +0.126 | 2019: +0.194 | 2020: +0.112 | 2021: +0.133 | 2022: +0.103 | 2023: +0.174 | 2024: +0.071 | 2025: +0.164 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.342 | 2016: -0.030 | 2017: +0.140 | 2018: +0.196 | 2019: +0.482 | 2020: +0.137 | 2021: +0.288 | 2022: +0.129 | 2023: +0.502 | 2024: +0.185 | 2025: +0.246 | 2026: +0.149
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.61
- Early IC=+0.0758, Recent IC=+0.1222, 1st-half IC=+0.1106, 2nd-half IC=+0.1254, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.110, Q3_mid=+0.099, Q4=+0.101, Q5_high_vol=+0.140

**`combo_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1120, Sharpe=+0.0365)
- Admission: Train IC=+0.1891, Deflated=+0.1883, IR=0.56, Mono=0.70, p=0.0004, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.127 | 2017: +0.024 | 2018: +0.140 | 2019: +0.124 | 2020: +0.105 | 2021: +0.157 | 2022: +0.142 | 2023: +0.117 | 2024: +0.062 | 2025: +0.129 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.028 | 2016: +0.045 | 2017: +0.212 | 2018: +0.393 | 2019: +0.142 | 2020: +0.120 | 2021: +0.405 | 2022: +0.072 | 2023: +0.190 | 2024: +0.194 | 2025: +0.146 | 2026: +0.093
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=1.09
- Early IC=+0.0820, Recent IC=+0.0898, 1st-half IC=+0.1007, 2nd-half IC=+0.1262, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.106, Q3_mid=+0.072, Q4=+0.108, Q5_high_vol=+0.161

**`combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max`** (Lock IC=+0.1340, Sharpe=+0.0219)
- Admission: Train IC=+0.2537, Deflated=+0.2521, IR=0.68, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.069 | 2017: +0.039 | 2018: +0.120 | 2019: +0.198 | 2020: +0.100 | 2021: +0.196 | 2022: +0.067 | 2023: +0.087 | 2024: +0.081 | 2025: +0.176 | 2026: +0.090
- Yearly Tail ICs:   2015: -0.033 | 2016: +0.099 | 2017: +0.092 | 2018: +0.221 | 2019: +0.515 | 2020: +0.037 | 2021: +0.356 | 2022: +0.215 | 2023: +0.199 | 2024: +0.325 | 2025: -0.024 | 2026: +0.017
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.05
- Early IC=+0.0797, Recent IC=+0.0840, 1st-half IC=+0.1187, 2nd-half IC=+0.1183, Neg regimes=0/5
- Weak component: `rally_strength_max` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.061, Q3_mid=+0.142, Q4=+0.168, Q5_high_vol=+0.159

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0841, Sharpe=+0.0197)
- Admission: Train IC=+0.1865, Deflated=+0.1852, IR=0.55, Mono=0.69, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.071 | 2017: +0.034 | 2018: +0.079 | 2019: +0.133 | 2020: +0.100 | 2021: +0.173 | 2022: +0.146 | 2023: +0.147 | 2024: +0.088 | 2025: +0.141 | 2026: +0.031
- Yearly Tail ICs:   2015: -0.132 | 2016: +0.164 | 2017: +0.032 | 2018: +0.270 | 2019: +0.227 | 2020: -0.010 | 2021: +0.389 | 2022: +0.200 | 2023: +0.232 | 2024: +0.216 | 2025: +0.013 | 2026: -0.081
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=1.72, Recency ratio=2.07
- Early IC=+0.0569, Recent IC=+0.1176, 1st-half IC=+0.0853, 2nd-half IC=+0.1467, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.088, Q3_mid=+0.098, Q4=+0.103, Q5_high_vol=+0.170

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.1109 | +0.0129 | +0.0129 | 1y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | fast | +0.1091 | -0.1852 | -0.1852 | 1y |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.1049 | -0.2082 | -0.2082 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position` | FP | fast | +0.1037 | -0.1580 | -0.1580 | 1y |
| `combo_max__bar_ret_0__morning_volume_weighted_momentum` | FP | fast | +0.1011 | -0.1980 | -0.1980 | 1y |
| `combo_tri_mean__bar_ret_0__bar_body_rng_0__volume_weighted_price_position` | Median | fast | +0.0981 | -0.1072 | -0.1072 | 1y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0962 | +0.0468 | +0.0468 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | fast | +0.0958 | -0.0206 | -0.0206 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0945 | +0.0032 | +0.0032 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position` | FP | fast | +0.0942 | -0.1429 | -0.1429 | 1y |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | TP | persistent | +0.0907 | +0.0022 | +0.0022 | 1y |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.0859 | -0.1751 | -0.1751 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__first_bar_return` | Median | fast | +0.0816 | -0.0708 | -0.0708 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Median | fast | +0.0790 | -0.0293 | -0.0293 | 1y |
| `combo_max__max_up_ret__bar_ret_0` | FP | fast | +0.0776 | -0.1601 | -0.1601 | 1y |
| `combo_rank_max__max_up_ret__first_bar_return` | FP | fast | +0.0764 | -0.1597 | -0.1597 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__bar_body_rng_0` | Median | fast | +0.0717 | -0.0530 | -0.0530 | 1y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position` | FP | fast | +0.0699 | -0.0987 | -0.0987 | 1y |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | fast | +0.0687 | -0.1392 | -0.1392 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__rbreaker_buy_setup_proximity_early` | TP | fast | +0.0677 | -0.0659 | -0.0659 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | FP | fast | +0.0666 | -0.1119 | -0.1119 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0652 | +0.0466 | +0.0466 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | FP | fast | +0.0617 | -0.0775 | -0.0775 | 1y |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | FP | fast | +0.0569 | -0.1658 | -0.1658 | 1y |
| `combo_mean__max_up_ret__bar_body_rng_0` | FP | fast | +0.0539 | -0.1137 | -0.1137 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | fast | +0.0527 | -0.0140 | -0.0140 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | FP | fast | +0.0501 | -0.1296 | -0.1296 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Median | fast | +0.0500 | -0.0513 | -0.0513 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Median | fast | +0.0486 | -0.0535 | -0.0535 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration` | FP | fast | +0.0468 | -0.1664 | -0.1664 | 1y |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | FP | fast | +0.0438 | -0.1087 | -0.1087 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | fast | +0.0436 | -0.0364 | -0.0364 | 1y |
| `max_up_ret` | FP | fast | +0.0327 | -0.1524 | -0.1524 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | FP | fast | +0.0317 | -0.0714 | -0.0714 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | FP | fast | +0.0216 | -0.0774 | -0.0774 | 1y |

**Decay distribution**: immediate=0, fast(1-2y)=30, gradual=0, persistent=5

**FP decay trajectories:**

- `combo_min__max_up_ret__bar_body_rng_0`: Y1:+0.022 → Y2:-0.077
- `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Y1:+0.032 → Y2:-0.071
- `max_up_ret`: Y1:+0.033 → Y2:-0.152
- `combo_ratio__first_bar_return__volume_weighted_price_position`: Y1:+0.044 → Y2:-0.109
- `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__volume_concentration`: Y1:+0.047 → Y2:-0.166
- `combo_sig_product__opening_drive_thrust_ratio__max_up_ret`: Y1:+0.050 → Y2:-0.130
- `combo_mean__max_up_ret__bar_body_rng_0`: Y1:+0.054 → Y2:-0.114
- `combo_mean__opening_drive_thrust_ratio__max_up_ret`: Y1:+0.057 → Y2:-0.166
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`: Y1:+0.062 → Y2:-0.078
- `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`: Y1:+0.067 → Y2:-0.112
- `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.069 → Y2:-0.139
- `combo_tri_min__max_up_ret__bar_body_rng_0__volume_weighted_price_position`: Y1:+0.070 → Y2:-0.099
- `combo_rank_max__max_up_ret__first_bar_return`: Y1:+0.076 → Y2:-0.160
- `combo_max__max_up_ret__bar_ret_0`: Y1:+0.078 → Y2:-0.160
- `combo_rank_max__bar_ret_0__volume_weighted_price_position`: Y1:+0.086 → Y2:-0.175
- `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__volume_weighted_price_position`: Y1:+0.094 → Y2:-0.143
- `combo_max__bar_ret_0__morning_volume_weighted_momentum`: Y1:+0.101 → Y2:-0.198
- `combo_tri_mean__opening_drive_thrust_ratio__first_bar_return__volume_weighted_price_position`: Y1:+0.104 → Y2:-0.158
- `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`: Y1:+0.105 → Y2:-0.208
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:+0.109 → Y2:-0.185

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rel_diff__bar_ret_0__demark_setup_reversal_early` | Median | persistent | +0.1558 | +0.0511 | +0.0511 | 1y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | Median | persistent | +0.1530 | +0.0454 | +0.0454 | 1y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__trend_day_regime_conviction` | Median | fast | +0.1513 | -0.0486 | -0.0486 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | Median | fast | +0.1509 | -0.0229 | -0.0229 | 1y |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | Median | persistent | +0.1495 | +0.0426 | +0.0426 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__net_volume_flow__bar_ret_0` | TP | persistent | +0.1481 | +0.0872 | +0.0872 | ∞ |
| `combo_tri_median__early_body_momentum__star50_limit_proximity_early__bar_ret_0` | Median | fast | +0.1442 | -0.0058 | -0.0058 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.1422 | +0.0512 | +0.0512 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1416 | +0.0781 | +0.0781 | ∞ |
| `combo_min__net_volume_flow__close_vs_open_range` | Median | fast | +0.1403 | -0.0664 | -0.0664 | 1y |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1362 | +0.0869 | +0.0869 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1349 | +0.0959 | +0.0959 | ∞ |
| `combo_rank_min__net_volume_flow__vwap_close_divergence_trend` | TP | fast | +0.1335 | -0.0683 | -0.0683 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | fast | +0.1333 | -0.0066 | -0.0066 | 1y |
| `combo_mean__bar_ret_0__vwap_close_divergence_trend` | Median | fast | +0.1329 | -0.0680 | -0.0680 | 1y |
| `combo_max__first_bar_return__vwap_close_divergence_trend` | Median | fast | +0.1323 | -0.1097 | -0.1097 | 1y |
| `combo_mean__first_bar_return__max_down_ret` | TP | persistent | +0.1320 | +0.0123 | +0.0123 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__early_body_momentum` | TP | persistent | +0.1312 | +0.0350 | +0.0350 | 1y |
| `combo_rank_max__bar_ret_0__vwap_close_divergence_trend` | Median | fast | +0.1293 | -0.1070 | -0.1070 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Median | persistent | +0.1282 | +0.0596 | +0.0596 | 1y |
| `combo_tri_min__max_up_ret__net_volume_flow__bar_ret_0` | Median | fast | +0.1281 | -0.0079 | -0.0079 | 1y |
| `combo_sig_product__trend_day_regime_conviction__vwap_close_divergence_trend` | Median | fast | +0.1275 | -0.0850 | -0.0850 | 1y |
| `combo_tri_max__volatility_expansion_trend_vector__early_body_momentum__bar_ret_0` | Median | fast | +0.1270 | -0.1123 | -0.1123 | 1y |
| `combo_tri_mean__trend_bar_close_consistency__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.1264 | +0.0207 | +0.0207 | 1y |
| `combo_mean__max_up_ret__vwap_close_divergence_trend` | Median | fast | +0.1254 | -0.0747 | -0.0747 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Median | fast | +0.1251 | -0.0396 | -0.0396 | 1y |
| `combo_tri_mean__early_body_momentum__trend_day_regime_conviction__bar_ret_0` | Median | fast | +0.1247 | -0.0773 | -0.0773 | 1y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | fast | +0.1239 | -0.1216 | -0.1216 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Median | fast | +0.1225 | -0.0013 | -0.0013 | 1y |
| `combo_sig_product__trend_bar_close_consistency__vwap_close_divergence_trend` | Median | fast | +0.1219 | -0.1128 | -0.1128 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Median | fast | +0.1217 | -0.0555 | -0.0555 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1216 | +0.0449 | +0.0449 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1204 | +0.0855 | +0.0855 | ∞ |
| `combo_mean__bar_ret_0__close_vs_open_range` | Median | fast | +0.1198 | -0.0391 | -0.0391 | 1y |
| `combo_rank_max__bar_ret_0__close_vs_open_range` | Median | fast | +0.1194 | -0.0961 | -0.0961 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | fast | +0.1192 | -0.0517 | -0.0517 | 1y |
| `combo_min__net_volume_flow__bar_body_rng_0` | Median | persistent | +0.1187 | +0.0012 | +0.0012 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.1187 | +0.0821 | +0.0821 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1186 | +0.1006 | +0.1006 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Median | persistent | +0.1179 | +0.0511 | +0.0511 | 1y |
| `num_up_bars` | Median | fast | +0.1166 | -0.0474 | -0.0474 | 1y |
| `combo_mean__first_bar_return__shaved_bar_trend_conviction` | Median | fast | +0.1163 | -0.0502 | -0.0502 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector__star50_limit_proximity_early` | Median | persistent | +0.1158 | +0.0713 | +0.0713 | ∞ |
| `combo_mean__max_up_ret__close_vs_open_range` | Median | fast | +0.1150 | -0.0716 | -0.0716 | 1y |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.1130 | +0.1000 | +0.1000 | ∞ |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1121 | -0.0266 | -0.0266 | 1y |
| `combo_rank_max__max_up_ret__max_down_ret` | Median | fast | +0.1116 | -0.0046 | -0.0046 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.1100 | +0.0760 | +0.0760 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__bar_body_rng_0` | TP | persistent | +0.1100 | +0.0075 | +0.0075 | 1y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | Median | persistent | +0.1094 | +0.0492 | +0.0492 | 1y |
| `combo_tri_min__max_up_ret__volatility_expansion_trend_vector__star50_limit_proximity_early` | TP | persistent | +0.1081 | +0.0802 | +0.0802 | ∞ |
| `combo_tri_max__max_up_ret__early_body_momentum__bar_ret_0` | Median | fast | +0.1066 | -0.0877 | -0.0877 | 1y |
| `combo_tri_mean__max_up_ret__early_body_momentum__bar_ret_0` | Median | fast | +0.1065 | -0.0584 | -0.0584 | 1y |
| `combo_mean__max_up_ret__max_down_ret` | Median | fast | +0.1058 | -0.0156 | -0.0156 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Median | fast | +0.1057 | -0.0442 | -0.0442 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Median | persistent | +0.1046 | +0.0619 | +0.0619 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | persistent | +0.1026 | +0.0811 | +0.0811 | ∞ |
| `combo_min__first_bar_return__early_order_flow_imbalance` | Median | fast | +0.1015 | -0.0324 | -0.0324 | 1y |
| `combo_max__bar_ret_0__max_down_ret` | Median | persistent | +0.1008 | +0.0047 | +0.0047 | 1y |
| `combo_rank_max__max_up_ret__net_volume_flow` | Median | fast | +0.1008 | -0.0170 | -0.0170 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Median | fast | +0.0993 | -0.0636 | -0.0636 | 1y |
| `combo_rank_max__max_up_ret__bar_ret_0` | Median | fast | +0.0977 | -0.0663 | -0.0663 | 1y |
| `combo_mean__max_up_ret__bar_body_rng_0` | Median | fast | +0.0972 | -0.0342 | -0.0342 | 1y |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0971 | +0.1049 | +0.1049 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.0971 | -0.0103 | -0.0103 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.0965 | +0.0098 | +0.0098 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_ret_0` | Median | persistent | +0.0962 | +0.0162 | +0.0162 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.0944 | +0.0858 | +0.0858 | ∞ |
| `combo_mean__first_bar_return__bar_body_rng_0` | Median | fast | +0.0942 | -0.0032 | -0.0032 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector__bar_ret_0` | Median | fast | +0.0941 | -0.0505 | -0.0505 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | Median | fast | +0.0941 | -0.0044 | -0.0044 | 1y |
| `combo_max__max_up_ret__max_down_ret` | Median | fast | +0.0930 | -0.0322 | -0.0322 | 1y |
| `combo_max__max_up_ret__vwap_close_divergence_trend` | Median | fast | +0.0921 | -0.0653 | -0.0653 | 1y |
| `combo_rank_max__max_up_ret__vwap_close_divergence_trend` | Median | fast | +0.0913 | -0.0531 | -0.0531 | 1y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Median | fast | +0.0890 | -0.0006 | -0.0006 | 1y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0888 | +0.1751 | +0.1751 | ∞ |
| `combo_mean__bar_ret_0__early_order_flow_imbalance` | Median | fast | +0.0883 | -0.0681 | -0.0681 | 1y |
| `combo_min__early_order_flow_imbalance__bar_body_rng_0` | Median | fast | +0.0868 | -0.0459 | -0.0459 | 1y |
| `combo_diff__max_up_ret__h2_l2_pullback_continuation` | Median | fast | +0.0858 | -0.0869 | -0.0869 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0` | Median | persistent | +0.0856 | +0.0551 | +0.0551 | ∞ |
| `combo_max__max_up_ret__close_vs_open_range` | Median | fast | +0.0823 | -0.0425 | -0.0425 | 1y |
| `max_up_ret` | Median | fast | +0.0801 | -0.0291 | -0.0291 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.0795 | -0.0153 | -0.0153 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__early_body_momentum` | Median | fast | +0.0784 | -0.0473 | -0.0473 | 1y |
| `combo_sig_product__net_volume_flow__vwap_close_divergence_trend` | FP | fast | +0.0783 | -0.1221 | -0.1221 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | Median | fast | +0.0777 | -0.0005 | -0.0005 | 1y |
| `combo_mean__max_up_ret__first_bar_return` | Median | fast | +0.0772 | -0.0329 | -0.0329 | 1y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0685 | +0.0220 | +0.0220 | 1y |
| `combo_sig_product__bar_ret_0__vwap_close_divergence_trend` | FP | fast | +0.0674 | -0.1036 | -0.1036 | 1y |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0634 | +0.1849 | +0.1849 | ∞ |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0602 | +0.1848 | +0.1848 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0601 | -0.0041 | -0.0041 | 1y |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0578 | +0.1809 | +0.1809 | ∞ |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0567 | +0.0084 | +0.0084 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__bar_ret_0` | Median | persistent | +0.0514 | +0.0104 | +0.0104 | 1y |
| `combo_clamp_diff__first_bar_return__body_size_progression` | TP | persistent | +0.0335 | +0.0977 | +0.0977 | ∞ |
| `combo_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0206 | +0.0793 | +0.0793 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0186 | +0.2613 | +0.2613 | ∞ |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0159 | +0.2573 | +0.2573 | ∞ |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Median | persistent | +0.0156 | +0.0876 | +0.0876 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=56, gradual=0, persistent=44

**FP decay trajectories:**

- `combo_sig_product__bar_ret_0__vwap_close_divergence_trend`: Y1:+0.067 → Y2:-0.104
- `combo_sig_product__net_volume_flow__vwap_close_divergence_trend`: Y1:+0.078 → Y2:-0.122

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.2153 | +0.0608 | +0.0608 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.2114 | +0.0678 | +0.0678 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.2067 | +0.0594 | +0.0594 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.2054 | +0.0334 | +0.0334 | 1y |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | Median | fast | +0.2047 | -0.0797 | -0.0797 | 1y |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Median | fast | +0.2015 | -0.0871 | -0.0871 | 1y |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | TP | fast | +0.1962 | -0.0369 | -0.0369 | 1y |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1936 | +0.0433 | +0.0433 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1927 | +0.0637 | +0.0637 | 1y |
| `combo_ifelse__gap_pct__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1925 | +0.0824 | +0.0824 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__rally_strength_max` | Median | persistent | +0.1922 | +0.0532 | +0.0532 | 1y |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | fast | +0.1908 | -0.0067 | -0.0067 | 1y |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1888 | -0.0980 | -0.0980 | 1y |
| `combo_max__max_up_ret__rally_strength_max` | Median | fast | +0.1860 | -0.0914 | -0.0914 | 1y |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Median | fast | +0.1854 | -0.0560 | -0.0560 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | fast | +0.1843 | -0.0180 | -0.0180 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1826 | +0.0526 | +0.0526 | 1y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Median | fast | +0.1819 | -0.0040 | -0.0040 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | fast | +0.1813 | -0.0105 | -0.0105 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1798 | +0.0536 | +0.0536 | 1y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1777 | -0.0708 | -0.0708 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1776 | +0.0306 | +0.0306 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1770 | -0.0804 | -0.0804 | 1y |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1769 | +0.0816 | +0.0816 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.1758 | +0.0900 | +0.0900 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1750 | +0.1164 | +0.1164 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1746 | -0.0705 | -0.0705 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1746 | +0.0674 | +0.0674 | 1y |
| `combo_ifelse__gap_pct__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1740 | +0.1067 | +0.1067 | ∞ |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1737 | +0.0897 | +0.0897 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1730 | +0.0733 | +0.0733 | 1y |
| `combo_mean__max_up_ret__bar_body_rng_0` | Median | fast | +0.1729 | -0.0304 | -0.0304 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1725 | -0.0618 | -0.0618 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1720 | +0.1097 | +0.1097 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Median | fast | +0.1719 | -0.0696 | -0.0696 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | TP | fast | +0.1717 | -0.0766 | -0.0766 | 1y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1714 | +0.0415 | +0.0415 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rally_strength_max` | Median | fast | +0.1705 | -0.0816 | -0.0816 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1704 | +0.0712 | +0.0712 | 1y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1696 | +0.1445 | +0.1445 | ∞ |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.1690 | +0.1012 | +0.1012 | ∞ |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1664 | +0.0547 | +0.0547 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.1637 | +0.0055 | +0.0055 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1635 | +0.0711 | +0.0711 | 1y |
| `combo_rank_min__max_up_ret__rally_strength_max` | Median | fast | +0.1633 | -0.0671 | -0.0671 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1632 | +0.0999 | +0.0999 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1623 | +0.1019 | +0.1019 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Median | fast | +0.1623 | -0.0243 | -0.0243 | 1y |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1612 | +0.0821 | +0.0821 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1608 | +0.1238 | +0.1238 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1594 | +0.0841 | +0.0841 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1590 | +0.0858 | +0.0858 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1576 | +0.0989 | +0.0989 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1564 | +0.1047 | +0.1047 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1558 | +0.1234 | +0.1234 | ∞ |
| `combo_max__volatility_expansion_trend_vector__volume_price_confirmation` | TP | fast | +0.1556 | -0.0197 | -0.0197 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.1555 | +0.0958 | +0.0958 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Median | fast | +0.1545 | -0.0273 | -0.0273 | 1y |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | TP | persistent | +0.1543 | +0.1126 | +0.1126 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__bar_ret_0` | TP | persistent | +0.1536 | +0.0157 | +0.0157 | 1y |
| `combo_min__bar_ret_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1536 | +0.1220 | +0.1220 | ∞ |
| `combo_min__bar_ret_0__limit_down_proximity_early` | TP | persistent | +0.1536 | +0.1220 | +0.1220 | ∞ |
| `combo_diff__max_up_ret__keltner_squeeze_width` | TP | fast | +0.1535 | -0.0612 | -0.0612 | 1y |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__gap_pct` | TP | fast | +0.1531 | -0.0925 | -0.0925 | 1y |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1526 | +0.0972 | +0.0972 | ∞ |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1523 | +0.1450 | +0.1450 | ∞ |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1523 | +0.1450 | +0.1450 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1496 | +0.1086 | +0.1086 | ∞ |
| `combo_rel_diff__max_up_ret__keltner_squeeze_width` | TP | fast | +0.1490 | -0.0142 | -0.0142 | 1y |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | fast | +0.1483 | -0.0151 | -0.0151 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | Median | persistent | +0.1469 | +0.0273 | +0.0273 | 1y |
| `combo_clamp_diff__max_up_ret__keltner_squeeze_width` | TP | fast | +0.1461 | -0.0619 | -0.0619 | 1y |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1438 | +0.1172 | +0.1172 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1433 | +0.1123 | +0.1123 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1425 | +0.1075 | +0.1075 | ∞ |
| `combo_mean__volume_weighted_price_position__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1411 | +0.1206 | +0.1206 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1411 | +0.0306 | +0.0306 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1407 | +0.1104 | +0.1104 | ∞ |
| `combo_ifelse__gap_pct__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | persistent | +0.1403 | +0.0359 | +0.0359 | 1y |
| `combo_ratio__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1393 | -0.0681 | -0.0681 | 1y |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Median | persistent | +0.1393 | +0.0156 | +0.0156 | 1y |
| `combo_min__max_up_ret__gap_pct` | TP | persistent | +0.1359 | +0.1042 | +0.1042 | ∞ |
| `combo_min__max_up_ret__bar_ret_0` | TP | persistent | +0.1356 | +0.0296 | +0.0296 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__demark_setup_reversal_early` | Median | fast | +0.1350 | -0.0680 | -0.0680 | 1y |
| `combo_rank_min__volume_weighted_price_position__limit_down_proximity_early` | TP | persistent | +0.1347 | +0.1375 | +0.1375 | ∞ |
| `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1346 | +0.1338 | +0.1338 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1339 | +0.1144 | +0.1144 | ∞ |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | fast | +0.1339 | -0.0039 | -0.0039 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1336 | +0.0869 | +0.0869 | ∞ |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.1325 | +0.0600 | +0.0600 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__rally_strength_max` | TP | persistent | +0.1313 | +0.0979 | +0.0979 | ∞ |
| `combo_max__max_up_ret__volume_price_confirmation` | Median | fast | +0.1313 | -0.0251 | -0.0251 | 1y |
| `combo_rank_min__max_up_ret__gap_pct` | TP | persistent | +0.1295 | +0.0975 | +0.0975 | ∞ |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1287 | +0.1090 | +0.1090 | ∞ |
| `combo_ratio__max_up_ret__keltner_squeeze_width` | Median | fast | +0.1274 | -0.0851 | -0.0851 | 1y |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1256 | +0.0991 | +0.0991 | ∞ |
| `combo_mean__max_up_ret__volume_price_confirmation` | TP | persistent | +0.1256 | +0.0373 | +0.0373 | 1y |
| `combo_rank_max__max_up_ret__volume_price_confirmation` | TP | fast | +0.1252 | -0.0063 | -0.0063 | 1y |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1247 | +0.1472 | +0.1472 | ∞ |
| `combo_min__volume_weighted_price_position__limit_down_proximity_early` | TP | persistent | +0.1240 | +0.1313 | +0.1313 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1227 | -0.0816 | -0.0816 | 1y |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1224 | +0.1374 | +0.1374 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.1217 | +0.1355 | +0.1355 | ∞ |
| `combo_tri_median__demark_setup_reversal_early__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1183 | +0.0799 | +0.0799 | ∞ |
| `combo_rank_min__rbreaker_buy_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1175 | +0.1773 | +0.1773 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volume_price_confirmation` | TP | persistent | +0.1175 | +0.1773 | +0.1773 | ∞ |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.1143 | +0.0098 | +0.0098 | 1y |
| `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_trend` | TP | persistent | +0.1133 | +0.1526 | +0.1526 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1092 | +0.0987 | +0.0987 | ∞ |
| `combo_min__star50_limit_proximity_early__volume_price_confirmation` | TP | persistent | +0.1059 | +0.1890 | +0.1890 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.1053 | +0.2016 | +0.2016 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_price_confirmation` | TP | persistent | +0.1048 | +0.1824 | +0.1824 | ∞ |
| `combo_ifelse__gap_pct__yesterday_early_momentum__star50_limit_proximity_early` | TP | persistent | +0.1045 | +0.1277 | +0.1277 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1012 | +0.1304 | +0.1304 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.0904 | +0.2104 | +0.2104 | ∞ |
| `combo_rel_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | TP | persistent | +0.0892 | +0.1862 | +0.1862 | ∞ |
| `combo_clamp_diff__volume_weighted_price_position__body_size_progression` | TP | persistent | +0.0869 | +0.0359 | +0.0359 | 1y |
| `combo_rank_max__star50_limit_proximity_early__volume_price_confirmation` | TP | persistent | +0.0860 | +0.1855 | +0.1855 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__directional_volume_signature` | TP | persistent | +0.0856 | +0.2166 | +0.2166 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.0804 | +0.1430 | +0.1430 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev` | TP | persistent | +0.0758 | +0.1169 | +0.1169 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__demark_setup_reversal_early__star50_limit_proximity_early` | TP | persistent | +0.0742 | +0.1016 | +0.1016 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__body_size_progression` | TP | persistent | +0.0717 | +0.2082 | +0.2082 | ∞ |
| `combo_min__bar_ret_0__directional_volume_signature` | Median | persistent | +0.0593 | +0.0801 | +0.0801 | ∞ |
| `combo_diff__rbreaker_sell_setup_proximity_early__late_bar_momentum` | TP | persistent | +0.0566 | +0.2179 | +0.2179 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=34, gradual=0, persistent=91

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.750±0.028 | 0.734±0.041 | 75% | WEAK |
| ic_ir | 0.707±0.081 | 0.600±0.094 | 40% | USEFUL |
| p_value | 0.000±0.000 | 0.000±0.000 | 100% | USELESS |
| max_corr | 0.901±0.059 | 0.901±0.029 | 29% | USEFUL |
| deflated_ic | 0.223±0.022 | 0.220±0.012 | 35% | USEFUL |
| overall_ic | 0.222±0.022 | 0.221±0.012 | 35% | USEFUL |
| raw_ic | 0.089±0.007 | 0.093±0.005 | 45% | USEFUL |

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.727±0.015 | 0.749±0.041 | 20% | USEFUL |
| ic_ir | 0.638±0.025 | 0.721±0.139 | 9% | USEFUL |
| p_value | 0.001±0.001 | 0.000±0.000 | 10% | USEFUL |
| max_corr | 0.809±0.095 | 0.892±0.075 | 56% | WEAK |
| deflated_ic | 0.174±0.015 | 0.232±0.022 | 8% | USEFUL |
| overall_ic | 0.175±0.015 | 0.233±0.022 | 7% | USEFUL |
| raw_ic | 0.109±0.007 | 0.124±0.013 | 30% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 11/20 top rejects are profitable (55%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Sharpe=+0.7428
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Sharpe=+0.7428
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449

**B2 Rolling Guard**: 6/20 top rejects are profitable (30%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__volume_surge_max`: Train IC=+0.1522, Lock IC=+0.0969, Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0962, Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0962, Sharpe=+0.8491

**BH-FDR Gate**: 1/5 top rejects are profitable (20%)

- `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0989, Lock IC=+0.0348, Sharpe=+0.1297

**B6 Yearly IC CV Gate**: 1/20 top rejects are profitable (5%)

- `combo_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1799, Lock IC=+0.0344, Sharpe=+0.1334

**B4 Correlation Gate**: 6/20 top rejects are profitable (30%)

- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783

### 500ETF — `single`

**7-Year Jackknife**: 10/20 top rejects are profitable (50%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Sharpe=+0.5717
- `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__star50_limit_proximity_early`: Train IC=+0.2198, Lock IC=+0.0912, Sharpe=+0.3360
- `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`: Train IC=+0.2237, Lock IC=+0.0991, Sharpe=+0.2685

**B2 Rolling Guard**: 6/20 top rejects are profitable (30%)

- `combo_mean__trend_day_regime_conviction__shaved_bar_trend_conviction`: Train IC=+0.2190, Lock IC=+0.0431, Sharpe=+0.2228
- `combo_z_sum__trend_day_regime_conviction__shaved_bar_trend_conviction`: Train IC=+0.2190, Lock IC=+0.0431, Sharpe=+0.2228
- `combo_mean__rsi_opening__shaved_bar_trend_conviction`: Train IC=+0.2181, Lock IC=+0.0458, Sharpe=+0.2228

**Temporal Validation Gate**: 1/20 top rejects are profitable (5%)

- `combo_clamp_diff__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.2743, Lock IC=+0.0624, Sharpe=+0.6830

**B3 Composite Floor**: 1/20 top rejects are profitable (5%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector__volume_weighted_momentum_acceleration`: Train IC=+0.1847, Lock IC=+0.0017, Sharpe=+0.3201

**B6 Yearly IC CV Gate**: 6/15 top rejects are profitable (40%)

- `combo_tri_min__smooth_momentum_structure__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1680, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352

**B6 Quality Gate**: 1/2 top rejects are profitable (50%)

- `combo_sig_product__vwap_close_divergence_trend__bar_body_rng_0`: Train IC=+0.1551, Lock IC=+0.0402, Sharpe=+0.1882

**B4 Correlation Gate**: 3/20 top rejects are profitable (15%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Sharpe=+0.3545
- `combo_tri_min__max_up_ret__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2645, Lock IC=+0.0855, Sharpe=+0.2823
- `combo_tri_min__max_up_ret__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2645, Lock IC=+0.0855, Sharpe=+0.2823

### 159915ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_mean__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Sharpe=+1.9220
- `combo_z_sum__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Sharpe=+1.9220
- `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Sharpe=+1.9220

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_mean__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2191, Lock IC=+0.1315, Sharpe=+1.7919
- `combo_z_sum__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2191, Lock IC=+0.1315, Sharpe=+1.7919
- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676

**Temporal Validation Gate**: 14/20 top rejects are profitable (70%)

- `combo_diff__volume_weighted_momentum_acceleration__limit_down_proximity_early`: Train IC=+0.2245, Lock IC=+0.1154, Sharpe=+0.8601
- `combo_z_diff__volume_weighted_momentum_acceleration__limit_down_proximity_early`: Train IC=+0.2245, Lock IC=+0.1154, Sharpe=+0.8601
- `combo_diff__volume_weighted_momentum_acceleration__rbreaker_buy_setup_proximity_early`: Train IC=+0.2245, Lock IC=+0.1154, Sharpe=+0.8601

**B3 Composite Floor**: 18/20 top rejects are profitable (90%)

- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2238, Lock IC=+0.1147, Sharpe=+1.4941
- `combo_tri_min__star50_limit_proximity_early__yesterday_first_30min_return__yesterday_early_vwap_dev`: Train IC=+0.2460, Lock IC=+0.1133, Sharpe=+0.8865
- `combo_rank_min__limit_down_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2349, Lock IC=+0.1410, Sharpe=+0.7550

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Sharpe=+1.7816
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1160 | 78 | 25 | 29 | 24 | 32% | 31% |
| B2 Rolling Guard | 121 | 78 | 36 | 27 | 15 | 46% | 19% |
| Temporal Validation Gate | 183 | 78 | 32 | 34 | 12 | 41% | 15% |
| BH-FDR Gate | 5 | 5 | 0 | 4 | 1 | 0% | 20% |
| B6 Yearly IC CV Gate | 57 | 57 | 41 | 8 | 8 | 72% | 14% |
| B4 Correlation Gate | 67 | 67 | 31 | 21 | 15 | 46% | 22% |

**7-Year Jackknife** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0002, Lock IC=+0.0825, Sharpe=+0.8131
- `combo_z_diff__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0002, Lock IC=+0.0825, Sharpe=+0.8131
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0570, Sharpe=+0.7428

**B4 Correlation Gate** — top TP casualties:
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2034, Lock IC=+0.0592, Sharpe=+0.5373
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 2516 | 78 | 29 | 27 | 22 | 37% | 28% |
| B2 Rolling Guard | 301 | 78 | 22 | 46 | 10 | 28% | 13% |
| Temporal Validation Gate | 233 | 78 | 24 | 41 | 13 | 31% | 17% |
| BH-FDR Gate | 3 | 3 | 1 | 2 | 0 | 33% | 0% |
| B3 Composite Floor | 56 | 56 | 7 | 27 | 22 | 12% | 39% |
| B6 Yearly IC CV Gate | 15 | 15 | 6 | 3 | 6 | 40% | 40% |
| B6 Temporal Stability Gate | 78 | 78 | 0 | 78 | 0 | 0% | 0% |
| B6 Quality Gate | 2 | 2 | 1 | 0 | 1 | 50% | 50% |
| B4 Correlation Gate | 474 | 78 | 2 | 60 | 16 | 3% | 21% |

**7-Year Jackknife** — top TP casualties:
- `combo_diff__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.0515, Lock IC=+0.0315, Sharpe=+1.1013
- `combo_z_diff__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.0515, Lock IC=+0.0315, Sharpe=+1.1013
- `combo_min__smooth_momentum_structure__bar_body_rng_0`: Train IC=+0.0513, Lock IC=+0.0503, Sharpe=+0.9850

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443
- `combo_tri_mean__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__volatility_expansion_trend_vector__star50_limit_proximity_early`: Train IC=+0.1680, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352

**B6 Quality Gate** — top TP casualties:
- `combo_sig_product__vwap_close_divergence_trend__bar_body_rng_0`: Train IC=+0.1551, Lock IC=+0.0402, Sharpe=+0.1882

**B4 Correlation Gate** — top TP casualties:
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1928, Lock IC=+0.1080, Sharpe=+0.9445
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1928, Lock IC=+0.1080, Sharpe=+0.9445
- `combo_tri_min__rbreaker_sell_setup_proximity_early__early_body_momentum__bar_ret_0`: Train IC=+0.2361, Lock IC=+0.1162, Sharpe=+0.7793

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1962 | 78 | 35 | 14 | 29 | 45% | 37% |
| B2 Rolling Guard | 280 | 78 | 23 | 10 | 45 | 29% | 58% |
| Temporal Validation Gate | 108 | 78 | 6 | 29 | 43 | 8% | 55% |
| BH-FDR Gate | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B3 Composite Floor | 121 | 78 | 1 | 25 | 52 | 1% | 67% |
| B6 Yearly IC CV Gate | 1 | 1 | 0 | 1 | 0 | 0% | 0% |
| B4 Correlation Gate | 252 | 78 | 0 | 16 | 62 | 0% | 79% |

**7-Year Jackknife** — top TP casualties:
- `combo_mean__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Sharpe=+1.9220
- `combo_z_sum__limit_down_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Sharpe=+1.9220
- `combo_mean__rbreaker_buy_setup_proximity_early__volume_price_confirmation`: Train IC=+0.1989, Lock IC=+0.1220, Sharpe=+1.9220

**B2 Rolling Guard** — top TP casualties:
- `combo_mean__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2191, Lock IC=+0.1315, Sharpe=+1.7919
- `combo_z_sum__star50_limit_proximity_early__volume_price_confirmation`: Train IC=+0.2191, Lock IC=+0.1315, Sharpe=+1.7919
- `combo_mean__limit_down_proximity_early__directional_volume_signature`: Train IC=+0.1969, Lock IC=+0.1239, Sharpe=+1.6676

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1734, Lock IC=+0.1528, Sharpe=+1.7449
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1734, Lock IC=+0.1528, Sharpe=+1.7449
- `combo_clamp_diff__demark_setup_reversal_early__directional_volume_signature`: Train IC=+0.1940, Lock IC=+0.1285, Sharpe=+1.1921

**B3 Composite Floor** — top TP casualties:
- `combo_min__opening_drive_thrust_ratio__directional_volume_signature`: Train IC=+0.1546, Lock IC=+0.0958, Sharpe=+1.6636
- `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`: Train IC=+0.2238, Lock IC=+0.1147, Sharpe=+1.4941
- `combo_rank_min__volatility_expansion_trend_vector__volume_price_confirmation`: Train IC=+0.1838, Lock IC=+0.1082, Sharpe=+1.0951

**B4 Correlation Gate** — top TP casualties:
- `combo_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3282, Lock IC=+0.1307, Sharpe=+1.7816
- `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.2387, Lock IC=+0.1195, Sharpe=+1.6332
- `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (183 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 103 | 50 | 20 | 0 | 30 | 40% | 0% |
| recency_ratio >= 2.5 (late-concentrated) | 58 | 50 | 27 | 5 | 18 | 54% | 10% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__rbreaker_sell_setup_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1676, Lock IC=+0.0458, Sharpe=+0.7885
- `combo_rank_min__star50_limit_proximity_early__morning_volume_weighted_momentum`: Train IC=+0.1378, Lock IC=+0.0455, Sharpe=+0.7415
- `combo_min__volume_weighted_price_position__morning_volume_weighted_momentum`: Train IC=+0.1447, Lock IC=+0.0138, Sharpe=+0.4244
- `combo_rank_min__volume_weighted_price_position__morning_volume_weighted_momentum`: Train IC=+0.1446, Lock IC=+0.0147, Sharpe=+0.2971
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2054, Lock IC=+0.0315, Sharpe=+0.0608

### 500ETF — `single` (233 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 212 | 50 | 0 | 8 | 42 | 0% | 16% |
| recency_ratio >= 2.5 (late-concentrated) | 21 | 21 | 6 | 0 | 15 | 29% | 0% |

### 159915ETF — `single` (108 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 74 | 50 | 0 | 36 | 14 | 0% | 72% |
| recency_ratio >= 2.5 (late-concentrated) | 20 | 20 | 0 | 12 | 8 | 0% | 60% |

**Top TP killed by recency_ratio cap:**
- `combo_mean__max_up_ret__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.0973, Sharpe=+0.6215
- `combo_z_sum__max_up_ret__directional_volume_signature`: Train IC=+0.1947, Lock IC=+0.0973, Sharpe=+0.6215
- `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1344, Lock IC=+0.1171, Sharpe=+0.5989
- `combo_max__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1344, Lock IC=+0.1171, Sharpe=+0.5989
- `vwap_slope_intraday`: Train IC=+0.0934, Lock IC=+0.0337, Sharpe=+0.2590

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `weak_link_cv`: FP is lower (d=-1.83). Threshold 0.935 → 78% accuracy.
- `half_ratio`: FP is higher (d=+1.78). Threshold 1.087 → 92% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-1.47). Threshold 0.035 → 79% accuracy.
- `recency_ratio`: FP is higher (d=+0.59). Threshold 0.654 → 92% accuracy.
- `n_negative_regimes`: FP is lower (d=-0.58). Threshold 0.000 → 79% accuracy.
- `ic_cv`: FP is higher (d=+0.54). Threshold 0.630 → 79% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/20
- Decaying signal (half ratio < 0.3): 0/20
- Weak component (CV > 2.0): 0/20
- Regime-dependent (≥2 negative regimes): 0/20

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `recency_ratio`: FP is higher (d=+1.73). Threshold 0.772 → 92% accuracy.
- `n_negative_regimes`: FP is lower (d=-1.41). Threshold 1.000 → 88% accuracy.
- `half_ratio`: FP is higher (d=+1.19). Threshold 0.950 → 88% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-1.18). Threshold 0.092 → 88% accuracy.
- `weak_link_cv`: FP is lower (d=-0.98). Threshold 0.547 → 88% accuracy.
- `ic_cv`: FP is lower (d=-0.79). Threshold 0.509 → 88% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/2
- Decaying signal (half ratio < 0.3): 0/2
- Weak component (CV > 2.0): 0/2
- Regime-dependent (≥2 negative regimes): 0/2

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `vwap_close_divergence_trend` | 2 | 1 | 3 | 67% |  |
| `volume_weighted_price_position` | 8 | 10 | 18 | 44% |  |
| `max_up_ret` | 15 | 25 | 40 | 38% |  |
| `bar_ret_0` | 6 | 15 | 21 | 29% |  |
| `net_volume_flow` | 1 | 3 | 4 | 25% |  |
| `first_bar_return` | 4 | 12 | 16 | 25% |  |
| `opening_drive_thrust_ratio` | 7 | 27 | 34 | 21% |  |
| `bar_body_rng_0` | 3 | 20 | 23 | 13% |  |
| `rbreaker_sell_setup_proximity_early` | 3 | 52 | 55 | 5% |  |
| `demark_setup_reversal_early` | 0 | 6 | 6 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 9 | 9 | 0% |  |
| `max_down_ret` | 0 | 2 | 2 | 0% |  |
| `gap_pct` | 0 | 6 | 6 | 0% |  |
| `keltner_squeeze_width` | 0 | 3 | 3 | 0% |  |
| `volume_price_confirmation` | 0 | 8 | 8 | 0% |  |
| `star50_limit_proximity_early` | 0 | 32 | 32 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 8 | 8 | 0% |  |
| `rally_strength_max` | 0 | 3 | 3 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 2 | 2 | 0% |  |
| `body_size_progression` | 0 | 7 | 7 | 0% |  |
| `yesterday_first_30min_return` | 0 | 3 | 3 | 0% |  |
| `limit_down_proximity_early` | 0 | 8 | 8 | 0% |  |
| `directional_volume_signature` | 0 | 3 | 3 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 12 | 12 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=8, TP=64, FP rate=11%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=1, TP=23, FP rate=4%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=9, TP=29, FP rate=24%

