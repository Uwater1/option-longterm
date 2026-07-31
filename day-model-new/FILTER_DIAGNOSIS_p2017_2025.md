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
| 300ETF | single | 125 | 41 | `[8, 7, 6, 5, 5, 5, 4, 3, 2, 2, 2, 2, ... (41 clusters)]` | 0.2737 | 58 | 58 | 9 | 46% | 0.13 |
| 500ETF | single | 206 | 47 | `[12, 10, 9, 8, 8, 8, 7, 7, 6, 6, 5, 5, ... (47 clusters)]` | 0.2603 | 3 | 147 | 56 | 1% | 0.43 |
| 159915ETF | single | 183 | 48 | `[12, 12, 10, 9, 7, 6, 5, 5, 5, 4, 4, 3, ... (48 clusters)]` | 0.2140 | 1 | 52 | 130 | 1% | 0.67 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 300ETF — `single` (FP=58, TP=9)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| weak_link_cv | 1.110 | 1.663 | 1.104 | 1.209 | -1.24 | 0.930 | 84% |
| ic_std_across_regimes | 0.053 | 0.070 | 0.054 | 0.064 | -1.19 | 0.031 | 85% |
| half_ratio | 1.828 | 1.184 | 1.551 | 1.044 | +0.93 | 1.067 | 90% |
| n_negative_regimes | 0.155 | 0.333 | 0.000 | 0.000 | -0.42 | 0.000 | 85% |
| n_negative_years | 0.828 | 0.778 | 1.000 | 1.000 | +0.09 | 0.000 | 85% |
| ic_cv | 0.877 | 0.868 | 0.869 | 0.863 | +0.07 | 0.648 | 85% |
| recency_ratio | 1.074 | 1.048 | 1.241 | 0.845 | +0.02 | -6.449 | 85% |

### 500ETF — `single` (FP=3, TP=56)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| half_ratio | 1.740 | 0.649 | 1.908 | 0.627 | +5.29 | 1.204 | 98% |
| ic_std_across_regimes | 0.024 | 0.067 | 0.025 | 0.068 | -4.09 | 0.091 | 93% |
| recency_ratio | 1.088 | 0.555 | 1.129 | 0.502 | +3.19 | 0.941 | 98% |
| n_negative_regimes | 0.000 | 0.536 | 0.000 | 1.000 | -1.52 | 1.000 | 93% |
| ic_cv | 0.373 | 0.427 | 0.379 | 0.409 | -0.66 | 0.736 | 93% |
| n_negative_years | 0.000 | 0.071 | 0.000 | 0.000 | -0.39 | 1.000 | 93% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 300ETF — `single` False Positives

**`combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=-0.0374, Sharpe=-2.5227)
- Admission: Train IC=+0.1738, Deflated=+0.1743, IR=0.60, Mono=0.73, p=0.0010, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.087 | 2017: -0.034 | 2018: +0.174 | 2019: +0.091 | 2020: +0.046 | 2021: +0.165 | 2022: +0.025 | 2023: +0.157 | 2024: +0.033 | 2025: +0.055 | 2026: -0.184
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.226 | 2017: +0.015 | 2018: +0.309 | 2019: +0.111 | 2020: +0.093 | 2021: +0.431 | 2022: +0.175 | 2023: +0.139 | 2024: +0.161 | 2025: -0.073 | 2026: -0.389
- IC CV=0.88, Neg years (linear/tail)=1/0 of 8, Half ratio=1.47, Recency ratio=1.36
- Early IC=+0.0699, Recent IC=+0.0947, 1st-half IC=+0.0716, 2nd-half IC=+0.1049, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=-0.010, Q2=+0.086, Q3_mid=+0.044, Q4=+0.063, Q5_high_vol=+0.219

**`combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0410, Sharpe=-2.2126)
- Admission: Train IC=+0.1875, Deflated=+0.1876, IR=0.50, Mono=0.71, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.057 | 2016: +0.052 | 2017: -0.027 | 2018: +0.102 | 2019: +0.056 | 2020: +0.046 | 2021: +0.160 | 2022: +0.011 | 2023: +0.158 | 2024: +0.059 | 2025: +0.044 | 2026: -0.164
- Yearly Tail ICs:   2015: +0.032 | 2016: +0.090 | 2017: +0.075 | 2018: +0.116 | 2019: +0.125 | 2020: +0.158 | 2021: +0.286 | 2022: +0.176 | 2023: +0.303 | 2024: +0.238 | 2025: -0.120 | 2026: -0.264
- IC CV=0.88, Neg years (linear/tail)=1/0 of 8, Half ratio=2.77, Recency ratio=2.89
- Early IC=+0.0376, Recent IC=+0.1086, 1st-half IC=+0.0380, 2nd-half IC=+0.1053, Neg regimes=1/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.059, Q3_mid=-0.001, Q4=+0.071, Q5_high_vol=+0.177

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0136, Sharpe=-1.9227)
- Admission: Train IC=+0.2100, Deflated=+0.2102, IR=0.71, Mono=0.75, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.181 | 2016: -0.115 | 2017: +0.115 | 2018: +0.283 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.250 | 2024: +0.186 | 2025: +0.049 | 2026: -0.303
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.68
- Early IC=+0.1311, Recent IC=+0.0894, 1st-half IC=+0.0926, 2nd-half IC=+0.0859, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.091, Q3_mid=+0.051, Q4=+0.072, Q5_high_vol=+0.160

**`combo_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0136, Sharpe=-1.9227)
- Admission: Train IC=+0.2095, Deflated=+0.2097, IR=0.71, Mono=0.75, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.115 | 2017: +0.115 | 2018: +0.285 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.249 | 2024: +0.186 | 2025: +0.049 | 2026: -0.298
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.68
- Early IC=+0.1311, Recent IC=+0.0894, 1st-half IC=+0.0925, 2nd-half IC=+0.0860, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.074, Q2=+0.091, Q3_mid=+0.051, Q4=+0.072, Q5_high_vol=+0.160

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0315, Sharpe=-1.8589)
- Admission: Train IC=+0.2232, Deflated=+0.2229, IR=0.66, Mono=0.73, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.053 | 2017: +0.009 | 2018: +0.176 | 2019: +0.100 | 2020: +0.034 | 2021: +0.182 | 2022: +0.022 | 2023: +0.151 | 2024: +0.031 | 2025: +0.038 | 2026: -0.133
- Yearly Tail ICs:   2015: +0.068 | 2016: +0.078 | 2017: -0.049 | 2018: +0.295 | 2019: +0.226 | 2020: +0.110 | 2021: +0.414 | 2022: +0.280 | 2023: +0.336 | 2024: +0.222 | 2025: -0.031 | 2026: -0.303
- IC CV=0.78, Neg years (linear/tail)=0/1 of 8, Half ratio=1.36, Recency ratio=0.99
- Early IC=+0.0923, Recent IC=+0.0913, 1st-half IC=+0.0778, 2nd-half IC=+0.1057, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.108, Q3_mid=+0.034, Q4=+0.056, Q5_high_vol=+0.188

**`max_up_ret`** (Lock IC=-0.0463, Sharpe=-1.8589)
- Admission: Train IC=+0.2051, Deflated=+0.2056, IR=0.62, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.084 | 2017: -0.040 | 2018: +0.136 | 2019: +0.049 | 2020: +0.048 | 2021: +0.166 | 2022: +0.013 | 2023: +0.149 | 2024: +0.056 | 2025: +0.033 | 2026: -0.152
- Yearly Tail ICs:   2015: +0.070 | 2016: +0.035 | 2017: +0.015 | 2018: +0.265 | 2019: +0.208 | 2020: +0.110 | 2021: +0.462 | 2022: +0.221 | 2023: +0.279 | 2024: +0.213 | 2025: -0.013 | 2026: -0.315
- IC CV=0.94, Neg years (linear/tail)=1/0 of 8, Half ratio=2.29, Recency ratio=2.13
- Early IC=+0.0481, Recent IC=+0.1023, 1st-half IC=+0.0452, 2nd-half IC=+0.1036, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.064, Q3_mid=+0.014, Q4=+0.050, Q5_high_vol=+0.186

**`combo_sig_product__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0333, Sharpe=-1.7361)
- Admission: Train IC=+0.1663, Deflated=+0.1665, IR=0.54, Mono=0.70, p=0.0014, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.044 | 2016: +0.089 | 2017: -0.048 | 2018: +0.111 | 2019: +0.118 | 2020: +0.041 | 2021: +0.134 | 2022: -0.033 | 2023: +0.157 | 2024: +0.047 | 2025: +0.019 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.023 | 2016: +0.141 | 2017: -0.097 | 2018: +0.317 | 2019: +0.220 | 2020: +0.117 | 2021: +0.389 | 2022: +0.159 | 2023: +0.259 | 2024: +0.080 | 2025: -0.034 | 2026: -0.040
- IC CV=1.09, Neg years (linear/tail)=2/1 of 8, Half ratio=1.81, Recency ratio=3.23
- Early IC=+0.0315, Recent IC=+0.1018, 1st-half IC=+0.0483, 2nd-half IC=+0.0873, Neg regimes=1/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.075, Q3_mid=-0.003, Q4=+0.070, Q5_high_vol=+0.171

**`combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0061, Sharpe=-1.6781)
- Admission: Train IC=+0.2384, Deflated=+0.2392, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.066 | 2017: -0.010 | 2018: +0.230 | 2019: +0.070 | 2020: +0.021 | 2021: +0.179 | 2022: +0.034 | 2023: +0.162 | 2024: +0.011 | 2025: +0.094 | 2026: -0.143
- Yearly Tail ICs:   2015: +0.014 | 2016: +0.099 | 2017: +0.167 | 2018: +0.271 | 2019: +0.324 | 2020: +0.182 | 2021: +0.426 | 2022: +0.281 | 2023: +0.376 | 2024: -0.055 | 2025: -0.049 | 2026: -0.194
- IC CV=0.97, Neg years (linear/tail)=1/1 of 8, Half ratio=1.37, Recency ratio=0.79
- Early IC=+0.1102, Recent IC=+0.0866, 1st-half IC=+0.0770, 2nd-half IC=+0.1057, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.102, Q3_mid=+0.061, Q4=+0.072, Q5_high_vol=+0.161

**`combo_mean__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0365, Sharpe=-1.6583)
- Admission: Train IC=+0.2523, Deflated=+0.2529, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.080 | 2017: -0.034 | 2018: +0.160 | 2019: +0.072 | 2020: +0.053 | 2021: +0.175 | 2022: +0.015 | 2023: +0.160 | 2024: +0.064 | 2025: +0.057 | 2026: -0.166
- Yearly Tail ICs:   2015: -0.023 | 2016: +0.177 | 2017: +0.157 | 2018: +0.341 | 2019: +0.358 | 2020: +0.125 | 2021: +0.374 | 2022: +0.208 | 2023: +0.245 | 2024: +0.290 | 2025: -0.131 | 2026: -0.344
- IC CV=0.85, Neg years (linear/tail)=1/0 of 8, Half ratio=1.81, Recency ratio=1.78
- Early IC=+0.0627, Recent IC=+0.1118, 1st-half IC=+0.0615, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.085, Q3_mid=+0.028, Q4=+0.054, Q5_high_vol=+0.212

**`combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0`** (Lock IC=-0.0546, Sharpe=-1.5992)
- Admission: Train IC=+0.1770, Deflated=+0.1774, IR=0.40, Mono=0.68, p=0.0008, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.080 | 2016: +0.084 | 2017: -0.008 | 2018: +0.077 | 2019: +0.055 | 2020: +0.020 | 2021: +0.162 | 2022: +0.029 | 2023: +0.170 | 2024: +0.020 | 2025: -0.000 | 2026: -0.132
- Yearly Tail ICs:   2015: +0.130 | 2016: -0.070 | 2017: -0.074 | 2018: +0.131 | 2019: +0.181 | 2020: +0.127 | 2021: +0.381 | 2022: +0.238 | 2023: +0.268 | 2024: +0.095 | 2025: +0.007 | 2026: -0.229
- IC CV=0.96, Neg years (linear/tail)=1/1 of 8, Half ratio=3.10, Recency ratio=2.72
- Early IC=+0.0347, Recent IC=+0.0946, 1st-half IC=+0.0320, 2nd-half IC=+0.0992, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.052, Q3_mid=+0.019, Q4=+0.063, Q5_high_vol=+0.123

**`combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`** (Lock IC=-0.0133, Sharpe=-1.5530)
- Admission: Train IC=+0.1264, Deflated=+0.1276, IR=0.47, Mono=0.66, p=0.0124, MaxCorr=0.58
- Yearly Linear ICs: 2015: -0.054 | 2016: -0.023 | 2017: +0.030 | 2018: +0.101 | 2019: +0.077 | 2020: +0.028 | 2021: +0.092 | 2022: +0.022 | 2023: +0.061 | 2024: +0.004 | 2025: +0.026 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.076 | 2016: -0.017 | 2017: +0.226 | 2018: +0.164 | 2019: +0.162 | 2020: +0.060 | 2021: +0.230 | 2022: +0.050 | 2023: +0.158 | 2024: +0.013 | 2025: +0.050 | 2026: -0.255
- IC CV=0.65, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.49
- Early IC=+0.0653, Recent IC=+0.0321, 1st-half IC=+0.0610, 2nd-half IC=+0.0457, Neg regimes=1/5
- Weak component: `double_bottom_bull_flag_early` (CV=1.91, neg years=2)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.038, Q3_mid=+0.053, Q4=+0.111, Q5_high_vol=-0.008

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0157, Sharpe=-1.4403)
- Admission: Train IC=+0.2163, Deflated=+0.2166, IR=0.69, Mono=0.73, p=0.0002, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.096 | 2017: +0.025 | 2018: +0.190 | 2019: +0.080 | 2020: +0.016 | 2021: +0.173 | 2022: +0.029 | 2023: +0.173 | 2024: +0.061 | 2025: +0.054 | 2026: -0.114
- Yearly Tail ICs:   2015: +0.028 | 2016: +0.135 | 2017: +0.078 | 2018: +0.299 | 2019: +0.165 | 2020: +0.051 | 2021: +0.304 | 2022: +0.247 | 2023: +0.406 | 2024: +0.179 | 2025: -0.004 | 2026: -0.080
- IC CV=0.74, Neg years (linear/tail)=0/0 of 8, Half ratio=1.48, Recency ratio=1.09
- Early IC=+0.1077, Recent IC=+0.1173, 1st-half IC=+0.0774, 2nd-half IC=+0.1145, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.087, Q3_mid=+0.043, Q4=+0.061, Q5_high_vol=+0.205

**`combo_rel_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=-0.0338, Sharpe=-1.4374)
- Admission: Train IC=+0.1362, Deflated=+0.1369, IR=0.57, Mono=0.72, p=0.0064, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.085 | 2016: +0.074 | 2017: +0.016 | 2018: +0.185 | 2019: +0.039 | 2020: +0.032 | 2021: +0.150 | 2022: +0.005 | 2023: +0.175 | 2024: +0.109 | 2025: +0.015 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.085 | 2016: +0.103 | 2017: +0.229 | 2018: +0.312 | 2019: +0.168 | 2020: +0.014 | 2021: +0.172 | 2022: +0.069 | 2023: +0.224 | 2024: +0.074 | 2025: -0.086 | 2026: -0.109
- IC CV=0.78, Neg years (linear/tail)=0/0 of 8, Half ratio=1.70, Recency ratio=1.41
- Early IC=+0.1005, Recent IC=+0.1420, 1st-half IC=+0.0654, 2nd-half IC=+0.1111, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.080, Q3_mid=+0.060, Q4=+0.026, Q5_high_vol=+0.183

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0282, Sharpe=-1.4181)
- Admission: Train IC=+0.1766, Deflated=+0.1782, IR=0.58, Mono=0.71, p=0.0008, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.036 | 2016: +0.044 | 2017: -0.041 | 2018: +0.138 | 2019: +0.113 | 2020: +0.035 | 2021: +0.173 | 2022: +0.000 | 2023: +0.187 | 2024: +0.024 | 2025: +0.021 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.184 | 2016: +0.167 | 2017: -0.046 | 2018: +0.281 | 2019: +0.266 | 2020: +0.067 | 2021: +0.444 | 2022: +0.210 | 2023: +0.243 | 2024: +0.123 | 2025: -0.059 | 2026: +0.099
- IC CV=1.01, Neg years (linear/tail)=1/1 of 8, Half ratio=1.66, Recency ratio=2.18
- Early IC=+0.0482, Recent IC=+0.1053, 1st-half IC=+0.0638, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.003, Q2=+0.170, Q3_mid=+0.051, Q4=+0.115, Q5_high_vol=+0.065

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0346, Sharpe=-1.3884)
- Admission: Train IC=+0.2324, Deflated=+0.2332, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.038 | 2017: +0.040 | 2018: +0.151 | 2019: +0.039 | 2020: +0.015 | 2021: +0.189 | 2022: +0.041 | 2023: +0.200 | 2024: +0.042 | 2025: +0.105 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.162 | 2017: +0.196 | 2018: +0.484 | 2019: +0.257 | 2020: +0.182 | 2021: +0.316 | 2022: +0.224 | 2023: +0.183 | 2024: +0.127 | 2025: +0.146 | 2026: -0.463
- IC CV=0.80, Neg years (linear/tail)=0/0 of 8, Half ratio=2.24, Recency ratio=1.26
- Early IC=+0.0957, Recent IC=+0.1210, 1st-half IC=+0.0548, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.082, Q2=+0.116, Q3_mid=+0.040, Q4=+0.035, Q5_high_vol=+0.185

**`combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0344, Sharpe=-1.3884)
- Admission: Train IC=+0.2318, Deflated=+0.2326, IR=0.82, Mono=0.80, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.038 | 2017: +0.041 | 2018: +0.151 | 2019: +0.039 | 2020: +0.015 | 2021: +0.189 | 2022: +0.041 | 2023: +0.200 | 2024: +0.042 | 2025: +0.105 | 2026: -0.208
- Yearly Tail ICs:   2015: +0.138 | 2016: +0.160 | 2017: +0.196 | 2018: +0.484 | 2019: +0.257 | 2020: +0.182 | 2021: +0.316 | 2022: +0.224 | 2023: +0.183 | 2024: +0.129 | 2025: +0.146 | 2026: -0.463
- IC CV=0.80, Neg years (linear/tail)=0/0 of 8, Half ratio=2.24, Recency ratio=1.26
- Early IC=+0.0959, Recent IC=+0.1209, 1st-half IC=+0.0548, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.116, Q3_mid=+0.040, Q4=+0.035, Q5_high_vol=+0.185

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=-0.0223, Sharpe=-1.3571)
- Admission: Train IC=+0.2655, Deflated=+0.2657, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.109 | 2016: +0.091 | 2017: +0.020 | 2018: +0.182 | 2019: +0.073 | 2020: -0.000 | 2021: +0.133 | 2022: +0.045 | 2023: +0.170 | 2024: +0.055 | 2025: +0.022 | 2026: -0.077
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.099 | 2017: +0.153 | 2018: +0.375 | 2019: +0.259 | 2020: +0.087 | 2021: +0.371 | 2022: +0.168 | 2023: +0.386 | 2024: +0.231 | 2025: -0.048 | 2026: -0.016
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.46, Recency ratio=1.12
- Early IC=+0.1009, Recent IC=+0.1127, 1st-half IC=+0.0718, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.079, Q3_mid=+0.041, Q4=+0.072, Q5_high_vol=+0.177

**`combo_rank_max__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0153, Sharpe=-1.3143)
- Admission: Train IC=+0.1886, Deflated=+0.1891, IR=0.51, Mono=0.73, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.086 | 2017: -0.046 | 2018: +0.125 | 2019: +0.050 | 2020: +0.040 | 2021: +0.174 | 2022: +0.018 | 2023: +0.171 | 2024: +0.046 | 2025: +0.077 | 2026: -0.148
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.068 | 2017: -0.092 | 2018: +0.289 | 2019: +0.241 | 2020: +0.096 | 2021: +0.371 | 2022: +0.246 | 2023: +0.229 | 2024: +0.159 | 2025: +0.084 | 2026: -0.332
- IC CV=1.01, Neg years (linear/tail)=1/1 of 8, Half ratio=2.75, Recency ratio=2.74
- Early IC=+0.0398, Recent IC=+0.1087, 1st-half IC=+0.0404, 2nd-half IC=+0.1113, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.008, Q2=+0.084, Q3_mid=+0.010, Q4=+0.046, Q5_high_vol=+0.199

**`combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=-0.0022, Sharpe=-1.3090)
- Admission: Train IC=+0.2499, Deflated=+0.2501, IR=0.67, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.084 | 2017: +0.039 | 2018: +0.222 | 2019: +0.068 | 2020: -0.023 | 2021: +0.147 | 2022: +0.065 | 2023: +0.177 | 2024: +0.018 | 2025: +0.070 | 2026: -0.099
- Yearly Tail ICs:   2015: +0.041 | 2016: -0.023 | 2017: +0.223 | 2018: +0.299 | 2019: +0.295 | 2020: +0.057 | 2021: +0.441 | 2022: +0.309 | 2023: +0.375 | 2024: +0.061 | 2025: -0.061 | 2026: -0.163
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.36, Recency ratio=0.75
- Early IC=+0.1305, Recent IC=+0.0974, 1st-half IC=+0.0789, 2nd-half IC=+0.1075, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.098, Q3_mid=+0.062, Q4=+0.075, Q5_high_vol=+0.151

**`combo_rank_max__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0123, Sharpe=-1.3041)
- Admission: Train IC=+0.2005, Deflated=+0.2011, IR=0.47, Mono=0.72, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.091 | 2017: +0.001 | 2018: +0.189 | 2019: +0.081 | 2020: +0.043 | 2021: +0.179 | 2022: +0.023 | 2023: +0.193 | 2024: +0.037 | 2025: +0.074 | 2026: -0.141
- Yearly Tail ICs:   2015: +0.050 | 2016: -0.025 | 2017: -0.077 | 2018: +0.407 | 2019: +0.159 | 2020: +0.149 | 2021: +0.402 | 2022: +0.157 | 2023: +0.275 | 2024: +0.121 | 2025: +0.156 | 2026: -0.301
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.35, Recency ratio=1.21
- Early IC=+0.0947, Recent IC=+0.1150, 1st-half IC=+0.0837, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.93, neg years=1)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.103, Q3_mid=+0.068, Q4=+0.065, Q5_high_vol=+0.201

**`combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0176, Sharpe=-1.2814)
- Admission: Train IC=+0.2013, Deflated=+0.2020, IR=0.61, Mono=0.74, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.095 | 2017: -0.036 | 2018: +0.201 | 2019: +0.103 | 2020: +0.048 | 2021: +0.137 | 2022: +0.044 | 2023: +0.144 | 2024: +0.046 | 2025: +0.044 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.012 | 2017: +0.035 | 2018: +0.120 | 2019: +0.237 | 2020: +0.137 | 2021: +0.246 | 2022: +0.318 | 2023: +0.256 | 2024: +0.250 | 2025: +0.043 | 2026: -0.016
- IC CV=0.82, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=1.15
- Early IC=+0.0822, Recent IC=+0.0949, 1st-half IC=+0.0856, 2nd-half IC=+0.0997, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.085, Q3_mid=+0.043, Q4=+0.062, Q5_high_vol=+0.214

**`combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0176, Sharpe=-1.2814)
- Admission: Train IC=+0.2012, Deflated=+0.2019, IR=0.62, Mono=0.74, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.095 | 2017: -0.036 | 2018: +0.201 | 2019: +0.104 | 2020: +0.048 | 2021: +0.137 | 2022: +0.045 | 2023: +0.144 | 2024: +0.046 | 2025: +0.044 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.012 | 2017: +0.035 | 2018: +0.120 | 2019: +0.238 | 2020: +0.137 | 2021: +0.246 | 2022: +0.318 | 2023: +0.256 | 2024: +0.250 | 2025: +0.043 | 2026: -0.016
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=1.15
- Early IC=+0.0823, Recent IC=+0.0948, 1st-half IC=+0.0857, 2nd-half IC=+0.0997, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.085, Q3_mid=+0.043, Q4=+0.062, Q5_high_vol=+0.214

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=-0.0225, Sharpe=-1.2669)
- Admission: Train IC=+0.2147, Deflated=+0.2148, IR=0.75, Mono=0.76, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.075 | 2017: +0.049 | 2018: +0.172 | 2019: +0.060 | 2020: +0.030 | 2021: +0.175 | 2022: +0.012 | 2023: +0.162 | 2024: +0.060 | 2025: +0.078 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.078 | 2016: +0.097 | 2017: +0.040 | 2018: +0.355 | 2019: +0.236 | 2020: +0.128 | 2021: +0.394 | 2022: +0.254 | 2023: +0.299 | 2024: +0.125 | 2025: +0.044 | 2026: -0.321
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=1.00
- Early IC=+0.1106, Recent IC=+0.1109, 1st-half IC=+0.0691, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.085, Q3_mid=+0.038, Q4=+0.053, Q5_high_vol=+0.190

**`combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0163, Sharpe=-1.2450)
- Admission: Train IC=+0.2335, Deflated=+0.2339, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.069 | 2017: +0.029 | 2018: +0.197 | 2019: +0.064 | 2020: +0.003 | 2021: +0.165 | 2022: +0.050 | 2023: +0.179 | 2024: +0.046 | 2025: +0.095 | 2026: -0.168
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.070 | 2017: +0.090 | 2018: +0.359 | 2019: +0.146 | 2020: +0.146 | 2021: +0.412 | 2022: +0.277 | 2023: +0.261 | 2024: +0.216 | 2025: +0.056 | 2026: -0.146
- IC CV=0.77, Neg years (linear/tail)=0/0 of 8, Half ratio=1.71, Recency ratio=1.00
- Early IC=+0.1127, Recent IC=+0.1125, 1st-half IC=+0.0695, 2nd-half IC=+0.1188, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.108, Q3_mid=+0.043, Q4=+0.055, Q5_high_vol=+0.191

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0091, Sharpe=-1.2289)
- Admission: Train IC=+0.2119, Deflated=+0.2119, IR=0.68, Mono=0.75, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.080 | 2017: -0.049 | 2018: +0.160 | 2019: +0.085 | 2020: +0.045 | 2021: +0.139 | 2022: +0.031 | 2023: +0.162 | 2024: +0.046 | 2025: +0.067 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.101 | 2016: +0.097 | 2017: +0.043 | 2018: +0.270 | 2019: +0.241 | 2020: +0.095 | 2021: +0.316 | 2022: +0.190 | 2023: +0.271 | 2024: +0.328 | 2025: -0.023 | 2026: -0.233
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.72, Recency ratio=1.87
- Early IC=+0.0558, Recent IC=+0.1042, 1st-half IC=+0.0592, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21, neg years=1)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.069, Q3_mid=+0.027, Q4=+0.037, Q5_high_vol=+0.221

**`combo_min__max_up_ret__bar_ret_0`** (Lock IC=-0.0256, Sharpe=-1.1985)
- Admission: Train IC=+0.1994, Deflated=+0.1999, IR=0.46, Mono=0.73, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.104 | 2017: -0.024 | 2018: +0.172 | 2019: +0.086 | 2020: +0.032 | 2021: +0.114 | 2022: +0.039 | 2023: +0.137 | 2024: +0.044 | 2025: +0.022 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.206 | 2016: -0.099 | 2017: -0.050 | 2018: +0.150 | 2019: +0.217 | 2020: +0.201 | 2021: +0.306 | 2022: +0.301 | 2023: +0.290 | 2024: +0.233 | 2025: +0.043 | 2026: -0.017
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=1.24, Recency ratio=1.22
- Early IC=+0.0740, Recent IC=+0.0901, 1st-half IC=+0.0712, 2nd-half IC=+0.0882, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.018, Q2=+0.069, Q3_mid=+0.032, Q4=+0.067, Q5_high_vol=+0.177

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=-0.0223, Sharpe=-1.1680)
- Admission: Train IC=+0.2309, Deflated=+0.2312, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.087 | 2017: +0.035 | 2018: +0.169 | 2019: +0.060 | 2020: +0.041 | 2021: +0.170 | 2022: +0.015 | 2023: +0.166 | 2024: +0.060 | 2025: +0.078 | 2026: -0.157
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.033 | 2017: +0.026 | 2018: +0.412 | 2019: +0.206 | 2020: +0.193 | 2021: +0.360 | 2022: +0.306 | 2023: +0.290 | 2024: +0.141 | 2025: +0.095 | 2026: -0.308
- IC CV=0.69, Neg years (linear/tail)=0/0 of 8, Half ratio=1.62, Recency ratio=1.14
- Early IC=+0.1001, Recent IC=+0.1142, 1st-half IC=+0.0683, 2nd-half IC=+0.1108, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.066, Q2=+0.083, Q3_mid=+0.041, Q4=+0.057, Q5_high_vol=+0.195

**`combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0217, Sharpe=-1.1078)
- Admission: Train IC=+0.2033, Deflated=+0.2039, IR=0.78, Mono=0.80, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.068 | 2017: -0.025 | 2018: +0.120 | 2019: +0.049 | 2020: +0.021 | 2021: +0.175 | 2022: +0.048 | 2023: +0.195 | 2024: +0.031 | 2025: +0.106 | 2026: -0.195
- Yearly Tail ICs:   2015: +0.114 | 2016: +0.226 | 2017: +0.189 | 2018: +0.318 | 2019: +0.122 | 2020: +0.076 | 2021: +0.298 | 2022: +0.217 | 2023: +0.209 | 2024: +0.189 | 2025: +0.178 | 2026: -0.352
- IC CV=0.95, Neg years (linear/tail)=1/0 of 8, Half ratio=2.87, Recency ratio=2.38
- Early IC=+0.0475, Recent IC=+0.1129, 1st-half IC=+0.0420, 2nd-half IC=+0.1207, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.030, Q2=+0.094, Q3_mid=-0.008, Q4=+0.057, Q5_high_vol=+0.202

**`combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0009, Sharpe=-1.0800)
- Admission: Train IC=+0.2127, Deflated=+0.2132, IR=0.73, Mono=0.78, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.069 | 2017: +0.012 | 2018: +0.217 | 2019: +0.075 | 2020: +0.013 | 2021: +0.153 | 2022: +0.054 | 2023: +0.179 | 2024: +0.021 | 2025: +0.104 | 2026: -0.158
- Yearly Tail ICs:   2015: +0.191 | 2016: -0.042 | 2017: +0.061 | 2018: +0.314 | 2019: +0.172 | 2020: +0.106 | 2021: +0.358 | 2022: +0.254 | 2023: +0.238 | 2024: +0.260 | 2025: +0.140 | 2026: -0.030
- IC CV=0.84, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=0.87
- Early IC=+0.1145, Recent IC=+0.1001, 1st-half IC=+0.0821, 2nd-half IC=+0.1113, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.114, Q3_mid=+0.055, Q4=+0.059, Q5_high_vol=+0.187

**`combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0009, Sharpe=-1.0800)
- Admission: Train IC=+0.2124, Deflated=+0.2130, IR=0.73, Mono=0.78, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.069 | 2017: +0.012 | 2018: +0.217 | 2019: +0.075 | 2020: +0.013 | 2021: +0.153 | 2022: +0.054 | 2023: +0.179 | 2024: +0.021 | 2025: +0.104 | 2026: -0.158
- Yearly Tail ICs:   2015: +0.189 | 2016: -0.042 | 2017: +0.064 | 2018: +0.314 | 2019: +0.173 | 2020: +0.110 | 2021: +0.356 | 2022: +0.256 | 2023: +0.238 | 2024: +0.260 | 2025: +0.140 | 2026: -0.030
- IC CV=0.84, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=0.87
- Early IC=+0.1146, Recent IC=+0.1002, 1st-half IC=+0.0821, 2nd-half IC=+0.1114, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.114, Q3_mid=+0.055, Q4=+0.059, Q5_high_vol=+0.187

**`combo_tri_max__max_up_ret__first_bar_return__bar_body_rng_0`** (Lock IC=-0.0060, Sharpe=-1.0686)
- Admission: Train IC=+0.2170, Deflated=+0.2175, IR=0.68, Mono=0.75, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.101 | 2017: +0.043 | 2018: +0.178 | 2019: +0.066 | 2020: +0.032 | 2021: +0.185 | 2022: +0.008 | 2023: +0.157 | 2024: +0.061 | 2025: +0.090 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.099 | 2017: +0.058 | 2018: +0.347 | 2019: +0.198 | 2020: +0.132 | 2021: +0.394 | 2022: +0.278 | 2023: +0.285 | 2024: +0.122 | 2025: +0.044 | 2026: -0.321
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.35, Recency ratio=0.98
- Early IC=+0.1107, Recent IC=+0.1088, 1st-half IC=+0.0795, 2nd-half IC=+0.1071, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.094, Q3_mid=+0.037, Q4=+0.052, Q5_high_vol=+0.204

**`combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`** (Lock IC=-0.0061, Sharpe=-1.0686)
- Admission: Train IC=+0.2168, Deflated=+0.2173, IR=0.68, Mono=0.75, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.100 | 2017: +0.043 | 2018: +0.178 | 2019: +0.066 | 2020: +0.032 | 2021: +0.185 | 2022: +0.008 | 2023: +0.157 | 2024: +0.061 | 2025: +0.090 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.099 | 2017: +0.058 | 2018: +0.347 | 2019: +0.198 | 2020: +0.131 | 2021: +0.394 | 2022: +0.280 | 2023: +0.281 | 2024: +0.125 | 2025: +0.044 | 2026: -0.321
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.35, Recency ratio=0.98
- Early IC=+0.1107, Recent IC=+0.1087, 1st-half IC=+0.0795, 2nd-half IC=+0.1071, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.094, Q3_mid=+0.037, Q4=+0.052, Q5_high_vol=+0.204

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=-0.0154, Sharpe=-1.0675)
- Admission: Train IC=+0.1756, Deflated=+0.1752, IR=0.54, Mono=0.71, p=0.0008, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.089 | 2016: +0.080 | 2017: -0.019 | 2018: +0.157 | 2019: +0.085 | 2020: +0.033 | 2021: +0.164 | 2022: +0.063 | 2023: +0.137 | 2024: +0.036 | 2025: +0.034 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.160 | 2016: -0.171 | 2017: +0.015 | 2018: +0.271 | 2019: +0.304 | 2020: +0.069 | 2021: +0.400 | 2022: -0.005 | 2023: +0.275 | 2024: +0.176 | 2025: +0.064 | 2026: -0.424
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=1.65, Recency ratio=1.25
- Early IC=+0.0690, Recent IC=+0.0860, 1st-half IC=+0.0648, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.118, Q3_mid=+0.013, Q4=+0.084, Q5_high_vol=+0.151

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0388, Sharpe=-0.9976)
- Admission: Train IC=+0.2042, Deflated=+0.2050, IR=0.89, Mono=0.83, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.95, Neg years (linear/tail)=0/0 of 8, Half ratio=2.70, Recency ratio=1.68
- Early IC=+0.0659, Recent IC=+0.1111, 1st-half IC=+0.0425, 2nd-half IC=+0.1149, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.094, Q3_mid=-0.004, Q4=+0.043, Q5_high_vol=+0.182

**`combo_max__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0209, Sharpe=-0.9725)
- Admission: Train IC=+0.1959, Deflated=+0.1967, IR=0.47, Mono=0.69, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.087 | 2017: -0.012 | 2018: +0.189 | 2019: +0.079 | 2020: +0.049 | 2021: +0.173 | 2022: +0.030 | 2023: +0.193 | 2024: +0.030 | 2025: +0.073 | 2026: -0.150
- Yearly Tail ICs:   2015: +0.105 | 2016: -0.047 | 2017: -0.051 | 2018: +0.334 | 2019: +0.175 | 2020: +0.215 | 2021: +0.348 | 2022: +0.168 | 2023: +0.234 | 2024: +0.160 | 2025: +0.194 | 2026: -0.343
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=1.37, Recency ratio=1.26
- Early IC=+0.0885, Recent IC=+0.1114, 1st-half IC=+0.0827, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.93, neg years=1)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.104, Q3_mid=+0.070, Q4=+0.068, Q5_high_vol=+0.203

**`combo_max__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=-0.0211, Sharpe=-0.9725)
- Admission: Train IC=+0.1959, Deflated=+0.1967, IR=0.47, Mono=0.69, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.087 | 2017: -0.012 | 2018: +0.189 | 2019: +0.079 | 2020: +0.049 | 2021: +0.173 | 2022: +0.030 | 2023: +0.193 | 2024: +0.030 | 2025: +0.073 | 2026: -0.150
- Yearly Tail ICs:   2015: +0.103 | 2016: -0.047 | 2017: -0.051 | 2018: +0.337 | 2019: +0.172 | 2020: +0.215 | 2021: +0.348 | 2022: +0.166 | 2023: +0.237 | 2024: +0.160 | 2025: +0.194 | 2026: -0.343
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=1.37, Recency ratio=1.26
- Early IC=+0.0885, Recent IC=+0.1114, 1st-half IC=+0.0827, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.93, neg years=1)
- Regime ICs: Q1_low_vol=+0.019, Q2=+0.103, Q3_mid=+0.070, Q4=+0.068, Q5_high_vol=+0.203

**`combo_tri_median__max_up_ret__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0152, Sharpe=-0.9549)
- Admission: Train IC=+0.1998, Deflated=+0.1999, IR=0.62, Mono=0.70, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.129 | 2016: +0.082 | 2017: +0.022 | 2018: +0.205 | 2019: +0.063 | 2020: -0.007 | 2021: +0.156 | 2022: +0.033 | 2023: +0.165 | 2024: +0.014 | 2025: +0.069 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.098 | 2016: -0.015 | 2017: +0.085 | 2018: +0.326 | 2019: +0.250 | 2020: +0.165 | 2021: +0.387 | 2022: +0.239 | 2023: +0.252 | 2024: +0.151 | 2025: +0.004 | 2026: -0.221
- IC CV=0.94, Neg years (linear/tail)=1/0 of 8, Half ratio=1.42, Recency ratio=0.79
- Early IC=+0.1137, Recent IC=+0.0894, 1st-half IC=+0.0689, 2nd-half IC=+0.0977, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.090, Q3_mid=+0.010, Q4=+0.074, Q5_high_vol=+0.157

**`combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0151, Sharpe=-0.9549)
- Admission: Train IC=+0.1997, Deflated=+0.1998, IR=0.62, Mono=0.70, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.129 | 2016: +0.082 | 2017: +0.022 | 2018: +0.206 | 2019: +0.063 | 2020: -0.007 | 2021: +0.156 | 2022: +0.033 | 2023: +0.165 | 2024: +0.014 | 2025: +0.069 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.092 | 2016: -0.015 | 2017: +0.085 | 2018: +0.326 | 2019: +0.250 | 2020: +0.165 | 2021: +0.381 | 2022: +0.239 | 2023: +0.252 | 2024: +0.151 | 2025: +0.004 | 2026: -0.221
- IC CV=0.94, Neg years (linear/tail)=1/0 of 8, Half ratio=1.42, Recency ratio=0.79
- Early IC=+0.1137, Recent IC=+0.0895, 1st-half IC=+0.0690, 2nd-half IC=+0.0977, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.090, Q3_mid=+0.010, Q4=+0.074, Q5_high_vol=+0.157

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=-0.0055, Sharpe=-0.8914)
- Admission: Train IC=+0.2709, Deflated=+0.2714, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.093 | 2017: -0.053 | 2018: +0.213 | 2019: +0.115 | 2020: +0.070 | 2021: +0.177 | 2022: +0.016 | 2023: +0.135 | 2024: +0.064 | 2025: +0.032 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.273 | 2016: +0.159 | 2017: +0.041 | 2018: +0.355 | 2019: +0.363 | 2020: +0.165 | 2021: +0.504 | 2022: +0.223 | 2023: +0.109 | 2024: +0.318 | 2025: -0.060 | 2026: +0.071
- IC CV=0.88, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=1.24
- Early IC=+0.0798, Recent IC=+0.0991, 1st-half IC=+0.0929, 2nd-half IC=+0.1080, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21, neg years=1)
- Regime ICs: Q1_low_vol=-0.018, Q2=+0.054, Q3_mid=+0.091, Q4=+0.070, Q5_high_vol=+0.243

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=-0.0261, Sharpe=-0.8875)
- Admission: Train IC=+0.2199, Deflated=+0.2204, IR=0.80, Mono=0.78, p=0.0002, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.114 | 2016: +0.056 | 2017: +0.004 | 2018: +0.173 | 2019: +0.050 | 2020: +0.003 | 2021: +0.181 | 2022: +0.048 | 2023: +0.189 | 2024: +0.031 | 2025: +0.109 | 2026: -0.185
- Yearly Tail ICs:   2015: +0.043 | 2016: +0.201 | 2017: +0.165 | 2018: +0.386 | 2019: +0.181 | 2020: +0.074 | 2021: +0.369 | 2022: +0.343 | 2023: +0.364 | 2024: +0.068 | 2025: +0.041 | 2026: +0.010
- IC CV=0.90, Neg years (linear/tail)=0/0 of 8, Half ratio=2.24, Recency ratio=1.24
- Early IC=+0.0886, Recent IC=+0.1097, 1st-half IC=+0.0540, 2nd-half IC=+0.1210, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.068, Q2=+0.102, Q3_mid=+0.023, Q4=+0.054, Q5_high_vol=+0.177

**`combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0270, Sharpe=-0.8830)
- Admission: Train IC=+0.1693, Deflated=+0.1698, IR=0.55, Mono=0.68, p=0.0012, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.053 | 2016: +0.050 | 2017: +0.038 | 2018: +0.119 | 2019: +0.042 | 2020: -0.056 | 2021: +0.146 | 2022: +0.071 | 2023: +0.180 | 2024: +0.051 | 2025: +0.060 | 2026: -0.150
- Yearly Tail ICs:   2015: -0.100 | 2016: -0.050 | 2017: +0.060 | 2018: +0.217 | 2019: +0.239 | 2020: +0.064 | 2021: +0.379 | 2022: +0.294 | 2023: +0.224 | 2024: +0.058 | 2025: +0.131 | 2026: -0.223
- IC CV=0.93, Neg years (linear/tail)=1/0 of 8, Half ratio=4.13, Recency ratio=1.47
- Early IC=+0.0787, Recent IC=+0.1156, 1st-half IC=+0.0281, 2nd-half IC=+0.1158, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.095, Q3_mid=+0.019, Q4=+0.101, Q5_high_vol=+0.077

**`combo_sig_product__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0323, Sharpe=-0.8613)
- Admission: Train IC=+0.1557, Deflated=+0.1552, IR=0.48, Mono=0.69, p=0.0020, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.037 | 2016: +0.096 | 2017: -0.031 | 2018: +0.153 | 2019: +0.123 | 2020: -0.014 | 2021: +0.152 | 2022: +0.028 | 2023: +0.145 | 2024: +0.027 | 2025: +0.004 | 2026: -0.084
- Yearly Tail ICs:   2015: -0.055 | 2016: +0.135 | 2017: -0.129 | 2018: +0.331 | 2019: +0.253 | 2020: +0.024 | 2021: +0.367 | 2022: +0.174 | 2023: +0.249 | 2024: +0.125 | 2025: +0.079 | 2026: -0.040
- IC CV=1.01, Neg years (linear/tail)=2/1 of 8, Half ratio=1.58, Recency ratio=1.43
- Early IC=+0.0606, Recent IC=+0.0864, 1st-half IC=+0.0599, 2nd-half IC=+0.0944, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.93, neg years=1)
- Regime ICs: Q1_low_vol=+0.053, Q2=+0.103, Q3_mid=+0.015, Q4=+0.083, Q5_high_vol=+0.127

**`combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=-0.0056, Sharpe=-0.8552)
- Admission: Train IC=+0.1731, Deflated=+0.1727, IR=0.56, Mono=0.73, p=0.0010, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.096 | 2016: +0.108 | 2017: -0.034 | 2018: +0.191 | 2019: +0.109 | 2020: +0.020 | 2021: +0.166 | 2022: +0.044 | 2023: +0.166 | 2024: +0.005 | 2025: +0.071 | 2026: -0.123
- Yearly Tail ICs:   2015: -0.007 | 2016: +0.140 | 2017: -0.092 | 2018: +0.343 | 2019: +0.246 | 2020: +0.113 | 2021: +0.389 | 2022: +0.182 | 2023: +0.259 | 2024: +0.120 | 2025: +0.091 | 2026: -0.040
- IC CV=0.96, Neg years (linear/tail)=1/1 of 8, Half ratio=1.38, Recency ratio=1.09
- Early IC=+0.0783, Recent IC=+0.0854, 1st-half IC=+0.0757, 2nd-half IC=+0.1042, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=1.06, neg years=2)
- Regime ICs: Q1_low_vol=+0.012, Q2=+0.112, Q3_mid=+0.038, Q4=+0.078, Q5_high_vol=+0.183

**`combo_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=-0.0284, Sharpe=-0.8306)
- Admission: Train IC=+0.1614, Deflated=+0.1623, IR=0.60, Mono=0.72, p=0.0014, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.069 | 2017: +0.034 | 2018: +0.192 | 2019: +0.044 | 2020: +0.043 | 2021: +0.166 | 2022: +0.020 | 2023: +0.162 | 2024: +0.115 | 2025: +0.022 | 2026: -0.086
- Yearly Tail ICs:   2015: -0.010 | 2016: +0.145 | 2017: +0.242 | 2018: +0.368 | 2019: +0.170 | 2020: +0.021 | 2021: +0.177 | 2022: +0.084 | 2023: +0.253 | 2024: +0.202 | 2025: -0.018 | 2026: -0.100
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=1.60, Recency ratio=1.23
- Early IC=+0.1128, Recent IC=+0.1383, 1st-half IC=+0.0744, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.046, Q2=+0.084, Q3_mid=+0.059, Q4=+0.037, Q5_high_vol=+0.211

**`combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0275, Sharpe=-0.8062)
- Admission: Train IC=+0.2167, Deflated=+0.2178, IR=0.62, Mono=0.71, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.062 | 2017: -0.004 | 2018: +0.168 | 2019: +0.066 | 2020: +0.018 | 2021: +0.185 | 2022: +0.053 | 2023: +0.201 | 2024: +0.012 | 2025: +0.097 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.159 | 2016: -0.062 | 2017: +0.153 | 2018: +0.455 | 2019: +0.205 | 2020: +0.194 | 2021: +0.385 | 2022: +0.177 | 2023: +0.159 | 2024: +0.141 | 2025: +0.243 | 2026: -0.400
- IC CV=0.90, Neg years (linear/tail)=1/0 of 8, Half ratio=1.78, Recency ratio=1.30
- Early IC=+0.0821, Recent IC=+0.1068, 1st-half IC=+0.0662, 2nd-half IC=+0.1177, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.033, Q2=+0.113, Q3_mid=+0.051, Q4=+0.056, Q5_high_vol=+0.185

**`combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=-0.0132, Sharpe=-0.7715)
- Admission: Train IC=+0.2165, Deflated=+0.2171, IR=0.61, Mono=0.74, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.084 | 2017: -0.016 | 2018: +0.153 | 2019: +0.062 | 2020: +0.049 | 2021: +0.180 | 2022: +0.031 | 2023: +0.199 | 2024: +0.037 | 2025: +0.090 | 2026: -0.159
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.072 | 2017: -0.054 | 2018: +0.310 | 2019: +0.237 | 2020: +0.162 | 2021: +0.341 | 2022: +0.233 | 2023: +0.318 | 2024: +0.166 | 2025: +0.158 | 2026: -0.376
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=1.82, Recency ratio=1.71
- Early IC=+0.0687, Recent IC=+0.1178, 1st-half IC=+0.0651, 2nd-half IC=+0.1187, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94, neg years=1)
- Regime ICs: Q1_low_vol=+0.021, Q2=+0.104, Q3_mid=+0.045, Q4=+0.057, Q5_high_vol=+0.203

**`combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=-0.0277, Sharpe=-0.7379)
- Admission: Train IC=+0.1930, Deflated=+0.1936, IR=0.67, Mono=0.73, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.087 | 2016: +0.065 | 2017: -0.025 | 2018: +0.158 | 2019: +0.063 | 2020: -0.011 | 2021: +0.164 | 2022: +0.069 | 2023: +0.192 | 2024: +0.010 | 2025: +0.095 | 2026: -0.197
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.097 | 2017: +0.128 | 2018: +0.352 | 2019: +0.151 | 2020: +0.030 | 2021: +0.404 | 2022: +0.227 | 2023: +0.218 | 2024: +0.175 | 2025: +0.194 | 2026: -0.148
- IC CV=1.04, Neg years (linear/tail)=2/0 of 8, Half ratio=2.49, Recency ratio=1.51
- Early IC=+0.0661, Recent IC=+0.1000, 1st-half IC=+0.0473, 2nd-half IC=+0.1178, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.100, Q3_mid=+0.022, Q4=+0.063, Q5_high_vol=+0.172

**`combo_rank_max__bar_ret_0__volume_weighted_price_position`** (Lock IC=-0.0214, Sharpe=-0.7372)
- Admission: Train IC=+0.2155, Deflated=+0.2166, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.032 | 2017: +0.051 | 2018: +0.189 | 2019: +0.057 | 2020: -0.007 | 2021: +0.167 | 2022: +0.055 | 2023: +0.189 | 2024: +0.001 | 2025: +0.086 | 2026: -0.174
- Yearly Tail ICs:   2015: +0.108 | 2016: -0.059 | 2017: +0.161 | 2018: +0.434 | 2019: +0.187 | 2020: +0.228 | 2021: +0.380 | 2022: +0.205 | 2023: +0.135 | 2024: +0.112 | 2025: +0.221 | 2026: -0.343
- IC CV=0.86, Neg years (linear/tail)=1/0 of 8, Half ratio=1.55, Recency ratio=0.78
- Early IC=+0.1210, Recent IC=+0.0945, 1st-half IC=+0.0694, 2nd-half IC=+0.1075, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.087, Q2=+0.127, Q3_mid=+0.049, Q4=+0.055, Q5_high_vol=+0.134

**`combo_sig_product__first_bar_return__volume_weighted_price_position`** (Lock IC=-0.0077, Sharpe=-0.7220)
- Admission: Train IC=+0.1727, Deflated=+0.1722, IR=0.66, Mono=0.76, p=0.0010, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.081 | 2017: +0.013 | 2018: +0.201 | 2019: +0.124 | 2020: -0.017 | 2021: +0.159 | 2022: +0.037 | 2023: +0.127 | 2024: -0.003 | 2025: +0.046 | 2026: -0.090
- Yearly Tail ICs:   2015: -0.012 | 2016: +0.026 | 2017: +0.173 | 2018: +0.251 | 2019: +0.185 | 2020: -0.024 | 2021: +0.369 | 2022: +0.316 | 2023: +0.201 | 2024: +0.064 | 2025: +0.203 | 2026: -0.163
- IC CV=0.96, Neg years (linear/tail)=2/1 of 8, Half ratio=1.11, Recency ratio=0.58
- Early IC=+0.1074, Recent IC=+0.0619, 1st-half IC=+0.0762, 2nd-half IC=+0.0847, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.089, Q3_mid=+0.001, Q4=+0.112, Q5_high_vol=+0.120

**`combo_max__max_up_ret__volume_surge_direction`** (Lock IC=-0.0158, Sharpe=-0.6017)
- Admission: Train IC=+0.2210, Deflated=+0.2198, IR=0.79, Mono=0.76, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.043 | 2017: -0.037 | 2018: +0.152 | 2019: +0.107 | 2020: -0.001 | 2021: +0.119 | 2022: +0.029 | 2023: +0.157 | 2024: +0.027 | 2025: +0.075 | 2026: -0.145
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.141 | 2017: +0.118 | 2018: +0.350 | 2019: +0.254 | 2020: +0.079 | 2021: +0.284 | 2022: +0.299 | 2023: +0.209 | 2024: +0.192 | 2025: +0.146 | 2026: -0.276
- IC CV=1.00, Neg years (linear/tail)=2/0 of 8, Half ratio=1.63, Recency ratio=1.61
- Early IC=+0.0573, Recent IC=+0.0921, 1st-half IC=+0.0556, 2nd-half IC=+0.0904, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.089, Q3_mid=+0.021, Q4=+0.047, Q5_high_vol=+0.153

**`combo_rank_max__max_up_ret__volume_surge_direction`** (Lock IC=-0.0117, Sharpe=-0.5740)
- Admission: Train IC=+0.2113, Deflated=+0.2101, IR=0.80, Mono=0.77, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.060 | 2017: -0.046 | 2018: +0.147 | 2019: +0.111 | 2020: -0.002 | 2021: +0.109 | 2022: +0.031 | 2023: +0.150 | 2024: +0.023 | 2025: +0.073 | 2026: -0.139
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.060 | 2017: +0.088 | 2018: +0.317 | 2019: +0.297 | 2020: +0.141 | 2021: +0.117 | 2022: +0.289 | 2023: +0.112 | 2024: +0.255 | 2025: +0.268 | 2026: -0.080
- IC CV=0.99, Neg years (linear/tail)=2/0 of 8, Half ratio=1.59, Recency ratio=1.67
- Early IC=+0.0542, Recent IC=+0.0907, 1st-half IC=+0.0563, 2nd-half IC=+0.0898, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.083, Q3_mid=+0.023, Q4=+0.051, Q5_high_vol=+0.143

**`combo_ratio__first_bar_return__volume_surge_direction`** (Lock IC=-0.0091, Sharpe=-0.5472)
- Admission: Train IC=+0.1306, Deflated=+0.1312, IR=0.32, Mono=0.66, p=0.0094, MaxCorr=0.03
- Yearly Linear ICs: 2015: +0.115 | 2016: +0.113 | 2017: +0.073 | 2018: +0.155 | 2019: +0.082 | 2020: -0.009 | 2021: +0.144 | 2022: +0.037 | 2023: +0.114 | 2024: +0.023 | 2025: +0.042 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.408 | 2016: +0.153 | 2017: +0.132 | 2018: +0.215 | 2019: +0.014 | 2020: -0.031 | 2021: +0.393 | 2022: +0.130 | 2023: +0.201 | 2024: -0.017 | 2025: +0.119 | 2026: -0.114
- IC CV=0.71, Neg years (linear/tail)=1/2 of 8, Half ratio=1.09, Recency ratio=0.60
- Early IC=+0.1140, Recent IC=+0.0687, 1st-half IC=+0.0760, 2nd-half IC=+0.0827, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.058, Q2=+0.080, Q3_mid=+0.049, Q4=+0.056, Q5_high_vol=+0.148

**`combo_rank_max__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.0022, Sharpe=-0.4643)
- Admission: Train IC=+0.1826, Deflated=+0.1821, IR=0.62, Mono=0.72, p=0.0004, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.026 | 2017: +0.003 | 2018: +0.134 | 2019: +0.115 | 2020: -0.021 | 2021: +0.130 | 2022: +0.048 | 2023: +0.198 | 2024: -0.025 | 2025: +0.092 | 2026: -0.152
- Yearly Tail ICs:   2015: -0.039 | 2016: -0.160 | 2017: +0.177 | 2018: +0.242 | 2019: +0.249 | 2020: +0.115 | 2021: +0.213 | 2022: +0.211 | 2023: +0.085 | 2024: +0.123 | 2025: +0.284 | 2026: -0.257
- IC CV=1.05, Neg years (linear/tail)=2/0 of 8, Half ratio=1.53, Recency ratio=1.28
- Early IC=+0.0715, Recent IC=+0.0914, 1st-half IC=+0.0607, 2nd-half IC=+0.0931, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.136, Q3_mid=+0.047, Q4=+0.058, Q5_high_vol=+0.072

**`first_30min_return`** (Lock IC=-0.0197, Sharpe=-0.4422)
- Admission: Train IC=+0.1189, Deflated=+0.1197, IR=0.45, Mono=0.69, p=0.0188, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.027 | 2016: +0.026 | 2017: -0.078 | 2018: +0.052 | 2019: +0.024 | 2020: +0.040 | 2021: +0.159 | 2022: +0.039 | 2023: +0.120 | 2024: +0.048 | 2025: +0.091 | 2026: -0.187
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.115 | 2017: +0.044 | 2018: +0.131 | 2019: +0.177 | 2020: -0.025 | 2021: +0.258 | 2022: +0.118 | 2023: +0.256 | 2024: +0.238 | 2025: +0.303 | 2026: -0.328
- IC CV=1.29, Neg years (linear/tail)=1/1 of 8, Half ratio=5.79, Recency ratio=-6.45
- Early IC=-0.0130, Recent IC=+0.0837, 1st-half IC=+0.0169, 2nd-half IC=+0.0979, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.071, Q3_mid=-0.001, Q4=+0.058, Q5_high_vol=+0.123

**`open_to_current_return`** (Lock IC=-0.0197, Sharpe=-0.4422)
- Admission: Train IC=+0.1189, Deflated=+0.1197, IR=0.45, Mono=0.69, p=0.0188, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.027 | 2016: +0.026 | 2017: -0.078 | 2018: +0.052 | 2019: +0.024 | 2020: +0.040 | 2021: +0.159 | 2022: +0.039 | 2023: +0.120 | 2024: +0.048 | 2025: +0.091 | 2026: -0.187
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.115 | 2017: +0.044 | 2018: +0.131 | 2019: +0.177 | 2020: -0.025 | 2021: +0.258 | 2022: +0.118 | 2023: +0.256 | 2024: +0.238 | 2025: +0.303 | 2026: -0.328
- IC CV=1.29, Neg years (linear/tail)=1/1 of 8, Half ratio=5.79, Recency ratio=-6.45
- Early IC=-0.0130, Recent IC=+0.0837, 1st-half IC=+0.0169, 2nd-half IC=+0.0979, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.071, Q3_mid=-0.001, Q4=+0.058, Q5_high_vol=+0.123

**`combo_mean__max_up_ret__volume_surge_direction`** (Lock IC=-0.0027, Sharpe=-0.4291)
- Admission: Train IC=+0.2219, Deflated=+0.2207, IR=0.79, Mono=0.77, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.060 | 2017: -0.012 | 2018: +0.168 | 2019: +0.103 | 2020: +0.030 | 2021: +0.134 | 2022: +0.031 | 2023: +0.161 | 2024: +0.039 | 2025: +0.082 | 2026: -0.116
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.102 | 2017: +0.055 | 2018: +0.286 | 2019: +0.168 | 2020: +0.203 | 2021: +0.220 | 2022: +0.161 | 2023: +0.410 | 2024: +0.274 | 2025: +0.232 | 2026: -0.205
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.52, Recency ratio=1.29
- Early IC=+0.0780, Recent IC=+0.1003, 1st-half IC=+0.0676, 2nd-half IC=+0.1029, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.107, Q3_mid=+0.019, Q4=+0.064, Q5_high_vol=+0.172

**`combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=-0.0043, Sharpe=-0.2113)
- Admission: Train IC=+0.1995, Deflated=+0.1983, IR=0.62, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.050 | 2017: -0.038 | 2018: +0.163 | 2019: +0.129 | 2020: +0.012 | 2021: +0.133 | 2022: +0.037 | 2023: +0.194 | 2024: +0.003 | 2025: +0.078 | 2026: -0.142
- Yearly Tail ICs:   2015: +0.102 | 2016: -0.130 | 2017: +0.011 | 2018: +0.275 | 2019: +0.170 | 2020: +0.112 | 2021: +0.223 | 2022: +0.168 | 2023: +0.258 | 2024: +0.168 | 2025: +0.254 | 2026: -0.117
- IC CV=0.97, Neg years (linear/tail)=1/0 of 8, Half ratio=1.33, Recency ratio=1.46
- Early IC=+0.0698, Recent IC=+0.1018, 1st-half IC=+0.0736, 2nd-half IC=+0.0977, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10, neg years=2)
- Regime ICs: Q1_low_vol=+0.036, Q2=+0.116, Q3_mid=+0.047, Q4=+0.066, Q5_high_vol=+0.150

**`combo_max__volume_weighted_price_position__volume_surge_direction`** (Lock IC=-0.0002, Sharpe=-0.0703)
- Admission: Train IC=+0.1755, Deflated=+0.1750, IR=0.61, Mono=0.71, p=0.0008, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.023 | 2017: +0.009 | 2018: +0.128 | 2019: +0.113 | 2020: -0.026 | 2021: +0.140 | 2022: +0.051 | 2023: +0.210 | 2024: -0.033 | 2025: +0.096 | 2026: -0.148
- Yearly Tail ICs:   2015: -0.100 | 2016: -0.119 | 2017: +0.153 | 2018: +0.287 | 2019: +0.198 | 2020: +0.087 | 2021: +0.261 | 2022: +0.241 | 2023: +0.142 | 2024: +0.096 | 2025: +0.253 | 2026: -0.253
- IC CV=1.11, Neg years (linear/tail)=2/0 of 8, Half ratio=1.71, Recency ratio=1.29
- Early IC=+0.0684, Recent IC=+0.0882, 1st-half IC=+0.0546, 2nd-half IC=+0.0932, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24, neg years=2)
- Regime ICs: Q1_low_vol=+0.091, Q2=+0.131, Q3_mid=+0.046, Q4=+0.054, Q5_high_vol=+0.073

### 500ETF — `single` False Positives

**`early_order_flow_imbalance`** (Lock IC=-0.0041, Sharpe=-1.9661)
- Admission: Train IC=+0.2348, Deflated=+0.2351, IR=0.58, Mono=0.73, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.093 | 2016: -0.043 | 2017: +0.093 | 2018: +0.101 | 2019: +0.121 | 2020: +0.038 | 2021: +0.122 | 2022: +0.141 | 2023: +0.079 | 2024: +0.107 | 2025: +0.091 | 2026: -0.135
- Yearly Tail ICs:   2015: +0.234 | 2016: -0.073 | 2017: +0.091 | 2018: +0.296 | 2019: +0.233 | 2020: +0.049 | 2021: +0.226 | 2022: +0.337 | 2023: +0.131 | 2024: +0.366 | 2025: +0.046 | 2026: -0.113
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.40, Recency ratio=0.96
- Early IC=+0.0969, Recent IC=+0.0927, 1st-half IC=+0.0827, 2nd-half IC=+0.1155, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.072, Q3_mid=+0.065, Q4=+0.113, Q5_high_vol=+0.095

**`range_progression_trend`** (Lock IC=-0.0206, Sharpe=-1.6976)
- Admission: Train IC=+0.2064, Deflated=+0.2063, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.082 | 2016: -0.030 | 2017: +0.063 | 2018: +0.063 | 2019: +0.071 | 2020: +0.033 | 2021: +0.100 | 2022: +0.158 | 2023: +0.056 | 2024: +0.086 | 2025: +0.101 | 2026: -0.183
- Yearly Tail ICs:   2015: +0.062 | 2016: -0.063 | 2017: +0.088 | 2018: +0.231 | 2019: +0.184 | 2020: +0.104 | 2021: +0.204 | 2022: +0.310 | 2023: +0.152 | 2024: +0.295 | 2025: +0.024 | 2026: -0.028
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=1.13
- Early IC=+0.0629, Recent IC=+0.0711, 1st-half IC=+0.0541, 2nd-half IC=+0.1033, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.079, Q3_mid=+0.049, Q4=+0.093, Q5_high_vol=+0.079

**`always_in_trend_persistence`** (Lock IC=-0.0147, Sharpe=-1.5236)
- Admission: Train IC=+0.1892, Deflated=+0.1892, IR=0.55, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.057 | 2016: -0.034 | 2017: +0.074 | 2018: +0.070 | 2019: +0.049 | 2020: +0.046 | 2021: +0.111 | 2022: +0.147 | 2023: +0.073 | 2024: +0.098 | 2025: +0.093 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.018 | 2016: -0.163 | 2017: +0.111 | 2018: +0.265 | 2019: +0.033 | 2020: +0.028 | 2021: +0.187 | 2022: +0.244 | 2023: +0.235 | 2024: +0.410 | 2025: -0.004 | 2026: -0.090
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=1.18
- Early IC=+0.0722, Recent IC=+0.0851, 1st-half IC=+0.0566, 2nd-half IC=+0.1083, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.071, Q3_mid=+0.058, Q4=+0.093, Q5_high_vol=+0.065

### 159915ETF — `single` False Positives

**`combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=-0.0153, Sharpe=-0.1443)
- Admission: Train IC=+0.1698, Deflated=+0.1696, IR=0.51, Mono=0.65, p=0.0012, MaxCorr=0.51
- Yearly Linear ICs: 2015: +0.046 | 2016: +0.052 | 2017: +0.101 | 2018: +0.113 | 2019: +0.008 | 2020: +0.084 | 2021: +0.062 | 2022: +0.021 | 2023: +0.072 | 2024: -0.047 | 2025: -0.027 | 2026: +0.020
- Yearly Tail ICs:   2015: -0.058 | 2016: +0.193 | 2017: +0.039 | 2018: +0.402 | 2019: +0.079 | 2020: +0.061 | 2021: +0.258 | 2022: +0.220 | 2023: +0.239 | 2024: +0.056 | 2025: +0.120 | 2026: -0.120
- IC CV=0.97, Neg years (linear/tail)=1/0 of 8, Half ratio=0.26, Recency ratio=0.12
- Early IC=+0.1069, Recent IC=+0.0125, 1st-half IC=+0.0837, 2nd-half IC=+0.0216, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61, neg years=0)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.012, Q3_mid=+0.021, Q4=+0.103, Q5_high_vol=+0.061

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0753, Sharpe=-0.1501)
- Admission: Train IC=+0.1986, Deflated=+0.1991, IR=0.58, Mono=0.72, p=0.0002, MaxCorr=0.71
- Yearly Linear ICs: 2015: +0.080 | 2016: +0.040 | 2017: -0.059 | 2018: +0.144 | 2019: +0.097 | 2020: +0.039 | 2021: +0.142 | 2022: +0.100 | 2023: +0.086 | 2024: -0.004 | 2025: +0.074 | 2026: +0.063
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.074 | 2017: -0.142 | 2018: +0.322 | 2019: +0.206 | 2020: +0.145 | 2021: +0.514 | 2022: +0.334 | 2023: +0.186 | 2024: +0.119 | 2025: +0.014 | 2026: +0.008
- IC CV=0.98, Neg years (linear/tail)=2/1 of 8, Half ratio=1.48, Recency ratio=0.96
- Early IC=+0.0425, Recent IC=+0.0409, 1st-half IC=+0.0597, 2nd-half IC=+0.0884, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=-0.001, Q2=+0.062, Q3_mid=+0.079, Q4=+0.058, Q5_high_vol=+0.154

**`combo_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0685, Sharpe=-0.2790)
- Admission: Train IC=+0.1985, Deflated=+0.1982, IR=0.47, Mono=0.68, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.063 | 2017: -0.040 | 2018: +0.162 | 2019: +0.138 | 2020: +0.017 | 2021: +0.124 | 2022: +0.028 | 2023: +0.140 | 2024: +0.031 | 2025: +0.098 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.143 | 2016: +0.067 | 2017: -0.139 | 2018: +0.311 | 2019: +0.233 | 2020: +0.183 | 2021: +0.252 | 2022: +0.150 | 2023: +0.227 | 2024: +0.258 | 2025: +0.079 | 2026: +0.266
- IC CV=0.93, Neg years (linear/tail)=1/1 of 8, Half ratio=1.11, Recency ratio=1.40
- Early IC=+0.0609, Recent IC=+0.0855, 1st-half IC=+0.0801, 2nd-half IC=+0.0886, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.015, Q2=+0.067, Q3_mid=+0.070, Q4=+0.060, Q5_high_vol=+0.195

**`combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0685, Sharpe=-0.2790)
- Admission: Train IC=+0.1985, Deflated=+0.1982, IR=0.47, Mono=0.68, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.063 | 2017: -0.040 | 2018: +0.162 | 2019: +0.138 | 2020: +0.017 | 2021: +0.124 | 2022: +0.028 | 2023: +0.140 | 2024: +0.031 | 2025: +0.098 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.143 | 2016: +0.067 | 2017: -0.139 | 2018: +0.311 | 2019: +0.233 | 2020: +0.183 | 2021: +0.252 | 2022: +0.150 | 2023: +0.227 | 2024: +0.258 | 2025: +0.079 | 2026: +0.266
- IC CV=0.93, Neg years (linear/tail)=1/1 of 8, Half ratio=1.11, Recency ratio=1.40
- Early IC=+0.0609, Recent IC=+0.0855, 1st-half IC=+0.0801, 2nd-half IC=+0.0886, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.015, Q2=+0.067, Q3_mid=+0.070, Q4=+0.060, Q5_high_vol=+0.195

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0544, Sharpe=-0.0805)
- Admission: Train IC=+0.2766, Deflated=+0.2766, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.80, Neg years (linear/tail)=1/0 of 8, Half ratio=1.14, Recency ratio=1.31
- Early IC=+0.0834, Recent IC=+0.1090, 1st-half IC=+0.0944, 2nd-half IC=+0.1072, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.023, Q2=+0.054, Q3_mid=+0.094, Q4=+0.081, Q5_high_vol=+0.219

**`combo_min__volume_weighted_price_position__volume_surge_direction`** (Lock IC=+0.0531, Sharpe=-0.1105)
- Admission: Train IC=+0.1673, Deflated=+0.1660, IR=0.59, Mono=0.72, p=0.0012, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.050 | 2017: -0.021 | 2018: +0.258 | 2019: +0.069 | 2020: -0.003 | 2021: +0.108 | 2022: +0.081 | 2023: +0.166 | 2024: -0.010 | 2025: +0.124 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.449 | 2016: -0.280 | 2017: +0.027 | 2018: +0.223 | 2019: +0.101 | 2020: +0.112 | 2021: +0.314 | 2022: +0.234 | 2023: +0.304 | 2024: +0.134 | 2025: +0.249 | 2026: -0.302
- IC CV=1.11, Neg years (linear/tail)=3/0 of 8, Half ratio=1.16, Recency ratio=0.66
- Early IC=+0.1186, Recent IC=+0.0781, 1st-half IC=+0.0805, 2nd-half IC=+0.0931, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.119, Q3_mid=+0.018, Q4=+0.099, Q5_high_vol=+0.138

**`combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0463, Sharpe=-0.5117)
- Admission: Train IC=+0.2881, Deflated=+0.2875, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.058 | 2017: -0.016 | 2018: +0.189 | 2019: +0.144 | 2020: +0.031 | 2021: +0.133 | 2022: +0.047 | 2023: +0.177 | 2024: +0.042 | 2025: +0.096 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.332 | 2016: +0.110 | 2017: +0.091 | 2018: +0.383 | 2019: +0.217 | 2020: +0.188 | 2021: +0.513 | 2022: +0.200 | 2023: +0.302 | 2024: +0.230 | 2025: -0.006 | 2026: +0.299
- IC CV=0.77, Neg years (linear/tail)=1/0 of 8, Half ratio=1.12, Recency ratio=1.27
- Early IC=+0.0866, Recent IC=+0.1097, 1st-half IC=+0.0932, 2nd-half IC=+0.1049, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.062, Q3_mid=+0.086, Q4=+0.082, Q5_high_vol=+0.204

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0463, Sharpe=-0.4058)
- Admission: Train IC=+0.1811, Deflated=+0.1817, IR=0.58, Mono=0.71, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.060 | 2017: -0.078 | 2018: +0.158 | 2019: +0.108 | 2020: +0.050 | 2021: +0.142 | 2022: +0.041 | 2023: +0.108 | 2024: +0.035 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.083 | 2017: -0.170 | 2018: +0.357 | 2019: +0.430 | 2020: +0.129 | 2021: +0.309 | 2022: +0.261 | 2023: +0.033 | 2024: +0.334 | 2025: -0.024 | 2026: +0.265
- IC CV=1.00, Neg years (linear/tail)=1/1 of 8, Half ratio=1.24, Recency ratio=1.88
- Early IC=+0.0383, Recent IC=+0.0720, 1st-half IC=+0.0733, 2nd-half IC=+0.0906, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=-0.057, Q2=+0.059, Q3_mid=+0.096, Q4=+0.054, Q5_high_vol=+0.209

**`combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.0463, Sharpe=-0.4058)
- Admission: Train IC=+0.1811, Deflated=+0.1817, IR=0.58, Mono=0.71, p=0.0004, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.060 | 2017: -0.078 | 2018: +0.158 | 2019: +0.108 | 2020: +0.050 | 2021: +0.142 | 2022: +0.041 | 2023: +0.108 | 2024: +0.035 | 2025: +0.062 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.191 | 2016: +0.083 | 2017: -0.170 | 2018: +0.357 | 2019: +0.430 | 2020: +0.129 | 2021: +0.309 | 2022: +0.261 | 2023: +0.033 | 2024: +0.334 | 2025: -0.024 | 2026: +0.265
- IC CV=1.00, Neg years (linear/tail)=1/1 of 8, Half ratio=1.24, Recency ratio=1.88
- Early IC=+0.0383, Recent IC=+0.0720, 1st-half IC=+0.0732, 2nd-half IC=+0.0906, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=-0.057, Q2=+0.059, Q3_mid=+0.096, Q4=+0.054, Q5_high_vol=+0.209

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0463, Sharpe=-0.3093)
- Admission: Train IC=+0.2456, Deflated=+0.2449, IR=0.66, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.108 | 2017: +0.020 | 2018: +0.215 | 2019: +0.107 | 2020: +0.039 | 2021: +0.141 | 2022: +0.070 | 2023: +0.131 | 2024: +0.015 | 2025: +0.082 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.248 | 2016: +0.051 | 2017: -0.006 | 2018: +0.304 | 2019: +0.179 | 2020: +0.238 | 2021: +0.436 | 2022: +0.314 | 2023: +0.235 | 2024: +0.097 | 2025: +0.161 | 2026: +0.049
- IC CV=0.70, Neg years (linear/tail)=0/1 of 8, Half ratio=0.96, Recency ratio=0.62
- Early IC=+0.1177, Recent IC=+0.0728, 1st-half IC=+0.1007, 2nd-half IC=+0.0963, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.067, Q3_mid=+0.054, Q4=+0.080, Q5_high_vol=+0.213

**`combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.0389, Sharpe=-0.6153)
- Admission: Train IC=+0.1680, Deflated=+0.1686, IR=0.40, Mono=0.66, p=0.0012, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.059 | 2017: -0.082 | 2018: +0.173 | 2019: +0.115 | 2020: +0.044 | 2021: +0.142 | 2022: +0.020 | 2023: +0.104 | 2024: +0.039 | 2025: +0.062 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.195 | 2016: +0.089 | 2017: -0.221 | 2018: +0.357 | 2019: +0.374 | 2020: +0.110 | 2021: +0.235 | 2022: +0.155 | 2023: +0.021 | 2024: +0.341 | 2025: +0.021 | 2026: +0.337
- IC CV=1.10, Neg years (linear/tail)=1/1 of 8, Half ratio=1.13, Recency ratio=1.56
- Early IC=+0.0458, Recent IC=+0.0713, 1st-half IC=+0.0777, 2nd-half IC=+0.0875, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=-0.060, Q2=+0.053, Q3_mid=+0.088, Q4=+0.062, Q5_high_vol=+0.218

**`combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0389, Sharpe=-0.6153)
- Admission: Train IC=+0.1680, Deflated=+0.1686, IR=0.40, Mono=0.66, p=0.0012, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.059 | 2017: -0.082 | 2018: +0.173 | 2019: +0.115 | 2020: +0.044 | 2021: +0.142 | 2022: +0.020 | 2023: +0.104 | 2024: +0.039 | 2025: +0.062 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.195 | 2016: +0.089 | 2017: -0.221 | 2018: +0.357 | 2019: +0.374 | 2020: +0.110 | 2021: +0.235 | 2022: +0.155 | 2023: +0.021 | 2024: +0.341 | 2025: +0.021 | 2026: +0.337
- IC CV=1.10, Neg years (linear/tail)=1/1 of 8, Half ratio=1.13, Recency ratio=1.56
- Early IC=+0.0458, Recent IC=+0.0713, 1st-half IC=+0.0777, 2nd-half IC=+0.0875, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=-0.060, Q2=+0.053, Q3_mid=+0.088, Q4=+0.062, Q5_high_vol=+0.218

**`combo_max__first_bar_sentiment__volume_surge_direction`** (Lock IC=+0.0321, Sharpe=-0.4244)
- Admission: Train IC=+0.1068, Deflated=+0.1051, IR=0.41, Mono=0.65, p=0.0324, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.056 | 2017: +0.032 | 2018: +0.173 | 2019: +0.111 | 2020: +0.024 | 2021: +0.056 | 2022: +0.054 | 2023: +0.151 | 2024: +0.001 | 2025: +0.109 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.163 | 2016: -0.076 | 2017: +0.112 | 2018: +0.321 | 2019: +0.227 | 2020: +0.150 | 2021: -0.120 | 2022: +0.086 | 2023: +0.205 | 2024: +0.055 | 2025: +0.327 | 2026: +0.019
- IC CV=0.78, Neg years (linear/tail)=0/1 of 8, Half ratio=0.80, Recency ratio=0.74
- Early IC=+0.1028, Recent IC=+0.0757, 1st-half IC=+0.0843, 2nd-half IC=+0.0676, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.115, Q3_mid=+0.018, Q4=+0.073, Q5_high_vol=+0.101

**`combo_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0303, Sharpe=-0.4943)
- Admission: Train IC=+0.1898, Deflated=+0.1891, IR=0.57, Mono=0.71, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.088 | 2016: +0.073 | 2017: -0.049 | 2018: +0.215 | 2019: +0.079 | 2020: +0.053 | 2021: +0.129 | 2022: +0.039 | 2023: +0.138 | 2024: +0.017 | 2025: +0.109 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.021 | 2017: -0.154 | 2018: +0.243 | 2019: +0.208 | 2020: +0.201 | 2021: +0.296 | 2022: +0.121 | 2023: +0.223 | 2024: +0.222 | 2025: +0.340 | 2026: -0.198
- IC CV=0.99, Neg years (linear/tail)=1/1 of 8, Half ratio=1.07, Recency ratio=0.93
- Early IC=+0.0831, Recent IC=+0.0771, 1st-half IC=+0.0812, 2nd-half IC=+0.0865, Neg regimes=1/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.006, Q2=+0.111, Q3_mid=+0.021, Q4=+0.079, Q5_high_vol=+0.184

**`combo_min__bar_body_rng_0__volume_surge_direction`** (Lock IC=+0.0300, Sharpe=-0.0790)
- Admission: Train IC=+0.2339, Deflated=+0.2334, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.059 | 2016: +0.030 | 2017: -0.002 | 2018: +0.189 | 2019: +0.080 | 2020: +0.037 | 2021: +0.160 | 2022: +0.026 | 2023: +0.166 | 2024: +0.016 | 2025: +0.085 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.261 | 2016: -0.184 | 2017: +0.046 | 2018: +0.187 | 2019: +0.040 | 2020: +0.264 | 2021: +0.464 | 2022: -0.047 | 2023: +0.425 | 2024: +0.276 | 2025: +0.386 | 2026: -0.259
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=1.16, Recency ratio=0.97
- Early IC=+0.0936, Recent IC=+0.0908, 1st-half IC=+0.0814, 2nd-half IC=+0.0943, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.105, Q3_mid=+0.056, Q4=+0.076, Q5_high_vol=+0.148

**`combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0286, Sharpe=-0.6094)
- Admission: Train IC=+0.2062, Deflated=+0.2060, IR=0.69, Mono=0.79, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.066 | 2017: +0.032 | 2018: +0.210 | 2019: +0.076 | 2020: -0.030 | 2021: +0.131 | 2022: +0.059 | 2023: +0.172 | 2024: +0.023 | 2025: +0.094 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.190 | 2016: -0.102 | 2017: +0.120 | 2018: +0.146 | 2019: +0.189 | 2020: +0.018 | 2021: +0.338 | 2022: +0.396 | 2023: +0.320 | 2024: +0.130 | 2025: +0.074 | 2026: -0.168
- IC CV=0.90, Neg years (linear/tail)=1/0 of 8, Half ratio=1.37, Recency ratio=0.81
- Early IC=+0.1206, Recent IC=+0.0975, 1st-half IC=+0.0751, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.102, Q3_mid=+0.054, Q4=+0.074, Q5_high_vol=+0.144

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=+0.0259, Sharpe=-0.2846)
- Admission: Train IC=+0.2430, Deflated=+0.2433, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.054 | 2017: -0.045 | 2018: +0.209 | 2019: +0.132 | 2020: +0.059 | 2021: +0.155 | 2022: +0.046 | 2023: +0.129 | 2024: +0.031 | 2025: +0.082 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.372 | 2016: -0.042 | 2017: -0.012 | 2018: +0.261 | 2019: +0.298 | 2020: +0.214 | 2021: +0.412 | 2022: +0.328 | 2023: +0.093 | 2024: +0.250 | 2025: +0.056 | 2026: +0.218
- IC CV=0.85, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=0.98
- Early IC=+0.0816, Recent IC=+0.0802, 1st-half IC=+0.0967, 2nd-half IC=+0.0964, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.060, Q3_mid=+0.077, Q4=+0.085, Q5_high_vol=+0.222

**`combo_mean__volume_weighted_price_position__volume_surge_direction`** (Lock IC=+0.0258, Sharpe=-0.9326)
- Admission: Train IC=+0.1680, Deflated=+0.1672, IR=0.58, Mono=0.70, p=0.0012, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.107 | 2016: +0.040 | 2017: +0.001 | 2018: +0.215 | 2019: +0.113 | 2020: -0.010 | 2021: +0.132 | 2022: +0.066 | 2023: +0.194 | 2024: -0.008 | 2025: +0.124 | 2026: -0.120
- Yearly Tail ICs:   2015: +0.168 | 2016: -0.218 | 2017: +0.131 | 2018: +0.296 | 2019: +0.091 | 2020: +0.083 | 2021: +0.286 | 2022: +0.285 | 2023: +0.224 | 2024: +0.158 | 2025: +0.266 | 2026: -0.386
- IC CV=0.96, Neg years (linear/tail)=2/0 of 8, Half ratio=1.24, Recency ratio=0.86
- Early IC=+0.1081, Recent IC=+0.0932, 1st-half IC=+0.0821, 2nd-half IC=+0.1021, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.059, Q2=+0.138, Q3_mid=+0.036, Q4=+0.089, Q5_high_vol=+0.125

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=+0.0255, Sharpe=-0.3058)
- Admission: Train IC=+0.2219, Deflated=+0.2214, IR=0.63, Mono=0.74, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.107 | 2017: -0.039 | 2018: +0.233 | 2019: +0.094 | 2020: +0.065 | 2021: +0.154 | 2022: +0.076 | 2023: +0.144 | 2024: +0.030 | 2025: +0.081 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.099 | 2017: -0.024 | 2018: +0.379 | 2019: +0.244 | 2020: +0.258 | 2021: +0.331 | 2022: +0.262 | 2023: +0.200 | 2024: +0.140 | 2025: +0.196 | 2026: +0.070
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.12, Recency ratio=0.90
- Early IC=+0.0970, Recent IC=+0.0869, 1st-half IC=+0.0967, 2nd-half IC=+0.1084, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.005, Q2=+0.074, Q3_mid=+0.061, Q4=+0.074, Q5_high_vol=+0.251

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=+0.0253, Sharpe=-0.2427)
- Admission: Train IC=+0.2219, Deflated=+0.2214, IR=0.63, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.107 | 2017: -0.039 | 2018: +0.233 | 2019: +0.094 | 2020: +0.065 | 2021: +0.154 | 2022: +0.076 | 2023: +0.144 | 2024: +0.030 | 2025: +0.081 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.223 | 2016: +0.099 | 2017: -0.026 | 2018: +0.381 | 2019: +0.244 | 2020: +0.258 | 2021: +0.328 | 2022: +0.260 | 2023: +0.200 | 2024: +0.140 | 2025: +0.196 | 2026: +0.073
- IC CV=0.83, Neg years (linear/tail)=1/1 of 8, Half ratio=1.12, Recency ratio=0.89
- Early IC=+0.0969, Recent IC=+0.0867, 1st-half IC=+0.0967, 2nd-half IC=+0.1083, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.005, Q2=+0.074, Q3_mid=+0.061, Q4=+0.074, Q5_high_vol=+0.251

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0244, Sharpe=-0.2554)
- Admission: Train IC=+0.2628, Deflated=+0.2633, IR=0.78, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.26, Recency ratio=1.41
- Early IC=+0.0674, Recent IC=+0.0948, 1st-half IC=+0.0879, 2nd-half IC=+0.1110, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.032, Q2=+0.068, Q3_mid=+0.113, Q4=+0.074, Q5_high_vol=+0.235

**`combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0244, Sharpe=-0.8744)
- Admission: Train IC=+0.1714, Deflated=+0.1712, IR=0.56, Mono=0.67, p=0.0010, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.097 | 2016: -0.003 | 2017: -0.036 | 2018: +0.104 | 2019: +0.070 | 2020: +0.039 | 2021: +0.115 | 2022: +0.058 | 2023: +0.100 | 2024: +0.004 | 2025: -0.009 | 2026: +0.073
- Yearly Tail ICs:   2015: +0.046 | 2016: +0.035 | 2017: -0.054 | 2018: +0.235 | 2019: +0.197 | 2020: +0.137 | 2021: +0.326 | 2022: +0.264 | 2023: +0.186 | 2024: +0.169 | 2025: -0.090 | 2026: -0.097
- IC CV=0.87, Neg years (linear/tail)=1/1 of 8, Half ratio=2.02, Recency ratio=1.52
- Early IC=+0.0342, Recent IC=+0.0519, 1st-half IC=+0.0380, 2nd-half IC=+0.0766, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.038, Q3_mid=+0.056, Q4=+0.058, Q5_high_vol=+0.140

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0229, Sharpe=-0.5791)
- Admission: Train IC=+0.2826, Deflated=+0.2824, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.072 | 2017: -0.020 | 2018: +0.232 | 2019: +0.117 | 2020: +0.046 | 2021: +0.179 | 2022: +0.026 | 2023: +0.145 | 2024: +0.046 | 2025: +0.072 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.256 | 2016: +0.064 | 2017: +0.062 | 2018: +0.372 | 2019: +0.343 | 2020: +0.149 | 2021: +0.582 | 2022: +0.177 | 2023: +0.156 | 2024: +0.188 | 2025: -0.085 | 2026: +0.280
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.06, Recency ratio=0.90
- Early IC=+0.1058, Recent IC=+0.0956, 1st-half IC=+0.1002, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.064, Q3_mid=+0.084, Q4=+0.086, Q5_high_vol=+0.228

**`combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=+0.0217, Sharpe=-0.2987)
- Admission: Train IC=+0.1702, Deflated=+0.1701, IR=0.48, Mono=0.68, p=0.0012, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.125 | 2016: +0.122 | 2017: -0.025 | 2018: +0.164 | 2019: -0.000 | 2020: +0.067 | 2021: +0.161 | 2022: +0.082 | 2023: +0.122 | 2024: +0.017 | 2025: +0.049 | 2026: -0.006
- Yearly Tail ICs:   2015: -0.097 | 2016: +0.070 | 2017: -0.132 | 2018: +0.350 | 2019: +0.061 | 2020: +0.096 | 2021: +0.263 | 2022: +0.338 | 2023: +0.220 | 2024: +0.164 | 2025: +0.067 | 2026: -0.023
- IC CV=0.92, Neg years (linear/tail)=2/1 of 8, Half ratio=1.83, Recency ratio=1.00
- Early IC=+0.0695, Recent IC=+0.0695, 1st-half IC=+0.0564, 2nd-half IC=+0.1031, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.076, Q3_mid=+0.015, Q4=+0.060, Q5_high_vol=+0.211

**`combo_sig_product__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0216, Sharpe=-0.8416)
- Admission: Train IC=+0.1921, Deflated=+0.1925, IR=0.67, Mono=0.72, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.107 | 2017: +0.050 | 2018: +0.192 | 2019: +0.079 | 2020: -0.008 | 2021: +0.155 | 2022: +0.035 | 2023: +0.154 | 2024: +0.041 | 2025: +0.073 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.076 | 2016: +0.191 | 2017: +0.051 | 2018: +0.359 | 2019: +0.136 | 2020: -0.018 | 2021: +0.383 | 2022: +0.246 | 2023: +0.349 | 2024: +0.122 | 2025: +0.066 | 2026: -0.137
- IC CV=0.76, Neg years (linear/tail)=1/1 of 8, Half ratio=1.20, Recency ratio=0.81
- Early IC=+0.1211, Recent IC=+0.0977, 1st-half IC=+0.0837, 2nd-half IC=+0.1005, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.092, Q3_mid=+0.056, Q4=+0.075, Q5_high_vol=+0.172

**`bar_body_rng_0`** (Lock IC=+0.0209, Sharpe=-0.8416)
- Admission: Train IC=+0.1921, Deflated=+0.1925, IR=0.67, Mono=0.72, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.100 | 2016: +0.107 | 2017: +0.047 | 2018: +0.192 | 2019: +0.077 | 2020: -0.009 | 2021: +0.155 | 2022: +0.035 | 2023: +0.153 | 2024: +0.041 | 2025: +0.072 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.081 | 2016: +0.174 | 2017: +0.052 | 2018: +0.365 | 2019: +0.131 | 2020: -0.020 | 2021: +0.383 | 2022: +0.249 | 2023: +0.339 | 2024: +0.122 | 2025: +0.057 | 2026: -0.139
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=1.22, Recency ratio=0.81
- Early IC=+0.1198, Recent IC=+0.0972, 1st-half IC=+0.0825, 2nd-half IC=+0.1005, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.091, Q3_mid=+0.055, Q4=+0.075, Q5_high_vol=+0.172

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.0205, Sharpe=-0.8741)
- Admission: Train IC=+0.1899, Deflated=+0.1894, IR=0.69, Mono=0.77, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.030 | 2018: +0.154 | 2019: -0.007 | 2020: +0.055 | 2021: +0.151 | 2022: +0.070 | 2023: +0.090 | 2024: +0.031 | 2025: +0.034 | 2026: +0.015
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.141 | 2017: -0.003 | 2018: +0.484 | 2019: +0.111 | 2020: +0.032 | 2021: +0.300 | 2022: +0.382 | 2023: +0.114 | 2024: +0.105 | 2025: -0.040 | 2026: -0.041
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=1.79, Recency ratio=0.65
- Early IC=+0.0924, Recent IC=+0.0603, 1st-half IC=+0.0519, 2nd-half IC=+0.0928, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.039, Q2=+0.063, Q3_mid=-0.001, Q4=+0.043, Q5_high_vol=+0.195

**`combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0200, Sharpe=-0.3911)
- Admission: Train IC=+0.1879, Deflated=+0.1880, IR=0.59, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.124 | 2016: +0.114 | 2017: -0.036 | 2018: +0.201 | 2019: +0.136 | 2020: +0.017 | 2021: +0.149 | 2022: +0.068 | 2023: +0.176 | 2024: +0.048 | 2025: +0.072 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.005 | 2016: +0.182 | 2017: -0.111 | 2018: +0.244 | 2019: +0.249 | 2020: +0.079 | 2021: +0.407 | 2022: +0.339 | 2023: +0.215 | 2024: +0.161 | 2025: +0.223 | 2026: -0.023
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.37, Recency ratio=1.35
- Early IC=+0.0828, Recent IC=+0.1119, 1st-half IC=+0.0866, 2nd-half IC=+0.1183, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.096, Q3_mid=+0.051, Q4=+0.057, Q5_high_vol=+0.243

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0200, Sharpe=-0.6924)
- Admission: Train IC=+0.2900, Deflated=+0.2899, IR=0.77, Mono=0.74, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.097 | 2017: +0.003 | 2018: +0.184 | 2019: +0.113 | 2020: +0.043 | 2021: +0.135 | 2022: +0.037 | 2023: +0.166 | 2024: +0.056 | 2025: +0.047 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.109 | 2017: +0.081 | 2018: +0.373 | 2019: +0.253 | 2020: +0.231 | 2021: +0.519 | 2022: +0.121 | 2023: +0.332 | 2024: +0.234 | 2025: -0.034 | 2026: +0.159
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.18
- Early IC=+0.0938, Recent IC=+0.1107, 1st-half IC=+0.0900, 2nd-half IC=+0.1024, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.062, Q3_mid=+0.072, Q4=+0.064, Q5_high_vol=+0.215

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.0185, Sharpe=-0.4405)
- Admission: Train IC=+0.2045, Deflated=+0.2038, IR=0.60, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.105 | 2017: -0.027 | 2018: +0.203 | 2019: +0.092 | 2020: +0.058 | 2021: +0.156 | 2022: +0.073 | 2023: +0.128 | 2024: +0.029 | 2025: +0.071 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.105 | 2017: -0.001 | 2018: +0.284 | 2019: +0.202 | 2020: +0.194 | 2021: +0.379 | 2022: +0.261 | 2023: +0.231 | 2024: +0.109 | 2025: +0.073 | 2026: +0.034
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=1.21, Recency ratio=0.89
- Early IC=+0.0884, Recent IC=+0.0784, 1st-half IC=+0.0862, 2nd-half IC=+0.1044, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.009, Q2=+0.057, Q3_mid=+0.047, Q4=+0.058, Q5_high_vol=+0.240

**`combo_min__first_bar_return__volume_surge_direction`** (Lock IC=+0.0184, Sharpe=-0.4276)
- Admission: Train IC=+0.1784, Deflated=+0.1778, IR=0.56, Mono=0.69, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.045 | 2017: +0.047 | 2018: +0.184 | 2019: +0.072 | 2020: +0.046 | 2021: +0.147 | 2022: +0.032 | 2023: +0.136 | 2024: -0.005 | 2025: +0.078 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.287 | 2016: -0.313 | 2017: +0.038 | 2018: +0.077 | 2019: +0.014 | 2020: +0.373 | 2021: +0.300 | 2022: +0.180 | 2023: +0.333 | 2024: +0.235 | 2025: +0.166 | 2026: -0.184
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=0.98, Recency ratio=0.57
- Early IC=+0.1156, Recent IC=+0.0656, 1st-half IC=+0.0819, 2nd-half IC=+0.0807, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.100, Q3_mid=+0.018, Q4=+0.074, Q5_high_vol=+0.150

**`combo_min__bar_ret_0__volume_surge_direction`** (Lock IC=+0.0183, Sharpe=-0.4276)
- Admission: Train IC=+0.1786, Deflated=+0.1781, IR=0.56, Mono=0.70, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.073 | 2016: +0.046 | 2017: +0.047 | 2018: +0.184 | 2019: +0.072 | 2020: +0.046 | 2021: +0.147 | 2022: +0.032 | 2023: +0.136 | 2024: -0.005 | 2025: +0.078 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.287 | 2016: -0.315 | 2017: +0.039 | 2018: +0.077 | 2019: +0.014 | 2020: +0.370 | 2021: +0.300 | 2022: +0.180 | 2023: +0.330 | 2024: +0.233 | 2025: +0.166 | 2026: -0.184
- IC CV=0.74, Neg years (linear/tail)=1/0 of 8, Half ratio=0.99, Recency ratio=0.57
- Early IC=+0.1155, Recent IC=+0.0657, 1st-half IC=+0.0819, 2nd-half IC=+0.0807, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.099, Q3_mid=+0.018, Q4=+0.074, Q5_high_vol=+0.150

**`combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0168, Sharpe=-0.5135)
- Admission: Train IC=+0.2188, Deflated=+0.2192, IR=0.70, Mono=0.77, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.079 | 2017: +0.045 | 2018: +0.207 | 2019: +0.081 | 2020: -0.013 | 2021: +0.149 | 2022: +0.052 | 2023: +0.169 | 2024: +0.024 | 2025: +0.098 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.080 | 2017: +0.131 | 2018: +0.378 | 2019: +0.123 | 2020: +0.093 | 2021: +0.426 | 2022: +0.286 | 2023: +0.280 | 2024: +0.222 | 2025: +0.176 | 2026: -0.085
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=1.27, Recency ratio=0.77
- Early IC=+0.1261, Recent IC=+0.0968, 1st-half IC=+0.0835, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.117, Q3_mid=+0.049, Q4=+0.070, Q5_high_vol=+0.162

**`combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0168, Sharpe=-0.5135)
- Admission: Train IC=+0.2186, Deflated=+0.2190, IR=0.70, Mono=0.77, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.079 | 2017: +0.045 | 2018: +0.207 | 2019: +0.081 | 2020: -0.013 | 2021: +0.149 | 2022: +0.052 | 2023: +0.169 | 2024: +0.024 | 2025: +0.098 | 2026: -0.107
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.080 | 2017: +0.130 | 2018: +0.378 | 2019: +0.123 | 2020: +0.093 | 2021: +0.426 | 2022: +0.289 | 2023: +0.280 | 2024: +0.222 | 2025: +0.176 | 2026: -0.085
- IC CV=0.81, Neg years (linear/tail)=1/0 of 8, Half ratio=1.27, Recency ratio=0.77
- Early IC=+0.1261, Recent IC=+0.0969, 1st-half IC=+0.0835, 2nd-half IC=+0.1060, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.117, Q3_mid=+0.049, Q4=+0.070, Q5_high_vol=+0.162

**`combo_max__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0165, Sharpe=-0.6040)
- Admission: Train IC=+0.2151, Deflated=+0.2155, IR=0.65, Mono=0.75, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.110 | 2017: +0.049 | 2018: +0.194 | 2019: +0.095 | 2020: +0.006 | 2021: +0.141 | 2022: +0.040 | 2023: +0.143 | 2024: +0.029 | 2025: +0.075 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.101 | 2016: +0.069 | 2017: +0.079 | 2018: +0.330 | 2019: +0.168 | 2020: +0.185 | 2021: +0.324 | 2022: +0.340 | 2023: +0.268 | 2024: +0.059 | 2025: +0.135 | 2026: -0.352
- IC CV=0.71, Neg years (linear/tail)=0/0 of 8, Half ratio=0.98, Recency ratio=0.71
- Early IC=+0.1217, Recent IC=+0.0860, 1st-half IC=+0.0921, 2nd-half IC=+0.0906, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.055, Q2=+0.099, Q3_mid=+0.047, Q4=+0.075, Q5_high_vol=+0.174

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0164, Sharpe=-0.3387)
- Admission: Train IC=+0.2260, Deflated=+0.2253, IR=0.58, Mono=0.72, p=0.0002, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.109 | 2017: -0.076 | 2018: +0.170 | 2019: +0.084 | 2020: +0.074 | 2021: +0.154 | 2022: +0.090 | 2023: +0.095 | 2024: +0.025 | 2025: +0.042 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.226 | 2017: -0.038 | 2018: +0.415 | 2019: +0.182 | 2020: +0.201 | 2021: +0.412 | 2022: +0.269 | 2023: +0.164 | 2024: +0.191 | 2025: +0.121 | 2026: +0.187
- IC CV=0.93, Neg years (linear/tail)=1/1 of 8, Half ratio=1.41, Recency ratio=1.28
- Early IC=+0.0471, Recent IC=+0.0601, 1st-half IC=+0.0712, 2nd-half IC=+0.1001, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.019, Q2=+0.043, Q3_mid=+0.028, Q4=+0.056, Q5_high_vol=+0.237

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.0158, Sharpe=-0.4533)
- Admission: Train IC=+0.2365, Deflated=+0.2367, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.099 | 2017: -0.039 | 2018: +0.161 | 2019: +0.126 | 2020: +0.068 | 2021: +0.115 | 2022: +0.040 | 2023: +0.128 | 2024: +0.032 | 2025: +0.050 | 2026: -0.051
- Yearly Tail ICs:   2015: +0.476 | 2016: -0.076 | 2017: -0.108 | 2018: +0.238 | 2019: +0.304 | 2020: +0.298 | 2021: +0.332 | 2022: +0.276 | 2023: +0.120 | 2024: +0.256 | 2025: +0.096 | 2026: +0.122
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=1.31
- Early IC=+0.0611, Recent IC=+0.0798, 1st-half IC=+0.0846, 2nd-half IC=+0.0849, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.004, Q2=+0.048, Q3_mid=+0.067, Q4=+0.059, Q5_high_vol=+0.207

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0157, Sharpe=-0.4533)
- Admission: Train IC=+0.2366, Deflated=+0.2368, IR=0.52, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.099 | 2017: -0.039 | 2018: +0.161 | 2019: +0.126 | 2020: +0.067 | 2021: +0.115 | 2022: +0.040 | 2023: +0.128 | 2024: +0.032 | 2025: +0.050 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.474 | 2016: -0.076 | 2017: -0.108 | 2018: +0.238 | 2019: +0.304 | 2020: +0.299 | 2021: +0.333 | 2022: +0.276 | 2023: +0.120 | 2024: +0.256 | 2025: +0.096 | 2026: +0.122
- IC CV=0.78, Neg years (linear/tail)=1/1 of 8, Half ratio=1.00, Recency ratio=1.31
- Early IC=+0.0610, Recent IC=+0.0798, 1st-half IC=+0.0846, 2nd-half IC=+0.0849, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.004, Q2=+0.048, Q3_mid=+0.067, Q4=+0.059, Q5_high_vol=+0.207

**`combo_rank_max__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0141, Sharpe=-0.7061)
- Admission: Train IC=+0.2026, Deflated=+0.2032, IR=0.54, Mono=0.71, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.112 | 2017: +0.050 | 2018: +0.194 | 2019: +0.090 | 2020: -0.007 | 2021: +0.146 | 2022: +0.043 | 2023: +0.154 | 2024: +0.036 | 2025: +0.076 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.072 | 2017: +0.038 | 2018: +0.334 | 2019: +0.170 | 2020: +0.024 | 2021: +0.343 | 2022: +0.299 | 2023: +0.322 | 2024: +0.032 | 2025: +0.142 | 2026: -0.377
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=1.11, Recency ratio=0.77
- Early IC=+0.1222, Recent IC=+0.0938, 1st-half IC=+0.0876, 2nd-half IC=+0.0969, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.093, Q3_mid=+0.050, Q4=+0.081, Q5_high_vol=+0.172

**`combo_rank_max__first_bar_return__volume_surge_direction`** (Lock IC=+0.0136, Sharpe=-0.1774)
- Admission: Train IC=+0.2246, Deflated=+0.2232, IR=0.72, Mono=0.78, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.088 | 2017: -0.004 | 2018: +0.200 | 2019: +0.144 | 2020: -0.006 | 2021: +0.039 | 2022: +0.045 | 2023: +0.168 | 2024: +0.026 | 2025: +0.074 | 2026: -0.086
- Yearly Tail ICs:   2015: +0.106 | 2016: -0.026 | 2017: -0.012 | 2018: +0.400 | 2019: +0.299 | 2020: +0.128 | 2021: -0.029 | 2022: +0.239 | 2023: +0.143 | 2024: +0.330 | 2025: +0.362 | 2026: -0.010
- IC CV=0.98, Neg years (linear/tail)=1/1 of 8, Half ratio=0.78, Recency ratio=0.93
- Early IC=+0.1049, Recent IC=+0.0977, 1st-half IC=+0.0858, 2nd-half IC=+0.0673, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.087, Q3_mid=+0.031, Q4=+0.073, Q5_high_vol=+0.124

**`combo_tri_median__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio`** (Lock IC=+0.0135, Sharpe=-0.4840)
- Admission: Train IC=+0.2014, Deflated=+0.2010, IR=0.51, Mono=0.72, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.110 | 2017: -0.021 | 2018: +0.216 | 2019: +0.135 | 2020: +0.027 | 2021: +0.128 | 2022: +0.058 | 2023: +0.171 | 2024: +0.053 | 2025: +0.061 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.082 | 2016: +0.094 | 2017: +0.028 | 2018: +0.265 | 2019: +0.260 | 2020: +0.284 | 2021: +0.224 | 2022: +0.183 | 2023: +0.203 | 2024: +0.272 | 2025: +0.136 | 2026: -0.001
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=1.15
- Early IC=+0.0976, Recent IC=+0.1120, 1st-half IC=+0.0983, 2nd-half IC=+0.1083, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.087, Q3_mid=+0.065, Q4=+0.046, Q5_high_vol=+0.249

**`combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=+0.0133, Sharpe=-0.4840)
- Admission: Train IC=+0.2012, Deflated=+0.2009, IR=0.51, Mono=0.72, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.122 | 2016: +0.110 | 2017: -0.021 | 2018: +0.216 | 2019: +0.135 | 2020: +0.028 | 2021: +0.128 | 2022: +0.058 | 2023: +0.171 | 2024: +0.053 | 2025: +0.061 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.083 | 2016: +0.092 | 2017: +0.028 | 2018: +0.265 | 2019: +0.260 | 2020: +0.284 | 2021: +0.226 | 2022: +0.183 | 2023: +0.205 | 2024: +0.272 | 2025: +0.136 | 2026: -0.001
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=1.15
- Early IC=+0.0974, Recent IC=+0.1122, 1st-half IC=+0.0984, 2nd-half IC=+0.1084, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.087, Q3_mid=+0.065, Q4=+0.046, Q5_high_vol=+0.249

**`combo_min__max_up_ret__volume_surge_direction`** (Lock IC=+0.0128, Sharpe=-0.5403)
- Admission: Train IC=+0.1881, Deflated=+0.1872, IR=0.45, Mono=0.65, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.074 | 2016: +0.084 | 2017: -0.021 | 2018: +0.188 | 2019: +0.065 | 2020: +0.069 | 2021: +0.132 | 2022: +0.044 | 2023: +0.152 | 2024: +0.030 | 2025: +0.067 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.264 | 2016: -0.174 | 2017: -0.065 | 2018: +0.296 | 2019: +0.115 | 2020: +0.343 | 2021: +0.254 | 2022: +0.002 | 2023: +0.395 | 2024: +0.228 | 2025: +0.186 | 2026: -0.210
- IC CV=0.79, Neg years (linear/tail)=1/1 of 8, Half ratio=1.32, Recency ratio=1.09
- Early IC=+0.0832, Recent IC=+0.0911, 1st-half IC=+0.0725, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.109, Q3_mid=+0.020, Q4=+0.085, Q5_high_vol=+0.156

**`combo_mean__volume_weighted_price_position__first_bar_sentiment`** (Lock IC=+0.0123, Sharpe=-0.5499)
- Admission: Train IC=+0.1745, Deflated=+0.1740, IR=0.60, Mono=0.76, p=0.0008, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.072 | 2017: +0.002 | 2018: +0.198 | 2019: +0.092 | 2020: -0.039 | 2021: +0.159 | 2022: +0.074 | 2023: +0.177 | 2024: -0.033 | 2025: +0.100 | 2026: -0.128
- Yearly Tail ICs:   2015: -0.006 | 2016: -0.028 | 2017: +0.170 | 2018: +0.289 | 2019: +0.160 | 2020: -0.029 | 2021: +0.381 | 2022: +0.330 | 2023: +0.260 | 2024: +0.048 | 2025: +0.202 | 2026: -0.163
- IC CV=1.12, Neg years (linear/tail)=2/1 of 8, Half ratio=1.53, Recency ratio=0.72
- Early IC=+0.1001, Recent IC=+0.0722, 1st-half IC=+0.0659, 2nd-half IC=+0.1009, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.060, Q2=+0.124, Q3_mid=+0.028, Q4=+0.088, Q5_high_vol=+0.108

**`combo_mean__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0113, Sharpe=-0.6406)
- Admission: Train IC=+0.2284, Deflated=+0.2274, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.070 | 2017: -0.041 | 2018: +0.206 | 2019: +0.114 | 2020: +0.040 | 2021: +0.139 | 2022: +0.040 | 2023: +0.173 | 2024: +0.028 | 2025: +0.099 | 2026: -0.119
- Yearly Tail ICs:   2015: -0.007 | 2016: -0.064 | 2017: -0.033 | 2018: +0.294 | 2019: +0.090 | 2020: +0.203 | 2021: +0.387 | 2022: +0.124 | 2023: +0.333 | 2024: +0.324 | 2025: +0.252 | 2026: -0.245
- IC CV=0.90, Neg years (linear/tail)=1/1 of 8, Half ratio=1.18, Recency ratio=1.21
- Early IC=+0.0828, Recent IC=+0.1004, 1st-half IC=+0.0858, 2nd-half IC=+0.1010, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.015, Q2=+0.115, Q3_mid=+0.037, Q4=+0.078, Q5_high_vol=+0.186

**`combo_max__first_bar_return__volume_surge_direction`** (Lock IC=+0.0104, Sharpe=-0.1272)
- Admission: Train IC=+0.2280, Deflated=+0.2267, IR=0.70, Mono=0.77, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.104 | 2016: +0.086 | 2017: -0.009 | 2018: +0.199 | 2019: +0.145 | 2020: -0.004 | 2021: +0.043 | 2022: +0.048 | 2023: +0.168 | 2024: +0.026 | 2025: +0.075 | 2026: -0.087
- Yearly Tail ICs:   2015: +0.154 | 2016: -0.018 | 2017: -0.017 | 2018: +0.420 | 2019: +0.331 | 2020: +0.160 | 2021: +0.014 | 2022: +0.275 | 2023: +0.180 | 2024: +0.305 | 2025: +0.339 | 2026: -0.101
- IC CV=0.99, Neg years (linear/tail)=2/1 of 8, Half ratio=0.80, Recency ratio=1.03
- Early IC=+0.0946, Recent IC=+0.0971, 1st-half IC=+0.0878, 2nd-half IC=+0.0701, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.050, Q2=+0.093, Q3_mid=+0.046, Q4=+0.076, Q5_high_vol=+0.128

**`combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0098, Sharpe=-1.6517)
- Admission: Train IC=+0.1910, Deflated=+0.1915, IR=0.53, Mono=0.70, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.071 | 2016: +0.048 | 2017: +0.006 | 2018: +0.230 | 2019: +0.066 | 2020: -0.007 | 2021: +0.177 | 2022: +0.034 | 2023: +0.175 | 2024: +0.002 | 2025: +0.117 | 2026: -0.152
- Yearly Tail ICs:   2015: +0.062 | 2016: +0.071 | 2017: -0.065 | 2018: +0.212 | 2019: +0.322 | 2020: +0.079 | 2021: +0.452 | 2022: +0.290 | 2023: +0.380 | 2024: -0.075 | 2025: +0.093 | 2026: -0.005
- IC CV=1.03, Neg years (linear/tail)=1/2 of 8, Half ratio=1.43, Recency ratio=0.76
- Early IC=+0.1175, Recent IC=+0.0891, 1st-half IC=+0.0731, 2nd-half IC=+0.1048, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.122, Q3_mid=+0.067, Q4=+0.058, Q5_high_vol=+0.144

**`combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0073, Sharpe=-0.4890)
- Admission: Train IC=+0.2219, Deflated=+0.2221, IR=0.68, Mono=0.78, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.118 | 2016: +0.100 | 2017: -0.006 | 2018: +0.213 | 2019: +0.078 | 2020: -0.003 | 2021: +0.124 | 2022: +0.062 | 2023: +0.162 | 2024: +0.028 | 2025: +0.087 | 2026: -0.097
- Yearly Tail ICs:   2015: +0.059 | 2016: -0.108 | 2017: +0.131 | 2018: +0.153 | 2019: +0.204 | 2020: +0.086 | 2021: +0.327 | 2022: +0.364 | 2023: +0.375 | 2024: +0.189 | 2025: +0.046 | 2026: -0.125
- IC CV=0.90, Neg years (linear/tail)=2/0 of 8, Half ratio=1.31, Recency ratio=0.92
- Early IC=+0.1036, Recent IC=+0.0951, 1st-half IC=+0.0777, 2nd-half IC=+0.1018, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.042, Q2=+0.097, Q3_mid=+0.062, Q4=+0.071, Q5_high_vol=+0.154

**`combo_min__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0057, Sharpe=-0.5935)
- Admission: Train IC=+0.1923, Deflated=+0.1926, IR=0.63, Mono=0.74, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.080 | 2017: +0.059 | 2018: +0.188 | 2019: +0.080 | 2020: +0.007 | 2021: +0.134 | 2022: +0.035 | 2023: +0.147 | 2024: +0.045 | 2025: +0.054 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.243 | 2016: -0.126 | 2017: +0.040 | 2018: +0.192 | 2019: +0.116 | 2020: +0.076 | 2021: +0.303 | 2022: +0.293 | 2023: +0.251 | 2024: +0.261 | 2025: +0.119 | 2026: -0.052
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=1.12, Recency ratio=0.77
- Early IC=+0.1239, Recent IC=+0.0959, 1st-half IC=+0.0844, 2nd-half IC=+0.0945, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.087, Q3_mid=+0.053, Q4=+0.067, Q5_high_vol=+0.164

**`combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0053, Sharpe=-0.2216)
- Admission: Train IC=+0.2028, Deflated=+0.2027, IR=0.65, Mono=0.78, p=0.0002, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.126 | 2016: +0.091 | 2017: +0.054 | 2018: +0.208 | 2019: +0.097 | 2020: +0.002 | 2021: +0.136 | 2022: +0.043 | 2023: +0.141 | 2024: +0.034 | 2025: +0.049 | 2026: -0.053
- Yearly Tail ICs:   2015: +0.180 | 2016: -0.020 | 2017: +0.011 | 2018: +0.269 | 2019: +0.163 | 2020: +0.199 | 2021: +0.342 | 2022: +0.270 | 2023: +0.359 | 2024: +0.109 | 2025: +0.057 | 2026: -0.031
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.67
- Early IC=+0.1310, Recent IC=+0.0878, 1st-half IC=+0.0903, 2nd-half IC=+0.0911, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.061, Q2=+0.085, Q3_mid=+0.050, Q4=+0.076, Q5_high_vol=+0.177

**`combo_rank_min__max_up_ret__volume_surge_direction`** (Lock IC=+0.0051, Sharpe=-0.7221)
- Admission: Train IC=+0.2000, Deflated=+0.1994, IR=0.44, Mono=0.68, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.080 | 2017: -0.027 | 2018: +0.184 | 2019: +0.070 | 2020: +0.069 | 2021: +0.146 | 2022: +0.042 | 2023: +0.146 | 2024: +0.031 | 2025: +0.061 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.181 | 2016: -0.163 | 2017: -0.084 | 2018: +0.190 | 2019: +0.187 | 2020: +0.323 | 2021: +0.341 | 2022: +0.033 | 2023: +0.347 | 2024: +0.226 | 2025: +0.066 | 2026: -0.286
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=1.40, Recency ratio=1.21
- Early IC=+0.0709, Recent IC=+0.0857, 1st-half IC=+0.0665, 2nd-half IC=+0.0930, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.111, Q3_mid=+0.022, Q4=+0.083, Q5_high_vol=+0.150

**`combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0044, Sharpe=-0.9717)
- Admission: Train IC=+0.1995, Deflated=+0.1997, IR=0.52, Mono=0.68, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.098 | 2017: -0.003 | 2018: +0.221 | 2019: +0.077 | 2020: +0.007 | 2021: +0.166 | 2022: +0.036 | 2023: +0.152 | 2024: +0.039 | 2025: +0.071 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.034 | 2016: +0.182 | 2017: -0.104 | 2018: +0.330 | 2019: +0.176 | 2020: +0.076 | 2021: +0.474 | 2022: +0.096 | 2023: +0.285 | 2024: +0.027 | 2025: +0.121 | 2026: -0.130
- IC CV=0.89, Neg years (linear/tail)=1/1 of 8, Half ratio=1.27, Recency ratio=0.87
- Early IC=+0.1094, Recent IC=+0.0951, 1st-half IC=+0.0813, 2nd-half IC=+0.1036, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.93)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.092, Q3_mid=+0.037, Q4=+0.068, Q5_high_vol=+0.211

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0037, Sharpe=-1.3784)
- Admission: Train IC=+0.2221, Deflated=+0.2231, IR=0.61, Mono=0.73, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.094 | 2016: +0.075 | 2017: +0.066 | 2018: +0.202 | 2019: +0.059 | 2020: -0.012 | 2021: +0.169 | 2022: +0.057 | 2023: +0.177 | 2024: +0.011 | 2025: +0.100 | 2026: -0.148
- Yearly Tail ICs:   2015: +0.131 | 2016: -0.019 | 2017: +0.161 | 2018: +0.513 | 2019: +0.186 | 2020: +0.218 | 2021: +0.351 | 2022: +0.216 | 2023: +0.213 | 2024: +0.118 | 2025: +0.197 | 2026: -0.330
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.38, Recency ratio=0.70
- Early IC=+0.1339, Recent IC=+0.0940, 1st-half IC=+0.0772, 2nd-half IC=+0.1068, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.122, Q3_mid=+0.052, Q4=+0.053, Q5_high_vol=+0.148

**`combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0025, Sharpe=-1.0214)
- Admission: Train IC=+0.1816, Deflated=+0.1821, IR=0.62, Mono=0.75, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.090 | 2017: +0.012 | 2018: +0.147 | 2019: +0.063 | 2020: +0.046 | 2021: +0.196 | 2022: +0.023 | 2023: +0.190 | 2024: +0.059 | 2025: +0.092 | 2026: -0.140
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.053 | 2017: -0.087 | 2018: +0.276 | 2019: +0.137 | 2020: +0.066 | 2021: +0.419 | 2022: +0.194 | 2023: +0.379 | 2024: +0.194 | 2025: +0.060 | 2026: -0.338
- IC CV=0.75, Neg years (linear/tail)=0/1 of 8, Half ratio=1.80, Recency ratio=1.56
- Early IC=+0.0797, Recent IC=+0.1244, 1st-half IC=+0.0695, 2nd-half IC=+0.1252, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.94)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.104, Q3_mid=+0.049, Q4=+0.051, Q5_high_vol=+0.214

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0008, Sharpe=-1.2659)
- Admission: Train IC=+0.2456, Deflated=+0.2452, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.137 | 2016: +0.093 | 2017: -0.047 | 2018: +0.181 | 2019: +0.105 | 2020: +0.022 | 2021: +0.171 | 2022: +0.057 | 2023: +0.174 | 2024: +0.055 | 2025: +0.066 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.076 | 2017: -0.014 | 2018: +0.199 | 2019: +0.257 | 2020: +0.078 | 2021: +0.423 | 2022: +0.414 | 2023: +0.226 | 2024: +0.300 | 2025: +0.021 | 2026: -0.023
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=1.72, Recency ratio=1.71
- Early IC=+0.0671, Recent IC=+0.1149, 1st-half IC=+0.0704, 2nd-half IC=+0.1209, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.065, Q3_mid=+0.056, Q4=+0.066, Q5_high_vol=+0.218

**`first_bar_return`** (Lock IC=+0.0007, Sharpe=-0.8124)
- Admission: Train IC=+0.1925, Deflated=+0.1926, IR=0.65, Mono=0.75, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.095 | 2017: +0.061 | 2018: +0.191 | 2019: +0.095 | 2020: +0.014 | 2021: +0.121 | 2022: +0.040 | 2023: +0.142 | 2024: +0.029 | 2025: +0.055 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.198 | 2016: -0.089 | 2017: +0.049 | 2018: +0.237 | 2019: +0.141 | 2020: +0.237 | 2021: +0.277 | 2022: +0.340 | 2023: +0.278 | 2024: +0.201 | 2025: +0.144 | 2026: -0.129
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.68
- Early IC=+0.1260, Recent IC=+0.0855, 1st-half IC=+0.0904, 2nd-half IC=+0.0844, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.091, Q3_mid=+0.045, Q4=+0.070, Q5_high_vol=+0.164

**`combo_mean__first_bar_return__first_bar_sentiment`** (Lock IC=+0.0007, Sharpe=-0.8124)
- Admission: Train IC=+0.1925, Deflated=+0.1926, IR=0.65, Mono=0.75, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.095 | 2017: +0.061 | 2018: +0.191 | 2019: +0.095 | 2020: +0.014 | 2021: +0.121 | 2022: +0.040 | 2023: +0.142 | 2024: +0.029 | 2025: +0.055 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.198 | 2016: -0.089 | 2017: +0.049 | 2018: +0.237 | 2019: +0.141 | 2020: +0.237 | 2021: +0.277 | 2022: +0.340 | 2023: +0.278 | 2024: +0.201 | 2025: +0.144 | 2026: -0.129
- IC CV=0.67, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.68
- Early IC=+0.1260, Recent IC=+0.0855, 1st-half IC=+0.0904, 2nd-half IC=+0.0844, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=1.06)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.091, Q3_mid=+0.045, Q4=+0.070, Q5_high_vol=+0.164

**`combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0006, Sharpe=-0.8981)
- Admission: Train IC=+0.1647, Deflated=+0.1656, IR=0.66, Mono=0.74, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.071 | 2017: +0.038 | 2018: +0.172 | 2019: +0.062 | 2020: -0.006 | 2021: +0.183 | 2022: +0.053 | 2023: +0.189 | 2024: +0.025 | 2025: +0.111 | 2026: -0.168
- Yearly Tail ICs:   2015: +0.169 | 2016: -0.067 | 2017: +0.157 | 2018: +0.350 | 2019: +0.073 | 2020: -0.002 | 2021: +0.369 | 2022: +0.191 | 2023: +0.254 | 2024: +0.203 | 2025: +0.245 | 2026: -0.161
- IC CV=0.82, Neg years (linear/tail)=1/1 of 8, Half ratio=1.75, Recency ratio=1.02
- Early IC=+0.1052, Recent IC=+0.1069, 1st-half IC=+0.0674, 2nd-half IC=+0.1182, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.106, Q3_mid=+0.060, Q4=+0.047, Q5_high_vol=+0.181

**`volume_weighted_price_position`** (Lock IC=+0.0000, Sharpe=-0.4047)
- Admission: Train IC=+0.1777, Deflated=+0.1783, IR=0.63, Mono=0.75, p=0.0008, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.074 | 2016: +0.014 | 2017: +0.013 | 2018: +0.181 | 2019: +0.043 | 2020: -0.059 | 2021: +0.154 | 2022: +0.076 | 2023: +0.195 | 2024: -0.023 | 2025: +0.108 | 2026: -0.160
- Yearly Tail ICs:   2015: +0.027 | 2016: -0.028 | 2017: +0.211 | 2018: +0.239 | 2019: +0.155 | 2020: -0.026 | 2021: +0.394 | 2022: +0.342 | 2023: +0.295 | 2024: +0.041 | 2025: +0.227 | 2026: -0.163
- IC CV=1.24, Neg years (linear/tail)=2/1 of 8, Half ratio=2.38, Recency ratio=0.88
- Early IC=+0.0972, Recent IC=+0.0857, 1st-half IC=+0.0446, 2nd-half IC=+0.1062, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.122, Q3_mid=+0.033, Q4=+0.066, Q5_high_vol=+0.084

### 500ETF — `single` Median Features

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1108, Sharpe=-0.1710)
- Admission: Train IC=+0.2482, Deflated=+0.2466, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.118 | 2017: +0.214 | 2018: +0.168 | 2019: +0.109 | 2020: +0.157 | 2021: +0.077 | 2022: +0.099 | 2023: +0.075 | 2024: +0.106 | 2025: +0.131 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.163 | 2016: +0.213 | 2017: +0.258 | 2018: +0.308 | 2019: +0.376 | 2020: +0.141 | 2021: +0.178 | 2022: +0.256 | 2023: +0.140 | 2024: +0.260 | 2025: +0.075 | 2026: +0.166
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.47
- Early IC=+0.1912, Recent IC=+0.0905, 1st-half IC=+0.1532, 2nd-half IC=+0.0942, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.022, Q3_mid=+0.090, Q4=+0.112, Q5_high_vol=+0.177

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1051, Sharpe=-0.1201)
- Admission: Train IC=+0.2432, Deflated=+0.2416, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.088 | 2017: +0.203 | 2018: +0.109 | 2019: +0.104 | 2020: +0.126 | 2021: +0.059 | 2022: +0.080 | 2023: +0.061 | 2024: +0.114 | 2025: +0.113 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.193 | 2017: +0.302 | 2018: +0.272 | 2019: +0.323 | 2020: +0.210 | 2021: +0.203 | 2022: +0.234 | 2023: +0.012 | 2024: +0.264 | 2025: +0.078 | 2026: +0.031
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.56
- Early IC=+0.1560, Recent IC=+0.0873, 1st-half IC=+0.1245, 2nd-half IC=+0.0855, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.015, Q3_mid=+0.082, Q4=+0.099, Q5_high_vol=+0.127

**`combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1001, Sharpe=-0.0297)
- Admission: Train IC=+0.2246, Deflated=+0.2231, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.109 | 2017: +0.225 | 2018: +0.117 | 2019: +0.097 | 2020: +0.129 | 2021: +0.092 | 2022: +0.098 | 2023: +0.107 | 2024: +0.103 | 2025: +0.141 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.246 | 2017: +0.218 | 2018: +0.334 | 2019: +0.149 | 2020: +0.315 | 2021: +0.131 | 2022: +0.130 | 2023: +0.065 | 2024: +0.312 | 2025: +0.181 | 2026: +0.167
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.62
- Early IC=+0.1709, Recent IC=+0.1052, 1st-half IC=+0.1242, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.011, Q3_mid=+0.097, Q4=+0.113, Q5_high_vol=+0.141

**`combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0988, Sharpe=-0.3635)
- Admission: Train IC=+0.2016, Deflated=+0.2004, IR=0.67, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.069 | 2017: +0.208 | 2018: +0.142 | 2019: +0.115 | 2020: +0.108 | 2021: +0.020 | 2022: +0.149 | 2023: +0.073 | 2024: +0.106 | 2025: +0.127 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.188 | 2016: -0.046 | 2017: +0.199 | 2018: +0.129 | 2019: +0.273 | 2020: +0.064 | 2021: +0.207 | 2022: +0.324 | 2023: +0.148 | 2024: +0.159 | 2025: +0.155 | 2026: -0.334
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.51
- Early IC=+0.1740, Recent IC=+0.0892, 1st-half IC=+0.1352, 2nd-half IC=+0.0943, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.037, Q3_mid=+0.095, Q4=+0.115, Q5_high_vol=+0.132

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0950, Sharpe=-0.0776)
- Admission: Train IC=+0.2668, Deflated=+0.2654, IR=0.85, Mono=0.82, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.090 | 2017: +0.240 | 2018: +0.181 | 2019: +0.128 | 2020: +0.172 | 2021: +0.100 | 2022: +0.076 | 2023: +0.077 | 2024: +0.135 | 2025: +0.116 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.143 | 2017: +0.232 | 2018: +0.322 | 2019: +0.417 | 2020: +0.148 | 2021: +0.225 | 2022: +0.284 | 2023: +0.145 | 2024: +0.244 | 2025: +0.101 | 2026: +0.058
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.50
- Early IC=+0.2105, Recent IC=+0.1062, 1st-half IC=+0.1693, 2nd-half IC=+0.1051, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.018, Q3_mid=+0.117, Q4=+0.131, Q5_high_vol=+0.195

**`combo_sig_product__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0944, Sharpe=-0.6509)
- Admission: Train IC=+0.2134, Deflated=+0.2111, IR=0.55, Mono=0.67, p=0.0000, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.010 | 2017: +0.222 | 2018: +0.023 | 2019: +0.090 | 2020: +0.095 | 2021: +0.070 | 2022: +0.079 | 2023: +0.096 | 2024: +0.156 | 2025: +0.085 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.023 | 2016: +0.037 | 2017: +0.423 | 2018: +0.100 | 2019: +0.245 | 2020: +0.213 | 2021: +0.172 | 2022: +0.031 | 2023: +0.098 | 2024: +0.232 | 2025: +0.009 | 2026: +0.086
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=1.03
- Early IC=+0.1228, Recent IC=+0.1261, 1st-half IC=+0.0984, 2nd-half IC=+0.1078, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.070, Q3_mid=+0.087, Q4=+0.121, Q5_high_vol=+0.082

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.0942, Sharpe=-0.2127)
- Admission: Train IC=+0.2523, Deflated=+0.2504, IR=0.98, Mono=0.84, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.128 | 2017: +0.198 | 2018: +0.224 | 2019: +0.118 | 2020: +0.165 | 2021: +0.115 | 2022: +0.116 | 2023: +0.081 | 2024: +0.107 | 2025: +0.128 | 2026: +0.060
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.250 | 2017: +0.233 | 2018: +0.429 | 2019: +0.250 | 2020: +0.222 | 2021: +0.206 | 2022: +0.268 | 2023: +0.151 | 2024: +0.215 | 2025: -0.102 | 2026: +0.032
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.45
- Early IC=+0.2107, Recent IC=+0.0940, 1st-half IC=+0.1704, 2nd-half IC=+0.1080, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.020, Q3_mid=+0.098, Q4=+0.148, Q5_high_vol=+0.204

**`combo_rank_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0938, Sharpe=-0.4554)
- Admission: Train IC=+0.1908, Deflated=+0.1895, IR=0.66, Mono=0.76, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.068 | 2017: +0.194 | 2018: +0.126 | 2019: +0.122 | 2020: +0.097 | 2021: +0.015 | 2022: +0.143 | 2023: +0.065 | 2024: +0.111 | 2025: +0.106 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.113 | 2016: +0.194 | 2017: +0.158 | 2018: +0.069 | 2019: +0.328 | 2020: +0.085 | 2021: +0.148 | 2022: +0.263 | 2023: +0.060 | 2024: +0.229 | 2025: -0.056 | 2026: -0.138
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.54
- Early IC=+0.1596, Recent IC=+0.0868, 1st-half IC=+0.1263, 2nd-half IC=+0.0922, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.034, Q3_mid=+0.101, Q4=+0.112, Q5_high_vol=+0.110

**`combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0937, Sharpe=-0.1678)
- Admission: Train IC=+0.1662, Deflated=+0.1648, IR=0.51, Mono=0.69, p=0.0012, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.311 | 2016: +0.097 | 2017: +0.255 | 2018: +0.117 | 2019: +0.122 | 2020: +0.160 | 2021: +0.066 | 2022: +0.118 | 2023: +0.042 | 2024: +0.108 | 2025: +0.096 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.185 | 2017: +0.205 | 2018: +0.103 | 2019: +0.246 | 2020: +0.141 | 2021: +0.091 | 2022: +0.228 | 2023: +0.020 | 2024: +0.083 | 2025: +0.034 | 2026: -0.040
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.40
- Early IC=+0.1860, Recent IC=+0.0747, 1st-half IC=+0.1557, 2nd-half IC=+0.0918, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.025, Q3_mid=+0.104, Q4=+0.127, Q5_high_vol=+0.153

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0933, Sharpe=-0.2396)
- Admission: Train IC=+0.2385, Deflated=+0.2369, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.125 | 2017: +0.152 | 2018: +0.158 | 2019: +0.096 | 2020: +0.139 | 2021: +0.058 | 2022: +0.126 | 2023: +0.073 | 2024: +0.090 | 2025: +0.110 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.233 | 2016: +0.265 | 2017: +0.234 | 2018: +0.351 | 2019: +0.286 | 2020: +0.171 | 2021: +0.124 | 2022: +0.256 | 2023: +0.184 | 2024: +0.182 | 2025: +0.111 | 2026: +0.113
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.52
- Early IC=+0.1549, Recent IC=+0.0812, 1st-half IC=+0.1349, 2nd-half IC=+0.0919, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.031, Q3_mid=+0.082, Q4=+0.112, Q5_high_vol=+0.155

**`combo_max__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.0923, Sharpe=-0.6750)
- Admission: Train IC=+0.1758, Deflated=+0.1744, IR=0.60, Mono=0.74, p=0.0004, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.277 | 2016: +0.071 | 2017: +0.198 | 2018: +0.122 | 2019: +0.120 | 2020: +0.114 | 2021: +0.019 | 2022: +0.127 | 2023: +0.054 | 2024: +0.101 | 2025: +0.111 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.124 | 2017: +0.174 | 2018: +0.089 | 2019: +0.262 | 2020: +0.089 | 2021: +0.102 | 2022: +0.288 | 2023: +0.058 | 2024: +0.223 | 2025: +0.011 | 2026: -0.111
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.48
- Early IC=+0.1601, Recent IC=+0.0774, 1st-half IC=+0.1298, 2nd-half IC=+0.0850, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.028, Q3_mid=+0.098, Q4=+0.109, Q5_high_vol=+0.113

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0883, Sharpe=-0.5698)
- Admission: Train IC=+0.2689, Deflated=+0.2675, IR=1.07, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.123 | 2017: +0.222 | 2018: +0.178 | 2019: +0.172 | 2020: +0.171 | 2021: +0.141 | 2022: +0.008 | 2023: +0.106 | 2024: +0.163 | 2025: +0.094 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.247 | 2017: +0.328 | 2018: +0.514 | 2019: +0.346 | 2020: +0.235 | 2021: +0.278 | 2022: +0.140 | 2023: +0.112 | 2024: +0.297 | 2025: -0.002 | 2026: +0.151
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.67
- Early IC=+0.2002, Recent IC=+0.1341, 1st-half IC=+0.1783, 2nd-half IC=+0.1107, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.005, Q3_mid=+0.122, Q4=+0.123, Q5_high_vol=+0.235

**`combo_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0883, Sharpe=-0.0326)
- Admission: Train IC=+0.2027, Deflated=+0.2025, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.059 | 2017: +0.223 | 2018: +0.127 | 2019: +0.101 | 2020: +0.128 | 2021: +0.063 | 2022: +0.081 | 2023: +0.080 | 2024: +0.116 | 2025: +0.143 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.324 | 2016: -0.050 | 2017: +0.227 | 2018: +0.096 | 2019: +0.298 | 2020: +0.092 | 2021: +0.402 | 2022: +0.228 | 2023: +0.235 | 2024: +0.264 | 2025: +0.180 | 2026: +0.056
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.56
- Early IC=+0.1752, Recent IC=+0.0982, 1st-half IC=+0.1280, 2nd-half IC=+0.0938, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.198, Q2=-0.002, Q3_mid=+0.141, Q4=+0.103, Q5_high_vol=+0.128

**`combo_rank_max__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.0857, Sharpe=-0.3128)
- Admission: Train IC=+0.1642, Deflated=+0.1626, IR=0.54, Mono=0.69, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.123 | 2017: +0.161 | 2018: +0.175 | 2019: +0.116 | 2020: +0.116 | 2021: +0.048 | 2022: +0.142 | 2023: +0.083 | 2024: +0.110 | 2025: +0.084 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.120 | 2016: +0.393 | 2017: +0.202 | 2018: +0.137 | 2019: +0.158 | 2020: +0.077 | 2021: +0.213 | 2022: +0.163 | 2023: +0.119 | 2024: +0.208 | 2025: +0.027 | 2026: -0.205
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.57
- Early IC=+0.1695, Recent IC=+0.0972, 1st-half IC=+0.1381, 2nd-half IC=+0.1059, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.043, Q3_mid=+0.092, Q4=+0.133, Q5_high_vol=+0.146

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.0849, Sharpe=-0.1619)
- Admission: Train IC=+0.2897, Deflated=+0.2885, IR=1.10, Mono=0.85, p=0.0000, MaxCorr=0.64
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.106 | 2017: +0.204 | 2018: +0.139 | 2019: +0.132 | 2020: +0.154 | 2021: +0.155 | 2022: +0.078 | 2023: +0.108 | 2024: +0.134 | 2025: +0.118 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.238 | 2017: +0.235 | 2018: +0.365 | 2019: +0.237 | 2020: +0.309 | 2021: +0.222 | 2022: +0.245 | 2023: +0.248 | 2024: +0.405 | 2025: +0.085 | 2026: +0.257
- IC CV=0.25, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.71
- Early IC=+0.1712, Recent IC=+0.1209, 1st-half IC=+0.1428, 2nd-half IC=+0.1188, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.012, Q3_mid=+0.107, Q4=+0.132, Q5_high_vol=+0.177

**`combo_sig_product__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0838, Sharpe=-0.6184)
- Admission: Train IC=+0.1802, Deflated=+0.1784, IR=0.43, Mono=0.68, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.044 | 2017: +0.211 | 2018: +0.064 | 2019: +0.056 | 2020: +0.094 | 2021: +0.080 | 2022: +0.057 | 2023: +0.079 | 2024: +0.167 | 2025: +0.079 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.106 | 2016: +0.010 | 2017: +0.218 | 2018: +0.090 | 2019: +0.144 | 2020: +0.227 | 2021: +0.094 | 2022: +0.056 | 2023: +0.227 | 2024: +0.219 | 2025: -0.035 | 2026: +0.049
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=0.90
- Early IC=+0.1371, Recent IC=+0.1231, 1st-half IC=+0.0980, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.169, Q2=+0.060, Q3_mid=+0.076, Q4=+0.111, Q5_high_vol=+0.099

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0824, Sharpe=-0.6419)
- Admission: Train IC=+0.1257, Deflated=+0.1240, IR=0.55, Mono=0.69, p=0.0116, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.120 | 2017: +0.220 | 2018: +0.203 | 2019: +0.095 | 2020: +0.120 | 2021: +0.048 | 2022: +0.118 | 2023: +0.063 | 2024: +0.082 | 2025: +0.082 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.318 | 2017: +0.178 | 2018: +0.341 | 2019: +0.036 | 2020: +0.089 | 2021: +0.205 | 2022: +0.164 | 2023: +0.069 | 2024: +0.098 | 2025: -0.109 | 2026: -0.035
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.34
- Early IC=+0.2119, Recent IC=+0.0730, 1st-half IC=+0.1505, 2nd-half IC=+0.0870, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.191, Q2=+0.024, Q3_mid=+0.099, Q4=+0.118, Q5_high_vol=+0.160

**`combo_sig_product__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0813, Sharpe=-0.8506)
- Admission: Train IC=+0.1205, Deflated=+0.1201, IR=0.44, Mono=0.65, p=0.0150, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.046 | 2017: +0.229 | 2018: +0.131 | 2019: +0.126 | 2020: +0.190 | 2021: +0.108 | 2022: +0.019 | 2023: +0.089 | 2024: +0.118 | 2025: +0.135 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.193 | 2016: -0.045 | 2017: +0.225 | 2018: +0.047 | 2019: +0.246 | 2020: +0.043 | 2021: +0.325 | 2022: -0.023 | 2023: +0.131 | 2024: +0.267 | 2025: +0.261 | 2026: -0.109
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=0.57, Recency ratio=0.58
- Early IC=+0.1803, Recent IC=+0.1038, 1st-half IC=+0.1520, 2nd-half IC=+0.0865, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.013, Q3_mid=+0.172, Q4=+0.079, Q5_high_vol=+0.145

**`combo_rank_min__high_low_sequence_momentum__max_down_ret`** (Lock IC=+0.0812, Sharpe=-0.0721)
- Admission: Train IC=+0.2050, Deflated=+0.2050, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.077 | 2017: +0.241 | 2018: +0.134 | 2019: +0.083 | 2020: +0.145 | 2021: +0.045 | 2022: +0.087 | 2023: +0.071 | 2024: +0.121 | 2025: +0.131 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.332 | 2016: +0.015 | 2017: +0.270 | 2018: +0.123 | 2019: +0.118 | 2020: +0.163 | 2021: +0.343 | 2022: +0.263 | 2023: +0.166 | 2024: +0.221 | 2025: +0.136 | 2026: +0.048
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.50
- Early IC=+0.1874, Recent IC=+0.0945, 1st-half IC=+0.1301, 2nd-half IC=+0.0895, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.007, Q3_mid=+0.139, Q4=+0.113, Q5_high_vol=+0.130

**`combo_rank_min__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0801, Sharpe=-0.0633)
- Admission: Train IC=+0.2141, Deflated=+0.2140, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.077 | 2017: +0.236 | 2018: +0.132 | 2019: +0.097 | 2020: +0.142 | 2021: +0.054 | 2022: +0.084 | 2023: +0.081 | 2024: +0.112 | 2025: +0.135 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.285 | 2016: -0.076 | 2017: +0.295 | 2018: +0.113 | 2019: +0.263 | 2020: +0.207 | 2021: +0.349 | 2022: +0.282 | 2023: +0.266 | 2024: +0.142 | 2025: +0.162 | 2026: -0.067
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.1860, Recent IC=+0.0945, 1st-half IC=+0.1339, 2nd-half IC=+0.0910, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.003, Q3_mid=+0.136, Q4=+0.113, Q5_high_vol=+0.131

**`combo_min__close_vs_open_range__first_bar_return`** (Lock IC=+0.0798, Sharpe=-0.2027)
- Admission: Train IC=+0.2013, Deflated=+0.2013, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.085 | 2017: +0.187 | 2018: +0.165 | 2019: +0.114 | 2020: +0.067 | 2021: +0.058 | 2022: +0.051 | 2023: +0.078 | 2024: +0.137 | 2025: +0.143 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.366 | 2016: +0.181 | 2017: +0.298 | 2018: +0.326 | 2019: +0.147 | 2020: +0.089 | 2021: +0.247 | 2022: +0.188 | 2023: +0.156 | 2024: +0.217 | 2025: +0.213 | 2026: +0.186
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.61
- Early IC=+0.1764, Recent IC=+0.1074, 1st-half IC=+0.1223, 2nd-half IC=+0.0855, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.200, Q2=-0.019, Q3_mid=+0.082, Q4=+0.102, Q5_high_vol=+0.142

**`combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0756, Sharpe=-0.7698)
- Admission: Train IC=+0.1706, Deflated=+0.1696, IR=0.48, Mono=0.70, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.071 | 2017: +0.181 | 2018: +0.112 | 2019: +0.075 | 2020: +0.130 | 2021: +0.018 | 2022: +0.114 | 2023: +0.064 | 2024: +0.088 | 2025: +0.122 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.052 | 2016: +0.187 | 2017: +0.140 | 2018: +0.038 | 2019: +0.187 | 2020: +0.102 | 2021: +0.116 | 2022: +0.338 | 2023: +0.106 | 2024: +0.148 | 2025: +0.019 | 2026: -0.184
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.52
- Early IC=+0.1468, Recent IC=+0.0763, 1st-half IC=+0.1183, 2nd-half IC=+0.0771, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.024, Q3_mid=+0.102, Q4=+0.087, Q5_high_vol=+0.099

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0719, Sharpe=-0.4456)
- Admission: Train IC=+0.2649, Deflated=+0.2639, IR=1.05, Mono=0.87, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.076 | 2017: +0.225 | 2018: +0.203 | 2019: +0.157 | 2020: +0.159 | 2021: +0.117 | 2022: +0.100 | 2023: +0.112 | 2024: +0.148 | 2025: +0.125 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.456 | 2016: +0.191 | 2017: +0.291 | 2018: +0.318 | 2019: +0.237 | 2020: +0.278 | 2021: +0.240 | 2022: +0.309 | 2023: +0.205 | 2024: +0.266 | 2025: -0.003 | 2026: -0.256
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.61
- Early IC=+0.2138, Recent IC=+0.1298, 1st-half IC=+0.1750, 2nd-half IC=+0.1239, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.240, Q2=+0.010, Q3_mid=+0.145, Q4=+0.135, Q5_high_vol=+0.206

**`combo_mean__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0716, Sharpe=-0.2601)
- Admission: Train IC=+0.2290, Deflated=+0.2288, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.069 | 2017: +0.225 | 2018: +0.138 | 2019: +0.101 | 2020: +0.121 | 2021: +0.072 | 2022: +0.076 | 2023: +0.072 | 2024: +0.122 | 2025: +0.144 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.291 | 2016: -0.115 | 2017: +0.318 | 2018: +0.081 | 2019: +0.240 | 2020: +0.089 | 2021: +0.312 | 2022: +0.309 | 2023: +0.294 | 2024: +0.313 | 2025: +0.133 | 2026: -0.168
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.54
- Early IC=+0.1816, Recent IC=+0.0972, 1st-half IC=+0.1305, 2nd-half IC=+0.0935, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.010, Q3_mid=+0.119, Q4=+0.100, Q5_high_vol=+0.133

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0706, Sharpe=-0.3313)
- Admission: Train IC=+0.1863, Deflated=+0.1849, IR=0.51, Mono=0.72, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.097 | 2021: +0.025 | 2022: +0.154 | 2023: +0.090 | 2024: +0.103 | 2025: +0.093 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.377 | 2017: +0.216 | 2018: +0.137 | 2019: +0.181 | 2020: +0.126 | 2021: +0.107 | 2022: +0.164 | 2023: +0.128 | 2024: +0.236 | 2025: -0.002 | 2026: -0.189
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=0.69
- Early IC=+0.1404, Recent IC=+0.0963, 1st-half IC=+0.1169, 2nd-half IC=+0.0990, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.047, Q3_mid=+0.090, Q4=+0.120, Q5_high_vol=+0.125

**`combo_rank_min__net_volume_flow__first_bar_return`** (Lock IC=+0.0706, Sharpe=-0.6439)
- Admission: Train IC=+0.2478, Deflated=+0.2476, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.073 | 2017: +0.177 | 2018: +0.188 | 2019: +0.128 | 2020: +0.087 | 2021: +0.081 | 2022: +0.079 | 2023: +0.072 | 2024: +0.123 | 2025: +0.123 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.012 | 2017: +0.207 | 2018: +0.394 | 2019: +0.169 | 2020: +0.107 | 2021: +0.257 | 2022: +0.254 | 2023: +0.269 | 2024: +0.310 | 2025: +0.104 | 2026: +0.027
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.54
- Early IC=+0.1828, Recent IC=+0.0979, 1st-half IC=+0.1336, 2nd-half IC=+0.0942, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.017, Q3_mid=+0.097, Q4=+0.138, Q5_high_vol=+0.146

**`combo_sig_product__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0705, Sharpe=-0.3494)
- Admission: Train IC=+0.1543, Deflated=+0.1543, IR=0.57, Mono=0.71, p=0.0024, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.026 | 2017: +0.202 | 2018: +0.134 | 2019: +0.129 | 2020: +0.090 | 2021: +0.097 | 2022: +0.083 | 2023: +0.096 | 2024: +0.121 | 2025: +0.194 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.058 | 2016: -0.181 | 2017: +0.220 | 2018: -0.014 | 2019: +0.216 | 2020: +0.090 | 2021: +0.301 | 2022: +0.194 | 2023: +0.137 | 2024: +0.240 | 2025: +0.387 | 2026: -0.270
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=0.65
- Early IC=+0.1679, Recent IC=+0.1086, 1st-half IC=+0.1285, 2nd-half IC=+0.1037, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.040, Q3_mid=+0.154, Q4=+0.115, Q5_high_vol=+0.118

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression`** (Lock IC=+0.0695, Sharpe=-0.6436)
- Admission: Train IC=+0.1698, Deflated=+0.1679, IR=0.57, Mono=0.71, p=0.0008, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.145 | 2017: +0.185 | 2018: +0.133 | 2019: +0.087 | 2020: +0.076 | 2021: +0.059 | 2022: +0.120 | 2023: +0.094 | 2024: +0.106 | 2025: +0.097 | 2026: +0.052
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.235 | 2017: +0.148 | 2018: +0.273 | 2019: +0.193 | 2020: +0.281 | 2021: +0.171 | 2022: +0.152 | 2023: -0.000 | 2024: +0.215 | 2025: -0.204 | 2026: -0.085
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=0.94, Recency ratio=0.63
- Early IC=+0.1587, Recent IC=+0.1001, 1st-half IC=+0.1060, 2nd-half IC=+0.0995, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.031, Q3_mid=+0.071, Q4=+0.123, Q5_high_vol=+0.136

**`combo_max__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0692, Sharpe=-0.3061)
- Admission: Train IC=+0.1779, Deflated=+0.1768, IR=0.53, Mono=0.69, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.063 | 2017: +0.113 | 2018: +0.147 | 2019: +0.078 | 2020: +0.081 | 2021: +0.024 | 2022: +0.116 | 2023: +0.074 | 2024: +0.102 | 2025: +0.099 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.076 | 2016: +0.198 | 2017: +0.154 | 2018: +0.158 | 2019: +0.206 | 2020: +0.076 | 2021: +0.146 | 2022: +0.223 | 2023: +0.169 | 2024: +0.147 | 2025: +0.024 | 2026: -0.153
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.68
- Early IC=+0.1302, Recent IC=+0.0881, 1st-half IC=+0.1045, 2nd-half IC=+0.0859, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.044, Q3_mid=+0.080, Q4=+0.099, Q5_high_vol=+0.094

**`combo_rank_max__star50_limit_proximity_early__early_body_momentum`** (Lock IC=+0.0691, Sharpe=-0.3201)
- Admission: Train IC=+0.1865, Deflated=+0.1853, IR=0.56, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.070 | 2017: +0.120 | 2018: +0.140 | 2019: +0.089 | 2020: +0.074 | 2021: +0.017 | 2022: +0.139 | 2023: +0.084 | 2024: +0.102 | 2025: +0.091 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.065 | 2016: +0.202 | 2017: +0.188 | 2018: +0.083 | 2019: +0.255 | 2020: +0.059 | 2021: +0.107 | 2022: +0.269 | 2023: +0.199 | 2024: +0.182 | 2025: -0.007 | 2026: -0.248
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.87, Recency ratio=0.72
- Early IC=+0.1300, Recent IC=+0.0935, 1st-half IC=+0.1046, 2nd-half IC=+0.0911, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.042, Q3_mid=+0.088, Q4=+0.111, Q5_high_vol=+0.094

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0675, Sharpe=-0.7673)
- Admission: Train IC=+0.1443, Deflated=+0.1428, IR=0.54, Mono=0.67, p=0.0044, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.088 | 2017: +0.169 | 2018: +0.200 | 2019: +0.047 | 2020: +0.123 | 2021: +0.033 | 2022: +0.136 | 2023: +0.089 | 2024: +0.062 | 2025: +0.080 | 2026: +0.074
- Yearly Tail ICs:   2015: +0.105 | 2016: +0.384 | 2017: +0.094 | 2018: +0.309 | 2019: +0.069 | 2020: +0.125 | 2021: +0.252 | 2022: +0.123 | 2023: +0.133 | 2024: +0.116 | 2025: -0.092 | 2026: -0.091
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.41
- Early IC=+0.1844, Recent IC=+0.0757, 1st-half IC=+0.1286, 2nd-half IC=+0.0850, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.028, Q3_mid=+0.097, Q4=+0.111, Q5_high_vol=+0.135

**`combo_mean__net_volume_flow__max_down_ret`** (Lock IC=+0.0666, Sharpe=-0.3458)
- Admission: Train IC=+0.2161, Deflated=+0.2158, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.074 | 2017: +0.200 | 2018: +0.156 | 2019: +0.100 | 2020: +0.124 | 2021: +0.078 | 2022: +0.088 | 2023: +0.073 | 2024: +0.130 | 2025: +0.133 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.031 | 2017: +0.199 | 2018: +0.160 | 2019: +0.189 | 2020: +0.079 | 2021: +0.308 | 2022: +0.329 | 2023: +0.356 | 2024: +0.313 | 2025: +0.049 | 2026: -0.085
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.57
- Early IC=+0.1779, Recent IC=+0.1015, 1st-half IC=+0.1313, 2nd-half IC=+0.0966, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.005, Q3_mid=+0.112, Q4=+0.121, Q5_high_vol=+0.133

**`combo_rank_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0663, Sharpe=-0.4907)
- Admission: Train IC=+0.1802, Deflated=+0.1790, IR=0.51, Mono=0.69, p=0.0002, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.240 | 2016: +0.091 | 2017: +0.153 | 2018: +0.135 | 2019: +0.078 | 2020: +0.118 | 2021: +0.015 | 2022: +0.152 | 2023: +0.096 | 2024: +0.084 | 2025: +0.096 | 2026: +0.058
- Yearly Tail ICs:   2015: +0.068 | 2016: +0.376 | 2017: +0.189 | 2018: +0.177 | 2019: +0.197 | 2020: +0.148 | 2021: +0.151 | 2022: +0.073 | 2023: +0.084 | 2024: +0.209 | 2025: -0.019 | 2026: -0.189
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.62
- Early IC=+0.1439, Recent IC=+0.0896, 1st-half IC=+0.1202, 2nd-half IC=+0.0917, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.043, Q3_mid=+0.104, Q4=+0.104, Q5_high_vol=+0.120

**`combo_min__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=+0.0660, Sharpe=-0.7390)
- Admission: Train IC=+0.2098, Deflated=+0.2092, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.097 | 2017: +0.180 | 2018: +0.153 | 2019: +0.115 | 2020: +0.104 | 2021: +0.083 | 2022: +0.088 | 2023: +0.077 | 2024: +0.123 | 2025: +0.142 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.266 | 2016: -0.156 | 2017: +0.259 | 2018: +0.074 | 2019: +0.187 | 2020: +0.292 | 2021: +0.178 | 2022: +0.134 | 2023: +0.317 | 2024: +0.197 | 2025: +0.235 | 2026: -0.075
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.60
- Early IC=+0.1661, Recent IC=+0.0996, 1st-half IC=+0.1261, 2nd-half IC=+0.0974, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.005, Q3_mid=+0.099, Q4=+0.143, Q5_high_vol=+0.143

**`combo_min__net_volume_flow__first_bar_return`** (Lock IC=+0.0647, Sharpe=-0.2556)
- Admission: Train IC=+0.2561, Deflated=+0.2559, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.201 | 2016: +0.072 | 2017: +0.182 | 2018: +0.177 | 2019: +0.121 | 2020: +0.094 | 2021: +0.083 | 2022: +0.085 | 2023: +0.078 | 2024: +0.133 | 2025: +0.124 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.331 | 2016: +0.018 | 2017: +0.229 | 2018: +0.387 | 2019: +0.126 | 2020: +0.113 | 2021: +0.293 | 2022: +0.235 | 2023: +0.310 | 2024: +0.344 | 2025: +0.135 | 2026: -0.064
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.59
- Early IC=+0.1797, Recent IC=+0.1054, 1st-half IC=+0.1313, 2nd-half IC=+0.1001, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.011, Q3_mid=+0.103, Q4=+0.134, Q5_high_vol=+0.146

**`combo_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0639, Sharpe=-0.6077)
- Admission: Train IC=+0.2308, Deflated=+0.2303, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.087 | 2017: +0.213 | 2018: +0.254 | 2019: +0.156 | 2020: +0.136 | 2021: +0.098 | 2022: +0.055 | 2023: +0.068 | 2024: +0.125 | 2025: +0.113 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.087 | 2017: +0.354 | 2018: +0.430 | 2019: +0.183 | 2020: +0.121 | 2021: +0.310 | 2022: +0.263 | 2023: +0.165 | 2024: +0.211 | 2025: +0.113 | 2026: -0.177
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.41
- Early IC=+0.2335, Recent IC=+0.0966, 1st-half IC=+0.1821, 2nd-half IC=+0.0898, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.001, Q3_mid=+0.135, Q4=+0.150, Q5_high_vol=+0.191

**`combo_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0639, Sharpe=-0.6077)
- Admission: Train IC=+0.2306, Deflated=+0.2301, IR=0.79, Mono=0.76, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.087 | 2017: +0.213 | 2018: +0.254 | 2019: +0.156 | 2020: +0.136 | 2021: +0.098 | 2022: +0.055 | 2023: +0.069 | 2024: +0.125 | 2025: +0.113 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.087 | 2017: +0.355 | 2018: +0.430 | 2019: +0.183 | 2020: +0.121 | 2021: +0.312 | 2022: +0.265 | 2023: +0.170 | 2024: +0.212 | 2025: +0.113 | 2026: -0.177
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.49, Recency ratio=0.41
- Early IC=+0.2337, Recent IC=+0.0967, 1st-half IC=+0.1820, 2nd-half IC=+0.0898, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.001, Q3_mid=+0.135, Q4=+0.150, Q5_high_vol=+0.191

**`combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0636, Sharpe=-0.1214)
- Admission: Train IC=+0.1735, Deflated=+0.1724, IR=0.56, Mono=0.71, p=0.0006, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.106 | 2017: +0.117 | 2018: +0.159 | 2019: +0.080 | 2020: +0.099 | 2021: +0.020 | 2022: +0.128 | 2023: +0.077 | 2024: +0.101 | 2025: +0.088 | 2026: +0.063
- Yearly Tail ICs:   2015: +0.047 | 2016: +0.402 | 2017: +0.195 | 2018: +0.194 | 2019: +0.160 | 2020: +0.093 | 2021: +0.140 | 2022: +0.150 | 2023: +0.146 | 2024: +0.227 | 2025: -0.047 | 2026: -0.159
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.65
- Early IC=+0.1379, Recent IC=+0.0892, 1st-half IC=+0.1119, 2nd-half IC=+0.0879, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.035, Q3_mid=+0.080, Q4=+0.105, Q5_high_vol=+0.120

**`combo_min__trend_bar_close_consistency__first_bar_return`** (Lock IC=+0.0619, Sharpe=-0.1417)
- Admission: Train IC=+0.2263, Deflated=+0.2266, IR=0.69, Mono=0.72, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.055 | 2017: +0.155 | 2018: +0.156 | 2019: +0.101 | 2020: +0.046 | 2021: +0.050 | 2022: +0.064 | 2023: +0.074 | 2024: +0.123 | 2025: +0.123 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.018 | 2017: +0.331 | 2018: +0.394 | 2019: +0.087 | 2020: +0.029 | 2021: +0.307 | 2022: +0.264 | 2023: +0.037 | 2024: +0.318 | 2025: +0.151 | 2026: +0.026
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.63
- Early IC=+0.1557, Recent IC=+0.0986, 1st-half IC=+0.1061, 2nd-half IC=+0.0808, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.027, Q3_mid=+0.076, Q4=+0.102, Q5_high_vol=+0.124

**`combo_min__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0619, Sharpe=-0.1417)
- Admission: Train IC=+0.2262, Deflated=+0.2265, IR=0.70, Mono=0.72, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.054 | 2017: +0.155 | 2018: +0.156 | 2019: +0.102 | 2020: +0.046 | 2021: +0.051 | 2022: +0.064 | 2023: +0.074 | 2024: +0.123 | 2025: +0.123 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.017 | 2017: +0.331 | 2018: +0.392 | 2019: +0.091 | 2020: +0.029 | 2021: +0.317 | 2022: +0.265 | 2023: +0.037 | 2024: +0.318 | 2025: +0.151 | 2026: +0.026
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.63
- Early IC=+0.1554, Recent IC=+0.0983, 1st-half IC=+0.1062, 2nd-half IC=+0.0808, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.027, Q3_mid=+0.076, Q4=+0.102, Q5_high_vol=+0.124

**`combo_rank_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0610, Sharpe=-0.3371)
- Admission: Train IC=+0.1800, Deflated=+0.1788, IR=0.64, Mono=0.74, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.084 | 2017: +0.178 | 2018: +0.119 | 2019: +0.074 | 2020: +0.106 | 2021: +0.122 | 2022: +0.077 | 2023: +0.091 | 2024: +0.149 | 2025: +0.154 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.222 | 2017: +0.179 | 2018: +0.282 | 2019: +0.330 | 2020: +0.148 | 2021: +0.286 | 2022: +0.022 | 2023: +0.103 | 2024: +0.332 | 2025: +0.115 | 2026: -0.098
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=0.80
- Early IC=+0.1474, Recent IC=+0.1174, 1st-half IC=+0.1011, 2nd-half IC=+0.1142, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.021, Q3_mid=+0.096, Q4=+0.088, Q5_high_vol=+0.125

**`combo_rank_max__volatility_expansion_trend_vector__max_down_ret`** (Lock IC=+0.0609, Sharpe=-0.4353)
- Admission: Train IC=+0.1991, Deflated=+0.1993, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.048 | 2017: +0.216 | 2018: +0.159 | 2019: +0.107 | 2020: +0.105 | 2021: +0.088 | 2022: +0.062 | 2023: +0.047 | 2024: +0.136 | 2025: +0.153 | 2026: -0.068
- Yearly Tail ICs:   2015: +0.350 | 2016: -0.108 | 2017: +0.230 | 2018: +0.127 | 2019: +0.354 | 2020: +0.058 | 2021: +0.265 | 2022: +0.230 | 2023: +0.214 | 2024: +0.304 | 2025: +0.243 | 2026: -0.150
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.51
- Early IC=+0.1867, Recent IC=+0.0946, 1st-half IC=+0.1311, 2nd-half IC=+0.0879, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.002, Q3_mid=+0.124, Q4=+0.106, Q5_high_vol=+0.127

**`combo_mean__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=+0.0605, Sharpe=-1.0184)
- Admission: Train IC=+0.2517, Deflated=+0.2514, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.095 | 2017: +0.183 | 2018: +0.186 | 2019: +0.108 | 2020: +0.104 | 2021: +0.105 | 2022: +0.105 | 2023: +0.081 | 2024: +0.117 | 2025: +0.143 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.392 | 2016: -0.099 | 2017: +0.140 | 2018: +0.276 | 2019: +0.342 | 2020: +0.187 | 2021: +0.123 | 2022: +0.279 | 2023: +0.347 | 2024: +0.131 | 2025: +0.134 | 2026: -0.091
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.54
- Early IC=+0.1843, Recent IC=+0.0988, 1st-half IC=+0.1301, 2nd-half IC=+0.1052, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.180, Q2=-0.003, Q3_mid=+0.112, Q4=+0.143, Q5_high_vol=+0.155

**`combo_rank_min__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0600, Sharpe=-0.0062)
- Admission: Train IC=+0.1574, Deflated=+0.1569, IR=0.43, Mono=0.67, p=0.0022, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.126 | 2017: +0.129 | 2018: +0.196 | 2019: +0.098 | 2020: +0.095 | 2021: +0.072 | 2022: +0.082 | 2023: +0.058 | 2024: +0.091 | 2025: +0.113 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.419 | 2016: +0.215 | 2017: +0.212 | 2018: +0.207 | 2019: +0.139 | 2020: +0.155 | 2021: +0.066 | 2022: +0.184 | 2023: +0.003 | 2024: +0.095 | 2025: +0.057 | 2026: -0.446
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.46
- Early IC=+0.1626, Recent IC=+0.0748, 1st-half IC=+0.1195, 2nd-half IC=+0.0788, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.152, Q2=-0.019, Q3_mid=+0.075, Q4=+0.140, Q5_high_vol=+0.145

**`combo_min__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0600, Sharpe=-1.2291)
- Admission: Train IC=+0.1973, Deflated=+0.1969, IR=0.40, Mono=0.66, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.085 | 2017: +0.128 | 2018: +0.146 | 2019: +0.070 | 2020: +0.109 | 2021: +0.083 | 2022: +0.116 | 2023: +0.090 | 2024: +0.111 | 2025: +0.141 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.121 | 2016: -0.072 | 2017: +0.085 | 2018: +0.145 | 2019: +0.194 | 2020: +0.282 | 2021: +0.109 | 2022: +0.185 | 2023: +0.125 | 2024: +0.209 | 2025: +0.155 | 2026: -0.171
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=0.73
- Early IC=+0.1371, Recent IC=+0.1001, 1st-half IC=+0.1011, 2nd-half IC=+0.1044, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.005, Q3_mid=+0.102, Q4=+0.124, Q5_high_vol=+0.127

**`combo_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0594, Sharpe=-0.8629)
- Admission: Train IC=+0.1861, Deflated=+0.1850, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.084 | 2017: +0.178 | 2018: +0.126 | 2019: +0.071 | 2020: +0.110 | 2021: +0.119 | 2022: +0.087 | 2023: +0.109 | 2024: +0.150 | 2025: +0.159 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.280 | 2017: +0.300 | 2018: +0.295 | 2019: +0.099 | 2020: +0.101 | 2021: +0.228 | 2022: +0.075 | 2023: +0.177 | 2024: +0.247 | 2025: +0.107 | 2026: -0.041
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=1.20, Recency ratio=0.85
- Early IC=+0.1521, Recent IC=+0.1295, 1st-half IC=+0.1014, 2nd-half IC=+0.1220, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.033, Q3_mid=+0.098, Q4=+0.090, Q5_high_vol=+0.130

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0593, Sharpe=-0.7951)
- Admission: Train IC=+0.2276, Deflated=+0.2272, IR=0.88, Mono=0.82, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.085 | 2017: +0.205 | 2018: +0.250 | 2019: +0.155 | 2020: +0.120 | 2021: +0.089 | 2022: +0.055 | 2023: +0.059 | 2024: +0.109 | 2025: +0.100 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.168 | 2017: +0.351 | 2018: +0.314 | 2019: +0.237 | 2020: +0.201 | 2021: +0.357 | 2022: +0.284 | 2023: +0.165 | 2024: +0.165 | 2025: +0.070 | 2026: -0.178
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.46, Recency ratio=0.38
- Early IC=+0.2275, Recent IC=+0.0857, 1st-half IC=+0.1765, 2nd-half IC=+0.0813, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.160, Q2=-0.024, Q3_mid=+0.126, Q4=+0.155, Q5_high_vol=+0.179

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0589, Sharpe=-0.5615)
- Admission: Train IC=+0.2713, Deflated=+0.2707, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.036 | 2017: +0.200 | 2018: +0.198 | 2019: +0.184 | 2020: +0.171 | 2021: +0.124 | 2022: +0.054 | 2023: +0.103 | 2024: +0.114 | 2025: +0.045 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.045 | 2017: +0.319 | 2018: +0.367 | 2019: +0.427 | 2020: +0.195 | 2021: +0.177 | 2022: +0.220 | 2023: +0.183 | 2024: +0.238 | 2025: +0.150 | 2026: +0.024
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.57, Recency ratio=0.55
- Early IC=+0.1989, Recent IC=+0.1087, 1st-half IC=+0.1791, 2nd-half IC=+0.1028, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.007, Q3_mid=+0.125, Q4=+0.150, Q5_high_vol=+0.205

**`combo_max__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0585, Sharpe=-0.7195)
- Admission: Train IC=+0.2686, Deflated=+0.2676, IR=1.05, Mono=0.85, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.083 | 2017: +0.234 | 2018: +0.168 | 2019: +0.111 | 2020: +0.161 | 2021: +0.115 | 2022: +0.100 | 2023: +0.085 | 2024: +0.153 | 2025: +0.109 | 2026: -0.006
- Yearly Tail ICs:   2015: +0.420 | 2016: +0.202 | 2017: +0.309 | 2018: +0.260 | 2019: +0.280 | 2020: +0.206 | 2021: +0.266 | 2022: +0.317 | 2023: +0.326 | 2024: +0.311 | 2025: -0.004 | 2026: -0.289
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.59
- Early IC=+0.2012, Recent IC=+0.1189, 1st-half IC=+0.1537, 2nd-half IC=+0.1217, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.232, Q2=+0.005, Q3_mid=+0.135, Q4=+0.138, Q5_high_vol=+0.172

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0573, Sharpe=-0.2479)
- Admission: Train IC=+0.2982, Deflated=+0.2978, IR=1.05, Mono=0.85, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.174 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.095 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.450 | 2016: +0.051 | 2017: +0.191 | 2018: +0.407 | 2019: +0.229 | 2020: +0.221 | 2021: +0.337 | 2022: +0.238 | 2023: +0.314 | 2024: +0.298 | 2025: +0.104 | 2026: -0.330
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.59
- Early IC=+0.2051, Recent IC=+0.1217, 1st-half IC=+0.1755, 2nd-half IC=+0.1177, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.006, Q3_mid=+0.133, Q4=+0.148, Q5_high_vol=+0.215

**`bar_body_rng_0`** (Lock IC=+0.0572, Sharpe=-0.7848)
- Admission: Train IC=+0.1378, Deflated=+0.1385, IR=0.49, Mono=0.67, p=0.0060, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.104 | 2017: +0.169 | 2018: +0.192 | 2019: +0.131 | 2020: +0.092 | 2021: +0.119 | 2022: +0.057 | 2023: +0.068 | 2024: +0.105 | 2025: +0.099 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.365 | 2016: -0.105 | 2017: +0.215 | 2018: +0.088 | 2019: +0.267 | 2020: +0.135 | 2021: +0.187 | 2022: +0.004 | 2023: +0.093 | 2024: +0.067 | 2025: +0.148 | 2026: -0.034
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.48
- Early IC=+0.1800, Recent IC=+0.0866, 1st-half IC=+0.1399, 2nd-half IC=+0.0861, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.036, Q3_mid=+0.115, Q4=+0.172, Q5_high_vol=+0.137

**`volatility_expansion_trend_vector`** (Lock IC=+0.0564, Sharpe=-1.1688)
- Admission: Train IC=+0.2577, Deflated=+0.2575, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.061 | 2017: +0.201 | 2018: +0.129 | 2019: +0.076 | 2020: +0.097 | 2021: +0.073 | 2022: +0.093 | 2023: +0.089 | 2024: +0.123 | 2025: +0.155 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.306 | 2016: -0.052 | 2017: +0.291 | 2018: +0.219 | 2019: +0.292 | 2020: +0.226 | 2021: +0.227 | 2022: +0.241 | 2023: +0.284 | 2024: +0.228 | 2025: +0.065 | 2026: -0.099
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.64
- Early IC=+0.1651, Recent IC=+0.1062, 1st-half IC=+0.1138, 2nd-half IC=+0.1009, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.015, Q3_mid=+0.111, Q4=+0.090, Q5_high_vol=+0.124

**`combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0560, Sharpe=-1.0726)
- Admission: Train IC=+0.2588, Deflated=+0.2581, IR=0.85, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.060 | 2017: +0.153 | 2018: +0.135 | 2019: +0.084 | 2020: +0.118 | 2021: +0.094 | 2022: +0.099 | 2023: +0.100 | 2024: +0.139 | 2025: +0.125 | 2026: -0.040
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.183 | 2017: +0.178 | 2018: +0.259 | 2019: +0.216 | 2020: +0.270 | 2021: +0.265 | 2022: +0.304 | 2023: +0.228 | 2024: +0.291 | 2025: +0.016 | 2026: -0.173
- IC CV=0.20, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.83
- Early IC=+0.1441, Recent IC=+0.1197, 1st-half IC=+0.1132, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.001, Q3_mid=+0.112, Q4=+0.126, Q5_high_vol=+0.127

**`combo_max__close_vs_open_range__max_down_ret`** (Lock IC=+0.0557, Sharpe=-0.2026)
- Admission: Train IC=+0.1851, Deflated=+0.1847, IR=0.50, Mono=0.67, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.063 | 2017: +0.213 | 2018: +0.131 | 2019: +0.096 | 2020: +0.116 | 2021: +0.083 | 2022: +0.065 | 2023: +0.046 | 2024: +0.133 | 2025: +0.151 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.291 | 2016: +0.107 | 2017: +0.255 | 2018: +0.050 | 2019: +0.202 | 2020: +0.047 | 2021: +0.250 | 2022: +0.234 | 2023: +0.153 | 2024: +0.320 | 2025: +0.061 | 2026: -0.005
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.52
- Early IC=+0.1720, Recent IC=+0.0893, 1st-half IC=+0.1226, 2nd-half IC=+0.0876, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.221, Q2=+0.017, Q3_mid=+0.110, Q4=+0.103, Q5_high_vol=+0.107

**`combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0550, Sharpe=-0.4475)
- Admission: Train IC=+0.2158, Deflated=+0.2154, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.034 | 2017: +0.155 | 2018: +0.220 | 2019: +0.177 | 2020: +0.184 | 2021: +0.159 | 2022: +0.043 | 2023: +0.088 | 2024: +0.140 | 2025: +0.074 | 2026: +0.037
- Yearly Tail ICs:   2015: +0.388 | 2016: -0.001 | 2017: +0.280 | 2018: +0.363 | 2019: +0.302 | 2020: -0.019 | 2021: +0.343 | 2022: +0.121 | 2023: +0.185 | 2024: +0.160 | 2025: +0.150 | 2026: +0.051
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.61
- Early IC=+0.1873, Recent IC=+0.1140, 1st-half IC=+0.1736, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.007, Q3_mid=+0.135, Q4=+0.123, Q5_high_vol=+0.229

**`combo_min__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0550, Sharpe=-0.9817)
- Admission: Train IC=+0.2328, Deflated=+0.2321, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.065 | 2017: +0.195 | 2018: +0.174 | 2019: +0.105 | 2020: +0.128 | 2021: +0.114 | 2022: +0.053 | 2023: +0.116 | 2024: +0.141 | 2025: +0.126 | 2026: -0.041
- Yearly Tail ICs:   2015: +0.290 | 2016: +0.249 | 2017: +0.255 | 2018: +0.272 | 2019: +0.330 | 2020: +0.154 | 2021: +0.355 | 2022: +0.123 | 2023: +0.114 | 2024: +0.248 | 2025: +0.053 | 2026: +0.132
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1846, Recent IC=+0.1283, 1st-half IC=+0.1393, 2nd-half IC=+0.1148, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.238, Q2=+0.020, Q3_mid=+0.123, Q4=+0.092, Q5_high_vol=+0.163

**`combo_rank_min__volatility_expansion_trend_vector__close_vs_open_range`** (Lock IC=+0.0549, Sharpe=-0.5958)
- Admission: Train IC=+0.2517, Deflated=+0.2512, IR=0.61, Mono=0.75, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.072 | 2017: +0.202 | 2018: +0.115 | 2019: +0.069 | 2020: +0.095 | 2021: +0.064 | 2022: +0.087 | 2023: +0.088 | 2024: +0.128 | 2025: +0.148 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.123 | 2017: +0.327 | 2018: +0.237 | 2019: +0.299 | 2020: +0.226 | 2021: +0.215 | 2022: +0.121 | 2023: +0.247 | 2024: +0.220 | 2025: -0.042 | 2026: -0.145
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=0.68
- Early IC=+0.1583, Recent IC=+0.1080, 1st-half IC=+0.1064, 2nd-half IC=+0.0998, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.017, Q3_mid=+0.104, Q4=+0.089, Q5_high_vol=+0.115

**`combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0541, Sharpe=-0.5111)
- Admission: Train IC=+0.2059, Deflated=+0.2054, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.098 | 2017: +0.196 | 2018: +0.233 | 2019: +0.142 | 2020: +0.133 | 2021: +0.143 | 2022: +0.090 | 2023: +0.083 | 2024: +0.135 | 2025: +0.098 | 2026: +0.001
- Yearly Tail ICs:   2015: +0.521 | 2016: +0.025 | 2017: +0.172 | 2018: +0.248 | 2019: +0.347 | 2020: +0.053 | 2021: +0.287 | 2022: +0.311 | 2023: +0.023 | 2024: +0.160 | 2025: +0.038 | 2026: -0.005
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.51
- Early IC=+0.2143, Recent IC=+0.1094, 1st-half IC=+0.1618, 2nd-half IC=+0.1195, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.194, Q2=-0.013, Q3_mid=+0.137, Q4=+0.174, Q5_high_vol=+0.199

**`combo_rank_max__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0538, Sharpe=-1.1112)
- Admission: Train IC=+0.2272, Deflated=+0.2265, IR=0.54, Mono=0.72, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.059 | 2017: +0.185 | 2018: +0.130 | 2019: +0.072 | 2020: +0.117 | 2021: +0.085 | 2022: +0.116 | 2023: +0.080 | 2024: +0.135 | 2025: +0.143 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.388 | 2016: +0.131 | 2017: +0.188 | 2018: +0.187 | 2019: +0.146 | 2020: +0.146 | 2021: +0.228 | 2022: +0.279 | 2023: +0.154 | 2024: +0.298 | 2025: +0.053 | 2026: -0.032
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=0.68
- Early IC=+0.1547, Recent IC=+0.1055, 1st-half IC=+0.1126, 2nd-half IC=+0.1127, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.018, Q3_mid=+0.121, Q4=+0.111, Q5_high_vol=+0.115

**`combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0534, Sharpe=-1.3411)
- Admission: Train IC=+0.2578, Deflated=+0.2570, IR=0.94, Mono=0.80, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.277 | 2016: +0.075 | 2017: +0.263 | 2018: +0.146 | 2019: +0.117 | 2020: +0.157 | 2021: +0.109 | 2022: +0.095 | 2023: +0.073 | 2024: +0.149 | 2025: +0.112 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.436 | 2016: -0.023 | 2017: +0.320 | 2018: +0.251 | 2019: +0.393 | 2020: +0.170 | 2021: +0.222 | 2022: +0.274 | 2023: +0.267 | 2024: +0.278 | 2025: -0.051 | 2026: -0.181
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.54
- Early IC=+0.2044, Recent IC=+0.1113, 1st-half IC=+0.1560, 2nd-half IC=+0.1159, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.010, Q3_mid=+0.140, Q4=+0.132, Q5_high_vol=+0.181

**`combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0528, Sharpe=-0.4408)
- Admission: Train IC=+0.2139, Deflated=+0.2135, IR=0.49, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.046 | 2017: +0.187 | 2018: +0.139 | 2019: +0.079 | 2020: +0.098 | 2021: +0.074 | 2022: +0.085 | 2023: +0.087 | 2024: +0.107 | 2025: +0.149 | 2026: -0.082
- Yearly Tail ICs:   2015: +0.373 | 2016: +0.063 | 2017: +0.270 | 2018: +0.196 | 2019: +0.169 | 2020: +0.218 | 2021: +0.235 | 2022: +0.188 | 2023: +0.103 | 2024: +0.234 | 2025: +0.130 | 2026: -0.235
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.60
- Early IC=+0.1629, Recent IC=+0.0975, 1st-half IC=+0.1182, 2nd-half IC=+0.0936, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.020, Q3_mid=+0.108, Q4=+0.105, Q5_high_vol=+0.111

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0527, Sharpe=-0.1565)
- Admission: Train IC=+0.2970, Deflated=+0.2966, IR=1.08, Mono=0.85, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.042 | 2017: +0.162 | 2018: +0.219 | 2019: +0.178 | 2020: +0.159 | 2021: +0.163 | 2022: +0.058 | 2023: +0.085 | 2024: +0.125 | 2025: +0.094 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.429 | 2016: +0.028 | 2017: +0.198 | 2018: +0.391 | 2019: +0.253 | 2020: +0.220 | 2021: +0.335 | 2022: +0.238 | 2023: +0.303 | 2024: +0.303 | 2025: +0.101 | 2026: -0.345
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.55
- Early IC=+0.1908, Recent IC=+0.1050, 1st-half IC=+0.1691, 2nd-half IC=+0.1101, Neg regimes=1/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.212, Q2=-0.001, Q3_mid=+0.122, Q4=+0.137, Q5_high_vol=+0.205

**`combo_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0525, Sharpe=-0.4214)
- Admission: Train IC=+0.2540, Deflated=+0.2534, IR=0.71, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.073 | 2017: +0.175 | 2018: +0.136 | 2019: +0.075 | 2020: +0.098 | 2021: +0.065 | 2022: +0.078 | 2023: +0.091 | 2024: +0.127 | 2025: +0.140 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.308 | 2016: +0.118 | 2017: +0.321 | 2018: +0.251 | 2019: +0.204 | 2020: +0.247 | 2021: +0.221 | 2022: +0.111 | 2023: +0.216 | 2024: +0.234 | 2025: -0.012 | 2026: -0.010
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.70
- Early IC=+0.1554, Recent IC=+0.1089, 1st-half IC=+0.1081, 2nd-half IC=+0.0965, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.004, Q3_mid=+0.103, Q4=+0.106, Q5_high_vol=+0.112

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=+0.0525, Sharpe=-0.9776)
- Admission: Train IC=+0.2151, Deflated=+0.2139, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.117 | 2017: +0.231 | 2018: +0.185 | 2019: +0.100 | 2020: +0.143 | 2021: +0.129 | 2022: +0.129 | 2023: +0.104 | 2024: +0.143 | 2025: +0.119 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.536 | 2016: +0.380 | 2017: +0.247 | 2018: +0.302 | 2019: +0.155 | 2020: +0.230 | 2021: +0.407 | 2022: +0.100 | 2023: +0.182 | 2024: +0.182 | 2025: +0.069 | 2026: -0.134
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.60
- Early IC=+0.2079, Recent IC=+0.1238, 1st-half IC=+0.1454, 2nd-half IC=+0.1376, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.015, Q3_mid=+0.135, Q4=+0.127, Q5_high_vol=+0.210

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0524, Sharpe=-0.6914)
- Admission: Train IC=+0.2127, Deflated=+0.2112, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.140 | 2017: +0.227 | 2018: +0.215 | 2019: +0.111 | 2020: +0.183 | 2021: +0.149 | 2022: +0.103 | 2023: +0.117 | 2024: +0.171 | 2025: +0.097 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.278 | 2017: +0.266 | 2018: +0.326 | 2019: +0.260 | 2020: +0.291 | 2021: +0.349 | 2022: -0.026 | 2023: +0.105 | 2024: +0.338 | 2025: -0.051 | 2026: -0.093
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.65
- Early IC=+0.2210, Recent IC=+0.1437, 1st-half IC=+0.1670, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.043, Q3_mid=+0.135, Q4=+0.133, Q5_high_vol=+0.231

**`combo_sig_product__net_volume_flow__max_down_ret`** (Lock IC=+0.0521, Sharpe=-0.6353)
- Admission: Train IC=+0.1207, Deflated=+0.1196, IR=0.48, Mono=0.66, p=0.0146, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.138 | 2016: +0.037 | 2017: +0.203 | 2018: +0.109 | 2019: +0.133 | 2020: +0.125 | 2021: +0.039 | 2022: +0.047 | 2023: +0.073 | 2024: +0.084 | 2025: +0.140 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.201 | 2017: +0.171 | 2018: +0.033 | 2019: +0.122 | 2020: +0.037 | 2021: +0.286 | 2022: +0.168 | 2023: +0.119 | 2024: +0.268 | 2025: +0.240 | 2026: -0.124
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=0.48, Recency ratio=0.50
- Early IC=+0.1560, Recent IC=+0.0786, 1st-half IC=+0.1301, 2nd-half IC=+0.0618, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.029, Q3_mid=+0.103, Q4=+0.118, Q5_high_vol=+0.074

**`combo_mean__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0519, Sharpe=-0.8017)
- Admission: Train IC=+0.2476, Deflated=+0.2473, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.098 | 2017: +0.152 | 2018: +0.193 | 2019: +0.110 | 2020: +0.112 | 2021: +0.089 | 2022: +0.111 | 2023: +0.084 | 2024: +0.123 | 2025: +0.124 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.473 | 2016: +0.113 | 2017: +0.133 | 2018: +0.290 | 2019: +0.176 | 2020: +0.264 | 2021: +0.162 | 2022: +0.246 | 2023: +0.355 | 2024: +0.234 | 2025: +0.039 | 2026: -0.112
- IC CV=0.27, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.60
- Early IC=+0.1725, Recent IC=+0.1033, 1st-half IC=+0.1295, 2nd-half IC=+0.1078, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.002, Q3_mid=+0.112, Q4=+0.157, Q5_high_vol=+0.148

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0518, Sharpe=-0.2853)
- Admission: Train IC=+0.2053, Deflated=+0.2054, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.093 | 2017: +0.259 | 2018: +0.235 | 2019: +0.142 | 2020: +0.133 | 2021: +0.080 | 2022: +0.095 | 2023: +0.039 | 2024: +0.124 | 2025: +0.101 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.246 | 2016: -0.006 | 2017: +0.243 | 2018: +0.406 | 2019: +0.109 | 2020: +0.236 | 2021: +0.186 | 2022: +0.169 | 2023: +0.222 | 2024: +0.235 | 2025: +0.034 | 2026: -0.250
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.33
- Early IC=+0.2472, Recent IC=+0.0813, 1st-half IC=+0.1692, 2nd-half IC=+0.0931, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.191, Q2=-0.023, Q3_mid=+0.137, Q4=+0.136, Q5_high_vol=+0.176

**`combo_max__high_low_sequence_momentum__max_down_ret`** (Lock IC=+0.0504, Sharpe=-0.7776)
- Admission: Train IC=+0.1538, Deflated=+0.1534, IR=0.47, Mono=0.70, p=0.0024, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.049 | 2017: +0.216 | 2018: +0.142 | 2019: +0.088 | 2020: +0.102 | 2021: +0.065 | 2022: +0.069 | 2023: +0.039 | 2024: +0.134 | 2025: +0.131 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.295 | 2016: +0.090 | 2017: +0.161 | 2018: -0.017 | 2019: +0.220 | 2020: +0.087 | 2021: +0.050 | 2022: +0.278 | 2023: +0.154 | 2024: +0.291 | 2025: +0.007 | 2026: +0.045
- IC CV=0.49, Neg years (linear/tail)=0/1 of 8, Half ratio=0.69, Recency ratio=0.48
- Early IC=+0.1791, Recent IC=+0.0866, 1st-half IC=+0.1211, 2nd-half IC=+0.0833, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.029, Q3_mid=+0.097, Q4=+0.091, Q5_high_vol=+0.112

**`combo_max__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=+0.0503, Sharpe=-1.5796)
- Admission: Train IC=+0.2718, Deflated=+0.2718, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.117 | 2017: +0.167 | 2018: +0.160 | 2019: +0.083 | 2020: +0.113 | 2021: +0.137 | 2022: +0.124 | 2023: +0.050 | 2024: +0.120 | 2025: +0.119 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.375 | 2016: -0.018 | 2017: +0.157 | 2018: +0.189 | 2019: +0.298 | 2020: +0.207 | 2021: +0.181 | 2022: +0.229 | 2023: +0.145 | 2024: +0.253 | 2025: +0.063 | 2026: -0.193
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.52
- Early IC=+0.1638, Recent IC=+0.0849, 1st-half IC=+0.1180, 2nd-half IC=+0.1121, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.004, Q3_mid=+0.115, Q4=+0.144, Q5_high_vol=+0.151

**`combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0498, Sharpe=-0.3399)
- Admission: Train IC=+0.2096, Deflated=+0.2090, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.040 | 2017: +0.162 | 2018: +0.202 | 2019: +0.175 | 2020: +0.184 | 2021: +0.152 | 2022: +0.041 | 2023: +0.103 | 2024: +0.138 | 2025: +0.061 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.355 | 2016: -0.000 | 2017: +0.318 | 2018: +0.310 | 2019: +0.308 | 2020: +0.005 | 2021: +0.332 | 2022: +0.067 | 2023: +0.113 | 2024: +0.175 | 2025: +0.039 | 2026: +0.248
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.66
- Early IC=+0.1818, Recent IC=+0.1208, 1st-half IC=+0.1716, 2nd-half IC=+0.1159, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.008, Q3_mid=+0.136, Q4=+0.126, Q5_high_vol=+0.222

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0490, Sharpe=-0.2860)
- Admission: Train IC=+0.1677, Deflated=+0.1678, IR=0.55, Mono=0.71, p=0.0008, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.108 | 2017: +0.192 | 2018: +0.220 | 2019: +0.126 | 2020: +0.108 | 2021: +0.167 | 2022: +0.095 | 2023: +0.088 | 2024: +0.134 | 2025: +0.072 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.453 | 2016: +0.114 | 2017: +0.109 | 2018: +0.317 | 2019: +0.321 | 2020: +0.122 | 2021: +0.267 | 2022: +0.324 | 2023: +0.075 | 2024: +0.084 | 2025: +0.119 | 2026: +0.022
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.91, Recency ratio=0.54
- Early IC=+0.2059, Recent IC=+0.1113, 1st-half IC=+0.1425, 2nd-half IC=+0.1295, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.205, Q2=-0.002, Q3_mid=+0.133, Q4=+0.166, Q5_high_vol=+0.174

**`combo_tri_mean__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0488, Sharpe=-1.1019)
- Admission: Train IC=+0.2612, Deflated=+0.2607, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.055 | 2017: +0.210 | 2018: +0.148 | 2019: +0.075 | 2020: +0.128 | 2021: +0.092 | 2022: +0.090 | 2023: +0.099 | 2024: +0.134 | 2025: +0.133 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.448 | 2016: +0.205 | 2017: +0.333 | 2018: +0.218 | 2019: +0.230 | 2020: +0.256 | 2021: +0.262 | 2022: +0.230 | 2023: +0.252 | 2024: +0.310 | 2025: +0.053 | 2026: -0.143
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.65
- Early IC=+0.1792, Recent IC=+0.1165, 1st-half IC=+0.1294, 2nd-half IC=+0.1091, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.015, Q3_mid=+0.127, Q4=+0.105, Q5_high_vol=+0.142

**`combo_min__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0486, Sharpe=-0.6142)
- Admission: Train IC=+0.2157, Deflated=+0.2159, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.125 | 2017: +0.145 | 2018: +0.224 | 2019: +0.146 | 2020: +0.088 | 2021: +0.104 | 2022: +0.062 | 2023: +0.062 | 2024: +0.116 | 2025: +0.105 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.364 | 2016: +0.000 | 2017: +0.288 | 2018: +0.427 | 2019: +0.307 | 2020: +0.114 | 2021: +0.209 | 2022: +0.265 | 2023: +0.100 | 2024: +0.199 | 2025: +0.029 | 2026: -0.144
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.48
- Early IC=+0.1846, Recent IC=+0.0892, 1st-half IC=+0.1433, 2nd-half IC=+0.0855, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.138, Q2=-0.009, Q3_mid=+0.080, Q4=+0.143, Q5_high_vol=+0.181

**`combo_max__net_volume_flow__max_down_ret`** (Lock IC=+0.0486, Sharpe=-0.2505)
- Admission: Train IC=+0.1926, Deflated=+0.1922, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.084 | 2017: +0.206 | 2018: +0.175 | 2019: +0.106 | 2020: +0.109 | 2021: +0.075 | 2022: +0.071 | 2023: +0.048 | 2024: +0.146 | 2025: +0.137 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.158 | 2017: +0.167 | 2018: +0.133 | 2019: +0.189 | 2020: +0.019 | 2021: +0.232 | 2022: +0.271 | 2023: +0.307 | 2024: +0.282 | 2025: +0.058 | 2026: -0.147
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.1906, Recent IC=+0.0970, 1st-half IC=+0.1338, 2nd-half IC=+0.0909, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.007, Q3_mid=+0.105, Q4=+0.124, Q5_high_vol=+0.122

**`morning_volume_weighted_momentum`** (Lock IC=+0.0484, Sharpe=-0.3058)
- Admission: Train IC=+0.1559, Deflated=+0.1555, IR=0.59, Mono=0.71, p=0.0024, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.039 | 2017: +0.203 | 2018: +0.126 | 2019: +0.090 | 2020: +0.097 | 2021: +0.088 | 2022: +0.095 | 2023: +0.096 | 2024: +0.115 | 2025: +0.165 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.078 | 2017: +0.280 | 2018: +0.104 | 2019: +0.039 | 2020: +0.117 | 2021: +0.174 | 2022: +0.149 | 2023: +0.283 | 2024: +0.184 | 2025: +0.241 | 2026: -0.108
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.64
- Early IC=+0.1646, Recent IC=+0.1051, 1st-half IC=+0.1083, 2nd-half IC=+0.1049, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.029, Q3_mid=+0.114, Q4=+0.091, Q5_high_vol=+0.124

**`combo_min__opening_drive_thrust_ratio__high_low_sequence_momentum`** (Lock IC=+0.0484, Sharpe=-0.3227)
- Admission: Train IC=+0.2513, Deflated=+0.2508, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.053 | 2017: +0.205 | 2018: +0.189 | 2019: +0.099 | 2020: +0.142 | 2021: +0.112 | 2022: +0.069 | 2023: +0.108 | 2024: +0.148 | 2025: +0.117 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.426 | 2016: +0.195 | 2017: +0.256 | 2018: +0.237 | 2019: +0.294 | 2020: +0.151 | 2021: +0.279 | 2022: +0.257 | 2023: +0.102 | 2024: +0.338 | 2025: +0.120 | 2026: +0.097
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.65
- Early IC=+0.1971, Recent IC=+0.1279, 1st-half IC=+0.1464, 2nd-half IC=+0.1193, Neg regimes=0/5
- Weak component: `high_low_sequence_momentum` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.222, Q2=+0.032, Q3_mid=+0.132, Q4=+0.100, Q5_high_vol=+0.173

**`combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0480, Sharpe=-0.2807)
- Admission: Train IC=+0.2464, Deflated=+0.2461, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.067 | 2017: +0.229 | 2018: +0.178 | 2019: +0.096 | 2020: +0.154 | 2021: +0.054 | 2022: +0.122 | 2023: +0.094 | 2024: +0.099 | 2025: +0.115 | 2026: -0.040
- Yearly Tail ICs:   2015: +0.381 | 2016: +0.097 | 2017: +0.228 | 2018: +0.248 | 2019: +0.166 | 2020: +0.274 | 2021: +0.175 | 2022: +0.245 | 2023: +0.334 | 2024: +0.260 | 2025: +0.032 | 2026: -0.115
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.47
- Early IC=+0.2034, Recent IC=+0.0966, 1st-half IC=+0.1515, 2nd-half IC=+0.1011, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.221, Q2=+0.004, Q3_mid=+0.164, Q4=+0.116, Q5_high_vol=+0.135

**`combo_mean__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0478, Sharpe=-0.8584)
- Admission: Train IC=+0.2406, Deflated=+0.2401, IR=0.85, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.091 | 2017: +0.234 | 2018: +0.258 | 2019: +0.155 | 2020: +0.157 | 2021: +0.133 | 2022: +0.084 | 2023: +0.089 | 2024: +0.150 | 2025: +0.089 | 2026: -0.001
- Yearly Tail ICs:   2015: +0.265 | 2016: -0.002 | 2017: +0.223 | 2018: +0.464 | 2019: +0.155 | 2020: +0.239 | 2021: +0.295 | 2022: +0.208 | 2023: +0.161 | 2024: +0.222 | 2025: +0.048 | 2026: -0.217
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.49
- Early IC=+0.2458, Recent IC=+0.1197, 1st-half IC=+0.1882, 2nd-half IC=+0.1190, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.222, Q2=-0.007, Q3_mid=+0.146, Q4=+0.158, Q5_high_vol=+0.211

**`combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0471, Sharpe=-0.3148)
- Admission: Train IC=+0.1999, Deflated=+0.1994, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.023 | 2017: +0.153 | 2018: +0.141 | 2019: +0.129 | 2020: +0.156 | 2021: +0.129 | 2022: +0.055 | 2023: +0.082 | 2024: +0.105 | 2025: +0.073 | 2026: +0.020
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.049 | 2017: +0.263 | 2018: +0.298 | 2019: +0.311 | 2020: +0.061 | 2021: +0.245 | 2022: -0.024 | 2023: +0.064 | 2024: +0.255 | 2025: -0.114 | 2026: +0.305
- IC CV=0.28, Neg years (linear/tail)=0/1 of 8, Half ratio=0.71, Recency ratio=0.63
- Early IC=+0.1472, Recent IC=+0.0934, 1st-half IC=+0.1400, 2nd-half IC=+0.0989, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.011, Q3_mid=+0.130, Q4=+0.071, Q5_high_vol=+0.204

**`combo_rank_max__max_up_ret__net_volume_flow`** (Lock IC=+0.0469, Sharpe=-1.4510)
- Admission: Train IC=+0.2350, Deflated=+0.2339, IR=0.72, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.102 | 2017: +0.185 | 2018: +0.218 | 2019: +0.083 | 2020: +0.125 | 2021: +0.095 | 2022: +0.106 | 2023: +0.095 | 2024: +0.139 | 2025: +0.102 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.221 | 2017: +0.239 | 2018: +0.288 | 2019: +0.129 | 2020: +0.309 | 2021: +0.299 | 2022: +0.153 | 2023: +0.212 | 2024: +0.308 | 2025: -0.033 | 2026: -0.308
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.83, Recency ratio=0.59
- Early IC=+0.2023, Recent IC=+0.1189, 1st-half IC=+0.1402, 2nd-half IC=+0.1158, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.28)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.000, Q3_mid=+0.103, Q4=+0.136, Q5_high_vol=+0.193

**`combo_mean__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0469, Sharpe=-1.2311)
- Admission: Train IC=+0.2594, Deflated=+0.2588, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.095 | 2017: +0.214 | 2018: +0.198 | 2019: +0.106 | 2020: +0.115 | 2021: +0.099 | 2022: +0.097 | 2023: +0.078 | 2024: +0.153 | 2025: +0.120 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.039 | 2017: +0.255 | 2018: +0.345 | 2019: +0.137 | 2020: +0.180 | 2021: +0.374 | 2022: +0.269 | 2023: +0.219 | 2024: +0.337 | 2025: +0.063 | 2026: -0.260
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.56
- Early IC=+0.2060, Recent IC=+0.1156, 1st-half IC=+0.1444, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.229, Q2=+0.005, Q3_mid=+0.124, Q4=+0.126, Q5_high_vol=+0.159

**`combo_min__trend_day_regime_conviction__first_bar_sentiment`** (Lock IC=+0.0466, Sharpe=-0.1390)
- Admission: Train IC=+0.1889, Deflated=+0.1883, IR=0.45, Mono=0.68, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.092 | 2017: +0.177 | 2018: +0.186 | 2019: +0.110 | 2020: +0.092 | 2021: +0.058 | 2022: +0.084 | 2023: +0.087 | 2024: +0.121 | 2025: +0.118 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.205 | 2016: +0.079 | 2017: +0.259 | 2018: +0.168 | 2019: +0.241 | 2020: +0.076 | 2021: +0.074 | 2022: +0.054 | 2023: +0.213 | 2024: +0.211 | 2025: +0.179 | 2026: +0.067
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.57
- Early IC=+0.1813, Recent IC=+0.1038, 1st-half IC=+0.1279, 2nd-half IC=+0.0923, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.012, Q3_mid=+0.090, Q4=+0.135, Q5_high_vol=+0.154

**`num_up_bars`** (Lock IC=+0.0459, Sharpe=-1.1323)
- Admission: Train IC=+0.1213, Deflated=+0.1198, IR=0.36, Mono=0.65, p=0.0144, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.077 | 2016: +0.103 | 2017: +0.054 | 2018: +0.116 | 2019: +0.074 | 2020: +0.072 | 2021: +0.034 | 2022: +0.131 | 2023: +0.083 | 2024: +0.141 | 2025: +0.117 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.190 | 2016: +0.253 | 2017: +0.002 | 2018: +0.082 | 2019: +0.121 | 2020: +0.184 | 2021: -0.075 | 2022: +0.221 | 2023: +0.122 | 2024: +0.211 | 2025: -0.019 | 2026: -0.077
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=1.47, Recency ratio=1.31
- Early IC=+0.0851, Recent IC=+0.1118, 1st-half IC=+0.0732, 2nd-half IC=+0.1074, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.054, Q3_mid=+0.097, Q4=+0.105, Q5_high_vol=+0.089

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0458, Sharpe=-0.3399)
- Admission: Train IC=+0.2092, Deflated=+0.2085, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.244 | 2016: +0.034 | 2017: +0.153 | 2018: +0.192 | 2019: +0.168 | 2020: +0.190 | 2021: +0.150 | 2022: +0.035 | 2023: +0.094 | 2024: +0.134 | 2025: +0.056 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.008 | 2017: +0.327 | 2018: +0.298 | 2019: +0.306 | 2020: -0.001 | 2021: +0.320 | 2022: +0.079 | 2023: +0.112 | 2024: +0.180 | 2025: +0.032 | 2026: +0.264
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.66, Recency ratio=0.66
- Early IC=+0.1728, Recent IC=+0.1143, 1st-half IC=+0.1669, 2nd-half IC=+0.1104, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.001, Q3_mid=+0.132, Q4=+0.119, Q5_high_vol=+0.222

**`combo_rank_min__opening_drive_thrust_ratio__high_low_sequence_momentum`** (Lock IC=+0.0456, Sharpe=-0.2787)
- Admission: Train IC=+0.2560, Deflated=+0.2556, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.052 | 2017: +0.200 | 2018: +0.193 | 2019: +0.099 | 2020: +0.138 | 2021: +0.119 | 2022: +0.075 | 2023: +0.116 | 2024: +0.146 | 2025: +0.119 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.406 | 2016: +0.215 | 2017: +0.237 | 2018: +0.237 | 2019: +0.305 | 2020: +0.175 | 2021: +0.374 | 2022: +0.285 | 2023: +0.069 | 2024: +0.303 | 2025: +0.121 | 2026: +0.047
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.66
- Early IC=+0.1968, Recent IC=+0.1297, 1st-half IC=+0.1450, 2nd-half IC=+0.1215, Neg regimes=0/5
- Weak component: `high_low_sequence_momentum` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.224, Q2=+0.029, Q3_mid=+0.133, Q4=+0.100, Q5_high_vol=+0.174

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0453, Sharpe=-0.8924)
- Admission: Train IC=+0.2303, Deflated=+0.2293, IR=0.99, Mono=0.85, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.102 | 2017: +0.203 | 2018: +0.217 | 2019: +0.144 | 2020: +0.152 | 2021: +0.126 | 2022: +0.062 | 2023: +0.118 | 2024: +0.155 | 2025: +0.097 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.529 | 2016: +0.284 | 2017: +0.348 | 2018: +0.372 | 2019: +0.202 | 2020: +0.194 | 2021: +0.265 | 2022: +0.183 | 2023: +0.221 | 2024: +0.180 | 2025: -0.155 | 2026: -0.059
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.65
- Early IC=+0.2099, Recent IC=+0.1365, 1st-half IC=+0.1642, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.015, Q3_mid=+0.146, Q4=+0.118, Q5_high_vol=+0.217

**`combo_clamp_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0447, Sharpe=-0.9029)
- Admission: Train IC=+0.2463, Deflated=+0.2457, IR=0.72, Mono=0.74, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.315 | 2016: +0.116 | 2017: +0.191 | 2018: +0.217 | 2019: +0.121 | 2020: +0.146 | 2021: +0.154 | 2022: +0.059 | 2023: +0.095 | 2024: +0.130 | 2025: +0.016 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.425 | 2016: +0.126 | 2017: +0.414 | 2018: +0.340 | 2019: +0.327 | 2020: +0.081 | 2021: +0.217 | 2022: +0.160 | 2023: +0.123 | 2024: +0.212 | 2025: -0.059 | 2026: -0.043
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.55
- Early IC=+0.2041, Recent IC=+0.1125, 1st-half IC=+0.1578, 2nd-half IC=+0.1092, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.002, Q3_mid=+0.078, Q4=+0.159, Q5_high_vol=+0.211

**`combo_tri_median__max_up_ret__net_volume_flow__body_size_progression`** (Lock IC=+0.0438, Sharpe=-0.8237)
- Admission: Train IC=+0.1627, Deflated=+0.1617, IR=0.56, Mono=0.69, p=0.0014, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.118 | 2016: +0.084 | 2017: +0.100 | 2018: +0.140 | 2019: +0.071 | 2020: +0.077 | 2021: +0.110 | 2022: +0.120 | 2023: +0.117 | 2024: +0.113 | 2025: +0.143 | 2026: -0.092
- Yearly Tail ICs:   2015: +0.243 | 2016: +0.142 | 2017: +0.121 | 2018: +0.237 | 2019: +0.149 | 2020: +0.123 | 2021: +0.298 | 2022: +0.100 | 2023: +0.136 | 2024: +0.160 | 2025: +0.168 | 2026: -0.378
- IC CV=0.20, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=0.96
- Early IC=+0.1200, Recent IC=+0.1151, 1st-half IC=+0.0869, 2nd-half IC=+0.1179, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.010, Q3_mid=+0.115, Q4=+0.108, Q5_high_vol=+0.114

**`first_30min_return`** (Lock IC=+0.0435, Sharpe=-0.2385)
- Admission: Train IC=+0.1669, Deflated=+0.1665, IR=0.69, Mono=0.76, p=0.0010, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.64
- Early IC=+0.1677, Recent IC=+0.1078, 1st-half IC=+0.1101, 2nd-half IC=+0.1064, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.027, Q3_mid=+0.106, Q4=+0.087, Q5_high_vol=+0.128

**`open_to_current_return`** (Lock IC=+0.0435, Sharpe=-0.2385)
- Admission: Train IC=+0.1669, Deflated=+0.1665, IR=0.69, Mono=0.76, p=0.0010, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.97, Recency ratio=0.64
- Early IC=+0.1677, Recent IC=+0.1078, 1st-half IC=+0.1101, 2nd-half IC=+0.1064, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.027, Q3_mid=+0.106, Q4=+0.087, Q5_high_vol=+0.128

**`combo_rank_min__max_up_ret__bar_ret_0`** (Lock IC=+0.0429, Sharpe=-0.2027)
- Admission: Train IC=+0.1999, Deflated=+0.1991, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.097 | 2017: +0.204 | 2018: +0.243 | 2019: +0.143 | 2020: +0.122 | 2021: +0.089 | 2022: +0.070 | 2023: +0.076 | 2024: +0.101 | 2025: +0.085 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.160 | 2016: +0.150 | 2017: +0.211 | 2018: +0.461 | 2019: +0.219 | 2020: +0.252 | 2021: +0.194 | 2022: +0.005 | 2023: +0.056 | 2024: +0.209 | 2025: +0.141 | 2026: -0.124
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.39
- Early IC=+0.2262, Recent IC=+0.0880, 1st-half IC=+0.1604, 2nd-half IC=+0.0830, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.022, Q3_mid=+0.110, Q4=+0.138, Q5_high_vol=+0.168

**`combo_rank_min__max_up_ret__first_bar_return`** (Lock IC=+0.0429, Sharpe=-0.2027)
- Admission: Train IC=+0.1999, Deflated=+0.1991, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.097 | 2017: +0.204 | 2018: +0.243 | 2019: +0.143 | 2020: +0.122 | 2021: +0.089 | 2022: +0.070 | 2023: +0.076 | 2024: +0.101 | 2025: +0.085 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.160 | 2016: +0.150 | 2017: +0.211 | 2018: +0.461 | 2019: +0.219 | 2020: +0.252 | 2021: +0.194 | 2022: +0.005 | 2023: +0.056 | 2024: +0.209 | 2025: +0.141 | 2026: -0.124
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.39
- Early IC=+0.2262, Recent IC=+0.0880, 1st-half IC=+0.1604, 2nd-half IC=+0.0830, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.022, Q3_mid=+0.110, Q4=+0.138, Q5_high_vol=+0.168

**`combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0426, Sharpe=-0.2324)
- Admission: Train IC=+0.2524, Deflated=+0.2516, IR=1.00, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.091 | 2017: +0.133 | 2018: +0.260 | 2019: +0.169 | 2020: +0.173 | 2021: +0.170 | 2022: +0.068 | 2023: +0.082 | 2024: +0.141 | 2025: +0.069 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.147 | 2017: +0.318 | 2018: +0.603 | 2019: +0.185 | 2020: +0.175 | 2021: +0.302 | 2022: +0.166 | 2023: +0.260 | 2024: +0.201 | 2025: -0.037 | 2026: +0.018
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.57
- Early IC=+0.1963, Recent IC=+0.1112, 1st-half IC=+0.1767, 2nd-half IC=+0.1173, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.015, Q3_mid=+0.105, Q4=+0.119, Q5_high_vol=+0.256

**`combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0423, Sharpe=-0.6060)
- Admission: Train IC=+0.2578, Deflated=+0.2576, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.041 | 2017: +0.183 | 2018: +0.163 | 2019: +0.075 | 2020: +0.105 | 2021: +0.091 | 2022: +0.072 | 2023: +0.113 | 2024: +0.139 | 2025: +0.109 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.390 | 2016: +0.233 | 2017: +0.268 | 2018: +0.290 | 2019: +0.235 | 2020: +0.157 | 2021: +0.298 | 2022: +0.289 | 2023: +0.175 | 2024: +0.327 | 2025: +0.057 | 2026: +0.050
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=0.73
- Early IC=+0.1734, Recent IC=+0.1257, 1st-half IC=+0.1205, 2nd-half IC=+0.1116, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.027, Q3_mid=+0.104, Q4=+0.085, Q5_high_vol=+0.153

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction`** (Lock IC=+0.0419, Sharpe=-1.0138)
- Admission: Train IC=+0.2381, Deflated=+0.2375, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.071 | 2017: +0.182 | 2018: +0.186 | 2019: +0.117 | 2020: +0.126 | 2021: +0.119 | 2022: +0.074 | 2023: +0.122 | 2024: +0.154 | 2025: +0.122 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.395 | 2016: +0.237 | 2017: +0.291 | 2018: +0.267 | 2019: +0.276 | 2020: +0.133 | 2021: +0.264 | 2022: +0.223 | 2023: +0.190 | 2024: +0.313 | 2025: +0.009 | 2026: +0.101
- IC CV=0.26, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.75
- Early IC=+0.1840, Recent IC=+0.1378, 1st-half IC=+0.1381, 2nd-half IC=+0.1240, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.031, Q3_mid=+0.128, Q4=+0.093, Q5_high_vol=+0.182

**`combo_max__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0413, Sharpe=-0.2764)
- Admission: Train IC=+0.1819, Deflated=+0.1813, IR=0.46, Mono=0.70, p=0.0002, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.065 | 2017: +0.161 | 2018: +0.110 | 2019: +0.041 | 2020: +0.097 | 2021: +0.059 | 2022: +0.103 | 2023: +0.078 | 2024: +0.130 | 2025: +0.144 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.138 | 2017: +0.204 | 2018: +0.107 | 2019: +0.095 | 2020: +0.229 | 2021: +0.234 | 2022: +0.141 | 2023: +0.105 | 2024: +0.332 | 2025: +0.036 | 2026: -0.074
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=0.76
- Early IC=+0.1355, Recent IC=+0.1036, 1st-half IC=+0.0909, 2nd-half IC=+0.1010, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.012, Q3_mid=+0.117, Q4=+0.094, Q5_high_vol=+0.077

**`combo_sig_product__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0411, Sharpe=-0.4576)
- Admission: Train IC=+0.1983, Deflated=+0.1986, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.117 | 2017: +0.144 | 2018: +0.239 | 2019: +0.147 | 2020: +0.089 | 2021: +0.099 | 2022: +0.063 | 2023: +0.060 | 2024: +0.104 | 2025: +0.090 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.43
- Early IC=+0.1915, Recent IC=+0.0822, 1st-half IC=+0.1494, 2nd-half IC=+0.0811, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.028, Q3_mid=+0.096, Q4=+0.141, Q5_high_vol=+0.168

**`combo_sig_product__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0410, Sharpe=-0.4576)
- Admission: Train IC=+0.1983, Deflated=+0.1986, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.117 | 2017: +0.144 | 2018: +0.239 | 2019: +0.147 | 2020: +0.089 | 2021: +0.099 | 2022: +0.063 | 2023: +0.060 | 2024: +0.104 | 2025: +0.090 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.43
- Early IC=+0.1912, Recent IC=+0.0822, 1st-half IC=+0.1494, 2nd-half IC=+0.0810, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.157, Q2=-0.028, Q3_mid=+0.095, Q4=+0.141, Q5_high_vol=+0.168

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0406, Sharpe=-1.4083)
- Admission: Train IC=+0.2700, Deflated=+0.2690, IR=1.19, Mono=0.87, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.084 | 2017: +0.227 | 2018: +0.211 | 2019: +0.123 | 2020: +0.152 | 2021: +0.131 | 2022: +0.092 | 2023: +0.112 | 2024: +0.158 | 2025: +0.106 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.239 | 2017: +0.276 | 2018: +0.342 | 2019: +0.238 | 2020: +0.198 | 2021: +0.307 | 2022: +0.234 | 2023: +0.347 | 2024: +0.214 | 2025: -0.113 | 2026: -0.303
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.79, Recency ratio=0.61
- Early IC=+0.2193, Recent IC=+0.1347, 1st-half IC=+0.1653, 2nd-half IC=+0.1298, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.231, Q2=+0.012, Q3_mid=+0.139, Q4=+0.142, Q5_high_vol=+0.202

**`first_bar_return`** (Lock IC=+0.0404, Sharpe=-0.4576)
- Admission: Train IC=+0.1983, Deflated=+0.1986, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.43
- Early IC=+0.1956, Recent IC=+0.0842, 1st-half IC=+0.1504, 2nd-half IC=+0.0820, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.027, Q3_mid=+0.096, Q4=+0.144, Q5_high_vol=+0.166

**`combo_mean__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0404, Sharpe=-0.4576)
- Admission: Train IC=+0.1983, Deflated=+0.1986, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.43
- Early IC=+0.1956, Recent IC=+0.0842, 1st-half IC=+0.1504, 2nd-half IC=+0.0820, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.162, Q2=-0.027, Q3_mid=+0.096, Q4=+0.144, Q5_high_vol=+0.166

**`vwap_trend_channel_slope`** (Lock IC=+0.0398, Sharpe=-0.3845)
- Admission: Train IC=+0.1370, Deflated=+0.1363, IR=0.58, Mono=0.69, p=0.0064, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.12, Recency ratio=0.88
- Early IC=+0.1257, Recent IC=+0.1111, 1st-half IC=+0.0899, 2nd-half IC=+0.1007, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.055, Q3_mid=+0.085, Q4=+0.046, Q5_high_vol=+0.095

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0393, Sharpe=-1.9156)
- Admission: Train IC=+0.2144, Deflated=+0.2132, IR=0.79, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.105 | 2017: +0.232 | 2018: +0.207 | 2019: +0.102 | 2020: +0.169 | 2021: +0.127 | 2022: +0.107 | 2023: +0.086 | 2024: +0.145 | 2025: +0.079 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.216 | 2016: +0.252 | 2017: +0.298 | 2018: +0.369 | 2019: +0.154 | 2020: +0.163 | 2021: +0.296 | 2022: +0.094 | 2023: +0.256 | 2024: +0.242 | 2025: -0.110 | 2026: -0.277
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.53
- Early IC=+0.2195, Recent IC=+0.1153, 1st-half IC=+0.1664, 2nd-half IC=+0.1228, Neg regimes=1/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.238, Q2=-0.004, Q3_mid=+0.129, Q4=+0.153, Q5_high_vol=+0.197

**`combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0390, Sharpe=-0.6507)
- Admission: Train IC=+0.2363, Deflated=+0.2358, IR=0.79, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.044 | 2017: +0.219 | 2018: +0.157 | 2019: +0.077 | 2020: +0.135 | 2021: +0.095 | 2022: +0.085 | 2023: +0.101 | 2024: +0.139 | 2025: +0.116 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.249 | 2017: +0.377 | 2018: +0.238 | 2019: +0.144 | 2020: +0.220 | 2021: +0.248 | 2022: +0.181 | 2023: +0.200 | 2024: +0.325 | 2025: +0.079 | 2026: -0.169
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.64
- Early IC=+0.1877, Recent IC=+0.1197, 1st-half IC=+0.1373, 2nd-half IC=+0.1107, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.219, Q2=+0.011, Q3_mid=+0.135, Q4=+0.112, Q5_high_vol=+0.149

**`combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0388, Sharpe=-1.1420)
- Admission: Train IC=+0.2278, Deflated=+0.2276, IR=0.87, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.226 | 2018: +0.241 | 2019: +0.145 | 2020: +0.142 | 2021: +0.169 | 2022: +0.092 | 2023: +0.108 | 2024: +0.150 | 2025: +0.088 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.336 | 2016: -0.072 | 2017: +0.187 | 2018: +0.368 | 2019: +0.218 | 2020: +0.248 | 2021: +0.353 | 2022: +0.155 | 2023: +0.156 | 2024: +0.280 | 2025: -0.017 | 2026: -0.111
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.55
- Early IC=+0.2336, Recent IC=+0.1290, 1st-half IC=+0.1699, 2nd-half IC=+0.1370, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.261, Q2=-0.010, Q3_mid=+0.143, Q4=+0.155, Q5_high_vol=+0.203

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0383, Sharpe=-0.5921)
- Admission: Train IC=+0.2273, Deflated=+0.2272, IR=0.59, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.062 | 2017: +0.236 | 2018: +0.134 | 2019: +0.080 | 2020: +0.161 | 2021: +0.091 | 2022: +0.106 | 2023: +0.114 | 2024: +0.077 | 2025: +0.098 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.290 | 2016: +0.065 | 2017: +0.393 | 2018: +0.242 | 2019: +0.055 | 2020: +0.236 | 2021: +0.277 | 2022: +0.222 | 2023: +0.074 | 2024: +0.291 | 2025: +0.094 | 2026: -0.203
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.52
- Early IC=+0.1853, Recent IC=+0.0957, 1st-half IC=+0.1460, 2nd-half IC=+0.1003, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.010, Q3_mid=+0.176, Q4=+0.086, Q5_high_vol=+0.130

**`combo_tri_median__max_up_ret__smooth_momentum_structure__net_volume_flow`** (Lock IC=+0.0379, Sharpe=-0.6625)
- Admission: Train IC=+0.1550, Deflated=+0.1542, IR=0.54, Mono=0.70, p=0.0024, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.128 | 2016: +0.075 | 2017: +0.097 | 2018: +0.128 | 2019: +0.068 | 2020: +0.067 | 2021: +0.091 | 2022: +0.114 | 2023: +0.086 | 2024: +0.121 | 2025: +0.119 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.172 | 2016: +0.156 | 2017: +0.064 | 2018: +0.170 | 2019: +0.163 | 2020: +0.045 | 2021: +0.300 | 2022: +0.106 | 2023: +0.077 | 2024: +0.277 | 2025: +0.145 | 2026: -0.284
- IC CV=0.22, Neg years (linear/tail)=0/0 of 8, Half ratio=1.32, Recency ratio=0.92
- Early IC=+0.1128, Recent IC=+0.1035, 1st-half IC=+0.0816, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.003, Q3_mid=+0.105, Q4=+0.113, Q5_high_vol=+0.104

**`combo_mean__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0378, Sharpe=-0.8881)
- Admission: Train IC=+0.2530, Deflated=+0.2530, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.072 | 2017: +0.181 | 2018: +0.184 | 2019: +0.074 | 2020: +0.106 | 2021: +0.086 | 2022: +0.088 | 2023: +0.086 | 2024: +0.116 | 2025: +0.118 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.278 | 2016: -0.023 | 2017: +0.249 | 2018: +0.433 | 2019: +0.174 | 2020: +0.174 | 2021: +0.240 | 2022: +0.262 | 2023: +0.257 | 2024: +0.271 | 2025: +0.071 | 2026: -0.306
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.75, Recency ratio=0.55
- Early IC=+0.1824, Recent IC=+0.1011, 1st-half IC=+0.1278, 2nd-half IC=+0.0963, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.004, Q3_mid=+0.112, Q4=+0.118, Q5_high_vol=+0.142

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0376, Sharpe=-1.6484)
- Admission: Train IC=+0.2120, Deflated=+0.2108, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.094 | 2017: +0.235 | 2018: +0.223 | 2019: +0.107 | 2020: +0.153 | 2021: +0.154 | 2022: +0.123 | 2023: +0.098 | 2024: +0.145 | 2025: +0.078 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.103 | 2017: +0.148 | 2018: +0.362 | 2019: +0.318 | 2020: +0.098 | 2021: +0.316 | 2022: +0.211 | 2023: -0.005 | 2024: +0.273 | 2025: +0.022 | 2026: -0.232
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=0.81, Recency ratio=0.53
- Early IC=+0.2282, Recent IC=+0.1214, 1st-half IC=+0.1660, 2nd-half IC=+0.1349, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.245, Q2=+0.007, Q3_mid=+0.125, Q4=+0.154, Q5_high_vol=+0.217

**`combo_sig_product__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0353, Sharpe=-0.9746)
- Admission: Train IC=+0.2002, Deflated=+0.1999, IR=0.43, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.130 | 2016: +0.061 | 2017: +0.154 | 2018: +0.128 | 2019: +0.053 | 2020: +0.084 | 2021: +0.074 | 2022: +0.107 | 2023: +0.068 | 2024: +0.114 | 2025: +0.147 | 2026: -0.103
- Yearly Tail ICs:   2015: +0.180 | 2016: +0.133 | 2017: +0.135 | 2018: +0.142 | 2019: +0.132 | 2020: +0.274 | 2021: +0.217 | 2022: +0.118 | 2023: +0.118 | 2024: +0.211 | 2025: +0.009 | 2026: -0.159
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=0.64
- Early IC=+0.1412, Recent IC=+0.0910, 1st-half IC=+0.0936, 2nd-half IC=+0.0981, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.021, Q3_mid=+0.110, Q4=+0.096, Q5_high_vol=+0.095

**`combo_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0349, Sharpe=-1.7365)
- Admission: Train IC=+0.2199, Deflated=+0.2190, IR=0.73, Mono=0.75, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.102 | 2017: +0.217 | 2018: +0.209 | 2019: +0.094 | 2020: +0.130 | 2021: +0.087 | 2022: +0.100 | 2023: +0.094 | 2024: +0.130 | 2025: +0.090 | 2026: -0.039
- Yearly Tail ICs:   2015: +0.235 | 2016: +0.204 | 2017: +0.200 | 2018: +0.434 | 2019: +0.220 | 2020: +0.141 | 2021: +0.287 | 2022: +0.117 | 2023: +0.208 | 2024: +0.252 | 2025: -0.106 | 2026: -0.333
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.53
- Early IC=+0.2131, Recent IC=+0.1122, 1st-half IC=+0.1490, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.007, Q3_mid=+0.116, Q4=+0.118, Q5_high_vol=+0.193

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0337, Sharpe=-1.4167)
- Admission: Train IC=+0.2577, Deflated=+0.2564, IR=0.87, Mono=0.81, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.106 | 2017: +0.201 | 2018: +0.209 | 2019: +0.129 | 2020: +0.142 | 2021: +0.089 | 2022: +0.105 | 2023: +0.119 | 2024: +0.137 | 2025: +0.119 | 2026: -0.052
- Yearly Tail ICs:   2015: +0.218 | 2016: +0.254 | 2017: +0.358 | 2018: +0.384 | 2019: +0.236 | 2020: +0.249 | 2021: +0.298 | 2022: +0.163 | 2023: +0.132 | 2024: +0.354 | 2025: -0.127 | 2026: -0.132
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.73, Recency ratio=0.62
- Early IC=+0.2048, Recent IC=+0.1279, 1st-half IC=+0.1552, 2nd-half IC=+0.1139, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.010, Q3_mid=+0.120, Q4=+0.127, Q5_high_vol=+0.210

**`combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0336, Sharpe=-1.0604)
- Admission: Train IC=+0.2405, Deflated=+0.2399, IR=0.72, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.065 | 2017: +0.195 | 2018: +0.156 | 2019: +0.064 | 2020: +0.118 | 2021: +0.079 | 2022: +0.109 | 2023: +0.103 | 2024: +0.117 | 2025: +0.127 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.285 | 2016: +0.235 | 2017: +0.316 | 2018: +0.343 | 2019: +0.084 | 2020: +0.202 | 2021: +0.240 | 2022: +0.160 | 2023: +0.219 | 2024: +0.252 | 2025: +0.044 | 2026: -0.265
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.89, Recency ratio=0.63
- Early IC=+0.1753, Recent IC=+0.1102, 1st-half IC=+0.1217, 2nd-half IC=+0.1082, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.016, Q3_mid=+0.114, Q4=+0.100, Q5_high_vol=+0.148

**`combo_diff__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0331, Sharpe=-0.5641)
- Admission: Train IC=+0.2460, Deflated=+0.2450, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.092 | 2017: +0.141 | 2018: +0.252 | 2019: +0.168 | 2020: +0.188 | 2021: +0.168 | 2022: +0.051 | 2023: +0.109 | 2024: +0.157 | 2025: +0.049 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.215 | 2017: +0.360 | 2018: +0.554 | 2019: +0.231 | 2020: +0.140 | 2021: +0.293 | 2022: +0.135 | 2023: +0.177 | 2024: +0.248 | 2025: -0.111 | 2026: +0.008
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.68
- Early IC=+0.1964, Recent IC=+0.1329, 1st-half IC=+0.1838, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.013, Q3_mid=+0.127, Q4=+0.125, Q5_high_vol=+0.255

**`vwap_close_divergence_trend`** (Lock IC=+0.0323, Sharpe=-0.2960)
- Admission: Train IC=+0.1534, Deflated=+0.1529, IR=0.60, Mono=0.70, p=0.0024, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.112 | 2016: +0.023 | 2017: +0.184 | 2018: +0.055 | 2019: +0.091 | 2020: +0.075 | 2021: +0.069 | 2022: +0.094 | 2023: +0.107 | 2024: +0.092 | 2025: +0.133 | 2026: -0.094
- Yearly Tail ICs:   2015: +0.081 | 2016: +0.019 | 2017: +0.138 | 2018: +0.210 | 2019: +0.269 | 2020: +0.030 | 2021: +0.253 | 2022: +0.060 | 2023: +0.292 | 2024: +0.110 | 2025: +0.182 | 2026: -0.357
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=0.83
- Early IC=+0.1195, Recent IC=+0.0992, 1st-half IC=+0.0846, 2nd-half IC=+0.1005, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.058, Q3_mid=+0.094, Q4=+0.045, Q5_high_vol=+0.084

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0316, Sharpe=-0.2324)
- Admission: Train IC=+0.2424, Deflated=+0.2416, IR=0.93, Mono=0.81, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.109 | 2017: +0.142 | 2018: +0.285 | 2019: +0.176 | 2020: +0.171 | 2021: +0.171 | 2022: +0.054 | 2023: +0.100 | 2024: +0.158 | 2025: +0.057 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.204 | 2017: +0.304 | 2018: +0.602 | 2019: +0.184 | 2020: +0.130 | 2021: +0.293 | 2022: +0.165 | 2023: +0.256 | 2024: +0.191 | 2025: -0.034 | 2026: +0.013
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.60
- Early IC=+0.2138, Recent IC=+0.1293, 1st-half IC=+0.1855, 2nd-half IC=+0.1228, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.006, Q3_mid=+0.128, Q4=+0.134, Q5_high_vol=+0.260

**`combo_rank_max__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0313, Sharpe=-1.0053)
- Admission: Train IC=+0.1877, Deflated=+0.1871, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.048 | 2017: +0.073 | 2018: +0.174 | 2019: +0.107 | 2020: +0.078 | 2021: +0.117 | 2022: +0.110 | 2023: +0.060 | 2024: +0.109 | 2025: +0.080 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.134 | 2016: -0.210 | 2017: +0.088 | 2018: +0.249 | 2019: +0.227 | 2020: +0.232 | 2021: +0.129 | 2022: +0.240 | 2023: +0.297 | 2024: +0.359 | 2025: +0.037 | 2026: -0.316
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.07, Recency ratio=0.69
- Early IC=+0.1235, Recent IC=+0.0847, 1st-half IC=+0.0987, 2nd-half IC=+0.1058, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.109, Q2=-0.020, Q3_mid=+0.115, Q4=+0.165, Q5_high_vol=+0.128

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0312, Sharpe=-1.4583)
- Admission: Train IC=+0.2596, Deflated=+0.2597, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.080 | 2017: +0.213 | 2018: +0.166 | 2019: +0.111 | 2020: +0.168 | 2021: +0.051 | 2022: +0.112 | 2023: +0.118 | 2024: +0.088 | 2025: +0.103 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.304 | 2016: -0.051 | 2017: +0.300 | 2018: +0.224 | 2019: +0.292 | 2020: +0.226 | 2021: +0.187 | 2022: +0.241 | 2023: +0.284 | 2024: +0.228 | 2025: -0.037 | 2026: -0.099
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.64, Recency ratio=0.54
- Early IC=+0.1900, Recent IC=+0.1031, 1st-half IC=+0.1557, 2nd-half IC=+0.0998, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.205, Q2=+0.017, Q3_mid=+0.179, Q4=+0.098, Q5_high_vol=+0.144

**`max_up_ret`** (Lock IC=+0.0308, Sharpe=-1.6524)
- Admission: Train IC=+0.2006, Deflated=+0.1991, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.28, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.61
- Early IC=+0.2011, Recent IC=+0.1236, 1st-half IC=+0.1370, 2nd-half IC=+0.1238, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.016, Q3_mid=+0.113, Q4=+0.122, Q5_high_vol=+0.206

**`combo_mean__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0297, Sharpe=-1.4140)
- Admission: Train IC=+0.1980, Deflated=+0.1968, IR=0.52, Mono=0.70, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.122 | 2017: +0.178 | 2018: +0.235 | 2019: +0.115 | 2020: +0.128 | 2021: +0.127 | 2022: +0.107 | 2023: +0.085 | 2024: +0.146 | 2025: +0.088 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.234 | 2017: +0.220 | 2018: +0.446 | 2019: +0.243 | 2020: +0.167 | 2021: +0.204 | 2022: -0.053 | 2023: +0.146 | 2024: +0.192 | 2025: -0.035 | 2026: -0.196
- IC CV=0.31, Neg years (linear/tail)=0/1 of 8, Half ratio=0.82, Recency ratio=0.56
- Early IC=+0.2062, Recent IC=+0.1156, 1st-half IC=+0.1490, 2nd-half IC=+0.1218, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.006, Q3_mid=+0.115, Q4=+0.162, Q5_high_vol=+0.205

**`combo_min__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0291, Sharpe=-0.6661)
- Admission: Train IC=+0.2084, Deflated=+0.2077, IR=0.59, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.064 | 2017: +0.172 | 2018: +0.114 | 2019: +0.049 | 2020: +0.088 | 2021: +0.094 | 2022: +0.101 | 2023: +0.098 | 2024: +0.129 | 2025: +0.132 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.158 | 2017: +0.343 | 2018: +0.341 | 2019: +0.053 | 2020: +0.182 | 2021: +0.181 | 2022: +0.203 | 2023: +0.061 | 2024: +0.296 | 2025: +0.050 | 2026: -0.210
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=1.20, Recency ratio=0.80
- Early IC=+0.1427, Recent IC=+0.1136, 1st-half IC=+0.0916, 2nd-half IC=+0.1097, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.015, Q3_mid=+0.096, Q4=+0.087, Q5_high_vol=+0.119

**`combo_sig_product__max_up_ret__early_body_momentum`** (Lock IC=+0.0290, Sharpe=-0.5714)
- Admission: Train IC=+0.2127, Deflated=+0.2115, IR=0.45, Mono=0.69, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.188 | 2017: +0.145 | 2018: +0.151 | 2019: +0.052 | 2020: +0.142 | 2021: +0.088 | 2022: +0.092 | 2023: +0.088 | 2024: +0.148 | 2025: +0.079 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.362 | 2016: +0.193 | 2017: +0.189 | 2018: +0.172 | 2019: +0.128 | 2020: +0.311 | 2021: +0.239 | 2022: +0.076 | 2023: +0.099 | 2024: +0.292 | 2025: -0.085 | 2026: -0.155
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.80
- Early IC=+0.1481, Recent IC=+0.1178, 1st-half IC=+0.1152, 2nd-half IC=+0.1055, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.003, Q3_mid=+0.083, Q4=+0.098, Q5_high_vol=+0.176

**`combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0290, Sharpe=-0.9127)
- Admission: Train IC=+0.1309, Deflated=+0.1303, IR=0.49, Mono=0.69, p=0.0092, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.052 | 2017: +0.089 | 2018: +0.180 | 2019: +0.118 | 2020: +0.076 | 2021: +0.132 | 2022: +0.075 | 2023: +0.063 | 2024: +0.138 | 2025: +0.050 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.177 | 2016: -0.252 | 2017: +0.150 | 2018: +0.198 | 2019: +0.296 | 2020: -0.018 | 2021: +0.188 | 2022: +0.180 | 2023: +0.134 | 2024: +0.408 | 2025: -0.065 | 2026: -0.312
- IC CV=0.34, Neg years (linear/tail)=0/1 of 8, Half ratio=1.05, Recency ratio=0.75
- Early IC=+0.1346, Recent IC=+0.1004, 1st-half IC=+0.1042, 2nd-half IC=+0.1091, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.133, Q2=-0.010, Q3_mid=+0.110, Q4=+0.137, Q5_high_vol=+0.151

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0289, Sharpe=-0.4555)
- Admission: Train IC=+0.2882, Deflated=+0.2875, IR=0.82, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.103 | 2017: +0.142 | 2018: +0.284 | 2019: +0.177 | 2020: +0.173 | 2021: +0.171 | 2022: +0.055 | 2023: +0.093 | 2024: +0.161 | 2025: +0.060 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.093 | 2017: +0.301 | 2018: +0.612 | 2019: +0.247 | 2020: +0.024 | 2021: +0.311 | 2022: +0.155 | 2023: +0.095 | 2024: +0.368 | 2025: +0.165 | 2026: -0.193
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.59
- Early IC=+0.2133, Recent IC=+0.1268, 1st-half IC=+0.1870, 2nd-half IC=+0.1223, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.005, Q3_mid=+0.133, Q4=+0.139, Q5_high_vol=+0.259

**`combo_rank_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0288, Sharpe=-1.9401)
- Admission: Train IC=+0.2306, Deflated=+0.2300, IR=0.86, Mono=0.82, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=0.66
- Early IC=+0.1956, Recent IC=+0.1299, 1st-half IC=+0.1403, 2nd-half IC=+0.1288, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.004, Q3_mid=+0.110, Q4=+0.141, Q5_high_vol=+0.218

**`combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction`** (Lock IC=+0.0287, Sharpe=-0.6970)
- Admission: Train IC=+0.1884, Deflated=+0.1883, IR=0.46, Mono=0.66, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.151 | 2016: +0.070 | 2017: +0.207 | 2018: +0.161 | 2019: +0.115 | 2020: +0.168 | 2021: +0.050 | 2022: +0.121 | 2023: +0.100 | 2024: +0.104 | 2025: +0.087 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.085 | 2017: +0.255 | 2018: +0.212 | 2019: +0.227 | 2020: +0.127 | 2021: -0.008 | 2022: +0.141 | 2023: +0.139 | 2024: +0.256 | 2025: +0.012 | 2026: +0.067
- IC CV=0.35, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.55
- Early IC=+0.1838, Recent IC=+0.1019, 1st-half IC=+0.1553, 2nd-half IC=+0.1017, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.034, Q3_mid=+0.177, Q4=+0.096, Q5_high_vol=+0.142

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0286, Sharpe=-1.4997)
- Admission: Train IC=+0.2207, Deflated=+0.2196, IR=0.79, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.100 | 2017: +0.259 | 2018: +0.198 | 2019: +0.115 | 2020: +0.163 | 2021: +0.118 | 2022: +0.109 | 2023: +0.077 | 2024: +0.144 | 2025: +0.070 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.220 | 2017: +0.238 | 2018: +0.437 | 2019: +0.173 | 2020: +0.138 | 2021: +0.239 | 2022: +0.136 | 2023: +0.192 | 2024: +0.262 | 2025: -0.161 | 2026: -0.333
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.48
- Early IC=+0.2284, Recent IC=+0.1101, 1st-half IC=+0.1700, 2nd-half IC=+0.1184, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.232, Q2=+0.008, Q3_mid=+0.128, Q4=+0.140, Q5_high_vol=+0.206

**`combo_mean__max_up_ret__bar_ret_0`** (Lock IC=+0.0282, Sharpe=-0.9455)
- Admission: Train IC=+0.2186, Deflated=+0.2178, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.110 | 2017: +0.192 | 2018: +0.241 | 2019: +0.136 | 2020: +0.113 | 2021: +0.137 | 2022: +0.101 | 2023: +0.098 | 2024: +0.141 | 2025: +0.077 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.127 | 2017: +0.255 | 2018: +0.462 | 2019: +0.112 | 2020: +0.236 | 2021: +0.268 | 2022: +0.108 | 2023: +0.143 | 2024: +0.136 | 2025: +0.044 | 2026: -0.239
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.55
- Early IC=+0.2164, Recent IC=+0.1197, 1st-half IC=+0.1560, 2nd-half IC=+0.1182, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.208, Q2=-0.013, Q3_mid=+0.109, Q4=+0.148, Q5_high_vol=+0.211

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=+0.0281, Sharpe=-0.9455)
- Admission: Train IC=+0.2184, Deflated=+0.2177, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.110 | 2017: +0.192 | 2018: +0.241 | 2019: +0.136 | 2020: +0.113 | 2021: +0.138 | 2022: +0.101 | 2023: +0.098 | 2024: +0.142 | 2025: +0.077 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.127 | 2017: +0.255 | 2018: +0.462 | 2019: +0.112 | 2020: +0.236 | 2021: +0.269 | 2022: +0.108 | 2023: +0.143 | 2024: +0.138 | 2025: +0.044 | 2026: -0.239
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.76, Recency ratio=0.55
- Early IC=+0.2165, Recent IC=+0.1196, 1st-half IC=+0.1561, 2nd-half IC=+0.1182, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.207, Q2=-0.013, Q3_mid=+0.109, Q4=+0.148, Q5_high_vol=+0.211

**`combo_sig_product__max_up_ret__high_low_sequence_momentum`** (Lock IC=+0.0281, Sharpe=-0.8940)
- Admission: Train IC=+0.1607, Deflated=+0.1599, IR=0.42, Mono=0.66, p=0.0018, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.145 | 2017: +0.103 | 2018: +0.134 | 2019: +0.065 | 2020: +0.132 | 2021: +0.051 | 2022: +0.114 | 2023: +0.100 | 2024: +0.149 | 2025: +0.076 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.285 | 2016: +0.170 | 2017: +0.185 | 2018: +0.157 | 2019: +0.164 | 2020: +0.179 | 2021: -0.033 | 2022: +0.131 | 2023: +0.080 | 2024: +0.224 | 2025: -0.066 | 2026: +0.061
- IC CV=0.30, Neg years (linear/tail)=0/1 of 8, Half ratio=1.03, Recency ratio=1.05
- Early IC=+0.1186, Recent IC=+0.1243, 1st-half IC=+0.1045, 2nd-half IC=+0.1073, Neg regimes=0/5
- Weak component: `high_low_sequence_momentum` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.016, Q3_mid=+0.068, Q4=+0.089, Q5_high_vol=+0.184

**`combo_sig_product__high_low_sequence_momentum__first_bar_return`** (Lock IC=+0.0279, Sharpe=-0.5752)
- Admission: Train IC=+0.1638, Deflated=+0.1646, IR=0.44, Mono=0.67, p=0.0014, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.119 | 2016: +0.004 | 2017: +0.150 | 2018: +0.180 | 2019: +0.078 | 2020: +0.065 | 2021: +0.075 | 2022: +0.090 | 2023: +0.054 | 2024: +0.132 | 2025: +0.126 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.227 | 2016: -0.060 | 2017: +0.180 | 2018: +0.332 | 2019: +0.150 | 2020: +0.190 | 2021: +0.193 | 2022: +0.180 | 2023: +0.035 | 2024: +0.193 | 2025: +0.290 | 2026: -0.386
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=0.56
- Early IC=+0.1647, Recent IC=+0.0930, 1st-half IC=+0.1045, 2nd-half IC=+0.0996, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.102, Q2=+0.004, Q3_mid=+0.111, Q4=+0.109, Q5_high_vol=+0.157

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0254, Sharpe=-1.5318)
- Admission: Train IC=+0.2121, Deflated=+0.2111, IR=0.70, Mono=0.72, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.221 | 2016: +0.104 | 2017: +0.151 | 2018: +0.212 | 2019: +0.072 | 2020: +0.131 | 2021: +0.057 | 2022: +0.119 | 2023: +0.089 | 2024: +0.126 | 2025: +0.096 | 2026: -0.059
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.256 | 2017: +0.254 | 2018: +0.361 | 2019: +0.112 | 2020: +0.224 | 2021: +0.191 | 2022: +0.133 | 2023: +0.133 | 2024: +0.254 | 2025: -0.150 | 2026: -0.307
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.59
- Early IC=+0.1815, Recent IC=+0.1076, 1st-half IC=+0.1326, 2nd-half IC=+0.1063, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.34)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.005, Q3_mid=+0.101, Q4=+0.133, Q5_high_vol=+0.174

**`combo_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0247, Sharpe=-1.6524)
- Admission: Train IC=+0.2006, Deflated=+0.1998, IR=0.50, Mono=0.70, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.237 | 2016: +0.111 | 2017: +0.099 | 2018: +0.263 | 2019: +0.109 | 2020: +0.101 | 2021: +0.175 | 2022: +0.098 | 2023: +0.055 | 2024: +0.139 | 2025: +0.074 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.204 | 2017: +0.140 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.064 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.90, Recency ratio=0.54
- Early IC=+0.1811, Recent IC=+0.0970, 1st-half IC=+0.1346, 2nd-half IC=+0.1214, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.140, Q2=-0.013, Q3_mid=+0.122, Q4=+0.146, Q5_high_vol=+0.204

**`combo_sig_product__net_volume_flow__first_bar_return`** (Lock IC=+0.0246, Sharpe=-0.5104)
- Admission: Train IC=+0.1810, Deflated=+0.1810, IR=0.54, Mono=0.66, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.034 | 2017: +0.155 | 2018: +0.199 | 2019: +0.137 | 2020: +0.068 | 2021: +0.044 | 2022: +0.058 | 2023: +0.067 | 2024: +0.055 | 2025: +0.109 | 2026: -0.101
- Yearly Tail ICs:   2015: +0.233 | 2016: -0.042 | 2017: +0.209 | 2018: +0.425 | 2019: +0.231 | 2020: +0.166 | 2021: +0.145 | 2022: +0.174 | 2023: +0.106 | 2024: +0.160 | 2025: +0.159 | 2026: -0.386
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.34
- Early IC=+0.1768, Recent IC=+0.0605, 1st-half IC=+0.1284, 2nd-half IC=+0.0530, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.033, Q3_mid=+0.066, Q4=+0.114, Q5_high_vol=+0.117

**`combo_sig_product__net_volume_flow__bar_ret_0`** (Lock IC=+0.0245, Sharpe=-0.5104)
- Admission: Train IC=+0.1810, Deflated=+0.1810, IR=0.54, Mono=0.66, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.034 | 2017: +0.155 | 2018: +0.199 | 2019: +0.138 | 2020: +0.068 | 2021: +0.044 | 2022: +0.058 | 2023: +0.067 | 2024: +0.054 | 2025: +0.108 | 2026: -0.100
- Yearly Tail ICs:   2015: +0.237 | 2016: -0.042 | 2017: +0.209 | 2018: +0.425 | 2019: +0.231 | 2020: +0.166 | 2021: +0.145 | 2022: +0.174 | 2023: +0.106 | 2024: +0.160 | 2025: +0.159 | 2026: -0.386
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.34
- Early IC=+0.1770, Recent IC=+0.0606, 1st-half IC=+0.1285, 2nd-half IC=+0.0529, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.033, Q3_mid=+0.066, Q4=+0.113, Q5_high_vol=+0.117

**`combo_max__close_vs_open_range__first_bar_return`** (Lock IC=+0.0235, Sharpe=-2.7519)
- Admission: Train IC=+0.2328, Deflated=+0.2321, IR=0.99, Mono=0.85, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.100 | 2017: +0.204 | 2018: +0.215 | 2019: +0.099 | 2020: +0.143 | 2021: +0.127 | 2022: +0.122 | 2023: +0.082 | 2024: +0.130 | 2025: +0.118 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.004 | 2017: +0.247 | 2018: +0.276 | 2019: +0.200 | 2020: +0.314 | 2021: +0.226 | 2022: +0.218 | 2023: +0.333 | 2024: +0.252 | 2025: -0.177 | 2026: -0.512
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.80, Recency ratio=0.51
- Early IC=+0.2091, Recent IC=+0.1060, 1st-half IC=+0.1508, 2nd-half IC=+0.1205, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.013, Q3_mid=+0.150, Q4=+0.141, Q5_high_vol=+0.155

**`combo_rank_max__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0231, Sharpe=-2.4234)
- Admission: Train IC=+0.2430, Deflated=+0.2424, IR=1.01, Mono=0.85, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.113 | 2017: +0.209 | 2018: +0.216 | 2019: +0.103 | 2020: +0.141 | 2021: +0.128 | 2022: +0.124 | 2023: +0.086 | 2024: +0.140 | 2025: +0.119 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.042 | 2017: +0.263 | 2018: +0.327 | 2019: +0.151 | 2020: +0.314 | 2021: +0.258 | 2022: +0.267 | 2023: +0.316 | 2024: +0.271 | 2025: -0.123 | 2026: -0.469
- IC CV=0.30, Neg years (linear/tail)=0/0 of 8, Half ratio=0.82, Recency ratio=0.53
- Early IC=+0.2095, Recent IC=+0.1107, 1st-half IC=+0.1511, 2nd-half IC=+0.1235, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.014, Q3_mid=+0.150, Q4=+0.145, Q5_high_vol=+0.156

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0219, Sharpe=-1.0362)
- Admission: Train IC=+0.2043, Deflated=+0.2041, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.088 | 2017: +0.208 | 2018: +0.154 | 2019: +0.100 | 2020: +0.168 | 2021: +0.053 | 2022: +0.114 | 2023: +0.130 | 2024: +0.086 | 2025: +0.086 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.366 | 2016: +0.139 | 2017: +0.347 | 2018: +0.232 | 2019: +0.179 | 2020: +0.141 | 2021: +0.176 | 2022: +0.055 | 2023: +0.102 | 2024: +0.225 | 2025: -0.029 | 2026: +0.003
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.60
- Early IC=+0.1810, Recent IC=+0.1082, 1st-half IC=+0.1483, 2nd-half IC=+0.1034, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.011, Q3_mid=+0.186, Q4=+0.105, Q5_high_vol=+0.126

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0212, Sharpe=-1.5281)
- Admission: Train IC=+0.1623, Deflated=+0.1608, IR=0.60, Mono=0.71, p=0.0014, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.184 | 2016: +0.100 | 2017: +0.219 | 2018: +0.119 | 2019: +0.031 | 2020: +0.132 | 2021: +0.050 | 2022: +0.127 | 2023: +0.105 | 2024: +0.126 | 2025: +0.092 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.296 | 2017: +0.350 | 2018: +0.235 | 2019: -0.036 | 2020: +0.189 | 2021: +0.211 | 2022: +0.092 | 2023: +0.136 | 2024: +0.213 | 2025: -0.065 | 2026: -0.180
- IC CV=0.47, Neg years (linear/tail)=0/1 of 8, Half ratio=1.03, Recency ratio=0.68
- Early IC=+0.1691, Recent IC=+0.1153, 1st-half IC=+0.1074, 2nd-half IC=+0.1104, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.014, Q3_mid=+0.119, Q4=+0.103, Q5_high_vol=+0.131

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0206, Sharpe=-0.7130)
- Admission: Train IC=+0.1744, Deflated=+0.1740, IR=0.60, Mono=0.77, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.121 | 2017: +0.116 | 2018: +0.277 | 2019: +0.078 | 2020: +0.110 | 2021: +0.083 | 2022: +0.127 | 2023: +0.036 | 2024: +0.101 | 2025: +0.073 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.148 | 2016: +0.089 | 2017: +0.306 | 2018: +0.479 | 2019: +0.081 | 2020: +0.190 | 2021: +0.206 | 2022: +0.012 | 2023: +0.064 | 2024: +0.172 | 2025: +0.148 | 2026: -0.305
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.35
- Early IC=+0.1966, Recent IC=+0.0687, 1st-half IC=+0.1384, 2nd-half IC=+0.0904, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.006, Q3_mid=+0.062, Q4=+0.118, Q5_high_vol=+0.180

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0205, Sharpe=-0.7130)
- Admission: Train IC=+0.1743, Deflated=+0.1739, IR=0.60, Mono=0.77, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.121 | 2017: +0.116 | 2018: +0.278 | 2019: +0.078 | 2020: +0.109 | 2021: +0.083 | 2022: +0.128 | 2023: +0.036 | 2024: +0.101 | 2025: +0.073 | 2026: -0.078
- Yearly Tail ICs:   2015: +0.147 | 2016: +0.085 | 2017: +0.306 | 2018: +0.479 | 2019: +0.081 | 2020: +0.187 | 2021: +0.206 | 2022: +0.012 | 2023: +0.064 | 2024: +0.172 | 2025: +0.148 | 2026: -0.305
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.35
- Early IC=+0.1968, Recent IC=+0.0685, 1st-half IC=+0.1383, 2nd-half IC=+0.0903, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.173, Q2=-0.006, Q3_mid=+0.062, Q4=+0.118, Q5_high_vol=+0.180

**`combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression`** (Lock IC=+0.0189, Sharpe=-0.2323)
- Admission: Train IC=+0.1942, Deflated=+0.1940, IR=0.49, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.079 | 2016: +0.050 | 2017: +0.112 | 2018: +0.088 | 2019: +0.023 | 2020: +0.073 | 2021: +0.043 | 2022: +0.092 | 2023: +0.113 | 2024: +0.100 | 2025: +0.120 | 2026: -0.124
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.168 | 2017: +0.180 | 2018: +0.237 | 2019: +0.021 | 2020: +0.171 | 2021: +0.209 | 2022: +0.201 | 2023: +0.183 | 2024: +0.247 | 2025: +0.095 | 2026: -0.049
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.30, Recency ratio=1.07
- Early IC=+0.1003, Recent IC=+0.1069, 1st-half IC=+0.0703, 2nd-half IC=+0.0917, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.012, Q3_mid=+0.106, Q4=+0.064, Q5_high_vol=+0.069

**`combo_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0186, Sharpe=-2.2632)
- Admission: Train IC=+0.2272, Deflated=+0.2269, IR=0.83, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.102 | 2017: +0.149 | 2018: +0.218 | 2019: +0.080 | 2020: +0.123 | 2021: +0.094 | 2022: +0.109 | 2023: +0.068 | 2024: +0.113 | 2025: +0.126 | 2026: -0.119
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.103 | 2017: +0.184 | 2018: +0.248 | 2019: +0.129 | 2020: +0.330 | 2021: +0.197 | 2022: +0.219 | 2023: +0.400 | 2024: +0.174 | 2025: -0.143 | 2026: -0.582
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.49
- Early IC=+0.1833, Recent IC=+0.0905, 1st-half IC=+0.1352, 2nd-half IC=+0.0995, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.015, Q3_mid=+0.122, Q4=+0.143, Q5_high_vol=+0.137

**`combo_max__trend_bar_close_consistency__first_bar_sentiment`** (Lock IC=+0.0165, Sharpe=-0.7540)
- Admission: Train IC=+0.1575, Deflated=+0.1577, IR=0.40, Mono=0.68, p=0.0022, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.065 | 2017: +0.138 | 2018: +0.181 | 2019: +0.033 | 2020: +0.096 | 2021: +0.138 | 2022: +0.127 | 2023: +0.066 | 2024: +0.103 | 2025: +0.091 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.377 | 2016: +0.208 | 2017: +0.167 | 2018: +0.093 | 2019: -0.051 | 2020: +0.197 | 2021: +0.210 | 2022: +0.245 | 2023: +0.073 | 2024: +0.354 | 2025: +0.142 | 2026: -0.478
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=1.07, Recency ratio=0.53
- Early IC=+0.1599, Recent IC=+0.0843, 1st-half IC=+0.1018, 2nd-half IC=+0.1088, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.026, Q3_mid=+0.114, Q4=+0.148, Q5_high_vol=+0.119

**`combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction`** (Lock IC=+0.0163, Sharpe=-1.2828)
- Admission: Train IC=+0.1321, Deflated=+0.1313, IR=0.44, Mono=0.66, p=0.0092, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.162 | 2016: -0.005 | 2017: +0.043 | 2018: +0.067 | 2019: +0.081 | 2020: +0.084 | 2021: +0.139 | 2022: -0.032 | 2023: +0.009 | 2024: +0.023 | 2025: -0.045 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.141 | 2016: +0.136 | 2017: +0.221 | 2018: +0.185 | 2019: +0.153 | 2020: +0.230 | 2021: +0.018 | 2022: -0.067 | 2023: +0.143 | 2024: +0.133 | 2025: -0.245 | 2026: +0.225
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=0.53, Recency ratio=0.28
- Early IC=+0.0551, Recent IC=+0.0157, 1st-half IC=+0.0693, 2nd-half IC=+0.0368, Neg regimes=1/5
- Weak component: `trend_day_regime_conviction` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.050, Q2=-0.041, Q3_mid=+0.048, Q4=+0.064, Q5_high_vol=+0.108

**`combo_rank_max__early_body_momentum__bar_ret_0`** (Lock IC=+0.0126, Sharpe=-2.1701)
- Admission: Train IC=+0.2447, Deflated=+0.2444, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.125 | 2017: +0.154 | 2018: +0.226 | 2019: +0.083 | 2020: +0.134 | 2021: +0.102 | 2022: +0.108 | 2023: +0.080 | 2024: +0.126 | 2025: +0.122 | 2026: -0.123
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.099 | 2017: +0.215 | 2018: +0.264 | 2019: +0.075 | 2020: +0.348 | 2021: +0.179 | 2022: +0.303 | 2023: +0.395 | 2024: +0.216 | 2025: -0.102 | 2026: -0.544
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.54
- Early IC=+0.1898, Recent IC=+0.1018, 1st-half IC=+0.1402, 2nd-half IC=+0.1035, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.016, Q3_mid=+0.129, Q4=+0.151, Q5_high_vol=+0.147

### 159915ETF — `single` Median Features

**`combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early`** (Lock IC=+0.1338, Sharpe=-0.1673)
- Admission: Train IC=+0.2239, Deflated=+0.2237, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.223 | 2016: +0.078 | 2017: -0.014 | 2018: +0.124 | 2019: +0.207 | 2020: +0.130 | 2021: +0.147 | 2022: +0.126 | 2023: +0.147 | 2024: +0.063 | 2025: +0.180 | 2026: +0.056
- Yearly Tail ICs:   2015: +0.268 | 2016: -0.018 | 2017: +0.093 | 2018: +0.144 | 2019: +0.442 | 2020: +0.168 | 2021: +0.253 | 2022: +0.268 | 2023: +0.334 | 2024: +0.200 | 2025: +0.199 | 2026: -0.361
- IC CV=0.53, Neg years (linear/tail)=1/0 of 8, Half ratio=1.22, Recency ratio=1.90
- Early IC=+0.0554, Recent IC=+0.1052, 1st-half IC=+0.1070, 2nd-half IC=+0.1310, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.108, Q3_mid=+0.101, Q4=+0.095, Q5_high_vol=+0.178

**`combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1266, Sharpe=-0.2347)
- Admission: Train IC=+0.2061, Deflated=+0.2053, IR=0.58, Mono=0.66, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.177 | 2017: -0.011 | 2018: +0.135 | 2019: +0.152 | 2020: +0.148 | 2021: +0.141 | 2022: +0.139 | 2023: +0.105 | 2024: +0.057 | 2025: +0.135 | 2026: +0.142
- Yearly Tail ICs:   2015: +0.062 | 2016: +0.161 | 2017: +0.132 | 2018: +0.332 | 2019: +0.256 | 2020: +0.100 | 2021: +0.375 | 2022: +0.118 | 2023: +0.094 | 2024: +0.151 | 2025: -0.039 | 2026: +0.185
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=1.32
- Early IC=+0.0619, Recent IC=+0.0814, 1st-half IC=+0.1033, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.101, Q3_mid=+0.063, Q4=+0.121, Q5_high_vol=+0.163

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1193, Sharpe=-0.2201)
- Admission: Train IC=+0.2001, Deflated=+0.1990, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.161 | 2017: +0.030 | 2018: +0.132 | 2019: +0.123 | 2020: +0.132 | 2021: +0.160 | 2022: +0.154 | 2023: +0.136 | 2024: +0.080 | 2025: +0.147 | 2026: +0.107
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.148 | 2017: +0.200 | 2018: +0.323 | 2019: +0.164 | 2020: +0.081 | 2021: +0.457 | 2022: +0.123 | 2023: +0.282 | 2024: +0.169 | 2025: +0.125 | 2026: +0.096
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.28, Recency ratio=1.32
- Early IC=+0.0818, Recent IC=+0.1079, 1st-half IC=+0.1090, 2nd-half IC=+0.1393, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.130, Q3_mid=+0.090, Q4=+0.118, Q5_high_vol=+0.167

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1161, Sharpe=-0.1261)
- Admission: Train IC=+0.1924, Deflated=+0.1914, IR=0.64, Mono=0.71, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.168 | 2017: +0.029 | 2018: +0.133 | 2019: +0.128 | 2020: +0.137 | 2021: +0.158 | 2022: +0.146 | 2023: +0.134 | 2024: +0.077 | 2025: +0.135 | 2026: +0.114
- Yearly Tail ICs:   2015: +0.012 | 2016: +0.174 | 2017: +0.193 | 2018: +0.300 | 2019: +0.155 | 2020: +0.091 | 2021: +0.455 | 2022: +0.116 | 2023: +0.293 | 2024: +0.147 | 2025: +0.105 | 2026: +0.109
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.29
- Early IC=+0.0815, Recent IC=+0.1054, 1st-half IC=+0.1104, 2nd-half IC=+0.1360, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.122, Q3_mid=+0.079, Q4=+0.118, Q5_high_vol=+0.169

**`combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1155, Sharpe=-0.1261)
- Admission: Train IC=+0.1950, Deflated=+0.1944, IR=0.54, Mono=0.68, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.186 | 2017: -0.005 | 2018: +0.142 | 2019: +0.136 | 2020: +0.150 | 2021: +0.152 | 2022: +0.145 | 2023: +0.120 | 2024: +0.060 | 2025: +0.133 | 2026: +0.114
- Yearly Tail ICs:   2015: -0.003 | 2016: +0.176 | 2017: +0.151 | 2018: +0.304 | 2019: +0.171 | 2020: +0.080 | 2021: +0.459 | 2022: +0.111 | 2023: +0.231 | 2024: +0.137 | 2025: +0.101 | 2026: +0.102
- IC CV=0.47, Neg years (linear/tail)=1/0 of 8, Half ratio=1.22, Recency ratio=1.32
- Early IC=+0.0683, Recent IC=+0.0900, 1st-half IC=+0.1039, 2nd-half IC=+0.1267, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.102, Q3_mid=+0.060, Q4=+0.120, Q5_high_vol=+0.177

**`combo_rel_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1106, Sharpe=-0.0225)
- Admission: Train IC=+0.2480, Deflated=+0.2465, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.058 | 2017: +0.017 | 2018: +0.079 | 2019: +0.182 | 2020: +0.098 | 2021: +0.155 | 2022: +0.144 | 2023: +0.152 | 2024: +0.075 | 2025: +0.182 | 2026: -0.004
- Yearly Tail ICs:   2015: -0.021 | 2016: +0.267 | 2017: -0.021 | 2018: +0.116 | 2019: +0.383 | 2020: +0.205 | 2021: +0.341 | 2022: +0.349 | 2023: +0.332 | 2024: +0.263 | 2025: +0.229 | 2026: -0.221
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.53, Recency ratio=2.35
- Early IC=+0.0482, Recent IC=+0.1135, 1st-half IC=+0.0936, 2nd-half IC=+0.1430, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.118, Q3_mid=+0.110, Q4=+0.107, Q5_high_vol=+0.159

**`combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1079, Sharpe=-0.2788)
- Admission: Train IC=+0.2028, Deflated=+0.2020, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.55
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.023 | 2017: -0.058 | 2018: +0.036 | 2019: +0.135 | 2020: +0.037 | 2021: +0.133 | 2022: +0.143 | 2023: +0.143 | 2024: +0.054 | 2025: +0.066 | 2026: +0.166
- Yearly Tail ICs:   2015: +0.075 | 2016: -0.087 | 2017: -0.081 | 2018: +0.099 | 2019: +0.341 | 2020: +0.141 | 2021: +0.172 | 2022: +0.208 | 2023: +0.292 | 2024: +0.125 | 2025: -0.089 | 2026: +0.357
- IC CV=0.88, Neg years (linear/tail)=1/1 of 8, Half ratio=2.54, Recency ratio=-8.81
- Early IC=-0.0112, Recent IC=+0.0983, 1st-half IC=+0.0471, 2nd-half IC=+0.1194, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.046, Q3_mid=+0.091, Q4=+0.116, Q5_high_vol=+0.131

**`combo_mean__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.1065, Sharpe=-0.2278)
- Admission: Train IC=+0.2353, Deflated=+0.2355, IR=0.72, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.094 | 2017: +0.000 | 2018: +0.078 | 2019: +0.167 | 2020: +0.104 | 2021: +0.150 | 2022: +0.084 | 2023: +0.171 | 2024: +0.070 | 2025: +0.198 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.309 | 2016: -0.018 | 2017: +0.026 | 2018: +0.263 | 2019: +0.418 | 2020: +0.166 | 2021: +0.183 | 2022: +0.247 | 2023: +0.432 | 2024: +0.202 | 2025: +0.339 | 2026: -0.454
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.68, Recency ratio=3.09
- Early IC=+0.0391, Recent IC=+0.1207, 1st-half IC=+0.0742, 2nd-half IC=+0.1247, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.083, Q3_mid=+0.109, Q4=+0.060, Q5_high_vol=+0.117

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1031, Sharpe=-0.6008)
- Admission: Train IC=+0.1923, Deflated=+0.1916, IR=0.64, Mono=0.75, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.149 | 2016: +0.057 | 2017: -0.014 | 2018: +0.019 | 2019: +0.160 | 2020: +0.102 | 2021: +0.098 | 2022: +0.081 | 2023: +0.141 | 2024: +0.126 | 2025: +0.190 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.210 | 2016: +0.114 | 2017: +0.081 | 2018: -0.016 | 2019: +0.319 | 2020: +0.179 | 2021: +0.151 | 2022: +0.361 | 2023: +0.373 | 2024: +0.169 | 2025: +0.270 | 2026: -0.291
- IC CV=0.63, Neg years (linear/tail)=1/1 of 8, Half ratio=2.21, Recency ratio=53.82
- Early IC=+0.0025, Recent IC=+0.1335, 1st-half IC=+0.0555, 2nd-half IC=+0.1225, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.094, Q3_mid=+0.108, Q4=+0.057, Q5_high_vol=+0.114

**`net_volume_flow`** (Lock IC=+0.0979, Sharpe=-0.7750)
- Admission: Train IC=+0.1871, Deflated=+0.1873, IR=0.65, Mono=0.73, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.053 | 2017: -0.019 | 2018: +0.036 | 2019: +0.116 | 2020: +0.049 | 2021: +0.139 | 2022: +0.063 | 2023: +0.165 | 2024: +0.072 | 2025: +0.205 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.110 | 2017: +0.061 | 2018: +0.026 | 2019: +0.301 | 2020: +0.192 | 2021: -0.005 | 2022: +0.332 | 2023: +0.452 | 2024: +0.160 | 2025: +0.185 | 2026: -0.324
- IC CV=0.72, Neg years (linear/tail)=1/1 of 8, Half ratio=2.98, Recency ratio=14.17
- Early IC=+0.0084, Recent IC=+0.1184, 1st-half IC=+0.0398, 2nd-half IC=+0.1186, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.093, Q3_mid=+0.106, Q4=+0.029, Q5_high_vol=+0.069

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0939, Sharpe=-0.4022)
- Admission: Train IC=+0.2165, Deflated=+0.2165, IR=0.57, Mono=0.72, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.100 | 2017: +0.028 | 2018: +0.120 | 2019: +0.193 | 2020: +0.109 | 2021: +0.137 | 2022: +0.077 | 2023: +0.192 | 2024: +0.058 | 2025: +0.147 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.055 | 2017: +0.048 | 2018: +0.293 | 2019: +0.344 | 2020: +0.167 | 2021: +0.174 | 2022: +0.124 | 2023: +0.496 | 2024: +0.175 | 2025: +0.282 | 2026: +0.072
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.69
- Early IC=+0.0741, Recent IC=+0.1249, 1st-half IC=+0.1057, 2nd-half IC=+0.1200, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.108, Q3_mid=+0.082, Q4=+0.083, Q5_high_vol=+0.145

**`combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0936, Sharpe=-0.3130)
- Admission: Train IC=+0.1482, Deflated=+0.1479, IR=0.41, Mono=0.66, p=0.0044, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.132 | 2017: -0.072 | 2018: +0.106 | 2019: +0.089 | 2020: +0.096 | 2021: +0.001 | 2022: +0.158 | 2023: +0.163 | 2024: +0.076 | 2025: +0.083 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.122 | 2016: +0.268 | 2017: -0.217 | 2018: +0.216 | 2019: +0.064 | 2020: +0.198 | 2021: +0.085 | 2022: +0.420 | 2023: +0.080 | 2024: +0.118 | 2025: -0.047 | 2026: +0.040
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=1.25, Recency ratio=6.95
- Early IC=+0.0172, Recent IC=+0.1194, 1st-half IC=+0.0735, 2nd-half IC=+0.0922, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.29)
- Regime ICs: Q1_low_vol=+0.028, Q2=+0.118, Q3_mid=+0.067, Q4=+0.085, Q5_high_vol=+0.119

**`combo_rank_max__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.0919, Sharpe=-0.8343)
- Admission: Train IC=+0.2039, Deflated=+0.2024, IR=0.75, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.040 | 2017: +0.033 | 2018: +0.085 | 2019: +0.130 | 2020: +0.074 | 2021: +0.174 | 2022: +0.173 | 2023: +0.138 | 2024: +0.083 | 2025: +0.135 | 2026: +0.066
- Yearly Tail ICs:   2015: -0.079 | 2016: +0.151 | 2017: +0.228 | 2018: +0.286 | 2019: +0.176 | 2020: +0.034 | 2021: +0.404 | 2022: +0.201 | 2023: +0.136 | 2024: +0.197 | 2025: +0.015 | 2026: -0.068
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.85, Recency ratio=1.86
- Early IC=+0.0596, Recent IC=+0.1108, 1st-half IC=+0.0801, 2nd-half IC=+0.1485, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.124, Q3_mid=+0.076, Q4=+0.117, Q5_high_vol=+0.146

**`combo_max__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.0916, Sharpe=-0.4785)
- Admission: Train IC=+0.2424, Deflated=+0.2422, IR=0.71, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.123 | 2017: +0.000 | 2018: +0.072 | 2019: +0.155 | 2020: +0.134 | 2021: +0.171 | 2022: +0.093 | 2023: +0.150 | 2024: +0.058 | 2025: +0.206 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.295 | 2016: -0.034 | 2017: +0.068 | 2018: +0.060 | 2019: +0.438 | 2020: +0.269 | 2021: +0.294 | 2022: +0.235 | 2023: +0.384 | 2024: +0.187 | 2025: +0.310 | 2026: -0.403
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.57, Recency ratio=2.87
- Early IC=+0.0362, Recent IC=+0.1041, 1st-half IC=+0.0794, 2nd-half IC=+0.1249, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.082, Q3_mid=+0.135, Q4=+0.074, Q5_high_vol=+0.117

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0902, Sharpe=-0.2369)
- Admission: Train IC=+0.1738, Deflated=+0.1730, IR=0.50, Mono=0.66, p=0.0012, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.113 | 2017: +0.034 | 2018: +0.112 | 2019: +0.135 | 2020: +0.124 | 2021: +0.177 | 2022: +0.125 | 2023: +0.162 | 2024: +0.095 | 2025: +0.114 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.146 | 2017: +0.115 | 2018: +0.319 | 2019: +0.216 | 2020: +0.022 | 2021: +0.452 | 2022: +0.062 | 2023: +0.263 | 2024: +0.131 | 2025: +0.094 | 2026: +0.017
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.45, Recency ratio=1.75
- Early IC=+0.0732, Recent IC=+0.1284, 1st-half IC=+0.0994, 2nd-half IC=+0.1443, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.079, Q3_mid=+0.098, Q4=+0.115, Q5_high_vol=+0.183

**`combo_max__bar_ret_0__volatility_expansion_trend_vector`** (Lock IC=+0.0894, Sharpe=-0.0643)
- Admission: Train IC=+0.1936, Deflated=+0.1931, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.082 | 2017: +0.048 | 2018: +0.080 | 2019: +0.128 | 2020: +0.122 | 2021: +0.182 | 2022: +0.084 | 2023: +0.159 | 2024: +0.070 | 2025: +0.205 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.147 | 2016: -0.188 | 2017: +0.139 | 2018: +0.220 | 2019: +0.259 | 2020: +0.048 | 2021: +0.310 | 2022: +0.198 | 2023: +0.386 | 2024: +0.140 | 2025: +0.366 | 2026: -0.590
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.56, Recency ratio=1.78
- Early IC=+0.0640, Recent IC=+0.1141, 1st-half IC=+0.0835, 2nd-half IC=+0.1298, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.083, Q3_mid=+0.143, Q4=+0.081, Q5_high_vol=+0.110

**`combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0889, Sharpe=-0.2773)
- Admission: Train IC=+0.2261, Deflated=+0.2257, IR=0.71, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.033 | 2017: +0.028 | 2018: +0.050 | 2019: +0.152 | 2020: +0.069 | 2021: +0.147 | 2022: +0.092 | 2023: +0.192 | 2024: +0.098 | 2025: +0.198 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.265 | 2016: +0.132 | 2017: +0.063 | 2018: -0.076 | 2019: +0.400 | 2020: +0.214 | 2021: +0.104 | 2022: +0.381 | 2023: +0.527 | 2024: +0.224 | 2025: +0.218 | 2026: -0.253
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=2.06, Recency ratio=3.72
- Early IC=+0.0389, Recent IC=+0.1449, 1st-half IC=+0.0664, 2nd-half IC=+0.1365, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.084, Q3_mid=+0.139, Q4=+0.063, Q5_high_vol=+0.105

**`combo_rank_min__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0888, Sharpe=-0.2203)
- Admission: Train IC=+0.2380, Deflated=+0.2374, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.032 | 2017: +0.012 | 2018: +0.025 | 2019: +0.120 | 2020: +0.058 | 2021: +0.170 | 2022: +0.103 | 2023: +0.160 | 2024: +0.095 | 2025: +0.200 | 2026: -0.085
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.270 | 2017: +0.037 | 2018: +0.094 | 2019: +0.349 | 2020: +0.159 | 2021: +0.303 | 2022: +0.319 | 2023: +0.379 | 2024: +0.243 | 2025: +0.164 | 2026: -0.259
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=3.58, Recency ratio=7.87
- Early IC=+0.0162, Recent IC=+0.1273, 1st-half IC=+0.0393, 2nd-half IC=+0.1406, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.081, Q3_mid=+0.125, Q4=+0.048, Q5_high_vol=+0.091

**`combo_sig_product__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.0887, Sharpe=-0.3901)
- Admission: Train IC=+0.2068, Deflated=+0.2059, IR=0.47, Mono=0.68, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.087 | 2017: +0.027 | 2018: +0.045 | 2019: +0.181 | 2020: +0.158 | 2021: +0.065 | 2022: +0.072 | 2023: +0.073 | 2024: +0.091 | 2025: +0.123 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.080 | 2016: +0.050 | 2017: +0.103 | 2018: +0.143 | 2019: +0.318 | 2020: +0.192 | 2021: -0.130 | 2022: +0.095 | 2023: +0.238 | 2024: +0.180 | 2025: +0.135 | 2026: +0.046
- IC CV=0.56, Neg years (linear/tail)=0/1 of 8, Half ratio=0.95, Recency ratio=2.28
- Early IC=+0.0360, Recent IC=+0.0819, 1st-half IC=+0.0909, 2nd-half IC=+0.0865, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.115, Q2=+0.075, Q3_mid=+0.088, Q4=+0.041, Q5_high_vol=+0.126

**`combo_rank_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0882, Sharpe=-1.0149)
- Admission: Train IC=+0.2457, Deflated=+0.2456, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.149 | 2017: +0.001 | 2018: +0.089 | 2019: +0.181 | 2020: +0.129 | 2021: +0.163 | 2022: +0.108 | 2023: +0.152 | 2024: +0.062 | 2025: +0.186 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.137 | 2016: -0.024 | 2017: +0.040 | 2018: +0.261 | 2019: +0.408 | 2020: +0.180 | 2021: +0.310 | 2022: +0.269 | 2023: +0.345 | 2024: +0.233 | 2025: +0.245 | 2026: -0.185
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.47, Recency ratio=2.43
- Early IC=+0.0440, Recent IC=+0.1067, 1st-half IC=+0.0878, 2nd-half IC=+0.1293, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.090, Q3_mid=+0.099, Q4=+0.098, Q5_high_vol=+0.129

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0874, Sharpe=-0.2319)
- Admission: Train IC=+0.2081, Deflated=+0.2077, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.131 | 2017: -0.012 | 2018: +0.123 | 2019: +0.139 | 2020: +0.110 | 2021: +0.166 | 2022: +0.159 | 2023: +0.107 | 2024: +0.067 | 2025: +0.143 | 2026: +0.023
- Yearly Tail ICs:   2015: -0.013 | 2016: +0.184 | 2017: +0.132 | 2018: +0.314 | 2019: +0.121 | 2020: +0.102 | 2021: +0.468 | 2022: +0.146 | 2023: +0.218 | 2024: +0.270 | 2025: +0.064 | 2026: -0.181
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.53, Recency ratio=1.55
- Early IC=+0.0559, Recent IC=+0.0868, 1st-half IC=+0.0879, 2nd-half IC=+0.1341, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.123, Q2=+0.092, Q3_mid=+0.077, Q4=+0.121, Q5_high_vol=+0.153

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0874, Sharpe=-0.5508)
- Admission: Train IC=+0.2622, Deflated=+0.2622, IR=0.82, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.116 | 2017: +0.014 | 2018: +0.119 | 2019: +0.200 | 2020: +0.117 | 2021: +0.158 | 2022: +0.100 | 2023: +0.188 | 2024: +0.077 | 2025: +0.178 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.178 | 2016: +0.145 | 2017: +0.002 | 2018: +0.285 | 2019: +0.386 | 2020: +0.229 | 2021: +0.257 | 2022: +0.228 | 2023: +0.555 | 2024: +0.269 | 2025: +0.093 | 2026: -0.230
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.33, Recency ratio=1.99
- Early IC=+0.0667, Recent IC=+0.1325, 1st-half IC=+0.1024, 2nd-half IC=+0.1362, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.099, Q3_mid=+0.118, Q4=+0.101, Q5_high_vol=+0.144

**`combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0873, Sharpe=-0.3451)
- Admission: Train IC=+0.2171, Deflated=+0.2173, IR=0.51, Mono=0.70, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.138 | 2017: +0.010 | 2018: +0.139 | 2019: +0.204 | 2020: +0.117 | 2021: +0.143 | 2022: +0.059 | 2023: +0.176 | 2024: +0.060 | 2025: +0.131 | 2026: +0.026
- Yearly Tail ICs:   2015: +0.344 | 2016: +0.016 | 2017: +0.045 | 2018: +0.264 | 2019: +0.351 | 2020: +0.197 | 2021: +0.115 | 2022: +0.102 | 2023: +0.517 | 2024: +0.026 | 2025: +0.255 | 2026: -0.053
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=1.04, Recency ratio=1.59
- Early IC=+0.0745, Recent IC=+0.1184, 1st-half IC=+0.1120, 2nd-half IC=+0.1162, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.100, Q3_mid=+0.069, Q4=+0.095, Q5_high_vol=+0.148

**`combo_max__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0864, Sharpe=-0.0202)
- Admission: Train IC=+0.2387, Deflated=+0.2388, IR=0.63, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.133 | 2017: +0.004 | 2018: +0.112 | 2019: +0.211 | 2020: +0.115 | 2021: +0.146 | 2022: +0.058 | 2023: +0.175 | 2024: +0.078 | 2025: +0.162 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.404 | 2016: +0.065 | 2017: +0.104 | 2018: +0.208 | 2019: +0.407 | 2020: +0.215 | 2021: +0.196 | 2022: +0.136 | 2023: +0.340 | 2024: +0.313 | 2025: +0.257 | 2026: -0.091
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=2.19
- Early IC=+0.0577, Recent IC=+0.1265, 1st-half IC=+0.0977, 2nd-half IC=+0.1201, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.065, Q3_mid=+0.116, Q4=+0.081, Q5_high_vol=+0.149

**`combo_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0827, Sharpe=-0.0240)
- Admission: Train IC=+0.2148, Deflated=+0.2156, IR=0.67, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.123 | 2017: +0.008 | 2018: +0.138 | 2019: +0.194 | 2020: +0.134 | 2021: +0.127 | 2022: +0.093 | 2023: +0.152 | 2024: +0.055 | 2025: +0.133 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.449 | 2016: -0.281 | 2017: +0.116 | 2018: +0.295 | 2019: +0.369 | 2020: +0.153 | 2021: +0.219 | 2022: +0.166 | 2023: +0.293 | 2024: +0.124 | 2025: +0.285 | 2026: +0.049
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.42
- Early IC=+0.0729, Recent IC=+0.1034, 1st-half IC=+0.1118, 2nd-half IC=+0.1122, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.093, Q3_mid=+0.090, Q4=+0.112, Q5_high_vol=+0.141

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0824, Sharpe=-0.6121)
- Admission: Train IC=+0.2351, Deflated=+0.2346, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.062 | 2017: +0.043 | 2018: +0.055 | 2019: +0.164 | 2020: +0.100 | 2021: +0.182 | 2022: +0.114 | 2023: +0.190 | 2024: +0.078 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.063 | 2017: +0.039 | 2018: +0.143 | 2019: +0.289 | 2020: +0.186 | 2021: +0.349 | 2022: +0.232 | 2023: +0.457 | 2024: +0.231 | 2025: +0.146 | 2026: -0.277
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.75, Recency ratio=2.75
- Early IC=+0.0487, Recent IC=+0.1341, 1st-half IC=+0.0845, 2nd-half IC=+0.1480, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.098, Q3_mid=+0.118, Q4=+0.089, Q5_high_vol=+0.146

**`combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0824, Sharpe=-0.3109)
- Admission: Train IC=+0.1800, Deflated=+0.1803, IR=0.49, Mono=0.66, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.107 | 2017: +0.011 | 2018: +0.110 | 2019: +0.202 | 2020: +0.113 | 2021: +0.143 | 2022: +0.059 | 2023: +0.162 | 2024: +0.073 | 2025: +0.152 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.158 | 2016: -0.024 | 2017: +0.141 | 2018: +0.308 | 2019: +0.207 | 2020: +0.026 | 2021: +0.316 | 2022: +0.045 | 2023: +0.384 | 2024: +0.124 | 2025: +0.346 | 2026: -0.217
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.14, Recency ratio=1.95
- Early IC=+0.0604, Recent IC=+0.1176, 1st-half IC=+0.1015, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.070, Q3_mid=+0.100, Q4=+0.077, Q5_high_vol=+0.162

**`combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0821, Sharpe=-0.4941)
- Admission: Train IC=+0.2171, Deflated=+0.2167, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.048 | 2017: +0.034 | 2018: +0.048 | 2019: +0.165 | 2020: +0.087 | 2021: +0.143 | 2022: +0.100 | 2023: +0.179 | 2024: +0.106 | 2025: +0.197 | 2026: -0.088
- Yearly Tail ICs:   2015: +0.249 | 2016: -0.053 | 2017: +0.064 | 2018: +0.031 | 2019: +0.396 | 2020: +0.246 | 2021: +0.109 | 2022: +0.308 | 2023: +0.347 | 2024: +0.267 | 2025: +0.295 | 2026: -0.202
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.81, Recency ratio=3.59
- Early IC=+0.0401, Recent IC=+0.1440, 1st-half IC=+0.0774, 2nd-half IC=+0.1402, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.084, Q3_mid=+0.148, Q4=+0.068, Q5_high_vol=+0.115

**`combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0813, Sharpe=-0.1094)
- Admission: Train IC=+0.1940, Deflated=+0.1952, IR=0.63, Mono=0.71, p=0.0002, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.072 | 2016: +0.062 | 2017: +0.019 | 2018: +0.026 | 2019: +0.149 | 2020: +0.033 | 2021: +0.161 | 2022: +0.084 | 2023: +0.113 | 2024: +0.094 | 2025: +0.167 | 2026: -0.045
- Yearly Tail ICs:   2015: -0.014 | 2016: +0.181 | 2017: +0.163 | 2018: -0.053 | 2019: +0.316 | 2020: +0.279 | 2021: +0.075 | 2022: +0.359 | 2023: +0.242 | 2024: +0.151 | 2025: +0.204 | 2026: -0.275
- IC CV=0.61, Neg years (linear/tail)=0/1 of 8, Half ratio=2.36, Recency ratio=4.52
- Early IC=+0.0229, Recent IC=+0.1036, 1st-half IC=+0.0518, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.070, Q2=+0.095, Q3_mid=+0.123, Q4=+0.136, Q5_high_vol=+0.030

**`combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0811, Sharpe=-0.6874)
- Admission: Train IC=+0.2034, Deflated=+0.2027, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.087 | 2017: +0.027 | 2018: +0.118 | 2019: +0.128 | 2020: +0.090 | 2021: +0.173 | 2022: +0.157 | 2023: +0.131 | 2024: +0.081 | 2025: +0.139 | 2026: +0.016
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.151 | 2017: +0.167 | 2018: +0.301 | 2019: +0.161 | 2020: +0.121 | 2021: +0.462 | 2022: +0.224 | 2023: +0.219 | 2024: +0.193 | 2025: +0.109 | 2026: -0.204
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.58, Recency ratio=1.46
- Early IC=+0.0724, Recent IC=+0.1058, 1st-half IC=+0.0903, 2nd-half IC=+0.1425, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.107, Q3_mid=+0.085, Q4=+0.122, Q5_high_vol=+0.144

**`trend_bar_close_consistency`** (Lock IC=+0.0806, Sharpe=-0.4274)
- Admission: Train IC=+0.1553, Deflated=+0.1549, IR=0.45, Mono=0.68, p=0.0028, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.055 | 2016: +0.017 | 2017: -0.031 | 2018: +0.000 | 2019: +0.074 | 2020: +0.026 | 2021: +0.109 | 2022: +0.058 | 2023: +0.144 | 2024: +0.066 | 2025: +0.222 | 2026: -0.136
- Yearly Tail ICs:   2015: +0.047 | 2016: +0.226 | 2017: -0.086 | 2018: +0.030 | 2019: +0.233 | 2020: +0.182 | 2021: +0.058 | 2022: +0.382 | 2023: +0.352 | 2024: +0.099 | 2025: +0.249 | 2026: -0.074
- IC CV=0.95, Neg years (linear/tail)=1/1 of 8, Half ratio=5.80, Recency ratio=-6.86
- Early IC=-0.0153, Recent IC=+0.1046, 1st-half IC=+0.0168, 2nd-half IC=+0.0973, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.087, Q3_mid=+0.112, Q4=+0.025, Q5_high_vol=+0.014

**`combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0802, Sharpe=-0.9988)
- Admission: Train IC=+0.2511, Deflated=+0.2513, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.161 | 2017: +0.001 | 2018: +0.129 | 2019: +0.197 | 2020: +0.139 | 2021: +0.144 | 2022: +0.090 | 2023: +0.172 | 2024: +0.050 | 2025: +0.148 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.164 | 2017: -0.001 | 2018: +0.271 | 2019: +0.369 | 2020: +0.256 | 2021: +0.256 | 2022: +0.228 | 2023: +0.533 | 2024: +0.224 | 2025: +0.068 | 2026: -0.090
- IC CV=0.53, Neg years (linear/tail)=0/1 of 8, Half ratio=1.12, Recency ratio=1.71
- Early IC=+0.0649, Recent IC=+0.1110, 1st-half IC=+0.1085, 2nd-half IC=+0.1211, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.100, Q3_mid=+0.092, Q4=+0.097, Q5_high_vol=+0.147

**`combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector`** (Lock IC=+0.0796, Sharpe=-0.0979)
- Admission: Train IC=+0.1772, Deflated=+0.1763, IR=0.63, Mono=0.73, p=0.0010, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.010 | 2017: +0.025 | 2018: +0.020 | 2019: +0.081 | 2020: +0.055 | 2021: +0.142 | 2022: +0.121 | 2023: +0.171 | 2024: +0.082 | 2025: +0.192 | 2026: -0.102
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.081 | 2017: +0.039 | 2018: -0.005 | 2019: +0.259 | 2020: +0.157 | 2021: +0.180 | 2022: +0.331 | 2023: +0.348 | 2024: +0.162 | 2025: +0.276 | 2026: -0.286
- IC CV=0.58, Neg years (linear/tail)=0/1 of 8, Half ratio=3.92, Recency ratio=5.61
- Early IC=+0.0225, Recent IC=+0.1265, 1st-half IC=+0.0341, 2nd-half IC=+0.1339, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.149, Q2=+0.057, Q3_mid=+0.127, Q4=+0.044, Q5_high_vol=+0.078

**`combo_max__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0772, Sharpe=-0.7924)
- Admission: Train IC=+0.2272, Deflated=+0.2274, IR=0.74, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.157 | 2017: -0.012 | 2018: +0.104 | 2019: +0.183 | 2020: +0.137 | 2021: +0.170 | 2022: +0.109 | 2023: +0.142 | 2024: +0.061 | 2025: +0.177 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.176 | 2017: +0.021 | 2018: +0.204 | 2019: +0.275 | 2020: +0.175 | 2021: +0.373 | 2022: +0.244 | 2023: +0.368 | 2024: +0.184 | 2025: +0.138 | 2026: -0.316
- IC CV=0.53, Neg years (linear/tail)=1/0 of 8, Half ratio=1.41, Recency ratio=2.21
- Early IC=+0.0459, Recent IC=+0.1014, 1st-half IC=+0.0926, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.092, Q3_mid=+0.114, Q4=+0.097, Q5_high_vol=+0.134

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0772, Sharpe=-0.5386)
- Admission: Train IC=+0.2313, Deflated=+0.2317, IR=0.63, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.084 | 2017: +0.064 | 2018: +0.067 | 2019: +0.173 | 2020: +0.066 | 2021: +0.220 | 2022: +0.089 | 2023: +0.165 | 2024: +0.079 | 2025: +0.179 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.017 | 2017: +0.238 | 2018: +0.208 | 2019: +0.343 | 2020: -0.017 | 2021: +0.310 | 2022: +0.236 | 2023: +0.279 | 2024: +0.249 | 2025: +0.235 | 2026: -0.216
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=1.77, Recency ratio=1.84
- Early IC=+0.0661, Recent IC=+0.1215, 1st-half IC=+0.0833, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.100, Q3_mid=+0.135, Q4=+0.115, Q5_high_vol=+0.121

**`combo_rank_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0767, Sharpe=-0.2421)
- Admission: Train IC=+0.2435, Deflated=+0.2428, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.172 | 2016: +0.070 | 2017: +0.032 | 2018: +0.107 | 2019: +0.174 | 2020: +0.115 | 2021: +0.130 | 2022: +0.086 | 2023: +0.187 | 2024: +0.098 | 2025: +0.172 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.369 | 2016: +0.147 | 2017: +0.095 | 2018: +0.234 | 2019: +0.386 | 2020: +0.228 | 2021: +0.313 | 2022: +0.245 | 2023: +0.453 | 2024: +0.213 | 2025: +0.148 | 2026: -0.102
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.40, Recency ratio=2.06
- Early IC=+0.0690, Recent IC=+0.1424, 1st-half IC=+0.0941, 2nd-half IC=+0.1321, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.090, Q3_mid=+0.139, Q4=+0.098, Q5_high_vol=+0.122

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0764, Sharpe=-0.0635)
- Admission: Train IC=+0.1929, Deflated=+0.1933, IR=0.61, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.096 | 2017: +0.006 | 2018: +0.085 | 2019: +0.225 | 2020: +0.129 | 2021: +0.113 | 2022: +0.071 | 2023: +0.145 | 2024: +0.089 | 2025: +0.126 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.452 | 2016: +0.156 | 2017: -0.031 | 2018: +0.061 | 2019: +0.428 | 2020: +0.267 | 2021: +0.122 | 2022: +0.189 | 2023: +0.391 | 2024: +0.215 | 2025: +0.315 | 2026: -0.204
- IC CV=0.55, Neg years (linear/tail)=0/1 of 8, Half ratio=1.10, Recency ratio=2.59
- Early IC=+0.0452, Recent IC=+0.1169, 1st-half IC=+0.1023, 2nd-half IC=+0.1121, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.063, Q3_mid=+0.110, Q4=+0.083, Q5_high_vol=+0.154

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0761, Sharpe=-0.7836)
- Admission: Train IC=+0.2217, Deflated=+0.2222, IR=0.81, Mono=0.76, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.098 | 2017: +0.005 | 2018: +0.085 | 2019: +0.210 | 2020: +0.121 | 2021: +0.165 | 2022: +0.110 | 2023: +0.147 | 2024: +0.077 | 2025: +0.173 | 2026: -0.066
- Yearly Tail ICs:   2015: +0.066 | 2016: +0.133 | 2017: +0.037 | 2018: +0.201 | 2019: +0.313 | 2020: +0.150 | 2021: +0.292 | 2022: +0.260 | 2023: +0.378 | 2024: +0.203 | 2025: +0.118 | 2026: -0.259
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=2.51
- Early IC=+0.0447, Recent IC=+0.1122, 1st-half IC=+0.0972, 2nd-half IC=+0.1351, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.129, Q2=+0.076, Q3_mid=+0.141, Q4=+0.097, Q5_high_vol=+0.142

**`combo_max__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0757, Sharpe=-1.2229)
- Admission: Train IC=+0.1984, Deflated=+0.1975, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.050 | 2017: +0.054 | 2018: +0.051 | 2019: +0.124 | 2020: +0.092 | 2021: +0.162 | 2022: +0.102 | 2023: +0.182 | 2024: +0.062 | 2025: +0.191 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.098 | 2016: +0.114 | 2017: +0.002 | 2018: +0.118 | 2019: +0.251 | 2020: +0.080 | 2021: +0.303 | 2022: +0.289 | 2023: +0.472 | 2024: +0.227 | 2025: +0.112 | 2026: -0.530
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.87, Recency ratio=2.33
- Early IC=+0.0525, Recent IC=+0.1223, 1st-half IC=+0.0719, 2nd-half IC=+0.1346, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.083, Q3_mid=+0.126, Q4=+0.071, Q5_high_vol=+0.105

**`combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0738, Sharpe=-0.4608)
- Admission: Train IC=+0.2167, Deflated=+0.2161, IR=0.75, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.048 | 2017: +0.034 | 2018: +0.052 | 2019: +0.170 | 2020: +0.084 | 2021: +0.138 | 2022: +0.103 | 2023: +0.181 | 2024: +0.111 | 2025: +0.189 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.235 | 2016: -0.022 | 2017: +0.072 | 2018: +0.002 | 2019: +0.387 | 2020: +0.241 | 2021: +0.134 | 2022: +0.318 | 2023: +0.381 | 2024: +0.250 | 2025: +0.281 | 2026: -0.189
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.80, Recency ratio=3.40
- Early IC=+0.0429, Recent IC=+0.1461, 1st-half IC=+0.0778, 2nd-half IC=+0.1399, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.082, Q3_mid=+0.146, Q4=+0.068, Q5_high_vol=+0.115

**`combo_tri_max__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0737, Sharpe=-0.7924)
- Admission: Train IC=+0.2272, Deflated=+0.2280, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.160 | 2017: -0.014 | 2018: +0.112 | 2019: +0.197 | 2020: +0.141 | 2021: +0.173 | 2022: +0.107 | 2023: +0.145 | 2024: +0.053 | 2025: +0.176 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.176 | 2017: +0.021 | 2018: +0.204 | 2019: +0.275 | 2020: +0.175 | 2021: +0.373 | 2022: +0.244 | 2023: +0.368 | 2024: +0.184 | 2025: +0.138 | 2026: -0.316
- IC CV=0.55, Neg years (linear/tail)=1/0 of 8, Half ratio=1.31, Recency ratio=2.01
- Early IC=+0.0493, Recent IC=+0.0990, 1st-half IC=+0.0997, 2nd-half IC=+0.1302, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.089, Q3_mid=+0.122, Q4=+0.105, Q5_high_vol=+0.139

**`combo_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0732, Sharpe=-0.9166)
- Admission: Train IC=+0.2401, Deflated=+0.2408, IR=0.66, Mono=0.71, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.084 | 2017: +0.059 | 2018: +0.069 | 2019: +0.178 | 2020: +0.049 | 2021: +0.219 | 2022: +0.083 | 2023: +0.163 | 2024: +0.082 | 2025: +0.177 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.036 | 2016: +0.063 | 2017: +0.216 | 2018: +0.221 | 2019: +0.339 | 2020: +0.069 | 2021: +0.343 | 2022: +0.241 | 2023: +0.367 | 2024: +0.254 | 2025: +0.200 | 2026: -0.243
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.87, Recency ratio=1.92
- Early IC=+0.0637, Recent IC=+0.1225, 1st-half IC=+0.0786, 2nd-half IC=+0.1470, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.103, Q3_mid=+0.128, Q4=+0.117, Q5_high_vol=+0.120

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return`** (Lock IC=+0.0717, Sharpe=-1.1315)
- Admission: Train IC=+0.2299, Deflated=+0.2298, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.104 | 2017: +0.033 | 2018: +0.088 | 2019: +0.181 | 2020: +0.104 | 2021: +0.190 | 2022: +0.097 | 2023: +0.184 | 2024: +0.074 | 2025: +0.172 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.112 | 2016: +0.115 | 2017: +0.094 | 2018: +0.212 | 2019: +0.301 | 2020: +0.078 | 2021: +0.332 | 2022: +0.298 | 2023: +0.372 | 2024: +0.166 | 2025: +0.220 | 2026: -0.367
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.52, Recency ratio=2.13
- Early IC=+0.0606, Recent IC=+0.1293, 1st-half IC=+0.0941, 2nd-half IC=+0.1427, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.081, Q3_mid=+0.140, Q4=+0.100, Q5_high_vol=+0.135

**`combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector`** (Lock IC=+0.0690, Sharpe=-0.4019)
- Admission: Train IC=+0.1826, Deflated=+0.1812, IR=0.62, Mono=0.74, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.140 | 2016: +0.008 | 2017: +0.010 | 2018: +0.034 | 2019: +0.077 | 2020: +0.055 | 2021: +0.128 | 2022: +0.144 | 2023: +0.147 | 2024: +0.070 | 2025: +0.179 | 2026: -0.112
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.081 | 2017: +0.039 | 2018: -0.016 | 2019: +0.254 | 2020: +0.179 | 2021: +0.151 | 2022: +0.353 | 2023: +0.381 | 2024: +0.160 | 2025: +0.265 | 2026: -0.291
- IC CV=0.58, Neg years (linear/tail)=0/1 of 8, Half ratio=3.95, Recency ratio=4.89
- Early IC=+0.0222, Recent IC=+0.1085, 1st-half IC=+0.0328, 2nd-half IC=+0.1296, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.044, Q3_mid=+0.122, Q4=+0.059, Q5_high_vol=+0.083

**`max_up_ret`** (Lock IC=+0.0682, Sharpe=-0.6312)
- Admission: Train IC=+0.2091, Deflated=+0.2080, IR=0.91, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.080 | 2017: +0.050 | 2018: +0.066 | 2019: +0.143 | 2020: +0.113 | 2021: +0.166 | 2022: +0.116 | 2023: +0.175 | 2024: +0.074 | 2025: +0.164 | 2026: -0.075
- Yearly Tail ICs:   2015: +0.048 | 2016: +0.198 | 2017: +0.106 | 2018: +0.212 | 2019: +0.279 | 2020: +0.177 | 2021: +0.343 | 2022: +0.267 | 2023: +0.389 | 2024: +0.190 | 2025: +0.128 | 2026: -0.261
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.68, Recency ratio=2.15
- Early IC=+0.0580, Recent IC=+0.1246, 1st-half IC=+0.0835, 2nd-half IC=+0.1403, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.098, Q3_mid=+0.115, Q4=+0.089, Q5_high_vol=+0.126

**`combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0636, Sharpe=-1.2636)
- Admission: Train IC=+0.2118, Deflated=+0.2126, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.143 | 2017: +0.016 | 2018: +0.117 | 2019: +0.197 | 2020: +0.128 | 2021: +0.173 | 2022: +0.108 | 2023: +0.155 | 2024: +0.077 | 2025: +0.167 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.089 | 2016: +0.131 | 2017: +0.158 | 2018: +0.196 | 2019: +0.235 | 2020: +0.080 | 2021: +0.371 | 2022: +0.288 | 2023: +0.316 | 2024: +0.123 | 2025: +0.229 | 2026: -0.357
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.73
- Early IC=+0.0668, Recent IC=+0.1157, 1st-half IC=+0.1109, 2nd-half IC=+0.1357, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.105, Q3_mid=+0.130, Q4=+0.107, Q5_high_vol=+0.128

**`combo_max__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0516, Sharpe=-0.9575)
- Admission: Train IC=+0.2036, Deflated=+0.2027, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.164 | 2016: +0.043 | 2017: +0.044 | 2018: +0.075 | 2019: +0.065 | 2020: +0.104 | 2021: +0.152 | 2022: +0.122 | 2023: +0.158 | 2024: +0.074 | 2025: +0.140 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.016 | 2016: +0.198 | 2017: +0.052 | 2018: +0.160 | 2019: +0.278 | 2020: +0.149 | 2021: +0.338 | 2022: +0.268 | 2023: +0.353 | 2024: +0.188 | 2025: +0.128 | 2026: -0.316
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=2.11, Recency ratio=1.96
- Early IC=+0.0593, Recent IC=+0.1159, 1st-half IC=+0.0628, 2nd-half IC=+0.1328, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.062, Q3_mid=+0.106, Q4=+0.091, Q5_high_vol=+0.124

**`combo_z_sum__yesterday_first_30min_return__yesterday_early_trend`** (Lock IC=+0.0515, Sharpe=-0.6868)
- Admission: Train IC=+0.1124, Deflated=+0.1121, IR=0.37, Mono=0.65, p=0.0294, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.138 | 2017: -0.056 | 2018: +0.129 | 2019: +0.026 | 2020: +0.093 | 2021: +0.004 | 2022: +0.122 | 2023: +0.128 | 2024: +0.046 | 2025: +0.048 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.184 | 2016: +0.243 | 2017: -0.163 | 2018: +0.220 | 2019: +0.013 | 2020: +0.215 | 2021: +0.093 | 2022: +0.361 | 2023: +0.060 | 2024: +0.113 | 2025: -0.009 | 2026: -0.027
- IC CV=1.04, Neg years (linear/tail)=1/1 of 8, Half ratio=0.99, Recency ratio=2.40
- Early IC=+0.0362, Recent IC=+0.0869, 1st-half IC=+0.0663, 2nd-half IC=+0.0659, Neg regimes=1/5
- Weak component: `yesterday_early_trend` (CV=1.18)
- Regime ICs: Q1_low_vol=-0.010, Q2=+0.101, Q3_mid=+0.072, Q4=+0.093, Q5_high_vol=+0.075

**`combo_rank_max__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0450, Sharpe=-0.2526)
- Admission: Train IC=+0.1846, Deflated=+0.1851, IR=0.38, Mono=0.66, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.244 | 2016: +0.095 | 2017: -0.027 | 2018: +0.075 | 2019: +0.172 | 2020: +0.164 | 2021: +0.131 | 2022: +0.048 | 2023: +0.087 | 2024: +0.056 | 2025: +0.083 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.242 | 2016: -0.262 | 2017: -0.038 | 2018: +0.355 | 2019: +0.243 | 2020: +0.291 | 2021: +0.281 | 2022: +0.162 | 2023: +0.181 | 2024: +0.055 | 2025: +0.121 | 2026: -0.195
- IC CV=0.70, Neg years (linear/tail)=1/1 of 8, Half ratio=1.02, Recency ratio=2.97
- Early IC=+0.0242, Recent IC=+0.0717, 1st-half IC=+0.0875, 2nd-half IC=+0.0895, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.052, Q3_mid=+0.094, Q4=+0.072, Q5_high_vol=+0.113

**`combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0`** (Lock IC=+0.0366, Sharpe=-0.2937)
- Admission: Train IC=+0.1484, Deflated=+0.1481, IR=0.34, Mono=0.65, p=0.0038, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.132 | 2016: +0.061 | 2017: +0.071 | 2018: +0.148 | 2019: +0.153 | 2020: +0.101 | 2021: +0.131 | 2022: +0.046 | 2023: +0.200 | 2024: +0.103 | 2025: +0.138 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.245 | 2016: -0.074 | 2017: -0.040 | 2018: +0.134 | 2019: +0.353 | 2020: +0.143 | 2021: +0.197 | 2022: +0.031 | 2023: +0.304 | 2024: +0.176 | 2025: +0.366 | 2026: -0.008
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=1.15, Recency ratio=1.38
- Early IC=+0.1097, Recent IC=+0.1516, 1st-half IC=+0.1076, 2nd-half IC=+0.1234, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.088, Q3_mid=+0.127, Q4=+0.083, Q5_high_vol=+0.165

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0366, Sharpe=-0.6946)
- Admission: Train IC=+0.1947, Deflated=+0.1949, IR=0.88, Mono=0.81, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.083 | 2016: +0.041 | 2017: +0.086 | 2018: +0.110 | 2019: +0.176 | 2020: +0.053 | 2021: +0.141 | 2022: +0.085 | 2023: +0.175 | 2024: +0.128 | 2025: +0.123 | 2026: -0.082
- Yearly Tail ICs:   2015: -0.248 | 2016: +0.198 | 2017: +0.162 | 2018: +0.240 | 2019: +0.254 | 2020: +0.156 | 2021: +0.147 | 2022: +0.191 | 2023: +0.389 | 2024: +0.298 | 2025: -0.010 | 2026: -0.104
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.47, Recency ratio=1.54
- Early IC=+0.0983, Recent IC=+0.1515, 1st-half IC=+0.0939, 2nd-half IC=+0.1380, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.078, Q3_mid=+0.115, Q4=+0.096, Q5_high_vol=+0.136

**`combo_sig_product__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0278, Sharpe=-0.5804)
- Admission: Train IC=+0.1264, Deflated=+0.1264, IR=0.41, Mono=0.68, p=0.0144, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.073 | 2017: +0.101 | 2018: +0.140 | 2019: +0.150 | 2020: +0.077 | 2021: +0.127 | 2022: +0.041 | 2023: +0.193 | 2024: +0.106 | 2025: +0.129 | 2026: -0.107
- Yearly Tail ICs:   2015: -0.067 | 2016: -0.040 | 2017: +0.215 | 2018: +0.174 | 2019: +0.114 | 2020: +0.019 | 2021: +0.258 | 2022: +0.036 | 2023: +0.291 | 2024: +0.114 | 2025: +0.139 | 2026: -0.097
- IC CV=0.37, Neg years (linear/tail)=0/0 of 8, Half ratio=1.09, Recency ratio=1.24
- Early IC=+0.1206, Recent IC=+0.1492, 1st-half IC=+0.1053, 2nd-half IC=+0.1148, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.071, Q3_mid=+0.116, Q4=+0.089, Q5_high_vol=+0.142

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration`** (Lock IC=+0.0575, Sharpe=+0.6959)
- Admission: Train IC=+0.1451, Deflated=+0.1460, IR=0.44, Mono=0.67, p=0.0042, MaxCorr=0.32
- Yearly Linear ICs: 2015: +0.022 | 2016: +0.005 | 2017: +0.040 | 2018: +0.076 | 2019: +0.041 | 2020: +0.030 | 2021: +0.170 | 2022: +0.027 | 2023: +0.048 | 2024: -0.031 | 2025: +0.044 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.258 | 2016: +0.108 | 2017: +0.045 | 2018: +0.319 | 2019: +0.057 | 2020: +0.178 | 2021: +0.173 | 2022: +0.149 | 2023: +0.060 | 2024: +0.193 | 2025: +0.078 | 2026: +0.104
- IC CV=1.06, Neg years (linear/tail)=1/0 of 8, Half ratio=1.61, Recency ratio=0.14
- Early IC=+0.0581, Recent IC=+0.0083, 1st-half IC=+0.0385, 2nd-half IC=+0.0621, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.037, Q2=+0.024, Q3_mid=+0.048, Q4=+0.030, Q5_high_vol=+0.129

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0592, Sharpe=+0.5373)
- Admission: Train IC=+0.2034, Deflated=+0.2025, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.114 | 2017: +0.000 | 2018: +0.208 | 2019: +0.104 | 2020: +0.048 | 2021: +0.143 | 2022: +0.085 | 2023: +0.105 | 2024: +0.016 | 2025: +0.065 | 2026: +0.047
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.119 | 2017: +0.028 | 2018: +0.272 | 2019: +0.237 | 2020: +0.158 | 2021: +0.424 | 2022: +0.269 | 2023: +0.077 | 2024: +0.168 | 2025: +0.225 | 2026: +0.111
- IC CV=0.72, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=0.58
- Early IC=+0.1045, Recent IC=+0.0606, 1st-half IC=+0.0953, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.027, Q2=+0.058, Q3_mid=+0.045, Q4=+0.067, Q5_high_vol=+0.233

**`combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0559, Sharpe=+0.3783)
- Admission: Train IC=+0.2333, Deflated=+0.2327, IR=0.65, Mono=0.79, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.094 | 2017: +0.021 | 2018: +0.206 | 2019: +0.107 | 2020: +0.039 | 2021: +0.136 | 2022: +0.069 | 2023: +0.126 | 2024: +0.016 | 2025: +0.091 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.011 | 2017: -0.032 | 2018: +0.313 | 2019: +0.160 | 2020: +0.262 | 2021: +0.378 | 2022: +0.326 | 2023: +0.222 | 2024: +0.158 | 2025: +0.282 | 2026: +0.096
- IC CV=0.69, Neg years (linear/tail)=0/1 of 8, Half ratio=0.92, Recency ratio=0.63
- Early IC=+0.1136, Recent IC=+0.0711, 1st-half IC=+0.1004, 2nd-half IC=+0.0927, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.49)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.068, Q3_mid=+0.055, Q4=+0.082, Q5_high_vol=+0.212

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.0808, Sharpe=+0.3659)
- Admission: Train IC=+0.2286, Deflated=+0.2287, IR=0.48, Mono=0.68, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=1.04, Recency ratio=1.45
- Early IC=+0.0589, Recent IC=+0.0855, 1st-half IC=+0.0825, 2nd-half IC=+0.0862, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.064, Q3_mid=+0.070, Q4=+0.060, Q5_high_vol=+0.200

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0808, Sharpe=+0.3659)
- Admission: Train IC=+0.2286, Deflated=+0.2287, IR=0.48, Mono=0.68, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.86, Neg years (linear/tail)=1/1 of 8, Half ratio=1.04, Recency ratio=1.45
- Early IC=+0.0589, Recent IC=+0.0855, 1st-half IC=+0.0825, 2nd-half IC=+0.0862, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=2.51)
- Regime ICs: Q1_low_vol=+0.007, Q2=+0.064, Q3_mid=+0.070, Q4=+0.060, Q5_high_vol=+0.200

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0326, Sharpe=+0.1677)
- Admission: Train IC=+0.2112, Deflated=+0.2105, IR=0.62, Mono=0.72, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.214 | 2016: +0.117 | 2017: -0.020 | 2018: +0.232 | 2019: +0.099 | 2020: +0.054 | 2021: +0.163 | 2022: +0.065 | 2023: +0.130 | 2024: +0.029 | 2025: +0.076 | 2026: -0.045
- Yearly Tail ICs:   2015: +0.198 | 2016: +0.112 | 2017: -0.026 | 2018: +0.363 | 2019: +0.287 | 2020: +0.118 | 2021: +0.395 | 2022: +0.239 | 2023: +0.102 | 2024: +0.209 | 2025: +0.196 | 2026: +0.115
- IC CV=0.80, Neg years (linear/tail)=1/1 of 8, Half ratio=1.10, Recency ratio=0.75
- Early IC=+0.1059, Recent IC=+0.0790, 1st-half IC=+0.0968, 2nd-half IC=+0.1063, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.079, Q3_mid=+0.047, Q4=+0.073, Q5_high_vol=+0.252

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0081, Sharpe=+0.1648)
- Admission: Train IC=+0.2066, Deflated=+0.2062, IR=0.67, Mono=0.71, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.107 | 2017: -0.057 | 2018: +0.207 | 2019: +0.078 | 2020: +0.072 | 2021: +0.171 | 2022: +0.067 | 2023: +0.123 | 2024: +0.029 | 2025: +0.069 | 2026: -0.083
- Yearly Tail ICs:   2015: +0.047 | 2016: +0.129 | 2017: +0.093 | 2018: +0.405 | 2019: +0.283 | 2020: +0.039 | 2021: +0.365 | 2022: +0.231 | 2023: +0.096 | 2024: +0.207 | 2025: +0.086 | 2026: +0.043
- IC CV=0.89, Neg years (linear/tail)=1/0 of 8, Half ratio=1.35, Recency ratio=1.02
- Early IC=+0.0748, Recent IC=+0.0762, 1st-half IC=+0.0783, 2nd-half IC=+0.1056, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.017, Q2=+0.068, Q3_mid=+0.027, Q4=+0.063, Q5_high_vol=+0.255

**`combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction`** (Lock IC=+0.0306, Sharpe=+0.1091)
- Admission: Train IC=+0.1905, Deflated=+0.1897, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.074 | 2016: +0.088 | 2017: -0.045 | 2018: +0.216 | 2019: +0.095 | 2020: +0.051 | 2021: +0.124 | 2022: +0.054 | 2023: +0.133 | 2024: +0.010 | 2025: +0.099 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.183 | 2016: +0.054 | 2017: -0.157 | 2018: +0.314 | 2019: +0.254 | 2020: +0.197 | 2021: +0.296 | 2022: +0.127 | 2023: +0.296 | 2024: +0.156 | 2025: +0.339 | 2026: -0.229
- IC CV=0.98, Neg years (linear/tail)=1/1 of 8, Half ratio=1.01, Recency ratio=0.85
- Early IC=+0.0848, Recent IC=+0.0717, 1st-half IC=+0.0834, 2nd-half IC=+0.0839, Neg regimes=1/5
- Weak component: `volume_surge_direction` (CV=1.10)
- Regime ICs: Q1_low_vol=-0.003, Q2=+0.114, Q3_mid=+0.022, Q4=+0.084, Q5_high_vol=+0.177

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0276, Sharpe=+0.0106)
- Admission: Train IC=+0.2054, Deflated=+0.2055, IR=0.54, Mono=0.72, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.096 | 2017: -0.072 | 2018: +0.144 | 2019: +0.091 | 2020: +0.062 | 2021: +0.138 | 2022: +0.048 | 2023: +0.132 | 2024: +0.044 | 2025: +0.060 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.312 | 2016: -0.044 | 2017: -0.042 | 2018: +0.223 | 2019: +0.226 | 2020: +0.119 | 2021: +0.429 | 2022: +0.245 | 2023: +0.115 | 2024: +0.334 | 2025: +0.057 | 2026: +0.045
- IC CV=0.94, Neg years (linear/tail)=1/1 of 8, Half ratio=1.57, Recency ratio=2.57
- Early IC=+0.0341, Recent IC=+0.0875, 1st-half IC=+0.0624, 2nd-half IC=+0.0978, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.018, Q2=+0.041, Q3_mid=+0.072, Q4=+0.026, Q5_high_vol=+0.224

### 500ETF — `single` True Positives

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0661, Sharpe=+1.4473)
- Admission: Train IC=+0.1843, Deflated=+0.1829, IR=0.58, Mono=0.69, p=0.0002, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.097 | 2017: +0.143 | 2018: +0.183 | 2019: +0.076 | 2020: +0.106 | 2021: +0.120 | 2022: +0.098 | 2023: -0.003 | 2024: +0.128 | 2025: +0.092 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.413 | 2016: +0.171 | 2017: +0.267 | 2018: +0.413 | 2019: +0.079 | 2020: +0.098 | 2021: +0.343 | 2022: +0.070 | 2023: +0.048 | 2024: +0.169 | 2025: +0.232 | 2026: +0.367
- IC CV=0.48, Neg years (linear/tail)=1/0 of 8, Half ratio=0.80, Recency ratio=0.38
- Early IC=+0.1629, Recent IC=+0.0623, 1st-half IC=+0.1197, 2nd-half IC=+0.0956, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.027, Q3_mid=+0.037, Q4=+0.083, Q5_high_vol=+0.211

**`combo_clamp_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1143, Sharpe=+1.3960)
- Admission: Train IC=+0.2159, Deflated=+0.2145, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.89
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

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0995, Sharpe=+1.2591)
- Admission: Train IC=+0.1672, Deflated=+0.1666, IR=0.74, Mono=0.75, p=0.0010, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.113 | 2019: +0.122 | 2020: +0.121 | 2021: +0.073 | 2022: +0.056 | 2023: +0.064 | 2024: +0.085 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.111 | 2017: +0.267 | 2018: +0.360 | 2019: +0.324 | 2020: +0.217 | 2021: +0.340 | 2022: +0.063 | 2023: +0.041 | 2024: +0.147 | 2025: +0.082 | 2026: +0.223
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.42
- Early IC=+0.1751, Recent IC=+0.0740, 1st-half IC=+0.1269, 2nd-half IC=+0.0731, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.199, Q2=-0.014, Q3_mid=+0.113, Q4=+0.120, Q5_high_vol=+0.129

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1107, Sharpe=+1.2537)
- Admission: Train IC=+0.2114, Deflated=+0.2098, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.030 | 2017: +0.190 | 2018: +0.142 | 2019: +0.181 | 2020: +0.142 | 2021: +0.093 | 2022: +0.048 | 2023: +0.069 | 2024: +0.097 | 2025: +0.039 | 2026: +0.231
- Yearly Tail ICs:   2015: +0.317 | 2016: -0.022 | 2017: +0.293 | 2018: +0.254 | 2019: +0.349 | 2020: +0.237 | 2021: +0.256 | 2022: -0.080 | 2023: +0.233 | 2024: +0.196 | 2025: -0.008 | 2026: +0.310
- IC CV=0.40, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.50
- Early IC=+0.1659, Recent IC=+0.0830, 1st-half IC=+0.1589, 2nd-half IC=+0.0788, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.003, Q3_mid=+0.069, Q4=+0.153, Q5_high_vol=+0.182

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.0505, Sharpe=+1.1989)
- Admission: Train IC=+0.1469, Deflated=+0.1447, IR=0.56, Mono=0.68, p=0.0040, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.136 | 2017: +0.128 | 2018: +0.125 | 2019: +0.098 | 2020: +0.104 | 2021: +0.068 | 2022: +0.103 | 2023: +0.034 | 2024: +0.145 | 2025: +0.054 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.177 | 2017: +0.119 | 2018: +0.196 | 2019: +0.143 | 2020: +0.201 | 2021: +0.196 | 2022: +0.008 | 2023: +0.036 | 2024: +0.115 | 2025: +0.036 | 2026: +0.312
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=0.86, Recency ratio=0.71
- Early IC=+0.1267, Recent IC=+0.0894, 1st-half IC=+0.1089, 2nd-half IC=+0.0931, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.175, Q2=-0.006, Q3_mid=+0.033, Q4=+0.093, Q5_high_vol=+0.169

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1502, Sharpe=+1.1714)
- Admission: Train IC=+0.1888, Deflated=+0.1873, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.70
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.043 | 2017: +0.167 | 2018: +0.148 | 2019: +0.174 | 2020: +0.083 | 2021: +0.082 | 2022: +0.053 | 2023: +0.110 | 2024: +0.162 | 2025: +0.108 | 2026: +0.199
- Yearly Tail ICs:   2015: -0.019 | 2016: +0.052 | 2017: +0.155 | 2018: +0.211 | 2019: +0.382 | 2020: +0.173 | 2021: +0.150 | 2022: +0.176 | 2023: +0.077 | 2024: +0.225 | 2025: +0.105 | 2026: +0.339
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.72, Recency ratio=0.86
- Early IC=+0.1574, Recent IC=+0.1361, 1st-half IC=+0.1410, 2nd-half IC=+0.1018, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.088, Q3_mid=+0.109, Q4=+0.108, Q5_high_vol=+0.160

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.1034, Sharpe=+1.0177)
- Admission: Train IC=+0.1469, Deflated=+0.1469, IR=0.50, Mono=0.67, p=0.0040, MaxCorr=0.13
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073 | 2025: +0.148 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.229 | 2017: +0.386 | 2018: +0.332 | 2019: +0.207 | 2020: +0.271 | 2021: +0.214 | 2022: -0.027 | 2023: +0.087 | 2024: +0.035 | 2025: +0.246 | 2026: +0.214
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.50, Recency ratio=0.34
- Early IC=+0.1761, Recent IC=+0.0591, 1st-half IC=+0.1355, 2nd-half IC=+0.0682, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.148, Q2=-0.015, Q3_mid=+0.115, Q4=+0.160, Q5_high_vol=+0.116

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1327, Sharpe=+0.9157)
- Admission: Train IC=+0.1775, Deflated=+0.1764, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.031 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.030 | 2024: +0.178 | 2025: +0.302 | 2026: +0.147
- IC CV=0.54, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.54
- Early IC=+0.1598, Recent IC=+0.0858, 1st-half IC=+0.1342, 2nd-half IC=+0.0836, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.026, Q3_mid=+0.111, Q4=+0.124, Q5_high_vol=+0.121

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1095, Sharpe=+0.7916)
- Admission: Train IC=+0.2252, Deflated=+0.2238, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.099 | 2017: +0.233 | 2018: +0.132 | 2019: +0.098 | 2020: +0.133 | 2021: +0.117 | 2022: +0.056 | 2023: +0.096 | 2024: +0.118 | 2025: +0.140 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.228 | 2017: +0.343 | 2018: +0.291 | 2019: +0.226 | 2020: +0.281 | 2021: +0.290 | 2022: +0.057 | 2023: +0.199 | 2024: +0.212 | 2025: +0.046 | 2026: +0.090
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.71, Recency ratio=0.58
- Early IC=+0.1821, Recent IC=+0.1052, 1st-half IC=+0.1377, 2nd-half IC=+0.0981, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.001, Q3_mid=+0.097, Q4=+0.107, Q5_high_vol=+0.174

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

**`combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1068, Sharpe=+0.6164)
- Admission: Train IC=+0.1284, Deflated=+0.1268, IR=0.39, Mono=0.69, p=0.0104, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.102 | 2017: +0.246 | 2018: +0.139 | 2019: +0.137 | 2020: +0.130 | 2021: +0.050 | 2022: +0.134 | 2023: +0.080 | 2024: +0.104 | 2025: +0.080 | 2026: +0.142
- Yearly Tail ICs:   2015: +0.222 | 2016: +0.144 | 2017: +0.171 | 2018: +0.053 | 2019: +0.295 | 2020: +0.064 | 2021: +0.144 | 2022: +0.108 | 2023: -0.025 | 2024: +0.060 | 2025: +0.087 | 2026: +0.140
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.49
- Early IC=+0.1922, Recent IC=+0.0933, 1st-half IC=+0.1564, 2nd-half IC=+0.1023, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.028, Q3_mid=+0.120, Q4=+0.131, Q5_high_vol=+0.139

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0958, Sharpe=+0.5075)
- Admission: Train IC=+0.2267, Deflated=+0.2261, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.41, Recency ratio=0.41
- Early IC=+0.2081, Recent IC=+0.0846, 1st-half IC=+0.1734, 2nd-half IC=+0.0709, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.210, Q2=-0.029, Q3_mid=+0.064, Q4=+0.154, Q5_high_vol=+0.202

**`combo_rank_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0715, Sharpe=+0.4915)
- Admission: Train IC=+0.1827, Deflated=+0.1829, IR=0.72, Mono=0.75, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.090 | 2017: +0.239 | 2018: +0.234 | 2019: +0.150 | 2020: +0.126 | 2021: +0.098 | 2022: +0.093 | 2023: +0.036 | 2024: +0.117 | 2025: +0.112 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.605 | 2016: -0.121 | 2017: +0.202 | 2018: +0.245 | 2019: +0.306 | 2020: +0.177 | 2021: +0.248 | 2022: +0.130 | 2023: +0.169 | 2024: +0.217 | 2025: +0.104 | 2026: -0.076
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.32
- Early IC=+0.2339, Recent IC=+0.0745, 1st-half IC=+0.1668, 2nd-half IC=+0.0928, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.027, Q3_mid=+0.134, Q4=+0.151, Q5_high_vol=+0.168

**`combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.0730, Sharpe=+0.4368)
- Admission: Train IC=+0.1762, Deflated=+0.1755, IR=0.47, Mono=0.67, p=0.0002, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.120 | 2016: +0.081 | 2017: +0.050 | 2018: +0.081 | 2019: +0.027 | 2020: +0.074 | 2021: -0.004 | 2022: +0.092 | 2023: +0.004 | 2024: +0.052 | 2025: +0.120 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.064 | 2017: +0.008 | 2018: +0.230 | 2019: +0.198 | 2020: +0.165 | 2021: +0.131 | 2022: +0.290 | 2023: +0.032 | 2024: +0.170 | 2025: +0.143 | 2026: -0.126
- IC CV=0.71, Neg years (linear/tail)=1/0 of 8, Half ratio=0.67, Recency ratio=0.42
- Early IC=+0.0657, Recent IC=+0.0279, 1st-half IC=+0.0579, 2nd-half IC=+0.0389, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.030, Q3_mid=+0.042, Q4=+0.043, Q5_high_vol=+0.078

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.0959, Sharpe=+0.4192)
- Admission: Train IC=+0.2631, Deflated=+0.2618, IR=0.81, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.096 | 2017: +0.219 | 2018: +0.144 | 2019: +0.100 | 2020: +0.114 | 2021: +0.119 | 2022: +0.077 | 2023: +0.113 | 2024: +0.124 | 2025: +0.139 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.303 | 2016: +0.235 | 2017: +0.309 | 2018: +0.376 | 2019: +0.189 | 2020: +0.286 | 2021: +0.174 | 2022: +0.185 | 2023: +0.203 | 2024: +0.345 | 2025: +0.179 | 2026: +0.232
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.84, Recency ratio=0.66
- Early IC=+0.1815, Recent IC=+0.1189, 1st-half IC=+0.1306, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.008, Q3_mid=+0.094, Q4=+0.106, Q5_high_vol=+0.169

**`combo_min__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0754, Sharpe=+0.4070)
- Admission: Train IC=+0.1539, Deflated=+0.1533, IR=0.48, Mono=0.67, p=0.0024, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.100 | 2017: +0.191 | 2018: +0.144 | 2019: +0.096 | 2020: +0.109 | 2021: +0.068 | 2022: +0.070 | 2023: +0.080 | 2024: +0.110 | 2025: +0.156 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.076 | 2017: +0.268 | 2018: +0.174 | 2019: +0.104 | 2020: +0.113 | 2021: +0.209 | 2022: +0.083 | 2023: +0.142 | 2024: +0.059 | 2025: +0.197 | 2026: +0.146
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.70, Recency ratio=0.57
- Early IC=+0.1672, Recent IC=+0.0954, 1st-half IC=+0.1215, 2nd-half IC=+0.0848, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.200, Q2=-0.017, Q3_mid=+0.086, Q4=+0.128, Q5_high_vol=+0.130

**`combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`** (Lock IC=+0.0700, Sharpe=+0.3994)
- Admission: Train IC=+0.1920, Deflated=+0.1913, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.033 | 2017: +0.193 | 2018: +0.176 | 2019: +0.152 | 2020: +0.142 | 2021: +0.127 | 2022: +0.039 | 2023: +0.094 | 2024: +0.101 | 2025: +0.047 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.442 | 2016: +0.051 | 2017: +0.431 | 2018: +0.139 | 2019: +0.294 | 2020: +0.117 | 2021: +0.193 | 2022: +0.049 | 2023: +0.138 | 2024: +0.214 | 2025: +0.038 | 2026: +0.348
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.53
- Early IC=+0.1842, Recent IC=+0.0976, 1st-half IC=+0.1550, 2nd-half IC=+0.0947, Neg regimes=1/5
- Weak component: `late_bar_momentum` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.196, Q2=-0.013, Q3_mid=+0.096, Q4=+0.136, Q5_high_vol=+0.182

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0982, Sharpe=+0.3922)
- Admission: Train IC=+0.1734, Deflated=+0.1721, IR=0.66, Mono=0.71, p=0.0006, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.039 | 2017: +0.233 | 2018: +0.109 | 2019: +0.115 | 2020: +0.103 | 2021: +0.063 | 2022: +0.077 | 2023: +0.078 | 2024: +0.083 | 2025: +0.141 | 2026: +0.075
- Yearly Tail ICs:   2015: +0.334 | 2016: +0.075 | 2017: +0.275 | 2018: +0.294 | 2019: +0.307 | 2020: +0.201 | 2021: +0.170 | 2022: +0.134 | 2023: +0.050 | 2024: +0.141 | 2025: +0.054 | 2026: +0.139
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=0.68, Recency ratio=0.47
- Early IC=+0.1708, Recent IC=+0.0804, 1st-half IC=+0.1153, 2nd-half IC=+0.0789, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.004, Q3_mid=+0.102, Q4=+0.111, Q5_high_vol=+0.123

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0857, Sharpe=+0.3857)
- Admission: Train IC=+0.2468, Deflated=+0.2452, IR=0.92, Mono=0.81, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.116 | 2017: +0.229 | 2018: +0.212 | 2019: +0.142 | 2020: +0.186 | 2021: +0.124 | 2022: +0.094 | 2023: +0.080 | 2024: +0.131 | 2025: +0.106 | 2026: +0.067
- Yearly Tail ICs:   2015: +0.240 | 2016: +0.225 | 2017: +0.268 | 2018: +0.396 | 2019: +0.311 | 2020: +0.120 | 2021: +0.232 | 2022: +0.304 | 2023: +0.146 | 2024: +0.228 | 2025: +0.010 | 2026: +0.090
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.60, Recency ratio=0.48
- Early IC=+0.2205, Recent IC=+0.1056, 1st-half IC=+0.1842, 2nd-half IC=+0.1109, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.230, Q2=+0.016, Q3_mid=+0.118, Q4=+0.151, Q5_high_vol=+0.212

**`combo_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1060, Sharpe=+0.3487)
- Admission: Train IC=+0.2512, Deflated=+0.2503, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.061 | 2017: +0.230 | 2018: +0.103 | 2019: +0.129 | 2020: +0.120 | 2021: +0.095 | 2022: +0.065 | 2023: +0.083 | 2024: +0.138 | 2025: +0.136 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.261 | 2016: +0.194 | 2017: +0.222 | 2018: +0.324 | 2019: +0.281 | 2020: +0.268 | 2021: -0.009 | 2022: +0.189 | 2023: +0.192 | 2024: +0.372 | 2025: +0.031 | 2026: +0.270
- IC CV=0.39, Neg years (linear/tail)=0/1 of 8, Half ratio=0.78, Recency ratio=0.66
- Early IC=+0.1662, Recent IC=+0.1102, 1st-half IC=+0.1261, 2nd-half IC=+0.0982, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.211, Q2=-0.009, Q3_mid=+0.099, Q4=+0.123, Q5_high_vol=+0.147

**`combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1112, Sharpe=+0.3432)
- Admission: Train IC=+0.2520, Deflated=+0.2506, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.091 | 2017: +0.219 | 2018: +0.137 | 2019: +0.108 | 2020: +0.139 | 2021: +0.071 | 2022: +0.079 | 2023: +0.063 | 2024: +0.109 | 2025: +0.126 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.232 | 2016: +0.116 | 2017: +0.279 | 2018: +0.296 | 2019: +0.366 | 2020: +0.160 | 2021: +0.155 | 2022: +0.270 | 2023: +0.138 | 2024: +0.273 | 2025: +0.139 | 2026: +0.153
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.48
- Early IC=+0.1777, Recent IC=+0.0861, 1st-half IC=+0.1394, 2nd-half IC=+0.0864, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.015, Q3_mid=+0.087, Q4=+0.106, Q5_high_vol=+0.150

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0921, Sharpe=+0.3192)
- Admission: Train IC=+0.2329, Deflated=+0.2322, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.315 | 2016: +0.087 | 2017: +0.219 | 2018: +0.204 | 2019: +0.175 | 2020: +0.133 | 2021: +0.087 | 2022: +0.047 | 2023: +0.079 | 2024: +0.088 | 2025: +0.120 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.128 | 2017: +0.185 | 2018: +0.457 | 2019: +0.304 | 2020: +0.267 | 2021: +0.043 | 2022: +0.131 | 2023: +0.135 | 2024: +0.262 | 2025: +0.099 | 2026: +0.094
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.40, Recency ratio=0.39
- Early IC=+0.2119, Recent IC=+0.0837, 1st-half IC=+0.1713, 2nd-half IC=+0.0682, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.029, Q3_mid=+0.059, Q4=+0.152, Q5_high_vol=+0.193

**`combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0335, Sharpe=+0.3145)
- Admission: Train IC=+0.1767, Deflated=+0.1756, IR=0.56, Mono=0.71, p=0.0002, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.032 | 2017: +0.038 | 2018: +0.068 | 2019: +0.151 | 2020: +0.080 | 2021: +0.101 | 2022: -0.007 | 2023: +0.011 | 2024: +0.054 | 2025: -0.055 | 2026: +0.188
- Yearly Tail ICs:   2015: +0.079 | 2016: +0.006 | 2017: +0.370 | 2018: +0.192 | 2019: +0.353 | 2020: +0.212 | 2021: +0.094 | 2022: -0.095 | 2023: +0.100 | 2024: +0.083 | 2025: -0.086 | 2026: +0.210
- IC CV=0.77, Neg years (linear/tail)=1/1 of 8, Half ratio=0.59, Recency ratio=0.61
- Early IC=+0.0528, Recent IC=+0.0323, 1st-half IC=+0.0810, 2nd-half IC=+0.0477, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.051, Q2=-0.012, Q3_mid=+0.059, Q4=+0.058, Q5_high_vol=+0.124

**`combo_rank_max__net_volume_flow__max_down_ret`** (Lock IC=+0.0648, Sharpe=+0.3118)
- Admission: Train IC=+0.2065, Deflated=+0.2064, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.059 | 2017: +0.210 | 2018: +0.179 | 2019: +0.125 | 2020: +0.107 | 2021: +0.090 | 2022: +0.079 | 2023: +0.043 | 2024: +0.142 | 2025: +0.152 | 2026: -0.054
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.048 | 2017: +0.247 | 2018: +0.114 | 2019: +0.383 | 2020: +0.043 | 2021: +0.300 | 2022: +0.244 | 2023: +0.162 | 2024: +0.340 | 2025: +0.240 | 2026: -0.023
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.69, Recency ratio=0.49
- Early IC=+0.1931, Recent IC=+0.0956, 1st-half IC=+0.1398, 2nd-half IC=+0.0966, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.217, Q2=-0.006, Q3_mid=+0.127, Q4=+0.133, Q5_high_vol=+0.134

**`combo_rank_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1093, Sharpe=+0.3039)
- Admission: Train IC=+0.2219, Deflated=+0.2209, IR=0.80, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.062 | 2017: +0.234 | 2018: +0.094 | 2019: +0.126 | 2020: +0.128 | 2021: +0.102 | 2022: +0.063 | 2023: +0.081 | 2024: +0.147 | 2025: +0.138 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.179 | 2017: +0.308 | 2018: +0.369 | 2019: +0.230 | 2020: +0.307 | 2021: +0.069 | 2022: +0.163 | 2023: +0.183 | 2024: +0.355 | 2025: +0.082 | 2026: +0.280
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.77, Recency ratio=0.72
- Early IC=+0.1605, Recent IC=+0.1155, 1st-half IC=+0.1314, 2nd-half IC=+0.1006, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.205, Q2=-0.002, Q3_mid=+0.100, Q4=+0.129, Q5_high_vol=+0.159

**`combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector`** (Lock IC=+0.0817, Sharpe=+0.3027)
- Admission: Train IC=+0.2502, Deflated=+0.2492, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.075 | 2017: +0.193 | 2018: +0.139 | 2019: +0.080 | 2020: +0.127 | 2021: +0.055 | 2022: +0.084 | 2023: +0.069 | 2024: +0.100 | 2025: +0.126 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.359 | 2016: +0.110 | 2017: +0.268 | 2018: +0.242 | 2019: +0.237 | 2020: +0.193 | 2021: +0.210 | 2022: +0.340 | 2023: +0.197 | 2024: +0.238 | 2025: +0.209 | 2026: -0.053
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=0.65, Recency ratio=0.51
- Early IC=+0.1663, Recent IC=+0.0841, 1st-half IC=+0.1269, 2nd-half IC=+0.0820, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.018, Q3_mid=+0.087, Q4=+0.095, Q5_high_vol=+0.135

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0867, Sharpe=+0.2984)
- Admission: Train IC=+0.2699, Deflated=+0.2686, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.093 | 2017: +0.220 | 2018: +0.191 | 2019: +0.123 | 2020: +0.135 | 2021: +0.152 | 2022: +0.043 | 2023: +0.113 | 2024: +0.145 | 2025: +0.122 | 2026: +0.045
- Yearly Tail ICs:   2015: +0.324 | 2016: +0.237 | 2017: +0.318 | 2018: +0.445 | 2019: +0.311 | 2020: +0.263 | 2021: +0.249 | 2022: +0.229 | 2023: +0.195 | 2024: +0.288 | 2025: +0.082 | 2026: +0.241
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.74, Recency ratio=0.63
- Early IC=+0.2057, Recent IC=+0.1289, 1st-half IC=+0.1555, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.228, Q2=+0.016, Q3_mid=+0.102, Q4=+0.111, Q5_high_vol=+0.201

**`combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0920, Sharpe=+0.2951)
- Admission: Train IC=+0.2329, Deflated=+0.2322, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.315 | 2016: +0.087 | 2017: +0.219 | 2018: +0.204 | 2019: +0.175 | 2020: +0.134 | 2021: +0.087 | 2022: +0.047 | 2023: +0.079 | 2024: +0.088 | 2025: +0.119 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.123 | 2017: +0.186 | 2018: +0.457 | 2019: +0.304 | 2020: +0.267 | 2021: +0.041 | 2022: +0.131 | 2023: +0.134 | 2024: +0.262 | 2025: +0.096 | 2026: +0.094
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.40, Recency ratio=0.39
- Early IC=+0.2119, Recent IC=+0.0836, 1st-half IC=+0.1713, 2nd-half IC=+0.0682, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.215, Q2=-0.029, Q3_mid=+0.059, Q4=+0.152, Q5_high_vol=+0.192

**`combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.1145, Sharpe=+0.2769)
- Admission: Train IC=+0.2328, Deflated=+0.2316, IR=0.87, Mono=0.83, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.096 | 2017: +0.227 | 2018: +0.137 | 2019: +0.123 | 2020: +0.150 | 2021: +0.116 | 2022: +0.070 | 2023: +0.090 | 2024: +0.121 | 2025: +0.148 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.248 | 2017: +0.311 | 2018: +0.407 | 2019: +0.129 | 2020: +0.336 | 2021: +0.116 | 2022: +0.084 | 2023: +0.195 | 2024: +0.361 | 2025: +0.093 | 2026: +0.243
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.57
- Early IC=+0.1814, Recent IC=+0.1028, 1st-half IC=+0.1479, 2nd-half IC=+0.0974, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.206, Q2=-0.008, Q3_mid=+0.101, Q4=+0.129, Q5_high_vol=+0.177

**`combo_mean__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0829, Sharpe=+0.2652)
- Admission: Train IC=+0.1661, Deflated=+0.1662, IR=0.61, Mono=0.72, p=0.0012, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.090 | 2017: +0.193 | 2018: +0.172 | 2019: +0.140 | 2020: +0.121 | 2021: +0.094 | 2022: +0.078 | 2023: +0.032 | 2024: +0.113 | 2025: +0.135 | 2026: +0.025
- Yearly Tail ICs:   2015: +0.369 | 2016: -0.029 | 2017: +0.117 | 2018: +0.185 | 2019: +0.322 | 2020: +0.036 | 2021: +0.313 | 2022: +0.148 | 2023: +0.158 | 2024: +0.290 | 2025: +0.176 | 2026: +0.035
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=0.62, Recency ratio=0.40
- Early IC=+0.1824, Recent IC=+0.0727, 1st-half IC=+0.1378, 2nd-half IC=+0.0855, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.158, Q2=-0.020, Q3_mid=+0.132, Q4=+0.148, Q5_high_vol=+0.143

**`combo_sig_product__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1138, Sharpe=+0.2628)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.42, Mono=0.67, p=0.0002, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.064 | 2017: +0.196 | 2018: +0.105 | 2019: +0.176 | 2020: +0.076 | 2021: +0.087 | 2022: +0.089 | 2023: +0.057 | 2024: +0.164 | 2025: +0.058 | 2026: +0.181
- Yearly Tail ICs:   2015: +0.201 | 2016: -0.078 | 2017: +0.194 | 2018: +0.319 | 2019: +0.255 | 2020: +0.061 | 2021: +0.195 | 2022: +0.202 | 2023: -0.020 | 2024: +0.075 | 2025: -0.152 | 2026: +0.171
- IC CV=0.41, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.74
- Early IC=+0.1505, Recent IC=+0.1107, 1st-half IC=+0.1298, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.066, Q3_mid=+0.094, Q4=+0.137, Q5_high_vol=+0.151

**`combo_mean__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0707, Sharpe=+0.2615)
- Admission: Train IC=+0.1755, Deflated=+0.1750, IR=0.65, Mono=0.74, p=0.0004, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.056 | 2017: +0.244 | 2018: +0.188 | 2019: +0.133 | 2020: +0.163 | 2021: +0.115 | 2022: +0.080 | 2023: +0.083 | 2024: +0.134 | 2025: +0.111 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.413 | 2016: -0.042 | 2017: +0.110 | 2018: +0.128 | 2019: +0.303 | 2020: +0.011 | 2021: +0.362 | 2022: +0.239 | 2023: +0.126 | 2024: +0.235 | 2025: +0.099 | 2026: +0.011
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.50
- Early IC=+0.2160, Recent IC=+0.1087, 1st-half IC=+0.1642, 2nd-half IC=+0.1105, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.229, Q2=+0.006, Q3_mid=+0.147, Q4=+0.140, Q5_high_vol=+0.168

**`combo_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0418, Sharpe=+0.2392)
- Admission: Train IC=+0.2281, Deflated=+0.2271, IR=0.97, Mono=0.81, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.105 | 2017: +0.198 | 2018: +0.221 | 2019: +0.150 | 2020: +0.159 | 2021: +0.140 | 2022: +0.066 | 2023: +0.102 | 2024: +0.127 | 2025: +0.021 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.214 | 2017: +0.417 | 2018: +0.376 | 2019: +0.327 | 2020: +0.122 | 2021: +0.258 | 2022: +0.158 | 2023: +0.198 | 2024: +0.027 | 2025: -0.043 | 2026: +0.030
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.55
- Early IC=+0.2092, Recent IC=+0.1145, 1st-half IC=+0.1725, 2nd-half IC=+0.1087, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.005, Q3_mid=+0.101, Q4=+0.150, Q5_high_vol=+0.223

**`combo_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0727, Sharpe=+0.2061)
- Admission: Train IC=+0.1831, Deflated=+0.1834, IR=0.69, Mono=0.76, p=0.0002, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.275 | 2016: +0.101 | 2017: +0.183 | 2018: +0.164 | 2019: +0.130 | 2020: +0.105 | 2021: +0.083 | 2022: +0.033 | 2023: +0.063 | 2024: +0.101 | 2025: +0.138 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.341 | 2016: -0.074 | 2017: +0.314 | 2018: +0.162 | 2019: +0.319 | 2020: +0.205 | 2021: +0.430 | 2022: +0.131 | 2023: +0.085 | 2024: +0.258 | 2025: +0.186 | 2026: -0.010
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.47
- Early IC=+0.1733, Recent IC=+0.0819, 1st-half IC=+0.1317, 2nd-half IC=+0.0714, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.001, Q3_mid=+0.096, Q4=+0.124, Q5_high_vol=+0.123

**`combo_min__first_bar_return__max_down_ret`** (Lock IC=+0.0728, Sharpe=+0.2061)
- Admission: Train IC=+0.1828, Deflated=+0.1830, IR=0.69, Mono=0.76, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.101 | 2017: +0.182 | 2018: +0.164 | 2019: +0.130 | 2020: +0.105 | 2021: +0.082 | 2022: +0.034 | 2023: +0.063 | 2024: +0.101 | 2025: +0.138 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.341 | 2016: -0.074 | 2017: +0.315 | 2018: +0.162 | 2019: +0.319 | 2020: +0.200 | 2021: +0.430 | 2022: +0.134 | 2023: +0.085 | 2024: +0.260 | 2025: +0.188 | 2026: -0.008
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=0.54, Recency ratio=0.47
- Early IC=+0.1733, Recent IC=+0.0821, 1st-half IC=+0.1316, 2nd-half IC=+0.0714, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.001, Q3_mid=+0.095, Q4=+0.124, Q5_high_vol=+0.123

**`combo_mean__first_bar_return__max_down_ret`** (Lock IC=+0.0745, Sharpe=+0.2028)
- Admission: Train IC=+0.2194, Deflated=+0.2195, IR=0.72, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.104 | 2017: +0.226 | 2018: +0.203 | 2019: +0.133 | 2020: +0.121 | 2021: +0.084 | 2022: +0.072 | 2023: +0.053 | 2024: +0.127 | 2025: +0.132 | 2026: +0.012
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.041 | 2017: +0.263 | 2018: +0.390 | 2019: +0.184 | 2020: +0.181 | 2021: +0.280 | 2022: +0.190 | 2023: +0.134 | 2024: +0.251 | 2025: +0.165 | 2026: -0.251
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.59, Recency ratio=0.42
- Early IC=+0.2146, Recent IC=+0.0903, 1st-half IC=+0.1515, 2nd-half IC=+0.0896, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.010, Q3_mid=+0.115, Q4=+0.135, Q5_high_vol=+0.158

**`combo_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0843, Sharpe=+0.1933)
- Admission: Train IC=+0.1848, Deflated=+0.1842, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.038 | 2017: +0.223 | 2018: +0.173 | 2019: +0.122 | 2020: +0.153 | 2021: +0.120 | 2022: +0.077 | 2023: +0.080 | 2024: +0.123 | 2025: +0.119 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.393 | 2016: -0.073 | 2017: +0.217 | 2018: +0.134 | 2019: +0.353 | 2020: +0.082 | 2021: +0.357 | 2022: +0.185 | 2023: +0.099 | 2024: +0.272 | 2025: +0.191 | 2026: +0.066
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=0.67, Recency ratio=0.51
- Early IC=+0.1979, Recent IC=+0.1013, 1st-half IC=+0.1547, 2nd-half IC=+0.1038, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.004, Q3_mid=+0.152, Q4=+0.149, Q5_high_vol=+0.148

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0970, Sharpe=+0.1808)
- Admission: Train IC=+0.1833, Deflated=+0.1822, IR=0.65, Mono=0.72, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.305 | 2016: +0.036 | 2017: +0.233 | 2018: +0.100 | 2019: +0.110 | 2020: +0.116 | 2021: +0.047 | 2022: +0.058 | 2023: +0.046 | 2024: +0.103 | 2025: +0.097 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.307 | 2016: +0.162 | 2017: +0.189 | 2018: +0.226 | 2019: +0.360 | 2020: +0.204 | 2021: +0.175 | 2022: +0.096 | 2023: +0.021 | 2024: +0.249 | 2025: +0.008 | 2026: +0.179
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.56, Recency ratio=0.45
- Early IC=+0.1665, Recent IC=+0.0746, 1st-half IC=+0.1201, 2nd-half IC=+0.0674, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.001, Q3_mid=+0.092, Q4=+0.116, Q5_high_vol=+0.108

**`combo_sig_product__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0553, Sharpe=+0.1769)
- Admission: Train IC=+0.1523, Deflated=+0.1495, IR=0.57, Mono=0.68, p=0.0030, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.145 | 2017: +0.140 | 2018: +0.130 | 2019: +0.110 | 2020: +0.099 | 2021: +0.100 | 2022: +0.123 | 2023: +0.055 | 2024: +0.145 | 2025: +0.062 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.276 | 2016: +0.094 | 2017: +0.396 | 2018: +0.245 | 2019: +0.274 | 2020: +0.221 | 2021: +0.190 | 2022: -0.155 | 2023: +0.105 | 2024: +0.144 | 2025: +0.011 | 2026: +0.177
- IC CV=0.24, Neg years (linear/tail)=0/1 of 8, Half ratio=1.01, Recency ratio=0.74
- Early IC=+0.1350, Recent IC=+0.1000, 1st-half IC=+0.1101, 2nd-half IC=+0.1113, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.047, Q3_mid=+0.062, Q4=+0.079, Q5_high_vol=+0.168

**`combo_sig_product__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1335, Sharpe=+0.1748)
- Admission: Train IC=+0.1662, Deflated=+0.1640, IR=0.52, Mono=0.68, p=0.0012, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.138 | 2016: -0.089 | 2017: +0.171 | 2018: -0.002 | 2019: +0.109 | 2020: +0.088 | 2021: +0.112 | 2022: +0.042 | 2023: +0.097 | 2024: +0.216 | 2025: +0.100 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.268 | 2016: -0.147 | 2017: +0.310 | 2018: +0.022 | 2019: +0.130 | 2020: +0.100 | 2021: +0.170 | 2022: -0.165 | 2023: +0.181 | 2024: +0.406 | 2025: -0.094 | 2026: +0.226
- IC CV=0.61, Neg years (linear/tail)=1/1 of 8, Half ratio=1.41, Recency ratio=1.86
- Early IC=+0.0841, Recent IC=+0.1561, 1st-half IC=+0.0875, 2nd-half IC=+0.1237, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.036, Q3_mid=+0.079, Q4=+0.118, Q5_high_vol=+0.144

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0550, Sharpe=+0.1707)
- Admission: Train IC=+0.2150, Deflated=+0.2149, IR=0.77, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.234 | 2018: +0.163 | 2019: +0.358 | 2020: +0.068 | 2021: +0.297 | 2022: +0.084 | 2023: +0.183 | 2024: +0.402 | 2025: +0.178 | 2026: -0.048
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=0.61, Recency ratio=0.50
- Early IC=+0.2290, Recent IC=+0.1140, 1st-half IC=+0.1742, 2nd-half IC=+0.1071, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.223, Q2=-0.006, Q3_mid=+0.159, Q4=+0.126, Q5_high_vol=+0.200

**`combo_rank_min__first_bar_return__max_down_ret`** (Lock IC=+0.0630, Sharpe=+0.1498)
- Admission: Train IC=+0.1811, Deflated=+0.1815, IR=0.64, Mono=0.72, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.098 | 2017: +0.201 | 2018: +0.164 | 2019: +0.130 | 2020: +0.098 | 2021: +0.071 | 2022: +0.027 | 2023: +0.056 | 2024: +0.103 | 2025: +0.123 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.344 | 2016: -0.075 | 2017: +0.320 | 2018: +0.225 | 2019: +0.326 | 2020: +0.179 | 2021: +0.349 | 2022: +0.131 | 2023: +0.073 | 2024: +0.220 | 2025: +0.160 | 2026: -0.097
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.52, Recency ratio=0.44
- Early IC=+0.1802, Recent IC=+0.0802, 1st-half IC=+0.1314, 2nd-half IC=+0.0683, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.009, Q3_mid=+0.104, Q4=+0.124, Q5_high_vol=+0.116

**`combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1371, Sharpe=+0.1462)
- Admission: Train IC=+0.1707, Deflated=+0.1690, IR=0.52, Mono=0.68, p=0.0006, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.195 | 2016: -0.009 | 2017: +0.128 | 2018: +0.102 | 2019: +0.171 | 2020: +0.058 | 2021: +0.119 | 2022: +0.027 | 2023: +0.046 | 2024: +0.167 | 2025: +0.095 | 2026: +0.206
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.008 | 2017: +0.213 | 2018: +0.153 | 2019: +0.357 | 2020: +0.002 | 2021: +0.382 | 2022: +0.080 | 2023: +0.082 | 2024: +0.123 | 2025: -0.037 | 2026: +0.325
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.93
- Early IC=+0.1152, Recent IC=+0.1066, 1st-half IC=+0.1132, 2nd-half IC=+0.0920, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.017, Q3_mid=+0.084, Q4=+0.123, Q5_high_vol=+0.156

**`max_down_ret`** (Lock IC=+0.0790, Sharpe=+0.1275)
- Admission: Train IC=+0.1510, Deflated=+0.1514, IR=0.58, Mono=0.71, p=0.0032, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.052 | 2017: +0.240 | 2018: +0.131 | 2019: +0.112 | 2020: +0.138 | 2021: +0.064 | 2022: +0.057 | 2023: +0.031 | 2024: +0.115 | 2025: +0.129 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.013 | 2017: +0.236 | 2018: +0.099 | 2019: +0.326 | 2020: +0.060 | 2021: +0.325 | 2022: +0.141 | 2023: +0.096 | 2024: +0.230 | 2025: +0.240 | 2026: +0.035
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.39
- Early IC=+0.1854, Recent IC=+0.0729, 1st-half IC=+0.1326, 2nd-half IC=+0.0736, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.006, Q3_mid=+0.136, Q4=+0.121, Q5_high_vol=+0.113

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.1006, Sharpe=+0.1239)
- Admission: Train IC=+0.2069, Deflated=+0.2053, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.126 | 2017: +0.186 | 2018: +0.102 | 2019: +0.056 | 2020: +0.103 | 2021: +0.001 | 2022: +0.096 | 2023: +0.050 | 2024: +0.076 | 2025: +0.117 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.139 | 2017: +0.335 | 2018: +0.251 | 2019: +0.115 | 2020: +0.206 | 2021: +0.122 | 2022: +0.186 | 2023: +0.052 | 2024: +0.242 | 2025: +0.093 | 2026: +0.239
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=0.58, Recency ratio=0.44
- Early IC=+0.1437, Recent IC=+0.0630, 1st-half IC=+0.1028, 2nd-half IC=+0.0600, Neg regimes=1/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.164, Q2=-0.005, Q3_mid=+0.086, Q4=+0.084, Q5_high_vol=+0.106

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0291, Sharpe=+0.0988)
- Admission: Train IC=+0.1772, Deflated=+0.1773, IR=0.44, Mono=0.69, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.141 | 2017: +0.075 | 2018: +0.165 | 2019: +0.094 | 2020: +0.135 | 2021: +0.076 | 2022: +0.096 | 2023: +0.080 | 2024: +0.096 | 2025: +0.077 | 2026: -0.021
- Yearly Tail ICs:   2015: +0.391 | 2016: +0.074 | 2017: +0.080 | 2018: +0.212 | 2019: +0.185 | 2020: +0.212 | 2021: +0.005 | 2022: +0.171 | 2023: +0.264 | 2024: +0.114 | 2025: +0.086 | 2026: -0.079
- IC CV=0.29, Neg years (linear/tail)=0/0 of 8, Half ratio=0.81, Recency ratio=0.73
- Early IC=+0.1198, Recent IC=+0.0881, 1st-half IC=+0.1130, 2nd-half IC=+0.0914, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.004, Q3_mid=+0.109, Q4=+0.141, Q5_high_vol=+0.145

**`combo_rank_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0531, Sharpe=+0.0725)
- Admission: Train IC=+0.1985, Deflated=+0.1984, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.148 | 2017: +0.146 | 2018: +0.232 | 2019: +0.124 | 2020: +0.121 | 2021: +0.095 | 2022: +0.065 | 2023: +0.058 | 2024: +0.102 | 2025: +0.125 | 2026: -0.026
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.202 | 2017: +0.372 | 2018: +0.527 | 2019: +0.070 | 2020: +0.250 | 2021: +0.008 | 2022: +0.268 | 2023: -0.001 | 2024: +0.153 | 2025: +0.160 | 2026: -0.223
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=0.54, Recency ratio=0.42
- Early IC=+0.1892, Recent IC=+0.0797, 1st-half IC=+0.1465, 2nd-half IC=+0.0792, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.119, Q2=-0.020, Q3_mid=+0.103, Q4=+0.139, Q5_high_vol=+0.178

**`combo_rank_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0805, Sharpe=+0.0712)
- Admission: Train IC=+0.1686, Deflated=+0.1682, IR=0.58, Mono=0.71, p=0.0008, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.048 | 2017: +0.223 | 2018: +0.166 | 2019: +0.110 | 2020: +0.147 | 2021: +0.099 | 2022: +0.078 | 2023: +0.080 | 2024: +0.120 | 2025: +0.121 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.050 | 2017: +0.153 | 2018: +0.091 | 2019: +0.327 | 2020: +0.059 | 2021: +0.353 | 2022: +0.208 | 2023: +0.072 | 2024: +0.188 | 2025: +0.122 | 2026: -0.052
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=0.66, Recency ratio=0.49
- Early IC=+0.1943, Recent IC=+0.0961, 1st-half IC=+0.1446, 2nd-half IC=+0.0957, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.206, Q2=+0.006, Q3_mid=+0.136, Q4=+0.146, Q5_high_vol=+0.126

**`combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0569, Sharpe=+0.0506)
- Admission: Train IC=+0.2175, Deflated=+0.2171, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.043 | 2017: +0.160 | 2018: +0.232 | 2019: +0.181 | 2020: +0.179 | 2021: +0.155 | 2022: +0.044 | 2023: +0.094 | 2024: +0.144 | 2025: +0.074 | 2026: +0.037
- Yearly Tail ICs:   2015: +0.388 | 2016: -0.004 | 2017: +0.279 | 2018: +0.361 | 2019: +0.296 | 2020: -0.007 | 2021: +0.353 | 2022: +0.136 | 2023: +0.172 | 2024: +0.176 | 2025: +0.158 | 2026: +0.069
- IC CV=0.36, Neg years (linear/tail)=0/1 of 8, Half ratio=0.65, Recency ratio=0.61
- Early IC=+0.1962, Recent IC=+0.1190, 1st-half IC=+0.1775, 2nd-half IC=+0.1158, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.005, Q3_mid=+0.136, Q4=+0.132, Q5_high_vol=+0.231

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0435, Sharpe=+0.0483)
- Admission: Train IC=+0.1737, Deflated=+0.1729, IR=0.63, Mono=0.75, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.150 | 2017: +0.182 | 2018: +0.240 | 2019: +0.135 | 2020: +0.137 | 2021: +0.083 | 2022: +0.102 | 2023: +0.072 | 2024: +0.083 | 2025: +0.097 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.302 | 2017: +0.378 | 2018: +0.505 | 2019: +0.129 | 2020: +0.123 | 2021: +0.004 | 2022: +0.124 | 2023: +0.117 | 2024: +0.064 | 2025: -0.049 | 2026: -0.277
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=0.55, Recency ratio=0.37
- Early IC=+0.2109, Recent IC=+0.0778, 1st-half IC=+0.1601, 2nd-half IC=+0.0880, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.148, Q2=-0.019, Q3_mid=+0.091, Q4=+0.159, Q5_high_vol=+0.197

**`combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence`** (Lock IC=+0.0533, Sharpe=+0.0477)
- Admission: Train IC=+0.1343, Deflated=+0.1330, IR=0.41, Mono=0.66, p=0.0078, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.182 | 2016: +0.004 | 2017: +0.168 | 2018: +0.118 | 2019: +0.075 | 2020: +0.144 | 2021: +0.068 | 2022: +0.096 | 2023: +0.134 | 2024: +0.069 | 2025: +0.048 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.029 | 2017: +0.385 | 2018: +0.038 | 2019: +0.133 | 2020: +0.209 | 2021: +0.020 | 2022: -0.011 | 2023: +0.321 | 2024: +0.068 | 2025: -0.045 | 2026: +0.305
- IC CV=0.33, Neg years (linear/tail)=0/1 of 8, Half ratio=0.83, Recency ratio=0.71
- Early IC=+0.1427, Recent IC=+0.1014, 1st-half IC=+0.1185, 2nd-half IC=+0.0979, Neg regimes=1/5
- Weak component: `early_late_momentum_divergence` (CV=0.53)
- Regime ICs: Q1_low_vol=+0.204, Q2=-0.045, Q3_mid=+0.157, Q4=+0.076, Q5_high_vol=+0.139

**`combo_sig_product__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0630, Sharpe=+0.0335)
- Admission: Train IC=+0.1649, Deflated=+0.1635, IR=0.44, Mono=0.66, p=0.0014, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.191 | 2016: -0.023 | 2017: +0.200 | 2018: +0.105 | 2019: +0.079 | 2020: +0.163 | 2021: +0.080 | 2022: +0.080 | 2023: +0.124 | 2024: +0.079 | 2025: +0.076 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.347 | 2016: +0.051 | 2017: +0.408 | 2018: +0.073 | 2019: +0.108 | 2020: +0.184 | 2021: +0.087 | 2022: -0.015 | 2023: +0.219 | 2024: +0.109 | 2025: -0.091 | 2026: +0.377
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=0.75, Recency ratio=0.67
- Early IC=+0.1524, Recent IC=+0.1020, 1st-half IC=+0.1300, 2nd-half IC=+0.0970, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.219, Q2=-0.049, Q3_mid=+0.151, Q4=+0.096, Q5_high_vol=+0.140

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0419, Sharpe=+0.0059)
- Admission: Train IC=+0.2578, Deflated=+0.2567, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.305 | 2016: +0.100 | 2017: +0.198 | 2018: +0.218 | 2019: +0.148 | 2020: +0.161 | 2021: +0.137 | 2022: +0.068 | 2023: +0.104 | 2024: +0.136 | 2025: +0.021 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.166 | 2017: +0.435 | 2018: +0.350 | 2019: +0.299 | 2020: +0.078 | 2021: +0.209 | 2022: +0.235 | 2023: +0.210 | 2024: +0.342 | 2025: +0.073 | 2026: +0.012
- IC CV=0.31, Neg years (linear/tail)=0/0 of 8, Half ratio=0.63, Recency ratio=0.58
- Early IC=+0.2078, Recent IC=+0.1201, 1st-half IC=+0.1721, 2nd-half IC=+0.1092, Neg regimes=1/5
- Weak component: `body_size_progression` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.209, Q2=-0.008, Q3_mid=+0.103, Q4=+0.152, Q5_high_vol=+0.228

### 159915ETF — `single` True Positives

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1243, Sharpe=+2.0348)
- Admission: Train IC=+0.3122, Deflated=+0.3118, IR=0.98, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.124 | 2017: -0.001 | 2018: +0.125 | 2019: +0.213 | 2020: +0.067 | 2021: +0.189 | 2022: +0.060 | 2023: +0.148 | 2024: +0.120 | 2025: +0.140 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.030 | 2016: +0.063 | 2017: +0.103 | 2018: +0.280 | 2019: +0.527 | 2020: +0.305 | 2021: +0.389 | 2022: +0.110 | 2023: +0.381 | 2024: +0.281 | 2025: +0.148 | 2026: +0.325
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.32, Recency ratio=2.19
- Early IC=+0.0604, Recent IC=+0.1324, 1st-half IC=+0.1037, 2nd-half IC=+0.1366, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.124, Q3_mid=+0.101, Q4=+0.111, Q5_high_vol=+0.205

**`combo_min__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1307, Sharpe=+1.7816)
- Admission: Train IC=+0.3282, Deflated=+0.3282, IR=1.09, Mono=0.87, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.074 | 2017: -0.006 | 2018: +0.097 | 2019: +0.227 | 2020: +0.043 | 2021: +0.155 | 2022: +0.034 | 2023: +0.154 | 2024: +0.136 | 2025: +0.131 | 2026: +0.130
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.038 | 2017: +0.123 | 2018: +0.286 | 2019: +0.586 | 2020: +0.294 | 2021: +0.346 | 2022: +0.266 | 2023: +0.366 | 2024: +0.304 | 2025: +0.145 | 2026: +0.355
- IC CV=0.69, Neg years (linear/tail)=1/0 of 8, Half ratio=1.41, Recency ratio=3.20
- Early IC=+0.0453, Recent IC=+0.1451, 1st-half IC=+0.0912, 2nd-half IC=+0.1285, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.106, Q3_mid=+0.112, Q4=+0.100, Q5_high_vol=+0.171

**`combo_rank_min__limit_down_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1471, Sharpe=+1.7038)
- Admission: Train IC=+0.2498, Deflated=+0.2501, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.016 | 2017: -0.006 | 2018: +0.068 | 2019: +0.223 | 2020: +0.017 | 2021: +0.124 | 2022: +0.019 | 2023: +0.147 | 2024: +0.110 | 2025: +0.131 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.232 | 2016: -0.077 | 2017: +0.116 | 2018: +0.247 | 2019: +0.595 | 2020: +0.129 | 2021: +0.347 | 2022: +0.200 | 2023: +0.316 | 2024: +0.237 | 2025: +0.141 | 2026: +0.375
- IC CV=0.83, Neg years (linear/tail)=1/0 of 8, Half ratio=1.48, Recency ratio=4.47
- Early IC=+0.0279, Recent IC=+0.1246, 1st-half IC=+0.0718, 2nd-half IC=+0.1065, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.085, Q3_mid=+0.109, Q4=+0.082, Q5_high_vol=+0.108

**`combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1316, Sharpe=+1.5377)
- Admission: Train IC=+0.2653, Deflated=+0.2632, IR=0.68, Mono=0.73, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.057 | 2017: +0.035 | 2018: +0.105 | 2019: +0.108 | 2020: +0.061 | 2021: +0.170 | 2022: +0.135 | 2023: +0.149 | 2024: +0.106 | 2025: +0.181 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.197 | 2017: +0.104 | 2018: +0.336 | 2019: +0.277 | 2020: +0.206 | 2021: +0.333 | 2022: +0.141 | 2023: +0.132 | 2024: +0.339 | 2025: +0.308 | 2026: +0.229
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=2.02, Recency ratio=1.82
- Early IC=+0.0700, Recent IC=+0.1274, 1st-half IC=+0.0729, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.089, Q3_mid=+0.090, Q4=+0.125, Q5_high_vol=+0.163

**`combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.1527, Sharpe=+1.5226)
- Admission: Train IC=+0.2931, Deflated=+0.2931, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.203 | 2016: -0.012 | 2017: -0.014 | 2018: +0.077 | 2019: +0.224 | 2020: +0.104 | 2021: +0.111 | 2022: +0.092 | 2023: +0.164 | 2024: +0.067 | 2025: +0.174 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.210 | 2016: -0.107 | 2017: +0.066 | 2018: +0.349 | 2019: +0.484 | 2020: +0.155 | 2021: +0.309 | 2022: +0.301 | 2023: +0.392 | 2024: +0.284 | 2025: +0.131 | 2026: +0.337
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=3.62
- Early IC=+0.0310, Recent IC=+0.1125, 1st-half IC=+0.0963, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.077, Q3_mid=+0.132, Q4=+0.105, Q5_high_vol=+0.117

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1527, Sharpe=+1.5226)
- Admission: Train IC=+0.2931, Deflated=+0.2931, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.203 | 2016: -0.012 | 2017: -0.014 | 2018: +0.077 | 2019: +0.224 | 2020: +0.104 | 2021: +0.111 | 2022: +0.092 | 2023: +0.164 | 2024: +0.067 | 2025: +0.174 | 2026: +0.116
- Yearly Tail ICs:   2015: +0.210 | 2016: -0.107 | 2017: +0.066 | 2018: +0.349 | 2019: +0.484 | 2020: +0.155 | 2021: +0.309 | 2022: +0.301 | 2023: +0.392 | 2024: +0.284 | 2025: +0.131 | 2026: +0.337
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=3.62
- Early IC=+0.0310, Recent IC=+0.1125, 1st-half IC=+0.0963, 2nd-half IC=+0.1112, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.131, Q2=+0.077, Q3_mid=+0.132, Q4=+0.105, Q5_high_vol=+0.117

**`combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1361, Sharpe=+1.5184)
- Admission: Train IC=+0.3147, Deflated=+0.3142, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.123 | 2017: -0.021 | 2018: +0.149 | 2019: +0.236 | 2020: +0.163 | 2021: +0.125 | 2022: +0.103 | 2023: +0.121 | 2024: +0.099 | 2025: +0.146 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.129 | 2017: +0.106 | 2018: +0.331 | 2019: +0.410 | 2020: +0.273 | 2021: +0.272 | 2022: +0.203 | 2023: +0.182 | 2024: +0.471 | 2025: +0.266 | 2026: +0.178
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=0.92, Recency ratio=1.72
- Early IC=+0.0639, Recent IC=+0.1099, 1st-half IC=+0.1307, 2nd-half IC=+0.1207, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.095, Q3_mid=+0.081, Q4=+0.127, Q5_high_vol=+0.189

**`combo_rank_min__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0759, Sharpe=+1.4912)
- Admission: Train IC=+0.1483, Deflated=+0.1490, IR=0.54, Mono=0.71, p=0.0040, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.201 | 2017: -0.006 | 2018: +0.122 | 2019: +0.156 | 2020: +0.158 | 2021: +0.097 | 2022: +0.078 | 2023: +0.110 | 2024: +0.058 | 2025: +0.111 | 2026: +0.045
- Yearly Tail ICs:   2015: -0.200 | 2016: +0.304 | 2017: +0.136 | 2018: +0.040 | 2019: +0.108 | 2020: +0.213 | 2021: -0.013 | 2022: +0.277 | 2023: +0.333 | 2024: +0.020 | 2025: +0.375 | 2026: -0.269
- IC CV=0.53, Neg years (linear/tail)=1/1 of 8, Half ratio=0.91, Recency ratio=1.45
- Early IC=+0.0576, Recent IC=+0.0837, 1st-half IC=+0.1011, 2nd-half IC=+0.0920, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.080, Q3_mid=+0.056, Q4=+0.063, Q5_high_vol=+0.156

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1346, Sharpe=+1.4890)
- Admission: Train IC=+0.3215, Deflated=+0.3208, IR=0.89, Mono=0.79, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.115 | 2017: +0.001 | 2018: +0.162 | 2019: +0.239 | 2020: +0.149 | 2021: +0.149 | 2022: +0.103 | 2023: +0.158 | 2024: +0.106 | 2025: +0.167 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.154 | 2016: +0.030 | 2017: +0.026 | 2018: +0.306 | 2019: +0.526 | 2020: +0.281 | 2021: +0.251 | 2022: +0.185 | 2023: +0.414 | 2024: +0.503 | 2025: +0.286 | 2026: +0.029
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.62
- Early IC=+0.0815, Recent IC=+0.1321, 1st-half IC=+0.1313, 2nd-half IC=+0.1358, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.089, Q3_mid=+0.107, Q4=+0.133, Q5_high_vol=+0.193

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1491, Sharpe=+1.4472)
- Admission: Train IC=+0.2433, Deflated=+0.2432, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.112 | 2017: +0.020 | 2018: +0.091 | 2019: +0.236 | 2020: +0.119 | 2021: +0.123 | 2022: +0.093 | 2023: +0.164 | 2024: +0.068 | 2025: +0.215 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.026 | 2017: +0.037 | 2018: +0.218 | 2019: +0.458 | 2020: +0.239 | 2021: +0.253 | 2022: +0.137 | 2023: +0.345 | 2024: +0.303 | 2025: +0.428 | 2026: +0.234
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=2.08
- Early IC=+0.0557, Recent IC=+0.1160, 1st-half IC=+0.1118, 2nd-half IC=+0.1205, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.111, Q3_mid=+0.108, Q4=+0.090, Q5_high_vol=+0.140

**`combo_min__limit_down_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1345, Sharpe=+1.4216)
- Admission: Train IC=+0.2796, Deflated=+0.2799, IR=0.86, Mono=0.81, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.028 | 2017: -0.006 | 2018: +0.076 | 2019: +0.222 | 2020: +0.013 | 2021: +0.132 | 2022: +0.010 | 2023: +0.146 | 2024: +0.116 | 2025: +0.124 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.225 | 2016: -0.071 | 2017: +0.112 | 2018: +0.298 | 2019: +0.599 | 2020: +0.182 | 2021: +0.322 | 2022: +0.231 | 2023: +0.297 | 2024: +0.281 | 2025: +0.104 | 2026: +0.483
- IC CV=0.84, Neg years (linear/tail)=1/0 of 8, Half ratio=1.47, Recency ratio=3.76
- Early IC=+0.0349, Recent IC=+0.1313, 1st-half IC=+0.0745, 2nd-half IC=+0.1098, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.109, Q2=+0.085, Q3_mid=+0.115, Q4=+0.084, Q5_high_vol=+0.115

**`combo_mean__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1432, Sharpe=+1.3853)
- Admission: Train IC=+0.3057, Deflated=+0.3049, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.117 | 2017: -0.022 | 2018: +0.162 | 2019: +0.228 | 2020: +0.155 | 2021: +0.144 | 2022: +0.108 | 2023: +0.117 | 2024: +0.080 | 2025: +0.142 | 2026: +0.137
- Yearly Tail ICs:   2015: +0.040 | 2016: +0.148 | 2017: +0.106 | 2018: +0.382 | 2019: +0.447 | 2020: +0.242 | 2021: +0.293 | 2022: +0.170 | 2023: +0.121 | 2024: +0.432 | 2025: +0.229 | 2026: +0.178
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=0.92, Recency ratio=1.41
- Early IC=+0.0699, Recent IC=+0.0985, 1st-half IC=+0.1309, 2nd-half IC=+0.1211, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.090, Q3_mid=+0.074, Q4=+0.135, Q5_high_vol=+0.198

**`combo_mean__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.1160, Sharpe=+1.3698)
- Admission: Train IC=+0.2422, Deflated=+0.2410, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.089 | 2017: -0.021 | 2018: +0.133 | 2019: +0.234 | 2020: +0.171 | 2021: +0.125 | 2022: +0.100 | 2023: +0.074 | 2024: +0.083 | 2025: +0.108 | 2026: +0.138
- Yearly Tail ICs:   2015: +0.014 | 2016: +0.184 | 2017: +0.160 | 2018: +0.284 | 2019: +0.342 | 2020: +0.188 | 2021: +0.144 | 2022: +0.247 | 2023: +0.043 | 2024: +0.265 | 2025: +0.156 | 2026: +0.347
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=0.78, Recency ratio=1.40
- Early IC=+0.0563, Recent IC=+0.0789, 1st-half IC=+0.1376, 2nd-half IC=+0.1071, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.096, Q3_mid=+0.075, Q4=+0.135, Q5_high_vol=+0.179

**`combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1382, Sharpe=+1.3500)
- Admission: Train IC=+0.2435, Deflated=+0.2431, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.071 | 2017: -0.002 | 2018: +0.159 | 2019: +0.207 | 2020: +0.121 | 2021: +0.137 | 2022: +0.096 | 2023: +0.136 | 2024: +0.066 | 2025: +0.154 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.049 | 2017: +0.130 | 2018: +0.339 | 2019: +0.410 | 2020: +0.080 | 2021: +0.369 | 2022: +0.109 | 2023: +0.164 | 2024: +0.380 | 2025: +0.224 | 2026: +0.269
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=0.90, Recency ratio=1.28
- Early IC=+0.0784, Recent IC=+0.1006, 1st-half IC=+0.1259, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.089, Q3_mid=+0.063, Q4=+0.113, Q5_high_vol=+0.189

**`combo_mean__bar_ret_0__limit_down_proximity_early`** (Lock IC=+0.1382, Sharpe=+1.3500)
- Admission: Train IC=+0.2434, Deflated=+0.2430, IR=0.61, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.071 | 2017: -0.002 | 2018: +0.159 | 2019: +0.207 | 2020: +0.121 | 2021: +0.137 | 2022: +0.095 | 2023: +0.135 | 2024: +0.066 | 2025: +0.154 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.046 | 2017: +0.130 | 2018: +0.339 | 2019: +0.412 | 2020: +0.080 | 2021: +0.368 | 2022: +0.106 | 2023: +0.164 | 2024: +0.384 | 2025: +0.224 | 2026: +0.269
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=0.90, Recency ratio=1.28
- Early IC=+0.0784, Recent IC=+0.1006, 1st-half IC=+0.1259, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.089, Q3_mid=+0.063, Q4=+0.114, Q5_high_vol=+0.188

**`combo_min__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=+0.0441, Sharpe=+1.1853)
- Admission: Train IC=+0.2231, Deflated=+0.2230, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.012 | 2017: +0.036 | 2018: +0.058 | 2019: +0.130 | 2020: +0.066 | 2021: +0.159 | 2022: +0.131 | 2023: +0.173 | 2024: +0.084 | 2025: +0.134 | 2026: -0.084
- Yearly Tail ICs:   2015: +0.356 | 2016: -0.299 | 2017: +0.059 | 2018: +0.211 | 2019: +0.348 | 2020: +0.248 | 2021: +0.214 | 2022: +0.187 | 2023: +0.336 | 2024: +0.096 | 2025: +0.234 | 2026: +0.041
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=2.23, Recency ratio=2.72
- Early IC=+0.0472, Recent IC=+0.1284, 1st-half IC=+0.0628, 2nd-half IC=+0.1400, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.057, Q3_mid=+0.141, Q4=+0.081, Q5_high_vol=+0.113

**`combo_min__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.1426, Sharpe=+1.1691)
- Admission: Train IC=+0.2774, Deflated=+0.2769, IR=0.79, Mono=0.79, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.006 | 2017: -0.001 | 2018: +0.093 | 2019: +0.229 | 2020: +0.098 | 2021: +0.121 | 2022: +0.077 | 2023: +0.169 | 2024: +0.098 | 2025: +0.169 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.227 | 2016: -0.063 | 2017: +0.024 | 2018: +0.385 | 2019: +0.505 | 2020: +0.182 | 2021: +0.275 | 2022: +0.167 | 2023: +0.391 | 2024: +0.284 | 2025: +0.167 | 2026: +0.522
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.16, Recency ratio=2.90
- Early IC=+0.0461, Recent IC=+0.1337, 1st-half IC=+0.1048, 2nd-half IC=+0.1218, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.080, Q3_mid=+0.152, Q4=+0.117, Q5_high_vol=+0.123

**`combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1277, Sharpe=+1.1407)
- Admission: Train IC=+0.3360, Deflated=+0.3352, IR=1.05, Mono=0.83, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.092 | 2017: -0.005 | 2018: +0.166 | 2019: +0.223 | 2020: +0.135 | 2021: +0.148 | 2022: +0.127 | 2023: +0.186 | 2024: +0.081 | 2025: +0.182 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.022 | 2017: +0.048 | 2018: +0.386 | 2019: +0.452 | 2020: +0.337 | 2021: +0.367 | 2022: +0.294 | 2023: +0.467 | 2024: +0.301 | 2025: +0.195 | 2026: +0.190
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.07, Recency ratio=1.68
- Early IC=+0.0789, Recent IC=+0.1327, 1st-half IC=+0.1338, 2nd-half IC=+0.1438, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.116, Q2=+0.138, Q3_mid=+0.123, Q4=+0.139, Q5_high_vol=+0.199

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1295, Sharpe=+1.1328)
- Admission: Train IC=+0.2696, Deflated=+0.2694, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.130 | 2017: +0.016 | 2018: +0.094 | 2019: +0.242 | 2020: +0.153 | 2021: +0.130 | 2022: +0.102 | 2023: +0.141 | 2024: +0.104 | 2025: +0.190 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.202 | 2017: +0.138 | 2018: +0.146 | 2019: +0.599 | 2020: +0.351 | 2021: +0.205 | 2022: +0.248 | 2023: +0.364 | 2024: +0.224 | 2025: +0.367 | 2026: +0.195
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=2.24
- Early IC=+0.0547, Recent IC=+0.1224, 1st-half IC=+0.1258, 2nd-half IC=+0.1275, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.136, Q2=+0.097, Q3_mid=+0.110, Q4=+0.126, Q5_high_vol=+0.166

**`combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1203, Sharpe=+1.1190)
- Admission: Train IC=+0.3406, Deflated=+0.3405, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.099 | 2017: -0.034 | 2018: +0.128 | 2019: +0.267 | 2020: +0.154 | 2021: +0.134 | 2022: +0.052 | 2023: +0.128 | 2024: +0.115 | 2025: +0.122 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.188 | 2016: +0.166 | 2017: +0.048 | 2018: +0.393 | 2019: +0.503 | 2020: +0.413 | 2021: +0.365 | 2022: +0.209 | 2023: +0.313 | 2024: +0.432 | 2025: +0.164 | 2026: +0.410
- IC CV=0.68, Neg years (linear/tail)=1/0 of 8, Half ratio=0.88, Recency ratio=2.56
- Early IC=+0.0473, Recent IC=+0.1211, 1st-half IC=+0.1330, 2nd-half IC=+0.1165, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.097, Q3_mid=+0.073, Q4=+0.124, Q5_high_vol=+0.199

**`combo_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1434, Sharpe=+1.1190)
- Admission: Train IC=+0.3403, Deflated=+0.3403, IR=0.96, Mono=0.83, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.086 | 2017: -0.029 | 2018: +0.115 | 2019: +0.268 | 2020: +0.157 | 2021: +0.122 | 2022: +0.061 | 2023: +0.146 | 2024: +0.111 | 2025: +0.155 | 2026: +0.130
- Yearly Tail ICs:   2015: +0.161 | 2016: +0.185 | 2017: +0.048 | 2018: +0.379 | 2019: +0.506 | 2020: +0.391 | 2021: +0.353 | 2022: +0.220 | 2023: +0.311 | 2024: +0.452 | 2025: +0.189 | 2026: +0.383
- IC CV=0.66, Neg years (linear/tail)=1/0 of 8, Half ratio=0.91, Recency ratio=2.99
- Early IC=+0.0429, Recent IC=+0.1284, 1st-half IC=+0.1315, 2nd-half IC=+0.1200, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.106, Q3_mid=+0.088, Q4=+0.113, Q5_high_vol=+0.190

**`combo_rank_min__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1617, Sharpe=+1.1078)
- Admission: Train IC=+0.2468, Deflated=+0.2472, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.040 | 2017: -0.056 | 2018: +0.095 | 2019: +0.245 | 2020: +0.122 | 2021: +0.099 | 2022: +0.056 | 2023: +0.135 | 2024: +0.095 | 2025: +0.167 | 2026: +0.139
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.021 | 2017: -0.034 | 2018: +0.385 | 2019: +0.534 | 2020: +0.249 | 2021: +0.283 | 2022: +0.154 | 2023: +0.234 | 2024: +0.339 | 2025: +0.287 | 2026: +0.349
- IC CV=0.79, Neg years (linear/tail)=1/1 of 8, Half ratio=1.08, Recency ratio=6.23
- Early IC=+0.0184, Recent IC=+0.1147, 1st-half IC=+0.0949, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.088, Q3_mid=+0.077, Q4=+0.090, Q5_high_vol=+0.131

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.1617, Sharpe=+1.1078)
- Admission: Train IC=+0.2468, Deflated=+0.2472, IR=0.72, Mono=0.78, p=0.0000, MaxCorr=1.00
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

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+1.0456)
- Admission: Train IC=+0.2890, Deflated=+0.2872, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.143 | 2017: +0.023 | 2018: +0.124 | 2019: +0.198 | 2020: +0.163 | 2021: +0.160 | 2022: +0.117 | 2023: +0.158 | 2024: +0.094 | 2025: +0.170 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.051 | 2016: +0.275 | 2017: +0.036 | 2018: +0.381 | 2019: +0.375 | 2020: +0.235 | 2021: +0.366 | 2022: +0.273 | 2023: +0.196 | 2024: +0.353 | 2025: +0.152 | 2026: +0.278
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.10, Recency ratio=1.71
- Early IC=+0.0736, Recent IC=+0.1260, 1st-half IC=+0.1315, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.108, Q2=+0.112, Q3_mid=+0.111, Q4=+0.137, Q5_high_vol=+0.196

**`combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1258, Sharpe=+1.0333)
- Admission: Train IC=+0.3197, Deflated=+0.3193, IR=1.03, Mono=0.84, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.152 | 2016: +0.126 | 2017: +0.006 | 2018: +0.127 | 2019: +0.227 | 2020: +0.059 | 2021: +0.178 | 2022: +0.044 | 2023: +0.149 | 2024: +0.126 | 2025: +0.143 | 2026: +0.112
- Yearly Tail ICs:   2015: -0.006 | 2016: +0.023 | 2017: +0.116 | 2018: +0.216 | 2019: +0.629 | 2020: +0.300 | 2021: +0.345 | 2022: +0.180 | 2023: +0.384 | 2024: +0.256 | 2025: +0.209 | 2026: +0.265
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=2.06
- Early IC=+0.0667, Recent IC=+0.1374, 1st-half IC=+0.1060, 2nd-half IC=+0.1322, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.083, Q2=+0.124, Q3_mid=+0.106, Q4=+0.114, Q5_high_vol=+0.196

**`combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1310, Sharpe=+1.0164)
- Admission: Train IC=+0.2854, Deflated=+0.2851, IR=0.79, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.130 | 2017: -0.009 | 2018: +0.180 | 2019: +0.223 | 2020: +0.148 | 2021: +0.151 | 2022: +0.099 | 2023: +0.145 | 2024: +0.084 | 2025: +0.161 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.041 | 2017: +0.189 | 2018: +0.293 | 2019: +0.389 | 2020: +0.197 | 2021: +0.393 | 2022: +0.143 | 2023: +0.198 | 2024: +0.351 | 2025: +0.251 | 2026: +0.170
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=0.95, Recency ratio=1.34
- Early IC=+0.0856, Recent IC=+0.1146, 1st-half IC=+0.1328, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.097, Q3_mid=+0.076, Q4=+0.119, Q5_high_vol=+0.203

**`combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0985, Sharpe=+1.0115)
- Admission: Train IC=+0.3304, Deflated=+0.3302, IR=1.21, Mono=0.87, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.128 | 2017: -0.015 | 2018: +0.195 | 2019: +0.218 | 2020: +0.175 | 2021: +0.139 | 2022: +0.093 | 2023: +0.145 | 2024: +0.103 | 2025: +0.133 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.115 | 2016: +0.109 | 2017: +0.111 | 2018: +0.364 | 2019: +0.526 | 2020: +0.297 | 2021: +0.345 | 2022: +0.400 | 2023: +0.404 | 2024: +0.322 | 2025: +0.291 | 2026: +0.156
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=0.88, Recency ratio=1.39
- Early IC=+0.0896, Recent IC=+0.1242, 1st-half IC=+0.1454, 2nd-half IC=+0.1275, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.116, Q3_mid=+0.090, Q4=+0.149, Q5_high_vol=+0.201

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1337, Sharpe=+0.9648)
- Admission: Train IC=+0.2967, Deflated=+0.2960, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.159 | 2017: -0.017 | 2018: +0.158 | 2019: +0.231 | 2020: +0.183 | 2021: +0.135 | 2022: +0.109 | 2023: +0.126 | 2024: +0.091 | 2025: +0.152 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.050 | 2016: +0.187 | 2017: +0.025 | 2018: +0.332 | 2019: +0.413 | 2020: +0.323 | 2021: +0.314 | 2022: +0.226 | 2023: +0.236 | 2024: +0.462 | 2025: +0.232 | 2026: +0.168
- IC CV=0.54, Neg years (linear/tail)=1/0 of 8, Half ratio=0.88, Recency ratio=1.53
- Early IC=+0.0708, Recent IC=+0.1083, 1st-half IC=+0.1395, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.104, Q3_mid=+0.080, Q4=+0.131, Q5_high_vol=+0.204

**`combo_mean__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1394, Sharpe=+0.9587)
- Admission: Train IC=+0.2407, Deflated=+0.2389, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.173 | 2016: +0.109 | 2017: -0.072 | 2018: +0.110 | 2019: +0.111 | 2020: +0.091 | 2021: +0.047 | 2022: +0.170 | 2023: +0.132 | 2024: +0.102 | 2025: +0.108 | 2026: +0.169
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.159 | 2017: +0.163 | 2018: +0.369 | 2019: +0.325 | 2020: +0.352 | 2021: +0.218 | 2022: +0.384 | 2023: +0.075 | 2024: +0.117 | 2025: +0.184 | 2026: +0.312
- IC CV=0.79, Neg years (linear/tail)=1/0 of 8, Half ratio=1.44, Recency ratio=6.15
- Early IC=+0.0190, Recent IC=+0.1171, 1st-half IC=+0.0781, 2nd-half IC=+0.1122, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.015, Q2=+0.134, Q3_mid=+0.046, Q4=+0.135, Q5_high_vol=+0.150

**`combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return`** (Lock IC=+0.1197, Sharpe=+0.9323)
- Admission: Train IC=+0.2378, Deflated=+0.2380, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.138 | 2016: +0.083 | 2017: -0.054 | 2018: +0.112 | 2019: +0.113 | 2020: +0.135 | 2021: +0.037 | 2022: +0.178 | 2023: +0.123 | 2024: +0.050 | 2025: +0.096 | 2026: +0.149
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.237 | 2017: +0.018 | 2018: +0.408 | 2019: +0.228 | 2020: +0.405 | 2021: +0.133 | 2022: +0.395 | 2023: +0.107 | 2024: +0.062 | 2025: +0.176 | 2026: +0.214
- IC CV=0.78, Neg years (linear/tail)=1/0 of 8, Half ratio=1.01, Recency ratio=3.02
- Early IC=+0.0288, Recent IC=+0.0869, 1st-half IC=+0.0887, 2nd-half IC=+0.0894, Neg regimes=0/5
- Weak component: `yesterday_early_momentum` (CV=1.24)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.151, Q3_mid=+0.052, Q4=+0.115, Q5_high_vol=+0.171

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1428, Sharpe=+0.8973)
- Admission: Train IC=+0.2881, Deflated=+0.2871, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.157 | 2017: -0.015 | 2018: +0.175 | 2019: +0.223 | 2020: +0.182 | 2021: +0.158 | 2022: +0.116 | 2023: +0.122 | 2024: +0.081 | 2025: +0.156 | 2026: +0.123
- Yearly Tail ICs:   2015: -0.038 | 2016: +0.188 | 2017: +0.025 | 2018: +0.362 | 2019: +0.438 | 2020: +0.276 | 2021: +0.318 | 2022: +0.195 | 2023: +0.211 | 2024: +0.430 | 2025: +0.180 | 2026: +0.168
- IC CV=0.53, Neg years (linear/tail)=1/0 of 8, Half ratio=0.89, Recency ratio=1.27
- Early IC=+0.0802, Recent IC=+0.1016, 1st-half IC=+0.1435, 2nd-half IC=+0.1277, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.103, Q3_mid=+0.078, Q4=+0.145, Q5_high_vol=+0.221

**`combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1319, Sharpe=+0.8890)
- Admission: Train IC=+0.2533, Deflated=+0.2532, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.116 | 2017: +0.052 | 2018: +0.141 | 2019: +0.216 | 2020: +0.104 | 2021: +0.210 | 2022: +0.071 | 2023: +0.121 | 2024: +0.107 | 2025: +0.162 | 2026: +0.102
- Yearly Tail ICs:   2015: -0.124 | 2016: +0.121 | 2017: +0.194 | 2018: +0.202 | 2019: +0.566 | 2020: +0.083 | 2021: +0.372 | 2022: +0.121 | 2023: +0.269 | 2024: +0.317 | 2025: +0.143 | 2026: +0.127
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=1.18
- Early IC=+0.0968, Recent IC=+0.1142, 1st-half IC=+0.1329, 2nd-half IC=+0.1343, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.104, Q2=+0.099, Q3_mid=+0.111, Q4=+0.160, Q5_high_vol=+0.198

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1152, Sharpe=+0.8863)
- Admission: Train IC=+0.3342, Deflated=+0.3337, IR=0.89, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.134 | 2017: -0.023 | 2018: +0.164 | 2019: +0.259 | 2020: +0.181 | 2021: +0.147 | 2022: +0.065 | 2023: +0.131 | 2024: +0.101 | 2025: +0.128 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.115 | 2016: +0.154 | 2017: +0.020 | 2018: +0.375 | 2019: +0.557 | 2020: +0.407 | 2021: +0.303 | 2022: +0.157 | 2023: +0.330 | 2024: +0.417 | 2025: +0.225 | 2026: +0.232
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=0.81, Recency ratio=1.65
- Early IC=+0.0703, Recent IC=+0.1162, 1st-half IC=+0.1507, 2nd-half IC=+0.1220, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.106, Q3_mid=+0.067, Q4=+0.143, Q5_high_vol=+0.223

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1342, Sharpe=+0.8852)
- Admission: Train IC=+0.2926, Deflated=+0.2914, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.123 | 2017: +0.009 | 2018: +0.185 | 2019: +0.200 | 2020: +0.148 | 2021: +0.174 | 2022: +0.129 | 2023: +0.138 | 2024: +0.072 | 2025: +0.163 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.124 | 2017: +0.112 | 2018: +0.408 | 2019: +0.382 | 2020: +0.221 | 2021: +0.446 | 2022: +0.149 | 2023: +0.174 | 2024: +0.394 | 2025: +0.176 | 2026: +0.145
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=0.99, Recency ratio=1.08
- Early IC=+0.0971, Recent IC=+0.1046, 1st-half IC=+0.1374, 2nd-half IC=+0.1367, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.119, Q3_mid=+0.077, Q4=+0.139, Q5_high_vol=+0.216

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1344, Sharpe=+0.8852)
- Admission: Train IC=+0.2925, Deflated=+0.2914, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.123 | 2017: +0.009 | 2018: +0.185 | 2019: +0.200 | 2020: +0.148 | 2021: +0.174 | 2022: +0.129 | 2023: +0.138 | 2024: +0.072 | 2025: +0.163 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.124 | 2017: +0.112 | 2018: +0.408 | 2019: +0.383 | 2020: +0.221 | 2021: +0.448 | 2022: +0.155 | 2023: +0.174 | 2024: +0.396 | 2025: +0.178 | 2026: +0.145
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.00, Recency ratio=1.08
- Early IC=+0.0971, Recent IC=+0.1048, 1st-half IC=+0.1373, 2nd-half IC=+0.1369, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.120, Q3_mid=+0.077, Q4=+0.139, Q5_high_vol=+0.216

**`combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return`** (Lock IC=+0.0906, Sharpe=+0.8830)
- Admission: Train IC=+0.2160, Deflated=+0.2168, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.142 | 2017: +0.010 | 2018: +0.142 | 2019: +0.207 | 2020: +0.126 | 2021: +0.144 | 2022: +0.069 | 2023: +0.161 | 2024: +0.064 | 2025: +0.154 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.390 | 2016: -0.080 | 2017: +0.071 | 2018: +0.274 | 2019: +0.431 | 2020: +0.069 | 2021: +0.280 | 2022: +0.036 | 2023: +0.363 | 2024: +0.255 | 2025: +0.401 | 2026: +0.073
- IC CV=0.51, Neg years (linear/tail)=0/0 of 8, Half ratio=1.01, Recency ratio=1.49
- Early IC=+0.0755, Recent IC=+0.1126, 1st-half IC=+0.1145, 2nd-half IC=+0.1152, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.163, Q2=+0.096, Q3_mid=+0.089, Q4=+0.080, Q5_high_vol=+0.163

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1533, Sharpe=+0.8711)
- Admission: Train IC=+0.2780, Deflated=+0.2763, IR=0.94, Mono=0.83, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.084 | 2017: -0.001 | 2018: +0.087 | 2019: +0.137 | 2020: +0.093 | 2021: +0.173 | 2022: +0.130 | 2023: +0.166 | 2024: +0.073 | 2025: +0.210 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.259 | 2017: +0.166 | 2018: +0.244 | 2019: +0.215 | 2020: +0.192 | 2021: +0.244 | 2022: +0.306 | 2023: +0.335 | 2024: +0.343 | 2025: +0.288 | 2026: +0.105
- IC CV=0.50, Neg years (linear/tail)=1/0 of 8, Half ratio=1.77, Recency ratio=2.85
- Early IC=+0.0424, Recent IC=+0.1209, 1st-half IC=+0.0818, 2nd-half IC=+0.1451, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.111, Q2=+0.133, Q3_mid=+0.085, Q4=+0.101, Q5_high_vol=+0.163

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1289, Sharpe=+0.8597)
- Admission: Train IC=+0.2864, Deflated=+0.2852, IR=0.80, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.151 | 2017: +0.006 | 2018: +0.159 | 2019: +0.210 | 2020: +0.165 | 2021: +0.174 | 2022: +0.127 | 2023: +0.140 | 2024: +0.068 | 2025: +0.180 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.033 | 2016: +0.202 | 2017: +0.058 | 2018: +0.304 | 2019: +0.342 | 2020: +0.238 | 2021: +0.348 | 2022: +0.265 | 2023: +0.287 | 2024: +0.397 | 2025: +0.228 | 2026: -0.061
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.06, Recency ratio=1.26
- Early IC=+0.0827, Recent IC=+0.1039, 1st-half IC=+0.1291, 2nd-half IC=+0.1368, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.107, Q3_mid=+0.094, Q4=+0.133, Q5_high_vol=+0.191

**`combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1368, Sharpe=+0.8496)
- Admission: Train IC=+0.3480, Deflated=+0.3476, IR=0.98, Mono=0.82, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.105 | 2017: -0.006 | 2018: +0.125 | 2019: +0.242 | 2020: +0.149 | 2021: +0.113 | 2022: +0.065 | 2023: +0.162 | 2024: +0.118 | 2025: +0.154 | 2026: +0.120
- Yearly Tail ICs:   2015: +0.169 | 2016: +0.202 | 2017: +0.038 | 2018: +0.423 | 2019: +0.498 | 2020: +0.401 | 2021: +0.302 | 2022: +0.240 | 2023: +0.379 | 2024: +0.460 | 2025: +0.167 | 2026: +0.327
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=0.99, Recency ratio=2.35
- Early IC=+0.0596, Recent IC=+0.1399, 1st-half IC=+0.1252, 2nd-half IC=+0.1241, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.094, Q3_mid=+0.091, Q4=+0.113, Q5_high_vol=+0.196

**`combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1497, Sharpe=+0.8445)
- Admission: Train IC=+0.2769, Deflated=+0.2751, IR=0.90, Mono=0.84, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.073 | 2017: -0.002 | 2018: +0.076 | 2019: +0.157 | 2020: +0.087 | 2021: +0.183 | 2022: +0.118 | 2023: +0.148 | 2024: +0.084 | 2025: +0.207 | 2026: +0.059
- Yearly Tail ICs:   2015: +0.080 | 2016: +0.205 | 2017: +0.158 | 2018: +0.182 | 2019: +0.344 | 2020: +0.248 | 2021: +0.237 | 2022: +0.277 | 2023: +0.319 | 2024: +0.382 | 2025: +0.301 | 2026: +0.105
- IC CV=0.51, Neg years (linear/tail)=1/0 of 8, Half ratio=1.80, Recency ratio=3.12
- Early IC=+0.0372, Recent IC=+0.1160, 1st-half IC=+0.0791, 2nd-half IC=+0.1428, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.126, Q3_mid=+0.089, Q4=+0.113, Q5_high_vol=+0.151

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1419, Sharpe=+0.8351)
- Admission: Train IC=+0.3040, Deflated=+0.3035, IR=0.84, Mono=0.78, p=0.0000, MaxCorr=0.92
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

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1466, Sharpe=+0.8182)
- Admission: Train IC=+0.2913, Deflated=+0.2898, IR=0.99, Mono=0.81, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.041 | 2017: -0.004 | 2018: +0.048 | 2019: +0.159 | 2020: +0.084 | 2021: +0.169 | 2022: +0.100 | 2023: +0.148 | 2024: +0.085 | 2025: +0.189 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.241 | 2017: +0.166 | 2018: +0.231 | 2019: +0.320 | 2020: +0.253 | 2021: +0.313 | 2022: +0.263 | 2023: +0.326 | 2024: +0.380 | 2025: +0.219 | 2026: +0.171
- IC CV=0.56, Neg years (linear/tail)=1/0 of 8, Half ratio=1.86, Recency ratio=5.29
- Early IC=+0.0220, Recent IC=+0.1164, 1st-half IC=+0.0721, 2nd-half IC=+0.1338, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.104, Q3_mid=+0.089, Q4=+0.101, Q5_high_vol=+0.130

**`combo_max__first_bar_return__impulse_bar_dominance`** (Lock IC=+0.0681, Sharpe=+0.8101)
- Admission: Train IC=+0.1516, Deflated=+0.1517, IR=0.46, Mono=0.67, p=0.0036, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.158 | 2016: +0.071 | 2017: +0.026 | 2018: +0.080 | 2019: +0.057 | 2020: +0.100 | 2021: +0.161 | 2022: +0.075 | 2023: +0.153 | 2024: +0.065 | 2025: +0.151 | 2026: -0.049
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.050 | 2017: +0.090 | 2018: +0.247 | 2019: +0.116 | 2020: +0.130 | 2021: +0.315 | 2022: +0.100 | 2023: +0.296 | 2024: +0.074 | 2025: +0.401 | 2026: -0.381
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.87, Recency ratio=2.06
- Early IC=+0.0530, Recent IC=+0.1089, 1st-half IC=+0.0614, 2nd-half IC=+0.1148, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.042, Q3_mid=+0.094, Q4=+0.064, Q5_high_vol=+0.136

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1325, Sharpe=+0.7977)
- Admission: Train IC=+0.2636, Deflated=+0.2619, IR=0.95, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.131 | 2017: +0.009 | 2018: +0.116 | 2019: +0.207 | 2020: +0.160 | 2021: +0.158 | 2022: +0.128 | 2023: +0.164 | 2024: +0.081 | 2025: +0.174 | 2026: +0.069
- Yearly Tail ICs:   2015: +0.124 | 2016: +0.177 | 2017: +0.053 | 2018: +0.295 | 2019: +0.445 | 2020: +0.180 | 2021: +0.368 | 2022: +0.285 | 2023: +0.268 | 2024: +0.296 | 2025: +0.125 | 2026: +0.032
- IC CV=0.44, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.98
- Early IC=+0.0624, Recent IC=+0.1232, 1st-half IC=+0.1271, 2nd-half IC=+0.1435, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.126, Q3_mid=+0.107, Q4=+0.134, Q5_high_vol=+0.198

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1135, Sharpe=+0.7682)
- Admission: Train IC=+0.2885, Deflated=+0.2871, IR=0.94, Mono=0.80, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.074 | 2017: +0.031 | 2018: +0.130 | 2019: +0.196 | 2020: +0.124 | 2021: +0.157 | 2022: +0.130 | 2023: +0.164 | 2024: +0.116 | 2025: +0.178 | 2026: +0.031
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.132 | 2017: +0.091 | 2018: +0.225 | 2019: +0.533 | 2020: +0.127 | 2021: +0.272 | 2022: +0.322 | 2023: +0.436 | 2024: +0.349 | 2025: +0.154 | 2026: +0.022
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.26, Recency ratio=1.74
- Early IC=+0.0805, Recent IC=+0.1398, 1st-half IC=+0.1165, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.099, Q3_mid=+0.114, Q4=+0.130, Q5_high_vol=+0.185

**`combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1250, Sharpe=+0.7559)
- Admission: Train IC=+0.3317, Deflated=+0.3317, IR=1.04, Mono=0.84, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.062 | 2017: -0.013 | 2018: +0.141 | 2019: +0.238 | 2020: +0.131 | 2021: +0.127 | 2022: +0.106 | 2023: +0.177 | 2024: +0.118 | 2025: +0.164 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.293 | 2016: +0.061 | 2017: +0.014 | 2018: +0.369 | 2019: +0.498 | 2020: +0.210 | 2021: +0.279 | 2022: +0.295 | 2023: +0.452 | 2024: +0.371 | 2025: +0.128 | 2026: +0.206
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.10, Recency ratio=2.31
- Early IC=+0.0639, Recent IC=+0.1478, 1st-half IC=+0.1248, 2nd-half IC=+0.1373, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.110, Q3_mid=+0.118, Q4=+0.127, Q5_high_vol=+0.185

**`combo_ratio__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0659, Sharpe=+0.7397)
- Admission: Train IC=+0.1602, Deflated=+0.1611, IR=0.50, Mono=0.73, p=0.0022, MaxCorr=0.83
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

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1269, Sharpe=+0.7270)
- Admission: Train IC=+0.2399, Deflated=+0.2387, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.137 | 2017: +0.043 | 2018: +0.089 | 2019: +0.186 | 2020: +0.133 | 2021: +0.162 | 2022: +0.122 | 2023: +0.164 | 2024: +0.046 | 2025: +0.179 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.282 | 2017: +0.145 | 2018: +0.376 | 2019: +0.305 | 2020: +0.146 | 2021: +0.446 | 2022: +0.212 | 2023: +0.346 | 2024: +0.209 | 2025: +0.246 | 2026: +0.076
- IC CV=0.43, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=1.59
- Early IC=+0.0659, Recent IC=+0.1051, 1st-half IC=+0.1123, 2nd-half IC=+0.1332, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.133, Q3_mid=+0.105, Q4=+0.103, Q5_high_vol=+0.123

**`combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1315, Sharpe=+0.7247)
- Admission: Train IC=+0.2915, Deflated=+0.2905, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.084 | 2017: +0.005 | 2018: +0.110 | 2019: +0.226 | 2020: +0.127 | 2021: +0.113 | 2022: +0.077 | 2023: +0.143 | 2024: +0.101 | 2025: +0.160 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.177 | 2016: +0.088 | 2017: +0.027 | 2018: +0.334 | 2019: +0.475 | 2020: +0.210 | 2021: +0.264 | 2022: +0.288 | 2023: +0.255 | 2024: +0.394 | 2025: +0.068 | 2026: +0.177
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=2.12
- Early IC=+0.0574, Recent IC=+0.1218, 1st-half IC=+0.1125, 2nd-half IC=+0.1155, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.079, Q3_mid=+0.092, Q4=+0.103, Q5_high_vol=+0.186

**`combo_mean__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0739, Sharpe=+0.7136)
- Admission: Train IC=+0.1783, Deflated=+0.1799, IR=0.43, Mono=0.66, p=0.0010, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.125 | 2017: +0.053 | 2018: +0.088 | 2019: +0.199 | 2020: +0.065 | 2021: +0.177 | 2022: +0.039 | 2023: +0.150 | 2024: +0.063 | 2025: +0.135 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.062 | 2016: -0.117 | 2017: +0.179 | 2018: +0.200 | 2019: +0.297 | 2020: +0.099 | 2021: +0.342 | 2022: +0.055 | 2023: +0.324 | 2024: +0.062 | 2025: +0.290 | 2026: +0.018
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.51
- Early IC=+0.0709, Recent IC=+0.1067, 1st-half IC=+0.0940, 2nd-half IC=+0.1150, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.077, Q3_mid=+0.114, Q4=+0.095, Q5_high_vol=+0.127

**`combo_ratio__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1308, Sharpe=+0.7043)
- Admission: Train IC=+0.1819, Deflated=+0.1803, IR=0.46, Mono=0.68, p=0.0004, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.009 | 2017: -0.012 | 2018: +0.072 | 2019: +0.170 | 2020: +0.085 | 2021: +0.112 | 2022: +0.141 | 2023: +0.103 | 2024: +0.117 | 2025: +0.125 | 2026: +0.147
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.030 | 2017: +0.155 | 2018: +0.235 | 2019: +0.268 | 2020: +0.153 | 2021: +0.188 | 2022: +0.076 | 2023: +0.066 | 2024: +0.234 | 2025: +0.025 | 2026: +0.202
- IC CV=0.52, Neg years (linear/tail)=1/0 of 8, Half ratio=1.38, Recency ratio=3.68
- Early IC=+0.0299, Recent IC=+0.1100, 1st-half IC=+0.0914, 2nd-half IC=+0.1259, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.085, Q2=+0.131, Q3_mid=+0.066, Q4=+0.120, Q5_high_vol=+0.153

**`first_bar_return`** (Lock IC=+0.0748, Sharpe=+0.7040)
- Admission: Train IC=+0.1526, Deflated=+0.1535, IR=0.54, Mono=0.71, p=0.0034, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.162 | 2017: +0.017 | 2018: +0.137 | 2019: +0.192 | 2020: +0.116 | 2021: +0.135 | 2022: +0.073 | 2023: +0.144 | 2024: +0.061 | 2025: +0.123 | 2026: +0.023
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.95, Recency ratio=1.34
- Early IC=+0.0766, Recent IC=+0.1025, 1st-half IC=+0.1124, 2nd-half IC=+0.1066, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.084, Q3_mid=+0.077, Q4=+0.075, Q5_high_vol=+0.154

**`combo_sig_product__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0733, Sharpe=+0.7040)
- Admission: Train IC=+0.1526, Deflated=+0.1536, IR=0.54, Mono=0.71, p=0.0034, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.157 | 2017: +0.019 | 2018: +0.138 | 2019: +0.193 | 2020: +0.115 | 2021: +0.133 | 2022: +0.072 | 2023: +0.143 | 2024: +0.060 | 2025: +0.120 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.212 | 2016: +0.026 | 2017: +0.218 | 2018: +0.219 | 2019: +0.181 | 2020: +0.014 | 2021: +0.292 | 2022: +0.172 | 2023: +0.298 | 2024: +0.059 | 2025: +0.264 | 2026: +0.083
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.93, Recency ratio=1.29
- Early IC=+0.0786, Recent IC=+0.1015, 1st-half IC=+0.1137, 2nd-half IC=+0.1055, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.086, Q3_mid=+0.078, Q4=+0.075, Q5_high_vol=+0.153

**`combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.1060, Sharpe=+0.6973)
- Admission: Train IC=+0.1539, Deflated=+0.1533, IR=0.63, Mono=0.71, p=0.0032, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.149 | 2017: -0.018 | 2018: +0.115 | 2019: +0.238 | 2020: +0.171 | 2021: +0.075 | 2022: +0.082 | 2023: +0.094 | 2024: +0.062 | 2025: +0.117 | 2026: +0.094
- Yearly Tail ICs:   2015: -0.031 | 2016: +0.335 | 2017: +0.111 | 2018: -0.012 | 2019: +0.495 | 2020: +0.181 | 2021: -0.167 | 2022: +0.351 | 2023: +0.241 | 2024: +0.294 | 2025: +0.088 | 2026: +0.250
- IC CV=0.70, Neg years (linear/tail)=1/2 of 8, Half ratio=0.69, Recency ratio=1.59
- Early IC=+0.0489, Recent IC=+0.0779, 1st-half IC=+0.1320, 2nd-half IC=+0.0913, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.109, Q3_mid=+0.062, Q4=+0.108, Q5_high_vol=+0.158

**`combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early`** (Lock IC=+0.1428, Sharpe=+0.6972)
- Admission: Train IC=+0.1916, Deflated=+0.1896, IR=0.58, Mono=0.71, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.038 | 2017: -0.003 | 2018: +0.098 | 2019: +0.181 | 2020: +0.120 | 2021: +0.143 | 2022: +0.150 | 2023: +0.108 | 2024: +0.090 | 2025: +0.161 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.138 | 2017: +0.068 | 2018: +0.192 | 2019: +0.334 | 2020: +0.162 | 2021: +0.248 | 2022: +0.108 | 2023: +0.106 | 2024: +0.018 | 2025: +0.421 | 2026: +0.241
- IC CV=0.46, Neg years (linear/tail)=1/0 of 8, Half ratio=1.20, Recency ratio=2.09
- Early IC=+0.0473, Recent IC=+0.0988, 1st-half IC=+0.1106, 2nd-half IC=+0.1328, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.081, Q2=+0.121, Q3_mid=+0.097, Q4=+0.116, Q5_high_vol=+0.189

**`combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.1108, Sharpe=+0.6963)
- Admission: Train IC=+0.2017, Deflated=+0.2023, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.071 | 2017: +0.002 | 2018: +0.075 | 2019: +0.167 | 2020: +0.052 | 2021: +0.117 | 2022: +0.080 | 2023: +0.183 | 2024: +0.083 | 2025: +0.173 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.199 | 2016: -0.043 | 2017: +0.069 | 2018: +0.337 | 2019: +0.321 | 2020: +0.189 | 2021: -0.005 | 2022: +0.192 | 2023: +0.389 | 2024: +0.171 | 2025: +0.240 | 2026: -0.049
- IC CV=0.58, Neg years (linear/tail)=0/0 of 8, Half ratio=2.06, Recency ratio=3.49
- Early IC=+0.0378, Recent IC=+0.1319, 1st-half IC=+0.0593, 2nd-half IC=+0.1220, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.082, Q3_mid=+0.070, Q4=+0.048, Q5_high_vol=+0.111

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1356, Sharpe=+0.6928)
- Admission: Train IC=+0.2920, Deflated=+0.2917, IR=0.73, Mono=0.74, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.073 | 2017: -0.020 | 2018: +0.100 | 2019: +0.254 | 2020: +0.122 | 2021: +0.109 | 2022: +0.080 | 2023: +0.148 | 2024: +0.090 | 2025: +0.155 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.072 | 2017: +0.019 | 2018: +0.277 | 2019: +0.481 | 2020: +0.204 | 2021: +0.300 | 2022: +0.244 | 2023: +0.203 | 2024: +0.379 | 2025: +0.089 | 2026: +0.270
- IC CV=0.63, Neg years (linear/tail)=1/0 of 8, Half ratio=0.98, Recency ratio=2.98
- Early IC=+0.0399, Recent IC=+0.1191, 1st-half IC=+0.1170, 2nd-half IC=+0.1147, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.107, Q3_mid=+0.065, Q4=+0.100, Q5_high_vol=+0.182

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return`** (Lock IC=+0.1232, Sharpe=+0.6752)
- Admission: Train IC=+0.2870, Deflated=+0.2861, IR=0.84, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.101 | 2017: +0.016 | 2018: +0.160 | 2019: +0.225 | 2020: +0.141 | 2021: +0.134 | 2022: +0.086 | 2023: +0.158 | 2024: +0.088 | 2025: +0.161 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.174 | 2016: +0.074 | 2017: +0.017 | 2018: +0.341 | 2019: +0.487 | 2020: +0.178 | 2021: +0.242 | 2022: +0.275 | 2023: +0.284 | 2024: +0.383 | 2025: +0.137 | 2026: +0.173
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=0.94, Recency ratio=1.40
- Early IC=+0.0881, Recent IC=+0.1230, 1st-half IC=+0.1320, 2nd-half IC=+0.1245, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.127, Q2=+0.095, Q3_mid=+0.089, Q4=+0.115, Q5_high_vol=+0.216

**`combo_max__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0775, Sharpe=+0.6742)
- Admission: Train IC=+0.1618, Deflated=+0.1631, IR=0.50, Mono=0.68, p=0.0018, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.157 | 2017: +0.012 | 2018: +0.144 | 2019: +0.198 | 2020: +0.119 | 2021: +0.130 | 2022: +0.059 | 2023: +0.141 | 2024: +0.060 | 2025: +0.139 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.186 | 2016: +0.103 | 2017: +0.128 | 2018: +0.237 | 2019: +0.198 | 2020: +0.087 | 2021: +0.206 | 2022: +0.220 | 2023: +0.315 | 2024: +0.108 | 2025: +0.448 | 2026: -0.340
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=0.85, Recency ratio=1.28
- Early IC=+0.0783, Recent IC=+0.1004, 1st-half IC=+0.1184, 2nd-half IC=+0.1004, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.087, Q3_mid=+0.085, Q4=+0.072, Q5_high_vol=+0.145

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1275, Sharpe=+0.6725)
- Admission: Train IC=+0.3408, Deflated=+0.3403, IR=0.93, Mono=0.81, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.123 | 2017: +0.001 | 2018: +0.170 | 2019: +0.241 | 2020: +0.166 | 2021: +0.138 | 2022: +0.077 | 2023: +0.175 | 2024: +0.104 | 2025: +0.157 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.102 | 2016: +0.152 | 2017: -0.004 | 2018: +0.410 | 2019: +0.545 | 2020: +0.395 | 2021: +0.268 | 2022: +0.208 | 2023: +0.443 | 2024: +0.442 | 2025: +0.245 | 2026: +0.175
- IC CV=0.51, Neg years (linear/tail)=0/1 of 8, Half ratio=0.93, Recency ratio=1.63
- Early IC=+0.0855, Recent IC=+0.1395, 1st-half IC=+0.1427, 2nd-half IC=+0.1324, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.133, Q2=+0.108, Q3_mid=+0.088, Q4=+0.129, Q5_high_vol=+0.224

**`combo_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0617, Sharpe=+0.6479)
- Admission: Train IC=+0.1591, Deflated=+0.1596, IR=0.48, Mono=0.69, p=0.0022, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.176 | 2017: -0.003 | 2018: +0.112 | 2019: +0.187 | 2020: +0.106 | 2021: +0.135 | 2022: +0.068 | 2023: +0.111 | 2024: +0.065 | 2025: +0.103 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.411 | 2016: -0.071 | 2017: +0.176 | 2018: +0.191 | 2019: +0.242 | 2020: -0.071 | 2021: +0.264 | 2022: +0.103 | 2023: +0.285 | 2024: -0.004 | 2025: +0.213 | 2026: +0.170
- IC CV=0.54, Neg years (linear/tail)=1/2 of 8, Half ratio=1.07, Recency ratio=1.61
- Early IC=+0.0544, Recent IC=+0.0878, 1st-half IC=+0.0954, 2nd-half IC=+0.1019, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.075, Q3_mid=+0.056, Q4=+0.068, Q5_high_vol=+0.151

**`combo_min__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1386, Sharpe=+0.6223)
- Admission: Train IC=+0.2465, Deflated=+0.2453, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.003 | 2017: +0.011 | 2018: +0.030 | 2019: +0.154 | 2020: +0.061 | 2021: +0.144 | 2022: +0.075 | 2023: +0.133 | 2024: +0.066 | 2025: +0.164 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.219 | 2016: -0.005 | 2017: +0.118 | 2018: +0.246 | 2019: +0.307 | 2020: +0.172 | 2021: +0.198 | 2022: +0.161 | 2023: +0.312 | 2024: +0.342 | 2025: +0.135 | 2026: +0.227
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=4.91
- Early IC=+0.0202, Recent IC=+0.0992, 1st-half IC=+0.0593, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.073, Q3_mid=+0.088, Q4=+0.081, Q5_high_vol=+0.092

**`combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1386, Sharpe=+0.6223)
- Admission: Train IC=+0.2465, Deflated=+0.2453, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.003 | 2017: +0.011 | 2018: +0.030 | 2019: +0.154 | 2020: +0.061 | 2021: +0.144 | 2022: +0.075 | 2023: +0.133 | 2024: +0.066 | 2025: +0.164 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.219 | 2016: -0.005 | 2017: +0.118 | 2018: +0.246 | 2019: +0.307 | 2020: +0.172 | 2021: +0.198 | 2022: +0.161 | 2023: +0.312 | 2024: +0.342 | 2025: +0.135 | 2026: +0.227
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=1.91, Recency ratio=4.91
- Early IC=+0.0202, Recent IC=+0.0992, 1st-half IC=+0.0593, 2nd-half IC=+0.1134, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.073, Q3_mid=+0.088, Q4=+0.081, Q5_high_vol=+0.092

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1308, Sharpe=+0.6052)
- Admission: Train IC=+0.2322, Deflated=+0.2318, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.222 | 2016: +0.117 | 2017: +0.048 | 2018: +0.105 | 2019: +0.222 | 2020: +0.126 | 2021: +0.135 | 2022: +0.095 | 2023: +0.154 | 2024: +0.083 | 2025: +0.205 | 2026: +0.033
- Yearly Tail ICs:   2015: +0.128 | 2016: +0.081 | 2017: +0.211 | 2018: +0.258 | 2019: +0.330 | 2020: +0.214 | 2021: +0.227 | 2022: +0.152 | 2023: +0.346 | 2024: +0.274 | 2025: +0.264 | 2026: +0.077
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=1.54
- Early IC=+0.0767, Recent IC=+0.1184, 1st-half IC=+0.1202, 2nd-half IC=+0.1260, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.105, Q3_mid=+0.096, Q4=+0.104, Q5_high_vol=+0.159

**`combo_mean__star50_limit_proximity_early__volume_weighted_price_position`** (Lock IC=+0.1320, Sharpe=+0.6019)
- Admission: Train IC=+0.2625, Deflated=+0.2627, IR=0.79, Mono=0.76, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.089 | 2017: +0.042 | 2018: +0.134 | 2019: +0.221 | 2020: +0.070 | 2021: +0.190 | 2022: +0.063 | 2023: +0.114 | 2024: +0.107 | 2025: +0.147 | 2026: +0.116
- Yearly Tail ICs:   2015: -0.024 | 2016: +0.028 | 2017: +0.199 | 2018: +0.204 | 2019: +0.590 | 2020: +0.129 | 2021: +0.318 | 2022: +0.116 | 2023: +0.255 | 2024: +0.344 | 2025: +0.140 | 2026: +0.146
- IC CV=0.50, Neg years (linear/tail)=0/0 of 8, Half ratio=1.05, Recency ratio=1.26
- Early IC=+0.0877, Recent IC=+0.1105, 1st-half IC=+0.1204, 2nd-half IC=+0.1264, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.085, Q3_mid=+0.108, Q4=+0.146, Q5_high_vol=+0.172

**`combo_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1361, Sharpe=+0.5812)
- Admission: Train IC=+0.2909, Deflated=+0.2908, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.071 | 2017: -0.020 | 2018: +0.104 | 2019: +0.260 | 2020: +0.127 | 2021: +0.113 | 2022: +0.077 | 2023: +0.149 | 2024: +0.090 | 2025: +0.154 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.083 | 2017: +0.042 | 2018: +0.281 | 2019: +0.503 | 2020: +0.204 | 2021: +0.288 | 2022: +0.261 | 2023: +0.199 | 2024: +0.402 | 2025: +0.055 | 2026: +0.237
- IC CV=0.65, Neg years (linear/tail)=1/0 of 8, Half ratio=0.91, Recency ratio=2.83
- Early IC=+0.0422, Recent IC=+0.1196, 1st-half IC=+0.1234, 2nd-half IC=+0.1129, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.168, Q2=+0.107, Q3_mid=+0.073, Q4=+0.104, Q5_high_vol=+0.180

**`combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.1017, Sharpe=+0.5812)
- Admission: Train IC=+0.2887, Deflated=+0.2882, IR=0.78, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.106 | 2017: -0.039 | 2018: +0.107 | 2019: +0.256 | 2020: +0.126 | 2021: +0.121 | 2022: +0.064 | 2023: +0.093 | 2024: +0.102 | 2025: +0.115 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.289 | 2016: +0.097 | 2017: +0.041 | 2018: +0.284 | 2019: +0.493 | 2020: +0.190 | 2021: +0.292 | 2022: +0.260 | 2023: +0.191 | 2024: +0.386 | 2025: +0.055 | 2026: +0.246
- IC CV=0.73, Neg years (linear/tail)=1/0 of 8, Half ratio=0.89, Recency ratio=2.83
- Early IC=+0.0343, Recent IC=+0.0970, 1st-half IC=+0.1175, 2nd-half IC=+0.1042, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.085, Q3_mid=+0.050, Q4=+0.113, Q5_high_vol=+0.190

**`combo_max__opening_drive_thrust_ratio__impulse_bar_dominance`** (Lock IC=+0.0968, Sharpe=+0.5705)
- Admission: Train IC=+0.2329, Deflated=+0.2328, IR=0.60, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.040 | 2017: +0.025 | 2018: +0.072 | 2019: +0.108 | 2020: +0.097 | 2021: +0.137 | 2022: +0.102 | 2023: +0.192 | 2024: +0.083 | 2025: +0.168 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.297 | 2016: +0.158 | 2017: +0.022 | 2018: +0.108 | 2019: +0.306 | 2020: +0.150 | 2021: +0.140 | 2022: +0.174 | 2023: +0.414 | 2024: +0.275 | 2025: +0.390 | 2026: -0.121
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.86, Recency ratio=2.83
- Early IC=+0.0486, Recent IC=+0.1376, 1st-half IC=+0.0707, 2nd-half IC=+0.1312, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.122, Q2=+0.057, Q3_mid=+0.088, Q4=+0.092, Q5_high_vol=+0.146

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1421, Sharpe=+0.5695)
- Admission: Train IC=+0.2358, Deflated=+0.2340, IR=0.76, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.062 | 2017: +0.024 | 2018: +0.086 | 2019: +0.155 | 2020: +0.111 | 2021: +0.160 | 2022: +0.135 | 2023: +0.131 | 2024: +0.114 | 2025: +0.193 | 2026: +0.064
- Yearly Tail ICs:   2015: -0.049 | 2016: +0.155 | 2017: +0.141 | 2018: +0.115 | 2019: +0.416 | 2020: +0.103 | 2021: +0.203 | 2022: +0.233 | 2023: +0.268 | 2024: +0.375 | 2025: +0.216 | 2026: -0.023
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=2.24
- Early IC=+0.0548, Recent IC=+0.1226, 1st-half IC=+0.0917, 2nd-half IC=+0.1423, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.087, Q3_mid=+0.107, Q4=+0.106, Q5_high_vol=+0.172

**`combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.1100, Sharpe=+0.5568)
- Admission: Train IC=+0.2297, Deflated=+0.2299, IR=0.78, Mono=0.81, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.160 | 2016: +0.112 | 2017: -0.039 | 2018: +0.156 | 2019: +0.124 | 2020: +0.144 | 2021: +0.056 | 2022: +0.185 | 2023: +0.124 | 2024: +0.055 | 2025: +0.080 | 2026: +0.143
- Yearly Tail ICs:   2015: +0.074 | 2016: +0.385 | 2017: +0.158 | 2018: +0.385 | 2019: +0.386 | 2020: +0.301 | 2021: +0.156 | 2022: +0.438 | 2023: +0.126 | 2024: +0.007 | 2025: +0.073 | 2026: +0.091
- IC CV=0.67, Neg years (linear/tail)=1/0 of 8, Half ratio=0.87, Recency ratio=1.54
- Early IC=+0.0581, Recent IC=+0.0895, 1st-half IC=+0.1131, 2nd-half IC=+0.0978, Neg regimes=0/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.29)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.161, Q3_mid=+0.052, Q4=+0.134, Q5_high_vol=+0.190

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1286, Sharpe=+0.5529)
- Admission: Train IC=+0.2467, Deflated=+0.2465, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.51
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.047 | 2017: -0.047 | 2018: +0.084 | 2019: +0.131 | 2020: +0.102 | 2021: +0.033 | 2022: +0.180 | 2023: +0.115 | 2024: +0.083 | 2025: +0.129 | 2026: +0.127
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.222 | 2017: +0.080 | 2018: +0.355 | 2019: +0.275 | 2020: +0.402 | 2021: +0.130 | 2022: +0.486 | 2023: +0.119 | 2024: +0.057 | 2025: +0.101 | 2026: +0.271
- IC CV=0.75, Neg years (linear/tail)=1/0 of 8, Half ratio=1.22, Recency ratio=5.34
- Early IC=+0.0186, Recent IC=+0.0992, 1st-half IC=+0.0787, 2nd-half IC=+0.0959, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.138, Q3_mid=+0.034, Q4=+0.104, Q5_high_vol=+0.175

**`combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1271, Sharpe=+0.5469)
- Admission: Train IC=+0.2377, Deflated=+0.2376, IR=0.59, Mono=0.73, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.168 | 2016: +0.044 | 2017: -0.054 | 2018: +0.073 | 2019: +0.131 | 2020: +0.100 | 2021: +0.042 | 2022: +0.180 | 2023: +0.112 | 2024: +0.081 | 2025: +0.126 | 2026: +0.122
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.166 | 2017: +0.014 | 2018: +0.359 | 2019: +0.259 | 2020: +0.391 | 2021: +0.172 | 2022: +0.463 | 2023: +0.068 | 2024: +0.023 | 2025: +0.066 | 2026: +0.302
- IC CV=0.76, Neg years (linear/tail)=1/0 of 8, Half ratio=1.32, Recency ratio=8.02
- Early IC=+0.0120, Recent IC=+0.0961, 1st-half IC=+0.0757, 2nd-half IC=+0.1001, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.020, Q2=+0.138, Q3_mid=+0.038, Q4=+0.103, Q5_high_vol=+0.174

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1091, Sharpe=+0.5217)
- Admission: Train IC=+0.3022, Deflated=+0.3007, IR=0.92, Mono=0.80, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.091 | 2017: +0.036 | 2018: +0.120 | 2019: +0.196 | 2020: +0.136 | 2021: +0.165 | 2022: +0.131 | 2023: +0.161 | 2024: +0.095 | 2025: +0.181 | 2026: +0.015
- Yearly Tail ICs:   2015: -0.021 | 2016: +0.122 | 2017: +0.102 | 2018: +0.263 | 2019: +0.516 | 2020: +0.151 | 2021: +0.344 | 2022: +0.317 | 2023: +0.379 | 2024: +0.370 | 2025: +0.153 | 2026: -0.065
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.23, Recency ratio=1.63
- Early IC=+0.0784, Recent IC=+0.1282, 1st-half IC=+0.1184, 2nd-half IC=+0.1454, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.137, Q2=+0.100, Q3_mid=+0.115, Q4=+0.134, Q5_high_vol=+0.182

**`combo_max__bar_body_rng_0__limit_down_proximity_early`** (Lock IC=+0.1023, Sharpe=+0.5185)
- Admission: Train IC=+0.1686, Deflated=+0.1681, IR=0.42, Mono=0.67, p=0.0012, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.117 | 2017: -0.014 | 2018: +0.134 | 2019: +0.136 | 2020: +0.076 | 2021: +0.144 | 2022: +0.126 | 2023: +0.090 | 2024: +0.022 | 2025: +0.111 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.110 | 2016: +0.009 | 2017: +0.114 | 2018: +0.316 | 2019: +0.260 | 2020: -0.057 | 2021: +0.337 | 2022: +0.033 | 2023: +0.086 | 2024: +0.190 | 2025: +0.154 | 2026: +0.027
- IC CV=0.61, Neg years (linear/tail)=1/1 of 8, Half ratio=1.19, Recency ratio=0.94
- Early IC=+0.0596, Recent IC=+0.0562, 1st-half IC=+0.0852, 2nd-half IC=+0.1014, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.070, Q3_mid=+0.042, Q4=+0.101, Q5_high_vol=+0.138

**`combo_sig_product__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0906, Sharpe=+0.5068)
- Admission: Train IC=+0.1912, Deflated=+0.1910, IR=0.45, Mono=0.68, p=0.0002, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.106 | 2017: +0.016 | 2018: +0.137 | 2019: +0.145 | 2020: +0.154 | 2021: +0.154 | 2022: +0.076 | 2023: +0.187 | 2024: +0.078 | 2025: +0.176 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.258 | 2016: -0.091 | 2017: -0.071 | 2018: +0.192 | 2019: +0.407 | 2020: +0.276 | 2021: +0.230 | 2022: +0.050 | 2023: +0.360 | 2024: +0.170 | 2025: +0.398 | 2026: +0.191
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.19, Recency ratio=1.73
- Early IC=+0.0765, Recent IC=+0.1324, 1st-half IC=+0.1075, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.090, Q3_mid=+0.110, Q4=+0.102, Q5_high_vol=+0.172

**`combo_max__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0976, Sharpe=+0.4955)
- Admission: Train IC=+0.1824, Deflated=+0.1820, IR=0.49, Mono=0.67, p=0.0004, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.105 | 2017: -0.014 | 2018: +0.107 | 2019: +0.187 | 2020: +0.127 | 2021: +0.147 | 2022: +0.118 | 2023: +0.056 | 2024: +0.077 | 2025: +0.068 | 2026: +0.155
- Yearly Tail ICs:   2015: +0.090 | 2016: +0.157 | 2017: +0.086 | 2018: +0.155 | 2019: +0.256 | 2020: +0.155 | 2021: +0.219 | 2022: +0.180 | 2023: +0.041 | 2024: +0.168 | 2025: +0.010 | 2026: +0.302
- IC CV=0.57, Neg years (linear/tail)=1/0 of 8, Half ratio=1.05, Recency ratio=1.42
- Early IC=+0.0466, Recent IC=+0.0662, 1st-half IC=+0.1068, 2nd-half IC=+0.1122, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.070, Q3_mid=+0.091, Q4=+0.140, Q5_high_vol=+0.112

**`combo_rank_min__max_up_ret__impulse_bar_dominance`** (Lock IC=+0.0519, Sharpe=+0.4591)
- Admission: Train IC=+0.2020, Deflated=+0.2008, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.036 | 2017: +0.034 | 2018: +0.058 | 2019: +0.074 | 2020: +0.030 | 2021: +0.158 | 2022: +0.146 | 2023: +0.176 | 2024: +0.092 | 2025: +0.166 | 2026: -0.116
- Yearly Tail ICs:   2015: -0.161 | 2016: +0.189 | 2017: +0.145 | 2018: +0.158 | 2019: +0.172 | 2020: +0.018 | 2021: +0.124 | 2022: +0.357 | 2023: +0.418 | 2024: +0.282 | 2025: +0.215 | 2026: -0.226
- IC CV=0.55, Neg years (linear/tail)=0/0 of 8, Half ratio=4.20, Recency ratio=2.90
- Early IC=+0.0461, Recent IC=+0.1335, 1st-half IC=+0.0347, 2nd-half IC=+0.1455, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.058, Q3_mid=+0.136, Q4=+0.055, Q5_high_vol=+0.101

**`combo_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1292, Sharpe=+0.4551)
- Admission: Train IC=+0.2835, Deflated=+0.2833, IR=0.75, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.042 | 2017: +0.016 | 2018: +0.124 | 2019: +0.185 | 2020: +0.108 | 2021: +0.160 | 2022: +0.129 | 2023: +0.158 | 2024: +0.058 | 2025: +0.194 | 2026: +0.030
- Yearly Tail ICs:   2015: +0.129 | 2016: -0.040 | 2017: +0.083 | 2018: +0.161 | 2019: +0.430 | 2020: +0.244 | 2021: +0.296 | 2022: +0.266 | 2023: +0.301 | 2024: +0.259 | 2025: +0.294 | 2026: -0.057
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.27, Recency ratio=1.55
- Early IC=+0.0698, Recent IC=+0.1081, 1st-half IC=+0.1074, 2nd-half IC=+0.1361, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.110, Q3_mid=+0.104, Q4=+0.093, Q5_high_vol=+0.177

**`combo_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1293, Sharpe=+0.4551)
- Admission: Train IC=+0.2832, Deflated=+0.2830, IR=0.75, Mono=0.79, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.042 | 2017: +0.016 | 2018: +0.124 | 2019: +0.185 | 2020: +0.108 | 2021: +0.159 | 2022: +0.129 | 2023: +0.159 | 2024: +0.058 | 2025: +0.194 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.131 | 2016: -0.041 | 2017: +0.083 | 2018: +0.164 | 2019: +0.430 | 2020: +0.246 | 2021: +0.294 | 2022: +0.266 | 2023: +0.302 | 2024: +0.263 | 2025: +0.294 | 2026: -0.057
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.27, Recency ratio=1.55
- Early IC=+0.0699, Recent IC=+0.1083, 1st-half IC=+0.1074, 2nd-half IC=+0.1360, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.110, Q3_mid=+0.104, Q4=+0.093, Q5_high_vol=+0.177

**`combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1133, Sharpe=+0.4549)
- Admission: Train IC=+0.2413, Deflated=+0.2405, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.011 | 2017: +0.014 | 2018: +0.093 | 2019: +0.194 | 2020: +0.097 | 2021: +0.147 | 2022: +0.123 | 2023: +0.168 | 2024: +0.089 | 2025: +0.191 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.250 | 2016: +0.038 | 2017: +0.091 | 2018: -0.042 | 2019: +0.361 | 2020: +0.225 | 2021: +0.225 | 2022: +0.284 | 2023: +0.443 | 2024: +0.255 | 2025: +0.266 | 2026: -0.148
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.38, Recency ratio=2.40
- Early IC=+0.0535, Recent IC=+0.1284, 1st-half IC=+0.1009, 2nd-half IC=+0.1397, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.104, Q3_mid=+0.134, Q4=+0.099, Q5_high_vol=+0.159

**`combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0725, Sharpe=+0.4339)
- Admission: Train IC=+0.2285, Deflated=+0.2289, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.137 | 2017: +0.014 | 2018: +0.130 | 2019: +0.194 | 2020: +0.098 | 2021: +0.126 | 2022: +0.118 | 2023: +0.153 | 2024: +0.067 | 2025: +0.131 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.352 | 2016: -0.106 | 2017: +0.173 | 2018: +0.247 | 2019: +0.393 | 2020: +0.074 | 2021: +0.286 | 2022: +0.149 | 2023: +0.507 | 2024: -0.006 | 2025: +0.196 | 2026: +0.134
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.18, Recency ratio=1.53
- Early IC=+0.0720, Recent IC=+0.1103, 1st-half IC=+0.1045, 2nd-half IC=+0.1231, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.090, Q3_mid=+0.088, Q4=+0.099, Q5_high_vol=+0.147

**`combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1066, Sharpe=+0.4207)
- Admission: Train IC=+0.1878, Deflated=+0.1863, IR=0.57, Mono=0.68, p=0.0004, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.052 | 2017: +0.029 | 2018: +0.069 | 2019: +0.159 | 2020: +0.077 | 2021: +0.126 | 2022: +0.154 | 2023: +0.127 | 2024: +0.128 | 2025: +0.133 | 2026: +0.094
- Yearly Tail ICs:   2015: +0.095 | 2016: +0.100 | 2017: +0.102 | 2018: +0.074 | 2019: +0.343 | 2020: +0.004 | 2021: +0.288 | 2022: +0.085 | 2023: +0.199 | 2024: +0.256 | 2025: +0.133 | 2026: +0.046
- IC CV=0.39, Neg years (linear/tail)=0/0 of 8, Half ratio=1.67, Recency ratio=2.71
- Early IC=+0.0479, Recent IC=+0.1296, 1st-half IC=+0.0830, 2nd-half IC=+0.1389, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.107, Q3_mid=+0.067, Q4=+0.114, Q5_high_vol=+0.152

**`combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1242, Sharpe=+0.4197)
- Admission: Train IC=+0.2081, Deflated=+0.2065, IR=0.57, Mono=0.69, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.084 | 2017: +0.031 | 2018: +0.063 | 2019: +0.152 | 2020: +0.122 | 2021: +0.156 | 2022: +0.151 | 2023: +0.131 | 2024: +0.135 | 2025: +0.154 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.044 | 2016: +0.135 | 2017: +0.085 | 2018: +0.096 | 2019: +0.369 | 2020: +0.075 | 2021: +0.347 | 2022: +0.133 | 2023: +0.221 | 2024: +0.239 | 2025: +0.152 | 2026: +0.117
- IC CV=0.36, Neg years (linear/tail)=0/0 of 8, Half ratio=1.63, Recency ratio=2.87
- Early IC=+0.0472, Recent IC=+0.1354, 1st-half IC=+0.0920, 2nd-half IC=+0.1499, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.103, Q2=+0.108, Q3_mid=+0.080, Q4=+0.125, Q5_high_vol=+0.180

**`combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early`** (Lock IC=+0.1058, Sharpe=+0.4149)
- Admission: Train IC=+0.2452, Deflated=+0.2443, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.015 | 2017: +0.016 | 2018: +0.085 | 2019: +0.204 | 2020: +0.098 | 2021: +0.135 | 2022: +0.123 | 2023: +0.167 | 2024: +0.100 | 2025: +0.184 | 2026: -0.018
- Yearly Tail ICs:   2015: +0.263 | 2016: +0.032 | 2017: +0.065 | 2018: -0.023 | 2019: +0.361 | 2020: +0.235 | 2021: +0.220 | 2022: +0.300 | 2023: +0.472 | 2024: +0.256 | 2025: +0.279 | 2026: -0.152
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.37, Recency ratio=2.62
- Early IC=+0.0509, Recent IC=+0.1332, 1st-half IC=+0.1020, 2nd-half IC=+0.1398, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.106, Q3_mid=+0.130, Q4=+0.100, Q5_high_vol=+0.166

**`combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1216, Sharpe=+0.4111)
- Admission: Train IC=+0.2077, Deflated=+0.2054, IR=0.64, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.056 | 2017: +0.020 | 2018: +0.098 | 2019: +0.110 | 2020: +0.126 | 2021: +0.161 | 2022: +0.162 | 2023: +0.129 | 2024: +0.095 | 2025: +0.161 | 2026: +0.084
- Yearly Tail ICs:   2015: -0.045 | 2016: +0.146 | 2017: +0.095 | 2018: +0.128 | 2019: +0.302 | 2020: +0.159 | 2021: +0.350 | 2022: +0.181 | 2023: +0.086 | 2024: +0.163 | 2025: +0.052 | 2026: +0.070
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.65, Recency ratio=1.89
- Early IC=+0.0593, Recent IC=+0.1122, 1st-half IC=+0.0879, 2nd-half IC=+0.1455, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.078, Q3_mid=+0.098, Q4=+0.131, Q5_high_vol=+0.176

**`combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1124, Sharpe=+0.3952)
- Admission: Train IC=+0.1987, Deflated=+0.1960, IR=0.52, Mono=0.69, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.100 | 2017: -0.031 | 2018: +0.096 | 2019: +0.091 | 2020: +0.077 | 2021: +0.066 | 2022: +0.131 | 2023: +0.154 | 2024: +0.122 | 2025: +0.085 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.264 | 2017: +0.061 | 2018: +0.442 | 2019: +0.295 | 2020: +0.014 | 2021: +0.130 | 2022: +0.254 | 2023: +0.202 | 2024: +0.169 | 2025: -0.014 | 2026: +0.123
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=1.60, Recency ratio=4.45
- Early IC=+0.0309, Recent IC=+0.1378, 1st-half IC=+0.0747, 2nd-half IC=+0.1196, Neg regimes=0/5
- Weak component: `yesterday_first_30min_return` (CV=0.99)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.111, Q3_mid=+0.063, Q4=+0.145, Q5_high_vol=+0.090

**`combo_rel_diff__first_bar_return__demark_setup_reversal_early`** (Lock IC=+0.1198, Sharpe=+0.3623)
- Admission: Train IC=+0.2782, Deflated=+0.2779, IR=0.74, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.070 | 2017: +0.010 | 2018: +0.133 | 2019: +0.195 | 2020: +0.138 | 2021: +0.153 | 2022: +0.125 | 2023: +0.142 | 2024: +0.082 | 2025: +0.172 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.031 | 2016: +0.011 | 2017: +0.083 | 2018: +0.169 | 2019: +0.423 | 2020: +0.239 | 2021: +0.284 | 2022: +0.269 | 2023: +0.263 | 2024: +0.239 | 2025: +0.299 | 2026: -0.104
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.19, Recency ratio=1.57
- Early IC=+0.0715, Recent IC=+0.1120, 1st-half IC=+0.1161, 2nd-half IC=+0.1383, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.107, Q3_mid=+0.100, Q4=+0.090, Q5_high_vol=+0.201

**`volatility_expansion_trend_vector`** (Lock IC=+0.0926, Sharpe=+0.3605)
- Admission: Train IC=+0.1817, Deflated=+0.1810, IR=0.60, Mono=0.73, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.016 | 2017: +0.028 | 2018: +0.009 | 2019: +0.101 | 2020: +0.047 | 2021: +0.138 | 2022: +0.089 | 2023: +0.166 | 2024: +0.080 | 2025: +0.212 | 2026: -0.095
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.081 | 2017: +0.039 | 2018: -0.016 | 2019: +0.246 | 2020: +0.179 | 2021: +0.151 | 2022: +0.361 | 2023: +0.381 | 2024: +0.160 | 2025: +0.280 | 2026: -0.291
- IC CV=0.61, Neg years (linear/tail)=0/1 of 8, Half ratio=3.52, Recency ratio=6.66
- Early IC=+0.0185, Recent IC=+0.1233, 1st-half IC=+0.0356, 2nd-half IC=+0.1253, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.070, Q3_mid=+0.126, Q4=+0.026, Q5_high_vol=+0.068

**`combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.1028, Sharpe=+0.3412)
- Admission: Train IC=+0.2239, Deflated=+0.2237, IR=0.79, Mono=0.79, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.134 | 2016: +0.018 | 2017: +0.017 | 2018: +0.051 | 2019: +0.132 | 2020: +0.055 | 2021: +0.145 | 2022: +0.071 | 2023: +0.197 | 2024: +0.078 | 2025: +0.205 | 2026: -0.056
- Yearly Tail ICs:   2015: +0.268 | 2016: +0.179 | 2017: +0.101 | 2018: +0.027 | 2019: +0.276 | 2020: +0.160 | 2021: +0.171 | 2022: +0.385 | 2023: +0.502 | 2024: +0.185 | 2025: +0.215 | 2026: -0.205
- IC CV=0.60, Neg years (linear/tail)=0/0 of 8, Half ratio=2.47, Recency ratio=4.05
- Early IC=+0.0339, Recent IC=+0.1374, 1st-half IC=+0.0520, 2nd-half IC=+0.1284, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.134, Q2=+0.081, Q3_mid=+0.119, Q4=+0.054, Q5_high_vol=+0.093

**`combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.0997, Sharpe=+0.3365)
- Admission: Train IC=+0.2785, Deflated=+0.2777, IR=0.76, Mono=0.76, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.134 | 2017: -0.020 | 2018: +0.148 | 2019: +0.245 | 2020: +0.155 | 2021: +0.136 | 2022: +0.076 | 2023: +0.094 | 2024: +0.088 | 2025: +0.122 | 2026: +0.068
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.085 | 2017: +0.048 | 2018: +0.307 | 2019: +0.510 | 2020: +0.168 | 2021: +0.248 | 2022: +0.243 | 2023: +0.193 | 2024: +0.380 | 2025: +0.140 | 2026: +0.204
- IC CV=0.62, Neg years (linear/tail)=1/0 of 8, Half ratio=0.79, Recency ratio=1.43
- Early IC=+0.0638, Recent IC=+0.0910, 1st-half IC=+0.1393, 2nd-half IC=+0.1095, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.097, Q3_mid=+0.047, Q4=+0.126, Q5_high_vol=+0.216

**`combo_rank_min__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0656, Sharpe=+0.3295)
- Admission: Train IC=+0.1904, Deflated=+0.1908, IR=0.49, Mono=0.71, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.105 | 2016: +0.086 | 2017: +0.045 | 2018: +0.052 | 2019: +0.178 | 2020: +0.080 | 2021: +0.171 | 2022: +0.030 | 2023: +0.165 | 2024: +0.074 | 2025: +0.148 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.157 | 2016: +0.032 | 2017: +0.134 | 2018: +0.192 | 2019: +0.259 | 2020: +0.225 | 2021: +0.320 | 2022: +0.124 | 2023: +0.344 | 2024: +0.033 | 2025: +0.281 | 2026: -0.183
- IC CV=0.57, Neg years (linear/tail)=0/0 of 8, Half ratio=1.51, Recency ratio=2.43
- Early IC=+0.0488, Recent IC=+0.1187, 1st-half IC=+0.0801, 2nd-half IC=+0.1208, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.110, Q2=+0.075, Q3_mid=+0.134, Q4=+0.079, Q5_high_vol=+0.110

**`combo_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1056, Sharpe=+0.3256)
- Admission: Train IC=+0.2367, Deflated=+0.2353, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.033 | 2017: +0.023 | 2018: +0.078 | 2019: +0.178 | 2020: +0.092 | 2021: +0.165 | 2022: +0.155 | 2023: +0.149 | 2024: +0.068 | 2025: +0.196 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.001 | 2016: +0.245 | 2017: +0.029 | 2018: +0.111 | 2019: +0.352 | 2020: +0.158 | 2021: +0.338 | 2022: +0.376 | 2023: +0.334 | 2024: +0.198 | 2025: +0.255 | 2026: -0.249
- IC CV=0.46, Neg years (linear/tail)=0/0 of 8, Half ratio=1.55, Recency ratio=2.15
- Early IC=+0.0506, Recent IC=+0.1086, 1st-half IC=+0.0925, 2nd-half IC=+0.1437, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.114, Q3_mid=+0.115, Q4=+0.098, Q5_high_vol=+0.157

**`combo_mean__bar_body_rng_0__impulse_bar_dominance`** (Lock IC=+0.0960, Sharpe=+0.3067)
- Admission: Train IC=+0.1631, Deflated=+0.1632, IR=0.41, Mono=0.67, p=0.0016, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.175 | 2016: +0.078 | 2017: +0.009 | 2018: +0.090 | 2019: +0.132 | 2020: +0.107 | 2021: +0.149 | 2022: +0.102 | 2023: +0.153 | 2024: +0.065 | 2025: +0.178 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.347 | 2016: -0.080 | 2017: -0.042 | 2018: +0.192 | 2019: +0.387 | 2020: +0.184 | 2021: +0.192 | 2022: +0.051 | 2023: +0.305 | 2024: +0.148 | 2025: +0.369 | 2026: -0.010
- IC CV=0.44, Neg years (linear/tail)=0/1 of 8, Half ratio=1.65, Recency ratio=2.21
- Early IC=+0.0493, Recent IC=+0.1089, 1st-half IC=+0.0734, 2nd-half IC=+0.1212, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.058, Q3_mid=+0.101, Q4=+0.079, Q5_high_vol=+0.134

**`combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1453, Sharpe=+0.2923)
- Admission: Train IC=+0.2057, Deflated=+0.2041, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.009 | 2017: +0.018 | 2018: +0.064 | 2019: +0.156 | 2020: +0.059 | 2021: +0.140 | 2022: +0.112 | 2023: +0.124 | 2024: +0.099 | 2025: +0.174 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.064 | 2017: +0.129 | 2018: +0.125 | 2019: +0.411 | 2020: +0.019 | 2021: +0.130 | 2022: +0.233 | 2023: +0.231 | 2024: +0.362 | 2025: +0.141 | 2026: -0.031
- IC CV=0.45, Neg years (linear/tail)=0/0 of 8, Half ratio=1.75, Recency ratio=2.72
- Early IC=+0.0412, Recent IC=+0.1118, 1st-half IC=+0.0723, 2nd-half IC=+0.1267, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=0.71)
- Regime ICs: Q1_low_vol=+0.144, Q2=+0.059, Q3_mid=+0.110, Q4=+0.086, Q5_high_vol=+0.125

**`combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance`** (Lock IC=+0.0934, Sharpe=+0.2719)
- Admission: Train IC=+0.1541, Deflated=+0.1522, IR=0.58, Mono=0.70, p=0.0032, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.053 | 2017: +0.034 | 2018: +0.074 | 2019: +0.073 | 2020: +0.011 | 2021: +0.156 | 2022: +0.135 | 2023: +0.180 | 2024: +0.084 | 2025: +0.165 | 2026: -0.031
- Yearly Tail ICs:   2015: -0.095 | 2016: +0.160 | 2017: +0.121 | 2018: +0.123 | 2019: +0.285 | 2020: -0.088 | 2021: +0.215 | 2022: +0.270 | 2023: +0.272 | 2024: +0.343 | 2025: +0.121 | 2026: -0.085
- IC CV=0.57, Neg years (linear/tail)=0/1 of 8, Half ratio=3.10, Recency ratio=2.47
- Early IC=+0.0530, Recent IC=+0.1309, 1st-half IC=+0.0453, 2nd-half IC=+0.1403, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.097, Q3_mid=+0.098, Q4=+0.093, Q5_high_vol=+0.096

**`combo_mean__max_up_ret__star50_limit_proximity_early`** (Lock IC=+0.1319, Sharpe=+0.2487)
- Admission: Train IC=+0.2459, Deflated=+0.2439, IR=0.66, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.076 | 2017: +0.021 | 2018: +0.132 | 2019: +0.164 | 2020: +0.128 | 2021: +0.161 | 2022: +0.153 | 2023: +0.139 | 2024: +0.112 | 2025: +0.177 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.041 | 2016: +0.205 | 2017: +0.125 | 2018: +0.280 | 2019: +0.362 | 2020: +0.165 | 2021: +0.295 | 2022: +0.265 | 2023: +0.170 | 2024: +0.314 | 2025: +0.159 | 2026: +0.112
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.33, Recency ratio=1.64
- Early IC=+0.0763, Recent IC=+0.1254, 1st-half IC=+0.1122, 2nd-half IC=+0.1493, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.130, Q2=+0.115, Q3_mid=+0.089, Q4=+0.135, Q5_high_vol=+0.199

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return`** (Lock IC=+0.0936, Sharpe=+0.2427)
- Admission: Train IC=+0.2163, Deflated=+0.2151, IR=0.51, Mono=0.73, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.152 | 2017: -0.074 | 2018: +0.153 | 2019: +0.109 | 2020: +0.124 | 2021: +0.065 | 2022: +0.159 | 2023: +0.150 | 2024: +0.081 | 2025: +0.076 | 2026: +0.117
- Yearly Tail ICs:   2015: +0.126 | 2016: +0.243 | 2017: +0.039 | 2018: +0.350 | 2019: +0.181 | 2020: +0.377 | 2021: +0.191 | 2022: +0.359 | 2023: -0.018 | 2024: +0.160 | 2025: +0.067 | 2026: +0.190
- IC CV=0.75, Neg years (linear/tail)=1/1 of 8, Half ratio=1.07, Recency ratio=2.90
- Early IC=+0.0397, Recent IC=+0.1150, 1st-half IC=+0.0999, 2nd-half IC=+0.1070, Neg regimes=1/5
- Weak component: `yesterday_early_vwap_dev` (CV=1.29)
- Regime ICs: Q1_low_vol=-0.005, Q2=+0.148, Q3_mid=+0.069, Q4=+0.139, Q5_high_vol=+0.155

**`opening_drive_thrust_ratio`** (Lock IC=+0.0792, Sharpe=+0.2360)
- Admission: Train IC=+0.2357, Deflated=+0.2357, IR=0.78, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.045 | 2017: +0.030 | 2018: +0.088 | 2019: +0.188 | 2020: +0.095 | 2021: +0.133 | 2022: +0.085 | 2023: +0.199 | 2024: +0.100 | 2025: +0.166 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.041 | 2017: -0.006 | 2018: +0.191 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.198 | 2025: +0.229 | 2026: -0.077
- IC CV=0.46, Neg years (linear/tail)=0/1 of 8, Half ratio=1.44, Recency ratio=2.54
- Early IC=+0.0589, Recent IC=+0.1493, 1st-half IC=+0.0929, 2nd-half IC=+0.1339, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.087, Q3_mid=+0.131, Q4=+0.097, Q5_high_vol=+0.133

**`combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1003, Sharpe=+0.2207)
- Admission: Train IC=+0.1889, Deflated=+0.1875, IR=0.49, Mono=0.69, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.084 | 2017: +0.029 | 2018: +0.075 | 2019: +0.150 | 2020: +0.123 | 2021: +0.146 | 2022: +0.142 | 2023: +0.146 | 2024: +0.122 | 2025: +0.126 | 2026: +0.099
- Yearly Tail ICs:   2015: -0.017 | 2016: +0.176 | 2017: +0.067 | 2018: +0.217 | 2019: +0.251 | 2020: +0.099 | 2021: +0.327 | 2022: +0.131 | 2023: +0.252 | 2024: +0.165 | 2025: +0.096 | 2026: +0.143
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.51, Recency ratio=2.57
- Early IC=+0.0521, Recent IC=+0.1338, 1st-half IC=+0.0950, 2nd-half IC=+0.1436, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.085, Q3_mid=+0.086, Q4=+0.116, Q5_high_vol=+0.182

**`combo_max__bar_body_rng_0__impulse_bar_dominance`** (Lock IC=+0.1036, Sharpe=+0.2192)
- Admission: Train IC=+0.1651, Deflated=+0.1654, IR=0.44, Mono=0.66, p=0.0016, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.153 | 2016: +0.124 | 2017: -0.006 | 2018: +0.106 | 2019: +0.080 | 2020: +0.113 | 2021: +0.159 | 2022: +0.080 | 2023: +0.156 | 2024: +0.024 | 2025: +0.193 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.077 | 2017: +0.018 | 2018: +0.167 | 2019: +0.384 | 2020: +0.086 | 2021: +0.250 | 2022: +0.167 | 2023: +0.339 | 2024: +0.135 | 2025: +0.476 | 2026: -0.326
- IC CV=0.61, Neg years (linear/tail)=1/0 of 8, Half ratio=1.65, Recency ratio=1.80
- Early IC=+0.0502, Recent IC=+0.0903, 1st-half IC=+0.0655, 2nd-half IC=+0.1077, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.046, Q3_mid=+0.079, Q4=+0.077, Q5_high_vol=+0.138

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.1213, Sharpe=+0.2173)
- Admission: Train IC=+0.2467, Deflated=+0.2471, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.163 | 2017: +0.012 | 2018: +0.139 | 2019: +0.210 | 2020: +0.122 | 2021: +0.118 | 2022: +0.087 | 2023: +0.126 | 2024: +0.072 | 2025: +0.157 | 2026: +0.066
- Yearly Tail ICs:   2015: +0.194 | 2016: +0.152 | 2017: +0.137 | 2018: +0.256 | 2019: +0.472 | 2020: +0.135 | 2021: +0.335 | 2022: +0.188 | 2023: +0.267 | 2024: +0.389 | 2025: +0.200 | 2026: +0.072
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=0.92, Recency ratio=1.31
- Early IC=+0.0754, Recent IC=+0.0991, 1st-half IC=+0.1190, 2nd-half IC=+0.1093, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.094, Q3_mid=+0.086, Q4=+0.086, Q5_high_vol=+0.151

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0786, Sharpe=+0.2167)
- Admission: Train IC=+0.1874, Deflated=+0.1876, IR=0.62, Mono=0.72, p=0.0004, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.121 | 2017: +0.026 | 2018: +0.133 | 2019: +0.141 | 2020: +0.122 | 2021: +0.171 | 2022: +0.092 | 2023: +0.179 | 2024: +0.078 | 2025: +0.153 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.104 | 2017: +0.184 | 2018: +0.223 | 2019: +0.145 | 2020: +0.089 | 2021: +0.363 | 2022: +0.155 | 2023: +0.291 | 2024: +0.090 | 2025: +0.221 | 2026: +0.017
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.24, Recency ratio=1.62
- Early IC=+0.0796, Recent IC=+0.1289, 1st-half IC=+0.1055, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.083, Q3_mid=+0.099, Q4=+0.107, Q5_high_vol=+0.161

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0784, Sharpe=+0.2167)
- Admission: Train IC=+0.1874, Deflated=+0.1876, IR=0.62, Mono=0.72, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.121 | 2017: +0.027 | 2018: +0.133 | 2019: +0.142 | 2020: +0.122 | 2021: +0.171 | 2022: +0.091 | 2023: +0.180 | 2024: +0.079 | 2025: +0.153 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.132 | 2016: +0.104 | 2017: +0.182 | 2018: +0.223 | 2019: +0.145 | 2020: +0.089 | 2021: +0.363 | 2022: +0.154 | 2023: +0.291 | 2024: +0.090 | 2025: +0.221 | 2026: +0.017
- IC CV=0.40, Neg years (linear/tail)=0/0 of 8, Half ratio=1.24, Recency ratio=1.61
- Early IC=+0.0802, Recent IC=+0.1293, 1st-half IC=+0.1056, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.164, Q2=+0.083, Q3_mid=+0.099, Q4=+0.107, Q5_high_vol=+0.160

**`combo_min__limit_down_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1106, Sharpe=+0.2142)
- Admission: Train IC=+0.2009, Deflated=+0.1995, IR=0.53, Mono=0.71, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.166 | 2016: +0.015 | 2017: +0.017 | 2018: +0.036 | 2019: +0.115 | 2020: +0.062 | 2021: +0.145 | 2022: +0.106 | 2023: +0.129 | 2024: +0.116 | 2025: +0.128 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.221 | 2016: +0.013 | 2017: +0.006 | 2018: +0.214 | 2019: +0.309 | 2020: +0.202 | 2021: +0.284 | 2022: +0.108 | 2023: +0.244 | 2024: +0.349 | 2025: +0.111 | 2026: +0.274
- IC CV=0.48, Neg years (linear/tail)=0/0 of 8, Half ratio=2.28, Recency ratio=4.61
- Early IC=+0.0265, Recent IC=+0.1223, 1st-half IC=+0.0578, 2nd-half IC=+0.1315, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.113, Q2=+0.067, Q3_mid=+0.094, Q4=+0.109, Q5_high_vol=+0.117

**`combo_rank_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.1432, Sharpe=+0.2000)
- Admission: Train IC=+0.2141, Deflated=+0.2130, IR=0.57, Mono=0.67, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.149 | 2017: -0.009 | 2018: +0.121 | 2019: +0.152 | 2020: +0.138 | 2021: +0.136 | 2022: +0.156 | 2023: +0.121 | 2024: +0.075 | 2025: +0.171 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.079 | 2016: -0.011 | 2017: +0.082 | 2018: +0.271 | 2019: +0.253 | 2020: +0.036 | 2021: +0.379 | 2022: +0.187 | 2023: +0.253 | 2024: +0.249 | 2025: +0.105 | 2026: +0.034
- IC CV=0.46, Neg years (linear/tail)=1/0 of 8, Half ratio=1.26, Recency ratio=1.68
- Early IC=+0.0576, Recent IC=+0.0969, 1st-half IC=+0.1026, 2nd-half IC=+0.1291, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.114, Q2=+0.118, Q3_mid=+0.070, Q4=+0.130, Q5_high_vol=+0.161

**`combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1073, Sharpe=+0.1834)
- Admission: Train IC=+0.1853, Deflated=+0.1840, IR=0.52, Mono=0.68, p=0.0004, MaxCorr=0.76
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.069 | 2017: +0.033 | 2018: +0.122 | 2019: +0.197 | 2020: +0.149 | 2021: +0.137 | 2022: +0.137 | 2023: +0.160 | 2024: +0.139 | 2025: +0.101 | 2026: +0.130
- Yearly Tail ICs:   2015: -0.118 | 2016: +0.179 | 2017: +0.085 | 2018: +0.307 | 2019: +0.407 | 2020: +0.112 | 2021: +0.174 | 2022: +0.004 | 2023: +0.260 | 2024: +0.242 | 2025: +0.081 | 2026: +0.335
- IC CV=0.32, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=1.93
- Early IC=+0.0775, Recent IC=+0.1496, 1st-half IC=+0.1344, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.111, Q3_mid=+0.045, Q4=+0.160, Q5_high_vol=+0.261

**`combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1073, Sharpe=+0.1834)
- Admission: Train IC=+0.1852, Deflated=+0.1839, IR=0.53, Mono=0.68, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.070 | 2017: +0.032 | 2018: +0.121 | 2019: +0.197 | 2020: +0.150 | 2021: +0.137 | 2022: +0.137 | 2023: +0.160 | 2024: +0.139 | 2025: +0.101 | 2026: +0.130
- Yearly Tail ICs:   2015: -0.119 | 2016: +0.179 | 2017: +0.085 | 2018: +0.307 | 2019: +0.408 | 2020: +0.114 | 2021: +0.174 | 2022: +0.002 | 2023: +0.261 | 2024: +0.242 | 2025: +0.081 | 2026: +0.335
- IC CV=0.33, Neg years (linear/tail)=0/0 of 8, Half ratio=1.11, Recency ratio=1.94
- Early IC=+0.0768, Recent IC=+0.1493, 1st-half IC=+0.1341, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.101, Q2=+0.111, Q3_mid=+0.045, Q4=+0.160, Q5_high_vol=+0.261

**`combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1138, Sharpe=+0.1660)
- Admission: Train IC=+0.1709, Deflated=+0.1697, IR=0.48, Mono=0.67, p=0.0012, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.051 | 2017: +0.034 | 2018: +0.055 | 2019: +0.129 | 2020: +0.102 | 2021: +0.115 | 2022: +0.137 | 2023: +0.140 | 2024: +0.120 | 2025: +0.166 | 2026: +0.055
- Yearly Tail ICs:   2015: -0.025 | 2016: +0.071 | 2017: +0.127 | 2018: +0.126 | 2019: +0.276 | 2020: +0.113 | 2021: +0.205 | 2022: +0.131 | 2023: +0.131 | 2024: +0.205 | 2025: +0.034 | 2026: -0.063
- IC CV=0.35, Neg years (linear/tail)=0/0 of 8, Half ratio=1.79, Recency ratio=2.92
- Early IC=+0.0445, Recent IC=+0.1298, 1st-half IC=+0.0758, 2nd-half IC=+0.1358, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.61)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.070, Q3_mid=+0.117, Q4=+0.068, Q5_high_vol=+0.147

**`combo_rank_max__bar_body_rng_0__volatility_expansion_trend_vector`** (Lock IC=+0.1009, Sharpe=+0.1617)
- Admission: Train IC=+0.2418, Deflated=+0.2417, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.176 | 2016: +0.128 | 2017: +0.002 | 2018: +0.070 | 2019: +0.153 | 2020: +0.130 | 2021: +0.173 | 2022: +0.089 | 2023: +0.144 | 2024: +0.054 | 2025: +0.216 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.288 | 2016: -0.033 | 2017: +0.125 | 2018: +0.086 | 2019: +0.460 | 2020: +0.226 | 2021: +0.278 | 2022: +0.263 | 2023: +0.339 | 2024: +0.229 | 2025: +0.344 | 2026: -0.314
- IC CV=0.53, Neg years (linear/tail)=0/0 of 8, Half ratio=1.59, Recency ratio=2.76
- Early IC=+0.0360, Recent IC=+0.0992, 1st-half IC=+0.0772, 2nd-half IC=+0.1229, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.142, Q2=+0.079, Q3_mid=+0.134, Q4=+0.074, Q5_high_vol=+0.113

**`combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1161, Sharpe=+0.1600)
- Admission: Train IC=+0.2325, Deflated=+0.2317, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.123 | 2017: +0.038 | 2018: +0.089 | 2019: +0.201 | 2020: +0.122 | 2021: +0.157 | 2022: +0.119 | 2023: +0.188 | 2024: +0.045 | 2025: +0.171 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.103 | 2016: +0.114 | 2017: +0.179 | 2018: +0.308 | 2019: +0.241 | 2020: +0.103 | 2021: +0.354 | 2022: +0.184 | 2023: +0.307 | 2024: +0.188 | 2025: +0.210 | 2026: +0.063
- IC CV=0.47, Neg years (linear/tail)=0/0 of 8, Half ratio=1.22, Recency ratio=1.83
- Early IC=+0.0636, Recent IC=+0.1163, 1st-half IC=+0.1102, 2nd-half IC=+0.1340, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.138, Q3_mid=+0.091, Q4=+0.089, Q5_high_vol=+0.138

**`combo_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0739, Sharpe=+0.1559)
- Admission: Train IC=+0.1794, Deflated=+0.1795, IR=0.47, Mono=0.70, p=0.0008, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.085 | 2017: +0.025 | 2018: +0.082 | 2019: +0.204 | 2020: +0.113 | 2021: +0.094 | 2022: +0.099 | 2023: +0.167 | 2024: +0.080 | 2025: +0.093 | 2026: +0.055
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.121 | 2017: +0.156 | 2018: +0.212 | 2019: +0.310 | 2020: -0.065 | 2021: +0.245 | 2022: +0.253 | 2023: +0.308 | 2024: +0.155 | 2025: -0.035 | 2026: +0.022
- IC CV=0.48, Neg years (linear/tail)=0/1 of 8, Half ratio=1.20, Recency ratio=2.31
- Early IC=+0.0535, Recent IC=+0.1235, 1st-half IC=+0.1001, 2nd-half IC=+0.1197, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.119, Q2=+0.089, Q3_mid=+0.086, Q4=+0.108, Q5_high_vol=+0.133

**`combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1259, Sharpe=+0.1557)
- Admission: Train IC=+0.2356, Deflated=+0.2340, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.146 | 2016: +0.095 | 2017: +0.037 | 2018: +0.095 | 2019: +0.149 | 2020: +0.075 | 2021: +0.149 | 2022: +0.145 | 2023: +0.133 | 2024: +0.126 | 2025: +0.134 | 2026: +0.114
- Yearly Tail ICs:   2015: -0.069 | 2016: +0.234 | 2017: +0.082 | 2018: +0.290 | 2019: +0.320 | 2020: +0.160 | 2021: +0.235 | 2022: +0.298 | 2023: +0.339 | 2024: +0.340 | 2025: -0.069 | 2026: +0.277
- IC CV=0.34, Neg years (linear/tail)=0/0 of 8, Half ratio=1.64, Recency ratio=1.97
- Early IC=+0.0659, Recent IC=+0.1298, 1st-half IC=+0.0881, 2nd-half IC=+0.1447, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.011, Q2=+0.118, Q3_mid=+0.092, Q4=+0.110, Q5_high_vol=+0.207

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0717, Sharpe=+0.1416)
- Admission: Train IC=+0.2601, Deflated=+0.2594, IR=1.11, Mono=0.85, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.165 | 2016: +0.073 | 2017: +0.031 | 2018: +0.090 | 2019: +0.171 | 2020: +0.096 | 2021: +0.117 | 2022: +0.094 | 2023: +0.188 | 2024: +0.100 | 2025: +0.174 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.117 | 2017: +0.125 | 2018: +0.254 | 2019: +0.395 | 2020: +0.240 | 2021: +0.247 | 2022: +0.368 | 2023: +0.557 | 2024: +0.213 | 2025: +0.126 | 2026: -0.067
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.52, Recency ratio=2.38
- Early IC=+0.0605, Recent IC=+0.1442, 1st-half IC=+0.0851, 2nd-half IC=+0.1297, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.121, Q2=+0.098, Q3_mid=+0.120, Q4=+0.100, Q5_high_vol=+0.108

**`combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0673, Sharpe=+0.1332)
- Admission: Train IC=+0.2480, Deflated=+0.2489, IR=0.64, Mono=0.72, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.133 | 2016: +0.043 | 2017: +0.029 | 2018: +0.087 | 2019: +0.188 | 2020: +0.050 | 2021: +0.161 | 2022: +0.051 | 2023: +0.184 | 2024: +0.081 | 2025: +0.171 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.290 | 2016: -0.062 | 2017: -0.026 | 2018: +0.161 | 2019: +0.474 | 2020: +0.209 | 2021: +0.351 | 2022: +0.108 | 2023: +0.425 | 2024: +0.209 | 2025: +0.338 | 2026: -0.146
- IC CV=0.57, Neg years (linear/tail)=0/1 of 8, Half ratio=1.59, Recency ratio=2.30
- Early IC=+0.0572, Recent IC=+0.1314, 1st-half IC=+0.0796, 2nd-half IC=+0.1263, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.095, Q2=+0.092, Q3_mid=+0.134, Q4=+0.093, Q5_high_vol=+0.117

**`combo_mean__limit_down_proximity_early__impulse_bar_dominance`** (Lock IC=+0.1145, Sharpe=+0.1225)
- Admission: Train IC=+0.1840, Deflated=+0.1821, IR=0.51, Mono=0.68, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.173 | 2016: -0.027 | 2017: +0.006 | 2018: +0.074 | 2019: +0.112 | 2020: +0.070 | 2021: +0.132 | 2022: +0.148 | 2023: +0.088 | 2024: +0.093 | 2025: +0.122 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.062 | 2016: +0.053 | 2017: -0.022 | 2018: +0.124 | 2019: +0.381 | 2020: +0.067 | 2021: +0.276 | 2022: +0.084 | 2023: +0.144 | 2024: +0.260 | 2025: +0.041 | 2026: +0.172
- IC CV=0.45, Neg years (linear/tail)=0/1 of 8, Half ratio=1.80, Recency ratio=2.24
- Early IC=+0.0404, Recent IC=+0.0906, 1st-half IC=+0.0684, 2nd-half IC=+0.1230, Neg regimes=0/5
- Weak component: `impulse_bar_dominance` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.044, Q3_mid=+0.095, Q4=+0.110, Q5_high_vol=+0.125

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0770, Sharpe=+0.1170)
- Admission: Train IC=+0.2620, Deflated=+0.2622, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.139 | 2017: +0.004 | 2018: +0.138 | 2019: +0.196 | 2020: +0.123 | 2021: +0.105 | 2022: +0.109 | 2023: +0.168 | 2024: +0.066 | 2025: +0.136 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.139 | 2017: +0.122 | 2018: +0.348 | 2019: +0.425 | 2020: +0.119 | 2021: +0.230 | 2022: +0.288 | 2023: +0.539 | 2024: +0.093 | 2025: +0.213 | 2026: -0.056
- IC CV=0.49, Neg years (linear/tail)=0/0 of 8, Half ratio=1.03, Recency ratio=1.65
- Early IC=+0.0707, Recent IC=+0.1165, 1st-half IC=+0.1117, 2nd-half IC=+0.1152, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.150, Q2=+0.106, Q3_mid=+0.088, Q4=+0.110, Q5_high_vol=+0.125

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=+0.0838, Sharpe=+0.1021)
- Admission: Train IC=+0.2092, Deflated=+0.2091, IR=0.63, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.098 | 2017: +0.041 | 2018: +0.108 | 2019: +0.184 | 2020: +0.094 | 2021: +0.158 | 2022: +0.106 | 2023: +0.168 | 2024: +0.065 | 2025: +0.164 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.168 | 2016: +0.095 | 2017: +0.175 | 2018: +0.159 | 2019: +0.225 | 2020: +0.086 | 2021: +0.307 | 2022: +0.256 | 2023: +0.358 | 2024: +0.106 | 2025: +0.153 | 2026: +0.000
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.57
- Early IC=+0.0741, Recent IC=+0.1166, 1st-half IC=+0.0967, 2nd-half IC=+0.1316, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.097, Q3_mid=+0.107, Q4=+0.089, Q5_high_vol=+0.133

**`combo_mean__max_up_ret__bar_ret_0`** (Lock IC=+0.0838, Sharpe=+0.1021)
- Admission: Train IC=+0.2089, Deflated=+0.2087, IR=0.63, Mono=0.76, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.098 | 2017: +0.041 | 2018: +0.107 | 2019: +0.184 | 2020: +0.094 | 2021: +0.158 | 2022: +0.105 | 2023: +0.168 | 2024: +0.065 | 2025: +0.164 | 2026: -0.022
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.092 | 2017: +0.175 | 2018: +0.156 | 2019: +0.225 | 2020: +0.087 | 2021: +0.307 | 2022: +0.255 | 2023: +0.360 | 2024: +0.110 | 2025: +0.153 | 2026: +0.015
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.58
- Early IC=+0.0739, Recent IC=+0.1166, 1st-half IC=+0.0966, 2nd-half IC=+0.1315, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.097, Q3_mid=+0.107, Q4=+0.089, Q5_high_vol=+0.133

**`combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector`** (Lock IC=+0.0893, Sharpe=+0.0953)
- Admission: Train IC=+0.2003, Deflated=+0.2011, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.108 | 2016: +0.039 | 2017: +0.044 | 2018: +0.020 | 2019: +0.147 | 2020: +0.030 | 2021: +0.189 | 2022: +0.051 | 2023: +0.168 | 2024: +0.083 | 2025: +0.195 | 2026: -0.081
- Yearly Tail ICs:   2015: +0.140 | 2016: -0.052 | 2017: +0.154 | 2018: +0.072 | 2019: +0.454 | 2020: +0.082 | 2021: +0.219 | 2022: +0.152 | 2023: +0.304 | 2024: +0.151 | 2025: +0.284 | 2026: -0.313
- IC CV=0.68, Neg years (linear/tail)=0/0 of 8, Half ratio=2.47, Recency ratio=3.92
- Early IC=+0.0319, Recent IC=+0.1251, 1st-half IC=+0.0525, 2nd-half IC=+0.1299, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.077, Q3_mid=+0.139, Q4=+0.058, Q5_high_vol=+0.080

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0743, Sharpe=+0.0905)
- Admission: Train IC=+0.1561, Deflated=+0.1557, IR=0.66, Mono=0.73, p=0.0026, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.163 | 2017: +0.013 | 2018: +0.122 | 2019: +0.186 | 2020: +0.138 | 2021: +0.085 | 2022: +0.092 | 2023: +0.134 | 2024: +0.051 | 2025: +0.112 | 2026: +0.030
- Yearly Tail ICs:   2015: -0.098 | 2016: +0.328 | 2017: +0.115 | 2018: +0.023 | 2019: +0.258 | 2020: +0.173 | 2021: -0.104 | 2022: +0.361 | 2023: +0.394 | 2024: +0.159 | 2025: +0.091 | 2026: -0.148
- IC CV=0.50, Neg years (linear/tail)=0/1 of 8, Half ratio=0.88, Recency ratio=1.37
- Early IC=+0.0672, Recent IC=+0.0921, 1st-half IC=+0.1097, 2nd-half IC=+0.0968, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.100, Q3_mid=+0.064, Q4=+0.079, Q5_high_vol=+0.136

**`combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1015, Sharpe=+0.0872)
- Admission: Train IC=+0.2638, Deflated=+0.2625, IR=1.03, Mono=0.84, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.075 | 2017: +0.028 | 2018: +0.075 | 2019: +0.188 | 2020: +0.140 | 2021: +0.149 | 2022: +0.122 | 2023: +0.186 | 2024: +0.110 | 2025: +0.181 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.076 | 2016: +0.172 | 2017: +0.198 | 2018: +0.207 | 2019: +0.338 | 2020: +0.236 | 2021: +0.323 | 2022: +0.282 | 2023: +0.397 | 2024: +0.256 | 2025: +0.197 | 2026: -0.002
- IC CV=0.41, Neg years (linear/tail)=0/0 of 8, Half ratio=1.39, Recency ratio=2.89
- Early IC=+0.0512, Recent IC=+0.1476, 1st-half IC=+0.1056, 2nd-half IC=+0.1471, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.120, Q3_mid=+0.113, Q4=+0.120, Q5_high_vol=+0.153

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0948, Sharpe=+0.0510)
- Admission: Train IC=+0.2031, Deflated=+0.2023, IR=0.48, Mono=0.68, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.164 | 2017: +0.000 | 2018: +0.123 | 2019: +0.160 | 2020: +0.132 | 2021: +0.157 | 2022: +0.124 | 2023: +0.140 | 2024: +0.087 | 2025: +0.109 | 2026: +0.099
- Yearly Tail ICs:   2015: +0.087 | 2016: +0.159 | 2017: +0.088 | 2018: +0.303 | 2019: +0.342 | 2020: +0.042 | 2021: +0.401 | 2022: +0.055 | 2023: +0.173 | 2024: +0.182 | 2025: -0.037 | 2026: +0.052
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.36, Recency ratio=1.84
- Early IC=+0.0619, Recent IC=+0.1139, 1st-half IC=+0.0991, 2nd-half IC=+0.1350, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.63)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.067, Q3_mid=+0.093, Q4=+0.118, Q5_high_vol=+0.174

**`combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0768, Sharpe=+0.0395)
- Admission: Train IC=+0.2358, Deflated=+0.2362, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.106 | 2017: +0.002 | 2018: +0.113 | 2019: +0.207 | 2020: +0.141 | 2021: +0.122 | 2022: +0.081 | 2023: +0.169 | 2024: +0.074 | 2025: +0.135 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.042 | 2017: +0.041 | 2018: +0.143 | 2019: +0.375 | 2020: +0.225 | 2021: +0.278 | 2022: +0.275 | 2023: +0.459 | 2024: +0.222 | 2025: +0.217 | 2026: -0.077
- IC CV=0.52, Neg years (linear/tail)=0/0 of 8, Half ratio=1.08, Recency ratio=2.13
- Early IC=+0.0571, Recent IC=+0.1217, 1st-half IC=+0.1083, 2nd-half IC=+0.1170, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.143, Q2=+0.084, Q3_mid=+0.110, Q4=+0.098, Q5_high_vol=+0.142

**`combo_rank_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0930, Sharpe=+0.0368)
- Admission: Train IC=+0.2553, Deflated=+0.2560, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.097 | 2017: +0.024 | 2018: +0.126 | 2019: +0.194 | 2020: +0.112 | 2021: +0.133 | 2022: +0.103 | 2023: +0.174 | 2024: +0.071 | 2025: +0.164 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.342 | 2016: -0.030 | 2017: +0.140 | 2018: +0.196 | 2019: +0.482 | 2020: +0.137 | 2021: +0.288 | 2022: +0.129 | 2023: +0.502 | 2024: +0.185 | 2025: +0.246 | 2026: +0.149
- IC CV=0.42, Neg years (linear/tail)=0/0 of 8, Half ratio=1.13, Recency ratio=1.61
- Early IC=+0.0758, Recent IC=+0.1222, 1st-half IC=+0.1106, 2nd-half IC=+0.1254, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.161, Q2=+0.110, Q3_mid=+0.099, Q4=+0.101, Q5_high_vol=+0.140

**`combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0841, Sharpe=+0.0197)
- Admission: Train IC=+0.1865, Deflated=+0.1852, IR=0.55, Mono=0.69, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.071 | 2017: +0.034 | 2018: +0.079 | 2019: +0.133 | 2020: +0.100 | 2021: +0.173 | 2022: +0.146 | 2023: +0.147 | 2024: +0.088 | 2025: +0.141 | 2026: +0.031
- Yearly Tail ICs:   2015: -0.132 | 2016: +0.164 | 2017: +0.032 | 2018: +0.270 | 2019: +0.227 | 2020: -0.010 | 2021: +0.389 | 2022: +0.200 | 2023: +0.232 | 2024: +0.216 | 2025: +0.013 | 2026: -0.081
- IC CV=0.38, Neg years (linear/tail)=0/1 of 8, Half ratio=1.72, Recency ratio=2.07
- Early IC=+0.0569, Recent IC=+0.1176, 1st-half IC=+0.0853, 2nd-half IC=+0.1467, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.088, Q3_mid=+0.098, Q4=+0.103, Q5_high_vol=+0.170

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0785, Sharpe=+0.0183)
- Admission: Train IC=+0.1626, Deflated=+0.1625, IR=0.57, Mono=0.67, p=0.0016, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.189 | 2016: +0.122 | 2017: -0.010 | 2018: +0.119 | 2019: +0.146 | 2020: +0.141 | 2021: +0.148 | 2022: +0.145 | 2023: +0.095 | 2024: +0.077 | 2025: +0.122 | 2026: +0.036
- Yearly Tail ICs:   2015: -0.083 | 2016: +0.167 | 2017: +0.062 | 2018: +0.291 | 2019: +0.107 | 2020: +0.024 | 2021: +0.456 | 2022: +0.166 | 2023: +0.149 | 2024: +0.173 | 2025: -0.003 | 2026: -0.064
- IC CV=0.47, Neg years (linear/tail)=1/0 of 8, Half ratio=1.31, Recency ratio=1.59
- Early IC=+0.0542, Recent IC=+0.0861, 1st-half IC=+0.0983, 2nd-half IC=+0.1289, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.86)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.088, Q3_mid=+0.092, Q4=+0.127, Q5_high_vol=+0.144

**`combo_max__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1120, Sharpe=+0.0026)
- Admission: Train IC=+0.1892, Deflated=+0.1884, IR=0.56, Mono=0.70, p=0.0004, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.127 | 2017: +0.025 | 2018: +0.140 | 2019: +0.124 | 2020: +0.105 | 2021: +0.157 | 2022: +0.142 | 2023: +0.117 | 2024: +0.063 | 2025: +0.129 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.028 | 2016: +0.043 | 2017: +0.219 | 2018: +0.393 | 2019: +0.141 | 2020: +0.125 | 2021: +0.396 | 2022: +0.072 | 2023: +0.190 | 2024: +0.194 | 2025: +0.143 | 2026: +0.093
- IC CV=0.38, Neg years (linear/tail)=0/0 of 8, Half ratio=1.25, Recency ratio=1.09
- Early IC=+0.0824, Recent IC=+0.0898, 1st-half IC=+0.1008, 2nd-half IC=+0.1262, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.138, Q2=+0.106, Q3_mid=+0.072, Q4=+0.108, Q5_high_vol=+0.161

---

## 4b. Post-Discovery IC Decay Curve

Year-by-year OOS IC after training ends. Reveals whether alpha decays
immediately (overfit), within 1-2 years (short-lived alpha), or persists.

Decay types: **immediate** (Y1 ≤ 0), **fast** (Y2 ≤ 0), **gradual** (dies later), **persistent** (still alive).

### 300ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | Median | fast | +0.1244 | -0.0561 | -0.0561 | 1y |
| `combo_mean__volume_weighted_price_position__volume_surge_direction` | Median | fast | +0.1237 | -0.1205 | -0.1205 | 1y |
| `combo_rank_min__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | fast | +0.1178 | -0.1506 | -0.1506 | 1y |
| `combo_tri_max__volume_weighted_price_position__bar_body_rng_0__opening_drive_thrust_ratio` | Median | fast | +0.1109 | -0.1684 | -0.1684 | 1y |
| `combo_max__first_bar_sentiment__volume_surge_direction` | Median | fast | +0.1095 | -0.0761 | -0.0761 | 1y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | FP | fast | +0.1091 | -0.1852 | -0.1852 | 1y |
| `combo_min__opening_drive_thrust_ratio__volume_surge_direction` | Median | fast | +0.1087 | -0.0759 | -0.0759 | 1y |
| `volume_weighted_price_position` | Median | fast | +0.1077 | -0.1599 | -0.1599 | 1y |
| `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.1060 | -0.1949 | -0.1949 | 1y |
| `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.1049 | -0.2082 | -0.2082 | 1y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | fast | +0.1045 | -0.2082 | -0.2082 | 1y |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.1037 | -0.1580 | -0.1580 | 1y |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.1037 | -0.1580 | -0.1580 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_surge_direction` | TP | fast | +0.1033 | -0.0655 | -0.0655 | 1y |
| `combo_mean__volume_weighted_price_position__first_bar_sentiment` | Median | fast | +0.1003 | -0.1279 | -0.1279 | 1y |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | fast | +0.1000 | -0.1481 | -0.1481 | 1y |
| `combo_mean__opening_drive_thrust_ratio__volume_surge_direction` | Median | fast | +0.0991 | -0.1190 | -0.1190 | 1y |
| `combo_min__bar_body_rng_0__limit_down_proximity_early` | Median | persistent | +0.0982 | +0.0127 | +0.0127 | 1y |
| `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0982 | +0.0127 | +0.0127 | 1y |
| `combo_tri_mean__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | fast | +0.0981 | -0.1072 | -0.1072 | 1y |
| `combo_tri_mean__bar_ret_0__volume_weighted_price_position__bar_body_rng_0` | Median | fast | +0.0981 | -0.1072 | -0.1072 | 1y |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.0969 | -0.1968 | -0.1968 | 1y |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.0962 | +0.0468 | +0.0468 | 1y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0962 | +0.0468 | +0.0468 | 1y |
| `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.0958 | -0.1978 | -0.1978 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | fast | +0.0958 | -0.0206 | -0.0206 | 1y |
| `combo_max__volume_weighted_price_position__volume_surge_direction` | FP | fast | +0.0957 | -0.1478 | -0.1478 | 1y |
| `combo_rank_max__volume_weighted_price_position__volume_surge_direction` | FP | fast | +0.0956 | -0.1539 | -0.1539 | 1y |
| `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | fast | +0.0948 | -0.1679 | -0.1679 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.0945 | +0.0032 | +0.0032 | 1y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.0942 | -0.1429 | -0.1429 | 1y |
| `combo_tri_min__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | fast | +0.0938 | -0.0625 | -0.0625 | 1y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | FP | fast | +0.0925 | -0.1974 | -0.1974 | 1y |
| `combo_tri_max__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Median | fast | +0.0919 | -0.1402 | -0.1402 | 1y |
| `first_30min_return` | FP | fast | +0.0908 | -0.1874 | -0.1874 | 1y |
| `open_to_current_return` | FP | fast | +0.0908 | -0.1874 | -0.1874 | 1y |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0` | TP | persistent | +0.0907 | +0.0022 | +0.0022 | 1y |
| `combo_tri_max__max_up_ret__first_bar_return__bar_body_rng_0` | FP | fast | +0.0899 | -0.1476 | -0.1476 | 1y |
| `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0` | FP | fast | +0.0898 | -0.1476 | -0.1476 | 1y |
| `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | FP | fast | +0.0896 | -0.1590 | -0.1590 | 1y |
| `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position` | Median | fast | +0.0865 | -0.0972 | -0.0972 | 1y |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.0859 | -0.1751 | -0.1751 | 1y |
| `combo_min__bar_body_rng_0__volume_surge_direction` | Median | fast | +0.0845 | -0.0552 | -0.0552 | 1y |
| `combo_rank_max__max_up_ret__volume_surge_direction` | FP | fast | +0.0837 | -0.1470 | -0.1470 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction` | FP | fast | +0.0830 | -0.1358 | -0.1358 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | Median | fast | +0.0824 | -0.0083 | -0.0083 | 1y |
| `combo_mean__max_up_ret__volume_surge_direction` | FP | fast | +0.0822 | -0.1159 | -0.1159 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Median | fast | +0.0816 | -0.0708 | -0.0708 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Median | fast | +0.0814 | -0.0621 | -0.0621 | 1y |
| `combo_rank_max__first_bar_return__volume_surge_direction` | Median | fast | +0.0812 | -0.0880 | -0.0880 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Median | fast | +0.0811 | -0.0619 | -0.0619 | 1y |
| `combo_min__first_bar_return__volume_surge_direction` | Median | fast | +0.0778 | -0.0723 | -0.0723 | 1y |
| `combo_min__bar_ret_0__volume_surge_direction` | Median | fast | +0.0777 | -0.0739 | -0.0739 | 1y |
| `combo_max__max_up_ret__bar_ret_0` | FP | fast | +0.0776 | -0.1601 | -0.1601 | 1y |
| `combo_rank_max__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0767 | -0.1492 | -0.1492 | 1y |
| `combo_rank_max__max_up_ret__first_bar_return` | FP | fast | +0.0764 | -0.1597 | -0.1597 | 1y |
| `combo_rank_max__first_bar_return__bar_body_rng_0` | Median | fast | +0.0758 | -0.0901 | -0.0901 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | TP | fast | +0.0757 | -0.0446 | -0.0446 | 1y |
| `combo_max__first_bar_return__volume_surge_direction` | Median | fast | +0.0750 | -0.0872 | -0.0872 | 1y |
| `combo_max__max_up_ret__volume_surge_direction` | FP | fast | +0.0750 | -0.1448 | -0.1448 | 1y |
| `combo_max__bar_ret_0__bar_body_rng_0` | Median | fast | +0.0750 | -0.0788 | -0.0788 | 1y |
| `combo_rank_max__first_bar_return__opening_drive_thrust_ratio` | FP | fast | +0.0747 | -0.1386 | -0.1386 | 1y |
| `combo_sig_product__star50_limit_proximity_early__opening_drive_thrust_ratio` | Median | persistent | +0.0743 | +0.0631 | +0.0631 | ∞ |
| `combo_sig_product__bar_ret_0__bar_body_rng_0` | Median | fast | +0.0733 | -0.0623 | -0.0623 | 1y |
| `combo_max__bar_ret_0__opening_drive_thrust_ratio` | FP | fast | +0.0729 | -0.1500 | -0.1500 | 1y |
| `combo_max__first_bar_return__opening_drive_thrust_ratio` | FP | fast | +0.0729 | -0.1505 | -0.1505 | 1y |
| `combo_tri_median__star50_limit_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Median | fast | +0.0724 | -0.0586 | -0.0586 | 1y |
| `bar_body_rng_0` | Median | fast | +0.0721 | -0.0623 | -0.0623 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | Median | fast | +0.0717 | -0.0530 | -0.0530 | 1y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | FP | fast | +0.0711 | -0.1230 | -0.1230 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Median | fast | +0.0708 | -0.0535 | -0.0535 | 1y |
| `combo_rank_min__bar_body_rng_0__opening_drive_thrust_ratio` | Median | fast | +0.0701 | -0.0935 | -0.0935 | 1y |
| `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0` | FP | fast | +0.0699 | -0.0987 | -0.0987 | 1y |
| `combo_tri_median__max_up_ret__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.0689 | -0.1391 | -0.1391 | 1y |
| `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position` | FP | fast | +0.0687 | -0.1392 | -0.1392 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | TP | fast | +0.0686 | -0.0825 | -0.0825 | 1y |
| `combo_min__max_up_ret__volume_surge_direction` | Median | fast | +0.0673 | -0.0609 | -0.0609 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0666 | -0.1119 | -0.1119 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | fast | +0.0657 | -0.0650 | -0.0650 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0652 | +0.0466 | +0.0466 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Median | persistent | +0.0624 | +0.0147 | +0.0147 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Median | persistent | +0.0624 | +0.0147 | +0.0147 | 1y |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | Median | fast | +0.0618 | -0.0109 | -0.0109 | 1y |
| `combo_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | Median | fast | +0.0618 | -0.0109 | -0.0109 | 1y |
| `combo_tri_median__star50_limit_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Median | fast | +0.0611 | -0.0563 | -0.0563 | 1y |
| `combo_tri_median__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | Median | fast | +0.0609 | -0.0563 | -0.0563 | 1y |
| `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.0598 | -0.1497 | -0.1497 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | fast | +0.0589 | -0.0276 | -0.0276 | 1y |
| `combo_mean__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0569 | -0.1658 | -0.1658 | 1y |
| `combo_rank_min__max_up_ret__volume_surge_direction` | Median | fast | +0.0567 | -0.0651 | -0.0651 | 1y |
| `first_bar_return` | Median | fast | +0.0554 | -0.0827 | -0.0827 | 1y |
| `combo_mean__first_bar_return__first_bar_sentiment` | Median | fast | +0.0554 | -0.0827 | -0.0827 | 1y |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | FP | fast | +0.0553 | -0.1845 | -0.1845 | 1y |
| `combo_min__first_bar_return__bar_body_rng_0` | Median | fast | +0.0540 | -0.0618 | -0.0618 | 1y |
| `combo_mean__max_up_ret__bar_body_rng_0` | FP | fast | +0.0539 | -0.1137 | -0.1137 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | fast | +0.0527 | -0.0140 | -0.0140 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Median | fast | +0.0500 | -0.0513 | -0.0513 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | Median | fast | +0.0498 | -0.0515 | -0.0515 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | Median | fast | +0.0486 | -0.0535 | -0.0535 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_ret_0__opening_drive_thrust_ratio` | Median | fast | +0.0485 | -0.0065 | -0.0065 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | Median | fast | +0.0467 | -0.0313 | -0.0313 | 1y |
| `combo_sig_product__first_bar_return__volume_weighted_price_position` | FP | fast | +0.0461 | -0.0904 | -0.0904 | 1y |
| `combo_ratio__rbreaker_buy_setup_proximity_early__volume_concentration` | TP | persistent | +0.0442 | +0.0707 | +0.0707 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio` | FP | fast | +0.0439 | -0.1119 | -0.1119 | 1y |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | FP | fast | +0.0438 | -0.1087 | -0.1087 | 1y |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | FP | fast | +0.0437 | -0.1087 | -0.1087 | 1y |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0436 | -0.1637 | -0.1637 | 1y |
| `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio` | FP | fast | +0.0436 | -0.1119 | -0.1119 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | Median | fast | +0.0419 | -0.0169 | -0.0169 | 1y |
| `combo_ratio__first_bar_return__volume_surge_direction` | FP | fast | +0.0417 | -0.0939 | -0.0939 | 1y |
| `combo_max__max_up_ret__first_bar_sentiment` | FP | fast | +0.0380 | -0.1327 | -0.1327 | 1y |
| `combo_min__max_up_ret__first_bar_sentiment` | FP | fast | +0.0343 | -0.0842 | -0.0842 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | Median | persistent | +0.0338 | +0.0153 | +0.0153 | 1y |
| `max_up_ret` | FP | fast | +0.0327 | -0.1524 | -0.1524 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0317 | -0.0714 | -0.0714 | 1y |
| `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early` | FP | fast | +0.0256 | -0.1056 | -0.1056 | 1y |
| `combo_min__max_up_ret__bar_ret_0` | FP | fast | +0.0224 | -0.0906 | -0.0906 | 1y |
| `combo_diff__max_up_ret__early_vwap_acceleration` | FP | fast | +0.0218 | -0.0859 | -0.0859 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | FP | fast | +0.0216 | -0.0774 | -0.0774 | 1y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | FP | fast | +0.0207 | -0.0951 | -0.0951 | 1y |
| `combo_sig_product__max_up_ret__opening_drive_thrust_ratio` | FP | fast | +0.0191 | -0.1068 | -0.1068 | 1y |
| `combo_rel_diff__max_up_ret__early_vwap_acceleration` | FP | fast | +0.0145 | -0.0880 | -0.0880 | 1y |
| `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio` | FP | fast | +0.0039 | -0.0842 | -0.0842 | ∞ |
| `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0` | FP | immediate | -0.0003 | -0.1319 | -0.1319 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | Median | immediate | -0.0086 | +0.0735 | +0.0735 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=111, gradual=0, persistent=12

**FP decay trajectories:**

- `combo_tri_median__smooth_momentum_structure__max_up_ret__bar_ret_0`: Y1:-0.000 → Y2:-0.132
- `combo_sig_product__bar_ret_0__opening_drive_thrust_ratio`: Y1:+0.004 → Y2:-0.084
- `combo_rel_diff__max_up_ret__early_vwap_acceleration`: Y1:+0.015 → Y2:-0.088
- `combo_sig_product__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.019 → Y2:-0.107
- `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.021 → Y2:-0.095
- `combo_min__max_up_ret__bar_body_rng_0`: Y1:+0.022 → Y2:-0.077
- `combo_diff__max_up_ret__early_vwap_acceleration`: Y1:+0.022 → Y2:-0.086
- `combo_min__max_up_ret__bar_ret_0`: Y1:+0.022 → Y2:-0.091
- `combo_min__volume_weighted_price_position__double_bottom_bull_flag_early`: Y1:+0.026 → Y2:-0.106
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.032 → Y2:-0.071
- `max_up_ret`: Y1:+0.033 → Y2:-0.152
- `combo_min__max_up_ret__first_bar_sentiment`: Y1:+0.034 → Y2:-0.084
- `combo_max__max_up_ret__first_bar_sentiment`: Y1:+0.038 → Y2:-0.133
- `combo_ratio__first_bar_return__volume_surge_direction`: Y1:+0.042 → Y2:-0.094
- `combo_tri_min__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`: Y1:+0.044 → Y2:-0.112
- `combo_tri_median__smooth_momentum_structure__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.044 → Y2:-0.164
- `combo_ratio__bar_ret_0__volume_weighted_price_position`: Y1:+0.044 → Y2:-0.109
- `combo_ratio__first_bar_return__volume_weighted_price_position`: Y1:+0.044 → Y2:-0.109
- `combo_tri_min__max_up_ret__first_bar_return__opening_drive_thrust_ratio`: Y1:+0.044 → Y2:-0.112
- `combo_sig_product__first_bar_return__volume_weighted_price_position`: Y1:+0.046 → Y2:-0.090
- `combo_mean__max_up_ret__bar_body_rng_0`: Y1:+0.054 → Y2:-0.114
- `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`: Y1:+0.055 → Y2:-0.184
- `combo_mean__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.057 → Y2:-0.166
- `combo_tri_median__smooth_momentum_structure__bar_ret_0__volume_weighted_price_position`: Y1:+0.060 → Y2:-0.150
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.067 → Y2:-0.112
- `combo_tri_median__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.069 → Y2:-0.139
- `combo_tri_median__max_up_ret__bar_ret_0__volume_weighted_price_position`: Y1:+0.069 → Y2:-0.139
- `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Y1:+0.070 → Y2:-0.099
- `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment`: Y1:+0.071 → Y2:-0.123
- `combo_max__first_bar_return__opening_drive_thrust_ratio`: Y1:+0.073 → Y2:-0.150
- `combo_max__bar_ret_0__opening_drive_thrust_ratio`: Y1:+0.073 → Y2:-0.150
- `combo_rank_max__first_bar_return__opening_drive_thrust_ratio`: Y1:+0.075 → Y2:-0.139
- `combo_max__max_up_ret__volume_surge_direction`: Y1:+0.075 → Y2:-0.145
- `combo_rank_max__max_up_ret__first_bar_return`: Y1:+0.076 → Y2:-0.160
- `combo_rank_max__max_up_ret__opening_drive_thrust_ratio`: Y1:+0.077 → Y2:-0.149
- `combo_max__max_up_ret__bar_ret_0`: Y1:+0.078 → Y2:-0.160
- `combo_mean__max_up_ret__volume_surge_direction`: Y1:+0.082 → Y2:-0.116
- `combo_rank_max__opening_drive_thrust_ratio__volume_surge_direction`: Y1:+0.083 → Y2:-0.136
- `combo_rank_max__max_up_ret__volume_surge_direction`: Y1:+0.084 → Y2:-0.147
- `combo_rank_max__bar_ret_0__volume_weighted_price_position`: Y1:+0.086 → Y2:-0.175
- `combo_tri_max__max_up_ret__bar_ret_0__opening_drive_thrust_ratio`: Y1:+0.090 → Y2:-0.159
- `combo_tri_max__max_up_ret__bar_ret_0__bar_body_rng_0`: Y1:+0.090 → Y2:-0.148
- `combo_tri_max__max_up_ret__first_bar_return__bar_body_rng_0`: Y1:+0.090 → Y2:-0.148
- `first_30min_return`: Y1:+0.091 → Y2:-0.187
- `open_to_current_return`: Y1:+0.091 → Y2:-0.187
- `combo_rank_max__max_up_ret__volume_weighted_price_position`: Y1:+0.092 → Y2:-0.197
- `combo_tri_min__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.094 → Y2:-0.143
- `combo_tri_mean__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.095 → Y2:-0.168
- `combo_rank_max__volume_weighted_price_position__volume_surge_direction`: Y1:+0.096 → Y2:-0.154
- `combo_max__volume_weighted_price_position__volume_surge_direction`: Y1:+0.096 → Y2:-0.148
- `combo_rank_max__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.096 → Y2:-0.198
- `combo_tri_max__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.097 → Y2:-0.197
- `combo_tri_mean__bar_ret_0__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.104 → Y2:-0.158
- `combo_tri_mean__first_bar_return__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.104 → Y2:-0.158
- `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`: Y1:+0.105 → Y2:-0.208
- `combo_tri_max__max_up_ret__bar_ret_0__volume_weighted_price_position`: Y1:+0.105 → Y2:-0.208
- `combo_tri_max__max_up_ret__volume_weighted_price_position__opening_drive_thrust_ratio`: Y1:+0.106 → Y2:-0.195
- `combo_mean__max_up_ret__volume_weighted_price_position`: Y1:+0.109 → Y2:-0.185

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_sig_product__volatility_expansion_trend_vector__max_down_ret` | Median | fast | +0.1941 | -0.0734 | -0.0734 | 1y |
| `morning_volume_weighted_momentum` | Median | fast | +0.1651 | -0.0906 | -0.0906 | 1y |
| `first_30min_return` | Median | fast | +0.1639 | -0.1128 | -0.1128 | 1y |
| `open_to_current_return` | Median | fast | +0.1639 | -0.1128 | -0.1128 | 1y |
| `combo_min__max_up_ret__close_vs_open_range` | Median | fast | +0.1593 | -0.0747 | -0.0747 | 1y |
| `combo_min__close_vs_open_range__first_bar_sentiment` | TP | fast | +0.1555 | -0.0329 | -0.0329 | 1y |
| `volatility_expansion_trend_vector` | Median | fast | +0.1545 | -0.0850 | -0.0850 | 1y |
| `combo_rank_max__volatility_expansion_trend_vector__max_down_ret` | Median | fast | +0.1545 | -0.0684 | -0.0684 | 1y |
| `combo_rank_max__net_volume_flow__max_down_ret` | TP | fast | +0.1541 | -0.0519 | -0.0519 | 1y |
| `combo_rank_min__max_up_ret__close_vs_open_range` | Median | fast | +0.1536 | -0.0692 | -0.0692 | 1y |
| `combo_max__close_vs_open_range__max_down_ret` | Median | fast | +0.1508 | -0.0675 | -0.0675 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.1499 | +0.0917 | +0.0917 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | fast | +0.1492 | -0.0818 | -0.0818 | 1y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.1483 | +0.0404 | +0.0404 | 1y |
| `combo_rank_min__volatility_expansion_trend_vector__close_vs_open_range` | Median | fast | +0.1477 | -0.0748 | -0.0748 | 1y |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | Median | fast | +0.1465 | -0.1032 | -0.1032 | 1y |
| `combo_mean__volatility_expansion_trend_vector__max_down_ret` | Median | fast | +0.1442 | -0.0187 | -0.0187 | 1y |
| `combo_max__close_vs_open_range__early_body_momentum` | Median | fast | +0.1436 | -0.0943 | -0.0943 | 1y |
| `combo_tri_median__max_up_ret__net_volume_flow__body_size_progression` | Median | fast | +0.1433 | -0.0918 | -0.0918 | 1y |
| `combo_min__close_vs_open_range__first_bar_return` | Median | persistent | +0.1433 | +0.0030 | +0.0030 | 1y |
| `combo_mean__volatility_expansion_trend_vector__first_bar_sentiment` | Median | fast | +0.1429 | -0.0518 | -0.0518 | 1y |
| `combo_rank_max__net_volume_flow__close_vs_open_range` | Median | fast | +0.1427 | -0.0672 | -0.0672 | 1y |
| `combo_min__volatility_expansion_trend_vector__max_down_ret` | Median | persistent | +0.1426 | +0.0237 | +0.0237 | 1y |
| `combo_min__volatility_expansion_trend_vector__first_bar_sentiment` | Median | fast | +0.1424 | -0.0356 | -0.0356 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1416 | +0.0781 | +0.0781 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1413 | +0.0748 | +0.0748 | ∞ |
| `combo_min__first_bar_sentiment__early_body_momentum` | Median | fast | +0.1408 | -0.0460 | -0.0460 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.1407 | +0.0488 | +0.0488 | 1y |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1405 | +0.1029 | +0.1029 | ∞ |
| `combo_min__net_volume_flow__close_vs_open_range` | Median | fast | +0.1403 | -0.0664 | -0.0664 | 1y |
| `combo_sig_product__net_volume_flow__max_down_ret` | Median | fast | +0.1401 | -0.0452 | -0.0452 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1390 | +0.0377 | +0.0377 | 1y |
| `combo_rank_min__volatility_expansion_trend_vector__max_down_ret` | Median | persistent | +0.1379 | +0.0221 | +0.0221 | 1y |
| `combo_min__first_bar_return__max_down_ret` | TP | persistent | +0.1378 | +0.0120 | +0.0120 | 1y |
| `combo_min__bar_ret_0__max_down_ret` | TP | persistent | +0.1377 | +0.0116 | +0.0116 | 1y |
| `combo_max__net_volume_flow__max_down_ret` | Median | fast | +0.1366 | -0.0614 | -0.0614 | 1y |
| `combo_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.1362 | +0.0869 | +0.0869 | ∞ |
| `combo_mean__first_bar_sentiment__max_down_ret` | TP | persistent | +0.1348 | +0.0248 | +0.0248 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | Median | persistent | +0.1346 | +0.0049 | +0.0049 | 1y |
| `combo_mean__net_volume_flow__max_down_ret` | Median | fast | +0.1330 | -0.0044 | -0.0044 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | fast | +0.1327 | -0.0711 | -0.0711 | 1y |
| `vwap_close_divergence_trend` | Median | fast | +0.1327 | -0.0940 | -0.0940 | 1y |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1323 | +0.0857 | +0.0857 | ∞ |
| `combo_rank_min__high_low_sequence_momentum__max_down_ret` | Median | persistent | +0.1323 | +0.0272 | +0.0272 | 1y |
| `combo_mean__first_bar_return__max_down_ret` | TP | persistent | +0.1320 | +0.0123 | +0.0123 | 1y |
| `combo_min__max_up_ret__trend_bar_close_consistency` | Median | fast | +0.1318 | -0.1093 | -0.1093 | 1y |
| `combo_max__high_low_sequence_momentum__max_down_ret` | Median | fast | +0.1309 | -0.0543 | -0.0543 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.1309 | +0.0883 | +0.0883 | ∞ |
| `max_down_ret` | TP | persistent | +0.1287 | +0.0305 | +0.0305 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Median | persistent | +0.1282 | +0.0596 | +0.0596 | 1y |
| `combo_tri_mean__max_up_ret__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | fast | +0.1269 | -0.0965 | -0.0965 | 1y |
| `combo_tri_mean__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | TP | persistent | +0.1264 | +0.0207 | +0.0207 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1260 | +0.0780 | +0.0780 | ∞ |
| `combo_mean__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1259 | +0.1051 | +0.1051 | ∞ |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | Median | fast | +0.1256 | -0.0406 | -0.0406 | 1y |
| `combo_max__early_body_momentum__bar_ret_0` | Median | fast | +0.1256 | -0.1186 | -0.1186 | 1y |
| `combo_sig_product__high_low_sequence_momentum__first_bar_return` | Median | fast | +0.1255 | -0.1226 | -0.1226 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | Median | persistent | +0.1253 | +0.0030 | +0.0030 | 1y |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | TP | fast | +0.1252 | -0.0261 | -0.0261 | 1y |
| `combo_rank_max__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.1251 | +0.0642 | +0.0642 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__net_volume_flow__volume_weighted_momentum_acceleration` | Median | fast | +0.1251 | -0.0396 | -0.0396 | 1y |
| `combo_mean__net_volume_flow__first_bar_sentiment` | Median | fast | +0.1244 | -0.0349 | -0.0349 | 1y |
| `combo_min__net_volume_flow__first_bar_return` | Median | fast | +0.1240 | -0.0004 | -0.0004 | 1y |
| `combo_rank_min__first_bar_return__max_down_ret` | TP | persistent | +0.1239 | +0.0065 | +0.0065 | 1y |
| `combo_rank_max__early_body_momentum__bar_ret_0` | Median | fast | +0.1239 | -0.1216 | -0.1216 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1232 | +0.0366 | +0.0366 | 1y |
| `combo_rank_min__net_volume_flow__first_bar_return` | Median | persistent | +0.1229 | +0.0199 | +0.0199 | 1y |
| `combo_min__trend_bar_close_consistency__first_bar_return` | Median | fast | +0.1227 | -0.0131 | -0.0131 | 1y |
| `combo_min__trend_bar_close_consistency__bar_ret_0` | Median | fast | +0.1226 | -0.0130 | -0.0130 | 1y |
| `combo_tri_max__star50_limit_proximity_early__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | persistent | +0.1222 | +0.0298 | +0.0298 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__trend_day_regime_conviction` | Median | fast | +0.1217 | -0.0555 | -0.0555 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | persistent | +0.1216 | +0.0449 | +0.0449 | 1y |
| `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.1199 | +0.0080 | +0.0080 | 1y |
| `combo_mean__close_vs_open_range__bar_ret_0` | Median | fast | +0.1198 | -0.0391 | -0.0391 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__trend_bar_close_consistency__body_size_progression` | Median | fast | +0.1198 | -0.1238 | -0.1238 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1196 | +0.0802 | +0.0802 | ∞ |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | Median | fast | +0.1194 | -0.0961 | -0.0961 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1192 | +0.0805 | +0.0805 | ∞ |
| `combo_tri_median__max_up_ret__smooth_momentum_structure__net_volume_flow` | Median | fast | +0.1192 | -0.0658 | -0.0658 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | fast | +0.1192 | -0.0517 | -0.0517 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | Median | fast | +0.1191 | -0.0307 | -0.0307 | 1y |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | Median | fast | +0.1188 | -0.0520 | -0.0520 | 1y |
| `combo_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1187 | +0.0462 | +0.0462 | 1y |
| `combo_min__trend_day_regime_conviction__first_bar_sentiment` | Median | fast | +0.1180 | -0.0503 | -0.0503 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | Median | persistent | +0.1179 | +0.0511 | +0.0511 | 1y |
| `combo_max__close_vs_open_range__first_bar_return` | Median | fast | +0.1175 | -0.0906 | -0.0906 | 1y |
| `combo_mean__trend_bar_close_consistency__bar_ret_0` | Median | fast | +0.1175 | -0.0641 | -0.0641 | 1y |
| `combo_min__opening_drive_thrust_ratio__high_low_sequence_momentum` | Median | fast | +0.1170 | -0.0455 | -0.0455 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__high_low_sequence_momentum` | Median | fast | +0.1168 | -0.0518 | -0.0518 | 1y |
| `num_up_bars` | Median | fast | +0.1166 | -0.0474 | -0.0474 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.1166 | +0.0962 | +0.0962 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | fast | +0.1159 | -0.0672 | -0.0672 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.1158 | +0.0713 | +0.0713 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | Median | fast | +0.1149 | -0.0402 | -0.0402 | 1y |
| `combo_rank_max__bar_ret_0__max_down_ret` | TP | persistent | +0.1134 | +0.0323 | +0.0323 | 1y |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1132 | +0.1514 | +0.1514 | ∞ |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.1130 | +0.1000 | +0.1000 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | Median | persistent | +0.1128 | +0.0051 | +0.0051 | 1y |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Median | persistent | +0.1128 | +0.0021 | +0.0021 | 1y |
| `combo_min__opening_drive_thrust_ratio__bar_ret_0` | Median | persistent | +0.1127 | +0.0049 | +0.0049 | 1y |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1121 | -0.0266 | -0.0266 | 1y |
| `combo_max__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.1115 | +0.0770 | +0.0770 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1111 | +0.0241 | +0.0241 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.1100 | +0.0760 | +0.0760 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__trend_bar_close_consistency__volatility_expansion_trend_vector` | Median | fast | +0.1093 | -0.0504 | -0.0504 | 1y |
| `combo_max__opening_drive_thrust_ratio__net_volume_flow` | Median | fast | +0.1087 | -0.0062 | -0.0062 | 1y |
| `combo_sig_product__net_volume_flow__first_bar_return` | Median | fast | +0.1085 | -0.1006 | -0.1006 | 1y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.1083 | +0.1990 | +0.1990 | ∞ |
| `combo_sig_product__net_volume_flow__bar_ret_0` | Median | fast | +0.1079 | -0.0996 | -0.0996 | 1y |
| `combo_rank_max__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.1079 | +0.0814 | +0.0814 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.1059 | +0.0666 | +0.0666 | ∞ |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Median | fast | +0.1057 | -0.0442 | -0.0442 | 1y |
| `combo_min__first_bar_sentiment__first_bar_return` | Median | fast | +0.1049 | -0.0093 | -0.0093 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.1040 | +0.0046 | +0.0046 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1026 | -0.0685 | -0.0685 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | Median | persistent | +0.1016 | +0.0064 | +0.0064 | 1y |
| `range_progression_trend` | FP | fast | +0.1010 | -0.1829 | -0.1829 | 1y |
| `combo_max__bar_ret_0__max_down_ret` | Median | persistent | +0.1008 | +0.0047 | +0.0047 | 1y |
| `combo_rank_max__max_up_ret__net_volume_flow` | Median | fast | +0.1008 | -0.0170 | -0.0170 | 1y |
| `combo_sig_product__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0999 | +0.1857 | +0.1857 | ∞ |
| `bar_body_rng_0` | Median | persistent | +0.0995 | +0.0133 | +0.0133 | 1y |
| `combo_max__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.0993 | +0.0492 | +0.0492 | 1y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0983 | +0.0010 | +0.0010 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | fast | +0.0978 | -0.0539 | -0.0539 | 1y |
| `combo_rank_max__max_up_ret__bar_ret_0` | Median | fast | +0.0977 | -0.0663 | -0.0663 | 1y |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | TP | fast | +0.0973 | -0.0114 | -0.0114 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__body_size_progression` | Median | persistent | +0.0971 | +0.0518 | +0.0518 | ∞ |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0971 | +0.1049 | +0.1049 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.0971 | -0.0103 | -0.0103 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Median | persistent | +0.0965 | +0.0098 | +0.0098 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | Median | persistent | +0.0965 | +0.0955 | +0.0955 | ∞ |
| `combo_max__max_up_ret__early_body_momentum` | Median | fast | +0.0962 | -0.0587 | -0.0587 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | Median | persistent | +0.0959 | +0.0555 | +0.0555 | ∞ |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0953 | +0.0159 | +0.0159 | 1y |
| `combo_sig_product__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0949 | +0.2061 | +0.2061 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | Median | persistent | +0.0944 | +0.0858 | +0.0858 | ∞ |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | Median | persistent | +0.0944 | +0.0037 | +0.0037 | 1y |
| `vwap_trend_channel_slope` | Median | fast | +0.0941 | -0.0312 | -0.0312 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0935 | +0.0791 | +0.0791 | ∞ |
| `always_in_trend_persistence` | FP | fast | +0.0929 | -0.1600 | -0.1600 | 1y |
| `first_bar_return` | Median | fast | +0.0924 | -0.0114 | -0.0114 | 1y |
| `combo_mean__first_bar_sentiment__bar_ret_0` | Median | fast | +0.0924 | -0.0114 | -0.0114 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0924 | -0.0814 | -0.0814 | 1y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0917 | +0.0324 | +0.0324 | 1y |
| `combo_max__trend_bar_close_consistency__first_bar_sentiment` | Median | fast | +0.0914 | -0.0975 | -0.0975 | 1y |
| `early_order_flow_imbalance` | FP | fast | +0.0913 | -0.1345 | -0.1345 | 1y |
| `combo_rank_max__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.0909 | +0.0586 | +0.0586 | ∞ |
| `combo_sig_product__first_bar_sentiment__bar_ret_0` | Median | fast | +0.0904 | -0.0098 | -0.0098 | 1y |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | Median | fast | +0.0902 | -0.0098 | -0.0098 | 1y |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Median | fast | +0.0900 | -0.0387 | -0.0387 | 1y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | Median | fast | +0.0890 | -0.0006 | -0.0006 | 1y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0888 | +0.1751 | +0.1751 | ∞ |
| `combo_mean__max_up_ret__first_bar_sentiment` | Median | fast | +0.0884 | -0.0300 | -0.0300 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | Median | persistent | +0.0884 | +0.0635 | +0.0635 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__trend_day_regime_conviction` | Median | fast | +0.0870 | -0.0502 | -0.0502 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | Median | fast | +0.0861 | -0.0127 | -0.0127 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__net_volume_flow` | Median | persistent | +0.0860 | +0.1133 | +0.1133 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | Median | fast | +0.0860 | -0.0622 | -0.0622 | 1y |
| `combo_rank_min__max_up_ret__bar_ret_0` | Median | fast | +0.0854 | -0.0011 | -0.0011 | 1y |
| `combo_rank_min__max_up_ret__first_bar_return` | Median | fast | +0.0854 | -0.0011 | -0.0011 | 1y |
| `combo_sig_product__star50_limit_proximity_early__close_vs_open_range` | Median | persistent | +0.0847 | +0.0862 | +0.0862 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | Median | persistent | +0.0822 | +0.0993 | +0.0993 | ∞ |
| `max_up_ret` | Median | fast | +0.0801 | -0.0291 | -0.0291 | 1y |
| `combo_rank_max__net_volume_flow__first_bar_sentiment` | Median | fast | +0.0799 | -0.0367 | -0.0367 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | Median | persistent | +0.0798 | +0.0736 | +0.0736 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.0795 | -0.0153 | -0.0153 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | Median | fast | +0.0794 | -0.0143 | -0.0143 | 1y |
| `combo_sig_product__max_up_ret__early_body_momentum` | Median | fast | +0.0790 | -0.0071 | -0.0071 | 1y |
| `combo_sig_product__star50_limit_proximity_early__early_body_momentum` | Median | persistent | +0.0789 | +0.0770 | +0.0770 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0784 | +0.1421 | +0.1421 | ∞ |
| `combo_mean__max_up_ret__first_bar_return` | Median | fast | +0.0772 | -0.0329 | -0.0329 | 1y |
| `combo_mean__max_up_ret__bar_ret_0` | Median | fast | +0.0772 | -0.0329 | -0.0329 | 1y |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | TP | fast | +0.0770 | -0.0213 | -0.0213 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0763 | +0.0498 | +0.0498 | ∞ |
| `combo_sig_product__max_up_ret__high_low_sequence_momentum` | Median | fast | +0.0758 | -0.0133 | -0.0133 | 1y |
| `combo_max__max_up_ret__first_bar_sentiment` | Median | fast | +0.0739 | -0.0361 | -0.0361 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | Median | persistent | +0.0737 | +0.0366 | +0.0366 | 1y |
| `combo_diff__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | TP | persistent | +0.0737 | +0.0374 | +0.0374 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | Median | fast | +0.0734 | -0.0792 | -0.0792 | 1y |
| `combo_sig_product__max_up_ret__bar_ret_0` | Median | fast | +0.0731 | -0.0782 | -0.0782 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0725 | +0.0204 | +0.0204 | 1y |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0723 | +0.0187 | +0.0187 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__volatility_expansion_trend_vector` | Median | fast | +0.0697 | -0.0297 | -0.0297 | 1y |
| `combo_rel_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0685 | +0.0220 | +0.0220 | 1y |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0634 | +0.1849 | +0.1849 | ∞ |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0625 | +0.0619 | +0.0619 | ∞ |
| `combo_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0608 | +0.0387 | +0.0387 | ∞ |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0602 | +0.1848 | +0.1848 | ∞ |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | fast | +0.0601 | -0.0041 | -0.0041 | 1y |
| `combo_sig_product__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0578 | +0.1809 | +0.1809 | ∞ |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | Median | persistent | +0.0567 | +0.0084 | +0.0084 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | Median | persistent | +0.0556 | +0.0391 | +0.0391 | ∞ |
| `combo_sig_product__max_up_ret__body_size_progression` | TP | persistent | +0.0541 | +0.0398 | +0.0398 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.0502 | +0.0030 | +0.0030 | 1y |
| `combo_diff__max_up_ret__smooth_momentum_structure` | Median | persistent | +0.0488 | +0.0179 | +0.0179 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | TP | persistent | +0.0481 | +0.0760 | +0.0760 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | TP | persistent | +0.0469 | +0.1123 | +0.1123 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | Median | persistent | +0.0452 | +0.0809 | +0.0809 | ∞ |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0389 | +0.2312 | +0.2312 | ∞ |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0211 | +0.0805 | +0.0805 | ∞ |
| `combo_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0206 | +0.0793 | +0.0793 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0186 | +0.2613 | +0.2613 | ∞ |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0159 | +0.2573 | +0.2573 | ∞ |
| `combo_clamp_diff__max_up_ret__late_bar_momentum` | Median | persistent | +0.0156 | +0.0876 | +0.0876 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_day_regime_conviction` | Median | immediate | -0.0453 | +0.1128 | +0.1128 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | immediate | -0.0548 | +0.1878 | +0.1878 | ∞ |

**Decay distribution**: immediate=2, fast(1-2y)=102, gradual=0, persistent=102

**FP decay trajectories:**

- `early_order_flow_imbalance`: Y1:+0.091 → Y2:-0.135
- `always_in_trend_persistence`: Y1:+0.093 → Y2:-0.160
- `range_progression_trend`: Y1:+0.101 → Y2:-0.183

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2+ IC (partial) | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `trend_bar_close_consistency` | Median | fast | +0.2224 | -0.1362 | -0.1362 | 1y |
| `combo_rank_max__bar_body_rng_0__volatility_expansion_trend_vector` | TP | fast | +0.2159 | -0.0741 | -0.0741 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.2153 | +0.0608 | +0.0608 | 1y |
| `volatility_expansion_trend_vector` | TP | fast | +0.2122 | -0.0952 | -0.0952 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.2114 | +0.0678 | +0.0678 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.2067 | +0.0594 | +0.0594 | 1y |
| `combo_max__bar_body_rng_0__volatility_expansion_trend_vector` | Median | fast | +0.2059 | -0.0835 | -0.0835 | 1y |
| `net_volume_flow` | Median | fast | +0.2054 | -0.0663 | -0.0663 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.2054 | +0.0334 | +0.0334 | 1y |
| `combo_min__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | fast | +0.2047 | -0.0565 | -0.0565 | 1y |
| `combo_max__bar_ret_0__volatility_expansion_trend_vector` | Median | fast | +0.2047 | -0.0797 | -0.0797 | 1y |
| `combo_rank_min__max_up_ret__volatility_expansion_trend_vector` | Median | fast | +0.2015 | -0.0871 | -0.0871 | 1y |
| `combo_mean__bar_body_rng_0__volatility_expansion_trend_vector` | Median | fast | +0.1985 | -0.0378 | -0.0378 | 1y |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1976 | -0.0830 | -0.0830 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1963 | -0.0913 | -0.0913 | 1y |
| `combo_diff__max_up_ret__demark_setup_reversal_early` | TP | fast | +0.1962 | -0.0369 | -0.0369 | 1y |
| `combo_z_sum__volume_weighted_price_position__volatility_expansion_trend_vector` | TP | fast | +0.1950 | -0.0810 | -0.0810 | 1y |
| `combo_diff__bar_ret_0__demark_setup_reversal_early` | TP | persistent | +0.1939 | +0.0293 | +0.0293 | 1y |
| `combo_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1939 | +0.0305 | +0.0305 | 1y |
| `combo_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1936 | +0.0433 | +0.0433 | 1y |
| `combo_max__bar_body_rng_0__impulse_bar_dominance` | TP | fast | +0.1927 | -0.0238 | -0.0238 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1927 | +0.0637 | +0.0637 | 1y |
| `combo_z_sum__impulse_bar_dominance__volatility_expansion_trend_vector` | Median | fast | +0.1923 | -0.1024 | -0.1024 | 1y |
| `combo_max__max_up_ret__volatility_expansion_trend_vector` | Median | fast | +0.1910 | -0.0955 | -0.0955 | 1y |
| `combo_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | fast | +0.1908 | -0.0067 | -0.0067 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.1904 | +0.0494 | +0.0494 | 1y |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | Median | fast | +0.1902 | -0.0310 | -0.0310 | 1y |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1894 | +0.0801 | +0.0801 | 1y |
| `combo_max__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | Median | fast | +0.1888 | -0.0980 | -0.0980 | 1y |
| `combo_rank_max__max_up_ret__bar_body_rng_0` | Median | fast | +0.1854 | -0.0560 | -0.0560 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__demark_setup_reversal_early` | TP | fast | +0.1843 | -0.0180 | -0.0180 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1826 | +0.0526 | +0.0526 | 1y |
| `combo_rel_diff__max_up_ret__demark_setup_reversal_early` | Median | fast | +0.1819 | -0.0040 | -0.0040 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1813 | +0.0531 | +0.0531 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | fast | +0.1813 | -0.0105 | -0.0105 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1808 | +0.0149 | +0.0149 | 1y |
| `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early` | Median | persistent | +0.1798 | +0.0561 | +0.0561 | 1y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1798 | +0.0536 | +0.0536 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1788 | +0.0501 | +0.0501 | 1y |
| `combo_sig_product__impulse_bar_dominance__volatility_expansion_trend_vector` | Median | fast | +0.1786 | -0.1119 | -0.1119 | 1y |
| `combo_mean__bar_body_rng_0__impulse_bar_dominance` | TP | fast | +0.1785 | -0.0232 | -0.0232 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__bar_body_rng_0` | Median | fast | +0.1780 | -0.0447 | -0.0447 | 1y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1777 | -0.0708 | -0.0708 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1776 | +0.0306 | +0.0306 | 1y |
| `combo_max__max_up_ret__bar_body_rng_0` | Median | fast | +0.1772 | -0.0720 | -0.0720 | 1y |
| `combo_max__max_up_ret__volume_weighted_price_position` | Median | fast | +0.1770 | -0.0804 | -0.0804 | 1y |
| `combo_mean__max_up_ret__star50_limit_proximity_early` | TP | persistent | +0.1769 | +0.0816 | +0.0816 | 1y |
| `combo_sig_product__max_up_ret__bar_body_rng_0` | TP | fast | +0.1761 | -0.0143 | -0.0143 | 1y |
| `combo_rank_min__bar_body_rng_0__volatility_expansion_trend_vector` | TP | persistent | +0.1759 | +0.0086 | +0.0086 | 1y |
| `combo_tri_max__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Median | fast | +0.1756 | -0.0756 | -0.0756 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.1750 | +0.1164 | +0.1164 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1750 | +0.1164 | +0.1164 | ∞ |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | fast | +0.1739 | -0.0629 | -0.0629 | 1y |
| `combo_mean__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1737 | +0.0897 | +0.0897 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | Median | fast | +0.1730 | -0.0660 | -0.0660 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1730 | +0.0733 | +0.0733 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1725 | -0.0618 | -0.0618 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1720 | +0.1097 | +0.1097 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__first_bar_return` | Median | fast | +0.1719 | -0.0696 | -0.0696 | 1y |
| `combo_rel_diff__first_bar_return__demark_setup_reversal_early` | TP | persistent | +0.1717 | +0.0479 | +0.0479 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__volume_weighted_price_position` | TP | fast | +0.1717 | -0.0766 | -0.0766 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1715 | -0.0557 | -0.0557 | 1y |
| `combo_tri_median__max_up_ret__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1711 | +0.0414 | +0.0414 | 1y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1704 | +0.0712 | +0.0712 | 1y |
| `combo_rank_min__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1696 | +0.1445 | +0.1445 | ∞ |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1696 | +0.1445 | +0.1445 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1692 | +0.1248 | +0.1248 | ∞ |
| `combo_min__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | persistent | +0.1690 | +0.1012 | +0.1012 | ∞ |
| `combo_max__opening_drive_thrust_ratio__impulse_bar_dominance` | TP | fast | +0.1676 | -0.0116 | -0.0116 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1675 | +0.0833 | +0.0833 | 1y |
| `combo_sig_product__volume_weighted_price_position__volatility_expansion_trend_vector` | Median | fast | +0.1672 | -0.0446 | -0.0446 | 1y |
| `combo_tri_max__max_up_ret__first_bar_sentiment__first_bar_return` | Median | fast | +0.1671 | -0.0839 | -0.0839 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1664 | +0.0547 | +0.0547 | 1y |
| `opening_drive_thrust_ratio` | TP | fast | +0.1663 | -0.0464 | -0.0464 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | fast | +0.1656 | -0.0271 | -0.0271 | 1y |
| `combo_rank_min__max_up_ret__impulse_bar_dominance` | TP | fast | +0.1654 | -0.1150 | -0.1150 | 1y |
| `combo_mean__max_up_ret__first_bar_return` | TP | fast | +0.1642 | -0.0230 | -0.0230 | 1y |
| `combo_mean__max_up_ret__bar_ret_0` | TP | fast | +0.1642 | -0.0224 | -0.0224 | 1y |
| `combo_min__limit_down_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1641 | +0.0895 | +0.0895 | ∞ |
| `combo_min__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1641 | +0.0895 | +0.0895 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1638 | +0.0711 | +0.0711 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.1637 | +0.0055 | +0.0055 | 1y |
| `max_up_ret` | Median | fast | +0.1636 | -0.0753 | -0.0753 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1632 | +0.1003 | +0.1003 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1632 | +0.0999 | +0.0999 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1623 | +0.1019 | +0.1019 | ∞ |
| `combo_max__opening_drive_thrust_ratio__bar_body_rng_0` | Median | fast | +0.1623 | -0.0243 | -0.0243 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_return` | TP | persistent | +0.1613 | +0.0724 | +0.0724 | 1y |
| `combo_tri_mean__star50_limit_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1612 | +0.0821 | +0.0821 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1611 | +0.0844 | +0.0844 | ∞ |
| `combo_clamp_diff__rbreaker_sell_setup_proximity_early__demark_setup_reversal_early` | TP | persistent | +0.1608 | +0.1238 | +0.1238 | ∞ |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1603 | +0.0921 | +0.0921 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1594 | +0.0841 | +0.0841 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | persistent | +0.1574 | +0.0877 | +0.0877 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.1568 | +0.0663 | +0.0663 | 1y |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1564 | +0.1047 | +0.1047 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1558 | +0.1234 | +0.1234 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1548 | +0.1304 | +0.1304 | ∞ |
| `combo_tri_min__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1544 | +0.1201 | +0.1201 | ∞ |
| `combo_mean__bar_ret_0__limit_down_proximity_early` | TP | persistent | +0.1543 | +0.1126 | +0.1126 | ∞ |
| `combo_mean__first_bar_return__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.1541 | +0.1122 | +0.1122 | ∞ |
| `combo_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1539 | +0.1045 | +0.1045 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1537 | +0.0163 | +0.0163 | 1y |
| `combo_sig_product__max_up_ret__first_bar_return` | TP | fast | +0.1531 | -0.0087 | -0.0087 | 1y |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | fast | +0.1528 | -0.0086 | -0.0086 | 1y |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1526 | +0.0972 | +0.0972 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1518 | +0.1112 | +0.1112 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | Median | fast | +0.1518 | -0.0171 | -0.0171 | 1y |
| `combo_rank_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1517 | +0.1183 | +0.1183 | ∞ |
| `combo_max__first_bar_return__impulse_bar_dominance` | TP | fast | +0.1512 | -0.0491 | -0.0491 | 1y |
| `combo_rank_min__max_up_ret__volume_weighted_price_position` | TP | fast | +0.1488 | -0.0468 | -0.0468 | 1y |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Median | fast | +0.1477 | -0.0170 | -0.0170 | 1y |
| `combo_min__max_up_ret__bar_body_rng_0` | Median | persistent | +0.1469 | +0.0273 | +0.0273 | 1y |
| `combo_mean__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1468 | +0.1163 | +0.1163 | ∞ |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1456 | +0.1168 | +0.1168 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1433 | +0.1123 | +0.1123 | ∞ |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__bar_body_rng_0` | Median | persistent | +0.1430 | +0.0231 | +0.0231 | 1y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1425 | +0.1075 | +0.1075 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1420 | +0.1368 | +0.1368 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1411 | +0.0306 | +0.0306 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1407 | +0.1104 | +0.1104 | ∞ |
| `combo_max__max_up_ret__impulse_bar_dominance` | Median | fast | +0.1401 | -0.0762 | -0.0762 | 1y |
| `combo_tri_max__max_up_ret__star50_limit_proximity_early__first_bar_return` | Median | persistent | +0.1393 | +0.0156 | +0.0156 | 1y |
| `combo_max__first_bar_sentiment__bar_ret_0` | TP | fast | +0.1392 | -0.0091 | -0.0091 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__bar_body_rng_0` | Median | fast | +0.1384 | -0.1047 | -0.1047 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1363 | +0.0022 | +0.0022 | 1y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_sentiment` | TP | fast | +0.1354 | -0.0071 | -0.0071 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | Median | persistent | +0.1353 | +0.1417 | +0.1417 | ∞ |
| `combo_mean__first_bar_return__volume_weighted_price_position` | TP | persistent | +0.1352 | +0.0002 | +0.0002 | 1y |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1348 | +0.1140 | +0.1140 | ∞ |
| `combo_rank_min__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1347 | +0.1375 | +0.1375 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1339 | +0.1144 | +0.1144 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1336 | +0.0869 | +0.0869 | ∞ |
| `combo_min__opening_drive_thrust_ratio__impulse_bar_dominance` | TP | fast | +0.1335 | -0.0835 | -0.0835 | 1y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | Median | persistent | +0.1334 | +0.1142 | +0.1142 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | Median | persistent | +0.1330 | +0.0153 | +0.0153 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.1326 | +0.0543 | +0.0543 | 1y |
| `combo_rank_max__max_up_ret__star50_limit_proximity_early` | Median | persistent | +0.1325 | +0.0600 | +0.0600 | 1y |
| `combo_min__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1313 | +0.1302 | +0.1302 | ∞ |
| `combo_tri_min__max_up_ret__first_bar_sentiment__bar_body_rng_0` | Median | persistent | +0.1307 | +0.0261 | +0.0261 | 1y |
| `combo_tri_min__opening_drive_thrust_ratio__first_bar_sentiment__first_bar_return` | TP | persistent | +0.1306 | +0.0018 | +0.0018 | 1y |
| `combo_rank_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1302 | +0.1210 | +0.1210 | ∞ |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1291 | +0.1272 | +0.1272 | ∞ |
| `combo_max__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.1289 | +0.1087 | +0.1087 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | Median | fast | +0.1288 | -0.1070 | -0.1070 | 1y |
| `combo_min__limit_down_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1282 | +0.0717 | +0.0717 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1279 | +0.0962 | +0.0962 | ∞ |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | Median | fast | +0.1264 | -0.0029 | -0.0029 | 1y |
| `combo_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early` | TP | persistent | +0.1256 | +0.0991 | +0.0991 | ∞ |
| `combo_ratio__star50_limit_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1247 | +0.1472 | +0.1472 | ∞ |
| `combo_min__limit_down_proximity_early__volume_weighted_price_position` | TP | persistent | +0.1240 | +0.1313 | +0.1313 | ∞ |
| `combo_sig_product__first_bar_return__demark_setup_reversal_early` | Median | persistent | +0.1232 | +0.0322 | +0.0322 | 1y |
| `first_bar_return` | TP | persistent | +0.1228 | +0.0226 | +0.0226 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | Median | fast | +0.1227 | -0.0816 | -0.0816 | 1y |
| `combo_mean__limit_down_proximity_early__impulse_bar_dominance` | TP | persistent | +0.1223 | +0.0985 | +0.0985 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.1222 | +0.0679 | +0.0679 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.1221 | +0.1221 | +0.1221 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1220 | +0.0355 | +0.0355 | 1y |
| `combo_sig_product__first_bar_sentiment__first_bar_return` | TP | persistent | +0.1201 | +0.0219 | +0.0219 | 1y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.1167 | +0.0941 | +0.0941 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.1147 | +0.0815 | +0.0815 | ∞ |
| `combo_ratio__bar_ret_0__volume_weighted_price_position` | TP | persistent | +0.1143 | +0.0098 | +0.0098 | 1y |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | Median | persistent | +0.1141 | +0.0804 | +0.0804 | ∞ |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | TP | persistent | +0.1121 | +0.0299 | +0.0299 | 1y |
| `combo_rank_min__first_bar_sentiment__first_bar_return` | TP | persistent | +0.1114 | +0.0453 | +0.0453 | 1y |
| `combo_max__bar_body_rng_0__limit_down_proximity_early` | TP | persistent | +0.1107 | +0.0893 | +0.0893 | ∞ |
| `combo_tri_max__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.1092 | +0.0987 | +0.0987 | ∞ |
| `combo_mean__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.1081 | +0.1384 | +0.1384 | ∞ |
| `combo_mean__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1078 | +0.1691 | +0.1691 | ∞ |
| `combo_min__first_bar_sentiment__bar_ret_0` | TP | persistent | +0.1027 | +0.0181 | +0.0181 | 1y |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1014 | +0.1299 | +0.1299 | ∞ |
| `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1012 | +0.1304 | +0.1304 | ∞ |
| `combo_tri_min__star50_limit_proximity_early__yesterday_early_momentum__yesterday_first_30min_return` | TP | persistent | +0.0964 | +0.1495 | +0.1495 | ∞ |
| `combo_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.0926 | +0.0552 | +0.0552 | ∞ |
| `combo_tri_median__star50_limit_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | Median | persistent | +0.0829 | +0.1006 | +0.1006 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_sentiment` | Median | fast | +0.0828 | -0.0177 | -0.0177 | 1y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0804 | +0.1430 | +0.1430 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.0791 | +0.1555 | +0.1555 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__yesterday_early_vwap_dev__yesterday_first_30min_return` | TP | persistent | +0.0758 | +0.1169 | +0.1169 | ∞ |
| `combo_max__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.0682 | +0.1549 | +0.1549 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__yesterday_first_30min_return` | Median | persistent | +0.0655 | +0.1661 | +0.1661 | ∞ |
| `combo_z_sum__yesterday_first_30min_return__yesterday_early_trend` | Median | persistent | +0.0478 | +0.0413 | +0.0413 | ∞ |
| `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector` | FP | immediate | -0.0273 | +0.0202 | +0.0202 | ∞ |

**Decay distribution**: immediate=1, fast(1-2y)=62, gradual=0, persistent=120

**FP decay trajectories:**

- `combo_abs_diff__max_up_ret__volatility_expansion_trend_vector`: Y1:-0.027 → Y2:+0.020

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 300ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.736±0.037 | 0.713±0.035 | 72% | WEAK |
| ic_ir | 0.635±0.125 | 0.551±0.076 | 42% | USEFUL |
| p_value | 0.001±0.004 | 0.001±0.001 | 22% | USEFUL |
| max_corr | 0.900±0.133 | 0.877±0.200 | 70% | WEAK |
| deflated_ic | 0.199±0.033 | 0.206±0.025 | 57% | WEAK |
| overall_ic | 0.199±0.033 | 0.206±0.025 | 58% | WEAK |
| raw_ic | 0.085±0.011 | 0.086±0.014 | 94% | USELESS |

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.728±0.009 | 0.728±0.042 | 11% | USEFUL |
| ic_ir | 0.563±0.014 | 0.643±0.130 | 6% | USEFUL |
| p_value | 0.000±0.000 | 0.001±0.002 | 0% | USEFUL |
| max_corr | 0.898±0.067 | 0.877±0.127 | 17% | USEFUL |
| deflated_ic | 0.210±0.019 | 0.197±0.035 | 32% | USEFUL |
| overall_ic | 0.210±0.019 | 0.198±0.035 | 32% | USEFUL |
| raw_ic | 0.087±0.009 | 0.115±0.018 | 20% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 8/20 top rejects are profitable (40%)

- `combo_mean__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449
- `combo_mean__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1799, Lock IC=+0.0714, Sharpe=+0.4449

**B2 Rolling Guard**: 3/20 top rejects are profitable (15%)

- `combo_rel_diff__rbreaker_sell_setup_proximity_early__bar_vol_0`: Train IC=+0.1479, Lock IC=+0.0962, Sharpe=+0.8491
- `combo_rel_diff__rbreaker_sell_setup_proximity_early__first_bar_volume`: Train IC=+0.1479, Lock IC=+0.0962, Sharpe=+0.8491
- `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.2310, Lock IC=+0.0219, Sharpe=+0.0687

**B4 Correlation Gate**: 6/20 top rejects are profitable (30%)

- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_return__bar_body_rng_0`: Train IC=+0.2333, Lock IC=+0.0559, Sharpe=+0.3783
- `combo_tri_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783
- `combo_tri_z_mean__star50_limit_proximity_early__bar_ret_0__bar_body_rng_0`: Train IC=+0.2332, Lock IC=+0.0557, Sharpe=+0.3783

### 500ETF — `single`

**7-Year Jackknife**: 12/20 top rejects are profitable (60%)

- `combo_tri_min__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_day_regime_conviction`: Train IC=+0.2211, Lock IC=+0.0921, Sharpe=+0.5717
- `combo_mean__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340
- `combo_z_sum__star50_limit_proximity_early__first_bar_return`: Train IC=+0.2191, Lock IC=+0.1123, Sharpe=+0.4340

**B2 Rolling Guard**: 2/20 top rejects are profitable (10%)

- `combo_clamp_diff__early_late_momentum_divergence__first_bar_sentiment`: Train IC=+0.1855, Lock IC=+0.0659, Sharpe=+0.3681
- `combo_sig_product__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.2239, Lock IC=+0.0978, Sharpe=+0.0194

**Temporal Validation Gate**: 1/20 top rejects are profitable (5%)

- `combo_clamp_diff__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.2743, Lock IC=+0.0624, Sharpe=+0.6830

**B3 Composite Floor**: 1/20 top rejects are profitable (5%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.1847, Lock IC=+0.0017, Sharpe=+0.3201

**B6 Yearly IC CV Gate**: 6/6 top rejects are profitable (100%)

- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1680, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352

**B4 Correlation Gate**: 1/20 top rejects are profitable (5%)

- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Sharpe=+0.3545

### 159915ETF — `single`

**7-Year Jackknife**: 14/20 top rejects are profitable (70%)

- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2018, Lock IC=+0.1126, Sharpe=+1.5724
- `combo_max__rbreaker_sell_setup_proximity_early__limit_down_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.9095
- `combo_max__rbreaker_sell_setup_proximity_early__rbreaker_buy_setup_proximity_early`: Train IC=+0.2122, Lock IC=+0.1352, Sharpe=+0.9095

**B2 Rolling Guard**: 16/20 top rejects are profitable (80%)

- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_rank_max__bar_body_rng_0__volume_weighted_price_position`: Train IC=+0.1830, Lock IC=+0.0792, Sharpe=+0.8691
- `combo_rel_diff__limit_down_proximity_early__demark_setup_reversal_early`: Train IC=+0.1712, Lock IC=+0.1393, Sharpe=+0.7803

**Temporal Validation Gate**: 11/20 top rejects are profitable (55%)

- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1734, Lock IC=+0.1528, Sharpe=+1.7449
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1734, Lock IC=+0.1528, Sharpe=+1.7449
- `combo_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1987, Lock IC=+0.1447, Sharpe=+1.1411

**BH-FDR Gate**: 1/4 top rejects are profitable (25%)

- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0396, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor**: 19/20 top rejects are profitable (95%)

- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2227, Lock IC=+0.1193, Sharpe=+1.3049
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2417, Lock IC=+0.1107, Sharpe=+1.2956
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2268, Lock IC=+0.1295, Sharpe=+1.2146

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890
- `combo_rank_min__star50_limit_proximity_early__volume_weighted_price_position`: Train IC=+0.3025, Lock IC=+0.1381, Sharpe=+1.4675

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 960 | 78 | 29 | 24 | 25 | 37% | 32% |
| B2 Rolling Guard | 115 | 78 | 41 | 28 | 9 | 53% | 12% |
| Temporal Validation Gate | 134 | 78 | 27 | 41 | 10 | 35% | 13% |
| BH-FDR Gate | 2 | 2 | 1 | 1 | 0 | 50% | 0% |
| B6 Yearly IC CV Gate | 21 | 21 | 18 | 3 | 0 | 86% | 0% |
| B6 Quality Gate | 1 | 1 | 0 | 1 | 0 | 0% | 0% |
| B4 Correlation Gate | 201 | 78 | 37 | 27 | 14 | 47% | 18% |

**7-Year Jackknife** — top TP casualties:
- `combo_ratio__limit_down_proximity_early__volume_concentration`: Train IC=+0.1720, Lock IC=+0.1235, Sharpe=+0.9843
- `combo_rank_min__volume_weighted_momentum_acceleration__max_up_ret`: Train IC=+0.0558, Lock IC=+0.0636, Sharpe=+0.8404
- `combo_diff__star50_limit_proximity_early__opening_drive_thrust_ratio`: Train IC=+0.0002, Lock IC=+0.0825, Sharpe=+0.8131

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1699 | 78 | 36 | 21 | 21 | 46% | 27% |
| B2 Rolling Guard | 207 | 78 | 31 | 38 | 9 | 40% | 12% |
| Temporal Validation Gate | 222 | 78 | 22 | 36 | 20 | 28% | 26% |
| BH-FDR Gate | 6 | 6 | 1 | 5 | 0 | 17% | 0% |
| B3 Composite Floor | 52 | 52 | 5 | 26 | 21 | 10% | 40% |
| B6 Yearly IC CV Gate | 6 | 6 | 0 | 0 | 6 | 0% | 100% |
| B6 Temporal Stability Gate | 40 | 40 | 0 | 40 | 0 | 0% | 0% |
| B6 Quality Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 598 | 78 | 0 | 62 | 16 | 0% | 21% |

**7-Year Jackknife** — top TP casualties:
- `combo_tri_max__star50_limit_proximity_early__volume_weighted_momentum_acceleration__volatility_expansion_trend_vector`: Train IC=+0.0506, Lock IC=+0.0831, Sharpe=+0.7879
- `combo_min__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=-0.0027, Lock IC=+0.0733, Sharpe=+0.7176
- `combo_min__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=-0.0090, Lock IC=+0.0732, Sharpe=+0.7176

**Temporal Validation Gate** — top TP casualties:
- `combo_clamp_diff__smooth_momentum_structure__volatility_expansion_trend_vector`: Train IC=+0.2743, Lock IC=+0.0624, Sharpe=+0.6830
- `combo_sig_product__volume_weighted_momentum_acceleration__bar_ret_0`: Train IC=+0.1935, Lock IC=+0.0636, Sharpe=+0.4836
- `combo_sig_product__volume_weighted_momentum_acceleration__first_bar_return`: Train IC=+0.1935, Lock IC=+0.0636, Sharpe=+0.4836

**B3 Composite Floor** — top TP casualties:
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443
- `combo_tri_mean__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1539, Lock IC=+0.0750, Sharpe=+0.5443

**B6 Yearly IC CV Gate** — top TP casualties:
- `combo_tri_min__smooth_momentum_structure__star50_limit_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1680, Lock IC=+0.0263, Sharpe=+0.6290
- `combo_tri_min__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352
- `combo_tri_min__opening_auction_imbalance__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1814, Lock IC=+0.0154, Sharpe=+0.4352

**B4 Correlation Gate** — top TP casualties:
- `combo_mean__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.2154, Lock IC=+0.1027, Sharpe=+0.3967
- `combo_z_sum__rbreaker_sell_setup_proximity_early__trend_day_regime_conviction`: Train IC=+0.2154, Lock IC=+0.1027, Sharpe=+0.3967
- `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`: Train IC=+0.2741, Lock IC=+0.0880, Sharpe=+0.3545

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1089 | 78 | 21 | 22 | 35 | 27% | 45% |
| B2 Rolling Guard | 172 | 78 | 19 | 18 | 41 | 24% | 53% |
| Temporal Validation Gate | 58 | 58 | 6 | 16 | 36 | 10% | 62% |
| BH-FDR Gate | 4 | 4 | 0 | 3 | 1 | 0% | 25% |
| B3 Composite Floor | 101 | 78 | 1 | 17 | 60 | 1% | 77% |
| B6 Yearly IC CV Gate | 1 | 1 | 1 | 0 | 0 | 100% | 0% |
| B4 Correlation Gate | 279 | 78 | 0 | 6 | 72 | 0% | 92% |

**7-Year Jackknife** — top TP casualties:
- `yesterday_illiquidity_amihud`: Train IC=+0.0550, Lock IC=+0.1294, Sharpe=+1.6004
- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2018, Lock IC=+0.1126, Sharpe=+1.5724
- `combo_product__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.0540, Lock IC=+0.0216, Sharpe=+1.2443

**B2 Rolling Guard** — top TP casualties:
- `yesterday_day_vwap_dev`: Train IC=+0.1185, Lock IC=+0.1197, Sharpe=+1.1213
- `combo_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537
- `combo_z_diff__star50_limit_proximity_early__late_bar_momentum`: Train IC=+0.1691, Lock IC=+0.1114, Sharpe=+1.0537

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1734, Lock IC=+0.1528, Sharpe=+1.7449
- `combo_rel_diff__yesterday_pm_return__rbreaker_buy_setup_proximity_early`: Train IC=+0.1734, Lock IC=+0.1528, Sharpe=+1.7449
- `combo_diff__yesterday_pm_return__limit_down_proximity_early`: Train IC=+0.1987, Lock IC=+0.1447, Sharpe=+1.1411

**BH-FDR Gate** — top TP casualties:
- `combo_sig_product__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.0396, Lock IC=+0.1184, Sharpe=+0.1847

**B3 Composite Floor** — top TP casualties:
- `combo_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2227, Lock IC=+0.1193, Sharpe=+1.3049
- `combo_tri_min__max_up_ret__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2417, Lock IC=+0.1107, Sharpe=+1.2956
- `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.2268, Lock IC=+0.1295, Sharpe=+1.2146

**B4 Correlation Gate** — top TP casualties:
- `combo_tri_z_mean__star50_limit_proximity_early__first_bar_sentiment__bar_body_rng_0`: Train IC=+0.3147, Lock IC=+0.1361, Sharpe=+1.5184
- `combo_rank_min__first_bar_sentiment__bar_ret_0`: Train IC=+0.1483, Lock IC=+0.0759, Sharpe=+1.4912
- `combo_tri_z_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.3215, Lock IC=+0.1346, Sharpe=+1.4890

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (134 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 106 | 50 | 16 | 0 | 34 | 32% | 0% |
| recency_ratio >= 2.5 (late-concentrated) | 24 | 24 | 12 | 0 | 12 | 50% | 0% |

### 500ETF — `single` (222 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 218 | 50 | 0 | 9 | 41 | 0% | 18% |
| recency_ratio >= 2.5 (late-concentrated) | 4 | 4 | 3 | 0 | 1 | 75% | 0% |

### 159915ETF — `single` (58 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 40 | 40 | 6 | 25 | 9 | 15% | 62% |
| recency_ratio >= 2.5 (late-concentrated) | 14 | 14 | 0 | 10 | 4 | 0% | 71% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__bar_body_rng_0__impulse_bar_dominance`: Train IC=+0.0957, Lock IC=+0.0822, Sharpe=+0.7710
- `combo_max__limit_down_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1344, Lock IC=+0.1171, Sharpe=+0.5989
- `combo_max__rbreaker_buy_setup_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1344, Lock IC=+0.1171, Sharpe=+0.5989
- `vwap_slope_intraday`: Train IC=+0.0934, Lock IC=+0.0337, Sharpe=+0.2590
- `combo_rank_max__limit_down_proximity_early__volatility_expansion_trend_vector`: Train IC=+0.1337, Lock IC=+0.1190, Sharpe=+0.2452

---

## 7. Root Cause Synthesis & Training-Only Fixes

### 300ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `weak_link_cv`: FP is lower (d=-1.24). Threshold 0.930 → 84% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-1.19). Threshold 0.031 → 85% accuracy.
- `half_ratio`: FP is higher (d=+0.93). Threshold 1.067 → 90% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/58
- Decaying signal (half ratio < 0.3): 0/58
- Weak component (CV > 2.0): 0/58
- Regime-dependent (≥2 negative regimes): 0/58

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `half_ratio`: FP is higher (d=+5.29). Threshold 1.204 → 98% accuracy.
- `ic_std_across_regimes`: FP is lower (d=-4.09). Threshold 0.091 → 93% accuracy.
- `recency_ratio`: FP is higher (d=+3.19). Threshold 0.941 → 98% accuracy.
- `n_negative_regimes`: FP is lower (d=-1.52). Threshold 1.000 → 93% accuracy.
- `ic_cv`: FP is lower (d=-0.66). Threshold 0.736 → 93% accuracy.

**Failure pattern counts:**
- Era-concentrated (IC CV > 1.5): 0/3
- Decaying signal (half ratio < 0.3): 0/3
- Weak component (CV > 2.0): 0/3
- Regime-dependent (≥2 negative regimes): 0/3

---

## 8. Primitive Component FP Rate (Cross-ETF)

Per-primitive FP rate across all combo features. Flag primitives with FP rate ≥ 80% AND n ≥ 5.

| Primitive | FP | TP | Total | FP Rate | Flag |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `early_vwap_acceleration` | 2 | 0 | 2 | 100% |  |
| `volume_surge_direction` | 7 | 1 | 8 | 88% | ⚠ TOXIC |
| `smooth_momentum_structure` | 3 | 1 | 4 | 75% |  |
| `volume_weighted_price_position` | 24 | 13 | 37 | 65% |  |
| `bar_ret_0` | 14 | 14 | 28 | 50% |  |
| `max_up_ret` | 35 | 36 | 71 | 49% |  |
| `opening_drive_thrust_ratio` | 23 | 49 | 72 | 32% |  |
| `first_bar_return` | 13 | 32 | 45 | 29% |  |
| `bar_body_rng_0` | 5 | 32 | 37 | 14% |  |
| `first_bar_sentiment` | 3 | 26 | 29 | 10% |  |
| `volatility_expansion_trend_vector` | 1 | 17 | 18 | 6% |  |
| `rbreaker_sell_setup_proximity_early` | 2 | 57 | 59 | 3% |  |
| `star50_limit_proximity_early` | 0 | 52 | 52 | 0% |  |
| `yesterday_first_30min_return` | 0 | 7 | 7 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 7 | 7 | 0% |  |
| `yesterday_early_vwap_dev` | 0 | 2 | 2 | 0% |  |
| `early_late_momentum_divergence` | 0 | 2 | 2 | 0% |  |
| `body_size_progression` | 0 | 9 | 9 | 0% |  |
| `demark_setup_reversal_early` | 0 | 7 | 7 | 0% |  |
| `net_volume_flow` | 0 | 6 | 6 | 0% |  |
| `limit_down_proximity_early` | 0 | 12 | 12 | 0% |  |
| `max_down_ret` | 0 | 17 | 17 | 0% |  |
| `late_bar_momentum` | 0 | 2 | 2 | 0% |  |
| `impulse_bar_dominance` | 0 | 11 | 11 | 0% |  |
| `trend_bar_close_consistency` | 0 | 2 | 2 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 6 | 6 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=24, TP=108, FP rate=18%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=6, TP=18, FP rate=25%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=21, TP=42, FP rate=33%

