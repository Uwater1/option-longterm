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

| ETF | Side | Admitted | Clusters | Cluster Sizes | Avg Sil | FP | Median | TP | FP Rate | Prod Score |
| :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 300ETF | single | 44 | 20 | `[4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, ... (20 clusters)]` | 0.2625 | 0 | 6 | 38 | 0% | 0.73 |
| 500ETF | single | 248 | 55 | `[13, 12, 11, 9, 8, 7, 7, 6, 6, 6, 6, 6, ... (55 clusters)]` | 0.3031 | 2 | 14 | 232 | 1% | 0.85 |
| 159915ETF | single | 29 | 16 | `[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, ... (16 clusters)]` | 0.3358 | 0 | 0 | 29 | 0% | 0.94 |

---

## 2. Training-Only Discriminators (KEY SECTION)

Metrics computable at admission time that separate future FP from future TP.
**Cohen's d > 0.8** = large effect (strong discriminator), **> 0.5** = medium.

Positive Cohen's d means FP has HIGHER value (more unstable/concentrated).

### 500ETF — `single` (FP=2, TP=232)

| Metric | FP Mean | TP Mean | FP Median | TP Median | Cohen's d | Best Threshold | Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| n_negative_years | 1.000 | 0.017 | 1.000 | 0.000 | +10.68 | 1.000 | 99% |
| ic_cv | 1.037 | 0.404 | 1.037 | 0.392 | +10.13 | 0.908 | 100% |
| recency_ratio | 0.293 | 0.737 | 0.293 | 0.718 | -3.03 | 1.652 | 99% |
| n_negative_regimes | 1.000 | 0.190 | 1.000 | 0.000 | +2.92 | 1.000 | 99% |
| weak_link_cv | 0.726 | 0.494 | 0.726 | 0.479 | +2.90 | 0.726 | 99% |
| ic_std_across_regimes | 0.086 | 0.069 | 0.086 | 0.069 | +2.55 | 0.091 | 99% |
| half_ratio | 0.882 | 0.765 | 0.882 | 0.738 | +0.97 | 1.486 | 99% |

---

## 3. False Positive Temporal Decomposition

Per-year training IC for each FP feature. Look for:
- IC concentrated in 1-2 years (era overfit)
- Recent IC much lower than early IC (decaying signal)
- High year-to-year variance (unstable signal)

### 500ETF — `single` False Positives

**`combo_clamp_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=-0.0051, Sharpe=-0.2213)
- Admission: Train IC=+0.1864, Deflated=+0.1868, IR=0.49, Mono=0.68, p=0.0010, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.157 | 2017: -0.076 | 2018: +0.108 | 2019: +0.092 | 2020: +0.026 | 2021: +0.054 | 2022: +0.013 | 2023: -0.039 | 2024: +0.027 | 2025: -0.087 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.214 | 2016: +0.333 | 2017: -0.080 | 2018: +0.171 | 2019: +0.219 | 2020: +0.181 | 2021: +0.086 | 2022: -0.171 | 2023: +0.084 | 2024: +0.078 | 2025: -0.146 | 2026: +0.123
- IC CV=1.04, Neg years (linear/tail)=1/1 of 7, Half ratio=0.88, Recency ratio=0.29
- Early IC=+0.1374, Recent IC=+0.0402, 1st-half IC=+0.0783, 2nd-half IC=+0.0690, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73, neg years=0)
- Regime ICs: Q1_low_vol=-0.043, Q2=+0.114, Q3_mid=+0.036, Q4=+0.044, Q5_high_vol=+0.215

**`combo_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=-0.0049, Sharpe=-0.2213)
- Admission: Train IC=+0.1863, Deflated=+0.1867, IR=0.48, Mono=0.67, p=0.0010, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.116 | 2016: +0.157 | 2017: -0.076 | 2018: +0.108 | 2019: +0.092 | 2020: +0.026 | 2021: +0.054 | 2022: +0.013 | 2023: -0.039 | 2024: +0.028 | 2025: -0.087 | 2026: +0.113
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.327 | 2017: -0.083 | 2018: +0.173 | 2019: +0.217 | 2020: +0.182 | 2021: +0.086 | 2022: -0.166 | 2023: +0.084 | 2024: +0.085 | 2025: -0.136 | 2026: +0.116
- IC CV=1.04, Neg years (linear/tail)=1/1 of 7, Half ratio=0.88, Recency ratio=0.29
- Early IC=+0.1368, Recent IC=+0.0402, 1st-half IC=+0.0781, 2nd-half IC=+0.0690, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73, neg years=0)
- Regime ICs: Q1_low_vol=-0.043, Q2=+0.114, Q3_mid=+0.036, Q4=+0.044, Q5_high_vol=+0.214

---

## 3b. Median (Usable) Temporal Decomposition

Features with positive lockbox IC but non-positive Sharpe.
These contribute signal to IC-weighted ensembles but aren't profitable standalone.

### 300ETF — `single` Median Features

**`combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0`** (Lock IC=+0.0555, Sharpe=-0.0703)
- Admission: Train IC=+0.1981, Deflated=+0.1972, IR=0.59, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.097 | 2016: +0.071 | 2017: +0.065 | 2018: +0.201 | 2019: +0.057 | 2020: -0.013 | 2021: +0.171 | 2022: +0.057 | 2023: +0.176 | 2024: +0.006 | 2025: +0.101 | 2026: -0.144
- Yearly Tail ICs:   2015: +0.115 | 2016: -0.049 | 2017: +0.157 | 2018: +0.513 | 2019: +0.159 | 2020: +0.183 | 2021: +0.364 | 2022: +0.216 | 2023: +0.223 | 2024: +0.070 | 2025: +0.172 | 2026: -0.299
- IC CV=0.72, Neg years (linear/tail)=1/1 of 7, Half ratio=1.16, Recency ratio=0.94
- Early IC=+0.0841, Recent IC=+0.0790, 1st-half IC=+0.0880, 2nd-half IC=+0.1017, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.058, Q3_mid=+0.129, Q4=+0.052, Q5_high_vol=+0.169

**`combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0529, Sharpe=-0.0513)
- Admission: Train IC=+0.2522, Deflated=+0.2513, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.079 | 2017: +0.004 | 2018: +0.216 | 2019: +0.087 | 2020: +0.020 | 2021: +0.161 | 2022: +0.034 | 2023: +0.163 | 2024: +0.053 | 2025: +0.041 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.063 | 2016: +0.108 | 2017: +0.160 | 2018: +0.356 | 2019: +0.357 | 2020: +0.115 | 2021: +0.475 | 2022: +0.089 | 2023: +0.262 | 2024: +0.192 | 2025: -0.080 | 2026: -0.004
- IC CV=0.73, Neg years (linear/tail)=0/0 of 7, Half ratio=1.51, Recency ratio=1.07
- Early IC=+0.0848, Recent IC=+0.0908, 1st-half IC=+0.0843, 2nd-half IC=+0.1274, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.017, Q2=+0.037, Q3_mid=+0.127, Q4=+0.148, Q5_high_vol=+0.169

**`combo_z_sum__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0477, Sharpe=-0.3260)
- Admission: Train IC=+0.2145, Deflated=+0.2131, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.103 | 2016: +0.080 | 2017: -0.034 | 2018: +0.162 | 2019: +0.073 | 2020: +0.052 | 2021: +0.176 | 2022: +0.015 | 2023: +0.162 | 2024: +0.063 | 2025: +0.059 | 2026: -0.165
- Yearly Tail ICs:   2015: -0.029 | 2016: +0.178 | 2017: +0.137 | 2018: +0.357 | 2019: +0.375 | 2020: +0.141 | 2021: +0.364 | 2022: +0.199 | 2023: +0.242 | 2024: +0.274 | 2025: -0.124 | 2026: -0.318
- IC CV=0.75, Neg years (linear/tail)=1/1 of 7, Half ratio=1.72, Recency ratio=1.25
- Early IC=+0.0914, Recent IC=+0.1142, 1st-half IC=+0.0689, 2nd-half IC=+0.1183, Neg regimes=1/5
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=-0.027, Q2=+0.032, Q3_mid=+0.102, Q4=+0.178, Q5_high_vol=+0.151

**`combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio`** (Lock IC=+0.0430, Sharpe=-0.1812)
- Admission: Train IC=+0.1466, Deflated=+0.1457, IR=0.59, Mono=0.73, p=0.0058, MaxCorr=0.73
- Yearly Linear ICs: 2015: +0.076 | 2016: +0.034 | 2017: -0.050 | 2018: +0.114 | 2019: +0.086 | 2020: +0.032 | 2021: +0.170 | 2022: +0.016 | 2023: +0.173 | 2024: +0.026 | 2025: +0.012 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.149 | 2016: +0.136 | 2017: -0.036 | 2018: +0.199 | 2019: +0.293 | 2020: +0.101 | 2021: +0.421 | 2022: +0.234 | 2023: +0.203 | 2024: +0.120 | 2025: -0.101 | 2026: +0.030
- IC CV=0.98, Neg years (linear/tail)=1/1 of 7, Half ratio=2.19, Recency ratio=1.84
- Early IC=+0.0546, Recent IC=+0.1006, 1st-half IC=+0.0450, 2nd-half IC=+0.0985, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=-0.043, Q2=+0.089, Q3_mid=+0.140, Q4=+0.030, Q5_high_vol=+0.132

**`combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position`** (Lock IC=+0.0426, Sharpe=-0.3432)
- Admission: Train IC=+0.1816, Deflated=+0.1799, IR=0.67, Mono=0.76, p=0.0006, MaxCorr=0.86
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

**`combo_sig_product__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.1018, Sharpe=-0.1776)
- Admission: Train IC=+0.2431, Deflated=+0.2424, IR=0.89, Mono=0.79, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.204 | 2016: +0.178 | 2017: +0.106 | 2018: +0.148 | 2019: +0.111 | 2020: +0.150 | 2021: +0.146 | 2022: +0.094 | 2023: +0.081 | 2024: +0.118 | 2025: +0.123 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.315 | 2016: +0.241 | 2017: +0.350 | 2018: +0.168 | 2019: +0.193 | 2020: +0.267 | 2021: +0.197 | 2022: -0.084 | 2023: +0.111 | 2024: +0.090 | 2025: +0.153 | 2026: +0.081
- IC CV=0.21, Neg years (linear/tail)=0/0 of 7, Half ratio=0.82, Recency ratio=0.78
- Early IC=+0.1907, Recent IC=+0.1481, 1st-half IC=+0.1770, 2nd-half IC=+0.1452, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.086, Q3_mid=+0.144, Q4=+0.180, Q5_high_vol=+0.209

**`combo_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0943, Sharpe=-0.0195)
- Admission: Train IC=+0.2038, Deflated=+0.2027, IR=0.53, Mono=0.73, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.086 | 2017: +0.225 | 2018: +0.243 | 2019: +0.136 | 2020: +0.162 | 2021: +0.165 | 2022: +0.100 | 2023: +0.107 | 2024: +0.146 | 2025: +0.071 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.235 | 2016: -0.060 | 2017: +0.161 | 2018: +0.342 | 2019: +0.136 | 2020: +0.247 | 2021: +0.275 | 2022: +0.134 | 2023: +0.067 | 2024: +0.267 | 2025: -0.040 | 2026: -0.291
- IC CV=0.32, Neg years (linear/tail)=0/1 of 7, Half ratio=0.92, Recency ratio=0.96
- Early IC=+0.1706, Recent IC=+0.1636, 1st-half IC=+0.1979, 2nd-half IC=+0.1818, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.228, Q2=+0.050, Q3_mid=+0.185, Q4=+0.155, Q5_high_vol=+0.272

**`combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence`** (Lock IC=+0.0862, Sharpe=-0.2737)
- Admission: Train IC=+0.2006, Deflated=+0.2007, IR=0.58, Mono=0.70, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.010 | 2017: +0.183 | 2018: +0.152 | 2019: +0.098 | 2020: +0.154 | 2021: +0.106 | 2022: +0.085 | 2023: +0.153 | 2024: +0.070 | 2025: +0.027 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.319 | 2016: +0.033 | 2017: +0.406 | 2018: +0.072 | 2019: +0.226 | 2020: +0.197 | 2021: +0.090 | 2022: -0.126 | 2023: +0.321 | 2024: +0.060 | 2025: -0.100 | 2026: +0.271
- IC CV=0.47, Neg years (linear/tail)=0/0 of 7, Half ratio=1.15, Recency ratio=1.18
- Early IC=+0.1101, Recent IC=+0.1299, 1st-half IC=+0.1243, 2nd-half IC=+0.1428, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.081, Q3_mid=+0.131, Q4=+0.093, Q5_high_vol=+0.213

**`combo_max__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0857, Sharpe=-0.1017)
- Admission: Train IC=+0.2065, Deflated=+0.2055, IR=0.57, Mono=0.74, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.063 | 2017: +0.152 | 2018: +0.110 | 2019: +0.030 | 2020: +0.092 | 2021: +0.053 | 2022: +0.100 | 2023: +0.078 | 2024: +0.130 | 2025: +0.142 | 2026: -0.104
- Yearly Tail ICs:   2015: +0.308 | 2016: +0.211 | 2017: +0.205 | 2018: +0.106 | 2019: +0.028 | 2020: +0.193 | 2021: +0.235 | 2022: +0.093 | 2023: +0.035 | 2024: +0.281 | 2025: +0.146 | 2026: -0.056
- IC CV=0.47, Neg years (linear/tail)=0/0 of 7, Half ratio=0.59, Recency ratio=0.70
- Early IC=+0.1032, Recent IC=+0.0726, 1st-half IC=+0.1274, 2nd-half IC=+0.0746, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.022, Q3_mid=+0.131, Q4=+0.121, Q5_high_vol=+0.117

**`combo_max__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0815, Sharpe=-0.0085)
- Admission: Train IC=+0.2182, Deflated=+0.2180, IR=0.55, Mono=0.71, p=0.0004, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.108 | 2017: +0.133 | 2018: +0.204 | 2019: +0.091 | 2020: +0.100 | 2021: +0.117 | 2022: +0.102 | 2023: +0.060 | 2024: +0.125 | 2025: +0.098 | 2026: -0.037
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.239 | 2017: +0.146 | 2018: +0.278 | 2019: +0.141 | 2020: +0.193 | 2021: +0.228 | 2022: +0.219 | 2023: +0.295 | 2024: +0.267 | 2025: +0.168 | 2026: -0.226
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.86, Recency ratio=0.75
- Early IC=+0.1452, Recent IC=+0.1089, 1st-half IC=+0.1474, 2nd-half IC=+0.1272, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.140, Q2=+0.014, Q3_mid=+0.148, Q4=+0.152, Q5_high_vol=+0.216

**`combo_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0809, Sharpe=-0.2503)
- Admission: Train IC=+0.2927, Deflated=+0.2920, IR=0.90, Mono=0.81, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.142 | 2017: +0.182 | 2018: +0.239 | 2019: +0.138 | 2020: +0.141 | 2021: +0.083 | 2022: +0.109 | 2023: +0.072 | 2024: +0.086 | 2025: +0.101 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.217 | 2017: +0.379 | 2018: +0.485 | 2019: +0.256 | 2020: +0.199 | 2021: +0.009 | 2022: +0.277 | 2023: +0.114 | 2024: +0.090 | 2025: +0.108 | 2026: -0.181
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.56
- Early IC=+0.2004, Recent IC=+0.1124, 1st-half IC=+0.2100, 2nd-half IC=+0.1523, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.054, Q3_mid=+0.199, Q4=+0.177, Q5_high_vol=+0.266

**`combo_max__net_volume_flow__bar_ret_0`** (Lock IC=+0.0784, Sharpe=-0.0612)
- Admission: Train IC=+0.1965, Deflated=+0.1959, IR=0.57, Mono=0.71, p=0.0008, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.107 | 2017: +0.170 | 2018: +0.235 | 2019: +0.118 | 2020: +0.108 | 2021: +0.107 | 2022: +0.094 | 2023: +0.074 | 2024: +0.109 | 2025: +0.105 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.219 | 2016: +0.037 | 2017: +0.152 | 2018: +0.279 | 2019: +0.140 | 2020: +0.257 | 2021: +0.282 | 2022: +0.156 | 2023: +0.362 | 2024: +0.184 | 2025: -0.069 | 2026: -0.486
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.72
- Early IC=+0.1495, Recent IC=+0.1075, 1st-half IC=+0.1774, 2nd-half IC=+0.1413, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.016, Q3_mid=+0.169, Q4=+0.149, Q5_high_vol=+0.233

**`combo_rank_min__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0781, Sharpe=-0.0570)
- Admission: Train IC=+0.2759, Deflated=+0.2752, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.150 | 2017: +0.182 | 2018: +0.240 | 2019: +0.135 | 2020: +0.137 | 2021: +0.083 | 2022: +0.102 | 2023: +0.072 | 2024: +0.083 | 2025: +0.097 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.135 | 2016: +0.302 | 2017: +0.378 | 2018: +0.505 | 2019: +0.129 | 2020: +0.123 | 2021: +0.004 | 2022: +0.124 | 2023: +0.117 | 2024: +0.064 | 2025: -0.049 | 2026: -0.277
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.55
- Early IC=+0.2005, Recent IC=+0.1099, 1st-half IC=+0.2103, 2nd-half IC=+0.1512, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.054, Q3_mid=+0.197, Q4=+0.175, Q5_high_vol=+0.265

**`combo_rank_min__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0773, Sharpe=-0.2088)
- Admission: Train IC=+0.2742, Deflated=+0.2735, IR=0.70, Mono=0.76, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.126 | 2017: +0.129 | 2018: +0.196 | 2019: +0.098 | 2020: +0.095 | 2021: +0.072 | 2022: +0.082 | 2023: +0.058 | 2024: +0.091 | 2025: +0.113 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.419 | 2016: +0.215 | 2017: +0.212 | 2018: +0.207 | 2019: +0.139 | 2020: +0.155 | 2021: +0.066 | 2022: +0.184 | 2023: +0.003 | 2024: +0.095 | 2025: +0.057 | 2026: -0.446
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.50
- Early IC=+0.1677, Recent IC=+0.0837, 1st-half IC=+0.1603, 2nd-half IC=+0.1139, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.169, Q2=-0.008, Q3_mid=+0.161, Q4=+0.137, Q5_high_vol=+0.195

**`bar_body_rng_0`** (Lock IC=+0.0756, Sharpe=-0.0707)
- Admission: Train IC=+0.1321, Deflated=+0.1314, IR=0.55, Mono=0.69, p=0.0152, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.104 | 2017: +0.169 | 2018: +0.192 | 2019: +0.131 | 2020: +0.092 | 2021: +0.119 | 2022: +0.057 | 2023: +0.068 | 2024: +0.105 | 2025: +0.099 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.365 | 2016: -0.105 | 2017: +0.215 | 2018: +0.088 | 2019: +0.267 | 2020: +0.135 | 2021: +0.187 | 2022: +0.004 | 2023: +0.093 | 2024: +0.067 | 2025: +0.148 | 2026: -0.034
- IC CV=0.28, Neg years (linear/tail)=0/1 of 7, Half ratio=0.94, Recency ratio=0.68
- Early IC=+0.1556, Recent IC=+0.1057, 1st-half IC=+0.1508, 2nd-half IC=+0.1415, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.005, Q3_mid=+0.139, Q4=+0.155, Q5_high_vol=+0.244

**`combo_rank_min__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0702, Sharpe=-0.1457)
- Admission: Train IC=+0.2819, Deflated=+0.2805, IR=0.78, Mono=0.78, p=0.0000, MaxCorr=0.81
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

**`combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0332, Sharpe=-0.5814)
- Admission: Train IC=+0.1685, Deflated=+0.1689, IR=0.52, Mono=0.70, p=0.0018, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.209 | 2016: -0.005 | 2017: +0.067 | 2018: +0.079 | 2019: +0.124 | 2020: +0.158 | 2021: +0.126 | 2022: -0.002 | 2023: +0.022 | 2024: +0.062 | 2025: -0.022 | 2026: +0.172
- Yearly Tail ICs:   2015: +0.109 | 2016: -0.014 | 2017: +0.499 | 2018: +0.228 | 2019: +0.189 | 2020: +0.253 | 2021: +0.034 | 2022: -0.181 | 2023: +0.021 | 2024: +0.083 | 2025: -0.127 | 2026: +0.369
- IC CV=0.59, Neg years (linear/tail)=1/1 of 7, Half ratio=1.89, Recency ratio=1.39
- Early IC=+0.1017, Recent IC=+0.1417, 1st-half IC=+0.0727, 2nd-half IC=+0.1374, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.130, Q3_mid=+0.052, Q4=+0.047, Q5_high_vol=+0.211

**`combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0279, Sharpe=-0.0835)
- Admission: Train IC=+0.1951, Deflated=+0.1951, IR=0.70, Mono=0.75, p=0.0008, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.177 | 2016: +0.032 | 2017: +0.038 | 2018: +0.068 | 2019: +0.151 | 2020: +0.080 | 2021: +0.101 | 2022: -0.007 | 2023: +0.011 | 2024: +0.055 | 2025: -0.054 | 2026: +0.187
- Yearly Tail ICs:   2015: +0.072 | 2016: +0.006 | 2017: +0.373 | 2018: +0.204 | 2019: +0.353 | 2020: +0.211 | 2021: +0.087 | 2022: -0.095 | 2023: +0.100 | 2024: +0.085 | 2025: -0.083 | 2026: +0.198
- IC CV=0.55, Neg years (linear/tail)=0/0 of 7, Half ratio=1.46, Recency ratio=0.86
- Early IC=+0.1044, Recent IC=+0.0902, 1st-half IC=+0.0746, 2nd-half IC=+0.1089, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.121, Q3_mid=+0.041, Q4=+0.035, Q5_high_vol=+0.199

---

## 4. True Positive Temporal Decomposition (Comparison)

What stable, persistent features look like in training.

### 300ETF — `single` True Positives

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0602, Sharpe=+1.0194)
- Admission: Train IC=+0.2690, Deflated=+0.2689, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.117 | 2017: -0.053 | 2018: +0.140 | 2019: +0.100 | 2020: +0.074 | 2021: +0.143 | 2022: +0.037 | 2023: +0.135 | 2024: +0.056 | 2025: +0.049 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.398 | 2016: +0.177 | 2017: -0.025 | 2018: +0.311 | 2019: +0.294 | 2020: +0.175 | 2021: +0.369 | 2022: +0.249 | 2023: +0.127 | 2024: +0.407 | 2025: +0.059 | 2026: +0.139
- IC CV=0.78, Neg years (linear/tail)=1/1 of 7, Half ratio=0.77, Recency ratio=0.57
- Early IC=+0.1913, Recent IC=+0.1086, 1st-half IC=+0.1458, 2nd-half IC=+0.1116, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.029, Q2=+0.013, Q3_mid=+0.082, Q4=+0.218, Q5_high_vol=+0.221

**`combo_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.0750, Sharpe=+0.7601)
- Admission: Train IC=+0.2121, Deflated=+0.2118, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.060 | 2017: -0.024 | 2018: +0.181 | 2019: +0.146 | 2020: +0.024 | 2021: +0.126 | 2022: +0.042 | 2023: +0.163 | 2024: +0.032 | 2025: +0.090 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.217 | 2016: +0.082 | 2017: +0.025 | 2018: +0.383 | 2019: +0.210 | 2020: +0.202 | 2021: +0.359 | 2022: +0.214 | 2023: +0.280 | 2024: +0.150 | 2025: -0.023 | 2026: +0.240
- IC CV=0.77, Neg years (linear/tail)=1/0 of 7, Half ratio=0.99, Recency ratio=0.54
- Early IC=+0.1382, Recent IC=+0.0750, 1st-half IC=+0.1144, 2nd-half IC=+0.1136, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.040, Q2=+0.017, Q3_mid=+0.099, Q4=+0.164, Q5_high_vol=+0.207

**`combo_mean__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0561, Sharpe=+0.6987)
- Admission: Train IC=+0.2124, Deflated=+0.2111, IR=0.67, Mono=0.74, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.117 | 2016: +0.054 | 2017: +0.002 | 2018: +0.172 | 2019: +0.051 | 2020: -0.003 | 2021: +0.179 | 2022: +0.056 | 2023: +0.192 | 2024: +0.025 | 2025: +0.114 | 2026: -0.181
- Yearly Tail ICs:   2015: +0.038 | 2016: +0.199 | 2017: +0.157 | 2018: +0.396 | 2019: +0.182 | 2020: +0.066 | 2021: +0.365 | 2022: +0.373 | 2023: +0.353 | 2024: +0.078 | 2025: +0.083 | 2026: +0.023
- IC CV=0.86, Neg years (linear/tail)=1/0 of 7, Half ratio=1.26, Recency ratio=1.03
- Early IC=+0.0855, Recent IC=+0.0880, 1st-half IC=+0.0792, 2nd-half IC=+0.0996, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.005, Q2=+0.054, Q3_mid=+0.101, Q4=+0.092, Q5_high_vol=+0.178

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0715, Sharpe=+0.6792)
- Admission: Train IC=+0.2194, Deflated=+0.2197, IR=0.57, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.114 | 2017: +0.004 | 2018: +0.209 | 2019: +0.105 | 2020: +0.047 | 2021: +0.144 | 2022: +0.084 | 2023: +0.108 | 2024: +0.016 | 2025: +0.068 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.209 | 2016: +0.108 | 2017: +0.053 | 2018: +0.274 | 2019: +0.240 | 2020: +0.147 | 2021: +0.459 | 2022: +0.269 | 2023: +0.064 | 2024: +0.158 | 2025: +0.221 | 2026: +0.079
- IC CV=0.60, Neg years (linear/tail)=0/0 of 7, Half ratio=0.87, Recency ratio=0.58
- Early IC=+0.1643, Recent IC=+0.0956, 1st-half IC=+0.1390, 2nd-half IC=+0.1207, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.038, Q3_mid=+0.120, Q4=+0.184, Q5_high_vol=+0.210

**`combo_max__bar_body_rng_0__volume_surge_direction`** (Lock IC=+0.0602, Sharpe=+0.6652)
- Admission: Train IC=+0.1408, Deflated=+0.1400, IR=0.50, Mono=0.67, p=0.0070, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.127 | 2016: +0.103 | 2017: +0.029 | 2018: +0.184 | 2019: +0.125 | 2020: -0.018 | 2021: +0.062 | 2022: +0.058 | 2023: +0.155 | 2024: +0.039 | 2025: +0.077 | 2026: -0.093
- Yearly Tail ICs:   2015: +0.219 | 2016: +0.015 | 2017: +0.038 | 2018: +0.286 | 2019: +0.172 | 2020: +0.147 | 2021: +0.012 | 2022: +0.313 | 2023: +0.215 | 2024: +0.288 | 2025: +0.335 | 2026: -0.081
- IC CV=0.72, Neg years (linear/tail)=1/0 of 7, Half ratio=0.81, Recency ratio=0.19
- Early IC=+0.1146, Recent IC=+0.0222, 1st-half IC=+0.1003, 2nd-half IC=+0.0813, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.084, Q2=+0.063, Q3_mid=+0.126, Q4=+0.047, Q5_high_vol=+0.153

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0`** (Lock IC=+0.0763, Sharpe=+0.6530)
- Admission: Train IC=+0.2667, Deflated=+0.2669, IR=0.68, Mono=0.71, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.069 | 2017: -0.028 | 2018: +0.197 | 2019: +0.149 | 2020: +0.025 | 2021: +0.149 | 2022: +0.048 | 2023: +0.171 | 2024: +0.048 | 2025: +0.095 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.314 | 2016: +0.093 | 2017: +0.020 | 2018: +0.350 | 2019: +0.207 | 2020: +0.184 | 2021: +0.532 | 2022: +0.186 | 2023: +0.247 | 2024: +0.283 | 2025: +0.049 | 2026: +0.192
- IC CV=0.76, Neg years (linear/tail)=1/0 of 7, Half ratio=1.08, Recency ratio=0.63
- Early IC=+0.1384, Recent IC=+0.0875, 1st-half IC=+0.1186, 2nd-half IC=+0.1276, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.032, Q3_mid=+0.111, Q4=+0.190, Q5_high_vol=+0.217

**`combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0764, Sharpe=+0.6503)
- Admission: Train IC=+0.1836, Deflated=+0.1831, IR=0.48, Mono=0.67, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.162 | 2016: +0.062 | 2017: -0.036 | 2018: +0.163 | 2019: +0.134 | 2020: +0.027 | 2021: +0.129 | 2022: +0.031 | 2023: +0.135 | 2024: +0.036 | 2025: +0.094 | 2026: +0.041
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.101 | 2017: -0.122 | 2018: +0.393 | 2019: +0.207 | 2020: +0.164 | 2021: +0.284 | 2022: +0.156 | 2023: +0.260 | 2024: +0.246 | 2025: +0.111 | 2026: +0.223
- IC CV=0.78, Neg years (linear/tail)=1/1 of 7, Half ratio=1.38, Recency ratio=0.69
- Early IC=+0.1115, Recent IC=+0.0767, 1st-half IC=+0.0790, 2nd-half IC=+0.1087, Neg regimes=0/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.62)
- Regime ICs: Q1_low_vol=+0.022, Q2=+0.002, Q3_mid=+0.074, Q4=+0.173, Q5_high_vol=+0.175

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.0602, Sharpe=+0.5551)
- Admission: Train IC=+0.2660, Deflated=+0.2658, IR=0.61, Mono=0.70, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.109 | 2017: -0.075 | 2018: +0.166 | 2019: +0.085 | 2020: +0.075 | 2021: +0.151 | 2022: +0.095 | 2023: +0.091 | 2024: +0.027 | 2025: +0.042 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.196 | 2016: +0.223 | 2017: -0.036 | 2018: +0.422 | 2019: +0.218 | 2020: +0.178 | 2021: +0.408 | 2022: +0.272 | 2023: +0.144 | 2024: +0.208 | 2025: +0.115 | 2026: +0.191
- IC CV=0.82, Neg years (linear/tail)=1/1 of 7, Half ratio=1.02, Recency ratio=0.74
- Early IC=+0.1530, Recent IC=+0.1131, 1st-half IC=+0.1144, 2nd-half IC=+0.1172, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.053, Q2=+0.037, Q3_mid=+0.103, Q4=+0.200, Q5_high_vol=+0.197

**`combo_rank_max__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0486, Sharpe=+0.5501)
- Admission: Train IC=+0.1863, Deflated=+0.1849, IR=0.72, Mono=0.78, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.041 | 2017: +0.001 | 2018: +0.129 | 2019: +0.046 | 2020: +0.005 | 2021: +0.177 | 2022: +0.037 | 2023: +0.200 | 2024: +0.022 | 2025: +0.094 | 2026: -0.194
- Yearly Tail ICs:   2015: +0.099 | 2016: +0.175 | 2017: +0.178 | 2018: +0.360 | 2019: +0.150 | 2020: +0.061 | 2021: +0.333 | 2022: +0.294 | 2023: +0.195 | 2024: +0.188 | 2025: +0.194 | 2026: -0.297
- IC CV=0.87, Neg years (linear/tail)=1/0 of 7, Half ratio=1.53, Recency ratio=1.28
- Early IC=+0.0719, Recent IC=+0.0922, 1st-half IC=+0.0615, 2nd-half IC=+0.0941, Neg regimes=1/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=-0.000, Q2=+0.032, Q3_mid=+0.060, Q4=+0.102, Q5_high_vol=+0.169

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0653, Sharpe=+0.4944)
- Admission: Train IC=+0.2662, Deflated=+0.2660, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.063 | 2017: -0.068 | 2018: +0.203 | 2019: +0.123 | 2020: +0.059 | 2021: +0.173 | 2022: +0.044 | 2023: +0.140 | 2024: +0.049 | 2025: +0.051 | 2026: -0.014
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.099 | 2017: +0.076 | 2018: +0.386 | 2019: +0.394 | 2020: +0.163 | 2021: +0.435 | 2022: +0.335 | 2023: +0.112 | 2024: +0.277 | 2025: -0.048 | 2026: +0.268
- IC CV=0.86, Neg years (linear/tail)=1/0 of 7, Half ratio=1.11, Recency ratio=0.79
- Early IC=+0.1475, Recent IC=+0.1159, 1st-half IC=+0.1209, 2nd-half IC=+0.1345, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.049, Q2=+0.010, Q3_mid=+0.110, Q4=+0.248, Q5_high_vol=+0.207

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0650, Sharpe=+0.4659)
- Admission: Train IC=+0.2949, Deflated=+0.2950, IR=0.76, Mono=0.73, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.096 | 2017: +0.008 | 2018: +0.184 | 2019: +0.117 | 2020: +0.042 | 2021: +0.132 | 2022: +0.038 | 2023: +0.177 | 2024: +0.054 | 2025: +0.049 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.333 | 2016: +0.106 | 2017: +0.100 | 2018: +0.398 | 2019: +0.276 | 2020: +0.235 | 2021: +0.492 | 2022: +0.149 | 2023: +0.329 | 2024: +0.242 | 2025: -0.040 | 2026: +0.148
- IC CV=0.65, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.50
- Early IC=+0.1748, Recent IC=+0.0867, 1st-half IC=+0.1480, 2nd-half IC=+0.1194, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.026, Q2=+0.027, Q3_mid=+0.113, Q4=+0.191, Q5_high_vol=+0.227

**`combo_min__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0559, Sharpe=+0.4336)
- Admission: Train IC=+0.2285, Deflated=+0.2280, IR=0.54, Mono=0.65, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.111 | 2016: +0.090 | 2017: +0.020 | 2018: +0.183 | 2019: +0.078 | 2020: -0.001 | 2021: +0.127 | 2022: +0.049 | 2023: +0.178 | 2024: +0.056 | 2025: +0.027 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.137 | 2017: +0.152 | 2018: +0.358 | 2019: +0.257 | 2020: +0.063 | 2021: +0.396 | 2022: +0.175 | 2023: +0.424 | 2024: +0.238 | 2025: -0.044 | 2026: -0.084
- IC CV=0.67, Neg years (linear/tail)=1/0 of 7, Half ratio=1.07, Recency ratio=0.63
- Early IC=+0.1005, Recent IC=+0.0629, 1st-half IC=+0.0957, 2nd-half IC=+0.1028, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.029, Q2=+0.054, Q3_mid=+0.113, Q4=+0.115, Q5_high_vol=+0.171

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0724, Sharpe=+0.4279)
- Admission: Train IC=+0.2394, Deflated=+0.2393, IR=0.57, Mono=0.68, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.045 | 2017: -0.016 | 2018: +0.180 | 2019: +0.149 | 2020: +0.035 | 2021: +0.123 | 2022: +0.052 | 2023: +0.168 | 2024: +0.033 | 2025: +0.099 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.428 | 2016: -0.085 | 2017: -0.005 | 2018: +0.284 | 2019: +0.273 | 2020: +0.251 | 2021: +0.362 | 2022: +0.326 | 2023: +0.159 | 2024: +0.278 | 2025: +0.110 | 2026: +0.203
- IC CV=0.77, Neg years (linear/tail)=1/2 of 7, Half ratio=0.93, Recency ratio=0.57
- Early IC=+0.1393, Recent IC=+0.0789, 1st-half IC=+0.1265, 2nd-half IC=+0.1178, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.027, Q3_mid=+0.117, Q4=+0.166, Q5_high_vol=+0.205

**`combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.0656, Sharpe=+0.4218)
- Admission: Train IC=+0.2354, Deflated=+0.2346, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.105 | 2017: -0.069 | 2018: +0.211 | 2019: +0.090 | 2020: +0.066 | 2021: +0.154 | 2022: +0.079 | 2023: +0.112 | 2024: +0.027 | 2025: +0.059 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.173 | 2016: +0.185 | 2017: -0.038 | 2018: +0.441 | 2019: +0.328 | 2020: +0.046 | 2021: +0.356 | 2022: +0.232 | 2023: +0.059 | 2024: +0.217 | 2025: +0.104 | 2026: +0.123
- IC CV=0.82, Neg years (linear/tail)=1/1 of 7, Half ratio=1.05, Recency ratio=0.72
- Early IC=+0.1538, Recent IC=+0.1102, 1st-half IC=+0.1180, 2nd-half IC=+0.1237, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.059, Q2=+0.023, Q3_mid=+0.103, Q4=+0.231, Q5_high_vol=+0.201

**`combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio`** (Lock IC=+0.0625, Sharpe=+0.4018)
- Admission: Train IC=+0.2713, Deflated=+0.2711, IR=0.74, Mono=0.76, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.069 | 2017: -0.018 | 2018: +0.235 | 2019: +0.114 | 2020: +0.040 | 2021: +0.178 | 2022: +0.028 | 2023: +0.141 | 2024: +0.047 | 2025: +0.074 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.243 | 2016: +0.035 | 2017: +0.066 | 2018: +0.384 | 2019: +0.314 | 2020: +0.140 | 2021: +0.564 | 2022: +0.194 | 2023: +0.140 | 2024: +0.215 | 2025: -0.069 | 2026: +0.319
- IC CV=0.74, Neg years (linear/tail)=1/0 of 7, Half ratio=1.12, Recency ratio=0.76
- Early IC=+0.1432, Recent IC=+0.1092, 1st-half IC=+0.1244, 2nd-half IC=+0.1394, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.002, Q2=+0.006, Q3_mid=+0.150, Q4=+0.220, Q5_high_vol=+0.210

**`combo_ratio__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0416, Sharpe=+0.4017)
- Admission: Train IC=+0.1624, Deflated=+0.1615, IR=0.46, Mono=0.65, p=0.0024, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.093 | 2017: +0.071 | 2018: +0.191 | 2019: +0.098 | 2020: +0.010 | 2021: +0.124 | 2022: +0.036 | 2023: +0.142 | 2024: +0.037 | 2025: +0.044 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.182 | 2016: -0.115 | 2017: +0.115 | 2018: +0.285 | 2019: +0.104 | 2020: +0.272 | 2021: +0.293 | 2022: +0.258 | 2023: +0.249 | 2024: +0.186 | 2025: +0.049 | 2026: -0.298
- IC CV=0.51, Neg years (linear/tail)=0/1 of 7, Half ratio=1.04, Recency ratio=0.69
- Early IC=+0.0969, Recent IC=+0.0669, 1st-half IC=+0.1013, 2nd-half IC=+0.1052, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.100, Q2=+0.065, Q3_mid=+0.139, Q4=+0.088, Q5_high_vol=+0.144

**`combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio`** (Lock IC=+0.0716, Sharpe=+0.3919)
- Admission: Train IC=+0.2603, Deflated=+0.2593, IR=0.61, Mono=0.71, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.091 | 2017: -0.038 | 2018: +0.224 | 2019: +0.093 | 2020: +0.064 | 2021: +0.153 | 2022: +0.075 | 2023: +0.146 | 2024: +0.029 | 2025: +0.084 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.070 | 2017: -0.074 | 2018: +0.393 | 2019: +0.268 | 2020: +0.273 | 2021: +0.338 | 2022: +0.237 | 2023: +0.164 | 2024: +0.125 | 2025: +0.273 | 2026: +0.100
- IC CV=0.74, Neg years (linear/tail)=1/1 of 7, Half ratio=1.03, Recency ratio=0.70
- Early IC=+0.1549, Recent IC=+0.1080, 1st-half IC=+0.1275, 2nd-half IC=+0.1309, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=-0.026, Q2=+0.038, Q3_mid=+0.124, Q4=+0.221, Q5_high_vol=+0.209

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0670, Sharpe=+0.3890)
- Admission: Train IC=+0.2361, Deflated=+0.2361, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.108 | 2017: +0.023 | 2018: +0.215 | 2019: +0.106 | 2020: +0.039 | 2021: +0.141 | 2022: +0.070 | 2023: +0.132 | 2024: +0.016 | 2025: +0.083 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.052 | 2017: -0.006 | 2018: +0.299 | 2019: +0.183 | 2020: +0.235 | 2021: +0.441 | 2022: +0.323 | 2023: +0.241 | 2024: +0.097 | 2025: +0.156 | 2026: +0.049
- IC CV=0.57, Neg years (linear/tail)=0/1 of 7, Half ratio=0.89, Recency ratio=0.60
- Early IC=+0.1495, Recent IC=+0.0898, 1st-half IC=+0.1358, 2nd-half IC=+0.1204, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.051, Q3_mid=+0.128, Q4=+0.168, Q5_high_vol=+0.201

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0`** (Lock IC=+0.0671, Sharpe=+0.3890)
- Admission: Train IC=+0.2361, Deflated=+0.2360, IR=0.50, Mono=0.69, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.192 | 2016: +0.108 | 2017: +0.023 | 2018: +0.215 | 2019: +0.106 | 2020: +0.038 | 2021: +0.141 | 2022: +0.070 | 2023: +0.132 | 2024: +0.016 | 2025: +0.083 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.052 | 2017: -0.006 | 2018: +0.300 | 2019: +0.183 | 2020: +0.237 | 2021: +0.441 | 2022: +0.323 | 2023: +0.241 | 2024: +0.097 | 2025: +0.156 | 2026: +0.049
- IC CV=0.57, Neg years (linear/tail)=0/1 of 7, Half ratio=0.89, Recency ratio=0.60
- Early IC=+0.1497, Recent IC=+0.0897, 1st-half IC=+0.1358, 2nd-half IC=+0.1204, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.051, Q3_mid=+0.128, Q4=+0.168, Q5_high_vol=+0.201

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.0572, Sharpe=+0.3641)
- Admission: Train IC=+0.1747, Deflated=+0.1741, IR=0.44, Mono=0.66, p=0.0016, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.102 | 2016: +0.098 | 2017: +0.031 | 2018: +0.194 | 2019: +0.079 | 2020: +0.014 | 2021: +0.172 | 2022: +0.029 | 2023: +0.173 | 2024: +0.059 | 2025: +0.057 | 2026: -0.110
- Yearly Tail ICs:   2015: +0.018 | 2016: +0.139 | 2017: +0.092 | 2018: +0.334 | 2019: +0.121 | 2020: +0.072 | 2021: +0.321 | 2022: +0.248 | 2023: +0.395 | 2024: +0.176 | 2025: -0.003 | 2026: -0.104
- IC CV=0.62, Neg years (linear/tail)=0/0 of 7, Half ratio=1.27, Recency ratio=0.93
- Early IC=+0.1000, Recent IC=+0.0934, 1st-half IC=+0.0913, 2nd-half IC=+0.1162, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.81)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.061, Q3_mid=+0.113, Q4=+0.139, Q5_high_vol=+0.165

**`combo_mean__max_up_ret__volume_surge_direction`** (Lock IC=+0.0540, Sharpe=+0.3602)
- Admission: Train IC=+0.1816, Deflated=+0.1804, IR=0.65, Mono=0.73, p=0.0006, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.106 | 2016: +0.055 | 2017: -0.019 | 2018: +0.179 | 2019: +0.111 | 2020: +0.027 | 2021: +0.124 | 2022: +0.034 | 2023: +0.159 | 2024: +0.023 | 2025: +0.087 | 2026: -0.106
- Yearly Tail ICs:   2015: +0.158 | 2016: +0.057 | 2017: +0.040 | 2018: +0.304 | 2019: +0.160 | 2020: +0.249 | 2021: +0.213 | 2022: +0.107 | 2023: +0.398 | 2024: +0.291 | 2025: +0.268 | 2026: -0.204
- IC CV=0.74, Neg years (linear/tail)=1/0 of 7, Half ratio=1.31, Recency ratio=0.94
- Early IC=+0.0806, Recent IC=+0.0755, 1st-half IC=+0.0823, 2nd-half IC=+0.1080, Neg regimes=0/5
- Weak component: `volume_surge_direction` (CV=1.02)
- Regime ICs: Q1_low_vol=+0.067, Q2=+0.056, Q3_mid=+0.128, Q4=+0.087, Q5_high_vol=+0.142

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.0728, Sharpe=+0.3499)
- Admission: Train IC=+0.2294, Deflated=+0.2299, IR=0.55, Mono=0.74, p=0.0000, MaxCorr=0.82
- Yearly Linear ICs: 2015: +0.200 | 2016: +0.071 | 2017: -0.093 | 2018: +0.129 | 2019: +0.067 | 2020: +0.041 | 2021: +0.095 | 2022: +0.109 | 2023: +0.058 | 2024: +0.021 | 2025: +0.045 | 2026: +0.151
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.260 | 2017: -0.063 | 2018: +0.287 | 2019: +0.204 | 2020: +0.254 | 2021: +0.174 | 2022: +0.239 | 2023: -0.083 | 2024: +0.166 | 2025: -0.078 | 2026: +0.337
- IC CV=1.14, Neg years (linear/tail)=1/1 of 7, Half ratio=0.62, Recency ratio=0.50
- Early IC=+0.1357, Recent IC=+0.0678, 1st-half IC=+0.1151, 2nd-half IC=+0.0718, Neg regimes=1/5
- Regime ICs: Q1_low_vol=-0.067, Q2=+0.000, Q3_mid=+0.053, Q4=+0.178, Q5_high_vol=+0.171

**`combo_mean__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0618, Sharpe=+0.3356)
- Admission: Train IC=+0.1971, Deflated=+0.1958, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.120 | 2016: +0.052 | 2017: +0.039 | 2018: +0.207 | 2019: +0.071 | 2020: -0.022 | 2021: +0.145 | 2022: +0.066 | 2023: +0.187 | 2024: +0.012 | 2025: +0.106 | 2026: -0.142
- Yearly Tail ICs:   2015: +0.215 | 2016: -0.114 | 2017: +0.208 | 2018: +0.352 | 2019: +0.152 | 2020: +0.096 | 2021: +0.420 | 2022: +0.300 | 2023: +0.247 | 2024: +0.201 | 2025: +0.147 | 2026: -0.110
- IC CV=0.80, Neg years (linear/tail)=1/1 of 7, Half ratio=1.03, Recency ratio=0.72
- Early IC=+0.0859, Recent IC=+0.0615, 1st-half IC=+0.0918, 2nd-half IC=+0.0946, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.078, Q3_mid=+0.124, Q4=+0.055, Q5_high_vol=+0.174

**`combo_mean__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0618, Sharpe=+0.3065)
- Admission: Train IC=+0.1969, Deflated=+0.1956, IR=0.51, Mono=0.69, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.120 | 2016: +0.052 | 2017: +0.039 | 2018: +0.207 | 2019: +0.071 | 2020: -0.022 | 2021: +0.145 | 2022: +0.066 | 2023: +0.187 | 2024: +0.012 | 2025: +0.106 | 2026: -0.141
- Yearly Tail ICs:   2015: +0.218 | 2016: -0.114 | 2017: +0.208 | 2018: +0.352 | 2019: +0.152 | 2020: +0.096 | 2021: +0.420 | 2022: +0.299 | 2023: +0.247 | 2024: +0.201 | 2025: +0.147 | 2026: -0.110
- IC CV=0.80, Neg years (linear/tail)=1/1 of 7, Half ratio=1.03, Recency ratio=0.72
- Early IC=+0.0859, Recent IC=+0.0615, 1st-half IC=+0.0918, 2nd-half IC=+0.0946, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.038, Q2=+0.078, Q3_mid=+0.124, Q4=+0.055, Q5_high_vol=+0.174

**`combo_min__volume_weighted_price_position__volume_surge_direction`** (Lock IC=+0.0717, Sharpe=+0.3059)
- Admission: Train IC=+0.1600, Deflated=+0.1586, IR=0.45, Mono=0.67, p=0.0026, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.099 | 2016: +0.050 | 2017: -0.014 | 2018: +0.257 | 2019: +0.071 | 2020: -0.005 | 2021: +0.111 | 2022: +0.080 | 2023: +0.167 | 2024: -0.015 | 2025: +0.130 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.428 | 2016: -0.248 | 2017: +0.054 | 2018: +0.237 | 2019: +0.106 | 2020: +0.084 | 2021: +0.389 | 2022: +0.221 | 2023: +0.343 | 2024: +0.095 | 2025: +0.314 | 2026: -0.234
- IC CV=1.04, Neg years (linear/tail)=2/1 of 7, Half ratio=1.05, Recency ratio=0.71
- Early IC=+0.0745, Recent IC=+0.0527, 1st-half IC=+0.0835, 2nd-half IC=+0.0881, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.062, Q3_mid=+0.151, Q4=+0.033, Q5_high_vol=+0.150

**`combo_z_sum__opening_drive_thrust_ratio__limit_down_proximity_early`** (Lock IC=+0.0637, Sharpe=+0.3013)
- Admission: Train IC=+0.1746, Deflated=+0.1733, IR=0.62, Mono=0.72, p=0.0016, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.086 | 2017: -0.069 | 2018: +0.194 | 2019: +0.097 | 2020: +0.050 | 2021: +0.150 | 2022: +0.067 | 2023: +0.104 | 2024: +0.022 | 2025: +0.056 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.173 | 2017: -0.114 | 2018: +0.462 | 2019: +0.354 | 2020: +0.122 | 2021: +0.319 | 2022: +0.191 | 2023: +0.050 | 2024: +0.041 | 2025: +0.222 | 2026: +0.117
- IC CV=0.85, Neg years (linear/tail)=1/1 of 7, Half ratio=1.30, Recency ratio=0.74
- Early IC=+0.1355, Recent IC=+0.1000, 1st-half IC=+0.0924, 2nd-half IC=+0.1197, Neg regimes=1/5
- Weak component: `limit_down_proximity_early` (CV=1.62)
- Regime ICs: Q1_low_vol=-0.065, Q2=+0.012, Q3_mid=+0.096, Q4=+0.230, Q5_high_vol=+0.173

**`combo_z_sum__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early`** (Lock IC=+0.0637, Sharpe=+0.3013)
- Admission: Train IC=+0.1746, Deflated=+0.1733, IR=0.62, Mono=0.72, p=0.0016, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.185 | 2016: +0.086 | 2017: -0.069 | 2018: +0.194 | 2019: +0.097 | 2020: +0.050 | 2021: +0.150 | 2022: +0.067 | 2023: +0.104 | 2024: +0.022 | 2025: +0.056 | 2026: -0.024
- Yearly Tail ICs:   2015: +0.104 | 2016: +0.173 | 2017: -0.114 | 2018: +0.462 | 2019: +0.354 | 2020: +0.122 | 2021: +0.319 | 2022: +0.191 | 2023: +0.050 | 2024: +0.041 | 2025: +0.222 | 2026: +0.117
- IC CV=0.85, Neg years (linear/tail)=1/1 of 7, Half ratio=1.30, Recency ratio=0.74
- Early IC=+0.1355, Recent IC=+0.1000, 1st-half IC=+0.0924, 2nd-half IC=+0.1197, Neg regimes=1/5
- Weak component: `rbreaker_buy_setup_proximity_early` (CV=1.62)
- Regime ICs: Q1_low_vol=-0.065, Q2=+0.012, Q3_mid=+0.096, Q4=+0.230, Q5_high_vol=+0.173

**`combo_min__max_up_ret__volume_weighted_price_position`** (Lock IC=+0.0486, Sharpe=+0.2752)
- Admission: Train IC=+0.2051, Deflated=+0.2042, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.095 | 2016: +0.087 | 2017: -0.009 | 2018: +0.218 | 2019: +0.037 | 2020: -0.009 | 2021: +0.163 | 2022: +0.056 | 2023: +0.174 | 2024: -0.002 | 2025: +0.084 | 2026: -0.143
- Yearly Tail ICs:   2015: -0.001 | 2016: +0.035 | 2017: +0.227 | 2018: +0.350 | 2019: +0.255 | 2020: +0.064 | 2021: +0.380 | 2022: +0.268 | 2023: +0.380 | 2024: +0.032 | 2025: -0.046 | 2026: -0.191
- IC CV=0.95, Neg years (linear/tail)=2/1 of 7, Half ratio=1.09, Recency ratio=0.84
- Early IC=+0.0910, Recent IC=+0.0767, 1st-half IC=+0.0887, 2nd-half IC=+0.0962, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.014, Q2=+0.074, Q3_mid=+0.146, Q4=+0.066, Q5_high_vol=+0.145

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0`** (Lock IC=+0.0632, Sharpe=+0.2334)
- Admission: Train IC=+0.2257, Deflated=+0.2252, IR=0.59, Mono=0.73, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.108 | 2017: -0.026 | 2018: +0.206 | 2019: +0.094 | 2020: +0.061 | 2021: +0.155 | 2022: +0.077 | 2023: +0.126 | 2024: +0.029 | 2025: +0.071 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.266 | 2016: +0.091 | 2017: -0.003 | 2018: +0.285 | 2019: +0.205 | 2020: +0.194 | 2021: +0.366 | 2022: +0.263 | 2023: +0.221 | 2024: +0.107 | 2025: +0.081 | 2026: +0.060
- IC CV=0.66, Neg years (linear/tail)=1/1 of 7, Half ratio=0.96, Recency ratio=0.73
- Early IC=+0.1488, Recent IC=+0.1080, 1st-half IC=+0.1317, 2nd-half IC=+0.1259, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.013, Q2=+0.046, Q3_mid=+0.118, Q4=+0.200, Q5_high_vol=+0.212

**`combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position`** (Lock IC=+0.0534, Sharpe=+0.2178)
- Admission: Train IC=+0.2240, Deflated=+0.2229, IR=0.80, Mono=0.79, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.093 | 2016: +0.030 | 2017: +0.039 | 2018: +0.150 | 2019: +0.044 | 2020: +0.011 | 2021: +0.194 | 2022: +0.045 | 2023: +0.196 | 2024: +0.038 | 2025: +0.106 | 2026: -0.206
- Yearly Tail ICs:   2015: +0.108 | 2016: +0.101 | 2017: +0.156 | 2018: +0.425 | 2019: +0.208 | 2020: +0.213 | 2021: +0.325 | 2022: +0.238 | 2023: +0.225 | 2024: +0.102 | 2025: +0.226 | 2026: -0.338
- IC CV=0.79, Neg years (linear/tail)=0/0 of 7, Half ratio=1.62, Recency ratio=1.67
- Early IC=+0.0614, Recent IC=+0.1023, 1st-half IC=+0.0643, 2nd-half IC=+0.1045, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.035, Q2=+0.047, Q3_mid=+0.077, Q4=+0.098, Q5_high_vol=+0.153

**`combo_clamp_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0555, Sharpe=+0.2131)
- Admission: Train IC=+0.1570, Deflated=+0.1561, IR=0.51, Mono=0.68, p=0.0036, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.098 | 2016: +0.068 | 2017: +0.034 | 2018: +0.193 | 2019: +0.044 | 2020: +0.042 | 2021: +0.166 | 2022: +0.017 | 2023: +0.160 | 2024: +0.115 | 2025: +0.020 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.208 | 2017: +0.139 | 2018: +0.354 | 2019: +0.158 | 2020: +0.046 | 2021: +0.209 | 2022: +0.019 | 2023: +0.234 | 2024: +0.156 | 2025: -0.023 | 2026: -0.122
- IC CV=0.64, Neg years (linear/tail)=0/0 of 7, Half ratio=1.30, Recency ratio=1.25
- Early IC=+0.0830, Recent IC=+0.1038, 1st-half IC=+0.0870, 2nd-half IC=+0.1131, Neg regimes=1/5
- Weak component: `early_vwap_acceleration` (CV=0.99)
- Regime ICs: Q1_low_vol=-0.029, Q2=+0.071, Q3_mid=+0.087, Q4=+0.187, Q5_high_vol=+0.135

**`combo_diff__max_up_ret__early_vwap_acceleration`** (Lock IC=+0.0557, Sharpe=+0.2131)
- Admission: Train IC=+0.1327, Deflated=+0.1318, IR=0.56, Mono=0.71, p=0.0114, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.091 | 2016: +0.067 | 2017: +0.038 | 2018: +0.192 | 2019: +0.045 | 2020: +0.041 | 2021: +0.164 | 2022: +0.018 | 2023: +0.160 | 2024: +0.115 | 2025: +0.020 | 2026: -0.078
- Yearly Tail ICs:   2015: -0.034 | 2016: +0.140 | 2017: +0.235 | 2018: +0.329 | 2019: +0.184 | 2020: +0.017 | 2021: +0.163 | 2022: +0.058 | 2023: +0.218 | 2024: +0.161 | 2025: -0.015 | 2026: -0.087
- IC CV=0.64, Neg years (linear/tail)=0/1 of 7, Half ratio=1.32, Recency ratio=1.30
- Early IC=+0.0789, Recent IC=+0.1026, 1st-half IC=+0.0856, 2nd-half IC=+0.1131, Neg regimes=1/5
- Weak component: `early_vwap_acceleration` (CV=0.99)
- Regime ICs: Q1_low_vol=-0.026, Q2=+0.071, Q3_mid=+0.087, Q4=+0.187, Q5_high_vol=+0.131

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0513, Sharpe=+0.2085)
- Admission: Train IC=+0.2874, Deflated=+0.2868, IR=0.82, Mono=0.81, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.088 | 2017: -0.043 | 2018: +0.214 | 2019: +0.118 | 2020: +0.070 | 2021: +0.175 | 2022: +0.011 | 2023: +0.139 | 2024: +0.066 | 2025: +0.034 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.144 | 2017: +0.077 | 2018: +0.394 | 2019: +0.368 | 2020: +0.168 | 2021: +0.502 | 2022: +0.240 | 2023: +0.115 | 2024: +0.335 | 2025: -0.047 | 2026: +0.050
- IC CV=0.73, Neg years (linear/tail)=1/0 of 7, Half ratio=1.06, Recency ratio=0.74
- Early IC=+0.1646, Recent IC=+0.1224, 1st-half IC=+0.1329, 2nd-half IC=+0.1409, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.024, Q2=+0.008, Q3_mid=+0.133, Q4=+0.240, Q5_high_vol=+0.212

**`star50_limit_proximity_early`** (Lock IC=+0.0720, Sharpe=+0.2049)
- Admission: Train IC=+0.1745, Deflated=+0.1743, IR=0.49, Mono=0.70, p=0.0016, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.059 | 2017: -0.103 | 2018: +0.108 | 2019: +0.076 | 2020: +0.041 | 2021: +0.102 | 2022: +0.097 | 2023: +0.030 | 2024: +0.001 | 2025: +0.045 | 2026: +0.162
- Yearly Tail ICs:   2015: +0.158 | 2016: +0.132 | 2017: -0.017 | 2018: +0.273 | 2019: +0.161 | 2020: +0.180 | 2021: +0.093 | 2022: +0.181 | 2023: -0.240 | 2024: +0.224 | 2025: -0.012 | 2026: +0.288
- IC CV=1.21, Neg years (linear/tail)=1/1 of 7, Half ratio=0.74, Recency ratio=0.59
- Early IC=+0.1228, Recent IC=+0.0719, 1st-half IC=+0.1004, 2nd-half IC=+0.0740, Neg regimes=2/5
- Regime ICs: Q1_low_vol=-0.079, Q2=-0.027, Q3_mid=+0.045, Q4=+0.184, Q5_high_vol=+0.153

**`combo_max__first_bar_return__bar_body_rng_0`** (Lock IC=+0.0545, Sharpe=+0.2038)
- Admission: Train IC=+0.1830, Deflated=+0.1824, IR=0.51, Mono=0.70, p=0.0006, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.092 | 2016: +0.110 | 2017: +0.049 | 2018: +0.194 | 2019: +0.095 | 2020: +0.006 | 2021: +0.139 | 2022: +0.039 | 2023: +0.142 | 2024: +0.028 | 2025: +0.076 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.105 | 2016: +0.066 | 2017: +0.065 | 2018: +0.324 | 2019: +0.150 | 2020: +0.184 | 2021: +0.319 | 2022: +0.351 | 2023: +0.255 | 2024: +0.064 | 2025: +0.154 | 2026: -0.333
- IC CV=0.57, Neg years (linear/tail)=0/0 of 7, Half ratio=1.12, Recency ratio=0.72
- Early IC=+0.1010, Recent IC=+0.0728, 1st-half IC=+0.0958, 2nd-half IC=+0.1071, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.64)
- Regime ICs: Q1_low_vol=+0.071, Q2=+0.081, Q3_mid=+0.132, Q4=+0.098, Q5_high_vol=+0.152

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio`** (Lock IC=+0.0589, Sharpe=+0.1133)
- Admission: Train IC=+0.2119, Deflated=+0.2110, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.186 | 2016: +0.105 | 2017: -0.059 | 2018: +0.211 | 2019: +0.081 | 2020: +0.073 | 2021: +0.171 | 2022: +0.066 | 2023: +0.123 | 2024: +0.032 | 2025: +0.068 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.025 | 2016: +0.125 | 2017: +0.077 | 2018: +0.399 | 2019: +0.281 | 2020: +0.065 | 2021: +0.349 | 2022: +0.219 | 2023: +0.089 | 2024: +0.211 | 2025: +0.089 | 2026: +0.042
- IC CV=0.77, Neg years (linear/tail)=1/0 of 7, Half ratio=1.15, Recency ratio=0.84
- Early IC=+0.1456, Recent IC=+0.1219, 1st-half IC=+0.1126, 2nd-half IC=+0.1295, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=1.14)
- Regime ICs: Q1_low_vol=-0.047, Q2=+0.027, Q3_mid=+0.104, Q4=+0.227, Q5_high_vol=+0.202

**`combo_ratio__bar_body_rng_0__volume_weighted_price_position`** (Lock IC=+0.0472, Sharpe=+0.0580)
- Admission: Train IC=+0.1898, Deflated=+0.1897, IR=0.65, Mono=0.75, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.101 | 2016: +0.099 | 2017: +0.068 | 2018: +0.199 | 2019: +0.093 | 2020: -0.002 | 2021: +0.156 | 2022: +0.028 | 2023: +0.137 | 2024: +0.039 | 2025: +0.058 | 2026: -0.098
- Yearly Tail ICs:   2015: +0.167 | 2016: +0.055 | 2017: +0.207 | 2018: +0.385 | 2019: +0.133 | 2020: +0.033 | 2021: +0.203 | 2022: +0.122 | 2023: +0.108 | 2024: +0.061 | 2025: +0.105 | 2026: -0.330
- IC CV=0.58, Neg years (linear/tail)=1/0 of 7, Half ratio=1.19, Recency ratio=0.77
- Early IC=+0.1003, Recent IC=+0.0769, 1st-half IC=+0.0926, 2nd-half IC=+0.1099, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.099, Q2=+0.052, Q3_mid=+0.124, Q4=+0.091, Q5_high_vol=+0.162

**`combo_rank_max__bar_ret_0__volume_weighted_price_position`** (Lock IC=+0.0489, Sharpe=+0.0550)
- Admission: Train IC=+0.2066, Deflated=+0.2055, IR=0.65, Mono=0.72, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.090 | 2016: +0.032 | 2017: +0.051 | 2018: +0.189 | 2019: +0.057 | 2020: -0.007 | 2021: +0.167 | 2022: +0.055 | 2023: +0.189 | 2024: +0.001 | 2025: +0.086 | 2026: -0.174
- Yearly Tail ICs:   2015: +0.108 | 2016: -0.059 | 2017: +0.161 | 2018: +0.434 | 2019: +0.187 | 2020: +0.228 | 2021: +0.380 | 2022: +0.205 | 2023: +0.135 | 2024: +0.112 | 2025: +0.221 | 2026: -0.343
- IC CV=0.79, Neg years (linear/tail)=1/1 of 7, Half ratio=1.28, Recency ratio=1.27
- Early IC=+0.0633, Recent IC=+0.0805, 1st-half IC=+0.0784, 2nd-half IC=+0.1004, Neg regimes=0/5
- Weak component: `volume_weighted_price_position` (CV=1.30)
- Regime ICs: Q1_low_vol=+0.047, Q2=+0.063, Q3_mid=+0.124, Q4=+0.049, Q5_high_vol=+0.164

### 500ETF — `single` True Positives

**`combo_rank_min__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1098, Sharpe=+1.3146)
- Admission: Train IC=+0.2846, Deflated=+0.2837, IR=0.74, Mono=0.75, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.062 | 2017: +0.234 | 2018: +0.094 | 2019: +0.126 | 2020: +0.128 | 2021: +0.102 | 2022: +0.063 | 2023: +0.081 | 2024: +0.147 | 2025: +0.138 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.304 | 2016: +0.179 | 2017: +0.308 | 2018: +0.369 | 2019: +0.230 | 2020: +0.307 | 2021: +0.069 | 2022: +0.163 | 2023: +0.183 | 2024: +0.355 | 2025: +0.082 | 2026: +0.280
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.77, Recency ratio=0.84
- Early IC=+0.1382, Recent IC=+0.1159, 1st-half IC=+0.1598, 2nd-half IC=+0.1226, Neg regimes=1/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.000, Q3_mid=+0.106, Q4=+0.159, Q5_high_vol=+0.190

**`combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.1086, Sharpe=+1.1207)
- Admission: Train IC=+0.2960, Deflated=+0.2948, IR=0.95, Mono=0.80, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.089 | 2017: +0.229 | 2018: +0.148 | 2019: +0.120 | 2020: +0.129 | 2021: +0.119 | 2022: +0.091 | 2023: +0.097 | 2024: +0.115 | 2025: +0.148 | 2026: +0.046
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.219 | 2017: +0.254 | 2018: +0.349 | 2019: +0.254 | 2020: +0.312 | 2021: +0.080 | 2022: +0.240 | 2023: +0.232 | 2024: +0.396 | 2025: +0.151 | 2026: +0.205
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.79
- Early IC=+0.1570, Recent IC=+0.1241, 1st-half IC=+0.1899, 2nd-half IC=+0.1266, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.024, Q3_mid=+0.134, Q4=+0.191, Q5_high_vol=+0.184

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.1042, Sharpe=+1.0863)
- Admission: Train IC=+0.3044, Deflated=+0.3038, IR=1.04, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.106 | 2017: +0.199 | 2018: +0.145 | 2019: +0.129 | 2020: +0.151 | 2021: +0.158 | 2022: +0.089 | 2023: +0.109 | 2024: +0.132 | 2025: +0.113 | 2026: +0.036
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.218 | 2017: +0.247 | 2018: +0.338 | 2019: +0.244 | 2020: +0.306 | 2021: +0.244 | 2022: +0.301 | 2023: +0.278 | 2024: +0.388 | 2025: +0.117 | 2026: +0.203
- IC CV=0.25, Neg years (linear/tail)=0/0 of 7, Half ratio=0.74, Recency ratio=0.91
- Early IC=+0.1705, Recent IC=+0.1545, 1st-half IC=+0.1947, 2nd-half IC=+0.1450, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.037, Q3_mid=+0.156, Q4=+0.214, Q5_high_vol=+0.193

**`combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1023, Sharpe=+1.0699)
- Admission: Train IC=+0.2808, Deflated=+0.2797, IR=0.56, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.068 | 2017: +0.215 | 2018: +0.110 | 2019: +0.100 | 2020: +0.099 | 2021: +0.090 | 2022: +0.057 | 2023: +0.109 | 2024: +0.134 | 2025: +0.127 | 2026: +0.054
- Yearly Tail ICs:   2015: +0.268 | 2016: +0.161 | 2017: +0.291 | 2018: +0.315 | 2019: +0.212 | 2020: +0.329 | 2021: +0.017 | 2022: +0.274 | 2023: +0.149 | 2024: +0.254 | 2025: +0.059 | 2026: +0.161
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.61, Recency ratio=0.70
- Early IC=+0.1352, Recent IC=+0.0945, 1st-half IC=+0.1604, 2nd-half IC=+0.0984, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.009, Q3_mid=+0.081, Q4=+0.172, Q5_high_vol=+0.158

**`combo_rel_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.0928, Sharpe=+1.0646)
- Admission: Train IC=+0.2669, Deflated=+0.2662, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.022 | 2017: +0.204 | 2018: +0.144 | 2019: +0.184 | 2020: +0.146 | 2021: +0.092 | 2022: +0.052 | 2023: +0.067 | 2024: +0.098 | 2025: +0.034 | 2026: +0.241
- Yearly Tail ICs:   2015: +0.321 | 2016: -0.066 | 2017: +0.335 | 2018: +0.258 | 2019: +0.361 | 2020: +0.211 | 2021: +0.283 | 2022: -0.062 | 2023: +0.259 | 2024: +0.215 | 2025: -0.018 | 2026: +0.293
- IC CV=0.51, Neg years (linear/tail)=0/1 of 7, Half ratio=0.88, Recency ratio=0.75
- Early IC=+0.1577, Recent IC=+0.1189, 1st-half IC=+0.1709, 2nd-half IC=+0.1510, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.069, Q3_mid=+0.132, Q4=+0.104, Q5_high_vol=+0.298

**`combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow`** (Lock IC=+0.1082, Sharpe=+1.0612)
- Admission: Train IC=+0.2950, Deflated=+0.2941, IR=0.93, Mono=0.80, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.217 | 2016: +0.096 | 2017: +0.227 | 2018: +0.137 | 2019: +0.123 | 2020: +0.150 | 2021: +0.116 | 2022: +0.070 | 2023: +0.090 | 2024: +0.121 | 2025: +0.148 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.328 | 2016: +0.248 | 2017: +0.311 | 2018: +0.407 | 2019: +0.129 | 2020: +0.336 | 2021: +0.116 | 2022: +0.084 | 2023: +0.195 | 2024: +0.361 | 2025: +0.093 | 2026: +0.243
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.85
- Early IC=+0.1560, Recent IC=+0.1332, 1st-half IC=+0.1887, 2nd-half IC=+0.1341, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.050, Q3_mid=+0.118, Q4=+0.196, Q5_high_vol=+0.184

**`combo_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0905, Sharpe=+1.0186)
- Admission: Train IC=+0.2535, Deflated=+0.2526, IR=0.74, Mono=0.77, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.096 | 2017: +0.204 | 2018: +0.221 | 2019: +0.164 | 2020: +0.136 | 2021: +0.115 | 2022: +0.066 | 2023: +0.089 | 2024: +0.143 | 2025: +0.111 | 2026: -0.012
- Yearly Tail ICs:   2015: +0.416 | 2016: -0.169 | 2017: +0.314 | 2018: +0.264 | 2019: +0.280 | 2020: +0.041 | 2021: +0.285 | 2022: +0.159 | 2023: +0.058 | 2024: +0.311 | 2025: +0.133 | 2026: -0.155
- IC CV=0.34, Neg years (linear/tail)=0/1 of 7, Half ratio=0.80, Recency ratio=0.68
- Early IC=+0.1851, Recent IC=+0.1256, 1st-half IC=+0.1985, 2nd-half IC=+0.1582, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.063, Q3_mid=+0.190, Q4=+0.172, Q5_high_vol=+0.271

**`combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1035, Sharpe=+1.0166)
- Admission: Train IC=+0.2848, Deflated=+0.2842, IR=0.85, Mono=0.79, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.099 | 2017: +0.233 | 2018: +0.132 | 2019: +0.098 | 2020: +0.133 | 2021: +0.117 | 2022: +0.056 | 2023: +0.096 | 2024: +0.118 | 2025: +0.140 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.267 | 2016: +0.228 | 2017: +0.343 | 2018: +0.291 | 2019: +0.226 | 2020: +0.281 | 2021: +0.290 | 2022: +0.057 | 2023: +0.199 | 2024: +0.212 | 2025: +0.046 | 2026: +0.090
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.83
- Early IC=+0.1531, Recent IC=+0.1267, 1st-half IC=+0.1893, 2nd-half IC=+0.1184, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.062, Q3_mid=+0.088, Q4=+0.197, Q5_high_vol=+0.171

**`combo_sig_product__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1190, Sharpe=+0.9993)
- Admission: Train IC=+0.2335, Deflated=+0.2332, IR=0.55, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.231 | 2016: +0.119 | 2017: +0.067 | 2018: +0.148 | 2019: +0.092 | 2020: +0.137 | 2021: +0.130 | 2022: +0.145 | 2023: +0.148 | 2024: +0.127 | 2025: +0.133 | 2026: +0.026
- Yearly Tail ICs:   2015: +0.302 | 2016: +0.010 | 2017: +0.259 | 2018: +0.219 | 2019: +0.368 | 2020: +0.223 | 2021: +0.281 | 2022: +0.241 | 2023: +0.293 | 2024: +0.228 | 2025: +0.065 | 2026: +0.000
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.90, Recency ratio=0.76
- Early IC=+0.1752, Recent IC=+0.1334, 1st-half IC=+0.1573, 2nd-half IC=+0.1410, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.105, Q2=+0.064, Q3_mid=+0.133, Q4=+0.177, Q5_high_vol=+0.238

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1029, Sharpe=+0.9892)
- Admission: Train IC=+0.2905, Deflated=+0.2900, IR=0.86, Mono=0.79, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.110 | 2017: +0.207 | 2018: +0.138 | 2019: +0.113 | 2020: +0.130 | 2021: +0.155 | 2022: +0.070 | 2023: +0.117 | 2024: +0.134 | 2025: +0.120 | 2026: +0.032
- Yearly Tail ICs:   2015: +0.263 | 2016: +0.167 | 2017: +0.315 | 2018: +0.358 | 2019: +0.238 | 2020: +0.260 | 2021: +0.277 | 2022: +0.266 | 2023: +0.258 | 2024: +0.297 | 2025: +0.217 | 2026: +0.225
- IC CV=0.26, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.87
- Early IC=+0.1640, Recent IC=+0.1425, 1st-half IC=+0.1908, 2nd-half IC=+0.1307, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.045, Q3_mid=+0.121, Q4=+0.209, Q5_high_vol=+0.174

**`combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.1025, Sharpe=+0.9501)
- Admission: Train IC=+0.2756, Deflated=+0.2750, IR=0.90, Mono=0.79, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.083 | 2017: +0.228 | 2018: +0.200 | 2019: +0.142 | 2020: +0.176 | 2021: +0.115 | 2022: +0.083 | 2023: +0.082 | 2024: +0.136 | 2025: +0.103 | 2026: +0.062
- Yearly Tail ICs:   2015: +0.372 | 2016: +0.155 | 2017: +0.294 | 2018: +0.333 | 2019: +0.329 | 2020: +0.125 | 2021: +0.236 | 2022: +0.345 | 2023: +0.191 | 2024: +0.211 | 2025: +0.006 | 2026: +0.049
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.81
- Early IC=+0.1806, Recent IC=+0.1457, 1st-half IC=+0.2056, 2nd-half IC=+0.1629, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.041, Q3_mid=+0.171, Q4=+0.178, Q5_high_vol=+0.265

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.1003, Sharpe=+0.9373)
- Admission: Train IC=+0.2978, Deflated=+0.2973, IR=0.86, Mono=0.76, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.085 | 2017: +0.223 | 2018: +0.202 | 2019: +0.130 | 2020: +0.154 | 2021: +0.156 | 2022: +0.044 | 2023: +0.107 | 2024: +0.139 | 2025: +0.117 | 2026: +0.051
- Yearly Tail ICs:   2015: +0.301 | 2016: +0.167 | 2017: +0.351 | 2018: +0.414 | 2019: +0.267 | 2020: +0.223 | 2021: +0.217 | 2022: +0.205 | 2023: +0.191 | 2024: +0.345 | 2025: +0.050 | 2026: +0.206
- IC CV=0.29, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.99
- Early IC=+0.1567, Recent IC=+0.1550, 1st-half IC=+0.1880, 2nd-half IC=+0.1599, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.055, Q3_mid=+0.157, Q4=+0.191, Q5_high_vol=+0.214

**`combo_min__net_volume_flow__first_bar_return`** (Lock IC=+0.0955, Sharpe=+0.9174)
- Admission: Train IC=+0.2369, Deflated=+0.2358, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.196 | 2016: +0.069 | 2017: +0.182 | 2018: +0.174 | 2019: +0.117 | 2020: +0.098 | 2021: +0.085 | 2022: +0.090 | 2023: +0.082 | 2024: +0.137 | 2025: +0.125 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.009 | 2017: +0.261 | 2018: +0.376 | 2019: +0.136 | 2020: +0.144 | 2021: +0.275 | 2022: +0.224 | 2023: +0.324 | 2024: +0.367 | 2025: +0.140 | 2026: -0.024
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1326, Recent IC=+0.0918, 1st-half IC=+0.1500, 2nd-half IC=+0.1229, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.027, Q3_mid=+0.157, Q4=+0.131, Q5_high_vol=+0.189

**`combo_min__net_volume_flow__bar_ret_0`** (Lock IC=+0.0955, Sharpe=+0.9174)
- Admission: Train IC=+0.2366, Deflated=+0.2356, IR=0.69, Mono=0.75, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.069 | 2017: +0.182 | 2018: +0.174 | 2019: +0.117 | 2020: +0.098 | 2021: +0.085 | 2022: +0.090 | 2023: +0.082 | 2024: +0.138 | 2025: +0.125 | 2026: -0.010
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.009 | 2017: +0.261 | 2018: +0.376 | 2019: +0.136 | 2020: +0.142 | 2021: +0.278 | 2022: +0.221 | 2023: +0.324 | 2024: +0.367 | 2025: +0.140 | 2026: -0.024
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.82, Recency ratio=0.69
- Early IC=+0.1324, Recent IC=+0.0918, 1st-half IC=+0.1499, 2nd-half IC=+0.1228, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.027, Q3_mid=+0.157, Q4=+0.131, Q5_high_vol=+0.189

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1013, Sharpe=+0.9131)
- Admission: Train IC=+0.3432, Deflated=+0.3433, IR=1.11, Mono=0.84, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.120 | 2017: +0.223 | 2018: +0.186 | 2019: +0.173 | 2020: +0.174 | 2021: +0.143 | 2022: +0.016 | 2023: +0.107 | 2024: +0.166 | 2025: +0.087 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.399 | 2016: +0.196 | 2017: +0.346 | 2018: +0.519 | 2019: +0.342 | 2020: +0.242 | 2021: +0.291 | 2022: +0.186 | 2023: +0.116 | 2024: +0.325 | 2025: -0.030 | 2026: +0.165
- IC CV=0.26, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.79
- Early IC=+0.1996, Recent IC=+0.1583, 1st-half IC=+0.2183, 2nd-half IC=+0.1739, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.090, Q3_mid=+0.158, Q4=+0.213, Q5_high_vol=+0.262

**`combo_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0866, Sharpe=+0.9094)
- Admission: Train IC=+0.2676, Deflated=+0.2674, IR=0.95, Mono=0.81, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.272 | 2016: +0.102 | 2017: +0.133 | 2018: +0.281 | 2019: +0.179 | 2020: +0.173 | 2021: +0.173 | 2022: +0.052 | 2023: +0.100 | 2024: +0.158 | 2025: +0.055 | 2026: +0.013
- Yearly Tail ICs:   2015: +0.298 | 2016: +0.197 | 2017: +0.308 | 2018: +0.601 | 2019: +0.196 | 2020: +0.112 | 2021: +0.281 | 2022: +0.162 | 2023: +0.261 | 2024: +0.190 | 2025: +0.013 | 2026: +0.013
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=1.00, Recency ratio=0.92
- Early IC=+0.1873, Recent IC=+0.1727, 1st-half IC=+0.2014, 2nd-half IC=+0.2015, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.156, Q2=+0.128, Q3_mid=+0.193, Q4=+0.163, Q5_high_vol=+0.324

**`combo_rank_min__net_volume_flow__max_down_ret`** (Lock IC=+0.0930, Sharpe=+0.9059)
- Admission: Train IC=+0.2081, Deflated=+0.2069, IR=0.58, Mono=0.71, p=0.0006, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.073 | 2017: +0.207 | 2018: +0.134 | 2019: +0.084 | 2020: +0.142 | 2021: +0.067 | 2022: +0.083 | 2023: +0.075 | 2024: +0.116 | 2025: +0.122 | 2026: +0.021
- Yearly Tail ICs:   2015: +0.315 | 2016: -0.034 | 2017: +0.199 | 2018: +0.141 | 2019: +0.196 | 2020: +0.246 | 2021: +0.298 | 2022: +0.264 | 2023: +0.225 | 2024: +0.269 | 2025: +0.125 | 2026: -0.035
- IC CV=0.49, Neg years (linear/tail)=0/1 of 7, Half ratio=0.81, Recency ratio=0.62
- Early IC=+0.1699, Recent IC=+0.1062, 1st-half IC=+0.1481, 2nd-half IC=+0.1193, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.174, Q2=-0.033, Q3_mid=+0.152, Q4=+0.091, Q5_high_vol=+0.229

**`combo_mean__volatility_expansion_trend_vector__close_vs_open_range`** (Lock IC=+0.0928, Sharpe=+0.9014)
- Admission: Train IC=+0.2342, Deflated=+0.2333, IR=0.52, Mono=0.72, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.180 | 2016: +0.072 | 2017: +0.196 | 2018: +0.120 | 2019: +0.068 | 2020: +0.103 | 2021: +0.069 | 2022: +0.093 | 2023: +0.089 | 2024: +0.126 | 2025: +0.154 | 2026: -0.074
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.106 | 2017: +0.315 | 2018: +0.241 | 2019: +0.189 | 2020: +0.230 | 2021: +0.216 | 2022: +0.156 | 2023: +0.162 | 2024: +0.285 | 2025: -0.011 | 2026: -0.002
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.66, Recency ratio=0.68
- Early IC=+0.1257, Recent IC=+0.0859, 1st-half IC=+0.1428, 2nd-half IC=+0.0945, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.192, Q2=-0.012, Q3_mid=+0.132, Q4=+0.128, Q5_high_vol=+0.142

**`combo_rank_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0898, Sharpe=+0.8833)
- Admission: Train IC=+0.2443, Deflated=+0.2433, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.073 | 2017: +0.176 | 2018: +0.136 | 2019: +0.076 | 2020: +0.099 | 2021: +0.063 | 2022: +0.080 | 2023: +0.093 | 2024: +0.130 | 2025: +0.140 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.122 | 2017: +0.348 | 2018: +0.222 | 2019: +0.196 | 2020: +0.261 | 2021: +0.207 | 2022: +0.146 | 2023: +0.270 | 2024: +0.265 | 2025: -0.017 | 2026: -0.063
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.69
- Early IC=+0.1167, Recent IC=+0.0809, 1st-half IC=+0.1365, 2nd-half IC=+0.0934, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.029, Q3_mid=+0.151, Q4=+0.129, Q5_high_vol=+0.149

**`morning_volume_weighted_momentum`** (Lock IC=+0.0893, Sharpe=+0.8807)
- Admission: Train IC=+0.1488, Deflated=+0.1481, IR=0.43, Mono=0.66, p=0.0076, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.139 | 2016: +0.039 | 2017: +0.203 | 2018: +0.126 | 2019: +0.090 | 2020: +0.097 | 2021: +0.088 | 2022: +0.095 | 2023: +0.096 | 2024: +0.115 | 2025: +0.165 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.078 | 2017: +0.280 | 2018: +0.104 | 2019: +0.039 | 2020: +0.117 | 2021: +0.174 | 2022: +0.149 | 2023: +0.283 | 2024: +0.184 | 2025: +0.241 | 2026: -0.108
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=1.04
- Early IC=+0.0893, Recent IC=+0.0925, 1st-half IC=+0.1300, 2nd-half IC=+0.1021, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.028, Q3_mid=+0.145, Q4=+0.111, Q5_high_vol=+0.122

**`combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0958, Sharpe=+0.8790)
- Admission: Train IC=+0.2777, Deflated=+0.2764, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.087 | 2017: +0.216 | 2018: +0.105 | 2019: +0.067 | 2020: +0.099 | 2021: +0.071 | 2022: +0.059 | 2023: +0.099 | 2024: +0.111 | 2025: +0.131 | 2026: +0.026
- Yearly Tail ICs:   2015: +0.334 | 2016: +0.203 | 2017: +0.352 | 2018: +0.308 | 2019: +0.086 | 2020: +0.250 | 2021: +0.079 | 2022: +0.220 | 2023: -0.028 | 2024: +0.333 | 2025: +0.169 | 2026: +0.141
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.53, Recency ratio=0.72
- Early IC=+0.1184, Recent IC=+0.0850, 1st-half IC=+0.1549, 2nd-half IC=+0.0824, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.028, Q3_mid=+0.083, Q4=+0.163, Q5_high_vol=+0.121

**`combo_rank_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1040, Sharpe=+0.8783)
- Admission: Train IC=+0.2789, Deflated=+0.2783, IR=0.62, Mono=0.71, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.073 | 2017: +0.226 | 2018: +0.079 | 2019: +0.082 | 2020: +0.119 | 2021: +0.089 | 2022: +0.032 | 2023: +0.095 | 2024: +0.142 | 2025: +0.138 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.208 | 2017: +0.338 | 2018: +0.282 | 2019: +0.119 | 2020: +0.215 | 2021: +0.215 | 2022: +0.160 | 2023: +0.008 | 2024: +0.221 | 2025: +0.089 | 2026: +0.313
- IC CV=0.49, Neg years (linear/tail)=0/0 of 7, Half ratio=0.57, Recency ratio=0.71
- Early IC=+0.1481, Recent IC=+0.1050, 1st-half IC=+0.1663, 2nd-half IC=+0.0955, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.021, Q3_mid=+0.075, Q4=+0.159, Q5_high_vol=+0.166

**`combo_rel_diff__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0867, Sharpe=+0.8522)
- Admission: Train IC=+0.2768, Deflated=+0.2765, IR=1.04, Mono=0.83, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.269 | 2016: +0.084 | 2017: +0.123 | 2018: +0.245 | 2019: +0.173 | 2020: +0.192 | 2021: +0.170 | 2022: +0.037 | 2023: +0.101 | 2024: +0.137 | 2025: +0.067 | 2026: +0.050
- Yearly Tail ICs:   2015: +0.253 | 2016: +0.159 | 2017: +0.310 | 2018: +0.524 | 2019: +0.248 | 2020: +0.132 | 2021: +0.291 | 2022: +0.126 | 2023: +0.166 | 2024: +0.183 | 2025: -0.036 | 2026: +0.013
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=1.08, Recency ratio=1.03
- Early IC=+0.1765, Recent IC=+0.1809, 1st-half IC=+0.1867, 2nd-half IC=+0.2012, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.153, Q2=+0.136, Q3_mid=+0.178, Q4=+0.170, Q5_high_vol=+0.306

**`combo_clamp_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.0867, Sharpe=+0.8508)
- Admission: Train IC=+0.2618, Deflated=+0.2614, IR=0.73, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.302 | 2016: +0.066 | 2017: +0.183 | 2018: +0.155 | 2019: +0.186 | 2020: +0.128 | 2021: +0.072 | 2022: +0.046 | 2023: +0.064 | 2024: +0.092 | 2025: +0.009 | 2026: +0.258
- Yearly Tail ICs:   2015: +0.325 | 2016: +0.140 | 2017: +0.389 | 2018: +0.234 | 2019: +0.275 | 2020: +0.193 | 2021: +0.272 | 2022: -0.120 | 2023: +0.215 | 2024: +0.205 | 2025: -0.030 | 2026: +0.397
- IC CV=0.48, Neg years (linear/tail)=0/0 of 7, Half ratio=0.76, Recency ratio=0.54
- Early IC=+0.1841, Recent IC=+0.0998, 1st-half IC=+0.1887, 2nd-half IC=+0.1433, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.117, Q2=+0.089, Q3_mid=+0.127, Q4=+0.112, Q5_high_vol=+0.285

**`combo_diff__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.0852, Sharpe=+0.8508)
- Admission: Train IC=+0.2426, Deflated=+0.2421, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.059 | 2017: +0.181 | 2018: +0.157 | 2019: +0.189 | 2020: +0.129 | 2021: +0.070 | 2022: +0.047 | 2023: +0.062 | 2024: +0.088 | 2025: +0.007 | 2026: +0.256
- Yearly Tail ICs:   2015: +0.180 | 2016: -0.049 | 2017: +0.341 | 2018: +0.264 | 2019: +0.342 | 2020: +0.200 | 2021: +0.229 | 2022: -0.083 | 2023: +0.171 | 2024: +0.113 | 2025: -0.069 | 2026: +0.323
- IC CV=0.48, Neg years (linear/tail)=0/1 of 7, Half ratio=0.77, Recency ratio=0.56
- Early IC=+0.1781, Recent IC=+0.0992, 1st-half IC=+0.1870, 2nd-half IC=+0.1443, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.118, Q2=+0.089, Q3_mid=+0.128, Q4=+0.113, Q5_high_vol=+0.277

**`combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.0983, Sharpe=+0.8497)
- Admission: Train IC=+0.3140, Deflated=+0.3135, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.070 | 2017: +0.222 | 2018: +0.172 | 2019: +0.130 | 2020: +0.143 | 2021: +0.144 | 2022: +0.029 | 2023: +0.101 | 2024: +0.151 | 2025: +0.107 | 2026: +0.070
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.128 | 2017: +0.345 | 2018: +0.409 | 2019: +0.318 | 2020: +0.264 | 2021: +0.142 | 2022: +0.293 | 2023: +0.120 | 2024: +0.278 | 2025: -0.051 | 2026: +0.162
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.95
- Early IC=+0.1514, Recent IC=+0.1436, 1st-half IC=+0.1768, 2nd-half IC=+0.1505, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.037, Q3_mid=+0.144, Q4=+0.175, Q5_high_vol=+0.218

**`combo_min__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1023, Sharpe=+0.8451)
- Admission: Train IC=+0.2726, Deflated=+0.2717, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.076 | 2017: +0.220 | 2018: +0.085 | 2019: +0.077 | 2020: +0.110 | 2021: +0.087 | 2022: +0.040 | 2023: +0.100 | 2024: +0.146 | 2025: +0.134 | 2026: +0.076
- Yearly Tail ICs:   2015: +0.288 | 2016: +0.181 | 2017: +0.301 | 2018: +0.284 | 2019: +0.086 | 2020: +0.233 | 2021: +0.117 | 2022: +0.183 | 2023: +0.055 | 2024: +0.304 | 2025: +0.084 | 2026: +0.292
- IC CV=0.49, Neg years (linear/tail)=0/0 of 7, Half ratio=0.56, Recency ratio=0.67
- Early IC=+0.1476, Recent IC=+0.0983, 1st-half IC=+0.1657, 2nd-half IC=+0.0922, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.021, Q3_mid=+0.071, Q4=+0.164, Q5_high_vol=+0.162

**`combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.1036, Sharpe=+0.8369)
- Admission: Train IC=+0.2881, Deflated=+0.2877, IR=0.89, Mono=0.81, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.086 | 2017: +0.220 | 2018: +0.201 | 2019: +0.126 | 2020: +0.135 | 2021: +0.156 | 2022: +0.045 | 2023: +0.114 | 2024: +0.146 | 2025: +0.124 | 2026: +0.049
- Yearly Tail ICs:   2015: +0.322 | 2016: +0.128 | 2017: +0.296 | 2018: +0.428 | 2019: +0.318 | 2020: +0.220 | 2021: +0.264 | 2022: +0.235 | 2023: +0.138 | 2024: +0.293 | 2025: +0.057 | 2026: +0.214
- IC CV=0.29, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.99
- Early IC=+0.1471, Recent IC=+0.1456, 1st-half IC=+0.1848, 2nd-half IC=+0.1496, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.066, Q3_mid=+0.126, Q4=+0.192, Q5_high_vol=+0.198

**`combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0961, Sharpe=+0.8340)
- Admission: Train IC=+0.2836, Deflated=+0.2830, IR=0.81, Mono=0.77, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.071 | 2017: +0.233 | 2018: +0.180 | 2019: +0.106 | 2020: +0.165 | 2021: +0.096 | 2022: +0.077 | 2023: +0.084 | 2024: +0.127 | 2025: +0.103 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.380 | 2016: +0.162 | 2017: +0.356 | 2018: +0.283 | 2019: +0.273 | 2020: +0.186 | 2021: +0.219 | 2022: +0.291 | 2023: +0.115 | 2024: +0.169 | 2025: +0.096 | 2026: -0.070
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.81
- Early IC=+0.1617, Recent IC=+0.1302, 1st-half IC=+0.1968, 2nd-half IC=+0.1402, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.032, Q3_mid=+0.149, Q4=+0.176, Q5_high_vol=+0.236

**`combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0877, Sharpe=+0.8325)
- Admission: Train IC=+0.2728, Deflated=+0.2724, IR=0.68, Mono=0.74, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.038 | 2017: +0.204 | 2018: +0.197 | 2019: +0.180 | 2020: +0.173 | 2021: +0.120 | 2022: +0.055 | 2023: +0.103 | 2024: +0.119 | 2025: +0.049 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.072 | 2017: +0.292 | 2018: +0.226 | 2019: +0.502 | 2020: +0.189 | 2021: +0.159 | 2022: +0.217 | 2023: +0.081 | 2024: +0.331 | 2025: +0.189 | 2026: +0.060
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=1.08, Recency ratio=0.90
- Early IC=+0.1619, Recent IC=+0.1463, 1st-half IC=+0.1668, 2nd-half IC=+0.1808, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.091, Q3_mid=+0.163, Q4=+0.117, Q5_high_vol=+0.313

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.1091, Sharpe=+0.8305)
- Admission: Train IC=+0.2894, Deflated=+0.2884, IR=0.85, Mono=0.81, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.278 | 2016: +0.085 | 2017: +0.224 | 2018: +0.193 | 2019: +0.127 | 2020: +0.177 | 2021: +0.102 | 2022: +0.088 | 2023: +0.114 | 2024: +0.145 | 2025: +0.132 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.452 | 2016: +0.177 | 2017: +0.256 | 2018: +0.316 | 2019: +0.210 | 2020: +0.242 | 2021: +0.252 | 2022: +0.317 | 2023: +0.230 | 2024: +0.272 | 2025: +0.037 | 2026: -0.301
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.76, Recency ratio=0.77
- Early IC=+0.1817, Recent IC=+0.1396, 1st-half IC=+0.2026, 2nd-half IC=+0.1535, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.221, Q2=+0.037, Q3_mid=+0.177, Q4=+0.166, Q5_high_vol=+0.265

**`combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0972, Sharpe=+0.8261)
- Admission: Train IC=+0.2552, Deflated=+0.2542, IR=0.79, Mono=0.77, p=0.0000, MaxCorr=0.75
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.119 | 2017: +0.110 | 2018: +0.189 | 2019: +0.088 | 2020: +0.115 | 2021: +0.140 | 2022: +0.076 | 2023: +0.053 | 2024: +0.120 | 2025: +0.138 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.471 | 2016: +0.195 | 2017: +0.217 | 2018: +0.389 | 2019: -0.049 | 2020: +0.108 | 2021: +0.319 | 2022: +0.065 | 2023: +0.203 | 2024: +0.172 | 2025: +0.259 | 2026: +0.331
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.73, Recency ratio=0.66
- Early IC=+0.1934, Recent IC=+0.1275, 1st-half IC=+0.1821, 2nd-half IC=+0.1331, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.159, Q2=+0.047, Q3_mid=+0.127, Q4=+0.189, Q5_high_vol=+0.255

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1042, Sharpe=+0.8216)
- Admission: Train IC=+0.3197, Deflated=+0.3192, IR=0.93, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.045 | 2017: +0.226 | 2018: +0.140 | 2019: +0.157 | 2020: +0.154 | 2021: +0.138 | 2022: +0.032 | 2023: +0.096 | 2024: +0.174 | 2025: +0.105 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.360 | 2016: +0.163 | 2017: +0.307 | 2018: +0.406 | 2019: +0.362 | 2020: +0.212 | 2021: +0.216 | 2022: +0.114 | 2023: +0.006 | 2024: +0.367 | 2025: +0.039 | 2026: +0.231
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.92
- Early IC=+0.1572, Recent IC=+0.1447, 1st-half IC=+0.1829, 2nd-half IC=+0.1556, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.078, Q3_mid=+0.118, Q4=+0.162, Q5_high_vol=+0.242

**`combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1015, Sharpe=+0.8156)
- Admission: Train IC=+0.2712, Deflated=+0.2706, IR=0.76, Mono=0.74, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.121 | 2017: +0.149 | 2018: +0.156 | 2019: +0.094 | 2020: +0.138 | 2021: +0.059 | 2022: +0.123 | 2023: +0.071 | 2024: +0.090 | 2025: +0.111 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.230 | 2016: +0.264 | 2017: +0.232 | 2018: +0.327 | 2019: +0.271 | 2020: +0.176 | 2021: +0.128 | 2022: +0.252 | 2023: +0.165 | 2024: +0.207 | 2025: +0.124 | 2026: +0.075
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.61, Recency ratio=0.64
- Early IC=+0.1538, Recent IC=+0.0984, 1st-half IC=+0.1829, 2nd-half IC=+0.1111, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.171, Q2=+0.014, Q3_mid=+0.140, Q4=+0.174, Q5_high_vol=+0.191

**`combo_rank_max__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1137, Sharpe=+0.8084)
- Admission: Train IC=+0.2149, Deflated=+0.2142, IR=0.56, Mono=0.68, p=0.0004, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.057 | 2017: +0.230 | 2018: +0.093 | 2019: +0.123 | 2020: +0.133 | 2021: +0.031 | 2022: +0.096 | 2023: +0.036 | 2024: +0.139 | 2025: +0.111 | 2026: +0.152
- Yearly Tail ICs:   2015: +0.353 | 2016: +0.065 | 2017: +0.185 | 2018: +0.151 | 2019: +0.343 | 2020: +0.164 | 2021: +0.294 | 2022: +0.113 | 2023: +0.030 | 2024: +0.178 | 2025: +0.302 | 2026: +0.147
- IC CV=0.63, Neg years (linear/tail)=0/0 of 7, Half ratio=0.54, Recency ratio=0.46
- Early IC=+0.1764, Recent IC=+0.0819, 1st-half IC=+0.1913, 2nd-half IC=+0.1035, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.014, Q3_mid=+0.136, Q4=+0.060, Q5_high_vol=+0.259

**`combo_min__max_up_ret__trend_day_regime_conviction`** (Lock IC=+0.1005, Sharpe=+0.7982)
- Admission: Train IC=+0.2431, Deflated=+0.2420, IR=0.71, Mono=0.78, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.156 | 2016: +0.073 | 2017: +0.186 | 2018: +0.154 | 2019: +0.087 | 2020: +0.107 | 2021: +0.108 | 2022: +0.114 | 2023: +0.116 | 2024: +0.144 | 2025: +0.144 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.234 | 2016: +0.202 | 2017: +0.337 | 2018: +0.370 | 2019: +0.152 | 2020: +0.147 | 2021: +0.142 | 2022: +0.153 | 2023: +0.219 | 2024: +0.203 | 2025: +0.131 | 2026: -0.111
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.94
- Early IC=+0.1143, Recent IC=+0.1073, 1st-half IC=+0.1464, 2nd-half IC=+0.1159, Neg regimes=0/5
- Weak component: `trend_day_regime_conviction` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.037, Q3_mid=+0.156, Q4=+0.139, Q5_high_vol=+0.150

**`combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0924, Sharpe=+0.7891)
- Admission: Train IC=+0.2168, Deflated=+0.2169, IR=0.53, Mono=0.71, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.066 | 2017: +0.221 | 2018: +0.195 | 2019: +0.105 | 2020: +0.178 | 2021: +0.060 | 2022: +0.121 | 2023: +0.134 | 2024: +0.099 | 2025: +0.079 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.365 | 2016: -0.051 | 2017: +0.284 | 2018: +0.219 | 2019: +0.292 | 2020: +0.223 | 2021: +0.166 | 2022: +0.232 | 2023: +0.336 | 2024: +0.228 | 2025: -0.037 | 2026: -0.099
- IC CV=0.42, Neg years (linear/tail)=0/1 of 7, Half ratio=0.98, Recency ratio=0.93
- Early IC=+0.1284, Recent IC=+0.1193, 1st-half IC=+0.1511, 2nd-half IC=+0.1478, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.053, Q3_mid=+0.164, Q4=+0.132, Q5_high_vol=+0.202

**`combo_sig_product__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.1231, Sharpe=+0.7781)
- Admission: Train IC=+0.2059, Deflated=+0.2050, IR=0.54, Mono=0.67, p=0.0006, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.049 | 2017: +0.197 | 2018: +0.137 | 2019: +0.171 | 2020: +0.117 | 2021: +0.085 | 2022: +0.063 | 2023: +0.095 | 2024: +0.154 | 2025: +0.121 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.017 | 2016: +0.029 | 2017: +0.149 | 2018: +0.211 | 2019: +0.461 | 2020: +0.261 | 2021: +0.230 | 2022: +0.173 | 2023: +0.060 | 2024: +0.225 | 2025: +0.057 | 2026: +0.339
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.85
- Early IC=+0.1182, Recent IC=+0.1008, 1st-half IC=+0.1531, 2nd-half IC=+0.1305, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.064, Q3_mid=+0.083, Q4=+0.120, Q5_high_vol=+0.224

**`combo_mean__max_up_ret__close_vs_open_range`** (Lock IC=+0.0980, Sharpe=+0.7715)
- Admission: Train IC=+0.2481, Deflated=+0.2472, IR=0.88, Mono=0.80, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.095 | 2017: +0.213 | 2018: +0.173 | 2019: +0.086 | 2020: +0.133 | 2021: +0.103 | 2022: +0.108 | 2023: +0.104 | 2024: +0.141 | 2025: +0.115 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.284 | 2016: +0.297 | 2017: +0.272 | 2018: +0.334 | 2019: +0.139 | 2020: +0.188 | 2021: +0.275 | 2022: +0.062 | 2023: +0.193 | 2024: +0.246 | 2025: -0.061 | 2026: -0.171
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.73
- Early IC=+0.1619, Recent IC=+0.1178, 1st-half IC=+0.1855, 2nd-half IC=+0.1276, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.031, Q3_mid=+0.168, Q4=+0.146, Q5_high_vol=+0.230

**`combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0855, Sharpe=+0.7598)
- Admission: Train IC=+0.2868, Deflated=+0.2858, IR=0.97, Mono=0.83, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.053 | 2017: +0.155 | 2018: +0.232 | 2019: +0.172 | 2020: +0.164 | 2021: +0.163 | 2022: +0.057 | 2023: +0.093 | 2024: +0.130 | 2025: +0.092 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.428 | 2016: +0.029 | 2017: +0.189 | 2018: +0.387 | 2019: +0.254 | 2020: +0.221 | 2021: +0.335 | 2022: +0.240 | 2023: +0.307 | 2024: +0.305 | 2025: +0.101 | 2026: -0.329
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=1.17, Recency ratio=1.18
- Early IC=+0.1389, Recent IC=+0.1633, 1st-half IC=+0.1598, 2nd-half IC=+0.1864, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.071, Q3_mid=+0.185, Q4=+0.139, Q5_high_vol=+0.263

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0792, Sharpe=+0.7590)
- Admission: Train IC=+0.2965, Deflated=+0.2961, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.074 | 2017: +0.196 | 2018: +0.155 | 2019: +0.174 | 2020: +0.112 | 2021: +0.096 | 2022: +0.028 | 2023: +0.065 | 2024: +0.113 | 2025: +0.125 | 2026: +0.085
- Yearly Tail ICs:   2015: +0.237 | 2016: +0.096 | 2017: +0.236 | 2018: +0.369 | 2019: +0.337 | 2020: +0.243 | 2021: +0.058 | 2022: +0.131 | 2023: +0.087 | 2024: +0.315 | 2025: +0.118 | 2026: +0.101
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.57
- Early IC=+0.1816, Recent IC=+0.1037, 1st-half IC=+0.1915, 2nd-half IC=+0.1369, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.006, Q3_mid=+0.094, Q4=+0.171, Q5_high_vol=+0.245

**`combo_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.0790, Sharpe=+0.7590)
- Admission: Train IC=+0.2964, Deflated=+0.2960, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.074 | 2017: +0.196 | 2018: +0.155 | 2019: +0.173 | 2020: +0.112 | 2021: +0.096 | 2022: +0.028 | 2023: +0.065 | 2024: +0.114 | 2025: +0.125 | 2026: +0.086
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.096 | 2017: +0.236 | 2018: +0.369 | 2019: +0.340 | 2020: +0.243 | 2021: +0.058 | 2022: +0.130 | 2023: +0.086 | 2024: +0.315 | 2025: +0.118 | 2026: +0.101
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.57
- Early IC=+0.1815, Recent IC=+0.1037, 1st-half IC=+0.1915, 2nd-half IC=+0.1368, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.006, Q3_mid=+0.094, Q4=+0.172, Q5_high_vol=+0.245

**`combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum`** (Lock IC=+0.0766, Sharpe=+0.7547)
- Admission: Train IC=+0.2166, Deflated=+0.2160, IR=0.73, Mono=0.73, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.033 | 2017: +0.201 | 2018: +0.182 | 2019: +0.156 | 2020: +0.142 | 2021: +0.137 | 2022: +0.034 | 2023: +0.098 | 2024: +0.099 | 2025: +0.046 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.446 | 2016: +0.045 | 2017: +0.423 | 2018: +0.148 | 2019: +0.295 | 2020: +0.115 | 2021: +0.191 | 2022: +0.046 | 2023: +0.134 | 2024: +0.209 | 2025: +0.043 | 2026: +0.356
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=1.01, Recency ratio=0.85
- Early IC=+0.1639, Recent IC=+0.1395, 1st-half IC=+0.1645, 2nd-half IC=+0.1667, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.084, Q3_mid=+0.161, Q4=+0.117, Q5_high_vol=+0.285

**`combo_rank_max__max_up_ret__net_volume_flow`** (Lock IC=+0.0975, Sharpe=+0.7540)
- Admission: Train IC=+0.2493, Deflated=+0.2487, IR=0.83, Mono=0.79, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.102 | 2017: +0.185 | 2018: +0.218 | 2019: +0.083 | 2020: +0.125 | 2021: +0.095 | 2022: +0.106 | 2023: +0.095 | 2024: +0.139 | 2025: +0.102 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.323 | 2016: +0.221 | 2017: +0.239 | 2018: +0.288 | 2019: +0.129 | 2020: +0.309 | 2021: +0.299 | 2022: +0.153 | 2023: +0.212 | 2024: +0.308 | 2025: -0.033 | 2026: -0.308
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.64
- Early IC=+0.1710, Recent IC=+0.1094, 1st-half IC=+0.1951, 2nd-half IC=+0.1273, Neg regimes=0/5
- Weak component: `net_volume_flow` (CV=0.32)
- Regime ICs: Q1_low_vol=+0.176, Q2=+0.003, Q3_mid=+0.179, Q4=+0.165, Q5_high_vol=+0.273

**`combo_max__volatility_expansion_trend_vector__first_bar_sentiment`** (Lock IC=+0.0886, Sharpe=+0.7521)
- Admission: Train IC=+0.2298, Deflated=+0.2297, IR=0.50, Mono=0.68, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.115 | 2017: +0.167 | 2018: +0.160 | 2019: +0.084 | 2020: +0.115 | 2021: +0.136 | 2022: +0.128 | 2023: +0.053 | 2024: +0.120 | 2025: +0.120 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.045 | 2017: +0.157 | 2018: +0.229 | 2019: +0.299 | 2020: +0.173 | 2021: +0.154 | 2022: +0.309 | 2023: +0.191 | 2024: +0.253 | 2025: +0.105 | 2026: -0.289
- IC CV=0.30, Neg years (linear/tail)=0/1 of 7, Half ratio=0.78, Recency ratio=0.73
- Early IC=+0.1721, Recent IC=+0.1256, 1st-half IC=+0.1645, 2nd-half IC=+0.1290, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.001, Q3_mid=+0.177, Q4=+0.151, Q5_high_vol=+0.205

**`combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0858, Sharpe=+0.7450)
- Admission: Train IC=+0.3177, Deflated=+0.3175, IR=0.90, Mono=0.80, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.283 | 2016: +0.104 | 2017: +0.134 | 2018: +0.281 | 2019: +0.180 | 2020: +0.173 | 2021: +0.172 | 2022: +0.052 | 2023: +0.095 | 2024: +0.153 | 2025: +0.057 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.208 | 2017: +0.327 | 2018: +0.611 | 2019: +0.275 | 2020: +0.129 | 2021: +0.238 | 2022: +0.147 | 2023: +0.148 | 2024: +0.202 | 2025: +0.099 | 2026: +0.012
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.99, Recency ratio=0.89
- Early IC=+0.1934, Recent IC=+0.1721, 1st-half IC=+0.2037, 2nd-half IC=+0.2016, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.155, Q2=+0.128, Q3_mid=+0.198, Q4=+0.162, Q5_high_vol=+0.330

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0805, Sharpe=+0.7405)
- Admission: Train IC=+0.3068, Deflated=+0.3067, IR=0.61, Mono=0.73, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.092 | 2017: +0.215 | 2018: +0.203 | 2019: +0.177 | 2020: +0.142 | 2021: +0.098 | 2022: +0.041 | 2023: +0.078 | 2024: +0.091 | 2025: +0.124 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.155 | 2017: +0.169 | 2018: +0.459 | 2019: +0.286 | 2020: +0.274 | 2021: +0.162 | 2022: +0.108 | 2023: +0.162 | 2024: +0.281 | 2025: +0.156 | 2026: +0.171
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.70, Recency ratio=0.59
- Early IC=+0.2033, Recent IC=+0.1204, 1st-half IC=+0.2236, 2nd-half IC=+0.1554, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.037, Q3_mid=+0.113, Q4=+0.222, Q5_high_vol=+0.265

**`combo_rank_min__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0927, Sharpe=+0.7243)
- Admission: Train IC=+0.2041, Deflated=+0.2034, IR=0.59, Mono=0.74, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.048 | 2017: +0.223 | 2018: +0.166 | 2019: +0.110 | 2020: +0.147 | 2021: +0.099 | 2022: +0.078 | 2023: +0.080 | 2024: +0.120 | 2025: +0.121 | 2026: +0.039
- Yearly Tail ICs:   2015: +0.370 | 2016: -0.050 | 2017: +0.153 | 2018: +0.091 | 2019: +0.327 | 2020: +0.059 | 2021: +0.353 | 2022: +0.208 | 2023: +0.072 | 2024: +0.188 | 2025: +0.122 | 2026: -0.052
- IC CV=0.48, Neg years (linear/tail)=0/1 of 7, Half ratio=0.86, Recency ratio=0.76
- Early IC=+0.1684, Recent IC=+0.1273, 1st-half IC=+0.1662, 2nd-half IC=+0.1421, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.054, Q3_mid=+0.148, Q4=+0.108, Q5_high_vol=+0.247

**`combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.0970, Sharpe=+0.7204)
- Admission: Train IC=+0.2749, Deflated=+0.2747, IR=0.84, Mono=0.77, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.294 | 2016: +0.126 | 2017: +0.215 | 2018: +0.216 | 2019: +0.132 | 2020: +0.169 | 2021: +0.103 | 2022: +0.082 | 2023: +0.070 | 2024: +0.094 | 2025: +0.117 | 2026: +0.105
- Yearly Tail ICs:   2015: +0.153 | 2016: +0.140 | 2017: +0.264 | 2018: +0.393 | 2019: +0.275 | 2020: +0.210 | 2021: +0.173 | 2022: +0.186 | 2023: -0.021 | 2024: +0.141 | 2025: +0.131 | 2026: +0.171
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.65
- Early IC=+0.2099, Recent IC=+0.1356, 1st-half IC=+0.2318, 2nd-half IC=+0.1553, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.070, Q3_mid=+0.132, Q4=+0.187, Q5_high_vol=+0.286

**`combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0969, Sharpe=+0.7204)
- Admission: Train IC=+0.2734, Deflated=+0.2732, IR=0.84, Mono=0.77, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.126 | 2017: +0.215 | 2018: +0.216 | 2019: +0.132 | 2020: +0.168 | 2021: +0.103 | 2022: +0.082 | 2023: +0.070 | 2024: +0.094 | 2025: +0.117 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.150 | 2016: +0.141 | 2017: +0.263 | 2018: +0.393 | 2019: +0.274 | 2020: +0.210 | 2021: +0.173 | 2022: +0.186 | 2023: -0.025 | 2024: +0.140 | 2025: +0.132 | 2026: +0.171
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.65
- Early IC=+0.2098, Recent IC=+0.1357, 1st-half IC=+0.2318, 2nd-half IC=+0.1552, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.069, Q3_mid=+0.132, Q4=+0.187, Q5_high_vol=+0.286

**`combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1087, Sharpe=+0.7147)
- Admission: Train IC=+0.2790, Deflated=+0.2789, IR=0.98, Mono=0.82, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.130 | 2017: +0.245 | 2018: +0.200 | 2019: +0.146 | 2020: +0.198 | 2021: +0.128 | 2022: +0.078 | 2023: +0.083 | 2024: +0.135 | 2025: +0.093 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.262 | 2017: +0.271 | 2018: +0.344 | 2019: +0.348 | 2020: +0.194 | 2021: +0.146 | 2022: +0.025 | 2023: -0.105 | 2024: +0.178 | 2025: -0.020 | 2026: +0.257
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.76
- Early IC=+0.2132, Recent IC=+0.1629, 1st-half IC=+0.2433, 2nd-half IC=+0.1741, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.211, Q2=+0.097, Q3_mid=+0.162, Q4=+0.203, Q5_high_vol=+0.297

**`combo_min__max_up_ret__high_low_sequence_momentum`** (Lock IC=+0.1017, Sharpe=+0.7104)
- Admission: Train IC=+0.2400, Deflated=+0.2388, IR=0.75, Mono=0.77, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.159 | 2016: +0.072 | 2017: +0.195 | 2018: +0.153 | 2019: +0.088 | 2020: +0.111 | 2021: +0.107 | 2022: +0.115 | 2023: +0.116 | 2024: +0.148 | 2025: +0.142 | 2026: -0.089
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.184 | 2017: +0.339 | 2018: +0.380 | 2019: +0.120 | 2020: +0.192 | 2021: +0.133 | 2022: +0.149 | 2023: +0.207 | 2024: +0.213 | 2025: +0.107 | 2026: -0.100
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.94
- Early IC=+0.1153, Recent IC=+0.1089, 1st-half IC=+0.1483, 2nd-half IC=+0.1172, Neg regimes=0/5
- Weak component: `high_low_sequence_momentum` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.035, Q3_mid=+0.156, Q4=+0.144, Q5_high_vol=+0.153

**`combo_mean__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0988, Sharpe=+0.7092)
- Admission: Train IC=+0.2692, Deflated=+0.2684, IR=0.81, Mono=0.80, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.073 | 2017: +0.226 | 2018: +0.165 | 2019: +0.117 | 2020: +0.152 | 2021: +0.122 | 2022: +0.080 | 2023: +0.100 | 2024: +0.151 | 2025: +0.113 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.411 | 2016: +0.198 | 2017: +0.321 | 2018: +0.218 | 2019: +0.351 | 2020: +0.163 | 2021: +0.315 | 2022: +0.202 | 2023: +0.200 | 2024: +0.323 | 2025: -0.028 | 2026: -0.026
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.84, Recency ratio=0.84
- Early IC=+0.1641, Recent IC=+0.1373, 1st-half IC=+0.1783, 2nd-half IC=+0.1497, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.047, Q3_mid=+0.162, Q4=+0.145, Q5_high_vol=+0.240

**`combo_min__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0854, Sharpe=+0.7078)
- Admission: Train IC=+0.2531, Deflated=+0.2529, IR=0.85, Mono=0.76, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.088 | 2017: +0.214 | 2018: +0.251 | 2019: +0.156 | 2020: +0.146 | 2021: +0.100 | 2022: +0.060 | 2023: +0.073 | 2024: +0.134 | 2025: +0.117 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.398 | 2016: +0.093 | 2017: +0.359 | 2018: +0.412 | 2019: +0.167 | 2020: +0.121 | 2021: +0.262 | 2022: +0.241 | 2023: +0.165 | 2024: +0.274 | 2025: +0.118 | 2026: -0.163
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.73
- Early IC=+0.1689, Recent IC=+0.1231, 1st-half IC=+0.1932, 2nd-half IC=+0.1635, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.082, Q3_mid=+0.152, Q4=+0.153, Q5_high_vol=+0.272

**`combo_mean__close_vs_open_range__first_bar_return`** (Lock IC=+0.0944, Sharpe=+0.7072)
- Admission: Train IC=+0.2053, Deflated=+0.2046, IR=0.69, Mono=0.76, p=0.0006, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.100 | 2017: +0.215 | 2018: +0.206 | 2019: +0.110 | 2020: +0.114 | 2021: +0.101 | 2022: +0.096 | 2023: +0.080 | 2024: +0.151 | 2025: +0.115 | 2026: -0.038
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.042 | 2017: +0.266 | 2018: +0.351 | 2019: +0.140 | 2020: +0.171 | 2021: +0.359 | 2022: +0.256 | 2023: +0.226 | 2024: +0.310 | 2025: +0.024 | 2026: -0.250
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.65
- Early IC=+0.1652, Recent IC=+0.1078, 1st-half IC=+0.1874, 2nd-half IC=+0.1368, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.010, Q3_mid=+0.148, Q4=+0.145, Q5_high_vol=+0.224

**`combo_mean__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0944, Sharpe=+0.7072)
- Admission: Train IC=+0.2051, Deflated=+0.2044, IR=0.70, Mono=0.76, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.100 | 2017: +0.215 | 2018: +0.205 | 2019: +0.110 | 2020: +0.114 | 2021: +0.101 | 2022: +0.096 | 2023: +0.080 | 2024: +0.151 | 2025: +0.114 | 2026: -0.036
- Yearly Tail ICs:   2015: +0.278 | 2016: +0.042 | 2017: +0.266 | 2018: +0.351 | 2019: +0.137 | 2020: +0.171 | 2021: +0.361 | 2022: +0.256 | 2023: +0.226 | 2024: +0.311 | 2025: +0.025 | 2026: -0.250
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.65
- Early IC=+0.1652, Recent IC=+0.1077, 1st-half IC=+0.1874, 2nd-half IC=+0.1368, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.214, Q2=+0.010, Q3_mid=+0.148, Q4=+0.146, Q5_high_vol=+0.224

**`combo_rank_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0830, Sharpe=+0.7016)
- Admission: Train IC=+0.2868, Deflated=+0.2865, IR=0.57, Mono=0.67, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.287 | 2016: +0.067 | 2017: +0.194 | 2018: +0.149 | 2019: +0.171 | 2020: +0.117 | 2021: +0.089 | 2022: +0.034 | 2023: +0.064 | 2024: +0.111 | 2025: +0.131 | 2026: +0.079
- Yearly Tail ICs:   2015: +0.249 | 2016: +0.097 | 2017: +0.214 | 2018: +0.389 | 2019: +0.325 | 2020: +0.223 | 2021: +0.118 | 2022: +0.125 | 2023: +0.121 | 2024: +0.318 | 2025: +0.150 | 2026: +0.051
- IC CV=0.45, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.59
- Early IC=+0.1773, Recent IC=+0.1039, 1st-half IC=+0.1881, 2nd-half IC=+0.1357, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.002, Q3_mid=+0.091, Q4=+0.163, Q5_high_vol=+0.244

**`combo_sig_product__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0959, Sharpe=+0.7015)
- Admission: Train IC=+0.2488, Deflated=+0.2487, IR=0.71, Mono=0.75, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.208 | 2016: +0.049 | 2017: +0.224 | 2018: +0.193 | 2019: +0.086 | 2020: +0.156 | 2021: +0.095 | 2022: +0.119 | 2023: +0.108 | 2024: +0.110 | 2025: +0.085 | 2026: -0.004
- Yearly Tail ICs:   2015: +0.388 | 2016: +0.080 | 2017: +0.253 | 2018: +0.247 | 2019: +0.167 | 2020: +0.274 | 2021: +0.180 | 2022: +0.244 | 2023: +0.334 | 2024: +0.276 | 2025: +0.032 | 2026: -0.115
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=0.99, Recency ratio=0.98
- Early IC=+0.1287, Recent IC=+0.1258, 1st-half IC=+0.1488, 2nd-half IC=+0.1469, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.048, Q3_mid=+0.177, Q4=+0.114, Q5_high_vol=+0.212

**`net_volume_flow`** (Lock IC=+0.0930, Sharpe=+0.7015)
- Admission: Train IC=+0.2354, Deflated=+0.2345, IR=0.68, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.151 | 2016: +0.063 | 2017: +0.165 | 2018: +0.154 | 2019: +0.088 | 2020: +0.107 | 2021: +0.085 | 2022: +0.104 | 2023: +0.088 | 2024: +0.132 | 2025: +0.131 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.332 | 2016: +0.088 | 2017: +0.166 | 2018: +0.242 | 2019: +0.165 | 2020: +0.274 | 2021: +0.194 | 2022: +0.244 | 2023: +0.334 | 2024: +0.276 | 2025: +0.032 | 2026: -0.115
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.82, Recency ratio=0.90
- Early IC=+0.1072, Recent IC=+0.0964, 1st-half IC=+0.1342, 2nd-half IC=+0.1097, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.171, Q2=-0.021, Q3_mid=+0.165, Q4=+0.123, Q5_high_vol=+0.161

**`combo_mean__net_volume_flow__first_bar_sentiment`** (Lock IC=+0.0933, Sharpe=+0.6969)
- Admission: Train IC=+0.2439, Deflated=+0.2433, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.218 | 2016: +0.098 | 2017: +0.153 | 2018: +0.192 | 2019: +0.110 | 2020: +0.112 | 2021: +0.089 | 2022: +0.111 | 2023: +0.084 | 2024: +0.123 | 2025: +0.124 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.473 | 2016: +0.113 | 2017: +0.133 | 2018: +0.290 | 2019: +0.176 | 2020: +0.264 | 2021: +0.162 | 2022: +0.246 | 2023: +0.355 | 2024: +0.234 | 2025: +0.039 | 2026: -0.112
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.64
- Early IC=+0.1577, Recent IC=+0.1001, 1st-half IC=+0.1609, 2nd-half IC=+0.1271, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.165, Q2=-0.002, Q3_mid=+0.176, Q4=+0.138, Q5_high_vol=+0.209

**`combo_rank_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0863, Sharpe=+0.6922)
- Admission: Train IC=+0.2386, Deflated=+0.2377, IR=0.71, Mono=0.74, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.070 | 2017: +0.271 | 2018: +0.191 | 2019: +0.147 | 2020: +0.174 | 2021: +0.099 | 2022: +0.054 | 2023: +0.065 | 2024: +0.158 | 2025: +0.105 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.476 | 2016: +0.084 | 2017: +0.234 | 2018: +0.163 | 2019: +0.358 | 2020: +0.068 | 2021: +0.297 | 2022: +0.084 | 2023: +0.183 | 2024: +0.402 | 2025: +0.178 | 2026: -0.048
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.86, Recency ratio=0.78
- Early IC=+0.1746, Recent IC=+0.1369, 1st-half IC=+0.1880, 2nd-half IC=+0.1607, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.228, Q2=+0.020, Q3_mid=+0.166, Q4=+0.131, Q5_high_vol=+0.287

**`combo_sig_product__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.1013, Sharpe=+0.6867)
- Admission: Train IC=+0.2569, Deflated=+0.2566, IR=0.64, Mono=0.75, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.145 | 2017: +0.119 | 2018: +0.143 | 2019: +0.067 | 2020: +0.118 | 2021: +0.071 | 2022: +0.088 | 2023: +0.123 | 2024: +0.127 | 2025: +0.132 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.383 | 2016: +0.210 | 2017: +0.317 | 2018: +0.179 | 2019: +0.052 | 2020: +0.222 | 2021: +0.242 | 2022: +0.179 | 2023: +0.012 | 2024: +0.323 | 2025: +0.087 | 2026: -0.171
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.50
- Early IC=+0.1903, Recent IC=+0.0943, 1st-half IC=+0.1743, 2nd-half IC=+0.1204, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.037, Q3_mid=+0.117, Q4=+0.170, Q5_high_vol=+0.234

**`combo_diff__net_volume_flow__volume_weighted_momentum_acceleration`** (Lock IC=+0.0934, Sharpe=+0.6839)
- Admission: Train IC=+0.2901, Deflated=+0.2895, IR=0.97, Mono=0.83, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.056 | 2017: +0.164 | 2018: +0.246 | 2019: +0.172 | 2020: +0.159 | 2021: +0.149 | 2022: +0.065 | 2023: +0.099 | 2024: +0.145 | 2025: +0.097 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.444 | 2016: +0.054 | 2017: +0.194 | 2018: +0.413 | 2019: +0.231 | 2020: +0.221 | 2021: +0.335 | 2022: +0.237 | 2023: +0.318 | 2024: +0.299 | 2025: +0.095 | 2026: -0.350
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=1.13, Recency ratio=1.06
- Early IC=+0.1452, Recent IC=+0.1538, 1st-half IC=+0.1649, 2nd-half IC=+0.1868, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.174, Q2=+0.075, Q3_mid=+0.195, Q4=+0.133, Q5_high_vol=+0.278

**`combo_mean__net_volume_flow__star50_limit_proximity_early`** (Lock IC=+0.0993, Sharpe=+0.6823)
- Admission: Train IC=+0.2596, Deflated=+0.2589, IR=0.77, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.088 | 2017: +0.186 | 2018: +0.155 | 2019: +0.124 | 2020: +0.147 | 2021: +0.089 | 2022: +0.091 | 2023: +0.058 | 2024: +0.111 | 2025: +0.107 | 2026: +0.090
- Yearly Tail ICs:   2015: +0.269 | 2016: +0.114 | 2017: +0.221 | 2018: +0.340 | 2019: +0.353 | 2020: +0.164 | 2021: +0.148 | 2022: +0.330 | 2023: +0.168 | 2024: +0.240 | 2025: +0.039 | 2026: +0.174
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.72
- Early IC=+0.1630, Recent IC=+0.1181, 1st-half IC=+0.1822, 2nd-half IC=+0.1317, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.012, Q3_mid=+0.138, Q4=+0.159, Q5_high_vol=+0.215

**`opening_drive_thrust_ratio`** (Lock IC=+0.0956, Sharpe=+0.6759)
- Admission: Train IC=+0.2584, Deflated=+0.2578, IR=0.76, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.068 | 2017: +0.231 | 2018: +0.204 | 2019: +0.140 | 2020: +0.167 | 2021: +0.144 | 2022: +0.069 | 2023: +0.102 | 2024: +0.152 | 2025: +0.088 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.517 | 2016: +0.047 | 2017: +0.205 | 2018: +0.244 | 2019: +0.347 | 2020: +0.069 | 2021: +0.321 | 2022: +0.278 | 2023: +0.019 | 2024: +0.151 | 2025: +0.052 | 2026: -0.026
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.90, Recency ratio=0.91
- Early IC=+0.1704, Recent IC=+0.1555, 1st-half IC=+0.1905, 2nd-half IC=+0.1720, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.082, Q3_mid=+0.165, Q4=+0.145, Q5_high_vol=+0.286

**`combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.1056, Sharpe=+0.6748)
- Admission: Train IC=+0.2252, Deflated=+0.2249, IR=0.49, Mono=0.67, p=0.0002, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.236 | 2016: +0.119 | 2017: +0.121 | 2018: +0.159 | 2019: +0.097 | 2020: +0.097 | 2021: +0.025 | 2022: +0.154 | 2023: +0.090 | 2024: +0.103 | 2025: +0.093 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.057 | 2016: +0.377 | 2017: +0.216 | 2018: +0.137 | 2019: +0.181 | 2020: +0.126 | 2021: +0.107 | 2022: +0.164 | 2023: +0.128 | 2024: +0.236 | 2025: -0.002 | 2026: -0.189
- IC CV=0.48, Neg years (linear/tail)=0/0 of 7, Half ratio=0.46, Recency ratio=0.35
- Early IC=+0.1788, Recent IC=+0.0630, 1st-half IC=+0.1965, 2nd-half IC=+0.0896, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.009, Q3_mid=+0.152, Q4=+0.113, Q5_high_vol=+0.266

**`combo_max__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.1014, Sharpe=+0.6742)
- Admission: Train IC=+0.2721, Deflated=+0.2709, IR=0.82, Mono=0.79, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.297 | 2016: +0.084 | 2017: +0.247 | 2018: +0.154 | 2019: +0.106 | 2020: +0.168 | 2021: +0.113 | 2022: +0.116 | 2023: +0.080 | 2024: +0.149 | 2025: +0.116 | 2026: -0.027
- Yearly Tail ICs:   2015: +0.543 | 2016: +0.168 | 2017: +0.280 | 2018: +0.201 | 2019: +0.261 | 2020: +0.072 | 2021: +0.310 | 2022: +0.226 | 2023: +0.106 | 2024: +0.236 | 2025: +0.069 | 2026: -0.077
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.74
- Early IC=+0.1904, Recent IC=+0.1405, 1st-half IC=+0.1985, 2nd-half IC=+0.1446, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.053, Q3_mid=+0.145, Q4=+0.173, Q5_high_vol=+0.266

**`combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.1029, Sharpe=+0.6670)
- Admission: Train IC=+0.3278, Deflated=+0.3273, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.72
- Yearly Linear ICs: 2015: +0.286 | 2016: +0.032 | 2017: +0.144 | 2018: +0.195 | 2019: +0.199 | 2020: +0.201 | 2021: +0.148 | 2022: +0.067 | 2023: +0.065 | 2024: +0.123 | 2025: +0.091 | 2026: +0.173
- Yearly Tail ICs:   2015: +0.229 | 2016: +0.051 | 2017: +0.165 | 2018: +0.358 | 2019: +0.482 | 2020: +0.214 | 2021: +0.284 | 2022: -0.019 | 2023: +0.129 | 2024: +0.172 | 2025: +0.122 | 2026: +0.350
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=1.09, Recency ratio=1.10
- Early IC=+0.1593, Recent IC=+0.1747, 1st-half IC=+0.1770, 2nd-half IC=+0.1934, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.127, Q3_mid=+0.142, Q4=+0.125, Q5_high_vol=+0.303

**`combo_rank_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0934, Sharpe=+0.6633)
- Admission: Train IC=+0.2715, Deflated=+0.2704, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.084 | 2017: +0.219 | 2018: +0.152 | 2019: +0.083 | 2020: +0.137 | 2021: +0.098 | 2022: +0.107 | 2023: +0.073 | 2024: +0.151 | 2025: +0.120 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.482 | 2016: +0.207 | 2017: +0.388 | 2018: +0.181 | 2019: +0.287 | 2020: +0.206 | 2021: +0.232 | 2022: +0.306 | 2023: +0.214 | 2024: +0.288 | 2025: +0.067 | 2026: -0.136
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.70
- Early IC=+0.1684, Recent IC=+0.1184, 1st-half IC=+0.1927, 2nd-half IC=+0.1237, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.039, Q3_mid=+0.158, Q4=+0.164, Q5_high_vol=+0.236

**`combo_rank_max__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.0992, Sharpe=+0.6630)
- Admission: Train IC=+0.2736, Deflated=+0.2726, IR=0.97, Mono=0.83, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.256 | 2016: +0.083 | 2017: +0.236 | 2018: +0.161 | 2019: +0.114 | 2020: +0.144 | 2021: +0.107 | 2022: +0.095 | 2023: +0.078 | 2024: +0.155 | 2025: +0.114 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.506 | 2016: +0.189 | 2017: +0.333 | 2018: +0.235 | 2019: +0.345 | 2020: +0.159 | 2021: +0.294 | 2022: +0.299 | 2023: +0.289 | 2024: +0.263 | 2025: +0.102 | 2026: -0.253
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.75
- Early IC=+0.1698, Recent IC=+0.1267, 1st-half IC=+0.1920, 2nd-half IC=+0.1382, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.210, Q2=+0.038, Q3_mid=+0.165, Q4=+0.155, Q5_high_vol=+0.252

**`combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.1005, Sharpe=+0.6564)
- Admission: Train IC=+0.2798, Deflated=+0.2791, IR=1.08, Mono=0.87, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.082 | 2017: +0.228 | 2018: +0.211 | 2019: +0.124 | 2020: +0.153 | 2021: +0.132 | 2022: +0.093 | 2023: +0.110 | 2024: +0.160 | 2025: +0.108 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.341 | 2016: +0.238 | 2017: +0.277 | 2018: +0.328 | 2019: +0.226 | 2020: +0.196 | 2021: +0.318 | 2022: +0.266 | 2023: +0.336 | 2024: +0.230 | 2025: -0.075 | 2026: -0.313
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.87
- Early IC=+0.1638, Recent IC=+0.1425, 1st-half IC=+0.1996, 2nd-half IC=+0.1597, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.045, Q3_mid=+0.193, Q4=+0.162, Q5_high_vol=+0.263

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow`** (Lock IC=+0.1074, Sharpe=+0.6556)
- Admission: Train IC=+0.2979, Deflated=+0.2976, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.128 | 2017: +0.196 | 2018: +0.224 | 2019: +0.118 | 2020: +0.164 | 2021: +0.111 | 2022: +0.118 | 2023: +0.080 | 2024: +0.107 | 2025: +0.127 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.370 | 2016: +0.259 | 2017: +0.224 | 2018: +0.419 | 2019: +0.228 | 2020: +0.218 | 2021: +0.191 | 2022: +0.259 | 2023: +0.157 | 2024: +0.211 | 2025: -0.081 | 2026: +0.004
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.73
- Early IC=+0.1889, Recent IC=+0.1376, 1st-half IC=+0.2213, 2nd-half IC=+0.1536, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.039, Q3_mid=+0.190, Q4=+0.192, Q5_high_vol=+0.274

**`combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1073, Sharpe=+0.6547)
- Admission: Train IC=+0.2468, Deflated=+0.2465, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.117 | 2017: +0.215 | 2018: +0.167 | 2019: +0.108 | 2020: +0.157 | 2021: +0.078 | 2022: +0.099 | 2023: +0.074 | 2024: +0.107 | 2025: +0.132 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.163 | 2016: +0.221 | 2017: +0.259 | 2018: +0.286 | 2019: +0.367 | 2020: +0.134 | 2021: +0.205 | 2022: +0.268 | 2023: +0.148 | 2024: +0.254 | 2025: +0.072 | 2026: +0.152
- IC CV=0.35, Neg years (linear/tail)=0/0 of 7, Half ratio=0.59, Recency ratio=0.66
- Early IC=+0.1783, Recent IC=+0.1175, 1st-half IC=+0.2107, 2nd-half IC=+0.1254, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.030, Q3_mid=+0.137, Q4=+0.187, Q5_high_vol=+0.217

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1081, Sharpe=+0.6470)
- Admission: Train IC=+0.3040, Deflated=+0.3040, IR=1.03, Mono=0.84, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.292 | 2016: +0.137 | 2017: +0.242 | 2018: +0.243 | 2019: +0.135 | 2020: +0.200 | 2021: +0.136 | 2022: +0.090 | 2023: +0.085 | 2024: +0.131 | 2025: +0.108 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.291 | 2016: +0.230 | 2017: +0.311 | 2018: +0.389 | 2019: +0.296 | 2020: +0.180 | 2021: +0.236 | 2022: +0.146 | 2023: -0.031 | 2024: +0.154 | 2025: -0.110 | 2026: +0.060
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.78
- Early IC=+0.2147, Recent IC=+0.1677, 1st-half IC=+0.2502, 2nd-half IC=+0.1810, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.094, Q3_mid=+0.191, Q4=+0.212, Q5_high_vol=+0.315

**`combo_mean__first_bar_sentiment__max_down_ret`** (Lock IC=+0.0844, Sharpe=+0.6370)
- Admission: Train IC=+0.1916, Deflated=+0.1909, IR=0.50, Mono=0.66, p=0.0010, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.092 | 2017: +0.194 | 2018: +0.177 | 2019: +0.140 | 2020: +0.115 | 2021: +0.094 | 2022: +0.077 | 2023: +0.032 | 2024: +0.117 | 2025: +0.130 | 2026: +0.025
- Yearly Tail ICs:   2015: +0.371 | 2016: -0.040 | 2017: +0.127 | 2018: +0.185 | 2019: +0.328 | 2020: +0.036 | 2021: +0.286 | 2022: +0.148 | 2023: +0.158 | 2024: +0.290 | 2025: +0.176 | 2026: +0.035
- IC CV=0.42, Neg years (linear/tail)=0/1 of 7, Half ratio=0.80, Recency ratio=0.54
- Early IC=+0.1922, Recent IC=+0.1042, 1st-half IC=+0.1718, 2nd-half IC=+0.1380, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.007, Q3_mid=+0.160, Q4=+0.121, Q5_high_vol=+0.254

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.0915, Sharpe=+0.6332)
- Admission: Train IC=+0.2748, Deflated=+0.2744, IR=0.72, Mono=0.75, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.291 | 2016: +0.093 | 2017: +0.217 | 2018: +0.187 | 2019: +0.128 | 2020: +0.165 | 2021: +0.086 | 2022: +0.062 | 2023: +0.068 | 2024: +0.087 | 2025: +0.131 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.326 | 2016: +0.074 | 2017: +0.262 | 2018: +0.368 | 2019: +0.296 | 2020: +0.197 | 2021: +0.171 | 2022: +0.221 | 2023: -0.019 | 2024: +0.166 | 2025: +0.174 | 2026: +0.110
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.65
- Early IC=+0.1919, Recent IC=+0.1253, 1st-half IC=+0.2125, 2nd-half IC=+0.1460, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.060, Q3_mid=+0.116, Q4=+0.160, Q5_high_vol=+0.262

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0993, Sharpe=+0.6328)
- Admission: Train IC=+0.3166, Deflated=+0.3161, IR=1.12, Mono=0.85, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.079 | 2017: +0.224 | 2018: +0.214 | 2019: +0.114 | 2020: +0.132 | 2021: +0.131 | 2022: +0.094 | 2023: +0.106 | 2024: +0.144 | 2025: +0.119 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.457 | 2016: +0.314 | 2017: +0.270 | 2018: +0.393 | 2019: +0.189 | 2020: +0.202 | 2021: +0.287 | 2022: +0.254 | 2023: +0.258 | 2024: +0.245 | 2025: -0.036 | 2026: -0.235
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.76
- Early IC=+0.1726, Recent IC=+0.1314, 1st-half IC=+0.2016, 2nd-half IC=+0.1481, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.209, Q2=+0.050, Q3_mid=+0.190, Q4=+0.161, Q5_high_vol=+0.267

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1115, Sharpe=+0.6293)
- Admission: Train IC=+0.3136, Deflated=+0.3128, IR=0.91, Mono=0.84, p=0.0000, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.290 | 2016: +0.137 | 2017: +0.228 | 2018: +0.223 | 2019: +0.109 | 2020: +0.187 | 2021: +0.148 | 2022: +0.098 | 2023: +0.110 | 2024: +0.165 | 2025: +0.103 | 2026: +0.017
- Yearly Tail ICs:   2015: +0.355 | 2016: +0.316 | 2017: +0.251 | 2018: +0.358 | 2019: +0.256 | 2020: +0.282 | 2021: +0.310 | 2022: -0.052 | 2023: +0.073 | 2024: +0.246 | 2025: -0.028 | 2026: -0.145
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.79
- Early IC=+0.2135, Recent IC=+0.1679, 1st-half IC=+0.2374, 2nd-half IC=+0.1686, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.199, Q2=+0.104, Q3_mid=+0.188, Q4=+0.175, Q5_high_vol=+0.315

**`combo_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0754, Sharpe=+0.6281)
- Admission: Train IC=+0.2335, Deflated=+0.2326, IR=0.71, Mono=0.74, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.220 | 2016: +0.127 | 2017: +0.141 | 2018: +0.227 | 2019: +0.145 | 2020: +0.090 | 2021: +0.098 | 2022: +0.067 | 2023: +0.070 | 2024: +0.123 | 2025: +0.105 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.357 | 2016: +0.027 | 2017: +0.261 | 2018: +0.482 | 2019: +0.314 | 2020: +0.115 | 2021: +0.207 | 2022: +0.265 | 2023: +0.153 | 2024: +0.216 | 2025: +0.015 | 2026: -0.144
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.54
- Early IC=+0.1736, Recent IC=+0.0942, 1st-half IC=+0.1788, 2nd-half IC=+0.1407, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.043, Q3_mid=+0.139, Q4=+0.137, Q5_high_vol=+0.243

**`combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector`** (Lock IC=+0.0984, Sharpe=+0.6279)
- Admission: Train IC=+0.2776, Deflated=+0.2768, IR=0.86, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.068 | 2017: +0.231 | 2018: +0.172 | 2019: +0.121 | 2020: +0.150 | 2021: +0.117 | 2022: +0.087 | 2023: +0.100 | 2024: +0.145 | 2025: +0.122 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.508 | 2016: +0.167 | 2017: +0.229 | 2018: +0.255 | 2019: +0.354 | 2020: +0.225 | 2021: +0.273 | 2022: +0.309 | 2023: +0.282 | 2024: +0.244 | 2025: +0.092 | 2026: -0.070
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.84, Recency ratio=0.89
- Early IC=+0.1498, Recent IC=+0.1336, 1st-half IC=+0.1756, 2nd-half IC=+0.1468, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.039, Q3_mid=+0.162, Q4=+0.148, Q5_high_vol=+0.228

**`combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1142, Sharpe=+0.6230)
- Admission: Train IC=+0.3226, Deflated=+0.3228, IR=0.98, Mono=0.83, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.277 | 2016: +0.138 | 2017: +0.224 | 2018: +0.223 | 2019: +0.105 | 2020: +0.171 | 2021: +0.116 | 2022: +0.104 | 2023: +0.086 | 2024: +0.097 | 2025: +0.126 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.246 | 2016: +0.342 | 2017: +0.172 | 2018: +0.455 | 2019: +0.218 | 2020: +0.266 | 2021: +0.251 | 2022: -0.006 | 2023: -0.026 | 2024: +0.089 | 2025: +0.055 | 2026: +0.165
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.62, Recency ratio=0.69
- Early IC=+0.2074, Recent IC=+0.1435, 1st-half IC=+0.2389, 2nd-half IC=+0.1477, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.215, Q2=+0.086, Q3_mid=+0.176, Q4=+0.205, Q5_high_vol=+0.294

**`combo_z_sum__trend_bar_close_consistency__max_down_ret`** (Lock IC=+0.0808, Sharpe=+0.6211)
- Admission: Train IC=+0.1957, Deflated=+0.1950, IR=0.39, Mono=0.66, p=0.0008, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.188 | 2016: +0.042 | 2017: +0.176 | 2018: +0.110 | 2019: +0.047 | 2020: +0.104 | 2021: +0.051 | 2022: +0.074 | 2023: +0.077 | 2024: +0.117 | 2025: +0.124 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.390 | 2016: +0.050 | 2017: +0.228 | 2018: +0.094 | 2019: +0.061 | 2020: +0.135 | 2021: +0.264 | 2022: +0.253 | 2023: +0.115 | 2024: +0.392 | 2025: +0.097 | 2026: -0.071
- IC CV=0.55, Neg years (linear/tail)=0/0 of 7, Half ratio=0.70, Recency ratio=0.67
- Early IC=+0.1151, Recent IC=+0.0775, 1st-half IC=+0.1230, 2nd-half IC=+0.0855, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.038, Q3_mid=+0.116, Q4=+0.101, Q5_high_vol=+0.157

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.0803, Sharpe=+0.6137)
- Admission: Train IC=+0.2950, Deflated=+0.2950, IR=0.60, Mono=0.70, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.315 | 2016: +0.086 | 2017: +0.219 | 2018: +0.206 | 2019: +0.176 | 2020: +0.131 | 2021: +0.087 | 2022: +0.047 | 2023: +0.078 | 2024: +0.089 | 2025: +0.119 | 2026: +0.081
- Yearly Tail ICs:   2015: +0.257 | 2016: +0.111 | 2017: +0.189 | 2018: +0.460 | 2019: +0.319 | 2020: +0.264 | 2021: +0.037 | 2022: +0.134 | 2023: +0.117 | 2024: +0.267 | 2025: +0.092 | 2026: +0.095
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.54
- Early IC=+0.2004, Recent IC=+0.1092, 1st-half IC=+0.2245, 2nd-half IC=+0.1496, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.037, Q3_mid=+0.112, Q4=+0.215, Q5_high_vol=+0.262

**`combo_rel_diff__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0816, Sharpe=+0.6117)
- Admission: Train IC=+0.1832, Deflated=+0.1824, IR=0.68, Mono=0.77, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.281 | 2016: +0.019 | 2017: +0.201 | 2018: +0.195 | 2019: +0.177 | 2020: +0.168 | 2021: +0.127 | 2022: +0.055 | 2023: +0.097 | 2024: +0.109 | 2025: +0.041 | 2026: +0.097
- Yearly Tail ICs:   2015: +0.379 | 2016: -0.012 | 2017: +0.375 | 2018: +0.144 | 2019: +0.253 | 2020: +0.039 | 2021: +0.209 | 2022: +0.064 | 2023: +0.151 | 2024: +0.261 | 2025: +0.067 | 2026: +0.390
- IC CV=0.44, Neg years (linear/tail)=0/1 of 7, Half ratio=1.16, Recency ratio=0.98
- Early IC=+0.1503, Recent IC=+0.1472, 1st-half IC=+0.1567, 2nd-half IC=+0.1812, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.080, Q3_mid=+0.155, Q4=+0.122, Q5_high_vol=+0.304

**`combo_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0977, Sharpe=+0.6114)
- Admission: Train IC=+0.2983, Deflated=+0.2980, IR=1.04, Mono=0.85, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.100 | 2017: +0.208 | 2018: +0.220 | 2019: +0.145 | 2020: +0.154 | 2021: +0.126 | 2022: +0.060 | 2023: +0.119 | 2024: +0.155 | 2025: +0.095 | 2026: -0.015
- Yearly Tail ICs:   2015: +0.503 | 2016: +0.307 | 2017: +0.348 | 2018: +0.393 | 2019: +0.186 | 2020: +0.195 | 2021: +0.283 | 2022: +0.134 | 2023: +0.224 | 2024: +0.209 | 2025: -0.133 | 2026: -0.139
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.86, Recency ratio=0.77
- Early IC=+0.1810, Recent IC=+0.1397, 1st-half IC=+0.1964, 2nd-half IC=+0.1683, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.181, Q2=+0.089, Q3_mid=+0.196, Q4=+0.145, Q5_high_vol=+0.283

**`combo_rank_min__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0778, Sharpe=+0.6083)
- Admission: Train IC=+0.2408, Deflated=+0.2402, IR=0.60, Mono=0.69, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.163 | 2016: +0.045 | 2017: +0.156 | 2018: +0.171 | 2019: +0.101 | 2020: +0.037 | 2021: +0.062 | 2022: +0.066 | 2023: +0.062 | 2024: +0.112 | 2025: +0.116 | 2026: -0.002
- Yearly Tail ICs:   2015: +0.427 | 2016: +0.006 | 2017: +0.316 | 2018: +0.395 | 2019: +0.113 | 2020: +0.057 | 2021: +0.252 | 2022: +0.293 | 2023: -0.003 | 2024: +0.322 | 2025: +0.094 | 2026: +0.158
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.46
- Early IC=+0.1077, Recent IC=+0.0491, 1st-half IC=+0.1331, 2nd-half IC=+0.0899, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.186, Q2=-0.046, Q3_mid=+0.114, Q4=+0.123, Q5_high_vol=+0.152

**`combo_sig_product__max_up_ret__early_body_momentum`** (Lock IC=+0.1053, Sharpe=+0.6079)
- Admission: Train IC=+0.2469, Deflated=+0.2464, IR=0.57, Mono=0.71, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.156 | 2017: +0.146 | 2018: +0.152 | 2019: +0.073 | 2020: +0.155 | 2021: +0.099 | 2022: +0.115 | 2023: +0.136 | 2024: +0.132 | 2025: +0.121 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.361 | 2016: +0.152 | 2017: +0.142 | 2018: +0.189 | 2019: +0.144 | 2020: +0.312 | 2021: +0.271 | 2022: +0.117 | 2023: +0.149 | 2024: +0.323 | 2025: +0.007 | 2026: -0.130
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.77, Recency ratio=0.65
- Early IC=+0.1944, Recent IC=+0.1268, 1st-half IC=+0.1796, 2nd-half IC=+0.1384, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.029, Q3_mid=+0.147, Q4=+0.182, Q5_high_vol=+0.249

**`combo_clamp_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0840, Sharpe=+0.6062)
- Admission: Train IC=+0.2897, Deflated=+0.2894, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.096 | 2017: +0.193 | 2018: +0.219 | 2019: +0.152 | 2020: +0.158 | 2021: +0.130 | 2022: +0.064 | 2023: +0.102 | 2024: +0.124 | 2025: +0.015 | 2026: +0.097
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.147 | 2017: +0.393 | 2018: +0.358 | 2019: +0.392 | 2020: +0.105 | 2021: +0.122 | 2022: +0.205 | 2023: +0.184 | 2024: +0.048 | 2025: +0.054 | 2026: +0.181
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.72
- Early IC=+0.2011, Recent IC=+0.1442, 1st-half IC=+0.2051, 2nd-half IC=+0.1751, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.093, Q3_mid=+0.191, Q4=+0.140, Q5_high_vol=+0.339

**`combo_rank_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0930, Sharpe=+0.6040)
- Admission: Train IC=+0.2441, Deflated=+0.2432, IR=0.93, Mono=0.80, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.111 | 2017: +0.152 | 2018: +0.220 | 2019: +0.070 | 2020: +0.137 | 2021: +0.059 | 2022: +0.127 | 2023: +0.094 | 2024: +0.130 | 2025: +0.095 | 2026: -0.050
- Yearly Tail ICs:   2015: +0.282 | 2016: +0.238 | 2017: +0.217 | 2018: +0.277 | 2019: +0.080 | 2020: +0.366 | 2021: +0.175 | 2022: +0.146 | 2023: +0.168 | 2024: +0.253 | 2025: -0.106 | 2026: -0.333
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.58
- Early IC=+0.1683, Recent IC=+0.0971, 1st-half IC=+0.1854, 2nd-half IC=+0.1206, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.010, Q3_mid=+0.173, Q4=+0.167, Q5_high_vol=+0.265

**`combo_rank_max__trend_bar_close_consistency__close_vs_open_range`** (Lock IC=+0.0779, Sharpe=+0.6003)
- Admission: Train IC=+0.1810, Deflated=+0.1802, IR=0.43, Mono=0.70, p=0.0014, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.148 | 2016: +0.043 | 2017: +0.174 | 2018: +0.090 | 2019: +0.027 | 2020: +0.094 | 2021: +0.061 | 2022: +0.077 | 2023: +0.089 | 2024: +0.100 | 2025: +0.146 | 2026: -0.109
- Yearly Tail ICs:   2015: +0.305 | 2016: +0.080 | 2017: +0.231 | 2018: +0.077 | 2019: +0.024 | 2020: +0.197 | 2021: +0.236 | 2022: +0.072 | 2023: +0.032 | 2024: +0.266 | 2025: +0.169 | 2026: -0.137
- IC CV=0.55, Neg years (linear/tail)=0/0 of 7, Half ratio=0.58, Recency ratio=0.79
- Early IC=+0.0978, Recent IC=+0.0768, 1st-half IC=+0.1247, 2nd-half IC=+0.0726, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.167, Q2=-0.042, Q3_mid=+0.134, Q4=+0.120, Q5_high_vol=+0.108

**`combo_rank_min__trend_bar_close_consistency__close_vs_open_range`** (Lock IC=+0.0843, Sharpe=+0.5989)
- Admission: Train IC=+0.2562, Deflated=+0.2552, IR=0.62, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.123 | 2016: +0.049 | 2017: +0.176 | 2018: +0.108 | 2019: +0.031 | 2020: +0.091 | 2021: +0.035 | 2022: +0.099 | 2023: +0.081 | 2024: +0.117 | 2025: +0.129 | 2026: -0.079
- Yearly Tail ICs:   2015: +0.318 | 2016: +0.196 | 2017: +0.455 | 2018: +0.309 | 2019: +0.016 | 2020: +0.209 | 2021: +0.182 | 2022: +0.230 | 2023: -0.021 | 2024: +0.277 | 2025: -0.027 | 2026: -0.155
- IC CV=0.56, Neg years (linear/tail)=0/1 of 7, Half ratio=0.59, Recency ratio=0.74
- Early IC=+0.0868, Recent IC=+0.0644, 1st-half IC=+0.1164, 2nd-half IC=+0.0686, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.154, Q2=-0.014, Q3_mid=+0.108, Q4=+0.110, Q5_high_vol=+0.107

**`combo_mean__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0933, Sharpe=+0.5981)
- Admission: Train IC=+0.2212, Deflated=+0.2205, IR=0.57, Mono=0.71, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.108 | 2017: +0.179 | 2018: +0.172 | 2019: +0.097 | 2020: +0.109 | 2021: +0.092 | 2022: +0.104 | 2023: +0.079 | 2024: +0.133 | 2025: +0.130 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.403 | 2016: +0.164 | 2017: +0.223 | 2018: +0.172 | 2019: +0.174 | 2020: +0.145 | 2021: +0.185 | 2022: +0.233 | 2023: +0.151 | 2024: +0.159 | 2025: +0.061 | 2026: +0.005
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.56
- Early IC=+0.1796, Recent IC=+0.1002, 1st-half IC=+0.1731, 2nd-half IC=+0.1177, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.168, Q2=-0.002, Q3_mid=+0.167, Q4=+0.142, Q5_high_vol=+0.209

**`combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1034, Sharpe=+0.5959)
- Admission: Train IC=+0.3331, Deflated=+0.3327, IR=1.00, Mono=0.82, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.276 | 2016: +0.097 | 2017: +0.241 | 2018: +0.197 | 2019: +0.159 | 2020: +0.167 | 2021: +0.148 | 2022: +0.031 | 2023: +0.100 | 2024: +0.164 | 2025: +0.093 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.392 | 2016: +0.169 | 2017: +0.359 | 2018: +0.471 | 2019: +0.332 | 2020: +0.197 | 2021: +0.201 | 2022: +0.175 | 2023: +0.072 | 2024: +0.305 | 2025: -0.061 | 2026: +0.197
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.85
- Early IC=+0.1863, Recent IC=+0.1579, 1st-half IC=+0.2156, 2nd-half IC=+0.1724, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.184, Q2=+0.108, Q3_mid=+0.149, Q4=+0.201, Q5_high_vol=+0.262

**`combo_rank_min__volatility_expansion_trend_vector__bar_ret_0`** (Lock IC=+0.0816, Sharpe=+0.5957)
- Admission: Train IC=+0.2444, Deflated=+0.2436, IR=0.65, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.075 | 2017: +0.191 | 2018: +0.189 | 2019: +0.131 | 2020: +0.076 | 2021: +0.068 | 2022: +0.049 | 2023: +0.067 | 2024: +0.109 | 2025: +0.131 | 2026: +0.014
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.070 | 2017: +0.308 | 2018: +0.297 | 2019: +0.272 | 2020: +0.175 | 2021: +0.291 | 2022: +0.185 | 2023: +0.210 | 2024: +0.119 | 2025: +0.147 | 2026: -0.075
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.53
- Early IC=+0.1356, Recent IC=+0.0723, 1st-half IC=+0.1579, 2nd-half IC=+0.1155, Neg regimes=1/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.202, Q2=-0.023, Q3_mid=+0.133, Q4=+0.145, Q5_high_vol=+0.188

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`** (Lock IC=+0.1100, Sharpe=+0.5923)
- Admission: Train IC=+0.3007, Deflated=+0.2999, IR=1.12, Mono=0.87, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.265 | 2016: +0.076 | 2017: +0.222 | 2018: +0.200 | 2019: +0.158 | 2020: +0.160 | 2021: +0.109 | 2022: +0.103 | 2023: +0.107 | 2024: +0.149 | 2025: +0.121 | 2026: +0.000
- Yearly Tail ICs:   2015: +0.447 | 2016: +0.193 | 2017: +0.298 | 2018: +0.326 | 2019: +0.238 | 2020: +0.285 | 2021: +0.249 | 2022: +0.317 | 2023: +0.204 | 2024: +0.302 | 2025: -0.008 | 2026: -0.323
- IC CV=0.35, Neg years (linear/tail)=0/0 of 7, Half ratio=0.77, Recency ratio=0.79
- Early IC=+0.1703, Recent IC=+0.1347, 1st-half IC=+0.2043, 2nd-half IC=+0.1569, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.227, Q2=+0.037, Q3_mid=+0.184, Q4=+0.166, Q5_high_vol=+0.268

**`combo_rank_min__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0713, Sharpe=+0.5914)
- Admission: Train IC=+0.2217, Deflated=+0.2206, IR=0.87, Mono=0.80, p=0.0002, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.191 | 2016: +0.148 | 2017: +0.146 | 2018: +0.232 | 2019: +0.124 | 2020: +0.121 | 2021: +0.095 | 2022: +0.065 | 2023: +0.058 | 2024: +0.102 | 2025: +0.125 | 2026: -0.026
- Yearly Tail ICs:   2015: -0.037 | 2016: +0.202 | 2017: +0.372 | 2018: +0.527 | 2019: +0.070 | 2020: +0.250 | 2021: +0.008 | 2022: +0.268 | 2023: -0.001 | 2024: +0.153 | 2025: +0.160 | 2026: -0.223
- IC CV=0.28, Neg years (linear/tail)=0/1 of 7, Half ratio=0.80, Recency ratio=0.64
- Early IC=+0.1692, Recent IC=+0.1080, 1st-half IC=+0.1784, 2nd-half IC=+0.1429, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.154, Q2=+0.047, Q3_mid=+0.161, Q4=+0.141, Q5_high_vol=+0.226

**`combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1008, Sharpe=+0.5899)
- Admission: Train IC=+0.3306, Deflated=+0.3300, IR=1.12, Mono=0.84, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.289 | 2016: +0.101 | 2017: +0.231 | 2018: +0.185 | 2019: +0.157 | 2020: +0.172 | 2021: +0.142 | 2022: +0.033 | 2023: +0.098 | 2024: +0.145 | 2025: +0.105 | 2026: +0.100
- Yearly Tail ICs:   2015: +0.409 | 2016: +0.251 | 2017: +0.357 | 2018: +0.456 | 2019: +0.298 | 2020: +0.315 | 2021: +0.302 | 2022: +0.078 | 2023: -0.003 | 2024: +0.236 | 2025: +0.074 | 2026: +0.233
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.78, Recency ratio=0.81
- Early IC=+0.1933, Recent IC=+0.1570, 1st-half IC=+0.2183, 2nd-half IC=+0.1708, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.105, Q3_mid=+0.135, Q4=+0.204, Q5_high_vol=+0.263

**`combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0799, Sharpe=+0.5898)
- Admission: Train IC=+0.2377, Deflated=+0.2372, IR=0.64, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.037 | 2017: +0.155 | 2018: +0.202 | 2019: +0.171 | 2020: +0.189 | 2021: +0.151 | 2022: +0.032 | 2023: +0.098 | 2024: +0.135 | 2025: +0.053 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.368 | 2016: +0.005 | 2017: +0.331 | 2018: +0.298 | 2019: +0.308 | 2020: -0.006 | 2021: +0.328 | 2022: +0.081 | 2023: +0.119 | 2024: +0.173 | 2025: +0.038 | 2026: +0.239
- IC CV=0.37, Neg years (linear/tail)=0/1 of 7, Half ratio=1.25, Recency ratio=1.20
- Early IC=+0.1411, Recent IC=+0.1699, 1st-half IC=+0.1516, 2nd-half IC=+0.1900, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.141, Q2=+0.114, Q3_mid=+0.151, Q4=+0.127, Q5_high_vol=+0.288

**`combo_mean__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0943, Sharpe=+0.5828)
- Admission: Train IC=+0.2370, Deflated=+0.2360, IR=0.65, Mono=0.73, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.169 | 2016: +0.063 | 2017: +0.180 | 2018: +0.138 | 2019: +0.072 | 2020: +0.113 | 2021: +0.077 | 2022: +0.102 | 2023: +0.088 | 2024: +0.133 | 2025: +0.139 | 2026: -0.072
- Yearly Tail ICs:   2015: +0.330 | 2016: +0.106 | 2017: +0.294 | 2018: +0.199 | 2019: +0.157 | 2020: +0.228 | 2021: +0.282 | 2022: +0.164 | 2023: +0.223 | 2024: +0.271 | 2025: +0.012 | 2026: -0.030
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.74, Recency ratio=0.82
- Early IC=+0.1160, Recent IC=+0.0951, 1st-half IC=+0.1378, 2nd-half IC=+0.1023, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.020, Q3_mid=+0.153, Q4=+0.122, Q5_high_vol=+0.158

**`combo_min__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0931, Sharpe=+0.5808)
- Admission: Train IC=+0.2427, Deflated=+0.2424, IR=0.75, Mono=0.79, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.062 | 2017: +0.202 | 2018: +0.176 | 2019: +0.114 | 2020: +0.139 | 2021: +0.113 | 2022: +0.046 | 2023: +0.109 | 2024: +0.143 | 2025: +0.115 | 2026: -0.030
- Yearly Tail ICs:   2015: +0.347 | 2016: +0.137 | 2017: +0.305 | 2018: +0.234 | 2019: +0.355 | 2020: +0.132 | 2021: +0.278 | 2022: +0.139 | 2023: +0.078 | 2024: +0.405 | 2025: -0.027 | 2026: +0.099
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.95, Recency ratio=0.97
- Early IC=+0.1294, Recent IC=+0.1261, 1st-half IC=+0.1513, 2nd-half IC=+0.1435, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.029, Q3_mid=+0.166, Q4=+0.116, Q5_high_vol=+0.209

**`combo_max__opening_drive_thrust_ratio__early_body_momentum`** (Lock IC=+0.0942, Sharpe=+0.5772)
- Admission: Train IC=+0.2602, Deflated=+0.2591, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.98
- Yearly Linear ICs: 2015: +0.260 | 2016: +0.087 | 2017: +0.214 | 2018: +0.161 | 2019: +0.087 | 2020: +0.153 | 2021: +0.107 | 2022: +0.110 | 2023: +0.075 | 2024: +0.148 | 2025: +0.116 | 2026: -0.047
- Yearly Tail ICs:   2015: +0.373 | 2016: +0.248 | 2017: +0.353 | 2018: +0.162 | 2019: +0.246 | 2020: +0.250 | 2021: +0.240 | 2022: +0.201 | 2023: +0.245 | 2024: +0.275 | 2025: -0.002 | 2026: -0.196
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.75
- Early IC=+0.1735, Recent IC=+0.1299, 1st-half IC=+0.1949, 2nd-half IC=+0.1341, Neg regimes=0/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.049, Q3_mid=+0.161, Q4=+0.166, Q5_high_vol=+0.247

**`combo_clamp_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0806, Sharpe=+0.5754)
- Admission: Train IC=+0.3030, Deflated=+0.3026, IR=0.77, Mono=0.76, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.314 | 2016: +0.107 | 2017: +0.186 | 2018: +0.215 | 2019: +0.120 | 2020: +0.142 | 2021: +0.150 | 2022: +0.060 | 2023: +0.092 | 2024: +0.117 | 2025: +0.009 | 2026: +0.108
- Yearly Tail ICs:   2015: +0.366 | 2016: +0.109 | 2017: +0.389 | 2018: +0.377 | 2019: +0.362 | 2020: +0.220 | 2021: +0.167 | 2022: +0.180 | 2023: +0.111 | 2024: +0.114 | 2025: -0.045 | 2026: +0.181
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.70
- Early IC=+0.2103, Recent IC=+0.1462, 1st-half IC=+0.2086, 2nd-half IC=+0.1666, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.095, Q3_mid=+0.196, Q4=+0.141, Q5_high_vol=+0.320

**`combo_diff__max_up_ret__early_late_momentum_divergence`** (Lock IC=+0.0789, Sharpe=+0.5754)
- Admission: Train IC=+0.2844, Deflated=+0.2839, IR=0.84, Mono=0.75, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.307 | 2016: +0.108 | 2017: +0.187 | 2018: +0.214 | 2019: +0.121 | 2020: +0.142 | 2021: +0.152 | 2022: +0.057 | 2023: +0.092 | 2024: +0.113 | 2025: +0.009 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.291 | 2016: +0.133 | 2017: +0.445 | 2018: +0.367 | 2019: +0.377 | 2020: +0.161 | 2021: +0.224 | 2022: +0.097 | 2023: +0.198 | 2024: +0.040 | 2025: -0.046 | 2026: +0.073
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.71
- Early IC=+0.2077, Recent IC=+0.1470, 1st-half IC=+0.2082, 2nd-half IC=+0.1672, Neg regimes=0/5
- Weak component: `early_late_momentum_divergence` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.096, Q3_mid=+0.195, Q4=+0.141, Q5_high_vol=+0.317

**`combo_max__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0859, Sharpe=+0.5722)
- Admission: Train IC=+0.2095, Deflated=+0.2087, IR=0.56, Mono=0.70, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.116 | 2017: +0.140 | 2018: +0.165 | 2019: +0.106 | 2020: +0.098 | 2021: +0.130 | 2022: +0.124 | 2023: +0.062 | 2024: +0.144 | 2025: +0.076 | 2026: -0.060
- Yearly Tail ICs:   2015: +0.406 | 2016: +0.165 | 2017: +0.178 | 2018: +0.165 | 2019: +0.150 | 2020: +0.134 | 2021: +0.167 | 2022: +0.255 | 2023: +0.111 | 2024: +0.336 | 2025: -0.037 | 2026: -0.091
- IC CV=0.35, Neg years (linear/tail)=0/0 of 7, Half ratio=0.82, Recency ratio=0.61
- Early IC=+0.1870, Recent IC=+0.1143, 1st-half IC=+0.1560, 2nd-half IC=+0.1276, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.154, Q2=-0.014, Q3_mid=+0.160, Q4=+0.149, Q5_high_vol=+0.229

**`combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1009, Sharpe=+0.5666)
- Admission: Train IC=+0.2191, Deflated=+0.2189, IR=0.48, Mono=0.66, p=0.0004, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.258 | 2016: +0.120 | 2017: +0.207 | 2018: +0.157 | 2019: +0.113 | 2020: +0.140 | 2021: +0.030 | 2022: +0.102 | 2023: +0.061 | 2024: +0.100 | 2025: +0.112 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.064 | 2016: +0.264 | 2017: +0.189 | 2018: +0.227 | 2019: +0.159 | 2020: +0.132 | 2021: +0.118 | 2022: +0.158 | 2023: +0.057 | 2024: +0.180 | 2025: +0.042 | 2026: +0.023
- IC CV=0.46, Neg years (linear/tail)=0/0 of 7, Half ratio=0.55, Recency ratio=0.45
- Early IC=+0.1893, Recent IC=+0.0848, 1st-half IC=+0.2060, 2nd-half IC=+0.1130, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.006, Q3_mid=+0.170, Q4=+0.118, Q5_high_vol=+0.268

**`combo_mean__max_up_ret__first_bar_return`** (Lock IC=+0.0876, Sharpe=+0.5580)
- Admission: Train IC=+0.2383, Deflated=+0.2376, IR=0.69, Mono=0.74, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.110 | 2017: +0.192 | 2018: +0.243 | 2019: +0.137 | 2020: +0.111 | 2021: +0.137 | 2022: +0.101 | 2023: +0.096 | 2024: +0.141 | 2025: +0.076 | 2026: -0.033
- Yearly Tail ICs:   2015: +0.244 | 2016: +0.129 | 2017: +0.266 | 2018: +0.480 | 2019: +0.117 | 2020: +0.231 | 2021: +0.284 | 2022: +0.102 | 2023: +0.139 | 2024: +0.142 | 2025: +0.046 | 2026: -0.250
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.78, Recency ratio=0.69
- Early IC=+0.1807, Recent IC=+0.1241, 1st-half IC=+0.2052, 2nd-half IC=+0.1590, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.203, Q2=+0.044, Q3_mid=+0.178, Q4=+0.175, Q5_high_vol=+0.279

**`combo_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0833, Sharpe=+0.5485)
- Admission: Train IC=+0.2593, Deflated=+0.2590, IR=0.93, Mono=0.78, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.299 | 2016: +0.097 | 2017: +0.194 | 2018: +0.219 | 2019: +0.151 | 2020: +0.156 | 2021: +0.134 | 2022: +0.063 | 2023: +0.101 | 2024: +0.123 | 2025: +0.012 | 2026: +0.093
- Yearly Tail ICs:   2015: +0.263 | 2016: +0.210 | 2017: +0.416 | 2018: +0.378 | 2019: +0.333 | 2020: +0.138 | 2021: +0.241 | 2022: +0.131 | 2023: +0.201 | 2024: +0.038 | 2025: -0.032 | 2026: +0.079
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.85, Recency ratio=0.73
- Early IC=+0.1980, Recent IC=+0.1453, 1st-half IC=+0.2053, 2nd-half IC=+0.1746, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.151, Q2=+0.096, Q3_mid=+0.185, Q4=+0.139, Q5_high_vol=+0.331

**`high_low_sequence_momentum`** (Lock IC=+0.0892, Sharpe=+0.5439)
- Admission: Train IC=+0.1985, Deflated=+0.1974, IR=0.41, Mono=0.66, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.048 | 2017: +0.197 | 2018: +0.123 | 2019: +0.066 | 2020: +0.100 | 2021: +0.046 | 2022: +0.097 | 2023: +0.072 | 2024: +0.131 | 2025: +0.130 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.316 | 2016: +0.149 | 2017: +0.216 | 2018: +0.152 | 2019: +0.199 | 2020: +0.179 | 2021: -0.014 | 2022: +0.163 | 2023: +0.098 | 2024: +0.241 | 2025: +0.015 | 2026: +0.061
- IC CV=0.50, Neg years (linear/tail)=0/1 of 7, Half ratio=0.69, Recency ratio=0.75
- Early IC=+0.0963, Recent IC=+0.0727, 1st-half IC=+0.1273, 2nd-half IC=+0.0883, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.187, Q2=-0.010, Q3_mid=+0.116, Q4=+0.120, Q5_high_vol=+0.125

**`combo_sig_product__close_vs_open_range__high_low_sequence_momentum`** (Lock IC=+0.0887, Sharpe=+0.5439)
- Admission: Train IC=+0.1985, Deflated=+0.1975, IR=0.41, Mono=0.66, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.049 | 2017: +0.197 | 2018: +0.121 | 2019: +0.068 | 2020: +0.099 | 2021: +0.042 | 2022: +0.097 | 2023: +0.071 | 2024: +0.132 | 2025: +0.129 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.316 | 2016: +0.149 | 2017: +0.216 | 2018: +0.152 | 2019: +0.199 | 2020: +0.179 | 2021: -0.014 | 2022: +0.163 | 2023: +0.098 | 2024: +0.241 | 2025: +0.015 | 2026: +0.061
- IC CV=0.50, Neg years (linear/tail)=0/1 of 7, Half ratio=0.69, Recency ratio=0.73
- Early IC=+0.0959, Recent IC=+0.0704, 1st-half IC=+0.1267, 2nd-half IC=+0.0875, Neg regimes=1/5
- Weak component: `high_low_sequence_momentum` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.190, Q2=-0.012, Q3_mid=+0.113, Q4=+0.119, Q5_high_vol=+0.123

**`trend_day_regime_conviction`** (Lock IC=+0.0886, Sharpe=+0.5435)
- Admission: Train IC=+0.2093, Deflated=+0.2084, IR=0.40, Mono=0.65, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.143 | 2016: +0.052 | 2017: +0.195 | 2018: +0.125 | 2019: +0.075 | 2020: +0.094 | 2021: +0.051 | 2022: +0.094 | 2023: +0.081 | 2024: +0.130 | 2025: +0.130 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.280 | 2016: +0.130 | 2017: +0.263 | 2018: +0.187 | 2019: +0.222 | 2020: +0.127 | 2021: -0.006 | 2022: +0.147 | 2023: +0.106 | 2024: +0.225 | 2025: +0.036 | 2026: +0.067
- IC CV=0.46, Neg years (linear/tail)=0/1 of 7, Half ratio=0.71, Recency ratio=0.75
- Early IC=+0.0973, Recent IC=+0.0725, 1st-half IC=+0.1278, 2nd-half IC=+0.0910, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.193, Q2=-0.009, Q3_mid=+0.117, Q4=+0.119, Q5_high_vol=+0.126

**`combo_rank_min__close_vs_open_range__max_down_ret`** (Lock IC=+0.0965, Sharpe=+0.5418)
- Admission: Train IC=+0.2016, Deflated=+0.2007, IR=0.50, Mono=0.69, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.081 | 2017: +0.225 | 2018: +0.120 | 2019: +0.084 | 2020: +0.141 | 2021: +0.037 | 2022: +0.078 | 2023: +0.082 | 2024: +0.114 | 2025: +0.137 | 2026: +0.035
- Yearly Tail ICs:   2015: +0.336 | 2016: +0.021 | 2017: +0.210 | 2018: +0.113 | 2019: +0.166 | 2020: +0.128 | 2021: +0.307 | 2022: +0.293 | 2023: +0.153 | 2024: +0.190 | 2025: +0.127 | 2026: +0.209
- IC CV=0.57, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.51
- Early IC=+0.1777, Recent IC=+0.0902, 1st-half IC=+0.1595, 2nd-half IC=+0.1084, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.193, Q2=-0.038, Q3_mid=+0.134, Q4=+0.105, Q5_high_vol=+0.224

**`combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.0882, Sharpe=+0.5405)
- Admission: Train IC=+0.3190, Deflated=+0.3187, IR=0.81, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.073 | 2017: +0.122 | 2018: +0.214 | 2019: +0.181 | 2020: +0.190 | 2021: +0.130 | 2022: +0.045 | 2023: +0.059 | 2024: +0.118 | 2025: +0.060 | 2026: +0.171
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.066 | 2017: +0.174 | 2018: +0.379 | 2019: +0.446 | 2020: +0.243 | 2021: +0.287 | 2022: -0.108 | 2023: +0.033 | 2024: +0.219 | 2025: +0.111 | 2026: +0.384
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.95, Recency ratio=0.85
- Early IC=+0.1871, Recent IC=+0.1599, 1st-half IC=+0.1933, 2nd-half IC=+0.1840, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.130, Q3_mid=+0.136, Q4=+0.138, Q5_high_vol=+0.313

**`combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration`** (Lock IC=+0.0883, Sharpe=+0.5405)
- Admission: Train IC=+0.2871, Deflated=+0.2867, IR=0.70, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.292 | 2016: +0.072 | 2017: +0.122 | 2018: +0.214 | 2019: +0.183 | 2020: +0.187 | 2021: +0.129 | 2022: +0.047 | 2023: +0.060 | 2024: +0.115 | 2025: +0.059 | 2026: +0.173
- Yearly Tail ICs:   2015: +0.107 | 2016: +0.040 | 2017: +0.176 | 2018: +0.355 | 2019: +0.459 | 2020: +0.180 | 2021: +0.262 | 2022: -0.053 | 2023: +0.066 | 2024: +0.138 | 2025: +0.082 | 2026: +0.352
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.95, Recency ratio=0.87
- Early IC=+0.1822, Recent IC=+0.1583, 1st-half IC=+0.1922, 2nd-half IC=+0.1832, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.128, Q2=+0.129, Q3_mid=+0.135, Q4=+0.138, Q5_high_vol=+0.304

**`combo_min__max_up_ret__first_bar_return`** (Lock IC=+0.0809, Sharpe=+0.5375)
- Admission: Train IC=+0.2159, Deflated=+0.2154, IR=0.47, Mono=0.67, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.100 | 2017: +0.203 | 2018: +0.228 | 2019: +0.135 | 2020: +0.124 | 2021: +0.100 | 2022: +0.087 | 2023: +0.095 | 2024: +0.105 | 2025: +0.079 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.051 | 2017: +0.156 | 2018: +0.449 | 2019: +0.151 | 2020: +0.182 | 2021: +0.163 | 2022: +0.110 | 2023: +0.150 | 2024: +0.173 | 2025: +0.005 | 2026: -0.167
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.64
- Early IC=+0.1759, Recent IC=+0.1121, 1st-half IC=+0.2050, 2nd-half IC=+0.1473, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.058, Q3_mid=+0.176, Q4=+0.160, Q5_high_vol=+0.247

**`combo_min__max_up_ret__bar_ret_0`** (Lock IC=+0.0809, Sharpe=+0.5375)
- Admission: Train IC=+0.2151, Deflated=+0.2146, IR=0.47, Mono=0.67, p=0.0004, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.100 | 2017: +0.204 | 2018: +0.228 | 2019: +0.135 | 2020: +0.124 | 2021: +0.100 | 2022: +0.087 | 2023: +0.096 | 2024: +0.105 | 2025: +0.079 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.192 | 2016: +0.051 | 2017: +0.169 | 2018: +0.449 | 2019: +0.151 | 2020: +0.182 | 2021: +0.160 | 2022: +0.110 | 2023: +0.150 | 2024: +0.173 | 2025: +0.005 | 2026: -0.167
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.64
- Early IC=+0.1760, Recent IC=+0.1120, 1st-half IC=+0.2050, 2nd-half IC=+0.1472, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.058, Q3_mid=+0.176, Q4=+0.160, Q5_high_vol=+0.247

**`combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0997, Sharpe=+0.5319)
- Admission: Train IC=+0.2853, Deflated=+0.2845, IR=0.77, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.097 | 2017: +0.205 | 2018: +0.219 | 2019: +0.129 | 2020: +0.139 | 2021: +0.084 | 2022: +0.104 | 2023: +0.117 | 2024: +0.132 | 2025: +0.125 | 2026: -0.048
- Yearly Tail ICs:   2015: +0.200 | 2016: +0.263 | 2017: +0.318 | 2018: +0.399 | 2019: +0.217 | 2020: +0.201 | 2021: +0.250 | 2022: +0.091 | 2023: +0.130 | 2024: +0.349 | 2025: -0.127 | 2026: -0.073
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.64
- Early IC=+0.1733, Recent IC=+0.1117, 1st-half IC=+0.2135, 2nd-half IC=+0.1395, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.065, Q3_mid=+0.151, Q4=+0.186, Q5_high_vol=+0.263

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.1046, Sharpe=+0.5221)
- Admission: Train IC=+0.2769, Deflated=+0.2760, IR=0.88, Mono=0.84, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.052 | 2017: +0.218 | 2018: +0.199 | 2019: +0.129 | 2020: +0.151 | 2021: +0.097 | 2022: +0.082 | 2023: +0.133 | 2024: +0.149 | 2025: +0.105 | 2026: -0.007
- Yearly Tail ICs:   2015: +0.371 | 2016: +0.227 | 2017: +0.327 | 2018: +0.318 | 2019: +0.192 | 2020: +0.224 | 2021: +0.232 | 2022: +0.235 | 2023: +0.243 | 2024: +0.179 | 2025: +0.020 | 2026: -0.108
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.83
- Early IC=+0.1486, Recent IC=+0.1241, 1st-half IC=+0.1837, 2nd-half IC=+0.1445, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.036, Q3_mid=+0.171, Q4=+0.152, Q5_high_vol=+0.232

**`combo_rank_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0992, Sharpe=+0.5215)
- Admission: Train IC=+0.2480, Deflated=+0.2473, IR=0.79, Mono=0.76, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.266 | 2016: +0.094 | 2017: +0.235 | 2018: +0.223 | 2019: +0.107 | 2020: +0.153 | 2021: +0.154 | 2022: +0.123 | 2023: +0.098 | 2024: +0.145 | 2025: +0.078 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.259 | 2016: +0.103 | 2017: +0.148 | 2018: +0.362 | 2019: +0.318 | 2020: +0.098 | 2021: +0.316 | 2022: +0.211 | 2023: -0.005 | 2024: +0.273 | 2025: +0.022 | 2026: -0.232
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.83
- Early IC=+0.1815, Recent IC=+0.1516, 1st-half IC=+0.2160, 2nd-half IC=+0.1576, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.220, Q2=+0.075, Q3_mid=+0.174, Q4=+0.195, Q5_high_vol=+0.278

**`combo_rank_min__max_up_ret__bar_ret_0`** (Lock IC=+0.0708, Sharpe=+0.5192)
- Admission: Train IC=+0.2350, Deflated=+0.2347, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.097 | 2017: +0.204 | 2018: +0.243 | 2019: +0.143 | 2020: +0.122 | 2021: +0.089 | 2022: +0.070 | 2023: +0.076 | 2024: +0.101 | 2025: +0.085 | 2026: -0.000
- Yearly Tail ICs:   2015: +0.160 | 2016: +0.150 | 2017: +0.211 | 2018: +0.461 | 2019: +0.219 | 2020: +0.252 | 2021: +0.194 | 2022: +0.005 | 2023: +0.056 | 2024: +0.209 | 2025: +0.141 | 2026: -0.124
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.61
- Early IC=+0.1698, Recent IC=+0.1035, 1st-half IC=+0.2008, 2nd-half IC=+0.1450, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.054, Q3_mid=+0.173, Q4=+0.154, Q5_high_vol=+0.251

**`combo_mean__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0935, Sharpe=+0.5186)
- Admission: Train IC=+0.2349, Deflated=+0.2343, IR=0.69, Mono=0.73, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.089 | 2017: +0.236 | 2018: +0.257 | 2019: +0.154 | 2020: +0.157 | 2021: +0.135 | 2022: +0.085 | 2023: +0.090 | 2024: +0.153 | 2025: +0.090 | 2026: +0.002
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.001 | 2017: +0.222 | 2018: +0.444 | 2019: +0.160 | 2020: +0.233 | 2021: +0.307 | 2022: +0.204 | 2023: +0.167 | 2024: +0.225 | 2025: +0.054 | 2026: -0.201
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.86, Recency ratio=0.85
- Early IC=+0.1723, Recent IC=+0.1458, 1st-half IC=+0.2074, 2nd-half IC=+0.1789, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.066, Q3_mid=+0.174, Q4=+0.165, Q5_high_vol=+0.281

**`combo_mean__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0934, Sharpe=+0.5186)
- Admission: Train IC=+0.2348, Deflated=+0.2342, IR=0.70, Mono=0.73, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.255 | 2016: +0.089 | 2017: +0.236 | 2018: +0.257 | 2019: +0.154 | 2020: +0.157 | 2021: +0.135 | 2022: +0.085 | 2023: +0.090 | 2024: +0.153 | 2025: +0.090 | 2026: +0.003
- Yearly Tail ICs:   2015: +0.277 | 2016: +0.001 | 2017: +0.222 | 2018: +0.444 | 2019: +0.162 | 2020: +0.233 | 2021: +0.307 | 2022: +0.204 | 2023: +0.167 | 2024: +0.222 | 2025: +0.055 | 2026: -0.201
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.86, Recency ratio=0.85
- Early IC=+0.1724, Recent IC=+0.1458, 1st-half IC=+0.2074, 2nd-half IC=+0.1788, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.212, Q2=+0.066, Q3_mid=+0.174, Q4=+0.165, Q5_high_vol=+0.282

**`combo_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0799, Sharpe=+0.5160)
- Admission: Train IC=+0.2083, Deflated=+0.2078, IR=0.62, Mono=0.71, p=0.0006, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.099 | 2017: +0.263 | 2018: +0.229 | 2019: +0.143 | 2020: +0.129 | 2021: +0.080 | 2022: +0.086 | 2023: +0.045 | 2024: +0.129 | 2025: +0.103 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.253 | 2016: -0.005 | 2017: +0.209 | 2018: +0.421 | 2019: +0.111 | 2020: +0.210 | 2021: +0.198 | 2022: +0.202 | 2023: +0.201 | 2024: +0.222 | 2025: +0.037 | 2026: -0.223
- IC CV=0.40, Neg years (linear/tail)=0/1 of 7, Half ratio=0.78, Recency ratio=0.64
- Early IC=+0.1627, Recent IC=+0.1045, 1st-half IC=+0.1910, 2nd-half IC=+0.1492, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.021, Q3_mid=+0.154, Q4=+0.131, Q5_high_vol=+0.236

**`combo_max__first_bar_return__max_down_ret`** (Lock IC=+0.0799, Sharpe=+0.5160)
- Admission: Train IC=+0.2082, Deflated=+0.2077, IR=0.62, Mono=0.71, p=0.0006, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.099 | 2017: +0.263 | 2018: +0.229 | 2019: +0.142 | 2020: +0.129 | 2021: +0.079 | 2022: +0.086 | 2023: +0.045 | 2024: +0.129 | 2025: +0.103 | 2026: -0.003
- Yearly Tail ICs:   2015: +0.253 | 2016: -0.003 | 2017: +0.210 | 2018: +0.421 | 2019: +0.111 | 2020: +0.210 | 2021: +0.198 | 2022: +0.202 | 2023: +0.201 | 2024: +0.222 | 2025: +0.037 | 2026: -0.223
- IC CV=0.40, Neg years (linear/tail)=0/1 of 7, Half ratio=0.78, Recency ratio=0.64
- Early IC=+0.1629, Recent IC=+0.1043, 1st-half IC=+0.1910, 2nd-half IC=+0.1491, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.021, Q3_mid=+0.154, Q4=+0.130, Q5_high_vol=+0.236

**`combo_mean__star50_limit_proximity_early__close_vs_open_range`** (Lock IC=+0.1024, Sharpe=+0.5133)
- Admission: Train IC=+0.2595, Deflated=+0.2588, IR=0.75, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.087 | 2017: +0.202 | 2018: +0.108 | 2019: +0.105 | 2020: +0.125 | 2021: +0.059 | 2022: +0.079 | 2023: +0.061 | 2024: +0.115 | 2025: +0.114 | 2026: +0.101
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.191 | 2017: +0.305 | 2018: +0.278 | 2019: +0.316 | 2020: +0.203 | 2021: +0.208 | 2022: +0.221 | 2023: +0.012 | 2024: +0.271 | 2025: +0.067 | 2026: +0.066
- IC CV=0.50, Neg years (linear/tail)=0/0 of 7, Half ratio=0.52, Recency ratio=0.51
- Early IC=+0.1791, Recent IC=+0.0918, 1st-half IC=+0.1947, 2nd-half IC=+0.1004, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.023, Q3_mid=+0.100, Q4=+0.152, Q5_high_vol=+0.208

**`first_bar_return`** (Lock IC=+0.0680, Sharpe=+0.5073)
- Admission: Train IC=+0.1937, Deflated=+0.1931, IR=0.59, Mono=0.71, p=0.0008, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.209 | 2016: +0.112 | 2017: +0.153 | 2018: +0.238 | 2019: +0.148 | 2020: +0.088 | 2021: +0.099 | 2022: +0.063 | 2023: +0.062 | 2024: +0.107 | 2025: +0.092 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.004 | 2017: +0.297 | 2018: +0.423 | 2019: +0.144 | 2020: +0.207 | 2021: +0.212 | 2022: +0.189 | 2023: +0.121 | 2024: +0.212 | 2025: +0.043 | 2026: -0.189
- IC CV=0.35, Neg years (linear/tail)=0/1 of 7, Half ratio=0.81, Recency ratio=0.58
- Early IC=+0.1605, Recent IC=+0.0933, 1st-half IC=+0.1765, 2nd-half IC=+0.1437, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.025, Q3_mid=+0.141, Q4=+0.143, Q5_high_vol=+0.231

**`combo_max__first_bar_sentiment__bar_ret_0`** (Lock IC=+0.0768, Sharpe=+0.5073)
- Admission: Train IC=+0.1927, Deflated=+0.1926, IR=0.55, Mono=0.69, p=0.0010, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.109 | 2017: +0.104 | 2018: +0.266 | 2019: +0.131 | 2020: +0.090 | 2021: +0.110 | 2022: +0.111 | 2023: +0.047 | 2024: +0.107 | 2025: +0.058 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.080 | 2016: +0.040 | 2017: +0.231 | 2018: +0.443 | 2019: +0.167 | 2020: +0.207 | 2021: +0.218 | 2022: +0.137 | 2023: +0.156 | 2024: +0.185 | 2025: +0.032 | 2026: -0.157
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.90, Recency ratio=0.68
- Early IC=+0.1462, Recent IC=+0.0999, 1st-half IC=+0.1589, 2nd-half IC=+0.1427, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.014, Q3_mid=+0.147, Q4=+0.163, Q5_high_vol=+0.205

**`combo_rank_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0852, Sharpe=+0.5028)
- Admission: Train IC=+0.2418, Deflated=+0.2411, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.080 | 2017: +0.185 | 2018: +0.173 | 2019: +0.118 | 2020: +0.063 | 2021: +0.055 | 2022: +0.043 | 2023: +0.067 | 2024: +0.123 | 2025: +0.138 | 2026: +0.022
- Yearly Tail ICs:   2015: +0.448 | 2016: +0.133 | 2017: +0.248 | 2018: +0.283 | 2019: +0.223 | 2020: +0.076 | 2021: +0.272 | 2022: +0.156 | 2023: +0.140 | 2024: +0.200 | 2025: +0.186 | 2026: +0.283
- IC CV=0.46, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.40
- Early IC=+0.1461, Recent IC=+0.0586, 1st-half IC=+0.1599, 2nd-half IC=+0.1006, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.195, Q2=-0.030, Q3_mid=+0.122, Q4=+0.142, Q5_high_vol=+0.185

**`combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1082, Sharpe=+0.5009)
- Admission: Train IC=+0.3032, Deflated=+0.3033, IR=0.84, Mono=0.76, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.285 | 2016: +0.138 | 2017: +0.218 | 2018: +0.124 | 2019: +0.143 | 2020: +0.175 | 2021: +0.141 | 2022: +0.048 | 2023: +0.106 | 2024: +0.153 | 2025: +0.104 | 2026: +0.091
- Yearly Tail ICs:   2015: +0.345 | 2016: +0.193 | 2017: +0.175 | 2018: +0.350 | 2019: +0.367 | 2020: +0.257 | 2021: +0.326 | 2022: +0.012 | 2023: +0.014 | 2024: +0.355 | 2025: +0.029 | 2026: +0.017
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.66, Recency ratio=0.75
- Early IC=+0.2114, Recent IC=+0.1580, 1st-half IC=+0.2262, 2nd-half IC=+0.1482, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.069, Q3_mid=+0.126, Q4=+0.222, Q5_high_vol=+0.265

**`combo_rank_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0958, Sharpe=+0.4945)
- Admission: Train IC=+0.2869, Deflated=+0.2863, IR=0.73, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.084 | 2017: +0.178 | 2018: +0.119 | 2019: +0.074 | 2020: +0.106 | 2021: +0.122 | 2022: +0.077 | 2023: +0.091 | 2024: +0.149 | 2025: +0.154 | 2026: -0.063
- Yearly Tail ICs:   2015: +0.445 | 2016: +0.222 | 2017: +0.179 | 2018: +0.282 | 2019: +0.330 | 2020: +0.148 | 2021: +0.286 | 2022: +0.022 | 2023: +0.103 | 2024: +0.332 | 2025: +0.115 | 2026: -0.098
- IC CV=0.35, Neg years (linear/tail)=0/0 of 7, Half ratio=0.66, Recency ratio=0.79
- Early IC=+0.1423, Recent IC=+0.1130, 1st-half IC=+0.1576, 2nd-half IC=+0.1042, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.033, Q3_mid=+0.153, Q4=+0.133, Q5_high_vol=+0.158

**`combo_mean__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0974, Sharpe=+0.4943)
- Admission: Train IC=+0.1979, Deflated=+0.1973, IR=0.63, Mono=0.76, p=0.0006, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.288 | 2016: +0.061 | 2017: +0.242 | 2018: +0.193 | 2019: +0.137 | 2020: +0.165 | 2021: +0.123 | 2022: +0.078 | 2023: +0.091 | 2024: +0.138 | 2025: +0.108 | 2026: +0.018
- Yearly Tail ICs:   2015: +0.401 | 2016: -0.028 | 2017: +0.137 | 2018: +0.125 | 2019: +0.336 | 2020: +0.019 | 2021: +0.390 | 2022: +0.257 | 2023: +0.148 | 2024: +0.233 | 2025: +0.086 | 2026: +0.010
- IC CV=0.41, Neg years (linear/tail)=0/1 of 7, Half ratio=0.90, Recency ratio=0.82
- Early IC=+0.1744, Recent IC=+0.1439, 1st-half IC=+0.1817, 2nd-half IC=+0.1629, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.207, Q2=+0.057, Q3_mid=+0.159, Q4=+0.126, Q5_high_vol=+0.273

**`combo_sig_product__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1254, Sharpe=+0.4916)
- Admission: Train IC=+0.2007, Deflated=+0.1999, IR=0.34, Mono=0.66, p=0.0006, MaxCorr=0.63
- Yearly Linear ICs: 2015: +0.183 | 2016: +0.078 | 2017: +0.220 | 2018: +0.102 | 2019: +0.176 | 2020: +0.109 | 2021: +0.089 | 2022: +0.105 | 2023: +0.057 | 2024: +0.162 | 2025: +0.063 | 2026: +0.204
- Yearly Tail ICs:   2015: +0.192 | 2016: -0.072 | 2017: +0.231 | 2018: +0.325 | 2019: +0.267 | 2020: +0.186 | 2021: +0.230 | 2022: +0.217 | 2023: -0.018 | 2024: +0.079 | 2025: -0.129 | 2026: +0.216
- IC CV=0.38, Neg years (linear/tail)=0/1 of 7, Half ratio=0.79, Recency ratio=0.76
- Early IC=+0.1304, Recent IC=+0.0989, 1st-half IC=+0.1628, 2nd-half IC=+0.1279, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.177, Q2=+0.044, Q3_mid=+0.093, Q4=+0.132, Q5_high_vol=+0.210

**`combo_min__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1014, Sharpe=+0.4889)
- Admission: Train IC=+0.3310, Deflated=+0.3310, IR=0.84, Mono=0.79, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.154 | 2017: +0.215 | 2018: +0.133 | 2019: +0.133 | 2020: +0.177 | 2021: +0.150 | 2022: +0.035 | 2023: +0.106 | 2024: +0.152 | 2025: +0.085 | 2026: +0.108
- Yearly Tail ICs:   2015: +0.248 | 2016: +0.292 | 2017: +0.179 | 2018: +0.438 | 2019: +0.223 | 2020: +0.315 | 2021: +0.407 | 2022: -0.046 | 2023: -0.019 | 2024: +0.277 | 2025: -0.025 | 2026: +0.327
- IC CV=0.28, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.75
- Early IC=+0.2187, Recent IC=+0.1636, 1st-half IC=+0.2322, 2nd-half IC=+0.1517, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.069, Q3_mid=+0.132, Q4=+0.234, Q5_high_vol=+0.260

**`combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1047, Sharpe=+0.4866)
- Admission: Train IC=+0.2694, Deflated=+0.2690, IR=0.76, Mono=0.74, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.293 | 2016: +0.089 | 2017: +0.243 | 2018: +0.178 | 2019: +0.147 | 2020: +0.180 | 2021: +0.116 | 2022: +0.068 | 2023: +0.075 | 2024: +0.138 | 2025: +0.091 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.165 | 2016: +0.198 | 2017: +0.175 | 2018: +0.277 | 2019: +0.390 | 2020: +0.129 | 2021: +0.157 | 2022: +0.106 | 2023: -0.095 | 2024: +0.212 | 2025: -0.058 | 2026: +0.163
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.74, Recency ratio=0.78
- Early IC=+0.1907, Recent IC=+0.1484, 1st-half IC=+0.2216, 2nd-half IC=+0.1641, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.204, Q2=+0.086, Q3_mid=+0.149, Q4=+0.177, Q5_high_vol=+0.276

**`combo_mean__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0934, Sharpe=+0.4866)
- Admission: Train IC=+0.2708, Deflated=+0.2703, IR=0.70, Mono=0.78, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.263 | 2016: +0.126 | 2017: +0.178 | 2018: +0.234 | 2019: +0.117 | 2020: +0.128 | 2021: +0.126 | 2022: +0.106 | 2023: +0.085 | 2024: +0.144 | 2025: +0.091 | 2026: -0.025
- Yearly Tail ICs:   2015: +0.310 | 2016: +0.234 | 2017: +0.220 | 2018: +0.446 | 2019: +0.243 | 2020: +0.167 | 2021: +0.204 | 2022: -0.056 | 2023: +0.146 | 2024: +0.192 | 2025: -0.035 | 2026: -0.196
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.65
- Early IC=+0.1946, Recent IC=+0.1267, 1st-half IC=+0.2111, 2nd-half IC=+0.1508, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.055, Q3_mid=+0.195, Q4=+0.172, Q5_high_vol=+0.284

**`combo_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0940, Sharpe=+0.4790)
- Admission: Train IC=+0.2438, Deflated=+0.2430, IR=0.83, Mono=0.75, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.098 | 2017: +0.208 | 2018: +0.208 | 2019: +0.092 | 2020: +0.147 | 2021: +0.079 | 2022: +0.116 | 2023: +0.097 | 2024: +0.129 | 2025: +0.088 | 2026: -0.046
- Yearly Tail ICs:   2015: +0.324 | 2016: +0.243 | 2017: +0.210 | 2018: +0.321 | 2019: +0.123 | 2020: +0.272 | 2021: +0.149 | 2022: +0.073 | 2023: +0.185 | 2024: +0.256 | 2025: -0.198 | 2026: -0.403
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.65
- Early IC=+0.1726, Recent IC=+0.1127, 1st-half IC=+0.1949, 2nd-half IC=+0.1378, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.012, Q3_mid=+0.168, Q4=+0.177, Q5_high_vol=+0.267

**`combo_sig_product__max_up_ret__body_size_progression`** (Lock IC=+0.0924, Sharpe=+0.4790)
- Admission: Train IC=+0.2143, Deflated=+0.2133, IR=0.80, Mono=0.76, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.248 | 2016: +0.157 | 2017: +0.091 | 2018: +0.142 | 2019: +0.095 | 2020: +0.137 | 2021: +0.104 | 2022: +0.064 | 2023: +0.064 | 2024: +0.126 | 2025: +0.114 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.262 | 2017: +0.063 | 2018: +0.152 | 2019: +0.019 | 2020: +0.249 | 2021: +0.201 | 2022: +0.051 | 2023: +0.093 | 2024: +0.065 | 2025: +0.202 | 2026: +0.245
- IC CV=0.36, Neg years (linear/tail)=0/0 of 7, Half ratio=0.66, Recency ratio=0.59
- Early IC=+0.2023, Recent IC=+0.1202, 1st-half IC=+0.1851, 2nd-half IC=+0.1222, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.173, Q2=+0.019, Q3_mid=+0.135, Q4=+0.180, Q5_high_vol=+0.234

**`combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0858, Sharpe=+0.4783)
- Admission: Train IC=+0.2682, Deflated=+0.2675, IR=0.75, Mono=0.76, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.138 | 2016: +0.032 | 2017: +0.186 | 2018: +0.158 | 2019: +0.085 | 2020: +0.113 | 2021: +0.097 | 2022: +0.064 | 2023: +0.099 | 2024: +0.133 | 2025: +0.112 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.418 | 2016: +0.212 | 2017: +0.314 | 2018: +0.294 | 2019: +0.165 | 2020: +0.135 | 2021: +0.315 | 2022: +0.266 | 2023: -0.080 | 2024: +0.260 | 2025: +0.085 | 2026: +0.014
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.96, Recency ratio=1.23
- Early IC=+0.0853, Recent IC=+0.1046, 1st-half IC=+0.1246, 2nd-half IC=+0.1199, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.183, Q2=+0.017, Q3_mid=+0.138, Q4=+0.103, Q5_high_vol=+0.170

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.1075, Sharpe=+0.4764)
- Admission: Train IC=+0.2792, Deflated=+0.2789, IR=0.87, Mono=0.79, p=0.0000, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.259 | 2016: +0.125 | 2017: +0.219 | 2018: +0.214 | 2019: +0.109 | 2020: +0.162 | 2021: +0.104 | 2022: +0.112 | 2023: +0.083 | 2024: +0.107 | 2025: +0.139 | 2026: +0.048
- Yearly Tail ICs:   2015: +0.311 | 2016: +0.229 | 2017: +0.226 | 2018: +0.346 | 2019: +0.324 | 2020: +0.198 | 2021: +0.267 | 2022: +0.253 | 2023: +0.177 | 2024: +0.202 | 2025: -0.038 | 2026: -0.074
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.69
- Early IC=+0.1918, Recent IC=+0.1333, 1st-half IC=+0.2251, 2nd-half IC=+0.1452, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.222, Q2=+0.048, Q3_mid=+0.169, Q4=+0.194, Q5_high_vol=+0.264

**`combo_max__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1047, Sharpe=+0.4717)
- Admission: Train IC=+0.2276, Deflated=+0.2270, IR=0.77, Mono=0.74, p=0.0002, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.162 | 2017: +0.173 | 2018: +0.190 | 2019: +0.103 | 2020: +0.130 | 2021: +0.092 | 2022: +0.106 | 2023: +0.069 | 2024: +0.111 | 2025: +0.079 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.312 | 2017: +0.252 | 2018: +0.281 | 2019: +0.113 | 2020: +0.127 | 2021: +0.213 | 2022: +0.113 | 2023: -0.066 | 2024: -0.002 | 2025: -0.009 | 2026: +0.199
- IC CV=0.26, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.61
- Early IC=+0.1808, Recent IC=+0.1109, 1st-half IC=+0.1992, 2nd-half IC=+0.1276, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.157, Q2=+0.078, Q3_mid=+0.153, Q4=+0.110, Q5_high_vol=+0.259

**`combo_max__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1048, Sharpe=+0.4717)
- Admission: Train IC=+0.2273, Deflated=+0.2268, IR=0.77, Mono=0.74, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.199 | 2016: +0.162 | 2017: +0.173 | 2018: +0.190 | 2019: +0.103 | 2020: +0.130 | 2021: +0.092 | 2022: +0.106 | 2023: +0.069 | 2024: +0.111 | 2025: +0.079 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.119 | 2016: +0.312 | 2017: +0.250 | 2018: +0.283 | 2019: +0.107 | 2020: +0.128 | 2021: +0.216 | 2022: +0.118 | 2023: -0.063 | 2024: -0.001 | 2025: -0.009 | 2026: +0.199
- IC CV=0.26, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.61
- Early IC=+0.1809, Recent IC=+0.1110, 1st-half IC=+0.1993, 2nd-half IC=+0.1275, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.079, Q3_mid=+0.153, Q4=+0.110, Q5_high_vol=+0.259

**`combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0809, Sharpe=+0.4676)
- Admission: Train IC=+0.2232, Deflated=+0.2230, IR=0.69, Mono=0.77, p=0.0002, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.020 | 2017: +0.164 | 2018: +0.187 | 2019: +0.126 | 2020: +0.171 | 2021: +0.144 | 2022: +0.061 | 2023: +0.098 | 2024: +0.113 | 2025: +0.044 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.238 | 2016: +0.049 | 2017: +0.263 | 2018: +0.341 | 2019: +0.313 | 2020: +0.061 | 2021: +0.245 | 2022: -0.024 | 2023: +0.153 | 2024: +0.255 | 2025: -0.114 | 2026: +0.305
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=1.23, Recency ratio=1.17
- Early IC=+0.1344, Recent IC=+0.1576, 1st-half IC=+0.1383, 2nd-half IC=+0.1703, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.135, Q2=+0.101, Q3_mid=+0.136, Q4=+0.083, Q5_high_vol=+0.286

**`combo_max__max_up_ret__early_body_momentum`** (Lock IC=+0.0867, Sharpe=+0.4672)
- Admission: Train IC=+0.2549, Deflated=+0.2541, IR=0.91, Mono=0.80, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.215 | 2016: +0.100 | 2017: +0.147 | 2018: +0.200 | 2019: +0.067 | 2020: +0.125 | 2021: +0.058 | 2022: +0.113 | 2023: +0.087 | 2024: +0.124 | 2025: +0.091 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.275 | 2016: +0.212 | 2017: +0.248 | 2018: +0.292 | 2019: +0.116 | 2020: +0.235 | 2021: +0.206 | 2022: +0.130 | 2023: +0.136 | 2024: +0.269 | 2025: -0.136 | 2026: -0.330
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.58
- Early IC=+0.1575, Recent IC=+0.0915, 1st-half IC=+0.1763, 2nd-half IC=+0.1174, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=+0.151, Q2=-0.013, Q3_mid=+0.161, Q4=+0.169, Q5_high_vol=+0.250

**`combo_rel_diff__max_up_ret__body_size_progression`** (Lock IC=+0.0824, Sharpe=+0.4647)
- Admission: Train IC=+0.2673, Deflated=+0.2666, IR=1.05, Mono=0.80, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.296 | 2016: +0.104 | 2017: +0.192 | 2018: +0.209 | 2019: +0.154 | 2020: +0.168 | 2021: +0.138 | 2022: +0.065 | 2023: +0.093 | 2024: +0.099 | 2025: +0.041 | 2026: +0.106
- Yearly Tail ICs:   2015: +0.216 | 2016: +0.155 | 2017: +0.367 | 2018: +0.372 | 2019: +0.376 | 2020: +0.151 | 2021: +0.253 | 2022: +0.132 | 2023: +0.192 | 2024: -0.017 | 2025: -0.018 | 2026: +0.060
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.89, Recency ratio=0.76
- Early IC=+0.2001, Recent IC=+0.1529, 1st-half IC=+0.2015, 2nd-half IC=+0.1796, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.158, Q2=+0.095, Q3_mid=+0.178, Q4=+0.155, Q5_high_vol=+0.321

**`combo_rank_max__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0908, Sharpe=+0.4636)
- Admission: Train IC=+0.2103, Deflated=+0.2096, IR=0.72, Mono=0.75, p=0.0006, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.113 | 2017: +0.209 | 2018: +0.216 | 2019: +0.103 | 2020: +0.141 | 2021: +0.128 | 2022: +0.124 | 2023: +0.086 | 2024: +0.140 | 2025: +0.119 | 2026: -0.096
- Yearly Tail ICs:   2015: +0.274 | 2016: +0.042 | 2017: +0.263 | 2018: +0.327 | 2019: +0.151 | 2020: +0.314 | 2021: +0.258 | 2022: +0.267 | 2023: +0.316 | 2024: +0.271 | 2025: -0.123 | 2026: -0.469
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.79
- Early IC=+0.1720, Recent IC=+0.1362, 1st-half IC=+0.1893, 2nd-half IC=+0.1541, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.042, Q3_mid=+0.174, Q4=+0.153, Q5_high_vol=+0.238

**`combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0849, Sharpe=+0.4635)
- Admission: Train IC=+0.2470, Deflated=+0.2471, IR=0.62, Mono=0.72, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.197 | 2016: +0.052 | 2017: +0.251 | 2018: +0.159 | 2019: +0.067 | 2020: +0.164 | 2021: +0.084 | 2022: +0.091 | 2023: +0.130 | 2024: +0.087 | 2025: +0.076 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.319 | 2016: +0.033 | 2017: +0.379 | 2018: +0.248 | 2019: +0.069 | 2020: +0.254 | 2021: +0.262 | 2022: +0.178 | 2023: +0.089 | 2024: +0.298 | 2025: +0.079 | 2026: -0.233
- IC CV=0.49, Neg years (linear/tail)=0/0 of 7, Half ratio=0.91, Recency ratio=1.00
- Early IC=+0.1244, Recent IC=+0.1242, 1st-half IC=+0.1512, 2nd-half IC=+0.1374, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.187, Q2=+0.050, Q3_mid=+0.167, Q4=+0.137, Q5_high_vol=+0.175

**`first_30min_return`** (Lock IC=+0.0884, Sharpe=+0.4547)
- Admission: Train IC=+0.1461, Deflated=+0.1453, IR=0.47, Mono=0.70, p=0.0086, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.88
- Early IC=+0.0999, Recent IC=+0.0884, 1st-half IC=+0.1378, 2nd-half IC=+0.0988, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.010, Q3_mid=+0.143, Q4=+0.124, Q5_high_vol=+0.134

**`open_to_current_return`** (Lock IC=+0.0884, Sharpe=+0.4547)
- Admission: Train IC=+0.1461, Deflated=+0.1453, IR=0.47, Mono=0.70, p=0.0086, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.144 | 2016: +0.056 | 2017: +0.205 | 2018: +0.130 | 2019: +0.080 | 2020: +0.092 | 2021: +0.085 | 2022: +0.094 | 2023: +0.095 | 2024: +0.120 | 2025: +0.164 | 2026: -0.113
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.099 | 2017: +0.224 | 2018: +0.229 | 2019: +0.073 | 2020: +0.062 | 2021: +0.270 | 2022: +0.181 | 2023: +0.257 | 2024: +0.228 | 2025: +0.208 | 2026: -0.307
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.72, Recency ratio=0.88
- Early IC=+0.0999, Recent IC=+0.0884, 1st-half IC=+0.1378, 2nd-half IC=+0.0988, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.179, Q2=+0.010, Q3_mid=+0.143, Q4=+0.124, Q5_high_vol=+0.134

**`combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum`** (Lock IC=+0.0949, Sharpe=+0.4467)
- Admission: Train IC=+0.2202, Deflated=+0.2199, IR=0.48, Mono=0.67, p=0.0004, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.213 | 2016: +0.105 | 2017: +0.114 | 2018: +0.161 | 2019: +0.080 | 2020: +0.102 | 2021: +0.022 | 2022: +0.125 | 2023: +0.073 | 2024: +0.098 | 2025: +0.091 | 2026: +0.065
- Yearly Tail ICs:   2015: +0.058 | 2016: +0.361 | 2017: +0.148 | 2018: +0.223 | 2019: +0.156 | 2020: +0.118 | 2021: +0.142 | 2022: +0.087 | 2023: +0.157 | 2024: +0.200 | 2025: -0.026 | 2026: -0.152
- IC CV=0.49, Neg years (linear/tail)=0/0 of 7, Half ratio=0.50, Recency ratio=0.39
- Early IC=+0.1590, Recent IC=+0.0621, 1st-half IC=+0.1781, 2nd-half IC=+0.0884, Neg regimes=1/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.140, Q2=-0.006, Q3_mid=+0.143, Q4=+0.108, Q5_high_vol=+0.244

**`combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency`** (Lock IC=+0.0997, Sharpe=+0.4454)
- Admission: Train IC=+0.1753, Deflated=+0.1750, IR=0.44, Mono=0.65, p=0.0014, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.049 | 2017: +0.152 | 2018: +0.118 | 2019: +0.074 | 2020: +0.101 | 2021: +0.010 | 2022: +0.146 | 2023: +0.084 | 2024: +0.086 | 2025: +0.097 | 2026: +0.034
- Yearly Tail ICs:   2015: +0.060 | 2016: +0.200 | 2017: +0.146 | 2018: +0.101 | 2019: +0.241 | 2020: +0.119 | 2021: +0.106 | 2022: +0.179 | 2023: +0.111 | 2024: +0.153 | 2025: -0.004 | 2026: -0.210
- IC CV=0.68, Neg years (linear/tail)=0/0 of 7, Half ratio=0.40, Recency ratio=0.34
- Early IC=+0.1535, Recent IC=+0.0521, 1st-half IC=+0.1820, 2nd-half IC=+0.0725, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.008, Q3_mid=+0.132, Q4=+0.088, Q5_high_vol=+0.214

**`combo_rel_diff__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0236, Sharpe=+0.4423)
- Admission: Train IC=+0.2636, Deflated=+0.2642, IR=0.70, Mono=0.75, p=0.0000, MaxCorr=0.44
- Yearly Linear ICs: 2015: +0.150 | 2016: +0.138 | 2017: -0.011 | 2018: +0.082 | 2019: +0.070 | 2020: +0.030 | 2021: +0.081 | 2022: +0.057 | 2023: -0.004 | 2024: +0.054 | 2025: -0.068 | 2026: +0.124
- Yearly Tail ICs:   2015: +0.455 | 2016: +0.225 | 2017: +0.124 | 2018: +0.264 | 2019: +0.306 | 2020: +0.145 | 2021: +0.131 | 2022: -0.022 | 2023: -0.011 | 2024: +0.101 | 2025: -0.102 | 2026: +0.414
- IC CV=0.68, Neg years (linear/tail)=1/0 of 7, Half ratio=0.61, Recency ratio=0.39
- Early IC=+0.1440, Recent IC=+0.0555, 1st-half IC=+0.1027, 2nd-half IC=+0.0632, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.004, Q2=+0.131, Q3_mid=+0.068, Q4=+0.036, Q5_high_vol=+0.187

**`combo_min__max_up_ret__close_vs_open_range`** (Lock IC=+0.0998, Sharpe=+0.4420)
- Admission: Train IC=+0.2543, Deflated=+0.2535, IR=0.76, Mono=0.80, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.086 | 2017: +0.184 | 2018: +0.126 | 2019: +0.074 | 2020: +0.109 | 2021: +0.128 | 2022: +0.091 | 2023: +0.101 | 2024: +0.147 | 2025: +0.151 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.338 | 2016: +0.272 | 2017: +0.299 | 2018: +0.295 | 2019: +0.091 | 2020: +0.098 | 2021: +0.226 | 2022: +0.076 | 2023: +0.172 | 2024: +0.247 | 2025: +0.107 | 2026: -0.057
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.70, Recency ratio=0.85
- Early IC=+0.1403, Recent IC=+0.1187, 1st-half IC=+0.1572, 2nd-half IC=+0.1102, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.047, Q3_mid=+0.162, Q4=+0.128, Q5_high_vol=+0.166

**`combo_min__close_vs_open_range__max_down_ret`** (Lock IC=+0.0984, Sharpe=+0.4409)
- Admission: Train IC=+0.1991, Deflated=+0.1980, IR=0.52, Mono=0.68, p=0.0006, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.264 | 2016: +0.074 | 2017: +0.215 | 2018: +0.114 | 2019: +0.081 | 2020: +0.122 | 2021: +0.045 | 2022: +0.088 | 2023: +0.086 | 2024: +0.119 | 2025: +0.139 | 2026: +0.024
- Yearly Tail ICs:   2015: +0.346 | 2016: -0.018 | 2017: +0.226 | 2018: +0.166 | 2019: +0.193 | 2020: +0.133 | 2021: +0.284 | 2022: +0.292 | 2023: +0.137 | 2024: +0.203 | 2025: +0.146 | 2026: +0.045
- IC CV=0.57, Neg years (linear/tail)=0/1 of 7, Half ratio=0.65, Recency ratio=0.49
- Early IC=+0.1691, Recent IC=+0.0837, 1st-half IC=+0.1556, 2nd-half IC=+0.1017, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.037, Q3_mid=+0.133, Q4=+0.115, Q5_high_vol=+0.203

**`combo_max__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0904, Sharpe=+0.4366)
- Admission: Train IC=+0.2135, Deflated=+0.2128, IR=0.71, Mono=0.76, p=0.0006, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.111 | 2017: +0.210 | 2018: +0.219 | 2019: +0.102 | 2020: +0.142 | 2021: +0.126 | 2022: +0.123 | 2023: +0.085 | 2024: +0.137 | 2025: +0.122 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.285 | 2016: +0.050 | 2017: +0.253 | 2018: +0.328 | 2019: +0.157 | 2020: +0.290 | 2021: +0.245 | 2022: +0.245 | 2023: +0.334 | 2024: +0.261 | 2025: -0.131 | 2026: -0.447
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.79
- Early IC=+0.1701, Recent IC=+0.1338, 1st-half IC=+0.1890, 2nd-half IC=+0.1535, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.198, Q2=+0.041, Q3_mid=+0.170, Q4=+0.157, Q5_high_vol=+0.236

**`combo_mean__net_volume_flow__bar_ret_0`** (Lock IC=+0.0914, Sharpe=+0.4298)
- Admission: Train IC=+0.2246, Deflated=+0.2240, IR=0.55, Mono=0.71, p=0.0002, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.091 | 2017: +0.184 | 2018: +0.211 | 2019: +0.122 | 2020: +0.110 | 2021: +0.105 | 2022: +0.103 | 2023: +0.078 | 2024: +0.137 | 2025: +0.111 | 2026: -0.035
- Yearly Tail ICs:   2015: +0.295 | 2016: -0.026 | 2017: +0.169 | 2018: +0.399 | 2019: +0.135 | 2020: +0.203 | 2021: +0.303 | 2022: +0.274 | 2023: +0.312 | 2024: +0.264 | 2025: -0.011 | 2026: -0.278
- IC CV=0.32, Neg years (linear/tail)=0/1 of 7, Half ratio=0.80, Recency ratio=0.73
- Early IC=+0.1472, Recent IC=+0.1076, 1st-half IC=+0.1737, 2nd-half IC=+0.1383, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.188, Q2=-0.003, Q3_mid=+0.167, Q4=+0.145, Q5_high_vol=+0.219

**`combo_min__close_vs_open_range__bar_ret_0`** (Lock IC=+0.0864, Sharpe=+0.4258)
- Admission: Train IC=+0.2398, Deflated=+0.2389, IR=0.71, Mono=0.74, p=0.0000, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.084 | 2017: +0.185 | 2018: +0.173 | 2019: +0.118 | 2020: +0.064 | 2021: +0.057 | 2022: +0.045 | 2023: +0.070 | 2024: +0.130 | 2025: +0.140 | 2026: +0.015
- Yearly Tail ICs:   2015: +0.434 | 2016: +0.137 | 2017: +0.273 | 2018: +0.284 | 2019: +0.195 | 2020: +0.082 | 2021: +0.267 | 2022: +0.189 | 2023: +0.136 | 2024: +0.222 | 2025: +0.198 | 2026: +0.290
- IC CV=0.45, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.42
- Early IC=+0.1444, Recent IC=+0.0601, 1st-half IC=+0.1588, 2nd-half IC=+0.1021, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.197, Q2=-0.028, Q3_mid=+0.123, Q4=+0.138, Q5_high_vol=+0.185

**`combo_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0740, Sharpe=+0.4236)
- Admission: Train IC=+0.2145, Deflated=+0.2135, IR=0.58, Mono=0.70, p=0.0006, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.277 | 2016: +0.100 | 2017: +0.174 | 2018: +0.174 | 2019: +0.139 | 2020: +0.099 | 2021: +0.090 | 2022: +0.041 | 2023: +0.054 | 2024: +0.097 | 2025: +0.141 | 2026: +0.016
- Yearly Tail ICs:   2015: +0.369 | 2016: -0.054 | 2017: +0.304 | 2018: +0.186 | 2019: +0.342 | 2020: +0.202 | 2021: +0.384 | 2022: +0.093 | 2023: +0.103 | 2024: +0.260 | 2025: +0.141 | 2026: +0.069
- IC CV=0.41, Neg years (linear/tail)=0/1 of 7, Half ratio=0.78, Recency ratio=0.50
- Early IC=+0.1881, Recent IC=+0.0943, 1st-half IC=+0.1675, 2nd-half IC=+0.1304, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.012, Q3_mid=+0.126, Q4=+0.101, Q5_high_vol=+0.247

**`combo_max__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0930, Sharpe=+0.4216)
- Admission: Train IC=+0.2550, Deflated=+0.2539, IR=0.70, Mono=0.77, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.279 | 2016: +0.108 | 2017: +0.193 | 2018: +0.220 | 2019: +0.126 | 2020: +0.106 | 2021: +0.167 | 2022: +0.093 | 2023: +0.088 | 2024: +0.134 | 2025: +0.072 | 2026: +0.019
- Yearly Tail ICs:   2015: +0.504 | 2016: +0.114 | 2017: +0.109 | 2018: +0.317 | 2019: +0.321 | 2020: +0.076 | 2021: +0.267 | 2022: +0.324 | 2023: +0.075 | 2024: +0.084 | 2025: +0.119 | 2026: +0.022
- IC CV=0.35, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.71
- Early IC=+0.1934, Recent IC=+0.1365, 1st-half IC=+0.1948, 2nd-half IC=+0.1536, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.197, Q2=+0.044, Q3_mid=+0.181, Q4=+0.155, Q5_high_vol=+0.258

**`combo_mean__trend_bar_close_consistency__bar_ret_0`** (Lock IC=+0.0820, Sharpe=+0.4201)
- Admission: Train IC=+0.2264, Deflated=+0.2258, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.072 | 2017: +0.180 | 2018: +0.181 | 2019: +0.071 | 2020: +0.105 | 2021: +0.083 | 2022: +0.089 | 2023: +0.089 | 2024: +0.115 | 2025: +0.119 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.299 | 2016: -0.007 | 2017: +0.254 | 2018: +0.413 | 2019: +0.164 | 2020: +0.167 | 2021: +0.237 | 2022: +0.273 | 2023: +0.236 | 2024: +0.292 | 2025: +0.083 | 2026: -0.288
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.74, Recency ratio=0.79
- Early IC=+0.1196, Recent IC=+0.0943, 1st-half IC=+0.1518, 2nd-half IC=+0.1124, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.017, Q3_mid=+0.137, Q4=+0.138, Q5_high_vol=+0.184

**`combo_mean__trend_bar_close_consistency__first_bar_return`** (Lock IC=+0.0819, Sharpe=+0.4201)
- Admission: Train IC=+0.2256, Deflated=+0.2250, IR=0.55, Mono=0.69, p=0.0002, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.167 | 2016: +0.072 | 2017: +0.180 | 2018: +0.181 | 2019: +0.071 | 2020: +0.106 | 2021: +0.083 | 2022: +0.089 | 2023: +0.089 | 2024: +0.114 | 2025: +0.119 | 2026: -0.071
- Yearly Tail ICs:   2015: +0.297 | 2016: -0.007 | 2017: +0.254 | 2018: +0.410 | 2019: +0.164 | 2020: +0.167 | 2021: +0.237 | 2022: +0.273 | 2023: +0.236 | 2024: +0.283 | 2025: +0.080 | 2026: -0.282
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.74, Recency ratio=0.79
- Early IC=+0.1192, Recent IC=+0.0944, 1st-half IC=+0.1517, 2nd-half IC=+0.1123, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.182, Q2=-0.017, Q3_mid=+0.137, Q4=+0.138, Q5_high_vol=+0.185

**`combo_min__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0875, Sharpe=+0.4183)
- Admission: Train IC=+0.2527, Deflated=+0.2517, IR=0.68, Mono=0.75, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.072 | 2017: +0.179 | 2018: +0.138 | 2019: +0.079 | 2020: +0.100 | 2021: +0.073 | 2022: +0.084 | 2023: +0.086 | 2024: +0.123 | 2025: +0.136 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.347 | 2016: +0.082 | 2017: +0.347 | 2018: +0.214 | 2019: +0.264 | 2020: +0.305 | 2021: +0.243 | 2022: +0.148 | 2023: +0.237 | 2024: +0.332 | 2025: -0.061 | 2026: -0.117
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.69
- Early IC=+0.1254, Recent IC=+0.0865, 1st-half IC=+0.1411, 2nd-half IC=+0.0980, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.164, Q2=-0.036, Q3_mid=+0.165, Q4=+0.129, Q5_high_vol=+0.161

**`combo_rank_min__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0756, Sharpe=+0.4159)
- Admission: Train IC=+0.2867, Deflated=+0.2865, IR=0.88, Mono=0.79, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.271 | 2016: +0.085 | 2017: +0.205 | 2018: +0.250 | 2019: +0.155 | 2020: +0.120 | 2021: +0.089 | 2022: +0.055 | 2023: +0.059 | 2024: +0.109 | 2025: +0.100 | 2026: +0.005
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.168 | 2017: +0.351 | 2018: +0.314 | 2019: +0.237 | 2020: +0.201 | 2021: +0.357 | 2022: +0.284 | 2023: +0.165 | 2024: +0.165 | 2025: +0.070 | 2026: -0.178
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.59
- Early IC=+0.1770, Recent IC=+0.1051, 1st-half IC=+0.1954, 2nd-half IC=+0.1545, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.172, Q2=+0.057, Q3_mid=+0.146, Q4=+0.160, Q5_high_vol=+0.274

**`combo_max__max_up_ret__bar_ret_0`** (Lock IC=+0.0835, Sharpe=+0.4050)
- Admission: Train IC=+0.2323, Deflated=+0.2316, IR=0.77, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.131 | 2017: +0.166 | 2018: +0.256 | 2019: +0.127 | 2020: +0.097 | 2021: +0.151 | 2022: +0.082 | 2023: +0.078 | 2024: +0.145 | 2025: +0.092 | 2026: -0.069
- Yearly Tail ICs:   2015: +0.202 | 2016: +0.166 | 2017: +0.311 | 2018: +0.476 | 2019: +0.152 | 2020: +0.257 | 2021: +0.267 | 2022: +0.158 | 2023: +0.089 | 2024: +0.257 | 2025: -0.036 | 2026: -0.337
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.69
- Early IC=+0.1797, Recent IC=+0.1240, 1st-half IC=+0.1970, 2nd-half IC=+0.1557, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.036, Q3_mid=+0.172, Q4=+0.173, Q5_high_vol=+0.280

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.0836, Sharpe=+0.4050)
- Admission: Train IC=+0.2307, Deflated=+0.2300, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.131 | 2017: +0.166 | 2018: +0.256 | 2019: +0.127 | 2020: +0.097 | 2021: +0.151 | 2022: +0.082 | 2023: +0.079 | 2024: +0.145 | 2025: +0.092 | 2026: -0.070
- Yearly Tail ICs:   2015: +0.204 | 2016: +0.163 | 2017: +0.309 | 2018: +0.479 | 2019: +0.152 | 2020: +0.259 | 2021: +0.267 | 2022: +0.158 | 2023: +0.089 | 2024: +0.257 | 2025: -0.037 | 2026: -0.336
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.69
- Early IC=+0.1795, Recent IC=+0.1241, 1st-half IC=+0.1969, 2nd-half IC=+0.1557, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.035, Q3_mid=+0.172, Q4=+0.173, Q5_high_vol=+0.280

**`combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration`** (Lock IC=+0.0730, Sharpe=+0.4030)
- Admission: Train IC=+0.2072, Deflated=+0.2067, IR=0.75, Mono=0.77, p=0.0006, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.236 | 2016: -0.006 | 2017: +0.160 | 2018: +0.224 | 2019: +0.129 | 2020: +0.174 | 2021: +0.144 | 2022: +0.044 | 2023: +0.076 | 2024: +0.117 | 2025: +0.054 | 2026: +0.064
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.054 | 2017: +0.217 | 2018: +0.368 | 2019: +0.215 | 2020: +0.102 | 2021: +0.297 | 2022: +0.004 | 2023: +0.278 | 2024: +0.270 | 2025: -0.020 | 2026: +0.340
- IC CV=0.49, Neg years (linear/tail)=1/0 of 7, Half ratio=1.31, Recency ratio=1.38
- Early IC=+0.1153, Recent IC=+0.1587, 1st-half IC=+0.1330, 2nd-half IC=+0.1741, Neg regimes=0/5
- Weak component: `volume_weighted_momentum_acceleration` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.139, Q2=+0.090, Q3_mid=+0.135, Q4=+0.106, Q5_high_vol=+0.273

**`combo_rank_max__max_up_ret__close_vs_open_range`** (Lock IC=+0.0933, Sharpe=+0.3998)
- Admission: Train IC=+0.2359, Deflated=+0.2353, IR=0.84, Mono=0.77, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.251 | 2016: +0.098 | 2017: +0.216 | 2018: +0.206 | 2019: +0.101 | 2020: +0.143 | 2021: +0.092 | 2022: +0.116 | 2023: +0.095 | 2024: +0.131 | 2025: +0.078 | 2026: -0.032
- Yearly Tail ICs:   2015: +0.356 | 2016: +0.252 | 2017: +0.228 | 2018: +0.284 | 2019: +0.150 | 2020: +0.278 | 2021: +0.168 | 2022: +0.077 | 2023: +0.158 | 2024: +0.260 | 2025: -0.228 | 2026: -0.409
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.71, Recency ratio=0.67
- Early IC=+0.1767, Recent IC=+0.1179, 1st-half IC=+0.1951, 2nd-half IC=+0.1382, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.192, Q2=+0.022, Q3_mid=+0.179, Q4=+0.169, Q5_high_vol=+0.270

**`combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow`** (Lock IC=+0.0973, Sharpe=+0.3986)
- Admission: Train IC=+0.2596, Deflated=+0.2590, IR=0.78, Mono=0.77, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.070 | 2017: +0.178 | 2018: +0.195 | 2019: +0.135 | 2020: +0.141 | 2021: +0.137 | 2022: +0.086 | 2023: +0.127 | 2024: +0.146 | 2025: +0.111 | 2026: -0.055
- Yearly Tail ICs:   2015: +0.381 | 2016: +0.139 | 2017: +0.328 | 2018: +0.330 | 2019: +0.239 | 2020: +0.205 | 2021: +0.229 | 2022: +0.176 | 2023: +0.330 | 2024: +0.250 | 2025: -0.124 | 2026: -0.065
- IC CV=0.27, Neg years (linear/tail)=0/0 of 7, Half ratio=1.00, Recency ratio=1.07
- Early IC=+0.1296, Recent IC=+0.1390, 1st-half IC=+0.1585, 2nd-half IC=+0.1577, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.046, Q3_mid=+0.197, Q4=+0.131, Q5_high_vol=+0.214

**`combo_sig_product__max_up_ret__first_bar_return`** (Lock IC=+0.0882, Sharpe=+0.3945)
- Admission: Train IC=+0.1807, Deflated=+0.1807, IR=0.65, Mono=0.74, p=0.0014, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.095 | 2017: +0.119 | 2018: +0.269 | 2019: +0.091 | 2020: +0.143 | 2021: +0.101 | 2022: +0.120 | 2023: +0.051 | 2024: +0.098 | 2025: +0.103 | 2026: +0.008
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.022 | 2017: +0.317 | 2018: +0.451 | 2019: +0.109 | 2020: +0.215 | 2021: +0.192 | 2022: +0.080 | 2023: +0.085 | 2024: +0.175 | 2025: +0.148 | 2026: -0.308
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.82
- Early IC=+0.1498, Recent IC=+0.1221, 1st-half IC=+0.1849, 2nd-half IC=+0.1463, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.012, Q3_mid=+0.150, Q4=+0.179, Q5_high_vol=+0.226

**`combo_sig_product__max_up_ret__bar_ret_0`** (Lock IC=+0.0882, Sharpe=+0.3945)
- Admission: Train IC=+0.1805, Deflated=+0.1805, IR=0.65, Mono=0.74, p=0.0014, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.205 | 2016: +0.095 | 2017: +0.119 | 2018: +0.269 | 2019: +0.092 | 2020: +0.143 | 2021: +0.101 | 2022: +0.120 | 2023: +0.051 | 2024: +0.098 | 2025: +0.103 | 2026: +0.007
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.022 | 2017: +0.318 | 2018: +0.451 | 2019: +0.109 | 2020: +0.215 | 2021: +0.192 | 2022: +0.080 | 2023: +0.085 | 2024: +0.175 | 2025: +0.148 | 2026: -0.308
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.81
- Early IC=+0.1498, Recent IC=+0.1218, 1st-half IC=+0.1850, 2nd-half IC=+0.1463, Neg regimes=0/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.011, Q3_mid=+0.150, Q4=+0.179, Q5_high_vol=+0.226

**`combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1194, Sharpe=+0.3901)
- Admission: Train IC=+0.2231, Deflated=+0.2228, IR=0.54, Mono=0.66, p=0.0002, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.280 | 2016: +0.139 | 2017: +0.236 | 2018: +0.142 | 2019: +0.131 | 2020: +0.152 | 2021: +0.083 | 2022: +0.138 | 2023: +0.085 | 2024: +0.111 | 2025: +0.083 | 2026: +0.160
- Yearly Tail ICs:   2015: +0.206 | 2016: +0.233 | 2017: +0.089 | 2018: +0.095 | 2019: +0.251 | 2020: +0.054 | 2021: +0.128 | 2022: +0.159 | 2023: -0.042 | 2024: +0.142 | 2025: +0.101 | 2026: +0.231
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.57, Recency ratio=0.57
- Early IC=+0.2108, Recent IC=+0.1206, 1st-half IC=+0.2330, 2nd-half IC=+0.1335, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.211, Q2=+0.074, Q3_mid=+0.165, Q4=+0.144, Q5_high_vol=+0.288

**`max_up_ret`** (Lock IC=+0.0936, Sharpe=+0.3841)
- Admission: Train IC=+0.2500, Deflated=+0.2496, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.114 | 2017: +0.198 | 2018: +0.205 | 2019: +0.098 | 2020: +0.136 | 2021: +0.139 | 2022: +0.095 | 2023: +0.104 | 2024: +0.143 | 2025: +0.080 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.254 | 2016: +0.194 | 2017: +0.220 | 2018: +0.464 | 2019: +0.204 | 2020: +0.155 | 2021: +0.304 | 2022: +0.005 | 2023: +0.134 | 2024: +0.269 | 2025: -0.096 | 2026: -0.247
- IC CV=0.30, Neg years (linear/tail)=0/0 of 7, Half ratio=0.73, Recency ratio=0.78
- Early IC=+0.1762, Recent IC=+0.1371, 1st-half IC=+0.1974, 2nd-half IC=+0.1449, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.193, Q2=+0.070, Q3_mid=+0.189, Q4=+0.169, Q5_high_vol=+0.274

**`combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1059, Sharpe=+0.3801)
- Admission: Train IC=+0.2088, Deflated=+0.2083, IR=0.73, Mono=0.72, p=0.0006, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.159 | 2017: +0.184 | 2018: +0.186 | 2019: +0.101 | 2020: +0.128 | 2021: +0.085 | 2022: +0.113 | 2023: +0.074 | 2024: +0.111 | 2025: +0.079 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.088 | 2016: +0.273 | 2017: +0.254 | 2018: +0.244 | 2019: +0.109 | 2020: +0.125 | 2021: +0.185 | 2022: +0.099 | 2023: -0.084 | 2024: +0.011 | 2025: -0.013 | 2026: +0.214
- IC CV=0.28, Neg years (linear/tail)=0/0 of 7, Half ratio=0.62, Recency ratio=0.60
- Early IC=+0.1787, Recent IC=+0.1076, 1st-half IC=+0.2015, 2nd-half IC=+0.1250, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.160, Q2=+0.089, Q3_mid=+0.150, Q4=+0.106, Q5_high_vol=+0.252

**`combo_rank_min__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0947, Sharpe=+0.3764)
- Admission: Train IC=+0.3072, Deflated=+0.3068, IR=0.82, Mono=0.81, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.275 | 2016: +0.102 | 2017: +0.200 | 2018: +0.210 | 2019: +0.141 | 2020: +0.146 | 2021: +0.129 | 2022: +0.045 | 2023: +0.112 | 2024: +0.158 | 2025: +0.098 | 2026: -0.008
- Yearly Tail ICs:   2015: +0.503 | 2016: +0.293 | 2017: +0.257 | 2018: +0.337 | 2019: +0.215 | 2020: +0.184 | 2021: +0.339 | 2022: +0.100 | 2023: +0.140 | 2024: +0.207 | 2025: +0.026 | 2026: -0.084
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=0.87, Recency ratio=0.75
- Early IC=+0.1890, Recent IC=+0.1413, 1st-half IC=+0.1972, 2nd-half IC=+0.1711, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.188, Q2=+0.076, Q3_mid=+0.194, Q4=+0.141, Q5_high_vol=+0.288

**`combo_rank_max__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0973, Sharpe=+0.3763)
- Admission: Train IC=+0.2325, Deflated=+0.2313, IR=0.72, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.100 | 2017: +0.226 | 2018: +0.241 | 2019: +0.145 | 2020: +0.142 | 2021: +0.169 | 2022: +0.092 | 2023: +0.108 | 2024: +0.150 | 2025: +0.088 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.336 | 2016: -0.072 | 2017: +0.187 | 2018: +0.368 | 2019: +0.218 | 2020: +0.248 | 2021: +0.353 | 2022: +0.155 | 2023: +0.156 | 2024: +0.280 | 2025: -0.017 | 2026: -0.111
- IC CV=0.30, Neg years (linear/tail)=0/1 of 7, Half ratio=0.89, Recency ratio=0.88
- Early IC=+0.1778, Recent IC=+0.1565, 1st-half IC=+0.1998, 2nd-half IC=+0.1773, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.225, Q2=+0.056, Q3_mid=+0.189, Q4=+0.150, Q5_high_vol=+0.274

**`combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0832, Sharpe=+0.3757)
- Admission: Train IC=+0.2343, Deflated=+0.2332, IR=0.81, Mono=0.79, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.241 | 2016: +0.080 | 2017: +0.240 | 2018: +0.175 | 2019: +0.067 | 2020: +0.154 | 2021: +0.108 | 2022: +0.108 | 2023: +0.090 | 2024: +0.131 | 2025: +0.068 | 2026: -0.065
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.269 | 2017: +0.245 | 2018: +0.211 | 2019: +0.106 | 2020: +0.196 | 2021: +0.227 | 2022: +0.121 | 2023: +0.082 | 2024: +0.253 | 2025: -0.128 | 2026: -0.320
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.66, Recency ratio=0.82
- Early IC=+0.1606, Recent IC=+0.1313, 1st-half IC=+0.1993, 2nd-half IC=+0.1319, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.026, Q3_mid=+0.166, Q4=+0.165, Q5_high_vol=+0.260

**`combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0715, Sharpe=+0.3735)
- Admission: Train IC=+0.2977, Deflated=+0.2979, IR=0.75, Mono=0.78, p=0.0000, MaxCorr=0.77
- Yearly Linear ICs: 2015: +0.210 | 2016: +0.049 | 2017: +0.164 | 2018: +0.182 | 2019: +0.150 | 2020: +0.194 | 2021: +0.148 | 2022: +0.006 | 2023: +0.114 | 2024: +0.089 | 2025: +0.071 | 2026: +0.053
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.115 | 2017: +0.110 | 2018: +0.412 | 2019: +0.301 | 2020: +0.248 | 2021: +0.420 | 2022: +0.228 | 2023: +0.081 | 2024: -0.121 | 2025: +0.098 | 2026: +0.457
- IC CV=0.31, Neg years (linear/tail)=0/0 of 7, Half ratio=1.42, Recency ratio=1.32
- Early IC=+0.1292, Recent IC=+0.1708, 1st-half IC=+0.1350, 2nd-half IC=+0.1914, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.166, Q2=+0.092, Q3_mid=+0.144, Q4=+0.092, Q5_high_vol=+0.272

**`combo_ratio__max_down_ret__volume_weighted_momentum_acceleration`** (Lock IC=+0.0837, Sharpe=+0.3731)
- Admission: Train IC=+0.2642, Deflated=+0.2624, IR=0.92, Mono=0.82, p=0.0000, MaxCorr=0.24
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.097 | 2017: +0.194 | 2018: +0.158 | 2019: +0.077 | 2020: +0.168 | 2021: +0.052 | 2022: +0.096 | 2023: +0.046 | 2024: +0.073 | 2025: +0.148 | 2026: +0.040
- Yearly Tail ICs:   2015: +0.405 | 2016: +0.229 | 2017: +0.386 | 2018: +0.332 | 2019: +0.207 | 2020: +0.271 | 2021: +0.214 | 2022: -0.027 | 2023: +0.087 | 2024: +0.035 | 2025: +0.246 | 2026: +0.214
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.56
- Early IC=+0.1961, Recent IC=+0.1099, 1st-half IC=+0.1766, 2nd-half IC=+0.1186, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.152, Q2=+0.040, Q3_mid=+0.111, Q4=+0.129, Q5_high_vol=+0.273

**`combo_rank_max__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0860, Sharpe=+0.3731)
- Admission: Train IC=+0.2204, Deflated=+0.2200, IR=0.40, Mono=0.66, p=0.0004, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.224 | 2016: +0.074 | 2017: +0.082 | 2018: +0.191 | 2019: +0.135 | 2020: +0.078 | 2021: +0.098 | 2022: +0.095 | 2023: +0.050 | 2024: +0.099 | 2025: +0.062 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.148 | 2016: +0.058 | 2017: +0.028 | 2018: +0.300 | 2019: +0.187 | 2020: +0.032 | 2021: +0.061 | 2022: +0.153 | 2023: +0.057 | 2024: +0.155 | 2025: +0.062 | 2026: +0.064
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=0.95, Recency ratio=0.59
- Early IC=+0.1492, Recent IC=+0.0880, 1st-half IC=+0.1324, 2nd-half IC=+0.1257, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.120, Q2=+0.005, Q3_mid=+0.156, Q4=+0.128, Q5_high_vol=+0.198

**`combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio`** (Lock IC=+0.1102, Sharpe=+0.3729)
- Admission: Train IC=+0.2634, Deflated=+0.2630, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.295 | 2016: +0.137 | 2017: +0.227 | 2018: +0.162 | 2019: +0.120 | 2020: +0.188 | 2021: +0.092 | 2022: +0.118 | 2023: +0.075 | 2024: +0.109 | 2025: +0.082 | 2026: +0.138
- Yearly Tail ICs:   2015: +0.188 | 2016: +0.378 | 2017: +0.062 | 2018: +0.154 | 2019: +0.261 | 2020: +0.145 | 2021: +0.158 | 2022: +0.031 | 2023: -0.110 | 2024: +0.095 | 2025: +0.041 | 2026: +0.170
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.65
- Early IC=+0.2159, Recent IC=+0.1399, 1st-half IC=+0.2319, 2nd-half IC=+0.1469, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.202, Q2=+0.075, Q3_mid=+0.161, Q4=+0.138, Q5_high_vol=+0.307

**`combo_sig_product__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0707, Sharpe=+0.3691)
- Admission: Train IC=+0.1927, Deflated=+0.1931, IR=0.46, Mono=0.69, p=0.0010, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.131 | 2017: +0.079 | 2018: +0.166 | 2019: +0.094 | 2020: +0.138 | 2021: +0.079 | 2022: +0.096 | 2023: +0.070 | 2024: +0.088 | 2025: +0.081 | 2026: -0.019
- Yearly Tail ICs:   2015: +0.421 | 2016: +0.068 | 2017: +0.093 | 2018: +0.175 | 2019: +0.191 | 2020: +0.223 | 2021: +0.013 | 2022: +0.158 | 2023: +0.214 | 2024: +0.140 | 2025: +0.068 | 2026: -0.041
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.88, Recency ratio=0.60
- Early IC=+0.1790, Recent IC=+0.1083, 1st-half IC=+0.1463, 2nd-half IC=+0.1282, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.089, Q2=+0.050, Q3_mid=+0.169, Q4=+0.111, Q5_high_vol=+0.225

**`combo_mean__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0859, Sharpe=+0.3654)
- Admission: Train IC=+0.2597, Deflated=+0.2588, IR=0.80, Mono=0.77, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.064 | 2017: +0.180 | 2018: +0.162 | 2019: +0.050 | 2020: +0.122 | 2021: +0.069 | 2022: +0.108 | 2023: +0.112 | 2024: +0.114 | 2025: +0.116 | 2026: -0.105
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.270 | 2017: +0.363 | 2018: +0.314 | 2019: +0.048 | 2020: +0.205 | 2021: +0.197 | 2022: +0.128 | 2023: +0.194 | 2024: +0.256 | 2025: -0.067 | 2026: -0.248
- IC CV=0.45, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.78
- Early IC=+0.1222, Recent IC=+0.0957, 1st-half IC=+0.1622, 2nd-half IC=+0.1047, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.165, Q2=+0.000, Q3_mid=+0.155, Q4=+0.137, Q5_high_vol=+0.195

**`combo_max__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0935, Sharpe=+0.3629)
- Admission: Train IC=+0.2581, Deflated=+0.2574, IR=0.69, Mono=0.77, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.262 | 2016: +0.095 | 2017: +0.231 | 2018: +0.216 | 2019: +0.109 | 2020: +0.175 | 2021: +0.156 | 2022: +0.100 | 2023: +0.089 | 2024: +0.151 | 2025: +0.074 | 2026: -0.023
- Yearly Tail ICs:   2015: +0.216 | 2016: +0.222 | 2017: +0.090 | 2018: +0.418 | 2019: +0.257 | 2020: +0.139 | 2021: +0.352 | 2022: +0.118 | 2023: -0.012 | 2024: +0.269 | 2025: +0.024 | 2026: -0.296
- IC CV=0.33, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.93
- Early IC=+0.1787, Recent IC=+0.1655, 1st-half IC=+0.2128, 2nd-half IC=+0.1688, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.213, Q2=+0.078, Q3_mid=+0.178, Q4=+0.179, Q5_high_vol=+0.288

**`combo_mean__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0870, Sharpe=+0.3502)
- Admission: Train IC=+0.2305, Deflated=+0.2298, IR=0.58, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.301 | 2016: +0.035 | 2017: +0.230 | 2018: +0.096 | 2019: +0.111 | 2020: +0.112 | 2021: +0.045 | 2022: +0.060 | 2023: +0.040 | 2024: +0.101 | 2025: +0.097 | 2026: +0.121
- Yearly Tail ICs:   2015: +0.283 | 2016: +0.155 | 2017: +0.179 | 2018: +0.256 | 2019: +0.332 | 2020: +0.234 | 2021: +0.139 | 2022: +0.071 | 2023: +0.017 | 2024: +0.244 | 2025: -0.031 | 2026: +0.271
- IC CV=0.68, Neg years (linear/tail)=0/0 of 7, Half ratio=0.51, Recency ratio=0.47
- Early IC=+0.1684, Recent IC=+0.0787, 1st-half IC=+0.1898, 2nd-half IC=+0.0964, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.031, Q3_mid=+0.087, Q4=+0.097, Q5_high_vol=+0.227

**`combo_mean__net_volume_flow__max_down_ret`** (Lock IC=+0.0939, Sharpe=+0.3484)
- Admission: Train IC=+0.1947, Deflated=+0.1940, IR=0.58, Mono=0.71, p=0.0008, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.074 | 2017: +0.188 | 2018: +0.155 | 2019: +0.099 | 2020: +0.118 | 2021: +0.078 | 2022: +0.092 | 2023: +0.076 | 2024: +0.134 | 2025: +0.130 | 2026: -0.011
- Yearly Tail ICs:   2015: +0.298 | 2016: +0.051 | 2017: +0.167 | 2018: +0.157 | 2019: +0.192 | 2020: +0.096 | 2021: +0.297 | 2022: +0.325 | 2023: +0.341 | 2024: +0.329 | 2025: +0.021 | 2026: -0.124
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.80, Recency ratio=0.64
- Early IC=+0.1519, Recent IC=+0.0977, 1st-half IC=+0.1508, 2nd-half IC=+0.1203, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.184, Q2=-0.014, Q3_mid=+0.152, Q4=+0.112, Q5_high_vol=+0.211

**`combo_min__trend_day_regime_conviction__close_vs_open_range`** (Lock IC=+0.0876, Sharpe=+0.3352)
- Admission: Train IC=+0.2422, Deflated=+0.2411, IR=0.51, Mono=0.70, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.069 | 2017: +0.203 | 2018: +0.124 | 2019: +0.062 | 2020: +0.100 | 2021: +0.054 | 2022: +0.094 | 2023: +0.080 | 2024: +0.115 | 2025: +0.136 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.299 | 2016: +0.178 | 2017: +0.341 | 2018: +0.236 | 2019: +0.203 | 2020: +0.113 | 2021: +0.192 | 2022: +0.149 | 2023: +0.116 | 2024: +0.267 | 2025: -0.078 | 2026: -0.008
- IC CV=0.48, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.62
- Early IC=+0.1234, Recent IC=+0.0771, 1st-half IC=+0.1417, 2nd-half IC=+0.0890, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.025, Q3_mid=+0.128, Q4=+0.135, Q5_high_vol=+0.142

**`combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early`** (Lock IC=+0.0677, Sharpe=+0.3299)
- Admission: Train IC=+0.1732, Deflated=+0.1723, IR=0.47, Mono=0.66, p=0.0016, MaxCorr=0.67
- Yearly Linear ICs: 2015: +0.146 | 2016: -0.049 | 2017: +0.116 | 2018: +0.052 | 2019: +0.111 | 2020: +0.099 | 2021: +0.059 | 2022: +0.031 | 2023: +0.014 | 2024: +0.206 | 2025: +0.045 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.366 | 2016: -0.072 | 2017: +0.120 | 2018: +0.289 | 2019: +0.301 | 2020: +0.036 | 2021: +0.277 | 2022: +0.172 | 2023: +0.004 | 2024: +0.350 | 2025: +0.081 | 2026: -0.170
- IC CV=0.78, Neg years (linear/tail)=1/1 of 7, Half ratio=0.96, Recency ratio=1.62
- Early IC=+0.0484, Recent IC=+0.0785, 1st-half IC=+0.0774, 2nd-half IC=+0.0742, Neg regimes=0/5
- Weak component: `double_bottom_bull_flag_early` (CV=0.69)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.082, Q3_mid=+0.074, Q4=+0.067, Q5_high_vol=+0.139

**`combo_rank_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0854, Sharpe=+0.3219)
- Admission: Train IC=+0.2631, Deflated=+0.2626, IR=0.83, Mono=0.77, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.273 | 2016: +0.048 | 2017: +0.233 | 2018: +0.113 | 2019: +0.122 | 2020: +0.121 | 2021: +0.073 | 2022: +0.056 | 2023: +0.064 | 2024: +0.085 | 2025: +0.133 | 2026: +0.084
- Yearly Tail ICs:   2015: +0.279 | 2016: +0.111 | 2017: +0.267 | 2018: +0.360 | 2019: +0.324 | 2020: +0.217 | 2021: +0.340 | 2022: +0.063 | 2023: +0.041 | 2024: +0.147 | 2025: +0.082 | 2026: +0.223
- IC CV=0.54, Neg years (linear/tail)=0/0 of 7, Half ratio=0.68, Recency ratio=0.61
- Early IC=+0.1604, Recent IC=+0.0973, 1st-half IC=+0.1623, 2nd-half IC=+0.1104, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.180, Q2=+0.024, Q3_mid=+0.081, Q4=+0.129, Q5_high_vol=+0.201

**`combo_rank_min__bar_ret_0__max_down_ret`** (Lock IC=+0.0693, Sharpe=+0.3200)
- Admission: Train IC=+0.2174, Deflated=+0.2166, IR=0.52, Mono=0.67, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.274 | 2016: +0.098 | 2017: +0.201 | 2018: +0.164 | 2019: +0.130 | 2020: +0.098 | 2021: +0.071 | 2022: +0.027 | 2023: +0.056 | 2024: +0.103 | 2025: +0.123 | 2026: +0.006
- Yearly Tail ICs:   2015: +0.344 | 2016: -0.075 | 2017: +0.320 | 2018: +0.225 | 2019: +0.326 | 2020: +0.179 | 2021: +0.349 | 2022: +0.131 | 2023: +0.073 | 2024: +0.220 | 2025: +0.160 | 2026: -0.097
- IC CV=0.44, Neg years (linear/tail)=0/1 of 7, Half ratio=0.74, Recency ratio=0.45
- Early IC=+0.1877, Recent IC=+0.0842, 1st-half IC=+0.1664, 2nd-half IC=+0.1232, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.176, Q2=-0.000, Q3_mid=+0.120, Q4=+0.092, Q5_high_vol=+0.242

**`combo_max__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0932, Sharpe=+0.3174)
- Admission: Train IC=+0.2305, Deflated=+0.2301, IR=0.56, Mono=0.76, p=0.0000, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.284 | 2016: +0.072 | 2017: +0.251 | 2018: +0.192 | 2019: +0.132 | 2020: +0.161 | 2021: +0.095 | 2022: +0.082 | 2023: +0.078 | 2024: +0.136 | 2025: +0.102 | 2026: +0.004
- Yearly Tail ICs:   2015: +0.441 | 2016: +0.069 | 2017: +0.150 | 2018: +0.141 | 2019: +0.264 | 2020: +0.040 | 2021: +0.349 | 2022: +0.217 | 2023: +0.103 | 2024: +0.097 | 2025: +0.161 | 2026: -0.044
- IC CV=0.43, Neg years (linear/tail)=0/0 of 7, Half ratio=0.86, Recency ratio=0.72
- Early IC=+0.1780, Recent IC=+0.1279, 1st-half IC=+0.1834, 2nd-half IC=+0.1579, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.235, Q2=+0.021, Q3_mid=+0.147, Q4=+0.125, Q5_high_vol=+0.278

**`combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1001, Sharpe=+0.3137)
- Admission: Train IC=+0.2115, Deflated=+0.2110, IR=0.63, Mono=0.72, p=0.0006, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.114 | 2017: +0.227 | 2018: +0.202 | 2019: +0.106 | 2020: +0.162 | 2021: +0.097 | 2022: +0.128 | 2023: +0.065 | 2024: +0.087 | 2025: +0.077 | 2026: +0.097
- Yearly Tail ICs:   2015: +0.114 | 2016: +0.312 | 2017: +0.049 | 2018: +0.345 | 2019: +0.149 | 2020: +0.092 | 2021: +0.213 | 2022: +0.148 | 2023: -0.121 | 2024: +0.052 | 2025: -0.028 | 2026: -0.048
- IC CV=0.37, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.67
- Early IC=+0.1921, Recent IC=+0.1293, 1st-half IC=+0.2263, 2nd-half IC=+0.1455, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.208, Q2=+0.079, Q3_mid=+0.174, Q4=+0.145, Q5_high_vol=+0.302

**`combo_rel_diff__max_up_ret__late_bar_momentum`** (Lock IC=+0.0722, Sharpe=+0.3118)
- Admission: Train IC=+0.2752, Deflated=+0.2746, IR=0.98, Mono=0.78, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.336 | 2016: +0.119 | 2017: +0.177 | 2018: +0.206 | 2019: +0.121 | 2020: +0.138 | 2021: +0.144 | 2022: +0.049 | 2023: +0.082 | 2024: +0.083 | 2025: +0.036 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.286 | 2016: +0.142 | 2017: +0.392 | 2018: +0.361 | 2019: +0.339 | 2020: +0.100 | 2021: +0.206 | 2022: +0.075 | 2023: +0.146 | 2024: -0.043 | 2025: -0.057 | 2026: +0.113
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.76, Recency ratio=0.62
- Early IC=+0.2276, Recent IC=+0.1410, 1st-half IC=+0.2151, 2nd-half IC=+0.1630, Neg regimes=0/5
- Weak component: `late_bar_momentum` (CV=0.56)
- Regime ICs: Q1_low_vol=+0.145, Q2=+0.089, Q3_mid=+0.187, Q4=+0.149, Q5_high_vol=+0.317

**`combo_min__close_vs_open_range__high_low_sequence_momentum`** (Lock IC=+0.0897, Sharpe=+0.3070)
- Admission: Train IC=+0.2399, Deflated=+0.2387, IR=0.58, Mono=0.71, p=0.0000, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.178 | 2016: +0.067 | 2017: +0.201 | 2018: +0.123 | 2019: +0.060 | 2020: +0.099 | 2021: +0.048 | 2022: +0.097 | 2023: +0.079 | 2024: +0.121 | 2025: +0.136 | 2026: -0.073
- Yearly Tail ICs:   2015: +0.309 | 2016: +0.177 | 2017: +0.336 | 2018: +0.237 | 2019: +0.180 | 2020: +0.178 | 2021: +0.170 | 2022: +0.161 | 2023: +0.109 | 2024: +0.291 | 2025: -0.102 | 2026: +0.006
- IC CV=0.50, Neg years (linear/tail)=0/0 of 7, Half ratio=0.61, Recency ratio=0.60
- Early IC=+0.1227, Recent IC=+0.0736, 1st-half IC=+0.1410, 2nd-half IC=+0.0864, Neg regimes=1/5
- Weak component: `high_low_sequence_momentum` (CV=0.50)
- Regime ICs: Q1_low_vol=+0.177, Q2=-0.024, Q3_mid=+0.126, Q4=+0.134, Q5_high_vol=+0.139

**`combo_sig_product__max_up_ret__close_vs_open_range`** (Lock IC=+0.1164, Sharpe=+0.3005)
- Admission: Train IC=+0.2835, Deflated=+0.2832, IR=0.84, Mono=0.76, p=0.0000, MaxCorr=0.65
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.153 | 2017: +0.085 | 2018: +0.126 | 2019: +0.079 | 2020: +0.129 | 2021: +0.109 | 2022: +0.116 | 2023: +0.155 | 2024: +0.130 | 2025: +0.127 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.418 | 2016: +0.234 | 2017: +0.381 | 2018: +0.247 | 2019: +0.217 | 2020: +0.135 | 2021: +0.271 | 2022: +0.127 | 2023: +0.084 | 2024: +0.255 | 2025: -0.001 | 2026: +0.008
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=0.69, Recency ratio=0.56
- Early IC=+0.2113, Recent IC=+0.1192, 1st-half IC=+0.1761, 2nd-half IC=+0.1221, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.107, Q2=+0.061, Q3_mid=+0.134, Q4=+0.182, Q5_high_vol=+0.247

**`combo_sig_product__opening_drive_thrust_ratio__max_down_ret`** (Lock IC=+0.0923, Sharpe=+0.2989)
- Admission: Train IC=+0.1596, Deflated=+0.1592, IR=0.53, Mono=0.69, p=0.0044, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.270 | 2016: +0.041 | 2017: +0.223 | 2018: +0.164 | 2019: +0.132 | 2020: +0.199 | 2021: +0.126 | 2022: +0.040 | 2023: +0.106 | 2024: +0.115 | 2025: +0.141 | 2026: +0.036
- Yearly Tail ICs:   2015: +0.214 | 2016: -0.045 | 2017: +0.194 | 2018: +0.096 | 2019: +0.271 | 2020: +0.060 | 2021: +0.355 | 2022: -0.023 | 2023: +0.155 | 2024: +0.284 | 2025: +0.253 | 2026: -0.059
- IC CV=0.42, Neg years (linear/tail)=0/1 of 7, Half ratio=1.01, Recency ratio=1.05
- Early IC=+0.1551, Recent IC=+0.1624, 1st-half IC=+0.1662, 2nd-half IC=+0.1684, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.071, Q3_mid=+0.184, Q4=+0.135, Q5_high_vol=+0.232

**`combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1096, Sharpe=+0.2938)
- Admission: Train IC=+0.2298, Deflated=+0.2291, IR=0.52, Mono=0.72, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.313 | 2016: +0.098 | 2017: +0.234 | 2018: +0.157 | 2019: +0.132 | 2020: +0.173 | 2021: +0.075 | 2022: +0.120 | 2023: +0.073 | 2024: +0.102 | 2025: +0.091 | 2026: +0.112
- Yearly Tail ICs:   2015: +0.225 | 2016: +0.141 | 2017: +0.112 | 2018: +0.136 | 2019: +0.267 | 2020: +0.159 | 2021: +0.154 | 2022: +0.113 | 2023: -0.050 | 2024: -0.055 | 2025: +0.090 | 2026: +0.197
- IC CV=0.45, Neg years (linear/tail)=0/0 of 7, Half ratio=0.65, Recency ratio=0.60
- Early IC=+0.2058, Recent IC=+0.1243, 1st-half IC=+0.2223, 2nd-half IC=+0.1451, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.218, Q2=+0.068, Q3_mid=+0.156, Q4=+0.114, Q5_high_vol=+0.299

**`combo_mean__first_bar_sentiment__early_body_momentum`** (Lock IC=+0.0870, Sharpe=+0.2911)
- Admission: Train IC=+0.2207, Deflated=+0.2199, IR=0.56, Mono=0.75, p=0.0004, MaxCorr=0.99
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.105 | 2017: +0.127 | 2018: +0.185 | 2019: +0.081 | 2020: +0.102 | 2021: +0.093 | 2022: +0.118 | 2023: +0.075 | 2024: +0.116 | 2025: +0.126 | 2026: -0.061
- Yearly Tail ICs:   2015: +0.417 | 2016: +0.146 | 2017: +0.117 | 2018: +0.232 | 2019: +0.159 | 2020: +0.244 | 2021: +0.142 | 2022: +0.211 | 2023: +0.215 | 2024: +0.162 | 2025: +0.111 | 2026: -0.122
- IC CV=0.32, Neg years (linear/tail)=0/0 of 7, Half ratio=0.75, Recency ratio=0.66
- Early IC=+0.1475, Recent IC=+0.0974, 1st-half IC=+0.1512, 2nd-half IC=+0.1138, Neg regimes=1/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.163, Q2=-0.010, Q3_mid=+0.173, Q4=+0.139, Q5_high_vol=+0.181

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure`** (Lock IC=+0.0925, Sharpe=+0.2876)
- Admission: Train IC=+0.2940, Deflated=+0.2932, IR=0.78, Mono=0.80, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.268 | 2016: +0.099 | 2017: +0.227 | 2018: +0.194 | 2019: +0.097 | 2020: +0.121 | 2021: +0.120 | 2022: +0.104 | 2023: +0.069 | 2024: +0.129 | 2025: +0.092 | 2026: -0.009
- Yearly Tail ICs:   2015: +0.534 | 2016: +0.286 | 2017: +0.261 | 2018: +0.260 | 2019: +0.174 | 2020: +0.171 | 2021: +0.333 | 2022: +0.057 | 2023: +0.178 | 2024: +0.261 | 2025: +0.022 | 2026: -0.078
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.66
- Early IC=+0.1832, Recent IC=+0.1203, 1st-half IC=+0.2029, 2nd-half IC=+0.1357, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.175, Q2=+0.076, Q3_mid=+0.184, Q4=+0.156, Q5_high_vol=+0.284

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0791, Sharpe=+0.2865)
- Admission: Train IC=+0.2907, Deflated=+0.2900, IR=0.87, Mono=0.80, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.310 | 2016: +0.110 | 2017: +0.179 | 2018: +0.192 | 2019: +0.131 | 2020: +0.145 | 2021: +0.107 | 2022: +0.070 | 2023: +0.050 | 2024: +0.071 | 2025: +0.119 | 2026: +0.071
- Yearly Tail ICs:   2015: +0.287 | 2016: +0.189 | 2017: +0.308 | 2018: +0.415 | 2019: +0.225 | 2020: +0.266 | 2021: -0.073 | 2022: +0.022 | 2023: -0.063 | 2024: +0.158 | 2025: -0.023 | 2026: +0.152
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.63, Recency ratio=0.60
- Early IC=+0.2098, Recent IC=+0.1262, 1st-half IC=+0.2236, 2nd-half IC=+0.1399, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.048, Q3_mid=+0.151, Q4=+0.192, Q5_high_vol=+0.247

**`combo_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1046, Sharpe=+0.2850)
- Admission: Train IC=+0.1951, Deflated=+0.1946, IR=0.73, Mono=0.72, p=0.0008, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.228 | 2016: +0.113 | 2017: +0.202 | 2018: +0.196 | 2019: +0.109 | 2020: +0.127 | 2021: +0.063 | 2022: +0.119 | 2023: +0.071 | 2024: +0.104 | 2025: +0.079 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.122 | 2016: +0.149 | 2017: +0.224 | 2018: +0.262 | 2019: +0.089 | 2020: +0.192 | 2021: +0.231 | 2022: +0.124 | 2023: -0.047 | 2024: +0.024 | 2025: -0.037 | 2026: +0.117
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=0.62, Recency ratio=0.56
- Early IC=+0.1705, Recent IC=+0.0949, 1st-half IC=+0.2007, 2nd-half IC=+0.1243, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.089, Q3_mid=+0.152, Q4=+0.090, Q5_high_vol=+0.242

**`combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression`** (Lock IC=+0.1051, Sharpe=+0.2757)
- Admission: Train IC=+0.3133, Deflated=+0.3127, IR=0.95, Mono=0.82, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.115 | 2017: +0.227 | 2018: +0.194 | 2019: +0.094 | 2020: +0.144 | 2021: +0.122 | 2022: +0.128 | 2023: +0.096 | 2024: +0.139 | 2025: +0.113 | 2026: -0.044
- Yearly Tail ICs:   2015: +0.523 | 2016: +0.354 | 2017: +0.246 | 2018: +0.315 | 2019: +0.176 | 2020: +0.243 | 2021: +0.373 | 2022: +0.041 | 2023: +0.160 | 2024: +0.183 | 2025: +0.093 | 2026: -0.306
- IC CV=0.34, Neg years (linear/tail)=0/0 of 7, Half ratio=0.70, Recency ratio=0.73
- Early IC=+0.1814, Recent IC=+0.1331, 1st-half IC=+0.2022, 2nd-half IC=+0.1426, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.196, Q2=+0.065, Q3_mid=+0.181, Q4=+0.172, Q5_high_vol=+0.269

**`combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment`** (Lock IC=+0.0830, Sharpe=+0.2706)
- Admission: Train IC=+0.2403, Deflated=+0.2401, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.79
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.097 | 2017: +0.076 | 2018: +0.194 | 2019: +0.122 | 2020: +0.077 | 2021: +0.108 | 2022: +0.090 | 2023: +0.041 | 2024: +0.093 | 2025: +0.073 | 2026: +0.078
- Yearly Tail ICs:   2015: +0.095 | 2016: +0.146 | 2017: -0.000 | 2018: +0.365 | 2019: +0.182 | 2020: +0.036 | 2021: +0.096 | 2022: +0.106 | 2023: -0.010 | 2024: +0.109 | 2025: +0.081 | 2026: -0.034
- IC CV=0.40, Neg years (linear/tail)=0/1 of 7, Half ratio=0.91, Recency ratio=0.60
- Early IC=+0.1538, Recent IC=+0.0926, 1st-half IC=+0.1360, 2nd-half IC=+0.1238, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.44)
- Regime ICs: Q1_low_vol=+0.126, Q2=+0.007, Q3_mid=+0.155, Q4=+0.137, Q5_high_vol=+0.199

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=+0.0926, Sharpe=+0.2677)
- Admission: Train IC=+0.2284, Deflated=+0.2276, IR=0.83, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.225 | 2016: +0.141 | 2017: +0.163 | 2018: +0.234 | 2019: +0.121 | 2020: +0.106 | 2021: +0.163 | 2022: +0.087 | 2023: +0.093 | 2024: +0.161 | 2025: +0.100 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.213 | 2016: +0.135 | 2017: +0.302 | 2018: +0.469 | 2019: +0.162 | 2020: +0.241 | 2021: +0.318 | 2022: +0.208 | 2023: +0.100 | 2024: +0.285 | 2025: +0.012 | 2026: -0.328
- IC CV=0.27, Neg years (linear/tail)=0/0 of 7, Half ratio=0.79, Recency ratio=0.75
- Early IC=+0.1845, Recent IC=+0.1379, 1st-half IC=+0.1965, 2nd-half IC=+0.1547, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.190, Q2=+0.044, Q3_mid=+0.174, Q4=+0.174, Q5_high_vol=+0.278

**`combo_sig_product__net_volume_flow__close_vs_open_range`** (Lock IC=+0.0872, Sharpe=+0.2512)
- Admission: Train IC=+0.2210, Deflated=+0.2199, IR=0.59, Mono=0.73, p=0.0004, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.181 | 2016: +0.069 | 2017: +0.209 | 2018: +0.099 | 2019: +0.063 | 2020: +0.098 | 2021: +0.062 | 2022: +0.085 | 2023: +0.096 | 2024: +0.112 | 2025: +0.128 | 2026: -0.064
- Yearly Tail ICs:   2015: +0.313 | 2016: +0.126 | 2017: +0.361 | 2018: +0.216 | 2019: +0.087 | 2020: +0.117 | 2021: +0.240 | 2022: +0.136 | 2023: +0.059 | 2024: +0.255 | 2025: -0.009 | 2026: +0.006
- IC CV=0.50, Neg years (linear/tail)=0/0 of 7, Half ratio=0.60, Recency ratio=0.64
- Early IC=+0.1248, Recent IC=+0.0798, 1st-half IC=+0.1414, 2nd-half IC=+0.0854, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.181, Q2=-0.041, Q3_mid=+0.150, Q4=+0.132, Q5_high_vol=+0.136

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0932, Sharpe=+0.2495)
- Admission: Train IC=+0.2011, Deflated=+0.2008, IR=0.54, Mono=0.69, p=0.0006, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.121 | 2017: +0.220 | 2018: +0.197 | 2019: +0.092 | 2020: +0.125 | 2021: +0.044 | 2022: +0.113 | 2023: +0.060 | 2024: +0.078 | 2025: +0.086 | 2026: +0.094
- Yearly Tail ICs:   2015: +0.136 | 2016: +0.326 | 2017: +0.180 | 2018: +0.327 | 2019: +0.042 | 2020: +0.106 | 2021: +0.148 | 2022: +0.143 | 2023: +0.014 | 2024: +0.120 | 2025: -0.103 | 2026: -0.070
- IC CV=0.46, Neg years (linear/tail)=0/0 of 7, Half ratio=0.55, Recency ratio=0.45
- Early IC=+0.1871, Recent IC=+0.0845, 1st-half IC=+0.2118, 2nd-half IC=+0.1166, Neg regimes=0/5
- Weak component: `volatility_expansion_trend_vector` (CV=0.43)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.017, Q3_mid=+0.183, Q4=+0.122, Q5_high_vol=+0.286

**`rbreaker_sell_setup_proximity_early`** (Lock IC=+0.1110, Sharpe=+0.2443)
- Admission: Train IC=+0.2832, Deflated=+0.2831, IR=0.67, Mono=0.73, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.245 | 2016: +0.138 | 2017: +0.226 | 2018: +0.116 | 2019: +0.121 | 2020: +0.123 | 2021: +0.067 | 2022: +0.092 | 2023: +0.079 | 2024: +0.089 | 2025: +0.095 | 2026: +0.184
- Yearly Tail ICs:   2015: +0.131 | 2016: +0.323 | 2017: +0.179 | 2018: +0.315 | 2019: +0.188 | 2020: +0.216 | 2021: +0.069 | 2022: -0.095 | 2023: -0.115 | 2024: +0.110 | 2025: -0.186 | 2026: +0.471
- IC CV=0.40, Neg years (linear/tail)=0/0 of 7, Half ratio=0.47, Recency ratio=0.49
- Early IC=+0.1914, Recent IC=+0.0947, 1st-half IC=+0.2179, 2nd-half IC=+0.1023, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.167, Q2=+0.086, Q3_mid=+0.104, Q4=+0.150, Q5_high_vol=+0.225

**`combo_min__star50_limit_proximity_early__max_down_ret`** (Lock IC=+0.0939, Sharpe=+0.2138)
- Admission: Train IC=+0.2591, Deflated=+0.2586, IR=0.78, Mono=0.76, p=0.0000, MaxCorr=0.80
- Yearly Linear ICs: 2015: +0.282 | 2016: +0.043 | 2017: +0.232 | 2018: +0.105 | 2019: +0.114 | 2020: +0.101 | 2021: +0.072 | 2022: +0.082 | 2023: +0.077 | 2024: +0.080 | 2025: +0.146 | 2026: +0.089
- Yearly Tail ICs:   2015: +0.320 | 2016: +0.101 | 2017: +0.263 | 2018: +0.348 | 2019: +0.296 | 2020: +0.189 | 2021: +0.237 | 2022: +0.115 | 2023: +0.034 | 2024: +0.143 | 2025: +0.075 | 2026: +0.194
- IC CV=0.60, Neg years (linear/tail)=0/0 of 7, Half ratio=0.58, Recency ratio=0.53
- Early IC=+0.1627, Recent IC=+0.0861, 1st-half IC=+0.1693, 2nd-half IC=+0.0982, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.182, Q2=+0.033, Q3_mid=+0.080, Q4=+0.108, Q5_high_vol=+0.203

**`vwap_trend_channel_slope`** (Lock IC=+0.0822, Sharpe=+0.2133)
- Admission: Train IC=+0.1640, Deflated=+0.1634, IR=0.44, Mono=0.67, p=0.0028, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.021 | 2017: +0.184 | 2018: +0.067 | 2019: +0.087 | 2020: +0.075 | 2021: +0.079 | 2022: +0.067 | 2023: +0.119 | 2024: +0.104 | 2025: +0.094 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.145 | 2016: +0.094 | 2017: +0.220 | 2018: +0.203 | 2019: +0.252 | 2020: +0.021 | 2021: +0.315 | 2022: +0.019 | 2023: +0.340 | 2024: +0.074 | 2025: +0.059 | 2026: -0.258
- IC CV=0.52, Neg years (linear/tail)=0/0 of 7, Half ratio=0.87, Recency ratio=0.99
- Early IC=+0.0779, Recent IC=+0.0768, 1st-half IC=+0.1100, 2nd-half IC=+0.0960, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.170, Q2=+0.063, Q3_mid=+0.120, Q4=+0.066, Q5_high_vol=+0.119

**`combo_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1074, Sharpe=+0.2090)
- Admission: Train IC=+0.2066, Deflated=+0.2061, IR=0.71, Mono=0.78, p=0.0006, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.124 | 2017: +0.217 | 2018: +0.233 | 2019: +0.089 | 2020: +0.114 | 2021: +0.081 | 2022: +0.140 | 2023: +0.083 | 2024: +0.074 | 2025: +0.099 | 2026: +0.109
- Yearly Tail ICs:   2015: +0.151 | 2016: +0.317 | 2017: +0.184 | 2018: +0.355 | 2019: +0.068 | 2020: +0.106 | 2021: +0.101 | 2022: +0.086 | 2023: -0.062 | 2024: +0.032 | 2025: -0.147 | 2026: -0.058
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.58, Recency ratio=0.53
- Early IC=+0.1833, Recent IC=+0.0974, 1st-half IC=+0.2127, 2nd-half IC=+0.1224, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.195, Q2=+0.101, Q3_mid=+0.184, Q4=+0.120, Q5_high_vol=+0.290

**`combo_min__close_vs_open_range__first_bar_sentiment`** (Lock IC=+0.0766, Sharpe=+0.1999)
- Admission: Train IC=+0.2239, Deflated=+0.2233, IR=0.68, Mono=0.76, p=0.0002, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.246 | 2016: +0.126 | 2017: +0.189 | 2018: +0.180 | 2019: +0.103 | 2020: +0.085 | 2021: +0.071 | 2022: +0.064 | 2023: +0.057 | 2024: +0.086 | 2025: +0.137 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.351 | 2016: +0.092 | 2017: +0.348 | 2018: +0.191 | 2019: +0.145 | 2020: +0.057 | 2021: +0.194 | 2022: +0.105 | 2023: +0.074 | 2024: +0.043 | 2025: +0.165 | 2026: +0.036
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.60, Recency ratio=0.42
- Early IC=+0.1856, Recent IC=+0.0779, 1st-half IC=+0.1798, 2nd-half IC=+0.1087, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.189, Q2=-0.013, Q3_mid=+0.173, Q4=+0.131, Q5_high_vol=+0.214

**`or_fill_ratio`** (Lock IC=+0.0805, Sharpe=+0.1951)
- Admission: Train IC=+0.1288, Deflated=+0.1281, IR=0.51, Mono=0.73, p=0.0172, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.130 | 2016: +0.041 | 2017: +0.154 | 2018: +0.055 | 2019: +0.054 | 2020: +0.072 | 2021: +0.023 | 2022: +0.085 | 2023: +0.083 | 2024: +0.114 | 2025: +0.135 | 2026: -0.076
- Yearly Tail ICs:   2015: +0.203 | 2016: +0.051 | 2017: +0.276 | 2018: +0.158 | 2019: +0.053 | 2020: +0.082 | 2021: +0.215 | 2022: +0.179 | 2023: +0.006 | 2024: +0.212 | 2025: +0.018 | 2026: +0.083
- IC CV=0.59, Neg years (linear/tail)=0/0 of 7, Half ratio=0.60, Recency ratio=0.55
- Early IC=+0.0856, Recent IC=+0.0472, 1st-half IC=+0.0996, 2nd-half IC=+0.0600, Neg regimes=1/5
- Regime ICs: Q1_low_vol=+0.141, Q2=-0.017, Q3_mid=+0.104, Q4=+0.101, Q5_high_vol=+0.074

**`star50_limit_proximity_early`** (Lock IC=+0.1129, Sharpe=+0.1931)
- Admission: Train IC=+0.2250, Deflated=+0.2247, IR=0.61, Mono=0.71, p=0.0002, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.249 | 2016: +0.058 | 2017: +0.221 | 2018: +0.079 | 2019: +0.126 | 2020: +0.089 | 2021: +0.038 | 2022: +0.083 | 2023: +0.071 | 2024: +0.110 | 2025: +0.089 | 2026: +0.186
- Yearly Tail ICs:   2015: +0.156 | 2016: +0.217 | 2017: +0.195 | 2018: +0.226 | 2019: +0.244 | 2020: +0.168 | 2021: -0.011 | 2022: -0.111 | 2023: -0.093 | 2024: +0.027 | 2025: -0.143 | 2026: +0.426
- IC CV=0.62, Neg years (linear/tail)=0/1 of 7, Half ratio=0.45, Recency ratio=0.42
- Early IC=+0.1534, Recent IC=+0.0639, 1st-half IC=+0.1839, 2nd-half IC=+0.0828, Neg regimes=0/5
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.047, Q3_mid=+0.084, Q4=+0.089, Q5_high_vol=+0.197

**`combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range`** (Lock IC=+0.0899, Sharpe=+0.1903)
- Admission: Train IC=+0.2493, Deflated=+0.2494, IR=0.76, Mono=0.77, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.202 | 2016: +0.077 | 2017: +0.215 | 2018: +0.183 | 2019: +0.093 | 2020: +0.174 | 2021: +0.062 | 2022: +0.117 | 2023: +0.145 | 2024: +0.101 | 2025: +0.057 | 2026: -0.031
- Yearly Tail ICs:   2015: +0.400 | 2016: +0.136 | 2017: +0.328 | 2018: +0.250 | 2019: +0.165 | 2020: +0.145 | 2021: +0.181 | 2022: +0.062 | 2023: +0.172 | 2024: +0.232 | 2025: -0.037 | 2026: +0.006
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.91, Recency ratio=0.84
- Early IC=+0.1397, Recent IC=+0.1179, 1st-half IC=+0.1547, 2nd-half IC=+0.1411, Neg regimes=0/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.185, Q2=+0.043, Q3_mid=+0.164, Q4=+0.128, Q5_high_vol=+0.209

**`combo_rank_max__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1063, Sharpe=+0.1838)
- Admission: Train IC=+0.1990, Deflated=+0.1985, IR=0.68, Mono=0.71, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.108 | 2017: +0.208 | 2018: +0.193 | 2019: +0.109 | 2020: +0.122 | 2021: +0.060 | 2022: +0.123 | 2023: +0.072 | 2024: +0.104 | 2025: +0.070 | 2026: +0.131
- Yearly Tail ICs:   2015: +0.176 | 2016: +0.129 | 2017: +0.247 | 2018: +0.225 | 2019: +0.110 | 2020: +0.182 | 2021: +0.186 | 2022: +0.074 | 2023: -0.042 | 2024: +0.056 | 2025: -0.098 | 2026: +0.119
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=0.60, Recency ratio=0.54
- Early IC=+0.1710, Recent IC=+0.0918, 1st-half IC=+0.2027, 2nd-half IC=+0.1216, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.162, Q2=+0.088, Q3_mid=+0.152, Q4=+0.089, Q5_high_vol=+0.242

**`combo_rank_max__net_volume_flow__first_bar_return`** (Lock IC=+0.0800, Sharpe=+0.1813)
- Admission: Train IC=+0.2090, Deflated=+0.2083, IR=0.67, Mono=0.75, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.195 | 2016: +0.119 | 2017: +0.176 | 2018: +0.234 | 2019: +0.119 | 2020: +0.115 | 2021: +0.114 | 2022: +0.098 | 2023: +0.077 | 2024: +0.124 | 2025: +0.106 | 2026: -0.080
- Yearly Tail ICs:   2015: +0.215 | 2016: +0.087 | 2017: +0.177 | 2018: +0.286 | 2019: +0.113 | 2020: +0.338 | 2021: +0.271 | 2022: +0.249 | 2023: +0.369 | 2024: +0.243 | 2025: -0.040 | 2026: -0.519
- IC CV=0.29, Neg years (linear/tail)=0/0 of 7, Half ratio=0.81, Recency ratio=0.73
- Early IC=+0.1570, Recent IC=+0.1150, 1st-half IC=+0.1805, 2nd-half IC=+0.1455, Neg regimes=0/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.029, Q3_mid=+0.169, Q4=+0.145, Q5_high_vol=+0.241

**`combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1166, Sharpe=+0.1778)
- Admission: Train IC=+0.2083, Deflated=+0.2076, IR=0.47, Mono=0.71, p=0.0006, MaxCorr=0.95
- Yearly Linear ICs: 2015: +0.303 | 2016: +0.102 | 2017: +0.246 | 2018: +0.139 | 2019: +0.137 | 2020: +0.130 | 2021: +0.050 | 2022: +0.134 | 2023: +0.080 | 2024: +0.104 | 2025: +0.080 | 2026: +0.142
- Yearly Tail ICs:   2015: +0.222 | 2016: +0.144 | 2017: +0.171 | 2018: +0.053 | 2019: +0.295 | 2020: +0.064 | 2021: +0.144 | 2022: +0.108 | 2023: -0.025 | 2024: +0.060 | 2025: +0.087 | 2026: +0.140
- IC CV=0.50, Neg years (linear/tail)=0/0 of 7, Half ratio=0.55, Recency ratio=0.47
- Early IC=+0.2042, Recent IC=+0.0966, 1st-half IC=+0.2267, 2nd-half IC=+0.1237, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.216, Q2=+0.067, Q3_mid=+0.152, Q4=+0.108, Q5_high_vol=+0.284

**`combo_sig_product__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.0870, Sharpe=+0.1717)
- Admission: Train IC=+0.2106, Deflated=+0.2106, IR=0.64, Mono=0.72, p=0.0006, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.210 | 2016: -0.023 | 2017: +0.215 | 2018: +0.153 | 2019: +0.096 | 2020: +0.159 | 2021: +0.104 | 2022: +0.064 | 2023: +0.147 | 2024: +0.083 | 2025: +0.048 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.350 | 2016: +0.048 | 2017: +0.428 | 2018: +0.120 | 2019: +0.125 | 2020: +0.182 | 2021: +0.112 | 2022: -0.043 | 2023: +0.245 | 2024: +0.116 | 2025: -0.091 | 2026: +0.336
- IC CV=0.58, Neg years (linear/tail)=1/0 of 7, Half ratio=1.20, Recency ratio=1.41
- Early IC=+0.0935, Recent IC=+0.1315, 1st-half IC=+0.1199, 2nd-half IC=+0.1442, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.146, Q2=+0.063, Q3_mid=+0.153, Q4=+0.085, Q5_high_vol=+0.211

**`combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency`** (Lock IC=+0.0905, Sharpe=+0.1591)
- Admission: Train IC=+0.2042, Deflated=+0.2041, IR=0.49, Mono=0.70, p=0.0006, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.229 | 2016: +0.091 | 2017: +0.168 | 2018: +0.190 | 2019: +0.037 | 2020: +0.123 | 2021: +0.030 | 2022: +0.133 | 2023: +0.085 | 2024: +0.054 | 2025: +0.083 | 2026: +0.063
- Yearly Tail ICs:   2015: +0.117 | 2016: +0.413 | 2017: +0.109 | 2018: +0.216 | 2019: +0.060 | 2020: +0.113 | 2021: +0.208 | 2022: +0.105 | 2023: +0.091 | 2024: +0.122 | 2025: -0.071 | 2026: -0.097
- IC CV=0.57, Neg years (linear/tail)=0/0 of 7, Half ratio=0.50, Recency ratio=0.48
- Early IC=+0.1600, Recent IC=+0.0761, 1st-half IC=+0.1901, 2nd-half IC=+0.0949, Neg regimes=1/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.138, Q2=-0.000, Q3_mid=+0.173, Q4=+0.116, Q5_high_vol=+0.272

**`combo_rank_max__bar_ret_0__max_down_ret`** (Lock IC=+0.0853, Sharpe=+0.1525)
- Admission: Train IC=+0.2453, Deflated=+0.2445, IR=0.64, Mono=0.70, p=0.0000, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.261 | 2016: +0.090 | 2017: +0.239 | 2018: +0.234 | 2019: +0.150 | 2020: +0.126 | 2021: +0.098 | 2022: +0.093 | 2023: +0.036 | 2024: +0.117 | 2025: +0.112 | 2026: +0.029
- Yearly Tail ICs:   2015: +0.605 | 2016: -0.121 | 2017: +0.202 | 2018: +0.245 | 2019: +0.306 | 2020: +0.177 | 2021: +0.248 | 2022: +0.130 | 2023: +0.169 | 2024: +0.217 | 2025: +0.104 | 2026: -0.076
- IC CV=0.39, Neg years (linear/tail)=0/1 of 7, Half ratio=0.80, Recency ratio=0.64
- Early IC=+0.1755, Recent IC=+0.1131, 1st-half IC=+0.1946, 2nd-half IC=+0.1552, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.194, Q2=+0.018, Q3_mid=+0.171, Q4=+0.145, Q5_high_vol=+0.257

**`combo_sig_product__opening_drive_thrust_ratio__bar_ret_0`** (Lock IC=+0.0807, Sharpe=+0.1521)
- Admission: Train IC=+0.1848, Deflated=+0.1844, IR=0.45, Mono=0.66, p=0.0012, MaxCorr=0.81
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.045 | 2017: +0.214 | 2018: +0.221 | 2019: +0.070 | 2020: +0.158 | 2021: +0.126 | 2022: +0.058 | 2023: +0.134 | 2024: +0.074 | 2025: +0.073 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.173 | 2016: -0.085 | 2017: +0.265 | 2018: +0.509 | 2019: +0.051 | 2020: +0.250 | 2021: +0.264 | 2022: -0.097 | 2023: +0.227 | 2024: +0.085 | 2025: +0.152 | 2026: -0.331
- IC CV=0.44, Neg years (linear/tail)=0/1 of 7, Half ratio=1.04, Recency ratio=1.13
- Early IC=+0.1261, Recent IC=+0.1423, 1st-half IC=+0.1495, 2nd-half IC=+0.1562, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.022, Q3_mid=+0.149, Q4=+0.112, Q5_high_vol=+0.214

**`combo_sig_product__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0808, Sharpe=+0.1521)
- Admission: Train IC=+0.1848, Deflated=+0.1844, IR=0.45, Mono=0.66, p=0.0012, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.207 | 2016: +0.045 | 2017: +0.214 | 2018: +0.221 | 2019: +0.070 | 2020: +0.158 | 2021: +0.126 | 2022: +0.058 | 2023: +0.134 | 2024: +0.074 | 2025: +0.073 | 2026: +0.038
- Yearly Tail ICs:   2015: +0.171 | 2016: -0.083 | 2017: +0.265 | 2018: +0.509 | 2019: +0.051 | 2020: +0.250 | 2021: +0.265 | 2022: -0.097 | 2023: +0.227 | 2024: +0.082 | 2025: +0.152 | 2026: -0.331
- IC CV=0.44, Neg years (linear/tail)=0/1 of 7, Half ratio=1.04, Recency ratio=1.13
- Early IC=+0.1258, Recent IC=+0.1421, 1st-half IC=+0.1495, 2nd-half IC=+0.1561, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.186, Q2=+0.021, Q3_mid=+0.148, Q4=+0.111, Q5_high_vol=+0.214

**`combo_sig_product__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.0793, Sharpe=+0.1517)
- Admission: Train IC=+0.2072, Deflated=+0.2079, IR=0.52, Mono=0.70, p=0.0006, MaxCorr=0.85
- Yearly Linear ICs: 2015: +0.194 | 2016: +0.012 | 2017: +0.175 | 2018: +0.249 | 2019: +0.114 | 2020: +0.166 | 2021: +0.181 | 2022: +0.103 | 2023: +0.085 | 2024: +0.110 | 2025: +0.050 | 2026: -0.034
- Yearly Tail ICs:   2015: +0.041 | 2016: +0.163 | 2017: +0.175 | 2018: +0.517 | 2019: +0.189 | 2020: +0.178 | 2021: +0.316 | 2022: +0.005 | 2023: +0.121 | 2024: +0.134 | 2025: -0.103 | 2026: -0.221
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=1.27, Recency ratio=1.68
- Early IC=+0.1031, Recent IC=+0.1732, 1st-half IC=+0.1438, 2nd-half IC=+0.1822, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.36)
- Regime ICs: Q1_low_vol=+0.147, Q2=+0.073, Q3_mid=+0.195, Q4=+0.174, Q5_high_vol=+0.216

**`combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure`** (Lock IC=+0.0847, Sharpe=+0.1161)
- Admission: Train IC=+0.2915, Deflated=+0.2911, IR=0.66, Mono=0.74, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.250 | 2016: +0.045 | 2017: +0.158 | 2018: +0.197 | 2019: +0.170 | 2020: +0.196 | 2021: +0.150 | 2022: +0.046 | 2023: +0.104 | 2024: +0.140 | 2025: +0.067 | 2026: +0.010
- Yearly Tail ICs:   2015: +0.367 | 2016: -0.042 | 2017: +0.192 | 2018: +0.274 | 2019: +0.235 | 2020: +0.120 | 2021: +0.202 | 2022: +0.268 | 2023: +0.062 | 2024: +0.153 | 2025: +0.144 | 2026: -0.157
- IC CV=0.35, Neg years (linear/tail)=0/1 of 7, Half ratio=1.22, Recency ratio=1.17
- Early IC=+0.1475, Recent IC=+0.1732, 1st-half IC=+0.1551, 2nd-half IC=+0.1897, Neg regimes=0/5
- Weak component: `smooth_momentum_structure` (CV=0.46)
- Regime ICs: Q1_low_vol=+0.148, Q2=+0.114, Q3_mid=+0.154, Q4=+0.113, Q5_high_vol=+0.299

**`combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression`** (Lock IC=+0.1161, Sharpe=+0.1138)
- Admission: Train IC=+0.2190, Deflated=+0.2185, IR=0.62, Mono=0.74, p=0.0004, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.037 | 2017: +0.198 | 2018: +0.102 | 2019: +0.079 | 2020: +0.095 | 2021: +0.068 | 2022: +0.088 | 2023: +0.105 | 2024: +0.116 | 2025: +0.118 | 2026: +0.087
- Yearly Tail ICs:   2015: +0.379 | 2016: +0.084 | 2017: +0.233 | 2018: +0.157 | 2019: +0.229 | 2020: +0.143 | 2021: +0.071 | 2022: +0.074 | 2023: -0.011 | 2024: -0.004 | 2025: -0.051 | 2026: +0.072
- IC CV=0.59, Neg years (linear/tail)=0/0 of 7, Half ratio=0.50, Recency ratio=0.58
- Early IC=+0.1404, Recent IC=+0.0814, 1st-half IC=+0.1787, 2nd-half IC=+0.0896, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.217, Q2=+0.041, Q3_mid=+0.111, Q4=+0.121, Q5_high_vol=+0.174

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1019, Sharpe=+0.0840)
- Admission: Train IC=+0.2129, Deflated=+0.2127, IR=0.64, Mono=0.74, p=0.0006, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.253 | 2016: +0.054 | 2017: +0.184 | 2018: +0.095 | 2019: +0.102 | 2020: +0.092 | 2021: +0.034 | 2022: +0.078 | 2023: +0.039 | 2024: +0.071 | 2025: +0.109 | 2026: +0.203
- Yearly Tail ICs:   2015: +0.410 | 2016: +0.053 | 2017: +0.038 | 2018: +0.301 | 2019: +0.064 | 2020: +0.316 | 2021: +0.150 | 2022: -0.059 | 2023: -0.058 | 2024: -0.058 | 2025: -0.001 | 2026: +0.464
- IC CV=0.61, Neg years (linear/tail)=0/0 of 7, Half ratio=0.48, Recency ratio=0.41
- Early IC=+0.1534, Recent IC=+0.0629, 1st-half IC=+0.1753, 2nd-half IC=+0.0842, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.62)
- Regime ICs: Q1_low_vol=+0.132, Q2=+0.036, Q3_mid=+0.111, Q4=+0.078, Q5_high_vol=+0.209

**`combo_sig_product__close_vs_open_range__early_body_momentum`** (Lock IC=+0.0727, Sharpe=+0.0817)
- Admission: Train IC=+0.2008, Deflated=+0.2002, IR=0.46, Mono=0.70, p=0.0006, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.136 | 2016: +0.062 | 2017: +0.161 | 2018: +0.121 | 2019: +0.046 | 2020: +0.088 | 2021: +0.063 | 2022: +0.098 | 2023: +0.062 | 2024: +0.119 | 2025: +0.127 | 2026: -0.111
- Yearly Tail ICs:   2015: +0.182 | 2016: +0.133 | 2017: +0.117 | 2018: +0.142 | 2019: +0.132 | 2020: +0.274 | 2021: +0.217 | 2022: +0.118 | 2023: +0.118 | 2024: +0.211 | 2025: +0.009 | 2026: -0.159
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=0.64, Recency ratio=0.76
- Early IC=+0.0988, Recent IC=+0.0752, 1st-half IC=+0.1257, 2nd-half IC=+0.0800, Neg regimes=1/5
- Weak component: `close_vs_open_range` (CV=0.48)
- Regime ICs: Q1_low_vol=+0.149, Q2=-0.034, Q3_mid=+0.152, Q4=+0.113, Q5_high_vol=+0.131

**`combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression`** (Lock IC=+0.1160, Sharpe=+0.0757)
- Admission: Train IC=+0.2674, Deflated=+0.2672, IR=0.71, Mono=0.76, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.243 | 2016: +0.102 | 2017: +0.219 | 2018: +0.117 | 2019: +0.067 | 2020: +0.098 | 2021: +0.051 | 2022: +0.123 | 2023: +0.099 | 2024: +0.092 | 2025: +0.126 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.412 | 2016: +0.188 | 2017: +0.226 | 2018: +0.226 | 2019: +0.218 | 2020: +0.216 | 2021: +0.180 | 2022: +0.104 | 2023: -0.057 | 2024: +0.078 | 2025: -0.005 | 2026: -0.058
- IC CV=0.54, Neg years (linear/tail)=0/0 of 7, Half ratio=0.41, Recency ratio=0.43
- Early IC=+0.1725, Recent IC=+0.0743, 1st-half IC=+0.2054, 2nd-half IC=+0.0849, Neg regimes=0/5
- Weak component: `body_size_progression` (CV=0.54)
- Regime ICs: Q1_low_vol=+0.200, Q2=+0.046, Q3_mid=+0.116, Q4=+0.159, Q5_high_vol=+0.200

**`combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1054, Sharpe=+0.0665)
- Admission: Train IC=+0.2091, Deflated=+0.2087, IR=0.68, Mono=0.74, p=0.0006, MaxCorr=0.86
- Yearly Linear ICs: 2015: +0.242 | 2016: +0.122 | 2017: +0.214 | 2018: +0.211 | 2019: +0.088 | 2020: +0.115 | 2021: +0.075 | 2022: +0.140 | 2023: +0.089 | 2024: +0.082 | 2025: +0.080 | 2026: +0.119
- Yearly Tail ICs:   2015: +0.175 | 2016: +0.350 | 2017: +0.170 | 2018: +0.272 | 2019: +0.105 | 2020: +0.112 | 2021: +0.131 | 2022: +0.143 | 2023: -0.070 | 2024: +0.109 | 2025: -0.176 | 2026: -0.063
- IC CV=0.42, Neg years (linear/tail)=0/0 of 7, Half ratio=0.56, Recency ratio=0.52
- Early IC=+0.1815, Recent IC=+0.0949, 1st-half IC=+0.2079, 2nd-half IC=+0.1161, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.40)
- Regime ICs: Q1_low_vol=+0.189, Q2=+0.098, Q3_mid=+0.180, Q4=+0.114, Q5_high_vol=+0.287

**`combo_sig_product__net_volume_flow__bar_ret_0`** (Lock IC=+0.0565, Sharpe=+0.0638)
- Admission: Train IC=+0.1789, Deflated=+0.1778, IR=0.46, Mono=0.67, p=0.0014, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.034 | 2017: +0.156 | 2018: +0.194 | 2019: +0.110 | 2020: +0.083 | 2021: +0.064 | 2022: +0.053 | 2023: +0.062 | 2024: +0.065 | 2025: +0.105 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.037 | 2017: +0.220 | 2018: +0.425 | 2019: +0.230 | 2020: +0.167 | 2021: +0.135 | 2022: +0.182 | 2023: +0.086 | 2024: +0.168 | 2025: +0.162 | 2026: -0.387
- IC CV=0.47, Neg years (linear/tail)=0/1 of 7, Half ratio=0.98, Recency ratio=1.02
- Early IC=+0.0722, Recent IC=+0.0733, 1st-half IC=+0.1127, 2nd-half IC=+0.1103, Neg regimes=1/5
- Weak component: `bar_ret_0` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.047, Q3_mid=+0.130, Q4=+0.136, Q5_high_vol=+0.127

**`combo_sig_product__net_volume_flow__first_bar_return`** (Lock IC=+0.0566, Sharpe=+0.0638)
- Admission: Train IC=+0.1789, Deflated=+0.1778, IR=0.46, Mono=0.67, p=0.0014, MaxCorr=1.00
- Yearly Linear ICs: 2015: +0.110 | 2016: +0.034 | 2017: +0.156 | 2018: +0.194 | 2019: +0.109 | 2020: +0.083 | 2021: +0.064 | 2022: +0.053 | 2023: +0.062 | 2024: +0.065 | 2025: +0.105 | 2026: -0.058
- Yearly Tail ICs:   2015: +0.202 | 2016: -0.035 | 2017: +0.220 | 2018: +0.425 | 2019: +0.230 | 2020: +0.167 | 2021: +0.137 | 2022: +0.182 | 2023: +0.086 | 2024: +0.165 | 2025: +0.162 | 2026: -0.388
- IC CV=0.47, Neg years (linear/tail)=0/1 of 7, Half ratio=0.98, Recency ratio=1.03
- Early IC=+0.0717, Recent IC=+0.0737, 1st-half IC=+0.1125, 2nd-half IC=+0.1103, Neg regimes=1/5
- Weak component: `first_bar_return` (CV=0.35)
- Regime ICs: Q1_low_vol=+0.183, Q2=-0.047, Q3_mid=+0.131, Q4=+0.136, Q5_high_vol=+0.127

**`combo_rel_diff__max_up_ret__early_body_momentum`** (Lock IC=+0.0159, Sharpe=+0.0630)
- Admission: Train IC=+0.2407, Deflated=+0.2417, IR=0.64, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.135 | 2016: +0.110 | 2017: +0.004 | 2018: +0.085 | 2019: +0.051 | 2020: +0.023 | 2021: +0.065 | 2022: +0.034 | 2023: +0.002 | 2024: +0.034 | 2025: -0.054 | 2026: +0.096
- Yearly Tail ICs:   2015: +0.368 | 2016: +0.184 | 2017: +0.177 | 2018: +0.275 | 2019: +0.164 | 2020: +0.248 | 2021: +0.140 | 2022: -0.022 | 2023: +0.068 | 2024: +0.095 | 2025: -0.176 | 2026: +0.347
- IC CV=0.64, Neg years (linear/tail)=0/0 of 7, Half ratio=0.54, Recency ratio=0.36
- Early IC=+0.1227, Recent IC=+0.0439, 1st-half IC=+0.0892, 2nd-half IC=+0.0482, Neg regimes=1/5
- Weak component: `early_body_momentum` (CV=0.39)
- Regime ICs: Q1_low_vol=-0.020, Q2=+0.141, Q3_mid=+0.016, Q4=+0.033, Q5_high_vol=+0.180

**`combo_ratio__max_down_ret__volatility_expansion_trend_vector`** (Lock IC=+0.0479, Sharpe=+0.0410)
- Admission: Train IC=+0.2185, Deflated=+0.2177, IR=0.74, Mono=0.75, p=0.0004, MaxCorr=0.10
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.077 | 2017: +0.225 | 2018: +0.162 | 2019: +0.118 | 2020: +0.119 | 2021: +0.022 | 2022: -0.017 | 2023: -0.025 | 2024: +0.066 | 2025: +0.145 | 2026: +0.102
- Yearly Tail ICs:   2015: +0.312 | 2016: +0.012 | 2017: +0.223 | 2018: +0.364 | 2019: +0.285 | 2020: +0.243 | 2021: +0.162 | 2022: -0.008 | 2023: -0.037 | 2024: +0.089 | 2025: +0.216 | 2026: +0.070
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=0.63, Recency ratio=0.44
- Early IC=+0.1622, Recent IC=+0.0708, 1st-half IC=+0.1680, 2nd-half IC=+0.1053, Neg regimes=1/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.172, Q2=-0.018, Q3_mid=+0.193, Q4=+0.079, Q5_high_vol=+0.219

**`combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency`** (Lock IC=+0.0317, Sharpe=+0.0388)
- Admission: Train IC=+0.2248, Deflated=+0.2252, IR=0.64, Mono=0.71, p=0.0002, MaxCorr=0.68
- Yearly Linear ICs: 2015: +0.198 | 2016: +0.031 | 2017: +0.038 | 2018: +0.083 | 2019: +0.134 | 2020: +0.109 | 2021: +0.111 | 2022: +0.009 | 2023: +0.017 | 2024: +0.060 | 2025: -0.043 | 2026: +0.180
- Yearly Tail ICs:   2015: +0.117 | 2016: +0.035 | 2017: +0.446 | 2018: +0.253 | 2019: +0.261 | 2020: +0.317 | 2021: +0.035 | 2022: -0.110 | 2023: +0.043 | 2024: +0.106 | 2025: -0.108 | 2026: +0.431
- IC CV=0.53, Neg years (linear/tail)=0/0 of 7, Half ratio=1.55, Recency ratio=0.96
- Early IC=+0.1144, Recent IC=+0.1100, 1st-half IC=+0.0784, 2nd-half IC=+0.1219, Neg regimes=0/5
- Weak component: `trend_bar_close_consistency` (CV=0.73)
- Regime ICs: Q1_low_vol=+0.062, Q2=+0.117, Q3_mid=+0.049, Q4=+0.035, Q5_high_vol=+0.208

**`combo_max__early_body_momentum__max_down_ret`** (Lock IC=+0.0689, Sharpe=+0.0005)
- Admission: Train IC=+0.1669, Deflated=+0.1666, IR=0.40, Mono=0.68, p=0.0026, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.170 | 2016: +0.044 | 2017: +0.177 | 2018: +0.146 | 2019: +0.063 | 2020: +0.098 | 2021: +0.065 | 2022: +0.058 | 2023: +0.041 | 2024: +0.120 | 2025: +0.149 | 2026: -0.091
- Yearly Tail ICs:   2015: +0.241 | 2016: +0.167 | 2017: +0.161 | 2018: +0.041 | 2019: +0.125 | 2020: +0.053 | 2021: +0.247 | 2022: +0.180 | 2023: +0.250 | 2024: +0.271 | 2025: +0.036 | 2026: -0.205
- IC CV=0.47, Neg years (linear/tail)=0/0 of 7, Half ratio=0.67, Recency ratio=0.76
- Early IC=+0.1069, Recent IC=+0.0816, 1st-half IC=+0.1369, 2nd-half IC=+0.0915, Neg regimes=0/5
- Weak component: `max_down_ret` (CV=0.55)
- Regime ICs: Q1_low_vol=+0.178, Q2=+0.015, Q3_mid=+0.123, Q4=+0.118, Q5_high_vol=+0.145

### 159915ETF — `single` True Positives

**`combo_min__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1228, Sharpe=+1.5491)
- Admission: Train IC=+0.2841, Deflated=+0.2818, IR=0.58, Mono=0.68, p=0.0000, MaxCorr=0.88
- Yearly Linear ICs: 2015: +0.230 | 2016: +0.089 | 2017: -0.026 | 2018: +0.120 | 2019: +0.266 | 2020: +0.164 | 2021: +0.125 | 2022: +0.062 | 2023: +0.148 | 2024: +0.109 | 2025: +0.150 | 2026: +0.123
- Yearly Tail ICs:   2015: +0.165 | 2016: +0.140 | 2017: +0.065 | 2018: +0.348 | 2019: +0.519 | 2020: +0.371 | 2021: +0.261 | 2022: +0.198 | 2023: +0.321 | 2024: +0.443 | 2025: +0.233 | 2026: +0.378
- IC CV=0.64, Neg years (linear/tail)=1/0 of 7, Half ratio=1.44, Recency ratio=0.91
- Early IC=+0.1594, Recent IC=+0.1447, 1st-half IC=+0.1271, 2nd-half IC=+0.1826, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.054, Q3_mid=+0.149, Q4=+0.180, Q5_high_vol=+0.217

**`combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1379, Sharpe=+1.4840)
- Admission: Train IC=+0.2945, Deflated=+0.2928, IR=0.60, Mono=0.72, p=0.0000, MaxCorr=0.00
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.046 | 2017: +0.009 | 2018: +0.127 | 2019: +0.235 | 2020: +0.125 | 2021: +0.141 | 2022: +0.096 | 2023: +0.184 | 2024: +0.126 | 2025: +0.179 | 2026: +0.072
- Yearly Tail ICs:   2015: +0.228 | 2016: +0.075 | 2017: +0.102 | 2018: +0.348 | 2019: +0.519 | 2020: +0.299 | 2021: +0.329 | 2022: +0.400 | 2023: +0.342 | 2024: +0.335 | 2025: +0.165 | 2026: +0.364
- IC CV=0.58, Neg years (linear/tail)=0/0 of 7, Half ratio=1.42, Recency ratio=1.13
- Early IC=+0.1182, Recent IC=+0.1331, 1st-half IC=+0.1155, 2nd-half IC=+0.1644, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.024, Q2=+0.101, Q3_mid=+0.163, Q4=+0.164, Q5_high_vol=+0.162

**`combo_z_sum__star50_limit_proximity_early__bar_body_rng_0`** (Lock IC=+0.1201, Sharpe=+1.4647)
- Admission: Train IC=+0.2647, Deflated=+0.2627, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.211 | 2016: +0.121 | 2017: -0.024 | 2018: +0.163 | 2019: +0.229 | 2020: +0.158 | 2021: +0.146 | 2022: +0.107 | 2023: +0.115 | 2024: +0.081 | 2025: +0.144 | 2026: +0.134
- Yearly Tail ICs:   2015: +0.035 | 2016: +0.162 | 2017: +0.098 | 2018: +0.366 | 2019: +0.465 | 2020: +0.227 | 2021: +0.302 | 2022: +0.180 | 2023: +0.155 | 2024: +0.453 | 2025: +0.221 | 2026: +0.173
- IC CV=0.54, Neg years (linear/tail)=1/0 of 7, Half ratio=1.45, Recency ratio=0.92
- Early IC=+0.1661, Recent IC=+0.1520, 1st-half IC=+0.1304, 2nd-half IC=+0.1894, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.054, Q2=+0.045, Q3_mid=+0.162, Q4=+0.220, Q5_high_vol=+0.200

**`combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early`** (Lock IC=+0.1333, Sharpe=+1.4351)
- Admission: Train IC=+0.2645, Deflated=+0.2631, IR=0.63, Mono=0.72, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.203 | 2016: +0.034 | 2017: -0.003 | 2018: +0.108 | 2019: +0.231 | 2020: +0.131 | 2021: +0.132 | 2022: +0.109 | 2023: +0.186 | 2024: +0.087 | 2025: +0.186 | 2026: +0.083
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.016 | 2017: +0.073 | 2018: +0.342 | 2019: +0.495 | 2020: +0.320 | 2021: +0.285 | 2022: +0.298 | 2023: +0.468 | 2024: +0.314 | 2025: +0.117 | 2026: +0.279
- IC CV=0.64, Neg years (linear/tail)=1/1 of 7, Half ratio=1.42, Recency ratio=1.09
- Early IC=+0.1210, Recent IC=+0.1317, 1st-half IC=+0.1124, 2nd-half IC=+0.1595, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.025, Q2=+0.071, Q3_mid=+0.145, Q4=+0.154, Q5_high_vol=+0.180

**`combo_mean__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1228, Sharpe=+1.2289)
- Admission: Train IC=+0.2443, Deflated=+0.2423, IR=0.65, Mono=0.71, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.227 | 2016: +0.092 | 2017: +0.001 | 2018: +0.171 | 2019: +0.207 | 2020: +0.134 | 2021: +0.155 | 2022: +0.118 | 2023: +0.146 | 2024: +0.069 | 2025: +0.156 | 2026: +0.111
- Yearly Tail ICs:   2015: +0.116 | 2016: +0.062 | 2017: +0.156 | 2018: +0.386 | 2019: +0.398 | 2020: +0.192 | 2021: +0.392 | 2022: +0.122 | 2023: +0.111 | 2024: +0.406 | 2025: +0.195 | 2026: +0.223
- IC CV=0.50, Neg years (linear/tail)=0/0 of 7, Half ratio=1.17, Recency ratio=0.91
- Early IC=+0.1595, Recent IC=+0.1445, 1st-half IC=+0.1489, 2nd-half IC=+0.1740, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.063, Q2=+0.053, Q3_mid=+0.136, Q4=+0.235, Q5_high_vol=+0.194

**`combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret`** (Lock IC=+0.1317, Sharpe=+1.2186)
- Admission: Train IC=+0.2455, Deflated=+0.2443, IR=0.59, Mono=0.73, p=0.0000, MaxCorr=0.83
- Yearly Linear ICs: 2015: +0.190 | 2016: +0.103 | 2017: +0.023 | 2018: +0.127 | 2019: +0.160 | 2020: +0.153 | 2021: +0.167 | 2022: +0.157 | 2023: +0.140 | 2024: +0.089 | 2025: +0.180 | 2026: +0.077
- Yearly Tail ICs:   2015: +0.005 | 2016: +0.249 | 2017: +0.070 | 2018: +0.325 | 2019: +0.351 | 2020: +0.181 | 2021: +0.386 | 2022: +0.252 | 2023: +0.141 | 2024: +0.292 | 2025: +0.142 | 2026: +0.114
- IC CV=0.39, Neg years (linear/tail)=0/0 of 7, Half ratio=1.26, Recency ratio=1.09
- Early IC=+0.1465, Recent IC=+0.1602, 1st-half IC=+0.1342, 2nd-half IC=+0.1686, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.051, Q2=+0.091, Q3_mid=+0.153, Q4=+0.277, Q5_high_vol=+0.159

**`combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1322, Sharpe=+1.1640)
- Admission: Train IC=+0.2557, Deflated=+0.2535, IR=0.49, Mono=0.66, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.226 | 2016: +0.108 | 2017: +0.032 | 2018: +0.161 | 2019: +0.225 | 2020: +0.138 | 2021: +0.175 | 2022: +0.118 | 2023: +0.172 | 2024: +0.104 | 2025: +0.176 | 2026: +0.061
- Yearly Tail ICs:   2015: +0.127 | 2016: +0.059 | 2017: +0.095 | 2018: +0.353 | 2019: +0.444 | 2020: +0.211 | 2021: +0.356 | 2022: +0.177 | 2023: +0.369 | 2024: +0.360 | 2025: +0.235 | 2026: +0.008
- IC CV=0.41, Neg years (linear/tail)=0/0 of 7, Half ratio=1.23, Recency ratio=0.94
- Early IC=+0.1667, Recent IC=+0.1562, 1st-half IC=+0.1533, 2nd-half IC=+0.1881, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.043, Q2=+0.092, Q3_mid=+0.188, Q4=+0.218, Q5_high_vol=+0.212

**`combo_clamp_diff__bar_ret_0__demark_setup_reversal_early`** (Lock IC=+0.1238, Sharpe=+1.1423)
- Admission: Train IC=+0.2232, Deflated=+0.2213, IR=0.41, Mono=0.67, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.232 | 2016: +0.041 | 2017: +0.015 | 2018: +0.122 | 2019: +0.181 | 2020: +0.105 | 2021: +0.158 | 2022: +0.132 | 2023: +0.162 | 2024: +0.057 | 2025: +0.189 | 2026: +0.027
- Yearly Tail ICs:   2015: +0.273 | 2016: +0.021 | 2017: +0.019 | 2018: +0.114 | 2019: +0.392 | 2020: +0.265 | 2021: +0.270 | 2022: +0.349 | 2023: +0.440 | 2024: +0.188 | 2025: +0.244 | 2026: -0.315
- IC CV=0.58, Neg years (linear/tail)=0/0 of 7, Half ratio=1.29, Recency ratio=0.97
- Early IC=+0.1362, Recent IC=+0.1317, 1st-half IC=+0.1196, 2nd-half IC=+0.1542, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.85)
- Regime ICs: Q1_low_vol=+0.056, Q2=+0.055, Q3_mid=+0.118, Q4=+0.187, Q5_high_vol=+0.203

**`combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment`** (Lock IC=+0.0993, Sharpe=+1.1273)
- Admission: Train IC=+0.2917, Deflated=+0.2894, IR=0.70, Mono=0.74, p=0.0000, MaxCorr=0.78
- Yearly Linear ICs: 2015: +0.254 | 2016: +0.171 | 2017: -0.008 | 2018: +0.180 | 2019: +0.206 | 2020: +0.202 | 2021: +0.114 | 2022: +0.080 | 2023: +0.113 | 2024: +0.071 | 2025: +0.120 | 2026: +0.095
- Yearly Tail ICs:   2015: +0.178 | 2016: +0.262 | 2017: +0.079 | 2018: +0.366 | 2019: +0.399 | 2020: +0.286 | 2021: +0.183 | 2022: +0.287 | 2023: +0.190 | 2024: +0.287 | 2025: +0.288 | 2026: +0.135
- IC CV=0.50, Neg years (linear/tail)=1/0 of 7, Half ratio=1.09, Recency ratio=0.74
- Early IC=+0.2127, Recent IC=+0.1577, 1st-half IC=+0.1715, 2nd-half IC=+0.1876, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.065, Q3_mid=+0.152, Q4=+0.238, Q5_high_vol=+0.250

**`combo_z_sum__first_bar_sentiment__limit_down_proximity_early`** (Lock IC=+0.0938, Sharpe=+1.1068)
- Admission: Train IC=+0.2093, Deflated=+0.2069, IR=0.53, Mono=0.69, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.049 | 2017: -0.027 | 2018: +0.121 | 2019: +0.229 | 2020: +0.140 | 2021: +0.103 | 2022: +0.086 | 2023: +0.055 | 2024: +0.068 | 2025: +0.098 | 2026: +0.129
- Yearly Tail ICs:   2015: +0.140 | 2016: +0.044 | 2017: +0.126 | 2018: +0.207 | 2019: +0.386 | 2020: +0.110 | 2021: +0.114 | 2022: +0.191 | 2023: +0.069 | 2024: +0.361 | 2025: +0.163 | 2026: +0.390
- IC CV=0.71, Neg years (linear/tail)=1/0 of 7, Half ratio=1.56, Recency ratio=0.85
- Early IC=+0.1435, Recent IC=+0.1218, 1st-half IC=+0.1091, 2nd-half IC=+0.1700, Neg regimes=0/5
- Weak component: `limit_down_proximity_early` (CV=1.21)
- Regime ICs: Q1_low_vol=+0.086, Q2=+0.038, Q3_mid=+0.149, Q4=+0.146, Q5_high_vol=+0.204

**`combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return`** (Lock IC=+0.1197, Sharpe=+1.1003)
- Admission: Train IC=+0.2638, Deflated=+0.2615, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.149 | 2017: -0.004 | 2018: +0.183 | 2019: +0.222 | 2020: +0.157 | 2021: +0.161 | 2022: +0.108 | 2023: +0.140 | 2024: +0.077 | 2025: +0.163 | 2026: +0.080
- Yearly Tail ICs:   2015: +0.159 | 2016: +0.086 | 2017: +0.128 | 2018: +0.270 | 2019: +0.368 | 2020: +0.277 | 2021: +0.441 | 2022: +0.171 | 2023: +0.226 | 2024: +0.316 | 2025: +0.217 | 2026: +0.186
- IC CV=0.46, Neg years (linear/tail)=1/0 of 7, Half ratio=1.26, Recency ratio=0.83
- Early IC=+0.1912, Recent IC=+0.1591, 1st-half IC=+0.1535, 2nd-half IC=+0.1937, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.064, Q3_mid=+0.180, Q4=+0.217, Q5_high_vol=+0.238

**`combo_min__star50_limit_proximity_early__bar_ret_0`** (Lock IC=+0.1171, Sharpe=+1.0935)
- Admission: Train IC=+0.2637, Deflated=+0.2612, IR=0.55, Mono=0.70, p=0.0000, MaxCorr=0.91
- Yearly Linear ICs: 2015: +0.239 | 2016: +0.078 | 2017: -0.023 | 2018: +0.106 | 2019: +0.259 | 2020: +0.133 | 2021: +0.110 | 2022: +0.073 | 2023: +0.152 | 2024: +0.091 | 2025: +0.148 | 2026: +0.103
- Yearly Tail ICs:   2015: +0.178 | 2016: +0.083 | 2017: +0.045 | 2018: +0.286 | 2019: +0.500 | 2020: +0.173 | 2021: +0.294 | 2022: +0.258 | 2023: +0.211 | 2024: +0.394 | 2025: +0.080 | 2026: +0.232
- IC CV=0.69, Neg years (linear/tail)=1/0 of 7, Half ratio=1.25, Recency ratio=0.76
- Early IC=+0.1588, Recent IC=+0.1212, 1st-half IC=+0.1288, 2nd-half IC=+0.1607, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.073, Q2=+0.035, Q3_mid=+0.115, Q4=+0.166, Q5_high_vol=+0.214

**`combo_rank_min__star50_limit_proximity_early__first_bar_return`** (Lock IC=+0.1185, Sharpe=+1.0647)
- Admission: Train IC=+0.2540, Deflated=+0.2515, IR=0.55, Mono=0.69, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.238 | 2016: +0.073 | 2017: -0.020 | 2018: +0.100 | 2019: +0.254 | 2020: +0.122 | 2021: +0.109 | 2022: +0.080 | 2023: +0.148 | 2024: +0.090 | 2025: +0.155 | 2026: +0.104
- Yearly Tail ICs:   2015: +0.185 | 2016: +0.072 | 2017: +0.019 | 2018: +0.277 | 2019: +0.481 | 2020: +0.204 | 2021: +0.300 | 2022: +0.244 | 2023: +0.203 | 2024: +0.379 | 2025: +0.089 | 2026: +0.270
- IC CV=0.71, Neg years (linear/tail)=1/0 of 7, Half ratio=1.22, Recency ratio=0.75
- Early IC=+0.1547, Recent IC=+0.1155, 1st-half IC=+0.1272, 2nd-half IC=+0.1555, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.030, Q3_mid=+0.107, Q4=+0.162, Q5_high_vol=+0.211

**`combo_z_sum__opening_drive_thrust_ratio__max_up_ret`** (Lock IC=+0.1129, Sharpe=+1.0635)
- Admission: Train IC=+0.2150, Deflated=+0.2131, IR=0.60, Mono=0.77, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.174 | 2016: +0.067 | 2017: +0.044 | 2018: +0.086 | 2019: +0.175 | 2020: +0.095 | 2021: +0.153 | 2022: +0.102 | 2023: +0.196 | 2024: +0.090 | 2025: +0.176 | 2026: -0.067
- Yearly Tail ICs:   2015: +0.115 | 2016: +0.117 | 2017: +0.112 | 2018: +0.240 | 2019: +0.343 | 2020: +0.205 | 2021: +0.260 | 2022: +0.308 | 2023: +0.596 | 2024: +0.204 | 2025: +0.067 | 2026: -0.270
- IC CV=0.44, Neg years (linear/tail)=0/0 of 7, Half ratio=1.32, Recency ratio=1.02
- Early IC=+0.1207, Recent IC=+0.1236, 1st-half IC=+0.1127, 2nd-half IC=+0.1494, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.006, Q2=+0.099, Q3_mid=+0.186, Q4=+0.122, Q5_high_vol=+0.165

**`combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1414, Sharpe=+1.0375)
- Admission: Train IC=+0.2449, Deflated=+0.2443, IR=0.74, Mono=0.78, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.107 | 2017: -0.074 | 2018: +0.108 | 2019: +0.116 | 2020: +0.092 | 2021: +0.053 | 2022: +0.172 | 2023: +0.132 | 2024: +0.102 | 2025: +0.109 | 2026: +0.174
- Yearly Tail ICs:   2015: +0.123 | 2016: +0.145 | 2017: +0.151 | 2018: +0.370 | 2019: +0.316 | 2020: +0.289 | 2021: +0.222 | 2022: +0.373 | 2023: +0.090 | 2024: +0.107 | 2025: +0.186 | 2026: +0.310
- IC CV=0.88, Neg years (linear/tail)=1/0 of 7, Half ratio=0.76, Recency ratio=0.51
- Early IC=+0.1428, Recent IC=+0.0727, 1st-half IC=+0.1224, 2nd-half IC=+0.0929, Neg regimes=1/5
- Weak component: `yesterday_first_30min_return` (CV=1.04)
- Regime ICs: Q1_low_vol=-0.016, Q2=+0.090, Q3_mid=+0.108, Q4=+0.167, Q5_high_vol=+0.123

**`combo_min__star50_limit_proximity_early__first_bar_sentiment`** (Lock IC=+0.0935, Sharpe=+0.9488)
- Admission: Train IC=+0.2509, Deflated=+0.2487, IR=0.57, Mono=0.70, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.234 | 2016: +0.099 | 2017: -0.032 | 2018: +0.122 | 2019: +0.237 | 2020: +0.185 | 2021: +0.097 | 2022: +0.052 | 2023: +0.079 | 2024: +0.087 | 2025: +0.108 | 2026: +0.128
- Yearly Tail ICs:   2015: +0.234 | 2016: +0.139 | 2017: +0.087 | 2018: +0.282 | 2019: +0.391 | 2020: +0.231 | 2021: +0.155 | 2022: +0.198 | 2023: +0.089 | 2024: +0.328 | 2025: +0.173 | 2026: +0.330
- IC CV=0.65, Neg years (linear/tail)=1/0 of 7, Half ratio=1.32, Recency ratio=0.85
- Early IC=+0.1665, Recent IC=+0.1410, 1st-half IC=+0.1344, 2nd-half IC=+0.1770, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.079, Q2=+0.059, Q3_mid=+0.139, Q4=+0.189, Q5_high_vol=+0.203

**`combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0`** (Lock IC=+0.1157, Sharpe=+0.9454)
- Admission: Train IC=+0.2542, Deflated=+0.2517, IR=0.58, Mono=0.74, p=0.0000, MaxCorr=0.87
- Yearly Linear ICs: 2015: +0.252 | 2016: +0.113 | 2017: -0.005 | 2018: +0.153 | 2019: +0.238 | 2020: +0.149 | 2021: +0.127 | 2022: +0.102 | 2023: +0.135 | 2024: +0.074 | 2025: +0.153 | 2026: +0.092
- Yearly Tail ICs:   2015: +0.121 | 2016: +0.090 | 2017: +0.064 | 2018: +0.342 | 2019: +0.459 | 2020: +0.231 | 2021: +0.294 | 2022: +0.243 | 2023: +0.207 | 2024: +0.376 | 2025: +0.128 | 2026: +0.250
- IC CV=0.55, Neg years (linear/tail)=1/0 of 7, Half ratio=1.06, Recency ratio=0.76
- Early IC=+0.1819, Recent IC=+0.1375, 1st-half IC=+0.1625, 2nd-half IC=+0.1720, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.080, Q2=+0.056, Q3_mid=+0.120, Q4=+0.222, Q5_high_vol=+0.241

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.1160, Sharpe=+0.9206)
- Admission: Train IC=+0.2885, Deflated=+0.2864, IR=0.50, Mono=0.66, p=0.0000, MaxCorr=0.74
- Yearly Linear ICs: 2015: +0.233 | 2016: +0.175 | 2017: -0.028 | 2018: +0.143 | 2019: +0.206 | 2020: +0.138 | 2021: +0.124 | 2022: +0.090 | 2023: +0.137 | 2024: +0.080 | 2025: +0.169 | 2026: +0.082
- Yearly Tail ICs:   2015: +0.231 | 2016: +0.192 | 2017: +0.043 | 2018: +0.295 | 2019: +0.402 | 2020: +0.222 | 2021: +0.331 | 2022: +0.221 | 2023: +0.248 | 2024: +0.269 | 2025: +0.348 | 2026: +0.114
- IC CV=0.55, Neg years (linear/tail)=1/0 of 7, Half ratio=1.22, Recency ratio=0.64
- Early IC=+0.2037, Recent IC=+0.1310, 1st-half IC=+0.1387, 2nd-half IC=+0.1697, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.045, Q2=+0.051, Q3_mid=+0.182, Q4=+0.148, Q5_high_vol=+0.254

**`combo_min__rbreaker_sell_setup_proximity_early__first_bar_return`** (Lock IC=+0.1162, Sharpe=+0.8574)
- Admission: Train IC=+0.2476, Deflated=+0.2451, IR=0.56, Mono=0.74, p=0.0000, MaxCorr=0.96
- Yearly Linear ICs: 2015: +0.257 | 2016: +0.096 | 2017: -0.001 | 2018: +0.154 | 2019: +0.244 | 2020: +0.146 | 2021: +0.127 | 2022: +0.095 | 2023: +0.138 | 2024: +0.074 | 2025: +0.158 | 2026: +0.088
- Yearly Tail ICs:   2015: +0.146 | 2016: +0.065 | 2017: +0.091 | 2018: +0.299 | 2019: +0.509 | 2020: +0.204 | 2021: +0.252 | 2022: +0.247 | 2023: +0.205 | 2024: +0.404 | 2025: +0.152 | 2026: +0.258
- IC CV=0.56, Neg years (linear/tail)=1/0 of 7, Half ratio=1.05, Recency ratio=0.77
- Early IC=+0.1766, Recent IC=+0.1366, 1st-half IC=+0.1636, 2nd-half IC=+0.1714, Neg regimes=0/5
- Weak component: `rbreaker_sell_setup_proximity_early` (CV=0.47)
- Regime ICs: Q1_low_vol=+0.077, Q2=+0.062, Q3_mid=+0.121, Q4=+0.222, Q5_high_vol=+0.237

**`combo_clamp_diff__max_up_ret__demark_setup_reversal_early`** (Lock IC=+0.1222, Sharpe=+0.8295)
- Admission: Train IC=+0.2110, Deflated=+0.2093, IR=0.40, Mono=0.65, p=0.0000, MaxCorr=0.90
- Yearly Linear ICs: 2015: +0.193 | 2016: +0.029 | 2017: +0.020 | 2018: +0.081 | 2019: +0.180 | 2020: +0.093 | 2021: +0.157 | 2022: +0.156 | 2023: +0.147 | 2024: +0.062 | 2025: +0.190 | 2026: -0.020
- Yearly Tail ICs:   2015: +0.114 | 2016: +0.286 | 2017: +0.060 | 2018: +0.072 | 2019: +0.415 | 2020: +0.174 | 2021: +0.226 | 2022: +0.316 | 2023: +0.362 | 2024: -0.012 | 2025: +0.189 | 2026: -0.096
- IC CV=0.60, Neg years (linear/tail)=0/0 of 7, Half ratio=1.36, Recency ratio=1.12
- Early IC=+0.1110, Recent IC=+0.1247, 1st-half IC=+0.1068, 2nd-half IC=+0.1453, Neg regimes=0/5
- Weak component: `demark_setup_reversal_early` (CV=0.85)
- Regime ICs: Q1_low_vol=+0.034, Q2=+0.076, Q3_mid=+0.128, Q4=+0.193, Q5_high_vol=+0.151

**`combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0`** (Lock IC=+0.0983, Sharpe=+0.7513)
- Admission: Train IC=+0.2347, Deflated=+0.2324, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.94
- Yearly Linear ICs: 2015: +0.235 | 2016: +0.164 | 2017: -0.001 | 2018: +0.132 | 2019: +0.198 | 2020: +0.138 | 2021: +0.143 | 2022: +0.088 | 2023: +0.173 | 2024: +0.051 | 2025: +0.146 | 2026: -0.017
- Yearly Tail ICs:   2015: +0.134 | 2016: +0.168 | 2017: -0.009 | 2018: +0.274 | 2019: +0.369 | 2020: +0.240 | 2021: +0.259 | 2022: +0.223 | 2023: +0.543 | 2024: +0.240 | 2025: +0.088 | 2026: -0.072
- IC CV=0.48, Neg years (linear/tail)=1/1 of 7, Half ratio=1.22, Recency ratio=0.70
- Early IC=+0.1996, Recent IC=+0.1407, 1st-half IC=+0.1454, 2nd-half IC=+0.1772, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.052, Q2=+0.062, Q3_mid=+0.193, Q4=+0.137, Q5_high_vol=+0.255

**`combo_min__star50_limit_proximity_early__yesterday_first_30min_return`** (Lock IC=+0.1263, Sharpe=+0.6808)
- Admission: Train IC=+0.2510, Deflated=+0.2513, IR=0.53, Mono=0.70, p=0.0000, MaxCorr=0.61
- Yearly Linear ICs: 2015: +0.171 | 2016: +0.051 | 2017: -0.050 | 2018: +0.079 | 2019: +0.132 | 2020: +0.101 | 2021: +0.034 | 2022: +0.178 | 2023: +0.116 | 2024: +0.078 | 2025: +0.128 | 2026: +0.126
- Yearly Tail ICs:   2015: +0.193 | 2016: +0.190 | 2017: +0.027 | 2018: +0.354 | 2019: +0.280 | 2020: +0.401 | 2021: +0.167 | 2022: +0.459 | 2023: +0.095 | 2024: +0.032 | 2025: +0.061 | 2026: +0.267
- IC CV=0.90, Neg years (linear/tail)=1/0 of 7, Half ratio=0.89, Recency ratio=0.61
- Early IC=+0.1112, Recent IC=+0.0677, 1st-half IC=+0.0972, 2nd-half IC=+0.0869, Neg regimes=1/5
- Weak component: `yesterday_first_30min_return` (CV=1.04)
- Regime ICs: Q1_low_vol=-0.035, Q2=+0.057, Q3_mid=+0.071, Q4=+0.110, Q5_high_vol=+0.159

**`combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return`** (Lock IC=+0.1073, Sharpe=+0.6682)
- Admission: Train IC=+0.2707, Deflated=+0.2678, IR=0.67, Mono=0.70, p=0.0000, MaxCorr=0.93
- Yearly Linear ICs: 2015: +0.247 | 2016: +0.160 | 2017: +0.013 | 2018: +0.139 | 2019: +0.211 | 2020: +0.129 | 2021: +0.116 | 2022: +0.090 | 2023: +0.124 | 2024: +0.073 | 2025: +0.157 | 2026: +0.055
- Yearly Tail ICs:   2015: +0.153 | 2016: +0.124 | 2017: +0.137 | 2018: +0.273 | 2019: +0.414 | 2020: +0.204 | 2021: +0.255 | 2022: +0.186 | 2023: +0.201 | 2024: +0.364 | 2025: +0.212 | 2026: +0.144
- IC CV=0.48, Neg years (linear/tail)=0/0 of 7, Half ratio=1.04, Recency ratio=0.60
- Early IC=+0.2036, Recent IC=+0.1224, 1st-half IC=+0.1571, 2nd-half IC=+0.1638, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.088, Q2=+0.072, Q3_mid=+0.164, Q4=+0.131, Q5_high_vol=+0.251

**`combo_rank_max__max_up_ret__first_bar_return`** (Lock IC=+0.1018, Sharpe=+0.6644)
- Admission: Train IC=+0.2252, Deflated=+0.2233, IR=0.49, Mono=0.70, p=0.0000, MaxCorr=0.92
- Yearly Linear ICs: 2015: +0.179 | 2016: +0.144 | 2017: +0.039 | 2018: +0.090 | 2019: +0.170 | 2020: +0.123 | 2021: +0.182 | 2022: +0.107 | 2023: +0.162 | 2024: +0.076 | 2025: +0.169 | 2026: -0.062
- Yearly Tail ICs:   2015: +0.130 | 2016: +0.110 | 2017: +0.207 | 2018: +0.247 | 2019: +0.212 | 2020: +0.075 | 2021: +0.387 | 2022: +0.280 | 2023: +0.372 | 2024: +0.081 | 2025: +0.269 | 2026: -0.309
- IC CV=0.38, Neg years (linear/tail)=0/0 of 7, Half ratio=1.37, Recency ratio=0.94
- Early IC=+0.1619, Recent IC=+0.1525, 1st-half IC=+0.1223, 2nd-half IC=+0.1675, Neg regimes=0/5
- Weak component: `max_up_ret` (CV=0.41)
- Regime ICs: Q1_low_vol=+0.065, Q2=+0.082, Q3_mid=+0.198, Q4=+0.118, Q5_high_vol=+0.197

**`combo_mean__max_up_ret__bar_body_rng_0`** (Lock IC=+0.1047, Sharpe=+0.6577)
- Admission: Train IC=+0.2332, Deflated=+0.2310, IR=0.46, Mono=0.68, p=0.0000, MaxCorr=0.97
- Yearly Linear ICs: 2015: +0.219 | 2016: +0.148 | 2017: +0.003 | 2018: +0.124 | 2019: +0.196 | 2020: +0.131 | 2021: +0.157 | 2022: +0.092 | 2023: +0.174 | 2024: +0.059 | 2025: +0.170 | 2026: -0.029
- Yearly Tail ICs:   2015: +0.129 | 2016: +0.168 | 2017: -0.009 | 2018: +0.274 | 2019: +0.369 | 2020: +0.240 | 2021: +0.259 | 2022: +0.223 | 2023: +0.543 | 2024: +0.193 | 2025: +0.088 | 2026: -0.072
- IC CV=0.46, Neg years (linear/tail)=0/1 of 7, Half ratio=1.29, Recency ratio=0.78
- Early IC=+0.1833, Recent IC=+0.1438, 1st-half IC=+0.1363, 2nd-half IC=+0.1754, Neg regimes=0/5
- Weak component: `bar_body_rng_0` (CV=0.51)
- Regime ICs: Q1_low_vol=+0.048, Q2=+0.070, Q3_mid=+0.195, Q4=+0.141, Q5_high_vol=+0.232

**`combo_min__opening_drive_thrust_ratio__first_bar_sentiment`** (Lock IC=+0.0982, Sharpe=+0.4585)
- Admission: Train IC=+0.2664, Deflated=+0.2647, IR=0.54, Mono=0.70, p=0.0000, MaxCorr=0.84
- Yearly Linear ICs: 2015: +0.206 | 2016: +0.119 | 2017: +0.008 | 2018: +0.139 | 2019: +0.195 | 2020: +0.134 | 2021: +0.129 | 2022: +0.096 | 2023: +0.156 | 2024: +0.056 | 2025: +0.133 | 2026: +0.009
- Yearly Tail ICs:   2015: +0.449 | 2016: -0.281 | 2017: +0.141 | 2018: +0.295 | 2019: +0.401 | 2020: +0.186 | 2021: +0.241 | 2022: +0.196 | 2023: +0.326 | 2024: +0.106 | 2025: +0.285 | 2026: +0.049
- IC CV=0.45, Neg years (linear/tail)=0/1 of 7, Half ratio=1.46, Recency ratio=0.81
- Early IC=+0.1621, Recent IC=+0.1314, 1st-half IC=+0.1149, 2nd-half IC=+0.1672, Neg regimes=0/5
- Weak component: `first_bar_sentiment` (CV=0.70)
- Regime ICs: Q1_low_vol=+0.049, Q2=+0.043, Q3_mid=+0.200, Q4=+0.129, Q5_high_vol=+0.215

**`combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector`** (Lock IC=+0.1152, Sharpe=+0.4306)
- Admission: Train IC=+0.1683, Deflated=+0.1674, IR=0.47, Mono=0.70, p=0.0024, MaxCorr=0.11
- Yearly Linear ICs: 2015: +0.187 | 2016: +0.009 | 2017: +0.011 | 2018: +0.090 | 2019: +0.130 | 2020: +0.055 | 2021: +0.087 | 2022: +0.139 | 2023: +0.083 | 2024: +0.083 | 2025: +0.120 | 2026: +0.148
- Yearly Tail ICs:   2015: +0.222 | 2016: -0.017 | 2017: +0.138 | 2018: +0.257 | 2019: +0.117 | 2020: +0.189 | 2021: +0.114 | 2022: +0.057 | 2023: -0.092 | 2024: +0.146 | 2025: +0.162 | 2026: +0.240
- IC CV=0.73, Neg years (linear/tail)=0/1 of 7, Half ratio=0.82, Recency ratio=0.73
- Early IC=+0.0981, Recent IC=+0.0711, 1st-half IC=+0.1115, 2nd-half IC=+0.0914, Neg regimes=0/5
- Weak component: `star50_limit_proximity_early` (CV=0.77)
- Regime ICs: Q1_low_vol=+0.072, Q2=+0.004, Q3_mid=+0.061, Q4=+0.194, Q5_high_vol=+0.118

**`combo_rank_max__opening_drive_thrust_ratio__first_bar_return`** (Lock IC=+0.0977, Sharpe=+0.4121)
- Admission: Train IC=+0.2105, Deflated=+0.2079, IR=0.47, Mono=0.66, p=0.0000, MaxCorr=0.89
- Yearly Linear ICs: 2015: +0.212 | 2016: +0.115 | 2017: +0.028 | 2018: +0.107 | 2019: +0.198 | 2020: +0.109 | 2021: +0.153 | 2022: +0.071 | 2023: +0.183 | 2024: +0.085 | 2025: +0.136 | 2026: -0.013
- Yearly Tail ICs:   2015: +0.327 | 2016: -0.015 | 2017: +0.187 | 2018: +0.304 | 2019: +0.229 | 2020: +0.099 | 2021: +0.324 | 2022: +0.124 | 2023: +0.387 | 2024: +0.089 | 2025: +0.255 | 2026: -0.089
- IC CV=0.45, Neg years (linear/tail)=0/1 of 7, Half ratio=1.30, Recency ratio=0.80
- Early IC=+0.1638, Recent IC=+0.1314, 1st-half IC=+0.1256, 2nd-half IC=+0.1637, Neg regimes=0/5
- Weak component: `opening_drive_thrust_ratio` (CV=0.52)
- Regime ICs: Q1_low_vol=+0.013, Q2=+0.084, Q3_mid=+0.165, Q4=+0.107, Q5_high_vol=+0.250

**`combo_max__max_up_ret__first_bar_return`** (Lock IC=+0.1009, Sharpe=+0.3747)
- Admission: Train IC=+0.2224, Deflated=+0.2203, IR=0.51, Mono=0.71, p=0.0000, MaxCorr=0.93
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
| `star50_limit_proximity_early` | TP | persistent | +0.0972 | +0.0305 | +0.1617 | 1y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0951 | +0.0914 | +0.0035 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0841 | +0.1076 | +0.0389 | 2y |
| `combo_min__volume_weighted_price_position__volume_surge_direction` | TP | gradual | +0.0803 | +0.1671 | -0.0552 | 2y |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0791 | +0.1124 | -0.0314 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__bar_ret_0` | TP | gradual | +0.0768 | +0.1262 | -0.0444 | 2y |
| `combo_tri_mean__star50_limit_proximity_early__first_bar_return__opening_drive_thrust_ratio` | TP | gradual | +0.0748 | +0.1457 | -0.0578 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0698 | +0.1315 | -0.0087 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0697 | +0.1318 | -0.0088 | 2y |
| `combo_z_sum__opening_drive_thrust_ratio__limit_down_proximity_early` | TP | gradual | +0.0671 | +0.1038 | -0.0242 | 2y |
| `combo_z_sum__opening_drive_thrust_ratio__rbreaker_buy_setup_proximity_early` | TP | gradual | +0.0671 | +0.1038 | -0.0242 | 2y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | TP | gradual | +0.0660 | +0.1225 | -0.0794 | 2y |
| `combo_mean__bar_ret_0__volume_weighted_price_position` | TP | gradual | +0.0657 | +0.1873 | -0.1414 | 2y |
| `combo_mean__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.0656 | +0.1873 | -0.1418 | 2y |
| `combo_max__bar_body_rng_0__volume_surge_direction` | TP | gradual | +0.0580 | +0.1547 | -0.0925 | 4y |
| `combo_tri_max__first_bar_return__volume_weighted_price_position__bar_body_rng_0` | Median | gradual | +0.0574 | +0.1761 | -0.1439 | 2y |
| `combo_rank_max__bar_ret_0__volume_weighted_price_position` | TP | gradual | +0.0565 | +0.1894 | -0.1718 | 2y |
| `combo_mean__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0563 | +0.1922 | -0.1808 | 2y |
| `combo_min__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0561 | +0.1743 | -0.1434 | 2y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_ret_0__bar_body_rng_0` | TP | gradual | +0.0520 | +0.1676 | -0.0321 | 4y |
| `combo_min__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0488 | +0.1776 | -0.0792 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0` | TP | persistent | +0.0468 | +0.1703 | +0.0010 | 4y |
| `combo_tri_max__max_up_ret__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.0447 | +0.1960 | -0.2064 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | gradual | +0.0440 | +0.1405 | -0.0163 | 4y |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | TP | gradual | +0.0417 | +0.1628 | -0.0038 | 4y |
| `combo_max__first_bar_return__bar_body_rng_0` | TP | gradual | +0.0392 | +0.1418 | -0.0760 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0376 | +0.1765 | -0.0345 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | gradual | +0.0369 | +0.1355 | -0.0350 | 4y |
| `combo_rank_max__max_up_ret__volume_weighted_price_position` | TP | gradual | +0.0365 | +0.1982 | -0.1888 | 4y |
| `combo_ratio__first_bar_return__volume_weighted_price_position` | TP | gradual | +0.0365 | +0.1422 | -0.1087 | 4y |
| `combo_mean__max_up_ret__volume_surge_direction` | TP | gradual | +0.0341 | +0.1595 | -0.1061 | 4y |
| `combo_tri_min__max_up_ret__bar_body_rng_0__opening_drive_thrust_ratio` | Median | gradual | +0.0339 | +0.1634 | -0.1046 | 4y |
| `combo_rank_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early` | TP | persistent | +0.0316 | +0.1375 | +0.0421 | ∞ |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0286 | +0.1729 | -0.1098 | 4y |
| `combo_ratio__bar_body_rng_0__volume_weighted_price_position` | TP | gradual | +0.0283 | +0.1374 | -0.0976 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__bar_body_rng_0__opening_drive_thrust_ratio` | TP | gradual | +0.0281 | +0.1410 | -0.0501 | 4y |
| `combo_ratio__opening_drive_thrust_ratio__volume_weighted_price_position` | Median | gradual | +0.0251 | +0.1565 | -0.1845 | 4y |
| `combo_ratio__first_bar_sentiment__volume_surge_direction` | Median | gradual | +0.0185 | +0.0578 | -0.0352 | 2y |
| `combo_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.0183 | +0.1596 | -0.0780 | 4y |
| `combo_clamp_diff__max_up_ret__early_vwap_acceleration` | TP | gradual | +0.0168 | +0.1601 | -0.0787 | 4y |
| `combo_sig_product__volume_weighted_price_position__opening_drive_thrust_ratio` | Median | gradual | +0.0156 | +0.1733 | -0.1061 | 4y |
| `combo_z_sum__max_up_ret__opening_drive_thrust_ratio` | Median | gradual | +0.0148 | +0.1624 | -0.1651 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__opening_drive_thrust_ratio` | TP | gradual | +0.0115 | +0.1387 | -0.0735 | 4y |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=38, persistent=6

### 500ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1531 | +0.0885 | +0.0772 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.1453 | +0.0865 | +0.0343 | 4y |
| `combo_sig_product__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1448 | +0.1477 | +0.0264 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1402 | +0.0834 | +0.1093 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1381 | +0.0885 | +0.1172 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.1362 | +0.0844 | +0.1543 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.1326 | +0.0846 | +0.0633 | 2y |
| `combo_rank_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1314 | +0.0791 | +0.1433 | ∞ |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.1284 | +0.0654 | +0.0974 | ∞ |
| `combo_max__volatility_expansion_trend_vector__first_bar_sentiment` | TP | gradual | +0.1280 | +0.0528 | -0.0499 | 1y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__body_size_progression` | TP | gradual | +0.1278 | +0.0960 | -0.0439 | 4y |
| `combo_rank_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1272 | +0.0957 | -0.0533 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1259 | +0.0976 | -0.0110 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1254 | +0.0728 | +0.0650 | ∞ |
| `combo_rank_max__close_vs_open_range__bar_ret_0` | TP | gradual | +0.1240 | +0.0878 | -0.0964 | 4y |
| `combo_max__close_vs_open_range__first_bar_sentiment` | TP | gradual | +0.1235 | +0.0617 | -0.0597 | 1y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.1235 | +0.0987 | +0.0916 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__early_body_momentum` | TP | persistent | +0.1234 | +0.0713 | +0.0644 | ∞ |
| `combo_max__close_vs_open_range__bar_ret_0` | TP | gradual | +0.1231 | +0.0850 | -0.0909 | 4y |
| `combo_rank_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1226 | +0.0721 | +0.1294 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.1213 | +0.1338 | -0.0326 | 4y |
| `combo_sig_product__max_up_ret__bar_ret_0` | TP | persistent | +0.1204 | +0.0511 | +0.0069 | 1y |
| `combo_max__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1204 | +0.0726 | +0.1121 | ∞ |
| `combo_sig_product__max_up_ret__first_bar_return` | TP | persistent | +0.1200 | +0.0510 | +0.0076 | 1y |
| `combo_sig_product__opening_drive_thrust_ratio__net_volume_flow` | TP | gradual | +0.1192 | +0.1078 | -0.0038 | 4y |
| `combo_max__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1186 | +0.0712 | +0.1193 | ∞ |
| `combo_mean__first_bar_sentiment__early_body_momentum` | TP | gradual | +0.1184 | +0.0750 | -0.0607 | 4y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | TP | persistent | +0.1178 | +0.0802 | +0.0526 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.1176 | +0.0753 | +0.1381 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1171 | +0.1454 | -0.0314 | 3y |
| `combo_sig_product__max_up_ret__close_vs_open_range` | TP | persistent | +0.1162 | +0.1552 | +0.0293 | 4y |
| `combo_max__max_up_ret__close_vs_open_range` | TP | gradual | +0.1161 | +0.0966 | -0.0465 | 4y |
| `combo_max__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.1159 | +0.0796 | -0.0265 | 4y |
| `combo_rank_max__max_up_ret__close_vs_open_range` | TP | gradual | +0.1159 | +0.0940 | -0.0318 | 4y |
| `combo_sig_product__max_up_ret__early_body_momentum` | TP | persistent | +0.1155 | +0.1363 | +0.0142 | 4y |
| `combo_min__max_up_ret__high_low_sequence_momentum` | TP | gradual | +0.1147 | +0.1160 | -0.0892 | 4y |
| `combo_min__max_up_ret__trend_day_regime_conviction` | TP | gradual | +0.1138 | +0.1158 | -0.0911 | 4y |
| `combo_max__max_up_ret__early_body_momentum` | TP | gradual | +0.1130 | +0.0872 | -0.0648 | 4y |
| `combo_tri_max__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1125 | +0.0604 | +0.0944 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.1120 | +0.0828 | +0.0483 | 4y |
| `combo_mean__net_volume_flow__first_bar_sentiment` | TP | gradual | +0.1114 | +0.0838 | -0.0349 | 4y |
| `combo_max__first_bar_sentiment__bar_ret_0` | TP | persistent | +0.1112 | +0.0471 | +0.0176 | 1y |
| `combo_max__opening_drive_thrust_ratio__early_body_momentum` | TP | gradual | +0.1102 | +0.0750 | -0.0470 | 4y |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1096 | +0.0720 | +0.1204 | ∞ |
| `combo_min__max_up_ret__first_bar_sentiment` | Median | gradual | +0.1091 | +0.0724 | -0.0110 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__early_body_momentum` | TP | gradual | +0.1086 | +0.0729 | -0.0533 | 4y |
| `combo_mean__max_up_ret__close_vs_open_range` | TP | gradual | +0.1081 | +0.1038 | -0.0698 | 4y |
| `combo_tri_max__opening_drive_thrust_ratio__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1078 | +0.0897 | -0.0652 | 4y |
| `combo_mean__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1077 | +0.1118 | -0.1047 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1059 | +0.0694 | +0.1242 | ∞ |
| `combo_mean__max_up_ret__first_bar_sentiment` | TP | gradual | +0.1059 | +0.0854 | -0.0252 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1058 | +0.0689 | +0.1240 | ∞ |
| `combo_sig_product__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1053 | +0.0568 | +0.2040 | ∞ |
| `combo_rank_max__max_up_ret__net_volume_flow` | TP | gradual | +0.1048 | +0.0965 | -0.0129 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__trend_bar_close_consistency` | TP | gradual | +0.1044 | +0.1170 | -0.0482 | 4y |
| `net_volume_flow` | TP | gradual | +0.1043 | +0.0882 | -0.0580 | 4y |
| `combo_mean__close_vs_open_range__first_bar_sentiment` | TP | gradual | +0.1039 | +0.0788 | -0.0471 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__smooth_momentum_structure` | TP | gradual | +0.1037 | +0.0692 | -0.0092 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1036 | +0.0856 | +0.1265 | ∞ |
| `combo_mean__net_volume_flow__bar_ret_0` | TP | gradual | +0.1034 | +0.0779 | -0.0348 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1032 | +0.0847 | -0.0341 | 3y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.1027 | +0.1068 | +0.0004 | 4y |
| `combo_rank_min__max_up_ret__first_bar_sentiment` | Median | gradual | +0.1024 | +0.0725 | -0.0114 | 4y |
| `combo_max__net_volume_flow__first_bar_sentiment` | Median | gradual | +0.1020 | +0.0603 | -0.0370 | 4y |
| `combo_max__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1016 | +0.0609 | +0.0950 | ∞ |
| `combo_mean__net_volume_flow__close_vs_open_range` | TP | gradual | +0.1015 | +0.0878 | -0.0722 | 4y |
| `combo_mean__max_up_ret__first_bar_return` | TP | gradual | +0.1010 | +0.0957 | -0.0328 | 4y |
| `combo_max__close_vs_open_range__early_body_momentum` | Median | gradual | +0.0998 | +0.0778 | -0.1041 | 4y |
| `combo_max__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0997 | +0.0891 | -0.0230 | 4y |
| `combo_max__opening_drive_thrust_ratio__bar_ret_0` | Median | gradual | +0.0997 | +0.1068 | -0.0124 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__net_volume_flow` | TP | gradual | +0.0989 | +0.0784 | -0.0139 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0986 | +0.0741 | +0.0837 | ∞ |
| `combo_sig_product__close_vs_open_range__early_body_momentum` | TP | gradual | +0.0982 | +0.0622 | -0.1110 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.0979 | +0.1096 | +0.0169 | 4y |
| `combo_rank_min__trend_bar_close_consistency__close_vs_open_range` | TP | gradual | +0.0978 | +0.0806 | -0.0792 | 4y |
| `combo_min__close_vs_open_range__high_low_sequence_momentum` | TP | gradual | +0.0972 | +0.0791 | -0.0733 | 4y |
| `combo_rank_max__net_volume_flow__first_bar_return` | TP | gradual | +0.0971 | +0.0787 | -0.0805 | 4y |
| `combo_sig_product__close_vs_open_range__high_low_sequence_momentum` | TP | gradual | +0.0969 | +0.0708 | -0.0670 | 4y |
| `high_low_sequence_momentum` | TP | gradual | +0.0967 | +0.0715 | -0.0668 | 4y |
| `combo_ratio__max_down_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0965 | +0.0456 | +0.0404 | 1y |
| `combo_sig_product__first_bar_sentiment__early_body_momentum` | TP | gradual | +0.0964 | +0.0699 | -0.0186 | 4y |
| `combo_mean__close_vs_open_range__first_bar_return` | TP | gradual | +0.0963 | +0.0803 | -0.0376 | 4y |
| `combo_mean__close_vs_open_range__bar_ret_0` | TP | gradual | +0.0963 | +0.0804 | -0.0365 | 4y |
| `max_up_ret` | TP | gradual | +0.0954 | +0.1044 | -0.0291 | 4y |
| `combo_rank_max__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.0947 | +0.0502 | +0.0721 | ∞ |
| `combo_rank_max__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0946 | +0.0342 | +0.1471 | 1y |
| `morning_volume_weighted_momentum` | TP | gradual | +0.0945 | +0.0957 | -0.0906 | 4y |
| `combo_max__net_volume_flow__bar_ret_0` | Median | gradual | +0.0942 | +0.0744 | -0.0693 | 4y |
| `combo_min__trend_day_regime_conviction__close_vs_open_range` | TP | gradual | +0.0942 | +0.0803 | -0.0763 | 4y |
| `first_30min_return` | TP | gradual | +0.0940 | +0.0954 | -0.1128 | 4y |
| `open_to_current_return` | TP | gradual | +0.0940 | +0.0954 | -0.1128 | 4y |
| `combo_sig_product__max_up_ret__early_late_momentum_divergence` | Median | persistent | +0.0939 | +0.0806 | +0.0872 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.0936 | +0.1057 | -0.0337 | 4y |
| `trend_day_regime_conviction` | TP | gradual | +0.0936 | +0.0810 | -0.0704 | 4y |
| `combo_max__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.0934 | +0.0884 | +0.0187 | 4y |
| `combo_rank_max__bar_ret_0__max_down_ret` | TP | persistent | +0.0934 | +0.0371 | +0.0319 | 1y |
| `combo_mean__volatility_expansion_trend_vector__close_vs_open_range` | TP | gradual | +0.0929 | +0.0892 | -0.0739 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.0929 | +0.1103 | -0.0440 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__bar_ret_0` | TP | gradual | +0.0924 | +0.1106 | -0.0113 | 4y |
| `rbreaker_sell_setup_proximity_early` | TP | persistent | +0.0921 | +0.0793 | +0.1842 | ∞ |
| `combo_mean__net_volume_flow__max_down_ret` | TP | gradual | +0.0916 | +0.0763 | -0.0107 | 4y |
| `combo_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.0914 | +0.1007 | -0.0668 | 4y |
| `combo_mean__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0910 | +0.0577 | +0.0902 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | gradual | +0.0909 | +0.1304 | -0.0189 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.0907 | +0.0969 | +0.0462 | ∞ |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.0903 | +0.0849 | +0.0811 | ∞ |
| `combo_rank_max__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0903 | +0.0410 | +0.0778 | 1y |
| `combo_min__net_volume_flow__bar_ret_0` | TP | gradual | +0.0901 | +0.0817 | -0.0100 | 4y |
| `combo_min__net_volume_flow__first_bar_return` | TP | gradual | +0.0900 | +0.0816 | -0.0091 | 4y |
| `combo_mean__trend_bar_close_consistency__first_bar_return` | TP | gradual | +0.0893 | +0.0887 | -0.0712 | 4y |
| `combo_mean__trend_bar_close_consistency__bar_ret_0` | TP | gradual | +0.0891 | +0.0886 | -0.0709 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__net_volume_flow` | TP | persistent | +0.0888 | +0.1089 | +0.0364 | 4y |
| `combo_sig_product__max_up_ret__trend_bar_close_consistency` | TP | persistent | +0.0885 | +0.1234 | +0.0058 | 4y |
| `combo_min__close_vs_open_range__max_down_ret` | TP | persistent | +0.0884 | +0.0859 | +0.0238 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0876 | +0.1145 | -0.0032 | 4y |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0876 | +0.1054 | +0.0873 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | gradual | +0.0874 | +0.0997 | -0.0347 | 4y |
| `combo_rank_max__max_up_ret__first_bar_return` | TP | gradual | +0.0873 | +0.0994 | -0.0695 | 4y |
| `combo_min__max_up_ret__bar_ret_0` | TP | persistent | +0.0871 | +0.0958 | +0.0056 | 4y |
| `combo_min__max_up_ret__first_bar_return` | TP | persistent | +0.0871 | +0.0954 | +0.0048 | 4y |
| `combo_max__bar_ret_0__max_down_ret` | TP | gradual | +0.0865 | +0.0449 | -0.0028 | 4y |
| `combo_max__first_bar_return__max_down_ret` | TP | gradual | +0.0864 | +0.0447 | -0.0031 | 4y |
| `combo_tri_min__opening_drive_thrust_ratio__max_up_ret__net_volume_flow` | TP | gradual | +0.0857 | +0.1275 | -0.0551 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__early_late_momentum_divergence` | Median | persistent | +0.0854 | +0.1533 | +0.1016 | 3y |
| `combo_mean__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.0851 | +0.0899 | +0.0024 | 4y |
| `or_fill_ratio` | TP | gradual | +0.0850 | +0.0827 | -0.0762 | 4y |
| `combo_mean__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.0849 | +0.0897 | +0.0027 | 4y |
| `combo_sig_product__net_volume_flow__close_vs_open_range` | TP | gradual | +0.0849 | +0.0964 | -0.0638 | 4y |
| `combo_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.0838 | +0.0863 | -0.0692 | 4y |
| `combo_rank_min__net_volume_flow__max_down_ret` | TP | persistent | +0.0835 | +0.0755 | +0.0221 | 4y |
| `combo_tri_mean__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0831 | +0.0824 | +0.0625 | ∞ |
| `star50_limit_proximity_early` | TP | persistent | +0.0825 | +0.0715 | +0.1859 | ∞ |
| `combo_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0824 | +0.0767 | +0.0885 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0824 | +0.0702 | +0.1054 | ∞ |
| `combo_tri_median__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | TP | gradual | +0.0822 | +0.1327 | -0.0071 | 4y |
| `combo_max__max_up_ret__bar_ret_0` | TP | gradual | +0.0822 | +0.0784 | -0.0688 | 4y |
| `combo_mean__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0822 | +0.0702 | +0.1055 | ∞ |
| `combo_max__max_up_ret__first_bar_return` | TP | gradual | +0.0821 | +0.0786 | -0.0695 | 4y |
| `combo_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0819 | +0.0775 | +0.0041 | 4y |
| `combo_rank_min__first_bar_sentiment__early_body_momentum` | Median | persistent | +0.0817 | +0.0582 | +0.0021 | 4y |
| `combo_mean__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.0801 | +0.1003 | -0.0345 | 4y |
| `combo_rank_min__net_volume_flow__close_vs_open_range` | TP | gradual | +0.0791 | +0.0931 | -0.0697 | 4y |
| `combo_mean__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0785 | +0.0606 | +0.1007 | ∞ |
| `combo_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.0783 | +0.0829 | +0.1265 | ∞ |
| `combo_mean__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0783 | +0.0914 | +0.0181 | 4y |
| `combo_rank_min__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0780 | +0.0817 | +0.0430 | ∞ |
| `combo_rank_min__close_vs_open_range__max_down_ret` | TP | persistent | +0.0776 | +0.0834 | +0.0324 | 4y |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0775 | +0.0385 | +0.2029 | 1y |
| `combo_tri_mean__opening_drive_thrust_ratio__star50_limit_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0775 | +0.0835 | +0.0381 | 4y |
| `combo_rank_max__trend_bar_close_consistency__close_vs_open_range` | TP | gradual | +0.0773 | +0.0898 | -0.1101 | 4y |
| `combo_mean__first_bar_sentiment__max_down_ret` | TP | persistent | +0.0768 | +0.0321 | +0.0255 | 1y |
| `combo_sig_product__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0756 | +0.0530 | +0.0807 | ∞ |
| `combo_rank_min__max_up_ret__close_vs_open_range` | TP | gradual | +0.0746 | +0.0893 | -0.0622 | 4y |
| `combo_z_sum__trend_bar_close_consistency__max_down_ret` | TP | gradual | +0.0738 | +0.0767 | -0.0605 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__net_volume_flow` | TP | persistent | +0.0718 | +0.0914 | +0.0770 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment` | TP | persistent | +0.0701 | +0.0496 | +0.0708 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__volatility_expansion_trend_vector` | TP | persistent | +0.0700 | +0.1166 | +0.0317 | 4y |
| `opening_drive_thrust_ratio` | TP | persistent | +0.0695 | +0.1017 | +0.0025 | 4y |
| `combo_rank_min__trend_bar_close_consistency__bar_ret_0` | TP | gradual | +0.0685 | +0.0629 | -0.0013 | 4y |
| `combo_mean__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0677 | +0.0745 | +0.1195 | ∞ |
| `combo_min__first_bar_sentiment__bar_ret_0` | TP | gradual | +0.0671 | +0.0698 | -0.0193 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0670 | +0.0655 | +0.1730 | ∞ |
| `combo_rank_min__max_up_ret__bar_ret_0` | TP | persistent | +0.0669 | +0.0747 | +0.0015 | 4y |
| `vwap_trend_channel_slope` | TP | gradual | +0.0667 | +0.1186 | -0.0312 | 4y |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | TP | gradual | +0.0663 | +0.0887 | -0.0124 | 4y |
| `combo_rank_min__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0653 | +0.0829 | +0.0886 | ∞ |
| `combo_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.0653 | +0.0991 | +0.0144 | 4y |
| `combo_rel_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0646 | +0.0927 | +0.1059 | ∞ |
| `combo_rank_min__first_bar_sentiment__bar_ret_0` | TP | gradual | +0.0645 | +0.0576 | -0.0261 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0644 | +0.1466 | +0.0959 | ∞ |
| `combo_min__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | gradual | +0.0644 | +0.0990 | -0.0554 | 4y |
| `combo_sig_product__max_up_ret__body_size_progression` | TP | persistent | +0.0643 | +0.0644 | +0.0777 | ∞ |
| `combo_min__close_vs_open_range__first_bar_sentiment` | TP | gradual | +0.0642 | +0.0572 | -0.0130 | 4y |
| `combo_clamp_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0638 | +0.1017 | +0.0968 | 3y |
| `combo_diff__max_up_ret__body_size_progression` | TP | persistent | +0.0634 | +0.1007 | +0.0929 | 3y |
| `first_bar_return` | TP | gradual | +0.0630 | +0.0618 | -0.0114 | 4y |
| `combo_sig_product__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0626 | +0.0952 | +0.1864 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0624 | +0.0683 | +0.1045 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0614 | +0.0983 | +0.0722 | ∞ |
| `combo_mean__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0601 | +0.0400 | +0.1214 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.0601 | +0.0725 | +0.0037 | 4y |
| `combo_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0598 | +0.1187 | -0.0151 | 4y |
| `combo_clamp_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0597 | +0.0920 | +0.1078 | 3y |
| `combo_rank_min__star50_limit_proximity_early__max_down_ret` | TP | persistent | +0.0591 | +0.0645 | +0.0839 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__trend_bar_close_consistency` | TP | persistent | +0.0586 | +0.0991 | +0.0265 | 4y |
| `combo_max__early_body_momentum__max_down_ret` | TP | gradual | +0.0585 | +0.0411 | -0.0906 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__first_bar_return` | TP | persistent | +0.0582 | +0.1339 | +0.0379 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.0580 | +0.1339 | +0.0377 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0574 | +0.0957 | +0.0747 | ∞ |
| `bar_body_rng_0` | Median | persistent | +0.0574 | +0.0682 | +0.0133 | 4y |
| `combo_rel_diff__net_volume_flow__volume_weighted_momentum_acceleration` | TP | persistent | +0.0572 | +0.0926 | +0.0020 | 4y |
| `combo_diff__max_up_ret__early_late_momentum_divergence` | TP | persistent | +0.0570 | +0.0915 | +0.1035 | 3y |
| `combo_rel_diff__max_up_ret__trend_bar_close_consistency` | TP | fast | +0.0569 | -0.0039 | +0.1243 | 1y |
| `combo_min__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.0569 | +0.1085 | +0.0537 | ∞ |
| `combo_rank_min__first_bar_sentiment__max_down_ret` | Median | persistent | +0.0553 | +0.0273 | +0.0177 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__bar_ret_0` | TP | persistent | +0.0553 | +0.0608 | +0.0050 | 4y |
| `combo_rank_max__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0552 | +0.0654 | +0.0031 | 4y |
| `combo_clamp_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0551 | +0.1026 | +0.0853 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__body_size_progression` | TP | persistent | +0.0549 | +0.0966 | +0.0973 | ∞ |
| `combo_sig_product__net_volume_flow__bar_ret_0` | TP | gradual | +0.0529 | +0.0620 | -0.0584 | 4y |
| `combo_sig_product__net_volume_flow__first_bar_return` | TP | gradual | +0.0528 | +0.0622 | -0.0583 | 4y |
| `combo_clamp_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0522 | +0.0948 | +0.0092 | 4y |
| `combo_diff__max_up_ret__volume_weighted_momentum_acceleration` | TP | persistent | +0.0519 | +0.0996 | +0.0133 | 4y |
| `combo_rel_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0515 | +0.0669 | +0.2407 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0510 | +0.1068 | +0.0938 | ∞ |
| `combo_rel_diff__max_up_ret__late_bar_momentum` | TP | persistent | +0.0495 | +0.0817 | +0.1019 | ∞ |
| `combo_rank_min__volatility_expansion_trend_vector__bar_ret_0` | TP | persistent | +0.0494 | +0.0677 | +0.0070 | 4y |
| `combo_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0472 | +0.0604 | +0.1725 | ∞ |
| `combo_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0468 | +0.0623 | +0.2560 | 3y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0468 | +0.0777 | +0.0807 | ∞ |
| `combo_min__opening_drive_thrust_ratio__close_vs_open_range` | TP | gradual | +0.0464 | +0.1094 | -0.0300 | 4y |
| `combo_clamp_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0458 | +0.1039 | +0.0103 | 4y |
| `combo_clamp_diff__star50_limit_proximity_early__body_size_progression` | TP | persistent | +0.0456 | +0.0640 | +0.2575 | 3y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__volatility_expansion_trend_vector` | TP | persistent | +0.0454 | +0.1141 | +0.0491 | ∞ |
| `combo_clamp_diff__star50_limit_proximity_early__volume_weighted_momentum_acceleration` | TP | persistent | +0.0453 | +0.0591 | +0.1708 | ∞ |
| `combo_min__close_vs_open_range__bar_ret_0` | TP | persistent | +0.0446 | +0.0704 | +0.0151 | 4y |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow` | TP | persistent | +0.0445 | +0.1069 | +0.0508 | ∞ |
| `combo_rank_min__close_vs_open_range__bar_ret_0` | TP | persistent | +0.0440 | +0.0688 | +0.0162 | 4y |
| `combo_rank_min__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.0439 | +0.1119 | -0.0057 | 4y |
| `combo_sig_product__opening_drive_thrust_ratio__volume_weighted_momentum_acceleration` | TP | persistent | +0.0437 | +0.0760 | +0.0636 | ∞ |
| `combo_min__bar_ret_0__max_down_ret` | TP | persistent | +0.0414 | +0.0536 | +0.0163 | 4y |
| `combo_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0402 | +0.1000 | +0.0763 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.0400 | +0.0807 | +0.0787 | ∞ |
| `combo_sig_product__opening_drive_thrust_ratio__max_down_ret` | TP | persistent | +0.0396 | +0.1063 | +0.0355 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__close_vs_open_range` | TP | persistent | +0.0392 | +0.0958 | +0.0770 | ∞ |
| `combo_rel_diff__max_up_ret__smooth_momentum_structure` | TP | persistent | +0.0372 | +0.1012 | +0.0503 | ∞ |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.0350 | +0.1025 | +0.0952 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.0346 | +0.1057 | +0.1085 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0346 | +0.0635 | +0.0789 | ∞ |
| `combo_rel_diff__max_up_ret__early_body_momentum` | TP | persistent | +0.0342 | +0.0018 | +0.0960 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__late_bar_momentum` | TP | persistent | +0.0338 | +0.0978 | +0.1118 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__smooth_momentum_structure` | TP | persistent | +0.0316 | +0.0984 | +0.0405 | ∞ |
| `combo_min__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | TP | gradual | +0.0315 | +0.0144 | -0.0292 | 1y |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0309 | +0.0978 | +0.0991 | ∞ |
| `combo_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio` | TP | persistent | +0.0307 | +0.0999 | +0.0913 | ∞ |
| `combo_tri_min__opening_drive_thrust_ratio__net_volume_flow__star50_limit_proximity_early` | TP | persistent | +0.0285 | +0.1013 | +0.0697 | ∞ |
| `combo_rank_min__bar_ret_0__max_down_ret` | TP | persistent | +0.0284 | +0.0565 | +0.0077 | 4y |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0279 | +0.0649 | +0.0855 | ∞ |
| `combo_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0275 | +0.0650 | +0.0856 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__max_up_ret` | TP | persistent | +0.0159 | +0.1070 | +0.0843 | ∞ |
| `combo_diff__max_up_ret__trend_bar_close_consistency` | FP | fast | +0.0127 | -0.0386 | +0.1126 | 1y |
| `combo_clamp_diff__max_up_ret__trend_bar_close_consistency` | FP | fast | +0.0125 | -0.0386 | +0.1128 | 1y |
| `combo_rel_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | TP | persistent | +0.0093 | +0.0168 | +0.1802 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__double_bottom_bull_flag_early` | TP | persistent | +0.0063 | +0.1139 | +0.0526 | ∞ |
| `combo_rel_diff__opening_drive_thrust_ratio__early_body_momentum` | Median | immediate | -0.0019 | +0.0216 | +0.1722 | ∞ |
| `combo_clamp_diff__opening_drive_thrust_ratio__trend_bar_close_consistency` | Median | immediate | -0.0068 | +0.0110 | +0.1873 | ∞ |
| `combo_ratio__max_down_ret__volatility_expansion_trend_vector` | TP | immediate | -0.0168 | -0.0247 | +0.1016 | ∞ |
| `combo_ratio__max_down_ret__net_volume_flow` | Median | immediate | -0.0560 | +0.0066 | +0.1091 | ∞ |

**Decay distribution**: immediate=4, fast(1-2y)=3, gradual=99, persistent=142

**FP decay trajectories:**

- `combo_clamp_diff__max_up_ret__trend_bar_close_consistency`: Y1:+0.013 → Y2:-0.039 → Y3:+0.027 → Y4:-0.087 → Y5:+0.113
- `combo_diff__max_up_ret__trend_bar_close_consistency`: Y1:+0.013 → Y2:-0.039 → Y3:+0.028 → Y4:-0.087 → Y5:+0.113

### 159915ETF — `single`

| Feature | Tier | Decay | Y1 IC | Y2 IC | Y3+ IC | Half-life |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| `combo_min__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1776 | +0.1159 | +0.1263 | 2y |
| `combo_z_sum__star50_limit_proximity_early__yesterday_first_30min_return` | TP | persistent | +0.1718 | +0.1322 | +0.1739 | ∞ |
| `combo_z_sum__rbreaker_sell_setup_proximity_early__max_up_ret` | TP | persistent | +0.1573 | +0.1397 | +0.0771 | 4y |
| `combo_clamp_diff__max_up_ret__demark_setup_reversal_early` | TP | gradual | +0.1564 | +0.1470 | -0.0204 | 2y |
| `combo_ratio__star50_limit_proximity_early__volatility_expansion_trend_vector` | TP | persistent | +0.1388 | +0.0826 | +0.1479 | ∞ |
| `combo_clamp_diff__bar_ret_0__demark_setup_reversal_early` | TP | persistent | +0.1316 | +0.1618 | +0.0271 | 2y |
| `combo_tri_mean__opening_drive_thrust_ratio__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.1184 | +0.1719 | +0.0609 | ∞ |
| `combo_mean__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.1176 | +0.1462 | +0.1112 | ∞ |
| `combo_rank_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.1109 | +0.1843 | +0.0745 | ∞ |
| `combo_max__max_up_ret__first_bar_return` | TP | gradual | +0.1102 | +0.1603 | -0.0743 | 4y |
| `combo_tri_mean__rbreaker_sell_setup_proximity_early__bar_body_rng_0__first_bar_return` | TP | persistent | +0.1084 | +0.1398 | +0.0803 | ∞ |
| `combo_rank_max__max_up_ret__first_bar_return` | TP | gradual | +0.1079 | +0.1605 | -0.0628 | 4y |
| `combo_z_sum__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.1066 | +0.1154 | +0.1344 | ∞ |
| `combo_z_sum__opening_drive_thrust_ratio__max_up_ret` | TP | gradual | +0.1023 | +0.1961 | -0.0670 | 4y |
| `combo_rank_min__rbreaker_sell_setup_proximity_early__bar_ret_0` | TP | persistent | +0.1019 | +0.1346 | +0.0957 | ∞ |
| `combo_min__opening_drive_thrust_ratio__star50_limit_proximity_early` | TP | persistent | +0.0959 | +0.1836 | +0.0723 | ∞ |
| `combo_min__opening_drive_thrust_ratio__first_bar_sentiment` | TP | persistent | +0.0957 | +0.1565 | +0.0085 | 4y |
| `combo_min__rbreaker_sell_setup_proximity_early__first_bar_return` | TP | persistent | +0.0952 | +0.1379 | +0.0878 | ∞ |
| `combo_mean__max_up_ret__bar_body_rng_0` | TP | gradual | +0.0924 | +0.1743 | -0.0287 | 4y |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__first_bar_return` | TP | persistent | +0.0903 | +0.1245 | +0.0555 | ∞ |
| `combo_tri_median__rbreaker_sell_setup_proximity_early__first_bar_sentiment__bar_body_rng_0` | TP | persistent | +0.0899 | +0.1369 | +0.0817 | ∞ |
| `combo_tri_mean__max_up_ret__first_bar_sentiment__bar_body_rng_0` | TP | gradual | +0.0881 | +0.1735 | -0.0172 | 4y |
| `combo_z_sum__first_bar_sentiment__limit_down_proximity_early` | TP | persistent | +0.0864 | +0.0552 | +0.1287 | ∞ |
| `combo_tri_min__rbreaker_sell_setup_proximity_early__max_up_ret__first_bar_sentiment` | TP | persistent | +0.0799 | +0.1128 | +0.0949 | ∞ |
| `combo_rank_min__star50_limit_proximity_early__first_bar_return` | TP | persistent | +0.0797 | +0.1471 | +0.0996 | ∞ |
| `combo_min__star50_limit_proximity_early__bar_ret_0` | TP | persistent | +0.0733 | +0.1517 | +0.1033 | ∞ |
| `combo_rank_max__opening_drive_thrust_ratio__first_bar_return` | TP | gradual | +0.0680 | +0.1844 | -0.0158 | 4y |
| `combo_min__star50_limit_proximity_early__bar_body_rng_0` | TP | persistent | +0.0616 | +0.1479 | +0.1225 | ∞ |
| `combo_min__star50_limit_proximity_early__first_bar_sentiment` | TP | persistent | +0.0521 | +0.0786 | +0.1281 | ∞ |

**Decay distribution**: immediate=0, fast(1-2y)=0, gradual=7, persistent=22

---

## 5. Gate Mechanism Failure Analysis

How FP features' gate metrics compare to TP features. High overlap = gate cannot distinguish.

### 500ETF — `single`

| Metric | FP Mean±Std | TP Mean±Std | Overlap | Verdict |
| :--- | :--- | :--- | ---: | :--- |
| monotonicity | 0.673±0.004 | 0.746±0.049 | 4% | USEFUL |
| ic_ir | 0.483±0.005 | 0.702±0.167 | 1% | USEFUL |
| p_value | 0.001±0.000 | 0.000±0.002 | 0% | USEFUL |
| max_corr | 0.914±0.035 | 0.896±0.116 | 7% | USEFUL |
| deflated_ic | 0.187±0.000 | 0.245±0.041 | 0% | USEFUL |
| overall_ic | 0.186±0.000 | 0.245±0.041 | 0% | USEFUL |
| raw_ic | 0.074±0.000 | 0.155±0.027 | 0% | USEFUL |

---

## 6. False Rejection (Missed Opportunities)

Top-20 rejects per gate evaluated on lockbox. High FN rate = gate too strict.

### 300ETF — `single`

**7-Year Jackknife**: 18/20 top rejects are profitable (90%)

- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0611, Sharpe=+0.7408
- `combo_clamp_diff__smooth_momentum_structure__volume_weighted_price_position`: Train IC=+0.1868, Lock IC=+0.0562, Sharpe=+0.7322
- `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.2263, Lock IC=+0.0582, Sharpe=+0.4998

**B2 Rolling Guard**: 13/20 top rejects are profitable (65%)

- `combo_clamp_diff__volume_weighted_momentum_acceleration__bar_body_rng_0`: Train IC=+0.2129, Lock IC=+0.0580, Sharpe=+0.6040
- `combo_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2064, Lock IC=+0.0549, Sharpe=+0.3658
- `combo_tri_min__max_up_ret__first_bar_return__bar_body_rng_0`: Train IC=+0.2022, Lock IC=+0.0537, Sharpe=+0.2896

**Temporal Validation Gate**: 14/20 top rejects are profitable (70%)

- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0574, Sharpe=+0.6934
- `combo_rank_max__max_up_ret__first_bar_return`: Train IC=+0.1999, Lock IC=+0.0478, Sharpe=+0.4510
- `combo_rank_max__max_up_ret__bar_ret_0`: Train IC=+0.1999, Lock IC=+0.0478, Sharpe=+0.4510

**B3 Composite Floor**: 17/20 top rejects are profitable (85%)

- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2120, Lock IC=+0.0697, Sharpe=+0.6724
- `combo_tri_mean__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.2193, Lock IC=+0.0613, Sharpe=+0.4615
- `combo_tri_z_mean__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.2193, Lock IC=+0.0613, Sharpe=+0.4615

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_z_sum__max_up_ret__volume_weighted_price_position`: Train IC=+0.2124, Lock IC=+0.0561, Sharpe=+0.6987
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2194, Lock IC=+0.0715, Sharpe=+0.6792
- `combo_rank_min__star50_limit_proximity_early__bar_body_rng_0`: Train IC=+0.2255, Lock IC=+0.0811, Sharpe=+0.6633

### 500ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_clamp_diff__max_up_ret__smooth_momentum_structure`: Train IC=+0.2887, Lock IC=+0.0884, Sharpe=+0.8893
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589
- `combo_min__star50_limit_proximity_early__opening_momentum_score`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589

**B2 Rolling Guard**: 19/20 top rejects are profitable (95%)

- `combo_mean__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.0871, Sharpe=+0.7496
- `combo_z_sum__bar_ret_0__max_down_ret`: Train IC=+0.2271, Lock IC=+0.0871, Sharpe=+0.7496
- `combo_mean__first_bar_return__max_down_ret`: Train IC=+0.2253, Lock IC=+0.0871, Sharpe=+0.7496

**Temporal Validation Gate**: 20/20 top rejects are profitable (100%)

- `combo_rel_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2959, Lock IC=+0.0814, Sharpe=+1.0746
- `combo_rel_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2959, Lock IC=+0.0814, Sharpe=+1.0746
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721

**B3 Composite Floor**: 20/20 top rejects are profitable (100%)

- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2796, Lock IC=+0.1038, Sharpe=+0.9098
- `combo_tri_z_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__net_volume_flow`: Train IC=+0.2796, Lock IC=+0.1038, Sharpe=+0.9098
- `combo_tri_mean__rbreaker_sell_setup_proximity_early__opening_drive_thrust_ratio__opening_auction_imbalance`: Train IC=+0.2796, Lock IC=+0.1038, Sharpe=+0.9098

**B6 Temporal Stability Gate**: 4/4 top rejects are profitable (100%)

- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2459, Lock IC=+0.0981, Sharpe=+0.6202
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2459, Lock IC=+0.0981, Sharpe=+0.6202
- `combo_rank_min__max_up_ret__net_volume_flow`: Train IC=+0.2478, Lock IC=+0.0918, Sharpe=+0.3100

**B4 Correlation Gate**: 20/20 top rejects are profitable (100%)

- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1044, Sharpe=+1.3464
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1044, Sharpe=+1.3464
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2960, Lock IC=+0.1086, Sharpe=+1.1207

### 159915ETF — `single`

**7-Year Jackknife**: 19/20 top rejects are profitable (95%)

- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3003, Lock IC=+0.0937, Sharpe=+1.4621
- `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early`: Train IC=+0.2925, Lock IC=+0.1215, Sharpe=+1.3070
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2770, Lock IC=+0.0944, Sharpe=+1.2576

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
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1128, Sharpe=+1.4945

---

## 6b. Per-Gate Confusion Matrix (Full Population)

Stratified sample of ALL rejects per gate evaluated on lockbox.
**Precision** = % of rejects that are true FP (lock IC ≤ 0). Higher = gate is accurate.
**Collateral** = % of rejects that are TP (lock IC > 0, Sharpe > 0). Lower = less damage.

### 300ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1039 | 78 | 31 | 22 | 25 | 40% | 32% |
| B2 Rolling Guard | 240 | 78 | 19 | 25 | 34 | 24% | 44% |
| Temporal Validation Gate | 124 | 78 | 11 | 25 | 42 | 14% | 54% |
| BH-FDR Gate | 2 | 2 | 1 | 1 | 0 | 50% | 0% |
| B3 Composite Floor | 57 | 57 | 0 | 7 | 50 | 0% | 88% |
| B4 Correlation Gate | 38 | 38 | 0 | 1 | 37 | 0% | 97% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__rbreaker_sell_setup_proximity_early__max_up_ret`: Train IC=+0.1975, Lock IC=+0.0611, Sharpe=+0.7408
- `combo_clamp_diff__smooth_momentum_structure__volume_weighted_price_position`: Train IC=+0.1868, Lock IC=+0.0562, Sharpe=+0.7322
- `combo_tri_min__max_up_ret__volume_weighted_price_position__bar_body_rng_0`: Train IC=+0.2263, Lock IC=+0.0582, Sharpe=+0.4998

**B2 Rolling Guard** — top TP casualties:
- `combo_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1337, Lock IC=+0.0639, Sharpe=+0.9014
- `combo_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1333, Lock IC=+0.0639, Sharpe=+0.9014
- `combo_clamp_diff__volume_weighted_momentum_acceleration__bar_body_rng_0`: Train IC=+0.2129, Lock IC=+0.0580, Sharpe=+0.6040

**Temporal Validation Gate** — top TP casualties:
- `combo_rank_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0574, Sharpe=+0.6934

**B3 Composite Floor** — top TP casualties:
- `combo_tri_median__rbreaker_sell_setup_proximity_early__max_up_ret__bar_body_rng_0`: Train IC=+0.2120, Lock IC=+0.0697, Sharpe=+0.6724
- `combo_tri_min__max_up_ret__first_bar_return__volume_weighted_price_position`: Train IC=+0.1746, Lock IC=+0.0614, Sharpe=+0.6539
- `combo_tri_min__max_up_ret__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1742, Lock IC=+0.0615, Sharpe=+0.6539

**B4 Correlation Gate** — top TP casualties:
- `combo_rank_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1836, Lock IC=+0.0751, Sharpe=+0.7326
- `combo_z_sum__max_up_ret__volume_weighted_price_position`: Train IC=+0.2124, Lock IC=+0.0561, Sharpe=+0.6987
- `combo_z_sum__rbreaker_sell_setup_proximity_early__bar_body_rng_0`: Train IC=+0.2194, Lock IC=+0.0715, Sharpe=+0.6792

### 500ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1490 | 78 | 17 | 30 | 31 | 22% | 40% |
| B2 Rolling Guard | 310 | 78 | 20 | 7 | 51 | 26% | 65% |
| Temporal Validation Gate | 255 | 78 | 16 | 15 | 47 | 21% | 60% |
| BH-FDR Gate | 11 | 11 | 8 | 3 | 0 | 73% | 0% |
| B3 Composite Floor | 250 | 78 | 2 | 9 | 67 | 3% | 86% |
| B6 Yearly IC CV Gate | 2 | 2 | 0 | 2 | 0 | 0% | 0% |
| B6 Temporal Stability Gate | 4 | 4 | 0 | 0 | 4 | 0% | 100% |
| B4 Correlation Gate | 467 | 78 | 1 | 10 | 67 | 1% | 86% |

**7-Year Jackknife** — top TP casualties:
- `combo_clamp_diff__max_up_ret__smooth_momentum_structure`: Train IC=+0.2887, Lock IC=+0.0884, Sharpe=+0.8893
- `combo_min__star50_limit_proximity_early__early_body_momentum`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589
- `combo_min__star50_limit_proximity_early__opening_momentum_score`: Train IC=+0.2635, Lock IC=+0.1044, Sharpe=+0.8589

**B2 Rolling Guard** — top TP casualties:
- `iv_diff_1d`: Train IC=+0.0000, Lock IC=+0.0579, Sharpe=+0.9730
- `combo_tri_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1336, Lock IC=+0.0625, Sharpe=+0.8248
- `combo_tri_z_mean__net_volume_flow__star50_limit_proximity_early__volume_weighted_momentum_acceleration`: Train IC=+0.1336, Lock IC=+0.0625, Sharpe=+0.8248

**Temporal Validation Gate** — top TP casualties:
- `combo_rel_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2959, Lock IC=+0.0814, Sharpe=+1.0746
- `combo_rel_diff__smooth_momentum_structure__opening_auction_imbalance`: Train IC=+0.2959, Lock IC=+0.0814, Sharpe=+1.0746
- `combo_diff__smooth_momentum_structure__net_volume_flow`: Train IC=+0.2977, Lock IC=+0.0949, Sharpe=+1.0721

**B3 Composite Floor** — top TP casualties:
- `combo_min__net_volume_flow__max_down_ret`: Train IC=+0.2096, Lock IC=+0.1011, Sharpe=+1.1572
- `combo_min__opening_auction_imbalance__max_down_ret`: Train IC=+0.2096, Lock IC=+0.1011, Sharpe=+1.1572
- `combo_rank_max__opening_auction_imbalance__close_vs_open_range`: Train IC=+0.2097, Lock IC=+0.0972, Sharpe=+1.0262

**B6 Temporal Stability Gate** — top TP casualties:
- `combo_min__max_up_ret__net_volume_flow`: Train IC=+0.2459, Lock IC=+0.0981, Sharpe=+0.6202
- `combo_min__max_up_ret__opening_auction_imbalance`: Train IC=+0.2459, Lock IC=+0.0981, Sharpe=+0.6202
- `combo_rank_min__max_up_ret__net_volume_flow`: Train IC=+0.2478, Lock IC=+0.0918, Sharpe=+0.3100

**B4 Correlation Gate** — top TP casualties:
- `combo_min__net_volume_flow__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1044, Sharpe=+1.3464
- `combo_min__opening_auction_imbalance__star50_limit_proximity_early`: Train IC=+0.2911, Lock IC=+0.1044, Sharpe=+1.3464
- `combo_min__rbreaker_sell_setup_proximity_early__opening_auction_imbalance`: Train IC=+0.2960, Lock IC=+0.1086, Sharpe=+1.1207

### 159915ETF — `single`

| Gate | Total Rej | Evaluated | FP Caught | Median | TP Killed | Precision | Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7-Year Jackknife | 1128 | 78 | 28 | 10 | 40 | 36% | 51% |
| B2 Rolling Guard | 382 | 78 | 18 | 6 | 54 | 23% | 69% |
| Temporal Validation Gate | 41 | 41 | 3 | 1 | 37 | 7% | 90% |
| BH-FDR Gate | 5 | 5 | 1 | 0 | 4 | 20% | 80% |
| B3 Composite Floor | 268 | 78 | 0 | 10 | 68 | 0% | 87% |
| B4 Correlation Gate | 34 | 34 | 0 | 0 | 34 | 0% | 100% |

**7-Year Jackknife** — top TP casualties:
- `combo_rank_min__star50_limit_proximity_early__first_bar_sentiment`: Train IC=+0.3003, Lock IC=+0.0937, Sharpe=+1.4621
- `combo_clamp_diff__bar_body_rng_0__demark_setup_reversal_early`: Train IC=+0.2925, Lock IC=+0.1215, Sharpe=+1.3070
- `combo_rank_min__rbreaker_sell_setup_proximity_early__first_bar_sentiment`: Train IC=+0.2770, Lock IC=+0.0944, Sharpe=+1.2576

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
- `combo_z_sum__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.2548, Lock IC=+0.1128, Sharpe=+1.4945

---

## 6c. Temporal Gate Sub-Condition Analysis

Breakdown of temporal gate rejects by condition:
- **recent_ic ≤ 0**: signal decayed (last training chunk has no predictive power)
- **recency_ratio ≥ 2.5**: signal suspiciously concentrated in late training

### 300ETF — `single` (124 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 84 | 50 | 14 | 25 | 11 | 28% | 50% |
| recency_ratio >= 2.5 (late-concentrated) | 40 | 40 | 0 | 33 | 7 | 0% | 82% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_min__first_bar_return__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_ret_0__volume_weighted_price_position`: Train IC=+0.1258, Lock IC=+0.0623, Sharpe=+0.8157
- `combo_rank_min__bar_body_rng_0__volume_surge_direction`: Train IC=+0.2050, Lock IC=+0.0574, Sharpe=+0.6934
- `combo_min__bar_body_rng_0__limit_down_proximity_early`: Train IC=+0.1663, Lock IC=+0.0681, Sharpe=+0.5038
- `combo_min__bar_body_rng_0__rbreaker_buy_setup_proximity_early`: Train IC=+0.1663, Lock IC=+0.0681, Sharpe=+0.5038

### 500ETF — `single` (255 total temporal rejects)

| Condition | N | Evaluated | FP Caught | TP Killed | Median | FP Precision | TP Collateral |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| recent_ic <= 0 (decayed) | 237 | 50 | 0 | 48 | 2 | 0% | 96% |
| recency_ratio >= 2.5 (late-concentrated) | 18 | 18 | 5 | 9 | 4 | 28% | 50% |

**Top TP killed by recency_ratio cap:**
- `combo_rank_max__net_volume_flow__first_bar_sentiment`: Train IC=+0.2273, Lock IC=+0.0765, Sharpe=+0.6052
- `combo_rank_max__opening_auction_imbalance__first_bar_sentiment`: Train IC=+0.2273, Lock IC=+0.0765, Sharpe=+0.6052
- `combo_sig_product__volatility_expansion_trend_vector__max_down_ret`: Train IC=+0.1208, Lock IC=+0.0756, Sharpe=+0.5940
- `combo_rank_max__opening_drive_thrust_ratio__first_bar_sentiment`: Train IC=+0.2176, Lock IC=+0.0763, Sharpe=+0.5337
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

### 500ETF — `single`

**Strong training-only discriminators (Cohen's d > 0.5):**

- `n_negative_years`: FP is higher (d=+10.68). Threshold 1.000 → 99% accuracy.
- `ic_cv`: FP is higher (d=+10.13). Threshold 0.908 → 100% accuracy.
- `recency_ratio`: FP is lower (d=-3.03). Threshold 1.652 → 99% accuracy.
- `n_negative_regimes`: FP is higher (d=+2.92). Threshold 1.000 → 99% accuracy.
- `weak_link_cv`: FP is higher (d=+2.90). Threshold 0.726 → 99% accuracy.
- `ic_std_across_regimes`: FP is higher (d=+2.55). Threshold 0.091 → 99% accuracy.
- `half_ratio`: FP is higher (d=+0.97). Threshold 1.486 → 99% accuracy.

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
| `trend_bar_close_consistency` | 2 | 19 | 21 | 10% |  |
| `max_up_ret` | 2 | 88 | 90 | 2% |  |
| `smooth_momentum_structure` | 0 | 5 | 5 | 0% |  |
| `net_volume_flow` | 0 | 31 | 31 | 0% |  |
| `volume_weighted_price_position` | 0 | 10 | 10 | 0% |  |
| `bar_ret_0` | 0 | 45 | 45 | 0% |  |
| `volatility_expansion_trend_vector` | 0 | 18 | 18 | 0% |  |
| `limit_down_proximity_early` | 0 | 2 | 2 | 0% |  |
| `early_body_momentum` | 0 | 13 | 13 | 0% |  |
| `rbreaker_buy_setup_proximity_early` | 0 | 2 | 2 | 0% |  |
| `early_vwap_acceleration` | 0 | 2 | 2 | 0% |  |
| `first_bar_sentiment` | 0 | 24 | 24 | 0% |  |
| `volume_weighted_momentum_acceleration` | 0 | 10 | 10 | 0% |  |
| `high_low_sequence_momentum` | 0 | 3 | 3 | 0% |  |
| `rbreaker_sell_setup_proximity_early` | 0 | 66 | 66 | 0% |  |
| `star50_limit_proximity_early` | 0 | 49 | 49 | 0% |  |
| `close_vs_open_range` | 0 | 35 | 35 | 0% |  |
| `max_down_ret` | 0 | 24 | 24 | 0% |  |
| `late_bar_momentum` | 0 | 2 | 2 | 0% |  |
| `early_late_momentum_divergence` | 0 | 2 | 2 | 0% |  |
| `yesterday_first_30min_return` | 0 | 2 | 2 | 0% |  |
| `opening_drive_thrust_ratio` | 0 | 85 | 85 | 0% |  |
| `double_bottom_bull_flag_early` | 0 | 2 | 2 | 0% |  |
| `trend_day_regime_conviction` | 0 | 2 | 2 | 0% |  |
| `bar_body_rng_0` | 0 | 20 | 20 | 0% |  |
| `body_size_progression` | 0 | 13 | 13 | 0% |  |
| `first_bar_return` | 0 | 32 | 32 | 0% |  |
| `volume_surge_direction` | 0 | 3 | 3 | 0% |  |
| `demark_setup_reversal_early` | 0 | 2 | 2 | 0% |  |

---

## 9. Operator Class FP Rate

- **Symmetric** (`max, mean, min, rank_max, rank_min`): FP=0, TP=170, FP rate=0%
- **Conditional** (`abs_diff, clamp_diff, diff, ifelse, product, ratio`): FP=2, TP=24, FP rate=8%
- **3-way** (`tri_ifelse, tri_max, tri_mean, tri_median, tri_min`): FP=0, TP=43, FP rate=0%

